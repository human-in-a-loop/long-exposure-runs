#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 2
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-stage2-launched
# ---
"""Post-hoc z-score-per-component diagnostic on the stage-2 leaderboard.

Presentation only: the frozen composite in scripts.sound_match.objective
is literal 0.5 / 0.25 / 0.25 per spec §Objective clause "weights frozen at
milestone start." This module computes z-normalized copies for each of the
three composite components across the 180-row stage-2 sweep, appends them
as columns, and preserves the raw-composite ordering.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"stage2_zscore_diagnostic requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np  # noqa: E402


COMPONENTS = ("mel_l1_db", "spectral_centroid_rmse_hz", "embedding_cos_vggish")


def _parse_float(s: str) -> float:
    if s in ("", "None", "null", "nan", "NaN"):
        return float("nan")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def compute_zscores(rows: list[dict]) -> dict:
    """Return {component: {'mean': ..., 'std': ..., 'iqr': ...}} + per-row z values."""
    stats = {}
    for col in COMPONENTS:
        vals = np.array([_parse_float(r.get(col, "")) for r in rows], dtype=np.float64)
        finite = vals[np.isfinite(vals)]
        if finite.size == 0:
            mean = float("nan"); std = float("nan"); iqr = float("nan")
        else:
            mean = float(np.mean(finite))
            std = float(np.std(finite, ddof=0))
            q1, q3 = np.percentile(finite, [25, 75])
            iqr = float(q3 - q1)
        stats[col] = {"mean": mean, "std": std, "iqr": iqr,
                      "n_finite": int(finite.size), "n_total": int(vals.size)}
        for r, v in zip(rows, vals):
            if std > 0 and np.isfinite(v):
                r[f"z_{col}"] = float((v - mean) / std)
            else:
                r[f"z_{col}"] = None
    return stats


def read_leaderboard(path: Path) -> tuple[list[dict], list[str]]:
    with open(path) as f:
        r = csv.DictReader(f, delimiter="\t")
        rows = [dict(row) for row in r]
        fields = r.fieldnames or []
    return rows, list(fields)


def write_zscore_leaderboard(rows: list[dict], src_fields: list[str], out: Path) -> None:
    z_fields = [f"z_{c}" for c in COMPONENTS]
    fields = list(src_fields) + z_fields
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t",
                           extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Stage-2 z-score diagnostic (presentation only)."
    )
    ap.add_argument("--stage2-leaderboard", required=True, type=Path)
    ap.add_argument("--out-tsv", required=True, type=Path)
    ap.add_argument("--stats-json", type=Path, default=None)
    args = ap.parse_args(argv)

    rows, fields = read_leaderboard(args.stage2_leaderboard)
    stats = compute_zscores(rows)
    write_zscore_leaderboard(rows, fields, args.out_tsv)
    if args.stats_json is not None:
        args.stats_json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.stats_json, "w") as f:
            json.dump({"components": stats, "n_rows": len(rows)},
                      f, sort_keys=True, indent=2)
    print(f"z-score leaderboard: {args.out_tsv}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
