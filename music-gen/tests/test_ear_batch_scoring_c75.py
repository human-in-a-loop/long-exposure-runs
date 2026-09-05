#!/usr/bin/env /usr/bin/python3
"""c75 P7 — Tests for score_gen_batch + probes.

Validates:
  1. score_gen_batch.py exists with expected surface + halt-honest sidecar path.
  2. band4_spot_check.json has expected schema.
  3. calibration_saturation_probe.json has expected schema.
  4. Selection sidecar has str supersedes_path per c14 lemma.
  5. Blocker sidecar has expected schema + honest verdict.
  6. LOO code does NOT self-include (grep-verified).
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_json(rel: str) -> dict:
    p = ROOT / rel
    assert p.exists(), f"missing {rel}"
    return json.loads(p.read_text())


def test_01_batch_scorer_present_with_expected_surface():
    p = ROOT / "scripts/ear/score_gen_batch.py"
    assert p.exists(), "score_gen_batch.py must exist"
    src = p.read_text()
    for tok in ["find_gen_ab_mix_files", "write_blocker_sidecar",
                "_try_load_vggish", "--unblocked", "HALT_HONEST_BLOCKED"]:
        assert tok in src, f"missing marker: {tok}"


def test_02_batch_scorer_no_prng_no_sidecar_nonfactor():
    src = (ROOT / "scripts/ear/score_gen_batch.py").read_text()
    assert "import random" not in src, "no PRNG"
    assert "sidecar_nonfactor" not in src, "no sidecar_nonfactor"
    assert "get_state" not in src and "save_state" not in src, "no VST3 state APIs"


def test_03_band4_spot_check_schema():
    d = _load_json("data/v4/ear/band4_spot_check_c75.json")
    for k in ["cycle", "backbone", "loo_scores", "band4_scores",
              "mandate_threshold_loo_min_minus_0p5", "gate_passes",
              "env_pin_sha256"]:
        assert k in d, f"band4 missing {k}"
    assert d["cycle"] == 75
    assert d["backbone"] == "vggish_only"
    assert d["env_pin_sha256"].startswith("2ac444c3")


def test_04_calibration_probe_schema():
    d = _load_json("data/v4/ear/calibration_saturation_probe_c75.json")
    for k in ["variants", "saturation_diagnosis", "raw_stats"]:
        assert k in d
    for v in ["current_linear_anchor", "sigmoid_dampen_0p9_ceiling", "percentile_5corpus"]:
        assert v in d["variants"]
    # Confirms P3.a — no self-include bug documented
    assert "P3a_loo_self_include_bug_check" in d["notes"]
    assert "PASS_no_bug" in d["notes"]["P3a_loo_self_include_bug_check"]


def test_05_selection_sidecar_str_supersedes_per_c14_lemma():
    d = _load_json("data/v4/ear/_selection/exemplar-band-metadata-realignment-c75.json")
    assert isinstance(d["supersedes_path"], str), "c14 lemma: str not list"
    assert d["supersedes_path"] == "M-V4-EAR-1/exemplar-sha16-resolved"


def test_06_blocker_sidecar_honest_verdict():
    d = _load_json("data/v4/gen/batch_score_blocker_c75.json")
    assert d["verdict"] == "HALT_HONEST_BLOCKED_ON_CALIBRATION_AND_INFRA"
    assert d["gen_rows_enumerated"] == 15, f"expected 15 gen rows, got {d['gen_rows_enumerated']}"
    assert d["manifests_modified_this_cycle"] == 0, "P4 halt-honest: no manifests modified"


def test_07_loo_no_self_include_bug_grep():
    src = (ROOT / "scripts/ear/v4_ear.py").read_text()
    # Verify the remaining dict comp excludes held_out
    assert re.search(r"remaining\s*=\s*\{.*k\s*!=\s*held_out.*\}", src), (
        "LOO code must exclude held_out from remaining bank")


def test_08_env_pin_canonical_across_c75_artifacts():
    canonical = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
    for rel in ["data/v4/ear/band4_spot_check_c75.json",
                "data/v4/ear/calibration_saturation_probe_c75.json",
                "data/v4/ear/_selection/exemplar-band-metadata-realignment-c75.json",
                "data/v4/gen/batch_score_blocker_c75.json"]:
        d = _load_json(rel)
        assert d.get("env_pin_sha256") == canonical, f"env_pin drift in {rel}"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} PASS")
    sys.exit(0 if passed == len(tests) else 1)
