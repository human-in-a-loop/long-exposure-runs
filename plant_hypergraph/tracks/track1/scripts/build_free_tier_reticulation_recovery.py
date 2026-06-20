#!/usr/bin/env python3
# created: 2026-05-18T21:05:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-track1-free-tier-reticulation-recovery
# agent: worker
# milestone: _plan/track1-free-tier-reticulation-recovery
"""Build the Track 1 free-tier reticulation recovery panel and diagnostics."""
from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track1" / "data"
PANEL_OUT = DATA / "free_tier_reticulation_panel.tsv"
EVIDENCE_OUT = DATA / "free_tier_reticulation_evidence.tsv"
DIAG_OUT = DATA / "free_tier_reticulation_join_diagnostics.tsv"


@dataclass(frozen=True)
class PanelTaxon:
    input_name: str
    family: str
    panel_role: str
    matched_control_for: str
    rationale: str


@dataclass(frozen=True)
class EvidenceSeed:
    input_name: str
    evidence_class: str
    parent_taxa_named: bool
    ploidy_or_chromosome_evidence: bool
    source_title: str
    source_url_or_doi: str
    source_type: str
    source_year: str
    independent_source_group: str
    license_or_access_note: str
    caveat: str


PANEL: list[PanelTaxon] = [
    PanelTaxon("Triticum aestivum", "Poaceae", "canonical_positive", "", "bread wheat allopolyploid seed case"),
    PanelTaxon("Brassica napus", "Brassicaceae", "canonical_positive", "", "rapeseed amphidiploid seed case"),
    PanelTaxon("Arachis hypogaea", "Fabaceae", "canonical_positive", "", "peanut allotetraploid seed case"),
    PanelTaxon("Gossypium hirsutum", "Malvaceae", "canonical_positive", "", "upland cotton allopolyploid seed case"),
    PanelTaxon("Coffea arabica", "Rubiaceae", "canonical_positive", "", "coffee allotetraploid seed case"),
    PanelTaxon("Nicotiana tabacum", "Solanaceae", "canonical_positive", "", "tobacco allotetraploid seed case"),
    PanelTaxon("Fragaria x ananassa", "Rosaceae", "canonical_positive", "", "cultivated strawberry hybrid/polyploid seed case"),
    PanelTaxon("Spartina anglica", "Poaceae", "canonical_positive", "", "classic recent allopolyploid seed case"),
    PanelTaxon("Tragopogon mirus", "Asteraceae", "canonical_positive", "", "recent allopolyploid seed case"),
    PanelTaxon("Tragopogon miscellus", "Asteraceae", "canonical_positive", "", "recent allopolyploid seed case"),
    PanelTaxon("Arabidopsis suecica", "Brassicaceae", "canonical_positive", "", "allopolyploid model seed case"),
    PanelTaxon("Helianthus anomalus", "Asteraceae", "canonical_positive", "", "homoploid hybrid species seed case"),
    PanelTaxon("Helianthus deserticola", "Asteraceae", "canonical_positive", "", "homoploid hybrid species seed case"),
    PanelTaxon("Helianthus paradoxus", "Asteraceae", "canonical_positive", "", "homoploid hybrid species seed case"),
    PanelTaxon("Iris nelsonii", "Iridaceae", "canonical_positive", "", "Louisiana iris hybrid species seed case"),
    PanelTaxon("Malus domestica", "Rosaceae", "canonical_positive", "", "crop introgression seed case"),
    PanelTaxon("Citrus sinensis", "Rutaceae", "canonical_positive", "", "sweet orange admixed origin seed case"),
    PanelTaxon("Citrus aurantium", "Rutaceae", "canonical_positive", "", "sour orange hybrid origin seed case"),
    PanelTaxon("Rosa canina", "Rosaceae", "canonical_positive", "", "dogrose reticulate/canine meiosis seed case"),
    PanelTaxon("Quercus robur", "Fagaceae", "canonical_positive", "", "oak introgression seed case"),
    PanelTaxon("Musa x paradisiaca", "Musaceae", "canonical_positive", "", "cultivated banana hybrid seed case"),
    PanelTaxon("Prunus domestica", "Rosaceae", "canonical_positive", "", "European plum polyploid origin seed case"),
    PanelTaxon("Camelina sativa", "Brassicaceae", "canonical_positive", "", "allohexaploid oilseed seed case"),
    PanelTaxon("Triticum monococcum", "Poaceae", "matched_control", "Triticum aestivum", "same crop complex control"),
    PanelTaxon("Brassica rapa", "Brassicaceae", "matched_control", "Brassica napus", "diploid progenitor/control"),
    PanelTaxon("Arachis duranensis", "Fabaceae", "matched_control", "Arachis hypogaea", "diploid progenitor/control"),
    PanelTaxon("Gossypium arboreum", "Malvaceae", "matched_control", "Gossypium hirsutum", "diploid cotton control"),
    PanelTaxon("Coffea canephora", "Rubiaceae", "matched_control", "Coffea arabica", "diploid coffee control"),
    PanelTaxon("Nicotiana sylvestris", "Solanaceae", "matched_control", "Nicotiana tabacum", "parental-lineage control"),
    PanelTaxon("Fragaria vesca", "Rosaceae", "matched_control", "Fragaria x ananassa", "diploid strawberry control"),
    PanelTaxon("Sporobolus alterniflorus", "Poaceae", "matched_control", "Spartina anglica", "parental-lineage control"),
    PanelTaxon("Tragopogon dubius", "Asteraceae", "matched_control", "Tragopogon mirus", "parental-lineage control"),
    PanelTaxon("Arabidopsis thaliana", "Brassicaceae", "matched_control", "Arabidopsis suecica", "model relative control"),
    PanelTaxon("Helianthus annuus", "Asteraceae", "matched_control", "Helianthus anomalus", "congeneric control"),
    PanelTaxon("Iris fulva", "Iridaceae", "matched_control", "Iris nelsonii", "parental-lineage control"),
    PanelTaxon("Malus sieversii", "Rosaceae", "matched_control", "Malus domestica", "wild-relative control"),
    PanelTaxon("Citrus medica", "Rutaceae", "matched_control", "Citrus sinensis", "ancestral citron control"),
    PanelTaxon("Rosa rugosa", "Rosaceae", "matched_control", "Rosa canina", "congeneric control"),
    PanelTaxon("Quercus alba", "Fagaceae", "matched_control", "Quercus robur", "oak source-density control"),
    PanelTaxon("Musa acuminata", "Musaceae", "matched_control", "Musa x paradisiaca", "banana progenitor/control"),
]


