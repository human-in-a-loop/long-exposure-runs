# created: 2026-05-17T18:08:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
# agent: worker
# milestone: M1.3

"""Render the M1.3 source-acquisition scale-gap closure matrix."""

from __future__ import annotations

from pathlib import Path


OUT = Path("substrate/staging/reticulation_sources/plots/m1_3_scale_gap_closure_matrix.png")


def main() -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    routes = [
        "CCDB\nmaintainer/export",
        "Plant DNA\nC-values export",
        "Wood-style\nsupplements",
        "Curated event\ntable",
    ]
    risks = ["Access", "License", "Parse"]
    # 0=low, 1=medium, 2=high. Values encode current blocker severity, not source quality.
    matrix = np.array(
        [
            [2, 1, 1],
            [1, 1, 1],
            [2, 2, 1],
            [1, 1, 1],
        ]
    )
    count_close = [30000, 2000, 0, 0]
    event_close = [0, 0, 500, 2000]

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10, 4.8), gridspec_kw={"width_ratios": [1.15, 1.0]})
    im = ax.imshow(matrix, cmap="YlOrRd", vmin=0, vmax=2)
    ax.set_xticks(range(len(risks)), risks)
    ax.set_yticks(range(len(routes)), routes)
    ax.set_title("Current route risk")
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            ax.text(x, y, ["low", "med", "high"][matrix[y, x]], ha="center", va="center", fontsize=9)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_ticks([0, 1, 2], labels=["low", "medium", "high"])

    y = np.arange(len(routes))
    ax2.barh(y - 0.18, count_close, height=0.36, label="count rows")
    ax2.barh(y + 0.18, event_close, height=0.36, label="event/evidence rows")
    ax2.axvline(30000, color="#4c78a8", linestyle="--", linewidth=1, label="count floor")
    ax2.axvline(2000, color="#f58518", linestyle=":", linewidth=1.5, label="event floor")
    ax2.set_yticks(y, routes)
    ax2.set_xscale("symlog", linthresh=100)
    ax2.set_xlabel("Plausible floor contribution, symlog rows")
    ax2.set_title("Floor closure potential")
    ax2.legend(fontsize=8, loc="lower right")

    fig.suptitle("M1.3 scale-gap closure matrix")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160)
    plt.close(fig)
    print(OUT.as_posix())


if __name__ == "__main__":
    main()
