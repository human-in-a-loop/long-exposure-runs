#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:00:00Z
# cycle: 29
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Apply the frozen 3-verdict adjudication rubric for the cycle-28
M3_WEAK verdict on hash-space geometry.

Rubric (LOCKED in
docs/collision_model_hash_space_geometry_adjudication_rubric.md
BEFORE this script's first run):

  M3_STANDS
      At least one (rule_type x batch) cell with p-value surviving
      Benjamini-Hochberg at q<0.05 across m=35 cells AND drop-batch_v2
      sensitivity (retained BH survivors >= 1) AND leave-one-cell-out
      (no single cell whose removal drops BH survivors to 0).

  M3_COLLAPSES_TO_REFUTES
      Zero cells survive BH q<0.05 across m=35.

  MIXED
      Exactly one BH survivor whose absence under drop_batch_v2 removes
      it, OR leave-one-cell-out shows total dependence on a single legacy
      content cluster.

Emits data/collision_model/hash_geometry_adjudication_verdict.json.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"hash_geometry_adjudication_verdict requires /usr/bin/python3, got {sys.executable}"
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "collision_model"
DOCS = ROOT / "docs"

MTC_PATH = OUT_DIR / "multiple_testing_correction.json"
DROP_PATH = OUT_DIR / "drop_batch_v2_sensitivity.json"
LOCO_PATH = OUT_DIR / "leave_one_cell_out.json"
RUBRIC_PATH = DOCS / "collision_model_hash_space_geometry_adjudication_rubric.md"

FROZEN_VERDICTS = ("M3_STANDS", "M3_COLLAPSES_TO_REFUTES", "MIXED")


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(mtc: dict, drop: dict, loco: dict) -> tuple[str, str]:
    bh_survivors_full = mtc["counts"]["bh_survivors"]
    bh_survivors_retained = drop["counts"]["bh_survivors_retained"]
    single_cell = bool(loco["single_cell_carries_signal"])

    if bh_survivors_full == 0:
        return (
            "M3_COLLAPSES_TO_REFUTES",
            "Zero cells survive Benjamini-Hochberg at q=0.05 on the full m=35 "
            "p-vector. Cycle-28's raw p=0.0487 was a multiple-testing artifact.",
        )

    if bh_survivors_full == 1:
        # Determine if the surviving cell IS the batch_v2 x harmonic cell.
        surv = mtc.get("survivors_bh", [])
        if surv and surv[0]["batch"] == "batch_v2":
            if bh_survivors_retained == 0:
                return (
                    "MIXED",
                    "Exactly one BH survivor, and drop-batch_v2 removes it "
                    "entirely (retained survivors = 0). The signal depends "
                    "on the batch_v2 legacy content cluster.",
                )
        if bh_survivors_retained >= 1 and not single_cell:
            return (
                "M3_STANDS",
                "At least one BH survivor, drop-batch_v2 leaves >=1 survivor, "
                "and no single-cell dependence under leave-one-cell-out.",
            )
        return (
            "MIXED",
            f"Exactly one BH survivor with dependency signal "
            f"(retained_survivors={bh_survivors_retained}, "
            f"single_cell_dependent={single_cell}).",
        )

    # bh_survivors_full >= 2
    if bh_survivors_retained >= 1 and not single_cell:
        return (
            "M3_STANDS",
            f"{bh_survivors_full} BH survivors on the full vector; "
            f"{bh_survivors_retained} survive under drop-batch_v2; "
            f"no single-cell dependence.",
        )
    return (
        "MIXED",
        f"{bh_survivors_full} BH survivors but survivors_retained="
        f"{bh_survivors_retained} or single_cell_dependent={single_cell}.",
    )


def main(argv: list[str]) -> int:
    mtc = json.loads(MTC_PATH.read_text())
    drop = json.loads(DROP_PATH.read_text())
    loco = json.loads(LOCO_PATH.read_text())

    verdict, reason = classify(mtc, drop, loco)
    assert verdict in FROZEN_VERDICTS, f"verdict {verdict!r} not in frozen set"

    rubric_sha = _sha256(RUBRIC_PATH)

    out = {
        "verdict": verdict,
        "verdict_reason": reason,
        "rubric_hash": rubric_sha,
        "rubric_path": str(RUBRIC_PATH.relative_to(ROOT)),
        "frozen_verdict_labels": list(FROZEN_VERDICTS),
        "bh_survivors": mtc.get("survivors_bh", []),
        "bonferroni_survivors": mtc.get("survivors_bonferroni", []),
        "sidak_survivors": mtc.get("survivors_sidak", []),
        "drop_v2_survivors": drop.get("survivors_bh_retained", []),
        "loco_contribution": {
            "single_cell_carries_signal": loco["single_cell_carries_signal"],
            "baseline_bh_survivors": loco["baseline_bh_survivors"],
            "changers_under_loco": loco["changers_under_loco"],
        },
        "counts": {
            "bh_full": mtc["counts"]["bh_survivors"],
            "bh_drop_v2": drop["counts"]["bh_survivors_retained"],
        },
        "r2_m3_mean_full": drop.get("r2_m3_mean_full"),
        "r2_m3_mean_drop_v2": drop.get("r2_m3_mean_retained"),
        "alpha_pinned": 0.7469387071101908,
        "inputs": {
            "multiple_testing_correction": str(MTC_PATH.relative_to(ROOT)),
            "drop_batch_v2_sensitivity": str(DROP_PATH.relative_to(ROOT)),
            "leave_one_cell_out": str(LOCO_PATH.relative_to(ROOT)),
        },
        "generator": "scripts/analysis/hash_geometry_adjudication_verdict.py",
        "run_stamp": "2026-08-29T00:00:00Z",
    }
    p = OUT_DIR / "hash_geometry_adjudication_verdict.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"[hash_geometry_adjudication_verdict] wrote {p}")
    print(f"[hash_geometry_adjudication_verdict] verdict = {verdict}")
    print(f"[hash_geometry_adjudication_verdict] rubric_hash = {rubric_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
