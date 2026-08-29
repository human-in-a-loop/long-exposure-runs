#!/usr/bin/env python3
# created: 2026-08-28T11:35:00Z  cycle: 26  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1 fork 8f3344880d29)  milestone: _manager/M-EAR-1-path-B-commit
"""Synthetic-fixture verification of `scripts/ear/train_armed_harness.py`.

Zero live network. All fixtures on-disk under a per-test tempdir. Training
is mocked at the `TrainingHooks.run_training` boundary — the real
`scripts/ear/train.py` is never invoked (it would want features + real
labels; here we only exercise the state machine).

Cycle 31 branch C: extended from 8 to 17 cases. Adds:
    (a) ratings-manifest content-hash-change re-fires training after
        prior TRAINED (test 9);
    (b) SB1/SB2/SB3 computability from `scripts/ear/sb_dry_run.py`
        (tests 10, 11, 12);
    (c) mock-egress-unblock probe: two consecutive media_ok=true
        rows drive IDLE→ARMED→TRIGGERED→...→READY on the cycle-8
        egress-ready machine (test 13);
    (d) zero-live-network AST-grep extended to cover sb_dry_run.py
        (existing test 7, extended and asserted here explicitly as
        test 14);
    (e) per-FAILED-substate resumability (tests 15a-c);
    (f) idempotent-on-repeat-flag with same content hash (existing
        test 3 covers this; test 16 explicitly asserts one bookkeeping
        row per repeat scan);
    (g) SB dry-run byte-determinism × 2 (test 17).

Plain assert; no pytest. Total case count: 17.

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
    targets.append(ROOT / "scripts" / "ear" / "sb_dry_run.py")
    for mod in targets:
        imports = _module_imports(mod)
        assert "scripts.classifier.sidecar_nonfactor" not in imports, mod
        # Also guard the shorter forms.
        assert "sidecar_nonfactor" not in imports, mod


# ===========================================================================
# Cycle 31 branch C — extended cases (9..17)
# ===========================================================================

import subprocess


ARR_DIR = ROOT / "data" / "ear" / "armed_harness_reinforcement"
RUBRIC_PATH = ROOT / "docs" / "ear_armed_harness_fixture_rubric.md"
SB_VERDICT_PATH = ARR_DIR / "sb_dry_run_verdict.json"


def _sb_verdict() -> dict:
    """Read the on-disk SB-dry-run verdict."""
    assert SB_VERDICT_PATH.is_file(), (
        f"SB dry-run verdict missing: {SB_VERDICT_PATH}. "
        "Run: PYTHONPATH=. /usr/bin/python3 scripts/ear/sb_dry_run.py")
    return json.loads(SB_VERDICT_PATH.read_text(encoding="utf-8"))


# (a) — scenario a
def test_ratings_manifest_content_hash_change_refires_training():
    """Preload TRAINED state with an initial manifest, then swap the manifest
    for one with a different content hash. Harness must transition
    TRAINED → READY (forced_reset) → TRAINING → TRAINED with the new
    manifest hash recorded in trained_v1.flag."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vids_a = ["v1", "v2"]
        vids_b = ["v1", "v2", "v3"]
        _make_manifest(base / "ratings_manifest.tsv", vids_a)
        for v in vids_b:  # write all clips upfront so audio-missing does not fire
            _write_clip(base / "clips", v)
        (base / "rated_ready.flag").write_text("ready\n")
        h1 = _make_harness(base)
        assert h1.scan_and_advance() == HState.TRAINED
        hash_a = json.loads((base / "trained_v1.flag").read_text())["manifest_hash"]
        # Swap manifest for one with a different content hash.
        _make_manifest(base / "ratings_manifest.tsv", vids_b)
        h2 = _make_harness(base)
        assert h2.persisted.state == HState.TRAINED, h2.persisted.state
        state = h2.scan_and_advance()
        assert state == HState.TRAINED, state
        hash_b = json.loads((base / "trained_v1.flag").read_text())["manifest_hash"]
        assert hash_a != hash_b, (hash_a, hash_b)
        # transitions.jsonl carries the retrain-forced_reset row.
        text = (base / "state" / "transitions.jsonl").read_text()
        assert '"forced_reset":true' in text, text[-400:]


