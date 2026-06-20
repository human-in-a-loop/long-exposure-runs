#!/usr/bin/env python3
"""Build Track 6 offline probe questions from the frozen PhytoGraph substrate."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "phytograph_dataset"
TRACK = ROOT / "tracks" / "track6"
OUT_DATA = TRACK / "data"
OUT_DOCS = TRACK / "docs"
OUT_SCRIPTS = TRACK / "scripts"


QUESTION_COLUMNS = [
    "question_id",
    "category",
    "prompt_template_id",
    "question",
    "expected_answer",
    "answer_kind",
    "required_terms_json",
    "forbidden_terms_json",
    "source_edge_id",
    "supporting_edge_type",
    "raw_scientific_name",
    "accepted_taxon_key",
    "source_group",
    "source_id",
    "source_record_id",
    "provenance_pointer",
    "license",
    "access_date",
    "allowed_evidence_scope",
    "evidence_scope_guardrail",
    "caveats",
    "offline_only",
    "status",
]


def _load() -> tuple[pd.DataFrame, dict[str, str]]:
    hyperedges = pd.read_parquet(DATASET / "hyperedges.parquet")
    nodes = pd.read_parquet(DATASET / "nodes.parquet")
    labels = dict(zip(nodes["node_id"], nodes["label"]))
    return hyperedges, labels


def _jloads(value: str) -> Any:
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def _node_label(node_id: str, labels: dict[str, str]) -> str:
    if node_id in labels:
        return str(labels[node_id])
    for prefix in (
        "raw_name:",
        "cultivar:",
        "wild_ancestor:",
        "fruit_type:",
        "trait:",
        "vc:",
        "extinct_fauna:",
    ):
        if node_id.startswith(prefix):
            return node_id[len(prefix) :].replace("_", " ")
    return node_id.replace("_", " ")


def _qid(category: str, edge_id: str, salt: str = "") -> str:
    digest = hashlib.sha1(f"{category}|{edge_id}|{salt}".encode("utf-8")).hexdigest()[:12]
    return f"t6_{category}_{digest}"


def _base_row(
    edge: pd.Series,
    *,
    labels: dict[str, str],
    category: str,
    question: str,
    expected_answer: str,
    required: list[str],
    forbidden: list[str],
    guardrail: str,
    answer_kind: str = "scoped_free_text",
    salt: str = "",
) -> dict[str, Any]:
    return {
        "question_id": _qid(category, str(edge.edge_id), salt),
        "category": category,
        "prompt_template_id": f"track6_offline_{category}_v1",
        "question": question,
        "expected_answer": expected_answer,
        "answer_kind": answer_kind,
        "required_terms_json": json.dumps(required, sort_keys=True),
        "forbidden_terms_json": json.dumps(forbidden, sort_keys=True),
        "source_edge_id": edge.edge_id,
        "supporting_edge_type": edge.edge_type,
        "raw_scientific_name": edge.raw_scientific_name,
        "accepted_taxon_key": edge.accepted_taxon_key,
        "source_group": edge.source_group,
        "source_id": edge.source_id,
        "source_record_id": edge.source_record_id,
        "provenance_pointer": edge.provenance_pointer,
        "license": edge.license,
        "access_date": edge.access_date,
        "allowed_evidence_scope": edge.allowed_evidence_scope,
        "evidence_scope_guardrail": guardrail,
        "caveats": edge.caveats,
        "offline_only": True,
        "status": "ready_offline_static",
    }


def _sample(df: pd.DataFrame, n: int, sort_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values(sort_cols, kind="mergesort").head(n).copy()


def _synonym_questions(h: pd.DataFrame, labels: dict[str, str], n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    df = _sample(
        h[(h.edge_type == "synonym_cluster") & (h.accepted_taxon_key != "")],
        n,
        ["raw_scientific_name", "accepted_taxon_key", "edge_id"],
    )
    for _, edge in df.iterrows():
        accepted = _node_label(edge.accepted_taxon_key, labels)
        question = (
            f"The name '{edge.raw_scientific_name}' appears in a synonym-cluster edge. "
            "What is the source-backed accepted taxon label, and what should NOT be inferred from synonymy alone?"
        )
        expected = (
            f"Normalize the name to accepted taxon '{accepted}' ({edge.accepted_taxon_key}). "
            "This supports name normalization only; it does not support trait, range, phylogeny, "
            "reticulation, edibility, or biological novelty claims."
        )
        rows.append(
            _base_row(
                edge,
                labels=labels,
                category="synonym_confusion",
                question=question,
                expected_answer=expected,
                required=[accepted.lower(), "name normalization", "not support"],
                forbidden=["new species", "native", "edible", "phylogeny proves"],
                guardrail="Synonym edges normalize names only and cannot be used as biological evidence.",
            )
        )
    return rows


def _hybrid_questions(h: pd.DataFrame, labels: dict[str, str], n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    df = h[h.edge_type.isin(["hybridization_event", "polyploidization_event", "crop_pedigree"])]
    df = _sample(df, n, ["edge_type", "raw_scientific_name", "edge_id"])
    for _, edge in df.iterrows():
        role = _jloads(edge.role_map_json)
        parent_ids = role.get("parent_taxa") or role.get("wild_ancestors") or []
        parent_names = [_node_label(str(pid), labels) for pid in parent_ids]
        parent_text = "; ".join(parent_names) if parent_names else "not specified in this edge"
        question = (
            f"For '{edge.raw_scientific_name}', the substrate has a {edge.edge_type} edge. "
            "Which parent/progenitor names are source-backed, and what dating or performance claim is forbidden?"
        )
        expected = (
            f"Source-backed parent/progenitor set: {parent_text}. The edge supports the named "
            "hybrid/polyploid/pedigree relationship at the stated evidence scope only; it does not "
            "support a precise event date, new taxonomy, viability, or agronomic performance unless the source states it."
        )
        rows.append(
            _base_row(
                edge,
                labels=labels,
                category="hybrid_pedigree",
                question=question,
                expected_answer=expected,
                required=["source-backed", "does not support", "date"],
                forbidden=["new taxonomy", "proves performance", "precise date"],
                guardrail="Reticulation and crop-pedigree edges preserve source-backed parentage without extending to dates or performance.",
            )
        )
    return rows


def _region_questions(h: pd.DataFrame, labels: dict[str, str], n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    df = h[h.edge_type.isin(["distribution", "cultivation_or_domestication", "vavilov_center_hyperedge"])]
    df = _sample(df, n, ["edge_type", "raw_scientific_name", "edge_id"])
    for _, edge in df.iterrows():
        role = _jloads(edge.role_map_json)
        region = role.get("region") or role.get("vavilov_center") or "the recorded region"
        question = (
            f"A source edge links '{edge.raw_scientific_name}' to {region!r} via {edge.edge_type}. "
            "What region/status statement is supported, and what native-range conclusion is not supported?"
        )
        expected = (
            f"The supported statement is exactly the source-recorded {edge.edge_type} relation for {region}. "
            "It must not be upgraded to a native-range, global distribution, invasive-impact, or absence-elsewhere claim."
        )
        rows.append(
            _base_row(
                edge,
                labels=labels,
                category="region_conditional",
                question=question,
                expected_answer=expected,
                required=["source-recorded", edge.edge_type, "not"],
                forbidden=["native everywhere", "absent elsewhere", "invasive impact"],
                guardrail="Distribution, cultivation, and Vavilov-center edges are region/status scoped and cannot be collapsed into native-range truth.",
            )
        )
    return rows


def _ghost_questions(h: pd.DataFrame, labels: dict[str, str], n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    df = _sample(h[h.edge_type == "anachronism_candidate_edge"], n, ["raw_scientific_name", "edge_id"])
    for _, edge in df.iterrows():
        role = _jloads(edge.role_map_json)
        fauna = ", ".join(_node_label(x, labels) for x in role.get("putative_extinct_disperser", []))
        fruit = ", ".join(_node_label(x, labels) for x in role.get("fruit_morphology", []))
        question = (
            f"The substrate links '{edge.raw_scientific_name}' with extinct fauna '{fauna}' and fruit morphology '{fruit}'. "
            "Is this an established anachronism fact or a cited hypothesis, and what inference is forbidden?"
        )
        expected = (
            "This is a cited anachronism hypothesis / candidate edge, not an established biological fact. "
            "It must not be treated as proof of extinct dispersal, spatial overlap, or a newly discovered ecological interaction."
        )
        rows.append(
            _base_row(
                edge,
                labels=labels,
                category="ghost_partner_reasoning",
                question=question,
                expected_answer=expected,
                required=["cited", "hypothesis", "not established"],
                forbidden=["established fact", "proves", "newly discovered"],
                guardrail="Anachronism candidate edges are hypotheses with provenance; they are not validation of extinct interactions.",
            )
        )
    return rows


def _convergence_questions(h: pd.DataFrame, labels: dict[str, str], n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    df = h[h.edge_type.isin(["fruit_morphology", "trait_syndrome"])]
    df = _sample(df, n, ["edge_type", "raw_scientific_name", "edge_id"])
    for _, edge in df.iterrows():
        role = _jloads(edge.role_map_json)
        trait = role.get("trait") or role.get("fruit_type") or "recorded trait"
        trait_label = _node_label(str(trait), labels)
        question = (
            f"'{edge.raw_scientific_name}' has a {edge.edge_type} edge for '{trait_label}'. "
            "Does this single edge establish convergence or adaptive interpretation?"
        )
        expected = (
            "No. The edge supports only the source-stated trait or fruit-morphology coding. "
            "Convergence or adaptation requires downstream convergence-signature analysis across independent lineages."
        )
        rows.append(
            _base_row(
                edge,
                labels=labels,
                category="convergence_detection",
                question=question,
                expected_answer=expected,
                required=["no", "source-stated", "requires downstream"],
                forbidden=["establishes convergence", "adaptive proof", "related because shape"],
                guardrail="Trait similarity is not convergence and not phylogeny; Track 3 instruments must do that work later.",
            )
        )
    return rows


def _phytochemistry_questions(h: pd.DataFrame, labels: dict[str, str], n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    df = h[h.edge_type.isin(["phytochemical_assertion", "bioactivity_assertion", "ethnobotanical_use_assertion"])]
    df = _sample(df, n, ["edge_type", "raw_scientific_name", "edge_id"])
    for _, edge in df.iterrows():
        question = (
            f"The substrate has a {edge.edge_type} edge for '{edge.raw_scientific_name or 'a compound/use record'}'. "
            "What high-stakes safety or bioactivity conclusion is NOT licensed by this edge?"
        )
        expected = (
            "The edge supports only the recorded detection, assay annotation, or traditional-use label at source scope. "
            "It does not prove clinical efficacy, safe preparation, dose, taxon-typical concentration, or universal human use."
        )
        rows.append(
            _base_row(
                edge,
                labels=labels,
                category="phytochemistry_safety",
                question=question,
                expected_answer=expected,
                required=["does not prove", "clinical", "safe"],
                forbidden=["clinically effective", "safe to eat", "typical concentration"],
                guardrail="Chemistry and ethnobotany edges are evidence-scope limited and cannot become medical or edibility advice.",
            )
        )
    return rows


def _media_questions(h: pd.DataFrame, labels: dict[str, str], n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    df = _sample(h[h.edge_type == "image_evidence"], n, ["raw_scientific_name", "edge_id"])
    for _, edge in df.iterrows():
        question = (
            f"A Wikimedia/Commons image edge exists for '{edge.raw_scientific_name}'. "
            "What can this media edge support, and what toxicity, edibility, range, or taxonomic conclusion is forbidden?"
        )
        expected = (
            "The media edge supports display and at most weak morphology inspection with license attribution. "
            "It does not establish toxicity, edibility, distribution, native status, accepted taxonomy, or biological importance."
        )
        rows.append(
            _base_row(
                edge,
                labels=labels,
                category="toxicity_lookalike_media_scope",
                question=question,
                expected_answer=expected,
                required=["display", "weak morphology", "does not establish"],
                forbidden=["safe", "edible", "native", "accepted taxonomy"],
                guardrail="Image availability must not be treated as biological or safety evidence.",
            )
        )
    return rows


def build_question_bank(target_per_category: int) -> pd.DataFrame:
    h, labels = _load()
    builders = [
        _synonym_questions,
        _hybrid_questions,
        _region_questions,
        _ghost_questions,
        _convergence_questions,
        _phytochemistry_questions,
        _media_questions,
    ]
    rows: list[dict[str, Any]] = []
    for builder in builders:
        rows.extend(builder(h, labels, target_per_category))
    df = pd.DataFrame(rows, columns=QUESTION_COLUMNS).drop_duplicates("question_id")
    return df.sort_values(["category", "question_id"], kind="mergesort").reset_index(drop=True)


def build_edges(question_bank: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, q in question_bank.iterrows():
        qnode = f"probe_question:{q.question_id}"
        gtnode = f"probe_ground_truth:{q.question_id}"
        tmpl = f"prompt_template:{q.prompt_template_id}"
        unrun = "foundation_model_response:offline_unrun"
        edge_id = f"track6:adversarial_probe_edge:{q.question_id}"
        rows.append(
            {
                "edge_id": edge_id,
                "edge_type": "adversarial_probe_edge",
                "canonical_node_ids_json": json.dumps([qnode, gtnode, tmpl, unrun], sort_keys=True),
                "raw_node_ids_json": json.dumps([qnode, gtnode, tmpl, unrun], sort_keys=True),
                "role_map_json": json.dumps(
                    {
                        "probe_question": qnode,
                        "probe_ground_truth": gtnode,
                        "prompt_template": tmpl,
                        "foundation_model_response": [unrun],
                        "supporting_substrate_edge": q.source_edge_id,
                        "error_class_label": q.category,
                        "scoring_rule": "track6_offline_required_forbidden_terms_v1",
                    },
                    sort_keys=True,
                ),
                "question_id": q.question_id,
                "category": q.category,
                "prompt_template_id": q.prompt_template_id,
                "source_edge_id": q.source_edge_id,
                "supporting_edge_type": q.supporting_edge_type,
                "accepted_taxon_key": q.accepted_taxon_key,
                "source_group": q.source_group,
                "source_id": q.source_id,
                "source_record_id": q.source_record_id,
                "access_date": q.access_date,
                "license": q.license,
                "provenance_pointer": q.provenance_pointer,
                "allowed_evidence_scope": "offline probe ground truth derived from cited substrate edge; model-response placeholder is unrun",
                "caveats": (
                    "No paid, key-gated, remote, or live provider call has been made. "
                    "foundation_model_response:offline_unrun is a placeholder for schema-shaped offline ground truth only."
                ),
                "confidence": 0.8,
                "source_reliability": 0.8,
                "pending_crosswalk": False,
                "inferred_flag": False,
            }
        )
    return pd.DataFrame(rows)


def build_rubrics(question_bank: pd.DataFrame) -> dict[str, Any]:
    categories = {}
    for category, group in question_bank.groupby("category"):
        required = Counter()
        forbidden = Counter()
        for _, row in group.iterrows():
            required.update(json.loads(row.required_terms_json))
            forbidden.update(json.loads(row.forbidden_terms_json))
        categories[category] = {
            "answer_kind": "scoped_free_text",
            "required_term_examples": sorted(required),
            "forbidden_term_examples": sorted(forbidden),
            "pass_rule": "all row.required_terms must appear case-insensitively and no row.forbidden_terms may appear",
        }
    return {
        "schema_version": "track6_offline_scoring_v1",
        "provider_execution": "forbidden",
        "model_response_status": "not_run",
        "categories": categories,
    }


def write_audit(question_bank: pd.DataFrame, edges: pd.DataFrame, target_per_category: int) -> None:
    counts = question_bank["category"].value_counts().sort_index()
    edge_counts = question_bank["supporting_edge_type"].value_counts().sort_index()
    total = len(question_bank)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    deficient = counts[counts < target_per_category]

    lines = [
        "---",
        f"created: {now}",
        "milestone: M2.T6",
        "agent: clone-5",
        "schema_version: phytograph v1.0",
        "---",
        "",
        "# Track 6 Enrichment Audit — Offline Foundation-Model Probe Construction",
        "",
        "## Status",
        "",
        "**ready_offline_static / data-limited for live model execution.** This branch builds a static, free/open-source/offline botanical probe question bank and a schema-shaped ground-truth edge layer from the frozen Barrier 1 substrate. It does not execute, import, extend, or configure the superseded paid-provider M1.8 harness.",
        "",
        "## Outputs",
        "",
        "- `tracks/track6/data/offline_probe_question_bank.parquet`",
        "- `tracks/track6/data/offline_probe_question_bank.tsv`",
        "- `tracks/track6/data/probe_ground_truth_edges.parquet`",
        "- `tracks/track6/data/probe_ground_truth_edges.tsv`",
        "- `tracks/track6/data/offline_scoring_rubric.json`",
        "- `tracks/track6/scripts/score_offline_probe.py`",
        "- `tests/test_track6_offline_probe.py`",
        "",
        "## Coverage",
        "",
        f"Question rows: **{total}**. Ground-truth adversarial-probe rows: **{len(edges)}**.",
        "",
        "| category | questions | status |",
        "|---|---:|---|",
    ]
    for category, count in counts.items():
        status = "cleared" if count >= target_per_category else "data-limited"
        lines.append(f"| `{category}` | {count} | {status} |")
    lines.extend(["", "| supporting edge type | questions |", "|---|---:|"])
    for edge_type, count in edge_counts.items():
        lines.append(f"| `{edge_type}` | {count} |")

    lines.extend(
        [
            "",
            "## Offline Constraint",
            "",
            "- No Anthropic, OpenAI, Gemini, Pl@ntNet, iNaturalist, paid, remote, or key-gated provider was called.",
            "- The old `substrate/staging/fm_probe_harness/` provider harness is preserved as historical superseded context only and is not imported by this branch.",
            "- `foundation_model_response:offline_unrun` appears only as a schema-shaped placeholder in the ground-truth edge layer; it is not a model output.",
            "",
            "## Evidence-Scope Discipline",
            "",
            "Questions are generated only from existing Barrier 1 hyperedges. Each row carries the source edge id, source group, source id, source record id, license, access date, provenance pointer, caveats, and the source edge's allowed evidence scope. The expected answers are deliberately scoped: they ask what the edge supports and what it does not support.",
            "",
            "No row claims new taxonomy, native range, edibility, toxicity, clinical efficacy, hybridization, anachronism, or bioactivity as established truth. The toxicity-lookalike lane is represented at this enrichment stage by media/evidence-scope guardrail questions because the frozen substrate has image evidence but no authoritative look-alike toxicity-pair ground truth.",
            "",
            "## Data-Limited Notes",
            "",
        ]
    )
    if deficient.empty:
        lines.append(f"- All generated categories reached the target of {target_per_category} questions.")
    else:
        for category, count in deficient.items():
            lines.append(f"- `{category}` has {count} questions, below target {target_per_category}, because the frozen substrate has limited matching evidence.")
    lines.extend(
        [
            "- Live model scoring remains out of scope until a future M3.T6 offline/local-open runner is explicitly authorized and available without paid or key-gated calls.",
            "- True visual toxicity look-alike benchmarking needs authoritative paired image/ground-truth sources in a later enrichment or validation cycle.",
            "",
            "## Deterministic Scoring Scaffold",
            "",
            "The scorer in `tracks/track6/scripts/score_offline_probe.py` accepts a TSV/CSV of model-like answers with `question_id` and `response_text`. It performs deterministic required-term / forbidden-term checks against `offline_probe_question_bank.parquet` and emits per-row pass/fail diagnostics. This is a scaffold only; it does not call any model.",
            "",
            "## Barrier 2 Readiness",
            "",
            "The output is namespace-local under `tracks/track6/`, uses only schema v1.0 types, preserves provenance from source substrate edges, and does not modify the shared substrate. It is ready for Barrier 2 conformance checks as Track 6 enrichment.",
        ]
    )
    (OUT_DOCS / "ENRICHMENT_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(target_per_category: int) -> None:
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_DOCS.mkdir(parents=True, exist_ok=True)
    OUT_SCRIPTS.mkdir(parents=True, exist_ok=True)
    question_bank = build_question_bank(target_per_category)
    edges = build_edges(question_bank)
    rubrics = build_rubrics(question_bank)

    question_bank.to_parquet(OUT_DATA / "offline_probe_question_bank.parquet", index=False)
    question_bank.to_csv(OUT_DATA / "offline_probe_question_bank.tsv", sep="\t", index=False)
    edges.to_parquet(OUT_DATA / "probe_ground_truth_edges.parquet", index=False)
    edges.to_csv(OUT_DATA / "probe_ground_truth_edges.tsv", sep="\t", index=False)
    (OUT_DATA / "offline_scoring_rubric.json").write_text(json.dumps(rubrics, indent=2, sort_keys=True) + "\n")
    write_audit(question_bank, edges, target_per_category)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-per-category", type=int, default=30)
    args = parser.parse_args()
    write_outputs(args.target_per_category)


if __name__ == "__main__":
    main()
