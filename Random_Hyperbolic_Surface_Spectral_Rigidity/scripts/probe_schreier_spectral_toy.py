# created: 2026-05-15T21:35:00Z
# cycle: 10
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M3-computational-probes
"""Schreier graph spectral toy probe for random permutation covers.

The model uses two independent uniform permutations a,b on [n]. The
undirected multigraph adjacency is A = P_a + P_a^T + P_b + P_b^T, so loops
and parallel edges are retained and every row sums to 4.
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

WINDOWS = (
    ("window_neg_edge", -4.0, -2.0),
    ("window_neg_mid", -2.0, 0.0),
    ("window_pos_mid", 0.0, 2.0),
    ("window_pos_edge", 2.0, 4.0000001),
)
TRACE_MOMENTS = (2, 4, 6, 8)

TRIAL_FIELDS = [
    "n",
    "trial",
    "observable",
    "value",
    "seed",
]

SUMMARY_FIELDS = [
    "n",
    "observable",
    "mean",
    "variance",
    "std",
    "q10",
    "q50",
    "q90",
    "trials",
    "seed",
]

FIT_FIELDS = [
    "observable",
    "fit_degree",
    "train_rmse",
    "holdout_rmse",
    "extrapolation_rmse",
    "derivative_at_zero",
    "coefficient_norm",
    "seed",
]


@dataclass(frozen=True)
class SpectralSample:
    n: int
    trial: int
    eigenvalues: np.ndarray
    observables: dict[str, float]


def parse_ints(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def permutation_matrix_adjacency(perms: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    n = len(perms[0])
    adjacency = np.zeros((n, n), dtype=float)
    rows = np.arange(n)
    for perm in perms:
        if len(perm) != n:
            raise ValueError("all permutations must have the same size")
        adjacency[rows, perm] += 1.0
        adjacency[perm, rows] += 1.0
    return adjacency


def random_permutations(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    return rng.permutation(n), rng.permutation(n)


def tree_closed_walk_moment(degree: int, k: int) -> int:
    if k == 0:
        return 1
    counts = {0: 1}
    for _ in range(k):
        nxt: dict[int, int] = {}
        for dist, count in counts.items():
            if dist == 0:
                nxt[1] = nxt.get(1, 0) + count * degree
            else:
                nxt[dist - 1] = nxt.get(dist - 1, 0) + count
                nxt[dist + 1] = nxt.get(dist + 1, 0) + count * (degree - 1)
        counts = nxt
    return counts.get(0, 0)


def top_nontrivial(eigenvalues: np.ndarray, count: int) -> list[float]:
    if count <= 0:
        return []
    ordered = np.sort(eigenvalues)[::-1]
    nontrivial = [float(v) for v in ordered if abs(float(v) - 4.0) > 1e-8]
    if len(nontrivial) < count:
        nontrivial.extend([float("nan")] * (count - len(nontrivial)))
    return nontrivial[:count]


def spectral_observables(adjacency: np.ndarray, top_count: int) -> tuple[np.ndarray, dict[str, float]]:
    n = adjacency.shape[0]
    eigenvalues = np.linalg.eigvalsh(adjacency)
    observables: dict[str, float] = {}
    for idx, value in enumerate(top_nontrivial(eigenvalues, top_count), start=1):
        observables[f"top_nontrivial_{idx}"] = value
    for name, lo, hi in WINDOWS:
        observables[name] = float(np.count_nonzero((eigenvalues >= lo) & (eigenvalues < hi)) / n)
    for k in TRACE_MOMENTS:
        trace_per_vertex = float(np.sum(eigenvalues**k) / n)
        tree_moment = float(tree_closed_walk_moment(4, k))
        observables[f"trace_moment_{k}_per_vertex"] = trace_per_vertex
        observables[f"centered_trace_moment_{k}"] = trace_per_vertex - tree_moment
    observables["spectral_radius_nontrivial"] = max(abs(v) for v in top_nontrivial(eigenvalues, max(1, top_count)) if not math.isnan(v))
    return eigenvalues, observables


def sample_once(n: int, trial: int, rng: np.random.Generator, top_count: int) -> SpectralSample:
    adjacency = permutation_matrix_adjacency(random_permutations(n, rng))
    eigenvalues, observables = spectral_observables(adjacency, top_count)
    return SpectralSample(n, trial, eigenvalues, observables)


def run_trials(n_values: list[int], trials: int, seed: int, top_count: int) -> tuple[list[dict[str, object]], list[SpectralSample]]:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    samples: list[SpectralSample] = []
    for n in n_values:
        for trial in range(trials):
            sample = sample_once(n, trial, rng, top_count)
            samples.append(sample)
            for observable, value in sample.observables.items():
                rows.append({"n": n, "trial": trial, "observable": observable, "value": value, "seed": seed})
    return rows, samples


def summarize_trials(rows: list[dict[str, object]], seed: int) -> list[dict[str, object]]:
    grouped: dict[tuple[int, str], list[float]] = {}
    for row in rows:
        value = float(row["value"])
        if math.isnan(value):
            continue
        grouped.setdefault((int(row["n"]), str(row["observable"])), []).append(value)
    summary: list[dict[str, object]] = []
    for (n, observable), values in sorted(grouped.items()):
        arr = np.asarray(values, dtype=float)
        summary.append(
            {
                "n": n,
                "observable": observable,
                "mean": float(np.mean(arr)),
                "variance": float(np.var(arr, ddof=1)) if len(arr) > 1 else 0.0,
                "std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
                "q10": float(np.quantile(arr, 0.10)),
                "q50": float(np.quantile(arr, 0.50)),
                "q90": float(np.quantile(arr, 0.90)),
                "trials": len(arr),
                "seed": seed,
            }
        )
    return summary


def split_by_x(rows: list[dict[str, object]]) -> dict[str, list[dict[str, float]]]:
    grouped: dict[str, list[dict[str, float]]] = {}
    for row in rows:
        n = int(row["n"])
        grouped.setdefault(str(row["observable"]), []).append({"n": float(n), "x": 1.0 / n, "observed": float(row["mean"])})
    return {key: sorted(value, key=lambda r: r["x"]) for key, value in grouped.items()}


def fit_observable_rows(
    summary: list[dict[str, object]],
    observables: list[str],
    degrees: list[int],
    seed: int,
) -> list[dict[str, object]]:
    grouped = split_by_x([row for row in summary if str(row["observable"]) in set(observables)])
    fit_rows: list[dict[str, object]] = []
    for observable, rows in grouped.items():
        if len(rows) < 4:
            continue
        ordered = sorted(rows, key=lambda r: r["x"])
        extrapolation = ordered[:1]
        holdout = ordered[-1:]
        train = ordered[1:-1]
        xs = np.asarray([row["x"] for row in train], dtype=float)
        ys = np.asarray([row["observed"] for row in train], dtype=float)
        for degree in degrees:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", np.exceptions.RankWarning)
                polynomial = Chebyshev.fit(xs, ys, degree)
            power = polynomial.convert(kind=Polynomial)
            residuals = {
                "train": [float(row["observed"] - polynomial(row["x"])) for row in train],
                "holdout": [float(row["observed"] - polynomial(row["x"])) for row in holdout],
                "extrapolation": [float(row["observed"] - polynomial(row["x"])) for row in extrapolation],
            }
            fit_rows.append(
                {
                    "observable": observable,
                    "fit_degree": degree,
                    "train_rmse": rmse(residuals["train"]),
                    "holdout_rmse": rmse(residuals["holdout"]),
                    "extrapolation_rmse": rmse(residuals["extrapolation"]),
                    "derivative_at_zero": float(polynomial.deriv()(0.0)),
                    "coefficient_norm": float(np.linalg.norm(power.coef)),
                    "seed": seed,
                }
            )
    return fit_rows


def rmse(values: list[float]) -> float:
    if not values:
        return 0.0
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def write_csv(rows: list[dict[str, object]], path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_eigenvalue_histograms(samples: list[SpectralSample], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    for n in sorted({sample.n for sample in samples}):
        eigenvalues = np.concatenate([sample.eigenvalues for sample in samples if sample.n == n])
        ax.hist(eigenvalues, bins=np.linspace(-4, 4, 65), density=True, histtype="step", linewidth=1.5, label=f"n={n}")
    ax.set_xlabel("adjacency eigenvalue")
    ax.set_ylabel("empirical spectral density")
    ax.set_title("Normalized Schreier adjacency spectra")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_trace_scaling(summary: list[dict[str, object]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    selected = [f"centered_trace_moment_{k}" for k in TRACE_MOMENTS]
    for observable in selected:
        rows = sorted([row for row in summary if row["observable"] == observable], key=lambda r: int(r["n"]))
        ns = [int(row["n"]) for row in rows]
        means = [float(row["mean"]) for row in rows]
        variances = [float(row["variance"]) for row in rows]
        axes[0].plot(ns, means, marker="o", label=observable.replace("centered_trace_moment_", "k="))
        axes[1].plot(ns, variances, marker="o", label=observable.replace("centered_trace_moment_", "k="))
    axes[0].set_xlabel("n")
    axes[0].set_ylabel("mean centered trace per vertex")
    axes[1].set_xlabel("n")
    axes[1].set_ylabel("sample variance")
    axes[1].set_yscale("symlog", linthresh=1e-8)
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Centered trace-moment scaling")
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_window_fit(summary: list[dict[str, object]], fit_rows: list[dict[str, object]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    selected = ["window_pos_edge", "centered_trace_moment_4"]
    for observable in selected:
        rows = sorted([row for row in summary if row["observable"] == observable], key=lambda r: float(1.0 / int(r["n"])))
        xs = np.asarray([1.0 / int(row["n"]) for row in rows], dtype=float)
        ys = np.asarray([float(row["mean"]) for row in rows], dtype=float)
        axes[0].plot(xs, ys, marker="o", linestyle="", label=observable)
        if len(rows) >= 4:
            train = rows[1:-1]
            tx = np.asarray([1.0 / int(row["n"]) for row in train], dtype=float)
            ty = np.asarray([float(row["mean"]) for row in train], dtype=float)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", np.exceptions.RankWarning)
                poly = Chebyshev.fit(tx, ty, 3)
            grid = np.linspace(0.0, max(xs) * 1.05, 120)
            axes[0].plot(grid, poly(grid), linewidth=1.4, label=f"{observable} degree 3")
    for observable in sorted({row["observable"] for row in fit_rows}):
        rows = sorted([row for row in fit_rows if row["observable"] == observable], key=lambda r: int(r["fit_degree"]))
        axes[1].plot(
            [int(row["fit_degree"]) for row in rows],
            [float(row["extrapolation_rmse"]) for row in rows],
            marker="o",
            label=observable,
        )
    axes[0].set_xlabel("x = 1/n")
    axes[0].set_ylabel("mean observable")
    axes[1].set_xlabel("fit degree")
    axes[1].set_ylabel("near-zero extrapolation RMSE")
    axes[1].set_yscale("symlog", linthresh=1e-8)
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle("Polynomial-window fits for spectral observables")
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", default="100,200,400,800")
    parser.add_argument("--trials", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20260515)
    parser.add_argument("--top-count", type=int, default=5)
    parser.add_argument("--fit-degrees", default="1,2,3,6")
    parser.add_argument("--fit-observables", default="window_pos_edge,window_pos_mid,centered_trace_moment_4,centered_trace_moment_6,spectral_radius_nontrivial")
    parser.add_argument("--trials-csv", type=Path, default=ROOT / "data/polynomial_method/schreier_spectral_toy_trials.csv")
    parser.add_argument("--summary-csv", type=Path, default=ROOT / "data/polynomial_method/schreier_spectral_toy_summary.csv")
    parser.add_argument("--fits-csv", type=Path, default=ROOT / "data/polynomial_method/schreier_spectral_window_fits.csv")
    parser.add_argument("--hist-png", type=Path, default=ROOT / "reports/figures/m3_schreier_spectral_eigenvalue_histograms.png")
    parser.add_argument("--trace-png", type=Path, default=ROOT / "reports/figures/m3_schreier_spectral_trace_scaling.png")
    parser.add_argument("--fit-png", type=Path, default=ROOT / "reports/figures/m3_schreier_spectral_window_fit.png")
    args = parser.parse_args()

    n_values = parse_ints(args.n_values)
    trial_rows, samples = run_trials(n_values, args.trials, args.seed, args.top_count)
    summary = summarize_trials(trial_rows, args.seed)
    fit_rows = fit_observable_rows(summary, [part.strip() for part in args.fit_observables.split(",") if part.strip()], parse_ints(args.fit_degrees), args.seed)

    write_csv(trial_rows, args.trials_csv, TRIAL_FIELDS)
    write_csv(summary, args.summary_csv, SUMMARY_FIELDS)
    write_csv(fit_rows, args.fits_csv, FIT_FIELDS)
    plot_eigenvalue_histograms(samples, args.hist_png)
    plot_trace_scaling(summary, args.trace_png)
    plot_window_fit(summary, fit_rows, args.fit_png)
    print(f"wrote {len(trial_rows)} trial observable rows to {args.trials_csv}")
    print(f"wrote {len(summary)} summary rows to {args.summary_csv}")
    print(f"wrote {len(fit_rows)} polynomial-window fit rows to {args.fits_csv}")
    print(f"wrote figures to {args.hist_png}, {args.trace_png}, and {args.fit_png}")


if __name__ == "__main__":
    main()
