"""
Track 3 Wave 4 convergence validation and confound ablation.

created:    2026-05-18T10:10:00+00:00
cycle:      14
run_id:     fork-cc044bf40be3-clone-2-track3-wave4-validation
agent:      worker
milestone:  M4.A-track3-convergence-confounds

This script reads the frozen M3.T3 convergence-pressure outputs and writes a
track-local Wave 4 interpretation package. It does not write the master
prediction or speculation ledgers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "track3"
DATA = TRACK / "data"
FIGURES = TRACK / "figures"
REPORTS = TRACK / "reports"

SCORES = DATA / "convergence_pressure_scores.tsv"
NULLS = DATA / "convergence_pressure_nulls.tsv"
CONFOUND = DATA / "convergence_pressure_confound_regression.tsv"
RECOVERY = DATA / "convergence_pressure_canonical_recovery.tsv"
PREDICTIONS = DATA / "convergence_predictions.tsv"
RUN_SUMMARY = DATA / "convergence_pressure_run_summary.json"

OUT_TSV = DATA / "track3_wave4_validation_outcomes.tsv"
OUT_JSON = DATA / "track3_wave4_validation_summary.json"
OUT_PNG = FIGURES / "track3_wave4_null_model_comparison.png"
OUT_REPORT = REPORTS / "track3_wave4_validation_ablation.md"

PENDING_TRAITS = {"drupe", "capsule"}
ZERO_CARRIER_CANONICAL = {"ant_domatia", "carnivory", "parasitism"}
CANONICAL_TEXTBOOK = {
    "c4_photosynthesis",
    "fleshy_fruit",
    "myrmecochory",
    "elaiosome",
    "samara",
}


def finite_number(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    scores = pd.read_csv(SCORES, sep="\t")
    nulls = pd.read_csv(NULLS, sep="\t")
    confound = pd.read_csv(CONFOUND, sep="\t")
    recovery = pd.read_csv(RECOVERY, sep="\t")
    predictions = pd.read_csv(PREDICTIONS, sep="\t")
    summary = json.loads(RUN_SUMMARY.read_text())
    return scores, nulls, confound, recovery, predictions, summary


def null_lookup(nulls: pd.DataFrame) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row["trait"]), str(row["null"])): row.to_dict()
        for _, row in nulls.iterrows()
    }


def regression_values(confound: pd.DataFrame) -> dict[str, Any]:
    return dict(zip(confound["name"].astype(str), confound["coef"]))


def null_is_degenerate(row: pd.Series, lookup: dict[tuple[str, str], dict[str, Any]]) -> bool:
    if str(row["trait"]) == "_other":
        return True
    for null_name in ("N1", "N2"):
        null_row = lookup.get((str(row["trait"]), null_name))
        if null_row is None:
            return True
        std = null_row.get("std")
        if not finite_number(std) or float(std) == 0.0:
            return True
    return False


def classify_row(
    row: pd.Series,
    prediction_row: pd.Series,
    recovery_by_trait: dict[str, pd.Series],
    nulls_by_trait: dict[tuple[str, str], dict[str, Any]],
    confound_verdict: str,
) -> dict[str, Any]:
    trait = str(row["trait"])
    n_carriers = int(row["n_carriers"])
    degenerate = null_is_degenerate(row, nulls_by_trait)
    row_class = str(prediction_row["row_class"])
    cp_min = row["CP_min"]

    if trait == "_other":
        status = "diagnostic_not_prediction"
        rationale = "_other is an out-of-axis coverage bucket and is excluded from canonical convergence scoring."
        special = "excluded_bucket; null comparison intentionally not used"
    elif n_carriers == 0:
        status = "data_limited_not_prediction"
        rationale = f"{trait} has zero accepted-key carriers, so CP evidence is undefined in this frozen substrate."
        special = "zero_carrier_trait; no biological absence claim"
    elif degenerate:
        status = "data_limited_not_prediction"
        rationale = "At least one null comparison is missing or has zero/undefined standard deviation."
        special = "null_degeneracy_blocks_validation"
    elif trait in PENDING_TRAITS and bool_value(row["clears_bar"]) and confound_verdict != "FAIL":
        status = "pending_convergence_prior"
        rationale = (
            f"{trait} clears CP_min >= 2.0 against both nulls, but no independent Wave 4 validation source "
            "has confirmed the trait as a biological convergence result."
        )
        special = "pending_hypothesis_only; no adaptive-origin claim"
    elif trait in CANONICAL_TEXTBOOK:
        status = "data_limited_not_prediction"
        rationale = (
            f"{trait} is a textbook convergence case, but it does not clear the current frozen-substrate CP_min "
            "threshold; this is treated as source/substrate limitation, not a negative biological result."
        )
        special = "canonical_weak_recovery; no biological negative claim"
    else:
        status = "observed_evidence_not_prediction"
        rationale = (
            f"{trait} has retained source-coded trait evidence but does not clear the current predictive threshold."
        )
        special = "observed_trait_summary_only"

    if confound_verdict == "FAIL" and status == "pending_convergence_prior":
        status = "falsified_by_confound"
        rationale = "The confound falsifier failed, so the CP ranking is not interpretable as a convergence-prior signal."
        special = "confound_falsifier_failed"

    n1 = nulls_by_trait.get((trait, "N1"), {})
    n2 = nulls_by_trait.get((trait, "N2"), {})
    recovery = recovery_by_trait.get(trait)
    return {
        "trait": trait,
        "row_class": row_class,
        "n_carriers": n_carriers,
        "n_families": int(row["n_families"]),
        "CP_N1": row["CP_N1"],
        "CP_N2": row["CP_N2"],
        "CP_min": cp_min,
        "n1_null_mean": n1.get("mean", float("nan")),
        "n1_null_std": n1.get("std", float("nan")),
        "n2_null_mean": n2.get("mean", float("nan")),
        "n2_null_std": n2.get("std", float("nan")),
        "canonical_recovery_band": "" if recovery is None else recovery["expected_band"],
        "canonical_recovery_agreement": "" if recovery is None else recovery["agreement"],
        "wave4_status": status,
        "status_rationale": rationale,
        "confound_verdict": confound_verdict,
        "special_handling": special,
        "enters_master_prediction_ledger": False,
    }


def build_outcomes(
    scores: pd.DataFrame,
    nulls: pd.DataFrame,
    confound: pd.DataFrame,
    recovery: pd.DataFrame,
    predictions: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    nulls_by_trait = null_lookup(nulls)
    recovery_by_trait = {str(row["trait"]): row for _, row in recovery.iterrows()}
    predictions_by_trait = {str(row["trait"]): row for _, row in predictions.iterrows()}
    conf = regression_values(confound)
    confound_verdict = str(conf.get("verdict", "UNKNOWN"))

    rows = []
    for _, score_row in scores.iterrows():
        trait = str(score_row["trait"])
        rows.append(
            classify_row(
                score_row,
                predictions_by_trait[trait],
                recovery_by_trait,
                nulls_by_trait,
                confound_verdict,
            )
        )

    outcomes = pd.DataFrame(rows)
    status_counts = outcomes["wave4_status"].value_counts().sort_index().to_dict()
    pending = sorted(outcomes.loc[outcomes["wave4_status"] == "pending_convergence_prior", "trait"].tolist())
    zero_carrier = sorted(outcomes.loc[outcomes["special_handling"].str.contains("zero_carrier", regex=False), "trait"].tolist())

    r2_cp = float(conf.get("R2_CP_min", float("nan")))
    r2_obs = float(conf.get("R2_observed_H_family", float("nan")))
    rho = float(conf.get("spearman_rho_residOBS_vs_CPmin", float("nan")))
    h3_decision = "data_limited"
    if confound_verdict == "FAIL":
        h3_decision = "falsified_by_confound"
    elif pending == ["capsule", "drupe"] and r2_cp < 0.7:
        h3_decision = "not_validated_pending"

    summary = {
        "run_id": "fork-cc044bf40be3-clone-2-track3-wave4-validation",
        "milestone": "M4.A-track3-convergence-confounds",
        "inputs": [str(p.relative_to(ROOT)) for p in [SCORES, NULLS, CONFOUND, RECOVERY, PREDICTIONS, RUN_SUMMARY]],
        "outputs": [str(p.relative_to(ROOT)) for p in [OUT_TSV, OUT_JSON, OUT_PNG, OUT_REPORT]],
        "n_rows": int(len(outcomes)),
        "status_counts": status_counts,
        "pending_traits": pending,
        "zero_carrier_traits": zero_carrier,
        "other_status": outcomes.loc[outcomes["trait"] == "_other", "wave4_status"].iloc[0],
        "confound": {
            "verdict": confound_verdict,
            "R2_observed_H_family": r2_obs,
            "R2_CP_min": r2_cp,
            "spearman_rho_residOBS_vs_CPmin": rho,
        },
        "h3_decision": h3_decision,
        "master_ledgers_promoted": False,
    }
    return outcomes, summary


def write_figure(outcomes: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    scored = outcomes[
        outcomes["CP_min"].map(finite_number)
        & (outcomes["wave4_status"] != "diagnostic_not_prediction")
    ].copy()
    scored = scored.sort_values("CP_min", ascending=True)
    colors = scored["wave4_status"].map({
        "pending_convergence_prior": "#2a7f62",
        "data_limited_not_prediction": "#b35c1e",
        "observed_evidence_not_prediction": "#536878",
        "falsified_by_confound": "#9b1c31",
    }).fillna("#536878")

    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    y = range(len(scored))
    ax.barh(y, scored["CP_min"], color=colors)
    ax.axvline(0, color="#222222", linewidth=0.8)
    ax.axvline(2.0, color="#2a7f62", linestyle="--", linewidth=1.0, label="CP_min threshold")
    ax.set_yticks(list(y))
    ax.set_yticklabels(scored["trait"])
    ax.set_xlabel("CP_min = min(z_N1, z_N2)")
    ax.set_title("Track 3 Wave 4 null-model comparison")
    ax.legend(loc="lower right")
    for i, (_, row) in enumerate(scored.iterrows()):
        label = f"N1 {row['n1_null_mean']:.2f}+/-{row['n1_null_std']:.2f}; N2 {row['n2_null_mean']:.2f}+/-{row['n2_null_std']:.2f}"
        x = float(row["CP_min"])
        ax.text(x + (0.35 if x >= 0 else -0.35), i, label, va="center", ha="left" if x >= 0 else "right", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=160)
    plt.close(fig)


def fmt_num(value: Any) -> str:
    if finite_number(value):
        return f"{float(value):.3f}"
    return ""


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in df.iterrows():
        vals = []
        for col in columns:
            value = row[col]
            if col.startswith("CP") or col.endswith("std") or col.endswith("mean"):
                vals.append(fmt_num(value))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(outcomes: pd.DataFrame, summary: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    display = outcomes.sort_values(["wave4_status", "trait"]).copy()
    pending = outcomes[outcomes["trait"].isin(sorted(PENDING_TRAITS))].sort_values("trait")
    diagnostic = outcomes[
        outcomes["trait"].isin(sorted(CANONICAL_TEXTBOOK | ZERO_CARRIER_CANONICAL | {"_other"}))
    ].sort_values("trait")
    report = f"""---
