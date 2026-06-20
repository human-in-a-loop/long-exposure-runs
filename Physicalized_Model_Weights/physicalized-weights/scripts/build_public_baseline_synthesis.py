# created: 2026-05-13T22:36:00Z
# cycle: 15
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PUBLICBASE-SYNTH-1

"""Integrate validated public programmable-baseline refresh into synthesis.

This is a bounded synthesis update over M-PUBLICBASE-1 and M-PUBLICBASE-2. It
does not fetch new benchmark data, rebuild the calibrated model, or change the
Phase 4 measured-evidence reopen condition.
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

RECENCY_SUMMARY = DATA / "public_baseline_recency_summary.json"
PRIOR_SUMMARY = DATA / "public_baseline_prior_refresh_summary.json"
SOURCE_TABLE = DATA / "public_baseline_sources.csv"
CAMPAIGN_MAPPING = DATA / "public_baseline_campaign_mapping.csv"
PRIOR_REFRESH = DATA / "public_baseline_prior_refresh.csv"
FINAL_SYNTHESIS = DOCS / "final_synthesis.md"
REPRODUCIBILITY = DOCS / "reproducibility.md"

REPORT_MD = DOCS / "public_baseline_refresh_synthesis.md"
CLAIM_MATRIX = DATA / "public_baseline_synthesis_claim_matrix.csv"
MANIFEST_CSV = DATA / "public_baseline_synthesis_manifest.csv"
SUMMARY_JSON = DATA / "public_baseline_synthesis_summary.json"
FLOW_PNG = DATA / "public_baseline_synthesis_flow.png"

PHASE4_REOPEN_CONDITION = (
    "valid_package && hash_match && schema_compatible && known_threshold_scenario && "
    "valid_trace && admissible_ingestion_path && measured_terms && "
    "production_or_shadow_or_canary_source && provenance_attestation && "
    "privacy_attestation && nonzero_request_volume && nonzero_accepted_fast_path_volume && "
    "measured_best_programmable_baseline && threshold_crossed && UCB_alpha(H - B) < 0 && "
    "lifecycle_terminal_state=actual_reopen_candidate"
)

COMMANDS = [
    "python3 physicalized-weights/scripts/public_baseline_recency_probe.py",
    "python3 physicalized-weights/scripts/public_baseline_prior_refresh.py",
    "python3 physicalized-weights/scripts/build_public_baseline_synthesis.py",
]

TEST_COMMANDS = [
    "python3 physicalized-weights/tests/test_public_baseline_recency_probe.py",
    "python3 physicalized-weights/tests/test_public_baseline_prior_refresh.py",
    "python3 physicalized-weights/tests/test_public_baseline_synthesis.py",
]

CLAIM_FIELDS = [
    "claim_id",
    "disposition",
    "evidence_level",
    "supporting_artifacts",
    "affected_campaign_claim",
    "notes",
]

MANIFEST_FIELDS = ["artifact_path", "artifact_class", "owning_milestone", "derivation"]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def replace_section(text: str, heading: str, section: str) -> str:
    marker = f"\n## {heading}\n"
    if marker not in text:
        return text.rstrip() + "\n\n" + f"## {heading}\n\n{section.strip()}\n"
    start = text.index(marker) + 1
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[:start] + f"## {heading}\n\n{section.strip()}\n"
    return text[:start] + f"## {heading}\n\n{section.strip()}\n" + text[next_start:]


def claim_rows(recency: dict[str, Any], prior: dict[str, Any]) -> list[dict[str, str]]:
    support_base = "physicalized-weights/data/public_baseline_recency_summary.json; physicalized-weights/data/public_baseline_prior_refresh_summary.json"
    return [
        {
            "claim_id": "public_mlperf_recency",
            "disposition": "supported",
            "evidence_level": "primary_public_benchmark_recency",
            "supporting_artifacts": "physicalized-weights/data/public_baseline_recency_summary.json; physicalized-weights/data/public_baseline_sources.csv",
            "affected_campaign_claim": "programmable baseline assumptions are current enough to screen for drift",
            "notes": f"{recency['latest_mlperf_inference_release']} is newer and material enough to record after closure.",
        },
        {
            "claim_id": "programmable_null_strength",
            "disposition": "strengthened_or_preserved",
            "evidence_level": "primary_public_benchmark_prior",
            "supporting_artifacts": "physicalized-weights/data/public_baseline_prior_refresh_summary.json; physicalized-weights/data/public_baseline_prior_refresh.csv",
            "affected_campaign_claim": "strong programmable baseline null",
            "notes": f"Primary MLCommons rows produce {prior['throughput_prior_rows']} throughput-prior rows and effect {prior['programmable_null_effect']}.",
        },
        {
            "claim_id": "direct_energy_calibration_from_public_mlperf",
            "disposition": "unsupported",
            "evidence_level": "blocked_direct_energy_calibration",
            "supporting_artifacts": "physicalized-weights/data/public_baseline_prior_refresh_summary.json; physicalized-weights/data/public_baseline_campaign_mapping.csv",
            "affected_campaign_claim": "energy-per-request calibration",
            "notes": f"Direct energy calibration rows are {prior['direct_energy_calibration_rows']}; no energy value is inferred from throughput-only rows.",
        },
        {
            "claim_id": "safety_filter_workload_comparability",
            "disposition": "unsupported",
            "evidence_level": "non_comparable_public_workload",
            "supporting_artifacts": "physicalized-weights/data/public_baseline_campaign_mapping.csv",
            "affected_campaign_claim": "identical safety-filter workload accounting",
            "notes": f"Direct safety-filter workload rows are {prior['safety_filter_direct_workload_rows']}; public benchmark rows do not measure the campaign workload.",
        },
        {
            "claim_id": "phase2_downgrade_after_public_refresh",
            "disposition": "preserved",
            "evidence_level": "conservative_synthesis",
            "supporting_artifacts": support_base + "; physicalized-weights/data/phase2_synthesis_summary.json",
            "affected_campaign_claim": "Phase 2 stronger-baseline downgrade",
            "notes": "Public throughput-prior evidence affects B, not measured hybrid total H; the downgrade is preserved.",
        },
        {
            "claim_id": "physicalized_reopen_from_public_benchmark",
            "disposition": "falsified_public_benchmark_only",
            "evidence_level": "non_reopen_public_benchmark_context",
            "supporting_artifacts": support_base + "; physicalized-weights/data/phase4_reopen_summary.json",
            "affected_campaign_claim": "current physicalized performance/economic superiority",
            "notes": "Public benchmark-only evidence is not production, shadow, or canary measured hybrid evidence and cannot reopen the claim.",
        },
        {
            "claim_id": "future_model_refresh_scope",
            "disposition": "bounded_future_work",
            "evidence_level": "scope_boundary",
            "supporting_artifacts": "physicalized-weights/docs/public_baseline_prior_refresh.md; physicalized-weights/docs/public_baseline_refresh_synthesis.md",
            "affected_campaign_claim": "future programmable-baseline model refresh",
            "notes": "A full model refresh is separate work; physicalized reopen still requires the unchanged Phase 4 condition.",
        },
    ]


def build_summary(recency: dict[str, Any], prior: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "milestone_id": "M-PUBLICBASE-SYNTH-1",
        "status": "validated",
        "public_baseline_refresh_integrated": True,
        "latest_mlperf_inference_release": recency["latest_mlperf_inference_release"],
        "latest_mlperf_inference_publication_date": recency["latest_mlperf_inference_publication_date"],
        "primary_mlcommons_rows_ingested": prior["primary_mlcommons_rows_ingested"],
        "raw_primary_rows_available": prior["raw_primary_rows_available"],
        "direct_energy_calibration_rows": prior["direct_energy_calibration_rows"],
        "safety_filter_direct_workload_rows": prior["safety_filter_direct_workload_rows"],
        "throughput_prior_rows": prior["throughput_prior_rows"],
        "programmable_null_effect": prior["programmable_null_effect"],
        "phase2_downgrade_preserved": True,
        "public_sources_reopen_physicalized_claim": False,
        "phase4_reopen_condition_unchanged": True,
        "current_superiority_claim_count": 0,
        "actual_reopen_candidate_count": 0,
        "new_reopen_gate_count": 0,
        "current_artifacts_reopen": False,
        "claim_count": len(rows),
        "integrated_milestones": ["M-PUBLICBASE-1", "M-PUBLICBASE-2", "M-CLOSURE-1"],
        "future_reopen_condition": PHASE4_REOPEN_CONDITION,
        "figure_caption": "public programmable-baseline refresh flow from official MLPerf recency through conservative prior mapping to strengthened programmable null and unchanged hybrid reopen boundary.",
    }


def write_png(path: Path) -> None:
    width, height = 980, 420
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                idx = (y * width + x) * 3
                pixels[idx: idx + 3] = bytes(color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                idx = (y0 * width + x0) * 3
                pixels[idx: idx + 3] = bytes(color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    colors = [(62, 112, 165), (68, 142, 104), (193, 128, 60), (126, 95, 165), (72, 72, 72)]
    points = [(120, 190), (300, 120), (490, 190), (670, 120), (850, 190)]
    rect(45, 50, 935, 310, (242, 245, 248))
    for a, b in zip(points, points[1:]):
        line(a[0], a[1], b[0], b[1], (150, 160, 170))
        line(a[0], a[1] + 1, b[0], b[1] + 1, (150, 160, 170))
    for idx, (x, y) in enumerate(points):
        rect(x - 58, y - 38, x + 58, y + 38, colors[idx])
        rect(x - 42, y - 22, x + 42, y + 22, (255, 255, 255))
        rect(x - 26, y - 10, x + 26, y + 10, colors[idx])
    rect(675, 335, 875, 360, (68, 142, 104))
    rect(675, 370, 875, 395, (72, 72, 72))
    raw = b"".join(b"\x00" + pixels[y * width * 3: (y + 1) * width * 3] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def write_report(summary: dict[str, Any], rows: list[dict[str, str]]) -> None:
    claims = "\n".join(
        f"- `{row['claim_id']}`: {row['disposition']} ({row['evidence_level']}). {row['notes']}"
        for row in rows
    )
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T22:36:00Z
cycle: 15
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PUBLICBASE-SYNTH-1
---

# Public Baseline Refresh Synthesis

This addendum exists after closure because `M-PUBLICBASE-1` found a materially changed public programmable-baseline condition and `M-PUBLICBASE-2` converted that condition into a conservative campaign mapping. It updates the reader-facing record without changing the measured hybrid reopen requirements.

`M-PUBLICBASE-1` found that the latest official MLPerf Inference release recorded here is `{summary['latest_mlperf_inference_release']}` from `{summary['latest_mlperf_inference_publication_date']}`, and that the public update is material enough to record as programmable-baseline drift. `M-PUBLICBASE-2` ingested `{summary['primary_mlcommons_rows_ingested']}` primary MLCommons rows from `{summary['raw_primary_rows_available']}` available rows, producing throughput-prior evidence only: direct energy calibration rows are `{summary['direct_energy_calibration_rows']}` and direct safety-filter workload rows are `{summary['safety_filter_direct_workload_rows']}`.

Claim impact:

{claims}

The synthesis result is conservative: the programmable null is `{summary['programmable_null_effect']}`, the Phase 2 downgrade is preserved, and no public benchmark source reopens physicalized superiority. Public programmable benchmark progress can strengthen `B`, but it does not supply measured hybrid `H`.

Future work boundary:

- A full model refresh is separate work and should map primary public data into explicit model terms before changing calibrated assumptions.
- Physicalized claim reopening remains possible only through lifecycle-valid measured hybrid evidence satisfying the unchanged Phase 4 condition.

```text
{PHASE4_REOPEN_CONDITION}
```

![public programmable-baseline refresh flow from official MLPerf recency through conservative prior mapping to strengthened programmable null and unchanged hybrid reopen boundary.](../data/public_baseline_synthesis_flow.png)
""",
        encoding="utf-8",
    )


