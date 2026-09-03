#!/usr/bin/env -S /usr/bin/python3
"""Tests for scripts.sound_match.fine_fit_sf2 (stage-2 fine fit).

Discipline checks + unit checks:
    1. interpreter guard
    2. no PRNG imports (AST grep)
    3. grid enumeration determinism (byte-identical over 2 runs)
    4. config-hash uniqueness across all 180 cells
    5. env-pin schema present with 7 keys
    6. EQ fit determinism on a synthetic reference (same input -> same gains)
    7. compressor engagement smoke test
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

from scripts.sound_match import fine_fit_sf2 as ff  # noqa: E402


def test_interpreter_guard():
    assert sys.executable == "/usr/bin/python3", sys.executable


def test_no_prng_imports():
    src = Path(ff.__file__).read_text()
    tree = ast.parse(src)
    forbidden = {"random", "secrets"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split(".")[0] not in forbidden, a.name
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden, node.module


def test_grid_enumeration_determinism():
    top_k = [
        {"rank_stage1": r, "bank": 0, "program": p, "preset_name": n,
         "composite_stage1": 700.0 + r}
        for r, p, n in [(1, 19, "Church Organ"), (2, 5, "EP2"),
                        (3, 38, "Synth Bass 1"), (4, 18, "Rock Organ"),
                        (5, 17, "Drawbar Organ")]
    ]
    a = ff.enumerate_grid(top_k)
    b = ff.enumerate_grid(top_k)
    assert a == b
    assert len(a) == 5 * 3 * 3 * 4 == 180


def test_config_hash_uniqueness():
    top_k = [
        {"rank_stage1": r, "bank": 0, "program": p, "preset_name": "",
         "composite_stage1": 0.0}
        for r, p in [(1, 19), (2, 5), (3, 38), (4, 18), (5, 17)]
    ]
    cells = ff.enumerate_grid(top_k)
    hashes = [c["config_hash"] for c in cells]
    assert len(hashes) == len(set(hashes)), "duplicate config hashes"


def test_env_pin_schema():
    for k in ("PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
              "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        assert k in ff._PINS
    assert ff._PINS["PYTHONHASHSEED"] == "0"


def test_eq_fit_deterministic_on_synthetic(tmp_path):
    sr = 44100
    n = sr  # 1 s
    t = np.arange(n) / sr
    # rendered: white noise-ish; reference: same-frequency sine (very different spectrum)
    rendered = 0.1 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
    reference = 0.1 * np.sin(2 * np.pi * 220 * t).astype(np.float32)
    r_path = tmp_path / "r.wav"
    ref_path = tmp_path / "ref.wav"
    sf.write(str(r_path), rendered, sr)
    sf.write(str(ref_path), reference, sr)
    g1 = ff._fit_eq_curve_from_reference(r_path, ref_path)
    g2 = ff._fit_eq_curve_from_reference(r_path, ref_path)
    assert g1 == g2
    assert len(g1) == 12
    # Zero-mean normalization: mean should be ~0.
    assert abs(sum(g1) / 12.0) < 1e-6


def test_compressor_engagement():
    sr = 44100
    n = sr // 4  # 250 ms
    # Loud signal (0.9 amplitude ~ -0.9 dBFS) should engage the compressor.
    loud = 0.9 * np.ones(n, dtype=np.float32)
    out, info = ff._apply_compressor(loud, sr=sr)
    assert info["n_samples_compressor_engaged"] > 0
    assert info["engagement_fraction"] > 0.5
    # Quiet signal (-40 dBFS, well below -18 threshold) should NOT engage.
    quiet = 0.01 * np.ones(n, dtype=np.float32)
    out2, info2 = ff._apply_compressor(quiet, sr=sr)
    assert info2["engagement_fraction"] < 0.05


def test_clip_and_count():
    y = np.array([-1.5, -0.5, 0.99, 1.5, 0.0], dtype=np.float32)
    clipped, frac = ff._clip_and_count(y)
    expected = np.array([-0.99, -0.5, 0.99, 0.99, 0.0], dtype=np.float32)
    assert np.allclose(clipped, expected, atol=1e-6)
    assert frac == 2 / 5


def test_read_top_k_from_stage1(tmp_path):
    lb = tmp_path / "lb.tsv"
    lb.write_text(
        "rank\tbank\tprogram\tcomposite\tstatus\n"
        "1\t0\t19\t668.7\tOK\n"
        "2\t0\t5\t674.3\tOK\n"
        "3\t0\t38\t728.3\tOK\n"
        "4\t0\t18\t804.0\tOK\n"
        "5\t0\t17\t805.2\tOK\n"
    )
    picked = ff._read_top_k_from_stage1(lb, k=3)
    assert [p["program"] for p in picked] == [19, 5, 38]


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    fails = 0
    for t in tests:
        try:
            # tmp_path emulation
            if "tmp_path" in t.__code__.co_varnames[:t.__code__.co_argcount]:
                import tempfile
                with tempfile.TemporaryDirectory() as td:
                    t(Path(td))
            else:
                t()
            print(f"PASS {t.__name__}")
        except Exception:
            fails += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    sys.exit(0 if fails == 0 else 1)
