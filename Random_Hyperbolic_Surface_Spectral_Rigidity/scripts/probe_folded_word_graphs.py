# created: 2026-05-15T18:20:00Z
# cycle: 7
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M3-computational-probes
"""Folded labelled word-graph probes for random permutation word families.

This is a deliberately small quotient diagnostic, not a full Stallings
subgroup-folding implementation.  It builds the deterministic labelled
trajectory graph traced by each word from a common symbolic basepoint, merges
identical labelled edges, computes graph invariants, and then measures random
permutation common fixed points plus sampled trajectory collision profiles.
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np

import probe_common_fixed_points as base


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FoldedFamily:
    family: str
    words: tuple[str, ...]
    group: str
    description: str


WORD_FAMILIES: tuple[FoldedFamily, ...] = (
    FoldedFamily("identity_control", ("1",), "control", "identity/empty word"),
    FoldedFamily("single_a", ("a",), "cyclic", "single primitive generator"),
    FoldedFamily("single_a2", ("aa",), "cyclic", "single square"),
    FoldedFamily("cyclic_pair_a_a2", ("a", "aa"), "cyclic", "same generator powers"),
    FoldedFamily("cyclic_pair_a2_a3", ("aa", "aaa"), "cyclic", "adjacent powers of one generator"),
    FoldedFamily("rank_two_pair_a_b", ("a", "b"), "rank_two", "two independent generators"),
    FoldedFamily("rank_two_pair_ab_ba", ("ab", "ba"), "rank_two", "two noncommuting two-step words"),
    FoldedFamily("rank_two_pair_ab_aB", ("ab", "aB"), "rank_two", "two words sharing a prefix"),
    FoldedFamily("commutator_single", ("abAB",), "mixed", "single commutator-like loop"),
    FoldedFamily("commutator_with_a", ("abAB", "a"), "mixed", "commutator plus generator"),
    FoldedFamily("cyclic_eight", tuple("a" * k for k in range(1, 9)), "eight_cyclic", "eight powers of one generator"),
    FoldedFamily(
        "mixed_eight",
        ("a", "aa", "ab", "aB", "ba", "bA", "abA", "aba"),
        "eight_mixed",
        "eight words mixing cyclic powers and rank-two words",
    ),
    FoldedFamily(
        "rank_two_eight",
        ("a", "b", "ab", "ba", "aB", "bA", "abA", "baB"),
        "eight_rank_two",
        "eight rank-two words with both generators visible",
    ),
)


def canonical_step(ch: str) -> tuple[str, int]:
    if not ch.isalpha():
        raise ValueError(f"unsupported word character {ch!r}")
    return (ch.lower(), -1 if ch.isupper() else 1)


def build_trajectory_graph(words: Iterable[str]) -> dict[str, object]:
    """Build a symbolic labelled trajectory quotient for the word tuple."""
    edges: set[tuple[int, int, str]] = set()
    vertices: set[int] = {0}
    next_vertex = 1
    reduced_words = [base.reduce_word(word) for word in words]
    for word in reduced_words:
        current = 0
        for ch in word:
            target = next_vertex
            next_vertex += 1
            label, direction = canonical_step(ch)
            if direction == 1:
                edge = (current, target, label)
            else:
                edge = (target, current, label)
            edges.add(edge)
            vertices.add(current)
            vertices.add(target)
            current = target
        if word:
            # Common fixed basepoint closes each word trajectory at the root.
            vertices.discard(current)
            edges = {
                (0 if src == current else src, 0 if dst == current else dst, label)
                for src, dst, label in edges
            }
            vertices = {0 if v == current else v for v in vertices}
    return graph_invariants(reduced_words, vertices, edges)


def graph_invariants(reduced_words: list[str], vertices: set[int], edges: set[tuple[int, int, str]]) -> dict[str, object]:
    parent = {v: v for v in vertices}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for src, dst, _ in edges:
        union(src, dst)
    components = len({find(v) for v in vertices}) if vertices else 0
    undirected_edges = len({(min(src, dst), max(src, dst), label) for src, dst, label in edges})
    cyclomatic_rank = undirected_edges - len(vertices) + components
    gens = sorted({ch.lower() for word in reduced_words for ch in word})
    is_cyclic = len(gens) <= 1 and all(word != "" for word in reduced_words)
    identity_present = any(word == "" for word in reduced_words)
    return {
        "reduced_words": reduced_words,
        "vertices": len(vertices),
        "directed_edges": len(edges),
        "undirected_edges": undirected_edges,
        "components": components,
        "cyclomatic_rank": max(0, cyclomatic_rank),
        "generator_rank": len(gens),
        "is_cyclic_power_family": is_cyclic,
        "identity_present": identity_present,
        "max_word_len": max((len(word) for word in reduced_words), default=0),
    }


def trajectory_profile(words: Iterable[str], perms: dict[str, np.ndarray], n: int, start: int) -> str:
    """Return a compact collision profile for trajectories from one basepoint."""
    seen: dict[int, int] = {start: 0}
    collisions = 0
    endpoints_fixed = 0
    visited_total = 1
    for word in words:
        point = start
        for ch in base.reduce_word(word):
            point = int(perms[ch][point])
            visited_total += 1
            if point in seen:
                collisions += 1
            else:
                seen[point] = len(seen)
        if point == start:
            endpoints_fixed += 1
    return f"v{len(seen)}_c{collisions}_e{endpoints_fixed}_t{visited_total}"


def sampled_profile(words: Iterable[str], perms: dict[str, np.ndarray], n: int, rng: np.random.Generator, max_points: int) -> str:
    common_images = [base.eval_word(word, perms, n) for word in words]
    fixed = np.ones(n, dtype=bool)
    points = np.arange(n)
    for image in common_images:
        fixed &= image == points
    candidates = np.flatnonzero(fixed)
    source = "fixed"
    if len(candidates) == 0:
        size = min(max_points, n)
        candidates = rng.choice(n, size=size, replace=False)
        source = "ambient"
    elif len(candidates) > max_points:
        candidates = rng.choice(candidates, size=max_points, replace=False)
    counts = Counter(trajectory_profile(words, perms, n, int(point)) for point in candidates)
    body = ";".join(f"{key}:{counts[key]}" for key in sorted(counts))
    return f"{source}|{body}"


def generators_in_families(families: Iterable[FoldedFamily]) -> str:
    gens = sorted({ch.lower() for family in families for word in family.words for ch in base.reduce_word(word) if ch.isalpha()})
    return "".join(gens) or "a"


def family_rows(n_values: list[int], samples: int, seed: int, max_profile_points: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    base_seed = np.random.SeedSequence(seed)
    child_sequences = base_seed.spawn(len(n_values) * samples)
    seq_iter = iter(child_sequences)
    generators = generators_in_families(WORD_FAMILIES)
    invariants = {family.family: build_trajectory_graph(family.words) for family in WORD_FAMILIES}
    for n in n_values:
        for sample in range(samples):
            rng = np.random.default_rng(next(seq_iter))
            perms = base.random_generator_perms(n, rng, generators=generators)
            for family in WORD_FAMILIES:
                inv = invariants[family.family]
                fixed_common = base.count_common_fixed(family.words, perms, n)
                rows.append(
                    {
                        "n": n,
                        "sample": sample,
                        "family": family.family,
                        "group": family.group,
                        "words": " ".join(family.words),
                        "word_count": len(family.words),
                        "max_word_len": inv["max_word_len"],
                        "vertices": inv["vertices"],
                        "directed_edges": inv["directed_edges"],
                        "undirected_edges": inv["undirected_edges"],
                        "components": inv["components"],
                        "cyclomatic_rank": inv["cyclomatic_rank"],
                        "generator_rank": inv["generator_rank"],
                        "is_cyclic_power_family": int(bool(inv["is_cyclic_power_family"])),
                        "identity_present": int(bool(inv["identity_present"])),
                        "fixed_common": fixed_common,
                        "trajectory_profile": sampled_profile(family.words, perms, n, rng, max_profile_points),
                        "seed": seed,
                    }
                )
    return rows


FIELDS = [
    "n",
    "sample",
    "family",
    "group",
    "words",
    "word_count",
    "max_word_len",
    "vertices",
    "directed_edges",
    "undirected_edges",
    "components",
    "cyclomatic_rank",
    "generator_rank",
    "is_cyclic_power_family",
    "identity_present",
    "fixed_common",
    "trajectory_profile",
    "seed",
]


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
    grouped: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["family"], int(row["n"]))].append(row)
    out: list[dict[str, object]] = []
    for (family, n), vals in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1])):
        counts = np.asarray([float(row["fixed_common"]) for row in vals], dtype=float)
        first = vals[0]
        out.append(
            {
                "family": family,
                "group": first["group"],
                "n": n,
                "mean": float(counts.mean()),
                "variance": float(counts.var(ddof=1)) if len(counts) > 1 else 0.0,
                "q90": float(np.quantile(counts, 0.90)),
                "q99": float(np.quantile(counts, 0.99)),
                "vertices": int(first["vertices"]),
                "directed_edges": int(first["directed_edges"]),
                "cyclomatic_rank": int(first["cyclomatic_rank"]),
                "generator_rank": int(first["generator_rank"]),
                "is_cyclic_power_family": int(first["is_cyclic_power_family"]),
            }
        )
    return out


def write_summary_csv(summary: list[dict[str, object]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "family",
        "group",
        "n",
        "mean",
        "variance",
        "q90",
        "q99",
        "vertices",
        "directed_edges",
        "cyclomatic_rank",
        "generator_rank",
        "is_cyclic_power_family",
    ]
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)


def plot_rank_scaling(summary: list[dict[str, object]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in summary:
        key = f"rank {row['generator_rank']}, cyclic {row['is_cyclic_power_family']}"
        grouped[key][int(row["n"])].append(float(row["mean"]))
    fig, ax = plt.subplots(figsize=(8, 5))
    for key, by_n in sorted(grouped.items()):
        xs = sorted(by_n)
        ys = [float(np.mean(by_n[n])) for n in xs]
        ax.plot(xs, ys, marker="o", label=key)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("cover degree n")
    ax.set_ylabel("mean common fixed-point count")
    ax.set_title("Folded word-graph rank/cyclicity scaling")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_profile_heatmap(rows: list[dict[str, str]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    selected = ["cyclic_pair_a_a2", "rank_two_pair_a_b", "rank_two_pair_ab_ba", "cyclic_eight", "mixed_eight", "rank_two_eight"]
    profile_counts: dict[str, Counter[str]] = {family: Counter() for family in selected}
    for row in rows:
        family = row["family"]
        if family not in profile_counts:
            continue
        for part in row["trajectory_profile"].split("|", 1)[-1].split(";"):
            if not part:
                continue
            key, value = part.rsplit(":", 1)
            profile_counts[family][key] += int(value)
    total_counts: Counter[str] = Counter()
    for counts in profile_counts.values():
        total_counts.update(counts)
    profiles = [profile for profile, _ in total_counts.most_common(12)]
    data = np.zeros((len(selected), len(profiles)))
    for i, family in enumerate(selected):
        total = sum(profile_counts[family].values()) or 1
        for j, profile in enumerate(profiles):
            data[i, j] = profile_counts[family][profile] / total
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(data, aspect="auto", cmap="viridis")
    ax.set_yticks(range(len(selected)), labels=selected)
    ax.set_xticks(range(len(profiles)), labels=profiles, rotation=45, ha="right")
    ax.set_title("Folded trajectory profile frequencies")
    fig.colorbar(im, ax=ax, label="empirical frequency")
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def parse_n_values(text: str) -> list[int]:
    return [int(part) for part in text.split(",") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", default="50,100,200,400")
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260515)
    parser.add_argument("--max-profile-points", type=int, default=8)
    parser.add_argument("--out-csv", type=Path, default=ROOT / "data/polynomial_method/folded_word_graph_probe.csv")
    parser.add_argument("--summary-csv", type=Path, default=ROOT / "data/polynomial_method/folded_word_graph_summary.csv")
    parser.add_argument("--rank-png", type=Path, default=ROOT / "reports/figures/m3_folded_graph_rank_scaling.png")
    parser.add_argument("--heatmap-png", type=Path, default=ROOT / "reports/figures/m3_folded_graph_profile_heatmap.png")
    parser.add_argument("--plot-only", action="store_true")
    args = parser.parse_args()

    if args.plot_only:
        rows = read_csv(args.out_csv)
    else:
        rows_raw = family_rows(parse_n_values(args.n_values), args.samples, args.seed, args.max_profile_points)
        write_csv(rows_raw, args.out_csv)
        rows = [{key: str(value) for key, value in row.items()} for row in rows_raw]
    summary = summarize(rows)
    write_summary_csv(summary, args.summary_csv)
    plot_rank_scaling(summary, args.rank_png)
    plot_profile_heatmap(rows, args.heatmap_png)
    print(f"wrote {len(rows)} rows to {args.out_csv}")
    print(f"wrote summary to {args.summary_csv}")
    print(f"wrote figures to {args.rank_png} and {args.heatmap_png}")


if __name__ == "__main__":
    main()
