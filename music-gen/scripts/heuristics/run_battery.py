#!/usr/bin/env -S /usr/bin/python3
# run_battery.py — CLI: --manifest <path> → writes clip_battery.tsv
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1
"""Run the four-heuristic battery on every clip in an ingestion manifest."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def main() -> int:
    assert sys.executable == "/usr/bin/python3", f"wrong interpreter: {sys.executable}"
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--workspace", type=Path,
                    default=Path("/home/user/long-exposure-runs/music-gen"))
    args = ap.parse_args()

    # Make `scripts.heuristics` importable when running as a script.
    sys.path.insert(0, str(args.workspace))
    from scripts.heuristics.battery import load_clip, run_battery, HEURISTICS

    with args.manifest.open() as f:
        rows = [json.loads(line) for line in f if line.strip()]
    source = [r for r in rows if r["kind"] == "source"][0]
    clips = sorted([r for r in rows if r["kind"] == "clip"], key=lambda r: r["clip_index"])

    source_id = source["source_id"]
    out_dir = args.out_dir or (args.workspace / "data" / "heuristics" / source_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    tsv_path = out_dir / "clip_battery.tsv"

    # Header: compute on first clip to know all raw feature names.
    header_written = False
    with tsv_path.open("w", newline="") as f:
        writer = None
        for c in clips:
            clip_path = args.workspace / c["clip_path"]
            y, sr = load_clip(clip_path)
            results = run_battery(y, sr)
            row = {
                "clip_index": c["clip_index"],
                "clip_id": c["clip_id"],
                "t_start_s": c["t_start_s"],
                "t_end_s": c["t_end_s"],
                "anchored_tail": c["anchored_tail"],
                "short_song": c.get("short_song", False),
            }
            for h in HEURISTICS:
                r = results[h]
                short = h.replace("_quality", "")
                row[f"{short}__mess_scale"] = "" if r.mess_scale is None else f"{r.mess_scale:.6f}"
                row[f"{short}__reason"] = r.reason or ""
                for k, v in r.raw_features.items():
                    row[f"{short}__raw__{k}"] = "" if v is None else f"{v:.6f}"
            if not header_written:
                writer = csv.DictWriter(f, fieldnames=list(row.keys()), delimiter="\t")
                writer.writeheader()
                header_written = True
            writer.writerow(row)
            print(f"  clip {c['clip_index']} ({clip_path.name}) done")
    print(f"WROTE {tsv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
