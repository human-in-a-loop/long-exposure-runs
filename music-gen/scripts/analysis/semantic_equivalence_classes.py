#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:35:00Z
# cycle: 30
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-semantic-cluster-overlap
# ---
"""Build per-rule_type per-ledger semantic-equivalence classes under
the frozen p20 thresholds.

Adjacency: edge(i,j) iff pairwise cosine distance < threshold[rule_type].
Connected components via union-find. Deterministic; no PRNG.
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
THR_JSON = ROOT / "data" / "collision_model" / "semantic_cluster_thresholds.json"
OUT_TSV = ROOT / "data" / "collision_model" / "semantic_equivalence_classes.tsv"


def _l2_norm(v):
    s = math.sqrt(sum(x * x for x in v))
    if s == 0.0:
        return v
    return [x / s for x in v]


def _cos_dist(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    d = 1.0 - dot
    if d < 0.0:
        d = 0.0
    if d > 2.0:
        d = 2.0
    return d


def _read_fps_grouped():
    """{(source, rule_type): [(rule_id, normed_vec), ...]},
    inner list deterministically sorted by rule_id."""
    grp = {}
    with open(FP_TSV, "r") as f:
        _ = f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            source, rt, _rts, rule_id, _, vec_json = parts
            vec = json.loads(vec_json)
            grp.setdefault((source, rt), []).append(
                (rule_id, _l2_norm(vec))
            )
    for k in grp:
        grp[k].sort(key=lambda x: x[0])
    return grp


class _UF:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        # Deterministic tie-break by lower index.
        if self.r[ra] < self.r[rb]:
            self.p[ra] = rb
        elif self.r[ra] > self.r[rb]:
            self.p[rb] = ra
        else:
            self.p[rb] = ra
            self.r[ra] += 1


def build_components(entries, threshold):
    n = len(entries)
    uf = _UF(n)
    for i in range(n):
        for j in range(i + 1, n):
            # ≤ threshold: identical-fingerprint pairs (dist=0)
            # collapse even when threshold=0. See rubric §4.
            if _cos_dist(entries[i][1], entries[j][1]) <= threshold:
                uf.union(i, j)
    # Bucket by root; canonicalize component_id by min rule_id.
    buckets = {}
    for i in range(n):
        buckets.setdefault(uf.find(i), []).append(i)
    # Sort by (min rule_id within component) for deterministic
    # component_id ordering.
    ordered = sorted(
        buckets.values(),
        key=lambda idxs: min(entries[k][0] for k in idxs)
    )
    return ordered  # list of index-lists, per component


def main():
    thr = json.loads(THR_JSON.read_text())["per_rule_type"]
    grp = _read_fps_grouped()
    rows = []
    for (source, rt), entries in sorted(grp.items()):
        threshold = thr[rt]["p20_threshold"]
        comps = build_components(entries, threshold)
        for comp_id, idxs in enumerate(comps):
            member_ids = sorted(entries[k][0] for k in idxs)
            rows.append({
                "source_ledger": source,
                "rule_type": rt,
                "component_id": comp_id,
                "n_members": len(idxs),
                "member_rule_ids": member_ids,
                "threshold_used": threshold,
            })
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    header = ("source_ledger\trule_type\tcomponent_id\tn_members\t"
              "threshold_used\tmember_rule_ids_json\n")
    lines = [header]
    for r in sorted(rows, key=lambda x: (x["source_ledger"],
                                         x["rule_type"],
                                         x["component_id"])):
        lines.append(
            f"{r['source_ledger']}\t{r['rule_type']}\t"
            f"{r['component_id']}\t{r['n_members']}\t"
            f"{r['threshold_used']:.10f}\t"
            f"{json.dumps(r['member_rule_ids'], separators=(',',':'))}\n"
        )
    OUT_TSV.write_text("".join(lines))
    sha = hashlib.sha256(OUT_TSV.read_bytes()).hexdigest()
    print(f"WROTE {OUT_TSV.relative_to(ROOT)}")
    # Summary lines.
    from collections import defaultdict
    n_by_key = defaultdict(int)
    for r in rows:
        n_by_key[(r["source_ledger"], r["rule_type"])] += 1
    for (source, rt) in sorted(n_by_key):
        print(f"  {source} / {rt}: {n_by_key[(source, rt)]} components")
    print(f"sha256={sha[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
