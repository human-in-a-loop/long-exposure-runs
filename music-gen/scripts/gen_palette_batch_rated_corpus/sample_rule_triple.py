#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T14:34:10Z
# cycle: 43
# run_id: fork-c320de981fda-clone-0
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-rated-corpus
# ---
"""Per-salt rule-triple selection via SHA-256 tiebreak on c40's shard.

For each rule_type in {harmonic, rhythmic, arrangement}, sort matching
rule_ids by ``sha256(f"{salt}|{rule_id}".encode("ascii")).hexdigest()``
ascending and take rank 0. NO PRNG, NO rejection loop, NO exclusion
set. c34 clone-2 unconditioned tiebreak pattern verbatim (per
``scripts/gen_palette_batch_v1/sample_rule_triple.py``); that module
is READ-ONLY and NOT imported at runtime — the pattern is re-implemented
locally to keep the anchor edge clean. Only difference vs c34 v1: the
rules source is c40's rated-corpus shard.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = _REPO / "data" / "rules" / "ledger_rated_corpus.jsonl"
RULE_TYPES = ("harmonic", "rhythmic", "arrangement")


def _load_by_type(ledger_path: Path = LEDGER_PATH) -> dict[str, list[str]]:
    """Stream-read ledger; return {rule_type: [rule_id, ...]}."""
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


def _salted_key(salt: int, rule_id: str) -> str:
    return hashlib.sha256(f"{salt}|{rule_id}".encode("ascii")).hexdigest()


def sample_triple(salt: int, ledger_path: Path = LEDGER_PATH) -> dict[str, str]:
    """Return {rule_type: rule_id} rank-0 by SHA-256 tiebreak for salt."""
    by_type = _load_by_type(ledger_path)
    triple: dict[str, str] = {}
    for rt in RULE_TYPES:
        ids = by_type.get(rt, [])
        if not ids:
            raise RuntimeError(f"no rules of type {rt} in {ledger_path}")
        triple[rt] = min(ids, key=lambda rid: _salted_key(salt, rid))
    return triple


def sample_triples(salts) -> dict:
    """Return {salt: {rule_type: rule_id}} for a list of salts."""
    return {s: sample_triple(s) for s in salts}


def rank_evidence(salt: int, ledger_path: Path = LEDGER_PATH) -> dict:
    """Return rank-0 witness (rule_id + salted key) per rule_type."""
    by_type = _load_by_type(ledger_path)
    out: dict = {"salt": salt, "per_type": {}}
    for rt in RULE_TYPES:
        ids = by_type.get(rt, [])
        sorted_ids = sorted(ids, key=lambda rid: _salted_key(salt, rid))
        out["per_type"][rt] = {
            "rank_0_rule_id": sorted_ids[0] if sorted_ids else None,
            "rank_0_salted_sha_prefix": _salted_key(salt, sorted_ids[0])[:16]
            if sorted_ids else None,
            "candidate_count": len(ids),
        }
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--salt", type=int, required=True)
    args = ap.parse_args()
    print(json.dumps(rank_evidence(args.salt), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
