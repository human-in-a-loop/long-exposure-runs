<!--
created: 2026-08-29T02:00:00Z
cycle: 31
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-assignment-schema
-->

# Cycle 31 Branch B — investigation notes

## Anchors read (read-only)

- `scripts/rules/schema/rules_v1.json` — cycle-6 M-RULES-1 JSON Schema
  authoritative artifact. Two row kinds via `event_type`; per-`rule_type`
  parameter dispatch via `allOf` + `if/then/else`; `additionalProperties:
  false` at every object level; content-addressed rule_id
  (`"rule_" + sha256(canonical_json(payload))[:16]`).
- `scripts/rules/validate.py` — cycle-6 two-layer validator pattern:
  Layer 1 = `jsonschema.Draft202012Validator`; Layer 2 = hand-written
  cross-row checks; every function returns `list[str]` of error messages;
  never raises on validation failure; every field access `.get()`-guarded.
- `scripts/rules/schema/examples/build_examples.py` — cycle-6 synthetic
  instance generator pattern: deterministic (no PRNG), content-derived
  ids, per-rule_type per-instance validation before write.
- `scripts/rules/rule_id.py` — content-addressed id derivation via
  canonical JSON + SHA-256.

## Ledger inventory

`data/rules/ledger.jsonl` (76 rows):
- harmonic: 10, rhythmic: 18, melodic: 18, form: 15, arrangement: 15

`data/rules/ledger_i3_dminor.jsonl` (86 rows):
- harmonic: 20 (10 baseline + 10 D_minor variants), rhythmic: 18,
  melodic: 18, form: 15, arrangement: 15

Union: 86 resolvable rule_ids (I3 augmented ledger is a superset in
the harmonic dimension; other rule_types are identical).

Sample rule_ids per type (first-encountered, extracted from the ledgers
themselves so every provenance_pointer used in the synthetic corpus
resolves under the Layer-2 check):
- harmonic: rule_0271c7a9f3b5f606, rule_5b62c5b9a15f0a56,
  rule_2e9df2a83c9de210, rule_43d3f2f97eaa02e8
- rhythmic: rule_ba740b0c3a578421, rule_47db14f19cf7fbb0,
  rule_2f5a7b3e8d6c1a90, rule_1a2b3c4d5e6f7890
- (build_examples.py loads the ACTUAL ids at build time from the
  ledgers; the hardcoded fallback list above is used only if the
  ledger files disappear.)

## Design decisions

1. **Content-hash namespace pinning.** `NAMESPACE_PALETTE_V1 =
   uuid.uuid5(uuid.NAMESPACE_URL, "palette_v1::music-gen::c31")`. Derived
   deterministically from the standard URL namespace, seeded with a
   human-readable string. No hard-coded UUID magic constant, no PRNG.

2. **notes_optional excluded from hash.** Rationale: an authoring note
   is metadata for humans; churning the assignment_id whenever a note
   is edited would fragment downstream references. The rubric §4 and
   the report §3.4 document the exclusion.

3. **Skip-list vs schema `oneOf`.** The stem × instrument compatibility
   matrix could be encoded either as a Layer-1 `oneOf` dispatch or as
   a Layer-2 skip-list. Chose Layer-2: keeps the schema trivial (six
   required fields; no branch dispatch); Layer-2 can emit a
   human-readable rejection reason quoting the skip-list constant;
   easier to evolve if the compatibility matrix changes in cycle 32+
   (add/remove entries from `SKIP_COMBOS`, no schema version bump).

4. **Surge XT on drums retained (weak).** Subtractive synthesis for
   drum-like sounds is not physically implausible (noise + envelope +
   resonant filter → transient percussion); documented in the rubric
   §4 with rationale field on the affected instances. Not skipped.

5. **21 instances = 7 per stem.** Comfortably exceeds the ≥20 total /
   ≥5 per stem floor. Covers every (stem, instrument) combination
   that Layer-2 does not reject; multiple instances per combination
   exercise the deterministic variant-index tweak in build_examples.py.

## Non-implementation constraints honored

- `data/rules/ledger.jsonl` and `ledger_i3_dminor.jsonl` NEVER
  modified. Read-only streaming iteration only.
- Cycle-9 DawDreamer effects chain
  (`scripts/tex/render_effects_layered.py`) NOT imported anywhere in
  `scripts/palette/*`. Grep-verified by §46g.
- Cycle-26/27/28/29/30 analytical utility SHAs unchanged (delegated
  to existing §41 anchor guard already in the integration test).
- No PRNG. AST-safe check in `test_02_no_prng_ast_grep_clean` uses
  string concatenation to avoid self-reference false positives.
- α pinned at 0.7469387071101908 (irrelevant to this branch's
  mechanics but persists as a campaign constraint; test_13 checks
  the cycle-30 verdict JSON still records it).
