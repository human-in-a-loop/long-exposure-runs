#!/usr/bin/python3
"""Per-clip PANNs Cnn14 (2048-D) + M-HEUR-1 (4-D) features for v2.

Reads data/ear_v2/resample_manifest.json (produced by
scripts.ear_v2.resample_corpus). For each clip, decodes the parent
MP3 twice at deterministic sample rates (32000 Hz for PANNs, 22050 Hz
for heuristics), slices the sample range, and caches a 2052-D float32
vector at data/ear_v2/features_v2/<clip_id>.npy.

Cache is content-addressed by clip_id (song_sha256 + clip_idx). Second
run is skip-if-hash-matches. Anchored-tail per-song aggregation is NOT
applied here — each clip is an independent training sample.

READ-ONLY imports of c6 primitives (scripts.classifier.tagger.Tagger,
scripts.heuristics.{melody,timbre,form,dynamics}). No import of
c23 model_v2_* or c25 feature_subset_adapter/stability_audit_v3_*.
"""
# created: 2026-08-29T12:06:00Z  cycle: 39  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2
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

FEATURE_VERSION = "ear-v2-per-clip-v1"
FEAT_DIM = 2052
PANNS_DIM = 2048
HEUR_DIM = 4
CACHE_DIR = Path("data/ear_v2/features_v2")
MANIFEST_PATH = Path("data/ear_v2/feature_cache_manifest_v2.json")
RESAMPLE_MANIFEST = Path("data/ear_v2/resample_manifest.json")


def _load_mp3_mono(path: Path, sr: int) -> np.ndarray:
    """Deterministic librosa mp3 load (soxr internal)."""
    import librosa
    y, _ = librosa.load(str(path), sr=sr, mono=True)
    return y.astype(np.float32)


def _panns_embed(y: np.ndarray, sr: int) -> np.ndarray:
    from scripts.classifier.tagger import Tagger
    global _TAGGER  # noqa: PLW0603
    try:
        _TAGGER  # type: ignore[used-before-assignment]
    except NameError:
        _TAGGER = Tagger()
    emb = _TAGGER.embed(y, sr)
    return np.asarray(emb, dtype=np.float32).reshape(-1)


def _heur_vec(y22: np.ndarray, sr22: int) -> np.ndarray:
    from scripts.heuristics.melody import melody_quality
    from scripts.heuristics.timbre import timbre_quality
    from scripts.heuristics.form import form_quality
    from scripts.heuristics.dynamics import dynamics_quality
    out = np.zeros(HEUR_DIM, dtype=np.float32)
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


def extract_clip(clip: dict, y32: np.ndarray, y22: np.ndarray) -> np.ndarray:
    """Slice a clip out of pre-loaded song audio and produce a 2052-D vector."""
    t0, t1 = float(clip["start_s"]), float(clip["end_s"])
    a32, b32 = int(round(t0 * 32000)), int(round(t1 * 32000))
    a22, b22 = int(round(t0 * 22050)), int(round(t1 * 22050))
    a32 = max(0, min(a32, y32.size))
    b32 = max(a32, min(b32, y32.size))
    a22 = max(0, min(a22, y22.size))
    b22 = max(a22, min(b22, y22.size))
    panns = _panns_embed(y32[a32:b32], 32000)
    heur = _heur_vec(y22[a22:b22], 22050)
    vec = np.zeros(FEAT_DIM, dtype=np.float32)
    vec[:PANNS_DIM] = panns[:PANNS_DIM]
    vec[PANNS_DIM:] = heur[:HEUR_DIM]
    return vec


def extract_all() -> dict:
    """Extract per-clip features for every clip in the resample manifest."""
    manifest = json.loads(RESAMPLE_MANIFEST.read_text())
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for song_rec in manifest["per_song"]:
        clips = song_rec["clips"]
        cache_hits = all(
            (CACHE_DIR / f"{c['clip_id']}.npy").exists() for c in clips
        )
        y32 = y22 = None
        for c in clips:
            cache_p = CACHE_DIR / f"{c['clip_id']}.npy"
            if cache_p.exists():
                v = np.load(cache_p).astype(np.float32).reshape(-1)
                if v.shape[0] != FEAT_DIM:
                    cache_p.unlink()
                    v = None
                else:
                    entries.append(_entry(c, v, cache_p))
                    continue
            if y32 is None:
                y32 = _load_mp3_mono(Path(song_rec["path"]), 32000)
                y22 = _load_mp3_mono(Path(song_rec["path"]), 22050)
            v = extract_clip(c, y32, y22)
            np.save(cache_p, v, allow_pickle=False)
            entries.append(_entry(c, v, cache_p))
        del y32, y22
        _ = cache_hits
    entries.sort(key=lambda e: (e["band"], e["song_sha256"], e["clip_idx"]))
    combined = hashlib.sha256(
        json.dumps(entries, sort_keys=True).encode()
    ).hexdigest()
    out = {
        "feature_version": FEATURE_VERSION,
        "feat_dim": FEAT_DIM,
        "cache_root": str(CACHE_DIR),
        "n_clips": len(entries),
        "combined_manifest_sha256": combined,
        "entries": entries,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(out, indent=2, sort_keys=True))
    return out


def _entry(clip: dict, v: np.ndarray, cache_p: Path) -> dict:
    feature_hash = hashlib.sha256(v.tobytes()).hexdigest()
    cache_sha = hashlib.sha256(cache_p.read_bytes()).hexdigest()
    return {
        "clip_id": clip["clip_id"],
        "clip_idx": int(clip["clip_idx"]),
        "song_sha256": clip["song_sha256"],
        "band": int(clip["band"]),
        "artist": clip["artist"],
        "playlist_id": clip["playlist_id"],
        "start_s": float(clip["start_s"]),
        "end_s": float(clip["end_s"]),
        "tail_anchored": bool(clip["tail_anchored"]),
        "feature_hash": feature_hash,
        "cache_file_sha256": cache_sha,
        "feature_version": FEATURE_VERSION,
    }


def load_matrix() -> tuple[np.ndarray, np.ndarray, list[dict]]:
    """Load the full (N_clips, 2052) X matrix + band labels y + entries."""
    manifest = json.loads(MANIFEST_PATH.read_text())
    entries = sorted(
        manifest["entries"],
        key=lambda e: (e["band"], e["song_sha256"], e["clip_idx"]),
    )
    X = np.zeros((len(entries), FEAT_DIM), dtype=np.float32)
    y = np.zeros(len(entries), dtype=np.int64)
    for i, e in enumerate(entries):
        p = CACHE_DIR / f"{e['clip_id']}.npy"
        X[i] = np.load(p).astype(np.float32).reshape(-1)
        y[i] = int(e["band"])
    return X, y, entries


if __name__ == "__main__":
    out = extract_all()
    print(json.dumps({
        "n_clips": out["n_clips"],
        "combined_manifest_sha256_prefix": out["combined_manifest_sha256"][:16],
    }, indent=2))
