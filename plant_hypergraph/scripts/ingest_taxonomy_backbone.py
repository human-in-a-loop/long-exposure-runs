# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone0
# agent: worker
# milestone: M1.1
"""Stage the PhytoGraph M1.1 taxonomy backbone from no-auth public sources."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import pandas as pd


ACCESS_DATE = "2026-05-17"
CLONE_ID = "fork-e34b5b2c1c6c-clone-0"
DEFAULT_OUT = Path("substrate/staging/taxonomy_backbone")
WFO_URL = "https://zenodo.org/records/18007552/files/wfo_plantlist_2025-12.zip"
GBIF_MATCH_URL = "https://api.gbif.org/v1/species/match"
OPENTREE_TNRS_URL = "https://api.opentreeoflife.org/v3/tnrs/match_names"
POWO_SEARCH_URL = "https://powo.science.kew.org/api/2/search"
USER_AGENT = "phytograph-taxonomy-backbone-m1.1/0.1"
LICENSE = {
    "WFO": "WFO Plant List 2025-12; Zenodo DOI 10.5281/zenodo.18007552; see metadata.json/license",
    "GBIF": "GBIF API terms/citation guidelines",
    "OpenTree": "Open Tree of Life license/citation guidance",
    "POWO": "Royal Botanic Gardens, Kew POWO website terms; API sampled conservatively",
}
TARGET_FLOOR = 50_000
M5_SEEDS = [
    "Quercus robur",
    "Poa annua",
    "Rosa canina",
    "Arabidopsis thaliana",
    "Solanum lycopersicum",
    "Zea mays",
    "Oryza sativa",
    "Triticum aestivum",
    "Acer saccharum",
    "Betula pendula",
    "Acacia dealbata",
    "Eucalyptus globulus",
    "Picea abies",
    "Pinus sylvestris",
    "Rhopalocarpus alternifolius (Baker) Capuron",
    "Rosa",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_name(value: str) -> str:
    return " ".join(str(value or "").lower().replace("×", "x").split())


def download(url: str, path: Path, refresh: bool) -> None:
    if path.exists() and not refresh:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=300, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as response:
        response.raise_for_status()
        with path.open("wb") as handle:
            for chunk in response.iter_bytes():
                handle.write(chunk)


def read_wfo_tables(zip_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    with zipfile.ZipFile(zip_path) as zf:
        taxon = pd.read_csv(zf.open("taxon.tsv"), sep="\t", dtype=str, keep_default_na=False)
        name = pd.read_csv(zf.open("name.tsv"), sep="\t", dtype=str, keep_default_na=False)
        synonym = pd.read_csv(zf.open("synonym.tsv"), sep="\t", dtype=str, keep_default_na=False)
        metadata = json.loads(zf.read("metadata.json").decode("utf-8"))
    return taxon, name, synonym, metadata


def family_for(taxon_id: str, parent: dict[str, str], rank: dict[str, str], sci: dict[str, str]) -> str:
    current = taxon_id
    for _ in range(30):
        if rank.get(current) == "family":
            return sci.get(current, "")
        current = parent.get(current, "")
        if not current:
            return ""
    return ""


def has_ancestor_named(taxon_id: str, target: str, parent: dict[str, str], sci: dict[str, str]) -> bool:
    current = taxon_id
    for _ in range(40):
        if sci.get(current) == target:
            return True
        current = parent.get(current, "")
        if not current:
            return False
    return False


def make_wfo_records(taxon: pd.DataFrame, name: pd.DataFrame, limit: int | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    name_cols = ["ID", "scientificName", "rank", "genus", "specificEpithet", "infraspecificEpithet", "authorship", "link"]
    merged = taxon.merge(name[name_cols], left_on="nameID", right_on="ID", how="left", suffixes=("_taxon", "_name"))
    merged = merged.rename(columns={"ID_taxon": "wfo_taxon_id", "ID_name": "wfo_name_id"})
    merged["rank"] = merged["rank"].str.lower()
    staged_ranks = {
        "family",
        "genus",
        "species",
        "subspecies",
        "variety",
        "form",
        "subvariety",
        "subform",
    }
    all_taxa = taxon.merge(name[["ID", "scientificName", "rank"]], left_on="nameID", right_on="ID", how="left", suffixes=("_taxon", "_name"))
    parent = dict(zip(all_taxa["ID_taxon"], all_taxa["parentID"]))
    rank = dict(zip(all_taxa["ID_taxon"], all_taxa["rank"].str.lower()))
    sci = dict(zip(all_taxa["ID_taxon"], all_taxa["scientificName"]))
    merged = merged[merged["rank"].isin(staged_ranks)].copy()
    merged["major_clade"] = ["Angiosperms" if has_ancestor_named(tid, "Angiosperms", parent, sci) else "" for tid in merged["wfo_taxon_id"]]
    merged = merged[merged["major_clade"].eq("Angiosperms")].copy()
    merged = merged.sort_values(["rank", "scientificName", "wfo_taxon_id"], kind="stable")
    if limit:
        merged = merged.head(limit).copy()
    merged["family"] = [family_for(tid, parent, rank, sci) for tid in merged["wfo_taxon_id"]]
    accepted = pd.DataFrame(
        {
            "accepted_taxon_key": "wfo:" + merged["wfo_taxon_id"],
            "wfo_id": merged["wfo_taxon_id"],
            "accepted_name": merged["scientificName"],
            "rank": merged["rank"],
            "family": merged["family"],
            "genus": merged["genus"],
            "species": merged["specificEpithet"],
            "infraspecific_epithet": merged["infraspecificEpithet"],
            "major_clade": merged["major_clade"],
            "parent_wfo_id": merged["parentID"],
            "source": "WFO",
            "source_identifier": merged["wfo_taxon_id"],
            "access_date": ACCESS_DATE,
            "license": LICENSE["WFO"],
            "ingest_clone_id": CLONE_ID,
            "provenance_url": merged["link_taxon"],
        }
    )
    wfo_taxa = accepted.copy()
    wfo_taxa.insert(0, "source_local_record_id", accepted["wfo_id"])
    return accepted.reset_index(drop=True), wfo_taxa.reset_index(drop=True)


def make_wfo_synonyms(synonym: pd.DataFrame, name: pd.DataFrame, accepted_keys: set[str]) -> pd.DataFrame:
    syn = synonym[synonym["taxonID"].map(lambda x: "wfo:" + x in accepted_keys)].copy()
    if syn.empty:
        return pd.DataFrame()
    name_cols = ["ID", "scientificName", "rank", "genus", "specificEpithet", "infraspecificEpithet", "link"]
    syn = syn.merge(name[name_cols], left_on="nameID", right_on="ID", how="left", suffixes=("_synonym", "_name"))
    out = pd.DataFrame(
        {
            "accepted_taxon_key": "wfo:" + syn["taxonID"],
            "source": "WFO",
            "source_identifier": syn["ID_synonym"],
            "source_name_id": syn["nameID"],
            "name_string": syn["scientificName"],
            "normalized_name_key": syn["scientificName"].map(normalize_name),
            "name_status": "synonym",
            "rank": syn["rank"].str.lower(),
            "family": "",
            "genus": syn["genus"],
            "species": syn["specificEpithet"],
            "infraspecific_epithet": syn["infraspecificEpithet"],
            "task_visibility": "name_normalization_only",
            "allowed_evidence_scope": "synonym/name normalization only; does not support trait, range, phylogeny, reticulation, or biological novelty claims",
            "access_date": ACCESS_DATE,
            "license": LICENSE["WFO"],
            "ingest_clone_id": CLONE_ID,
            "provenance_url": syn["link_synonym"],
        }
    )
    return out.drop_duplicates().reset_index(drop=True)


def match_gbif(client: httpx.Client, name: str) -> dict[str, str]:
    try:
        r = client.get(GBIF_MATCH_URL, params={"name": name, "kingdom": "Plantae"}, timeout=20)
        if not r.is_success:
            return {}
        p = r.json()
    except Exception:
        return {}
    if not p.get("usageKey"):
        return {}
    return {
        "gbif_taxon_key": str(p.get("acceptedUsageKey") or p.get("usageKey")),
        "gbif_usage_key": str(p.get("usageKey") or ""),
        "accepted_name": str(p.get("scientificName") or p.get("canonicalName") or ""),
        "rank": str(p.get("rank") or "").lower(),
        "family": str(p.get("family") or ""),
        "genus": str(p.get("genus") or ""),
        "status": str(p.get("status") or ""),
        "confidence": str(p.get("confidence") or ""),
        "match_type": str(p.get("matchType") or ""),
    }


def match_opentree(client: httpx.Client, names: list[str]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for i in range(0, len(names), 500):
        batch = names[i : i + 500]
        try:
            r = client.post(
                OPENTREE_TNRS_URL,
                json={"names": batch, "context_name": "Land plants", "do_approximate_matching": False, "include_suppressed": False},
                timeout=60,
            )
            if not r.is_success:
                continue
            payload = r.json()
        except Exception:
            continue
        for result in payload.get("results", []):
            match = (result.get("matches") or [{}])[0]
            taxon = match.get("taxon") or {}
            if taxon.get("ott_id"):
                out[result.get("name", "")] = {
                    "ott_id": str(taxon.get("ott_id") or ""),
                    "accepted_name": str(taxon.get("name") or ""),
                    "rank": str(taxon.get("rank") or "").lower(),
                    "status": "synonym" if match.get("is_synonym") else "matched",
                    "confidence": str(match.get("score") or ""),
                }
    return out


def match_powo(client: httpx.Client, name: str) -> dict[str, str]:
    try:
        r = client.get(POWO_SEARCH_URL, params={"name": name}, timeout=20)
        if not r.is_success:
            return {}
        payload = r.json()
    except Exception:
        return {}
    results = payload.get("results") or []
    if not results:
        return {}
    first = results[0]
    return {
        "powo_id": str(first.get("fqId") or first.get("id") or first.get("url") or ""),
        "accepted_name": str(first.get("name") or ""),
        "rank": str(first.get("rank") or "").lower(),
        "family": str(first.get("family") or ""),
        "genus": str(first.get("genus") or ""),
        "status": str(first.get("taxonomicStatus") or first.get("accepted") or "matched"),
    }


def crosswalk(accepted: pd.DataFrame, crosswalk_limit: int, include_m5: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    attempts = accepted.head(crosswalk_limit).copy()
    if include_m5:
        extra = accepted[accepted["accepted_name"].isin(M5_SEEDS)]
        attempts = pd.concat([attempts, extra], ignore_index=True).drop_duplicates("accepted_taxon_key")
    names = attempts["accepted_name"].tolist()
    gbif: dict[str, dict[str, str]] = {}
    powo: dict[str, dict[str, str]] = {}
    with httpx.Client(headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        ott = match_opentree(client, names)
        for name in names:
            gbif[name] = match_gbif(client, name)
            powo[name] = match_powo(client, name)
            time.sleep(0.02)
    attempted_keys = set(attempts["accepted_taxon_key"])
    rows = []
    gbif_rows = []
    ot_rows = []
    powo_rows = []
    for row in accepted.itertuples(index=False):
        name = row.accepted_name
        g = gbif.get(name, {})
        o = ott.get(name, {})
        p = powo.get(name, {})
        category = "wfo_only_not_attempted"
        confidence = "wfo_anchor_only"
        if row.accepted_taxon_key in attempted_keys:
            names_seen = {normalize_name(name)}
            names_seen |= {normalize_name(x.get("accepted_name", "")) for x in (g, o, p) if x.get("accepted_name")}
            ranks_seen = {str(row.rank).lower()}
            ranks_seen |= {x.get("rank", "") for x in (g, o, p) if x.get("rank")}
            if not (g or o or p):
                category = "no_external_match"
                confidence = "low"
            elif len(names_seen) > 1:
                category = "accepted_name_disagreement"
                confidence = "medium"
            elif len(ranks_seen) > 1:
                category = "rank_disagreement"
                confidence = "medium"
            else:
                category = "matched_name_rank_agreement"
                confidence = "high"
        rows.append(
            {
                "accepted_taxon_key": row.accepted_taxon_key,
                "wfo_id": row.wfo_id,
                "ott_id": o.get("ott_id", ""),
                "powo_id": p.get("powo_id", ""),
                "gbif_taxon_key": g.get("gbif_taxon_key", ""),
                "match_method": "wfo_bulk_anchor_plus_api_name_match" if row.accepted_taxon_key in attempted_keys else "wfo_bulk_anchor_external_not_attempted",
                "normalized_name_key": normalize_name(name),
                "wfo_accepted_name": name,
                "gbif_accepted_name": g.get("accepted_name", ""),
                "opentree_accepted_name": o.get("accepted_name", ""),
                "powo_accepted_name": p.get("accepted_name", ""),
                "wfo_rank": row.rank,
                "gbif_rank": g.get("rank", ""),
                "opentree_rank": o.get("rank", ""),
                "powo_rank": p.get("rank", ""),
                "disagreement_category": category,
                "confidence": confidence,
                "source": "crosswalk",
                "source_identifier": row.wfo_id,
                "access_date": ACCESS_DATE,
                "license": "; ".join(sorted(set(LICENSE.values()))),
                "ingest_clone_id": CLONE_ID,
            }
        )
        if g:
            gbif_rows.append(source_taxon_row("GBIF", g.get("gbif_taxon_key", ""), g, row.accepted_taxon_key))
        if o:
            ot_rows.append(source_taxon_row("OpenTree", o.get("ott_id", ""), o, row.accepted_taxon_key))
        if p:
            powo_rows.append(source_taxon_row("POWO", p.get("powo_id", ""), p, row.accepted_taxon_key))
    return pd.DataFrame(rows), pd.DataFrame(gbif_rows), pd.DataFrame(ot_rows), pd.DataFrame(powo_rows)


def source_taxon_row(source: str, identifier: str, payload: dict[str, str], accepted_key: str) -> dict[str, str]:
    return {
        "source_local_record_id": identifier,
        "accepted_taxon_key": accepted_key,
        "source": source,
        "source_identifier": identifier,
        "accepted_name": payload.get("accepted_name", ""),
        "rank": payload.get("rank", ""),
        "family": payload.get("family", ""),
        "genus": payload.get("genus", ""),
        "species": "",
        "infraspecific_epithet": "",
        "status": payload.get("status", ""),
        "match_type": payload.get("match_type", "name_search"),
        "confidence": payload.get("confidence", ""),
        "access_date": ACCESS_DATE,
        "license": LICENSE[source],
        "ingest_clone_id": CLONE_ID,
    }


def conflicts_from_crosswalk(source_crosswalk: pd.DataFrame) -> pd.DataFrame:
    conflicts = source_crosswalk[~source_crosswalk["disagreement_category"].isin(["matched_name_rank_agreement", "wfo_only_not_attempted"])].copy()
    if conflicts.empty:
        return pd.DataFrame(
            columns=[
                "accepted_taxon_key",
                "conflict_type",
                "disagreement_category",
                "wfo_id",
                "ott_id",
                "powo_id",
                "gbif_taxon_key",
                "evidence",
                "source",
                "source_identifier",
                "access_date",
                "license",
                "ingest_clone_id",
            ]
        )
    conflicts["conflict_type"] = conflicts["disagreement_category"]
    conflicts["evidence"] = conflicts.apply(
        lambda r: json.dumps(
            {
                "wfo": [r["wfo_accepted_name"], r["wfo_rank"]],
                "gbif": [r["gbif_accepted_name"], r["gbif_rank"]],
                "opentree": [r["opentree_accepted_name"], r["opentree_rank"]],
                "powo": [r["powo_accepted_name"], r["powo_rank"]],
            },
            sort_keys=True,
        ),
        axis=1,
    )
    return conflicts[
        [
            "accepted_taxon_key",
            "conflict_type",
            "disagreement_category",
            "wfo_id",
            "ott_id",
            "powo_id",
            "gbif_taxon_key",
            "evidence",
            "source",
            "source_identifier",
            "access_date",
            "license",
            "ingest_clone_id",
        ]
    ].reset_index(drop=True)


def common_names_empty() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "accepted_taxon_key",
            "common_name",
            "language",
            "region",
            "source",
            "source_identifier",
            "access_date",
            "license",
            "ingest_clone_id",
        ]
    )


def write_manifest(out_dir: Path, records: list[dict[str, Any]]) -> None:
    path = out_dir / "raw_manifest.tsv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def make_plot(out_path: Path, counts: dict[str, int], matched_count: int, accepted_count: int) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = list(counts) + ["crosswalk_matched", "tier0_floor"]
    values = [counts[k] for k in counts] + [matched_count, TARGET_FLOOR]
    colors = ["#2f6f4e", "#536878", "#8a6f2a", "#7c4f8f", "#3b6ea8", "#b84e3f"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(labels, values, color=colors[: len(labels)])
    ax.axhline(TARGET_FLOOR, color="#1f2933", linewidth=1.2, linestyle="--", label="Tier 0 floor")
    ax.set_ylabel("Rows / accepted taxa")
    ax.set_title("Taxonomy backbone staging coverage by source")
    ax.tick_params(axis="x", rotation=25)
    ax.text(0.01, 0.95, f"WFO accepted-key rows: {accepted_count:,}", transform=ax.transAxes, va="top")
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def write_audit(out_dir: Path, summary: dict[str, Any]) -> None:
    text = f"""---
