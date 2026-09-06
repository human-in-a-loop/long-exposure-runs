#!/usr/bin/env /usr/bin/python3
"""M-V4-EAR-1 v2 calibration module (c76 sibling to v4_ear.py).

Purpose
-------
c75 diagnostic (data/v4/ear/calibration_saturation_probe_c75.json) established
that the c74-landed `scripts/ear/v4_ear.py` linear-anchor calibration clips
4/5 exemplar LOO scores to 7.0 because anchor_high is computed as the mean of
loo raw stats (0.930365) which sits BELOW most exemplars' raw stats. c76
lands a WIDER-LINEAR calibration variant that scales anchor_high above the
raw ceiling to avoid saturation.

READ-ONLY anchors preserved (invariant d + FD-1)
------------------------------------------------
* `scripts/ear/v4_ear.py` sha256 `aeac868f97492d60e1a7db80ad0290ab63a120a6ba962b17751e151127b5f5b2` NOT touched.
* `data/v4/ear/exemplar_set.json` NOT touched.
* `data/v4/ear/{exemplar_embeddings.npz, band4_embeddings.npz}` NOT touched.

This module re-uses `v4_ear`'s public API for signature loading, statistic
computation, and sanity gate; it exports a NEW calibration function
`calibrate_wider_linear` and a wrapper `leave_one_out_v2` + `score_audio_v2`.

Empirical L119 infeasibility disclosure (c76)
---------------------------------------------
Even under wider-linear calibration, L119 mandate `band4_max < loo_min - 0.5`
CANNOT be satisfied because the underlying raw statistic itself has
band4_max (stay_live 0.9413) > exemplar_min (desire 0.8706). Any monotone
calibration is empirically infeasible under the current VGGish-only backbone.
See `scripts/ear/probe_l119_infeasibility_c76.py` +
`data/v4/ear/l119_infeasibility_proof_c76.json` for the sweep across 3
statistics x 3 calibrations. Under FD-6 operator-ear-authority precedent
(standing since c47), M-V4-GEN-1 completion falls to operator adjudication.

Constants + backbone + env-pin: inherited from v4_ear (imported).
No PRNG. No sidecar_nonfactor. No VST3 state APIs.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict

# READ-ONLY re-export via import from c74 module
from scripts.ear import v4_ear as _v1

WINDOW_SECONDS = _v1.WINDOW_SECONDS
BEST_FRACTION = _v1.BEST_FRACTION
NOISE_FLOOR_DEFAULT = _v1.NOISE_FLOOR_DEFAULT

CALIBRATION_ID_V2 = "wider_linear_c76"
ANCHOR_HIGH_V2_MARGIN = 0.02
ANCHOR_HIGH_V2_FLOOR = 0.98


def calibrate_wider_linear(statistic: float, raw_max_over_ex: float,
                            anchor_low: float = NOISE_FLOOR_DEFAULT) -> float:
    """Wider-linear calibration [1,7].

    anchor_high = max(raw_max_over_ex + ANCHOR_HIGH_V2_MARGIN, ANCHOR_HIGH_V2_FLOOR)
    Ensures exemplar loo raw stats (up to essence 0.9567) land below the ceiling
    and do NOT clip to 7.0. Preserves monotonicity.
    """
    anchor_high = max(raw_max_over_ex + ANCHOR_HIGH_V2_MARGIN, ANCHOR_HIGH_V2_FLOOR)
    if anchor_high <= anchor_low:
        return 1.0
    raw = 1.0 + 6.0 * (statistic - anchor_low) / (anchor_high - anchor_low)
    return max(1.0, min(7.0, raw))


def leave_one_out_v2(exemplar_set: dict,
                     exemplar_signatures: Dict[str, list] | None = None,
                     noise_floor: float = NOISE_FLOOR_DEFAULT) -> Dict[str, float]:
    """Per-exemplar leave-one-out under WIDER-LINEAR calibration.

    Uses the same c74 raw statistic (max-over-exemplar-windows, best-50% mean)
    but calibrates via `calibrate_wider_linear` with a raw-ceiling-derived
    anchor_high, so all 5 exemplars land in [~6.2, ~6.8] range instead of
    clipping.
    """
    if exemplar_signatures is None:
        exemplar_signatures = _v1.build_exemplar_signatures(exemplar_set)

    # First pass: compute raw stats for all exemplars to derive shared raw ceiling
    raw_stats: Dict[str, float] = {}
    for held_out in exemplar_signatures:
        rest = {k: v for k, v in exemplar_signatures.items() if k != held_out}
        raw_stats[held_out] = _v1._max_over_exemplar_windows(
            exemplar_signatures[held_out], rest
        )
    raw_max = max(raw_stats.values())

    scores: Dict[str, float] = {}
    for held_out, raw in raw_stats.items():
        scores[held_out] = calibrate_wider_linear(raw, raw_max, noise_floor)
    return scores


def score_audio_v2(candidate_windows: list,
                   exemplar_signatures: Dict[str, list],
                   raw_max_over_ex: float,
                   noise_floor: float = NOISE_FLOOR_DEFAULT) -> float:
    """Score a candidate under wider-linear calibration.

    `raw_max_over_ex` must be supplied by the caller (from a shared LOO pass
    over the exemplar set). This decouples per-candidate scoring from
    per-cycle exemplar re-analysis.
    """
    statistic = _v1._max_over_exemplar_windows(candidate_windows, exemplar_signatures)
    return calibrate_wider_linear(statistic, raw_max_over_ex, noise_floor)


def module_env_manifest_v2() -> dict:
    """Provenance manifest for v2 calibration."""
    return {
        "calibration_id": CALIBRATION_ID_V2,
        "anchor_high_v2_margin": ANCHOR_HIGH_V2_MARGIN,
        "anchor_high_v2_floor": ANCHOR_HIGH_V2_FLOOR,
        "best_fraction": BEST_FRACTION,
        "noise_floor_default": NOISE_FLOOR_DEFAULT,
        "window_seconds": WINDOW_SECONDS,
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
        "supersedes": "v4_ear.py::_calibrate_1_7 (c74 linear-anchor, retained READ-ONLY)",
        "backbone": _v1.BACKBONE,
        "l119_infeasibility": "empirically infeasible under VGGish backbone regardless of calibration; see data/v4/ear/l119_infeasibility_proof_c76.json",
    }


if __name__ == "__main__":
    print(json.dumps(module_env_manifest_v2(), sort_keys=True, indent=2))
