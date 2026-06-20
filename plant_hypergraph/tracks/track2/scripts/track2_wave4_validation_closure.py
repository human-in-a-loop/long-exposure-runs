#!/usr/bin/env python3
"""Build Track 2 Wave 4 held-out validation closure artifacts.

This script summarizes existing Track 2 validation and ablation outputs. It
does not re-score candidates, fetch new evidence, or promote master-ledger
claims.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "track2"
DATA = TRACK / "data"
FIGURES = TRACK / "figures"
REPORTS = TRACK / "reports"

VALIDATION_PATH = DATA / "ghost_partner_validation_scores.tsv"
ABLATION_PATH = DATA / "ghost_partner_ablation_results.tsv"
PREDICTIONS_PATH = DATA / "ghost_partner_predictions.tsv"
OUTCOMES_PATH = DATA / "track2_wave4_validation_outcomes.tsv"
FIGURE_PATH = FIGURES / "track2_wave4_validation_ablation.png"
REPORT_PATH = REPORTS / "track2_wave4_validation_closure.md"

HELDOUT_CANON = [
    "Persea americana",
    "Maclura pomifera",
    "Gleditsia triacanthos",
    "Annona cherimola",
    "Mauritia flexuosa",
    "Spondias mombin",
    "Sideroxylon foetidissimum",
    "Asimina triloba",
]


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t").fillna("")


def final_status(row: pd.Series) -> str:
    if row["validation_class"] == "data_limited":
        return "data_limited"
    if row["validation_class"] == "insufficient_support":
        return "insufficient_support"
    if row["ablation_outcome"] == "falsified_by_ablation":
        return "falsified"
    if row["validation_class"] == "validation_ready":
        return "pending"
    if row["validation_class"] == "not_recovered":
        return "falsified"
    return "pending"


def blocking_controls(row: pd.Series) -> str:
    controls: list[str] = []
    if row["accepted_key_status"] == "accepted_key_absent":
        controls.append("accepted_key_absent")
    if row["modern_failure_evidence_status"] != "seed_modern_failure_present":
        controls.append("modern_failure_missing")
    if bool(row["source_singleton"]):
        controls.append("singleton_source")
    if bool(row["living_megafauna_ambiguity"]):
        controls.append("living_megafauna_ambiguity")
    if row["ablation_outcome"] == "falsified_by_ablation":
        controls.append("ablation_fragile")
    return "|".join(controls) if controls else "none"


def closure_reason(row: pd.Series) -> str:
    status = row["wave4_outcome_status"]
    if status == "data_limited":
        if row["accepted_key_status"] == "accepted_key_absent":
            return "cannot validate held-out recovery without accepted focal taxon key"
        return "candidate support remains data-limited under living-megafauna or evidence-scope controls"
    if status == "insufficient_support":
        return "accepted key is present or recoverable but modern-failure support is absent or morphology-only"
    if status == "falsified":
        return "pre-ablation validation-ready status does not survive singleton/source-class controls"
    if status == "pending":
        return "validation-ready under local rules but still requires independent external validation"
    return "pending adjudication"


def build_outcomes(validation: pd.DataFrame) -> pd.DataFrame:
    out = validation.copy()
    out["wave4_outcome_status"] = out.apply(final_status, axis=1)
    out["blocking_controls"] = out.apply(blocking_controls, axis=1)
    out["closure_reason"] = out.apply(closure_reason, axis=1)
    out["validation_protocol"] = (
        "held-out Janzen-Martin scaffold checked against accepted-key, "
        "modern-failure, singleton-source, source-class, and living-megafauna controls"
    )
    out["claim_scope"] = "track-local validation scaffold only; no established anachronism claim"
    out["enters_master_prediction_ledger"] = False
    columns = [
        "heldout_scientific_name",
        "common_name",
        "candidate_id",
        "best_rank",
        "candidate_score",
        "accepted_key_status",
        "modern_failure_evidence_status",
        "source_singleton",
        "living_megafauna_ambiguity",
        "validation_class",
        "ablation_outcome",
        "wave4_outcome_status",
        "blocking_controls",
        "closure_reason",
        "validation_protocol",
        "claim_scope",
        "inferred_anachronism_claim",
        "enters_master_prediction_ledger",
    ]
    return out[columns]


def write_figure(outcomes: pd.DataFrame, ablations: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    status_counts = outcomes["wave4_outcome_status"].value_counts().reindex(
        ["validated", "pending", "falsified", "data_limited", "insufficient_support"],
        fill_value=0,
    )
    ablation_plot = ablations.set_index("ablation")[
        ["pending_validation_count", "heldout_validation_ready"]
    ]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    status_counts.plot(kind="bar", ax=axes[0], color=["#4878a8", "#5f9e6e", "#b55d60", "#d19a3a", "#7a6aa8"])
    axes[0].set_title("Held-out final status")
    axes[0].set_ylabel("Held-out cases")
    axes[0].set_xlabel("Wave 4 outcome")
    axes[0].tick_params(axis="x", labelrotation=25)

    ablation_plot.plot(kind="bar", ax=axes[1], width=0.82, color=["#4f6f8f", "#c77c43"])
    axes[1].set_title("Ablation survival")
    axes[1].set_ylabel("Rows")
    axes[1].set_xlabel("Ablation")
    axes[1].tick_params(axis="x", labelrotation=35)
    axes[1].legend(fontsize=8)

    fig.suptitle("Track 2 held-out validation closure under evidence controls", fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=160)
    plt.close()


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df[columns].itertuples(index=False):
        cells = [str(value).replace("|", "<br>") for value in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def status_sentence(outcomes: pd.DataFrame) -> str:
    counts = outcomes["wave4_outcome_status"].value_counts().to_dict()
    parts = [
        f"{counts.get('validated', 0)} validated",
        f"{counts.get('pending', 0)} pending",
        f"{counts.get('falsified', 0)} falsified",
        f"{counts.get('data_limited', 0)} data-limited",
        f"{counts.get('insufficient_support', 0)} insufficient-support",
    ]
    return ", ".join(parts)


def write_report(outcomes: pd.DataFrame, ablations: pd.DataFrame) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    singleton = ablations[ablations["ablation"].eq("remove_singleton_source_rows")].iloc[0]
    normalized = ablations[ablations["ablation"].eq("source_count_candidate_class_normalized")].iloc[0]
    no_modern = ablations[ablations["ablation"].eq("remove_modern_failure_component")].iloc[0]
    text = f"""---
