# M-EAR-1/real-label-training-v1 — Cycle 38 (Fork 33a2a8003c84, Clone-0)

**Verdict: `EAR_v1_PARTIAL`** (all three success bars fall short; SB3 shortfall is the c37-predicted F1-singleton-corpus degeneracy).

**Rubric SHA-256 (byte-equal to `data/ear_v1/rubric_hash.txt` and `data/ear_v1/verdict.json.rubric_hash`):**
`10131bf35543d88e9ef0ce7f1f180b9bfa657c0848291493dc9eb65498baa37f`

---

## 1. Corpus honesty caveat (prominent)

**The rated corpus on disk is 43 of the 80-song target — 54% corpus coverage.** The v1 verdict is credible for the corpus that exists on disk; it is **NOT** calibrated to the full 80-song target. Audio egress remains blocked, so the missing 37 songs cannot be downloaded this cycle. `workspace/harvest_playlists.sh` should continue to be retried at cycle-top (non-blocking probe per Fixed Decisions). Model artifact `data/ear_v1/corn_head_v1.pt` is labeled `preview_partial_corpus_v1`.

Band distribution (43 songs): band-4 × 10, band-5 × 10, band-6 × 13, band-7 × 10.

## 2. F1-statistic surgery on `scripts/ear/leak_test.py`

Under c38 anchor-preservation authorization, the c6 `S = max(S_model, S_resid)` combined-statistic line was retired and replaced with the c37 clone-1 F1 pooled-variance implementation (`f1_pooled_variance_statistic`, lifted verbatim from `scripts/ear_sb3_fallback/candidate_f1_pooled_variance.py`).

Diff manifest (`data/ear_v1/leak_test_diff_manifest.json`):

- `old_sha256` = `6de3b28d6c046b0a7e55673450e0ca03fc8b91021addd22131229cfbbf0a1ec0` (c6 anchor SHA, fixture-verified).
- `new_sha256` = `f30e0f49ac6b5158e6a5430383e64ec0fbe72ce537b2e94f7cb133c7a0c3506e`.
- `statistic_version` = `"F1_pooled_variance_v1"` (module constant + every emitted row).
- Changed line ranges: 12 contiguous ranges (see manifest).

AST/regex verified: `max(S_model, S_resid)` absent from function bodies (only present in comment strings documenting what was retired). `f1_pooled_variance_statistic` defined and used at call sites.

## 3. Per-fold CV results

5-fold stratified leave-one-per-band on the 43-song corpus, ordinal predictions clip to `{4, 5, 6, 7}`. Aggregate MAE = **1.140**.

| Fold | N held-out | MAE   |
|------|-----------:|------:|
| 0    | 9          | 1.333 |
| 1    | 9          | 1.111 |
| 2    | 9          | 1.222 |
| 3    | 8          | 1.125 |
| 4    | 8          | 0.875 |

Baselines (both degenerate on this class distribution, band-6 is majority):

- Majority-class MAE = 0.930 (predict 6 for every song).
- Mean-integer MAE  = 0.930 (predict 6 for every song).

Trained CORN 1-7 head (2052-D → 128 → 6, dropout=0.3, Adam lr=1e-3, 200 epochs, `torch.manual_seed(0)`) is **worse** than both trivial baselines.

## 4. Success-bar outcomes (SB1 / SB2 / SB3)

Thresholds pinned per c26 Path B commitment (`docs/ear_path_b_commitment.md`); NOT refit.

### SB1 — MAE margin (threshold: margin > 0.5909)

- **Observed margin** = -0.209  (model MAE 1.140 − min(baselines) 0.930)
- **Shortfall** = 0.800
- **PASS**: NO

Model does not beat the trivial predict-majority baseline on this 43-song corpus.

### SB2 — Mean pairwise Kendall τ (threshold: τ ≥ 0.4)

- **Observed** = -0.099 across 10 stratified bootstrap resamples.
- Per-resample τ: {-0.053, -0.139, -0.025, +0.002, -0.294, -0.073, -0.087, -0.108, -0.054, -0.156}.
- **Shortfall** = 0.499
- **PASS**: NO

