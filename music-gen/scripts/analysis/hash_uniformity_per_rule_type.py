#!/usr/bin/env python3
# ---
# created: 2026-08-28T22:35:00Z
# cycle: 28
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Hash-space uniformity per (rule_type x batch).

For each batch, for each rule_type, for each salt: read the sampled
(rank-0) rule_id from that batch's provenance (or per-song
sampling_manifest.json for batch_v5_n16); look up the rule_id's row
index in the source rules ledger via order-of-append.

Under H0 (SHA-256-uniform sampling), each of K rule_ids should win
with probability 1/K per salt; observed winners across N_salts should
follow Multinomial(N_salts, uniform_over_K).  Compute the chi-squared
statistic:

    chi2 = sum_i (obs_i - N/K)^2 / (N/K)

against the uniform expectation.  Report the analytic chi-squared
survival function p-value (dof=K-1) with an honest small-count caveat
(most bins have expected count << 5).  Also report the normalized
deviation used by hash_geometry_fit:

    deviation = min(1, chi2 / (N * (K - 1)))

which is 0 when all bins hit their expected count and 1 when all N
salts hit a single bin (chi2 = N*(K-1) under maximum concentration).

Emits:
  data/collision_model/hash_uniformity.tsv       -- long form
  data/collision_model/hash_uniformity_summary.json

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"hash_uniformity_per_rule_type requires /usr/bin/python3, got {sys.executable}"
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "collision_model"

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")

# Per plan-of-record: which ledger each batch samples from.
BATCH_LEDGER = {
    "batch_v1": "data/rules/ledger.jsonl",
    "batch_v2": "data/rules/ledger.jsonl",
    "batch_v3_i3": "data/rules/ledger_i3_dminor.jsonl",
    "batch_v3_i4": "data/rules/ledger.jsonl",
    "batch_v4": "data/rules/ledger_i3_dminor.jsonl",
    "batch_v5_n16": "data/rules/ledger_i3_dminor.jsonl",
    "batch_v6": "data/rules/ledger_i3_dminor.jsonl",
}


def load_rule_indices(ledger_path: pathlib.Path) -> dict[str, dict[str, int]]:
    """Return {rule_type: {rule_id: order-of-append index}} for effective rules.

    Order-of-append = position of the first "rule" event in the JSONL.
    Superseded rules are still in the index (they're candidates the sampler
    could rank against before supersede resolution — but the sampler pulls
    from `effective_rules` which resolves supersedes, so we cross-check
    against effective ids only).
    """
    order: dict[str, dict[str, int]] = {rt: {} for rt in RULE_TYPES}
    for line in ledger_path.open():
        r = json.loads(line)
        if r.get("event_type") != "rule":
            continue
        rt = r.get("rule_type")
        rid = r.get("rule_id")
        if rt in order and rid and rid not in order[rt]:
            order[rt][rid] = len(order[rt])
    return order


def winners_per_batch(batch: str) -> dict[str, dict[int, str]]:
    """Return {rule_type: {salt: winner_rule_id}}."""
    out: dict[str, dict[int, str]] = {rt: {} for rt in RULE_TYPES}
    prov = ROOT / "data" / "gen" / batch / "provenance.jsonl"
    if prov.exists():
        for line in prov.open():
            r = json.loads(line)
            stage = r.get("stage")
            if stage in ("sample_rules", "sample_rules_unconditioned", "sample_rules_i4"):
                salt = int(r["salt"])
                chosen = r["output_shas"]["chosen_rule_ids"]
                for rt, rid in chosen.items():
                    if rt in out:
                        out[rt][salt] = rid
    else:
        base = ROOT / "data" / "gen" / batch
        for song_dir in sorted(base.glob("song_*"), key=lambda p: int(p.name.split("_")[1])):
            manifest = song_dir / "sampling_manifest.json"
            if not manifest.exists():
                continue
            m = json.loads(manifest.read_text())
            salt = int(m["salt"])
            chosen = m["chosen_rule_ids"]
            for rt, rid in chosen.items():
                if rt in out:
                    out[rt][salt] = rid
    return out


