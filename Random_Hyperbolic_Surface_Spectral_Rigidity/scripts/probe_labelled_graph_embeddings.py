# created: 2026-05-15T19:25:00Z
# cycle: 8
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M3-computational-probes
"""Direct labelled-graph embedding probes for random permutation actions."""

from __future__ import annotations

import argparse
import csv
import itertools
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np

import probe_common_fixed_points as base


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class LabelledTemplate:
    template: str
    vertices: tuple[int, ...]
    edges: tuple[tuple[int, int, str], ...]
    group: str
    description: str


TEMPLATES: tuple[LabelledTemplate, ...] = (
    LabelledTemplate("no_edge_control", (0, 1), (), "control", "two free injective vertices"),
    LabelledTemplate("single_label_cycle", (0,), ((0, 0, "a"),), "rank_one", "one labelled loop"),
    LabelledTemplate("cyclic_power_quotient", (0, 1), ((0, 1, "a"), (1, 0, "a")), "rank_one", "two-step a-cycle"),
    LabelledTemplate("figure_eight_ab", (0,), ((0, 0, "a"), (0, 0, "b")), "rank_two", "two labelled loops sharing one vertex"),
    LabelledTemplate(
        "theta_mixed",
        (0, 1),
        ((0, 1, "a"), (0, 1, "b"), (1, 0, "a")),
        "rank_two",
        "two vertices with parallel mixed labels and return edge",
    ),
    LabelledTemplate(
        "trace_pair_toy",
        (0, 1, 2),
        ((0, 1, "a"), (1, 0, "a"), (0, 2, "b"), (2, 0, "b")),
        "rank_two",
        "two trace-side cycles sharing a base vertex",
    ),
    LabelledTemplate(
        "eight_word_cyclic_toy",
        tuple(range(8)),
        tuple((i, (i + 1) % 8, "a") for i in range(8)),
        "eight_rank_one",
        "eight-edge cyclic diagonal quotient",
    ),
    LabelledTemplate(
        "eight_word_rank2_toy",
        tuple(range(7)),
        (
            (0, 1, "a"),
            (1, 2, "a"),
            (2, 3, "a"),
            (3, 0, "a"),
            (0, 4, "b"),
            (4, 5, "b"),
            (5, 6, "b"),
            (6, 0, "b"),
        ),
        "eight_rank_two",
        "two four-edge labelled cycles sharing one vertex",
    ),
)


FIELDS = [
    "n",
    "sample_mode",
    "template",
    "vertices",
    "edges",
    "labels_used",
    "cyclomatic_rank",
    "is_rank_one_template",
    "embedding_count_estimate",
    "success_probability",
    "naive_power",
    "normalized_count",
    "standard_error",
    "samples",
    "seed",
]


def canonical_label(label: str) -> str:
    if len(label) != 1 or not label.isalpha():
        raise ValueError(f"unsupported edge label {label!r}")
    return label


def labels_used(template: LabelledTemplate) -> tuple[str, ...]:
    return tuple(sorted({canonical_label(label).lower() for _, _, label in template.edges}))


def falling_factorial(n: int, k: int) -> int:
    if k > n:
        return 0
    out = 1
    for value in range(n - k + 1, n + 1):
        out *= value
    return out


def template_invariants(template: LabelledTemplate) -> dict[str, object]:
    labels = labels_used(template)
    parent = {v: v for v in template.vertices}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for src, dst, _ in template.edges:
        union(src, dst)
    components = len({find(v) for v in template.vertices}) if template.vertices else 0
    directed_edges = len({(src, dst, label.lower()) for src, dst, label in template.edges})
    cyclomatic_rank = max(0, directed_edges - len(template.vertices) + components)
    return {
        "vertices": len(template.vertices),
        "edges": len(template.edges),
        "labels_used": " ".join(labels),
        "cyclomatic_rank": cyclomatic_rank,
        "is_rank_one_template": int(len(labels) <= 1 and len(template.edges) > 0),
        "naive_power": len(template.vertices) - len(template.edges),
    }


def all_injective_assignments(n: int, vertices: tuple[int, ...]) -> Iterable[dict[int, int]]:
    for values in itertools.permutations(range(n), len(vertices)):
        yield dict(zip(vertices, values))


def random_injective_assignment(n: int, vertices: tuple[int, ...], rng: np.random.Generator) -> dict[int, int]:
    if len(vertices) > n:
        return {}
    values = rng.choice(n, size=len(vertices), replace=False)
    return {vertex: int(value) for vertex, value in zip(vertices, values)}


