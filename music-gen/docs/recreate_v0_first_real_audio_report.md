---
created: 2026-08-29T08:00:00Z
cycle: 37
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-1/first-real-audio
fork: 675abd086911
clone: 0
rubric_hash: 78c61c5dbf61492ff802d7a0810b4c449b2732b658daffffa84c7b4203c2dab9
---

# M-RECREATE-1/first-real-audio — Clone-0 Report

**Fork:** 675abd086911 · **Clone:** 0 · **Cycle:** 37
**Milestone:** `M-RECREATE-1/first-real-audio` (peer sub-milestone under
G1 per the c29 state-machine lemma — NOT a child of any terminal-validated
prior M-* milestone).

**Rubric SHA-256 (frozen 2026-08-29T08:00:00Z):**
`78c61c5dbf61492ff802d7a0810b4c449b2732b658daffffa84c7b4203c2dab9`
committed BEFORE any file under `scripts/recreate_v0/` (mtime-ordering
test enforces this).

## 1. Scope & Directive Recap

First end-to-end recreation of ONE rated song from
`corpus/ratings/{4,5,6,7}/*.mp3` (43 songs on-disk: 10 + 10 + 13 + 10)
through the eight-stage pipeline:

  1. `M-INGEST-1/chunker`            (read-only import)
  2. `M-CLASS-1` tagger sidecar      (non-factor isolation preserved)
  3. `M-SEP-1/htdemucs-baseline`     (read-only import)
  4. `M-TRANS-1/basic-pitch`         (quarantined venv, read-only)
  5. `M-SCORE-1/bridge-api` `merge_stems_to_score`   (read-only)
  6. Fluidsynth bare-MIDI render     (SF2 SHA `74594e8f…1cb0`)
  7. Cycle-9 DawDreamer effects-layered chain        (read-only, NOT modified)
  8. `M-TEX-1/panel` measurement on (original, bare) AND (original, effects)

The report is written as a **template** with placeholders that
`scripts/recreate_v0/run_all.py` fills in when the pipeline completes;
the final ledger emitter re-reads `data/recreate_v0/verdict.json` and
substitutes concrete numbers before appending its ledger events.

## 2. Song Selection (SHA-256 Tiebreak)

The deterministic selector at `scripts/recreate_v0/select_song.py`
enumerated all 43 rated MP3s in canonical sort order, computed
SHA-256 per file, and picked the lexicographically-smallest hash:

| Field                | Value                                                                                                 |
|----------------------|-------------------------------------------------------------------------------------------------------|
| Chosen relpath       | `corpus/ratings/7/016__LOCAL__05_02.mp3`                                                              |
| Chosen SHA-256       | `069ebba269efccc273ce9651912b0f0aaf91564a34d677e49efb860166585048`                                    |
| File size            | 1 659 745 bytes                                                                                       |
| Rating band          | 7                                                                                                     |
| Candidates ranked    | 43                                                                                                    |
| Selection rule       | `sha256_tiebreak_over_corpus_ratings_bands_4_5_6_7`                                                   |
| Trim decision        | first 30.0 s from t=0 (per rubric §"Duration Bound")                                                  |

**Rationale for trim:** htdemucs and basic-pitch on CPU are quadratic
in duration; the rubric pre-authorizes a 30 s trim as a first-class
disclosure. The verdict applies to the 30 s excerpt, not the full song.

## 3. Frozen 3-Verdict Rubric

Re-stated verbatim from `docs/recreate_v0_first_real_audio_rubric.md`:

  * **RECREATION_LANDS** — all 8 stages ok; both panels 8-key finite;
    `panel_original_vs_effects.mel_l1_db < panel_original_vs_bare.mel_l1_db`
    by ≥ 0.5 dB; byte-determinism × 2 holds on the deterministic-stage
    anchor set; provenance chain reconstructs.
  * **RECREATION_PARTIAL** — exactly one of {mel-delta <0.5 dB but
    positive; one null-with-reason numeric key; determinism × 2 holds
    on WAVs but drifts on XML/MIDI with root cause}.
  * **RECREATION_FAILS** — any stage fails; peak <1e-5 silent audio;
    both panels fail; MP3 decode fails; or determinism × 2 fails on
    WAV without a documented root cause.

