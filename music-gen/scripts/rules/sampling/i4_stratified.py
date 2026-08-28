#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T16:00:00Z
# cycle: 15
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 392503ab7d47)
# milestone: M-GEN-1/batch-v3-i4
# ---
"""I4 stratified rejection sampler for M-GEN-1/batch-v3-i4.

Implements the cycle-14 collision-floor investigation's I4 intervention
(``docs/collision_floor_investigation_report.md`` §I4;
``data/rules/collision_floor_analysis/intervention_proposal.json``):
within each rule_type, rank candidates by the sample_rules SHA-256 rank hash
for the current salt, then pick the lowest-rank candidate that has not
already been picked at any lower salt within the same rule_type. Since every
rule_type has K >= 10 >= N=8, this makes within-rule_type collisions
impossible by construction; predicted floor at N=8 is 0 pairs.

Design constraints (per campaign brief):
  * SHA-256 tiebreak discipline; NO PRNG anywhere.
  * Interpreter guard `/usr/bin/python3`.
  * No `sidecar_nonfactor` imports.
  * Deterministic across processes: same (ledger, salt, prior picks) ->
    same output byte-for-byte.

Public API:
  * ``I4Sampler(ledger_path)`` — stateful helper that carries the per-
    rule_type already_picked set across salts.
  * ``sample_ruleset_i4(ledger_path, salt, already_picked)`` — pure
    functional variant. ``already_picked`` is a dict ``{rule_type: set[str]}``
    of rule_ids to exclude; the function returns a SampledRuleset AND the
    set of newly-picked rule_ids per rule_type (caller merges).

The output SampledRuleset carries the SAME dataclass surface as
``scripts.gen.sample_rules.SampledRuleset`` so drop-in use in the batch
driver is trivial.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Reuse SampledRuleset shape + hash function from the batch_v2 sampler so
# the collision analyzer and provenance emitter see an identical surface.
from scripts.gen.sample_rules import (  # noqa: E402
    SampledRuleset,
    RULE_TYPES,
    _content_hash,
)
from scripts.rules.ledger import effective_rules  # noqa: E402


class I4SamplerError(Exception):
    """Raised when the stratified rejection would leave a rule_type empty."""


def _score_and_sort(candidates: List[dict], salt: int) -> List[Tuple[str, dict]]:
    """SHA-256 rank the candidates for this salt, ascending."""
    scored = [(_content_hash(r, salt=salt), r) for r in candidates]
    scored.sort(key=lambda t: t[0])
    return scored


def sample_ruleset_i4(
    ledger_path: Path,
    salt: int,
    already_picked: Dict[str, Set[str]] | None = None,
) -> Tuple[SampledRuleset, Dict[str, str]]:
    """Deterministic I4 stratified rejection sampler for one salt.

    Args:
        ledger_path: path to the rules ledger JSONL.
        salt: integer salt (>= 0).
        already_picked: per-rule_type set of rule_ids already picked at
            lower salts. Missing keys are treated as empty sets.

    Returns:
        (SampledRuleset, newly_picked) where ``newly_picked`` is
        ``{rule_type: rule_id}`` for the caller to merge into its running
        state.

    Raises:
        I4SamplerError: if a rule_type has fewer available candidates than
            required (i.e., every candidate has already been picked).
    """
    salt = int(salt)
    already_picked = {rt: set(already_picked.get(rt, ())) for rt in RULE_TYPES} if already_picked else {rt: set() for rt in RULE_TYPES}

    rules = effective_rules(Path(ledger_path))
    by_type: Dict[str, List[dict]] = {rt: [] for rt in RULE_TYPES}
    for r in rules:
        rt = r.get("rule_type")
        if rt in by_type:
            by_type[rt].append(r)

    chosen: Dict[str, dict] = {}
    per_type: Dict[str, dict] = {}
    newly_picked: Dict[str, str] = {}

    for rt in RULE_TYPES:
        candidates = by_type[rt]
        scored = _score_and_sort(candidates, salt)
        excluded = already_picked[rt]

        winner_hash = None
        winner = None
        skipped: List[dict] = []
        for h, r in scored:
            rid = r.get("rule_id")
            if rid in excluded:
                skipped.append({"rule_id": rid, "content_hash": h})
                continue
            winner_hash, winner = h, r
            break

        if winner is None:
            raise I4SamplerError(
                f"I4 stratified rejection sampler exhausted rule_type={rt} at "
                f"salt={salt}: {len(candidates)} candidates, "
                f"{len(excluded)} already picked. "
                "This is a FAIL of the intervention as specified."
            )

        chosen[rt] = winner
        newly_picked[rt] = winner.get("rule_id")

        per_type[rt] = {
            "n_candidates": len(candidates),
            "n_already_picked_before": len(excluded),
            "n_skipped_this_call": len(skipped),
            "winner_rule_id": winner.get("rule_id"),
            "winner_content_hash": winner_hash,
            "skipped": skipped,
            # Full ranked candidate list for provenance parity with sample_rules.
            "all_candidates": [
                {"rule_id": r.get("rule_id"), "content_hash": h} for h, r in scored
            ],
        }

    manifest = {
        "algorithm": "i4_stratified_rejection_sha256",
        "salt": salt,
        "salt_envelope": ("legacy_bare" if salt == 0 else "canonical_json_envelope"),
        "prng_used": False,
        "per_rule_type": per_type,
        "skipped_instrument": [],
        # Snapshot the exclusion set for reproducibility.
        "already_picked_snapshot": {rt: sorted(already_picked[rt]) for rt in RULE_TYPES},
    }
    rs = SampledRuleset(rules=chosen, sampling_manifest=manifest)
    return rs, newly_picked


@dataclass
class I4Sampler:
    """Stateful wrapper carrying the cross-salt `already_picked` set.

    Typical use in a batch driver:

        sampler = I4Sampler(ledger_path)
        for salt in SALTS:
            rs = sampler.sample(salt)   # SampledRuleset
            ... coherence gate, render, score ...
    """
    ledger_path: Path
    already_picked: Dict[str, Set[str]] = field(default_factory=lambda: {rt: set() for rt in RULE_TYPES})

    def sample(self, salt: int) -> SampledRuleset:
        rs, newly = sample_ruleset_i4(self.ledger_path, salt, self.already_picked)
        for rt, rid in newly.items():
            self.already_picked[rt].add(rid)
        return rs

    def snapshot(self) -> Dict[str, List[str]]:
        return {rt: sorted(self.already_picked[rt]) for rt in RULE_TYPES}


def _main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path, default=_REPO / "data" / "rules" / "ledger.jsonl")
    ap.add_argument("--out", type=Path,
                    default=_REPO / "data" / "gen" / "i4_sampling_probe.json")
    ap.add_argument("--n-salts", type=int, default=8)
    args = ap.parse_args(argv)

    sampler = I4Sampler(args.ledger)
    per_salt = []
    for s in range(args.n_salts):
        rs = sampler.sample(s)
        per_salt.append({"salt": s, "chosen_rule_ids": rs.rule_ids()})

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({
        "algorithm": "i4_stratified_rejection_sha256",
        "n_salts": args.n_salts,
        "per_salt": per_salt,
        "final_already_picked": sampler.snapshot(),
    }, indent=2, sort_keys=True))
    print(f"[i4_stratified] wrote {args.out}")
    for row in per_salt:
        print(f"  salt={row['salt']}: {row['chosen_rule_ids']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
