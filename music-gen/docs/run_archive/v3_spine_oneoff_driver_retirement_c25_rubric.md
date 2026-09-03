# v3-Spine One-Off Driver Retirement Rubric (c25)

**Milestone:** `_infra/retire-oneoff-drivers-c22`
**Cycle:** 25
**Clone:** clone-1 (fork 4c826786aced)
**Frozen:** author-mtime hard, git-log advisory per c46 `_plan/git-log-gate-policy-amendment` path (ii)

## Authorization

The c22 deletion contract at `data/v3/recreate_v3/retirement_catalog_c22.json`
is contingent on reproduce-proof green on BOTH Chicken Grease (sha16
`31a164f845f8e27e`) AND Rome (sha16 `51e433ade2a845e1`) via the unified
`recreate_v3.py --reproduce-check` driver. c23 clone-0 emitted:

- Chicken Grease reproduce_report.json SHA
  `8b23c448afbc8596a72e4c25e56d729b64b31d4a1ea72e3f34f45e9fdba9a648`,
  verdict `REPRODUCE_PANEL_ONLY`.
- Rome reproduce_report.json SHA
  `5cb0b78837d37cac6ce6b8ed4728d7f2f14b3f42d5dcc4d5f26e2f8dbf37b6a2`,
  verdict `REPRODUCE_PANEL_ONLY`.

Both verdicts land at ≥ `REPRODUCE_PANEL_ONLY`; env-pin drift is
documented and expected for pre-c22 anchors. Deletion is authorized.

## Contract (verbatim from operator directive, adapted per c22 catalog)

Move each of the 37 cataloged one-off drivers from `scripts/v3_spine/`
to `tools/stale/oneoff_v3_drivers_retired_c25/<original-basename>` via
`os.rename` (content-preserving) followed by `os.utime` to advance
mtime per the c38 lesson. Preserve the SHA-256 of every moved file
byte-identically at the destination. Move-mechanism script:
`scripts/v3_spine/retirement_c25/move.py`. Interpreter guard
`/usr/bin/python3` mandatory. Zero PRNG imports (retirement is a pure
content-addressed operation). Zero `sidecar_nonfactor` imports. AST-
forbidden: `save_state`, `get_state`, `save_preset`, `load_state`,
`set_state` (c31 STILL_GAP + c35 A anti-pattern locks).

## Frozen 3-verdict rubric

- **`RETIREMENT_LANDS`** — all three conditions AND-hold:
  1. All 37 cataloged files present at their destination path with
     SHA-256 byte-equal to their pre-move value.
  2. Grep-zero verification returns 0 broken imports across `scripts/`,
     `tools/` (excluding `tools/stale/`), `tests/`, `data/`, `docs/`.
  3. Every entry in the preserved-set anchor list (≥25 entries) has
     `pre_sha == post_sha`.
- **`RETIREMENT_PARTIAL`** — ≤35 of the 37 targets moved, with per-file
  honest reason recorded for each un-moved entry; preserved-set SHAs
  all match; no broken imports in preserved-set callers.
- **`RETIREMENT_FAILS`** — any preserved-set SHA drift OR any broken
  import in a preserved-set caller.

## Preserved set (strict, READ-ONLY across the retirement operation)

- `scripts/v3_spine/recreate_v3.py` (c22 unified driver, SHA
  `72e80ee82cd21dbd…`)
- `scripts/v3_spine/recreate_v3_checkpointed.py` (c24)
- Every file under `scripts/v3_spine/v3_pipeline/` (c22 stage module;
  `env_pin.py` SHA `ab6d54638faeb161…`)
- `scripts/v3_spine/stage_cache.py` (c24)
- `scripts/v3_spine/launch_detached.py` (c24)
- `scripts/v3_spine/midi_from_json_events.py` (c4 canonical serializer)
- `scripts/palette_render/render_stem.py` (SHA
  `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`)
- Every `scripts/v3_spine/torch213_reproduce_probe_c*.py`
- Every `scripts/v3_spine/anchor_preservation_c*.py`
- Every `scripts/v3_spine/verdict_c*.py`
- Every `scripts/**/*_ledger.py` EXCEPT `peach_dream_c20_ledger.py`
  (which is in the c22 catalog as a peach_dream_c20 sibling and moves).

Additionally pinned to the anchor manifest:

- c23 clone-2 rules artifact `data/v3/rules/rules_artifact.jsonl`
  (SHA `e19fb205b282dabb…`).
- c23 clone-0 Chicken Grease reproduce report
  (SHA `8b23c448afbc8596…`).
- c23 clone-0 Rome reproduce report
  (SHA `5cb0b78837d37cac…`).

## Three-way `rubric_hash_v3_retirement` chain (byte-equality required)

1. SHA-256 of `docs/v3_spine_oneoff_driver_retirement_c25_rubric.md`
   (this doc, after final save).
2. Content of `data/v3/retirement/c25/rubric_hash.txt` (single-line
   hex, no trailing newline).
3. Field `rubric_hash_v3_retirement` in
   `data/v3/retirement/c25/verdict.json`.

All three must be byte-equal.

## Byte-determinism × 2 (idempotence)

The move script must be idempotent. Two fresh `subprocess.run`
invocations under identical env pins must produce byte-identical
`moves.jsonl` when hashed over the `{basename, sha256, action_class}`
triples only (timestamp fields excluded from the determinism hash).
Second run detects each target already at destination and records
`action: already_moved` with no rename performed.

## Env pins

- `PYTHONHASHSEED=0`
- `SOURCE_DATE_EPOCH=1756463424`
- `TZ=UTC`
- `LC_ALL=C.UTF-8`
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`

Not strictly required for `os.rename` correctness — kept for
reproducibility across ancillary probes.

## FD-1 halt

On any preserved-set SHA drift OR broken import in the preserved-set
caller graph, emit `RETIREMENT_FAILS` honestly. Do not retry, tune,
or force closure.
