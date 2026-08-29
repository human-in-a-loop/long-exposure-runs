#!/usr/bin/env python3
"""M-DAW-SPIKE-1/palette-schema-v2 — two-layer validator.

Author: cyd7bevdr@mozmail.com, cycle 34 Branch A clone-0 (fork 43802db1a81c).

Layer 1: jsonschema.Draft202012Validator against palette_v2.json.
Layer 2 (hand-written, cross-row):
  1. Duplicate assignment_id_v2 rejection.
  2. Provenance-pointer resolvability (streaming READ-ONLY on rules ledgers).
  3. v2_iterated_params: iterated_params key set === c33 P1-output anchor.
  4. v2_iterated_params: iteration_size == len(iterated_params) AND
     iteration_sha_256 == canonical-JSON SHA of iterated_params.
  5. v2_iterated_params: plugin_version matches c33 anchor.
  6. plugin_name ∈ {surge_xt, dexed, sfizz, fluidsynth_gm}.
  7. provenance_pointers sorted-lex canonical-form.
  8. v2 row with format=v1_flat and instrument ∈ {surge_xt, dexed}: REJECTED.
  9. assignment_id_v2 recomputation consistency (hash check).

Contract mirrors c31 M-RULES-1/validate.py:
  * Every function returns list[str] of error messages. Empty = success.
  * NEVER raises on validation failure. NEVER partial-crashes.
  * Every field access .get()-guarded.
  * Non-factor isolation: MUST NOT import scripts.classifier.sidecar_nonfactor.
"""

import json
import re
import sys
from pathlib import Path
from typing import Iterable, List, Optional

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

from jsonschema import Draft202012Validator  # noqa: E402

_HERE = Path(__file__).resolve().parent
SCHEMA_PATH = _HERE / "schema" / "palette_v2.json"

_KNOWN_PLUGIN_NAMES = frozenset({"surge_xt", "dexed", "sfizz", "fluidsynth_gm"})
_VST3_PLUGINS = frozenset({"surge_xt", "dexed"})


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    with open(path, "r") as f:
        return json.load(f)


_validator = Draft202012Validator(load_schema())


def _layer1_errors(row: dict) -> List[str]:
    errors = []
    for e in _validator.iter_errors(row):
        path = "/".join(str(p) for p in e.absolute_path) or "<root>"
        errors.append(f"schema:{path}:{e.message}")
    return errors


