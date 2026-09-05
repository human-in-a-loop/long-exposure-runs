#!/usr/bin/env /usr/bin/python3
"""c75 P4 — Band-4 spot check per campaign L119 mandate.

Scores 3 pre-computed band-4 songs (aguanile, stay_live, wagon_wheel) via c74 EAR-1
impl READ-ONLY. Passes IF max(band4_scores) < min(loo_exemplar_scores) - 0.5
(mandate that band-4 renders score clearly below LOO exemplar ceiling).

Output: data/v4/ear/band4_spot_check_c75.json
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

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


def main():
    import numpy as np
    exemplar_set = v4_ear.load_exemplar_set()
    exemplar_sigs = v4_ear.build_exemplar_signatures(exemplar_set)

    # LOO baseline for exemplar ceiling
    loo_scores = v4_ear.leave_one_out(exemplar_set, exemplar_sigs)
    loo_min = min(loo_scores.values())

    # Load band-4 embeddings
    b4 = np.load(ROOT / "data/v4/ear/band4_embeddings.npz")
    band4_scores = {}
    for name in b4.files:
        windows = b4[name].astype("float64").tolist()
        # Score against full exemplar set
        band4_scores[name] = round(v4_ear.score_audio(windows, exemplar_sigs), 4)

    b4_max = max(band4_scores.values())
    b4_min = min(band4_scores.values())
    # Mandate per campaign L119: band-4 should score clearly BELOW LOO exemplar ceiling
    mandate_threshold = loo_min - 0.5
    passes = b4_max < mandate_threshold

    out = {
        "milestone_id": "P4-band4-spot-check",
        "cycle": 75,
        "backbone": "vggish_only",
        "loo_scores": {k: round(v, 4) for k, v in loo_scores.items()},
        "loo_min": round(loo_min, 4),
        "band4_scores": band4_scores,
        "band4_max": round(b4_max, 4),
        "band4_min": round(b4_min, 4),
        "mandate_threshold_loo_min_minus_0p5": round(mandate_threshold, 4),
        "gate_passes": passes,
        "gate_description": "band-4 max < loo_min - 0.5 (campaign L119)",
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    if not passes:
        out["halt_honest_finding"] = (
            "Band-4 songs score >= loo_min - 0.5. Calibration does NOT distinguish "
            "band-4 from band-7 exemplars under current linear-anchor scheme. This "
            "corroborates c74 P2 saturation finding and BLOCKS passer-count trust "
            "for the batch-scoring pass in P1. Hand to c76 for calibration-anchor fix."
        )
    out_path = ROOT / "data/v4/ear/band4_spot_check_c75.json"
    out_path.write_text(json.dumps(out, sort_keys=True, indent=2))
    print("BAND4_SPOT_CHECK_LANDED", out_path)
    print(f"band4 scores: {band4_scores}, max={b4_max:.3f}, loo_min={loo_min:.3f}, gate={'PASS' if passes else 'FAIL'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
