---
created: 2026-05-17T18:00:00Z
cycle: 2
run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone7
agent: worker
milestone: M1.9
---

# M1.9 Wikidata / Wikimedia Commons Ingest Audit

## Status

Crosswalk status: data-limited.
Media status: data-limited.

This branch produced a reproducible staging package and live endpoint sample, but did not reach the M1.9 coverage floors in the available run. Wikidata SPARQL returned 15,269 unique plant-scoped taxon crosswalk rows before repeated HTTP 502/504 failures on deeper pagination; Wikimedia Commons returned 160 media metadata rows before rate limiting and timeout constraints prevented reaching the 10,000-taxon media target.

## Artifacts

| Path | Purpose |
|---|---|
| `scripts/fetch_wikidata_taxon_crosswalk.py` | Paginated Wikidata SPARQL fetcher for plant-scoped identifier crosswalk rows. |
| `scripts/fetch_commons_media_metadata.py` | Commons category metadata fetcher; stores metadata URLs and license fields only. |
| `scripts/build_image_evidence_edges.py` | Converts Commons media rows into schema v1.0 `image_evidence` staging rows. |
| `tests/test_wikidata_commons_schema.py` | Validates required columns, no image-byte storage, evidence scope, and missingness reporting. |
| `data/wikidata_taxon_crosswalk.tsv` | Staged Wikidata taxon crosswalk rows. |
| `data/commons_media_metadata.tsv` | Staged Commons metadata rows. |
| `data/commons_media_errors.tsv` | Per-category Commons API errors. |
| `data/image_evidence_edges.tsv` | Staged `image_evidence` hyperedge rows. |

## Commands Run

```bash
python3 substrate/staging/wikidata_commons/scripts/fetch_wikidata_taxon_crosswalk.py --max-rows 30000 --limit 5000 --sleep 1.0 --retries 2
python3 substrate/staging/wikidata_commons/scripts/fetch_wikidata_taxon_crosswalk.py --max-rows 30000 --limit 1000 --sleep 0.8 --retries 2
python3 substrate/staging/wikidata_commons/scripts/fetch_wikidata_taxon_crosswalk.py --max-rows 30000 --limit 5000 --sleep 1.0 --retries 2 --scope-properties P961,P960,P1391,P685,P830
python3 substrate/staging/wikidata_commons/scripts/fetch_commons_media_metadata.py --max-taxa 10000 --max-files-per-taxon 1 --sleep 1.0 --retries 1
python3 substrate/staging/wikidata_commons/scripts/build_image_evidence_edges.py
```

## SPARQL Query Template

The broad hierarchy queries below were tested and rejected for this run because the endpoint timed out even at small page sizes:

```sparql
SELECT ?taxon ?taxonName WHERE {
  ?taxon wdt:P31 wd:Q16521 ;
         wdt:P225 ?taxonName ;
         wdt:P171* wd:Q756 .
}
LIMIT 100
```

```sparql
SELECT ?taxon ?taxonName WHERE {
  wd:Q756 ^wdt:P171* ?taxon .
  ?taxon wdt:P225 ?taxonName .
}
LIMIT 100
```

The viable query used plant-specific identifier properties as the plant scope. `__SCOPE_PROP__` was iterated over `P5037`, `P961`, `P960`, `P1391`, then attempted over `P685` and `P830`.

```sparql
SELECT ?taxon ?taxonName ?scopeIdentifier ?commonsCategory WHERE {
  ?taxon wdt:__SCOPE_PROP__ ?scopeIdentifier .
  ?taxon wdt:P225 ?taxonName .
  OPTIONAL { ?taxon wdt:P373 ?commonsCategory . }
}
ORDER BY ?taxon
LIMIT __LIMIT__
OFFSET __OFFSET__
```

Endpoint: Wikidata Query Service SPARQL endpoint [31].

## Commons API Endpoint

Endpoint: Wikimedia Commons MediaWiki Action API [32].

Parameters:

```text
action=query
generator=categorymembers
gcmtitle=Category:{commons_category}
gcmtype=file
gcmlimit=1
prop=imageinfo
iiprop=url|mime|mediatype|size|extmetadata
format=json
formatversion=2
```

The fetcher stores file title, Commons page URL, direct file URL if exposed by the API, MIME/media type, license short name, license URL, artist, attribution, credit, usage terms, source text, width, height, and retrieval timestamp. It never downloads image bytes.

## Rate Limits and Retry Behavior

Both fetchers set a descriptive `User-Agent`, bounded request timeouts, bounded retries, and sleeps between requests. Wikidata was run with 1.0 second sleeps for large pages and 0.8 second sleeps for smaller pages; Commons was run at 1.0 second between categories. Wikidata failures observed: HTTP 504 at offset 15,000 for POWO-scoped rows, HTTP 504 at offset 2,000 during a smaller-page retry, and HTTP 502 at offset 5,000 on later identifier-property pagination. Commons failures observed: HTTP 429 Too Many Requests, recorded per category in `data/commons_media_errors.tsv`.

## Access Dates

All live rows in this branch were retrieved on 2026-05-17 UTC. Row-level retrieval timestamps are stored in each TSV.

## Coverage Counts

| Measure | Count |
|---|---:|
| total Wikidata taxon rows | 15,269 |
| rows with P225 taxon name | 15,269 |
| rows with P685 NCBI taxonomy ID | 0 |
| rows with P960 Tropicos ID | 0 |
| rows with P961 IPNI plant ID | 269 |
| rows with P1391 IPNI publication ID | 0 |
| rows with P5037 POWO ID | 15,000 |
| rows with P830 Encyclopedia of Life ID | 0 |
| rows with Commons category | 1,776 |
| taxa with at least one staged Commons media record | 160 |
| Commons media rows | 160 |
| Commons API error rows | 188 |
| media rows with license present | 159 |
| media rows with attribution present | 160 |
| media rows missing license | 1 |
| media rows missing attribution | 0 |
| staged `image_evidence` edges | 160 |

License coverage among staged media rows was high in this sample: 159/160 rows had `license_short_name` or `license_url`, and 160/160 had at least one of attribution, artist, or credit. This does not generalize to unqueried categories; Commons rate limiting means missingness beyond the sample remains unresolved.

Machine-check missingness summary:

```text
media rows missing license: 1
media rows missing attribution: 0
```

## Evidence Scope

Every staged media edge uses:

```text
edge_type=image_evidence
allowed_evidence_scope=media_display;weak_morphology_inspection
disallowed_evidence_scope=taxonomy;distribution;native_status;edibility;toxicity;human_use;biological_importance
```

Media availability is treated as an observation-process/source-coverage variable. It is not evidence of biological importance, distribution, native status, edibility, toxicity, human use, or taxonomic correctness.

## Known Biases

Wikidata coverage is notability-biased and uneven across regions, languages, institutions, and taxonomic groups. Commons image availability overrepresents cultivated, charismatic, temperate, easily photographed, and iNaturalist-imported taxa. License templates and author metadata vary by uploader and import pipeline; rows without license or attribution are not Atlas-display-ready. Wikidata and Commons are likely correlated with LLM training visibility, so these fields should be treated as coverage and bias covariates in later ablations rather than biological salience.

## Barrier 1 Merge Notes

Downstream joiners may rely on `wikidata_qid`, `taxon_name`, the external identifier columns, `commons_category`, and row-level `retrieved_at`. Suggested crosswalk dedup key: `wikidata_qid`. Suggested media dedup key: `wikidata_qid + commons_file_title + license_url`. Suggested image-edge dedup key: `taxon_node_id + edge_type + image_media_node_id + source_node_id`.

Rows in `image_evidence_edges.tsv` are schema-compatible with frozen PhytoGraph schema v1.0 and require no schema extension. Because coverage floors were not reached, this branch should merge at Barrier 1 as `data-limited` unless a later retry reaches >=30,000 crosswalk rows and >=10,000 taxa with Commons metadata.
