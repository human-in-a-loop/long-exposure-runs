#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:40:00Z
# cycle: 30
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-semantic-cluster-overlap
# ---
"""Compute K_eff-semantic per (ledger × rule_type) from the
semantic-equivalence-class TSV. K_eff-semantic = number of connected
components.

Deterministic. No PRNG.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from collections import defaultdict

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[2]
EC_TSV = ROOT / "data" / "collision_model" / "semantic_equivalence_classes.tsv"
OUT_TSV = ROOT / "data" / "collision_model" / "effective_k_semantic.tsv"

RT_SHORT = {"harmonic": "H", "rhythmic": "R", "melodic": "M",
            "form": "F", "arrangement": "A"}


def main():
    counts = defaultdict(int)
    with open(EC_TSV, "r") as f:
        _ = f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            source, rt, _cid, _n, _thr, _mids = parts
            counts[(source, rt)] += 1
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    lines = ["source_ledger\trule_type\trule_type_short\tK_eff_semantic\n"]
    for (source, rt) in sorted(counts):
        lines.append(f"{source}\t{rt}\t{RT_SHORT[rt]}\t{counts[(source,rt)]}\n")
    OUT_TSV.write_text("".join(lines))
    sha = hashlib.sha256(OUT_TSV.read_bytes()).hexdigest()
    print(f"WROTE {OUT_TSV.relative_to(ROOT)}")
    for (source, rt) in sorted(counts):
        print(f"  {source} / {rt} ({RT_SHORT[rt]}): "
              f"K_eff_semantic={counts[(source,rt)]}")
    print(f"sha256={sha[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
