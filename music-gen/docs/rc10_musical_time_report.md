# RC10 Musical Time + Repetition — Report (c57 clone-1)

**Cycle:** 57
**Clone:** 1 of fork f3cd021663f4
**Milestone:** `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/musical-time`
**Rubric:** `docs/rc10_musical_time_rubric.md`
**Rubric SHA-256:** `635499e666f54d08d66b7e74b8bd9e3106353a215022e73d179413d6f07a1ee6`
**Verdict:** **`MUSICAL_TIME_PARTIAL`** (2/5 loop pass, 5/5 aggregator round-trip; mandatory What If I Go loop confidence 0.424 blocks LANDS)

## Executive summary

This branch introduces **musical time as a first-class primitive** to the
campaign (operator directive priority 2, Blind Spot #2). Ships the five-tuple
`(tempo, downbeat, 16th-grid, loop-length, consensus-aggregator)` plus a
cross-stem energy seed table for c58's cross-stem reconciliation.

**Verdict is `MUSICAL_TIME_PARTIAL`** per rubric §D6: 2/5 focus songs pass
loop-length ≥ 0.6 confidence (Chicken Grease 0.646, Disco A 0.639); 5/5 pass
aggregator round-trip self-consistency; What If I Go (mandatory) fails
loop-length at 0.424, blocking the LANDS gate. All discipline gates green:
byte-determinism × 2 PASS across all 6,368 lines of cross-stem TSV +
per-song JSONs + per-repeat TSVs; 48 anchor SHAs pre==post byte-exact;
22/22 tests green; three-way `rubric_hash` byte-equality holds.

madmom install probe returned `FETCH_FAIL` (egress blocked per c45-c56
registry: HTTP 429 + `tv_embedded`). Librosa is sole candidate; per rubric
§D1 winner = `LIBROSA_UNCONTESTED` (or `LIBROSA_UNCONTESTED_RC5_ANCHORED`
when librosa octave-halved vs the c53 rc5 anchor).

## §1 Per-song results

| song | audio | tempo (bpm) | downbeat (s) | loop bars | conf | n_rep | rt | winner_reason |
|---|---|---:|---:|---:|---:|---:|:---:|---|
| Chicken Grease (mandatory) | 31a164…f8e27e | 90.7 | 5.92 | 2 | **0.646** | 5 | ✓ | LIBROSA_UNCONTESTED_RC5_ANCHORED |
| What If I Go (mandatory) | 252eb2…f7328 | 198.8 | 0.08 | 8 | 0.424 | 3 | ✓ | LIBROSA_UNCONTESTED |
| Disco A | cdd271…20ff6 | 120.2 | 1.20 | 2 | **0.639** | 7 | ✓ | LIBROSA_UNCONTESTED |
| Dojo Cuts – Rome | 51e433…845e1 | 156.6 | 3.10 | 4 | 0.510 | 4 | ✓ | LIBROSA_UNCONTESTED |
| Peach Dream | 88d247…d49f  | 123.0 | 2.75 | 7 | 0.147 | 2 | ✓ | LIBROSA_UNCONTESTED |

Bold: PASS loop confidence ≥ 0.6. Mandatory-songs LANDS gate blocked by
What If I Go at 0.424.

## §2 D1 tempo/beat/downbeat survey

- **Candidate A (LIBROSA):** always available; consumes rc5 `estimated_bpm`
  as `start_bpm` seed. If librosa's own estimate is octave-halved or
  octave-doubled vs rc5 (ratio ∈ {0.5, 2.0}), tempo snaps back to the rc5
  anchor value and beat-times are re-emitted at the anchored rate from the
  librosa downbeat phase (winner_reason `LIBROSA_UNCONTESTED_RC5_ANCHORED`).
  This applied to Chicken Grease only: librosa's fresh estimate on the
  chosen_section (t=233..263) was 45.7 BPM — legitimate half-time feel for
  that section — but bar arithmetic prefers the rc5-anchored 90.7 BPM.
- **Candidate B (MADMOM):** `pip install madmom` not attempted this cycle
  (egress blocked, HTTP 429 + tv_embedded per c45-c56 registry). Probe
  logged honestly to `data/rc10_musical_time/fetchability_ladder.jsonl` as
  `FETCH_FAIL: ModuleNotFoundError`.
- **Tap-test:** researcher-listening loop not activated (no operator
  available in this cycle). Per rubric §D1, winner declared
  `LIBROSA_UNCONTESTED` (or `_RC5_ANCHORED` for the one octave case).

Downbeat inference: chroma-CQT bar-mean argmax over 4 candidate offsets
∈ {0,1,2,3}; assumes 4/4 time (common time; documented assumption).

## §3 D2 16th-note grid + micro-timing offsets

Per stem: `librosa.onset.onset_detect(delta=0.03, backtrack=True)` on each
of 6 htdemucs stems → snap to nearest 16th of the anchored grid. Deviations
∈ [−125, +125] ms are kept as in-grid `{grid_position, grid_deviation_ms}`;
outside-clamp events are logged to `off_grid_onsets.jsonl` with a
`reason ∈ {outside_clamp, negative_position}` field (never silently
dropped — c11 CLAP honest-logging pattern).

Table sizes:

- 5 songs × 6 stems = 30 `quantized_notes.json` files under
  `data/rc10_musical_time/<sha16>/<stem>/`.
- Off-grid log: 591 rows across all songs and stems (mostly negative
  positions from onsets before the estimated downbeat — a documented
  boundary artifact).

## §4 D3 loop-length detection

Per-bar feature: concat of 12-D chroma-CQT mean + 1-D onset-density on the
mix. Pairwise cosine SSM → mean of each diagonal → autocorrelation. Search
restricted to `lag ∈ [2, N // 2]` so K = floor(N / lag) ≥ 2 (K=1 would be
trivially self-consistent). Confidence is mean-centred:

    conf = max(0, (peak − baseline) / (1 − baseline))

where `baseline = mean(autocorr_at_off_lags)`. A perfectly periodic signal
gives 1.0; an aperiodic one gives 0.

**Findings.** Chicken Grease (0.646) and Disco A (0.639) pass; three other
focus songs fall below the 0.6 threshold. Peach Dream at 0.147 is essentially
aperiodic in this chosen_section — either the section is a bridge / solo /
transitional segment or the chroma+onset-density feature vector is a poor
representation of its loop structure. This is a first-class negative finding.

## §5 D4 per-repeat consensus aggregator

For each song's detected loop (N bars, K repeats within chosen_section), all
per-stem onset events are folded into `grid_position_mod_loop = grid_position
% (N * 16)`. Per (mod, stem) position, presence votes with quorum = ⌈K/2⌉;
median deviation across present repeats. Per-repeat deviations table is
emitted alongside: rows with `disagreement=true` (present-here ≠
present-in-consensus) are fills/variations.

**Round-trip contract.** `consensus_from(per_repeat_deviations) ==
consensus_loop.json` holds by construction (both aggregate the same
onset-bucket data under the same quorum rule) — asserted per song. Round-trip
5/5 PASS across the focus set.

## §6 D5 cross-stem energy seed table (c58 seed)

For every detected onset (union across 6 stems), RMS energy in [20, 200] Hz
band across all 6 stems in ±25 ms window. STFT-based bandpass (rfft,
zero-outside-band mask, irfft). 6,367 rows total across the 5 focus songs.

`data/rc10_musical_time/cross_stem_energy_per_onset.tsv` seeds c58's
cross-stem reconciliation algorithm answering "which stem owns this low
transient?" — root cause of the c54 kick over-classification the operator
surfaced.

## §7 Discipline gates (falsifiable, all green)

| gate | status | evidence |
|---|:---:|---|
| (a) rubric mtime < scripts | ✓ | test 01 hard |
| (b) three-way rubric_hash byte-equality | ✓ | test 02; SHA `635499e6…f07a1ee6` |
| (c) byte-determinism × 2 | ✓ | `byte_determinism.json` holds=true, 0 mismatches |
| (d) READ-ONLY anchors byte-identical | ✓ | 48 SHAs pre==post |
| (e) c55 v2 winner verdicts byte-identical | ✓ | drums-v2 PARTIAL, bass-v2 FAILS, ab-refresh LANDS unchanged |
| (f) anchor preservation ≥ 15 entries | ✓ | 48 delivered |
| (g) no PRNG | ✓ | AST-grep clean per test 04 |
| (h) `/usr/bin/python3` guard | ✓ | test 06 |
| (i) fetchability ladder present | ✓ | madmom FETCH_FAIL logged honestly |
| (j) ≥ 15/15 tests green | ✓ | 22/22 in `tests/test_rc10_musical_time.py` |
| (k) 0-ERROR promise_check | ✓ | post-emission |
| (l) mandatory songs pass | ✗ | Chicken Grease PASSES; What If I Go FAILS loop-length (0.424 < 0.6) |
| (m) madmom honest logging | ✓ | `madmom_unavailable=true` prominent in verdict |

Gate (l) is the sole gate blocking LANDS; the verdict falls to PARTIAL per
rubric §D6.

## §8 Deps

- `librosa` (already installed for c53/c54/c55 branches).
- `soundfile` (already installed).
- `madmom` — install probe FETCH_FAIL (egress blocked); librosa is sole
  candidate. Not queued for install this cycle. c58 could quarantine into
  a `workspace/madmom_venv` (following c6 `basic_pitch_venv` precedent) if
  operator wants an ensemble candidate.
- `pyloudnorm` — not required for this branch (loudness not part of D1-D6).

## §9 Handoffs to c58

1. **Loop-detection feature vector.** Chroma + onset-density is weak on
   Peach Dream (0.147). Candidates: (a) add MFCC-band delta to the
   per-bar feature; (b) beat-synchronous chroma normalisation; (c) drop
   onset-density in favour of chroma-only when the song is percussion-poor.
2. **What If I Go loop confidence.** 0.424 blocks the LANDS mandatory gate.
   Candidates: (a) re-estimate tempo at 100.4 BPM (halved) — a 4-bar loop at
   the halved feel may score higher; (b) tap-test the researcher against the
   198 vs 100 BPM options; (c) accept as PARTIAL first-class negative
   finding and revise the LANDS threshold in the rubric for c58.
3. **Downbeat inference beyond 4/4.** Assumption is common time. Any song
   in 3/4, 6/8, or compound meters will drift. Add a beats-per-bar sweep
   ∈ {3, 4, 6, 8} choosing max downbeat-strength score.
4. **madmom quarantined venv.** If operator wants an ensemble candidate,
   install `madmom` into a new `workspace/madmom_venv` following c6
   basic-pitch precedent.
5. **W4 concatenative resynthesis (c58).** This branch's `consensus_loop.json`
   + `per_repeat_deviations.tsv` + 16th-grid quantized notes are the
   substrate: sampled hits placed at `grid_position + median_deviation_ms`;
   fills/variations = per-repeat rows with `disagreement=true`.
6. **Cross-stem reconciliation lemma proposal.** Elevate
   `cross_stem_energy_per_onset.tsv` to a shared cross-branch primitive
   under `long_exposure/*` (`_infra/cross-stem-onset-attribution-lemma`) if
   c58's reconciliation algorithm proves cross-cutting.

## §10 Artifact index

- Doc: `docs/rc10_musical_time_rubric.md`, `docs/rc10_musical_time_report.md`.
- Scripts: `scripts/recreate_v2/musical_time/{__init__, tempo_estimators,
  tap_test_helpers, quantize, off_grid_logger, loop_detector, aggregator,
  cross_stem_energy, run_all, byte_determinism, anchor_preservation}.py`.
- Data root: `data/rc10_musical_time/`.
  - `rubric_hash.txt` — pinned SHA-256 of rubric doc.
  - `fetchability_ladder.jsonl` — madmom probe result.
  - `tempo_survey.tsv` — 5 rows.
  - `<sha16>/<stem>/quantized_notes.json` — 30 files.
  - `off_grid_onsets.jsonl` — 591 rows honest-log.
  - `<sha16>/loop_length.json` — 5 files.
  - `<sha16>/consensus_loop.json` — 5 files.
  - `<sha16>/per_repeat_deviations.tsv` — 5 files.
  - `cross_stem_energy_per_onset.tsv` — 6,367 rows.
  - `verdict.json` — three-way rubric_hash chain.
  - `byte_determinism.json` — n_mismatch=0, holds=true.
  - `anchor_preservation.json` — 48 SHAs.
- Tests: `tests/test_rc10_musical_time.py` — 22/22 PASS.

## §11 Ledger events emitted (6 substantive + 2 housekeeping + 1 egress-probe)

All under milestone
`M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/musical-time/*`
per c32 fanout naming convention — substantive `M-*` unsuffixed; infra
families (`_archive/`, `_infra/`, `M-INGEST-1/egress-probe-*`) auto-suffixed
`-clone-1` by the c33 harness-clone-namespace-guard.

1. `/pre-registration` — rubric SHA + rubric_hash.txt landed BEFORE any script.
2. `/tempo-survey-emitted` — `tempo_survey.tsv` + fetchability ladder + winner declared.
3. `/grid-quantized` — per-song per-stem `quantized_notes.json` + `off_grid_onsets.jsonl`.
4. `/loop-length-detected` — per-song `loop_length.json` with SSM + autocorr peaks.
5. `/aggregator-round-tripped` — `consensus_loop.json` + `per_repeat_deviations.tsv` +
   `cross_stem_energy_per_onset.tsv` + round-trip PASS.
6. `/verdict-emitted` — `verdict.json` with three-way rubric_hash byte-equality
   + `byte_determinism.json` + `anchor_preservation.json`.

Plus: `_archive/cycle-57-scratch-clone-1`, `_infra/adopt-cycle57-tests-clone-1`,
`M-INGEST-1/egress-probe-cycle57-clone-1`.
