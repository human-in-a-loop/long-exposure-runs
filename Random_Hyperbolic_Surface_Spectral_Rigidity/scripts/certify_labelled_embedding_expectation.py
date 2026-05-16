# created: 2026-05-15T23:00:00Z
# cycle: 12
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M4-formal-certification
"""Certify exact expectations for labelled-template permutation embeddings."""

from __future__ import annotations

import argparse
import csv
import itertools
import math
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class LabelledTemplate:
    name: str
    vertices: tuple[int, ...]
    edges: tuple[tuple[int, int, str], ...]
    description: str


TEMPLATES: tuple[LabelledTemplate, ...] = (
    LabelledTemplate("no_edge", (0, 1), (), "two free injective vertices"),
    LabelledTemplate("single_edge", (0, 1), ((0, 1, "a"),), "one forward labelled edge"),
    LabelledTemplate("same_label_path", (0, 1, 2), ((0, 1, "a"), (1, 2, "a")), "two compatible same-label constraints"),
    LabelledTemplate("conflicting_domain", (0, 1, 2), ((0, 1, "a"), (0, 2, "a")), "one source forced to two targets"),
    LabelledTemplate("conflicting_image", (0, 1, 2), ((1, 0, "a"), (2, 0, "a")), "two sources forced to one target"),
    LabelledTemplate("inverse_edge", (0, 1), ((0, 1, "A"),), "inverse label normalized by reversing orientation"),
    LabelledTemplate("inverse_regression_pair", (0, 1), ((0, 1, "a"), (0, 1, "A")), "Cycle 8 inverse-label regression case"),
    LabelledTemplate(
        "eight_word_cyclic_toy",
        tuple(range(8)),
        tuple((i, (i + 1) % 8, "a") for i in range(8)),
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
        "two four-edge labelled cycles sharing one vertex",
    ),
)


FIELDS = [
    "n",
    "template",
    "vertices",
    "raw_edges",
    "constraint_total",
    "constraint_counts",
    "partial_injection",
    "formula_expectation",
    "bruteforce_expectation",
    "match",
    "normalized_by_naive_power",
    "description",
]


def falling_factorial(n: int, k: int) -> int:
    if k < 0:
        raise ValueError("k must be nonnegative")
    if k > n:
        return 0
    out = 1
    for value in range(n - k + 1, n + 1):
        out *= value
    return out


def normalize_edge(src: int, dst: int, label: str) -> tuple[int, int, str]:
    if len(label) != 1 or not label.isalpha():
        raise ValueError(f"unsupported edge label {label!r}")
    if label.isupper():
        return dst, src, label.lower()
    return src, dst, label.lower()


def constraint_counts(template: LabelledTemplate) -> dict[str, int] | None:
    by_label: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for src, dst, label in template.edges:
        by_label[normalize_edge(src, dst, label)[2]].add(normalize_edge(src, dst, label)[:2])

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
    return dict(sorted(counts.items()))


def formula_expectation(template: LabelledTemplate, n: int) -> Fraction:
    if n < len(template.vertices):
        return Fraction(0, 1)
    counts = constraint_counts(template)
    if counts is None:
        return Fraction(0, 1)
    expectation = Fraction(falling_factorial(n, len(template.vertices)), 1)
    for count in counts.values():
        denom = falling_factorial(n, count)
        if denom == 0:
            return Fraction(0, 1)
        expectation *= Fraction(1, denom)
    return expectation


def labels_used(template: LabelledTemplate) -> tuple[str, ...]:
    return tuple(sorted({normalize_edge(src, dst, label)[2] for src, dst, label in template.edges}))


def invert_perm(perm: tuple[int, ...]) -> tuple[int, ...]:
    inv = [0] * len(perm)
    for idx, value in enumerate(perm):
        inv[value] = idx
    return tuple(inv)


def edge_satisfied(edge: tuple[int, int, str], assignment: dict[int, int], perms: dict[str, tuple[int, ...]]) -> bool:
    src, dst, label = edge
    if label.isupper():
        return perms[label.lower()][assignment[dst]] == assignment[src]
    return perms[label.lower()][assignment[src]] == assignment[dst]


def count_embeddings_for_perms(template: LabelledTemplate, n: int, perms: dict[str, tuple[int, ...]]) -> int:
    count = 0
    for values in itertools.permutations(range(n), len(template.vertices)):
        assignment = dict(zip(template.vertices, values))
        if all(edge_satisfied(edge, assignment, perms) for edge in template.edges):
            count += 1
    return count


def brute_force_expectation(template: LabelledTemplate, n: int) -> Fraction:
    if n < len(template.vertices):
        return Fraction(0, 1)
    labels = labels_used(template)
    if not labels:
        return Fraction(falling_factorial(n, len(template.vertices)), 1)
    perms_by_label = [list(itertools.permutations(range(n))) for _ in labels]
    total = 0
    tuples = 0
    for perm_tuple in itertools.product(*perms_by_label):
        perms = dict(zip(labels, perm_tuple))
        total += count_embeddings_for_perms(template, n, perms)
        tuples += 1
    return Fraction(total, tuples)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def normalized_by_naive_power(template: LabelledTemplate, n: int, expectation: Fraction) -> Fraction:
    counts = constraint_counts(template)
    constraint_total = sum(counts.values()) if counts else len(template.edges)
    exponent = len(template.vertices) - constraint_total
    if exponent >= 0:
        return expectation / Fraction(n**exponent, 1)
    return expectation * Fraction(n ** (-exponent), 1)


def result_rows(max_n: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for template in TEMPLATES:
        for n in range(2, max_n + 1):
            counts = constraint_counts(template)
            formula = formula_expectation(template, n)
            brute = brute_force_expectation(template, n)
            rows.append(
                {
                    "n": n,
                    "template": template.name,
                    "vertices": len(template.vertices),
                    "raw_edges": len(template.edges),
                    "constraint_total": sum(counts.values()) if counts else "",
                    "constraint_counts": " ".join(f"{label}:{count}" for label, count in (counts or {}).items()),
                    "partial_injection": int(counts is not None),
                    "formula_expectation": fraction_text(formula),
                    "bruteforce_expectation": fraction_text(brute),
                    "match": int(formula == brute),
                    "normalized_by_naive_power": fraction_text(normalized_by_naive_power(template, n, formula)),
                    "description": template.description,
                }
            )
    return rows


def write_csv(rows: list[dict[str, object]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=4)
    parser.add_argument("--out-csv", type=Path, default=ROOT / "data/formal_certification/labelled_embedding_expectation_exhaustive.csv")
    args = parser.parse_args()
    if args.max_n > 4:
        raise ValueError("max-n above 4 is intentionally disabled; exhaustive enumeration scales as |S_n|^labels")
    rows = result_rows(args.max_n)
    write_csv(rows, args.out_csv)
    mismatches = [row for row in rows if row["match"] != 1]
    if mismatches:
        raise AssertionError(f"{len(mismatches)} formula/bruteforce mismatches")
    print(f"wrote {len(rows)} exhaustive certification rows to {args.out_csv}")
    print("all formula expectations match brute-force enumeration")


if __name__ == "__main__":
    main()
