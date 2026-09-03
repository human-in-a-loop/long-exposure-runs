# Family-2 stem-sampled builder — c6 rubric

## 1. Contract inherited from c5 spec

Per `docs/sound_match/family2_stem_sampled_spec.md` §Builder sketch and
§Objective panel. This cycle promotes the c5 spike (which proved the
pitch-shift → sum → LUFS-normalize → panel path end-to-end) into a real
per-note builder that consumes the full bass.mid (59 notes, ~30 s) and
emits a family-2 profile + replay proof.

## 2. Reference contract (READ-ONLY)

- Stem: `data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav`
  sha `1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd`
- MIDI: `data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid`
  sha `4863ca285c7db513c8bfc22da5e35e65036b0ecad2538a6d9794c80eb15f8ac9`

## 3. Design levers (named, frozen)

- **Strategy**: `single_slice_pitch_shift` — one stable slice extracted from
  the reference stem at `stem_slice_start_s = 0.0`, length
  `stem_slice_len_s = 3.0` seconds. For each MIDI note, `librosa.effects.pitch_shift`
  the same slice to the target pitch. Chosen over per-note-pick + windowed
  f0 for c6 first cut because (a) the c5 spike already validated this
  path, (b) it is the smallest deterministic pure function of
  (stem, midi, program_params), (c) it avoids the pyin-subharmonic quirk
  that the c5 spike encountered on a very short 6 s reference.
- **Envelope**: `adsr_lite` — 5 ms linear attack, flat sustain scaled to the
  note's duration, 5 ms linear release. Same shape as c5 spike.
- **Reference f0 estimate**: `librosa.pyin(fmin=E1=41.20 Hz, fmax=E4=329.63 Hz)`
  with fmin/fmax pinned to the bass range so the c5 spike's 34.45 Hz
  subharmonic quirk cannot recur. Fallback to `librosa.yin(fmin=50, fmax=400)`
  and finally to 82.41 Hz (E2) if both refuse.
- **LUFS normalize**: `pyloudnorm.Meter(sr).integrated_loudness` → gain to
  −18.0 dB LUFS-I; RMS-dBFS fallback path logged if pyloudnorm unavailable.

## 4. Objective panel (frozen, no re-weighting)

Same three keys, same weights (0.5 / 0.25 / 0.25) as sf2:
`mel_l1_db + spectral_centroid_rmse_hz + embedding_cos_vggish`.
Panel is finite gate only, NEVER a LANDS gate per FD-6.

## 5. Verdict rubric (frozen 3-way)

- `FAMILY2_CONFIRMED`: `embedding_cos_vggish ≥ 0.60` AND all 3 panel
  values finite AND replay proof HOLDS.
- `FAMILY2_RULED_OUT`: `embedding_cos_vggish ≤ 0.40` AND all 3 panel
  values finite AND replay proof HOLDS.
- `FAMILY2_INDETERMINATE`: panel finite AND replay HOLDS AND
  `embedding_cos_vggish ∈ (0.40, 0.60)`.

Same thresholds as sf2 arc (`data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json`)
— pre-registered, no drift.

## 6. Regression coverage

Two profiles differing only in identity fields (e.g., different
`stem_slice_start_s` values 0.0 vs 1.0) MUST produce DIFFERENT replay
SHAs on the same MIDI. Lesson from sf2 defect must not repeat: the
profile's identity fields must actually flow through to the audio bytes.

## 7. Family-2 replay-proof contract (FD-16c)

Family-2 is a distinct RENDER FAMILY from sf2 per FD-16(c) — it needs its
OWN `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.replay_proof.json`.
Sibling to but not covered by the sf2 replay proofs. Byte-identical ×2
fresh `tempfile.mkdtemp()` dirs under unified env pins.

## 8. Three-way rubric_hash chain

SHA-256 of this markdown pinned to
`data/v4/profiles/31a164f845f8e27e/family2_builder_c6_rubric_hash.txt`
BEFORE any builder script edit. Final `bass_family2_verdict.json`
carries `rubric_hash` byte-equal to that pinned content and to this
doc's SHA-256 at close-of-cycle.