created: {now_iso()}
cycle: 2
run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone0
agent: worker
milestone: M1.1
---

# M1.1 Taxonomy Backbone Ingest Audit

## Scope

This branch staged a source-preserving taxonomy backbone for Barrier 1. WFO is the operational accepted-key anchor; this is not a biological adjudication that WFO is correct over GBIF, Open Tree, or POWO.

## Source Access

| source | path used | no-auth result | license / citation note | bulk suitability | staged rows |
|---|---|---:|---|---|---:|
| WFO Plant List | Zenodo static file `wfo_plantlist_2025-12.zip` | yes | {LICENSE['WFO']} | bulk suitable | {summary['row_counts']['wfo_taxa']} |
| GBIF taxonomy | Species match API | yes | {LICENSE['GBIF']} | API-only in this run; full backbone is ~1GB and deferred | {summary['row_counts']['gbif_taxa']} |
| Open Tree taxonomy | TNRS API | yes | {LICENSE['OpenTree']} | API batch suitable for crosswalk samples; bulk TLS path failed locally | {summary['row_counts']['opentree_taxa']} |
| POWO | `api/2/search?name=` JSON endpoint | yes | {LICENSE['POWO']} | conservative sampled API use only; no bulk dump path confirmed | {summary['row_counts']['powo_taxa']} |

