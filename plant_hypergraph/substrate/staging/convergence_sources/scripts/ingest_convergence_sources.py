# created: 2026-05-17T18:20:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone3
# agent: worker
# milestone: M1.5
"""Stage source-stated convergence specialty trait assertions for PhytoGraph M1.5."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import pathlib
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import UTC, datetime

BASE = pathlib.Path(__file__).resolve().parents[1]
RAW = BASE / "raw"
DATA = BASE / "data"
AUDIT = BASE / "INGEST_AUDIT.md"
ACCESS_DATE = "2026-05-17"
CLONE_ID = "clone-3"
RUN_ID = "run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone3"

AUSTRAITS_RECORD_API = "https://zenodo.org/api/records/11188867"
AUSTRAITS_ZIP_URL = "https://zenodo.org/api/records/11188867/files/austraits-6.0.0.zip/content"
AUSTRAITS_ZIP = RAW / "austraits-6.0.0.zip"
AUSTRAITS_MANIFEST = RAW / "manifests" / "austraits_zenodo_11188867.json"

SOURCE = {
    "source_id": "austraits_6_0_0",
    "source_name": "AusTraits 6.0.0",
    "version": "6.0.0",
    "doi": "10.5281/zenodo.11188867",
    "url": "https://zenodo.org/records/11188867",
    "license": "CC-BY-4.0",
    "reliability": "0.80",
}

TRAIT_PLAN = {
    "plant_growth_form": {
        "edge_type": "life_form",
        "node_type": "life_form",
        "role": "life_form",
        "scope": "growth-form coding",
        "not_scope": "distribution;ecology beyond growth form;convergence;phylogenetic independence",
    },
    "life_history": {
        "edge_type": "trait_syndrome",
        "node_type": "trait",
        "role": "trait",
        "scope": "source-stated life-history trait membership",
        "not_scope": "convergence;phylogenetic independence;taxonomic identity",
    },
    "woodiness": {
        "edge_type": "life_form",
        "node_type": "life_form",
        "role": "life_form",
        "scope": "source-stated woody/herbaceous growth-form coding",
        "not_scope": "distribution;ecology beyond growth form;convergence;phylogenetic independence",
    },
    "fruit_type": {
        "edge_type": "fruit_morphology",
        "node_type": "fruit_type",
        "role": "fruit_type",
        "scope": "morphological coding of fruit type per source",
        "not_scope": "ecological dispersal syndrome;edibility;convergence;phylogenetic independence",
    },
    "fruit_dehiscence": {
        "edge_type": "fruit_morphology",
        "node_type": "fruit_type",
        "role": "fruit_type",
        "scope": "fruit dehiscence morphology per source",
        "not_scope": "ecological dispersal syndrome;edibility;convergence;phylogenetic independence",
    },
    "fruit_fleshiness": {
        "edge_type": "fruit_morphology",
        "node_type": "fruit_type",
        "role": "fruit_type",
        "scope": "fruit fleshiness morphology per source",
        "not_scope": "ecological dispersal syndrome;edibility;convergence;phylogenetic independence",
    },
    "diaspore_fleshiness": {
        "edge_type": "fruit_morphology",
        "node_type": "fruit_type",
        "role": "fruit_type",
        "scope": "diaspore fleshiness morphology per source",
        "not_scope": "ecological dispersal syndrome;edibility;convergence;phylogenetic independence",
    },
    "dispersal_syndrome": {
        "edge_type": "trait_syndrome",
        "node_type": "trait",
        "role": "trait",
        "scope": "source-stated dispersal syndrome trait membership",
        "not_scope": "fruit morphology;convergence;phylogenetic independence",
    },
    "dispersers": {
        "edge_type": "trait_syndrome",
        "node_type": "trait",
        "role": "trait",
        "scope": "source-stated disperser category membership",
        "not_scope": "observed animal partnership;convergence;phylogenetic independence",
    },
    "dispersal_appendage": {
        "edge_type": "trait_syndrome",
        "node_type": "trait",
        "role": "trait",
        "scope": "source-stated dispersal appendage trait membership",
        "not_scope": "observed dispersal interaction;convergence;phylogenetic independence",
    },
    "seed_shape": {
        "edge_type": "trait_syndrome",
        "node_type": "trait",
        "role": "trait",
        "scope": "source-stated seed shape trait membership",
        "not_scope": "fruit morphology unless source states fruit;convergence;phylogenetic independence",
    },
    "photosynthetic_pathway": {
        "edge_type": "trait_syndrome",
        "node_type": "trait",
        "role": "trait",
        "scope": "source-stated photosynthetic pathway membership",
        "not_scope": "independent C4 origin count;convergence;phylogenetic independence",
    },
    "plant_succulence": {
        "edge_type": "life_form",
        "node_type": "life_form",
        "role": "life_form",
        "scope": "source-stated succulence growth-form coding",
        "not_scope": "family-level succulence inference;convergence;phylogenetic independence",
    },
}

REJECTED_CANDIDATES = [
    ("c4_wikipedia_list", "C4 plants from Wikipedia list", "secondary_web_page", "not a primary curated dataset; not used for staging"),
    ("c4_sage_2011_review", "C4 plant lineages of planet Earth", "publication_review", "review enumerates lineages but no redistributable species table was staged"),
    ("c4_china_frontiers_2023", "Geographic distribution of C4 species across China", "publication_supplement_candidate", "regional list pending supplement retrieval; not enough campaign-scale coverage alone"),
    ("c4_grass_global_database", "Global database of C4 photosynthesis in grasses", "publication_supplement_candidate", "candidate source identified but not retrieved in this branch"),
    ("succulence_family_inference_cactaceae", "Treat all Cactaceae as succulent", "inference", "family membership is not a source-stated row-level succulence assertion"),
    ("succulence_family_inference_crassulaceae", "Treat all Crassulaceae as succulent", "inference", "family membership is not a source-stated row-level succulence assertion"),
    ("succulence_family_inference_aizoaceae", "Treat all Aizoaceae as succulent", "inference", "family membership is not a source-stated row-level succulence assertion"),
    ("myrmecochory_wikipedia_summary", "Myrmecochory summary page", "secondary_web_page", "not a row-level taxon dataset"),
    ("elaiosome_britannica_examples", "Britannica elaiosome examples", "secondary_web_page", "not a scalable trait list"),
    ("myrmecochory_genus_expansion", "Expand myrmecochorous genera to all species", "forbidden_expansion", "genus-level claims cannot be expanded to species"),
    ("samara_family_inference_aceraceae", "Treat maples as samara-bearing", "inference", "family/genus membership does not assert every species row has samara"),
    ("samara_common_name_inference", "Infer samara from common name winged seed", "inference", "common-name morphology was not accepted as source-stated fruit type"),
    ("fruit_syndrome_from_fruit_type", "Infer dispersal syndrome from berry/drupe", "forbidden_scope", "fruit morphology does not support dispersal syndrome"),
    ("zoochory_from_fleshy_fruit", "Infer animal dispersal from fleshy fruit", "forbidden_scope", "fleshiness alone is not staged as animal dispersal"),
    ("ant_dispersal_from_elaiosome", "Infer observed ant partnership from elaiosome", "forbidden_scope", "appendage trait does not assert observed animal partnership"),
    ("convergence_from_c4_trait", "Emit convergence_signature for all C4 taxa", "forbidden_scope", "trait membership does not enumerate independent-origin set"),
    ("convergence_from_succulence_trait", "Emit convergence_signature for succulent taxa", "forbidden_scope", "trait membership does not enumerate independent-origin set"),
    ("convergence_from_samara_trait", "Emit convergence_signature for samara taxa", "forbidden_scope", "trait membership does not enumerate independent-origin set"),
    ("try_full_trait_database", "TRY full database", "license_registration", "registration/license workflow outside no-auth branch"),
    ("powo_trait_scrape", "Scrape POWO pages for fruit morphology", "scraping", "aggressive scraping rejected where dumps/APIs preferred"),
    ("manual_pdf_table_extraction", "Extract unnamed PDF tables manually", "missing_provenance", "not staged without stable table identifiers and row provenance"),
    ("horticultural_trait_blog", "Horticultural blog fruit-type lists", "weak_source", "insufficient source reliability for substrate staging"),
    ("image_based_trait_calls", "Infer fruit type from images", "forbidden_inference", "media evidence cannot establish biology in M1.5"),
]


def download_if_needed() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "manifests").mkdir(parents=True, exist_ok=True)
    if not AUSTRAITS_MANIFEST.exists():
        urllib.request.urlretrieve(AUSTRAITS_RECORD_API, AUSTRAITS_MANIFEST)
    if not AUSTRAITS_ZIP.exists():
        urllib.request.urlretrieve(AUSTRAITS_ZIP_URL, AUSTRAITS_ZIP)


def edge_id(row: dict[str, str]) -> str:
    key = "|".join(
        [
            row["source_id"],
            row["dataset_id"],
            row["observation_id"],
            row["taxon_name"],
            row["trait_name"],
            row["value"],
            row["edge_type"],
        ]
    )
    return "conv_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:20]


def node_id(node_type: str, label: str) -> str:
    digest = hashlib.sha1(f"{node_type}|{label}".encode("utf-8")).hexdigest()[:16]
    return f"{node_type}:{digest}"


def split_values(value: str) -> list[str]:
    value = (value or "").strip()
    if not value or value.lower() in {"unknown", "undefined", "na", "n/a"}:
        return []
    return [part for part in value.split() if part]


def write_tsv(path: pathlib.Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_taxa(zf: zipfile.ZipFile) -> dict[str, dict[str, str]]:
    with zf.open("austraits-6.0.0/taxa.csv") as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline=""))
        return {row["taxon_name"]: row for row in reader}


def stage() -> dict[str, object]:
    download_if_needed()
    DATA.mkdir(parents=True, exist_ok=True)
    raw_rows = 0
    staged_edges: list[dict[str, str]] = []
    nodes: dict[tuple[str, str], dict[str, str]] = {}
    list_counts: Counter[str] = Counter()
    level_counts: dict[str, Counter[str]] = defaultdict(Counter)

    with zipfile.ZipFile(AUSTRAITS_ZIP) as zf:
        taxa = load_taxa(zf)
        with zf.open("austraits-6.0.0/traits.csv") as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline=""))
            for row in reader:
                trait_name = row["trait_name"]
                plan = TRAIT_PLAN.get(trait_name)
                if not plan:
                    continue
                raw_rows += 1
                taxon_name = row["taxon_name"].strip()
                values = split_values(row["value"])
                if not taxon_name or not values:
                    continue
                taxon = taxa.get(taxon_name, {})
                taxon_rank = taxon.get("taxon_rank", "unresolved") or "unresolved"
                if taxon_rank not in {"species", "genus", "subspecies", "variety"}:
                    taxon_rank = "unresolved"
                level_counts[trait_name][taxon_rank] += 1
                taxon_node = node_id("unresolved_taxon_name", taxon_name)
                nodes[("unresolved_taxon_name", taxon_name)] = {
                    "node_id": taxon_node,
                    "node_type": "unresolved_taxon_name",
                    "label": taxon_name,
                    "source_id": SOURCE["source_id"],
                    "source_record_id": row["observation_id"],
                    "taxon_rank": taxon_rank,
                    "pending_crosswalk": "true",
                    "clone_id": CLONE_ID,
                }
                for value in values:
                    trait_label = f"{trait_name}:{value}"
                    trait_node = node_id(plan["node_type"], trait_label)
                    nodes[(plan["node_type"], trait_label)] = {
                        "node_id": trait_node,
                        "node_type": plan["node_type"],
                        "label": trait_label,
                        "source_id": SOURCE["source_id"],
                        "source_record_id": trait_name,
                        "taxon_rank": "",
                        "pending_crosswalk": "false",
                        "clone_id": CLONE_ID,
                    }
                    edge = {
                        "edge_id": "",
                        "edge_type": plan["edge_type"],
                        "role_map_json": json.dumps(
                            {
                                "taxon": taxon_node,
                                plan["role"]: trait_node,
                                "source": SOURCE["source_id"],
                            },
                            sort_keys=True,
                        ),
                        "taxon_name": taxon_name,
                        "taxon_rank": taxon_rank,
                        "pending_crosswalk": "true",
                        "trait_name": trait_name,
                        "value": value,
                        "dataset_id": row["dataset_id"],
                        "observation_id": row["observation_id"],
                        "source_id": SOURCE["source_id"],
                        "source_name": SOURCE["source_name"],
                        "source_version": SOURCE["version"],
                        "source_url": SOURCE["url"],
                        "doi": SOURCE["doi"],
                        "license": SOURCE["license"],
                        "attribution": "Falster, Gallagher, Wenk, Sauquet et al.; original AusTraits contributors",
                        "access_date": ACCESS_DATE,
                        "source_reliability": SOURCE["reliability"],
                        "confidence": "0.80",
                        "allowed_evidence_scope": plan["scope"],
                        "disallowed_evidence_scope": plan["not_scope"],
                        "caveats": "Harmonized AusTraits row; taxon name unresolved until M1.1 crosswalk; no convergence inference.",
                        "direct_source_claim": "true",
                        "normalization_artifact": "trait value split on whitespace where AusTraits stores multi-state categorical values",
                        "ingest_clone_id": CLONE_ID,
                    }
                    edge["edge_id"] = edge_id(edge)
                    staged_edges.append(edge)
                    list_counts[trait_name] += 1

    source_registry = [
        {
            "source_id": SOURCE["source_id"],
            "source_name": SOURCE["source_name"],
            "url_or_doi": f"https://doi.org/{SOURCE['doi']}",
            "access_mode": "DUMP",
            "license": SOURCE["license"],
            "redistribution_status": "redistributable with attribution",
            "expected_trait_coverage": ",".join(TRAIT_PLAN),
            "row_count": str(len(staged_edges)),
            "known_bias": "Australian flora; harmonized from many primary sources; source coverage uneven by trait and clade",
            "source_reliability": SOURCE["reliability"],
            "access_date": ACCESS_DATE,
        },
        {
            "source_id": "specialty_publication_candidates",
            "source_name": "C4/succulence/myrmecochory/elaiosome/samara publication candidates",
            "url_or_doi": "see rejected_records.tsv",
            "access_mode": "mixed",
            "license": "per-publication",
            "redistribution_status": "not staged in this branch",
            "expected_trait_coverage": "C4 lineages; myrmecochory; elaiosome; succulence; samara",
            "row_count": "0",
            "known_bias": "scale, licensing, and row-level provenance unresolved",
            "source_reliability": "0.75",
            "access_date": ACCESS_DATE,
        },
    ]

    rejected_rows = [
        {
            "reject_id": rid,
            "candidate": label,
            "reject_class": klass,
            "reason": reason,
            "ingest_clone_id": CLONE_ID,
        }
        for rid, label, klass, reason in REJECTED_CANDIDATES
    ]

    write_tsv(
        DATA / "staged_nodes.tsv",
        ["node_id", "node_type", "label", "source_id", "source_record_id", "taxon_rank", "pending_crosswalk", "clone_id"],
        sorted(nodes.values(), key=lambda r: (r["node_type"], r["label"])),
    )
    write_tsv(
        DATA / "staged_edges.tsv",
        [
            "edge_id",
            "edge_type",
            "role_map_json",
            "taxon_name",
            "taxon_rank",
            "pending_crosswalk",
            "trait_name",
            "value",
            "dataset_id",
            "observation_id",
            "source_id",
            "source_name",
            "source_version",
            "source_url",
            "doi",
            "license",
            "attribution",
            "access_date",
            "source_reliability",
            "confidence",
            "allowed_evidence_scope",
            "disallowed_evidence_scope",
            "caveats",
            "direct_source_claim",
            "normalization_artifact",
            "ingest_clone_id",
        ],
        staged_edges,
    )
    write_tsv(
        DATA / "source_registry.tsv",
        [
            "source_id",
            "source_name",
            "url_or_doi",
            "access_mode",
            "license",
            "redistribution_status",
            "expected_trait_coverage",
            "row_count",
            "known_bias",
            "source_reliability",
            "access_date",
        ],
        source_registry,
    )
    write_tsv(
        DATA / "rejected_records.tsv",
        ["reject_id", "candidate", "reject_class", "reason", "ingest_clone_id"],
        rejected_rows,
    )

    return {
        "raw_rows": raw_rows,
        "edge_rows": len(staged_edges),
        "node_rows": len(nodes),
        "list_counts": dict(list_counts),
        "level_counts": {k: dict(v) for k, v in level_counts.items()},
        "rejected_rows": len(rejected_rows),
    }


def write_audit(summary: dict[str, object]) -> None:
    list_counts: dict[str, int] = summary["list_counts"]  # type: ignore[assignment]
    level_counts: dict[str, dict[str, int]] = summary["level_counts"]  # type: ignore[assignment]
    scale_rows = []
    for trait_name, count in sorted(list_counts.items(), key=lambda item: (-item[1], item[0])):
        levels = level_counts.get(trait_name, {})
        scale_rows.append(
            "| {trait} | {count} | {species} | {genus} | {subspecies} | {unresolved} | {status} |".format(
                trait=trait_name,
                count=count,
                species=levels.get("species", 0),
                genus=levels.get("genus", 0),
                subspecies=levels.get("subspecies", 0) + levels.get("variety", 0),
                unresolved=levels.get("unresolved", 0),
                status="meets >=500" if count >= 500 else "data-limited",
            )
        )

    now = datetime.now(UTC).replace(microsecond=0).isoformat()
    content = f"""---
