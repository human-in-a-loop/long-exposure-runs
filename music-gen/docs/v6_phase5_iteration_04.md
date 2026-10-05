# v6 Phase 5 — first scorecard-driven improvement iteration (iteration 04)

Date: 2026-10-05. Branch `claude/music-gen-planning-ghzop7`. All numbers below were measured in this session; the
scorecard tables at the end are filled in once the `corpus_accomp` embeddings and the iteration-04 render land.

## 1. Fair reference: `corpus_accomp` (drums + bass + other, no vocals)

All 29 reference songs carry vocals while the generator makes instrumentals, so `--reference corpus` confounds
"not real" with "no singer". `scripts/v6/corpus_accompaniment_v6.py build|embed|baseline|gates|all` sums the Demucs
stems `drums + bass + other` per song (mono 22.05 kHz 16-bit; scaled to a 0.999 peak only when the sum clips, gain
recorded) into `data/v6/public/corpus_accomp/<source sha16>.wav` + `manifest.json`, embeds them with CLAP + MERT
(sha-cached), derives the split-half noise floor (20 deterministic splits, `baseline_real_vs_real.run_case` machinery)
into `data/v6/scorecard/baseline_corpus_accomp/` and stores the thresholds under
`gates_v6.json["references"]["corpus_accomp"]`. `scorecard.py --reference corpus_accomp` reads that block
(`gates_for_reference`; the top-level `backbones` block stays the full-mix floor); `scorecard.json["gates"]["key"]`
says which block was used. 5 of 29 accompaniments needed a gain (< 1.0, min 0.82 for "Don't Know What's Normal").

Noise floor and the rescored iteration 03: see section 7.

## 2. Chord-quality debias (parsimony prior in `chords_v6.py`)

