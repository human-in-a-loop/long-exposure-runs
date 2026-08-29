# M-EAR-1/real-label-training-v0 — Preview Partial Corpus Report

**Cycle 36 Branch A, fork 87da4f517029, clone-0.**
**Rubric SHA-256 (verdict-embedded):** `636c2cd0486760f38bda7d02f1be8472f9e756176e83bb3d8e61ee53491bb2e9`.
**Rubric doc:** `docs/ear_v0_real_label_training_rubric.md`.
**Cycle status at this report revision:** in-flight — feature extraction incomplete (see §3).
**Verdict:** `[TBD-post-training: verdict]`.

> This report is landed at the report-skeleton stage per the c36 auditor's
> anti-null-cycle rule. Placeholders marked `[TBD-post-training: …]` will
> be filled by `tools/_write_ear_v0_report.py` after the pipeline runs to
> completion (feature extraction → folds → CORN training → SB evaluation →
> leak ablation → verdict → determinism × 2 → anchor snapshot). The
> commitment to the c26-frozen thresholds and the `preview_partial_corpus_v0`
> caveat is complete and binding as of this landing.

## 1. Preview partial corpus caveat (READ THIS FIRST)

This is the **preview_partial_corpus_v0** ear model — a *first-class*
deliverable per the operator, but **NOT** the full-corpus target.

- **Corpus:** 43 rated songs delivered so far (of the 80 planned in the
  c26 Path B commitment). ~54% of target.
- **Scale bounds:** `{min: 4, max: 7, absent_bands: [1, 2, 3]}`. Bands 1, 2, 3
  are absent from the delivered corpus; the model can only learn
  "4-ish vs 5-ish vs 6-ish vs 7-ish". The CORN 1-7 head is trained
  intact, but held-out expectations are clipped to `[4, 7]` before
  rounding.
- **Class imbalance:** 10 / 10 / 13 / 10 songs (bands 4 / 5 / 6 / 7).
  Handled via per-band sampler weights `(43 / 4) / n_band` inside the
  training loop.
- **Ordinal collapse:** {4, 5, 6, 7} is the effective ordinal scale for
  this preview.
- **Genre (SB3 non-factor):** DEFERRED — `deferred_aliased_with_band`.
  On this corpus each rating band uses exactly one YouTube playlist_id
  (or the LOCAL_BAND_N fallback for band-7 uploads), so `genre` is
  unseparable from the label. Alias-confirmation printed to
  `data/ear_v0/leak_ablation_summary.json.genre.alias_confirmed`.
- **Era (SB3 non-factor):** DEFERRED — `deferred_no_metadata`.
  Release-year is not present in `corpus/ratings/*/RECEIPTS.md` or
  `corpus/ratings/ratings_manifest.tsv`. Deferred to post-yt-dlp-metadata
  cycle.

**This model MUST NOT be used to gate downstream generation.** It exists
to (a) prove the c6 chassis works with real labels end-to-end, (b)
publish honest SB numbers against the c26-frozen rubric, and (c) hand a
concrete `v1` reweighted-and-expanded target to cycle 37.

## 2. Rubric commitment (frozen, pre-implementation)

Three c26 Path B success bars, verbatim thresholds:

| SB | Bar | Threshold | Anchor |
|---|---|---|---|
| SB1 | Held-out MAE beats `min(majority-class, mean-integer)` | margin > **0.5909** | c22 recipe-envelope IQR |
| SB2 | Mean pairwise Kendall τ across 10 stratified bootstrap resamples | ≥ **0.4** | c23 threshold |
| SB3 | Non-factor leak-detection at α=1.0 on `artist` | ≥ **0.90** | c6 protocol |

**Verdict logic (frozen):**

- `EAR_v0_LANDS` = SB1 AND SB2 AND SB3.
- `EAR_v0_PARTIAL` = SB1 AND (SB2 OR SB3).
- `EAR_v0_INSUFFICIENT` = SB1 FAIL OR (SB2 FAIL AND SB3 FAIL).