created: {now}
cycle: 2
run_id: {RUN_ID}
agent: worker
milestone: M1.5
---

# M1.5 Convergence Specialty Source Ingest Audit

## Scope

This branch staged structural Track 3 source assertions only: fruit morphology, life form, and generic trait membership from source-stated AusTraits 6.0.0 rows. It did not compute convergence pressure, infer independent origins, expand genus-level claims to species, or write to the unified substrate.

## Source Registry

| Source | Access | License | Staged rows | Reuse status | Bias / limitation |
|---|---|---|---:|---|---|
| AusTraits 6.0.0, DOI `{SOURCE['doi']}` | Zenodo dump | CC-BY-4.0 | {summary['edge_rows']} | Redistributable with attribution | Australian flora; harmonized from many primary sources; trait coverage uneven |
| C4 / succulence / myrmecochory / elaiosome / samara publication candidates | mixed supplements and reviews | per-publication | 0 | Not staged here | Candidate-specific access, scale, and row-provenance blockers recorded in `data/rejected_records.tsv` |

## Staged Schema Mapping

| Source trait | Staged edge type | Node type | Evidence scope |
|---|---|---|---|
| `plant_growth_form`, `woodiness`, `plant_succulence` | `life_form` | `life_form` | Source-stated growth form only |
| `fruit_type`, `fruit_dehiscence`, `fruit_fleshiness`, `diaspore_fleshiness` | `fruit_morphology` | `fruit_type` | Source-stated fruit/diaspore morphology only |
| `life_history`, `dispersal_syndrome`, `dispersers`, `dispersal_appendage`, `seed_shape`, `photosynthetic_pathway` | `trait_syndrome` | `trait` | Source-stated trait membership only |
| explicit source-enumerated convergent sets | `convergence_signature` | `trait` + taxa + clade context | None staged; no source in this branch met the explicit-enumeration requirement |

