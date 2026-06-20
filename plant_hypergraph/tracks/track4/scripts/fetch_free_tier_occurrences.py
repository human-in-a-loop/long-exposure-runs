#!/usr/bin/env python3
# created: 2026-05-18T21:05:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-track4-free-tier-bioclim-recovery
# agent: worker
# milestone: _plan/track4-free-tier-bioclim-recovery
"""Fetch bounded free-tier GBIF occurrence records for Track 4 crop/CWR taxa."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track4" / "data"
CACHE = DATA / "free_tier_occurrence_cache"
SUMMARY_OUT = DATA / "free_tier_occurrence_summary.tsv"

CWR = DATA / "crop_wild_relative_pairs.tsv"
CLIMATE = DATA / "climate_envelope_coverage.tsv"
HELDOUT = DATA / "heldout_validation_seed.tsv"

GBIF = "https://api.gbif.org/v1"
USER_AGENT = "PhytoGraph Track4 free-tier recovery; contact local research run"
LICENSE_COMPATIBLE = {
    "http://creativecommons.org/publicdomain/zero/1.0/legalcode",
    "http://creativecommons.org/licenses/by/4.0/legalcode",
    "http://creativecommons.org/licenses/by/3.0/legalcode",
}
SEVERE_ISSUES = {
    "ZERO_COORDINATE",
    "COORDINATE_INVALID",
    "COUNTRY_COORDINATE_MISMATCH",
    "COORDINATE_OUT_OF_RANGE",
    "PRESUMED_NEGATED_LONGITUDE",
    "PRESUMED_NEGATED_LATITUDE",
}
PANEL_SEEDS = [
    "Arachis hypogaea",
    "Arachis duranensis",
    "Arachis ipaensis",
    "Avena sativa",
    "Avena sterilis",
    "Aegilops speltoides",
    "Aegilops tauschii",
]


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def request_json(url: str, cache_path: Path) -> dict[str, Any]:
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    cache_path.write_text(json.dumps(data, indent=2, sort_keys=True))
    time.sleep(0.2)
    return data


def build_panel() -> pd.DataFrame:
    cwr = read_tsv(CWR)
    climate = read_tsv(CLIMATE)
    heldout = read_tsv(HELDOUT)
    rows: list[dict[str, str]] = []

    def add(name: str, role: str, accepted_key: str = "", crop_anchor: str = "") -> None:
        if not name:
            return
        rows.append(
            {
                "queried_name": name,
                "role": role,
                "accepted_key": accepted_key,
                "crop_anchor": crop_anchor,
            }
        )

    for name in PANEL_SEEDS:
        key = climate.loc[climate["taxon_canonical_name"].eq(name), "accepted_taxon_key"]
        add(name, "seed_panel", key.iloc[0] if not key.empty else "")

    for _, row in cwr.iterrows():
        if row["crop_taxon"] in PANEL_SEEDS:
            add(row["crop_taxon"], "crop_anchor", row["crop_accepted_taxon_key"], row["crop_taxon"])
        if row["wild_ancestor_name"] in PANEL_SEEDS:
            add(
                row["wild_ancestor_name"],
                "wild_relative",
                row["wild_ancestor_accepted_key"],
                row["crop_taxon"],
            )

    for _, row in heldout.head(15).iterrows():
        add(row["crop_taxon"], "heldout_crop", row["accepted_taxon_key"], row["crop_taxon"])

    panel = pd.DataFrame(rows).drop_duplicates(subset=["queried_name", "role", "crop_anchor"])
    return panel.sort_values(["queried_name", "role", "crop_anchor"])


def gbif_match(name: str) -> dict[str, Any]:
    q = urllib.parse.urlencode({"name": name, "kingdom": "Plantae"})
    safe = name.replace(" ", "_").replace("/", "_")
    return request_json(f"{GBIF}/species/match?{q}", CACHE / f"match_{safe}.json")


def gbif_occurrences(taxon_key: str, name: str) -> dict[str, Any]:
    params = {
        "taxonKey": taxon_key,
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
        "limit": "300",
        "offset": "0",
    }
    q = urllib.parse.urlencode(params)
    safe = name.replace(" ", "_").replace("/", "_")
    return request_json(f"{GBIF}/occurrence/search?{q}", CACHE / f"occurrence_{safe}_{taxon_key}.json")


def source_label(record: dict[str, Any]) -> str:
    dataset = record.get("datasetName") or record.get("datasetTitle") or record.get("datasetKey") or "unknown_dataset"
    publisher = record.get("publishingOrgKey") or record.get("institutionCode") or ""
    if "iNaturalist" in str(dataset):
        return "GBIF_iNaturalist_mediated"
    return f"GBIF:{dataset}" if not publisher else f"GBIF:{dataset}:{publisher}"


def is_cultivated(record: dict[str, Any]) -> bool:
    fields = [
        record.get("establishmentMeans"),
        record.get("degreeOfEstablishment"),
        record.get("pathway"),
        record.get("occurrenceRemarks"),
        record.get("habitat"),
    ]
    text = " ".join(str(v).lower() for v in fields if v)
    return any(term in text for term in ["cultivat", "garden", "botanic", "planted", "managed"])


def reject_reason(record: dict[str, Any], wild_role: bool) -> str:
    if record.get("decimalLatitude") in (None, "", 0) or record.get("decimalLongitude") in (None, "", 0):
        return "missing_or_zero_coordinate"
    if record.get("license") not in LICENSE_COMPATIBLE:
        return "license_not_cc0_or_cc_by"
    uncertainty = record.get("coordinateUncertaintyInMeters")
    if uncertainty not in (None, ""):
        try:
            if float(uncertainty) > 50000:
                return "coordinate_uncertainty_over_50km"
        except (TypeError, ValueError):
            pass
    issues = set(record.get("issues") or [])
    if issues & SEVERE_ISSUES:
        return "severe_geospatial_issue"
    if wild_role and is_cultivated(record):
        return "wild_relative_record_cultivated_or_managed"
    return ""


def summarize_records(panel_row: pd.Series, match: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    wild_role = panel_row["role"] == "wild_relative"
    total = len(records)
    coord = sum(1 for r in records if r.get("decimalLatitude") not in (None, "") and r.get("decimalLongitude") not in (None, ""))
    license_ok = sum(1 for r in records if r.get("license") in LICENSE_COMPATIBLE)
    cultivated = sum(1 for r in records if is_cultivated(r))
    reasons: list[str] = []
    post_filter = 0
    wild_candidate = 0
    source_counts: dict[str, int] = {}
    for record in records:
        reason = reject_reason(record, wild_role)
        if reason:
            reasons.append(reason)
            continue
        post_filter += 1
        if not is_cultivated(record):
            wild_candidate += 1
        source_counts[source_label(record)] = source_counts.get(source_label(record), 0) + 1
    dominant = max(set(reasons), key=reasons.count) if reasons else ""
    source = max(source_counts, key=source_counts.get) if source_counts else "none_after_filter"
    return {
        "queried_name": panel_row["queried_name"],
        "accepted_key": panel_row["accepted_key"],
        "gbif_usage_key": str(match.get("usageKey", "")),
        "gbif_scientific_name": match.get("scientificName", ""),
        "role": panel_row["role"],
        "crop_anchor": panel_row["crop_anchor"],
        "source": source,
        "total_records": total,
        "coordinate_records": coord,
        "license_compatible_records": license_ok,
        "post_filter_records": post_filter,
        "cultivated_flagged_records": cultivated,
        "wild_candidate_records": wild_candidate,
        "dominant_rejection_reason": dominant,
    }


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    panel = build_panel()
    summaries: list[dict[str, Any]] = []
    for _, panel_row in panel.iterrows():
        match = gbif_match(panel_row["queried_name"])
        usage_key = match.get("usageKey")
        records: list[dict[str, Any]] = []
        if usage_key:
            data = gbif_occurrences(str(usage_key), panel_row["queried_name"])
            records = list(data.get("results") or [])
        summaries.append(summarize_records(panel_row, match, records))
    pd.DataFrame(summaries).to_csv(SUMMARY_OUT, sep="\t", index=False)
    print(f"wrote {SUMMARY_OUT} ({len(summaries)} taxa)")


if __name__ == "__main__":
    main()