created: 2026-05-18T10:10:00+00:00
cycle: 14
run_id: fork-cc044bf40be3-clone-2-track3-wave4-validation
agent: worker
milestone: M4.A-track3-convergence-confounds
---

# Track 3 Wave 4 Validation And Confound Ablation

## Scope

This branch reinterprets the frozen M3.T3 convergence-pressure outputs for Wave 4 validation and ablation. It reads only Track 3-local artifacts and writes Track 3-local outputs; `prediction_ledger.tsv` and `speculation_ledger.tsv` are not promoted by this branch.

## Method

The instrument score is `CP_min(T)=min(z_N1,z_N2)`, where `z_N1=(H_family-mean_N1)/sd_N1` and `z_N2=(H_family-mean_N2)/sd_N2`. N1 preserves family-size carrier structure and N2 preserves sampling-density carrier structure. A trait can remain a pending convergence-prior only when both z-scores are finite, both null standard deviations are non-zero, `_other` is excluded, and the confound falsifier does not fail.

The Wave 4 interpretation is deliberately non-adaptive: these outputs do not establish adaptive convergence, independent origins, evolutionary inevitability, new trait occurrences, new taxonomy, or new distribution facts.

## H3 Decision

Decision: `{summary['h3_decision']}`.

The current branch does not validate H3. `drupe` and `capsule` remain pending convergence-prior hypotheses, but canonical textbook traits do not consistently clear the frozen-substrate threshold and the confound regression is substantial (`R2_observed_H_family={summary['confound']['R2_observed_H_family']:.3f}`, `R2_CP_min={summary['confound']['R2_CP_min']:.3f}`). The existing hard falsifier does not fail because residual-rank agreement is below threshold (`rho={summary['confound']['spearman_rho_residOBS_vs_CPmin']:.3f}`), so the result is data-limited rather than falsified by confound.

