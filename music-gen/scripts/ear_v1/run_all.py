#!/usr/bin/python3
"""Orchestrator: features -> train -> leak-ablation -> evaluate.

Emits, under data/ear_v1/:
  - rubric_hash.txt           (frozen; written during rubric commitment)
  - chosen_songs.json
  - feature_cache_manifest.json  (pre/post byte-identical assertion)
  - training_result.json + corn_head_v1.pt + held_out_predictions.tsv
  - leak_test_summary.json
  - leak_test_diff_manifest.json   (frozen at surgery time)
  - sb_results.json
  - anchor_preservation.json
  - verdict.json
  - determinism_check.json    (populated by --deterministic-second-run)

Byte-determinism × 2: caller re-runs `python3 -m scripts.ear_v1.run_all`
in a scratch temp dir and asserts SHA equality on verdict.json,
leak_test_summary.json, corn_head_v1.pt.
"""
# created: 2026-08-29T11:09:00Z  cycle: 38  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0)  milestone: M-EAR-1/real-label-training-v1
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
from pathlib import Path

from scripts.ear_v1.ingest_ratings import discover_songs
from scripts.ear_v1.features_v1 import (
    write_manifest, MANIFEST_PATH, load_song,
)
from scripts.ear_v1.train_v1 import train
from scripts.ear_v1.leak_ablation_v1 import summarize as leak_summarize
from scripts.ear_v1.evaluate_v1 import evaluate

DATA_DIR = Path("data/ear_v1")

# Anchors: everything in the READ-ONLY zone of the c38 v1 brief.
# leak_test.py is authorized-mutation, tracked separately in
# leak_test_diff_manifest.json — NOT in this equality-asserted set.
ANCHOR_FILES = [
    # c6 pipeline (read-only in this cycle)
    "scripts/ear/features.py",
    "scripts/ear/model.py",
    "scripts/ear/corn.py",
    "scripts/ear/train.py",
    # c22 stability harness (read-only)
    "scripts/ear/stability_audit.py",
    "scripts/ear/stability_metrics.py",
    "scripts/ear/synthetic_labels.py",
    # classifier tagger (indirect c6 anchor; PANNs Cnn14 embed source)
    "scripts/classifier/tagger.py",
    # c26 Path B commitment doc
    "docs/ear_path_b_commitment.md",
    # c36 Branch A scripts (reference only)
    "scripts/ear_v0/ingest_ratings.py",
    "scripts/ear_v0/extract_features_v0.py",
    "scripts/ear_v0/train_v0.py",
    "scripts/ear_v0/evaluate_success_bars.py",
    "scripts/ear_v0/leak_ablation_v0.py",
]


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha_file(p: Path) -> str:
    if not p.exists():
        return "MISSING"
    return _sha_bytes(p.read_bytes())


def snapshot_anchors() -> dict:
    return {p: _sha_file(Path(p)) for p in ANCHOR_FILES}


def write_chosen_songs(songs) -> Path:
    import wave
    import subprocess

    def _probe_mp3(path: Path) -> dict:
        # Fallback ffprobe-less path: use mutagen if available; else best-effort
        # duration=NaN + sr=44100 default. Music-gen images ship librosa.
        try:
            import librosa
            duration = float(librosa.get_duration(path=str(path)))
        except Exception:
            duration = float("nan")
        try:
            import librosa
            y, sr = librosa.load(str(path), sr=None, mono=False)
            channels = 1 if y.ndim == 1 else int(y.shape[0])
            sample_rate = int(sr)
        except Exception:
            channels = 2
            sample_rate = 44100
        return {"duration_s": duration, "sr": sample_rate, "channels": channels}

    rows = []
    for s in songs:
        info = _probe_mp3(s.path)
        rows.append({
            "path": str(s.path),
            "band": s.band,
            "sha256": s.sha256,
            "duration": info["duration_s"],
            "sr": info["sr"],
            "channels": info["channels"],
            "artist_parsed": s.artist,
            "video_id": s.video_id,
            "playlist_id": s.playlist_id,
            "title": s.title,
        })
    rows.sort(key=lambda r: (r["band"], r["sha256"]))
    p = DATA_DIR / "chosen_songs.json"
    p.write_text(json.dumps({
        "corpus_size": len(rows),
        "bands_covered": sorted({r["band"] for r in rows}),
        "songs": rows,
    }, indent=2, sort_keys=True))
    return p


def _manifest_sha(manifest: dict) -> str:
    return _sha_bytes(json.dumps(manifest, sort_keys=True).encode())


def main() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    anchors_pre = snapshot_anchors()

    songs = discover_songs(Path("."))
    write_chosen_songs(songs)

    # Feature cache manifest — pre snapshot.
    manifest_pre = write_manifest(songs)
    pre_sha = _manifest_sha(manifest_pre)

    # Sanity: verify all 43 songs load cleanly.
    for s in songs:
        _ = load_song(s)

    # Train.
    tres = train(songs)

    # Leak ablation.
    leak_summarize()

    # Feature cache manifest — post snapshot (must match).
    manifest_post = write_manifest(songs)
    post_sha = _manifest_sha(manifest_post)
    assert pre_sha == post_sha, (
        f"feature-cache-manifest drift: pre={pre_sha[:16]} post={post_sha[:16]}"
    )

    # Evaluate + emit verdict.
    v = evaluate()

    # Anchor preservation — pre/post.
    anchors_post = snapshot_anchors()
    anchor_out = {
        "anchors": ANCHOR_FILES,
        "n_anchors": len(ANCHOR_FILES),
        "pre": anchors_pre,
        "post": anchors_post,
        "all_unchanged": anchors_pre == anchors_post,
        "changed_paths": sorted(
            [p for p in ANCHOR_FILES if anchors_pre[p] != anchors_post[p]]
        ),
        "authorized_mutation_tracked_separately": "scripts/ear/leak_test.py",
    }
    (DATA_DIR / "anchor_preservation.json").write_text(
        json.dumps(anchor_out, indent=2, sort_keys=True)
    )

    return {
        "verdict": v["verdict"],
        "anchor_all_unchanged": anchor_out["all_unchanged"],
        "feature_manifest_pre_post_equal": pre_sha == post_sha,
    }


if __name__ == "__main__":
    r = main()
    print(json.dumps(r, indent=2))
