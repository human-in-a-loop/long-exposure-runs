# created: 2026-05-17T17:35:00Z
# cycle: 2
# run_id: fork-e34b5b2c1c6c-clone-5
# agent: worker
# milestone: M1.7
"""Render a family-by-source assertion-density heatmap for M1.7."""

from __future__ import annotations

import csv
import math
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "substrate" / "staging" / "chemodiversity_ethnobotany_sources"


def short_source(name: str) -> str:
    return (
        name.replace("Dr. Duke Phytochemical and Ethnobotanical Databases", "Dr. Duke")
        .replace("Native American Ethnobotany Database (Moerman), NAEB mirror", "Moerman/NAEB")
    )


def main() -> None:
    out_path = Path(os.environ.get("FIGURE_OUT", OUT / "source_bias_heatmap.png"))
    with (OUT / "family_source_matrix.tsv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))

    family_totals: dict[str, int] = {}
    sources = sorted({r["source_name"] for r in rows})
    for row in rows:
        family_totals[row["family_raw"]] = family_totals.get(row["family_raw"], 0) + int(row["total_assertions"])

    families = [family for family, _count in sorted(family_totals.items(), key=lambda item: item[1], reverse=True)[:25]]
    values = [[0.0 for _ in sources] for _ in families]
    row_lookup = {(r["family_raw"], r["source_name"]): r for r in rows}
    for i, family in enumerate(families):
        for j, source in enumerate(sources):
            row = row_lookup.get((family, source))
            if row:
                values[i][j] = math.log10(1 + int(row["total_assertions"]))

    width = max(9, 1.2 * len(sources))
    height = max(7, 0.32 * len(families) + 2.5)
    fig, ax = plt.subplots(figsize=(width, height), constrained_layout=True)
    image = ax.imshow(values, aspect="auto", cmap="viridis")
    ax.set_yticks(range(len(families)))
    ax.set_yticklabels(families)
    ax.set_xticks(range(len(sources)))
    ax.set_xticklabels([short_source(s) for s in sources], rotation=35, ha="right")
    ax.set_xlabel("Source")
    ax.set_ylabel("Family")
    ax.set_title("M1.7 family-by-source assertion density")
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("log10(1 + phytochemical + ethnobotanical assertions)")
    fig.savefig(out_path, dpi=160)
    print(out_path)


if __name__ == "__main__":
    main()