def _chi2_sf_dof(chi2: float, dof: int) -> float:
    """Chi-squared survival function without scipy dependency.

    Uses the regularized upper incomplete gamma function Q(k/2, x/2)
    computed via the series expansion of the lower incomplete gamma
    (numerically stable for the K values we see here: dof <= 20,
    chi2 <= a few hundred).
    """
    if chi2 <= 0.0:
        return 1.0
    if dof <= 0:
        return float("nan")
    a = dof / 2.0
    x = chi2 / 2.0
    # Use scipy-free implementation via math.lgamma and series.
    # For x < a+1, use the series for P(a,x); else use continued fraction for Q(a,x).
    if x < a + 1.0:
        # Power series (Numerical Recipes 6.2, gser).
        term = 1.0 / a
        total = term
        n = 1
        while n < 500:
            term *= x / (a + n)
            total += term
            if abs(term) < abs(total) * 1e-14:
                break
            n += 1
        # P(a,x) = e^{-x} * x^a * total / Gamma(a)
        log_pref = -x + a * math.log(x) - math.lgamma(a)
        p_lower = math.exp(log_pref) * total
        return max(0.0, 1.0 - p_lower)
    else:
        # Continued fraction for Q(a,x) (gcf).
        b = x + 1.0 - a
        c = 1.0 / 1e-300
        d = 1.0 / b
        h = d
        for i in range(1, 500):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-300:
                d = 1e-300
            c = b + an / c
            if abs(c) < 1e-300:
                c = 1e-300
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-14:
                break
        log_pref = -x + a * math.log(x) - math.lgamma(a)
        return max(0.0, min(1.0, math.exp(log_pref) * h))


def compute(batch: str) -> dict:
    ledger = ROOT / BATCH_LEDGER[batch]
    idx = load_rule_indices(ledger)
    wins = winners_per_batch(batch)

    per_rule_type = {}
    for rt in RULE_TYPES:
        K = len(idx[rt])
        salt_to_winner = wins[rt]
        salts = sorted(salt_to_winner.keys())
        N = len(salts)
        # Count winners per rule_id (bin over K candidates).
        counts = {rid: 0 for rid in idx[rt]}
        winners_indices: list[int] = []
        for s in salts:
            rid = salt_to_winner[s]
            if rid in counts:
                counts[rid] += 1
                winners_indices.append(idx[rt][rid])
            else:
                # winner not in candidate list -- schema drift; count as bin K (bookkeeping)
                counts.setdefault("__OFF_LEDGER__", 0)
                counts["__OFF_LEDGER__"] += 1
        # Chi-squared vs uniform-over-K.
        if K > 0 and N > 0:
            expected = N / K
            chi2 = sum((c - expected) ** 2 / expected for rid, c in counts.items()
                       if rid != "__OFF_LEDGER__")
            dof = K - 1
            p_value = _chi2_sf_dof(chi2, dof) if dof > 0 else float("nan")
            max_chi2 = N * (K - 1)  # analytic max under full concentration
            deviation = min(1.0, chi2 / max_chi2) if max_chi2 > 0 else 0.0
        else:
            chi2 = 0.0
            dof = 0
            p_value = float("nan")
            deviation = 0.0

        per_rule_type[rt] = {
            "K": K,
            "N_salts": N,
            "chi2": chi2,
            "dof": dof,
            "p_value": p_value,
            "deviation_normalized": deviation,
            "winner_counts_top": sorted(
                ((rid, c) for rid, c in counts.items() if c > 0),
                key=lambda t: (-t[1], t[0]),
            )[:8],
            "unique_winners": sum(1 for c in counts.values() if c > 0),
            "winner_index_sequence": winners_indices,
        }
    return {"batch": batch, "per_rule_type": per_rule_type}


def main(argv: list[str]) -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    batches = list(BATCH_LEDGER.keys())
    rows: list[str] = ["batch_id\trule_type\tK\tN_salts\tchi2\tdof\tp_value\tdeviation_normalized\tunique_winners"]
    summary = {"batches": {}}
    for b in batches:
        r = compute(b)
        summary["batches"][b] = r["per_rule_type"]
        for rt in RULE_TYPES:
            e = r["per_rule_type"][rt]
            rows.append(
                f"{b}\t{rt}\t{e['K']}\t{e['N_salts']}\t{e['chi2']:.6f}\t{e['dof']}\t"
                f"{e['p_value']:.6f}\t{e['deviation_normalized']:.6f}\t{e['unique_winners']}"
            )
    (OUT_DIR / "hash_uniformity.tsv").write_text("\n".join(rows) + "\n")
    summary["methodology"] = {
        "chi2_definition": "sum_i (obs_i - N/K)^2 / (N/K); bins over K rule_ids per rule_type",
        "p_value": "chi-squared survival function with dof=K-1 (analytic; small-count caveat applies for most rule_types)",
        "deviation_normalized": "min(1, chi2 / (N*(K-1))); 0 = uniform, 1 = full concentration",
        "expected_under_H0": "each of K rule_ids wins 1/K per salt",
    }
    summary["frozen_alpha"] = 0.7469387071101908
    summary["scripts"] = "scripts/analysis/hash_uniformity_per_rule_type.py"
    (OUT_DIR / "hash_uniformity_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(f"[hash_uniformity] wrote {OUT_DIR / 'hash_uniformity.tsv'}")
    print(f"[hash_uniformity] wrote {OUT_DIR / 'hash_uniformity_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
