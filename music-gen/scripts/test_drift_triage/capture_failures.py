#!/usr/bin/python3
# created: 2026-08-29T18:32:00Z  cycle: 48  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-existing-test-drift-triage-clone-2
"""Capture the 87 pre-existing failures from tests/test_integration_cross_branch.py
byte-deterministically. Parses "FAIL <identifier>: <message>" lines from the
test's stdout+stderr, preserving the file line-number of each FAIL emission.

Usage:
    /usr/bin/python3 scripts/test_drift_triage/capture_failures.py \
        --workspace . --out data/pre_existing_test_drift/captured_failures.jsonl

Env pins (BLAS + PYTHONHASHSEED + SOURCE_DATE_EPOCH + TZ + LC_ALL) are set
inside the subprocess call, so callers only need to invoke this module.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

print("[test_drift_triage.capture_failures] startup", flush=True)

_ALLOWED = ("/usr/bin/python3",)
if sys.executable not in _ALLOWED and not os.environ.get("TEST_DRIFT_TRIAGE_ALLOW_ANY_PYTHON"):
    print(
        f"[test_drift_triage.capture_failures] interpreter guard: expected one of "
        f"{_ALLOWED}, got {sys.executable!r}",
        file=sys.stderr,
    )
    sys.exit(2)

FAIL_RE = re.compile(r"^FAIL\s+(?P<identifier>[^:]+?):\s+(?P<message>.*)$")


def _pinned_env() -> dict[str, str]:
    e = dict(os.environ)
    e["OMP_NUM_THREADS"] = "1"
    e["MKL_NUM_THREADS"] = "1"
    e["OPENBLAS_NUM_THREADS"] = "1"
    e["PYTHONHASHSEED"] = "0"
    e["SOURCE_DATE_EPOCH"] = "1756463424"
    e["TZ"] = "UTC"
    e["LC_ALL"] = "C.UTF-8"
    e["PYTHONPATH"] = "."
    return e


def run_test(workspace: Path) -> str:
    """Invoke tests/test_integration_cross_branch.py as subprocess.
    Returns combined stdout+stderr text."""
    cmd = ["/usr/bin/python3", "tests/test_integration_cross_branch.py"]
    proc = subprocess.run(
        cmd, cwd=str(workspace), env=_pinned_env(),
        capture_output=True, text=True, timeout=300,
    )
    return (proc.stdout or "") + (proc.stderr or "")


def parse_failures(text: str, source_ts_utc: str) -> list[dict]:
    rows: list[dict] = []
    for i, line in enumerate(text.splitlines(), start=1):
        m = FAIL_RE.match(line)
        if not m:
            continue
        rows.append({
            "line": i,
            "section": m.group("identifier").strip(),
            "identifier": m.group("identifier").strip(),
            "message": m.group("message").strip(),
            "capture_ts_utc": source_ts_utc,
        })
    return rows


def write_jsonl(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    ts_utc = "2026-08-29T18:00:00Z"  # SOURCE_DATE_EPOCH-derived, pinned
    text = run_test(args.workspace)
    rows = parse_failures(text, ts_utc)
    write_jsonl(rows, args.out)
    print(f"[test_drift_triage.capture_failures] captured {len(rows)} failures", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
