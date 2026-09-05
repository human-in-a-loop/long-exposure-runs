# Sweep-Driver Family Policy (v4)

**Landed:** cycle 59 (P4 policy doc; no code changes required).
**Authority:** c58 auditor cumulative-progress finding + operator directive
2026-09-03 part (2) anti-stall rule.

## Problem statement

The v4 sound-matching layer accreted per-instrument sweep drivers as they
were needed:

| Cycle | Driver                              | Instrument | Reason for a new file                     |
|-------|-------------------------------------|------------|-------------------------------------------|
| c1    | `coarse_sweep_sf2.py`               | bass       | first driver (CG bass, cycle-1 target)    |
| c10   | `coarse_sweep_sf2_drums.py`         | drums      | GM channel-10 percussion routing hardcoded|
| c13   | `coarse_sweep_sf2_guitar.py`        | guitar     | GM 24–31 whitelist + guitar track name    |
| c3    | `fine_fit_sf2_v2.py`                | bass       | EQ v2 chain (12-band iirpeak + pyloudnorm)|
| c11   | `fine_fit_sf2_drums.py`             | drums      | c11 channel-aware replay path             |
| c14   | `fine_fit_sf2_guitar.py`            | guitar     | GM 24–31 grid                             |

Each driver has a specific hardcoded assumption in its
`_extract_<instrument>_midi` helper (track name lookup) and its
`_rewrite_<instrument>_midi_with_program` helper (channel + bank/PC insertion
site). Reuse across instruments requires either an additive kwarg thread
(if the assumption is a parameter) or an additive sibling driver (if the
assumption is structural).

As new instruments open (piano, other, vocals), the campaign risks either
(a) unbounded driver-file proliferation, or (b) unsafe edits to
already-READ-ONLY per-instrument anchors. This policy specifies the
decision tree.

## Decision tree (per new-instrument arc)

**When a new instrument arc opens** (e.g. WIG piano stage-1 first-launch):

### Step 1 — OPT_A investigation (audit existing family driver)

Read the closest existing family driver (`coarse_sweep_sf2.py` for
coarse; `fine_fit_sf2_v2.py` for fine) and inspect its
`_extract_<instrument>_midi`, `_rewrite_<instrument>_midi_with_program`,
and any per-instrument constant blocks (GM program whitelist, channel
number).

Ask: **"Is every instrument-specific assumption already parameterized by
existing kwargs (`--song-sha16`, `--stem`, `--reference-stem`,
`--midi-source`, `--midi-excerpt`)?"**

- **If YES → OPT_A adopted.** Reuse driver as-is. Documentation drift
  (docstring saying "bass, cycle-1 CG target") does not require a new
  driver; add an invariant (d) disclosure row noting the shared driver.
  Zero code changes. Cheapest path.

### Step 2 — OPT_B fallback (author additive sibling driver)

**If NO** (hardcoded track name, hardcoded channel, hardcoded GM range,
etc. block reuse) → OPT_B fires. Author a sibling driver
`coarse_sweep_sf2_<instrument>.py` (or `fine_fit_sf2_<instrument>.py`)
following the c10/c11/c13/c14 precedent:

- Copy the closest existing driver verbatim.
- Rename `_extract_bass_midi` → `_extract_<instrument>_midi`; update
  `t.name == "bass"` check to the target instrument's track name.
- Update `_rewrite_bass_midi_with_program` if the target instrument
  uses a non-default MIDI channel (drums = ch 10 idx 9; pitched = ch 0).
- Update GM whitelist if applicable (guitar 24–31; bass 32–39;
  drums-kits GM percussion banks; piano 0–7).
- Disclose SHA drift per invariant (d) via `data/v4/regression/`
  amendment table sidecar (follows c48/c31/c30 shape).
- Add a minimum 8-case regression test suite to
  `tests/test_sound_match_<instrument>_sweep.py` matching the c13
  guitar coverage pattern.

Prefer OPT_A first-pass investigation (cheapest). Fall back to OPT_B
only if hardcoded assumptions truly block reuse.

### Step 3 — Never modify existing per-instrument drivers

Existing drivers (`coarse_sweep_sf2.py` — bass; `coarse_sweep_sf2_drums.py`;
`coarse_sweep_sf2_guitar.py`; and their fine-fit siblings) are READ-ONLY
anchors. Editing them to make them instrument-agnostic would break their
per-anchor SHA and invalidate downstream reproducibility (leaderboard
regressions, replay-proof stability). If OPT_A investigation reveals that
`coarse_sweep_sf2.py` COULD be made generic with a small edit, that edit
is BANNED under this policy — author OPT_B sibling instead.

