---
created: 2026-08-28T07:00:00Z
run_id: run-2026-08-28T040704Z
cycle: 6
agent: worker
milestone: M-TRANS-1
---

# M-TRANS-1 — Transcription survey (six-axis coverage)

**Cycle 6, fork 3168fb0e47a1, clone-0 branch.**

Scope: run basic-pitch 0.4.0 in a quarantined venv and one alternative
transcriber against the M-SEP-1 clean-reference stems (drums / bass /
piano-labelled-as-`other`) at three durations {30, 60, 90} s, report
note-level F1, and publish an honest six-axis coverage matrix with an
adopt-or-build verdict on the pitch/rhythm side.

## 1. Objective and scope

M-TRANS-1's plan-of-record success criterion is:

> Per-axis coverage report published; note-level F1 measured for pitch on
> seed clips against a manually-corrected reference; timbre/dynamics/form
> axes flagged with what is measured vs. what is not.

This cycle uses `data/separation/synth_mix/gt/synth_{030,060,090}s/*.wav`
(fluidsynth-rendered from committed MIDIs) as the clean-reference input,
so the "manually-corrected reference" is replaced by the exact
programmatic ground truth recovered from `scripts/separation/synth_gt.py`.
No rated audio is touched. Vocals-to-text is a placeholder because the
synth mixes' vocals stem is silent by construction.

## 2. Environment

