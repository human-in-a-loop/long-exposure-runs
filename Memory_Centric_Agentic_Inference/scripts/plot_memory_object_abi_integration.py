#!/usr/bin/env python3
# created: 2026-05-12T20:10:00Z
# cycle: 41
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ABIINT-1
"""Plot ABI-to-runtime/planner integration replay outputs."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def as_int(value: str) -> int:
    return int(float(value or 0))


def save(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    print(f"wrote {path.relative_to(ROOT)}")


def plot_actions() -> None:
    rows = read_csv(DATA / "memory_object_abi_integration_results.csv")
    labels = [row["case_id"].replace("_", "\n") for row in rows]
    runtime = [as_int(row["runtime_action_count"]) for row in rows]
    planner = [as_int(row["planner_action_count"]) for row in rows]
    colors = ["#4c78a8" if row["abi_status"] == "accepted" else "#e45756" for row in rows]
    x = range(len(rows))
    plt.figure(figsize=(12, 4.8))
    plt.bar([i - 0.18 for i in x], runtime, width=0.36, label="runtime actions", color=colors)
    plt.bar([i + 0.18 for i in x], planner, width=0.36, label="planner actions", color="#72b7b2")
    plt.axhline(0, color="#333333", linewidth=0.8)
    plt.xticks(list(x), labels, rotation=0, fontsize=7)
    plt.ylabel("emitted action count")
    plt.title("ABI integration action emission: rejected rows stay at zero")
    plt.legend()
    save(DATA / "memory_object_abi_integration_actions.png")


def plot_boundary() -> None:
    rows = read_csv(DATA / "memory_object_abi_option_boundary.csv")
    status_order = {"allowed_opaque": 2, "allowed_object_actions": 1, "blocked_before_actions": 0}
    option_order = {
        "A_conventional_request_model_kv_serving": 0,
        "B_memory_object_aware_runtime": 1,
        "C_trajectory_dag_memory_fabric": 2,
    }
    x = [option_order[row["selected_option"]] for row in rows]
    y = [status_order[row["boundary_result"]] for row in rows]
    colors = ["#54a24b" if row["boundary_result"] != "blocked_before_actions" else "#e45756" for row in rows]
    plt.figure(figsize=(8, 4.8))
    plt.scatter(x, y, s=90, color=colors)
    for xi, yi, row in zip(x, y, rows):
        plt.text(xi + 0.03, yi + 0.03, row["case_id"], fontsize=7)
    plt.xticks([0, 1, 2], ["A opaque", "B object ABI", "C DAG ABI"])
    plt.yticks([0, 1, 2], ["blocked", "object actions", "opaque allowed"])
    plt.ylim(-0.4, 2.5)
    plt.title("Option boundary under opaque, admitted, and rejected ABI states")
    save(DATA / "memory_object_abi_option_boundary.png")


def plot_failures() -> None:
    rows = read_csv(DATA / "memory_object_abi_integration_failure_modes.csv")
    labels = [row["failure_mode"].replace("_", "\n") for row in rows]
    counts = [as_int(row["blocked_case_count"]) for row in rows]
    downstream = [as_int(row["downstream_memory_action_count"]) for row in rows]
    x = range(len(rows))
    plt.figure(figsize=(10, 4.8))
    plt.bar(x, counts, color="#e45756", label="blocked cases")
    plt.plot(x, downstream, marker="o", color="#111111", label="downstream memory actions")
    plt.xticks(list(x), labels, fontsize=7)
    plt.ylabel("count")
    plt.title("Fail-closed integration reasons before action emission")
    plt.legend()
    save(DATA / "memory_object_abi_integration_failures.png")


def main() -> None:
    plot_actions()
    plot_boundary()
    plot_failures()


if __name__ == "__main__":
    main()
