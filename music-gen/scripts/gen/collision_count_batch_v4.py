#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T17:15:00Z
# cycle: 16
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork cc548ca0c2e5)
# milestone: M-GEN-1/batch-v4-compound
# ---
"""Standalone entry point for the batch-v4 collision count.

Thin wrapper over ``scripts.gen.collision_analysis.analyze`` (cycle-13),
with per-rule_type contribution reporting as required by the research
brief. Re-imports the SAME analyze() function the driver uses; separate
CLI exists solely so an auditor can re-materialize the count from just
``data/gen/batch_v4/song_<s>/sampling_manifest.json`` without running
the full render pipeline.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.gen.collision_analysis import analyze, write_tsv  # noqa: E402


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v4")
    args = ap.parse_args(argv)

    result = analyze(args.batch_root)
    (args.batch_root / "collision_analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    write_tsv(result, args.batch_root / "collision_matrix.tsv")
    total = result["coerced"]["total_pairwise_collisions"]
    print(f"[collision_count_batch_v4] coerced pairs = {total}")
    print(f"[collision_count_batch_v4] per-rule_type contribution:")
    for rt in result["rule_types"]:
        n = len(result["coerced"]["per_rule_type_pairs"][rt])
        print(f"  {rt}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
