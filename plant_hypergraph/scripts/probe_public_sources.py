#!/usr/bin/env python3
# created: 2026-05-17T00:45:40Z
# cycle: 1
# run_id: run-2026-05-17T004540Z
# agent: worker
# milestone: M1
"""Tiny no-auth smoke tests for WFO, GBIF, and Open Tree public reads."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx


ACCESS_DATE = "2026-05-17"
EXAMPLES = ["Quercus robur", "Rosa canina", "Rhopalocarpus alternifolius (Baker) Capuron"]
DEFAULT_OUT = Path("data/source_probe_results.json")
TIMEOUT = 20.0


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def compact_error(exc: Exception) -> str:
    return f"{exc.__class__.__name__}: {exc}"


def get_json(
    client: httpx.Client,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    insecure_tls_fallback: bool = False,
) -> tuple[int | None, Any, str | None, bool]:
    try:
        response = client.get(url, params=params)
        status = response.status_code
        response.raise_for_status()
        return status, response.json(), None, False
    except Exception as exc:  # endpoint smoke tests must fail gracefully
        if insecure_tls_fallback and "CERTIFICATE_VERIFY_FAILED" in str(exc):
            try:
                with httpx.Client(
                    timeout=TIMEOUT,
                    verify=False,
                    headers={"User-Agent": "plant-hypergraph-cycle1-probe/0.1"},
                ) as insecure_client:
                    response = insecure_client.get(url, params=params)
                    status = response.status_code
                    response.raise_for_status()
                    return status, response.json(), "TLS verification failed locally; retried with verify=False", True
            except Exception as retry_exc:
                status = getattr(getattr(retry_exc, "response", None), "status_code", None)
                return status, None, compact_error(retry_exc), False
        status = getattr(getattr(exc, "response", None), "status_code", None)
        return status, None, compact_error(exc), False


def post_json(client: httpx.Client, url: str, *, payload: dict[str, Any]) -> tuple[int | None, Any, str | None]:
    try:
        response = client.post(url, json=payload)
        status = response.status_code
        response.raise_for_status()
        return status, response.json(), None
    except Exception as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        return status, None, compact_error(exc)


def probe_wfo(client: httpx.Client) -> dict[str, Any]:
    endpoint = "https://list.worldfloraonline.org/matching_rest.php"
    records = []
    for name in EXAMPLES:
        status, payload, error, used_insecure_tls = get_json(
            client,
            endpoint,
            params={"input_string": name},
            insecure_tls_fallback=True,
        )
        match = (payload or {}).get("match") or {}
        first_candidate = ((payload or {}).get("candidates") or [{}])[0]
        records.append(
            {
                "input_name": name,
                "http_status": status,
                "ok": payload is not None,
                "failure_reason": error,
                "used_insecure_tls_fallback": used_insecure_tls,
                "selected_fields": {
                    "wfo_id": match.get("wfo_id") or match.get("wfoId"),
                    "full_name_plain": match.get("full_name_plain") or match.get("fullNameStringPlain"),
                    "placement": match.get("placement"),
                    "candidate_count": len((payload or {}).get("candidates") or []),
                    "first_candidate_wfo_id": first_candidate.get("wfo_id") or first_candidate.get("wfoId"),
                    "first_candidate_name": first_candidate.get("full_name_plain")
                    or first_candidate.get("fullNameStringPlain"),
                    "method": (payload or {}).get("method"),
                },
                "response_sha256": digest_payload(payload) if payload is not None else None,
            }
        )
    return {
        "source": "WFO Plant List",
        "endpoint": endpoint,
        "documentation_refs": ["[1]", "[2]"],
        "records": records,
    }


def probe_gbif(client: httpx.Client) -> dict[str, Any]:
    species_endpoint = "https://api.gbif.org/v1/species/match"
    occurrence_endpoint = "https://api.gbif.org/v1/occurrence/search"
    species_records = []
    occurrence_records = []
    for name in EXAMPLES[:2]:
        status, payload, error, _ = get_json(client, species_endpoint, params={"name": name, "kingdom": "Plantae"})
        usage_key = (payload or {}).get("usageKey")
        species_records.append(
            {
                "input_name": name,
                "http_status": status,
                "ok": error is None,
                "failure_reason": error,
                "selected_fields": {
                    "usageKey": usage_key,
                    "acceptedUsageKey": (payload or {}).get("acceptedUsageKey"),
                    "scientificName": (payload or {}).get("scientificName"),
                    "canonicalName": (payload or {}).get("canonicalName"),
                    "rank": (payload or {}).get("rank"),
                    "status": (payload or {}).get("status"),
                    "confidence": (payload or {}).get("confidence"),
                    "matchType": (payload or {}).get("matchType"),
                },
                "response_sha256": digest_payload(payload) if payload is not None else None,
            }
        )
        if usage_key:
            occ_status, occ_payload, occ_error, _ = get_json(
                client,
                occurrence_endpoint,
                params={"taxonKey": usage_key, "limit": 1, "hasCoordinate": "true"},
            )
            result = ((occ_payload or {}).get("results") or [{}])[0]
            occurrence_records.append(
                {
                    "input_name": name,
                    "http_status": occ_status,
                    "ok": occ_error is None,
                    "failure_reason": occ_error,
                    "selected_fields": {
                        "count": (occ_payload or {}).get("count"),
                        "gbifID": result.get("gbifID"),
                        "species": result.get("species"),
                        "countryCode": result.get("countryCode"),
                        "datasetKey": result.get("datasetKey"),
                        "license": result.get("license"),
                        "basisOfRecord": result.get("basisOfRecord"),
                    },
                    "response_sha256": digest_payload(occ_payload) if occ_payload is not None else None,
                }
            )
    return {
        "source": "GBIF",
        "species_endpoint": species_endpoint,
        "occurrence_endpoint": occurrence_endpoint,
        "documentation_refs": ["[6]", "[7]", "[8]", "[10]", "[11]"],
        "species_records": species_records,
        "occurrence_records": occurrence_records,
    }


def probe_opentree(client: httpx.Client) -> dict[str, Any]:
    endpoint = "https://api.opentreeoflife.org/v3/tnrs/match_names"
    payload = {
        "names": EXAMPLES[:2],
        "context_name": "Land plants",
        "do_approximate_matching": False,
        "include_suppressed": False,
    }
    status, response_payload, error = post_json(client, endpoint, payload=payload)
    records = []
    for result in (response_payload or {}).get("results", []):
        first_match = (result.get("matches") or [{}])[0]
        taxon = first_match.get("taxon") or {}
        records.append(
            {
                "input_name": result.get("name"),
                "selected_fields": {
                    "matched_name": first_match.get("matched_name"),
                    "score": first_match.get("score"),
                    "is_synonym": first_match.get("is_synonym"),
                    "ott_id": taxon.get("ott_id"),
                    "taxon_name": taxon.get("name"),
                    "rank": taxon.get("rank"),
                    "tax_sources": taxon.get("tax_sources"),
                },
            }
        )
    return {
        "source": "Open Tree of Life",
        "endpoint": endpoint,
        "documentation_refs": ["[12]", "[13]", "[14]", "[15]"],
        "http_status": status,
        "ok": error is None,
        "failure_reason": error,
        "taxonomy_metadata": (response_payload or {}).get("taxonomy"),
        "records": records,
        "response_sha256": digest_payload(response_payload) if response_payload is not None else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    args = parser.parse_args()
    out_path = Path(args.out)

    with httpx.Client(timeout=TIMEOUT, headers={"User-Agent": "plant-hypergraph-cycle1-probe/0.1"}) as client:
        result = {
            "created_at": now_iso(),
            "access_date": ACCESS_DATE,
            "script": "scripts/probe_public_sources.py",
            "examples": EXAMPLES,
            "probes": [probe_wfo(client), probe_gbif(client), probe_opentree(client)],
        }

    reached = {}
    for probe in result["probes"]:
        if probe["source"] == "WFO Plant List":
            reached[probe["source"]] = any(record.get("ok") for record in probe["records"])
        elif probe["source"] == "GBIF":
            reached[probe["source"]] = any(record.get("ok") for record in probe["species_records"])
        elif probe["source"] == "Open Tree of Life":
            reached[probe["source"]] = bool(probe.get("ok"))

    result["summary"] = {
        "all_sources_reached": all(reached.values()),
        "source_reached": reached,
        "note": "Failures are recorded per endpoint; the script exits zero if JSON output was written.",
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
