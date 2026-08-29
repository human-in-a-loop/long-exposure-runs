<!--
created: 2026-08-29T07:45:00Z
cycle: 34
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-schema-v2
-->

# Palette schema v2 — cycle 34 Branch A report (clone-0, fork 43802db1a81c)

**Verdict:** `SCHEMA_V2_LANDS` — all 15 rubric criteria (a)–(o) met.

**Rubric SHA-256 (frozen 2026-08-29T07:00:00Z):**
`ed737733c79848c9f84e7dc0bbd3421b2fbb6f8442e485c3bb3e3c553c452ec2`

Closes cycle-33 auditor deferred item (a). Ships `palette_v2.json` as
a PEER schema — the frozen c31 `palette_v1.json` is unedited. Cycle 35+
palette-driven bare-render + batch generation can now consume v2 to
dispatch Surge XT + Dexed via the c33 Branch B `pinned_state_v2`
(P1 `get_parameter(i)`-iterated) format.

---

## §1 Frozen rubric (verbatim)

The frozen 2-verdict rubric is committed at
`docs/palette_schema_v2_rubric.md` (SHA-256
`ed737733c79848c9f84e7dc0bbd3421b2fbb6f8442e485c3bb3e3c553c452ec2`).
Copy of that SHA in `data/palette_v2/rubric_hash.txt`; embedded
verbatim in `data/palette_v2/schema/verdict.json` under `rubric_hash`.

Verdict enum is binary — **SCHEMA_V2_LANDS** or
**SCHEMA_V2_INSUFFICIENT** — no PARTIAL variant. Fifteen named
conditions (a)–(o); all must PASS for SCHEMA_V2_LANDS.

## §2 Execution timeline

| Step | Time (UTC) | Artifact | SHA / count |
|------|-----------|----------|--------------|
| Egress probe | 07:05 | `workspace/harvest_playlists.sh` → media_ok=false / 0 files | http_code=403 (persistent) |
| Cycle launched | 07:06 | `_run/cycle_34_launched-clone-0` | ledger event |
| Rubric doc frozen | 07:00 | `docs/palette_schema_v2_rubric.md` | SHA `ed737733…52ec2` |
| Rubric SHA written | 07:07 | `data/palette_v2/rubric_hash.txt` | SHA matches doc |
| `_plan/palette_schema_v2_rubric_frozen-clone-0` | 07:07 | ledger event | — |
| `M-DAW-SPIKE-1/palette-schema-v2` in-progress | 07:08 | ledger event | — |
| c31 + c33 anchor snapshot | 07:10 | `data/palette_v2/anchor_preservation_before.json` | 52 files hashed |
| Schema JSON authored | 07:11 | `scripts/palette_v2/schema/palette_v2.json` | draft 2020-12, `additionalProperties:false` everywhere |
| Schema YAML mirror | 07:12 | `scripts/palette_v2/schema/palette_v2.yaml` | `yaml.safe_load == json.load` verified |
| Provenance module | 07:13 | `scripts/palette_v2/provenance.py` | NAMESPACE_PALETTE_V2 = `063eb50e-…-8912` |
| Validator | 07:14 | `scripts/palette_v2/validate.py` | 2-layer + 9 hand-written checks |
| Build examples | 07:15 | `scripts/palette_v2/schema/examples/build_examples.py` | SHA-256 tiebreak, NO PRNG |
| Valid instances built | 07:16 | 16 files across drums/bass/other/mono × surge_xt/dexed × 2 | — |
| Planted invalid built | 07:16 | 8 files (one per rejection class) | — |
| `validate_all.py` | 07:17 | `data/palette_v2/schema/{assignment_ids_v2_expected.tsv, validation_report.tsv, skip_manifest.json}` | assignment_ids TSV SHA `0fa1d969…f44e0` |
| Determinism × 2 | 07:18 | fresh-tempdir build twice | SHA-256 equal (`2d87c16e…d841`) |
| Test suite | 07:20 | `tests/test_palette_schema_v2.py` | 23/23 pass |
| Cross-branch §51 | 07:22 | extended `tests/test_integration_cross_branch.py` | 17/17 §51 checks pass |
| Verdict + report | 07:45 | this doc + `data/palette_v2/schema/verdict.json` | SCHEMA_V2_LANDS |

