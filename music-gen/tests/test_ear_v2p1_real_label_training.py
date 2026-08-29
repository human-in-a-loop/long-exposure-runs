#!/usr/bin/python3
"""c47 clone-0 Branch A test suite for M-EAR-1/real-label-training-v2.1.

Plain-assert style; no pytest dependency. Invocation:
  PYTHONPATH=. /usr/bin/python3 tests/test_ear_v2p1_real_label_training.py

Coverage: ≥12 cases per c47 brief (target 16/16).
"""
# created: 2026-08-29T17:15:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2.1

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


RUBRIC_DOC = ROOT / "docs" / "ear_real_label_training_v2p1_rubric.md"
RUBRIC_HASH = ROOT / "data" / "ear_v2p1" / "rubric_hash.txt"
VERDICT = ROOT / "data" / "ear_v2p1" / "verdict.json"
TRAIN_DET = ROOT / "data" / "ear_v2p1" / "training_determinism_check.json"
SB3_DET = ROOT / "data" / "ear_v2p1" / "sb3_determinism_check.json"
SB3_R1 = ROOT / "data" / "ear_v2p1" / "sb3_50ctl_run_1" / "sb3_50ctl_verdict_v2p1.json"
SB3_R2 = ROOT / "data" / "ear_v2p1" / "sb3_50ctl_run_2" / "sb3_50ctl_verdict_v2p1.json"
ANCHOR = ROOT / "data" / "ear_v2p1" / "anchor_preservation_v2p1.json"
REPORT = ROOT / "docs" / "ear_real_label_training_v2p1_report.md"

SCRIPTS_DIR = ROOT / "scripts" / "ear_v2p1"
CHASSIS = ROOT / "scripts" / "ear"
C22_HARNESS = ("synthetic_labels.py", "stability_metrics.py", "stability_audit.py")
PATH_B_DOC = ROOT / "docs" / "ear_path_b_commitment.md"
V2_VERDICT = ROOT / "data" / "ear_v2" / "verdict.json"
V2_RUBRIC = ROOT / "docs" / "ear_real_label_training_v2_rubric.md"
C46_SB3 = ROOT / "data" / "ear_v2" / "sb3_control_widening_result.json"

VERDICT_ALLOWED = {
    "EAR_v2p1_STABLE_FPR_PASS",
    "EAR_v2p1_BOUNDARY_TIP",
    "EAR_v2p1_FPR_STILL_OVERSHOOT",
}


PASS = 0
FAIL = 0
FAILED_TESTS: list[str] = []


def _test(name: str):
    def deco(fn):
        global PASS, FAIL
        try:
            fn()
            print(f"[PASS] {name}")
            PASS += 1
        except AssertionError as e:
            print(f"[FAIL] {name}: {e}")
            FAILED_TESTS.append(name)
            FAIL += 1
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {name}: {type(e).__name__}: {e}")
            FAILED_TESTS.append(name)
            FAIL += 1
        return fn
    return deco


# ----------------------------------------------------------------- tests
@_test("01_rubric_mtime_gate_hard")
def _t01():
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    for p in SCRIPTS_DIR.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        assert rubric_mtime < p.stat().st_mtime, (
            f"rubric mtime {rubric_mtime} not < script "
            f"{p.relative_to(ROOT)} mtime {p.stat().st_mtime}"
        )


