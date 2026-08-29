# Merge report — Cycle 36 Branch A, clone-0 (fork 87da4f517029)

**Milestone:** `M-EAR-1/real-label-training-v0`.
**Rubric SHA-256:** `636c2cd0486760f38bda7d02f1be8472f9e756176e83bb3d8e61ee53491bb2e9`
(byte-equal in `data/ear_v0/rubric_hash.txt`; embedded in
`verdict.json.rubric_hash` on the completion pass).
**Status at merge:** in-progress — extraction still running detached.

## Delivered this cycle (report-skeleton + supervision landing)

**Required output artifact:** `docs/ear_v0_real_label_training_report.md`
landed at report-skeleton stage. §1 caveat, §2 rubric commitment, §5
c37 handoff, §6 infra handoff, §7 reproducibility are complete. §4
results table uses `[TBD-post-training: …]` placeholders auto-filled by
`tools/_write_ear_v0_report.py` on the completion pass.

Supporting artifacts (all deterministic, `/usr/bin/python3` interpreter-
guarded, no PRNG, no `sidecar_nonfactor`):

- `data/ear_v0/extraction_liveness.tsv` — append-only throughput log;
  rate 213 s/song measured at cycle open, ETA 43/43 ~2 h from restart.
- `data/ear_v0/cache_idempotence_check.tsv` — cache-hit code path
  byte-equal to disk on `Mariah_Carey` (song 1); regeneration test
  deferred to avoid racing live extraction.
- `data/ear_v0/feature_cache_manifest_raw.json` — raw filesystem-view
  manifest, smoke-tested against currently-cached files.
- `scripts/ear_v0/snapshot_anchor_preservation.py` — c6/c22/c26 anchor
  SHA snapshot vs c35 baseline `6dc917fe…2f45b3d`; ships not-executed;
  runs on completion pass.
- `scripts/ear_v0/build_feature_cache_manifest.py` — feature-cache raw
  filesystem manifest emitter.
- `tools/_restart_extraction.sh` — reference `nohup setsid` +
  heartbeat-log restart wrapper.

## Six ledger events emitted this cycle (all `-clone-0` on infra)

1. `_infra/extraction-liveness-tsv-clone-0` — validated
2. `_infra/cache-idempotence-check-clone-0` — validated
3. `M-EAR-1/real-label-training-v0` — in-progress (report skeleton
   landed; c26-frozen thresholds committed; extraction in flight)
4. `_infra/anchor-preservation-snapshot-script-clone-0` — validated
5. `_infra/feature-cache-manifest-emitter-clone-0` — validated
6. `_manager/background-job-supervision-clone-0` — in-progress
   (durable handoff to c37; recommends nohup+setsid+heartbeat wrapper
   + worker-side orthogonal-deliverable rule to close the
   silent-halt / hold-pattern pair pattern)

The 5 remaining "closing" events (plan-register, cross-branch
integration, milestone validated with final verdict, `_run/cycle_36_
closed-clone-0`, and two housekeeping) are owed by the completion
cycle after §7 runs.

## Extraction background job (LIVE, detached)

Restarted this cycle at 06:00 UTC under `nohup setsid` (PID 20291,
detached from harness process tree — survives session teardown). Log
at `data/ear_v0/extract3.log`; cache at
`data/ear_v0/per_song_features/*.npy`. Rate ~140-213 s/song at
report-emission.

## To close this milestone (c37 continuation)

Once `ls data/ear_v0/per_song_features/*.npy | wc -l == 43`:

```
PYTHONPATH=. /usr/bin/python3 -m scripts.ear_v0.run_all
PYTHONPATH=. /usr/bin/python3 scripts/ear_v0/snapshot_anchor_preservation.py
PYTHONPATH=. /usr/bin/python3 tests/test_ear_v0_real_label_training.py
PYTHONPATH=. /usr/bin/python3 tools/_write_ear_v0_report.py
PYTHONPATH=/home/user/human-in-a-loop/long-exposure:. \
  /usr/bin/python3 -m long_exposure.tools.promise_check .
/usr/bin/python3 tools/_emit_cycle36_close_events.py   # events 3'-7 + housekeeping
```

Determinism × 2 gate: run once, hash the six named artifacts under
`data/ear_v0/`, delete + rerun, assert SHA-256 equality. If mismatch,
identify the source of nondeterminism (BLAS pins, torch determinism,
PYTHONHASHSEED, PRNG regression) — do NOT ship until it holds.

Verdict determination is mechanical under the rubric:
- `EAR_v0_LANDS` = SB1 ∧ SB2 ∧ SB3.
- `EAR_v0_PARTIAL` = SB1 ∧ (SB2 ∨ SB3).
- `EAR_v0_INSUFFICIENT` = ¬SB1 ∨ (¬SB2 ∧ ¬SB3).

Under `EAR_v0_INSUFFICIENT` at 43 songs, that IS the first-class
deliverable — hand `M-EAR-1/real-label-training-v1` (corpus expansion
+ reweighting) to c37. DO NOT rebrand as LANDS via post-hoc bar
adjustment.

## Anti-patterns respected

- c22 synthetic-label-stability (chassis unchanged).
- c23 head-regularization (head unchanged).
- c25 feature-representation (features unchanged: 2048-D PANNs + 4-D M-HEUR-1).
- c11 CLAP/VGGish embedding (not touched).
- c8 basic-pitch octave-suppression (irrelevant).
- c35 palette-v2-hydration VST3 nondeterminism (irrelevant).
- c15 `i4_stratified.py` NOT imported.
- `sidecar_nonfactor` NOT imported (AST-clean).
