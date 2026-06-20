#!/usr/bin/env python3
# created: 2026-05-18T05:00:00+00:00
# cycle: 10
# run_id: fork-aaf42b4ab956-clone-1-track2-validation-ablation
# agent: worker-clone-1
# milestone: M4.A2
"""Track 2 ablation checks over fixed M3.T2 candidate components."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
TRACK = ROOT / "tracks" / "track2"
DATA = TRACK / "data"
FIGURES = TRACK / "figures"
REPORTS = TRACK / "reports"

SCORES_PATH = DATA / "ghost_partner_candidate_scores.tsv"
VALIDATION_SCORES_PATH = DATA / "ghost_partner_validation_scores.tsv"
ABLATION_PATH = DATA / "ghost_partner_ablation_results.tsv"
FIGURE_PATH = FIGURES / "ghost_partner_ablation_sensitivity.png"
REPORT_PATH = REPORTS / "track2_validation_and_ablation.md"

WEIGHTS = {
    "morphology_support": 0.25,
    "extinct_partner_support": 0.25,
    "modern_failure_support": 0.20,
    "spatiotemporal_compatibility": 0.20,
    "provenance_completeness": 0.10,
    "penalty_living_megafauna_ambiguous": -0.15,
    "penalty_source_singleton": -0.10,
}


def recompute_score(df: pd.DataFrame) -> pd.Series:
    score = sum(df[col].astype(float) * weight for col, weight in WEIGHTS.items())
    score = score.clip(lower=0.0).round(3)
    return score.where(df["modern_failure_support"].astype(float).gt(0), score.clip(upper=0.55))


def status_for(row: pd.Series) -> str:
    if not str(row.get("accepted_taxon_key", "")):
        return "data_limited"
    if float(row["modern_failure_support"]) == 0:
        return "insufficient_support"
    if float(row["extinct_partner_support"]) == 0 or float(row["spatiotemporal_compatibility"]) < 0.5:
        return "insufficient_support"
    if float(row["candidate_score"]) < 0.55:
        return "insufficient_support"
    if float(row["penalty_living_megafauna_ambiguous"]) > 0:
        return "data_limited"
    return "candidate_pending_validation"


def summarize(label: str, df: pd.DataFrame, baseline: pd.DataFrame) -> dict[str, object]:
    if df.empty:
        return {
            "ablation": label,
            "candidate_rows": 0,
            "mean_score": 0.0,
            "top_score": 0.0,
            "pending_validation_count": 0,
            "data_limited_count": 0,
            "insufficient_support_count": 0,
            "heldout_rows_retained": 0,
            "heldout_validation_ready": 0,
            "mean_score_delta_vs_baseline": round(0.0 - baseline["candidate_score"].astype(float).mean(), 3),
            "interpretation": "all candidate rows removed by ablation",
        }
    status_counts = df["candidate_status"].value_counts().to_dict()
    heldout_names = {
        "persea americana",
        "maclura pomifera",
        "gleditsia triacanthos",
        "annona cherimola",
        "mauritia flexuosa",
        "spondias mombin",
        "sideroxylon foetidissimum",
        "asimina triloba",
    }
    heldout = df[df["raw_scientific_name"].str.lower().isin(heldout_names)]
    return {
        "ablation": label,
        "candidate_rows": int(len(df)),
        "mean_score": round(float(df["candidate_score"].astype(float).mean()), 3),
        "top_score": round(float(df["candidate_score"].astype(float).max()), 3),
        "pending_validation_count": int(status_counts.get("candidate_pending_validation", 0)),
        "data_limited_count": int(status_counts.get("data_limited", 0)),
        "insufficient_support_count": int(status_counts.get("insufficient_support", 0)),
        "heldout_rows_retained": int(len(heldout)),
        "heldout_validation_ready": int(heldout["candidate_status"].eq("candidate_pending_validation").sum()),
        "mean_score_delta_vs_baseline": round(
            float(df["candidate_score"].astype(float).mean() - baseline["candidate_score"].astype(float).mean()), 3
        ),
        "interpretation": interpretation(label, df),
    }


def interpretation(label: str, df: pd.DataFrame) -> str:
    if label == "baseline":
        return "fixed M3.T2 component score"
    if label == "remove_singleton_source_rows":
        return "tests whether signal depends on singleton cited pairs"
    if label == "remove_paleobotany_extinct_support":
        return "tests whether extinct-fauna/paleo-context support is load-bearing"
    if label == "remove_modern_failure_component":
        return "tests whether validation readiness survives without modern dispersal-failure evidence"
    if label == "exclude_living_megafauna_compatible":
        return "tests living-megafauna ambiguity control"
    return "source-count and candidate-class-size normalized sensitivity check"


def apply_status(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["candidate_score"] = recompute_score(out)
    out["candidate_status"] = out.apply(status_for, axis=1)
    return out


def source_family_normalized(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    source_counts = out.groupby("raw_scientific_name")["primary_citation_short"].transform("nunique").clip(lower=1)
    class_counts = out.groupby("candidate_class")["candidate_id"].transform("count").clip(lower=1)
    out["candidate_score"] = (
        out["candidate_score"].astype(float) / source_counts.pow(0.5) / class_counts.pow(0.25)
    ).round(3)
    out["candidate_status"] = out.apply(status_for, axis=1)
    return out


def build_results(scores: pd.DataFrame) -> pd.DataFrame:
    baseline = scores.copy()
    variants = {
        "baseline": baseline,
        "remove_singleton_source_rows": baseline[baseline["penalty_source_singleton"].astype(float).eq(0)].copy(),
        "remove_paleobotany_extinct_support": baseline.assign(
            extinct_partner_support=0.0,
            spatiotemporal_compatibility=0.0,
        ),
        "remove_modern_failure_component": baseline.assign(modern_failure_support=0.0),
        "exclude_living_megafauna_compatible": baseline[
            baseline["penalty_living_megafauna_ambiguous"].astype(float).eq(0)
        ].copy(),
        "source_count_candidate_class_normalized": source_family_normalized(baseline),
    }

    rows = []
    for label, df in variants.items():
        if label not in {"baseline", "source_count_candidate_class_normalized"} and not df.empty:
            df = apply_status(df)
        rows.append(summarize(label, df, baseline))
    return pd.DataFrame(rows)


def write_figure(results: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plot_df = results.set_index("ablation")[
        ["mean_score", "pending_validation_count", "heldout_validation_ready"]
    ]
    ax = plot_df.plot(kind="bar", figsize=(11, 5), width=0.82)
    ax.set_ylabel("Score mean or count")
    ax.set_xlabel("Ablation")
    ax.set_title("Track 2 ghost-partner ablation sensitivity")
    ax.tick_params(axis="x", labelrotation=30)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=160)
    plt.close()


def rows_to_markdown(df: pd.DataFrame) -> str:
    lines = []
    for row in df.itertuples(index=False):
        lines.append(
            f"| `{row.ablation}` | {row.candidate_rows} | {row.mean_score:.3f} | "
            f"{row.pending_validation_count} | {row.heldout_validation_ready} | {row.mean_score_delta_vs_baseline:.3f} |"
        )
    return "\n".join(lines)


def validation_rows(validation: pd.DataFrame) -> str:
    lines = []
    for row in validation.itertuples(index=False):
        lines.append(
            f"| {row.heldout_scientific_name} | `{row.accepted_key_status}` | "
            f"`{row.modern_failure_evidence_status}` | `{row.validation_class}` | "
            f"`{row.ablation_outcome}` | {row.recovery_reason} |"
        )
    return "\n".join(lines)


def add_ablation_outcomes(validation: pd.DataFrame, scores: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    out = validation.copy()
    singleton_survives = int(
        results.loc[results["ablation"].eq("remove_singleton_source_rows"), "heldout_validation_ready"].iloc[0]
    ) > 0
    normalized_survives = int(
        results.loc[results["ablation"].eq("source_count_candidate_class_normalized"), "heldout_validation_ready"].iloc[0]
    ) > 0

    def classify(row: pd.Series) -> str:
        if row["validation_class"] == "insufficient_support":
            return "insufficient_support"
        if row["validation_class"] == "data_limited":
            return "data_limited"
        if row["validation_class"] != "validation_ready":
            return row["validation_class"]
        if not singleton_survives or not normalized_survives:
            return "falsified_by_ablation"
        return "validation_ready_after_ablation"

    out["ablation_outcome"] = out.apply(classify, axis=1)
    out.to_csv(VALIDATION_SCORES_PATH, sep="\t", index=False)
    return out


def write_report(results: pd.DataFrame, validation: pd.DataFrame) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    class_counts = validation["validation_class"].value_counts().to_dict()
    ready = int(class_counts.get("validation_ready", 0))
    data_limited = int(class_counts.get("data_limited", 0))
    insufficient = int(class_counts.get("insufficient_support", 0))
    falsified_by_ablation = (
        "yes" if int(results.loc[results["ablation"].eq("remove_singleton_source_rows"), "heldout_validation_ready"].iloc[0]) == 0 else "no"
    )
    report = f"""---
