# created: 2026-05-17T01:45:00Z
# cycle: 3
# run_id: run-2026-05-17T004540Z
# agent: worker
# milestone: M5
"""Build a tiny frozen public taxonomy/name sample from WFO, GBIF, and Open Tree."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import sys
from collections import Counter, defaultdict
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

import httpx


ACCESS_DATE = "2026-05-17"
CREATED = "2026-05-17T01:45:00Z"
DEFAULT_OUT = Path("data/public_taxonomy_sample/v0.1")
TIMEOUT = 20.0
USER_AGENT = "plant-hypergraph-cycle3-public-sample/0.1"

SEEDS = [
    ("Quercus robur", "accepted_species"),
    ("Poa annua", "accepted_species"),
    ("Rosa canina", "accepted_species"),
    ("Arabidopsis thaliana", "accepted_species"),
    ("Solanum lycopersicum", "accepted_species"),
    ("Zea mays", "accepted_species"),
    ("Oryza sativa", "accepted_species"),
    ("Triticum aestivum", "accepted_species"),
    ("Acer saccharum", "accepted_species"),
    ("Betula pendula", "accepted_species"),
    ("Acacia dealbata", "accepted_species"),
    ("Eucalyptus globulus", "accepted_species"),
    ("Picea abies", "accepted_species"),
    ("Pinus sylvestris", "accepted_species"),
    ("Rhopalocarpus alternifolius (Baker) Capuron", "authorship_name"),
    ("Rosa", "genus_level_ambiguity"),
]

WFO_ENDPOINT = "https://list.worldfloraonline.org/matching_rest.php"
GBIF_MATCH_ENDPOINT = "https://api.gbif.org/v1/species/match"
OPENTREE_TNRS_ENDPOINT = "https://api.opentreeoflife.org/v3/tnrs/match_names"

TAXA_COLUMNS = [
    "local_taxon_id",
    "source",
    "source_taxon_id",
    "canonical_name",
    "accepted_name",
    "rank",
    "parent_id",
    "status",
    "query_name",
    "match_type",
    "confidence",
]
NAMES_COLUMNS = [
    "name_id",
    "name_string",
    "accepted_taxon_id",
    "source",
    "source_name_id",
    "name_status",
    "query_name",
    "leakage_group_id",
    "task_visibility",
]
CROSSWALK_COLUMNS = [
    "query_name",
    "rationale_class",
    "wfo_id",
    "wfo_status",
    "gbif_key",
    "gbif_status",
    "ott_id",
    "opentree_status",
    "sources_matched",
    "match_summary",
    "disagreement_category",
]
EDGE_COLUMNS = [
    "edge_id",
    "edge_family",
    "node_id",
    "node_type",
    "role",
    "role_weight",
    "edge_weight",
    "provenance",
    "is_synthetic",
]
SPLIT_COLUMNS = ["leakage_group_id", "split", "query_name", "basis"]


def slug(text: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", text.strip().lower()).strip("_")
    return value[:80] or "empty"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(payload))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def request_json(client: httpx.Client, method: str, url: str, *, params: dict[str, Any] | None = None, json_body: Any = None, insecure_tls_fallback: bool = False) -> dict[str, Any]:
    request = {"method": method, "url": url, "params": params or {}, "json": json_body}
    try:
        response = client.request(method, url, params=params, json=json_body)
        return {
            "ok": response.is_success,
            "http_status": response.status_code,
            "request": request,
            "payload": response.json() if response.content else None,
            "error": None if response.is_success else response.text[:500],
            "used_insecure_tls_fallback": False,
        }
    except Exception as exc:
        if insecure_tls_fallback and "CERTIFICATE_VERIFY_FAILED" in str(exc):
            try:
                with httpx.Client(timeout=TIMEOUT, verify=False, headers={"User-Agent": USER_AGENT}) as insecure:
                    response = insecure.request(method, url, params=params, json=json_body)
                    return {
                        "ok": response.is_success,
                        "http_status": response.status_code,
                        "request": request,
                        "payload": response.json() if response.content else None,
                        "error": None if response.is_success else response.text[:500],
                        "used_insecure_tls_fallback": True,
                    }
            except Exception as retry_exc:
                return {"ok": False, "http_status": None, "request": request, "payload": None, "error": f"{retry_exc.__class__.__name__}: {retry_exc}", "used_insecure_tls_fallback": False}
        return {"ok": False, "http_status": None, "request": request, "payload": None, "error": f"{exc.__class__.__name__}: {exc}", "used_insecure_tls_fallback": False}


def cached_request(raw_path: Path, client: httpx.Client, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
    if raw_path.exists():
        return read_json(raw_path)
    result = request_json(client, method, url, **kwargs)
    result["response_sha256"] = sha256_bytes(canonical_json(result.get("payload"))) if result.get("payload") is not None else None
    write_json(raw_path, result)
    return result


def first_wfo_match(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {}
    match = payload.get("match") or {}
    if match:
        return match
    candidates = payload.get("candidates") or []
    return candidates[0] if candidates else {}


def text_field(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def split_for_group(group_id: str) -> str:
    x = int(hashlib.sha256(group_id.encode("utf-8")).hexdigest()[:8], 16) / float(16**8)
    if x < 0.6:
        return "train"
    if x < 0.8:
        return "validation"
    return "test"


def add_incidence(rows: list[dict[str, Any]], edge_id: str, family: str, members: list[tuple[str, str, str, float]], provenance: str, edge_weight: float) -> None:
    for node_id, node_type, role, role_weight in members:
        if not node_id:
            continue
        rows.append(
            {
                "edge_id": edge_id,
                "edge_family": family,
                "node_id": node_id,
                "node_type": node_type,
                "role": role,
                "role_weight": f"{role_weight:.3f}",
                "edge_weight": f"{edge_weight:.3f}",
                "provenance": provenance,
                "is_synthetic": "false",
            }
        )


def normalize(seed_rows: list[tuple[str, str]], raw: dict[str, dict[str, dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    taxa: list[dict[str, Any]] = []
    names: list[dict[str, Any]] = []
    crosswalk: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    splits_by_group: dict[str, dict[str, Any]] = {}
    seen_taxa: set[str] = set()
    seen_names: set[str] = set()

    def add_taxon(row: dict[str, Any]) -> str:
        if row["local_taxon_id"] not in seen_taxa:
            seen_taxa.add(row["local_taxon_id"])
            taxa.append(row)
        return str(row["local_taxon_id"])

    def add_name(row: dict[str, Any]) -> None:
        if row["name_id"] not in seen_names:
            seen_names.add(row["name_id"])
            names.append(row)
            splits_by_group.setdefault(
                row["leakage_group_id"],
                {"leakage_group_id": row["leakage_group_id"], "split": split_for_group(row["leakage_group_id"]), "query_name": row["query_name"], "basis": "accepted_taxon_or_source_name_cluster"},
            )

    for query_name, rationale in seed_rows:
        qslug = slug(query_name)
        source_taxa: dict[str, str] = {}
        status_by_source: dict[str, str] = {}

        wfo_raw = raw["wfo"][qslug]
        wfo_payload = wfo_raw.get("payload") if wfo_raw.get("ok") else None
        wfo = first_wfo_match(wfo_payload)
        if wfo:
            wfo_id = text_field(wfo, "wfo_id", "wfoId", "id")
            canonical = text_field(wfo, "full_name_plain", "fullNameStringPlain", "scientificName", "name")
            accepted = text_field(wfo, "accepted_name", "acceptedName", "acceptedNameStringPlain") or canonical
            rank = text_field(wfo, "rank", "taxonRank") or text_field((wfo_payload or {}).get("parsedName") or {}, "rank")
            if (wfo_payload or {}).get("match"):
                status = text_field(wfo, "taxonomicStatus", "status") or "matched"
            else:
                status = "candidate_unresolved"
            local_id = f"wfo:{wfo_id or qslug}"
            source_taxa["wfo"] = add_taxon({"local_taxon_id": local_id, "source": "WFO", "source_taxon_id": wfo_id, "canonical_name": canonical, "accepted_name": accepted, "rank": rank, "parent_id": "", "status": status, "query_name": query_name, "match_type": text_field(wfo_payload or {}, "method"), "confidence": ""})
            status_by_source["wfo"] = status
            add_name({"name_id": f"name:wfo:{wfo_id or qslug}:query", "name_string": query_name, "accepted_taxon_id": local_id, "source": "WFO", "source_name_id": wfo_id, "name_status": "query_name", "query_name": query_name, "leakage_group_id": f"cluster:{local_id}", "task_visibility": "name_normalization_only"})
            if canonical and canonical != query_name:
                add_name({"name_id": f"name:wfo:{wfo_id or qslug}:canonical", "name_string": canonical, "accepted_taxon_id": local_id, "source": "WFO", "source_name_id": wfo_id, "name_status": status, "query_name": query_name, "leakage_group_id": f"cluster:{local_id}", "task_visibility": "name_normalization_only"})

        gbif_raw = raw["gbif"][qslug]
        gbif = gbif_raw.get("payload") if gbif_raw.get("ok") else None
        if gbif and gbif.get("usageKey"):
            usage_key = str(gbif.get("usageKey"))
            accepted_key = str(gbif.get("acceptedUsageKey") or usage_key)
            local_id = f"gbif:{accepted_key}"
            rank = text_field(gbif, "rank")
            parent_id = ""
            for parent_rank in ("species", "genus", "family", "kingdom"):
                key = gbif.get(f"{parent_rank}Key")
                name = gbif.get(parent_rank)
                if key and str(key) != accepted_key:
                    parent_id = f"gbif:{key}"
                    add_taxon({"local_taxon_id": parent_id, "source": "GBIF", "source_taxon_id": key, "canonical_name": name or "", "accepted_name": name or "", "rank": parent_rank, "parent_id": "", "status": "backbone_parent", "query_name": query_name, "match_type": "derived_from_match", "confidence": ""})
                    break
            source_taxa["gbif"] = add_taxon({"local_taxon_id": local_id, "source": "GBIF", "source_taxon_id": accepted_key, "canonical_name": text_field(gbif, "canonicalName", "scientificName"), "accepted_name": text_field(gbif, "accepted", "scientificName", "canonicalName"), "rank": rank, "parent_id": parent_id, "status": text_field(gbif, "status") or "matched", "query_name": query_name, "match_type": text_field(gbif, "matchType"), "confidence": text_field(gbif, "confidence")})
            status_by_source["gbif"] = text_field(gbif, "status") or "matched"
            add_name({"name_id": f"name:gbif:{usage_key}:query", "name_string": query_name, "accepted_taxon_id": local_id, "source": "GBIF", "source_name_id": usage_key, "name_status": text_field(gbif, "status") or "query_name", "query_name": query_name, "leakage_group_id": f"cluster:{local_id}", "task_visibility": "name_normalization_only"})
            canonical = text_field(gbif, "canonicalName", "scientificName")
            if canonical and canonical != query_name:
                add_name({"name_id": f"name:gbif:{usage_key}:canonical", "name_string": canonical, "accepted_taxon_id": local_id, "source": "GBIF", "source_name_id": usage_key, "name_status": "canonical", "query_name": query_name, "leakage_group_id": f"cluster:{local_id}", "task_visibility": "name_normalization_only"})

        ot_raw = raw["opentree"][qslug]
        ot_payload = ot_raw.get("payload") if ot_raw.get("ok") else None
        ot_result = ((ot_payload or {}).get("results") or [{}])[0]
        ot_match = (ot_result.get("matches") or [{}])[0]
        ot_taxon = ot_match.get("taxon") or {}
        if ot_taxon.get("ott_id"):
            ott_id = str(ot_taxon.get("ott_id"))
            local_id = f"ott:{ott_id}"
            status = "synonym" if ot_match.get("is_synonym") else "matched"
            source_taxa["opentree"] = add_taxon({"local_taxon_id": local_id, "source": "OpenTree", "source_taxon_id": ott_id, "canonical_name": text_field(ot_taxon, "name"), "accepted_name": text_field(ot_taxon, "name"), "rank": text_field(ot_taxon, "rank"), "parent_id": "", "status": status, "query_name": query_name, "match_type": "TNRS", "confidence": text_field(ot_match, "score")})
            status_by_source["opentree"] = status
            add_name({"name_id": f"name:ott:{ott_id}:query", "name_string": query_name, "accepted_taxon_id": local_id, "source": "OpenTree", "source_name_id": ott_id, "name_status": status, "query_name": query_name, "leakage_group_id": f"cluster:{local_id}", "task_visibility": "name_normalization_only"})
            matched_name = text_field(ot_match, "matched_name") or text_field(ot_taxon, "name")
            if matched_name and matched_name != query_name:
                add_name({"name_id": f"name:ott:{ott_id}:matched", "name_string": matched_name, "accepted_taxon_id": local_id, "source": "OpenTree", "source_name_id": ott_id, "name_status": "matched_name", "query_name": query_name, "leakage_group_id": f"cluster:{local_id}", "task_visibility": "name_normalization_only"})

        for local_id in source_taxa.values():
            taxon = next(t for t in taxa if t["local_taxon_id"] == local_id)
            if taxon.get("parent_id"):
                add_incidence(edges, f"edge:tax_parent:{local_id}", "taxonomic_parentage", [(local_id, "taxon", "child_taxon", 1.0), (taxon["parent_id"], "taxon", "parent_taxon", 1.0), (f"rank:{taxon['rank']}", "rank", "child_rank", 1.0), (f"source:{taxon['source']}", "source", "source", 1.0)], taxon["source"], 0.8 if taxon["source"] == "GBIF" else 1.0)

        if len(source_taxa) >= 2:
            add_incidence(edges, f"edge:source_context:{qslug}", "regional_checklist_context", [(f"query:{qslug}", "name_string", "query_name", 1.0), *[(taxon_id, "taxon", f"{source}_taxon", 1.0) for source, taxon_id in source_taxa.items()], *[(f"source:{source}", "source", "source", 1.0) for source in source_taxa]], "public_source_crosswalk", 0.7)

        statuses = {v.lower() for v in status_by_source.values() if v}
        sources_matched = len(source_taxa)
        if sources_matched == 0:
            category = "unmatched"
        elif sources_matched == 1:
            category = "single_source_only"
        elif len(statuses) > 1:
            category = "different_status"
        else:
            accepted_names = {next(t for t in taxa if t["local_taxon_id"] == tid)["accepted_name"].lower() for tid in source_taxa.values() if next(t for t in taxa if t["local_taxon_id"] == tid)["accepted_name"]}
            category = "different_accepted_name" if len(accepted_names) > 1 else "all_source_agreement"

        crosswalk.append(
            {
                "query_name": query_name,
                "rationale_class": rationale,
                "wfo_id": source_taxa.get("wfo", "").removeprefix("wfo:"),
                "wfo_status": status_by_source.get("wfo", "missing"),
                "gbif_key": source_taxa.get("gbif", "").removeprefix("gbif:"),
                "gbif_status": status_by_source.get("gbif", "missing"),
                "ott_id": source_taxa.get("opentree", "").removeprefix("ott:"),
                "opentree_status": status_by_source.get("opentree", "missing"),
                "sources_matched": sources_matched,
                "match_summary": ";".join(f"{source}={taxon_id}" for source, taxon_id in sorted(source_taxa.items())),
                "disagreement_category": category,
            }
        )

    names_by_taxon: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for name in names:
        names_by_taxon[name["accepted_taxon_id"]].append(name)
    for accepted_taxon_id, cluster_names in sorted(names_by_taxon.items()):
        source = cluster_names[0]["source"]
        members: list[tuple[str, str, str, float]] = [
            (accepted_taxon_id, "taxon", "accepted_taxon", 1.0),
            (f"source:{source}", "source", "source", 1.0),
        ]
        members.extend((name["name_id"], "name_string", "name", 1.0) for name in cluster_names)
        add_incidence(edges, f"edge:synonym_cluster:{accepted_taxon_id}", "synonym_cluster", members, source, 1.0 if source == "WFO" else 0.8)

    return taxa, names, crosswalk, edges, list(splits_by_group.values())


def make_coverage_plot(path: Path, crosswalk: list[dict[str, Any]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [row["query_name"] for row in crosswalk]
    sources = ["wfo", "gbif", "ott"]
    colors = {"wfo": "#2C7A7B", "gbif": "#4A5568", "ott": "#B7791F"}
    fig, ax = plt.subplots(figsize=(10, 6))
    for y, row in enumerate(crosswalk):
        present = [bool(row["wfo_id"]), bool(row["gbif_key"]), bool(row["ott_id"])]
        for x, ok in enumerate(present):
            ax.scatter(x, y, s=110, marker="s", color=colors[sources[x]] if ok else "#E2E8F0", edgecolor="#2D3748", linewidth=0.5)
        ax.text(3.25, y, row["disagreement_category"], va="center", fontsize=7)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["WFO", "GBIF", "Open Tree"])
    ax.set_xlim(-0.5, 5.8)
    ax.set_title("Public sample source coverage by seed name")
    ax.set_xlabel("Source")
    ax.set_ylabel("Seed name")
    ax.grid(axis="x", color="#CBD5E0", linewidth=0.5)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def build(out_dir: Path, seed_rows: list[tuple[str, str]]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "seed_names.csv", ["query_name", "rationale_class"], [{"query_name": name, "rationale_class": rationale} for name, rationale in seed_rows])
    raw: dict[str, dict[str, dict[str, Any]]] = {"wfo": {}, "gbif": {}, "opentree": {}}

    with httpx.Client(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        for name, _ in seed_rows:
            qslug = slug(name)
            raw["wfo"][qslug] = cached_request(out_dir / "raw" / "wfo" / f"{qslug}.json", client, "GET", WFO_ENDPOINT, params={"input_string": name}, insecure_tls_fallback=True)
            raw["gbif"][qslug] = cached_request(out_dir / "raw" / "gbif" / f"{qslug}.json", client, "GET", GBIF_MATCH_ENDPOINT, params={"name": name, "kingdom": "Plantae"})
            raw["opentree"][qslug] = cached_request(out_dir / "raw" / "opentree" / f"{qslug}.json", client, "POST", OPENTREE_TNRS_ENDPOINT, json_body={"names": [name], "context_name": "Land plants", "do_approximate_matching": False, "include_suppressed": False})

    taxa, names, crosswalk, edges, splits = normalize(seed_rows, raw)
    write_csv(out_dir / "taxa.csv", TAXA_COLUMNS, taxa)
    write_csv(out_dir / "names.csv", NAMES_COLUMNS, names)
    write_csv(out_dir / "source_crosswalk.csv", CROSSWALK_COLUMNS, crosswalk)
    write_csv(out_dir / "hyperedges.csv", EDGE_COLUMNS, edges)
    write_csv(out_dir / "splits.csv", SPLIT_COLUMNS, sorted(splits, key=lambda r: r["leakage_group_id"]))
    make_coverage_plot(out_dir / "source_coverage.png", crosswalk)

    artifact_paths = [p for p in sorted(out_dir.rglob("*")) if p.is_file() and p.name != "metadata.json"]
    metadata = {
        "created": CREATED,
        "access_date": ACCESS_DATE,
        "cycle": 3,
        "milestone": "M5",
        "script": "scripts/build_public_taxonomy_sample.py",
        "endpoints": {
            "wfo": WFO_ENDPOINT,
            "gbif_match": GBIF_MATCH_ENDPOINT,
            "opentree_tnrs": OPENTREE_TNRS_ENDPOINT,
        },
        "query_parameters": {
            "wfo": {"input_string": "<seed_name>"},
            "gbif": {"name": "<seed_name>", "kingdom": "Plantae"},
            "opentree": {"names": ["<seed_name>"], "context_name": "Land plants", "do_approximate_matching": False, "include_suppressed": False},
        },
        "software_versions": {
            "python": platform.python_version(),
            "httpx": getattr(httpx, "__version__", "unknown"),
            "matplotlib": importlib_metadata.version("matplotlib"),
        },
        "license_citation_notes": {
            "WFO": "Use WFO Plant List/API citation guidance; source used only for tiny no-auth name matching sample.",
            "GBIF": "Use GBIF citation/terms guidance; species match API only, no async downloads or occurrence records in this cycle.",
            "OpenTree": "Use Open Tree license/citation guidance; TNRS used as taxonomy/phylogeny synthesis context, not WFO-equivalent truth.",
        },
        "known_limitations": [
            "Small seed-list sample; not representative of plant taxonomy.",
            "No occurrence provenance edges are emitted because occurrence reads are disabled for this cycle.",
            "No trait, reticulate, hybrid-origin, range, or phylogenetic novelty claims are supported.",
            "WFO/GBIF/Open Tree records are source-specific and intentionally not reconciled into one accepted truth.",
        ],
        "summary": {
            "seed_count": len(seed_rows),
            "seeds_with_two_or_more_sources": sum(1 for row in crosswalk if int(row["sources_matched"]) >= 2),
            "disagreement_categories": dict(Counter(row["disagreement_category"] for row in crosswalk)),
            "taxa_rows": len(taxa),
            "name_rows": len(names),
            "hyperedge_rows": len(edges),
        },
        "hashes": {str(path.relative_to(out_dir)): sha256_file(path) for path in artifact_paths},
    }
    write_json(out_dir / "metadata.json", metadata)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    metadata = build(Path(args.out_dir), SEEDS)
    print(json.dumps(metadata["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
