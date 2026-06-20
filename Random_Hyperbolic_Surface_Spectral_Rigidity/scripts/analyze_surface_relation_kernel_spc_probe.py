# created: 2026-05-17T01:30:00Z
# cycle: 50
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M39-surface-relation-kernel-spc-probe
"""Diagnose whether Lemma 3.3 kernel closure supports direct SPC.

This is deterministic analytical bookkeeping.  It reconstructs where the
surface-relation kernel condition enters Kim--Tao Lemma 3.3 and classifies
candidate relation-kernel mechanisms for the evaluated Corollary 3.4 ratio
at x=1/n.  It does not simulate surface quotient families.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/extension_candidates"
FIGS = ROOT / "reports/figures"
DOCS = ROOT / "docs/proof_ledger"
REPORTS = ROOT / "reports/extension_candidates"

SCHEMA_CSV = DATA / "m39_kernel_constraint_schema.csv"
CLASSIFICATION_CSV = DATA / "m39_kernel_spc_classification.csv"
BETA_CSV = DATA / "m39_kernel_beta_budget.csv"
PIVOT_CSV = DATA / "m39_kernel_pivot_decision.csv"

FLOW_FIG = FIGS / "m39_kernel_constraint_flow.png"
MAP_FIG = FIGS / "m39_kernel_spc_decision_map.png"
BETA_FIG = FIGS / "m39_kernel_beta_budget.png"

PROOF_LEDGER = DOCS / "surface_relation_kernel_spc_probe.md"
REPORT = REPORTS / "m39_surface_relation_kernel_spc_probe.md"

LAMBDA0_POWER = 20
KAPPA_VALUES = [3.0, 5.0, 8.0]
ETA_VALUES = [0.02, 0.05, 0.08, 0.12, 0.18]
DENOMINATOR_LOSSES = [0.0, 0.25, 0.5, 1.0]


@dataclass(frozen=True)
class Mechanism:
    name: str
    kernel_role: str
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
    requires_absolute_kernel_stratum: bool
    uses_toy_or_free_group_proxy: bool
    theorem_template: str
    decision: str
    reason: str

    def a_value(self, kappa: float) -> float:
        return 2.0 * kappa - self.a_offset

    def beta(self, kappa: float, eta: float, denominator_loss: float | None = None) -> float:
        loss = self.d_loss if denominator_loss is None else denominator_loss
        return (2.0 * kappa - self.a_value(kappa)) * eta + self.sigma - loss


def bool_text(value: bool) -> str:
    return "True" if value else "False"


MECHANISMS = [
    Mechanism(
        "markov_baseline",
        "global reciprocal-integer interpolation of x^2 p(x)",
        "none",
        "x=1/n",
        "paper_safe",
        "Kim--Tao Markov brothers step",
        "paper_proved_baseline",
        0.0,
        0.0,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "not a kernel SPC theorem",
        "baseline",
        "Existing bound has Lambda0^20 and zero direct saving.",
    ),
    Mechanism(
        "kernel_closure_admissibility",
        "defines the admissible folded quotients W_r in Lemma 3.3",
        "none from kernel closure itself",
        "x=1/n",
        "paper_safe",
        "new argument turning admissibility into evaluated sign information",
        "underdetermined_surface_input",
        0.75,
        0.10,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_kernel only after an additional sign theorem",
        "not_theorem_ready",
        "Kernel closure is paper-native, but Lemma 3.3 uses it to define/factor quotient targets, not to pair opposite signs.",
    ),
    Mechanism(
        "kernel_class_signed_pairing",
        "partition W_r by relation-kernel closure class",
        "hypothetical signs of Q_r(1/n) across relation-compatible classes",
        "x=1/n",
        "paper_safe",
        "sign-reversing or orthogonality theorem for evaluated Q_r(1/n)",
        "surface_theorem_target",
        1.25,
        0.35,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_kernel(A,sigma) for relation-kernel classes",
        "conditional_next_attempt",
        "This is the only non-vacuous kernel SPC template, but the required sign theorem is external to current Lemma 3.3.",
    ),
    Mechanism(
        "relation_word_orientation_pairing",
        "pair quotient classes by orientation/opposite traversal of the surface relation",
        "possible orientation sign in evaluated quotient polynomials",
        "x=1/n",
        "paper_safe",
        "orientation-reversal identity changing Q_r(1/n) sign while preserving weights",
        "underdetermined_surface_input",
        1.0,
        0.20,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_kernel orientation-pairing lemma",
        "not_theorem_ready",
        "The paper's folded-quotient construction does not expose an orientation sign; it only requires kernel paths to close.",
    ),
    Mechanism(
        "quotient_polynomial_sign_grouping",
        "group by evaluated Q_{gamma1,gamma2}(1/n) sign inside kernel-compatible quotient profiles",
        "Q_i(1/n) signs",
        "x=1/n",
        "paper_safe",
        "evaluated polynomial sign distribution theorem for relation-compatible W_r",
        "surface_theorem_target",
        1.0,
        0.30,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "SPC_kernel via evaluated quotient-polynomial signs",
        "conditional_next_attempt",
        "This is genuinely pointwise if proved at x=1/n, but current inputs do not supply the sign distribution.",
    ),
    Mechanism(
        "transform_weight_only_sign",
        "kernel strata inherit no sign except external transform factors",
        "(h o f_Lambda0)^vee(k ell_gamma) signs",
        "x=1/n",
        "paper_safe",
        "length-shell transform-phase cancellation after quotient factors are controlled",
        "underdetermined_surface_input",
        0.75,
        0.25,
        0.0,
        True,
        True,
        True,
        False,
        False,
        "belongs to length-shell transform-phase branch",
        "pivot_to_length_phase_if_pursued",
        "If signs come only from transform values, this is not a relation-kernel mechanism.",
    ),
    Mechanism(
        "absolute_kernel_stratum_control",
        "control total mass inside fixed relation-kernel strata",
        "none after absolute values",
        "x=1/n",
        "paper_safe",
        "sum_i |w_i Q_i(1/n)| or coefficient total variation per kernel stratum",
        "coefficient_variation_equivalent",
        2.0,
        0.0,
        0.0,
        True,
        True,
        True,
        True,
        False,
        "coefficient/signed-variation theorem, not SPC_kernel",
        "pivot_to_coefficient_signed_variation",
        "Absolute control may be valuable, but it is no longer signed pointwise cancellation.",
    ),
    Mechanism(
        "x0_kernel_coefficient_cancellation",
        "formal coefficient cancellation near t=0 in kernel-compatible classes",
        "coefficient signs at x=0",
        "x=0",
        "paper_safe_only_after_value_transfer",
        "neighborhood/value argument transferring x=0 control to x=1/n",
        "range_blocked",
        1.5,
        0.0,
        0.0,
        True,
        False,
        True,
        False,
        False,
        "wrong-point unless upgraded to value control",
        "blocked_wrong_point",
        "The target is Q_i(1/n)/Q_id(1/n), so x=0 coefficient cancellation alone is vacuous.",
    ),
    Mechanism(
        "denominator_loss_kernel_grouping",
        "kernel grouping outside the paper-safe Q_id(1/n) regime",
        "Q_i(1/n) signs possibly amplified by 1/Q_id(1/n)",
        "x=1/n",
        "near_zero_or_off_range",
        "|Q_id(1/n)|^{-1} <= n^D with D paid in beta",
        "denominator_blocked",
        1.25,
        0.35,
        1.0,
        True,
        True,
        False,
        False,
        False,
        "SPC_kernel only if denominator loss is explicitly paid",
        "blocked_by_denominator_loss",
        "Any numerator saving is reduced by D; near zeros erase the direct route.",
    ),
    Mechanism(
        "toy_free_group_kernel_proxy",
        "replace the surface kernel by a free-group or Schreier proxy",
        "toy pairing signs",
        "not_the_surface_ratio",
        "no_Q_id_surface_denominator",
        "actual Lemma 3.3 surface relation and denominator normalization",
        "toy_only",
        1.0,
        0.20,
        0.0,
        False,
        False,
        False,
        False,
        True,
        "not theorem evidence for Kim--Tao surface numerator",
        "do_not_use_as_evidence",
        "Free-group/Schreier proxies omit the surface relation, MPvH/Nau inputs, and Q_id normalization.",
    ),
]


SCHEMA_ROWS = [
    {
        "stage": "1",
        "paper_object": "C_{gamma1,gamma2}",
        "lemma_location": "Lemma 3.3 step 1",
        "kernel_condition_role": "source graph is mapped onto folded quotients",
        "feeds": "surjective folded morphisms r: C -> W_r",
        "sign_information": "none",
    },
    {
        "stage": "2",
        "paper_object": "W_r",
        "lemma_location": "Lemma 3.3 step 1",
        "kernel_condition_role": "every W_r path spelling ker(F_{2g}->Gamma) is closed",
        "feeds": "admissible quotient family R",
        "sign_information": "admissibility only",
    },
    {
        "stage": "3",
        "paper_object": "E_emb_n(W_r)",
        "lemma_location": "Lemma 3.3 steps 2-3",
        "kernel_condition_role": "factor C -> W_r -> X_phi and count injective embeddings",
        "feeds": "polynomials p_r(n), summed p_{gamma1,gamma2}(n)",
        "sign_information": "not exposed by kernel closure",
    },
    {
        "stage": "4",
        "paper_object": "Q_{gamma1,gamma2}(t)",
        "lemma_location": "Lemma 3.3 step 4",
        "kernel_condition_role": "all admissible W_r contributions are absorbed into numerator polynomial",
        "feeds": "Q_{gamma1,gamma2}(1/n)/Q_id(1/n)",
        "sign_information": "possible evaluated signs, but no paper theorem groups them",
    },
    {
        "stage": "5",
        "paper_object": "Corollary 3.4 p(1/n)/Q_id(1/n)",
        "lemma_location": "Corollary 3.4",
        "kernel_condition_role": "applies after inserting gamma_i^k_i into Lemma 3.3",
        "feeds": "weighted surface numerator with Selberg/transform weights",
        "sign_information": "only transform and evaluated Q_i signs remain",
    },
]


def ensure_dirs() -> None:
    for path in (DATA, FIGS, DOCS, REPORTS):
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def classification_rows() -> list[dict[str, object]]:
    rows = []
    for m in MECHANISMS:
        rows.append(
            {
                "mechanism": m.name,
                "kernel_role": m.kernel_role,
                "sign_source": m.sign_source,
                "evaluation_point": m.evaluation_point,
                "denominator_regime": m.denominator_regime,
                "required_input": m.required_input,
                "classification": m.classification,
                "A_offset": m.a_offset,
                "sigma": m.sigma,
                "D": m.d_loss,
                "Lambda0_power": LAMBDA0_POWER,
                "beta_formula": "beta=(2*kappa-A)*eta+sigma-D",
                "paper_native": bool_text(m.paper_native),
                "pointwise_at_x_1_over_n": bool_text(m.pointwise_at_x_1_over_n),
                "denominator_safe": bool_text(m.denominator_safe),
                "requires_absolute_kernel_stratum": bool_text(m.requires_absolute_kernel_stratum),
                "uses_toy_or_free_group_proxy": bool_text(m.uses_toy_or_free_group_proxy),
                "claims_proved_exponent_improvement": "False",
                "claims_local_statistics": "False",
                "claims_variance_law": "False",
                "claims_shrinking_window_theorem": "False",
                "theorem_template": m.theorem_template,
                "decision": m.decision,
                "reason": m.reason,
            }
        )
    return rows


def beta_rows() -> list[dict[str, object]]:
    rows = []
    for m in MECHANISMS:
        for kappa in KAPPA_VALUES:
            for eta in ETA_VALUES:
                for denom_loss in DENOMINATOR_LOSSES:
                    beta = m.beta(kappa, eta, denom_loss)
                    rows.append(
                        {
                            "mechanism": m.name,
                            "classification": m.classification,
                            "kappa": kappa,
                            "eta": eta,
                            "A": m.a_value(kappa),
                            "A_offset": m.a_offset,
                            "sigma": m.sigma,
                            "D": denom_loss,
                            "beta": beta,
                            "beta_formula": "beta=(2*kappa-A)*eta+sigma-D",
                            "grouped_variance_exponent": 1.0 + 2.0 * kappa * eta - beta,
                            "denominator_safe_regime": bool_text(denom_loss == 0.0 and m.denominator_safe),
                            "saving_survives_denominator": bool_text(beta > 0.0),
                            "theorem_ready_spc_kernel": bool_text(
                                m.classification == "surface_theorem_target"
                                and m.pointwise_at_x_1_over_n
                                and denom_loss == 0.0
                            ),
                            "coefficient_variation_equivalent": bool_text(
                                m.classification == "coefficient_variation_equivalent"
                            ),
                            "near_zero_denominator_obstruction": bool_text(
                                m.classification == "denominator_blocked" or denom_loss > 0.0
                            ),
                        }
                    )
    return rows


def pivot_rows() -> list[dict[str, object]]:
    return [
        {
            "decision": "kernel_spc_not_currently_theorem_ready",
            "status": "validated_decision",
            "evidence": "Lemma 3.3 kernel closure defines admissible folded quotients and embedding counts; it does not supply a sign-pairing theorem.",
            "next_target": "surface_numerator_coefficient_signed_variation_first_attack",
            "pivot_rule": "If proof requires sum_i |w_i Q_i(1/n)| or total variation inside fixed kernel strata, pivot to coefficient/signed variation.",
        },
        {
            "decision": "conditional_spc_kernel_template_preserved",
            "status": "conditional_only",
            "evidence": "A non-vacuous template exists only for evaluated Q_i(1/n) sign cancellation across relation-kernel classes.",
            "next_target": "only pursue if a new surface relation sign theorem is available",
            "pivot_rule": "Do not count smaller admissible quotient family size as signed cancellation.",
        },
        {
            "decision": "length_phase_branch_secondary",
            "status": "weaker_fallback",
            "evidence": "If signs come only from transform weights, the mechanism belongs to length-shell phase grouping, not relation-kernel closure.",
            "next_target": "transform_phase_length_shell_spc_probe only after coefficient route triage",
            "pivot_rule": "Require quotient-polynomial signs to remain controlled after transform phase grouping.",
        },
    ]


def write_docs() -> None:
    proof = """---
