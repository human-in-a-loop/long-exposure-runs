# created: 2026-05-16T12:05:00Z
# cycle: 25
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M14-external-decay-thresholds
"""Tests for M14 external-decay threshold modeling."""

from __future__ import annotations

import math
import sys
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import enumerate_trace_like_weighted_quotients as m11  # noqa: E402
import model_external_decay_thresholds as m14  # noqa: E402


@lru_cache(maxsize=1)
def records() -> tuple[m11.PairRecord, ...]:
    return tuple(m11.build_pair_records(max_len=5))


@lru_cache(maxsize=1)
def grid_rows() -> tuple[dict[str, str], ...]:
    return tuple(m14.build_grid_rows(list(records())))


def dominant_records(L: int = 5) -> list[m11.PairRecord]:
    return [
        record
        for record in records()
        if record.L == L
        and m14.n_power(record) == 1
        and m11.record_in_variant(record, "rank_two_noncyclic_remainder")
    ]


def row_for(**filters: str) -> dict[str, str]:
    matches = [row for row in grid_rows() if all(row[key] == value for key, value in filters.items())]
    assert matches, filters
    return matches[0]


def test_decay_weights_are_monotone_in_exponent_for_fixed_record() -> None:
    record = dominant_records()[0]
    assert m14.decay_weight(record, "polynomial_length", 2.0) <= m14.decay_weight(record, "polynomial_length", 1.0)
    assert m14.decay_weight(record, "exponential_length", 0.5) <= m14.decay_weight(record, "exponential_length", 0.1)
    assert m14.decay_weight(record, "folded_complexity", 2.0) <= m14.decay_weight(record, "folded_complexity", 1.0)
    assert m14.decay_weight(record, "rank_penalty", 0.25) <= m14.decay_weight(record, "rank_penalty", 0.5)


def test_zero_decay_reproduces_m13_l5_dominant_values() -> None:
    items = dominant_records()
    expected_tv = 200.0
    expected_av = 800.0
    for model, parameter in [("polynomial_length", 0.0), ("exponential_length", 0.0), ("folded_complexity", 0.0), ("rank_penalty", 1.0)]:
        stats = m14.summarize_terms(items, "weight_unweighted", model, parameter, L=5, order=1)
        assert abs(stats["decayed_tv"] - expected_tv) < 1e-9
        assert abs(stats["decayed_coefficient_absolute_variation"] - expected_av) < 1e-9
        assert abs(stats["decayed_signed_coefficient_sum"] + expected_av) < 1e-9


def test_rank_only_penalty_rescales_pure_rank_two_filtered_set() -> None:
    items = dominant_records()
    base = m14.summarize_terms(items, "weight_unweighted", "rank_penalty", 1.0, L=5, order=1)
    half = m14.summarize_terms(items, "weight_unweighted", "rank_penalty", 0.5, L=5, order=1)
    assert abs(half["decayed_tv"] - 0.5 * base["decayed_tv"]) < 1e-9
    assert abs(half["decayed_coefficient_absolute_variation"] - 0.5 * base["decayed_coefficient_absolute_variation"]) < 1e-9
    assert abs(half["decayed_signed_coefficient_sum"] - 0.5 * base["decayed_signed_coefficient_sum"]) < 1e-9


def test_fitted_slopes_require_three_positive_l_values() -> None:
    assert math.isnan(m14.fit_loglog_slope([(1, 1.0), (2, 4.0)]))
    slope = m14.fit_loglog_slope([(1, 1.0), (2, 4.0), (4, 16.0)])
    assert abs(slope - 2.0) < 1e-9


def test_threshold_tables_distinguish_tv_av_and_signed_metrics() -> None:
    thresholds = m14.build_threshold_rows(list(grid_rows()))
    metrics = {
        row["metric"]
        for row in thresholds
        if row["variant"] == "rank_two_noncyclic_remainder"
        and row["weight_scheme"] == "weight_unweighted"
        and row["n_power"] == "1"
        and row["coefficient_order"] == "1"
        and row["decay_model"] == "polynomial_length"
    }
    assert {"decayed_tv", "decayed_coefficient_absolute_variation", "decayed_signed_coefficient_sum", "m12_tv_bound_proxy"} <= metrics


def test_corrected_decay_slopes_change_with_decay_parameter() -> None:
    baseline = row_for(
        variant="rank_two_noncyclic_remainder",
        weight_scheme="weight_unweighted",
        n_power="1",
        coefficient_order="1",
        decay_model="polynomial_length",
        parameter_value="0",
        metric="decayed_coefficient_absolute_variation",
    )
    strong = row_for(
        variant="rank_two_noncyclic_remainder",
        weight_scheme="weight_unweighted",
        n_power="1",
        coefficient_order="1",
        decay_model="polynomial_length",
        parameter_value="10",
        metric="decayed_coefficient_absolute_variation",
    )
    assert float(strong["empirical_growth_slope"]) < float(baseline["empirical_growth_slope"])


if __name__ == "__main__":
    test_decay_weights_are_monotone_in_exponent_for_fixed_record()
    test_zero_decay_reproduces_m13_l5_dominant_values()
    test_rank_only_penalty_rescales_pure_rank_two_filtered_set()
    test_fitted_slopes_require_three_positive_l_values()
    test_threshold_tables_distinguish_tv_av_and_signed_metrics()
    test_corrected_decay_slopes_change_with_decay_parameter()
    print("all external decay threshold tests passed")