Binary L2 templates on leaky stem chroma favour 4–5-note templates (the cosine break-even for a 4- vs 3-note template is
an extra-bin level of 0.464x the triad bins). Pre-registered rule (`params.parsimony` in every chords file): a rich
quality (7 / maj7 / 9 / sus over maj; min7 over min) keeps its cosine only when EVERY extra tone (7th / 9th / 4th bin)
carries chroma energy >= 0.6 x the mean of its base-triad bins (sus additionally needs the 4th louder than the 3rd);
otherwise its similarity is clamped to (best triad of any root at that beat) - 0.01. Calibrated on rendered ground
truth (10 iteration-03 `ab_mix.wav` vs `plan.beat_chords`, 2112 keys-sounding beats): ungated exact 0.411 / root
0.565; margin 0.6 exact 0.383 / root 0.547; margin 1.0 exact 0.277 (rendered voicings always sound the 7th, so this
set only measures the gate's false-negative cost; margins above 0.6 cost accuracy fast, so 0.6 was kept).

Quality histogram over the 29 corpus songs (old chords kept in `data/v6/rules/chords_before_debias/`, old chain in
`data/v6/rules/harmony/chain_before_debias.json`):

| quality | beats before | beats after | segments before | segments after |
|---|---|---|---|---|
| maj | 825 | 1019 | 157 | 185 |
| min | 894 | 979 | 172 | 185 |
| 7 | 293 | 340 | 72 | 86 |
| min7 | 1814 | 1862 | 273 | 268 |
| maj7 | 3647 | 3579 | 679 | 654 |
| 9 | 700 | 334 | 83 | 40 |
| sus | 2861 | 2812 | 398 | 409 |
| N | 1998 | 2107 | 125 | 133 |

The gate changed the un-smoothed argmax on 33.5 % of beats (per song 17.5–59.9 %) and gated 36 % of (beat, state)
cells, but Viterbi + the leaky chroma keep maj7 / sus dominant: on real stems the 7th bin usually does carry >= 0.6x
the triad mean (median extra/triad ratio on chosen rich beats 0.92, IQR 0.47–2.06). maj/min did NOT come to dominate;
only the `9` quality collapsed (-52 % segments) and maj/min grew +18 % / +8 %. Chain (26/29 songs used, same 3
exclusions): 69 -> 71 states, NON_DEGENERATE both, max stationary N 0.122 -> 0.131; segment counts by quality
`{7: 71->85, 9: 80->38, maj: 151->179, maj7: 641->616, min: 154->166, min7: 270->265, sus: 386->396}`. LOO
cross-entropy (bits/chord): beat 1.538 -> 1.540 (uniform 6.109 -> 6.150, gap 4.570 -> 4.609), segment 5.444 -> 5.464
(gap 0.664 -> 0.686) — i.e. unchanged within noise; the rebuilt chain is what iteration 04 composed from.

## 3. Seventh-resolution semantics (the CAPS definition)

`validators.CAPS["unresolved_sevenths"]` (cap <= 2 per song, unchanged): at a chord change, a keys voice on the chord
7th is resolved when (i) RETAINED — its pitch still sounds in the next voicing, in the same or another voice (a common
tone, hence a chord tone of the next chord) — or (ii) it moves DOWN BY STEP (1–2 semitones); otherwise unresolved.
Chord unchanged is exempt, and so is a 7th released into a rest (an `N` slot between the two voiced chords). ONE
function, `voicing.unresolved_sevenths`, is used by the DP transition cost, the validator and the new stage-1 mask:
`harmony.resolvable_matrix` zeroes every chain change whose 7th has no retention / step-down target in the next chord
(`voicing.seventh_resolvable`; 39 of the chain's transitions, mean row mass removed 0.198; one row `3:min7 -> 10:maj7`
kept because it would empty) so the harmony never forces the voicing DP into an unresolved 7th. 9 chords gained a
rootless 3-5-7-9 voicing alternative (the bass carries the root) so a preceding 7th that is the 9 chord's 5th can be
retained; `voice_sequence_cyclic` tries up to 8 pinned first voicings (was 4).

Results: seed sweep (72 fixture cases) 72/72 all caps pass after repair (before-repair column 25/72, was 45/72: the
constructive layer now produces more parallels that the repair pass removes — repairs 66 -> 117; forced violations 0).
29-donor `--no-render` pass (seed 2, same donors as iteration 03): unresolved_sevenths pass 9/29 -> 28/29
(remaining: song 1 x3 — a self-adjacent `A A` label whose Imaj7 -> IVmaj7 junction has 36 feasible voicing pairs but
the cyclic search did not reach one; songs 12, 16 x1), parallel_fifths 29 -> 28, section_repeat_integrity 27 -> 26.

## 4. Patch-selection realism (`render_v6/select.py`, pool unchanged)

Priors recorded in `patch_plan.json["priors"]` and per candidate (`library_prior`, `cosine`, `score`):
(a) GM sf2 banks (fluidr3_gm, freepats_gm, generaluser_gs, musescore_general) x 0.3 in every role whenever the role's
candidate set has an sfz option; on the CLAP path the prior enters the softmax as `score = cosine + T ln(prior)`, so a
GM patch must lead by > T ln(1/0.3) = 0.06 cosine (T = 0.05) to win; (b) melody pool = electric_piano, piano,
electric_guitar, acoustic_guitar (borrowed from the comp_guitar pool), brass; synth leads / synth brass only for a
synth-leaning band (BAND_PRIOR lead >= 0.5, i.e. band 4); calliope / square / fifths leads never; (c) keys: sampled
pianos / e-pianos (Salamander, Upright KW, FM Piano) x 2.0. Test: `tests/test_v6_render_select.py::test_06`.

Iteration 04 picks for the focus songs (all band 5):

| song | role | iteration 03 | iteration 04 (cosine, prior) |
|---|---|---|---|
| WIG | melody | Synth Calliope Lead | FM Piano 2 (DX7-style) (0.575, 1.0) — family lead -> electric_piano |
| WIG | keys | FreePats Electric Piano 1 (GM) | FM Piano 1 (DX7-style) (0.570, 2.0) |
| WIG | bass | FluidR3 Acoustic Bass (GM) | FluidR3 Acoustic Bass (GM) (0.402, 0.3) — still the most similar by > 0.06 |
| WIG | comp_guitar | GeneralUser Nylon Guitar | (no comp_guitar drawn this seed) |
| Rome | melody | Upright Piano KW | EGuitar FSBS jazz tone (0.634, 1.0) |
| Rome | keys | FluidR3 Bright Yamaha Grand (GM) | Upright Piano KW (0.471, 2.0) |
| Rome | bass | GeneralUser Finger Bass (GM) | Finger Bass YR sfz (0.466, 1.0) |
| Rome | comp_guitar / pad | EGuitar FSBS jazz / — | Spanish Classical Guitar / Synth Pad Choir |
| Disco A | melody | EGuitar FSBS jazz tone | EGuitar FSBS clean bridge (0.397, 1.0) |
| Disco A | keys | Drawbar Organ Emulation | Upright Piano KW (0.411, 2.0) |
| Disco A | bass | FreePats Electric Bass 1 (GM) | GeneralUser Finger Bass (GM) (0.619, 0.3) |
| Disco A | drums | GeneralUser Power kit (GM) | AVL Blonde Bop (0.651, 1.0) |

## 5. Mix-level gaps (`render_v6/mix.py`)

Iteration-03 descriptors vs the corpus: L/R correlation 0.973 vs 0.80, stereo width -18.7 vs -12.9 dB, crest 12.6 vs
14.1 dB, peak -2.0 vs -0.03 dBFS, LUFS -12.2 vs -11.8, centroid 2563 vs 2421 Hz. Changes (all deterministic, recorded
in `mix_manifest.json["phase5_targets"]`): keys keep their sampled stereo image (side x 1.25; a mono keys stem gets a
9 ms Haas spread at -6 dB) and are panned +20 %; comping guitar gets an 11 ms L/R (Haas) delay at -25 %; pad side
x 1.6 (was 1.3); the reverb return (-9 dB, was -10) carries six early-reflection taps with different L/R delays
(7.1/13.3/23.9 vs 9.7/17.9/29.3 ms, -12 dB) for a decorrelated early field; bus compressor eased from -10 dB / 2:1
to -6 dB / 1.5:1; true-peak ceiling -1.0 -> -0.5 dBTP. On the synthetic test stems: width -15.3 -> -9.1 dB, L/R
correlation 0.943 -> 0.785, crest 11.6 -> 12.1 dB, peak -2.2 -> -1.7 dBFS at the same LUFS. Iteration-04 descriptors
vs the corpus: section 7.

## 6. Render-path memory retention (found and fixed during the iteration-04 run)

The compose+render process grew ~0.5 GB per song and was OOM-killed (cgroup) at 7.9 GB anon RSS after song 14
(iteration 03 had died at 13 GB). Compose alone is flat (198 -> 199 -> 199 MB over 3 songs). tracemalloc between
render songs 2 and 3 pointed at ONE line: `scripts/v6/gen/render.py:44`, `struct.pack("<" + "h" * n, *samples)` in
`write_wav_int16` — a unique ~14-million-character format string per file, and the `struct` module caches every distinct
compiled format (up to 100 entries), so each rendered mix (song + replay-proof render, 4 objects a song) stayed alive
for the life of the process (+108 MiB traced per song, 336 MiB after 3). Fix: `ai.astype("<i2").tobytes()`, proven
byte-identical to the struct form (so replay proofs and iteration-03 hashes are unaffected). Test
`tests/test_v6_render_memory.py`: 3 fixture songs composed + rendered in one process, RSS 411 -> 374 -> 374 MB,
growth song 2 -> 3 = 0 MB (< 150 MB cap) + the byte-identity test. Iteration 04 was relaunched with `--skip-existing`
(14 songs reused). Not the culprit: CLAP (no libtorch mapped in the process: all donor timbre vectors were disk-cache
hits), module-level memos (none in the gen modules), pedalboard objects.

## 7. Scorecards

(filled in below once the embeddings and the render land)
