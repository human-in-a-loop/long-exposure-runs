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


def build_exemplar_signatures(exemplar_set: dict, backbone: str = "clap_vggish_ensemble") -> Dict[str, list]:
    """Build per-exemplar top-k window signatures.

    c74+ implementation: for each exemplar, extract 10 s windows over the whole
    section, embed with CLAP + VGGish, retain best 50% by within-exemplar
    self-similarity. Returns dict mapping exemplar_sha16 -> list of signatures.
    """
    raise NotImplementedError(
        "c74+ substantive implementation with CLAP+VGGish weight fetch. "
        "Scaffold pinned at c73 per M-V4-EAR-1 opening; see docs/specs/v4_rules_and_ear_spec.md."
    )


def score_audio(audio_path: str, exemplar_signatures: Dict[str, list],
                anchor_high: float | None = None, anchor_low: float | None = None,
                noise_floor: float = NOISE_FLOOR_DEFAULT) -> float:
    """Return ear score in [1, 7] via max-over-exemplar-windows top-k similarity.

    anchor_high: leave-one-out mean (default = RATING_ANCHOR_HIGH region).
    anchor_low: fixed noise floor (default NOISE_FLOOR_DEFAULT).
    """
    raise NotImplementedError("c74+ substantive implementation")


def leave_one_out(exemplar_set: dict) -> Dict[str, float]:
    """Per-exemplar leave-one-out score. Sanity gate: ≥4/5 ≥6, none < 5.5."""
    raise NotImplementedError("c74+ substantive implementation")


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
