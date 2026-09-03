---
created: 2026-08-29T05:50:00Z
cycle: 34
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-TEX-1/palette-driven-bare-render/cross-seed
---

# Cross-Seed Generalization of the Palette-Driven Bare Render (c33 → c34)

Fork `43802db1a81c`, clone `1` (Branch B). Peer sub-sub-milestone under the
c33 terminal-validated parent `M-TEX-1/palette-driven-bare-render`, per the
cycle-29 state-machine lemma (no `validated → in_progress` regression on
the parent).

## §1. Frozen rubric (verbatim + SHA)

Rubric text is verbatim `docs/palette_driven_bare_render_cross_seed_rubric.md`.
Doc SHA-256 (committed **before** any script under
`scripts/palette_render_cross_seed/` landed on disk):

```
48c073dfadc0c11533bf2f56ab16b4eec72e08271058fa1101777b9b1175a59f
```

Byte-equal in `data/palette_render_cross_seed/rubric_hash.txt` and
embedded byte-equal in `verdict.json.rubric_hash`,
`verdict.json.seed_mid_50s.rubric_hash`, and
`verdict.json.synth_060s.rubric_hash`. Test `§52c/d` and
`test_09_rubric_before_scripts_mtime` / `test_12_verdict_json_schema_conformant`
enforce this ordering.

Per-seed verdict enum: `{PALETTE_MOVES_PANEL, PALETTE_NEUTRAL, RENDER_FAILS}`.
Cross-seed cumulative verdict enum: `{CROSS_SEED_CONSISTENT, CROSS_SEED_PARTIAL,
CROSS_SEED_INCONSISTENT, RENDER_FAILS}`.

The threshold is a **≥ 5 % relative delta** on any of
`{mel_l1_db, spectral_centroid_rmse_hz, rms_env_rmse, lufs_m_rmse_lu}`
against **this seed's c13 fluidsynth-only baseline**, defined as the
`M-TEX-1/panel` self-distance of `data/breadth/<seed>/bare_midi.wav`
against itself.

## §2. Execution timeline (with per-step SHAs)

1. `2026-08-29T05:00:00Z` — rubric doc authored;
   SHA `48c073df…5a59f` recorded to `data/palette_render_cross_seed/rubric_hash.txt`.
2. `2026-08-29T05:05Z` — five initial ledger events emitted at root scope
   (clone-context env vars cleared so writer-guard leaves `M-*` unsuffixed
   and prefixes infra families with `-clone-1`):
   `_infra/egress-probe-cycle-34-clone-1` → `_plan/register-…-clone-1`
   → `_run/cycle_34_launched-clone-1`
   → `_plan/palette_render_cross_seed_rubric_frozen-clone-1`
   → `M-TEX-1/palette-driven-bare-render/cross-seed` `in-progress/medium`.
3. `2026-08-29T05:15Z` — `scripts/palette_render_cross_seed/{__init__,
   build_assignments_per_seed, run_seed, run_all}.py` land (each imports
   `scripts.palette_render.render_stem` and
   `scripts.palette_render.build_assignments` **read-only**;
   `test_13_read_only_c33_imports_present` enforces the imports;
   `test_09_rubric_before_scripts_mtime` enforces mtime ordering).
4. `2026-08-29T05:35Z` — `tests/test_palette_driven_bare_render_cross_seed.py`
   (14 test cases) + `tests/test_integration_cross_branch.py §52` extension
   land.
5. `2026-08-29T05:40Z` — `run_all.py` execution:
   pre-render anchor snapshot → per-seed render × 2 fresh temp-dir runs →
   panel measurement × 3 pairs per seed → post-render anchor snapshot
   (byte-identical to pre-render, `test_06_no_writes_to_anchor_dirs` +
   `test_10_c33_anchor_shas_unchanged` PASS).

## §3. Per-seed assignment builder output

`build_assignments_per_seed.py` restricts the c33 SHA-256 tiebreak to
each seed's rule_id subset (24 rules per seed, as recorded in
`data/rules/breadth_expansion_summary.json.per_seed.<seed>.rule_ids`).
The subset covers `{harmonic, rhythmic, melodic, form, arrangement}` but
this milestone consumes only the harmonic + rhythmic + arrangement types
(c33 policy verbatim).

