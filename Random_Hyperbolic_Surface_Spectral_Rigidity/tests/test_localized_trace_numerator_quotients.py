# created: 2026-05-16T18:21:00Z
# cycle: 34
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M23-localized-trace-numerator-quotient-family-model

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from model_localized_trace_numerator_quotients import (  # noqa: E402
    SUMMARY_CSV,
    SUPPORT_Q,
    TERMS_CSV,
    build_rows,
    transform_weight,
)


def load_terms() -> list[dict[str, str]]:
    with TERMS_CSV.open() as f:
        return list(csv.DictReader(f))


def load_summary() -> list[dict[str, str]]:
    with SUMMARY_CSV.open() as f:
        return list(csv.DictReader(f))


def test_transform_support_excludes_terms_beyond_support() -> None:
    assert transform_weight("compact_support", SUPPORT_Q + 1.0) == 0.0
    rows = build_rows()
    invalid = [row for row in rows if row["support_argument_1"] > SUPPORT_Q or row["support_argument_2"] > SUPPORT_Q]
    assert invalid
    assert all(row["support_valid"] is False and row["weighted_total_variation_proxy"] == 0.0 for row in invalid)


def test_diagonal_and_cyclic_tags_separated_from_rank_two() -> None:
    rows = load_terms()
    diagonal = [row for row in rows if row["quotient_control_tag"] == "identity/diagonal"]
    cyclic = [row for row in rows if row["quotient_control_tag"] == "cyclic"]
    rank_two = [row for row in rows if row["quotient_control_tag"] == "rank_two_noncyclic"]
    assert diagonal and cyclic and rank_two
    assert all(row["cyclic_flag"] == "True" for row in diagonal + cyclic)
    assert all(row["cyclic_flag"] == "False" for row in rank_two)


def test_d_strata_are_preserved_in_summaries() -> None:
    rows = load_summary()
    keys = {(row["transform_model"], row["quotient_control_tag"], row["d_C_minus_V"]) for row in rows}
    coarse = {(row["transform_model"], row["quotient_control_tag"]) for row in rows}
    assert len(keys) > len(coarse)
    assert "d_C_minus_V" in rows[0]


def test_optimistic_decay_decreases_total_variation_monotonically() -> None:
    totals: dict[str, float] = defaultdict(float)
    for row in load_terms():
        totals[row["transform_model"]] += float(row["weighted_total_variation_proxy"])
    assert totals["compact_support"] >= totals["paley_wiener_scaled"] >= totals["optimistic_decay"]
    assert totals["compact_support"] > totals["optimistic_decay"]


def test_unknown_surface_group_not_counted_as_m4_certified() -> None:
    rows = [row for row in load_terms() if row["quotient_control_tag"] == "unknown_surface_group"]
    assert rows
    assert all(row["coverage_by_M4_M12"] != "M4_certified" for row in rows)
    assert all(row["coverage_by_M4_M12"] == "unknown_surface_group" for row in rows)


def main() -> None:
    test_transform_support_excludes_terms_beyond_support()
    test_diagonal_and_cyclic_tags_separated_from_rank_two()
    test_d_strata_are_preserved_in_summaries()
    test_optimistic_decay_decreases_total_variation_monotonically()
    test_unknown_surface_group_not_counted_as_m4_certified()
    print("all localized trace numerator quotient tests passed")


if __name__ == "__main__":
    main()
