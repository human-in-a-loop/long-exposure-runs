# v6 Phase 5 — iteration 05: localise first, then act (fair scoring mode, diagnostics, two pre-registered changes)

Date: 2026-10-05. Branch `claude/music-gen-planning-ghzop7`. Iteration 04 FLAGged every distribution gate on both backbones
against both references and its four knobs moved kid_song by at most 15 %, so this iteration first LOCALISED the gap
(docs/v6_iteration_05_diagnostics.md, all rules pre-registered) and only then changed the generator / renderer.

## 1. Fair scoring mode is now the primary gate

`scorecard.py --match-reference-format` (`scripts/v6/scorecard_format.py`): candidates are resampled / down-mixed to the
reference's modal format before embedding (cached by source sha16 under `data/v6/scorecard/format_cache/`, the transformed file's
sha keys the embedding cache), the run name gets `_fmt`, scorecard.json carries `candidate_format`. The descriptor helpers moved
verbatim to `scorecard_descriptors.py` (scorecard.py 709 -> 667 lines). Tests: `tests/test_v6_scorecard_format.py` (5).
`*_vs_corpus_accomp_fmt` is the primary gate on BOTH backbones from now on; the unmatched runs are kept.

## 2. Diagnostics in one page (details and tables in docs/v6_iteration_05_diagnostics.md)

| # | gap | evidence (iteration 04, format-matched vs corpus_accomp) | effect size |
|---|---|---|---|
| 1 | per-stem: **other** (keys + comp + melody + pad) farthest from the real Demucs "other" | CLAP kid 0.00202 vs real floor p97.5 5.2e-05; c2st 0.994; coverage 0.03; descriptors: onset rate 2.6 vs 4.1 Hz (d -1.34), harmonic/percussive +4.8 dB (d +1.25), low share -5 dB, RMS +4.8 dB | **39x** the floor |
| 2 | per-stem: **bass** | kid 0.0019 vs 1.5e-04; c2st 1.000; coverage 0.003; the real stem is 98 % < 250 Hz with a broadband bleed tail, ours clean and mid-heavy | 12.9x (partly a Demucs-bleed artefact) |
| 3 | per-stem: **drums** | kid 0.00148 vs 2.0e-04; c2st 0.98; +4.5 dB > 4 kHz, harmonic/percussive +5.6 dB, RMS +2.9 dB | 7.3x |
| 4 | **homogeneity** (set level) | candidate song-mean spread 0.093 vs 0.215 (clap), 0.019 vs 0.038 (mert); 5th-percentile candidate pair cosine above the median real pair; LUFS sd 0.55 vs 3.4 LU, 24/29 bop kits, 12/29 one piano | spread ratio **0.43 / 0.50** (rule: < 0.60 confirms) |
| 5 | **tonal balance / dynamics** (what the classifier hears) | LDA score AUC 1.000; top descriptors: > 4 kHz share +5.95 dB (d 0.98), zcr +50 % (d 1.03), rolloff +945 Hz, centroid +391 Hz, within-window dynamic range -7.9 dB (d -0.62), crest -1 dB; the iteration-04 tilt steer sat 4-6 dB short of the band target (shelf saturated at -2.5 dB) | d 0.6-1.0 |
| 6 | mix chain as such (oracle: real stems through our chain) | real stems re-mixed through `mix.mix_song` vs corpus_accomp, split protocol: kid 0.57x the CLAP floor p97.5 / 0.30x MERT; c2st 0.642 (gate 0.61, marginal) / 0.497; coverage 0.65 vs 0.72 / 0.79 vs 0.78 -> **PASS on both backbones**: the chain is not the gap | within the floor |

Format matching alone removed 41 % of the CLAP kid (0.001361 -> 0.000799) and 9 % of the MERT kid (0.006435 -> 0.005829);
both backbones stay FLAG on every gate at ~8x their floor.

## 3. Pre-existing bug fixed: section_repeat_integrity 25/29 -> 29/29

The iteration-04 diagnosis ("a skeleton repair is not inherited") was only part of it: `melody.fill_weak`'s suspension test reads
the PRECEDING pitch, which in a recurrence is a re-drawn non-skeleton note, so the realised skeleton flipped between
"suspension + resolution" and a plain skeleton note across occurrences (song 4 had no repair at all). `humanize.vary_recurrences`
now copies the label's REALISED skeleton notes (`humanize.realised_skeleton`, post-repair) into every recurrence and drops weak
onsets inside a suspension's (s, s+4]. Regression test `tests/test_v6_humanize.py::test_10` (fixtures 12 seeds x 3 donors +
iteration-04 songs 1/3/4/17 with the real rules). Seed sweep 72/72 (`data/v6/gen/sweeps/seed_sweep_20261005T0600Z_it05_skeleton`),
29-donor seed-3 `--no-render` pass 29/29 on every cap.

## 4. The two changes (pre-registered in docs/v6_iteration_05_diagnostics.md §5 before iteration 05 was rendered)

Change 1 — homogeneity (gap 4): (a) the drum-kit FAMILY is SHA-drawn per song from `KIT_FAMILY_PRIOR` BEFORE the CLAP ranking
(`select.KIT_FAMILY_FIRST`; the softmax temperature was shown to be a weak knob: re-drawing the recorded iteration-04 top-5 lists at
T = 0.05..0.20 kept 21-24/29 jazz kits); (b) one loudness target PER SONG, SHA inverse-CDF over the band's per-song corpus LUFS
list, clamped to [-16, -12] (`mix.song_target_lufs`); (c) per-song room size (+/- 0.08) and reverb return (+/- 2 dB)
(`mix.song_room`). All recorded (`patch_plan.json[selection.drums.kit_family*]`, `mix_manifest.json[song_variation]`).
Pre-registered expectations: distinct kits >= 10/29 and jazz share <= 50 %; candidate LUFS sd >= 1.2 LU; CLAP spread ratio >= 0.55.

