# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: fork-e34b5b2c1c6c-clone-5
# agent: worker
# milestone: M1.7
"""Ingest M1.7 chemodiversity and ethnobotany source-local staging tables.

This script stages only evidence-level rows. It preserves raw taxon labels and
source identifiers; Barrier 1 owns canonical taxonomy normalization.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sqlite3
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "m1_7_raw"
OUT = ROOT / "substrate" / "staging" / "chemodiversity_ethnobotany_sources"
ACCESS_DATE = date.today().isoformat()
CLONE_ID = "fork-e34b5b2c1c6c-clone-5"

DUKE_ZIP_URL = "https://ndownloader.figshare.com/files/43363335"
NAEB_DB_URL = "https://naeb.louispotok.com/naeb.db"


PHYTO_FIELDS = [
    "edge_id",
    "edge_type",
    "taxon_label_raw",
    "taxon_id_if_available",
    "compound_id",
    "compound_label",
    "plant_part",
    "concentration_value",
    "concentration_unit",
    "concentration_text_raw",
    "source_name",
    "source_record_id",
    "citation",
    "license_class",
    "access_date",
    "allowed_evidence_scope",
    "does_not_support",
    "confidence",
    "caveats",
    "family_raw",
]

ETHNO_FIELDS = [
    "edge_id",
    "edge_type",
    "taxon_label_raw",
    "taxon_id_if_available",
    "people_group",
    "region",
    "language_or_local_context",
    "use_category",
    "use_text_normalized",
    "use_text_raw_pointer",
    "plant_part",
    "preparation_context",
    "source_name",
    "source_record_id",
    "source_citation",
    "license_class",
    "access_date",
    "allowed_evidence_scope",
    "does_not_support",
    "sovereignty_flag",
    "confidence",
    "caveats",
    "family_raw",
]


def stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1("|".join(p or "" for p in parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{h}"


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: clean(row.get(name, "")) for name in fieldnames})


def read_csv(path: Path, encoding: str = "latin1") -> list[dict[str, str]]:
    with path.open(encoding=encoding, newline="") as fh:
        return list(csv.DictReader(fh))


def download_if_missing(url: str, path: Path) -> bool:
    if path.exists() and path.stat().st_size:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, path)
    return True


def prepare_sources() -> dict[str, str]:
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    source_status: dict[str, str] = {}

    duke_zip = RAW / "Duke-Source-CSV.zip"
    download_if_missing(DUKE_ZIP_URL, duke_zip)
    duke_dir = RAW / "duke_source"
    if not (duke_dir / "FARMACY_NEW.csv").exists():
        duke_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(duke_zip) as zf:
            zf.extractall(duke_dir)
    source_status["Dr. Duke Phytochemical and Ethnobotanical Databases"] = "downloaded_or_present"

    naeb_db = RAW / "naeb.db"
    download_if_missing(NAEB_DB_URL, naeb_db)
    source_status["Native American Ethnobotany Database (Moerman), NAEB mirror"] = "downloaded_or_present"

    optional_inputs = {
        "KNApSAcK": RAW / "knapsack_species_metabolite.tsv",
        "NPASS": RAW / "npass_species_source_permitted.tsv",
        "PROTA": RAW / "prota_ethnobotany_permitted.tsv",
        "PROSEA": RAW / "prosea_ethnobotany_permitted.tsv",
        "ChEBI": RAW / "chebi_compound_classes.tsv",
    }
    for name, path in optional_inputs.items():
        source_status[name] = "local_permitted_input_present" if path.exists() else "metadata_only_no_local_permitted_input"
    return source_status


def ingest_duke() -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, dict[str, str]], set[str], set[str], list[dict[str, str]]]:
    base = RAW / "duke_source"
    taxa = {row["FNFNUM"]: row for row in read_csv(base / "FNFTAX.csv") if clean(row.get("FNFNUM"))}
    parts = {row["PPCO"]: row.get("PPNA", "") for row in read_csv(base / "PARTS.csv")}
    refs = {row["REFERENCE"]: row.get("LONGREF", "") or row.get("REFERENCE", "") for row in read_csv(base / "REFERENCES.csv")}
    chemicals = {}
    for row in read_csv(base / "CHEMICALS.csv"):
        key = clean(row.get("CHEMID")) or clean(row.get("CHEM"))
        if key:
            chemicals[key] = row

    compound_nodes: dict[str, dict[str, str]] = {}
    class_nodes: set[str] = set()
    phyto_edges: list[dict[str, str]] = []
    seen_edges: set[tuple[str, str, str, str, str]] = set()

    for row in read_csv(base / "FARMACY_NEW.csv"):
        fnf = clean(row.get("FNFNUM"))
        tax = taxa.get(fnf)
        chem_label = clean(row.get("CHEM"))
        compound_key = clean(row.get("CHEMID")) or chem_label
        if not tax or not chem_label or not compound_key:
            continue
        compound_id = f"DUKE_CHEM:{compound_key}"
        compound_nodes[compound_id] = {
            "node_id": compound_id,
            "node_type": "phytochemical_compound",
            "compound_label": chem_label,
            "source_name": "Dr. Duke Phytochemical and Ethnobotanical Databases",
            "source_record_id": compound_key,
            "license_class": "CC0",
            "access_date": ACCESS_DATE,
            "caveats": "Duke compound identifier; not canonicalized to ChEBI in this wave unless ChEBI local map is present.",
        }
        chem_class = clean(row.get("CHEMCLASS"))
        if chem_class:
            class_nodes.add(chem_class)
        plant_part = parts.get(clean(row.get("PPCO")), clean(row.get("PPCO")))
        concentration_bits = []
        for name in ["AMT_LO", "AMT_OR_HI", "AMT_OR_LO", "AMT_HI", "AMT_ULHI", "EOPCT_LO", "EOPCT_OR_HI", "EOPCT_OR_LO", "EOPCT_HI"]:
            value = clean(row.get(name))
            if value:
                concentration_bits.append(f"{name}={value}")
        unit = clean(row.get("QUANT_UNIT"))
        citation_key = clean(row.get("REFERENCE")) or clean(row.get("NAPREF")) or "Duke-Source-CSV:FARMACY_NEW"
        citation = refs.get(citation_key, citation_key)
        key = (fnf, compound_id, plant_part, citation_key, "|".join(concentration_bits))
        if key in seen_edges:
            continue
        seen_edges.add(key)
        phyto_edges.append(
            {
                "edge_id": stable_id("phyto_edge", "duke", *key),
                "edge_type": "phytochemical_assertion",
                "taxon_label_raw": clean(tax.get("TAXON")),
                "taxon_id_if_available": f"DUKE_FNFNUM:{fnf}",
                "compound_id": compound_id,
                "compound_label": chem_label,
                "plant_part": plant_part,
                "concentration_value": "",
                "concentration_unit": unit,
                "concentration_text_raw": "; ".join(concentration_bits),
                "source_name": "Dr. Duke Phytochemical and Ethnobotanical Databases",
                "source_record_id": f"FARMACY_NEW:{fnf}:{compound_key}:{citation_key}",
                "citation": citation,
                "license_class": "CC0",
                "access_date": ACCESS_DATE,
                "allowed_evidence_scope": "Supports detection of this compound in this raw taxon label by this source.",
                "does_not_support": "Does not support taxon-typical concentration, representative concentration, bioactivity, mechanism, clinical efficacy, universality, or safety.",
                "confidence": "0.80",
                "caveats": "Raw taxon label preserved; canonical synonym normalization deferred to Barrier 1.",
                "family_raw": clean(tax.get("FAMILY")),
            }
        )

    bio_edges: list[dict[str, str]] = []
    activity_nodes: set[str] = set()
    for row in read_csv(base / "AGGREGAC.csv"):
        chem_label = clean(row.get("CHEM"))
        activity = clean(row.get("ACTIVITY"))
        if not chem_label or not activity:
            continue
        compound_id = f"DUKE_CHEM:{''.join(ch for ch in chem_label.upper() if ch.isalnum() or ch in '+-')}"
        activity_nodes.add(activity)
        ref = clean(row.get("REFERENCE")) or "Duke-Source-CSV:AGGREGAC"
        bio_edges.append(
            {
                "edge_id": stable_id("bioactivity_edge", "duke", chem_label, activity, ref),
                "edge_type": "bioactivity_assertion",
                "compound_id": compound_id,
                "compound_label": chem_label,
                "bioactivity_class": activity,
                "assay_context": clean(row.get("DOSAGE")),
                "source_name": "Dr. Duke Phytochemical and Ethnobotanical Databases",
                "source_record_id": f"AGGREGAC:{clean(row.get('AGGNO'))}",
                "citation": refs.get(ref, ref),
                "license_class": "CC0",
                "access_date": ACCESS_DATE,
                "allowed_evidence_scope": "Supports source-recorded bioactivity or assay annotation for the compound.",
                "does_not_support": "Does not support clinical efficacy, therapeutic dose, taxon-level bioactivity, or safety.",
                "confidence": "0.75",
                "caveats": "Activity vocabulary preserved from source; no clinical interpretation is inferred.",
            }
        )

    ethno_edges: list[dict[str, str]] = []
    for row in read_csv(base / "ETHNOBOT.csv"):
        taxon = clean(row.get("TAXON")) or " ".join(p for p in [clean(row.get("GENUS")), clean(row.get("SPECIES"))] if p)
        if not taxon:
            continue
        ref = clean(row.get("LONGREF")) or clean(row.get("REFERENCE")) or "Duke-Source-CSV:ETHNOBOT"
        ethno_edges.append(
            {
                "edge_id": stable_id("ethno_edge", "duke", clean(row.get("ETHNO")), taxon, clean(row.get("ACTIVITY"))),
                "edge_type": "ethnobotanical_use_assertion",
                "taxon_label_raw": taxon,
                "taxon_id_if_available": f"DUKE_ETHNO:{clean(row.get('ETHNO'))}",
                "people_group": "not_specified_in_source",
                "region": clean(row.get("COUNTRY")),
                "language_or_local_context": "",
                "use_category": "ethnobotanical_use",
                "use_text_normalized": clean(row.get("ACTIVITY")),
                "use_text_raw_pointer": f"ETHNOBOT:{clean(row.get('ETHNO'))}",
                "plant_part": "",
                "preparation_context": "",
                "source_name": "Dr. Duke Phytochemical and Ethnobotanical Databases",
                "source_record_id": f"ETHNOBOT:{clean(row.get('ETHNO'))}",
                "source_citation": ref,
                "license_class": "CC0",
                "access_date": ACCESS_DATE,
                "allowed_evidence_scope": "Supports recorded human-use label in this source.",
                "does_not_support": "Does not support clinical bioactivity, mechanism, universality, current practice, or safety.",
                "sovereignty_flag": "no",
                "confidence": "0.70",
                "caveats": "People-group attribution is not present in this Duke table; row is not used as sovereignty-source evidence.",
                "family_raw": clean(row.get("FAMILY")),
            }
        )

    return phyto_edges, ethno_edges, compound_nodes, class_nodes, activity_nodes, bio_edges


def ingest_naeb() -> list[dict[str, str]]:
    db = sqlite3.connect(RAW / "naeb.db")
    db.row_factory = sqlite3.Row
    rows = db.execute(
        """
        select
          uses.id as use_id, species.name as taxon, species.family as family,
          species.usda_code as usda_code, tribes.name as tribe,
          use_categories.name as category, use_subcategories.name as subcategory,
          uses.notes as notes, uses.rawsource as rawsource, uses.pageno as pageno,
          sources.refcode as refcode, sources.fulltext as fulltext
        from uses
        left join species on uses.species = species.id
        left join tribes on uses.tribe = tribes.id
        left join sources on uses.source = sources.id
        left join use_categories on uses.use_category = use_categories.id
        left join use_subcategories on uses.use_subcategory = use_subcategories.id
        """
    ).fetchall()
    ethno_edges: list[dict[str, str]] = []
    for row in rows:
        people = clean(row["tribe"])
        citation = clean(row["rawsource"]) or clean(row["fulltext"]) or clean(row["refcode"])
        if not clean(row["taxon"]) or not people or not citation:
            continue
        use_norm = " / ".join(part for part in [clean(row["category"]), clean(row["subcategory"])] if part)
        ethno_edges.append(
            {
                "edge_id": stable_id("ethno_edge", "moerman_naeb", str(row["use_id"]), clean(row["taxon"]), people),
                "edge_type": "ethnobotanical_use_assertion",
                "taxon_label_raw": clean(row["taxon"]),
                "taxon_id_if_available": f"NAEB_USDA:{clean(row['usda_code'])}" if clean(row["usda_code"]) else "",
                "people_group": people,
                "region": "North America",
                "language_or_local_context": people,
                "use_category": clean(row["category"]),
                "use_text_normalized": use_norm,
                "use_text_raw_pointer": f"NAEB:uses:{row['use_id']}",
                "plant_part": "",
                "preparation_context": "",
                "source_name": "Native American Ethnobotany Database (Moerman), NAEB mirror",
                "source_record_id": f"NAEB:uses:{row['use_id']}",
                "source_citation": citation,
                "license_class": "source license unclear; mirror CC0 dedication only for mirror contributions",
                "access_date": ACCESS_DATE,
                "allowed_evidence_scope": "Supports recorded use by the named people group as represented in NAEB.",
                "does_not_support": "Does not support clinical bioactivity, mechanism, universality, current practice, safety, or decontextualized traditional-knowledge reuse.",
                "sovereignty_flag": "yes",
                "confidence": "0.75",
                "caveats": "Sovereignty-sensitive row; people-group and source citation must be preserved through all downstream uses.",
                "family_raw": clean(row["family"]),
            }
        )
    db.close()
    return ethno_edges


def load_optional_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Load optional permitted local TSVs if supplied by a human operator."""
    phyto_rows: list[dict[str, str]] = []
    ethno_rows: list[dict[str, str]] = []
    optional_phyto = {
        "KNApSAcK": RAW / "knapsack_species_metabolite.tsv",
        "NPASS": RAW / "npass_species_source_permitted.tsv",
    }
    for source_name, path in optional_phyto.items():
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                source_record_id = clean(row.get("source_record_id")) or clean(row.get("citation"))
                phyto_rows.append(
                    {
                        "edge_id": stable_id("phyto_edge", source_name, clean(row.get("taxon_label_raw")), clean(row.get("compound_id")), source_record_id),
                        "edge_type": "phytochemical_assertion",
                        "taxon_label_raw": clean(row.get("taxon_label_raw")),
                        "taxon_id_if_available": clean(row.get("taxon_id_if_available")),
                        "compound_id": clean(row.get("compound_id")),
                        "compound_label": clean(row.get("compound_label")),
                        "plant_part": clean(row.get("plant_part")),
                        "concentration_value": clean(row.get("concentration_value")),
                        "concentration_unit": clean(row.get("concentration_unit")),
                        "concentration_text_raw": clean(row.get("concentration_text_raw")),
                        "source_name": source_name,
                        "source_record_id": source_record_id,
                        "citation": clean(row.get("citation")),
                        "license_class": "restricted; permitted assertion-level staging only",
                        "access_date": clean(row.get("access_date")) or ACCESS_DATE,
                        "allowed_evidence_scope": "Supports source-recorded compound detection for this raw taxon label.",
                        "does_not_support": "Does not support raw bulk redistribution, taxon-typical concentration, bioactivity, clinical efficacy, universality, or safety.",
                        "confidence": clean(row.get("confidence")) or "0.75",
                        "caveats": "Loaded from operator-supplied permitted assertion TSV; raw bulk export not redistributed.",
                        "family_raw": clean(row.get("family_raw")),
                    }
                )
    optional_ethno = {
        "PROTA": RAW / "prota_ethnobotany_permitted.tsv",
        "PROSEA": RAW / "prosea_ethnobotany_permitted.tsv",
    }
    for source_name, path in optional_ethno.items():
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                ethno_rows.append(
                    {
                        "edge_id": stable_id("ethno_edge", source_name, clean(row.get("taxon_label_raw")), clean(row.get("people_group")), clean(row.get("source_record_id"))),
                        "edge_type": "ethnobotanical_use_assertion",
                        "taxon_label_raw": clean(row.get("taxon_label_raw")),
                        "taxon_id_if_available": clean(row.get("taxon_id_if_available")),
                        "people_group": clean(row.get("people_group")),
                        "region": clean(row.get("region")),
                        "language_or_local_context": clean(row.get("language_or_local_context")),
                        "use_category": clean(row.get("use_category")),
                        "use_text_normalized": clean(row.get("use_text_normalized")),
                        "use_text_raw_pointer": clean(row.get("use_text_raw_pointer")) or clean(row.get("source_record_id")),
                        "plant_part": clean(row.get("plant_part")),
                        "preparation_context": clean(row.get("preparation_context")),
                        "source_name": source_name,
                        "source_record_id": clean(row.get("source_record_id")),
                        "source_citation": clean(row.get("source_citation")),
                        "license_class": "restricted; sovereignty-preserving assertion-level staging only",
                        "access_date": clean(row.get("access_date")) or ACCESS_DATE,
                        "allowed_evidence_scope": "Supports recorded use by the named people/region as represented in source.",
                        "does_not_support": "Does not support clinical bioactivity, mechanism, universality, current practice, safety, or decontextualized traditional-knowledge reuse.",
                        "sovereignty_flag": "yes",
                        "confidence": clean(row.get("confidence")) or "0.70",
                        "caveats": "Loaded from operator-supplied permitted assertion TSV; attribution must be preserved downstream.",
                        "family_raw": clean(row.get("family_raw")),
                    }
                )
    return phyto_rows, ethno_rows


