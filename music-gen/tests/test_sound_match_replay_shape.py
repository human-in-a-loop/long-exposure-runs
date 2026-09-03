#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES
# ---
"""Replay dispatch-table shape (no binaries invoked)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.sound_match import replay  # noqa: E402


def test_dispatch_table_covers_expected_families():
    for fam in ("sf2", "sfz", "stem_sampled", "surge"):
        assert fam in replay._DISPATCH
    print("PASS test_dispatch_table_covers_expected_families")


def test_replay_rejects_unknown_family():
    profile = {"family": "banjo"}
    try:
        replay.replay(profile, Path("/dev/null"), Path("/tmp/x.wav"))
    except ValueError:
        print("PASS test_replay_rejects_unknown_family")
        return
    raise AssertionError("expected ValueError on family=banjo")


def test_replay_signature_shape():
    # Signature: replay(profile: Mapping, midi_path: Path, out_wav_path: Path) -> str
    import inspect
    sig = inspect.signature(replay.replay)
    params = list(sig.parameters)
    assert params == ["profile", "midi_path", "out_wav_path"], params
    print("PASS test_replay_signature_shape")


if __name__ == "__main__":
    test_dispatch_table_covers_expected_families()
    test_replay_rejects_unknown_family()
    test_replay_signature_shape()
    print("OK")
