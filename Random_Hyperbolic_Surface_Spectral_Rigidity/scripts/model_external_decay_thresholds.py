# created: 2026-05-16T11:55:00Z
# cycle: 25
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M14-external-decay-thresholds
"""Model external decay thresholds for M12-style aggregate control."""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import enumerate_trace_like_weighted_quotients as m11  # noqa: E402


GRID_CSV = ROOT / "data/extension_candidates/external_decay_threshold_grid.csv"
THRESHOLD_CSV = ROOT / "data/extension_candidates/external_decay_sufficient_exponents.csv"
DOMINANT_CSV = ROOT / "data/extension_candidates/external_decay_dominant_profiles.csv"
CURVES_FIG = ROOT / "reports/figures/m14_decay_threshold_curves.png"
HEATMAP_FIG = ROOT / "reports/figures/m14_dominant_stratum_decay_heatmap.png"
BOUND_FIG = ROOT / "reports/figures/m14_bound_mode_decay_comparison.png"

VARIANTS = [
    "all_conflict_free",
    "primitive_non_diagonal",
    "diagonal_cyclic_only",
    "signed_diagonal_subtracted_proxy",
    "rank_two_noncyclic_remainder",
]
WEIGHT_SCHEMES = ["weight_unweighted", "weight_exp_decay_theta_0_5", "weight_length_inverse"]
MAX_ORDER = 4
TARGET_SLOPES = [0.0, 1.0, 2.0]


def parameter_grid() -> list[tuple[str, str, float]]:
    values: list[tuple[str, str, float]] = []
    for step in range(0, 21):
        value = 0.5 * step
        values.append(("polynomial_length", "sigma", value))
        values.append(("folded_complexity", "tau", value))
    for step in range(0, 21):
        values.append(("exponential_length", "beta", 0.1 * step))
    for value in [1.0, 0.5, 0.25, 0.1, 0.01]:
        values.append(("rank_penalty", "eta", value))
    return values


def num_text(value: float) -> str:
    if math.isnan(value):
        return ""
    if abs(value) < 1e-12:
        value = 0.0
    return f"{value:.12g}"


def n_power(record: m11.PairRecord) -> int:
    return record.skeleton.count_a + record.skeleton.count_b - record.skeleton.vertex_count


def coefficient(record: m11.PairRecord, order: int) -> float:
    return float(m11.profile_coefficients(record.skeleton)[order])


def rank_number(record: m11.PairRecord) -> int:
    return 1 if record.rank_label == "rank_one" else 2


def decay_weight(record: m11.PairRecord, model: str, value: float) -> float:
    length_sum = record.u.length + record.v.length
    if model == "polynomial_length":
        return (1.0 + length_sum) ** (-value)
    if model == "exponential_length":
        return math.exp(-value * length_sum)
    if model == "folded_complexity":
        complexity = record.skeleton.vertex_count + record.skeleton.count_a + record.skeleton.count_b
        return (1.0 + complexity) ** (-value)
    if model == "rank_penalty":
        return value ** (rank_number(record) - 1)
    raise ValueError(model)


def summarize_terms(records: list[m11.PairRecord], scheme: str, model: str, parameter: float, L: int, order: int) -> dict[str, float]:
    signed = 0.0
    av = 0.0
    tv = 0.0
    profiles: set[str] = set()
    for record in records:
        weight = m11.pair_weights(record)[scheme]
        decay = decay_weight(record, model, parameter)
        coeff = coefficient(record, order)
        term = weight * decay * coeff
        signed += term
        av += abs(term)
        tv += abs(weight) * decay
        profiles.add(record.skeleton.key)
    return {
        "num_terms": float(len(records)),
        "num_profiles": float(len(profiles)),
        "decayed_tv": tv,
        "decayed_coefficient_absolute_variation": av,
        "decayed_signed_coefficient_sum": signed,
        "m12_tv_bound_proxy": (L ** (2 * order)) * tv,
    }