# (b/SB1) — scenario b, SB1
def test_sb1_computable_from_synthetic_dry_run():
    v = _sb_verdict()
    for k in ("sb1_margin", "majority_class_baseline_mae",
              "mean_integer_baseline_mae", "sb1_baseline_hard"):
        assert k in v, k
        x = v[k]
        assert isinstance(x, (int, float)) and float(x) == float(x), (k, x)
    assert v["sb1_ok"] is True, v


# (b/SB2) — scenario b, SB2
def test_sb2_computable_from_synthetic_dry_run():
    v = _sb_verdict()
    assert v["sb2_mean_tau"] == v["sb2_mean_tau"], v["sb2_mean_tau"]  # not NaN
    per = v["sb2_per_resample_tau"]
    assert isinstance(per, list) and len(per) == 10, per
    for x in per:
        assert isinstance(x, (int, float)) and float(x) == float(x), x
    assert v["sb2_ok"] is True, v


# (b/SB3) — scenario b, SB3
def test_sb3_computable_from_synthetic_dry_run():
    v = _sb_verdict()
    per = v["sb3_detection_rate_per_leak_type"]
    for k in ("artist", "genre", "era"):
        assert k in per, k
        r = per[k]
        assert isinstance(r, (int, float)) and float(r) == float(r), (k, r)
        assert 0.0 <= float(r) <= 1.0, (k, r)
    assert v["sb3_ok"] is True, v


# (c) — scenario c
def test_mock_egress_unblock_probe_fires_full_state_chain():
    """Author a synthetic egress_status.jsonl with two consecutive
    media_ok=true rows; run the cycle-8 egress-ready state machine
    against it with mocked subprocess hooks; assert transitions
    IDLE → ARMED → (not visible when both trues arrive together)
    → TRIGGERED → HARVESTING → CHUNKING → CLASSIFYING → READY.
    Record transitions to state_transitions_verification.jsonl.
    """
    from scripts.egress_ready.state import (
        EgressReadyMachine, State, Clock as EClock,
    )
    from scripts.egress_ready.subprocess_hooks import (
        SubprocessHooks, HookResult,
    )

    class _MockHooks(SubprocessHooks):
        def __init__(self):
            pass  # skip parent init; we never subprocess.run anything
        def _ok(self, tag: str) -> HookResult:
            return HookResult(ok=True, returncode=0, stderr_tail=f"mock-{tag}",
                              duration_s=0.0)
        def run_harvest(self): return self._ok("harvest")
        def run_chunker(self): return self._ok("chunker")
        def run_classifier(self): return self._ok("classifier")
        def write_ready_flag(self): return self._ok("ready_flag")

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        state_dir = base / "state"
        state_dir.mkdir()

        # Author mock egress_status.jsonl (two consecutive fresh media_ok=true).
        egress = base / "egress_status.jsonl"
        row1 = {"ts": "2026-08-29T12:00:00Z", "media_ok": True,
                "http_code": 206, "target": "*.googlevideo.com"}
        row2 = {"ts": "2026-08-29T12:15:00Z", "media_ok": True,
                "http_code": 206, "target": "*.googlevideo.com"}
        egress.write_text(json.dumps(row1) + "\n" + json.dumps(row2) + "\n")

        # Also mirror to ARR_DIR/mock_egress_status.jsonl so the
        # integration test / repro can find it later.
        ARR_DIR.mkdir(parents=True, exist_ok=True)
        mock_dst = ARR_DIR / "mock_egress_status.jsonl"
        mock_dst.write_text(egress.read_text())

        # Frozen clock at 2026-08-29T12:20 so both rows are fresh.
        fixed = datetime(2026, 8, 29, 12, 20, 0, tzinfo=timezone.utc)
        m = EgressReadyMachine(
            state_path=state_dir / "state.json",
            transitions_path=state_dir / "transitions.jsonl",
            egress_status_path=egress,
            hooks=_MockHooks(),
            clock=EClock(now=lambda: fixed),
        )
        assert m.persisted.state == State.IDLE
        final = m.scan_and_advance()
        assert final == State.READY, final

        # Assert atomic state.json write — no *.tmp turds.
        turds = [p for p in state_dir.iterdir()
                 if p.name not in ("state.json", "transitions.jsonl")
                 and not p.name.startswith(".")]
        # Diagnostic files land under state_dir when there's a failure;
        # this is a success path so nothing extra.
        assert turds == [], turds

        # Assert every transition is on the frozen legal-transition path.
        lines = (state_dir / "transitions.jsonl").read_text().splitlines()
        events = [json.loads(ln) for ln in lines if ln.strip()]
        seq = [(e["from_state"], e["to_state"]) for e in events]
        # Legal chain: IDLE -> TRIGGERED (skipping ARMED because both trues are in one scan)
        # -> HARVESTING -> CHUNKING -> CLASSIFYING -> READY.
        expected = [
            ("IDLE", "TRIGGERED"),
            ("TRIGGERED", "HARVESTING"),
            ("HARVESTING", "CHUNKING"),
            ("CHUNKING", "CLASSIFYING"),
            ("CLASSIFYING", "READY"),
        ]
        assert seq == expected, seq

        # Persist the verified sequence for the reinforcement artifact.
        with (ARR_DIR / "state_transitions_verification.jsonl").open("w") as fh:
            for ev in events:
                fh.write(json.dumps(ev, sort_keys=True) + "\n")