created: 2026-05-18T10:20:00+00:00
cycle: 14
run_id: fork-cc044bf40be3-clone-0-track2-wave4-closure
agent: worker-clone-0
milestone: M4.V2
---

# Track 2 Wave 4 Validation Closure

## Scope

This closure package adjudicates the existing Track 2 held-out Janzen-Martin
validation scaffold under the frozen M3.T2 Ghost-Partner Candidate Ranker. It
does not refit the ranker, fetch new literature, infer new ecological history,
or write the master `prediction_ledger.tsv` or `speculation_ledger.tsv`.

## Decision

No held-out Janzen-Martin case is validated by the current frozen evidence
package. The final held-out disposition is: {status_sentence(outcomes)}.

The branch therefore closes M4.V2 as a track-local null/data-limited validation
result: H2 is not supported at the requested 30% canonical recovery threshold
under current accepted-key and ablation controls.

## Held-Out Outcomes

{markdown_table(outcomes, [
    "heldout_scientific_name",
    "candidate_id",
    "best_rank",
    "accepted_key_status",
    "modern_failure_evidence_status",
    "ablation_outcome",
    "wave4_outcome_status",
    "blocking_controls",
])}

## Mechanism Finding

The ranker can nominate a case only when cited morphology/extinct-partner
support is present, but validation requires stronger conditions: an accepted
focal taxon key, explicit modern dispersal-failure support, and survival under
source and living-megafauna controls. Six held-out cases remain data-limited,
one is insufficient-support, and the only pre-ablation validation-ready case
(`Asimina triloba`) is falsified by source/singleton ablation.

