# created: 2026-05-16T00:30:00Z
# cycle: 14
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M5-extension-candidates
"""Compare exact labelled-template expansions with Cycle 9 polynomial fits."""

from __future__ import annotations

import argparse
import csv
import math
import os
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_COEFFS = ROOT / "data/extension_candidates/labelled_embedding_expansion_coefficients.csv"
DEFAULT_DIAGNOSTICS = ROOT / "data/polynomial_method/polynomial_window_diagnostics.csv"
DEFAULT_FIT_SUMMARY = ROOT / "data/polynomial_method/polynomial_window_fit_summary.csv"
DEFAULT_OUT_CSV = ROOT / "data/extension_candidates/labelled_embedding_expansion_fit_comparison.csv"
DEFAULT_FIGURE = ROOT / "reports/figures/m5_expansion_vs_cycle9_fits.png"

COMPARISON_FIELDS = [
    "template",
    "comparison_status",
    "n",
    "x",
    "split",
    "cycle9_fit_degree",
    "observed",
    "cycle9_prediction",
    "cycle9_abs_error",
    "exact_value",
    "exact_abs_error",
    "taylor_order",
    "taylor_prediction",
    "taylor_abs_error",
]


def parse_fraction(text: str) -> Fraction:
    text = (text or "0").strip().strip('"')
    return Fraction(text)


def falling_factorial(n: int, k: int) -> int:
    out = 1
    for j in range(k):
        out *= n - j
    return out


def read_coefficients(path: Path) -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            counts = [int(part) for part in row["constraint_counts"].split(";") if part]
            coeffs = [parse_fraction(row[f"coeff_{idx}"]) for idx in range(5)]
            rows[row["template"]] = {
                "vertices": int(row["vertices"]),
                "constraint_counts": counts,
                "conflict": row["conflict"].lower() == "true",
                "coeffs": coeffs,
                "description": row["description"],
            }
    return rows


def exact_normalized(template: dict[str, object], n: int) -> Fraction:
    if template["conflict"]:
        return Fraction(0, 1)
    vertices = int(template["vertices"])
    counts = list(template["constraint_counts"])
    if n < vertices:
        return Fraction(0, 1)
    constraint_total = sum(counts)
    value = Fraction(n, 1) ** (constraint_total - vertices)
    value *= falling_factorial(n, vertices)
    for count in counts:
        value /= falling_factorial(n, count)
    return value


def taylor_value(coeffs: list[Fraction], x: Fraction, order: int) -> Fraction:
    return sum(coeffs[idx] * (x**idx) for idx in range(order + 1))


def read_cycle9_diagnostics(path: Path) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if row.get("bootstrap_id", "0") != "0":
                continue
            grouped[row["template"]].append(row)
    return grouped