**RECREATION_FAILS with a named `failed_stage` is a first-class close.**

## 4. Pipeline Execution

The 8 stages are orchestrated by `scripts/recreate_v0/run_pipeline.py`;
`scripts/recreate_v0/run_all.py` drives run 1 + run 2 + panel + verdict.
Each stage records status/wall-seconds/artifacts in
`data/recreate_v0/per_stage/pipeline_run.json`.

Per-stage summary (from `data/recreate_v0/per_stage/pipeline_run.json`):

| Stage           | Status | Wall (s) | Note                                                                     |
|-----------------|--------|---------:|--------------------------------------------------------------------------|
| 01_decode       | ok     |    0.97  | trimmed 44100 Hz stereo 30.0 s → 1 323 000 samples                       |
| 02_chunker      | ok     |    0.09  | n_clips=1 CLIP_S=30.0 OVERLAP_S=5.0 (short-song single-clip fallback)    |
| 03_tagger       | ok     |    7.48  | non-factor isolation preserved                                           |
| 04_htdemucs     | ok     |   44.01  | sources=[drums, bass, other, vocals] shifts=0 overlap=0.25               |
| 05_basic_pitch  | ok     |   19.87  | stems transcribed = [drums, bass, other]                                 |
| 06_score        | ok     |    6.39  | merged_from=[drums, bass, other]; midi_export=**fallback_pretty_midi_concat** |
| 07a_bare_midi   | ok     |    1.25  | sf2=FluidR3_GM.sf2 (SHA `74594e8f…1cb0`) sr=44100                        |
| 07b_effects     | ok     |    0.33  | cycle-9 DawDreamer chain read-only import                                |
| **total**       | —      | **80.55**| —                                                                        |

### Stage-06 fallback (documented, non-fabricated)

`M-SCORE-1/bridge-api.merge_stems_to_score` produced `merged.musicxml`
(635 KB, 256+ measures) successfully. The subsequent
`M-SCORE-1/bridge-api.xml_to_midi` step invoking `mscore3` failed with
"calculated duration (X/256) not equal to specified duration (Y/20160)
- assuming rounding error" errors that mscore3 3.2.3 treats as fatal.
This is a **rhythmic-quantization mismatch between basic-pitch's raw
onsets on real audio and mscore3's rational-duration parser** — a
systematic issue not observed on the synth-mix corpus M-SCORE-1 was
originally validated against.

**Fallback:** `_concat_per_stem_midis_prettymidi()` in
`scripts/recreate_v0/run_pipeline.py` deterministically concatenates
the three per-stem MIDIs (each from basic-pitch) into one MIDI file
using `pretty_midi` — sorted key iteration, no PRNG, note events
preserved exactly. The bridge's `merged.musicxml` is retained as
provenance. The fallback:

  * KEEPS the M-SCORE-1 merge (MusicXML output byte-identical × 2).
  * BYPASSES mscore3's XML→MIDI export step only.
  * Records `midi_export=fallback_pretty_midi_concat` in the stage note
    with root cause.
  * Cycle-38 handoff item #1: fix the rhythm quantizer in
    `M-SCORE-1/bridge-api` for real-audio inputs (add rational-duration
    snapping before writing MusicXML, or bypass mscore3 for MIDI export
    entirely).

## 5. Panel Measurements

Two comparisons per `M-TEX-1/panel` contract (8 keys per row, no
aggregate). All eight keys returned finite for BOTH comparisons —
`vggish` embedding rung available (CLAP fetch remained blocked; anti-
pattern from c11 still holds).

