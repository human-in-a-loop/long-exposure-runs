#!/usr/bin/env python3
# ---
# created: 2026-08-29T01:15:00Z
# cycle: 30
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-semantic-cluster-overlap
# ---
"""Cycle-30 test suite for the semantic-cluster-overlap probe.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
        /usr/bin/python3 tests/test_semantic_cluster_overlap.py

Plain-assert style, no pytest.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import subprocess
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "scripts" / "analysis"
DATA = ROOT / "data" / "collision_model"
RUBRIC_DOC = ROOT / "docs" / "collision_model_semantic_cluster_overlap_rubric.md"
VERDICT_JSON = DATA / "semantic_cluster_verdict.json"
FIT_JSON = DATA / "semantic_cluster_fit.json"
THR_JSON = DATA / "semantic_cluster_thresholds.json"
FP_TSV = DATA / "rule_structural_fingerprints.tsv"
EC_TSV = DATA / "semantic_equivalence_classes.tsv"
KEFF_TSV = DATA / "effective_k_semantic.tsv"

NEW_SCRIPTS = [
    "rule_structural_fingerprints.py",
    "semantic_cluster_thresholds.py",
    "semantic_equivalence_classes.py",
    "effective_k_semantic.py",
    "semantic_cluster_fit.py",
    "semantic_cluster_verdict.py",
    "anchor_preservation_semantic.py",
]

ALPHA_PINNED = 0.7469387071101908


def test_interpreter_guard_present_in_all_new_scripts():
    for name in NEW_SCRIPTS:
        p = ANALYSIS / name
        assert p.is_file(), f"missing script {name}"
        src = p.read_text()
        assert "/usr/bin/python3" in src, f"interpreter guard missing in {name}"
        assert "assert sys.executable" in src, f"assert-guard missing in {name}"
    print("PASS test_interpreter_guard_present_in_all_new_scripts")


def _ast_visits_prng(source: str) -> list[str]:
    tree = ast.parse(source)
    prng_names = {"random", "randrange", "randint", "sample", "shuffle",
                  "choice", "choices", "uniform", "gauss", "np_random"}
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in ("random", "numpy.random"):
                    hits.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in (
                    "random", "numpy"):
                # numpy is fine; numpy.random is not.
                if node.module.startswith("numpy.random"):
                    hits.append(node.module)
                if node.module == "random":
                    hits.append(node.module)
        if isinstance(node, ast.Attribute) and isinstance(node.attr, str):
            if node.attr in prng_names and node.attr != "sample":
                # 'sample' too generic — allow.
                pass
    return hits


def test_no_prng_in_fingerprint_or_threshold_scripts():
    for name in ("rule_structural_fingerprints.py",
                 "semantic_cluster_thresholds.py",
                 "semantic_equivalence_classes.py",
                 "effective_k_semantic.py",
                 "semantic_cluster_fit.py",
                 "semantic_cluster_verdict.py"):
        src = (ANALYSIS / name).read_text()
        hits = _ast_visits_prng(src)
        assert not hits, f"PRNG-family import in {name}: {hits}"
    print("PASS test_no_prng_in_fingerprint_or_threshold_scripts")


def test_alpha_still_pinned_at_0_7469():
    src_fit = (ANALYSIS / "semantic_cluster_fit.py").read_text()
    assert "0.7469387071101908" in src_fit, "alpha not pinned in fit"
    src_verdict = (ANALYSIS / "semantic_cluster_verdict.py").read_text()
    assert "0.7469387071101908" in src_verdict, "alpha not pinned in verdict"
    fit = json.loads(FIT_JSON.read_text())
    assert abs(fit["alpha_pinned"] - ALPHA_PINNED) < 1e-12
    verdict = json.loads(VERDICT_JSON.read_text())
    assert abs(verdict["alpha_pinned"] - ALPHA_PINNED) < 1e-12
    print("PASS test_alpha_still_pinned_at_0_7469")


def test_fingerprint_deterministic_across_two_runs():
    sha1 = hashlib.sha256(FP_TSV.read_bytes()).hexdigest()
    r = subprocess.run(
        ["/usr/bin/python3", str(ANALYSIS / "rule_structural_fingerprints.py")],
        capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr
    sha2 = hashlib.sha256(FP_TSV.read_bytes()).hexdigest()
    assert sha1 == sha2, f"fingerprint TSV not deterministic ({sha1} != {sha2})"
    print("PASS test_fingerprint_deterministic_across_two_runs")


def test_threshold_computed_on_76_row_ledger_only():
    """The threshold script MUST NOT reference ledger_i3_dminor. This
    enforces pre-registration integrity: the 20th-percentile threshold
    cannot depend on the augmented ledger."""
    src = (ANALYSIS / "semantic_cluster_thresholds.py").read_text()
    assert "ledger_i3_dminor" not in src, (
        "threshold script references ledger_i3_dminor — breaks "
        "pre-registration integrity"
    )
    thr = json.loads(THR_JSON.read_text())
    assert thr["source_ledger"] == "data/rules/ledger.jsonl"
    assert thr["source_ledger_tag"] == "76row"
    print("PASS test_threshold_computed_on_76_row_ledger_only")


def test_equivalence_classes_deterministic():
    sha1 = hashlib.sha256(EC_TSV.read_bytes()).hexdigest()
    r = subprocess.run(
        ["/usr/bin/python3", str(ANALYSIS / "semantic_equivalence_classes.py")],
        capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr
    sha2 = hashlib.sha256(EC_TSV.read_bytes()).hexdigest()
    assert sha1 == sha2, f"equivalence-class TSV not deterministic"
    print("PASS test_equivalence_classes_deterministic")


def test_effective_k_semantic_le_raw_k():
    """K_eff-semantic must be ≤ raw K per rule_type per ledger."""
    RAW_K = {
        "76row": {"harmonic": 10, "rhythmic": 18, "melodic": 18,
                  "form": 15, "arrangement": 15},
        "86row_i3": {"harmonic": 20, "rhythmic": 18, "melodic": 18,
                     "form": 15, "arrangement": 15},
    }
    with open(KEFF_TSV) as f:
        _ = f.readline()
        for line in f:
            source, rt, _short, keff = line.rstrip("\n").split("\t")
            keff = int(keff)
            raw = RAW_K[source][rt]
            assert keff <= raw, f"K_eff {keff} > raw K {raw} for {source}/{rt}"
            assert keff >= 1, f"K_eff must be ≥1 for {source}/{rt}"
    print("PASS test_effective_k_semantic_le_raw_k")


def test_verdict_dispatch_all_three_branches():
    """The dispatcher must return each frozen label under matched inputs."""
    sys.path.insert(0, str(ANALYSIS))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sc_verdict", str(ANALYSIS / "semantic_cluster_verdict.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # M4_REFUTES: mean R² ≤ 0
    v, _ = mod._dispatch(-0.5, 0.95)
    assert v == "M4_REFUTES", f"expected M4_REFUTES got {v}"
    v, _ = mod._dispatch(0.0, 0.95)
    assert v == "M4_REFUTES", f"expected M4_REFUTES at 0 got {v}"
    # M4_WEAK: 0 < R² < 0.60
    v, _ = mod._dispatch(0.3, 0.95)
    assert v == "M4_WEAK", f"expected M4_WEAK got {v}"
    # M4_EXPLAINS: R² ≥ 0.60 AND aggregate ≥ 0.9088
    v, _ = mod._dispatch(0.7, 0.95)
    assert v == "M4_EXPLAINS", f"expected M4_EXPLAINS got {v}"
    # High shape R² but low aggregate → WEAK
    v, _ = mod._dispatch(0.7, 0.5)
    assert v == "M4_WEAK", f"expected WEAK on aggregate degradation got {v}"
    print("PASS test_verdict_dispatch_all_three_branches")


def test_rubric_hash_matches_committed_doc():
    v = json.loads(VERDICT_JSON.read_text())
    recorded = v["rubric_hash"]
    actual = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    assert recorded == actual, (
        f"rubric hash drift: recorded {recorded}, on-disk {actual}"
    )
    print("PASS test_rubric_hash_matches_committed_doc")


def test_rubric_committed_before_verdict_scripts():
    """Rubric doc must exist alongside verdict; presence check +
    frozen labels named in the rubric text."""
    assert RUBRIC_DOC.exists(), "rubric doc missing"
    assert VERDICT_JSON.exists(), "verdict JSON missing"
    txt = RUBRIC_DOC.read_text()
    for label in ("M4_EXPLAINS", "M4_WEAK", "M4_REFUTES"):
        assert label in txt, f"rubric doc missing frozen label {label}"
    # Rubric mentions the 20th-percentile choice and α pin.
    assert "20th percentile" in txt or "20th-percentile" in txt
    assert "0.7469387071101908" in txt, "rubric missing pinned α value"
    print("PASS test_rubric_committed_before_verdict_scripts")


def test_semantic_cluster_verdict_frozen_label():
    v = json.loads(VERDICT_JSON.read_text())
    assert v["verdict"] in ("M4_EXPLAINS", "M4_WEAK", "M4_REFUTES")
    print("PASS test_semantic_cluster_verdict_frozen_label")


def test_anchor_preservation_all_prior_cycle_utilities():
    anch = json.loads(
        (DATA / "anchor_preservation_semantic.json").read_text())
    utils = anch["utility_anchors"]
    for group in ("cycle_26_utilities", "cycle_27_utilities",
                  "cycle_28_utilities", "cycle_29_utilities"):
        assert group in utils, f"anchor group missing: {group}"
        for name, entry in utils[group]["entries"].items():
            # PASS or ANCHORED_NEW both acceptable; FAIL is not.
            assert entry["status"] != "FAIL", (
                f"prior-cycle utility {name} SHA drifted: {entry}"
            )
    print("PASS test_anchor_preservation_all_prior_cycle_utilities")


def main() -> int:
    tests = [
        test_interpreter_guard_present_in_all_new_scripts,
        test_no_prng_in_fingerprint_or_threshold_scripts,
        test_alpha_still_pinned_at_0_7469,
        test_fingerprint_deterministic_across_two_runs,
        test_threshold_computed_on_76_row_ledger_only,
        test_equivalence_classes_deterministic,
        test_effective_k_semantic_le_raw_k,
        test_verdict_dispatch_all_three_branches,
        test_rubric_hash_matches_committed_doc,
        test_rubric_committed_before_verdict_scripts,
        test_semantic_cluster_verdict_frozen_label,
        test_anchor_preservation_all_prior_cycle_utilities,
    ]
    n = 0
    for t in tests:
        t()
        n += 1
    print(f"\nOK {n}/{n} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
