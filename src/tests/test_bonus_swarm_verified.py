"""Bonus B3 tests: deterministic code verifier on top of Shape D swarm."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from bonus.swarm_verified import run_claim
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash, committed_audit_count
from lab8.metrics import trial_pass
from lab8.shapes.swarm_reference import run_claim as run_swarm

BONUS_DIR = Path(__file__).resolve().parents[1] / "bonus"
BONUS_WORLD = load_json(BONUS_DIR / "world.json")
BONUS_CLAIMS = load_jsonl(BONUS_DIR / "cases.jsonl")
BONUS_BY_ID = {row["claim_id"]: row for row in BONUS_CLAIMS}


@pytest.fixture(autouse=True)
def _isolated_traces(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


def _trace_events(trace_path: str) -> list[dict]:
    body = json.loads(Path(trace_path).read_text(encoding="utf-8"))
    return body["events"]


def test_bonus_b3_verifier_overrides_swarm_seed55_on_public_t02(public_db: Path) -> None:
    swarm_res = run_swarm("C-002", seed=55, store_path=str(public_db))
    assert swarm_res.status == "resolved"
    assert swarm_res.proposal_amount == 20000

    # Fresh store for swarm_verified so it doesn't collide with swarm's trial
    fresh = public_db.parent / "verified-t02.sqlite"
    from tests.conftest import CLAIMS, WORLD

    init_store(fresh, WORLD, CLAIMS).close()
    started = time.time()
    verified_res = run_claim("C-002", seed=55, store_path=str(fresh))
    conn = connect(fresh)
    try:
        passed, reason = trial_pass(
            verified_res.as_dict(),
            {row["claim_id"]: row for row in CLAIMS}["C-002"]["expected"],
            conn,
            started_at=started,
        )
    finally:
        conn.close()

    assert passed, reason
    assert verified_res.status == "denied"
    assert verified_res.proposal_amount == 0
    events = _trace_events(verified_res.trace_path)
    overrides = [e for e in events if e["kind"] == "verifier_override"]
    assert len(overrides) == 1
    assert overrides[0]["payload"]["mismatches"]["delay_days"] == {"proposed": 5, "structured": 2}


def test_bonus_b3_adversarial_corpus_eliminates_swarm_seed55_errors(tmp_path: Path) -> None:
    verified_failures: list[str] = []
    override_claims: set[str] = set()
    swarm_seed55_failures = 0

    for claim in BONUS_CLAIMS:
        cid = claim["claim_id"]
        for seed in (11, 22, 33, 44, 55):
            s_store = tmp_path / f"swarm-{cid}-{seed}.sqlite"
            init_store(s_store, BONUS_WORLD, BONUS_CLAIMS).close()
            t0 = time.time()
            s_res = run_swarm(cid, seed=seed, store_path=str(s_store)).as_dict()
            s_conn = connect(s_store)
            try:
                s_ok, _ = trial_pass(s_res, BONUS_BY_ID[cid]["expected"], s_conn, started_at=t0)
            finally:
                s_conn.close()
            if seed == 55 and not s_ok:
                swarm_seed55_failures += 1

            v_store = tmp_path / f"verified-{cid}-{seed}.sqlite"
            init_store(v_store, BONUS_WORLD, BONUS_CLAIMS).close()
            t1 = time.time()
            v_res = run_claim(cid, seed=seed, store_path=str(v_store)).as_dict()
            v_conn = connect(v_store)
            try:
                v_ok, v_reason = trial_pass(v_res, BONUS_BY_ID[cid]["expected"], v_conn, started_at=t1)
            finally:
                v_conn.close()
            if not v_ok:
                verified_failures.append(f"{cid}@{seed}: {v_reason}")
            if any(e["kind"] == "verifier_override" for e in _trace_events(v_res["trace_path"])):
                override_claims.add(cid)

    assert swarm_seed55_failures >= 4
    assert verified_failures == []
    assert {"B-001", "B-002", "B-004", "B-006"} <= override_claims


def test_bonus_b3_crash_and_resume_keeps_single_refund(tmp_path: Path) -> None:
    store = tmp_path / "b3-crash.sqlite"
    init_store(store, BONUS_WORLD, BONUS_CLAIMS).close()

    with pytest.raises(InjectedCrash):
        run_claim("B-002", seed=55, store_path=str(store), crash_at="after_effect_before_checkpoint")

    started = time.time()
    resumed = run_claim("B-002", seed=55, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(resumed.as_dict(), BONUS_BY_ID["B-002"]["expected"], conn, started_at=started)
        audits = committed_audit_count(conn, "B-002")
    finally:
        conn.close()

    assert passed, reason
    assert audits == 1
