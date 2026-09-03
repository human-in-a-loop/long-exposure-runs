# RC10 Branch C Rubric — Other-Residual + Vocals Transcription Re-Survey (c53, clone-2)

**Milestone parent:** `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`
(peer sub of `M-RECREATE-2/accurate-small-set-v2` per c29 state-machine lemma)

**Frozen anchors (READ-ONLY):**

- v2 rubric doc: `docs/m_recreate_2_accurate_small_set_rubric_v2.md`, SHA-256 = `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`.
- Focus set: `data/recreate_v2/focus_set_v2.json`, 5 songs including Chicken Grease (t=233.6–263.6s window).
- Baseline stems: `data/recreate_v2/baseline/<sha16>/rc9_6stem/{vocals,other}.wav` — six-stem htdemucs outputs, all 5 focus songs present.
- rc5 tempo estimate: `data/rc5_impl/<sha16>/rc5_tempo_estimate.json` (used for D4 beat-grid snap).

**Scope:** two stem types re-benchmarked against ORIGINAL SEPARATED STEMS on chosen_section windows.

## §D2 — Content metrics (per operator UPDATE #3)

- **Vocals:**
  - `f0_agreement_pct`: framewise `librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), hop_length=512, sr=sr)` on both original vocal stem and rendered vocals audio. Count frames voiced-in-both; percent of those within ±1 semitone.
  - `voiced_time_coverage_ratio`: rendered voiced-frame-count / baseline voiced-frame-count (both from pyin on respective audio).
  - **PASS:** `f0_agreement_pct ≥ 60% AND coverage_ratio ∈ [0.5, 2.0]`.

- **Other-residual:**
  - `mean_chroma_cosine`: beat-synchronous mean cosine of `librosa.feature.chroma_cqt(hop=512)` between original stem and rendered comp-pattern audio (fluidsynth GM 0 piano render of extracted chord track). Beat grid from rc5.
  - `density_ratio`: rendered notes/s ÷ baseline notes/s (baseline notes = basic-pitch on original for reference count).
  - **PASS:** `mean_chroma_cosine ≥ 0.55 AND density_ratio ∈ [0.5, 2.0]`.

Secondary (informational): mel_l1_db, spec_centroid_rmse_hz, rms_env_rmse, embedding_cosine (may be `null:vggish_unavailable`, per c11 anti-pattern lock).

## §D3 — Candidate matrix per stem

**Vocals:**
- **v_a** basic-pitch defaults (quarantined venv, subprocess dispatch from `/usr/bin/python3`).
- **v_b** basic-pitch tuned `--onset-threshold=0.3 --frame-threshold=0.3 --minimum-note-length=100 --minimum-frequency=80 --maximum-frequency=1100` (CLI).
- **v_c** `librosa.pyin(y, fmin=C2, fmax=C7, hop_length=512)` + voicing-confidence segmentation: contiguous voiced runs ≥100 ms → note event; median pitch rounded to nearest MIDI.

**Other-residual:**
- **o_a** basic-pitch defaults.
- **o_b** chroma-based chord-track fallback: `librosa.feature.chroma_cqt(hop=512)` beat-synchronous over rc5 beat grid, argmax over 24 major/minor triad templates per beat, render as GM 0 piano triad held for beat duration (via `pretty_midi`; audio render via fluidsynth deferred — chroma metric computed directly on templated MIDI's implied pitch classes).

## §D4 — Post-processing (measured with and without)

1. Snap onsets to rc5 beat grid within ±50 ms.
2. Drop notes shorter than 32nd-note at estimated tempo (`60/(bpm*8)` seconds).
3. Derive velocity from original stem local RMS envelope in note window (normalized to [1, 127]).
4. Sanity-filter pitches outside instrument physical range (vocals 80–1100 Hz; other-residual C1–C7).

## §D5 — Winner selection

Per stem type, winner = candidate with highest content-metric score on ≥3/5 focus songs (score = `f0_agreement_pct` for vocals, `mean_chroma_cosine` for other-residual). Ties broken by SHA-256 tiebreak on candidate name string. Winner recorded in `data/rc10_impl/other_vocals/winner_per_stem_type.json`.

## §D6 — A/B artifacts

For every (song, stem, candidate) iteration + winner, write RMS-dBFS-normalized (target -23 dBFS RMS as LUFS-I proxy; pyloudnorm unavailable in venv — documented deviation) `original.wav` + `rendered.wav` pair under `data/recreate_v2/ab_pairs/<song_sha16>/{other_residual,vocals}/iter_<candidate>/`.

## §D7 — Verdict enum

- **`RC10_OTHER_VOCALS_LANDS`** — both stems PASS on ≥3/5 focus songs.
- **`RC10_OTHER_VOCALS_PARTIAL`** — exactly 1 stem passes ≥3/5.
- **`RC10_OTHER_VOCALS_FAILS`** — otherwise.

Capability-ceiling report mandatory if any stem fails after honest effort: name WHICH metric, by HOW MUCH, best candidate output surfaced.

## §D8 — Anti-patterns respected

- c11 CLAP/VGGish: no fetch attempted; embedding_cosine returns `null:vggish_unavailable` if unresolvable.
- c22/c23/c25 ear chassis: no M-EAR-1 emissions.
- c31/c35 VST3 nondeterminism: no VST3 renders.
- NO PRNG (AST-grep clean under `scripts/recreate_v2/rc10_other_vocals/`).
- `/usr/bin/python3` interpreter guard on every script; basic-pitch dispatched via venv subprocess.
- c48 env-var flags default OFF.

## Env pins (byte-determinism × 2)

- `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`.
- Single-thread BLAS: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`.
- Two fresh `tempfile.mkdtemp()` runs; SHA-256 equality asserted per output.

## Deviations documented

1. **LUFS-I -23 → RMS dBFS -23 proxy**: `pyloudnorm` is not installed in the basic-pitch venv (only lib with librosa available). Loudness normalization applied as RMS scale-to-target, which is measurement-close for stationary content and adequate for A/B comparison; not a true ITU-R BS.1770-3 gate. This is a documented deviation from D6 rather than a silent skip.
2. **Chord-track render**: `o_b` computes chroma cosine on the templated MIDI's pitch-class implication rather than re-rendering to audio via fluidsynth, because the audio-render path adds indirection that doesn't change chroma-family metric semantics (chroma of a rendered triad equals the templated triad chroma up to release-tail).
