#!/usr/bin/env python3
# created: 2026-05-12T03:06:00Z
# cycle: 23
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODDEPLOY-1

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    print(path.relative_to(ROOT))


def plot_join_graph(rows: list[dict[str, str]]) -> None:
    center = (0.0, 0.0)
    nodes = [
        ("run_id", (-2.8, 1.8)),
        ("interval_id", (0.0, 2.25)),
        ("workload_id", (2.8, 1.8)),
        ("object_id", (3.0, -0.4)),
        ("topology_id", (0.0, -2.25)),
        ("tenant_id", (-3.0, -0.4)),
        ("security_context_id", (-1.6, -1.7)),
    ]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter([center[0]], [center[1]], s=1600, color="#4C78A8")
    ax.text(*center, "DC-001/DC-002\nreplay row", color="white", ha="center", va="center", weight="bold")
    colors = ["#F58518", "#54A24B", "#B279A2", "#E45756", "#72B7B2", "#FF9DA6", "#9D755D"]
    for idx, (label, xy) in enumerate(nodes):
        ax.scatter([xy[0]], [xy[1]], s=1100, color=colors[idx])
        ax.text(*xy, label, ha="center", va="center", fontsize=9, weight="bold")
        ax.annotate("", xy=center, xytext=xy, arrowprops={"arrowstyle": "->", "color": "#555555", "lw": 1.4})
    ax.set_title("Production telemetry join keys for power, bytes, latency, workload/object, topology, tenant, and security logs")
    ax.set_axis_off()
    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(-3.0, 3.0)
    save(DATA / "production_telemetry_join_graph.png")


def plot_preflight_matrix(rows: list[dict[str, str]]) -> None:
    categories = []
    impacts = []
    for row in rows:
        if row["collector_category"] not in categories:
            categories.append(row["collector_category"])
        for impact in row["claim_impact"].split(";"):
            impact = impact.strip()
            if impact and impact not in impacts:
                impacts.append(impact)
    impacts = [i for i in impacts if i != "all"] + (["all"] if "all" in impacts else [])
    matrix = [[0 for _ in impacts] for _ in categories]
    for row in rows:
        y = categories.index(row["collector_category"])
        row_impacts = [i.strip() for i in row["claim_impact"].split(";") if i.strip()]
        if "all" in row_impacts:
            row_impacts = impacts
        for impact in row_impacts:
            if impact in impacts:
                matrix[y][impacts.index(impact)] += 1
    fig, ax = plt.subplots(figsize=(10, 5.5))
    im = ax.imshow(matrix, cmap="magma")
    ax.set_xticks(range(len(impacts)), impacts, rotation=30, ha="right")
    ax.set_yticks(range(len(categories)), categories)
    ax.set_title("Preflight fail-closed checks by collector category and claim impact")
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, str(value), ha="center", va="center", color="white" if value else "black")
    fig.colorbar(im, ax=ax, label="blocking checks")
    save(DATA / "production_telemetry_preflight_matrix.png")


def plot_pilot_scope(rows: list[dict[str, str]]) -> None:
    labels = [f"{r['pilot_step']}. {r['scope']}" for r in rows]
    option_counts = [len([o for o in r["architecture_options"].split(";") if o.strip()]) for r in rows]
    collector_counts = [len([c for c in r["minimum_collectors"].split(";") if c.strip()]) for r in rows]
    y = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.barh([v - 0.18 for v in y], option_counts, height=0.35, label="architecture options covered", color="#4C78A8")
    ax.barh([v + 0.18 for v in y], collector_counts, height=0.35, label="minimum collector groups", color="#F58518")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("count")
    ax.set_title("Minimal pilot coverage to test Option A vs B/C without production endorsement")
    ax.legend(loc="lower right")
    save(DATA / "production_telemetry_pilot_scope.png")


def main() -> None:
    plot_join_graph(read_csv(DATA / "production_telemetry_join_contract.csv"))
    plot_preflight_matrix(read_csv(DATA / "production_telemetry_preflight_checks.csv"))
    plot_pilot_scope(read_csv(DATA / "production_telemetry_pilot_design.csv"))


if __name__ == "__main__":
    main()
