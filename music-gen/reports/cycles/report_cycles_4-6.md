---
title: "Music-Gen — Cycles 4-6"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Cycles 4-6

## Abstract

Cycles 4-6 extended the deterministic music-generation pipeline along three parallel workstreams that could progress without the rated corpus, whose audio downloads remain blocked by the workspace egress policy. A pitch/rhythm transcription survey (M-TRANS-1) measured note-level F1 for two transcribers across three durations on the M-SEP-1 clean-reference stems and published a seven-axis coverage matrix with an adopt-or-build verdict. A rules-ledger schema (M-RULES-1/schema) was designed, validated end-to-end on 25 synthetic instances, and hardened by a 15-check planted-invalid rejection matrix. An ear-model preparation chassis (M-EAR-1/preparation) — feature extractor, ordinal 1-7 CORN regression head, and a non-factor leak-test harness — was built and calibrated on the 55-clip classifier validation set; the leak detector clears its ≥ 0.90 detection floor and ≤ 0.10 false-positive ceiling for artist, genre, and era plants at full-strength contamination. All three deliverables were integrated back onto the main workspace, with 10 plan-of-record rows added, 6 ledger events written, one accidental append repaired, the cross-branch integration test extended to 130 checks (all green), and the rules-schema test suite adding 25 further checks. No new research directions were opened during the integration cycle.

## Introduction

The Music-Gen campaign builds a strictly deterministic loop from audio ingestion through classification, source separation, transcription, merged score, MIDI, DAW render, rules extraction, and generation. The campaign's fixed decisions — 30 s clips with 5 s overlap; non-negotiable provenance; only music continuing downstream; open-source survey before custom builds — were established in earlier cycles.

By the start of cycle 4, the ingestion chassis, music/non-music classifier, DAW round-trip spike, source-separation adoption (htdemucs), heuristics battery, and texture panel had all landed. The rated corpus of 80 songs (ear bands 6/5/4) had been registered with full provenance, but audio acquisition remained blocked by an egress denial of `*.googlevideo.com`. Per the campaign's rule that acquisition never blocks downstream work, cycles 4-6 targeted three workstreams that do not depend on the rated bytes: pitch/rhythm transcription, the rules-ledger schema, and the preparation half of the ear-model milestone (chassis, features, and leak-test).

These three efforts ran as sibling clones of one fanout; a subsequent worker-only cycle integrated their outputs back onto the main workspace. This report covers all three workstreams, the integration, and the state of the campaign at cycle-6 exit.

## Approach

The three workstreams were partitioned so their file trees do not overlap: `scripts/transcribe/*` for M-TRANS-1, `scripts/rules/*` for the schema branch, and `scripts/ear/*` for M-EAR-1 preparation. Each branch produced its own report under `docs/`, extended `tests/test_integration_cross_branch.py` with a section of invariants scoped to its own artefacts, and wrote shadow-ledger events inside its branch. A separate worker-only cycle merged the three onto the main workspace, propagated the sub-milestone rows into the plan of record, emitted six real ledger events (three adoption rows, one shadow-report reconciliation, one rollup, and one plan-file record), and reran the cross-branch test at the merged state.

Toolchain constraints drove one non-trivial environment decision. The pitch-transcription baseline, basic-pitch 0.4.0, pins `tensorflow<2.15.1`, while the main workspace runs TensorFlow 2.21.0 for the classifier's PANNs backbone. Rather than resolve the pin at the top level, the branch created a quarantined virtual environment at `workspace/basic_pitch_venv/` and drove basic-pitch through a subprocess. The `numpy` pin (1.26.4, forced earlier by `laion-clap`) held across both environments, so only TensorFlow needed isolation. A separate `jsonschema` 4.26.0 was added at the top level for the rules validator without disturbing the classifier or PANNs stacks.

## Findings

### Transcription survey (M-TRANS-1)

