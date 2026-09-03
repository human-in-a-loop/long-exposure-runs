---
created: 2026-09-03T00:00:00Z
cycle: 25
run_id: fork-4c826786aced-clone-1
agent: worker
milestone: _infra/retire-oneoff-drivers-c22
---

# v3-Spine One-Off Driver Retirement — c25 clone-1 Report

## 1. Context

The c22 `_infra/retire-oneoff-drivers-c22` deletion contract at
`data/v3/recreate_v3/retirement_catalog_c22.json` gated 37 per-song
v3-spine driver scripts behind reproduce-proof green on both
Chicken Grease (`sha16 31a164f845f8e27e`) and Rome (`sha16
51e433ade2a845e1`) via the unified `recreate_v3.py --reproduce-check`
driver.

c23 clone-0 emitted both reproduce reports:

- Chicken Grease `data/v3/reproduce/c23/31a164f845f8e27e/reproduce_report.json`
  SHA `8b23c448afbc8596b0194549fb3402b0200badce197c84cf30de0873817d628c`,
  verdict `REPRODUCE_PANEL_ONLY`.
- Rome `data/v3/reproduce/c23/51e433ade2a845e1/reproduce_report.json`
  SHA `5cb0b78837d37cac1c3142ac715b2e99f2f3200445d986c59ae6307ca7a66a3b`,
  verdict `REPRODUCE_PANEL_ONLY`.

Both land at ≥ `REPRODUCE_PANEL_ONLY`; env-pin drift is documented and
expected for pre-c22 anchors. Deletion is authorized. This cycle
executes the move.

## 2. Rubric chain (three-way byte-equality)

| Position | Value |
| --- | --- |
| `docs/v3_spine_oneoff_driver_retirement_c25_rubric.md` SHA-256 | `0508ad553b8a10f0be05daf7d6ee7509393793fa34897ab461c0caeea8069e0c` |
| `data/v3/retirement/c25/rubric_hash.txt` content | `0508ad553b8a10f0be05daf7d6ee7509393793fa34897ab461c0caeea8069e0c` |
| `data/v3/retirement/c25/verdict.json.rubric_hash_v3_retirement` | `0508ad553b8a10f0be05daf7d6ee7509393793fa34897ab461c0caeea8069e0c` |

All three byte-equal; three-way chain holds.

Rubric doc mtime pre-dates every mtime under
`scripts/v3_spine/retirement_c25/` and
`tests/test_v3_spine_oneoff_driver_retirement_c25.py`
(test 01 enforces).

## 3. Move table

37 targets consumed verbatim from the catalog's `candidates` dict
(rome_51e433ade2a845e1 × 12, disco_a_cdd2717e52820ff6 × 12,
peach_dream_c20 × 13). Every file moved via `os.rename` from
`scripts/v3_spine/<basename>` to
`tools/stale/oneoff_v3_drivers_retired_c25/<basename>` with mtime
advanced via `os.utime` per the c38 lesson. SHA-256 preserved
byte-identical at destination.

`data/v3/retirement/c25/moves.jsonl` SHA
`bee8bcac8e05e5fedd7b87e5e29fab57cda589e0c19a4e27b2147c9dbc8e8bb6`.
Per-file rows follow the schema
`{basename, src, dst, sha256, mtime_pre, mtime_post, action}`.

Terminal state: 37/37 at destination. First run: 37 `renamed`; second
fresh subprocess run: 37 `already_moved` (idempotent branch — source
absent, destination present with SHA byte-equal to the pre-move value).
The moves.jsonl reflects the second-pass terminal state per the
byte-determinism ×2 protocol (see §6).

## 4. Grep-zero verification

`data/v3/retirement/c25/grep_zero_verification.json` SHA
`9e8fb9da78c7473d36be15984e658fd1734b917a46b4e3be1055c06b8b175731`.

- Scanned roots: `scripts/`, `tools/` (excluding `tools/stale/`),
  `tests/`, `data/`, `docs/`.
- Excluded: `tools/stale/`, `**/__pycache__/**`.
- File-type filter: `.py`, `.md`, `.json`, `.jsonl`, `.txt`, `.tsv`.
- Files scanned: **2,747**.
- Python-import patterns checked per stem:
  `from scripts.v3_spine.<stem> import …`,
  `import scripts.v3_spine.<stem>`,
  `from scripts.v3_spine import <stem>`.
- Literal-string pattern checked (non-`.py` only):
  `scripts/v3_spine/<stem>.py`.

