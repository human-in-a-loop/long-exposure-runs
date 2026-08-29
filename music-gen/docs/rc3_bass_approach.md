# RC3 Bass Approach — pyin monophonic (c51 clone-1)

## Chosen path

`librosa.pyin` monophonic on `data/recreate_v2/baseline/<sha16>/rc0/bass.wav` OR c49 htdemucs-4stem `04_htdemucs/bass.wav` (whichever exists).

Parameters (frozen):
- `fmin = librosa.note_to_hz('E1')` = 41.2 Hz
- `fmax = librosa.note_to_hz('E4')` = 329.6 Hz
- `sr = 44100`, `hop_length = 512`

Grouping: contiguous voiced frames ≥ 60ms → one note. Median f0 → MIDI via `librosa.hz_to_midi(round to int)`. Segment onset time = start of voiced run. Velocity = 100 (fixed).

## Fallback

If pyin voiced-fraction < 0.1 on any focus song, fall back to lowered `basic-pitch` thresholds (`--onset_threshold 0.1 --frame_threshold 0.15`, MIDI-note filter [24, 55]) via `workspace/basic_pitch_venv`. Recorded in per-song `rc3_bass_notes.jsonl` metadata.

## Terminal sanity

Median MIDI pitch < 55 asserted per song.