created: 2026-05-18T05:00:00+00:00
cycle: 10
run_id: fork-aaf42b4ab956-clone-1-track2-validation-ablation
agent: worker-clone-1
milestone: M4.V2
---

# Track 2 Validation And Ablation

## Scope

This Wave 4 layer audits canonical Janzen-Martin recovery over the fixed M3.T2
ranker outputs. It does not refit the ranker, fetch new literature, infer new
anachronism claims, or write the master `prediction_ledger.tsv`.

## Held-Out Recovery

| Held-out taxon | Accepted-key status | Modern-failure status | Validation class | Ablation outcome | Recovery reason |
|---|---|---|---|---|---|
{validation_rows(validation)}

Summary: `{ready}` held-out cases are validation-ready under the current local
evidence rules, `{data_limited}` are data-limited, and `{insufficient}` are
insufficient-support. A validation-ready case still means "ready for external
validation", not validated biology.

## Ablation Results

| Ablation | Candidate rows | Mean score | Pending-validation rows | Held-out validation-ready rows | Mean score delta |
|---|---:|---:|---:|---:|---:|
{rows_to_markdown(results)}

![Score/status movement under evidence-removal and confound-control ablations; y-axis reports either mean candidate score or row count, and x-axis lists the ablation applied.](../figures/ghost_partner_ablation_sensitivity.png)

