#!/usr/bin/env python3
# created: 2026-05-12T07:10:00Z
# cycle: 28
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ATTEST-1

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


def plot_envelope_coverage() -> None:
    schema = read_csv(DATA / "production_attestation_envelope_schema.csv")
    keys = read_csv(DATA / "production_attestation_key_registry.csv")
    replay = read_csv(DATA / "production_attestation_replay_registry.csv")
    labels = ["required\nenvelope fields", "registered\nkey states", "digest\nbindings", "replay\nregistry rows"]
    values = [
        sum(1 for row in schema if row["required"] == "true"),
        len({row["key_state"] for row in keys}),
        3,
        len(replay),
    ]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(labels, values, color=["#377eb8", "#4daf4a", "#984ea3", "#ff7f00"])
    ax.set_ylabel("Covered items")
    ax.set_title("Attestation envelope coverage")
    ax.grid(axis="y", alpha=0.25)
    save(fig, DATA / "production_attestation_envelope_coverage.png")


def plot_failure_modes() -> None:
    failures = read_csv(DATA / "production_attestation_failure_modes.csv")
    labels = [row["failure_category"] for row in failures]
    values = [int(row["invalid_envelope_count"]) for row in failures]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(labels, values, color="#e41a1c")
    ax.set_xlabel("Invalid envelope count")
    ax.set_title("Attestation envelopes fail closed before intake credit")
    ax.grid(axis="x", alpha=0.25)
    save(fig, DATA / "production_attestation_failure_modes.png")


def plot_boundary() -> None:
    rows = read_csv(DATA / "production_attestation_intake_boundary.csv")
    valid_sig = sum(1 for row in rows if row["signature_valid"] == "true")
    mechanical = sum(1 for row in rows if row["attestation_status"] == "mechanically_valid")
    labels = ["signature\nvalid", "mechanically\nvalid", "trusted\nsource", "production\ntrust", "claim\ncredit"]
    values = [valid_sig, mechanical, 0, 0, 0]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(labels, values, color=["#377eb8", "#4daf4a", "#999999", "#999999", "#999999"])
    ax.set_ylim(0, max(values) + 1)
    ax.set_ylabel("Fixture envelopes")
    ax.set_title("Test signature validity is not production trust")
    ax.grid(axis="y", alpha=0.25)
    save(fig, DATA / "production_attestation_boundary.png")


def main() -> None:
    plot_envelope_coverage()
    plot_failure_modes()
    plot_boundary()


if __name__ == "__main__":
    main()
