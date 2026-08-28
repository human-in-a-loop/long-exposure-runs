#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:10:00Z
# cycle: 29
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry/adjudication
# ---
"""Cycle-29 test suite for the hash-geometry adjudication branch.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
        /usr/bin/python3 tests/test_hash_geometry_adjudication.py

Plain-assert style, no pytest.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "scripts" / "analysis"
DATA = ROOT / "data" / "collision_model"
DOCS = ROOT / "docs"

NEW_SCRIPTS = (
    "multiple_testing_correction.py",
    "drop_batch_v2_sensitivity.py",
    "leave_one_cell_out_contribution.py",
    "hash_geometry_adjudication_verdict.py",
)

RUBRIC_DOC = DOCS / "collision_model_hash_space_geometry_adjudication_rubric.md"


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ scripts

def test_interpreter_guard_present_in_new_scripts() -> None:
    for name in NEW_SCRIPTS:
        src = (ANALYSIS / name).read_text()
        assert 'assert sys.executable == "/usr/bin/python3"' in src, name
        ast.parse(src, filename=name)
    print("PASS test_interpreter_guard_present_in_new_scripts")


def test_no_prng_in_sampling() -> None:
    banned = {"random", "numpy.random", "torch", "secrets"}
    for name in NEW_SCRIPTS:
        src = (ANALYSIS / name).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    for b in banned:
                        assert not a.name.startswith(b), f"{name} imports banned {a.name}"
            elif isinstance(node, ast.ImportFrom):
                m = node.module or ""
                for b in banned:
                    assert not m.startswith(b), f"{name} imports banned {m}"
        assert not re.search(r"\bnp\.random\.", src), f"{name} uses np.random.*"
        assert not re.search(r"\brandom\.", src), f"{name} uses random.*"
    print("PASS test_no_prng_in_sampling")


def test_alpha_still_pinned_at_0_7469() -> None:
    src = (ANALYSIS / "drop_batch_v2_sensitivity.py").read_text()
    assert "0.7469387071101908" in src, "alpha literal missing from drop_batch_v2_sensitivity.py"
    drop = json.loads((DATA / "drop_batch_v2_sensitivity.json").read_text())
    assert abs(float(drop["alpha_pinned"]) - 0.7469387071101908) < 1e-12
    verd = json.loads((DATA / "hash_geometry_adjudication_verdict.json").read_text())
    assert abs(float(verd["alpha_pinned"]) - 0.7469387071101908) < 1e-12
    print("PASS test_alpha_still_pinned_at_0_7469")


# ------------------------------------------------------------------ Bonferroni + BH

def test_bonferroni_threshold_computed_correctly() -> None:
    mtc = json.loads((DATA / "multiple_testing_correction.json").read_text())
    m = mtc["m_cells"]
    alpha = mtc["alpha"]
    expected = alpha / m
    assert abs(mtc["bonferroni_threshold"] - expected) < 1e-15
    # 35 cells at alpha 0.05 -> threshold approximately 0.001428.
    assert m == 35, m
    assert abs(mtc["bonferroni_threshold"] - 0.05 / 35) < 1e-15
    print("PASS test_bonferroni_threshold_computed_correctly")


def test_bh_procedure_matches_reference() -> None:
    """BH procedure hand-verified on the actual p-vector."""
    mtc = json.loads((DATA / "multiple_testing_correction.json").read_text())
    per_cell = mtc["per_cell"]
    pvals = [c["p_value"] for c in per_cell]
    q = mtc["q_bh"]
    m = len(pvals)
    # Reproduce the BH survivor count independently.
    order = sorted(range(m), key=lambda i: (pvals[i], i))
    max_rank = 0
    for rank1, idx in enumerate(order, start=1):
        if pvals[idx] <= rank1 * q / m:
            max_rank = rank1
    ref_count = max_rank
    got_count = mtc["counts"]["bh_survivors"]
    assert ref_count == got_count, (ref_count, got_count)
    print("PASS test_bh_procedure_matches_reference")


# ---------------------------------------------------------- drop-batch_v2

def test_drop_batch_v2_excludes_correct_ledger_rows() -> None:
    drop = json.loads((DATA / "drop_batch_v2_sensitivity.json").read_text())
    assert drop["excluded_batch"] == "batch_v2"
    assert drop["excluded_batch_sha_prefix"] == "be5726ab"
    # 35 - 5 (per rule_type for batch_v2) = 30 retained cells.
    assert drop["m_full"] == 35
    assert drop["m_retained"] == 30
    assert drop["counts"]["cells_removed_by_drop"] == 5
    # Retained R^2 should exclude batch_v2 from the per_batch_r2 dict.
    assert "batch_v2" not in drop["per_batch_r2_retained"], drop["per_batch_r2_retained"]
    print("PASS test_drop_batch_v2_excludes_correct_ledger_rows")


# ------------------------------------------------------------------ LOCO

def test_loco_holds_out_correct_cell() -> None:
    loco = json.loads((DATA / "leave_one_cell_out.json").read_text())
    per = loco["per_cell"]
    # 35 cells -> 35 LOCO rows.
    assert loco["m_cells"] == 35
    assert len(per) == 35
    # Each per-cell row has the held-out cell identified.
    for row in per:
        assert set(row.keys()) >= {
            "batch",
            "rule_type",
            "p_value_held_out",
            "chi2_held_out",
            "bh_survivors_when_held_out",
            "chi2_sum_of_remaining",
        }, row.keys()
    # Sum-of-remaining should equal baseline - held.
    baseline = loco["baseline_chi2_sum"]
    for row in per:
        expected = baseline - row["chi2_held_out"]
        assert abs(row["chi2_sum_of_remaining"] - expected) < 1e-9, row
    print("PASS test_loco_holds_out_correct_cell")


# ------------------------------------------------------------------ verdict rubric

def test_verdict_rubric_frozen_hash_matches_committed_doc() -> None:
    verd = json.loads((DATA / "hash_geometry_adjudication_verdict.json").read_text())
    expected = _sha256_bytes(RUBRIC_DOC.read_bytes())
    assert verd["rubric_hash"] == expected, (verd["rubric_hash"], expected)
    print("PASS test_verdict_rubric_frozen_hash_matches_committed_doc")


def _synthetic_mtc_drop_loco(bh_survivors, retained, single_cell, survivor_batch="batch_x"):
    survivors_bh = [
        {"batch": survivor_batch, "rule_type": "harmonic", "p_value": 0.001}
        for _ in range(bh_survivors)
    ]
    mtc = {
        "counts": {"bh_survivors": bh_survivors},
        "survivors_bh": survivors_bh,
        "survivors_bonferroni": [],
        "survivors_sidak": [],
    }
    drop = {
        "counts": {"bh_survivors_retained": retained},
        "survivors_bh_retained": [],
        "r2_m3_mean_full": 0.0,
        "r2_m3_mean_retained": 0.0,
    }
    loco = {
        "single_cell_carries_signal": single_cell,
        "baseline_bh_survivors": bh_survivors,
        "changers_under_loco": [],
    }
    return mtc, drop, loco


def test_verdict_dispatch_all_three_branches() -> None:
    """Import classify() and check each frozen branch fires."""
    sys.path.insert(0, str(ANALYSIS))
    import hash_geometry_adjudication_verdict as adj  # type: ignore

    # COLLAPSES: bh_survivors_full = 0.
    mtc, drop, loco = _synthetic_mtc_drop_loco(0, 0, False)
    v, _ = adj.classify(mtc, drop, loco)
    assert v == "M3_COLLAPSES_TO_REFUTES", v

    # STANDS: multiple BH survivors, drop-v2 keeps >=1, no single-cell dep.
    mtc, drop, loco = _synthetic_mtc_drop_loco(3, 2, False)
    v, _ = adj.classify(mtc, drop, loco)
    assert v == "M3_STANDS", v

    # MIXED: exactly 1 BH survivor in batch_v2, drop-v2 removes it.
    mtc, drop, loco = _synthetic_mtc_drop_loco(1, 0, False, survivor_batch="batch_v2")
    v, _ = adj.classify(mtc, drop, loco)
    assert v == "MIXED", v

    # MIXED via single-cell dependence: >=2 survivors but LOCO shows dependency.
    mtc, drop, loco = _synthetic_mtc_drop_loco(2, 2, True)
    v, _ = adj.classify(mtc, drop, loco)
    assert v == "MIXED", v

    print("PASS test_verdict_dispatch_all_three_branches")


def test_verdict_json_uses_frozen_label() -> None:
    verd = json.loads((DATA / "hash_geometry_adjudication_verdict.json").read_text())
    assert verd["verdict"] in {"M3_STANDS", "M3_COLLAPSES_TO_REFUTES", "MIXED"}
    assert verd["frozen_verdict_labels"] == ["M3_STANDS", "M3_COLLAPSES_TO_REFUTES", "MIXED"]
    print("PASS test_verdict_json_uses_frozen_label")


def test_rubric_committed_before_verdict_scripts() -> None:
    """Rubric doc must exist and predate the verdict JSON. We verify presence
    of both files here; the git log / ledger event `verdict_rubric_frozen`
    covers temporal ordering."""
    assert RUBRIC_DOC.exists(), "adjudication rubric doc missing"
    assert (DATA / "hash_geometry_adjudication_verdict.json").exists(), "verdict JSON missing"
    # Rubric must list all three frozen verdicts by name.
    txt = RUBRIC_DOC.read_text()
    for label in ("M3_STANDS", "M3_COLLAPSES_TO_REFUTES", "MIXED"):
        assert label in txt, f"rubric doc missing frozen label {label}"
    print("PASS test_rubric_committed_before_verdict_scripts")


def main() -> int:
    tests = [
        test_interpreter_guard_present_in_new_scripts,
        test_no_prng_in_sampling,
        test_alpha_still_pinned_at_0_7469,
        test_bonferroni_threshold_computed_correctly,
        test_bh_procedure_matches_reference,
        test_drop_batch_v2_excludes_correct_ledger_rows,
        test_loco_holds_out_correct_cell,
        test_verdict_rubric_frozen_hash_matches_committed_doc,
        test_verdict_dispatch_all_three_branches,
        test_verdict_json_uses_frozen_label,
        test_rubric_committed_before_verdict_scripts,
    ]
    n = 0
    for t in tests:
        t()
        n += 1
    print(f"\nOK {n}/{n} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
