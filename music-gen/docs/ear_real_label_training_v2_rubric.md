---
created: 2026-08-29T12:00:00Z
cycle: 39
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-EAR-1/real-label-training-v2
---

# Rubric — M-EAR-1/real-label-training-v2 (c39 clone-1)

Frozen BEFORE any script under `scripts/ear_v2/` lands (mtime + git-log
dual gate; test 01/02 in `tests/test_ear_real_label_training_v2.py`).
Rubric SHA-256 pinned to `data/ear_v2/rubric_hash.txt` and embedded
verbatim in `data/ear_v2/verdict.json.rubric_hash`.

Direct response to c38 clone-0 `EAR_v1_PARTIAL` (all three c26-frozen
success bars failed on the 43-song singleton-artist corpus). This v2
intervention is a corpus-side resample only — **orthogonal** to the
c22 chassis-audit, c23 head-regularization, and c25 feature-swap
anti-pattern axes (all three remain locked).

## Chassis (READ-ONLY imports, unchanged)

- Features: c6 PANNs Cnn14 penultimate 2048-D + c6 M-HEUR-1 mess-scale 4-D → 2052-D per clip.
- Head: c6 `CornHead(2052→128→ReLU→Dropout(0.3)→6)`; CORN 1-7 ordinal (K=7, sub-heads for `y>1..y>6`).
- Determinism envelope: `OMP/MKL/OPENBLAS_NUM_THREADS=1`, `torch.manual_seed(0)`, `torch.set_num_threads(1)`, `torch.use_deterministic_algorithms(True, warn_only=True)`.
- Anchor-preservation manifest: 25+ SHAs byte-identical pre/post (c6 chassis, c22 stability harness, c26 Path B doc, c38 clone-0 v1 tree, c1 chunker, c6 feature cache).

## Resample protocol (anchored-tail per-song)

1. Discover 43 songs via `scripts.ear_v0.ingest_ratings.discover_songs` (band ∈ {4,5,6,7}, sorted by `(band, sha256)`).
2. Duration = `librosa.get_duration(path=...)`. Skip any song with `duration < 30 s` with an honest skip reason (`data/ear_v2/resample_manifest.json.skipped`).
3. For each surviving song of duration `D` seconds:
   - Generate clip starts at `{0, 25, 50, 75, ...}` while `start + 30 ≤ D`.
   - Append a tail-anchored final clip with `start = D − 30`, `end = D` (may overlap prior clip by > 5 s per the c1 chunker anchored-tail rule; this is the intended anti-truncation guarantee).
   - Cap at 6 clips per song: durations > 155 s truncate to the first 5 hop-strided starts + tail-anchored final.
   - Discretization: `D ∈ [30, 55): 2 clips; [55, 80): 3; [80, 105): 4; [105, 130): 5; ≥ 130: 6 (capped)`.
4. Every clip inherits its parent song's `(band, artist, playlist_id, song_sha256)` tuple.
5. Total effective sample count expected in `[172, 258]` on the 43-song corpus.

## Feature extraction (per clip)

- Load MP3 twice deterministically: mono @ PANNs sr (32000 Hz) for PANNs Cnn14, mono @ 22050 Hz for the 4-D heuristic vector.
- Slice each MP3 by the resample-manifest clip bounds converted to sample offsets per sr.
- Emit 2052-D float32 per clip. Cache under `data/ear_v2/features_v2/<song_sha256>__<clip_idx>.npy`.
- Cache key = `(song_sha256, clip_idx)`; second run is skip-if-hash-matches.
- Anchored-tail per-song aggregation is NOT applied here — each clip is an independent training sample.

## CV fold construction (per-song grouping, no clip leakage)

- 5-fold stratified `GroupKFold(groups=song_id, stratify=band)`.
- Deterministic assignment: sort songs by `(band, sha256)` then round-robin per band to fold indices `0..4`. All clips of a song go entirely into either the training or the held-out half (assertion in test 07).
- Per-song per-band class re-balancing weights per c38 v1 protocol: `w = (n_total / len(BANDS)) / class_count[band]`, broadcast to clip level.

## Training (c6 chassis verbatim)

- `Adam(lr=1e-3, weight_decay=1e-3)`, 200 epochs, batch = full CV split.
- CORN loss (BCE-with-logits over 6 binary sub-heads), weighted mean over samples.
- Per-fold held-out prediction: integer band prediction = `1 + sum(sigmoid(logits) > 0.5)`, then clipped to `[min(BANDS), max(BANDS)] = [4,7]` and rounded.
- Per-clip held-out predictions concatenated across 5 folds → `data/ear_v2/held_out_predictions.tsv` (5-col schema plus `clip_id`, `song_sha256`, `band_true`, `band_pred_int`, `band_pred_expectation`, `fold_id`, `artist`, `playlist_id`).

## Success bars (c26-frozen thresholds; unchanged)

