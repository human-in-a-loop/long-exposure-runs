# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone7
# agent: worker
# milestone: M1.9
"""Build schema v1.0 image_evidence edge staging rows from Commons metadata."""

from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
from datetime import datetime, timezone

ALLOWED_SCOPE = "media_display;weak_morphology_inspection"
DISALLOWED_SCOPE = "taxonomy;distribution;native_status;edibility;toxicity;human_use;biological_importance"

FIELDNAMES = [
    "edge_id",
    "edge_type",
    "taxon_node_id",
    "image_media_node_id",
    "source_node_id",
    "wikidata_qid",
    "taxon_name",
    "commons_file_title",
    "commons_page_url",
    "file_url",
    "provenance_url",
    "license_short_name",
    "license_url",
    "artist",
    "attribution",
    "credit",
    "usage_terms",
    "mime",
    "media_type",
    "width",
    "height",
    "source_reliability",
    "confidence_level",
    "allowed_evidence_scope",
    "disallowed_evidence_scope",
    "caveat",
    "retrieved_at",
    "built_at",
]


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}:{digest}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", default="substrate/staging/wikidata_commons/data/commons_media_metadata.tsv")
    parser.add_argument("--out", default="substrate/staging/wikidata_commons/data/image_evidence_edges.tsv")
    args = parser.parse_args()

    media_path = pathlib.Path(args.media)
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    built_at = datetime.now(timezone.utc).isoformat()
    rows = 0

    with media_path.open("r", newline="", encoding="utf-8") as in_handle, out_path.open(
        "w", newline="", encoding="utf-8"
    ) as out_handle:
        reader = csv.DictReader(in_handle, delimiter="\t")
        writer = csv.DictWriter(out_handle, delimiter="\t", fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in reader:
            qid = row["wikidata_qid"]
            file_title = row["commons_file_title"]
            page_url = row["commons_page_url"]
            writer.writerow(
                {
                    "edge_id": stable_id("image_evidence", qid, file_title),
                    "edge_type": "image_evidence",
                    "taxon_node_id": f"wikidata:{qid}",
                    "image_media_node_id": stable_id("commons_media", file_title),
                    "source_node_id": "source:wikimedia_commons",
                    "wikidata_qid": qid,
                    "taxon_name": row.get("taxon_name", ""),
                    "commons_file_title": file_title,
                    "commons_page_url": page_url,
                    "file_url": row.get("file_url", ""),
                    "provenance_url": page_url,
                    "license_short_name": row.get("license_short_name", ""),
                    "license_url": row.get("license_url", ""),
                    "artist": row.get("artist", ""),
                    "attribution": row.get("attribution", ""),
                    "credit": row.get("credit", ""),
                    "usage_terms": row.get("usage_terms", ""),
                    "mime": row.get("mime", ""),
                    "media_type": row.get("media_type", ""),
                    "width": row.get("width", ""),
                    "height": row.get("height", ""),
                    "source_reliability": "aggregator_with_bias:0.6",
                    "confidence_level": "medium",
                    "allowed_evidence_scope": ALLOWED_SCOPE,
                    "disallowed_evidence_scope": DISALLOWED_SCOPE,
                    "caveat": "Commons media availability is a source-coverage variable, not evidence of taxonomy, distribution, edibility, toxicity, human use, native status, or biological importance.",
                    "retrieved_at": row.get("retrieved_at", ""),
                    "built_at": built_at,
                }
            )
            rows += 1
    print(f"wrote={rows} out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
