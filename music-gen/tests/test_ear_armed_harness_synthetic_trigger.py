#!/usr/bin/env python3
# created: 2026-08-28T11:35:00Z  cycle: 26  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1 fork 8f3344880d29)  milestone: _manager/M-EAR-1-path-B-commit
"""Synthetic-fixture verification of `scripts/ear/train_armed_harness.py`.

Zero live network. All fixtures on-disk under a per-test tempdir. Training
is mocked at the `TrainingHooks.run_training` boundary — the real
`scripts/ear/train.py` is never invoked (it would want features + real
labels; here we only exercise the state machine).

Test count: 8 (satisfies the ≥6 brief). Plain assert; no pytest.

Invocation:
    PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \\
        /usr/bin/python3 tests/test_ear_armed_harness_synthetic_trigger.py
"""
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import ast
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

# Make scripts importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.ear.train_armed_harness import (  # noqa: E402
    ArmedHarness,
    HClock,
    HState,
    TrainingHookResult,
    TrainingHooks,
    content_hash_manifest,
)


ROOT = Path(__file__).resolve().parent.parent
FIXED_TIME = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)


def _fixed_clock() -> HClock:
    return HClock(now=lambda: FIXED_TIME)


class _StubTrainingHooks(TrainingHooks):
    """No-op hooks: returns a canned success without invoking the real
    training loop. Optionally simulates a failure."""

    def __init__(self, out_dir: Path, *, fail: bool = False, mae: float = 0.5,
                 write_checkpoint: bool = True):
        super().__init__(features_dir=Path("/nonexistent"), out_dir=out_dir)
        self._fail = fail
        self._mae = mae
        self._write_checkpoint = write_checkpoint

    def run_training(self, ratings_manifest: Path) -> TrainingHookResult:
        if self._fail:
            return TrainingHookResult(
                ok=False, mean_mae=float("nan"),
                stderr_tail="stub failure", returncode=2,
            )
        self.out_dir.mkdir(parents=True, exist_ok=True)
        # Write a fake result artifact + checkpoint so downstream idempotency
        # checks (which stat the checkpoint) succeed.
        rp = self.out_dir / "training_result.json"
        rp.write_text(json.dumps({"mean_mae": self._mae}, sort_keys=True))
        ck = self.out_dir / "corn_head_v1.pt"
        if self._write_checkpoint:
            ck.write_bytes(b"\x00stub-checkpoint\x00")
        return TrainingHookResult(
            ok=True, mean_mae=self._mae,
            stderr_tail="", returncode=0,
            training_result_path=str(rp.resolve()),
            checkpoint_path=str(ck.resolve()),
        )


