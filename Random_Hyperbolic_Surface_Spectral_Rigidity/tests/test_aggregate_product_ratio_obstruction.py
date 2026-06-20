# created: 2026-05-16T07:10:00Z
# cycle: 20
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M9-aggregate-product-ratio-obstruction
"""Tests for M9 aggregate product-ratio obstruction examples."""

from __future__ import annotations

import csv
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_aggregate_product_ratio_obstruction as agg  # noqa: E402


def load_generated_rows() -> list[dict[str, str]]:
    agg.main()
    with agg.OUT_CSV.open(newline="") as f:
        return list(csv.DictReader(f))


def test_conditional_inequality_on_generated_rows() -> None:
    rows = load_generated_rows()
    for row in rows:
        lhs = abs(Fraction(row["aggregate_coefficient"]))
        rhs = Fraction(row["aggregate_bound_proxy"])
        assert lhs <= rhs, row


def test_exponential_count_exceeds_low_degree_polynomial() -> None:
    rows = load_generated_rows()
    selected = [row for row in rows if row["family"] == "exponential_count_path" and row["L"] == "40"][0]
    coefficient = abs(Fraction(selected["aggregate_coefficient"]))
    assert coefficient > 40**8


def test_signed_cancellation_is_exact() -> None:
    rows = load_generated_rows()
    signed = [row for row in rows if row["family"] == "signed_cancelled_pair"]
    assert signed
    assert all(Fraction(row["aggregate_coefficient"]) == 0 for row in signed)


def test_requirements_mark_per_template_insufficient() -> None:
    agg.main()
    with agg.REQ_CSV.open(newline="") as f:
        rows = list(csv.DictReader(f))
    per_template = [row for row in rows if row["requirement"] == "per-template product-ratio envelope"][0]
    assert per_template["present_in_m7"] == "yes"
    assert per_template["sufficient_for_polynomial_aggregate"] == "no"
    needed = {row["requirement"] for row in rows if row["needed_for_kim_tao_bridge"].startswith("yes")}
    assert "polynomial family-count control" in needed
    assert "rank-sensitive decay" in needed


if __name__ == "__main__":
    test_conditional_inequality_on_generated_rows()
    test_exponential_count_exceeds_low_degree_polynomial()
    test_signed_cancellation_is_exact()
    test_requirements_mark_per_template_insufficient()
    print("all aggregate product-ratio obstruction tests passed")
