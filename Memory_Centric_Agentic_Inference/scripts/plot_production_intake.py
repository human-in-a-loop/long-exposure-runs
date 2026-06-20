#!/usr/bin/env python3
# created: 2026-05-12T06:10:00Z
# cycle: 27
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-INTAKE-1

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


def plot_manifest_coverage() -> None:
    schema = read_csv(DATA / "production_intake_bundle_manifest_schema.csv")
    valid = read_csv(DATA / "production_intake_valid_bundle_manifest.csv")
    custody = read_csv(DATA / "production_intake_chain_of_custody_requirements.csv")
    labels = ["manifest\nsections", "required\nfields", "payload\nstreams", "custody\nrequirements"]
    values = [len({r["manifest_section"] for r in schema}), len(schema), len(valid), len(custody)]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(labels, values, color=["#377eb8", "#4daf4a", "#984ea3", "#ff7f00"])
    ax.set_ylabel("Covered items")
    ax.set_title("Production intake manifest coverage")
    ax.grid(axis="y", alpha=0.25)
    save(fig, DATA / "production_intake_manifest_coverage.png")


def plot_failure_modes() -> None:
    failures = read_csv(DATA / "production_intake_failure_modes.csv")
    labels = [r["failure_category"] for r in failures]
    values = [int(r["invalid_bundle_count"]) for r in failures]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(labels, values, color="#e41a1c")
    ax.set_xlabel("Invalid bundle count")
    ax.set_title("Intake bundles fail closed before ingestion")
    ax.grid(axis="x", alpha=0.25)
    save(fig, DATA / "production_intake_failure_modes.png")


def plot_boundary() -> None:
    rows = read_csv(DATA / "production_intake_downstream_boundary.csv")
    admissible = sum(1 for r in rows if r["admission_status"] == "structurally_admissible")
    labels = ["structural\nadmission", "production\ntarget granted", "production\ncalibrated", "production\nready", "claim\ncredit"]
    values = [admissible, 0, 0, 0, 0]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(labels, values, color=["#4daf4a", "#999999", "#999999", "#999999", "#999999"])
    ax.set_ylim(0, max(1, admissible) + 0.5)
    ax.set_ylabel("Fixture bundles allowed")
    ax.set_title("Intake admission is not production calibration")
    ax.grid(axis="y", alpha=0.25)
    save(fig, DATA / "production_intake_boundary.png")


def main() -> None:
    plot_manifest_coverage()
    plot_failure_modes()
    plot_boundary()


if __name__ == "__main__":
    main()
