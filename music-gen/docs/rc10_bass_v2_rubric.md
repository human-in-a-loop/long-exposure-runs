---
created: 2026-09-02T02:15:00Z
cycle: 55
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2
supersedes_path: docs/rc10_drums_bass_rubric.md
---

# RC10 Bass Articulation v2 — Frozen Rubric

Peer sub-milestone under `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey` per c29 state-machine lemma. NOT a re-verdict of the c54 terminal `RC10_DRUMS_BASS_LANDS` parent — bass v2 iterates on the WINNING family (`pyin_mono`) responding to operator listening feedback on syncopation / ghost-note / slap-pop loss.

## Rubric hash
`data/rc10_bass_v2_impl/rubric_hash.txt` MUST byte-equal SHA-256 of this file.
`data/rc10_bass_v2_impl/verdict.json.rubric_hash` MUST byte-equal that value.
Three-way byte-equality chain is a hard gate.

## D3 Onset-segmented pyin (replaces c54 pyin-only continuity tracking)

Fixed decisions:
- `librosa.onset.onset_detect(y_bass, sr, hop_length=512, delta=0.02, backtrack=True)` — low-delta captures ghost transients.
- For each inter-onset interval `[t_i, t_{i+1})`: run `librosa.pyin(y_bass[t_i:t_{i+1}], fmin=librosa.note_to_hz('E1')=41.20, fmax=librosa.note_to_hz('E4')=329.63, hop_length=512, frame_length=2048)`. Median voiced f0 → nearest MIDI.
- Same-pitch consecutive onsets become SEPARATE note events (fixes c54 syncopation loss).
- `MIN_DURATION_S = 0.040` (40 ms ghost-note floor). Shorter dropped.
- Voiced-probability threshold within interval: median `voiced_probability > 0.1` (c54 empirical calibration retained; strict 0.5 → 0 notes on real htdemucs bass residuals per c54 audit MODERATE #1).

## D4 Slap/pop detector

- Per-onset HF band energy `E_hf(t)` = sum of magnitude² in 2000–8000 Hz bins over ±100 ms window around onset (n_fft=2048, hop=512).
- Rolling median `M_hf(t)` = median of `E_hf(τ)` over τ ∈ [t−1 s, t+1 s].
- Onset is `slap` iff `E_hf(t) > 3 × M_hf(t)`.
- Slap onsets → `velocity = 100`, `articulation = "slap"`.

## D5 Velocity + articulation encoding

Notes JSON schema: `{onset_s, duration_s, midi, velocity, articulation}` where `articulation ∈ {"sustained", "ghost", "slap"}`.

Priority-ordered first-match articulation:
1. D4 slap detector fires → `"slap"`, velocity = 100.
2. Else if `duration_s < 0.080` AND `velocity < 50` → `"ghost"`.
3. Else → `"sustained"`.

Non-slap velocity: peak RMS within inter-onset interval, linearly mapped to `[40, 90]` peak-normalized per song.

## D6 Four-metric composite gate (per song)

1. Bass onset F1 ≥ 0.60 vs `librosa.onset.onset_detect(y_bass_baseline)` reference — preserved from c54; must not regress vs c54 v1 by more than 0.05.
2. Note-count ratio ∈ [0.7, 1.5] = predicted_notes / detected_onsets.
3. Velocity std ≥ 10 across all notes (dynamics must reflect articulation).
4. Low-band (<250 Hz) energy correlation ≥ 0.5 vs baseline envelope.

## D7 Verdict

- `RC10_BASS_V2_LANDS` iff ≥3/5 focus songs pass ALL 4 metrics.
- `RC10_BASS_V2_PARTIAL` iff 2/5 pass all four OR ≥3/5 pass 3-of-4 with metric-1 (onset F1) preserved AND the v2-vs-v1 onset-F1 regression contract holds.
- `RC10_BASS_V2_FAILS` otherwise.
- Chicken Grease (`31a164f845f8e27e`) + What If I Go (`252eb21ce7df7328`) MANDATORY per-song accepts.
- Regression contract: v2 onset F1 per song MUST NOT drop below (v1 onset F1 − 0.05) for any song. Per-song delta table published; if any song regresses beyond −0.05, verdict caps at PARTIAL with honest regression note.

## A/B emission

Per focus song: `data/recreate_v2/ab_pairs/<sha16>/bass/iter_1/{original.wav, rendered.wav}`.

Rendered via fluidsynth GM 34 (electric bass finger, program=33 in 0-indexed pretty_midi) with per-note MIDI events carrying velocity from D5. Articulation-driven envelope shaping:
- `slap` → sharp attack (velocity=100, short envelope decay via shortened note-off).
- `ghost` → soft attack (velocity <50 already handles).
- `sustained` → default.

LUFS-I normalize both to −23 LUFS-I with true-peak-limit 0.99 via `pyloudnorm.Meter.integrated_loudness`. If pyloudnorm unavailable in `basic_pitch_venv` (this branch runs system-side so not blocking), fall back to RMS-dBFS proxy with honest §Issues disclosure. System-side pyloudnorm is verified present.

## Falsifiable success criteria

- (a) rubric doc mtime < any script under `scripts/recreate_v2/rc10_bass_v2/` (test 01 hard, test 02 SOFT git-log per c46 amendment)
- (b) three-way rubric_hash byte-equality (doc SHA == `data/rc10_bass_v2_impl/rubric_hash.txt` == `verdict.json.rubric_hash`)
- (c) verdict.json.verdict ∈ {RC10_BASS_V2_LANDS, RC10_BASS_V2_PARTIAL, RC10_BASS_V2_FAILS}
- (d) byte-determinism × 2 across all output artifacts via two fresh `tempfile.mkdtemp()` runs under BLAS + `PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1756463424` + `TZ=UTC` + `LC_ALL=C.UTF-8` + single-thread BLAS
- (e) c50 v2 rubric SHA `0e11f704…debe1f` byte-identical pre==post
- (f) c54 v1 `docs/rc10_drums_bass_rubric.md` SHA `a79bee01…5fd919` byte-identical pre==post
- (g) c54 v1 `data/rc10_drums_bass_impl/*` byte-identical pre==post (v1 chain READ-ONLY)
- (h) `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b` byte-identical pre==post (do-not-touch anchor)
- (j) NO PRNG (AST-grep clean; librosa/scipy calls only)
- (k) NO `sidecar_nonfactor` import (AST-grep)
- (l) `/usr/bin/python3` interpreter guard on every top-level script
- (m) c48 env-var flags default OFF via `os.environ.setdefault`
- (n) anchor preservation ≥25 SHAs pre==post byte-exact
- (o) Chicken Grease + What If I Go BOTH per-song accepts hold
- (p) v2 onset F1 no regression >0.05 on any song vs c54 v1 (reference: librosa.onset.onset_detect on baseline stem — both v1 and v2 use the same reference)
- (q) ≥15/15 tests green in `tests/test_rc10_bass_v2.py`
- (r) 0-ERROR promise_check post-emission
