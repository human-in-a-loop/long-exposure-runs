---
title: "Music-Gen — Transcription Survey (M-TRANS-1), Clone 0 of Fork 3168fb0e47a1, Cycles 1–1"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Transcription Survey (M-TRANS-1), Clone 0 of Fork 3168fb0e47a1, Cycles 1–1

## Abstract

This branch executed the transcription survey stage of the Music-Gen pipeline. Using the synth-mix ground-truth stems produced by the earlier separation stage as clean-reference input, two independent transcribers were evaluated against exact reference note events for bass, "other" (piano triads), and drums, at three durations (30 s, 60 s, 90 s). The first transcriber is **basic-pitch 0.4.0**, installed in a quarantined virtual environment at `workspace/basic_pitch_venv/` and driven from the top-level interpreter over subprocess to keep its TensorFlow-2.15 / NumPy-1.26 pins out of the main environment. The second is a **librosa-family fallback** built from `librosa.pyin` (monophonic bass), a CQT peak-picking chord tracker (polyphonic "other"), and a spectral-flux onset detector with drum-band classification (drums). The alternative was chosen after a fetchability probe eliminated Crepe (PyPI HTTP 403 on the source dist) and rejected magenta 2.1.4 as too heavy for the branch's scope.

Note-level F1 was computed with `mir_eval.transcription.precision_recall_f1_overlap` for all nine (transcriber, stem, mix) cells per transcriber, published in `data/transcribe/results.tsv` with a `disclaimer` column marking the drum row as a lower bound (basic-pitch is a polyphonic-pitch model and returns zero notes on drums). A six-axis coverage matrix accompanies the F1 table with an explicit status flag on each axis: rhythm, melody, harmony, and dynamics are measured on this corpus; timbre is a placeholder self-similarity anchor; form is deferred (the synth mixes have no section structure); and vocals-to-text returns a documented `NO_VOCAL_STEM` sentinel because there is no vocal audio in the workspace this cycle.

The verdict on the pitch/rhythm side is **build, not adopt**. No single transcriber wins on every stem: the librosa-family fallback beats basic-pitch on monophonic bass (F1 1.000 vs 0.47) and is the only one that produces any drum output at all (F1 0.40 vs 0.00); basic-pitch beats the fallback on polyphonic "other" (F1 0.72 vs 0.32). The recommendation is a thin per-stem router that dispatches to the best available transcriber per stem type.

## 1. Objective and Scope

The Music-Gen prompt requires that every stage of the ingestion → separation → transcription → score → rules → generation pipeline first survey open-source options before any custom construction is entertained. This cycle discharges the transcription survey (milestone M-TRANS-1) on the pitch/rhythm side, using clean-reference stems produced upstream. It does **not** cover: (i) transcription from real polyphonic mixes (the rated corpus is still blocked at the egress boundary — see the campaign status note); (ii) vocal transcription against real voice audio; (iii) resynthesis-based timbre fidelity. Each of these is either impossible on this cycle's inputs or deferred to a later cycle with an explicit label in the coverage matrix.

## 2. Inputs

**Audio.** Three durations of the synthetic ground-truth mix produced by the separation stage — `synth_030s`, `synth_060s`, `synth_090s` — each with per-stem WAV files for drums, bass, and "other" (piano triads). All files are 44.1 kHz stereo. The mixes are built by tiling an 8-second loop and truncating to the target duration, so the reference tile policy is deterministic and known.

**Reference note events.** Regenerated deterministically from the loop-and-tile audio policy of `scripts/separation/synth_gt.py` into per-(mix, stem) JSONL note lists at `data/transcribe/reference/<mix>/<stem>.jsonl`, along with a manifest of SHA-256 hashes at `data/transcribe/reference/reference_manifest.json`. All twelve reference hashes reproduce bit-for-bit on rerun. Note counts scale exactly with duration: bass 15/30/45, "other" 45/90/135, drums 180/360/540 (from 4, 12, and 48 notes per 8-second loop respectively).

## 3. Transcribers Under Test

### 3.1 basic-pitch 0.4.0 (Spotify)

TensorFlow-based polyphonic-pitch model. Installed under `workspace/basic_pitch_venv/` with a full 62-package pin file (`requirements.frozen.txt`); the load-bearing pins are `basic-pitch==0.4.0`, `tensorflow==2.15.0.post1`, `numpy==1.26.4`. The venv is called only through `scripts/transcribe/_bp_call.py`, which is executed as a subprocess by the top-level `/usr/bin/python3`; a guard inside `_bp_call.py` resolves the running interpreter path and asserts it lives inside the venv before importing basic-pitch, so accidental invocation from the wrong environment fails loud.

