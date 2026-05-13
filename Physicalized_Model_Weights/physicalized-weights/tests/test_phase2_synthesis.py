# created: 2026-05-13T07:36:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-SYNTH-2

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def build() -> None:
    import importlib.util

    script = ROOT / "physicalized-weights/scripts/build_phase2_synthesis.py"
    spec = importlib.util.spec_from_file_location("build_phase2_synthesis", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.main()


def rows() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/phase2_claim_matrix.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def summary() -> dict:
    return json.loads((ROOT / "physicalized-weights/data/phase2_synthesis_summary.json").read_text())


def test_m_swbase_2_result_is_represented() -> None:
    data = summary()
    assert data["stronger_baseline_winner_counts"]["programmable_accelerator"] == 9
    assert data["stronger_baseline_winner_counts"]["optimized_software_runtime"] == 1
    assert data["preserved_case_winner"] == "programmable_accelerator"


def test_safety_filter_superiority_not_preserved() -> None:
    perf = [row for row in rows() if "performance or economic winner" in row["claim"]][0]
    assert perf["phase2_status"] in {"falsified", "superseded"}
    assert perf["phase2_status"] != "preserved"


def test_hybrid_wins_count_is_zero() -> None:
    assert summary()["hybrid_workload_wins"] == 0


def test_programmable_accelerator_dominance_in_claim_matrix() -> None:
    text = "\n".join(row["claim"] + " " + row["supporting_artifacts"] for row in rows()).lower()
    assert "programmable accelerator is the strongest current baseline" in text
    assert "stronger_baseline_summary.json" in text


def test_every_claim_has_supporting_artifact_and_reopen_condition() -> None:
    for row in rows():
        assert row["supporting_artifacts"].strip()
        assert row["reopen_condition"].strip()
        for artifact in row["supporting_artifacts"].split(";"):
            assert (ROOT / artifact.strip()).exists(), artifact


def test_png_exists_and_is_nonempty() -> None:
    path = ROOT / "physicalized-weights/data/phase2_evidence_map.png"
    assert path.exists()
    assert path.stat().st_size > 1000


def test_final_synthesis_contains_phase2_downgrade() -> None:
    text = (ROOT / "physicalized-weights/docs/final_synthesis.md").read_text()
    assert "Phase 2 Addendum" in text
    assert "hybrid physicalized safety/filter wins zero workload scenarios" in text
    assert "M-SWBASE-2" in text


def run_tests() -> None:
    build()
    tests = [
        test_m_swbase_2_result_is_represented,
        test_safety_filter_superiority_not_preserved,
        test_hybrid_wins_count_is_zero,
        test_programmable_accelerator_dominance_in_claim_matrix,
        test_every_claim_has_supporting_artifact_and_reopen_condition,
        test_png_exists_and_is_nonempty,
        test_final_synthesis_contains_phase2_downgrade,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_tests()