Read-only anchors that were **not** touched:
`scripts/palette/*`, `scripts/palette_probe/*`, `scripts/palette_render/*`,
`scripts/dawdreamer_state/*`, `data/palette/*`, `data/palette_probe/*`,
`data/palette_render/*`, `data/dawdreamer_state/*`,
`docs/palette_*_report.md`, `docs/palette_*_rubric.md`,
`docs/dawdreamer_state_*.md`, `data/rules/ledger*.jsonl`,
`long_exposure/workspace_bootstrap.py`. Byte-identity verified in
§9 below.

## §3 v2 schema contract summary

Root required fields: `schema_v` (const `"palette_v2"`),
`assignment_id_v2` (UUID5 hex, 32 lowercase hex chars),
`stem` ∈ `{drums, bass, other, mono}` (**`mono` NEW in v2**),
`instrument` ∈ `{surge_xt, dexed, sfizz, fluidsynth_gm}`,
`pinned_state` (discriminated union), `provenance_pointers`
(sorted-lex list of `rule_[0-9a-f]{16}`), `extractor_version`
(const `"palette_v2_c34"`). Optional: `notes_optional`.

### Discriminator table

| `pinned_state.format` | Required fields | Purpose | Layer 2 gate |
|-----------------------|-----------------|---------|---------------|
| `v1_flat` | `plugin_name, plugin_version, parameter_dict` (+ optional `preset_name_optional`, `external_state_sha_optional`) | Backwards-compat read path for c31 palette-v1 rows | Rejected when `instrument ∈ {surge_xt, dexed}` on v2 rows (VST3 MUST use v2_iterated_params) |
| `v2_iterated_params` | `plugin_name, plugin_version, iterated_params, iteration_size, iteration_sha_256` | New format for VST3 pinned state from c33 P1 iterate | `iterated_params` key set === c33 P1-output anchor for `plugin_name`; `iteration_size == len(iterated_params)`; `iteration_sha_256 == sha256(canonical_json(iterated_params))`; `plugin_version` matches anchor |

### Layer 2 cross-row rules

1. Duplicate `assignment_id_v2` (with earlier-file reference).
2. Provenance-pointer resolvability against both rules ledgers (streaming, READ-ONLY).
3. `iterated_params` key set === c33 P1 anchor (VST3).
4. `iteration_size` + `iteration_sha_256` self-consistency.
5. `plugin_version` matches c33 anchor.
6. `plugin_name ∈` known set (enforced on `v2_iterated_params`; `v1_flat` accepts c31 legacy names for backwards-compat).
7. `provenance_pointers` sorted-lex, no duplicates.
8. `v1_flat + instrument ∈ {surge_xt, dexed}` rejected.
9. `assignment_id_v2` recomputation consistency.
10. v1/v2 field-cross-contamination: `parameter_dict` in a v2_iterated_params
    row (or vice versa) emits a specific field-named message.

## §4 NAMESPACE_PALETTE_V2

`NAMESPACE_PALETTE_V2 = uuid5(NAMESPACE_URL, "palette_v2::music-gen::c34")
 = 063eb50e-0aac-59bb-84a8-ef26540a8912`.

DISTINCT from c31 `NAMESPACE_PALETTE_V1 = uuid5(NAMESPACE_URL,
"palette_v1::music-gen::c31") = 44e07e49-d932-519e-8f5c-583c960bb37e`.

Rationale: guarantees that no v1 `assignment_id` can collide with any
v2 `assignment_id_v2` (different UUID5 namespace → disjoint output
space). Also human-auditable: the seed strings differ deliberately
(`v1::…::c31` vs `v2::…::c34`), so future readers can reproduce both
UUIDs from the printed sources.

## §5 Synthetic-instance summary

**16 valid v2 instances** across `drums`, `bass`, `other`, `mono` × `surge_xt`, `dexed` × 2 salts each. All pass both validator layers. Per-stem × per-plugin count: **4 rows per stem** (2 per VST3 plugin).

| stem | surge_xt | dexed | total |
|------|----------|-------|-------|
| drums | 2 | 2 | 4 |
| bass  | 2 | 2 | 4 |
| other | 2 | 2 | 4 |
| mono  | 2 | 2 | 4 |
| **total** | **8** | **8** | **16** |

