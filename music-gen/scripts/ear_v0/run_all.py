"""Orchestrator: run features -> train -> evaluate -> anchor_preservation.

Byte-determinism × 2: caller reruns the script (or the child scripts)
and asserts SHA-256 equality on the six named outputs.

Anchor preservation: snapshots pre/post SHAs of upstream c6/c22/c26
files that MUST NOT be mutated by this branch.
"""
# created: 2026-08-29T07:27:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: M-EAR-1/real-label-training-v0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
from pathlib import Path

from scripts.ear_v0.ingest_ratings import discover_songs
from scripts.ear_v0.extract_features_v0 import extract_all, build_manifest, MANIFEST_PATH
from scripts.ear_v0.train_v0 import train
from scripts.ear_v0.evaluate_success_bars import evaluate
from scripts.ear_v0.leak_ablation_v0 import summarize as leak_summarize

ANCHOR_FILES = [
    "scripts/ear/features.py",
    "scripts/ear/model.py",
    "scripts/ear/corn.py",
    "scripts/ear/leak_test.py",
    "scripts/classifier/tagger.py",
    "scripts/ear/synthetic_labels.py",
    "scripts/ear/stability_metrics.py",
    "scripts/ear/stability_audit.py",
    "docs/ear_path_b_commitment.md",
]


def _sha(p: Path) -> str:
    if not p.exists():
        return "MISSING"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def snapshot_anchors() -> dict:
    return {p: _sha(Path(p)) for p in ANCHOR_FILES}


def main() -> dict:
    pre = snapshot_anchors()

    songs = discover_songs(Path("."))
    extract_all(songs)
    manifest = build_manifest(songs)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    tres = train(songs)
    leak_summarize()
    v = evaluate()
    post = snapshot_anchors()

    anchor = {
        "pre": pre,
        "post": post,
        "unchanged": pre == post,
        "changed_paths": sorted([p for p in ANCHOR_FILES if pre[p] != post[p]]),
    }
    with open("data/ear_v0/anchor_preservation.json", "w") as f:
        json.dump(anchor, f, indent=2, sort_keys=True)
    return {"verdict": v["verdict"], "anchor_unchanged": anchor["unchanged"]}


if __name__ == "__main__":
    r = main()
    print(json.dumps(r, indent=2))
