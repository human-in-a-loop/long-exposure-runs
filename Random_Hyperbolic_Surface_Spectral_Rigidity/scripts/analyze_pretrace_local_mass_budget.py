# created: 2026-05-16T20:40:00Z
# cycle: 40
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M29-pretrace-local-mass-intermediate-from-theorem2-proof

"""Generate M29 pre-trace local-mass budget tables and figures."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np

DATA_DIR = Path("data/extension_candidates")
FIGURE_DIR = Path("reports/figures")
BUDGET_PATH = DATA_DIR / "m29_pretrace_local_mass_budget.csv"
CLASSIFICATION_PATH = DATA_DIR / "m29_local_mass_statement_classification.csv"
EXPONENT_FIGURE = FIGURE_DIR / "m29_local_mass_exponent_comparison.png"
PIPELINE_FIGURE = FIGURE_DIR / "m29_theorem2_proof_pipeline.png"

BRANCH_DECISION = "advance_pretrace_local_mass_branch"
ALPHA0_MODELS = [
    ("representative_alpha0", 0.040),
    ("small_alpha0_stress", 0.012),
]
ENERGY_MODELS = [
    ("fixed_energy", 0.0),
    ("mild_growth", 0.05),
    ("high_growth", 0.20),
]
MASS_MODELS = [
    ("m28_linf_derived_fixed_patch", 3.0, "proved_from_final_linf", False),
    ("pretrace_fixed_cutoff_local_mass", 1.0, "extracted_from_4_9", True),
    ("hypothetical_no_sobolev_loss_reference", 1.0, "comparison_only", False),
]


def mass_exponent(alpha0: float, lambda_growth: float, lambda_power: float) -> float:
    """Exponent e in bound scale n^e, suppressing constants."""
    return lambda_power * lambda_growth - alpha0


def build_budget_rows() -> list[dict[str, float | str | bool]]:
    rows: list[dict[str, float | str | bool]] = []
    for alpha_label, alpha0 in ALPHA0_MODELS:
        for energy_label, lambda_growth in ENERGY_MODELS:
            baseline = mass_exponent(alpha0, lambda_growth, 3.0)
            for model, lambda_power, source_kind, claimable in MASS_MODELS:
                exponent = mass_exponent(alpha0, lambda_growth, lambda_power)
                lambda_power_gap_vs_m28 = 3.0 - lambda_power
                high_energy_n_gap_vs_m28 = baseline - exponent
                claimed_improvement = model == "pretrace_fixed_cutoff_local_mass"
                rows.append(
                    {
                        "alpha_label": alpha_label,
                        "alpha0": alpha0,
                        "energy_label": energy_label,
                        "lambda_growth_exponent_b": lambda_growth,
                        "model": model,
                        "source_kind": source_kind,
                        "lambda_power": lambda_power,
                        "mass_bound_n_exponent": exponent,
                        "lambda_power_gap_vs_m28": lambda_power_gap_vs_m28,
                        "high_energy_n_gap_vs_m28": high_energy_n_gap_vs_m28,
                        "claimable_corollary": claimable,
                        "claimed_improvement_over_m28": claimed_improvement,
                        "classification": classify_budget_row(model, source_kind, claimable),
                    }
                )
    return rows


def classify_budget_row(model: str, source_kind: str, claimable: bool) -> str:
    if model == "hypothetical_no_sobolev_loss_reference" or source_kind == "comparison_only":
        return "comparison_only"
    if claimable:
        return "standalone_smoothed_kernel_mass_corollary"
    return "m28_deterministic_mass_bound"


def build_classification_rows(budget_rows: list[dict[str, float | str | bool]]) -> list[dict[str, str]]:
    positive_gap_rows = [
        row
        for row in budget_rows
        if row["claimed_improvement_over_m28"] is True and float(row["lambda_power_gap_vs_m28"]) > 0.0
    ]
    return [
        {
            "item": "controlled_statistic",
            "classification": "centered_pretrace_fourth_mass_after_S_subtraction",
            "source": "2603.01127.txt:1101-1147; docs/proof_ledger/pretrace_local_mass_intermediate.md",
            "evidence": "V_n is the fourth power of centered local spectral mass; Proposition 4.1 controls int a(V_n-S)^2.",
            "decision": "",
        },
        {
            "item": "fixed_cutoff_local_mass",
            "classification": "standalone_smoothed_kernel_mass_corollary",
            "source": "2603.01127.txt:1168-1218; docs/proof_ledger/delocalization_proof_reconstruction.md",
            "evidence": f"{len(positive_gap_rows)} budget rows show a positive Lambda-power gap over the M28 Linf-derived mass model.",
            "decision": "",
        },
        {
            "item": "arbitrary_fixed_ball_family",
            "classification": "not_established",
            "source": "docs/proof_ledger/pretrace_local_mass_intermediate.md",
            "evidence": "The proof fixes a smooth cutoff a and does not union over spatial centers or nonsmooth indicators.",
            "decision": "",
        },
        {
            "item": "unsupported_lower_mass_claims",
            "classification": "unsupported_stronger_claim",
            "source": "docs/proof_ledger/pretrace_local_mass_intermediate.md",
            "evidence": "Upper local mass bounds do not imply lower mass or equidistribution in specified regions.",
            "decision": "",
        },
        {
            "item": "hypothetical_no_sobolev_loss_reference",
            "classification": "comparison_only",
            "source": "scripts/analyze_pretrace_local_mass_budget.py",
            "evidence": "Included only to show the size of the final analytic conversion loss; it cannot drive the branch decision.",
            "decision": "",
        },
        {
            "item": "branch_decision",
            "classification": "standalone_smoothed_kernel_mass_corollary",
            "source": "2603.01127.txt:1215-1229",
            "evidence": "The pre-Sobolev local mass estimate has Lambda power 1, while the final squared Linf-derived mass model has Lambda power 3.",
            "decision": BRANCH_DECISION,
        },
    ]


def write_csv(path: Path, rows: list[dict[str, float | str | bool]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_exponent_comparison(rows: list[dict[str, float | str | bool]]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    alpha_label = "representative_alpha0"
    sub = [row for row in rows if row["alpha_label"] == alpha_label]
    energy_labels = [label for label, _ in ENERGY_MODELS]
    x = np.arange(len(energy_labels))
    width = 0.24
    colors = {
        "m28_linf_derived_fixed_patch": "#4c72b0",
        "pretrace_fixed_cutoff_local_mass": "#2a8c63",
        "hypothetical_no_sobolev_loss_reference": "#c44e52",
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    for idx, (model, _power, _source, _claimable) in enumerate(MASS_MODELS):
        vals = [
            float(next(row["mass_bound_n_exponent"] for row in sub if row["energy_label"] == energy and row["model"] == model))
            for energy in energy_labels
        ]
        ax.bar(x + (idx - 1) * width, vals, width, label=model, color=colors[model])
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(energy_labels)
    ax.set_ylabel("exponent e in mass bound scale n^e")
    ax.set_title("M29 local mass budget: pre-Sobolev vs final Linf-derived")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(EXPONENT_FIGURE, dpi=180)
    plt.close(fig)


def plot_pipeline() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    labels = [
        "pre-trace\n(2.5)",
        "centered\nlocal mass",
        "V_n and\nS subtraction",
        "Prop. 4.1\nmoment bound",
        "Chebyshev +\nfiber/window union",
        "local L2 mass\n(4.9)",
        "Sobolev/elliptic\nLinf",
    ]
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.set_xlim(0, len(labels))
    ax.set_ylim(0, 1)
    ax.axis("off")
    for idx, label in enumerate(labels):
        x = idx + 0.08
        face = "#e8f2ed" if label.startswith("local") else "#eef1f6"
        if "Sobolev" in label:
            face = "#f7e6e3"
        rect = Rectangle((x, 0.35), 0.82, 0.32, facecolor=face, edgecolor="#2f3b45", linewidth=1)
        ax.add_patch(rect)
        ax.text(x + 0.41, 0.51, label, ha="center", va="center", fontsize=9)
        if idx < len(labels) - 1:
            arrow = FancyArrowPatch((x + 0.84, 0.51), (idx + 1.06, 0.51), arrowstyle="->", mutation_scale=12, linewidth=1)
            ax.add_patch(arrow)
    ax.text(5.49, 0.2, "M29 extracted statement sits here", ha="center", va="center", fontsize=9, color="#216a4a")
    ax.text(6.49, 0.82, "final Theorem 2", ha="center", va="center", fontsize=9, color="#9b3d31")
    fig.tight_layout()
    fig.savefig(PIPELINE_FIGURE, dpi=180)
    plt.close(fig)


def main() -> None:
    budget_rows = build_budget_rows()
    classification_rows = build_classification_rows(budget_rows)
    write_csv(BUDGET_PATH, budget_rows)
    write_csv(CLASSIFICATION_PATH, classification_rows)
    plot_exponent_comparison(budget_rows)
    plot_pipeline()
    print(f"wrote {BUDGET_PATH} ({len(budget_rows)} rows)")
    print(f"wrote {CLASSIFICATION_PATH} ({len(classification_rows)} rows)")
    print(f"wrote {EXPONENT_FIGURE}")
    print(f"wrote {PIPELINE_FIGURE}")
    print(f"decision={BRANCH_DECISION}")


if __name__ == "__main__":
    main()
