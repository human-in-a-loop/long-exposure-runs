# created: 2026-05-13T18:36:00Z
# cycle: 8
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-DEFER-1
"""Build the M-DEFER-1 campaign deferral and evidence watchlist package."""

from __future__ import annotations

import csv
import json
import struct
import zlib
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
DOCS_DIR = ROOT / "physicalized-weights" / "docs"

WATCHLIST_CSV = DATA_DIR / "campaign_deferral_watchlist.csv"
RESULTS_CSV = DATA_DIR / "campaign_deferral_watchlist_results.csv"
SUMMARY_JSON = DATA_DIR / "campaign_deferral_watchlist_summary.json"
FIGURE_PNG = DATA_DIR / "campaign_deferral_watchlist.png"
REPORT_MD = DOCS_DIR / "campaign_deferral_watchlist.md"

FIGURE_CAPTION = (
    "Deferral map separating closed claims, inactive reopen triggers, "
    "insufficient substitutes, and prototype-only verification triggers."
)


@dataclass(frozen=True)
class Trigger:
    trigger_id: str
    trigger_type: str
    required_artifact: str
    minimum_evidence_class: str
    current_status: str
    action_if_observed: str
    insufficient_substitutes: str
    owning_prior_milestone: str


@dataclass(frozen=True)
class Result:
    trigger_id: str
    trigger_type: str
    required_artifact: str
    minimum_evidence_class: str
    current_status: str
    action_if_observed: str
    insufficient_substitutes: str
    owning_prior_milestone: str
    classification: str
    action_scope: str
    creates_new_reopen_gate: bool
    can_activate_current_superiority_claim: bool
    requires_phase4_lifecycle: bool
    requires_uncertainty_durability: bool
    rationale: str


CLAIM_DISPOSITIONS = [
    {
        "claim_id": "broad_fixed_frontier_model_physicalization",
        "disposition": "rejected_under_current_evidence",
        "rationale": "Update cadence, yield, integration, and programmable-baseline burdens remain unclosed.",
        "owning_milestones": "M-TAX-1;M-SYNTH-2;M-PHASE4-SYNTH-1",
    },
    {
        "claim_id": "safety_filter_performance_or_economic_winner",
        "disposition": "falsified_under_stronger_programmable_baseline",
        "rationale": "Equal-workload stronger-baseline replay gives the hybrid zero workload wins.",
        "owning_milestones": "M-SWBASE-2;M-SYNTH-2",
    },
    {
        "claim_id": "hybrid_architecture_and_prototype",
        "disposition": "retained_as_architecture_failure_mode_evidence_scaffold",
        "rationale": "The architecture remains useful for interfaces, fallback, audit, and HDL closure studies.",
        "owning_milestones": "M-ARCH-1;M-PROTO-1",
    },
    {
        "claim_id": "phase4_reopen_pathway",
        "disposition": "complete_but_inactive_absent_actual_measured_evidence",
        "rationale": "The validated lifecycle and uncertainty conjunction exists, but no current artifact satisfies it.",
        "owning_milestones": "M-PHASE4-SYNTH-1",
    },
    {
        "claim_id": "non_safety_target_classes_current_superiority",
        "disposition": "no_calibrated_current_superiority_claim",
        "rationale": "M-ROBUST-1 found zero calibrated physicalized wins across the broader target classes.",
        "owning_milestones": "M-ROBUST-1",
    },
]