def update_final_synthesis(summary: dict[str, Any]) -> None:
    section = f"""This post-closure addendum integrates `M-PUBLICBASE-1` and `M-PUBLICBASE-2` into the canonical campaign record. It exists because official public programmable-baseline evidence moved after closure: `{summary['latest_mlperf_inference_release']}` was recorded as the latest MLPerf Inference release, and primary MLCommons v6.0 rows were mapped into campaign terms.

The public-baseline refresh affects the programmable baseline term `B`, not measured hybrid evidence `H`. `M-PUBLICBASE-2` ingested `{summary['primary_mlcommons_rows_ingested']}` primary MLCommons rows from `{summary['raw_primary_rows_available']}` available rows and found `{summary['throughput_prior_rows']}` throughput-prior rows, `{summary['direct_energy_calibration_rows']}` direct energy-calibration rows, and `{summary['safety_filter_direct_workload_rows']}` direct safety-filter workload rows. The result is `programmable_null_effect = {summary['programmable_null_effect']}`.

The Phase 2 downgrade is preserved, no public benchmark source reopens physicalized superiority, and endpoint counters remain `current_superiority_claim_count = 0`, `actual_reopen_candidate_count = 0`, `new_reopen_gate_count = 0`, and `current_artifacts_reopen = false`. The Phase 4 reopen condition remains unchanged; public benchmark-only evidence is not production, shadow, or canary measured hybrid evidence.

The generated addendum is `physicalized-weights/docs/public_baseline_refresh_synthesis.md`; the claim matrix is `physicalized-weights/data/public_baseline_synthesis_claim_matrix.csv`; the manifest is `physicalized-weights/data/public_baseline_synthesis_manifest.csv`; and the compact summary is `physicalized-weights/data/public_baseline_synthesis_summary.json`."""
    FINAL_SYNTHESIS.write_text(
        replace_section(FINAL_SYNTHESIS.read_text(encoding="utf-8"), "Post-Closure Public Baseline Refresh", section),
        encoding="utf-8",
    )


