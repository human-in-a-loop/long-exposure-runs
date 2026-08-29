#!/usr/bin/env python3
# Interpreter guard: /usr/bin/python3.
"""Enumerate the three orthogonal feasibility axes into axes.tsv.

Analytical / deterministic / no live network / no PRNG. Consumes read-only
snapshots of ratings_manifest.tsv and egress_status.jsonl only via document
references — no import of harvest/ingestion runtime paths.

Emits: data/corpus_expansion_plan/axes.tsv
"""
from __future__ import annotations

import csv
import os
import sys
from typing import Iterable

# Startup banner (c43 CLI-Startup-Silence interdiction).
print("[enumerate_axes] c48 Branch B — enumerating 3 feasibility axes.", file=sys.stderr)


AXES_HEADER = [
    "axis",
    "id",
    "name",
    "owner",
    "expected_outcome",
    "trigger_condition",
    "cost_hours_analytical",
    "cost_hours_operator_dependent",
    "expected_corpus_delta_lo",
    "expected_corpus_delta_hi",
    "expected_sb1_delta",
    "expected_sb2_delta",
    "expected_sb3_delta",
]


def axis_i_egress_unblock() -> list[dict]:
    """Axis (i): egress unblock — yt-dlp version + alt-CDN + policy-doc drafts."""
    return [
        {
            "axis": "i",
            "id": "i.1",
            "name": "yt-dlp version probe (analytical)",
            "owner": "researcher",
            "expected_outcome": "docs/corpus_expansion_plan/ytdlp_version_probe.md documenting current pinned yt-dlp version vs upstream release history diff; identifies whether a version bump would address tv_embedded closure",
            "trigger_condition": "on-disk yt-dlp version < upstream release with commit-message match tv_embedded|player_client|429",
            "cost_hours_analytical": 0.5,
            "cost_hours_operator_dependent": "0",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 37,
            "expected_sb1_delta": "conditional_on_delivery",
            "expected_sb2_delta": "conditional_on_delivery",
            "expected_sb3_delta": "conditional_on_delivery",
        },
        {
            "axis": "i",
            "id": "i.2",
            "name": "alternative CDN characterization",
            "owner": "researcher",
            "expected_outcome": "docs/corpus_expansion_plan/ytcdn_alt_shard_map.md enumerating googlevideo.com / googleusercontent.com / rr*.sn-* alt shards as fallback surface characterization",
            "trigger_condition": "data/ingestion/egress_status.jsonl shows >= 3 consecutive failures on same CDN sub-shard",
            "cost_hours_analytical": 0.5,
            "cost_hours_operator_dependent": "0",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 15,
            "expected_sb1_delta": "conditional_on_delivery",
            "expected_sb2_delta": "conditional_on_delivery",
            "expected_sb3_delta": "conditional_on_delivery",
        },
        {
            "axis": "i",
            "id": "i.3",
            "name": "workspace policy documentation draft",
            "owner": "worker",
            "expected_outcome": "docs/workspace_egress_policy_request.md explaining the c45 -> c47 registered failure sub-class + rationale for policy review",
            "trigger_condition": "policy_change_present = absent after >= 5 cycles of periodic probing",
            "cost_hours_analytical": 1.0,
            "cost_hours_operator_dependent": "unbounded",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 37,
            "expected_sb1_delta": "conditional_on_delivery",
            "expected_sb2_delta": "conditional_on_delivery",
            "expected_sb3_delta": "conditional_on_delivery",
        },
    ]


