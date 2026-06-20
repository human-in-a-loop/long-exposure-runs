"""
PhytoGraph Botanical Atlas — Wave 3 / M3.A static-site builder.

Header metadata (artifact-tracking):
  created: 2026-05-18T03:00:00+00:00
  cycle: 9
  run_id: run-phytograph-cycle9-wave3-atlas
  agent: worker
  milestone: M3.A

Reads:  phytograph_dataset/*.parquet (read-only frozen substrate)
        tracks/track*/data/*           (read-only Wave-2/3 track outputs)
Writes: botanical_atlas_site/pages/<accepted_key>.json (one per accepted-key taxon)
        botanical_atlas_site/search_index.json
        botanical_atlas_site/coverage_summary.json
        botanical_atlas_site/provenance_registry.json
        botanical_atlas_site/counter_claim_template.json
        botanical_atlas_site/index.html
        botanical_atlas_site/app.js
        botanical_atlas_site/style.css
        botanical_atlas_site/build_log.json

The Atlas is a research instrument: every rendered claim is labelled with
its evidence class (observed | enriched | predicted | data-limited) and its
provenance. No row without a `provenance_ref` is rendered. If a Wave-3
instrument output is absent, the per-track section renders an explicit
`instrument_pending` placeholder, NEVER a fabricated prediction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SUBSTRATE = ROOT / "phytograph_dataset"
TRACKS = ROOT / "tracks"
SITE = ROOT / "botanical_atlas_site"
PAGES = SITE / "pages"

# Source group -> Track number. Determines which per-track section an edge
# is rendered under. Each source_group is a Wave-2 enrichment except
# taxonomy_backbone and wikidata_commons, which are substrate-level.
SOURCE_GROUP_TO_TRACK: dict[str, int | None] = {
    "taxonomy_backbone": None,           # header/substrate
    "wikidata_commons": None,            # media/crosswalk
    "reticulation_sources": 1,
    "paleobotany_sources": 2,
    "convergence_sources": 3,
    "domestication_sources": 4,
    "chemodiversity_ethnobotany_sources": 5,
    # Track 6 lives outside the substrate (offline probe ground-truth only).
}

TRACK_TITLES = {
    1: "Reticulation Atlas",
    2: "Ghost Hyperedges",
    3: "Convergence Pressure",
    4: "Domestication Hypergraph",
    5: "Chemodiversity Predictor",
    6: "Foundation-Model Probe",
}

# Default evidence class per edge_type. Refined per-row if inferred_flag=true
# (-> predicted) or pending_crosswalk=true (band still ENRICHED but caveat
# shown explicitly). taxonomy_backbone and substrate-merged Wave-2 rows are
# OBSERVED if they cite primary literature, otherwise ENRICHED.
EDGE_TYPE_DEFAULT_CLASS: dict[str, str] = {
    # taxonomy_backbone / wikidata
    "taxonomic_parentage": "observed",
    "synonym_cluster": "observed",
    "image_evidence": "observed",
    "distribution": "observed",
    "taxonomic_conflict": "observed",
    # Track 1
    "chromosome_count_assertion": "enriched",
    "ploidy_state_assertion": "enriched",
    "hybridization_event": "enriched",
    "polyploidization_event": "enriched",
    "reticulate_inheritance_evidence": "enriched",
    # Track 2
    "anachronism_candidate_edge": "enriched",
    # Track 3
    "trait_syndrome": "enriched",
    "fruit_morphology": "enriched",
    "life_form": "observed",
    # Track 4
    "crop_pedigree": "enriched",
    "vavilov_center_hyperedge": "enriched",
    "cultivation_or_domestication": "enriched",
    # Track 5
    "phytochemical_assertion": "enriched",
    "bioactivity_assertion": "enriched",
    "ethnobotanical_use_assertion": "enriched",
    # Track 6
    "adversarial_probe_edge": "enriched",
}

ATLAS_OUTPUT_CONTRACT = {
    1: {
        "mode": "prediction_adapter",
        "expected": ["tracks/track1/outputs/tci_per_taxon.tsv",
                     "tracks/track1/outputs/tci_hotspots_genus.tsv"],
        "reason": "Expose Track 1 TCI instrument rows as data-limited instrument results, not validated reticulation claims.",
    },
    2: {
        "mode": "prediction_adapter",
        "expected": ["tracks/track2/data/ghost_partner_candidate_scores.tsv",
                     "tracks/track2/data/ghost_partner_predictions.tsv"],
        "reason": "Expose accepted-key resolved candidate-prioritization rows as predictions awaiting validation.",
    },
    3: {
        "mode": "prediction_adapter",
        "expected": ["tracks/track3/data/convergence_pressure_scores.tsv",
                     "tracks/track3/data/convergence_predictions.tsv"],
        "reason": "Expose Track 3 pending convergence-prior rows on carrier pages as hypotheses awaiting validation.",
    },
    4: {
        "mode": "prediction_adapter",
        "expected": ["tracks/track4/data/crop_substitution_candidates.tsv"],
        "reason": "Expose data-limited crop-substitution candidate rows on crop and candidate taxon pages.",
    },
    5: {
        "mode": "prediction_adapter",
        "expected": ["tracks/track5/data/phytochemistry_predictions.tsv"],
        "reason": "Expose pending screening-prior phytochemistry rows with source-dominance caveats.",
    },
    6: {
        "mode": "prediction_adapter",
        "expected": ["tracks/track6/data/probe_results.tsv",
                     "tracks/track6/data/offline_probe_question_bank.tsv"],
        "reason": "Expose deterministic offline probe result rows joined to accepted-key question-bank rows.",
    },
}


def load_substrate() -> dict[str, pd.DataFrame]:
    nodes = pd.read_parquet(SUBSTRATE / "nodes.parquet")
    edges = pd.read_parquet(SUBSTRATE / "hyperedges.parquet")
    cross = pd.read_parquet(SUBSTRATE / "taxon_crosswalk.parquet")
    syn = pd.read_parquet(SUBSTRATE / "synonym_resolution.parquet")
    src = pd.read_parquet(SUBSTRATE / "source_registry.parquet")
    return {"nodes": nodes, "edges": edges, "crosswalk": cross,
            "synonyms": syn, "sources": src}


def load_track6_probes() -> pd.DataFrame:
    p = TRACKS / "track6" / "data" / "probe_ground_truth_edges.parquet"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_parquet(p)


def detect_wave3_instruments() -> dict[int, dict[str, Any]]:
    """Probe the Atlas integration contract for each track."""
    out = {}
    for tid, contract in ATLAS_OUTPUT_CONTRACT.items():
        present = []
        for rel in contract["expected"]:
            p = ROOT / rel
            if p.exists():
                present.append(rel)
        out[tid] = {"present": bool(present), "paths": present,
                    "expected": contract["expected"],
                    "mode": contract["mode"],
                    "reason": contract["reason"],
                    "sibling_clone": f"M3.T{tid} (sibling fan-out clone)"}
    return out


def _clean_key(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _prediction_payload(**kwargs: Any) -> dict[str, Any]:
    payload = {
        "edge_id": kwargs["edge_id"],
        "edge_type": kwargs.get("edge_type", "atlas_prediction_row"),
        "source_group": kwargs.get("source_group", "atlas_prediction_adapter"),
        "source_id": kwargs.get("source_id"),
        "source_record_id": kwargs.get("source_record_id"),
        "access_date": kwargs.get("access_date", "2026-05-18"),
        "license": kwargs.get("license", "derived from cited track-local source rows"),
        "provenance_pointer": kwargs.get("provenance_pointer"),
        "allowed_evidence_scope": kwargs.get("allowed_evidence_scope"),
        "confidence": kwargs.get("confidence"),
        "source_reliability": kwargs.get("source_reliability"),
        "pending_crosswalk": bool(kwargs.get("pending_crosswalk", False)),
        "inferred_flag": True,
        "caveats": kwargs.get("caveats"),
        "role_map_json": kwargs.get("role_map_json"),
        "raw_scientific_name": kwargs.get("raw_scientific_name"),
        "prediction_statement": kwargs.get("prediction_statement"),
        "expected_validation_source": kwargs.get("expected_validation_source"),
        "status": kwargs.get("status"),
        "score": kwargs.get("score"),
        "rank": kwargs.get("rank"),
        "track_output_path": kwargs.get("track_output_path"),
    }
    return payload


def load_instrument_predictions() -> dict[int, dict[str, list[dict]]]:
    """Load accepted-keyed prediction/result rows from existing track outputs.

    The adapters are deliberately narrow: they do not infer biology, promote
    master-ledger rows, or write into track namespaces. They only make existing
    track-local outputs queryable from the Atlas under the PREDICTED band.
    """
    predictions: dict[int, dict[str, list[dict]]] = {
        t: defaultdict(list) for t in range(1, 7)
    }

    # Track 1: per-taxon tree-compatibility index. These rows are instrument
    # outputs, not validation claims; current confidence is generally
    # data_limited because canonical polyploid recovery is blocked by
    # accepted-key coverage.
    t1 = TRACKS / "track1" / "outputs" / "tci_per_taxon.tsv"
    if t1.exists():
        df = pd.read_csv(t1, sep="\t")
        for rec in df.to_dict("records"):
            key = _clean_key(rec.get("accepted_key"))
            if not key:
                continue
            tci = rec.get("tci")
            label = rec.get("label") or key
            predictions[1][key].append(_prediction_payload(
                edge_id=f"atlas:track1:tci:{key}",
                edge_type="tree_compatibility_index_result",
                source_group="track1_reticulation_atlas",
                source_id="tracks/track1/outputs/tci_per_taxon.tsv",
                source_record_id=key,
                provenance_pointer="tracks/track1/reports/track1_reticulation_atlas.md",
                allowed_evidence_scope=(
                    "Per-taxon TCI instrument result over accepted-key resolved "
                    "evidence; supports data-limited prioritization, not a "
                    "validated reticulation or single-parent inheritance claim."
                ),
                confidence=rec.get("confidence"),
                caveats=(
                    f"tci_provenance={rec.get('tci_provenance')}; "
                    "chromosome-count and ploidy-state rows are structural "
                    "context only."
                ),
                raw_scientific_name=label,
                prediction_statement=(
                    f"Track 1 TCI instrument result for {label}: "
                    f"tree_compatibility_index={tci}; confidence={rec.get('confidence')}."
                ),
                expected_validation_source=(
                    "Barrier 4 canonical polyploid/hybrid held-out validation "
                    "after accepted-key coverage repair."
                ),
                status=rec.get("confidence"),
                score=tci,
                rank=rec.get("tci_provenance"),
                track_output_path=str(t1.relative_to(ROOT)),
            ))

    # Track 3: pending convergence-prior hypotheses. The prediction TSV is
    # trait-level, so this adapter projects rows onto the accepted-key pages
    # named by their listed supporting hyperedges. The source TSV intentionally
    # truncates long support lists, so page coverage is a queryability sample,
    # not an exhaustive carrier enumeration.
    t3 = TRACKS / "track3" / "data" / "convergence_predictions.tsv"
    if t3.exists():
        preds = pd.read_csv(t3, sep="\t")
        edge_key = {}
        substrate_edges = SUBSTRATE / "hyperedges.parquet"
        if substrate_edges.exists():
            edges = pd.read_parquet(
                substrate_edges, columns=["edge_id", "accepted_taxon_key"])
            edge_key = dict(zip(edges["edge_id"], edges["accepted_taxon_key"]))
        for rec in preds.to_dict("records"):
            if rec.get("row_class") != "pending_convergent_trait_hypothesis":
                continue
            support = str(rec.get("supporting_hyperedges") or "")
            supporting_edges = [
                e for e in support.split(";")
                if e and not e.startswith("...(") and e in edge_key
            ]
            seen_keys = set()
            for edge_id in supporting_edges:
                key = _clean_key(edge_key.get(edge_id))
                if not key or key in seen_keys:
                    continue
                seen_keys.add(key)
                predictions[3][key].append(_prediction_payload(
                    edge_id=f"atlas:track3:{rec.get('prediction_id')}:{edge_id}",
                    edge_type="convergence_pressure_hypothesis",
                    source_group="track3_convergence_pressure",
                    source_id="tracks/track3/data/convergence_predictions.tsv",
                    source_record_id=rec.get("prediction_id"),
                    provenance_pointer=edge_id,
                    allowed_evidence_scope=rec.get("observed_evidence_scope"),
                    confidence=rec.get("CP_min"),
                    caveats=rec.get("hypothesis_caveat"),
                    prediction_statement=rec.get("prediction_statement"),
                    expected_validation_source=rec.get("expected_validation_source"),
                    status=rec.get("status"),
                    score=rec.get("score"),
                    rank=rec.get("rank"),
                    track_output_path=str(t3.relative_to(ROOT)),
                ))

    # Track 2: candidate-prioritization output. Join prose prediction rows
    # onto accepted-key-resolved candidate score rows.
    t2_scores = TRACKS / "track2" / "data" / "ghost_partner_candidate_scores.tsv"
    t2_preds = TRACKS / "track2" / "data" / "ghost_partner_predictions.tsv"
    if t2_scores.exists():
        scores = pd.read_csv(t2_scores, sep="\t")
        if t2_preds.exists():
            preds = pd.read_csv(t2_preds, sep="\t")
            scores = scores.merge(preds, on="candidate_id", how="left",
                                  suffixes=("", "_prediction"))
        for rec in scores.to_dict("records"):
            key = _clean_key(rec.get("accepted_taxon_key"))
            if not key:
                continue
            predictions[2][key].append(_prediction_payload(
                edge_id=f"atlas:track2:{rec.get('candidate_id')}",
                edge_type="ghost_partner_candidate_prediction",
                source_group="track2_ghost_partner_ranker",
                source_id=rec.get("primary_citation_short"),
                source_record_id=rec.get("source_edge_id"),
                provenance_pointer=rec.get("source_edge_id"),
                allowed_evidence_scope=rec.get("allowed_evidence_scope"),
                confidence=rec.get("candidate_score"),
                pending_crosswalk=rec.get("pending_crosswalk", False),
                caveats=rec.get("hypothesis_caveat") or rec.get("interpretation_caveat"),
                raw_scientific_name=rec.get("raw_scientific_name"),
                prediction_statement=rec.get("prediction_statement") or rec.get("evidence_boundary"),
                expected_validation_source=rec.get("expected_validation_source"),
                status=rec.get("status") or rec.get("candidate_status"),
                score=rec.get("candidate_score"),
                rank=rec.get("rank"),
                track_output_path=str(t2_scores.relative_to(ROOT)),
            ))

    # Track 4: data-limited crop-substitution candidates. Render on both crop
    # and wild-relative pages so researchers can navigate either endpoint.
    t4 = TRACKS / "track4" / "data" / "crop_substitution_candidates.tsv"
    if t4.exists():
        df = pd.read_csv(t4, sep="\t")
        for rec in df.to_dict("records"):
            base = dict(
                edge_type="crop_substitution_candidate_prediction",
                source_group="track4_crop_substitution_engine",
                source_id=rec.get("supporting_source_id"),
                source_record_id=rec.get("supporting_edge_id"),
                provenance_pointer=rec.get("supporting_edge_id"),
                allowed_evidence_scope=rec.get("allowed_evidence_scope"),
                confidence=rec.get("substitution_score_non_climate"),
                caveats=rec.get("claim_boundary") or rec.get("climate_shortfall_reason"),
                expected_validation_source=rec.get("expected_validation_source"),
                status=rec.get("prediction_status"),
                score=rec.get("substitution_score_non_climate"),
                rank=rec.get("rank_within_crop"),
                track_output_path=str(t4.relative_to(ROOT)),
            )
            crop_key = _clean_key(rec.get("crop_accepted_taxon_key"))
            wild_key = _clean_key(rec.get("candidate_wild_relative_key"))
            statement = (
                f"Candidate substitute for {rec.get('crop_taxon')}: "
                f"{rec.get('candidate_wild_relative')} (non-climate score "
                f"{rec.get('substitution_score_non_climate')}; climate status "
                f"{rec.get('climate_match_status')})."
            )
            if crop_key:
                predictions[4][crop_key].append(_prediction_payload(
                    edge_id=f"atlas:track4:crop:{rec.get('candidate_id')}",
                    prediction_statement=statement,
                    **base,
                ))
            if wild_key:
                predictions[4][wild_key].append(_prediction_payload(
                    edge_id=f"atlas:track4:wild:{rec.get('candidate_id')}",
                    prediction_statement=(
                        f"Wild-relative candidate for crop {rec.get('crop_taxon')}: "
                        f"{rec.get('candidate_wild_relative')}."
                    ),
                    **base,
                ))

    # Track 5: pending screening-prior phytochemistry predictions.
    t5 = TRACKS / "track5" / "data" / "phytochemistry_predictions.tsv"
    if t5.exists():
        df = pd.read_csv(t5, sep="\t")
        for i, rec in enumerate(df.to_dict("records")):
            key = _clean_key(rec.get("taxon_accepted_key"))
            if not key:
                continue
            predictions[5][key].append(_prediction_payload(
                edge_id=f"atlas:track5:{key}:{rec.get('predicted_compound_class')}:{i}",
                edge_type="phytochemistry_screening_prior_prediction",
                source_group="track5_chemodiversity_predictor",
                source_id=rec.get("dominant_source"),
                source_record_id=rec.get("supporting_hyperedges"),
                provenance_pointer=rec.get("supporting_hyperedges"),
                allowed_evidence_scope=rec.get("evidence_scope"),
                confidence=rec.get("score"),
                caveats=(
                    f"dominant_source={rec.get('dominant_source')}; "
                    f"duke_share_in_family={rec.get('duke_share_in_family')}; "
                    "prediction is a screening prior, not detection/bioactivity/safety."
                ),
                prediction_statement=rec.get("prediction_statement"),
                expected_validation_source=rec.get("expected_validation_source"),
                status=rec.get("status"),
                score=rec.get("score"),
                rank=rec.get("family_quantile"),
                track_output_path=str(t5.relative_to(ROOT)),
            ))

    # Track 6: deterministic offline results joined to accepted-key question
    # bank rows. These are benchmark results for local controls, not paid API
    # model evaluations.
    t6_results = TRACKS / "track6" / "data" / "probe_results.tsv"
    t6_q = TRACKS / "track6" / "data" / "offline_probe_question_bank.tsv"
    if t6_results.exists() and t6_q.exists():
        results = pd.read_csv(t6_results, sep="\t")
        questions = pd.read_csv(t6_q, sep="\t")
        merged = results.merge(questions, on=["question_id", "category"], how="left",
                               suffixes=("", "_question"))
        for rec in merged.to_dict("records"):
            key = _clean_key(rec.get("accepted_taxon_key"))
            if not key:
                continue
            predictions[6][key].append(_prediction_payload(
                edge_id=f"atlas:track6:{rec.get('model_id')}:{rec.get('question_id')}",
                edge_type="offline_probe_result",
                source_group="track6_offline_probe_runner",
                source_id=rec.get("model_id"),
                source_record_id=rec.get("question_id"),
                provenance_pointer=rec.get("source_edge_id"),
                allowed_evidence_scope=rec.get("allowed_evidence_scope"),
                confidence=1.0 if rec.get("result_role") == "negative_control" else 0.8,
                caveats=rec.get("control_caveat") or rec.get("caveats"),
                raw_scientific_name=rec.get("raw_scientific_name"),
                prediction_statement=(
                    f"Offline probe result for {rec.get('model_id')} on "
                    f"{rec.get('category')}: status={rec.get('result_status')}, "
                    f"passed={rec.get('passed')}, provider_execution={rec.get('provider_execution')}."
                ),
                expected_validation_source="Barrier 4 model-run reconciliation if free/open/local model execution becomes available.",
                status=rec.get("result_status"),
                score=1 if rec.get("passed") is True else 0,
                rank=rec.get("result_role"),
                track_output_path=str(t6_results.relative_to(ROOT)),
            ))

    return predictions


def build_taxon_index(nodes: pd.DataFrame, cross: pd.DataFrame,
                      syn: pd.DataFrame) -> pd.DataFrame:
    """One row per accepted_taxon_key with display fields."""
    taxon_nodes = nodes[nodes.node_type.isin([
        "species", "genus", "family", "taxon", "infraspecific_unit"
    ])].copy()
    # Map accepted_taxon_key -> primary (accepted) label
    keyed = taxon_nodes.dropna(subset=["accepted_taxon_key"])
    # Prefer species > genus > family > taxon rank for display
    rank_pref = {"species": 0, "infraspecific_unit": 1, "genus": 2,
                 "family": 3, "taxon": 4}
    keyed = keyed.assign(_r=keyed.node_type.map(rank_pref).fillna(9))
    keyed = keyed.sort_values("_r").drop_duplicates(
        "accepted_taxon_key", keep="first")

    # Crosswalk display fields
    cross_small = cross[["accepted_taxon_key", "wfo_accepted_name",
                         "gbif_accepted_name", "opentree_accepted_name",
                         "powo_accepted_name", "wfo_id", "gbif_taxon_key",
                         "ott_id", "powo_id"]].drop_duplicates(
        "accepted_taxon_key")
    df = keyed.merge(cross_small, on="accepted_taxon_key", how="left")

    # Synonym aggregation
    syn_clusters = syn[syn.edge_type == "synonym_cluster"]
    syn_map = syn_clusters.groupby("accepted_taxon_key")["raw_scientific_name"]\
        .apply(lambda s: sorted(set(s))[:8]).to_dict()
    df["synonyms"] = df.accepted_taxon_key.map(syn_map).apply(
        lambda x: x if isinstance(x, list) else [])

    # Family/genus breadcrumb via WFO label parsing (best-effort).
    # accepted name "Genus species" -> infer genus.
    def infer_genus(row):
        nm = row.get("wfo_accepted_name") or row.get("label") or ""
        parts = str(nm).split()
        return parts[0] if parts and parts[0][:1].isupper() else ""
    df["genus_label"] = df.apply(infer_genus, axis=1)

    # Display name fallback chain
    df["display_name"] = (df.wfo_accepted_name.fillna(df.label)
                          .fillna(df.accepted_taxon_key))
    return df


def classify_edge(edge: dict, source_group: str) -> tuple[int | None, str]:
    """Return (track_id_or_None, evidence_class) for a hyperedge row."""
    track = SOURCE_GROUP_TO_TRACK.get(source_group)
    et = edge.get("edge_type", "")
    default = EDGE_TYPE_DEFAULT_CLASS.get(et, "enriched")
    # inferred_flag promotes to predicted
    if edge.get("inferred_flag"):
        return track, "predicted"
    return track, default


def edge_to_payload(row: dict) -> dict:
    """Reduce a hyperedge row to a serialisable JSON payload for a page."""
    return {
        "edge_id": row["edge_id"],
        "edge_type": row["edge_type"],
        "source_group": row["source_group"],
        "source_id": row["source_id"],
        "source_record_id": row.get("source_record_id"),
        "access_date": row.get("access_date"),
        "license": row.get("license"),
        "provenance_pointer": row.get("provenance_pointer"),
        "allowed_evidence_scope": row.get("allowed_evidence_scope"),
        "confidence": row.get("confidence"),
        "source_reliability": row.get("source_reliability"),
        "pending_crosswalk": bool(row.get("pending_crosswalk")),
        "inferred_flag": bool(row.get("inferred_flag")),
        "caveats": row.get("caveats"),
        "role_map_json": row.get("role_map_json"),
        "raw_scientific_name": row.get("raw_scientific_name"),
    }


def build_pages(taxon_idx: pd.DataFrame,
                edges: pd.DataFrame,
                probe6: pd.DataFrame,
                instruments: dict[int, dict[str, Any]],
                instrument_predictions: dict[int, dict[str, list[dict]]],
                limit: int | None = None) -> tuple[dict, list[dict]]:
    """Emit one JSON per accepted-key taxon. Returns (coverage_summary, search_rows)."""
    PAGES.mkdir(parents=True, exist_ok=True)
    # Group substrate edges by accepted_taxon_key for O(1) lookup.
    edges_keyed = edges.dropna(subset=["accepted_taxon_key"])
    by_key: dict[str, list[dict]] = defaultdict(list)
    for rec in edges_keyed.to_dict("records"):
        by_key[rec["accepted_taxon_key"]].append(rec)

    # Track 6 probe edges by accepted_taxon_key
    probe_by_key: dict[str, list[dict]] = defaultdict(list)
    if not probe6.empty:
        for rec in probe6.dropna(subset=["accepted_taxon_key"]).to_dict("records"):
            probe_by_key[rec["accepted_taxon_key"]].append(rec)

    coverage = {t: Counter() for t in range(1, 7)}
    search_rows = []
    pages_written = 0

    iterable = taxon_idx.itertuples(index=False)
    for i, tx in enumerate(iterable):
        if limit is not None and i >= limit:
            break
        key = _clean_key(tx.accepted_taxon_key)
        if not key:
            continue

        # Per-track buckets
        track_sections: dict[int, dict] = {
            t: {"observed": [], "enriched": [], "predicted": []}
            for t in range(1, 7)
        }
        header_edges = []  # taxonomy, synonyms, image, distribution

        for e in by_key.get(key, []):
            sg = e.get("source_group", "")
            track, klass = classify_edge(e, sg)
            payload = edge_to_payload(e)
            if track is None:
                header_edges.append(payload)
            else:
                track_sections[track][klass].append(payload)

        # Track 6 probe ground-truth (lives outside substrate)
        for e in probe_by_key.get(key, []):
            payload = {
                "edge_id": e.get("edge_id"),
                "edge_type": e.get("edge_type", "adversarial_probe_edge"),
                "source_group": "track6_offline_probe",
                "source_id": e.get("source_id"),
                "source_record_id": e.get("source_record_id"),
                "access_date": e.get("access_date"),
                "license": e.get("license"),
                "provenance_pointer": e.get("provenance_pointer"),
                "allowed_evidence_scope": e.get("allowed_evidence_scope"),
                "confidence": e.get("confidence"),
                "pending_crosswalk": False,
                "inferred_flag": False,
                "caveats": e.get("caveats"),
                "category": e.get("category"),
                "question_id": e.get("question_id"),
            }
            track_sections[6]["enriched"].append(payload)

        # Per-track section state: observed/enriched/predicted/data-limited
        per_track_render = {}
        for t in range(1, 7):
            sec = track_sections[t]
            has_substrate = any(sec[k] for k in ("observed", "enriched"))
            inst = instruments[t]
            rows_for_track = instrument_predictions.get(t, {}).get(key, [])
            sec["predicted"].extend(rows_for_track)
            if not has_substrate and not rows_for_track:
                state = "data-limited"
            else:
                # Prefer the strongest band visible: predicted > enriched > observed
                if sec["predicted"]:
                    state = "predicted"
                elif sec["enriched"]:
                    state = "enriched"
                else:
                    state = "observed"
            coverage[t][state] += 1
            placeholder_only = inst["mode"] == "contract_placeholder"
            per_track_render[t] = {
                "title": TRACK_TITLES[t],
                "state": state,
                "observed": sec["observed"],
                "enriched": sec["enriched"],
                "predicted": sec["predicted"],
                "instrument_pending": placeholder_only or not inst["present"],
                "instrument_expected_files": inst["expected"],
                "instrument_mode": inst["mode"],
                "instrument_contract_reason": inst["reason"],
                "instrument_sibling_clone": inst["sibling_clone"],
                "data_limited_reason": (
                    f"No Track {t} substrate or instrument rows for this "
                    "accepted key under the Atlas integration contract."
                ) if state == "data-limited" else "",
            }

        # Build neighborhood subgraph (small: substrate edges only).
        neighborhood = {
            "accepted_taxon_key": key,
            "edges": [
                {"edge_id": e["edge_id"], "edge_type": e["edge_type"],
                 "source_group": e.get("source_group")}
                for e in by_key.get(key, [])
            ],
        }

        page = {
            "schema_version": "atlas_page_v1.0",
            "accepted_taxon_key": key,
            "display_name": getattr(tx, "display_name", key),
            "rank": getattr(tx, "node_type", None),
            "wfo_accepted_name": getattr(tx, "wfo_accepted_name", None),
            "gbif_accepted_name": getattr(tx, "gbif_accepted_name", None),
            "opentree_accepted_name": getattr(tx, "opentree_accepted_name", None),
            "powo_accepted_name": getattr(tx, "powo_accepted_name", None),
            "external_ids": {
                "wfo": getattr(tx, "wfo_id", None),
                "gbif": getattr(tx, "gbif_taxon_key", None),
                "ott": getattr(tx, "ott_id", None),
                "powo": getattr(tx, "powo_id", None),
            },
            "genus_inferred": getattr(tx, "genus_label", ""),
            "synonyms": list(getattr(tx, "synonyms", []) or []),
            "header_edges": header_edges,
            "tracks": per_track_render,
            "neighborhood": neighborhood,
            "counter_claim_target_template": {
                "accepted_taxon_key": key,
                "target_kind": "evidence_row_or_prediction",
                "target_edge_id": "<paste edge_id from page>",
                "reviewer_id": "<your-orcid-or-email>",
                "comment": "<your counter-claim — 1 to 5 sentences>",
                "iso_timestamp": "<filled by CLI>",
            },
        }

        # Write page (slugify accepted_taxon_key — replace ':' with '_')
        slug = key.replace(":", "_").replace("/", "_")
        (PAGES / f"{slug}.json").write_text(
            json.dumps(page, ensure_ascii=False, separators=(",", ":")))
        pages_written += 1

        # Search index row: very compact
        search_rows.append({
            "k": key,
            "n": page["display_name"],
            "s": page["synonyms"][:3],
            "f": getattr(tx, "genus_label", ""),
            "u": slug,
        })

    coverage_summary = {
        "total_pages_written": pages_written,
        "per_track": {
            str(t): dict(coverage[t]) for t in range(1, 7)
        },
        "instruments_detected": {str(t): instruments[t] for t in range(1, 7)},
        "instrument_prediction_rows_by_track": {
            str(t): sum(len(v) for v in instrument_predictions.get(t, {}).values())
            for t in range(1, 7)
        },
        "instrument_prediction_taxa_by_track": {
            str(t): len(instrument_predictions.get(t, {}))
            for t in range(1, 7)
        },
    }
    return coverage_summary, search_rows


def emit_static_shell(coverage_summary: dict, instruments: dict) -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "coverage_summary.json").write_text(
        json.dumps(coverage_summary, indent=2))

    # Counter-claim template (mirrors CLI schema)
    (SITE / "counter_claim_template.json").write_text(json.dumps({
        "schema": "phytograph.counter_claim.v1",
        "fields": {
            "accepted_taxon_key": "string, required",
            "target_edge_id": "string, required (substrate edge_id, instrument prediction id, or page header edge_id)",
            "target_kind": "enum: observed_row | enriched_row | predicted_row | header_row",
            "reviewer_id": "string, required (orcid: or email:)",
            "comment": "string, 1..5000 chars, required",
            "iso_timestamp": "filled by CLI",
            "atlas_build_id": "string, filled by CLI",
        },
        "append_only": True,
        "ledger_event_emitted": True,
        "cli": "tools/file_counter_claim.py",
    }, indent=2))

    # Provenance registry: source_group -> license/access date/role
    edges = pd.read_parquet(SUBSTRATE / "hyperedges.parquet")
    prov = (edges.groupby("source_group")
            .agg(license=("license", lambda s: sorted(set(str(x) for x in s.dropna()))[:3]),
                 access_dates=("access_date", lambda s: sorted(set(str(x) for x in s.dropna()))),
                 row_count=("edge_id", "size"))
            .reset_index())
    (SITE / "provenance_registry.json").write_text(
        json.dumps(prov.to_dict("records"), indent=2, default=str))

    # HTML shell — vanilla JS, runnable via `python3 -m http.server`
    (SITE / "index.html").write_text(INDEX_HTML)
    (SITE / "app.js").write_text(APP_JS)
    (SITE / "style.css").write_text(STYLE_CSS)


# ---------------------------- static shell ---------------------------------

INDEX_HTML = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>PhytoGraph Botanical Atlas — Wave 3</title>
<link rel="stylesheet" href="style.css">
</head><body>
<header>
  <h1>PhytoGraph Botanical Atlas</h1>
  <p class="subtitle">Wave 3 / M3.A — researcher-facing window over frozen
     Barrier-1 substrate plus available Wave-3 instrument outputs.</p>
  <p class="warn">This Atlas is a <em>research instrument</em>, not a wiki.
     Every claim carries an evidence class
     (<span class="band observed">OBSERVED</span>
      <span class="band enriched">ENRICHED</span>
      <span class="band predicted">PREDICTION</span>
      <span class="band data-limited">DATA-LIMITED</span>)
     and a provenance pointer. See
     <a href="page_contract.md">page_contract.md</a> and
     <a href="reports/atlas_barrier3_scaffold.md">atlas_barrier3_scaffold.md</a>.</p>
</header>
<section id="searchbox">
  <input id="q" placeholder="Search accepted name, synonym, common name, or genus…" autofocus>
  <div id="filters">
    <label>Genus <input id="f_genus" placeholder="e.g. Triticum"></label>
  </div>
  <ul id="results"></ul>
</section>
<section id="page"></section>
<footer>
  <p>Build: <span id="buildmeta"></span>. Read-only over
     <code>phytograph_dataset/</code> and <code>tracks/track*/</code>.</p>
</footer>
<script src="app.js"></script>
</body></html>
"""

