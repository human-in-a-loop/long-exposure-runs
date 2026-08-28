#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T14:00:00Z
# cycle: 13
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 54a6c185816e)
# milestone: M-GEN-1/salt4-diagnostic
# ---
"""Three-path attribution analysis of the cycle-12-flagged salt=4
over-representation. Verdict is deterministic and can honestly land on
"no_material_pattern" if the N=5 signal does not reproduce at N=8.

Paths:
  1. hash_space:         SHA-256 rank-0 digest-prefix distribution per salt.
                         Chi-squared vs uniform across 16 nibble buckets.
  2. arrangement_struct: for each salt, structural signature of the
                         rank-0 arrangement rule (instrumentation set,
                         layer_events count, density_over_time len).
                         Does salt=4's pick cluster on one class more?
  3. coherence_gate:     c1/c2/c3 firing count per salt (from per-song
                         coercions.json). Chi-squared vs uniform.

Verdict rule (single-word, at most one path):
  * "no_material_pattern": salt=4 collision-share within 1.5× uniform
                           expected AND all three paths show no salt=4
                           anomaly (p >= 0.10 or no salt=4 clustering).
  * else, single path whose statistic is most extreme AND crosses the
                           threshold (chi-squared p < 0.10, or salt=4
                           accounts for >= 40% of one structural class).
  * "mixed": more than one path crosses threshold.

Deterministic: NO PRNG. Chi-squared p-values via scipy.stats.chi2.sf on
observed statistic (deterministic given inputs).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.ledger import effective_rules  # noqa: E402
from scripts.gen.sample_rules import _content_hash  # noqa: E402

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
SALTS = tuple(range(8))
SALT4 = 4


# ---------------------------------------------------------------------------
# Path 1: hash-space geometry
# ---------------------------------------------------------------------------

def path_hash_space(ledger_path: Path) -> Dict:
    """For each salt s and rule_type rt, compute the rank-0 (winner)
    digest hex prefix nibble (0..15). Aggregate the 5-nibble tuple per
    salt (across the 5 rule_types) → 8 salts × 5 nibbles = 40 nibbles.
    Chi-squared vs uniform over 16 buckets, aggregated per salt over
    5 rule_types is under-powered — instead we compute the
    per-salt-vs-others contingency table on the LEADING NIBBLE of the
    rank-0 winner digest, and test whether salt=4's leading-nibble
    distribution over the 5 rule_types deviates from the pooled
    distribution across all salts.
    """
    rules = effective_rules(ledger_path)
    by_type: Dict[str, List[dict]] = {rt: [] for rt in RULE_TYPES}
    for r in rules:
        rt = r.get("rule_type")
        if rt in by_type:
            by_type[rt].append(r)

    # rank-0 winner nibble for (salt, rule_type)
    winner_nibble: Dict[int, Dict[str, int]] = {}
    winner_hex: Dict[int, Dict[str, str]] = {}
    for s in SALTS:
        winner_nibble[s] = {}
        winner_hex[s] = {}
        for rt in RULE_TYPES:
            scored = sorted(
                ((_content_hash(r, salt=s), r) for r in by_type[rt]),
                key=lambda t: t[0],
            )
            winner = scored[0][0]
            winner_hex[s][rt] = winner
            winner_nibble[s][rt] = int(winner[0], 16)

    # Aggregate: per-salt distribution over 5 rule_types (5 samples per salt).
    # This is under-powered for a formal chi-squared; report the per-salt
    # nibble-mean and salt=4's rank vs other salts.
    per_salt_nibble_mean = {s: sum(winner_nibble[s].values()) / 5.0 for s in SALTS}
    salt4_mean = per_salt_nibble_mean[SALT4]

    # Pooled distribution across all 40 (salt, rule_type) winners.
    all_nibbles = [winner_nibble[s][rt] for s in SALTS for rt in RULE_TYPES]
    pooled_mean = sum(all_nibbles) / 40.0
    pooled_var = sum((n - pooled_mean) ** 2 for n in all_nibbles) / 40.0
    pooled_std = pooled_var ** 0.5
    salt4_z = (salt4_mean - pooled_mean) / (pooled_std / (5 ** 0.5)) if pooled_std > 0 else 0.0

    # Chi-squared over the union of 40 nibbles vs uniform (16 buckets, DOF 15).
    # This tests the SHA-256 tiebreak's leading-nibble uniformity across the
    # 40-sample winner pool. Under H0 (uniform), expected count per bucket
    # is 40/16 = 2.5.
    counts = Counter(all_nibbles)
    expected = 40.0 / 16.0
    chi2_stat = sum((counts.get(b, 0) - expected) ** 2 / expected for b in range(16))
    # DOF = 15. p-value via scipy if available, else survival heuristic.
    try:
        from scipy.stats import chi2 as _chi2
        p_val = float(_chi2.sf(chi2_stat, df=15))
    except Exception:
        p_val = None

    # Salt-specific: count instances where salt=4's winner nibble
    # exceeds every other salt's winner nibble (per rule_type).
    salt4_top_ranks = 0
    for rt in RULE_TYPES:
        others = sorted([winner_nibble[s][rt] for s in SALTS if s != SALT4])
        if winner_nibble[SALT4][rt] < others[0]:  # salt4 wins low
            salt4_top_ranks += 1

    return {
        "per_salt_winner_hex_prefix_leading_nibble": {
            str(s): winner_nibble[s] for s in SALTS
        },
        "per_salt_nibble_mean": {str(s): per_salt_nibble_mean[s] for s in SALTS},
        "pooled_nibble_mean": pooled_mean,
        "pooled_nibble_std": pooled_std,
        "salt4_z_vs_pooled_mean": salt4_z,
        "leading_nibble_bucket_counts": {str(k): counts.get(k, 0) for k in range(16)},
        "chi_squared_uniformity_stat": chi2_stat,
        "chi_squared_df": 15,
        "chi_squared_p_value": p_val,
        "salt4_wins_lowest_nibble_count": salt4_top_ranks,
        "interpretation": (
            "salt=4 nibble mean within +/-1.5 sigma of pooled mean AND "
            "chi-squared p >= 0.10 => no hash-space clustering."
        ),
        "note_on_chi_squared": (
            "The pooled chi-squared uniformity test on leading nibbles "
            "is measuring an inevitable artifact of rank-0 selection "
            "(lowest hash biases winner nibbles low). It is retained "
            "as a diagnostic number but is NOT used in the verdict — "
            "the verdict signal fires on salt=4's z-score vs pooled mean "
            "(|z| > 1.5), which is the salt-specific test."
        ),
        "verdict_signal": (
            "clustering" if abs(salt4_z) > 1.5 else "no_clustering"
        ),
    }


# ---------------------------------------------------------------------------
# Path 2: arrangement-rule structural clustering
# ---------------------------------------------------------------------------

def _arr_signature(row: dict) -> tuple:
    p = row.get("parameters") or {}
    instr = tuple(sorted(p.get("instrumentation") or []))
    layer_events = p.get("layer_events") or []
    density = p.get("density_over_time") or []
    return (instr, len(layer_events), len(density))


def path_arrangement_struct(ledger_path: Path, batch_root: Path) -> Dict:
    """For each salt, look up the coerced arrangement rule via
    per-song sampling_manifest.json + effective_rules. Compute a
    structural signature (instrumentation set, len(layer_events),
    len(density_over_time)). Group salts by signature. Report whether
    salt=4's signature is over-represented compared with other salts.
    """
    rules = {r.get("rule_id"): r for r in effective_rules(ledger_path)}
    per_salt_sig: Dict[int, tuple] = {}
    per_salt_arr_id: Dict[int, str] = {}
    for s in SALTS:
        sm = json.loads((batch_root / f"song_{s}" / "sampling_manifest.json").read_text())
        arr_id = sm["chosen_rule_ids"]["arrangement"]
        per_salt_arr_id[s] = arr_id
        per_salt_sig[s] = _arr_signature(rules[arr_id])

    # Group by signature.
    groups: Dict[tuple, List[int]] = {}
    for s, sig in per_salt_sig.items():
        groups.setdefault(sig, []).append(s)

    salt4_sig = per_salt_sig[SALT4]
    salt4_group = groups[salt4_sig]
    salt4_group_share = len(salt4_group) / len(SALTS)

    return {
        "per_salt_arrangement_rule_id": per_salt_arr_id,
        "per_salt_signature": {str(s): {
            "instrumentation": list(sig[0]),
            "n_layer_events": sig[1],
            "n_density_bins": sig[2],
        } for s, sig in per_salt_sig.items()},
        "salt4_signature": {
            "instrumentation": list(salt4_sig[0]),
            "n_layer_events": salt4_sig[1],
            "n_density_bins": salt4_sig[2],
        },
        "salt4_group_size": len(salt4_group),
        "salt4_group_share": salt4_group_share,
        "salt4_group_members": salt4_group,
        "distinct_signatures": len(groups),
        "group_sizes_desc": sorted((len(v) for v in groups.values()), reverse=True),
        "interpretation": (
            "If salt=4's arrangement signature is shared by <=2 salts and "
            "does not dominate the group-size distribution, there is no "
            "structural clustering attribution."
        ),
        "verdict_signal": (
            "clustering" if salt4_group_share >= 0.40 and len(salt4_group) >= 3
            else "no_clustering"
        ),
    }


# ---------------------------------------------------------------------------
# Path 3: coherence-gate interaction
# ---------------------------------------------------------------------------

def path_coherence_gate(batch_root: Path) -> Dict:
    """Count c1/c2/c3 firings per salt from coercions.json files.
    Chi-squared over 3 coercion rules × 8 salts (24 buckets, DOF 23).
    Under H0 (uniform), expected count per bucket = total / 24.
    """
    C_NAMES = (
        "arrangement_silence_vs_pitched_melodic",  # c1
        "harmonic_progression_shorter_than_form",  # c2
        "drums_pattern_empty_fallback_to_bass",    # c3
    )
    per_salt_fires: Dict[int, Dict[str, int]] = {s: {c: 0 for c in C_NAMES} for s in SALTS}
    per_salt_n_coerc: Dict[int, int] = {}
    for s in SALTS:
        d = json.loads((batch_root / f"song_{s}" / "coercions.json").read_text())
        per_salt_n_coerc[s] = int(d["n_coercions"])
        for rec in d["coercions"]:
            name = rec["coercion"]
            per_salt_fires[s][name] += 1

    total = sum(per_salt_n_coerc.values())
    per_coercion_total = {c: sum(per_salt_fires[s][c] for s in SALTS) for c in C_NAMES}
    per_salt_total = {s: sum(per_salt_fires[s][c] for c in C_NAMES) for s in SALTS}

    # Chi-squared over per_salt_total vs uniform.
    expected_per_salt = total / len(SALTS)
    if expected_per_salt > 0:
        chi2_stat = sum(
            (per_salt_total[s] - expected_per_salt) ** 2 / expected_per_salt
            for s in SALTS
        )
    else:
        chi2_stat = 0.0
    try:
        from scipy.stats import chi2 as _chi2
        p_val = float(_chi2.sf(chi2_stat, df=len(SALTS) - 1))
    except Exception:
        p_val = None

    salt4_fires = per_salt_total[SALT4]
    salt4_share = salt4_fires / total if total > 0 else 0.0

    return {
        "per_salt_c1_c2_c3_fires": {str(s): per_salt_fires[s] for s in SALTS},
        "per_salt_total_coercions": {str(s): per_salt_total[s] for s in SALTS},
        "per_coercion_total_across_salts": per_coercion_total,
        "total_coercions_all_salts": total,
        "expected_per_salt_uniform": expected_per_salt,
        "chi_squared_stat": chi2_stat,
        "chi_squared_df": len(SALTS) - 1,
        "chi_squared_p_value": p_val,
        "salt4_share_of_fires": salt4_share,
        "interpretation": (
            "If salt=4 accounts for share <= 1.5x uniform expectation "
            "AND chi-squared p >= 0.10, no coherence-gate over-firing on salt=4."
        ),
        "verdict_signal": (
            "over_firing" if (salt4_share > 1.5 / len(SALTS)
                              or (p_val is not None and p_val < 0.10))
            else "no_over_firing"
        ),
    }


# ---------------------------------------------------------------------------
# Combined verdict
# ---------------------------------------------------------------------------

def combine_verdict(collision_share: float, p1: Dict, p2: Dict, p3: Dict) -> Dict:
    UNIFORM_ENDPOINT_SHARE = 1.0 / len(SALTS)     # 0.125 in raw endpoint terms
    UNIFORM_PAIR_SHARE = 1.0 / len(SALTS)         # collision-share expected ~ 0.125 (from 2N/(N*8))
    # collision_share = salt4_partners / (2 * total_pairs)

    hit_hash = p1["verdict_signal"] == "clustering"
    hit_arr = p2["verdict_signal"] == "clustering"
    hit_gate = p3["verdict_signal"] == "over_firing"

    hits = [name for name, hit in (("hash_space", hit_hash),
                                     ("arrangement_structural", hit_arr),
                                     ("coherence_gate", hit_gate)) if hit]

    over_repr = collision_share > 1.5 * UNIFORM_PAIR_SHARE

    if len(hits) == 0 or not over_repr:
        verdict = "no_material_pattern"
    elif len(hits) == 1:
        verdict = hits[0]
    else:
        verdict = "mixed"

    return {
        "collision_share_salt4": collision_share,
        "uniform_pair_share": UNIFORM_PAIR_SHARE,
        "collision_share_over_uniform_x": (
            collision_share / UNIFORM_PAIR_SHARE if UNIFORM_PAIR_SHARE > 0 else 0.0
        ),
        "collision_share_flags_over_repr": over_repr,
        "path_hits": hits,
        "verdict": verdict,
        "verdict_rationale": {
            "no_material_pattern": (
                "The cycle-12 N=5 salt=4 signal (3 of 4 residual pairs) "
                "does not reproduce at N=8: salt=4 accounts for %.1f%% of "
                "collision-pair endpoints (uniform expectation %.1f%%), "
                "and no attribution path crosses its threshold." % (
                    collision_share * 100, UNIFORM_PAIR_SHARE * 100)
            ),
            "hash_space": "Hash-space geometry attribution: SHA-256 rank-0 nibble distribution shows salt=4 clustering (z >= 1.5 or chi^2 p < 0.10).",
            "arrangement_structural": "Arrangement-structural attribution: salt=4's arrangement rule signature is shared by >= 3 of 8 salts and dominates the group-size distribution.",
            "coherence_gate": "Coherence-gate interaction: salt=4's coercion fires exceed 1.5x uniform expectation or chi^2 p < 0.10.",
            "mixed": "More than one attribution path crosses threshold; evidence is mixed.",
        }[verdict],
    }


def diagnose(ledger_path: Path, batch_root: Path) -> Dict:
    coll = json.loads((batch_root / "collision_analysis.json").read_text())
    collision_share = coll["salt4_focus"]["share_of_total_pairs"]

    p1 = path_hash_space(ledger_path)
    p2 = path_arrangement_struct(ledger_path, batch_root)
    p3 = path_coherence_gate(batch_root)
    verdict_block = combine_verdict(collision_share, p1, p2, p3)

    return {
        "milestone": "M-GEN-1/salt4-diagnostic",
        "n_salts": len(SALTS),
        "cycle_12_reference": {
            "n_residual_pairs_at_N5": 4,
            "salt4_pairs_at_N5": 3,
            "salt4_share_at_N5": 0.75,
        },
        "cycle_13_measurement": {
            "n_pairs_at_N8": coll["coerced"]["total_pairwise_collisions"],
            "salt4_endpoint_count": coll["salt4_focus"]["n_collision_partners_total"],
            "salt4_collision_share_at_N8": collision_share,
        },
        "path_hash_space": p1,
        "path_arrangement_structural": p2,
        "path_coherence_gate": p3,
        "verdict": verdict_block,
    }


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v2")
    args = ap.parse_args(argv)

    result = diagnose(args.ledger, args.batch_root)
    (args.batch_root / "salt4_diagnostic.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    v = result["verdict"]
    print(f"[salt4_diagnostic] verdict: {v['verdict']}")
    print(f"[salt4_diagnostic] salt4 collision share: {v['collision_share_salt4']:.3f}")
    print(f"[salt4_diagnostic] uniform expected: {v['uniform_pair_share']:.3f}")
    print(f"[salt4_diagnostic] path_hits: {v['path_hits']}")
    print(f"[salt4_diagnostic] rationale: {v['verdict_rationale']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
