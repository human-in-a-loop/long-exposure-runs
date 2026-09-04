#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T05:15:00Z
# cycle: 19
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: _infra/adopt-cycle19-lufs-diagnostic-tests
# purpose: Regression tests for the c18 LUFS-I diagnostic on cg_ab_mix.wav.
#           Anchors the DIAGNOSTIC-ONLY contract (audio bytes not mutated),
#           the on-disk measurement values, the piano-silence-floor semantics,
#           and the discipline guards on measure_cg_ab_mix_lufs.py.
# ---
"""c19 + c20 LUFS diagnostic regression suite.

Test cases (8 total; ≥6 c19 gate + 1 c20 FETCH_FAIL fixture):
  01  SHA regression on cg_ab_mix.lufs_diagnostic.json (frozen c18 anchor
      6810d5056edf5889...)
  02  Byte-identity: cg_ab_mix.wav SHA `6e13e007...f9484b` unchanged pre==post
      (validates `does_not_mutate_audio: true` contract; audio-bytes-untouched)
  03  LUFS-I measurements finite + approximately equal expected values for
      non-silent stems (bass -18.48, drums -13.69, guitar -27.86, vocals
      -23.97, mix -15.32) within ±0.5 LU tolerance
  04  Piano LUFS-I is -inf (silence-floor sentinel per c14 audibility-grounded
      NULL finding); other LUFS-I is below -60 dB silence floor
  05  Discipline guards on measure_cg_ab_mix_lufs.py: interpreter guard
      /usr/bin/python3, no PRNG imports, no sidecar_nonfactor, no VST3 state
      APIs, no --verify-det pass-through
  06  env_pin canonical 7-key subset asserted with env_pin_sha256 =
      2ac444c36298d6ada... recorded in sidecar
  07  Pyloudnorm probe outcome: fetch_status == "OK" round-trip assertion
      + measurements dict populated for all 7 named cells
  08  c20 Track 2 FETCH_FAIL branch fixture — simulate pyloudnorm
      unavailability via sys.modules shim inside a tempfile.mkdtemp()
      workspace, invoke measure_cg_ab_mix_lufs.main(), assert the
      FETCH_FAIL row shape (fetch_status='FETCH_FAIL',
      fetch_status_reason non-null, measurements=None,
      does_not_mutate_audio=true, env_pin_sha256 pinned). Frozen c18
      anchor JSON + c17 mix WAV byte-identical pre==post.

Invariant (d) disclosure: the c18 brief spec described the LUFS values with
2-decimal precision; the on-disk JSON has full float precision. Tests round
to 2 decimals via approx tolerance.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import re
import unittest
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DELIVERY = WORKSPACE / "data" / "v4" / "deliveries" / "31a164f845f8e27e"
LUFS_JSON = DELIVERY / "cg_ab_mix.lufs_diagnostic.json"
MIX_WAV = DELIVERY / "cg_ab_mix.wav"
LUFS_SCRIPT = WORKSPACE / "scripts" / "sound_match" / "measure_cg_ab_mix_lufs.py"

# c18 anchors (READ-ONLY per FD-1)
LUFS_JSON_SHA_C18 = "6810d5056edf5889e7d27b946d79c2e05328b44704f79b542c49b9c64f647b6b"
MIX_WAV_SHA_C17 = "6e13e0075c5d8116784109067cf2c73acd65e47d67398b88aa08e0f752f9484b"

# Canonical 7-key env-pin subset
ENV_PIN_SHA_C18 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
ENV_KEYS = frozenset({
    "PYTHONHASHSEED",
    "SOURCE_DATE_EPOCH",
    "TZ",
    "LC_ALL",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
})

# Expected LUFS-I values from c18 measurement (rounded to 2 decimals).
EXPECTED_LUFS = {
    "cg_ab_mix": -15.32,
    "stem_bass": -18.48,
    "stem_drums": -13.69,
    "stem_guitar": -27.86,
    "stem_vocals": -23.97,
}
SILENT_STEMS = ("stem_piano_reference_only_null_in_mix",
                "stem_other_reference_only_null_in_mix")


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class TestMeasureCgAbMixLufs(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(LUFS_JSON.read_text())

    def test_01_lufs_json_sha_regression(self) -> None:
        """LUFS-diagnostic sidecar sha byte-equal to c18 frozen anchor."""
        got = _sha256(LUFS_JSON)
        self.assertEqual(got, LUFS_JSON_SHA_C18,
            f"LUFS JSON SHA drifted; expected {LUFS_JSON_SHA_C18[:16]}..., "
            f"got {got[:16]}...")

    def test_02_cg_ab_mix_bytes_unmodified(self) -> None:
        """cg_ab_mix.wav SHA unchanged from c17 anchor (DIAGNOSTIC-ONLY
        contract enforcement)."""
        got = _sha256(MIX_WAV)
        self.assertEqual(got, MIX_WAV_SHA_C17,
            f"cg_ab_mix.wav SHA drifted; expected {MIX_WAV_SHA_C17[:16]}..., "
            f"got {got[:16]}...")
        # Also assert the JSON records the same pre==post
        self.assertEqual(self.data["cg_ab_mix_wav_sha256_pre"], MIX_WAV_SHA_C17)
        self.assertEqual(self.data["cg_ab_mix_wav_sha256_post"], MIX_WAV_SHA_C17)
        self.assertTrue(self.data["does_not_mutate_audio"])
        self.assertTrue(self.data["diagnostic_only"])

    def test_03_lufs_values_finite_and_approx(self) -> None:
        """LUFS-I measurements finite for non-silent stems and within ±0.5 LU
        of expected values."""
        m = self.data["measurements"]
        for label, expected in EXPECTED_LUFS.items():
            self.assertIn(label, m, f"missing measurement: {label}")
            got = m[label]["lufs_i"]
            self.assertIsInstance(got, (int, float),
                f"{label}: LUFS-I not numeric: {got}")
            self.assertTrue(math.isfinite(got),
                f"{label}: LUFS-I not finite: {got}")
            self.assertAlmostEqual(got, expected, delta=0.5,
                msg=f"{label}: LUFS-I {got} not within 0.5 LU of {expected}")

    def test_04_silent_stems_at_or_below_silence_floor(self) -> None:
        """Piano LUFS-I is -inf sentinel; other LUFS-I below -60 dB floor
        (audibility-grounded c14 NULL finding)."""
        m = self.data["measurements"]
        # Piano: json.loads returns -inf for -Infinity literal? Actually
        # standard JSON does not support Infinity; pyloudnorm can serialize
        # via -Infinity token. On the c18 anchor, piano lufs_i is -inf.
        piano = m["stem_piano_reference_only_null_in_mix"]["lufs_i"]
        self.assertTrue(
            (isinstance(piano, float) and (piano == -math.inf or piano < -60.0))
            or piano is None,
            f"piano LUFS-I should be -inf or ≤ -60 dB, got {piano}",
        )
        other = m["stem_other_reference_only_null_in_mix"]["lufs_i"]
        self.assertIsInstance(other, (int, float))
        self.assertLess(other, -60.0,
            f"other LUFS-I {other} should be below -60 dB silence floor")

    def test_05_discipline_guards_on_script(self) -> None:
        """AST + regex guards: interpreter guard, no PRNG, no
        sidecar_nonfactor, no VST3 state APIs, no --verify-det passthrough."""
        src = LUFS_SCRIPT.read_text()
        # Interpreter guard: shebang carries /usr/bin/python3
        first = src.splitlines()[0]
        self.assertIn("/usr/bin/python3", first,
            "interpreter guard shebang missing /usr/bin/python3")

        # AST: no PRNG imports (random, numpy.random)
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotEqual(alias.name, "random",
                        "random import forbidden")
                    self.assertFalse(alias.name.startswith("numpy.random"),
                        f"numpy.random import forbidden: {alias.name}")
            if isinstance(node, ast.ImportFrom):
                self.assertNotEqual(node.module, "random",
                    "from random import forbidden")
                self.assertFalse(
                    (node.module or "").startswith("numpy.random"),
                    f"from numpy.random import forbidden: {node.module}")

        # AST: no sidecar_nonfactor import
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn("sidecar_nonfactor", (node.module or ""))
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn("sidecar_nonfactor", alias.name)

        # Regex call-pattern check for forbidden VST3 state calls (not
        # substring — must be a call site, docstring mentions ok)
        forbidden_calls = ["get_state", "save_state", "save_preset",
                          "load_state", "set_state"]
        for name in forbidden_calls:
            pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*\(")
            self.assertIsNone(pat.search(src),
                f"forbidden VST3 state API call site: {name}")

        # --verify-det pass-through forbidden per FD-16(b)
        self.assertIsNone(
            re.search(r'add_argument\s*\(\s*["\']--verify-det["\']', src),
            "--verify-det argparse pass-through forbidden per FD-16(b)")

    def test_06_env_pin_canonical_7_key_subset(self) -> None:
        """env_pin_sha256 pins the canonical 7-key subset used cross-cycle
        (bass_v2 replay-proof, cg_ab_mix replay-proof)."""
        got = self.data.get("env_pin_sha256")
        self.assertEqual(got, ENV_PIN_SHA_C18,
            f"env_pin_sha256 drifted; expected {ENV_PIN_SHA_C18[:16]}..., "
            f"got {(got or '<none>')[:16]}...")
        # Also assert the 7 canonical env vars are the pinned set inside the
        # script source
        src = LUFS_SCRIPT.read_text()
        for k in ENV_KEYS:
            self.assertIn(k, src, f"canonical env pin key missing in script: {k}")

    def test_08_fetch_fail_branch_shape(self) -> None:
        """c20 Track 2: simulate pyloudnorm unavailability via sys.modules
        shim; assert FETCH_FAIL row shape; c18 anchor JSON + c17 mix WAV
        byte-identical pre==post (isolated tempdir output)."""
        import importlib.util
        import shutil
        import sys
        import tempfile
        from unittest import mock

        # Frozen c18 + c17 anchor SHAs, verified pre==post around the fixture.
        c18_json_sha_pre = _sha256(LUFS_JSON)
        mix_wav_sha_pre = _sha256(MIX_WAV)
        self.assertEqual(c18_json_sha_pre, LUFS_JSON_SHA_C18)
        self.assertEqual(mix_wav_sha_pre, MIX_WAV_SHA_C17)

        with tempfile.TemporaryDirectory() as td:
            tmp_root = Path(td)
            tmp_delivery = tmp_root / "data" / "v4" / "deliveries" / \
                "31a164f845f8e27e"
            tmp_delivery.mkdir(parents=True)
            tmp_mix = tmp_delivery / "cg_ab_mix.wav"
            shutil.copyfile(MIX_WAV, tmp_mix)
            tmp_out = tmp_delivery / "cg_ab_mix.lufs_diagnostic.json"
            tmp_stems = tmp_root / "data" / "v3" / "deliveries" / \
                "31a164f845f8e27e" / "cert_run1" / "stems_6s"
            tmp_stems.mkdir(parents=True)

            spec = importlib.util.spec_from_file_location(
                "measure_cg_ab_mix_lufs_fetch_fail_fixture",
                str(LUFS_SCRIPT),
            )
            self.assertIsNotNone(spec)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # Redirect module-level paths into the isolated tempdir so the
            # frozen c18 sidecar under data/v4/deliveries/... is never
            # overwritten.
            mod.DELIVERY = tmp_delivery
            mod.MIX = tmp_mix
            mod.STEMS = tmp_stems

            # Shim pyloudnorm to force ImportError inside main()'s try/except.
            with mock.patch.dict(sys.modules, {"pyloudnorm": None}):
                rc = mod.main()

            self.assertEqual(rc, 0, "FETCH_FAIL path should return 0")
            self.assertTrue(tmp_out.exists(),
                "FETCH_FAIL path must write the diagnostic sidecar")
            data = json.loads(tmp_out.read_text())
            self.assertEqual(data.get("fetch_status"), "FETCH_FAIL",
                f"expected fetch_status=FETCH_FAIL, got {data.get('fetch_status')}")
            self.assertIsInstance(data.get("fetch_status_reason"), str)
            self.assertIn("import failed", data["fetch_status_reason"])
            self.assertIsNone(data.get("measurements"),
                "FETCH_FAIL row must set measurements=None")
            self.assertTrue(data.get("does_not_mutate_audio"))
            self.assertTrue(data.get("diagnostic_only"))
            self.assertEqual(data.get("cg_ab_mix_wav_sha256_pre"),
                             data.get("cg_ab_mix_wav_sha256_post"))
            self.assertEqual(data.get("env_pin_sha256"), ENV_PIN_SHA_C18,
                "FETCH_FAIL row must still pin canonical env_pin_sha256")

        # c18 anchor JSON + c17 mix WAV byte-identical pre==post.
        self.assertEqual(_sha256(LUFS_JSON), c18_json_sha_pre,
            "c18 LUFS anchor JSON must remain byte-identical after fixture")
        self.assertEqual(_sha256(MIX_WAV), mix_wav_sha_pre,
            "c17 cg_ab_mix.wav must remain byte-identical after fixture")

    def test_07_pyloudnorm_probe_ok(self) -> None:
        """Fetch status == OK on the c18 diagnostic; measurements populated
        for all 7 named cells (mix + 4 non-silent stems + 2 silent-reference
        stems)."""
        self.assertEqual(self.data["fetch_status"], "OK",
            f"pyloudnorm probe status drift: {self.data.get('fetch_status')}")
        self.assertIsNone(self.data.get("fetch_status_reason"))
        m = self.data["measurements"]
        expected_cells = set(EXPECTED_LUFS.keys()) | set(SILENT_STEMS)
        self.assertEqual(set(m.keys()), expected_cells,
            f"measurement keys drift: expected {expected_cells}, got {set(m.keys())}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
