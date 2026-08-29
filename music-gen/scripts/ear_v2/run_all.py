#!/usr/bin/python3
"""End-to-end orchestrator: resample -> features -> train -> evaluate.

Also snapshots 25+ anchor SHAs pre/post and writes anchor_preservation.json.
Byte-determinism × 2 protocol: caller re-runs this module and asserts
SHA-equal on training_result.json + corn_head_v2.pt + sb_v2_verdict.json.
"""
# created: 2026-08-29T12:09:00Z  cycle: 39  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
from pathlib import Path

from scripts.ear_v2.resample_corpus import build_manifest as build_resample
from scripts.ear_v2.extract_features_v2 import extract_all as extract_features
from scripts.ear_v2.train_v2 import train
from scripts.ear_v2.evaluate_sb_v2 import evaluate
from scripts.ear_v0.ingest_ratings import discover_songs

DATA_DIR = Path("data/ear_v2")

# 25+ anchor SHAs — READ-ONLY set. Any change here indicates an anchor
# preservation violation that must be surfaced in verdict.json.
ANCHOR_FILES = [
    # c6 chassis (7 files)
    "scripts/ear/features.py",
    "scripts/ear/model.py",
    "scripts/ear/corn.py",
    "scripts/ear/leak_test.py",  # post-c38-clone-0 F1 pooled-variance
    "scripts/classifier/tagger.py",
    "docs/ear_preparation_report.md",
    "data/ear/leak_test_summary.json",
    # c22 stability harness (3 files) + c22 report + c22 data
    "scripts/ear/synthetic_labels.py",
    "scripts/ear/stability_metrics.py",
    "scripts/ear/stability_audit.py",
    "docs/ear_stability_audit_report.md",
    "data/ear/stability_audit/stability_report.json",
    # c26 Path B doc (1 file)
    "docs/ear_path_b_commitment.md",
    # c38 clone-0 v1 artifact tree (12+ files)
    "scripts/ear_v1/__init__.py",
    "scripts/ear_v1/features_v1.py",
    "scripts/ear_v1/train_v1.py",
    "scripts/ear_v1/evaluate_v1.py",
    "scripts/ear_v1/leak_ablation_v1.py",
    "scripts/ear_v1/run_all.py",
    "scripts/ear_v1/ingest_ratings.py",
    "docs/ear_real_label_training_v1_report.md",
    "data/ear_v1/rubric_hash.txt",
    "data/ear_v1/verdict.json",
    "data/ear_v1/corn_head_v1.pt",
    "data/ear_v1/training_result.json",
    # c1 chunker
    "scripts/ingest/chunker.py",
    # ratings manifest (READ-ONLY per brief)
    "corpus/ratings/ratings_manifest.tsv",
]


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha_file(p: Path) -> str:
    if not p.exists():
        return "MISSING"
    return _sha_bytes(p.read_bytes())


def snapshot_anchors() -> dict:
    return {p: _sha_file(Path(p)) for p in ANCHOR_FILES}


def snapshot_feature_cache_manifest() -> str:
    """SHA of sorted-relpath concat manifest of the c6 feature cache."""
    root = Path("data/ear/features")
    if not root.exists():
        return "MISSING"
    items = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            items.append(f"{p.relative_to(root)}\t{_sha_file(p)}")
    return _sha_bytes("\n".join(items).encode())


def main() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    anchors_pre = snapshot_anchors()
    c6_cache_pre = snapshot_feature_cache_manifest()

    songs = discover_songs(Path("."))
    resample_m = build_resample(songs)
    features_m = extract_features()
    _ = train()
    v = evaluate()

    anchors_post = snapshot_anchors()
    c6_cache_post = snapshot_feature_cache_manifest()
    anchor_out = {
        "n_anchors": len(ANCHOR_FILES),
        "anchors": ANCHOR_FILES,
        "pre": anchors_pre,
        "post": anchors_post,
        "all_unchanged": anchors_pre == anchors_post,
        "changed_paths": sorted(
            [p for p in ANCHOR_FILES if anchors_pre[p] != anchors_post[p]]
        ),
        "c6_feature_cache_pre_sha": c6_cache_pre,
        "c6_feature_cache_post_sha": c6_cache_post,
        "c6_feature_cache_unchanged": c6_cache_pre == c6_cache_post,
    }
    (DATA_DIR / "anchor_preservation.json").write_text(
        json.dumps(anchor_out, indent=2, sort_keys=True)
    )
    return {
        "verdict": v["verdict"],
        "sb1_margin": v["sb1"]["margin"],
        "sb2_mean_tau": v["sb2"]["mean_tau"],
        "sb3_pass": v["sb3"]["pass"],
        "sb3_denominator": v["sb3"]["per_leak_type"]["artist"]["denominator_pairs"],
        "n_songs_kept": resample_m["n_songs_kept"],
        "n_clips_total": resample_m["n_clips_total"],
        "n_features_cached": features_m["n_clips"],
        "anchors_unchanged": anchor_out["all_unchanged"],
        "c6_feature_cache_unchanged": anchor_out["c6_feature_cache_unchanged"],
    }


if __name__ == "__main__":
    r = main()
    print(json.dumps(r, indent=2))
