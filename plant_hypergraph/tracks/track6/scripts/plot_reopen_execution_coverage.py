#!/usr/bin/env python3
"""Plot Track 6 local model execution reopen coverage.

created: 2026-05-18T19:05:00+00:00
cycle: 26
run_id: run-phytograph-cycle26-track6-local-model-execution-reopen
agent: worker
milestone: _plan/track6-local-model-execution-reopen
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track6" / "data"


def main() -> int:
    out = Path(os.environ["FIGURE_OUT"])
    diagnostics = pd.read_csv(DATA / "local_model_probe_scoring_diagnostics.tsv", sep="\t")
    diagnostics = diagnostics.sort_values("category")

    x = range(len(diagnostics))
    width = 0.26
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar([i - width for i in x], diagnostics["static_benchmark_questions"], width, label="static benchmark questions", color="#64748b")
    ax.bar(x, diagnostics["runnable_response_count"], width, label="runnable responses", color="#2563eb")
    ax.bar([i + width for i in x], diagnostics["scored_response_count"], width, label="scored responses", color="#16a34a")
    ax.set_xticks(list(x), diagnostics["category"], rotation=30, ha="right")
    ax.set_ylabel("count")
    ax.set_title("Track 6 reopen local model execution coverage")
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    for idx, row in enumerate(diagnostics.to_dict("records")):
        ax.text(idx - width, float(row["static_benchmark_questions"]) + 0.6, str(row["static_benchmark_questions"]), ha="center", fontsize=8)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
