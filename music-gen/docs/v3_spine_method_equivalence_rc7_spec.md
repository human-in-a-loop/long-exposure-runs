# v3 Spine — rc7 Method-Equivalence Spec (Cycle 6, Track B)

Pinned pre-code per FD-1 discipline. Closes c5 MODERATE finding #2.

## Objective

Numeric side-by-side of two per-stem mixdown methods on the *same* v3
operator-section inputs:

- **Method A** = c5's inline plain per-stem RMS-match
  (implementation: `scripts/v3_spine/mix_match_operator_section.py`).
  Per-stem gain clamp ±24 dB, sum, peak-limit 0.707, int16 stereo.
- **Method B** = additive-sibling v3-paths fork of the c53
  `scripts/recreate_v2/rc7_v2_rerun.py` chain
  (`scripts/v3_spine/rc7_v2_rerun_v3_paths.py`). Consumes the same v3
  per-track WAVs as "bare" (skips MIDI-split-and-fluidsynth-render because
  v3 already has per-track WAVs). Fits 12-band iirpeak EQ (Q=1.4,
  log-spaced 20..20 kHz) vs baseline stem spectrum, applies EQ + RMS
  loudness match (max gain 48 dB), sums, peak-limits 0.999, int16
  stereo via `_canonicalize_wav_deterministic`.

## Inputs

- Rendered per-track WAVs (source for both methods):
  `data/v3_spine/31a164f845f8e27e/operator_section/render/per_track/{drums,bass,guitar,piano,other}.wav`
  plus `.../render/vocals_htdemucs.wav`.
- Baseline stems (target RMS + EQ target spectrum):
  `data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/{drums,bass,guitar,piano,other,vocals}.wav`.

## Anti-instructions

- `scripts/recreate_v2/rc7_v2_rerun.py` is READ-ONLY. Do not edit.
- `scripts/palette_render/render_stem.py` is READ-ONLY. Do not edit.
- `scripts/v3_spine/mix_match_operator_section.py` is READ-ONLY. Do not
  edit. If numeric equivalence holds the finding closes on the audit;
  no code churn.
- No PRNG. `/usr/bin/python3`. Env pins per c5 (BLAS single-thread,
  `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, TZ=UTC).
- Do not re-implement rc7 a third way — the fork is a wrapper around
  READ-ONLY imports from `scripts.recreate_v2.rc7_mix_balance`
  (`_fit_eq_curve_from_original`, `_apply_old_chain_baseline`,
  `_sha256_file`, `_read_wav_float`, `_rms_db`) plus
  `scripts.palette_render.render_stem` (`_apply_eq_curve_iirpeak`,
  `_apply_loudness_target`, `_canonicalize_wav_deterministic`).

## Metrics

For each of {drums, bass, guitar, piano, other, vocals} per-stem *matched*
outputs and for the full-mix bounce, compute:

- `rms_delta_db` = |RMS_A_db − RMS_B_db|
- `lufs_s_delta_lu` = |LUFS-S_A − LUFS-S_B| (via `pyloudnorm.Meter(sr)`
  integrated_loudness proxy — LUFS-S window not required for
  short-duration equivalence check; if pyloudnorm unavailable, fall back
  to `rms_delta_db` only and record `lufs_available=false`)
- `max_abs_diff` = max |A[i] − B[i]| after sample-level alignment
  (same shape asserted; zero-pad the shorter to the longer's length)
- `corr` = Pearson correlation of A vs B (mono mixdown for stereo)

## Success bar

`max_abs_diff` on the full-mix bounce ≤ 1e-3 → methods are numerically
equivalent → c5 MODERATE #2 closes as `MODERATE_2_METHOD_EQUIVALENT_CLOSED`.

Anything larger is a first-class finding (not a failure to smooth over —
FD-1). Verdict is honest disclosure of the delta and its interpretation:

- `MODERATE_2_METHODS_DIFFER_EXPECTED` if delta > 1e-3 (interpretation: EQ chain
  fundamentally reshapes spectrum, RMS-match alone does not).

## Determinism

Both methods must byte-det ×2 on the same inputs. Recorded in the JSON.

## Deliverables

- `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` (Method B implementation)
- `scripts/v3_spine/method_equivalence_rc7.py` (comparator + JSON emitter)
- `data/v3_spine/rc7_method_equivalence.json` (metrics + verdict)
- `data/v3_spine/rc7_v2_v3_paths/` (Method B outputs)
