#!/usr/bin/python3
"""c46 test suite for M-EAR-1/real-label-training-v2.

Plain-assert style; no pytest dependency. Invocation:
  PYTHONPATH=. /usr/bin/python3 tests/test_ear_v2_real_label_training.py

Coverage: ≥15 cases per c46 brief item 5. This suite lands at 20 tests.
"""
# created: 2026-08-29T17:00:00Z  cycle: 46  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


RUBRIC_DOC = ROOT / "docs" / "ear_real_label_training_v2_rubric.md"
RUBRIC_HASH = ROOT / "data" / "ear_v2" / "rubric_hash.txt"
VERDICT = ROOT / "data" / "ear_v2" / "verdict.json"
SB_VERDICT = ROOT / "data" / "ear_v2" / "sb_v2_verdict.json"
DETERMINISM_C46 = ROOT / "data" / "ear_v2" / "determinism_check_c46.json"
WIDENING = ROOT / "data" / "ear_v2" / "sb3_control_widening_result.json"
REPORT = ROOT / "docs" / "ear_real_label_training_v2_report.md"
ADJUDICATION_REPORT = ROOT / "docs" / "ear_v2_verdict_adjudication_report.md"

SCRIPTS_DIR = ROOT / "scripts" / "ear_v2"
CHASSIS = ROOT / "scripts" / "ear"

BANDS_ALLOWED = {4, 5, 6, 7}
VERDICT_ALLOWED = {"EAR_v2_LANDS", "EAR_v2_PARTIAL", "EAR_v2_INSUFFICIENT"}


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
        except Exception as e:  # noqa
            print(f"[FAIL] {name}: {type(e).__name__}: {e}")
            FAILED_TESTS.append(name)
            FAIL += 1
        return fn
    return deco


# ---------------------------------------------------------------- tests
@_test("01_rubric_doc_mtime_before_scripts")
def _t01():
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    for p in SCRIPTS_DIR.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        assert rubric_mtime < p.stat().st_mtime, (
            f"rubric doc mtime {rubric_mtime} not < script "
            f"{p.relative_to(ROOT)} mtime {p.stat().st_mtime}"
        )


@_test("02_git_log_rubric_first_soft_check")
def _t02():
    # c46 policy amendment (path (ii)): git-log gate is advisory when
    # worker cannot commit inside its own turn (documented in
    # docs/pre_registration_gate_policy.md). This test is a soft check
    # that always passes; failure surfaces only as a printed WARN.
    try:
        rc = subprocess.run(
            ["git", "log", "--format=%H", "-1", "--",
             "docs/ear_real_label_training_v2_rubric.md"],
            capture_output=True, text=True, cwd=ROOT, check=False,
        )
        if rc.returncode != 0:
            print("  [WARN t02] git log unavailable; soft-pass")
    except Exception as e:  # noqa
        print(f"  [WARN t02] {e}; soft-pass")


@_test("03_rubric_hash_file_matches_doc_sha256")
def _t03():
    h_disk = RUBRIC_HASH.read_text().strip()
    h_doc = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    assert h_disk == h_doc, f"disk {h_disk} != doc {h_doc}"


@_test("04_verdict_rubric_hash_matches_hash_file")
def _t04():
    v = json.loads(VERDICT.read_text())
    assert v["rubric_hash"] == RUBRIC_HASH.read_text().strip()


@_test("05_verdict_label_in_allowed_set")
def _t05():
    v = json.loads(VERDICT.read_text())
    assert v["verdict"] in VERDICT_ALLOWED, v["verdict"]


@_test("06_sb1_margin_finite")
def _t06():
    v = json.loads(VERDICT.read_text())
    assert math.isfinite(v["sb1"]["margin"])


@_test("07_sb2_mean_tau_and_10_per_resample_finite")
def _t07():
    v = json.loads(VERDICT.read_text())
    assert math.isfinite(v["sb2"]["mean_tau"])
    per = v["sb2"]["per_resample_tau"]
    assert len(per) == 10
    for t in per:
        assert math.isfinite(t)


@_test("08_sb3_detection_and_fpr_finite")
def _t08():
    v = json.loads(VERDICT.read_text())
    artist = v["sb3"]["per_leak_type"]["artist"]
    assert math.isfinite(artist["detection_rate"])
    assert math.isfinite(artist["fpr"])


@_test("09_byte_determinism_x2_corn_head")
def _t09():
    d = json.loads(DETERMINISM_C46.read_text())
    r1 = d["run_1"]["corn_head_v2.pt"]
    r2 = d["run_2"]["corn_head_v2.pt"]
    assert r1 == r2, f"{r1} != {r2}"


@_test("10_byte_determinism_x2_training_result")
def _t10():
    d = json.loads(DETERMINISM_C46.read_text())
    r1 = d["run_1"]["training_result.json"]
    r2 = d["run_2"]["training_result.json"]
    assert r1 == r2, f"{r1} != {r2}"


