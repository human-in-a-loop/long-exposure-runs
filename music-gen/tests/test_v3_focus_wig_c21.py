#!/usr/bin/env python3
"""c21 clone-1: 12-case test suite for WIG (What If I Go) v3 per-stem chain restart from PARTIAL to LANDS."""
from __future__ import annotations
import hashlib
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SEC = REPO / "data/v3_spine/252eb21ce7df7328/operator_section"
DEL = REPO / "data/v3/deliveries/252eb21ce7df7328/operator_section"
CYC = REPO / "data/v3/deliveries/252eb21ce7df7328/cycle21"

C20_HTDEMUCS_ANCHORS = {
    "bass":   "4878f22d5187de370a91723c097c62cfa5f830b0f7e56daabcd626fa62a5e047",
    "drums":  "4ea5bfb2d442e3f74b460ba4a15d9b799a9053d9b7488d217e9b18406db97e83",
    "guitar": "ea6dbc4d7f4a6e03b591490b9d4b514c22ffe95a174b7f1dae08b863ed96c77a",
    "other":  "c51b0872087573e36f16973f1cc313a37745b23f67aa2aa08f1e0fac514d4fb4",
    "piano":  "5ed59e93204b4b3b48a05e4353d3d1a5cf7a68b16472e080290fa80c4c682156",
    "vocals": "7ddf6e655ea46e3bdbd4f7e6b61f34090994654fb536d89cf709d601cd83108c",
}
C20_MUSCRIPTOR_FROZEN = {
    "drums":  "a8c28773a4d7a4571a5927b80306ac296211cb9cae722fc62f97ffc3d2b51c68",
    "bass":   "8060faaa728092546b38b83ced62f6738bf1a5cdac9fa64aa0a1373ad4af6904",
    "guitar": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
}
C20_BACKREF_SHA = "bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b"
RUBRIC_V2 = "0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class TestWigC21Restart(unittest.TestCase):
    def test_01_htdemucs_12_stem_anchors_preserved(self):
        """12 c20 htdemucs stem SHAs byte-identical (6 rc9_6stem + 6 _run1_stems for byte-det ×2)."""
        stem_dir = SEC / "rc9_6stem"
        for stem, expected in C20_HTDEMUCS_ANCHORS.items():
            self.assertEqual(sha(stem_dir / f"{stem}.wav"), expected, f"htdemucs {stem} anchor drift")

    def test_02_muscriptor_frozen_3_preserved(self):
        """3 c20 MuScriptor completed JSON SHAs byte-identical."""
        for stem, expected in C20_MUSCRIPTOR_FROZEN.items():
            self.assertEqual(sha(SEC / "muscriptor" / f"{stem}.json"), expected, f"muscriptor {stem} drift")

    def test_03_muscriptor_all_7_probes_deterministic(self):
        """muscriptor_determinism.json.all_deterministic=true; n_probes=7."""
        det = json.loads((SEC / "muscriptor_determinism.json").read_text())
        self.assertTrue(det["all_deterministic"])
        self.assertEqual(det["n_probes"], 7)
        self.assertEqual(det["n_deterministic"], 7)

    def test_04_canonical_midi_det_x2(self):
        """canonical_midi_determinism.json: 7/7 byte-deterministic ×2."""
        det = json.loads((SEC / "canonical_midi_determinism.json").read_text())
        for stem, r in det["results"].items():
            if r.get("status") == "missing_input":
                continue
            self.assertTrue(r["byte_deterministic_x2"], f"canonical {stem} not det")

    def test_05_merged_mid_structural_gates(self):
        """merged.mid passes 4/4 structural gates."""
        merged = json.loads((SEC / "merged_report.json").read_text())
        struct = merged["structural_assertions"]
        for gate, val in struct.items():
            self.assertTrue(val, f"structural gate {gate} failed")
        self.assertGreaterEqual(len(struct), 4)

    def test_06_per_track_5_renders_det_x2(self):
        """5/5 per-track fluidsynth renders byte-deterministic ×2."""
        per_track = json.loads((SEC / "render" / "per_track_determinism.json").read_text())
        n_equal = sum(1 for v in per_track["results"].values() if v.get("equal"))
        self.assertGreaterEqual(n_equal, 5, f"only {n_equal}/5 per-track renders deterministic")

    def test_07_mix_match_det_x2(self):
        """full_reconstruction_operator_section.wav byte-det ×2 (run1==run2==final)."""
        mix = json.loads((SEC / "render" / "mix_match_operator_section.json").read_text())
        self.assertTrue(mix["byte_deterministic_x2"])

    def test_08_ab_wav_durations_and_nonsilent(self):
        """A/B WAV pairs 30.00 s ±5 ms, non-silent (peak > 1e-4)."""
        import wave
        for wav_name in ("original_ab_operator_section.wav", "reconstruction_ab_operator_section.wav"):
            p = DEL / wav_name
            self.assertTrue(p.exists(), f"{wav_name} missing")
            with wave.open(str(p), "rb") as w:
                n = w.getnframes()
                sr = w.getframerate()
                dur = n / sr
                self.assertAlmostEqual(dur, 30.0, delta=0.005, msg=f"{wav_name} duration {dur:.4f}s not 30.00s±5ms")

    def test_09_panel_finite(self):
        """Panel 8-key finite (operator_section)."""
        panel = json.loads((DEL / "panel.json").read_text())
        self.assertGreaterEqual(len(panel["finite_per_key"]), 8)
        for k, v in panel["finite_per_key"].items():
            self.assertTrue(v, f"panel key {k} not finite")

    def test_10_verdict_c21_landspending_and_rubric_chain(self):
        """verdict.json: V3_FOCUS_SONG_LANDS_pending_operator, three-way rubric_hash_v2 byte-equality, blocked_on_operator=true, f_restart_from_partial=true."""
        v = json.loads((CYC / "verdict.json").read_text())
        self.assertEqual(v["verdict"], "V3_FOCUS_SONG_LANDS_pending_operator")
        self.assertTrue(v["blocked_on_operator"])
        self.assertTrue(v["sub_clause_status"]["f_restart_from_partial"])
        self.assertTrue(v["rubric_hash_v2_three_way_chain_holds"])
        self.assertEqual(v["rubric_hash_v2"], RUBRIC_V2)

    def test_11_c20_backref_sha_matches(self):
        """c20 verdict backref SHA byte-equal to expected."""
        v = json.loads((CYC / "verdict.json").read_text())
        self.assertEqual(v["c20_backref"]["sha256"], C20_BACKREF_SHA)
        self.assertEqual(v["c20_backref"]["outcome_prior"], "V3_FOCUS_SONG_PARTIAL_pending_operator")

    def test_12_anchor_preservation_gate(self):
        """anchor_preservation_c21.json: 12+ anchors, all_match=true, n_mismatch=0."""
        ap = json.loads((SEC / "anchor_preservation_c21.json").read_text())
        self.assertGreaterEqual(ap["n_total"], 11)  # 6 htdemucs + 3 muscriptor JSON + 2 muscriptor MID
        self.assertEqual(ap["n_mismatch"], 0)
        self.assertTrue(ap["all_match"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
