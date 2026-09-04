---
created: 2026-09-04T04:20:00Z
cycle: 18
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-V4-RULES-1
---

# Pinned-profile schema v1 — rationale companion

## Purpose

Companion to `scripts/sound_match/pinned_profile_schema_v1.json` (c17 SHA
`8f61d9391a5a3bcf…`) and its validator
`scripts/sound_match/profile_validator.py` (c17 SHA `cd17106f651e9de7…`).
Records **why** the schema takes its current permissive shape, in one
place, so future cycles do not re-litigate the choice.

Closes c17 auditor MODERATE #2 (imprecise "fabricated invariant" wording
in the c17 report). The schema does not fabricate anything; it captures
on-disk reality per invariant (d).

## Two invariants at play

### Invariant (e) — cross-cycle pinned-profile shape stability (c16)

`docs/agent_picks_selection_invariants.md` (SHA `c185718424bd5d93…`)
codified invariant (e) at c16: *the shape of `acceptance_fork` blocks in
pinned-profile deliveries should be stable across cycles so downstream
consumers (delivery driver, schema validator, cross-branch integration
tests) can read them without a per-cycle special case.*

Canonical shape (c14 drums anchor):

```json
"acceptance_fork": {
  "chosen": {...},
  "rejected": [...],
  "authority": "...",
  "invariants_doc": "docs/agent_picks_selection_invariants.md"
}
"supersedes_path": "<str or null, per c14 lemma>"
```

### Invariant (d) — on-disk-vs-brief divergence disclosure (c15)

Same document, invariant (d): *when what is on disk diverges from what a
brief or spec described, disclose the divergence and treat the on-disk
artifact as authoritative per FD-1 (no rewriting of validated
artifacts).*

## Where the three on-disk anchors sit

The v4 workspace has three pinned-profile-shape anchors that predate the
schema:

| Cycle | Instrument | Manifest                                   | Notable shape                                                     |
|------:|:-----------|:-------------------------------------------|:------------------------------------------------------------------|
| c9    | CG bass    | `cg_bass_pinned_profile.json`              | Uses `operator_authority` (not `authority`); grandfathered.       |
| c14   | CG drums   | `cg_drums_pinned_profile.json`             | **Canonical** 4-key `acceptance_fork`; `chosen` is an object.     |
| c15   | CG guitar  | `cg_guitar_pinned_profile.json`            | Missing `manifest_schema_version` / `agent` / `env_pin` at top; 3-nested-key fork (invariants_doc folded into `authority` string) — retroactively disclosed under invariant (d). |

## What the schema does

The v1 JSON Schema draft-07 at
`scripts/sound_match/pinned_profile_schema_v1.json` validates *all three*
on-disk shapes as first-class. Its `acceptance_fork` rule requires:

- `chosen` (any type — object at c14, string at c9/c15)
- `rejected` (array)
- one-of `{authority, operator_authority}`

Its top-level `supersedes_path` rule requires `str` or `null` — never a
list, per the c14 lemma (`docs/agent_picks_selection_invariants.md`
§c14).

Anything stricter would either:

1. Force a rewrite of c9 or c14 or c15, which FD-1 forbids; or
2. Refuse to validate one of the three landed anchors, which invariant
   (d) forbids (on-disk is authoritative).

Neither option is acceptable. The permissive shape is the correct
resolution, not a compromise.

## What the schema does NOT do

- It does **not** fabricate a new invariant. The c17 report's
  "fabricated invariant" phrasing was imprecise; the schema is a
  reflection of invariants (d) and (e) as they already stand, plus the
  c14 supersede-path lemma. This clarification note supersedes that
  phrasing.
- It does not tighten any acceptance-fork enforcement. Future cycles
  MAY tighten if and only if a future operator directive says to
  re-issue the three anchors under a stricter shape. Until then the
  permissive shape is the norm.
- It does not modify any on-disk anchor. c9/c14/c15 manifests are
  byte-identical pre==post any c17/c18 work.

## Test coverage

`tests/test_pinned_profile_schema.py` (c17 SHA `9450ca4eb599fa4b…`) 6/6:

1. c9 bass validates
2. c14 drums validates
3. c15 guitar validates
4. Missing `acceptance_fork` fails
5. Missing `authority`/`operator_authority` fails
6. `supersedes_path` as list fails

The suite is the operational specification of the schema; this rationale
doc explains the framing.

## Cross-links

- Schema: `scripts/sound_match/pinned_profile_schema_v1.json`
- Validator: `scripts/sound_match/profile_validator.py`
- Test suite: `tests/test_pinned_profile_schema.py`
- Invariants doc: `docs/agent_picks_selection_invariants.md`
- Interpreter guard policy: `docs/interpreter_guard_policy.md`
- Bass-gain clarification companion (same-cycle):
  `docs/sound_match/cg_ab_bass_gain_clarification_c18.md`

## Notes for future cycles

- Whenever a new pinned-profile anchor lands, add a fourth row to the
  table above and run `tests/test_pinned_profile_schema.py`. If a new
  anchor cannot validate under the permissive schema, document the
  divergence under invariant (d) rather than editing the schema in
  isolation.
- If operator directs a scope extension of `acceptance_fork` strictness
  (e.g. mandate `authority` and drop the `operator_authority` alias),
  that decision closes with a v2 schema at
  `scripts/sound_match/pinned_profile_schema_v2.json` **plus** a
  rewrite/replacement of the three existing anchors, not a silent
  tightening of v1.
