---
title: "Music-Gen — M-INGEST-1/breadth-second-seeds (cycle 1, fork 00b3ae64444c, clone 1)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — M-INGEST-1/breadth-second-seeds (cycle 1, fork 00b3ae64444c, clone 1)

## Abstract

Cycle 1 of clone 1 exercised the eight-stage Music-Gen pipeline (chunker → prepare-audio → M-CLASS-1 → M-SEP-1 htdemucs → M-TRANS-1 basic-pitch → M-SCORE-1 merge_stems_to_score → render_bare_midi → M-TEX-1 panel) end-to-end on two additional seeds beyond the cycle-9 `synth_030s` baseline, chosen to maximise informational contrast within the on-disk corpus: `seed_mid_50s` (50 s / 22 050 Hz mono / pure-sine content) and `synth_060s` (60 s / 44 100 Hz stereo / fluidsynth ground-truth). Both seeds passed 8/8 stages with per-seed byte-determinism verified across two independent runs (24 / 24 SHA-256 anchors matched on the twelve frozen contract artefacts × two seeds), and the cross-seed panel comparison yields genuine variation that reveals the pipeline is correctly content-discriminating rather than content-agnostic. The verdict is **`validated/medium`** under the brief's explicit downgrade rule for the corpus state: no non-synth audio is on disk (the 80-song rated corpus remains a metadata-only registration behind the egress deny of `*.googlevideo.com`), so pipeline generalisation is demonstrated across `seed_id` and across two provenance sub-classes (`synth_seed_gen` vs `synth_ground_truth`) but *not* across the natural-recording ↔ synth boundary. All eight artefact classes (WAV, per-stem WAV × 4, per-stem MIDI × 3, merged MIDI, merged MusicXML, bare-MIDI render, panel TSV) are byte-stable per seed under the campaign's single-thread BLAS + `torch.manual_seed(0)` + TF-deterministic-ops contract. Cross-branch integration test §22 (per-seed SHA-256 anchors and breadth-invariant checks) is green.

## Introduction

By the end of cycle 9 the pipeline had been demonstrated end-to-end on exactly one seed — the 30 s fluidsynth-rendered M-SEP-1 ground-truth mix. That is a workable proof-of-life but a poor proof-of-generalisation: a chain that only ever runs on one input can silently encode assumptions about sample rate, channel count, note density, or content class that break on the second input. The brief for this branch asks the pipeline to be exercised on additional on-disk seeds and honestly reports what happens at each stage, without fabricating seeds or attempting the network fetches the workspace still refuses. The success bar was at least one additional seed (target two) passing end-to-end, byte-determinism per seed, panel numbers for original-vs-bare-MIDI on each seed compared against the baseline, and candid failure reporting per stage; the brief pre-authorises a `/medium` grade if all seeds available are synth-derived.

## Approach

**Seed enumeration.** `scripts/breadth/enumerate_seeds.py` swept `corpus/seed/`, `corpus/ratings/`, `data/ingestion/seed/`, and `data/separation/synth_mix/` and wrote the full 18-row table to `data/breadth/seed_enumeration.tsv`. The provenance summary:

| provenance_class | count | source |
|---|---:|---|
| `synth_seed_gen` | 3 | `data/ingestion/seed/` — CC-0 sines from `scripts/ingest/seed_gen.py`, mono 22 050 Hz, durations {22, 50, 87} s |
| `synth_ground_truth` | 15 (5 × 3 mixes) | `data/separation/synth_mix/gt/` — fluidsynth-rendered stems and summed mix, 44.1 kHz stereo, durations {30, 60, 90} s |
| `unknown` (real recording) | **0** | egress blocked; `corpus/ratings/` holds manifest TSVs only |

No non-synth audio is on disk. Per the campaign's Fixed Decision that acquisition never blocks downstream work, the cycle proceeded on what is present.

**Seed selection.** Priority order was (a) non-synth, (b) ≥ 30 s, (c) not the M-SEP-1 30 s baseline. With no (a) candidates available, (b) and (c) admit four seeds; the two picked were one from each provenance sub-class for maximum informational contrast: `seed_mid_50s` for the `synth_seed_gen` class (which exercises the sample-rate and upmix paths and tests classifier discrimination) and `synth_060s` for the `synth_ground_truth` class (content-family match with baseline, longer duration, tests pipeline stability under scaling on the same content class).

