<!--
created: 2026-08-29T02:30:00Z
cycle: 31
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-assignment-schema
-->

# Palette assignment schema — report (cycle 31, Branch B)

**Fork:** `cfc5009aca96` / clone-1 (Branch B of a 3-branch parallel cycle).
**Milestone:** `M-DAW-SPIKE-1/palette-assignment-schema` (new peer
sub-milestone under `M-DAW-SPIKE-1`).
**Verdict:** **PASS** under the frozen rubric (SHA-256
`1493818cb276344e817a965c6d8b9d3cbfe02607e7cd741fdc46a1b3560ebce9`).
**Scope:** schema-authoring only. NO rendering, NO plugin invocation.

## 1. Context and cycle-30 arc-close recap

Cycle 30 closed the collision-modeling explanatory arc as
`PARTIAL_BP_UNRESOLVED_SHAPE`: aggregate BP-scaled fit stands with
α pinned at 0.7469387071101908; the per-rule_type shape residual
(R² = −0.869) has no known mechanism after four auditor-named
probes (M1 coherence-gate, M2 effective-K, M3 hash-space geometry,
M4 semantic-cluster overlap). That arc has no bearing on this
branch's mechanics — this branch delivers the schema interface for
cycle 32's palette-driven bare-render implementation.

The operator steering (2026-08-28) named "render realism" the
primary priority, with the instrument palette expanding from
GM-soundfont-only rendering to the four-instrument set
{surge_xt, dexed, sfizz, fluidsynth_gm}. This branch specifies
the typed assignment interface that per-batch bare-render will
consume, without invoking any of those plugins itself.

**Independence from siblings.** Branch A probes per-instrument
determinism under the render harness. Branch C reinforces the
armed-harness fixtures. Branch B (this branch) authors the
assignment schema independent of both: the schema accepts any
(stem, instrument) row Layer-2 does not reject, and cycle 32's
render module consumes BOTH this schema AND Branch A's
determinism verdicts to decide which instruments to invoke.

## 2. Frozen success rubric

The rubric was committed at `docs/palette_assignment_schema_rubric.md`
BEFORE any implementation script was written. Its SHA-256 is
recorded in `data/palette/schema/rubric_hash.txt` and verified by
`test_11_rubric_hash_matches_committed_doc`. Any post-commit edit
to the rubric surfaces as a test failure.

**PASS conditions** (all six):
- (a) All ≥20 synthetic instances validate under both Layer 1
  and Layer 2 with zero errors.
- (b) ≥8 planted-invalid classes rejected with specific messages
  naming the offending field.
- (c) `assignment_id` determinism verified × 2.
- (d) Validator round-trip preserves canonical form.
- (e) JSON and YAML schema variants load-identical.
- (f) `additionalProperties: false` at every object level.

**REDEFINED_CONTRACT** (falsifiability escape hatch): first-class
negative finding permitted if any (a)–(f) is empirically
unachievable. Report §6 would then name the specific constraint.

**Observed:** all six conditions met (§6 remains empty of
weakenings). Verdict = **PASS**.

## 3. Schema design decisions

The authoritative artifact is `scripts/palette/schema/palette_v1.json`
(JSON Schema draft 2020-12). A YAML mirror
`scripts/palette/schema/palette_v1.yaml` is emitted deterministically
by `scripts/palette/schema/_build_yaml.py` and asserted equal at
every level by `test_03_json_yaml_load_identical`.

### 3.1 Top-level row shape

```json
{
  "schema_v": "palette_v1",
  "assignment_id": "<UUID5 hex, 32 lowercase hex chars>",
  "stem": "drums | bass | other",
  "instrument": "surge_xt | dexed | sfizz | fluidsynth_gm",
  "pinned_state": { ... },
  "provenance_pointers": [ "rule_<16hex>", ... ],
  "extractor_version": "palette_v1_c31",
  "notes_optional": "<free-text authoring note>"
}
```

