# RC10 Musical Time + Repetition — Rubric (c57 clone-1)

**Cycle:** 57
**Clone:** 1 (of fork f3cd021663f4)
**Parent milestone:** `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`
**Peer siblings:** `drums-v2-*` (c55), `bass-v2/*` (c55), `ab-pairs-refresh/*` (c55), `guitar-piano/*` (c53), `other-vocals/*` (c53), `drums-bass-*` (c54)
**Rubric SHA anchor:** pinned into `data/rc10_musical_time/rubric_hash.txt`; three-way byte-equality (doc SHA == rubric_hash.txt content == `verdict.json.rubric_hash`).
**Preface.** This rubric introduces musical time as a first-class primitive to
the campaign (operator directive priority 2, 2026-09-02 architectural
directive). Blind Spot #2: notes are absolute seconds, no tempo map / beat
grid / bars; syncopation cannot be represented; the 1–2 bar loop repeated
~15× per 30 s window is never exploited. This branch ships (tempo, beat,
downbeat, 16th-grid, loop-length, consensus-aggregator, cross-stem-energy)
as a shared five-tuple + one seed table.

## §D1 Tempo/beat/downbeat estimator survey

- **Candidate A (LIBROSA)** — always available.
  `librosa.beat.beat_track(y=mix_mono, sr=44100, units='time',
  start_bpm=<c53 rc5 anchor per song>)` for tempo + beat. Downbeat inferred
  via bar-level chroma-CQT peak (12-D chroma-CQT mean per bar, argmax across
  a candidate offset ∈ [0, beats_per_bar) — the offset whose bar mean
  chroma peak-to-median ratio is highest).
- **Candidate B (MADMOM)** — learned, IF `pip install madmom` succeeds
  offline against the workspace proxy allowlist. `RNNBeatProcessor` +
  `DBNBeatTrackingProcessor` for beat; `RNNDownBeatProcessor` +
  `DBNDownBeatTrackingProcessor` for downbeat.
  Fetch attempt logged to `data/rc10_musical_time/fetchability_ladder.jsonl`
  per c11 CLAP honest-logging precedent (per-rung SHA + failure mode).
- **Tap-test winner selection (per song).** 25 Hz sine click at each
  candidate's estimated beat times, mixed at −10 dB (30 % amplitude) under
  the baseline mix on `chosen_section` (per focus_set_v2). Researcher listens
  through `docs/rc10_musical_time_tap_test_workflow.md` and picks per-song
  winner. If madmom fetch fails, librosa is sole candidate and tap-test is a
  self-consistency check (winner = `LIBROSA_UNCONTESTED`).
  Winner + per-candidate tempo + `downbeat_start_s` recorded in
  `data/rc10_musical_time/tempo_survey.tsv`.

## §D2 16th-note grid + micro-timing offsets

Per song: from winner tempo/beat/downbeat construct

    grid_times = downbeat_start + arange(N_beats * 4) * (60.0 / tempo_bpm / 4)

For each onset from `librosa.onset.onset_detect(delta=0.03, backtrack=True)`
on each baseline stem (per-stem grid, all 6 htdemucs stems), record:

- `grid_position: int` — nearest 16th index
  `int(round((onset_time - downbeat_start) / (60/tempo/4)))`.
- `grid_deviation_ms: float in [-125, +125]` —
  `(onset_time - grid_times[grid_position]) * 1000`.

Deviations outside [−125, +125] ms clamped as `null_off_grid` and logged to
`data/rc10_musical_time/off_grid_onsets.jsonl` (never silently dropped;
c11 honest-logging pattern).

Per-stem quantized notes:
`data/rc10_musical_time/<sha16>/<stem>/quantized_notes.json`
schema `{onset_s, grid_position, grid_deviation_ms, stem}`.

## §D3 Loop-length detection

Bar-level self-similarity per song on chosen_section (READ-ONLY from
`focus_set_v2`):

- Per-bar feature: concat of (12-D chroma-CQT mean over bar) + (1-D
  onset-density on the original mix normalised per bar).
- Pairwise cosine SSM over N ≥ 4 bars (from chosen_section; N target 8).
- Autocorrelate the SSM diagonal (lag ∈ [1, N−1] bars).
- `loop_length_bars` = argmax of autocorr for lag > 1.
- `loop_length_confidence` = autocorr peak height / autocorr at lag=0.

Emit per song at `data/rc10_musical_time/<sha16>/loop_length.json`:
`{loop_length_bars: int, loop_length_confidence: float, ssm_diag_shape:
list, autocorr_peaks: list}`.

## §D4 Per-repeat consensus aggregator

For detected loop of N bars over K repeats within chosen_section
(K = floor(chosen_section_bars / N)):

- Fold all onset events into loop grid:
  `grid_position_mod_loop = grid_position % (N * 16)`.