def fit_loglog_slope(points: list[tuple[int, float]]) -> float:
    positive = [(float(L), float(value)) for L, value in points if value > 0]
    if len(positive) < 3:
        return math.nan
    xs = [math.log(L) for L, _ in positive]
    ys = [math.log(value) for _, value in positive]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom == 0:
        return math.nan
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom


def build_grid_rows(records: list[m11.PairRecord]) -> list[dict[str, str]]:
    grouped: dict[tuple[int, str, int], list[m11.PairRecord]] = defaultdict(list)
    for record in records:
        for variant in VARIANTS:
            if m11.record_in_variant(record, variant):
                grouped[(record.L, variant, n_power(record))].append(record)

    rows: list[dict[str, str]] = []
    slope_buckets: dict[tuple[str, str, str, str, str, int, int, str], list[tuple[int, float]]] = defaultdict(list)
    raw_rows: list[dict[str, object]] = []

    for (L, variant, d), items in sorted(grouped.items()):
        for scheme in WEIGHT_SCHEMES:
            for model, parameter_name, parameter in parameter_grid():
                for order in range(1, MAX_ORDER + 1):
                    stats = summarize_terms(items, scheme, model, parameter, L, order)
                    raw = {
                        "L": L,
                        "variant": variant,
                        "weight_scheme": scheme,
                        "n_power": d,
                        "coefficient_order": order,
                        "decay_model": model,
                        "parameter_name": parameter_name,
                        "parameter_value": parameter,
                        **stats,
                    }
                    raw_rows.append(raw)
                    for metric in [
                        "decayed_tv",
                        "decayed_coefficient_absolute_variation",
                        "decayed_signed_coefficient_sum",
                        "m12_tv_bound_proxy",
                    ]:
                        value = abs(float(stats[metric])) if metric == "decayed_signed_coefficient_sum" else float(stats[metric])
                        key = (variant, scheme, model, parameter_name, num_text(parameter), d, order, metric)
                        slope_buckets[key].append((L, value))

    slopes = {key: fit_loglog_slope(points) for key, points in slope_buckets.items()}
    for raw in raw_rows:
        row_key_base = (
            str(raw["variant"]),
            str(raw["weight_scheme"]),
            str(raw["decay_model"]),
            str(raw["parameter_name"]),
            num_text(float(raw["parameter_value"])),
            int(raw["n_power"]),
            int(raw["coefficient_order"]),
        )
        for metric in [
            "decayed_tv",
            "decayed_coefficient_absolute_variation",
            "decayed_signed_coefficient_sum",
            "m12_tv_bound_proxy",
        ]:
            slope = slopes[row_key_base + (metric,)]
            out = {
                "L": str(raw["L"]),
                "variant": str(raw["variant"]),
                "weight_scheme": str(raw["weight_scheme"]),
                "n_power": str(raw["n_power"]),
                "coefficient_order": str(raw["coefficient_order"]),
                "decay_model": str(raw["decay_model"]),
                "parameter_name": str(raw["parameter_name"]),
                "parameter_value": num_text(float(raw["parameter_value"])),
                "metric": metric,
                "metric_value": num_text(abs(float(raw[metric])) if metric == "decayed_signed_coefficient_sum" else float(raw[metric])),
                "signed_metric_value": num_text(float(raw[metric])) if metric == "decayed_signed_coefficient_sum" else "",
                "empirical_growth_slope": num_text(slope),
                "slope_points": str(len([1 for L, value in slope_buckets[row_key_base + (metric,)] if value > 0])),
                "num_terms": num_text(float(raw["num_terms"])),
                "num_profiles": num_text(float(raw["num_profiles"])),
                "notes": "slope is log(metric magnitude) versus log(L), computed only with at least three positive L values",
            }
            rows.append(out)
    return rows