created: 2026-05-17T01:30:00Z
cycle: 50
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M39-surface-relation-kernel-spc-probe
---

# Surface-Relation Kernel SPC Probe

## Lemma 3.3 Reconstruction

Kim--Tao Lemma 3.3 starts with the two-cycle labelled graph
`C_{gamma1,gamma2}` built from cyclically reduced words for `gamma1` and
`gamma2`.  The quotient family `R` consists of surjective labelled-graph
morphisms `r: C_{gamma1,gamma2} -> W_r` such that `W_r` is folded and every
path in `W_r` spelling an element of `ker(F_{2g} -> Gamma)` is closed.

That condition enters before any polynomial is evaluated.  It defines the
admissible folded targets `W_r`; each morphism into a Schreier graph factors
uniquely as `C_{gamma1,gamma2} -> W_r -> X_phi`, and the expectation becomes
`sum_{r in R} E_emb_n(W_r)`.  MPvH/Nau inputs then express each embedding
expectation through a polynomial contribution `p_r(n)`, these contributions
sum to `p_{gamma1,gamma2}(n)`, and the reciprocal variable `t=1/n` conversion
produces `Q_{gamma1,gamma2}(t)/Q_id(t)`.

## Consequence For Corollary 3.4

In Corollary 3.4 the same lemma is applied to `gamma1^k1` and `gamma2^k2`,
giving summands