Determinism was verified by rerunning `_bp_call.py` on the 30-second bass stem inside the venv and comparing byte-for-byte with the stored JSONL output: the SHA-256 matched exactly (44 notes both times, zero observed jitter — the target for this cycle was ±0.02 s tolerance, achieved was 0).

### 3.2 librosa-family fallback (alternative)

Selected after a fetchability ladder recorded in `data/transcribe/alternative_selection.jsonl`:

- **Crepe** — installation failed with HTTP 403 on the PyPI source distribution; not usable in this workspace.
- **magenta 2.1.4** with `note-seq` — fetchable, but the dependency footprint is disproportionate for a second transcriber intended as a diversity check. Recorded and rejected.
- **librosa-family (`librosa.pyin` + CQT peak picking + spectral-flux onsets)** — chosen. Every dependency was already resolved in the top-level environment from the heuristics milestone.

The fallback dispatches by stem: `pyin` for bass (monophonic), CQT peak-picking against an I–vi–IV–V triad template for "other" (polyphonic), and band-passed `librosa.onset.onset_detect` with argmax-band classification for drums.

## 4. Evaluation Protocol

Every (transcriber, mix, stem) cell is scored with `mir_eval.transcription.precision_recall_f1_overlap` using default onset/offset tolerances. Drum stems are scored with a documented **fake-Hz identity trick**: MIDI drum numbers are mapped to synthetic frequencies `100 + midi` Hz with `pitch_tolerance=0.5` cents. Identical drum numbers give zero cents of pitch difference and pass; adjacent drum numbers (e.g. kick 36 → snare 38) give roughly 25 cents and fail. This enforces exact drum-class identity through the pitched-note interface without a separate scoring path.

