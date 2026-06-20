# created: 2026-05-13T03:24:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PROTO-1
"""Evaluate the combinational HDL core with Yosys eval.

This substitutes for a compiled Verilator simulation in the current container,
where Verilator is installed but make/C++ compiler tooling is absent.
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HDL = ROOT / "physicalized-weights" / "hdl" / "safety_filter_core.sv"
OUT = ROOT / "physicalized-weights" / "data" / "hdl_sim_results.csv"

CASES = [
    ("all_zero_bias_allow", [0, 0, 0, 0, 0, 0, 0, 0], -10, 0, 74),
    ("nominal_block_high_margin", [8, -4, 5, 6, -3, 2, 4, -1], 261, 1, 197),
    ("nominal_allow_high_margin", [-4, 6, -3, 0, 8, -2, -5, 3], -250, 0, 314),
    ("max_signed_features", [127, 127, 127, 127, 127, 127, 127, 127], 1895, 1, 1831),
    ("min_signed_features", [-128, -128, -128, -128, -128, -128, -128, -128], -1930, 0, 1994),
    ("threshold_equal", [6, 0, 1, 0, 0, 0, 0, 1], 64, 1, 0),
    ("near_threshold_allow", [6, 0, 0, 0, 0, 1, 0, 1], 63, 0, 1),
    ("near_threshold_block", [6, 0, 0, 0, 0, 0, 1, 1], 65, 1, 1),
]


def parse_bits(text: str, signal: str, signed: bool = False) -> int:
    pattern = re.compile(rf"Eval result: \\\\?{signal} = (\d+)'([01x]+)")
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"missing {signal} in yosys output")
    width = int(match.group(1))
    bits = match.group(2)
    if "x" in bits:
        raise RuntimeError(f"{signal} evaluated to unknown bits: {bits}")
    value = int(bits, 2)
    if signed and bits[0] == "1":
        value -= 1 << width
    return value


def yosys_eval(features: list[int]) -> tuple[int, int, int, int]:
    sets = " ".join(f"-set feature{i} {value}" for i, value in enumerate(features))
    command = (
        f"read_verilog -sv {HDL}; "
        "prep -top safety_filter_core; "
        f"eval {sets} -show score -show decision_block -show margin -show confidence"
    )
    completed = subprocess.run(
        ["yosys", "-p", command],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = completed.stdout
    return (
        parse_bits(output, "score", signed=True),
        parse_bits(output, "decision_block"),
        parse_bits(output, "margin"),
        parse_bits(output, "confidence"),
    )


def main() -> None:
    rows = []
    all_match = True
    for case_id, features, expected_score, expected_decision, expected_margin in CASES:
        score, decision, margin, confidence = yosys_eval(features)
        match = (
            score == expected_score
            and decision == expected_decision
            and margin == expected_margin
            and confidence == expected_margin
        )
        all_match = all_match and match
        rows.append(
            {
                "case_id": case_id,
                "score": score,
                "decision_block": decision,
                "margin": margin,
                "confidence": confidence,
                "expected_score": expected_score,
                "expected_decision": expected_decision,
                "expected_margin": expected_margin,
                "match": str(match).lower(),
                "simulator": "yosys_eval",
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} HDL eval rows to {OUT}")
    print(f"all_match: {str(all_match).lower()}")
    if not all_match:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