```text
w(gamma1,k1) w(gamma2,k2)
Q_{gamma1^k1,gamma2^k2}(1/n) / Q_id(1/n).
```

The positive Selberg length/sinh factors do not create signs.  Remaining
signs can come from transform values and from the evaluated quotient
polynomials `Q_i(1/n)`.  Kernel closure is therefore a paper-native label on
admissible quotient classes, but Lemma 3.3 by itself does not identify an
opposite-sign pairing, orthogonality relation, or sign distribution for
`Q_i(1/n)`.

## Candidate Template

A non-vacuous direct target must be evaluated at x=1/n and would have to be:

```text
SPC_kernel(A,sigma):
|sum_{i in G_kernel} w_i Q_i(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)).
```

For `q=n^eta`, denominator loss `|Q_id(1/n)|^{-1} <= n^D` gives

```text
beta = (2*kappa - A)*eta + sigma - D.
```

The Markov baseline is `A=2*kappa`, `sigma=0`, `D=0`, with `Lambda0^20`.

## Decision

The relation-kernel route is not currently theorem-ready.  The honest status
is conditional: `kernel_class_signed_pairing` and
`quotient_polynomial_sign_grouping` are valid theorem templates only if a new
surface theorem supplies evaluated `Q_i(1/n)` sign cancellation inside
relation-compatible quotient classes.