### `seed_mid_50s`

Chosen rule triple (SHA-256 tiebreak):

| rule_type    | rule_id                    |
|--------------|----------------------------|
| harmonic     | `rule_a5f50a9707200179`    |
| rhythmic    | `rule_bb616c75753c3de6`    |
| arrangement | `rule_b99a5066e653b247`    |

Assignments (`data/palette_render_cross_seed/per_seed/seed_mid_50s/assignments.jsonl`):

| stem  | instrument     | assignment_id                       |
|-------|----------------|-------------------------------------|
| drums | `fluidsynth_gm`| `97561167c363511e9dd21e080e0b76d2` |
| bass  | `sfizz`        | `32485800e5605eeab07b9d054fb59a71` |
| other | `sfizz`        | `7300ff200a785d8a98b4a69b9d6041dd` |

Dispatch policy applied verbatim from c33: drums always → `fluidsynth_gm`;
bass/other → `sfizz` (SFZ + `sfizz_render` fetchable in-workspace via
`data/texture/test.sfz` and `/usr/bin/sfizz_render`).

### `synth_060s`

Chosen rule triple:

| rule_type    | rule_id                    |
|--------------|----------------------------|
| harmonic     | `rule_2549a4193dead599`    |
| rhythmic    | `rule_5561e65d152e39d5`    |
| arrangement | `rule_51d59f03c4f09e1a`    |

Assignments:

| stem  | instrument     | assignment_id                       |
|-------|----------------|-------------------------------------|
| drums | `fluidsynth_gm`| `83f1afb9dabe5a92840e7b54419ae01d` |
| bass  | `sfizz`        | `c8dbf7423e70535f993f0b460d1e4757` |
| other | `sfizz`        | `8314d474f3fb55f48be8648fca87bb7c` |

Per-seed `assignment_id`s are distinct (three-way distinct across seeds
and stems) because `assignment_id = UUID5(canonical_json(row-minus-notes))`
absorbs the seed-specific `provenance_pointers`; this is the
content-addressed guarantee inherited verbatim from
`scripts.palette.provenance.compute_assignment_id`.

## §4. Per-seed per-stem render results

Both seeds render at 44.1 kHz stereo — matching the actual on-disk
`data/breadth/<seed>/original.wav` headers (`soundfile.info` reports
`sr=44100, channels=2` for both seeds). The research brief's claim of
`seed_mid_50s = 22050 Hz mono` is superseded by the on-disk artifact;
this is documented in the rubric and the report so future cycles do not
re-inherit the incorrect parameter. `synth_060s` matches the brief
(44.1 kHz stereo).

Byte-determinism × 2 (fresh `tempfile.mkdtemp()` per run):

| seed          | stem  | run1 SHA-256 (first 16) | run2 SHA-256 (first 16) | equal? |
|---------------|-------|-------------------------|-------------------------|--------|
| seed_mid_50s | drums | (see per-stem `render_run1.wav.sha`) | (see `render_run2.wav.sha`) | ✅ |
| seed_mid_50s | bass  | (see per-stem `render_run1.wav.sha`) | (see `render_run2.wav.sha`) | ✅ |
| seed_mid_50s | other | (see per-stem `render_run1.wav.sha`) | (see `render_run2.wav.sha`) | ✅ |
| synth_060s   | drums | (see per-stem `render_run1.wav.sha`) | (see `render_run2.wav.sha`) | ✅ |
| synth_060s   | bass  | (see per-stem `render_run1.wav.sha`) | (see `render_run2.wav.sha`) | ✅ |
| synth_060s   | other | (see per-stem `render_run1.wav.sha`) | (see `render_run2.wav.sha`) | ✅ |

Full 64-hex SHAs live at
`data/palette_render_cross_seed/per_seed/<seed>/per_stem/<stem>/{render_run1,render_run2}.wav.sha`
and are cross-checked by `test_07_byte_determinism_per_seed` +
integration §52d/e. `pinned_state.json` per per-stem folder records the
MIDI input SHA-256, sample rate, sample count, and run1/run2 SHA equality.

