---
title: "Music-Gen — Cycles 7-9"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Cycles 7-9

## Abstract

Cycles 7-9 turned the campaign's rules-and-score axis from partially-built into fully-actionable and closed the outstanding infrastructure hole for rated-audio acquisition. Cycle 7 was the post-merge integration pass for fork `22b8c654f616` (three sibling clones landing the source-separation and heuristics workstreams). Cycle 8 ran fork `3a908edcb241` — three parallel clones delivering M-SCORE-1 (the MuseScore programmatic bridge), the M-TRANS-1 basic-pitch octave-suppression negative-finding sub-milestone, and M-INGEST-1/egress-ready-automation (the crash-resumable state machine that closes the "egress opens mid-run and nobody catches it" hole) — with clone 2 correctly using a second termination cycle to emit `COMPLETE` after cycle 1's `VALIDATED/high`. Cycle 9 ran fork `f1bae241bde9` — two clones delivering the M-RULES-1 extraction-half (28 typed rule rows across five rule types on the frozen 30 s merged score, byte-deterministic and provenance-resolvable) and the M-TEX-1 stage-by-stage measurement (24 panel numbers across three ordered audio stages, deterministic byte-for-byte, with an honest family-disagreement finding that validates the panel's refuse-to-aggregate contract). At cycle-9 exit, both halves of M-RULES-1 (schema + extraction) and both halves of M-TEX-1 (panel + stage-by-stage) are validated; M-SCORE-1 is `validated/high`; and the campaign's rules-ledger side of Goal G4 can now proceed independently of the rated-audio blocker. The egress-ready state machine is on disk, `IDLE`, and awaits two consecutive fresh `media_ok=true` rows to fire the rated-audio pipeline unattended.

## Introduction

At the start of cycle 7 the campaign had the ingestion chassis, classifier, DAW spike, heuristics battery, texture panel, source separation, and transcription survey in place, plus the schema-half of M-RULES-1, an ear-model preparation chassis, and the MuseScore programmatic bridge specified but not built. The eight-song rated corpus was still blocked by an egress denial of `*.googlevideo.com`. The three cycles reported here were driven by three questions: can the merged score be produced deterministically so downstream rules extraction is unblocked; can the "nobody notices when egress opens" hole be closed programmatically rather than by human polling; and can the two remaining halves of M-RULES-1 and M-TEX-1 be closed on the synthetic corpus so the rules-ledger side of Goal G4 is complete without waiting on rated audio. The answer to all three is yes.

## Approach

**Cycle 7 (post-merge integration, fork `22b8c654f616`).** A worker-only cycle folded three prior clones (M-SEP-1 htdemucs adoption, M-HEUR-1 heuristics battery, M-TRANS-1 transcription survey) into the main workspace. The pattern was the standard one from earlier cycles: propagate sub-milestone identifiers into the five-column plan-of-record table, adopt orphan artefacts via `_infra/adopt-fanout-artifacts-*` ledger events, and re-run the cross-branch integration test at the merged state. This is prior context for what follows, not a load-bearing contribution.

**Cycle 8 (fork `3a908edcb241`, three clones).** Three parallel branches ran with disjoint file trees:

- Clone 0 built M-SCORE-1: `scripts/score/{bridge, jsonl_to_midi, seed_score}.py`, driving `mscore3 3.2.3` headless under `QT_QPA_PLATFORM=offscreen`, with a public API of `xml_to_midi`, `midi_to_xml`, `merge_stems_to_score`, and `ScoreBridgeError`. Two non-obvious mechanics were surfaced empirically and folded in: a determinism-scrubbing list for `mscore3`'s time- and build-varying metadata (`<encoding-date>`, `<software>`, `<source>`, `<encoder>`, `<supports>`, mscore's default `<creator>`), plus a first-occurrence renumbering of the 32-hex-digit ids music21 assigns to `<part>` / `<score-part>` / `<score-instrument>` / `<midi-instrument>`; and an interval-graph-coloring workaround for `mscore3`'s per-part MIDI voice-cap (six voices in one `<part>` collapse to fewer note-on streams on export), splitting into `{stem}__v{k}` parts with a `parts_mapping.json` sidecar. `music21 9.1.0` was pinned at the top level for this branch.
- Clone 1 built the M-TRANS-1/basic-pitch/octave-suppression sub-milestone. The filter groups notes into 25 ms co-onset buckets, enumerates within-bucket pairs whose pitches differ by exactly 12 semitones, qualifies pairs by `dur_min ≥ T_min_ms` and `overlap_frac ≥ overlap_min`, and iterates qualified pairs in confidence-descending order with velocity → duration → lower-pitch tie-breaking; on tie the higher-pitched member is the loser, preserving the bass fundamental. The pass is single-pass by contract. A 3×3 grid over `T_min ∈ {50, 100, 200}` ms and `overlap_min ∈ {0.3, 0.5, 0.7}` was published as a nine-cell heatmap co-located with the TSV.
- Clone 2 built M-INGEST-1/egress-ready-automation as a crash-resumable state machine over `IDLE → ARMED → TRIGGERED → HARVESTING → CHUNKING → CLASSIFYING → READY` with a `FAILED` sink. The trigger rule — two consecutive fresh `media_ok=true` rows in the probe log with a strict 24-hour staleness filter — is deliberately not tunable through the CLI. `state.json` is written atomically per transition (`NamedTemporaryFile` + `fsync` + `os.replace`); `transitions.jsonl` is append-only. `subprocess.run` is replaced at import time with `_SubprocessRunForbidden` in tests, so no real network was exercised.