def build_threshold_rows(grid_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in grid_rows:
        grouped[
            (
                row["variant"],
                row["weight_scheme"],
                row["n_power"],
                row["coefficient_order"],
                row["decay_model"],
                row["parameter_name"],
                row["metric"],
            )
        ].append(row)

    rows: list[dict[str, str]] = []
    for key, items in sorted(grouped.items()):
        variant, scheme, d, order, model, parameter_name, metric = key
        by_param: dict[str, str] = {}
        for item in items:
            if item["empirical_growth_slope"]:
                by_param[item["parameter_value"]] = item["empirical_growth_slope"]
        ordered = sorted(by_param.items(), key=lambda pair: float(pair[0]), reverse=(model == "rank_penalty"))
        # Rank penalty strength increases as eta decreases, so sort from weak to strong as 1, .5, ..., .01.
        if model == "rank_penalty":
            ordered = sorted(by_param.items(), key=lambda pair: -float(pair[0]))
        for target in TARGET_SLOPES:
            chosen_parameter = ""
            chosen_slope = ""
            for parameter, slope_text in ordered:
                slope = float(slope_text)
                if slope <= target:
                    chosen_parameter = parameter
                    chosen_slope = slope_text
                    break
            zero_row = next((item for item in items if item["parameter_value"] in {"0", "1"} and item["empirical_growth_slope"]), None)
            rows.append(
                {
                    "variant": variant,
                    "weight_scheme": scheme,
                    "n_power": d,
                    "coefficient_order": order,
                    "decay_model": model,
                    "parameter_name": parameter_name,
                    "metric": metric,
                    "target_slope": num_text(target),
                    "minimum_sufficient_parameter": chosen_parameter,
                    "slope_at_parameter": chosen_slope,
                    "baseline_slope": zero_row["empirical_growth_slope"] if zero_row else "",
                    "threshold_found": "yes" if chosen_parameter else "no",
                    "notes": "rank_penalty parameter is eta; smaller eta is stronger decay, while other models use larger exponents as stronger decay",
                }
            )
    return rows


def build_dominant_profile_rows(records: list[m11.PairRecord], best_sigma: float, best_beta: float, best_tau: float) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    items = [
        record
        for record in records
        if record.L == 5
        and n_power(record) == 1
        and m11.record_in_variant(record, "rank_two_noncyclic_remainder")
    ]
    grouped: dict[str, list[m11.PairRecord]] = defaultdict(list)
    for record in items:
        grouped[record.skeleton.key].append(record)
    for key, group in sorted(grouped.items()):
        skeleton = group[0].skeleton
        coeff1 = coefficient(group[0], 1)
        base_av = sum(abs(m11.pair_weights(record)["weight_unweighted"] * coeff1) for record in group)
        sigma_av = sum(abs(m11.pair_weights(record)["weight_unweighted"] * coeff1) * decay_weight(record, "polynomial_length", best_sigma) for record in group)
        beta_av = sum(abs(m11.pair_weights(record)["weight_unweighted"] * coeff1) * decay_weight(record, "exponential_length", best_beta) for record in group)
        tau_av = sum(abs(m11.pair_weights(record)["weight_unweighted"] * coeff1) * decay_weight(record, "folded_complexity", best_tau) for record in group)
        rows.append(
            {
                "L": "5",
                "variant": "rank_two_noncyclic_remainder",
                "n_power": "1",
                "canonical_key": key,
                "pair_classes": str(len(group)),
                "V": str(skeleton.vertex_count),
                "C": str(skeleton.count_a + skeleton.count_b),
                "length_sums": ";".join(sorted({str(record.u.length + record.v.length) for record in group})),
                "rank_proxy": group[0].rank_label,
                "coeff_order_1": num_text(coeff1),
                "base_order1_av": num_text(base_av),
                "poly_length_order1_av_at_sigma": num_text(sigma_av),
                "exp_length_order1_av_at_beta": num_text(beta_av),
                "folded_complexity_order1_av_at_tau": num_text(tau_av),
                "notes": "dominant-profile contribution uses L=5 unweighted d=1 rank-two remainder",
            }
        )
    rows.sort(key=lambda row: float(row["base_order1_av"]), reverse=True)
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def threshold_value(threshold_rows: list[dict[str, str]], model: str, metric: str, target: str, order: str = "1") -> float:
    matches = [
        row
        for row in threshold_rows
        if row["variant"] == "rank_two_noncyclic_remainder"
        and row["weight_scheme"] == "weight_unweighted"
        and row["n_power"] == "1"
        and row["coefficient_order"] == order
        and row["decay_model"] == model
        and row["metric"] == metric
        and row["target_slope"] == target
        and row["threshold_found"] == "yes"
    ]
    if not matches:
        return math.nan
    return float(matches[0]["minimum_sufficient_parameter"])


def plot_threshold_curves(grid_rows: list[dict[str, str]]) -> None:
    CURVES_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    colors = {"polynomial_length": "#4c78a8", "exponential_length": "#59a14f", "folded_complexity": "#e15759", "rank_penalty": "#f28e2b"}
    for model, color in colors.items():
        rows = [
            row
            for row in grid_rows
            if row["variant"] == "rank_two_noncyclic_remainder"
            and row["weight_scheme"] == "weight_unweighted"
            and row["n_power"] == "1"
            and row["coefficient_order"] == "1"
            and row["metric"] == "decayed_coefficient_absolute_variation"
            and row["empirical_growth_slope"]
            and row["decay_model"] == model
        ]
        rows = sorted(rows, key=lambda row: float(row["parameter_value"]))
        ax.plot([float(row["parameter_value"]) for row in rows], [float(row["empirical_growth_slope"]) for row in rows], marker="o", label=model.replace("_", " "), color=color)
    for target in TARGET_SLOPES:
        ax.axhline(target, color="black", linewidth=0.8, alpha=0.25)
    ax.set_xlabel("decay parameter")
    ax.set_ylabel("fitted log-log growth slope")
    ax.set_title("Dominant-stratum AV growth slopes under external decay")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "Caption: fitted growth slopes versus decay parameter for order-one coefficient absolute variation in the unweighted d=1 rank-two remainder.", fontsize=8)
    fig.savefig(CURVES_FIG, dpi=160)
    plt.close(fig)


