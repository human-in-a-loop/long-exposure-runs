# created: 2026-05-13T07:32:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-SYNTH-2

"""Build Phase 2 downgrade synthesis artifacts.

Consumes validated M-CAL-1, M-WORKLOAD-1, and M-SWBASE-2 outputs, then emits
a claim matrix, compact JSON summary, evidence-status PNG, and human-readable
downgrade note. No new hardware model is introduced here.
"""

from __future__ import annotations

import csv
import json
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"

STATUS_COLORS = {
    "preserved": (62, 142, 88),
    "weakened": (226, 158, 54),
    "falsified": (200, 72, 72),
    "superseded": (96, 108, 190),
    "open": (128, 128, 128),
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def claim_rows() -> list[dict[str, str]]:
    return [
        {
            "claim_id": "C1",
            "claim": "Full dense frontier weights remain anti-targets for permanent fixed hardware.",
            "phase1_status": "rejected",
            "phase2_status": "preserved",
            "evidence_level": "modeled",
            "supporting_artifacts": "physicalized-weights/docs/target_ranking.md; physicalized-weights/data/calibrated_breakeven_summary.json; physicalized-weights/data/stronger_baseline_summary.json",
            "reopen_condition": "Measured long-lived dense model deployment with slow update cadence, high utilization, and lower total cost than optimized software and programmable accelerators under identical serving workload.",
        },
        {
            "claim_id": "C2",
            "claim": "Analog or in-memory broad physicalization remains speculative without device calibration.",
            "phase1_status": "speculative",
            "phase2_status": "preserved",
            "evidence_level": "speculative",
            "supporting_artifacts": "physicalized-weights/docs/taxonomy_and_null.md; physicalized-weights/data/calibrated_breakeven_summary.json",
            "reopen_condition": "Device-calibrated data for drift, conversion overhead, precision, yield, repair, retention, and system integration that beats the same programmable baselines.",
        },
        {
            "claim_id": "C3",
            "claim": "Safety/filter classifier is a credible target for bounded architecture and failure-mode study.",
            "phase1_status": "supported",
            "phase2_status": "weakened",
            "evidence_level": "inferred",
            "supporting_artifacts": "physicalized-weights/docs/hybrid_safety_filter_architecture.md; physicalized-weights/docs/prototype_verification_closure.md; physicalized-weights/data/workload_summary.json",
            "reopen_condition": "Production traces showing stable high effective fast-path volume, low fallback, monthly-or-slower policy updates, bounded audit and feature costs, and durable utilization.",
        },
        {
            "claim_id": "C4",
            "claim": "Safety/filter classifier physicalization is a performance or economic winner over strong programmable baselines.",
            "phase1_status": "provisionally_supported",
            "phase2_status": "falsified",
            "evidence_level": "modeled",
            "supporting_artifacts": "physicalized-weights/data/stronger_baseline_summary.json; physicalized-weights/data/stronger_baseline_comparison.csv; physicalized-weights/docs/stronger_baseline_comparison.md",
            "reopen_condition": "Identical-workload production measurement where hybrid physicalized safety/filter wins at least one durable high-volume regime after feature extraction, audit logging, fallback, updates, utilization, and programmable accelerator costs are charged.",
        },
        {
            "claim_id": "C5",
            "claim": "Hybrid architecture with fallback, audit, update, health, drift, and rollback controls remains useful.",
            "phase1_status": "supported",
            "phase2_status": "preserved",
            "evidence_level": "simulated",
            "supporting_artifacts": "physicalized-weights/docs/hybrid_safety_filter_architecture.md; physicalized-weights/data/hybrid_arch_summary.json; physicalized-weights/docs/prototype_safety_filter.md",
            "reopen_condition": "Reopen only if control-plane invariants fail under richer traces, mutable policy logic enters the fixed block, or fallback/audit paths cannot be made reliable.",
        },
        {
            "claim_id": "C6",
            "claim": "Programmable accelerator is the strongest current baseline for the tested safety/filter workload.",
            "phase1_status": "baseline",
            "phase2_status": "preserved",
            "evidence_level": "modeled",
            "supporting_artifacts": "physicalized-weights/data/stronger_baseline_summary.json; physicalized-weights/data/stronger_baseline_comparison.csv",
            "reopen_condition": "Measured accelerator implementation performs worse than modeled across the same feature, audit, fallback, update, and utilization conditions while hybrid costs remain bounded.",
        },
        {
            "claim_id": "C7",
            "claim": "Effective fast-path volume, not raw request volume, controls fixed-substrate viability.",
            "phase1_status": "implicit",
            "phase2_status": "preserved",
            "evidence_level": "modeled",
            "supporting_artifacts": "physicalized-weights/data/workload_viability_overlay.csv; physicalized-weights/docs/workload_trace_assumptions.md",
            "reopen_condition": "Production traces show raw request volume remains predictive even after fallback, near-threshold, stale-policy, drift, audit-failure, and fail-safe routing are accounted for.",
        },
        {
            "claim_id": "C8",
            "claim": "Measured production traces are required before promoting a physicalized safety/filter product claim.",
            "phase1_status": "recommended",
            "phase2_status": "preserved",
            "evidence_level": "inferred",
            "supporting_artifacts": "physicalized-weights/data/calibrated_breakeven_summary.json; physicalized-weights/data/workload_summary.json; physicalized-weights/data/stronger_baseline_summary.json",
            "reopen_condition": "The claim is satisfied, not reopened, by production traces with feature extraction cost, audit cost, fallback rate, accelerator energy and latency, update cadence, and utilization.",
        },
        {
            "claim_id": "C9",
            "claim": "Phase 1 safety/filter target ranking remains a sufficient reason to claim hardware superiority.",
            "phase1_status": "supported",
            "phase2_status": "superseded",
            "evidence_level": "modeled",
            "supporting_artifacts": "physicalized-weights/data/target_scores_summary.json; physicalized-weights/data/stronger_baseline_summary.json",
            "reopen_condition": "A new target-ranking pass must include stronger-baseline replay or measured production baselines before superiority language can return.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["claim_id", "claim", "phase1_status", "phase2_status", "evidence_level", "supporting_artifacts", "reopen_condition"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_png(path: Path, rows: list[dict[str, str]]) -> None:
    width, height = 900, 460
    image = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(width, x1), min(height, y1)
        for y in range(y0, y1):
            row = y * width * 3
            for x in range(x0, x1):
                image[row + x * 3 : row + x * 3 + 3] = bytes(color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                image[(y0 * width + x0) * 3 : (y0 * width + x0) * 3 + 3] = bytes(color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    rect(0, 0, width, 80, (34, 44, 58))
    rect(60, 110, 840, 120, (215, 215, 215))
    x_step = 780 // max(1, len(rows) - 1)
    for idx, row in enumerate(rows):
        x = 60 + idx * x_step
        y = 230
        if idx:
            line(60 + (idx - 1) * x_step, y, x, y, (190, 190, 190))
        color = STATUS_COLORS[row["phase2_status"]]
        rect(x - 26, y - 70, x + 26, y - 18, color)
        rect(x - 20, y - 64, x + 20, y - 24, (255, 255, 255))
        rect(x - 15, y - 59, x + 15, y - 29, color)
        rect(x - 26, y + 18, x + 26, y + 70, color)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["phase2_status"]] = counts.get(row["phase2_status"], 0) + 1
    x = 90
    for status, color in STATUS_COLORS.items():
        h = counts.get(status, 0) * 28
        rect(x, 410 - h, x + 90, 410, color)
        x += 150

    raw = b"".join(b"\x00" + image[y * width * 3 : (y + 1) * width * 3] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def write_doc(path: Path, summary: dict, rows: list[dict[str, str]]) -> None:
    status_counts = summary["phase2_status_counts"]
    text = f"""---
created: 2026-05-13T07:32:00Z
cycle: 2
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-SYNTH-2
---

# Phase 2 Synthesis Downgrade

Under current calibrated assumptions and equal workload accounting, hybrid physicalized safety/filter wins zero workload scenarios. The stronger programmable accelerator wins nine of ten scenarios, and optimized software wins the zero-invocation control. The prior Phase 1 safety/filter result is therefore preserved only as an architectural and failure-mode study, not as a performance or economic superiority claim.

## Claim Status

Phase 2 status counts: `{json.dumps(status_counts, sort_keys=True)}`. The safety/filter performance/economic claim is `falsified`; the target-ranking superiority language is `superseded`; the bounded hybrid control-plane design is `preserved`.

| claim | Phase 1 status | Phase 2 status | evidence | reopen condition |
|---|---:|---:|---:|---|
"""
    for row in rows:
        text += f"| {row['claim']} | {row['phase1_status']} | {row['phase2_status']} | {row['evidence_level']} | {row['reopen_condition']} |\n"
    text += f"""
## Phase 2 Evidence

- `M-CAL-1`: calibrated hybrid winner share `{summary['calibrated_hybrid_winner_share']}` and decision `{summary['calibrated_safety_filter_decision']}`.
- `M-WORKLOAD-1`: workload classifications `{json.dumps(summary['workload_classification_counts'], sort_keys=True)}`.
- `M-SWBASE-2`: winner counts `{json.dumps(summary['stronger_baseline_winner_counts'], sort_keys=True)}`; hybrid workload wins `{summary['hybrid_workload_wins']}`.
- Formerly preserved high-volume stable moderation case winner: `{summary['preserved_case_winner']}` with decision `{summary['preserved_case_decision_class']}`.

![Phase 1 and Phase 2 claim statuses, showing which claims were preserved, weakened, falsified, or superseded after calibrated workload and stronger-baseline replay.](../data/phase2_evidence_map.png)

## Reopening Standard

The physicalized safety/filter performance case can reopen only with measured production evidence under identical workload accounting: request volume, accepted fast-path volume, fallback and near-threshold frequency, policy update cadence, audit logging cost, feature extraction cost, utilization, accelerator energy and latency, and operational failure behavior must all be charged to the competing alternatives. A reopened claim must show a durable positive hybrid margin against optimized software and the programmable accelerator, not just a lower isolated dot-product cost.
"""
    path.write_text(text)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    calibrated = read_json(DATA / "calibrated_breakeven_summary.json")
    workload = read_json(DATA / "workload_summary.json")
    stronger = read_json(DATA / "stronger_baseline_summary.json")
    comparison = read_csv(DATA / "stronger_baseline_comparison.csv")
    rows = claim_rows()
    status_counts = {status: sum(1 for row in rows if row["phase2_status"] == status) for status in STATUS_COLORS}
    hybrid_wins = sum(1 for row in comparison if row["alternative"] == "hybrid_physicalized_safety_filter" and row["winner"] == "hybrid_physicalized_safety_filter")

    summary = {
        "schema_version": 1,
        "milestone_id": "M-SYNTH-2",
        "status": "validated",
        "central_conclusion": "Hybrid physicalized safety/filter remains useful as an architecture and failure-mode study, but current calibrated equal-workload evidence falsifies its performance/economic superiority over a strong programmable accelerator.",
        "phase2_status_counts": status_counts,
        "claim_count": len(rows),
        "calibrated_hybrid_winner_share": calibrated["calibrated_hybrid_winner_share"],
        "calibrated_safety_filter_decision": calibrated["safety_filter_decision"],
        "workload_classification_counts": workload["classification_counts"],
        "stronger_baseline_winner_counts": stronger["winner_counts"],
        "stronger_baseline_decision_class_counts": stronger["decision_class_counts"],
        "hybrid_workload_wins": hybrid_wins,
        "preserved_case_winner": stronger["preserved_case_winner"],
        "preserved_case_decision_class": stronger["preserved_case_decision_class"],
        "reopening_standard": "Measured production traces must show durable positive hybrid margin against optimized software and programmable accelerator under identical feature, audit, fallback, update, utilization, energy, and latency accounting.",
        "evidence_map_caption": "Phase 1 and Phase 2 claim statuses, showing which claims were preserved, weakened, falsified, or superseded after calibrated workload and stronger-baseline replay.",
    }

    write_csv(DATA / "phase2_claim_matrix.csv", rows)
    (DATA / "phase2_synthesis_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_png(DATA / "phase2_evidence_map.png", rows)
    write_doc(DOCS / "phase2_synthesis_downgrade.md", summary, rows)
    print(f"wrote {DATA / 'phase2_claim_matrix.csv'}")
    print(f"wrote {DATA / 'phase2_synthesis_summary.json'}")
    print(f"wrote {DATA / 'phase2_evidence_map.png'}")
    print(f"wrote {DOCS / 'phase2_synthesis_downgrade.md'}")
    print("hybrid_workload_wins:", hybrid_wins)


if __name__ == "__main__":
    main()
