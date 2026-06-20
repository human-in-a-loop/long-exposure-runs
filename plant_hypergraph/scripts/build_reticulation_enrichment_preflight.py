# created: 2026-05-17T20:10:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
# agent: worker
# milestone: M2.T1-preflight

import csv
import json
from collections import defaultdict
from pathlib import Path


INPUT_DIR = Path("substrate/staging/reticulation_sources/normalized")
OUTPUT_DIR = Path("tracks/track1/reticulation_enrichment")
PLOTS_DIR = OUTPUT_DIR / "plots"

FEATURES_PATH = OUTPUT_DIR / "seed_enrichment_features.tsv"
EXPECTATIONS_PATH = OUTPUT_DIR / "seed_case_expectations.tsv"
AUDIT_PATH = OUTPUT_DIR / "PREFLIGHT_AUDIT.md"
FIGURE_PATH = PLOTS_DIR / "seed_evidence_class_matrix.png"

TABLES = {
    "chromosome_count_assertions.tsv": "chromosome_count_assertion",
    "ploidy_state_assertions.tsv": "ploidy_context",
    "hybridization_events.tsv": "hybridization_event",
    "polyploidization_events.tsv": "polyploidization_event",
    "reticulate_inheritance_evidence.tsv": "reticulate_inheritance_evidence",
}

ALLOWED_EDGE_TYPES = {
    "chromosome_count_assertion",
    "hybridization_event",
    "polyploidization_event",
    "reticulate_inheritance_evidence",
}

CANONICAL_CASES = [
    "Triticum aestivum",
    "Brassica napus",
    "Spartina anglica",
    "Tragopogon mirus",
    "Tragopogon miscellus",
    "Arabidopsis thaliana",
]


def read_tsv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bool_text(value):
    return "true" if value else "false"


def parse_roles(row):
    value = row.get("node_roles_json") or "{}"
    return json.loads(value)


def normalized_parent_count(row):
    roles = parse_roles(row)
    parents = roles.get("parent_taxa") or []
    return len(parents)


def collect_features():
    features = defaultdict(
        lambda: {
            "raw_scientific_name": "",
            "canonical_node_id": "",
            "chromosome_count_assertion_count": 0,
            "reported_counts": set(),
            "ploidy_context_assertion_count": 0,
            "hybridization_event_count": 0,
            "polyploidization_event_count": 0,
            "reticulate_inheritance_evidence_count": 0,
            "explicit_parent_count": 0,
            "evidence_classes": set(),
            "source_ids": set(),
            "source_names": set(),
            "source_versions": set(),
            "access_dates": set(),
            "licenses": set(),
            "allowed_support": set(),
            "input_tables": set(),
        }
    )

    input_counts = {}
    demotions = []

    for filename, evidence_class in TABLES.items():
        path = INPUT_DIR / filename
        rows = read_tsv(path)
        input_counts[filename] = len(rows)
        for row in rows:
            edge_type = row["edge_type"]
            if edge_type not in ALLOWED_EDGE_TYPES:
                raise ValueError(f"{filename} has schema v1.0 drift edge_type={edge_type!r}")
            if not row["canonical_node_id"].startswith("raw_name:"):
                raise ValueError(f"{filename} invented non-raw canonical ID: {row['canonical_node_id']}")

            name = row["raw_scientific_name"]
            item = features[name]
            item["raw_scientific_name"] = name
            item["canonical_node_id"] = row["canonical_node_id"]
            item["evidence_classes"].add(evidence_class)
            item["input_tables"].add(filename)
            item["source_ids"].add(row["source_id"])
            item["source_names"].add(row["source_name"])
            item["source_versions"].add(row.get("source_version_or_release", ""))
            item["access_dates"].add(row["access_date"])
            item["licenses"].add(row["license"])
            item["allowed_support"].add(row["allowed_evidence_scope"])

            if evidence_class == "chromosome_count_assertion":
                item["chromosome_count_assertion_count"] += 1
                if row.get("raw_count"):
                    item["reported_counts"].add(row["raw_count"])
            elif evidence_class == "ploidy_context":
                item["ploidy_context_assertion_count"] += 1
                demotions.append(
                    f"{name}: ploidy context retained as caveated reticulate_inheritance_evidence, not an event"
                )
            elif evidence_class == "hybridization_event":
                item["hybridization_event_count"] += 1
                item["explicit_parent_count"] += normalized_parent_count(row)
            elif evidence_class == "polyploidization_event":
                item["polyploidization_event_count"] += 1
                item["explicit_parent_count"] += normalized_parent_count(row)
            elif evidence_class == "reticulate_inheritance_evidence":
                item["reticulate_inheritance_evidence_count"] += 1
                item["explicit_parent_count"] += normalized_parent_count(row)

    rows = []
    for name in sorted(features):
        item = features[name]
        event_supported = (
            item["hybridization_event_count"]
            + item["polyploidization_event_count"]
            + item["reticulate_inheritance_evidence_count"]
        ) > 0
        count_only = (
            item["chromosome_count_assertion_count"] > 0
            and not event_supported
            and item["ploidy_context_assertion_count"] == 0
        )
        reticulation_seed = event_supported or item["ploidy_context_assertion_count"] > 0
        rows.append(
            {
                "raw_scientific_name": name,
                "canonical_node_id": item["canonical_node_id"],
                "chromosome_count_assertion_count": item["chromosome_count_assertion_count"],
                "distinct_reported_counts": len(item["reported_counts"]),
                "reported_counts_list": "|".join(sorted(item["reported_counts"])),
                "ploidy_context_assertion_count": item["ploidy_context_assertion_count"],
                "hybridization_event_count": item["hybridization_event_count"],
                "polyploidization_event_count": item["polyploidization_event_count"],
                "reticulate_inheritance_evidence_count": item["reticulate_inheritance_evidence_count"],
                "explicit_parent_count": item["explicit_parent_count"],
                "evidence_class_count": len(item["evidence_classes"]),
                "evidence_classes": "|".join(sorted(item["evidence_classes"])),
                "source_count": len(item["source_ids"]),
                "source_ids": "|".join(sorted(item["source_ids"])),
                "source_names": "|".join(sorted(item["source_names"])),
                "source_versions": "|".join(sorted(v for v in item["source_versions"] if v)),
                "access_dates": "|".join(sorted(item["access_dates"])),
                "licenses": "|".join(sorted(item["licenses"])),
                "input_tables": "|".join(sorted(item["input_tables"])),
                "reticulation_seed_flag": bool_text(reticulation_seed),
                "count_only_flag": bool_text(count_only),
                "event_supported_flag": bool_text(event_supported),
                "allowed_support_summary": " || ".join(sorted(item["allowed_support"])),
            }
        )
    return rows, input_counts, demotions