def label_constraint_counts(template: LabelledTemplate) -> dict[str, int] | None:
    """Return per-label partial-bijection sizes, or None if inconsistent."""
    by_label: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for src, dst, label in template.edges:
        label = canonical_label(label)
        if label.isupper():
            src, dst = dst, src
        by_label[label.lower()].add((src, dst))
    counts: dict[str, int] = {}
    for label, pairs in by_label.items():
        sources: dict[int, int] = {}
        targets: dict[int, int] = {}
        for src, dst in pairs:
            if src in sources and sources[src] != dst:
                return None
            if dst in targets and targets[dst] != src:
                return None
            sources[src] = dst
            targets[dst] = src
        counts[label] = len(pairs)
    return counts


def assignment_constraint_probability(template: LabelledTemplate, n: int, assignment: dict[int, int]) -> float:
    """Probability a random permutation tuple realizes this injective assignment."""
    if len(assignment) != len(template.vertices):
        return 0.0
    counts = label_constraint_counts(template)
    if counts is None:
        return 0.0
    probability = 1.0
    for edge_count in counts.values():
        denom = falling_factorial(n, edge_count)
        if denom == 0:
            return 0.0
        probability /= denom
    return probability


def embedding_succeeds(template: LabelledTemplate, assignment: dict[int, int], perms: dict[str, np.ndarray]) -> bool:
    if len(assignment) != len(template.vertices):
        return False
    for src, dst, label in template.edges:
        label = canonical_label(label)
        if int(perms[label][assignment[src]]) != assignment[dst]:
            return False
    return True


def count_embeddings_for_perms(template: LabelledTemplate, n: int, perms: dict[str, np.ndarray]) -> int:
    return sum(1 for assignment in all_injective_assignments(n, template.vertices) if embedding_succeeds(template, assignment, perms))


def exact_embedding_count(template: LabelledTemplate, n: int) -> tuple[float, float]:
    labels = labels_used(template)
    total_assignments = falling_factorial(n, len(template.vertices))
    if total_assignments == 0:
        return 0.0, 0.0
    if not labels:
        return float(total_assignments), 1.0
    perms_by_label = [list(itertools.permutations(range(n))) for _ in labels]
    total_count = 0
    total_perm_tuples = 0
    for perm_tuple in itertools.product(*perms_by_label):
        perms: dict[str, np.ndarray] = {}
        for label, perm_values in zip(labels, perm_tuple):
            perm = np.asarray(perm_values, dtype=int)
            perms[label] = perm
            perms[label.upper()] = base.invert_perm(perm)
        total_count += count_embeddings_for_perms(template, n, perms)
        total_perm_tuples += 1
    estimate = total_count / total_perm_tuples
    return float(estimate), float(estimate / total_assignments)


def monte_carlo_embedding_count(template: LabelledTemplate, n: int, samples: int, seed_seq: np.random.SeedSequence) -> tuple[float, float, float]:
    total_assignments = falling_factorial(n, len(template.vertices))
    if total_assignments == 0 or samples <= 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed_seq)
    probabilities = []
    for _ in range(samples):
        assignment = random_injective_assignment(n, template.vertices, rng)
        probabilities.append(assignment_constraint_probability(template, n, assignment))
    arr = np.asarray(probabilities, dtype=float)
    p = float(arr.mean())
    estimate = total_assignments * p
    se = total_assignments * float(arr.std(ddof=1) / math.sqrt(samples)) if samples > 1 else 0.0
    return float(estimate), float(p), float(se)


def normalized_count(estimate: float, n: int, naive_power: int) -> float:
    scale = n ** naive_power if naive_power >= 0 else 1.0 / (n ** abs(naive_power))
    return float(estimate / scale) if scale else 0.0


def row_for_result(
    template: LabelledTemplate,
    n: int,
    sample_mode: str,
    estimate: float,
    success_probability: float,
    standard_error: float,
    samples: int,
    seed: int,
) -> dict[str, object]:
    inv = template_invariants(template)
    return {
        "n": n,
        "sample_mode": sample_mode,
        "template": template.template,
        "vertices": inv["vertices"],
        "edges": inv["edges"],
        "labels_used": inv["labels_used"],
        "cyclomatic_rank": inv["cyclomatic_rank"],
        "is_rank_one_template": inv["is_rank_one_template"],
        "embedding_count_estimate": estimate,
        "success_probability": success_probability,
        "naive_power": inv["naive_power"],
        "normalized_count": normalized_count(estimate, n, int(inv["naive_power"])),
        "standard_error": standard_error,
        "samples": samples,
        "seed": seed,
    }


