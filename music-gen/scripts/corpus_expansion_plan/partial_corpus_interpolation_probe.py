#!/usr/bin/env python3
# Interpreter guard: /usr/bin/python3.
"""Analytical N-required projection under c26-frozen chassis.

No re-training. No rendering. No live network. No PRNG. Consumes only
in-source constants derived from prior-cycle verdict.json snapshots and
c26 pre-registered thresholds. Model is a first-order per-song
sensitivity kappa linear regression on the (N, observed) trajectory:

    margin(N) = margin(N_ref) + kappa * (N - N_ref)

If kappa is not monotonically-signed toward the threshold across the three
observation points (c36 v0 N=43, c38 v1 N=43, c45 v2 N=43), the projection
returns INSUFFICIENT_CONVERGENCE_ANALYSIS honestly.

Emits: data/corpus_expansion_plan/partial_corpus_projection.json
"""
from __future__ import annotations

import json
import os
import sys

# Startup banner (c43 CLI-Startup-Silence interdiction).
print("[partial_corpus_interpolation_probe] c48 Branch B — analytical N-required projection under c26 fix-lock.", file=sys.stderr)


# --- c26 frozen thresholds (per docs/ear_path_b_commitment.md §3) -----------
C26_SB1_MARGIN_PASS_THRESHOLD = 0.5909090909  # frozen IQR
C26_SB2_TAU_PASS_THRESHOLD = 0.4              # frozen
# SB3: detection >= 0.90 at alpha=1.0 AND FPR <= 0.10
C26_SB3_DETECTION_PASS = 0.90
C26_SB3_FPR_PASS = 0.10


# --- Observation series (READ-ONLY reference; do NOT modify) -----------------
# c36 v0 EAR_v0_INSUFFICIENT, c38 v1 EAR_v1_PARTIAL, c45 v2 EAR_v2_PARTIAL.
# All three under the SAME chassis (c6 CORN 1-7 head + c6 features + c22 harness);
# only methodology hardening differs. All three sit at N=43 rated songs on disk.
# The SB1 margin -0.2093 value is per c46 mapping-clarified paragraph relative
# to the c38 v1 baseline; it is an IMPROVEMENT-clause value, NOT a PASS
# threshold and is negative because CORN MAE at v2 is greater than the harder
# baseline min(majority, mean_integer)=0.6250 by a margin of ~0.21.
SB1_TRAJECTORY = [
    {"cycle": 36, "N": 43, "verdict": "EAR_v0_INSUFFICIENT", "margin_observed_or_placeholder": None,
     "note": "c36 v0 recorded no SB1 margin - INSUFFICIENT verdict fired on chassis instability, not on margin computation."},
    {"cycle": 38, "N": 43, "verdict": "EAR_v1_PARTIAL", "margin_observed_or_placeholder": 0.0,
     "note": "c38 v1 EAR_v1_PARTIAL baseline; margin used as improvement anchor for c45 delta."},
    {"cycle": 45, "N": 43, "verdict": "EAR_v2_PARTIAL", "margin_observed_or_placeholder": -0.2093,
     "note": "c45 v2 SB1 margin delta vs c38 v1 baseline per c46 mapping-clarified."},
]

SB2_TRAJECTORY = [
    {"cycle": 36, "N": 43, "verdict": "EAR_v0_INSUFFICIENT", "mean_tau_placeholder": None},
    {"cycle": 38, "N": 43, "verdict": "EAR_v1_PARTIAL", "mean_tau_placeholder": 0.0},
    {"cycle": 45, "N": 43, "verdict": "EAR_v2_PARTIAL", "mean_tau_placeholder": -0.0314,
     "note": "c45 v2 SB2 mean tau delta_vs_v1 improvement axis per c46."},
]

SB3_STATE = {
    "detection_at_alpha_1_0": 1.000,
    "fpr_at_denominator_50": 0.100,
    "denominator": 50,
    "note": "c47 v2.1 confirmed detection PASS 1.000 stable + FPR=0.100 at 50-ctl boundary; corpus-invariant at chassis level per c22/c23/c25 anti-pattern lockouts.",
}


def _project_sb1() -> dict:
    """SB1: derive kappa from c38 -> c45 delta; extrapolate to PASS threshold."""
    observed = [(t["N"], t["margin_observed_or_placeholder"]) for t in SB1_TRAJECTORY if t["margin_observed_or_placeholder"] is not None]
    # All observations are at N=43. Linear extrapolation is under-identified.
    unique_N = {n for n, _ in observed}
    if len(unique_N) < 2:
        return {
            "verdict": "INSUFFICIENT_CONVERGENCE_ANALYSIS",
            "reason": "All three verdict observations sit at N=43; kappa (per-song margin sensitivity) is not identifiable from the trajectory. Extrapolation to N required to cross margin > 0.5909 requires at least one additional N observation.",
            "current_margin_v2": -0.2093,
            "target_threshold": C26_SB1_MARGIN_PASS_THRESHOLD,
            "observations_summary": observed,
            "recommended_probe": "Re-run v2 chassis at N=80 (post corpus-expansion delivery) to enable a two-point kappa estimate; N=80 is the c26 pre-registered target so this trigger is naturally aligned with the corpus-expansion axis (ii).",
        }
    # Two distinct N values -> compute kappa. (Unreachable in current data.)
    n0, m0 = observed[0]
    n1, m1 = observed[-1]
    kappa = (m1 - m0) / (n1 - n0)
    if kappa <= 0:
        return {
            "verdict": "INSUFFICIENT_CONVERGENCE_ANALYSIS",
            "reason": "kappa non-positive; more songs would not close the margin gap under linear model.",
            "kappa": kappa,
        }
    required_delta = (C26_SB1_MARGIN_PASS_THRESHOLD - m1) / kappa
    n_required = int(n1 + required_delta + 0.999)
    return {
        "verdict": "PROJECTED",
        "kappa": kappa,
        "n_required": n_required,
        "target_threshold": C26_SB1_MARGIN_PASS_THRESHOLD,
    }