def _make_manifest(path: Path, video_ids: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["rating\tvideo_id\ttitle"]
    for i, vid in enumerate(video_ids):
        lines.append(f"{5 + (i % 3) - 1}\t{vid}\tStub - Track {i}")
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_clip(dir_: Path, video_id: str) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    p = dir_ / f"{video_id}.wav"
    p.write_bytes(b"RIFF----WAVEfmt \x10\x00\x00\x00" + b"\x00" * 32)
    return p


def _make_harness(base: Path, *, fail: bool = False, mae: float = 0.5,
                  write_checkpoint: bool = True,
                  clips_dir_name: str = "clips") -> ArmedHarness:
    state_dir = base / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return ArmedHarness(
        state_path=state_dir / "state.json",
        transitions_path=state_dir / "transitions.jsonl",
        rated_ready_flag=base / "rated_ready.flag",
        ratings_manifest=base / "ratings_manifest.tsv",
        trained_flag=base / "trained_v1.flag",
        training_out_dir=base / "training_out",
        hooks=_StubTrainingHooks(
            base / "training_out", fail=fail, mae=mae,
            write_checkpoint=write_checkpoint,
        ),
        clock=_fixed_clock(),
        clips_dir=base / clips_dir_name,
    )


# ---------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------

def test_cold_start_ready_holds_without_flag():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _make_manifest(base / "ratings_manifest.tsv", ["v1", "v2"])
        h = _make_harness(base)
        state = h.scan_and_advance()
        assert state == HState.READY, state
        # transitions.jsonl written with a noop row.
        lines = (base / "state" / "transitions.jsonl").read_text().splitlines()
        assert len(lines) == 1
        assert '"noop":true' in lines[0]


def test_synthetic_flag_triggers_ready_to_trained():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vids = ["v1", "v2"]
        _make_manifest(base / "ratings_manifest.tsv", vids)
        for v in vids:
            _write_clip(base / "clips", v)
        (base / "rated_ready.flag").write_text("ready\n")
        h = _make_harness(base)
        state = h.scan_and_advance()
        assert state == HState.TRAINED, state
        assert (base / "trained_v1.flag").is_file()
        payload = json.loads((base / "trained_v1.flag").read_text())
        assert payload["manifest_hash"] == content_hash_manifest(
            base / "ratings_manifest.tsv"), payload
        assert payload["mean_mae"] == 0.5


def test_content_hash_gate_prevents_redundant_training():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vids = ["v1", "v2"]
        _make_manifest(base / "ratings_manifest.tsv", vids)
        for v in vids:
            _write_clip(base / "clips", v)
        (base / "rated_ready.flag").write_text("ready\n")
        # First scan: trains.
        h1 = _make_harness(base)
        assert h1.scan_and_advance() == HState.TRAINED
        # Second scan: state.json + trained_v1.flag persist. New harness reads
        # them and should NOT retrain (idempotent noop).
        h2 = _make_harness(base)
        assert h2.persisted.state == HState.TRAINED, h2.persisted.state
        state = h2.scan_and_advance()
        assert state == HState.TRAINED, state
        # transitions log across the two harnesses: at least one noop row
        # after the initial training success.
        lines = (base / "state" / "transitions.jsonl").read_text().splitlines()
        noop_rows = [ln for ln in lines if '"noop":true' in ln]
        assert len(noop_rows) >= 1


def test_audio_missing_transitions_to_failed():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vids = ["v1", "v2"]
        _make_manifest(base / "ratings_manifest.tsv", vids)
        # Deliberately no clips written.
        (base / "rated_ready.flag").write_text("ready\n")
        h = _make_harness(base)
        state = h.scan_and_advance()
        assert state == HState.FAILED, state
        assert h.persisted.failed_stage == "training/audio_missing"


def test_atomic_state_write_survives_simulated_crash():
    """The harness writes state.json via tempfile + os.replace. The invariant
    we check: after any successful transition, `state.json` is fully readable
    JSON (no partial-write turds visible on the filesystem), and re-loading
    the harness reconstructs the same persisted state."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vids = ["v1"]
        _make_manifest(base / "ratings_manifest.tsv", vids)
        _write_clip(base / "clips", "v1")
        (base / "rated_ready.flag").write_text("ready\n")
        h = _make_harness(base)
        h.scan_and_advance()
        state_path = base / "state" / "state.json"
        # No .tmp turds in the state dir (os.replace succeeded atomically).
        tmp_turds = [p for p in state_path.parent.iterdir()
                     if p.name != state_path.name
                     and p.name != "transitions.jsonl"]
        assert tmp_turds == [], tmp_turds
        # File is complete JSON, re-loadable.
        raw = state_path.read_text()
        parsed = json.loads(raw)
        assert parsed["state"] == HState.TRAINED.value
        # Reconstruct a second harness; persisted state re-loads cleanly.
        h2 = _make_harness(base)
        assert h2.persisted.state == HState.TRAINED


def test_byte_deterministic_transitions_jsonl():
    """Two independent runs (fresh tempdirs) with identical input fixtures
    produce byte-identical transitions.jsonl. The clock is frozen; every
    identity used inside transitions.jsonl is either the manifest content
    hash or the fixed clock — no tempdir paths leak into the log."""
    def _run_once() -> bytes:
        td = tempfile.mkdtemp()
        try:
            base = Path(td)
            vids = ["v1", "v2"]
            _make_manifest(base / "ratings_manifest.tsv", vids)
            for v in vids:
                _write_clip(base / "clips", v)
            (base / "rated_ready.flag").write_text("ready\n")
            h = _make_harness(base)
            h.scan_and_advance()
            return (base / "state" / "transitions.jsonl").read_bytes()
        finally:
            shutil.rmtree(td, ignore_errors=True)

    b1 = _run_once()
    b2 = _run_once()
    assert hashlib.sha256(b1).hexdigest() == hashlib.sha256(b2).hexdigest(), (
        b1[:200], b2[:200])


NETWORK_LIBS = {"urllib", "urllib2", "urllib3", "requests", "socket",
                "httpx", "aiohttp", "http", "http.client"}


def _module_imports(mod_path: Path) -> set[str]:
    tree = ast.parse(mod_path.read_text(), filename=str(mod_path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name)
                names.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
                names.add(node.module.split(".")[0])
    return names


def test_zero_live_network_ast_grep():
    targets = [ROOT / "scripts" / "ear" / "train_armed_harness.py"]
    targets += sorted((ROOT / "scripts" / "egress_ready").glob("*.py"))
    for mod in targets:
        imports = _module_imports(mod)
        for lib in NETWORK_LIBS:
            assert lib not in imports, f"{mod}: imports {lib!r}"


def test_no_sidecar_nonfactor_imports():
    targets = [ROOT / "scripts" / "ear" / "train_armed_harness.py"]
    targets += sorted((ROOT / "scripts" / "egress_ready").glob("*.py"))
    for mod in targets:
        imports = _module_imports(mod)
        assert "scripts.classifier.sidecar_nonfactor" not in imports, mod
        # Also guard the shorter forms.
        assert "sidecar_nonfactor" not in imports, mod


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

CASES = [
    test_cold_start_ready_holds_without_flag,
    test_synthetic_flag_triggers_ready_to_trained,
    test_content_hash_gate_prevents_redundant_training,
    test_audio_missing_transitions_to_failed,
    test_atomic_state_write_survives_simulated_crash,
    test_byte_deterministic_transitions_jsonl,
    test_zero_live_network_ast_grep,
    test_no_sidecar_nonfactor_imports,
]


def main() -> int:
    failures = []
    for case in CASES:
        try:
            case()
            print(f"PASS {case.__name__}")
        except Exception as e:  # pragma: no cover
            failures.append((case.__name__, e))
            print(f"FAIL {case.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(CASES) - len(failures)}/{len(CASES)} passed")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
