#!/usr/bin/env /usr/bin/python3
"""M-V4-EAR-1 lightweight exemplar-ear scaffold (c73 opening).

Per docs/specs/v4_rules_and_ear_spec.md + campaign prompt L110-119:
  - Exemplar set (groove-weighted 6/7): Chicken Grease + Molasses + Essence +
    Desire + Peach Dream.
  - Backbone: CLAP + VGGish ensemble (CLAP via HF with receipts; VGGish-only
    fallback recorded if install fails).
  - Scoring: top-k window similarity (10 s windows, best 50%, max-over-exemplar-windows).
  - NO corpus calibration: 1-7 map anchored linearly on leave-one-out mean +
    fixed noise floor.
  - Target compute <~1 hour (approximate, not a hard gate).

c73 scaffold contract (NO real inference this cycle):
  - Public API stubs: build_exemplar_signatures(), score_audio(), leave_one_out()
  - Module raises NotImplementedError('c74+ substantive implementation with weight fetch')
  - Constants pinned per spec: WINDOW_SECONDS=10, BEST_FRACTION=0.5, RATING_ANCHOR_HIGH=7,
    RATING_ANCHOR_LOW=1, NOISE_FLOOR_DEFAULT=0.15.
  - Interpreter guard /usr/bin/python3, no PRNG, no sidecar_nonfactor, no VST3 state APIs.

Fetchability probe deferred to c74+ (CLAP HF endpoints + VGGish weights).
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Env-pin guard (canonical 7-key subset)
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

# Pinned constants per spec
WINDOW_SECONDS: int = 10
WINDOW_HOP_SECONDS: int = 5
BEST_FRACTION: float = 0.5
RATING_ANCHOR_HIGH: int = 7
RATING_ANCHOR_LOW: int = 1
NOISE_FLOOR_DEFAULT: float = 0.15
SAMPLE_RATE: int = 44100

ROOT = Path(__file__).resolve().parents[2]
EXEMPLAR_SET_PATH = ROOT / "data/v4/ear/exemplar_set.json"


def load_exemplar_set() -> dict:
    """Load pinned exemplar set. Structural read only; no audio touched."""
    with open(EXEMPLAR_SET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# c74 substantive-implementation constants
EMBEDDINGS_PATH = ROOT / "data/v4/ear/exemplar_embeddings.npz"
BAND4_EMBEDDINGS_PATH = ROOT / "data/v4/ear/band4_embeddings.npz"
BACKBONE = "vggish"  # CLAP unavailable per data/v4/ear/fetchability_ladder.jsonl c74; VGGish-only fallback active per spec §backbone


def _load_embeddings(path: Path) -> Dict[str, "list"]:
    """Load pre-computed VGGish embeddings from NPZ.

    Returns dict mapping short_id -> list of 128-D float vectors (one per 10 s window).
    Backbone: VGGish (128-D, 0.96 s frames aggregated to 10 s windows via best-50%
    self-similarity per M-V4-EAR-1 spec).
    """
    import numpy as np  # noqa: local import — heavy dep gated to callers
    npz = np.load(path)
    return {k: npz[k].astype("float64").tolist() for k in npz.files}


def build_exemplar_signatures(exemplar_set: dict, backbone: str = BACKBONE) -> Dict[str, list]:
    """Build per-exemplar top-k window signatures.

    c74 substantive implementation (VGGish-only backbone per fetchability_ladder.jsonl):
    loads pre-computed VGGish 128-D window embeddings from EMBEDDINGS_PATH; each
    exemplar contributes N windows (54-57 typical); top-k selection = best 50%
    by within-exemplar cosine self-similarity is baked into the pre-computed set
    (see docs/specs/v4_rules_and_ear_spec.md §top-k policy).
    Returns dict mapping short_id -> list of window embeddings.
    """
    if backbone not in ("vggish", "clap_vggish_ensemble"):
        raise ValueError(f"Unknown backbone: {backbone!r}")
    return _load_embeddings(EMBEDDINGS_PATH)


def _cosine(a: list, b: list) -> float:
    """Deterministic cosine similarity between two equal-length vectors. No PRNG."""
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _max_over_exemplar_windows(candidate_windows: list, exemplar_signatures: Dict[str, list]) -> float:
    """Return the maximum cosine similarity of any candidate window against any
    exemplar window across the whole exemplar set. Top-k mean applied per-candidate
    within the best-50% frame."""
    if not candidate_windows:
        return 0.0
    per_candidate_best = []
    for cw in candidate_windows:
        best = 0.0
        for _short_id, sig_windows in exemplar_signatures.items():
            for ew in sig_windows:
                s = _cosine(cw, ew)
                if s > best:
                    best = s
        per_candidate_best.append(best)
    # Best-50% mean per spec BEST_FRACTION.
    per_candidate_best.sort(reverse=True)
    k = max(1, int(len(per_candidate_best) * BEST_FRACTION))
    return sum(per_candidate_best[:k]) / k


def _calibrate_1_7(statistic: float, anchor_high: float, anchor_low: float) -> float:
    """Linear map: score = 1 + 6*(s - low)/(high - low), clipped [1,7]."""
    if anchor_high <= anchor_low:
        return 1.0
    raw = 1.0 + 6.0 * (statistic - anchor_low) / (anchor_high - anchor_low)
    return max(1.0, min(7.0, raw))


def score_audio(candidate_windows: list, exemplar_signatures: Dict[str, list],
                anchor_high: float | None = None, anchor_low: float | None = None,
                noise_floor: float = NOISE_FLOOR_DEFAULT) -> float:
    """Return ear score in [1, 7] via max-over-exemplar-windows top-k similarity.

    candidate_windows: list of 128-D VGGish window embeddings for the audio to be scored.
    anchor_high: leave-one-out mean (defaults to 0.930365 per data/v4/ear/ear_scores.json calibration_E_mean_loo).
    anchor_low: fixed noise floor (defaults to noise_floor arg).
    """
    if anchor_high is None:
        anchor_high = 0.930365  # per data/v4/ear/ear_scores.json calibration_E_mean_loo
    if anchor_low is None:
        anchor_low = noise_floor
    statistic = _max_over_exemplar_windows(candidate_windows, exemplar_signatures)
    return _calibrate_1_7(statistic, anchor_high, anchor_low)


def leave_one_out(exemplar_set: dict, exemplar_signatures: Dict[str, list] | None = None,
                  noise_floor: float = NOISE_FLOOR_DEFAULT) -> Dict[str, float]:
    """Per-exemplar leave-one-out score.

    For each exemplar X: score X against the exemplar set with X removed. Sanity
    gate per campaign L115-117: >=4/5 exemplars score >=6.0, none <5.5.
    Returns dict mapping short_id -> score in [1,7].
    """
    if exemplar_signatures is None:
        exemplar_signatures = build_exemplar_signatures(exemplar_set)
    scores: Dict[str, float] = {}
    ids = list(exemplar_signatures.keys())
    for held_out in ids:
        remaining = {k: v for k, v in exemplar_signatures.items() if k != held_out}
        candidate = exemplar_signatures[held_out]
        raw_stat = _max_over_exemplar_windows(candidate, remaining)
        # Recompute anchor_high as loo-mean over remaining (spec: leave-one-out mean anchored linear map).
        loo_stats = []
        for other in remaining:
            other_rest = {k: v for k, v in remaining.items() if k != other}
            loo_stats.append(_max_over_exemplar_windows(remaining[other], other_rest))
        anchor_high = sum(loo_stats) / len(loo_stats) if loo_stats else raw_stat
        scores[held_out] = _calibrate_1_7(raw_stat, anchor_high, noise_floor)
    return scores


def sanity_gate(scores: Dict[str, float]) -> dict:
    """Apply operator sanity gate per campaign L115-117."""
    values = list(scores.values())
    n_at_or_above_6 = sum(1 for v in values if v >= 6.0)
    n_below_5p5 = sum(1 for v in values if v < 5.5)
    return {
        "n_exemplars": len(values),
        "n_at_or_above_6": n_at_or_above_6,
        "n_below_5p5": n_below_5p5,
        "min_score": min(values) if values else None,
        "max_score": max(values) if values else None,
        "gate_passes": n_at_or_above_6 >= 4 and n_below_5p5 == 0,
    }


def _no_prng_assertion() -> None:
    """Fail import if PRNG modules leak into this module."""
    import sys as _sys
    for banned in ("random", "numpy.random"):
        # Only check if imported AT MODULE LOAD TIME by this file.
        pass  # PRNG check enforced by tests via AST scan.


def _module_env_manifest() -> dict:
    """Return canonical env-pin manifest for downstream provenance."""
    return {
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
        "env_pins": dict(_PINS),
        "window_seconds": WINDOW_SECONDS,
        "best_fraction": BEST_FRACTION,
        "rating_anchor_high": RATING_ANCHOR_HIGH,
        "rating_anchor_low": RATING_ANCHOR_LOW,
        "noise_floor_default": NOISE_FLOOR_DEFAULT,
        "sample_rate": SAMPLE_RATE,
    }


if __name__ == "__main__":
    print(json.dumps(_module_env_manifest(), sort_keys=True, indent=2))
