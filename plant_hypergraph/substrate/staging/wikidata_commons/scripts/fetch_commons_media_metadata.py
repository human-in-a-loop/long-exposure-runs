# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone7
# agent: worker
# milestone: M1.9
"""Fetch Wikimedia Commons media metadata for Wikidata Commons categories."""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import time
from datetime import datetime, timezone
from html import unescape
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "PhytoGraph-M1.9-WikidataCommons/0.1 (metadata-only; contact: local-research)"
DEFAULT_SLEEP_SECONDS = 0.4
DEFAULT_TIMEOUT_SECONDS = 60

FIELDNAMES = [
    "wikidata_qid",
    "taxon_name",
    "commons_category",
    "commons_file_title",
    "commons_page_url",
    "file_url",
    "mime",
    "media_type",
    "license_short_name",
    "license_url",
    "artist",
    "attribution",
    "credit",
    "usage_terms",
    "source",
    "width",
    "height",
    "retrieved_at",
]


def clean_html(value: str) -> str:
    return unescape(value or "").replace("\n", " ").replace("\t", " ").strip()


def ext_value(extmetadata: dict, key: str) -> str:
    return clean_html(extmetadata.get(key, {}).get("value", ""))


def existing_taxa(path: pathlib.Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open("r", newline="", encoding="utf-8") as handle:
        return {row["wikidata_qid"] for row in csv.DictReader(handle, delimiter="\t") if row.get("wikidata_qid")}


def iter_crosswalk(path: pathlib.Path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row.get("commons_category"):
                yield row


def category_files(category: str, max_files: int, retries: int) -> list[dict]:
    params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": f"Category:{category}",
        "gcmtype": "file",
        "gcmlimit": str(max_files),
        "prop": "imageinfo",
        "iiprop": "url|mime|mediatype|size|extmetadata",
        "format": "json",
        "formatversion": "2",
    }
    headers = {"User-Agent": USER_AGENT}
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            url = f"{COMMONS_API}?{urlencode(params)}"
            request = Request(url, headers=headers)
            with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8")).get("query", {}).get("pages", [])
        except Exception as exc:  # pragma: no cover - exercised by live endpoint
            last_error = exc
            time.sleep(min(20, 2**attempt))
    raise RuntimeError(f"Commons API failed for category={category!r}: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--crosswalk", default="substrate/staging/wikidata_commons/data/wikidata_taxon_crosswalk.tsv")
    parser.add_argument("--out", default="substrate/staging/wikidata_commons/data/commons_media_metadata.tsv")
    parser.add_argument("--max-taxa", type=int, default=10000)
    parser.add_argument("--max-files-per-taxon", type=int, default=1)
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--errors", default="substrate/staging/wikidata_commons/data/commons_media_errors.tsv")
    args = parser.parse_args()

    out_path = pathlib.Path(args.out)
    errors_path = pathlib.Path(args.errors)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = existing_taxa(out_path)
    mode = "a" if out_path.exists() else "w"
    rows_written = 0
    taxa_with_media = set(done)
    retrieved_at = datetime.now(timezone.utc).isoformat()

    errors_mode = "a" if errors_path.exists() else "w"
    with out_path.open(mode, newline="", encoding="utf-8") as handle, errors_path.open(
        errors_mode, newline="", encoding="utf-8"
    ) as errors_handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=FIELDNAMES)
        error_writer = csv.DictWriter(
            errors_handle,
            delimiter="\t",
            fieldnames=["wikidata_qid", "taxon_name", "commons_category", "error", "retrieved_at"],
        )
        if mode == "w":
            writer.writeheader()
        if errors_mode == "w":
            error_writer.writeheader()
        for taxon in iter_crosswalk(pathlib.Path(args.crosswalk)):
            if len(taxa_with_media) >= args.max_taxa:
                break
            qid = taxon["wikidata_qid"]
            if qid in done:
                continue
            try:
                pages = category_files(taxon["commons_category"], args.max_files_per_taxon, args.retries)
            except Exception as exc:  # pragma: no cover - endpoint-dependent
                error_writer.writerow(
                    {
                        "wikidata_qid": qid,
                        "taxon_name": taxon.get("taxon_name", ""),
                        "commons_category": taxon.get("commons_category", ""),
                        "error": str(exc),
                        "retrieved_at": retrieved_at,
                    }
                )
                errors_handle.flush()
                time.sleep(max(args.sleep, 2.0))
                continue
            wrote_for_taxon = False
            for page in pages:
                title = page.get("title", "")
                imageinfo = (page.get("imageinfo") or [{}])[0]
                ext = imageinfo.get("extmetadata") or {}
                writer.writerow(
                    {
                        "wikidata_qid": qid,
                        "taxon_name": taxon.get("taxon_name", ""),
                        "commons_category": taxon.get("commons_category", ""),
                        "commons_file_title": title,
                        "commons_page_url": f"https://commons.wikimedia.org/wiki/{quote(title.replace(' ', '_'))}",
                        "file_url": imageinfo.get("url", ""),
                        "mime": imageinfo.get("mime", ""),
                        "media_type": imageinfo.get("mediatype", ""),
                        "license_short_name": ext_value(ext, "LicenseShortName"),
                        "license_url": ext_value(ext, "LicenseUrl"),
                        "artist": ext_value(ext, "Artist"),
                        "attribution": ext_value(ext, "Attribution"),
                        "credit": ext_value(ext, "Credit"),
                        "usage_terms": ext_value(ext, "UsageTerms"),
                        "source": ext_value(ext, "ImageDescription") or ext_value(ext, "ObjectName"),
                        "width": imageinfo.get("width", ""),
                        "height": imageinfo.get("height", ""),
                        "retrieved_at": retrieved_at,
                    }
                )
                rows_written += 1
                wrote_for_taxon = True
            if wrote_for_taxon:
                taxa_with_media.add(qid)
            handle.flush()
            time.sleep(args.sleep)
    print(f"wrote={rows_written} taxa_with_media={len(taxa_with_media)} out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