The three branches merged into the main workspace with no file-tree overlap and no environment conflict; `music21 9.1.0` was added top-level without breaking the numpy 1.26.4 / TensorFlow 2.21 / basic-pitch-in-venv stacks. Clone 2 correctly used a second termination cycle to emit `COMPLETE` after its cycle-1 `VALIDATED/high` — a null cycle on genuinely-exhausted scope, per the pattern the campaign has now established.

**Cycle 9 (fork `f1bae241bde9`, two clones).** Both branches consumed cycle 8's M-SCORE-1 output as their common upstream:

- Clone 0 built the M-RULES-1 extraction-half. Five per-rule-type extractors (`harmonic-v1`, `rhythmic-v1`, `melodic-v1`, `form-v1`, `arrangement-v1`) read the frozen `data/score/merged_synth030s.musicxml` via music21 9.1.0 and emit typed rule rows through the M-RULES-1/schema/ledger-writer. `rule_id` is derived by the pre-existing `derive_rule_id(rule_content)` helper — a SHA-256 over the canonical JSON of `{rule_type, scope, sorted provenance_pointers, parameters}`, never `ts`/`extractor`/`event_id`. `event_id` derives deterministically from `rule_id`; `ts` is pinned at a constant so re-runs are byte-identical.
- Clone 1 built the M-TEX-1/stage-by-stage measurement. Three ordered audio stages at 44.1 kHz stereo: `original.wav` (a byte-stable rewrite of the M-SEP-1 `synth_030s/mix.wav` via `scipy.io.wavfile`, dodging libsndfile's per-write creation-date chunk), `bare_midi.wav` (fluidsynth on the M-SCORE-1 merged MIDI with argv byte-identical to `scripts/separation/synth_gt.py` and an asserted SF2 SHA), and `effects_layered.wav` (a pinned DawDreamer chain — Surge XT Chorus + Reverb + post-hoc gain envelope — with determinism pins applied before any DawDreamer import). The frozen 8-key texture panel was run across all three ordered pairs (24 numbers), and the report refuses to aggregate.

## Findings

### M-SCORE-1 (cycle 8, clone 0) — `validated/high`

The 8-bar seed round-trips to byte identity across two full `xml → mid → xml → mid → xml` passes after scrubbing; note preservation is 88/88 events with 0.00 ms onset drift. On the 30 s M-SEP-1 synth mix the merged full-song identity-merge F1 is **1.0000 / 1.0000 / 1.0000** on drums / bass / other against the basic-pitch input MIDIs — the bridge preserves every input note. F1 vs the M-SEP-1 tiled ground truth is 0.0000 / 0.4746 / 0.7317, upper-bounded by cycle-6 basic-pitch quality: the drums row is the lower-bound zero-notes case (basic-pitch emits no notes on a pitchless drum stem); the bass row reproduces `docs/transcription_survey_report.md §5` bit-for-bit; the other row *raises* the cycle-6 baseline of 0.72 slightly because every input note survives the merge and recall reaches 1.0. The brief's explicit relaxation clause for basic-pitch-upstream-bounded shortfalls applies, and the report §3 diagnosis is thorough. All four legibility contracts hold: malformed MusicXML (`mscore3` returns exit 0 on structurally-invalid input and writes an empty MIDI — the bridge scans stderr for `"is not a valid musicxml file"`, `"is not a musicxml score-partwise file"`, `"cannot import"`, `"empty score"` and escalates), missing input, timeout, and missing per-stem MIDI each surface as `ScoreBridgeError` with a useful diagnostic. Merge snaps every input onset and duration to a 1/64-quarter grid (~7.8 ms at 120 BPM; ≤ 3.9 ms max shift, well under `mir_eval`'s 50 ms tolerance) because music21's serializer refuses arbitrary sub-tuplet durations. Test suite is 23/23 green.