def coverage_summary(phyto_edges: list[dict[str, str]], ethno_edges: list[dict[str, str]], compound_nodes: dict[str, dict[str, str]], source_status: dict[str, str]) -> list[dict[str, str]]:
    by_source: dict[str, dict[str, set[str] | int | str]] = defaultdict(lambda: {"taxa": set(), "compounds": set(), "phyto": 0, "ethno": 0})
    for row in phyto_edges:
        item = by_source[row["source_name"]]
        item["phyto"] = int(item["phyto"]) + 1
        item["taxa"].add(row["taxon_label_raw"])  # type: ignore[union-attr]
        item["compounds"].add(row["compound_id"])  # type: ignore[union-attr]
    for row in ethno_edges:
        item = by_source[row["source_name"]]
        item["ethno"] = int(item["ethno"]) + 1
        item["taxa"].add(row["taxon_label_raw"])  # type: ignore[union-attr]

    rows: list[dict[str, str]] = []
    all_source_names = set(by_source)
    all_source_names.update(source_status)
    for source in sorted(all_source_names):
        item = by_source.get(source, {"taxa": set(), "compounds": set(), "phyto": 0, "ethno": 0})
        rows.append(
            {
                "source_name": source,
                "access_status": source_status.get(source, "staged"),
                "phytochemical_assertions": str(item["phyto"]),
                "ethnobotanical_assertions": str(item["ethno"]),
                "distinct_taxa": str(len(item["taxa"])),  # type: ignore[arg-type]
                "distinct_compounds": str(len(item["compounds"])),  # type: ignore[arg-type]
            }
        )
    return rows