# (d) — extended AST coverage
def test_zero_live_network_ast_grep_covers_sb_dry_run():
    """AST-walk asserts zero live-network imports in
    scripts/ear/sb_dry_run.py AND in this fixture file."""
    targets = [ROOT / "scripts" / "ear" / "sb_dry_run.py",
               Path(__file__).resolve()]
    for mod in targets:
        imports = _module_imports(mod)
        for lib in NETWORK_LIBS:
            assert lib not in imports, f"{mod}: imports {lib!r}"


# (e) — per-FAILED-substate resumability
def _preload_state(base: Path, state_json: dict) -> None:
    """Write a state.json that the harness constructor will load."""
    state_dir = base / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "state.json").write_text(
        json.dumps(state_json, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def test_resumable_from_failed_training_loop():
    """Preload state.json in FAILED[training/loop]; assert retry on next
    scan transitions FAILED → TRAINING → TRAINED (clean restart)."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vids = ["v1"]
        _make_manifest(base / "ratings_manifest.tsv", vids)
        _write_clip(base / "clips", "v1")
        (base / "rated_ready.flag").write_text("ready\n")
        _preload_state(base, {
            "state": "FAILED",
            "last_transition_utc": "2026-08-29T12:00:00Z",
            "manifest_hash": "deadbeef" * 8,
            "checkpoint_path": None,
            "failed_stage": "training/loop",
            "training_result_path": None,
        })
        h = _make_harness(base)
        assert h.persisted.state == HState.FAILED
        assert h.persisted.failed_stage == "training/loop"
        state = h.scan_and_advance()
        assert state == HState.TRAINED, state


def test_resumable_from_failed_training_audio_missing_when_audio_returns():
    """Preload FAILED[training/audio_missing]; on retry with audio now
    present, transitions to TRAINED."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vids = ["v1", "v2"]
        _make_manifest(base / "ratings_manifest.tsv", vids)
        for v in vids:
            _write_clip(base / "clips", v)
        (base / "rated_ready.flag").write_text("ready\n")
        _preload_state(base, {
            "state": "FAILED",
            "last_transition_utc": "2026-08-29T12:00:00Z",
            "manifest_hash": None,
            "checkpoint_path": None,
            "failed_stage": "training/audio_missing",
            "training_result_path": None,
        })
        h = _make_harness(base)
        state = h.scan_and_advance()
        assert state == HState.TRAINED, state


def test_resumable_from_failed_training_audio_missing_stays_failed_when_still_missing():
    """Preload FAILED[training/audio_missing]; on retry with audio STILL
    missing, transitions FAILED (retry attempted but audio_missing
    re-detected)."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _make_manifest(base / "ratings_manifest.tsv", ["v1"])
        (base / "rated_ready.flag").write_text("ready\n")
        _preload_state(base, {
            "state": "FAILED",
            "last_transition_utc": "2026-08-29T12:00:00Z",
            "manifest_hash": None,
            "checkpoint_path": None,
            "failed_stage": "training/audio_missing",
            "training_result_path": None,
        })
        h = _make_harness(base)
        state = h.scan_and_advance()
        assert state == HState.FAILED, state
        assert h.persisted.failed_stage == "training/audio_missing"


# (f) — idempotent-on-repeat-flag with same content hash
def test_idempotent_repeat_scan_writes_bookkeeping_row_only():
    """Second scan after TRAINED with an unchanged manifest writes ONE
    noop bookkeeping row and does not fire training. Complement of
    test_content_hash_gate_prevents_redundant_training with a stricter
    invariant on the transitions log."""
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        vids = ["v1", "v2"]
        _make_manifest(base / "ratings_manifest.tsv", vids)
        for v in vids:
            _write_clip(base / "clips", v)
        (base / "rated_ready.flag").write_text("ready\n")
        h = _make_harness(base)
        h.scan_and_advance()
        lines_before = (base / "state" / "transitions.jsonl").read_text().splitlines()
        # Second scan: should add exactly one noop row.
        h2 = _make_harness(base)
        state = h2.scan_and_advance()
        assert state == HState.TRAINED, state
        lines_after = (base / "state" / "transitions.jsonl").read_text().splitlines()
        added = lines_after[len(lines_before):]
        assert len(added) == 1, added
        assert '"noop":true' in added[0], added[0]


# (g) — SB dry-run byte-determinism × 2
def test_sb_dry_run_byte_determinism_x2():
    """Run scripts/ear/sb_dry_run.py twice against two fresh temp-dir
    outputs; assert SHA-256 equality on sb_dry_run_verdict.json.
    (Wall time bound: --epochs 20 keeps this under ~2 min on the
    reference machine.)"""
    script = ROOT / "scripts" / "ear" / "sb_dry_run.py"
    assert script.is_file(), script
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        out1 = base / "run1"
        out2 = base / "run2"
        env = dict(os.environ, PYTHONPATH=str(ROOT))
        # Both invocations pass a fixed tempdir; determinism proves the
        # verdict does not carry any tempdir-dependent identity.
        subprocess.run(
            [sys.executable, str(script),
             "--out-dir", str(out1), "--epochs", "20"],
            check=True, env=env, cwd=str(ROOT),
            timeout=1200,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [sys.executable, str(script),
             "--out-dir", str(out2), "--epochs", "20"],
            check=True, env=env, cwd=str(ROOT),
            timeout=1200,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        h1 = hashlib.sha256((out1 / "sb_dry_run_verdict.json").read_bytes()).hexdigest()
        h2 = hashlib.sha256((out2 / "sb_dry_run_verdict.json").read_bytes()).hexdigest()
        assert h1 == h2, (h1, h2)


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
    # Cycle 31 branch C additions
    test_ratings_manifest_content_hash_change_refires_training,
    test_sb1_computable_from_synthetic_dry_run,
    test_sb2_computable_from_synthetic_dry_run,
    test_sb3_computable_from_synthetic_dry_run,
    test_mock_egress_unblock_probe_fires_full_state_chain,
    test_zero_live_network_ast_grep_covers_sb_dry_run,
    test_resumable_from_failed_training_loop,
    test_resumable_from_failed_training_audio_missing_when_audio_returns,
    test_resumable_from_failed_training_audio_missing_stays_failed_when_still_missing,
    test_idempotent_repeat_scan_writes_bookkeeping_row_only,
    test_sb_dry_run_byte_determinism_x2,
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