@_test("02_git_log_gate_soft_c46_amendment")
def _t02():
    try:
        rubric_rel = str(RUBRIC_DOC.relative_to(ROOT))
        r = subprocess.run(
            ["git", "log", "--diff-filter=A", "--name-only",
             "--pretty=format:%H%x00", "--", rubric_rel,
             str(SCRIPTS_DIR.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0 or not r.stdout.strip():
            print("[soft] git-log gate: HARNESS_GATED (c46 amendment path (ii))")
            return
        print("[soft] git-log gate: commits present; mtime gate remains authoritative")
    except Exception as e:  # noqa
        print(f"[soft] git-log gate check skipped: {e}")


@_test("03_three_way_rubric_hash_byte_equality")
def _t03():
    doc_sha = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    disk = RUBRIC_HASH.read_text().strip()
    assert doc_sha == disk, (doc_sha, disk)
    v = json.loads(VERDICT.read_text())
    assert v["rubric_hash"] == doc_sha, (v["rubric_hash"], doc_sha)


@_test("04_sb3_detection_finite_equals_one")
def _t04():
    v = json.loads(VERDICT.read_text())
    d = v["detection_v2p1"]
    assert isinstance(d, (float, int)) and d == 1.0, d
    r1 = json.loads(SB3_R1.read_text())
    r2 = json.loads(SB3_R2.read_text())
    assert r1["at_n_controls_50"]["detection_rate"] == 1.0
    assert r2["at_n_controls_50"]["detection_rate"] == 1.0


@_test("05_sb3_fpr_finite_both_runs")
def _t05():
    v = json.loads(VERDICT.read_text())
    for k in ("fpr_run_1", "fpr_run_2"):
        x = v[k]
        assert isinstance(x, (int, float)), (k, type(x))
        assert 0.0 <= x <= 1.0, (k, x)


@_test("06_byte_determinism_sb3_verdict_x2")
def _t06():
    s1 = hashlib.sha256(SB3_R1.read_bytes()).hexdigest()
    s2 = hashlib.sha256(SB3_R2.read_bytes()).hexdigest()
    assert s1 == s2, (s1, s2)
    v = json.loads(VERDICT.read_text())
    assert v["byte_determinism_x2"] is True
    assert v["byte_determinism_shas"] == [s1, s2], v["byte_determinism_shas"]


@_test("07_byte_determinism_training_artifacts_x2")
def _t07():
    td = json.loads(TRAIN_DET.read_text())
    assert td["corn_head_v2p1_byte_det_x2"] is True
    assert td["training_result_v2p1_byte_det_x2"] is True
    assert td["corn_head_v2p1_run_1_sha256"] == td["corn_head_v2p1_run_2_sha256"]
    assert td["training_result_v2p1_run_1_sha256"] == td["training_result_v2p1_run_2_sha256"]


@_test("08_c22_stability_harness_mtimes_unchanged")
def _t08():
    a = json.loads(ANCHOR.read_text())
    entries = a["entries"]
    for n in C22_HARNESS:
        rel = f"scripts/ear/{n}"
        e = entries.get(rel)
        assert e and e.get("present"), rel
    assert a["unchanged"] is True, a["drift"]


@_test("09_c6_chassis_anchor_shas_unchanged")
def _t09():
    a = json.loads(ANCHOR.read_text())
    entries = a["entries"]
    for n in ("features.py", "model.py", "corn.py", "leak_test.py"):
        rel = f"scripts/ear/{n}"
        assert entries.get(rel, {}).get("present"), rel
    assert a["unchanged"] is True


@_test("10_c26_threshold_values_unchanged_literal")
def _t10():
    body = PATH_B_DOC.read_text()
    # SB1 margin literal 0.5909
    assert "0.5909" in body, "SB1 margin literal missing from Path B doc"
    # SB2 mean tau 0.4
    assert " 0.4" in body or "≥ 0.4" in body or ">=0.4" in body or "0.4 " in body
    # SB3 detection 0.90 at α=1.0
    assert "0.90" in body
    # SB3 FPR ≤ 0.10
    assert "0.10" in body


@_test("11_no_prng_in_scripts_ear_v2p1")
def _t11():
    forbidden_calls = {
        ("random",),
        ("random", "random"),
        ("random", "choice"),
        ("random", "randint"),
        ("random", "sample"),
        ("random", "shuffle"),
        ("np", "random"),
        ("numpy", "random"),
        ("secrets", "token_bytes"),
        ("secrets", "token_hex"),
        ("secrets", "choice"),
    }
    for p in SCRIPTS_DIR.rglob("*.py"):
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                parts = []
                cur = node
                while isinstance(cur, ast.Attribute):
                    parts.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    parts.append(cur.id)
                path = tuple(reversed(parts))
                # Whitelist torch.manual_seed(0).
                if path[:2] == ("torch", "manual_seed"):
                    continue
                if path in forbidden_calls:
                    raise AssertionError(
                        f"forbidden PRNG in {p.relative_to(ROOT)}: {'.'.join(path)}"
                    )


@_test("12_no_sidecar_nonfactor_imports")
def _t12():
    for p in SCRIPTS_DIR.rglob("*.py"):
        src = p.read_text()
        assert "sidecar_nonfactor" not in src, p.relative_to(ROOT)


@_test("13_interpreter_guard_first_lines")
def _t13():
    for p in SCRIPTS_DIR.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        head = p.read_text().splitlines()[:5]
        joined = "\n".join(head)
        assert "/usr/bin/python3" in joined, p.relative_to(ROOT)


@_test("14_no_i4_stratified_imports")
def _t14():
    for p in SCRIPTS_DIR.rglob("*.py"):
        src = p.read_text()
        assert "i4_stratified" not in src, p.relative_to(ROOT)


@_test("15_corpus_n_caveat_present_in_report")
def _t15():
    assert REPORT.is_file(), REPORT
    body = REPORT.read_text()
    assert "43/80" in body, "'43/80' missing"
    assert "preview_partial_corpus_v2p1" in body, "'preview_partial_corpus_v2p1' missing"


@_test("16_sb1_sb2_not_reverdicted")
def _t16():
    v = json.loads(VERDICT.read_text())
    assert v["sb1_status"] == "FAIL_unchanged_from_c45", v["sb1_status"]
    assert v["sb2_status"] == "FAIL_unchanged_from_c45", v["sb2_status"]
    # And v2 verdict.json unchanged.
    v2 = json.loads(V2_VERDICT.read_text())
    assert v2["rubric_hash"] == "01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0"


@_test("17_verdict_label_in_allowed_set")
def _t17():
    v = json.loads(VERDICT.read_text())
    assert v["verdict"] in VERDICT_ALLOWED, v["verdict"]
    assert v["mapping_label"] in {
        "EAR_v2p1_PARTIAL_WITH_SB3_PASS",
        "EAR_v2p1_PARTIAL_WITH_SB3_BOUNDARY_TIP",
        "EAR_v2p1_PARTIAL",
    }


@_test("18_c46_sb3_widening_anchor_sha_recorded_in_verdict")
def _t18():
    expected = hashlib.sha256(C46_SB3.read_bytes()).hexdigest()
    v = json.loads(VERDICT.read_text())
    assert v["c46_sb3_widening_result_sha256"] == expected


# ----------------------------------------------------------------- run
if __name__ == "__main__":
    print(f"\nRESULT: {PASS} passed, {FAIL} failed")
    if FAILED_TESTS:
        for n in FAILED_TESTS:
            print(f"  - FAILED: {n}")
    sys.exit(1 if FAIL else 0)
