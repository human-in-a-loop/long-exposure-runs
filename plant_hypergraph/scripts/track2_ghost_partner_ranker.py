#!/usr/bin/env python3
# created: 2026-05-17T23:59:50+00:00
# cycle: 9
# run_id: fork-aaf42b4ab956-clone-1-track2-ghost-ranker
# agent: worker
# milestone: M3.T2
"""Rank Track 2 ghost-partner candidates without promoting them to facts.

The score is a transparent prioritization statistic over cited Track 2 seed
rows. It is not a classifier and it never emits an established anachronism
claim.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TRACK = ROOT / "tracks" / "track2"
DATA = TRACK / "data"
FIGURES = TRACK / "figures"
REPORTS = TRACK / "reports"
MERGE_REPORT = ROOT / ".long-exposure" / "fork-aaf42b4ab956" / "clone-1" / "merge_report.md"

SEED_PATH = DATA / "ghost_partner_seed_edges.parquet"
SUPPORT_PATH = DATA / "ghost_partner_support_nodes.parquet"
RANGE_PATH = DATA / "ghost_partner_range_context_edges.parquet"
SCORES_PATH = DATA / "ghost_partner_candidate_scores.tsv"
PREDICTIONS_PATH = DATA / "ghost_partner_predictions.tsv"
COMPONENTS_PATH = DATA / "ghost_partner_score_components.tsv"
DATA_LIMITED_PATH = DATA / "ghost_partner_data_limited_cases.tsv"
HELDOUT_PATH = DATA / "janzen_martin_heldout_recovery_scaffold.tsv"
FIGURE_PATH = FIGURES / "ghost_candidate_score_components.png"
REPORT_PATH = REPORTS / "track2_ghost_hyperedges.md"

WEIGHTS = {
    "morphology_support": 0.25,
    "extinct_partner_support": 0.25,
    "modern_failure_support": 0.20,
    "spatiotemporal_compatibility": 0.20,
    "provenance_completeness": 0.10,
    "penalty_living_megafauna_ambiguous": -0.15,
    "penalty_source_singleton": -0.10,
}

MODERN_FAILURE_TERMS = (
    "recruitment failure",
    "dispersal failure",
    "parent-shadow",
    "missing partner",
    "missing partners",
    "nonsensical fruit",
    "anachronistic fruit",
)

JANZEN_MARTIN_HELDOUT = [
    ("Persea americana", "avocado"),
    ("Maclura pomifera", "osage orange"),
    ("Gleditsia triacanthos", "honey locust"),
    ("Annona cherimola", "cherimoya"),
    ("Mauritia flexuosa", "moriche palm"),
    ("Spondias mombin", "hog plum"),
    ("Sideroxylon foetidissimum", "mastic bully"),
    ("Asimina triloba", "pawpaw"),
]


def parse_jsonish(value: object) -> dict:
    if value is None:
        return {}
    text = str(value).strip()
    if not text or text == "{}":
        return {}
    try:
        obj, _ = json.JSONDecoder().raw_decode(text)
    except json.JSONDecodeError:
        return {}
    return obj if isinstance(obj, dict) else {}


def clean_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def genus_from_node(node_id: str) -> str:
    tail = clean_text(node_id).split(":")[-1]
    return tail.split("_")[0].lower() if tail else ""


def scientific_name_from_node(node_id: str) -> str:
    tail = clean_text(node_id).split(":")[-1]
    return tail.replace("_", " ").lower()


def normalized_scientific_name(value: object) -> str:
    return " ".join(clean_text(value).lower().replace("_", " ").split())


def has_value(value: object) -> bool:
    return bool(clean_text(value))


def provenance_completeness(row: pd.Series) -> float:
    required = [
        "source_id",
        "source_record_id",
        "access_date",
        "license",
        "provenance_pointer",
        "allowed_evidence_scope",
        "caveats",
    ]
    return sum(has_value(row.get(col, "")) for col in required) / len(required)


def status_for(row: pd.Series, score: float) -> str:
    if row["edge_type"] != "anachronism_candidate_edge":
        return "excluded_schema_scope"
    if row["provenance_completeness"] < 1.0 or not has_value(row["allowed_evidence_scope"]):
        return "data_limited"
    if not has_value(row["accepted_taxon_key"]):
        return "data_limited"
    if row["modern_failure_support"] == 0:
        return "insufficient_support"
    if row["extinct_partner_support"] == 0 or (
        row["modern_failure_support"] == 0 and row["spatiotemporal_compatibility"] < 0.5
    ):
        return "insufficient_support"
    if score < 0.55:
        return "insufficient_support"
    return "candidate_pending_validation"


def compatibility(seed_geo: str, support_geo: str) -> float:
    seed = seed_geo.lower()
    support = support_geo.lower()
    if not seed or not support:
        return 0.0
    broad = {
        "neotropics": ["south america", "mesoamerica", "central america", "north america"],
        "eastern north america": ["north america"],
        "amazonian south america": ["south america"],
        "andean south america": ["south america"],
        "mesoamerica": ["north america", "south america"],
    }
    if seed in support or support in seed:
        return 1.0
    for key, values in broad.items():
        if key in seed and any(v in support for v in values):
            return 0.75
    return 0.0


def build() -> dict:
    FIGURES.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    seeds = pd.read_parquet(SEED_PATH)
    support = pd.read_parquet(SUPPORT_PATH)
    ranges = pd.read_parquet(RANGE_PATH)

    support_by_node = support.set_index("node_id", drop=False).to_dict("index")
    extinct_support_names = {
        scientific_name_from_node(v)
        for v in support.loc[support["node_type"].eq("extinct_fauna"), "node_id"].dropna()
        if clean_text(v)
    }
    living_range_genera = {
        normalized_scientific_name(v).split()[0]
        for v in ranges["raw_scientific_name"].dropna()
        if normalized_scientific_name(v)
        and normalized_scientific_name(v) not in extinct_support_names
    }
    source_counts = seeds.groupby(["plant_node_id", "extinct_fauna_node_id"])[
        "primary_citation_short"
    ].transform("nunique")

    rows: list[dict] = []
    components: list[dict] = []
    for idx, seed in seeds.reset_index(drop=True).iterrows():
        caveat = parse_jsonish(seed.get("caveats"))
        support_row = support_by_node.get(clean_text(seed.get("extinct_fauna_node_id")), {})
        temporal = parse_jsonish(support_row.get("temporal_annotation_json"))
        caveat_blob = " ".join(
            [
                clean_text(seed.get("caveats")),
                clean_text(seed.get("primary_citation_full")),
                clean_text(seed.get("interpretation_caveat")),
                clean_text(caveat.get("named_hypothesis_quote", "")),
            ]
        ).lower()

        morphology = 1.0 if has_value(seed.get("fruit_type_node_id")) else 0.0
        extinct = 1.0 if support_row and seed.get("extinct_fauna_node_id", "").startswith("extinct_fauna:") else 0.5
        modern_failure = 0.5 if any(term in caveat_blob for term in MODERN_FAILURE_TERMS) else 0.0
        geo = compatibility(seed.get("geographic_scope", ""), support_row.get("geographic_scope", ""))
        time = 1.0 if temporal.get("last_appearance_kyr_min") is not None else 0.0
        spatiotemporal = round((geo + time) / 2, 3) if geo or time else 0.0
        provenance = round(provenance_completeness(seed), 3)
        living_ambiguous = 1.0 if genus_from_node(seed.get("extinct_fauna_node_id", "")) in living_range_genera else 0.0
        singleton = 1.0 if int(source_counts.iloc[idx]) <= 1 else 0.0

        component_values = {
            "morphology_support": morphology,
            "extinct_partner_support": extinct,
            "modern_failure_support": modern_failure,
            "spatiotemporal_compatibility": spatiotemporal,
            "provenance_completeness": provenance,
            "penalty_living_megafauna_ambiguous": living_ambiguous,
            "penalty_source_singleton": singleton,
        }
        score = round(max(0.0, sum(component_values[k] * WEIGHTS[k] for k in WEIGHTS)), 3)
        if modern_failure == 0:
            score = min(score, 0.55)
        row = {
            "candidate_id": f"T2C{idx + 1:04d}",
            "source_edge_id": seed.get("edge_id", ""),
            "rank": 0,
            "candidate_status": "",
            "candidate_score": score,
            "raw_scientific_name": seed.get("raw_scientific_name", ""),
            "accepted_taxon_key": seed.get("accepted_taxon_key", ""),
            "pending_crosswalk": bool(seed.get("pending_crosswalk")),
            "candidate_class": seed.get("candidate_class", ""),
            "plant_node_id": seed.get("plant_node_id", ""),
            "fruit_type_node_id": seed.get("fruit_type_node_id", ""),
            "extinct_fauna_node_id": seed.get("extinct_fauna_node_id", ""),
            "geographic_scope": seed.get("geographic_scope", ""),
            "primary_citation_short": seed.get("primary_citation_short", ""),
            "primary_citation_page": seed.get("primary_citation_page", ""),
            "allowed_evidence_scope": seed.get("allowed_evidence_scope", ""),
            "interpretation_caveat": seed.get("interpretation_caveat", ""),
            "inferred_anachronism_claim": False,
            "enters_prediction_ledger": False,
            "evidence_boundary": "candidate prioritization only; not established anachronism status",
            **component_values,
        }
        row["candidate_status"] = status_for(pd.Series(row | seed.to_dict()), score)
        if living_ambiguous:
            row["ambiguity_flag"] = "living_megafauna_compatible_genus"
        elif singleton:
            row["ambiguity_flag"] = "source_singleton"
        else:
            row["ambiguity_flag"] = ""
        rows.append(row)
        for component, value in component_values.items():
            components.append(
                {
                    "candidate_id": row["candidate_id"],
                    "candidate_class": row["candidate_class"],
                    "component": component,
                    "component_value": value,
                    "weight": WEIGHTS[component],
                    "weighted_contribution": round(value * WEIGHTS[component], 3),
                }
            )

    scores = pd.DataFrame(rows).sort_values(
        ["candidate_score", "raw_scientific_name", "extinct_fauna_node_id"],
        ascending=[False, True, True],
    )
    scores["rank"] = range(1, len(scores) + 1)
    comp = pd.DataFrame(components).merge(scores[["candidate_id", "rank"]], on="candidate_id")
    comp = comp.sort_values(["rank", "component"])
    limited = scores[
        scores["candidate_status"].isin(["data_limited", "insufficient_support", "excluded_schema_scope"])
    ].copy()
    limited["data_limited_reason"] = limited.apply(reason_for_limited, axis=1)
    predictions = build_prediction_table(scores)
    heldout = build_heldout_scaffold(scores)

    scores.to_csv(SCORES_PATH, sep="\t", index=False)
    predictions.to_csv(PREDICTIONS_PATH, sep="\t", index=False)
    comp.to_csv(COMPONENTS_PATH, sep="\t", index=False)
    limited.to_csv(DATA_LIMITED_PATH, sep="\t", index=False)
    heldout.to_csv(HELDOUT_PATH, sep="\t", index=False)
    write_figure(scores)
    write_report(scores, predictions, heldout)
    write_merge_report(scores, predictions, heldout)
    return {
        "scored_candidates": int(len(scores)),
        "candidate_status_counts": scores["candidate_status"].value_counts().to_dict(),
        "data_limited_cases": int(len(limited)),
        "track_prediction_rows": int(len(predictions)),
        "heldout_scaffold_rows": int(len(heldout)),
        "top_score": float(scores["candidate_score"].max()),
    }


def reason_for_limited(row: pd.Series) -> str:
    reasons = []
    if row["candidate_status"] == "excluded_schema_scope":
        reasons.append("edge outside Track 2 anachronism_candidate_edge scope")
    if not has_value(row["accepted_taxon_key"]):
        reasons.append("missing accepted focal taxon key")
    if row["provenance_completeness"] < 1.0:
        reasons.append("incomplete provenance or allowed evidence scope")
    if row["modern_failure_support"] == 0:
        reasons.append("no explicit modern dispersal-failure component in seed row")
    if row["spatiotemporal_compatibility"] < 0.5:
        reasons.append("range/time compatibility is missing or weak")
    if row["penalty_living_megafauna_ambiguous"] > 0:
        reasons.append("living-megafauna-compatible genus requires ambiguity handling")
    if row["penalty_source_singleton"] > 0:
        reasons.append("single source for candidate pair")
    return "; ".join(reasons)


def prediction_status(candidate_status: str) -> str:
    if candidate_status == "candidate_pending_validation":
        return "pending"
    if candidate_status == "data_limited":
        return "data_limited"
    if candidate_status == "insufficient_support":
        return "data_limited"
    return "superseded"


def validation_source(row: pd.Series) -> str:
    if row["candidate_status"] != "candidate_pending_validation":
        return "not validation-ready until accepted-key/support gaps are resolved"
    return (
        "Wave 4 held-out Janzen-Martin recovery plus targeted literature check for "
        "modern dispersal failure, extinct-fauna geography/time overlap, and living-megafauna contrast"
    )


def build_prediction_table(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in scores.itertuples(index=False):
        statement = (
            "Hypothesis for validation: prioritize "
            f"{row.raw_scientific_name} as a Track 2 ghost-partner candidate in "
            f"`{row.candidate_class}` because cited seed evidence links "
            f"{row.fruit_type_node_id} with {row.extinct_fauna_node_id}. "
            "This is not an established anachronism claim."
        )
        caveats = [
            row.evidence_boundary,
            "candidate-only output; no master prediction_ledger.tsv write in M3.T2",
        ]
        if not has_value(row.accepted_taxon_key):
            caveats.append("missing accepted focal taxon key")
        if row.modern_failure_support == 0:
            caveats.append("no explicit modern dispersal-failure component in seed row")
        if row.penalty_living_megafauna_ambiguous > 0:
            caveats.append("living-megafauna-compatible contrast required before validation")
        rows.append(
            {
                "track": "track2",
                "prediction_id": f"T2-GHOST-{int(row.rank):04d}",
                "candidate_id": row.candidate_id,
                "rank": int(row.rank),
                "prediction_statement": statement,
                "supporting_hyperedges": row.source_edge_id,
                "supporting_node_set": json.dumps(
                    {
                        "plant": row.plant_node_id,
                        "fruit_morphology": row.fruit_type_node_id,
                        "putative_extinct_disperser": row.extinct_fauna_node_id,
                    },
                    sort_keys=True,
                ),
                "expected_validation_source": validation_source(pd.Series(row._asdict())),
                "status": prediction_status(row.candidate_status),
                "candidate_status": row.candidate_status,
                "candidate_score": row.candidate_score,
                "ablation_sensitivity": (
                    "remove anachronism_candidate_edge, extinct_fauna/paleo-context support, "
                    "modern-failure term, source-singleton penalty, or living-megafauna penalty"
                ),
                "hypothesis_caveat": "; ".join(caveats),
                "allowed_evidence_scope": row.allowed_evidence_scope,
                "inferred_anachronism_claim": False,
                "enters_master_prediction_ledger": False,
                "date_filed": "2026-05-18",
                "date_resolved": "",
            }
        )
    return pd.DataFrame(rows)


def build_heldout_scaffold(scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    by_name = {
        clean_text(row.raw_scientific_name).lower(): row
        for row in scores.sort_values("rank").itertuples(index=False)
    }
    for scientific_name, common_name in JANZEN_MARTIN_HELDOUT:
        row = by_name.get(scientific_name.lower())
        if row is None:
            rows.append(
                {
                    "heldout_scientific_name": scientific_name,
                    "common_name": common_name,
                    "in_seed_layer": False,
                    "best_candidate_id": "",
                    "best_rank": "",
                    "candidate_status": "not_present",
                    "candidate_score": "",
                    "accepted_taxon_key": "",
                    "recovery_bucket": "not_recovered_in_seed_layer",
                    "validation_use": "hold-out label scaffold only; do not train on canonical label",
                }
            )
            continue
        if row.candidate_status == "candidate_pending_validation":
            bucket = "recovered_validation_ready_seed"
        elif row.candidate_status == "data_limited":
            bucket = "recovered_but_data_limited"
        else:
            bucket = "recovered_but_insufficient_support"
        rows.append(
            {
                "heldout_scientific_name": scientific_name,
                "common_name": common_name,
                "in_seed_layer": True,
                "best_candidate_id": row.candidate_id,
                "best_rank": int(row.rank),
                "candidate_status": row.candidate_status,
                "candidate_score": row.candidate_score,
                "accepted_taxon_key": row.accepted_taxon_key,
                "recovery_bucket": bucket,
                "validation_use": "hold-out label scaffold only; do not train on canonical label",
            }
        )
    return pd.DataFrame(rows)


def write_figure(scores: pd.DataFrame) -> None:
    components = [
        "morphology_support",
        "extinct_partner_support",
        "modern_failure_support",
        "spatiotemporal_compatibility",
    ]
    plot_df = scores.groupby("candidate_class")[components].mean().sort_index()
    ax = plot_df.plot(kind="bar", figsize=(11, 5), width=0.82)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Mean component value")
    ax.set_xlabel("Candidate class")
    ax.set_title("Track 2 candidate component coverage")
    ax.legend(title="Component", fontsize=8)
    ax.tick_params(axis="x", labelrotation=35)
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=160)
    plt.close()


def status_rows(scores: pd.DataFrame) -> str:
    counts = scores["candidate_status"].value_counts().sort_index()
    return "\n".join(f"| `{status}` | {count} |" for status, count in counts.items())


def top_rows(scores: pd.DataFrame, limit: int = 8) -> str:
    rows = []
    for row in scores.head(limit).itertuples(index=False):
        rows.append(
            f"| {int(row.rank)} | `{row.candidate_id}` | {row.raw_scientific_name} | "
            f"{row.candidate_score:.3f} | `{row.candidate_status}` | `{row.ambiguity_flag}` |"
        )
    return "\n".join(rows)


def heldout_rows(heldout: pd.DataFrame) -> str:
    rows = []
    for row in heldout.itertuples(index=False):
        rows.append(
            f"| {row.heldout_scientific_name} | {row.in_seed_layer} | {row.best_rank} | "
            f"`{row.candidate_status}` | `{row.recovery_bucket}` |"
        )
    return "\n".join(rows)


def write_report(scores: pd.DataFrame, predictions: pd.DataFrame, heldout: pd.DataFrame) -> None:
    report = f"""---
