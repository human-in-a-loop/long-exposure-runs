# Operator decision log (consolidated)

Chronological record of every operator decision that steers the campaign.
Verbatim guidance text lives in `docs/guidance/`; this file is the index
and current-force summary. Where a later decision supersedes an earlier
one, the earlier entry says so.

## 2026-08-29 — v2 era (pre-pivot; context only)
- Root-cause audits RC1–RC10 and design decisions D1–D4 (peak-section
  auto-pick, hybrid vocals, htdemucs_6s, per-stem loudness+EQ mix match):
  `docs/OPERATOR_recreation_root_cause_audit.md`. D1–D4 remain in force in
  v3/v4; the v2 transcription stack they were attached to is deleted.

## 2026-09-02 — the v3 pivot and its doctrine
1. **Architectural blind spots** (`…architectural_blind_spots.txt`):
   seven structural failures of hand-rolled transcription identified;
   superseded by the pivot below (kept as postmortem).
2. **Pivot to MuScriptor** (prompt + `docs/PIVOT_v3_simplest_robust_pipeline.md`):
   transcription replaced wholesale by a prebuilt learned model;
   hand-rolled DSP transcription permanently banned. Scoped correction the
   same day: every proven stage (rc1/rc4/rc5/rc6/rc7/rc8/rc9/gold set,
   palette, section selection) is kept and reused.
3. **Per-stem transcription** (`…per_stem_transcription.txt`): htdemucs
   isolation feeds MuScriptor per stem with stem-matched instrument
   whitelists; merged on a shared tempo map; full-mix pass is cross-check
   only. IN FORCE.
4. **Canonical MIDI, Option A** (`…midi_canonicalization_option_a.txt`):
   authoritative MIDI is serialized from MuScriptor's deterministic JSON
   events by a pure-function serializer; MuScriptor's own MIDI writer is
   debug-only. IN FORCE.
5. **Stop env probes; build the focus set** (`…stop_env_probes…txt`):
   cross-cycle torch/BLAS drift closed as a non-factor; focus songs built
   without waiting on listening verdicts. IN FORCE (drift detectable via
   env_pin).
6. **Spine LANDS** (`…spine_lands_verdict.txt`): Chicken Grease accepted
   by ear; palette upgrade path unlocked.
7. **Run-to-completion decisions D-A…D-F** (`…run_to_completion_decisions.txt`),
   all IN FORCE:
   - D-A autonomous completion — operator listening is post-hoc; no cycle
     idles on a verdict; the run must be able to finish and close.
   - D-B build/deliver all focus songs; later milestones start when
     artifacts exist.
   - D-C full-corpus recreation A/Bs OUT OF SCOPE; corpus transcription
     only as rules/ear input.
   - D-D palette becomes PRIMARY render after one proven palette render on
     Chicken Grease (see determinism gate, below).
   - D-E ear trained on AUDIO ONLY (embeddings vs ratings, held-out
     validation, seeded).
   - D-F completion = 5 novel INSTRUMENTAL songs (band-6/7 style) at ear
     ≥6 + one interpolation-hybrid demo, donor-song mix match, delivered
     under `data/v3/deliveries/generated/`; then completion report and
     clean close.
8. **Focus gate satisfied** (`…focus_gate_satisfied.txt`): What If I Go +
   Disco A approved (3/5 incl. mandatory).
9. **Determinism consolidation** (`…determinism_consolidation.txt`): ONE
   parameterized driver for all recreation; per-song facts in data, never
   code; env-pin manifest in every delivery. IN FORCE.
10. **Determinism stance for generation** (`…determinism_stance_generation.txt`):
    rules extractor deterministic; ear seeded-reproducible; composition is
    a SEEDED GENERATOR PROGRAM (agent designs the generator, never
    hand-writes songs except as flagged fallback). IN FORCE.

## 2026-09-03 — hardening and closure prep
11. **Stage-checkpointed driver** (`…stage_checkpointed_driver.txt`):
    content-addressed per-stage caching; long runs detached; replay-audit
    freshness cache. IN FORCE — `recreate_v3_checkpointed.py` is the only
    executor of audio.
12. **Rome + Peach Dream approved; full determinism certificate**
    (`…full_determinism_certificate.txt`): focus set 5/5 operator-approved;
    M-V3-FOCUS LANDS. End-to-end double-run certificate required
    (`docs/v3_determinism_certificate.md`), stage coverage audit, Surge XT
    exclusion clause (palette-primary only if byte-deterministic; else
    deterministic palette members carry the primary path), certificate
    discipline extends to rules/ear/generator/donor-mix. IN FORCE.
13. **Sound-matching two-phase policy** (operator-agreed, recorded in
    `docs/ARCHITECTURE_v4_simplified.md`): the per-instrument sound-match
    SEARCH may be stochastic/agentic; the winning **sound profile** is
    pinned and its replay must be byte-deterministic; VST escape hatch =
    sha-pinned bounce with `render_replayable: false`. IN FORCE.
14. **Cleanup/refactor stage** (operator-directed, this document's era):
    run killed; stale code/data/docs pruned per
    `docs/REFACTOR_2026-09-03_inventory.md`; simplified architecture in
    `docs/ARCHITECTURE_v4_simplified.md`; conventions in
    `docs/CODEBASE_GUIDE.md`. Historical note: pre-refactor manifests
    reference rubrics/specs at `docs/<name>.md`; those files now live in
    `docs/specs/` (current binding) or `docs/run_archive/` (historical) —
    content and hashes unchanged (rubric_v2 hash re-verified 2026-09-03).

## Standing constraints (never expired)
- Model config verbatim (`claude-opus-4-7`); never changed by the run.
- Corpus audio never committed, never released; experimental use only.
- The operator's ear is the final authority on audible quality; a verdict
  arriving via guidance outranks any internal gate.