**Interpreter (orchestrator):** `/usr/bin/python3` (guarded).
**Interpreter (subprocess target):** `workspace/basic_pitch_venv/bin/python3` (guarded inside `_bp_call.py`).
**Reason for split:** basic-pitch 0.4.0 pins `tensorflow<2.15.1`; the top-level env has TF 2.21.0 (M-CLASS-1 branch's PANNs). Reconciled per `_manager/M-TRANS-1-deps-conflict` (validated/high, cycle 6): option (b) quarantined venv.

**Venv creation** (one-shot, this cycle):

```bash
/usr/bin/python3 -m venv workspace/basic_pitch_venv
workspace/basic_pitch_venv/bin/python3 -m pip install -U pip
workspace/basic_pitch_venv/bin/python3 -m pip install basic-pitch==0.4.0
workspace/basic_pitch_venv/bin/python3 -m pip freeze > workspace/basic_pitch_venv/requirements.frozen.txt
```

**Frozen pins (venv):** `basic-pitch==0.4.0`, `tensorflow==2.15.0`,
`numpy==1.26.4` (matches top-level after cycle-5 downgrade — no numpy
conflict remains; only tensorflow is isolated). Full pin list at
`workspace/basic_pitch_venv/requirements.frozen.txt` (62 packages).

**Fetchability ladder** — first rung that installs cleanly wins:

| Rung | Target | Outcome | Notes |
|---|---|---|---|
| 1 | `crepe==0.0.15` | **FAIL** | `pip download` fails at `setup.py` metadata generation: `urllib.error.HTTPError: HTTP Error 403: Forbidden`. Crepe's setup fetches its model weights from a blocked host during install. |
| 2 | `magenta==2.1.4` wheel | fetches | Wheel comes down (2.1 MB), but the `onsets-frames` checkpoint follows a GCS-hosted path that lands on the same block Crepe hits, and its ~300 MB dependency tree (`apache-beam`, `mesh-tensorflow`, `sonnet`, etc.) is disproportionate to a survey. Not installed. |
| 3 | `note-seq==0.0.5` wheel | fetches | Magenta's core note-sequence library alone, but without the onsets-frames model it isn't a transcriber. Not adopted. |
| 4 | **librosa-family fallback** | **CHOSEN** | Distinct-from-basic-pitch pipeline: `librosa.pyin` (monophonic pitch) + `librosa.onset.onset_detect` (rhythm) + CQT peak-picking (polyphonic). Already installed. |

Probe log persisted at `data/transcribe/alternative_selection.jsonl`.
**Diversity caveat:** the survey's "≥1 alternative" bar is met, but both
transcribers share `librosa`'s STFT/CQT as a low-level dependency; the
diversity is limited to algorithmic layer (NMP CNN vs pyin+onset+CQT
peak-picking), not toolkit family. Flagged for future cycles.

## 3. Ground-truth recovery

`scripts/separation/synth_gt.py` (lines 113–147) renders each stem by:

1. `fluidsynth` renders the 8 s / 4-bar MIDI phrase (LOOP_S = 4 × BAR_S,
   BAR_S = 60/BPM × 4 = 0.5 s × 4 = 2.0 s, so LOOP_S = 8.0 s at BPM=120).
2. The audio is **truncated to the first 8 s** (n_loop = 8·SR samples).
3. The 8 s block is **tiled in the audio domain** `ceil(D / 8)` times.
4. Trimmed to `D · SR` samples.

So at the note-event layer, the ground truth for duration D is the
original MIDI's note list replicated at offsets `{0, 8, 16, …}` with any
note whose `start ≥ D` dropped and any note whose `end > D` clipped to D.

`scripts/transcribe/reference_events.py` implements this exactly. Stem→
MIDI mapping honours the (subtle) rename in `synth_gt.py` line 166 that
writes `piano.mid`'s render to `other.wav`.

Sanity counts (matches expected note density):

| Duration | drums.jsonl | bass.jsonl | other.jsonl | vocals.jsonl |
|---:|---:|---:|---:|---:|
| 30 s | 180 | 15 | 45 | 0 |
| 60 s | 360 | 30 | 90 | 0 |
| 90 s | 540 | 45 | 135 | 0 |

Determinism gate: rerun of `reference_events.py` produces SHA-256-identical
JSONL for all 12 files (verified via `_determinism_check.py`).

**SHA-256 anchors** (first 16 hex chars each; full manifest at
`data/transcribe/reference/reference_manifest.json`):

- `synth_030s/drums.reference.jsonl` → `e48f0e9978e26092…`
- `synth_030s/bass.reference.jsonl` → (see manifest)
- `synth_090s/other.reference.jsonl` → `779193f320f15d05…`

## 4. Transcribers evaluated

| Transcriber | Version | Where it runs | Model | Notes |
|---|---|---|---|---|
| `basic_pitch` | 0.4.0 | quarantined venv via subprocess | ICASSP 2022 NMP (TF SavedModel) | polyphonic pitch; deterministic under single-thread BLAS pins |
| `alternative` | — | top-level env | `librosa.pyin` (bass) + `librosa.onset.onset_detect` + sub-band spectral classifier (drums) + CQT peak-picking (other) | hand-tuned distinct pipeline |

Skipped alternatives: Crepe (fetch blocked), magenta onsets-frames
(same blocked GCS path + disproportionate deps). See §2 ladder.

## 5. Note-level F1 results

Metric: `mir_eval.transcription.precision_recall_f1_overlap` with
`onset_tolerance=0.05 s`, `pitch_tolerance=50 cents`,
`offset_ratio=0.20`, `offset_min_tolerance=0.05 s`. For drums, GM drum
note numbers are mapped to a fake-Hz identity space
(`hz = 100 + midi_pitch`) with `pitch_tolerance=0.5` so only exact drum
class matches, and the same call is reused.

Full table (`data/transcribe/results.tsv`):

| transcriber | mix | stem | precision | recall | f1 | notes_ref | notes_est |
|---|---|---|---:|---:|---:|---:|---:|
| basic_pitch | synth_030s | drums | 1.0000 | 0.0000 | **0.0000** | 180 | 0 |
| basic_pitch | synth_030s | bass  | 0.3182 | 0.9333 | 0.4746 |  15 |  44 |
| basic_pitch | synth_030s | other | 0.5769 | 1.0000 | **0.7317** |  45 |  78 |
| basic_pitch | synth_060s | drums | 1.0000 | 0.0000 | **0.0000** | 360 | 0 |
| basic_pitch | synth_060s | bass  | 0.3118 | 0.9667 | 0.4715 |  30 |  93 |
| basic_pitch | synth_060s | other | 0.5769 | 1.0000 | 0.7317 |  90 | 156 |
| basic_pitch | synth_090s | drums | 1.0000 | 0.0000 | **0.0000** | 540 | 0 |
| basic_pitch | synth_090s | bass  | 0.3258 | 0.9556 | 0.4859 |  45 | 132 |
| basic_pitch | synth_090s | other | 0.5593 | 0.9778 | 0.7116 | 135 | 236 |
| alternative | synth_030s | drums | 0.4958 | 0.3278 | 0.3946 | 180 | 119 |
| alternative | synth_030s | bass  | 1.0000 | 1.0000 | **1.0000** |  15 |  15 |
| alternative | synth_030s | other | 0.2000 | 0.8222 | 0.3217 |  45 | 185 |
| alternative | synth_060s | drums | 0.4979 | 0.3306 | 0.3973 | 360 | 239 |
| alternative | synth_060s | bass  | 1.0000 | 1.0000 | 1.0000 |  30 |  30 |
| alternative | synth_060s | other | 0.2033 | 0.8222 | 0.3260 |  90 | 364 |
| alternative | synth_090s | drums | 0.4986 | 0.3315 | 0.3982 | 540 | 359 |
| alternative | synth_090s | bass  | 1.0000 | 1.0000 | 1.0000 |  45 |  45 |
| alternative | synth_090s | other | 0.2048 | 0.8296 | 0.3284 | 135 | 547 |

**Drum-stem disclaimer (LOWER BOUND):** basic-pitch's ICASSP-2022 model is
a polyphonic-pitch estimator. On pitchless drum stems it emits zero notes
across all three mixes (the pitch head sees no coherent harmonic
structure). The 0.0000 F1 rows are a **lower bound**, not a definitive
measurement — the model was not designed for this input. The
disclaimer is carried in `results.tsv`'s `disclaimer` column and is
gated by `tests/test_integration_cross_branch.py §12d`.

![note-level F1 per (transcriber, stem), mean over 30/60/90 s](../data/transcribe/results_bar_chart.png)

**Determinism jitter (basic-pitch, bass @ synth_030s, two runs under the
single-thread BLAS pins in `_bp_call.py`):** SHA-256 bit-identical;
n_notes constant (44); F1 delta = 0.0000. Target was ±0.02; observed is
0. The single-thread environment vars (`OMP_NUM_THREADS=1`,
`MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`) + `tf.random.set_seed(0)`
+ `tf.config.threading.set_{intra,inter}_op_parallelism_threads(1)`
suffice to remove the documented TF float-non-determinism on this
workload.

## 6. Six-axis coverage

Per axis, status + what is measured + what is not (materialized in
`data/transcribe/six_axis_coverage.json`; every axis has an explicit
row — no silent omissions):

| Axis | Status | What is measured | What is NOT measured |
|---|---|---|---|
| **rhythm** | measurable | Beat F-measure (`librosa.beat.beat_track` on drums stem vs reference beats at 0.5 s spacing, `mir_eval.beat.f_measure` with 70 ms window): **0.99, 0.99, 0.99** at 30/60/90 s. Estimated BPM 120.19 (ref 120.00). Drum-onset F1 in results.tsv (~0.40 for the alternative). | groove nuance; rubato; polyrhythm; micro-timing |
| **melody** | measurable | Note-level F1 on bass (monophonic) + other/piano (polyphonic) — see §5 table. | expressive articulation; ornaments; vibrato |
| **harmony** | measurable | Hand-built triad detector over `librosa.feature.chroma_cqt`, template-matched against `{C:maj, A:min, F:maj, G:maj}`, scored via `mir_eval.chord.triads` weighted accuracy against the I–vi–IV–V bar-tiled reference: **0.983, 0.983, 0.983** at 30/60/90 s. | modulations; extended harmony; voicings; chord inversions |
| **timbre** | proxy-only | MFCC-13 mean-vector self-similarity (≈ 1.0) as sanity anchor. Resynthesis-based similarity (`orig` vs `fluidsynth(est_midi)`) deferred: wiring fluidsynth-in-the-loop across two transcribers × three stems × three mixes = 18 renders is out of scope this cycle. | true timbre labels (none exist for synthetic mixes); instrument-family classification beyond the known GM patch label |
| **dynamics** | **upgraded to measurable** | `mir_eval.transcription_velocity.precision_recall_f1_overlap` on the bass stem with `velocity_tolerance=0.1` (~13/127 MIDI velocity units): alternative F1 = 1.000/1.000/1.000; basic-pitch F1 = 0.475/0.472/0.486. Full table at `data/transcribe/velocity/velocity_f1.tsv`. | envelope evolution within a held note; sustain-pedal dynamics; crescendo/decrescendo shapes |
| **form** | deferred | nothing (synth mixes have no section labels; 30/60/90 s durations are pure loop tiles with no A/B structure) | everything (verse/chorus segmentation; A/B/A form; motivic recurrence). Will unlock when rated audio arrives + a labelled-form corpus is chosen. |
| **vocals-to-text** | placeholder | `transcribe_vocals(wav) -> "NO_VOCAL_STEM"` on the silent-by-construction synth vocals stem. | actual speech-to-text (no vocal audio in workspace this cycle) |

## 7. Adopt-or-build verdict

Comparing basic-pitch vs alternative across the melodic tuples (2
transcribers × 3 mixes × 2 melodic stems = 12 cells, drum row reported
but not weighted per §5 disclaimer):

- **basic-pitch wins the piano/`other` polyphonic column** decisively
  (mean F1 = 0.725 vs 0.325).
- **alternative wins the bass monophonic column** decisively (mean F1 =
  1.000 vs 0.481).
- **Neither transcriber wins drums**: basic-pitch = 0.000 (out of
  distribution), alternative = 0.397 (recall-capped by
  `librosa.onset.onset_detect` at fixed threshold).

**Verdict: BUILD.** No single off-the-shelf transcriber is adequate.
The concrete recommendation is a per-stem router: basic-pitch for
polyphonic pitched stems (piano/`other`), a Crepe- or pyin-class
monophonic pitcher for bass (alternative here hits 1.000, cheaply), and
a dedicated onset+classifier for drums (recall ≈ 0.33 today, must
improve — the natural next-cycle experiment is a spectral-flux onset
picker tuned per drum class with a small trained head on GM-drum
templates). This matches the plan-of-record intent that "per-instrument
isolation of the 'other' stem" (and by extension per-stem
transcription strategy) is a first-order refinement.

