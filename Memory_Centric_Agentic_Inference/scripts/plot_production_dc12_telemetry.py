#!/usr/bin/env python3
# created: 2026-05-11T23:40:00Z
# cycle: 20
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODTELEM-1
"""Plot production-shaped DC-001/DC-002 telemetry ingestion results."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA = DATA / "production_dc12_telemetry_schema.csv"
RESULTS = DATA / "production_dc12_ingestion_results.csv"
REPLAY = DATA / "production_dc12_threshold_replay.csv"
CLAIMS = DATA / "production_dc12_claim_update_matrix.csv"

OUT_COVERAGE = DATA / "production_dc12_telemetry_coverage.png"
OUT_REPLAY = DATA / "production_dc12_threshold_replay.png"
OUT_CLAIMS = DATA / "production_dc12_claim_gate_matrix.png"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def fnum(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "") or 0.0)
    except ValueError:
        return 0.0


def save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def plot_coverage(schema: list[dict[str, str]], results: list[dict[str, str]]) -> None:
    required = sum(1 for row in schema if row["required"] == "true")
    optional = len(schema) - required
    reasons = Counter(row["blocked_reason"] or "passed" for row in results)
    labels = ["required fields", "optional fields"] + list(reasons)
    values = [required, optional] + [reasons[label] for label in reasons]
    colors = ["#4c78a8", "#72b7b2"] + ["#54a24b" if label == "passed" else "#b84a4a" for label in reasons]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("count")
    ax.set_title("Production DC-001/DC-002 telemetry coverage and fail-closed reasons")
    ax.tick_params(axis="x", rotation=25)
    save(fig, OUT_COVERAGE)


def plot_replay(replay: list[dict[str, str]]) -> None:
    labels = [row["fixture_id"] for row in replay]
    measured = [fnum(row, "measured_value") for row in replay]
    thresholds = [fnum(row, "threshold_value") for row in replay]
    fig, ax = plt.subplots(figsize=(13, 6))
    x = range(len(labels))
    ax.bar([i - 0.18 for i in x], measured, width=0.36, label="synthetic measured value", color="#4c78a8")
    ax.bar([i + 0.18 for i in x], thresholds, width=0.36, label="existing threshold/noise floor", color="#d18f2f")
    ax.set_xticks(list(x), labels, rotation=35, ha="right")
    ax.set_yscale("symlog", linthresh=1e-8)
    ax.set_ylabel("joules/byte for DC-001; us or threshold units for DC-002")
    ax.set_title("Production-shaped DC-001/DC-002 threshold replay")
    ax.legend()
    save(fig, OUT_REPLAY)


def plot_claims(results: list[dict[str, str]], claims: list[dict[str, str]]) -> None:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in results:
        key = row["evidence_label"]
        if row["production_calibrated"] == "true":
            grouped[key]["production_calibrated"] += 1
        elif row["calibration_candidate"] == "true":
            grouped[key]["candidate_only"] += 1
        elif row["security_credit_allowed"] == "false":
            grouped[key]["security_blocked"] += 1
        else:
            grouped[key]["blocked_or_control"] += 1
    statuses = ["candidate_only", "blocked_or_control", "security_blocked", "production_calibrated"]
    labels = sorted(grouped)
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = [0] * len(labels)
    colors = {
        "candidate_only": "#4c78a8",
        "blocked_or_control": "#b84a4a",
        "security_blocked": "#8f5aa8",
        "production_calibrated": "#54a24b",
    }
    for status in statuses:
        vals = [grouped[label][status] for label in labels]
        ax.bar(labels, vals, bottom=bottom, label=status, color=colors[status])
        bottom = [a + b for a, b in zip(bottom, vals)]
    ax.set_ylabel("fixture rows")
    ax.set_title(f"Claim gate matrix: {len(claims)} claim rows remain non-production-calibrated")
    ax.legend()
    save(fig, OUT_CLAIMS)


def main() -> None:
    plot_coverage(read_csv(SCHEMA), read_csv(RESULTS))
    plot_replay(read_csv(REPLAY))
    plot_claims(read_csv(RESULTS), read_csv(CLAIMS))


if __name__ == "__main__":
    main()
