"""Synthetic-label recipes for the M-EAR-1/synthetic-label-stability-audit.

Four recipe families, ten total recipes, each parameterized by an SHA-256
salt in the ``stab-audit-*`` namespace (deliberately distinct from cycle-6's
salt). Every choice is a SHA-256 tiebreak from the salt + feature content —
NO PRNG anywhere. Recipes take a mapping of ``clip_id -> np.ndarray`` and
return a mapping of ``clip_id -> int`` (rating in {1..7}).

Family A ("hash-noise", salts 0,1)
    Pure noise floor. Rating = 1 + (int(sha256(salt || clip_id).digest()[:8]) mod 7).

Family B ("linear-projection", salts 2,3)
    Deterministic salt-derived coefficient vector c ∈ [-1, 1]^D dotted with
    the (mean-centered) feature vector. Scores across the 55 clips are
    rank-quantized to 7 equal-population bins (ties broken by SHA-256
    tiebreak on (salt || clip_id)).

Family C ("nonlinear", salts 4,5)
    32 axis indices and sign flips chosen from SHA-256(salt || purpose || i).
    Score = sum_i sign_i * tanh((feat[axis_i] - mu[axis_i]) / (sigma[axis_i] + eps)).
    Rank-quantized to 7 bins (SHA-256-tiebreak dedup).

Family D ("signed-popcount", salts 6,7,8,9)
    32 hash-picked feature axes with hash-picked sign flips. Score = sum over
    the 32 axes of sign_k * (feat[axis_k] > median[axis_k]), i.e. the signed
    popcount of thresholded z-scored features on a hash-selected axis subset.
    Rank-quantized to 7 equal-population bins via SHA-256 tiebreak. Structurally
    distinct from B (thresholded not linear) and C (integer popcount not
    tanh-summed real signal), and from A (feature-derived not pure hash).
    Family D deliberately allocates 4 salts (vs 2 for A/B/C) to broaden the
    envelope on the family with the most axis-choice variability.

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: ``/usr/bin/python3`` enforced via ``._interp``.
"""
# created: 2026-08-28T17:32:00Z  cycle: 22  run_id: run-2026-08-28T040704Z
# agent: worker (clone-2, fork cc548ca0c2e5)  milestone: M-EAR-1/synthetic-label-stability-audit
from __future__ import annotations
from . import _interp  # noqa: F401 -- interpreter guard

import hashlib
from typing import Callable, Mapping

import numpy as np

K = 7  # 1..7 ordinal
SALT_NAMESPACE = "stab-audit"


# ---------------------------------------------------------------------------
# SHA-256 primitives (no PRNG, ever)
# ---------------------------------------------------------------------------
def _sha256_bytes(*parts: str | bytes | int) -> bytes:
    h = hashlib.sha256()
    for p in parts:
        if isinstance(p, int):
            p = str(p)
        if isinstance(p, str):
            p = p.encode("utf-8")
        h.update(p)
        h.update(b"\x00")  # domain separator between parts
    return h.digest()


def _sha_int(*parts) -> int:
    """Unsigned 64-bit int from SHA-256 tiebreak."""
    return int.from_bytes(_sha256_bytes(*parts)[:8], "big", signed=False)


def _sha_unit(*parts) -> float:
    """Float in [0, 1) from SHA-256 tiebreak, 52-bit mantissa precision."""
    v = int.from_bytes(_sha256_bytes(*parts)[:7], "big", signed=False)
    return v / (1 << 56)


def _sha_signed_unit(*parts) -> float:
    """Float in [-1, 1) from SHA-256 tiebreak."""
    return 2.0 * _sha_unit(*parts) - 1.0


def salt_for(idx: int) -> str:
    """Canonical salt string for recipe index (0..9)."""
    return f"{SALT_NAMESPACE}-{idx}"


