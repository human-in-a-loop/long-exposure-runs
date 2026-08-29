# M-RECREATE-2/accurate-small-set — pre-registration rubric

**Cycle**: 49
**Author**: worker (c49 linear cycle)
**Status**: frozen at c49 landing; consumed READ-ONLY by c50+ RC branches.

## 1. Scope

M-RECREATE-2 is the operator-carried response to the OPERATOR PRIORITY
OVERRIDE #2 (2026-08-29, `docs/OPERATOR_recreation_root_cause_audit.md`).
It is a **peer sub-milestone under G1** per the c29 state-machine lemma —
NOT a child of terminal-validated `M-RECREATE-1/*`.

The scope is accurate reconstruction of a **focus set of 3–5 songs with
strong rhythm sections, mandatorily including Chicken Grease (band 6)**.
Six architectural root causes named in the operator audit are fixed as
six pre-registered per-fix acceptance tests (RC1–RC6), each measured
against **ORIGINAL SEPARATED STEMS** produced by htdemucs (READ-ONLY c37
anchor). A new **panel gate** (RC6) replaces the c37/c39-42 mel-L1-only
gate that let LANDS fire while VGGish embedding regressed.

M-RECREATE-2 is decomposed into **six per-fix peer sub-milestones**:

| Sub-milestone                                          | RC  | c50+ branch owner |
|--------------------------------------------------------|-----|-------------------|
| `M-RECREATE-2/accurate-small-set/rc1-vocals-transcription` | RC1 | c50 candidate fanout |
| `M-RECREATE-2/accurate-small-set/rc2-drum-onset-transcription` | RC2 | c50 candidate fanout |
| `M-RECREATE-2/accurate-small-set/rc3-bass-transcription`   | RC3 | c50 candidate fanout |
| `M-RECREATE-2/accurate-small-set/rc4-gm-program-map`       | RC4 | folds into RC1-RC3 merged.midi |
| `M-RECREATE-2/accurate-small-set/rc5-tempo-beat-grid`      | RC5 | c51 linear |
| `M-RECREATE-2/accurate-small-set/rc6-panel-gate`           | RC6 | c52+ (depends on RC1-RC3) |

Every RC branch inherits this rubric SHA verbatim in its verdict JSON via
`rubric_hash` byte-equality chain (doc SHA == `data/recreate_v2/rubric_hash.txt`
== per-RC `verdict.json.rubric_hash`).

## 2. Fixed decisions (c49-frozen)

- **Focus set = 3–5 songs.** Mandatory: Chicken Grease (band 6). Filler
  slots (2–4) drawn from operator-named pool
  `{Mura Masa "What If I Go" (5), Disco A (5), Peach Dream (6), Lost (6),
   Dojo Cuts "Rome" (5)}` ranked ascending by
  `SHA-256(f"{artist}|{title}|{playlist_id}".encode("utf-8"))`; top 4 taken.
  Persisted at `data/recreate_v2/focus_set.json`.
- **Trim window**: 30 s per operator ("30 s excerpt"), starting at 0.0 s
  (no offset — matches c37 anchor semantics).
- **htdemucs stems are READ-ONLY anchors** at
  `data/recreate_v0_full_corpus/per_song/<band>/<sha16>/per_stage/04_htdemucs/{vocals,drums,bass,other}.wav`.
  Re-running htdemucs is out-of-scope for c49 (stems are already the
  c37-anchor product of a c37-frozen `torch.manual_seed(0)` run).
- **All RC0 baseline measurements byte-deterministic × 2** via fresh
  `tempfile.mkdtemp()` under env pins `PYTHONHASHSEED=0`,
  `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`,
  `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`,
  `torch.manual_seed(0)`.
- **SHA-256 tiebreak only. NO PRNG.** AST-grep clean under
  `scripts/recreate_v2/`.
- **`/usr/bin/python3` interpreter guard** on every new script.
- **c31 STILL_GAP AST-forbidden methods** (`get_state`, `save_state`,
  `save_preset`, `load_state`, `set_state(bytes)`) remain forbidden.