def result_rows(n_values: list[int], samples: int, seed: int, exact_max_n: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seed_base = np.random.SeedSequence(seed)
    child_sequences = iter(seed_base.spawn(len(n_values) * len(TEMPLATES)))
    for n in n_values:
        for template in TEMPLATES:
            labels = labels_used(template)
            if n <= exact_max_n and len(labels) <= 2:
                estimate, probability = exact_embedding_count(template, n)
                rows.append(row_for_result(template, n, "exact", estimate, probability, 0.0, 0, seed))
            estimate, probability, se = monte_carlo_embedding_count(template, n, samples, next(child_sequences))
            rows.append(row_for_result(template, n, "monte_carlo", estimate, probability, se, samples, seed))
    return rows


def write_csv(rows: list[dict[str, object]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def summarize(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[int, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["n"]), row["template"], row["sample_mode"])].append(row)
    out: list[dict[str, object]] = []
    for (n, template, mode), vals in sorted(grouped.items()):
        first = vals[0]
        estimates = np.asarray([float(row["embedding_count_estimate"]) for row in vals], dtype=float)
        out.append(
            {
                "n": n,
                "template": template,
                "sample_mode": mode,
                "vertices": int(first["vertices"]),
                "edges": int(first["edges"]),
                "labels_used": first["labels_used"],
                "cyclomatic_rank": int(first["cyclomatic_rank"]),
                "is_rank_one_template": int(first["is_rank_one_template"]),
                "embedding_count_estimate": float(estimates.mean()),
                "success_probability": float(np.mean([float(row["success_probability"]) for row in vals])),
                "naive_power": int(first["naive_power"]),
                "normalized_count": float(np.mean([float(row["normalized_count"]) for row in vals])),
                "standard_error": float(np.mean([float(row["standard_error"]) for row in vals])),
                "samples": int(first["samples"]),
                "seed": int(first["seed"]),
            }
        )
    return out


def write_summary_csv(summary: list[dict[str, object]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(summary)


def plot_scaling(summary: list[dict[str, object]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    selected = [
        "single_label_cycle",
        "cyclic_power_quotient",
        "figure_eight_ab",
        "theta_mixed",
        "trace_pair_toy",
        "eight_word_cyclic_toy",
        "eight_word_rank2_toy",
    ]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for template in selected:
        rows = [row for row in summary if row["template"] == template and row["sample_mode"] == "monte_carlo"]
        xs = [int(row["n"]) for row in rows]
        ys = [float(row["embedding_count_estimate"]) for row in rows]
        if xs:
            ax.plot(xs, ys, marker="o", label=template)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("cover degree n")
    ax.set_ylabel("estimated injective embeddings")
    ax.set_title("Labelled quotient-template embedding scaling")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_normalized(summary: list[dict[str, object]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in summary:
        if row["sample_mode"] == "monte_carlo":
            key = f"rank_one={row['is_rank_one_template']}, edges={row['edges']}"
            grouped[key].append(row)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for key, rows in sorted(grouped.items()):
        by_n: dict[int, list[float]] = defaultdict(list)
        for row in rows:
            by_n[int(row["n"])].append(float(row["normalized_count"]))
        xs = sorted(by_n)
        ys = [float(np.mean(by_n[n])) for n in xs]
        ax.plot(xs, ys, marker="o", label=key)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("cover degree n")
    ax.set_ylabel("mean count / naive n^(|V|-|E|)")
    ax.set_title("Naive constraint-count normalization")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def parse_n_values(text: str) -> list[int]:
    return [int(part) for part in text.split(",") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", default="3,4,5,20,50,100,200,400")
    parser.add_argument("--samples", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20260515)
    parser.add_argument("--exact-max-n", type=int, default=4)
    parser.add_argument("--out-csv", type=Path, default=ROOT / "data/polynomial_method/labelled_graph_embedding_probe.csv")
    parser.add_argument("--summary-csv", type=Path, default=ROOT / "data/polynomial_method/labelled_graph_embedding_summary.csv")
    parser.add_argument("--scaling-png", type=Path, default=ROOT / "reports/figures/m3_labelled_embedding_scaling.png")
    parser.add_argument("--normalized-png", type=Path, default=ROOT / "reports/figures/m3_labelled_embedding_normalized.png")
    parser.add_argument("--plot-only", action="store_true")
    args = parser.parse_args()

    if args.plot_only:
        rows = read_csv(args.out_csv)
    else:
        raw_rows = result_rows(parse_n_values(args.n_values), args.samples, args.seed, args.exact_max_n)
        write_csv(raw_rows, args.out_csv)
        rows = [{key: str(value) for key, value in row.items()} for row in raw_rows]
    summary = summarize(rows)
    write_summary_csv(summary, args.summary_csv)
    plot_scaling(summary, args.scaling_png)
    plot_normalized(summary, args.normalized_png)
    print(f"wrote {len(rows)} rows to {args.out_csv}")
    print(f"wrote summary to {args.summary_csv}")
    print(f"wrote figures to {args.scaling_png} and {args.normalized_png}")


if __name__ == "__main__":
    main()