## Outputs

| artifact | rows |
|---|---:|
| `accepted_taxa.parquet` | {summary['row_counts']['accepted_taxa']} |
| `synonym_clusters.parquet` | {summary['row_counts']['synonym_clusters']} |
| `common_names.parquet` | {summary['row_counts']['common_names']} |
| `source_crosswalk.parquet` | {summary['row_counts']['source_crosswalk']} |
| `taxonomic_conflicts.parquet` | {summary['row_counts']['taxonomic_conflicts']} |

## Crosswalk Coverage

- Tier 0 floor: {TARGET_FLOOR:,} accepted taxa.
- Accepted taxa staged: {summary['row_counts']['accepted_taxa']:,}.
- API crosswalk attempts: {summary['crosswalk_attempt_limit']:,} WFO accepted names plus prior M5 seed overlap where present.
- Rows with at least one external ID: {summary['crosswalk_rows_with_external_id']:,}.
- Rows without external IDs are retained with explicit null fields, mostly `wfo_only_not_attempted`.

Conflict categories:

{summary['conflict_category_markdown']}

## Provenance And Evidence Scope

Every staged row includes `source`, `source_identifier`, `access_date`, `license`, and `ingest_clone_id`. Synonym rows are marked `name_normalization_only` and cannot support trait, range, edibility, phylogeny, reticulation, or biological-novelty claims.