# ---------------------------------------------------------------------------
# Feature imputation (mirror scripts.ear.model.train_and_eval)
# ---------------------------------------------------------------------------
def _impute(X: np.ndarray) -> np.ndarray:
    """Replace NaNs in X with the finite per-column mean (0 if column all-NaN).

    Mirrors the imputation in scripts.ear.model.train_and_eval so that
    recipe scoring cannot silently degenerate to insertion-order (which
    happens when NaN scores tie the sort primary key on 1279/2052
    dead-PANNs axes present in the ear feature cache).
    """
    X = X.astype(np.float64).copy()
    col_mean = np.nanmean(X, axis=0)
    col_mean = np.where(np.isfinite(col_mean), col_mean, 0.0)
    inds = np.where(np.isnan(X))
    X[inds] = np.take(col_mean, inds[1])
    return X


# ---------------------------------------------------------------------------
# Rank-quantize helper (SHA-256 tiebreak on equal scores)
# ---------------------------------------------------------------------------
def _rank_to_7bins(
    scores: Mapping[str, float], salt: str
) -> dict[str, int]:
    """Map a mapping of clip_id -> float to clip_id -> int in {1..7} by rank.

    Sort by (score, sha256(salt||clip_id)) ascending; then assign bin index
    ceil((rank_1based / N) * 7). This yields ~equal-population bins.
    """
    ordered = sorted(
        scores.items(),
        key=lambda kv: (kv[1], _sha_int(salt, "quantize", kv[0])),
    )
    n = len(ordered)
    if n == 0:
        return {}
    out: dict[str, int] = {}
    for i, (cid, _s) in enumerate(ordered):
        # rank_1based = i+1 ; bin = ceil(rank / n * K)  ⇒  in {1..K}
        bin_idx = ((i * K) // n) + 1
        if bin_idx > K:
            bin_idx = K
        out[cid] = bin_idx
    return out


# ---------------------------------------------------------------------------
# Family A: hash-noise floor
# ---------------------------------------------------------------------------
def recipe_hash_noise(
    features: Mapping[str, np.ndarray], salt: str
) -> dict[str, int]:
    out: dict[str, int] = {}
    for cid in features:
        out[cid] = 1 + (_sha_int(salt, "noise", cid) % K)
    return out


# ---------------------------------------------------------------------------
# Family B: linear projection
# ---------------------------------------------------------------------------
def _linear_coefs(salt: str, dim: int) -> np.ndarray:
    """Deterministic salt-derived coefficient vector in [-1, 1]^dim."""
    c = np.empty(dim, dtype=np.float64)
    for i in range(dim):
        c[i] = _sha_signed_unit(salt, "coef", i)
    return c


def recipe_linear_projection(
    features: Mapping[str, np.ndarray], salt: str
) -> dict[str, int]:
    ids = list(features.keys())
    if not ids:
        return {}
    X = _impute(np.stack([features[c] for c in ids], axis=0))
    # Per-axis z-score. In 2052-D with only mean-centering, ||x|| varies
    # widely and the linear-projection ranking collapses to ||x||-ranking by
    # concentration of measure; z-scoring makes ||x_z|| ≈ sqrt(D) for every
    # clip so the ranking is driven by direction, not norm.
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True) + 1e-8
    Xz = (X - mu) / sd
    coefs = _linear_coefs(salt, X.shape[1])
    scores = Xz @ coefs
    scores_map = {cid: float(scores[i]) for i, cid in enumerate(ids)}
    return _rank_to_7bins(scores_map, salt)


# ---------------------------------------------------------------------------
# Family C: nonlinear (axis-pick + sign + tanh)
# ---------------------------------------------------------------------------
_C_N_AXES = 32


def _pick_axes_and_signs(
    salt: str, dim: int, n: int
) -> tuple[list[int], list[float]]:
    axes: list[int] = []
    signs: list[float] = []
    seen: set[int] = set()
    i = 0
    while len(axes) < n:
        # Deterministic dedup via extended-i counter.
        a = _sha_int(salt, "axis", i) % dim
        if a not in seen:
            axes.append(a)
            seen.add(a)
            signs.append(1.0 if (_sha_int(salt, "sign", len(signs)) & 1) else -1.0)
        i += 1
        if i > dim * 4:  # pathological guard (never triggered in practice)
            break
    return axes, signs