APP_JS = r"""
'use strict';
async function loadJSON(p){const r=await fetch(p);if(!r.ok)throw new Error(p);return r.json();}
let INDEX=null;
async function init(){
  try{INDEX=await loadJSON('search_index.json');}catch(e){
    document.getElementById('buildmeta').textContent='search_index.json missing — run build_atlas.py';
    return;}
  const cov=await loadJSON('coverage_summary.json');
  document.getElementById('buildmeta').textContent =
    INDEX.length + ' taxa indexed · ' + cov.total_pages_written + ' pages';
  document.getElementById('q').addEventListener('input',doSearch);
  document.getElementById('f_genus').addEventListener('input',doSearch);
}
function doSearch(){
  const q=document.getElementById('q').value.trim().toLowerCase();
  const g=document.getElementById('f_genus').value.trim().toLowerCase();
  const out=document.getElementById('results'); out.innerHTML='';
  if(q.length<2 && !g) return;
  let n=0;
  for(const row of INDEX){
    const hay=(row.n+' '+(row.s||[]).join(' ')+' '+row.f).toLowerCase();
    if(q && !hay.includes(q)) continue;
    if(g && !(row.f||'').toLowerCase().startsWith(g)) continue;
    const li=document.createElement('li');
    const a=document.createElement('a'); a.textContent=row.n;
    a.href='#'+row.u; a.onclick=ev=>{ev.preventDefault();showPage(row.u);return false;};
    li.appendChild(a); out.appendChild(li);
    if(++n>=200){const li2=document.createElement('li');li2.textContent='… more — refine query';out.appendChild(li2);break;}
  }
}
async function showPage(slug){
  const p=await loadJSON('pages/'+slug+'.json');
  const root=document.getElementById('page'); root.innerHTML='';
  const h2=document.createElement('h2'); h2.textContent=p.display_name; root.appendChild(h2);
  const meta=document.createElement('p'); meta.className='meta';
  meta.innerHTML='Accepted key: <code>'+p.accepted_taxon_key+'</code> · rank: '+
    (p.rank||'unknown')+' · genus (inferred): '+(p.genus_inferred||'—');
  root.appendChild(meta);
  const syn=document.createElement('p'); syn.className='syn';
  syn.textContent='Synonyms: '+((p.synonyms&&p.synonyms.length)?p.synonyms.join('; '):'(none ingested)');
  root.appendChild(syn);
  const prov=document.createElement('p'); prov.className='prov';
  const ids=p.external_ids||{};
  prov.innerHTML='Provenance: ' + Object.entries(ids).filter(([,v])=>v)
      .map(([k,v])=>'<span class="badge">'+k+':'+v+'</span>').join(' ');
  root.appendChild(prov);
  for(let t=1;t<=6;t++){
    const sec=p.tracks[t]; if(!sec)continue;
    const div=document.createElement('section'); div.className='track band-'+sec.state;
    const h=document.createElement('h3');
    h.innerHTML='Track '+t+' — '+sec.title+
      ' <span class="bandtag">'+sec.state.toUpperCase()+'</span>';
    div.appendChild(h);
    if(sec.state==='data-limited'){
      const p1=document.createElement('p'); p1.className='reason';
      p1.textContent=sec.data_limited_reason; div.appendChild(p1);
    } else {
      for(const klass of ['observed','enriched','predicted']){
        for(const e of sec[klass]||[]){
          const row=document.createElement('div'); row.className='row '+klass;
          row.innerHTML='<span class="band '+klass+'">'+klass.toUpperCase()+'</span> '+
            '<code>'+e.edge_type+'</code> — src <code>'+(e.source_group||'?')+
            '</code> — license: '+(e.license||'?').slice(0,60)+
            (e.pending_crosswalk?' <em>(pending_crosswalk)</em>':'')+
            ' — confidence '+(e.confidence!=null?e.confidence:'—');
          div.appendChild(row);
        }
      }
    }
    if(sec.instrument_pending){
      const ip=document.createElement('p'); ip.className='ipending';
      ip.innerHTML='<strong>Instrument M3.T'+t+': pending</strong> — expected files '+
        '<code>'+sec.instrument_expected_files.join(', ')+'</code> from <em>'+
        sec.instrument_sibling_clone+'</em>. '+(sec.instrument_contract_reason||'Not yet emitted at Atlas build time.');
      div.appendChild(ip);
    }
    root.appendChild(div);
  }
  // Counter-claim button
  const cc=document.createElement('section'); cc.className='counterclaim';
  cc.innerHTML='<h3>File a counter-claim</h3>'+
    '<p>Counter-claims are append-only and require a target edge_id. The form '+
    'below builds a JSON payload; save it as a line to <code>counter_claims.jsonl</code> '+
    'or pipe through <code>tools/file_counter_claim.py</code> to also emit a '+
    'promise-ledger event.</p>'+
    '<label>Target edge_id <input id="cc_edge" size="60"></label><br>'+
    '<label>Reviewer id (orcid:… or email:…) <input id="cc_who" size="40"></label><br>'+
    '<label>Comment <textarea id="cc_cmt" rows="3" cols="60"></textarea></label><br>'+
    '<button id="cc_go">Build JSON</button>'+
    '<pre id="cc_out"></pre>';
  root.appendChild(cc);
  document.getElementById('cc_go').onclick=()=>{
    const payload={
      schema:'phytograph.counter_claim.v1',
      accepted_taxon_key:p.accepted_taxon_key,
      target_edge_id:document.getElementById('cc_edge').value.trim(),
      target_kind:'evidence_row_or_prediction',
      reviewer_id:document.getElementById('cc_who').value.trim(),
      comment:document.getElementById('cc_cmt').value.trim(),
      iso_timestamp:new Date().toISOString(),
    };
    document.getElementById('cc_out').textContent=JSON.stringify(payload,null,2);
  };
}
init();
"""

