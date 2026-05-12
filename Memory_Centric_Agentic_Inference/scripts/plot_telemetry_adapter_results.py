#!/usr/bin/env python3
# created: 2026-05-12T04:30:00Z
# cycle: 25
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ADAPTER-1

from __future__ import annotations

import csv
from collections import Counter
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


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def split_fields(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def plot_coverage() -> None:
    interface = read_csv(DATA / "telemetry_adapter_interface.csv")
    counts = [len(split_fields(row["emitted_schema_fields"])) for row in interface]
    labels = [row["collector_category"].replace(" counters", "").replace(" and ", "\n") for row in interface]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(range(len(labels)), counts, color="#377eb8")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Schema fields emitted")
    ax.set_title("Adapter stream coverage by required collector class")
    ax.grid(axis="y", alpha=0.25)
    save(fig, DATA / "telemetry_adapter_stream_coverage.png")


def plot_failures() -> None:
    join = read_csv(DATA / "telemetry_adapter_join_results.csv")
    failures = Counter(row["blocked_reason"].split(":")[0] for row in join if row["blocked_reason"])
    labels = list(failures)
    values = [failures[label] for label in labels]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(labels, values, color="#e41a1c")
    ax.set_xlabel("Invalid fixture cases")
    ax.set_title("Join and preflight failure modes")
    ax.grid(axis="x", alpha=0.25)
    save(fig, DATA / "telemetry_adapter_join_failures.png")


def plot_boundary() -> None:
    rows = read_csv(DATA / "telemetry_adapter_claim_boundary.csv")
    labels = [row["boundary_id"] for row in rows]
    calibrated = [1 if row["production_calibrated"] == "true" else 0 for row in rows]
    ready = [1 if row["production_ready"] == "true" else 0 for row in rows]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(labels, [1] * len(labels), label="synthetic fixture boundary", color="#4daf4a")
    ax.bar(labels, calibrated, label="production calibrated", color="#984ea3")
    ax.bar(labels, ready, label="production ready", color="#ff7f00", alpha=0.8)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Allowed state")
    ax.set_title("Fixture adapters stop before production calibration")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(loc="upper right")
    save(fig, DATA / "telemetry_adapter_claim_boundary.png")


def main() -> None:
    plot_coverage()
    plot_failures()
    plot_boundary()


if __name__ == "__main__":
    main()