`additionalProperties: false` at every object level. `stem` and
`instrument` are enums; the schema does NOT encode compatibility
between them (see §3.3).

### 3.2 pinned_state sub-object

Matches Branch-A's serialization lemma verbatim: `plugin_name`,
`plugin_version`, `parameter_dict`, optional `preset_name_optional`,
optional `external_state_sha_optional` (64-hex SHA-256 of any
external state file the plugin loads).

`parameter_dict` uses `patternProperties` with pattern
`^[a-zA-Z0-9_/. -]+$` on keys (accommodates plugin UI names like
`"Osc 1 Type"` and file paths like `"presets/palette/base.sfz"`);
values are `["number", "string", "boolean"]`.

### 3.3 Stem × instrument compatibility matrix

Encoded via Layer-2 skip-list rather than via schema `oneOf`
constructs. Rationale: the schema stays trivial (six required
fields; no branch dispatch), and Layer-2 can quote a
human-readable rejection reason.

| stem  | fluidsynth_gm | sfizz | surge_xt | dexed |
|-------|:-------------:|:-----:|:--------:|:-----:|
| drums | ✓             | ✓     | ✓ (weak) | ✗     |
| bass  | ✓             | ✓     | ✓        | ✓     |
| other | ✓             | ✓     | ✓        | ✓     |

Dexed × drums is the only skip cell. Recorded in
`data/palette/schema/skip_manifest.json` with rationale. Rejected
by `scripts/palette/validate.py`'s `SKIP_COMBOS` frozenset with
message `"stem=drums × instrument=dexed is in skip list …"`.

### 3.4 assignment_id construction

`assignment_id = uuid.uuid5(NAMESPACE_PALETTE_V1, canonical_json).hex`

where `NAMESPACE_PALETTE_V1` is a content-derived UUID5 pinned in
`scripts/palette/provenance.py` (derived from
`uuid.uuid5(uuid.NAMESPACE_URL, "palette_v1::music-gen::c31")`),
and `canonical_json` is `json.dumps(payload, sort_keys=True,
separators=(",", ":"), ensure_ascii=True)` over the six
`_HASHED_FIELDS`: `schema_v`, `stem`, `instrument`, `pinned_state`,
sorted `provenance_pointers`, `extractor_version`.

`notes_optional` is EXCLUDED from the hash. Rationale: authoring
notes evolve independently of the assignment's operational
identity; excluding them lets a curator edit a note without
churning downstream references.

## 4. Two-layer validator design

Mirrors the cycle-6 M-RULES-1/schema pattern verbatim.

**Layer 1 (mechanical):** `jsonschema.Draft202012Validator` against
`palette_v1.json`. Iterates over errors and formats them as
`"schema:<json-path>:<msg>"`.

**Layer 2 (semantic, hand-written):**
- assignment_id hash consistency (compute vs declared).
- stem × instrument not in `SKIP_COMBOS`.
- provenance_pointers non-empty; every element resolvable against
  the union of `data/rules/ledger.jsonl` + `ledger_i3_dminor.jsonl`
  (streaming read, no full-load; `known_rule_ids()` computes the
  86-element set once and reuses across a batch).
- pinned_state.external_state_sha_optional matches `^[0-9a-f]{64}$`
  (Layer 1 already checks; Layer 2 re-checks defensively).

**Contract invariants:**
- Every function returns `list[str]` of error messages. Empty = success.
- NEVER raises on validation failure. NEVER partial-crashes.
- Every field access `.get()`-guarded (inheriting the lesson from
  M-INGEST-1 provenance MODERATE-2).
- Non-factor isolation: `scripts.classifier.sidecar_nonfactor` NOT
  imported (grep-verified by §46f).

`validate_batch(rows)` extends Layer 2 with duplicate-`assignment_id`
detection across the batch — the ONLY class of failure that is
undetectable per-row.

## 5. Synthetic instance corpus

21 valid instances shipped, 7 per stem, distributed as:

| stem  | fluidsynth_gm | sfizz | surge_xt | dexed | total |
|-------|:-------------:|:-----:|:--------:|:-----:|:-----:|
| drums | 2             | 2     | 3        | 0     | 7     |
| bass  | 2             | 2     | 2        | 1     | 7     |
| other | 2             | 2     | 2        | 1     | 7     |
| **total** | **6**     | **6** | **7**    | **2** | **21**|

Every instance's `pinned_state` uses plausible, plugin-specific
parameter names (e.g. Surge XT `"Osc 1 Type": "Classic"`, Dexed
`"Algorithm": 5`, sfizz `"sample_path": "presets/palette/base.sfz"`,
fluidsynth `"bank": 0, "preset_num": 33`). Deterministic per-variant
tweaks (variant index → single-parameter increment) ensure distinct
assignment_ids across rows with the same (stem, instrument).

`provenance_pointers` on every row references at least one rule_id
that is verified to resolve against the actual rules ledgers
(streaming lookup; `test_08_provenance_pointer_resolvability`
enumerates all 27 pointer-instance pairs). The 86-element universe
of resolvable rule_ids is the union of `data/rules/ledger.jsonl`
(76 rows) and `data/rules/ledger_i3_dminor.jsonl` (86 rows).

`data/palette/schema/assignment_ids_expected.tsv` records
(relpath, assignment_id) for every synthetic instance. Determinism
× 2 (test_05): SHA-256 of this TSV is byte-equal across two
independent runs of `build_examples.py` in a wiped output
directory. Observed:
`9c30baeb388c0e3271eebba62af411ab4d799cfddf99ccfcd68003d7172c2d32`.

## 6. Planted-invalid corpus + validation-report table

11 planted-invalid files covering 10 distinct rejection classes.
The rubric requires ≥8 classes with specific error messages naming
the offending field; observed = 10.

| # | class                                | offending field                    | layer | first error message excerpt                                  |
|---|--------------------------------------|-------------------------------------|-------|--------------------------------------------------------------|
| 1 | missing_assignment_id                | `assignment_id`                     | L1    | `schema:<root>:'assignment_id' is a required property`       |
| 2 | malformed_assignment_id (non-hex)    | `assignment_id`                     | L1    | `schema:assignment_id:… does not match '^[0-9a-f]{32}$'`     |
| 3 | wrong_stem (not in enum)             | `stem`                              | L1    | `schema:stem:'vocals' is not one of ['drums','bass','other']`|
| 4 | wrong_instrument (not in enum)       | `instrument`                        | L1    | `schema:instrument:'moog_minimoog' is not one of …`          |
| 5 | external_state_sha 63-char hex       | `external_state_sha_optional`       | L1    | `schema:pinned_state/external_state_sha_optional:… pattern`  |
| 6 | pinned_state extra top-level key     | `unknown_field`                     | L1    | `schema:pinned_state:Additional properties are not allowed`  |
| 7 | assignment_id mismatch (Layer 2)     | `assignment_id`                     | L2    | `assignment_id mismatch: declared=…, computed_from_canonical=`|
| 8 | provenance_pointers unresolvable     | `provenance_pointers`               | L2    | `provenance_pointers[0] unresolvable: rule_id=… not found in`|
| 9 | Dexed × drums combo                  | `instrument`                        | L2    | `stem=drums × instrument=dexed is in skip list …`            |
| 10| duplicate_assignment_id (batch only) | `assignment_id`                     | L2b   | `duplicate_assignment_id: … first-seen at row[0]`            |

`data/palette/schema/validation_report.tsv` records
(relpath, layer_1_errors_count, layer_2_errors_count,
first_error_msg, expected_verdict, observed_verdict) for every
valid + planted-invalid instance and the batch-duplicate probe.
33 rows total. `expected_verdict == observed_verdict` for all 33
rows — asserted by §46d in the cross-branch integration test.

