# created: 2026-05-18T00:00:00+00:00
# cycle: 34
# run_id: run-phytograph-taxonomy-results-site
# agent: worker
# milestone: _plan/taxonomy-results-site
"""Validate the public PhytoGraph taxonomy results site."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "taxonomy_results_site"
QA_REPORT = ROOT / "reports/taxonomy_results_site_qa.md"

REQUIRED_FILES = [
    SITE / "index.html",
    SITE / "assets/styles.css",
    SITE / "assets/app.js",
    SITE / "data/site_summary.json",
    SITE / "README.md",
    SITE / "PROVENANCE.md",
    QA_REPORT,
]

REQUIRED_FIGURES = [
    "campaign_hypergraph_map.svg",
    "track_status_overview.svg",
    "evidence_recovered_vs_rejected.svg",
    "accepted_key_joins.svg",
    "source_bias_summary.svg",
    "occurrence_bioclim_readiness.svg",
    "validation_outcomes.svg",
    "future_evidence_predicates.svg",
]

REQUIRED_ROUTES = [
    "Start Here",
    "Choose a Track",
    "What Was Found",
    "Why Claims Were Not Promoted",
    "Evidence Explorer",
    "Methods for Taxonomists",
    "Limitations",
    "What Evidence Would Change the Conclusion",
]

BANNED_PUBLIC_TERMS = [
    r"\blong-exposure\b",
    r"\bagent(s)?\b",
    r"\bcycle(s)?\b",
    r"\bprompt(s)?\b",
    r"\bin-cycle\b",
    r"\bmanager(s)?\b",
    r"\btelemetry\b",
    r"\bfan-out\b",
    r"\barchitecture\b",
    r"\bCodex\b",
    r"\bClaude\b",
    r"\bcompaction\b",
    r"\brun(s)?\b",
    r"\bautonomous\b",
    "/" + "home/",
    r"\bworkspace\b",
    r"\b" + "jer" + "emy" + r"\b",
]


def public_text_files() -> list[Path]:
    files = []
    for path in SITE.rglob("*"):
        if path.suffix.lower() in {".html", ".css", ".js", ".json", ".md", ".svg"}:
            files.append(path)
    return files


def test_required_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    assert not missing, f"missing required files: {missing}"
    for figure in REQUIRED_FIGURES:
        assert (SITE / "assets/figures" / figure).exists(), figure
    for idx in range(1, 7):
        assert (SITE / "data/evidence_tables" / f"track{idx}.json").exists()


def test_routes_and_assets_are_referenced() -> None:
    html = (SITE / "index.html").read_text(encoding="utf-8")
    for route in REQUIRED_ROUTES:
        assert route in html
    for figure in REQUIRED_FIGURES:
        assert f"assets/figures/{figure}" in html or figure in html
    for href in re.findall(r'(?:src|href)="([^"]+)"', html):
        if href.startswith("#") or href.startswith("http") or href.startswith("data:"):
            continue
        assert (SITE / href).exists(), href


def test_public_language_boundary() -> None:
    pattern = re.compile("|".join(BANNED_PUBLIC_TERMS), re.IGNORECASE)
    failures = []
    for path in public_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = pattern.search(text)
        if match:
            failures.append(f"{path.relative_to(ROOT)}: {match.group(0)}")
    assert not failures, "banned public-facing term found: " + "; ".join(failures)


def test_summary_tracks_and_statuses() -> None:
    summary = json.loads((SITE / "data/site_summary.json").read_text(encoding="utf-8"))
    assert summary["substrate"]["taxa_indexed"] == 60000
    assert len(summary["tracks"]) == 6
    statuses = {track["status_code"] for track in summary["tracks"]}
    assert "sidecar_readiness_uncontrolled" in statuses
    assert "H2_remains_not_supported_or_data_limited" in statuses
    assert "confound_limited" in statuses
    assert "still_data_limited" in statuses
    assert "H5_remains_source_biased" in statuses
    assert "environment_limited_untested" in statuses


def test_cross_track_tables_remain_unpromoted() -> None:
    for name in ["prediction_ledger.tsv", "speculation_ledger.tsv"]:
        path = ROOT / name
        assert path.exists(), name
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1, f"{name} should remain header-only"