def update_reproducibility() -> None:
    section = f"""Replay the public programmable-baseline recency probe, conservative prior refresh, and synthesis addendum:

```bash
{chr(10).join(COMMANDS)}
```

Expected outcomes:

- `physicalized-weights/data/public_baseline_recency_summary.json` records MLPerf Inference v6.0 as the latest public MLPerf Inference release observed by this campaign.
- `physicalized-weights/data/public_baseline_prior_refresh_summary.json` records 12 primary MLCommons rows ingested from 520 available rows, zero direct energy calibration rows, zero direct safety-filter workload rows, and `programmable_null_effect: strengthened_or_preserved`.
- `physicalized-weights/data/public_baseline_synthesis_summary.json` records `phase2_downgrade_preserved: true`, `phase4_reopen_condition_unchanged: true`, and endpoint counters at zero or false.

Validation:

```bash
{chr(10).join(TEST_COMMANDS)}
file physicalized-weights/data/public_baseline_synthesis_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```"""
    REPRODUCIBILITY.write_text(
        replace_section(REPRODUCIBILITY.read_text(encoding="utf-8"), "Public Baseline Refresh Replay", section),
        encoding="utf-8",
    )


def manifest_rows() -> list[dict[str, str]]:
    rows = [
        (RECENCY_SUMMARY, "source_summary", "M-PUBLICBASE-1", "source-derived"),
        (SOURCE_TABLE, "source_table", "M-PUBLICBASE-1", "source-derived"),
        (PRIOR_SUMMARY, "source_summary", "M-PUBLICBASE-2", "source-derived"),
        (CAMPAIGN_MAPPING, "mapping_table", "M-PUBLICBASE-2", "generated"),
        (PRIOR_REFRESH, "prior_refresh_table", "M-PUBLICBASE-2", "generated"),
        (REPORT_MD, "synthesis_report", "M-PUBLICBASE-SYNTH-1", "generated"),
        (CLAIM_MATRIX, "claim_matrix", "M-PUBLICBASE-SYNTH-1", "generated"),
        (SUMMARY_JSON, "summary_json", "M-PUBLICBASE-SYNTH-1", "generated"),
        (FLOW_PNG, "figure", "M-PUBLICBASE-SYNTH-1", "generated"),
        (FINAL_SYNTHESIS, "canonical_synthesis", "M-PUBLICBASE-SYNTH-1", "generated_update"),
        (REPRODUCIBILITY, "reproduction_record", "M-PUBLICBASE-SYNTH-1", "generated_update"),
    ]
    return [
        {
            "artifact_path": rel(path),
            "artifact_class": klass,
            "owning_milestone": milestone,
            "derivation": derivation,
        }
        for path, klass, milestone, derivation in rows
    ]


