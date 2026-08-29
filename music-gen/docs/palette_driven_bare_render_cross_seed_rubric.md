---
created: 2026-08-29T05:00:00Z
cycle: 34
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-TEX-1/palette-driven-bare-render/cross-seed
---

# Frozen Rubric — M-TEX-1/palette-driven-bare-render/cross-seed

Committed **before** any Python script lands under `scripts/palette_render_cross_seed/`.
Its SHA-256 is recorded verbatim in `data/palette_render_cross_seed/rubric_hash.txt`
and embedded byte-equal into both `seed_mid_50s.rubric_hash` and `synth_060s.rubric_hash`
of `data/palette_render_cross_seed/verdict.json`.

## Scope

Cross-seed generalization test of the c33 `PALETTE_MOVES_PANEL` finding on
the two breadth-second-seeds anchored by c10/c13:

- `seed_mid_50s` — `data/breadth/seed_mid_50s/{original.wav, bare_midi.wav}`
- `synth_060s`  — `data/breadth/synth_060s/{original.wav, bare_midi.wav}`

The c33 machinery (`scripts/palette_render/{build_assignments,render_stem}`)
is imported read-only. Per-seed rule-triple selection restricts the SHA-256
tiebreak to the c12 `M-RULES-1/extraction/breadth-seeds/<seed>` rule_id
subset (enumerated in `data/rules/breadth_expansion_summary.json`).

## Panel key mapping

The M-TEX-1/panel exposes four numeric-family keys plus four
metadata/embedding keys (`PUBLIC_KEYS` of `scripts.texture.panel`):

| Rubric name (brief)              | On-disk panel key (`scripts.texture.panel.PUBLIC_KEYS`) |
|----------------------------------|---------------------------------------------------------|
| `mel_l1_db`                      | `mel_l1_db`                                             |
| `spectral_centroid_rmse_hz`      | `spectral_centroid_rmse_hz`                             |
| `rms_env_rmse`                   | `rms_env_rmse`                                          |
| `lufs_m_rmse`                    | `lufs_m_rmse_lu`  (the panel spells the LU suffix)      |
| `embedding_cosine_distance`      | `embedding_cosine_distance`                             |
| `embedding_rung`                 | `embedding_rung`                                        |
| `sr_hz`                          | `sr_hz`                                                 |
| `n_samples_compared`             | `n_samples_compared`                                    |

The four numeric-family keys used by the ≥5 % activation check are
`{mel_l1_db, spectral_centroid_rmse_hz, rms_env_rmse, lufs_m_rmse_lu}`.

## Per-seed rubric (applied independently to each seed)

### PALETTE_MOVES_PANEL

BOTH must hold:

1. Both `panel_original_vs_palette.tsv` and `panel_fluidsynth_vs_palette.tsv`
   for this seed carry all eight panel keys, and each of the four numeric-family
   keys evaluates to a finite number (not NaN, not ±inf); the embedding cosine
   is either finite in `[0, 2]` or explicitly `null` with an `embedding_rung`
   of `none_available`.
2. In this seed's `panel_fluidsynth_vs_palette.tsv`, at least one of the four
   numeric-family keys differs by **≥ 5 % relative** from the same key measured
   on this seed's c13 fluidsynth-only baseline. The relative delta is computed
   as

   ```
   delta_pct(k) = |value_palette(k) − value_fluidsynth_baseline(k)|
                / max(1e-9, |value_fluidsynth_baseline(k)|)
   ```

   for each of the four numeric-family keys `k`. For this seed, the
   "fluidsynth-only baseline" is the M-TEX-1/panel measurement of
   `(data/breadth/<seed>/bare_midi.wav, data/breadth/<seed>/bare_midi.wav)` —
   i.e. the self-distance of the c13 fluidsynth-only bare against itself,
   which is the numeric floor the palette-bare must clear. This preserves
   c33's "did the palette add anything?" semantic when applied to a seed
   whose c13 fluidsynth-only bare IS the seed-local baseline.

### PALETTE_NEUTRAL

Both panels are 8-key finite as in criterion 1, **and** all four
numeric-family keys in `panel_fluidsynth_vs_palette.tsv` are within
±5 % of the c13 fluidsynth-only baseline of that seed (i.e. the
palette activation exercised end-to-end but collapsed to c13
fluidsynth — either sfizz was not chosen for either non-drums stem, or
the SFZ soundfont was not fetchable in-workspace for this seed's rule
provenance).

### RENDER_FAILS

Any of:

- Any per-stem or `bare_combined.wav` SHA-256 mismatch across two
  independent `tempfile.mkdtemp()` runs.
- Any panel row returns fewer than 8 keys, or any of the four
  numeric-family keys is NaN or ±inf.
- The fetchability ladder logs a non-recoverable error (fluidsynth
  binary missing, SF2 SHA mismatch, sfizz binary missing when sfizz
  was actually dispatched — sfizz absence with fluidsynth_gm fallback
  is recoverable, not fatal).

The rubric is exhaustive over the outcome space. No PARTIAL / WEAK
sub-variants exist at the per-seed level.

## Cross-seed cumulative verdict

Function of the two per-seed labels `(v[seed_mid_50s], v[synth_060s])`:

| `seed_mid_50s` verdict     | `synth_060s` verdict      | cumulative                    |
|----------------------------|---------------------------|-------------------------------|
| PALETTE_MOVES_PANEL        | PALETTE_MOVES_PANEL       | CROSS_SEED_CONSISTENT         |
| PALETTE_MOVES_PANEL        | PALETTE_NEUTRAL           | CROSS_SEED_PARTIAL            |
| PALETTE_NEUTRAL            | PALETTE_MOVES_PANEL       | CROSS_SEED_PARTIAL            |
| PALETTE_NEUTRAL            | PALETTE_NEUTRAL           | CROSS_SEED_INCONSISTENT       |
| RENDER_FAILS (any seed)    | (any)                     | RENDER_FAILS                  |
| (any)                      | RENDER_FAILS (any seed)   | RENDER_FAILS                  |

## Interpretation

- **CROSS_SEED_CONSISTENT** — palette activation is content-invariant;
  the c33 finding generalizes beyond synth_030s.
- **CROSS_SEED_PARTIAL** — content-dependent activation. Cycle 35+
  characterizes which content features drive the split (candidate axes:
  polyphony, envelope shape, per-seed rule-provenance density,
  seed-length interaction with panel windowing).
- **CROSS_SEED_INCONSISTENT** — the c33 result was seed-specific to
  synth_030s; the palette schema exercises correctly but does not add
  texture on either alternative seed.
- **RENDER_FAILS** — cross-seed harness itself is unsound; investigate
  before restating any cross-seed claim.

The rubric is closed. No adjustments after any seed's data lands.
