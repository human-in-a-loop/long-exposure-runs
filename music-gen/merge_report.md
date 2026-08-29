# Merge Report — cycle 34 Branch A (clone-0, fork 43802db1a81c)

**NOTE ON PATH**: The brief specified
`/home/user/music-gen-instance/fork-43802db1a81c/clone-0/merge_report.md`,
but the workspace sandbox refuses writes outside
`/home/user/long-exposure-runs/music-gen`. Following the c31 Branch B
precedent, this merge report lands at the workspace-root fallback
`merge_report.md`; the merge conductor picks up whichever path exists.

## Milestone

`M-DAW-SPIKE-1/palette-schema-v2` — new peer sub-milestone under
`M-DAW-SPIKE-1` per c29 state-machine lemma. Closes c33 auditor
deferred item (a).

## Verdict

**SCHEMA_V2_LANDS** — all 15 named rubric criteria (a)–(o) PASS.
Rubric SHA-256 (frozen 2026-08-29T07:00Z):
`ed737733c79848c9f84e7dc0bbd3421b2fbb6f8442e485c3bb3e3c553c452ec2`.

## Ledger events emitted (8 total; strict order)

| # | milestone_id | ts |
|---|--------------|----|
| 1 | `_infra/egress-probe-cycle-34-clone-0` | 07:05 |
| 2 | `_run/cycle_34_launched-clone-0` | 07:06 |
| 3 | `_plan/palette_schema_v2_rubric_frozen-clone-0` | 07:07 |
| 4 | `M-DAW-SPIKE-1/palette-schema-v2` (in-progress/medium) | 07:08 |
| 5 | `M-DAW-SPIKE-1/palette-schema-v2` (validated/high, SCHEMA_V2_LANDS) | 07:50 |
| 6 | `_run/cycle_34_closed-clone-0` | 07:55 |
| 7 | `_archive/cycle-34-scratch-clone-0` | 07:56 |
| 8 | `_infra/adopt-cycle34-tests-clone-0` | 07:57 |

Infra families all suffixed `-clone-0` per c32/c33 convention;
substantive `M-*` unsuffixed.

## Deliverables

**Docs:** `docs/palette_schema_v2_rubric.md`,
`docs/palette_schema_v2_report.md`.

**Scripts:** `scripts/palette_v2/{__init__.py, validate.py,
provenance.py, schema/palette_v2.json, schema/palette_v2.yaml,
schema/_build_yaml.py, schema/validate_all.py,
schema/examples/build_examples.py,
schema/examples/{drums,bass,other,mono}/*.json,
schema/examples/planted_invalid/*.json}`.

**Data:** `data/palette_v2/rubric_hash.txt`,
`data/palette_v2/anchor_preservation_before.json`,
`data/palette_v2/schema/{assignment_ids_v2_expected.tsv (SHA
0fa1d969…f44e0), validation_report.tsv, skip_manifest.json,
verdict.json}`.

**Tests:** `tests/test_palette_schema_v2.py` (23 cases, all PASS).
`tests/test_integration_cross_branch.py` §51 (17 checks, all PASS).

**Archived to `tools/stale/`:**
`_emit_cycle34_launch_events.py`, `_emit_cycle34_close_events.py`,
`_verify_determinism.py`, `_probe_p3.py`.

## Test + validation results

- `PYTHONPATH=. /usr/bin/python3 tests/test_palette_schema_v2.py` → **23/23 pass**.
- `PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py` → **§51: 17/17 pass** (3 pre-existing failures in sibling clone-2's §53 on `scripts/gen_palette_batch_v1/__init__.py` — unrelated to Branch A).
- `promise_check .` → **0 ERRORs**.

## Key facts for the conductor

- `NAMESPACE_PALETTE_V2 = 063eb50e-0aac-59bb-84a8-ef26540a8912`
  (distinct from c31 v1 namespace `44e07e49-d932-519e-8f5c-583c960bb37e`).
- v2 `stem` enum now includes `mono` (NEW in v2).
- v2 `pinned_state.format ∈ {v1_flat, v2_iterated_params}`; v2_iterated_params
  enforced VST3-only by Layer 2.
- c31 palette-v1 `palette_v1.json` NOT edited — this is a PEER schema.
- c33 dawdreamer_state P1 anchors `p1_state_v2.json` + `p1_state_sha` for
  surge_xt + dexed are READ-ONLY; test-verified byte-identical before/after.
- `_ANCHOR_PLUGIN_VERSIONS` currently hard-coded in
  `scripts/palette_v2/provenance.py` as `{surge_xt: "1.3.4", dexed: "0.9.9"}`;
  §11 of the report flags freezing this into
  `data/palette_v2/anchor_manifest.json` as cycle-35 follow-up.

## Egress state

`workspace/harvest_playlists.sh` returned exit-0 with 0 audio files
retrieved across bands 6/5/4 (http_code=403 on media). Ear-band
ingestion still gated on the c26 armed-harness contract (two
consecutive `media_ok=true`).

## Ledger baseline

Pre-branch ledger: 501 rows. Post-branch: 509 rows (+8 events).
