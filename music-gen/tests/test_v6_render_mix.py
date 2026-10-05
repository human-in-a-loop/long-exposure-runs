#!/usr/bin/python3
"""v6 Phase 4 tests — mix chain: the master hits the corpus-derived target LUFS within +/-0.5, never clips, stays under
-1 dBTP, is byte-deterministic; the look-ahead limiter holds its ceiling; the corpus reference file carries 29 songs with
per-band medians and a target inside the -14 +/- 2 clamp.

Run: /usr/bin/python3 -m pytest tests/test_v6_render_mix.py -q
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

import numpy as np  # noqa: E402

from scripts.v6.gen.render_v6 import mix  # noqa: E402

SR = 44100


def _tone(f, secs, amp, env_hz=0.0):
    t = np.arange(int(SR * secs)) / SR
    x = amp * np.sin(2 * np.pi * f * t)
    if env_hz:
        x *= (np.sin(2 * np.pi * env_hz * t) > 0).astype(np.float64)
    return np.stack([x, x], axis=1).astype(np.float32)


def _stems(secs=12.0):
    rng_free = np.arange(int(SR * secs))
    clicks = np.zeros(int(SR * secs))
    clicks[::SR // 2] = 1.0  # 2 Hz impulses
    clicks = np.convolve(clicks, np.exp(-np.arange(400) / 60.0), mode="same")
    drums = np.stack([clicks, clicks * 0.8], axis=1).astype(np.float32)
    noise = (np.sin(rng_free * 12.9898) * 43758.5453) % 1.0 - 0.5  # deterministic hash noise, no PRNG
    pad = _tone(220.0, secs, 0.1) + _tone(277.0, secs, 0.08)
    return {"drums": drums * 0.9, "bass": _tone(55.0, secs, 0.3, 2.0), "keys": _tone(440.0, secs, 0.15, 1.0), "comp_guitar": _tone(330.0, secs, 0.1, 4.0),
            "melody": _tone(880.0, secs, 0.12, 0.5), "pad": pad, "percussion": np.stack([noise, noise], axis=1).astype(np.float32) * 0.05}


def test_01_master_hits_target_lufs_and_never_clips() -> None:
    ref = mix.load_reference()
    stems = _stems()
    out, man = mix.mix_song(stems, SR, 5, False, 110.0, 0.1, ref, length_s=12.0)
    target = ref["target_lufs"]
    assert abs(man["master"]["lufs_final"] - target) <= 0.5, (man["master"]["lufs_final"], target)
    assert man["master"]["true_peak_dbtp_final"] <= mix.TRUE_PEAK_DBTP + 0.05
    assert float(np.abs(out).max()) < 1.0 and man["master"]["clipped_samples"] == 0
    assert out.dtype == np.float32 and out.shape == (int(SR * 12.0), 2)
    for role in stems:
        ps = man["per_stem"][role]
        assert ps["hpf_hz"] == mix.HPF_HZ[role] and ps["compressor"]["ratio"] == mix.COMP[role][1] and 0.05 <= ps["gain"] <= 8.0
    assert man["per_stem"]["bass"]["pan"] == 0.0 and man["per_stem"]["keys"]["pan"] == 0.2 and man["per_stem"]["comp_guitar"]["pan"] == -0.25 and man["per_stem"]["melody"]["pan"] == 0.1
    assert man["reverb"]["sends"]["bass"] == 0.0 and man["reverb"]["room_size"] == mix.room_size(5, False, 110.0)
    assert man["reference"]["band_used"]["lufs_integrated_median"] is not None and man["master"]["tilt_target_db"] is not None
    out2, man2 = mix.mix_song(stems, SR, 5, False, 110.0, 0.1, ref, length_s=12.0)
    assert hashlib.sha256(out.tobytes()).hexdigest() == hashlib.sha256(out2.tobytes()).hexdigest()
    assert json.dumps(man, sort_keys=True) == json.dumps(man2, sort_keys=True)
    # a very loud and a very quiet input both land on target
    for scale in (8.0, 0.02):
        o, m = mix.mix_song({k: v * scale for k, v in stems.items()}, SR, 7, True, 70.0, -0.1, ref, length_s=12.0)
        assert abs(m["master"]["lufs_final"] - target) <= 0.5 and float(np.abs(o).max()) < 1.0, (scale, m["master"]["lufs_final"])
    assert mix.room_size(7, True, 70.0) > mix.room_size(5, False, 140.0)
    print(f"test_01 PASS: LUFS {man['master']['lufs_final']} vs target {target}; TP {man['master']['true_peak_dbtp_final']} dBTP; crest {man['master']['crest_factor_db_final']}; deterministic")


def test_02_peak_limiter_holds_ceiling() -> None:
    x = _tone(100.0, 3.0, 2.5)  # +8 dBFS sine
    x[SR:SR + 50] *= 4.0  # a spike
    y, info = mix.peak_limit(x, SR, -1.0)
    assert mix.true_peak_dbtp(y, SR) <= -1.0 + 1e-6 and info["max_gain_reduction_db"] > 8.0
    assert float(np.abs(y).max()) <= 10 ** (-1.0 / 20.0) + 1e-6
    quiet = _tone(100.0, 1.0, 0.1)
    z, info2 = mix.peak_limit(quiet, SR, -1.0)
    assert np.allclose(z, quiet, atol=1e-6) and info2["max_gain_reduction_db"] == 0.0
    y2, _ = mix.peak_limit(x, SR, -1.0)
    assert np.array_equal(y, y2)
    print(f"test_02 PASS: limiter ceiling held (GR {info['max_gain_reduction_db']} dB), transparent below ceiling, deterministic")


def test_04_group_stems_sum_to_the_master_and_leave_it_byte_identical() -> None:
    """Iteration 05 --keep-stems: mix_song(groups={}) fills drums / bass / other (mix.STEM_GROUP), each mastered with the master's own
    gain + limiter curve; the master output is byte-identical to the plain call and the groups' sum tracks the master closely."""
    ref = mix.load_reference()
    stems = _stems()
    out, man = mix.mix_song(stems, SR, 5, False, 110.0, 0.1, ref, length_s=12.0)
    groups = {}
    out2, man2 = mix.mix_song(stems, SR, 5, False, 110.0, 0.1, ref, length_s=12.0, groups=groups)
    assert hashlib.sha256(out.tobytes()).hexdigest() == hashlib.sha256(out2.tobytes()).hexdigest()
    assert json.dumps(man, sort_keys=True) == json.dumps(man2, sort_keys=True)
    assert sorted(groups) == ["bass", "drums", "other"] and all(g.shape == out.shape and g.dtype == np.float32 for g in groups.values())
    assert {mix.STEM_GROUP[r] for r in stems} == set(groups) and mix.STEM_GROUP["percussion"] == "drums" and mix.STEM_GROUP["pad"] == "other"
    total = sum(groups.values())
    err = float(np.sqrt(np.mean((total - out) ** 2))) / max(float(np.sqrt(np.mean(out ** 2))), 1e-9)
    assert err < 0.35, f"group sum deviates from the master by {err:.3f} relative RMS (bus compressor acts per group)"
    assert all(float(np.abs(g).max()) <= 1.0 for g in groups.values())
    # a group only carries its own roles: bass is centred (L == R), drums keep the kit's L/R imbalance of the test stem
    assert np.allclose(groups["bass"][:, 0], groups["bass"][:, 1], atol=1e-6)
    assert not np.allclose(groups["drums"][:, 0], groups["drums"][:, 1], atol=1e-3)
    groups_b = {}
    mix.mix_song(stems, SR, 5, False, 110.0, 0.1, ref, length_s=12.0, groups=groups_b)
    assert all(np.array_equal(groups[g], groups_b[g]) for g in groups)
    print(f"test_04 PASS: 3 group stems, sum-vs-master relative RMS error {err:.3f}, master byte-identical, deterministic")


