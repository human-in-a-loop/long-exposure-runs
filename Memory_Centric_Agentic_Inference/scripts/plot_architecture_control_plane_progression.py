# created: 2026-05-12T13:37:27Z
# cycle: 42
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ARCHPKG-1

from __future__ import annotations

import csv
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_IN = DATA / "architecture_control_plane_progression.csv"
PNG_OUT = DATA / "architecture_control_plane_progression.png"


def read_rows() -> list[dict[str, str]]:
    with CSV_IN.open(newline="") as f:
        return list(csv.DictReader(f))


def short_label(stage_id: str) -> str:
    labels = {
        "taxonomy": "Taxonomy",
        "trace_schema": "Trace\nschema",
        "abi_schema": "ABI\nschema",
        "abi_validation": "ABI\nvalidation",
        "runtime_prototype_compatibility": "Runtime\ncompat",
        "constrained_planner_compatibility": "Planner\ncompat",
        "abi_integration_replay": "Action\ngating",
        "final_architecture_package": "Final\npackage",
        "production_evidence_gatechain": "Production\ngatechain",
    }
    return labels.get(stage_id, stage_id)


def evidence_label(value: str) -> str:
    labels = {
        "validated_artifact": "validated",
        "synthetic_trace_contract": "synthetic trace",
        "synthetic_contract": "synthetic contract",
        "synthetic_integration_replay": "integration replay",
        "derived_synthesis": "derived synthesis",
        "future_production_target_prerequisite": "future production gate",
    }
    return labels.get(value, value.replace("_", " "))


def main() -> None:
    rows = read_rows()
    fig, ax = plt.subplots(figsize=(14.5, 6.2))
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.set_ylim(-1.25, 1.65)
    ax.axis("off")

    for idx, row in enumerate(rows):
        is_gate = row["stage_id"] == "production_evidence_gatechain"
        color = "#E45756" if is_gate else "#4C78A8"
        face = "#FDEDEC" if is_gate else "#EAF2F8"
        ax.text(
            idx,
            0.45,
            short_label(row["stage_id"]),
            ha="center",
            va="center",
            fontsize=10,
            bbox={"boxstyle": "round,pad=0.35", "fc": face, "ec": color, "lw": 1.6},
        )
        ax.text(
            idx,
            -0.2,
            "\n".join(textwrap.wrap(evidence_label(row["evidence_label"]), width=16)),
            ha="center",
            va="center",
            fontsize=8,
            color="#333333",
        )
        if idx < len(rows) - 1:
            ax.add_patch(FancyArrowPatch((idx + 0.35, 0.45), (idx + 0.65, 0.45), arrowstyle="->", mutation_scale=12, color="#555555", lw=1.2))

    gate_idx = next(i for i, row in enumerate(rows) if row["stage_id"] == "production_evidence_gatechain")
    ax.plot([gate_idx - 0.45, gate_idx + 0.45], [1.0, 1.0], color="#E45756", lw=3)
    ax.text(
        gate_idx,
        1.22,
        "blocked until trusted production-target evidence passes all gates",
        ha="center",
        va="center",
        fontsize=9,
        color="#9D2B2B",
    )
    ax.text(
        3.5,
        1.22,
        "contract validation -> runtime/planner compatibility -> fail-closed action gating",
        ha="center",
        va="center",
        fontsize=10,
        color="#1F4E79",
    )
    ax.text(
        4.0,
        -0.85,
        "Production credit remains false across all stages; the final gate is a future prerequisite, not evidence from this run.",
        ha="center",
        va="center",
        fontsize=9,
        color="#333333",
    )
    ax.set_title(
        "Control-plane progression from memory-object contract validation to runtime/planner action gating",
        fontsize=13,
        pad=16,
    )
    plt.tight_layout()
    plt.savefig(PNG_OUT, dpi=170)
    plt.close()
    print(PNG_OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
