---
created: 2026-08-29T11:00:00Z
cycle: 38
run_id: run-2026-08-28T040704Z
agent: worker (clone-0)
milestone: M-EAR-1/real-label-training-v1
---

# EAR v1 — Real-Label Training Rubric (frozen, cycle 38)

## Purpose

This rubric is committed BEFORE any script under `scripts/ear_v1/`
lands, and BEFORE `scripts/ear/leak_test.py` is edited to substitute
the c37 clone-1 F1 pooled-variance statistic for the c6
`S = max(S_model, S_resid)` line. Its SHA-256 is written to
`data/ear_v1/rubric_hash.txt` (32-hex, no trailing newline) and
embedded verbatim as `rubric_hash` in `data/ear_v1/verdict.json`.

The rubric is a mtime + git-log dual gate: every mtime under
`scripts/ear_v1/` and the anchored `scripts/ear/leak_test.py` edit
MUST postdate the rubric commit, and `tests/test_ear_real_label_training_v1.py`
enforces both channels.

## Three-verdict rubric (verbatim, frozen)

- **EAR_v1_LANDS** — SB1 margin > 0.5909 (MAE beats
  `min(majority-class, mean-integer)` by more than the c22
  recipe-envelope IQR) AND SB2 mean pairwise Kendall τ ≥ 0.4 across
  10 stratified bootstrap resamples AND SB3 F1 pooled-variance
  detection ≥ 0.90 at α=1.0 per leak type with FPR ≤ 0.10 per leak
  type. Named SB verdicts required.
- **EAR_v1_PARTIAL** — at least one of SB1/SB2/SB3 short of its
  threshold; named-SB attribution required + numeric shortfall.
- **EAR_v1_INSUFFICIENT** — corpus or chassis pathology blocks
  credible measurement. Concrete failure mode named + characterized.
  First-class close.

## Corpus honesty caveat

The rated corpus is 43 of the 80-song target — 54% corpus coverage.
The v1 verdict is credible for the corpus that exists on disk; it is
NOT calibrated to the full 80-song target. This caveat is carried in
the report abstract, again in §2, again in the verdict section, and
again as the last line before c39 handoff seeds.

## Scale honesty

The corpus covers bands {4, 5, 6, 7}. Bands {1, 2, 3} are absent.
`verdict.json.scale_bounds` records `{min: 4, max: 7,
absent_bands: [1, 2, 3]}`. The head is a partial-corpus preview.

## Non-factor coverage (SB3)

- **artist**: parsed from filename (c36 clone-0 convention). Live
  channel for the F1 pooled-variance detector.
- **genre**: `deferred_aliased_with_band` — `playlist_id`
  perfectly aliases with rating band on this corpus. Emitted as
  a field, not a comment.
- **era**: `deferred_no_metadata` — no release-year in
  RECEIPTS / ratings_manifest.tsv. Emitted as a field, not a
  comment.

## Determinism envelope

- α pinned campaign-wide at 0.7469387071101908 (Fixed Decisions).
- SHA-256 tiebreak; NO PRNG anywhere in `scripts/ear_v1/*`.
- Interpreter guard on every script: `sys.executable ==
  "/usr/bin/python3"`.
- BLAS thread pins set before torch import: `OMP_NUM_THREADS =
  MKL_NUM_THREADS = OPENBLAS_NUM_THREADS = 1`.
- `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH` pinned, `TZ=UTC`,
  `LC_ALL=C.UTF-8`, `torch.manual_seed(0)`, single-thread BLAS.
- `verdict.json`, `leak_test_summary.json`, `corn_head_v1.pt`
  MUST be byte-identical across two independent fresh-temp-dir
  runs. Enforced by `determinism_check.json` × 2.

## Authorized mutations under c38 anchor-preservation authorization

- `scripts/ear/leak_test.py` — retire `max(S_model, S_resid)`;
  substitute the c37 clone-1 F1 pooled-variance implementation.
  Stable name `f1_pooled_variance_statistic(y_true, y_pred,
  leak_labels) -> float`. No compat shim. Add
  `statistic_version = "F1_pooled_variance_v1"` field to emitted
  rows. `data/ear_v1/leak_test_diff_manifest.json` records
  `{file, old_sha256, new_sha256, changed_line_ranges}`.

## Anti-patterns (frozen out)

- c22 synthetic-label-stability, c23 head-regularization, c25
  feature-representation: those audits invalidated on the 55-clip
  synthetic-label valset. This cycle is the c26 Path B REAL-LABEL
  trigger firing — different corpus, different statistic. Nothing
  here re-attempts a synthetic-label chassis audit.
- c11 CLAP/VGGish embedding — no embedding-family import.
- c35 palette-schema-v2-hydration-render — no palette code touched.
- c8 basic-pitch octave-suppression — not on the path.
