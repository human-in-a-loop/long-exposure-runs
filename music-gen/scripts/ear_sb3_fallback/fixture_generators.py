#!/usr/bin/env python3
"""SHA-256-derived deterministic fixture generation.

No PRNG. Given (salt, corpus_type, alpha), returns byte-identical fixtures.

Fixture contents:
    - features: (N, D) float64 in [0,1]
    - artist_ids: (N,) int32 group labels
    - predictions: (N,) float64 "model predictions" of an ordinal 1-7 label
    - labels: (N,) float64 ordinal 1-7 rating (with planted leak strength alpha)

Corpora:
    singleton_43: 43 songs, artist_ids all distinct (0..42)
    repeat_55:    55 clips, 11 artists x 5 clips per artist (artist_ids in 0..10)

Planted leak semantics:
    rating(i) = (1 - alpha) * feature_signal(i) + alpha * artist_effect(i)
    predictions(i) = feature_signal(i) + noise(i)

    Under alpha=0 the model has no artist information available (predictions
    are functions of features only + noise, and features drive the label).
    Under alpha=1 the model still trains on features, but the label is
    fully driven by the non-factor artist -> residuals cluster by artist.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from typing import Tuple

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"Interpreter guard: expected /usr/bin/python3, got {sys.executable}"
    )

CORPUS_SIZES = {"singleton_43": 43, "repeat_55": 55}
FEATURE_DIM = 8


def _sha_bytes(salt: int, tag: str, index: int) -> bytes:
    """Deterministic 32-byte SHA-256 digest, keyed on (salt, tag, index)."""
    key = f"c37-clone-1|salt={salt}|tag={tag}|index={index}".encode("utf-8")
    return hashlib.sha256(key).digest()


def _sha_uniform(salt: int, tag: str, index: int, dim: int = 1) -> list[float]:
    """SHA-256-derived uniform [0,1) draws. Deterministic. No PRNG."""
    out: list[float] = []
    for k in range(dim):
        digest = hashlib.sha256(
            f"c37-clone-1|salt={salt}|tag={tag}|index={index}|k={k}".encode()
        ).digest()
        # First 8 bytes → uint64 → [0,1)
        u = struct.unpack(">Q", digest[:8])[0]
        out.append(u / 2**64)
    return out


def _artist_ids(corpus_type: str) -> list[int]:
    n = CORPUS_SIZES[corpus_type]
    if corpus_type == "singleton_43":
        return list(range(n))
    if corpus_type == "repeat_55":
        # 11 artists x 5 clips
        return [i // 5 for i in range(n)]
    raise ValueError(f"unknown corpus_type: {corpus_type}")


def _features(salt: int, corpus_type: str) -> list[list[float]]:
    n = CORPUS_SIZES[corpus_type]
    feats = []
    for i in range(n):
        feats.append(_sha_uniform(salt, f"feat:{corpus_type}", i, dim=FEATURE_DIM))
    return feats


def _feature_signal(features: list[list[float]]) -> list[float]:
    """A fixed linear projection to a scalar 'signal' in ~[1,7]."""
    # Weights are static, not salt-dependent — this is the "model's" feature map.
    weights = [0.5, -0.3, 0.7, 0.1, -0.2, 0.4, 0.3, -0.1]
    out = []
    for fv in features:
        s = sum(w * f for w, f in zip(weights, fv))
        # Map to [1,7]: shift/scale.
        # sum(w) = 1.4 → signal is roughly Normal-ish around 0.7.
        scaled = 4.0 + 6.0 * s
        # Clip to [1,7].
        scaled = max(1.0, min(7.0, scaled))
        out.append(scaled)
    return out


def _artist_effect(salt: int, corpus_type: str, artist_ids: list[int]) -> list[float]:
    """Per-artist ordinal offset, deterministic in salt+artist_id.

    Each artist has a fixed effect in [1,7]. Songs by the same artist share
    the same artist_effect (this is exactly what a non-factor leak looks like).
    """
    # Unique artist ids.
    uniq = sorted(set(artist_ids))
    per_artist: dict[int, float] = {}
    for aid in uniq:
        u = _sha_uniform(salt, f"artist:{corpus_type}", aid, dim=1)[0]
        per_artist[aid] = 1.0 + 6.0 * u
    return [per_artist[a] for a in artist_ids]


def _noise(salt: int, corpus_type: str, tag: str, n: int) -> list[float]:
    """Bounded [-0.5, +0.5] SHA-derived noise."""
    return [_sha_uniform(salt, f"noise:{corpus_type}:{tag}", i, dim=1)[0] - 0.5
            for i in range(n)]


def generate_fixture(
    salt: int,
    corpus_type: str,
    alpha: float,
) -> Tuple[list[list[float]], list[int], list[float], list[float]]:
    """Return (features, artist_ids, predictions, labels).

    All lists are of length N = CORPUS_SIZES[corpus_type].
    """
    if corpus_type not in CORPUS_SIZES:
        raise ValueError(f"corpus_type must be one of {list(CORPUS_SIZES)}")
    if not (0.0 <= alpha <= 1.0):
        raise ValueError(f"alpha must be in [0,1], got {alpha}")

    n = CORPUS_SIZES[corpus_type]
    features = _features(salt, corpus_type)
    artist_ids = _artist_ids(corpus_type)
    feat_signal = _feature_signal(features)
    art_effect = _artist_effect(salt, corpus_type, artist_ids)
    label_noise = _noise(salt, corpus_type, "label", n)
    pred_noise = _noise(salt, corpus_type, "pred", n)

    labels = []
    predictions = []
    for i in range(n):
        # Label: mixture of feature signal and artist effect (planted leak).
        lab = (1.0 - alpha) * feat_signal[i] + alpha * art_effect[i] + 0.3 * label_noise[i]
        labels.append(max(1.0, min(7.0, lab)))
        # Prediction: model sees only features (approximates feature signal + noise).
        # The model does NOT get to see artist labels; it only fits features.
        pred = feat_signal[i] + 0.3 * pred_noise[i]
        predictions.append(max(1.0, min(7.0, pred)))
    return features, artist_ids, predictions, labels


def residuals(predictions: list[float], labels: list[float]) -> list[float]:
    """label - prediction (per-song). This is what the fallback statistics
    operate on."""
    return [labels[i] - predictions[i] for i in range(len(labels))]


if __name__ == "__main__":
    # Byte-determinism smoke: two independent generations must match.
    for c in CORPUS_SIZES:
        for a in (0.0, 0.5, 1.0):
            r1 = generate_fixture(0, c, a)
            r2 = generate_fixture(0, c, a)
            assert r1 == r2, (c, a)
    print("fixture-determinism smoke OK")
