"""Egress-ready state machine.

Watches egress_status.jsonl and, on two consecutive fresh media_ok=true rows,
drives the rated-audio pipeline (harvest -> chunker -> classifier -> ready-flag).

State is persisted to data/egress_ready/state.json on every transition via
tempfile + os.replace (POSIX-atomic). transitions.jsonl is append-only.

Legal transitions:
  IDLE        -> ARMED, TRIGGERED (manual)
  ARMED       -> IDLE, TRIGGERED, FAILED
  TRIGGERED   -> HARVESTING, FAILED, IDLE (manual)
  HARVESTING  -> CHUNKING, FAILED
  CHUNKING    -> CLASSIFYING, FAILED
  CLASSIFYING -> READY, FAILED
  READY       -> IDLE (manual reset)
  FAILED      -> HARVESTING, CHUNKING, CLASSIFYING (--resume), IDLE (--reset-failure + --force-idle)

created: 2026-08-28
cycle: 8
milestone: M-INGEST-1/egress-ready-automation
"""
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", (
    f"scripts/egress_ready expects /usr/bin/python3, got {sys.executable}"
)

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set

from scripts.egress_ready.trigger import (
    TriggerDecision,
    TriggerKind,
    detect_trigger,
    load_jsonl,
)
from scripts.egress_ready.subprocess_hooks import HookResult, SubprocessHooks


class State(Enum):
    IDLE = "IDLE"
    ARMED = "ARMED"
    TRIGGERED = "TRIGGERED"
    HARVESTING = "HARVESTING"
    CHUNKING = "CHUNKING"
    CLASSIFYING = "CLASSIFYING"
    READY = "READY"
    FAILED = "FAILED"


# The single authoritative transition map. Any transition not in this map is
# rejected as an InvalidTransition. Manual overrides go through this map too --
# there are no back doors.
TRANSITIONS: Dict[State, Set[State]] = {
    State.IDLE:        {State.ARMED, State.TRIGGERED},
    State.ARMED:       {State.IDLE, State.TRIGGERED, State.FAILED},
    State.TRIGGERED:   {State.HARVESTING, State.FAILED, State.IDLE},
    State.HARVESTING:  {State.CHUNKING, State.FAILED},
    State.CHUNKING:    {State.CLASSIFYING, State.FAILED},
    State.CLASSIFYING: {State.READY, State.FAILED},
    State.READY:       {State.IDLE},
    State.FAILED:      {State.HARVESTING, State.CHUNKING, State.CLASSIFYING, State.IDLE},
}


class InvalidTransition(Exception):
    pass


