#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T13:55:00Z
# cycle: 13
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 54a6c185816e)
# milestone: M-GEN-1/batch-v2
# ---
"""Collision analysis over the batch-v2 sampling manifests.

For each rule_type, iterate 8 x 8 salt pairs and count matching
coerced rule_ids. Aggregate: total pairwise collisions across rule_types;
per-salt collision-partner count.

Reads:
    data/gen/batch_v2/song_<s>/sampling_manifest.json for s in 0..7

Writes:
    data/gen/batch_v2/collision_analysis.json
    data/gen/batch_v2/collision_matrix.tsv   (long-form: rule_type, s_i, s_j, same)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
SALTS = tuple(range(8))


def _load_coerced_ids(batch_root: Path) -> Dict[int, Dict[str, str]]:
    out: Dict[int, Dict[str, str]] = {}
    for s in SALTS:
        sm = json.loads((batch_root / f"song_{s}" / "sampling_manifest.json").read_text())
        out[s] = dict(sm["chosen_rule_ids"])
    return out


def _load_raw_ids(batch_root: Path) -> Dict[int, Dict[str, str]]:
    out: Dict[int, Dict[str, str]] = {}
    for s in SALTS:
        sm = json.loads((batch_root / f"song_{s}" / "sampling_manifest.json").read_text())
        out[s] = dict(sm["raw_rule_ids"])
    return out


def analyze(batch_root: Path) -> Dict:
    coerced = _load_coerced_ids(batch_root)
    raw = _load_raw_ids(batch_root)

    per_rule_type_matrix: Dict[str, List[List[int]]] = {}
    per_rule_type_pairs: Dict[str, List[List[int]]] = {}
    per_rule_type_raw_pairs: Dict[str, List[List[int]]] = {}
    per_salt_partners: Dict[int, Dict[str, List[int]]] = {s: {rt: [] for rt in RULE_TYPES} for s in SALTS}

    total_coerced_pairs = 0
    total_raw_pairs = 0
    for rt in RULE_TYPES:
        M = [[0]*len(SALTS) for _ in SALTS]
        pairs = []
        pairs_raw = []
        for i, si in enumerate(SALTS):
            for j, sj in enumerate(SALTS):
                same = int(coerced[si][rt] == coerced[sj][rt])
                M[i][j] = same
                if i < j and same:
                    pairs.append([si, sj])
                    per_salt_partners[si][rt].append(sj)
                    per_salt_partners[sj][rt].append(si)
                    total_coerced_pairs += 1
                if i < j and raw[si][rt] == raw[sj][rt]:
                    pairs_raw.append([si, sj])
                    total_raw_pairs += 1
        per_rule_type_matrix[rt] = M
        per_rule_type_pairs[rt] = pairs
        per_rule_type_raw_pairs[rt] = pairs_raw

    # Per-salt totals (partner endpoints, coerced)
    per_salt_endpoint_count = {
        s: sum(len(per_salt_partners[s][rt]) for rt in RULE_TYPES)
        for s in SALTS
    }

    # Salt=4 focus block
    salt4_partners = per_salt_partners[4]
    salt4_n_partners_total = sum(len(v) for v in salt4_partners.values())

    result = {
        "n_salts": len(SALTS),
        "salts": list(SALTS),
        "rule_types": list(RULE_TYPES),
        "coerced": {
            "total_pairwise_collisions": total_coerced_pairs,
            "per_rule_type_pairs": per_rule_type_pairs,
            "per_rule_type_matrix": per_rule_type_matrix,
            "per_salt_endpoint_count": per_salt_endpoint_count,
            "per_salt_partners": per_salt_partners,
        },
        "raw": {
            "total_pairwise_collisions": total_raw_pairs,
            "per_rule_type_pairs": per_rule_type_raw_pairs,
        },
        "salt4_focus": {
            "n_collision_partners_total": salt4_n_partners_total,
            "per_rule_type_partners": salt4_partners,
            "share_of_total_pairs": (
                salt4_n_partners_total / (2 * total_coerced_pairs)
                if total_coerced_pairs > 0 else 0.0
            ),
        },
        "trend": {
            "cycle_11_batch_v1_N5_28rules": 5,
            "cycle_12_batch_v1_rerun_N5_76rules": 4,
            "cycle_13_batch_v2_N8_76rules": total_coerced_pairs,
            "expected_scaling_if_random": (
                # If collision-per-pair rate were constant, pairs grow as C(N,2)
                round(4 * (8 * 7 / 2) / (5 * 4 / 2), 2)
            ),
        },
    }
    return result


def write_tsv(result: Dict, out: Path) -> None:
    lines = ["rule_type\ts_i\ts_j\tsame_coerced"]
    for rt, M in result["coerced"]["per_rule_type_matrix"].items():
        for i, si in enumerate(SALTS):
            for j, sj in enumerate(SALTS):
                lines.append(f"{rt}\t{si}\t{sj}\t{M[i][j]}")
    out.write_text("\n".join(lines) + "\n")


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v2")
    args = ap.parse_args(argv)

    result = analyze(args.batch_root)
    (args.batch_root / "collision_analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    write_tsv(result, args.batch_root / "collision_matrix.tsv")

    print(f"[collision_analysis] total coerced pairs: {result['coerced']['total_pairwise_collisions']}")
    print(f"[collision_analysis] total raw pairs:     {result['raw']['total_pairwise_collisions']}")
    print(f"[collision_analysis] per-salt endpoint count:")
    for s in SALTS:
        print(f"  salt={s}: {result['coerced']['per_salt_endpoint_count'][s]}")
    print(f"[collision_analysis] salt=4 share of pairs: "
          f"{result['salt4_focus']['share_of_total_pairs']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