Runs are single-threaded (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`) so that basic-pitch's forward pass is deterministic.

## 5. Results

The full nine-cell-per-transcriber table lives in `data/transcribe/results.tsv`. The condensed picture, averaged across the three durations (F1 is stable across durations to three decimal places for every cell):

| Stem  | basic-pitch F1 | librosa-family F1 | Winner        | Margin |
|-------|----------------|-------------------|---------------|--------|
| bass  | 0.477          | 1.000             | librosa       | +0.523 |
| other | 0.725          | 0.325             | basic-pitch   | +0.400 |
| drums | 0.000 (lower bound) | 0.397        | librosa       | +0.397 |

Every drum row for basic-pitch carries an explicit `disclaimer` column in `results.tsv`: *"basic-pitch is polyphonic-pitch-oriented; F1 on drums is a LOWER BOUND."* Basic-pitch emits zero notes on drum audio, so precision is trivially reported as 1.000 and recall is 0.000 — the lower-bound label is what makes this row honest rather than misleading.

![Note-level F1 by transcriber and stem, averaged across three durations. Drum bar for basic-pitch is a documented lower bound.](data/transcribe/results_bar_chart.png)

Two caveats about the numerics belong here and not in a footnote:

- **The alternative's bass F1 of 1.000 is a corpus-triviality artifact.** The synth bass line is a monophonic sequence of sustained whole-note roots at 120 BPM; `pyin` nails it. Any evaluation against real, articulated bass lines will surface real gaps not visible here. Flag on file for when the rated audio arrives.
- **The alternative's "other" F1 of 0.325** reflects the fallback's polyphonic-chord approach against basic-pitch's per-note polyphony, on triad audio where per-note ground truth is dense. It is a real weakness of the fallback for that stem, not a scoring artifact.

## 6. Six-Axis Coverage Matrix

The full JSON with per-axis numerics is at `data/transcribe/six_axis_coverage.json`. Status meanings: **measurable** = a real metric is computed against a real reference on this corpus; **upgraded-to-measurable** = an axis that was originally scoped as a proxy and gained a real metric this cycle; **proxy-only** = an anchor is reported but does not evaluate transcription fidelity; **deferred** = not measurable on this corpus and no proxy attempted; **placeholder** = an API surface exists but there is no substrate to run it on.

| Axis            | What is measured                                                                                             | Status                    |
|-----------------|--------------------------------------------------------------------------------------------------------------|---------------------------|
| Rhythm          | Beat F-measure via `librosa.beat.beat_track` on the drums stem (F ≈ 0.99 all durations) plus the drum-onset F1 already in results.tsv | measurable                |
| Melody          | Note-level F1 from `mir_eval.transcription` on bass and "other" (in results.tsv)                             | measurable                |
| Harmony         | Triad detection via `librosa.chroma_cqt` peak template vs the I–vi–IV–V reference, scored with `mir_eval.chord.triads` — weighted accuracy 0.983 on every duration | measurable                |
| Timbre          | MFCC-13 mean-vector cosine self-similarity as a sanity anchor. The measurement is $\cos(\mathrm{mfcc}(x), \mathrm{mfcc}(x))$ and returns 1.0 modulo floating-point noise; the real timbre metric requires the resynthesis pipeline, deferred | proxy-only                |
| Dynamics        | `mir_eval.transcription_velocity.precision_recall_f1_overlap` on the bass stem (velocity tolerance ≈ 13/127 MIDI velocity units): librosa-family 1.000; basic-pitch ≈ 0.48 | upgraded-to-measurable    |
| Form            | Nothing — the synth mixes are uniform 8-second loop tiles with no section structure                          | deferred                  |
| Vocals-to-text  | `transcribe_vocals(wav)` returns the sentinel string `"NO_VOCAL_STEM"` on the silent-vocals input by design  | placeholder               |

The timbre row is deliberately labelled `proxy-only`. Under the hood it is a self-cosine that trivially yields unity, and this cycle's audit flagged the label as overstating the measurement — the honest phrasing is that the file exists as a sanity anchor and the axis remains not-yet-measured. Renaming the JSON key from `cos_self` to `sanity_anchor` is on the next-cycle probe list.

## 7. Adopt-or-Build Verdict

**Build.** No single transcriber wins on every stem, and the cross-stem margins are large: 0.52 on bass in favour of the librosa fallback, 0.40 on "other" in favour of basic-pitch, and 0.40 on drums in favour of the fallback (with basic-pitch's zero being a lower bound, not a real zero). The right structure is a thin router with signature `transcribe(stem_wav, stem_type) → midi` that dispatches basic-pitch to polyphonic pitched stems, `pyin` to monophonic pitched stems, and a per-band drum-onset detector to drums. The router itself is a few dozen lines; the underlying transcribers stay as they are.

This is the campaign's first build verdict — the separation stage adopted `htdemucs`, and all earlier stages either adopted an existing tool outright or used stdlib-only construction with no survey needed.

## 8. Environmental Hygiene

Basic-pitch's TensorFlow 2.15 / NumPy 1.26 requirements are incompatible with several packages the top-level environment already hosts (notably the PANNs classifier, librosa 0.11 for the heuristics stage, and the texture-panel embedding stack). The pattern used here — a fully quarantined virtual environment invoked over subprocess with a guard on the interpreter path — resolves the conflict without downgrading anything in the top-level environment. It is a reusable pattern for future milestones that surface similarly incompatible pins.

The venv is reproducible: `workspace/basic_pitch_venv/requirements.frozen.txt` pins all 62 packages, and the subprocess call path is a single 25-line script.

## 9. Determinism and Verification

Determinism was verified along two independent axes and confirmed by an independent audit:

1. **Reference recovery.** All twelve reference JSONL SHA-256 hashes recorded in `reference_manifest.json` reproduce bit-for-bit when regenerated from the tile policy in `synth_gt.py`.
2. **Model invocation.** Rerunning basic-pitch on the 30-second bass stem inside the quarantined venv produced a byte-identical JSONL to the stored output (44 notes both times).
3. **F1 recomputation.** Directly calling `mir_eval.transcription.precision_recall_f1_overlap` on the stored basic-pitch bass@030s JSONL against the reference JSONL yielded P = 0.3182, R = 0.9333, F1 = 0.4746, exactly matching the corresponding row of `results.tsv`.

## 10. Known Limitations and Next-Cycle Probes

Priorities are ordered by expected F1 impact:

1. **Basic-pitch octave-doubling suppression.** Post-process to drop octave-doubled co-onset notes. Expected effect: bass F1 0.48 → ~0.9, "other" F1 0.72 → ~0.85. Cheapest high-value fix.
2. **Per-band drum onset detector.** Three band-passed `librosa.onset.onset_detect` calls with argmax bin per hit, replacing the single-detector approach; should lift alternative drum recall above 0.33.
3. **Per-stem router prototype.** The concrete implementation of the build verdict.
4. **Timbre axis upgrade.** Wire fluidsynth resynthesis into the loop so `timbre` earns its `proxy-only` label instead of running a trivial self-similarity. In the interim, rename `cos_self` to `sanity_anchor` in `six_axis_coverage.json` to remove the wording overstatement flagged by this cycle's audit.
5. **Retry Crepe and magenta** when the workspace egress policy relaxes — the current librosa-family fallback is honestly labelled as low-diversity.

The alternative-bass F1 of 1.000 will not survive contact with real, articulated bass audio; the finding should not be read as a universal claim about `pyin`.

## 11. Files Produced This Cycle

- `docs/transcription_survey_report.md` — the primary artifact of this branch.
- `scripts/transcribe/reference_events.py` — deterministic reference generator.
- `scripts/transcribe/_bp_call.py` — subprocess entrypoint into the quarantined basic-pitch venv, with interpreter-path guard.
- `scripts/transcribe/eval_transcription.py` — mir_eval wrapper, including the fake-Hz drum identity trick.
- `scripts/transcribe/six_axis_coverage.py` — six-axis matrix builder.
- `workspace/basic_pitch_venv/` — quarantined environment, with `requirements.frozen.txt`.
- `data/transcribe/reference/` — twelve reference JSONLs plus SHA manifest.
- `data/transcribe/basic_pitch/`, `data/transcribe/alternative/` — nine JSONLs each.
- `data/transcribe/results.tsv` — the F1 table with the `disclaimer` column.
- `data/transcribe/velocity/velocity_f1.tsv` — bass velocity F1 for the dynamics axis.
- `data/transcribe/six_axis_coverage.json` — the coverage matrix.
- `data/transcribe/alternative_selection.jsonl` — the fetchability ladder.
- `data/transcribe/results_bar_chart.png` — the summary figure embedded above.
- `tests/test_integration_cross_branch.py` — extended with M-TRANS-1 checks (venv path, interpreter guard, basic-pitch pin, reference-manifest reproduction, results.tsv shape and header, lower-bound disclaimer presence, six-axis section presence, non-factor isolation scan). Full suite passes.

## 12. Status

The milestone M-TRANS-1 is discharged on the pitch/rhythm side with the six-axis coverage matrix and a build verdict. The sub-milestones for basic-pitch integration, alternative-transcriber selection, and the six-axis coverage matrix are recorded in this branch's shadow ledger and land on merge. The prior manager item covering the basic-pitch dependency conflict was resolved by the quarantined-venv approach and does not re-emit.

## References

[1] Bittner, R. M. et al. *A Lightweight Instrument-Agnostic Model for Polyphonic Note Transcription and Multipitch Estimation*, ICASSP 2022 — basic-pitch.
[2] Raffel, C. et al. *mir_eval: A Transparent Implementation of Common MIR Metrics*, ISMIR 2014.
[3] Mauch, M. and Dixon, S. *pYIN: A Fundamental Frequency Estimator Using Probabilistic Threshold Distributions*, ICASSP 2014.
[4] McFee, B. et al. *librosa: Audio and Music Signal Analysis in Python*, SciPy 2015.

## Appendix: Implementation Details

**Session references (this cycle).**

- Researcher session: `aff8ffcc-5663-4cdb-8c7c-0eaf93894462`
- Worker session: `6418d3f6-b78b-41b6-bb9e-5d674bc92e13`
- Auditor session: `5523fd16-3a44-4edb-bdc7-c1f1b40a0a01`
- Fanout fork: `3168fb0e47a1`, clone 0.

**Ledger state at end of cycle (this branch's shadow ledger).**
`M-TRANS-1` sub-milestones `basic-pitch`, `alternative`, `six-axis-coverage` recorded; the M-TRANS-1 rollup is queued for promotion to `validated/high` on fanout merge. The 27 orphan-artifact warnings surfaced by `promise_check` at branch scope are expected — the artifacts live in the clone-0 shadow ledger and resolve when the root conductor folds them into the top-level ledger under `_infra/adopt-fanout-artifacts-m-trans-1`. Two sibling-clone-owned errors on `M-RULES-1/schema` and `M-EAR-1/preparation` are not this branch's and are flagged for the root conductor.

**Cross-branch integration test.** `tests/test_integration_cross_branch.py` §12 (M-TRANS-1) checks all pass in a clean run of the full suite: venv path, venv interpreter, basic-pitch pin, reference manifest reproduction, results-TSV shape and header, lower-bound disclaimer, report presence with lower-bound disclaimer plus six-axis section, seven axis rows present, non-factor isolation scan clean.

**Test summary.** Full suite passes with zero failures.

**Audit outcome.** Validated. Two MODERATE findings recorded and non-blocking: (i) the timbre axis label `proxy-only` overstates the underlying self-cosine measurement (substance is honest; rename planned); (ii) the alternative-bass F1 of 1.000 is a corpus-triviality artifact on the synth ground truth (disclosed in §5 and §8 above). One MINOR wording nit on a bar-duration derivation was logged and not fixed.

**Cross-reference map (values that flow out of this branch).**
- `scripts/transcribe/_bp_call.py` (basic-pitch invocation contract) → consumed by future per-stem router.
- `data/transcribe/reference/*` (reference JSONL + manifest) → reused by any future transcription evaluation on the synth-mix corpus.
- Preprocessing rule "44100 Hz stereo before any separator" (inherited from separation stage) also applies to transcription inputs.
- Six-axis coverage matrix schema → reused by downstream generation-quality evaluation.
