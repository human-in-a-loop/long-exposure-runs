# created: 2026-05-16T12:45:00Z
# cycle: 26
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M15-kim-tao-bridge-requirement
"""Compare M14 decay requirements with crude Selberg/geodesic growth proxies."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DECAY_CSV = ROOT / "data/extension_candidates/kim_tao_decay_requirement_table.csv"
SCENARIO_CSV = ROOT / "data/extension_candidates/conditional_exponent_scenarios.csv"
DECAY_FIG = ROOT / "reports/figures/m15_decay_requirement_vs_selberg_growth.png"
SCENARIO_FIG = ROOT / "reports/figures/m15_conditional_exponent_scenarios.png"

M14_REQUIREMENTS = {
    "tv_order1_linear": 0.6,
    "coeff_av_order1_linear": 1.6,
    "coeff_av_order4_linear": 1.9,
}


def num_text(value: float) -> str:
    if math.isnan(value):
        return ""
    if abs(value) < 1e-12:
        value = 0.0
    return f"{value:.12g}"


def effective_beta_per_word(model: str, c_length: float, cutoff_delta: float) -> float:
    """Return net exponential decay in word length after growth is included."""
    selberg_decay = c_length * (0.5 + cutoff_delta)
    word_growth = math.log(3.0)
    geodesic_growth = c_length
    if model == "reduced_word_growth":
        return selberg_decay - word_growth
    if model == "primitive_geodesic_growth":
        return selberg_decay - geodesic_growth
    if model == "combined_word_geodesic_growth":
        return selberg_decay - word_growth - geodesic_growth
    raise ValueError(model)


def build_decay_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    c_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    delta_values = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    models = [
        "reduced_word_growth",
        "primitive_geodesic_growth",
        "combined_word_geodesic_growth",
    ]
    for model in models:
        for c_length in c_values:
            for cutoff_delta in delta_values:
                beta = effective_beta_per_word(model, c_length, cutoff_delta)
                for requirement, threshold in M14_REQUIREMENTS.items():
                    rows.append(
                        {
                            "growth_model": model,
                            "ell_per_word_c": num_text(c_length),
                            "extra_test_decay_delta": num_text(cutoff_delta),
                            "selberg_weight_beta_per_word": num_text(0.5 * c_length),
                            "cutoff_decay_beta_per_word": num_text(cutoff_delta * c_length),
                            "effective_beta_after_growth": num_text(beta),
                            "m14_requirement": requirement,
                            "required_beta": num_text(threshold),
                            "margin": num_text(beta - threshold),
                            "meets_requirement": "yes" if beta >= threshold else "no",
                            "notes": (
                                "Proxy only: ell is modeled as c*L; Selberg hyperbolic weight "
                                "is exp(-ell/2), optional cutoff contributes exp(-delta*ell)."
                            ),
                        }
                    )
    return rows


def trace_alpha_from_q_loss(q_loss_power: float, epsilon: float) -> tuple[float, float, float]:
    """Representative Theorem 1 alpha algebra with q^b replacing q^(2 kappa)."""
    half_loss = 0.5 * q_loss_power
    K = math.floor((half_loss + 5.0) / (2.0 * epsilon)) + 1.0
    m = half_loss + 3.0 + K
    alpha0 = 1.0 / (3.0 * m)
    alpha_weyl = min(alpha0, 1.0 / 9.0)
    alpha_rigidity = (2.0 / 3.0) * alpha_weyl
    return alpha0, alpha_weyl, alpha_rigidity


def theorem2_alpha_from_q_loss(q_loss_power: float) -> tuple[float, float]:
    """Representative Theorem 2 algebra with q^b replacing q^(4 kappa)."""
    derivative_order = 0.5 * q_loss_power + 11.0
    alpha0 = 1.0 / (16.0 * derivative_order)
    return alpha0, 0.5 * alpha0


def build_scenario_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for kappa in [3.0, 5.0, 8.0]:
        for epsilon in [0.05, 0.1]:
            current_trace_loss = 2.0 * kappa
            trace_scenarios = [
                ("current_trace_markov", current_trace_loss),
                ("half_trace_markov_power", current_trace_loss / 2.0),
                ("fixed_q2_trace_loss", 2.0),
                ("bounded_trace_loss", 0.0),
            ]
            base_alpha0, base_weyl, base_rigidity = trace_alpha_from_q_loss(current_trace_loss, epsilon)
            for label, q_loss in trace_scenarios:
                alpha0, alpha_weyl, alpha_rigidity = trace_alpha_from_q_loss(q_loss, epsilon)
                rows.append(
                    {
                        "theorem_path": "theorem1_rigidity",
                        "scenario": label,
                        "kappa": num_text(kappa),
                        "epsilon": num_text(epsilon),
                        "q_loss_power_b": num_text(q_loss),
                        "current_q_loss_power": num_text(current_trace_loss),
                        "intermediate_alpha0": num_text(alpha0),
                        "theorem_alpha": num_text(alpha_rigidity),
                        "current_theorem_alpha": num_text(base_rigidity),
                        "improvement_factor": num_text(alpha_rigidity / base_rigidity),
                        "dominant_remaining_axis": "smooth cutoff derivative budget and Weyl-edge 2/3 conversion",
                        "notes": "Trace path uses alpha_R=(2/3)*min(alpha0,1/9); reducing q-loss helps until other axes dominate.",
                    }
                )

            current_pretrace_loss = 4.0 * kappa
            pretrace_scenarios = [
                ("current_pretrace_markov", current_pretrace_loss),
                ("half_pretrace_markov_power", current_pretrace_loss / 2.0),
                ("fixed_q4_pretrace_loss", 4.0),
                ("bounded_pretrace_loss", 0.0),
            ]
            _, base_linf = theorem2_alpha_from_q_loss(current_pretrace_loss)
            for label, q_loss in pretrace_scenarios:
                alpha0, alpha_linf = theorem2_alpha_from_q_loss(q_loss)
                rows.append(
                    {
                        "theorem_path": "theorem2_delocalization",
                        "scenario": label,
                        "kappa": num_text(kappa),
                        "epsilon": num_text(epsilon),
                        "q_loss_power_b": num_text(q_loss),
                        "current_q_loss_power": num_text(current_pretrace_loss),
                        "intermediate_alpha0": num_text(alpha0),
                        "theorem_alpha": num_text(alpha_linf),
                        "current_theorem_alpha": num_text(base_linf),
                        "improvement_factor": num_text(alpha_linf / base_linf),
                        "dominant_remaining_axis": "eighth-power cutoff derivative budget plus local mass to Linf conversion",
                        "notes": "Pre-trace path uses alpha=alpha0/2 with alpha0=1/(16*(b/2+11)).",
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_decay(rows: list[dict[str, str]]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    models = ["reduced_word_growth", "primitive_geodesic_growth", "combined_word_geodesic_growth"]
    delta_values = sorted({float(row["extra_test_decay_delta"]) for row in rows})
    for ax, model in zip(axes, models):
        for c_length in [0.5, 1.0, 2.0, 3.0]:
            values = []
            for delta in delta_values:
                beta = effective_beta_per_word(model, c_length, delta)
                values.append(beta)
            ax.plot(delta_values, values, marker="o", label=f"c={c_length:g}")
        ax.axhline(M14_REQUIREMENTS["tv_order1_linear"], color="#4c78a8", linestyle=":", label="TV beta 0.6")
        ax.axhline(M14_REQUIREMENTS["coeff_av_order1_linear"], color="#f58518", linestyle="--", label="AV beta 1.6")
        ax.axhline(M14_REQUIREMENTS["coeff_av_order4_linear"], color="#e45756", linestyle="-.", label="AV beta 1.9")
        ax.axhline(0.0, color="black", linewidth=0.8)
        ax.set_title(model.replace("_", " "))
        ax.set_xlabel("extra cutoff decay delta")
        ax.grid(True, alpha=0.25)
    axes[0].set_ylabel("effective beta per word after growth")
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4)
    fig.suptitle("M15 proxy: Selberg/test-function decay versus growth and M14 thresholds")
    fig.tight_layout(rect=(0, 0.14, 1, 0.93))
    DECAY_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(DECAY_FIG, dpi=180)
    plt.close(fig)


def plot_scenarios(rows: list[dict[str, str]]) -> None:
    selected = [
        row
        for row in rows
        if row["epsilon"] == "0.1" and row["kappa"] in {"3", "5", "8"}
    ]
    paths = ["theorem1_rigidity", "theorem2_delocalization"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=False)
    for ax, path in zip(axes, paths):
        path_rows = [row for row in selected if row["theorem_path"] == path]
        labels = []
        values = []
        for kappa in ["3", "5", "8"]:
            current = [row for row in path_rows if row["kappa"] == kappa and row["scenario"].startswith("current")][0]
            bounded = [row for row in path_rows if row["kappa"] == kappa and row["scenario"].startswith("bounded")][0]
            labels.extend([f"k={kappa}\ncurrent", f"k={kappa}\nbounded"])
            values.extend([float(current["theorem_alpha"]), float(bounded["theorem_alpha"])])
        ax.bar(labels, values, color=["#bab0ac", "#54a24b"] * 3)
        ax.set_title(path.replace("_", " "))
        ax.set_ylabel("representative theorem alpha")
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Conditional theorem alpha if Markov q-loss is replaced")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    SCENARIO_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SCENARIO_FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    decay_rows = build_decay_rows()
    scenario_rows = build_scenario_rows()
    write_csv(DECAY_CSV, decay_rows)
    write_csv(SCENARIO_CSV, scenario_rows)
    plot_decay(decay_rows)
    plot_scenarios(scenario_rows)
    print(f"wrote {DECAY_CSV} rows={len(decay_rows)}")
    print(f"wrote {SCENARIO_CSV} rows={len(scenario_rows)}")
    print(f"wrote {DECAY_FIG}")
    print(f"wrote {SCENARIO_FIG}")


if __name__ == "__main__":
    main()
