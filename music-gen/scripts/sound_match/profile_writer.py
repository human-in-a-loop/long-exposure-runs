#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES
# ---
"""Profile writer for v4 sound-matching layer.

Schema keys (see docs/specs/v4_sound_matching_layer_spec.md):
    schema_v, song_sha16, instrument, family, identity, params,
    deps_sha256, objective_scores, search_metadata, render_replayable,
    render_sha256 (per-replay-run), profile_id.

`profile_id` is UUID5 of a canonical-JSON dict of the row minus
`render_sha256` (the run-specific replay evidence). This makes the id
stable across replays and re-verifiable from the pinned inputs.
"""
from __future__ import annotations

import hashlib
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Mapping

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"profile_writer requires /usr/bin/python3 (got {sys.executable})"
    )

SCHEMA_V = "v4.0"
_NAMESPACE_PROFILE = uuid.UUID("2f4b6c7d-8e9a-4b1c-a2d3-e4f556677889")
_ALLOWED_FAMILIES = {"sf2", "sfz", "stem_sampled", "surge"}
_REQUIRED_KEYS = (
    "schema_v",
    "song_sha16",
    "instrument",
    "family",
    "identity",
    "params",
    "deps_sha256",
    "objective_scores",
    "search_metadata",
    "render_replayable",
)


def canonical_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def compute_profile_id(row: Mapping[str, Any]) -> str:
    """UUID5 content hash of the row minus render_sha256* + profile_id.

    Any top-level field whose name starts with ``render_sha256`` is
    excluded before hashing (c3 additive extension per MODERATE #3:
    covers legacy `render_sha256`, the new `render_sha256_canonical_replay`,
    and any future `render_sha256_*` sibling). Replays produce the same
    profile_id from the pinned inputs.
    """
    body = {
        k: v for k, v in row.items()
        if k != "profile_id" and not k.startswith("render_sha256")
    }
    return str(uuid.uuid5(_NAMESPACE_PROFILE, canonical_json(body).decode()))


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_profile(
    *,
    song_sha16: str,
    instrument: str,
    family: str,
    identity: Mapping[str, Any],
    params: Mapping[str, Any],
    deps_sha256: Mapping[str, str],
    objective_scores: Mapping[str, Any],
    search_metadata: Mapping[str, Any],
    render_replayable: bool = True,
    render_sha256: str | None = None,
    provenance: Mapping[str, Any] | None = None,
    render_sha256_canonical_replay: str | None = None,
) -> dict:
    """Build a v4 sound profile row.

    Additive kwargs (all backward-compatible; profile_id excludes them):

    * ``provenance`` (c2): a dict naming the stage-1 + stage-2 sweep
      leaderboards and their SHA-256s so the winning-profile row is
      traceable to the sweep evidence it came from.
    * ``render_sha256_canonical_replay`` (c3, MODERATE #3 fix): SHA-256
      of the canonical `replay(profile, MIDI)` output produced under
      pinned env, distinct from the in-sweep render SHA already recorded
      under ``search_metadata.render_sha256_in_sweep``. Excluded from
      profile_id computation (see ``compute_profile_id``).

    When both new kwargs are omitted, the row shape is byte-identical to
    c1's; when only ``provenance`` is set, byte-identical to c2's.
    """
    if family not in _ALLOWED_FAMILIES:
        raise ValueError(
            f"family={family!r} not in {_ALLOWED_FAMILIES}"
        )
    row: dict = {
        "schema_v": SCHEMA_V,
        "song_sha16": song_sha16,
        "instrument": instrument,
        "family": family,
        "identity": dict(identity),
        "params": dict(params),
        "deps_sha256": dict(deps_sha256),
        "objective_scores": dict(objective_scores),
        "search_metadata": dict(search_metadata),
        "render_replayable": bool(render_replayable),
    }
    for k in _REQUIRED_KEYS:
        if k not in row:
            raise KeyError(f"profile missing required key: {k}")
    if provenance is not None:
        row["provenance"] = dict(provenance)
    row["profile_id"] = compute_profile_id(row)
    if render_sha256 is not None:
        row["render_sha256"] = render_sha256
    if render_sha256_canonical_replay is not None:
        row["render_sha256_canonical_replay"] = render_sha256_canonical_replay
    return row


def write_profile(row: Mapping[str, Any], out_path: Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(canonical_json(row))
