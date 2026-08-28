"""CORN-bottleneck variant of the cycle-6 CORN head.

Architecture: Linear(2052, 32) -> ReLU -> Dropout(0.3) -> Linear(32, 6).
Optimizer: Adam at cycle-6 hyperparameters (lr=1e-3, weight_decay=1e-3).
Hypothesis (registered pre-run): a 4x smaller bottleneck forces reliance
on lower-dimensional feature structure; if there is any signal in the
55-clip feature matrix, it should survive; if there isn't, MAE regresses
toward majority-class and the negative result is definitive.

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

VARIANT_NAME = "bottleneck"
HIDDEN = 32
DROPOUT = 0.3
WEIGHT_DECAY = 1e-3


def build_head(feat_dim: int) -> nn.Module:
    return nn.Sequential(
        nn.Linear(feat_dim, HIDDEN),
        nn.ReLU(),
        nn.Dropout(DROPOUT),
        nn.Linear(HIDDEN, K - 1),
    )


_fit = make_fit(build_head, weight_decay=WEIGHT_DECAY)
train_and_eval = make_train_and_eval(_fit)
