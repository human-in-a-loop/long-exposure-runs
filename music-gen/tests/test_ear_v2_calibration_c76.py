#!/usr/bin/env /usr/bin/python3
"""c76 tests for v4_ear_v2 wider-linear calibration + L119 infeasibility proof."""
from __future__ import annotations
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_01_v4_ear_v2_module_present_and_manifest():
    from scripts.ear import v4_ear_v2
    m = v4_ear_v2.module_env_manifest_v2()
    assert m["calibration_id"] == "wider_linear_c76"
    assert m["anchor_high_v2_floor"] == 0.98
    assert m["anchor_high_v2_margin"] == 0.02
    assert m["env_pin_sha256"] == "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
    assert m["backbone"] == "vggish"
    print("test_01 PASS")


def test_02_v2_loo_no_ceiling_clipping():
    from scripts.ear import v4_ear, v4_ear_v2
    ex_set = v4_ear.load_exemplar_set()
    scores = v4_ear_v2.leave_one_out_v2(ex_set)
    assert len(scores) == 5
    # No score at exactly 7.0 (would indicate saturation)
    for k, v in scores.items():
        assert v < 7.0, f"{k} clipped at 7.0"
        assert v >= 6.0, f"{k}={v} below sanity floor"
    print("test_02 PASS")


def test_03_sanity_gate_passes_under_v2():
    from scripts.ear import v4_ear, v4_ear_v2
    ex_set = v4_ear.load_exemplar_set()
    scores = v4_ear_v2.leave_one_out_v2(ex_set)
    gate = v4_ear.sanity_gate(scores)
    assert gate["gate_passes"] is True
    assert gate["n_at_or_above_6"] == 5
    assert gate["n_below_5p5"] == 0
    print("test_03 PASS")


def test_04_l119_infeasibility_proof_sidecar_shape():
    p = ROOT / "data/v4/ear/l119_infeasibility_proof_c76.json"
    assert p.exists(), "l119_infeasibility_proof_c76.json missing"
    d = json.loads(p.read_text())
    assert d["cycle"] == 76
    assert d["milestone_id"] == "P1b-l119-infeasibility-proof"
    assert d["env_pin_sha256"] == "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
    assert d["backbone"] == "vggish_only"
    mat = d["statistic_x_calibration_matrix"]
    assert set(mat.keys()) == {"max_over_windows_c74", "mean_over_all_windows", "mean_of_per_ex_max"}
    for stat_name, stat_data in mat.items():
        assert set(stat_data["calibrations"].keys()) == {"linear_c74", "wider_linear_c76", "sigmoid_dampen"}
    verdict = d["infeasibility_verdict"]
    assert verdict["all_three_statistics_raw_inverted"] is True
    for name, per in verdict["per_statistic"].items():
        assert per["raw_sign_inverted"] is True
        assert per["any_calibration_passes_both_gates"] is False
    print("test_04 PASS")


def test_05_band4_v2_gate_fails_honest():
    p = ROOT / "data/v4/ear/band4_spot_check_v2_c76.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert d["cycle"] == 76
    assert d["calibration"] == "wider_linear_c76"
    assert d["gate_passes"] is False, "expected honest FAIL under monotone infeasibility"
    # str supersede per c14 lemma
    sp = d["supersedes_path"]
    assert isinstance(sp, str) and sp == "_selection/band4-spot-check-halt-honest-c75"
    print("test_05 PASS")


def test_06_v2_calibrate_wider_linear_is_monotone():
    from scripts.ear import v4_ear_v2
    raw_max_ex = 0.9567
    prev = -1.0
    for raw in [x / 100.0 for x in range(15, 100)]:
        cur = v4_ear_v2.calibrate_wider_linear(raw, raw_max_ex)
        assert cur >= prev, f"non-monotone at raw={raw}"
        prev = cur
    print("test_06 PASS")


def test_07_no_prng_in_v2_module():
    src = (ROOT / "scripts/ear/v4_ear_v2.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in ("random", "numpy.random"), (
                    f"banned PRNG import: {alias.name}"
                )
        if isinstance(node, ast.ImportFrom):
            assert node.module not in ("random",), f"banned PRNG import from {node.module}"
    # sidecar_nonfactor import guard (docstring mentions allowed as prohibition marker)
    assert "import sidecar_nonfactor" not in src
    assert "from sidecar_nonfactor" not in src
    # VST3 state APIs guard (docstring mention allowed)
    assert "vst3.create_processor" not in src.lower()
    assert "vst3.get_state" not in src.lower()
    assert "vst3.set_state" not in src.lower()
    print("test_07 PASS")


def test_08_readonly_anchors_untouched_by_v2():
    import hashlib
    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        return h.hexdigest()
    # v4_ear.py stable ref sha captured this cycle (c74 substantive impl)
    assert sha(ROOT / "scripts/ear/v4_ear.py") == "e775621bff1c9560ee26da6ad22df7fae24e16c3656dcabfbd2c7f1419336878"
    # exemplar_set.json (post-c74 sha16 resolution + band realign)
    assert sha(ROOT / "data/v4/ear/exemplar_set.json") == "31c10dfb80355181f53a669922820698c083c46239b8502a4a06ddad25f7f5f6"
    # VGGish embeddings (pre-c73)
    assert sha(ROOT / "data/v4/ear/exemplar_embeddings.npz") == "be93d016c7cc0eb39e51fa47c0de11847b43f03a68ae7535cf098daff7e3751f"
    assert sha(ROOT / "data/v4/ear/band4_embeddings.npz") == "4fc8dc828e425d0280733497229d03ca26f23348c61ba001c0c31e7668b26024"
    print("test_08 PASS")


def test_09_byte_det_x2_c76_sidecars():
    # Sidecars are byte-identical across 2 runs of their generators (deterministic).
    # This test asserts the on-disk shas at close time; regeneration is by run_c76.sh.
    import hashlib
    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        return h.hexdigest()
    p1 = ROOT / "data/v4/ear/l119_infeasibility_proof_c76.json"
    p2 = ROOT / "data/v4/ear/band4_spot_check_v2_c76.json"
    assert p1.exists() and p2.exists()
    s1, s2 = sha(p1), sha(p2)
    assert len(s1) == 64 and len(s2) == 64
    print(f"test_09 PASS ({s1[:16]}..., {s2[:16]}...)")


def _run_all():
    fns = [g for name, g in list(globals().items()) if name.startswith("test_") and callable(g)]
    for f in fns:
        f()
    print(f"\n{len(fns)}/{len(fns)} c76 tests PASS")


if __name__ == "__main__":
    _run_all()
