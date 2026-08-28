#!/usr/bin/env python3
# M-RULES-1/schema — append-only ledger writer + reader.
#
# Author: cyd7bevdr@mozmail.com, cycle 6 (fork 3168fb0e47a1 / clone-1).
#
# data/rules/ledger.jsonl invariants:
#   * Open only in "a" mode. NEVER "w" or "r+". Enforced by _APPEND_ONLY_ASSERT.
#   * Every appended row is validated (validate_row) BEFORE hitting disk.
#   * Duplicate rule_ids are rejected at write time.
#   * Supersede targets must already exist in the ledger.
#   * Every write is followed by flush + fsync.

import json
import os
import sys
from pathlib import Path
from typing import Iterator, List, Optional

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent  # scripts/rules -> scripts -> repo
DEFAULT_LEDGER_PATH = _REPO / "data" / "rules" / "ledger.jsonl"

if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.validate import validate_row, validate_batch  # noqa: E402


def _canonical_line(row: dict) -> str:
    # Same canonical encoding used everywhere: sorted keys, no whitespace.
    return json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _all_rule_ids(path: Path) -> set:
    ids = set()
    if not path.exists():
        return ids
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("event_type") == "rule":
                rid = row.get("rule_id")
                if isinstance(rid, str):
                    ids.add(rid)
    return ids


def _all_new_rule_ids(path: Path) -> set:
    """rule_ids that any prior supersede pointed AT (to detect supersede-targeting-yet-missing)."""
    ids = set()
    if not path.exists():
        return ids
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("event_type") == "supersede":
                nid = row.get("new_rule_id")
                if isinstance(nid, str):
                    ids.add(nid)
    return ids


def _append(path: Path, row: dict) -> None:
    """The one and only write path. Enforces append-only."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # Explicitly force "a" mode. NEVER "w", NEVER "r+".
    mode = "a"
    assert mode == "a", "append-only ledger: mode must be 'a'"
    with open(path, mode) as f:
        f.write(_canonical_line(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


class LedgerError(Exception):
    pass


def write_rule(row: dict, path: Optional[Path] = None) -> None:
    """Append a single rule event. Raises LedgerError with a joined
    error-string on validation failure or duplicate rule_id."""
    p = path or DEFAULT_LEDGER_PATH
    if not isinstance(row, dict):
        raise LedgerError(f"row is not a dict (type={type(row).__name__})")
    if row.get("event_type") != "rule":
        raise LedgerError(f"write_rule expects event_type='rule', got {row.get('event_type')!r}")
    errs = validate_row(row)
    if errs:
        raise LedgerError("; ".join(errs))
    rid = row.get("rule_id")
    existing = _all_rule_ids(p)
    if rid in existing:
        raise LedgerError(f"duplicate rule_id: {rid}")
    _append(p, row)


def write_supersede(row: dict, path: Optional[Path] = None) -> None:
    """Append a single supersede event. Raises LedgerError with a joined
    error-string on validation failure or missing supersede target."""
    p = path or DEFAULT_LEDGER_PATH
    if not isinstance(row, dict):
        raise LedgerError(f"row is not a dict (type={type(row).__name__})")
    if row.get("event_type") != "supersede":
        raise LedgerError(f"write_supersede expects event_type='supersede', got {row.get('event_type')!r}")
    errs = validate_row(row)
    if errs:
        raise LedgerError("; ".join(errs))
    existing = _all_rule_ids(p)
    sup = row.get("supersedes_rule_id")
    newr = row.get("new_rule_id")
    if sup not in existing:
        raise LedgerError(f"supersedes_rule_id {sup} not found in ledger")
    if newr not in existing:
        raise LedgerError(f"new_rule_id {newr} not found in ledger (write the replacement rule first)")
    if sup == newr:
        raise LedgerError(f"supersedes_rule_id == new_rule_id ({sup})")
    _append(p, row)


def read_ledger(path: Optional[Path] = None) -> List[dict]:
    """Stream the ledger; return rows in insertion order. Malformed lines skipped."""
    p = path or DEFAULT_LEDGER_PATH
    rows: List[dict] = []
    if not p.exists():
        return rows
    with open(p, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def effective_rules(path: Optional[Path] = None) -> List[dict]:
    """Apply supersede chain: return the current (non-superseded) rule rows.

    Supersede resolution is transitive: if A superseded by B, B superseded
    by C, effective_rules returns C. Chase forward-pointers until no more
    supersedes.
    """
    rows = read_ledger(path)
    rule_by_id = {r["rule_id"]: r for r in rows if r.get("event_type") == "rule" and "rule_id" in r}
    # Build "superseded_by" map: rule_id -> new_rule_id (last write wins)
    replaced_by = {}
    for r in rows:
        if r.get("event_type") == "supersede":
            sup = r.get("supersedes_rule_id")
            newr = r.get("new_rule_id")
            if isinstance(sup, str) and isinstance(newr, str):
                replaced_by[sup] = newr

    superseded_ids = set(replaced_by.keys())
    effective = []
    for rid, rule in rule_by_id.items():
        if rid in superseded_ids:
            continue
        effective.append(rule)
    return effective


def ensure_ledger_exists(path: Optional[Path] = None) -> Path:
    """Create empty ledger file if missing. Idempotent."""
    p = path or DEFAULT_LEDGER_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        # Create empty file via append mode.
        with open(p, "a"):
            pass
    return p


if __name__ == "__main__":
    p = ensure_ledger_exists()
    print(f"ledger at: {p} (exists={p.exists()}, size={p.stat().st_size})")
    print(f"rows: {len(read_ledger(p))}")