EVIDENCE: list[EvidenceSeed] = [
    EvidenceSeed("Triticum aestivum", "polyploidization_event", True, True, "Ancient hybridizations among the ancestral genomes of bread wheat", "https://doi.org/10.1126/science.1250092", "journal_article", "2014", "genome_phylogenomics", "DOI metadata/open abstract access; factual event coding only", "supports source-reported wheat allopolyploid origin; not a new PhytoGraph claim"),
    EvidenceSeed("Triticum aestivum", "reticulate_inheritance_evidence", True, True, "Analysis of the bread wheat genome using whole-genome shotgun sequencing", "https://doi.org/10.1038/nature11650", "journal_article", "2012", "genome_sequence", "DOI metadata/open abstract access; factual event coding only", "supports source-reported hexaploid wheat genome composition"),
    EvidenceSeed("Brassica napus", "polyploidization_event", True, True, "Early allopolyploid evolution in the post-Neolithic Brassica napus oilseed genome", "https://doi.org/10.1126/science.1253435", "journal_article", "2014", "genome_sequence", "DOI metadata/open abstract access; factual event coding only", "supports source-reported Brassica napus allopolyploid origin"),
    EvidenceSeed("Arachis hypogaea", "polyploidization_event", True, True, "The genome sequence of segmental allotetraploid peanut Arachis hypogaea", "https://doi.org/10.1038/s41588-019-0405-z", "journal_article", "2019", "genome_sequence", "DOI metadata/open abstract access; factual event coding only", "supports source-reported allotetraploid peanut origin"),
    EvidenceSeed("Gossypium hirsutum", "polyploidization_event", True, True, "Repeated polyploidization of Gossypium genomes and the evolution of spinnable cotton fibres", "https://doi.org/10.1038/nature11798", "journal_article", "2012", "genome_sequence", "DOI metadata/open abstract access; factual event coding only", "supports source-reported allopolyploid cotton origin"),
    EvidenceSeed("Coffea arabica", "polyploidization_event", True, True, "Molecular characterisation and origin of the Coffea arabica L. genome", "https://doi.org/10.1007/s001220051041", "journal_article", "1999", "molecular_origin_study", "DOI metadata access; factual event coding only", "supports source-reported allotetraploid coffee origin"),
    EvidenceSeed("Nicotiana tabacum", "polyploidization_event", True, True, "The tobacco genome sequence and its comparison with those of tomato and potato", "https://doi.org/10.1038/ncomms4833", "journal_article", "2014", "genome_sequence", "DOI metadata/open abstract access; factual event coding only", "supports source-reported allotetraploid tobacco origin"),
    EvidenceSeed("Fragaria x ananassa", "polyploidization_event", True, True, "Origin and evolution of the octoploid strawberry genome", "https://doi.org/10.1038/s41588-019-0356-4", "journal_article", "2019", "genome_sequence", "DOI metadata/open abstract access; factual event coding only", "supports source-reported octoploid strawberry ancestry"),
    EvidenceSeed("Spartina anglica", "hybridization_event", True, True, "Polyploid evolution in Spartina: dealing with highly redundant hybrid genomes", "https://doi.org/10.1111/j.1095-8312.2004.00333.x", "journal_article", "2004", "polyploid_review", "DOI metadata access; factual event coding only", "supports source-reported Spartina anglica hybrid/polyploid origin; accepted key may join through synonym"),
    EvidenceSeed("Tragopogon mirus", "polyploidization_event", True, True, "The recent and recurrent origin of allopolyploid species in Tragopogon", "https://doi.org/10.1073/pnas.0405153101", "journal_article", "2004", "polyploid_case_study", "DOI metadata/open abstract access; factual event coding only", "supports source-reported recent allopolyploid origin"),
    EvidenceSeed("Tragopogon miscellus", "polyploidization_event", True, True, "The recent and recurrent origin of allopolyploid species in Tragopogon", "https://doi.org/10.1073/pnas.0405153101", "journal_article", "2004", "polyploid_case_study", "DOI metadata/open abstract access; factual event coding only", "supports source-reported recent allopolyploid origin"),
    EvidenceSeed("Arabidopsis suecica", "polyploidization_event", True, True, "Sequencing of the genus Arabidopsis identifies a complex history of nonbifurcating speciation and abundant trans-specific polymorphism", "https://doi.org/10.1038/ng.3617", "journal_article", "2016", "genome_phylogenomics", "DOI metadata/open abstract access; factual event coding only", "supports source-reported Arabidopsis suecica allopolyploid origin"),
    EvidenceSeed("Helianthus anomalus", "hybridization_event", True, False, "Major ecological transitions in wild sunflowers facilitated by hybridization", "https://doi.org/10.1126/science.1086949", "journal_article", "2003", "hybrid_speciation_case_study", "DOI metadata/open abstract access; factual event coding only", "supports source-reported homoploid hybrid species origin"),
    EvidenceSeed("Helianthus deserticola", "hybridization_event", True, False, "Major ecological transitions in wild sunflowers facilitated by hybridization", "https://doi.org/10.1126/science.1086949", "journal_article", "2003", "hybrid_speciation_case_study", "DOI metadata/open abstract access; factual event coding only", "supports source-reported homoploid hybrid species origin"),
    EvidenceSeed("Helianthus paradoxus", "hybridization_event", True, False, "Major ecological transitions in wild sunflowers facilitated by hybridization", "https://doi.org/10.1126/science.1086949", "journal_article", "2003", "hybrid_speciation_case_study", "DOI metadata/open abstract access; factual event coding only", "supports source-reported homoploid hybrid species origin"),
    EvidenceSeed("Iris nelsonii", "hybridization_event", True, False, "Natural hybridization in Louisiana irises: genetic variation and ecological determinants", "https://doi.org/10.2307/2445221", "journal_article", "1990", "hybrid_speciation_case_study", "DOI metadata access; factual event coding only", "supports source-reported Louisiana iris hybrid origin"),
    EvidenceSeed("Malus domestica", "reticulate_inheritance_evidence", True, False, "New insight into the history of domesticated apple: secondary contribution of the European wild apple to the genome of cultivated varieties", "https://doi.org/10.1371/journal.pgen.1002703", "journal_article", "2012", "crop_introgression_study", "open access article; factual event coding only", "supports source-reported introgression into cultivated apple"),
    EvidenceSeed("Citrus sinensis", "reticulate_inheritance_evidence", True, False, "Sequencing of diverse mandarin, pummelo and orange genomes reveals complex history of admixture during citrus domestication", "https://doi.org/10.1038/nbt.2906", "journal_article", "2014", "crop_introgression_study", "DOI metadata/open abstract access; factual event coding only", "supports source-reported admixed citrus domestication history"),
    EvidenceSeed("Citrus aurantium", "hybridization_event", True, False, "Genomics of the origin and evolution of Citrus", "https://doi.org/10.1038/nature25447", "journal_article", "2018", "genome_phylogenomics", "DOI metadata/open abstract access; factual event coding only", "supports source-reported hybrid origin in Citrus"),
    EvidenceSeed("Rosa canina", "reticulate_inheritance_evidence", False, True, "Evolution by reticulation: European dogroses originated by multiple hybridization across the genus Rosa", "https://doi.org/10.1111/j.1365-294X.2005.02730.x", "journal_article", "2005", "reticulation_case_study", "DOI metadata access; factual event coding only", "supports source-reported reticulate origin of dogroses; parent resolution remains caveated"),
    EvidenceSeed("Quercus robur", "reticulate_inheritance_evidence", False, False, "Extensive recent secondary contacts between four European white oak species", "https://doi.org/10.1111/nph.16069", "journal_article", "2019", "introgression_case_study", "DOI metadata/open abstract access; factual event coding only", "supports source-reported oak introgression/contact, not a discrete new species event"),
    EvidenceSeed("Musa x paradisiaca", "hybridization_event", True, True, "Multidisciplinary perspectives on banana domestication", "https://doi.org/10.1073/pnas.1102001108", "journal_article", "2011", "crop_origin_review", "open access article; factual event coding only", "supports source-reported hybrid domestication context; accepted key may be unstable"),
    EvidenceSeed("Prunus domestica", "polyploidization_event", True, True, "The origin and domestication of Prunus domestica L. inferred from nuclear and chloroplast DNA sequence variation", "https://doi.org/10.1111/j.1365-294X.2009.04457.x", "journal_article", "2010", "crop_origin_study", "DOI metadata access; factual event coding only", "supports source-reported polyploid origin hypotheses; parentage remains caveated"),
    EvidenceSeed("Camelina sativa", "polyploidization_event", True, True, "The emerging biofuel crop Camelina sativa retains a highly undifferentiated hexaploid genome structure", "https://doi.org/10.1038/ncomms4706", "journal_article", "2014", "genome_sequence", "open access article; factual event coding only", "supports source-reported allohexaploid genome structure"),
]