## Per-List Row Counts

| Trait list | Staged assertion rows | species-level source names | genus-level source names | infraspecific source names | unresolved source names | Scale status |
|---|---:|---:|---:|---:|---:|---|
{chr(10).join(scale_rows)}

At least five lists clear the >=500-row threshold. The largest staged lists are plant growth form, life history, fruit type, fruit dehiscence, fruit fleshiness, dispersal syndrome, photosynthetic pathway, dispersers, seed shape, woodiness, and dispersal appendage.

## Direct Claims vs Normalization Artifacts

Direct source claims are the AusTraits row-level tuple `(taxon_name, trait_name, value, dataset_id, observation_id, source_id)`. Normalization artifacts added by this branch are stable PhytoGraph node IDs, edge IDs, role-map JSON, evidence-scope fields, and splitting whitespace-separated multi-state categorical values into separate trait-membership assertions; the original `value` token is preserved in every edge row.

## Rejected / Quarantined Records

`data/rejected_records.tsv` contains {summary['rejected_rows']} rejected or quarantined candidates. The negative checks include forbidden source-implied expansions, secondary web summaries, genus-to-species expansion attempts, image-derived trait calls, C4/succulence convergence-signature attempts, TRY registration/license blockage, and publication candidates not staged because row-level redistributable supplements were not retrieved in this branch.

