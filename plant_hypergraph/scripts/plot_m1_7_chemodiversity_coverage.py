# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: fork-e34b5b2c1c6c-clone-5
# agent: worker
# milestone: M1.7
"""Plot M1.7 per-source coverage summary."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "substrate" / "staging" / "chemodiversity_ethnobotany_sources"


def main() -> None:
    out_path = Path(os.environ.get("FIGURE_OUT", OUT / "source_coverage_bar.png"))
    with (OUT / "source_coverage_summary.tsv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    rows = [r for r in rows if int(r["phytochemical_assertions"]) or int(r["ethnobotanical_assertions"])]
    labels = [r["source_name"].replace("Dr. Duke Phytochemical and Ethnobotanical Databases", "Dr. Duke").replace("Native American Ethnobotany Database (Moerman), NAEB mirror", "Moerman/NAEB") for r in rows]
    phyto = [int(r["phytochemical_assertions"]) for r in rows]
    ethno = [int(r["ethnobotanical_assertions"]) for r in rows]
    taxa = [int(r["distinct_taxa"]) for r in rows]
    compounds = [int(r["distinct_compounds"]) for r in rows]

    x = range(len(rows))
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    series = [
        ("Phytochemical assertions", phyto, "#3b6ea8"),
        ("Ethnobotanical assertions", ethno, "#8f5b2e"),
        ("Distinct taxa", taxa, "#4f8a5b"),
        ("Distinct compounds", compounds, "#7a4f9a"),
    ]
    for ax, (title, values, color) in zip(axes.flat, series):
        ax.bar(x, values, color=color)
        ax.set_title(title)
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, rotation=25, ha="right")
        ax.set_ylabel("Rows / distinct count")
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("M1.7 source coverage against staging floors")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    print(out_path)


if __name__ == "__main__":
    main()