def guard_inputs(recency: dict[str, Any], prior: dict[str, Any]) -> None:
    if recency.get("public_sources_reopen_physicalized_claim") is not False:
        raise RuntimeError("M-PUBLICBASE-1 unexpectedly reopens the physicalized claim")
    if prior.get("direct_energy_calibration_rows") != 0:
        raise RuntimeError("This synthesis expects zero direct energy calibration rows")
    if prior.get("safety_filter_direct_workload_rows") != 0:
        raise RuntimeError("This synthesis expects zero direct safety-filter workload rows")
    if prior.get("phase2_downgrade_preserved") is not True:
        raise RuntimeError("M-PUBLICBASE-2 must preserve the Phase 2 downgrade")


def main() -> dict[str, Any]:
    for path in [RECENCY_SUMMARY, PRIOR_SUMMARY, SOURCE_TABLE, CAMPAIGN_MAPPING, PRIOR_REFRESH, FINAL_SYNTHESIS, REPRODUCIBILITY]:
        if not path.exists():
            raise FileNotFoundError(rel(path))

    recency = read_json(RECENCY_SUMMARY)
    prior = read_json(PRIOR_SUMMARY)
    guard_inputs(recency, prior)
    rows = claim_rows(recency, prior)
    summary = build_summary(recency, prior, rows)

    write_csv(CLAIM_MATRIX, rows, CLAIM_FIELDS)
    write_png(FLOW_PNG)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary, rows)
    update_final_synthesis(summary)
    update_reproducibility()
    write_csv(MANIFEST_CSV, manifest_rows(), MANIFEST_FIELDS)

    summary["generated_manifest_sha256"] = sha256(MANIFEST_CSV)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    main()
