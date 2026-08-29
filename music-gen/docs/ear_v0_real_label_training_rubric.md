---
created: 2026-08-29T07:20:00Z
cycle: 36
run_id: run-2026-08-28T040704Z
agent: worker (clone-0, fork 87da4f517029)
milestone: M-EAR-1/real-label-training-v0
---

# EAR v0 — Real-Label Training Rubric (frozen, cycle 36 Branch A)

## Purpose

This rubric is committed BEFORE any script under `scripts/ear_v0/` is
written to disk. It locks the verdict criteria for the first real-label
training pass of the M-EAR-1 CORN 1–7 head against the operator's rated
corpus (43 songs, 10 band-4 + 10 band-5 + 13 band-6 + 10 band-7).

Rubric SHA-256 is recorded in `data/ear_v0/rubric_hash.txt` and embedded
verbatim in `data/ear_v0/verdict.json.rubric_hash`. Both the rubric doc
mtime and its git-log first commit MUST precede any `scripts/ear_v0/*.py`
file's mtime / first commit (`tests/test_ear_v0_real_label_training.py`
enforces this).

## Three success bars (unchanged from cycle-26 Path B commitment)

- **SB1 — MAE margin**: held-out mean absolute error must beat
  `min(majority-class MAE, mean-integer MAE)` by a margin **strictly
  greater than 0.5909** (the cycle-22 recipe-envelope IQR).
- **SB2 — Ordinal stability**: mean pairwise Kendall τ ≥ **0.4** across
  10 SHA-256-seeded stratified bootstrap resamples of the held-out
  predictions (per c23 threshold).
- **SB3 — Non-factor leak resistance**: leak-test detection rate ≥
  **0.90** at α = 1.0 on the `artist` column (parsed from
  `corpus/ratings/*/RECEIPTS.md` title strings) per the c6 leak-test
  protocol. `genre` and `era` are documented structural deferrals for
  this corpus (see §Deferrals below) and do not affect the rubric.

## Three-verdict rubric

- **EAR_v0_LANDS** — all three of {SB1, SB2, SB3} pass.
- **EAR_v0_PARTIAL** — SB1 passes AND at least one of {SB2, SB3} passes.
- **EAR_v0_INSUFFICIENT** — SB1 fails, OR SB1 passes but both SB2 and
  SB3 fail.

The rubric is symmetric in {SB2, SB3} above SB1: SB1 acts as a gate.
Failing SB1 is a first-class negative finding at this corpus size (43
songs, ~1.45× the 55-clip synthetic valset that Path A was audited on).
Do NOT rebrand INSUFFICIENT as LANDS via post-hoc bar adjustment; the
c22/c23/c25 anti-pattern lock is binding on chassis redesign.

## Scale honesty

The corpus covers rating bands {4, 5, 6, 7}. Bands {1, 2, 3} are absent.
The model can learn a "4-ish vs 5-ish vs 6-ish vs 7-ish" distinction
only. `verdict.json.scale_bounds` records `{min: 4, max: 7,
absent_bands: [1, 2, 3]}`. The provenance label carried on the model
artifact is `preview_partial_corpus_v0` — this is a first-class
deliverable per operator intent, NOT calibrated to the full 80-song
target.

## Deferrals (SB3 §)

- **genre**: structural deferral. `playlist_id` in `ratings_manifest.tsv`
  is perfectly aliased with rating band on this corpus — every song at a
  given band shares one playlist_id, and each playlist represents a
  single ordinal-band collection. Genre is therefore unseparable from
  signal by construction on this corpus. Reported as
  `genre_status: "deferred_aliased_with_band"` in the leak-ablation
  summary and verdict JSON; no ablation score attempted.
- **era**: deferred pending post-yt-dlp-metadata cycle. Release-year
  metadata is not present in RECEIPTS or ratings_manifest. Reported as
  `era_status: "deferred_no_metadata"`.

## Determinism envelope

- SHA-256 tiebreak; NO PRNG anywhere in `scripts/ear_v0/*`.
- Interpreter guard: every script asserts `sys.executable ==
  "/usr/bin/python3"`.
- BLAS thread pins set before torch import:
  `OMP_NUM_THREADS = MKL_NUM_THREADS = OPENBLAS_NUM_THREADS = 1`.
- `torch.manual_seed(0)`; `torch.use_deterministic_algorithms(True)`
  where compatible.
- Non-factor sidecar isolation: AST-grep for `sidecar_nonfactor` at
  import-line start returns empty across `scripts/ear_v0/*`.
- Byte-determinism × 2: rerun steps 5–10 (feature-extract → train →
  evaluate) into a fresh `tempfile.mkdtemp()` scratch and assert
  SHA-256 equality on all six named outputs:
  `feature_cache_manifest.json`, `training_result.json`,
  `corn_head_v0_real.pt`, `held_out_predictions.tsv`,
  `leak_ablation_summary.json`, `verdict.json`.

## Anchor preservation

The following upstream anchors are READ-ONLY this cycle. Their SHA-256
manifests are recorded pre and post in
`data/ear_v0/anchor_preservation.json`; both snapshots must be equal.

- c6 feature cache manifest under `data/ear/features/`.
- `scripts/ear/{features,model,corn,leak_test}.py`.
- `scripts/classifier/tagger.py`.
- c22 stability harness: `scripts/ear/{synthetic_labels,stability_metrics,stability_audit}.py`.
- c26 Path B doc: `docs/ear_path_b_commitment.md`.

## Explicit non-goals

- No re-architecture of the c6 CORN head or the 2052-D feature
  representation (c22/c23/c25 anti-patterns locked).
- No import of `scripts.rules.sampling.i4_stratified` (c15 lock).
- No re-attempt of VGGish rung failure (c11 lock).
- No live network calls; rated audio is on-disk. Egress-probe row still
  emits `media_ok=false` non-blocking per convention.

## Handoff plan

- On **EAR_v0_LANDS**: hand `M-EAR-1/real-label-training-v1` to c37 for
  corpus expansion (43 → 80 songs as they arrive) with the honest
  partial-corpus caveat carried forward; also seed
  `M-GEN-1/first-generation` with real-ear scoring capability.
- On **EAR_v0_PARTIAL**: hand `M-EAR-1/real-label-training-v1` naming
  which SB failed. Pre-registered NOT chassis-redesign.
- On **EAR_v0_INSUFFICIENT**: first-class negative finding. Hand
  `M-EAR-1/real-label-training-v1` with the concrete remediation
  proposal (larger corpus + reweighting + era-metadata fetch as SB3
  unlock). Do NOT adjust the SB thresholds mid-cycle.
