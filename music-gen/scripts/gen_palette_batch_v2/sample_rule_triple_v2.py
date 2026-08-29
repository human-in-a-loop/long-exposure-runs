#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:05:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v2-sampler-diversified
# ---
"""Per-salt DIFFERENT rule triples via SHA-256 tiebreak with cross-salt distinctness.

For each rule_type in {harmonic, rhythmic, arrangement}:
  For each salt in a set of salts:
    Rank all rule_ids by sha256(f"{salt}|{rule_id}|{rule_type}".encode()).hexdigest().
    Rank-0 is the initial choice.
  Enforce cross-salt distinctness by iterating salts in ascending order:
    If a higher-salt clone's rank-0 rule_id equals a lower-salt clone's
    rank-0 rule_id (in the same rule_type), the higher-salt clone falls
    to next rank. Repeat as needed.

NO PRNG. Reads data/rules/ledger.jsonl streaming-only.
Base 76-row ledger actual counts: H=10, R=18, M=18, F=15, A=15
(brief's "K=20 harmonic" was a carry-over from batch-v6's ledger_i3_dminor).
Not a blocker; distinctness requires only |candidates_per_type| >= |salts|,
i.e. |candidates| >= 3, which every rule_type in {harmonic, rhythmic,
arrangement} satisfies (min = 10 on harmonic).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = _REPO / "data" / "rules" / "ledger.jsonl"
RULE_TYPES = ("harmonic", "rhythmic", "arrangement")


def _load_by_type(ledger_path: Path = LEDGER_PATH) -> dict[str, list[str]]:
    by_type: dict[str, list[str]] = {rt: [] for rt in RULE_TYPES}
    with open(ledger_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            rt = row.get("rule_type")
            rid = row.get("rule_id")
            if rt in by_type and isinstance(rid, str) and rid.startswith("rule_"):
                by_type[rt].append(rid)
    return by_type


def _salted_key(salt: int, rule_id: str, rule_type: str) -> str:
    return hashlib.sha256(
        f"{salt}|{rule_id}|{rule_type}".encode("ascii")
    ).hexdigest()


def _ranked_ids(salt: int, rule_type: str,
                candidates: list[str]) -> list[str]:
    """Return candidate rule_ids sorted ascending by salted SHA-256 digest.
    Ties (astronomically unlikely on SHA-256) broken lexicographically on rule_id.
    """
    return sorted(candidates,
                  key=lambda rid: (_salted_key(salt, rid, rule_type), rid))


def sample_triples(salts: list[int],
                   ledger_path: Path = LEDGER_PATH
                   ) -> dict[int, dict[str, str]]:
    """Return {salt: {rule_type: rule_id}} with cross-salt distinctness enforced.

    Iterates salts in ascending order. For each salt, for each rule_type,
    picks the highest-rank rule_id NOT already taken by a lower salt.
    """
    by_type = _load_by_type(ledger_path)
    for rt in RULE_TYPES:
        if len(by_type.get(rt, [])) < len(salts):
            raise RuntimeError(
                f"insufficient rule_ids for rule_type={rt}: "
                f"{len(by_type.get(rt, []))} < {len(salts)}"
            )
    triples: dict[int, dict[str, str]] = {}
    for salt in sorted(salts):
        chosen: dict[str, str] = {}
        for rt in RULE_TYPES:
            taken = {triples[s][rt] for s in triples}
            ranked = _ranked_ids(salt, rt, by_type[rt])
            picked = None
            for rid in ranked:
                if rid not in taken:
                    picked = rid
                    break
            if picked is None:
                # Should be unreachable given the size guard above.
                raise RuntimeError(
                    f"salt={salt} rule_type={rt}: no distinct rule_id "
                    f"available (taken={sorted(taken)})"
                )
            chosen[rt] = picked
        triples[salt] = chosen
    return triples


def rank_evidence(salt: int, ledger_path: Path = LEDGER_PATH) -> dict:
    """Return rank-0 witness (rule_id + salted digest prefix) per rule_type.
    Used by report §3 evidence."""
    by_type = _load_by_type(ledger_path)
    out: dict = {"salt": salt, "per_type": {}}
    for rt in RULE_TYPES:
        ids = by_type.get(rt, [])
        ranked = _ranked_ids(salt, rt, ids)
        out["per_type"][rt] = {
            "rank_0_rule_id": ranked[0] if ranked else None,
            "rank_0_salted_sha_prefix":
                _salted_key(salt, ranked[0], rt)[:16] if ranked else None,
            "candidate_count": len(ids),
            "full_ranking_first8": [
                {"rule_id": rid,
                 "salted_sha_prefix": _salted_key(salt, rid, rt)[:16]}
                for rid in ranked[:8]
            ],
        }
    return out


def assignments_sha_for_salt(triple: dict[str, str]) -> str:
    """SHA-256 of the canonical-JSON representation of the salt's rule triple.
    Used to compare across-salt inequality on assignments payload (not on
    the actual assignments.jsonl file, which pins additional metadata).
    """
    payload = json.dumps(triple, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--salt", type=int, required=True)
    args = ap.parse_args()
    print(json.dumps(rank_evidence(args.salt), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