## 8. Blind spots per transcriber

**basic-pitch 0.4.0:**

- Drum stems: F1 = 0.0000 on all three mixes; produces zero notes.
  Model was designed for pitched polyphonic instruments.
- Bass over-generation: 44/93/132 notes estimated vs 15/30/45 ref
  (~3× over-generation). Precision ~0.32 across mixes. Likely: the
  activation head fires at every partial of the bass fundamental. Filed
  as a next-cycle probe: post-process by pitch-class collapsing octaves
  that co-onset with a lower one.
- Piano over-generation: ~2× (78/45, 156/90, 236/135). Same
  hypothesis: octave partials of block-chord fundamentals surviving
  the note-decoder threshold.
- Polyphony ceiling: not stressed by this workload (≤3-voice piano
  chords). Untested at ≥4 concurrent notes.

**Alternative (librosa-family):**

- Drum classification is a 3-way spectral-band argmax; confused when
  hihat and snare co-occur (misses snare because hihat's high-band
  energy dominates the 5-frame window).
- CQT peak-picking on the piano stem massively over-generates (185
  notes vs 45 ref); every partial above -25 dB and lasting ≥4 frames
  becomes a note. Would need explicit fundamental-frequency
  disambiguation (harmonic-comb template subtraction) to match
  basic-pitch on `other`.