## Validation

- `tools/taxonomy_backbone_checks.py {out_dir}`: {summary['validation']['taxonomy_backbone_checks']}.
- `python3 -m unittest tests/test_taxonomy_backbone.py`: {summary['validation']['test_taxonomy_backbone']}.
- `python3 -m unittest tests/test_public_taxonomy_sample.py`: {summary['validation']['test_public_taxonomy_sample']}.

## Known Disagreements And Blockers

- POWO: no bulk no-auth dump was confirmed during this clone; API matching is intentionally sampled to avoid aggressive scraping.
- GBIF: full backbone archive is public but ~1GB; this branch used API matching for crosswalk evidence and WFO for scale.
- Open Tree: the public bulk URL probed earlier failed TLS verification locally; TNRS API remained usable.
- Family assignment is inherited from WFO parent traversal and should be checked at Barrier 1 before sibling branches treat it as a join feature.

## Figure

![Taxonomy backbone staging coverage by source and crosswalk completeness relative to the Tier 0 target.](source_row_counts.png)
"""
    (out_dir / "INGEST_AUDIT.md").write_text(text, encoding="utf-8")


def build(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir)
    raw_dir = out_dir / "raw" / "wfo"
    zip_path = raw_dir / "wfo_plantlist_2025-12.zip"
    download(WFO_URL, zip_path, args.refresh)
    taxon, name, synonym, wfo_meta = read_wfo_tables(zip_path)
    accepted, wfo_taxa = make_wfo_records(taxon, name, args.limit)
    if len(accepted) < TARGET_FLOOR and not args.limit:
        raise RuntimeError(f"WFO accepted taxa below Tier 0 floor: {len(accepted)}")
    synonym_clusters = make_wfo_synonyms(synonym, name, set(accepted["accepted_taxon_key"]))
    source_crosswalk, gbif_taxa, opentree_taxa, powo_taxa = crosswalk(accepted, args.crosswalk_limit, include_m5=True)
    taxonomic_conflicts = conflicts_from_crosswalk(source_crosswalk)
    common_names = common_names_empty()

    tables = {
        "wfo_taxa": wfo_taxa,
        "gbif_taxa": gbif_taxa,
        "opentree_taxa": opentree_taxa,
        "powo_taxa": powo_taxa,
        "accepted_taxa": accepted,
        "synonym_clusters": synonym_clusters,
        "common_names": common_names,
        "source_crosswalk": source_crosswalk,
        "taxonomic_conflicts": taxonomic_conflicts,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    for stem, df in tables.items():
        df.to_parquet(out_dir / f"{stem}.parquet", index=False)
        df.to_csv(out_dir / f"{stem}.csv", index=False)

    row_counts = {stem: len(df) for stem, df in tables.items()}
    source_rows = {k: row_counts[k] for k in ("wfo_taxa", "gbif_taxa", "opentree_taxa", "powo_taxa")}
    matched = int((source_crosswalk[["gbif_taxon_key", "ott_id", "powo_id"]] != "").any(axis=1).sum())
    make_plot(out_dir / "source_row_counts.png", source_rows, matched, len(accepted))
    manifest = [
        {
            "source": "WFO",
            "endpoint_or_dump_url": WFO_URL,
            "release_or_version": wfo_meta.get("version", "2025-12"),
            "access_date": ACCESS_DATE,
            "license": LICENSE["WFO"],
            "local_raw_path": str(zip_path),
            "row_count": str(len(taxon) + len(name) + len(synonym)),
            "checksum_sha256": sha256_file(zip_path),
        },
        {
            "source": "GBIF",
            "endpoint_or_dump_url": GBIF_MATCH_URL,
            "release_or_version": "API live read",
            "access_date": ACCESS_DATE,
            "license": LICENSE["GBIF"],
            "local_raw_path": "not cached; normalized API results staged",
            "row_count": str(row_counts["gbif_taxa"]),
            "checksum_sha256": "",
        },
        {
            "source": "OpenTree",
            "endpoint_or_dump_url": OPENTREE_TNRS_URL,
            "release_or_version": "API live read",
            "access_date": ACCESS_DATE,
            "license": LICENSE["OpenTree"],
            "local_raw_path": "not cached; normalized API results staged",
            "row_count": str(row_counts["opentree_taxa"]),
            "checksum_sha256": "",
        },
        {
            "source": "POWO",
            "endpoint_or_dump_url": POWO_SEARCH_URL,
            "release_or_version": "API live read",
            "access_date": ACCESS_DATE,
            "license": LICENSE["POWO"],
            "local_raw_path": "not cached; normalized API results staged",
            "row_count": str(row_counts["powo_taxa"]),
            "checksum_sha256": "",
        },
    ]
    write_manifest(out_dir, manifest)
    conflict_counts = source_crosswalk["disagreement_category"].value_counts().to_dict()
    summary = {
        "created": now_iso(),
        "access_date": ACCESS_DATE,
        "ingest_clone_id": CLONE_ID,
        "row_counts": row_counts,
        "crosswalk_attempt_limit": args.crosswalk_limit,
        "crosswalk_rows_with_external_id": matched,
        "conflict_categories": conflict_counts,
        "conflict_category_markdown": "\n".join(f"- `{k}`: {v}" for k, v in sorted(conflict_counts.items())),
        "validation": {
            "taxonomy_backbone_checks": "not run yet",
            "test_taxonomy_backbone": "not run yet",
            "test_public_taxonomy_sample": "not run yet",
        },
        "artifacts": sorted(str(p.relative_to(out_dir)) for p in out_dir.iterdir() if p.is_file()),
    }
    (out_dir / "build_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_audit(out_dir, summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--limit", type=int, default=None, help="Limit WFO accepted rows for smoke runs")
    parser.add_argument("--crosswalk-limit", type=int, default=500, help="Number of WFO accepted names to crosswalk through API paths")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    summary = build(args)
    print(json.dumps({"row_counts": summary["row_counts"], "crosswalk_rows_with_external_id": summary["crosswalk_rows_with_external_id"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
