---
created: 2026-08-29T05:15:00Z
cycle: 33
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-TEX-1/palette-driven-bare-render
---

# M-TEX-1/palette-driven-bare-render — Cycle 33 Branch A Report

Fork `4595e91f7574`, clone-0. First substantive activation of the c31
palette contract on a real render.

**Verdict: PALETTE_MOVES_PANEL** (all four numeric-family panel keys
moved beyond the frozen 5 % threshold vs the c9 fluidsynth-only
baseline; byte-determinism × 2 confirmed on both `bare_combined.wav`
and every per-stem WAV).

## §1. Frozen rubric verbatim + SHA

The full rubric is at `docs/palette_driven_bare_render_rubric.md`.
It commits the three verdicts (PALETTE_MOVES_PANEL / PALETTE_NEUTRAL /
RENDER_FAILS) and the numeric threshold `PALETTE_DELTA_PCT = 0.05`
against the c9 baseline denominator.

Rubric SHA-256 (`data/palette_render/rubric_hash.txt`):

    ae2f3b50e89d165908f8e53ba2e522d38e45afcc214c0013279781b9fef0e648

This same string is embedded in `data/palette_render/verdict.json`
under key `rubric_hash`. Test §11 asserts byte-equality between doc
SHA, `rubric_hash.txt`, and `verdict.json.rubric_hash`.

## §2. Execution timeline

| Step | Time (UTC)           | Event                                                                             |
|------|----------------------|-----------------------------------------------------------------------------------|
| 1    | 2026-08-29T04:29:xxZ | `workspace/harvest_playlists.sh` invoked — exit=124 (timeout=30s → egress still blocked, as expected per corpus/CORPUS_STATUS.md). Non-blocking. |
| 2    | 2026-08-29T04:30:00Z | `docs/palette_driven_bare_render_rubric.md` written (SHA above).                  |
| 3    | 2026-08-29T04:30:xxZ | `data/palette_render/rubric_hash.txt` written; sleep 2s so scripts have later mtime. |
| 4    | 2026-08-29T04:32–35Z | `scripts/palette_render/{__init__,build_assignments,render_stem,run_all}.py` authored. |
| 5    | 2026-08-29T04:40:00Z | `tests/test_palette_driven_bare_render.py` authored.                              |
| 6    | 2026-08-29T05:00:00Z | Early ledger events emitted (4 events: egress-probe, launched, rubric-frozen, milestone in-progress). |
| 7    | 2026-08-29T05:03:xxZ | `run_all.py` executed — two full pipeline runs into fresh `tempfile.mkdtemp()` dirs; combined SHA byte-identical. |
| 8    | 2026-08-29T05:04:xxZ | Local test PASS (40+ checks). Cross-branch §48 PASS (all 18 new checks).          |
| 9    | 2026-08-29T05:05:xxZ | Verdict roll-up ledger event emitted (validated/high, PALETTE_MOVES_PANEL).       |
| 10   | 2026-08-29T05:06:xxZ | `_run/cycle_33_closed-clone-0` + `_archive/cycle-33-scratch-clone-0` + `_infra/adopt-cycle33-tests-clone-0` emitted; emitter archived to `tools/stale/`. |

## §3. Assignment builder output

`data/palette_render/assignments.jsonl` — three rows, one per stem.

Chosen rule_ids (SHA-256 tiebreak: winner = row with the
lexicographically smallest SHA-256(rule_id) hex, per rule_type on
`data/rules/ledger.jsonl`):

    harmonic:    rule_88b63bd5e771c045
    rhythmic:    rule_51d59f03c4f09e1a
    arrangement: rule_900193a92a8810e5

`provenance_pointers = sorted(chosen.values())`, applied identically
to every assignment row. Per-stem dispatch:

| Stem  | Instrument     | assignment_id                          | Rationale                                                          |
|-------|----------------|----------------------------------------|--------------------------------------------------------------------|
| drums | fluidsynth_gm  | `581c64b1dd9655a0831f294aa636baf2`     | c9 anchored path per brief (SF2 sha `74594e8f…1cb0`).              |
| bass  | sfizz          | `054be70869155fadaa754db97aa8ffc1`     | SFZ (`data/texture/test.sfz`) fetchable + `sfizz_render` present.  |
| other | sfizz          | `5134f5ade55059fd8961e8fc5ea48272`     | Same fetchability probe result.                                    |

Every row passes both layers of `scripts/palette/validate.py` with
zero errors; `assignment_id` recomputes byte-equal via
`scripts.palette.provenance.compute_assignment_id`.

## §4. Per-stem render results

