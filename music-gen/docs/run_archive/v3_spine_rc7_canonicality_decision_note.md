# v3 spine — rc7 canonicality decision note (c7 Track B)

**Milestone:** `M-V3-SPINE-1/rc7-canonicality-note-completed`
**Cycle:** 7
**Scope:** one-page characterization only. No code change, no verdict-shifting
artifact, no recommendation. Feeds the operator ear decision loop.

## What this note is

The v3 spine currently has two byte-deterministic-within-cycle reconstruction
paths for the 30 s Chicken Grease operator section, sharing all upstream
transcription and per-track render. They differ only in the final per-stem
loudness-match + sum stage:

- **Method A** (cycle 5, `scripts/v3_spine/mix_match_operator_section.py`) —
  plain broadband per-stem RMS match, then sum. No EQ, no LUFS-S targeting.
- **Method B** (cycle 6, `scripts/v3_spine/rc7_v2_rerun_v3_paths.py`) — v3-input
  fork of c53 `rc7_v2_rerun.py`: 12-band iirpeak (Q=1.4, `np.geomspace(20,
  20000, 12)`) EQ curve fit per stem from the original 6-stem spectrum, plus
  RMS + LUFS-S loudness targeting per stem, then sum.

Both are internally consistent. Both are byte-deterministic across two fresh
`tempfile.mkdtemp()` runs within their own cycle. Both take the same c5
per-track WAVs and the same per-stem loudness anchors as inputs. Neither is
this note's preferred output.

## Per-file characterization

Raw numbers from `data/v3_spine/cycle7/rc7_canonicality_metrics.json`.
Reference: `data/v3_spine/31a164f845f8e27e/operator_section/section.wav`
(30 s @ 44.1 kHz stereo; the Chicken Grease operator section, t = 233.639..263.639 s).

| Metric | Method A (c5 plain RMS-match) | Method B (c6 iirpeak EQ + RMS + LUFS-S) |
|---|---:|---:|
| SHA-256 (first 16 hex) | `cc919559b4508b6b…` | `f40796be982998b0…` |
| Path (repo-relative) | `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav` | `data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav` |
| Sample rate (Hz) | 44100 | 44100 |
| Channels | 2 | 2 |
| Duration (s) | 30.000 | 30.000 |
| LUFS-I (integrated, LU) | −19.95 | −17.87 |
| LUFS-S mean (LU) | −20.02 | −18.02 |
| LUFS-S std (LU) | 0.640 | 0.889 |
| LUFS-S max (LU) | −19.07 | −17.06 |
| True peak (dBFS, max abs sample) | −3.01 | −0.01 |
| Max abs sample (linear) | 0.7070 | 0.9990 |
| Spectral centroid mean (Hz) | 3910.1 | 2353.2 |
| Spectral centroid std (Hz) | 2740.0 | 1619.2 |
| Spectral flatness mean | 0.03025 | 0.00684 |
| Mel L1 vs original operator-section (0..30 s, dB) | 8.727 | 7.489 |

## What the numbers describe

- Method B sits ~2 LU louder integrated and ~2 LU louder short-term than
  Method A, and pushes the true peak from −3 dBFS up to −0.01 dBFS. That is
  the LUFS-S targeting stage doing its job — the RMS-only Method A leaves
  a lower operating level.
- Method B's spectral centroid is ~1.5 kHz lower than Method A's, with about
  60 % of Method A's spread; the 12-band iirpeak shaping pulls energy out
  of the upper octave and down into the low-mid band. Spectral flatness
  drops accordingly.
- Method B lands ~1.2 dB closer to the original operator section on mel-L1,
  measured mono against `section.wav` over the first 30 s. Mel-L1 is
  documentary, not decisive — per FD-6 the panel is never authoritative.
- Both files hit the same duration (1_323_000 samples) with the same
  channel count and sample rate. Track C's empty-stem probe confirms this
  (`data/v3_spine/cycle7/empty_stem_duration_sanity.json`).

## What this note is not

- Not a recommendation. Neither method is promoted. Neither is retired.
- Not an aggregate score. Each row above is one measurement; there is no
  weighted sum.
- Not a verdict-shifting artifact. Cycle 6's verdict (see
  `data/v3_spine/verdict_c6.json`) already closes the method-equivalence
  question as `MODERATE_2_METHODS_DIFFER_EXPECTED` (Method B numerically
  differs from Method A by max-abs 0.502, corr 0.965; the EQ chain reshapes
  the spectrum vs plain RMS match — first-class per FD-1).

## Operator handoff

Operator ear on the two A/B pairs remains the only authoritative gate per
FD-6; this note characterizes both candidates so the operator can compare
them against their internal reference for Chicken Grease. The A/B pairs are:

- Method A: `data/v3/deliveries/31a164f845f8e27e/operator_section/{original_ab,reconstruction_ab}_operator_section.wav`
- Method B: reconstructed from `data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav` (mirror the AB slicing when the operator asks).
