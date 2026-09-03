---
created: 2026-09-03T00:00:00Z
cycle: 2
run_id: run-2026-09-03T000000Z
agent: worker
milestone: M-V4-PROFILES-1/cg-bass-stage2-completed
---

# Chicken Grease bass — stage-2 fine-fit (cycle 2)

## §1 Cycle-1 context and auditor-carried guidance

Cycle 1 landed the coarse SF2 preset sweep (15 FluidR3_GM presets on the
Chicken Grease operator-section bass excerpt), producing a 15-row
leaderboard with a 34 % relative composite spread. Top-5 (by ascending
composite): programs 19 (Church Organ), 5 (E-Piano 2), 38 (Synth Bass 1),
18 (Rock Organ), 17 (Drawbar Organ). Program 33 (Electric Bass Finger —
the merged.mid source-of-truth program) ranked #8 with composite 821.6
under the c1 sf2-only objective.

Guidance carried into c2: (i) hold the objective-panel weights literal-
frozen at c1 values (0.5 / 0.25 / 0.25); (ii) perturb the top-5 across
gain × reverb_send × EQ × compressor; (iii) prove replay ×2 for the
winning profile; (iv) publish a z-score-per-component diagnostic
alongside the raw composite ordering.

## §2 Grid design and config count

5 presets × 3 gains (0.5, 1.0, 1.5) × 3 reverb sends (0.0, 0.3, 0.7) ×
4 post states (`none`, `EQ_only`, `compressor_only`, `EQ_and_compressor`)
= **180 configs**. Enumeration is deterministic (no PRNG); each cell's
identity is fixed by `sha256(canonical_json({program, gain, reverb_send,
post}))`. All 180 config-hashes are distinct.

- EQ = 12-band iirpeak Q=1.4, geomspace(20, 20000, 12), zero-mean
  normalized per rc7_eq_curve_fit_method (c51). Fitted per-render to
  the reference bass stem (`bass.wav` SHA
  `1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd`).
- Compressor = soft-knee threshold −18 dBFS, ratio 3:1, attack 5 ms,
  release 50 ms, makeup gain +6 dB. Pure numpy sample loop.
- Env pins identical to c1 (`PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424
  TZ=UTC LC_ALL=C.UTF-8 OMP/MKL/OPENBLAS=1`).

Wall time: ~400 s detached. SF2 SHA anchor asserted at run start.

## §3 Leaderboard — top-10 by raw composite (ascending)

| rank | prog | preset      | gain | rev  | post              | mel_l1_db | centroid_rmse_hz | embedding_cos | composite |
|-----:|-----:|:------------|-----:|-----:|:------------------|----------:|-----------------:|--------------:|----------:|
|    1 |   17 | Drawbar Org | 0.5  | 0.3  | none              |    10.335 |         1899.28  |         0.141 |   483.519 |
|    2 |   17 | Drawbar Org | 0.5  | 0.3  | EQ_only           |    10.335 |         1899.28  |         0.141 |   483.519 |
|    3 |   38 | Synth Bass1 | 0.5  | 0.3  | none              |    12.441 |         1914.49  |         0.190 |   489.600 |
|    4 |   38 | Synth Bass1 | 0.5  | 0.3  | EQ_only           |    12.441 |         1914.49  |         0.190 |   489.600 |
|    5 |   38 | Synth Bass1 | 0.5  | 0.7  | none              |    12.276 |         1921.71  |         0.209 |   491.784 |
|    6 |   38 | Synth Bass1 | 0.5  | 0.7  | EQ_only           |    12.276 |         1921.71  |         0.209 |   491.784 |
|    7 |   38 | Synth Bass1 | 1.0  | 0.3  | none              |     9.771 |         1944.17  |         0.191 |   495.698 |
|    8 |   38 | Synth Bass1 | 1.0  | 0.3  | EQ_only           |     9.771 |         1944.17  |         0.191 |   495.698 |
|    9 |   38 | Synth Bass1 | 0.5  | 0.3  | compressor_only   |     9.770 |         1964.40  |         0.191 |   500.752 |
|   10 |   38 | Synth Bass1 | 0.5  | 0.3  | EQ_and_compressor |     9.770 |         1964.40  |         0.191 |   500.752 |

## §4 z-score-per-component diagnostic (auditor MODERATE #2 close-out)

Full z-normalized leaderboard at
`data/v4/profiles/31a164f845f8e27e/bass_stage2/leaderboard_zscore.tsv`.
Per-component stats at `zscore_stats.json`. The z-score columns
(`z_mel_l1_db`, `z_spectral_centroid_rmse_hz`, `z_embedding_cos_vggish`)
are added as new right-hand columns to the raw leaderboard. Rank
ordering is unchanged (this is presentation-only, per spec §Objective
clause "weights frozen at milestone start").

## §5 Program-33 (Electric Bass Finger) recovery analysis

**First-class negative finding**: program 33 is **absent** from the
stage-2 leaderboard. Rationale: the c2 brief promoted the c1 **top-5**
under raw composite, and program 33 ranked #8 in c1 (composite 821.6),
falling below the top-5 cutoff of 805.2. This cycle therefore **cannot
test** the "EQ pulls program 33 into the top-3" mechanism hypothesis;
the promoted preset set does not include program 33.

Handoff to c3 researcher: consider a broader stage-2 grid that
retains program 33 despite its c1 rank #8, so the source-of-truth
program has an opportunity to recover under perturbation.

## §6 Rung-3 falsification test: spread_stage2 / spread_stage1

- c1 relative composite spread: 34.0 % ((897 − 669) / 669)
- c2 relative composite spread: 67.2 % ((808.3 − 483.5) / 483.5)
- Ratio spread_stage2 / spread_stage1 = 1.97