created: 2026-05-18T02:45:00+00:00
run_id: fork-aaf42b4ab956-clone-1-track2-ghost-ranker
agent: worker
milestone: M3.T2
schema_version: v1.0
---

# Track 2 Ghost-Partner Candidate Ranker

## Status

This is the M3.T2 Ghost-Partner Candidate Ranker over the validated Barrier 2
Track 2 enrichment layer. It ranks cited paleobotany, extinct-fauna, and
Janzen-Martin seed rows for validation priority only. It does not claim any row
is an established anachronism and it does not write the master
`prediction_ledger.tsv`.

## Inputs

| Input | Role |
|---|---|
| `tracks/track2/data/ghost_partner_seed_edges.parquet` | 31 cited candidate seed edges from Wave 2 enrichment |
| `tracks/track2/data/anachronism_candidate_seed_summary.tsv` | candidate-class seed coverage |
| `tracks/track2/data/ghost_partner_support_nodes.parquet` | extinct-fauna, paleo-context, and modern-disperser support nodes |
| `tracks/track2/data/ghost_partner_range_context_edges.parquet` | PHYLACINE range-context support, not prediction evidence |
| `data/barrier2_track_enrichment_conformance.json` | Barrier 2 conformance status: Track 2 ready at seed scale |

## Mechanism

