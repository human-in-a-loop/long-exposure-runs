# created: 2026-05-13T05:28:00Z
# cycle: 2
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-CAL-1
"""Local overhead probes for the calibration companion model.

These are host/Python proxies only. They bound interpreter, branching, and
CSV/JSON audit overhead on this machine; they are not hardware measurements.
"""

from __future__ import annotations

import csv
import json
import statistics
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
OUT_JSON = DATA_DIR / "local_overhead_probe.json"
OUT_CSV = DATA_DIR / "local_overhead_probe.csv"

WEIGHTS = [12, -7, 5, 9, -11, 4, 6, -3]
FEATURES = [8, -4, 5, 6, -3, 2, 4, -1]


def dot_product() -> int:
    return sum(f * w for f, w in zip(FEATURES, WEIGHTS)) - 10


def dispatch(score: int) -> str:
    if score >= 64:
        return "block"
    return "allow"


def time_call(fn, iterations: int) -> float:
    start = time.perf_counter_ns()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter_ns() - start
    return elapsed / iterations / 1000.0


def audit_json_csv(iterations: int) -> float:
    rows = []
    start = time.perf_counter_ns()
    with tempfile.TemporaryDirectory() as tmp:
        json_path = Path(tmp) / "audit.jsonl"
        csv_path = Path(tmp) / "audit.csv"
        with json_path.open("w") as jf, csv_path.open("w", newline="") as cf:
            writer = csv.DictWriter(cf, fieldnames=["request_id", "decision", "score"])
            writer.writeheader()
            for i in range(iterations):
                score = dot_product()
                row = {"request_id": f"probe-{i}", "decision": dispatch(score), "score": score}
                jf.write(json.dumps(row, sort_keys=True) + "\n")
                writer.writerow(row)
                rows.append(row)
    elapsed = time.perf_counter_ns() - start
    if not rows:
        raise RuntimeError("audit probe did not write rows")
    return elapsed / iterations / 1000.0


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    iterations = 20_000
    audit_iterations = 2_000

    dot_samples = [time_call(dot_product, iterations) for _ in range(5)]
    dispatch_samples = [time_call(lambda: dispatch(261), iterations) for _ in range(5)]
    combined_samples = [time_call(lambda: dispatch(dot_product()), iterations) for _ in range(5)]
    audit_samples = [audit_json_csv(audit_iterations) for _ in range(3)]

    rows = [
        ("python_int8_dot_product", statistics.median(dot_samples), "us/request", iterations, "local_measured"),
        ("fallback_dispatch_branch", statistics.median(dispatch_samples), "us/request", iterations, "local_measured"),
        ("dot_plus_dispatch", statistics.median(combined_samples), "us/request", iterations, "local_measured"),
        ("csv_json_audit_logging", statistics.median(audit_samples), "us/request", audit_iterations, "local_measured"),
    ]

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "median_value", "unit", "iterations", "source_type"])
        writer.writeheader()
        for metric, value, unit, count, source_type in rows:
            writer.writerow(
                {
                    "metric": metric,
                    "median_value": f"{value:.6f}",
                    "unit": unit,
                    "iterations": count,
                    "source_type": source_type,
                }
            )

    summary = {
        "schema_version": 1,
        "milestone_id": "M-CAL-1",
        "interpretation": "local host/Python proxy, not hardware truth",
        "iterations": {"dot_dispatch": iterations, "audit": audit_iterations},
        "metrics": {
            metric: {
                "median_value": value,
                "unit": unit,
                "source_type": source_type,
            }
            for metric, value, unit, _count, source_type in rows
        },
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