Change 2 — tonal balance and the "other" layer (gaps 5 and 1): (a) `mix.TILT_STEER` full strength with a 6 dB cap (was 0.5 x,
3 dB); (b) comping guitar more often and denser (`ENSEMBLE_P` comp_guitar 0.5 -> 0.7, `parts.COMP_KEEP_P` 0.55 -> 0.7) and
percussion 0.25 -> 0.4 (recorded in `render_manifest.json[iteration_05]`). Pre-registered expectations: master tilt within 2 dB of
the band target on most songs; > 4 kHz share gap shrinks from +6 dB toward +2 dB; "other" onset rate rises toward >= 3.2 Hz.
Tests: `tests/test_v6_iteration05_changes.py` (5).

## 5. Iteration 05 (seed 4, 29 donors, humanize, renderer v6, replay proofs)

`data/v6/gen/iteration_05_corpus`: 29/29 songs composed and rendered (compose ~2 s, render 26-69 s, median 42 s), replay
proofs 29/29 HOLD (`ab_mix.replay_proof.json`), validators 29/29 on EVERY cap (`validators_table.json`; iteration 04 was 25/29,
the four section_repeat_integrity failures are gone with the realised-skeleton fix). All manifests carry the iteration-05 fields
(`patch_plan.json` kit family draw, `mix_manifest.json[song_variation]`, `render_manifest.json[iteration_05]`).

Pre-registered expectations of the two changes, measured on the 29 manifests:

| expectation (written before the render) | iteration 04 | iteration 05 | met |
|---|---|---|---|
| distinct drum kits >= 10 / 29, jazz (bop / brush) share <= 50 % | 6 kits, 24/29 jazz | 10 kits (AVL Black Pearl 13, GM Room 4, GM Power 3, ...), families neutral 15 / rock 8 / jazz 6 | yes |
| candidate LUFS sd >= 1.2 LU (per-song targets) | -12.34 ± 0.35 (44.1 kHz stereo) | -13.26 ± 1.50, targets -16.0 .. -12.0 | yes |
| master tilt within 2 dB of the band target | 3.2 dB short on average, shelf saturated at -2.5 dB | residual +0.55 ± 0.70 dB (shelf -3.1 dB mean, 2 songs at the -6 dB cap) | yes |
| CLAP song-mean spread ratio >= 0.55 (homogeneity rule 0.60) | 0.434 | **0.405** (mert 0.479, was 0.498) | **no — slightly worse** |
| > 4 kHz share gap shrinking toward +2 dB | +5.95 dB | **+1.5 dB** (centroid gap +391 -> -43 Hz, rolloff +945 -> +12 Hz) | yes |
| "other" group onset rate toward >= 3.2 Hz | 2.59 Hz | 2.72 Hz (real 4.13) | **no** |

Mix descriptors in the fair (22.05 kHz mono) domain now sit ON the reference: LUFS -16.96 ± 1.48 vs -17.2 ± 3.4 (gap 0.24 LU, was
1.0), crest 14.83 ± 1.46 vs 14.97 ± 2.24 (gap -0.14 dB, was -1.0), centroid 1699 ± 222 vs 1674 ± 444 Hz (gap +25 Hz, was +424).

### 5.1 Scorecards (thresholds in parentheses; `*_fmt` = fair mode, the primary gate)

PENDING_SCORE_TABLE

### 5.2 Diagnostics re-run on iteration 05

Discriminant descriptors (fair mode): the LDA score still separates the sets perfectly (AUC 1.000 on both backbones) but every
descriptor that explained it in iteration 04 has collapsed: top |rho| 0.27 (was 0.45); > 4 kHz share rho 0.08 (was 0.45, gap +1.5 dB
vs +6.0), centroid rho 0.04 (gap -43 Hz vs +391), rolloff gap +12 Hz (vs +945), zcr d 0.25 (vs 1.03). What is left: within-window
dynamic range -6.75 dB (rho -0.27, d -0.51), mid-band share +1.8 dB (d 0.57), spectral flatness lower (d -0.52). In words: the
spectral-balance correlates were real and were removed, and the classifier is just as sure as before — the remaining distance is
not in low-level spectral balance.

Per-stem descriptors (candidate groups vs real Demucs stems): "other" is unchanged in the properties that matter (onset rate 2.72 vs
4.13 Hz, harmonic/percussive +5.4 dB, low share -4.8 dB) and brighter than before in its > 4 kHz share (+6.7 dB; the added
comping guitar strums are bright); drums went from too bright to too DARK (centroid 2081 vs 3159 Hz, zcr 0.078 vs 0.186, > 4 kHz
-1.3 dB) under the full-strength shelf while staying too tonal (H/P +6.3 dB) — the global tilt shelf fixed the mix-level number by
pushing the drums past the target instead of darkening the "other" layer that carried the excess. Bass unchanged (confounded).

PENDING_STEMS_IT05

Spread: CLAP 0.405 / MERT 0.479 (CONFIRMED on both; 0.434 / 0.498 in iteration 04): kit families, loudness targets and rooms now
vary per song, yet the songs' CLAP means are marginally MORE alike — the between-song variance ratio fell 0.95 -> 0.86. The
diversity that a music embedding sees is not the diversity these draws add.

### 5.3 Ablations (one change reverted at a time, 29 songs each, CLAP fair mode vs corpus_accomp)

PENDING_ABLATIONS


## 6. What moved, what got worse

PENDING_MOVED
