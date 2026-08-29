#!/usr/bin/env python3
# Interpreter guard: /usr/bin/python3.
"""Aggregate per-axis cost + expected corpus-delta range.

Deterministic; consumes axes.tsv (written by enumerate_axes.py); no live
network; no PRNG. Uses sum/min/max with canonical JSON emission.

Emits: data/corpus_expansion_plan/cost_estimator_output.json
"""
from __future__ import annotations

import csv
import json
import os
import sys

# Startup banner (c43 CLI-Startup-Silence interdiction).
print("[cost_estimator] c48 Branch B — aggregating per-axis costs.", file=sys.stderr)

AXIS_LABELS = {
    "i": "axis_i_egress_unblock",
    "ii": "axis_ii_alternative_sources",
    "iii": "axis_iii_partial_corpus_interpolation",
}

CONFIDENCE_BY_AXIS = {
    "i": "low",
    "ii": "medium",
    "iii": "high",
}

NOTE_BY_AXIS = {
    "i": "Egress unblock depends on out-of-band factors (yt-dlp upstream, CDN policy, workspace policy review); operator-dependent hours unbounded.",
    "ii": "Substitutability caveat: alt corpora need rating-band-equivalent distribution within +/- 2 songs per band.",
    "iii": "Analytical only; produces N-required projection under c26-frozen chassis, no corpus growth.",
}


def _agg_operator_hours(cells: list[str]) -> str:
    """Sum operator-dependent hours where meaningful; return 'unbounded' if any cell is unbounded."""
    if any(c == "unbounded" for c in cells):
        return "unbounded"
    total_lo = 0.0
    total_hi = 0.0
    all_zero = True
    for c in cells:
        if c in ("0", "", None):
            continue
        all_zero = False
        if "-" in c:
            lo, hi = c.split("-", 1)
            total_lo += float(lo)
            total_hi += float(hi)
        else:
            v = float(c)
            total_lo += v
            total_hi += v
    if all_zero:
        return "0"
    if total_lo == total_hi:
        return str(int(total_lo)) if total_lo.is_integer() else f"{total_lo:.1f}"
    lo_s = str(int(total_lo)) if total_lo.is_integer() else f"{total_lo:.1f}"
    hi_s = str(int(total_hi)) if total_hi.is_integer() else f"{total_hi:.1f}"
    return f"{lo_s}-{hi_s}"


def summarize(axes_tsv_path: str) -> dict:
    per_axis: dict[str, list[dict]] = {"i": [], "ii": [], "iii": []}
    with open(axes_tsv_path, newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            per_axis[row["axis"]].append(row)

    out: dict = {}
    for axis_key in ("i", "ii", "iii"):
        items = per_axis[axis_key]
        analytical_hours = round(sum(float(x["cost_hours_analytical"]) for x in items), 6)
        op_cells = [x["cost_hours_operator_dependent"] for x in items]
        op_hours = _agg_operator_hours(op_cells)
        delta_lo = min(int(x["expected_corpus_delta_lo"]) for x in items)
        delta_hi = max(int(x["expected_corpus_delta_hi"]) for x in items)
        out[AXIS_LABELS[axis_key]] = {
            "total_hours_analytical": analytical_hours,
            "total_hours_operator_dependent": op_hours,
            "expected_corpus_delta_range": [delta_lo, delta_hi],
            "confidence": CONFIDENCE_BY_AXIS[axis_key],
            "action_items_count": len(items),
            "note": NOTE_BY_AXIS[axis_key],
        }
    return out


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    axes_tsv = argv[0] if argv else "data/corpus_expansion_plan/axes.tsv"
    out_json = argv[1] if len(argv) > 1 else "data/corpus_expansion_plan/cost_estimator_output.json"
    summary = summarize(axes_tsv)
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"[cost_estimator] wrote {out_json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
