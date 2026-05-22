# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone7
# agent: worker
# milestone: M1.9
"""Fetch plant taxon identifier crosswalk rows from Wikidata SPARQL."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "PhytoGraph-M1.9-WikidataCommons/0.1 (metadata-only; contact: local-research)"
DEFAULT_LIMIT = 5000
DEFAULT_SLEEP_SECONDS = 1.2
DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_SCOPE_PROPERTIES = ["P5037", "P961", "P960", "P1391"]

QUERY_TEMPLATE = """
SELECT ?taxon ?taxonName ?scopeIdentifier ?commonsCategory WHERE {
  ?taxon wdt:__SCOPE_PROP__ ?scopeIdentifier .
  ?taxon wdt:P225 ?taxonName .
  OPTIONAL { ?taxon wdt:P373 ?commonsCategory . }
}
ORDER BY ?taxon
LIMIT __LIMIT__
OFFSET __OFFSET__
"""

FIELDNAMES = [
    "wikidata_qid",
    "wikidata_url",
    "taxon_name",
    "ncbi_taxonomy_id",
    "tropicos_id",
    "ipni_plant_id",
    "ipni_publication_id",
    "powo_id",
    "eol_id",
    "commons_category",
    "retrieved_at",
]

PROPERTY_TO_FIELD = {
    "P685": "ncbi_taxonomy_id",
    "P960": "tropicos_id",
    "P961": "ipni_plant_id",
    "P1391": "ipni_publication_id",
    "P5037": "powo_id",
    "P830": "eol_id",
}


def qid_from_uri(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def binding_value(binding: dict, key: str) -> str:
    return binding.get(key, {}).get("value", "")


def read_existing_qids(path: pathlib.Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open("r", newline="", encoding="utf-8") as handle:
        return {row["wikidata_qid"] for row in csv.DictReader(handle, delimiter="\t") if row.get("wikidata_qid")}


def fetch_batch(scope_property: str, offset: int, limit: int, retries: int) -> list[dict]:
    query = (
        QUERY_TEMPLATE.replace("__SCOPE_PROP__", scope_property)
        .replace("__LIMIT__", str(limit))
        .replace("__OFFSET__", str(offset))
    )
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    params = {"query": query, "format": "json"}
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            url = f"{SPARQL_ENDPOINT}?{urlencode(params)}"
            request = Request(url, headers=headers)
            with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))["results"]["bindings"]
        except Exception as exc:  # pragma: no cover - exercised by live endpoint
            last_error = exc
            time.sleep(min(30, 2**attempt))
    raise RuntimeError(f"SPARQL batch failed at offset={offset}: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="substrate/staging/wikidata_commons/data/wikidata_taxon_crosswalk.tsv")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--max-rows", type=int, default=30000)
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS)
    parser.add_argument("--scope-properties", default=",".join(DEFAULT_SCOPE_PROPERTIES))
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_existing_qids(out_path)
    mode = "a" if out_path.exists() else "w"
    wrote = 0
    seen = set(existing)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    scope_properties = [p.strip() for p in args.scope_properties.split(",") if p.strip()]

    with out_path.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=FIELDNAMES)
        if mode == "w":
            writer.writeheader()
        for scope_property in scope_properties:
            offset = 0
            while len(seen) < args.max_rows:
                batch = fetch_batch(scope_property=scope_property, offset=offset, limit=args.limit, retries=args.retries)
                if not batch:
                    break
                for binding in batch:
                    qid = qid_from_uri(binding_value(binding, "taxon"))
                    if qid in seen:
                        continue
                    identifier_field = PROPERTY_TO_FIELD[scope_property]
                    row = {
                        "wikidata_qid": qid,
                        "wikidata_url": binding_value(binding, "taxon"),
                        "taxon_name": binding_value(binding, "taxonName"),
                        "ncbi_taxonomy_id": "",
                        "tropicos_id": "",
                        "ipni_plant_id": "",
                        "ipni_publication_id": "",
                        "powo_id": "",
                        "eol_id": "",
                        "commons_category": binding_value(binding, "commonsCategory"),
                        "retrieved_at": retrieved_at,
                    }
                    row[identifier_field] = binding_value(binding, "scopeIdentifier")
                    writer.writerow(
                        row
                    )
                    seen.add(qid)
                    wrote += 1
                offset += args.limit
                handle.flush()
                if len(batch) < args.limit:
                    break
                time.sleep(args.sleep)
            if len(seen) >= args.max_rows:
                break
    print(f"wrote={wrote} total={len(seen)} out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
