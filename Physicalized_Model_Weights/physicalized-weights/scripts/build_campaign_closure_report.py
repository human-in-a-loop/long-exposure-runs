# created: 2026-05-13T19:08:00Z
# cycle: 9
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-CLOSURE-1
"""Build the campaign-level closure report.

This is a reporting projection over validated milestones. It must not add a
model, evaluator, gate, or synthetic evidence path.
"""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"
TEST_PATH = ROOT / "physicalized-weights" / "tests" / "test_campaign_closure_report.py"

REPORT_MD = DOCS / "campaign_closure_report.md"
EXEC_SUMMARY_MD = DOCS / "campaign_executive_summary.md"
FINAL_SYNTHESIS_MD = DOCS / "final_synthesis.md"
REPRO_MD = DOCS / "reproducibility.md"
CLAIMS_CSV = DATA / "campaign_closure_claim_disposition.csv"
MANIFEST_CSV = DATA / "campaign_closure_manifest.csv"
SUMMARY_JSON = DATA / "campaign_closure_summary.json"
FLOW_PNG = DATA / "campaign_closure_evidence_flow.png"

FIGURE_CAPTION = (
    "Campaign evidence flow from taxonomy and modeling through Phase 2 downgrade, "
    "Phase 3/4 reopen pathway, robustness stress test, deferral watchlist, and "
    "final current-evidence closure."
)

COMMANDS = [
    "python3 physicalized-weights/scripts/build_campaign_closure_report.py",
    "python3 physicalized-weights/tests/test_campaign_closure_report.py",
    "file physicalized-weights/data/campaign_closure_evidence_flow.png",
    "python3 -m long_exposure.tools.promise_check .",
    "python3 -m long_exposure.tools.org_check .",
]

