# created: 2026-05-16T21:42:00Z
# cycle: 42
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M31-schreier-variance-mechanism-theoremization
"""Analyze paired-word covariance templates for the Schreier benchmark.

The script keeps the scope fixed-k and finite: enumerate length k words over
{a,A,b,B}, aggregate by freely reduced word, classify reduced word pairs, and
record M4-style labelled-template constraint exponents for k=2,4,6.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "extension_candidates"
FIGURE_DIR = ROOT / "reports" / "figures"

PAIR_CLASS_PATH = DATA_DIR / "m31_pair_template_classes.csv"
COVARIANCE_ORDER_PATH = DATA_DIR / "m31_pair_covariance_orders.csv"
SUMMARY_PATH = DATA_DIR / "m31_variance_order_summary.csv"
CLASSIFICATION_PATH = DATA_DIR / "m31_variance_mechanism_classification.csv"

PAIR_CLASS_FIGURE = FIGURE_DIR / "m31_pair_class_covariance_orders.png"
MECHANISM_FIGURE = FIGURE_DIR / "m31_variance_order_mechanism_map.png"
SLOPE_FIGURE = FIGURE_DIR / "m31_m30_slope_reinterpretation.png"

M30_VARIANCE_PATH = DATA_DIR / "m30_schreier_variance_scaling.csv"

LETTERS = ("a", "A", "b", "B")
INVERSE = {"a": "A", "A": "a", "b": "B", "B": "b"}
FORWARD_LABEL = {"a": "a", "A": "a", "b": "b", "B": "b"}
DECISION = "advance_schreier_variance_theorem"
K_VALUES = (2, 4, 6)


@dataclass(frozen=True)
class TemplateOrder:
    vertices: int
    constraints: int
    exponent: int
    partial_injection: bool


@dataclass(frozen=True)
class WordFeatures:
    word: tuple[str, ...]
    inverse: tuple[str, ...]
    rotations: frozenset[tuple[str, ...]]
    inverse_rotations: frozenset[tuple[str, ...]]
    primitive_root: tuple[str, ...]
    primitive_power: int
    generator_set: frozenset[str]


def reduce_word(word: tuple[str, ...]) -> tuple[str, ...]:
    stack: list[str] = []
    for letter in word:
        if stack and INVERSE[letter] == stack[-1]:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def inverse_word(word: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(INVERSE[letter] for letter in reversed(word))


def cyclic_rotations(word: tuple[str, ...]) -> set[tuple[str, ...]]:
    if not word:
        return {()}
    return {word[i:] + word[:i] for i in range(len(word))}


def primitive_root(word: tuple[str, ...]) -> tuple[tuple[str, ...], int]:
    if not word:
        return (), 0
    length = len(word)
    for period in range(1, length + 1):
        if length % period == 0:
            root = word[:period]
            if root * (length // period) == word:
                return root, length // period
    return word, 1


@lru_cache(maxsize=None)
def word_features(word: tuple[str, ...]) -> WordFeatures:
    root, power = primitive_root(word)
    inv = inverse_word(word)
    return WordFeatures(
        word=word,
        inverse=inv,
        rotations=frozenset(cyclic_rotations(word)),
        inverse_rotations=frozenset(cyclic_rotations(inv)),
        primitive_root=root,
        primitive_power=power,
        generator_set=frozenset(FORWARD_LABEL[l] for l in word),
    )


@lru_cache(maxsize=None)
def reduced_word_counts(k: int) -> Counter[tuple[str, ...]]:
    counts: Counter[tuple[str, ...]] = Counter()
    for index in range(4**k):
        value = index
        word: list[str] = []
        for _ in range(k):
            word.append(LETTERS[value & 3])
            value >>= 2
        counts[reduce_word(tuple(word))] += 1
    return counts


def word_edges(word: tuple[str, ...], prefix: str) -> tuple[list[str], list[tuple[str, str, str]]]:
    vertices = [f"{prefix}0"]
    edges: list[tuple[str, str, str]] = []
    current = f"{prefix}0"
    for idx, letter in enumerate(word, start=1):
        nxt = f"{prefix}0" if idx == len(word) else f"{prefix}{idx}"
        edges.append((current, nxt, letter))
        if nxt not in vertices:
            vertices.append(nxt)
        current = nxt
    return vertices, edges


def normalize_edge(src: str, dst: str, label: str) -> tuple[str, str, str]:
    if label.isupper():
        return dst, src, label.lower()
    return src, dst, label.lower()


@lru_cache(maxsize=None)
def template_order(w1: tuple[str, ...], w2: tuple[str, ...], same_basepoint: bool) -> TemplateOrder:
    vertices1, edges1 = word_edges(w1, "x")
    vertices2, edges2 = word_edges(w2, "y")
    alias: dict[str, str] = {}
    if same_basepoint:
        alias["y0"] = "x0"

    def canon(vertex: str) -> str:
        return alias.get(vertex, vertex)

    vertices = {canon(v) for v in vertices1 + vertices2}
    normalized = {normalize_edge(canon(src), canon(dst), label) for src, dst, label in edges1 + edges2}
    by_label: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for src, dst, label in normalized:
        by_label[label].add((src, dst))

    partial = True
    for pairs in by_label.values():
        sources: dict[str, str] = {}
        targets: dict[str, str] = {}
        for src, dst in pairs:
            if src in sources and sources[src] != dst:
                partial = False
            if dst in targets and targets[dst] != src:
                partial = False
            sources[src] = dst
            targets[dst] = src

    constraint_count = sum(len(pairs) for pairs in by_label.values())
    return TemplateOrder(len(vertices), constraint_count, len(vertices) - constraint_count, partial)


def pair_class(w1: tuple[str, ...], w2: tuple[str, ...]) -> str:
    if not w1 and not w2:
        return "identity_identity"
    if not w1 or not w2:
        return "identity_nontrivial"
    if w1 == w2:
        return "same_reduced_word"
    if w1 == inverse_word(w2):
        return "inverse_reduced_word"
    rotations2 = cyclic_rotations(w2)
    inv_rotations2 = cyclic_rotations(inverse_word(w2))
    if w1 in rotations2 or w1 in inv_rotations2:
        return "cyclic_or_inverse_conjugate"
    root1, power1 = primitive_root(w1)
    root2, power2 = primitive_root(w2)
    root2_inv = inverse_word(root2)
    if power1 > 1 or power2 > 1:
        if root1 == root2 or root1 == root2_inv:
            return "shared_power_relation"
    if set(FORWARD_LABEL[l] for l in w1) & set(FORWARD_LABEL[l] for l in w2):
        return "generic_shared_generator"
    return "generic_disjoint_generators"


def pair_class_from_features(f1: WordFeatures, f2: WordFeatures) -> str:
    w1 = f1.word
    w2 = f2.word
    if not w1 and not w2:
        return "identity_identity"
    if not w1 or not w2:
        return "identity_nontrivial"
    if w1 == w2:
        return "same_reduced_word"
    if w1 == f2.inverse:
        return "inverse_reduced_word"
    if w1 in f2.rotations or w1 in f2.inverse_rotations:
        return "cyclic_or_inverse_conjugate"
    if f1.primitive_power > 1 or f2.primitive_power > 1:
        if f1.primitive_root == f2.primitive_root or f1.primitive_root == inverse_word(f2.primitive_root):
            return "shared_power_relation"
    if f1.generator_set & f2.generator_set:
        return "generic_shared_generator"
    return "generic_disjoint_generators"


def covariance_exponent_bound(w1: tuple[str, ...], w2: tuple[str, ...]) -> int:
    if not w1 or not w2:
        return -2
    distinct = template_order(w1, w2, same_basepoint=False)
    same = template_order(w1, w2, same_basepoint=True)
    return max(distinct.exponent, same.exponent)


def order_label(exponent: int) -> str:
    if exponent > 0:
        return f"O(n^{exponent})"
    if exponent == 0:
        return "O(1)"
    return f"O(n^{exponent})"


@lru_cache(maxsize=None)
def build_pair_rows(k_values: tuple[int, ...] = K_VALUES) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    class_acc: dict[tuple[int, str], dict[str, object]] = {}

    for k in k_values:
        counts = reduced_word_counts(k)
        reduced_words = sorted(counts)
        features = {word: word_features(word) for word in reduced_words}
        total_pairs = 0
        for w1 in reduced_words:
            for w2 in reduced_words:
                multiplicity = counts[w1] * counts[w2]
                total_pairs += multiplicity
                cls = pair_class_from_features(features[w1], features[w2])
                max_exp = covariance_exponent_bound(w1, w2)
                positive = max_exp > 0
                key = (k, cls)
                if key not in class_acc:
                    class_acc[key] = {
                        "k": k,
                        "pair_class": cls,
                        "reduced_pair_types": 0,
                        "word_pair_multiplicity": 0,
                        "max_template_exponent": -999,
                        "max_distinct_basepoint_exponent": -999,
                        "max_same_basepoint_exponent": -999,
                        "distinct_basepoint_partial_injection_failures": 0,
                        "same_basepoint_partial_injection_failures": 0,
                        "positive_power_obstruction": False,
                        "representative_w1": "".join(w1) or "id",
                        "representative_w2": "".join(w2) or "id",
                    }
                acc = class_acc[key]
                distinct = template_order(w1, w2, same_basepoint=False)
                same = template_order(w1, w2, same_basepoint=True)
                acc["reduced_pair_types"] = int(acc["reduced_pair_types"]) + 1
                acc["word_pair_multiplicity"] = int(acc["word_pair_multiplicity"]) + multiplicity
                if max_exp > int(acc["max_template_exponent"]):
                    acc["max_template_exponent"] = max_exp
                    acc["representative_w1"] = "".join(w1) or "id"
                    acc["representative_w2"] = "".join(w2) or "id"
                acc["max_distinct_basepoint_exponent"] = max(
                    int(acc["max_distinct_basepoint_exponent"]), distinct.exponent
                )
                acc["max_same_basepoint_exponent"] = max(
                    int(acc["max_same_basepoint_exponent"]), same.exponent
                )
                if not distinct.partial_injection:
                    acc["distinct_basepoint_partial_injection_failures"] = int(
                        acc["distinct_basepoint_partial_injection_failures"]
                    ) + 1
                if not same.partial_injection:
                    acc["same_basepoint_partial_injection_failures"] = int(
                        acc["same_basepoint_partial_injection_failures"]
                    ) + 1
                acc["positive_power_obstruction"] = bool(acc["positive_power_obstruction"] or positive)

        assert total_pairs == 16**k

    class_rows: list[dict[str, object]] = []
    order_rows: list[dict[str, object]] = []
    for (_, _), acc in sorted(class_acc.items()):
        max_exp = int(acc["max_template_exponent"])
        acc["covariance_order_before_normalization"] = order_label(max_exp)
        acc["normalized_variance_order_after_n_minus_2"] = order_label(max_exp - 2)
        class_rows.append(acc)
        w1 = tuple(str(acc["representative_w1"]).replace("id", ""))
        w2 = tuple(str(acc["representative_w2"]).replace("id", ""))
        distinct = template_order(w1, w2, same_basepoint=False)
        same = template_order(w1, w2, same_basepoint=True)
        order_rows.append(
            {
                "k": acc["k"],
                "pair_class": acc["pair_class"],
                "representative_w1": acc["representative_w1"],
                "representative_w2": acc["representative_w2"],
                "reduced_pair_types": acc["reduced_pair_types"],
                "word_pair_multiplicity": acc["word_pair_multiplicity"],
                "max_distinct_basepoint_exponent_all_pairs": acc["max_distinct_basepoint_exponent"],
                "max_same_basepoint_exponent_all_pairs": acc["max_same_basepoint_exponent"],
                "distinct_basepoint_partial_injection_failures": acc["distinct_basepoint_partial_injection_failures"],
                "same_basepoint_partial_injection_failures": acc["same_basepoint_partial_injection_failures"],
                "distinct_basepoint_vertices": distinct.vertices,
                "distinct_basepoint_constraints": distinct.constraints,
                "distinct_basepoint_exponent": distinct.exponent,
                "distinct_basepoint_partial_injection": distinct.partial_injection,
                "same_basepoint_vertices": same.vertices,
                "same_basepoint_constraints": same.constraints,
                "same_basepoint_exponent": same.exponent,
                "same_basepoint_partial_injection": same.partial_injection,
                "covariance_order_before_normalization": order_label(max_exp),
                "normalized_variance_order_after_n_minus_2": order_label(max_exp - 2),
                "positive_power_obstruction": acc["positive_power_obstruction"],
            }
        )

    summary_rows: list[dict[str, object]] = []
    for k in k_values:
        class_subset = [row for row in class_rows if int(row["k"]) == k]
        max_exp = max(int(row["max_template_exponent"]) for row in class_subset)
        obstructions = [row["pair_class"] for row in class_subset if row["positive_power_obstruction"]]
        summary_rows.append(
            {
                "k": k,
                "length_k_words": 4**k,
                "word_pairs": 16**k,
                "reduced_word_types": len(reduced_word_counts(k)),
                "pair_classes": len(class_subset),
                "max_covariance_order_before_normalization": order_label(max_exp),
                "normalized_variance_order_after_n_minus_2": order_label(max_exp - 2),
                "positive_power_obstruction_classes": ";".join(obstructions),
                "supports_ok_n_minus_2_template": not obstructions and max_exp <= 0,
            }
        )
    return class_rows, order_rows, summary_rows


def load_m30_variance_rows() -> list[dict[str, object]]:
    if not M30_VARIANCE_PATH.exists():
        return []
    with M30_VARIANCE_PATH.open() as f:
        return list(csv.DictReader(f))


def slope_model_rows() -> list[dict[str, object]]:
    rows = load_m30_variance_rows()
    out: list[dict[str, object]] = []
    for k in (2, 4, 6):
        points = [
            (float(row["n"]), float(row["variance_centered_trace"]))
            for row in rows
            if int(row["k"]) == k and float(row["variance_centered_trace"]) > 0
        ]
        points.sort()
        if len(points) < 2:
            continue
        n = np.asarray([p[0] for p in points], dtype=float)
        y = np.asarray([p[1] for p in points], dtype=float)
        fit_rows = []
        for model, design in (
            ("c*n^-1", np.column_stack([n ** -1])),
            ("c*n^-2", np.column_stack([n ** -2])),
            ("a*n^-1+b*n^-2", np.column_stack([n ** -1, n ** -2])),
        ):
            coef, *_ = np.linalg.lstsq(design, y, rcond=None)
            pred = design @ coef
            sse = float(np.sum((y - pred) ** 2))
            fit_rows.append((model, sse, coef, pred))
        best = min(fit_rows, key=lambda item: item[1])[0]
        slope = float(np.polyfit(np.log(n), np.log(y), 1)[0])
        for model, sse, coef, pred in fit_rows:
            out.append(
                {
                    "k": k,
                    "model": model,
                    "sse": sse,
                    "best_model": model == best,
                    "fitted_slope": slope,
                    "coefficients": " ".join(f"{value:.8g}" for value in coef),
                    "n_values": " ".join(str(int(value)) for value in n),
                    "observed_variances": " ".join(f"{value:.8g}" for value in y),
                    "predicted_variances": " ".join(f"{value:.8g}" for value in pred),
                }
            )
    return out


def classification_rows(summary_rows: list[dict[str, object]], slope_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    all_supported = all(row["supports_ok_n_minus_2_template"] for row in summary_rows)
    best_models = sorted({row["model"] for row in slope_rows if row["best_model"]})
    if all_supported:
        decision = DECISION
        rationale = "All checked k=2,4,6 pair classes have M4-compatible covariance templates of order O(1) before the outer n^-2 normalization."
    else:
        decision = "preserve_variance_as_conjectural_benchmark"
        rationale = "At least one checked pair class has a positive-power covariance-order obstruction in the template table."
    return [
        {
            "item": "paired_word_expansion",
            "classification": "derived_finite_pair_expansion",
            "claim_status": "theorem_template",
            "decision": "",
            "rationale": "Variance expands as n^-2 times a finite sum of fixed-word covariances over length-k word pairs.",
        },
        {
            "item": "small_k_pair_templates",
            "classification": "m4_style_order_certification",
            "claim_status": "checked_k_2_4_6",
            "decision": "",
            "rationale": "Reduced pair classes are aggregated by multiplicity and checked through same/distinct-basepoint labelled constraint exponents.",
        },
        {
            "item": "m30_slope_reinterpretation",
            "classification": "finite_size_crossover_consistent_with_n_minus_2",
            "claim_status": "empirical_reinterpretation",
            "decision": "",
            "rationale": f"M30 slopes are compared to n^-1, n^-2, and mixed fits; best least-squares models on the small grid are {', '.join(best_models) or 'unavailable'}.",
        },
        {
            "item": "hyperbolic_transfer",
            "classification": "hyperbolic_transfer_not_claimed",
            "claim_status": "scope_firewall",
            "decision": "",
            "rationale": "The argument is for the free two-permutation Schreier benchmark and does not supply a surface-group quotient-family theorem.",
        },
        {
            "item": "branch_decision",
            "classification": "schreier_variance_mechanism_package",
            "claim_status": "decision",
            "decision": decision,
            "rationale": rationale,
        },
    ]


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_pair_classes(class_rows: list[dict[str, object]], out: Path) -> None:
    order = [
        "identity_identity",
        "identity_nontrivial",
        "same_reduced_word",
        "inverse_reduced_word",
        "cyclic_or_inverse_conjugate",
        "shared_power_relation",
        "generic_shared_generator",
        "generic_disjoint_generators",
    ]
    xs = np.arange(len(order))
    width = 0.24
    fig, ax = plt.subplots(figsize=(11, 5.4))
    colors = {2: "#2f6f9f", 4: "#b35a2a", 6: "#4c8a3f"}
    for offset, k in enumerate(K_VALUES):
        values = []
        for cls in order:
            found = [row for row in class_rows if int(row["k"]) == k and row["pair_class"] == cls]
            values.append(int(found[0]["max_template_exponent"]) if found else np.nan)
        ax.bar(xs + (offset - 1) * width, values, width=width, label=f"k={k}", color=colors[k])
    ax.axhline(0, color="#222222", linewidth=1.0)
    ax.axhline(-2, color="#666666", linewidth=0.8, linestyle="--")
    ax.set_xticks(xs)
    ax.set_xticklabels(order, rotation=35, ha="right")
    ax.set_ylabel("max template exponent before outer n^-2")
    ax.set_title("M31 pair classes show no positive covariance-order exponent for k=2,4,6")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_mechanism_map(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")
    boxes = [
        ("Trace word expansion", "Tr(A^k)=sum_w Fix(w)", 0.08, 0.62),
        ("Paired variance", "n^-2 sum Cov(Fix(w1),Fix(w2))", 0.36, 0.62),
        ("Basepoint split", "x=y and x!=y templates", 0.64, 0.62),
        ("M4 constraint count", "(n)_V / product (n)_C", 0.22, 0.24),
        ("Order certificate", "max V-C <= 0 for k=2,4,6", 0.52, 0.24),
        ("Conclusion", "normalized variance O(n^-2)", 0.78, 0.24),
    ]
    for title, body, x, y in boxes:
        ax.add_patch(plt.Rectangle((x - 0.105, y - 0.09), 0.21, 0.18, facecolor="#f6f3ea", edgecolor="#333333", linewidth=1.1))
        ax.text(x, y + 0.035, title, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.text(x, y - 0.03, body, ha="center", va="center", fontsize=8.5)
    arrows = [((0.185, 0.62), (0.255, 0.62)), ((0.465, 0.62), (0.535, 0.62)), ((0.64, 0.53), (0.52, 0.33)), ((0.325, 0.24), (0.415, 0.24)), ((0.625, 0.24), (0.675, 0.24))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.2, "color": "#333333"})
    ax.text(0.5, 0.92, "Schreier variance mechanism: finite word-pair covariance reduces to labelled templates", ha="center", fontsize=12, fontweight="bold")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_slope_reinterpretation(slope_rows: list[dict[str, object]], out: Path) -> None:
    raw_rows = load_m30_variance_rows()
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharey=False)
    for ax, k in zip(axes, (2, 4, 6)):
        points = [
            (float(row["n"]), float(row["variance_centered_trace"]))
            for row in raw_rows
            if int(row["k"]) == k and float(row["variance_centered_trace"]) > 0
        ]
        points.sort()
        n = np.asarray([p[0] for p in points], dtype=float)
        y = np.asarray([p[1] for p in points], dtype=float)
        ax.loglog(n, y, "o", color="#222222", label="M30 variance")
        ngrid = np.linspace(min(n), max(n), 100)
        for model, color in (("c*n^-1", "#9b3a32"), ("c*n^-2", "#2f6f9f"), ("a*n^-1+b*n^-2", "#4c8a3f")):
            match = [row for row in slope_rows if int(row["k"]) == k and row["model"] == model]
            if not match:
                continue
            coeff = [float(x) for x in str(match[0]["coefficients"]).split()]
            if model == "c*n^-1":
                pred = coeff[0] * ngrid**-1
            elif model == "c*n^-2":
                pred = coeff[0] * ngrid**-2
            else:
                pred = coeff[0] * ngrid**-1 + coeff[1] * ngrid**-2
                pred = np.maximum(pred, min(y) * 0.1)
            ax.loglog(ngrid, pred, color=color, linewidth=1.2, label=model)
        slope = [row for row in slope_rows if int(row["k"]) == k]
        slope_text = float(slope[0]["fitted_slope"]) if slope else float("nan")
        ax.set_title(f"k={k}, fitted slope {slope_text:.3f}")
        ax.set_xlabel("n")
        ax.set_ylabel("variance")
        ax.grid(alpha=0.25, which="both")
    axes[0].legend(fontsize=8)
    fig.suptitle("M30 finite-grid slopes are compatible with an n^-2 mechanism plus finite-size terms", fontsize=12, fontweight="bold")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()

    class_rows, order_rows, summary_rows = build_pair_rows()
    slope_rows = slope_model_rows()
    classification = classification_rows(summary_rows, slope_rows)

    write_csv(class_rows, PAIR_CLASS_PATH)
    write_csv(order_rows, COVARIANCE_ORDER_PATH)
    write_csv(summary_rows, SUMMARY_PATH)
    write_csv(classification, CLASSIFICATION_PATH)

    plot_pair_classes(class_rows, PAIR_CLASS_FIGURE)
    plot_mechanism_map(MECHANISM_FIGURE)
    plot_slope_reinterpretation(slope_rows, SLOPE_FIGURE)

    for path, rows in (
        (PAIR_CLASS_PATH, class_rows),
        (COVARIANCE_ORDER_PATH, order_rows),
        (SUMMARY_PATH, summary_rows),
        (CLASSIFICATION_PATH, classification),
    ):
        print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")
    for path in (PAIR_CLASS_FIGURE, MECHANISM_FIGURE, SLOPE_FIGURE):
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"decision={classification[-1]['decision']}")


if __name__ == "__main__":
    main()
