# created: 2026-05-15T20:45:00Z
# cycle: 9
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M3-computational-probes
"""Polynomial-window diagnostics for labelled embedding observables.

The main observable is the Cycle 8 normalized embedding count as a function
of x = 1/n. Fits use Chebyshev polynomials on each training window for
conditioning, while the reported derivative is with respect to x.
"""

from __future__ import annotations

import argparse
import csv
import math
import warnings
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial import Chebyshev, Polynomial


ROOT = Path(__file__).resolve().parents[1]

DIAGNOSTIC_FIELDS = [
    "template",
    "n",
    "x",
    "observed",
    "fit_degree",
    "prediction",
    "residual",
    "split",
    "bootstrap_id",
    "seed",
]

SUMMARY_FIELDS = [
    "template",
    "fit_degree",
    "train_rmse",
    "holdout_rmse",
    "extrapolation_rmse",
    "derivative_at_zero",
    "coefficient_norm",
    "chebyshev_norm",
    "bootstrap_sd",
    "seed",
]

DEFAULT_TEMPLATES = ("single_label_cycle", "eight_word_cyclic_toy", "eight_word_rank2_toy")


@dataclass(frozen=True)
class FitResult:
    template: str
    degree: int
    polynomial: Chebyshev
    power_polynomial: Polynomial
    derivative_at_zero: float
    coefficient_norm: float
    chebyshev_norm: float