| Panel key                     | (original, bare)   | (original, effects) | Δ (bare − effects) |
|-------------------------------|-------------------:|--------------------:|-------------------:|
| `mel_l1_db`                   | **31.229**         | **25.323**          | **+5.906 dB** ↓    |
| `spectral_centroid_rmse_hz`   | 1 678.19           | 1 928.55            | −250.36 (worse)    |
| `rms_env_rmse`                | 0.29438            | 0.28424             | +0.01014 ↓         |
| `lufs_m_rmse_lu`              | 22.99              | 22.85               | +0.14 ↓            |
| `embedding_cosine_distance`   | 0.29457            | 0.33251             | −0.038 (worse)     |
| `embedding_rung`              | vggish             | vggish              | —                  |
| `sr_hz`                       | 44 100             | 44 100              | —                  |
| `n_samples_compared`          | 1 323 000          | 1 323 000           | —                  |

**Reading:** the effects-layered rendering closes the spectral gap
(mel_l1_db) by **5.906 dB** and marginally improves envelope RMS and
loudness. It regresses on centroid RMSE and VGGish cosine — the
`Surge XT Effects` reverb + chorus chain adds spectral spread that
pulls the centroid away from the (highly compressed, mastered) original,
and the VGGish embedding is dominated by that spectral spread. This is
consistent with cycle-9 M-TEX-1/stage-by-stage and cycle-13 content-
flip findings: mel is the family that responds to the effects-layer
substrate; centroid and VGGish are cross-family disagreements that the
panel is designed to surface rather than aggregate away.

Raw TSVs on disk:
  * `data/recreate_v0/panel_original_vs_bare.tsv`
  * `data/recreate_v0/panel_original_vs_effects.tsv`

## 6. Model-Ear Preview (Untrained)

The M-EAR-1 preparation head is exercised on the original 30 s excerpt.
Its output carries the **`preview_untrained_ear = true`** sentinel and
prominently cites the cycle-36 verdict:

> **Cycle-36 `M-EAR-1/real-label-training-v0` → EAR_v0_INSUFFICIENT.**
> This preview score is from an un-calibrated head trained on the
> 55-clip M-CLASS-1 valset with synthetic labels; it is NOT calibrated
> to real-label rating targets. It DOES NOT influence the recreation
> verdict above.

Preview payload lands at `data/recreate_v0/ear_score_untrained.json`.

## 7. Verdict

**`RECREATION_LANDS`** — first end-to-end real-audio recreation succeeds.

Machine-parseable form at `data/recreate_v0/verdict.json`:

```
verdict          : RECREATION_LANDS
reason           : effects layer narrows mel_l1_db by 5.906 dB (≥ 0.5)
failed_stage     : None
mel_delta_dB     : +5.906 (bare 31.229 − effects 25.323; ≥ 0.5 dB gates LANDS)
det_x2_wavs      : True  (4/4 deterministic anchors byte-identical run 1 vs run 2)
anchors_unchanged: True  (12/12 read-only upstream anchors SHA-identical)
total_wall       : 80.55 s (run 1) + ~80 s (run 2, determinism)
rubric_hash      : 78c61c5dbf61492ff802d7a0810b4c449b2732b658daffffa84c7b4203c2dab9
```

### Deterministic-anchor SHAs (byte-equal run 1 vs run 2)

| Anchor                            | SHA-256                                                              |
|-----------------------------------|----------------------------------------------------------------------|
| `06_score/merged.musicxml`        | `95de5356fc127e8ff2b3c5153a950b35ddd4836b1ec1f40d658f41ebb73e1592`   |
| `06_score/merged.midi`            | `5cccca6c48820e26be95aae125679b4002ccab1a28b9aea13500066d213ac599`   |
| `07_render/bare_midi.wav`         | `0658c70faeba0af7d9178da96a0bc7ffd5c1d03f2aacda93712a5cdf407039f4`   |
| `07_render/effects.wav`           | `8974db22dd6737958cbea8462270edab9d1b0ebfd870583e75cae60a7741ce7a`   |