**Result:** `python_import_matches = []`, `zero_broken_imports = true`.
Literal-string matches in non-py files (docs/data): 160 rows — these
are historical narrative references in reports, ledger events, and
manifests, not Python runtime imports; per the rubric they are
reported but do NOT gate `RETIREMENT_LANDS`.

## 5. Preserved-set anchor table

`data/v3/retirement/c25/anchor_preservation_pre.json` SHA
`86971bdc8b14970483260e36f3fce2f9442b62a46d882a30a06facb6874900ed`.
`data/v3/retirement/c25/anchor_preservation_post.json` SHA
`64bceb7098a2d84ba5312a5d85a2046537b3f7807d062fd8ccbf7cf67f7a69bf`.
`data/v3/retirement/c25/anchor_preservation_diff.json` SHA
`d8b38ead20a22bb194261f4d4c1d721e0de0304fa8041f9209ec8524b097fc3b`,
`n_diff = 0`, `all_match = true`.

**Count:** 61 preserved anchors (exceeds ≥25 rubric floor). Breakdown:

- 6 named single files: `recreate_v3.py`, `recreate_v3_checkpointed.py`,
  `stage_cache.py`, `launch_detached.py`, `midi_from_json_events.py`,
  `render_stem.py`.
- 2 rubric artifacts:
  `docs/v3_spine_oneoff_driver_retirement_c25_rubric.md`,
  `data/v3/retirement/c25/rubric_hash.txt`.
- 3 external references:
  `data/v3/rules/rules_artifact.jsonl` (c23 clone-2, SHA `e19fb205b282dabb…`),
  `data/v3/reproduce/c23/31a164f845f8e27e/reproduce_report.json`
  (SHA `8b23c448afbc8596…`),
  `data/v3/reproduce/c23/51e433ade2a845e1/reproduce_report.json`
  (SHA `5cb0b78837d37cac…`).
- 2 `scripts/v3_spine/v3_pipeline/*.py` (module + env_pin, latter SHA
  `ab6d54638faeb161…`).
- 12 `scripts/v3_spine/torch213_reproduce_probe_c*.py`.
- 15 `scripts/v3_spine/anchor_preservation_c*.py`.
- 17 `scripts/v3_spine/verdict_c*.py`.
- 4 `scripts/**/*_ledger.py` (excluding the cataloged
  `peach_dream_c20_ledger.py` sibling, which is one of the 37 movers).

Explicit named-anchor verification (test 11):
- `scripts/v3_spine/recreate_v3.py` post-SHA byte-equal to the c22
  anchor `72e80ee82cd21dbd…`.
- `scripts/v3_spine/v3_pipeline/env_pin.py` post-SHA byte-equal to the
  c22 anchor `ab6d54638faeb161…`.
- `scripts/palette_render/render_stem.py` post-SHA has prefix
  `214372d920a319a9…` (c21 do-not-touch invariant preserved).

**Gate result:** `all_match = true`; preserved-set SHA-drift condition
does not fire.

## 6. Byte-determinism × 2

`data/v3/retirement/c25/byte_determinism.json` SHA
`09a1eb53605554e82753abe55495365b744457638dd6f144ed148665c4e146c6`.