DIAGNOSTIC_ONLY_TAXA = {
    "Citrus sinensis": "GBIF accepted-key resolution collapses this input to the same accepted key used for Citrus aurantium in the current API response; retained as a join diagnostic, not a distinct instrument-ready event row.",
}


def fetch_json(url: str, timeout: int = 12) -> dict:
    req = Request(url, headers={"User-Agent": "PhytoGraph free-tier recovery (mailto:example@example.com)"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def gbif_match(name: str) -> dict[str, str]:
    url = "https://api.gbif.org/v1/species/match?" + urlencode({"name": name, "rank": "SPECIES"})
    try:
        data = fetch_json(url)
    except Exception as exc:
        return {
            "accepted_key": "",
            "accepted_name": "",
            "gbif_match_type": "api_error",
            "join_status": "api_error",
            "synonym_path": "",
            "failure_mode": f"gbif_error:{type(exc).__name__}",
        }
    key = data.get("acceptedUsageKey") or data.get("usageKey") or ""
    accepted = data.get("acceptedUsage") or ""
    if key and not accepted:
        try:
            accepted_data = fetch_json(f"https://api.gbif.org/v1/species/{key}")
            accepted = accepted_data.get("scientificName") or data.get("scientificName") or ""
        except Exception:
            accepted = data.get("scientificName") or ""
    status = data.get("status") or ""
    match_type = data.get("matchType") or ""
    confidence = data.get("confidence", "")
    synonym_path = ""
    if status == "SYNONYM" and data.get("scientificName") != accepted:
        synonym_path = f"{data.get('scientificName', name)} -> {accepted}"
    join_status = "accepted_key_joined" if key else "no_accepted_key"
    failure_mode = "" if key else f"gbif_no_match:{match_type}"
    return {
        "accepted_key": f"gbif:{key}" if key else "",
        "accepted_name": accepted,
        "gbif_match_type": f"{match_type};status={status};confidence={confidence}",
        "join_status": join_status,
        "synonym_path": synonym_path,
        "failure_mode": failure_mode,
    }


def metadata_count(endpoint: str, name: str) -> int:
    query = f'"{name}" hybrid OR allopolyploid OR polyploid OR introgression'
    if endpoint == "crossref":
        url = "https://api.crossref.org/works?" + urlencode({"query.bibliographic": query, "rows": 0})
        try:
            return int(fetch_json(url).get("message", {}).get("total-results", 0))
        except Exception:
            return -1
    url = "https://api.openalex.org/works?" + urlencode({"search": query, "per-page": 1})
    try:
        return int(fetch_json(url).get("meta", {}).get("count", 0))
    except Exception:
        return -1


def source_density_band(hit_count: int) -> str:
    if hit_count < 0:
        return "unknown"
    if hit_count >= 500:
        return "high"
    if hit_count >= 100:
        return "medium"
    return "low"


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    match_by_name: dict[str, dict[str, str]] = {}
    hit_counts: dict[tuple[str, str], int] = {}
    for taxon in PANEL:
        match_by_name[taxon.input_name] = gbif_match(taxon.input_name)
        time.sleep(0.05)
        hit_counts[(taxon.input_name, "crossref_metadata")] = metadata_count("crossref", taxon.input_name)
        time.sleep(0.05)
        hit_counts[(taxon.input_name, "openalex_metadata")] = metadata_count("openalex", taxon.input_name)
        time.sleep(0.05)

    evidence_by_name: dict[str, list[EvidenceSeed]] = {}
    for seed in EVIDENCE:
        evidence_by_name.setdefault(seed.input_name, []).append(seed)

    panel_rows: list[dict[str, object]] = []
    evidence_rows: list[dict[str, object]] = []
    diag_rows: list[dict[str, object]] = []

    for taxon in PANEL:
        match = match_by_name[taxon.input_name]
        crossref_hits = hit_counts[(taxon.input_name, "crossref_metadata")]
        openalex_hits = hit_counts[(taxon.input_name, "openalex_metadata")]
        usable = [
            seed for seed in evidence_by_name.get(taxon.input_name, [])
            if match["accepted_key"] and seed.evidence_class in {
                "hybridization_event",
                "polyploidization_event",
                "reticulate_inheritance_evidence",
            } and taxon.input_name not in DIAGNOSTIC_ONLY_TAXA
        ]
        panel_rows.append(
            {
                "input_name": taxon.input_name,
                "panel_role": taxon.panel_role,
                "matched_control_for": taxon.matched_control_for,
                "accepted_key": match["accepted_key"],
                "accepted_name": match["accepted_name"],
                "family": taxon.family,
                "gbif_match_type": match["gbif_match_type"],
                "synonym_path": match["synonym_path"],
                "crossref_reticulation_hit_count": crossref_hits,
                "openalex_reticulation_hit_count": openalex_hits,
                "source_density_band": source_density_band(max(crossref_hits, openalex_hits)),
                "usable_event_shaped_evidence_count": len(usable),
                "rationale": taxon.rationale,
            }
        )
        for source_group, count in [
            ("gbif_species_api", 1 if match["accepted_key"] else 0),
            ("crossref_metadata", crossref_hits),
            ("openalex_metadata", openalex_hits),
            ("curated_open_literature", len(evidence_by_name.get(taxon.input_name, []))),
        ]:
            diag_rows.append(
                {
                    "input_name": taxon.input_name,
                    "panel_role": taxon.panel_role,
                    "source_group": source_group,
                    "accepted_key": match["accepted_key"],
                    "accepted_name": match["accepted_name"],
                    "accepted_key_match": bool(match["accepted_key"]),
                    "synonym_path": match["synonym_path"],
                    "failure_mode": match["failure_mode"] if not match["accepted_key"] else "",
                    "source_hit_count": count,
                    "usable_event_shaped_hit_count": len(usable) if source_group == "curated_open_literature" else 0,
                    "diagnostic_class": (
                        "taxonomy_join_failure" if not match["accepted_key"]
                        else "event_evidence_recovered" if source_group == "curated_open_literature" and usable
                        else "metadata_only_or_no_event"
                    ),
                }
            )
        for seed in evidence_by_name.get(taxon.input_name, []):
            event_shape = seed.evidence_class in {
                "hybridization_event",
                "polyploidization_event",
                "reticulate_inheritance_evidence",
            }
            support = (
                "accepted_key_event_shaped"
                if match["accepted_key"] and event_shape and taxon.input_name not in DIAGNOSTIC_ONLY_TAXA
                else "diagnostic_only"
            )
            caveat = seed.caveat
            if taxon.input_name in DIAGNOSTIC_ONLY_TAXA:
                caveat = f"{seed.caveat}; {DIAGNOSTIC_ONLY_TAXA[taxon.input_name]}"
            evidence_rows.append(
                {
                    "input_name": taxon.input_name,
                    "accepted_key": match["accepted_key"],
                    "accepted_name": match["accepted_name"],
                    "family": taxon.family,
                    "evidence_class": seed.evidence_class,
                    "event_shape": str(event_shape).lower(),
                    "parent_taxa_named": str(seed.parent_taxa_named).lower(),
                    "ploidy_or_chromosome_evidence": str(seed.ploidy_or_chromosome_evidence).lower(),
                    "source_title": seed.source_title,
                    "source_url_or_doi": seed.source_url_or_doi,
                    "source_type": seed.source_type,
                    "source_year": seed.source_year,
                    "independent_source_group": seed.independent_source_group,
                    "license_or_access_note": seed.license_or_access_note,
                    "join_status": match["join_status"],
                    "support_status": support,
                    "caveat": caveat,
                }
            )

    write_tsv(
        PANEL_OUT,
        panel_rows,
        [
            "input_name",
            "panel_role",
            "matched_control_for",
            "accepted_key",
            "accepted_name",
            "family",
            "gbif_match_type",
            "synonym_path",
            "crossref_reticulation_hit_count",
            "openalex_reticulation_hit_count",
            "source_density_band",
            "usable_event_shaped_evidence_count",
            "rationale",
        ],
    )
    write_tsv(
        EVIDENCE_OUT,
        evidence_rows,
        [
            "input_name",
            "accepted_key",
            "accepted_name",
            "family",
            "evidence_class",
            "event_shape",
            "parent_taxa_named",
            "ploidy_or_chromosome_evidence",
            "source_title",
            "source_url_or_doi",
            "source_type",
            "source_year",
            "independent_source_group",
            "license_or_access_note",
            "join_status",
            "support_status",
            "caveat",
        ],
    )
    write_tsv(
        DIAG_OUT,
        diag_rows,
        [
            "input_name",
            "panel_role",
            "source_group",
            "accepted_key",
            "accepted_name",
            "accepted_key_match",
            "synonym_path",
            "failure_mode",
            "source_hit_count",
            "usable_event_shaped_hit_count",
            "diagnostic_class",
        ],
    )


if __name__ == "__main__":
    main()
