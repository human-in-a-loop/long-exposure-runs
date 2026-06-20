# created: 2026-05-13T02:20:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-TARGET-1
"""Score physicalized-weight target candidates against strong baselines.

Scores are modeled heuristics on 0-5 axes. They narrow architecture search
space; they are not silicon measurements.
"""

from __future__ import annotations

import csv
import json
import math
import struct
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
SUMMARY_PATH = DATA_DIR / "breakeven_summary.json"
GRID_PATH = DATA_DIR / "breakeven_grid.csv"

AXES = (
    "update_stability",
    "reuse_volume",
    "approximation_tolerance",
    "integration_complexity",
    "energy_upside_vs_baseline",
    "software_baseline_resistance",
    "evidence_quality",
)


@dataclass(frozen=True)
class Component:
    component_id: str
    name: str
    category: str
    evidence_level: str
    update_interval_days: float
    reuse_volume: float
    update_stability: float
    approximation_tolerance: float
    integration_complexity: float
    energy_upside_vs_baseline: float
    software_baseline_resistance: float
    evidence_quality: float
    baseline_comparison: str
    rationale: str
    falsifier: str


@dataclass(frozen=True)
class ScoreRow:
    rank: int
    component_id: str
    name: str
    category: str
    evidence_level: str
    update_interval_days: float
    reuse_volume: float
    update_stability: float
    approximation_tolerance: float
    integration_complexity: float
    energy_upside_vs_baseline: float
    software_baseline_resistance: float
    evidence_quality: float
    total_score: float
    baseline_penalty: float
    recommended_next_target: bool
    baseline_comparison: str
    rationale: str
    falsifier: str


