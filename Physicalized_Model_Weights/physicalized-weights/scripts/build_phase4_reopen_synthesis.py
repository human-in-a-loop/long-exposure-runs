# created: 2026-05-13T16:40:00Z
# cycle: 6
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PHASE4-SYNTH-1

"""Build the Phase 4 reopen lifecycle synthesis refresh.

This is a consolidation layer over already validated summaries. It does not
define a new reopen gate; it makes the full post-Phase-3 lifecycle and
uncertainty rule canonical in the final campaign record.
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

CLAIM_MATRIX_CSV = DATA / "phase4_reopen_claim_matrix.csv"
MANIFEST_CSV = DATA / "phase4_reopen_manifest.csv"
SUMMARY_JSON = DATA / "phase4_reopen_summary.json"
FLOW_PNG = DATA / "phase4_reopen_lifecycle_flow.png"
REPORT_MD = DOCS / "phase4_reopen_lifecycle_synthesis.md"
FINAL_SYNTHESIS_MD = DOCS / "final_synthesis.md"
REPRO_MD = DOCS / "reproducibility.md"
TEST_PATH = ROOT / "physicalized-weights" / "tests" / "test_phase4_reopen_synthesis.py"

FUTURE_REOPEN_CONDITION = (
    "valid_package && hash_match && schema_compatible && known_threshold_scenario && "
    "valid_trace && admissible_ingestion_path && measured_terms && "
    "production_or_shadow_or_canary_source && provenance_attestation && "
    "privacy_attestation && nonzero_request_volume && nonzero_accepted_fast_path_volume && "
    "measured_best_programmable_baseline && threshold_crossed && UCB_alpha(H - B) < 0 && "
    "lifecycle_terminal_state=actual_reopen_candidate"
)

PHASE4_COMMANDS = [
    "python3 physicalized-weights/scripts/evidence_acquisition_readiness.py",
    "python3 physicalized-weights/scripts/evidence_pack_template_dryrun.py",
    "python3 physicalized-weights/scripts/evidence_pack_intake_rehearsal.py",
    "python3 physicalized-weights/scripts/reopen_uncertainty_protocol.py",
    "python3 physicalized-weights/scripts/evidence_package_lifecycle.py",
    "python3 physicalized-weights/scripts/build_phase4_reopen_synthesis.py",
]

PHASE4_TEST_COMMANDS = [
    "python3 physicalized-weights/tests/test_evidence_acquisition_readiness.py",
    "python3 physicalized-weights/tests/test_evidence_pack_template_dryrun.py",
    "python3 physicalized-weights/tests/test_evidence_pack_intake_rehearsal.py",
    "python3 physicalized-weights/tests/test_reopen_uncertainty_protocol.py",
    "python3 physicalized-weights/tests/test_evidence_package_lifecycle.py",
    "python3 physicalized-weights/tests/test_phase4_reopen_synthesis.py",
]

REQUIRED_INPUTS = {
    "M-SYNTH-2": [
        DATA / "phase2_synthesis_summary.json",
        DATA / "phase2_claim_matrix.csv",
        DOCS / "phase2_synthesis_downgrade.md",
    ],
    "M-PHASE3-SYNTH-1": [
        DATA / "phase3_reopen_summary.json",
        DATA / "phase3_reopen_claim_matrix.csv",
        DOCS / "phase3_reopen_pathway_summary.md",
    ],
    "M-SWBASE-2": [
        DATA / "stronger_baseline_summary.json",
    ],
    "M-ARCH-1": [
        DOCS / "hybrid_safety_filter_architecture.md",
    ],
    "M-PROTO-1": [
        DATA / "prototype_verification_closure.json",
    ],
    "M-MEASURE-1": [
        DOCS / "production_measurement_requirements.md",
        DATA / "local_overhead_summary.json",
    ],
    "M-ACQUIRE-1": [
        DATA / "evidence_acquisition_readiness_summary.json",
        DATA / "evidence_acquisition_readiness_results.csv",
        DOCS / "evidence_acquisition_readiness.md",
    ],
    "M-DRYRUN-1": [
        DATA / "evidence_pack_dryrun_summary.json",
        DATA / "evidence_pack_dryrun_results.csv",
        DOCS / "operator_evidence_pack_template.md",
    ],
    "M-INTAKE-1": [
        DATA / "evidence_pack_intake_rehearsal_summary.json",
        DATA / "evidence_pack_intake_rehearsal_results.csv",
        DOCS / "evidence_pack_intake_rehearsal.md",
    ],
    "M-EVIDENCEPACK-1": [
        DATA / "evidence_pack_replay_summary.json",
        DATA / "evidence_pack_replay_results.csv",
        DOCS / "evidence_pack_replay_harness.md",
    ],
    "M-UNCERTAINTY-1": [
        DATA / "reopen_uncertainty_summary.json",
        DATA / "reopen_uncertainty_results.csv",
        DOCS / "measured_reopen_uncertainty_protocol.md",
    ],
    "M-LIFECYCLE-1": [
        DATA / "evidence_package_lifecycle_summary.json",
        DATA / "evidence_package_lifecycle_results.csv",
        DOCS / "evidence_package_lifecycle_state_machine.md",
    ],
}

PHASE4_OUTPUTS = [
    REPORT_MD,
    FINAL_SYNTHESIS_MD,
    REPRO_MD,
    CLAIM_MATRIX_CSV,
    MANIFEST_CSV,
    SUMMARY_JSON,
    FLOW_PNG,
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_inputs() -> None:
    missing = [rel(path) for paths in REQUIRED_INPUTS.values() for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Phase 4 input artifacts: " + ", ".join(missing))


def load_inputs() -> dict[str, Any]:
    require_inputs()
    return {
        "phase2": read_json(DATA / "phase2_synthesis_summary.json"),
        "phase3": read_json(DATA / "phase3_reopen_summary.json"),
        "acquire": read_json(DATA / "evidence_acquisition_readiness_summary.json"),
        "dryrun": read_json(DATA / "evidence_pack_dryrun_summary.json"),
        "intake": read_json(DATA / "evidence_pack_intake_rehearsal_summary.json"),
        "replay": read_json(DATA / "evidence_pack_replay_summary.json"),
        "uncertainty": read_json(DATA / "reopen_uncertainty_summary.json"),
        "lifecycle": read_json(DATA / "evidence_package_lifecycle_summary.json"),
        "lifecycle_rows": read_csv(DATA / "evidence_package_lifecycle_results.csv"),
    }


def actual_reopen_count(inputs: dict[str, Any]) -> int:
    return sum(
        int(inputs[name].get("actual_reopen_candidate_count", 0))
        for name in ["phase3", "acquire", "dryrun", "intake", "replay", "uncertainty", "lifecycle"]
    )


def guard_non_reopen(inputs: dict[str, Any]) -> None:
    count = actual_reopen_count(inputs)
    if count != 0:
        raise RuntimeError(f"Current artifacts report {count} actual reopen candidates")
    if inputs["lifecycle"].get("hypothetical_actual_candidate_control_count") != 1:
        raise RuntimeError("Lifecycle positive-control accounting must be exactly one hypothetical branch")
    for row in inputs["lifecycle_rows"]:
        if row.get("current_artifact") == "True" and row.get("actual_reopen_candidate") == "True":
            raise RuntimeError(f"Current lifecycle row reopens unexpectedly: {row.get('case_id')}")


def claim_rows(inputs: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "claim_id": "phase2_performance_superiority_falsified",
            "claim_class": "falsified",
            "evidence_kind": "modeled_equal_workload_replay",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/data/phase2_synthesis_summary.json; physicalized-weights/data/stronger_baseline_summary.json",
            "conclusion": "Safety/filter performance and economic superiority remains falsified against the stronger programmable accelerator baseline.",
        },
        {
            "claim_id": "hybrid_architecture_still_valid_as_failure_mode_study",
            "claim_class": "preserved_architecture_study",
            "evidence_kind": "architecture_and_prototype",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/docs/hybrid_safety_filter_architecture.md; physicalized-weights/data/prototype_verification_closure.json",
            "conclusion": "The hybrid safety/filter block remains useful as a bounded architecture, failure-mode, and evidence-scaffold study.",
        },
        {
            "claim_id": "production_measurement_required",
            "claim_class": "future_reopen_condition",
            "evidence_kind": "measurement_contract",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/docs/production_measurement_requirements.md; physicalized-weights/data/local_overhead_summary.json",
            "conclusion": "Local proxies decompose overheads, but future reopening requires measured production, shadow, or canary latency, energy, utilization, and baseline terms.",
        },
        {
            "claim_id": "evidence_pack_replay_required",
            "claim_class": "future_reopen_condition",
            "evidence_kind": "manifest_replay_contract",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/data/evidence_pack_replay_summary.json; physicalized-weights/docs/evidence_pack_replay_harness.md",
            "conclusion": "Future traces must pass manifest integrity, schema, source, ingestion, provenance, privacy, and downstream replay gates.",
        },
        {
            "claim_id": "operator_dryrun_is_non_evidence",
            "claim_class": "non_evidence",
            "evidence_kind": "template_dryrun",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/data/evidence_pack_dryrun_summary.json; physicalized-weights/docs/operator_evidence_pack_template.md",
            "conclusion": "Operator templates and dry-run acceptance checks are collection preparation only and cannot reopen the Phase 2 downgrade.",
        },
        {
            "claim_id": "intake_rehearsal_is_non_evidence",
            "claim_class": "non_evidence",
            "evidence_kind": "synthetic_safe_handoff_rehearsal",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/data/evidence_pack_intake_rehearsal_summary.json; physicalized-weights/docs/evidence_pack_intake_rehearsal.md",
            "conclusion": "Intake rehearsal proves handoff mechanics and replay delegation, but rehearsal packages are not current measured evidence.",
        },
        {
            "claim_id": "uncertainty_margin_required",
            "claim_class": "future_reopen_condition",
            "evidence_kind": "uncertainty_protocol",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/data/reopen_uncertainty_summary.json; physicalized-weights/docs/measured_reopen_uncertainty_protocol.md",
            "conclusion": "A point threshold crossing is insufficient; future reopening also requires UCB_alpha(H - B) < 0.",
        },
        {
            "claim_id": "lifecycle_candidate_branch_is_hypothetical_only",
            "claim_class": "positive_control_only",
            "evidence_kind": "lifecycle_state_machine_control",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/data/evidence_package_lifecycle_summary.json; physicalized-weights/docs/evidence_package_lifecycle_state_machine.md",
            "conclusion": "The single candidate branch is a labeled hypothetical positive control and is excluded from current artifact reopen counts.",
        },
        {
            "claim_id": "current_artifacts_do_not_reopen",
            "claim_class": "current_claim_state",
            "evidence_kind": "campaign_synthesis",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/data/phase4_reopen_summary.json; physicalized-weights/data/phase4_reopen_claim_matrix.csv",
            "conclusion": "Current committed artifacts have actual_reopen_candidate_count=0 and current_artifacts_reopen=false.",
        },
        {
            "claim_id": "future_reopen_condition",
            "claim_class": "future_reopen_condition",
            "evidence_kind": "conjunctive_rule",
            "current_measured_evidence": "false",
            "supporting_artifacts": "physicalized-weights/data/phase4_reopen_summary.json; physicalized-weights/docs/phase4_reopen_lifecycle_synthesis.md",
            "conclusion": FUTURE_REOPEN_CONDITION,
        },
    ]


def write_claim_matrix(rows: list[dict[str, str]]) -> None:
    fields = [
        "claim_id",
        "claim_class",
        "evidence_kind",
        "current_measured_evidence",
        "supporting_artifacts",
        "conclusion",
    ]
    with CLAIM_MATRIX_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_png(path: Path) -> None:
    width, height = 980, 430
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                idx = (y * width + x) * 3
                pixels[idx : idx + 3] = bytes(color)

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

    stages = [
        ("Phase 2", (181, 83, 75)),
        ("Measure", (80, 127, 178)),
        ("Trace/Replay", (89, 149, 109)),
        ("Operator Prep", (202, 135, 72)),
        ("Uncertainty", (135, 102, 174)),
        ("Lifecycle", (76, 145, 158)),
        ("Current Reopen", (70, 70, 70)),
    ]
    rect(40, 55, 940, 315, (242, 244, 247))
    points = [(95 + i * 130, 165 + (i % 2) * 42) for i in range(len(stages))]
    for left, right in zip(points, points[1:]):
        line(left[0], left[1], right[0], right[1], (162, 170, 180))
    for idx, (x, y) in enumerate(points):
        color = stages[idx][1]
        rect(x - 45, y - 32, x + 45, y + 32, color)
        rect(x - 35, y - 22, x + 35, y + 22, (255, 255, 255))
        rect(x - 25, y - 12, x + 25, y + 12, color)
    rect(735, 330, 890, 360, (242, 244, 247))
    rect(735, 365, 890, 395, (181, 83, 75))
    rect(895, 365, 925, 395, (255, 255, 255))
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def build_summary(inputs: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    lifecycle = inputs["lifecycle"]
    return {
        "schema_version": 1,
        "milestone_id": "M-PHASE4-SYNTH-1",
        "status": "validated",
        "central_conclusion": (
            "Phase 2 remains downgraded: broad fixed frontier physicalization is rejected, "
            "safety/filter performance superiority remains falsified against stronger programmable baselines, "
            "and the hybrid architecture remains useful only as a failure-mode and evidence-scaffold study."
        ),
        "current_artifacts_reopen": False,
        "actual_reopen_candidate_count": actual_reopen_count(inputs),
        "hypothetical_actual_candidate_control_count": lifecycle.get("hypothetical_actual_candidate_control_count", 0),
        "future_reopen_condition": FUTURE_REOPEN_CONDITION,
        "integrated_milestones": [
            "M-SYNTH-2",
            "M-PHASE3-SYNTH-1",
            "M-ACQUIRE-1",
            "M-DRYRUN-1",
            "M-INTAKE-1",
            "M-EVIDENCEPACK-1",
            "M-UNCERTAINTY-1",
            "M-LIFECYCLE-1",
        ],
        "claim_count": len(rows),
        "phase2_stronger_baseline_winner_counts": inputs["phase2"].get("stronger_baseline_winner_counts", {}),
        "phase3_actual_reopen_candidate_count": inputs["phase3"].get("actual_reopen_candidate_count", 0),
        "readiness_is_evidence": inputs["acquire"].get("readiness_is_evidence", False),
        "dryrun_is_evidence": inputs["dryrun"].get("dryrun_is_evidence", False),
        "intake_actual_reopen_candidate_count": inputs["intake"].get("actual_reopen_candidate_count", 0),
        "uncertainty_rule": inputs["uncertainty"].get("uncertainty_rule", "UCB_alpha(H - B) < 0"),
        "lifecycle_terminal_state_counts": lifecycle.get("terminal_state_counts", {}),
        "lifecycle_states_defined": lifecycle.get("states_defined", []),
        "figure_caption": "Campaign-level evidence flow from Phase 2 downgrade through production measurement, trace/replay gates, operator preparation, uncertainty margins, lifecycle closure, and the still-empty current reopen branch.",
    }


def write_report(summary: dict[str, Any], rows: list[dict[str, str]]) -> None:
    claims = "\n".join(f"- `{row['claim_id']}`: {row['conclusion']}" for row in rows)
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T16:40:00Z
cycle: 6
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PHASE4-SYNTH-1
---

# Phase 4 Reopen Lifecycle Synthesis

Phase 4 refreshes the canonical campaign record after acquisition readiness, operator dry-run, intake rehearsal, uncertainty margins, and lifecycle closure. It does not add a new gate. It consolidates the validated monotone conjunction that a future package must satisfy before it can challenge the Phase 2 downgrade.

Current claim state:

- Broad/full fixed frontier-model physicalization remains rejected.
- Safety/filter performance superiority remains falsified against stronger programmable baselines.
- The hybrid safety/filter architecture remains useful as a failure-mode and evidence-scaffold study.
- Current committed artifacts report `actual_reopen_candidate_count = {summary['actual_reopen_candidate_count']}` and `current_artifacts_reopen = false`.
- The lifecycle positive branch count is `{summary['hypothetical_actual_candidate_control_count']}`, and that branch is a hypothetical control only.

Future reopening requires this full conjunction:

```text
{FUTURE_REOPEN_CONDITION}
```

![Campaign-level evidence flow from Phase 2 downgrade through production measurement, trace/replay gates, operator preparation, uncertainty margins, lifecycle closure, and the still-empty current reopen branch.](../data/phase4_reopen_lifecycle_flow.png)

## Claim Matrix

{claims}

## Lifecycle Link

`M-LIFECYCLE-1` defines the terminal states used here, including `collection_ready_not_evidence`, `dryrun_ready_not_evidence`, `intake_rehearsed_not_evidence`, `replay_valid_nonactual`, `threshold_crossed_nonactual`, `uncertainty_inconclusive`, `statistically_durable_nonactual`, and `actual_reopen_candidate`. The Phase 4 synthesis keeps the hypothetical `actual_reopen_candidate` branch separate from current evidence.

## Replay

Run from `<workspace>`:

```bash
{chr(10).join(PHASE4_COMMANDS)}
```

Then validate:

```bash
{chr(10).join(PHASE4_TEST_COMMANDS)}
file physicalized-weights/data/phase4_reopen_lifecycle_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```
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
    section = f"""Phase 4 folds `M-ACQUIRE-1`, `M-DRYRUN-1`, `M-INTAKE-1`, `M-UNCERTAINTY-1`, and `M-LIFECYCLE-1` into the canonical campaign record. The current claim state is unchanged but now unambiguous: broad/full fixed frontier physicalization remains rejected; safety/filter performance superiority remains falsified against stronger programmable baselines; and the hybrid architecture remains useful as a failure-mode and evidence-scaffold study.

