# created: 2026-05-17T01:05:00Z
# cycle: 49
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M38-surface-native-grouping-problem
"""Classify paper-native grouping invariants for the Corollary 3.4 numerator.

This script is deterministic bookkeeping.  It does not enumerate surface
quotient families; it records which groupings are visible in the actual
Kim--Tao Lemma 3.3 / Corollary 3.4 objects and which proposed controls remain
genuine pointwise targets at x=1/n after weights and denominator normalization.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/extension_candidates"
FIGS = ROOT / "reports/figures"

CLASSIFICATION_CSV = DATA / "m38_grouping_invariant_classification.csv"
BETA_CSV = DATA / "m38_grouping_beta_budget.csv"
DEPENDENCY_CSV = DATA / "m38_grouping_dependency_matrix.csv"
TEMPLATE_CSV = DATA / "m38_candidate_spc_theorem_templates.csv"

MAP_FIG = FIGS / "m38_surface_grouping_invariant_map.png"
BETA_FIG = FIGS / "m38_grouping_beta_budget.png"
BOUNDARY_FIG = FIGS / "m38_grouping_vs_coefficient_variation_boundary.png"

LAMBDA0_POWER = 20
KAPPA_VALUES = [3.0, 5.0, 8.0]
ETA_VALUES = [0.02, 0.05, 0.08, 0.12, 0.18]
DENOMINATOR_LOSSES = [0.0, 0.25, 0.5, 1.0]


@dataclass(frozen=True)
class Grouping:
    name: str
    invariant: str
    paper_visibility: str
    sign_source: str
    evaluation_point: str
    denominator_regime: str
    required_input: str
    classification: str
    a_offset: float
    sigma: float
    d_loss: float
    paper_native: bool
    pointwise_at_x_1_over_n: bool
    denominator_safe: bool
    requires_absolute_fixed_stratum: bool
    uses_schreier_evidence: bool
    theorem_template: str
    reason: str

    def a_value(self, kappa: float) -> float:
        return 2.0 * kappa - self.a_offset

    def beta(self, eta: float, denominator_loss: float | None = None) -> float:
        loss = self.d_loss if denominator_loss is None else denominator_loss
        return self.a_offset * eta + self.sigma - loss


def bool_text(value: bool) -> str:
    return "True" if value else "False"


GROUPINGS = [
    Grouping(
        "markov_baseline",
        "global_corollary34_ratio",
        "paper_proved",
        "none",
        "x=1/n",
        "paper_safe",
        "reciprocal-integer control plus Markov brothers for x^2 p(x)",
        "paper_proved_baseline",
        0.0,
        0.0,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "not a new grouping theorem",
        "Existing baseline; included to anchor Lambda0^20 and zero saving.",
    ),
    Grouping(
        "quotient_complex_profile_pointwise",
        "quotient polynomial degree/profile and d=C-V proxy",
        "paper_visible",
        "Q_{gamma1^k1,gamma2^k2}(1/n) signs after transform weights",
        "x=1/n",
        "paper_safe",
        "surface quotient-family cancellation inside each profile without absolute coefficient expansion",
        "underdetermined_surface_input",
        1.5,
        0.30,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_G(A,sigma) for quotient-complex profiles",
        "Paper-native invariant, but no current surface theorem supplies profile-level sign cancellation.",
    ),
    Grouping(
        "surface_relation_kernel_grouping",
        "kernel constraints from the surface relation and quotient complex",
        "paper_visible_but_implicit",
        "evaluated quotient-polynomial signs constrained by surface-group relations",
        "x=1/n",
        "paper_safe",
        "new Lemma 3.3-level structural cancellation theorem for relation-compatible quotients",
        "surface_theorem_target",
        1.25,
        0.35,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_G(A,sigma) for surface-relation kernel classes",
        "This is the cleanest surviving direct grouping target because it is surface-native and pointwise.",
    ),
    Grouping(
        "diagonal_offdiagonal_relation_balance",
        "diagonal versus off-diagonal word relation",
        "paper_visible",
        "signed balance between diagonal and non-diagonal evaluated terms",
        "x=1/n",
        "paper_safe",
        "actual surface diagonal/off-diagonal cancellation after Selberg and transform weights",
        "underdetermined_surface_input",
        1.0,
        0.25,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_G(A,sigma) for diagonal/off-diagonal classes",
        "Visible in the aggregate, but the diagonal is typically same-sign and must be balanced by a real surface input.",
    ),
    Grouping(
        "primitive_power_profile",
        "primitive geodesic and power pair (gamma,k)",
        "paper_visible",
        "transform signs and quotient evaluations across primitive-power shells",
        "x=1/n",
        "paper_safe",
        "power-profile cancellation that does not take absolute values inside each power shell",
        "underdetermined_surface_input",
        1.0,
        0.20,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_G(A,sigma) for primitive-power profiles",
        "Primitive-power structure is native to the Selberg sum but cancellation remains unproved.",
    ),
    Grouping(
        "length_shell_transform_phase",
        "geodesic length shell and transform sign/phase",
        "paper_visible",
        "(h o f_Lambda0)^vee(k ell_gamma) signs times Q_i(1/n)",
        "x=1/n",
        "paper_safe",
        "phase cancellation across length shells after positive Selberg length denominator",
        "surface_theorem_target",
        1.0,
        0.35,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_G(A,sigma) for transform-phase length shells",
        "Native sign source; theorem-ready as a falsifiable target but not proved by current paper inputs.",
    ),
    Grouping(
        "fixed_d_absolute_control",
        "fixed d=C-V stratum",
        "paper_visible_via_degree_proxy",
        "none after absolute values",
        "x=1/n",
        "paper_safe",
        "sum of absolute weights or coefficient total variation inside every fixed d stratum",
        "coefficient_variation_equivalent",
        2.0,
        0.0,
        0.0,
        True,
        True,
        True,
        True,
        False,
        "not direct SPC_G; coefficient/signed-variation theorem",
        "Taking absolute values in fixed d strata collapses the direct route into coefficient variation.",
    ),
    Grouping(
        "length_or_power_absolute_control",
        "fixed length or primitive-power stratum",
        "paper_visible",
        "none after absolute values",
        "x=1/n",
        "paper_safe",
        "absolute control in every length or primitive-power shell",
        "coefficient_variation_equivalent",
        2.0,
        0.10,
        0.0,
        True,
        True,
        True,
        True,
        False,
        "not direct SPC_G; coefficient/signed-variation theorem",
        "A useful proof may exist, but it is no longer signed pointwise cancellation.",
    ),
    Grouping(
        "coefficient_expansion_by_x0",
        "coefficient cancellation at x=0",
        "paper_object_wrong_point",
        "coefficient signs at x=0",
        "x=0",
        "paper_safe",
        "neighborhood or coefficient-variation theorem connecting x=0 to x=1/n",
        "range_blocked",
        2.0,
        0.25,
        0.0,
        True,
        False,
        True,
        False,
        False,
        "blocked unless upgraded to coefficient variation",
        "The target value is x=1/n; cancellation only at x=0 is the wrong point.",
    ),
    Grouping(
        "off_range_reciprocal_grouping",
        "reciprocal grid below paper-safe range",
        "paper_range_violation",
        "evaluated quotient signs",
        "x=1/n",
        "off_range",
        "Lemma 3.3 denominator and error control outside n >= C q^kappa",
        "range_blocked",
        2.0,
        0.25,
        0.0,
        True,
        True,
        False,
        False,
        False,
        "blocked outside paper range",
        "Leaving the safe reciprocal-integer range loses the Corollary 3.4 normalization.",
    ),
    Grouping(
        "near_zero_denominator_grouping",
        "Q_id(1/n) small or zero",
        "paper_excluded_in_safe_range",
        "numerator signs divided by unstable denominator",
        "x=1/n",
        "denominator_loss",
        "lower bound for Q_id(1/n) or explicit D-loss budget",
        "denominator_blocked",
        2.0,
        0.45,
        1.0,
        True,
        True,
        False,
        False,
        False,
        "blocked unless beta remains positive after D",
        "Denominator loss subtracts from every signed numerator saving.",
    ),
    Grouping(
        "schreier_pairing_analogy",
        "independent-permutation sign pairing",
        "toy_imported",
        "toy model pairing signs",
        "x=1/n",
        "paper_safe",
        "surface replacement for independent permutation pairing",
        "toy_only",
        2.0,
        0.30,
        0.0,
        False,
        True,
        True,
        False,
        True,
        "analogy only",
        "Schreier evidence lacks the surface relation, Q_id, MPvH/Nau inputs, and Selberg weights.",
    ),
]


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


def classification_rows() -> list[dict[str, object]]:
    rows = []
    for group in GROUPINGS:
        rows.append(
            {
                "grouping": group.name,
                "grouping_invariant": group.invariant,
                "paper_visibility": group.paper_visibility,
                "sign_source": group.sign_source,
                "evaluation_point": group.evaluation_point,
                "denominator_regime": group.denominator_regime,
                "required_input": group.required_input,
                "classification": group.classification,
                "A_offset": group.a_offset,
                "sigma": group.sigma,
                "D": group.d_loss,
                "Lambda0_power": LAMBDA0_POWER,
                "beta_formula": "beta=(2 kappa - A) eta + sigma - D",
                "paper_native": bool_text(group.paper_native),
                "pointwise_at_x_1_over_n": bool_text(group.pointwise_at_x_1_over_n),
                "denominator_safe": bool_text(group.denominator_safe),
                "requires_absolute_fixed_stratum": bool_text(group.requires_absolute_fixed_stratum),
                "uses_schreier_or_independent_permutation_evidence": bool_text(group.uses_schreier_evidence),
                "claims_proved_exponent_improvement": "False",
                "claims_local_statistics": "False",
                "claims_variance_law": "False",
                "claims_shrinking_window_theorem": "False",
                "theorem_template": group.theorem_template,
                "reason": group.reason,
            }
        )
    return rows


def beta_rows() -> list[dict[str, object]]:
    rows = []
    for group in GROUPINGS:
        for kappa in KAPPA_VALUES:
            markov_exponent = 1.0 + 2.0 * kappa * 0.0
            for eta in ETA_VALUES:
                for d_loss in DENOMINATOR_LOSSES:
                    beta = group.beta(eta, d_loss)
                    theorem_ready = (
                        group.classification == "surface_theorem_target"
                        and group.paper_native
                        and group.pointwise_at_x_1_over_n
                        and group.denominator_safe
                        and d_loss == 0.0
                        and not group.requires_absolute_fixed_stratum
                    )
                    rows.append(
                        {
                            "grouping": group.name,
                            "classification": group.classification,
                            "kappa": kappa,
                            "eta": eta,
                            "A": group.a_value(kappa),
                            "A_offset": group.a_offset,
                            "sigma": group.sigma,
                            "D": d_loss,
                            "Lambda0_power": LAMBDA0_POWER,
                            "beta": beta,
                            "markov_variance_exponent": 1.0 + 2.0 * kappa * eta,
                            "grouped_variance_exponent": 1.0 + 2.0 * kappa * eta - beta,
                            "denominator_safe_regime": bool_text(d_loss == 0.0 and group.denominator_safe),
                            "saving_survives_denominator": bool_text(beta > 0.0),
                            "theorem_ready_spc_g": bool_text(theorem_ready),
                            "coefficient_variation_equivalent": bool_text(group.classification == "coefficient_variation_equivalent"),
                            "near_zero_denominator_obstruction": bool_text(d_loss > 0.0 and d_loss >= group.a_offset * eta + group.sigma),
                        }
                    )
    return rows


def dependency_rows() -> list[dict[str, object]]:
    dependencies = [
        ("actual Corollary 3.4 summand", "required_for_all", "yes"),
        ("Selberg length weight positivity", "sign bookkeeping", "yes"),
        ("transform sign values", "possible sign source", "yes"),
        ("Q_i(1/n) evaluated signs", "possible sign source", "yes"),
        ("Q_id(1/n) lower bound", "denominator safety", "yes"),
        ("coefficient expansion", "collapses direct route if essential", "conditional"),
        ("Schreier independent pairing", "negative control only", "no"),
    ]
    rows = []
    for group in GROUPINGS:
        for dependency, role, needed in dependencies:
            if dependency == "coefficient expansion":
                status = "required" if group.requires_absolute_fixed_stratum else "not_required_for_direct_target"
            elif dependency == "Schreier independent pairing":
                status = "toy_only" if group.uses_schreier_evidence else "not_used"
            elif dependency == "Q_id(1/n) lower bound":
                status = "fails_or_costs_D" if not group.denominator_safe else "required_and_available_in_paper_range"
            else:
                status = "required" if group.paper_native else "missing_from_toy"
            rows.append(
                {
                    "grouping": group.name,
                    "classification": group.classification,
                    "dependency": dependency,
                    "role": role,
                    "needed_for_valid_surface_theorem": needed,
                    "status_for_grouping": status,
                }
            )
    return rows


def template_rows() -> list[dict[str, object]]:
    templates = []
    for group in GROUPINGS:
        if group.classification in {"surface_theorem_target", "underdetermined_surface_input"}:
            templates.append(
                {
                    "template": group.theorem_template,
                    "grouping": group.name,
                    "classification": group.classification,
                    "statement": (
                        f"For grouping G={group.name}, prove |sum_i_in_G w_i "
                        "Q_i(1/n)/Q_id(1/n)| <= C n Lambda0^20 ||htilde||^2 "
                        "q^A n^(-sigma+o(1)) by signed cancellation at x=1/n."
                    ),
                    "falsifiable_hypotheses": (
                        "paper-native; evaluated at x=1/n; denominator safe; "
                        "no absolute fixed-stratum variation inside G"
                    ),
                    "A_offset": group.a_offset,
                    "sigma": group.sigma,
                    "D": group.d_loss,
                    "Lambda0_power": LAMBDA0_POWER,
                    "beta_formula": "beta=(2 kappa - A) eta + sigma - D",
                    "pivot_rule": (
                        "If proof requires sum_i |w_i Q_i| or coefficient total "
                        "variation inside fixed strata, pivot to coefficient/signed variation."
                    ),
                    "claims_proved_exponent_improvement": "False",
                }
            )
    return templates


def plot_classification(rows: list[dict[str, object]]) -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["classification"])] = counts.get(str(row["classification"]), 0) + 1
    labels = list(counts)
    values = [counts[label] for label in labels]
    colors = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#b279a2"]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(labels, values, color=colors[: len(labels)])
    ax.set_ylabel("grouping rows")
    ax.set_title("M38 paper-native grouping invariant classifications")
    ax.tick_params(axis="x", rotation=25)
    ax.text(0.02, 0.93, "Only paper-native, pointwise, denominator-safe rows can be SPC_G targets.", transform=ax.transAxes, fontsize=9)
    fig.tight_layout()
    fig.savefig(MAP_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {MAP_FIG.relative_to(ROOT)}")


def plot_beta(rows: list[dict[str, object]]) -> None:
    selected = [
        r
        for r in rows
        if float(r["kappa"]) == 5.0
        and float(r["eta"]) == 0.08
        and str(r["grouping"]) != "markov_baseline"
    ]
    names = [str(r["grouping"]) for r in selected if float(r["D"]) == 0.0]
    losses = DENOMINATOR_LOSSES
    matrix = []
    for name in names:
        matrix.append([float(r["beta"]) for r in selected if str(r["grouping"]) == name])
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=-0.8, vmax=0.8)
    ax.set_xticks(range(len(losses)), [f"D={loss:g}" for loss in losses])
    ax.set_yticks(range(len(names)), names)
    ax.set_title("Signed-saving beta budget at kappa=5, eta=0.08")
    fig.colorbar(im, ax=ax, label="beta")
    fig.tight_layout()
    fig.savefig(BETA_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {BETA_FIG.relative_to(ROOT)}")


def plot_boundary(rows: list[dict[str, object]]) -> None:
    surface = [r for r in rows if r["classification"] == "surface_theorem_target"]
    cv = [r for r in rows if r["classification"] == "coefficient_variation_equivalent"]
    under = [r for r in rows if r["classification"] == "underdetermined_surface_input"]
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.scatter([float(r["A_offset"]) for r in surface], [float(r["sigma"]) for r in surface], color="#4c78a8", label="surface theorem target", s=80)
    ax.scatter([float(r["A_offset"]) for r in under], [float(r["sigma"]) for r in under], color="#54a24b", label="underdetermined surface input", s=80)
    ax.scatter([float(r["A_offset"]) for r in cv], [float(r["sigma"]) for r in cv], color="#f58518", label="coefficient variation equivalent", s=80)
    for eta in [0.05, 0.12, 0.18]:
        xs = [0.0, 2.5]
        ys = [max(0.0, 0.25 - eta * x) for x in xs]
        ax.plot(xs, ys, "--", linewidth=1, label=f"beta=0.25, eta={eta}")
    ax.set_xlabel("A offset from Markov: 2kappa-A")
    ax.set_ylabel("sigma")
    ax.set_title("Boundary between pointwise grouping and coefficient variation")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(BOUNDARY_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {BOUNDARY_FIG.relative_to(ROOT)}")


def main() -> None:
    rows = classification_rows()
    beta = beta_rows()
    dependencies = dependency_rows()
    templates = template_rows()

    write_csv(CLASSIFICATION_CSV, rows)
    write_csv(BETA_CSV, beta)
    write_csv(DEPENDENCY_CSV, dependencies)
    write_csv(TEMPLATE_CSV, templates)

    plot_classification(rows)
    plot_beta(beta)
    plot_boundary(rows)
    print("decision=surface_relation_and_transform_phase_groupings_survive_only_as_new_SPC_G_targets")
    print("pivot_rule=pivot_to_coefficient_signed_variation_if_absolute_fixed_stratum_control_is_required")


if __name__ == "__main__":
    main()