## Case study: c59 WIG piano stage-1 deferral

**Cycle 59, P3.** OPT_A investigation on `coarse_sweep_sf2.py` found:

- L206 argparse description: `"Family-1 coarse SF2 preset sweep (bass, cycle-1 CG target)."`
- L178 `_extract_bass_midi()`: hardcoded `t.name == "bass"` track name filter.
- L96 `_rewrite_bass_midi_with_program()`: hardcoded `channel=0`
  insertion for bank-select + program-change.
- L266 call site: unconditionally invokes `_extract_bass_midi(merged, dst)`
  regardless of the `--instrument` kwarg value (which is only recorded,
  not consumed).

**Verdict: OPT_B required.** The `--instrument` kwarg is cosmetic; the
driver assumes track name "bass" and channel 0. Piano would need track
name "piano" and channel 0 (still fine for the channel), but requires
a distinct `_extract_piano_midi()` helper. The bank-select and
program-change would work unchanged on channel 0 (piano is a pitched
instrument like bass).

**Action:** author `scripts/sound_match/coarse_sweep_sf2_piano.py` in
c60 (concrete authoring plan below); defer WIG piano stage-1 launch to
c60. Not a preservation-spin deferral per operator directive 2026-09-03
part (2): concrete resume command pinned; scope is honest work-not-done.

### c60 authoring plan for coarse_sweep_sf2_piano.py

1. Copy `scripts/sound_match/coarse_sweep_sf2.py` verbatim to
   `scripts/sound_match/coarse_sweep_sf2_piano.py`.
2. Update docstring L10: `"Family-1 coarse SF2 preset sweep (piano)."`
3. Rename `_extract_bass_midi` → `_extract_piano_midi`; change
   `t.name == "bass"` → `t.name == "piano"`. Rename local variables
   `bass_track` → `piano_track`, `bt` → `pt`. Preserve channel 0
   remap (piano is on channel 0 in WIG merged.mid per stem_midi_probe).
4. Rename `_rewrite_bass_midi_with_program` → `_rewrite_piano_midi_with_program`;
   preserve channel=0 (piano is pitched, same channel-0 convention as bass).
   Change docstring L104 "leaves fluidsynth on the default program 0
   (piano)" is now literal — no change needed.
5. Update `argparse` description L206 to `"...piano..."`.
6. Update call site L266 to `_extract_piano_midi(merged, dst)`.
7. Rename `bass_midi` local → `piano_midi` throughout.
8. Update `n_bass_notes` sanity probe → `n_piano_notes`; update
   `NULL_MIDI_EMPTY` sentinel narrative if desired.
9. Add regression test `tests/test_sound_match_coarse_sweep_sf2_piano.py`
   with ≥8 cases mirroring c13 guitar test coverage: dry-run smoke,
   env-pin regression, interpreter guard, sweep-hygiene wiring,
   NULL_MIDI_EMPTY branch, NULL_STEM_TOO_QUIET branch, distinct
   render SHA per (bank, program) cell, leaderboard TSV shape.
10. Disclose the new file at `data/v4/regression/c60_sweep_driver_amendment_piano.json`
    with SHA pinned + parent (c1 bass coarse driver) SHA byte-identical
    pre==post pins per invariant (d).

Wall estimate: ≤ 30 min authoring + ≤ 15 min test suite = ≤ 45 min
before the first WIG piano stage-1 launch. Fits inside a normal
substantive c60 cycle.

## Coarse-sweep drivers do NOT require OP-1 SerialLock

The OP-1 SerialLock (`data/v4/_run/fine_fit_serial_lock`) is a fine-fit
guard against the VGGish-heavy fine-fit contention that motivated
its introduction in c31. Coarse sweeps (per-cell fluidsynth render +
mel/centroid/embedding score without EQ+compressor grid explosion) are
lightweight enough to run concurrently. Piano coarse stage-1 (c60+)
may run in parallel with any active fine-fit sweep on a different song.

## Cross-arc precedent

This policy formalizes what c10/c11/c13/c14 already did organically.
It also codifies what c28 did organically for the `--song-sha16` alias
additive kwarg (which unblocked drums coarse sweep across all songs
without requiring per-song sibling drivers — that was a legitimate
OPT_A case).

The distinction:

- **OPT_A kwarg thread** for cross-song reuse of the same instrument
  driver (per-song facts live in data per FD-1).
- **OPT_B sibling driver** for cross-instrument reuse when hardcoded
  assumptions block parameterization.

Never modify existing per-instrument drivers.

## Ledger event

Pinned via `_plan/sweep-driver-family-policy-codified-c59` event in
`promise_ledger.jsonl` at cycle 59 close.