- pyin on bass is essentially perfect on this workload because the
  bass melody is 4 held quarter-note-length roots per 8 s loop with
  strong fundamentals and no polyphony.
- No expressive velocity: velocities are hard-coded (100 for bass, 100
  for kick/snare, 70 for hihat, 85 for piano).

## 9. Non-factor discipline

`scripts/transcribe/*.py` — 6 source files —
never `import` or `from` any `sidecar_nonfactor`. Verified by AST-style
regex scan gated in `tests/test_integration_cross_branch.py §12f`. The
scripts read only WAVs under `data/separation/synth_mix/gt/` and MIDIs
under `data/separation/synth_mix/midi/`; no path under
`data/classifier/_nonfactor/` is touched.

## 10. Reproducibility

**Regeneration order** (from a clean state, using the M-SEP-1
ground-truth stems):

```
/usr/bin/python3 -m venv workspace/basic_pitch_venv
workspace/basic_pitch_venv/bin/python3 -m pip install basic-pitch==0.4.0
workspace/basic_pitch_venv/bin/python3 -m pip freeze > workspace/basic_pitch_venv/requirements.frozen.txt

/usr/bin/python3 scripts/transcribe/reference_events.py
/usr/bin/python3 scripts/transcribe/basic_pitch_baseline.py
/usr/bin/python3 scripts/transcribe/alternative.py
/usr/bin/python3 scripts/transcribe/eval_transcription.py
/usr/bin/python3 scripts/transcribe/six_axis_coverage.py
```

