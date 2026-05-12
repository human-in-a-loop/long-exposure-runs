#!/usr/bin/env python3
# created: 2026-05-11T23:50:00Z
# cycle: 19
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-DC12-1
"""Host-local proxy benchmarks for DC-001/DC-002 calibration plumbing.

These measurements are intentionally modest and unprivileged. They validate
the measurement path and threshold overlay mechanics; they are not GPU, HBM,
CXL, pooled-memory, or datacenter power measurements.
"""

from __future__ import annotations

import csv
import multiprocessing as mp
import os
import platform
import random
import statistics
import time
from pathlib import Path
from multiprocessing import shared_memory


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OUT_METADATA = DATA / "dc12_local_bench_metadata.csv"
OUT_BYTE = DATA / "dc12_byte_movement_measurements.csv"
OUT_CONTENTION = DATA / "dc12_contention_measurements.csv"

SEED = 12012
BUFFER_SIZES = [1 << 20, 4 << 20, 16 << 20]
RANDOM_WORKING_SETS = [256 << 10, 1 << 20, 4 << 20]
WORKER_COUNTS = sorted({1, 2, 4, max(1, min(os.cpu_count() or 1, 8))})
POWER_SOURCE = "unavailable"
EVIDENCE = "host_local_proxy"


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((pct / 100.0) * (len(ordered) - 1)))))
    return ordered[index]