Two transcribers were evaluated against the M-SEP-1 clean-reference stems (drums, bass, and piano-labelled-as-`other`) at durations of 30, 60, and 90 s. The ground-truth reference for each duration is not a hand annotation but the exact program that generated the fluidsynth mixes: an 8 s / 4-bar phrase tiled in the audio domain, with the note-event ground truth recovered by replicating the source MIDI's note list at offsets `{0, 8, 16, …}`, dropping any note whose start passes the duration, and clipping any note whose end passes the duration. Regenerating the reference is SHA-256 bit-identical across runs on all twelve reference JSONL files.

The two transcribers are:

- **basic-pitch 0.4.0**, the ICASSP-2022 neural music-processing model, run through the quarantined venv.
- **A librosa-family alternative** — `librosa.pyin` for monophonic bass, `librosa.onset.onset_detect` plus a sub-band spectral classifier for drums, and CQT peak-picking for the polyphonic `other` stem. This alternative was chosen only after Crepe (fetch blocked at install-time; its setup pulls model weights from a host on the egress deny-list), Magenta's onsets-frames (same blocked host plus ~300 MB of dependencies), and note-seq (fetches but is not a transcriber by itself) were ruled out. The full ladder is recorded at `data/transcribe/alternative_selection.jsonl`. The two transcribers share `librosa`'s STFT/CQT at the low level, so the diversity is algorithmic rather than toolkit-family; this caveat is carried forward.

Note-level F1 was computed with `mir_eval.transcription.precision_recall_f1_overlap` at `onset_tolerance=0.05 s`, `pitch_tolerance=50 cents`, `offset_ratio=0.20`, `offset_min_tolerance=0.05 s`. For drums, general-MIDI drum note numbers were mapped to a synthetic pitch space (`hz = 100 + midi_pitch`) with `pitch_tolerance=0.5` so only exact drum-class matches count.

Mean F1 across the three durations, per stem:

| Stem | basic-pitch | alternative |
|---|---:|---:|
| drums (see disclaimer) | 0.000 | 0.397 |
| bass (monophonic) | 0.481 | **1.000** |
| other / piano (polyphonic) | **0.725** | 0.325 |

*Drum-stem disclaimer (lower bound):* basic-pitch is a polyphonic-pitch estimator; on pitchless drum stems it emits zero notes across all three durations, and the 0.000 F1 rows are a lower bound rather than a definitive measurement. The disclaimer is carried in the results table's `disclaimer` column and gated by an integration-test check.

![Note-level F1 by transcriber and stem, mean over 30/60/90 s clips](data/transcribe/results_bar_chart.png)

Determinism was verified on the basic-pitch × bass × 30 s cell by running the transcriber twice under single-thread BLAS pins (`OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`) with `tf.random.set_seed(0)` and the intra-/inter-op thread counts pinned to 1. The two runs are SHA-256 bit-identical (F1 delta = 0.000, ahead of the ±0.02 target). The librosa alternative is float-deterministic on the same inputs.

**Seven-axis coverage.** Every axis is explicit; no axis is silently omitted:

| Axis | Status | What is measured | What is not |
|---|---|---|---|
| rhythm | measurable | Beat F-measure at 70 ms tolerance = 0.99 at all three durations; estimated tempo 120.19 BPM vs reference 120.00 | groove nuance, rubato, polyrhythm, micro-timing |
| melody | measurable | Note-level F1 (table above) | expressive articulation, ornaments, vibrato |
| harmony | measurable | Triad detection over `chroma_cqt` vs the I-vi-IV-V reference: weighted accuracy = 0.983 at all three durations | modulations, extended harmony, voicings, inversions |
| timbre | proxy-only | MFCC-13 self-similarity ≈ 1.0 as sanity anchor | fluidsynth-in-the-loop resynthesis similarity, deferred |
| dynamics | measurable | Velocity F1 at ~13/127 tolerance on bass: alternative 1.000/1.000/1.000; basic-pitch 0.475/0.472/0.486 | envelope evolution within held notes, pedal, crescendo shapes |
| form | deferred | nothing (30/60/90 s durations are pure loop tiles with no A/B structure) | verse/chorus segmentation, motivic recurrence — unlocks with rated audio and a labelled form corpus |
| vocals-to-text | placeholder | returns `NO_VOCAL_STEM` on the silent-by-construction synth vocals stem | actual speech-to-text — no vocal audio yet |