REQUIRED_INPUTS: dict[str, list[Path]] = {
    "M-TAX-1": [DOCS / "taxonomy_and_null.md"],
    "M-MODEL-1": [DATA / "breakeven_summary.json"],
    "M-TARGET-1": [DATA / "target_scores_summary.json", DOCS / "target_ranking.md"],
    "M-ARCH-1": [DOCS / "hybrid_safety_filter_architecture.md"],
    "M-PROTO-1": [
        DATA / "prototype_verification_closure.json",
        DATA / "hdl_sim_results.csv",
        DOCS / "prototype_verification_closure.md",
    ],
    "M-SWBASE-2": [DATA / "stronger_baseline_summary.json", DOCS / "stronger_baseline_comparison.md"],
    "M-SYNTH-2": [DATA / "phase2_synthesis_summary.json", DOCS / "phase2_synthesis_downgrade.md"],
    "M-PHASE3-SYNTH-1": [DATA / "phase3_reopen_summary.json", DOCS / "phase3_reopen_pathway_summary.md"],
    "M-PHASE4-SYNTH-1": [DATA / "phase4_reopen_summary.json", DOCS / "phase4_reopen_lifecycle_synthesis.md"],
    "M-ROBUST-1": [DATA / "target_robustness_summary.json", DOCS / "target_robustness_stress_test.md"],
    "M-DEFER-1": [
        DATA / "campaign_deferral_watchlist_summary.json",
        DATA / "campaign_deferral_watchlist_results.csv",
        DOCS / "campaign_deferral_watchlist.md",
    ],
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_inputs() -> None:
    missing = [rel(path) for paths in REQUIRED_INPUTS.values() for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing closure input artifacts: " + ", ".join(missing))


def load_inputs() -> dict[str, Any]:
    require_inputs()
    return {
        "breakeven": read_json(DATA / "breakeven_summary.json"),
        "target": read_json(DATA / "target_scores_summary.json"),
        "prototype": read_json(DATA / "prototype_verification_closure.json"),
        "stronger": read_json(DATA / "stronger_baseline_summary.json"),
        "phase2": read_json(DATA / "phase2_synthesis_summary.json"),
        "phase3": read_json(DATA / "phase3_reopen_summary.json"),
        "phase4": read_json(DATA / "phase4_reopen_summary.json"),
        "robust": read_json(DATA / "target_robustness_summary.json"),
        "defer": read_json(DATA / "campaign_deferral_watchlist_summary.json"),
        "defer_rows": read_csv(DATA / "campaign_deferral_watchlist_results.csv"),
    }


def claim_rows(inputs: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "claim_id": "full_frontier_fixed_weight_physicalization",
            "disposition": "rejected_under_current_evidence",
            "evidence_level": "taxonomy_and_modeled_null",
            "supporting_artifacts": "physicalized-weights/docs/taxonomy_and_null.md; physicalized-weights/data/breakeven_summary.json",
            "current_measured_evidence": "false",
            "conclusion": "Full frontier-model fixed-weight physicalization remains rejected absent evidence closing update, yield, integration, and programmable-baseline burdens.",
        },
        {
            "claim_id": "safety_filter_performance_superiority",
            "disposition": "falsified_under_stronger_programmable_baseline",
            "evidence_level": "calibrated_equal_workload_replay",
            "supporting_artifacts": "physicalized-weights/data/phase2_synthesis_summary.json; physicalized-weights/data/stronger_baseline_summary.json; physicalized-weights/docs/stronger_baseline_comparison.md",
            "current_measured_evidence": "false",
            "conclusion": "The safety/filter hybrid wins zero Phase 2 workload scenarios against the stronger programmable baseline.",
        },
        {
            "claim_id": "hybrid_architecture_failure_mode_value",
            "disposition": "retained_as_architecture_and_failure_mode_study",
            "evidence_level": "architecture_design",
            "supporting_artifacts": "physicalized-weights/docs/hybrid_safety_filter_architecture.md; physicalized-weights/docs/campaign_deferral_watchlist.md",
            "current_measured_evidence": "false",
            "conclusion": "The hybrid architecture remains useful for interface, fallback, audit, update, and failure-mode reasoning, not as a current winner.",
        },
        {
            "claim_id": "prototype_hdl_evidence",
            "disposition": "retained_as_bounded_prototype_evidence",
            "evidence_level": "python_yosys_verilator_lint_graphviz",
            "supporting_artifacts": "physicalized-weights/data/prototype_verification_closure.json; physicalized-weights/docs/prototype_verification_closure.md; physicalized-weights/data/hdl_sim_results.csv",
            "current_measured_evidence": "false",
            "conclusion": "The fixed classifier prototype has bounded combinational closure evidence; compiled Verilator remains blocked by unavailable build tools.",
        },
        {
            "claim_id": "future_measured_reopen_path",
            "disposition": "complete_but_inactive_absent_actual_measured_evidence",
            "evidence_level": "phase4_lifecycle_and_uncertainty_contract",
            "supporting_artifacts": "physicalized-weights/data/phase4_reopen_summary.json; physicalized-weights/docs/phase4_reopen_lifecycle_synthesis.md",
            "current_measured_evidence": "false",
            "conclusion": "Future restart uses the existing Phase 4 conjunction; no current artifact is an actual reopen candidate.",
        },
        {
            "claim_id": "non_safety_target_robustness",
            "disposition": "no_calibrated_current_superiority_claim",
            "evidence_level": "target_class_stress_test",
            "supporting_artifacts": "physicalized-weights/data/target_robustness_summary.json; physicalized-weights/docs/target_robustness_stress_test.md",
            "current_measured_evidence": "false",
            "conclusion": "M-ROBUST-1 found zero calibrated physicalized wins across target classes; favorable-plausible wins are not current evidence.",
        },
        {
            "claim_id": "campaign_deferral_state",
            "disposition": "closed_under_current_evidence_deferred_until_valid_measured_package",
            "evidence_level": "deferral_watchlist",
            "supporting_artifacts": "physicalized-weights/data/campaign_deferral_watchlist_summary.json; physicalized-weights/data/campaign_deferral_watchlist_results.csv; physicalized-weights/docs/campaign_deferral_watchlist.md",
            "current_measured_evidence": "false",
            "conclusion": "The campaign is closed under current evidence and defers future work unless real lifecycle-valid measured evidence appears.",
        },
    ]


def guard_invariants(inputs: dict[str, Any], rows: list[dict[str, str]]) -> None:
    if inputs["phase4"].get("actual_reopen_candidate_count") != 0:
        raise RuntimeError("Phase 4 reports a current actual reopen candidate")
    if inputs["defer"].get("new_reopen_gate_count") != 0:
        raise RuntimeError("Deferral summary reports a new reopen gate")
    if inputs["defer"].get("current_superiority_claim_count") != 0:
        raise RuntimeError("Deferral summary reports a current superiority claim")
    if inputs["robust"].get("current_superiority_claim_count") != 0:
        raise RuntimeError("Robustness summary reports a current superiority claim")
    for row in rows:
        supports = [item.strip() for item in row["supporting_artifacts"].split(";") if item.strip()]
        if not supports:
            raise RuntimeError(f"Claim lacks support: {row['claim_id']}")
        for support in supports:
            if not (ROOT / support).exists():
                raise RuntimeError(f"Missing support for {row['claim_id']}: {support}")


def write_claims(rows: list[dict[str, str]]) -> None:
    fields = [
        "claim_id",
        "disposition",
        "evidence_level",
        "supporting_artifacts",
        "current_measured_evidence",
        "conclusion",
    ]
    with CLAIMS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_png(path: Path) -> None:
    width, height = 1100, 450
    pixels = bytearray([248, 249, 247] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            offset = (y * width + max(0, x0)) * 3
            for _ in range(max(0, x0), min(width, x1)):
                pixels[offset : offset + 3] = bytes(color)
                offset += 3

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                idx = (y0 * width + x0) * 3
                pixels[idx : idx + 3] = bytes(color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    colors = [
        (83, 113, 157),
        (80, 145, 116),
        (184, 82, 72),
        (131, 105, 166),
        (204, 139, 66),
        (84, 143, 154),
        (70, 70, 70),
    ]
    points = [(85 + i * 155, 185 + (i % 2) * 48) for i in range(7)]
    rect(35, 52, 1065, 330, (236, 240, 242))
    for a, b in zip(points, points[1:]):
        line(a[0], a[1], b[0], b[1], (145, 154, 165))
        line(a[0], a[1] + 1, b[0], b[1] + 1, (145, 154, 165))
    for (x, y), color in zip(points, colors):
        rect(x - 52, y - 35, x + 52, y + 35, color)
        rect(x - 39, y - 22, x + 39, y + 22, (255, 255, 255))
        rect(x - 27, y - 10, x + 27, y + 10, color)
    rect(885, 360, 1025, 392, (184, 82, 72))
    rect(885, 397, 1025, 424, (70, 70, 70))

    raw = b"".join(b"\x00" + bytes(pixels[y * width * 3 : (y + 1) * width * 3]) for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def build_summary(inputs: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "milestone_id": "M-CLOSURE-1",
        "status": "validated",
        "current_superiority_claim_count": 0,
        "actual_reopen_candidate_count": inputs["phase4"].get("actual_reopen_candidate_count", 0),
        "new_reopen_gate_count": inputs["defer"].get("new_reopen_gate_count", 0),
        "current_artifacts_reopen": False,
        "phase4_future_reopen_condition_unchanged": inputs["defer"].get("phase4_future_reopen_condition_unchanged", False),
        "current_measured_evidence_available": False,
        "claim_count": len(rows),
        "claim_ids": [row["claim_id"] for row in rows],
        "disposition_counts": {key: sum(1 for row in rows if row["disposition"] == key) for key in sorted({row["disposition"] for row in rows})},
        "stronger_baseline_winner_counts": inputs["stronger"].get("winner_counts", {}),
        "phase2_hybrid_workload_wins": inputs["phase2"].get("hybrid_workload_wins", 0),
        "robust_calibrated_physicalized_win_count": inputs["robust"].get("calibrated_physicalized_win_count", 0),
        "deferral_insufficient_trigger_ids": inputs["defer"].get("insufficient_trigger_ids", []),
        "deferral_measured_reopen_trigger_ids": inputs["defer"].get("measured_reopen_trigger_ids", []),
        "future_reopen_condition": inputs["phase4"].get("future_reopen_condition", ""),
        "figure_caption": FIGURE_CAPTION,
        "interpretation": (
            "The campaign is closed under current evidence: no current physicalized-weight performance/economic "
            "superiority claim is supported, no current artifact reopens the Phase 2 downgrade, architecture and "
            "prototype value are retained, and future evaluation is deferred until actual lifecycle-valid measured evidence appears."
        ),
    }


def disposition_table(rows: list[dict[str, str]]) -> str:
    lines = ["| Claim | Disposition | Support |", "|---|---|---|"]
    for row in rows:
        support = "<br>".join(f"`{item.strip()}`" for item in row["supporting_artifacts"].split(";"))
        lines.append(f"| `{row['claim_id']}` | {row['disposition']} | {support} |")
    return "\n".join(lines)


def write_report(summary: dict[str, Any], rows: list[dict[str, str]], inputs: dict[str, Any]) -> None:
    measured = ", ".join(f"`{item}`" for item in summary["deferral_measured_reopen_trigger_ids"])
    insufficient = ", ".join(f"`{item}`" for item in summary["deferral_insufficient_trigger_ids"])
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T19:08:00Z
cycle: 9
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-CLOSURE-1
---

# Campaign Closure Report

## Directive Restatement

The campaign investigated whether useful portions of neural-network inference can be physicalized into hardware, with artifacts kept under `<workspace>`, and with Wolfram, Verilator, Yosys, and Graphviz used where they added tractable evidence.

## Method Summary By Phase

- Phase 1 defined the physicalization taxonomy, strongest null hypothesis, break-even model, target ranking, hybrid safety/filter architecture, and bounded prototype.
- Phase 2 calibrated the safety/filter case against workload assumptions and stronger optimized-software and programmable-accelerator baselines.
- Phase 3 and Phase 4 built the measured evidence pathway: production trace schema, ingestion admissibility, replayable evidence packs, uncertainty durability, and lifecycle terminal states.
- M-ROBUST-1 stress-tested non-safety target classes against the stronger programmable baseline.
- M-DEFER-1 converted the validated negative endpoint into a deferral watchlist so future cycles do not treat substitutes as measured evidence.

## Final Claim Disposition

{disposition_table(rows)}

## Strongest Null Hypothesis And Outcome

The operative null was that software/runtime improvements and programmable accelerators capture the practical benefit before a fixed physical substrate can amortize substrate, update, yield, integration, fallback, and audit costs. Current artifacts support the null for performance/economic superiority: `phase2_hybrid_workload_wins = {summary['phase2_hybrid_workload_wins']}`, `robust_calibrated_physicalized_win_count = {summary['robust_calibrated_physicalized_win_count']}`, and `current_superiority_claim_count = {summary['current_superiority_claim_count']}`.

## Why Safety/Filter Moved From Plausible To Falsified

Phase 1 identified safety/filter as a plausible narrow target because it had stable features, high reuse, and a bounded fallback architecture. Phase 2 replayed that target under equal workload accounting and a stronger programmable accelerator; the stronger baseline won nine of ten scenarios, optimized software won the zero-invocation control, and the hybrid won zero scenarios.

## What Remains Valuable

The architecture and prototype remain valuable as a bounded study of interfaces, fixed-policy versioning, confidence/fallback behavior, audit hooks, HDL equivalence, and closure criteria. That is different from a performance or economic win: the retained value is design and verification evidence, not a claim that fixed weights beat programmable baselines.

## Why Current Artifacts Cannot Reopen

Current artifacts report `actual_reopen_candidate_count = {summary['actual_reopen_candidate_count']}`, `current_artifacts_reopen = false`, and `new_reopen_gate_count = {summary['new_reopen_gate_count']}`. Synthetic traces, local proxy timing, vendor-only claims, templates, dry-runs, intake rehearsals, lifecycle controls, and point crossings without uncertainty durability remain non-evidence for reopening.

## Future Evidence Triggers

M-DEFER-1 preserves restart triggers without creating new gates. Measured reopen triggers are {measured}; insufficient substitutes are {insufficient}. Any future performance/economic restart must use the existing Phase 4 condition:

```text
{summary['future_reopen_condition']}
```

![{FIGURE_CAPTION}](../data/campaign_closure_evidence_flow.png)

## Artifact Reproduction Commands

Run from `<workspace>`:

```bash
{chr(10).join(COMMANDS)}
```
""",
        encoding="utf-8",
    )


def write_executive_summary(summary: dict[str, Any]) -> None:
    EXEC_SUMMARY_MD.write_text(
        f"""---
created: 2026-05-13T19:08:00Z
cycle: 9
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-CLOSURE-1
---

# Campaign Executive Summary

## What Was Tested

The campaign tested whether fixed or semi-fixed physicalized neural-network inference components can beat optimized software and programmable accelerators after update cadence, utilization, fallback, audit, yield, integration, and lifecycle evidence are counted.

## What Won

The strong programmable accelerator baseline won the current performance/economic comparison. The hybrid safety/filter architecture won only as a retained architecture and verification study.

## What Failed

Full frontier fixed-weight physicalization is rejected under current evidence, and safety/filter performance superiority is falsified under the stronger equal-workload baseline. Synthetic, proxy, template, rehearsal, vendor-only, and dry-run artifacts are not measured evidence.

## What Would Change The Answer

A future production, shadow, or canary evidence package could restart the existing Phase 4 evaluation only if it has valid hashes, schema compatibility, admissible ingestion, measured terms, provenance and privacy attestations, nonzero accepted fast-path volume, measured best programmable baseline, threshold crossing, uncertainty durability, and lifecycle terminal state `actual_reopen_candidate`.

## Where Artifacts Live

The closure report is `physicalized-weights/docs/campaign_closure_report.md`, the claim table is `physicalized-weights/data/campaign_closure_claim_disposition.csv`, the manifest is `physicalized-weights/data/campaign_closure_manifest.csv`, and the closure summary is `physicalized-weights/data/campaign_closure_summary.json`.
""",
        encoding="utf-8",
    )


def replace_section(text: str, heading: str, section: str) -> str:
    marker = f"\n## {heading}\n"
    if marker not in text:
        return text.rstrip() + "\n" + marker + "\n" + section.strip() + "\n"
    start = text.index(marker) + 1
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[:start] + f"## {heading}\n\n" + section.strip() + "\n"
    return text[:start] + f"## {heading}\n\n" + section.strip() + "\n" + text[next_start:]


def update_final_synthesis(summary: dict[str, Any]) -> None:
    section = f"""M-CLOSURE-1 is the reader-facing final disposition layer for the current evidence package. It consolidates the taxonomy, models, target ranking, architecture/prototype, Phase 2 stronger-baseline downgrade, Phase 3/4 reopen pathway, M-ROBUST-1 target-class stress test, and M-DEFER-1 deferral watchlist.

The closure state is: no current physicalized-weight performance/economic superiority claim, no current reopen candidate, retained architecture/prototype value, and explicit deferral until genuinely new measured evidence appears. The generated closure report is `physicalized-weights/docs/campaign_closure_report.md`; the executive summary is `physicalized-weights/docs/campaign_executive_summary.md`; the claim table is `physicalized-weights/data/campaign_closure_claim_disposition.csv`; the manifest is `physicalized-weights/data/campaign_closure_manifest.csv`.

Counters preserved by the closure package: `current_superiority_claim_count = {summary['current_superiority_claim_count']}`, `actual_reopen_candidate_count = {summary['actual_reopen_candidate_count']}`, and `new_reopen_gate_count = {summary['new_reopen_gate_count']}`. Deferral state: `closed_under_current_evidence_deferred_until_valid_measured_package`."""
    text = FINAL_SYNTHESIS_MD.read_text(encoding="utf-8")
    FINAL_SYNTHESIS_MD.write_text(replace_section(text, "Campaign Closure Disposition", section), encoding="utf-8")


def update_reproducibility() -> None:
    section = f"""Replay the campaign closure reporting layer:

```bash
{chr(10).join(COMMANDS)}
```

Expected invariant outputs:

- `physicalized-weights/data/campaign_closure_summary.json` reports `current_superiority_claim_count: 0`.
- `physicalized-weights/data/campaign_closure_summary.json` reports `actual_reopen_candidate_count: 0`.
- `physicalized-weights/data/campaign_closure_summary.json` reports `new_reopen_gate_count: 0`.
- `physicalized-weights/docs/campaign_executive_summary.md` keeps synthetic, proxy, template, rehearsal, vendor-only, and dry-run artifacts out of measured-evidence status."""
    text = REPRO_MD.read_text(encoding="utf-8")
    REPRO_MD.write_text(replace_section(text, "Campaign Closure Replay", section), encoding="utf-8")


def write_manifest() -> None:
    rows: list[dict[str, str]] = []
    for milestone, paths in REQUIRED_INPUTS.items():
        for path in paths:
            rows.append(
                {
                    "milestone_id": milestone,
                    "artifact_path": rel(path),
                    "artifact_sha256": sha256(path),
                    "artifact_role": "input",
                    "replay_command": "",
                }
            )
    outputs = [
        Path(__file__).resolve(),
        TEST_PATH,
        REPORT_MD,
        EXEC_SUMMARY_MD,
        FINAL_SYNTHESIS_MD,
        REPRO_MD,
        CLAIMS_CSV,
        MANIFEST_CSV,
        SUMMARY_JSON,
        FLOW_PNG,
    ]
    for path in outputs:
        rows.append(
            {
                "milestone_id": "M-CLOSURE-1",
                "artifact_path": rel(path),
                "artifact_sha256": "self_referential_manifest" if path == MANIFEST_CSV else sha256(path),
                "artifact_role": "implementation" if path in {Path(__file__).resolve(), TEST_PATH} else "output",
                "replay_command": "python3 physicalized-weights/scripts/build_campaign_closure_report.py",
            }
        )
    fields = ["milestone_id", "artifact_path", "artifact_sha256", "artifact_role", "replay_command"]
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    inputs = load_inputs()
    rows = claim_rows(inputs)
    guard_invariants(inputs, rows)
    write_claims(rows)
    write_png(FLOW_PNG)
    summary = build_summary(inputs, rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary, rows, inputs)
    write_executive_summary(summary)
    update_final_synthesis(summary)
    update_reproducibility()
    write_manifest()
    for path in [REPORT_MD, EXEC_SUMMARY_MD, FINAL_SYNTHESIS_MD, REPRO_MD, CLAIMS_CSV, MANIFEST_CSV, SUMMARY_JSON, FLOW_PNG]:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