- **SB1** — clip-level MAE margin over `min(majority_class_mae, mean_integer_mae) > 0.5909` (c22 recipe-envelope IQR). Reported both at the clip level AND at song-median-aggregated level for cross-comparison with v1.
- **SB2** — mean pairwise Kendall τ across 10 stratified-bootstrap resamples of the clip-level (band_true, band_pred_int) vector `≥ 0.4`. Resamples are per-band SHA-256-derived indices (no PRNG).
- **SB3** — F1 pooled-variance leak-detection statistic on artist (LIVE) at α=1.0. Statistic version `F1_pooled_variance_v1` per c38 clone-0 lift; `detection_rate ≥ 0.90` AND `fpr ≤ 0.10`; τ = 90th percentile of 25 SHA-permutation null distributions; detection rate over 20 SHA-subsample repeats.
- **SB3 denominator condition** (new geometric requirement): the F1 denominator (count of within-artist paired clips) MUST be strictly `> 43` for the statistic to be geometrically valid. Reported in `data/ear_v2/leak_test_v2_summary.json.leak_types.artist.denominator_pairs`; asserted by test 08.
- Genre = `deferred_aliased_with_band` (playlist_id perfectly aliases with band on this corpus, per c26 Path B).
- Era = `deferred_no_metadata` (c26).

## Three-verdict rubric (frozen)

- **`EAR_v2_LANDS`** — SB1 margin `> 0.5909` AND SB2 mean τ `≥ 0.4` AND SB3 artist detection `≥ 0.90` at α=1.0 AND SB3 FPR `≤ 0.10`. First real-label crossing of the c26 pre-registered thresholds; the c26 chassis is finally credible on real data.

- **`EAR_v2_PARTIAL`** — at least one of SB1/SB2/SB3 falls short AND at least one improves materially over v1. Improvement criteria (any of): SB1 margin `> −0.2093` (v1 baseline); SB2 mean τ `> −0.0987` (v1 baseline); SB3 F1 denominator `> 43` with a finite non-pinned value. Named per-SB attribution required in `verdict.json.named_sb_attribution` (each entry names the SB, observed, threshold, shortfall). Positive first-class finding: corpus-side resample intervention moves the needle even if the c26 thresholds aren't fully crossed.

- **`EAR_v2_INSUFFICIENT`** — no SB improves over v1 within noise. Corpus-geometry alone is not the bottleneck. Handoff seeds:
  - operator-corpus-expansion urgency (deliver remaining 37 rated songs to reach the 80-song target) as the c40 primary,
  - formal deprecation of the c26 chassis for the 43-song regime,
  - re-opening of head-architecture-v3 under the Fixed Decisions escape hatch is discussable (three failure modes in the real-label regime beats the c22/c23/c25 chassis-audit exhaustion signal).

## Anti-pattern discipline (all six anti-patterns remain locked; three directly in scope)

- **c22** `M-EAR-1/synthetic-label-stability-audit` — NOT re-fired.
- **c23** `M-EAR-1/head-regularization-audit` — NOT touched; test 17 asserts no import of `scripts.ear.model_v2_ridge`, `model_v2_bottleneck`, or `model_v2_frozen_projector`.
- **c25** `M-EAR-1/feature-representation-audit` — NOT touched; test 18 asserts no import of `scripts.ear.feature_subset_adapter` or `scripts.ear.stability_audit_v3_representations`.
- No PRNG (test 19 AST-asserts no `random`, no `np.random`, no `torch.manual_seed(<non-zero>)`; only campaign-pinned `torch.manual_seed(0)`).
- No `sidecar_nonfactor` imports (test 20).
- Interpreter guard `#!/usr/bin/python3` on every script (test 21).

## Byte-determinism × 2

- Run `python3 -m scripts.ear_v2.run_all` twice in fresh working dirs (or with `data/ear_v2/features_v2/` cleared for the SB/train stage; the features-cache stage is content-addressed so it is skip-if-hash-matches on the second run).
- Assert SHA-256 equality on: `training_result.json`, `corn_head_v2.pt`, `sb_v2_verdict.json`.
- Reported in `data/ear_v2/determinism_check.json`; asserted by test 10.

## Ledger event contract

- 6 substantive `M-EAR-1/real-label-training-v2/*` events (auto-suffixed `-clone-1` by the c33 harness-clone-namespace-guard) + 4 housekeeping under `-clone-1` per the c32 fanout-namespace convention.
- `narrative` field required. `run_id = "run-2026-08-28T040704Z"`. Nested `confidence: {level, rationale, assessor: 'worker'}`. `workspace` as `pathlib.Path`. State machine: `validated → in_progress` forbidden.

## Deliverable checklist

- `docs/ear_real_label_training_v2_rubric.md` (this file) committed BEFORE any `scripts/ear_v2/` file — test 01 (mtime) + test 02 (git-log; `MERGE_DEFERRED` acceptable per c38 precedent, documented in verdict.json).
- `data/ear_v2/rubric_hash.txt` = `sha256(docs/ear_real_label_training_v2_rubric.md)` — test 03.
- `data/ear_v2/verdict.json.rubric_hash` byte-equal to `rubric_hash.txt` — test 04.
- `data/ear_v2/resample_manifest.json` per-song clip counts in `[1, 6]`; total `∈ [172, 258]` — test 05.
- Every clip's `(start, end, song_id, band, artist)` reproducible from `ratings_manifest.tsv` + this protocol — test 06.
- GroupKFold per-song-grouping — test 07.
- SB3 F1 denominator `> 43` — test 08.
- SB1/SB2/SB3 finite — test 09.
- Byte-determinism × 2 — test 10.
- Anchor preservation (25+) — tests 11-16.
- AST anti-pattern discipline — tests 17-20.
- Interpreter guard — test 21.
- Ledger event schema/count — test 22.
- `docs/ear_real_label_training_v2_report.md` — 12 sections per brief.