Protocol: two fresh `subprocess.run(["/usr/bin/python3", "-c", …])`
invocations of `scripts.v3_spine.retirement_c25.move.move_all()` under
env pins `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
`LC_ALL=C.UTF-8`, single-thread BLAS.

The determinism SHA hashes only the
`{basename, sha256, action_class}` triples (timestamp fields excluded
so `mtime_pre`/`mtime_post` differences between first-run `renamed`
rows and second-run `already_moved` rows do not spuriously break the
gate). `action_class` collapses `renamed` and `already_moved` into
`moved`, so an idempotent second pass yields byte-identical determinism
SHA.

- First-run determinism SHA:
  `7a0c1941b57019f2ba2da6fcb3f35e1f3cac7f304f43f159c9da57a76be045cb`.
- Second-run determinism SHA:
  `7a0c1941b57019f2ba2da6fcb3f35e1f3cac7f304f43f159c9da57a76be045cb`.
- `byte_determinism_holds = true`.

## 7. Test suite (12 cases, all green)

`tests/test_v3_spine_oneoff_driver_retirement_c25.py` executed via
`PYTHONPATH=. /usr/bin/python3 tests/test_v3_spine_oneoff_driver_retirement_c25.py`.

| # | Case | Result |
| --- | --- | --- |
| 01 | `rubric_mtime_pre_registration` | PASS |
| 02 | `three_way_rubric_hash_chain` | PASS |
| 03 | `per_file_sha_preservation_across_rename` | PASS (37/37) |
| 04 | `grep_zero_import_assertion` | PASS (0 Python-import matches) |
| 05 | `preserved_set_sha_anchor_list` | PASS (61 entries; all_match) |
| 06 | `catalog_vs_actual_consistency` | PASS (37/37 resolvable) |
| 07 | `idempotence` | PASS |
| 08 | `interpreter_guard_on_retirement_script` | PASS |
| 09 | `no_prng_grep` | PASS (AST-clean) |
| 10 | `no_sidecar_nonfactor_grep` | PASS |
| 11 | `c22_anchor_pre_post_byte_identical` | PASS |
| 12 | `vst3_state_api_ast_forbidden` | PASS (AST-clean) |

Ran 12 tests in 0.010s — OK.

## 8. Verdict

**`RETIREMENT_LANDS`** — all three AND-conditions hold:

1. 37 targets moved (first run) and idempotently detected as
   already-moved on the fresh second subprocess (both cases produce
   post-move SHA byte-equal to the pre-move value at destination).
2. Grep-zero returned 0 Python-import matches across 2,747 scanned
   files.
3. Preserved-set anchor diff is empty (61/61 entries pre==post).

Per-file honest reasons: `[]` — no missing sources; no partial moves.

## 9. Ledger events emitted (6 named + 2 housekeeping + 1 egress-probe)

Auto-suffixed to `-clone-1` via the c33 harness namespace guard for
`_infra/*`, `_archive/*`, and `M-INGEST-1/egress-probe-cycle25`:

1. `_infra/retire-oneoff-drivers-c22/rubric-committed-clone-1`
2. `_infra/retire-oneoff-drivers-c22/catalog-consumed-clone-1`
3. `_infra/retire-oneoff-drivers-c22/moves-emitted-clone-1`
4. `_infra/retire-oneoff-drivers-c22/grep-zero-verified-clone-1`
5. `_infra/retire-oneoff-drivers-c22/anchor-preservation-verified-clone-1`
6. `_infra/retire-oneoff-drivers-c22/verdict-emitted-clone-1`
7. `_archive/cycle-25-scratch-clone-1` (housekeeping)
8. `_infra/adopt-cycle25-tests-clone-1` (housekeeping)
9. `M-INGEST-1/egress-probe-cycle25-clone-1`

All 9 landed via `long_exposure.tools.ledger_append` with the canonical
`run_id: fork-4c826786aced-clone-1` and short-form
`confidence.assessor: worker`. UUID5 content-hash `event_id`s
auto-derived by the writer.

## 10. Handoffs / uncertainties

- **Substantive infra-milestone closure signal:** the six-named
  `_infra/retire-oneoff-drivers-c22/*-clone-1` sub-leaves + the c22
  parent's now-satisfied deletion contract collectively close the
  milestone. If the root conductor needs an explicit unsuffixed closure
  event on `_infra/retire-oneoff-drivers-c22` (as opposed to
  suffixed sub-leaves), that can be emitted from root scope in a
  post-merge integration cycle (auto-suffix does not fire outside a
  fanout clone context per the c33 guard).
- **Literal-string references in docs/data:** 160 non-Python literal
  references to `scripts/v3_spine/<stem>.py` remain in narrative
  reports, ledger events, and manifests. Per the rubric, these do NOT
  break Python runtime; they are historical audit-trail entries. No
  action required. A future documentation refactor could rewrite these
  to point at the new destination path
  `tools/stale/oneoff_v3_drivers_retired_c25/<basename>`, but the
  ledger's `supersedes_path` mechanism already carries that provenance.
- **The catalog's "not_cataloged_reason" `*_ledger.py` entry** says
  policy `*_ledger.py` are preserved. The catalog's `peach_dream_c20`
  group includes `peach_dream_c20_ledger.py` as an explicit exception
  (it's an emitter, not a policy artifact). The catalog is authoritative
  per the operator directive; that file moves. The preserved-set anchor
  list correctly excludes it from the `scripts/**/*_ledger.py` glob.
- **Deferred deletion for c5/c20/c21 landing scripts** (per the
  catalog's `not_cataloged_reason.deliver.py, …`): the 24
  `*_operator_section*.py` + parent-dir siblings remain in
  `scripts/v3_spine/` pending explicit operator green-light. Not in
  scope for c25.
- **c26+ closure path per operator directive point 5:** palette proof →
  rules → ear → gen — proceeds independently of this cycle. Checkpointed
  driver is now standard vehicle.
