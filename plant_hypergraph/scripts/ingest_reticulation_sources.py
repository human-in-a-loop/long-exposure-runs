# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
# agent: worker
# milestone: M1.3

"""Stage PhytoGraph M1.3 reticulation source probes and conservative seed rows.

The current pass is intentionally conservative: it probes documented public
web endpoints, preserves raw responses and checksums, and stages only source-
backed seed assertions where no bulk export endpoint is reachable.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE = Path("substrate/staging/reticulation_sources")
RAW = BASE / "raw"
NORMALIZED = BASE / "normalized"
PLOTS = BASE / "plots"
ACCESS_DATE = datetime.now(timezone.utc).date().isoformat()

PROVENANCE_FIELDS = [
    "edge_type",
    "raw_scientific_name",
    "canonical_node_id",
    "node_roles_json",
    "source_id",
    "source_name",
    "source_version_or_release",
    "access_date",
    "license",
    "attribution",
    "confidence",
    "source_reliability",
    "allowed_evidence_scope",
    "caveats_json",
    "temporal_annotation",
]


@dataclass(frozen=True)
class SourceProbe:
    source_id: str
    source_name: str
    url: str
    license: str
    attribution: str
    reliability: str
    version: str
    expected_bulk_access: str


SOURCE_PROBES = [
    SourceProbe(
        "ccdb",
        "Chromosome Counts Database",
        "https://ccdb.tau.ac.il/",
        "Not stated on probed pages; citation-required database use",
        "CCDB, Tel Aviv University; Rice et al. 2015",
        "0.86",
        "site probed 2026-05-17; landing page reports version 1.66.6 in prior audit",
        "documented export/API not found from landing and browse pages",
    ),
    SourceProbe(
        "plant_dna_cvalues",
        "Plant DNA C-values Database",
        "https://cvalues.science.kew.org/",
        "Not stated on probed pages; cite Kew Plant DNA C-values Database",
        "Leitch, Johnston, Pellicer, Hidalgo, Bennett; Royal Botanic Gardens, Kew",
        "0.88",
        "Release 7.1, April 2019",
        "search web app reachable; all-row export endpoint not found from probed pages",
    ),
    SourceProbe(
        "wood_2009_polyploid_speciation",
        "Wood et al. 2009 polyploid speciation synthesis",
        "https://doi.org/10.1073/pnas.0811575106",
        "Article/supplement copyright by PNAS; factual extracted rows only",
        "Wood et al. 2009, PNAS",
        "0.82",
        "2009 PNAS article",
        "supplement URL tested but machine retrieval blocked; cite source and stage canonical public examples conservatively",
    ),
]


CURATED_COUNTS = [
    ("Triticum aestivum", "2n=42", "2n", "Poaceae", "hexaploid crop count used as positive validation seed"),
    ("Brassica napus", "2n=38", "2n", "Brassicaceae", "amphidiploid crop count used as positive validation seed"),
    ("Spartina anglica", "2n=120", "2n", "Poaceae", "allopolyploid marsh grass count used as positive validation seed"),
    ("Tragopogon mirus", "2n=24", "2n", "Asteraceae", "recent allopolyploid count used as positive validation seed"),
    ("Tragopogon miscellus", "2n=24", "2n", "Asteraceae", "recent allopolyploid count used as positive validation seed"),
    ("Arabidopsis thaliana", "2n=10", "2n", "Brassicaceae", "negative validation seed: count-only row must not create event"),
    ("Zea mays", "2n=20", "2n", "Poaceae", "count-only row"),
    ("Oryza sativa", "2n=24", "2n", "Poaceae", "count-only row"),
    ("Gossypium hirsutum", "2n=52", "2n", "Malvaceae", "polyploid crop count seed"),
    ("Arachis hypogaea", "2n=40", "2n", "Fabaceae", "polyploid crop count seed"),
    ("Musa acuminata", "2n=22", "2n", "Musaceae", "banana progenitor count seed"),
    ("Musa balbisiana", "2n=22", "2n", "Musaceae", "banana progenitor count seed"),
]

CURATED_PLOIDY = [
    ("Triticum aestivum", "hexaploid", "inferred_from_literature_synthesis"),
    ("Brassica napus", "amphidiploid", "inferred_from_literature_synthesis"),
    ("Spartina anglica", "allopolyploid", "inferred_from_literature_synthesis"),
    ("Tragopogon mirus", "allopolyploid", "inferred_from_literature_synthesis"),
    ("Tragopogon miscellus", "allopolyploid", "inferred_from_literature_synthesis"),
    ("Arabidopsis thaliana", "diploid", "count_context_only_not_event"),
]

CURATED_EVENTS = [
    (
        "polyploidization_event",
        "Triticum aestivum",
        ["Triticum urartu", "Aegilops speltoides lineage", "Aegilops tauschii"],
        "hexaploid bread wheat allopolyploid origin; progenitor roles summarized from systematic-botany consensus",
    ),
    (
        "polyploidization_event",
        "Brassica napus",
        ["Brassica rapa", "Brassica oleracea"],
        "amphidiploid origin represented conservatively as source-backed synthesis event",
    ),
    (
        "hybridization_event",
        "Spartina anglica",
        ["Spartina alterniflora", "Spartina maritima"],
        "hybrid origin followed by chromosome doubling represented as literature-backed event",
    ),
    (
        "polyploidization_event",
        "Tragopogon mirus",
        ["Tragopogon dubius", "Tragopogon porrifolius"],
        "recent allopolyploid event represented as canonical positive validation seed",
    ),
    (
        "polyploidization_event",
        "Tragopogon miscellus",
        ["Tragopogon dubius", "Tragopogon pratensis"],
        "recent allopolyploid event represented as canonical positive validation seed",
    ),
]


def node_id(raw_name: str) -> str:
    cleaned = re.sub(r"\s+", "_", raw_name.strip())
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "", cleaned)
    return f"raw_name:{cleaned}"


def parse_count(raw: str) -> dict[str, str | bool | int | None]:
    lowered = raw.strip().lower()
    count_type = "unknown"
    if lowered.startswith("2n"):
        count_type = "2n"
    elif lowered.startswith("n"):
        count_type = "n"
    elif lowered.startswith("x"):
        count_type = "x"
    nums = [int(x) for x in re.findall(r"\d+", lowered)]
    is_range = bool(re.search(r"\d+\s*[-–]\s*\d+", lowered))
    return {
        "raw_count": raw,
        "count_type": count_type,
        "parsed_min": min(nums) if nums else None,
        "parsed_max": max(nums) if nums else None,
        "is_range": is_range,
        "is_approximate": any(token in lowered for token in ["ca", "circa", "~", "approx"]),
        "is_mixed_or_irregular": any(token in lowered for token in ["+", "b", "ii", ";", ","]),
        "parse_status": "parsed_simple" if nums else "raw_only",
    }


def fetch_probe(source: SourceProbe) -> dict[str, str]:
    request = Request(source.url, headers={"User-Agent": "PhytoGraph-M1.3-access-probe/0.1"})
    raw_path = RAW / f"{source.source_id}.html"
    try:
        with urlopen(request, timeout=20) as response:
            data = response.read()
            status = str(response.status)
            content_type = response.headers.get("content-type", "")
        raw_path.write_bytes(data)
        outcome = "reachable"
    except HTTPError as exc:
        data = exc.read()
        raw_path.write_bytes(data)
        status = str(exc.code)
        content_type = exc.headers.get("content-type", "") if exc.headers else ""
        outcome = "http_error"
    except URLError as exc:
        data = str(exc.reason).encode("utf-8", errors="replace")
        raw_path.write_bytes(data)
        status = "url_error"
        content_type = "text/plain"
        outcome = "url_error"
    checksum = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    return {
        "source_id": source.source_id,
        "source_name": source.source_name,
        "url": source.url,
        "raw_path": raw_path.as_posix(),
        "sha256": checksum,
        "http_status": status,
        "content_type": content_type,
        "access_date": ACCESS_DATE,
        "probe_outcome": outcome,
        "expected_bulk_access": source.expected_bulk_access,
    }


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def base_edge(edge_type: str, raw_name: str, source: SourceProbe, roles: dict, caveats: dict) -> dict[str, object]:
    return {
        "edge_type": edge_type,
        "raw_scientific_name": raw_name,
        "canonical_node_id": node_id(raw_name),
        "node_roles_json": json.dumps(roles, sort_keys=True),
        "source_id": source.source_id,
        "source_name": source.source_name,
        "source_version_or_release": source.version,
        "access_date": ACCESS_DATE,
        "license": source.license,
        "attribution": source.attribution,
        "confidence": "0.62",
        "source_reliability": source.reliability,
        "allowed_evidence_scope": "",
        "caveats_json": json.dumps(caveats, sort_keys=True),
        "temporal_annotation": "",
    }


def build_rows() -> dict[str, list[dict[str, object]]]:
    ccdb = SOURCE_PROBES[0]
    cvalues = SOURCE_PROBES[1]
    wood = SOURCE_PROBES[2]

    count_rows = []
    for raw_name, raw_count, count_source_type, family, note in CURATED_COUNTS:
        parsed = parse_count(raw_count)
        row = base_edge(
            "chromosome_count_assertion",
            raw_name,
            ccdb,
            {"taxon": node_id(raw_name), "chromosome_count": raw_count, "source": ccdb.source_id},
            {
                "staging_mode": "curated_seed_not_bulk_ccdb",
                "family_or_group_hint": family,
                "note": note,
                **parsed,
            },
        )
        row.update(parsed)
        row["count_source_type"] = count_source_type
        row["allowed_evidence_scope"] = "supports reported chromosome count only; does not support uniform species ploidy or a polyploidization event"
        count_rows.append(row)

    ploidy_rows = []
    for raw_name, ploidy, evidence_mode in CURATED_PLOIDY:
        row = base_edge(
            "reticulate_inheritance_evidence",
            raw_name,
            cvalues if raw_name == "Arabidopsis thaliana" else wood,
            {"taxon": node_id(raw_name), "ploidy_state": ploidy, "source": wood.source_id},
            {"staging_mode": "curated_seed", "evidence_mode": evidence_mode, "not_established_source_fact": True},
        )
        row["edge_type"] = "reticulate_inheritance_evidence"
        row["ploidy_state"] = ploidy
        row["ploidy_assertion_status"] = "inferred_supporting_evidence_not_event"
        row["allowed_evidence_scope"] = "supports caveated ploidy-context evidence only; does not establish event timing or progenitors"
        ploidy_rows.append(row)

    event_rows = []
    reticulate_rows = []
    for edge_type, child, parents, note in CURATED_EVENTS:
        roles = {
            "child_taxon": node_id(child),
            "parent_taxa": [node_id(parent) for parent in parents],
            "source": wood.source_id,
        }
        caveats = {
            "staging_mode": "curated_canonical_seed",
            "source_assertion_level": "literature_synthesis_event",
            "note": note,
            "parent_names_raw": parents,
        }
        row = base_edge(edge_type, child, wood, roles, caveats)
        row["confidence"] = "0.70"
        row["allowed_evidence_scope"] = (
            "supports named hybridization/polyploidization event as source-backed synthesis; "
            "does not support novel taxonomy or precise dating"
        )
        event_rows.append(row)

        evidence = base_edge("reticulate_inheritance_evidence", child, wood, roles, caveats)
        evidence["confidence"] = "0.72"
        evidence["allowed_evidence_scope"] = "supports multi-parent reticulate inheritance evidence; does not resolve a single phylogenetic placement"
        reticulate_rows.append(evidence)

    return {
        "chromosome_count_assertions": count_rows,
        "ploidy_state_assertions": ploidy_rows,
        "hybridization_events": [r for r in event_rows if r["edge_type"] == "hybridization_event"],
        "polyploidization_events": [r for r in event_rows if r["edge_type"] == "polyploidization_event"],
        "reticulate_inheritance_evidence": reticulate_rows,
    }


def write_plots(row_counts: dict[str, int]) -> None:
    import matplotlib.pyplot as plt

    PLOTS.mkdir(parents=True, exist_ok=True)
    labels = ["chromosome_count", "reticulate_events"]
    observed = [
        row_counts["chromosome_count_assertions"],
        row_counts["hybridization_events"] + row_counts["polyploidization_events"] + row_counts["reticulate_inheritance_evidence"],
    ]
    targets = [30000, 2000]
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    x = range(len(labels))
    ax.bar([i - 0.18 for i in x], observed, width=0.36, label="staged rows")
    ax.bar([i + 0.18 for i in x], targets, width=0.36, label="M1.3 floor")
    ax.set_xticks(list(x), labels)
    ax.set_yscale("log")
    ax.set_ylabel("Rows, log scale")
    ax.set_title("Reticulation-source staged row counts vs targets")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS / "source_row_counts_vs_targets.png", dpi=160)
    plt.close(fig)

    family_counts: dict[str, int] = {}
    for _, _, _, family, _ in CURATED_COUNTS:
        family_counts[family] = family_counts.get(family, 0) + 1
    ordered = sorted(family_counts.items(), key=lambda item: item[1], reverse=True)
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.bar([name for name, _ in ordered], [count for _, count in ordered], color="#4c78a8")
    ax.set_ylabel("Seed chromosome-count rows")
    ax.set_title("Top family hints in staged count seeds")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(PLOTS / "top_families_count_bias.png", dpi=160)
    plt.close(fig)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    probes = [fetch_probe(source) for source in SOURCE_PROBES]
    write_tsv(RAW / "checksum_manifest.tsv", probes, list(probes[0].keys()))

    source_manifest = []
    for source, probe in zip(SOURCE_PROBES, probes):
        source_manifest.append(
            {
                **probe,
                "license": source.license,
                "attribution": source.attribution,
                "source_reliability": source.reliability,
                "source_version_or_release": source.version,
                "bias_profile": "temperate Northern Hemisphere and crop/model systems overrepresented; tropical understory lineages under-sampled",
                "bulk_scale_status": "access-limited in this run",
            }
        )
    write_tsv(NORMALIZED / "source_manifest.tsv", source_manifest, list(source_manifest[0].keys()))

    rows = build_rows()
    count_fields = PROVENANCE_FIELDS + [
        "raw_count",
        "count_type",
        "parsed_min",
        "parsed_max",
        "is_range",
        "is_approximate",
        "is_mixed_or_irregular",
        "parse_status",
        "count_source_type",
    ]
    write_tsv(NORMALIZED / "chromosome_count_assertions.tsv", rows["chromosome_count_assertions"], count_fields)
    ploidy_fields = PROVENANCE_FIELDS + ["ploidy_state", "ploidy_assertion_status"]
    write_tsv(NORMALIZED / "ploidy_state_assertions.tsv", rows["ploidy_state_assertions"], ploidy_fields)
    write_tsv(NORMALIZED / "hybridization_events.tsv", rows["hybridization_events"], PROVENANCE_FIELDS)
    write_tsv(NORMALIZED / "polyploidization_events.tsv", rows["polyploidization_events"], PROVENANCE_FIELDS)
    write_tsv(NORMALIZED / "reticulate_inheritance_evidence.tsv", rows["reticulate_inheritance_evidence"], PROVENANCE_FIELDS)

    row_counts = {name: len(value) for name, value in rows.items()}
    write_tsv(
        NORMALIZED / "row_counts.tsv",
        [{"table": key, "rows": value} for key, value in row_counts.items()],
        ["table", "rows"],
    )
    write_plots(row_counts)
    print(json.dumps({"access_date": ACCESS_DATE, "row_counts": row_counts}, indent=2))


if __name__ == "__main__":
    main()
