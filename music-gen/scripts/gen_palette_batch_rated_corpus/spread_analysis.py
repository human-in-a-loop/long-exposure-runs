#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T14:34:40Z
# cycle: 43
# run_id: fork-c320de981fda-clone-0
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-rated-corpus
# ---
"""Spread analysis across 3 salts (verbatim c34 v1 pattern).

Per-key (mel_l1_db, spectral_centroid_rmse_hz, rms_env_rmse,
lufs_m_rmse_lu) IQR (25th, 75th) + max-min on each of the two panels.

Deterministic; no PRNG.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")


def _percentile_linear(values, q):
    if not values:
        return float("nan")
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    idx = (len(s) - 1) * (q / 100.0)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return s[lo]
    frac = idx - lo
    return s[lo] + frac * (s[hi] - s[lo])


def _iqr_and_range(values):
    p25 = _percentile_linear(values, 25.0)
    p75 = _percentile_linear(values, 75.0)
    return {
        "values": list(values),
        "p25": p25,
        "p75": p75,
        "iqr": p75 - p25,
        "max_minus_min": (max(values) - min(values)) if values else float("nan"),
    }


def compute_spread(per_salt_panels: dict) -> dict:
    """Return the {salts, per_key} structure for spread_analysis.json.

    per_salt_panels: {salt: {panel_name: {panel_key: value}}}.
    """
    salts = sorted(per_salt_panels.keys())
    per_key = {"panel_original": {}, "panel_fluidsynth": {}}
    for pname in per_key:
        for k in NUMERIC_KEYS:
            values = [per_salt_panels[s][pname].get(k) for s in salts]
            values = [v for v in values if v is not None and math.isfinite(v)]
            per_key[pname][k] = _iqr_and_range(values)
    return {"salts": salts, "per_key": per_key}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir",
                    default="data/gen_palette_batch_rated_corpus")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    per_salt_panels = {}
    for salt_dir in sorted(data_dir.glob("per_song/*")):
        if not salt_dir.is_dir():
            continue
        try:
            salt = int(salt_dir.name)
        except ValueError:
            continue
        panels = {}
        for tsv_name in ("panel_original", "panel_fluidsynth"):
            tsv_path = salt_dir / f"{tsv_name}.tsv"
            if not tsv_path.exists():
                continue
            lines = tsv_path.read_text().strip().splitlines()
            if len(lines) < 2:
                continue
            hdr = lines[0].split("\t")
            row = lines[1].split("\t")
            panels[tsv_name] = {}
            for k, v in zip(hdr, row):
                try:
                    panels[tsv_name][k] = float(v) if v else None
                except ValueError:
                    panels[tsv_name][k] = v
        per_salt_panels[salt] = panels

    result = compute_spread(per_salt_panels)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
