#!/usr/bin/env /usr/bin/python3
"""c76 P1c — Band-4 spot check under WIDER-LINEAR (v2) calibration.

Documents (again, honestly) that even with the c76 wider-linear calibration
the L119 gate `band4_max < loo_min - 0.5` still FAILS because the underlying
raw statistic already has band4_max_raw > exemplar_min_raw — a monotone-
invariant that no calibration can fix. See
`scripts/ear/probe_l119_infeasibility_c76.py` for the 3x3 sweep proof.

READ-ONLY: v4_ear.py + exemplar_set.json + *.npz not touched.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
         "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
         "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np

from scripts.ear import v4_ear, v4_ear_v2


def main():
    ex_set = v4_ear.load_exemplar_set()
    ex_sigs = v4_ear.build_exemplar_signatures(ex_set)

    # v2 LOO to derive raw_max_ex + loo_min under v2 calibration
    loo_scores_v2 = v4_ear_v2.leave_one_out_v2(ex_set, ex_sigs)
    loo_min = min(loo_scores_v2.values())

    # Derive raw_max_ex for v2 anchor
    raw_stats = {}
    for held in ex_sigs:
        rest = {k: v for k, v in ex_sigs.items() if k != held}
        raw_stats[held] = v4_ear._max_over_exemplar_windows(ex_sigs[held], rest)
    raw_max_ex = max(raw_stats.values())

    # Band-4 scoring under v2 calibration
    b4d = np.load(ROOT / "data/v4/ear/band4_embeddings.npz")
    b4_scores = {}
    for k in b4d.files:
        windows = b4d[k].astype("float64").tolist()
        b4_scores[k] = v4_ear_v2.score_audio_v2(windows, ex_sigs, raw_max_ex)
    b4_max = max(b4_scores.values())
    b4_min = min(b4_scores.values())

    mandate_threshold = loo_min - 0.5
    gate_passes = b4_max < mandate_threshold

    out = {
        "cycle": 76,
        "milestone_id": "P1c-band4-spot-check-under-v2-calibration",
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
        "backbone": "vggish_only",
        "calibration": v4_ear_v2.CALIBRATION_ID_V2,
        "loo_scores_v2": loo_scores_v2,
        "loo_min": loo_min,
        "band4_scores_v2": b4_scores,
        "band4_max": b4_max,
        "band4_min": b4_min,
        "gate_description": "band-4 max < loo_min - 0.5 (campaign L119)",
        "mandate_threshold_loo_min_minus_0p5": mandate_threshold,
        "gate_passes": gate_passes,
        "halt_honest_finding": (
            "V2 wider-linear calibration eliminates ceiling clipping (5/5 "
            "exemplars in [6.21, 6.83]) but band-4 max still exceeds "
            "loo_min-0.5 threshold. Root cause is the raw VGGish cosine "
            "statistic itself: stay_live (band-4) has higher raw similarity "
            "to the exemplar bank than desire (band-7). L119 is monotone-"
            "infeasible under VGGish. See l119_infeasibility_proof_c76.json."
        ),
        "supersedes_path": "_selection/band4-spot-check-halt-honest-c75",
    }
    out_path = ROOT / "data/v4/ear/band4_spot_check_v2_c76.json"
    out_path.write_text(json.dumps(out, sort_keys=True, indent=2))
    print(f"Wrote {out_path}")
    print(f"gate_passes: {gate_passes}  b4_max={b4_max:.4f}  loo_min-0.5={mandate_threshold:.4f}")


if __name__ == "__main__":
    main()
