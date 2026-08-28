---
title: "Music-Gen — Cycles 10-12"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Cycles 10-12

## Abstract

Cycles 10-12 turned the campaign's rules-and-generation spine from validated components into a live end-to-end deterministic generation pass and hardened the ledger surface that everything sits on. Cycle 10 was the fork `00b3ae64444c` fanout with three clones: **M-GEN-1/first-generation** sampled one rule per rule_type from the 28-row M-RULES-1 ledger by SHA-256 tiebreak (no PRNG), assembled a 30 s three-Part MusicXML score, exported to MIDI through the M-SCORE-1 bridge, rendered bare via fluidsynth and effects-layered via the pinned DawDreamer chain, measured the M-TEX-1/panel across the bare↔effects pair, and scored with M-HEUR-1 + the M-EAR-1/preparation CORN head under an explicit uncalibrated-labels sentinel; **M-INGEST-1/breadth-second-seeds** ran the eight-stage pipeline end-to-end on two additional on-disk seeds (`seed_mid_50s`, `synth_060s`) with 24/24 SHA-256 byte-determinism per seed, honest per-stage failure reporting, and a candid corpus-limitation `/medium` verdict for the absence of any non-synth audio; and a third clone tightened the ledger-writer schema so every future append validates against a single-source-of-truth module with `status` / `narrative` / nested `confidence` / explicit `event_id` required. Cycle 11 was a researcher pass framing the integration. Cycle 12 was the post-merge integration for fork `00b3ae64444c` — the substantive adoption had already been done by the clones themselves through shadow-ledger emit into fanout concat, so the integration reduced to plan-row hygiene, two schema repairs on pre-hardening ledger rows, and a five-event capstone rollup emitted through the hardened writer, which caught real deficiencies in a first-draft event on its first live traffic and forced a corrected retry. At cycle-12 exit the workspace holds 191 ledger rows, zero `promise_check` ERRORs, and 413+ cross-branch integration test PASS lines across §1–§22 — including the load-bearing new sections §20 (schema hardening), §21 (M-GEN-1 SHA-256 anchors and PRNG-import grep guard), and §22 (breadth per-seed SHA-256 anchors × 2 seeds). Rated audio remains egress-blocked; the state machine that will unblock M-EAR-1 is `IDLE` and awaits its two-consecutive-`media_ok=true` trigger.

## Introduction

By the end of cycle 9 the campaign had a rules-and-score axis that was validated in pieces: an M-RULES-1 ledger with 28 typed rules, an M-SCORE-1 bridge with round-trip byte identity, a fluidsynth + DawDreamer render path, an M-TEX-1 panel with a refuse-to-aggregate contract, and an M-EAR-1 preparation chassis behind an uncalibrated-labels sentinel. What the campaign did not have was a live example that turned all of those pieces into a single deterministic generation. It also did not have a pipeline that had been demonstrated on more than one seed, and its ledger-writer helper had a recurring lesson — missing `event_id`, missing `status`, missing `narrative`, and non-canonical `confidence` — that had already been repaired twice in earlier cycles and would keep coming back until the validator was enforced at write time rather than at audit time. Cycles 10-12 addressed all three: first live generation, first pipeline breadth beyond one seed, and first hardened ledger writer that catches the recurring defects on the way in rather than on the way out.

## Approach

**Cycle 10 (fork `00b3ae64444c`, three clones).** Three parallel branches with disjoint file trees:

- **Clone 0 (M-GEN-1/first-generation).** `scripts/gen/sample_rules.py` groups the 28-row ledger by `rule_type`, computes SHA-256 over the canonical-JSON content of each candidate, and returns the lexicographically smallest hash per rule_type as the winner. Algorithm recorded on the manifest as `sha256_over_canonical_json_ascending` with `prng_used: false`; §21 of the cross-branch integration test greps every `scripts/gen/*.py` for `^(from|import) (random|numpy\.random|torch|secrets)` and fails on any hit. `scripts/gen/assemble_score.py` builds a three-Part music21 score satisfying the sampled rules' typed parameters. Render goes through the M-SCORE-1 bridge (`xml_to_midi`), fluidsynth with the pinned SF2 SHA `74594e8f…1cb0`, and the cycle-9 DawDreamer chain (Surge XT Chorus + Reverb + gain envelope) with determinism pins applied before any DawDreamer import. Scoring writes `scoring_v1.json` with three blocks (M-HEUR-1 mess-scales; M-TEX-1/panel bare-vs-effects; CORN head prediction with `ear.calibration = "synthetic_labels_only"` sentinel). Provenance writes `provenance_v1.jsonl` — six canonical-order rows carrying `input_shas` + `output_shas` + `script` + `script_version` so the chain reconstructs from any intermediate step forward.
- **Clone 1 (M-INGEST-1/breadth-second-seeds).** `scripts/breadth/enumerate_seeds.py` swept `corpus/seed/`, `corpus/ratings/`, `data/ingestion/seed/`, and `data/separation/synth_mix/` and confirmed on-disk that all 18 candidates are synth-derived (0 natural-recording seeds). Priority-order selection (non-synth first, then ≥ 30 s, then not the baseline) admitted the two seeds that maximise informational contrast within the available corpus: `seed_mid_50s` (50 s / 22 050 Hz mono / pure-sine content, exercising the sample-rate and upmix paths) and `synth_060s` (60 s / 44 100 Hz stereo / fluidsynth ground-truth, exercising the scaling axis on the baseline's content class). `scripts/breadth/run_seed.py` walks all eight stages, writes per-seed `stage_manifest.jsonl` with SHA / elapsed / diagnostic per stage, and drops all outputs into `data/breadth/<seed_id>/`. Basic-pitch is invoked in its quarantined venv via subprocess with the cycle-6 environment pins passed through the child env.
- **Clone 2 (ledger-writer schema hardening).** Extracted the ledger-event schema into a single-source-of-truth module `long_exposure/tools/_ledger_schema.py`, required `status`, `narrative`, nested `confidence: {level, rationale, assessor}`, and explicit `event_id` at write time, and added `tests/test_ledger_writer_validation.py` plus §20 of the cross-branch integration test. §20 pins the SSoT schema module identity so future edits cannot silently forget the contract.

**Cycle 11 (researcher).** Framed the integration cycle: no new research direction, no audit-level re-validation of the three clones' internal claims, one post-merge integration cycle whose job is to reconcile the workspace, run the validators, and close.

**Cycle 12 (post-merge integration, worker).** Two artefacts: `tools/stale/_repair_and_emit_fork_00b3ae64444c.py` (an atomic-`os.replace` ledger repair + five-event rollup emitter that also drives `promise_check` and both test suites and writes a JSON status report), and a rewritten workspace-root `merge_report.md` superseding the earlier fork-`f1bae241bde9` rollup. Two rows were added to `plan_of_record.md` for `M-INGEST-1/breadth-second-seeds/seed_mid_50s` and `M-INGEST-1/breadth-second-seeds/synth_060s` so `promise_check` accepts the pre-existing per-seed events on ledger lines 174 and 177. Two schema repairs on pre-hardening drift: line 160's `event_id` (a raw SHA-256 hex `3c9f2758…958d` produced by an ad-hoc emitter before clone 2's writer landed) was canonicalised via `uuid5(NAMESPACE_NIL, hex)` with the original hex preserved in `event_id_original`, and lines 179–184's `milestone_id: "M-TEST-1/writer"` (six round-trip test fixtures from clone 2's writer tests) were moved to the reserved namespace `_infra/ledger-writer-test-fixtures` with the originals preserved in `milestone_id_original`.

## Findings

### M-GEN-1/first-generation (cycle 10, clone 0) — `validated/medium`; parent M-GEN-1 rollup `validated/medium`

Five sampled rules:

| rule_type | winner_rule_id | content_hash (first 16) | n_candidates |
|---|---|---|:---:|
| arrangement | `rule_67d34b1c927ef33d` | `37dcaaf18bbf68ac` | 5 |
| form | `rule_84816f91e31e50c4` | `789c5c27825167fa` | 5 |
| harmonic | `rule_0271c7a9f3b5f606` | (F major, `[V, vii, iii, I, i, I, II, ii]`, cadence=none) | 6 |
| melodic | `rule_09f340921fa2d258` | — | 6 |
| rhythmic | `rule_88b63bd5e771c045` | — | 6 |

Assembler summary: `active_parts=[drums]`, `key=F_major`, `meter=4/4`, `pattern_tokens=32`, `progression_len=8`, `seconds_per_measure=2.0`, `sections_dropped=29`, `sections_placed=4`, `tempo_bpm=120.0`, `total_measures=15`.