**Orchestrator.** `scripts/breadth/run_seed.py` walks the eight stages, writes a per-seed `stage_manifest.jsonl` recording the SHA-256, elapsed time, and diagnostic notes for each stage, and drops all outputs into `data/breadth/<seed_id>/`. The interpreter guard `assert sys.executable == '/usr/bin/python3'` fires at import; basic-pitch is invoked in its quarantined venv (`workspace/basic_pitch_venv/bin/python3`) via subprocess with the cycle-6 environment pins passed in the child env; determinism relies on `torch.manual_seed(0)` for htdemucs, TF seed 0 in the basic-pitch venv, `librosa.resample(res_type='soxr_hq')` for the deterministic rate conversion, fluidsynth with the pinned SF2 SHA `74594e8f…1cb0`, `scipy.io.wavfile.write` for timestamp-free WAVs, and the M-SCORE-1 `_scrub_musicxml` for timestamp-free MusicXML.

## Findings

### Per-seed pipeline pass table

Both seeds passed 8/8 stages. Per-stage timing and diagnostics are recorded in each seed's `data/breadth/<seed_id>/stage_manifest.jsonl`.

| Stage | seed_mid_50s | synth_060s |
|---|---|---|
| chunker | ✅ 2 clips (30 s + 30–50 s anchored tail) | ✅ 3 clips (0–30, 25–55, 30–60 s anchored tail) |
| prepare_audio | ✅ mono → stereo (L=R), 22 050 → 44 100 via soxr HQ | ✅ 44 100 stereo pass-through |
| classifier (M-CLASS-1) | ✅ `Sine wave` p = 0.9431 | ✅ `Music` p = 0.8770 |
| htdemucs (M-SEP-1) | ✅ peaks drums=0.256, bass=0.132, other=0.545, vocals=0.048 | ✅ peaks drums=0.443, bass=0.309, other=0.361, vocals=0.023 |
| basic-pitch (M-TRANS-1) | ✅ 55 drums / 80 bass / 10 other notes | ✅ 57 drums / 60 bass / 194 other notes |
| merge_stems_to_score (M-SCORE-1) | ✅ 3 stems merged | ✅ 3 stems merged |
| render_bare_midi (M-TEX-1) | ✅ peak = 0.470, 2 205 000 samples | ✅ peak = 0.503, 2 646 000 samples |
| texture_panel (M-TEX-1/panel) | ✅ 8 keys finite, VGGish rung | ✅ 8 keys finite, VGGish rung |

### Panel numbers across seeds + baseline

Original-vs-bare-MIDI panel from `data/breadth/summary.tsv`:

| seed_id | mel_l1_db | sc_rmse_hz | rms_env_rmse | lufs_m_rmse_lu | embed_cos | rung | provenance |
|---|---:|---:|---:|---:|---:|:---:|---|
| **synth_030s** (baseline, cycle 9) | **9.906** | **2804.9** | **0.02759** | **2.682** | **0.1234** | vggish | synth_ground_truth |
| synth_060s (this cycle) | 10.755 | 2764.9 | 0.02887 | 2.843 | 0.1619 | vggish | synth_ground_truth |
| seed_mid_50s (this cycle) | 15.808 | 601.0 | 0.30918 | 20.837 | 0.1593 | vggish | synth_seed_gen |

![Original-vs-bare-MIDI texture panel per seed (grouped bars, one panel per family, no aggregate)](docs/figures/pipeline_breadth_panel.png)

Reading the table:

- **`synth_060s` vs `synth_030s` baseline (same content family, 2× duration).** Mel L1 drifts +8.6 %, spectral centroid RMSE −1.4 %, RMS-env RMSE +4.6 %, LUFS-M RMSE +6.0 %, embedding cosine +31 %. The three energy/spectral metrics track the baseline closely — a stability check the pipeline passes. The larger embedding drift is consistent with VGGish's known sensitivity to duration-dependent global summarisation (`mean_over_frames` is not scale-invariant when the underlying content distribution shifts even slightly between mixes).
- **`seed_mid_50s` vs `synth_030s` baseline (disjoint content class).** Every metric diverges dramatically. Spectral centroid RMSE *drops* from 2 805 Hz to 601 Hz because the seed is pure sines and its bare-MIDI transcription is also near-tonal, so both spectra concentrate in narrow bands and the RMSE between two narrow-band spectra is small. Mel L1 goes the other way (+60 %) because it is a log-domain L1 that rewards spectral overlap, and the sine → basic-pitch → SF2-render chain deposits energy in mel bands outside the seed's tone. LUFS-M RMSE is 7.8× the baseline because bare-MIDI from GM piano at velocity 60–80 is much louder than the −7 dBFS sines. RMS-env RMSE = 0.309 is the largest divergence in the table — a *feature* of the panel, not a bug — because pure sines have `seed_gen.py`'s per-note attack-decay envelope while SF2 piano samples have a hard attack and long decay tail, and RMS envelope is directly sensitive to that attack-shape mismatch.