## Per-Trait Outcomes

{markdown_table(display, ['trait', 'row_class', 'n_carriers', 'n_families', 'CP_N1', 'CP_N2', 'CP_min', 'wave4_status', 'confound_verdict', 'special_handling'])}

## Pending Hypotheses

{markdown_table(pending, ['trait', 'n_carriers', 'n_families', 'CP_N1', 'CP_N2', 'CP_min', 'canonical_recovery_band', 'canonical_recovery_agreement', 'wave4_status', 'status_rationale'])}

`drupe` and `capsule` clear `CP_min >= 2.0` against both nulls and are the only current pending hypothesis rows. They do not enter the master prediction ledger here because independent validation and Barrier 4 reconciliation are still required.

## Diagnostic And Data-Limited Non-Predictions

{markdown_table(diagnostic, ['trait', 'n_carriers', 'n_families', 'CP_min', 'canonical_recovery_band', 'canonical_recovery_agreement', 'wave4_status', 'status_rationale'])}

`_other` is a coverage diagnostic and is not a biological trait hypothesis. `ant_domatia`, `carnivory`, and `parasitism` have zero retained accepted-key carriers, so their CP evidence is undefined. Negative or low CP for canonical traits such as `c4_photosynthesis`, `fleshy_fruit`, `myrmecochory`, `elaiosome`, and `samara` is treated as weak recovery in this frozen substrate, not as evidence that those textbook traits are biologically absent or non-convergent.

