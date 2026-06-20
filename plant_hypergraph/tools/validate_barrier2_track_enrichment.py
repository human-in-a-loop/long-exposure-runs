# created: 2026-05-18T01:30:00+00:00
# cycle: 8
# run_id: run-phytograph-cycle8-postmerge-integration
# agent: worker
# milestone: _plan/wave2-postmerge-integration

"""Barrier 2 conformance checks for Wave 2 track enrichment outputs.

This validator is deliberately scoped to integration hygiene: track namespace
isolation, evidence-boundary preservation, schema-shaped fields, and known
data-limited divergence items. It does not audit biological correctness and it
does not promote enrichment rows to predictions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "barrier2_track_enrichment_conformance.json"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def read_parquet(rel: str) -> pd.DataFrame:
    path = ROOT / rel
    if not path.exists():
        fail(f"missing required parquet: {rel}")
    return pd.read_parquet(path)


def read_tsv(rel: str) -> pd.DataFrame:
    path = ROOT / rel
    if not path.exists():
        fail(f"missing required TSV: {rel}")
    return pd.read_csv(path, sep="\t")


def require_columns(df: pd.DataFrame, rel: str, columns: set[str]) -> None:
    missing = sorted(columns - set(df.columns))
    if missing:
        fail(f"{rel} missing columns: {missing}")


def all_false(series: pd.Series) -> bool:
    return series.fillna(False).astype(bool).eq(False).all()


def main() -> int:
    findings: list[dict[str, Any]] = []
    checks: list[str] = []

    for track in range(1, 7):
        rel = f"tracks/track{track}/docs/ENRICHMENT_AUDIT.md"
        if not (ROOT / rel).exists():
            fail(f"missing track audit: {rel}")
    checks.append("all six ENRICHMENT_AUDIT.md files exist")

    master_prediction = ROOT / "prediction_ledger.tsv"
    if master_prediction.exists():
        pred = pd.read_csv(master_prediction, sep="\t")
        if len(pred) != 0:
            fail("master prediction_ledger.tsv has rows during enrichment integration")
    checks.append("master prediction_ledger.tsv remains empty")

    t1 = read_parquet("tracks/track1/data/reticulation_enrichment_edges.parquet")
    require_columns(
        t1,
        "track1 reticulation enrichment",
        {
            "edge_type",
            "accepted_taxon_key",
            "pending_crosswalk",
            "canonical_node_ids_json",
            "allowed_evidence_scope",
            "caveats_json",
        },
    )
    expected_t1 = {
        "chromosome_count_assertion",
        "ploidy_state_assertion",
        "hybridization_event",
        "polyploidization_event",
        "reticulate_inheritance_evidence",
    }
    if len(t1) != 28 or set(t1["edge_type"]) != expected_t1:
        fail("Track 1 row count or edge-type set changed")
    t1_pending = int(t1["pending_crosswalk"].fillna(False).astype(bool).sum())
    t1_resolved = int((t1["accepted_taxon_key"].fillna("") != "").sum())
    if (t1_pending, t1_resolved) != (25, 3):
        fail(f"Track 1 expected 25 pending and 3 resolved, got {t1_pending}/{t1_resolved}")
    if t1["canonical_node_ids_json"].fillna("").str.contains("tree_compatibility_index").any():
        fail("Track 1 leaked tree_compatibility_index into enrichment")
    findings.append(
        {
            "track": "track1",
            "status": "ready_data_limited",
            "finding": "28 seed rows retained; canonical validation seeds remain mostly pending_crosswalk.",
        }
    )

    t2_seed = read_parquet("tracks/track2/data/ghost_partner_seed_edges.parquet")
    t2_range = read_parquet("tracks/track2/data/ghost_partner_range_context_edges.parquet")
    require_columns(
        t2_seed,
        "track2 seed edges",
        {
            "edge_type",
            "prediction_status",
            "enters_prediction_ledger",
            "inferred_anachronism_claim",
            "pending_crosswalk",
            "candidate_class",
        },
    )
    if len(t2_seed) != 31 or len(t2_range) != 52:
        fail("Track 2 expected 31 seed edges and 52 range-context edges")
    if not t2_seed["prediction_status"].eq("not_prediction").all():
        fail("Track 2 seed edge promoted to prediction_status other than not_prediction")
    if not all_false(t2_seed["enters_prediction_ledger"]):
        fail("Track 2 seed edge marked for prediction ledger")
    if not all_false(t2_seed["inferred_anachronism_claim"]):
        fail("Track 2 inferred anachronism claim emitted during enrichment")
    findings.append(
        {
            "track": "track2",
            "status": "ready_seed_scale",
            "finding": "31 cited seeds and 52 range-context supports remain not_prediction.",
        }
    )

    t3 = read_parquet("tracks/track3/data/convergence_trait_edges.parquet")
    t3_summary = read_tsv("tracks/track3/data/trait_coverage_summary.tsv")
    require_columns(
        t3,
        "track3 convergence trait edges",
        {"track_edge_type", "trait", "pending_crosswalk", "allowed_evidence_scope"},
    )
    if len(t3) != 209_297:
        fail(f"Track 3 expected 209297 trait rows, got {len(t3)}")
    if not t3["track_edge_type"].eq("track3_trait_membership").all():
        fail("Track 3 emitted a non-membership track edge type")
    if t3.astype(str).apply(lambda col: col.str.contains("convergence_signature", regex=False)).any().any():
        fail("Track 3 leaked convergence_signature into enrichment")
    canonical_summary = t3_summary[t3_summary["trait"] != "_other"]
    floor_met = sorted(canonical_summary.loc[canonical_summary["floor_met_500_taxa"] == "yes", "trait"].tolist())
    if floor_met != ["capsule", "fleshy_fruit"]:
        fail(f"Track 3 expected only capsule and fleshy_fruit to meet floor, got {floor_met}")
    other_rows = int(t3_summary.loc[t3_summary["trait"] == "_other", "n_retained_edges"].iloc[0])
    findings.append(
        {
            "track": "track3",
            "status": "ready_with_conformance_review_item",
            "finding": f"209297 memberships retained; _other bucket has {other_rows} rows and must be interpreted explicitly at Barrier 2.",
        }
    )

    t4 = read_parquet("tracks/track4/data/domestication_enrichment_edges.parquet")
    t4_cov = read_tsv("tracks/track4/data/crop_cwr_coverage_summary.tsv")
    t4_climate = read_tsv("tracks/track4/data/climate_envelope_coverage.tsv")
    t4_heldout = read_tsv("tracks/track4/data/heldout_validation_seed.tsv")
    require_columns(t4, "track4 domestication edges", {"edge_type", "accepted_taxon_key", "pending_crosswalk", "evidence_status"})
    if len(t4) != 6 or int(t4_cov["unjoined_rows"].sum()) != 609:
        fail("Track 4 expected 6 retained edges and 609 unjoined/data-limited rows across coverage table")
    if t4_climate["bioclim_values_present"].fillna(False).astype(bool).any():
        fail("Track 4 climate placeholders unexpectedly contain observed bioclim values")
    if t4_heldout["overlaps_training_pedigree"].fillna(False).astype(bool).any():
        fail("Track 4 held-out seed overlaps retained crop-pedigree training evidence")
    findings.append(
        {
            "track": "track4",
            "status": "ready_data_limited",
            "finding": "6 observed edges retained; CWR joins and all bioclim vectors remain data-limited.",
        }
    )

    t5 = read_parquet("tracks/track5/data/track5_enrichment_edges.parquet")
    t5_bio = read_parquet("tracks/track5/data/track5_bioactivity_assertions.parquet")
    t5_classes = read_parquet("tracks/track5/data/track5_compound_class_membership.parquet")
    t5_source = read_tsv("tracks/track5/data/source_density_diagnostics.tsv")
    require_columns(t5, "track5 enrichment edges", {"edge_type", "accepted_taxon_key", "pending_crosswalk", "source_class"})
    if len(t5) != 23_524 or len(t5_bio) != 28_733 or len(t5_classes) != 9_500:
        fail("Track 5 expected enrichment/bioactivity/compound-class row counts changed")
    if t5["pending_crosswalk"].fillna(True).astype(bool).any():
        fail("Track 5 resolved taxon-keyed enrichment contains pending_crosswalk rows")
    if "accepted_taxon_key" in t5_bio.columns:
        fail("Track 5 bioactivity firewall broken: compound-level file has accepted_taxon_key")
    duke_share = float(t5_source.loc[t5_source["source_id"].str.contains("Duke", regex=False), "share_of_total_edges"].iloc[0])
    if duke_share < 0.99:
        fail("Track 5 expected Dr. Duke source-dominance diagnostic is no longer present")
    findings.append(
        {
            "track": "track5",
            "status": "ready_with_source_bias_warning",
            "finding": f"23524 resolved taxon-keyed rows retained; Duke share of combined signal is {duke_share:.6f}.",
        }
    )

    t6_q = read_parquet("tracks/track6/data/offline_probe_question_bank.parquet")
    t6_edges = read_parquet("tracks/track6/data/probe_ground_truth_edges.parquet")
    require_columns(t6_q, "track6 offline questions", {"category", "offline_only", "status"})
    require_columns(t6_edges, "track6 ground truth edges", {"edge_type", "role_map_json", "allowed_evidence_scope"})
    if len(t6_q) != 210 or len(t6_edges) != 210:
        fail("Track 6 expected 210 questions and 210 ground-truth edges")
    if not t6_q["offline_only"].fillna(False).astype(bool).all():
        fail("Track 6 contains non-offline probe question rows")
    if not t6_edges["edge_type"].eq("adversarial_probe_edge").all():
        fail("Track 6 ground-truth file contains non-adversarial probe edge")
    if not t6_edges["role_map_json"].fillna("").str.contains("offline_unrun", regex=False).all():
        fail("Track 6 expected offline_unrun placeholder missing from at least one row")
    findings.append(
        {
            "track": "track6",
            "status": "ready_offline_static",
            "finding": "210 offline questions and schema-shaped adversarial_probe_edge rows retained; no live responses present.",
        }
    )

    result = {
        "status": "PASS",
        "scope": "Barrier 2 Wave 2 enrichment integration conformance only",
        "checks": checks,
        "findings": findings,
        "nonblocking_review_items": [
            "Track 1 canonical polyploid validation seeds remain pending or absent.",
            "Track 3 _other bucket is large under strict headline counting.",
            "Track 4 crop/CWR and climate coverage is sparse.",
            "Track 5 is Dr. Duke dominated and must carry source-density ablations.",
            "Track 6 is an offline static benchmark only; provider scoring is absent by design.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: Barrier 2 track enrichment conformance ({len(findings)} tracks checked)")
    print(f"WROTE: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