**No REDEFINED_CONTRACT weakenings.** All six rubric conditions
hold exactly. §6 records no falsifiability-escape invocation.

## 7. Determinism verification (× 2)

Two independent reproducibility surfaces are verified:

1. **assignment_ids_expected.tsv byte-equal across runs**
   (`test_05_assignment_id_determinism_two_runs`): wipe
   `scripts/palette/schema/examples/<stem>/*.json` and the TSV;
   invoke `build_examples.py` in a fresh subprocess; verify
   SHA-256 of the regenerated TSV matches the first-run SHA.
   Observed: identical
   `9c30baeb388c0e3271eebba62af411ab4d799cfddf99ccfcd68003d7172c2d32`.

2. **canonical JSON stable across two calls**
   (`test_07_validator_round_trip_canonical_form_preserved`):
   for every valid instance, `canonical_json_for_assignment_id`
   returns byte-identical output on repeated calls, and the
   instance validates cleanly. This is the "validator round-trip
   preserves canonical form" clause of rubric §2(d).

No PRNG anywhere. AST-safe check in `test_02_no_prng_ast_grep_clean`
verifies the four forbidden needles (`random.`, `np.random`,
`torch.rand`, `os.urandom`) do not appear in any of
`scripts/palette/*` or `tests/test_palette_assignment_schema.py`
(self-reference guard uses string concatenation to keep the test
file itself clean).

## 8. Cycle 32 handoff

**How cycle 32's palette-driven bare-render implementation must
consume this schema:**

1. **Load and validate every input row** through
   `scripts.palette.validate.validate_batch(rows)`. Reject the
   batch if any row surfaces a Layer-1 or Layer-2 error.

2. **Read Branch A's determinism verdicts** — Branch A publishes
   per-instrument determinism results under some
   `data/palette/determinism/*.json` path (its own report will
   document the exact location). For each row in the batch,
   look up the row's `instrument` field in the verdicts.

3. **Skip INDETERMINATE instruments.** If Branch A marks an
   instrument INDETERMINATE, the render module MUST NOT invoke
   it for any row; log a skip event and continue with the next
   row. This is the only cross-branch join point in cycle 32.

4. **Dispatch by (stem, instrument)** to the pinned_state.
   The `parameter_dict` is passed verbatim to the plugin loader.
   `preset_name_optional` and `external_state_sha_optional`
   are honored when the plugin exposes those interfaces.

5. **Record the assignment_id in the render output's provenance**
   so a downstream heuristics/ear scoring pass can join back to
   the assignment row deterministically.

**Constraints cycle 32 inherits from this branch:**

- The schema is v1 and stable. Any addition of a new stem, a new
  instrument, or a new pinned_state field must land under a new
  peer sub-milestone (`M-DAW-SPIKE-1/palette-assignment-schema-v2`)
  and MUST NOT edit `palette_v1.json`. Content-addressed
  assignment_id makes v2 rows distinguishable from v1 rows even
  when they share (stem, instrument) tuples.
- Dexed × drums remains a hard skip. Any evidence that Dexed can
  meaningfully render percussion must land in the plan-of-record
  before the skip is retired.
- `notes_optional` MUST NOT influence rendering. It is metadata
  for human authors; the render module ignores it.
- Provenance_pointer resolvability MUST be re-checked at render
  time (not just at build time) — the rules ledgers can grow
  between authoring and rendering; a pointer that resolved
  yesterday might resolve to a different rule tomorrow. (In
  practice, rules ledger append-only invariant guarantees
  existing rule_ids remain resolvable; the resolvability check
  is a defense in depth.)

**Branch B verdict:** **PASS** under the frozen rubric. All six
PASS conditions hold. No REDEFINED_CONTRACT weakenings invoked.
21 synthetic instances validate; 10 planted-invalid classes reject
with specific error messages; assignment_id determinism × 2;
canonical form preserved; JSON/YAML load-identical;
`additionalProperties: false` recursive audit passes. Ready for
cycle 32 consumption.
