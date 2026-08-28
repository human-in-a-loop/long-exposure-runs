#!/usr/bin/env python3
# ---
# created: 2026-08-28T22:45:00Z
# cycle: 28
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Effective K under hash-space-geometry mechanism (M3).

Reads data/collision_model/hash_uniformity_summary.json (produced by
hash_uniformity_per_rule_type.py) and computes:

    K_eff_hash = K * (1 - deviation_normalized)

where deviation_normalized in [0, 1] is chi2/(N*(K-1)) capped at 1.

deviation_normalized = 0 -> hash-uniform sampling -> K_eff_hash = K
deviation_normalized = 1 -> full concentration -> K_eff_hash = 0

K_eff_hash is clipped at max(K_eff_hash, 1) for downstream BP-formula
substitution (documented degeneracy handling, matches cycle-27 M2).

Emits data/collision_model/effective_k_hash.tsv.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"effective_k_hash requires /usr/bin/python3, got {sys.executable}"
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "collision_model"

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")


def main(argv: list[str]) -> int:
    summary_path = OUT_DIR / "hash_uniformity_summary.json"
    summary = json.loads(summary_path.read_text())
    batches = sorted(summary["batches"].keys())
    rows = ["batch_id\trule_type\tK\tdeviation_normalized\tK_eff_hash_raw\tK_eff_hash_clipped"]
    for b in batches:
        per_rt = summary["batches"][b]
        for rt in RULE_TYPES:
            e = per_rt[rt]
            K = int(e["K"])
            dev = float(e["deviation_normalized"])
            k_eff_raw = K * (1.0 - dev)
            k_eff_clipped = max(k_eff_raw, 1.0)
            rows.append(
                f"{b}\t{rt}\t{K}\t{dev:.6f}\t{k_eff_raw:.6f}\t{k_eff_clipped:.6f}"
            )
    out = OUT_DIR / "effective_k_hash.tsv"
    out.write_text("\n".join(rows) + "\n")
    print(f"[effective_k_hash] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
