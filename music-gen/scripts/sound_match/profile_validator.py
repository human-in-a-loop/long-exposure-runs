#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T00:00:00Z
# cycle: 17
# run_id: run-2026-09-04T000000Z
# agent: worker
# milestone: M-V4-RULES-1/pinned-profile-schema-v1
# ---
"""Validate a v4 pinned-profile manifest against pinned_profile_schema_v1.

Sibling to profile_writer.py (kept small so profile_writer.py stays a
diff-small READ-ONLY anchor). Two layers:

Layer 1 (structural): JSON Schema draft-07 via `jsonschema.Draft7Validator`
                       against `pinned_profile_schema_v1.json`.
Layer 2 (semantic):    hand-written cross-key checks that Layer 1 cannot
                       express cleanly — invariant (e) acceptance_fork
                       shape (4 nested keys or grandfathered v9 shape),
                       supersedes_path must be str (per c14 lemma).

Contract: raises `PinnedProfileValidationError` with a list-of-errors
string when validation fails; returns None on success. Never
partial-crashes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(f"profile_validator requires /usr/bin/python3 (got {sys.executable})")


_SCHEMA_PATH = Path(__file__).resolve().parent / "pinned_profile_schema_v1.json"


class PinnedProfileValidationError(ValueError):
    pass


def _layer1(profile: dict, errors: list[str]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        errors.append("jsonschema not installed; Layer 1 SKIPPED (Layer 2 will still run).")
        return
    schema = json.loads(_SCHEMA_PATH.read_text())
    validator = jsonschema.Draft7Validator(schema)
    for e in sorted(validator.iter_errors(profile), key=lambda x: list(x.path)):
        path = "/".join(str(p) for p in e.path) or "<root>"
        errors.append(f"Layer1 {path}: {e.message}")


def _layer2(profile: dict, errors: list[str]) -> None:
    # supersedes_path (c14 lemma): must be str or null, never list.
    if "supersedes_path" in profile:
        sp = profile["supersedes_path"]
        if sp is not None and not isinstance(sp, str):
            errors.append(
                f"Layer2 supersedes_path: expected str or null, got {type(sp).__name__} (c14 lemma)"
            )
    # acceptance_fork shape: 4-key canonical (c14) OR 3-key with rationale (c15)
    # OR grandfathered (c9 bass_v2). Accept any of these.
    fork = profile.get("acceptance_fork")
    if not isinstance(fork, dict):
        errors.append("Layer2 acceptance_fork: required object present")
        return
    # Invariant (e) permissive contract: chosen + rejected + one-of {authority, operator_authority}.
    required = {"chosen", "rejected"}
    missing = required - set(fork.keys())
    if missing:
        errors.append(f"Layer2 acceptance_fork: missing required keys {sorted(missing)}")
    if "authority" not in fork and "operator_authority" not in fork:
        errors.append("Layer2 acceptance_fork: must have 'authority' or 'operator_authority'")
    # env_pin coherence: values dict must contain exactly the keys array.
    env = profile.get("env_pin") or {}
    keys = env.get("keys") or []
    values = env.get("values") or {}
    if isinstance(keys, list) and isinstance(values, dict):
        vs = set(values.keys())
        ks = set(keys)
        if vs != ks:
            errors.append(
                f"Layer2 env_pin: keys array {sorted(ks)} must match values object keys {sorted(vs)}"
            )
    # song_sha16 basic shape (Layer 1 covers, but keep here in case Layer 1 skipped).
    ssha = profile.get("song_sha16", "")
    if not (isinstance(ssha, str) and len(ssha) == 16 and all(c in "0123456789abcdef" for c in ssha)):
        errors.append("Layer2 song_sha16: expected 16 lowercase hex chars")


def validate_pinned_profile(profile: dict) -> None:
    """Raise PinnedProfileValidationError with a joined list of errors, or None on success."""
    errors: list[str] = []
    _layer1(profile, errors)
    _layer2(profile, errors)
    if errors:
        raise PinnedProfileValidationError("; ".join(errors))


def validate_file(path: str | Path) -> None:
    p = Path(path)
    profile = json.loads(p.read_text())
    validate_pinned_profile(profile)


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    import argparse
    ap = argparse.ArgumentParser(description="Validate a v4 pinned-profile manifest.")
    ap.add_argument("path", help="Path to a pinned-profile JSON")
    args = ap.parse_args(argv)
    try:
        validate_file(args.path)
    except PinnedProfileValidationError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1
    print(f"VALID {args.path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
