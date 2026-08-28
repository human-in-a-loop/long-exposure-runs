#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T05:20:00Z
# cycle: 4
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel
# ---
"""Test suite for the texture-distance panel.

Run:
    PYTHONPATH=. /usr/bin/python3 -m unittest tests.test_texture_panel -v
"""
from __future__ import annotations

import pathlib
import unittest
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import soundfile as sf

from scripts.texture.panel import texture_distance, PUBLIC_KEYS, _BANNED_KEYS
from scripts.texture import embedding_panel

ROOT = pathlib.Path(__file__).resolve().parents[1]
DAW = ROOT / "data" / "daw_spike"
TEX = ROOT / "data" / "texture"

# References from data/daw_spike/agreement.json.
REF_MEL_L1_DB = 3.130554437637329
REF_RMS_ENV_RMSE = 0.040991
REF_SC_RMSE_HZ = 159.017
TOL = 0.05  # ±5%

# Documented FP-nondeterminism tolerance for the embedding metric on self-dist.
EMB_SELF_TOL = 1e-4
NUM_SELF_TOL = 1e-6


def _load(p: pathlib.Path):
    a, sr = sf.read(str(p), always_2d=True)
    return a.astype(np.float32), int(sr)


class PanelContractTests(unittest.TestCase):
    def setUp(self):
        self.ardour, self.sr = _load(DAW / "ardour_render.wav")
        self.daw_matched, self.sr_m = _load(DAW / "dawdreamer_render_matched.wav")

    def test_panel_refuse_aggregate(self):
        """result dict must have exactly the seven declared keys, and no banned key."""
        r = texture_distance(self.ardour, self.daw_matched, self.sr, sr_b=self.sr_m)
        self.assertEqual(set(r.keys()), set(PUBLIC_KEYS),
                         f"expected exactly {sorted(PUBLIC_KEYS)}, got {sorted(r.keys())}")
        for banned in _BANNED_KEYS:
            self.assertNotIn(banned, r, f"panel exposed banned key {banned!r}")

    def test_sr_mismatch_raises(self):
        """Passing mismatched SRs must ValueError — panel refuses to guess."""
        with self.assertRaises(ValueError):
            texture_distance(self.ardour, self.daw_matched, 48000, sr_b=22050)


class SelfDistanceTests(unittest.TestCase):
    def test_self_distance_zero(self):
        """texture_distance(a, a) must be at floor on every metric."""
        a, sr = _load(DAW / "ardour_render.wav")
        r = texture_distance(a, a, sr, sr_b=sr)
        self.assertLess(abs(r["mel_l1_db"]), NUM_SELF_TOL)
        self.assertLess(abs(r["spectral_centroid_rmse_hz"]), NUM_SELF_TOL)
        self.assertLess(abs(r["rms_env_rmse"]), NUM_SELF_TOL)
        # LUFS-M: comparing a signal to itself must yield 0 exactly.
        self.assertLess(abs(r["lufs_m_rmse_lu"]), NUM_SELF_TOL)
        # Embedding: allow a small FP-nondeterminism floor.
        self.assertIsNotNone(r["embedding_cosine_distance"])
        self.assertLess(abs(r["embedding_cosine_distance"]), EMB_SELF_TOL)


class MatchedPairTests(unittest.TestCase):
    def setUp(self):
        a, sr = _load(DAW / "ardour_render.wav")
        b, srb = _load(DAW / "dawdreamer_render_matched.wav")
        self.result = texture_distance(a, b, sr, sr_b=srb)

    def _within(self, got: float, ref: float) -> bool:
        return abs(got - ref) / abs(ref) <= TOL

    def test_matched_pair_within_tolerance(self):
        self.assertTrue(self._within(self.result["mel_l1_db"], REF_MEL_L1_DB),
                        f"mel_l1_db {self.result['mel_l1_db']} vs ref {REF_MEL_L1_DB}")
        self.assertTrue(self._within(self.result["rms_env_rmse"], REF_RMS_ENV_RMSE),
                        f"rms_env_rmse {self.result['rms_env_rmse']} vs ref {REF_RMS_ENV_RMSE}")
        self.assertTrue(self._within(self.result["spectral_centroid_rmse_hz"], REF_SC_RMSE_HZ),
                        f"spectral_centroid_rmse_hz {self.result['spectral_centroid_rmse_hz']} vs ref {REF_SC_RMSE_HZ}")


class KnownDifferentTests(unittest.TestCase):
    def test_known_different_larger_than_matched(self):
        """fluidsynth-vs-sfizz (same MIDI) must beat matched by ≥ 2× on mel_l1 and sc_rmse."""
        a, sr = _load(DAW / "ardour_render.wav")
        b, srb = _load(DAW / "dawdreamer_render_matched.wav")
        matched = texture_distance(a, b, sr, sr_b=srb)

        f, srf = _load(TEX / "fluid_render.wav")
        z, srz = _load(TEX / "sfizz_render.wav")
        diff = texture_distance(f, z, srf, sr_b=srz)

        self.assertGreater(diff["mel_l1_db"], 2 * matched["mel_l1_db"],
                           f"mel_l1_db: matched={matched['mel_l1_db']:.2f} diff={diff['mel_l1_db']:.2f}")
        self.assertGreater(diff["spectral_centroid_rmse_hz"], 2 * matched["spectral_centroid_rmse_hz"],
                           f"sc_rmse: matched={matched['spectral_centroid_rmse_hz']:.2f} "
                           f"diff={diff['spectral_centroid_rmse_hz']:.2f}")
        # Also assert absolute scale (mel_l1 > 10 dB, sc_rmse > 500 Hz) per the brief.
        self.assertGreater(diff["mel_l1_db"], 10.0)
        self.assertGreater(diff["spectral_centroid_rmse_hz"], 500.0)


class EmbeddingRungTests(unittest.TestCase):
    def test_embedding_rung_logged(self):
        """embedding_rung.log must exist and name a valid rung."""
        log = TEX / "embedding_rung.log"
        self.assertTrue(log.exists(), f"missing {log}")
        import json
        data = json.loads(log.read_text())
        self.assertIn(data["rung"], {"clap", "vggish", "none_available"})
        # And the runtime rung agrees.
        self.assertEqual(data["rung"], embedding_panel.get_rung())


if __name__ == "__main__":
    unittest.main(verbosity=2)
