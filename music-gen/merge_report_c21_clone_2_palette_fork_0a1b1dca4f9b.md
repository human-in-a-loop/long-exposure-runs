# Merge report — c21 fork `0a1b1dca4f9b` clone-2 palette-render

Target path (outside sandbox):
`/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-2/merge_report.md`
— root conductor please `cp` this file into place at merge time.

## Scoped objective

Land the operator-D-D-directed Surge XT / sfizz palette render on
Chicken Grease (`audio_sha16 = 31a164f845f8e27e`) operator-section
`t = 233.63918 .. 263.63918 s` as sibling secondary deliverable to the
operator-LANDED c5 v3 fluidsynth reconstruction.

## Outcome

**Verdict: `PALETTE_MOVES_PANEL`** — three-way `rubric_hash_v2` chain
holds; per-stem byte-det gate holds across all 6 stems; both panels
8-key finite; Comparison B `(c5 fluidsynth, palette)` delta magnitudes
exceed 5 % relative threshold on 4 / 5 numeric keys. `blocked_on_operator
= true` per FD-6. Per operator D-D: if operator confirms audibly, this
palette render becomes the c22 input to the palette-becomes-primary
decision campaign-wide.

## On-disk artifacts

- Report: `docs/v3_spine_chicken_grease_palette_render_c21_report.md`
- Rubric: `docs/v3_spine_chicken_grease_palette_render_c21_rubric.md`
  (SHA `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879`)
- Verdict: `data/v3/deliveries/31a164f845f8e27e/cycle21/verdict_palette.json`
  (SHA `5ba4eaca242fcd29…`)
- Full palette reconstruction: `data/v3/deliveries/31a164f845f8e27e/palette_render/full_reconstruction_palette.wav`
  (SHA `17fe1dad639b44b5…`)
- Per-stem palette WAVs: `data/v3/deliveries/31a164f845f8e27e/palette_render/per_stem/{drums,bass,guitar,piano,other,vocals}/render.wav`
- Delivery manifest: `data/v3/deliveries/31a164f845f8e27e/palette_render/manifest.json`
- Panels: `data/v3/deliveries/31a164f845f8e27e/palette_render/panel_original_vs_palette.tsv`,
  `data/v3/deliveries/31a164f845f8e27e/palette_render/panel_fluidsynth_vs_palette.tsv`
- Byte-det + fetchability sidecars: `data/v3/deliveries/31a164f845f8e27e/palette_render/{byte_determinism.json,fetchability_ladder.jsonl}`
- Anchor preservation: `data/v3_spine/31a164f845f8e27e/palette_render/anchor_preservation.json`
  (phase=post, all_match=true, n_mismatch=0, n_entries=61)
- Impl scripts: `scripts/v3_spine/palette_render/{__init__,anchor_preservation,render_palette,mix_and_deliver,panels_and_verdict}.py`
- Tests: `tests/test_v3_spine_chicken_grease_palette_render_c21.py` — 12/12 green

## Ledger events (11)

Concatenated into main ledger (workspace shadow-ledger auto-routed via
c33 harness guard). Registered in `plan_of_record.md` this cycle (10 new
milestone rows: 1 substantive umbrella, 6 named sub-leaves,
1 M-INGEST-1 egress-probe row, plus 2 housekeeping under `-clone-2`
suffix + 1 `_plan/register` + 1 `_run/palette-render-cycle-21-clone-2`).

    _plan/register-c21-palette-render-milestones
    M-V3-SPINE-1/chicken-grease-palette-render/rubric-committed
    M-V3-SPINE-1/chicken-grease-palette-render/fetchability-probed
    M-V3-SPINE-1/chicken-grease-palette-render/per-stem-rendered
    M-V3-SPINE-1/chicken-grease-palette-render/panel-emitted
    M-V3-SPINE-1/chicken-grease-palette-render/delivery-emitted
    M-V3-SPINE-1/chicken-grease-palette-render/verdict-emitted
    _archive/cycle-21-palette-scratch-clone-2
    _infra/adopt-cycle21-palette-scripts-clone-2
    M-INGEST-1/egress-probe-cycle21-clone-2
    _run/palette-render-cycle-21-clone-2

`promise_check` returns **0 ERRORs** post-emission (WARN set unchanged
from cycle start — all pre-existing).

## Cross-branch conflict scan

None. Writes disjoint under
`data/v3_spine/31a164f845f8e27e/palette_render/` and
`data/v3/deliveries/31a164f845f8e27e/palette_render/` (both new
directories) plus `data/v3/deliveries/31a164f845f8e27e/cycle21/`. The c5
operator-blessed operator_section delivery is byte-identical pre == post
(hard gate) — no overwrite risk. `scripts/palette_render/render_stem.py`
and `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` SHAs byte-identical
pre == post (do-not-touch invariants preserved).

## Honest handoffs to c22 / operator

1. **Surge XT VST3 REDEFINED_GAP arm** — 2855 / 2855 params hydrate but
   render diverges with `max_pairwise_rms = 0.068` on Chicken Grease
   bass content, three orders of magnitude beyond the c36
   `SMALL_PERTURBATION_TOLERABLE ≤ 1e-4` envelope. fluidsynth_gm(33
   electric bass finger) fallback engaged and delivers byte-det bass.
   VST3 characterization preserved verbatim in `byte_determinism.json`
   and `fetchability_ladder.jsonl`. c31 STILL_GAP (`get_state`,
   `save_state`, `set_state(bytes)`) anti-patterns remain AST-forbidden
   and NOT re-attempted.

2. **sfizz coverage 0 / 3** — `workspace/palette/sfz/` does not exist,
   so every sfizz-eligible stem (guitar / piano / other) falls through
   honestly to fluidsynth_gm(25 / 0 / 88). A future cycle with egress
   open (currently HTTP 429 / tv_embedded per c47 + registry) can
   populate the SFZ palette and re-render for a true sampler-based
   palette test.

3. **Operator ear on palette A/B** — the Comparison A audibility test
   materializes as `data/v3/deliveries/31a164f845f8e27e/palette_render/full_reconstruction_palette.wav`
   played against
   `data/v3/deliveries/31a164f845f8e27e/operator_section/original_ab_operator_section.wav`.
   Verdict is `PALETTE_MOVES_PANEL` numerically; whether the shift is
   audibly *better* than the c5 fluidsynth reference is the operator's
   call per FD-6.

4. **If operator confirms** — per D-D, c22 opens the palette-becomes-
   primary decision. The four remaining M-V3-FOCUS-1 songs (WIG /
   Dojo Cuts Rome / Peach Dream / Disco A) can then be re-rendered via
   the palette pipeline as a batch.

5. **Merge-report cp** — this file needs to be `cp`ed by the root
   conductor to `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-2/merge_report.md`
   at merge time (path outside the workspace sandbox — same limitation
   as c20 clone-2 Peach Dream merge report).
