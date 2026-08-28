#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:30:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 855d4c2e9945)
# milestone: M-GEN-1/collision-floor-investigation
# ---
"""Cluster verdict: structural vs hash-geometric mechanism.

For each rule_type, computes:
  1. Birthday-paradox baseline: expected pairs at N=8 given K rules.
  2. Observed pair count from attribution.
  3. Per-rule pick frequency across the 8 salts (via sampler).
  4. Tight-cluster identification: rules whose pairwise structural distance
     ≤ (median − 1σ) form a cluster.
  5. For each collision-contributor rule, structural neighbor analysis:
     - Its nearest structural neighbors under the distance metric.
     - Whether the collision is a "same rule picked multiply" (dominant-rule)
       or a "different similar rules colliding" (cluster-driven) pattern.

Verdict per rule_type is one of:
  - hash_geometric        : observed ≈ BP baseline; picks spread; no dominant rule
  - dominant_rule         : one rule captures ≥ 3 salts (small-K over-selection)
  - structural_cluster    : multiple similar-but-not-identical rules cluster
                            in structural space and collide via ranking geometry
  - mixed                 : combination
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.analysis.collision_attribution import attribute_collisions  # noqa: E402
from scripts.rules.analysis.pairwise_distance import pairwise_distances  # noqa: E402
from scripts.rules.analysis.structural_fingerprints import extract_all  # noqa: E402
from scripts.gen.sample_rules import RULE_TYPES  # noqa: E402


def _birthday_expected(N: int, K: int) -> float:
    if K <= 0:
        return 0.0
    return math.comb(N, 2) / K


def _collect_pick_freq(attribution: dict) -> Dict[str, Counter]:
    per_salt = attribution["per_salt_picks"]
    freq: Dict[str, Counter] = {rt: Counter() for rt in RULE_TYPES}
    for salt_str, picks in per_salt.items():
        for rt, rid in picks.items():
            if rid is not None:
                freq[rt][rid] += 1
    return freq


def _tight_cluster_rules(pair_records: List[dict], threshold: float) -> Dict[str, List[str]]:
    """Return dict rule_id -> list of neighbor rule_ids within threshold."""
    neighbors: Dict[str, List[str]] = {}
    for pr in pair_records:
        d = pr["distance"]
        if d <= threshold:
            neighbors.setdefault(pr["rule_id_a"], []).append(pr["rule_id_b"])
            neighbors.setdefault(pr["rule_id_b"], []).append(pr["rule_id_a"])
    return neighbors


def verdict(ledger_path: Path, n_salts: int = 8) -> dict:
    attribution = attribute_collisions(ledger_path, n_salts)
    dists = pairwise_distances(ledger_path)
    freq = _collect_pick_freq(attribution)

    per_type: Dict[str, dict] = {}
    for rt in RULE_TYPES:
        payload = dists[rt]
        K = payload["n_rules"]
        obs_pairs = attribution["per_rule_type_pair_count"][rt]
        exp_pairs = _birthday_expected(n_salts, K)
        pick_freq = freq[rt]
        distinct_picks = len(pick_freq)
        # Dominant-rule test: single rule captures ≥ 3 salts.
        max_pick = max(pick_freq.values(), default=0)
        # Tight-cluster analysis: threshold at median − 1σ (never negative).
        thr_1sd = max(0.0, payload["distance_median"] - payload["distance_stdev"])
        thr_2sd = max(0.0, payload["distance_median"] - 2 * payload["distance_stdev"])
        tight_1sd = _tight_cluster_rules(payload["pair_records"], thr_1sd)
        tight_2sd = _tight_cluster_rules(payload["pair_records"], thr_2sd)

        # Assess whether the collisions involve rules that also have close
        # structural neighbors (structural cluster) — for each contributor rule,
        # count its neighbors under both thresholds.
        contributor_ids = set()
        for pair_rec in attribution["pairs"]:
            if rt in pair_rec["contributors"]:
                contributor_ids.add(pair_rec["contributor_rule_ids"][rt])

        contributor_neighbor_counts_1sd = {
            rid: len(tight_1sd.get(rid, [])) for rid in sorted(contributor_ids)
        }
        contributor_neighbor_counts_2sd = {
            rid: len(tight_2sd.get(rid, [])) for rid in sorted(contributor_ids)
        }

        # Verdict:
        if obs_pairs == 0:
            v = "no_collision"
        elif max_pick >= 3:
            # A single rule captured 3+ salts. This is dominant-rule.
            # It is a *small-K* signature that is intermediate between pure
            # hash-geometry (uniform-uniform) and structural clustering
            # (multiple similar rules).
            v = "dominant_rule"
        elif obs_pairs <= exp_pairs * 1.5:
            v = "hash_geometric"
        else:
            # Multiple pairs, no single dominator, above BP. Look for structural
            # cluster: contributor rules with 1+ tight neighbors.
            if sum(contributor_neighbor_counts_1sd.values()) > 0:
                v = "structural_cluster"
            else:
                v = "mixed"

        per_type[rt] = {
            "n_rules": K,
            "observed_pairs": obs_pairs,
            "birthday_expected_pairs": exp_pairs,
            "ratio_observed_over_expected": (obs_pairs / exp_pairs) if exp_pairs > 0 else None,
            "pick_frequency_across_salts": dict(pick_freq),
            "distinct_picks": distinct_picks,
            "max_single_rule_picks": max_pick,
            "threshold_1sd": thr_1sd,
            "threshold_2sd": thr_2sd,
            "tight_cluster_edges_1sd": sum(len(v) for v in tight_1sd.values()) // 2,
            "tight_cluster_edges_2sd": sum(len(v) for v in tight_2sd.values()) // 2,
            "contributor_neighbor_counts_1sd": contributor_neighbor_counts_1sd,
            "contributor_neighbor_counts_2sd": contributor_neighbor_counts_2sd,
            "contributor_rule_ids": sorted(contributor_ids),
            "verdict": v,
        }

    # Aggregate verdict:
    ranked = sorted(RULE_TYPES,
                    key=lambda rt: -per_type[rt]["observed_pairs"])
    top_contributor = ranked[0] if per_type[ranked[0]]["observed_pairs"] > 0 else None
    system_verdict = per_type[top_contributor]["verdict"] if top_contributor else "no_collision"

    total_obs = sum(per_type[rt]["observed_pairs"] for rt in RULE_TYPES)
    total_exp = sum(per_type[rt]["birthday_expected_pairs"] for rt in RULE_TYPES)

    return {
        "n_salts": n_salts,
        "per_rule_type": per_type,
        "top_contributor": top_contributor,
        "system_verdict": system_verdict,
        "aggregate_observed_pairs": total_obs,
        "aggregate_birthday_expected_pairs": total_exp,
        "aggregate_ratio_obs_over_exp": (total_obs / total_exp) if total_exp > 0 else None,
    }


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--out", type=Path,
                    default=_REPO / "data" / "rules" /
                    "collision_floor_analysis" / "cluster_verdict.json")
    ap.add_argument("--n-salts", type=int, default=8)
    args = ap.parse_args(argv)
    result = verdict(args.ledger, args.n_salts)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(f"[cluster_analysis] wrote {args.out}")
    print(f"  top_contributor: {result['top_contributor']}")
    print(f"  system_verdict: {result['system_verdict']}")
    print(f"  aggregate obs={result['aggregate_observed_pairs']} "
          f"exp={result['aggregate_birthday_expected_pairs']:.2f}")
    for rt in RULE_TYPES:
        pt = result["per_rule_type"][rt]
        print(f"  {rt:12s} obs={pt['observed_pairs']} exp={pt['birthday_expected_pairs']:.2f} "
              f"max_pick={pt['max_single_rule_picks']} verdict={pt['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
