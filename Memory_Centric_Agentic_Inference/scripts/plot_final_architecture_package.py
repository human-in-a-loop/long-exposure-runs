# created: 2026-05-12T00:45:00Z
# cycle: 21
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-FINALPKG-1

from __future__ import annotations

import csv
from collections import Counter
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


def plot_claim_heatmap(rows: list[dict[str, str]]) -> None:
    labels = ["validated_mechanism", "synthetic_supported", "host_local_proxy_only", "contract_ready", "production_calibration_required", "production_ready", "blocked"]
    gates = ["production_ready", "fail_closed_without_production_target", "production_target_seen"]
    counts = Counter((r["readiness_label"], r["gate_status"]) for r in rows)
    matrix = [[counts[(label, gate)] for gate in gates] for label in labels]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    im = ax.imshow(matrix, cmap="viridis")
    ax.set_xticks(range(len(gates)), gates, rotation=25, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_title("Claim readiness by evidence class and gate status")
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, str(value), ha="center", va="center", color="white" if value else "black")
    fig.colorbar(im, ax=ax, label="claim count")
    save(DATA / "final_claim_readiness_heatmap.png")


def plot_option_readiness(rows: list[dict[str, str]]) -> None:
    labels = [r["workload_class"] for r in rows]
    options = [r["option"] for r in rows]
    readiness_score = {
        "validated_mechanism": 2,
        "synthetic_supported": 1,
        "host_local_proxy_only": 1,
        "contract_ready": 1.5,
        "production_calibration_required": 0.5,
        "production_ready": 3,
        "blocked": 0,
    }
    values = [readiness_score.get(r["readiness_label"], 0) for r in rows]
    colors = {"A": "#4C78A8", "B": "#F58518", "C": "#54A24B"}
    fig, ax = plt.subplots(figsize=(10, 4.8))
    bars = ax.bar(labels, values, color=[colors.get(o, "#777777") for o in options])
    ax.set_ylabel("readiness score")
    ax.set_title("Option A/B/C readiness under workload regimes and blockers")
    ax.set_ylim(0, 3.2)
    ax.set_xticks(range(len(labels)), labels, rotation=25, ha="right")
    for bar, row in zip(bars, rows):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f"{row['option']} / {row['readiness_label']}", ha="center", va="bottom", fontsize=8, rotation=90)
    save(DATA / "final_architecture_option_readiness.png")


def plot_experiment_priority(rows: list[dict[str, str]]) -> None:
    rows = sorted(rows, key=lambda r: int(r["rank"]))[:8]
    labels = [r["experiment"] for r in rows]
    scores = [int(float(r["priority_score"])) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    y = list(range(len(rows)))
    ax.barh(y, scores, color="#B279A2")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("priority score")
    ax.set_title("Ranked production experiments by claim impact and unresolved empirical boundary")
    for idx, score in enumerate(scores):
        ax.text(score + 0.1, idx, str(score), va="center")
    save(DATA / "final_production_experiment_priority.png")


def main() -> None:
    plot_claim_heatmap(read_csv(DATA / "final_claim_readiness_matrix.csv"))
    plot_option_readiness(read_csv(DATA / "final_architecture_option_readiness.csv"))
    plot_experiment_priority(read_csv(DATA / "final_production_experiment_backlog.csv"))


if __name__ == "__main__":
    main()
