---
created: 2026-09-02T02:30:00Z
run_id: run-2026-08-28T040704Z
cycle: 55
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/ab-pairs-refresh
clone: clone-2
supersedes_path: null
---

# RC10 A/B Pairs Refresh Rubric (c55 fork 7cc01d726807 clone-2 Branch C)

**Scope.** Narrowly scoped: (i) install `pyloudnorm==0.1.1` in `workspace/basic_pitch_venv`
to close c54 audit Issue #3 (Branch C used RMS-dBFS proxy); (ii) swap A/B pair rendering
from `pretty_midi.PrettyMIDI.synthesize()` sine synth (c53 Branch B honest issue) to
fluidsynth CLI + FluidR3_GM.sf2 (SHA `74594e8f…1cb0`) with per-stem GM program pre-baked
into rendered MIDI via pretty_midi; (iii) emit 40 A/B pair WAVs (5 focus songs × 4 stems ×
{original, rendered}) under `data/recreate_v2/ab_pairs/<sha16>/{guitar,piano,other_residual,vocals}/iter_1/`;
(iv) normalize all pairs to true LUFS-I −23 via `pyloudnorm.Meter.integrated_loudness`.

Peer sub-milestone under `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`
per c29 state-machine lemma. c53/c54 winners are READ-ONLY inputs — NO transcription changes.

## §D1 Focus set

Uses `data/recreate_v2/focus_set_v2.json` verbatim (5 songs incl. Chicken Grease band-6). Chosen-section
metadata carried through unchanged. Baseline stems from `data/recreate_v2/baseline/<sha16>/rc9_6stem/{guitar,piano,other,vocals}.wav`.

## §D2 Winner MIDI sources (READ-ONLY per c53/c54)

- **guitar, piano** → per-song winners from `data/rc10_impl/guitar_piano/winner_per_stem.json`;
  MIDI at `data/rc10_impl/guitar_piano/per_song/<sha16>/<stem>/<candidate>__<pp>.midi`.
- **other_residual, vocals** → per-stem-type winners from
  `data/rc10_impl/other_vocals/winner_per_stem_type.json`:
  - vocals → `v_a` postprocessed (pp)
  - other_residual → `o_b` raw
  Per-song winner MIDI regenerated this cycle via READ-ONLY import of
  `scripts.recreate_v2.rc10_other_vocals.run_rc10` helpers (`_bp_predict`, `_chroma_chord_track`,
  `_postprocess`); persisted to `data/rc10_impl/other_vocals/per_song/<sha16>/<stem>/winner.mid`
  (this cycle writes; content re-derivable from READ-ONLY baseline stems + c53 code).

## §D3 pyloudnorm venv install spec

- Target: `workspace/basic_pitch_venv/bin/pip install pyloudnorm==0.1.1`
- Sanity: `pyloudnorm.Meter(sr).integrated_loudness(ones)` returns finite value
- Recorded in `data/rc10_ab_pairs_refresh/fetchability_ladder.jsonl`
- Closes c54 audit Issue #3

## §D4 fluidsynth CLI + FluidR3_GM.sf2 rendering spec

- Executable: `/usr/bin/fluidsynth` CLI
- SoundFont: `/usr/share/sounds/sf2/FluidR3_GM.sf2` (SHA `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`)
- Invocation shape: `fluidsynth -a null -T wav -F <out.wav> -r 44100 -R 1 -C 0 -g 1.0 <sf2> <midi>`
  (`-R 1` disables reverb; `-C 0` disables chorus; `-g 1.0` fixes gain)
- Per-stem GM program pre-baked into MIDI via `pretty_midi.Instrument(program=<gm>, is_drum=<bool>)`
  before fluidsynth invocation:
  - guitar → GM 25 (Steel-string Acoustic Guitar)
  - piano → GM 0 (Acoustic Grand Piano)
  - other_residual → GM 0 (Acoustic Grand Piano, safest neutral timbre for chord-track winner)
  - vocals → GM 54 (Voice Oohs, best available GM lead-voice proxy)
- Stereo output; deterministically renderable twice under BLAS + `PYTHONHASHSEED=0` +
  `SOURCE_DATE_EPOCH=1756463424` + `TZ=UTC` + `LC_ALL=C.UTF-8`