def bench_copy_read_write() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for size in BUFFER_SIZES:
        iterations = max(2, min(8, (32 << 20) // size))
        source = bytearray((i * 17 + 3) % 251 for i in range(size))
        target = bytearray(size)
        retained = [source, target]
        for pattern in ["sequential_copy", "sequential_read", "sequential_write"]:
            samples: list[float] = []
            checksum = 0
            for i in range(iterations):
                t0 = time.perf_counter()
                if pattern == "sequential_copy":
                    target[:] = source
                    checksum ^= target[(i * 4099) % size]
                elif pattern == "sequential_read":
                    view = memoryview(source)
                    checksum ^= sum(view[0:size:4096]) & 255
                else:
                    target[:] = bytes([(i + size) & 255]) * size
                    checksum ^= target[(i * 8191) % size]
                samples.append(time.perf_counter() - t0)
            wall = sum(samples)
            bytes_touched = size * iterations * (2 if pattern == "sequential_copy" else 1)
            rows.append(
                {
                    "measurement_id": f"DC001-{pattern}-{size}",
                    "phase": "byte_movement",
                    "access_pattern": pattern,
                    "buffer_size_bytes": size,
                    "working_set_bytes": size,
                    "iteration_count": iterations,
                    "bytes_touched": bytes_touched,
                    "wall_time_s": round(wall, 9),
                    "throughput_mb_s": round(bytes_touched / max(wall, 1e-12) / (1 << 20), 3),
                    "latency_p50_us": round(percentile(samples, 50) * 1e6, 3),
                    "latency_p95_us": round(percentile(samples, 95) * 1e6, 3),
                    "latency_p99_us": round(percentile(samples, 99) * 1e6, 3),
                    "worker_count": 1,
                    "residency_retained_bytes": sum(len(buf) for buf in retained),
                    "power_source": POWER_SOURCE,
                    "energy_proxy_byte_seconds": round(bytes_touched * wall, 3),
                    "checksum": checksum,
                    "evidence_label": EVIDENCE,
                }
            )
    return rows


def bench_random_access() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    rng = random.Random(SEED)
    for size in RANDOM_WORKING_SETS:
        buf = bytearray((i * 13 + 7) % 253 for i in range(size))
        probes = 4096
        indexes = [rng.randrange(size) for _ in range(probes)]
        samples: list[float] = []
        checksum = 0
        for idx in indexes:
            t0 = time.perf_counter()
            checksum ^= buf[idx]
            samples.append(time.perf_counter() - t0)
        wall = sum(samples)
        rows.append(
            {
                "measurement_id": f"DC001-random_access-{size}",
                "phase": "random_access",
                "access_pattern": "random_read_byte",
                "buffer_size_bytes": size,
                "working_set_bytes": size,
                "iteration_count": probes,
                "bytes_touched": probes,
                "wall_time_s": round(wall, 9),
                "throughput_mb_s": round(probes / max(wall, 1e-12) / (1 << 20), 3),
                "latency_p50_us": round(percentile(samples, 50) * 1e6, 3),
                "latency_p95_us": round(percentile(samples, 95) * 1e6, 3),
                "latency_p99_us": round(percentile(samples, 99) * 1e6, 3),
                "worker_count": 1,
                "residency_retained_bytes": size,
                "power_source": POWER_SOURCE,
                "energy_proxy_byte_seconds": round(probes * wall, 3),
                "checksum": checksum,
                "evidence_label": EVIDENCE,
            }
        )
    return rows


def contention_worker(
    worker_id: int,
    worker_count: int,
    shm_name: str,
    size: int,
    rounds: int,
    start_event: mp.Event,
    sink: mp.Queue,
) -> None:
    shm = shared_memory.SharedMemory(name=shm_name)
    buf = shm.buf
    rng = random.Random(SEED + worker_count * 100 + worker_id)
    indexes = [rng.randrange(0, size - 64) for _ in range(rounds)]
    local: list[float] = []
    start_event.wait()
    for i, idx in enumerate(indexes):
        t0 = time.perf_counter()
        if (i + worker_id) % 3 == 0:
            buf[idx] = (buf[idx] + worker_id + i) & 255
        else:
            _ = buf[idx] ^ buf[idx + 63]
        local.append(time.perf_counter() - t0)
    sink.put(local)
    shm.close()


def bench_contention() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    size = 8 << 20
    for workers in WORKER_COUNTS:
        shm = shared_memory.SharedMemory(create=True, size=size)
        shm.buf[:] = bytes((i * 11 + 5) % 251 for i in range(size))
        samples: list[float] = []
        rounds = 3500
        start_event = mp.Event()
        sink: mp.Queue = mp.Queue()
        processes = [
            mp.Process(target=contention_worker, args=(wid, workers, shm.name, size, rounds, start_event, sink))
            for wid in range(workers)
        ]
        start = time.perf_counter()
        for process in processes:
            process.start()
        start_event.set()
        for _ in processes:
            samples.extend(sink.get())
        for process in processes:
            process.join()
        elapsed = time.perf_counter() - start
        shm.close()
        shm.unlink()
        operations = workers * rounds
        bytes_touched = operations * 64
        rows.append(
            {
                "measurement_id": f"DC002-contention-{workers}w",
                "phase": "contention",
                "access_pattern": "mixed_random_read_write",
                "worker_count": workers,
                "buffer_size_bytes": size,
                "working_set_bytes": size,
                "operation_count": operations,
                "bytes_touched": bytes_touched,
                "wall_time_s": round(elapsed, 9),
                "ops_per_second": round(operations / max(elapsed, 1e-12), 3),
                "latency_p50_us": round(percentile(samples, 50) * 1e6, 3),
                "latency_p95_us": round(percentile(samples, 95) * 1e6, 3),
                "latency_p99_us": round(percentile(samples, 99) * 1e6, 3),
                "contention_proxy_p95_over_1w": "",
                "contention_proxy_p99_over_1w": "",
                "residency_retained_bytes": size,
                "power_source": POWER_SOURCE,
                "evidence_label": EVIDENCE,
            }
        )
    base_p95 = next(float(r["latency_p95_us"]) for r in rows if int(r["worker_count"]) == 1)
    base_p99 = next(float(r["latency_p99_us"]) for r in rows if int(r["worker_count"]) == 1)
    for row in rows:
        row["contention_proxy_p95_over_1w"] = round(float(row["latency_p95_us"]) / max(base_p95, 1e-9), 4)
        row["contention_proxy_p99_over_1w"] = round(float(row["latency_p99_us"]) / max(base_p99, 1e-9), 4)
    return rows


def metadata_rows() -> list[dict[str, object]]:
    keys = {
        "environment_id": f"{platform.node()}-{platform.machine()}",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or "unknown",
        "cpu_count": os.cpu_count() or 1,
        "benchmark_seed": SEED,
        "buffer_sizes_bytes": ";".join(str(v) for v in BUFFER_SIZES),
        "random_working_sets_bytes": ";".join(str(v) for v in RANDOM_WORKING_SETS),
        "worker_counts": ";".join(str(v) for v in WORKER_COUNTS),
        "power_source": POWER_SOURCE,
        "external_validity": "host_local_proxy_not_gpu_hbm_cxl_or_datacenter_calibration",
    }
    return [
        {
            "measurement_id": "DC12-LOCAL-PROXY",
            "metadata_key": key,
            "metadata_value": value,
            "evidence_label": EVIDENCE,
        }
        for key, value in keys.items()
    ]


def main() -> None:
    byte_rows = bench_copy_read_write() + bench_random_access()
    contention_rows = bench_contention()
    write_csv(
        OUT_METADATA,
        metadata_rows(),
        ["measurement_id", "metadata_key", "metadata_value", "evidence_label"],
    )
    write_csv(
        OUT_BYTE,
        byte_rows,
        [
            "measurement_id",
            "phase",
            "access_pattern",
            "buffer_size_bytes",
            "working_set_bytes",
            "iteration_count",
            "bytes_touched",
            "wall_time_s",
            "throughput_mb_s",
            "latency_p50_us",
            "latency_p95_us",
            "latency_p99_us",
            "worker_count",
            "residency_retained_bytes",
            "power_source",
            "energy_proxy_byte_seconds",
            "checksum",
            "evidence_label",
        ],
    )
    write_csv(
        OUT_CONTENTION,
        contention_rows,
        [
            "measurement_id",
            "phase",
            "access_pattern",
            "worker_count",
            "buffer_size_bytes",
            "working_set_bytes",
            "operation_count",
            "bytes_touched",
            "wall_time_s",
            "ops_per_second",
            "latency_p50_us",
            "latency_p95_us",
            "latency_p99_us",
            "contention_proxy_p95_over_1w",
            "contention_proxy_p99_over_1w",
            "residency_retained_bytes",
            "power_source",
            "evidence_label",
        ],
    )


if __name__ == "__main__":
    main()
