#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:20:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 00b3ae64444c)
# milestone: M-GEN-1/first-generation
# ---
"""Deterministic rule sampler for M-GEN-1/first-generation.

Algorithm (SHA-256 tiebreak, NO PRNG):
  1. Load post-supersede rules via scripts.rules.ledger.effective_rules.
  2. Group by `rule_type`.
  3. Within each group, sort by sha256(canonical_json(rule_row)) ascending.
  4. Pick index 0.

The sampling is a pure function of the ledger contents. Same 28-row ledger
→ same 5 rule_ids on any process, any machine, any Python version that
respects insertion order (3.7+). No `random`, `numpy.random`, `torch.rand`,
`secrets` — SHA-256 all the way.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.ledger import effective_rules  # noqa: E402


RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")


def _canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _content_hash(row: dict) -> str:
    """SHA-256 over the canonical JSON of the whole rule row."""
    return hashlib.sha256(_canonical_json(row).encode()).hexdigest()


@dataclass
class SampledRuleset:
    rules: Dict[str, dict] = field(default_factory=dict)          # rule_type -> chosen rule row
    sampling_manifest: dict = field(default_factory=dict)          # per-type: candidates + winner

    def rule_ids(self) -> Dict[str, str]:
        return {rt: self.rules[rt].get("rule_id") for rt in RULE_TYPES if rt in self.rules}


def sample_ruleset(ledger_path: Path) -> SampledRuleset:
    """Deterministically pick one rule per rule_type."""
    rules = effective_rules(Path(ledger_path))
    by_type: Dict[str, List[dict]] = {rt: [] for rt in RULE_TYPES}
    for r in rules:
        rt = r.get("rule_type")
        if rt in by_type:
            by_type[rt].append(r)

    chosen: Dict[str, dict] = {}
    manifest: Dict[str, dict] = {"algorithm": "sha256_over_canonical_json_ascending", "prng_used": False}
    per_type: Dict[str, dict] = {}
    for rt in RULE_TYPES:
        candidates = by_type[rt]
        # Sort by content hash ascending.
        scored = [(_content_hash(r), r) for r in candidates]
        scored.sort(key=lambda t: t[0])
        winner_hash, winner = scored[0]
        chosen[rt] = winner
        per_type[rt] = {
            "n_candidates": len(candidates),
            "winner_rule_id": winner.get("rule_id"),
            "winner_content_hash": winner_hash,
            "all_candidates": [{"rule_id": r.get("rule_id"), "content_hash": h} for h, r in scored],
        }
    manifest["per_rule_type"] = per_type
    manifest["skipped_instrument"] = []  # populated later by the assembler if it drops any
    return SampledRuleset(rules=chosen, sampling_manifest=manifest)


def _main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path, default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--out", type=Path, default=_REPO / "data" / "gen" / "sampling_manifest.json")
    args = ap.parse_args(argv)

    rs = sample_ruleset(args.ledger)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({
        "chosen_rule_ids": rs.rule_ids(),
        "sampling_manifest": rs.sampling_manifest,
    }, indent=2, sort_keys=True))
    print(f"[sample_rules] wrote {args.out}")
    for rt, rid in rs.rule_ids().items():
        print(f"  {rt:12s} -> {rid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
