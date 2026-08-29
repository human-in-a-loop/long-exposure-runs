#!/usr/bin/python3
"""Sweep chosen_songs_full.json and write early_exit stubs for unstarted/incomplete songs.

Rubric §7(2): SILENT SONG DROPS ARE FORBIDDEN. Every song in chosen_songs_full.json must
have a stage_manifest.json on disk — either a real one written by run_full_corpus.py or an
early_exit stub carrying the reason.

A song is CONSIDERED COMPLETE if per_song/<band>/<song_index>/stage_manifest.json exists AND
contains both run1_shas and run2_shas keys with non-empty dicts AND status=="complete".

For any song NOT complete, this script writes a stub:
  {"early_exit": "cycle_wall_clock_exceeded", "canonical_index": <i>, "band": <b>, ...}

Idempotent: never overwrites an existing complete manifest; only writes stubs where missing.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"wrong interpreter: {sys.executable}"

ROOT = Path(__file__).resolve().parent.parent.parent
BASE = ROOT / "data" / "recreate_v0_full_corpus"
CHOSEN = BASE / "chosen_songs_full.json"
PER_SONG = BASE / "per_song"


def is_complete(manifest_path: Path) -> bool:
    if not manifest_path.exists():
        return False
    try:
        m = json.loads(manifest_path.read_text())
    except Exception:
        return False
    if m.get("status") != "complete":
        return False
    if not m.get("run1_shas") or not m.get("run2_shas"):
        return False
    return True


def main() -> int:
    chosen = json.loads(CHOSEN.read_text())
    songs = chosen["songs"]

    stubs_written = 0
    already_complete = 0
    already_stub = 0

    for i, song in enumerate(songs):
        band = song["band"]
        song_dir = PER_SONG / str(band) / f"song_{i:02d}"
        manifest_path = song_dir / "stage_manifest.json"

        if is_complete(manifest_path):
            already_complete += 1
            continue

        # Check if there's an existing stub or partial run — treat any non-complete manifest
        # as needing a stub overwrite unless it's already a stub.
        if manifest_path.exists():
            try:
                existing = json.loads(manifest_path.read_text())
                if existing.get("early_exit"):
                    already_stub += 1
                    continue
            except Exception:
                pass

        song_dir.mkdir(parents=True, exist_ok=True)
        stub = {
            "canonical_index": i,
            "band": band,
            "relpath": song["relpath"],
            "sha256": song.get("sha256", ""),
            "status": "early_exit",
            "early_exit": "cycle_wall_clock_exceeded",
            "reason": "session-2 cycle wall-clock exceeded before this song could be processed",
            "stub_written_at": datetime.now(timezone.utc).isoformat(),
            "run1_shas": {},
            "run2_shas": {},
        }
        manifest_path.write_text(json.dumps(stub, indent=2, sort_keys=True))
        stubs_written += 1

    summary = {
        "total_songs": len(songs),
        "already_complete": already_complete,
        "already_stub": already_stub,
        "stubs_written": stubs_written,
        "swept_at": datetime.now(timezone.utc).isoformat(),
    }
    (BASE / "sweep_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
