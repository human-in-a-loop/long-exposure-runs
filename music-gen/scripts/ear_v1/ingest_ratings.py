#!/usr/bin/python3
"""Ingest the operator's rated corpus (43 songs) — c38 v1 re-anchor.

Delegates to scripts.ear_v0.ingest_ratings which parses the filename
convention (NNN__<video_id>__<title>.mp3) and reads
corpus/ratings/ratings_manifest.tsv for playlist/artist metadata.

Deterministic sort key: (band, sha256). No PRNG. No sidecar_nonfactor
import.
"""
# created: 2026-08-29T11:05:00Z  cycle: 38  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0)  milestone: M-EAR-1/real-label-training-v1
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

from pathlib import Path
from scripts.ear_v0.ingest_ratings import (
    Song, BANDS, discover_songs, parse_artist, parse_filename,
)

__all__ = ["Song", "BANDS", "discover_songs", "parse_artist", "parse_filename"]


if __name__ == "__main__":
    songs = discover_songs(Path("."))
    print(f"[v1] {len(songs)} songs discovered")
    for b in BANDS:
        print(f"  band {b}: {sum(1 for s in songs if s.band == b)}")
