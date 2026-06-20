# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone0
# agent: worker
# milestone: M1.1
"""Checks for PhytoGraph M1.1 taxonomy backbone staging outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_PROVENANCE = {"source", "source_identifier", "access_date", "license", "ingest_clone_id"}
ACCEPTED_COLUMNS = {
    "accepted_taxon_key",
    "wfo_id",
    "accepted_name",
    "rank",
    "family",
    "genus",
    "species",
    "infraspecific_epithet",
    *REQUIRED_PROVENANCE,
}
CROSSWALK_COLUMNS = {
    "accepted_taxon_key",
    "wfo_id",
    "ott_id",
    "powo_id",
    "gbif_taxon_key",
    "match_method",
    "normalized_name_key",
    "disagreement_category",
    "confidence",
    *REQUIRED_PROVENANCE,
}


def read_table(base: Path, name: str) -> pd.DataFrame:
    path = base / f"{name}.parquet"
    if not path.exists():
        raise AssertionError(f"missing {path}")
    return pd.read_parquet(path)


def require_columns(df: pd.DataFrame, cols: set[str], name: str) -> None:
    missing = cols - set(df.columns)
    if missing:
        raise AssertionError(f"{name} missing columns: {sorted(missing)}")


def check_base(base: Path, *, min_accepted: int = 50_000) -> list[str]:
    accepted = read_table(base, "accepted_taxa")
    crosswalk = read_table(base, "source_crosswalk")
    synonyms = read_table(base, "synonym_clusters")
    conflicts = read_table(base, "taxonomic_conflicts")

    require_columns(accepted, ACCEPTED_COLUMNS, "accepted_taxa")
    require_columns(crosswalk, CROSSWALK_COLUMNS, "source_crosswalk")
    if len(accepted) < min_accepted:
        raise AssertionError(f"accepted_taxa below floor: {len(accepted)} < {min_accepted}")
    if accepted["accepted_taxon_key"].duplicated().any():
        raise AssertionError("accepted_taxon_key is not unique")
    if accepted["wfo_id"].duplicated().any():
        raise AssertionError("wfo_id is not unique in accepted_taxa")
    if len(crosswalk) != len(accepted):
        raise AssertionError(f"source_crosswalk rows {len(crosswalk)} != accepted rows {len(accepted)}")
    for table_name in (
        "wfo_taxa",
        "gbif_taxa",
        "opentree_taxa",
        "powo_taxa",
        "accepted_taxa",
        "synonym_clusters",
        "common_names",
        "source_crosswalk",
        "taxonomic_conflicts",
    ):
        table = read_table(base, table_name)
        if table.empty:
            continue
        require_columns(table, REQUIRED_PROVENANCE, table_name)
        for col in REQUIRED_PROVENANCE:
            if table[col].fillna("").eq("").any():
                raise AssertionError(f"{table_name} has missing provenance column {col}")
    if not set(crosswalk["accepted_taxon_key"]).issubset(set(accepted["accepted_taxon_key"])):
        raise AssertionError("source_crosswalk has orphan accepted keys")
    if not synonyms.empty:
        if not set(synonyms["accepted_taxon_key"]).issubset(set(accepted["accepted_taxon_key"])):
            raise AssertionError("synonym_clusters has orphan accepted keys")
        if not synonyms["task_visibility"].eq("name_normalization_only").all():
            raise AssertionError("synonym rows must remain name_normalization_only")
    if "disagreement_category" not in conflicts.columns:
        raise AssertionError("taxonomic_conflicts missing disagreement_category")
    if not (base / "raw_manifest.tsv").exists():
        raise AssertionError("missing raw_manifest.tsv")
    if not (base / "source_row_counts.png").exists():
        raise AssertionError("missing source_row_counts.png")
    if not (base / "INGEST_AUDIT.md").exists():
        raise AssertionError("missing INGEST_AUDIT.md")
    return [
        f"accepted_taxa={len(accepted)}",
        f"source_crosswalk={len(crosswalk)}",
        f"synonym_clusters={len(synonyms)}",
        f"taxonomic_conflicts={len(conflicts)}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", nargs="?", default="substrate/staging/taxonomy_backbone")
    parser.add_argument("--min-accepted", type=int, default=50_000)
    args = parser.parse_args()
    messages = check_base(Path(args.base), min_accepted=args.min_accepted)
    print("OK " + " ".join(messages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
