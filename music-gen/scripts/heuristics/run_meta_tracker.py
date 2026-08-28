#!/usr/bin/env -S /usr/bin/python3
# run_meta_tracker.py — CLI: --manifest <path> → writes meta_descriptors.json
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1/meta-tracker
"""Run the intra-song meta-tracker for one seed song."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    assert sys.executable == "/usr/bin/python3", f"wrong interpreter: {sys.executable}"
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--battery-tsv", type=Path, default=None,
                    help="defaults to data/heuristics/<source_id>/clip_battery.tsv")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--workspace", type=Path,
                    default=Path("/home/user/long-exposure-runs/music-gen"))
    args = ap.parse_args()

    sys.path.insert(0, str(args.workspace))
    from scripts.heuristics.meta_tracker import run_meta_tracker

    with args.manifest.open() as f:
        first = json.loads(next(f))
    source_id = first["source_id"]
    battery_tsv = args.battery_tsv or (args.workspace / "data" / "heuristics" / source_id / "clip_battery.tsv")
    out = args.out or (args.workspace / "data" / "heuristics" / source_id / "meta_descriptors.json")

    result = run_meta_tracker(args.manifest, battery_tsv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
    print(f"WROTE {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
