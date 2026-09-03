# RC2 + RC3 Implementation Rubric (c51 clone-1, frozen)

Milestone parent: `M-RECREATE-2/accurate-small-set-v2` (c50 rubric-v2 supersede chain).
Parent v2 rubric anchor: `docs/m_recreate_2_accurate_small_set_rubric_v2.md` SHA-256 `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f` (BYTE-PRESERVED).

## Scope

Implement RC2 (drum onset transcription via `librosa.onset.onset_detect` + per-onset band-energy classifier) and RC3 (bass transcription via pyin monophonic) on the 5-song c50 focus set (`data/recreate_v2/focus_set_v2.json`). Per-song accepts measured against baselines in `data/recreate_v2/baseline/<sha16>/`. Panel-gate (RC6) is c52+ scope.

## Frozen 3-verdict rubric

- **RC2_RC3_LANDS**: ≥3/5 focus songs pass BOTH RC2 accept AND RC3 accept.
- **RC2_RC3_PARTIAL**: 1-2/5 songs pass BOTH, OR ≥3/5 pass EITHER RC2 or RC3 (not both).
- **RC2_RC3_FAILS**: 0/5 pass either RC2 or RC3, OR script errors on ≥2 songs.

## RC2 accept per song

- Drum onset F1 vs baseline `rc2_drum_onset_count.json.onset_times_s` (tolerance ±50ms, `mir_eval.onset.f_measure`) ≥ 0.60.
- Drum note count within `[0.5×, 2×]` of baseline onset count.
  - Chicken Grease baseline = 109 onsets → produced count ∈ [55, 218] (kills the "5 drum notes in 30s" failure).
- Onset params pre-registered in `data/recreate_v2/rc2_classifier_bands.json` (SHA-256 `68d715fb5d0be7062e4b93900987cedadb12090a78bbc3a87e936c1c1762a94e`).
- Kick/snare/hihat classifier: per-onset 50ms window RMS in each of {kick_band=[20,200], snare_band=[200,3000], hihat_band=[3000,22050]}; argmax → GM channel-10 note {36, 38, 42}.

## RC3 accept per song

- Bass note count within `[0.5×, 2×]` of baseline `rc3_bass_pyin_voiced_segments.json.voiced_segments_count`.
- Low-band (<250 Hz) energy correlation ≥ 0.5 (Pearson on hop=512 RMS envelopes of scipy.signal.butter-order-4 lowpass on baseline bass.wav vs rendered bass wav).
- Median MIDI pitch < 55 (terminal sanity gate).
- Approach: `librosa.pyin` monophonic (fmin=41.2Hz=E1, fmax=329.6Hz=E4, hop=512); voiced-segment grouping (min 60ms); segment onset = start; velocity fixed 100.

## Chain-of-anchors (byte-preservation)

Verdict JSON MUST carry:
- `rubric_hash`: SHA-256 of this document.
- `parent_rubric_hash_v2`: `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f` (c50 v2 anchor, BYTE-PRESERVED).
- Three-way byte-equality: doc SHA == `data/rc2_rc3_impl/rubric_hash.txt` == `verdict.json.rubric_hash`.

## Discipline

- NO PRNG (SHA-256 tiebreak only where ordering required; deterministic librosa/scipy calls).
- `/usr/bin/python3` interpreter guard on every new script under `scripts/recreate_v2/`.
- Byte-determinism × 2 asserted on per-song `rc2_drum_notes.jsonl`, `rc3_bass_notes.jsonl`, `merged.midi`, `rc3_bass_rendered.wav`.
- Env pins: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, single-thread BLAS.
- c48 env-var flags OFF.
- `scripts/palette_render/render_stem.py` UNTOUCHED (Branch C territory).
- File deletion FORBIDDEN; scratch → `tools/stale/`.

## Anti-pattern locks respected

- c11 CLAP: not touched.
- c22/c23/c25 M-EAR-1: not opened.
- c35 palette-schema-v2 VST3: not touched.
