#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:12:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v2-sampler-diversified
# ---
"""Spread analysis across 3 salts on both panels.

Per-key IQR (linear-interp percentile, numpy-default) + max−min on the
4 numeric-family keys (mel_l1_db, spectral_centroid_rmse_hz,
rms_env_rmse, lufs_m_rmse_lu). Reported for BOTH `panel_original` and
`panel_fluidsynth`. Also computes Pearson correlation of per-salt
sfizz_count vs per-salt mel_l1_db on `panel_fluidsynth`.

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


def _percentile_linear(values: list[float], q: float) -> float:
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


def _iqr_and_range(values: list[float]) -> dict:
    p25 = _percentile_linear(values, 25.0)
    p75 = _percentile_linear(values, 75.0)
    return {
        "values": list(values),
        "p25": p25,
        "p75": p75,
        "iqr": p75 - p25,
        "max_minus_min": (max(values) - min(values)) if values else float("nan"),
    }


def _pearson(x: list[float], y: list[float]) -> float | None:
    n = len(x)
    if n < 2 or n != len(y):
        return None
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    denx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    deny = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if denx == 0 or deny == 0:
        return None
    return num / (denx * deny)


def compute_spread(per_salt: list[dict],
                   per_salt_panels: dict[int, dict[str, dict]]) -> dict:
    """Return a dict conforming to spread_analysis.json schema.

    per_salt: list of song dicts from render_song.render_song.
    per_salt_panels: {salt: {panel_name: {panel_key: value}}}.
    """
    salts = sorted(per_salt_panels.keys())

    per_key = {"panel_original": {}, "panel_fluidsynth": {}}
    for pname in per_key:
        for k in NUMERIC_KEYS:
            values = [per_salt_panels[s][pname].get(k) for s in salts]
            values = [v for v in values if v is not None and math.isfinite(v)]
            per_key[pname][k] = _iqr_and_range(values)

    sfizz_counts = [s["dispatch"]["sfizz_count"] for s in per_salt]
    mel_deltas = [per_salt_panels[s["salt"]]["panel_fluidsynth"].get("mel_l1_db", 0.0)
                  for s in per_salt]
    corr = _pearson(sfizz_counts, mel_deltas)

    return {
        "salts": salts,
        "per_key": per_key,
        "sfizz_counts_per_salt": sfizz_counts,
        "mel_l1_db_per_salt_fluid_vs_palette": mel_deltas,
        "sfizz_vs_delta_correlation": corr,
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir",
                    default="data/gen_palette_batch_v2",
                    help="dir with per_song/<salt>/panel_*.tsv + dispatch_summary.json")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    per_salt = []
    per_salt_panels = {}
    for salt_dir in sorted(data_dir.glob("per_song/*")):
        if not salt_dir.is_dir():
            continue
        try:
            salt = int(salt_dir.name)
        except ValueError:
            continue
        dispatch = json.loads((salt_dir / "dispatch_summary.json").read_text())
        per_salt.append({"salt": salt, "dispatch": dispatch})
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

    result = compute_spread(per_salt, per_salt_panels)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
