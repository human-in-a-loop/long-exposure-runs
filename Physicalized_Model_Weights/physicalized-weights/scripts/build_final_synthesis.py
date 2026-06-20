# created: 2026-05-13T04:40:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-FINAL-1

"""Build final synthesis metadata and evidence-map artifacts.

This script is intentionally dependency-free. It checks that the validated
milestone artifacts exist, records their SHA-256 hashes, emits a CSV/JSON
evidence manifest, writes a compact final summary, and renders a simple PNG
evidence map without matplotlib.
"""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"


TYPE_COLORS = {
    "sourced": (82, 116, 255),
    "modeled": (48, 151, 92),
    "simulated": (226, 137, 46),
    "synthesized": (126, 79, 196),
    "inferred": (58, 160, 173),
    "speculative": (136, 136, 136),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows() -> list[dict[str, str]]:
    return [
        {
            "path": "physicalized-weights/docs/taxonomy_and_null.md",
            "milestone": "M-TAX-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "",
            "claim_supported": "Defines physicalization levels, inference-component candidates, strong software/runtime null hypothesis, and falsification criteria.",
        },
        {
            "path": "REFERENCES.md",
            "milestone": "M-FINAL-1",
            "evidence_type": "sourced",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "",
            "claim_supported": "Records the external sources used for RISC-V openness, toolchain context, and analog in-memory-computing background claims.",
        },
        {
            "path": "physicalized-weights/docs/final_synthesis.md",
            "milestone": "M-FINAL-1",
            "evidence_type": "speculative",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/docs/taxonomy_and_null.md; REFERENCES.md",
            "claim_supported": "Keeps analog, photonic, and process-specific hardware-advantage claims explicitly speculative until device-level calibration, drift, conversion, yield, and repair data exist.",
        },
        {
            "path": "physicalized-weights/scripts/breakeven_model.py",
            "milestone": "M-MODEL-1",
            "evidence_type": "modeled",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/breakeven_model.py",
            "dependent_artifacts": "physicalized-weights/docs/taxonomy_and_null.md",
            "claim_supported": "Implements the normalized break-even comparison across programmable, optimized software, accelerator, fixed, analog, and hybrid strategies.",
        },
        {
            "path": "physicalized-weights/data/breakeven_summary.json",
            "milestone": "M-MODEL-1/M-BASE-1",
            "evidence_type": "modeled",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/breakeven_model.py",
            "dependent_artifacts": "physicalized-weights/scripts/breakeven_model.py; physicalized-weights/data/breakeven_grid.csv",
            "claim_supported": "Software-optimized and programmable-accelerator baselines dominate many sampled regions; fixed digital wins only under favorable volume/update assumptions.",
        },
        {
            "path": "physicalized-weights/data/breakeven_update_volume.png",
            "milestone": "M-MODEL-1",
            "evidence_type": "modeled",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/breakeven_model.py",
            "dependent_artifacts": "physicalized-weights/data/breakeven_grid.csv",
            "claim_supported": "Visualizes break-even sensitivity to request volume and update cadence.",
        },
        {
            "path": "physicalized-weights/scripts/symbolic_breakeven.wls",
            "milestone": "M-MODEL-1",
            "evidence_type": "modeled",
            "validation_status": "validated",
            "generating_command": "wolfram-batch -script physicalized-weights/scripts/symbolic_breakeven.wls",
            "dependent_artifacts": "physicalized-weights/docs/taxonomy_and_null.md",
            "claim_supported": "Symbolically checks the break-even inequality, zero-volume failure, update-cadence divergence, and software-savings threshold shift.",
        },
        {
            "path": "physicalized-weights/docs/target_ranking.md",
            "milestone": "M-TARGET-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/data/target_scores_summary.json; physicalized-weights/data/breakeven_summary.json",
            "claim_supported": "Ranks safety/filter classifier as the narrow next target and rejects full frontier dense weights as an anti-target.",
        },
        {
            "path": "physicalized-weights/data/target_scores_summary.json",
            "milestone": "M-TARGET-1",
            "evidence_type": "modeled",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/target_scoring.py",
            "dependent_artifacts": "physicalized-weights/data/breakeven_summary.json; physicalized-weights/data/breakeven_grid.csv",
            "claim_supported": "Scores 10 candidate components and 5 anti-targets while preserving software/runtime baseline pressure.",
        },
        {
            "path": "physicalized-weights/docs/hybrid_safety_filter_architecture.md",
            "milestone": "M-ARCH-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/docs/target_ranking.md; physicalized-weights/data/hybrid_arch_summary.json",
            "claim_supported": "Specifies a bounded host/RISC-V-compatible safety-filter architecture with version, health, drift, audit, fallback, and rollback controls.",
        },
        {
            "path": "physicalized-weights/docs/hybrid_safety_filter_arch.png",
            "milestone": "M-ARCH-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "dot -Tpng physicalized-weights/docs/hybrid_safety_filter_arch.dot -o physicalized-weights/docs/hybrid_safety_filter_arch.png",
            "dependent_artifacts": "physicalized-weights/docs/hybrid_safety_filter_arch.dot",
            "claim_supported": "Shows the architecture boundary between host runtime, fixed classifier, fallback, audit, updates, and fail-safe state.",
        },
        {
            "path": "physicalized-weights/data/hybrid_arch_summary.json",
            "milestone": "M-ARCH-1",
            "evidence_type": "simulated",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/fallback_policy_sim.py",
            "dependent_artifacts": "physicalized-weights/scripts/fallback_policy_sim.py",
            "claim_supported": "Simulates fallback policy cases so stale, low-confidence, unhealthy, drifted, or unaudited outputs do not silently use the fast path.",
        },
        {
            "path": "physicalized-weights/docs/prototype_safety_filter.md",
            "milestone": "M-PROTO-1",
            "evidence_type": "simulated",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/data/prototype_summary.json; physicalized-weights/data/hdl_sim_results.csv",
            "claim_supported": "Documents the tiny fixed classifier prototype, baseline comparison, and route behavior.",
        },
        {
            "path": "physicalized-weights/data/prototype_summary.json",
            "milestone": "M-PROTO-1",
            "evidence_type": "simulated",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/prototype_safety_filter.py",
            "dependent_artifacts": "physicalized-weights/scripts/prototype_safety_filter.py",
            "claim_supported": "Records 16 prototype cases: 6 fast path, 8 fallback, 2 fail-safe, with normalized baseline costs.",
        },
        {
            "path": "physicalized-weights/hdl/safety_filter_core.sv",
            "milestone": "M-PROTO-1",
            "evidence_type": "synthesized",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/scripts/prototype_safety_filter.py",
            "claim_supported": "Implements only fixed signed int8 dot product, threshold compare, margin, and confidence in HDL.",
        },
        {
            "path": "physicalized-weights/data/hdl_sim_results.csv",
            "milestone": "M-PROTO-1",
            "evidence_type": "synthesized",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/hdl/run_yosys_eval.py",
            "dependent_artifacts": "physicalized-weights/hdl/safety_filter_core.sv; physicalized-weights/data/prototype_vectors.csv",
            "claim_supported": "Yosys eval matches Python golden outputs for all HDL vector cases.",
        },
        {
            "path": "physicalized-weights/data/yosys_safety_filter.log",
            "milestone": "M-PROTO-1",
            "evidence_type": "synthesized",
            "validation_status": "validated",
            "generating_command": "yosys -s physicalized-weights/hdl/safety_filter_core.ys > physicalized-weights/data/yosys_safety_filter.log 2>&1",
            "dependent_artifacts": "physicalized-weights/hdl/safety_filter_core.sv; physicalized-weights/hdl/safety_filter_core.ys",
            "claim_supported": "Yosys check/synthesis reports no structural problems, no memories, and no processes for the pure combinational core.",
        },
        {
            "path": "physicalized-weights/data/prototype_verification_closure.json",
            "milestone": "M-PROTO-1",
            "evidence_type": "synthesized",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/verify_prototype_closure.py",
            "dependent_artifacts": "physicalized-weights/data/hdl_sim_results.csv; physicalized-weights/data/yosys_safety_filter.log; physicalized-weights/data/verilator_safety_filter.log",
            "claim_supported": "Hash-ties the amended Verilator/Yosys/Python/synthesis closure and records compiled Verilator as blocked by missing build tools.",
        },
        {
            "path": "physicalized-weights/docs/prototype_verification_closure.md",
            "milestone": "M-PROTO-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/data/prototype_verification_closure.json",
            "claim_supported": "Defines the narrow amended evidence contract and reopen criteria for M-PROTO-1.",
        },
        {
            "path": "physicalized-weights/docs/final_synthesis.md",
            "milestone": "M-FINAL-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/data/evidence_manifest.json; physicalized-weights/data/final_synthesis_summary.json",
            "claim_supported": "Integrates validated artifacts into the final evidence-labeled answer to the directive.",
        },
        {
            "path": "physicalized-weights/scripts/build_final_synthesis.py",
            "milestone": "M-FINAL-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/docs/final_synthesis.md; physicalized-weights/docs/reproducibility.md",
            "claim_supported": "Builds the final evidence manifest, summary JSON, and evidence map from workspace artifacts.",
        },
        {
            "path": "physicalized-weights/data/final_synthesis_summary.json",
            "milestone": "M-FINAL-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/build_final_synthesis.py",
            "dependent_artifacts": "physicalized-weights/data/breakeven_summary.json; physicalized-weights/data/target_scores_summary.json; physicalized-weights/data/prototype_summary.json; physicalized-weights/data/prototype_verification_closure.json",
            "claim_supported": "Summarizes the final conclusion, validated milestones, evidence type counts, break-even outputs, target recommendation, prototype routes, and closure status.",
        },
        {
            "path": "physicalized-weights/docs/reproducibility.md",
            "milestone": "M-FINAL-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "",
            "dependent_artifacts": "physicalized-weights/scripts/build_final_synthesis.py",
            "claim_supported": "Gives compact commands for regenerating the first-arc artifacts with current local tool limitations noted.",
        },
        {
            "path": "physicalized-weights/tests/test_final_synthesis.py",
            "milestone": "M-FINAL-1",
            "evidence_type": "simulated",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/tests/test_final_synthesis.py",
            "dependent_artifacts": "physicalized-weights/docs/final_synthesis.md; physicalized-weights/data/evidence_manifest.csv; physicalized-weights/data/final_synthesis_summary.json",
            "claim_supported": "Checks milestone coverage, manifest coverage, path existence, current hashes, evidence labels, falsification criteria, reopen rules, and no broad fixed-frontier overclaim.",
        },
        {
            "path": "physicalized-weights/data/final_evidence_map.png",
            "milestone": "M-FINAL-1",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/build_final_synthesis.py",
            "dependent_artifacts": "physicalized-weights/data/evidence_manifest.json",
            "claim_supported": "Evidence map linking validated milestones, generated artifacts, and final claims by evidence type.",
        },
        {
            "path": "physicalized-weights/docs/phase2_synthesis_downgrade.md",
            "milestone": "M-SYNTH-2",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/build_phase2_synthesis.py",
            "dependent_artifacts": "physicalized-weights/data/phase2_claim_matrix.csv; physicalized-weights/data/phase2_synthesis_summary.json",
            "claim_supported": "Downgrades the safety/filter performance/economic claim after calibrated workload and stronger-baseline replay while preserving the architecture/failure-mode value.",
        },
        {
            "path": "physicalized-weights/data/phase2_claim_matrix.csv",
            "milestone": "M-SYNTH-2",
            "evidence_type": "modeled",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/build_phase2_synthesis.py",
            "dependent_artifacts": "physicalized-weights/data/calibrated_breakeven_summary.json; physicalized-weights/data/workload_summary.json; physicalized-weights/data/stronger_baseline_summary.json",
            "claim_supported": "Machine-checkable classification of major Phase 1 claims as preserved, weakened, falsified, superseded, or open after Phase 2 evidence.",
        },
        {
            "path": "physicalized-weights/data/phase2_synthesis_summary.json",
            "milestone": "M-SYNTH-2",
            "evidence_type": "modeled",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/build_phase2_synthesis.py",
            "dependent_artifacts": "physicalized-weights/data/phase2_claim_matrix.csv; physicalized-weights/data/stronger_baseline_summary.json",
            "claim_supported": "Records zero hybrid workload wins, programmable-accelerator dominance, and the reopening standard for the safety/filter performance claim.",
        },
        {
            "path": "physicalized-weights/data/phase2_evidence_map.png",
            "milestone": "M-SYNTH-2",
            "evidence_type": "inferred",
            "validation_status": "validated",
            "generating_command": "python3 physicalized-weights/scripts/build_phase2_synthesis.py",
            "dependent_artifacts": "physicalized-weights/data/phase2_claim_matrix.csv",
            "claim_supported": "Visualizes Phase 1 and Phase 2 claim statuses after calibrated workload and stronger-baseline replay.",
        },
    ]


def write_png(path: Path, manifest_rows: list[dict[str, str]]) -> None:
    width, height = 980, 520
    image = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(width, x1), min(height, y1)
        for y in range(y0, y1):
            row = y * width * 3
            for x in range(x0, x1):
                idx = row + x * 3
                image[idx : idx + 3] = bytes(color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                idx = (y0 * width + x0) * 3
                image[idx : idx + 3] = bytes(color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    milestone_order = ["M-TAX-1", "M-MODEL-1", "M-BASE-1", "M-TARGET-1", "M-ARCH-1", "M-PROTO-1", "M-FINAL-1"]
    positions = {m: (80 + i * 130, 110 + (i % 2) * 80) for i, m in enumerate(milestone_order)}
    for a, b in zip(milestone_order, milestone_order[1:]):
        line(*positions[a], *positions[b], (190, 190, 190))
    for m, (x, y) in positions.items():
        types = sorted({r["evidence_type"] for r in manifest_rows if m in r["milestone"]})
        color = TYPE_COLORS.get(types[0], (80, 80, 80)) if types else (80, 80, 80)
        rect(x - 34, y - 24, x + 34, y + 24, color)
        rect(x - 30, y - 20, x + 30, y + 20, (255, 255, 255))
        rect(x - 24, y - 14, x + 24, y + 14, color)

    counts: dict[str, int] = {}
    for row in manifest_rows:
        counts[row["evidence_type"]] = counts.get(row["evidence_type"], 0) + 1
    x = 80
    for evidence_type, color in TYPE_COLORS.items():
        h = counts.get(evidence_type, 0) * 14
        rect(x, 380 - h, x + 70, 380, color)
        x += 105

    raw = b"".join(b"\x00" + image[y * width * 3 : (y + 1) * width * 3] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    manifest_rows = rows()
    write_png(DATA / "final_evidence_map.png", manifest_rows)
    with (DATA / "breakeven_summary.json").open() as handle:
        breakeven = json.load(handle)
    with (DATA / "target_scores_summary.json").open() as handle:
        target = json.load(handle)
    with (DATA / "prototype_summary.json").open() as handle:
        prototype = json.load(handle)
    with (DATA / "prototype_verification_closure.json").open() as handle:
        closure = json.load(handle)

    summary = {
        "schema_version": 1,
        "milestone_id": "M-FINAL-1",
        "status": "validated",
        "evidence_map_caption": "evidence map linking validated milestones, generated artifacts, and final claims, distinguishing sourced, modeled, simulated, synthesized, inferred, and speculative support.",
        "central_conclusion": "Full frontier-model fixed-weight physicalization is not supported. Narrow stable safety/filter physicalization remains useful as an architecture and failure-mode study, but Phase 2 stronger-baseline replay falsifies its current performance/economic superiority claim.",
        "validated_milestones": ["M-TAX-1", "M-MODEL-1", "M-BASE-1", "M-TARGET-1", "M-ARCH-1", "M-PROTO-1", "M-FINAL-1", "M-CAL-1", "M-WORKLOAD-1", "M-SWBASE-2", "M-SYNTH-2"],
        "artifact_count": len(manifest_rows),
        "evidence_type_counts": {kind: sum(1 for row in manifest_rows if row["evidence_type"] == kind) for kind in TYPE_COLORS},
        "break_even_winner_counts": breakeven["winner_counts"],
        "break_even_dominant_variables": breakeven["dominant_variables"],
        "target_recommendation": target["recommended_next_target"],
        "prototype_route_counts": prototype["route_counts"],
        "prototype_fast_path_fraction": prototype["fast_path_fraction"],
        "prototype_baseline_comparison": prototype["baseline_comparison"],
        "prototype_closure_status": closure["closure_status"],
        "prototype_evidence_contract": closure["evidence_contract"],
        "compiled_verilator_status": closure["compiled_verilator"]["compiled_simulation_status"],
        "reopen_criteria": closure["reopen_criteria"],
    }
    phase2_summary_path = DATA / "phase2_synthesis_summary.json"
    if phase2_summary_path.exists():
        phase2 = json.loads(phase2_summary_path.read_text())
        summary["phase2_hybrid_workload_wins"] = phase2["hybrid_workload_wins"]
        summary["phase2_preserved_case_winner"] = phase2["preserved_case_winner"]
        summary["phase2_reopening_standard"] = phase2["reopening_standard"]
    (DATA / "final_synthesis_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for row in manifest_rows:
        path = ROOT / row["path"]
        if not path.exists():
            raise FileNotFoundError(row["path"])
        row["artifact_hash"] = sha256(path)

    csv_path = DATA / "evidence_manifest.csv"
    json_path = DATA / "evidence_manifest.json"
    fields = [
        "path",
        "milestone",
        "evidence_type",
        "validation_status",
        "generating_command",
        "artifact_hash",
        "dependent_artifacts",
        "claim_supported",
    ]
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(manifest_rows)
    json_path.write_text(json.dumps(manifest_rows, indent=2) + "\n")
    print(f"wrote {csv_path}")
    print(f"wrote {json_path}")
    print(f"wrote {DATA / 'final_synthesis_summary.json'}")
    print(f"wrote {DATA / 'final_evidence_map.png'}")
    print("artifact_count:", len(manifest_rows))


if __name__ == "__main__":
    main()