def _project_sb2() -> dict:
    """SB2: same story - single observed N -> under-identified."""
    observed = [(t["N"], t["mean_tau_placeholder"]) for t in SB2_TRAJECTORY if t.get("mean_tau_placeholder") is not None]
    unique_N = {n for n, _ in observed}
    if len(unique_N) < 2:
        return {
            "verdict": "INSUFFICIENT_CONVERGENCE_ANALYSIS",
            "reason": "All observed SB2 measurements sit at N=43; per-song tau sensitivity is not identifiable without a second N observation. The c26 SB2 threshold (mean tau >= 0.4) is far from the c45 v2 baseline (-0.0314); a naive linear extrapolation would require a large N delta but has no support in the data.",
            "current_mean_tau_v2": -0.0314,
            "target_threshold": C26_SB2_TAU_PASS_THRESHOLD,
            "observations_summary": observed,
            "recommended_probe": "Two-point kappa needs re-run at delivered N > 43; naturally paired with corpus-expansion axis (ii). If tau still negative at N=80, honest response per c26 §5 is to publish corpus-expansion-ticket instantiation with the observed value, not to redesign chassis.",
        }
    n0, t0 = observed[0]
    n1, t1 = observed[-1]
    kappa = (t1 - t0) / (n1 - n0)
    if kappa <= 0:
        return {
            "verdict": "INSUFFICIENT_CONVERGENCE_ANALYSIS",
            "reason": "kappa non-positive; more songs would not close tau gap under linear model.",
            "kappa": kappa,
        }
    required_delta = (C26_SB2_TAU_PASS_THRESHOLD - t1) / kappa
    n_required = int(n1 + required_delta + 0.999)
    return {
        "verdict": "PROJECTED",
        "kappa": kappa,
        "n_required": n_required,
        "target_threshold": C26_SB2_TAU_PASS_THRESHOLD,
    }


def _project_sb3() -> dict:
    """SB3: corpus-invariant at chassis level; FPR dominated by denominator widening (c46)."""
    detection = SB3_STATE["detection_at_alpha_1_0"]
    fpr = SB3_STATE["fpr_at_denominator_50"]
    detection_pass = detection >= C26_SB3_DETECTION_PASS
    fpr_pass = fpr <= C26_SB3_FPR_PASS  # boundary equality counts as pass
    if detection_pass and fpr_pass:
        note = "SB3 already at boundary PASS under c47 v2.1 stability (FPR=0.100 exactly). Additional corpus growth is expected to widen the FPR margin as the leak-detector denominator grows; qualitative direction: neutral-to-positive. No re-training required to observe this."
        verdict = "PROJECTED_ALREADY_AT_BOUNDARY_PASS"
    else:
        note = "SB3 not at PASS in observed state."
        verdict = "INSUFFICIENT_CONVERGENCE_ANALYSIS"
    return {
        "verdict": verdict,
        "detection_observed": detection,
        "fpr_observed": fpr,
        "denominator": SB3_STATE["denominator"],
        "target_detection_threshold": C26_SB3_DETECTION_PASS,
        "target_fpr_threshold": C26_SB3_FPR_PASS,
        "note": note,
        "corpus_invariance_note": SB3_STATE["note"],
    }


def project_all() -> dict:
    return {
        "c26_thresholds_frozen": {
            "sb1_margin_pass": C26_SB1_MARGIN_PASS_THRESHOLD,
            "sb2_tau_pass": C26_SB2_TAU_PASS_THRESHOLD,
            "sb3_detection_pass": C26_SB3_DETECTION_PASS,
            "sb3_fpr_pass": C26_SB3_FPR_PASS,
        },
        "chassis_fix_lock": "c26 chassis (c6 CORN 1-7 head + c6 features + c22 harness) UNCHANGED; axis (iii) projects N-required only.",
        "corpus_state": {"on_disk_songs": 43, "target": 80, "gap": 37},
        "sb1": _project_sb1(),
        "sb2": _project_sb2(),
        "sb3": _project_sb3(),
        "methodology": "First-order kappa: margin(N) = margin(N_ref) + kappa * (N - N_ref). All three prior observations sit at N=43, so SB1 and SB2 return INSUFFICIENT_CONVERGENCE_ANALYSIS - honest under-identification, not a redesign trigger. SB3 is corpus-invariant at chassis level (c22/c23/c25 anti-pattern lockouts) and already at boundary PASS under c47 v2.1 stability.",
    }


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    out_path = argv[0] if argv else "data/corpus_expansion_plan/partial_corpus_projection.json"
    projection = project_all()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(projection, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"[partial_corpus_interpolation_probe] wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
