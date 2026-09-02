---
created: 2026-09-02T23:15:00Z
run_id: run-2026-09-02T231500Z
cycle: 21
agent: worker
milestone: M-V3-SPINE-1/chicken-grease-palette-render
---

# Chicken Grease Surge XT / sfizz Palette Render — Cycle 21 Rubric (frozen)

Song: Chicken Grease, `audio_sha16 = 31a164f845f8e27e`, operator-section
`t = 233.63918 .. 263.63918 s`.

This rubric is committed BEFORE any Python edit under
`scripts/v3_spine/palette_render/`. The rubric SHA is pinned to
`data/v3_spine/31a164f845f8e27e/palette_render/rubric_hash_v2.txt`.
Three-way rubric_hash_v2 byte-equality is asserted at verdict time
(doc SHA-256 == `rubric_hash_v2.txt` content == `verdict_palette.json.rubric_hash_v2`).

## Frozen 3-verdict rubric

### PALETTE_MOVES_PANEL

All of:

1. Every per-stem render succeeds OR is honestly logged as a
   REDEFINED_GAP or SMALL_PERTURBATION_TOLERABLE arm with fallback data
   present.
2. Per-stem byte-determinism × 2 holds on each rendered WAV OR the
   VST3-stem's 3-fresh-tempdir pairwise RMS envelope satisfies
   `max_pairwise_rms ≤ 1e-4` per the c36 clone-2 small-perturbation
   characterization (SMALL_PERTURBATION_TOLERABLE arm).
3. Comparison B panel — `(c5 fluidsynth-render, palette-render)` on
   the operator section — shows delta magnitudes exceeding the 5%
   threshold on ≥ 3 of the 8 panel keys.
4. c5 operator-blessed delivery byte-identical pre==post (hard).

### PALETTE_NEUTRAL

Renders succeed and byte-determinism gate holds, but Comparison B panel
deltas fall below the 5% threshold on ALL 8 keys.

### RENDER_FAILS

Any of:

- Per-stem byte-determinism × 2 fails on a non-VST3 stem, OR
- Bass VST3 render fails all 3 fresh-tempdir attempts AND
  `max_pairwise_rms > 1e-4` (structural drift, not envelope-tolerable).
- Fetchability failure that leaves any required stem without a
  renderable pipeline (fluidsynth_gm fallback failure counts).
- Either comparison panel returns non-finite on any of the 8 keys.
- c5 operator-blessed delivery drifts (any anchor SHA changes).

## Panel-is-never-a-LANDS-gate reminder (FD-6)

The panel is a diagnostic measurement, not a LANDS gate. The rubric
above fires `PALETTE_MOVES_PANEL` on the *comparison B delta magnitude
criterion*; it never fires LANDS on any panel-numeric-passes-threshold.
Operator ear remains the only LANDS authority per FD-6. This cycle's
verdict carries `blocked_on_operator = true`.

## Render pipeline (frozen at rubric commit)

| Stem   | Instrument                                        | Fallback                        |
|--------|---------------------------------------------------|---------------------------------|
| drums  | fluidsynth GM channel 10 (c5 unchanged)           | (n/a — GM baseline)             |
| bass   | Surge XT VST3 via DawDreamer + c33 P1 hydration   | REDEFINED_GAP arm on VST3 fail  |
| guitar | sfizz first; fluidsynth_gm(25) fallback           | fluidsynth_gm(25 clean electric)|
| piano  | sfizz first; fluidsynth_gm(0) fallback            | fluidsynth_gm(0 acoustic grand) |
| other  | sfizz first; fluidsynth_gm(88) fallback           | fluidsynth_gm(88 new age pad)   |
| vocals | htdemucs vocals stem verbatim (D2, from c5)       | (n/a — verbatim copy)           |

## Anti-patterns locked

- `get_state` / `save_state` / `save_preset` / `load_state` /
  `set_state(bytes)` on VST3 — AST-forbidden (c31 STILL_GAP + c35 A).
- CLAP fetch — not attempted; VGGish rung is authoritative.
- No `M-EAR-1/*` events emitted from this branch.

## Environment pins (every subprocess)

`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
`LC_ALL=C.UTF-8`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`, `torch.manual_seed(0)`.

## Read-only anchors

The following must survive pre == post byte-identical:

- c5 delivery: `data/v3/deliveries/31a164f845f8e27e/` root and
  `operator_section/`.
- c5 canonical per-stem MIDIs at
  `data/v3_spine/31a164f845f8e27e/operator_section/canonical_midi/*.mid`.
- c5 htdemucs vocals: `data/v3_spine/31a164f845f8e27e/operator_section/render/vocals_htdemucs.wav`.
- c6 Method B: `data/v3_spine/rc7_v2_v3_paths/`.
- c33 palette-render anchor: `scripts/palette_render/render_stem.py`
  (SHA `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`).
- c53 rc7 chain: `scripts/recreate_v2/rc7_mix_balance.py`.
- c6 v3-paths chain: `scripts/v3_spine/rc7_v2_rerun_v3_paths.py`.
- SF2: `/usr/share/sounds/sf2/FluidR3_GM.sf2` (SHA
  `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`).
- Rubric v1: `docs/v3_spine_rubric.md`.
- Rubric v2: `docs/v3_spine_rubric_v2.md` (SHA
  `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`).

Pre and post anchor snapshots are pinned to
`data/v3_spine/31a164f845f8e27e/palette_render/anchor_preservation.json`
(≥ 60 SHAs). `all_match = true` is a hard gate.