No current artifact is actual measured reopen evidence. The refreshed synthesis reports `actual_reopen_candidate_count = {summary['actual_reopen_candidate_count']}` and `current_artifacts_reopen = false`. The lifecycle branch that reaches `actual_reopen_candidate` is counted separately as `hypothetical_actual_candidate_control_count = {summary['hypothetical_actual_candidate_control_count']}` and is not current measured evidence.

Future reopening requires the full lifecycle and uncertainty-aware conjunction:

```text
{FUTURE_REOPEN_CONDITION}
```

The lifecycle states are defined by `M-LIFECYCLE-1` in `physicalized-weights/docs/evidence_package_lifecycle_state_machine.md`. The generated Phase 4 report is `physicalized-weights/docs/phase4_reopen_lifecycle_synthesis.md`, the claim matrix is `physicalized-weights/data/phase4_reopen_claim_matrix.csv`, the manifest is `physicalized-weights/data/phase4_reopen_manifest.csv`, and the compact summary is `physicalized-weights/data/phase4_reopen_summary.json`."""
    text = FINAL_SYNTHESIS_MD.read_text(encoding="utf-8")
    FINAL_SYNTHESIS_MD.write_text(replace_section(text, "Phase 4 Reopen Lifecycle Synthesis", section), encoding="utf-8")


def update_reproducibility() -> None:
    section = f"""Replay the post-Phase-3 operational layers and final synthesis refresh in dependency order:

