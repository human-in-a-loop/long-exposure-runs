#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:15:00Z
# cycle: 34
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render/cross-seed
# ---
"""Cross-seed generalization of the c33 palette-driven bare render.

Read-only imports from `scripts.palette_render.{build_assignments, render_stem}`
via `build_assignments_per_seed.py` and `run_seed.py` — grep-verified this
module does NOT write to `scripts/palette_render/` or `data/palette_render/`.

NO PRNG. Interpreter-guarded /usr/bin/python3. No `sidecar_nonfactor` imports.
No import of `scripts.tex.render_effects_layered` (c9 anchor).
No import of `scripts.gen.batch_v2` / `scripts.rules.sampling.i4_stratified` (c13/c15).
"""
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

SEEDS = ("seed_mid_50s", "synth_060s")
NUMERIC_FAMILY_KEYS = (
    "mel_l1_db",
    "spectral_centroid_rmse_hz",
    "rms_env_rmse",
    "lufs_m_rmse_lu",
)
PALETTE_DELTA_PCT = 5.0  # % relative delta threshold per rubric.