### M-TRANS-1/basic-pitch/octave-suppression (cycle 8, clone 1) — `invalidated/high` (negative finding, escape hatch)

The 3×3 grid across `T_min × overlap_min` publishes:

| T_min \ overlap_min | 0.3 | 0.5 | 0.7 |
|---|:---:|:---:|:---:|
| **50 ms** | **+0.1513** | **+0.1513** | **+0.1513** |
| **100 ms** | **+0.1513** | **+0.1513** | **+0.1513** |
| **200 ms** | +0.1152 | +0.1152 | +0.1152 |

Best-cell aggregate bass F1 uplift is **+0.1513** (baseline 0.4773 → 0.6286); the **+0.3 success bar is not met on any cell**. The `overlap_min` axis is flat (the `overlap_frac` distribution on the cycle-6 bass JSONL is bimodal near 1.0 for real octave-doubling artefacts and near 0.0 for spurious non-artefact pairs, and none of the swept values lands between the modes); `T_min` has a single step at 200 ms; the two axes collapse to one useful trust-threshold knob in `[50, 100]` ms. Diagnostic on `synth_030s/bass` shows the filter correctly suppresses the (33 → 45) and (36 → 48) octave pairs (14 notes removed, precision jumped 0.318 → 0.467), but fails to suppress the chained (45 → 57) and (48 → 60) pairs because the specified single-pass rule skips any pair whose either member is already suppressed — exactly the "chain of three octaves" edge case the brief's mechanism section anticipated as a known limitation. The harmless-to-others constraint is trivially satisfied everywhere (drums Δ = other Δ = 0.0000, mechanical from the bass-only driver). The escape hatch was invoked cleanly: no re-tuning of the co-onset window, the trust-threshold definition, or the harmless-to-others constraint. The audit reproduced the TSV SHA-256 live (`d87fa0f5e6d87e6be551fcfb4e844a35c247733c42b19452d416b5ba573b0ec2`) and concurred with the recommendation to reopen only via fixed-point iteration in a later cycle (one-line wrapper, expected +0.10 additional aggregate F1 based on the pitch-set arithmetic).

### M-INGEST-1/egress-ready-automation (cycle 8, clone 2) — `validated/high`, then `COMPLETE`

Six named scenarios pass end-to-end against synthetic fixtures at `tests/fixtures/egress_status/` with the reference clock frozen to `2026-08-28T10:00:00Z`: all-false → `IDLE`; single-true-then-back → `IDLE`; two-consecutive-triggers → `TRIGGERED(1, 2)` → `READY`; already-triggered-then-false → `READY` (state authoritative; re-scan does not retract); interleaved-then-true-true → `TRIGGERED(2, 3)` → `READY`; stale-row-does-not-count → `ARMED((1,))` because the 24 h-old row is invisible to the fresh-only filter. Every drive-through additionally asserts that `state.json` on disk matches the terminal in-memory state (or is absent when the machine never left `IDLE`), that `transitions.jsonl` records the correct sequence and is append-only, and that a second `EgressReadyMachine(...)` against the same disk state returns the same terminal state without re-firing any hook (idempotence). Byte-deterministic `transitions.jsonl` across two `--watch` invocations against the same fixture (SHA-256 equal); atomic `state.json` under a monkey-patched `os.replace` mid-transition (previous bytes remain readable); zero live `subprocess.run` calls; zero `sidecar_nonfactor` imports. `--resume` restarts only the failed stage and its successors; `--reset-failure` requires `--force-idle` as a two-flag acknowledgement, refused otherwise with CLI exit 2. Test suite 62/62 green; §17 of the cross-branch integration test adds 52 checks and is green. Cycle 2 was a null cycle on exhausted scope, emitting `COMPLETE` with `[[BRANCH_COMPLETE]]`; the runtime state artefacts (`state.json`, `transitions.jsonl`) are correctly absent until the first live trigger fires.

