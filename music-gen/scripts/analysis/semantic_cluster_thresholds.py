#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:20:00Z
# cycle: 30
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-semantic-cluster-overlap
# ---
"""Compute per-rule_type 20th-percentile pairwise-distance threshold
on the 76-row baseline `ledger.jsonl` ONLY.

Pre-registration integrity: this script MUST NOT read the augmented
86-row I3 ledger. A test asserts absence of any augmented-ledger
substring in this file's source.

Pairwise distance: 1 - cosine similarity of L2-normalized fingerprint
vectors within a rule_type.

Deterministic. No PRNG.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[2]
FP_TSV = ROOT / "data" / "collision_model" / "rule_structural_fingerprints.tsv"
OUT_JSON = ROOT / "data" / "collision_model" / "semantic_cluster_thresholds.json"

# Pre-registered percentile — locked before any batch-v6 outcome
# analysis. See rubric doc §3.
THRESHOLD_PERCENTILE = 0.20

# Ledger the threshold is computed on — MUST be the 76-row baseline.
# The name below is a token, not a filesystem read (kept for the audit
# trail); actual data comes from FP_TSV filtered by source_ledger.
THRESHOLD_SOURCE_LEDGER = "76row"


def _l2_norm(v):
    s = math.sqrt(sum(x * x for x in v))
    if s == 0.0:
        return v
    return [x / s for x in v]


def _cos_dist(a, b):
    """1 - cosine similarity of already-L2-normalized vectors.
    Clamps near-zero to 0.0 and near-2.0 to 2.0."""
    dot = sum(x * y for x, y in zip(a, b))
    d = 1.0 - dot
    if d < 0.0:
        d = 0.0
    if d > 2.0:
        d = 2.0
    return d


def _percentile(sorted_vals, p):
    """Linear-interpolated percentile on a sorted list.
    p in [0,1]. Deterministic; no numpy."""
    n = len(sorted_vals)
    if n == 0:
        return 0.0
    if n == 1:
        return sorted_vals[0]
    k = p * (n - 1)
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return sorted_vals[lo]
    frac = k - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def _read_fps_76():
    """Load fingerprints from the 76-row ledger ONLY."""
    per_rt = {}
    with open(FP_TSV, "r") as f:
        header = f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            source, rt, _, rule_id, _, vec_json = parts
            if source != THRESHOLD_SOURCE_LEDGER:
                continue
            vec = json.loads(vec_json)
            per_rt.setdefault(rt, []).append((rule_id, vec))
    return per_rt


def compute_thresholds():
    per_rt = _read_fps_76()
    result = {}
    for rt, entries in sorted(per_rt.items()):
        n = len(entries)
        # Normalize all vectors up-front.
        normed = [(rid, _l2_norm(v)) for rid, v in entries]
        # All pairwise distances (i<j).
        dists = []
        for i in range(n):
            for j in range(i + 1, n):
                dists.append(_cos_dist(normed[i][1], normed[j][1]))
        dists.sort()
        thr = _percentile(dists, THRESHOLD_PERCENTILE)
        result[rt] = {
            "n_rules_76row": n,
            "n_pairs": len(dists),
            "min_dist": dists[0] if dists else 0.0,
            "max_dist": dists[-1] if dists else 0.0,
            "p20_threshold": thr,
        }
    return result


def main():
    thresholds = compute_thresholds()
    payload = {
        "generator": "scripts/analysis/semantic_cluster_thresholds.py",
        "source_ledger": "data/rules/ledger.jsonl",
        "source_ledger_tag": THRESHOLD_SOURCE_LEDGER,
        "note": (
            "20th-percentile per-rule_type pairwise cosine-distance "
            "threshold on the 76-row baseline ledger. Pre-registered; "
            "the augmented I3 ledger is never read here."
        ),
        "threshold_percentile": THRESHOLD_PERCENTILE,
        "per_rule_type": thresholds,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True))
    sha = hashlib.sha256(OUT_JSON.read_bytes()).hexdigest()
    print(f"WROTE {OUT_JSON.relative_to(ROOT)}")
    for rt, info in sorted(thresholds.items()):
        print(f"  {rt}: n={info['n_rules_76row']:2d} "
              f"pairs={info['n_pairs']:4d} "
              f"p20={info['p20_threshold']:.6f} "
              f"[min={info['min_dist']:.4f} max={info['max_dist']:.4f}]")
    print(f"sha256={sha[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