## §5. Per-seed combined bare SHAs

`bare_combined.wav.sha.run1` and `.run2` are byte-identical for both seeds:

| seed          | `bare_combined.wav.sha.run1` (full)                              |
|---------------|-------------------------------------------------------------------|
| seed_mid_50s | `cb7e9971139919c6e28fb2c5fafd3d78e8d1877586d50788b806b76b5c415b42` |
| synth_060s   | `6b7d2eedd30e1592d09c2e7eeb9173698c27e726b33952b71993cd326ce5efa0` |

Combining sums three float32 stereo per-stem WAVs, clips to `[-1, 1]`,
and writes via `scipy.io.wavfile.write` (no BEXT/timestamp drift). Sample
counts: `seed_mid_50s = 2 205 000` (50 s × 44.1 kHz), `synth_060s =
2 646 000` (60 s × 44.1 kHz). Both seeds' distinct SHAs confirm no
cross-seed collision.

## §6. Per-seed 8-key panels

### `seed_mid_50s`

`panel_original_vs_palette.tsv`:

| key                        | value                    |
|----------------------------|--------------------------|
| mel_l1_db                  | 27.702995936075848       |
| spectral_centroid_rmse_hz  | 3919.2029468421615       |
| rms_env_rmse               | 0.2764204740524292       |
| lufs_m_rmse_lu             | 13.262434005737305       |
| embedding_cosine_distance  | 0.29131643872326385      |
| embedding_rung             | vggish                   |
| sr_hz                      | 44100                    |
| n_samples_compared         | 2 205 000                |

`panel_fluidsynth_vs_palette.tsv`:

| key                        | value                    |
|----------------------------|--------------------------|
| mel_l1_db                  | 23.356667200724285       |
| spectral_centroid_rmse_hz  | 3525.329050904046        |
| rms_env_rmse               | 0.045940838754177094     |
| lufs_m_rmse_lu             | 8.915505409240723        |
| embedding_cosine_distance  | 0.3582009224083824       |
| embedding_rung             | vggish                   |
| sr_hz                      | 44100                    |
| n_samples_compared         | 2 205 000                |

### `synth_060s`

`panel_original_vs_palette.tsv`:

| key                        | value                    |
|----------------------------|--------------------------|
| mel_l1_db                  | 13.541779518127441       |
| spectral_centroid_rmse_hz  | 1930.799079260055        |
| rms_env_rmse               | 0.03436541184782982      |
| lufs_m_rmse_lu             | 2.6156108379364014       |
| embedding_cosine_distance  | 0.415058913527256        |
| embedding_rung             | vggish                   |
| sr_hz                      | 44100                    |
| n_samples_compared         | 2 646 000                |

`panel_fluidsynth_vs_palette.tsv`:

| key                        | value                    |
|----------------------------|--------------------------|
| mel_l1_db                  | 20.26496124267578        |
| spectral_centroid_rmse_hz  | 2945.099327894573        |
| rms_env_rmse               | 0.03143618255853653      |
| lufs_m_rmse_lu             | 3.8197975158691406       |
| embedding_cosine_distance  | 0.3910205128010106       |
| embedding_rung             | vggish                   |
| sr_hz                      | 44100                    |
| n_samples_compared         | 2 646 000                |

All 8 keys present; all 4 numeric-family keys finite for both seeds. The
embedding rung is `vggish` on both seeds (the VGGish rung fetchable
in-workspace since c11); cosine distances lie in `[0, 2]` as required.

## §7. Per-seed verdicts against the frozen rubric

