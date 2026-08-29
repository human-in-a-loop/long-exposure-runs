#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T09:11:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v4
# ---
"""Per-key IQR + max−min spread across 8 salts on the two panels.

Reads data/palette_render_v4/verdict.json (per_salt_panels), computes
per-key statistics across salts, compares against c36 v3's 3-salt spread
if present.

NO PRNG. No sidecar_nonfactor. /usr/bin/python3 guarded.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
OUT_DIR = _REPO / "data" / "palette_render_v4"
V3_OUT_DIR = _REPO / "data" / "palette_render_v3"
NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")


def _iqr(values):
    n = len(values)
    if n < 2:
        return 0.0
    s = sorted(values)
    # Nearest-rank quartiles (deterministic, no numpy interpolation drift).
    q1 = s[int(0.25 * (n - 1))]
    q3 = s[int(0.75 * (n - 1))]
    return float(q3 - q1)


def _spread(values):
    if not values:
        return {"iqr": 0.0, "max_minus_min": 0.0, "median": None, "n": 0}
    return {
        "iqr": _iqr(values),
        "max_minus_min": float(max(values) - min(values)),
        "median": float(statistics.median(values)),
        "n": len(values),
    }


def _spread_from_verdict(path: Path) -> dict:
    if not path.is_file():
        return {}
    v = json.loads(path.read_text())
    per_salt_panels = v.get("per_salt_panels", {})
    out: dict[str, dict[str, dict]] = {"panel_original": {}, "panel_fluidsynth": {}}
    for panel_name in ("panel_original", "panel_fluidsynth"):
        for k in NUMERIC_KEYS:
            vals = []
            for s_key, panels in per_salt_panels.items():
                p = panels.get(panel_name, {})
                val = p.get(k)
                if isinstance(val, (int, float)):
                    vals.append(float(val))
            out[panel_name][k] = _spread(vals)
    return out


def main() -> int:
    v4 = _spread_from_verdict(OUT_DIR / "verdict.json")
    v3 = _spread_from_verdict(V3_OUT_DIR / "verdict.json")

    # v4-vs-v3 delta on IQR (informative only — not a hard gate).
    delta: dict[str, dict[str, dict]] = {"panel_original": {}, "panel_fluidsynth": {}}
    v4_wins_count = 0
    v3_wins_count = 0
    for panel_name in ("panel_original", "panel_fluidsynth"):
        for k in NUMERIC_KEYS:
            v4_iqr = v4.get(panel_name, {}).get(k, {}).get("iqr")
            v3_iqr = v3.get(panel_name, {}).get(k, {}).get("iqr")
            row = {"v4_iqr": v4_iqr, "v3_iqr": v3_iqr}
            if isinstance(v4_iqr, (int, float)) and isinstance(v3_iqr, (int, float)):
                row["v4_minus_v3_iqr"] = v4_iqr - v3_iqr
                if v4_iqr > v3_iqr:
                    v4_wins_count += 1
                elif v4_iqr < v3_iqr:
                    v3_wins_count += 1
            delta[panel_name][k] = row

    result = {
        "v4_spread": v4,
        "v3_spread": v3,
        "iqr_delta_v4_vs_v3": delta,
        "iqr_v4_wins_of_8": v4_wins_count,
        "iqr_v3_wins_of_8": v3_wins_count,
        "corroborates_param_moves_audio": v4_wins_count > v3_wins_count,
    }
    (OUT_DIR / "spread_analysis.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