**Pinned versions:**

- Interpreter: `/usr/bin/python3` (asserted at every entry point).
- Venv interpreter: `workspace/basic_pitch_venv/bin/python3` (asserted
  inside `_bp_call.py`).
- basic-pitch: `0.4.0`. tensorflow: `2.15.0`. numpy: `1.26.4`. See
  `workspace/basic_pitch_venv/requirements.frozen.txt` for the full
  62-line pin set.
- mir_eval: `0.8.2`. librosa: `0.11.0`. pretty_midi: `0.2.11.post0`.
- ICASSP 2022 model bundled inside basic-pitch wheel at
  `workspace/basic_pitch_venv/lib/python3.11/site-packages/basic_pitch/saved_models/icassp_2022/nmp/`.

**Reference SHAs:** all 12 (mix, stem) reference JSONL SHAs are anchored
in `data/transcribe/reference/reference_manifest.json` and gated in
§12b of the cross-branch test.

**Determinism:** reference-events regen is SHA-identical. basic-pitch
under single-thread BLAS pins is SHA-identical (verified on bass @
synth_030s). The alternative (librosa-based) is float-deterministic on
this workload (pyin + onset detect + CQT are deterministic when the
input WAV bytes are identical).

## 11. Cross-branch test extension

`tests/test_integration_cross_branch.py` §12 adds 15 M-TRANS-1 checks:
venv path exists (12a-1), venv interpreter present (12a-2), pins file
present (12a-3), pins include basic-pitch==0.4.0 (12a-4), reference
manifest present (12b-1), 12-pair manifest (12b-2), SHA reproduction
(12b-3), results TSV present (12c-1), 18 data rows (12c-2), header
schema (12c-3 × 6), LOWER-BOUND disclaimer in TSV (12d), report present
(12e-1), report carries lower-bound disclaimer (12e-2), report has
six-axis section (12e-3), no sidecar_nonfactor import in
scripts/transcribe (12f), and six-axis coverage matrix has all 7 axes
(12g).

## 12. Open questions / next-cycle probes

- **Per-stem router prototype.** Wire basic-pitch(piano) + pyin(bass) +
  a dedicated drum-onset classifier as a single `transcribe(stem_wav,
  stem_type) -> midi` façade. Adopt-or-build verdict cashed out.
- **Drum-onset F1 recovery.** Alternative recall = 0.33; the miss set is
  dominated by snare-under-hihat confusion. A per-band spectral-flux
  picker (three parallel `librosa.onset.onset_detect` calls on band-passed
  audio) is the natural fix, no learning required.
- **basic-pitch octave-doubling suppression** for `other` and bass:
  post-process to drop notes whose fundamental is an octave above a
  co-onset note. Expected to lift bass F1 from ~0.48 toward ~0.9 and
  piano F1 from ~0.72 toward ~0.85.
- **Timbre axis upgrade to measurable.** Wire a fluidsynth-in-the-loop
  resynthesis path (est.mid → fluidsynth → wav → MFCC cosine vs
  original stem) so timbre becomes a real number, not a self-similarity
  anchor.
- **Vocals-to-text** stays placeholder until rated audio unblocks (see
  `corpus/CORPUS_STATUS.md` egress policy).
