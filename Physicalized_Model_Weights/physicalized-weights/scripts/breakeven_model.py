# created: 2026-05-13T02:05:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-MODEL-1
"""First-order break-even model for physicalized neural-network inference.

The model uses normalized cost/energy units. Defaults are placeholders for
boundary finding, not claims about a specific silicon process or workload.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


STRATEGIES = (
    "programmable_unoptimized",
    "software_optimized",
    "programmable_accelerator",
    "fixed_digital_weights",
    "analog_in_memory",
    "hybrid_physicalized_submodel",
)


@dataclass(frozen=True)
class Inputs:
    parameter_count_b: float = 7.0
    weight_bits: int = 8
    tokens_per_request: int = 512
    requests_per_day: float = 100_000.0
    update_interval_days: float = 90.0
    offchip_energy_per_gb: float = 1.0
    local_energy_per_gb: float = 0.18
    compute_energy_per_request: float = 0.45
    software_memory_savings: float = 0.0
    utilization: float = 0.60
    fixed_substrate_cost: float = 350_000.0
    analog_conversion_overhead: float = 0.35
    yield_repair_factor: float = 1.15
    accuracy_fallback_penalty: float = 0.04
    integration_cost: float = 30_000.0


@dataclass(frozen=True)
class Result:
    strategy: str
    requests_per_day: float
    update_interval_days: float
    software_memory_savings: float
    fixed_substrate_cost: float
    analog_conversion_overhead: float
    yield_repair_factor: float
    accuracy_fallback_penalty: float
    requests_per_update: float
    per_request_cost: float
    amortized_fixed_cost: float
    total_normalized_cost: float


def weight_gb(inputs: Inputs) -> float:
    return inputs.parameter_count_b * 1e9 * inputs.weight_bits / 8 / 1e9


def traffic_multiplier(tokens_per_request: int) -> float:
    """Small decode requests reuse weights more poorly than long batches."""
    return max(0.20, min(1.0, tokens_per_request / 512.0))


def base_memory_cost(inputs: Inputs) -> float:
    return weight_gb(inputs) * inputs.offchip_energy_per_gb * traffic_multiplier(inputs.tokens_per_request)


def local_memory_cost(inputs: Inputs) -> float:
    return weight_gb(inputs) * inputs.local_energy_per_gb * traffic_multiplier(inputs.tokens_per_request)


def per_request_cost(strategy: str, inputs: Inputs) -> float:
    mem = base_memory_cost(inputs)
    local = local_memory_cost(inputs)
    compute = inputs.compute_energy_per_request
    util_penalty = 1.0 / max(inputs.utilization, 1e-9)

    if strategy == "programmable_unoptimized":
        return (mem + compute) * util_penalty
    if strategy == "software_optimized":
        return (mem * (1.0 - inputs.software_memory_savings) + compute * 0.92) * util_penalty
    if strategy == "programmable_accelerator":
        return (local * (1.0 - 0.50 * inputs.software_memory_savings) + compute * 0.55) * (0.85 + 0.15 * util_penalty)
    if strategy == "fixed_digital_weights":
        return (local * 0.42 + compute * 0.35) * (0.80 + 0.20 * util_penalty)
    if strategy == "analog_in_memory":
        array_cost = local * 0.18 + compute * 0.18
        conversion = mem * inputs.analog_conversion_overhead
        fallback = mem * inputs.accuracy_fallback_penalty
        return (array_cost + conversion + fallback) * inputs.yield_repair_factor * (0.85 + 0.15 * util_penalty)
    if strategy == "hybrid_physicalized_submodel":
        physical_fraction = 0.35
        programmable_part = (mem * (1.0 - inputs.software_memory_savings) + compute * 0.90) * (1.0 - physical_fraction)
        physical_part = (local * 0.35 + compute * 0.40) * physical_fraction
        fallback = mem * inputs.accuracy_fallback_penalty * 0.30
        return (programmable_part + physical_part + fallback) * (0.90 + 0.10 * util_penalty)
    raise ValueError(f"unknown strategy: {strategy}")


def fixed_cost(strategy: str, inputs: Inputs) -> float:
    if strategy in {"programmable_unoptimized", "software_optimized"}:
        return 0.0
    if strategy == "programmable_accelerator":
        return inputs.fixed_substrate_cost * 0.08
    if strategy == "fixed_digital_weights":
        return inputs.fixed_substrate_cost + inputs.integration_cost
    if strategy == "analog_in_memory":
        return inputs.fixed_substrate_cost * 1.25 * inputs.yield_repair_factor + inputs.integration_cost
    if strategy == "hybrid_physicalized_submodel":
        return inputs.fixed_substrate_cost * 0.35 + inputs.integration_cost * 0.60
    raise ValueError(f"unknown strategy: {strategy}")


def update_penalty(strategy: str, inputs: Inputs) -> float:
    # Frequent updates strand fixed/mask-programmed value. Reprogrammable and
    # hybrid strategies pay less because the control plane and fallback survive.
    days = max(inputs.update_interval_days, 1e-9)
    if strategy == "fixed_digital_weights":
        return inputs.fixed_substrate_cost * (30.0 / days)
    if strategy == "analog_in_memory":
        return inputs.fixed_substrate_cost * 0.40 * (30.0 / days)
    if strategy == "hybrid_physicalized_submodel":
        return inputs.fixed_substrate_cost * 0.12 * (30.0 / days)
    if strategy == "programmable_accelerator":
        return inputs.fixed_substrate_cost * 0.01 * (30.0 / days)
    return 0.0


def evaluate(inputs: Inputs) -> list[Result]:
    n = inputs.requests_per_day * inputs.update_interval_days
    rows: list[Result] = []
    for strategy in STRATEGIES:
        pr = per_request_cost(strategy, inputs)
        fixed = fixed_cost(strategy, inputs) + update_penalty(strategy, inputs)
        amortized = fixed / n if n > 0 else math.inf if fixed > 0 else 0.0
        rows.append(
            Result(
                strategy=strategy,
                requests_per_day=inputs.requests_per_day,
                update_interval_days=inputs.update_interval_days,
                software_memory_savings=inputs.software_memory_savings,
                fixed_substrate_cost=inputs.fixed_substrate_cost,
                analog_conversion_overhead=inputs.analog_conversion_overhead,
                yield_repair_factor=inputs.yield_repair_factor,
                accuracy_fallback_penalty=inputs.accuracy_fallback_penalty,
                requests_per_update=n,
                per_request_cost=pr,
                amortized_fixed_cost=amortized,
                total_normalized_cost=pr + amortized,
            )
        )
    return rows


def winner(rows: Iterable[Result]) -> Result:
    return min(rows, key=lambda r: r.total_normalized_cost)


def breakeven_requests(programmable_cost: float, physicalized_cost: float, fixed: float) -> float | None:
    delta = programmable_cost - physicalized_cost
    if delta <= 0:
        return None
    return fixed / delta


def grid(defaults: Inputs) -> list[Result]:
    requests = [0, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000]
    update_days = [1, 7, 30, 90, 365]
    savings_values = [0.0, 0.2, 0.35, 0.5]
    analog_overheads = [defaults.analog_conversion_overhead, 0.8]
    yield_factors = [defaults.yield_repair_factor, 1.6]
    rows: list[Result] = []
    for req in requests:
        for days in update_days:
            for savings in savings_values:
                for conversion in analog_overheads:
                    for yield_factor in yield_factors:
                        rows.extend(
                            evaluate(
                                Inputs(
                                    **{
                                        **asdict(defaults),
                                        "requests_per_day": float(req),
                                        "update_interval_days": float(days),
                                        "software_memory_savings": savings,
                                        "analog_conversion_overhead": conversion,
                                        "yield_repair_factor": yield_factor,
                                    }
                                )
                            )
                        )
    return rows


def write_csv(rows: list[Result], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(rows[0]).keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_summary(rows: list[Result], defaults: Inputs, path: Path) -> None:
    scenario_keys = sorted({(r.requests_per_day, r.update_interval_days, r.software_memory_savings, r.analog_conversion_overhead, r.yield_repair_factor) for r in rows})
    winners: dict[str, int] = {s: 0 for s in STRATEGIES}
    sample_boundaries: list[dict[str, float | str | None]] = []
    for key in scenario_keys:
        subset = [r for r in rows if (r.requests_per_day, r.update_interval_days, r.software_memory_savings, r.analog_conversion_overhead, r.yield_repair_factor) == key]
        win = winner(subset)
        winners[win.strategy] += 1
        software = next(r for r in subset if r.strategy == "software_optimized")
        for strategy_name in ("fixed_digital_weights", "analog_in_memory", "hybrid_physicalized_submodel"):
            phys = next(r for r in subset if r.strategy == strategy_name)
            fixed_total = fixed_cost(strategy_name, Inputs(**{**asdict(defaults), "update_interval_days": key[1], "software_memory_savings": key[2], "analog_conversion_overhead": key[3], "yield_repair_factor": key[4]}))
            sample_boundaries.append(
                {
                    "software_memory_savings": key[2],
                    "update_interval_days": key[1],
                    "strategy": strategy_name,
                    "breakeven_requests_vs_software_optimized": breakeven_requests(software.per_request_cost, phys.per_request_cost, fixed_total),
                }
            )

    summary = {
        "schema_version": 1,
        "strategies": list(STRATEGIES),
        "default_inputs": asdict(defaults),
        "placeholder_assumptions": [
            "normalized cost/energy units, not process-specific joules or dollars",
            "fixed_substrate_cost is an amortization proxy for fabrication, packaging, integration, and opportunity cost",
            "software_memory_savings reduces programmable memory movement before physicalized strategies are compared",
        ],
        "winner_counts": winners,
        "dominant_variables": [
            "requests_per_update",
            "software_memory_savings",
            "fixed_substrate_cost",
            "update_interval_days",
            "analog_conversion_overhead",
            "yield_repair_factor",
            "accuracy_fallback_penalty",
            "utilization",
        ],
        "sample_boundaries": sample_boundaries[:120],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


def plot_region(rows: list[Result], out_path: Path, savings: float = 0.35) -> None:
    import numpy as np

    req_values = sorted({r.requests_per_day for r in rows})
    update_values = sorted({r.update_interval_days for r in rows})
    strategy_index = {s: i for i, s in enumerate(STRATEGIES)}
    z = np.zeros((len(update_values), len(req_values)))

    for i, days in enumerate(update_values):
        for j, req in enumerate(req_values):
            subset = [
                r
                for r in rows
                if r.requests_per_day == req
                and r.update_interval_days == days
                and r.software_memory_savings == savings
                and abs(r.analog_conversion_overhead - 0.35) < 1e-12
                and abs(r.yield_repair_factor - 1.15) < 1e-12
            ]
            z[i, j] = strategy_index[winner(subset).strategy]

    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 5.5))
        cmap = plt.get_cmap("tab10", len(STRATEGIES))
        image = ax.imshow(z, origin="lower", aspect="auto", cmap=cmap, vmin=-0.5, vmax=len(STRATEGIES) - 0.5)
        ax.set_xticks(range(len(req_values)))
        ax.set_xticklabels([f"{v:g}" for v in req_values], rotation=35, ha="right")
        ax.set_yticks(range(len(update_values)))
        ax.set_yticklabels([f"{v:g}" for v in update_values])
        ax.set_xlabel("Requests per day")
        ax.set_ylabel("Update interval (days)")
        ax.set_title("Break-even winner regions at software memory savings = 0.35")
        cbar = fig.colorbar(image, ax=ax, ticks=range(len(STRATEGIES)))
        cbar.ax.set_yticklabels(STRATEGIES)
        ax.grid(color="white", linewidth=0.7, alpha=0.7)
        fig.tight_layout()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=180)
        plt.close(fig)
    except ModuleNotFoundError:
        write_simple_png_region(z.astype(int).tolist(), out_path)


def write_simple_png_region(z: list[list[int]], out_path: Path) -> None:
    """Dependency-free fallback heatmap PNG for minimal environments."""
    import struct
    import zlib

    palette = [
        (31, 119, 180),
        (255, 127, 14),
        (44, 160, 44),
        (214, 39, 40),
        (148, 103, 189),
        (140, 86, 75),
    ]
    cell = 54
    margin = 12
    rows = len(z)
    cols = len(z[0])
    width = cols * cell + 2 * margin
    height = rows * cell + 2 * margin
    pixels = bytearray()
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            gx = (x - margin) // cell
            gy = rows - 1 - ((y - margin) // cell)
            if margin <= x < width - margin and margin <= y < height - margin and 0 <= gx < cols and 0 <= gy < rows:
                color = palette[z[gy][gx] % len(palette)]
                if (x - margin) % cell == 0 or (y - margin) % cell == 0:
                    color = (245, 245, 245)
            else:
                color = (255, 255, 255)
            row.extend(color)
        pixels.extend(row)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(pixels), 9))
        + chunk(b"IEND", b"")
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(png)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("physicalized-weights/data"))
    parser.add_argument("--fixed-substrate-cost", type=float, default=Inputs.fixed_substrate_cost)
    parser.add_argument("--utilization", type=float, default=Inputs.utilization)
    parser.add_argument("--parameter-count-b", type=float, default=Inputs.parameter_count_b)
    parser.add_argument("--tokens-per-request", type=int, default=Inputs.tokens_per_request)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    defaults = Inputs(
        fixed_substrate_cost=args.fixed_substrate_cost,
        utilization=args.utilization,
        parameter_count_b=args.parameter_count_b,
        tokens_per_request=args.tokens_per_request,
    )
    rows = grid(defaults)
    write_csv(rows, args.out_dir / "breakeven_grid.csv")
    write_summary(rows, defaults, args.out_dir / "breakeven_summary.json")
    plot_region(rows, args.out_dir / "breakeven_update_volume.png")
    print(f"wrote {len(rows)} rows to {args.out_dir}")


if __name__ == "__main__":
    main()
