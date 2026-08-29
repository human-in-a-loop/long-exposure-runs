#!/usr/bin/env python3
"""M-DAW-SPIKE-1/palette-assignment-schema — two-layer validator.

Author: cyd7bevdr@mozmail.com, cycle 31 (fork cfc5009aca96 / clone-1, Branch B).

Layer 1: jsonschema.Draft202012Validator against palette_v1.json.
Layer 2 (hand-written, cross-row):
  * assignment_id matches compute_assignment_id(row) (hash consistency).
  * provenance_pointers non-empty; every element resolves against the
    union of data/rules/ledger.jsonl + data/rules/ledger_i3_dminor.jsonl.
  * pinned_state.external_state_sha_optional matches ^[0-9a-f]{64}$
    (Layer 1 already checks, but Layer 2 re-checks defensively).
  * Stem × instrument combo not in the skip list (Dexed × drums rejected).
  * (validate_batch) duplicate assignment_id across rows.

Contract mirrors cycle-6 M-RULES-1/validate.py exactly:
  * Every function returns list[str] of error messages. Empty = success.
  * NEVER raises on validation failure. NEVER partial-crashes.
  * Every field access .get()-guarded.
  * Non-factor isolation: MUST NOT import scripts.classifier.sidecar_nonfactor.
"""

import json
import re
import sys
from pathlib import Path
from typing import Iterable, List

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

from jsonschema import Draft202012Validator  # noqa: E402

_HERE = Path(__file__).resolve().parent
SCHEMA_PATH = _HERE / "schema" / "palette_v1.json"

# Skip list — stem/instrument combos that are physically implausible.
# Rationale documented in docs/palette_assignment_schema_rubric.md §4.
SKIP_COMBOS = frozenset({
    ("drums", "dexed"),
})

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    with open(path, "r") as f:
        return json.load(f)


_validator = Draft202012Validator(load_schema())


def _layer1_errors(row: dict) -> List[str]:
    """Mechanical JSON Schema validation. Returns list of error strings."""
    errors = []
    for e in _validator.iter_errors(row):
        path = "/".join(str(p) for p in e.absolute_path) or "<root>"
        errors.append(f"schema:{path}:{e.message}")
    return errors


def _layer2_row_errors(row: dict, known_ids: set = None) -> List[str]:
    """Semantic checks on a single row. Every access .get()-guarded.

    Args:
      row: candidate assignment dict.
      known_ids: pre-loaded set of resolvable rule_id strings. If None,
        computed lazily via provenance.known_rule_ids().
    """
    from scripts.palette.provenance import compute_assignment_id, known_rule_ids

    errors: List[str] = []
    if not isinstance(row, dict):
        return [f"row is not a dict (type={type(row).__name__})"]

    # (1) assignment_id hash consistency.
    aid_declared = row.get("assignment_id")
    if isinstance(aid_declared, str) and re.match(r"^[0-9a-f]{32}$", aid_declared):
        try:
            aid_computed = compute_assignment_id(row)
            if aid_computed != aid_declared:
                errors.append(
                    f"assignment_id mismatch: declared={aid_declared}, "
                    f"computed_from_canonical_json={aid_computed}"
                )
        except Exception as e:
            errors.append(f"assignment_id: could not recompute ({type(e).__name__}: {e})")

    # (2) stem / instrument skip-list check.
    stem = row.get("stem")
    instrument = row.get("instrument")
    if isinstance(stem, str) and isinstance(instrument, str):
        if (stem, instrument) in SKIP_COMBOS:
            errors.append(
                f"stem={stem} × instrument={instrument} is in skip list "
                f"(implausible combo; see docs/palette_assignment_schema_rubric.md §4)"
            )

    # (3) provenance_pointers resolvability.
    pointers = row.get("provenance_pointers") or []
    if isinstance(pointers, list):
        if len(pointers) == 0:
            errors.append("provenance_pointers must be non-empty")
        else:
            if known_ids is None:
                known_ids = known_rule_ids()
            for i, ptr in enumerate(pointers):
                if not isinstance(ptr, str) or not ptr:
                    errors.append(f"provenance_pointers[{i}] must be a non-empty string")
                elif ptr not in known_ids:
                    errors.append(
                        f"provenance_pointers[{i}] unresolvable: rule_id={ptr} "
                        f"not found in data/rules/ledger.jsonl or "
                        f"data/rules/ledger_i3_dminor.jsonl"
                    )

    # (4) pinned_state.external_state_sha_optional pattern (defensive).
    ps = row.get("pinned_state") or {}
    if isinstance(ps, dict):
        sha_opt = ps.get("external_state_sha_optional")
        if sha_opt is not None:
            if not isinstance(sha_opt, str) or not _SHA256_RE.match(sha_opt):
                errors.append(
                    f"pinned_state.external_state_sha_optional must match "
                    f"^[0-9a-f]{{64}}$ (got {sha_opt!r})"
                )

    return errors


def validate_row(row: dict, known_ids: set = None) -> List[str]:
    """Full per-row validation (Layer 1 + Layer 2). Returns list of errors.
    Never raises."""
    if not isinstance(row, dict):
        return [f"row is not a dict (type={type(row).__name__})"]
    errors = _layer1_errors(row)
    errors.extend(_layer2_row_errors(row, known_ids=known_ids))
    return errors


def validate_batch(rows: Iterable[dict]) -> List[str]:
    """Validate a sequence of rows in order. Adds:
      * duplicate assignment_id across rows.
    """
    from scripts.palette.provenance import known_rule_ids

    errors: List[str] = []
    seen_aids: dict = {}
    known_ids = known_rule_ids()

    for i, row in enumerate(rows):
        prefix = f"row[{i}]"
        row_errors = validate_row(row, known_ids=known_ids)
        for e in row_errors:
            errors.append(f"{prefix} {e}")

        aid = (row or {}).get("assignment_id") if isinstance(row, dict) else None
        if isinstance(aid, str):
            if aid in seen_aids:
                errors.append(
                    f"{prefix} duplicate_assignment_id: {aid} "
                    f"first-seen at row[{seen_aids[aid]}]"
                )
            else:
                seen_aids[aid] = i

    return errors


if __name__ == "__main__":
    assert isinstance(_validator, Draft202012Validator)
    print("schema loaded:", SCHEMA_PATH)
    print("layer1 errors on {}:", _layer1_errors({}))
