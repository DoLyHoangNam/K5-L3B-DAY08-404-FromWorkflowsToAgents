"""Bonus B3: swarm_verified — deterministic code verifier before commit.

Wraps the Shape D swarm flow and adds a single-round deterministic verifier
that checks (`delay_days`, `status`, `damage_verified`) against the structured
order view before calling `durability.issue_refund`. When a discrepancy is
found (e.g. seed % 5 == 0 trusting ticket delay), the verifier repairs from
the structured order row, recomputes `compute_compensation`, and logs a
`verifier_override` event into the trace.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, tool_cost
from lab8.trace import Trace

SHAPE = "swarm_verified"
VERIFIED_FIELDS = ("delay_days", "status", "damage_verified")


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    run_id = make_run_id(SHAPE, claim_id, seed)
    trace = Trace(run_id)

    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    ticket = claim_row["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)

    if not claim_row["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim_row["principal_id"]
    )
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add(
        "investigator",
        {
            "lookup_order": order_view,
            "policy_count": len(
                (investigated["tools"].get("lookup_policy") or {}).get("policies") or []
            ),
        },
    )
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=order_view.get("reason"),
        )

    structured_order: dict[str, Any] = dict(order_view["order"])
    proposed_order: dict[str, Any] = dict(structured_order)
    # Keep the underlying swarm behavior intact before the verifier step.
    if (
        parsed_delay is not None
        and parsed_delay != int(proposed_order["delay_days"])
        and seed % 5 == 0
    ):
        proposed_order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})

    quote_payload = investigated["tools"]["compute_compensation"]
    if proposed_order["delay_days"] != structured_order["delay_days"]:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, proposed_order)

    # Code verifier: cross-check fields used for quoting against structured order view.
    mismatches = {
        field: {
            "proposed": proposed_order.get(field),
            "structured": structured_order.get(field),
        }
        for field in VERIFIED_FIELDS
        if proposed_order.get(field) != structured_order.get(field)
    }
    if mismatches:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, structured_order)
        trace.add(
            "verifier_override",
            {
                "round": 1,
                "mismatches": mismatches,
                "repaired_amount_vnd": int(quote_payload["amount_vnd"]),
            },
        )

    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", quote_payload)
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote_payload.get("reason"),
        )

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )

    return finish(
        conn,
        shape=SHAPE,
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
