---
title: "Music-Gen — M-GEN-1/first-generation (cycle 1, fork 00b3ae64444c, clone 0)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — M-GEN-1/first-generation (cycle 1, fork 00b3ae64444c, clone 0)

## Abstract

Cycle 1 of clone 0 delivered the campaign's first end-to-end deterministic generation pass: five rules (one per rule_type) were sampled from the 28-row M-RULES-1 ledger by SHA-256 tiebreak over canonical-JSON content-hashes with no PRNG anywhere, assembled into a 30 s three-Part MusicXML score via music21, exported to MIDI through the M-SCORE-1 bridge, rendered bare via fluidsynth with the pinned SF2, layered through the cycle-9 DawDreamer chain, measured by the M-TEX-1/panel across the bare↔effects pair, and scored by the M-HEUR-1 mess-scale battery plus the M-EAR-1/preparation CORN head under an explicit uncalibrated-labels sentinel. Every artefact on the six-stage provenance chain is byte-deterministic across two independent runs (the auditor re-ran `scripts.gen.assemble_score` in a scratch directory and reproduced the sampling-manifest and MusicXML SHA-256 byte-identically); the six declared SHA-256 prefixes on disk match the worker's report exactly; the integration test suite runs 413/413 with 61 dedicated §21 M-GEN-1 checks. The verdict is **`validated/medium`** — the pipeline claim is solid, but two known limitations shave the confidence honestly: the CORN head is trained only on synthetic labels (the `ear.calibration = "synthetic_labels_only"` sentinel is surfaced on the scoring JSON and in report §1 and §8.2 so the 6/7 rating cannot be mistaken for a musical judgment), and the sampled arrangement rule silences pitched Parts, producing a rule-composition incoherence the report publishes rather than patches. Parent M-GEN-1 rolls up to `validated/medium` at branch close.

## Introduction

By the end of cycle 9, all the ingredients for a first deterministic generation were on disk: the 28-row rules ledger with content-hashed `rule_id`s and typed per-rule-type parameters (M-RULES-1, both halves closed); the M-SCORE-1 bridge with round-trip byte identity; the fluidsynth path with a pinned SF2 SHA; the cycle-9 DawDreamer chain (Surge XT Chorus + Reverb + gain envelope) with determinism pins applied before any DawDreamer import; the M-TEX-1/panel with its refuse-to-aggregate contract; the M-HEUR-1 battery; and the M-EAR-1/preparation CORN head from the ear-preparation chassis. The brief for this branch was to compose them into a single deterministic generation pass — sample one rule per rule_type, assemble a score that satisfies those rules' typed parameters, render it, measure and score it, and publish the full `rule_id → audio_sha` provenance chain — without introducing a PRNG anywhere in the sampler, and with a candid falsifiability escape hatch if score assembly failed on any sampled rule. This is the pipeline's first live example that turns the rules ledger from a validated data structure into a load-bearing input.

## Approach

**Sampling.** `scripts/gen/sample_rules.py` groups the ledger by `rule_type`, computes SHA-256 over the canonical-JSON content of each candidate, and returns the lexicographically smallest hash per rule_type as the winner. The algorithm is recorded on the manifest as `sha256_over_canonical_json_ascending` with `prng_used: false`; a targeted grep guard in `tests/test_integration_cross_branch.py §21` fails the run if `random`, `numpy.random`, `torch`, or `secrets` appears in an import statement anywhere under `scripts/gen/`. The five winners and their content hashes are written to `data/gen/sampling_manifest.json` with the full candidate list per rule_type for auditability.

**Assembly.** `scripts/gen/assemble_score.py` builds a three-Part music21 score satisfying each winner's typed parameters: the rhythmic rule fixes meter (4/4), tempo (120 BPM), pattern (a 32-cell 16th-grid with `swing_ratio 0.5`); the harmonic rule fixes key (F major) and chord progression (`[V, vii, iii, I, i, I, II, ii]`); the arrangement rule fixes `active_parts` (`[drums]`); the form rule provides sections dropped to the target duration (29 dropped beyond 30 s, 4 placed); the melodic rule fixes contour and range. Total measures = 15; seconds per measure = 2.0. Every assembler decision is written into the manifest's `assembler_summary` block, including the honest `sections_dropped=29` count.