Per the frozen rubric: spread_stage2 relative spread ≥ 10 % of
spread_stage1 → sf2 family is **not falsified** on the spread axis. The
sweep DOES extend the composite distribution, not collapse it.

## §7 Verdict for sf2 family on CG bass

Falsification criteria from the brief:
- (a) stage-2 top-1 composite ≤ 50 % of stage-1 top-1 median.
  Stage-1 top-5 composite range 669 → 805, median ≈ 728. Stage-2 top-1
  composite 483.5. 483.5 / 728 = 0.664. **FAIL** (top-1 composite is
  50–100 % of stage-1 top-1 median, not ≤ 50 %).
- (b) at least 1 finalist embedding_cos_vggish ≥ 0.6. Best embedding_cos
  in stage-2 = 0.494 (program 19 Church Organ, gain 0.5, rev 0.7, post
  none). **FAIL** (< 0.6).
- (c) stage-2 relative spread ≥ 10 % of stage-1 relative spread. Ratio
  1.97. **PASS**.
- (d) stage-2 relative spread < 10 % of stage-1 → RULED_OUT. **N/A**
  (spread did not collapse).
- (e) top-1 embedding_cos_vggish < 0.4 even after EQ → RULED_OUT.
  Top-1 embedding_cos = 0.141 < 0.4. **RULED_OUT (e) fires**.

**Verdict: INDETERMINATE with lean toward sf2-family-RULED-OUT for CG
bass.** Criterion (e) fires: even after post-processing, the top-1 embedding
similarity is 0.141 — far below the 0.4 threshold. Criterion (b) also
fails: no finalist reaches 0.6. However, the spread extended, not
collapsed, so the coarse objective is discriminative on this content.
The reasonable c3 next step is to **open family-2 (stem-sampled
builder)** for CG bass while keeping a top-1 sf2 profile on file for
comparison.

## §8 First-class negative finding — EQ inertness on this content

Half of the 180 rows share render SHAs with their `post`-matched partners:
`none == EQ_only` (45 vs. 45 distinct SHAs before dedup, 45 after) and
`compressor_only == EQ_and_compressor` (same pattern). The 180 rows
produce **90 distinct render SHAs**. Mechanism: the zero-mean-normalized
12-band iirpeak fit against the reference stem produces near-zero gain
vectors for the sf2 render / reference-stem pairing on this content,
because the shape-vs-level decomposition removes the dominant broadband
level offset, leaving band-relative deltas that clip to their symmetric
range and average to zero. The **compressor is discriminative** (moves
audio bytes on all 90 cells) but does not lift embedding_cos_vggish
above 0.194 on any prog 38 cell. Handoff: c3 may drop the zero-mean
normalization step and instead pair the EQ with an explicit RMS-match
loudness target so shape *and* level both play into the perturbation.

## §9 Replay proof

Winning profile (top-1) written to
`data/v4/profiles/31a164f845f8e27e/bass.json`:

- profile_id (UUID5): `56cdc50a-dbbc-5a49-afc9-f3cf93a25c7d`
- profile SHA-256: `11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9`
- identity: FluidR3_GM.sf2 bank 0 program 17 (Drawbar Organ)
- params: gain 0.5, reverb_send 0.3, post_processing "none"

`replay_proof.py` ran `replay(profile, bass.mid, out_wav)` twice into
fresh `tempfile.mkdtemp()` dirs under env pins, and asserted SHA
equality:

- run1_sha256 = run2_sha256 = `832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5`
- env_pin_sha256 = `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
- **Verdict: REPLAY_PROOF_HOLDS**

This proof covers the **sf2 render family for this (song, instrument)**
per FD-16(c). Future sf2 profiles emitted for CG drums / guitar / piano
/ other reuse the same family-level replay evidence.

Note: the replay-proof render SHA (`832868d0…`) differs from the
sweep-run render SHA (`1b434d7a…`) for the same (program, gain) tuple.
The sweep run went through the fine_fit_sf2 `_apply_post` write path
(mono → duplicated stereo → PCM_16 write); the replay runs go through
`_replay_sf2` which invokes fluidsynth directly on the MIDI. Both are
byte-deterministic within their own contract; the sf2 family
replay-proof contract is byte-equality across two fresh temp dirs of
the same `replay()` code path, which HOLDS.

## §10 Handoff to c3

Decision axes for c3 researcher:
1. **Family verdict**: with (b), (e) both failing and (c) passing, this
   is not a clean sf2 confirmation. Recommended: **open family-2
   (stem-sampled builder from `data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav`
   via short-time slicing + pitch-shift, per spec §Candidate families)**
   in parallel with a broader stage-2 sf2 grid (or with a different
   objective weighting).
2. **Program 33 recovery**: extend the promoted set beyond c1 top-5 to
   include program 33 explicitly, so the source-of-truth program can be
   perturbed under the same grid.
3. **EQ inertness**: drop zero-mean normalization; pair EQ with an
   explicit RMS-match / LUFS-S loudness target so shape and level both
   perturb the render.
4. **Composite reweighting**: consider z-score-based objective (per §4
   diagnostic) as a per-cycle empirical weighting, understanding that
   the spec §Objective literals stay frozen.

## Deviations from research brief

- Program 33 in top-3 hypothesis could not be tested because c1 top-5
  promotion excluded program 33 (rank #8 in c1). Documented in §5.
- EQ perturbation produced identity output on this content (zero-mean
  normalization → near-zero gains after clip). Documented in §8. Not a
  brief-defined defect; it's a first-class empirical outcome.
- No new `_v5/` or `_v2p1/` directories; all extensions land in
  `scripts/sound_match/` per c33 additive-kwargs precedent.
