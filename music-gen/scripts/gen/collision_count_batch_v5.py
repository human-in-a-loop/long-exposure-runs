#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T22:00:00Z
# cycle: 23
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 3fbd8c1ab57c)
# milestone: M-GEN-1/batch-v5-n16
# ---
"""Collision analysis for batch-v5-n16 (N=16 salts).

Uses the same cycle-13 attribution methodology as cycle-13/16
(pairwise coerced-rule-id equality within each rule_type, dominant
contributor per pair), just parameterized to a 16-salt grid.

Reads:
    data/gen/batch_v5_n16/song_<s>/sampling_manifest.json for s in 0..15

Writes:
    data/gen/batch_v5_n16/collision_analysis.json
    data/gen/batch_v5_n16/collision_matrix.tsv
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
SALTS = tuple(range(16))


def _load_ids(batch_root: Path, key: str) -> Dict[int, Dict[str, str]]:
    out: Dict[int, Dict[str, str]] = {}
    for s in SALTS:
        sm = json.loads((batch_root / f"song_{s}" / "sampling_manifest.json").read_text())
        out[s] = dict(sm[key])
    return out


def _attribute_pair(coerced: Dict[int, Dict[str, str]],
                    si: int, sj: int) -> Dict[str, bool]:
    """Which rule_types are byte-identical between salts si and sj?

    Cycle-13 attribution methodology: a pair (si, sj) is a "collision pair"
    iff at least one rule_type has coerced[si][rt] == coerced[sj][rt].
    A pair may match on multiple rule_types (counted once per rule_type
    in the histogram; per-pair primary attribution uses cycle-13 tiebreak
    below).
    """
    return {rt: coerced[si][rt] == coerced[sj][rt] for rt in RULE_TYPES}


def _dominant_rule_type(matches: Dict[str, bool]) -> str | None:
    """Cycle-13 tiebreak: first rule_type by RULE_TYPES declaration order
    that has a match. Returns None if no rule_type matches.
    """
    for rt in RULE_TYPES:
        if matches[rt]:
            return rt
    return None


def analyze(batch_root: Path) -> Dict:
    coerced = _load_ids(batch_root, "chosen_rule_ids")
    raw = _load_ids(batch_root, "raw_rule_ids")

    per_rule_type_matrix: Dict[str, List[List[int]]] = {}
    per_rule_type_pairs: Dict[str, List[List[int]]] = {}
    per_rule_type_raw_pairs: Dict[str, List[List[int]]] = {}
    per_salt_partners: Dict[int, Dict[str, List[int]]] = {
        s: {rt: [] for rt in RULE_TYPES} for s in SALTS
    }

    # Per-pair records: (si, sj, dominant_rt, matches_all)
    pair_records: List[Dict] = []
    total_coerced_pairs = 0
    total_raw_pairs = 0

    # Per-rule_type histogram: counts every (i,j,rt) hit (not unique-per-pair).
    histogram: Dict[str, int] = {rt: 0 for rt in RULE_TYPES}
    # Primary attribution histogram (one increment per pair using tiebreak).
    primary_histogram: Dict[str, int] = {rt: 0 for rt in RULE_TYPES}

    for rt in RULE_TYPES:
        M = [[0]*len(SALTS) for _ in SALTS]
        pairs: List[List[int]] = []
        pairs_raw: List[List[int]] = []
        for i, si in enumerate(SALTS):
            for j, sj in enumerate(SALTS):
                same = int(coerced[si][rt] == coerced[sj][rt])
                M[i][j] = same
                if i < j and same:
                    pairs.append([si, sj])
                    per_salt_partners[si][rt].append(sj)
                    per_salt_partners[sj][rt].append(si)
                if i < j and raw[si][rt] == raw[sj][rt]:
                    pairs_raw.append([si, sj])
                    total_raw_pairs += 1
        per_rule_type_matrix[rt] = M
        per_rule_type_pairs[rt] = pairs
        per_rule_type_raw_pairs[rt] = pairs_raw

    # Walk unique pairs to build per-pair attribution + primary histogram.
    for i, si in enumerate(SALTS):
        for j, sj in enumerate(SALTS):
            if i >= j:
                continue
            matches = _attribute_pair(coerced, si, sj)
            any_match = any(matches.values())
            if not any_match:
                continue
            total_coerced_pairs += 1
            for rt in RULE_TYPES:
                if matches[rt]:
                    histogram[rt] += 1
            dom = _dominant_rule_type(matches)
            if dom is not None:
                primary_histogram[dom] += 1
            pair_records.append({
                "s_i": si,
                "s_j": sj,
                "matches": {rt: bool(matches[rt]) for rt in RULE_TYPES},
                "dominant_rule_type": dom,
            })

    per_salt_endpoint_count = {
        s: sum(len(per_salt_partners[s][rt]) for rt in RULE_TYPES)
        for s in SALTS
    }

    form_arr = primary_histogram["form"] + primary_histogram["arrangement"]
    form_arr_fraction = (form_arr / total_coerced_pairs) if total_coerced_pairs else 0.0

    return {
        "n_salts": len(SALTS),
        "salts": list(SALTS),
        "rule_types": list(RULE_TYPES),
        "coerced": {
            "total_pairwise_collisions": total_coerced_pairs,
            "per_rule_type_pairs": per_rule_type_pairs,
            "per_rule_type_matrix": per_rule_type_matrix,
            "per_salt_endpoint_count": per_salt_endpoint_count,
            "per_salt_partners": per_salt_partners,
            "histogram_any_rt": histogram,
            "primary_histogram_tiebreak": primary_histogram,
            "form_arrangement_primary_fraction": form_arr_fraction,
            "pair_records": pair_records,
        },
        "raw": {
            "total_pairwise_collisions": total_raw_pairs,
            "per_rule_type_pairs": per_rule_type_raw_pairs,
        },
        "K_distribution": {
            "harmonic": 20,
            "rhythmic": 15,
            "melodic": 15,
            "form": 15,
            "arrangement": 15,
        },
    }


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
                    default=_REPO / "data" / "gen" / "batch_v5_n16")
    args = ap.parse_args(argv)

    result = analyze(args.batch_root)
    (args.batch_root / "collision_analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True))
    write_tsv(result, args.batch_root / "collision_matrix.tsv")

    total = result["coerced"]["total_pairwise_collisions"]
    print(f"[collision_count_batch_v5] coerced pairs = {total}")
    print(f"[collision_count_batch_v5] primary attribution (tiebreak, cycle-13):")
    for rt in result["rule_types"]:
        print(f"  {rt}: {result['coerced']['primary_histogram_tiebreak'][rt]}")
    print(f"[collision_count_batch_v5] {{form, arrangement}} fraction = "
          f"{result['coerced']['form_arrangement_primary_fraction']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
