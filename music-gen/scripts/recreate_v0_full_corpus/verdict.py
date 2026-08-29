#!/usr/bin/python3
# ---
# created: 2026-08-29T12:25:00Z
# cycle: 39
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/full-corpus-recreation
# fork: c320de981fda
# clone: 0
# ---
"""Verdict resolver for M-RECREATE-1/full-corpus-recreation.

Reads all_results.json + anchor_preservation.json, applies the frozen
3-verdict rubric (FULL_CORPUS_LANDS / FULL_CORPUS_PARTIAL /
FULL_CORPUS_FAILS), writes verdict.json with rubric_hash embedded,
per-band positive-mel-delta counts, and per-song attribution for
non-LANDS outcomes.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "data" / "recreate_v0_full_corpus"
RUBRIC_HASH = (DATA_ROOT / "rubric_hash.txt").read_text().strip()


def _mel_delta(r: dict) -> float | None:
    p = r.get("panels", {})
    pb = p.get("original_vs_bare", {}) or {}
    pe = p.get("original_vs_effects", {}) or {}
    b, e = pb.get("mel_l1_db"), pe.get("mel_l1_db")
    if isinstance(b, (int, float)) and isinstance(e, (int, float)):
        return b - e
    return None


def main() -> int:
    results = json.loads((DATA_ROOT / "all_results.json").read_text())
    anchor_pres = json.loads((DATA_ROOT / "anchor_preservation.json").read_text())
    anchors_unchanged = bool(anchor_pres.get("unchanged"))

    n = len(results)
    per_song_findings = []
    per_band_positive: Counter = Counter()
    per_band_total: Counter = Counter()
    per_band_pipeline_ok: Counter = Counter()
    per_band_byte_det_ok: Counter = Counter()

    n_pipeline_ok = 0
    n_byte_det_ok = 0
    n_positive_delta = 0
    n_mel_delta_computable = 0
    n_early_exit = 0
    per_anchor_failures = []

    for r in results:
        band = r["band"]
        per_band_total[band] += 1
        pipeline_ok = (r.get("run1_failed_stage") is None)
        if pipeline_ok:
            n_pipeline_ok += 1
            per_band_pipeline_ok[band] += 1
        if r.get("run1_failed_stage") == "early_exit:wall_clock_exceeded":
            n_early_exit += 1

        det_ok = r.get("determinism", {}).get("all_deterministic_anchors_equal", False)
        if det_ok:
            n_byte_det_ok += 1
            per_band_byte_det_ok[band] += 1
        else:
            # Log per-anchor failures for the failing songs
            per_anchor = r.get("determinism", {}).get("per_anchor", {}) or {}
            for anchor, det in per_anchor.items():
                if not det.get("equal", False):
                    per_anchor_failures.append({
                        "song_sha16": r["sha16"], "band": band,
                        "anchor": anchor,
                        "run1_sha": det.get("run1"),
                        "run2_sha": det.get("run2"),
                    })

        d = _mel_delta(r)
        if d is not None:
            n_mel_delta_computable += 1
            if d > 0:
                n_positive_delta += 1
                per_band_positive[band] += 1

        per_song_findings.append({
            "canonical_index": r.get("canonical_index"),
            "band": band, "sha16": r["sha16"],
            "relpath": r["relpath"],
            "run1_failed_stage": r.get("run1_failed_stage"),
            "run1_wall_clock_s": r.get("run1_wall_clock_s"),
            "run2_wall_clock_s": r.get("run2_wall_clock_s"),
            "byte_det_x2": det_ok,
            "mel_l1_db_delta_bare_minus_effects": d,
            "delta_positive": (d is not None and d > 0),
        })

    n_pipeline_fail = n - n_pipeline_ok
    n_byte_det_fail = n - n_byte_det_ok
    n_mel_delta_fail = n_mel_delta_computable - n_positive_delta

    # Rubric decision
    lands_threshold = 33  # ceil(0.89 * 37)
    if n_pipeline_fail > 4 or n_byte_det_fail > 5 or n_mel_delta_fail > 4:
        verdict = "FULL_CORPUS_FAILS"
        reason = (f"pipeline_fail={n_pipeline_fail} (>4) OR "
                  f"byte_det_fail={n_byte_det_fail} (>5) OR "
                  f"mel_delta_fail={n_mel_delta_fail} (>4)")
    elif (n_pipeline_ok == n and n_byte_det_ok == n and
          n_positive_delta >= lands_threshold):
        verdict = "FULL_CORPUS_LANDS"
        reason = (f"{n}/{n} pipeline OK, {4*n}/{4*n} byte-det anchors, "
                  f"{n_positive_delta}/{n} positive mel delta (>={lands_threshold} threshold)")
    else:
        verdict = "FULL_CORPUS_PARTIAL"
        reason = (f"pipeline_ok={n_pipeline_ok}/{n}; byte_det_ok={n_byte_det_ok}/{n}; "
                  f"positive_mel_delta={n_positive_delta}/{n} "
                  f"(LANDS requires 37/37 + 148/148 + >={lands_threshold})")

    per_band_summary = {}
    for band in sorted(per_band_total.keys()):
        per_band_summary[str(band)] = {
            "n_total": per_band_total[band],
            "n_pipeline_ok": per_band_pipeline_ok[band],
            "n_byte_det_ok": per_band_byte_det_ok[band],
            "n_positive_mel_delta": per_band_positive[band],
        }

    payload = {
        "verdict": verdict,
        "reason": reason,
        "n_songs": n,
        "n_pipeline_ok": n_pipeline_ok,
        "n_pipeline_fail": n_pipeline_fail,
        "n_byte_det_x2_ok": n_byte_det_ok,
        "n_byte_det_x2_fail": n_byte_det_fail,
        "n_byte_det_anchors_total": 4 * n,
        "n_byte_det_anchors_ok": 4 * n - len(per_anchor_failures),
        "n_positive_mel_delta": n_positive_delta,
        "n_mel_delta_computable": n_mel_delta_computable,
        "n_mel_delta_fail": n_mel_delta_fail,
        "n_early_exit": n_early_exit,
        "per_band_summary": per_band_summary,
        "per_song_findings": per_song_findings,
        "per_anchor_byte_det_failures": per_anchor_failures,
        "anchors_unchanged": anchors_unchanged,
        "rubric_hash": RUBRIC_HASH,
        "rubric_verdicts": ["FULL_CORPUS_LANDS", "FULL_CORPUS_PARTIAL",
                            "FULL_CORPUS_FAILS"],
        "lands_threshold_positive_mel_delta": lands_threshold,
        "milestone": "M-RECREATE-1/full-corpus-recreation",
        "fork": "c320de981fda",
        "clone": 0,
        "cycle": 39,
        "run_id": "run-2026-08-28T040704Z",
    }
    (DATA_ROOT / "verdict.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"[verdict] {verdict} — {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