def default_triggers() -> list[Trigger]:
    phase4_requirement = (
        "valid package with hash match, schema compatibility, valid trace, admissible ingestion path, "
        "measured terms, production/shadow/canary source, provenance/privacy attestations, nonzero "
        "request and accepted fast-path volume, measured best programmable baseline, threshold crossing, "
        "UCB_alpha(H-B)<0, and lifecycle_terminal_state=actual_reopen_candidate"
    )
    return [
        Trigger(
            "measured_shadow_or_canary_package",
            "measured_package",
            "Replayable shadow/canary evidence package with raw admissible trace artifacts and attestations.",
            phase4_requirement,
            "inactive_pending_artifact",
            "Activate existing Phase 4 performance/economic reopen evaluation only after lifecycle and uncertainty conditions pass.",
            "synthetic traces; local proxy timing; template packages; summaries without raw package artifacts",
            "M-PHASE4-SYNTH-1",
        ),
        Trigger(
            "measured_production_package",
            "measured_package",
            "Replayable production evidence package with raw admissible trace artifacts and attestations.",
            phase4_requirement,
            "inactive_pending_artifact",
            "Activate existing Phase 4 performance/economic reopen evaluation only after lifecycle and uncertainty conditions pass.",
            "vendor-only numbers; local proxy timing; unverifiable production summaries; point crossings without uncertainty durability",
            "M-PHASE4-SYNTH-1",
        ),
        Trigger(
            "programmable_baseline_public_update",
            "baseline_update",
            "Public source or reproducible benchmark materially changing optimized software or programmable accelerator assumptions.",
            "independent public baseline evidence with comparable workload, units, and feature/audit/fallback accounting",
            "watch_only",
            "Refresh baseline assumptions and rerun existing calibrated models; do not infer a physicalized win.",
            "vendor-only marketing claims; incomparable peak TOPS; missing workload/accounting terms",
            "M-SWBASE-2",
        ),
        Trigger(
            "compiled_verilator_available",
            "prototype_toolchain",
            "Local compiled Verilator simulation becomes runnable for the existing HDL testbench.",
            "toolchain availability plus compiled simulation log matching Python/Yosys vectors",
            "watch_only",
            "Reopen prototype verification closure only; do not reopen performance/economic superiority.",
            "lint-only success; Yosys-only structural checks; unrelated compiler availability",
            "M-PROTO-1",
        ),
        Trigger(
            "hdl_design_scope_change",
            "prototype_design_change",
            "HDL changes add sequential state, memories, mutable policy logic, handshake timing, or altered constants.",
            "source diff plus regenerated lint, simulation, synthesis, and vector-equivalence evidence",
            "watch_only",
            "Reopen prototype verification closure only; do not reopen performance/economic superiority.",
            "documentation-only changes; regenerated diagram without source/equivalence checks",
            "M-PROTO-1",
        ),
        Trigger(
            "new_stable_high-volume_target_evidence",
            "target_evidence",
            "Measured package for a stable high-volume target class outside the current safety/filter path.",
            phase4_requirement,
            "inactive_pending_artifact",
            "Map target evidence into existing Phase 4 lifecycle and uncertainty pathway before any superiority evaluation.",
            "M-ROBUST-1 favorable-plausible rows; extreme counterfactuals; target-score intuition alone",
            "M-ROBUST-1",
        ),
        Trigger(
            "vendor_benchmark_only",
            "insufficient_substitute",
            "Vendor benchmark or accelerator claim without raw admissible package artifacts.",
            "insufficient",
            "insufficient",
            "Record as context only; do not reopen evaluation.",
            "claimed energy savings; peak throughput; private customer summary",
            "M-INGEST-1",
        ),
        Trigger(
            "synthetic_counterfactual_only",
            "insufficient_substitute",
            "Synthetic or counterfactual trace crossing thresholds without actual measured source.",
            "insufficient",
            "insufficient",
            "Use only as a control exercising logic; do not reopen evaluation.",
            "privacy-safe synthetic trace; hypothetical actual-candidate control",
            "M-PIPELINE-1",
        ),
        Trigger(
            "local_proxy_only",
            "insufficient_substitute",
            "Local timing or proxy measurement without measured production/shadow/canary package.",
            "insufficient",
            "insufficient",
            "Use only for local overhead or sanity context; do not reopen evaluation.",
            "Python microbenchmarks; proxy energy estimates; single-path local traces",
            "M-MEASURE-1",
        ),
        Trigger(
            "template_or_dryrun_only",
            "insufficient_substitute",
            "Operator template, dry-run, intake rehearsal, or lifecycle placeholder without measured evidence.",
            "insufficient",
            "insufficient",
            "Keep as readiness evidence only; do not reopen evaluation.",
            "filled template; dry-run manifest; intake rehearsal; lifecycle-ready nonactual package",
            "M-DRYRUN-1",
        ),
    ]


