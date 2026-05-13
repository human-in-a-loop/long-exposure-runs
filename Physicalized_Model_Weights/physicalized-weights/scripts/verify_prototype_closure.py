# created: 2026-05-13T04:05:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PROTO-1
"""Verify closure evidence for the M-PROTO-1 safety-filter HDL prototype.

This script does not build new hardware. It ties the existing Python golden
model, emitted vector files, Yosys eval rows, Verilator lint log, Yosys
synthesis log, HDL source, and Graphviz netlist artifacts into one explicit
verification contract.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import shutil
import struct
import sys
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "physicalized-weights"
DATA = BASE / "data"
HDL = BASE / "hdl" / "safety_filter_core.sv"
PY_PROTO = BASE / "scripts" / "prototype_safety_filter.py"
VECTORS_CSV = DATA / "prototype_vectors.csv"
ROUTES_CSV = DATA / "prototype_route_results.csv"
HDL_RESULTS_CSV = DATA / "hdl_sim_results.csv"
SUMMARY_JSON = DATA / "prototype_summary.json"
VERILATOR_LOG = DATA / "verilator_safety_filter.log"
YOSYS_LOG = DATA / "yosys_safety_filter.log"
NETLIST_DOT = DATA / "safety_filter_core_netlist.dot"
NETLIST_PNG = DATA / "safety_filter_core_netlist.png"
YOSYS_SCRIPT = BASE / "hdl" / "safety_filter_core.ys"
YOSYS_EVAL_SCRIPT = BASE / "hdl" / "run_yosys_eval.py"
OUT_JSON = DATA / "prototype_verification_closure.json"
OUT_CSV = DATA / "prototype_equivalence_matrix.csv"
OUT_PNG = DATA / "prototype_equivalence_matrix.png"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def artifacts_are_fresh(sources: list[Path], artifacts: list[Path]) -> bool:
    newest_source = max(path.stat().st_mtime_ns for path in sources)
    return all(path.exists() and path.stat().st_size > 0 and path.stat().st_mtime_ns >= newest_source for path in artifacts)


def load_proto_module():
    spec = importlib.util.spec_from_file_location("prototype_safety_filter", PY_PROTO)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {PY_PROTO}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["prototype_safety_filter"] = module
    spec.loader.exec_module(module)
    return module


def parse_hdl_params(text: str) -> dict[str, int | list[int]]:
    def signed(name: str) -> int:
        pattern = re.compile(
            rf"localparam signed \[[^\]]+\] {name} =\s*(-?)(?:\d+)'sd(\d+);"
        )
        match = pattern.search(text)
        if not match:
            raise RuntimeError(f"missing HDL localparam {name}")
        sign, value = match.groups()
        number = int(value)
        return -number if sign else number

    return {
        "weights": [signed(f"W{i}") for i in range(8)],
        "bias": signed("BIAS"),
        "threshold": signed("THRESHOLD"),
    }


def verilator_status(log_text: str) -> dict[str, object]:
    lint_segment = log_text.split("Verilator build attempt:")[0]
    lint_passed = "Verilator lint:" in lint_segment and "%Error" not in lint_segment
    make_missing = "make: not found" in log_text
    compiler_missing = not any(shutil.which(name) for name in ("c++", "g++", "clang++"))
    make_available = shutil.which("make") is not None
    compiler_available = not compiler_missing
    compiled_passed = (
        "compiled_verilator_passed: true" in log_text.lower()
        or "Verilator compiled simulation passed" in log_text
    )
    return {
        "lint_passed": lint_passed,
        "make_available": make_available,
        "compiler_available": compiler_available,
        "make_constraint_recorded": make_missing or not make_available,
        "compiled_simulation_present": compiled_passed,
        "compiled_simulation_passed": compiled_passed,
        "compiled_simulation_status": "passed"
        if compiled_passed
        else ("blocked_make_unavailable" if make_missing or not make_available else "not_run"),
    }


def write_png(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    cell = 34
    left = 260
    top = 56
    width = left + cell * len(columns) + 20
    height = top + cell * len(rows) + 28
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            row = y * width * 3
            for x in range(max(0, x0), min(width, x1)):
                idx = row + x * 3
                pixels[idx : idx + 3] = bytes(color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        if x0 == x1:
            rect(x0, min(y0, y1), x0 + 1, max(y0, y1) + 1, color)
        elif y0 == y1:
            rect(min(x0, x1), y0, max(x0, x1) + 1, y0 + 1, color)

    colors = {"pass": (55, 145, 95), "n/a": (190, 190, 190), "fail": (195, 70, 65)}
    rect(0, 0, width, height, (248, 249, 250))
    for row_idx, row in enumerate(rows):
        y = top + row_idx * cell
        rect(0, y, width, y + cell, (255, 255, 255) if row_idx % 2 == 0 else (242, 245, 247))
        for col_idx, column in enumerate(columns):
            x = left + col_idx * cell
            value = row[column]
            rect(x + 5, y + 5, x + cell - 5, y + cell - 5, colors.get(value, colors["fail"]))
            line(x, y, x + cell, y, (220, 224, 228))
            line(x, y, x, y + cell, (220, 224, 228))
    line(left, top, left + cell * len(columns), top, (80, 80, 80))
    line(left, top, left, top + cell * len(rows), (80, 80, 80))

    # Tiny bitmap-style labels are intentionally minimal; CSV/JSON carry full labels.
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


def main() -> None:
    proto = load_proto_module()
    summary = json.loads(SUMMARY_JSON.read_text())
    hdl_text = HDL.read_text()
    hdl_params = parse_hdl_params(hdl_text)
    py_params = {
        "weights": proto.WEIGHTS,
        "bias": proto.BIAS,
        "threshold": proto.THRESHOLD,
        "feature_count": proto.FEATURE_COUNT,
        "confidence_threshold": proto.CONFIDENCE_THRESHOLD,
    }
    summary_params = {
        "weights": summary["weights"],
        "bias": summary["bias"],
        "threshold": summary["threshold"],
        "feature_count": summary["feature_count"],
        "confidence_threshold": summary["confidence_threshold"],
    }

    vector_rows = {row["case_id"]: row for row in read_csv(VECTORS_CSV)}
    route_rows = {row["case_id"]: row for row in read_csv(ROUTES_CSV)}
    yosys_rows = read_csv(HDL_RESULTS_CSV)
    log_text = VERILATOR_LOG.read_text()
    yosys_log = YOSYS_LOG.read_text()
    verilator = verilator_status(log_text)
    yosys_synthesis_passed = "Found and reported 0 problems." in yosys_log
    yosys_no_state = (
        "Number of memories:               0" in yosys_log
        and "Number of processes:              0" in yosys_log
    )
    graphviz_present = NETLIST_DOT.exists() and NETLIST_DOT.stat().st_size > 0
    graphviz_present = graphviz_present and NETLIST_PNG.exists() and NETLIST_PNG.stat().st_size > 0
    structural_artifacts_fresh = artifacts_are_fresh(
        [HDL, YOSYS_SCRIPT, YOSYS_EVAL_SCRIPT],
        [HDL_RESULTS_CSV, YOSYS_LOG, NETLIST_DOT, NETLIST_PNG],
    )

    matrix_rows: list[dict[str, str]] = []
    all_yosys_match = True
    for row in yosys_rows:
        case_id = row["case_id"]
        py_row = vector_rows.get(case_id)
        route_row = route_rows.get(case_id)
        py_match = (
            py_row is not None
            and int(py_row["score"]) == int(row["score"])
            and (py_row["decision"] == "block") == (row["decision_block"] == "1")
            and int(py_row["margin"]) == int(row["margin"])
            and int(py_row["confidence"]) == int(row["confidence"])
        )
        route_match = (
            route_row is not None
            and int(route_row["score"]) == int(row["score"])
            and int(route_row["margin"]) == int(row["margin"])
        )
        yosys_match = row["match"] == "true" and py_match and route_match
        all_yosys_match = all_yosys_match and yosys_match
        matrix_rows.append(
            {
                "case_id": case_id,
                "python_golden": "pass" if py_match else "fail",
                "route_output": "pass" if route_match else "fail",
                "yosys_eval": "pass" if yosys_match else "fail",
                "verilator_lint": "pass" if verilator["lint_passed"] else "fail",
                "yosys_synthesis": "pass" if yosys_synthesis_passed and yosys_no_state else "fail",
                "graphviz_artifacts": "pass" if graphviz_present else "fail",
                "compiled_verilator": "pass"
                if verilator["compiled_simulation_passed"]
                else "n/a",
                "overall": "pass"
                if (
                    yosys_match
                    and verilator["lint_passed"]
                    and yosys_synthesis_passed
                    and yosys_no_state
                    and graphviz_present
                )
                else "fail",
            }
        )

    hdl_params_match_python = (
        hdl_params["weights"] == py_params["weights"]
        and hdl_params["bias"] == py_params["bias"]
        and hdl_params["threshold"] == py_params["threshold"]
    )
    summary_params_match_python = summary_params == py_params
    closure_passed = (
        all_yosys_match
        and hdl_params_match_python
        and summary_params_match_python
        and verilator["lint_passed"]
        and (verilator["compiled_simulation_passed"] or verilator["make_constraint_recorded"])
        and yosys_synthesis_passed
        and yosys_no_state
        and graphviz_present
        and structural_artifacts_fresh
        and all(row["overall"] == "pass" for row in matrix_rows)
    )

    fieldnames = list(matrix_rows[0].keys())
    with OUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matrix_rows)

    write_png(
        OUT_PNG,
        matrix_rows,
        [
            "python_golden",
            "route_output",
            "yosys_eval",
            "verilator_lint",
            "yosys_synthesis",
            "graphviz_artifacts",
            "compiled_verilator",
            "overall",
        ],
    )

    closure = {
        "schema_version": 1,
        "milestone_id": "M-PROTO-1",
        "closure_status": "validated" if closure_passed else "failed",
        "evidence_contract": "amended_lint_yosys_eval_synthesis"
        if not verilator["compiled_simulation_passed"]
        else "compiled_verilator_plus_yosys",
        "compiled_verilator": verilator,
        "hashes": {
            "hdl_source_sha256": sha256(HDL),
            "python_source_sha256": sha256(PY_PROTO),
            "prototype_vectors_sha256": sha256(VECTORS_CSV),
            "prototype_route_results_sha256": sha256(ROUTES_CSV),
            "hdl_sim_results_sha256": sha256(HDL_RESULTS_CSV),
            "prototype_summary_sha256": sha256(SUMMARY_JSON),
            "verilator_log_sha256": sha256(VERILATOR_LOG),
            "yosys_log_sha256": sha256(YOSYS_LOG),
            "netlist_dot_sha256": sha256(NETLIST_DOT),
            "netlist_png_sha256": sha256(NETLIST_PNG),
        },
        "freshness": {
            "structural_artifacts_fresh": structural_artifacts_fresh,
            "source_files": [
                str(HDL.relative_to(ROOT)),
                str(YOSYS_SCRIPT.relative_to(ROOT)),
                str(YOSYS_EVAL_SCRIPT.relative_to(ROOT)),
            ],
            "generated_artifacts": [
                str(HDL_RESULTS_CSV.relative_to(ROOT)),
                str(YOSYS_LOG.relative_to(ROOT)),
                str(NETLIST_DOT.relative_to(ROOT)),
                str(NETLIST_PNG.relative_to(ROOT)),
            ],
        },
        "parameters": {
            "python": py_params,
            "hdl": hdl_params,
            "summary": summary_params,
            "hdl_params_match_python": hdl_params_match_python,
            "summary_params_match_python": summary_params_match_python,
        },
        "vector_counts": {
            "python_vectors": len(vector_rows),
            "route_rows": len(route_rows),
            "yosys_eval_rows": len(yosys_rows),
            "equivalence_rows": len(matrix_rows),
        },
        "checks": {
            "yosys_eval_matches_python": all_yosys_match,
            "verilator_lint_passed": verilator["lint_passed"],
            "yosys_synthesis_passed": yosys_synthesis_passed,
            "yosys_reports_no_memories_or_processes": yosys_no_state,
            "graphviz_artifacts_present": graphviz_present,
            "structural_artifacts_fresh": structural_artifacts_fresh,
            "closure_tests_required": True,
        },
        "reopen_criteria": [
            "compiled Verilator simulation later runs and disagrees with Python or Yosys rows",
            "Yosys eval and Python golden outputs diverge for any vector",
            "HDL source hash changes without regenerated closure artifacts",
            "the HDL core gains sequential state, memories, handshake timing, or mutable policy logic",
            "Verilator lint, Yosys synthesis, or Graphviz netlist evidence becomes missing or stale",
        ],
        "figure_caption": (
            "equivalence matrix showing which prototype evidence paths agree for each fixed "
            "classifier vector: Python golden model, Yosys HDL eval, lint/synthesis structural "
            "checks, and generated artifacts."
        ),
    }
    OUT_JSON.write_text(json.dumps(closure, indent=2) + "\n")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_PNG}")
    print(f"closure_status: {closure['closure_status']}")
    if not closure_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