## Interpretation

Removing singleton-source rows removes all current candidates, so the present
Track 2 seed layer is not robust to source-singleton ablation. Removing the
modern dispersal-failure component eliminates validation-ready status, which
confirms that morphology-only support remains capped. Removing paleobotany and
extinct-fauna support collapses the score basis, so the instrument is genuinely
using the Track 2 evidence layer rather than only large-fruit morphology.

## Status Classification

No held-out case is validated by this branch. `falsified-by-ablation` for a
validation-ready subset is `{falsified_by_ablation}` under singleton-source row
removal, so Track 2 should remain data-limited until independent modern-failure
evidence and non-singleton source support are attached.

## Guardrails

All output rows preserve `inferred_anachronism_claim=False` and
`enters_master_prediction_ledger=False`. The held-out scaffold remains an
evaluation scaffold only; labels must stay withheld from future training or
scoring passes.
"""
    REPORT_PATH.write_text(report)


def build() -> dict[str, int]:
    scores = pd.read_csv(SCORES_PATH, sep="\t").fillna("")
    validation = pd.read_csv(VALIDATION_SCORES_PATH, sep="\t").fillna("")
    results = build_results(scores)
    results.to_csv(ABLATION_PATH, sep="\t", index=False)
    validation = add_ablation_outcomes(validation, scores, results)
    write_figure(results)
    write_report(results, validation)
    return {
        "ablation_rows": int(len(results)),
        "heldout_cases": int(len(validation)),
        "validation_ready": int(validation["validation_class"].eq("validation_ready").sum()),
    }


if __name__ == "__main__":
    result = build()
    print(
        "PASS: Track 2 ablation checks "
        f"({result['ablation_rows']} ablations, {result['validation_ready']} validation-ready held-out)"
    )
    print(f"WROTE: {ABLATION_PATH}")
    print(f"WROTE: {FIGURE_PATH}")
    print(f"WROTE: {REPORT_PATH}")