def test_03_reference_file_and_measures() -> None:
    assert mix.MIX_REFERENCE.exists(), "run scripts/v6/gen/render_v6/mix.py to measure the corpus"
    ref = json.loads(mix.MIX_REFERENCE.read_text())
    assert ref["n_songs"] == 29 and set(ref["per_band"]) == {"4", "5", "7"}
    assert mix.TARGET_LUFS_CLAMP[0] <= ref["target_lufs"] <= mix.TARGET_LUFS_CLAMP[1]
    assert ref["target_lufs"] == mix.clamp_target(ref["overall"]["lufs_integrated_median"])
    for b in ref["per_band"].values():
        assert b["n"] >= 1 and -25 < b["lufs_integrated_median"] < -5 and 5 < b["crest_factor_db_median"] < 25 and -30 < b["spectral_tilt_db_median"] < 0
    assert all({"sha16", "band", "lufs_integrated", "crest_factor_db", "spectral_tilt_db"} <= set(r) for r in ref["per_song"])
    sine = _tone(1000.0, 2.0, 0.5)
    assert abs(mix.crest_db(sine) - 3.01) < 0.05
    bright = _tone(8000.0, 2.0, 0.5)
    assert mix.spectral_tilt_db(bright, SR) > 20 > -20 > mix.spectral_tilt_db(_tone(500.0, 2.0, 0.5), SR)
    assert abs(mix.true_peak_dbtp(sine, SR) - (-6.02)) < 0.1
    print(f"test_03 PASS: reference {ref['n_songs']} songs, target {ref['target_lufs']} LUFS, per-band medians {dict((b, v['lufs_integrated_median']) for b, v in ref['per_band'].items())}")


if __name__ == "__main__":
    test_01_master_hits_target_lufs_and_never_clips()
    test_02_peak_limiter_holds_ceiling()
    test_03_reference_file_and_measures()