The rubric SHA-256 `636c2cd0…1bb2e9` is stored at
`data/ear_v0/rubric_hash.txt` and will be embedded byte-equal in
`verdict.json.rubric_hash`. Git-mtime + git-log fallback tests
(`test_03_rubric_mtime_before_scripts`) enforce that no script under
`scripts/ear_v0/` predates the rubric doc. **These gates are green from
cycle 2 and are not re-verified this cycle** (auditor exclusion).

## 3. Extraction status

Feature extraction is a long-running CPU-bound job (PANNs Cnn14 forward
pass × N clips per song). Two prior sessions terminated it silently
(monitor + background-task teardown on session end). This session
restarted the extractor detached (`nohup setsid`) with a heartbeat log.

- **Liveness log:** `data/ear_v0/extraction_liveness.tsv` (append-only,
  one row per cycle: `ts, files_seen, sec_per_song, eta_to_43_iso,
  newest_mtime_iso, note`).
- **Rate at report-skeleton emission:** see the latest liveness row.
  Empirical rate ≈ 213 s / song (~3.5 min); ETA to 43/43 ≈ ~2 h from
  restart under this rate.
- **Cache idempotence:** `data/ear_v0/cache_idempotence_check.tsv`
  confirms the cache-hit path returns byte-identical bytes to disk on
  a re-invocation of `extract_song()`. Regeneration-determinism test
  (delete + re-run) is deferred to the completion pass to avoid racing
  the live background job.
- **Extractor stdout:** `data/ear_v0/extract3.log` (this restart).
  Prior partial logs preserved at `extract.log`, `extract2.log`.

## 4. Results (skeleton — placeholders filled by completion pass)

### Success bars

| SB | Threshold | Observed | Pass? |
|---|---|---|---|
| SB1: MAE margin over `min(majority-class, mean-integer)` | > 0.5909 | `[TBD-post-training: sb1_margin]` (MAE=`[TBD-post-training: mae_aggregate]`; baseline_min=`[TBD-post-training: baseline_min]`) | `[TBD-post-training: sb1_pass]` |
| SB2: mean pairwise Kendall τ over 10 stratified bootstraps | ≥ 0.4 | `[TBD-post-training: mean_tau]` | `[TBD-post-training: sb2_pass]` |
| SB3: leak-detection at α=1.0 on `artist` | ≥ 0.90 | `[TBD-post-training: artist_detection_rate]` | `[TBD-post-training: sb3_pass]` |

### Baselines (SB1 inputs)

- Majority-class MAE (predict modal band): `[TBD-post-training: baseline_majority_class_MAE]`.
- Mean-integer MAE (predict rounded population mean): `[TBD-post-training: baseline_mean_integer_MAE]`.

### Per-fold MAE (5-fold stratified leave-one-per-band CV)

| Fold | Held out | MAE |
|---|---|---|
| 0 | `[TBD-post-training: fold_0_n]` | `[TBD-post-training: MAE_fold_1]` |
| 1 | `[TBD-post-training: fold_1_n]` | `[TBD-post-training: MAE_fold_2]` |
| 2 | `[TBD-post-training: fold_2_n]` | `[TBD-post-training: MAE_fold_3]` |
| 3 | `[TBD-post-training: fold_3_n]` | `[TBD-post-training: MAE_fold_4]` |
| 4 | `[TBD-post-training: fold_4_n]` | `[TBD-post-training: MAE_fold_5]` |
| — Aggregate | 43 | `[TBD-post-training: mae_aggregate]` |

### Non-factor leak-ablation (per-column)

- **artist**: `[TBD-post-training: artist_detection_rate]` at α=1.0
  (threshold ≥ 0.90). Parse yield: `[TBD-post-training: artist_parse_yield]` / 43.
- **genre**: `[TBD-post-training: genre_detection_rate=deferred_aliased_with_band]` — playlist_id
  perfectly aliases with rating band on this corpus; genre unseparable
  from signal by construction.
- **era**: `[TBD-post-training: era_detection_rate=deferred_no_metadata]` — release-year absent
  from RECEIPTS/manifest; deferred to post-yt-dlp-metadata cycle.

### Anchor preservation

- `data/ear_v0/anchor_preservation.json.combined_manifest_sha` vs c35
  baseline `6dc917fe…2f45b3d`: `[TBD-post-training: anchor_unchanged]`.

## 5. Handoff to cycle 37

