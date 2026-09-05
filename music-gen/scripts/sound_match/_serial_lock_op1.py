#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-05T00:00:00Z
# cycle: 32
# run_id: run-2026-09-05T000000Z
# agent: worker
# milestone: _plan/register-OP-1-fine-fit-serial-lock
# ---
"""OP-1 serial-launch lock helper for fine-fit drivers loading VGGish.

Contract (per docs/agent_picks_selection_invariants.md operational invariant OP-1):

    Fine-fit drivers that load VGGish embeddings MUST run serial. This module
    provides a context-manager and CLI-style check that uses an on-disk
    sentinel file created via os.open(..., O_CREAT | O_EXCL | O_WRONLY) to
    guarantee mutual exclusion at the syscall boundary.

Trigger:
    c31 fine_fit_sf2_guitar was SIGSTOP-killed (exit 147 = 128+19) at 163/180
    due to parallel VGGish memory contention with a concurrent bass
    fine-fit sweep. Serial-solo retry succeeded 180/180.

Sentinel path:
    data/v4/_run/fine_fit_serial_lock (relative to workspace root)

Payload (canonical JSON):
    {
      "pid": int,
      "driver": str,
      "cycle": int,
      "started_at": ISO-8601 UTC string, freshly stamped per acquire
                    (datetime.now(timezone.utc).isoformat()) — c55 fix
                    per _infra/op1-writer-full-fix-c55.
    }

    Rationale for wall-clock on started_at (c55): the sentinel is
    operational infrastructure whose purpose is to help operators
    identify stale/dead sentinels. A SOURCE_DATE_EPOCH-derived
    timestamp (c52/c53/c54 partial-fix chain) does not refresh on
    re-acquire and can carry stale wall-time from a prior release,
    defeating the diagnostic value of the field. Discipline preserved
    elsewhere: no PRNG; kernel-level O_CREAT|O_EXCL exclusion is
    unchanged; sentinel content is not a determinism-tracked artifact.

Discipline:
    - No PRNG.
    - started_at is wall-clock (see rationale above); no other field
      uses wall-clock time.
    - /usr/bin/python3 interpreter guard on any callable script; this
      module is import-only.
    - Failure mode: incumbent-owner refusal returns non-zero exit AND
      prints a clear operator-actionable error naming the incumbent
      (pid + driver + cycle + started_at + sentinel path).
"""

from __future__ import annotations

import errno
import json
import os
import pathlib
import sys
from datetime import datetime, timezone


# Workspace-root-relative sentinel path.
SENTINEL_REL = "data/v4/_run/fine_fit_serial_lock"


def _workspace_root() -> pathlib.Path:
    """Return the workspace root (parent of scripts/sound_match/)."""
    here = pathlib.Path(__file__).resolve()
    # scripts/sound_match/_serial_lock_op1.py -> workspace-root
    return here.parent.parent.parent


def _iso_epoch(seconds: int) -> str:
    """Return ISO-8601 UTC string for a Unix epoch (no wall clock)."""
    return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()


def sentinel_path() -> pathlib.Path:
    return _workspace_root() / SENTINEL_REL


class SerialLockRefusal(RuntimeError):
    """Raised when the sentinel is already present (another driver holds it)."""


class SerialLock:
    """Context manager enforcing OP-1 serial-launch lock.

    Usage inside a driver's main() (typical shape):

        with SerialLock(driver="fine_fit_sf2_v2", cycle=32):
            ... driver body ...

    On enter:
        - Creates sentinel via os.open(O_CREAT | O_EXCL | O_WRONLY).
        - On EEXIST, reads the existing sentinel payload and raises
          SerialLockRefusal with an operator-actionable message.

    On exit (finally):
        - Removes the sentinel (best-effort). Also handles the case
          where the sentinel was already removed by an external process.
    """

    def __init__(self, driver: str, cycle: int,
                 sentinel: pathlib.Path | None = None) -> None:
        self.driver = str(driver)
        self.cycle = int(cycle)
        self.sentinel = sentinel or sentinel_path()
        self._entered = False

    def _payload(self) -> bytes:
        # c55 fix (_infra/op1-writer-full-fix-c55): started_at is freshly
        # stamped per acquire using datetime.now(timezone.utc). Prior
        # c52/c53/c54 partial-fix chain used SOURCE_DATE_EPOCH, which
        # never refreshed across re-acquires and produced misleading
        # incumbent diagnostics. pid + cycle + driver already refresh
        # correctly (pid via os.getpid(); cycle + driver via constructor
        # args passed by the driver at each launch).
        payload = {
            "pid": os.getpid(),
            "driver": self.driver,
            "cycle": self.cycle,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "sentinel_path": str(self.sentinel),
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def acquire(self) -> None:
        self.sentinel.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(self.sentinel),
                         os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except OSError as e:
            if e.errno == errno.EEXIST:
                incumbent = self._read_incumbent()
                msg = (
                    "OP-1 SERIAL-LAUNCH LOCK REFUSAL: sentinel present at "
                    f"{self.sentinel}. Incumbent: {incumbent}. "
                    f"This driver ({self.driver}, cycle {self.cycle}) refuses "
                    "concurrent entry per docs/agent_picks_selection_invariants.md "
                    "operational invariant OP-1. If the incumbent process is dead, "
                    "manually remove the sentinel and re-launch."
                )
                raise SerialLockRefusal(msg) from None
            raise
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(self._payload())
        except Exception:
            # Best-effort cleanup on write failure.
            try:
                os.unlink(str(self.sentinel))
            except OSError:
                pass
            raise
        self._entered = True

    def release(self) -> None:
        if not self._entered:
            return
        try:
            os.unlink(str(self.sentinel))
        except FileNotFoundError:
            # External process removed it — non-fatal.
            pass
        self._entered = False

    def _read_incumbent(self) -> str:
        try:
            with open(self.sentinel, "rb") as f:
                data = f.read().decode(errors="replace")
            return data
        except OSError as e:
            return f"<unreadable: {e}>"

    # Context-manager protocol.
    def __enter__(self) -> "SerialLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()


def refuse_if_held(driver: str, cycle: int) -> int:
    """CLI-shape helper: check-and-refuse without acquiring.

    Returns 0 if free, non-zero and prints message if held.
    Intended for driver-entry probes that do not want to wrap main().
    """
    s = sentinel_path()
    if not s.exists():
        return 0
    try:
        with open(s, "rb") as f:
            incumbent = f.read().decode(errors="replace")
    except OSError as e:
        incumbent = f"<unreadable: {e}>"
    print(
        f"OP-1 SERIAL-LAUNCH LOCK REFUSAL: sentinel present at {s}. "
        f"Incumbent: {incumbent}. Driver {driver!r} (cycle {cycle}) refuses.",
        file=sys.stderr,
    )
    return 47  # arbitrary non-zero; distinct from typical exit codes
