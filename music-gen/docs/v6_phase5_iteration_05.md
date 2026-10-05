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

Runs: `data/v6/scorecard/runs/iteration_0{4,5}_corpus_vs_corpus_accomp_fmt` (primary), `..._vs_corpus_accomp`, `..._vs_corpus`; archived under
`docs/scorecards/`. Bold = gate metrics. Every gate FLAGs in every run of both iterations; novelty PASSes everywhere (no copying).

| reference / backbone / metric | iteration 04 | iteration 05 | change | threshold | verdict 05 |
|---|---|---|---|---|---|
| vs corpus_accomp FMT / clap / **kid_song** | 0.0007987 | 0.001208 | +51 % | 9.75e-05 | FLAG |
| vs corpus_accomp FMT / clap / **c2st** | 0.9256 | 0.9527 | +3 % | 0.61 | FLAG |
| vs corpus_accomp FMT / clap / **coverage** | 0.2212 | 0.1578 | -29 % | > 0.492 | FLAG |
| vs corpus_accomp FMT / clap / density | 2.455 | 1.381 | -44 % | - | INFO |
| vs corpus_accomp FMT / clap / fad | 0.2715 | 0.3369 | +24 % | - | INFO |
| vs corpus_accomp FMT / clap / kNN-real | 0.006553 | 0.004276 | -35 % | - | INFO |
| vs corpus_accomp FMT / clap / novelty_max_cos | 0.951 | 0.9485 | -0 % | 0.985 | PASS |
| vs corpus_accomp FMT / mert / **kid_song** | 0.005829 | 0.005381 | -8 % | 0.000717 | FLAG |
| vs corpus_accomp FMT / mert / **c2st** | 0.9259 | 0.9266 | +0 % | 0.57 | FLAG |
| vs corpus_accomp FMT / mert / **coverage** | 0.3136 | 0.3156 | +1 % | > 0.603 | FLAG |
| vs corpus_accomp FMT / mert / density | 1.457 | 1.143 | -22 % | - | INFO |
| vs corpus_accomp FMT / mert / fad | 9.404 | 9.03 | -4 % | - | INFO |
| vs corpus_accomp FMT / mert / kNN-real | 0.007767 | 0.01948 | +151 % | - | INFO |
| vs corpus_accomp FMT / mert / novelty_max_cos | 0.9819 | 0.9811 | -0 % | 0.995 | PASS |
| vs corpus_accomp (unmatched) / clap / **kid_song** | 0.001361 | 0.001872 | +38 % | 9.75e-05 | FLAG |
| vs corpus_accomp (unmatched) / clap / **c2st** | 0.9835 | 0.99 | +1 % | 0.61 | FLAG |
| vs corpus_accomp (unmatched) / clap / **coverage** | 0.08477 | 0.04273 | -50 % | > 0.492 | FLAG |
| vs corpus_accomp (unmatched) / clap / density | 0.1604 | 0.0715 | -55 % | - | INFO |
| vs corpus_accomp (unmatched) / clap / fad | 0.3759 | 0.4521 | +20 % | - | INFO |
| vs corpus_accomp (unmatched) / clap / kNN-real | 0.001699 | 0.003563 | +110 % | - | INFO |
| vs corpus_accomp (unmatched) / clap / novelty_max_cos | 0.9333 | 0.9304 | -0 % | 0.985 | PASS |
| vs corpus_accomp (unmatched) / mert / **kid_song** | 0.006435 | 0.005736 | -11 % | 0.000717 | FLAG |
| vs corpus_accomp (unmatched) / mert / **c2st** | 0.9313 | 0.9312 | -0 % | 0.57 | FLAG |
| vs corpus_accomp (unmatched) / mert / **coverage** | 0.2853 | 0.2901 | +2 % | > 0.603 | FLAG |
| vs corpus_accomp (unmatched) / mert / density | 1.258 | 1.017 | -19 % | - | INFO |
| vs corpus_accomp (unmatched) / mert / fad | 9.664 | 9.204 | -5 % | - | INFO |
| vs corpus_accomp (unmatched) / mert / kNN-real | 0.006553 | 0.01686 | +157 % | - | INFO |
| vs corpus_accomp (unmatched) / mert / novelty_max_cos | 0.9812 | 0.981 | -0 % | 0.995 | PASS |
| vs corpus (unmatched) / clap / **kid_song** | 0.001662 | 0.002178 | +31 % | 0.000199 | FLAG |
| vs corpus (unmatched) / clap / **c2st** | 0.9306 | 0.9528 | +2 % | 0.67 | FLAG |
| vs corpus (unmatched) / clap / **coverage** | 0.1741 | 0.1378 | -21 % | > 0.467 | FLAG |
| vs corpus (unmatched) / clap / density | 4.168 | 3.384 | -19 % | - | INFO |
| vs corpus (unmatched) / clap / fad | 0.4767 | 0.5547 | +16 % | - | INFO |
| vs corpus (unmatched) / clap / kNN-real | 0.002913 | 0.0019 | -35 % | - | INFO |
| vs corpus (unmatched) / clap / novelty_max_cos | 0.9373 | 0.9411 | +0 % | 0.985 | PASS |
| vs corpus (unmatched) / mert / **kid_song** | 0.005126 | 0.005055 | -1 % | 0.000851 | FLAG |
| vs corpus (unmatched) / mert / **c2st** | 0.9746 | 0.9769 | +0 % | 0.55 | FLAG |
| vs corpus (unmatched) / mert / **coverage** | 0.1371 | 0.1193 | -13 % | > 0.555 | FLAG |
| vs corpus (unmatched) / mert / density | 0.382 | 0.2081 | -46 % | - | INFO |
| vs corpus (unmatched) / mert / fad | 7.666 | 7.459 | -3 % | - | INFO |
| vs corpus (unmatched) / mert / kNN-real | 0.01019 | 0.02043 | +100 % | - | INFO |
| vs corpus (unmatched) / mert / novelty_max_cos | 0.9821 | 0.9816 | -0 % | 0.995 | PASS |


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