def components() -> list[Component]:
    return [
        Component("safety_filter", "Fixed safety/filter classifier submodels", "candidate", "inferred", 180, 4.4, 4.3, 3.8, 4.0, 3.5, 3.6, 3.0, "Programmable accelerators are strong, but isolation and fallback make fixed or semi-fixed safety filters testable.", "Small repeated classifiers can be long-lived, isolated, and tolerant of conservative fallback.", "Demote if policy churn forces weekly updates or false-positive/negative cost requires full programmable execution."),
        Component("rerank_transform", "Repeated retrieval/reranking feature transforms", "candidate", "inferred", 120, 4.2, 4.0, 3.5, 3.7, 3.4, 3.4, 2.8, "Software caching helps, but repeated feature transforms can remain hot across requests.", "Reranking pipelines often reuse stable transforms at high volume and can fall back to programmable paths.", "Demote if workload-specific feature changes dominate or batching/caching erases memory movement."),
        Component("wake_router", "Small always-on wake-word or router models", "candidate", "inferred", 365, 3.9, 4.6, 4.0, 4.2, 3.2, 3.7, 3.1, "Programmable accelerator cost may dominate for always-on tiny models; fixed local logic has a plausible idle-energy niche.", "Always-on routing has stable weights, simple interfaces, and high aggregate reuse despite small per-request work.", "Demote if the router must track fast-changing model menus or if CPU/NPU idle states already match the energy target."),
        Component("moe_router", "Mixture-of-experts router or dispatch logic", "candidate", "modeled", 90, 4.5, 3.5, 3.2, 3.6, 3.0, 3.2, 2.7, "Software runtimes already optimize dispatch, so credit only the stable high-volume router core.", "Routers are reused heavily and smaller than experts, but integration with dynamic serving is nontrivial.", "Demote if expert churn or load balancing changes the router distribution faster than quarterly."),
        Component("lora_adapter", "Domain-specific adapter or LoRA blocks with slow update cadence", "candidate", "modeled", 90, 3.6, 3.4, 3.0, 3.1, 3.0, 2.8, 2.6, "The software-optimized baseline is dangerous here because adapters are already compact and easy to swap.", "Some long-lived enterprise adapters have enough stability to justify semi-fixed treatment, not permanent masks.", "Demote if tenant-specific updates are monthly or if memory savings from adapter caching reaches 50%."),
        Component("embedding_table", "Fixed or slowly changing embedding tables for constrained vocabularies/domains", "candidate", "inferred", 180, 3.5, 3.9, 2.5, 2.8, 3.1, 2.6, 2.5, "Programmable memory hierarchy improvements compete directly; only constrained stable vocabularies survive.", "Constrained domains can make table storage stable and reusable, but vocabulary churn is a major risk.", "Demote if vocabulary/logit head variants churn or if compression/caching removes the movement bottleneck."),
        Component("projection_block", "Frozen first-layer projections or low-rank projection blocks", "candidate", "modeled", 180, 3.2, 3.7, 2.8, 2.9, 2.9, 2.5, 2.5, "Programmable accelerators handle dense projections well, so physicalization must exploit exceptional reuse or locality.", "Projection blocks are static and simple, but they are deeply coupled to model layout.", "Demote if accelerator matrix units keep the block bandwidth-local or if model revisions alter dimensions."),
        Component("kv_compress", "KV-cache compression/decompression transforms", "candidate", "speculative", 60, 4.0, 2.6, 2.7, 2.4, 3.3, 2.2, 2.0, "Software/runtime KV management is a core null-hypothesis strength; fixed transforms need robust cross-model reuse.", "KV traffic is important, but context-dependent behavior makes fixed physicalization risky.", "Demote if quality loss is prompt-dependent or runtime compression policies change frequently."),
        Component("quant_scale", "Quantization/dequantization and scaling constants", "candidate", "inferred", 180, 4.1, 3.8, 2.2, 3.9, 2.2, 1.8, 2.8, "Quantization is already a software/compiler strength, so fixed constants alone get limited credit.", "Constants are stable and easy to integrate, but energy upside may be too small for a dedicated substrate.", "Demote if compiler fusion removes standalone movement or if formats change per model family."),
        Component("rope_transform", "Positional encoding / RoPE / deterministic transform support", "candidate", "inferred", 365, 4.0, 4.7, 3.6, 4.0, 1.8, 1.6, 3.0, "Deterministic transforms are easy to optimize in software or programmable logic; physicalized weights add little.", "This is stable and reusable, but it is not obviously weight-dominated.", "Demote if profiling shows negligible memory/energy share versus attention and KV movement."),
        Component("frontier_dense", "Full frontier LLM dense weights burned permanently into fixed logic", "anti-target", "modeled", 14, 4.8, 0.8, 0.8, 0.3, 4.0, 0.4, 2.6, "Even if per-request energy looks attractive, update cadence, yield, stranded capital, and programmable baselines dominate.", "Superficially large energy upside fails the null because the entire model is high-churn and hard to repair.", "Promote only with evidence of multi-year frozen weights, extreme volume, repairability, and no competitive programmable path."),
        Component("tenant_finetune", "Frequently updated tenant-specific fine-tunes or adapters", "anti-target", "modeled", 7, 2.0, 0.6, 1.8, 1.7, 2.5, 0.8, 2.7, "Software adapter loading and routing are designed for this case; fixed substrates strand value quickly.", "Update churn prevents amortization even if adapters are small.", "Promote only if a tenant model freezes for quarters and reaches high shared reuse."),
        Component("dynamic_attention", "Dynamic attention over live context as fixed physical logic", "anti-target", "inferred", 1, 4.7, 0.4, 0.7, 0.5, 2.8, 0.7, 2.5, "KV/cache software and programmable accelerators are the right baseline; live context is not static weight state.", "Attention dataflow is important but too dynamic to burn as fixed weights.", "Promote only for a narrow fixed transform inside attention with measured stability and fallback."),
        Component("training_state", "Training/optimizer state and gradient computation", "anti-target", "inferred", 0.1, 0.8, 0.1, 0.3, 0.4, 1.2, 0.3, 2.8, "This is not inference weight reuse; programmable training systems remain the relevant substrate.", "Optimizer state mutates continuously and cannot amortize fixed physicalization.", "Promote only if the scope changes to inference-only frozen auxiliary weights."),
        Component("vocab_head_churn", "High-churn vocabulary/logit-head variants", "anti-target", "speculative", 14, 2.6, 0.8, 1.5, 1.2, 2.6, 0.9, 2.1, "Tokenizer/head churn is exactly where software indirection and table updates are cheap.", "Variants look table-like but update and SKU fragmentation erase the fixed-weight case.", "Promote only for a constrained vocabulary with stable deployment and high shared traffic."),
    ]


