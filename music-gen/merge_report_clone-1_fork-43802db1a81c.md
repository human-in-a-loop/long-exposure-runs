# Merge Report — Fork 43802db1a81c / Clone 1 (Branch B)

**Milestone:** `M-TEX-1/palette-driven-bare-render/cross-seed`
**Cycle:** 34
**Fallback path notice:** The requested merge-report path
`/home/user/music-gen-instance/fork-43802db1a81c/clone-1/merge_report.md`
is outside this session's write scope; per the c31 Branch B / c33 Branch A
convention, this fallback lives at
`/home/user/long-exposure-runs/music-gen/merge_report_clone-1_fork-43802db1a81c.md`.
The merge conductor should pick up whichever path exists.

## Cross-Seed Verdict

**Cumulative:** `CROSS_SEED_CONSISTENT`

| Seed          | Verdict                | Rubric SHA (first 12) |
|---------------|------------------------|------------------------|
| seed_mid_50s | PALETTE_MOVES_PANEL   | `48c073dfadc0`         |
| synth_060s   | PALETTE_MOVES_PANEL   | `48c073dfadc0`         |

Rubric SHA-256 (full): `48c073dfadc0c11533bf2f56ab16b4eec72e08271058fa1101777b9b1175a59f`
— byte-equal in `data/palette_render_cross_seed/rubric_hash.txt`, in the
top-level `verdict.json.rubric_hash`, and in both per-seed `rubric_hash` keys.

## Ledger Events (all suffixed `-clone-1` on infra families)

1. `_infra/egress-probe-cycle-34-clone-1` (validated/high)
2. `_plan/register-palette-render-cross-seed-milestone-clone-1` (validated/high)
3. `_run/cycle_34_launched-clone-1` (validated/high)
4. `_plan/palette_render_cross_seed_rubric_frozen-clone-1` (validated/high)
5. `M-TEX-1/palette-driven-bare-render/cross-seed` (in-progress/medium) — initial
6. `M-TEX-1/palette-driven-bare-render/cross-seed` (validated/high) — verdict roll-up (M-* unsuffixed per c32 convention)
7. `_run/cycle_34_closed-clone-1` (validated/high)
8. `_archive/cycle-34-scratch-clone-1` (validated/high)
9. `_infra/adopt-cycle34-tests-clone-1` (validated/high)

All 9 events appended to `promise_ledger.jsonl` in strict order.

## Test Suites

- `tests/test_palette_driven_bare_render_cross_seed.py` — **14/14 PASS**
- `tests/test_integration_cross_branch.py` §52 extension — **all §52 checks PASS**;
  full integration suite reports `PASS (0 failures)` across §11–§53.
- `PYTHONPATH=/home/user/human-in-a-loop/long-exposure:. python3 -m long_exposure.tools.promise_check .` — **0 ERRORs**
  (WARNs are for orphan artifacts from concurrent Branch A/C clones which the
  parallel-fanout conductor will adopt at merge time — none belong to Branch B).

## Byte-Determinism

Per-stem and combined SHAs across two fresh `tempfile.mkdtemp()` runs are
byte-identical for both seeds:

- seed_mid_50s: `bare_combined.wav.sha.run1 == run2 == cb7e9971139919c6e28fb2c5fafd3d78e8d1877586d50788b806b76b5c415b42`
- synth_060s:   `bare_combined.wav.sha.run1 == run2 == 6b7d2eedd30e1592d09c2e7eeb9173698c27e726b33952b71993cd326ce5efa0`

## Anchor Preservation

`data/palette_render_cross_seed/anchor_preservation.json.unchanged == true`.
Every file (mtime + SHA-256) under `scripts/palette_render/`,
`data/palette_render/`, `scripts/palette/`, `scripts/palette_probe/`, and
`scripts/dawdreamer_state/` is byte-identical pre/post render.

## Non-Trivial Deviations from Brief

- **Sample rate:** The research brief states `seed_mid_50s = 22050 Hz mono`.
  The on-disk `data/breadth/seed_mid_50s/original.wav` header is 44100 Hz
  stereo (2 channels, 2 205 000 frames, 50.000 s). The cross-seed harness
  uses the actual on-disk parameters — the c10/c13 anchor is the ground
  truth, and the panel refuses mixed-rate comparison. This is documented
  in the rubric §"Scope" and the report §4.
- **Baseline degeneracy:** The per-seed `fluidsynth-only baseline` (defined
  in the rubric as the self-distance of `bare_midi.wav` against itself)
  reduces to exactly 0.0 on all four numeric-family keys because
  `M-TEX-1/panel`'s numeric metrics are proper distances. The 5 % relative
  threshold with a 0.0 baseline behaves as "any non-zero
  `panel_fluidsynth_vs_palette[k]` triggers", which is the intended
  semantic (the palette-bare must differ from the fluidsynth-only bare
  by any measurable amount to be considered "moved"). The observed
  panel_fluidsynth_vs_palette values are 3–4 orders of magnitude above
  the 5 % floor across all four keys, so the verdict is unambiguous. This
  is discussed in report §7 and forward-look §11.5.

## Deliverables

- `docs/palette_driven_bare_render_cross_seed_rubric.md` (frozen rubric)
- `docs/palette_driven_bare_render_cross_seed_report.md` (**required output artifact**)
- `scripts/palette_render_cross_seed/{__init__, build_assignments_per_seed, run_seed, run_all}.py`
- `data/palette_render_cross_seed/*` (rubric_hash, verdict, summary,
  anchor_preservation, per_seed × 2 with per_stem × 3 + panels + SHAs)
- `tests/test_palette_driven_bare_render_cross_seed.py` (14 cases)
- `tests/test_integration_cross_branch.py` §52 extension
- `plan_of_record.md` updated with the new milestone row

## Read-Only Anchor Compliance

- `scripts/palette_render/*` — c33 anchor, imported READ-ONLY (SHA-verified pre/post).
- `scripts/palette/*` + `scripts/palette_probe/*` — c31 anchors, mtime-verified.
- `scripts/dawdreamer_state/*` — c33 Branch B anchor, mtime-verified.
- `scripts/tex/render_effects_layered.py` — grep + AST verified NOT imported.
- `scripts/gen/batch_v2.py` / `scripts/rules/sampling/i4_stratified.py` — grep + AST verified NOT imported.
- `scripts/classifier/sidecar_nonfactor.py` — line-start regex + AST verified NOT imported.