def _layer2_row_errors(row: dict, known_ids: Optional[set] = None) -> List[str]:
    from scripts.palette_v2.provenance import (
        compute_assignment_id_v2,
        known_rule_ids,
        anchor_iterated_params,
        sha256_iterated_params,
    )

    errors: List[str] = []
    if not isinstance(row, dict):
        return [f"row is not a dict (type={type(row).__name__})"]

    # (9) assignment_id_v2 hash consistency
    aid_declared = row.get("assignment_id_v2")
    if isinstance(aid_declared, str) and re.match(r"^[0-9a-f]{32}$", aid_declared):
        try:
            aid_computed = compute_assignment_id_v2(row)
            if aid_computed != aid_declared:
                errors.append(
                    f"assignment_id_v2 mismatch: declared={aid_declared}, "
                    f"computed_from_canonical_json={aid_computed}"
                )
        except Exception as e:
            errors.append(f"assignment_id_v2: could not recompute ({type(e).__name__}: {e})")

    # (7) provenance_pointers sorted-lex canonical form
    pointers = row.get("provenance_pointers") or []
    if isinstance(pointers, list) and len(pointers) > 0:
        if pointers != sorted(pointers):
            errors.append(
                f"provenance_pointers must be lexicographically sorted "
                f"(canonical form); got {pointers}"
            )
        if len(set(pointers)) != len(pointers):
            errors.append(
                f"provenance_pointers contains duplicate rule_ids: {pointers}"
            )

    # (2) provenance_pointers resolvability
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
                        f"provenance_pointers[{i}] unresolvable: rule_id={ptr!r} "
                        f"not found in data/rules/ledger.jsonl or "
                        f"data/rules/ledger_i3_dminor.jsonl"
                    )

    ps = row.get("pinned_state") or {}
    if not isinstance(ps, dict):
        return errors  # nothing else to check
    fmt = ps.get("format")
    plugin_name = ps.get("plugin_name")
    plugin_version = ps.get("plugin_version")
    instrument = row.get("instrument")

    # (6) plugin_name in known set (v2_iterated_params only — v1_flat accepts
    # c31 legacy names like "Surge XT", "Dexed", "fluidsynth" for backwards-compat)
    if fmt == "v2_iterated_params" and isinstance(plugin_name, str) \
            and plugin_name not in _KNOWN_PLUGIN_NAMES:
        errors.append(
            f"pinned_state.plugin_name unknown: {plugin_name!r} not in "
            f"{sorted(_KNOWN_PLUGIN_NAMES)}"
        )

    # (2a) v1/v2 field-cross-contamination — specific field-named message
    if fmt == "v2_iterated_params":
        for v1_only in ("parameter_dict", "preset_name_optional", "external_state_sha_optional"):
            if v1_only in ps:
                errors.append(
                    f"pinned_state.{v1_only} is a v1 field; not permitted with "
                    f"format=v2_iterated_params (additional properties rejected)"
                )
    if fmt == "v1_flat":
        for v2_only in ("iterated_params", "iteration_size", "iteration_sha_256"):
            if v2_only in ps:
                errors.append(
                    f"pinned_state.{v2_only} is a v2 field; not permitted with "
                    f"format=v1_flat"
                )

    # (8) v1_flat + VST3 rejection (v2 rows for VST3 MUST use v2_iterated_params)
    if fmt == "v1_flat" and instrument in _VST3_PLUGINS:
        errors.append(
            f"pinned_state.format v1_flat with instrument={instrument!r} "
            f"is rejected: v2 rows for VST3 plugins (surge_xt, dexed) MUST "
            f"use format=v2_iterated_params (v1_flat is a legacy-read path)"
        )

    # v2_iterated_params-specific checks
    if fmt == "v2_iterated_params":
        iterated = ps.get("iterated_params")
        iter_size = ps.get("iteration_size")
        iter_sha = ps.get("iteration_sha_256")

        if isinstance(iterated, dict):
            # (4) iteration_size == len(iterated_params)
            if isinstance(iter_size, int) and iter_size != len(iterated):
                errors.append(
                    f"pinned_state.iteration_size mismatch: declared={iter_size}, "
                    f"len(iterated_params)={len(iterated)}"
                )
            # (4) iteration_sha_256 == sha256(canonical_json(iterated_params))
            if isinstance(iter_sha, str):
                computed_sha = sha256_iterated_params(iterated)
                if iter_sha != computed_sha:
                    errors.append(
                        f"pinned_state.iteration_sha_256 mismatch: "
                        f"declared={iter_sha}, "
                        f"computed_from_canonical_json_iterated_params={computed_sha}"
                    )
            # (3) key set === c33 P1 anchor + (5) plugin_version match
            if isinstance(plugin_name, str) and plugin_name in _VST3_PLUGINS:
                try:
                    anchor_keys, anchor_version = anchor_iterated_params(plugin_name)
                except Exception as e:
                    errors.append(
                        f"pinned_state.iterated_params anchor read failed for "
                        f"plugin_name={plugin_name}: {type(e).__name__}: {e}"
                    )
                else:
                    row_keys = set(iterated.keys())
                    extra = row_keys - anchor_keys
                    missing = anchor_keys - row_keys
                    if extra or missing:
                        errors.append(
                            f"pinned_state.iterated_params key set does not "
                            f"match c33 P1-output anchor for "
                            f"plugin_name={plugin_name}: "
                            f"extra_keys={sorted(extra)[:3]}"
                            f"{'...' if len(extra)>3 else ''} "
                            f"missing_keys={sorted(missing)[:3]}"
                            f"{'...' if len(missing)>3 else ''}"
                        )
                    if isinstance(plugin_version, str) and plugin_version != anchor_version:
                        errors.append(
                            f"pinned_state.plugin_version mismatch vs c33 "
                            f"dawdreamer_state anchor for "
                            f"plugin_name={plugin_name}: declared={plugin_version!r}, "
                            f"anchor={anchor_version!r}"
                        )
            elif isinstance(plugin_name, str):
                # v2_iterated_params only permitted for VST3; sfizz/fluidsynth_gm
                # must use v1_flat (documented skip reason format_v1_flat_only)
                errors.append(
                    f"pinned_state.format=v2_iterated_params is only permitted "
                    f"for VST3 plugins (surge_xt, dexed); got "
                    f"plugin_name={plugin_name!r}"
                )

    return errors


def validate_row(row: dict, known_ids: Optional[set] = None) -> List[str]:
    if not isinstance(row, dict):
        return [f"row is not a dict (type={type(row).__name__})"]
    errors = _layer1_errors(row)
    errors.extend(_layer2_row_errors(row, known_ids=known_ids))
    return errors


def validate_batch(rows: Iterable[dict]) -> List[str]:
    from scripts.palette_v2.provenance import known_rule_ids

    errors: List[str] = []
    seen_aids: dict = {}
    known_ids = known_rule_ids()

    for i, row in enumerate(rows):
        prefix = f"row[{i}]"
        row_errors = validate_row(row, known_ids=known_ids)
        for e in row_errors:
            errors.append(f"{prefix} {e}")

        aid = (row or {}).get("assignment_id_v2") if isinstance(row, dict) else None
        if isinstance(aid, str):
            if aid in seen_aids:
                errors.append(
                    f"{prefix} duplicate_assignment_id_v2: {aid} "
                    f"first-seen at row[{seen_aids[aid]}]"
                )
            else:
                seen_aids[aid] = i

    return errors


if __name__ == "__main__":
    print("schema loaded:", SCHEMA_PATH)
    print("layer1 errors on {}:", _layer1_errors({}))