def write_audit_inputs(phyto_edges: list[dict[str, str]], ethno_edges: list[dict[str, str]], source_status: dict[str, str]) -> None:
    family_counts = Counter(row["family_raw"] or "unknown" for row in phyto_edges)
    source_counts = Counter(row["source_name"] for row in phyto_edges + ethno_edges)
    sovereignty_missing = [
        row["edge_id"]
        for row in ethno_edges
        if row["source_name"] in {"Native American Ethnobotany Database (Moerman), NAEB mirror", "PROTA", "PROSEA"}
        and (not row["people_group"] or not row["source_citation"] or not row["access_date"])
    ]
    audit = {
        "access_date": ACCESS_DATE,
        "clone_id": CLONE_ID,
        "source_status": source_status,
        "phytochemical_assertions": len(phyto_edges),
        "ethnobotanical_assertions": len(ethno_edges),
        "distinct_phytochemical_taxa": len({r["taxon_label_raw"] for r in phyto_edges}),
        "distinct_compounds": len({r["compound_id"] for r in phyto_edges}),
        "families_with_100_phytochemical_assertions": sum(1 for _, c in family_counts.items() if c >= 100),
        "top_family_counts": family_counts.most_common(25),
        "source_counts": source_counts.most_common(),
        "sovereignty_missing_critical_fields": sovereignty_missing,
    }
    (OUT / "audit_metrics.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")