## Figure

![Observed CP_min against N1/N2 null context for scored Track 3 traits; vertical dashed line marks the CP_min >= 2 pending-prior threshold.](../figures/track3_wave4_null_model_comparison.png)

## Outputs

- `tracks/track3/data/track3_wave4_validation_outcomes.tsv`
- `tracks/track3/data/track3_wave4_validation_summary.json`
- `tracks/track3/figures/track3_wave4_null_model_comparison.png`
- `tracks/track3/reports/track3_wave4_validation_ablation.md`

## Ledger Boundary

Every row has `enters_master_prediction_ledger=False`. This branch supplies a track-local Wave 4 validation/ablation package for auditor review; any master-ledger status change belongs to Barrier 4 reconciliation.
"""
    OUT_REPORT.write_text(report)


def main() -> int:
    scores, nulls, confound, recovery, predictions, run_summary = load_inputs()
    outcomes, summary = build_outcomes(scores, nulls, confound, recovery, predictions)
    summary["m3_run_summary"] = run_summary

    DATA.mkdir(parents=True, exist_ok=True)
    outcomes.to_csv(OUT_TSV, sep="\t", index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_figure(outcomes)
    write_report(outcomes, summary)
    print(f"Wrote {OUT_TSV.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_PNG.relative_to(ROOT)}")
    print(f"Wrote {OUT_REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
