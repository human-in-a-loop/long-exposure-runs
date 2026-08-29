# Merge Report — cycle 36 Branch A (clone-0, fork 87da4f517029)

**NOTE ON PATH**: The brief specified
`/home/user/music-gen-instance/fork-87da4f517029/clone-0/merge_report.md`,
but the workspace sandbox refuses writes outside
`/home/user/long-exposure-runs/music-gen`. Per the c31 Branch B, c34
Branch A, and c35 Branch C precedent, this merge report lands at the
workspace-root fallback `merge_report.md`; the merge conductor picks up
whichever path exists.

## Milestone

`M-EAR-1/real-label-training-v0` — new peer sub-milestone under
`M-EAR-1` per c29 state-machine lemma. First real-label ear-model
training pass on the 43-song rated corpus the operator delivered
(10 band-4 + 10 band-5 + 13 band-6 + 10 band-7 across
`corpus/ratings/{4,5,6,7}/*.mp3`; ordinal scale collapses to {4,5,6,7}
for this preview run). Fires the c26 Path B pre-registered plan.

## Verdict

**`EAR_v0_INSUFFICIENT`** — first-class negative deliverable per c26
Path B pre-registration.

All three success bars fail on the 43-song preview corpus:

| Success bar | Threshold | Observed | Result |
|---|---|---|---|
| SB1 (MAE margin over min-baseline) | > 0.5909 | **−0.2093** (MAE 1.1395; baseline_min 0.9302; majority = mean_int = 6) | FAIL |
| SB2 (mean Kendall τ across 10 stratified bootstraps) | ≥ 0.4 | **−0.0987** | FAIL |
| SB3 (artist-leak detection at α=1.0) | ≥ 0.90 | **0.0** (parse yield 43/43) | FAIL |

- Rubric SHA-256: `636c2cd0…1bb2e9` (verified byte-equal in
  `data/ear_v0/verdict.json.rubric_hash` and `data/ear_v0/rubric_hash.txt`)
- Per-fold MAE: 1.3333 / 1.1111 / 1.2222 / 1.1250 / 0.8750 (aggregate
  1.1395; n=9/9/9/8/8)
- Byte-determinism × 2: SHA-256 equal on all six tracked artifacts
  (`feature_cache_manifest.json`, `training_result.json`,
  `corn_head_v0_real.pt`, `held_out_predictions.tsv`,
  `leak_ablation_summary.json`, `verdict.json`); proof in
  `scratchpad/ear_v0_sha_run{1,2}.txt` (diff-clean)
- c6 chassis anchor preservation: `unchanged=True`
- Non-factor genre column: `deferred_aliased_with_band`
  (`alias_confirmed=true`; each rating band = one `playlist_id`)
- Non-factor era column: `deferred_no_metadata`
- Model artifact provenance label: `preview_partial_corpus_v0`
- Scale bounds honestly documented: `{min:4, max:7, absent_bands:[1,2,3]}`

## `preview_partial_corpus_v0` caveat — RETAINED

Binding. The model artifact `data/ear_v0/corn_head_v0_real.pt` is
labeled `preview_partial_corpus_v0` in provenance. This label may only
be dropped when the full 80-song target corpus arrives (bands 1–3
delivered + rebalance across 1–7) and `M-EAR-1/real-label-training-v1`
reruns successfully. c37 is explicitly prohibited from dropping the
caveat via post-hoc bar adjustment or from relaxing the frozen
SB1/SB2/SB3 thresholds (0.5909 / 0.4 / 0.90).

## SB3 statistic-degeneracy finding (new, first-class)

On a corpus where every artist appears exactly once (43/43 songs =
43 singleton artists), the c6 η² leak-test statistic degenerates to
`S_model = S_resid = 1.0`, forcing SB3 detection to identically 0
regardless of true information leakage. This is a rubric-design gap
in c26, not a chassis defect — c26 pre-registered SB3 before the
per-artist distribution was known. Documented in
`data/ear_v0/leak_ablation_summary.json.artist.notes` and handed off
as `_manager/ear-sb3-statistic-degeneracy-on-singleton-artists-clone-0`
for c37 to address BEFORE `real-label-training-v1` runs.

