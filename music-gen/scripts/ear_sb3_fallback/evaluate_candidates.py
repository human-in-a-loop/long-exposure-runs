#!/usr/bin/env python3
"""Evaluate F1/F2/F3 against the frozen rubric.

Produces:
    data/ear_sb3_fallback/per_candidate/<F>/summary.json
    data/ear_sb3_fallback/per_candidate/<F>/calibration.json
    data/ear_sb3_fallback/per_candidate/<F>/detection_alpha_1_0.jsonl
    data/ear_sb3_fallback/per_candidate/<F>/fpr_alpha_0.jsonl
    data/ear_sb3_fallback/per_candidate/<F>/stability_check.jsonl
    data/ear_sb3_fallback/comparison_matrix.tsv
    data/ear_sb3_fallback/verdict.json
"""
from __future__ import annotations

import decimal
import hashlib
import json
import pathlib
import sys
from typing import Callable

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"Interpreter guard: expected /usr/bin/python3, got {sys.executable}"
    )

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))  # workspace root

from scripts.ear_sb3_fallback.fixture_generators import (  # noqa: E402
    generate_fixture,
    residuals,
    CORPUS_SIZES,
)
from scripts.ear_sb3_fallback.candidate_f1_pooled_variance import f1_statistic  # noqa: E402
from scripts.ear_sb3_fallback.candidate_f2_permutation import f2_statistic  # noqa: E402
from scripts.ear_sb3_fallback.candidate_f3_shrinkage import f3_statistic  # noqa: E402

DATA_DIR = pathlib.Path("data/ear_sb3_fallback")

CALIBRATION_SALTS = list(range(0, 20))
DETECTION_SALTS = list(range(100, 200))
STABILITY_SALTS = list(range(0, 100))


def _round12(x: float) -> str:
    """Round to 12 decimals as a byte-stable decimal string."""
    d = decimal.Decimal(x).quantize(decimal.Decimal("1E-12"))
    return f"{d:.12f}"


def _sha_scalar(x: float) -> str:
    return hashlib.sha256(_round12(x).encode()).hexdigest()


def _call(cand: str, res: list[float], ids: list[int], salt: int) -> float:
    if cand == "F1":
        return f1_statistic(res, ids)
    if cand == "F2":
        return f2_statistic(res, ids, salt=salt, k_perm=200)
    if cand == "F3":
        return f3_statistic(res, ids)
    raise ValueError(cand)


def _p90(xs: list[float]) -> float:
    ys = sorted(xs)
    n = len(ys)
    idx = int(0.90 * (n - 1))
    return ys[idx]


def _calibrate(cand: str, corpus: str) -> tuple[float, list[float]]:
    """Return (tau, no-leak stat samples). tau = 90th percentile."""
    stats = []
    for salt in CALIBRATION_SALTS:
        _, ids, pred, lab = generate_fixture(salt, corpus, 0.0)
        res = residuals(pred, lab)
        stats.append(_call(cand, res, ids, salt))
    return _p90(stats), stats


def _detection_rate(cand: str, corpus: str, alpha: float, tau: float) -> tuple[float, list[float]]:
    stats = []
    for salt in DETECTION_SALTS:
        _, ids, pred, lab = generate_fixture(salt, corpus, alpha)
        res = residuals(pred, lab)
        stats.append(_call(cand, res, ids, salt))
    hits = sum(1 for s in stats if s > tau)
    return hits / len(stats), stats


def _fpr(cand: str, corpus: str, tau: float) -> tuple[float, list[float]]:
    stats = []
    for salt in DETECTION_SALTS:
        _, ids, pred, lab = generate_fixture(salt, corpus, 0.0)
        res = residuals(pred, lab)
        stats.append(_call(cand, res, ids, salt))
    fp = sum(1 for s in stats if s > tau)
    return fp / len(stats), stats


def _stability_check(cand: str, corpus: str, alpha: float) -> tuple[bool, int]:
    """Byte-determinism SHA-256 equality across two independent regenerations."""
    mismatches = 0
    for salt in STABILITY_SALTS:
        _, ids1, p1, l1 = generate_fixture(salt, corpus, alpha)
        _, ids2, p2, l2 = generate_fixture(salt, corpus, alpha)
        assert ids1 == ids2 and p1 == p2 and l1 == l2, "fixture nondeterminism"
        s1 = _call(cand, residuals(p1, l1), ids1, salt)
        s2 = _call(cand, residuals(p2, l2), ids2, salt)
        if _sha_scalar(s1) != _sha_scalar(s2):
            mismatches += 1
    return mismatches == 0, mismatches


