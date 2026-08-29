#!/usr/bin/python3
"""Feature loader for M-EAR-1/real-label-training-v1 (c38 clone-0).

Uses c6 scripts.ear.features primitives (via the c36 v0 extractor's
per-song cache at data/ear_v0/per_song_features/<song_sha>.npy). Each
song is a 2052-D float32 vector — 2048 PANNs Cnn14 penultimate + 4
M-HEUR-1 mess-scale. Anchored-tail per-song aggregation preserved.

Feature-cache SHA-manifest at data/ear_v1/feature_cache_manifest.json
is asserted byte-identical pre/post the train+evaluate step by
run_all.py.
"""
# created: 2026-08-29T11:05:00Z  cycle: 38  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0)  milestone: M-EAR-1/real-label-training-v1
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import hashlib
import json
from pathlib import Path

import numpy as np

from scripts.ear.features import FEATURE_VERSION as C6_FEATURE_VERSION
from scripts.ear_v1.ingest_ratings import Song

FEAT_DIM = 2052
FEATURE_VERSION = "ear-v1-real-label-v1"  # cycle-38 v1 pin
CACHE_DIR = Path("data/ear_v0/per_song_features")  # c6/v0 anchored cache
MANIFEST_PATH = Path("data/ear_v1/feature_cache_manifest.json")


def load_song(song: Song) -> np.ndarray:
    """Return the (2052,) float32 feature vector for a song."""
    p = CACHE_DIR / f"{song.sha256}.npy"
    v = np.load(p).astype(np.float32).reshape(-1)
    if v.shape[0] != FEAT_DIM:
        raise ValueError(f"unexpected feat dim {v.shape[0]} != {FEAT_DIM}")
    return v


def load_matrix(songs: list[Song]) -> tuple[np.ndarray, np.ndarray]:
    X = np.zeros((len(songs), FEAT_DIM), dtype=np.float32)
    y = np.zeros(len(songs), dtype=np.int64)
    for i, s in enumerate(songs):
        X[i] = load_song(s)
        y[i] = s.band
    return X, y


def build_manifest(songs: list[Song]) -> dict:
    entries = []
    for s in songs:
        p = CACHE_DIR / f"{s.sha256}.npy"
        v = np.load(p).astype(np.float32).reshape(-1)
        feature_hash = hashlib.sha256(v.tobytes()).hexdigest()
        cache_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        entries.append({
            "song_sha256": s.sha256,
            "feature_version": FEATURE_VERSION,
            "c6_feature_version": C6_FEATURE_VERSION,
            "feature_hash": feature_hash,
            "cache_file_sha256": cache_hash,
            "artist": s.artist,
            "band": s.band,
            "video_id": s.video_id,
            "playlist_id": s.playlist_id,
            "n_dims": int(v.shape[0]),
        })
    entries.sort(key=lambda e: (e["band"], e["song_sha256"]))
    combined = hashlib.sha256(
        json.dumps(entries, sort_keys=True).encode()
    ).hexdigest()
    return {
        "feature_version": FEATURE_VERSION,
        "c6_feature_version": C6_FEATURE_VERSION,
        "cache_root": str(CACHE_DIR),
        "n_songs": len(entries),
        "combined_manifest_sha256": combined,
        "entries": entries,
    }


def write_manifest(songs: list[Song]) -> dict:
    manifest = build_manifest(songs)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True)
    )
    return manifest


if __name__ == "__main__":
    from scripts.ear_v1.ingest_ratings import discover_songs
    songs = discover_songs(Path("."))
    m = write_manifest(songs)
    print(f"[v1] wrote manifest with {m['n_songs']} songs; combined="
          f"{m['combined_manifest_sha256'][:16]}")
