---
created: 2026-08-29T07:20:00Z
cycle: 36
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/palette-driven-batch-v3
---

# Rubric — M-GEN-1/palette-driven-batch-v3 (Cycle-36 Branch B)

Committed BEFORE any Python edit to `scripts/palette_render/render_stem.py`
or any new script under `scripts/palette_render_v3/`. Rubric SHA-256 of
this file (mtime-ordered ahead of scripts) is recorded verbatim in
`data/palette_render_v3/rubric_hash.txt` and embedded in
`data/palette_render_v3/verdict.json`.

## Context

C35 clone-1 diagnosed `SPREAD_STILL_COLLAPSED`: c33
`scripts.palette_render.render_stem(stem, instrument, out_dir)` is
`(stem, instrument)`-parameterized only and never consumes
`pinned_state`, `provenance_pointers`, or `iterated_params`. This branch
extends the signature (non-breaking, additive) to accept
`parameter_dict` for fluidsynth/sfizz dispatchers so per-salt rule
triples move audio bytes.

## Frozen 3-verdict rubric

### `PARAM_MOVES_AUDIO`

ALL of the following hold:

1. **Backwards-compat regression PASS.** With
   `render_stem(..., parameter_dict=None)`, the three c33 anchor SHAs
   for the c33 salt-0 assignment (bass, other, combined for
   `synth_030s`) MUST match byte-identically:
     - `bass` SHA = `6b9a5219e761854bdcf42a87f370a283e3fb096faf64648eb198c98520540280`
     - `other` SHA = `a2e5d0585404b448a2120c3c4bd6432ec1962ed82c3a7a74dd7518ed3d10f621`
     - `bare_combined` SHA = `a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794`
2. **Per-salt byte-determinism × 2.** For each salt s ∈ {0, 1, 2},
   two independent `tempfile.mkdtemp()` renders through the extended
   `render_stem` with `parameter_dict` populated MUST yield SHA-256
   equal `bare_combined.wav` (and per-stem WAVs).
3. **Cross-salt SHA INequality on `bare_combined.wav`.** All three
   pairwise comparisons (0,1)/(0,2)/(1,2) MUST differ, OR at least
   two of three MUST differ with the third's identity attributed to
   a documented parameter-table shallowness.
4. **Panel finiteness.** Both `panel_original.tsv` and
   `panel_fluidsynth.tsv` MUST return all 8 keys, with all four
   numeric-family keys finite, per salt.

### `PARAM_NEUTRAL`

Criteria (1) and (2) hold, but criterion (3) fails — cross-salt
`bare_combined.wav` SHAs are identical across all three pairs. The
parameter table is too shallow to move fluidsynth/sfizz CLI bytes.
First-class negative finding; hand `M-GEN-1/palette-driven-batch-v4`
(deeper perturbation, wider parameter table) to c37.

### `RENDER_FAILS`

Criterion (1) fails on any of the three c33 anchor SHAs (unacceptable
backwards-compat break) OR criterion (2) fails on any salt. First-class
negative finding; hand `_manager/c33-render-stem-signature-extension-triage`
to c37.

## Parameter perturbation table (fixed, SHA-256-derived per rule)

For each `(rule_id, param_name)` pair, `SHA-256(f"{rule_id}|{param_name}".encode("utf-8"))`
yields a digest; `int.from_bytes(digest[:4], "big") % 4` indexes into the
appropriate 4-entry table below.

### Fluidsynth (drums + fluidsynth_gm fallback)

| param              | index 0 | 1     | 2     | 3     |
|--------------------|---------|-------|-------|-------|
| `chorus_level`     | 0.3     | 0.5   | 0.7   | 0.9   |
| `reverb_level`     | 0.2     | 0.4   | 0.6   | 0.8   |
| `reverb_room_size` | 0.4     | 0.5   | 0.6   | 0.7   |
| `gain`             | 0.6     | 0.75  | 0.9   | 1.05  |

### Sfizz opcode overrides (bass/other, if `sfizz_render --set` supported)

| param                     | index 0 | 1    | 2   | 3    |
|---------------------------|---------|------|-----|------|
| `master_volume` (dB)      | -3      | -1.5 | 0   | 1.5  |
| `master_pitch_offset` (¢) | -2      | 0    | 2   | 4    |
| `envelope_attack_mult`    | 0.5     | 0.75 | 1.0 | 1.25 |
| `envelope_release_mult`   | 0.75    | 1.0  | 1.25| 1.5  |

If `sfizz_render --set` is unsupported, this cycle falls back to
threading fluidsynth-family gain envelope on the sfizz-dispatched stem
via a documented `dispatch_summary.json` fallback record. If BOTH fail
per stem, the stem's dispatch collapses to `fluidsynth_gm` with the
fluidsynth parameter table applied instead (fully documented per-salt).

## VST3 exclusion

`surge_xt`, `dexed`: any non-None `parameter_dict` raises
`NotImplementedError("VST3 param threading deferred to c37 pending
Branch-C VST3-nondeterminism verdict")`. VST3 dispatch is intentionally
NOT touched this cycle; c35 Branch A's `V2_MOVES_PANEL`-blocked-by-`RENDER_FAILS`
result placed VST3-binary-internal nondeterminism as an anti-pattern-locked
surface. Branch C characterizes analytically; Branch B routes around.

## Discipline

* c33 `render_stem` backwards-compat is a HARD GATE. Any break of the
  three anchor SHAs when `parameter_dict=None` is `RENDER_FAILS`;
  do NOT hide the break by editing the c33 anchor path.
* c31 STILL_GAP anti-pattern (get_state/save_state/save_preset/load_state/
  set_state(bytes)) is NOT re-opened.
* c9 chain (`scripts.tex.render_effects_layered`) NOT imported.
* c13 batch pipeline, c15 `i4_stratified.py`, c22 stability harness,
  c26/27/28/29/30 collision-modeling utilities NOT imported.
* `data/rules/ledger_i3_dminor.jsonl` NOT read.
* No `M-EAR-1/*` events emitted.
* PARAM_NEUTRAL is first-class if the table is too shallow — surface
  honestly; do NOT deepen mid-cycle to force PARAM_MOVES_AUDIO.
* α pinned at 0.7469387071101908 (unused this branch; no collision
  utilities imported).
* SHA-256 tiebreak throughout; no PRNG (AST-grep enforced).
* No `sidecar_nonfactor` imports.
* `-clone-1` suffix on all infra-family ledger events; substantive
  `M-GEN-1/palette-driven-batch-v3` unsuffixed per c32 convention.

## Ordering guarantee

This rubric's on-disk mtime is BEFORE any file under
`scripts/palette_render_v3/` AND BEFORE the additive-kwarg edit to
`scripts/palette_render/render_stem.py`. Test §16(iii) enforces via
`stat().st_mtime` + git-log fallback.
