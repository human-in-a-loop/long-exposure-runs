# Final Audit — Stage 37 (test 13 of 23)

**Cycle:** final audit
**Stage index:** 37 of 48
**Slice focus:** c47 append-only anchor manifest + c48 harness/writer hardening v3 baseline replay + c46 line-745 UUID5 pinning
**Findings appended this stage:** 0

## Probes

### Probe 13.1 — c47 `_infra/anchor-manifest-v1` append-only integrity (18 → 19)

**Milestone under test:** `_infra/pin-source-date-epoch-anchor-clone-2` (c47 Branch C, validated/high).

**Evidence chain:**
- `data/anchor_manifest_v1.json` on disk: whole-file SHA-256 = `138f37a025304f09e34625ebe5bdf4bd03664e522b32f67225ff90374cf3b67f`.
- `data/deprecation_and_anchor_pin/source_date_epoch_pin.json` records `manifest_post_sha256` = `138f37a025304f09e34625ebe5bdf4bd03664e522b32f67225ff90374cf3b67f` → **byte-equal to current file** (whole-manifest preservation from c47 → present).
- `anchor_count` field = 19; `len(anchors)` = 19 — consistent.
- Anchor #19 record:
  - `anchor_id`: `env/SOURCE_DATE_EPOCH`
  - `cycle`: 47, `pinned_by`: `clone-2`, `pinned_cycle`: 47, `kind`: `env_pin`
  - `value`: `1756463424`
  - `value_sha256`: `8ac32472d175ff32e0723cd23fbf5c193b944ccb4ef1e022deec4306e112d2a4`
    - Recomputed `sha256(str(1756463424).encode("utf-8"))` = `8ac32472d175ff32e0723cd23fbf5c193b944ccb4ef1e022deec4306e112d2a4` → **match**.
  - `entry_sha256`: `30ebead368418cb1b49cce024f8aa45f59bb591dfc437f9bd9bbf19abc71e28c`
    - Recomputed `sha256(canonical_json({"key":..., "value":..., "value_sha256":...}))` = `30ebead368418cb1b49cce024f8aa45f59bb591dfc437f9bd9bbf19abc71e28c` → **match**.
- Pre-append snapshot at `data/deprecation_and_anchor_pin/anchor_preservation_pre.json` pins `manifest_pre_anchor_count` = 18 and `manifest_pre_sha` = `6dc917fe365a37ff87c3d72f45b3d433894221f8ebdbb36ed3beb5d44a7a821f`. The audit cannot recompute the pre-append file SHA today (the file was mutated within the c47 branch turn), but c47's own probe attested to it under the same rubric-hash chain that gates DEPRECATION_LANDS_AND_ANCHOR_PINNED.
- Note: `anchor_preservation_pre.json.anchors_pre` uses a REDUCED per-entry projection (only 5 keys per entry) versus the actual manifest entries which carry additional fields (`is_readonly`, `path_entries`, `pinned_by`, `pinned_cycle`). This is a snapshot-time serialization detail, not a manifest edit — the whole-file SHA equality against `manifest_post_sha256` is the load-bearing anchor and it holds.

**Verdict:** PASS. Append-only integrity from c47's post-append snapshot to the current file is byte-verified; the new entry (#19) is internally consistent (value_sha256 + entry_sha256 both self-verify).

### Probe 13.2 — c48 harness-v3 baseline replay (793 rows)

**Milestone under test:** `_infra/harness-and-writer-hardening-v3/baseline-replay-verified-clone-0` (c48 Branch A, validated/high).

**Evidence chain:**
- `data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl` on disk: 793 rows; SHA-256 = `c175d65a87bae90be2b8212fbfc0a547ff49964e5fbc30582fef2be5933871f3`.
- `baseline_manifest_sha.txt` content = `c175d65a…871f3` → **byte-equal**.
- `verdict.json.provenance.baseline_manifest_sha256` = `c175d65a…871f3` → **byte-equal**.
- Manifest schema: each row is `{lineno, event_id, milestone_id, canonical_sha256_pre_edit}`.
- **Re-execution of the baseline replay against the current `promise_ledger.jsonl` first 793 lines**: for each `i ∈ [1..793]`, `sha256(raw_line_bytes_i)` equals `manifest[i-1].canonical_sha256_pre_edit`. **0 / 793 mismatches** — all 793 pre-c48 rows byte-identical to their pre-edit state today, under both env-flag defaults OFF.
- Total current ledger row count: 920 (793 pre-c48 baseline + 127 post-c48 additions; append-only preserved).

**Verdict:** PASS. The c48 baseline replay contract — that the pre-existing 793 rows remain byte-identical after the `long_exposure/workspace_bootstrap.py` + `long_exposure/tools/_ledger_schema.py` edits — is empirically upheld today.

### Probe 13.3 — c46 line-745 UUID5 pinning under both flag states

**Milestone under test:** `_infra/harness-and-writer-hardening-v3/toggle-round-trip-verified-clone-0` (c48 Branch A, validated/high).

**Evidence chain:**
- `promise_ledger.jsonl` line 745: `event_id` = `658231db-5d86-56e5-8ca9-2a9bed7fdf9f`, `milestone_id` = `_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1`, `supersedes` = `91a17dc3-3ae0-58ef-99b3-52ba594a04c7` (present).
- `data/harness_and_writer_hardening_v3/line_745_divergence.json`:
  - `on_disk_event_id`: `658231db-5d86-56e5-8ca9-2a9bed7fdf9f`
  - `re_derived_supersedes_OUT_hash`: `658231db-5d86-56e5-8ca9-2a9bed7fdf9f`  ← flag OFF (default)
  - `re_derived_supersedes_IN_hash`:  `6366af60-acb7-5e3f-a2e5-89b47f42c82f`  ← flag ON
- Re-derivation via `long_exposure.tools._ledger_schema.content_hash_event_id_v2(row, include_supersedes=…)`:
  - `include_supersedes=False` → `658231db-5d86-56e5-8ca9-2a9bed7fdf9f` — **matches on-disk event_id** and c48 verdict's `c46_line_745_baseline_event_id`.
  - `include_supersedes=True`  → `6366af60-acb7-5e3f-a2e5-89b47f42c82f` — **matches** c48 verdict's `c46_line_745_alternate_event_id_under_flag`.
- Legacy `content_hash_event_id(row)` (pre-v3 API, which excludes only `event_id`+`ts` and therefore INCLUDES `supersedes` in the hash input) returns `6366af60-…` — consistent with the fixture's "supersedes IN" flavor.

**Verdict:** PASS. Both flag states of `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH` reproduce the pinned UUID5 values byte-exactly; the on-disk c46 line-745 event_id (`658231db-…`) is reproduced by the flag-OFF (default) canonicalization path, i.e. `supersedes` is excluded from the content hash.

## Findings

None this stage. All three probes PASS.

## Cross-stage cumulative
- Findings file rows so far: ~111 (5 CRITICAL, ~14 MODERATE, ~28 INFO; F40 previously retracted).
- No new findings appended by stage 37.

[OUTPUT: final_audit_stage]
Stage 37 (test 13/23): c47 anchor-manifest #19 append-only integrity PASS (whole-file SHA byte-equal to c47 post-append snapshot; anchor #19 value_sha256 + entry_sha256 self-verify); c48 harness-v3 baseline replay PASS (0/793 raw-line SHA mismatches on current ledger); c46 line-745 UUID5 pinning PASS both flag states via library re-derivation.
File: audits/final/stages/test_13of23.md
Findings appended: 0
[END OUTPUT: final_audit_stage]