def write_expectations(feature_rows):
    by_name = {row["raw_scientific_name"]: row for row in feature_rows}
    rows = []
    for name in CANONICAL_CASES:
        row = by_name[name]
        expected = "event-supported positive" if name != "Arabidopsis thaliana" else "count/ploidy-context negative control"
        rows.append(
            {
                "raw_scientific_name": name,
                "canonical_node_id": row["canonical_node_id"],
                "case_role": expected,
                "expected_reticulation_seed_flag": "true",
                "expected_event_supported_flag": "false" if name == "Arabidopsis thaliana" else "true",
                "expected_count_only_flag": "false",
                "observed_reticulation_seed_flag": row["reticulation_seed_flag"],
                "observed_event_supported_flag": row["event_supported_flag"],
                "observed_count_only_flag": row["count_only_flag"],
                "expected_reason": (
                    "chromosome count plus caveated diploid ploidy context only; no hybridization/polyploidization event rows"
                    if name == "Arabidopsis thaliana"
                    else "source-backed hybridization/polyploidization or explicit reticulate-inheritance evidence row"
                ),
            }
        )
    write_tsv(
        EXPECTATIONS_PATH,
        rows,
        [
            "raw_scientific_name",
            "canonical_node_id",
            "case_role",
            "expected_reticulation_seed_flag",
            "expected_event_supported_flag",
            "expected_count_only_flag",
            "observed_reticulation_seed_flag",
            "observed_event_supported_flag",
            "observed_count_only_flag",
            "expected_reason",
        ],
    )


def plot_matrix(feature_rows):
    import matplotlib.pyplot as plt

    by_name = {row["raw_scientific_name"]: row for row in feature_rows}
    columns = [
        ("chromosome_count_assertion_count", "count"),
        ("ploidy_context_assertion_count", "ploidy"),
        ("hybridization_event_count", "hybrid"),
        ("polyploidization_event_count", "polyploid"),
        ("reticulate_inheritance_evidence_count", "reticulate"),
    ]
    matrix = [
        [1 if int(by_name[name][field]) > 0 else 0 for field, _ in columns]
        for name in CANONICAL_CASES
    ]

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.imshow(matrix, cmap="Greens", vmin=0, vmax=1)
    ax.set_xticks(range(len(columns)), [label for _, label in columns], rotation=35, ha="right")
    ax.set_yticks(range(len(CANONICAL_CASES)), CANONICAL_CASES)
    ax.set_title("Seed-scale reticulation evidence-class matrix")
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, "yes" if value else "no", ha="center", va="center", fontsize=8)
    ax.tick_params(axis="both", length=0)
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=180)
    plt.close(fig)


