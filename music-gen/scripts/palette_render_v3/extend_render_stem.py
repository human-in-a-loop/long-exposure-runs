#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T07:25:00Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v3
# ---
"""Documentation shim for the additive-kwarg extension of c33 render_stem.

This module DOES NOT redefine render_stem. It only:
  1. Re-exports the (now-extended) c33 render_stem from
     ``scripts.palette_render.render_stem`` so callers can bind the
     API at a c36-Branch-B-specific import path if desired.
  2. Provides a ``signature_summary()`` helper that inspects the
     upstream ``render_stem`` and asserts the ``parameter_dict``
     keyword-only parameter exists with default None.
  3. Provides the ``VST3_INSTRUMENTS`` frozenset that callers can
     query before dispatching.

The actual extension is inline in
``scripts.palette_render.render_stem.render_stem`` (additive kwargs
only; backwards-compat verified in
``data/palette_render_v3/backwards_compat_check.json``).
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette_render.render_stem import (  # noqa: E402
    render_stem,
    render_fluidsynth,
    render_sfizz,
    SAMPLE_RATE,
    SAMPLE_COUNT,
)

VST3_INSTRUMENTS = frozenset({"surge_xt", "dexed"})
PARAMETERIZED_INSTRUMENTS = frozenset({"fluidsynth", "fluidsynth_gm", "sfizz"})


def signature_summary() -> dict:
    """Introspect render_stem's signature.

    Returns a dict with:
      - 'params': list of parameter names in order
      - 'has_parameter_dict': bool
      - 'parameter_dict_kind': 'KEYWORD_ONLY' or None
      - 'parameter_dict_default_is_None': bool
    """
    sig = inspect.signature(render_stem)
    out = {
        "params": list(sig.parameters.keys()),
        "has_parameter_dict": "parameter_dict" in sig.parameters,
        "parameter_dict_kind": None,
        "parameter_dict_default_is_None": False,
    }
    if out["has_parameter_dict"]:
        p = sig.parameters["parameter_dict"]
        out["parameter_dict_kind"] = str(p.kind).rsplit(".", 1)[-1]
        out["parameter_dict_default_is_None"] = p.default is None
    return out


__all__ = [
    "render_stem",
    "render_fluidsynth",
    "render_sfizz",
    "SAMPLE_RATE",
    "SAMPLE_COUNT",
    "VST3_INSTRUMENTS",
    "PARAMETERIZED_INSTRUMENTS",
    "signature_summary",
]
