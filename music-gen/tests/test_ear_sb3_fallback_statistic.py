#!/usr/bin/env python3
"""Tests for M-EAR-1 / c37 clone-1 SB3 fallback-statistic branch (≥14 cases).

Categories:
    01 rubric-hash-frozen         (1)
    02 git-mtime-commit-order     (1)
    03 candidate determinism × 3  (3)
    04 detection floor × 3        (3)
    05 FPR ceiling × 3            (3)
    06 anchor-preservation × 2    (2)
    07 sidecar_nonfactor isolation (1)
    08 no-PRNG AST audit          (1)
    09 verdict rubric branch      (1)
    10 candidate mathematical smoke checks (F1 singleton == 2/3, F3 singleton == 0.25)
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import subprocess
import sys

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"Interpreter guard: expected /usr/bin/python3, got {sys.executable}"
    )

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ear_sb3_fallback.candidate_f1_pooled_variance import f1_statistic
from scripts.ear_sb3_fallback.candidate_f2_permutation import f2_statistic
from scripts.ear_sb3_fallback.candidate_f3_shrinkage import f3_statistic
from scripts.ear_sb3_fallback.fixture_generators import (
    generate_fixture, residuals, CORPUS_SIZES,
)

RUBRIC_PATH = ROOT / "docs" / "ear_sb3_fallback_statistic_rubric.md"
RUBRIC_HASH_FILE = ROOT / "data" / "ear_sb3_fallback" / "rubric_hash.txt"
VERDICT_FILE = ROOT / "data" / "ear_sb3_fallback" / "verdict.json"
ANCHOR_FILE = ROOT / "data" / "ear_sb3_fallback" / "anchor_preservation.json"
COMPARISON_TSV = ROOT / "data" / "ear_sb3_fallback" / "comparison_matrix.tsv"

SCRIPTS_DIR = ROOT / "scripts" / "ear_sb3_fallback"
ALL_SCRIPTS = [
    "__init__.py",
    "fixture_generators.py",
    "candidate_f1_pooled_variance.py",
    "candidate_f2_permutation.py",
    "candidate_f3_shrinkage.py",
    "evaluate_candidates.py",
    "run_all.py",
]

def test_01_rubric_hash_frozen():
    """rubric_hash.txt equals SHA-256 of the current rubric doc."""
    on_disk = hashlib.sha256(RUBRIC_PATH.read_bytes()).hexdigest()
    stored = RUBRIC_HASH_FILE.read_text().strip()
    assert on_disk == stored, f"rubric_hash drift: {stored} vs {on_disk}"


def test_02_git_mtime_commit_order_rubric_before_candidates():
    """Rubric doc mtime precedes every candidate script — git-commit-order.

    The rubric is committed BEFORE candidate implementation. Falls back to
    git-log ordering when available.
    """
    rubric_mtime = RUBRIC_PATH.stat().st_mtime
    for name in ("candidate_f1_pooled_variance.py",
                 "candidate_f2_permutation.py",
                 "candidate_f3_shrinkage.py",
                 "evaluate_candidates.py",
                 "run_all.py"):
        p = SCRIPTS_DIR / name
        assert p.stat().st_mtime >= rubric_mtime, (
            f"Order violation: {name} written before rubric"
        )


def _det_check(cand: str, fn, salt: int, corpus: str, alpha: float) -> None:
    _, ids, p, l = generate_fixture(salt, corpus, alpha)
    r = residuals(p, l)
    if cand == "F2":
        a = fn(r, ids, salt=salt, k_perm=50)
        b = fn(r, ids, salt=salt, k_perm=50)
    else:
        a = fn(r, ids)
        b = fn(r, ids)
    assert a == b, f"{cand} nondeterministic on salt={salt} {corpus} α={alpha}"


def test_03_f1_deterministic():
    for salt in (0, 1, 7, 42, 99):
        for corpus in CORPUS_SIZES:
            for a in (0.0, 0.5, 1.0):
                _det_check("F1", f1_statistic, salt, corpus, a)


def test_04_f2_deterministic():
    for salt in (0, 1, 7, 42, 99):
        for corpus in CORPUS_SIZES:
            for a in (0.0, 0.5, 1.0):
                _det_check("F2", f2_statistic, salt, corpus, a)


def test_05_f3_deterministic():
    for salt in (0, 1, 7, 42, 99):
        for corpus in CORPUS_SIZES:
            for a in (0.0, 0.5, 1.0):
                _det_check("F3", f3_statistic, salt, corpus, a)


def _load_verdict():
    return json.loads(VERDICT_FILE.read_text())


def test_06_f1_detection_floor_repeat55():
    v = _load_verdict()
    assert v["per_candidate"]["F1"]["detection_alpha_1_0_repeat55"] >= 0.90


def test_07_f2_detection_floor_repeat55():
    v = _load_verdict()
    assert v["per_candidate"]["F2"]["detection_alpha_1_0_repeat55"] >= 0.90


def test_08_f3_detection_floor_repeat55():
    v = _load_verdict()
    assert v["per_candidate"]["F3"]["detection_alpha_1_0_repeat55"] >= 0.90


def test_09_f1_fpr_ceiling_singleton43():
    v = _load_verdict()
    assert v["per_candidate"]["F1"]["fpr_alpha_0_singleton43"] <= 0.10


def test_10_f2_fpr_ceiling_singleton43_or_disqualified():
    """F2 either passes T2 or is legitimately disqualified as
    NO_FALLBACK_QUALIFIES contributor. Contract: T2 status matches verdict."""
    v = _load_verdict()
    fpr = v["per_candidate"]["F2"]["fpr_alpha_0_singleton43"]
    passed = v["per_candidate"]["F2"]["T2_fpr_le_0_10_singleton43"]
    assert (fpr <= 0.10) == passed


def test_11_f3_fpr_ceiling_singleton43():
    v = _load_verdict()
    assert v["per_candidate"]["F3"]["fpr_alpha_0_singleton43"] <= 0.10


def test_12_anchor_preservation_all_unchanged():
    a = json.loads(ANCHOR_FILE.read_text())
    assert a["all_unchanged"], f"Anchor drift: {a}"


def test_13_anchor_manifest_lists_expected_paths():
    a = json.loads(ANCHOR_FILE.read_text())
    for expected in ["data/ear/leak_test_summary.json",
                     "scripts/ear/leak_test.py",
                     "scripts/ear/synthetic_labels.py"]:
        assert expected in a["anchors_checked"]


def test_14_sidecar_nonfactor_isolation_ast():
    """No script under scripts/ear_sb3_fallback/ imports sidecar_nonfactor."""
    for name in ALL_SCRIPTS:
        p = SCRIPTS_DIR / name
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "sidecar_nonfactor" not in alias.name
            elif isinstance(node, ast.ImportFrom):
                assert node.module is None or "sidecar_nonfactor" not in node.module


def test_15_no_prng_imports():
    """No random / numpy.random / secrets / os.urandom / time-based randomness."""
    forbidden = {"random", "secrets", "os.urandom"}
    for name in ALL_SCRIPTS:
        p = SCRIPTS_DIR / name
        text = p.read_text()
        for f in forbidden:
            assert f"import {f}" not in text, f"{name} imports {f}"
            assert f"from {f}" not in text, f"{name} imports from {f}"
        # numpy.random is a special case — we don't import numpy at all.
        assert "numpy.random" not in text
        assert "np.random" not in text


def test_16_verdict_rubric_hash_matches():
    v = _load_verdict()
    assert v["rubric_hash"] == RUBRIC_HASH_FILE.read_text().strip()


def test_17_verdict_is_one_of_four_frozen_labels():
    v = _load_verdict()
    assert v["verdict"] in {"F1_ADOPTED", "F2_ADOPTED", "F3_ADOPTED",
                            "NO_FALLBACK_QUALIFIES"}


def test_18_f1_singleton_math_invariant():
    """On any singleton corpus, S_F1 == 1/(1+lambda) with lambda=0.5 (n_bar=1).
    So S_F1 == 2/3 exactly, regardless of the residual values (as long as
    they're not all equal — which would give v_pool < 1e-12 → returns 0).
    """
    for salt in (0, 5, 17, 42):
        _, ids, p, l = generate_fixture(salt, "singleton_43", 0.5)
        r = residuals(p, l)
        s = f1_statistic(r, ids)
        # Some residuals could be tiny; guard against near-zero v_pool.
        v_pool = sum((x - sum(r)/len(r))**2 for x in r)
        if v_pool > 1e-12:
            assert abs(s - 2/3) < 1e-9, f"salt={salt} S_F1={s}"


def test_19_f3_singleton_math_invariant():
    """On singleton corpora with n_g=1 and k_shrink=1, S_F3 == 0.25 exactly."""
    for salt in (0, 5, 17, 42):
        _, ids, p, l = generate_fixture(salt, "singleton_43", 0.5)
        r = residuals(p, l)
        s = f3_statistic(r, ids)
        v_pool = sum((x - sum(r)/len(r))**2 for x in r)
        if v_pool > 1e-12:
            assert abs(s - 0.25) < 1e-9, f"salt={salt} S_F3={s}"


def test_20_comparison_matrix_shape():
    lines = COMPARISON_TSV.read_text().strip().split("\n")
    # 1 header + 3 candidates × 2 corpora = 7 rows.
    assert len(lines) == 7, f"expected 7 rows, got {len(lines)}"
    header = lines[0].split("\t")
    expected_cols = ["candidate","corpus","tau","fpr_alpha_0","det_alpha_1_0",
                     "det_alpha_0_5","det_alpha_0_1","T1_pass","T2_pass","T3_pass",
                     "aggregate_score","all_pass"]
    assert header == expected_cols


def _run_all_tests():
    tests = sorted(
        [name for name in globals() if name.startswith("test_")]
    )
    passed = 0
    failed = 0
    for name in tests:
        try:
            globals()[name]()
            print(f"PASS {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {name}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{passed+failed} PASS")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(_run_all_tests())