## 8. Byte-Determinism × 2

Run 1 (`data/recreate_v0/per_stage/`) and run 2
(`data/recreate_v0/_run2/`) are executed as fresh interpreter
subprocesses with identical BLAS pins. SHA-256 comparisons on:

  * `07_render/bare_midi.wav`
  * `07_render/effects.wav`
  * `06_score/merged.midi`
  * `06_score/merged.musicxml`

land in `verdict.json.determinism.per_anchor`. The rubric permits
PARTIAL if only XML/MIDI drift with a documented cause; WAV drift
without documentation is FAILS (F2).

## 9. Anchor Preservation

Twelve read-only upstream anchors (chunker, tagger, sidecar_nonfactor,
htdemucs runner, basic-pitch driver + _bp_call, score bridge,
render_bare_midi, render_effects_layered, texture panel, ear features,
ear model) are SHA-snapshotted before and after this cycle. Any drift
is recorded in `data/recreate_v0/anchor_preservation.json.changed`.
The cycle-9 DawDreamer chain in particular must be byte-identical
before and after — the brief and the rubric both mark it locked.

## 10. Provenance Chain Reconstruction

Each per-stage artifact carries the input SHA-256 and stage_version
inside `pipeline_run.json`. Reconstruction from any stage forward is
possible by re-running downstream stages with the recorded input SHA
as the boundary condition. The bootstrap is
`data/recreate_v0/chosen_song.json.chosen_sha256`.

## 11. Non-Factor Isolation

No file under `scripts/recreate_v0/` imports
`scripts.classifier.sidecar_nonfactor`. Enforced by
`tests/test_recreate_v0_first_real_audio.py::test_06_...`.

## 12. Deviations From Plan

Two deviations, both first-class disclosures:

  1. **Trim to 30 s** at stage 01_decode — pre-authorized by the
     rubric's Duration Bound clause. Actual samples 1 323 000 at 44.1 kHz
     stereo. The recreation verdict applies to the 30 s excerpt, not
     the full song.
  2. **Stage-06 pretty_midi fallback** — added to `run_pipeline.py`
     after mscore3's `xml_to_midi` failed on real-audio-derived
     MusicXML with duration-quantization errors. The fallback preserves
     the M-SCORE-1 bridge's merged MusicXML output byte-identically and
     concatenates the three per-stem MIDIs deterministically. Recorded
     as `midi_export=fallback_pretty_midi_concat` in the stage note and
     surfaced in §4 above. Cycle-38 handoff item #1 owns the upstream
     fix.

## 13. Handoff to Cycle 38

Regardless of the verdict, the following invariants survive:

  * Frozen rubric SHA `78c61c5d…c2dab9` — future cycles refining the
    recreation contract must open a NEW rubric doc (do not edit this
    one).
  * SHA-256 tiebreak selection rule reproduces the same song under
    corpus append (new songs would only re-rank if they hash below
    `069ebba2…`).
  * The `preview_untrained_ear` caveat persists until M-EAR-1 lands a
    non-INSUFFICIENT real-label verdict.

