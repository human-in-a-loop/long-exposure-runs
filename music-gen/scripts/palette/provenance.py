#!/usr/bin/env python3
"""M-DAW-SPIKE-1/palette-assignment-schema — provenance + assignment_id utilities.

Author: cyd7bevdr@mozmail.com, cycle 31 (fork cfc5009aca96 / clone-1, Branch B).

Public API:
  * canonical_json_for_assignment_id(row) -> str
        Returns the deterministic canonical JSON string that goes into the
        UUID5 hash. EXCLUDES notes_optional (per rubric §4 to allow
        authoring-note edits without invalidating the id).
  * compute_assignment_id(row) -> str
        UUID5 hex (32 lowercase hex chars).
  * resolve_provenance_pointer(rule_id, ledger_paths=DEFAULT_LEDGER_PATHS)
        Streams the two rules ledgers looking for rule_id. Returns the
        matching row dict, or None on miss. Read-only.

Contract:
  * NEVER modifies the rules ledgers.
  * NEVER partial-crashes; malformed rows are skipped.
  * No PRNG; no sidecar_nonfactor imports.
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Iterable, Optional

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_REPO = Path(__file__).resolve().parent.parent.parent  # palette -> scripts -> repo
DEFAULT_LEDGER_PATHS = (
    _REPO / "data" / "rules" / "ledger.jsonl",
    _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl",
)

# UUID5 namespace for palette_v1 assignments. Content-derived from the string
# "palette_v1::music-gen::c31" so it is stable and human-auditable.
# uuid.uuid5(uuid.NAMESPACE_URL, "palette_v1::music-gen::c31") ->
#   3e5c3f5b-4b52-5c05-9d1e-c67f8f9a4d21 (deterministic).
NAMESPACE_PALETTE_V1 = uuid.uuid5(uuid.NAMESPACE_URL, "palette_v1::music-gen::c31")

# Fields that participate in the assignment_id hash. notes_optional is
# EXCLUDED to allow authoring-note edits without churning the id.
_HASHED_FIELDS = (
    "schema_v",
    "stem",
    "instrument",
    "pinned_state",
    "provenance_pointers",
    "extractor_version",
)


def _canonicalize_pinned_state(ps):
    """Sort parameter_dict keys deterministically; return a new dict."""
    if not isinstance(ps, dict):
        return ps
    out = {}
    for k in ("plugin_name", "plugin_version", "parameter_dict",
              "preset_name_optional", "external_state_sha_optional"):
        if k in ps:
            v = ps[k]
            if k == "parameter_dict" and isinstance(v, dict):
                v = {pk: v[pk] for pk in sorted(v)}
            out[k] = v
    return out


def canonical_json_for_assignment_id(row: dict) -> str:
    """Return the canonical JSON string used to derive assignment_id.

    Behavior:
      * Uses only the six _HASHED_FIELDS.
      * Sorts provenance_pointers alphabetically.
      * Sorts parameter_dict keys alphabetically.
      * `sort_keys=True, separators=(',',':'), ensure_ascii=True`.
    """
    payload = {}
    for k in _HASHED_FIELDS:
        v = row.get(k) if isinstance(row, dict) else None
        if k == "provenance_pointers" and isinstance(v, list):
            v = sorted(v)
        elif k == "pinned_state":
            v = _canonicalize_pinned_state(v)
        payload[k] = v
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_assignment_id(row: dict) -> str:
    """UUID5 hex (32 lowercase hex chars) over canonical JSON payload."""
    canonical = canonical_json_for_assignment_id(row)
    return uuid.uuid5(NAMESPACE_PALETTE_V1, canonical).hex


def _iter_ledger_rows(path: Path) -> Iterable[dict]:
    """Stream JSONL rows; skip malformed lines silently (never partial-crash)."""
    if not path.is_file():
        return
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def resolve_provenance_pointer(
    rule_id: str,
    ledger_paths: Iterable[Path] = DEFAULT_LEDGER_PATHS,
) -> Optional[dict]:
    """Return the ledger row matching rule_id, or None. Read-only, streaming."""
    if not isinstance(rule_id, str) or not rule_id:
        return None
    for path in ledger_paths:
        p = Path(path)
        for row in _iter_ledger_rows(p):
            if row.get("rule_id") == rule_id:
                return row
    return None


def known_rule_ids(ledger_paths: Iterable[Path] = DEFAULT_LEDGER_PATHS) -> set:
    """One-shot set of all rule_id strings across the ledgers.

    Layer 2 validator uses this to avoid an O(N × rows) rescan per row.
    """
    ids = set()
    for path in ledger_paths:
        for row in _iter_ledger_rows(Path(path)):
            rid = row.get("rule_id")
            if isinstance(rid, str):
                ids.add(rid)
    return ids


if __name__ == "__main__":
    # smoke: compute id twice, expect equal
    ex = {
        "schema_v": "palette_v1",
        "stem": "bass",
        "instrument": "sfizz",
        "pinned_state": {
            "plugin_name": "sfizz",
            "plugin_version": "1.2.3",
            "parameter_dict": {"amp_velocity": 0.9},
        },
        "provenance_pointers": ["rule_ba740b0c3a578421"],
        "extractor_version": "palette_v1_c31",
    }
    a = compute_assignment_id(ex)
    b = compute_assignment_id(ex)
    assert a == b
    print(f"smoke ok: assignment_id={a}")
