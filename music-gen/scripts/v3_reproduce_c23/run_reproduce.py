#!/usr/bin/env /usr/bin/python3
"""c23 reproduce-proof runner.

Orchestrates one song's reproduce-proof:
  1. Snapshot READ-ONLY anchor SHA (pre)
  2. Invoke c22 unified driver `scripts/v3_spine/recreate_v3.py`
  3. Copy driver-produced delivery + invoke emitter to build
     data/v3/reproduce/c23/<sha16>/reproduce_report.json
  4. Snapshot READ-ONLY anchor SHA (post) — verified inside emitter

Verdict enum + halt discipline defined in
docs/v3_reproduce_proof_c23_rubric.md.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts.v3_reproduce_c23.emit_reproduce_report import (  # noqa: E402
    snapshot_readonly_anchor, READ_ONLY_ANCHORS,
)

ANCHOR_DELIVERY = {
    # CG anchor: c5 operator-blessed operator_section dir (has panel.json + full_reconstruction_operator_section.wav)
    "31a164f845f8e27e": REPO / "data/v3/deliveries/31a164f845f8e27e/operator_section",
    # Rome anchor: parent dir where c20 clone-1 delivery lives (panel.json + original_ab.wav + full_reconstruction.wav);
    # cycle20/ only carries verdict.json. READ-ONLY anchor SHA `d2c2d704...` on cycle20/verdict.json is verified
    # separately by snapshot_readonly_anchor.
    "51e433ade2a845e1": REPO / "data/v3/deliveries/51e433ade2a845e1",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--song", required=True, choices=list(ANCHOR_DELIVERY.keys()))
    ap.add_argument("--cycle", type=int, default=23,
                    help="Driver --cycle passthrough (default 23)")
    ap.add_argument("--skip-driver", action="store_true",
                    help="Reuse existing new-delivery dir; only re-emit report")
    ap.add_argument("--dry-run", action="store_true",
                    help="Pass through to driver for a schema-only run")
    args = ap.parse_args()

    song = args.song
    anchor_dir = ANCHOR_DELIVERY[song]
    assert anchor_dir.exists(), f"anchor dir missing: {anchor_dir}"

    # New delivery dir for the c23 reproduce run
    new_dir = REPO / f"data/v3/deliveries/{song}/cycle{args.cycle}_reproduce"
    new_dir.mkdir(parents=True, exist_ok=True)
    out_report = REPO / f"data/v3/reproduce/c23/{song}/reproduce_report.json"
    out_report.parent.mkdir(parents=True, exist_ok=True)

    # (1) Snapshot READ-ONLY anchor pre
    anchor_pre = snapshot_readonly_anchor(song)
    pre_json = out_report.parent / "anchor_pre.json"
    pre_json.write_text(json.dumps(anchor_pre, indent=2, sort_keys=True) + "\n")
    print(f"[c23_run] anchor_pre matches={anchor_pre['matches']} sha={anchor_pre['observed_sha256']}")
    if not anchor_pre["matches"]:
        print(f"[c23_run] FD-1 halt: anchor pre-drift on {song}", file=sys.stderr)
        # Still emit report with FAILS verdict via emitter below (skip driver)
        driver_exit = 99
    else:
        driver_exit = 0

    # (2) Driver invocation
    if not args.skip_driver and anchor_pre["matches"]:
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = "0"
        env["SOURCE_DATE_EPOCH"] = "1756463424"
        env["TZ"] = "UTC"
        env["LC_ALL"] = "C.UTF-8"
        env["OMP_NUM_THREADS"] = "1"
        env["MKL_NUM_THREADS"] = "1"
        env["OPENBLAS_NUM_THREADS"] = "1"
        cmd = ["/usr/bin/python3", "scripts/v3_spine/recreate_v3.py",
               "--song", song, "--section", "operator",
               "--out", str(new_dir.relative_to(REPO)),
               "--cycle", str(args.cycle)]
        if args.dry_run:
            cmd.append("--dry-run")
        print(f"[c23_run] driver: {' '.join(cmd)}")
        # Live stream driver output
        proc = subprocess.run(cmd, cwd=str(REPO), env=env)
        driver_exit = proc.returncode
        print(f"[c23_run] driver exit={driver_exit}")

    # (3) Emit reproduce report
    emit_cmd = ["/usr/bin/python3", "scripts/v3_reproduce_c23/emit_reproduce_report.py",
                "--song", song,
                "--new-delivery", str(new_dir.relative_to(REPO)),
                "--anchor-delivery", str(anchor_dir.relative_to(REPO)),
                "--out", str(out_report.relative_to(REPO)),
                "--driver-exit", str(driver_exit),
                "--anchor-pre-json", str(pre_json.relative_to(REPO))]
    print(f"[c23_run] emitter: {' '.join(emit_cmd)}")
    ep = subprocess.run(emit_cmd, cwd=str(REPO))
    if ep.returncode != 0:
        print(f"[c23_run] emitter failed rc={ep.returncode}", file=sys.stderr)
        return ep.returncode

    # Verdict passthrough
    report = json.loads(out_report.read_text())
    print(f"[c23_run] song={song} verdict={report['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