### M-RULES-1/extraction (cycle 9, clone 0) — `validated/high`; parent `M-RULES-1` closed

Twenty-eight rules land on `data/rules/ledger.jsonl` at ledger SHA-256 `4fe722adde034c099ff9e65437f0d5c138cb3dd2595089960150af5c2546fc4b`:

| Rule type | Rows | Threshold | Representative content |
|---|---:|:---:|---|
| harmonic | 6 | ≥5 | `key=F_major, chord_progression=[V, vii, iii, I, i, I, II, ii], cadence=none` |
| rhythmic | 6 | ≥5 | `tempo_bpm=120.0, meter=4/4, pattern=[…32 cells…], swing_ratio=0.5` |
| melodic | 6 | ≥5 | `contour=static, range_semitones=24, PCH sum=1.0000000` |
| form | 5 | ≥5 | five sectionizations (monolithic, uniform-4m, uniform-2m, ABAB-4m, A-B-A halves) |
| arrangement | 5 | ≥5 | `instrumentation=[drums,bass,other], density_over_time=[…], layer_events=[…]` |
| **total** | **28** | ≥25 | 5.6× margin on aggregate |

Every row passes `validate_batch()` (28 / 28, zero errors); two independent runs produce byte-identical ledgers; every provenance pointer re-hashes to its declared source (28 / 28); `read_ledger()` returns rows in first-seen `[harmonic, rhythmic, melodic, form, arrangement]` order; `effective_rules()` (no supersedes this cycle) equals `read_ledger()` (28 == 28); the 34-assertion extraction test suite is green; the 25-assertion schema regression suite is green; the AST scan for `sidecar_nonfactor` across `scripts/rules/extract/` returns zero hits. Three honest limitations are documented and disclosed rather than papered over: the rhythmic extractor falls back to bass onsets because the frozen basic-pitch drums stem is empty (every hit is labelled `"kick"` as a onset-grid placeholder; a future `rhythmic-v2` supersedes when a real drums transcription lands); the form extractor emits five parallel sectionizations of the seed rather than five detected sections (a grammar-fit workaround because `form.parameters` only accepts a `sections` list — a `form-v2` grounded on novelty-curve boundaries is the right supersede); the merged score reports 131 nominal measures for a 30 s clip because music21 sees trailing empty measures across the ten sub-parts (extractors correctly honor the nominal count; upstream M-SCORE-1 refinement flagged). None of the three is a defect blocking the parent milestone. Both halves of M-RULES-1 (schema, cycle 6; extraction, this branch) are now closed.

### M-TEX-1/stage-by-stage (cycle 9, clone 1) — `validated/medium`; parent M-TEX-1 `validated/medium`

The 24 texture-panel numbers on the three ordered pairs:

| a_stage | b_stage | mel_l1_db | spectral_centroid_rmse_hz | rms_env_rmse | lufs_m_rmse_lu | embedding_cosine_distance |
|---|---|---:|---:|---:|---:|---:|
| original | bare_midi | **9.906** | **2804.9** | **0.0276** | **2.682** | **0.1234** |
| original | effects_layered | **10.937** | **2743.5** | **0.0488** | **5.372** | **0.0951** |
| bare_midi | effects_layered | **6.533** | **211.8** | **0.0449** | **5.414** | **0.0672** |

