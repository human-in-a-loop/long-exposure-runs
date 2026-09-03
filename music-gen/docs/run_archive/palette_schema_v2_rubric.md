<!--
created: 2026-08-29T07:00:00Z
cycle: 34
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-schema-v2
-->

# Palette schema v2 — frozen 2-verdict rubric (cycle 34, Branch A, clone-0)

**Committed BEFORE any Python script under `scripts/palette_v2/`.**
The SHA-256 of this file is recorded in `data/palette_v2/rubric_hash.txt`
and embedded verbatim in `data/palette_v2/schema/verdict.json` under
key `rubric_hash`. Any post-freeze edit to this document invalidates
the verdict. File-mtime + git-log ordering is enforced by
`tests/test_palette_schema_v2.py::test_rubric_committed_before_scripts`.

**Milestone:** `M-DAW-SPIKE-1/palette-schema-v2` — new peer sub-milestone
under `M-DAW-SPIKE-1` per c29 state-machine lemma. NOT a child of the
terminal-validated `M-DAW-SPIKE-1/palette-assignment-schema`,
`M-DAW-SPIKE-1/palette-instrument-determinism`, or
`M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround`.

**Scope:** peer schema authoring only. Ships `palette_v2.json` as a
NEW file — the frozen c31 `palette_v1.json` is NOT edited. No
rendering. Cycle 35+ palette-driven bare-render + batch generation
will consume this v2 schema to unblock Surge XT + Dexed via the c33
Branch B `pinned_state_v2` P1 (`get_parameter(i)`-iterated) format.

## §1 Verdict enum (binary — no PARTIAL)

**SCHEMA_V2_LANDS** — every condition (a)–(o) in §2 is met exactly.

**SCHEMA_V2_INSUFFICIENT** — any condition in §2 is unmet. The report
§10 explains which criterion + why, and documents whether a
redefined-contract path is warranted (e.g., iteration_size discrepancy
across plugins) or the branch simply falls short.

## §2 Named conditions (all required for SCHEMA_V2_LANDS)

(a) **Valid instances** — ≥16 synthetic v2 instances validate under
both Layer 1 (JSON Schema draft 2020-12) and Layer 2 (cross-row).
Coverage: drums, bass, other, mono stems × Surge XT and Dexed only;
≥4 per stem.

(b) **Planted-invalid coverage** — ≥8 planted-invalid v2 instances
(one per rejection class named in §5) each rejected with a specific
field-named error message.

(c) **`assignment_id_v2` determinism × 2** — TSV byte-equal across two
fresh independent builds. SHA-256 of `assignment_ids_v2_expected.tsv`
identical.

(d) **Validator round-trip** — validator does not mutate its input;
canonical-JSON form is preserved.

(e) **JSON + YAML load-identical** — `json.load(palette_v2.json) ==
yaml.safe_load(palette_v2.yaml)` deep-equal.

(f) **`additionalProperties: false` recursive audit** — every
object-level definition in the JSON Schema carries
`"additionalProperties": false` OR is explicitly under a
`patternProperties` parent.

(g) **Palette-v1 backwards-compat** — ≥3 c31 palette-v1 assignments
(READ-ONLY from `scripts/palette/schema/examples/{drums,bass,other}/*.json`)
validate under the v2 validator via the `format=v1_flat` path.

(h) **Rubric SHA committed before scripts** — earliest mtime under
`scripts/palette_v2/*.py` is strictly greater than mtime of
`docs/palette_schema_v2_rubric.md`; git-log fallback confirms the
same order.

(i) **Test count** — ≥14 test cases in
`tests/test_palette_schema_v2.py`, all PASS.

(j) **Cross-branch integration** — §51 in
`tests/test_integration_cross_branch.py` PASSES with palette-schema-v2
invariants.

(k) **Rubric hash consistency** — `data/palette_v2/rubric_hash.txt`
byte-equal to the SHA-256 of `docs/palette_schema_v2_rubric.md`; the
same string appears verbatim in `data/palette_v2/schema/verdict.json`
under `rubric_hash`.

(l) **c31 palette-v1 anchor SHAs unchanged** — SHA manifest of
`scripts/palette/*`, `data/palette/schema/*`, `docs/palette_assignment_schema_*.md`
byte-identical before/after this branch.

(m) **c33 dawdreamer_state P1 anchor SHAs unchanged** — SHA manifest
of `data/dawdreamer_state/per_plugin/{surge_xt,dexed}/p1_state_v2.json`
+ `p1_state_sha` byte-identical before/after.

(n) **No PRNG** — AST-grep on `scripts/palette_v2/`: no `import random`,
`numpy.random`, `secrets.` usage.

(o) **Rules ledgers unmodified** — SHA of `data/rules/ledger.jsonl`
and `data/rules/ledger_i3_dminor.jsonl` byte-identical before/after.

## §3 Schema-v2 contract (authoritative summary)

