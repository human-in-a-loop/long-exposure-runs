#!/usr/bin/env python3
"""M-DAW-SPIKE-1/palette-schema-v2 — provenance + assignment_id_v2 utilities.

Author: cyd7bevdr@mozmail.com, cycle 34 Branch A clone-0 (fork 43802db1a81c).

Public API:
  * canonical_json_for_assignment_id_v2(row) -> str
  * compute_assignment_id_v2(row) -> str
  * resolve_provenance_pointer(rule_id) -> Optional[dict]
  * known_rule_ids() -> set[str]
  * anchor_iterated_params(plugin_name) -> tuple[set, str]  # (key_set, plugin_version)

Contract:
  * NEVER modifies the rules ledgers or c33 dawdreamer_state anchors.
  * NEVER partial-crashes; malformed rows are skipped.
  * No PRNG; no sidecar_nonfactor imports.
"""

import hashlib
import json
import sys
import uuid
from pathlib import Path
from typing import Iterable, Optional, Tuple

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_REPO = Path(__file__).resolve().parent.parent.parent  # palette_v2 -> scripts -> repo
DEFAULT_LEDGER_PATHS = (
    _REPO / "data" / "rules" / "ledger.jsonl",
    _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl",
)

# NEW UUID5 namespace, distinct from c31's palette_v1 namespace.
# Computed once, stable, human-auditable:
#   uuid5(NAMESPACE_URL, "palette_v2::music-gen::c34")
#     -> 063eb50e-0aac-59bb-84a8-ef26540a8912
# vs c31 palette_v1 namespace 44e07e49-d932-519e-8f5c-583c960bb37e.
NAMESPACE_PALETTE_V2 = uuid.uuid5(uuid.NAMESPACE_URL, "palette_v2::music-gen::c34")

# Fields participating in assignment_id_v2 hash. notes_optional EXCLUDED.
_HASHED_FIELDS = (
    "schema_v",
    "stem",
    "instrument",
    "pinned_state",
    "provenance_pointers",
    "extractor_version",
)

# c33 dawdreamer_state P1 anchor paths (READ-ONLY).
_ANCHOR_DIR = _REPO / "data" / "dawdreamer_state" / "per_plugin"


def _canonicalize_pinned_state(ps):
    """Sort inner dict keys deterministically; return a new dict."""
    if not isinstance(ps, dict):
        return ps
    out = {}
    keys_v1 = ("format", "plugin_name", "plugin_version", "parameter_dict",
               "preset_name_optional", "external_state_sha_optional")
    keys_v2 = ("format", "plugin_name", "plugin_version", "iterated_params",
               "iteration_size", "iteration_sha_256")
    fmt = ps.get("format")
    order = keys_v2 if fmt == "v2_iterated_params" else keys_v1
    for k in order:
        if k in ps:
            v = ps[k]
            if k == "parameter_dict" and isinstance(v, dict):
                v = {pk: v[pk] for pk in sorted(v)}
            if k == "iterated_params" and isinstance(v, dict):
                v = {pk: v[pk] for pk in sorted(v)}
            out[k] = v
    # Preserve any remaining keys (defensive; Layer 1 rejects extras anyway)
    for k, v in ps.items():
        if k not in out:
            out[k] = v
    return out


def canonical_json_for_assignment_id_v2(row: dict) -> str:
    payload = {}
    for k in _HASHED_FIELDS:
        v = row.get(k) if isinstance(row, dict) else None
        if k == "provenance_pointers" and isinstance(v, list):
            v = sorted(v)
        elif k == "pinned_state":
            v = _canonicalize_pinned_state(v)
        payload[k] = v
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_assignment_id_v2(row: dict) -> str:
    canonical = canonical_json_for_assignment_id_v2(row)
    return uuid.uuid5(NAMESPACE_PALETTE_V2, canonical).hex


def canonical_json_iterated_params(iterated: dict) -> str:
    """Canonical JSON of iterated_params (used by iteration_sha_256 check)."""
    return json.dumps(iterated, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_iterated_params(iterated: dict) -> str:
    return hashlib.sha256(canonical_json_iterated_params(iterated).encode("utf-8")).hexdigest()


def _iter_ledger_rows(path: Path) -> Iterable[dict]:
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


def resolve_provenance_pointer(rule_id: str,
                               ledger_paths: Iterable[Path] = DEFAULT_LEDGER_PATHS) -> Optional[dict]:
    if not isinstance(rule_id, str) or not rule_id:
        return None
    for p in ledger_paths:
        for row in _iter_ledger_rows(Path(p)):
            if row.get("rule_id") == rule_id:
                return row
    return None


def known_rule_ids(ledger_paths: Iterable[Path] = DEFAULT_LEDGER_PATHS) -> set:
    ids = set()
    for p in ledger_paths:
        for row in _iter_ledger_rows(Path(p)):
            rid = row.get("rule_id")
            if isinstance(rid, str):
                ids.add(rid)
    return ids


# c33 P1 anchor plugin_version manifest — locked at c33 close.
# (surge_xt / dexed are the two VST3 plugins the c33 Branch B WORKAROUND_FOUND
#  verdict covered; sfizz + fluidsynth_gm continue to use v1_flat.)
_ANCHOR_PLUGIN_VERSIONS = {
    "surge_xt": "1.3.4",
    "dexed": "0.9.9",
}


def anchor_iterated_params(plugin_name: str) -> Tuple[set, str]:
    """Return (key_set, plugin_version) for the c33 P1 anchor. READ-ONLY.

    Raises FileNotFoundError if the anchor is missing (VST3 not
    characterized in c33) or the plugin is unknown.
    """
    if plugin_name not in _ANCHOR_PLUGIN_VERSIONS:
        raise KeyError(f"plugin_name {plugin_name!r} has no c33 P1 anchor")
    path = _ANCHOR_DIR / plugin_name / "p1_state_v2.json"
    with open(path, "r") as f:
        anchor = json.load(f)
    return set(anchor.keys()), _ANCHOR_PLUGIN_VERSIONS[plugin_name]


if __name__ == "__main__":
    # smoke
    ex = {
        "schema_v": "palette_v2",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": {
            "format": "v2_iterated_params",
            "plugin_name": "surge_xt",
            "plugin_version": "1.3.4",
            "iterated_params": {"00000:M1: -": 0.0},
            "iteration_size": 1,
            "iteration_sha_256": sha256_iterated_params({"00000:M1: -": 0.0}),
        },
        "provenance_pointers": ["rule_0271c7a9f3b5f606"],
        "extractor_version": "palette_v2_c34",
    }
    a = compute_assignment_id_v2(ex)
    b = compute_assignment_id_v2(ex)
    assert a == b
    print(f"smoke ok: assignment_id_v2={a}, NAMESPACE_PALETTE_V2={NAMESPACE_PALETTE_V2}")