def evaluate_all() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for cand in ("F1", "F2", "F3"):
        per_dir = DATA_DIR / "per_candidate" / cand
        per_dir.mkdir(parents=True, exist_ok=True)

        cand_report = {"candidate": cand, "corpora": {}}

        for corpus in ("singleton_43", "repeat_55"):
            tau, cal_stats = _calibrate(cand, corpus)
            fpr_val, fpr_stats = _fpr(cand, corpus, tau)
            det_1_0, det_1_0_stats = _detection_rate(cand, corpus, 1.0, tau)
            det_0_5, det_0_5_stats = _detection_rate(cand, corpus, 0.5, tau)
            det_0_1, det_0_1_stats = _detection_rate(cand, corpus, 0.1, tau)

            cand_report["corpora"][corpus] = {
                "tau": tau,
                "calibration_stats_summary": {"n": len(cal_stats),
                                              "min": min(cal_stats),
                                              "max": max(cal_stats),
                                              "mean": sum(cal_stats)/len(cal_stats)},
                "fpr_alpha_0": fpr_val,
                "detection_alpha_1_0": det_1_0,
                "detection_alpha_0_5": det_0_5,
                "detection_alpha_0_1": det_0_1,
            }

            # Write out detection/fpr sample streams (subsample first 10 for
            # brevity + all summary stats).
            (per_dir / f"detection_alpha_1_0_{corpus}.jsonl").write_text(
                "\n".join(json.dumps({"salt": s, "stat": v}) for s, v in
                          zip(DETECTION_SALTS, det_1_0_stats)) + "\n"
            )
            (per_dir / f"fpr_alpha_0_{corpus}.jsonl").write_text(
                "\n".join(json.dumps({"salt": s, "stat": v}) for s, v in
                          zip(DETECTION_SALTS, fpr_stats)) + "\n"
            )

        # Stability: check on singleton at alpha=0 (100 salts).
        stab_ok, mism = _stability_check(cand, "singleton_43", 0.0)
        cand_report["stability_singleton"] = {"passed": stab_ok, "mismatches": mism, "n_salts": len(STABILITY_SALTS)}
        stab_ok_r, mism_r = _stability_check(cand, "repeat_55", 1.0)
        cand_report["stability_repeat"] = {"passed": stab_ok_r, "mismatches": mism_r, "n_salts": len(STABILITY_SALTS)}

        (per_dir / "summary.json").write_text(json.dumps(cand_report, indent=2, sort_keys=True))
        results[cand] = cand_report

    return results


def apply_rubric(results: dict) -> dict:
    """Apply the frozen 4-verdict rubric."""
    per_cand = {}
    for cand, r in results.items():
        rep = r["corpora"]["repeat_55"]
        sing = r["corpora"]["singleton_43"]
        t1 = rep["detection_alpha_1_0"] >= 0.90
        t2 = sing["fpr_alpha_0"] <= 0.10
        t3 = r["stability_singleton"]["passed"] and r["stability_repeat"]["passed"]
        agg = (rep["detection_alpha_1_0"]
               + (1.0 - sing["fpr_alpha_0"])
               + 0.5 * rep["detection_alpha_0_5"])
        per_cand[cand] = {
            "T1_detection_ge_0_90_repeat55": t1,
            "T2_fpr_le_0_10_singleton43": t2,
            "T3_stability": t3,
            "all_pass": t1 and t2 and t3,
            "aggregate_score": agg,
            "detection_alpha_1_0_repeat55": rep["detection_alpha_1_0"],
            "detection_alpha_0_5_repeat55": rep["detection_alpha_0_5"],
            "detection_alpha_0_1_repeat55": rep["detection_alpha_0_1"],
            "fpr_alpha_0_singleton43": sing["fpr_alpha_0"],
            "detection_alpha_1_0_singleton43": sing["detection_alpha_1_0"],
        }

    passing = [c for c, r in per_cand.items() if r["all_pass"]]
    if not passing:
        verdict = "NO_FALLBACK_QUALIFIES"
        chosen = None
    else:
        # Tiebreak by aggregate score, then alpha order.
        best = max(passing, key=lambda c: (per_cand[c]["aggregate_score"], -ord(c[1])))
        # per_cand[c]["aggregate_score"] descending, then alpha ascending.
        # Simplify:
        passing_sorted = sorted(passing, key=lambda c: (-per_cand[c]["aggregate_score"], c))
        chosen = passing_sorted[0]
        verdict = f"{chosen}_ADOPTED"

    rubric_hash = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    return {
        "verdict": verdict,
        "chosen_candidate": chosen,
        "rubric_hash": rubric_hash,
        "per_candidate": per_cand,
    }


def write_comparison_matrix(results: dict, verdict_report: dict) -> None:
    lines = ["candidate\tcorpus\ttau\tfpr_alpha_0\tdet_alpha_1_0\tdet_alpha_0_5\tdet_alpha_0_1\tT1_pass\tT2_pass\tT3_pass\taggregate_score\tall_pass"]
    for cand in ("F1", "F2", "F3"):
        r = results[cand]
        rep = r["corpora"]["repeat_55"]
        sing = r["corpora"]["singleton_43"]
        pc = verdict_report["per_candidate"][cand]
        # Row per corpus.
        for corpus in ("singleton_43", "repeat_55"):
            c = r["corpora"][corpus]
            lines.append(
                "\t".join([
                    cand,
                    corpus,
                    f"{c['tau']:.6f}",
                    f"{c['fpr_alpha_0']:.4f}",
                    f"{c['detection_alpha_1_0']:.4f}",
                    f"{c['detection_alpha_0_5']:.4f}",
                    f"{c['detection_alpha_0_1']:.4f}",
                    str(pc["T1_detection_ge_0_90_repeat55"]),
                    str(pc["T2_fpr_le_0_10_singleton43"]),
                    str(pc["T3_stability"]),
                    f"{pc['aggregate_score']:.6f}",
                    str(pc["all_pass"]),
                ])
            )
    (DATA_DIR / "comparison_matrix.tsv").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    results = evaluate_all()
    verdict = apply_rubric(results)
    write_comparison_matrix(results, verdict)
    (DATA_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))
    print(json.dumps(verdict, indent=2, sort_keys=True))
