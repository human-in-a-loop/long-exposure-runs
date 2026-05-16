# created: 2026-05-16T03:25:00Z
# cycle: 17
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M6-final-synthesis

"""Render final M6 summary figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
LADDER_OUT = ROOT / "reports/figures/final_campaign_evidence_ladder.png"
BOTTLENECK_OUT = ROOT / "reports/figures/final_bottleneck_map.png"


def setup_axes(ax):
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def rounded_box(ax, xy, width, height, text, face, edge="#2f3a45", fontsize=9):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.015",
        linewidth=1.0,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#18212b",
        wrap=True,
    )


def arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops={"arrowstyle": "->", "lw": 1.2, "color": "#405261"},
    )


def draw_ladder():
    fig, ax = plt.subplots(figsize=(12, 6.8))
    setup_axes(ax)
    ax.set_title(
        "Final campaign evidence ladder",
        fontsize=16,
        fontweight="bold",
        loc="left",
        pad=12,
    )
    ax.text(
        0.02,
        0.92,
        "Validated campaign ladder from paper reconstruction through proof ledgers, probes, certification, and extension benchmark.",
        fontsize=10,
        color="#44515c",
    )

    nodes = [
        (0.04, 0.72, "M1\npaper map\nreconstructed", "#d7ecff"),
        (0.22, 0.72, "M2\nproof ledger\nloss map", "#d9f2e3"),
        (0.40, 0.72, "M3\ntoy probes\nnumerical", "#fff1c7"),
        (0.58, 0.72, "M4\nfinite identity\ncertified", "#eadfff"),
        (0.76, 0.72, "M5\nfixed vs growing\nproved toy", "#f8d7da"),
    ]
    for x, y, label, color in nodes:
        rounded_box(ax, (x, y), 0.14, 0.13, label, color, fontsize=9)
    for x in [0.18, 0.36, 0.54, 0.72]:
        arrow(ax, x, 0.785, x + 0.04, 0.785)

    rounded_box(
        ax,
        (0.31, 0.42),
        0.38,
        0.12,
        "M6 final synthesis\nclaim ledger + artifact index + audit packet",
        "#e8ecef",
        fontsize=10,
    )
    arrow(ax, 0.47, 0.72, 0.47, 0.54)

    evidence = [
        ("reconstructed", "Theorem statements, proof architecture, exponent/loss ledgers"),
        ("certified/proved toy", "Finite labelled-template expectation identity and exact expansions"),
        ("numerical evidence", "Permutation, quotient, labelled-embedding, polynomial-window, Schreier probes"),
        ("negative findings", "Naive composite intersections, rare Monte Carlo events, deferred direct transfers"),
        ("non-claims", "No improved Kim--Tao exponent; imported MPvH/Nau/MP23 remain imported"),
    ]
    y = 0.30
    for label, detail in evidence:
        ax.text(0.08, y, label, fontsize=10, fontweight="bold", color="#24313c")
        ax.text(0.28, y, detail, fontsize=9.5, color="#364753")
        y -= 0.055

    fig.tight_layout()
    LADDER_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(LADDER_OUT, dpi=180)
    plt.close(fig)


def draw_bottleneck():
    fig, ax = plt.subplots(figsize=(12, 7.2))
    setup_axes(ax)
    ax.set_title(
        "Proof bottleneck and toy-mechanism map",
        fontsize=16,
        fontweight="bold",
        loc="left",
        pad=12,
    )
    ax.text(
        0.02,
        0.92,
        "Proof-side loss sources and evidence-side mechanism analogues, highlighting polynomial/interpolation derivative amplification.",
        fontsize=10,
        color="#44515c",
    )

    left = [
        ("Proposition 3.1\nvariance", "q^{2kappa} Markov loss\n+ smoothing derivative budget"),
        ("Weyl law\nto rigidity", "grid/Chebyshev probability\n+ edge inversion alpha_R < 2 alpha_W/3"),
        ("Theorem 2\nfourth moment", "S diagonal subtraction\n+ q^{4kappa}, fiber union, Sobolev"),
    ]
    right = [
        ("Fixed templates", "normalized expansions tame\n(e.g. cyclic = 1, rank2 = 1 - 9x + ...)"),
        ("Growing profiles", "zeros/poles move to x=0\nat radius scale 1/L"),
        ("Mechanism benchmark", "derivatives amplify without claiming\nhyperbolic exponent improvement"),
    ]

    ax.text(0.08, 0.84, "Kim--Tao proof reconstruction", fontsize=12, fontweight="bold", color="#24313c")
    ax.text(0.60, 0.84, "Campaign evidence analogue", fontsize=12, fontweight="bold", color="#24313c")

    ys = [0.67, 0.47, 0.27]
    for (title, detail), y in zip(left, ys):
        rounded_box(ax, (0.06, y), 0.30, 0.12, f"{title}\n{detail}", "#d9f2e3", fontsize=9)
    for (title, detail), y in zip(right, ys):
        rounded_box(ax, (0.61, y), 0.31, 0.12, f"{title}\n{detail}", "#fff1c7", fontsize=9)
    for y in ys:
        arrow(ax, 0.36, y + 0.06, 0.61, y + 0.06)

    rounded_box(
        ax,
        (0.37, 0.08),
        0.25,
        0.10,
        "Strongest contribution:\nreproducible toy benchmark for interpolation loss",
        "#f8d7da",
        fontsize=9.5,
    )
    arrow(ax, 0.765, 0.27, 0.50, 0.18)

    fig.tight_layout()
    BOTTLENECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(BOTTLENECK_OUT, dpi=180)
    plt.close(fig)


def main() -> int:
    draw_ladder()
    draw_bottleneck()
    print(f"wrote {LADDER_OUT.relative_to(ROOT)}")
    print(f"wrote {BOTTLENECK_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
