# mess_scale — piecewise-linear transfer function shared by every heuristic.
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1
"""Uniform mess-scale transfer function.

`mess_scale(raw, anchors)` maps a raw feature value through a piecewise-linear
function defined by (raw, mess) anchor pairs. All heuristics compose through
this helper so the mapping is auditable and reproducible.

Contract:
- `anchors` is a non-empty, strictly-increasing-in-x list of (raw_x, mess_y)
  pairs. Every mess_y must be in [0.0, 1.0].
- Output is clipped to [0.0, 1.0].
- Values below `anchors[0].x` return `anchors[0].y`; above `anchors[-1].x`
  return `anchors[-1].y` (flat extrapolation).
- NaN in → 0.0 out (silent failure mode: a null-with-reason result should be
  produced BEFORE calling mess_scale; see the per-heuristic guards).

The `blend` helper composes several already-mess-scaled features by a fixed
weight vector. Weights must sum to 1.0 (± 1e-9).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence, Tuple


Anchor = Tuple[float, float]


def mess_scale(raw: float, anchors: Sequence[Anchor]) -> float:
    """Piecewise-linear interpolation from raw feature space to [0, 1]."""
    if not anchors:
        raise ValueError("anchors must be non-empty")
    if isinstance(raw, float) and math.isnan(raw):
        return 0.0
    xs = [a[0] for a in anchors]
    ys = [a[1] for a in anchors]
    for i in range(len(xs) - 1):
        if xs[i + 1] <= xs[i]:
            raise ValueError(f"anchors must be strictly increasing in x: {anchors}")
    for y in ys:
        if not (0.0 <= y <= 1.0):
            raise ValueError(f"anchor y values must be in [0,1]: {anchors}")
    if raw <= xs[0]:
        return _clip01(ys[0])
    if raw >= xs[-1]:
        return _clip01(ys[-1])
    for i in range(len(xs) - 1):
        if xs[i] <= raw <= xs[i + 1]:
            span = xs[i + 1] - xs[i]
            t = (raw - xs[i]) / span
            return _clip01(ys[i] + t * (ys[i + 1] - ys[i]))
    # unreachable
    return _clip01(ys[-1])


def blend(features_mess: Sequence[float], weights: Sequence[float]) -> float:
    """Weighted average of already-mess-scaled features."""
    if len(features_mess) != len(weights):
        raise ValueError("features and weights length mismatch")
    s = sum(weights)
    if abs(s - 1.0) > 1e-9:
        raise ValueError(f"weights must sum to 1.0, got {s}")
    return _clip01(sum(f * w for f, w in zip(features_mess, weights)))


def _clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


@dataclass(frozen=True)
class HeuristicResult:
    """The canonical return type for every clip-level heuristic.

    - `mess_scale` is None for null-with-reason results (e.g. clip too short,
      unvoiced-dominant). `reason` MUST be populated when mess_scale is None.
    - `raw_features` carries every intermediate scalar so the auditor can
      reproduce the mess_scale value from anchors alone.
    - `blind_spots` is a snapshot of the module-level BLIND_SPOTS tuple at
      call time so a stale/updated docstring cannot silently drift from what
      the run recorded.
    """
    name: str
    raw_features: dict
    mess_scale: float | None
    reason: str | None = None
    blind_spots: tuple = field(default_factory=tuple)

    def to_row(self) -> dict:
        """Flatten to a TSV-friendly dict."""
        row = {
            "heuristic": self.name,
            "mess_scale": "" if self.mess_scale is None else f"{self.mess_scale:.6f}",
            "reason": self.reason or "",
        }
        for k, v in self.raw_features.items():
            row[f"raw__{k}"] = "" if v is None else f"{v:.6f}"
        return row
