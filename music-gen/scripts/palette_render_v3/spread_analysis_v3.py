#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T07:28:00Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v3
# ---
"""Cross-salt spread analysis on M-TEX-1/panel numeric-family keys.

Consumes per-salt panel TSVs written by run_batch_v3.py and produces
per-key IQR + max-min across salts 0, 1, 2 for both panel comparisons.
Output: data/palette_render_v3/spread_analysis.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
OUT_DIR = _REPO / "data" / "palette_render_v3"
SALTS = [0, 1, 2]
NUMERIC_KEYS = ["mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu"]


def _read_panel_tsv(path: Path) -> dict[str, float | None]:
    with open(path) as f:
        header = f.readline().strip().split("\t")
        row = f.readline().strip().split("\t")
    out: dict[str, float | None] = {}
    for k, v in zip(header, row):
        if v == "":
            out[k] = None
        else:
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = None
    return out


def _iqr(values: list[float]) -> float:
    """Simple IQR: q3 - q1 via linear interpolation over sorted values."""
    if not values:
        return float("nan")
    s = sorted(values)
    n = len(s)
    def q(p):
        pos = p * (n - 1)
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        frac = pos - lo
        return s[lo] * (1 - frac) + s[hi] * frac
    return q(0.75) - q(0.25)


def main() -> int:
    per_song_dir = OUT_DIR / "per_song"
    per_salt: dict[str, dict[int, dict[str, float | None]]] = {
        "panel_original": {}, "panel_fluidsynth": {}
    }
    for s in SALTS:
        for name in per_salt:
            path = per_song_dir / str(s) / f"{name}.tsv"
            per_salt[name][s] = _read_panel_tsv(path)

    result: dict = {"per_key_spread": {}, "salts": SALTS}
    for name in per_salt:
        result["per_key_spread"][name] = {}
        for k in NUMERIC_KEYS:
            values = [per_salt[name][s].get(k) for s in SALTS
                      if per_salt[name][s].get(k) is not None]
            if len(values) == 0:
                stats = {"n": 0, "iqr": None, "max_minus_min": None,
                         "values_per_salt": [None]*3}
            else:
                stats = {
                    "n": len(values),
                    "min": min(values),
                    "max": max(values),
                    "iqr": _iqr(values),
                    "max_minus_min": max(values) - min(values),
                    "values_per_salt": [per_salt[name][s].get(k) for s in SALTS],
                }
            result["per_key_spread"][name][k] = stats

    (OUT_DIR / "spread_analysis.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    print(json.dumps({k: list(v.keys()) for k, v in result["per_key_spread"].items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
