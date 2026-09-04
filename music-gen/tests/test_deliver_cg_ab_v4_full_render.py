#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T04:00:00Z
# cycle: 18
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-V4-SHOWCASE-1
# purpose: Regression tests for the CG A/B full-render path landed at c17.
#           Anchors cg_ab_mix.wav SHA + per-cell provenance + bass gain
#           amplification semantics (guards against c17 narrative "attenuation"
#           drift) + OPT3 htdemucs stem-substitution routing + discipline
#           guards + replay-proof anchor.
# ---
"""c18 Track 1 full-render regression suite.

Test cases (12 total; ≥8 gate):
  01  SHA regression on cg_ab_mix.wav = 6e13e0075c5d8116... (frozen c17)
  02  Manifest per-cell provenance keys present + env_pin block + notes
  03  Bass gain formula: gain = ref_rms / ren_rms capped [0.05, 4.0]
      at scripts/sound_match/deliver_cg_ab_v4.py line 245-248
  04  Bass gain interpretation: on-disk 2.688385 > 1.0 => amplification
      (regression guard against c17 "attenuation" narrative drift)
  05  Drums OPT3 htdemucs stem-substitution routing (source_sha256 anchor)
  06  Guitar OPT3 htdemucs stem-substitution routing (source_sha256 anchor)
  07  Discipline guards (AST-grep): interpreter guard /usr/bin/python3,
      no PRNG imports, no sidecar_nonfactor, no VST3 state APIs, no
      --verify-det in driver source
  08  Replay-proof anchor regression: cg_ab_mix.replay_proof.json fields
      + REPLAY_PROOF_HOLDS verdict + run1_sha256 == run2_sha256 == mix SHA
  09  Manifest schema shape: top-level keys present + provenance
      has 6 stems + output_sha256 == cg_ab_mix.wav SHA
  10  Piano and Other NULL sub-blocks present with render_family
      "null_no_synthesis" (audibility-grounded c14)
  11  Vocals hybrid overlay: render_family == "htdemucs_hybrid_overlay"
      + source_sha256 pinned (per campaign L59-60)
  12  env_pin block is the canonical 7-key subset (matches replay-proof
      env_pin_sha256 = 2ac444c3...)

Invariant (d) on-disk-vs-brief divergence disclosure: c18 brief spec
described `provenance.drums.source == "htdemucs_stem"`; on-disk manifest
uses `render_family="htdemucs_stem_substitution"` + `source_sha256`.
Tests validate the on-disk shape per FD-1 + invariant (d).
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent

DELIVERY_DIR = WORKSPACE / "data" / "v4" / "deliveries" / "31a164f845f8e27e"
MIX_WAV = DELIVERY_DIR / "cg_ab_mix.wav"
MANIFEST = DELIVERY_DIR / "cg_ab_mix.manifest.json"
REPLAY_PROOF = DELIVERY_DIR / "cg_ab_mix.replay_proof.json"

DRIVER = WORKSPACE / "scripts" / "sound_match" / "deliver_cg_ab_v4.py"

# Frozen c17 anchors (READ-ONLY; do NOT edit)
ANCHOR_MIX_SHA = "6e13e0075c5d8116784109067cf2c73acd65e47d67398b88aa08e0f752f9484b"
ANCHOR_DRUMS_STEM_SHA = "34492c03f301b6eac3a75343b61244193889d039ae4ccce4c35cc44d568ac835"
ANCHOR_GUITAR_STEM_SHA = "e4ff08ea10f9bbcb7083e889172fe5fcf4fac57865e957d1bbdcda9341868bd8"
ANCHOR_ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestFullRender(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for p in (MIX_WAV, MANIFEST, REPLAY_PROOF, DRIVER):
            if not p.exists():
                raise unittest.SkipTest(f"required c17 anchor missing: {p}")
        cls.mf = json.loads(MANIFEST.read_text())
        cls.rp = json.loads(REPLAY_PROOF.read_text())
        cls.src = DRIVER.read_text()

    # 01 --------------------------------------------------------------
    def test_01_mix_wav_sha_regression(self) -> None:
        """cg_ab_mix.wav byte-identical to c17 anchor."""
        self.assertEqual(sha256_of(MIX_WAV), ANCHOR_MIX_SHA)

    # 02 --------------------------------------------------------------
    def test_02_manifest_provenance_keys(self) -> None:
        """Per-cell provenance for 6 stems + env_pin block present."""
        prov = self.mf.get("provenance", {})
        for stem in ("bass", "drums", "guitar", "piano", "other", "vocals"):
            self.assertIn(stem, prov, f"missing provenance.{stem}")
        self.assertIn("env_pin", self.mf)
        self.assertIn("env_pin_sha256", self.mf)
        self.assertIn("notes", self.mf)
        self.assertIn("M-V4-METRIC-SEMANTICS-c16",
                      json.dumps(self.mf["notes"]),
                      msg="Track 2 metric-semantics carryover note expected in manifest.notes")

    # 03 --------------------------------------------------------------
    def test_03_bass_gain_formula_source_pin(self) -> None:
        """deliver_cg_ab_v4.py implements gain = ref_rms/ren_rms capped [0.05, 4.0]."""
        # Locate the exact substrings; source line ~245-248 per c18 brief.
        self.assertIn("gain = ref_rms / ren_rms", self.src)
        self.assertIn("if gain > 4.0: gain = 4.0", self.src)
        self.assertIn("if gain < 0.05: gain = 0.05", self.src)

    # 04 --------------------------------------------------------------
    def test_04_bass_gain_amplification_semantics(self) -> None:
        """On-disk rms_normalize_gain > 1.0 means amplification (NOT attenuation).

        Guards against c17 report narrative drift: prior text said
        'gain 0.093 (attenuation)' but on-disk value is 2.688385
        (amplification). Formula is ref_rms / ren_rms; when the render
        is quieter than the reference (typical for organ vs bass), the
        ratio exceeds 1.0 and the bass is amplified toward the reference.
        """
        gain = self.mf["provenance"]["bass"]["rms_normalize_gain"]
        self.assertAlmostEqual(gain, 2.688385, places=6)
        self.assertGreater(gain, 1.0,
                           msg="gain > 1.0 => amplification, NOT attenuation")
        self.assertLessEqual(gain, 4.0, msg="capped at 4.0")
        self.assertGreaterEqual(gain, 0.05, msg="capped at 0.05")

    # 05 --------------------------------------------------------------
    def test_05_drums_opt3_htdemucs_routing(self) -> None:
        """Drums provenance names htdemucs stem substitution with anchored SHA.

        Invariant (d) disclosure: on-disk field is `render_family` +
        `source_sha256`; c18 brief used the shorthand `source` + `sha256`.
        Test validates the on-disk shape per FD-1.
        """
        d = self.mf["provenance"]["drums"]
        self.assertEqual(d["render_family"], "htdemucs_stem_substitution")
        self.assertEqual(d["acceptance"], "OPT3")
        self.assertEqual(d["source_sha256"], ANCHOR_DRUMS_STEM_SHA)

    # 06 --------------------------------------------------------------
    def test_06_guitar_opt3_htdemucs_routing(self) -> None:
        """Guitar provenance names htdemucs stem substitution with anchored SHA."""
        g = self.mf["provenance"]["guitar"]
        self.assertEqual(g["render_family"], "htdemucs_stem_substitution")
        self.assertEqual(g["acceptance"], "OPT3")
        self.assertEqual(g["source_sha256"], ANCHOR_GUITAR_STEM_SHA)

    # 07 --------------------------------------------------------------
    def test_07_discipline_guards(self) -> None:
        """AST-grep + call-pattern regex: interpreter, PRNG, forbidden APIs.

        Comments/docstrings that *describe* the ban (e.g. the module
        docstring "no PRNG, no sidecar_nonfactor, no --verify-det")
        are NOT violations — they document the invariant. This test
        checks actual imports (AST) and actual call/argparse patterns
        (regex), not raw substring hits inside comments/docstrings.
        """
        # Interpreter guard on first line.
        first = self.src.splitlines()[0]
        self.assertIn("/usr/bin/python3", first,
                      msg="interpreter guard required per docs/interpreter_guard_policy.md")
        # AST-scan: no PRNG imports; no sidecar_nonfactor imports.
        tree = ast.parse(self.src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name, "random")
                    self.assertFalse(alias.name.startswith("numpy.random"))
                    self.assertNotIn("sidecar_nonfactor", alias.name)
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    self.assertNotEqual(node.module, "random")
                    self.assertFalse(node.module.startswith("numpy.random"))
                    self.assertNotIn("sidecar_nonfactor", node.module)
                for alias in node.names:
                    self.assertNotIn("sidecar_nonfactor", alias.name)
        # No VST3 state-API *call* sites (c33/c35 anti-pattern lock).
        # Match `.name(` or bare `name(` call sites; skips docstring mentions.
        for forbidden in ("get_state", "save_state", "save_preset",
                          "load_state", "set_state"):
            pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(forbidden)}\s*\(")
            self.assertIsNone(pat.search(self.src),
                              msg=f"VST3 state API call site '{forbidden}(' banned in driver")
        # No --verify-det argparse registration (FD-16(b): NEVER for routine runs).
        self.assertIsNone(
            re.search(r'add_argument\s*\(\s*["\']--verify-det["\']', self.src),
            msg="--verify-det argparse flag banned in driver per FD-16(b)")

    # 08 --------------------------------------------------------------
    def test_08_replay_proof_anchor(self) -> None:
        """cg_ab_mix.replay_proof.json holds REPLAY_PROOF_HOLDS with byte-eq."""
        self.assertEqual(self.rp["verdict"], "REPLAY_PROOF_HOLDS")
        self.assertEqual(self.rp["run1_sha256"], self.rp["run2_sha256"])
        self.assertEqual(self.rp["run1_sha256"], ANCHOR_MIX_SHA)
        self.assertEqual(self.rp["song_sha16"], "31a164f845f8e27e")
        self.assertEqual(self.rp["env_pin_sha256"], ANCHOR_ENV_PIN_SHA)

    # 09 --------------------------------------------------------------
    def test_09_manifest_schema_shape(self) -> None:
        """Manifest has expected top-level keys + output_sha256 matches mix."""
        for k in ("output_relpath", "output_sha256", "provenance",
                  "env_pin", "env_pin_sha256", "song_sha16"):
            self.assertIn(k, self.mf)
        self.assertEqual(self.mf["output_sha256"], ANCHOR_MIX_SHA)
        self.assertEqual(self.mf["song_sha16"], "31a164f845f8e27e")

    # 10 --------------------------------------------------------------
    def test_10_piano_and_other_null_no_synthesis(self) -> None:
        """Piano and Other NULL per audibility-grounded c14 findings."""
        for stem in ("piano", "other"):
            s = self.mf["provenance"][stem]
            self.assertEqual(s["render_family"], "null_no_synthesis")

    # 11 --------------------------------------------------------------
    def test_11_vocals_hybrid_overlay(self) -> None:
        """Vocals hybrid overlay from htdemucs (campaign L59-60)."""
        v = self.mf["provenance"]["vocals"]
        self.assertEqual(v["render_family"], "htdemucs_hybrid_overlay")
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", v["source_sha256"]))

    # 12 --------------------------------------------------------------
    def test_12_env_pin_canonical_7_key_subset(self) -> None:
        """env_pin block is the canonical 7-key subset per c17."""
        expected = {"PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
                    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"}
        self.assertEqual(set(self.mf["env_pin"].keys()), expected)
        self.assertEqual(self.mf["env_pin_sha256"], ANCHOR_ENV_PIN_SHA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
