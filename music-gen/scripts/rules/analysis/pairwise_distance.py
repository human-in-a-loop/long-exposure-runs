#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:30:00Z
# cycle: 14
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 855d4c2e9945)
# milestone: M-GEN-1/collision-floor-investigation
# ---
"""Per-rule_type pairwise structural distance.

Distance metric:
  - Categorical field: 0 if equal, 1 otherwise (Hamming).
  - Numeric field: normalized-difference |a-b|/(|a|+|b|+eps).
  - Rule-pair distance = sum of per-field distances.

Emits pairwise_distances_<rule_type>.tsv per rule_type.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.analysis.structural_fingerprints import (  # noqa: E402
    extract_all, FIELDS_BY_TYPE, CATEGORICAL_FIELDS,
)
from scripts.gen.sample_rules import RULE_TYPES  # noqa: E402

_EPS = 1e-9


def _field_distance(rt: str, field: str, a, b) -> float:
    if field in CATEGORICAL_FIELDS[rt]:
        return 0.0 if a == b else 1.0
    try:
        af = float(a)
        bf = float(b)
    except (TypeError, ValueError):
        return 0.0 if a == b else 1.0
    denom = abs(af) + abs(bf) + _EPS
    return abs(af - bf) / denom


def pairwise_distances(ledger_path: Path) -> Dict[str, dict]:
    """Return per-rule_type distance matrix + summary stats."""
    rows = extract_all(ledger_path)
    by_type: Dict[str, List[dict]] = {rt: [] for rt in RULE_TYPES}
    for r in rows:
        by_type[r["rule_type"]].append(r)

    result: Dict[str, dict] = {}
    for rt, group in by_type.items():
        n = len(group)
        pair_records: List[dict] = []
        distances: List[float] = []
        for i in range(n):
            for j in range(i + 1, n):
                d = 0.0
                for f in FIELDS_BY_TYPE[rt]:
                    col = f"fp_{f}"
                    d += _field_distance(rt, f, group[i].get(col), group[j].get(col))
                pair_records.append({
                    "rule_id_a": group[i]["rule_id"],
                    "rule_id_b": group[j]["rule_id"],
                    "distance": d,
                })
                distances.append(d)
        if distances:
            mean_d = statistics.mean(distances)
            stdev_d = statistics.pstdev(distances)
            median_d = statistics.median(distances)
            min_d = min(distances)
            max_d = max(distances)
        else:
            mean_d = stdev_d = median_d = min_d = max_d = 0.0
        result[rt] = {
            "n_rules": n,
            "n_pairs": len(pair_records),
            "distance_mean": mean_d,
            "distance_stdev": stdev_d,
            "distance_median": median_d,
            "distance_min": min_d,
            "distance_max": max_d,
            "n_fields": len(FIELDS_BY_TYPE[rt]),
            "pair_records": pair_records,
        }
    return result


def write_tsv_per_type(result: Dict[str, dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for rt, payload in result.items():
        lines = ["rule_id_a\trule_id_b\tdistance"]
        for pr in payload["pair_records"]:
            lines.append(f"{pr['rule_id_a']}\t{pr['rule_id_b']}\t{pr['distance']:.6f}")
        (out_dir / f"pairwise_distances_{rt}.tsv").write_text("\n".join(lines) + "\n")


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path,
                    default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--out-dir", type=Path,
                    default=_REPO / "data" / "rules" / "collision_floor_analysis")
    args = ap.parse_args(argv)
    result = pairwise_distances(args.ledger)
    write_tsv_per_type(result, args.out_dir)

    # Also emit a distance_summary.json aggregate.
    summary = {rt: {k: v for k, v in payload.items() if k != "pair_records"}
               for rt, payload in result.items()}
    (args.out_dir / "distance_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(f"[pairwise_distance] wrote 5 pairwise_distances_*.tsv + distance_summary.json")
    for rt in RULE_TYPES:
        s = summary[rt]
        print(f"  {rt:12s} K={s['n_rules']:2d}  n_pairs={s['n_pairs']:3d}  "
              f"mean={s['distance_mean']:.3f}  median={s['distance_median']:.3f}  "
              f"sd={s['distance_stdev']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