- **Rendering may stay fluidsynth-GM this milestone** (palette swap
  deferred); per-stem GM program assignment (RC4) is mandatory.
- **c33 harness auto-suffix behavior**: c49 default OFF
  (`MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION` unset). All M-RECREATE-2/*
  substantive event ids remain unsuffixed per c32 convention.

## 3. Per-RC acceptance criteria (verbatim from operator audit + brief)

Each RC's acceptance test is compared against the READ-ONLY RC0 baseline
at `data/recreate_v2/baseline/<song_id>/` frozen this cycle.

### RC1 — Vocals transcription (undoing "skip vocals")

**Fix**: transcribe the vocals stem using basic-pitch (pitched-note) OR
pyin f0-tracking; include the melody line as a lead part in `merged.midi`.

**Accept iff**: for a given focus song,
- vocal-part note count > 0 in the produced `merged.midi`; AND
- voiced-time coverage ≥ **50 %** of the original vocal stem's voiced
  time, where voiced-time is measured by pyin's `voiced_flag` mask
  (baseline reference: `baseline/<song>/rc1_vocals_voiced_time_s.json`).

### RC2 — Drums onset-based transcription (killing "5 notes in 30 s")

**Fix**: replace basic-pitch on the drums stem with onset detection
(`librosa.onset.onset_detect` default params) + per-onset band-energy
classification into kick/snare/hihat, mapped to GM channel 10 notes
36/38/42.

**Accept iff**: for a given focus song,
- drum onset F1 ≥ **0.60** vs onsets detected on the original drums
  stem (`baseline/<song>/rc2_drum_onset_count.json` frozen count and
  onset-time array); AND
- drum note count in `merged.midi` within [0.5×, 2×] of the original-stem
  onset count.

Chicken Grease negative-control target: current 5 notes → post-fix ≥ ~30
notes (i.e. within 0.5× of the baseline onset count, whichever is larger).

### RC3 — Bass-specific transcription + octave sanity

**Fix**: lower basic-pitch onset/frame thresholds on the bass stem OR use
pyin monophonic f0-tracking; sanity-check median MIDI pitch < 55.

**Accept iff**: for a given focus song,
- bass note count within [0.5×, 2×] of pyin-voiced-segment count on the
  original bass stem (`baseline/<song>/rc3_bass_pyin_voiced_segments.json`); AND
- low-band (< 250 Hz) energy correlation between rendered-bass-only and
  the original bass stem ≥ **0.5**
  (`baseline/<song>/rc3_bass_low_band_energy.json` reference envelope);
  AND
- median MIDI pitch in bass part < 55.

### RC4 — Explicit GM program map per stem

**Fix**: assign GM program per stem in `merged.midi`:
bass → 33 (Acoustic Bass) or 34 (Electric Bass Finger);
drums → GM channel 10 (percussion, program byte free);
other → keys/guitar patch (per-song choice, logged);
vocals → a lead voice/synth patch.

**Accept iff**: `merged.midi` contains **zero** parts on program 4
(basic-pitch's default Electric Piano 1) unless the per-song "other"
choice was deliberately program 4 and logged in
`data/recreate_v2/<song>/rc4_program_map.json`.

### RC5 — Tempo and beat-grid estimation

**Fix**: run `librosa.beat.beat_track` on the original mix; set the
`merged.musicxml` score tempo from the estimate; quantize MusicXML
against the real beat grid.

**Accept iff**: for a given focus song,
- `abs(estimated_bpm - score_bpm) ≤ 2`, where `estimated_bpm` is the
  baseline pin at `baseline/<song>/rc5_tempo_bpm.json`.

RC5 also closes the c37/c39-42 quantization defect (open handoff).

### RC6 — Panel gate (replaces mel-L1-only)

**Fix**: LANDS gate becomes an **AND** over three conditions, not any
single metric:

1. RC1, RC2, RC3 accepts (per above) all hold on the focus song; AND
2. VGGish embedding cosine distance `original vs effects-render` ≤ VGGish
   cosine distance `original vs bare-render` (i.e. effects **does not
   regress** the perceptual embedding); AND
3. Spectral-centroid RMSE (Hz) does **not** worsen bare→effects:
   `centroid_rmse(original, effects) ≤ centroid_rmse(original, bare)`.

**Mel-L1 alone can never again confer LANDS.**

Baseline references: `baseline/<song>/rc6_vggish_embedding.npy` and
`baseline/<song>/rc6_centroid_time_series.npy` (30 s trim of original mix,
44.1 kHz stereo mono-mixdown, hop=512, n_fft=2048).

## 4. M-RECREATE-2 rollup verdict (3-way rubric)

Every per-RC branch emits its own PASS / PARTIAL / FAIL under the
per-RC criteria above. The rollup verdict is applied post-hoc after all
RC branches land:

| Rollup verdict            | Definition                                                                          |
|---------------------------|-------------------------------------------------------------------------------------|
| `M_RECREATE_2_LANDS`      | Panel gate (RC6) passes on **≥3 focus songs**, AND all 6 RC per-fix accepts hold on **≥3 focus songs**. |
| `M_RECREATE_2_PARTIAL`    | Panel gate passes on 1–2 focus songs, **OR** ≥4/6 RC accepts hold on ≥3 focus songs (whichever is stricter). |
| `M_RECREATE_2_INSUFFICIENT` | Anything else.                                                                       |

The rollup verdict is not emitted this cycle. It fires at the end of the
c50+ RC-branch arc when RC1–RC6 all have per-song verdicts on disk.

## 5. Anti-pattern lockouts (reassert)

The five campaign-level anti-patterns (c11 CLAP, c22 chassis-audit, c23
head-reg, c25 feature-rep, c35 palette-v2 VST3) all remain locked. No RC
in M-RECREATE-2 intersects them.

## 6. Discipline invariants (c49-pre-registered)

- Rubric doc SHA-256 landed BEFORE any file under `scripts/recreate_v2/`
  (mtime hard; git-log advisory per c46 path (ii)).
- Rubric SHA-256 pinned in `data/recreate_v2/rubric_hash.txt` byte-equal
  to this doc's SHA-256.
- Per-RC branch verdict JSON contains `rubric_hash` byte-equal to
  `data/recreate_v2/rubric_hash.txt`.
- Focus set persisted at `data/recreate_v2/focus_set.json` with per-song
  `sha16`, `rating_band`, on-disk path, existence check, and audio SHA-256
  for the READ-ONLY anchor manifest.
- RC0 baseline byte-deterministic × 2 across two fresh
  `tempfile.mkdtemp()` runs.
- Anchor preservation manifest ≥ 25 entries pre==post byte-exact,
  including all htdemucs stem SHAs.
- No import of `scripts.tex.render_effects_layered`, `sidecar_nonfactor`,
  `scripts.rules.sampling.i4_stratified`, c26-c30 collision-model
  utilities, or any `M-EAR-1/*` or `M-GEN-1/*` script under
  `scripts/recreate_v2/`.

## 7. Deferred to c50+

- Any RC1–RC5 implementation code. c49 ships anchor-manifest
  pre-registration stubs raising `NotImplementedError("c50+ branch")`.
- RC6 panel-gate implementation (depends on RC1–RC3 outputs).
- The two c48 Branch A env-var flag flips
  (`MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`,
  `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`).
- Any M-EAR-1 arc work. v2.1 PARTIAL_WITH_SB3_PASS parked per operator.
- Any M-GEN-1 batch work. Palette arc halted per operator.

## 8. Rubric_hash chain contract

The three-way rubric_hash byte-equality chain (doc SHA == rubric_hash.txt
== per-RC verdict.json.rubric_hash) is a HARD gate for every RC
branch's landing. Any drift REJECTS the branch.
