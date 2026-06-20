#!/usr/bin/env python3
# created: 2026-05-12T05:30:00Z
# cycle: 26
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PORT-1

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


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def split_fields(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def plot_coverage() -> None:
    schema = read_csv(DATA / "production_dc12_telemetry_schema.csv")
    contract = read_csv(DATA / "adapter_conformance_contract.csv")
    aliases = read_csv(DATA / "adapter_join_alias_map.csv")
    profiles = read_csv(DATA / "adapter_backend_profile_fixtures.csv")
    values = [
        sum(1 for row in schema if row["required"] == "true"),
        len({row["profile_class"] for row in profiles}),
        len(aliases),
        sum(1 for row in aliases if row["accepted_aliases"]),
    ]
    labels = ["required\nschema fields", "stream\nclasses", "join\nkeys", "logical\naliases"]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(labels, values, color=["#377eb8", "#4daf4a", "#984ea3", "#ff7f00"])
    ax.set_ylabel("Covered items")
    ax.set_title("Adapter conformance coverage")
    ax.grid(axis="y", alpha=0.25)
    ax.text(0.5, max(values) * 0.82, f"contract rows: {len(contract)}", ha="center")
    save(fig, DATA / "adapter_conformance_coverage.png")


def plot_failures() -> None:
    failures = read_csv(DATA / "adapter_conformance_failure_modes.csv")
    labels = [row["failure_category"] for row in failures]
    values = [int(row["invalid_profile_count"]) for row in failures]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(labels, values, color="#e41a1c")
    ax.set_xlabel("Invalid backend-shaped profile count")
    ax.set_title("Conformance failures fail closed")
    ax.grid(axis="x", alpha=0.25)
    save(fig, DATA / "adapter_conformance_failures.png")


def plot_boundary() -> None:
    rows = read_csv(DATA / "adapter_conformance_ingestion_boundary.csv")
    labels = ["conformance\npass", "production\ntarget", "production\ncalibrated", "production\nready", "claim\ncredit"]
    pass_count = sum(1 for row in rows if row["conformance_status"] == "pass")
    values = [pass_count, 0, 0, 0, 0]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(labels, values, color=["#4daf4a", "#999999", "#999999", "#999999", "#999999"])
    ax.set_ylim(0, max(1, pass_count) + 0.5)
    ax.set_ylabel("Fixture rows allowed")
    ax.set_title("Conformance remains pre-production")
    ax.grid(axis="y", alpha=0.25)
    save(fig, DATA / "adapter_conformance_boundary.png")


def main() -> None:
    plot_coverage()
    plot_failures()
    plot_boundary()


if __name__ == "__main__":
    main()