Special points:

- Missing accepted key: candidate is data-limited, not a failed biological
  hypothesis.
- Modern-failure support equal to zero: morphology-only cases are capped at
  insufficient support.
- Singleton-source support: current candidate layer collapses when singleton
  rows are removed.
- Living-megafauna ambiguity: ghost-partner interpretation is penalized and
  cannot validate a case.

## Ablation Summary

{markdown_table(ablations, [
    "ablation",
    "candidate_rows",
    "pending_validation_count",
    "heldout_validation_ready",
    "mean_score_delta_vs_baseline",
])}

The singleton-source ablation leaves `{int(singleton.candidate_rows)}` candidate
rows and `{int(singleton.heldout_validation_ready)}` validation-ready held-out
rows. Source/class normalization leaves `{int(normalized.heldout_validation_ready)}`
validation-ready held-out rows. Removing the modern-failure component leaves
`{int(no_modern.pending_validation_count)}` pending-validation rows. These
controls rule out a validated H2 recovery result in the current substrate.

![Held-out status counts and ablation survival under singleton-source, source-class, accepted-key, and modern-failure controls.](../figures/track2_wave4_validation_ablation.png)

## Guardrails

All rows are track-local validation outcomes. `inferred_anachronism_claim` is
false for every row and `enters_master_prediction_ledger` is false for every
row. A `falsified` outcome here means falsified as a Wave 4 validation-ready
recovery under the stated controls, not proof that a biological anachronism is
absent.

## Reopen Conditions

Reopen Track 2 validation only when at least one of these changes is available:

- accepted-key repair for currently absent canonical held-out taxa;
- independent modern dispersal-failure evidence beyond the seed citation;
- non-singleton source support for candidate plant-extinct-fauna pairs;
- an explicit living-megafauna contrast that separates current dispersal from
  ghost-megafauna interpretation.
"""
    REPORT_PATH.write_text(text)


def assert_master_ledgers_header_only() -> None:
    for name in ["prediction_ledger.tsv", "speculation_ledger.tsv"]:
        path = ROOT / name
        lines = [line for line in path.read_text().splitlines() if line.strip()]
        if len(lines) != 1:
            raise AssertionError(f"{name} must remain header-only, found {len(lines)} nonblank lines")


def build() -> dict[str, int]:
    validation = read_tsv(VALIDATION_PATH)
    ablations = read_tsv(ABLATION_PATH)
    predictions = read_tsv(PREDICTIONS_PATH)

    outcomes = build_outcomes(validation)
    missing = set(HELDOUT_CANON) - set(outcomes["heldout_scientific_name"])
    if missing:
        raise AssertionError(f"missing held-out outcomes: {sorted(missing)}")
    if predictions["enters_master_prediction_ledger"].astype(str).str.lower().ne("false").any():
        raise AssertionError("Track 2 prediction rows must not enter master prediction ledger")

    OUTCOMES_PATH.parent.mkdir(parents=True, exist_ok=True)
    outcomes.to_csv(OUTCOMES_PATH, sep="\t", index=False)
    write_figure(outcomes, ablations)
    write_report(outcomes, ablations)
    assert_master_ledgers_header_only()
    return {
        "heldout_cases": int(len(outcomes)),
        "validated": int(outcomes["wave4_outcome_status"].eq("validated").sum()),
        "falsified": int(outcomes["wave4_outcome_status"].eq("falsified").sum()),
        "data_limited": int(outcomes["wave4_outcome_status"].eq("data_limited").sum()),
        "insufficient_support": int(outcomes["wave4_outcome_status"].eq("insufficient_support").sum()),
    }


if __name__ == "__main__":
    result = build()
    print(
        "PASS: Track 2 Wave 4 validation closure "
        f"({result['heldout_cases']} held-out, {result['validated']} validated, "
        f"{result['falsified']} falsified)"
    )
    print(f"WROTE: {OUTCOMES_PATH}")
    print(f"WROTE: {FIGURE_PATH}")
    print(f"WROTE: {REPORT_PATH}")