Rank agreement across bootstrap resamples is not merely low — it is slightly negative, consistent with a chassis that is not extracting a stable ordinal signal from these 43 real-label song embeddings.

### SB3 — F1 pooled-variance leak detection (threshold: detection ≥ 0.90, FPR ≤ 0.10)

Per leak type:

| Leak type | Status                       | Detection | FPR   | Pass  |
|-----------|------------------------------|----------:|------:|-------|
| artist    | live                         |     1.000 | 1.000 | NO (FPR) |
| genre     | deferred_aliased_with_band   |         — |     — | —     |
| era       | deferred_no_metadata         |         — |     — | —     |

**c37 prediction confirmed.** On a singleton-artist corpus (43 distinct artists → 43 groups of size 1), the F1 pooled-variance statistic collapses to the constant **2/3** by construction. `null_std = 1.1e-16` (float epsilon) — the observed statistic and the null distribution both pin at 0.6666…, so every "leak-planted" repeat and every "no-leak" control produces the same F1 above the 90th-percentile threshold, driving both detection and FPR to 1.0. This is exactly the singleton-corpus pathology c37 clone-1 foreshadowed.

**Genre** is `deferred_aliased_with_band` because `playlist_id` perfectly aliases with the rating band on this corpus (band-4 songs all have `LOCAL_BAND_4` or the band-4 YouTube playlist_id, etc.) — genre cannot be separated from the signal by construction. **Era** is `deferred_no_metadata` because release-year metadata is not present in `corpus/ratings/*/RECEIPTS.md` or `ratings_manifest.tsv`. Both deferrals are recorded verbatim as fields in `data/ear_v1/leak_test_summary.json`, not as comments.

## 5. Anchor preservation

14 read-only anchors, all byte-identical pre/post (`data/ear_v1/anchor_preservation.json.all_unchanged = true`):

| Anchor path                            | SHA-256 (pre = post)                                           |
|----------------------------------------|----------------------------------------------------------------|
| scripts/ear/features.py                | 5e7cbf33cd81b501368f6334b2e5c67c41172c4d9e60bb34154274897c611f53 |
| scripts/ear/model.py                   | d4322a95fc2328b201b4040713dfdf8e294d8d0ae31db7e81c6390371492b552 |
| scripts/ear/corn.py                    | 5028c58c20f23cd62c94789fad3522f94953417b79dec33b8506704b83a9921b |
| scripts/ear/train.py                   | 94facf5497123f075c2298974df6378f545467cf5f2a8f32020e86345befed99 |
| scripts/ear/stability_audit.py         | b1ce5137b665a962657f1ee128db4d36abcb6d2174f57101b354a3194ea02e4c |
| scripts/ear/stability_metrics.py       | 6a5cb5183fdc77e80677ef01bb47f777a2662404f737f8aa74287f30cf97dc27 |
| scripts/ear/synthetic_labels.py        | b71f194ef97e8936bb8942d5fccba899e6efe47e292cca185728d1cd9f41fb4d |
| scripts/classifier/tagger.py           | d02fb36fb469e376f61957837f8010c7fcd1df5e8fd6a1cc1ab8a5fd393ae2ea |
| docs/ear_path_b_commitment.md          | 2c81d80a693371ca2ee06dc7f7125e121be4b310f0b6cc9d2b29513f2839ec55 |
| scripts/ear_v0/ingest_ratings.py       | 4f0f6afc13664ddf528b11eeaf1e361b91e12fb5a80cfa02efe768a0690172fb |
| scripts/ear_v0/extract_features_v0.py  | 7d967367b6fdd2aa44ed74cd48c5cddf52da0d738d614bcba601e5afacdedf77 |
| scripts/ear_v0/train_v0.py             | ed636392066b6b159cb81d0e30f71867a39bd029a2943e136eb8d9b9dd69ac63 |
| scripts/ear_v0/evaluate_success_bars.py| 8b9e17b5d7d8a6915a7a70df7c307e8929226e3920349885c072eec92dd0d714 |
| scripts/ear_v0/leak_ablation_v0.py     | 5fb0b8802af2949ae9d1cabb39bbc49d782fd4a9a260786aa63cf0e18f8b9e5d |

