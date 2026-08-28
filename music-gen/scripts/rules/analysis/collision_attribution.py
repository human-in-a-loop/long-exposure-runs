#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:30:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 855d4c2e9945)
# milestone: M-GEN-1/collision-floor-investigation
# ---
"""Per-pair rule_type attribution of M-GEN-1 batch-v2 collisions.

Reproduces the cycle-13 11-pair collision floor from the frozen
76-row ledger + frozen SHA-256 tiebreak sampler. Attributes each
pair to every rule_type in which salt_i and salt_j pick the same
rule_id. One pair can have multiple contributor rule_types (multi-count).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.gen.sample_rules import sample_ruleset, RULE_TYPES  # noqa: E402


def attribute_collisions(ledger_path: Path, n_salts: int = 8) -> dict:
    """Return per-pair contributor rule_types.

    Structure:
      {
        "n_salts": int,
        "rule_types": [...],
        "per_salt_picks": {salt: {rule_type: rule_id}},
        "pairs": [{pair: [i,j], contributors: [rule_type,...],
                   contributor_rule_ids: {rule_type: rule_id}}],
        "per_rule_type_pair_count": {rule_type: int},
        "per_rule_type_pairs": {rule_type: [[i,j],...]},
        "total_pairwise_collisions": int,
        "any_collision_pair_count": int,   # unique pairs, any rule_type
      }
    """
    salt_picks: Dict[int, Dict[str, str]] = {}
    for salt in range(n_salts):
        rs = sample_ruleset(ledger_path, salt=salt)
        salt_picks[salt] = rs.rule_ids()

    pairs: List[dict] = []
    per_rt_pairs: Dict[str, List[List[int]]] = {rt: [] for rt in RULE_TYPES}
    total_pair_contribs = 0
    any_collision = set()
    for i in range(n_salts):
        for j in range(i + 1, n_salts):
            contributors: List[str] = []
            contributor_ids: Dict[str, str] = {}
            for rt in RULE_TYPES:
                a = salt_picks[i].get(rt)
                b = salt_picks[j].get(rt)
                if a is not None and a == b:
                    contributors.append(rt)
                    contributor_ids[rt] = a
                    per_rt_pairs[rt].append([i, j])
                    total_pair_contribs += 1
            if contributors:
                any_collision.add((i, j))
                pairs.append({
                    "pair": [i, j],
                    "contributors": contributors,
                    "contributor_rule_ids": contributor_ids,
                })

    return {
        "n_salts": n_salts,
        "rule_types": list(RULE_TYPES),
        "per_salt_picks": {str(k): v for k, v in salt_picks.items()},
        "pairs": pairs,
        "per_rule_type_pair_count": {rt: len(per_rt_pairs[rt]) for rt in RULE_TYPES},
        "per_rule_type_pairs": per_rt_pairs,
        "total_pairwise_collisions": total_pair_contribs,
        "any_collision_pair_count": len(any_collision),
    }


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--out", type=Path,
                    default=_REPO / "data" / "rules" /
                    "collision_floor_analysis" / "attribution.json")
    ap.add_argument("--n-salts", type=int, default=8)
    args = ap.parse_args(argv)

    result = attribute_collisions(args.ledger, args.n_salts)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(f"[collision_attribution] wrote {args.out}")
    print(f"  total_pairwise_collisions = {result['total_pairwise_collisions']}")
    print(f"  any_collision_pair_count  = {result['any_collision_pair_count']}")
    for rt in RULE_TYPES:
        print(f"  {rt:12s} pair_count = {result['per_rule_type_pair_count'][rt]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