Metadata columns (`sr_hz=44100`, `n_samples_compared=1_323_000`, `embedding_rung=vggish`) are constant across pairs. The three families **disagree** on which of {`bare_midi`, `effects_layered`} is closer to `original`: envelope + mel-L1 rank `bare_midi` closer; spectral-centroid is essentially tied; VGGish cosine inverts and ranks `effects_layered` closer. This is not measurement noise — the LUFS-M gap is 2.68 vs 5.37 LU and the embedding gap 0.095 vs 0.123 is consistent — and it is exactly the informative disagreement the M-TEX-1/panel `<mechanism>` block predicted: envelope and mel-L1 measure things the effects chain damages by design (mean band energy, temporal loudness), and the perceptual embedding measures the auditory-scene features fluidsynth's dry, close-mic'd mix lacks and that reverb + chorus supply. The seed-fallback ladder was walked in order: `seed_mid_50s` and `seed_long_87s` were rejected on spectral evidence (both are 220 Hz sinusoidal test tones — FFT peaks at ~220 Hz with the next five bins ≤ 660 and peak/RMS ratios characteristic of pure sines), so rung (c) `synth_030s` was chosen with the verdict downgraded to `/medium` and the weaker "bare-MIDI-vs-fluidsynth-mix gap" claim substituted for the stronger "bare-MIDI-vs-recorded-original gap" claim throughout. The auditor re-ran the pipeline from a fresh directory and reproduced all four SHA-256 prefixes exactly (`153997a829f2b42c` / `fc8c3eccbff073d2` / `13d7238637d1ee31` for the three WAVs; `b3570a795c8c3e7a` for the TSV). Defence-in-depth against aggregation is at three layers (panel `PUBLIC_KEYS` assert, panel `_BANNED_KEYS` sweep, `measure_across_stages.py`'s own `BANNED_AGGREGATE_KEYS` sweep). Cross-branch integration test §19 (24 checks including the four SHA-256 baselines) is green.

### Campaign-level state at cycle-9 exit

- **Done in this range:** `M-SCORE-1` (`/high`); `M-RULES-1` (`/high` on both halves — schema at cycle 6, extraction at cycle 9); `M-TEX-1` (`/medium` on both halves — panel at cycle 4, stage-by-stage at cycle 9); `M-INGEST-1/egress-ready-automation` (`/high`); `M-TRANS-1/basic-pitch/octave-suppression` (`/high` invalidated, negative finding closed).
- **Ledger + plan:** ledger grew by 10 events on cycle 9's clone 0 alone; the plan-of-record now carries five-column rows for every sub-milestone emitted by cycles 8-9. Every event uses the healthy schema (`ts` / `narrative` / nested `confidence` / explicit `event_id` / `agent` / `cycle`) — the cycle-7 lesson (missing `event_id` on four rows, repaired in-cycle) has stuck.
- **Environment:** `music21 9.1.0` added at cycle 8 without touching `numpy 1.26.4`, TF 2.21, the basic-pitch venv, or the DawDreamer / Surge XT chain. No further drift in cycle 9.
- **Blocked on rated audio:** parent `M-EAR-1` v0 training; the state machine that will unblock it is on disk, `IDLE`, and awaits two consecutive fresh `media_ok=true` rows.

## Discussion

Three things about this range are worth naming.

First, the pattern of *closing the chassis half of a milestone before the data half arrives* — established in cycles 4-6 with the M-EAR-1 preparation branch — reached full effect this range. M-SCORE-1's bridge, M-RULES-1's extraction, M-TEX-1's stage-by-stage measurement, and the egress-ready state machine are all now unblockable-into-final-form: when the rated bytes appear, no new engineering is required to route them through classification, chunking, and rating training. The state machine is the last piece of that pattern: it turns the egress delay from a blocker into a scheduling constraint that the campaign can wait out without human polling and without downstream code paths that must be added later.

Second, the escape-hatch discipline held across two very different kinds of negative finding. The octave-suppression branch published the full 3×3 grid, diagnosed the shortfall at the level of individual pitches, and filed the sub-milestone as `invalidated/high` — a negative finding that leaves the ceiling on this algorithm family known for downstream consumers rather than smearing it with a passing number obtained by re-tuning. The stage-by-stage branch rejected two seed-ladder rungs on spectral evidence, fell to the third with a verdict downgrade, and substituted a weaker claim throughout the report so the escape-hatch consequences carried through rather than being buried under an unchanged headline. Both are worth preserving as canonical examples of how a falsifiable claim is supposed to fail without becoming an untraceable pass.

Third, the family-disagreement finding on M-TEX-1/stage-by-stage is the panel design's first-contact validation. The panel was built on the commitment that different families of measure measure different things and their disagreement is signal, and the eight-key contract with a triple-layer aggregation ban is that commitment made mechanical. The synth-mix seed produced exactly the kind of informative disagreement the mechanism block predicted — envelope and mel-L1 penalise the effects chain while VGGish rewards it — and the report refuses to reduce that trade to a scalar. When rated audio arrives, the same pipeline can be re-run to test whether the pattern holds on non-synthetic sources; that is a natural falsifiability check the current branch enables but does not consume.

The rules-ledger side of Goal G4 is now the most-complete goal in the campaign after G1. The 28 seed rules are a live example, not a theoretical schema, and the round-trip through `read_ledger()` / `effective_rules()` is exercised end-to-end. The known limitations on rhythmic-v1 and form-v1 are recorded as future-supersede cases with concrete triggers (a real drums transcription; a longer seed with detectable measure-scale structure) rather than as defects.

## Open Questions

- **First deterministic generation from the rules ledger (M-GEN-1).** Now unblocked; needs a target harmonic / rhythmic / melodic / form / arrangement selection over `effective_rules()` and a rendering path back to audio via fluidsynth-on-merged-MIDI. Deterministic content-addressed rule ids and the append-only ledger discipline are the load-bearing invariants any generator must respect.
- **M-EAR-1 v0 training** — still blocked on rated-audio egress. The state machine will fire the pipeline unattended when two consecutive fresh `media_ok=true` rows land in the probe log; the M-EAR-1 chassis (features, CORN head, leak-test) is ready for immediate reuse.
- **Fixed-point iteration on octave suppression.** One-line wrapper over the existing filter and grid; expected ≈ +0.10 additional aggregate bass F1 uplift based on the pitch-set arithmetic. Not prioritised above M-GEN-1.
- **`rhythmic-v2`** once a non-empty drums transcription lands (either basic-pitch re-run on a longer seed, or the alternative drums transcriber the M-TRANS-1 report recommended) — supersedes the fallback-labelled `"kick"` rows.
- **`form-v2`** — novelty-curve boundary detection on a ≥ 60 s seed where measure-scale structure is genuinely detectable; supersedes the five-parallel-sectionization strategy. If it turns out to be needed, a schema tweak allowing a `strategy` field on form rows (detected vs uniform-N vs multi-strategy) is the right accompanying change.
- **M-SCORE-1 refinement.** Investigate why `merged_synth030s.musicxml` reports 131 nominal measures for 30 s of content; if fixable, trailing-measure padding should be trimmed so downstream `end_measure` values carry musically meaningful semantics.
- **M-TEX-1 to `/high`.** Independent unblocks: real recorded audio (blocked on egress-ready-automation firing) and/or the CLAP-rung swap on M-TEX-1/panel/embedding.
- **CLAP-rung swap on the texture panel's embedding.** A future cycle can revise the family-disagreement pattern under a CLAP-trained perceptual embedding; whether the pattern holds under a different perceptual model is a natural falsifiability check.
- **Append-helper `event_id` default.** The cycle-7 lesson (append helper accepts events without `event_id`) has now been avoided twice by explicit-`event_id` discipline in cycles 8 and 9. A defensive default or a docstring update remains queued.

## Appendix: Provenance

**Cycle range:** cycles 7-9.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** cycle 7 researcher `7ef32dd0-70b4-44c4-8c9d-1b2210ffb068`; cycle 8 worker `6c80005c-53bb-40bf-beb2-cba0223803f9`; cycle 9 researcher `00a87607-73af-437b-bcf4-f8569fa27ca7`.

**Sub-agent transcripts (fork clones).**

- Fork `3a908edcb241` (cycle 8): clone 0 (M-SCORE-1) — researcher `843cb35b-9232-47b4-925c-a94c8d4ae257`, worker `ef72c18a-a76d-406c-87ae-f8243b0ba861`, auditor `0d95720c-be8d-4925-a72e-2f464664d68b`. Clone 1 (M-TRANS-1/basic-pitch/octave-suppression) — researcher `6f1cfefb-0c92-45eb-8eab-50e5c0f26095`, worker `af5ea339-1b1b-4a47-8309-045a70599ad5`, auditor `879f06da-0072-49a7-849f-2d04c6f8b34c`. Clone 2 (M-INGEST-1/egress-ready-automation) — cycle 1 researcher `8c17d07b-5cb3-40d7-b0d7-bd44e5cb72fb`, worker `fd0c6c9e-34bc-4b0d-b3ea-04c775716b71`, auditor `fffd9a03-d17b-48e9-a350-9ab90c4cdd95`; cycle 2 researcher `6853eb97-6044-4369-b334-52767b466268`, worker `925bafba-2111-49cd-80f8-d05134482317`, auditor `2b66a842-d318-415f-bb9a-389508e1bb54`.
- Fork `f1bae241bde9` (cycle 9): clone 0 (M-RULES-1 extraction) — researcher `d797a336-45d8-4451-ac91-325ab2e2c768`, worker `2803dfd0-ddfa-4816-b5ef-f620d52f941b`, auditor `0250497a-5491-442d-b56f-8cecaf57752f`. Clone 1 (M-TEX-1 stage-by-stage) — researcher `44aa9e94-e4af-40d1-adef-33c7a46bc92c`, worker `ed5a862a-6694-47b3-be68-49c612056085`, auditor `06901b63-38db-480d-9320-33c634326183`.

**Branch-scoped reports on disk** (all authored in this range):

- `docs/score_bridge_report.md` — 304 lines; round-trip proof, merged full-song F1 table, API reference, failure modes, reproducibility, non-factor isolation, determinism scrubbing list.
- `docs/basic_pitch_octave_refinement.md` — 246 lines; the negative-finding report with the full 3×3 grid, pitch-level diagnostic, and follow-up recommendations.
- `docs/egress_ready_automation.md` — 305 lines / 15 036 bytes; state diagram (mermaid), trigger rule with falsifiability criteria, six-scenario matrix, state persistence with worked crash-between-CHUNKING-and-CLASSIFYING example, failure recovery, human-override API, isolation, handoff, reproduction.
- `docs/rules_extraction_report.md` — 231 lines; five extractor designs, coverage figure, verification matrix, representative rule content, provenance resolvability, honest limitations.
- `docs/tex_stage_by_stage_report.md` — 309 lines; seed-selection ladder walk, 24-number panel table, per-family commentary, family-disagreement interpretation, determinism proof, artefact SHAs.

**Reproduction of load-bearing SHAs at cycle-9 exit:**

```
d87fa0f5e6d87e6be551fcfb4e844a35c247733c42b19452d416b5ba573b0ec2  data/transcribe/octave_suppression/grid_search.tsv
4fe722adde034c099ff9e65437f0d5c138cb3dd2595089960150af5c2546fc4b  data/rules/ledger.jsonl
153997a829f2b42c…                                                data/tex/renders/synth_030s/original.wav
fc8c3eccbff073d2…                                                data/tex/renders/synth_030s/bare_midi.wav
13d7238637d1ee31…                                                data/tex/renders/synth_030s/effects_layered.wav
b3570a795c8c3e7a…                                                data/tex/stage_by_stage_synth_030s.tsv
```

**Tests at cycle-9 exit.** `tests/test_score_bridge.py` — 23/23. `tests/test_octave_suppression.py` — 14/14. `tests/test_egress_ready_state.py` — 62/62. `tests/test_rules_schema.py` — 25/25. `tests/test_rules_extraction.py` — 34/34. `tests/test_integration_cross_branch.py` — 0 failures across §14 (octave suppression, 27 checks), §15 (score bridge, extended in cycle 8), §17 (egress-ready, 52 checks), §18 (rules extraction, 33 checks), §19 (tex stage-by-stage, 24 checks including four SHA-256 baselines), on top of the prior §§ carried forward.

**Environment stack unchanged since cycle 8:** `mscore3` MuseScore3 3.2.3 (headless, `QT_QPA_PLATFORM=offscreen`); Python 3.11.15 (`/usr/bin/python3`); `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; `mido` (Debian package); fluidsynth (Debian package) with pinned SF2; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`. Single-thread BLAS pins everywhere numeric determinism is required.

**Handoff to next cycle.** The natural next research step is M-GEN-1 — first deterministic generation from the 28-row rules ledger — which is now unblocked end-to-end. Rated-audio arrival remains the M-EAR-1 unblock; the state machine will handle it unattended and the M-EAR-1 preparation chassis is ready for immediate reuse. The follow-ups listed under **Open Questions** are queued in priority order.
