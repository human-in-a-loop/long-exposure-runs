# created: 2026-05-16T19:53:00Z
# cycle: 38
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M27-multiplicity-and-cluster-corollaries-from-rigidity

from __future__ import annotations

import csv
import math
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analyze_multiplicity_cluster_bounds import (  # noqa: E402
    CLASSIFICATION_PATH,
    GRID_PATH,
    build_rows,
    f_edge_asym,
    f_prime,
    f_profile,
    reference_count_envelope,
)


def test_f_prime_matches_finite_difference() -> None:
    for lam in [0.31, 1.0, 4.0, 25.0]:
        h = 1e-5 * max(lam, 1.0)
        finite_diff = (f_profile(lam + h) - f_profile(lam - h)) / (2 * h)
        assert abs(finite_diff - f_prime(lam)) < 5e-4


def test_edge_scaling_constant() -> None:
    for delta in [1e-3, 3e-4, 1e-4]:
        ratio = f_profile(0.25 + delta) / (delta**1.5)
        assert abs(ratio - math.pi / 3.0) < 0.02
        assert f_edge_asym(delta) > 0


def test_cluster_envelope_monotone_in_radius_and_density() -> None:
    n = 10_000
    alpha_small_radius = 0.20
    alpha_large_radius = 0.01
    assert reference_count_envelope(4.0, 0.0, n, alpha_large_radius) > reference_count_envelope(
        4.0, 0.0, n, alpha_small_radius
    )
    assert reference_count_envelope(4.0, 0.0, n, alpha_large_radius) > reference_count_envelope(
        0.26, 0.0, n, alpha_large_radius
    )


def test_generated_classification_contains_endpoint_only() -> None:
    if not CLASSIFICATION_PATH.exists() or not GRID_PATH.exists():
        rows = build_rows()
        assert any(row["classification"] == "tautological_or_endpoint_only" for row in rows)
        return
    with CLASSIFICATION_PATH.open() as handle:
        rows = list(csv.DictReader(handle))
    labels = {row["classification"] for row in rows}
    assert "tautological_or_endpoint_only" in labels or "edge_endpoint_equivalent" in labels
    assert any(row["decision"] == "preserve_as_bookkeeping_corollary" for row in rows)
    assert not any(row["decision"] == "advance_multiplicity_cluster_branch" for row in rows)


if __name__ == "__main__":
    test_f_prime_matches_finite_difference()
    test_edge_scaling_constant()
    test_cluster_envelope_monotone_in_radius_and_density()
    test_generated_classification_contains_endpoint_only()
    print("all multiplicity cluster bound tests passed")
