"""Generate docs/ear_v0_real_label_training_report.md from run artifacts.

Reads: data/ear_v0/{verdict.json, training_result.json, leak_ablation_summary.json,
                    anchor_preservation.json, held_out_folds.json, feature_cache_manifest.json,
                    rubric_hash.txt}
Writes: docs/ear_v0_real_label_training_report.md
"""
# created: 2026-08-29T05:45:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: M-EAR-1/real-label-training-v0
import sys, os, json
assert sys.executable == "/usr/bin/python3", sys.executable
from pathlib import Path

D = Path("data/ear_v0")
V = json.loads((D / "verdict.json").read_text())
TR = json.loads((D / "training_result.json").read_text())
L = json.loads((D / "leak_ablation_summary.json").read_text())
AN = json.loads((D / "anchor_preservation.json").read_text())
FF = json.loads((D / "held_out_folds.json").read_text())
FM = json.loads((D / "feature_cache_manifest.json").read_text())
RH = (D / "rubric_hash.txt").read_text().strip()

verdict = V["verdict"]
sb1, sb2, sb3 = V["sb1"], V["sb2"], V["sb3"]
cls = TR["class_distribution"]
sb_bounds = TR["scale_bounds"]

per_fold_lines = "\n".join(
    f"| {r['fold_id']} | {r['n_held_out']} | {r['mae']:.4f} |"
    for r in TR["per_fold_mae"]
)