| group (CLAP vs real Demucs stems) | kid 04 | kid 05 | floor p97.5 | ratio 04 | ratio 05 | c2st 04 -> 05 | coverage 04 -> 05 | kNN-real 04 -> 05 |
|---|---|---|---|---|---|---|---|---|
| other | 0.00202 | 0.00205 | 5.16e-05 | 39.1x | **39.8x** | 0.994 -> 0.988 | 0.027 -> 0.022 | 0.000 -> 0.006 |
| bass | 0.0019 | 0.00199 | 0.000147 | 12.9x | **13.5x** | 1.000 -> 0.999 | 0.003 -> 0.000 | 0.000 -> 0.001 |
| drums | 0.00148 | 0.00221 | 0.000202 | 7.3x | **10.9x** | 0.980 -> 0.978 | 0.049 -> 0.023 | 0.019 -> 0.031 |

Per-stem CLAP, iteration 04 vs 05 (same real-stem floors): "other" and bass unchanged within noise, **drums worse** (7.3x -> 10.9x): the drawn kit families put GM sf2 kits (Room / Power / Jazz / Brush / Standard) on 11 of 29 songs where iteration 04 had sampled AVL kits on 25, and the full-strength shelf pushed the kit past the target into too-dark territory.

Iteration 05 per-stem table in the full layout of docs/v6_iteration_05_diagnostics.md §3 (CLAP, candidate groups format-matched to
the Demucs stems, 10 deterministic real-vs-real splits; stems re-rendered with `--keep-stems`, mix replay equal 29/29; the stem wavs
were deleted after scoring, `data/v6/scorecard/diagnostics/iteration_05/stems_it05/stems_diagnostic.json` keeps the numbers):

| group (cand vs real, CLAP) | kid_song | real floor p97.5 | gap ratio | c2st | floor c2st | coverage | floor cov | kNN-real | floor kNN | windows cand / real |
|---|---|---|---|---|---|---|---|---|---|---|
| other | 0.00205 | 5.16e-05 | **39.8x** | 0.988 | 0.462 | 0.022 | 0.766 | 0.006 | 0.585 | 774 / 1446 |
| bass | 0.00199 | 0.000147 | **13.5x** | 0.999 | 0.457 | 0.000 | 0.807 | 0.001 | 0.531 | 842 / 1174 |
| drums | 0.00221 | 0.000202 | **10.9x** | 0.978 | 0.520 | 0.023 | 0.691 | 0.031 | 0.481 | 837 / 1310 |

