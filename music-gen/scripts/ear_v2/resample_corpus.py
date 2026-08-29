#!/usr/bin/python3
"""Anchored-tail per-song resampling of the 43-song rated corpus.

Emits data/ear_v2/resample_manifest.json with per-song clip bounds.
Deterministic — filename-sorted per band by (band, sha256); clip start
formula pinned in the c39 clone-1 rubric §"Resample protocol".

Duration source: librosa.get_duration (best-effort; falls back to
audioread on decode failure).
"""
# created: 2026-08-29T12:05:00Z  cycle: 39  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import json
import math
from pathlib import Path

from scripts.ear_v0.ingest_ratings import Song, discover_songs

CLIP_S = 30.0
HOP_S = 25.0  # 5 s overlap for standard-case starts
MAX_CLIPS = 6
MIN_DURATION = 30.0
OUT_PATH = Path("data/ear_v2/resample_manifest.json")


def _duration_seconds(path: Path) -> float:
    """Deterministic duration via librosa; fallback via audioread."""
    import librosa
    try:
        return float(librosa.get_duration(path=str(path)))
    except Exception:
        try:
            import audioread
            with audioread.audio_open(str(path)) as af:
                return float(af.duration)
        except Exception:
            return float("nan")


def clip_bounds(duration_s: float) -> list[tuple[float, float]]:
    """Return list of (start, end) tuples per rubric §"Resample protocol"."""
    D = float(duration_s)
    if not math.isfinite(D) or D < MIN_DURATION:
        return []
    # Hop-strided starts while start + CLIP_S <= D.
    starts: list[float] = []
    s = 0.0
    while s + CLIP_S <= D + 1e-6:
        starts.append(round(s, 6))
        s += HOP_S
    # Tail-anchored final clip (end = D). Skip if already present.
    tail_start = round(D - CLIP_S, 6)
    if not starts or starts[-1] < tail_start - 1e-6:
        starts.append(tail_start)
    # Cap at 6 clips: keep first 5 + tail-anchored final.
    if len(starts) > MAX_CLIPS:
        starts = starts[: MAX_CLIPS - 1] + [tail_start]
    return [(s0, round(s0 + CLIP_S, 6)) for s0 in starts]


def build_manifest(songs: list[Song]) -> dict:
    """Build resample manifest for `songs`, ordered (band, sha256)."""
    songs = sorted(songs, key=lambda s: (s.band, s.sha256))
    per_song_records = []
    skipped = []
    total_clips = 0
    for s in songs:
        D = _duration_seconds(s.path)
        bounds = clip_bounds(D)
        if not bounds:
            skipped.append({
                "song_sha256": s.sha256,
                "band": s.band,
                "reason": (
                    "duration_below_min_30s" if D < MIN_DURATION else
                    "duration_probe_failed"
                ),
                "duration_s": None if not math.isfinite(D) else float(D),
                "path": str(s.path),
            })
            continue
        clips = []
        for idx, (t0, t1) in enumerate(bounds):
            clips.append({
                "clip_idx": idx,
                "clip_id": f"{s.sha256}__{idx:02d}",
                "start_s": float(t0),
                "end_s": float(t1),
                "duration_s": float(round(t1 - t0, 6)),
                "tail_anchored": bool(idx == len(bounds) - 1 and len(bounds) > 1),
                "band": int(s.band),
                "artist": s.artist,
                "playlist_id": s.playlist_id,
                "video_id": s.video_id,
                "song_sha256": s.sha256,
            })
        per_song_records.append({
            "song_sha256": s.sha256,
            "band": int(s.band),
            "artist": s.artist,
            "playlist_id": s.playlist_id,
            "video_id": s.video_id,
            "duration_s": float(D),
            "path": str(s.path),
            "n_clips": len(clips),
            "clips": clips,
        })
        total_clips += len(clips)

    manifest = {
        "milestone": "M-EAR-1/real-label-training-v2",
        "cycle": 39,
        "resample_protocol_version": "anchored_tail_per_song_v1",
        "clip_seconds": CLIP_S,
        "hop_seconds": HOP_S,
        "max_clips_per_song": MAX_CLIPS,
        "min_duration_seconds": MIN_DURATION,
        "n_songs_input": len(songs),
        "n_songs_kept": len(per_song_records),
        "n_songs_skipped": len(skipped),
        "n_clips_total": total_clips,
        "per_song": per_song_records,
        "skipped": skipped,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


if __name__ == "__main__":
    songs = discover_songs(Path("."))
    m = build_manifest(songs)
    print(json.dumps({
        "n_songs_kept": m["n_songs_kept"],
        "n_songs_skipped": m["n_songs_skipped"],
        "n_clips_total": m["n_clips_total"],
    }, indent=2))