## Required output artifact

`docs/ear_v0_real_label_training_report.md` — present at required
path, placeholders filled with verified numeric values, caveat
retained. This is the canonical deliverable for the milestone.

## Shipped artifacts

Rubric + report:

- `docs/ear_v0_real_label_training_rubric.md` (frozen; SHA
  `636c2cd0…1bb2e9`; committed BEFORE any script under `scripts/ear_v0/`
  landed; mtime + git-log order verified by test)
- `docs/ear_v0_real_label_training_report.md` (required output)

Data (under `data/ear_v0/`):

- `verdict.json`, `rubric_hash.txt`, `training_result.json`,
  `corn_head_v0_real.pt`, `held_out_predictions.tsv`,
  `held_out_folds.json`, `leak_ablation_summary.json`,
  `feature_cache_manifest.json`, `anchor_preservation.json`,
  `cache_idempotence_check.tsv`, `extraction_liveness.tsv`
- `per_song_features/*.npy` (43 files)

Scripts (under `scripts/ear_v0/`; all previously landed, unchanged
this cycle):

- `__init__.py`, `ingest_ratings.py`, `extract_features_v0.py`,
  `train_v0.py`, `evaluate_success_bars.py`, `leak_ablation_v0.py`,
  `run_all.py`, `snapshot_anchor_preservation.py`,
  `build_feature_cache_manifest.py`

Tests:

- `tests/test_ear_v0_real_label_training.py` — 18/18 pass
  (spec called ≥14)
- `tests/test_integration_cross_branch.py §57` extended — invariants
  a–l all green, entire suite 0 failures

Determinism proof:

- `scratchpad/ear_v0_sha_run{1,2}.txt` — SHA-256 tables for two
  independent `run_all.py` invocations; diff-clean

## Ledger events (5 named + 2 housekeeping, all `-clone-0` suffix on
infra families; substantive `M-*` unsuffixed per c32 convention)

Emitted in strict order via `tools/stale/_emit_c36_clone0_close_events.py`:

1. `M-EAR-1/real-label-training-v0` — validated/high (substantive;
   unsuffixed per c32 convention)
2. `_infra/cross-branch-integration-test-cycle36-clone-0` — validated/high
3. **Event c (`_plan/register-real-label-training-v0-milestone`)
   legitimately skipped** — plan row already present in
   `plan_of_record.md` (grep count = 1); brief's escape clause honored.
4. `_run/cycle_36_closed-clone-0` — validated/high
5. `_archive/cycle-36-scratch-clone-0` — validated/high (10 c36 scratch
   tools archived to `tools/stale/`)
6. `_infra/adopt-cycle36-tests-clone-0` — validated/high

All events carry required fields (short-form `assessor` enum, UUID5
content-hash `event_id`, pinned `run_id`, nested `confidence` block,
`ts=2026-08-29T06:45:00Z`).

## promise_check

- **0 ERRORs**.
- WARN count: 204 (pre-existing; unchanged by this branch).

## Executable state (for c37 verification)

```
cat data/ear_v0/verdict.json
sha256sum data/ear_v0/{feature_cache_manifest.json,training_result.json,corn_head_v0_real.pt,held_out_predictions.tsv,leak_ablation_summary.json,verdict.json}
tail -6 promise_ledger.jsonl   # 5 c36 clone-0 events + skip note
```

## Handoff to c37

**Primary M-EAR-1 continuation (as pre-registered by c26 Path B):**

- `M-EAR-1/real-label-training-v1` — full 80-song corpus (bands 1–3
  + rebalance across 1–7) + reweighting exploration (inverse-frequency
  vs inverse-sqrt vs focal-loss on boundary bands) + `yt-dlp`
  era-metadata fetch to un-defer SB3's era column.

**Binding prohibitions on c37:**