```bash
{chr(10).join(PHASE4_COMMANDS)}
```

Expected non-reopen outcomes:

- `physicalized-weights/data/evidence_acquisition_readiness_summary.json` reports readiness is not evidence.
- `physicalized-weights/data/evidence_pack_dryrun_summary.json` reports dry-run artifacts are not evidence.
- `physicalized-weights/data/evidence_pack_intake_rehearsal_summary.json` reports `actual_reopen_candidate_count: 0`.
- `physicalized-weights/data/reopen_uncertainty_summary.json` requires `UCB_alpha(H - B) < 0`.
- `physicalized-weights/data/evidence_package_lifecycle_summary.json` reports `actual_reopen_candidate_count: 0` and `hypothetical_actual_candidate_control_count: 1`.
- `physicalized-weights/data/phase4_reopen_summary.json` reports `current_artifacts_reopen: false`.

Validation:

```bash
{chr(10).join(PHASE4_TEST_COMMANDS)}
file physicalized-weights/data/phase4_reopen_lifecycle_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```"""
    text = REPRO_MD.read_text(encoding="utf-8")
    REPRO_MD.write_text(replace_section(text, "Phase 4 Reopen Lifecycle Replay", section), encoding="utf-8")


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
    for path in [Path(__file__).resolve(), TEST_PATH] + PHASE4_OUTPUTS:
        if path == MANIFEST_CSV:
            digest = "self_referential_manifest"
        else:
            digest = sha256(path) if path.exists() else ""
        rows.append(
            {
                "milestone_id": "M-PHASE4-SYNTH-1",
                "artifact_path": rel(path),
                "artifact_sha256": digest,
                "artifact_role": "implementation" if path in {Path(__file__).resolve(), TEST_PATH} else "output",
                "replay_command": "python3 physicalized-weights/scripts/build_phase4_reopen_synthesis.py",
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
    guard_non_reopen(inputs)
    rows = claim_rows(inputs)
    write_claim_matrix(rows)
    write_png(FLOW_PNG)
    summary = build_summary(inputs, rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary, rows)
    update_final_synthesis(summary)
    update_reproducibility()
    write_manifest()
    print(f"wrote {CLAIM_MATRIX_CSV}")
    print(f"wrote {MANIFEST_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {FLOW_PNG}")
    print(f"wrote {REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