The score is a transparent prioritization statistic:

```text
S(c) = 0.25 M + 0.25 E + 0.20 F + 0.20 G + 0.10 P - 0.15 L - 0.10 Q
```

`M` is morphology support, `E` is extinct-fauna or paleo-context support, `F`
is modern dispersal-failure support, `G` is geography/time compatibility, `P`
is provenance completeness, `L` is living-megafauna ambiguity, and `Q` is
singleton-source thinness. The score is not a truth probability.

Special-point behavior is explicit: missing accepted focal keys become
`data_limited`; morphology without modern failure/geography support remains
`insufficient_support`; living-megafauna-compatible cases receive an ambiguity
penalty and flag; singleton source rows carry a source-thinness penalty.

## Outputs

| Output | Rows | Purpose |
|---|---:|---|
| `tracks/track2/data/ghost_partner_candidate_scores.tsv` | {len(scores)} | ranked candidate table with component columns |
| `tracks/track2/data/ghost_partner_predictions.tsv` | {len(predictions)} | track-local candidate prediction ledger; no master ledger write |
| `tracks/track2/data/ghost_partner_score_components.tsv` | {len(scores) * len(WEIGHTS)} | long-form component diagnostics |
| `tracks/track2/data/ghost_partner_data_limited_cases.tsv` | {int(scores['candidate_status'].isin(['data_limited', 'insufficient_support', 'excluded_schema_scope']).sum())} | blocked or caveated rows |
| `tracks/track2/data/janzen_martin_heldout_recovery_scaffold.tsv` | {len(heldout)} | held-out canonical-case recovery scaffold |
| `tracks/track2/figures/ghost_candidate_score_components.png` | 1 | component coverage by candidate class |

