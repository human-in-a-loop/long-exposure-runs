#!/usr/bin/env python3
"""Build Track 5 Wave 4 temporal/source closure artifacts.

created: 2026-05-18T10:05:00+00:00
cycle: 14
run_id: fork-cc044bf40be3-clone-1-track5-wave4-closure
agent: worker-clone-1
milestone: M4.V5
"""
from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5"
DATA = T5 / "data"
FIG = T5 / "figures"
REPORTS = T5 / "reports"


def _top_decile(value: object) -> bool:
    if pd.isna(value):
        return False
    return float(value) <= 0.10


def build_outcomes() -> pd.DataFrame:
    holdouts = pd.read_csv(DATA / "temporal_holdout_recovery.tsv", sep="\t")
    ablations = pd.read_csv(DATA / "source_ablation_results.tsv", sep="\t")
    rows: list[dict[str, object]] = []

    for row in holdouts.to_dict("records"):
        pct = row.get("family_percentile")
        top_decile = _top_decile(pct)
        status = str(row.get("status", ""))
        outcome = "validated_temporal_recovery" if status == "validated" and top_decile else "data_limited_not_recovered"
        rows.append(
            {
                "row_type": "temporal_holdout",
                "target_taxon": row["taxon"],
                "chemical_class": row["target_compound_class"],
                "family": row["family"],
                "cutoff_status": row["cutoff_filter_status"],
                "rank_within_family": row.get("rank_within_family", ""),
                "family_percentile": row.get("family_percentile", ""),
                "top_decile": top_decile,
                "variant": "",
                "prediction_count": "",
                "outcome": outcome,
                "interpretation": row["diagnostic"],
            }
        )

    for row in ablations.to_dict("records"):
        variant = row["variant"]
        if variant == "full":
            outcome = "baseline_source_dominated"
        elif variant == "duke_downweighted":
            outcome = "not_independent_duke_still_present"
        else:
            outcome = "collapsed_or_no_eligible_non_duke_stratum"
        rows.append(
            {
                "row_type": "source_ablation",
                "target_taxon": "",
                "chemical_class": "",
                "family": "",
                "cutoff_status": "",
                "rank_within_family": "",
                "family_percentile": "",
                "top_decile": False,
                "variant": variant,
                "prediction_count": int(row["prediction_count"]),
                "outcome": outcome,
                "interpretation": row["notes"],
            }
        )

    out = pd.DataFrame(rows)
    DATA.mkdir(parents=True, exist_ok=True)
    out.to_csv(DATA / "track5_wave4_validation_outcomes.tsv", sep="\t", index=False)
    return out


def plot_summary(outcomes: pd.DataFrame) -> None:
    holdouts = outcomes[outcomes["row_type"] == "temporal_holdout"].copy()
    ablations = outcomes[outcomes["row_type"] == "source_ablation"].copy()
    holdouts["plot_percentile"] = pd.to_numeric(holdouts["family_percentile"], errors="coerce").fillna(1.0)
    ablations["prediction_count"] = pd.to_numeric(ablations["prediction_count"], errors="coerce").fillna(0)

    FIG.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.15, 1]})

    colors = ["#8c564b" if v else "#6b7280" for v in holdouts["top_decile"]]
    ax1.barh(holdouts["target_taxon"], holdouts["plot_percentile"], color=colors)
    ax1.axvline(0.10, color="#b91c1c", linestyle="--", linewidth=1)
    ax1.set_xlim(0, 1.05)
    ax1.set_xlabel("family percentile (lower is better)")
    ax1.set_title("Temporal holdout recovery")
    ax1.invert_yaxis()

    ax2.bar(ablations["variant"], ablations["prediction_count"], color=["#374151", "#b91c1c", "#4b5563", "#9ca3af", "#9ca3af"])
    ax2.set_ylabel("prediction rows")
    ax2.set_title("Prediction survival by ablation")
    ax2.tick_params(axis="x", rotation=25)
    for i, v in enumerate(ablations["prediction_count"]):
        ax2.text(i, float(v) + 25, str(int(v)), ha="center", fontsize=8)

    fig.suptitle("Track 5 Wave 4 temporal validation and source ablation summary", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "track5_wave4_temporal_source_summary.png", dpi=150)
    plt.close(fig)


