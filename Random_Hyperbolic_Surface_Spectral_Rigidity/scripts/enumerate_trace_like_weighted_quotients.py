# created: 2026-05-16T09:05:00Z
# cycle: 22
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M11-trace-like-weighted-quotient-class
"""Enumerate trace-like weighted quotient classes before folded skeleton aggregation."""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
PROFILE_CSV = ROOT / "data/extension_candidates/trace_like_weighted_quotient_profiles.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/trace_like_weighted_quotient_summary.csv"
DIAGONAL_CSV = ROOT / "data/extension_candidates/trace_like_weighted_diagonal_decomposition.csv"
GROWTH_FIG = ROOT / "reports/figures/m11_trace_like_family_growth.png"
DIAGONAL_FIG = ROOT / "reports/figures/m11_diagonal_subtraction_effect.png"
TV_FIG = ROOT / "reports/figures/m11_weighted_total_variation.png"
LETTERS = ("a", "A", "b", "B")
INVERSE = {"a": "A", "A": "a", "b": "B", "B": "b"}
LABEL = {"a": "a", "A": "a", "b": "b", "B": "b"}
L_MAX = 5
MAX_ORDER = 4


@dataclass(frozen=True)
class Skeleton:
    key: str
    edges: tuple[tuple[int, str, int], ...]
    vertex_count: int
    count_a: int
    count_b: int
    conflict: bool


@dataclass(frozen=True)
class ConjugacyRep:
    word: str
    length: int
    orbit_size: int
    primitive_root: str
    primitive_power_exponent: int


@dataclass(frozen=True)
class PairRecord:
    L: int
    u: ConjugacyRep
    v: ConjugacyRep
    skeleton: Skeleton
    diagonal_cyclic: bool
    rank_label: str


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


def is_cyclically_reduced(word: str) -> bool:
    return bool(word) and INVERSE[word[0]] != word[-1]


def inverse_word(word: str) -> str:
    return "".join(INVERSE[letter] for letter in reversed(word))


def rotations(word: str) -> list[str]:
    return [word[index:] + word[:index] for index in range(len(word))]


def conjugacy_orbit(word: str) -> set[str]:
    return set(rotations(word)) | set(rotations(inverse_word(word)))


def canonical_conjugacy_word(word: str) -> str:
    if not is_cyclically_reduced(word):
        raise ValueError(f"word is not cyclically reduced: {word}")
    return min(conjugacy_orbit(word))


