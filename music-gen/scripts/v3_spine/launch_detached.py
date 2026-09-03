#!/usr/bin/env python3
"""Detached-launch helper for long v3-driver invocations.

A session boundary in the launching agent no longer kills the computation.
The child inherits env pins from the caller's process; stdout+stderr are
redirected to `logfile`. Callers poll `os.kill(pid, 0)` and tail the logfile.

Contract: see docs/v3_spine_stage_checkpointed_driver_spec.md.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"interpreter guard: expected /usr/bin/python3, got {sys.executable}")


def launch_detached(cmd: list[str], logfile: Path, workdir: Path | None = None) -> int:
    """Fork `cmd` under setsid with stdout+stderr → logfile. Return child PID.

    The child is fully detached: killing this process does not kill the child,
    and the child does not die when the parent's terminal closes. Poll the child
    with `os.kill(pid, 0)`.
    """
    logfile = Path(logfile)
    logfile.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(logfile, "ab")  # append-safe if pre-existing
    # start_new_session=True gives the child its own session (like setsid) so
    # SIGHUP from parent's controlling terminal is not delivered to it.
    proc = subprocess.Popen(
        cmd,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        cwd=str(workdir) if workdir else None,
        start_new_session=True,
        close_fds=True,
    )
    return proc.pid


def is_running(pid: int) -> bool:
    """Cheap liveness check that does not touch child state."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists but not ours to signal
    return True


if __name__ == "__main__":
    # tiny smoke: launch /bin/true detached, poll until reaped by init
    import tempfile
    import time
    with tempfile.TemporaryDirectory() as td:
        lf = Path(td) / "smoke.log"
        pid = launch_detached(["/bin/sh", "-c", "echo hi; sleep 0.1"], lf)
        assert pid > 0
        # give it a moment
        deadline = time.time() + 3.0
        while is_running(pid) and time.time() < deadline:
            time.sleep(0.05)
        assert lf.read_text().strip() == "hi", f"logfile content: {lf.read_text()!r}"
    print(f"launch_detached smoke test: PASS (pid={pid})")