**Verdict: BUILD.** No single off-the-shelf transcriber is adequate. The concrete recommendation is a per-stem router: basic-pitch for polyphonic pitched stems, a Crepe- or pyin-class monophonic pitcher for bass (the alternative already hits 1.000 here, cheaply), and a dedicated onset-plus-classifier for drums (recall ≈ 0.33 today, capped by the fixed-threshold onset detector).

### Rules-ledger schema (M-RULES-1/schema)

The schema-half of M-RULES-1 was closed. The extraction-half — first extraction from a merged score — remains gated on M-SCORE-1 and is explicitly out of scope.

The schema is JSON-Schema-2020-12 authoritative. Five rule types are supported end-to-end: `harmonic`, `rhythmic`, `melodic`, `form`, and `arrangement`. Every rule carries a content-derived identifier, provenance pointers, a continuous confidence in [0, 1], typed parameters keyed by rule type, and a scope block naming the level (`song` / `section` / `measure`) and start/end times.

Load-bearing design decisions:

- **Content-addressed `rule_id`.** The id is `"rule_" + sha256(canonical_json({rule_type, scope, sorted provenance_pointers, parameters}))[:16]`. Identical content produces identical ids; a one-bit change produces a different id. This distinguishes refinement (which changes content) from a repeated rule (same content, ignored on second write) without human judgment.
- **Append-only with supersede-as-event.** The ledger never edits in place. A `supersede` row references the old and new rule ids and carries a free-text reason. `effective_rules()` reads the supersede table at load time and filters superseded rows out. Transitive chains (A → B, B → C) resolve to only C.
- **Unknown-type policy: reject.** `rule_type` is a five-value enum. Anything else fails at the JSON Schema layer.
- **`additionalProperties: false` at every level.** A stray field is rejected, including any non-factor field (`genre`, `artist`, `era`, …). Non-factor isolation is a side-benefit of the schema rigor and is exercised by a dedicated planted-invalid case.
- **Two-layer validator.** JSON Schema enforces shapes, enums, and bounds mechanically. A hand-written Python layer enforces what JSON Schema cannot express portably: pitch-class-histogram sum-to-1 (within `1e-6`), scope end > start, form section end-measure > start-measure, and cross-row duplicate `rule_id`.

Twenty-five synthetic instances (five per rule type) were built by `scripts/rules/schema/examples/build_examples.py`. All 25 pass Layer 1 and Layer 2 clean; all 25 round-trip through `json.loads` and canonical-JSON re-serialisation with byte identity; and all 25 rule ids are reproducible from content on both computes.

Fifteen planted-invalid cases are caught cleanly. Eleven mutate a single field of a valid instance and are picked up by either JSON Schema (unknown type; empty provenance list; out-of-range confidence; unknown key regex; out-of-range swing ratio; extra top-level field such as `"genre": "rock"`) or by the Python layer (pitch-class-histogram sum drift of 0.001; form section with equal start and end; scope with equal start and end; duplicate rule id across two rows). Four further contract checks target the ledger writer itself: rejecting a duplicate `rule_id` at write time; rejecting a supersede whose target is not in the ledger; grepping the writer source for `open(..., "w")` or `"r+"` (both absent, enforcing append-only); and verifying that a full supersede chain returns only the leaf rule from `effective_rules()`.

### Ear-model preparation chassis (M-EAR-1/preparation)

Three interlocking deliverables were built without any dependency on the rated corpus.

**Feature extractor.** The default feature vector is the PANNs Cnn14 penultimate 2048-dim embedding concatenated with the four-dimensional M-HEUR-1 mess-scale vector — 2052 dimensions in all. An optional VGGish 128-dim embedding lifts the vector to 2180 dimensions but triples per-clip latency and does not materially change the leak-test outcome on spot checks; it is off by default. Features are cached at `data/ear/features/<clip_id>.npz` keyed by `(source_wav_sha256, feature_version, has_vggish)`; re-extraction from a cold cache produces a byte-identical 2048-dim PANNs vector on rerun.