Each stem was rendered twice into fresh `tempfile.mkdtemp()`
directories inside the same pipeline run, and the whole pipeline was
executed twice more into distinct temp dirs (`run1` and `run2`).
Byte-determinism × 2 confirmed on all three stems (SHA-256 abbreviated;
full 64-hex in `data/palette_render/per_stem/<stem>/render_run{1,2}.wav.sha`):

| Stem  | Instrument     | run1 SHA (first 12) | run2 SHA (first 12) | sha_equal |
|-------|----------------|---------------------|---------------------|-----------|
| drums | fluidsynth_gm  | `f66a776dfde8`      | `f66a776dfde8`      | true      |
| bass  | sfizz          | `6b9a5219e761`      | `6b9a5219e761`      | true      |
| other | sfizz          | `a2e5d0585404`      | `a2e5d0585404`      | true      |

`pinned_state.json` per stem captures the MIDI input SHA-256,
sample_rate=44100, sample_count=1_323_000 (=30 s), instrument, and
cross-run sha_equal flag.

## §5. Combined bare SHA × 2

    bare_combined.wav.sha.run1: a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794
    bare_combined.wav.sha.run2: a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794

Byte-identical across two full-pipeline runs. `bare_combined.wav` is
the sum of the three per-stem WAVs at 44.1 kHz stereo, written via
`scipy.io.wavfile.write` (which emits no BEXT/timestamp metadata, so
the file-level SHA is byte-stable — matches the c9 anchor pattern).

## §6. Two panel TSVs (all 8 keys per row)

`data/palette_render/panel_original_vs_palette.tsv`:

| key                          | value              |
|------------------------------|--------------------|
| mel_l1_db                    | 16.5519873         |
| spectral_centroid_rmse_hz    | 1982.9060605       |
| rms_env_rmse                 | 0.0591135          |
| lufs_m_rmse_lu               | 4.8783164          |
| embedding_cosine_distance    | 0.4029 (VGGish)    |
| embedding_rung               | vggish             |
| sr_hz                        | 44100              |
| n_samples_compared           | 1_323_000          |

`data/palette_render/panel_fluidsynth_vs_palette.tsv` (the true
"did the palette add anything?" comparison):

| key                          | value              |
|------------------------------|--------------------|
| mel_l1_db                    | 23.6785361         |
| spectral_centroid_rmse_hz    | 3094.5054817       |
| rms_env_rmse                 | 0.0649894          |
| lufs_m_rmse_lu               | 6.6885347          |
| embedding_cosine_distance    | 0.3290 (VGGish)    |
| embedding_rung               | vggish             |
| sr_hz                        | 44100              |
| n_samples_compared           | 1_323_000          |

Additionally `data/palette_render/panel_original_vs_fluidsynth_c9_baseline.tsv`
is written so the rubric denominator is self-contained and
reproducible from artifacts alone (not taken from any prior TSV).

## §7. Verdict against frozen rubric

Numeric threshold: `PALETTE_DELTA_PCT = 0.05` on

    rel_delta(k) = abs(panel_fluid_vs_palette[k] - baseline_c9[k]) / max(abs(baseline_c9[k]), 1e-12)

where `baseline_c9[k] = panel_original_vs_fluidsynth_c9_baseline[k]`.

| Key                        | baseline_c9      | fluid_vs_palette | rel_delta   | ≥ 5 % ? |
|----------------------------|------------------|------------------|-------------|---------|
| mel_l1_db                  | 9.9060593        | 23.6785361       | 1.390       | YES     |
| spectral_centroid_rmse_hz  | 2804.9113042     | 3094.5054817     | 0.103       | YES     |
| rms_env_rmse               | 0.0275858        | 0.0649894        | 1.356       | YES     |
| lufs_m_rmse_lu             | 2.6821613        | 6.6885347        | 1.494       | YES     |

All four numeric-family keys move above threshold. Verdict:
**PALETTE_MOVES_PANEL**.

Note on interpretation: because the SFZ soundfont is a single-region
sawtooth (the fetchable c31 anchor), the sfizz-rendered bass and
other stems have a very different timbre from fluidsynth's GM
patches. This makes the fluid-vs-palette panel distances substantially
larger than the fluid-vs-original panel baseline, driving rel_deltas
above 100 % on three of the four keys. A more musically realistic
SFZ soundfont would land the render closer to a smaller-but-still
supra-threshold delta; this cycle's finding is that the *contract*
functions and drives the panel numbers, not that this particular SFZ
sounds like real bass.

## §8. Fetchability ladder summary

`data/palette_render/fetchability_ladder.jsonl` (four rows per run):