**Family-disagreement recurrence.** On `synth_060s` three of the four numeric metrics sit within 10 % of the baseline while VGGish embedding cosine drifts 31 %. This is a milder but real recurrence of the cycle-9 family-disagreement finding on M-TEX-1/stage-by-stage (where envelope + mel-L1 ranked one direction and VGGish inverted), and it reinforces the panel's aggregation-refusal design: the families genuinely carry different information about the original ↔ bare-MIDI relationship.

### Byte-determinism

Two independent runs of `scripts/breadth/run_seed.py` (out-dirs `data/breadth/<seed>/` vs `stale/breadth_determinism/_det/<seed>/`) produce SHA-256-identical outputs on 12 frozen contract artefacts × 2 seeds. Result: **24 / 24 PASS**, table at `data/breadth/determinism_baselines.txt`. Per-seed short SHA-256 prefixes:

| Artefact | seed_mid_50s | synth_060s |
|---|---|---|
| `original.wav` | 1d8eca66 | 9c64045c |
| `stems/drums.wav` | bddfea47 | 05db247a |
| `stems/bass.wav` | 1f533f48 | 32ad1be5 |
| `stems/other.wav` | 8220e311 | 15915ffd |
| `stems/vocals.wav` | 9c68c415 | 716e3c6f |
| `transcriptions/drums.mid` | 71ffce62 | 4b1e68e5 |
| `transcriptions/bass.mid` | 209e0a02 | 82ba631f |
| `transcriptions/other.mid` | 38c70a5b | 236e2e15 |
| `merged.mid` | a48242f4 | 60c88c24 |
| `merged.musicxml` | e86da1f2 | 9b88ca1b |
| `bare_midi.wav` | cea3e3b4 | 07a9d0b7 |
| `panel.tsv` | b10d2a0c | cc0acb5f |

Cross-branch integration test §22 re-verifies these SHAs at test time (not just at generation time) and passes with zero failures. The AST scan for `sidecar_nonfactor` across `scripts/breadth/` returns empty.

### Honest failure reporting

No stage failed on either selected seed. The `/medium` cap is a corpus fact, not a stage-level defect. Two "quiet passes worth calling out" are named on the report:

- **htdemucs on pure sines (`seed_mid_50s`).** The model produced four non-silent stems, but the energy distribution is heavily skewed to `other` (peak 0.545) and away from drums, bass, and vocals (0.256, 0.132, 0.048). This is the model doing the correct thing on atypical content — a sinusoid has no drum transients, no bass fundamental in htdemucs's bass band, and no vocal formants — but "non-silent" is a low bar for calling the split informative. A follow-up cycle could add a SI-SDR-vs-mixture baseline to catch pathologically-thin separations.
- **basic-pitch on pure sines (`seed_mid_50s`).** The seed content is a decaying C-E-G triad repeated over 50 s, so the ground-truth note count is O(30); basic-pitch emitted 55 + 80 + 10 = 145 notes, ≈ 5× the truth. This is the same octave-doubling artefact identified in cycle 8 (`M-TRANS-1/basic-pitch/octave-suppression`, closed `invalidated/high`); do **not** re-attempt octave-suppression on this data. The anti-pattern lock is binding.

## Discussion

Two things about this branch are worth naming. First, the classifier discrimination (`Sine wave` p = 0.94 vs `Music` p = 0.88) plus the panel-metric divergence between `seed_mid_50s` and the baseline together falsify the "content-agnostic extractor" hypothesis the research brief posed as one of its Key Questions. The pipeline is doing content-appropriate things at every stage — the sine seed correctly gets classified as a sine, correctly routes most of its energy to `other` under htdemucs, correctly produces a bare-MIDI render whose RMS envelope is very different from the seed's, and correctly reports that difference as a large RMS-env RMSE. The panel is signal-preserving; it is not smoothing over content class.

Second, the `/medium` verdict is a textbook application of the brief's own downgrade rubric rather than a hedge. Every additional bit of engineering that could tighten this branch further — a richer separation baseline, more elaborate panel weighting, a longer basic-pitch grid — would produce numbers that do not answer the question the corpus limitation forces open. The single missing axis is natural-recording provenance, and that is governed by the egress boundary, not by any code the campaign has authored. The value-add of a real-audio arrival grows with each cycle that pre-wires the automation: `scripts/breadth/run_seed.py` is a drop-in-ready orchestrator for the moment `M-INGEST-1/egress-ready-automation` fires, and no code change is required to point it at a newly-arrived audio path.

