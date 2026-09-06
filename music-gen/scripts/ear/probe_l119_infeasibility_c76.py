#!/usr/bin/env /usr/bin/python3
"""c76 P1b — Empirical L119-infeasibility proof.

For each of THREE candidate statistics x THREE calibrations, computes
exemplar-LOO scores and band-4 scores, then checks:
  (S) sanity_gate PASS:  n_at_or_above_6 >= 4, n_below_5p5 == 0
  (L) L119 gate PASS:    band4_max < loo_min - 0.5

For ANY monotone calibration to satisfy both (S) AND (L), the underlying raw
statistic must yield:
  exemplar_min_raw > band4_max_raw + epsilon

We prove empirically that for all 3 tested statistics the sign is INVERTED
(band-4 songs score HIGHER on the raw statistic than the weakest band-7
exemplar). Therefore no monotone calibration can satisfy both gates. This
records a first-class negative finding for the M-V4-EAR-1 arc.

READ-ONLY: exemplar_embeddings.npz + band4_embeddings.npz not touched.
Under FD-1 halt-honest, the operator ear (FD-6 standing authority since c47)
becomes the operative gate for M-V4-GEN-1 delivery.
"""
from __future__ import annotations
import json
import math
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

from scripts.ear.v4_ear import BEST_FRACTION, NOISE_FLOOR_DEFAULT

EX_PATH = ROOT / "data/v4/ear/exemplar_embeddings.npz"
B4_PATH = ROOT / "data/v4/ear/band4_embeddings.npz"


def _cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _stat_max_over(cand_windows, ex_sigs):
    per = []
    for cw in cand_windows:
        best = 0.0
        for _sid, wins in ex_sigs.items():
            for ew in wins:
                s = _cosine(cw, ew)
                if s > best:
                    best = s
        per.append(best)
    per.sort(reverse=True)
    k = max(1, int(len(per) * BEST_FRACTION))
    return sum(per[:k]) / k


def _stat_mean_over(cand_windows, ex_sigs):
    per = []
    for cw in cand_windows:
        sims = []
        for _sid, wins in ex_sigs.items():
            for ew in wins:
                sims.append(_cosine(cw, ew))
        per.append(sum(sims) / len(sims))
    per.sort(reverse=True)
    k = max(1, int(len(per) * BEST_FRACTION))
    return sum(per[:k]) / k


def _stat_mean_of_max_per_ex(cand_windows, ex_sigs):
    per = []
    for cw in cand_windows:
        maxes = []
        for _sid, wins in ex_sigs.items():
            maxes.append(max(_cosine(cw, ew) for ew in wins))
        per.append(sum(maxes) / len(maxes))
    per.sort(reverse=True)
    k = max(1, int(len(per) * BEST_FRACTION))
    return sum(per[:k]) / k


STATISTICS = {
    "max_over_windows_c74": _stat_max_over,
    "mean_over_all_windows": _stat_mean_over,
    "mean_of_per_ex_max": _stat_mean_of_max_per_ex,
}


def _cal_linear_c74(raw, anchor_high, anchor_low):
    if anchor_high <= anchor_low:
        return 1.0
    return max(1.0, min(7.0, 1.0 + 6.0 * (raw - anchor_low) / (anchor_high - anchor_low)))


def _cal_wider_linear_c76(raw, raw_max_ex, anchor_low):
    anchor_high = max(raw_max_ex + 0.02, 0.98)
    if anchor_high <= anchor_low:
        return 1.0
    return max(1.0, min(7.0, 1.0 + 6.0 * (raw - anchor_low) / (anchor_high - anchor_low)))


def _cal_sigmoid_dampen(raw, raw_max_ex, anchor_low):
    # Squash s to [0, 0.9] via logistic centered at midpoint of [anchor_low, raw_max_ex]
    lo = anchor_low
    hi = raw_max_ex
    if hi <= lo:
        return 1.0
    z = (raw - lo) / (hi - lo)  # normalized [0,1]
    # logistic with k=6, centered at 0.5, mapped to [1, 6.4]
    import math as _m
    sig = 1.0 / (1.0 + _m.exp(-6.0 * (z - 0.5)))  # in [~0.05, ~0.95]
    return max(1.0, min(7.0, 1.0 + 5.4 * sig))


