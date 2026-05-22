#!/usr/bin/env python3
"""Plot Track 5 non-Duke temporal chemistry reopen coverage.

created: 2026-05-18T18:05:00+00:00
cycle: 25
run_id: run-phytograph-cycle25-track5-non-duke-temporal-chemistry-reopen
agent: worker
milestone: _plan/track5-non-duke-temporal-chemistry-reopen
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track5" / "data"


def main() -> int:
    out = Path(os.environ["FIGURE_OUT"])
    diagnostics = pd.read_csv(DATA / "track5_reopen_source_diagnostics.tsv", sep="\t")
    diagnostics = diagnostics.sort_values("candidate_rows", ascending=True)

    labels = diagnostics["source_name"].str.replace("Dr. Duke Phytochemical and Ethnobotanical Databases", "Dr. Duke", regex=False)
    y = range(len(diagnostics))

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.barh(y, diagnostics["candidate_rows"], color="#9ca3af", label="candidate rows")
    ax.barh(y, diagnostics["accepted_key_rows"], color="#2563eb", label="accepted-key rows")
    ax.barh(y, diagnostics["dated_rows"], color="#16a34a", label="dated rows")
    ax.barh(y, diagnostics["non_duke_rows"], color="#c2410c", label="non-Duke rows")
    ax.set_yticks(list(y), labels)
    ax.set_xlabel("rows (log scale)")
    ax.set_xscale("symlog", linthresh=1)
    ax.set_title("Track 5 reopen chemistry evidence coverage")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    for idx, row in enumerate(diagnostics.to_dict("records")):
        ax.text(max(float(row["candidate_rows"]), 1.0), idx, f"  dated={row['dated_rows']}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
