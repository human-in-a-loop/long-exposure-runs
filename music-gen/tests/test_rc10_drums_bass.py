#!/usr/bin/env /usr/bin/python3
# Tests for RC10 Branch A — drums + bass transcription re-survey.
# created: 2026-09-02, cycle 54, run-2026-08-28T040704Z, worker, fork bdd7bb47f1b5 clone-0
import ast
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestRC10(unittest.TestCase):
    def setUp(self):
        self.impl = ROOT / "data/rc10_drums_bass_impl"
        self.scripts = ROOT / "scripts/recreate_v2/rc10_drums_bass"

    def test_01_rubric_doc_present(self):
        p = ROOT / "docs/rc10_drums_bass_rubric.md"
        self.assertTrue(p.exists())
        self.assertGreater(len(p.read_bytes()), 1000)

    def test_02_rubric_mtime_before_scripts(self):
        rubric_m = (ROOT / "docs/rc10_drums_bass_rubric.md").stat().st_mtime
        for py in self.scripts.rglob("*.py"):
            if py.name == "__init__.py":
                continue
            self.assertLess(rubric_m, py.stat().st_mtime + 1.0,
                            f"{py} older than rubric")

    def test_03_rubric_hash_three_way_chain(self):
        doc_sha = hashlib.sha256((ROOT / "docs/rc10_drums_bass_rubric.md").read_bytes()).hexdigest()
        pinned = (self.impl / "rubric_hash.txt").read_text().strip()
        verdict = json.loads((self.impl / "verdict.json").read_text())
        self.assertEqual(doc_sha, pinned)
        self.assertEqual(doc_sha, verdict["rubric_hash"])

    def test_04_verdict_in_frozen_enum(self):
        v = json.loads((self.impl / "verdict.json").read_text())
        self.assertIn(v["verdict"], {
            "RC10_DRUMS_BASS_LANDS",
            "RC10_DRUMS_BASS_PARTIAL",
            "RC10_DRUMS_BASS_FAILS",
        })

    def test_05_winner_json_shape(self):
        w = json.loads((self.impl / "winner_per_stem.json").read_text())
        self.assertIn("drums", w)
        self.assertIn("bass", w)
        for stem in ("drums", "bass"):
            self.assertIn("candidate", w[stem])
            self.assertIn("mean_composite", w[stem])

    def test_06_scorecard_row_count(self):
        # header + 5 songs × (1 drums + 3 bass) × 2 D4 = 40 rows
        lines = (self.impl / "scorecard.tsv").read_text().strip().splitlines()
        self.assertEqual(len(lines), 41)

    def test_07_byte_determinism_manifest(self):
        d = json.loads((self.impl / "byte_determinism.json").read_text())
        self.assertGreater(d["n_total"], 0)
        self.assertEqual(d["n_mismatch"], 0)
        self.assertEqual(d["n_match"], d["n_total"])

    def test_08_anchor_preservation_ge_25(self):
        ap = json.loads((self.impl / "anchor_preservation.json").read_text())
        self.assertGreaterEqual(ap["n_entries"], 25)

    def test_09_no_prng_ast(self):
        forbidden = {"random", "numpy.random"}
        # Check every python file under the scripts dir
        for py in self.scripts.rglob("*.py"):
            tree = ast.parse(py.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        self.assertNotIn(a.name, forbidden, f"{py} imports {a.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module in forbidden:
                        self.fail(f"{py} imports from {node.module}")

    def test_10_interpreter_guard_in_common(self):
        text = (self.scripts / "_common.py").read_text()
        self.assertIn("/usr/bin/python3", text)
        self.assertIn("interpreter guard", text)

    def test_11_c48_env_flags_default_off(self):
        # every setdefault, never overwrite
        text = (self.scripts / "_common.py").read_text()
        self.assertIn("os.environ.setdefault", text)
        # no unguarded os.environ[...] = to those flags
        self.assertNotIn('os.environ["PYTHONHASHSEED"] =', text)

    def test_12_no_sidecar_nonfactor(self):
        for py in self.scripts.rglob("*.py"):
            self.assertNotIn("sidecar_nonfactor", py.read_text())

    def test_13_ab_pairs_present(self):
        # winner AB per song per stem
        for sha16 in ("31a164f845f8e27e",):
            for stem in ("drums", "bass"):
                p = ROOT / f"data/recreate_v2/ab_pairs/{sha16}/{stem}/iter_1"
                self.assertTrue(p.exists(), f"missing AB dir {p}")
                self.assertTrue((p / "original.wav").exists())
                self.assertTrue((p / "rendered.wav").exists())

    def test_14_ab_lufs_normalized_close_to_minus_23(self):
        import soundfile as sf
        import numpy as np
        import pyloudnorm as pln
        sha16 = "31a164f845f8e27e"
        p = ROOT / f"data/recreate_v2/ab_pairs/{sha16}/drums/iter_1/original.wav"
        y, sr = sf.read(str(p))
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        meter = pln.Meter(sr)
        lu = meter.integrated_loudness(y)
        self.assertTrue(-30.0 < lu < -18.0, f"LUFS {lu} out of range")

    def test_15_verdict_matches_gate_criterion(self):
        v = json.loads((self.impl / "verdict.json").read_text())
        d = v["drums"]["songs_pass"]
        b = v["bass"]["songs_pass"]
        n_ok = int(d >= 3) + int(b >= 3)
        want = {2: "RC10_DRUMS_BASS_LANDS", 1: "RC10_DRUMS_BASS_PARTIAL", 0: "RC10_DRUMS_BASS_FAILS"}[n_ok]
        self.assertEqual(v["verdict"], want)


if __name__ == "__main__":
    unittest.main(verbosity=2)