Song-level aggregation, used for the eventual training path on 80 real songs, is `[weighted_mean || weighted_std]`. The per-clip weight follows the M-INGEST-1 anchored-tail debias rule: `weight = (t_end - t_start - overlap_with_prev) / 30` for the anchored tail clip, `1.0` otherwise. Numerical spot check against the M-HEUR-1 seeds: `7/30 = 0.23333…` for the long seed's anchored clip, `2/3 = 0.66666…` for the mid seed's anchored clip, and 1.0 for the short seed (single clip, no anchored tail). For the 55-clip leak test each clip is a single-clip song, so aggregation collapses to identity and the standard-deviation block is zero by construction.

**CORN ordinal head.** A CORN (Cao, Mirjalili, Raschka 2020) 1-to-7 ordinal regression head is used because ear-band ratings are ordinal, not categorical. For K = 7 the target is encoded as six binary sub-targets `t_k = 1[y > k]`; the head is `Linear(2052, 128) → ReLU → Dropout(0.3) → Linear(128, 6)` trained with `BCEWithLogitsLoss`; prediction is `1 + Σ_k 1[σ(logit_k) > 0.5]`. Training is Adam at `lr = 1e-3`, weight decay `1e-3`, full-batch on 55 samples, with all thread counts pinned and all seeds fixed. NaN heuristic values (from cases where the source heuristic returned null-with-reason) are imputed column-wise with the training-set mean.

Five-fold stratified cross-validation on synthetic labels (labels generated by projecting the feature matrix onto its first principal component, standardising, and rounding `y = 4 + 1.5·z + 1.0·noise` clipped to [1, 7]):

| Metric | mean | std |
|---|---:|---:|
| CORN mean absolute error | 0.891 | 0.106 |
| Majority-class MAE | 2.164 | 0.266 |
| Mean-integer MAE | 1.545 | 0.172 |
| Off-by-one accuracy | 0.836 | 0.106 |
| Kendall τ vs true ordinal | 0.741 | 0.103 |

CORN beats both naïve baselines cleanly and is off-by-one 84 % of the time.

**Non-factor leak-test harness.** Every one of the 55 valset clips gets three synthetic non-factor labels: `synth_artist` (five values, round-robin over the manifest), `synth_genre` (three values correlated with the true classifier label, so a well-fit head naturally picks it up), and `synth_era` (three values bucketing clips by SHA-256 of the clip id). These labels live at `data/ear/synth_nonfactor_plant.json` — a name, path, and format deliberately unlike the classifier's own `data/classifier/_nonfactor/`, so any accidental cross-read `grep`s visibly.

For each plant and contamination strength α ∈ {1.0, 0.5, 0.1}, a synthetic rating is `y = round(4 + α · 2 · z_nf + (1-α) · 2 · noise)` clipped to [1, 7]. The harness trains the CORN head, computes a two-sided η² statistic combining a `S_model` channel that reads off learned prediction structure (fires on correlated plants) and a `S_resid` channel that reads off residual dependence on the non-factor (fires on orthogonal plants), and compares it to the 90th percentile of a control distribution drawn from ≥ 20 no-leak controls.

Detection rates and false-positive rates on 20 no-leak controls per leak type, at the calibrated `epochs = 60` used inside the leak-test only:

| Leak type | Detection α = 1.0 | Detection α = 0.5 | Detection α = 0.1 | False-positive rate | τ percentile |
|---|:---:|:---:|:---:|:---:|:---:|
| artist | **0.914** | 0.257 | 0.057 | 0.100 | 90th |
| genre  | **1.000** | 0.829 | 0.086 | 0.100 | 90th |
| era    | **0.914** | 0.400 | 0.086 | 0.100 | 90th |

The α = 1.0 column clears the ≥ 0.90 floor for all three leak types; false-positive rates hit the ≤ 0.10 ceiling exactly at the 90th percentile by design. The weak-leak (α = 0.1) numbers are reported honestly: a 10 % signal / 90 % noise plant sits at or below the detector's sensitivity floor, and the success bar is specifically the α = 1.0 case. The two consecutive full runs at these settings reproduce all detection rates and τ values within `1e-5` under the pinned numeric envelope.

