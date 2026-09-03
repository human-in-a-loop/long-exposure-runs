#!/usr/bin/env -S /usr/bin/python3
"""Tests for scripts.sound_match.replay_proof.

Cases:
    1. tempfile dir isolation (2 different dirs used)
    2. SHA-comparison logic: matching SHAs -> HOLDS
    3. verdict enum shape (only HOLDS or FAILS)
    4. honest-failure path: mock non-deterministic render -> FAILS + SystemExit
    5. env_pin_sha256 present and stable across runs
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.sound_match import replay_proof as rp  # noqa: E402


def _make_dummy_midi(tmp_path: Path) -> Path:
    """Write a minimal MIDI-like file (any bytes; replay_fn is mocked)."""
    p = tmp_path / "bass.mid"
    p.write_bytes(b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x01\xe0MTrk\x00\x00\x00\x04\x00\xff/\x00")
    return p


def test_holds_when_shas_equal(tmp_path):
    """Deterministic mock render -> HOLDS."""
    profile = {"profile_id": "prof-xyz", "family": "sf2", "identity": {}, "params": {}}
    midi = _make_dummy_midi(tmp_path)
    call_state = {"n": 0}

    def mock_replay(profile, midi_path, out_wav):
        Path(out_wav).write_bytes(b"identical-render-bytes")
        call_state["n"] += 1
        return hashlib.sha256(b"identical-render-bytes").hexdigest()

    out_json = tmp_path / "report.json"
    report = rp.prove_replay(profile, midi, out_json=out_json, replay_fn=mock_replay)
    assert report["verdict"] == "REPLAY_PROOF_HOLDS"
    assert report["run1_sha256"] == report["run2_sha256"]
    assert call_state["n"] == 2  # called twice
    # Persisted JSON matches
    persisted = json.loads(out_json.read_text())
    assert persisted["verdict"] == "REPLAY_PROOF_HOLDS"


def test_tempdir_isolation(tmp_path):
    """Two runs use two different tempfile.mkdtemp() dirs."""
    profile = {"profile_id": "p", "family": "sf2", "identity": {}, "params": {}}
    midi = _make_dummy_midi(tmp_path)
    dirs: list[str] = []

    def mock_replay(profile, midi_path, out_wav):
        dirs.append(str(Path(out_wav).parent))
        Path(out_wav).write_bytes(b"x")
        return hashlib.sha256(b"x").hexdigest()

    report = rp.prove_replay(profile, midi, replay_fn=mock_replay)
    assert len(dirs) == 2
    assert dirs[0] != dirs[1]
    assert report["tempdir_run1"] != report["tempdir_run2"]


def test_verdict_enum_shape(tmp_path):
    """Verdict must be exactly HOLDS or FAILS."""
    profile = {"profile_id": "p", "family": "sf2", "identity": {}, "params": {}}
    midi = _make_dummy_midi(tmp_path)

    def mock_replay(profile, midi_path, out_wav):
        Path(out_wav).write_bytes(b"a")
        return hashlib.sha256(b"a").hexdigest()

    report = rp.prove_replay(profile, midi, replay_fn=mock_replay)
    assert report["verdict"] in ("REPLAY_PROOF_HOLDS", "REPLAY_PROOF_FAILS")


def test_honest_failure_path_raises(tmp_path):
    """Non-deterministic render -> FAILS + SystemExit per FD-1."""
    profile = {"profile_id": "p", "family": "sf2", "identity": {}, "params": {}}
    midi = _make_dummy_midi(tmp_path)
    counter = {"i": 0}

    def mock_replay(profile, midi_path, out_wav):
        counter["i"] += 1
        Path(out_wav).write_bytes(f"drift-{counter['i']}".encode())
        return hashlib.sha256(f"drift-{counter['i']}".encode()).hexdigest()

    out_json = tmp_path / "fail.json"
    try:
        rp.prove_replay(profile, midi, out_json=out_json, replay_fn=mock_replay)
        raise AssertionError("expected SystemExit")
    except SystemExit as se:
        assert "REPLAY_PROOF_FAILS" in str(se)
    # Report still persisted before raise
    persisted = json.loads(out_json.read_text())
    assert persisted["verdict"] == "REPLAY_PROOF_FAILS"
    assert persisted["run1_sha256"] != persisted["run2_sha256"]


def test_env_pin_sha_stable(tmp_path):
    """env_pin_sha256 is a stable function of the env pins."""
    a = rp._env_pin_sha()
    b = rp._env_pin_sha()
    assert a == b
    assert len(a) == 64


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    fails = 0
    for t in tests:
        try:
            if "tmp_path" in t.__code__.co_varnames[:t.__code__.co_argcount]:
                with tempfile.TemporaryDirectory() as td:
                    t(Path(td))
            else:
                t()
            print(f"PASS {t.__name__}")
        except Exception:
            fails += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    sys.exit(0 if fails == 0 else 1)