def load_calibration(summary_path: Path = SUMMARY_PATH, grid_path: Path = GRID_PATH) -> dict[str, float]:
    summary = json.loads(summary_path.read_text())
    winner_counts = summary["winner_counts"]
    scenarios = max(1, sum(winner_counts.values()))
    baseline_share = (winner_counts.get("software_optimized", 0) + winner_counts.get("programmable_accelerator", 0)) / scenarios
    fixed_share = (
        winner_counts.get("fixed_digital_weights", 0)
        + winner_counts.get("analog_in_memory", 0)
        + winner_counts.get("hybrid_physicalized_submodel", 0)
    ) / scenarios

    savings_values: set[float] = set()
    update_values: set[float] = set()
    with grid_path.open(newline="") as f:
        for row in csv.DictReader(f):
            savings_values.add(float(row["software_memory_savings"]))
            update_values.add(float(row["update_interval_days"]))

    return {
        "baseline_winner_share": baseline_share,
        "physicalized_winner_share": fixed_share,
        "max_software_savings": max(savings_values),
        "min_update_interval_days": min(update_values),
        "max_update_interval_days": max(update_values),
    }


def clamp(value: float, lo: float = 0.0, hi: float = 5.0) -> float:
    return max(lo, min(hi, value))


def score_components(software_memory_savings: float = 0.35) -> tuple[list[ScoreRow], dict[str, float]]:
    calibration = load_calibration()
    rows: list[ScoreRow] = []
    baseline_pressure = calibration["baseline_winner_share"]
    savings_penalty = software_memory_savings * (0.75 + 0.50 * baseline_pressure)

    for item in components():
        adjusted_energy = clamp(item.energy_upside_vs_baseline - savings_penalty * (5.0 - item.software_baseline_resistance) / 5.0)
        adjusted_resistance = clamp(item.software_baseline_resistance - software_memory_savings * 1.2)
        update_score = item.update_stability
        reuse_score = item.reuse_volume

        if item.reuse_volume <= 0:
            reuse_score = 0.0
            adjusted_energy = 0.0
            adjusted_resistance = 0.0
        if item.update_interval_days <= 1.0:
            update_score = min(update_score, item.update_interval_days)
            adjusted_energy = min(adjusted_energy, 1.0)
            adjusted_resistance = min(adjusted_resistance, 1.0)

        total = (
            1.25 * update_score
            + 1.25 * reuse_score
            + item.approximation_tolerance
            + item.integration_complexity
            + 1.20 * adjusted_energy
            + 1.10 * adjusted_resistance
            + 0.75 * item.evidence_quality
        ) / 7.55
        if item.category == "anti-target":
            total *= 0.72
        if item.reuse_volume <= 0 or item.update_interval_days <= 1.0:
            total = min(total, 1.9)

        rows.append(
            ScoreRow(
                rank=0,
                component_id=item.component_id,
                name=item.name,
                category=item.category,
                evidence_level=item.evidence_level,
                update_interval_days=item.update_interval_days,
                reuse_volume=round(reuse_score, 3),
                update_stability=round(update_score, 3),
                approximation_tolerance=item.approximation_tolerance,
                integration_complexity=item.integration_complexity,
                energy_upside_vs_baseline=round(adjusted_energy, 3),
                software_baseline_resistance=round(adjusted_resistance, 3),
                evidence_quality=item.evidence_quality,
                total_score=round(total, 3),
                baseline_penalty=round(savings_penalty, 3),
                recommended_next_target=False,
                baseline_comparison=item.baseline_comparison,
                rationale=item.rationale,
                falsifier=item.falsifier,
            )
        )

    rows.sort(key=lambda r: (r.total_score, r.category == "candidate"), reverse=True)
    top_candidate_seen = False
    ranked: list[ScoreRow] = []
    for rank, row in enumerate(rows, start=1):
        recommended = False
        if row.category == "candidate" and not top_candidate_seen:
            recommended = True
            top_candidate_seen = True
        ranked.append(ScoreRow(**{**asdict(row), "rank": rank, "recommended_next_target": recommended}))
    return ranked, calibration


