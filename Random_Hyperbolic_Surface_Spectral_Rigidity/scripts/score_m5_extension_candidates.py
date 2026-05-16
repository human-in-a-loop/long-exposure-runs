# created: 2026-05-15T23:45:00Z
# cycle: 13
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M5-extension-candidates

"""Generate Cycle 13 M5 extension-candidate scores and matrix figure."""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "extension_candidates" / "m5_candidate_scores.csv"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    title: str
    mathematical_value: int
    tractability: int
    evidence_strength: int
    dependency_risk: int
    next_test_clarity: int
    rank: int
    decision: str


CANDIDATES = [
    Candidate(
        "C1",
        "Markov/interpolation-loss sharpening",
        5,
        4,
        5,
        3,
        5,
        1,
        "advance-primary",
    ),
    Candidate(
        "C2",
        "Exact labelled-template polynomial expansion",
        4,
        5,
        5,
        1,
        5,
        2,
        "advance-technical-lemma",
    ),
    Candidate(
        "C3",
        "Delocalization-side improvement",
        4,
        3,
        3,
        3,
        3,
        3,
        "advance-secondary",
    ),
    Candidate(
        "C4",
        "Schreier spectral-window benchmark",
        3,
        4,
        4,
        2,
        4,
        4,
        "advance-benchmark",
    ),
    Candidate(
        "C5",
        "Tree closed-walk moment certification",
        2,
        5,
        3,
        1,
        4,
        5,
        "defer-supporting",
    ),
    Candidate(
        "C6",
        "Direct Weil-Petersson transfer",
        5,
        1,
        1,
        5,
        1,
        6,
        "reject-defer",
    ),
    Candidate(
        "C7",
        "Full Selberg trace formalization",
        4,
        1,
        2,
        5,
        1,
        7,
        "reject-defer",
    ),
]


def write_csv(path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "candidate_id",
        "title",
        "mathematical_value",
        "tractability",
        "evidence_strength",
        "dependency_risk",
        "next_test_clarity",
        "rank",
        "decision",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for candidate in sorted(CANDIDATES, key=lambda c: c.rank):
            writer.writerow(candidate.__dict__)


def plot_matrix(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(CANDIDATES, key=lambda c: c.rank)
    metrics = [
        ("mathematical_value", "Value"),
        ("tractability", "Tractability"),
        ("evidence_strength", "Evidence"),
        ("dependency_risk", "Dependency risk"),
        ("next_test_clarity", "Next test"),
    ]
    data = np.array([[getattr(c, key) for key, _ in metrics] for c in ordered], dtype=float)

    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    image = ax.imshow(data, cmap="viridis", vmin=1, vmax=5, aspect="auto")
    ax.set_xticks(range(len(metrics)), [label for _, label in metrics], rotation=25, ha="right")
    ax.set_yticks(
        range(len(ordered)),
        [f"{c.rank}. {c.candidate_id} {c.title}" for c in ordered],
    )
    ax.set_title("M5 extension candidate matrix")
    ax.set_xlabel("Score axis, 1=low and 5=high")
    ax.set_ylabel("Ranked candidate")

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = int(data[i, j])
            color = "white" if value <= 2 else "black"
            ax.text(j, i, str(value), ha="center", va="center", color=color, fontsize=10)

    cbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("Score")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main() -> None:
    out = Path(os.environ.get("FIGURE_OUT", ROOT / "reports" / "figures" / "m5_extension_candidate_matrix.png"))
    write_csv()
    plot_matrix(out)
    print(f"wrote {CSV_PATH.relative_to(ROOT)}")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