def plot_decay_heatmap(grid_rows: list[dict[str, str]]) -> None:
    HEATMAP_FIG.parent.mkdir(parents=True, exist_ok=True)
    models = ["polynomial_length", "exponential_length", "folded_complexity", "rank_penalty"]
    parameters = {"polynomial_length": "2", "exponential_length": "0.5", "folded_complexity": "2", "rank_penalty": "0.5"}
    metrics = ["decayed_tv", "decayed_coefficient_absolute_variation", "decayed_signed_coefficient_sum", "m12_tv_bound_proxy"]
    data = []
    for model in models:
        line = []
        for metric in metrics:
            row = next(
                item
                for item in grid_rows
                if item["L"] == "5"
                and item["variant"] == "rank_two_noncyclic_remainder"
                and item["weight_scheme"] == "weight_unweighted"
                and item["n_power"] == "1"
                and item["coefficient_order"] == "1"
                and item["decay_model"] == model
                and item["parameter_value"] == parameters[model]
                and item["metric"] == metric
            )
            line.append(float(row["metric_value"]))
        data.append(line)
    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    image = ax.imshow(data, cmap="magma", norm="log")
    ax.set_xticks(range(len(metrics)), [metric.replace("_", "\n") for metric in metrics], fontsize=8)
    ax.set_yticks(range(len(models)), [f"{model}\n{parameters[model]}" for model in models], fontsize=8)
    for y, line in enumerate(data):
        for x, value in enumerate(line):
            ax.text(x, y, f"{value:.3g}", ha="center", va="center", color="white", fontsize=8)
    ax.set_title("Dominant L=5 stratum under representative decay")
    fig.colorbar(image, ax=ax, label="metric value, log scale")
    fig.text(0.01, 0.01, "Caption: decayed TV, coefficient AV, signed magnitude, and M12 TV proxy in the L=5 unweighted d=1 rank-two stratum under representative external decay models.", fontsize=8)
    fig.savefig(HEATMAP_FIG, dpi=160)
    plt.close(fig)


