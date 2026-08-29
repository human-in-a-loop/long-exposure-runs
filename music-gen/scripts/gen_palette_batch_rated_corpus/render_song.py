#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T14:34:30Z
# cycle: 43
# run_id: fork-c320de981fda-clone-0
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-rated-corpus
# ---
"""Thin per-salt render wrapper — dispatches to c33 render_stem.

READ-ONLY import of scripts.palette_render.render_stem (carries c36's
additive parameter_dict=None kwarg). Grep-verifiable zero write to
scripts/palette_render/*. VST3 branches raise NotImplementedError on
non-None parameter_dict (c35 anti-pattern locked; c33 render_stem
does not currently ship VST3 dispatch anyway).
"""
from __future__ import annotations

import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette_render.render_stem import (  # noqa: E402
    render_stem, SAMPLE_RATE, SAMPLE_COUNT,
)


def render_one_stem(stem: str, instrument: str, out_dir: Path,
                    parameter_dict: dict) -> dict:
    """Delegate to c33 render_stem verbatim."""
    if instrument in ("surge_xt", "dexed") and parameter_dict is not None:
        raise NotImplementedError(
            "VST3 param_dict path locked (c35 anti-pattern)"
        )
    return render_stem(stem, instrument, out_dir,
                       parameter_dict=parameter_dict)
