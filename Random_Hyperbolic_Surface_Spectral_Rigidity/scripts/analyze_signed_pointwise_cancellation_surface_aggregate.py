# created: 2026-05-17T00:35:00Z
# cycle: 48
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M37-signed-pointwise-cancellation-surface-aggregate
"""Signed-cancellation ledger for the Corollary 3.4 surface aggregate.

This is an analytical bookkeeping script, not a surface simulation.  It records
which signed pointwise mechanisms would be genuine theorem targets for the
actual Kim--Tao ratio p(1/n)/Q_id(1/n), and which mechanisms collapse to
coefficient variation, denominator obstruction, range obstruction, or toy-only
evidence.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/extension_candidates"
FIGS = ROOT / "reports/figures"

MECHANISM_CSV = DATA / "m37_signed_mechanism_classification.csv"
STRATUM_CSV = DATA / "m37_stratum_cancellation_grid.csv"
DENOM_CSV = DATA / "m37_denominator_signed_saving_grid.csv"
TARGET_CSV = DATA / "m37_theorem_target_table.csv"

MECHANISM_FIG = FIGS / "m37_signed_mechanism_map.png"
STRATUM_FIG = FIGS / "m37_stratum_cancellation_budget.png"
BOUNDARY_FIG = FIGS / "m37_direct_vs_cv_cancellation_boundary.png"

LAMBDA0_POWER = 20
KAPPA_VALUES = [3.0, 5.0, 8.0]
ETA_VALUES = [0.02, 0.05, 0.08, 0.12, 0.18]
DENOM_LOSSES = [0.0, 0.25, 0.5, 1.0, 2.0]
STRATA = ["all_terms", "fixed_d", "fixed_length", "primitive_power", "quotient_complexity"]


@dataclass(frozen=True)
class Mechanism:
    name: str
    cancellation_type: str
    stratum_type: str
    classification: str
    a_offset: float
    sigma: float
    denominator_loss_d: float
    surface_attached: bool
    pointwise_at_x_1_over_n: bool
    requires_absolute_control: bool
    toy_only: bool
    range_safe: bool
    reason: str

    def effective_a(self, kappa: float) -> float:
        return 2.0 * kappa - self.a_offset

    def beta(self, eta: float, denominator_loss: float | None = None) -> float:
        d_loss = self.denominator_loss_d if denominator_loss is None else denominator_loss
        return self.a_offset * eta + self.sigma - d_loss


MECHANISMS = [
    Mechanism(
        "markov_baseline",
        "none",
        "global",
        "paper_proved_baseline",
        0.0,
        0.0,
        0.0,
        True,
        True,
        False,
        False,
        True,
        "Existing reciprocal-integer plus Markov interpolation bound.",
    ),
    Mechanism(
        "surface_signed_pointwise_grouping",
        "signed_pointwise",
        "surface_quotient_strata",
        "surface_theorem_target",
        1.5,
        0.35,
        0.0,
        True,
        True,
        False,
        False,
        True,
        "Would group actual weighted Q_{gamma1^k1,gamma2^k2}(1/n) terms with signs after normalization.",
    ),
    Mechanism(
        "diagonal_offdiagonal_signed_balance",
        "diagonal_offdiagonal",
        "primitive_power",
        "surface_theorem_target",
        1.0,
        0.25,
        0.0,
        True,
        True,
        False,
        False,
        True,
        "Could be independent only if diagonal and off-diagonal surface strata cancel at x=1/n.",
    ),
    Mechanism(
        "oscillatory_transform_phase",
        "phase_oscillation",
        "length",
        "surface_theorem_target",
        1.0,
        0.35,
        0.0,
        True,
        True,
        False,
        False,
        True,
        "Uses signs from transform values together with surface quotient evaluations.",
    ),
    Mechanism(
        "fixed_d_absolute_stratum_control",
        "absolute_stratum_bound",
        "fixed_d",
        "coefficient_variation_equivalent",
        2.0,
        0.0,
        0.0,
        True,
        True,
        True,
        False,
        True,
        "If every fixed d=C-V stratum is controlled in absolute value, this is coefficient variation in substance.",
    ),
    Mechanism(
        "coefficient_sign_variation_control",
        "coefficient_variation",
        "coefficient",
        "coefficient_variation_equivalent",
        2.0,
        0.15,
        0.0,
        True,
        True,
        True,
        False,
        True,
        "Expands coefficients or total signed variation rather than proving a pointwise value cancellation.",
    ),
    Mechanism(
        "x_zero_only_cancellation",
        "wrong_point",
        "special_point",
        "range_blocked",
        2.0,
        0.35,
        0.0,
        True,
        False,
        False,
        False,
        True,
        "Cancellation at x=0 does not control the evaluated ratio at x=1/n.",
    ),
    Mechanism(
        "off_range_reciprocal_cancellation",
        "wrong_range",
        "reciprocal_boundary",
        "range_blocked",
        2.0,
        0.35,
        0.0,
        True,
        True,
        False,
        False,
        False,
        "Uses reciprocal values below the Corollary 3.4 safe range.",
    ),
    Mechanism(
        "near_zero_denominator_signed_saving",
        "denominator_loss",
        "denominator",
        "denominator_blocked",
        2.0,
        0.6,
        1.0,
        True,
        True,
        False,
        False,
        False,
        "A near-zero denominator subtracts D from the signed numerator saving.",
    ),
    Mechanism(
        "schreier_pairing_transfer",
        "toy_pairing",
        "toy",
        "toy_only",
        2.0,
        0.35,
        0.0,
        False,
        True,
        False,
        True,
        True,
        "Independent-permutation cancellations do not include the surface relation, Q_id, MPvH/Nau inputs, or Selberg weights.",
    ),
]


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


def build_mechanism_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for mechanism in MECHANISMS:
        rows.append(
            {
                "mechanism": mechanism.name,
                "cancellation_type": mechanism.cancellation_type,
                "stratum_type": mechanism.stratum_type,
                "classification": mechanism.classification,
                "A_offset_from_markov": mechanism.a_offset,
                "sigma": mechanism.sigma,
                "denominator_loss_D": mechanism.denominator_loss_d,
                "Lambda0_power": LAMBDA0_POWER,
                "surface_attached": bool_text(mechanism.surface_attached),
                "pointwise_at_x_1_over_n": bool_text(mechanism.pointwise_at_x_1_over_n),
                "requires_absolute_control": bool_text(mechanism.requires_absolute_control),
                "uses_only_schreier_or_independent_permutation_evidence": bool_text(mechanism.toy_only),
                "paper_safe_range": bool_text(mechanism.range_safe and mechanism.denominator_loss_d == 0.0),
                "paper_proved_success": bool_text(mechanism.name == "markov_baseline"),
                "claims_proved_exponent_improvement": "False",
                "claims_local_statistics": "False",
                "claims_variance_law": "False",
                "claims_shrinking_window_theorem": "False",
                "reason": mechanism.reason,
            }
        )
    special_points = [
        ("x=0", "range_blocked", "Wrong evaluation point unless paired with neighborhood or coefficient control."),
        ("x=1/n", "surface_theorem_target", "The actual denominator-normalized target point."),
        ("n=Cq^kappa", "surface_theorem_target", "Paper-safe boundary after constants are chosen."),
        ("q->infinity", "surface_theorem_target", "Degree and quotient complexity grow with q."),
        ("fixed_Lambda0", "paper_proved_baseline", "Isolates the q-exponent while preserving Lambda0^20."),
        ("high_Lambda0", "paper_proved_baseline", "M37 preserves Lambda0^20 and proves no high-energy saving."),
        ("Q_id(1/n)=0", "denominator_blocked", "Excluded in the paper range but fatal outside it."),
        ("Q_id(1/n) near-zero", "denominator_blocked", "Modeled by D; it can erase every signed saving."),
    ]
    for point, classification, reason in special_points:
        rows.append(
            {
                "mechanism": f"special_point:{point}",
                "cancellation_type": "special_point",
                "stratum_type": "special_point",
                "classification": classification,
                "A_offset_from_markov": 0.0,
                "sigma": 0.0,
                "denominator_loss_D": 0.0,
                "Lambda0_power": LAMBDA0_POWER,
                "surface_attached": "True",
                "pointwise_at_x_1_over_n": bool_text(point == "x=1/n"),
                "requires_absolute_control": "False",
                "uses_only_schreier_or_independent_permutation_evidence": "False",
                "paper_safe_range": bool_text(point in {"x=1/n", "n=Cq^kappa", "fixed_Lambda0", "high_Lambda0"}),
                "paper_proved_success": "False",
                "claims_proved_exponent_improvement": "False",
                "claims_local_statistics": "False",
                "claims_variance_law": "False",
                "claims_shrinking_window_theorem": "False",
                "reason": reason,
            }
        )
    return rows


def build_stratum_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    active = [m for m in MECHANISMS if m.name != "markov_baseline"]
    for kappa in KAPPA_VALUES:
        for eta in ETA_VALUES:
            markov_exp = 1.0 + 2.0 * kappa * eta
            for mechanism in active:
                if mechanism.classification == "toy_only":
                    strata = ["toy"]
                elif mechanism.stratum_type in {"special_point", "reciprocal_boundary", "denominator"}:
                    strata = [mechanism.stratum_type]
                else:
                    strata = STRATA
                for stratum in strata:
                    beta = mechanism.beta(eta)
                    exponent = markov_exp - beta
                    useful = (
                        beta > 0
                        and mechanism.classification == "surface_theorem_target"
                        and mechanism.pointwise_at_x_1_over_n
                        and mechanism.range_safe
                    )
                    rows.append(
                        {
                            "kappa": kappa,
                            "eta": eta,
                            "mechanism": mechanism.name,
                            "classification": mechanism.classification,
                            "stratum_type": stratum,
                            "A": mechanism.effective_a(kappa),
                            "A_offset_from_markov": mechanism.a_offset,
                            "sigma": mechanism.sigma,
                            "denominator_loss_D": mechanism.denominator_loss_d,
                            "Lambda0_power": LAMBDA0_POWER,
                            "candidate_beta": beta,
                            "markov_variance_exponent": markov_exp,
                            "signed_variance_exponent": exponent,
                            "survives_absolute_values": bool_text(not mechanism.requires_absolute_control and useful),
                            "coefficient_variation_equivalent": bool_text(mechanism.requires_absolute_control),
                            "independent_signed_target": bool_text(useful),
                            "paper_proved_success": "False",
                        }
                    )
    return rows


def build_denominator_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    representative = [m for m in MECHANISMS if m.classification in {"surface_theorem_target", "coefficient_variation_equivalent"}]
    for eta in ETA_VALUES:
        for mechanism in representative:
            raw = mechanism.a_offset * eta + mechanism.sigma
            for d_loss in DENOM_LOSSES:
                net = mechanism.beta(eta, d_loss)
                rows.append(
                    {
                        "eta": eta,
                        "mechanism": mechanism.name,
                        "classification": mechanism.classification,
                        "A_offset_from_markov": mechanism.a_offset,
                        "sigma": mechanism.sigma,
                        "denominator_loss_D": d_loss,
                        "raw_beta_before_denominator": raw,
                        "net_beta_after_denominator": net,
                        "saving_survives_denominator": bool_text(net > 0),
                        "denominator_safe_regime": bool_text(d_loss == 0.0),
                        "near_zero_denominator_obstruction": bool_text(d_loss >= raw and d_loss > 0.0),
                    }
                )
    return rows


def build_target_rows() -> list[dict[str, object]]:
    targets = [
        (
            "SPC(A,sigma)",
            "surface_theorem_target",
            "|p(1/n)/Q_id(1/n)| <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)) by signed grouping at x=1/n",
            "independent_next_target_if_grouping_is_surface_attached",
        ),
        (
            "fixed_stratum_absolute_control",
            "coefficient_variation_equivalent",
            "absolute or total-variation control in fixed d, length, primitive-power, or quotient-complexity strata",
            "not_independent_from_coefficient_variation",
        ),
        (
            "wrong_point_cancellation",
            "range_blocked",
            "cancellation visible only at x=0 or away from x=1/n",
            "does_not_control_evaluated_ratio",
        ),
        (
            "denominator_uncontrolled_ratio",
            "denominator_blocked",
            "numerator saving without Q_id(1/n) lower bound or with |Q_id(1/n)|^-1 <= n^D",
            "saving_loses_D_and_can_be_erased",
        ),
        (
            "schreier_or_independent_pairing",
            "toy_only",
            "sign-reversing pairings in independent-permutation or Schreier models",
            "analogy_only_no_surface_theorem",
        ),
    ]
    return [
        {
            "target": name,
            "classification": classification,
            "statement": statement,
            "decision": decision,
            "requires_new_surface_group_input": bool_text(classification == "surface_theorem_target"),
            "claims_proved_exponent_improvement": "False",
        }
        for name, classification, statement, decision in targets
    ]


def plot_mechanism_map(rows: list[dict[str, object]]) -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for row in rows:
        if str(row["mechanism"]).startswith("special_point:"):
            continue
        counts[str(row["classification"])] = counts.get(str(row["classification"]), 0) + 1
    colors = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#b279a2"]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    labels = list(counts)
    values = [counts[label] for label in labels]
    ax.bar(labels, values, color=colors[: len(labels)])
    ax.set_ylabel("mechanism rows")
    ax.set_title("M37 signed cancellation mechanism classifications")
    ax.tick_params(axis="x", rotation=25)
    ax.text(0.02, 0.94, "Only surface-attached pointwise rows remain independent theorem targets.", transform=ax.transAxes, fontsize=9)
    fig.tight_layout()
    fig.savefig(MECHANISM_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {MECHANISM_FIG.relative_to(ROOT)}")


def plot_stratum_budget(rows: list[dict[str, object]]) -> None:
    filtered = [r for r in rows if r["stratum_type"] in {"all_terms", "fixed_d", "fixed_length", "primitive_power", "quotient_complexity"} and r["eta"] == 0.08 and r["kappa"] == 5.0]
    names = sorted({str(r["mechanism"]) for r in filtered})
    strata = STRATA
    value = {(str(r["mechanism"]), str(r["stratum_type"])): float(r["candidate_beta"]) for r in filtered}
    fig, ax = plt.subplots(figsize=(9, 4.8))
    image = [[value.get((name, stratum), 0.0) for stratum in strata] for name in names]
    im = ax.imshow(image, aspect="auto", cmap="RdYlGn", vmin=-0.4, vmax=0.8)
    ax.set_xticks(range(len(strata)), strata, rotation=20)
    ax.set_yticks(range(len(names)), names)
    ax.set_title("Candidate beta by stratum at kappa=5, eta=0.08")
    fig.colorbar(im, ax=ax, label="beta=(2kappa-A)eta+sigma-D")
    fig.tight_layout()
    fig.savefig(STRATUM_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {STRATUM_FIG.relative_to(ROOT)}")


def plot_boundary(rows: list[dict[str, object]]) -> None:
    surface = [r for r in rows if r["classification"] == "surface_theorem_target" and r["denominator_loss_D"] == 0.0]
    cv = [r for r in rows if r["classification"] == "coefficient_variation_equivalent" and r["denominator_loss_D"] == 0.0]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.scatter([float(r["A_offset_from_markov"]) for r in surface], [float(r["sigma"]) for r in surface], label="surface pointwise target", color="#4c78a8", s=80)
    ax.scatter([float(r["A_offset_from_markov"]) for r in cv], [float(r["sigma"]) for r in cv], label="coefficient-variation equivalent", color="#f58518", s=80)
    for eta in [0.05, 0.12, 0.18]:
        xs = [0.0, 3.0]
        ys = [max(0.0, 0.25 - eta * x) for x in xs]
        ax.plot(xs, ys, linestyle="--", linewidth=1, label=f"beta=0.25 boundary, eta={eta}")
    ax.set_xlabel("A offset from Markov: 2kappa-A")
    ax.set_ylabel("direct sigma")
    ax.set_title("Pointwise signed cancellation versus coefficient-variation boundary")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(BOUNDARY_FIG, dpi=180)
    plt.close(fig)
    print(f"wrote {BOUNDARY_FIG.relative_to(ROOT)}")


def main() -> None:
    mechanism_rows = build_mechanism_rows()
    stratum_rows = build_stratum_rows()
    denominator_rows = build_denominator_rows()
    target_rows = build_target_rows()

    write_csv(MECHANISM_CSV, mechanism_rows)
    write_csv(STRATUM_CSV, stratum_rows)
    write_csv(DENOM_CSV, denominator_rows)
    write_csv(TARGET_CSV, target_rows)

    plot_mechanism_map(mechanism_rows)
    plot_stratum_budget(stratum_rows)
    plot_boundary(denominator_rows)

    decision = "signed_pointwise_cancellation_remains_independent_only_as_new_surface_ratio_theorem"
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