sfizz + fluidsynth_gm continue to be palette-v1-format-eligible only
(`skip_manifest.json.format_v1_flat_only`); v2's
`format=v2_iterated_params` variant is enforced VST3-only by Layer 2.

Full assignment_id_v2 table:
`data/palette_v2/schema/assignment_ids_v2_expected.tsv` (SHA-256
`0fa1d9696b2615a318239bffeb192a8ea3ba1161c92abe9caed372b9ac2f44e0`).

## §6 Planted-invalid summary

All 8 rejection classes present; each rejected with a specific
field-named error message.

| # | Class | Field named in error | First error message (excerpt) |
|---|-------|----------------------|--------------------------------|
| 01 | `missing_format_discriminator` | `format` | `schema:pinned_state:'format' is a required property` |
| 02 | `v2_iterated_with_v1_fields` | `parameter_dict` | `pinned_state.parameter_dict is a v1 field; not permitted with format=v2_iterated_params` |
| 03 | `iterated_params_key_set_mismatch` | `iterated_params` | `pinned_state.iterated_params key set does not match c33 P1-output anchor …` |
| 04 | `iteration_sha_256_mismatch` | `iteration_sha_256` | `pinned_state.iteration_sha_256 mismatch: declared=000…, computed…=…` |
| 05 | `plugin_version_mismatch` | `plugin_version` | `pinned_state.plugin_version mismatch vs c33 dawdreamer_state anchor for plugin_name=surge_xt: declared='9.9.9', anchor='1.3.4'` |
| 06 | `unknown_plugin_name` | `plugin_name` | `pinned_state.plugin_name unknown: 'foobar' not in [dexed, fluidsynth_gm, sfizz, surge_xt]` |
| 07 | `provenance_pointer_not_found` | `provenance_pointers` | `provenance_pointers[0] unresolvable: rule_id='rule_deadbeefdeadbeef' not found in …` |
| 08 | `provenance_pointer_unsorted` | `provenance_pointers` | `provenance_pointers must be lexicographically sorted (canonical form); got …` |

## §7 Palette-v1 backwards-compat evidence

Layer 1 + Layer 2 accept ≥3 c31 palette-v1 example rows when they are
re-authored as v2 rows with `pinned_state.format = "v1_flat"` and
`extractor_version = "palette_v2_c34"`. Test
`07_v1_backcompat` walks the c31 example directory (READ-ONLY),
translates each row into the v2 shape, recomputes `assignment_id_v2`,
and validates. **3 c31 rows PASS** (all on sfizz + fluidsynth_gm rows;
c31 surge_xt/dexed rows correctly refused under the v2 v1_flat+VST3
rejection rule per §3 gate 8).

## §8 Test-suite results

`PYTHONPATH=. /usr/bin/python3 tests/test_palette_schema_v2.py` — **23/23 pass**:

```
PASS 01_interpreter_guard
PASS 02_no_prng
PASS 03_no_cycle9_effects
PASS 04_no_cycle13_batch
PASS 05_no_sidecar
PASS 06_anchor_readonly
PASS 07_v1_backcompat
PASS 08_valid_instances
PASS 09_planted_01_format .. 09_planted_08_provenance_pointers  (8 cases)
PASS 17_determinism
PASS 18_json_yaml_identical
PASS 19_addlprops_false
PASS 20_rubric_before_scripts
PASS 21_v1_anchor_unchanged
PASS 22_c33_anchor_unchanged
PASS 23_verdict_json
```

`PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py` — **§51: 17/17 checks green** (parallel sibling clone-2 Branch C's §53 has 3 pre-existing failures on `scripts/gen_palette_batch_v1/__init__.py` — unrelated to this Branch A).

`PYTHONPATH=/home/user/human-in-a-loop/long-exposure:. /usr/bin/python3 -m long_exposure.tools.promise_check .` — **0 ERRORs**. Remaining WARNs are orphan-artifact warnings on brand-new files that are cleared by the `_infra/adopt-cycle34-tests-clone-0` housekeeping event listed in §10.

## §9 Read-only anchor preservation

`data/palette_v2/anchor_preservation_before.json` hashes 52 anchor
files at branch start. Tests §21 (c31 palette-v1: `scripts/palette/*`,
`data/palette/*`, `docs/palette_assignment_*`) and §22 (c33
dawdreamer_state P1: `data/dawdreamer_state/per_plugin/{surge_xt,dexed}/p1_state_v2.json`
+ `p1_state_sha`) both **PASS** — zero byte drift on any anchor.

## §10 Verdict against frozen 2-verdict rubric

**SCHEMA_V2_LANDS** — every named condition (a)–(o) in the rubric §2
resolves to PASS. Numeric summary:

- (a) **16 ≥ 16** valid instances validate under both layers.
- (b) **8 = 8** planted-invalid classes rejected with field-named errors.
- (c) **SHA-256 equal** across two fresh-tempdir builds
  (`2d87c16e121061a69a0575d4a26943f733fca77eeb31efeed9bd9b51c271d841`).
- (d) Validator round-trip preserves canonical form (no `parameter_dict`
  key re-ordering, no `iterated_params` mutation).
- (e) `json.load(palette_v2.json) == yaml.safe_load(palette_v2.yaml)`
  deep-equal.
- (f) `additionalProperties: false` at every object-level node
  (recursive audit, test 19).
- (g) **3 ≥ 3** c31 palette-v1 rows revalidate under v2 v1_flat path.
- (h) Rubric doc mtime ≤ min(script mtimes) with git-log fallback
  confirming same order.
- (i) **23 ≥ 14** tests green.
- (j) Cross-branch §51: 17/17 checks pass.
- (k) `data/palette_v2/rubric_hash.txt` byte-equal to SHA of rubric doc.
- (l) c31 palette-v1 SHA manifest byte-identical.
- (m) c33 dawdreamer_state P1 SHA manifest byte-identical.
- (n) AST-grep on `scripts/palette_v2/`: 0 `random`/`numpy.random`/`secrets` hits.
- (o) `data/rules/ledger.jsonl` + `data/rules/ledger_i3_dminor.jsonl`
  SHAs byte-identical.

## §11 Forward-look items for cycle 35

1. **Palette-driven bare-render extension (v2 dispatch)** — extend
   `scripts/palette_render/` to consume `assignment_id_v2` rows,
   hydrate the c33 P1 `iterated_params` state, and dispatch to
   Surge XT + Dexed via DawDreamer with the anchored parameter set
   applied per-parameter. Ships parity check against the c31 v1_flat
   render path for sfizz/fluidsynth_gm rows (which pass through v2's
   backwards-compat path unchanged).
2. **Palette-driven batch generation on v2** — extend
   `scripts/gen_palette_batch_v1/` (c34 Branch C) to accept v2
   assignments so a single batch can span all four instruments
   (sfizz + fluidsynth_gm under v1_flat, surge_xt + dexed under
   v2_iterated_params) without a schema fork.
3. **Provenance module streaming-read cache** — the current provenance
   module walks the rules ledgers on every `known_rule_ids()` call
   (~162 rows across both ledgers as of c33). At the cycle-35+ batch
   scale, adding a cache keyed on `(ledger_path, mtime)` cuts the
   validator's cold-start latency without changing determinism.
4. **v2 `mono` stem consumers** — `mono` is NEW in v2. Bare-render and
   batch pipelines need to grow a mono-mixdown branch that maps a
   single VST3 render to the mono stem taxonomy (as opposed to
   drums/bass/other separation), or the mono examples remain
   render-inert.
5. **c33 `pinned_state_v2` schema anchor lock** — freeze the
   `_ANCHOR_PLUGIN_VERSIONS` manifest (currently `{surge_xt: 1.3.4,
   dexed: 0.9.9}`) into a versioned data file under
   `data/palette_v2/anchor_manifest.json` so a future dawdreamer
   upgrade cannot silently drift the Layer 2 §5 check.

Egress remains blocked — `workspace/harvest_playlists.sh` returned
exit-0 with **0 audio files** across bands 6/5/4 (http_code=403 on
media). Ear-band ingestion continues to gate on two consecutive
`media_ok=true` per the frozen c26 armed-harness contract; no change
to that contract this branch.
