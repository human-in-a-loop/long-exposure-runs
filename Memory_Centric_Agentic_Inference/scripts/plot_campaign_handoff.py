# created: 2026-05-12T01:25:00Z
# cycle: 22
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-HANDOFF-1

from __future__ import annotations

import csv
import re
import textwrap
from collections import Counter, defaultdict
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


def plot_artifact_dependency_graph(rows: list[dict[str, str]]) -> None:
    by_milestone = Counter(r["milestone"] for r in rows)
    ordered = [m for m in [
        "M-TAX-1", "M-LIFE-1", "M-COST-1", "M-SIM-1", "M-SCHED-1", "M-ARCH-1",
        "M-TRACE-1", "M-QUEUE-1", "M-COMP-1", "M-PROTO-1", "M-CALIB-1", "M-SEC-1",
        "M-SYNTH-1", "M-EXP-1", "M-ENERGY-1", "M-SECOPS-1", "M-PLAN-1",
        "M-ABI-1", "M-ABIINT-1", "M-ARCHPKG-1", "M-DC12-1", "M-PRODTELEM-1",
        "M-FINALPKG-1", "M-HANDOFF-1",
    ] if m in by_milestone]
    counts = [by_milestone[m] for m in ordered]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.plot(range(len(ordered)), counts, marker="o", color="#4C78A8", linewidth=2)
    ax.fill_between(range(len(ordered)), counts, color="#4C78A8", alpha=0.18)
    for i in range(len(ordered) - 1):
        ax.annotate("", xy=(i + 0.85, counts[i + 1]), xytext=(i + 0.15, counts[i]), arrowprops={"arrowstyle": "->", "color": "#666666", "lw": 0.8})
    ax.set_xticks(range(len(ordered)), ordered, rotation=45, ha="right")
    ax.set_ylabel("tracked artifacts")
    ax.set_title("Milestone and artifact dependency structure")
    ax.grid(axis="y", alpha=0.25)
    save(DATA / "handoff_artifact_dependency_graph.png")


def plot_claim_traceability_coverage(rows: list[dict[str, str]]) -> None:
    labels = ["data_artifacts", "narrative_artifacts", "validation_sources", "figures", "limitation_named"]
    counts = []
    for label in labels:
        if label == "limitation_named":
            counts.append(sum(1 for r in rows if r.get(label, "").strip()))
        else:
            counts.append(sum(1 for r in rows if r.get(label, "").strip() and all((ROOT / p.strip()).exists() for p in r[label].split(";") if p.strip())))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.bar(labels, counts, color=["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#72B7B2"])
    ax.set_ylim(0, max(counts) + 2)
    ax.set_ylabel("claims covered")
    ax.set_title("Claim traceability coverage across data, narrative, tests, figures, and limitations")
    ax.set_xticks(range(len(labels)), labels, rotation=20, ha="right")
    for bar, value in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.2, str(value), ha="center", va="bottom")
    save(DATA / "handoff_claim_traceability_coverage.png")


def plot_experiment_upgrade_path(rows: list[dict[str, str]]) -> None:
    rows = rows[:8]
    claims = sorted({
        claim
        for r in rows
        for claim in re.findall(r"CL-\d{3}", r.get("claim_upgrade_path", ""))
    })
    if not claims:
        claims = ["CL-002", "CL-003", "CL-004", "CL-005", "CL-012"]
    matrix = []
    for row in rows:
        linked = set(re.findall(r"CL-\d{3}", row.get("claim_upgrade_path", "")))
        matrix.append([1 if claim in linked else 0 for claim in claims])
    fig, ax = plt.subplots(figsize=(11.5, 6.0))
    im = ax.imshow(matrix, cmap="YlGnBu", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(claims)), claims)
    ylabels = [
        f"{r['rank']}. " + "\n".join(textwrap.wrap(r["open_question"], width=34, max_lines=2, placeholder="..."))
        for r in rows
    ]
    ax.set_yticks(range(len(rows)), ylabels)
    ax.set_title("Production experiments mapped to claim upgrade and falsification paths")
    ax.set_xlabel("Claims that the experiment could update")
    ax.set_ylabel("Production experiment")
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, "✓" if value else "", ha="center", va="center", color="black", fontsize=11)
    cbar = fig.colorbar(im, ax=ax, label="claim can be updated", fraction=0.04, pad=0.03)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["no", "yes"])
    save(DATA / "handoff_experiment_upgrade_path.png")


def main() -> None:
    plot_artifact_dependency_graph(read_csv(DATA / "handoff_artifact_index.csv"))
    plot_claim_traceability_coverage(read_csv(DATA / "handoff_claim_traceability.csv"))
    plot_experiment_upgrade_path(read_csv(DATA / "handoff_open_questions.csv"))


if __name__ == "__main__":
    main()