Hard pivot rule: if the proof uses only a smaller admissible family, or if it
requires `sum_i |w_i Q_i(1/n)|` or coefficient total variation inside fixed
kernel strata, the branch is coefficient/signed variation for the actual
surface numerator, not direct signed pointwise cancellation.  If the only
signs used are transform signs, the mechanism belongs to the weaker
length-shell transform-phase branch.
"""
    report = """---
created: 2026-05-17T01:30:00Z
cycle: 50
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M39-surface-relation-kernel-spc-probe
---

# M39 Surface-Relation Kernel SPC Probe

## Result

Decision: `kernel_spc_not_currently_theorem_ready`.

The Lemma 3.3 kernel-closure condition is genuinely paper-native, but in the
paper proof it functions as an admissibility condition for folded quotient
targets `W_r`.  It feeds the embedding expectations `E_emb_n(W_r)` and then
the numerator polynomial `Q_{gamma1,gamma2}`, but the proof does not expose a
sign-pairing or orthogonality mechanism for evaluated values at `x=1/n`.

## Classification

`kernel_class_signed_pairing` and `quotient_polynomial_sign_grouping` remain
conditional `surface_theorem_target` rows because they would be genuine
`SPC_kernel(A,sigma)` statements if proved at the evaluated point.  The
available paper input does not prove them.  `kernel_closure_admissibility` and
`relation_word_orientation_pairing` are underdetermined surface inputs;
`absolute_kernel_stratum_control` is coefficient-variation-equivalent;
`x0_kernel_coefficient_cancellation` is wrong-point; denominator-loss and toy
free-group proxy routes are blocked or toy-only.

