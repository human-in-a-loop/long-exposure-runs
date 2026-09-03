#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T20:00:00Z
# cycle: 3
# run_id: run-2026-09-03T200000Z
# agent: worker
# milestone: M-V4-PROFILES-1/profile-writer-canonical-replay-field-added
# ---
"""profile_writer v2 (c3 additive extension) regression tests.

Contract:
 1. c2 profile SHA `11747a42cb1a8f7f...` reproduces byte-identical when the
    new kwarg is absent.
 2. `render_sha256_canonical_replay` field round-trips at top level when set.
 3. UUID5 profile_id is invariant under adding the new field.
 4. Schema-v4.0 valid with and without the new field.
 5. Legacy `render_sha256` still excluded from profile_id pre-image (and
    both the legacy and c3 fields are simultaneously excluded when set).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.sound_match import profile_writer as pw  # noqa: E402


def _c2_kwargs_from_disk() -> dict:
    d = json.load(open(REPO / "data/v4/profiles/31a164f845f8e27e/bass.json"))
    return dict(
        song_sha16=d["song_sha16"],
        instrument=d["instrument"],
        family=d["family"],
        identity=d["identity"],
        params=d["params"],
        deps_sha256=d["deps_sha256"],
        objective_scores=d["objective_scores"],
        search_metadata=d["search_metadata"],
        render_replayable=d["render_replayable"],
        provenance=d.get("provenance"),
    )


# 1. backwards-compat SHA regression
def test_c2_profile_sha_byte_identical_under_extended_signature():
    kwargs = _c2_kwargs_from_disk()
    row = pw.build_profile(**kwargs)
    new_bytes = pw.canonical_json(row)
    on_disk = (REPO / "data/v4/profiles/31a164f845f8e27e/bass.json").read_bytes()
    assert new_bytes == on_disk, (
        "c2 profile SHA drift: "
        f"new={hashlib.sha256(new_bytes).hexdigest()[:16]} "
        f"disk={hashlib.sha256(on_disk).hexdigest()[:16]}"
    )
    # exact expected SHA per brief
    assert hashlib.sha256(new_bytes).hexdigest() == (
        "11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9"
    )


# 2. new field round-trips at top level
def test_render_sha256_canonical_replay_round_trips():
    kwargs = _c2_kwargs_from_disk()
    fake_sha = "0" * 64
    row = pw.build_profile(
        **kwargs,
        render_sha256_canonical_replay=fake_sha,
    )
    assert row.get("render_sha256_canonical_replay") == fake_sha
    # Round-trip through canonical JSON
    bs = pw.canonical_json(row)
    row2 = json.loads(bs.decode())
    assert row2["render_sha256_canonical_replay"] == fake_sha


# 3. profile_id invariance under adding the new field
def test_profile_id_invariant_under_new_field():
    kwargs = _c2_kwargs_from_disk()
    row_a = pw.build_profile(**kwargs)
    row_b = pw.build_profile(**kwargs, render_sha256_canonical_replay="a" * 64)
    assert row_a["profile_id"] == row_b["profile_id"]


# 4. schema-v4.0 valid with and without the new field
def test_schema_v_and_required_keys():
    kwargs = _c2_kwargs_from_disk()
    for extra in ({}, {"render_sha256_canonical_replay": "b" * 64}):
        row = pw.build_profile(**kwargs, **extra)
        assert row["schema_v"] == "v4.0"
        for k in pw._REQUIRED_KEYS:
            assert k in row, k


# 5. profile_id excludes render_sha256* pre-image
def test_profile_id_excludes_render_sha256_and_new_field():
    kwargs = _c2_kwargs_from_disk()
    row = pw.build_profile(
        **kwargs,
        render_sha256="c" * 64,
        render_sha256_canonical_replay="d" * 64,
    )
    # profile_id should equal the plain-c2 profile_id (both render fields
    # are excluded from the UUID5 pre-image).
    row_plain = pw.build_profile(**kwargs)
    assert row["profile_id"] == row_plain["profile_id"]


if __name__ == "__main__":  # pragma: no cover
    ns = dict(globals())
    tests = [n for n in ns if n.startswith("test_")]
    passed = failed = 0
    for t in sorted(tests):
        try:
            ns[t]()
            print(f"PASS {t}")
            passed += 1
        except Exception as e:
            print(f"FAIL {t}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