A calibration note travels with the harness. The CORN head's default training regime is 200 epochs and is fine for the model itself; the leak-test uses 60 epochs because, on 55 clips × 2052 features, 200 epochs lets the head memorise training folds and the residual channel loses signal-to-noise on orthogonal plants. At 60 epochs the head sits in the regime the `S_resid` statistic is designed to measure. Both settings are recorded in their respective run configs and the discrepancy is called out in the harness's argparse comment.

**Non-factor isolation.** No file under `scripts/ear/` imports `scripts.classifier.sidecar_nonfactor`. The integration test parses every `scripts/ear/*.py` to AST and asserts this at merge time; the auditor's protocol includes planting an evil import and verifying the check fails, then removing it and verifying the check passes.

### Post-merge integration

A worker-only cycle folded the three branch outputs back onto the main workspace. There is no overlap between the three branches' file trees (`scripts/transcribe/*`, `scripts/rules/*`, `scripts/ear/*`, and their `data/*` subtrees are disjoint) and no environment conflict (basic-pitch and TensorFlow 2.15 are confined to `workspace/basic_pitch_venv/`; `jsonschema` was added at the top level without touching existing pins). No cross-branch merge conflicts had to be resolved.

Two integration issues surfaced and were addressed:

- **Ten sub-milestone identifiers** produced by the three branches lived only in the plan-of-record's three-column reference table, not in the five-column milestones table that the internal consistency check reads. Ten rows were added — three for the transcription sub-milestones, one for the rules-schema sub-milestone, and five for the rules-schema sub-parts — bringing the internal check's error count from 10 to 0.
- **Twenty-seven orphan-artifact warnings and one missing-artifact warning** cleared by writing three adoption events on the ledger: one for the 25 synthetic rule-example JSONs; one for the two leak-test determinism artefacts (`leak_test_summary.det_run1.json`, `leak_test_summary.pre_fix.json`); and one for a shadow-only merge report referenced from a clone-scope-complete row.

Two further ledger events (a rollup for the integration and a record of the plan-of-record edit) were written for traceability, bringing the ledger from 102 events to 108. The plan-of-record grew from 31 to 40 tracked milestones. One accidental append — four ledger rows written without the `event_id` field, a consequence of the append helper not defaulting the field — was repaired within a minute by stripping and re-appending, before any other reader had consumed the malformed rows. The observation that the append helper accepts an event without an `event_id` is carried forward as a note for a defensive default or a docstring update in a later cycle.

**Tests at cycle-6 exit.**

- `tests/test_integration_cross_branch.py` — 130 of 130 checks passing (447 lines). The test now covers the ingestion chassis, classifier validation-set and sidecar, DAW-spike agreement, texture panel (exact-8 keys and matched-pair reproduction), source separation (per-stem RMS on the UMXHQ path), heuristics (isolation and anchored-tail debias), transcription (fifteen new checks covering the venv path, reference manifest, results TSV, the lower-bound disclaimer, and the seven-axis coverage), rules schema, and ear-model preparation isolation.
- `tests/test_rules_schema.py` — 25 of 25 checks passing (413 lines). Covers the planted-invalid suite, round-trip determinism, supersede transitivity, and duplicate-id rejection.

Four canonicalisation warnings remain on old ledger lines from before the canonicalisation rule was enforced; they are unfixable in an append-only ledger and are not regressions. Five "no ledger events" warnings on parent milestones (`M-SCORE-1`, `M-EAR-1`, `M-TEX-1`, `M-GEN-1`, `M-RULES-1`) are expected: sub-milestones roll up to parents on completion, and each of these parents has genuinely-remaining work.

## Discussion

