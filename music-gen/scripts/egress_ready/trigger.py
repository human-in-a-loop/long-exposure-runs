"""Trigger detector for egress-ready automation.

Consumes rows from data/ingestion/egress_status.jsonl (or a synthetic
fixture) and decides whether the two-consecutive-fresh-true rule is met.

created: 2026-08-28
cycle: 8
milestone: M-INGEST-1/egress-ready-automation
"""
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", (
    f"scripts/egress_ready expects /usr/bin/python3, got {sys.executable}"
)

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


DEFAULT_STALENESS_HOURS = 24


class TriggerKind(Enum):
    NONE = "NONE"           # zero fresh trues, or last row broke the streak
    ARMED = "ARMED"         # exactly one fresh true at the end
    TRIGGERED = "TRIGGERED" # two consecutive fresh trues at the end


@dataclass(frozen=True)
class TriggerDecision:
    kind: TriggerKind
    # For ARMED: idx of the single true row (in the ORIGINAL rows list).
    # For TRIGGERED: (i0, i1) of the two consecutive trues.
    # For NONE: empty tuple.
    indices: tuple = ()
    # Human-legible reason for logging.
    reason: str = ""


def _parse_ts(ts: str) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp; return None if unparsable."""
    if not isinstance(ts, str):
        return None
    # Accept trailing Z (Zulu) as UTC.
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _is_fresh(row: Dict[str, Any], now_utc: datetime, staleness_hours: int) -> bool:
    """A row is fresh iff (now_utc - row.ts) < staleness_hours.

    Strict '<' comparison: a row at exactly staleness_hours is stale.
    Rows with missing/unparsable ts are treated as stale (safest default).
    """
    ts = _parse_ts(row.get("ts", ""))
    if ts is None:
        return False
    return (now_utc - ts) < timedelta(hours=staleness_hours)


def detect_trigger(
    rows: List[Dict[str, Any]],
    now_utc: datetime,
    staleness_hours: int = DEFAULT_STALENESS_HOURS,
) -> TriggerDecision:
    """Scan rows in chronological order and report the current streak state.

    Rules:
      - Rows older than staleness_hours from now_utc are IGNORED entirely
        (they do not count as true or false).
      - Two consecutive fresh rows with media_ok=true, with no fresh false
        between them, cause TRIGGERED.
      - Exactly one fresh true at the tail, with no following false, is ARMED.
      - Any fresh false at the tail (or no fresh trues at all) is NONE.
      - Only the LAST STREAK matters: [T, F, T, T] -> TRIGGERED(2,3);
        [T, T, F] -> NONE.
    """
    if not isinstance(rows, list):
        return TriggerDecision(TriggerKind.NONE, (), "rows is not a list")

    # Build filtered stream of (orig_idx, media_ok_bool) for FRESH rows only.
    fresh: List[tuple] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        if not _is_fresh(row, now_utc, staleness_hours):
            continue
        fresh.append((i, bool(row.get("media_ok", False))))

    if not fresh:
        return TriggerDecision(TriggerKind.NONE, (), "no fresh rows in staleness window")

    # Walk fresh rows and track streak of consecutive trues ending at the last.
    # If the last fresh row is False -> NONE.
    last_orig_idx, last_ok = fresh[-1]
    if not last_ok:
        return TriggerDecision(TriggerKind.NONE, (), "trailing fresh row is media_ok=false")

    # Last is True. Check second-to-last.
    if len(fresh) >= 2:
        prev_orig_idx, prev_ok = fresh[-2]
        if prev_ok:
            return TriggerDecision(
                TriggerKind.TRIGGERED,
                (prev_orig_idx, last_orig_idx),
                "two consecutive fresh media_ok=true rows",
            )
    return TriggerDecision(
        TriggerKind.ARMED,
        (last_orig_idx,),
        "exactly one fresh media_ok=true at tail",
    )


def load_jsonl(path) -> List[Dict[str, Any]]:
    """Load a JSONL file into a list of dict rows. Robust to blank lines."""
    import json
    from pathlib import Path
    p = Path(path)
    if not p.is_file():
        return []
    out: List[Dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            out.append(row)
    return out