def parse_degrees(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def read_summary(path: Path, templates: tuple[str, ...] = DEFAULT_TEMPLATES) -> dict[str, list[dict[str, float]]]:
    grouped: dict[str, list[dict[str, float]]] = {template: [] for template in templates}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            template = row["template"]
            if template not in grouped or row["sample_mode"] != "monte_carlo":
                continue
            n = int(row["n"])
            grouped[template].append(
                {
                    "n": float(n),
                    "x": 1.0 / n,
                    "observed": float(row["normalized_count"]),
                    "standard_error": float(row.get("standard_error", 0.0) or 0.0),
                }
            )
    return {template: sorted(rows, key=lambda r: r["x"]) for template, rows in grouped.items()}


def split_rows(rows: list[dict[str, float]], holdout_frac: float, seed: int) -> dict[str, list[dict[str, float]]]:
    if len(rows) < 4:
        return {"train": rows, "holdout": [], "extrapolation": []}
    ordered = sorted(rows, key=lambda r: r["x"])
    side_count = max(1, int(round(len(rows) * holdout_frac)))
    extrapolation = ordered[:side_count]
    candidates = ordered[side_count:]
    rng = np.random.default_rng(seed)
    holdout_count = min(side_count, max(1, len(candidates) // 3))
    holdout_idx = set(rng.choice(len(candidates), size=holdout_count, replace=False).tolist())
    holdout = [row for idx, row in enumerate(candidates) if idx in holdout_idx]
    train = [row for idx, row in enumerate(candidates) if idx not in holdout_idx]
    return {"train": train, "holdout": holdout, "extrapolation": extrapolation}


def fit_polynomial(xs: np.ndarray, ys: np.ndarray, degree: int, template: str) -> FitResult:
    if len(xs) == 0:
        raise ValueError("cannot fit empty data")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", np.exceptions.RankWarning)
        polynomial = Chebyshev.fit(xs, ys, degree)
    power_polynomial = polynomial.convert(kind=Polynomial)
    derivative_at_zero = float(polynomial.deriv()(0.0))
    coefficient_norm = float(np.linalg.norm(power_polynomial.coef))
    chebyshev_norm = float(np.linalg.norm(polynomial.coef))
    return FitResult(template, degree, polynomial, power_polynomial, derivative_at_zero, coefficient_norm, chebyshev_norm)


def rmse(values: list[float]) -> float:
    if not values:
        return 0.0
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def rows_for_fit(
    template: str,
    degree: int,
    splits: dict[str, list[dict[str, float]]],
    fit: FitResult,
    bootstrap_id: int,
    seed: int,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for split, rows in splits.items():
        for row in rows:
            prediction = float(fit.polynomial(row["x"]))
            observed = float(row["observed"])
            out.append(
                {
                    "template": template,
                    "n": int(row["n"]),
                    "x": row["x"],
                    "observed": observed,
                    "fit_degree": degree,
                    "prediction": prediction,
                    "residual": observed - prediction,
                    "split": split,
                    "bootstrap_id": bootstrap_id,
                    "seed": seed,
                }
            )
    return out


def bootstrap_observed(rows: list[dict[str, float]], rng: np.random.Generator) -> list[dict[str, float]]:
    out = []
    for row in rows:
        se = max(float(row.get("standard_error", 0.0)), 0.0)
        new_row = dict(row)
        new_row["observed"] = float(rng.normal(row["observed"], se)) if se > 0 else float(row["observed"])
        out.append(new_row)
    return out


def diagnostic_rows(
    grouped: dict[str, list[dict[str, float]]],
    degrees: list[int],
    holdout_frac: float,
    bootstrap: int,
    seed: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    detail_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    seed_seq = np.random.SeedSequence(seed)
    child_iter = iter(seed_seq.spawn(max(1, len(grouped) * len(degrees) * max(1, bootstrap))))

    for template, rows in grouped.items():
        if not rows:
            continue
        splits = split_rows(rows, holdout_frac, seed + sum(ord(ch) for ch in template))
        train_x = np.asarray([row["x"] for row in splits["train"]], dtype=float)
        train_y = np.asarray([row["observed"] for row in splits["train"]], dtype=float)
        for degree in degrees:
            fit = fit_polynomial(train_x, train_y, degree, template)
            base_rows = rows_for_fit(template, degree, splits, fit, 0, seed)
            detail_rows.extend(base_rows)
            by_split: dict[str, list[float]] = {"train": [], "holdout": [], "extrapolation": []}
            for row in base_rows:
                by_split[str(row["split"])].append(float(row["residual"]))

            bootstrap_predictions: list[float] = []
            for bootstrap_id in range(1, bootstrap + 1):
                rng = np.random.default_rng(next(child_iter))
                boot_train = bootstrap_observed(splits["train"], rng)
                boot_x = np.asarray([row["x"] for row in boot_train], dtype=float)
                boot_y = np.asarray([row["observed"] for row in boot_train], dtype=float)
                boot_fit = fit_polynomial(boot_x, boot_y, degree, template)
                bootstrap_predictions.append(float(boot_fit.polynomial(0.0)))
                detail_rows.extend(rows_for_fit(template, degree, {"train": boot_train}, boot_fit, bootstrap_id, seed))

            summary_rows.append(
                {
                    "template": template,
                    "fit_degree": degree,
                    "train_rmse": rmse(by_split["train"]),
                    "holdout_rmse": rmse(by_split["holdout"]),
                    "extrapolation_rmse": rmse(by_split["extrapolation"]),
                    "derivative_at_zero": fit.derivative_at_zero,
                    "coefficient_norm": fit.coefficient_norm,
                    "chebyshev_norm": fit.chebyshev_norm,
                    "bootstrap_sd": float(np.std(bootstrap_predictions, ddof=1)) if len(bootstrap_predictions) > 1 else 0.0,
                    "seed": seed,
                }
            )
    return detail_rows, summary_rows


def write_csv(rows: list[dict[str, object]], path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_fit_error(summary: list[dict[str, object]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    for template in sorted({row["template"] for row in summary}):
        rows = [row for row in summary if row["template"] == template]
        degrees = [int(row["fit_degree"]) for row in rows]
        holdout = [float(row["holdout_rmse"]) for row in rows]
        extrap = [float(row["extrapolation_rmse"]) for row in rows]
        ax.plot(degrees, holdout, marker="o", label=f"{template} holdout")
        ax.plot(degrees, extrap, marker="x", linestyle="--", label=f"{template} extrap")
    ax.set_xlabel("fit degree")
    ax.set_ylabel("RMSE in normalized count")
    ax.set_yscale("symlog", linthresh=1e-8)
    ax.set_title("Polynomial fit and hold-out errors")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_derivative_growth(summary: list[dict[str, object]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    for template in sorted({row["template"] for row in summary}):
        rows = [row for row in summary if row["template"] == template]
        degrees = [int(row["fit_degree"]) for row in rows]
        derivatives = [abs(float(row["derivative_at_zero"])) for row in rows]
        norms = [float(row["chebyshev_norm"]) for row in rows]
        ax.plot(degrees, derivatives, marker="o", label=f"{template} |P'(0)|")
        ax.plot(degrees, norms, marker="x", linestyle="--", label=f"{template} Cheb norm")
    ax.set_xlabel("fit degree")
    ax.set_ylabel("diagnostic magnitude")
    ax.set_yscale("symlog", linthresh=1e-8)
    ax.set_title("Derivative and coefficient growth")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_extrapolation(detail: list[dict[str, object]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    selected_degree = max(int(row["fit_degree"]) for row in detail if int(row["bootstrap_id"]) == 0)
    rows = [row for row in detail if int(row["bootstrap_id"]) == 0 and int(row["fit_degree"]) == selected_degree]
    for template in sorted({row["template"] for row in rows}):
        template_rows = sorted([row for row in rows if row["template"] == template], key=lambda r: float(r["x"]))
        xs = [float(row["x"]) for row in template_rows]
        observed = [float(row["observed"]) for row in template_rows]
        predicted = [float(row["prediction"]) for row in template_rows]
        ax.plot(xs, observed, marker="o", linestyle="", label=f"{template} observed")
        ax.plot(xs, predicted, linewidth=1.4, label=f"{template} degree {selected_degree}")
    ax.axvline(0.0, color="black", linewidth=1, alpha=0.5)
    ax.set_xlabel("x = 1/n")
    ax.set_ylabel("normalized embedding count")
    ax.set_title("Extrapolation toward x = 0")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-summary", type=Path, default=ROOT / "data/polynomial_method/labelled_graph_embedding_summary.csv")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "data/polynomial_method/polynomial_window_diagnostics.csv")
    parser.add_argument("--fit-summary", type=Path, default=ROOT / "data/polynomial_method/polynomial_window_fit_summary.csv")
    parser.add_argument("--seed", type=int, default=20260515)
    parser.add_argument("--degrees", default="1,2,3,4,6,8")
    parser.add_argument("--holdout-frac", type=float, default=0.25)
    parser.add_argument("--bootstrap", type=int, default=100)
    parser.add_argument("--fit-error-png", type=Path, default=ROOT / "reports/figures/m3_polynomial_window_fit_error.png")
    parser.add_argument("--derivative-png", type=Path, default=ROOT / "reports/figures/m3_polynomial_window_derivative_growth.png")
    parser.add_argument("--extrapolation-png", type=Path, default=ROOT / "reports/figures/m3_polynomial_window_extrapolation.png")
    args = parser.parse_args()

    grouped = read_summary(args.input_summary)
    detail, summary = diagnostic_rows(grouped, parse_degrees(args.degrees), args.holdout_frac, args.bootstrap, args.seed)
    write_csv(detail, args.out_csv, DIAGNOSTIC_FIELDS)
    write_csv(summary, args.fit_summary, SUMMARY_FIELDS)
    plot_fit_error(summary, args.fit_error_png)
    plot_derivative_growth(summary, args.derivative_png)
    plot_extrapolation(detail, args.extrapolation_png)
    print(f"wrote {len(detail)} diagnostic rows to {args.out_csv}")
    print(f"wrote {len(summary)} fit rows to {args.fit_summary}")
    print(f"wrote figures to {args.fit_error_png}, {args.derivative_png}, and {args.extrapolation_png}")


if __name__ == "__main__":
    main()
