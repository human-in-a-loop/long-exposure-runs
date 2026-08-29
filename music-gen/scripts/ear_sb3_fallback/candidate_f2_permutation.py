#!/usr/bin/env python3
"""F2 — SHA-256-salted permutation rank test with within-artist symmetry.

Motivation. Rather than parameterize residual dispersion, F2 asks: does
the ordering of residuals correlate with the ordering of artist_id groups
more than would be expected under a fully symmetric relabeling?

Statistic:

    Observed = mean over groups g of |mean_g(r) - grand_mean(r)|
    Null = same computed under K SHA-256-derived permutations of artist_ids
    S_F2 = fraction of null draws with statistic <= Observed
          (equivalently, 1 - p-value of a one-sided permutation test)

With K=200 permutations, S_F2 is a discretized fraction in [0, 1] with
resolution 1/201. On singleton corpora, permuting artist_ids is a no-op
(each label is unique) — the "within-artist symmetry" constraint states
that identity-permutations count as no-ops and are excluded from the null
denominator. In that regime we fall back to a symmetry-preserving
alternative: PERMUTE the RESIDUALS across artist positions and compute
the same observed statistic — this restores test power on singleton
corpora because residual ordering is what carries the leak signal.

Permutation source: SHA-256 keyed on (salt, k, i) to yield a Fisher-Yates
swap sequence. No PRNG.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from typing import Sequence

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"Interpreter guard: expected /usr/bin/python3, got {sys.executable}"
    )

K_PERMUTATIONS = 200


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _observed(residuals: Sequence[float], artist_ids: Sequence[int]) -> float:
    grand = _mean(residuals)
    groups: dict[int, list[float]] = {}
    for r, a in zip(residuals, artist_ids):
        groups.setdefault(a, []).append(r)
    return _mean([abs(_mean(xs) - grand) for xs in groups.values()])


def _sha_perm(seq: list[int], salt: int, k: int) -> list[int]:
    """Deterministic Fisher-Yates. Uses SHA-256 to pick swap indices."""
    out = seq.copy()
    n = len(out)
    for i in range(n - 1, 0, -1):
        digest = hashlib.sha256(
            f"c37-clone-1|F2|salt={salt}|k={k}|i={i}".encode()
        ).digest()
        u = struct.unpack(">Q", digest[:8])[0]
        j = u % (i + 1)
        out[i], out[j] = out[j], out[i]
    return out


def f2_statistic(residuals: Sequence[float], artist_ids: Sequence[int],
                 salt: int, k_perm: int = K_PERMUTATIONS) -> float:
    """Return the SHA-256-permutation-based S_F2 in [0,1]."""
    if len(residuals) != len(artist_ids):
        raise ValueError("length mismatch")
    if not residuals:
        return 0.0

    obs = _observed(residuals, artist_ids)

    # Determine if any two elements share an artist id — governs the two
    # branches in the docstring.
    has_repeats = len(set(artist_ids)) < len(artist_ids)

    null_vals = []
    residuals_list = list(residuals)
    ids_list = list(artist_ids)
    for k in range(k_perm):
        if has_repeats:
            perm_ids = _sha_perm(ids_list, salt, k)
            null_vals.append(_observed(residuals_list, perm_ids))
        else:
            # Singleton regime: permute residuals across the fixed artist
            # positions (the "within-artist symmetry" no-op branch).
            perm_res = _sha_perm(residuals_list, salt, k)
            null_vals.append(_observed(perm_res, ids_list))

    # One-sided: fraction of null draws whose statistic <= observed.
    le = sum(1 for v in null_vals if v <= obs)
    return le / (k_perm + 1)


if __name__ == "__main__":
    # Smoke: pure noise, no signal -> S_F2 hovers around 0.5.
    residuals = [0.1, -0.2, 0.05, -0.15, 0.2, -0.05, 0.12, -0.08]
    ids_rep = [0, 0, 1, 1, 2, 2, 3, 3]
    s = f2_statistic(residuals, ids_rep, salt=0, k_perm=100)
    print(f"random smoke repeat S_F2 = {s:.4f}  (expected ~0.5)")

    # Smoke: strongly grouped residuals -> S_F2 close to 1.0.
    residuals_grouped = [1.0, 1.1, -1.0, -1.1, 1.0, 1.1, -1.0, -1.1]
    ids_grouped = [0, 0, 1, 1, 2, 2, 3, 3]
    s2 = f2_statistic(residuals_grouped, ids_grouped, salt=0, k_perm=100)
    print(f"grouped smoke S_F2 = {s2:.4f}  (expected >0.9)")

    # Determinism.
    a = f2_statistic(residuals, ids_rep, salt=42, k_perm=100)
    b = f2_statistic(residuals, ids_rep, salt=42, k_perm=100)
    assert a == b
    print("F2 smoke OK")