STYLE_CSS = """
body{font-family:system-ui,-apple-system,sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;color:#222;}
header{border-bottom:1px solid #ccc;padding-bottom:.5em;}
.subtitle{color:#555;margin:.2em 0;}
.warn{background:#fffbe6;border:1px solid #e8d97a;padding:.5em;border-radius:4px;}
#searchbox input{font-size:1em;padding:.4em;width:60%;}
#filters{margin:.5em 0;}
#results{list-style:none;padding:0;max-height:300px;overflow:auto;}
#results li a{text-decoration:none;}
section.track{border:1px solid #ddd;padding:.5em;margin:.5em 0;border-radius:4px;}
.band-observed{border-left:6px solid #2c7fb8;}
.band-enriched{border-left:6px solid #eab308;}
.band-predicted{border-left:6px solid #f97316;}
.band-data-limited{border-left:6px solid #888;background:#f6f6f6;}
.band{display:inline-block;padding:1px 6px;border-radius:3px;font-size:.75em;color:#fff;margin-right:4px;}
.band.observed{background:#2c7fb8;}
.band.enriched{background:#eab308;color:#222;}
.band.predicted{background:#f97316;}
.band.data-limited{background:#888;}
.bandtag{float:right;font-size:.8em;background:#222;color:#fff;padding:1px 6px;border-radius:3px;}
.row{font-family:ui-monospace,monospace;font-size:.85em;margin:.2em 0;}
.row em{color:#a04000;}
.badge{display:inline-block;background:#eef;border:1px solid #aac;padding:1px 4px;margin:0 2px;font-size:.8em;border-radius:3px;}
.ipending{background:#fff7ed;border:1px dashed #f97316;padding:.4em;}
.counterclaim{border:1px solid #ccc;padding:.5em;margin-top:1em;}
.counterclaim input,.counterclaim textarea{font-family:ui-monospace,monospace;}
pre#cc_out{background:#f6f6f6;padding:.5em;overflow:auto;}
footer{margin-top:2em;color:#666;font-size:.85em;border-top:1px solid #ccc;padding-top:.5em;}
"""


