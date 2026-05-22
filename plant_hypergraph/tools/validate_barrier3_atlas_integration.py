#!/usr/bin/env python3
# Header metadata:
#   created: 2026-05-18T08:00:00+00:00
#   cycle: 11
#   run_id: run-phytograph-cycle11-barrier3-readiness
#   agent: worker
#   milestone: _plan/barrier3-readiness-package
"""Validate Barrier 3 instrument-to-Atlas readiness.

This script audits the Atlas as an integration surface only. It does not
validate biological claims, run Wave 4 experiments, or write master ledgers.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "botanical_atlas_site"
PAGES = SITE / "pages"

TRACK_SOURCES = {
    1: ROOT / "tracks/track1/outputs/tci_per_taxon.tsv",
    2: ROOT / "tracks/track2/data/ghost_partner_predictions.tsv",
    3: ROOT / "tracks/track3/data/convergence_predictions.tsv",
    4: ROOT / "tracks/track4/data/crop_substitution_candidates.tsv",
    5: ROOT / "tracks/track5/data/phytochemistry_predictions.tsv",
    6: ROOT / "tracks/track6/data/probe_results.tsv",
}

TRACK_NAMES = {
    1: "Reticulation Atlas",
    2: "Ghost Hyperedges",
    3: "Convergence Pressure",
    4: "Domestication Hypergraph",
    5: "Chemodiversity Predictor",
    6: "Foundation-Model Probe",
}

OUTPUT_JSON = ROOT / "data/barrier3_atlas_instrument_contract.json"
OUTPUT_TSV = ROOT / "data/barrier3_atlas_instrument_contract.tsv"
OUTPUT_REPORT = ROOT / "reports/barrier3_atlas_instrument_readiness.md"
OUTPUT_FIG = ROOT / "reports/barrier3_atlas_instrument_coverage.png"

DISALLOWED_STATUS = {"validated"}
OVERCLAIM_TERMS = {
    1: ("validated reticulation", "established reticulation", "new hybridization"),
    2: ("established anachronism", "validated anachronism"),
    3: ("validated convergence", "established convergence"),
    4: ("validated crop-substitution recommendation", "climate suitability"),
    5: ("validated bioactivity", "established bioactivity", "safe to consume"),
    6: ("publishable model-performance evaluation", "leaderboard", "vendor ranking"),
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def read_tsv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def source_row_count(track: int, path: Path) -> tuple[int, list[str]]:
    df = read_tsv(path)
    if df.empty and not path.exists():
        return 0, []
    classes: list[str] = []
    for col in ("row_class", "status", "prediction_status", "result_status", "candidate_status", "confidence"):
        if col in df.columns:
            classes.extend(str(v) for v in df[col].dropna().unique() if str(v))
    return len(df), sorted(set(classes))


def load_pages(limit: int | None = None) -> list[dict[str, Any]]:
    paths = sorted(PAGES.glob("*.json"))
    if limit is not None:
        paths = paths[:limit]
    return [read_json(p) for p in paths]


def row_has_provenance(row: dict[str, Any]) -> bool:
    return bool(row.get("source_id") or row.get("source_record_id") or row.get("provenance_pointer") or row.get("license"))


def row_has_caveat(row: dict[str, Any]) -> bool:
    return bool(row.get("caveats") or row.get("allowed_evidence_scope"))


def track6_mode() -> str:
    path = ROOT / "tracks/track6/data/local_model_availability.json"
    if not path.exists():
        return "benchmark_only_data_limited"
    data = read_json(path)
    if data.get("local_open_model_runnable"):
        return "local_model_results_available"
    return data.get("runner_mode") or "benchmark_only_data_limited"


def collect_page_contract(pages: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for track in range(1, 7):
        result[track] = {
            "projected_rows": 0,
            "taxa": set(),
            "states": Counter(),
            "row_statuses": set(),
            "provenance_ok": True,
            "caveat_ok": True,
            "prediction_boundary_ok": True,
            "missing_indicator_ok": False,
            "instrument_pending_seen": False,
            "instrument_mode_values": set(),
            "overclaim_hits": [],
            "validated_rows": [],
            "source_artifact_refs": set(),
        }

    for page in pages:
        taxon_key = page.get("accepted_taxon_key")
        tracks = page.get("tracks", {})
        for track in range(1, 7):
            sec = tracks.get(str(track)) or tracks.get(track)
            if not sec:
                result[track]["prediction_boundary_ok"] = False
                continue
            result[track]["states"][sec.get("state", "")] += 1
            result[track]["instrument_pending_seen"] |= bool(sec.get("instrument_pending"))
            result[track]["instrument_mode_values"].add(sec.get("instrument_mode", ""))
            if sec.get("data_limited_reason") or sec.get("state") == "data-limited":
                result[track]["missing_indicator_ok"] = True

            for band in ("observed", "enriched", "predicted"):
                for row in sec.get(band, []):
                    if band == "predicted":
                        result[track]["projected_rows"] += 1
                        result[track]["taxa"].add(taxon_key)
                    status = str(row.get("status") or "").strip()
                    if status:
                        result[track]["row_statuses"].add(status)
                    if status.lower() in {"data_limited", "data-limited", "pending_data_limited"}:
                        result[track]["missing_indicator_ok"] = True
                    if status.lower() in DISALLOWED_STATUS:
                        result[track]["validated_rows"].append(row.get("edge_id"))
                    if not row_has_provenance(row):
                        result[track]["provenance_ok"] = False
                    if not row_has_caveat(row):
                        result[track]["caveat_ok"] = False
                    if band == "predicted" and not row.get("inferred_flag"):
                        result[track]["prediction_boundary_ok"] = False
                    if band in {"observed", "enriched"} and row.get("inferred_flag"):
                        result[track]["prediction_boundary_ok"] = False
                    if row.get("track_output_path"):
                        result[track]["source_artifact_refs"].add(row["track_output_path"])
                    text = " ".join(str(row.get(k) or "") for k in (
                        "prediction_statement", "caveats", "allowed_evidence_scope", "expected_validation_source"
                    )).lower()
                    for term in OVERCLAIM_TERMS[track]:
                        if term.lower() in text:
                            # Keep negated boundary phrases out of the blocker bucket.
                            if f"not a {term.lower()}" not in text and f"not {term.lower()}" not in text:
                                result[track]["overclaim_hits"].append(f"{row.get('edge_id')}::{term}")
    return result


def expected_projected_rows(track: int, source_rows: int, coverage: dict[str, Any]) -> tuple[int | None, str]:
    actual = int(coverage.get("instrument_prediction_rows_by_track", {}).get(str(track), 0))
    if track == 1:
        return source_rows, "full accepted-key TCI projection expected"
    if track == 3:
        return actual, "partial support-list-limited page projection expected from truncated support lists"
    if track == 4:
        return actual, "candidate rows intentionally rendered on crop and wild-relative endpoints"
    if track == 6:
        return actual, "offline probe results intentionally filtered to accepted-key joined question rows"
    return actual, "accepted-key resolved Atlas projection expected"


def build_contract() -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    coverage = read_json(SITE / "coverage_summary.json")
    build_log = read_json(SITE / "build_log.json")
    search_index = read_json(SITE / "search_index.json")
    pages = load_pages()
    page_contract = collect_page_contract(pages)

    master_prediction_lines = (ROOT / "prediction_ledger.tsv").read_text().splitlines()
    master_speculation_lines = (ROOT / "speculation_ledger.tsv").read_text().splitlines()
    master_ledgers_header_only = len(master_prediction_lines) == 1 and len(master_speculation_lines) == 1

    rows: list[dict[str, Any]] = []
    hard_errors: list[str] = []
    for track, source in TRACK_SOURCES.items():
        source_rows, source_classes = source_row_count(track, source)
        page_info = page_contract[track]
        expected_rows, expectation_note = expected_projected_rows(track, source_rows, coverage)
        atlas_rows = page_info["projected_rows"]
        taxa_count = len(page_info["taxa"])
        blocking = []
        if not source.exists():
            blocking.append("source_artifact_missing")
        if expected_rows is not None and atlas_rows != expected_rows:
            blocking.append(f"projected_rows_mismatch_expected_{expected_rows}_actual_{atlas_rows}")
        if page_info["instrument_pending_seen"]:
            blocking.append("stale_instrument_pending_placeholder_seen")
        if "prediction_adapter" not in page_info["instrument_mode_values"]:
            blocking.append("prediction_adapter_mode_absent")
        if not page_info["provenance_ok"]:
            blocking.append("missing_provenance")
        if not page_info["caveat_ok"]:
            blocking.append("missing_caveat_or_allowed_scope")
        if not page_info["prediction_boundary_ok"]:
            blocking.append("prediction_vs_evidence_boundary_failure")
        if not page_info["missing_indicator_ok"]:
            blocking.append("missing_data_indicator_absent")
        if page_info["validated_rows"]:
            blocking.append("unsupported_validated_status")
        if page_info["overclaim_hits"]:
            blocking.append("possible_overclaim_language")
        if track == 6 and track6_mode() == "benchmark_only_data_limited":
            # Explicitly nonblocking: Barrier 3 checks queryability, not model-runtime publication quality.
            pass

        status = "ready" if not blocking else "blocked"
        if track in {3, 6} and status == "ready":
            status = "ready_with_nonblocking_warning"
        if track == 4 and status == "ready":
            status = "ready_data_limited"
        if track == 5 and status == "ready":
            status = "ready_with_source_dominance_warning"

        row = {
            "track": f"Track {track}",
            "track_name": TRACK_NAMES[track],
            "source_artifact": str(source.relative_to(ROOT)),
            "source_rows": source_rows,
            "atlas_projected_rows": atlas_rows,
            "taxon_pages_with_rows": taxa_count,
            "row_class_values": ";".join(sorted(set(source_classes) | page_info["row_statuses"])),
            "provenance_field_present": str(page_info["provenance_ok"]),
            "caveat_field_present": str(page_info["caveat_ok"]),
            "prediction_vs_evidence_field_present": str(page_info["prediction_boundary_ok"]),
            "missing_data_indicator_present": str(page_info["missing_indicator_ok"]),
            "barrier3_status": status,
            "blocking_issue": ";".join(blocking),
            "expectation_note": expectation_note,
            "source_artifact_refs_seen": ";".join(sorted(page_info["source_artifact_refs"])),
        }
        rows.append(row)
        if blocking:
            hard_errors.extend(f"Track {track}: {b}" for b in blocking)

    global_checks = {
        "pages_written": build_log.get("pages_written"),
        "search_index_rows": len(search_index),
        "coverage_total_pages_written": coverage.get("total_pages_written"),
        "all_six_track_adapters_present": len(rows) == 6 and all(r["barrier3_status"] != "blocked" for r in rows),
        "master_ledgers_header_only": master_ledgers_header_only,
        "track6_runner_mode": track6_mode(),
        "track3_projection_note": "support-list-limited: supporting_hyperedges lists are truncated in convergence_predictions.tsv; Atlas projection is queryable but not exhaustive.",
        "barrier3_readiness": "ready_with_nonblocking_warnings" if not hard_errors else "blocked",
    }
    if not master_ledgers_header_only:
        hard_errors.append("master_ledgers_not_header_only")
        global_checks["barrier3_readiness"] = "blocked"

    contract = {
        "schema": "phytograph.barrier3_atlas_instrument_contract.v1",
        "generated_at": "2026-05-18T08:00:00+00:00",
        "global_checks": global_checks,
        "tracks": rows,
    }
    return contract, rows, 0 if not hard_errors else 1


def write_outputs(contract: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(contract, indent=2))

    fieldnames = [
        "track", "source_artifact", "source_rows", "atlas_projected_rows",
        "taxon_pages_with_rows", "row_class_values", "provenance_field_present",
        "caveat_field_present", "prediction_vs_evidence_field_present",
        "missing_data_indicator_present", "barrier3_status", "blocking_issue",
    ]
    with OUTPUT_TSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    write_figure(rows)
    write_report(contract, rows)


def write_figure(rows: list[dict[str, Any]]) -> None:
    labels = [r["track"].replace("Track ", "T") for r in rows]
    source = [int(r["source_rows"]) for r in rows]
    projected = [int(r["atlas_projected_rows"]) for r in rows]
    taxa = [int(r["taxon_pages_with_rows"]) for r in rows]
    x = range(len(rows))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([i - width for i in x], source, width=width, label="source rows", color="#4c78a8")
    ax.bar(list(x), projected, width=width, label="projected rows", color="#f58518")
    ax.bar([i + width for i in x], taxa, width=width, label="taxon pages", color="#54a24b")
    ax.set_yscale("symlog", linthresh=10)
    ax.set_xticks(list(x), labels)
    ax.set_ylabel("Rows / pages (symlog)")
    ax.set_title("Barrier 3 Atlas Instrument Projection Coverage")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.text(
        0.01, 0.01,
        "Per-track Atlas projection coverage, showing source rows, projected rows, "
        "and taxon pages carrying queryable evidence/prediction sections.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUTPUT_FIG, dpi=180)
    plt.close(fig)


def write_report(contract: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    gc = contract["global_checks"]
    verdict = gc["barrier3_readiness"]
    lines = [
        "---",
        "created: 2026-05-18T08:00:00+00:00",
        "cycle: 11",
        "run_id: run-phytograph-cycle11-barrier3-readiness",
        "agent: worker",
        "milestone: _plan/barrier3-readiness-package",
        "---",
        "",
        "# Barrier 3 Atlas Instrument Readiness",
        "",
        f"Verdict: **{verdict}**.",
        "",
        "This package audits whether Wave 3 instruments are queryable from the Botanical Atlas. It does not run Wave 4 validation, does not promote biological predictions, and does not write to the master prediction or speculation ledgers.",
        "",
        f"Atlas rebuild/accounting: {gc['pages_written']} pages, {gc['search_index_rows']} search rows, master ledgers header-only = {gc['master_ledgers_header_only']}.",
        "",
        "![Per-track Atlas projection coverage, showing source rows, projected rows, and taxon pages carrying queryable evidence/prediction sections.](barrier3_atlas_instrument_coverage.png)",
        "",
        "| Track | Instrument status | Atlas queryability | Caveat quality | Evidence/prediction boundary | Remaining Wave 4-only work |",
        "|---|---|---|---|---|---|",
    ]
    wave4 = {
        1: "Canonical polyploid/hybrid recovery after accepted-key coverage repair.",
        2: "Held-out Janzen-Martin recovery and living-megafauna contrast.",
        3: "Independent trait-list validation and source/family-size ablations; page projection is support-list-limited.",
        4: "Expert crop-wild-relative comparison after climate vectors are computable.",
        5: "Temporal phytochemistry holdout and source-dominance ablations.",
        6: "Free/open/local model execution if available; current runner is benchmark-only/data-limited.",
    }
    for r in rows:
        track_num = int(r["track"].split()[1])
        query = f"{r['atlas_projected_rows']} rows on {r['taxon_pages_with_rows']} pages"
        caveat = "present" if r["caveat_field_present"] == "True" else "missing"
        boundary = "preserved" if r["prediction_vs_evidence_field_present"] == "True" else "failed"
        lines.append(
            f"| {r['track']} {r['track_name']} | {r['barrier3_status']} | {query} | {caveat} | {boundary} | {wave4[track_num]} |"
        )
    lines.extend([
        "",
        "## Contract Notes",
        "",
        "- Track 1 TCI rows are data-limited instrument outputs over all accepted-key pages, not validated reticulation claims.",
        "- Track 3 convergence rows are pending trait-level priors; page linkage is explicitly partial because long support lists are truncated in `convergence_predictions.tsv`.",
        "- Track 4 remains data-limited because observed bioclim vectors are absent; Atlas rows are candidate rankings, not climate-suitability recommendations.",
        "- Track 5 remains source-dominated and Duke-sensitive; Atlas rows are screening priors, not detections, bioactivity claims, or safety claims.",
        f"- Track 6 runner mode is `{gc['track6_runner_mode']}`; it is benchmark-only/data-limited, not a publishable model-performance evaluation.",
        "- `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only.",
    ])
    OUTPUT_REPORT.write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true", help="validate without writing outputs")
    args = ap.parse_args(argv)
    contract, rows, rc = build_contract()
    if not args.no_write:
        write_outputs(contract, rows)
    if rc == 0:
        print(
            "PASS: Barrier 3 Atlas instrument contract "
            f"({contract['global_checks']['pages_written']} pages, 6 tracks)"
        )
    else:
        print("FAIL: Barrier 3 Atlas instrument contract", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
