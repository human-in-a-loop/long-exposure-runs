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

15. **Ear + sequence-model simplifications** (2026-09-03): the ear's
    full-corpus isotonic calibration is DROPPED — the 1–7 map anchors
    linearly on the exemplar set's leave-one-out mean and a fixed noise
    floor (exemplars must self-score ≥ 6; small band-4 spot check only).
    The CA-vs-Markov comparison in M-V4-RULES is a light sanity benchmark,
    not a strict selection gate: the CA model is retained unless it clearly
    fails (degenerate output, gross conformance failure), and both models
    stay available to the generator. IN FORCE.

16. **Stringency relaxations for the v4 run** (2026-09-03, operator-
    directed; quality-preserving): (a) double-run determinism proofs are
    ONCE PER NEW CODE PATH, not per artifact — cache-key identity +
    recorded shas carry the evidence thereafter; certificate re-issued
    only on env_pin change. (b) FAST verification is the DEFAULT for all
    routine driver runs (no `--verify-det`): the delivered bytes are
    identical with or without the ×2 self-check, which runs only for
    certificates and after env_pin changes. (c) Sound-profile replay
    proofs are per render family per song, not per profile. (d)
    Pre-registration/rubric-hash ceremony exists at milestone level only;
    anchor-preservation checks run only when inputs or env_pin changed;
    audits never re-derive verdicts on byte-identical inputs. (e) Merge
    structural gates WARN (not halt) on generated/interpolated songs.
    (f) Ear exemplar sanity is ≥4 of 5 exemplars ≥6 with none below 5.5.
    IN FORCE.

17. **v4 closure run completes** (2026-09-04 c21): all six closure
    milestones reach terminal state per campaign prompt. M-V4-RULES-1
    substantive (Model A statistical + Model B CA/VOMM, 97 rules across
    5 categories, 5 songs, byte-det ×2 HOLDS), M-V4-EAR-1 lightweight
    VGGish exemplar ear (CLAP unavailable — recorded substitution;
    sanity bar met 5/5 exemplars ≥6 LOO), M-V4-GEN-1 stall rule fired
    at 8 iterations with 3 passers of the 5 target (best 5 delivered +
    honest gap analysis) plus interpolation-hybrid demo. Two milestones
    LANDS with honest gaps: M-V4-PROFILES-1 4 non-CG songs blocked_on
    `_manager/M-V4-METRIC-SEMANTICS-c16` operator-authority escalation;
    M-V4-GEN-1 3-of-5 passers not 5-of-5. No cycle idled on operator.
    Completion report: `docs/v4_closure_completion_report.md`. Run
    ended cleanly per M-V4-CLOSE-1 directive.

18. **v4 REOPEN under distance-semantics resolution** (2026-09-05 c22):
    the 2026-09-04 operator directive definitively identified
    `embedding_cos_vggish` as a DISTANCE (identity probe = 0.0), voided
    the 0.60/0.40 thresholds as similarity clauses, and unblocked the
    4 non-CG focus songs plus mandated a CG family-verdict recompute.
    c22 landed Step 1 (audit: composite already uses embedding as
    positive-weight distance — ranks valid under distance semantics;
    re-label only), Step 2 (3 corrected sf2 family verdicts +
    corrected pinned profile siblings for bass, drums, guitar; family-2
    keeps FAMILY2_RULED_OUT because it loses on composite
    centroid/mel despite lowest embedding distance), Step 5
    (freshness_check_c22 for RULES + EAR both FRESHNESS_CACHE_HIT), and
    Step 7 (this report supersede). Invariant (d) disclosure: c9
    bass_v2 narrative claimed emb_cos=0.4946 but the on-disk bytes are
    prog 33 EBF composite=455.84 (the c3 stage-2b TOP-1 BY
    COMPOSITE) — meaning the CG-bass cell in the currently-delivered
    `cg_ab_mix.wav` (SHA `6e13e007…f9484b`) is ALREADY the corrected
    winner. Deferred: drums+guitar CG A/B re-render (additive driver
    extension; queued for next cycle) + 4 non-CG focus-song sweeps
    (unblocked, queued) + GEN batch stall-counter reset (conditional on
    donor-resolution audit). Completion report:
    `docs/v4_closure_completion_report.md`;
    original preserved as `_c21_original.md`.

19. **v4 CLEAN CLOSE at c77** (2026-09-06): campaign concluded per
    M-V4-CLOSE-1 with completion report v3
    (`docs/v4_completion_report_v3.md`, supersedes v2 via c14 str
    lemma). Verdict matrix: M-V4-CERT LANDS (E2E_DETERMINISM_HOLDS);
    M-V4-PROFILES LANDS_WITH_HONEST_GAPS; M-V4-SHOWCASE LANDS_pending_operator
    (9 A/Bs delivered, byte-det ×2); M-V4-RULES LANDS (76-rule artifact
    + VOMM CA-substitute); M-V4-EAR HALT-HONEST (c76 formal proof: L119
    empirically infeasible under VGGish-only backbone via monotone-
    calibration lemma; CLAP torchvision::nms blocked); M-V4-GEN
    HALT-HONEST_DELIVER_15 (3 iterations × 5 songs × byte-det ×2 = 15
    gen renders; batch-scoring delegated to FD-6 operator ear per c47
    OPT1 extension); M-V4-CLOSE LANDS. 24 A/Bs (9 focus + 15 gen) sit
    `pending_operator` per FD-6 for post-hoc ear verdict. env_pin
    `2ac444c3…922ca` held 56 cycles unchanged. c47 preservation-spin
    BAN honored from c69 onward. Stall rule pre-empted at 3 iterations
    since additional iterations cannot resolve the ear blocker
    (preservation-spin pattern BANNED). Interpolation demo optional,
    NOT authored (c78+ if operator requests). Run ends cleanly per
    campaign L151-152; operator verifies everything post-close.

## Standing constraints (never expired)
- Model config verbatim (`claude-opus-4-7`); never changed by the run.
- Corpus audio never committed, never released; experimental use only.
- The operator's ear is the final authority on audible quality; a verdict
  arriving via guidance outranks any internal gate.

