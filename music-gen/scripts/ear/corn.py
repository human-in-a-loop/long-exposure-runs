"""CORN (Chained Ordinal Regression Networks) loss + predictor.

Cao, Mirjalili, Raschka 2020 — for K ordinal classes the model emits
K-1 binary logits `[y > 1, y > 2, ..., y > K-1]`; each sub-head is a
BCEWithLogits target. Prediction: 1 + count(sigmoid(logits) > 0.5).

Kept in-tree (~40 LOC) to avoid installing an extra pip package
that would drift the numpy/tf pin.
"""
# created: 2026-08-28T06:55:00Z  cycle: 6  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2)  milestone: M-EAR-1/preparation/model
from __future__ import annotations
from . import _interp  # noqa: F401 — interpreter guard

import numpy as np
import torch
import torch.nn.functional as F


def labels_to_corn(y: torch.Tensor, K: int) -> torch.Tensor:
    """y ∈ {1,...,K} → (N, K-1) float targets [y>1, y>2, ..., y>K-1]."""
    thresh = torch.arange(1, K, device=y.device).unsqueeze(0)  # (1, K-1)
    return (y.unsqueeze(1) > thresh).float()


def corn_loss(logits: torch.Tensor, y: torch.Tensor, K: int) -> torch.Tensor:
    """BCEWithLogits summed over the K-1 sub-heads, mean over batch."""
    target = labels_to_corn(y, K)  # (N, K-1)
    return F.binary_cross_entropy_with_logits(logits, target, reduction="mean")


def corn_predict(logits: torch.Tensor) -> torch.Tensor:
    """logits (N, K-1) → integer ordinal labels in {1,...,K}."""
    return 1 + (torch.sigmoid(logits) > 0.5).sum(dim=1).long()


def corn_predict_np(logits: np.ndarray) -> np.ndarray:
    return 1 + (1.0 / (1.0 + np.exp(-logits)) > 0.5).sum(axis=1).astype(np.int64)
