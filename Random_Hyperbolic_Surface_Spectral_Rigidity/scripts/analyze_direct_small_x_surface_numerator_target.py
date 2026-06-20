# created: 2026-05-17T00:14:00Z
# cycle: 47
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M36-direct-small-x-surface-numerator-target
"""Exponent ledger for the direct small-x Corollary 3.4 target.

This script does not simulate Kim--Tao surface quotient families.  It records
the exact exponent bookkeeping for replacing the Markov interpolation bound on
the paper-defined ratio p(1/n)/Q_id(1/n), including the repaired Lambda0^20
energy factor.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/extension_candidates"
FIGS = ROOT / "reports/figures"

BUDGET_CSV = DATA / "m36_direct_small_x_budget.csv"
DENOM_CSV = DATA / "m36_denominator_obstruction_grid.csv"
CLASS_CSV = DATA / "m36_mechanism_classification.csv"
IMPLICATION_CSV = DATA / "m36_direct_vs_cv_implication_table.csv"

BUDGET_FIG = FIGS / "m36_direct_small_x_budget_map.png"
DENOM_FIG = FIGS / "m36_denominator_obstruction_map.png"
GRAPH_FIG = FIGS / "m36_direct_vs_cv_dependency_graph.png"

KAPPA_VALUES = [3.0, 5.0, 8.0]
ETA_VALUES = [0.02, 0.05, 0.08, 0.12, 0.18]
A_OFFSETS = [0.0, 1.0, 2.0, 3.0]
SIGMA_VALUES = [0.0, 0.15, 0.35, 0.6]
DENOM_LOSSES = [0.0, 0.25, 0.5, 1.0, 2.0]
LAMBDA0_POWER = 20
ALPHA_W = 0.006


@dataclass(frozen=True)
class Model:
    name: str
    family: str
    classification: str
    a_offset: float
    sigma: float
    denominator_loss_d: float
    lambda0_power: int
    proof_status: str
    needs_surface_input: bool
    only_toy_evidence: bool

    def effective_a(self, kappa: float) -> float:
        return 2.0 * kappa - self.a_offset

    def beta(self, eta: float) -> float:
        return self.a_offset * eta + self.sigma - self.denominator_loss_d


MODELS = [
    Model(
        "markov_baseline",
        "markov",
        "paper_proved_baseline",
        0.0,
        0.0,
        0.0,
        LAMBDA0_POWER,
        "theorem_level_existing",
        False,
        False,
    ),
    Model(
        "direct_small_x_pointwise",
        "direct_small_x",
        "conditional_surface_theorem_target",
        1.0,
        0.35,
        0.0,
        LAMBDA0_POWER,
        "conditional",
        True,
        False,
    ),
    Model(
        "direct_small_x_strong",
        "direct_small_x",
        "conditional_surface_theorem_target",
        2.0,
        0.6,
        0.0,
        LAMBDA0_POWER,
        "conditional",
        True,
        False,
    ),
    Model(
        "direct_small_x_with_denominator_loss",
        "direct_small_x",
        "conditional_but_denominator_sensitive",
        2.0,
        0.6,
        0.5,
        LAMBDA0_POWER,
        "conditional",
        True,
        False,
    ),
    Model(
        "coefficient_variation_control",
        "coefficient_variation",
        "conditional_stronger_structured_target",
        2.0,
        0.0,
        0.0,
        LAMBDA0_POWER,
        "conditional",
        True,
        False,
    ),
    Model(
        "signed_cancellation_control",
        "signed_cancellation",
        "conditional_comparable_to_direct_input",
        1.5,
        0.35,
        0.0,
        LAMBDA0_POWER,
        "conditional",
        True,
        False,
    ),
    Model(
        "stronger_lemma33_input",
        "lemma33",
        "conditional_stronger_input",
        3.0,
        0.35,
        0.0,
        LAMBDA0_POWER,
        "conditional",
        True,
        False,
    ),
    Model(
        "schreier_toy_transfer",
        "toy_transfer",
        "blocked_toy_only_insufficient",
        2.0,
        0.35,
        0.0,
        LAMBDA0_POWER,
        "blocked",
        True,
        True,
    ),
]


def variance_exponent(kappa: float, eta: float, model: Model) -> float:
    """Exponent in n for n Lambda0^20 ||h||^2 q^A n^(-sigma+D)."""
    return 1.0 + model.effective_a(kappa) * eta - model.sigma + model.denominator_loss_d


def markov_exponent(kappa: float, eta: float) -> float:
    return 1.0 + 2.0 * kappa * eta


def local_window_required_beta(kappa: float, eta: float, d: float) -> float:
    return 2.0 * kappa * eta + 2.0 * d - 1.0


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"no rows for {path}")
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def build_budget_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for kappa in KAPPA_VALUES:
        for eta in ETA_VALUES:
            baseline = markov_exponent(kappa, eta)
            for model in MODELS:
                exponent = variance_exponent(kappa, eta, model)
                beta = model.beta(eta)
                rows.append(
                    {
                        "kappa": kappa,
                        "eta": eta,
                        "model": model.name,
                        "family": model.family,
                        "classification": model.classification,
                        "A": model.effective_a(kappa),
                        "sigma": model.sigma,
                        "denominator_loss_D": model.denominator_loss_d,
                        "Lambda0_power": model.lambda0_power,
                        "q_loss_exponent": model.effective_a(kappa) * eta,
                        "variance_exponent": exponent,
                        "markov_variance_exponent": baseline,
                        "saving_vs_markov": baseline - exponent,
                        "candidate_beta": beta,
                        "baseline_q_2kappa_reproduced": bool_text(model.name == "markov_baseline"),
                        "paper_proved_success": bool_text(model.name == "markov_baseline"),
                        "claims_proved_exponent_improvement": "False",
                    }
                )
    return rows


def build_denominator_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for kappa in [5.0]:
        for eta in ETA_VALUES:
            for a_offset in A_OFFSETS:
                for sigma in SIGMA_VALUES:
                    raw_beta = a_offset * eta + sigma
                    for d_loss in DENOM_LOSSES:
                        net_beta = raw_beta - d_loss
                        rows.append(
                            {
                                "kappa": kappa,
                                "eta": eta,
                                "A": 2.0 * kappa - a_offset,
                                "A_offset_from_markov": a_offset,
                                "sigma": sigma,
                                "denominator_loss_D": d_loss,
                                "raw_beta_before_denominator": raw_beta,
                                "net_beta_after_denominator": net_beta,
                                "saving_survives_denominator": bool_text(net_beta > 0.0),
                                "near_zero_denominator_obstruction": bool_text(d_loss > raw_beta),
                                "paper_denominator_safe_regime": "n >= q^kappa and Q_id(1/n) in [C^-1,C]",
                            }
                        )
    return rows


def build_classification_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for model in MODELS:
        rows.append(
            {
                "mechanism": model.name,
                "classification": model.classification,
                "proof_status": model.proof_status,
                "paper_proved_input": bool_text(model.name == "markov_baseline"),
                "requires_new_surface_group_input": bool_text(model.needs_surface_input),
                "uses_only_schreier_or_independent_permutation_evidence": bool_text(model.only_toy_evidence),
                "Lambda0_power": model.lambda0_power,
                "claims_proved_exponent_improvement": "False",
                "claims_local_statistics": "False",
                "claims_variance_law": "False",
                "claims_shrinking_window_theorem": "False",
            }
        )
    special_points = [
        ("x=0", "vacuous_without_neighborhood_control", "P(0)=0 does not control p(1/n)/Q_id(1/n)."),
        ("x=1/n", "actual_target_point", "Direct theorem must evaluate the ratio at the Lemma 3.3 sample point."),
        ("n=Cq^kappa", "range_boundary", "Compatible if kappa is chosen at least as large as the Lemma 3.3 constant exponent."),
        ("q->infinity", "growing_degree_and_family", "deg p=O(Lambda0^(-1/2)q) and quotient complexity grow."),
        ("fixed_Lambda0", "isolates_trace_q_loss", "Energy factor is inert and q-exponent savings are visible."),
        ("high_Lambda0", "retains_Lambda0_20_factor", "M36 keeps Lambda0^20 and proves no high-energy improvement."),
        ("Q_id(1/n)=0", "excluded_in_paper_range_but_obstructive_outside", "The ratio is meaningless at a zero."),
        ("Q_id(1/n) near-zero", "denominator_loss_model", "A loss D can erase direct numerator savings."),
    ]
    for point, classification, note in special_points:
        rows.append(
            {
                "mechanism": f"special_point:{point}",
                "classification": classification,
                "proof_status": "diagnostic",
                "paper_proved_input": bool_text(point in {"x=1/n", "n=Cq^kappa"}),
                "requires_new_surface_group_input": "False",
                "uses_only_schreier_or_independent_permutation_evidence": "False",
                "Lambda0_power": LAMBDA0_POWER,
                "claims_proved_exponent_improvement": "False",
                "claims_local_statistics": "False",
                "claims_variance_law": "False",
                "claims_shrinking_window_theorem": "False",
                "note": note,
            }
        )
    return rows


def build_implication_rows() -> list[dict[str, object]]:
    return [
        {
            "route": "direct_small_x_ratio_bound",
            "target_statement": "|p(1/n)/Q_id(1/n)| <= n Lambda0^20 ||htilde||^2 q^A n^(-sigma)",
            "strictly_weaker_than_coefficient_variation": "potentially_true",
            "reason": "It can use signed cancellation at the point x=1/n without bounding every coefficient.",
            "independent_route_status": "plausible_conditional",
        },
        {
            "route": "coefficient_variation_bound",
            "target_statement": "weighted coefficient variation of p/Q_id is <= n Lambda0^20 q^A n^(-sigma)",
            "strictly_weaker_than_coefficient_variation": "not_applicable",
            "reason": "This is the structured stronger route; it implies pointwise small-x control in the needed interval.",
            "independent_route_status": "stronger_structured_target",
        },
        {
            "route": "direct_bound_from_fixed_pair_Q_estimates_only",
            "target_statement": "sum fixed-pair bounds without aggregate signed control",
            "strictly_weaker_than_coefficient_variation": "false",
            "reason": "Without aggregate cancellation or total variation control, fixed-pair estimates reproduce only Markov-scale or worse bounds.",
            "independent_route_status": "blocked",
        },
        {
            "route": "direct_bound_with_uncontrolled_denominator",
            "target_statement": "numerator-only estimate for p(1/n)",
            "strictly_weaker_than_coefficient_variation": "false",
            "reason": "If Q_id(1/n) is zero or near-zero, numerator savings do not survive normalization.",
            "independent_route_status": "blocked_outside_paper_denominator_range",
        },
        {
            "route": "schreier_or_independent_permutation_transfer",
            "target_statement": "reuse M30-M33 trace variance mechanisms",
            "strictly_weaker_than_coefficient_variation": "false",
            "reason": "The surface numerator also requires the surface relation, MPvH/Witten-zeta normalization, Nau boundedness, Q_id, and Selberg weights.",
            "independent_route_status": "not_a_surface_proof",
        },
    ]


def plot_budget(rows: list[dict[str, object]]) -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    subset = [r for r in rows if float(r["kappa"]) == 5.0 and r["family"] in {"markov", "direct_small_x", "coefficient_variation"}]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for model in sorted({r["model"] for r in subset}):
        mr = [r for r in subset if r["model"] == model]
        mr.sort(key=lambda r: float(r["eta"]))
        ax.plot([float(r["eta"]) for r in mr], [float(r["saving_vs_markov"]) for r in mr], marker="o", label=model)
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_xlabel("eta where q=n^eta")
    ax.set_ylabel("n-exponent saving vs Markov baseline")
    ax.set_title("Direct small-x exponent-saving regions, kappa=5")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(BUDGET_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {BUDGET_FIG.relative_to(ROOT)}")


def plot_denominator(rows: list[dict[str, object]]) -> None:
    subset = [r for r in rows if float(r["eta"]) == 0.08 and abs(float(r["A_offset_from_markov"]) - 2.0) < 1e-12]
    xs = sorted({float(r["sigma"]) for r in subset})
    ys = sorted({float(r["denominator_loss_D"]) for r in subset})
    grid = []
    for y in ys:
        row = []
        for x in xs:
            match = next(r for r in subset if float(r["sigma"]) == x and float(r["denominator_loss_D"]) == y)
            row.append(float(match["net_beta_after_denominator"]))
        grid.append(row)
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    im = ax.imshow(grid, origin="lower", aspect="auto", extent=[min(xs), max(xs), min(ys), max(ys)], cmap="RdYlGn")
    ax.contour(xs, ys, grid, levels=[0.0], colors="black", linewidths=1.2)
    ax.set_xlabel("direct sigma")
    ax.set_ylabel("denominator loss D")
    ax.set_title("Denominator loss erases direct-evaluation savings")
    fig.colorbar(im, ax=ax, label="net beta after denominator")
    fig.tight_layout()
    fig.savefig(DENOM_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {DENOM_FIG.relative_to(ROOT)}")


def plot_graph() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.axis("off")
    nodes = {
        "Lemma 3.3\nQ/Q_id": (0.08, 0.68),
        "Corollary 3.4\np(1/n)/Q_id(1/n)": (0.35, 0.68),
        "Markov on x^2 p\npaper baseline": (0.67, 0.86),
        "direct small-x\nratio theorem": (0.67, 0.62),
        "coefficient variation\nstructured theorem": (0.67, 0.38),
        "stronger Lemma 3.3\ninput": (0.35, 0.25),
        "Proposition 3.1\nLambda0^20 q^(2kappa)\nor improved q^A n^-sigma": (0.9, 0.66),
        "Schreier toy transfer\nblocked": (0.12, 0.15),
    }
    edges = [
        ("Lemma 3.3\nQ/Q_id", "Corollary 3.4\np(1/n)/Q_id(1/n)"),
        ("Corollary 3.4\np(1/n)/Q_id(1/n)", "Markov on x^2 p\npaper baseline"),
        ("Corollary 3.4\np(1/n)/Q_id(1/n)", "direct small-x\nratio theorem"),
        ("Corollary 3.4\np(1/n)/Q_id(1/n)", "coefficient variation\nstructured theorem"),
        ("stronger Lemma 3.3\ninput", "Corollary 3.4\np(1/n)/Q_id(1/n)"),
        ("Markov on x^2 p\npaper baseline", "Proposition 3.1\nLambda0^20 q^(2kappa)\nor improved q^A n^-sigma"),
        ("direct small-x\nratio theorem", "Proposition 3.1\nLambda0^20 q^(2kappa)\nor improved q^A n^-sigma"),
        ("coefficient variation\nstructured theorem", "Proposition 3.1\nLambda0^20 q^(2kappa)\nor improved q^A n^-sigma"),
    ]
    for start, end in edges:
        x0, y0 = nodes[start]
        x1, y1 = nodes[end]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops={"arrowstyle": "->", "lw": 1.3, "color": "#555"})
    for label, (x, y) in nodes.items():
        face = "#e8f1ff"
        if "blocked" in label:
            face = "#f4dddd"
        if "paper baseline" in label:
            face = "#e4f3e2"
        ax.text(x, y, label, ha="center", va="center", fontsize=9, bbox={"boxstyle": "round,pad=0.35", "facecolor": face, "edgecolor": "#444"})
    ax.text(0.12, 0.06, "No transfer arrow: missing surface relation, Q_id, MPvH/Nau inputs, and Selberg weights.", ha="left", fontsize=8)
    fig.tight_layout()
    fig.savefig(GRAPH_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {GRAPH_FIG.relative_to(ROOT)}")


def main() -> None:
    budget = build_budget_rows()
    denom = build_denominator_rows()
    classification = build_classification_rows()
    implication = build_implication_rows()
    write_csv(BUDGET_CSV, budget)
    write_csv(DENOM_CSV, denom)
    write_csv(CLASS_CSV, classification)
    write_csv(IMPLICATION_CSV, implication)
    plot_budget(budget)
    plot_denominator(denom)
    plot_graph()
    print("decision=direct_small_x_is_distinct_conditional_target_but_requires_new_surface_ratio_estimate")


if __name__ == "__main__":
    main()