def report_markdown(outcomes: pd.DataFrame) -> str:
    holdouts = outcomes[outcomes["row_type"] == "temporal_holdout"]
    ablations = outcomes[outcomes["row_type"] == "source_ablation"]

    def display(value: object) -> str:
        if pd.isna(value):
            return ""
        text = str(value)
        return "" if text.lower() == "nan" else text

    holdout_table = "\n".join(
        "| {target_taxon} | {chemical_class} | {family} | {cutoff_status} | {rank} | {pct} | {top} | {outcome} |".format(
            target_taxon=row["target_taxon"],
            chemical_class=row["chemical_class"],
            family=row["family"],
            cutoff_status=row["cutoff_status"],
            rank=display(row["rank_within_family"]),
            pct=display(row["family_percentile"]),
            top=str(row["top_decile"]).lower(),
            outcome=row["outcome"],
        )
        for row in holdouts.to_dict("records")
    )
    ablation_table = "\n".join(
        f"| {row['variant']} | {row['prediction_count']} | {row['outcome']} | {row['interpretation']} |"
        for row in ablations.to_dict("records")
    )

    return f"""---
created: 2026-05-18T10:05:00+00:00
cycle: 14
run_id: fork-cc044bf40be3-clone-1-track5-wave4-closure
agent: worker-clone-1
milestone: M4.V5
---

# Track 5 Wave 4 Temporal and Source Closure

## Decision

H5 is not validated under the frozen Track 5 inputs. The temporal holdout set does not recover the required canonical source taxa in the top decile of their families, and the source controls show that the M3.T5 score is a Duke-dominated screening prior rather than a source-independent chemodiversity signal. The appropriate closure is `M4.V5=deferred/data_limited` for temporal validation and `M4.A-track5-duke-source-ablation=validated` as a source-bias/null ablation result.

## Temporal Holdout Outcomes

| Target taxon | Chemical class | Family | Cutoff status | Rank | Family percentile | Top decile | Outcome |
|---|---|---|---|---:|---:|---|---|
{holdout_table}

Missing ranks and percentiles are meaningful null results: the current tables lack historical assertion dates, several targets do not resolve to accepted keys in the frozen substrate, and qualified family/class signatures are absent for the tested target classes. These are coverage and temporal-provenance limits, not evidence about real-world compound absence.

## Source Ablation Outcomes

| Variant | Prediction rows | Outcome | Interpretation |
|---|---:|---|---|
{ablation_table}

The no-Duke result is decisive for the current instrument mechanics. The score is `score(t,k|f)=S_f[k]*w_specificity(k)*w_screening(t)`, so if Duke supplies the retained family/class rows used to estimate `S_f[k]`, removing Duke makes that term zero or undefined and prediction rows vanish. Duke-downweighted rows do not establish independence because Duke still defines `S_f[k]`.

![Temporal holdout family-percentile outcomes compared with prediction-count survival under no-Duke, source-matched, screening-matched, and Duke-downweighted ablations.](../figures/track5_wave4_temporal_source_summary.png)

## Source-Bias Interpretation

The current Track 5 artifact measures where a Duke-backed family/class signature plus screening intensity makes a candidate eligible for follow-up. It does not yet distinguish biological chemodiversity neighborhood completion from source coverage, screening density, or class-harmonization availability. The validated contribution of this branch is therefore the ablation finding: source-independent Track 5 signal is absent under the current frozen inputs, and a fair non-Duke matched comparison is data-limited because the required local non-Duke detection/class stratum is empty.

## Evidence Firewall

This closure is about prediction mechanics and source coverage only. It does not assert taxon-level compound detection, medical effect, preparation advice, dose, or safety status. All positive biological interpretation remains blocked until non-Duke source recovery, historical assertion dating, and Barrier 4 ledger reconciliation are available.
"""


def write_report(outcomes: pd.DataFrame) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "track5_wave4_temporal_source_closure.md").write_text(report_markdown(outcomes), encoding="utf-8")


def main() -> int:
    outcomes = build_outcomes()
    plot_summary(outcomes)
    write_report(outcomes)
    print(f"WROTE: {DATA / 'track5_wave4_validation_outcomes.tsv'} ({len(outcomes)} rows)")
    print(f"WROTE: {FIG / 'track5_wave4_temporal_source_summary.png'}")
    print(f"WROTE: {REPORTS / 'track5_wave4_temporal_source_closure.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