def main() -> None:
    source_status = prepare_sources()
    phyto_edges, duke_ethno, compound_nodes, class_nodes, activity_nodes, bio_edges = ingest_duke()
    naeb_ethno = ingest_naeb()
    optional_phyto, optional_ethno = load_optional_rows()

    phyto_edges.extend(optional_phyto)
    ethno_edges = duke_ethno + naeb_ethno + optional_ethno

    for row in optional_phyto:
        if row["compound_id"] and row["compound_id"] not in compound_nodes:
            compound_nodes[row["compound_id"]] = {
                "node_id": row["compound_id"],
                "node_type": "phytochemical_compound",
                "compound_label": row["compound_label"],
                "source_name": row["source_name"],
                "source_record_id": row["source_record_id"],
                "license_class": row["license_class"],
                "access_date": row["access_date"],
                "caveats": "Operator-supplied permitted assertion row.",
            }

    compound_node_rows = sorted(compound_nodes.values(), key=lambda r: r["node_id"])
    chemical_class_rows = [
        {
            "node_id": stable_id("chemical_class", name),
            "node_type": "chemical_class",
            "chemical_class_label": name,
            "source_name": "Dr. Duke Phytochemical and Ethnobotanical Databases",
            "source_record_id": name,
            "license_class": "CC0",
            "access_date": ACCESS_DATE,
            "caveats": "Source vocabulary; no ontology claim beyond source class label.",
        }
        for name in sorted(class_nodes)
    ]
    bioactivity_node_rows = [
        {
            "node_id": stable_id("bioactivity_class", name),
            "node_type": "bioactivity_class",
            "bioactivity_class_label": name,
            "source_name": "Dr. Duke Phytochemical and Ethnobotanical Databases",
            "source_record_id": name,
            "license_class": "CC0",
            "access_date": ACCESS_DATE,
            "caveats": "Source vocabulary; does not imply clinical efficacy.",
        }
        for name in sorted(activity_nodes)
    ]
    ethno_node_rows = [
        {
            "node_id": stable_id("ethnobotanical_use_record", row["source_name"], row["source_record_id"]),
            "node_type": "ethnobotanical_use_record",
            "source_name": row["source_name"],
            "source_record_id": row["source_record_id"],
            "taxon_label_raw": row["taxon_label_raw"],
            "people_group": row["people_group"],
            "region": row["region"],
            "source_citation": row["source_citation"],
            "license_class": row["license_class"],
            "access_date": row["access_date"],
            "sovereignty_flag": row["sovereignty_flag"],
            "caveats": row["caveats"],
        }
        for row in ethno_edges
    ]

    write_tsv(OUT / "phytochemical_compound_nodes.tsv", ["node_id", "node_type", "compound_label", "source_name", "source_record_id", "license_class", "access_date", "caveats"], compound_node_rows)
    write_tsv(OUT / "chemical_class_nodes.tsv", ["node_id", "node_type", "chemical_class_label", "source_name", "source_record_id", "license_class", "access_date", "caveats"], chemical_class_rows)
    write_tsv(OUT / "bioactivity_class_nodes.tsv", ["node_id", "node_type", "bioactivity_class_label", "source_name", "source_record_id", "license_class", "access_date", "caveats"], bioactivity_node_rows)
    write_tsv(OUT / "ethnobotanical_use_record_nodes.tsv", ["node_id", "node_type", "source_name", "source_record_id", "taxon_label_raw", "people_group", "region", "source_citation", "license_class", "access_date", "sovereignty_flag", "caveats"], ethno_node_rows)
    write_tsv(OUT / "phytochemical_assertion_edges.tsv", PHYTO_FIELDS, phyto_edges)
    write_tsv(
        OUT / "bioactivity_assertion_edges.tsv",
        ["edge_id", "edge_type", "compound_id", "compound_label", "bioactivity_class", "assay_context", "source_name", "source_record_id", "citation", "license_class", "access_date", "allowed_evidence_scope", "does_not_support", "confidence", "caveats"],
        bio_edges,
    )
    write_tsv(OUT / "ethnobotanical_use_assertion_edges.tsv", ETHNO_FIELDS, ethno_edges)
    write_tsv(
        OUT / "source_coverage_summary.tsv",
        ["source_name", "access_status", "phytochemical_assertions", "ethnobotanical_assertions", "distinct_taxa", "distinct_compounds"],
        coverage_summary(phyto_edges, ethno_edges, compound_nodes, source_status),
    )
    write_audit_inputs(phyto_edges, ethno_edges, source_status)
    print(f"wrote staging tables to {OUT}")


if __name__ == "__main__":
    main()