Ranking unchanged (other > bass > drums), every group still an order of magnitude outside its own floor; drums moved toward bass.
Per-stem descriptor gaps, iteration 05 (Cohen's d in parentheses): **other** H/P ratio +5.4 dB (+1.40), onset rate 2.72 vs 4.13 Hz
(-1.22), mid share +1.5 dB (+0.91), low share -4.8 dB (-0.91), > 4 kHz share +6.7 dB (+0.84), RMS +4.4 dB (+0.76); **drums** zcr
0.078 vs 0.186 (-1.33), centroid 2081 vs 3159 Hz (-1.22), H/P +6.3 dB (+1.01), rolloff -1353 Hz (-0.91), low share +2.6 dB (+0.54),
RMS +2.8 dB (+0.38); **bass** mid share +10.8 dB (+1.57), bandwidth -704 Hz (-1.39), dynamic range +50 dB (+1.21), centroid -529 Hz
(-0.92) — the bass gaps are the Demucs-bleed signature of the diagnostics doc, unchanged.

Spread: CLAP 0.405 / MERT 0.479 (CONFIRMED on both; 0.434 / 0.498 in iteration 04): kit families, loudness targets and rooms now
vary per song, yet the songs' CLAP means are marginally MORE alike — the between-song variance ratio fell 0.95 -> 0.86. The
diversity that a music embedding sees is not the diversity these draws add.

### 5.3 Ablations (one change reverted at a time, 29 songs each, CLAP fair mode vs corpus_accomp)

Protocol (scratch `ablate.py`): the 29 iteration-05 songs were re-rendered from their own `render_manifest.json` (same donor, band,
seed 4, same compositions — only the renderer settings differ), each mix format-matched to 22.05 kHz mono at once and the 44.1 kHz
wav deleted, then scored with `scorecard.py --match-reference-format --backbones clap` against `corpus_accomp` (runs
`iteration_05_ablation_{A,B,C,C1,D}_vs_corpus_accomp_fmt`, archived under `docs/scorecards/`). MERT was NOT run on the ablations:
one MERT pass over 29 mixes is ~1 h under the shared CPU with the MUSDB embed holding the one-embedding-at-a-time slot, i.e. not
cheap; the CLAP numbers are what the attribution rests on. CLAP spread = `diag_embed_v6.py spread` on each ablation's scorecard
(cached embeddings).

| ablation | what is reverted relative to full iteration 05 | code |
|---|---|---|
| A | tilt steer back to iteration-04 strength: 0.5 x with a 3 dB cap (iteration 05: 1.0 x, 6 dB) | `mix.TILT_STEER = {strength 0.5, cap_db 3.0}` |
| B | density knobs back to iteration 04: comp_guitar 0.5, percussion 0.25, `COMP_KEEP_P` 0.55 (iteration 05: 0.7 / 0.4 / 0.7); 11/29 renders are byte-identical to iteration 05 (songs whose ensemble draw did not change) | `select.ENSEMBLE_P`, `parts.COMP_KEEP_P` |
| C | the whole homogeneity package off: kit family NOT drawn first (CLAP ranking over all kits as in iteration 04), ONE loudness target (the reference's -12 LUFS) for every song, band room size and the fixed reverb return | `select.KIT_FAMILY_FIRST = False`, `mix.song_target_lufs`, `mix.song_room` stubbed |
| C1 | kit-family-first off ONLY (per-song loudness target and room draws kept) — splits C into its kit part and its loudness / room part | `select.KIT_FAMILY_FIRST = False` |
| D | A + B + C together = the iteration-04 renderer on the iteration-05 compositions (seed 4, realised-skeleton fix); the residual D vs iteration 04 is what the compositions / seed changed, not the renderer | all of the above |

| set (CLAP, fair mode vs corpus_accomp) | **kid_song** (9.75e-05) | **c2st** (0.61) | **coverage** (> 0.492) | kNN-real | fad | density | novelty (0.985) | CLAP spread ratio (rule 0.60) | kits jazz / neutral / rock | LUFS target sd | tilt shelf mean dB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| iteration 04 (seed 3) | 0.000799 | 0.926 | 0.221 | 0.0066 | 0.272 | 2.46 | 0.951 | 0.434 | 24 / 5 / 0 (3 bop/brush kits on 24) | 0 (-12) | ~ -2.5 (saturated) |
| **iteration 05** (seed 4) | **0.001208** | 0.953 | 0.158 | 0.0043 | 0.337 | 1.38 | 0.949 | 0.405 | 6 / 15 / 8 | 1.50 | -3.18 |
| A: tilt steer 0.5 x / 3 dB | 0.001194 | 0.950 | 0.158 | 0.0043 | 0.335 | 1.42 | 0.949 | 0.402 | 6 / 15 / 8 | 1.50 | -1.56 |
| B: density knobs 04 | 0.001199 | 0.951 | 0.164 | 0.0043 | 0.336 | 1.38 | 0.949 | 0.415 | 6 / 15 / 8 | 1.50 | -3.18 |
| C: homogeneity package off | **0.000967** | 0.936 | 0.191 | 0.0086 | 0.299 | 1.64 | 0.952 | 0.442 | 20 / 4 / 5 | 0 (-12) | -4.76 |
| C1: kit-family-first off only | {{C1_kid}} | {{C1_c2st}} | {{C1_cov}} | {{C1_knn}} | {{C1_fad}} | {{C1_dens}} | {{C1_nov}} | {{C1_spread}} | {{C1_kits}} | 1.50 | {{C1_shelf}} |
| D: A + B + C | {{D_kid}} | {{D_c2st}} | {{D_cov}} | {{D_knn}} | {{D_fad}} | {{D_dens}} | {{D_nov}} | {{D_spread}} | {{D_kits}} | 0 (-12) | {{D_shelf}} |

Attribution of the CLAP regression (fmt kid_song 0.000799 -> 0.001208, +0.000409, +51 %), one revert at a time:

- **Change 1, the homogeneity package, is the cause.** Reverting it alone (C) takes kid_song 0.001208 -> 0.000967, i.e. recovers
  0.000241 = **59 %** of the regression, and moves every other CLAP number the same way (c2st 0.953 -> 0.936, coverage 0.158 ->
  0.191, fad 0.337 -> 0.299, kNN-real 0.0043 -> 0.0086). {{C1_TEXT}}
- Change 2a, the full-strength tilt steer (A), accounts for 0.000014 = **3 %**; change 2b, the density knobs (B), for 0.000009 =
  **2 %** — both inside the run-to-run noise of a 29-song set (the B renders are byte-identical to iteration 05 on 11 songs).
- {{D_TEXT}}
- The homogeneity package did not even buy what it was for: the CLAP spread ratio is 0.442 with the package OFF (C) and 0.405 with it
  ON — the per-song kit-family / loudness / room draws made the songs' CLAP means slightly MORE alike while making each song less like
  the reference. A (0.402) and B (0.415) leave the spread where iteration 05 has it. Diversity in the renderer's texture parameters is
  not diversity that CLAP measures between songs.
- Caveat: iteration 04 is seed 3 and pre-dates the realised-skeleton fix, the ablations are seed 4 with it; D (iteration-04 renderer
  settings on the iteration-05 compositions) is the clean reference point for the renderer changes, iteration 04 itself is not.


## 6. What moved, what got worse

### 6.1 Iteration 04 vs 05, both references, both backbones, unmatched and format-matched

Runs: `data/v6/scorecard/runs/iteration_0{4,5}_corpus_vs_corpus{,_accomp,_accomp_fmt}/`. Thresholds in parentheses (vs corpus /
vs corpus_accomp / vs corpus_accomp fmt; the fmt run uses the corpus_accomp gates); every gate metric FLAGs in all six runs on both
backbones, novelty PASSes everywhere (no copying). The `_fmt` columns are the primary gate.

| backbone / metric | it04 vs corpus | it05 vs corpus | it04 vs corpus_accomp | it05 vs corpus_accomp | it04 vs corpus_accomp FMT | it05 vs corpus_accomp FMT |
|---|---|---|---|---|---|---|
| clap kid_song (thr 1.99e-4 / 9.75e-5 / 9.75e-5) | 0.001662 | 0.002178 (+31 %) | 0.001361 | 0.001872 (+38 %) | 0.000799 | **0.001208 (+51 %)** |
| clap c2st (0.67 / 0.61 / 0.61) | 0.931 | 0.953 | 0.984 | 0.990 | 0.926 | 0.953 |
| clap coverage (> 0.467 / 0.493 / 0.493) | 0.174 | 0.138 | 0.085 | 0.043 | 0.221 | 0.158 (-29 %) |
| clap density | 4.17 | 3.38 | 0.160 | 0.072 | 2.46 | 1.38 |
| clap fad | 0.477 | 0.555 | 0.376 | 0.452 | 0.272 | 0.337 (+24 %) |
| clap knn_real_fraction | 0.0029 | 0.0019 | 0.0017 | 0.0036 | 0.0066 | 0.0043 |
| clap novelty_max_cos (< 0.985) | 0.937 | 0.941 | 0.933 | 0.930 | 0.951 | 0.949 |
| mert kid_song (thr 8.5e-4 / 7.2e-4 / 7.2e-4) | 0.005126 | 0.005055 (-1 %) | 0.006435 | 0.005736 (-11 %) | 0.005829 | **0.005381 (-8 %)** |
| mert c2st (0.55 / 0.57 / 0.57) | 0.975 | 0.977 | 0.931 | 0.931 | 0.926 | 0.927 |
| mert coverage (> 0.555 / 0.603 / 0.603) | 0.137 | 0.119 | 0.285 | 0.290 | 0.314 | 0.316 |
| mert density | 0.382 | 0.208 | 1.258 | 1.017 | 1.457 | 1.143 |
| mert fad | 7.67 | 7.46 | 9.66 | 9.20 | 9.40 | 9.03 (-4 %) |
| mert knn_real_fraction | 0.0102 | 0.0204 | 0.0066 | 0.0169 | 0.0078 | 0.0195 |
| mert novelty_max_cos (< 0.995) | 0.982 | 0.982 | 0.981 | 0.981 | 0.982 | 0.981 |

### 6.2 Validators, iteration 04 vs 05 (29 songs, 17 caps; `validators_table.json`)

| validator | cap | iteration 04 | iteration 05 |
|---|---|---|---|
| bass_root_missing_on_change | == 0 per song | 29/29 | 29/29 |
| cadences_realized | == 1.0 (fraction) | 29/29 | 29/29 |
| harmonic_rhythm_realized | == 1.0 (fraction) | 29/29 | 29/29 |
| leading_tone_unresolved_at_cadence | <= 1 per song | 29/29 | 29/29 |
| melodic_leaps_unresolved | <= 2 per 64 bars | 29/29 | 29/29 |
| melody_range_violations | == 0 per song | 29/29 | 29/29 |
| melody_strong_beat_non_chord_tones | <= 0.05 (fraction) | 29/29 | 29/29 |
| parallel_fifths | <= 1 per 64 bars | 29/29 | 29/29 |
| parallel_octaves | <= 1 per 64 bars | 29/29 | 29/29 |
| section_repeat_integrity | True per song | **25/29** | **29/29** |
| section_repeat_skeleton_integrity | True per song | **25/29** | **29/29** |
| section_repeat_surface_differs | True per song | 29/29 | 29/29 |
| swing_in_corpus_iqr | True per song | 29/29 | 29/29 |
| timing_ks_max | <= 0.25 per song | 29/29 | 29/29 |
| unresolved_sevenths | <= 2 per song | 29/29 | 29/29 |
| velocity_std_min | >= 8.0 per song | 29/29 | 29/29 |
| voice_crossing | <= 2 per 64 bars | 29/29 | 29/29 |
| **songs passing every cap** | | **25/29** | **29/29** |

No cap was changed. Replay proofs 29/29 HOLD, seed sweep 72/72 (section 3).

### 6.3 Descriptors, iteration 04 vs 05

Mix descriptors (mean ± sd over 29 songs). Left: the 44.1 kHz stereo mixes vs the full-mix corpus (as in the iteration-04 table);
right: the fair domain (22.05 kHz mono copies vs corpus_accomp), the domain the primary gate is scored in.

| descriptor | it04 (44.1k stereo) | it05 (44.1k stereo) | corpus | it04 fmt | it05 fmt | corpus_accomp |
|---|---|---|---|---|---|---|
| lufs_integrated | -12.34 ± 0.34 | -13.26 ± 1.47 | -11.82 ± 3.29 | -16.19 ± 0.54 | -16.96 ± 1.45 | -17.20 ± 3.34 |
| crest_factor_db | 13.15 ± 0.80 | 14.38 ± 1.68 | 14.06 ± 1.93 | 13.97 ± 0.91 | 14.83 ± 1.44 | 14.97 ± 2.20 |
| spectral_centroid_hz | 2656 ± 253 | 2368 ± 237 | 2421 ± 606 | 2097 ± 357 | 1699 ± 218 | 1674 ± 436 |
| stereo_width_db | -8.36 ± 2.78 | -9.71 ± 3.15 | -12.94 ± 11.8 | - | - | - |
| lr_correlation | 0.71 ± 0.15 | 0.77 ± 0.13 | 0.80 ± 0.17 | - | - | - |
| peak_dbfs | -1.60 ± 0.87 | -1.10 ± 0.44 | -0.03 ± 2.84 | -1.50 ± 0.90 | -1.22 ± 0.44 | -1.07 ± 2.69 |

Discriminant (window-level) descriptors in the fair domain, candidate-minus-reference gap with Cohen's d, and the Spearman rho of
the descriptor with the CLAP LDA score (`descriptors{,_it05}/DISCRIMINANT.md`; the LDA score AUC is 1.000 in both iterations):

| descriptor | gap it04 (d) | gap it05 (d) | rho clap it04 -> it05 |
|---|---|---|---|
| high_ratio_db (> 4 kHz share) | +5.95 dB (0.98) | +1.53 dB (0.27) | +0.45 -> +0.08 |
| zcr | +0.033 (1.03) | +0.007 (0.25) | +0.45 -> +0.22 |
| spectral_rolloff_hz | +945 Hz (0.73) | +12 Hz (0.01) | +0.35 -> +0.06 |
| spectral_centroid_hz | +391 Hz (0.70) | -43 Hz (-0.09) | +0.34 -> +0.04 |
| spectral_bandwidth_hz | +244 Hz (0.55) | -36 Hz (-0.08) | +0.28 -> -0.02 |
| mid_ratio_db (250 Hz - 4 kHz share) | +2.76 dB (0.90) | +1.81 dB (0.57) | +0.33 -> +0.23 |
| dynamic_range_db (p95 - p5 frame RMS) | -7.85 dB (-0.62) | **-6.75 dB (-0.51)** | -0.33 -> **-0.27** (now the top correlate) |
| low_ratio_db (< 250 Hz share) | -0.26 dB (-0.11) | +0.40 dB (+0.17) | -0.35 -> -0.22 |
| spectral_flatness | +0.0016 (0.09) | -0.0088 (-0.52) | +0.18 -> -0.18 |
| rms_db | +2.01 dB (0.49) | +1.40 dB (0.33) | +0.16 -> +0.08 |
| crest_db | -0.96 dB (-0.42) | -0.31 dB (-0.13) | -0.17 -> -0.04 |
| onset_rate_hz | -0.14 Hz (-0.14) | -0.04 Hz (-0.04) | -0.07 -> -0.02 |
| hp_ratio_db | -0.28 dB (-0.07) | -0.10 dB (-0.03) | -0.05 -> -0.02 |

Every spectral-balance correlate of iteration 04 was removed (d 0.7-1.0 -> |d| < 0.3; the mix centroid now sits 25 Hz from the
reference), the LDA score separates the sets exactly as well as before, and the one descriptor still correlated with it is the
within-window dynamic range (-6.75 dB, d -0.51). Spread (CLAP / MERT): 0.434 / 0.498 -> 0.405 / 0.479, CONFIRMED homogeneity both
times. Per-stem (5.2): other 39.1x -> 39.8x, bass 12.9x -> 13.5x, drums 7.3x -> 10.9x.

### 6.4 Ablation attribution (5.3 in one paragraph)

Of the +0.000409 CLAP fmt kid_song regression, the homogeneity package (kit family drawn first, per-song loudness target, per-song
room) explains 59 % on its own (C), the tilt steer 3 % (A), the density knobs 2 % (B){{D_ATTR}}. The package also lowered the CLAP
spread ratio it was meant to raise (0.442 without it -> 0.405 with it). The one change that did what it promised at the descriptor
level — the tilt steer, which put the master's > 4 kHz share, centroid, rolloff and zcr on the reference — moved the embedding gate by
3 %, and over-darkened the drums while doing it (5.2). MERT, which does not see the kit / loudness / room draws the same way, improved
slightly on every reference (kid -1 / -11 / -8 %, fad -3 / -5 / -4 %).

### 6.5 What moved, what got worse

Better: validators 25/29 -> 29/29 on every cap (realised-skeleton fix, section 3); fair-domain mix descriptors on the reference
(LUFS gap 1.0 -> 0.24 LU, crest gap 1.0 -> 0.14 dB, centroid gap +424 -> +25 Hz); the > 4 kHz / zcr / rolloff / centroid
discriminants gone (d ~1 -> < 0.3); 10 distinct kits with families 15 neutral / 8 rock / 6 jazz (was 24/29 jazz); candidate LUFS sd
0.35 -> 1.47 LU; MERT kid_song -8 % (fmt), fad -4 %, kNN-real 0.0078 -> 0.0195, coverage flat; CLAP novelty unchanged (PASS).

Worse (honestly): **CLAP fmt kid_song +51 %** (0.000799 -> 0.001208, 8.2x -> 12.4x the floor), c2st 0.926 -> 0.953, coverage 0.221
-> 0.158 (-29 %), fad +24 %, density 2.46 -> 1.38, kNN-real 0.0066 -> 0.0043; the same direction on both unmatched CLAP runs (kid +31 %
/ +38 %, coverage -21 % / -50 %). Per-stem **drums 7.3x -> 10.9x** (GM sf2 kits on 11/29 songs where iteration 04 had multi-layer AVL
kits on 25; full-strength shelf pushes the kit from +4.5 dB too bright to -1.3 dB too dark, centroid -1078 Hz, zcr d -1.33); "other"
> 4 kHz share +4.3 -> +6.7 dB (bright strummed comp guitar on 70 % of songs) with onset rate 2.59 -> 2.72 Hz only (target >= 3.2, real
4.13); CLAP spread ratio 0.434 -> 0.405 and MERT 0.498 -> 0.479 (the pre-registered >= 0.55 was missed in the wrong direction); MERT
coverage vs corpus 0.137 -> 0.119. Unchanged: "other" 39x, bass 13x, dynamic range -7 dB, LDA AUC 1.000, every gate FLAG.

### 6.6 Remaining gaps, ranked, with effect sizes — the brief for iteration 06

Effect sizes are each gap's own pre-registered statistic (as in the diagnostics doc §5); the order weighs size against how cleanly
the gap is attributable to something the generator controls. Three iterations of renderer / mix knobs (04: patches, width, harmony
debias; 05: tilt, kits, loudness, room, density probabilities) have moved the CLAP gate by -14 % and +51 % and the MERT gate by
+2 % and -8 %, while the per-stem "other" ratio sat at 39x throughout and the oracle says the mix chain PASSes. What is left is
composition and arrangement.

| rank | gap | effect size (iteration 05) | what I would change in iteration 06 |
|---|---|---|---|
| 1 | **"other" layer (keys + comp + melody + pad)**: too sparse, too sustained, no low-mid body, too loud and too bright | kid 39.8x its floor; c2st 0.988; coverage 0.022; onset rate 2.72 vs 4.13 Hz (d -1.22); H/P +5.4 dB (d +1.40); low share -4.8 dB (d -0.91); RMS +4.4 dB (d +0.76); > 4 kHz +6.7 dB (d +0.84) | Composer-side density with a TARGET, not a probability: give each song an "other"-layer onset-rate target drawn from the corpus distribution (median ~4 Hz) and have the comping / keys / guitar parts fill to it (short chord stabs, left-hand patterns, 8th-note strums on the comping instrument, counter-lines on the pad); add a low-register layer (keys left hand an octave down, or the pad doubling the bass register at -12 dB) for the -4.8 dB low share; trim the "other" group gain ~4 dB in gain staging; darker comp patches (nylon / muted electric instead of bright strummed steel). Pre-register: onset rate >= 3.5 Hz, H/P within 2 dB, low share within 2 dB, "other" ratio < 25x. |
| 2 | **homogeneity**: generated songs twice as alike as real songs | CLAP spread ratio 0.405 (rule 0.60; was 0.434), MERT 0.479; between/within variance 0.86 vs 1.43; 5th-percentile candidate pair above the median real pair | Vary what a music embedding sees: the ARRANGEMENT. Per-song ensemble templates that actually differ (guitar-led with no keys, keys-only ballad, pad-less rhythm-section songs, songs with no melody instrument in the verse), 3-4 comping styles (stabs / sustained / arpeggiated / strummed) drawn per song, section-level texture changes (intro / bridge with half the layers). Pre-register: CLAP spread ratio >= 0.50, and check it on the ablation copies before the full score. |
| 3 | **within-window dynamic range** -6.75 dB: 10-s windows are wall-to-wall | d -0.51; rho -0.27 (the top discriminant left on both backbones); crest gap only -0.14 dB (so it is not the limiter) | Arrangement dynamics, not mastering: drum drop-outs in intros / last A sections / bridges, a 2-bar break before the final chorus, half-time or ride-only sections, phrase-level velocity arcs (+/- 12) on keys and comp, a 2-4 dB section-gain map in the mix. Pre-register: dynamic range gap within 3 dB. |
| 4 | **drums**: too tonal, now too dark, one-shots in silence | kid 10.9x (was 7.3x); H/P +6.3 dB (d +1.01); centroid -1078 Hz (d -1.22); zcr d -1.33; dynamic range +17 dB | Take the drums OUT of the master tilt shelf (steer the "other" bus, which carried the excess, and leave the drum bus at the kit's own balance); prefer multi-layer AVL kits within the drawn family (quality factor in the ranking, GM sf2 only as fallback); a short room / bleed layer on the drum bus (early reflections + low-level broadband noise gated to the hits) for the H/P and dynamic-range gaps. |
| 5 | **bass**: clean stem vs Demucs-separated stem | kid 13.5x; mid share +10.8 dB (d +1.57); dynamic range +50 dB (d +1.21) | Not acted on again: the signature (digital silence between notes, no broadband tail) is the reference's separation artefact; if anything, a cheap control (add -50 dBFS pink noise + 2 dB of 1-3 kHz string noise to the candidate bass group and re-score the stem) to measure how much of the 13.5x is bleed. |
| 6 | mix chain | oracle PASS (kid 0.57x / 0.30x the floor; CLAP c2st 0.642 vs gate 0.61) | Nothing. |

What I would NOT change again: the master tilt steer strength / cap (3 % of the kid, over-darkens the drums); the ensemble / comping
PROBABILITIES as a density lever (2 %; onset rate +0.13 Hz); the per-song loudness target, room size and reverb return (cost 59 % of the
regression together with the kit draw and lowered the spread); the kit-family prior / softmax temperature as a diversity lever (CLAP does
not reward kit variety between songs); anything in the mix chain, which the oracle cleared; and the scoring protocol (fair mode stays
the primary gate, both backbones, gates untouched). Keep: the realised-skeleton fix, format matching, the per-stem and spread diagnostics
as the pre-registered checks for every iteration-06 change (run them on the 22.05 kHz copies BEFORE the full scorecard, as the ablations
did: 29 renders + CLAP in ~30 min).