def primitive_root(word: str) -> tuple[str, int]:
    canonical = canonical_conjugacy_word(word)
    n = len(canonical)
    for d in range(1, n + 1):
        if n % d:
            continue
        block = canonical[:d]
        if block * (n // d) == canonical:
            return canonical_conjugacy_word(block), n // d
    return canonical, 1


def conjugacy_representatives(max_len: int) -> list[ConjugacyRep]:
    reps: dict[str, set[str]] = {}
    for word in reduced_words(max_len):
        if not is_cyclically_reduced(word):
            continue
        key = canonical_conjugacy_word(word)
        reps.setdefault(key, set()).add(word)
    out: list[ConjugacyRep] = []
    for word, orbit in sorted(reps.items(), key=lambda item: (len(item[0]), item[0])):
        root, exponent = primitive_root(word)
        out.append(ConjugacyRep(word, len(word), len(orbit), root, exponent))
    return out


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
    return Skeleton(key, canonical, len(relabel), counts["a"], counts["b"], conflict)


def rank_proxy(skeleton: Skeleton) -> str:
    labels = {label for _, label, _ in skeleton.edges}
    return "rank_one" if len(labels) <= 1 else "rank_two_noncyclic"


def product_profile(skeleton: Skeleton) -> tuple[list[int], list[int]]:
    numerator = list(range(skeleton.vertex_count))
    denominator = list(range(skeleton.count_a)) + list(range(skeleton.count_b))
    return numerator, denominator


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
        coeffs = multiply_poly(coeffs, [Fraction(j) ** r for r in range(max_order + 1)])
    return coeffs


def frac_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def num_text(value: float | Fraction) -> str:
    if isinstance(value, Fraction):
        return frac_text(value)
    return f"{value:.12g}"


def pair_multiplicity(record: PairRecord) -> int:
    return record.u.orbit_size * record.v.orbit_size


def pair_weights(record: PairRecord) -> dict[str, float]:
    mult = pair_multiplicity(record)
    length_sum = record.u.length + record.v.length
    return {
        "weight_unweighted": float(mult),
        "weight_exp_decay_theta_0_5": mult * math.exp(-0.5 * length_sum),
        "weight_length_inverse": mult / max(1, record.u.length * record.v.length),
    }


def is_diagonal_cyclic(u: ConjugacyRep, v: ConjugacyRep, skeleton: Skeleton) -> bool:
    return u.word == v.word or u.primitive_root == v.primitive_root or rank_proxy(skeleton) == "rank_one"


def build_pair_records(max_len: int = L_MAX) -> list[PairRecord]:
    reps = conjugacy_representatives(max_len)
    by_l = defaultdict(list)
    for rep in reps:
        by_l[rep.length].append(rep)
    records: list[PairRecord] = []
    for L in range(1, max_len + 1):
        eligible = [rep for length in range(1, L + 1) for rep in by_l[length]]
        for u in eligible:
            for v in eligible:
                skeleton = canonicalize_edges(two_word_edges(u.word, v.word))
                records.append(PairRecord(L, u, v, skeleton, is_diagonal_cyclic(u, v, skeleton), rank_proxy(skeleton)))
    return records


def build_profile_rows(records: list[PairRecord]) -> list[dict[str, str]]:
    grouped: dict[tuple[int, str, bool], list[PairRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.L, record.skeleton.key, record.skeleton.conflict)].append(record)
    rows: list[dict[str, str]] = []
    for (L, key, _), items in sorted(grouped.items()):
        skeleton = items[0].skeleton
        coeffs = profile_coefficients(skeleton)
        weights = defaultdict(float)
        diagonal_classes = 0
        primitive_nondiagonal_classes = 0
        rank_two_after_diagonal_classes = 0
        primitive_power_classes = 0
        pre_fold_multiplicity = 0
        for item in items:
            pre_fold_multiplicity += pair_multiplicity(item)
            for name, value in pair_weights(item).items():
                weights[name] += value
            if item.u.primitive_power_exponent > 1 or item.v.primitive_power_exponent > 1:
                primitive_power_classes += 1
            if item.diagonal_cyclic:
                diagonal_classes += 1
            elif item.u.primitive_power_exponent == 1 and item.v.primitive_power_exponent == 1:
                primitive_nondiagonal_classes += 1
            if not item.diagonal_cyclic and item.rank_label == "rank_two_noncyclic":
                rank_two_after_diagonal_classes += 1
        C = skeleton.count_a + skeleton.count_b
        rows.append(
            {
                "L": str(L),
                "canonical_key": key,
                "conjugacy_class_multiplicity": str(len(items)),
                "pre_fold_pair_multiplicity": str(pre_fold_multiplicity),
                "weight_unweighted": num_text(weights["weight_unweighted"]),
                "weight_exp_decay_theta_0_5": num_text(weights["weight_exp_decay_theta_0_5"]),
                "weight_length_inverse": num_text(weights["weight_length_inverse"]),
                "V": str(skeleton.vertex_count),
                "count_a": str(skeleton.count_a),
                "count_b": str(skeleton.count_b),
                "C": str(C),
                "n_power": str(C - skeleton.vertex_count),
                "conflict": "yes" if skeleton.conflict else "no",
                "primitive_power_pair_classes": str(primitive_power_classes),
                "diagonal_cyclic_pair_classes": str(diagonal_classes),
                "primitive_nondiagonal_pair_classes": str(primitive_nondiagonal_classes),
                "rank_two_after_diagonal_pair_classes": str(rank_two_after_diagonal_classes),
                "rank_proxy": rank_proxy(skeleton),
                "coeff_order_1": frac_text(coeffs[1]),
                "coeff_order_2": frac_text(coeffs[2]),
                "coeff_order_3": frac_text(coeffs[3]),
                "coeff_order_4": frac_text(coeffs[4]),
                "notes": "trace-like cyclic conjugacy pairs before folded skeleton aggregation",
            }
        )
    return rows


def record_in_variant(record: PairRecord, variant: str) -> bool:
    if record.skeleton.conflict:
        return False
    if variant == "all_conflict_free":
        return True
    if variant == "primitive_non_diagonal":
        return not record.diagonal_cyclic and record.u.primitive_power_exponent == 1 and record.v.primitive_power_exponent == 1
    if variant == "diagonal_cyclic_only":
        return record.diagonal_cyclic
    if variant == "signed_diagonal_subtracted_proxy":
        return not record.diagonal_cyclic
    if variant == "rank_two_noncyclic_remainder":
        return not record.diagonal_cyclic and record.rank_label == "rank_two_noncyclic"
    raise ValueError(variant)


def summarize_records(records: list[PairRecord]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    variants = [
        "all_conflict_free",
        "primitive_non_diagonal",
        "diagonal_cyclic_only",
        "signed_diagonal_subtracted_proxy",
        "rank_two_noncyclic_remainder",
    ]
    weight_schemes = ["weight_unweighted", "weight_exp_decay_theta_0_5", "weight_length_inverse"]
    by_l = defaultdict(list)
    for record in records:
        by_l[record.L].append(record)
    for L in sorted(by_l):
        for variant in variants:
            variant_records = [record for record in by_l[L] if record_in_variant(record, variant)]
            profile_count = len({record.skeleton.key for record in variant_records})
            pair_classes = len(variant_records)
            for scheme in weight_schemes:
                for order in range(1, MAX_ORDER + 1):
                    aggregate = 0.0
                    weight_l1 = 0.0
                    for record in variant_records:
                        weight = pair_weights(record)[scheme]
                        aggregate += weight * float(profile_coefficients(record.skeleton)[order])
                        weight_l1 += abs(weight)
                    per_template = L ** (2 * order)
                    rows.append(
                        {
                            "L": str(L),
                            "variant": variant,
                            "weight_scheme": scheme,
                            "num_profiles": str(profile_count),
                            "pair_classes": str(pair_classes),
                            "coefficient_order": str(order),
                            "aggregate_coefficient": num_text(aggregate),
                            "weight_l1": num_text(weight_l1),
                            "m7_bound_proxy": str(per_template),
                            "weighted_aggregate_bound_proxy": num_text(per_template * weight_l1),
                            "notes": "signed proxy is all conflict-free with diagonal/cyclic records removed",
                        }
                    )
    return rows


def build_diagonal_rows(records: list[PairRecord]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    by_l = defaultdict(list)
    for record in records:
        by_l[record.L].append(record)
    for L in sorted(by_l):
        for category, keep in [
            ("conflict", lambda r: r.skeleton.conflict),
            ("diagonal_cyclic", lambda r: (not r.skeleton.conflict) and r.diagonal_cyclic),
            ("primitive_non_diagonal", lambda r: (not r.skeleton.conflict) and (not r.diagonal_cyclic) and r.u.primitive_power_exponent == 1 and r.v.primitive_power_exponent == 1),
            ("rank_two_after_diagonal", lambda r: (not r.skeleton.conflict) and (not r.diagonal_cyclic) and r.rank_label == "rank_two_noncyclic"),
        ]:
            items = [record for record in by_l[L] if keep(record)]
            weights = defaultdict(float)
            for item in items:
                for name, value in pair_weights(item).items():
                    weights[name] += abs(value)
            rows.append(
                {
                    "L": str(L),
                    "category": category,
                    "pair_classes": str(len(items)),
                    "pre_fold_pair_multiplicity": str(sum(pair_multiplicity(item) for item in items)),
                    "num_profiles": str(len({item.skeleton.key for item in items})),
                    "weight_unweighted_l1": num_text(weights["weight_unweighted"]),
                    "weight_exp_decay_theta_0_5_l1": num_text(weights["weight_exp_decay_theta_0_5"]),
                    "weight_length_inverse_l1": num_text(weights["weight_length_inverse"]),
                    "notes": "classification is assigned before folding; profile count is after folding",
                }
            )
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_growth(records: list[PairRecord], profile_rows: list[dict[str, str]]) -> None:
    GROWTH_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    xs = list(range(1, L_MAX + 1))
    raw_words = [len(reduced_words(L)) for L in xs]
    raw_pairs = [value * value for value in raw_words]
    reps = [len(conjugacy_representatives(L)) for L in xs]
    rep_pairs = [value * value for value in reps]
    folded = [len({row["canonical_key"] for row in profile_rows if row["L"] == str(L)}) for L in xs]
    conflict_free = [len({row["canonical_key"] for row in profile_rows if row["L"] == str(L) and row["conflict"] == "no"}) for L in xs]
    for values, label, color in [
        (raw_pairs, "raw ordered reduced-word pairs", "#4c78a8"),
        (rep_pairs, "ordered conjugacy-representative pairs", "#f28e2b"),
        (folded, "folded profiles", "#59a14f"),
        (conflict_free, "conflict-free folded profiles", "#e15759"),
    ]:
        ax.plot(xs, values, marker="o", label=label, color=color)
    ax.set_yscale("log")
    ax.set_xlabel("maximum length L")
    ax.set_ylabel("count")
    ax.set_title("Trace-like quotienting before folding")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "Caption: raw ordered word-pair counts, cyclic conjugacy representative pairs, folded profiles, and conflict-free folded profiles by length cutoff.", fontsize=8)
    fig.savefig(GROWTH_FIG, dpi=160)
    plt.close(fig)


def plot_diagonal_effect(summary_rows: list[dict[str, str]]) -> None:
    DIAGONAL_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    colors = {"all_conflict_free": "#4c78a8", "diagonal_cyclic_only": "#f28e2b", "signed_diagonal_subtracted_proxy": "#e15759"}
    for variant, color in colors.items():
        rows = [
            row
            for row in summary_rows
            if row["variant"] == variant and row["weight_scheme"] == "weight_unweighted" and row["coefficient_order"] == "1"
        ]
        ax.plot([int(row["L"]) for row in rows], [max(abs(float(row["aggregate_coefficient"])), 1e-6) for row in rows], marker="o", label=variant, color=color)
    ax.set_yscale("log")
    ax.set_xlabel("maximum length L")
    ax.set_ylabel("|aggregate coefficient of x|, unweighted")
    ax.set_title("Diagonal subtraction effect")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "Caption: unweighted order-one aggregate coefficient magnitudes before, within, and after signed diagonal/cyclic subtraction.", fontsize=8)
    fig.savefig(DIAGONAL_FIG, dpi=160)
    plt.close(fig)


def plot_weighted_total_variation(summary_rows: list[dict[str, str]]) -> None:
    TV_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    colors = {"weight_unweighted": "#4c78a8", "weight_exp_decay_theta_0_5": "#f28e2b", "weight_length_inverse": "#59a14f"}
    for scheme, color in colors.items():
        rows = [
            row
            for row in summary_rows
            if row["variant"] == "all_conflict_free" and row["weight_scheme"] == scheme and row["coefficient_order"] == "1"
        ]
        ax.plot([int(row["L"]) for row in rows], [float(row["weight_l1"]) for row in rows], marker="o", label=scheme, color=color)
    ax.set_yscale("log")
    ax.set_xlabel("maximum length L")
    ax.set_ylabel("total variation proxy")
    ax.set_title("Weighted total variation for conflict-free classes")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "Caption: total variation proxies for all conflict-free trace-like quotient classes under unweighted, exponential-decay, and inverse-length weights.", fontsize=8)
    fig.savefig(TV_FIG, dpi=160)
    plt.close(fig)


def main() -> None:
    records = build_pair_records()
    profile_rows = build_profile_rows(records)
    summary_rows = summarize_records(records)
    diagonal_rows = build_diagonal_rows(records)
    write_csv(profile_rows, PROFILE_CSV)
    write_csv(summary_rows, SUMMARY_CSV)
    write_csv(diagonal_rows, DIAGONAL_CSV)
    plot_growth(records, profile_rows)
    plot_diagonal_effect(summary_rows)
    plot_weighted_total_variation(summary_rows)
    print(f"wrote {PROFILE_CSV}")
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {DIAGONAL_CSV}")
    print(f"wrote {GROWTH_FIG}")
    print(f"wrote {DIAGONAL_FIG}")
    print(f"wrote {TV_FIG}")
    for L in range(1, L_MAX + 1):
        profiles = [row for row in profile_rows if row["L"] == str(L)]
        conflict_free = [row for row in profiles if row["conflict"] == "no"]
        print(f"L={L}: profiles={len(profiles)} conflict_free={len(conflict_free)} pair_records={sum(1 for record in records if record.L == L)}")


if __name__ == "__main__":
    main()