Root object required fields: `schema_v` (const `"palette_v2"`),
`assignment_id_v2` (UUID5 hex, 32 lowercase hex chars),
`stem` (`drums|bass|other|mono`), `instrument` (`surge_xt|dexed|sfizz|fluidsynth_gm`),
`pinned_state` (discriminated union on `format`),
`provenance_pointers` (sorted-lex list of `rule_[0-9a-f]{16}` strings),
`extractor_version` (const `"palette_v2_c34"`). Optional:
`notes_optional`.

`pinned_state.format ∈ {"v1_flat", "v2_iterated_params"}` is the
discriminator.

- **v1_flat** variant (backwards-compat READ path): matches c31
  `pinned_state` verbatim — `{plugin_name, plugin_version, parameter_dict,
  preset_name_optional, external_state_sha_optional}` with
  `additionalProperties: false`. Layer 2 rejects if `instrument ∈
  {surge_xt, dexed}` on a v2 row (VST3 rows MUST use v2_iterated_params).

- **v2_iterated_params** variant: `{plugin_name, plugin_version,
  iterated_params, iteration_size, iteration_sha_256}` with
  `additionalProperties: false`. `iterated_params` is a strict
  `additionalProperties: false` object whose key set MUST exactly
  equal the c33 P1-output anchor key set for the named `plugin_name`
  (Layer 2 loads the frozen key set from
  `data/dawdreamer_state/per_plugin/<plugin>/p1_state_v2.json`,
  READ-ONLY). `iteration_size == len(iterated_params)` AND
  `iteration_sha_256 == sha256(canonical_json(iterated_params))`.

`assignment_id_v2` = `uuid5(NAMESPACE_PALETTE_V2, canonical_json(row-minus-notes_optional))`
where `NAMESPACE_PALETTE_V2 = uuid5(NAMESPACE_URL,
"palette_v2::music-gen::c34") = 063eb50e-0aac-59bb-84a8-ef26540a8912`.
This is DISTINCT from the c31 v1 namespace
`44e07e49-d932-519e-8f5c-583c960bb37e`, guaranteeing no v1↔v2
`assignment_id` collision.

## §4 Layer 2 cross-row checks

1. Duplicate `assignment_id_v2` rejection (with reference to earlier-seen
   file path).
2. Provenance-pointer resolvability against both rules ledgers (streaming,
   READ-ONLY).
3. `format=v2_iterated_params`: `iterated_params` key set === anchored
   P1-output key set for `plugin_name`.
4. `format=v2_iterated_params`: `iteration_size == len(iterated_params)`
   AND `iteration_sha_256 == sha256(canonical_json(iterated_params))`.
5. `format=v2_iterated_params`: `plugin_version` matches the c33
   dawdreamer_state anchor's plugin_version.
6. `plugin_name ∈ {surge_xt, dexed, sfizz, fluidsynth_gm}`; unknown
   `plugin_name` rejected.
7. `provenance_pointers` sorted-lex canonical-form check (unsorted or
   duplicate rule_ids rejected).
8. v2 row with `format=v1_flat` and `instrument ∈ {surge_xt, dexed}`:
   rejected (VST3 v2 rows MUST use v2_iterated_params).

## §5 Planted-invalid rejection classes (≥8 required)

1. `missing_format_discriminator` — `pinned_state` omits `format`.
2. `v2_iterated_with_v1_fields` — `format=v2_iterated_params` but
   pinned_state includes `parameter_dict` (v1 field).
3. `iterated_params_key_set_mismatch` — `iterated_params` has an extra
   key not in the c33 P1-output anchor.
4. `iteration_sha_256_mismatch` — `iteration_sha_256` does not equal
   the canonical-JSON SHA of `iterated_params`.
5. `plugin_version_mismatch` — `plugin_version` string does not match
   the c33 dawdreamer_state anchor.
6. `unknown_plugin_name` — `plugin_name: "foobar"`.
7. `provenance_pointer_not_found` — rule_id string that resolves
   nowhere in either rules ledger.
8. `provenance_pointer_unsorted` — provenance_pointers list not in
   lexicographic order.

## §6 Skip manifest

sfizz + fluidsynth_gm rows MUST use `format=v1_flat` (v2 skip reason
`format_v1_flat_only`). v2's `format=v2_iterated_params` variant is
enforced by Layer 2 to appear ONLY when `instrument ∈ {surge_xt,
dexed}`.

## §7 Fixed decisions binding (from `music_gen_long_exposure_prompt.md`)

- SHA-256 tiebreak, NO PRNG.
- Interpreter guard `/usr/bin/python3` on every script.
- No `sidecar_nonfactor` imports.
- JSON Schema draft 2020-12 with `additionalProperties: false` everywhere.
- Never delete files; scratch → `tools/stale/`.
- Ledger hygiene: `narrative`, pinned `run_id = "run-2026-08-28T040704Z"`,
  nested `confidence: {level, rationale, assessor}`, UUID5 event_id.

## §8 Anti-patterns

Do NOT re-attempt: c8 basic-pitch octave suppression, c11 CLAP fetchability,
c22 synthetic-label stability audit, c23 head regularization, c25
feature representation. These have been terminally invalidated on the
55-clip synthetic-label valset.
