#!/usr/bin/env python3
# created: 2026-05-18T21:05:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-track4-free-tier-bioclim-recovery
# agent: worker
# milestone: _plan/track4-free-tier-bioclim-recovery
"""Search local/open metadata for Track 4 candidate-level comparator readiness."""

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
OUT = DATA / "free_tier_validation_comparators.tsv"

CANDIDATES = DATA / "crop_substitution_candidates.tsv"
HELDOUT = DATA / "heldout_validation_seed.tsv"

USER_AGENT = "PhytoGraph Track4 open comparator search; contact local research run"
STRESS_TERMS = ("drought", "heat", "salinity", "climate", "stress", "adaptation", "resilience")
OUTPUT_COLUMNS = [
    "crop",
    "crop_key",
    "candidate_taxon",
    "candidate_key",
    "comparator_source",
    "relation_type",
    "climate_stress_context",
    "overlaps_training_evidence",
    "candidate_level_comparator",
    "same_genus",
    "validation_allowed",
    "caveat",
]


def read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def request_crossref(query: str, cache_name: str) -> dict[str, Any]:
    cache_path = CACHE / cache_name
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    params = urllib.parse.urlencode({"query.bibliographic": query, "rows": "3"})
    req = urllib.request.Request(
        f"https://api.crossref.org/works?{params}",
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - metadata probe should fail closed.
        data = {"error": str(exc), "message": {"items": []}}
    cache_path.write_text(json.dumps(data, indent=2, sort_keys=True))
    time.sleep(0.2)
    return data


def first_metadata_hit(crop: str, candidate: str) -> tuple[str, str, bool]:
    query = f"{crop} {candidate} wild relative drought climate"
    safe = (crop + "_" + candidate).replace(" ", "_").replace("/", "_")
    data = request_crossref(query, f"crossref_{safe}.json")
    items = (data.get("message") or {}).get("items") or []
    if not items:
        return "Crossref metadata search: no result", "", False
    item = items[0]
    title = " ".join(item.get("title") or []).strip()
    doi = item.get("DOI", "")
    source = f"Crossref metadata: {title}" + (f"; DOI {doi}" if doi else "")
    text = json.dumps(item).lower()
    stress = ", ".join(term for term in STRESS_TERMS if term in text)
    names_present = crop.lower() in text and candidate.lower() in text
    stress_present = bool(stress)
    return source, stress, bool(names_present and stress_present)


def same_genus(a: str, b: str) -> str:
    if not a or not b:
        return "not_applicable"
    return str(a.split()[0].lower() == b.split()[0].lower()).lower()


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    candidates = read_tsv(CANDIDATES)
    heldout = read_tsv(HELDOUT)
    rows: list[dict[str, str]] = []

    for _, row in candidates.iterrows():
        crop = row["crop_taxon"]
        candidate = row["candidate_wild_relative"]
        source, stress, metadata_candidate_stress = first_metadata_hit(crop, candidate)
        rows.append(
            {
                "crop": crop,
                "crop_key": row["crop_accepted_taxon_key"],
                "candidate_taxon": candidate,
                "candidate_key": row["candidate_wild_relative_key"],
                "comparator_source": source,
                "relation_type": "open_metadata_candidate_context",
                "climate_stress_context": stress,
                "overlaps_training_evidence": "true",
                "candidate_level_comparator": str(metadata_candidate_stress).lower(),
                "same_genus": same_genus(crop, candidate),
                "validation_allowed": "false",
                "caveat": "candidate is from M3.T4 training-derived row, so it is not disjoint held-out comparator evidence even if open metadata mentions stress context",
            }
        )

    for _, row in heldout.iterrows():
        rows.append(
            {
                "crop": row["crop_taxon"],
                "crop_key": row["accepted_taxon_key"],
                "candidate_taxon": "",
                "candidate_key": "",
                "comparator_source": row["cgiar_or_recommendation_source"],
                "relation_type": "crop_program_level_only",
                "climate_stress_context": row["region_of_practical_relevance"],
                "overlaps_training_evidence": str(row["overlaps_training_pedigree"]).lower(),
                "candidate_level_comparator": "false",
                "same_genus": "not_applicable",
                "validation_allowed": "false",
                "caveat": "held-out source names a crop program or crop context, not a candidate wild relative comparator row",
            }
        )

    pd.DataFrame(rows, columns=OUTPUT_COLUMNS).to_csv(OUT, sep="\t", index=False)
    allowed = sum(row["validation_allowed"] == "true" for row in rows)
    print(f"wrote {OUT} ({len(rows)} rows; validation_allowed={allowed})")


if __name__ == "__main__":
    main()
