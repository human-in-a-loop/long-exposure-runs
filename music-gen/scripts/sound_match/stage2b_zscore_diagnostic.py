#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T20:00:00Z
# cycle: 3
# run_id: run-2026-09-03T200000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-stage2b-launched
# ---
"""Thin wrapper reusing the c2 stage-2 z-score-diagnostic compute path on
the 216-row stage-2b leaderboard.

c2's ``stage2_zscore_diagnostic`` is column-name-based and format-agnostic;
the only thing that changes at c3 is the input row count (216 vs 180) and
the presence of a new ``loudness_method`` column that we intentionally
ignore here. The report continues to present the raw composite as
authoritative per spec §Objective (weights literal-frozen 0.5/0.25/0.25).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# --- env pins BEFORE any observed import ---
_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"stage2b_zscore_diagnostic requires /usr/bin/python3 (got {sys.executable})"
    )

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.stage2_zscore_diagnostic import (  # noqa: E402
    read_leaderboard,
    compute_zscores,
    write_zscore_leaderboard,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Stage-2b z-score diagnostic (presentation only, c2 shim)."
    )
    ap.add_argument("--stage2b-leaderboard", required=True, type=Path)
    ap.add_argument("--out-tsv", required=True, type=Path)
    ap.add_argument("--stats-json", type=Path, default=None)
    args = ap.parse_args(argv)

    rows, fields = read_leaderboard(args.stage2b_leaderboard)
    stats = compute_zscores(rows)
    write_zscore_leaderboard(rows, fields, args.out_tsv)
    if args.stats_json is not None:
        import json
        args.stats_json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.stats_json, "w") as f:
            json.dump(
                {"components": stats, "n_rows": len(rows),
                 "cycle": 3, "source": "stage2b"},
                f, sort_keys=True, indent=2,
            )
    print(f"z-score leaderboard: {args.out_tsv}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