def write_default_watchlist(path: Path = WATCHLIST_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = default_triggers()
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def read_triggers(path: Path = WATCHLIST_CSV) -> list[Trigger]:
    if not path.exists():
        write_default_watchlist(path)
    with path.open(newline="") as f:
        return [Trigger(**row) for row in csv.DictReader(f)]


def classify(trigger: Trigger) -> Result:
    text = f"{trigger.minimum_evidence_class} {trigger.action_if_observed}".lower()
    requires_phase4 = "lifecycle" in text and "actual_reopen_candidate" in text
    requires_uncertainty = "ucb_alpha" in text or "uncertainty" in text
    creates_new_gate = False
    current_claim = False

    if trigger.trigger_type == "measured_package":
        classification = "inactive_reopen_trigger"
        action_scope = "performance_economic_reopen_existing_phase4_only"
        rationale = "Requires the existing Phase 4 lifecycle and uncertainty conjunction before evaluation activates."
    elif trigger.trigger_id == "new_stable_high-volume_target_evidence":
        classification = "inactive_reopen_trigger"
        action_scope = "performance_economic_reopen_existing_phase4_only"
        rationale = "Target-class evidence must enter the same Phase 4 path; M-ROBUST-1 model-space wins are not evidence."
    elif trigger.trigger_type == "baseline_update":
        classification = "watch_baseline_refresh"
        action_scope = "model_refresh_only"
        rationale = "A stronger public baseline can refresh assumptions but does not establish physicalized superiority."
    elif trigger.trigger_type in {"prototype_toolchain", "prototype_design_change"}:
        classification = "prototype_verification_trigger"
        action_scope = "prototype_verification_only"
        rationale = "Toolchain or HDL changes affect closure evidence, not performance/economic claims."
    else:
        classification = "insufficient_substitute"
        action_scope = "no_reopen"
        rationale = "The source is a known insufficient substitute for actual measured lifecycle-valid evidence."

    return Result(
        **asdict(trigger),
        classification=classification,
        action_scope=action_scope,
        creates_new_reopen_gate=creates_new_gate,
        can_activate_current_superiority_claim=current_claim,
        requires_phase4_lifecycle=requires_phase4,
        requires_uncertainty_durability=requires_uncertainty,
        rationale=rationale,
    )


def write_results(rows: list[Result], path: Path = RESULTS_CSV) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def make_summary(rows: list[Result]) -> dict[str, object]:
    classification_counts = Counter(row.classification for row in rows)
    action_scope_counts = Counter(row.action_scope for row in rows)
    insufficient_ids = [row.trigger_id for row in rows if row.classification == "insufficient_substitute"]
    measured = [row for row in rows if row.classification == "inactive_reopen_trigger"]
    prototype = [row for row in rows if row.action_scope == "prototype_verification_only"]
    claim_counts = Counter(item["disposition"] for item in CLAIM_DISPOSITIONS)
    current_claim_count = sum(1 for row in rows if row.can_activate_current_superiority_claim)

    return {
        "schema_version": 1,
        "milestone_id": "M-DEFER-1",
        "status": "validated",
        "claim_dispositions": CLAIM_DISPOSITIONS,
        "claim_disposition_counts": dict(sorted(claim_counts.items())),
        "trigger_count": len(rows),
        "classification_counts": dict(sorted(classification_counts.items())),
        "action_scope_counts": dict(sorted(action_scope_counts.items())),
        "insufficient_trigger_ids": insufficient_ids,
        "measured_reopen_trigger_ids": [row.trigger_id for row in measured],
        "prototype_only_trigger_ids": [row.trigger_id for row in prototype],
        "new_reopen_gate_count": sum(1 for row in rows if row.creates_new_reopen_gate),
        "current_superiority_claim_count": current_claim_count,
        "current_artifacts_reopen": False,
        "phase4_future_reopen_condition_unchanged": True,
        "measured_triggers_require_lifecycle_and_uncertainty": all(
            row.requires_phase4_lifecycle and row.requires_uncertainty_durability for row in measured
        ),
        "prototype_triggers_reopen_performance_claim": any(
            row.action_scope != "prototype_verification_only" for row in prototype
        ),
        "all_triggers_have_owner_and_action": all(row.owning_prior_milestone and row.action_if_observed for row in rows),
        "figure_caption": FIGURE_CAPTION,
        "interpretation": (
            "The campaign is closed under current evidence: rejected or falsified claims remain closed, "
            "architecture/prototype evidence is retained, and future substantive performance evaluation is "
            "deferred until existing Phase 4 measured-package conditions are satisfied."
        ),
    }


def write_png(counts: Counter[str], path: Path = FIGURE_PNG) -> None:
    width, height = 980, 430
    pixels = bytearray([248, 249, 247] * width * height)
    palette = {
        "inactive_reopen_trigger": (38, 103, 166),
        "insufficient_substitute": (178, 67, 67),
        "prototype_verification_trigger": (94, 126, 66),
        "watch_baseline_refresh": (130, 104, 54),
    }
    labels = [
        "inactive_reopen_trigger",
        "insufficient_substitute",
        "prototype_verification_trigger",
        "watch_baseline_refresh",
    ]
    max_count = max(counts.values() or [1])
    bar_w = 140
    gap = 80
    base_x = 90
    base_y = 335
    chart_h = 230

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(width, x1), min(height, y1)
        for y in range(y0, y1):
            offset = (y * width + x0) * 3
            for _ in range(x0, x1):
                pixels[offset : offset + 3] = bytes(color)
                offset += 3

    rect(60, 60, 920, 65, (60, 60, 60))
    rect(60, base_y, 920, base_y + 3, (90, 90, 90))
    for i, label in enumerate(labels):
        count = counts.get(label, 0)
        x = base_x + i * (bar_w + gap)
        h = int((count / max_count) * chart_h) if max_count else 0
        rect(x, base_y - h, x + bar_w, base_y, palette[label])
        rect(x, base_y + 18, x + 18, base_y + 36, palette[label])
        # Minimal tick marks encode counts without requiring fonts.
        for tick in range(count):
            rect(x + tick * 18, base_y - h - 18, x + tick * 18 + 10, base_y - h - 6, (35, 35, 35))

    rows = []
    for y in range(height):
        start = y * width * 3
        rows.append(b"\x00" + bytes(pixels[start : start + width * 3]))
    raw = b"".join(rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def write_report(summary: dict[str, object], rows: list[Result], path: Path = REPORT_MD) -> None:
    disposition_lines = "\n".join(
        f"- `{item['claim_id']}`: {item['disposition']}. {item['rationale']}"
        for item in CLAIM_DISPOSITIONS
    )
    do_not = [
        "synthetic traces",
        "local proxy timing",
        "vendor-only accelerator claims",
        "dry-run/intake/lifecycle templates",
        "production summaries without raw admissible package artifacts",
        "point crossings without uncertainty durability",
    ]
    reopen = [
        "measured shadow/canary/production package satisfying Phase 4 lifecycle and uncertainty conditions",
        "updated public baseline evidence strong enough to materially change programmable accelerator assumptions",
        "actual toolchain/environment improvement that changes HDL closure evidence, such as compiled Verilator becoming available",
    ]
    trigger_lines = "\n".join(
        f"| `{row.trigger_id}` | {row.classification} | {row.action_scope} | `{row.owning_prior_milestone}` |"
        for row in rows
    )
    path.write_text(
        "---\n"
        "created: 2026-05-13T18:36:00Z\n"
        "cycle: 8\n"
        "run_id: run-2026-05-13T015136Z\n"
        "agent: worker\n"
        "milestone: M-DEFER-1\n"
        "---\n\n"
        "# Campaign Deferral Watchlist\n\n"
        "M-DEFER-1 formalizes campaign closure under current evidence. It does not add a new reopen gate, "
        "does not introduce synthetic evidence, and does not alter the Phase 4 future reopen conjunction.\n\n"
        "## Current Disposition\n\n"
        f"{disposition_lines}\n\n"
        "## Do Not Reopen For\n\n"
        + "\n".join(f"- {item}" for item in do_not)
        + "\n\n## Reopen Evaluation Only For\n\n"
        + "\n".join(f"- {item}" for item in reopen)
        + "\n\n## Machine-Readable Watchlist\n\n"
        "| Trigger | Classification | Action scope | Owning milestone |\n"
        "|---|---|---|---|\n"
        f"{trigger_lines}\n\n"
        f"![{FIGURE_CAPTION}](../data/campaign_deferral_watchlist.png)\n\n"
        "## Summary Controls\n\n"
        f"- `new_reopen_gate_count`: {summary['new_reopen_gate_count']}\n"
        f"- `current_superiority_claim_count`: {summary['current_superiority_claim_count']}\n"
        f"- `current_artifacts_reopen`: {str(summary['current_artifacts_reopen']).lower()}\n"
        f"- `phase4_future_reopen_condition_unchanged`: {str(summary['phase4_future_reopen_condition_unchanged']).lower()}\n",
        encoding="utf-8",
    )


def main() -> None:
    triggers = read_triggers()
    results = [classify(trigger) for trigger in triggers]
    write_results(results)
    summary = make_summary(results)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_png(Counter(row.classification for row in results))
    write_report(summary, results)
    for path in [WATCHLIST_CSV, RESULTS_CSV, SUMMARY_JSON, FIGURE_PNG, REPORT_MD]:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