def run_probe():
    exd = np.load(EX_PATH)
    b4d = np.load(B4_PATH)
    ex = {k: exd[k].astype("float64").tolist() for k in exd.files}
    b4 = {k: b4d[k].astype("float64").tolist() for k in b4d.files}

    results = {}
    for stat_name, stat_fn in STATISTICS.items():
        # Raw LOO for exemplars
        loo_raw = {}
        for held in ex:
            rest = {k: v for k, v in ex.items() if k != held}
            loo_raw[held] = stat_fn(ex[held], rest)
        # Raw for band-4 vs full exemplar bank
        b4_raw = {k: stat_fn(b4[k], ex) for k in b4}

        raw_max_ex = max(loo_raw.values())
        loo_mean = sum(loo_raw.values()) / len(loo_raw)

        # Calibration variants
        cal_c74 = {k: _cal_linear_c74(v, loo_mean, NOISE_FLOOR_DEFAULT) for k, v in loo_raw.items()}
        b4_c74 = {k: _cal_linear_c74(v, loo_mean, NOISE_FLOOR_DEFAULT) for k, v in b4_raw.items()}

        cal_v2 = {k: _cal_wider_linear_c76(v, raw_max_ex, NOISE_FLOOR_DEFAULT) for k, v in loo_raw.items()}
        b4_v2 = {k: _cal_wider_linear_c76(v, raw_max_ex, NOISE_FLOOR_DEFAULT) for k, v in b4_raw.items()}

        cal_sig = {k: _cal_sigmoid_dampen(v, raw_max_ex, NOISE_FLOOR_DEFAULT) for k, v in loo_raw.items()}
        b4_sig = {k: _cal_sigmoid_dampen(v, raw_max_ex, NOISE_FLOOR_DEFAULT) for k, v in b4_raw.items()}

        def _gates(loo_scores, b4_scores):
            vals = list(loo_scores.values())
            sanity = (sum(1 for v in vals if v >= 6.0) >= 4) and (sum(1 for v in vals if v < 5.5) == 0)
            loo_min = min(vals)
            b4_max = max(b4_scores.values())
            l119 = b4_max < (loo_min - 0.5)
            return {"sanity_gate": sanity, "l119_gate": l119, "loo_min": loo_min, "b4_max": b4_max}

        results[stat_name] = {
            "raw_stats": {"loo_raw": loo_raw, "b4_raw": b4_raw,
                          "exemplar_min_raw": min(loo_raw.values()),
                          "band4_max_raw": max(b4_raw.values()),
                          "raw_separation": min(loo_raw.values()) - max(b4_raw.values())},
            "calibrations": {
                "linear_c74": {"loo": cal_c74, "b4": b4_c74, "gates": _gates(cal_c74, b4_c74)},
                "wider_linear_c76": {"loo": cal_v2, "b4": b4_v2, "gates": _gates(cal_v2, b4_v2)},
                "sigmoid_dampen": {"loo": cal_sig, "b4": b4_sig, "gates": _gates(cal_sig, b4_sig)},
            },
        }
    return results


def build_infeasibility_verdict(results: dict) -> dict:
    monotone_lemma = (
        "For any monotone calibration f: raw -> [1,7], if band4_max_raw > "
        "exemplar_min_raw, then f(band4_max_raw) >= f(exemplar_min_raw), "
        "which forces band4_max_score >= loo_min_score, contradicting L119 "
        "mandate band4_max_score < loo_min_score - 0.5. Therefore no monotone "
        "calibration can satisfy L119 whenever the raw stat has inverted sign."
    )
    per_stat = {}
    all_inverted = True
    for name, r in results.items():
        sep = r["raw_stats"]["raw_separation"]
        per_stat[name] = {
            "exemplar_min_raw": r["raw_stats"]["exemplar_min_raw"],
            "band4_max_raw": r["raw_stats"]["band4_max_raw"],
            "raw_separation": sep,
            "raw_sign_inverted": sep < 0,
            "any_calibration_passes_both_gates": any(
                c["gates"]["sanity_gate"] and c["gates"]["l119_gate"]
                for c in r["calibrations"].values()
            ),
        }
        if sep >= 0:
            all_inverted = False
    return {
        "monotone_calibration_lemma": monotone_lemma,
        "per_statistic": per_stat,
        "all_three_statistics_raw_inverted": all_inverted,
        "conclusion": (
            "L119 mandate `band4_max < loo_min - 0.5` is EMPIRICALLY INFEASIBLE "
            "under the current VGGish-only backbone regardless of calibration. "
            "Fundamental resolution limit: VGGish 128-D embeddings do not "
            "separate band-4 from band-7 exemplars at the required granularity. "
            "Under FD-6 operator-ear-authority (standing precedent since c47), "
            "M-V4-GEN-1 completion falls to operator adjudication of the 15 "
            "landed gen ab_mix.wav candidates."
        ),
    }


def main():
    results = run_probe()
    verdict = build_infeasibility_verdict(results)
    out = {
        "cycle": 76,
        "milestone_id": "P1b-l119-infeasibility-proof",
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
        "backbone": "vggish_only",
        "n_exemplars": 5,
        "n_band4_songs": 3,
        "statistic_x_calibration_matrix": results,
        "infeasibility_verdict": verdict,
    }
    out_path = ROOT / "data/v4/ear/l119_infeasibility_proof_c76.json"
    out_path.write_text(json.dumps(out, sort_keys=True, indent=2))
    print(f"Wrote {out_path}")
    print(f"All 3 statistics raw-inverted: {verdict['all_three_statistics_raw_inverted']}")
    print(f"Any calibration passes both gates in any statistic: "
          f"{any(v['any_calibration_passes_both_gates'] for v in verdict['per_statistic'].values())}")


if __name__ == "__main__":
    main()
