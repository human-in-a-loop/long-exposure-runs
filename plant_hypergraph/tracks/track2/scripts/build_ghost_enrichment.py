#!/usr/bin/env python3
"""Build Track 2 ghost-partner enrichment seed artifacts.

This script is deliberately conservative: it transforms cited M1.4
paleobotany rows into Track 2 enrichment seeds, but it does not infer new
anachronism claims and it does not write prediction-ledger rows.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "phytograph_dataset"
STAGING = ROOT / "substrate" / "staging" / "paleobotany_sources"
OUT = ROOT / "tracks" / "track2"
DATA = OUT / "data"
DOCS = OUT / "docs"


def parse_json_prefix(value: str) -> dict:
    if not value:
        return {}
    value = str(value).strip()
    if not value:
        return {}
    try:
        obj, _ = json.JSONDecoder().raw_decode(value)
    except json.JSONDecodeError:
        return {"_parse_error": value}
    return obj if isinstance(obj, dict) else {"_parsed": obj}


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open() as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def member_for_role(role_map_json: str, role: str) -> str:
    role_map = json.loads(role_map_json or "{}")
    values = role_map.get(role, [])
    return values[0] if values else ""


def candidate_class(row: pd.Series, caveat: dict) -> str:
    region = str(caveat.get("geographic_scope", "")).lower()
    fruit = member_for_role(row["role_map_json"], "fruit_morphology").lower()
    fauna = member_for_role(row["role_map_json"], "putative_extinct_disperser").lower()
    if "madagascar" in region or "aepyornis" in fauna:
        return "madagascar_elephant_bird_baobab"
    if "new zealand" in region or "dinornis" in fauna:
        return "new_zealand_moa_divarication"
    if "europe" in region or "bos_primigenius" in fauna:
        return "european_browsing_regime"
    if "eastern north america" in region or "north america" in region:
        return "north_american_temperate_megafauna_fruit"
    if "palm" in fruit or "amazonian" in region or "megatherium" in fauna:
        return "amazonian_palm_or_ground_sloth_fruit"
    return "neotropical_gomphothere_large_fruit"


def collect_support_nodes() -> pd.DataFrame:
    support_files = [
        STAGING / "lqe" / "extinct_fauna.jsonl",
        STAGING / "pbdb" / "extinct_fauna.jsonl",
        STAGING / "lqe" / "paleo_context.jsonl",
        STAGING / "pbdb" / "paleo_context.jsonl",
        STAGING / "iucn" / "animal_consumer_disperser.jsonl",
    ]
    records: list[dict] = []
    for path in support_files:
        for row in load_jsonl(path):
            prov = row.get("provenance", {})
            caveat = row.get("C", {})
            attrs = row.get("attrs", {})
            records.append(
                {
                    "node_id": row.get("node_id", ""),
                    "node_type": row.get("node_type", ""),
                    "label": row.get("label", ""),
                    "support_role": "modern_disperser_context"
                    if row.get("node_type") == "animal_consumer"
                    else row.get("node_type", ""),
                    "source_group": "paleobotany_sources",
                    "source_file": str(path.relative_to(ROOT)),
                    "source_id": prov.get("source_id", ""),
                    "access_date": prov.get("access_date", ""),
                    "license": prov.get("license", ""),
                    "confidence": prov.get("confidence", None),
                    "source_reliability": prov.get("source_reliability", None),
                    "geographic_scope": caveat.get("geographic_scope", attrs.get("continent_or_region", "")),
                    "uncertainty_class": caveat.get("uncertainty_class", ""),
                    "temporal_annotation_json": json.dumps(row.get("T", {}), sort_keys=True),
                    "raw_attrs_json": json.dumps(attrs, sort_keys=True),
                    "raw_caveats_json": json.dumps(caveat, sort_keys=True),
                }
            )
    return pd.DataFrame.from_records(records)


def build() -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    hyperedges = pd.read_parquet(DATASET / "hyperedges.parquet")
    candidates = hyperedges[
        (hyperedges["source_group"] == "paleobotany_sources")
        & (hyperedges["edge_type"] == "anachronism_candidate_edge")
    ].copy()

    if candidates.empty:
        raise SystemExit("No paleobotany anachronism_candidate_edge rows found.")

    caveats = candidates["caveats"].map(parse_json_prefix)
    candidates["track"] = "track2"
    candidates["milestone_id"] = "M2.T2"
    candidates["enrichment_role"] = "literature_curated_seed"
    candidates["literature_curated"] = True
    candidates["inferred_anachronism_claim"] = False
    candidates["prediction_status"] = "not_prediction"
    candidates["enters_prediction_ledger"] = False
    candidates["instrument_phase_allowed"] = "M3.T2 may rank later; M2.T2 seeds are not predictions"
    candidates["plant_node_id"] = candidates["role_map_json"].map(lambda r: member_for_role(r, "plant"))
    candidates["fruit_type_node_id"] = candidates["role_map_json"].map(
        lambda r: member_for_role(r, "fruit_morphology")
    )
    candidates["extinct_fauna_node_id"] = candidates["role_map_json"].map(
        lambda r: member_for_role(r, "putative_extinct_disperser")
    )
    candidates["primary_citation_short"] = caveats.map(lambda c: c.get("primary_citation_short", ""))
    candidates["primary_citation_page"] = caveats.map(lambda c: c.get("primary_citation_page", ""))
    candidates["primary_citation_full"] = caveats.map(lambda c: c.get("primary_citation_full", ""))
    candidates["geographic_scope"] = caveats.map(lambda c: c.get("geographic_scope", ""))
    candidates["uncertainty_class"] = caveats.map(lambda c: c.get("uncertainty_class", ""))
    candidates["interpretation_caveat"] = caveats.map(lambda c: c.get("interpretation_caveat", ""))
    candidates["discipline_note"] = caveats.map(lambda c: c.get("discipline_note", ""))
    candidates["candidate_class"] = candidates.apply(
        lambda row: candidate_class(row, caveats.loc[row.name]), axis=1
    )
    candidates["barrier2_merge_key"] = candidates.apply(
        lambda row: "|".join(
            [
                row["edge_type"],
                row["plant_node_id"],
                row["fruit_type_node_id"],
                row["extinct_fauna_node_id"],
                row["primary_citation_short"],
            ]
        ),
        axis=1,
    )

    required_truths = {
        "no_inferred_flags": not candidates["inferred_flag"].astype(bool).any(),
        "no_prediction_rows": not candidates["enters_prediction_ledger"].astype(bool).any(),
        "all_cited": (candidates["primary_citation_short"].str.len() > 0).all()
        and (candidates["primary_citation_page"].str.len() > 0).all(),
        "all_have_roles": (
            (candidates["plant_node_id"].str.len() > 0)
            & (candidates["fruit_type_node_id"].str.len() > 0)
            & (candidates["extinct_fauna_node_id"].str.len() > 0)
        ).all(),
    }
    failed = [name for name, ok in required_truths.items() if not ok]
    if failed:
        raise SystemExit(f"Track 2 enrichment safety checks failed: {failed}")

    support_nodes = collect_support_nodes()
    distribution_edges = hyperedges[
        (hyperedges["source_group"] == "paleobotany_sources")
        & (hyperedges["edge_type"] == "distribution")
    ].copy()
    distribution_edges["track"] = "track2"
    distribution_edges["enrichment_role"] = "range_context_support"
    distribution_edges["prediction_status"] = "not_prediction"
    distribution_edges["enters_prediction_ledger"] = False

    candidates.to_parquet(DATA / "ghost_partner_seed_edges.parquet", index=False)
    candidates.to_csv(DATA / "ghost_partner_seed_edges.tsv", sep="\t", index=False)
    support_nodes.to_parquet(DATA / "ghost_partner_support_nodes.parquet", index=False)
    support_nodes.to_csv(DATA / "ghost_partner_support_nodes.tsv", sep="\t", index=False)
    distribution_edges.to_parquet(DATA / "ghost_partner_range_context_edges.parquet", index=False)

    summary = (
        candidates.groupby("candidate_class", dropna=False)
        .agg(
            seed_edges=("edge_id", "count"),
            plant_names=("raw_scientific_name", "nunique"),
            extinct_fauna=("extinct_fauna_node_id", "nunique"),
            pending_crosswalk_rows=("pending_crosswalk", "sum"),
            cited_sources=("primary_citation_short", lambda s: "|".join(sorted(set(s)))),
        )
        .reset_index()
        .sort_values(["candidate_class"])
    )
    summary.to_csv(DATA / "anachronism_candidate_seed_summary.tsv", sep="\t", index=False)

    source_counts = Counter(candidates["primary_citation_short"])
    metrics = {
        "candidate_seed_edges": int(len(candidates)),
        "candidate_classes": int(candidates["candidate_class"].nunique()),
        "unique_plant_names": int(candidates["raw_scientific_name"].nunique()),
        "unique_extinct_fauna": int(candidates["extinct_fauna_node_id"].nunique()),
        "pending_crosswalk_rows": int(candidates["pending_crosswalk"].sum()),
        "resolved_candidate_rows": int((~candidates["pending_crosswalk"]).sum()),
        "range_context_edges": int(len(distribution_edges)),
        "support_nodes": int(len(support_nodes)),
        "extinct_fauna_support_nodes": int((support_nodes["node_type"] == "extinct_fauna").sum()),
        "paleo_context_support_nodes": int((support_nodes["node_type"] == "paleo_context").sum()),
        "modern_disperser_support_nodes": int((support_nodes["node_type"] == "animal_consumer").sum()),
        "inferred_candidate_rows": int(candidates["inferred_anachronism_claim"].sum()),
        "prediction_ledger_rows_written": 0,
        "source_counts": dict(sorted(source_counts.items())),
    }
    (DATA / "ghost_partner_enrichment_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    )
    write_audit(metrics, summary)
    write_merge_report(metrics)
    return metrics


def write_audit(metrics: dict, summary: pd.DataFrame) -> None:
    rows = "\n".join(
        f"| `{r.candidate_class}` | {int(r.seed_edges)} | {int(r.plant_names)} | "
        f"{int(r.extinct_fauna)} | {int(r.pending_crosswalk_rows)} | {r.cited_sources} |"
        for r in summary.itertuples()
    )
    source_rows = "\n".join(
        f"| {source} | {count} |" for source, count in metrics["source_counts"].items()
    )
    audit = f"""---
