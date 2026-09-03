<!--
created: 2026-09-02T00:00:00Z
cycle: 53
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano
fork: bdd7bb47f1b5
clone: clone-1
-->
# RC10 Branch B Rubric — Guitar + Piano Transcription Re-Survey on Real htdemucs 6-Stem Outputs

**Pre-registered:** 2026-09-02 (c53 clone-1). This document's SHA-256
is the rubric hash pinned by:

- `data/rc10_impl/guitar_piano/rubric_hash.txt` — byte-equal to `sha256(this file)`
- `data/rc10_impl/guitar_piano/verdict.json.rubric_hash` — byte-equal to the same

**Three-way byte-equality chain** (doc SHA == rubric_hash.txt == verdict.rubric_hash) is
gate (b) of §3.

**Peer sub-milestone under `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`,**
which is itself a new c29 peer under `M-RECREATE-2/accurate-small-set-v2`.

## §1 Scope

Guitar + Piano only. Drums+bass live under clone-0. Other+vocals live under clone-2.
This clone is disjoint from both; no cross-clone writes.

- Inputs (READ-ONLY):
  - `data/recreate_v2/baseline/<sha16>/rc9_6stem/other_guitar.wav`
  - `data/recreate_v2/baseline/<sha16>/rc9_6stem/other_piano.wav`
  - `data/rc5_impl/<sha16>/rc5_tempo_estimate.json` (BPM anchor)
  - `data/recreate_v2/focus_set_v2.json` (5 focus songs with `chosen_section`)
- Focus songs: 5 (Chicken Grease band 6 + 4 others). SHA-16 IDs enumerated in the
  focus_set_v2 JSON; verdict scoring is over exactly this set.

## §2 D-block (frozen)

### D1 Baseline anchors (READ-ONLY)

Per-song baseline stems are loudness-normalized on `chosen_section` per
`focus_set_v2.json`. No modification.

### D2 Content metrics per stem

Both metrics computed on the `chosen_section` t-window of both original and rendered stem.

- **Beat-synchronous chroma-CQT cosine per beat, mean and median.**
  Chroma-CQT computed on both signals (mono mixdown, sr = 22050, hop = 512).
  Beat frames come from `librosa.beat.beat_track(..., start_bpm=rc5.corrected_estimate,
  tightness=100, hop_length=512)` on the ORIGINAL mixdown of the section (identical
  grid for both signals so aggregation is comparable). Chroma frames are
  aggregated to per-beat vectors via `librosa.util.sync(..., aggregate=np.mean)`.
  Cosine per beat = dot / (||a||·||b|| + 1e-12); NaN beats (zero-norm) dropped.
- **Note-density ratio.** `notes_rendered_per_beat / notes_original_per_beat`,
  where `notes_original` = `librosa.onset.onset_detect(..., hop_length=512,
  sr=22050, backtrack=False)` on the original stem. Pass band **[0.5, 2.0]**.

### D3 Candidate matrix per stem

Three candidates per stem type:

| ID  | Guitar recipe                                                                                        | Piano recipe                                                       |
|-----|------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| C1  | basic-pitch defaults                                                                                 | basic-pitch defaults                                               |
| C2  | basic-pitch tuned: `onset_threshold=0.3, frame_threshold=0.2, minimum_note_length=100`, 80–1300 Hz clip | basic-pitch tuned: `minimum_note_length=80`, 27.5–4186 Hz          |
| C3  | Beat-sync chroma-CQT chord-track → 24-triad Krumhansl template → sustained triads on beat grid via pretty_midi (GM 25 Acoustic Guitar) | Same as guitar but rendered on GM 0 Acoustic Grand Piano |

Frequency-window clip on C2 is post-transcription (drop notes with pitch outside
freq window; count logged). C3 is a "correct chord track" fallback per operator
UPDATE #4 — for polyphonic failures, correct comp beats wrong note soup.

### D4 Post-processing (mandatory, applied to every candidate; measured with and without)

1. **Snap onsets** to rc5 beat grid within ±50 ms tolerance.
2. **Drop 32nd-notes at BPM.** Drop notes with `duration_s < 60/(bpm × 8)`.
3. **Derive velocity from stem RMS.** Local RMS envelope in each note's time
   window (hop 512), normalized to [1, 127] via linear map from
   [rms.min, rms.max].
4. **Range-filter.** Drop pitches outside D3's per-stem freq window; log count.

Both "with-D4" and "without-D4" scored for every candidate.

### D5 Winner selection per stem

Adopt the candidate with the highest `chroma_cosine_mean` averaged over the 5
focus songs (or per-song basis — see below), preferring the **with-D4** flavor
of that candidate. Per-song winner: highest chroma_cosine_mean on that song.
Winner-per-stem-type: candidate that wins on ≥3/5 focus songs; ties broken by
`SHA-256(candidate_name.encode('utf-8'))` first byte (deterministic; no PRNG).

### D6 A/B artifacts