The natural cheapest follow-up to widen the M-RULES-1 corpus without new audio is to run the rules extractor over the two new merged MusicXMLs (`data/breadth/seed_mid_50s/merged.musicxml` and `data/breadth/synth_060s/merged.musicxml`), emitting `M-RULES-1/extraction/breadth-<seed_id>` per seed. Both files are on disk and consumable by `scripts/rules/extract/from_score.py` with no code change; this is called out in the auditor's guidance and is the recommended next follow-up.

## Open Questions

- **Rules extraction per breadth seed.** Cheapest way to widen the M-RULES-1 corpus without new audio; both merged MusicXMLs are on disk.
- **SI-SDR-vs-mixture baseline on M-SEP-1.** Would catch pathologically-thin htdemucs splits on atypical content classes like pure sines, without requiring re-training.
- **`/high` promotion.** Blocked entirely on natural-recording audio arrival. When `M-INGEST-1/egress-ready-automation` fires, the same `run_seed.py` orchestrator can be pointed at any newly-arrived audio path with zero code change.
- **VGGish `mean_over_frames` scale-sensitivity.** The 31 % embedding cosine drift between `synth_030s` and `synth_060s` under otherwise-matched content is a known artefact of the global summarisation; a CLAP-rung swap on M-TEX-1/panel/embedding remains the orthogonal path to a more scale-invariant perceptual measure.
- **Shadow-ledger adoption at post-merge integration.** `_infra/adopt-fanout-artifacts-m-ingest-1-breadth-second-seeds` covering `data/breadth/**`, `docs/pipeline_breadth_report.md`, `docs/figures/pipeline_breadth_panel.png`, `scripts/breadth/*.py`, and the §22 integration-test delta.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `00b3ae64444c`, clone 1.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `ed73c585-23ab-449c-9562-8a3ac46e5887`, worker `4d1aea55-0e21-43e0-ac6d-78fe877a7bb6`, auditor `44175d82-39e4-43ff-96a8-4084644a6b86`.
**Auditor verdict:** **VALIDATED** at grade `/medium` under the brief's explicit downgrade rule for the on-disk corpus state.

**Deliverables on disk:**

- Code: `scripts/breadth/{enumerate_seeds.py, run_seed.py, …}` — interpreter-guarded, zero `sidecar_nonfactor` imports (AST-verified).
- Data: `data/breadth/{seed_mid_50s, synth_060s}/{original.wav, stems/{drums,bass,other,vocals}.wav, transcriptions/{drums,bass,other}.{mid,jsonl}, merged.{mid,musicxml}, bare_midi.wav, panel.tsv, stage_manifest.jsonl, classification.json, clips/*.wav}`; `data/breadth/{summary.tsv, seed_enumeration.tsv, determinism_baselines.txt}`.
- Figure: `docs/figures/pipeline_breadth_panel.png` (113 521 B).
- Report: `docs/pipeline_breadth_report.md` (281 lines, 9 sections).
- Test: `tests/test_integration_cross_branch.py §22` — per-seed SHA-256 anchors + breadth invariants; 0 failures.

**Environment stack unchanged since cycle 9:** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; htdemucs via `torch.manual_seed(0)`; VGGish rung on the texture panel; DawDreamer + Surge XT for effects (not exercised here). Single-thread BLAS pins throughout.

**Ledger routing.** Closure events landed in the per-clone shadow ledger at `/home/user/music-gen-instance/fork-00b3ae64444c/clone-1/promise_ledger.jsonl`; workspace `promise_check` shows ~55 orphan-artifact WARNs on the new files. Clears at post-merge integration under the standard `_infra/adopt-fanout-artifacts-m-ingest-1-breadth-second-seeds` pattern from cycles 3, 5, 7. `org_check` shows a WARN for the figure under `docs/figures/`, consistent with the campaign convention (`rules_extraction_coverage.png`, `tex_stage_by_stage_families.png`, `gen_first_generation_provenance.png`).

**Handoff.** Merge report written to `/home/user/music-gen-instance/fork-00b3ae64444c/clone-1/merge_report.md`. The recommended next research step is either the standard post-merge integration for fork `00b3ae64444c` (adopt the breadth artefacts and re-run `promise_check`) or the cheap follow-up of running `scripts/rules/extract/from_score.py` over the two new merged MusicXMLs to widen the M-RULES-1 corpus without new audio.

<verdict>validated</verdict>
