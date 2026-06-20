#!/usr/bin/env python3
# created: 2026-05-12T09:15:00Z
# cycle: 30
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-GATECHAIN-1
"""Plot evidence gatechain replay coverage and quarantine boundaries."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
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
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def plot_state_coverage() -> None:
    schema = read_csv(DATA / "evidence_gatechain_state_schema.csv")
    rows = read_csv(DATA / "evidence_gatechain_valid_fixture_paths.csv") + read_csv(DATA / "evidence_gatechain_invalid_fixture_paths.csv")
    paths_by_state: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row["state_id"]:
            paths_by_state[row["state_id"]].add(row["path_id"])
    states = [row["state_id"] for row in schema]
    counts = [len(paths_by_state[state]) for state in states]
    colors = ["#2f6f73" if state != "production_claim_credit_allowed" else "#9f3a38" for state in states]
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.barh(states, counts, color=colors)
    ax.set_xlabel("fixture paths exercising state")
    ax.set_title("Evidence gatechain state coverage")
    ax.invert_yaxis()
    save(fig, DATA / "evidence_gatechain_state_coverage.png")


def plot_quarantine_reasons() -> None:
    rows = read_csv(DATA / "evidence_gatechain_quarantine_reasons.csv")
    labels = [row["quarantine_category"] + "\n" + row["blocked_reason"] for row in rows]
    counts = [int(row["path_count"]) for row in rows]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.bar(range(len(rows)), counts, color="#7a5c2e")
    ax.set_xticks(range(len(rows)), labels, rotation=45, ha="right")
    ax.set_ylabel("path count")
    ax.set_title("Fail-closed quarantine reasons")
    save(fig, DATA / "evidence_gatechain_quarantine_reasons.png")


def plot_claim_boundary() -> None:
    rows = read_csv(DATA / "evidence_gatechain_replay_results.csv")
    blocked = Counter(row["blocked_at_state"] or "not_blocked" for row in rows)
    labels = list(blocked)
    counts = [blocked[label] for label in labels]
    colors = ["#396a9f" if label != "production_ingestion_accepted" else "#9f3a38" for label in labels]
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.bar(labels, counts, color=colors)
    ax.set_ylabel("path count")
    ax.set_title("Claim-credit boundary by blocked transition")
    ax.tick_params(axis="x", rotation=35)
    ax.text(0.02, 0.94, "All current fixture/proxy/synthetic paths: claim_credit_allowed=false", transform=ax.transAxes, fontsize=9)
    save(fig, DATA / "evidence_gatechain_claim_boundary.png")


def main() -> None:
    plot_state_coverage()
    plot_quarantine_reasons()
    plot_claim_boundary()


if __name__ == "__main__":
    main()