@dataclass
class Clock:
    """Injectable clock for byte-determinism in tests."""
    now: Callable[[], datetime]

    @staticmethod
    def system() -> "Clock":
        return Clock(now=lambda: datetime.now(timezone.utc))


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _atomic_write_text(path: Path, text: str) -> None:
    """tempfile + os.replace on the same directory: POSIX-atomic rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(text)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name
    os.replace(tmp_path, str(path))


@dataclass
class Persisted:
    state: State
    last_transition_utc: str
    evidence: Dict[str, Any]
    diagnostic_path: Optional[str]
    # Which stage was in-flight when we last FAILED (drives --resume).
    failed_stage: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "last_transition_utc": self.last_transition_utc,
            "evidence": self.evidence,
            "diagnostic_path": self.diagnostic_path,
            "failed_stage": self.failed_stage,
        }

    @staticmethod
    def initial() -> "Persisted":
        return Persisted(State.IDLE, "", {}, None, None)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Persisted":
        return Persisted(
            state=State(d["state"]),
            last_transition_utc=d.get("last_transition_utc", ""),
            evidence=d.get("evidence", {}) or {},
            diagnostic_path=d.get("diagnostic_path"),
            failed_stage=d.get("failed_stage"),
        )


class EgressReadyMachine:
    def __init__(
        self,
        state_path: Path,
        transitions_path: Path,
        egress_status_path: Path,
        hooks: Optional[SubprocessHooks] = None,
        clock: Optional[Clock] = None,
        diagnostic_dir: Optional[Path] = None,
        staleness_hours: int = 24,
    ):
        self.state_path = Path(state_path)
        self.transitions_path = Path(transitions_path)
        self.egress_status_path = Path(egress_status_path)
        self.hooks = hooks if hooks is not None else SubprocessHooks()
        self.clock = clock if clock is not None else Clock.system()
        self.diagnostic_dir = Path(diagnostic_dir) if diagnostic_dir else self.state_path.parent
        self.staleness_hours = staleness_hours

        if self.state_path.is_file():
            try:
                d = json.loads(self.state_path.read_text(encoding="utf-8"))
                self.persisted = Persisted.from_dict(d)
            except (json.JSONDecodeError, KeyError, ValueError):
                self.persisted = Persisted.initial()
        else:
            self.persisted = Persisted.initial()

    # ---------- persistence ----------

    def _persist(self) -> None:
        _atomic_write_text(
            self.state_path,
            json.dumps(self.persisted.to_dict(), indent=2, sort_keys=True) + "\n",
        )

    def _audit(self, from_state: State, to_state: State, reason: str, evidence_ref: Any) -> None:
        self.transitions_path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp_utc": _iso(self.clock.now()),
            "from_state": from_state.value,
            "to_state": to_state.value,
            "reason": reason,
            "evidence_ref": evidence_ref,
        }
        with open(self.transitions_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")

    # ---------- transition primitive ----------

    def _transition(
        self,
        to_state: State,
        reason: str,
        evidence_ref: Any = None,
        diagnostic_path: Optional[str] = None,
        failed_stage: Optional[str] = None,
    ) -> None:
        cur = self.persisted.state
        if to_state not in TRANSITIONS.get(cur, set()):
            raise InvalidTransition(
                f"illegal transition {cur.value} -> {to_state.value} (reason={reason!r})"
            )
        self._audit(cur, to_state, reason, evidence_ref)

        # diagnostic_path lifetime: written on FAILED, cleared on IDLE/READY,
        # carried forward otherwise (so --resume still sees it).
        if to_state == State.FAILED:
            new_diag = diagnostic_path
            new_fs = failed_stage
        elif to_state in {State.IDLE, State.READY}:
            new_diag = None
            new_fs = None
        else:
            new_diag = self.persisted.diagnostic_path
            new_fs = self.persisted.failed_stage

        self.persisted = Persisted(
            state=to_state,
            last_transition_utc=_iso(self.clock.now()),
            evidence={"reason": reason, "ref": evidence_ref},
            diagnostic_path=new_diag,
            failed_stage=new_fs,
        )
        self._persist()

    # ---------- FAILED helper ----------

    def _fail(self, from_stage: State, hook_name: str, result: HookResult) -> None:
        ts = self.clock.now().strftime("%Y%m%d_%H%M%S")
        diag = self.diagnostic_dir / f"diagnostic_{ts}.json"
        diag.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "failed_at_stage": from_stage.value,
            "hook": hook_name,
            "returncode": result.returncode,
            "stderr_tail": result.stderr_tail,
            "duration_s": result.duration_s,
            "timestamp_utc": _iso(self.clock.now()),
        }
        diag.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self._transition(
            State.FAILED,
            f"hook {hook_name} returned ok=False",
            evidence_ref=str(diag),
            diagnostic_path=str(diag),
            failed_stage=from_stage.value,
        )

    # ---------- scan / drive ----------

    def scan_and_advance(self) -> State:
        """One-shot: read egress_status.jsonl, apply trigger rule, drive chain."""
        rows = load_jsonl(self.egress_status_path)
        decision = detect_trigger(rows, self.clock.now(), self.staleness_hours)
        cur = self.persisted.state

        # Idempotence: once past TRIGGERED, subsequent scans do NOT retract.
        # State is authoritative; the trigger scan only matters IDLE/ARMED.
        if cur in {State.TRIGGERED, State.HARVESTING, State.CHUNKING,
                   State.CLASSIFYING, State.READY, State.FAILED}:
            self._drive_chain()
            return self.persisted.state

        # cur is IDLE or ARMED: reconcile with decision.
        if decision.kind == TriggerKind.NONE:
            if cur == State.ARMED:
                self._transition(State.IDLE, decision.reason or "streak broken",
                                 evidence_ref=list(decision.indices))
            return self.persisted.state

        if decision.kind == TriggerKind.ARMED:
            if cur == State.IDLE:
                self._transition(State.ARMED, decision.reason,
                                 evidence_ref=list(decision.indices))
            return self.persisted.state

        # TRIGGERED. Legal from both IDLE and ARMED.
        self._transition(State.TRIGGERED, decision.reason,
                         evidence_ref=list(decision.indices))
        self._drive_chain()
        return self.persisted.state

    def _drive_chain(self) -> None:
        """Advance TRIGGERED -> HARVESTING -> CHUNKING -> CLASSIFYING -> READY.

        Structured so that entering a stage (transition first, then run hook)
        and resuming a stage (hook first, then transition) both terminate on
        stage-hook failure with a FAILED landing and the failing stage recorded.
        """
        while True:
            cur = self.persisted.state
            if cur == State.TRIGGERED:
                self._transition(State.HARVESTING, "chain: start harvest")
                continue

            if cur == State.HARVESTING:
                res = self.hooks.run_harvest()
                if not res.ok:
                    self._fail(State.HARVESTING, "run_harvest", res)
                    return
                self._transition(State.CHUNKING, "chain: harvest ok -> chunk")
                continue

            if cur == State.CHUNKING:
                res = self.hooks.run_chunker()
                if not res.ok:
                    self._fail(State.CHUNKING, "run_chunker", res)
                    return
                self._transition(State.CLASSIFYING, "chain: chunk ok -> classify")
                continue

            if cur == State.CLASSIFYING:
                r1 = self.hooks.run_classifier()
                if not r1.ok:
                    self._fail(State.CLASSIFYING, "run_classifier", r1)
                    return
                r2 = self.hooks.write_ready_flag()
                if not r2.ok:
                    self._fail(State.CLASSIFYING, "write_ready_flag", r2)
                    return
                self._transition(State.READY, "chain: classify ok, ready flag written")
                return

            # READY, FAILED, IDLE, ARMED: nothing more for the chain to do.
            return


# ---------- human-override API (invoked from cli.py or tests) ----------

def force_idle(machine: EgressReadyMachine, reason: str = "human_override") -> State:
    """Force IDLE from any state EXCEPT an in-flight subprocess stage."""
    cur = machine.persisted.state
    if cur == State.IDLE:
        return cur
    if cur in {State.HARVESTING, State.CHUNKING, State.CLASSIFYING}:
        raise InvalidTransition(
            f"cannot force IDLE from in-flight stage {cur.value}; kill process first"
        )
    machine._transition(State.IDLE, f"human_override: {reason}")
    return machine.persisted.state


def force_trigger(machine: EgressReadyMachine, reason: str = "human_override") -> State:
    """Force TRIGGERED from IDLE/ARMED. Drives the chain immediately."""
    cur = machine.persisted.state
    if cur not in {State.IDLE, State.ARMED}:
        raise InvalidTransition(
            f"force_trigger only from IDLE or ARMED (was {cur.value})"
        )
    machine._transition(State.TRIGGERED, f"human_override: {reason}")
    machine._drive_chain()
    return machine.persisted.state


def resume(machine: EgressReadyMachine) -> State:
    """From FAILED, restart the failing stage."""
    cur = machine.persisted.state
    if cur != State.FAILED:
        raise InvalidTransition(f"resume only from FAILED (was {cur.value})")
    fs = machine.persisted.failed_stage
    if fs not in {State.HARVESTING.value, State.CHUNKING.value, State.CLASSIFYING.value}:
        raise InvalidTransition(f"cannot resume: unknown failed_stage {fs!r}")
    machine._transition(State(fs), f"resume: restarting failing stage {fs}")
    machine._drive_chain()
    return machine.persisted.state


def reset_failure(machine: EgressReadyMachine, force_idle_ack: bool) -> State:
    """FAILED -> IDLE, only if --force-idle was also passed."""
    cur = machine.persisted.state
    if cur != State.FAILED:
        raise InvalidTransition(f"reset_failure only from FAILED (was {cur.value})")
    if not force_idle_ack:
        raise InvalidTransition(
            "reset_failure requires --force-idle to acknowledge; refusing"
        )
    machine._transition(State.IDLE, "human_override: reset_failure + force_idle")
    return machine.persisted.state
