"""CLI for egress-ready state machine.

Usage:
  python3 -m scripts.egress_ready.cli --watch              # single-shot scan
  python3 -m scripts.egress_ready.cli --watch --loop 60    # poll every 60s (not used in tests)
  python3 -m scripts.egress_ready.cli --status             # pretty-print state.json
  python3 -m scripts.egress_ready.cli --force-idle         # any state -> IDLE
  python3 -m scripts.egress_ready.cli --force-trigger      # IDLE/ARMED -> TRIGGERED
  python3 -m scripts.egress_ready.cli --resume             # FAILED -> restart failing stage
  python3 -m scripts.egress_ready.cli --reset-failure --force-idle  # FAILED -> IDLE

created: 2026-08-28
cycle: 8
milestone: M-INGEST-1/egress-ready-automation
"""
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", (
    f"scripts/egress_ready expects /usr/bin/python3, got {sys.executable}"
)

import argparse
import json
import time
from pathlib import Path

from scripts.egress_ready.state import (
    EgressReadyMachine,
    InvalidTransition,
    force_idle,
    force_trigger,
    reset_failure,
    resume,
)


DEFAULT_STATE_PATH = Path("data/egress_ready/state.json")
DEFAULT_TRANSITIONS_PATH = Path("data/egress_ready/transitions.jsonl")
DEFAULT_EGRESS_STATUS_PATH = Path("data/ingestion/egress_status.jsonl")
DEFAULT_DIAGNOSTIC_DIR = Path("data/egress_ready/")


def _build_machine(args) -> EgressReadyMachine:
    return EgressReadyMachine(
        state_path=Path(args.state_path),
        transitions_path=Path(args.transitions_path),
        egress_status_path=Path(args.egress_status_path),
        diagnostic_dir=Path(args.diagnostic_dir),
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="egress_ready")
    ap.add_argument("--watch", action="store_true", help="scan egress_status.jsonl and advance")
    ap.add_argument("--loop", type=int, default=0, help="if >0, poll every N seconds (stub)")
    ap.add_argument("--status", action="store_true", help="print current state.json")
    ap.add_argument("--force-idle", action="store_true", help="force state to IDLE")
    ap.add_argument("--force-trigger", action="store_true", help="force TRIGGERED from IDLE/ARMED")
    ap.add_argument("--resume", action="store_true", help="from FAILED, restart failing stage")
    ap.add_argument("--reset-failure", action="store_true",
                    help="from FAILED, allow IDLE reset (requires --force-idle)")
    ap.add_argument("--state-path", default=str(DEFAULT_STATE_PATH))
    ap.add_argument("--transitions-path", default=str(DEFAULT_TRANSITIONS_PATH))
    ap.add_argument("--egress-status-path", default=str(DEFAULT_EGRESS_STATUS_PATH))
    ap.add_argument("--diagnostic-dir", default=str(DEFAULT_DIAGNOSTIC_DIR))
    args = ap.parse_args(argv)

    if args.status:
        p = Path(args.state_path)
        if p.is_file():
            print(p.read_text(encoding="utf-8").rstrip())
        else:
            print(json.dumps({"state": "IDLE", "note": "no state.json yet"}, indent=2))
        return 0

    # --reset-failure without --force-idle is a documented refusal.
    if args.reset_failure and not args.force_idle:
        print("REFUSED: --reset-failure requires --force-idle to acknowledge", file=sys.stderr)
        return 2

    machine = _build_machine(args)
    try:
        if args.reset_failure:
            reset_failure(machine, force_idle_ack=True)
            return 0
        if args.force_idle:
            force_idle(machine)
            return 0
        if args.force_trigger:
            force_trigger(machine)
            return 0
        if args.resume:
            resume(machine)
            return 0
        if args.watch:
            if args.loop and args.loop > 0:
                # Live polling; not exercised by tests this cycle.
                while True:
                    machine.scan_and_advance()
                    time.sleep(args.loop)
            else:
                machine.scan_and_advance()
            return 0
    except InvalidTransition as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 3

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
