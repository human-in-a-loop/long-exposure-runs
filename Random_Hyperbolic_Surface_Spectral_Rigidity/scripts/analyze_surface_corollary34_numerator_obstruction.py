# created: 2026-05-16T23:59:45Z
# cycle: 46
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M35-surface-corollary34-numerator-obstruction
"""Classifier for the Kim--Tao Corollary 3.4 numerator obstruction.

This is an exponent ledger, not a simulation of surface-group quotient
families.  It records where the existing q^(2 kappa) loss enters and what
algebra a future surface-group numerator theorem would need to replace.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/extension_candidates"
FIGS = ROOT / "reports/figures"

LOSS_CSV = DATA / "m35_interpolation_loss_budget.csv"
CLASS_CSV = DATA / "m35_candidate_mechanism_classification.csv"
GAP_CSV = DATA / "m35_surface_input_gap_matrix.csv"
GRID_CSV = DATA / "m35_direct_vs_markov_regime_grid.csv"

LOSS_FIG = FIGS / "m35_corollary34_interpolation_loss.png"
GRAPH_FIG = FIGS / "m35_mechanism_dependency_graph.png"
MAP_FIG = FIGS / "m35_direct_vs_coefficient_variation_map.png"

KAPPA_VALUES = [3.0, 5.0, 8.0]
ETA_VALUES = [0.02, 0.05, 0.08, 0.12, 0.18]
D_VALUES = [0.02, 0.05, 0.08, 0.12, 0.18]
ALPHA_W = 0.006


@dataclass(frozen=True)
class Mechanism:
    name: str
    classification: str
    effective_a_offset: float
    sigma: float
    proof_status: str
    new_surface_input: bool
    description: str

    def effective_a(self, kappa: float) -> float:
        return 2.0 * kappa - self.effective_a_offset


MECHANISMS = [
    Mechanism(
        "existing_markov_interpolation",
        "paper_proved_baseline",
        0.0,
        0.0,
        "theorem_level_existing",
        False,
        "Corollary 3.4 plus reciprocal-integer control and Markov on x^2 p(x).",
    ),
    Mechanism(
        "coefficient_variation_target",
        "conditional_surface_theorem_target",
        2.0,
        0.0,
        "conditional",
        True,
        "Absolute coefficient/signed-variation control for the actual weighted p(x)/Q_id.",
    ),
    Mechanism(
        "direct_small_x_target",
        "conditional_surface_theorem_target",
        0.0,
        0.35,
        "conditional",
        True,
        "Direct evaluation bound at x=1/n, possibly using cancellation invisible to coefficient variation.",
    ),
    Mechanism(
        "signed_cancellation_target",
        "conditional_surface_theorem_target",
        1.0,
        0.25,
        "conditional",
        True,
        "Signed aggregate cancellation in the paper-defined geodesic-weighted numerator.",
    ),
    Mechanism(
        "stronger_surface_lemma33_target",
        "conditional_stronger_input",
        3.0,
        0.25,
        "conditional",
        True,
        "Strengthen Lemma 3.3 uniformly before Corollary 3.4 aggregates the quotient family.",
    ),
    Mechanism(
        "blocked_by_missing_surface_input",
        "toy_only_insufficient",
        2.0,
        0.0,
        "toy_only",
        True,
        "Independent-permutation M4/M7/M33 evidence without MPvH/Nau/surface-group input.",
    ),
]


def required_beta(kappa: float, d: float, eta: float) -> float:
    return 2.0 * kappa * eta + 2.0 * d - 1.0


def candidate_beta(kappa: float, eta: float, mechanism: Mechanism) -> float:
    return mechanism.effective_a_offset * eta + mechanism.sigma


def build_loss_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for kappa in KAPPA_VALUES:
        for eta in ETA_VALUES:
            q_loss_exponent = 2.0 * kappa * eta
            for mechanism in MECHANISMS:
                effective_a = mechanism.effective_a(kappa)
                variance_exponent = 1.0 + effective_a * eta - mechanism.sigma
                rows.append(
                    {
                        "kappa": kappa,
                        "eta": eta,
                        "mechanism": mechanism.name,
                        "classification": mechanism.classification,
                        "effective_A": effective_a,
                        "sigma": mechanism.sigma,
                        "q_loss_exponent": q_loss_exponent if mechanism.name == "existing_markov_interpolation" else effective_a * eta,
                        "markov_q_2kappa_reproduced": mechanism.name == "existing_markov_interpolation",
                        "variance_exponent": variance_exponent,
                        "candidate_beta": candidate_beta(kappa, eta, mechanism),
                        "proved_exponent_improvement": False,
                    }
                )
    return rows


def build_classification_rows() -> list[dict[str, object]]:
    rows = []
    for mechanism in MECHANISMS:
        rows.append(
            {
                "mechanism": mechanism.name,
                "classification": mechanism.classification,
                "proof_status": mechanism.proof_status,
                "paper_proved_input": mechanism.name == "existing_markov_interpolation",
                "requires_new_surface_group_input": mechanism.new_surface_input,
                "uses_only_schreier_or_independent_permutation_evidence": mechanism.name == "blocked_by_missing_surface_input",
                "claims_proved_exponent_improvement": False,
                "claims_local_statistics": False,
                "claims_variance_law": False,
                "claims_shrinking_window_theorem": False,
                "description": mechanism.description,
            }
        )
    special_points = [
        ("x=0", "vacuous_without_coefficient_and_denominator_control", "Expansion point alone does not bound p(1/n)/Q_id(1/n)."),
        ("x=1/n", "target_evaluation_point", "Must stay in Lemma 3.3 range n >= q^kappa and denominator-normalized."),
        ("n=q^kappa", "hard_easy_boundary", "Reciprocal mesh starts here; Markov converts mesh control into small-x derivative control."),
        ("q->infinity", "degree_and_family_complexity_grow", "deg p <= C Lambda0^(-1/2) q and quotient-family complexity grow."),
        ("fixed_Lambda0", "isolates_trace_q_loss", "Keeps Lambda factors inert so the q^(2 kappa) mechanism is visible."),
        ("high_Lambda0", "not_uniform_energy_claim", "Retains endpoint energy factors rather than proving a new energy-uniform theorem."),
        ("Q_id(1/n)", "denominator_normalization_required", "Need Q_id bounded away from zero before numerator savings are meaningful."),
    ]
    for point, classification, description in special_points:
        rows.append(
            {
                "mechanism": f"special_point:{point}",
                "classification": classification,
                "proof_status": "diagnostic",
                "paper_proved_input": point in {"x=1/n", "n=q^kappa", "Q_id(1/n)"},
                "requires_new_surface_group_input": point not in {"x=1/n", "n=q^kappa", "Q_id(1/n)"},
                "uses_only_schreier_or_independent_permutation_evidence": False,
                "claims_proved_exponent_improvement": False,
                "claims_local_statistics": False,
                "claims_variance_law": False,
                "claims_shrinking_window_theorem": False,
                "description": description,
            }
        )
    return rows


def build_gap_rows() -> list[dict[str, object]]:
    return [
        {
            "input": "Lemma 3.3 fixed-pair rational expansion",
            "paper_status": "proved",
            "needed_for_saving": "base_object",
            "gap": "No aggregate coefficient saving; only Q_gamma1,gamma2/Q_id with error.",
            "schreier_transfer_sufficient": False,
        },
        {
            "input": "Corollary 3.4 weighted numerator p(x)",
            "paper_status": "proved_definition",
            "needed_for_saving": "target_object",
            "gap": "Weighted coefficient variation and signed small-x cancellation are not bounded beyond Markov.",
            "schreier_transfer_sufficient": False,
        },
        {
            "input": "Q_id(1/n) denominator normalization",
            "paper_status": "proved_bounded_for_n_ge_qkappa",
            "needed_for_saving": "normalization",
            "gap": "Any numerator target must keep denominator bounded away from zero.",
            "schreier_transfer_sufficient": False,
        },
        {
            "input": "Markov reciprocal-integer interpolation",
            "paper_status": "proved",
            "needed_for_saving": "baseline_to_replace",
            "gap": "This is where q^(2 kappa) appears; replacing it needs direct p/Q_id control.",
            "schreier_transfer_sufficient": False,
        },
        {
            "input": "M4/M7/M33 independent-permutation template evidence",
            "paper_status": "internal_toy_theorem",
            "needed_for_saving": "insufficient_analogy",
            "gap": "Does not include surface-group relation, Witten-zeta normalization, or Nau boundedness.",
            "schreier_transfer_sufficient": False,
        },
        {
            "input": "new surface-group coefficient-variation theorem",
            "paper_status": "open",
            "needed_for_saving": "possible_future_theorem",
            "gap": "Must control the actual geodesic-weighted folded quotient-polynomial family.",
            "schreier_transfer_sufficient": False,
        },
    ]


def build_grid_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    selected = [m for m in MECHANISMS if m.name in {
        "existing_markov_interpolation",
        "coefficient_variation_target",
        "direct_small_x_target",
        "stronger_surface_lemma33_target",
    }]
    for d in D_VALUES:
        for eta in ETA_VALUES:
            support_valid = eta >= d
            endpoint_beating = d > ALPHA_W
            for kappa in [5.0]:
                beta_req = required_beta(kappa, d, eta)
                for mechanism in selected:
                    beta = candidate_beta(kappa, eta, mechanism)
                    conditional_success = support_valid and endpoint_beating and beta > beta_req
                    rows.append(
                        {
                            "kappa": kappa,
                            "alpha_W": ALPHA_W,
                            "d": d,
                            "eta": eta,
                            "mechanism": mechanism.name,
                            "support_valid": support_valid,
                            "endpoint_beating": endpoint_beating,
                            "required_beta": beta_req,
                            "candidate_beta": beta,
                            "conditional_success_if_new_surface_input_proved": conditional_success and mechanism.new_surface_input,
                            "paper_proved_success": False,
                            "failure_reason": classify_failure(support_valid, endpoint_beating, beta, beta_req, mechanism),
                        }
                    )
    return rows


def classify_failure(support_valid: bool, endpoint_beating: bool, beta: float, beta_req: float, mechanism: Mechanism) -> str:
    if not support_valid:
        return "support_invalid_eta_lt_d"
    if not endpoint_beating:
        return "not_endpoint_beating"
    if mechanism.name == "existing_markov_interpolation":
        return "baseline_no_new_beta_saving"
    if mechanism.name == "blocked_by_missing_surface_input":
        return "toy_only_no_surface_transfer"
    if beta <= beta_req:
        return "candidate_saving_too_small"
    return "conditional_on_new_surface_group_theorem"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_loss(rows: list[dict[str, object]]) -> None:
    sample = [r for r in rows if float(r["kappa"]) == 5.0 and r["mechanism"] in {
        "existing_markov_interpolation",
        "coefficient_variation_target",
        "direct_small_x_target",
        "stronger_surface_lemma33_target",
    }]
    labels = []
    values = []
    for mechanism in ["existing_markov_interpolation", "coefficient_variation_target", "direct_small_x_target", "stronger_surface_lemma33_target"]:
        vals = [float(r["q_loss_exponent"]) for r in sample if r["mechanism"] == mechanism and float(r["eta"]) == 0.08]
        labels.append(mechanism.replace("_", "\n"))
        values.append(vals[0])
    LOSS_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    colors = ["#4c78a8", "#72b7b2", "#f58518", "#54a24b"]
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("q-loss exponent after q=n^eta, eta=0.08")
    ax.set_title("Corollary 3.4 numerator: existing Markov loss versus hypothetical controls")
    ax.axhline(values[0], color="black", linewidth=1.0, linestyle="--", label="paper baseline")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(LOSS_FIG, dpi=160)
    plt.close(fig)


def plot_graph() -> None:
    nodes = [
        ("Lemma 3.3\nQ_gamma/Q_id", 0.12, 0.72, "#4c78a8"),
        ("Corollary 3.4\np(x)/Q_id", 0.38, 0.72, "#4c78a8"),
        ("reciprocal samples\nn >= q^kappa", 0.62, 0.72, "#4c78a8"),
        ("Markov on x^2 p(x)\nq^{2kappa}", 0.84, 0.72, "#4c78a8"),
        ("coefficient variation\nopen surface input", 0.38, 0.34, "#f58518"),
        ("direct small-x\nopen surface input", 0.62, 0.34, "#f58518"),
        ("Schreier benchmark\nno transfer", 0.12, 0.34, "#e45756"),
    ]
    edges = [(0, 1), (1, 2), (2, 3), (1, 4), (1, 5), (6, 4)]
    GRAPH_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    for i, j in edges:
        x1, y1 = nodes[i][1], nodes[i][2]
        x2, y2 = nodes[j][1], nodes[j][2]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops={"arrowstyle": "->", "lw": 1.6, "color": "#333333"})
    for label, x, y, color in nodes:
        ax.text(x, y, label, ha="center", va="center", fontsize=9, bbox={"boxstyle": "round,pad=0.3", "fc": color, "ec": "none", "alpha": 0.88}, color="white")
    ax.set_title("Dependency graph: paper-proved path and open numerator targets")
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(GRAPH_FIG, dpi=160)
    plt.close(fig)


def plot_map(rows: list[dict[str, object]]) -> None:
    mechanisms = ["existing_markov_interpolation", "coefficient_variation_target", "direct_small_x_target"]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.8), sharex=True, sharey=True)
    for ax, mechanism in zip(axes, mechanisms):
        subset = [r for r in rows if r["mechanism"] == mechanism]
        xs = [float(r["eta"]) for r in subset]
        ys = [float(r["d"]) for r in subset]
        vals = []
        for r in subset:
            if r["failure_reason"] == "conditional_on_new_surface_group_theorem":
                vals.append(1.0)
            elif r["failure_reason"] == "baseline_no_new_beta_saving":
                vals.append(0.2)
            elif r["failure_reason"].startswith("support"):
                vals.append(0.0)
            else:
                vals.append(0.55)
        ax.scatter(xs, ys, c=vals, cmap="RdYlGn", vmin=0.0, vmax=1.0, s=95, edgecolors="black", linewidths=0.25)
        ax.plot([min(ETA_VALUES), max(ETA_VALUES)], [min(ETA_VALUES), max(ETA_VALUES)], color="#555555", linestyle="--", linewidth=1.0)
        ax.set_title(mechanism.replace("_", "\n"))
        ax.set_xlabel("eta")
        ax.set_ylabel("d")
    fig.suptitle("Direct small-x and coefficient-variation targets are conditional, not proved")
    fig.tight_layout()
    fig.savefig(MAP_FIG, dpi=160)
    plt.close(fig)


def main() -> None:
    loss_rows = build_loss_rows()
    class_rows = build_classification_rows()
    gap_rows = build_gap_rows()
    grid_rows = build_grid_rows()
    write_csv(LOSS_CSV, loss_rows)
    write_csv(CLASS_CSV, class_rows)
    write_csv(GAP_CSV, gap_rows)
    write_csv(GRID_CSV, grid_rows)
    plot_loss(loss_rows)
    plot_graph()
    plot_map(grid_rows)
    for path, rows in [(LOSS_CSV, loss_rows), (CLASS_CSV, class_rows), (GAP_CSV, gap_rows), (GRID_CSV, grid_rows)]:
        print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")
    for path in [LOSS_FIG, GRAPH_FIG, MAP_FIG]:
        print(f"wrote {path.relative_to(ROOT)}")
    print("decision=preserve_surface_numerator_as_open_theorem_target_no_schreier_transfer")


if __name__ == "__main__":
    os.environ.setdefault("MPLBACKEND", "Agg")
    main()