All six declared SHA-256 prefixes on disk match the worker's report exactly and were independently auditor-verified: `sampling_manifest.json` `faafc86ba79dccd2`, `generated.musicxml` `95d8671af26e7cf9`, `generated.mid` `f237dcfc75f5de94`, `bare_midi.wav` `5b6f608249ea72ac`, `effects_layered.wav` `d81089d39f31b5ca`, `scoring_v1.json` `011e7c90e1ab3c72`. A fresh re-run of `scripts.gen.assemble_score` under `PYTHONHASHSEED=0 OMP=MKL=OPENBLAS=1 /usr/bin/python3` into a scratch directory reproduced the sampling-manifest and MusicXML SHAs byte-identically.

Scoring: M-HEUR-1 mess-scales all finite in [0, 1] (melody 0.4358 / timbre 0.2938 / form 0.3029 / dynamics 0.9266); M-TEX-1/panel bare-vs-effects 8 keys with no aggregate (mel_l1_db 16.76, spectral_centroid_rmse_hz 1798.62, rms_env_rmse 0.01057, lufs_m_rmse_lu 13.28, embedding_cosine_distance 0.0968); CORN head `ear.prediction = 6` under the `ear.calibration = "synthetic_labels_only"` sentinel, surfaced in both §1 and §8.2 of the report so it cannot be mistaken for a musical judgment. `provenance_v1.jsonl` — six canonical-order rows, chain reconstructs from any intermediate step forward. The falsifiability hatch fired once and honestly: the first-pass scoring JSON leaked full paths and therefore drifted between runs; the fix stored basenames + SHA-256s.

### M-INGEST-1/breadth-second-seeds (cycle 10, clone 1) — `validated/medium`

Both selected seeds passed 8/8 stages end-to-end (chunker → prepare-audio → M-CLASS-1 → M-SEP-1 htdemucs → M-TRANS-1 basic-pitch → M-SCORE-1 → render_bare_midi → M-TEX-1 panel). Byte-determinism across two independent runs: **24 / 24 SHA-256 anchors matched** (12 frozen contract artefacts × 2 seeds).

Panel numbers (original vs bare-MIDI) compared against the cycle-9 baseline:

| seed_id | mel_l1_db | sc_rmse_hz | rms_env_rmse | lufs_m_rmse_lu | embed_cos | provenance |
|---|---:|---:|---:|---:|---:|---|
| **synth_030s** (baseline, cycle 9) | **9.906** | **2804.9** | **0.02759** | **2.682** | **0.1234** | synth_ground_truth |
| synth_060s (this cycle) | 10.755 | 2764.9 | 0.02887 | 2.843 | 0.1619 | synth_ground_truth |
| seed_mid_50s (this cycle) | 15.808 | 601.0 | 0.30918 | 20.837 | 0.1593 | synth_seed_gen |

Content discrimination is real (classifier: `Sine wave` p = 0.9431 vs `Music` p = 0.8770; panel RMS-env RMSE 11× different and LUFS-M RMSE 7.8× different between the sine seed and the ground-truth-family seed). The `/medium` cap is a corpus fact, not a stage-level defect: no non-synth audio exists on disk. Two "quiet passes worth calling out" are named honestly on the report — htdemucs's energy skew on pure sines (correct-model-on-atypical-content, not a regression) and basic-pitch's 5× over-count on the sine seed's ~30 ground-truth notes (same octave-doubling artefact identified in cycle 8; the anti-pattern lock on re-attempting octave-suppression remains binding).

**Family-disagreement recurrence.** On `synth_060s` (same content family as baseline, longer duration), three of four numeric metrics track within 10 % while VGGish embedding cosine drifts 31 %. This is a second live datapoint validating the M-TEX-1/panel aggregation-refusal design commitment (the first was cycle 9 on M-TEX-1/stage-by-stage), and the mechanism is the same: VGGish's `mean_over_frames` global summarisation is not scale-invariant when the underlying content distribution shifts even slightly.

### Ledger-writer schema hardening (cycle 10, clone 2) — `validated/high`

Extracted the schema into `long_exposure/tools/_ledger_schema.py`; required `status`, `narrative`, nested `confidence: {level, rationale, assessor}`, and explicit `event_id` at write time; added `tests/test_ledger_writer_validation.py` and §20 of the cross-branch integration test pinning the SSoT module identity. The recurring cycle-7 lesson (append helper accepts events without `event_id`) is now enforced at write time rather than caught at audit time.

### Post-merge integration (cycle 12, worker)