## Pivot Recommendation

The next honest target is
`surface_numerator_coefficient_signed_variation_first_attack`.  Continue the
direct kernel SPC branch only if a new Lemma 3.3-level input can prove
evaluated `Q_i(1/n)` cancellation across relation-kernel classes without
absolute kernel-stratum control.

![how Lemma 3.3 kernel closure feeds from folded quotients to `Q_{gamma1,gamma2}(1/n)`](../figures/m39_kernel_constraint_flow.png)

![classification of relation-kernel grouping mechanisms by theorem readiness and obstruction](../figures/m39_kernel_spc_decision_map.png)

![beta budget for candidate `SPC_kernel(A,sigma)` rows under safe and lossy denominator regimes](../figures/m39_kernel_beta_budget.png)
"""
    PROOF_LEDGER.write_text(proof)
    REPORT.write_text(report)


def plot_flow() -> None:
    rows = SCHEMA_ROWS
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    y_positions = list(reversed(range(len(rows))))
    for i, (row, y) in enumerate(zip(rows, y_positions)):
        ax.text(
            0.02,
            y,
            f"{row['stage']}. {row['paper_object']}\n{row['kernel_condition_role']}\nfeeds: {row['feeds']}",
            va="center",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#eef3f7", edgecolor="#4a6678"),
            fontsize=9,
        )
        if i < len(rows) - 1:
            ax.annotate(
                "",
                xy=(0.50, y - 0.55),
                xytext=(0.50, y - 0.15),
                arrowprops=dict(arrowstyle="->", color="#4a6678", lw=1.5),
            )
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_title("Lemma 3.3 kernel closure: admissibility to evaluated quotient polynomial")
    fig.tight_layout()
    fig.savefig(FLOW_FIG, dpi=180)
    plt.close(fig)


def plot_decision_map() -> None:
    classes = [
        "paper_proved_baseline",
        "surface_theorem_target",
        "underdetermined_surface_input",
        "coefficient_variation_equivalent",
        "range_blocked",
        "denominator_blocked",
        "toy_only",
    ]
    counts = {c: 0 for c in classes}
    for m in MECHANISMS:
        counts[m.classification] += 1
    colors = ["#5b6f95", "#4c8f7a", "#d3a23f", "#9b6b9e", "#c76655", "#a84848", "#777777"]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(range(len(classes)), [counts[c] for c in classes], color=colors)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=30, ha="right")
    ax.set_ylabel("mechanism count")
    ax.set_title("Relation-kernel SPC mechanism classification")
    for idx, c in enumerate(classes):
        ax.text(idx, counts[c] + 0.05, str(counts[c]), ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(MAP_FIG, dpi=180)
    plt.close(fig)


def plot_beta_budget() -> None:
    selected = [
        m
        for m in MECHANISMS
        if m.name
        in {
            "kernel_class_signed_pairing",
            "quotient_polynomial_sign_grouping",
            "absolute_kernel_stratum_control",
            "denominator_loss_kernel_grouping",
        }
    ]
    losses = [0.0, 0.25, 0.5, 1.0]
    eta = 0.08
    kappa = 5.0
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    width = 0.18
    x_base = list(range(len(losses)))
    for offset, m in enumerate(selected):
        values = [m.beta(kappa, eta, d) for d in losses]
        xs = [x + (offset - 1.5) * width for x in x_base]
        ax.bar(xs, values, width=width, label=m.name)
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x_base)
    ax.set_xticklabels([f"D={d:g}" for d in losses])
    ax.set_ylabel("beta at kappa=5, eta=0.08")
    ax.set_title("SPC_kernel beta budget under denominator loss")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(BETA_FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    write_csv(SCHEMA_CSV, SCHEMA_ROWS)
    write_csv(CLASSIFICATION_CSV, classification_rows())
    write_csv(BETA_CSV, beta_rows())
    write_csv(PIVOT_CSV, pivot_rows())
    write_docs()
    plot_flow()
    plot_decision_map()
    plot_beta_budget()
    print(f"wrote {SCHEMA_CSV.relative_to(ROOT)} ({len(SCHEMA_ROWS)} rows)")
    print(f"wrote {CLASSIFICATION_CSV.relative_to(ROOT)} ({len(MECHANISMS)} rows)")
    print(f"wrote {BETA_CSV.relative_to(ROOT)} ({len(beta_rows())} rows)")
    print(f"wrote {PIVOT_CSV.relative_to(ROOT)} ({len(pivot_rows())} rows)")
    print(f"wrote {FLOW_FIG.relative_to(ROOT)}")
    print(f"wrote {MAP_FIG.relative_to(ROOT)}")
    print(f"wrote {BETA_FIG.relative_to(ROOT)}")
    print("decision=kernel_spc_not_currently_theorem_ready")
    print("pivot_rule=pivot_to_coefficient_signed_variation_if_absolute_kernel_stratum_control_is_required")


if __name__ == "__main__":
    main()