**Render.** MIDI is exported via the M-SCORE-1 bridge (`xml_to_midi`); `bare_midi.wav` renders through fluidsynth with the pinned SF2 SHA `74594e8f…1cb0`; `effects_layered.wav` applies the cycle-9 DawDreamer chain with determinism pins (`OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `torch.set_num_threads(1)`, `torch.manual_seed(0)`, `np.random.seed(0)`) applied *before* the first `import dawdreamer`. Both renders are 44.1 kHz stereo × 1 323 000 samples (exactly 30 s), non-silent (peaks 0.148 and 0.180 respectively).

**Scoring.** `scripts/gen/score_generation.py` writes `scoring_v1.json` with three blocks: the four M-HEUR-1 mess-scales (melody / timbre / form / dynamics, each finite in [0, 1], with populated `raw_features` and `blind_spots`); the M-TEX-1/panel bare-vs-effects measurement (8 keys, no aggregate, defence-in-depth against aggregation preserved through the panel contract); and the M-EAR-1 CORN head prediction with an explicit `calibration: "synthetic_labels_only"` sentinel. The scoring JSON stores basenames + SHA-256s rather than full paths, so it is portable and byte-stable.

**Provenance.** `scripts/gen/emit_provenance.py` emits `provenance_v1.jsonl` — six canonical-order rows (`sample_rules → assemble_score → xml_to_midi → render_bare → render_effects → score_generation`), each carrying `input_shas`, `output_shas`, `script`, and `script_version`, so the chain reconstructs from any intermediate step forward.

## Findings

### Sampled rules

| rule_type | winner_rule_id | content_hash (first 16) | n_candidates |
|---|---|---|:---:|
| arrangement | `rule_67d34b1c927ef33d` | `37dcaaf18bbf68ac` | 5 |
| form | `rule_84816f91e31e50c4` | `789c5c27825167fa` | 5 |
| harmonic | `rule_0271c7a9f3b5f606` | (F major, `[V, vii, iii, I, i, I, II, ii]`, cadence=none) | 6 |
| melodic | `rule_09f340921fa2d258` | — | 6 |
| rhythmic | `rule_88b63bd5e771c045` | — | 6 |

`assembler_summary`: `active_parts=[drums]`, `key=F_major`, `meter=4/4`, `pattern_tokens=32`, `progression_len=8`, `seconds_per_measure=2.0`, `sections_dropped=29`, `sections_placed=4`, `tempo_bpm=120.0`, `total_measures=15`.

### On-disk SHA-256 (all six auditor-verified)

| Artefact | SHA-256 (first 16) |
|---|---|
| `data/gen/sampling_manifest.json` | `faafc86ba79dccd2` |
| `data/gen/generated.musicxml` | `95d8671af26e7cf9` |
| `data/gen/generated.mid` | `f237dcfc75f5de94` |
| `data/gen/renders/bare_midi.wav` | `5b6f608249ea72ac` |
| `data/gen/renders/effects_layered.wav` | `d81089d39f31b5ca` |
| `data/gen/scoring_v1.json` | `011e7c90e1ab3c72` |

The auditor independently re-ran `scripts.gen.assemble_score` under `PYTHONHASHSEED=0 OMP=MKL=OPENBLAS=1 /usr/bin/python3` into a fresh scratch directory and reproduced the sampling-manifest and MusicXML SHAs byte-identically; §21 anchors the SHA prefixes as regression baselines and runs green at test time (not just at generation time).

### Scoring

- **M-HEUR-1 mess-scales (all finite in [0, 1]):** melody 0.4358 / timbre 0.2938 / form 0.3029 / dynamics 0.9266, each with populated `raw_features` and `blind_spots`.
- **M-TEX-1/panel (bare ↔ effects, 8 keys, no aggregate):** mel_l1_db 16.76, spectral_centroid_rmse_hz 1798.62, rms_env_rmse 0.01057, lufs_m_rmse_lu 13.28, embedding_cosine_distance 0.0968, embedding_rung `vggish`, sr_hz 44100, n_samples_compared 1 323 000.
- **M-EAR-1/preparation CORN head:** `ear.prediction = 6` in [1, 7] with `ear.calibration = "synthetic_labels_only"` sentinel present; the sentinel is re-surfaced in report §1 and §8.2 so downstream code cannot mistake the 6/7 rating for a musical judgment.
- **Meta-tracker (single-clip reduction):** `meta_tracker_single_clip` block records the `anchored_tail_weight = 1.0` collapse for a single clip and reports `heuristic_variance_across_clips = 0.0` — an honest reflection of "no across-clip signal on a single-clip render", not a fabricated statistic.

### Provenance chain

`data/gen/provenance_v1.jsonl` — six rows in canonical order (`sample_rules → assemble_score → xml_to_midi → render_bare → render_effects → score_generation`), each carrying `input_shas` + `output_shas` + `script` + `script_version`. The chain reconstructs from any intermediate step forward, and the §21 test asserts stage order and SHA presence.

![Provenance chain: rule_id → audio_sha, five sampled rules through six generation stages to bare + effects renders and the scoring JSON.](docs/figures/gen_first_generation_provenance.png)

### Non-PRNG and non-factor isolation

- PRNG scan of `scripts/gen/*.py`: **zero** `^(from|import) (random|numpy\.random|torch|secrets)` matches.
- Non-factor scan: the only textual match on `sidecar_nonfactor` under `scripts/gen/` is inside `assemble_score.py:46`'s docstring; the §21 grep guard uses `^(from|import) …sidecar_nonfactor` at line start and rejects it correctly.
- Interpreter guard `assert sys.executable == "/usr/bin/python3"` present on all six runnable scripts.

### Falsifiability escape hatches

The "byte-determinism failed → hunt source" hatch fired and was resolved honestly: the first-pass scoring JSON leaked full paths and therefore drifted between runs; the fix stored basenames + SHA-256s. All other hatches did not need to fire; the report §9 records which fired and which did not.

## Discussion

Three things about this branch are worth naming.

First, the sampling algorithm's determinism-by-content-hash is the load-bearing invariant. The rules-ledger schema (cycle 6) established content-derived `rule_id`s; the rules-ledger extraction (cycle 9) established content-derived `event_id`s on ledger rows; this cycle establishes content-derived rule *selection*. Determinism-by-hash is now the campaign's default answer whenever "how do you pick?" arises, and the answer is legible under audit because every candidate's hash is written to the manifest alongside the winner. A future change to the ledger ordering, a future addition of a new candidate rule, or a future edit to any candidate's content will change the sampler's output in a fully-explainable way; a future switch to a PRNG-driven sampler would break the invariant and would be caught by the §21 grep guard.

Second, the rule-composition incoherence is not a bug in the pipeline — it is a real signal from a pipeline built on rules that were *selected* for content-hash determinism, not for musical coherence. The sampled arrangement rule silences pitched Parts; the sampled harmonic and melodic rules assume pitched Parts exist. The branch publishes this tension rather than patching it away, and the concrete recommendation is a `M-GEN-1/rule-composition-constraint` sub-milestone in a future cycle: a *post-sampling* coherence gate that flags when the arrangement silences all pitched Parts, or when form section granularity exceeds the target duration by more than 4×. It must not live in the sampler itself, because that would break the SHA-256 tiebreak's determinism; it lives as a validator on the sampler's output. (One minor documentation refinement noted by the auditor: §8.1's claim that pitched Parts "produce no notes" under the drums-only arrangement is directionally correct but the exported `generated.mid` still contains ~62 note-on events with velocity > 0 from `music21.harmony.ChordSymbol` writing chord pitches at MIDI export; the pipeline is still non-silent and byte-deterministic, and the directional claim about rule composition stands.)

Third, the uncalibrated-ear caveat is the campaign's biggest open credibility gap. The CORN head is trained on synthetic labels because the rated audio is still egress-blocked, and the head predicts 6/7 on a drum-solo generated from an arbitrary rule composition — a strong signal that the head is uncalibrated. The `ear.calibration = "synthetic_labels_only"` sentinel plumbed through the scoring JSON and re-surfaced in the report is doing its job of preventing this from being read as a musical judgment, and the M-INGEST-1/egress-ready-automation state machine (cycle 8) will fire the retraining pipeline unattended the moment two consecutive fresh `media_ok=true` rows land. Everything downstream — the corn head weights persisted at `data/ear/corn_head_v1.pt`, the feature-version guard, the re-score of this cycle's `effects_layered.wav` for calibrated comparison — is a straight-line consequence of that unblock.

At branch close, `M-GEN-1/first-generation` is `validated/medium` and parent `M-GEN-1` rolls up to `validated/medium`. `/medium` (rather than `/high`) is the honest grade: the pipeline claim is solid, but the two known limitations (uncalibrated ear, rule-composition incoherence) shave the confidence.

## Open Questions

- **`M-GEN-1/rule-composition-constraint`** — post-sampling coherence gate that flags arrangement-silences-pitched-Parts or form-granularity-too-fine-for-duration. Runs on the sampler's output, not inside the sampler; preserves the SHA-256 determinism.
- **CORN-head calibration.** When rated audio arrives, retrain the head on real labels, persist weights at `data/ear/corn_head_v1.pt` with a feature-version guard, and re-score this cycle's `effects_layered.wav` so 6/7 can be compared against a calibrated baseline.
- **Longer-duration M-GEN-1 targets.** `duration_s=60` or `90` so more of the sampled form rule's 128-measure structure lands. The current 30 s target was inherited from M-TEX-1/stage-by-stage; longer targets are cheap here.
- **Documentation refinements** (auditor MINOR): update report §11 total-check count from 343 → 413 and §21 count from 39 → 61; tighten §8.1 to note that `ChordSymbol` MIDI realisations still fire even when the arrangement rule leaves pitched Parts otherwise empty. Not blocking.
- **Split the cross-branch integration test** by milestone at ~890 lines. Cheap in scope; correctly deferred to a dedicated future cycle by the worker so it does not entangle a substantive branch.
- **Shadow-ledger adoption at post-merge integration** — 85 orphan-artifact WARNs will clear under `_infra/adopt-fanout-artifacts-m-gen-1` at fork merge.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `00b3ae64444c`, clone 0.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `c96fe124-a573-407b-9793-4dce6be05ae8`, worker `a9c6730b-5fc1-450f-8e2c-26bdb58cc27d`, auditor `179df4e2-bde2-4aa4-8bc5-6e58b7c16aaa`.
**Auditor verdict:** **VALIDATED**. Sub-milestone `M-GEN-1/first-generation` closes at `validated/medium`; parent `M-GEN-1` rolls up at `validated/medium`.

**Deliverables on disk:**

- Code: `scripts/gen/{__init__.py, sample_rules.py, assemble_score.py, render_pipeline.py, score_generation.py, emit_provenance.py, plot_gen_report.py}` — interpreter-guarded, zero PRNG imports, no `sidecar_nonfactor` imports.
- Data: `data/gen/{sampling_manifest.json, generated.musicxml, generated.mid, renders/{bare_midi.wav, effects_layered.wav}, scoring_v1.json, provenance_v1.jsonl, render_manifest.json}`.
- Figure: `docs/figures/gen_first_generation_provenance.png`.
- Report: `docs/gen_first_generation_report.md` (397 lines).
- Test: `tests/test_integration_cross_branch.py §21` — 61 M-GEN-1/first-generation checks including per-artefact SHA-256 anchors, panel-no-aggregate assertion, heuristics-in-[0,1] contract, ear-calibration-sentinel presence, PRNG-import grep guard, and provenance-chain shape.
- Plan of record: line 42 carries the `M-GEN-1/first-generation` row with all five falsifiable criteria (a)–(e).

**Test state at branch close:** `tests/test_integration_cross_branch.py` — 413 PASS / 0 FAIL, 61 in §21. Live auditor re-run of `scripts.gen.assemble_score` in a scratch directory reproduces the sampling-manifest and MusicXML SHAs byte-identically.

**Environment stack unchanged since cycle 9:** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; VGGish rung on the texture panel; M-EAR-1/preparation CORN head. Single-thread BLAS pins throughout; DawDreamer determinism pins applied before import.

**Ledger routing.** Seven M-GEN-1 events written to the per-clone shadow ledger at `/home/user/music-gen-instance/fork-00b3ae64444c/clone-0/promise_ledger.jsonl`. `promise_check .` → 0 ERRORs, 85 orphan-artifact WARNs on `data/gen/*`, `scripts/gen/*`, `docs/gen_first_generation_report.md`, `docs/figures/gen_first_generation_provenance.png` — expected because the root ledger has 156 rows with no `M-GEN-1/*` events; adoption happens at fork post-merge integration under `_infra/adopt-fanout-artifacts-m-gen-1`. `org_check .` shows only pre-existing "figure in docs/" WARNs (`docs/figures/gen_first_generation_provenance.png` follows the same location convention as `pipeline_breadth_panel.png` and `tex_stage_by_stage_families.png`) and three root-file WARNs; none introduced by this branch.

**Handoff.** Merge report written to `/home/user/music-gen-instance/fork-00b3ae64444c/clone-0/merge_report.md`. The workspace-root `merge_report.md` is stale (fork `3a908edcb241` clone 2, cycle 8) and should be overwritten at fork rollup with the `00b3ae64444c` rollup once all sibling clones report in.

<verdict>validated</verdict>