Two-path conditional:

### If EAR_v0_LANDS

- Do **NOT** drop the `preview_partial_corpus_v0` caveat this cycle
  even under LANDS — the caveat may be dropped only when the full
  80-song corpus arrives and v1 reruns successfully.
- `M-EAR-1/real-label-training-v1` seed for c37: corpus expansion to
  the full 80-song target as new uploads land (bands 1–3 + rebalance).

### If EAR_v0_PARTIAL or EAR_v0_INSUFFICIENT

Hand `M-EAR-1/real-label-training-v1` to c37 with the following
non-negotiable constraints:

1. **Corpus expansion**: continue collecting band-1/2/3 songs until
   scale spans {1, 2, 3, 4, 5, 6, 7} at ≥ 5 per band, closing the
   "4-ish vs 5-ish" ordinal collapse. Full 80-song c26 Path B target.
2. **Reweighting**: try (a) inverse-frequency band weights only
   (current sampler baseline), (b) inverse-sqrt-frequency (soften),
   (c) focal-loss-like emphasis on the boundary bands.
3. **Era-metadata fetch**: run yt-dlp metadata refresh to populate
   release-year; unblocks SB3 era column.
4. **Genre unaliasing**: not solvable on this corpus — requires
   cross-genre samples per band; deferred until corpus grows.
5. **DO NOT** re-attempt c6 chassis redesign (c22 / c23 / c25
   anti-patterns locked — three independent audits invalidated
   ridge/bottleneck/frozen-projector head variants and
   HEUR-only/PANNs-only/VGGish-only feature variants).
6. **DO NOT** relax SB thresholds. The c26 Path B commitment
   pre-registered `0.5909 / 0.4 / 0.90` and this branch honors them.
   `EAR_v0_INSUFFICIENT` at 43 songs is a first-class deliverable, not
   a signal to adjust bars.

Handoff must name which SB failed and by how much (auto-filled).

## 6. Infrastructure handoff — background-job supervision

**Second silent-halt observed** this campaign: c31 fixture and the c36
extraction both died without a completion record when the parent Claude
session ended. Emitted `_manager/background-job-supervision-clone-0`
this cycle (in_progress, durable handoff to c37) recommending:

- **(a)** A `nohup setsid` + heartbeat wrapper documented as a sibling
  to `docs/fanout_launched_event_convention.md`. Every long-running
  background job (feature extraction, training, batched renders) must
  be launched detached from the harness's process tree so a session
  teardown does not reap it; and must emit a heartbeat line (e.g. one
  per song, one per fold, one per second) to a dedicated log so a
  supervisor can distinguish stall from progress.
- **(b)** A worker-side rule: any cycle spawned while a supervised
  background job is live MUST produce at least one named on-disk
  deliverable orthogonal to that job's output before it may sleep or
  exit. This closes the "hold-pattern null cycle" the c36 audit
  flagged. The report-skeleton, liveness TSV, idempotence TSV, and
  anchor-snapshot script this cycle satisfy the rule.

## 7. Reproducibility

- Interpreter guard: `/usr/bin/python3` on every script under
  `scripts/ear_v0/`.
- All randomness SHA-256-derived (no `random`, no `numpy.random`);
  AST-grep verified from cycle 2.
- BLAS pins on training: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
  `OPENBLAS_NUM_THREADS=1`; `torch.set_num_threads(1)`;
  `torch.manual_seed(0)` + fold_id per fold;
  `torch.use_deterministic_algorithms(True, warn_only=True)`;
  `PYTHONHASHSEED=0`.
- Re-run (from empty cache):
  ```
  PYTHONPATH=. /usr/bin/python3 -m scripts.ear_v0.extract_features_v0
  PYTHONPATH=. /usr/bin/python3 -m scripts.ear_v0.run_all
  PYTHONPATH=. /usr/bin/python3 tests/test_ear_v0_real_label_training.py
  ```
- Six artifacts under `data/ear_v0/` carry byte-determinism × 2
  contracts once the completion pass runs:
  `feature_cache_manifest.json`, `training_result.json`,
  `corn_head_v0_real.pt`, `held_out_predictions.tsv`,
  `leak_ablation_summary.json`, `verdict.json`.