- Per (grid_position_mod_loop, stem): count `K_present` (bars where an
  onset falls at this position) → `presence = K_present >= ceil(K/2)`.
- Per present (grid_position_mod_loop, stem): median `grid_deviation_ms`
  across K_present repeats.
- Per-repeat deviations row: `{repeat_index, grid_position_mod_loop, stem,
  present_here, deviation_ms_here, present_in_consensus, disagreement}`.
  Rows with `disagreement=true` are fills/variations.

Emit:

- `data/rc10_musical_time/<sha16>/consensus_loop.json` — `{loop_length_bars,
  positions: [{grid_pos_mod, stem, presence, median_deviation_ms}]}`.
- `data/rc10_musical_time/<sha16>/per_repeat_deviations.tsv` — all rows.

**Round-trip contract.** `consensus_loop_from(per_repeat_deviations) ==
consensus_loop.json` (self-consistency test).

## §D5 Cross-stem energy seed table (for c58 cross-stem reconciliation)

For every detected onset (union across all six htdemucs stems), record RMS
energy in the [20, 200] Hz band across all six stems in a ±25 ms window
around the onset time. STFT `n_fft=2048`, `hop=512` on 44.1 kHz.

Table `data/rc10_musical_time/cross_stem_energy_per_onset.tsv` — columns

    song_sha16, onset_time_s, source_stem, energy_drums, energy_bass,
    energy_vocals, energy_guitar, energy_piano, energy_other_residual

(all six energy columns are RMS in the [20, 200] Hz band).

## §D6 Verdict rubric (frozen 3-verdict)

- `MUSICAL_TIME_LANDS`: tempo/beat/downbeat present per all 5 focus songs;
  16th-grid quantization runs on all 5 songs with all deviations
  ∈ [−125, +125] ms (off-grid honestly logged); loop length detected with
  confidence ≥ 0.6 on ≥ 3/5 focus songs; aggregator round-trip
  self-consistency passes on ≥ 3/5 focus songs.
- `MUSICAL_TIME_PARTIAL`: loop detected on 2/5 OR aggregator round-trip
  passes on 2/5; other subsystems land.
- `MUSICAL_TIME_FAILS`: <2/5 loop-length OR <2/5 aggregator OR any focus
  song fails 16th-grid quantization (unable to produce even the off-grid
  table).

**MANDATORY:** Chicken Grease + What If I Go must be in the ≥3/5 that pass
loop-length + aggregator round-trip (per operator surfacing these songs by
name).

## §Falsifiability

- (a) Rubric doc mtime < every `.py` under `scripts/recreate_v2/musical_time/`.
- (b) Three-way `rubric_hash` byte-equality on verdict.json.
- (c) Byte-determinism × 2 across every JSON, TSV, and JSONL under
  `data/rc10_musical_time/` under BLAS pins + `PYTHONHASHSEED=0` +
  `SOURCE_DATE_EPOCH=1756463424` + `TZ=UTC` + `LC_ALL=C.UTF-8`.
- (d) READ-ONLY anchors byte-identical pre==post: c53 clone-2 rc5 tempo
  estimates (`baseline/<sha16>/rc5_tempo_bpm.json`); c50 v2 rubric SHA
  `0e11f704…debe1f`; c49 v1 rubric SHA `958ade38…3fe58b9d`;
  `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b`;
  `data/recreate_v2/focus_set_v2.json`; `data/recreate_v2/baseline/<sha16>/`
  (all baseline 6-stem WAVs + chosen_section metadata).
- (e) c54 + c55 v2 winner/verdict artifacts byte-identical pre==post.
- (f) Anchor preservation snapshot ≥ 15 SHAs (target 25+).
- (g) NO PRNG (AST-grep clean); no `sidecar_nonfactor` import.
- (h) `/usr/bin/python3` guard on every script; c48 env-flags default OFF via
  `os.environ.setdefault`.
- (i) `data/rc10_musical_time/fetchability_ladder.jsonl` present with per-rung
  madmom install probe result (honest FETCH_OK or FETCH_FAIL + reason).
- (j) ≥ 15/15 tests green in `tests/test_rc10_musical_time.py`.
- (k) 0-ERROR promise_check post-emission.
- (l) Chicken Grease + What If I Go pass loop-length ≥ 0.6 + aggregator
  round-trip (mandatory).
- (m) fetchability ladder documents madmom install result HONESTLY — if
  FETCH_FAIL, verdict may still LAND on librosa-only path with a documented
  `madmom_unavailable=true` field.

## §Non-goals

Excluded from this branch (deferred to c58 or later): W4 concatenative
resynthesis; accuracy scoring vs Branch A gold set; any v3/v4 of the c55
classifier family; M-EAR-1/*, M-GEN-1/*, corpus-breadth emissions; any
edit to `scripts/palette_render/render_stem.py` (c33 do-not-touch anchor);
any edit to c50 v2 rubric.
