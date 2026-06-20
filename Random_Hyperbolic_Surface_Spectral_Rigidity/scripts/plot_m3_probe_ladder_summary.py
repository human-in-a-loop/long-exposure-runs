# created: 2026-05-15T22:25:00Z
# cycle: 11
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M3-computational-probes

import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


STAGES = [
    (
        "Fixed points",
        "common fixed points",
        "cyclic powers order one",
        "composite words collapse",
    ),
    (
        "Folded profiles",
        "trajectory quotient",
        "rank/cyclicity separated",
        "rare events remain sparse",
    ),
    (
        "Labelled embeddings",
        "injective quotient maps",
        "rank-two stable after normalization",
        "expectation toy",
    ),
    (
        "Polynomial windows",
        "count vs x = 1/n",
        "degree-3 stable; high degree unstable",
        "conditioning diagnostic",
    ),
    (
        "Schreier spectra",
        "adjacency spectral windows",
        "coarse windows concentrate",
        "not hyperbolic Laplacian",
    ),
]


def main() -> None:
    out = os.environ.get("FIGURE_OUT", "reports/figures/m3_probe_ladder_summary.png")
    fig, ax = plt.subplots(figsize=(14, 4.8))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    colors = ["#ece7f2", "#d0d1e6", "#a6bddb", "#67a9cf", "#1c9099"]
    xs = [0.03, 0.225, 0.42, 0.615, 0.81]
    width = 0.16
    height = 0.58

    for idx, (x, stage, color) in enumerate(zip(xs, STAGES, colors), start=1):
        title, observable, signal, limit = stage
        box = FancyBboxPatch(
            (x, 0.22),
            width,
            height,
            boxstyle="round,pad=0.018,rounding_size=0.02",
            linewidth=1.4,
            edgecolor="#263238",
            facecolor=color,
        )
        ax.add_patch(box)
        ax.text(x + width / 2, 0.72, f"{idx}. {title}", ha="center", va="center", fontsize=11, weight="bold")
        ax.text(x + width / 2, 0.59, f"Observable:\n{observable}", ha="center", va="center", fontsize=9)
        ax.text(x + width / 2, 0.43, f"Stable signal:\n{signal}", ha="center", va="center", fontsize=9)
        ax.text(x + width / 2, 0.29, f"Limitation:\n{limit}", ha="center", va="center", fontsize=8.5)

    labels = [
        "adds quotient\nstructure",
        "counts embeddings\ndirectly",
        "fits reciprocal\nwindows",
        "projects to\noperator statistic",
    ]
    for i, label in enumerate(labels):
        start = (xs[i] + width + 0.01, 0.51)
        end = (xs[i + 1] - 0.01, 0.51)
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, linewidth=1.2, color="#37474f"))
        ax.text((start[0] + end[0]) / 2, 0.61, label, ha="center", va="center", fontsize=8, color="#37474f")

    ax.text(
        0.5,
        0.93,
        "M3 computational ladder: from random-permutation constraints to a Schreier operator toy",
        ha="center",
        va="center",
        fontsize=14,
        weight="bold",
    )
    ax.text(
        0.5,
        0.08,
        "Validated scope: reproducible finite toy benchmark suite and mechanism analogue; not a verification of hyperbolic spectral rigidity.",
        ha="center",
        va="center",
        fontsize=10,
        color="#37474f",
    )

    fig.tight_layout()
    fig.savefig(out, dpi=180)


if __name__ == "__main__":
    main()
