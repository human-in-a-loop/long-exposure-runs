#!/usr/bin/env python3
"""Track 5 ethnobotanical sovereignty-field audit.
Verifies that ethnobotanical assertions in the enrichment projection retain the
required sovereignty fields: people_or_region (or its substrate-canonical placeholder),
source_id, license, access_date.

Required outcome: zero missing-required-field rows across all source provenance groups.
Any nonzero row count is fail-loud.
"""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5" / "data"

REQUIRED_FIELDS = ["people_or_region", "source_id", "license", "access_date"]


def main() -> int:
    enr = pd.read_parquet(T5 / "track5_enrichment_edges.parquet")
    ethno = enr[enr["edge_type"] == "ethnobotanical_use_assertion"].copy()
    parsed = ethno["sovereignty_fields_json"].apply(lambda s: json.loads(s) if isinstance(s, str) and s else {})
    rows = []
    for source, grp_idx in ethno.groupby("source_id").groups.items():
        grp = ethno.loc[grp_idx]
        sub_parsed = parsed.loc[grp_idx]
        missing = {f: 0 for f in REQUIRED_FIELDS}
        for i, sov in sub_parsed.items():
            row = grp.loc[i]
            field_vals = {
                "people_or_region": sov.get("people_or_region"),
                "source_id": row["source_id"],
                "license": row["license"],
                "access_date": row["access_date"],
            }
            for f, v in field_vals.items():
                if v is None or (isinstance(v, str) and not v.strip()):
                    missing[f] += 1
        rows.append({
            "source_id": source,
            "n_ethno_rows": len(grp),
            **{f"missing_{f}": missing[f] for f in REQUIRED_FIELDS},
            "total_missing_field_failures": sum(missing.values()),
        })
    audit = pd.DataFrame(rows)
    audit.to_csv(T5 / "sovereignty_field_audit.tsv", sep="\t", index=False)
    total_missing = int(audit[[f"missing_{f}" for f in REQUIRED_FIELDS]].values.sum())
    print(audit.to_string(index=False))
    print(f"TOTAL missing sovereignty fields across enrichment ethno rows: {total_missing}")
    return 0 if total_missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