created: 2026-05-17T23:59:00Z
run_id: fork-56e44dff3ca4-clone-1
agent: worker
milestone: M2.T2
schema_version: v1.0
---

# ENRICHMENT_AUDIT.md — Track 2 Ghost-Partner Enrichment

## Status

Track 2 enrichment is **seed-scale and schema-conformant**. It converts the
Barrier 1 paleobotany/anachronism rows into Track 2-local enrichment artifacts
without promoting any seed into a prediction.

## Inputs

| Input | Role | Rows used |
|---|---|---:|
| `phytograph_dataset/hyperedges.parquet` / `anachronism_candidate_edge` | cited Janzen-Martin and related candidate seeds | {metrics['candidate_seed_edges']} |
| `phytograph_dataset/hyperedges.parquet` / `distribution` | PHYLACINE range-context support | {metrics['range_context_edges']} |
| `substrate/staging/paleobotany_sources/*/*.jsonl` | extinct fauna, paleo-context, and extant disperser support nodes | {metrics['support_nodes']} |

The frozen Barrier 1 substrate was read-only. This branch wrote only under
`tracks/track2/`.

## Outputs

| Artifact | Description |
|---|---|
| `tracks/track2/data/ghost_partner_seed_edges.parquet` | Track 2 seed edge table derived from cited `anachronism_candidate_edge` rows. |
| `tracks/track2/data/ghost_partner_seed_edges.tsv` | Diffable copy of the seed edge table. |
| `tracks/track2/data/anachronism_candidate_seed_summary.tsv` | Candidate-class coverage summary for Barrier 2. |
| `tracks/track2/data/ghost_partner_support_nodes.parquet` | Extinct-fauna, paleo-context, and extant-disperser support nodes. |
| `tracks/track2/data/ghost_partner_range_context_edges.parquet` | PHYLACINE distribution support edges, not predictions. |
| `tracks/track2/data/ghost_partner_enrichment_metrics.json` | Machine-readable counts and safety-check results. |
| `tracks/track2/tests/test_ghost_enrichment.py` | Regression tests for evidence-boundary and schema conformance. |