The three workstreams share a common posture. Each committed to a substantive artefact that stands on its own — a survey with numbers and a verdict; a schema with a validator and a rejection matrix; a training-agnostic chassis with a leak detector — while explicitly deferring the piece of the milestone that genuinely requires either an upstream deliverable (the rules extractor waits for merged scores from M-SCORE-1) or the rated audio (the ear-model's real training run waits for egress). The pattern is worth naming: closing the *chassis half* of a milestone before the *data half* is available is the campaign's principal way of turning egress delay from a blocker into a scheduling constraint.

The transcription verdict is the most consequential result of the three. "Build a per-stem router" is not a rejection of the surveyed tools — basic-pitch is a strong polyphonic pitcher and the librosa alternative is a strong monophonic bass tracker — it is a claim that the *shape* of the transcription problem in this pipeline does not admit a single tool. That claim needs the surveyed numbers to be legible, and the honest disclaimers on the drum and weak-leak rows are how that legibility is preserved: an out-of-distribution measurement should not be treated as evidence against the model that produced it.

The leak-test's calibration decision deserves the same honesty. Reporting `epochs = 60` inside the harness while the head trains at `epochs = 200` in production would be a defect if the two settings were not clearly separated in-code and in-report. They are, and the mechanism is understood: the residual channel of the η² statistic requires the head to *not* be in a perfect-memorisation regime, which for 55 clips × 2052 features means a lower epoch budget than the head's own default. The correlated-plant channel is invariant to this budget; only the orthogonal-plant channels move.

The rules schema's content-addressed rule ids are the last decision worth flagging. The choice — hash the content, use the hash as the id — turns the "same rule extracted twice" and "a refined variant of the same rule" cases into a purely mechanical distinction: identical hashes mean identical content mean the second write is a no-op, and different hashes mean different content mean the second write is a new rule. Superseding is then always an explicit event, never an implicit overwrite. This is why the append-only property is enforceable at the writer without any human judgment about what counts as an edit.

## Open Questions

- **Per-stem transcription router.** Wire basic-pitch(piano/other) + pyin(bass) + a per-band spectral-flux drum-onset picker as a single `transcribe(stem_wav, stem_type) → midi` façade. The adopt-or-build verdict is now cashed out; the router is the next concrete step.
- **Octave-doubling suppression** for basic-pitch on `other` and bass stems, by dropping notes whose fundamental is an octave above a co-onset note. Expected to lift bass F1 from ≈ 0.48 toward ≈ 0.9 and piano F1 from ≈ 0.72 toward ≈ 0.85.
- **Drum-onset F1 recovery.** The librosa alternative sits at recall ≈ 0.33 because the miss set is dominated by snare-under-hihat confusion. A three-band spectral-flux picker is the natural fix and requires no learning.
- **Timbre axis upgrade.** Fold a fluidsynth-in-the-loop resynthesis path (estimated MIDI → fluidsynth → WAV → MFCC cosine vs the original stem) so timbre becomes a real number rather than a self-similarity anchor.
- **M-SCORE-1 bridge**, which unblocks the extraction-half of M-RULES-1.
- **Real ear-model training.** The eventual `scripts/ear/train.py` will consume the 80 real songs' features and ratings, train the CORN head with a train/val/test split, and rerun the leak test against the classifier's real non-factor sidecar. It runs the moment two consecutive `media_ok=true` rows appear in the egress probe log.
- **Fetch retries** for Crepe and Magenta once egress relaxes, so the transcription survey can be re-run with a wider algorithmic family than the librosa-derived alternative currently provides.
- **Append-helper defensive default** for `event_id`, either as a helper default or a docstring update, so a future caller cannot re-hit the four-row mistake corrected in-cycle.

## Appendix: Implementation Details

**Working directory:** `/home/user/long-exposure-runs/music-gen`.

**New code, this cycle range:**

- `scripts/transcribe/` — 6 files, including `_bp_call.py` (venv subprocess wrapper), `reference_events.py` (ground-truth recovery), `basic_pitch_baseline.py`, `alternative.py`, `eval_transcription.py`, `six_axis_coverage.py`.
- `scripts/rules/` — schema, validator (`validate_row`, `validate_batch`), ledger writer (`write_rule`, append-only, `LedgerError` on duplicate or missing supersede target), `rule_id.derive_rule_id`, `effective_rules`, and 25 synthetic examples plus the deterministic builder.
- `scripts/ear/` — `_interp.py` (interpreter guard), `features.py` (PANNs + heuristics + optional VGGish, cached npz), `corn.py` (~40 LOC CORN loss and predictor), `model.py` (Linear-ReLU-Dropout-Linear head), `leak_test.py` (η² harness with `S_model` and `S_resid` channels, per-leak-type τ escalation).

**Quarantined environment:** `workspace/basic_pitch_venv/` with `basic-pitch==0.4.0`, `tensorflow==2.15.0`, `numpy==1.26.4`; full 62-line pin set at `workspace/basic_pitch_venv/requirements.frozen.txt`.

**Tests added or extended:**

- `tests/test_integration_cross_branch.py` — extended to 447 lines / 130 checks; new sections cover M-TRANS-1 (15 checks: venv presence, reference manifest, results TSV rows and header, lower-bound disclaimer in TSV and report, six-axis coverage, no `sidecar_nonfactor` import in `scripts/transcribe/`), M-RULES-1/schema, and M-EAR-1/preparation isolation.
- `tests/test_rules_schema.py` — 413 lines / 25 checks: 11 planted-invalid mutations at the row layer, four ledger-writer contract checks, and round-trip / supersede / duplicate cases.

**Ledger state at cycle-6 exit:** 108 events, 40 tracked milestones, 0 internal-check errors, 0 orphan-artifact warnings, 0 missing-artifact warnings, 4 pre-existing canonicalisation warnings, 5 expected "no ledger events" warnings on parent milestones with genuinely-remaining work.

**Milestone status at cycle-6 exit:**

- Done in this range: `M-TRANS-1` and its three sub-milestones (`basic-pitch`, `alternative`, `six-axis-coverage`); `M-RULES-1/schema` and its five sub-parts (`json-schema`, `validator`, `ledger-writer`, `synthetic-instances`, `tests`); `M-EAR-1/preparation`.
- Blocked on rated audio: parent `M-EAR-1` (v0 training).
- Blocked on upstream: `M-RULES-1` extraction-half (needs `M-SCORE-1`).
- Not started: `M-SCORE-1`, `M-GEN-1`.

**Post-merge fixup artefacts:**

- Plan of record: 10 new rows in the milestones table.
- Ledger: 6 new events (`_infra/adopt-fanout-artifacts-m-rules-1-schema`, `_infra/adopt-fanout-artifacts-m-ear-1-preparation`, `_archive/clone-1-shadow-merge-report`, `_run/post-merge-integration-fork-3168fb0e47a1`, `_plan/register-post-merge-integration-milestones`, `_archive/integration-scratch-fork-3168fb0e47a1`).
- Repair: `tools/stale/_fix_missing_event_ids.py` stripped and re-appended four ledger rows written without `event_id`; no other reader had consumed them.

**Session references** (sub-agent transcripts underlying this report):

- Cycle 4: worker `c0d79af9-9bf4-49fe-8a1b-099a6e62246b`.
- Cycle 5: researcher `2fca5ef4-443d-4182-9f17-40dcf8f45b51`.
- Cycle 6: worker `32775f9f-0b78-4930-b57f-6e37f4800d2c`.
- Fork `3168fb0e47a1`, clone-2 (M-EAR-1/preparation): researcher/worker/auditor triads across cycles 4-6 recorded in `reports/cycles/report_cycles_4-6_clone_2.md`. Clone-2 confirmed at each triad that its scope was fully discharged in cycles 1-3 and produced no new work in this range, correctly holding rather than gold-plating validated criteria.

**Branch-scoped reports on disk:** `docs/transcription_survey_report.md`, `docs/rules_schema_report.md`, `docs/ear_preparation_report.md`.

**Reference:** Cao, W., Mirjalili, V., Raschka, S. "Rank consistent ordinal regression for neural networks with application to age estimation." *Pattern Recognition Letters* 140:325-331, 2020. arXiv:1901.07884.
