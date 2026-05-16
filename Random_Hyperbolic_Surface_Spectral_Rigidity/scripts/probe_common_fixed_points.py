# created: 2026-05-15T17:30:00Z
# cycle: 6
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M3-computational-probes
"""Monte Carlo probes for common fixed points of random permutation words."""

from __future__ import annotations

import argparse
import csv
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class WordFamily:
    family: str
    words: tuple[str, ...]
    scale_power: int
    description: str


WORD_FAMILIES: tuple[WordFamily, ...] = (
    WordFamily("identity_control", ("1",), 0, "identity word fixes every point"),
    WordFamily("cancel_control", ("aA",), 0, "inverse cancellation reduces to identity"),
    WordFamily("single_a", ("a",), 0, "one primitive word"),
    WordFamily("cyclic_pair_a_a2", ("a", "aa"), 0, "same primitive powers"),
    WordFamily("cyclic_triple_a_a2_a3", ("a", "aa", "aaa"), 0, "three same primitive powers"),
    WordFamily("duplicate_pair_a_a", ("a", "a"), 0, "duplicated constraint control"),
    WordFamily("rank_two_pair_a_b", ("a", "b"), 1, "independent generator fixed-point constraints"),
    WordFamily("rank_two_pair_ab_aB", ("ab", "aB"), 1, "two noncyclic reduced words"),
    WordFamily("independent_triple_a_b_c", ("a", "b", "c"), 2, "three independent generator constraints"),
    WordFamily("commutator_single", ("abAB",), 0, "single commutator-like word"),
    WordFamily("mixed_identity_a", ("1", "a"), 0, "identity plus one real constraint"),
    WordFamily("rank_two_four_a_b_ab_aB", ("a", "b", "ab", "aB"), 1, "rank-two words with dependent fixed-point constraints"),
    WordFamily("independent_four", ("a", "b", "c", "d"), 3, "four independent generator constraints"),
    WordFamily("cyclic_four", ("a", "aa", "aaa", "aaaa"), 0, "four same primitive powers"),
    WordFamily("rank_two_eight", ("a", "b", "ab", "aB", "ba", "bA", "aba", "abA"), 1, "eight rank-two words with dependent fixed-point constraints"),
    WordFamily("independent_eight", ("a", "b", "c", "d", "e", "f", "g", "h"), 7, "eight independent generator constraints"),
    WordFamily("cyclic_eight", ("a", "aa", "aaa", "aaaa", "aaaaa", "aaaaaa", "aaaaaaa", "aaaaaaaa"), 0, "eight same primitive powers"),
)


def reduce_word(word: str) -> str:
    """Reduce a word in free generators a,b,c using uppercase as inverse."""
    if word in ("", "1", "e", "id"):
        return ""
    stack: list[str] = []
    for ch in word:
        if not ch.isalpha():
            raise ValueError(f"unsupported word character {ch!r} in {word!r}")
        if stack and stack[-1] != ch and stack[-1].lower() == ch.lower():
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)


def invert_perm(perm: np.ndarray) -> np.ndarray:
    inv = np.empty_like(perm)
    inv[perm] = np.arange(len(perm))
    return inv


def random_generator_perms(n: int, rng: np.random.Generator, generators: str = "abc") -> dict[str, np.ndarray]:
    perms: dict[str, np.ndarray] = {}
    for gen in generators:
        perm = rng.permutation(n)
        perms[gen] = perm
        perms[gen.upper()] = invert_perm(perm)
    return perms


def generators_in_words(families: Iterable[WordFamily]) -> str:
    gens = sorted({ch.lower() for family in families for word in family.words for ch in reduce_word(word) if ch.isalpha()})
    return "".join(gens) or "a"


def eval_word(word: str, perms: dict[str, np.ndarray], n: int) -> np.ndarray:
    reduced = reduce_word(word)
    result = np.arange(n)
    for ch in reduced:
        result = perms[ch][result]
    return result


def count_common_fixed(words: Iterable[str], perms: dict[str, np.ndarray], n: int) -> int:
    points = np.arange(n)
    mask = np.ones(n, dtype=bool)
    for word in words:
        image = eval_word(word, perms, n)
        mask &= image == points
    return int(mask.sum())