| Resource                                    | Status | Notes                              |
|---------------------------------------------|--------|------------------------------------|
| /usr/share/sounds/sf2/FluidR3_GM.sf2         | ok     | SHA `74594e8f…1cb0` matches c9 pin.|
| workspace/data/texture/test.sfz              | ok     | Single-region sawtooth (c11 anchor).|
| /usr/bin/fluidsynth                          | ok     | System binary present.             |
| /usr/bin/sfizz_render                        | ok     | System binary present.             |

No `not_determinism_safe` skips triggered — every stem's chosen
instrument was fetchable and byte-deterministic. Surge XT + Dexed
never enter the assignment builder (excluded up-front per c31
STILL_GAP verdicts, matching the rubric's structural exclusion at
the builder layer).

## §9. Read-only anchor preservation

`data/palette_render/anchor_preservation.json` captures mtimes of
every `.py` under `scripts/palette/` and `scripts/palette_probe/`
before and after the pipeline run. Post ≡ pre (`unchanged: true`).
Test §6 asserts this invariant.

Additional read-only reads that touched no files:

  * `data/rules/ledger.jsonl` streamed row-by-row (no writes).
  * `data/tex/renders/synth_030s/{original,bare_midi}.wav` opened
    only for panel measurement.
  * `data/transcribe/basic_pitch/synth_030s/{drums,bass,other}.mid`
    opened only for rendering input.

## §10. Forward look — candidates for cycle 34

  * **Broader assignment-builder sampling**: the current builder
    picks a single (harmonic, rhythmic, arrangement) triple. A
    sub-milestone `M-TEX-1/palette-driven-bare-render/rule-sweep`
    could sweep 8 salted rule triples and measure panel dispersion.
  * **Second seed via `M-INGEST-1/breadth-second-seeds/seed_mid_50s`**:
    apply the same palette-driven-bare-render pipeline to the 50 s
    seed. Would test whether the PALETTE_MOVES_PANEL outcome
    generalizes across seeds.
  * **SFZ soundfont fetchability expansion**: the current SFZ is a
    sawtooth; a more musically realistic bass SFZ (e.g. a GS bass
    or a public-domain electric-bass sample pack) would reduce the
    fluid-vs-palette delta magnitude and give a more nuanced
    "did the palette add anything?" signal.
  * **DawDreamer 0.9.0+ upgrade probe** to close the c31 STILL_GAP
    verdicts on Surge XT + Dexed VST3 pinned-state extraction —
    would let those instruments enter the assignment builder and
    open up much richer palette dispatch.
  * **Upstream `promise_check` parser hardening** (side-note from
    c32): the substring `"milestone id"` in a description silently
    disables that row.

## §11. Cross-branch integration surface

`tests/test_integration_cross_branch.py §48` extends the workspace
integration suite with 18 palette-render invariants (package + script
presence; rubric-doc-before-scripts mtime; per-stem SHA + pinned_state
present for all three stems; verdict.json parseable with rubric hash
embedded; c31 anchor preservation; bare_combined SHA equal across
runs). All 18 checks PASS.

`tests/test_palette_driven_bare_render.py` contains 12 named test
groups covering: interpreter guard, no-PRNG AST, no cycle-9 effects
import, no cycle-13 batch import, no `sidecar_nonfactor`, no writes
under `scripts/palette/`, palette-validator round-trip, per-stem +
combined byte-determinism × 2, 8-key finite panel on both TSVs,
rubric-mtime-before-scripts (with git-log fallback), verdict-JSON
schema conformance, fetchability-ladder presence. All PASS.

## Ledger events (this branch)

Written to the per-clone shadow ledger at
`/home/user/music-gen-instance/fork-4595e91f7574/clone-0/promise_ledger.jsonl`
(routed via `AGENT_FORK_ID` + `AGENT_INSTANCE_DIR` env vars set by
the fan-out conductor). The conductor will `concat_clone_ledgers`
into main on merge. All 8 events under c32 fanout-namespace
convention (infra families suffixed `-clone-0`; substantive `M-*`
milestone_id unsuffixed):

  1. `_infra/egress-probe-cycle-33-clone-0`
  2. `_run/cycle_33_launched-clone-0`
  3. `_plan/palette_driven_bare_render_rubric_frozen-clone-0`
  4. `M-TEX-1/palette-driven-bare-render` (in-progress/medium)
  5. `M-TEX-1/palette-driven-bare-render` (validated/high, verdict roll-up)
  6. `_run/cycle_33_closed-clone-0`
  7. `_archive/cycle-33-scratch-clone-0`
  8. `_infra/adopt-cycle33-tests-clone-0`
