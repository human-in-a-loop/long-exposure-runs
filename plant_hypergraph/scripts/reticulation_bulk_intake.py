# created: 2026-05-17T18:00:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
# agent: worker
# milestone: M1.3

"""Local-file bulk intake for PhytoGraph M1.3 reticulation sources.

This script accepts only approved local files. It does not fetch source data
and it writes to a preview directory unless --promote is explicitly supplied.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


BASE = Path("substrate/staging/reticulation_sources")
NORMALIZED = BASE / "normalized"
PREVIEW = NORMALIZED / "bulk_intake_preview"

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

COUNT_FIELDS = PROVENANCE_FIELDS + [
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
PLOIDY_FIELDS = PROVENANCE_FIELDS + ["ploidy_state", "ploidy_assertion_status"]

SOURCE_LABELS = {
    "ccdb": ("Chromosome Counts Database", "0.86"),
    "plant_dna_cvalues": ("Plant DNA C-values Database", "0.88"),
    "curated_events": ("Curated systematic-botany reticulation event table", "0.80"),
}


def node_id(raw_name: str) -> str:
    cleaned = re.sub(r"\s+", "_", raw_name.strip())
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "", cleaned)
    return f"raw_name:{cleaned}"


def nonblank(value: object) -> str:
    return "" if value is None else str(value).strip()


def first(row: dict[str, object], aliases: Iterable[str]) -> str:
    lowered = {key.lower().strip(): value for key, value in row.items()}
    for alias in aliases:
        value = nonblank(lowered.get(alias.lower()))
        if value:
            return value
    return ""


def parse_count(raw: str) -> dict[str, object]:
    lowered = raw.strip().lower()
    count_type = "unknown"
    body = lowered
    if lowered.startswith("2n"):
        count_type = "2n"
        body = lowered[2:]
    elif lowered.startswith("n"):
        count_type = "n"
        body = lowered[1:]
    elif lowered.startswith("x"):
        count_type = "x"
        body = lowered[1:]
    nums = [int(x) for x in re.findall(r"\d+", body)]
    return {
        "raw_count": raw,
        "count_type": count_type,
        "parsed_min": min(nums) if nums else "",
        "parsed_max": max(nums) if nums else "",
        "is_range": bool(re.search(r"\d+\s*[-–]\s*\d+", body)),
        "is_approximate": any(token in lowered for token in ["ca", "circa", "~", "approx"]),
        "is_mixed_or_irregular": any(token in lowered for token in ["+", "b", "ii", ";", ","]),
        "parse_status": "parsed_simple" if nums else "raw_only",
    }


def load_rows(path: Path) -> list[dict[str, object]]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        with path.open(newline="", encoding="utf-8") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            delimiter = "\t" if suffix == ".tsv" else csv.Sniffer().sniff(sample, delimiters=",\t").delimiter
            return list(csv.DictReader(handle, delimiter=delimiter))
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("rows", [])
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list of row objects or {'rows': [...]}")
        return [dict(row) for row in data]
    if suffix == ".xlsx":
        try:
            import pandas as pd  # type: ignore
        except ImportError as exc:
            raise ValueError("XLSX input requires pandas/openpyxl in this environment") from exc
        return pd.read_excel(path).fillna("").to_dict(orient="records")
    raise ValueError(f"Unsupported input extension: {path.suffix}")


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def base_edge(args: argparse.Namespace, edge_type: str, raw_name: str, roles: dict[str, object], caveats: dict[str, object]) -> dict[str, object]:
    source_name, reliability = SOURCE_LABELS[args.source]
    return {
        "edge_type": edge_type,
        "raw_scientific_name": raw_name,
        "canonical_node_id": node_id(raw_name),
        "node_roles_json": json.dumps(roles, sort_keys=True),
        "source_id": args.source,
        "source_name": source_name,
        "source_version_or_release": args.source_version,
        "access_date": args.access_date,
        "license": args.license,
        "attribution": args.attribution,
        "confidence": args.confidence,
        "source_reliability": reliability,
        "allowed_evidence_scope": "",
        "caveats_json": json.dumps(caveats, sort_keys=True),
        "temporal_annotation": args.temporal_annotation or "",
    }


def require_row_fields(row: dict[str, object], checks: dict[str, str], row_number: int) -> None:
    missing = [label for label, value in checks.items() if not nonblank(value)]
    if missing:
        raise ValueError(f"row {row_number} missing required field(s): {', '.join(missing)}")


def normalize_count_rows(args: argparse.Namespace, rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    out: list[dict[str, object]] = []
    for i, row in enumerate(rows, start=2):
        raw_name = first(row, ["raw_scientific_name", "scientific_name", "taxon", "name"])
        raw_count = first(row, ["raw_count", "chromosome_count", "count", "count_text"])
        record_id = first(row, ["source_record_id", "record_id", "id", "citation_id"])
        require_row_fields(row, {"raw_scientific_name": raw_name, "raw_count": raw_count, "source_record_id": record_id}, i)
        parsed = parse_count(raw_count)
        caveats = {
            "bulk_intake_mode": "approved_local_file",
            "acquisition_route": args.acquisition_route,
            "source_record_id": record_id,
            "verbatim_row": row,
            **parsed,
        }
        edge = base_edge(
            args,
            "chromosome_count_assertion",
            raw_name,
            {"taxon": node_id(raw_name), "chromosome_count": raw_count, "source": args.source, "source_record_id": record_id},
            caveats,
        )
        edge.update(parsed)
        edge["count_source_type"] = first(row, ["count_source_type", "count_type"]) or parsed["count_type"]
        edge["allowed_evidence_scope"] = "supports reported chromosome count only; does not support uniform species ploidy or a polyploidization event"
        out.append(edge)
    return {"chromosome_count_assertions": out}


def normalize_cvalue_rows(args: argparse.Namespace, rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    out: list[dict[str, object]] = []
    for i, row in enumerate(rows, start=2):
        raw_name = first(row, ["raw_scientific_name", "scientific_name", "taxon", "name"])
        ploidy = first(row, ["ploidy_state", "ploidy", "inferred_ploidy"])
        record_id = first(row, ["source_record_id", "record_id", "id", "citation_id"])
        require_row_fields(row, {"raw_scientific_name": raw_name, "ploidy_state": ploidy, "source_record_id": record_id}, i)
        caveats = {
            "bulk_intake_mode": "approved_local_file",
            "acquisition_route": args.acquisition_route,
            "source_record_id": record_id,
            "verbatim_row": row,
            "not_established_source_fact": True,
        }
        edge = base_edge(
            args,
            "reticulate_inheritance_evidence",
            raw_name,
            {"taxon": node_id(raw_name), "ploidy_state": ploidy, "source": args.source, "source_record_id": record_id},
            caveats,
        )
        edge["ploidy_state"] = ploidy
        edge["ploidy_assertion_status"] = "inferred_supporting_evidence_not_event"
        edge["allowed_evidence_scope"] = "supports caveated ploidy-context evidence only; does not establish event timing or progenitors"
        out.append(edge)
    return {"ploidy_state_assertions": out}


def parent_names(row: dict[str, object]) -> list[str]:
    encoded = first(row, ["parent_taxa_json", "parents_json"])
    if encoded:
        data = json.loads(encoded)
        if not isinstance(data, list):
            raise ValueError("parent_taxa_json must decode to a list")
        return [nonblank(item) for item in data if nonblank(item)]
    parent_text = first(row, ["parent_taxa", "parents"])
    if parent_text:
        return [part.strip() for part in re.split(r"[|;]", parent_text) if part.strip()]
    return [name for name in [first(row, ["parent1", "parent_a"]), first(row, ["parent2", "parent_b"]), first(row, ["parent3", "parent_c"])] if name]


def normalize_event_rows(args: argparse.Namespace, rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    hybrid: list[dict[str, object]] = []
    poly: list[dict[str, object]] = []
    evidence: list[dict[str, object]] = []
    for i, row in enumerate(rows, start=2):
        child = first(row, ["child_raw_scientific_name", "raw_scientific_name", "child", "taxon", "name"])
        record_id = first(row, ["source_record_id", "record_id", "id", "citation_id"])
        declared = first(row, ["event_type", "edge_type"]).lower()
        parents = parent_names(row)
        require_row_fields(row, {"child_raw_scientific_name": child, "event_type": declared, "source_record_id": record_id}, i)
        if declared not in {"hybridization_event", "polyploidization_event", "reticulate_inheritance_evidence"}:
            raise ValueError(f"row {i} has unsupported event_type: {declared}")
        roles = {
            "child_taxon": node_id(child),
            "parent_taxa": [node_id(parent) for parent in parents],
            "source": args.source,
            "source_record_id": record_id,
        }
        caveats = {
            "bulk_intake_mode": "approved_local_file",
            "acquisition_route": args.acquisition_route,
            "source_record_id": record_id,
            "parent_names_raw": parents,
            "verbatim_row": row,
        }
        if len(parents) < 2:
            if not args.demote_one_parent:
                raise ValueError(f"row {i} has fewer than two parent roles")
            edge = base_edge(args, "reticulate_inheritance_evidence", child, roles, {**caveats, "demotion_reason": "fewer_than_two_parent_roles"})
            edge["confidence"] = "0.45"
            edge["allowed_evidence_scope"] = "supports caveated reticulation mention only; insufficient parent roles for event assertion"
            evidence.append(edge)
            continue
        edge = base_edge(args, declared, child, roles, caveats)
        edge["allowed_evidence_scope"] = "supports named hybridization/polyploidization event as source-backed assertion; does not support novel taxonomy or precise dating"
        if declared == "hybridization_event":
            hybrid.append(edge)
        elif declared == "polyploidization_event":
            poly.append(edge)
        else:
            edge["allowed_evidence_scope"] = "supports multi-parent reticulate inheritance evidence; does not resolve a single phylogenetic placement"
            evidence.append(edge)
        ev = base_edge(args, "reticulate_inheritance_evidence", child, roles, caveats)
        ev["allowed_evidence_scope"] = "supports multi-parent reticulate inheritance evidence; does not resolve a single phylogenetic placement"
        evidence.append(ev)
    return {
        "hybridization_events": hybrid,
        "polyploidization_events": poly,
        "reticulate_inheritance_evidence": evidence,
    }


def normalize(args: argparse.Namespace, rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    if args.source == "ccdb":
        return normalize_count_rows(args, rows)
    if args.source == "plant_dna_cvalues":
        return normalize_cvalue_rows(args, rows)
    return normalize_event_rows(args, rows)


def output_fields(table: str) -> list[str]:
    if table == "chromosome_count_assertions":
        return COUNT_FIELDS
    if table == "ploidy_state_assertions":
        return PLOIDY_FIELDS
    return PROVENANCE_FIELDS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, choices=sorted(SOURCE_LABELS))
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=PREVIEW)
    parser.add_argument("--promote", action="store_true", help="write directly to normalized staging tables")
    parser.add_argument("--demote-one-parent", action="store_true", help="demote one-parent event rows to reticulate evidence")
    parser.add_argument("--source-version", required=True)
    parser.add_argument("--access-date", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--attribution", required=True)
    parser.add_argument("--acquisition-route", required=True)
    parser.add_argument("--confidence", default="0.70")
    parser.add_argument("--temporal-annotation", default="")
    args = parser.parse_args(argv)
    for field in ["source_version", "access_date", "license", "attribution", "acquisition_route"]:
        if not getattr(args, field).strip():
            parser.error(f"--{field.replace('_', '-')} is required and cannot be blank")
    try:
        datetime.strptime(args.access_date, "%Y-%m-%d")
    except ValueError:
        parser.error("--access-date must be YYYY-MM-DD")
    if args.promote:
        args.output_dir = NORMALIZED
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows = load_rows(args.input)
    normalized = normalize(args, rows)
    counts = {}
    for table, table_rows in normalized.items():
        path = args.output_dir / f"{table}.tsv"
        write_tsv(path, table_rows, output_fields(table))
        counts[table] = len(table_rows)
    write_tsv(
        args.output_dir / "bulk_intake_row_counts.tsv",
        [{"table": table, "rows": count, "generated_at": datetime.now(timezone.utc).isoformat()} for table, count in counts.items()],
        ["table", "rows", "generated_at"],
    )
    print(json.dumps({"source": args.source, "output_dir": args.output_dir.as_posix(), "row_counts": counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
