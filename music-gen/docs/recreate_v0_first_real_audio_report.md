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

Per-stage summary (populated from `pipeline_run.json`):

```
See: data/recreate_v0/per_stage/pipeline_run.json
```

Concrete per-stage wall times and output SHAs land in that JSON. The
final verdict emitter is responsible for surfacing the failed_stage (if
any) prominently at the top of §7.

## 5. Panel Measurements

Two comparisons per `M-TEX-1/panel` contract (8 keys per row, no
aggregate):

  * `data/recreate_v0/panel_original_vs_bare.tsv`
  * `data/recreate_v0/panel_original_vs_effects.tsv`

The panel returns `{mel_l1_db, spectral_centroid_rmse_hz, rms_env_rmse,
lufs_m_rmse_lu, embedding_cosine_distance, embedding_rung, sr_hz,
n_samples_compared}`. Concrete numbers land in the TSVs; the verdict's
mel-delta gate reads from those files.

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

See `data/recreate_v0/verdict.json` for the machine-parseable form:

```
verdict          : ${verdict}
reason           : ${reason}
failed_stage     : ${failed_stage or "None"}
mel_delta_dB     : ${mel_delta} (bare - effects; ≥0.5 dB gates LANDS)
det_x2_wavs      : ${determinism.all_deterministic_anchors_equal}
anchors_unchanged: ${anchors_unchanged}
rubric_hash      : 78c61c5dbf61492ff802d7a0810b4c449b2732b658daffffa84c7b4203c2dab9
```

Templated fields are substituted by the ledger emitter after run_all.py
completes; the ${...} form is left visible in the on-disk template so
that a stalled run leaves an obvious "this template still has
placeholders" marker rather than fabricating numbers.

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

**Trim to 30 s** is the primary deviation and is a first-class disclosure
per the rubric's Duration Bound clause — not a stage failure. If the
pipeline reached FAIL on any stage, the failed_stage is named in
`verdict.json.failed_stage` and this section documents which stage
failed and why (concrete stack-trace tail lives in the stage's `error`
+ `note` fields inside `pipeline_run.json`).

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

**If verdict = RECREATION_LANDS:** propose a batch extension
(N-song variant) on the same rubric to test cross-song generalization.

**If verdict = RECREATION_PARTIAL:** name the specific PARTIAL clause
(P1 / P2 / P3), propose one targeted fix, and pre-register whether that
fix would move the verdict to LANDS.

**If verdict = RECREATION_FAILS:** the failed_stage is named. Cycle 38's
scoped brief should either (a) sink work into fixing that stage on real
audio, or (b) redefine the recreation contract to bypass the failing
stage with a documented fallback.

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