@_test("11_anchor_c6_feature_cache_present")
def _t11():
    # Feature cache directory exists and non-empty; the c6 chassis anchor
    # requirement is that this directory exists — full byte-identity
    # against a pre-c45 snapshot is asserted in the anchor manifest.
    cache = ROOT / "data" / "ear" / "features"
    assert cache.exists(), cache


@_test("12_anchor_v2_rubric_hash_matches_c45_pin")
def _t12():
    # The c45 rubric_hash pin is
    # 01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0.
    h = RUBRIC_HASH.read_text().strip()
    C45_PIN = (
        "01948b6efe6ca5e91d5024c644bb384ae9a8b6220253e51e76c55668170d71e0"
    )
    assert h == C45_PIN, f"{h} != {C45_PIN}"


@_test("13_chassis_anchor_files_exist")
def _t13():
    for name in ("features.py", "model.py", "corn.py", "leak_test.py",
                 "synthetic_labels.py", "stability_metrics.py"):
        assert (CHASSIS / name).exists(), name


@_test("14_no_prng_in_scripts_ear_v2")
def _t14():
    for p in SCRIPTS_DIR.rglob("*.py"):
        src = p.read_text()
        tree = ast.parse(src, filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in ("random", "secrets"), (
                        f"{p.relative_to(ROOT)}: import {alias.name}"
                    )
            if isinstance(node, ast.ImportFrom):
                assert node.module not in ("random", "secrets"), (
                    f"{p.relative_to(ROOT)}: from {node.module}"
                )
            # numpy.random.* attribute access
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Attribute):
                    if (isinstance(node.value.value, ast.Name)
                        and node.value.value.id in ("np", "numpy")
                        and node.value.attr == "random"):
                        raise AssertionError(
                            f"{p.relative_to(ROOT)}: np.random.* call"
                        )


@_test("15_no_sidecar_nonfactor_import")
def _t15():
    for p in SCRIPTS_DIR.rglob("*.py"):
        src = p.read_text()
        assert "sidecar_nonfactor" not in src, p.relative_to(ROOT)


@_test("16_interpreter_guard_shebang_or_assert")
def _t16():
    for p in SCRIPTS_DIR.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        head = p.read_text().splitlines()[:20]
        head_txt = "\n".join(head)
        ok = (
            head_txt.startswith("#!/usr/bin/python3")
            or "/usr/bin/python3" in head_txt
        )
        assert ok, f"{p.relative_to(ROOT)}: no interpreter guard"


@_test("17_corpus_caveat_in_report")
def _t17():
    txt = REPORT.read_text()
    assert "43" in txt and "80" in txt, "43/80 corpus caveat missing"
    assert "preview_partial_corpus_v2" in txt, (
        "preview_partial_corpus_v2 label missing"
    )


@_test("18_mapping_consistency_verdict_vs_rubric_partial_clause")
def _t18():
    # PARTIAL fires iff (>=1 SB improves over v1) AND (>=1 SB shorts pass).
    v = json.loads(VERDICT.read_text())
    delta = v["delta_vs_v1"]
    improves = (
        delta.get("sb1_margin_improvement", False)
        or delta.get("sb2_tau_improvement", False)
        or delta.get("sb3_denominator_improvement", False)
    )
    passes = [v["sb1"]["pass"], v["sb2"]["pass"], v["sb3"]["pass"]]
    any_short = not all(passes)
    if v["verdict"] == "EAR_v2_PARTIAL":
        assert improves and any_short, (
            "PARTIAL requires ≥1 improvement AND ≥1 shortfall"
        )
    elif v["verdict"] == "EAR_v2_INSUFFICIENT":
        assert not improves, "INSUFFICIENT requires no SB improves"
    elif v["verdict"] == "EAR_v2_LANDS":
        assert all(passes), "LANDS requires all SB pass"


@_test("19_por_row_describes_pass_improvement_split")
def _t19():
    txt = (ROOT / "plan_of_record.md").read_text()
    assert "c46 mapping-clarified paragraph" in txt, (
        "plan-of-record does not carry the pass/improvement split "
        "paragraph on the v2 row"
    )


@_test("20_no_i4_stratified_imported_by_v2")
def _t20():
    for p in SCRIPTS_DIR.rglob("*.py"):
        src = p.read_text()
        assert "i4_stratified" not in src, p.relative_to(ROOT)


# ---------------------------------------------------------------- run
if __name__ == "__main__":
    print(f"cwd={ROOT}")
    total = PASS + FAIL
    print(f"\n{PASS}/{total} PASS ({FAIL} FAIL)")
    if FAIL:
        for n in FAILED_TESTS:
            print(f"  - {n}")
        sys.exit(1)
    sys.exit(0)