The substantive adoption had already been done by the clones themselves through shadow-ledger emit into fanout concat. Integration reduced to plan-row hygiene, two schema repairs, and a five-event rollup capstone:

| # | milestone_id | status/conf |
|---|---|---|
| 1 | `_infra/ledger-writer-test-fixtures` | validated/high |
| 2 | `_infra/repair-ledger-cycle10` | validated/high |
| 3 | `_plan/register-post-merge-integration-fork-00b3ae64444c` | validated/high |
| 4 | `_run/post-merge-integration-fork-00b3ae64444c` | validated/high |
| 5 | `_archive/integration-scratch-fork-00b3ae64444c` | validated/high |

**Live proof-of-life of the hardened writer.** The first-draft rollup events failed with `LedgerAppendError: ledger event schema validation failed on 3 field(s): missing required field 'status'; missing required field 'narrative'; confidence.rationale missing`. The tightening from cycle 10 caught real deficiencies in its own process on its first live traffic — exactly as designed — and after the fields were fixed the retry succeeded. The earlier draft also mis-called `append_ledger_event(event)` with the wrong arity (correct: `append_ledger_event(workspace, event)`), which failed loudly at the Python layer. Both are the kind of failure the hardened writer was built to make impossible to reach the ledger.

### Verification at cycle-12 exit

