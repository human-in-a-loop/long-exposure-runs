<!--
created: 2026-09-02T04:30:00Z
cycle: 57
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/gold-set
-->

# RC10 Gold Set — Listening Workflow

## Purpose

Reference procedure for the researcher (human) performing the manual-correction
pass in D3 step 2 of the gold-set build. When no human is available in-cycle,
the fallback in `rc10_gold_set_rubric.md §4` fires: emit the ensemble candidate
verbatim with `confidence: "low"` and flag as `deferred_to_operator`.

## Step 1 — Audio preparation (band-passed slices)

Per (song, stem, section):

1. Slice the original htdemucs 6-stem output for the target stem to the
   section window (peak or exposed, from `focus_set_v3.json`).
2. Produce three band-passed variants:
   - `low`: 20–200 Hz (kick/bass energy)
   - `mid`: 200–2000 Hz (snare/bass fundamentals/low mids)
   - `high`: 2000–20000 Hz (hats/cymbals/attack transients)
3. Use `scipy.signal.butter(order=4, btype='bandpass')` for each band.

## Step 2 — Click track

Choose click source in this order:

1. Branch B (`M-RECREATE-2/.../musical-time`) grid + downbeat estimator winner
   if landed by mid-cycle. Record `branchB_grid_sha` in provenance.
2. Else: c53 clone-2 rc5 tempo anchor. Record fallback in `edit_log.jsonl`
   header.

Synthesize a 25 Hz click at each beat time as a 5-ms sine burst at 0.3 amplitude
mixed into a fresh channel of the listening bounce.

## Step 3 — Side-by-side loop

Load into a DAW or `sox` two-channel loop:

- ch1: original stem slice (unfiltered)
- ch2: `gold_fluidsynth.wav` at ~-6 LU relative
- click track: overlaid on ch1

Play looped at 4-bar boundaries. Focus each pass on one class (kick, then snare,
then ghost-snare, then hats, etc.).

## Step 4 — Edit per note

For each ensemble candidate note in the current section:

- **Accept**: leave in `gold_notes.json`; set `confidence` per §5.
- **Edit**: modify one or more fields; append `{op:"edit", note_index:i, before:{...}, after:{...}, rationale:str, ts:ISO}` to `edit_log.jsonl`.
- **Add**: append `{op:"add", note:{...}, rationale, ts}`.
- **Remove**: append `{op:"remove", note_index:i, before:{...}, rationale, ts}`.

## Step 5 — Confidence labels

- `high`: unambiguous audible hit AND spectral evidence in the appropriate
  band-passed slice AND the class assignment is unambiguous.
- `medium`: audible but marginal — weak hit, low-SNR ghost, borderline pitch
  ambiguity of ±1 semitone, articulation guessed.
- `low`: uncertain. Note is retained, but operator listening resolution is
  required. Every `low`-confidence note surfaces in report §Issues.

## Step 6 — Cross-stem coonset flagging (D4)

For each accepted `class == "kick"` drum onset, listen to the bass stem's
same time window (± 30 ms) with the same band-passed slicing. Record
`kick_bass_coonset: bool` alongside `relative_energy_drum_low` and
`relative_energy_bass_low` (both computed automatically post-hand-correction).

## Step 7 — Determinism guarantee

`edit_log.jsonl` is append-only. Replaying the log deterministically
reproduces `gold_notes.json` from the ensemble candidate. No PRNG.
