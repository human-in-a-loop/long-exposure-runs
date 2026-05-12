#!/usr/bin/env python3
# created: 2026-05-12T08:10:00Z
# cycle: 29
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRUSTPOL-1

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


def plot_coverage() -> None:
    schema = read_csv(DATA / "operator_trust_policy_schema.csv")
    lifecycle = read_csv(DATA / "operator_key_lifecycle_matrix.csv")
    replacement = read_csv(DATA / "operator_attestation_replacement_map.csv")
    counts = Counter(row["policy_dimension"] for row in schema)
    labels = ["trust\nroot", "key\ncustody", "collector\nidentity", "telemetry\nbinding", "replay", "tenant /\nsecurity", "audit", "replacement\nmap"]
    values = [
        counts["trust_root"],
        counts["key_custody"] + counts["key_lifecycle"] + len(lifecycle),
        counts["collector_identity"],
        counts["telemetry_binding"],
        counts["replay_protection"],
        counts["tenant_security"],
        counts["auditability"],
        len(replacement),
    ]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, values, color=["#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628", "#f781bf", "#999999", "#e41a1c"])
    ax.set_ylabel("Covered controls")
    ax.set_title("Operator trust policy coverage")
    ax.grid(axis="y", alpha=0.25)
    save(fig, DATA / "operator_trust_policy_coverage.png")


def plot_failures() -> None:
    failures = read_csv(DATA / "operator_trust_policy_failure_modes.csv")
    rows = [row for row in failures if int(row["invalid_profile_count"]) > 0]
    labels = [row["failure_category"] for row in rows]
    values = [int(row["invalid_profile_count"]) for row in rows]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(labels, values, color="#e41a1c")
    ax.set_xlabel("Invalid policy profiles")
    ax.set_title("Operator trust policy failures fail closed")
    ax.grid(axis="x", alpha=0.25)
    save(fig, DATA / "operator_trust_policy_failures.png")


def plot_boundary() -> None:
    rows = read_csv(DATA / "operator_trust_policy_boundary.csv")
    labels = ["mechanically\nvalid", "policy\nadmissible", "trusted\nsource", "production\ntrust", "production\nready"]
    values = [
        sum(1 for row in rows if row["mechanically_valid_signature"] == "true"),
        sum(1 for row in rows if row["trust_policy_admissible"] == "true"),
        sum(1 for row in rows if row["attestation_source_trusted"] == "true"),
        sum(1 for row in rows if row["production_trust_established"] == "true"),
        sum(1 for row in rows if row["production_ready"] == "true"),
    ]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(labels, values, color=["#377eb8", "#4daf4a", "#999999", "#999999", "#999999"])
    ax.set_ylabel("Policy profiles")
    ax.set_title("Policy admissibility is not production claim readiness")
    ax.grid(axis="y", alpha=0.25)
    save(fig, DATA / "operator_trust_policy_boundary.png")


def main() -> None:
    plot_coverage()
    plot_failures()
    plot_boundary()


if __name__ == "__main__":
    main()
