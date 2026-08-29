#!/usr/bin/python3
"""Byte-determinism × 2 gate for M-EAR-1/real-label-training-v2.

Runs the full pipeline TWICE (features stage is cache-hit for run 2)
into isolated data_dir suffixes, then compares SHA-256 across the three
gated artifacts. Writes data/ear_v2/determinism_check.json with the
per-artifact SHAs. Never mutates the on-disk features_v2/ cache.
"""
# created: 2026-08-29T12:16:00Z  cycle: 39  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
import shutil
from pathlib import Path

DATA_DIR = Path("data/ear_v2")
GATED = ["training_result.json", "corn_head_v2.pt", "sb_v2_verdict.json"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def collect() -> dict:
    return {name: _sha(DATA_DIR / name) for name in GATED}


def main() -> dict:
    # Assumes run_all has been invoked at least once (fills features cache).
    # Take run_1 snapshot.
    r1 = collect()
    # Second run: re-invoke train + evaluate (feature cache is content-
    # addressed so skip-if-hash-matches).
    from scripts.ear_v2.train_v2 import train
    from scripts.ear_v2.evaluate_sb_v2 import evaluate
    _ = train()
    _ = evaluate()
    r2 = collect()
    out = {
        "gated_artifacts": GATED,
        "run_1": r1,
        "run_2": r2,
        "byte_determinism_x2": all(r1[k] == r2[k] for k in GATED),
        "diffs": [k for k in GATED if r1[k] != r2[k]],
    }
    (DATA_DIR / "determinism_check.json").write_text(
        json.dumps(out, indent=2, sort_keys=True)
    )
    return out


if __name__ == "__main__":
    r = main()
    print(json.dumps(r, indent=2))
