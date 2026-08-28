"""CORN-ridge variant of the cycle-6 CORN head.

Architecture: Linear(2052, 128) -> ReLU -> Dropout(0.5) -> Linear(128, 6).
Optimizer: Adam, lr=1e-3, weight_decay=1e-2 (up from 1e-3 baseline).
Hypothesis (registered pre-run): explicit L2 + higher dropout suppresses
over-fitting to per-recipe label noise, lifting mean pairwise Kendall
tau above 0.4 relative to the cycle-6 chassis's 0.059 floor.

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: `/usr/bin/python3`.
"""
# created: 2026-08-28T20:20:00Z  cycle: 23  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 3fbd8c1ab57c)  milestone: M-EAR-1/head-regularization-audit
from __future__ import annotations
from . import _interp  # noqa: F401

import torch.nn as nn

from .model import K
from ._variant_core import make_fit, make_train_and_eval

VARIANT_NAME = "ridge"
HIDDEN = 128
DROPOUT = 0.5
WEIGHT_DECAY = 1e-2


def build_head(feat_dim: int) -> nn.Module:
    return nn.Sequential(
        nn.Linear(feat_dim, HIDDEN),
        nn.ReLU(),
        nn.Dropout(DROPOUT),
        nn.Linear(HIDDEN, K - 1),
    )


_fit = make_fit(build_head, weight_decay=WEIGHT_DECAY)
train_and_eval = make_train_and_eval(_fit)
