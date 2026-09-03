#!/usr/bin/python3
"""c25 one-off driver retirement — test suite (≥12 cases)."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import pathlib
import sys
import unittest

os.environ.setdefault("PYTHONHASHSEED", "0")

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUBRIC_DOC = ROOT / "docs" / "v3_spine_oneoff_driver_retirement_c25_rubric.md"
RUBRIC_HASH_FILE = ROOT / "data" / "v3" / "retirement" / "c25" / "rubric_hash.txt"
VERDICT_FILE = ROOT / "data" / "v3" / "retirement" / "c25" / "verdict.json"
MOVES_JSONL = ROOT / "data" / "v3" / "retirement" / "c25" / "moves.jsonl"
GREP_ZERO_JSON = ROOT / "data" / "v3" / "retirement" / "c25" / "grep_zero_verification.json"
ANCHOR_POST = ROOT / "data" / "v3" / "retirement" / "c25" / "anchor_preservation_post.json"
ANCHOR_PRE = ROOT / "data" / "v3" / "retirement" / "c25" / "anchor_preservation_pre.json"
BYTE_DET = ROOT / "data" / "v3" / "retirement" / "c25" / "byte_determinism.json"
CATALOG = ROOT / "data" / "v3" / "recreate_v3" / "retirement_catalog_c22.json"
RETIREMENT_DIR = ROOT / "scripts" / "v3_spine" / "retirement_c25"
MOVE_SCRIPT = RETIREMENT_DIR / "move.py"
STALE_DIR = ROOT / "tools" / "stale" / "oneoff_v3_drivers_retired_c25"


def _sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class C25RetirementTests(unittest.TestCase):

    def test_01_rubric_mtime_pre_registration(self):
        rubric_mtime = RUBRIC_DOC.stat().st_mtime
        for p in RETIREMENT_DIR.rglob("*.py"):
            self.assertLess(
                rubric_mtime, p.stat().st_mtime,
                f"rubric doc must pre-date every retirement_c25 script; "
                f"{p.name} mtime={p.stat().st_mtime}")

    def test_02_three_way_rubric_hash_chain(self):
        doc_sha = _sha256(RUBRIC_DOC)
        file_sha = RUBRIC_HASH_FILE.read_text().strip()
        self.assertEqual(doc_sha, file_sha,
                         "rubric_hash.txt must byte-equal doc SHA-256")
        verdict = json.loads(VERDICT_FILE.read_text())
        self.assertEqual(verdict["rubric_hash_v3_retirement"], doc_sha)

    def test_03_per_file_sha_preservation_across_rename(self):
        with open(MOVES_JSONL) as f:
            moves = [json.loads(l) for l in f if l.strip()]
        self.assertEqual(len(moves), 37)
        for m in moves:
            self.assertIn(m["action"], {"renamed", "already_moved"},
                          f"unexpected action: {m}")
            self.assertIsNotNone(m["sha256"], f"missing sha for {m}")
            dst = ROOT / m["dst"]
            self.assertTrue(dst.exists(), f"destination missing: {dst}")
            self.assertEqual(_sha256(dst), m["sha256"],
                             f"post-move SHA drift on {m['basename']}")

    def test_04_grep_zero_import_assertion(self):
        gz = json.loads(GREP_ZERO_JSON.read_text())
        self.assertEqual(gz["python_import_matches"], [],
                         f"broken imports found: {gz['python_import_matches']}")
        self.assertTrue(gz["zero_broken_imports"])

    def test_05_preserved_set_sha_anchor_list(self):
        post = json.loads(ANCHOR_POST.read_text())
        pre = json.loads(ANCHOR_PRE.read_text())
        self.assertGreaterEqual(post["n_entries"], 25,
                                f"expected ≥25 preserved anchors, "
                                f"got {post['n_entries']}")
        pre_map = {e["path"]: e["sha256"] for e in pre["entries"]}
        post_map = {e["path"]: e["sha256"] for e in post["entries"]}
        for path, post_sha in post_map.items():
            self.assertEqual(pre_map.get(path), post_sha,
                             f"anchor drift: {path}")
        # Named specific anchors that must be present.
        must_have = [
            "scripts/palette_render/render_stem.py",
            "scripts/v3_spine/recreate_v3.py",
            "scripts/v3_spine/v3_pipeline/env_pin.py",
            "scripts/v3_spine/midi_from_json_events.py",
        ]
        for path in must_have:
            self.assertIn(path, post_map, f"missing named anchor: {path}")

    def test_06_catalog_vs_actual_consistency(self):
        cat = json.loads(CATALOG.read_text())
        targets = []
        for group in cat["candidates"].values():
            targets.extend(group)
        self.assertEqual(len(targets), 37)
        for rel in targets:
            src = ROOT / rel
            dst = STALE_DIR / pathlib.Path(rel).name
            # Post-run: EITHER at source OR at destination (never both;
            # after move the source is gone).
            self.assertTrue(
                src.exists() or dst.exists(),
                f"catalog entry not resolvable: {rel}")

    def test_07_idempotence(self):
        det = json.loads(BYTE_DET.read_text())
        self.assertTrue(det["byte_determinism_holds"])
        self.assertEqual(det["first_run_determinism_sha"],
                         det["second_run_determinism_sha"])

    def test_08_interpreter_guard_on_retirement_script(self):
        text = MOVE_SCRIPT.read_text()
        self.assertTrue(text.startswith("#!/usr/bin/python3"),
                        "move.py must have /usr/bin/python3 shebang")
        self.assertIn("sys.executable ==", text,
                      "move.py must assert sys.executable")

    def test_09_no_prng_grep(self):
        forbidden = {"random", "secrets", "numpy.random", "torch.random"}
        for p in RETIREMENT_DIR.rglob("*.py"):
            src = p.read_text()
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn(alias.name, forbidden,
                                         f"{p.name}: forbidden import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module in forbidden:
                        self.fail(f"{p.name}: forbidden ImportFrom {node.module}")

    def test_10_no_sidecar_nonfactor_grep(self):
        pat_import = "import scripts.classifier.sidecar_nonfactor"
        pat_from = "from scripts.classifier.sidecar_nonfactor"
        for p in RETIREMENT_DIR.rglob("*.py"):
            text = p.read_text()
            self.assertNotIn(pat_import, text,
                             f"{p.name}: sidecar_nonfactor import present")
            self.assertNotIn(pat_from, text,
                             f"{p.name}: sidecar_nonfactor import present")

    def test_11_c22_anchor_pre_post_byte_identical(self):
        post = json.loads(ANCHOR_POST.read_text())
        by_path = {e["path"]: e["sha256"] for e in post["entries"]}
        # c22 unified driver.
        self.assertEqual(
            by_path.get("scripts/v3_spine/recreate_v3.py"),
            _sha256(ROOT / "scripts" / "v3_spine" / "recreate_v3.py"))
        # c22 env_pin module.
        self.assertEqual(
            by_path.get("scripts/v3_spine/v3_pipeline/env_pin.py"),
            _sha256(ROOT / "scripts" / "v3_spine" / "v3_pipeline" / "env_pin.py"))
        # c21 render_stem.py anchor SHA prefix.
        rs_sha = _sha256(ROOT / "scripts" / "palette_render" / "render_stem.py")
        self.assertTrue(
            rs_sha.startswith("214372d920a319a9"),
            f"render_stem.py anchor drift: {rs_sha}")

    def test_12_vst3_state_api_ast_forbidden(self):
        forbidden_names = {"save_state", "get_state", "save_preset",
                           "load_state", "set_state"}
        for p in RETIREMENT_DIR.rglob("*.py"):
            src = p.read_text()
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    name = None
                    if isinstance(func, ast.Attribute):
                        name = func.attr
                    elif isinstance(func, ast.Name):
                        name = func.id
                    if name in forbidden_names:
                        self.fail(f"{p.name}: forbidden VST3 state API call: {name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