- **Ledger:** 186 rows before integration → 191 rows after (5 rollup events; the shadow-ledger clone events had already merged in during fanout collapse).
- **`promise_check`:** rc = 0, **0 ERRORs**, 7 pre-existing WARNs unchanged (5 trailing-slash canonicalisation on old rows, `M-EAR-1` parent with no events, and one orphan CORN-head feature-cache byproduct `data/ear/features/gen_first_gen_d81089d39f31b5ca.npz` from clone 0's ear scoring; trivial to adopt in a follow-up if desired).
- **`tests/test_ledger_writer_validation.py`:** rc = 0 (PASS).
- **`tests/test_integration_cross_branch.py`:** rc = 0, `result: PASS (0 failures)` across §1–§22 with 413 total PASS lines; §20 pins the SSoT schema module identity, §21 pins the M-GEN-1 byte-determinism SHAs and the PRNG-import grep guard (61 checks), §22 pins the breadth per-seed SHAs across two seeds.

### Divergence, conflict, and overlap

None. All three cycle-10 clones self-verdicted validated; zero cross-branch content conflict; file trees disjoint (`scripts/gen/*`, `scripts/breadth/*`, and `tests/test_ledger_writer_validation.py` + `long_exposure/tools/_ledger_schema.py`). The `M-TRANS-1/basic-pitch/octave-suppression` anti-pattern lock (`invalidated/high` since cycle 8) held: clone 1 named it explicitly and did not re-attempt; clones 0 and 2 did not touch M-TRANS-1.

## Discussion

Three things about this range are worth naming.

First, cycles 10-12 close the gap between "the pipeline is proven" and "the pipeline has run end-to-end on live inputs and produced a byte-deterministic artefact with a full provenance chain." SHA-256 as the campaign's universal tiebreak — content-derived `rule_id`s (cycle 6), content-derived `event_id`s (cycle 9), and now content-derived rule *selection* (cycle 10) — is what makes the generation legible under audit: every candidate's hash is written to the manifest alongside the winner, and any future change to the ledger ordering, a new candidate rule, or an edit to any candidate's content will change the sampler's output in a fully-explainable way. A future switch to a PRNG-driven sampler is caught by the §21 grep guard. The pipeline is proven; the taste is not, and the report says so.

Second, the rule-composition incoherence surfaced by M-GEN-1/first-generation is not a bug in the pipeline — it is a real signal from a pipeline built on rules that were *selected* for content-hash determinism, not for musical coherence. The sampled arrangement rule silences pitched Parts; the sampled harmonic and melodic rules assume pitched Parts exist. Publishing this tension rather than patching it away is the falsifiability contract paying off again (cycle 8's octave-suppression closure was the first live datapoint; this is the second). The right fix is a post-sampling `M-GEN-1/rule-composition-constraint` coherence gate that flags when the arrangement silences all pitched Parts or when form section granularity exceeds the target duration by more than 4×; the wrong fix is to put it inside the sampler, because that would break the SHA-256 tiebreak's determinism.

Third, the cycle-10 ledger-writer hardening is the campaign's answer to the recurring "append helper accepts an event without X" lesson that has already been repaired twice. Moving the schema into a single-source-of-truth module and enforcing it at write time turns a recurring audit-time defect into a caught-at-boundary error, and the fact that the *cycle-12 integration's own first-draft events* were the first live traffic to trip the validator is the strongest possible evidence that the enforcement was necessary. `_infra/repair-ledger-cycle10` cleaned up the pre-hardening drift (one raw-hex `event_id`, six `M-TEST-1/writer` test-fixture rows moved to the reserved namespace) with the originals preserved as `event_id_original` / `milestone_id_original` — an append-only ledger cannot lose the historical record, so the repair adds fields rather than editing them.

The uncalibrated CORN head remains the campaign's biggest open credibility gap. The `ear.calibration = "synthetic_labels_only"` sentinel prevents the 6/7 rating on a drum-solo from being read as a musical judgment, and the `M-INGEST-1/egress-ready-automation` state machine will fire the retraining pipeline unattended the moment two consecutive fresh `media_ok=true` rows land. Everything downstream — CORN-head retraining, weight persistence at `data/ear/corn_head_v1.pt` with a feature-version guard, re-score of this cycle's `effects_layered.wav` for calibrated comparison — is a straight-line consequence of that unblock.

## Open Questions

- **`M-GEN-1/rule-composition-constraint`** — post-sampling coherence gate that flags arrangement-silences-pitched-Parts or form-granularity-too-fine-for-duration. Runs on the sampler's output, not inside the sampler; preserves the SHA-256 determinism.
- **CORN-head calibration.** When rated audio arrives, retrain the head on real labels, persist weights at `data/ear/corn_head_v1.pt` with a feature-version guard, and re-score the cycle-10 `effects_layered.wav` so 6/7 can be compared against a calibrated baseline.
- **Longer-duration M-GEN-1 targets.** `duration_s=60` or `90` so more of the sampled form rule's 128-measure structure lands. The current 30 s target was inherited from M-TEX-1/stage-by-stage; longer targets are cheap here.
- **Rules extraction per breadth seed.** Cheapest way to widen the M-RULES-1 corpus without new audio: run `scripts/rules/extract/from_score.py` over `data/breadth/{seed_mid_50s, synth_060s}/merged.musicxml`, emitting `M-RULES-1/extraction/breadth-<seed_id>` per seed.
- **SI-SDR-vs-mixture baseline on M-SEP-1.** Would catch pathologically-thin htdemucs splits on atypical content classes without re-training.
- **Split `tests/test_integration_cross_branch.py` by milestone** at ~890 lines. Cheap in scope; correctly deferred to a dedicated future cycle by cycle-10 workers so it does not entangle a substantive branch.
- **Adopt the CORN-head feature-cache byproduct.** `data/ear/features/gen_first_gen_d81089d39f31b5ca.npz` is a legitimate cycle-10 clone-0 side effect but is not in the declared artefact list; the next auditor pass should decide whether to adopt under `M-GEN-1/first-generation` or delete.
- **Documentation refinements** (auditor MINOR on M-GEN-1): update the report's total-check count from 343 → 413 and §21 count from 39 → 61; tighten the arrangement-silences-pitched-Parts claim to note that `ChordSymbol` MIDI realisations still fire even when the arrangement rule leaves pitched Parts otherwise empty. Not blocking.
- **CLAP-rung swap on the texture panel's embedding.** Orthogonal path to a more scale-invariant perceptual measure than VGGish's `mean_over_frames`; would revise the family-disagreement pattern now observed twice.
- **`M-INGEST-1/egress-ready-automation` firing.** Rated audio remains blocked; the state machine is `IDLE` and awaits its two-consecutive-`media_ok=true` trigger. Once it fires, `scripts/breadth/run_seed.py` is drop-in ready for the newly-arrived audio path (no code change required), and M-EAR-1 v0 training becomes eligible.

## Appendix: Provenance

**Cycle range:** cycles 10-12.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** cycle 10 worker `32b9a84b-e739-4c2a-8bbd-3b80bee60cec`; cycle 11 researcher `cac1cf88-e8ab-45c7-9e09-cdde39869b1d`; cycle 12 worker `97cbc233-d4b1-426d-90a4-80947635eb6d`.

**Sub-agent transcripts (fork `00b3ae64444c` clones).**

- Clone 0 (M-GEN-1/first-generation): researcher `c96fe124-a573-407b-9793-4dce6be05ae8`, worker `a9c6730b-5fc1-450f-8e2c-26bdb58cc27d`, auditor `179df4e2-bde2-4aa4-8bc5-6e58b7c16aaa`. Verdict `VALIDATED`, sub-milestone closes at `validated/medium`, parent M-GEN-1 rolls up at `validated/medium`.
- Clone 1 (M-INGEST-1/breadth-second-seeds): researcher `ed73c585-23ab-449c-9562-8a3ac46e5887`, worker `4d1aea55-0e21-43e0-ac6d-78fe877a7bb6`, auditor `44175d82-39e4-43ff-96a8-4084644a6b86`. Verdict `VALIDATED` at grade `/medium` under the brief's explicit downgrade rule for the on-disk corpus state.
- Clone 2 (ledger-writer schema hardening): verdict `validated/high`. Deliverables `long_exposure/tools/_ledger_schema.py`, `tests/test_ledger_writer_validation.py`, §20 of the cross-branch integration test.

**Deliverables on disk at cycle-12 exit:**

- Code: `scripts/gen/*` (7 modules, interpreter-guarded, zero PRNG imports); `scripts/breadth/*` (interpreter-guarded, zero `sidecar_nonfactor` imports); `long_exposure/tools/_ledger_schema.py` (SSoT schema module).
- Data: `data/gen/{sampling_manifest.json, generated.musicxml, generated.mid, renders/{bare_midi.wav, effects_layered.wav}, scoring_v1.json, provenance_v1.jsonl, render_manifest.json}`; `data/breadth/{seed_mid_50s, synth_060s}/*` (full per-seed artefact sets) + `{summary.tsv, seed_enumeration.tsv, determinism_baselines.txt}`.
- Figures: `docs/figures/{gen_first_generation_provenance.png, pipeline_breadth_panel.png}`.
- Reports: `docs/gen_first_generation_report.md` (397 lines); `docs/pipeline_breadth_report.md` (281 lines).
- Tests: `tests/test_ledger_writer_validation.py`; `tests/test_integration_cross_branch.py` — 413 PASS / 0 FAIL, with §20 (schema hardening), §21 (M-GEN-1, 61 checks including PRNG-import grep guard + SHA-256 anchors + provenance-chain shape), §22 (breadth per-seed SHA-256 anchors × 2 seeds).
- Repair + rollup tooling: `tools/stale/_repair_and_emit_fork_00b3ae64444c.py`; workspace-root `merge_report.md` rewritten with the actual integration outcome.
- Plan of record: 2 sub-milestone rows added at cycle 12 for `M-INGEST-1/breadth-second-seeds/{seed_mid_50s, synth_060s}`.

**Ledger state at cycle-12 exit:** 191 events. Repair events: `_infra/ledger-writer-test-fixtures`, `_infra/repair-ledger-cycle10`. Line 160's `event_id` canonicalised via `uuid5(NAMESPACE_NIL, "3c9f2758…958d")` with `event_id_original` preserved. Lines 179–184 (six `M-TEST-1/writer` test fixtures) moved to the reserved namespace `_infra/ledger-writer-test-fixtures` with `milestone_id_original` preserved.

**Environment stack unchanged since cycle 9:** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; VGGish rung on the texture panel; M-EAR-1/preparation CORN head under the `synthetic_labels_only` sentinel. Single-thread BLAS pins throughout; DawDreamer determinism pins applied before import.

**Rated audio.** Still egress-blocked per `corpus/CORPUS_STATUS.md`. `M-INGEST-1/egress-ready-automation` will fire the retraining pipeline unattended when two consecutive fresh `media_ok=true` rows land in `data/ingestion/egress_status.jsonl`. Not this cycle's problem; the state machine has been on disk since cycle 8, `IDLE`, and its runtime state files remain correctly absent until the first live trigger.

**Handoff to next cycle.** The natural next research step is `M-GEN-1/rule-composition-constraint` as a post-sampling coherence gate — the smallest legible unit that raises M-GEN-1 above `/medium` without touching the SHA-256 tiebreak's determinism. The cheap follow-up is rules extraction over the two new breadth-seed merged MusicXMLs to widen the M-RULES-1 corpus. The pre-wired large unblock remains M-EAR-1 v0 training on rated audio; when it arrives the entire chain from egress-ready-automation through CORN-head retraining, weight persistence, and re-scoring is a straight-line consequence of the trigger.
