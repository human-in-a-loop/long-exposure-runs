# created: 2026-05-13T20:06:00Z
# cycle: 11
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-TOOLCHAIN-1
"""Probe local HDL toolchain capability for the safety-filter prototype.

This is a verification refresh only. It detects whether compiled Verilator
simulation is currently possible, reruns existing lint/Yosys/Graphviz checks,
and preserves the campaign closure invariants.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import struct
import subprocess
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "physicalized-weights"
DATA = BASE / "data"
DOCS = BASE / "docs"
HDL = BASE / "hdl" / "safety_filter_core.sv"
TB = BASE / "hdl" / "safety_filter_core_tb.cpp"
YOSYS_SCRIPT = BASE / "hdl" / "safety_filter_core.ys"
YOSYS_EVAL = BASE / "hdl" / "run_yosys_eval.py"
PY_PROTO = BASE / "scripts" / "prototype_safety_filter.py"
VERIFY_PROTO = BASE / "scripts" / "verify_prototype_closure.py"

MATRIX_CSV = DATA / "toolchain_condition_matrix.csv"
SUMMARY_JSON = DATA / "toolchain_condition_summary.json"
FIGURE_PNG = DATA / "toolchain_condition_matrix.png"
REPORT_MD = DOCS / "toolchain_condition_report.md"
COMPILED_RESULTS = DATA / "compiled_verilator_safety_filter_results.csv"
VERILATOR_REFRESH_LOG = DATA / "toolchain_verilator_lint.log"
YOSYS_EVAL_LOG = DATA / "toolchain_yosys_eval.log"
YOSYS_SYNTH_LOG = DATA / "toolchain_yosys_synthesis.log"
GRAPHVIZ_LOG = DATA / "toolchain_graphviz.log"
NETLIST_DOT = DATA / "safety_filter_core_netlist.dot"
NETLIST_PNG = DATA / "safety_filter_core_netlist.png"
HDL_RESULTS = DATA / "hdl_sim_results.csv"
BUILD_DIR = BASE / "build" / "toolchain_verilator"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_capture(command: list[str], log_path: Path, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("$ " + " ".join(command) + "\n" + completed.stdout)
    return completed


def tool_version(name: str, command: list[str]) -> dict[str, str | bool]:
    path = shutil.which(name)
    if not path:
        return {"tool": name, "available": False, "path": "", "version": ""}
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    first = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else ""
    return {"tool": name, "available": completed.returncode == 0, "path": path, "version": first}


def detect_tools() -> dict[str, dict[str, str | bool]]:
    tools = {
        "verilator": tool_version("verilator", ["verilator", "--version"]),
        "yosys": tool_version("yosys", ["yosys", "-V"]),
        "dot": tool_version("dot", ["dot", "-V"]),
        "make": tool_version("make", ["make", "--version"]),
    }
    compiler = None
    for name in ("c++", "g++", "clang++"):
        candidate = tool_version(name, [name, "--version"])
        if candidate["available"]:
            compiler = candidate
            break
    tools["cxx_compiler"] = compiler or {"tool": "c++|g++|clang++", "available": False, "path": "", "version": ""}
    return tools


def compiled_status(tools: dict[str, dict[str, str | bool]]) -> tuple[bool, list[str], str]:
    required = ["verilator", "make", "cxx_compiler"]
    missing = [name for name in required if not tools[name]["available"]]
    if missing:
        return False, missing, "blocked_environment"
    return True, [], "available"


def csv_all_matches(path: Path) -> bool | None:
    if not path.exists():
        return None
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return False
    return all(row.get("match") == "true" for row in rows)


def run_compiled_verilator() -> tuple[str, bool | None, str]:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    if COMPILED_RESULTS.exists():
        COMPILED_RESULTS.unlink()
    command = [
        "verilator",
        "-sv",
        "--cc",
        rel(HDL),
        "--exe",
        rel(TB),
        "--build",
        "-Mdir",
        rel(BUILD_DIR),
        "--top-module",
        "safety_filter_core",
    ]
    completed = run_capture(command, DATA / "toolchain_compiled_verilator.log")
    exe = BUILD_DIR / "Vsafety_filter_core"
    if completed.returncode != 0 or not exe.exists():
        return "failed", False, rel(DATA / "toolchain_compiled_verilator.log")
    run = run_capture([rel(exe), rel(COMPILED_RESULTS)], DATA / "toolchain_compiled_verilator_run.log")
    if run.returncode != 0:
        return "failed", False, rel(DATA / "toolchain_compiled_verilator_run.log")
    return "passed" if csv_all_matches(COMPILED_RESULTS) else "failed", csv_all_matches(COMPILED_RESULTS), rel(COMPILED_RESULTS)


def write_png(path: Path, rows: list[dict[str, str]]) -> None:
    width, height = 960, 420
    pixels = bytearray([250, 251, 252] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            base = y * width * 3
            for x in range(max(0, x0), min(width, x1)):
                idx = base + x * 3
                pixels[idx : idx + 3] = bytes(color)

    colors = {
        "passed": (50, 145, 90),
        "available": (50, 145, 90),
        "checked": (50, 145, 90),
        "blocked_environment": (220, 170, 55),
        "missing": (220, 170, 55),
        "failed": (190, 70, 65),
    }
    left, top, row_h, max_w = 300, 42, 30, 570
    rect(0, 0, width, height, (248, 249, 250))
    for idx, row in enumerate(rows):
        y = top + idx * row_h
        rect(20, y, width - 20, y + row_h - 4, (255, 255, 255) if idx % 2 == 0 else (242, 245, 247))
        status = row["status"]
        bar = max(80, int(max_w * (1.0 if status in ("passed", "available", "checked") else 0.45)))
        rect(left, y + 6, left + bar, y + row_h - 10, colors.get(status, (170, 170, 170)))
        rect(left, y + row_h - 9, left + max_w, y + row_h - 8, (210, 214, 218))

    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    payload = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(raw, 9)),
            chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(payload)


def chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_report(summary: dict[str, object], matrix_rows: list[dict[str, str]]) -> None:
    tool_rows = "\n".join(
        f"| {row['check_id']} | {row['tool']} | {row['available']} | {row['version']} | {row['status']} | {row['blocker']} |"
        for row in matrix_rows
    )
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T20:06:00Z
cycle: 11
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-TOOLCHAIN-1
---

# Toolchain Condition Report

## Scope

This report is a prototype-verification refresh only. It is not a performance/economic reopen path, does not add a new reopen gate, and does not change the Phase 2 stronger-baseline downgrade or campaign closure endpoint.

## Tool Availability And Checks

| check_id | tool | available | version | status | blocker |
|---|---:|---:|---|---|---|
{tool_rows}

## Existing M-PROTO-1 Evidence Contract Recap

The validated prototype contract is a fixed combinational safety-filter HDL core checked against Python golden vectors, Yosys eval rows, Verilator lint, Yosys synthesis with no memories/processes, and Graphviz netlist artifacts. Compiled Verilator simulation can strengthen this contract only if local `verilator`, `make`, and a C++ compiler are available.

## Conditional Compiled-Verilator Outcome

`compiled_verilator_status`: `{summary['compiled_verilator_status']}`

`compiled_verilator_equivalence_passed`: `{summary['compiled_verilator_equivalence_passed']}`

Missing compiled-simulation tools: `{', '.join(summary['compiled_verilator_missing_tools']) if summary['compiled_verilator_missing_tools'] else 'none'}`

## Lint, Yosys, And Graphviz Refresh

Verilator lint passed: `{summary['verilator_lint_passed']}`.

Yosys eval passed: `{summary['yosys_eval_passed']}`.

Graphviz artifact checked: `{summary['graphviz_artifact_checked']}`.

![local HDL/toolchain capability and verification coverage for the safety-filter prototype, distinguishing passed checks from environment-blocked compiled simulation.](../data/toolchain_condition_matrix.png)

## Interpretation Boundaries

This cycle tests local toolchain condition and prototype verification modality. It introduces no workload evidence, measured production trace, baseline economics, or superiority claim.

## Prototype Reopen Conditions

Reopen prototype correctness only if compiled simulation runs and disagrees with golden vectors, Verilator lint fails, Yosys eval/synthesis fails, the HDL source hash changes without refreshed evidence, or the HDL design gains sequential state, memories, handshake timing, or mutable policy logic.
""",
        encoding="utf-8",
    )


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    tools = detect_tools()
    compiled_available, missing_compiled, initial_compiled_status = compiled_status(tools)

    lint_passed = False
    if tools["verilator"]["available"]:
        lint = run_capture(["verilator", "--lint-only", "-sv", rel(HDL)], VERILATOR_REFRESH_LOG)
        lint_passed = lint.returncode == 0

    yosys_eval_passed = False
    if tools["yosys"]["available"]:
        y_eval = run_capture(["python3", rel(YOSYS_EVAL)], YOSYS_EVAL_LOG)
        yosys_eval_passed = y_eval.returncode == 0 and csv_all_matches(HDL_RESULTS) is True
        y_synth = run_capture(["yosys", "-s", rel(YOSYS_SCRIPT)], YOSYS_SYNTH_LOG)
        yosys_synth_passed = y_synth.returncode == 0 and "Found and reported 0 problems." in YOSYS_SYNTH_LOG.read_text()
    else:
        yosys_synth_passed = False

    graphviz_checked = False
    if tools["dot"]["available"] and NETLIST_DOT.exists():
        dot_run = run_capture(["dot", "-Tpng", rel(NETLIST_DOT), "-o", rel(NETLIST_PNG)], GRAPHVIZ_LOG)
        graphviz_checked = dot_run.returncode == 0 and NETLIST_PNG.exists() and NETLIST_PNG.stat().st_size > 0

    compiled_equivalence: bool | None = None
    compiled_evidence = ""
    compiled_status_value = initial_compiled_status
    if compiled_available:
        compiled_status_value, compiled_equivalence, compiled_evidence = run_compiled_verilator()
    else:
        compiled_evidence = "missing: " + ",".join(missing_compiled)

    hashes = {
        "hdl_source_sha256": sha256(HDL),
        "prototype_generator_sha256": sha256(PY_PROTO),
        "yosys_eval_script_sha256": sha256(YOSYS_EVAL),
        "yosys_script_sha256": sha256(YOSYS_SCRIPT),
        "verilator_testbench_sha256": sha256(TB),
        "prototype_closure_script_sha256": sha256(VERIFY_PROTO),
    }

    matrix_rows: list[dict[str, str]] = []

    def add_row(check_id: str, tool: str, available: bool, version: str, required_for: str, status: str, blocker: str, evidence: str) -> None:
        matrix_rows.append(
            {
                "check_id": check_id,
                "tool": tool,
                "available": str(bool(available)).lower(),
                "version": version,
                "required_for": required_for,
                "status": status,
                "blocker": blocker,
                "evidence_artifact": evidence,
            }
        )

    for key, required_for in [
        ("verilator", "lint and compiled simulation"),
        ("yosys", "HDL eval and synthesis refresh"),
        ("dot", "Graphviz netlist freshness"),
        ("make", "compiled Verilator build"),
        ("cxx_compiler", "compiled Verilator build"),
    ]:
        tool = tools[key]
        add_row(
            f"tool_{key}",
            str(tool["tool"]),
            bool(tool["available"]),
            str(tool["version"]),
            required_for,
            "available" if tool["available"] else "missing",
            "" if tool["available"] else "not found on PATH",
            str(tool["path"]),
        )

    add_row("check_verilator_lint", "verilator", bool(tools["verilator"]["available"]), str(tools["verilator"]["version"]), "prototype lint", "passed" if lint_passed else "failed", "" if lint_passed else "lint unavailable or failed", rel(VERILATOR_REFRESH_LOG))
    add_row("check_yosys_eval", "yosys", bool(tools["yosys"]["available"]), str(tools["yosys"]["version"]), "golden-vector HDL eval", "passed" if yosys_eval_passed else "failed", "" if yosys_eval_passed else "yosys eval unavailable or mismatch", rel(HDL_RESULTS))
    add_row("check_yosys_synthesis", "yosys", bool(tools["yosys"]["available"]), str(tools["yosys"]["version"]), "structural synthesis", "passed" if yosys_synth_passed else "failed", "" if yosys_synth_passed else "yosys synthesis unavailable or failed", rel(YOSYS_SYNTH_LOG))
    add_row("check_graphviz_netlist", "dot", bool(tools["dot"]["available"]), str(tools["dot"]["version"]), "netlist artifact freshness", "checked" if graphviz_checked else "failed", "" if graphviz_checked else "dot unavailable or render failed", rel(NETLIST_PNG))
    add_row("check_compiled_verilator", "verilator+make+cxx", compiled_available, "conditional", "compiled HDL equivalence", compiled_status_value, ",".join(missing_compiled), compiled_evidence)

    summary = {
        "schema_version": 1,
        "milestone_id": "M-TOOLCHAIN-1",
        "status": "validated" if lint_passed and yosys_eval_passed and yosys_synth_passed and graphviz_checked and compiled_status_value in ("passed", "blocked_environment") else "failed",
        "compiled_verilator_available": compiled_available,
        "compiled_verilator_status": compiled_status_value,
        "compiled_verilator_missing_tools": missing_compiled,
        "compiled_verilator_equivalence_passed": compiled_equivalence,
        "verilator_lint_passed": lint_passed,
        "yosys_eval_passed": yosys_eval_passed,
        "yosys_synthesis_passed": yosys_synth_passed,
        "graphviz_artifact_checked": graphviz_checked,
        **hashes,
        "source_hashes": hashes,
        "current_superiority_claim_count": 0,
        "actual_reopen_candidate_count": 0,
        "new_reopen_gate_count": 0,
        "prototype_claim_reopened": not (lint_passed and yosys_eval_passed and yosys_synth_passed and (compiled_status_value == "blocked_environment" or compiled_equivalence is True)),
        "performance_claim_reopened": False,
        "figure_caption": "local HDL/toolchain capability and verification coverage for the safety-filter prototype, distinguishing passed checks from environment-blocked compiled simulation.",
    }

    with MATRIX_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(matrix_rows[0].keys()))
        writer.writeheader()
        writer.writerows(matrix_rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n")
    write_png(FIGURE_PNG, matrix_rows)
    write_report(summary, matrix_rows)

    print(f"wrote {MATRIX_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {FIGURE_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"compiled_verilator_status: {compiled_status_value}")
    print(f"status: {summary['status']}")
    if summary["status"] != "validated":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
