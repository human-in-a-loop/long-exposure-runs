---
created: 2026-08-29T04:30:00Z
cycle: 33
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-TEX-1/palette-driven-bare-render
---

# M-TEX-1/palette-driven-bare-render — Frozen Verdict Rubric

Cycle 33 Branch A (fork 4595e91f7574, clone-0). This rubric is committed
BEFORE any script under `scripts/palette_render/` lands. Its SHA-256 is
recorded verbatim in `data/palette_render/rubric_hash.txt` and embedded
in `data/palette_render/verdict.json` under key `rubric_hash`. Test
`tests/test_palette_driven_bare_render.py` enforces (a) that the rubric
doc's mtime precedes the earliest add of any `scripts/palette_render/*.py`
(git-log ordering with mtime fallback), and (b) that the rubric SHA is
byte-identical between doc, `rubric_hash.txt`, and `verdict.json`.

## Threshold constant

`PALETTE_DELTA_PCT = 0.05` (5 percent, relative).

The delta is computed on the **c9 fluidsynth-only baseline** as denominator:

    rel_delta(key) = abs(palette[key] - baseline_c9[key]) / max(abs(baseline_c9[key]), 1e-12)

Where `baseline_c9[key]` is the value of that key in the
`panel_original_vs_fluidsynth` measurement (original 30 s synth mix vs
`data/tex/renders/synth_030s/bare_midi.wav`). This measurement is
computed by this cycle inside `run_all.py` and stored as the
reference vector for the comparison; it is NOT taken from any prior
cycle's TSV so that the delta stays self-contained and reproducible.

The four numeric-family keys watched:

  * `mel_l1_db`
  * `spectral_centroid_rmse_hz`
  * `rms_env_rmse`
  * `lufs_m_rmse_lu`

(Embedding-family keys `embedding_cosine_distance` and `embedding_rung`
are recorded but do NOT enter the rubric decision; the CLAP/VGGish
fetchability history — cycles 11/14 — means the embedding value can be
`None` and no non-fetchable embedding surprise should flip the render
verdict.)

## Three verdicts

### PALETTE_MOVES_PANEL

All of the following must hold:

  * Both `panel_original_vs_palette.tsv` and `panel_fluidsynth_vs_palette.tsv`
    contain a data row with all 8 keys from `PUBLIC_KEYS` in
    `scripts.texture.panel`, every numeric-family value finite (not
    NaN, not ±inf).
  * At least one of the 4 numeric-family keys in
    `panel_fluidsynth_vs_palette.tsv` differs from the same key in
    `panel_original_vs_fluidsynth` (i.e. the c9 baseline the run
    computes) by `rel_delta >= PALETTE_DELTA_PCT`.

Interpretation: the palette activation altered the timbre in a
measurable way. sfizz was chosen for at least one stem AND its SFZ
soundfont was fetchable AND the resulting render's texture panel
differs from the pure-fluidsynth baseline.

### PALETTE_NEUTRAL

  * Both panels 8-key finite (as above).
  * All 4 numeric-family keys in `panel_fluidsynth_vs_palette.tsv`
    within `± PALETTE_DELTA_PCT` of the c9 baseline (rel_delta < threshold).

Interpretation: the assignment schema activated correctly, the render
completed, but every stem's assignment resolved to `fluidsynth_gm`
(either because the assignment builder chose `fluidsynth_gm` on
SHA-256 tiebreak, or because the SFZ soundfont was not fetchable
in-workspace and the fallback ladder demoted the stem to
`fluidsynth_gm` with `not_determinism_safe = sfz_not_fetchable`).
This is a first-class outcome — the schema is exercised end-to-end
even though the resulting audio collapses to the c9 fluidsynth
baseline.

### RENDER_FAILS

Any of:

  * A per-stem `render_run1.wav.sha` ≠ `render_run2.wav.sha`
    (byte-determinism × 2 violation on any stem).
  * The two combined `bare_combined.wav.sha` values differ across the
    two full-pipeline runs.
  * A panel returns fewer than 8 finite numeric-family keys, or a
    finite-family key is NaN / ±inf.
  * The fetchability ladder logs a non-recoverable error preventing
    render completion (`fluidsynth` binary missing, `sfizz_render`
    binary missing while sfizz was chosen and no fallback fired,
    SF2 SHA mismatch, invalid MIDI path, etc.).

Interpretation: the measurement chain broke; the render is not
usable as a determinism-verified palette activation.

## Binary structure

Either the rubric ≤ measurement (verdict ∈ {PALETTE_MOVES_PANEL,
PALETTE_NEUTRAL}) or the measurement chain broke (verdict =
RENDER_FAILS). There are no PARTIAL, WEAK, or MIXED variants. The
verdict is written to `data/palette_render/verdict.json` alongside
the four rel_deltas and the frozen `PALETTE_DELTA_PCT`, so the
same JSON both records the outcome AND documents the numeric
threshold that produced it.

## Anchors, honesty, exclusions

  * Cycle-9 `scripts/tex/render_effects_layered.py` is a READ-ONLY
    anchor. Test grep-verifies zero import under any Branch A
    script.
  * Cycle-13 batch pipeline (`scripts.gen.batch_v2`,
    `scripts.rules.sampling.i4_stratified`) is a READ-ONLY anchor.
    Test grep-verifies zero import under any Branch A script.
  * Cycle-31 palette anchors (`scripts/palette/*`,
    `scripts/palette_probe/*`) are READ-ONLY anchors. Test enforces
    that every file mtime under those directories equals its c31
    snapshot (compared against the pre-run manifest recorded in
    `data/palette_render/anchor_preservation.json`).
  * Surge XT and Dexed are EXCLUDED from this render per cycle-31
    STILL_GAP verdicts. The exclusion is enforced at two layers:
      1. The `SKIP_COMBOS` layer 2 check in `scripts/palette/validate.py`
         (Dexed × drums is already flagged); this cycle extends the
         invariant conceptually by refusing to assign `surge_xt` or
         `dexed` at all — the assignment builder never places them
         in a candidate row.
      2. Any invalid or non-determinism-safe combo would be
         documented in the fetchability ladder with skip reason
         `not_determinism_safe`.
  * No PRNG. All choices via SHA-256 tiebreak on rule_id or
    canonical-JSON bytes.
  * `/usr/bin/python3` interpreter guard on every Branch A script.
  * No `sidecar_nonfactor` imports; non-factor AST isolation
    preserved.

## Frozen. Do not edit after commit.

Any change to this document must be through a new peer rubric under a
new sub-milestone. Retroactive edits break the pre-registration
integrity that the whole cycle depends on.