def main() -> int:
    global SITE, PAGES
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="cap pages emitted (for tests/smoke runs)")
    ap.add_argument("--out", type=str, default=str(SITE),
                    help="output site dir (default botanical_atlas_site/)")
    args = ap.parse_args()
    SITE = Path(args.out)
    PAGES = SITE / "pages"

    t0 = time.time()
    print(f"[build_atlas] loading substrate…", flush=True)
    sub = load_substrate()
    probe6 = load_track6_probes()
    instruments = detect_wave3_instruments()
    print(f"[build_atlas]   nodes={len(sub['nodes'])} edges={len(sub['edges'])} "
          f"crosswalk={len(sub['crosswalk'])} probe6={len(probe6)}", flush=True)

    print(f"[build_atlas] building taxon index…", flush=True)
    taxon_idx = build_taxon_index(sub["nodes"], sub["crosswalk"], sub["synonyms"])
    print(f"[build_atlas]   {len(taxon_idx)} accepted-key taxa", flush=True)

    print(f"[build_atlas] loading track prediction adapters…", flush=True)
    instrument_predictions = load_instrument_predictions()
    for t in range(1, 7):
        n_rows = sum(len(v) for v in instrument_predictions.get(t, {}).values())
        n_taxa = len(instrument_predictions.get(t, {}))
        print(f"[build_atlas]   track{t}: {n_rows} rows across {n_taxa} taxa", flush=True)

    print(f"[build_atlas] emitting per-taxon pages…", flush=True)
    coverage, search_rows = build_pages(
        taxon_idx, sub["edges"], probe6, instruments, instrument_predictions,
        limit=args.limit)

    print(f"[build_atlas] writing search index ({len(search_rows)} rows)…", flush=True)
    (SITE / "search_index.json").write_text(
        json.dumps(search_rows, ensure_ascii=False, separators=(",", ":")))

    emit_static_shell(coverage, instruments)

    elapsed = time.time() - t0
    build_log = {
        "atlas_build_id": hashlib.sha1(
            f"{coverage['total_pages_written']}::{elapsed:.0f}".encode()).hexdigest()[:12],
        "pages_written": coverage["total_pages_written"],
        "search_index_rows": len(search_rows),
        "elapsed_seconds": round(elapsed, 2),
        "instruments_detected": coverage["instruments_detected"],
        "per_track_coverage": coverage["per_track"],
    }
    (SITE / "build_log.json").write_text(json.dumps(build_log, indent=2))
    print(f"[build_atlas] done in {elapsed:.1f}s — "
          f"{coverage['total_pages_written']} pages → {SITE}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