def write_csv(rows: list[ScoreRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(rows[0]).keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_summary(rows: list[ScoreRow], calibration: dict[str, float], path: Path, software_memory_savings: float) -> None:
    top = next(r for r in rows if r.recommended_next_target)
    summary = {
        "schema_version": 1,
        "software_memory_savings": software_memory_savings,
        "axes": list(AXES),
        "calibration": calibration,
        "candidate_count": sum(1 for r in rows if r.category == "candidate"),
        "anti_target_count": sum(1 for r in rows if r.category == "anti-target"),
        "recommended_next_target": asdict(top),
        "top_ranked": [asdict(r) for r in rows[:8]],
        "anti_targets": [asdict(r) for r in rows if r.category == "anti-target"],
        "method_notes": [
            "scores are modeled/inferred/speculative heuristics, not measured silicon results",
            "energy_upside_vs_baseline and software_baseline_resistance are reduced as software_memory_savings increases",
            "zero reuse volume or near-zero update interval caps viability because fixed costs cannot amortize",
            "baseline calibration comes from winner shares in breakeven_summary.json and grid ranges in breakeven_grid.csv",
        ],
    }
    path.write_text(json.dumps(summary, indent=2) + "\n")


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _draw_rect(pixels: bytearray, width: int, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    for y in range(max(0, y0), min(y1, len(pixels) // (width * 3))):
        for x in range(max(0, x0), min(x1, width)):
            idx = (y * width + x) * 3
            pixels[idx : idx + 3] = bytes(color)


def write_heatmap(rows: list[ScoreRow], path: Path) -> None:
    cell_w, cell_h = 52, 24
    left, top = 260, 20
    width = left + cell_w * (len(AXES) + 1) + 20
    height = top + cell_h * len(rows) + 20
    pixels = bytearray([248, 248, 246] * width * height)
    axis_fields = list(AXES) + ["total_score"]
    for row_idx, row in enumerate(rows):
        y = top + row_idx * cell_h
        stripe = (238, 238, 234) if row_idx % 2 else (248, 248, 246)
        _draw_rect(pixels, width, 0, y, width, y + cell_h, stripe)
        for col_idx, axis in enumerate(axis_fields):
            value = getattr(row, axis)
            scaled = clamp(float(value)) / 5.0
            red = int(238 - 135 * scaled)
            green = int(231 - 55 * (1.0 - scaled))
            blue = int(208 - 165 * scaled)
            x = left + col_idx * cell_w
            _draw_rect(pixels, width, x + 1, y + 1, x + cell_w - 1, y + cell_h - 1, (red, green, blue))
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _png_chunk(b"IDAT", zlib.compress(raw, 9))
    png += _png_chunk(b"IEND", b"")
    path.write_bytes(png)


def main() -> None:
    rows, calibration = score_components(software_memory_savings=0.35)
    write_csv(rows, DATA_DIR / "target_scores.csv")
    write_summary(rows, calibration, DATA_DIR / "target_scores_summary.json", software_memory_savings=0.35)
    write_heatmap(rows, DATA_DIR / "target_score_heatmap.png")
    print(f"wrote {len(rows)} target rows to {DATA_DIR}")
    print(f"recommended target: {next(r.name for r in rows if r.recommended_next_target)}")


if __name__ == "__main__":
    main()