## §D5 iter_1 A/B pair emission schema

For each of 5 focus songs × 4 stems = 20 output pairs:

- `data/recreate_v2/ab_pairs/<sha16>/<stem>/iter_1/original.wav` — mono baseline stem WAV
  (SHA-verified pre-copy from `data/recreate_v2/baseline/<sha16>/rc9_6stem/<stem>.wav` with
  `other_residual → other.wav`), then LUFS-I normalized to −23.0
- `data/recreate_v2/ab_pairs/<sha16>/<stem>/iter_1/rendered.wav` — fluidsynth-rendered from
  the c53/c54 winner MIDI (with GM program pre-baked), then LUFS-I normalized to −23.0

Both files stereo PCM_16 at 44.1 kHz. True-peak-limit at 0.99.

## §D6 Verdict thresholds (frozen 3-way enum)

- `AB_REFRESH_LANDS`: 40/40 WAVs written + ≥36/40 within `abs(lufs_i_post − (−23.0)) ≤ 0.5 LU`
  + 20/20 winner MIDI SHA-256s byte-identical to c53/c54 anchors (transcription bit-preserved)
- `AB_REFRESH_PARTIAL`: 40/40 WAVs written + LUFS ±0.5 LU met on 28–35 pairs
  (accept ceiling on peak-limited signals) + winner MIDI SHAs preserved
- `AB_REFRESH_FAILS`: <32 pair WAVs write successfully OR any winner MIDI SHA diverges

## §D7 Anchor invariants (READ-ONLY, snapshot pre==post)

- `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b` (do-not-touch)
- `docs/m_recreate_2_accurate_small_set_rubric_v2.md` SHA `0e11f704…debe1f`
- `docs/rc10_guitar_piano_rubric.md` SHA `c7fe33a7…03d7a8`
- `docs/rc10_other_vocals_rubric.md` SHA `571296bc…ab3620`
- `docs/rc10_drums_bass_rubric.md` SHA `a79bee01…5fd919`
- `data/rc10_impl/guitar_piano/winner_per_stem.json`
- `data/rc10_impl/other_vocals/winner_per_stem_type.json`
- `data/rc10_drums_bass_impl/winner_per_stem.json`
- `/usr/share/sounds/sf2/FluidR3_GM.sf2` SHA `74594e8f…1cb0`

## §D8 Byte-determinism × 2

The 20 rendered pair WAVs must be byte-identical (SHA-256 equal) across two runs into fresh
`tempfile.mkdtemp()` dirs, then final-persisted to the target path once. The 20 original
pair WAVs derive deterministically from `soundfile.read` + LUFS-I gain scaling and must
also be byte-identical × 2. Result recorded in `data/rc10_ab_pairs_refresh/byte_determinism.json`.

## §D9 Winner MIDI anchor preservation

The 20 winner MIDI SHA-256s (5 songs × 4 stems) recorded pre-render and re-hashed
post-render; must be byte-identical. Recorded in `data/rc10_ab_pairs_refresh/anchor_preservation.json`.

## §D10 Discipline

- No PRNG; no `sidecar_nonfactor` import; `/usr/bin/python3` interpreter guard on every
  top-level script; c48 env-var flags default OFF via `os.environ.setdefault`.
- No transcription changes; no `winner_per_stem.json` edits.
- Do not touch `scripts/palette_render/render_stem.py`, c50 v2 rubric, c53 Branch B/C rubric docs.
- Do not emit drums/bass A/B pairs (owned by clone-0 and clone-1 this cycle).

## §D11 Vocals GM caveat surface

GM 54 "Voice Oohs" is an approximate proxy for a vocal lead line. Surface honestly in
report §Issues that this is an audible timbre choice; c56 may swap to a fluidsynth-compatible
vocal SoundFont if fetchable. Not a blocker; §D6 ±0.5 LU is what gates `AB_REFRESH_LANDS`.

## §D12 Three-way rubric_hash chain

`sha256(docs/rc10_ab_pairs_refresh_rubric.md)`
== content of `data/rc10_ab_pairs_refresh/rubric_hash.txt`
== `verdict.json.rubric_hash`