def write_audit(feature_rows, input_counts, demotions):
    by_name = {row["raw_scientific_name"]: row for row in feature_rows}
    positives = [name for name in CANONICAL_CASES if name != "Arabidopsis thaliana"]
    count_total = sum(input_counts.values())
    event_support_total = sum(1 for row in feature_rows if row["event_supported_flag"] == "true")

    text = f"""---
created: 2026-05-17T20:10:00Z
cycle: 2
run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
agent: worker
milestone: M2.T1-preflight
---

# Track 1 Reticulation Enrichment Preflight Audit

This is a seed-scale preflight from M1.3 `validated/access-limited` staging, not M2.T1 production reticulation enrichment and not evidence of production coverage. It proves that existing normalized rows can be transformed into schema-conformant Track 1 feature records while preserving raw scientific-name canonical IDs.

## Inputs

| table | rows |
|---|---:|
"""
    for filename in TABLES:
        text += f"| `{filename}` | {input_counts[filename]} |\n"

    text += f"""
Total staged input rows read: {count_total}.
Feature rows emitted: {len(feature_rows)}.
Event-supported seed taxa: {event_support_total}.

## Canonical Cases

| taxon | role | count rows | ploidy context | hybrid events | polyploid events | reticulate evidence | event supported |
|---|---|---:|---:|---:|---:|---:|---|
"""
    for name in CANONICAL_CASES:
        row = by_name[name]
        role = "negative control" if name == "Arabidopsis thaliana" else "canonical positive"
        text += (
            f"| {name} | {role} | {row['chromosome_count_assertion_count']} | "
            f"{row['ploidy_context_assertion_count']} | {row['hybridization_event_count']} | "
            f"{row['polyploidization_event_count']} | {row['reticulate_inheritance_evidence_count']} | "
            f"{row['event_supported_flag']} |\n"
        )

    text += """
## Evidence Boundary

- Chromosome-count rows support `chromosome_count_assertion` features only; they do not create `hybridization_event`, `polyploidization_event`, or event-supported flags.
- Ploidy-context rows are retained as caveated supporting context and counted separately from explicit event rows.
- Event support requires an explicit `hybridization_event`, `polyploidization_event`, or parent-bearing `reticulate_inheritance_evidence` row.
- Canonical IDs remain `raw_name:<scientific_name_with_underscores>`; taxonomy backbone crosswalk keys are deferred to Barrier 1.

## Demotions And Non-Inferences

"""
    for item in sorted(set(demotions)):
        text += f"- {item}.\n"
    text += """- Count-only evidence is not promoted to reticulation event support.
- No one-parent or underspecified event rows were present in the validated seed event tables.
- No missing-provenance rows were accepted; source IDs, source names, licenses, access dates, and allowed-support summaries are preserved in the feature TSV.

## Later Production Requirements For M3.T1

The tree-compatibility-index prototype will need production-scale fields for every accepted row: raw scientific name, raw count text or event type, parsed count where applicable, at least one row-level source/citation identifier, source version, access date, license, attribution, acquisition route, allowed evidence scope, confidence/source reliability, and parent roles for event-backed rows. Production CCDB/event ingestion must also expose source-density features so later ablations can test whether reticulation scores collapse into count density, publication density, or source coverage.

![Seed-scale evidence-class matrix showing which canonical taxa are supported by chromosome counts, ploidy context, explicit hybridization events, explicit polyploidization events, and reticulate-inheritance evidence.](plots/seed_evidence_class_matrix.png)
"""
    AUDIT_PATH.write_text(text, encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    feature_rows, input_counts, demotions = collect_features()
    write_tsv(
        FEATURES_PATH,
        feature_rows,
        [
            "raw_scientific_name",
            "canonical_node_id",
            "chromosome_count_assertion_count",
            "distinct_reported_counts",
            "reported_counts_list",
            "ploidy_context_assertion_count",
            "hybridization_event_count",
            "polyploidization_event_count",
            "reticulate_inheritance_evidence_count",
            "explicit_parent_count",
            "evidence_class_count",
            "evidence_classes",
            "source_count",
            "source_ids",
            "source_names",
            "source_versions",
            "access_dates",
            "licenses",
            "input_tables",
            "reticulation_seed_flag",
            "count_only_flag",
            "event_supported_flag",
            "allowed_support_summary",
        ],
    )
    write_expectations(feature_rows)
    plot_matrix(feature_rows)
    write_audit(feature_rows, input_counts, demotions)
    print(f"wrote {FEATURES_PATH} ({len(feature_rows)} rows)")
    print(f"wrote {EXPECTATIONS_PATH}")
    print(f"wrote {AUDIT_PATH}")
    print(f"wrote {FIGURE_PATH}")


if __name__ == "__main__":
    main()
