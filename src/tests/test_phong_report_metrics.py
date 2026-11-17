"""Tests authored by Hoang The Phong (MSSV: 2A202603832) — Data & Report Specialist.

Validates benchmark metrics integrity, crash report completeness,
variance calculations in lab8.metrics, and documentation format compliance.
All tests run fast and pass in pytest -q (host level, no @pytest.mark.student).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from lab8.metrics import summarize

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT.parent / "report" / "team"


def test_phong_benchmark_report_shapes_and_trials():
    """Verify benchmark.json contains 4 shapes with exactly 70 trials each and consistent metrics."""
    bench_file = REPORTS_DIR / "benchmark.json"
    assert bench_file.exists(), "src/reports/benchmark.json must exist"
    data = json.loads(bench_file.read_text(encoding="utf-8"))

    assert "by_shape" in data, "benchmark.json must have 'by_shape'"
    by_shape = data["by_shape"]
    required_shapes = {"workflow", "single", "orchestrator", "swarm"}
    assert required_shapes.issubset(by_shape.keys()), f"Missing shapes in benchmark: {required_shapes - set(by_shape.keys())}"

    for shape in required_shapes:
        stats = by_shape[shape]
        assert stats["trials"] == 70, f"{shape} must have 70 trials"
        assert stats["graded_trials"] == 70, f"{shape} must have 70 graded trials"

    # Shape A (workflow) must be deterministic 100% pass and have lowest cost per success
    wf = by_shape["workflow"]
    assert wf["pass_rate"] == 1.0
    assert wf["pass_5"] == 1.0
    assert wf["seed_variance"] == 0.0
    assert wf["cost_per_success_vnd"] == pytest.approx(28.79, abs=0.1)

    # Swarm must show weakness on seed 55
    sw = by_shape["swarm"]
    assert sw["pass_rate"] < 1.0
    assert sw["seed_pass_rates"]["55"] < 1.0
    assert sw["seed_variance"] > 0.0

    # Workflow must be more cost-effective than orchestrator
    orch = by_shape["orchestrator"]
    assert wf["cost_per_success_vnd"] < orch["cost_per_success_vnd"]


def test_phong_crash_report_safety():
    """Verify crash.json achieves perfect 20/20 crash safety across all injected crash scenarios."""
    crash_file = REPORTS_DIR / "crash.json"
    assert crash_file.exists(), "src/reports/crash.json must exist"
    data = json.loads(crash_file.read_text(encoding="utf-8"))

    assert data.get("crash_safety") == "20/20", "crash_safety must be '20/20'"
    assert data.get("count") == 20
    assert data.get("passed") == 20
    scenarios = data.get("scenarios", [])
    assert len(scenarios) == 20
    assert all(sc.get("passed") is True for sc in scenarios)


def test_phong_metrics_summarize_variance_calculation():
    """Verify population variance and pass^5 calculation in lab8.metrics.summarize."""
    # Synthetic trial set across 2 seeds and 2 claims
    trials: list[dict[str, Any]] = [
        {"shape": "test_shape", "claim_id": "C-1", "seed": 11, "passed": True, "cost_estimate": 10.0, "steps": 2, "model_calls": 1, "tool_calls": 1},
        {"shape": "test_shape", "claim_id": "C-2", "seed": 11, "passed": True, "cost_estimate": 10.0, "steps": 2, "model_calls": 1, "tool_calls": 1},
        {"shape": "test_shape", "claim_id": "C-1", "seed": 22, "passed": True, "cost_estimate": 10.0, "steps": 2, "model_calls": 1, "tool_calls": 1},
        {"shape": "test_shape", "claim_id": "C-2", "seed": 22, "passed": False, "cost_estimate": 10.0, "steps": 2, "model_calls": 1, "tool_calls": 1},
    ]
    summary = summarize(trials)
    shape_stat = summary["test_shape"]

    assert shape_stat["trials"] == 4
    assert shape_stat["successes"] == 3
    assert shape_stat["pass_rate"] == 0.75
    # Seed 11 rate = 1.0, Seed 22 rate = 0.5 -> Mean = 0.75
    # Population variance = ((1.0 - 0.75)^2 + (0.5 - 0.75)^2) / 2 = (0.0625 + 0.0625) / 2 = 0.0625
    assert shape_stat["seed_variance"] == pytest.approx(0.0625)
    # pass_5 requires claim passed across all seeds: C-1 passed (11 & 22), C-2 failed at 22 -> 1 of 2 claims
    assert shape_stat["pass_5"] == pytest.approx(0.5)


def test_phong_docs_decision_adr_format():
    """Verify decision_adr.md contains all required label lines with workflow selected."""
    adr_file = DOCS_DIR / "decision_adr.md"
    assert adr_file.exists(), "decision_adr.md must exist"
    content = adr_file.read_text(encoding="utf-8")

    assert "- Shape chọn: workflow" in content
    assert "- Crash safety: 20/20" in content
    assert "- Secret leak / approval bypass: 0 / 0" in content
    assert "- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000" in content
    assert "## Vì sao shape này" in content
    assert "## Có đáng đổi lấy multi-agent không" in content
    assert "## Trace và bằng chứng" in content
    assert "## Giới hạn" in content


def test_phong_docs_research_card_format():
    """Verify research_card.md has no empty fields in the team answer column."""
    card_file = DOCS_DIR / "research_card.md"
    assert card_file.exists(), "research_card.md must exist"
    content = card_file.read_text(encoding="utf-8")

    required_fields = ["CÂU", "SOURCE", "CLAIM", "BOUNDARY", "HYPOTHESIS", "METHOD", "FAILURE / METRIC"]
    for line in content.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in required_fields:
            assert cells[2], f"Field '{cells[0]}' in research_card.md must not be empty"
            required_fields.remove(cells[0])
    assert not required_fields, f"Missing fields in research_card.md: {required_fields}"


def test_phong_docs_group_report_sections():
    """Verify group_report.md contains all mandatory sections from 1 to 8."""
    rep_file = DOCS_DIR / "group_report.md"
    assert rep_file.exists(), "group_report.md must exist"
    content = rep_file.read_text(encoding="utf-8")

    assert "- Tên nhóm: 404" in content
    for section_idx in range(1, 9):
        assert f"## {section_idx}." in content, f"Section {section_idx} must exist in group_report.md"
