<!--
created: 2026-08-29T02:00:00Z
cycle: 31
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-assignment-schema
-->

# Palette assignment schema — frozen success rubric (cycle 31, Branch B)

**Committed BEFORE implementation.** Verdict scripts read the SHA-256
of this file back and compare against the value recorded in
`data/palette/schema/rubric_hash.txt`. Any change to this document
after the first commit invalidates the verdict.

**Milestone:** `M-DAW-SPIKE-1/palette-assignment-schema` (new peer
sub-milestone under `M-DAW-SPIKE-1`; NOT a child of any
terminal-validated sibling).

**Scope:** schema authoring only. NO rendering, NO plugin invocation.
The schema specifies the assignment interface that cycle 32's
palette-driven bare-render implementation will consume. Independent of
Branch A's determinism verdicts.

**α:** pinned at 0.7469387071101908 elsewhere in the campaign;
irrelevant to this branch's mechanics but persists as a campaign
constraint.

---

## 1. Verdict enum (binary)

**PASS** — every one of the six named conditions below (§2 a–f) is
met exactly, without qualification.

**REDEFINED_CONTRACT** — one or more conditions could not be met
under reasonable schema-authoring effort; the report §6 documents
the specific constraint that had to weaken, the empirical reason,
the schema at its weakest passing state, and a concrete
recommendation for cycle 32.

There is NO PARTIAL. There is NO FAIL. A schema-authoring branch
either meets contract or ships a documented redefined-contract
first-class negative finding.

## 2. PASS conditions (all six must hold)

(a) **All synthetic instances validate.** ≥20 instances, at least
5 per stem (drums, bass, other), covering the stem-appropriate
instruments per the compatibility matrix (§4). Each validates
under both Layer 1 (jsonschema.Draft202012Validator) and Layer 2
(hand-written cross-row) with zero errors.

(b) **≥8 planted-invalid classes rejected with specific error
messages.** Each rejection message names the offending field. The
ten canonical classes are:
  1. Missing `assignment_id` (Layer 1 required-field failure).
  2. Malformed `assignment_id` (non-hex characters).
  3. Wrong `stem` (not in enum).
  4. Wrong `instrument` (not in enum).
  5. `pinned_state.external_state_sha_optional` = 63-char hex
     (Layer 1 pattern failure).
  6. `pinned_state` with an extra top-level key (Layer 1
     `additionalProperties: false` failure).
  7. `assignment_id` mismatch (Layer 2 hash-mismatch: id present
     but doesn't match canonical hash).
  8. `provenance_pointers` with an unresolvable rule_id string
     (Layer 2 resolvability failure).
  9. Dexed × drums combo (Layer 2 stem/instrument skip-list
     failure).
  10. Duplicate `assignment_id` across two rows in
      `validate_batch` (Layer 2 duplicate failure).

At least 8 of these 10 classes must be present in the planted
corpus and rejected with a specific, non-empty error message
naming the offending field.

(c) **`assignment_id` determinism verified × 2.** Two independent
runs of `scripts/palette/schema/examples/build_examples.py` (in
fresh temp working directories, no cached state) produce a
byte-identical `data/palette/schema/assignment_ids_expected.tsv`.

(d) **Validator round-trip preserves canonical form.** For every
valid instance, `canonical_json_for_assignment_id(row) → validate_row
→ canonical_json_for_assignment_id` is byte-identical.

(e) **JSON and YAML schema variants load-identical.**
`yaml.safe_load(open(palette_v1.yaml).read()) ==
json.load(open(palette_v1.json))` at every level.

(f) **`additionalProperties: false` recursive.** Every JSON Schema
object level in `palette_v1.json` — top-level, `pinned_state`,
`parameter_dict`, every subschema in `if/then` clauses — carries
`"additionalProperties": false`. Recursive audit in the test
suite passes.

## 3. Determinism constraints (branch-wide)

- Every new script begins with `assert sys.executable ==
  "/usr/bin/python3"`.
- No PRNG anywhere. AST-grep for `random.`, `np.random`, `torch.rand`,
  `os.urandom` returns empty across `scripts/palette/*` and
  `tests/test_palette_assignment_schema.py`.
- SHA-256 tiebreak for any deterministic sort.
- UUID5 content-hash for `assignment_id` construction (namespace
  pinned in `scripts/palette/provenance.py`).
- No `sidecar_nonfactor` imports anywhere in the module tree.

## 4. Stem × instrument compatibility matrix

| stem  | fluidsynth_gm | sfizz | surge_xt | dexed |
|-------|:-------------:|:-----:|:--------:|:-----:|
| drums | ✓             | ✓     | ✓ (weak) | ✗     |
| bass  | ✓             | ✓     | ✓        | ✓     |
| other | ✓             | ✓     | ✓        | ✓     |

- Dexed × drums is the only skip cell. Rationale: Dexed emulates
  the DX7, a 6-operator FM synthesizer with melodic voice
  architecture; it has no percussion voicing. The skip is
  recorded in `data/palette/schema/skip_manifest.json`, not in
  the schema. The schema accepts any (stem, instrument) row that
  Layer-2 does not reject.
- Surge XT on drums is retained (weak) with a documented
  rationale field in the instance itself (subtractive synth for
  drums is unusual but not forbidden).

## 5. Read-only anchor invariants

- `data/rules/ledger.jsonl` (76 rows) and
  `data/rules/ledger_i3_dminor.jsonl` (86 rows) are read only for
  provenance-pointer resolvability. The branch never appends or
  edits these files.
- Cycle-9 DawDreamer effects chain
  (`scripts/tex/render_effects_layered.py`) is not imported
  anywhere in `scripts/palette/*` (grep-verified).
- Cycle-26/27/28/29/30 analytical utilities SHAs unchanged
  (delegated to §41 anchor guard).

## 6. REDEFINED_CONTRACT protocol

If any (a)–(f) is empirically unachievable:
- Report §6 names the specific constraint that had to weaken.
- Report §6 gives the empirical evidence for the weakening.
- The verdict JSON records `verdict: "REDEFINED_CONTRACT"` with a
  `weakened_constraints` array naming each PASS letter that failed.
- The report §6 provides a concrete recommendation for cycle 32:
  either lift the weakening in the render module, or accept the
  redefinition durably.

## 7. Rubric hash verification

The verdict script computes the SHA-256 of THIS file and writes it
to `data/palette/schema/rubric_hash.txt`. The test
`test_11_rubric_hash_matches_committed_doc` asserts the recorded
hash equals a fresh recomputation. Any post-commit edit to this
document surfaces as a test failure.

## 8. Post-implementation invariants (for cycle 32 handoff)

- Cycle 32's palette-driven bare-render implementation consumes
  BOTH this schema AND Branch A's determinism verdicts (which
  instruments are byte-reproducible under the render harness).
- The render module MUST NOT invoke an instrument whose Branch-A
  verdict is INDETERMINATE.
- The render module MUST validate every input assignment row
  through `scripts/palette/validate.py` before dispatching.

**Rubric frozen. Verdict scripts read from here.**
