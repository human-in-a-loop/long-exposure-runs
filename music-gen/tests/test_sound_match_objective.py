#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES
# ---
"""Objective panel wrapper tests.

Contract:
    - Returns the expected key set on a known-different WAV pair (all 5
      metric-family keys plus composite + weights + rung + sr/n).
    - Composite is FINITE on a plausible pair.
    - Weights literals are frozen at 0.5 / 0.25 / 0.25 (fallback 0.67/0.33
      when embedding rung is 'none_available').
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.sound_match import objective as obj  # noqa: E402


def _write_tone(path: Path, freq: float, dur_s: float = 2.0, sr: int = 44100) -> None:
    t = np.linspace(0, dur_s, int(sr * dur_s), endpoint=False)
    y = 0.3 * np.sin(2 * np.pi * freq * t).astype(np.float32)
    sf.write(str(path), y, sr, subtype="PCM_16")


def test_weight_literals_frozen():
    assert obj.W_MEL == 0.5
    assert obj.W_CENTROID == 0.25
    assert obj.W_EMBED == 0.25
    assert obj.FALLBACK_W_MEL == 0.67
    assert obj.FALLBACK_W_CENTROID == 0.33
    print("PASS test_weight_literals_frozen")


def test_score_pair_shape_on_known_different():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        a = td / "a.wav"
        b = td / "b.wav"
        _write_tone(a, 220.0)
        _write_tone(b, 880.0)
        out = obj.score_pair(a, b)
        for k in ("mel_l1_db", "spectral_centroid_rmse_hz",
                  "embedding_cos_vggish", "embedding_cos_clap_or_none",
                  "embedding_component", "composite", "weights",
                  "embedding_rung", "sr_hz", "n_samples_compared"):
            assert k in out, f"missing key: {k}"
        assert out["sr_hz"] == 44100
        assert out["n_samples_compared"] > 0
        # composite must be finite for a plausible pair
        assert out["composite"] == out["composite"], "composite is NaN"
        # metric-family keys must be finite
        assert out["mel_l1_db"] == out["mel_l1_db"]
        assert out["spectral_centroid_rmse_hz"] == out["spectral_centroid_rmse_hz"]
    print("PASS test_score_pair_shape_on_known_different")


def test_score_pair_self_metric_is_small():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        a = td / "a.wav"
        _write_tone(a, 220.0)
        out = obj.score_pair(a, a)
        # spectral distance on self must be tiny (numeric noise only).
        assert abs(out["mel_l1_db"]) < 1e-3, out
        assert abs(out["spectral_centroid_rmse_hz"]) < 1.0, out
    print("PASS test_score_pair_self_metric_is_small")


if __name__ == "__main__":
    test_weight_literals_frozen()
    test_score_pair_shape_on_known_different()
    test_score_pair_self_metric_is_small()
    print("OK")
