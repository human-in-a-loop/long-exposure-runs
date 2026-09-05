#!/usr/bin/env /usr/bin/python3
"""M-V4-EAR-1 c73 scaffold tests.

Verifies contract of the scaffold-only module (real inference deferred to c74+):
  test_01_module_imports_and_stubs_raise
  test_02_exemplar_set_structural_validation
  test_03_spec_compliant_window_size_constant
  test_04_no_prng_no_sidecar_no_vst3_state
  test_05_env_pin_manifest_canonical
"""
from __future__ import annotations
import ast
import json
import os
import sys
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
    "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ear import v4_ear as VE


def test_01_module_imports_and_substantive_api_present() -> None:
    """c74 substantive-landing supersede of c73 scaffold-stubs-raise test.

    c73 scaffold declared NotImplementedError; c74 wired the API to load
    pre-existing VGGish embeddings + score. Substantive impl asserted here:
    build_exemplar_signatures returns non-empty dict; leave_one_out returns
    per-exemplar float scores.
    """
    assert hasattr(VE, "build_exemplar_signatures")
    assert hasattr(VE, "score_audio")
    assert hasattr(VE, "leave_one_out")
    es = VE.load_exemplar_set()
    sigs = VE.build_exemplar_signatures(es)
    assert isinstance(sigs, dict) and len(sigs) == 5, f"expected 5 exemplar signatures, got {len(sigs)}"
    scores = VE.leave_one_out(es, sigs)
    assert isinstance(scores, dict) and len(scores) == 5, f"expected 5 loo scores, got {len(scores)}"
    for k, v in scores.items():
        assert isinstance(v, float) and 1.0 <= v <= 7.0, f"{k}: score {v} out of [1,7]"


def test_02_exemplar_set_structural_validation() -> None:
    with open(VE.EXEMPLAR_SET_PATH, "r", encoding="utf-8") as f:
        es = json.load(f)
    assert len(es["exemplars"]) == 5, "must be exactly 5 exemplars per campaign L112"
    ids = {e["id"] for e in es["exemplars"]}
    expected = {"chicken_grease", "molasses", "essence", "desire", "peach_dream"}
    assert ids == expected, f"exemplar ids mismatch: {ids} != {expected}"
    # CG + PD sha16 must be resolved (both are in operator focus set)
    resolved = {e["id"]: e["sha16"] for e in es["exemplars"]}
    assert resolved["chicken_grease"] == "31a164f845f8e27e"
    assert resolved["peach_dream"] == "88d247468cb6d49f"
    # Scoring block matches spec constants
    sc = es["scoring"]
    assert sc["window_seconds"] == 10
    assert sc["best_fraction"] == 0.5
    assert sc["aggregate"] == "max_over_exemplar_windows"
    assert sc["corpus_calibration"] == "explicitly_disabled_per_operator_simplification_2026-09-03"
    # Sanity gate matches campaign L115-117
    sg = es["sanity_gate"]
    assert sg["min_pass_count"] == 4
    assert sg["min_pass_score"] == 6.0
    assert sg["no_exemplar_below"] == 5.5


def test_03_spec_compliant_window_size_constant() -> None:
    assert VE.WINDOW_SECONDS == 10, "spec-mandated window size 10 s (campaign L114)"
    assert VE.BEST_FRACTION == 0.5, "spec-mandated best 50% (campaign L114)"
    assert VE.RATING_ANCHOR_HIGH == 7
    assert VE.RATING_ANCHOR_LOW == 1
    assert VE.SAMPLE_RATE == 44100


def test_04_no_prng_no_sidecar_no_vst3_state() -> None:
    src = Path(VE.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned_imports = {"random", "sidecar_nonfactor"}
    banned_names = {"get_state", "save_state", "save_preset", "load_state", "set_state"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for al in node.names:
                assert al.name.split(".")[0] not in banned_imports, f"banned import: {al.name}"
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in banned_imports, f"banned import from: {node.module}"
        elif isinstance(node, ast.Attribute) and node.attr in banned_names:
            # Names appearing as attrs are banned VST3 state calls
            raise AssertionError(f"banned VST3 state attr: {node.attr}")


def test_05_env_pin_manifest_canonical() -> None:
    m = VE._module_env_manifest()
    assert m["env_pin_sha256"] == "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
    for key in ("PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
                "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        assert key in m["env_pins"], f"missing env pin: {key}"
    assert m["window_seconds"] == 10
    assert m["best_fraction"] == 0.5


def main() -> int:
    tests = [
        ("test_01_module_imports_and_substantive_api_present", test_01_module_imports_and_substantive_api_present),
        ("test_02_exemplar_set_structural_validation", test_02_exemplar_set_structural_validation),
        ("test_03_spec_compliant_window_size_constant", test_03_spec_compliant_window_size_constant),
        ("test_04_no_prng_no_sidecar_no_vst3_state", test_04_no_prng_no_sidecar_no_vst3_state),
        ("test_05_env_pin_manifest_canonical", test_05_env_pin_manifest_canonical),
    ]
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS {name}")
        except AssertionError as e:
            print(f"  FAIL {name}: {e}")
            failures += 1
        except Exception as e:
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
            failures += 1
    print(f"{len(tests) - failures}/{len(tests)} PASS")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