def plot_bound_comparison(grid_rows: list[dict[str, str]], thresholds: list[dict[str, str]]) -> None:
    BOUND_FIG.parent.mkdir(parents=True, exist_ok=True)
    sigma = threshold_value(thresholds, "polynomial_length", "decayed_coefficient_absolute_variation", "1")
    beta = threshold_value(thresholds, "exponential_length", "decayed_coefficient_absolute_variation", "1")
    tau = threshold_value(thresholds, "folded_complexity", "decayed_coefficient_absolute_variation", "1")
    choices = [
        ("polynomial_length", sigma),
        ("exponential_length", beta),
        ("folded_complexity", tau),
    ]
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    styles = {"decayed_coefficient_absolute_variation": "-", "decayed_signed_coefficient_sum": ":", "m12_tv_bound_proxy": "--"}
    colors = {"polynomial_length": "#4c78a8", "exponential_length": "#59a14f", "folded_complexity": "#e15759"}
    for model, parameter in choices:
        if math.isnan(parameter):
            continue
        parameter_text = num_text(parameter)
        for metric, linestyle in styles.items():
            rows = [
                row
                for row in grid_rows
                if row["variant"] == "rank_two_noncyclic_remainder"
                and row["weight_scheme"] == "weight_unweighted"
                and row["n_power"] == "1"
                and row["coefficient_order"] == "1"
                and row["decay_model"] == model
                and row["parameter_value"] == parameter_text
                and row["metric"] == metric
            ]
            rows = sorted(rows, key=lambda row: int(row["L"]))
            ax.plot([int(row["L"]) for row in rows], [float(row["metric_value"]) for row in rows], linestyle=linestyle, marker="o", color=colors[model], label=f"{model} {parameter_text} {metric}")
    ax.set_yscale("log")
    ax.set_xlabel("length cutoff L")
    ax.set_ylabel("metric value")
    ax.set_title("Bound modes at sufficient AV-growth thresholds")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.text(0.01, 0.01, "Caption: M12 TV proxy, coefficient AV, and signed sums under the first polynomial/exponential/folded-complexity decay parameters making order-one AV growth at most linear.", fontsize=8)
    fig.savefig(BOUND_FIG, dpi=160)
    plt.close(fig)


def main() -> None:
    records = m11.build_pair_records()
    grid_rows = build_grid_rows(records)
    threshold_rows = build_threshold_rows(grid_rows)
    best_sigma = threshold_value(threshold_rows, "polynomial_length", "decayed_coefficient_absolute_variation", "1")
    best_beta = threshold_value(threshold_rows, "exponential_length", "decayed_coefficient_absolute_variation", "1")
    best_tau = threshold_value(threshold_rows, "folded_complexity", "decayed_coefficient_absolute_variation", "1")
    dominant_rows = build_dominant_profile_rows(records, best_sigma if not math.isnan(best_sigma) else 0.0, best_beta if not math.isnan(best_beta) else 0.0, best_tau if not math.isnan(best_tau) else 0.0)
    write_csv(grid_rows, GRID_CSV)
    write_csv(threshold_rows, THRESHOLD_CSV)
    write_csv(dominant_rows, DOMINANT_CSV)
    plot_threshold_curves(grid_rows)
    plot_decay_heatmap(grid_rows)
    plot_bound_comparison(grid_rows, threshold_rows)
    print(f"wrote {GRID_CSV}")
    print(f"wrote {THRESHOLD_CSV}")
    print(f"wrote {DOMINANT_CSV}")
    print(f"wrote {CURVES_FIG}")
    print(f"wrote {HEATMAP_FIG}")
    print(f"wrote {BOUND_FIG}")
    for model, metric in [
        ("polynomial_length", "decayed_coefficient_absolute_variation"),
        ("exponential_length", "decayed_coefficient_absolute_variation"),
        ("folded_complexity", "decayed_coefficient_absolute_variation"),
        ("rank_penalty", "decayed_coefficient_absolute_variation"),
    ]:
        value = threshold_value(threshold_rows, model, metric, "1")
        print(f"dominant k=1 AV target slope<=1: {model} threshold={num_text(value)}")


if __name__ == "__main__":
    main()