Per (song, stem, iter=0-of-winner), loudness-normalized (LUFS-I −23 via
`pyloudnorm`) `original.wav` + `rendered.wav` under
`data/recreate_v2/ab_pairs/<sha16>/{guitar,piano}/iter_0/`.

### D7 Verdict

Per-stem PASS ⇔ `chroma_cosine_mean ≥ 0.60` AND
`note_density_ratio ∈ [0.5, 2.0]` on ≥3/5 focus songs (using the winner
candidate + D4-flavor for each song).

- `RC10_GUITAR_PIANO_LANDS` — both stems pass on ≥3/5 focus songs.
- `RC10_GUITAR_PIANO_PARTIAL` — exactly one stem passes.
- `RC10_GUITAR_PIANO_FAILS` — neither passes. Honest capability-ceiling report
  names failing metric, by how much, and best-candidate output surfaced.

## §3 Falsifiable success criteria

- (a) Rubric mtime STRICTLY LESS THAN every file mtime under
  `scripts/recreate_v2/rc10_guitar_piano/`.
- (b) Three-way rubric_hash byte-equality: doc SHA == `rubric_hash.txt` content
  == `verdict.json.rubric_hash`.
- (c) 3 candidates × 2 stems × 5 songs = 30 candidate outputs; each with-D4 +
  without-D4 = 60 rows in the scorecard. Every content metric finite.
- (d) Byte-determinism × 2: two runs into fresh `tempfile.mkdtemp()` dirs under
  `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`,
  `OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=OMP_NUM_THREADS=1`. All candidate MIDIs
  + scorecard.tsv + winner_per_stem.json + verdict.json + per-song A/B WAV pairs
  SHA-256 equal. Recorded in `data/rc10_impl/guitar_piano/byte_determinism.json`
  with `n_mismatch == 0`.
- (e) Anchor preservation ≥25 SHAs pre==post byte-exact: c49 v1 rubric
  (`958ade38…3fe58b9d`), c50 v2 rubric (`0e11f704…debe1f`), c51 Branch A/B/C
  verdicts, c52 render_stem.py (`214372d9…5b2b`), c53 clone-2 rc5 estimates × 5,
  10 baseline guitar+piano WAVs, `focus_set_v2.json`.
- (f) `winner_per_stem.json` pins candidate name + chroma_cosine_mean +
  note_density_ratio per (song, stem).
- (g) Scorecard TSV `data/rc10_impl/guitar_piano/scorecard.tsv` with columns
  `song_id, stem, candidate, chroma_cosine_mean, chroma_cosine_median,
  note_density_ratio, post_processing, pass_fail`; markdown sidecar
  `docs/rc10_guitar_piano_scorecard.md`.
- (h) A/B pairs loudness-normalized within ±0.5 LU of −23 LUFS-I (verified via
  `pyloudnorm.Meter.integrated_loudness`).
- (i) NO PRNG (AST scan for `random.*`, `numpy.random.*` seedless calls);
  `/usr/bin/python3` shebang + `sys.executable` assertion in every script; c48
  env flags default OFF via `os.environ.setdefault`; no `sidecar_nonfactor`
  import; `scripts/palette_render/render_stem.py` NOT modified.
- (j) ≥15 tests green in `tests/test_rc10_guitar_piano.py`.
- (k) `promise_check` 0-ERROR.

## §4 Ledger emission plan (6 substantive unsuffixed + 2 housekeeping + 1 egress-probe under `-clone-1`)

Substantive (unsuffixed per c32):
1. `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano/pre-registration`
2. `.../candidate-matrix-implemented`
3. `.../candidate-matrix-scored`
4. `.../winner-selected`
5. `.../ab-pairs-emitted`
6. `.../verdict-emitted`

Housekeeping (`-clone-1` suffix per c33):
7. `_archive/cycle-53-rc10-guitar-piano-scratch-clone-1`
8. `_infra/adopt-cycle53-rc10-guitar-piano-tests-clone-1`

Egress-probe (path A per c49):
9. `M-INGEST-1/egress-probe-cycle53-clone-1`

## §5 Non-goals (explicit)

- Do NOT modify c51 A/B/C verdicts.
- Do NOT re-run htdemucs.
- Do NOT touch `scripts/palette_render/render_stem.py`.
- Do NOT attempt VST3 rendering (c31 STILL_GAP + c35 palette-v2 locked).
- Do NOT emit `M-EAR-1/*` or `M-GEN-1/*` events.
- Do NOT attempt corpus acquisition (egress blocked 17+ cycles).
- Do NOT re-open c11/c22/c23/c25/c35 anti-patterns.
- Do NOT retro-timestamp.

## §6 Anti-pattern watch

None triggered. C3 chord-track is a NEW pattern operator explicitly named in
UPDATE #4. Distinct from c25 (that was ear-model feature choice under synthetic
labels; this is transcription-representation choice under real-stem content
metrics).