![Mean candidate-score component coverage by Track 2 candidate class; y-axis is mean component value on a 0-1 scale, with living-megafauna/source penalties reported in TSV diagnostics rather than plotted.](../figures/ghost_candidate_score_components.png)

## Candidate Status Counts

| Status | Count |
|---|---:|
{status_rows(scores)}

## Top Ranked Candidates

| Rank | Candidate | Taxon | Score | Status | Ambiguity |
|---:|---|---|---:|---|---|
{top_rows(scores)}

## Held-Out Janzen-Martin Scaffold

This table is a validation scaffold, not a validation result. Labels must be
withheld from future training/scoring passes and used only to evaluate recovery.

| Held-out taxon | In seed layer | Best rank | Candidate status | Recovery bucket |
|---|---:|---:|---|---|
{heldout_rows(heldout)}

## Evidence Boundaries

- `inferred_anachronism_claim` is `false` for every candidate and prediction row.
- `enters_master_prediction_ledger` is `false` for every track-local prediction
  row in this M3 branch.
- Rows missing accepted focal taxon keys remain `data_limited`; this branch does
  not perform independent synonym normalization.
- `hypothesis_caveat` states why each row is a candidate hypothesis and what
  validation gap blocks stronger interpretation.
- Living-megafauna-compatible cases are flagged as ambiguity controls rather
  than treated as ghost-megafauna evidence.

