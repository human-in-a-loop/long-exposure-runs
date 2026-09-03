<!--
created: 2026-09-02T00:00:00Z
cycle: 54
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey
fork: bdd7bb47f1b5
clone: 0
-->

# RC10 Branch A — Drums + Bass Transcription Re-Survey — Frozen Rubric (v1)

**Cycle:** c54 fanout branch A (clone-0)
**Parent milestone:** `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`
**Scope:** drums + bass only (rhythm section fix priority per operator UPDATE #3).
**Doc-first:** this rubric is committed BEFORE any script under
`scripts/recreate_v2/rc10_drums_bass/`. Three-way `rubric_hash` byte-equality
chain: doc SHA-256 == `data/rc10_drums_bass_impl/rubric_hash.txt` ==
`data/rc10_drums_bass_impl/verdict.json.rubric_hash`.

## D1 — Baseline anchors (READ-ONLY)

- **Drums stem input:** `data/recreate_v2/baseline/<sha16>/rc9_6stem/drums.wav` per focus song.
- **Bass stem input:** `data/recreate_v2/baseline/<sha16>/rc9_6stem/bass.wav`.
- **Chosen section:** `focus_set_v2.chosen_section.{t_start_s, t_end_s}` per song.
- **c53 clone-2 tempo estimate:** `data/rc5_impl/<sha16>/rc5_tempo_estimate.json.corrected_estimate` (drives D4 beat-grid snap).
- **c49 v1 rubric anchor:** `data/recreate_v2/rubric_hash.txt` = `958ade38…3fe58b9d`.
- **c50 v2 rubric anchor:** `data/recreate_v2/rubric_hash_v2.txt` = `0e11f704…debe1f`.
- **c51 Branch B substantive MIDIs:** `data/rc2_rc3_impl/<sha16>/merged.midi` (READ-ONLY informational baseline).
- **Do-not-touch invariant:** `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b`.

## D2 — Content metrics per stem (gate)

**Drums PASS iff:**
- (a) onset F1 ≥ 0.60 vs baseline onset times (tolerance ±50 ms), where the baseline reference is `librosa.onset.onset_detect` on the baseline drums stem (chosen section) with the same params.
- (b) note count within [0.5×, 2×] of baseline onset count.

**Bass PASS iff:**
- (a) framewise-f0 agreement (pyin on both stems, hop=512, fmin=C1=32.7Hz, fmax=C4=261.6Hz; % of jointly-voiced frames within 1 semitone) ≥ 0.60.
- (b) low-band (< 250 Hz) energy correlation (Pearson on hop=512 RMS envelopes) ≥ 0.5.
- (c) median MIDI pitch of transcribed notes < 55.
- (d) bass-note count within [0.5×, 2×] of pyin-voiced-segment count baseline.

Secondary (recorded, not gating): texture panel (mel-L1 dB, spectral centroid RMSE, RMS-envelope RMSE) — best-effort via `scripts.texture.panel` if available.

## D3 — Candidate matrix

- **Drums:** [D3a] `librosa.onset.onset_detect(y, sr, hop_length=512, backtrack=True, units='time')` + per-onset band-energy classifier (kick 50–120 Hz, snare 200–500 Hz + noise 4–8 kHz, hihat 6–12 kHz) → GM channel 10 notes {36, 38, 42}. Single candidate. Basic-pitch on drums remains RC2 anti-pattern (locked).
- **Bass:** [D3a] basic-pitch 0.4.0 defaults (quarantined venv); [D3b] basic-pitch tuned (`onset_threshold=0.3, frame_threshold=0.2, minimum_note_length=100, minimum_frequency=30, maximum_frequency=500, multiple_pitch_bends=False`); [D3c] `librosa.pyin` monophonic with voicing-confidence segmentation (voiced_probability > 0.5 and voiced_flag True; note pitch = median semitone-rounded f0 per segment; velocity = per-segment RMS-derived).

## D4 — Post-processing pipeline (mandatory; measured with AND without)

1. **Beat-grid snap:** snap every onset to `rc5_tempo_estimate.corrected_estimate` beat grid within ±50 ms; out-of-tolerance onsets kept unsnapped.
2. **Glitch drop:** drop notes with duration < 32nd note (= `60/bpm/8`).
3. **Envelope velocity:** derive `velocity` from local RMS envelope of stem in note-onset window (hop=512, window=1 beat), normalize per-stem to MIDI [1, 127].
4. **Range filter:** drop bass pitches outside MIDI [24, 71] (~30–500 Hz); drums kept only on {36, 38, 42}.

## D5 — Winner selection per stem type

Highest composite score on the majority (≥3/5) of focus songs:
- Drums composite = onset F1.
- Bass composite = framewise-f0 agreement.

Ties broken by SHA-256 of candidate name. Winner recorded in
`data/rc10_drums_bass_impl/winner_per_stem.json`.

## D6 — Per-stem A/B artifacts

For every candidate iteration, write LUFS-I -23 normalized
`original.wav` (baseline stem, chosen section) and `rendered.wav`
(fluidsynth of candidate MIDI: drums on channel 10 with standard
drum kit; bass on GM program 33 electric bass) under
`data/recreate_v2/ab_pairs/<sha16>/{drums,bass}/iter_<N>/`. First-class
artifacts; NOT gate-blocking on their own.

## D7 — Byte-determinism × 2

Two fresh `tempfile.mkdtemp()` runs under env pins:
`PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1`.

SHA-256 equality asserted across runs on all per-song per-candidate
JSON + MIDI outputs. WAV outputs subject to fluidsynth determinism
(same env + same input yields byte-equal output).

## D8 — Verdict enum (frozen)

- `RC10_DRUMS_BASS_LANDS` if BOTH stems pass D2 gate on ≥3/5 focus songs.
- `RC10_DRUMS_BASS_PARTIAL` if EXACTLY 1 stem passes on ≥3/5 focus songs.
- `RC10_DRUMS_BASS_FAILS` if 0 stems pass on ≥3/5 focus songs.

Honest capability-ceiling report acceptable if either stem fails: surface WHICH metric fails, by HOW MUCH, and best candidate's raw output per song.

## Success criteria checklist (§3 of brief)

- (a) rubric doc mtime < any script under `scripts/recreate_v2/rc10_drums_bass/`.
- (b) three-way rubric_hash byte-equality chain.
- (c) per-song per-candidate content-metric TSV `data/rc10_drums_bass_impl/scorecard.tsv`.
- (d) byte-determinism × 2 across all outputs (D7).
- (e) anchor preservation ≥25 SHAs pre==post byte-exact.
- (f) A/B pairs under `data/recreate_v2/ab_pairs/<sha16>/{drums,bass}/iter_1/` with LUFS-I normalization.
- (g) `winner_per_stem.json` pins candidate name + composite score per stem.
- (h) NO PRNG (AST-grep), `/usr/bin/python3` interpreter guard, c48 env-var flags default OFF.
- (i) ≥15/15 tests green in `tests/test_rc10_drums_bass.py`.
- (j) 0-ERROR `promise_check` post-emission.
- (k) `docs/rc10_drums_bass_report.md` shipped with per-song per-stem scorecard, PASS/FAIL per D2 metric, winner-per-stem summary, honest capability-ceiling declaration if applicable.
