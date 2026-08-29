"""Per-song feature extractor for the 43 rated songs.

Uses c6 scripts.ear.features primitives (READ-ONLY import — no mutation
of the c6 pipeline; verified by anchor_preservation.json). Extracts
PANNs Cnn14 2048-D penultimate + M-HEUR-1 4-D mess-scale = 2052-D per
song.

Chunker semantics: the M-INGEST-1 30 s / 5 s-overlap chunker is applied
in-memory (equivalent to writing clips to disk then re-loading — same
sample boundaries, same anchored-tail rule). Anchored-tail debias weight
`(clip_len - overlap_with_prev) / 30` used for song aggregation.

Content-hash cache: data/ear_v0/per_song_features/<song_sha256>.npy
carries the 2052-D float32 vector. Manifest at
data/ear_v0/feature_cache_manifest.json records
(song_sha256, feature_version, feature_hash, artist, band).

Non-factor sidecar isolation: no import of sidecar_nonfactor anywhere.
"""
# created: 2026-08-29T07:23:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: M-EAR-1/real-label-training-v0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import librosa

# c6 primitives — READ-ONLY.
from scripts.ear.features import FEATURE_VERSION as C6_FEATURE_VERSION
from scripts.classifier.tagger import MODEL_SR as PANNS_SR

from scripts.ear_v0.ingest_ratings import Song, discover_songs

FEATURE_VERSION = "ear-v0-real-label-v1"  # narrows c6 version + audio-mode pin
FEAT_DIM = 2052  # 2048 PANNs + 4 heuristic
CLIP_S = 30.0
OVERLAP_S = 5.0
CACHE_DIR = Path("data/ear_v0/per_song_features")
MANIFEST_PATH = Path("data/ear_v0/feature_cache_manifest.json")


def _load_mp3_mono(path: Path, sr: int) -> np.ndarray:
    """Deterministic mono load at target sr (librosa uses soxr internally)."""
    y, _ = librosa.load(str(path), sr=sr, mono=True)
    return y.astype(np.float32)


def _chunk_indices(n_samples: int, sr: int) -> list[tuple[int, int]]:
    """M-INGEST-1 chunker: 30 s clips with 5 s overlap, anchored-tail last."""
    clip_n = int(round(CLIP_S * sr))
    hop_n = int(round((CLIP_S - OVERLAP_S) * sr))
    if n_samples <= clip_n:
        return [(0, n_samples)]
    starts: list[int] = []
    s = 0
    while s + clip_n <= n_samples:
        starts.append(s)
        s += hop_n
    # Tail-anchored: if last clip doesn't reach the end, add one that does.
    if starts[-1] + clip_n < n_samples:
        starts.append(max(0, n_samples - clip_n))
    return [(s, s + clip_n) for s in starts]


def _panns_embed(y: np.ndarray, sr: int) -> np.ndarray:
    from scripts.classifier.tagger import Tagger
    global _TAGGER  # noqa: PLW0603
    try:
        _TAGGER
    except NameError:
        _TAGGER = Tagger()
    emb = _TAGGER.embed(y, sr)
    return np.asarray(emb, dtype=np.float32).reshape(-1)


def _heur_vec(y22: np.ndarray, sr22: int) -> np.ndarray:
    from scripts.heuristics.melody import melody_quality
    from scripts.heuristics.timbre import timbre_quality
    from scripts.heuristics.form import form_quality
    from scripts.heuristics.dynamics import dynamics_quality
    out = np.zeros(4, dtype=np.float32)
    for i, fn in enumerate(
        [melody_quality, timbre_quality, form_quality, dynamics_quality]
    ):
        try:
            r = fn(y22, sr22)
            m = getattr(r, "mess_scale", None)
            if m is not None and np.isfinite(m):
                out[i] = float(m)
        except Exception:
            pass  # 0.0 stays
    return out


def _anchored_tail_weights(clip_bounds: list[tuple[int, int]], sr: int) -> np.ndarray:
    """Anchored-tail debias: weight_i = (len_i - overlap_with_prev) / clip_len."""
    if len(clip_bounds) == 1:
        return np.array([1.0], dtype=np.float32)
    clip_n = int(round(CLIP_S * sr))
    ws = np.zeros(len(clip_bounds), dtype=np.float32)
    ws[0] = 1.0
    for i in range(1, len(clip_bounds)):
        prev_end = clip_bounds[i - 1][1]
        this_start = clip_bounds[i][0]
        overlap = max(0, prev_end - this_start)
        ws[i] = max(0.0, (clip_n - overlap) / float(clip_n))
    return ws


def extract_song(song: Song) -> np.ndarray:
    """Return (2052,) float32 song-level feature vector."""
    cache = CACHE_DIR / f"{song.sha256}.npy"
    if cache.exists():
        v = np.load(cache).astype(np.float32).reshape(-1)
        if v.shape[0] == FEAT_DIM:
            return v

    # Load at both sample rates deterministically.
    y32 = _load_mp3_mono(song.path, PANNS_SR)
    y22 = _load_mp3_mono(song.path, 22050)
    bounds32 = _chunk_indices(y32.size, PANNS_SR)
    ws = _anchored_tail_weights(bounds32, PANNS_SR)
    ws /= float(ws.sum())

    # PANNs per clip.
    panns_song = np.zeros(2048, dtype=np.float64)
    for i, (a, b) in enumerate(bounds32):
        panns_song += float(ws[i]) * _panns_embed(y32[a:b], PANNS_SR).astype(np.float64)
    panns_song = panns_song.astype(np.float32)

    # Heuristics per clip on 22050 timeline (same bounds proportionally).
    bounds22 = _chunk_indices(y22.size, 22050)
    ws22 = _anchored_tail_weights(bounds22, 22050)
    ws22 /= float(ws22.sum())
    heur_song = np.zeros(4, dtype=np.float64)
    for i, (a, b) in enumerate(bounds22):
        heur_song += float(ws22[i]) * _heur_vec(y22[a:b], 22050).astype(np.float64)
    heur_song = heur_song.astype(np.float32)

    v = np.concatenate([panns_song, heur_song]).astype(np.float32)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(cache, v)
    return v


def build_manifest(songs: list[Song]) -> dict:
    """Build the feature_cache_manifest.json record."""
    entries = []
    for s in songs:
        cache = CACHE_DIR / f"{s.sha256}.npy"
        v = np.load(cache).astype(np.float32).reshape(-1)
        # canonical feature_hash: SHA-256 of the raw float32 bytes.
        fhash = hashlib.sha256(v.tobytes()).hexdigest()
        entries.append({
            "song_sha256": s.sha256,
            "feature_version": FEATURE_VERSION,
            "c6_feature_version": C6_FEATURE_VERSION,
            "feature_hash": fhash,
            "artist": s.artist,
            "band": s.band,
            "video_id": s.video_id,
            "playlist_id": s.playlist_id,
            "n_dims": int(v.shape[0]),
        })
    entries.sort(key=lambda e: (e["band"], e["song_sha256"]))
    return {
        "feature_version": FEATURE_VERSION,
        "c6_feature_version": C6_FEATURE_VERSION,
        "n_songs": len(entries),
        "entries": entries,
    }


def extract_all(songs: list[Song]) -> None:
    for i, s in enumerate(songs, 1):
        print(f"[{i:2d}/{len(songs)}] band={s.band} {s.sha256[:16]} {s.artist}",
              flush=True)
        extract_song(s)


if __name__ == "__main__":
    songs = discover_songs(Path("."))
    extract_all(songs)
    manifest = build_manifest(songs)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(f"manifest written: {MANIFEST_PATH}")