## License / Reuse Limits

AusTraits is CC-BY and requires citation of the resource paper and, where possible, original data sources. This branch preserves AusTraits attribution, DOI, version, access date, and source ID on every edge; downstream display should preserve the same attribution chain.

## Taxonomy Dependency

All taxon names are staged as `unresolved_taxon_name` nodes with `pending_crosswalk=true`. No spelling corrections, synonym resolution, accepted-name substitution, or species expansion was performed; Barrier 1 / M1.1 owns that crosswalk.

## Validation Commands

```bash
python3 substrate/staging/convergence_sources/scripts/ingest_convergence_sources.py
python3 -m pytest substrate/staging/convergence_sources/tests/test_convergence_sources_schema.py
python3 -m long_exposure.tools.promise_check
```

## Handoff Notes for Barrier 1

Barrier 1 should join `data/staged_edges.tsv` against the M1.1 taxonomic crosswalk using the unresolved source `taxon_name`, retain source-level taxon-rank fields for diagnostics, and deduplicate with the campaign canonical key after accepted taxon IDs exist. `trait_syndrome` rows must not be promoted to `convergence_signature` until Wave 2 estimates independent origins with phylogenetic context.
"""
    AUDIT.write_text(content, encoding="utf-8")


def main() -> None:
    summary = stage()
    (DATA / "ingest_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    write_audit(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
