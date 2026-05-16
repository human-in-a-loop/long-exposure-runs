# created: 2026-05-16T21:02:00Z
# cycle: 41
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M30-schreier-benchmark-theoremization
"""Build the M30 Schreier trace-moment benchmark artifacts.

The model is A_n = P_a + P_a^{-1} + P_b + P_b^{-1} for two independent
uniform permutations.  Fixed-k traces expand as fixed-point counts of free
words; free-reducing words give the 4-regular tree closed-walk moment.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "extension_candidates"
FIGURE_DIR = ROOT / "reports" / "figures"

TREE_PATH = DATA_DIR / "m30_schreier_tree_moments.csv"
TRIALS_PATH = DATA_DIR / "m30_schreier_trace_moment_trials.csv"
VARIANCE_PATH = DATA_DIR / "m30_schreier_variance_scaling.csv"
CLASSIFICATION_PATH = DATA_DIR / "m30_schreier_benchmark_classification.csv"
CONVERGENCE_FIGURE = FIGURE_DIR / "m30_schreier_moment_convergence.png"
VARIANCE_FIGURE = FIGURE_DIR / "m30_schreier_variance_scaling.png"
ANALOGY_FIGURE = FIGURE_DIR / "m30_trace_method_analogy_map.png"

RUN_ID = "run-2026-05-15T153635Z"
SEED = 20260516
DEFAULT_N_VALUES = (80, 140, 220, 320)
DEFAULT_TRIALS = 24
MOMENTS = tuple(range(1, 11))
EVEN_MOMENTS = (2, 4, 6, 8, 10)
VARIANCE_MOMENTS = (2, 4, 6)
LETTERS = (0, 1, 2, 3)
INVERSE = {0: 1, 1: 0, 2: 3, 3: 2}
DECISION = "advance_schreier_benchmark_program"


@dataclass(frozen=True)
class TraceRow:
    n: int
    trial: int
    k: int
    normalized_trace: float
    tree_moment: int
    centered_trace: float
    seed: int


def reduce_word(word: tuple[int, ...]) -> tuple[int, ...]:
    stack: list[int] = []
    for letter in word:
        if stack and INVERSE[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def count_freely_reducing_words(k: int) -> int:
    if k == 0:
        return 1
    count = 0
    for index in range(4**k):
        value = index
        word: list[int] = []
        for _ in range(k):
            word.append(value & 3)
            value >>= 2
        if not reduce_word(tuple(word)):
            count += 1
    return count


def tree_closed_walk_moment(degree: int, k: int) -> int:
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


def random_schreier_adjacency(n: int, rng: np.random.Generator) -> np.ndarray:
    rows = np.arange(n)
    a = rng.permutation(n)
    b = rng.permutation(n)
    adjacency = np.zeros((n, n), dtype=float)
    adjacency[rows, a] += 1.0
    adjacency[a, rows] += 1.0
    adjacency[rows, b] += 1.0
    adjacency[b, rows] += 1.0
    return adjacency


def normalized_traces(adjacency: np.ndarray, moments: tuple[int, ...]) -> dict[int, float]:
    n = adjacency.shape[0]
    eigenvalues = np.linalg.eigvalsh(adjacency)
    return {k: float(np.sum(eigenvalues**k) / n) for k in moments}


def build_tree_rows(max_k: int = 10) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for k in range(max_k + 1):
        dp = tree_closed_walk_moment(4, k)
        free = count_freely_reducing_words(k)
        rows.append(
            {
                "k": k,
                "tree_moment": dp,
                "free_reduction_count": free,
                "odd_moment_zero": bool(k % 2 and dp == 0),
                "methods_agree": bool(dp == free),
            }
        )
    return rows


def run_trials(
    n_values: tuple[int, ...] = DEFAULT_N_VALUES,
    trials: int = DEFAULT_TRIALS,
    seed: int = SEED,
    moments: tuple[int, ...] = MOMENTS,
) -> list[TraceRow]:
    rng = np.random.default_rng(seed)
    tree = {k: tree_closed_walk_moment(4, k) for k in moments}
    rows: list[TraceRow] = []
    for n in n_values:
        for trial in range(trials):
            traces = normalized_traces(random_schreier_adjacency(n, rng), moments)
            for k in moments:
                rows.append(
                    TraceRow(
                        n=n,
                        trial=trial,
                        k=k,
                        normalized_trace=traces[k],
                        tree_moment=tree[k],
                        centered_trace=traces[k] - tree[k],
                        seed=seed,
                    )
                )
    return rows


def summarize_variance(rows: list[TraceRow]) -> list[dict[str, object]]:
    grouped: dict[tuple[int, int], list[float]] = {}
    means: dict[tuple[int, int], list[float]] = {}
    for row in rows:
        grouped.setdefault((row.k, row.n), []).append(row.centered_trace)
        means.setdefault((row.k, row.n), []).append(row.normalized_trace)

    by_k: dict[int, list[tuple[int, float]]] = {}
    for (k, n), values in grouped.items():
        if len(values) > 1:
            variance = float(np.var(values, ddof=1))
        else:
            variance = 0.0
        by_k.setdefault(k, []).append((n, variance))

    slopes: dict[int, float] = {}
    for k, pairs in by_k.items():
        positive = [(n, var) for n, var in sorted(pairs) if var > 0]
        if len(positive) >= 2:
            xs = np.log([n for n, _ in positive])
            ys = np.log([var for _, var in positive])
            slopes[k] = float(np.polyfit(xs, ys, 1)[0])
        else:
            slopes[k] = float("nan")

    out: list[dict[str, object]] = []
    for (k, n), values in sorted(grouped.items()):
        arr = np.asarray(values, dtype=float)
        mean_arr = np.asarray(means[(k, n)], dtype=float)
        variance = float(np.var(arr, ddof=1)) if len(arr) > 1 else 0.0
        out.append(
            {
                "k": k,
                "n": n,
                "mean_normalized_trace": float(np.mean(mean_arr)),
                "tree_moment": tree_closed_walk_moment(4, k),
                "mean_centered_trace": float(np.mean(arr)),
                "variance_centered_trace": variance,
                "std_centered_trace": math.sqrt(variance),
                "trials": len(arr),
                "loglog_variance_slope_for_k": slopes[k],
                "reference_slope_n_minus_1": -1.0,
                "reference_slope_n_minus_2": -2.0,
                "variance_status": classify_variance_slope(slopes[k]),
            }
        )
    return out


def classify_variance_slope(slope: float) -> str:
    if not math.isfinite(slope):
        return "insufficient_variance_data"
    if slope <= -1.5:
        return "compatible_with_n_minus_2_or_better"
    if slope <= -0.5:
        return "compatible_with_n_minus_1_scale"
    if slope < 0:
        return "weak_decay_observed"
    return "unstable_or_nondecaying"


def classification_rows(variance_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    terminal_n = max(int(row["n"]) for row in variance_rows)
    slopes = [
        float(row["loglog_variance_slope_for_k"])
        for row in variance_rows
        if int(row["k"]) in VARIANCE_MOMENTS and int(row["n"]) == terminal_n
    ]
    stable_count = sum(1 for slope in slopes if math.isfinite(slope) and slope < -0.5)
    decision = DECISION if stable_count >= 2 else "preserve_as_computational_benchmark_only"
    decision_rationale = (
        "Expectation theorem template plus exact tree baseline and reproducible variance evidence justify preserving M30 as a standalone benchmark."
        if decision == DECISION
        else "Expectation theorem template and exact tree baseline are clean, but this run's variance evidence is too weak for the stronger benchmark-program decision."
    )
    return [
        {
            "item": "fixed_k_expectation",
            "classification": "proved_fixed_k_expectation",
            "claim_status": "theorem_template",
            "decision": "",
            "rationale": "Freely reducing words contribute n fixed points and nontrivial reduced fixed-k words have O_k(1) expected fixed points.",
        },
        {
            "item": "tree_moment_regeneration",
            "classification": "proved_tree_benchmark",
            "claim_status": "exact_computation",
            "decision": "",
            "rationale": "Dynamic programming and explicit free-reduction enumeration agree through k=10.",
        },
        {
            "item": "centered_variance",
            "classification": "numerical_variance_evidence",
            "claim_status": "empirical",
            "decision": "",
            "rationale": f"{stable_count} of {len(slopes)} tested even moments have fitted variance slope below -0.5.",
        },
        {
            "item": "hyperbolic_transfer",
            "classification": "hyperbolic_transfer_not_claimed",
            "claim_status": "nonclaim",
            "decision": "",
            "rationale": "The model uses a free-group random permutation law and adjacency spectrum, not a surface-group cover or hyperbolic Laplacian.",
        },
        {
            "item": "branch_decision",
            "classification": "schreier_trace_benchmark_package",
            "claim_status": "decision",
            "decision": decision,
            "rationale": decision_rationale,
        },
    ]


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def trace_rows_as_dicts(rows: list[TraceRow]) -> list[dict[str, object]]:
    return [
        {
            "n": row.n,
            "trial": row.trial,
            "k": row.k,
            "normalized_trace": row.normalized_trace,
            "tree_moment": row.tree_moment,
            "centered_trace": row.centered_trace,
            "seed": row.seed,
        }
        for row in rows
    ]


def plot_moment_convergence(variance_rows: list[dict[str, object]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharex=True)
    axes_flat = list(axes.flat)
    for ax, k in zip(axes_flat, EVEN_MOMENTS):
        subset = [row for row in variance_rows if int(row["k"]) == k]
        ns = np.asarray([int(row["n"]) for row in subset], dtype=float)
        means = np.asarray([float(row["mean_normalized_trace"]) for row in subset], dtype=float)
        tree = float(subset[0]["tree_moment"])
        ax.plot(ns, means, marker="o", label="sample mean")
        ax.axhline(tree, color="black", linestyle="--", linewidth=1.0, label="tree moment")
        ax.set_xscale("log", base=2)
        ax.set_title(f"k={k}")
        ax.set_xlabel("n")
        ax.set_ylabel("n^-1 Tr(A^k)")
    axes_flat[-1].axis("off")
    axes_flat[0].legend(fontsize=8)
    fig.suptitle("Schreier trace moments converge toward 4-regular tree baselines")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def plot_variance_scaling(variance_rows: list[dict[str, object]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for k in VARIANCE_MOMENTS:
        subset = [row for row in variance_rows if int(row["k"]) == k]
        ns = np.asarray([int(row["n"]) for row in subset], dtype=float)
        variances = np.asarray([float(row["variance_centered_trace"]) for row in subset], dtype=float)
        slope = float(subset[0]["loglog_variance_slope_for_k"])
        ax.loglog(ns, variances, marker="o", linewidth=1.6, label=f"k={k}, slope={slope:.2f}")
    ref_ns = np.asarray(sorted({int(row["n"]) for row in variance_rows}), dtype=float)
    anchor = max(float(row["variance_centered_trace"]) for row in variance_rows if int(row["k"]) == 2)
    ax.loglog(ref_ns, anchor * (ref_ns / ref_ns[0]) ** -1, "k--", linewidth=1, label="n^-1 reference")
    ax.loglog(ref_ns, anchor * (ref_ns / ref_ns[0]) ** -2, "k:", linewidth=1.2, label="n^-2 reference")
    ax.set_xlabel("n")
    ax.set_ylabel("sample variance of n^-1 Tr(A^k) - m_k")
    ax.set_title("Centered Schreier trace-moment variance scaling")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def plot_analogy_map(out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.set_axis_off()
    boxes = [
        (0.08, 0.68, "Schreier trace", "words in F(a,b)\nfixed points of w(Pa,Pb)", "#d9f0ff"),
        (0.39, 0.68, "M3/M4 template layer", "labelled embeddings\nfalling-factorial expectations", "#e3f5d7"),
        (0.70, 0.68, "Kim--Tao trace side", "Selberg terms\nquotient-family polynomialization", "#fff1c7"),
        (0.08, 0.24, "tree/identity term", "freely reducing words\nm_k contribution", "#edf7ff"),
        (0.39, 0.24, "finite fluctuation", "nontrivial reduced words\nO_k(1) fixed-point expectation", "#eef9e7"),
        (0.70, 0.24, "scope firewall", "surface-group law and\nhyperbolic Laplacian not claimed", "#ffe6df"),
    ]
    for x, y, title, body, color in boxes:
        ax.add_patch(plt.Rectangle((x, y), 0.22, 0.18, facecolor=color, edgecolor="#333333", linewidth=1.1))
        ax.text(x + 0.11, y + 0.125, title, ha="center", va="center", fontsize=10, weight="bold")
        ax.text(x + 0.11, y + 0.055, body, ha="center", va="center", fontsize=8.5)
    arrows = [((0.30, 0.77), (0.39, 0.77)), ((0.61, 0.77), (0.70, 0.77)), ((0.19, 0.68), (0.19, 0.42)), ((0.50, 0.68), (0.50, 0.42)), ((0.81, 0.68), (0.81, 0.42))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.4, "color": "#333333"})
    ax.text(0.5, 0.96, "Trace-method analogy map: usable finite benchmark, bounded transfer claim", ha="center", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-values", default=",".join(str(n) for n in DEFAULT_N_VALUES))
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    n_values = tuple(int(part) for part in args.n_values.split(",") if part)
    tree_rows = build_tree_rows(10)
    trial_rows = run_trials(n_values=n_values, trials=args.trials, seed=args.seed)
    variance_rows = summarize_variance(trial_rows)
    class_rows = classification_rows(variance_rows)

    write_csv(TREE_PATH, tree_rows, ["k", "tree_moment", "free_reduction_count", "odd_moment_zero", "methods_agree"])
    write_csv(TRIALS_PATH, trace_rows_as_dicts(trial_rows), ["n", "trial", "k", "normalized_trace", "tree_moment", "centered_trace", "seed"])
    write_csv(
        VARIANCE_PATH,
        variance_rows,
        [
            "k",
            "n",
            "mean_normalized_trace",
            "tree_moment",
            "mean_centered_trace",
            "variance_centered_trace",
            "std_centered_trace",
            "trials",
            "loglog_variance_slope_for_k",
            "reference_slope_n_minus_1",
            "reference_slope_n_minus_2",
            "variance_status",
        ],
    )
    write_csv(CLASSIFICATION_PATH, class_rows, ["item", "classification", "claim_status", "decision", "rationale"])
    plot_moment_convergence(variance_rows, CONVERGENCE_FIGURE)
    plot_variance_scaling(variance_rows, VARIANCE_FIGURE)
    plot_analogy_map(ANALOGY_FIGURE)

    print(f"wrote {TREE_PATH.relative_to(ROOT)} ({len(tree_rows)} rows)")
    print(f"wrote {TRIALS_PATH.relative_to(ROOT)} ({len(trial_rows)} rows)")
    print(f"wrote {VARIANCE_PATH.relative_to(ROOT)} ({len(variance_rows)} rows)")
    print(f"wrote {CLASSIFICATION_PATH.relative_to(ROOT)} ({len(class_rows)} rows)")
    print(f"wrote {CONVERGENCE_FIGURE.relative_to(ROOT)}")
    print(f"wrote {VARIANCE_FIGURE.relative_to(ROOT)}")
    print(f"wrote {ANALOGY_FIGURE.relative_to(ROOT)}")
    print(f"decision={class_rows[-1]['decision']}")


if __name__ == "__main__":
    main()