The single authorized mutation (`scripts/ear/leak_test.py`) is tracked separately in `data/ear_v1/leak_test_diff_manifest.json`.

## 6. Byte-determinism × 2

`data/ear_v1/determinism_check.json.all_equal = true`. Two fresh-temp-dir runs under `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756800000`, `TZ=UTC`, `LC_ALL=C.UTF-8`, `torch.manual_seed(0)`, single-thread BLAS pins:

| Artifact                    | run-1 SHA-256                                                  | run-2 SHA-256                                                  | Equal |
|-----------------------------|----------------------------------------------------------------|----------------------------------------------------------------|:-----:|
| verdict.json                | 1933edacd8ce792aef30d6208f75f87753e083bc39954e270e659f9f2d98a84d | 1933edacd8ce792aef30d6208f75f87753e083bc39954e270e659f9f2d98a84d | ✓ |
| leak_test_summary.json      | 1552a1b981679da96828d43647229404d06a0d866480c4a19afee101e9e4ce11 | 1552a1b981679da96828d43647229404d06a0d866480c4a19afee101e9e4ce11 | ✓ |
| corn_head_v1.pt             | 2befa5884062d45f0fae9683476347a4f74ab266b0f49ac0b3dda369d0646cb7 | 2befa5884062d45f0fae9683476347a4f74ab266b0f49ac0b3dda369d0646cb7 | ✓ |

## 7. Corpus honesty caveat (restated)

**43 of the 80-song target — 54% corpus coverage.** The `EAR_v1_PARTIAL` verdict is honest for the 43 real-label songs currently on disk. The chassis + the F1 leak-test statistic are correctly wired and byte-deterministic; the shortfall is in the audible signal being extracted from the 43-song corpus, in the ordinal-agreement across bootstrap resamples, and in the singleton-artist structure of a 43-artist corpus (which degenerates the F1 pooled-variance statistic). A rerun on the full 80-song corpus once egress unblocks is the natural next step.

## 8. c39 handoff seeds

Under the c37 clone-0 audit's decision tree, `EAR_v1_PARTIAL` fires **all three** shortfall paths (SB1-short, SB2-short, SB3-short):

1. **SB1-short → corpus-expansion probe.** With band-6 as the majority class (13 / 43 = 30.2%), the majority-baseline MAE floor is 0.930; the required c22-IQR margin of 0.5909 demands model MAE ≤ 0.339. A 43-song corpus with degenerate stratification (all four classes 8-13 songs) is too small a lever. Handoff: retry `workspace/harvest_playlists.sh` at every cycle-top; when two consecutive `media_ok=true` egress-status rows land, refire M-EAR-1/real-label-training-v2 on the expanded corpus.
2. **SB2-short → resample-count probe.** τ = -0.099 with n_resamples=10 is close enough to zero that resample noise is a plausible contributor. Handoff: reevaluate SB2 with n_resamples ∈ {50, 100} on the same 43-song corpus and report τ-vs-n curve; if τ recovers into [0.2, 0.4] at n=100, treat as SB2-resample-sensitive rather than SB2-fundamental.
3. **SB3-short → alternative singleton-corpus statistic.** The F1 pooled-variance statistic collapses on 43-distinct-artist corpora. Handoff: investigate a variance-preserving alternative (e.g. bootstrap the artist-column with duplicated songs to induce group structure, or replace F1 with a rank-based statistic that survives the singleton case). Do NOT rework the c6 anchor a second time this campaign year — the c37/c38 F1 lift is a locked anchor from this point forward.

**Regardless of the three probes above:** retry `workspace/harvest_playlists.sh` at cycle-top (non-blocking per Fixed Decisions). None of the paths above touch cycle-9 DawDreamer, the closed collision-modeling arc, or the c22/c23/c25/c26/c27 anti-patterns.

---

**43 of the 80-song target — 54% corpus coverage.**
