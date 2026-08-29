#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:04:00Z
# cycle: 34
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v1
# ---
"""M-GEN-1/palette-driven-batch-v1 — package init.

Cycle 34 Branch C (fork 43802db1a81c, clone-2). First activation of
the c33 palette-render machinery in the M-GEN-1 batch chain, advancing
G5. NEW peer sub-milestone under M-GEN-1 per c29 state-machine lemma
— NOT a child of M-GEN-1/batch-v{1..6} or the collision-modeling arc.

Modules:
  * sample_rule_triple.py — per-salt SHA-256 tiebreak selection of
    one rule per {harmonic, rhythmic, arrangement} from
    data/rules/ledger.jsonl. NO PRNG, NO rejection loop.
  * render_song.py       — per-salt orchestrator: build assignments via
    scripts.palette_render.build_assignments (READ-ONLY import),
    dispatch per-stem via scripts.palette_render.render_stem
    (READ-ONLY), two independent tempdir runs, per-stem + combined
    SHA-256 equality asserted.
  * run_batch.py         — iterates salts 0, 1, 2 through render_song;
    computes panel_original + panel_fluidsynth per salt via
    scripts.texture.panel (READ-ONLY); writes batch_manifest.json,
    summary.tsv, verdict.json, anchor_preservation.json.
  * spread_analysis.py   — per-key (mel_l1_db, spectral_centroid_rmse_hz,
    rms_env_rmse, lufs_m_rmse_lu) IQR + max-min across 3 salts +
    Pearson correlation of per-salt sfizz-count vs mel_l1_db delta.

Read-only anchors (grep-verified untouched):
  * scripts.palette_render.*  (c33 anchors)
  * scripts.palette.*         (c31 palette-v1 anchors)
  * scripts.texture.panel     (M-TEX-1/panel)
  * scripts.tex.render_effects_layered  (c9 chain — NOT imported)
  * scripts.gen.batch_v2*     (c13 pipeline — NOT imported)
  * scripts.rules.sampling.i4_stratified  (c15 — NOT imported)
  * scripts.analysis.*        (c26/c27/c28/c29/c30 — NOT imported)
  * scripts.ear.stability_*   (c22 — NOT imported)
"""
import sys

assert sys.executable == "/usr/bin/python3", sys.executable