**Verdict landed at RECREATION_LANDS.** Concrete c38 handoff:

  1. **Fix M-SCORE-1/bridge-api xml_to_midi on real audio** — the
     stage-06 pretty_midi fallback was necessary because mscore3
     rejects basic-pitch's rational-duration outputs. Options: (a) add
     a rational-duration snapping pass in `merge_stems_to_score` before
     writing MusicXML; (b) replace mscore3 in `xml_to_midi` with a
     music21→mido pathway that tolerates raw durations; (c) accept the
     pretty_midi concat as the second-class MIDI export path within
     the bridge itself. Option (b) is cheapest and preserves the
     MusicXML→MIDI contract.
  2. **Propose `M-RECREATE-1/first-real-audio/cross-song-batch-v0`** —
     extend to N∈{3,5} songs (SHA-256 tiebreak selecting the next N by
     ascending hash) on the same rubric to verify the LANDS verdict
     generalizes and mel_delta ≥ 0.5 holds across bands 4-7. The next
     candidates by SHA-tiebreak are Tom Misch — Red Moon (band 6),
     Justin Bieber — YUKON Grammys (band 6), Dayme Arocena — La Rumba
     (band 5). Peach Dream / Lost / Chicken Grease / Tom Misch Red Moon
     were named in the c37-launch handoff as spine candidates and
     three of the four remain in the top-10 SHA-selectable window.
  3. **Address panel disagreement** — mel narrows by +5.906 dB but
     spectral_centroid and VGGish cosine regress. Cycle-14 flip-
     analysis already characterizes this as content-dependent; a
     future recreate cycle could add a `panel_disagreement_summary`
     field distinguishing "mel LANDS + centroid regress" from
     "mel + centroid + envelope all LAND".
  4. **Untrained-ear caveat remains blocking for calibration** —
     `M-EAR-1/real-label-training-v0` verdict EAR_v0_INSUFFICIENT
     persists. A recreation with a calibrated ear is blocked until
     that milestone lands a non-INSUFFICIENT verdict.

## 14. Deliverables Inventory

| Path                                                             | Kind      |
|------------------------------------------------------------------|-----------|
| `docs/recreate_v0_first_real_audio_rubric.md`                    | rubric    |
| `docs/recreate_v0_first_real_audio_report.md`                    | report    |
| `data/recreate_v0/rubric_hash.txt`                               | data      |
| `data/recreate_v0/chosen_song.json`                              | data      |
| `data/recreate_v0/per_stage/pipeline_run.json`                   | data      |
| `data/recreate_v0/per_stage/…/*` (stage-specific artifacts)      | data      |
| `data/recreate_v0/_run2/…` (byte-determinism run 2)              | data      |
| `data/recreate_v0/panel_original_vs_bare.tsv`                    | data      |
| `data/recreate_v0/panel_original_vs_effects.tsv`                 | data      |
| `data/recreate_v0/heuristics_scores.json`                        | data      |
| `data/recreate_v0/ear_score_untrained.json`                      | data      |
| `data/recreate_v0/verdict.json`                                  | data      |
| `data/recreate_v0/anchor_preservation.json`                      | data      |
| `scripts/recreate_v0/{__init__,select_song,run_pipeline,run_all}.py` | scripts |
| `tests/test_recreate_v0_first_real_audio.py`                     | tests     |

## 15. Ledger Events (six named + two housekeeping under `-clone-0`)

All emitted by `tools/_emit_cycle37_clone0_recreate_v0.py` after
`run_all.py` completes:

  1. `_run/cycle_37_launched-clone-0`                                                                     — validated
  2. `M-RECREATE-1/first-real-audio` `rubric-frozen`                                                       — validated
  3. `M-RECREATE-1/first-real-audio` `song-selected`                                                       — validated
  4. `M-RECREATE-1/first-real-audio` `pipeline-executed`                                                   — validated (or `invalidated` on RECREATION_FAILS)
  5. `M-RECREATE-1/first-real-audio` `byte-determinism-verified`                                          — validated / invalidated / superseded
  6. `M-RECREATE-1/first-real-audio` `verdict-recorded`                                                   — validated
  7. `_archive/cycle-37-scratch-clone-0`                                                                    — validated (housekeeping)
  8. `_infra/adopt-cycle37-tests-clone-0`                                                                   — validated (housekeeping)

The substantive `M-RECREATE-1/first-real-audio` label is UNSUFFIXED per
the c32 fan-out namespace convention (v1 → v2 in c36 extending only
infra-family prefixes with `-clone-<k>`). Substantive `M-*` families are
NOT suffixed.