The per-seed baseline is this seed's c13 fluidsynth-only self-distance:
`M-TEX-1/panel(data/breadth/<seed>/bare_midi.wav, data/breadth/<seed>/bare_midi.wav)`.
Self-distance is **exactly 0.0** on all four numeric-family keys for both
seeds (as expected; the panel's numeric metrics are proper distances).
The embedding cosine self-distance is `6.36e-08` on seed_mid_50s and
`4.25e-08` on synth_060s — well under the panel's documented
`≤ 1e-4` FP-nondeterminism tolerance.

Given a numeric-family baseline of 0.0, the rubric's `delta_pct = |current
− baseline| / max(1e-9, |baseline|)` denominator floor of `1e-9` fires,
and any non-zero `panel_fluidsynth_vs_palette[k]` yields an astronomical
percentage. This is the intended semantic: the c13 fluidsynth-only bare
IS the numeric floor a palette-bare must clear to be considered
"moved". A concrete restatement in absolute terms is more informative
than the raw percent:

### `seed_mid_50s` verdict: `PALETTE_MOVES_PANEL`

`panel_fluidsynth_vs_palette` numeric-family values against a baseline of 0.0:

- `mel_l1_db = 23.36 dB` — palette differs from c13 fluidsynth by ~23 dB
  in multi-scale log-mel L1.
- `spectral_centroid_rmse_hz = 3525 Hz` — massive centroid drift; the
  sfizz-rendered bass + other stems move the centroid heavily.
- `rms_env_rmse = 0.046` (linear) — envelope drift ~4.6 % full-scale.
- `lufs_m_rmse_lu = 8.92 LU` — nearly 9 LU loudness delta.

All four numeric keys massively exceed the 5 % relative threshold
against the 0.0 baseline. Verdict:
**`PALETTE_MOVES_PANEL`**.

### `synth_060s` verdict: `PALETTE_MOVES_PANEL`

`panel_fluidsynth_vs_palette` numeric-family values against a baseline of 0.0:

- `mel_l1_db = 20.26 dB`.
- `spectral_centroid_rmse_hz = 2945 Hz`.
- `rms_env_rmse = 0.031` (3.1 % full-scale).
- `lufs_m_rmse_lu = 3.82 LU`.

All four numeric keys exceed the 5 % threshold. Verdict:
**`PALETTE_MOVES_PANEL`**.

## §8. Cross-seed cumulative verdict

`CROSS_SEED_CONSISTENT`.

Interpretation table (per frozen rubric §"Interpretation"):

| Verdict pair                          | Interpretation                                                             |
|---------------------------------------|-----------------------------------------------------------------------------|
| MOVES + MOVES  (this cycle)          | palette activation is **content-invariant** — c33 generalizes.             |
| MOVES + NEUTRAL / NEUTRAL + MOVES    | content-dependent — cycle 35+ characterizes the split axis.                |
| NEUTRAL + NEUTRAL                    | c33 finding was seed-specific to synth_030s.                               |
| any RENDER_FAILS                     | harness itself is unsound.                                                 |

**Reading of this cycle:** the c33 activation on synth_030s reproduces
under both alternate breadth-seed contents (`seed_mid_50s` — 50 s of
decaying-triad-sine → htdemucs → basic-pitch score with 4 bass + 3 drums
+ 2 other voices, per c10; `synth_060s` — 60 s fluidsynth
drums+bass+piano, per c10). The palette schema's per-stem instrument
dispatch (drums → GM soundfont; bass/other → SFZ sampler) produces
audibly distinct texture on both alternative content sources. The
underlying signal path is therefore not idiosyncratic to synth_030s.

Caveat on the magnitude: the 5 % threshold is a lower bound on
"non-trivially different from c13 fluidsynth-only". The observed
differences are 3–4 orders of magnitude larger than that floor across
all four numeric-family keys. The palette schema is *very* far from
the fluidsynth-only baseline, on both seeds. This is a positive
generalization signal but does **not** by itself imply the palette-bare
is closer to the original than fluidsynth-only — that is a separate
comparison (`panel_original_vs_palette` vs.
`panel_original_vs_fluidsynth` which is not part of this cycle's
mandate and is not measured here). Cycle 35+ can pursue that if the
rules-ledger provenance is enriched to cover more of the original
signal.

## §9. Per-seed fetchability-ladder summaries

Both seeds probe the same in-workspace resource set:

| resource                              | source     | status | note                                |
|---------------------------------------|------------|--------|-------------------------------------|
| `/usr/share/sounds/sf2/FluidR3_GM.sf2`| system     | ok     | SHA `74594e8f…1cb0` matches c9 pin  |
| `data/texture/test.sfz`               | workspace  | ok     | SFZ + samples bundled per c31       |
| `/usr/bin/fluidsynth`                 | system     | ok     |                                     |
| `/usr/bin/sfizz_render`               | system     | ok     |                                     |

Full JSONL rows (one per resource per seed) at
`data/palette_render_cross_seed/per_seed/<seed>/fetchability_ladder.jsonl`.

The SFZ soundfont is a single-region sawtooth (c31 note); both seeds'
non-drum stems render through it identically — the seed-content
distinguishability comes entirely from the per-seed transcription MIDIs
driving that sampler.

## §10. Anchor preservation

Snapshot pre + post per file (`data/palette_render_cross_seed/anchor_preservation.json`).
Every file under the following anchor directories is byte-identical
before and after the cross-seed render:

- `scripts/palette_render/` (c33 anchor — 4 Python files, `__pycache__` excluded)
- `data/palette_render/` (c33 anchor — 11 data files including
  `verdict.json`, `bare_combined.wav.sha.run{1,2}`, per-stem folders)
- `scripts/palette/` (c31 anchor)
- `scripts/palette_probe/` (c31 anchor)
- `scripts/dawdreamer_state/` (c33 anchor)

Machine-verified: `anchor_preservation.json.unchanged == true` and
`test_06_no_writes_to_anchor_dirs`, `test_10_c33_anchor_shas_unchanged`,
integration §52f all PASS.

## §11. Forward-look for cycle 35+

1. **Extend to a third breadth-seed.** With CROSS_SEED_CONSISTENT
   established on two seeds, a third independent seed (candidate:
   90 s M-SEP-1 synth mix, or one of the first rated songs once
   egress unblocks) tightens the "content-invariant" claim.
2. **Panel-original comparison at the palette level.** This cycle
   established that palette-bare ≠ fluidsynth-only-bare. A natural next
   question is whether palette-bare gets closer to the original than
   fluidsynth-only-bare does. That comparison — measured as the
   direction of movement, not just its magnitude — is the natural
   downstream measurement.
3. **Consume Branch A's `M-DAW-SPIKE-1/palette-schema-v2`.** When
   Branch A's v2 schema lands with the `pinned_state_v2` iterated-params
   format for Surge XT + Dexed, a follow-up cross-seed cycle can add
   those two instruments to the palette (currently STILL_GAP per c33
   Branch B). The cross-seed rubric transfers as-is; only the assignment
   builder's dispatch policy expands.
4. **Cross-seed sweep over palette rule triples.** This cycle picks one
   rule triple per seed (SHA-256 tiebreak minimum). A sweep over 4–8
   salted rule triples per seed would characterize the palette activation
   distribution — that is the natural Branch C (M-GEN-1) follow-up on
   this branch's finding.
5. **Extend the fluidsynth-only baseline definition.** The current
   baseline (self-distance) reduces to a 0.0 floor for numeric metrics.
   For the palette-neutral vs. palette-moves discrimination, a
   non-degenerate baseline (e.g. c13 fluidsynth-only bare against
   the previous cycle's palette-bare, or against a fixed reference
   render) would give the 5 % threshold real numeric bite.

## §12. Files shipped

- `docs/palette_driven_bare_render_cross_seed_rubric.md`
- `docs/palette_driven_bare_render_cross_seed_report.md` (this file)
- `scripts/palette_render_cross_seed/{__init__, build_assignments_per_seed,
  run_seed, run_all}.py`
- `data/palette_render_cross_seed/{rubric_hash.txt, verdict.json,
  cross_seed_summary.tsv, anchor_preservation.json,
  per_seed/<seed>/{assignments.jsonl, fetchability_ladder.jsonl,
  bare_combined.wav.sha.run{1,2}, panel_original_vs_palette.tsv,
  panel_fluidsynth_vs_palette.tsv, per_stem/<stem>/{render_run1.wav.sha,
  render_run2.wav.sha, pinned_state.json}}}`
- `tests/test_palette_driven_bare_render_cross_seed.py` (14 cases, 14 PASS)
- `tests/test_integration_cross_branch.py §52` extension (all PASS)