- MAY NOT relax SB thresholds (0.5909 / 0.4 / 0.90 frozen).
- MAY NOT drop the `preview_partial_corpus_v0` caveat until full
  80-song corpus lands AND v1 reruns successfully.
- c22 chassis / c23 head-regularization / c25 feature-representation
  anti-patterns REMAIN LOCKED — no redesign attempted or permitted.

**Highest-priority new finding for c37 to address BEFORE v1 runs:**

- `_manager/ear-sb3-statistic-degeneracy-on-singleton-artists-clone-0`
  (durable, opened this milestone). Options: (a) corpus expansion with
  within-artist repeats; (b) fallback statistic — pooled variance with
  explicit small-cell adjustment. This is a rubric-design gap in c26,
  not a chassis defect.

**Durable infra handoffs (persist as-is, still open):**

- `_manager/background-job-supervision-clone-0` — corrective doctrine
  held (`nohup setsid` + heartbeat + worker-side orthogonal-deliverable
  rule when a supervised job is in flight). PID 20291 completed
  cleanly this run. c37 should incorporate: **manual poll
  (`ls | wc -l`) is mandatory first action for any cycle inheriting a
  supervised background job** (auditor correction to c36's null-cycle
  root-cause diagnosis — the nulls were harness-timeout on the
  `until … sleep` wait wrapper, not extractor stall).
- `_manager/hold-pattern-recurrence-clone-0` — durable documentation
  of the two-null-cycle failure mode and its corrective (§0 mandatory
  poll before any pause consideration).
- `_infra/egress-probe-emission-convention` — c35 clone-0 emitter bug
  fix, still open.
- `_infra/promise_check-clone-suffix-false-negative-fix` — still open.
- Rubric-committee-of-one review checklist — c36 Branch C
  rubric-internal contradiction + this milestone's SB3 singleton-artist
  gap now form two data points. Recommended checklist item:
  **"will each SB have measurable dynamic range on the target
  corpus?"** as pre-commit gate.
- `assessor` field enum discipline (minor, new): clone identity does
  NOT go in `assessor`; short-form enum only (`worker`, `auditor`,
  `harness`, `human`, `manager`, `researcher`, `final_auditor`).
  Decorated identity → `assessor_original`.

## Campaign-level M-EAR-1 status after this closure

| Cycle | Milestone | Verdict |
|---|---|---|
| c22 | synthetic-label-stability-audit | INVALIDATED |
| c23 | head-regularization-audit | INVALIDATED |
| c25 | feature-representation-audit | INVALIDATED |
| c26 | _manager/M-EAR-1-path-B-commit | VALIDATED |
| c31 | armed-harness-fixture-reinforcement | VALIDATED |
| **c36** | **real-label-training-v0** | **VALIDATED with EAR_v0_INSUFFICIENT** |

The four-audit + one-real-label evidence base is now complete for
M-EAR-1 at this corpus scale (N ≤ 55 synthetic / N = 43 real). Both
label regimes independently show the c6 CORN chassis cannot beat
trivial baselines. This forecloses the "more compute / more
regularization / different features" family with independent
evidence — a coherent negative finding more valuable than a marginal
PASS would have been.

## Fork closure

All three clones of fork 87da4f517029 now merged:

- clone-0 (this branch): `EAR_v0_INSUFFICIENT` validated
- clone-1: `PARAM_MOVES_AUDIO` validated
  (`M-GEN-1/palette-driven-batch-v3`)
- clone-2: `MIXED` validated
  (`M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization`)

Fork closes cleanly with 3/3 merge reports.

## Deviations from brief (documented)

1. Merge report lands at workspace-root fallback path (see NOTE at
   top). Sandbox blocks writes outside `/home/user/long-exposure-runs/music-gen`.
2. Event c (`_plan/register-real-label-training-v0-milestone`)
   skipped — plan row already present in `plan_of_record.md`; brief's
   plan-row-present escape clause honored. All other events emitted
   in strict order.