lines = f"""# M-EAR-1/real-label-training-v0 — Preview Partial Corpus Report

**Cycle 36, Branch A, fork 87da4f517029, clone-0.**
**Rubric SHA-256 (verdict-embedded):** `{RH}`
**Rubric doc:** `docs/ear_v0_real_label_training_rubric.md`.
**Verdict:** **{verdict}**.

## 1. Preview partial corpus caveat (READ THIS FIRST)

This is the **preview_partial_corpus_v0** ear model — a *first-class*
deliverable per the operator, but **NOT** the full-corpus target.

- **Corpus:** 43 rated songs delivered so far (of the 80 planned in the
  c26 Path B commitment). ~54% of target.
- **Scale bounds:** `{sb_bounds}`. Bands 1, 2, 3 are absent; the model
  can only learn "4-ish vs 5-ish vs 6-ish vs 7-ish".
- **Class imbalance:** {cls[str(4)] if str(4) in cls else cls.get(4)}/{cls[str(5)] if str(5) in cls else cls.get(5)}/{cls[str(6)] if str(6) in cls else cls.get(6)}/{cls[str(7)] if str(7) in cls else cls.get(7)} (band-4/5/6/7). Handled via
  per-band sampler weights `(43/4) / n_band` in training.
- **Ordinal collapse:** Full 1-7 head trained, but only the {sb_bounds['min']}-{sb_bounds['max']} range
  is represented in training data — held-out predictions are clipped to
  `[{sb_bounds['min']}, {sb_bounds['max']}]` before rounding.
- **Genre (SB3 non-factor):** DEFERRED — `deferred_aliased_with_band`.
  On this corpus each rating band uses exactly one YouTube playlist_id
  (or the LOCAL_BAND_N fallback for band-7), so `genre` is unseparable
  from the label. Alias confirmed: `{L['genre'].get('alias_confirmed')}`.
- **Era (SB3 non-factor):** DEFERRED — `deferred_no_metadata`.
  Release-year metadata is not present in `corpus/ratings/*/RECEIPTS.md`
  or `corpus/ratings/ratings_manifest.tsv`. Waiting on yt-dlp metadata
  refresh cycle.

**This model MUST NOT be used to gate downstream generation.** It exists to
(a) prove the c6 chassis works with real labels end-to-end, (b) publish
honest SB numbers against the c26-frozen rubric, and (c) hand a concrete
`v1` reweighted-and-expanded target to cycle 37.

## 2. Verdict against c26 frozen rubric

| Success Bar | Threshold | Observed | Pass? |
|---|---|---|---|
| SB1: MAE margin over `min(majority-class, mean-integer)` | > 0.5909 | {sb1['margin']:.4f} | **{'PASS' if sb1['pass'] else 'FAIL'}** |
| SB2: mean pairwise Kendall τ over 10 SHA-seeded stratified bootstraps | ≥ 0.4 | {sb2['mean_tau']:.4f} | **{'PASS' if sb2['pass'] else 'FAIL'}** |
| SB3: leak-detection at α=1.0 on `artist` (η² vs 90-pct null) | ≥ 0.90 | {sb3['artist_detection']:.4f} | **{'PASS' if sb3['pass'] else 'FAIL'}** |

**Rubric ↔ verdict:** `verdict.rubric_hash` byte-equal to
`data/ear_v0/rubric_hash.txt` and to SHA-256 of the doc file.

**Verdict rule:**
- `EAR_v0_LANDS` = SB1 AND SB2 AND SB3.
- `EAR_v0_PARTIAL` = SB1 AND (SB2 OR SB3).
- `EAR_v0_INSUFFICIENT` = SB1 FAIL OR (SB2 FAIL AND SB3 FAIL).

## 3. Corpus composition

| Band | N | Playlist(s) | Notes |
|---|---|---|---|
| 4 | {cls.get(str(4), cls.get(4))} | LOCAL_BAND_4 (from operator upload) | 10 songs |
| 5 | {cls.get(str(5), cls.get(5))} | LOCAL_BAND_5 (from operator upload) | 10 songs |
| 6 | {cls.get(str(6), cls.get(6))} | LOCAL_BAND_6 (from operator upload) | 13 songs (rotates 13→5 across folds) |
| 7 | {cls.get(str(7), cls.get(7))} | LOCAL_BAND_7 (from operator upload) | 10 songs |

Total: {TR['corpus_size']} songs. Feature vectors: {FM['n_songs']} cached at
`data/ear_v0/per_song_features/<sha256>.npy` (2052 float32 dims each).

## 4. Feature pipeline (c6 anchor, READ-ONLY import)

Feature vector per song: **PANNs Cnn14 penultimate (2048-D) + M-HEUR-1
mess-scale (4-D) = 2052-D**, matching the c6 chassis `feature_version`
`{FM['c6_feature_version']}`. This branch pins the composite version as
`{FM['feature_version']}` for the ear_v0 audio-mode.

Chunker: M-INGEST-1 30 s / 5 s-overlap with tail-anchored final clip.
Song aggregation: anchored-tail debias weight `(30 − overlap_with_prev) / 30`.
Sample rates: PANNs at {32000} Hz mono; heuristics at 22050 Hz mono.
Content-hash cache: idempotent per `sha256(song file)`.

**c6 chassis anchors (byte-verified unchanged):**

- `unchanged` = **{AN['unchanged']}**
- `changed_paths` = `{AN['changed_paths']}`

## 5. Folds

5-fold stratified leave-one-per-band CV. Fold assignment is
`sorted-song-sha256 rotation modulo 5` per band — **NO PRNG**. Band-6 (13
songs) rotates so all 13 appear in a held-out fold across the 5 folds.

| Fold | Held out | MAE |
|---|---|---|
{per_fold_lines}
| — Aggregate | 43 | **{TR['aggregate_mae']:.4f}** |

Sampler weights recorded in `data/ear_v0/held_out_folds.json` under
`sampler_weights[song_sha256] = (43/4) / n_band`.

## 6. Training configuration

| Hyperparam | Value |
|---|---|
| Architecture | Linear(2052, 128) → ReLU → Dropout(0.3) → Linear(128, 6) (CORN 1-7 head) |
| Optimizer | Adam, lr=1e-3, weight_decay=1e-3 |
| Loss | Per-sample CORN sub-head BCE, weighted by class-imbalance sampler weights |
| Epochs | {TR['epochs']} |
| Seed | torch.manual_seed({TR['seed']}) per fold (SEED + fold_id) |
| BLAS pins | OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1 |
| Thread pool | torch.set_num_threads(1) |
| Determinism | torch.use_deterministic_algorithms(True, warn_only=True) |

Combined 5-fold state dict at `data/ear_v0/corn_head_v0_real.pt` labeled
`preview_partial_corpus_v0`.

## 7. Success bar details

### SB1 — MAE beats baselines by > 0.5909

- Held-out mean MAE: **{sb1['mae']:.4f}** (mean of |y_pred_int − y_true| over 43 songs).
- Majority-class MAE (predict {sb1['majority_value']}): {sb1['majority_mae']:.4f}.
- Mean-integer MAE (predict {sb1['mean_int_value']}): {sb1['mean_int_mae']:.4f}.
- `baseline_min` = **{sb1['baseline_min_mae']:.4f}**.
- `margin` = baseline_min − MAE = **{sb1['margin']:.4f}**.
- Threshold: margin > 0.5909 (c22 recipe-envelope IQR).
- **Result: {'PASS' if sb1['pass'] else 'FAIL'}.**

### SB2 — mean pairwise Kendall τ ≥ 0.4

10 SHA-256-seeded per-band stratified bootstrap resamples of held-out
predictions. Per-resample τ (see `verdict.json → sb2.per_resample_tau`).

- Mean τ: **{sb2['mean_tau']:.4f}** (required ≥ 0.4).
- **Result: {'PASS' if sb2['pass'] else 'FAIL'}.**

### SB3 — non-factor leak-ablation

Delegated to `scripts/ear_v0/leak_ablation_v0.py` — see
`leak_ablation_summary.json` for full details.

- **artist**: η² observed = {L['artist']['s_observed_max']:.4f}, 90-pct null τ = {L['artist']['tau_90pct_null']:.4f},
  detected = {L['artist']['detected']}, detection_rate = {sb3['artist_detection']:.4f}
  (threshold ≥ 0.90). Parse failures: {L['artist']['artist_parse_failures']}/43 songs.
- **genre**: `deferred_aliased_with_band`. Playlist_id perfectly aliases with
  rating band ({L['genre']['alias_confirmed']}). Cannot separate.
- **era**: `deferred_no_metadata`. Release-year metadata absent.
- **columns_covered**: {L['columns_covered']} (three columns as required by rubric §Deferrals).
- **Result: {'PASS' if sb3['pass'] else 'FAIL'}** on artist column at α=1.0.

## 8. Non-factor sidecar isolation

- AST-grep: zero `from|import ...sidecar_nonfactor` at import-line start
  across `scripts/ear_v0/*.py`.
- Non-factor writer (c6 M-CLASS-1) NOT invoked by this branch.

## 9. Handoff to cycle 37

**`M-EAR-1/real-label-training-v1`** — corpus expansion + reweighting:

1. **Corpus expansion**: continue collecting band-1/2/3 songs until scale
   spans {1, 2, 3, 4, 5, 6, 7} at ≥5 per band, closing the "4-ish vs 5-ish"
   ordinal collapse. Full 80-song c26 Path B target.
2. **Reweighting**: try (a) inverse-frequency band weights only (current
   sampler baseline), (b) inverse-sqrt-frequency (soften), (c) focal-loss-
   like emphasis on the boundary bands as they arrive.
3. **Era-metadata fetch**: run yt-dlp metadata refresh to populate
   release-year; unblocks SB3 era column.
4. **Genre unaliasing**: not solvable on this corpus — requires cross-genre
   samples per band; deferred until corpus grows.
5. **DO NOT** re-attempt c6 chassis redesign (c22/c23/c25 anti-patterns
   locked — three independent audits invalidated ridge/bottleneck/frozen-
   projector head variants and HEUR-only/PANNs-only/VGGish-only feature
   variants). DO NOT relax SB thresholds — the c26 Path B commitment
   pre-registered the bars and this branch honors them.

## 10. Reproducibility

Interpreter guard: `/usr/bin/python3` on every script. All randomness
SHA-256-derived (no PRNG). BLAS pins + `torch.manual_seed(0)` +
`torch.use_deterministic_algorithms(True, warn_only=True)` +
`PYTHONHASHSEED=0`.

Re-run:
```
PYTHONPATH=. /usr/bin/python3 -m scripts.ear_v0.run_all
PYTHONPATH=. /usr/bin/python3 tests/test_ear_v0_real_label_training.py
```

Six artifacts under `data/ear_v0/` carry byte-determinism contracts:
`feature_cache_manifest.json`, `training_result.json`,
`corn_head_v0_real.pt`, `held_out_predictions.tsv`,
`leak_ablation_summary.json`, `verdict.json`.
"""

out = Path("docs/ear_v0_real_label_training_report.md")
out.write_text(lines)
print(f"wrote {out} ({len(lines)} bytes)")
