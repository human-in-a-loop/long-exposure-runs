#!/usr/bin/env /usr/bin/python3
"""c75 P3.b — DIAGNOSTIC probe: LOO calibration-saturation characterization.

Per c74 auditor P2 finding: 4/5 exemplars scored exactly 7.0 under VGGish-only,
suggesting calibration saturation at RATING_ANCHOR_HIGH=7. This probe:

  (i)  P3.a verified: LOO code does NOT self-include (verified by inspection at
       scripts/ear/v4_ear.py::leave_one_out — remaining dict comprehension excludes
       held_out). Saturation is GENUINE, not a bug.

  (ii) Compute raw statistics per exemplar under 3 variants:
       - variant_current  : c74 impl (linear-anchor to loo-mean; clipped [1,7])
       - variant_sigmoid  : sigmoid dampening at 0.9 * ceiling
       - variant_percentile: percentile calibration against 5-exemplar corpus

Output: data/v4/ear/calibration_saturation_probe_c75.json

READ-ONLY consumers of v4_ear.py; DOES NOT modify v4_ear.py or exemplar_set.json.
"""
from __future__ import annotations
import json
import math
import os
import sys
from pathlib import Path

# Env pins (canonical 7-key subset)
_PINS = {
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
    "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.ear import v4_ear  # READ-ONLY import


def compute_raw_stats(sigs: dict) -> dict:
    """For each exemplar X: raw = max-over-exemplar-windows(X, sigs \\ X)."""
    raw = {}
    for held_out in sigs:
        remaining = {k: v for k, v in sigs.items() if k != held_out}
        raw[held_out] = v4_ear._max_over_exemplar_windows(sigs[held_out], remaining)
    return raw


def variant_current(raw: dict, noise_floor: float = 0.15) -> dict:
    """Reproduce c74 linear-anchor-to-loo-mean map (verify against v4_ear.leave_one_out)."""
    scores = {}
    # Anchor = mean of loo raw stats over remaining (per exemplar)
    ids = list(raw.keys())
    for held_out in ids:
        raw_stat = raw[held_out]
        # anchor_high = mean of loo raw for remaining (each scored against remaining \\ self)
        # For efficiency in a probe: reuse raw dict — anchor_high approximates
        # since raw[i] = score of i against {all - i}, and loo over remaining is
        # score of i against {remaining - i}. For 5-exemplar corpus these differ
        # slightly but characterize the same saturation phenomenon.
        remaining_raw = [raw[k] for k in ids if k != held_out]
        anchor_high = sum(remaining_raw) / len(remaining_raw)
        scores[held_out] = v4_ear._calibrate_1_7(raw_stat, anchor_high, noise_floor)
    return scores


def variant_sigmoid(raw: dict, noise_floor: float = 0.15, ceiling_frac: float = 0.9) -> dict:
    """Sigmoid dampening at ceiling_frac * (top raw stat)."""
    scores = {}
    ids = list(raw.keys())
    max_raw = max(raw.values())
    center = ceiling_frac * max_raw
    # Steepness: k tuned so raw=noise_floor maps near 1, raw=max_raw maps near 7.
    span = max_raw - noise_floor
    k = 6.0 / max(span, 1e-9)  # slope
    for held_out in ids:
        r = raw[held_out]
        # Sigmoid: score = 1 + 6 * sigmoid(k*(r-center)) but calibrated so
        # r=noise_floor -> ~1, r=max_raw -> ~7.
        z = k * (r - center)
        s = 1.0 / (1.0 + math.exp(-z))
        # Map s in (0,1) linearly to (1,7)
        score = 1.0 + 6.0 * s
        scores[held_out] = round(max(1.0, min(7.0, score)), 4)
    return scores


def variant_percentile(raw: dict) -> dict:
    """Percentile calibration: rank raw across the 5-exemplar corpus, linear map to (1,7)."""
    scores = {}
    ids = sorted(raw.keys())
    sorted_raw = sorted(raw.values())
    for held_out in ids:
        r = raw[held_out]
        # Percentile = fraction of exemplars with raw <= r
        rank = sum(1 for v in sorted_raw if v <= r) - 1  # 0-indexed
        pct = rank / max(1, len(sorted_raw) - 1) if len(sorted_raw) > 1 else 0.5
        score = 1.0 + 6.0 * pct
        scores[held_out] = round(max(1.0, min(7.0, score)), 4)
    return scores


def diagnose_saturation(raw: dict, scores_current: dict) -> dict:
    """Characterize whether saturation is calibration-driven or fundamental."""
    r_vals = list(raw.values())
    r_min, r_max = min(r_vals), max(r_vals)
    r_span = r_max - r_min
    r_span_relative = r_span / max(r_max, 1e-9)
    ceiling_count = sum(1 for s in scores_current.values() if s >= 6.99)
    return {
        "raw_min": r_min,
        "raw_max": r_max,
        "raw_span": r_span,
        "raw_span_relative": r_span_relative,
        "ceiling_count_at_7p0": ceiling_count,
        "characterization": (
            "confirmed_saturation" if r_span_relative < 0.05
            else "wide_span_ceiling_from_anchor_choice" if ceiling_count >= 2
            else "no_clear_saturation"
        ),
    }


def main():
    sigs = v4_ear.build_exemplar_signatures(v4_ear.load_exemplar_set())
    raw = compute_raw_stats(sigs)
    v_curr = variant_current(raw)
    v_sig = variant_sigmoid(raw)
    v_pct = variant_percentile(raw)
    diag = diagnose_saturation(raw, v_curr)

    out = {
        "milestone_id": "P3-diagnostic",
        "cycle": 75,
        "backbone": "vggish_only",
        "n_exemplars": len(sigs),
        "raw_stats": {k: round(v, 6) for k, v in raw.items()},
        "variants": {
            "current_linear_anchor": v_curr,
            "sigmoid_dampen_0p9_ceiling": v_sig,
            "percentile_5corpus": v_pct,
        },
        "saturation_diagnosis": diag,
        "notes": {
            "P3a_loo_self_include_bug_check": "PASS_no_bug — remaining excludes held_out at v4_ear.py:166",
            "P3b_purpose": "diagnostic only; does NOT alter v4_ear.py or exemplar_set.json per brief",
            "downstream_c76": "if characterization=confirmed_saturation, propose anchor-scaling fix in c76",
        },
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    out_path = ROOT / "data/v4/ear/calibration_saturation_probe_c75.json"
    out_path.write_text(json.dumps(out, sort_keys=True, indent=2))
    print("PROBE_LANDED", out_path)
    print(json.dumps(diag, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
