# created: 2026-05-16T14:34:00Z
# cycle: 28
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M17-local-window-variance-input
"""Empirical variance benchmark for M3 Schreier spectral-window toy data."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
TRIALS_CSV = ROOT / "data/polynomial_method/schreier_spectral_toy_trials.csv"
OUT_CSV = ROOT / "data/extension_candidates/schreier_window_variance_benchmark.csv"
FIG = ROOT / "reports/figures/m17_schreier_window_variance_scaling.png"


def num_text(value: float) -> str:
    if math.isnan(value) or math.isinf(value):
        return str(value)
    if abs(value) < 1e-14:
        value = 0.0
    return f"{value:.12g}"


def sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        return math.nan
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def fit_log_slope(points: list[tuple[int, float]]) -> tuple[float, float]:
    valid = [(math.log(n), math.log(v)) for n, v in points if n > 0 and v > 0]
    if len(valid) < 2:
        return math.nan, math.nan
    xs = [x for x, _ in valid]
    ys = [y for _, y in valid]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    slope = sum((x - xbar) * (y - ybar) for x, y in valid) / denom
    intercept = ybar - slope * xbar
    return slope, intercept


def build_rows() -> list[dict[str, str]]:
    grouped: dict[tuple[int, str], list[float]] = defaultdict(list)
    with TRIALS_CSV.open() as handle:
        for row in csv.DictReader(handle):
            observable = row["observable"]
            if not observable.startswith("window_"):
                continue
            n = int(row["n"])
            grouped[(n, observable)].append(float(row["value"]))

    slope_by_window: dict[str, float] = {}
    intercept_by_window: dict[str, float] = {}
    windows = sorted({window for _, window in grouped})
    for window in windows:
        points = []
        for (n, observable), values in grouped.items():
            if observable == window:
                points.append((n, sample_variance(values)))
        slope, intercept = fit_log_slope(sorted(points))
        slope_by_window[window] = slope
        intercept_by_window[window] = intercept

    rows: list[dict[str, str]] = []
    for (n, observable), values in sorted(grouped.items()):
        mean = sum(values) / len(values)
        normalized_var = sample_variance(values)
        rows.append(
            {
                "n": str(n),
                "window": observable,
                "trials": str(len(values)),
                "mean_normalized_count": num_text(mean),
                "variance_normalized_count": num_text(normalized_var),
                "std_normalized_count": num_text(math.sqrt(normalized_var)),
                "variance_raw_count_proxy": num_text(normalized_var * n * n),
                "std_raw_count_proxy": num_text(math.sqrt(normalized_var) * n),
                "variance_slope_vs_n": num_text(slope_by_window[observable]),
                "variance_log_intercept": num_text(intercept_by_window[observable]),
                "interpretation": "Toy Schreier normalized window-count variance; evidence only for benchmark behavior, not Kim--Tao.",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_scaling(rows: list[dict[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    windows = []
    for row in rows:
        if row["window"] not in windows:
            windows.append(row["window"])
    colors = ["#4c78a8", "#f58518", "#54a24b", "#e45756"]
    for color, window in zip(colors, windows):
        selected = [row for row in rows if row["window"] == window]
        n_values = [float(row["n"]) for row in selected]
        variances = [float(row["variance_normalized_count"]) for row in selected]
        slope = float(selected[0]["variance_slope_vs_n"])
        ax.loglog(n_values, variances, marker="o", color=color, label=f"{window} slope {slope:.2f}")
    ax.set_xlabel("Schreier size n")
    ax.set_ylabel("empirical variance of normalized window count")
    ax.set_title("M3 Schreier spectral-window variance benchmark")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    write_csv(OUT_CSV, rows)
    plot_scaling(rows)
    print(f"wrote {OUT_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"wrote {FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