## Validation Readiness

The {int((scores['candidate_status'] == 'candidate_pending_validation').sum())} `candidate_pending_validation` rows are ready as a Wave 4 validation
queue. Data-limited canonical cases such as *Maclura pomifera*, *Gleditsia
triacanthos*, *Mauritia flexuosa*, and *Persea americana* need accepted-key
recovery before they can be used as canonical taxon-key validation targets.

## Reproduction

```bash
python3 scripts/track2_ghost_partner_ranker.py
python3 -m pytest -q tracks/track2/tests/test_ghost_partner_ranker.py
```
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def write_merge_report(scores: pd.DataFrame, predictions: pd.DataFrame, heldout: pd.DataFrame) -> None:
    MERGE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    merge = f"""# Clone 1 Merge Report — Track 2 Ghost-Partner Ranker

## Scope

Fork `aaf42b4ab956`, clone 1. Built the M3.T2 Ghost-Partner Candidate Ranker
contract artifacts for conductor pickup.

## Outputs

- `scripts/track2_ghost_partner_ranker.py`
- `tracks/track2/data/ghost_partner_candidate_scores.tsv`
- `tracks/track2/data/ghost_partner_predictions.tsv`
- `tracks/track2/data/ghost_partner_score_components.tsv`
- `tracks/track2/data/ghost_partner_data_limited_cases.tsv`
- `tracks/track2/data/janzen_martin_heldout_recovery_scaffold.tsv`
- `tracks/track2/figures/ghost_candidate_score_components.png`
- `tracks/track2/reports/track2_ghost_hyperedges.md`
- `tracks/track2/tests/test_ghost_partner_ranker.py`

## Summary

Scored {len(scores)} candidate rows and emitted {len(predictions)} track-local
candidate prediction rows. Status counts: {scores['candidate_status'].value_counts().to_dict()}.
Held-out scaffold rows: {len(heldout)}.

## Evidence Boundary

No row is marked as an established anachronism. The branch does not write the
master `prediction_ledger.tsv`; it emits track-local M3.T2 candidate hypotheses
with explicit caveats and validation targets.
"""
    MERGE_REPORT.write_text(merge, encoding="utf-8")


if __name__ == "__main__":
    metrics = build()
    print(
        "PASS: Track 2 ghost-partner ranker "
        f"({metrics['scored_candidates']} candidates, top score {metrics['top_score']:.3f})"
    )
    print(f"WROTE: {SCORES_PATH.relative_to(ROOT)}")
    print(f"WROTE: {PREDICTIONS_PATH.relative_to(ROOT)}")
    print(f"WROTE: {COMPONENTS_PATH.relative_to(ROOT)}")
    print(f"WROTE: {DATA_LIMITED_PATH.relative_to(ROOT)}")
    print(f"WROTE: {HELDOUT_PATH.relative_to(ROOT)}")
    print(f"WROTE: {FIGURE_PATH.relative_to(ROOT)}")
    print(f"WROTE: {REPORT_PATH.relative_to(ROOT)}")
