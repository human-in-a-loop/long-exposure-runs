#!/usr/bin/env python3
# M-RULES-1/schema — two-layer validator.
#
# Author: cyd7bevdr@mozmail.com, cycle 6 (fork 3168fb0e47a1 / clone-1).
#
# Layer 1 (mechanical): jsonschema.Draft202012Validator against
#   scripts/rules/schema/rules_v1.json.
# Layer 2 (semantic, cross-row, hand-written): checks JSON Schema can't
#   express portably — PCH sum-to-1, scope end_s>start_s, form section
#   end_measure>start_measure, duplicate rule_id detection, supersede-target
#   existence.
#
# Contract:
#   * Every function returns a list of error strings (empty on success).
#   * NEVER raises on validation failure. NEVER partial-crashes.
#   * Every field access uses .get() with an explicit default —
#     inheriting the lesson from M-INGEST-1 provenance MODERATE-2.
#
# Non-factor isolation: this module MUST NOT import
# scripts.classifier.sidecar_nonfactor.

import json
import math
import os
import sys
from pathlib import Path
from typing import Iterable, List

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

from jsonschema import Draft202012Validator  # noqa: E402

_HERE = Path(__file__).resolve().parent
SCHEMA_PATH = _HERE / "schema" / "rules_v1.json"
_PCH_TOL = 1e-6


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    with open(path, "r") as f:
        return json.load(f)


_validator = Draft202012Validator(load_schema())


def _layer1_errors(row: dict) -> List[str]:
    """Mechanical JSON Schema validation. Returns list of error strings."""
    errors = []
    for e in _validator.iter_errors(row):
        # Include JSON-path so cross-row layer can key off it if needed.
        path = "/".join(str(p) for p in e.absolute_path) or "<root>"
        errors.append(f"schema:{path}:{e.message}")
    return errors


def _layer2_row_errors(row: dict) -> List[str]:
    """Semantic checks on a single row: scope, PCH sum, form section order.
    Every access .get()-guarded."""
    errors: List[str] = []
    event_type = row.get("event_type")
    if event_type != "rule":
        return errors  # supersede rows have no per-row semantic beyond schema

    scope = row.get("scope") or {}
    level = scope.get("level")
    start_s = scope.get("start_s")
    end_s = scope.get("end_s")
    if isinstance(start_s, (int, float)) and isinstance(end_s, (int, float)):
        if level in ("song", "section"):
            if not (end_s > start_s):
                errors.append(
                    f"scope.end_s ({end_s}) must be > scope.start_s ({start_s}) for level={level}"
                )
        elif level == "measure":
            if not (end_s >= start_s):
                errors.append(
                    f"scope.end_s ({end_s}) must be >= scope.start_s ({start_s}) for level=measure"
                )

    rule_type = row.get("rule_type")
    parameters = row.get("parameters") or {}

    if rule_type == "melodic":
        pch = parameters.get("pitch_class_histogram")
        if isinstance(pch, list) and len(pch) == 12 and all(isinstance(x, (int, float)) for x in pch):
            s = sum(pch)
            if not math.isclose(s, 1.0, abs_tol=_PCH_TOL):
                errors.append(f"pitch_class_histogram sum != 1 (got {s:.10f}, tol {_PCH_TOL})")

    if rule_type == "form":
        sections = parameters.get("sections") or []
        for i, sect in enumerate(sections):
            if not isinstance(sect, dict):
                continue
            sm = sect.get("start_measure")
            em = sect.get("end_measure")
            if isinstance(sm, int) and isinstance(em, int) and not (em > sm):
                errors.append(
                    f"sections[{i}].end_measure ({em}) must be > start_measure ({sm})"
                )

    if rule_type == "arrangement":
        # non-schema soft-check: layer_events t_s should lie within scope
        events = parameters.get("layer_events") or []
        for i, ev in enumerate(events):
            if not isinstance(ev, dict):
                continue
            t_s = ev.get("t_s")
            if isinstance(t_s, (int, float)) and isinstance(end_s, (int, float)):
                if t_s > end_s + 1e-6:
                    errors.append(
                        f"layer_events[{i}].t_s ({t_s}) exceeds scope.end_s ({end_s})"
                    )

    return errors


def validate_row(row: dict) -> List[str]:
    """Full per-row validation (Layer 1 + Layer 2). Returns list of errors.
    Never raises."""
    if not isinstance(row, dict):
        return [f"row is not a dict (type={type(row).__name__})"]
    errors = _layer1_errors(row)
    # Layer 2 depends on typed fields present; still run so we surface everything.
    errors.extend(_layer2_row_errors(row))
    return errors


def validate_batch(rows: Iterable[dict]) -> List[str]:
    """Validate a sequence of rows in order. Includes cross-row checks:
    duplicate rule_id, supersede-target existence.

    Cross-row semantics:
      * A rule row's rule_id must be unique across all prior rows.
      * A supersede row's supersedes_rule_id must reference a rule row that
        appears earlier in the batch.
      * A supersede row's new_rule_id must reference a rule row that appears
        earlier-or-same-position in the batch. (In practice, extractors write
        the replacement rule first, then the supersede event.)
    """
    errors: List[str] = []
    seen_rule_ids: set = set()
    rule_ids_by_position: list = []

    for i, row in enumerate(rows):
        prefix = f"row[{i}]"
        row_errors = validate_row(row)
        for e in row_errors:
            errors.append(f"{prefix} {e}")

        # Even if row has schema errors, try to advance cross-row bookkeeping
        # using .get() so we don't miss dup detection just because another
        # field is malformed.
        event_type = (row or {}).get("event_type") if isinstance(row, dict) else None
        if event_type == "rule":
            rid = (row or {}).get("rule_id")
            if isinstance(rid, str):
                if rid in seen_rule_ids:
                    errors.append(f"{prefix} duplicate rule_id: {rid}")
                else:
                    seen_rule_ids.add(rid)
                    rule_ids_by_position.append(rid)
        elif event_type == "supersede":
            sup = (row or {}).get("supersedes_rule_id")
            newr = (row or {}).get("new_rule_id")
            if isinstance(sup, str) and sup not in seen_rule_ids:
                errors.append(
                    f"{prefix} supersedes_rule_id {sup} not found in earlier rule rows"
                )
            if isinstance(newr, str) and newr not in seen_rule_ids:
                errors.append(
                    f"{prefix} new_rule_id {newr} not found in earlier rule rows"
                )
            if isinstance(sup, str) and isinstance(newr, str) and sup == newr:
                errors.append(
                    f"{prefix} supersedes_rule_id == new_rule_id ({sup}) — supersede must point to a different rule"
                )

    return errors


if __name__ == "__main__":
    # smoke: schema loads and validator instantiates
    assert isinstance(_validator, Draft202012Validator)
    print("schema loaded:", SCHEMA_PATH)
    print("layer1 errors on {}:", _layer1_errors({}))
