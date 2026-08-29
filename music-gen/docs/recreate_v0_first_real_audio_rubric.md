---
created: 2026-08-29T08:00:00Z
cycle: 37
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-1/first-real-audio
fork: 675abd086911
clone: 0
status: FROZEN
---

# M-RECREATE-1/first-real-audio — Frozen 3-Verdict Rubric

**Frozen: 2026-08-29T08:00:00Z. Any change requires a new sub-milestone under a new fork.**

This rubric is committed BEFORE any Python file under `scripts/recreate_v0/`
lands on disk. The mtime + git-log fallback ordering test asserts this at
run time. The verdict JSON's `rubric_hash` field must equal the SHA-256 of
this file (as recorded in `data/recreate_v0/rubric_hash.txt`).

## Scope

First end-to-end recreation of a rated song from
`corpus/ratings/{4,5,6,7}/*.mp3` through the eight-stage pipeline:

  1. `M-INGEST-1/chunker`            (read-only import)
  2. `M-CLASS-1` tagger sidecar      (non-factor isolation preserved)
  3. `M-SEP-1/htdemucs-baseline`     (read-only import)
  4. `M-TRANS-1/basic-pitch`         (quarantined venv, read-only)
  5. `M-SCORE-1/bridge-api` `merge_stems_to_score`   (read-only)
  6. Fluidsynth bare-MIDI render     (SF2 SHA `74594e8f…1cb0`)
  7. Cycle-9 DawDreamer effects-layered chain        (read-only, NOT modified)
  8. `M-TEX-1/panel` measurement on TWO comparisons:
     (original, bare) AND (original, effects-layered)

Song selection: SHA-256 tiebreak over the corpus manifest (see §Song-Selection).

## Verdicts (mutually exclusive)

### RECREATION_LANDS

All eight stages complete without error AND the effects-layered panel is
materially closer to the original than the bare panel on at least the
`mel_l1_db` metric:

  * (a) All 8 stages reach `status=ok` in `per_stage/pipeline_run.json`.
  * (b) Both panel TSVs contain 8 finite keys per row (per M-TEX-1/panel
    contract) — no `None` on numeric keys.
  * (c) `panel_original_vs_effects.mel_l1_db < panel_original_vs_bare.mel_l1_db`
    by ≥ 0.5 dB (effects layer measurably narrows the spectral gap).
  * (d) Byte-determinism × 2 holds on the deterministic-stage anchor set
    (bare_midi.wav, effects.wav, merged.musicxml, merged.midi,
    panel_original_vs_bare.tsv, panel_original_vs_effects.tsv).
  * (e) Provenance chain reconstructs from any intermediate stage forward
    (each per-stage artifact carries the input SHA and stage_version).

### RECREATION_PARTIAL

Exactly one of the following holds and every other criterion above passes:

  * (P1) Effects-vs-bare `mel_l1_db` delta is < 0.5 dB but positive (effects
    layer applied but not measurably closer to original).
  * (P2) One numeric panel key returns null-with-reason on either comparison
    while the other seven remain finite (documented-degradation case).
  * (P3) Byte-determinism × 2 holds on the two WAV rendering stages
    (bare_midi.wav, effects.wav) but drifts on the intermediate MusicXML
    or panel TSV via an isolated, root-caused non-determinism source
    (documented in the report; not fabricated).

### RECREATION_FAILS

Any of the following:

  * (F1) Any of stages 1–7 raises an unhandled exception, exits non-zero,
    or produces silent audio (peak amplitude < 1e-5) — the failed stage
    is named in `verdict.json.failed_stage`.
  * (F2) Byte-determinism × 2 fails on `bare_midi.wav` OR `effects.wav`
    without a documented root cause.
  * (F3) Both panel comparisons fail to produce 8 finite keys.
  * (F4) The chosen song's audio decode fails (corrupted MP3).

**RECREATION_FAILS with a named failed stage is a first-class close per
brief.** No silent-failure permitted.

## Song-Selection Rule (SHA-256 Tiebreak)

Deterministic and PRNG-free:

  1. Enumerate every `corpus/ratings/{4,5,6,7}/*.mp3` file (sorted by
     relative path for canonical order).
  2. For each candidate, compute the SHA-256 of the file's bytes.
  3. Choose the file whose SHA-256 hex is lexicographically smallest.
  4. Record the choice + hex + relative path + rating band in
     `data/recreate_v0/chosen_song.json`.

Rationale: content-derived, reproducible across cycles, no PRNG, no
sort-key dependence on filesystem inode order.

## Duration Bound (Honesty Note)

Real songs in the corpus range from ~2 min to ~7 min. htdemucs and
basic-pitch on CPU are quadratic in duration and this pipeline's wall
time on an unbounded song may exceed the cycle budget.

The pipeline MAY trim the chosen song's decoded audio to the FIRST 30 s
starting at t=0 (before the chunker stage) if wall-time-guard triggers.
The trim decision is captured in `chosen_song.json.trim_seconds` and
prominently surfaced in the report — the recreation verdict then applies
to that 30 s excerpt, not the full song. A trim is not a stage failure;
it IS a first-class disclosure that shrinks the scope of the verdict.

## Model-Ear Score Caveat (Preview Untrained)

The M-EAR-1 model score MUST carry the `preview_untrained_ear=true`
sentinel and cite the cycle-36 `M-EAR-1/real-label-training-v0` verdict
of EAR_v0_INSUFFICIENT. It is a preview number, not a calibrated
prediction, and cannot influence the recreation verdict above.

## Anchor Preservation

The following files must be SHA-identical before and after this cycle's
work (`data/recreate_v0/anchor_preservation.json` records both hashes):

  * `scripts/ingest/chunker.py`
  * `scripts/classifier/tagger.py`
  * `scripts/classifier/sidecar_nonfactor.py`
  * `scripts/separation/apply_htdemucs.py` (or the primary htdemucs entry)
  * `scripts/transcribe/basic_pitch_driver.py` (or the primary basic-pitch entry)
  * `scripts/score/bridge.py`
  * `scripts/tex/render_bare_midi.py`
  * `scripts/tex/render_effects_layered.py`
  * `scripts/texture/panel.py`
  * `scripts/ear/features.py`
  * `scripts/ear/model.py`

Any mtime change is an anti-invariant. The cycle-9 DawDreamer chain in
particular is a locked anchor per the brief — it MUST NOT be modified.

## Frozen Sentinel

This rubric was frozen by clone-0 of fork 675abd086911 at
2026-08-29T08:00:00Z. The verdict recorded by
`scripts/recreate_v0/run_all.py` embeds this file's SHA-256 verbatim.