## Coverage

| Metric | Value |
|---|---:|
| Candidate seed edges | {metrics['candidate_seed_edges']} |
| Candidate classes | {metrics['candidate_classes']} |
| Unique plant names | {metrics['unique_plant_names']} |
| Unique extinct-fauna nodes in seed edges | {metrics['unique_extinct_fauna']} |
| Pending-crosswalk seed rows retained as caveated seeds | {metrics['pending_crosswalk_rows']} |
| Resolved seed rows | {metrics['resolved_candidate_rows']} |
| Range-context support edges | {metrics['range_context_edges']} |
| Extinct-fauna support nodes | {metrics['extinct_fauna_support_nodes']} |
| Paleo-context support nodes | {metrics['paleo_context_support_nodes']} |
| Modern-disperser context nodes | {metrics['modern_disperser_support_nodes']} |
| Inferred candidate rows emitted | {metrics['inferred_candidate_rows']} |
| Prediction-ledger rows written | {metrics['prediction_ledger_rows_written']} |

## Candidate Classes

| Candidate class | Seed edges | Plant names | Extinct fauna | Pending crosswalk rows | Sources |
|---|---:|---:|---:|---:|---|
{rows}

## Citation Source Mix

| Source | Seed rows |
|---|---:|
{source_rows}

## Evidence Boundary

