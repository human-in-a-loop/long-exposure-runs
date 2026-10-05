# v6 Phase 5 — iteration 05 diagnostics: localising the distribution gap before touching the generator

Date: 2026-10-05. Branch `claude/music-gen-planning-ghzop7`. Candidate set = iteration 04 (`data/v6/gen/iteration_04_corpus`,
29 songs, seed 3). Fair reference = `corpus_accomp` (drums + bass + other, Demucs, 22.05 kHz mono). Every rule below was
written into the diagnostic code (`scripts/v6/diag_common.py`, `diag_embed_v6.py`, `diag_stems_v6.py`) BEFORE the number it
judges was computed; the measured values follow each rule.

## 0. Fair scoring mode (`scorecard.py --match-reference-format`)

Iteration 04 (doc 8.4) showed that ~40 % of the CLAP distance to `corpus_accomp` was the reference's own format (22.05 kHz
mono). `scripts/v6/scorecard_format.py` now resamples / down-mixes every candidate to the reference's modal (sample rate,
channels) before embedding — soxr_hq, channel mean, 16-bit PCM copies cached under `data/v6/scorecard/format_cache/<source
sha16>_<sr>hz_<ch>ch.wav`, the transformed file's own sha keying the embedding cache — adds `_fmt` to the run name and writes
`candidate_format` into scorecard.json. From now on `*_vs_corpus_accomp_fmt` is the primary gate on both backbones; the
unmatched runs are kept for continuity.

Iteration 04 vs `corpus_accomp`, unmatched vs format-matched (gates `references.corpus_accomp`):

| backbone / metric | unmatched | format-matched (`_fmt`) | threshold | verdict (fmt) |
|---|---|---|---|---|
| clap kid_song | 0.001361 | 0.000799 (-41 %) | 9.75e-05 (8.2x) | FLAG |
| clap c2st | 0.984 | 0.926 | 0.61 | FLAG |
| clap coverage | 0.085 | 0.221 | > 0.4925 | FLAG |
| clap density / fad / kNN-real | 0.16 / 0.376 / 0.0017 | 2.46 / 0.271 / 0.0066 | floor 2.86 / 0.133 / 0.53 | INFO |
| mert kid_song | 0.006435 | 0.005829 (-9 %) | 7.17e-04 (8.1x) | FLAG |
| mert c2st | 0.931 | 0.926 | 0.57 | FLAG |
| mert coverage | 0.285 | 0.314 | > 0.6029 | FLAG |
| mert density / fad / kNN-real | 1.258 / 9.66 / 0.0066 | 1.46 / 9.40 / 0.0078 | floor 2.56 / 7.78 / - | INFO |
| novelty_max_cos | PASS / PASS | 0.951 / 0.982 PASS | 0.985 / 0.995 | PASS |

Format matching removes 41 % of the CLAP kid and 9 % of the MERT kid; both backbones stay FLAG on every gate at ~8x the
floor. Mix descriptors in the matched domain (both 22.05 kHz mono): candidates -16.19 ± 0.55 LUFS vs reference -17.2 ± 3.4;
crest 13.97 ± 0.92 vs 14.97 ± 2.24 dB; centroid 2097 ± 363 vs 1674 ± 444 Hz; peak -1.5 ± 0.9 vs -1.07 ± 2.7 dBFS. Two things
stand out before any embedding: the candidates are still 420 Hz brighter, and their song-to-song SPREAD on every descriptor is
3-6x smaller than the reference's (LUFS sd 0.55 vs 3.4, crest sd 0.9 vs 2.2, peak sd 0.9 vs 2.7).

## 1. Spread / homogeneity (2b) — `diag_embed_v6.py spread`

Song-mean embedding = unit-norm mean of the unit-normed windows. Pre-registered rule: homogeneity is a confirmed gap when the
candidate between-song spread (1 - mean pairwise cosine of song means) is < 0.60 x the reference's.

| backbone | cand pairwise cos mean [p5, p95] | ref pairwise cos mean [p5, p95] | spread cand | spread ref | ratio | between/within var cand | ref | cand -> nearest ref cos | verdict |
|---|---|---|---|---|---|---|---|---|---|
| clap | 0.907 [0.819, 0.976] | 0.785 [0.569, 0.914] | 0.093 | 0.215 | **0.434** | 0.950 | 1.428 | 0.897 | CONFIRMED |
| mert | 0.981 [0.970, 0.992] | 0.962 [0.935, 0.983] | 0.019 | 0.038 | **0.498** | 0.899 | 1.183 | 0.981 | CONFIRMED |

Candidate songs are about twice as alike as real songs are to each other on both backbones (the 5th percentile of candidate
pairs, 0.82, is above the MEDIAN real pair), and the between-song/within-song variance ratio is 0.67-0.76x the reference's:
one generated song's windows vary as much as a real song's, but the songs do not differ from each other. The same statistic
against the full-mix corpus gives 0.48 (clap) / 0.67 (mert): the vocal-free reference is the stricter one, as it should be.
Mechanisms visible in the manifests: 25/29 drum kits are the three AVL bop/brush kits, 12/29 keys are "Upright Piano KW",
every song has keys + melody, 7 distinct ensembles, the mix is normalised to one LUFS target (sd 0.55 LU vs 3.4).

