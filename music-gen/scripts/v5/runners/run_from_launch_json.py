#!/usr/bin/python3
"""Re-execute (or print) the EXACT generator command pinned in a launch JSON or a byte-determinism record.

created: 2026-09-10T04:20:00Z
cycle: 90
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/runners-decision-c90

Why: the c89 auditor's stated gap was orchestration reproducibility — the per-cycle pipeline runners lived only in the worker's
session scratchpad. Every iteration's command IS pinned on disk (`data/v5/logs/gen_iter0N_cNN.launch.json` `generate_command`;
`data/v5/gen/byte_determinism_cNN.json` `entries.<name>.command`), so this module turns those pins back into a run without
retyping anything: the command string is split with `shlex.split` and reproduced byte-for-byte in `--dry-run` (default).

Usage (from the workspace root):
    /usr/bin/python3 scripts/v5/runners/run_from_launch_json.py data/v5/logs/gen_iter05_c89.launch.json            # prints the command
    /usr/bin/python3 scripts/v5/runners/run_from_launch_json.py data/v5/gen/byte_determinism_c89.json \
        --entry iteration_04_flag_off_replay --out /tmp/some_fresh_dir                                             # entry command, --out swapped
    /usr/bin/python3 scripts/v5/runners/run_from_launch_json.py <json> --execute --log data/v5/logs/<name>.log     # detached via launch_detached

Discipline: `/usr/bin/python3` interpreter guard; no PRNG; no wall-clock in the command; `--execute` REFUSES to run when the pinned
`generate_v5` sha in the record differs from the on-disk `scripts/v5/generate_v5.py` (drift = a new proof, not a replay) unless
`--allow-drift` is given; `--out` must be given with `--execute` unless `--in-place` is given (never overwrite an iteration tree by accident).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_HERE = Path(__file__).resolve()
_WS = next(p for p in _HERE.parents if (p / "scripts" / "v5" / "repo_root.py").exists())
sys.path.insert(0, str(_WS))
from scripts.v5.repo_root import repo_root  # noqa: E402

ROOT = repo_root(__file__)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pinned_command(record: dict, entry: str | None) -> tuple[str, str | None]:
    """Return (command_string, pinned_generate_v5_sha) from a launch JSON (`generate_command`) or a byte-det record entry."""
    if entry:
        ent = record["entries"][entry]
        return ent["command"], ent.get("generate_v5_sha256")
    if "generate_command" in record:
        return record["generate_command"], record.get("generate_v5_sha256_post_edit")
    if "cmd" in record:  # c79 transcription launch JSON shape
        return " ".join(record["cmd"]), None
    raise KeyError("record carries neither 'generate_command' nor 'cmd'; pass --entry for a byte-determinism record")


def rewrite_out(argv: list[str], out: str | None) -> list[str]:
    if out is None:
        return argv
    if "--out" in argv:
        i = argv.index("--out")
        return argv[: i + 1] + [out] + argv[i + 2:]
    return argv + ["--out", out]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("record", help="launch JSON or byte_determinism JSON (workspace-relative or absolute)")
    ap.add_argument("--entry", default=None, help="byte_determinism record: entries.<name> whose `command` to use")
    ap.add_argument("--out", default=None, help="replace the pinned --out with this directory (required with --execute unless --in-place)")
    ap.add_argument("--in-place", action="store_true", help="allow --execute with the pinned --out (overwrites the iteration tree only if the generator does)")
    ap.add_argument("--execute", action="store_true", help="launch detached via scripts/v3_spine/launch_detached (default: dry-run print)")
    ap.add_argument("--log", default=None, help="logfile for --execute (required)")
    ap.add_argument("--allow-drift", action="store_true", help="execute even if on-disk generate_v5.py sha != pinned sha")
    a = ap.parse_args()
    os.chdir(ROOT)
    rec = json.loads(Path(a.record).read_text())
    cmd_s, pinned = pinned_command(rec, a.entry)
    argv = rewrite_out(shlex.split(cmd_s), a.out)
    on_disk = _sha(ROOT / "scripts" / "v5" / "generate_v5.py")
    drift = bool(pinned) and pinned != on_disk
    if not a.execute:
        print(cmd_s)
        if a.out:
            print("# with --out swapped:", shlex.join(argv), file=sys.stderr)
        print(f"# pinned generate_v5 sha {pinned} ; on-disk {on_disk} ; drift={drift}", file=sys.stderr)
        return 0
    if drift and not a.allow_drift:
        print(f"REFUSED: generate_v5.py drifted ({on_disk[:16]}… vs pinned {str(pinned)[:16]}…); a replay on a drifted image is a new proof — pass --allow-drift", file=sys.stderr)
        return 3
    if a.out is None and not a.in_place:
        print("REFUSED: --execute needs --out <fresh dir> (or --in-place)", file=sys.stderr)
        return 3
    if not a.log:
        print("REFUSED: --execute needs --log <file>", file=sys.stderr)
        return 3
    from scripts.v3_spine.launch_detached import launch_detached  # READ-ONLY c24 helper
    pid = launch_detached(argv, Path(a.log), ROOT)
    print(json.dumps({"pid": pid, "log": a.log, "command": shlex.join(argv), "pinned_generate_v5_sha256": pinned, "on_disk_generate_v5_sha256": on_disk}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