def family_rows(n_values: list[int], samples: int, seed: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    base = np.random.SeedSequence(seed)
    child_sequences = base.spawn(len(n_values) * samples)
    seq_iter = iter(child_sequences)
    generators = generators_in_words(WORD_FAMILIES)
    for n in n_values:
        for sample in range(samples):
            rng = np.random.default_rng(next(seq_iter))
            perms = random_generator_perms(n, rng, generators=generators)
            for family in WORD_FAMILIES:
                fixed_common = count_common_fixed(family.words, perms, n)
                normalized = fixed_common / (n ** (-family.scale_power)) if family.scale_power > 0 else float(fixed_common)
                rows.append(
                    {
                        "n": n,
                        "sample": sample,
                        "family": family.family,
                        "word_count": len(family.words),
                        "words": " ".join(family.words),
                        "fixed_common": fixed_common,
                        "normalized_common": normalized,
                        "seed": seed,
                    }
                )
    return rows


def write_csv(rows: list[dict[str, object]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ["n", "sample", "family", "word_count", "words", "fixed_common", "normalized_common", "seed"]
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def summarize(rows: list[dict[str, str]]) -> list[dict[str, float | str | int]]:
    grouped: dict[tuple[str, int], list[float]] = defaultdict(list)
    grouped_norm: dict[tuple[str, int], list[float]] = defaultdict(list)
    for row in rows:
        key = (row["family"], int(row["n"]))
        grouped[key].append(float(row["fixed_common"]))
        grouped_norm[key].append(float(row["normalized_common"]))
    out: list[dict[str, float | str | int]] = []
    for (family, n), vals in sorted(grouped.items(), key=lambda x: (x[0][0], x[0][1])):
        arr = np.asarray(vals, dtype=float)
        narr = np.asarray(grouped_norm[(family, n)], dtype=float)
        out.append(
            {
                "family": family,
                "n": n,
                "mean": float(arr.mean()),
                "variance": float(arr.var(ddof=1)) if len(arr) > 1 else 0.0,
                "q50": float(np.quantile(arr, 0.50)),
                "q90": float(np.quantile(arr, 0.90)),
                "q99": float(np.quantile(arr, 0.99)),
                "normalized_mean": float(narr.mean()),
            }
        )
    return out


def write_summary_csv(summary: list[dict[str, float | str | int]], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ["family", "n", "mean", "variance", "q50", "q90", "q99", "normalized_mean"]
    with out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary)


def plot_scaling(summary: list[dict[str, float | str | int]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    selected = [
        "cyclic_pair_a_a2",
        "rank_two_pair_a_b",
        "cyclic_four",
        "independent_four",
        "cyclic_eight",
        "independent_eight",
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    for family in selected:
        xs = [int(r["n"]) for r in summary if r["family"] == family]
        ys = [float(r["mean"]) for r in summary if r["family"] == family]
        if xs:
            ax.plot(xs, ys, marker="o", label=family)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("cover degree n")
    ax.set_ylabel("mean common fixed-point count")
    ax.set_title("Common fixed-point scaling by word family")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_tails(rows: list[dict[str, str]], out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    selected = ["cyclic_pair_a_a2", "rank_two_pair_a_b", "cyclic_four", "independent_four", "independent_eight"]
    fig, ax = plt.subplots(figsize=(8, 5))
    for family in selected:
        vals = sorted(float(r["normalized_common"]) for r in rows if r["family"] == family)
        if not vals:
            continue
        surv_x = []
        surv_y = []
        total = len(vals)
        for idx, val in enumerate(vals):
            surv_x.append(max(val, 1e-12))
            surv_y.append((total - idx) / total)
        ax.step(surv_x, surv_y, where="post", label=family)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("normalized common fixed-point count")
    ax.set_ylabel("empirical P(X >= x)")
    ax.set_title("Empirical normalized tails")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def parse_n_values(raw: str) -> list[int]:
    values = [int(x.strip()) for x in raw.split(",") if x.strip()]
    if not values or any(v <= 0 for v in values):
        raise ValueError("--n-values must contain positive integers")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-values", default="50,100,200", help="comma-separated cover degrees")
    parser.add_argument("--samples", type=int, default=100, help="Monte Carlo samples per n")
    parser.add_argument("--seed", type=int, default=20260515, help="base RNG seed")
    parser.add_argument("--max-word-len", type=int, default=8, help="reject configured words longer than this after reduction")
    parser.add_argument("--out-csv", type=Path, default=ROOT / "data/polynomial_method/common_fixed_point_probe.csv")
    parser.add_argument("--summary-csv", type=Path, default=ROOT / "data/polynomial_method/common_fixed_point_summary.csv")
    parser.add_argument("--scaling-png", type=Path, default=ROOT / "reports/figures/m3_common_fixed_point_scaling.png")
    parser.add_argument("--tails-png", type=Path, default=ROOT / "reports/figures/m3_common_fixed_point_tails.png")
    parser.add_argument("--plot-only", action="store_true", help="read --out-csv and regenerate summaries/figures")
    args = parser.parse_args()

    too_long = [(f.family, w) for f in WORD_FAMILIES for w in f.words if len(reduce_word(w)) > args.max_word_len]
    if too_long:
        raise ValueError(f"configured word exceeds --max-word-len: {too_long[:3]}")

    if args.plot_only:
        raw_rows = read_csv(args.out_csv)
    else:
        rows = family_rows(parse_n_values(args.n_values), args.samples, args.seed)
        write_csv(rows, args.out_csv)
        raw_rows = [{k: str(v) for k, v in row.items()} for row in rows]

    summary = summarize(raw_rows)
    write_summary_csv(summary, args.summary_csv)
    plot_scaling(summary, args.scaling_png)
    plot_tails(raw_rows, args.tails_png)

    print(f"wrote {args.out_csv}")
    print(f"wrote {args.summary_csv}")
    print(f"wrote {args.scaling_png}")
    print(f"wrote {args.tails_png}")


if __name__ == "__main__":
    main()
