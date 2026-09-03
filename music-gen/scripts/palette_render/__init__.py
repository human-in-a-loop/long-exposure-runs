#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T04:32:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render
# ---
"""M-TEX-1/palette-driven-bare-render — package init.

Cycle 33 Branch A. First substantive activation of the c31 palette
contract on a real render. Package composition:

  * build_assignments.py — resolve three rules → per-stem palette
    assignments; validated through both layers of scripts.palette.validate.
  * render_stem.py — dispatch per-stem to fluidsynth CLI or sfizz_render CLI.
  * run_all.py — orchestrator: two independent temp-dir runs, panel
    measurements, verdict.

Read-only anchors (never imported at package level):
  * scripts.tex.render_effects_layered (cycle 9)
  * scripts.gen.batch_v2, scripts.rules.sampling.i4_stratified (cycle 13)
  * scripts.palette.* and scripts.palette_probe.* — imported READ-ONLY
    (provenance + validator only).
"""
import sys

assert sys.executable == "/usr/bin/python3", sys.executable
