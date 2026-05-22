# created: 2026-05-17T17:35:00Z
# cycle: 2
# run_id: fork-e34b5b2c1c6c-clone-5
# agent: worker
# milestone: M1.7
"""Profile M1.7 source density for Barrier-1 handoff controls."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "substrate" / "staging" / "chemodiversity_ethnobotany_sources"

PHYTO = OUT / "phytochemical_assertion_edges.tsv"
ETHNO = OUT / "ethnobotanical_use_assertion_edges.tsv"
COVERAGE = OUT / "source_coverage_summary.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def norm_family(row: dict[str, str]) -> str:
    value = (row.get("family_raw") or "").strip()
    return value if value else "__missing_family__"


def pct(part: int, total: int) -> str:
    return f"{(part / total):.6f}" if total else "0.000000"


def summarize_source(
    source: str,
    domain: str,
    rows: list[dict[str, str]],
    record_field: str,
    citation_field: str,
) -> dict[str, object]:
    source_rows = [r for r in rows if r.get("source_name") == source]
    families = Counter(norm_family(r) for r in source_rows)
    dominant_family, dominant_count = ("", 0)
    if families:
        dominant_family, dominant_count = families.most_common(1)[0]
    compounds = {r.get("compound_id", "") for r in source_rows if r.get("compound_id", "").strip()}
    uses = {r.get("use_category", "") for r in source_rows if r.get("use_category", "").strip()}
    return {
        "source_name": source,
        "edge_domain": domain,
        "assertion_count": len(source_rows),
        "distinct_taxa": len({r.get("taxon_label_raw", "") for r in source_rows if r.get("taxon_label_raw", "").strip()}),
        "distinct_families": len(families),
        "missing_family_rows": families.get("__missing_family__", 0),
        "distinct_compounds": len(compounds),
        "distinct_use_categories": len(uses),
        "dominant_family": dominant_family,
        "dominant_family_assertions": dominant_count,
        "dominant_family_share": pct(dominant_count, len(source_rows)),
        "record_identifier_field": record_field,
        "citation_field": citation_field,
        "license_classes": "|".join(sorted({r.get("license_class", "") for r in source_rows if r.get("license_class", "").strip()})),
        "access_dates": "|".join(sorted({r.get("access_date", "") for r in source_rows if r.get("access_date", "").strip()})),
        "evidence_scopes": "|".join(sorted({r.get("allowed_evidence_scope", "") for r in source_rows if r.get("allowed_evidence_scope", "").strip()})),
    }


def coverage_metrics(phyto_rows: list[dict[str, str]], ethno_rows: list[dict[str, str]]) -> dict[str, int]:
    family_counts = Counter(norm_family(r) for r in phyto_rows)
    return {
        "phytochemical_assertions": len(phyto_rows),
        "ethnobotanical_assertions": len(ethno_rows),
        "distinct_phytochemical_taxa": len({r.get("taxon_label_raw", "") for r in phyto_rows if r.get("taxon_label_raw", "").strip()}),
        "distinct_compounds": len({r.get("compound_id", "") for r in phyto_rows if r.get("compound_id", "").strip()}),
        "families_ge_100_phytochemical_assertions": sum(1 for count in family_counts.values() if count >= 100),
        "distinct_ethnobotanical_taxa": len({r.get("taxon_label_raw", "") for r in ethno_rows if r.get("taxon_label_raw", "").strip()}),
        "distinct_use_categories": len({r.get("use_category", "") for r in ethno_rows if r.get("use_category", "").strip()}),
    }


def main() -> None:
    phyto = read_tsv(PHYTO)
    ethno = read_tsv(ETHNO)
    coverage = read_tsv(COVERAGE)
    all_sources = [r["source_name"] for r in coverage]

    source_rows: list[dict[str, object]] = []
    for source in all_sources:
        source_rows.append(summarize_source(source, "phytochemical_assertion", phyto, "source_record_id", "citation"))
        source_rows.append(summarize_source(source, "ethnobotanical_use_assertion", ethno, "source_record_id", "source_citation"))

    source_fields = [
        "source_name",
        "edge_domain",
        "assertion_count",
        "distinct_taxa",
        "distinct_families",
        "missing_family_rows",
        "distinct_compounds",
        "distinct_use_categories",
        "dominant_family",
        "dominant_family_assertions",
        "dominant_family_share",
        "record_identifier_field",
        "citation_field",
        "license_classes",
        "access_dates",
        "evidence_scopes",
    ]
    write_tsv(OUT / "source_bias_profile.tsv", source_rows, source_fields)

    by_family_source: dict[tuple[str, str], dict[str, object]] = {}
    family_totals: Counter[str] = Counter()
    for source in all_sources:
        for family in {norm_family(r) for r in phyto if r.get("source_name") == source} | {norm_family(r) for r in ethno if r.get("source_name") == source}:
            by_family_source[(family, source)] = {
                "family_raw": family,
                "source_name": source,
                "phytochemical_assertions": 0,
                "phytochemical_distinct_taxa": 0,
                "distinct_compounds": 0,
                "ethnobotanical_assertions": 0,
                "ethnobotanical_distinct_taxa": 0,
                "distinct_use_categories": 0,
                "total_assertions": 0,
                "source_share_within_family": "0.000000",
                "record_identifier_fields": "source_record_id",
                "citation_fields": "citation|source_citation",
                "license_classes": "",
                "access_dates": "",
                "evidence_scopes": "",
            }

    grouped_phyto: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    grouped_ethno: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in phyto:
        grouped_phyto[(norm_family(row), row["source_name"])].append(row)
    for row in ethno:
        grouped_ethno[(norm_family(row), row["source_name"])].append(row)

    for key in set(grouped_phyto) | set(grouped_ethno):
        family, source = key
        p_rows = grouped_phyto.get(key, [])
        e_rows = grouped_ethno.get(key, [])
        total = len(p_rows) + len(e_rows)
        family_totals[family] += total
        by_family_source[key] = {
            "family_raw": family,
            "source_name": source,
            "phytochemical_assertions": len(p_rows),
            "phytochemical_distinct_taxa": len({r["taxon_label_raw"] for r in p_rows}),
            "distinct_compounds": len({r["compound_id"] for r in p_rows if r.get("compound_id", "").strip()}),
            "ethnobotanical_assertions": len(e_rows),
            "ethnobotanical_distinct_taxa": len({r["taxon_label_raw"] for r in e_rows}),
            "distinct_use_categories": len({r["use_category"] for r in e_rows if r.get("use_category", "").strip()}),
            "total_assertions": total,
            "source_share_within_family": "0.000000",
            "record_identifier_fields": "source_record_id",
            "citation_fields": "citation|source_citation",
            "license_classes": "|".join(sorted({r.get("license_class", "") for r in p_rows + e_rows if r.get("license_class", "").strip()})),
            "access_dates": "|".join(sorted({r.get("access_date", "") for r in p_rows + e_rows if r.get("access_date", "").strip()})),
            "evidence_scopes": "|".join(sorted({r.get("allowed_evidence_scope", "") for r in p_rows + e_rows if r.get("allowed_evidence_scope", "").strip()})),
        }

    matrix_rows = []
    for key, row in by_family_source.items():
        family, _source = key
        row["source_share_within_family"] = pct(int(row["total_assertions"]), family_totals[family])
        matrix_rows.append(row)
    matrix_rows.sort(key=lambda r: (-int(r["total_assertions"]), str(r["family_raw"]), str(r["source_name"])))
    matrix_fields = [
        "family_raw",
        "source_name",
        "phytochemical_assertions",
        "phytochemical_distinct_taxa",
        "distinct_compounds",
        "ethnobotanical_assertions",
        "ethnobotanical_distinct_taxa",
        "distinct_use_categories",
        "total_assertions",
        "source_share_within_family",
        "record_identifier_fields",
        "citation_fields",
        "license_classes",
        "access_dates",
        "evidence_scopes",
    ]
    write_tsv(OUT / "family_source_matrix.tsv", matrix_rows, matrix_fields)

    base = coverage_metrics(phyto, ethno)
    scenarios: list[dict[str, object]] = []

    def add_scenario(name: str, omitted_source: str, p_rows: list[dict[str, str]], e_rows: list[dict[str, str]]) -> None:
        metrics = coverage_metrics(p_rows, e_rows)
        scenarios.append(
            {
                "scenario": name,
                "omitted_source": omitted_source,
                **metrics,
                "retained_phytochemical_assertion_share": pct(metrics["phytochemical_assertions"], base["phytochemical_assertions"]),
                "retained_ethnobotanical_assertion_share": pct(metrics["ethnobotanical_assertions"], base["ethnobotanical_assertions"]),
                "retained_compound_share": pct(metrics["distinct_compounds"], base["distinct_compounds"]),
                "retained_phytochemical_taxon_share": pct(metrics["distinct_phytochemical_taxa"], base["distinct_phytochemical_taxa"]),
                "retained_ethnobotanical_taxon_share": pct(metrics["distinct_ethnobotanical_taxa"], base["distinct_ethnobotanical_taxa"]),
            }
        )

    add_scenario("all_sources", "", phyto, ethno)
    for source in all_sources:
        add_scenario(
            f"minus_source:{source}",
            source,
            [r for r in phyto if r.get("source_name") != source],
            [r for r in ethno if r.get("source_name") != source],
        )
    add_scenario("phytochemistry_only", "all_ethnobotanical_assertions", phyto, [])
    add_scenario("ethnobotany_only", "all_phytochemical_assertions", [], ethno)

    scenario_fields = [
        "scenario",
        "omitted_source",
        "phytochemical_assertions",
        "ethnobotanical_assertions",
        "distinct_phytochemical_taxa",
        "distinct_compounds",
        "families_ge_100_phytochemical_assertions",
        "distinct_ethnobotanical_taxa",
        "distinct_use_categories",
        "retained_phytochemical_assertion_share",
        "retained_ethnobotanical_assertion_share",
        "retained_compound_share",
        "retained_phytochemical_taxon_share",
        "retained_ethnobotanical_taxon_share",
    ]
    write_tsv(OUT / "leave_one_source_out_coverage.tsv", scenarios, scenario_fields)

    summary = {
        "source_bias_profile_rows": len(source_rows),
        "family_source_matrix_rows": len(matrix_rows),
        "leave_one_source_out_rows": len(scenarios),
        "base_coverage": base,
        "top_family_source_rows": matrix_rows[:20],
    }
    (OUT / "source_bias_profile_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