def read_fit_summary(path: Path) -> dict[tuple[str, int], dict[str, float]]:
    rows: dict[tuple[str, int], dict[str, float]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            key = (row["template"], int(row["fit_degree"]))
            rows[key] = {
                "train_rmse": float(row["train_rmse"]),
                "holdout_rmse": float(row["holdout_rmse"]),
                "extrapolation_rmse": float(row["extrapolation_rmse"]),
            }
    return rows


def build_comparison(
    coefficients: dict[str, dict[str, object]],
    diagnostics: dict[str, list[dict[str, str]]],
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for template_name, template in coefficients.items():
        rows = diagnostics.get(template_name, [])
        if not rows:
            out.append(
                {
                    "template": template_name,
                    "comparison_status": "skipped_no_cycle9_rows",
                    "n": "",
                    "x": "",
                    "split": "",
                    "cycle9_fit_degree": "",
                    "observed": "",
                    "cycle9_prediction": "",
                    "cycle9_abs_error": "",
                    "exact_value": "",
                    "exact_abs_error": "",
                    "taylor_order": "",
                    "taylor_prediction": "",
                    "taylor_abs_error": "",
                }
            )
            continue
        for row in rows:
            n = int(float(row["n"]))
            x = Fraction(1, n)
            observed = float(row["observed"])
            cycle9_prediction = float(row["prediction"])
            exact = float(exact_normalized(template, n))
            for order in range(1, 5):
                prediction = float(taylor_value(template["coeffs"], x, order))
                out.append(
                    {
                        "template": template_name,
                        "comparison_status": "compared",
                        "n": n,
                        "x": float(x),
                        "split": row["split"],
                        "cycle9_fit_degree": int(row["fit_degree"]),
                        "observed": observed,
                        "cycle9_prediction": cycle9_prediction,
                        "cycle9_abs_error": abs(cycle9_prediction - observed),
                        "exact_value": exact,
                        "exact_abs_error": abs(exact - observed),
                        "taylor_order": order,
                        "taylor_prediction": prediction,
                        "taylor_abs_error": abs(prediction - observed),
                    }
                )
    return out


def rmse(values: list[float]) -> float:
    if not values:
        return 0.0
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def write_comparison(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMPARISON_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def plot_comparison(
    figure_path: Path,
    coefficients: dict[str, dict[str, object]],
    diagnostics: dict[str, list[dict[str, str]]],
    comparison_rows: list[dict[str, object]],
    fit_summary: dict[tuple[str, int], dict[str, float]],
) -> None:
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), constrained_layout=True)
    curve_templates = ["eight_word_cyclic_toy", "eight_word_rank2_toy"]
    colors = {3: "#2f6fbb", 8: "#a23b72"}

    for ax, template_name in zip(axes[:2], curve_templates):
        rows = [r for r in diagnostics.get(template_name, []) if r.get("bootstrap_id", "0") == "0"]
        xs = sorted({float(r["x"]) for r in rows})
        if not xs:
            ax.set_title(f"{template_name}\n(no Cycle 9 rows)")
            continue
        ns = [round(1 / x) for x in xs]
        exact = [float(exact_normalized(coefficients[template_name], n)) for n in ns]
        taylor4 = [
            float(taylor_value(coefficients[template_name]["coeffs"], Fraction(1, n), 4))
            for n in ns
        ]
        observed_by_x = {}
        pred_by_degree: dict[int, dict[float, float]] = defaultdict(dict)
        for row in rows:
            x = float(row["x"])
            observed_by_x[x] = float(row["observed"])
            degree = int(row["fit_degree"])
            if degree in colors:
                pred_by_degree[degree][x] = float(row["prediction"])
        ax.plot(xs, exact, color="black", lw=2, label="exact")
        ax.plot(xs, taylor4, color="#6a994e", lw=1.5, ls="--", label="Taylor order 4")
        ax.scatter(sorted(observed_by_x), [observed_by_x[x] for x in sorted(observed_by_x)], color="black", s=18, zorder=3, label="Cycle 9 observed")
        for degree, color in colors.items():
            points = pred_by_degree.get(degree, {})
            if points:
                ax.plot(sorted(points), [points[x] for x in sorted(points)], color=color, alpha=0.85, label=f"Cycle 9 degree {degree}")
        ax.set_xscale("log")
        ax.set_xlabel("x = 1/n")
        ax.set_ylabel("normalized observable")
        ax.set_title(template_name)
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8)

    ax = axes[2]
    width = 0.18
    xbase = np.arange(len(curve_templates))
    for offset_idx, degree in enumerate([1, 2, 3, 6, 8]):
        values = [
            fit_summary.get((template, degree), {}).get("extrapolation_rmse", math.nan)
            for template in curve_templates
        ]
        ax.bar(xbase + (offset_idx - 2) * width, values, width=width, label=f"fit degree {degree}")
    taylor4_values = []
    for template in curve_templates:
        rows = [
            r for r in comparison_rows
            if r["comparison_status"] == "compared"
            and r["template"] == template
            and r["taylor_order"] == 4
            and r["split"] == "extrapolation"
        ]
        taylor4_values.append(rmse([float(r["taylor_abs_error"]) for r in rows]))
    ax.scatter(xbase, taylor4_values, marker="D", s=55, color="black", label="Taylor order 4")
    ax.set_yscale("symlog", linthresh=1e-12)
    ax.set_xticks(xbase)
    ax.set_xticklabels(["cyclic", "rank-two"])
    ax.set_ylabel("extrapolation RMSE")
    ax.set_title("Sparse-grid fit error")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(fontsize=8)

    fig.suptitle("Exact falling-factorial expansions versus Cycle 9 polynomial-window fits", fontsize=13)
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coefficients", type=Path, default=DEFAULT_COEFFS)
    parser.add_argument("--diagnostics", type=Path, default=DEFAULT_DIAGNOSTICS)
    parser.add_argument("--fit-summary", type=Path, default=DEFAULT_FIT_SUMMARY)
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    parser.add_argument("--figure", type=Path, default=Path(os.environ.get("FIGURE_OUT", DEFAULT_FIGURE)))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    coefficients = read_coefficients(args.coefficients)
    diagnostics = read_cycle9_diagnostics(args.diagnostics)
    fit_summary = read_fit_summary(args.fit_summary)
    rows = build_comparison(coefficients, diagnostics)
    write_comparison(args.out_csv, rows)
    plot_comparison(args.figure, coefficients, diagnostics, rows, fit_summary)
    compared = sum(1 for row in rows if row["comparison_status"] == "compared")
    skipped = sum(1 for row in rows if row["comparison_status"] != "compared")
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.figure}")
    print(f"comparison_rows={compared}")
    print(f"skipped_templates={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