def recipe_nonlinear(
    features: Mapping[str, np.ndarray], salt: str
) -> dict[str, int]:
    ids = list(features.keys())
    if not ids:
        return {}
    X = _impute(np.stack([features[c] for c in ids], axis=0))
    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-8
    axes, signs = _pick_axes_and_signs(salt, X.shape[1], _C_N_AXES)
    Z = np.tanh((X[:, axes] - mu[axes]) / sd[axes]) * np.asarray(signs)
    scores = Z.sum(axis=1)
    scores_map = {cid: float(scores[i]) for i, cid in enumerate(ids)}
    return _rank_to_7bins(scores_map, salt)


# ---------------------------------------------------------------------------
# Family D: signed popcount (32 hash-picked axes, hash-picked signs, median-thresh)
# ---------------------------------------------------------------------------
_D_N_AXES = 32


def _pick_popcount_axes_signs(
    salt: str, dim: int, n: int
) -> tuple[list[int], list[int]]:
    axes: list[int] = []
    signs: list[int] = []
    seen: set[int] = set()
    i = 0
    while len(axes) < n:
        a = _sha_int(salt, "pc-axis", i) % dim
        if a not in seen:
            axes.append(a)
            seen.add(a)
            signs.append(1 if (_sha_int(salt, "pc-sign", len(signs)) & 1) else -1)
        i += 1
        if i > dim * 4:
            break
    return axes, signs


def recipe_signed_popcount(
    features: Mapping[str, np.ndarray], salt: str
) -> dict[str, int]:
    ids = list(features.keys())
    if not ids:
        return {}
    X = _impute(np.stack([features[c] for c in ids], axis=0))
    axes, signs = _pick_popcount_axes_signs(salt, X.shape[1], _D_N_AXES)
    # Per-axis median → binary above/below
    medians = np.median(X[:, axes], axis=0)  # (n_axes,)
    bits = (X[:, axes] > medians).astype(np.int64)  # (N, n_axes)
    signed = bits * np.asarray(signs, dtype=np.int64)  # (N, n_axes)
    scores = signed.sum(axis=1)  # (N,) integer signed popcount
    scores_map = {cid: float(scores[i]) for i, cid in enumerate(ids)}
    return _rank_to_7bins(scores_map, salt)


# ---------------------------------------------------------------------------
# Recipe registry — 10 entries, insertion order fixed for determinism
# ---------------------------------------------------------------------------
Recipe = Callable[[Mapping[str, np.ndarray], str], dict[str, int]]

RECIPES: list[dict] = [
    {"idx": 0, "family": "hash-noise",        "func": recipe_hash_noise,       "salt": salt_for(0)},
    {"idx": 1, "family": "hash-noise",        "func": recipe_hash_noise,       "salt": salt_for(1)},
    {"idx": 2, "family": "linear-projection", "func": recipe_linear_projection,"salt": salt_for(2)},
    {"idx": 3, "family": "linear-projection", "func": recipe_linear_projection,"salt": salt_for(3)},
    {"idx": 4, "family": "nonlinear",         "func": recipe_nonlinear,        "salt": salt_for(4)},
    {"idx": 5, "family": "nonlinear",         "func": recipe_nonlinear,        "salt": salt_for(5)},
    {"idx": 6, "family": "signed-popcount",   "func": recipe_signed_popcount,   "salt": salt_for(6)},
    {"idx": 7, "family": "signed-popcount",   "func": recipe_signed_popcount,   "salt": salt_for(7)},
    {"idx": 8, "family": "signed-popcount",   "func": recipe_signed_popcount,   "salt": salt_for(8)},
    {"idx": 9, "family": "signed-popcount",   "func": recipe_signed_popcount,   "salt": salt_for(9)},
]


def apply_recipe(
    recipe: dict, features: Mapping[str, np.ndarray]
) -> dict[str, int]:
    return recipe["func"](features, recipe["salt"])
