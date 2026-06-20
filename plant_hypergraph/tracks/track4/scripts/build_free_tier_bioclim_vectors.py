#!/usr/bin/env python3
# created: 2026-05-18T21:05:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-track4-free-tier-bioclim-recovery
# agent: worker
# milestone: _plan/track4-free-tier-bioclim-recovery
"""Build Track 4 free-tier BIOCLIM vector feasibility rows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track4" / "data"
CACHE = DATA / "free_tier_occurrence_cache"
SUMMARY = DATA / "free_tier_occurrence_summary.tsv"
OUT = DATA / "free_tier_bioclim_vectors.tsv"

CLIMATE_PATTERNS = ("*worldclim*.tif", "*WorldClim*.tif", "*chelsa*.tif", "*CHELSA*.tif", "*.bil")
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
OUTPUT_COLUMNS = [
    "taxon",
    "accepted_key",
    "role",
    "crop_anchor",
    "source",
    "n_coordinates_used",
    "coordinate_filter_version",
    "bioclim_variable",
    "mean",
    "median",
    "min",
    "max",
    "aggregation_method",
    "raster_or_climate_source",
    "license_access_note",
    "caveat",
    "extraction_status",
]


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def local_climate_files() -> list[Path]:
    files: list[Path] = []
    for pattern in CLIMATE_PATTERNS:
        files.extend(ROOT.glob(pattern))
        files.extend((ROOT / "data").glob(f"**/{pattern}") if (ROOT / "data").exists() else [])
        files.extend((ROOT / "tracks").glob(f"**/{pattern}") if (ROOT / "tracks").exists() else [])
    return sorted(set(p for p in files if p.is_file()))


def coordinates_for_taxon(taxon: str, usage_key: str, wild_role: bool) -> int:
    cache_file = CACHE / f"occurrence_{taxon.replace(' ', '_')}_{usage_key}.json"
    if not cache_file.exists():
        return 0
    data: dict[str, Any] = json.loads(cache_file.read_text())
    seen: set[tuple[float, float]] = set()
    for record in data.get("results") or []:
        if record.get("license") not in LICENSE_COMPATIBLE:
            continue
        if set(record.get("issues") or []) & SEVERE_ISSUES:
            continue
        lat = record.get("decimalLatitude")
        lon = record.get("decimalLongitude")
        if lat in (None, "", 0) or lon in (None, "", 0):
            continue
        try:
            lat_f = round(float(lat), 3)
            lon_f = round(float(lon), 3)
        except (TypeError, ValueError):
            continue
        if abs(lat_f) < 0.001 and abs(lon_f) < 0.001:
            continue
        uncertainty = record.get("coordinateUncertaintyInMeters")
        if uncertainty not in (None, ""):
            try:
                if float(uncertainty) > 50000:
                    continue
            except (TypeError, ValueError):
                pass
        if wild_role:
            text = " ".join(
                str(record.get(k, "")).lower()
                for k in ["establishmentMeans", "degreeOfEstablishment", "pathway", "occurrenceRemarks", "habitat"]
            )
            if any(term in text for term in ["cultivat", "garden", "botanic", "planted", "managed"]):
                continue
        seen.add((lat_f, lon_f))
    return len(seen)


def main() -> None:
    summary = read_tsv(SUMMARY)
    climate_files = local_climate_files()
    rows: list[dict[str, str | int]] = []
    for _, row in summary.iterrows():
        n_coords = coordinates_for_taxon(
            row["queried_name"],
            row["gbif_usage_key"],
            row["role"] == "wild_relative",
        )
        if climate_files:
            caveat = "local raster detected but extraction is not implemented in this branch without an audited raster manifest"
            extraction_status = "not_computed_no_audited_raster_manifest"
            raster_source = ";".join(str(p.relative_to(ROOT)) for p in climate_files[:5])
        else:
            caveat = "post-filter occurrence coordinates may exist, but no local WorldClim/CHELSA raster or sampled climate file was found; climate mismatch remains undefined"
            extraction_status = "not_computed_no_local_raster_or_runtime"
            raster_source = "none_found_in_workspace"
        rows.append(
            {
                "taxon": row["queried_name"],
                "accepted_key": row["accepted_key"],
                "role": row["role"],
                "crop_anchor": row["crop_anchor"],
                "source": row["source"],
                "n_coordinates_used": n_coords,
                "coordinate_filter_version": "gbif_cc0_ccby_uncertainty50km_no_severe_geospatial_issue_v1",
                "bioclim_variable": "none_computed",
                "mean": "",
                "median": "",
                "min": "",
                "max": "",
                "aggregation_method": "not_computed",
                "raster_or_climate_source": raster_source,
                "license_access_note": "GBIF occurrence metadata cached locally with dataset keys/licenses; climate rasters not redistributed",
                "caveat": caveat,
                "extraction_status": extraction_status,
            }
        )
    pd.DataFrame(rows, columns=OUTPUT_COLUMNS).to_csv(OUT, sep="\t", index=False)
    numeric = sum(bool(str(row["mean"]).strip()) for row in rows)
    print(f"wrote {OUT} ({len(rows)} rows; numeric_bioclim_vectors={numeric})")


if __name__ == "__main__":
    main()
