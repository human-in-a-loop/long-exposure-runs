#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T00:00:00Z
# cycle: 17
# run_id: run-2026-09-04T000000Z
# agent: worker
# milestone: M-V4-RULES-1/pinned-profile-schema-v1
# ---
"""Tests for pinned_profile_schema_v1 + profile_validator.

Covers c14/c16-canonical shape codified by invariant (e):
  1. c9 bass_v2 grandfathered pinned profile validates.
  2. c14 drums canonical pinned profile validates.
  3. c15 guitar canonical pinned profile validates.
  4. Malformed input: missing acceptance_fork -> fails with clear message.
  5. Malformed input: 3-key nested acceptance_fork missing 'authority' -> fails.
  6. Malformed input: supersedes_path as list (c14 lemma) -> fails.

Runner: PYTHONPATH=. /usr/bin/python3 tests/test_pinned_profile_schema.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Path shim so imports work whether invoked from workspace root or elsewhere.
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[1]
sys.path.insert(0, str(_ROOT))

from scripts.sound_match.profile_validator import (  # noqa: E402
    PinnedProfileValidationError,
    validate_pinned_profile,
)


_DELIVERY = _ROOT / "data/v4/deliveries/31a164f845f8e27e"


def _load(name: str) -> dict:
    return json.loads((_DELIVERY / name).read_text())


def test_c9_bass_v2_grandfathered_validates() -> None:
    profile = _load("cg_bass_pinned_profile.json")
    validate_pinned_profile(profile)  # must not raise


def test_c14_drums_canonical_validates() -> None:
    profile = _load("cg_drums_pinned_profile.json")
    validate_pinned_profile(profile)  # must not raise


def test_c15_guitar_canonical_validates() -> None:
    profile = _load("cg_guitar_pinned_profile.json")
    validate_pinned_profile(profile)  # must not raise


def test_missing_acceptance_fork_fails_clearly() -> None:
    profile = _load("cg_drums_pinned_profile.json")
    profile.pop("acceptance_fork", None)
    try:
        validate_pinned_profile(profile)
    except PinnedProfileValidationError as e:
        assert "acceptance_fork" in str(e), f"expected acceptance_fork in error, got: {e}"
        return
    raise AssertionError("expected PinnedProfileValidationError")


def test_incomplete_acceptance_fork_missing_authority_fails() -> None:
    profile = _load("cg_drums_pinned_profile.json")
    # Neither 'authority' nor 'operator_authority' -> must fail per Layer 2 permissive rule.
    profile["acceptance_fork"] = {"chosen": "OPT3", "rejected": ["OPT1", "OPT2"]}
    try:
        validate_pinned_profile(profile)
    except PinnedProfileValidationError as e:
        assert "authority" in str(e), f"expected authority in error, got: {e}"
        return
    raise AssertionError("expected PinnedProfileValidationError")


def test_supersedes_path_as_list_fails_c14_lemma() -> None:
    profile = _load("cg_drums_pinned_profile.json")
    profile["supersedes_path"] = ["path/a", "path/b"]  # violates c14 lemma
    try:
        validate_pinned_profile(profile)
    except PinnedProfileValidationError as e:
        assert "supersedes_path" in str(e), f"expected supersedes_path in error, got: {e}"
        return
    raise AssertionError("expected PinnedProfileValidationError")


def main() -> int:
    tests = [
        test_c9_bass_v2_grandfathered_validates,
        test_c14_drums_canonical_validates,
        test_c15_guitar_canonical_validates,
        test_missing_acceptance_fork_fails_clearly,
        test_incomplete_acceptance_fork_missing_authority_fails,
        test_supersedes_path_as_list_fails_c14_lemma,
    ]
    n_pass = 0
    for t in tests:
        try:
            t()
            n_pass += 1
            print(f"PASS  {t.__name__}")
        except Exception as e:
            print(f"FAIL  {t.__name__}: {e}")
    total = len(tests)
    print(f"\n{n_pass}/{total} PASS")
    return 0 if n_pass == total else 1


if __name__ == "__main__":
    sys.exit(main())
