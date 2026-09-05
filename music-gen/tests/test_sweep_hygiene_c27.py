#!/usr/bin/python3
"""c27 Track A regression tests for _sweep_hygiene_c27.

Covers the operator-mandated procedure fix (2026-09-05):
  - Per-candidate render->score->delete
  - Running top-K displacement rule
  - Post-pin cleanup
  - df-guard prune @ >= 85 % + abort @ >= 90 %
  - Legacy batch-render regression path retained

Discipline: /usr/bin/python3 interpreter guard, no PRNG, no sidecar_nonfactor,
no VST3 state APIs, no live network.
"""
from __future__ import annotations

import ast
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.sound_match import _sweep_hygiene_c27 as hyg  # noqa: E402


def _make_row(path: Path, composite: float, sha: str = "abcd") -> dict:
    return {
        "render_path": str(path),
        "composite": composite,
        "render_wav_sha": sha,
    }


class TestRunningTopK(unittest.TestCase):
    def test_01_per_candidate_delete_bounded_disk(self) -> None:
        """Mock a 10-cell sweep with K=3: assert at most 3 WAVs on disk at any peak."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            topk = hyg.RunningTopK(k=3)
            peak = 0
            for i in range(10):
                p = tmp / f"cell_{i:03d}.wav"
                p.write_bytes(b"\x00" * 128)
                topk.push(_make_row(p, composite=100.0 + i, sha=f"sha{i}"))
                current = len(list(tmp.glob("*.wav")))
                peak = max(peak, current)
            self.assertLessEqual(peak, 3, f"peak WAV count on disk = {peak}, expected <=3")
            self.assertEqual(len(topk.kept_rows()), 3)

    def test_02_running_heap_displacement_rule(self) -> None:
        """Better composite (lower) should evict worst; new WAV survives, old is deleted."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            topk = hyg.RunningTopK(k=2)
            # push worst=500, mid=300 -> heap full [500,300]
            p1 = tmp / "a.wav"; p1.write_bytes(b"1")
            p2 = tmp / "b.wav"; p2.write_bytes(b"2")
            topk.push(_make_row(p1, 500.0, "a"))
            topk.push(_make_row(p2, 300.0, "b"))
            self.assertTrue(p1.exists())
            self.assertTrue(p2.exists())
            # push better cell (100) - should evict p1 (500).
            p3 = tmp / "c.wav"; p3.write_bytes(b"3")
            deleted = topk.push(_make_row(p3, 100.0, "c"))
            self.assertEqual(deleted, str(p1))
            self.assertFalse(p1.exists(), "p1 should be evicted+deleted")
            self.assertTrue(p2.exists())
            self.assertTrue(p3.exists())
            # push worse cell (999) - rejected on entry, its WAV deleted.
            p4 = tmp / "d.wav"; p4.write_bytes(b"4")
            deleted2 = topk.push(_make_row(p4, 999.0, "d"))
            self.assertEqual(deleted2, str(p4))
            self.assertFalse(p4.exists())

    def test_03_post_pin_cleanup_deletes_non_pin(self) -> None:
        """After pin, all kept WAVs except the pinned path are deleted."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            paths = []
            rows = []
            for i in range(3):
                p = tmp / f"kept_{i}.wav"
                p.write_bytes(b"x")
                paths.append(p)
                rows.append(_make_row(p, composite=float(i), sha=f"s{i}"))
            pinned = {str(paths[0])}
            deleted = hyg.prune_after_pin(rows, pinned)
            self.assertEqual(set(deleted), {str(paths[1]), str(paths[2])})
            self.assertTrue(paths[0].exists())
            self.assertFalse(paths[1].exists())
            self.assertFalse(paths[2].exists())

    def test_04_df_guard_prune_trigger_at_85pct(self) -> None:
        """df guard: usage=87 % (>=85) triggers _prune_stale_sweep_audio."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stage = root / "stage"; stage.mkdir()
            with mock.patch.object(hyg, "_disk_used_pct_user", side_effect=[87.0, 82.0]), \
                 mock.patch.object(hyg, "_prune_stale_sweep_audio", return_value=["/tmp/foo.wav", "/tmp/bar.wav"]) as mprune:
                status = hyg.df_guard_before_stage(
                    workspace_root=root, stage_dir=stage,
                    prune_pct=85.0, abort_pct=90.0,
                )
            mprune.assert_called_once()
            self.assertEqual(status["used_pct_before"], 87.0)
            self.assertEqual(status["used_pct_after"], 82.0)
            self.assertEqual(status["n_pruned"], 2)

    def test_05_df_guard_abort_at_90pct_after_prune(self) -> None:
        """df guard: usage>=90 % post-prune raises RuntimeError (FD-1 halt)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stage = root / "stage"; stage.mkdir()
            with mock.patch.object(hyg, "_disk_used_pct_user", side_effect=[91.0, 90.5]), \
                 mock.patch.object(hyg, "_prune_stale_sweep_audio", return_value=[]):
                with self.assertRaisesRegex(RuntimeError, "df-guard abort"):
                    hyg.df_guard_before_stage(
                        workspace_root=root, stage_dir=stage,
                        prune_pct=85.0, abort_pct=90.0,
                    )

    def test_06_nan_composite_rejected_on_entry(self) -> None:
        """NaN or inf composite: WAV auto-deleted, cell excluded from top-K."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            topk = hyg.RunningTopK(k=5)
            p = tmp / "nan.wav"; p.write_bytes(b"n")
            topk.push(_make_row(p, float("nan"), "n"))
            self.assertFalse(p.exists())
            self.assertEqual(len(topk.kept_rows()), 0)
            self.assertEqual(topk.stats()["n_rejected"], 1)

    def test_07_stale_audio_pruner_respects_age_gate(self) -> None:
        """_prune_stale_sweep_audio: freshly-written WAVs (age<60s) survive."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sweep_dir = root / "data" / "v4" / "profiles" / "abc123" / "bass_sweep_stage2"
            sweep_dir.mkdir(parents=True)
            fresh = sweep_dir / "fresh.wav"; fresh.write_bytes(b"1")
            pruned = hyg._prune_stale_sweep_audio(root, min_age_seconds=60.0)
            self.assertEqual(pruned, [], "fresh WAV under age gate should survive")
            self.assertTrue(fresh.exists())
            # Force-age the file and re-run.
            past = fresh.stat().st_mtime - 120.0
            os.utime(fresh, (past, past))
            pruned2 = hyg._prune_stale_sweep_audio(root, min_age_seconds=60.0)
            self.assertEqual(pruned2, [str(fresh)])
            self.assertFalse(fresh.exists())


class TestDiscipline(unittest.TestCase):
    """AST-scan the c27 hygiene module for banned surfaces."""

    def _module_source(self) -> str:
        return (REPO / "scripts" / "sound_match" / "_sweep_hygiene_c27.py").read_text()

    def test_08_interpreter_guard_present(self) -> None:
        src = self._module_source()
        self.assertTrue(src.startswith("#!/usr/bin/python3"),
                        "canonical /usr/bin/python3 shebang required")

    def test_09_no_prng_imports(self) -> None:
        src = self._module_source()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertNotIn(a.name, {"random", "numpy.random"})
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module, {"random", "numpy.random"})

    def test_10_no_forbidden_call_patterns(self) -> None:
        """AST scan: no forbidden imports or attribute-calls in real code.

        The discipline docstring may name these strings; the test scans the
        AST for import/call sites only.
        """
        src = self._module_source()
        tree = ast.parse(src)
        banned_modules = {"scripts.classifier.sidecar_nonfactor"}
        banned_attrs = {"get_state", "save_state", "save_preset",
                        "load_state", "set_state", "set_state_information",
                        "get_state_information"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.assertNotIn(a.name, banned_modules)
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module or "", banned_modules)
            if isinstance(node, ast.Attribute):
                self.assertNotIn(node.attr, banned_attrs)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, banned_attrs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