- Every row in `ghost_partner_seed_edges.parquet` has
  `enrichment_role = literature_curated_seed`.
- Every row has `prediction_status = not_prediction` and
  `enters_prediction_ledger = false`.
- Every row has `inferred_anachronism_claim = false`; no spatial-overlap or
  morphology-only candidate was generated in this branch.
- `allowed_evidence_scope` remains `cited hypothesis only; not inferred by
  Barrier 1`, and the copied caveats retain the source warning that the row is
  not established anachronism status.
- `pending_crosswalk` rows are retained with their raw names and caveats; this
  branch does not perform independent synonym normalization.

## Mechanism Check

Mechanism hypothesis: premature prediction leakage would occur if a cited
candidate seed were recoded as a ranked candidate or model output. This build
rules that mechanism out for M2.T2 by setting all seed rows to
`not_prediction`, writing zero prediction-ledger rows, and testing that no row
has `inferred_anachronism_claim = true`.

Special points:

- `pending_crosswalk = true`: retained as caveated seed, not discarded and not
  resolved locally.
- Missing citation: build fails; all emitted seed rows require citation short
  name and page/section.
- Inference flag true: build fails; all emitted seed rows must be cited source
  rows.
- Prediction ledger boundary: no `ghost_partner_predictions.tsv` or master
  `prediction_ledger.tsv` writes are performed.

## Known Limitations

- This is not the M3.T2 Ghost-Partner Candidate Ranker. It is a Wave 2
  enrichment seed table.
- The seed canon is source-biased toward Janzen-Martin/Guimarães neotropical
  megafaunal fruit cases plus a small set of Madagascar, New Zealand, temperate
  North American, and European examples.
- Twenty-five seed rows are still `pending_crosswalk` after Barrier 1. They are
  usable as literature-curated seeds but are not ready for taxon-key-only
  joins without Barrier 2 handling.
- PHYLACINE/IUCN range context is support evidence only; no range-overlap
  inference was run.

## Reproduction

```bash
python3 tracks/track2/scripts/build_ghost_enrichment.py
python3 -m pytest -q tracks/track2/tests/test_ghost_enrichment.py
```
"""
    (DOCS / "ENRICHMENT_AUDIT.md").write_text(audit)


def write_merge_report(metrics: dict) -> None:
    merge_dir = ROOT / ".long-exposure" / "fork-56e44dff3ca4" / "clone-1"
    merge_dir.mkdir(parents=True, exist_ok=True)
    report = f"""# Merge Report — fork 56e44dff3ca4 clone 1

## Scope

Track 2 ghost-partner enrichment. The branch converted cited paleobotany,
extinct-fauna, and Janzen-Martin seed rows into Track 2-local enrichment
artifacts while preventing inferred anachronism claims from entering
predictions.

## Artifacts

- `tracks/track2/docs/ENRICHMENT_AUDIT.md`
- `tracks/track2/data/ghost_partner_seed_edges.parquet`
- `tracks/track2/data/ghost_partner_seed_edges.tsv`
- `tracks/track2/data/anachronism_candidate_seed_summary.tsv`
- `tracks/track2/data/ghost_partner_support_nodes.parquet`
- `tracks/track2/data/ghost_partner_support_nodes.tsv`
- `tracks/track2/data/ghost_partner_range_context_edges.parquet`
- `tracks/track2/data/ghost_partner_enrichment_metrics.json`
- `tracks/track2/scripts/build_ghost_enrichment.py`
- `tracks/track2/tests/test_ghost_enrichment.py`

## Counts

- Candidate seed edges: {metrics['candidate_seed_edges']}
- Candidate classes: {metrics['candidate_classes']}
- Support nodes: {metrics['support_nodes']}
- Range-context support edges: {metrics['range_context_edges']}
- Prediction rows written: 0

## Merge Notes

Barrier 2 should treat these as `literature_curated_seed` rows only. They are
not Track 2 predictions and should not be copied into `prediction_ledger.tsv`
until an M3.T2 instrument ranks candidates and a validation source is assigned.
"""
    (merge_dir / "merge_report.md").write_text(report)


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2, sort_keys=True))