## 2. Discriminant descriptors (2c) — `diag_embed_v6.py descriptors`, format-matched candidates

LDA direction w = (Ledoit-Wolf pooled covariance)^-1 (mu_cand - mu_ref) in embedding space, per-window score x.w (AUC 1.000 on
both backbones: the sets are perfectly separable along w). Spearman rho of each per-window descriptor with the score over all
824 + 1451 windows, with the candidate-minus-reference mean gap and Cohen's d (windows are the embedding windows; the
reference is mono so stereo width is undefined and dropped):

| descriptor | rho clap | rho mert | cand mean | ref mean | gap | Cohen d |
|---|---|---|---|---|---|---|
| high_ratio_db (E > 4 kHz / total) | +0.454 | +0.41 | -16.4 | -22.4 | **+5.95 dB** | 0.98 |
| zcr | +0.454 | +0.42 | 0.099 | 0.066 | +0.033 | 1.03 |
| low_ratio_db (E < 250 Hz / total) | -0.352 | -0.34 | -2.52 | -2.25 | -0.26 dB | -0.11 |
| spectral_rolloff_hz | +0.345 | | 4621 | 3677 | +945 Hz | 0.73 |
| spectral_centroid_hz | +0.339 | | 2122 | 1730 | +391 Hz | 0.70 |
| mid_ratio_db (250 Hz - 4 kHz) | +0.334 | +0.32 | -4.22 | -6.98 | +2.76 dB | 0.90 |
| dynamic_range_db (p95 - p5 frame RMS) | -0.332 | -0.33 | 14.9 | 22.8 | **-7.85 dB** | -0.62 |
| spectral_bandwidth_hz | +0.276 | | 2352 | 2108 | +244 Hz | 0.55 |
| crest_db | -0.167 | | 13.7 | 14.6 | -0.96 dB | -0.42 |
| rms_db | +0.163 | | -15.4 | -17.4 | +2.0 dB | 0.49 |
| onset_rate_hz, hp_ratio_db, spectral_flatness | < 0.19 | | 4.24 / 4.28 / 0.020 | 4.39 / 4.55 / 0.018 | ~0 | < 0.14 |

What the classifier hears, in order: (i) too much high-frequency energy (+6 dB above 4 kHz, zcr +50 %, rolloff +945 Hz,
centroid +391 Hz even after band-limiting both sides to 11 kHz) together with too little low end relative to the whole; (ii) too
little within-window dynamic range (15 vs 23 dB: real 10-s windows contain breaks, decays and phrase dynamics, ours are
wall-to-wall); (iii) too loud / too dense a mid band. Onset rate, harmonic/percussive balance and flatness are NOT what
separates the sets — the rhythmic density and the tonal/noise mix are already in range. (On the unmatched 44.1 kHz stereo
candidates the same table is dominated by bandwidth / centroid / rolloff with d ~ 1.5-2.1, i.e. the format confound.)

## 3. Per-stem distribution scoring (2a) — `diag_stems_v6.py render-stems` + `score-stems`

The 29 iteration-04 songs were re-rendered with `render_song(keep_stems=True)` (new `--keep-stems`; `mix.mix_song(groups=...)`
masters the drums / bass / other groups with the master's own gain and limiter curve, mix byte-identical: 29/29 re-rendered
mixes equal the iteration-04 sha256). Candidate groups (drums = drums + percussion; bass; other = keys + comp_guitar + melody +
pad) were format-matched to the corpus Demucs stems (22.05 kHz mono) and scored with CLAP against `data/v6/stems/<donor>/
<kind>.wav` of all 29 songs. Pre-registered ranking rule: gap ratio = kid_song(candidate group vs real group) / p97.5 of the
real group's own split-half kid_song (10 deterministic splits); the largest ratio is the group farthest from real.

PENDING_STEMS_TABLE

## 4. Mix-chain oracle (2d) — `diag_stems_v6.py oracle`

The REAL stems (drums, bass, other -> the `keys` role) of all 29 songs were resampled to 44.1 kHz stereo and mixed through our
chain (`mix.mix_song`: per-role HPF / gain staging / compression / placement, reverb bus, bus compressor, tilt steer, loudness
to the corpus target, true-peak limiter), then format-matched back to 22.05 kHz mono and compared with `corpus_accomp` under
the split protocol oracle(half A) vs real(half B) on the same 10 deterministic splits as real(A) vs real(B). Pre-registered
verdict: the chain is a gap (FLAG) when the oracle's mean kid_song exceeds the real-vs-real p97.5 over these splits AND its
mean c2st exceeds the corpus_accomp gate (0.61 clap / 0.57 mert).

PENDING_ORACLE_TABLE

## 5. Ranked gaps

PENDING_RANKING
