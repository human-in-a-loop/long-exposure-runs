#!/usr/bin/env python3
# created: 2026-05-12T18:10:00Z
# cycle: 39
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CLAIMEXP-1
"""Plot claim expiry and revalidation outputs."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

RESULTS = DATA / "claim_expiry_results.csv"
FAILURES = DATA / "claim_expiry_failure_modes.csv"
REVALIDATION = DATA / "claim_expiry_revalidation_boundary.csv"

OUT_TIMELINE = DATA / "claim_expiry_timeline.png"
OUT_FAILURES = DATA / "claim_expiry_failure_modes.png"
OUT_REVALIDATION = DATA / "claim_expiry_revalidation_boundary.png"

STATUS_COLOR = {
    "currently_supportable": "#31a354",
    "revalidation_required": "#fdae6b",
    "expired": "#d95f0e",
    "invalidated_by_change": "#756bb1",
    "not_production_supported": "#636363",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def plot_timeline(rows: list[dict[str, str]]) -> None:
    ordered = rows
    y = range(len(ordered))
    colors = [STATUS_COLOR[row["observed_status"]] for row in ordered]
    ages = [float(row["age_hours"]) for row in ordered]
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.barh(y, ages, color=colors)
    ax.axvline(168, color="#222222", linestyle="--", linewidth=1, label="TTL boundary (expired at age >= TTL)")
    ax.set_yticks(y)
    ax.set_yticklabels([row["case_id"] for row in ordered], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("evidence age (hours)")
    ax.set_title("Claim-support lifecycle state over age and drift probes")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_TIMELINE, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_TIMELINE.relative_to(ROOT)}")


def plot_failures(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda row: int(row["count"]), reverse=True)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.barh(range(len(ordered)), [int(row["count"]) for row in ordered], color="#d95f0e")
    ax.set_yticks(range(len(ordered)))
    ax.set_yticklabels([row["failure_mode"] for row in ordered], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("probe count")
    ax.set_title("Claim expiry and revalidation failure modes")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_FAILURES, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_FAILURES.relative_to(ROOT)}")


def plot_revalidation(rows: list[dict[str, str]]) -> None:
    counts = Counter("fresh replay required" if row["fresh_production_replay_required"] == "true" else "fresh replay not required" for row in rows)
    labels = list(counts)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(labels, [counts[label] for label in labels], color=["#fdae6b" if "required" in label else "#31a354" for label in labels])
    ax.set_ylabel("probe cases")
    ax.set_title("Fresh replay boundary versus stale or changed deployment")
    ax.grid(axis="y", alpha=0.25)
    ax.text(
        0.5,
        -0.18,
        "Old replay copies are never accepted as revalidation evidence.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(OUT_REVALIDATION, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_REVALIDATION.relative_to(ROOT)}")


def main() -> None:
    plot_timeline(read_csv(RESULTS))
    plot_failures(read_csv(FAILURES))
    plot_revalidation(read_csv(REVALIDATION))


if __name__ == "__main__":
    main()
