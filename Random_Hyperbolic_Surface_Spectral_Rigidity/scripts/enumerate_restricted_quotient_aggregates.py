# created: 2026-05-16T08:05:00Z
# cycle: 21
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M10-restricted-quotient-aggregate
"""Enumerate a restricted two-word folded quotient aggregate toy model."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
PROFILE_CSV = ROOT / "data/extension_candidates/restricted_quotient_family_profiles.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/restricted_quotient_aggregate_summary.csv"
GROWTH_FIG = ROOT / "reports/figures/m10_restricted_quotient_family_growth.png"
COEFF_FIG = ROOT / "reports/figures/m10_restricted_quotient_aggregate_coefficients.png"
LETTERS = ("a", "A", "b", "B")
INVERSE = {"a": "A", "A": "a", "b": "B", "B": "b"}
LABEL = {"a": "a", "A": "a", "b": "b", "B": "b"}
L_MAX = 4
MAX_ORDER = 4


@dataclass(frozen=True)
class Skeleton:
    key: str
    edges: tuple[tuple[int, str, int], ...]
    vertex_count: int
    count_a: int
    count_b: int
    conflict: bool


class DSU:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if ry == 0:
            rx, ry = ry, rx
        self.parent[ry] = rx
        return True


def reduced_words(max_len: int) -> list[str]:
    words: list[str] = []

    def extend(prefix: str, remaining: int) -> None:
        if prefix:
            words.append(prefix)
        if remaining == 0:
            return
        for letter in LETTERS:
            if prefix and INVERSE[prefix[-1]] == letter:
                continue
            extend(prefix + letter, remaining - 1)

    extend("", max_len)
    return words


def normalize_step(source: int, target: int, letter: str) -> tuple[int, str, int]:
    label = LABEL[letter]
    if letter.isupper():
        return target, label, source
    return source, label, target


def word_loop_edges(word: str, start_vertex: int) -> tuple[list[tuple[int, str, int]], int]:
    edges: list[tuple[int, str, int]] = []
    current = 0
    next_vertex = start_vertex
    for index, letter in enumerate(word):
        target = 0 if index == len(word) - 1 else next_vertex
        if target != 0:
            next_vertex += 1
        edges.append(normalize_step(current, target, letter))
        current = target
    return edges, next_vertex


def two_word_edges(u: str, v: str) -> list[tuple[int, str, int]]:
    first, next_vertex = word_loop_edges(u, 1)
    second, _ = word_loop_edges(v, next_vertex)
    return first + second


def has_partial_injection_conflict(edges: list[tuple[int, str, int]]) -> bool:
    outgoing: dict[tuple[int, str], int] = {}
    incoming: dict[tuple[str, int], int] = {}
    for source, label, target in edges:
        out_key = (source, label)
        in_key = (label, target)
        if out_key in outgoing and outgoing[out_key] != target:
            return True
        if in_key in incoming and incoming[in_key] != source:
            return True
        outgoing[out_key] = target
        incoming[in_key] = source
    return False


def fold_edges(raw_edges: list[tuple[int, str, int]]) -> tuple[tuple[tuple[int, str, int], ...], bool]:
    max_vertex = max([0] + [v for edge in raw_edges for v in (edge[0], edge[2])])
    dsu = DSU(max_vertex + 1)
    conflict_seen = has_partial_injection_conflict(raw_edges)
    changed = True
    while changed:
        changed = False
        normalized = sorted({(dsu.find(s), label, dsu.find(t)) for s, label, t in raw_edges})
        by_out: dict[tuple[int, str], int] = {}
        by_in: dict[tuple[str, int], int] = {}
        for source, label, target in normalized:
            out_key = (source, label)
            in_key = (label, target)
            if out_key in by_out and dsu.union(by_out[out_key], target):
                conflict_seen = True
                changed = True
            else:
                by_out[out_key] = target
            if in_key in by_in and dsu.union(by_in[in_key], source):
                conflict_seen = True
                changed = True
            else:
                by_in[in_key] = source
    folded = tuple(sorted({(dsu.find(s), label, dsu.find(t)) for s, label, t in raw_edges}))
    return folded, conflict_seen


def canonicalize_edges(raw_edges: list[tuple[int, str, int]]) -> Skeleton:
    folded, conflict = fold_edges(raw_edges)
    adjacency: dict[int, list[tuple[str, int]]] = defaultdict(list)
    for source, label, target in folded:
        adjacency[source].append((label, target))
        adjacency[target].append((label.upper(), source))
    relabel = {0: 0}
    queue: deque[int] = deque([0])
    while queue:
        vertex = queue.popleft()
        for _, neighbor in sorted(adjacency[vertex], key=lambda item: (item[0], item[1])):
            if neighbor not in relabel:
                relabel[neighbor] = len(relabel)
                queue.append(neighbor)
    canonical = tuple(sorted((relabel[s], label, relabel[t]) for s, label, t in folded))
    key = ";".join(f"{s}{label}{t}" for s, label, t in canonical)
    counts = Counter(label for _, label, _ in canonical)
    return Skeleton(
        key=key,
        edges=canonical,
        vertex_count=len(relabel),
        count_a=counts["a"],
        count_b=counts["b"],
        conflict=conflict,
    )


def rank_proxy(skeleton: Skeleton) -> str:
    labels = {label for _, label, _ in skeleton.edges}
    if len(labels) <= 1:
        return "rank_one"
    return "rank_two_noncyclic"


def cyclic_proxy(skeleton: Skeleton) -> str:
    if rank_proxy(skeleton) == "rank_one":
        return "yes"
    degree = Counter()
    for source, _, target in skeleton.edges:
        degree[source] += 1
        degree[target] += 1
    return "yes" if degree and all(value == 2 for value in degree.values()) else "no"


def product_profile(skeleton: Skeleton) -> tuple[list[int], list[int]]:
    numerator = list(range(skeleton.vertex_count))
    denominator = list(range(skeleton.count_a)) + list(range(skeleton.count_b))
    return numerator, denominator


def profile_expression(skeleton: Skeleton) -> str:
    numerator, denominator = product_profile(skeleton)
    num = "*".join(f"(n-{j})" for j in numerator) or "1"
    den = "*".join(f"(n-{j})" for j in denominator) or "1"
    return f"{num}/{den}"


def multiply_poly(poly: list[Fraction], factor: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0) for _ in poly]
    for i, a in enumerate(poly):
        if a == 0:
            continue
        for j, b in enumerate(factor):
            if i + j < len(out):
                out[i + j] += a * b
    return out


def profile_coefficients(skeleton: Skeleton, max_order: int = MAX_ORDER) -> list[Fraction]:
    numerator, denominator = product_profile(skeleton)
    coeffs = [Fraction(1)] + [Fraction(0) for _ in range(max_order)]
    for j in numerator:
        coeffs = multiply_poly(coeffs, [Fraction(1), Fraction(-j)])
    for j in denominator:
        if j == 0:
            continue
        series = [Fraction(j) ** r for r in range(max_order + 1)]
        coeffs = multiply_poly(coeffs, series)
    return coeffs


def frac_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def build_profile_rows(max_len: int = L_MAX) -> list[dict[str, str]]:
    words = reduced_words(max_len)
    by_len = defaultdict(list)
    for word in words:
        by_len[len(word)].append(word)
    rows: list[dict[str, str]] = []
    for L in range(1, max_len + 1):
        grouped: dict[str, tuple[Skeleton, int]] = {}
        eligible = [word for length in range(1, L + 1) for word in by_len[length]]
        for u in eligible:
            for v in eligible:
                skeleton = canonicalize_edges(two_word_edges(u, v))
                old = grouped.get(skeleton.key)
                grouped[skeleton.key] = (skeleton, 1 if old is None else old[1] + 1)
        for key in sorted(grouped):
            skeleton, multiplicity = grouped[key]
            rows.append(
                {
                    "L": str(L),
                    "canonical_key": skeleton.key,
                    "multiplicity": str(multiplicity),
                    "V": str(skeleton.vertex_count),
                    "count_a": str(skeleton.count_a),
                    "count_b": str(skeleton.count_b),
                    "conflict": "yes" if skeleton.conflict else "no",
                    "rank_proxy": rank_proxy(skeleton),
                    "cyclic_proxy": cyclic_proxy(skeleton),
                    "profile_expression": "conflict" if skeleton.conflict else profile_expression(skeleton),
                    "notes": "folded two-loop skeleton from ordered reduced-word pairs",
                }
            )
    return rows


def row_variant(row: dict[str, str]) -> str:
    return "cyclic_rank_one" if row["cyclic_proxy"] == "yes" or row["rank_proxy"] == "rank_one" else "rank_two_noncyclic"


def coefficients_from_row(row: dict[str, str]) -> list[Fraction]:
    skeleton = Skeleton(
        key=row["canonical_key"],
        edges=tuple(),
        vertex_count=int(row["V"]),
        count_a=int(row["count_a"]),
        count_b=int(row["count_b"]),
        conflict=row["conflict"] == "yes",
    )
    return profile_coefficients(skeleton)


def summarize_profiles(profile_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    by_l = defaultdict(list)
    for row in profile_rows:
        by_l[int(row["L"])].append(row)
    for L in sorted(by_l):
        source_rows = [row for row in by_l[L] if row["conflict"] == "no"]
        variants = {
            "all_conflict_free": source_rows,
            "cyclic_rank_one": [row for row in source_rows if row_variant(row) == "cyclic_rank_one"],
            "rank_two_noncyclic": [row for row in source_rows if row_variant(row) == "rank_two_noncyclic"],
        }
        variants["diagonal_subtracted_proxy"] = source_rows
        for variant, variant_rows in variants.items():
            signs = {}
            if variant == "diagonal_subtracted_proxy":
                signs = {row["canonical_key"]: (-1 if row_variant(row) == "cyclic_rank_one" else 1) for row in variant_rows}
            for order in range(1, MAX_ORDER + 1):
                aggregate = Fraction(0)
                weight_l1 = 0
                total_multiplicity = 0
                for row in variant_rows:
                    multiplicity = int(row["multiplicity"])
                    sign = signs.get(row["canonical_key"], 1)
                    coeff = coefficients_from_row(row)[order]
                    aggregate += sign * multiplicity * coeff
                    weight_l1 += multiplicity
                    total_multiplicity += multiplicity
                per_template = L ** (2 * order)
                rows.append(
                    {
                        "L": str(L),
                        "variant": variant,
                        "num_skeletons": str(len(variant_rows)),
                        "total_multiplicity": str(total_multiplicity),
                        "weight_l1": str(weight_l1),
                        "coefficient_order": str(order),
                        "aggregate_coefficient": frac_text(aggregate),
                        "m7_bound_proxy": str(per_template),
                        "aggregate_bound_proxy": str(per_template * weight_l1),
                        "notes": "toy signed subtraction" if variant == "diagonal_subtracted_proxy" else "positive multiplicity aggregate",
                    }
                )
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_growth(profile_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    GROWTH_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    for variant, color in [
        ("all_conflict_free", "#4c78a8"),
        ("cyclic_rank_one", "#f28e2b"),
        ("rank_two_noncyclic", "#59a14f"),
    ]:
        rows = [row for row in summary_rows if row["variant"] == variant and row["coefficient_order"] == "1"]
        ax.plot([int(row["L"]) for row in rows], [int(row["num_skeletons"]) for row in rows], marker="o", color=color, label=f"{variant} skeletons")
        ax.plot([int(row["L"]) for row in rows], [int(row["total_multiplicity"]) for row in rows], linestyle="--", color=color, label=f"{variant} multiplicity")
    ax.set_yscale("log")
    ax.set_xlabel("maximum word length L")
    ax.set_ylabel("count")
    ax.set_title("Restricted folded quotient-family growth")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "Caption: canonical skeleton counts and multiplicities by length and rank-filter variant.", fontsize=8)
    fig.savefig(GROWTH_FIG, dpi=160)
    plt.close(fig)


def plot_coefficients(summary_rows: list[dict[str, str]]) -> None:
    COEFF_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    colors = {
        "all_conflict_free": "#4c78a8",
        "cyclic_rank_one": "#f28e2b",
        "rank_two_noncyclic": "#59a14f",
        "diagonal_subtracted_proxy": "#e15759",
    }
    for variant, color in colors.items():
        rows = [row for row in summary_rows if row["variant"] == variant and row["coefficient_order"] == "1"]
        ax.plot(
            [int(row["L"]) for row in rows],
            [max(abs(Fraction(row["aggregate_coefficient"])), Fraction(1, 1000)) for row in rows],
            marker="o",
            color=color,
            label=variant,
        )
    ax.set_yscale("log")
    ax.set_xlabel("maximum word length L")
    ax.set_ylabel("|aggregate coefficient of x|")
    ax.set_title("Aggregate coefficient growth by rank-filter variant")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "Caption: aggregate coefficient magnitudes for all, cyclic/rank-one, rank-two/noncyclic, and diagonal-subtracted proxy variants.", fontsize=8)
    fig.savefig(COEFF_FIG, dpi=160)
    plt.close(fig)


def main() -> None:
    profile_rows = build_profile_rows()
    summary_rows = summarize_profiles(profile_rows)
    write_csv(profile_rows, PROFILE_CSV)
    write_csv(summary_rows, SUMMARY_CSV)
    plot_growth(profile_rows, summary_rows)
    plot_coefficients(summary_rows)
    print(f"wrote {PROFILE_CSV}")
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {GROWTH_FIG}")
    print(f"wrote {COEFF_FIG}")
    for L in range(1, L_MAX + 1):
        rows = [row for row in summary_rows if row["L"] == str(L) and row["coefficient_order"] == "1"]
        compact = ", ".join(f"{row['variant']}={row['num_skeletons']}/{row['total_multiplicity']}" for row in rows)
        print(f"L={L}: {compact}")


if __name__ == "__main__":
    main()