def axis_ii_alternative_sources() -> list[dict]:
    """Axis (ii): alternative sources — manual seed / friend tunnel / operator delivery."""
    return [
        {
            "axis": "ii",
            "id": "ii.1",
            "name": "manual seed alternative (operator handoff protocol)",
            "owner": "operator",
            "expected_outcome": "docs/corpus_expansion_plan/operator_handoff_protocol.md documenting the c36 43-song operator-delivered corpus precedent + protocol reuse for the 37-song gap",
            "trigger_condition": "operator_confirms_seeds_available = confirmed AND count >= 37",
            "cost_hours_analytical": 1.0,
            "cost_hours_operator_dependent": "1-4",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 37,
            "expected_sb1_delta": "conditional_on_delivery",
            "expected_sb2_delta": "conditional_on_delivery",
            "expected_sb3_delta": "conditional_on_delivery",
        },
        {
            "axis": "ii",
            "id": "ii.2",
            "name": "friend-of-workspace tunnel (rating-band-equivalent alternative corpus)",
            "owner": "researcher",
            "expected_outcome": "docs/corpus_expansion_plan/alt_corpus_fetchability.md scoring Freesound.org public-domain + Free Music Archive community-rated subsets on band-distribution substitutability (target: within +/- 2 songs per band vs current 10/10/13/10)",
            "trigger_condition": "alt_corpus_band_dist_within_2 = present AND fetchable = available",
            "cost_hours_analytical": 1.0,
            "cost_hours_operator_dependent": "0",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 40,
            "expected_sb1_delta": "conditional_on_delivery",
            "expected_sb2_delta": "conditional_on_delivery",
            "expected_sb3_delta": "conditional_on_delivery",
        },
        {
            "axis": "ii",
            "id": "ii.3",
            "name": "upstream operator delivery-cadence probe",
            "owner": "worker",
            "expected_outcome": "data/corpus_expansion_plan/operator_cadence.tsv enumerating c36 -> c47 corpus-count trajectory (43 -> 43 -> 43 -> 43); cadence verdict: stable at 43",
            "trigger_condition": "operator_delivers_new_rated_song >= 1 since c47 close",
            "cost_hours_analytical": 1.0,
            "cost_hours_operator_dependent": "0",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 37,
            "expected_sb1_delta": "conditional_on_delivery",
            "expected_sb2_delta": "conditional_on_delivery",
            "expected_sb3_delta": "conditional_on_delivery",
        },
    ]


def axis_iii_partial_corpus_interpolation() -> list[dict]:
    """Axis (iii): partial-corpus interpolation — analytical N-required projection under c26 fix-lock."""
    return [
        {
            "axis": "iii",
            "id": "iii.1",
            "name": "SB1 margin projection under c26-frozen chassis",
            "owner": "worker",
            "expected_outcome": "data/corpus_expansion_plan/partial_corpus_projection.json[.sb1] with kappa derived from c36 v0 -> c38 v1 -> c45 v2 trajectory + N-required to reach margin > 0.5909",
            "trigger_condition": "kappa_sb1_derivable_from_c36_c38_c45 = present AND monotonic_in_N = confirmed",
            "cost_hours_analytical": 1.0,
            "cost_hours_operator_dependent": "0",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 0,
            "expected_sb1_delta": "positive",
            "expected_sb2_delta": "neutral",
            "expected_sb3_delta": "neutral",
        },
        {
            "axis": "iii",
            "id": "iii.2",
            "name": "SB2 tau projection under c26-frozen chassis",
            "owner": "worker",
            "expected_outcome": "data/corpus_expansion_plan/partial_corpus_projection.json[.sb2] with N-required to reach mean tau >= 0.4 OR honest INSUFFICIENT_CONVERGENCE_ANALYSIS if trajectory non-monotonic",
            "trigger_condition": "sb2_trajectory_monotonic_in_N = confirmed OR INSUFFICIENT_CONVERGENCE_ANALYSIS = present",
            "cost_hours_analytical": 1.0,
            "cost_hours_operator_dependent": "0",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 0,
            "expected_sb1_delta": "neutral",
            "expected_sb2_delta": "positive",
            "expected_sb3_delta": "neutral",
        },
        {
            "axis": "iii",
            "id": "iii.3",
            "name": "SB3 detection + FPR projection under c26-frozen chassis",
            "owner": "worker",
            "expected_outcome": "data/corpus_expansion_plan/partial_corpus_projection.json[.sb3] with honest sensitivity note: SB3 is corpus-invariant at chassis level (c22/c23/c25 anti-pattern lockout); denominator widening at 50 controls per c46 dominates FPR",
            "trigger_condition": "sb3_denominator_widened_to_50 = present AND fpr_boundary_documented = confirmed",
            "cost_hours_analytical": 1.0,
            "cost_hours_operator_dependent": "0",
            "expected_corpus_delta_lo": 0,
            "expected_corpus_delta_hi": 0,
            "expected_sb1_delta": "neutral",
            "expected_sb2_delta": "neutral",
            "expected_sb3_delta": "neutral",
        },
    ]


def all_rows() -> list[dict]:
    return axis_i_egress_unblock() + axis_ii_alternative_sources() + axis_iii_partial_corpus_interpolation()


def write_tsv(rows: Iterable[dict], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=AXES_HEADER, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            # Enforce deterministic key ordering; every row must have every field.
            missing = [k for k in AXES_HEADER if k not in r]
            if missing:
                raise ValueError(f"row {r.get('id')!r} missing fields: {missing}")
            w.writerow({k: r[k] for k in AXES_HEADER})


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    out_path = argv[0] if argv else "data/corpus_expansion_plan/axes.tsv"
    rows = all_rows()
    write_tsv(rows, out_path)
    print(f"[enumerate_axes] wrote {len(rows)} rows -> {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
