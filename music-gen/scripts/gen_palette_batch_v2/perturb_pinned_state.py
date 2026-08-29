#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:07:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v2-sampler-diversified
# ---
"""Deterministic per-rule perturbation of Surge XT + Dexed pinned states.

Consumes the c33 dawdreamer_state P1 iterated_params anchor
(`data/dawdreamer_state/per_plugin/<plugin>/p1_state_v2.json` — READ-ONLY)
and produces a `v2_iterated_params` payload deterministically perturbed
by (rule_id, param_name).

For each `(rule_id, param_name)`:
  digest = sha256(f"{rule_id}|{param_name}".encode("ascii")).digest()
  seed_u32 = int.from_bytes(digest[0:4], "big")

Fixed typed perturbation table (drums = fluidsynth-static — no perturbation):
  * float in [0.0, 1.0]         → clamp(base + delta*δ_f, 0.0, 1.0),
                                   δ_f = 0.05, delta ∈ [-1, +1]
                                   via seed_u32 mapped through int(seed_u32) / (2^32-1)*2 - 1.
  * float outside [0.0, 1.0]    → base + delta*δ_f*max(1e-6, abs(base)),
                                   scale-relative perturbation, δ_f = 0.05.
  * int (Python int, not bool)  → base + ((seed_u32 % N) - N//2), N = 3.
  * bool                        → base XOR (seed_u32 & 1).

Result is validated through `scripts.palette_v2.validate.validate_row_v2`
before return. NO PRNG. NO writes into c33 or c34 anchor directories.

Note: c33 `scripts.palette_render.render_stem` does NOT consume
`pinned_state` — it dispatches on `(stem, instrument)` alone and, for
`instrument ∈ {fluidsynth_gm, sfizz}`, renders per-stem MIDI through the
committed SF2/SFZ. The v2_iterated_params payload authored here is
CORRECT and VALIDATED against palette_v2 schema, but does not flow into
audio bytes on this cycle. That gap is the c36 handoff.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

FLOAT_DELTA = 0.05
INT_STRIDE_N = 3
DAWDREAMER_STATE_ROOT = _REPO / "data" / "dawdreamer_state" / "per_plugin"

# Plugins that carry a v2 pinned-state anchor. drums = fluidsynth-static.
PALETTE_V2_PLUGINS = ("surge_xt", "dexed")


def _seed_u32(rule_id: str, param_name: str) -> int:
    digest = hashlib.sha256(
        f"{rule_id}|{param_name}".encode("ascii")
    ).digest()
    return int.from_bytes(digest[0:4], "big")


def _perturb_scalar(base: object, seed_u32: int) -> object:
    """Deterministic typed perturbation. bool checked BEFORE int (bool is int-subclass)."""
    if isinstance(base, bool):
        return bool(int(base) ^ (seed_u32 & 1))
    if isinstance(base, int):
        return int(base) + ((seed_u32 % INT_STRIDE_N) - (INT_STRIDE_N // 2))
    if isinstance(base, float):
        # Map seed_u32 to a signed delta in [-1, +1] via fixed-point.
        delta = (seed_u32 / float(2**32 - 1)) * 2.0 - 1.0
        if 0.0 <= base <= 1.0:
            return max(0.0, min(1.0, base + delta * FLOAT_DELTA))
        scale = max(1e-6, abs(base))
        return base + delta * FLOAT_DELTA * scale
    # Non-scalar or unknown type: pass through unchanged.
    return base


def _load_anchor(plugin_name: str) -> dict:
    """Load c33 P1 anchor for `plugin_name` from data/dawdreamer_state/.

    The c33 anchor's on-disk shape (see
    scripts/dawdreamer_state/probe_p1_iterate_parameters.py::probe_one)
    is a FLAT dict: `{"<5-digit-index>:<name>": <value>, ...}`. That
    matches palette_v2 schema's `iterated_params` key pattern
    `^[0-9]{5}:.+$` exactly. Return a normalized wrapper so downstream
    code always sees `{iterated_params, plugin_name, plugin_version}`.
    """
    path = DAWDREAMER_STATE_ROOT / plugin_name / "p1_state_v2.json"
    if not path.is_file():
        raise RuntimeError(
            f"c33 anchor missing for plugin={plugin_name}: {path}"
        )
    obj = json.loads(path.read_text())
    if not isinstance(obj, dict):
        raise RuntimeError(
            f"anchor for {plugin_name} must be a flat dict; got "
            f"{type(obj).__name__}"
        )
    # Plugin-version pin comes from c34 palette_v2.provenance's canonical
    # anchor manifest so the validator's Layer-2 (5) plugin_version check
    # passes byte-for-byte.
    from scripts.palette_v2.provenance import anchor_iterated_params  # noqa: E402
    _keys, plugin_version = anchor_iterated_params(plugin_name)
    return {
        "plugin_name": plugin_name,
        "plugin_version": plugin_version,
        "iterated_params": obj,
    }


def perturb_v2_payload(rule_id: str, plugin_name: str) -> dict:
    """Return a `v2_iterated_params` payload for `(rule_id, plugin_name)`.

    Shape conforms to palette_v2 schema's `format=v2_iterated_params`
    variant. Every param in the anchor `iterated_params` block is
    perturbed by the (rule_id, param_name) rule of the fixed table above.
    """
    if plugin_name not in PALETTE_V2_PLUGINS:
        raise ValueError(
            f"palette-v2 pinned-state format only for {PALETTE_V2_PLUGINS}; "
            f"got {plugin_name} (drums = fluidsynth-static; no perturbation)"
        )
    anchor = _load_anchor(plugin_name)
    base_iterated = anchor.get("iterated_params") or {}
    if not isinstance(base_iterated, dict):
        raise RuntimeError(
            f"anchor iterated_params must be dict; got {type(base_iterated).__name__}"
        )

    perturbed: dict[str, object] = {}
    for pname, base in sorted(base_iterated.items()):
        seed = _seed_u32(rule_id, pname)
        perturbed[pname] = _perturb_scalar(base, seed)

    # Use the palette_v2 canonical helpers so the SHA-256 encoding matches
    # the validator's expectation byte-for-byte.
    from scripts.palette_v2.provenance import sha256_iterated_params  # noqa: E402
    payload = {
        "format": "v2_iterated_params",
        "plugin_name": plugin_name,
        "plugin_version": anchor["plugin_version"],
        "iterated_params": perturbed,
        "iteration_size": len(perturbed),
        "iteration_sha_256": sha256_iterated_params(perturbed),
    }
    return payload


def build_v2_assignment_row(stem: str, plugin_name: str,
                            rule_id: str,
                            provenance_pointers: list[str]) -> dict:
    """Assemble a palette-v2 assignment row and validate through palette_v2.

    Signature intentionally matches palette-v1's authoring flow.
    `assignment_id_v2` is computed by scripts.palette_v2.provenance.
    """
    # Import lazily to keep the module importable even if palette_v2 is missing
    # (the validator is exercised only when payloads are authored).
    from scripts.palette_v2.provenance import compute_assignment_id_v2  # noqa: E402
    from scripts.palette_v2.validate import validate_row as validate_row_v2  # noqa: E402

    pinned = perturb_v2_payload(rule_id, plugin_name)
    row = {
        "schema_v": "palette_v2",
        "stem": stem,
        "instrument": plugin_name,
        "pinned_state": pinned,
        "provenance_pointers": sorted(provenance_pointers),
        "extractor_version": "palette_v2_c34",
    }
    row["assignment_id_v2"] = compute_assignment_id_v2(row)
    errors = validate_row_v2(row)
    if errors:
        raise RuntimeError(
            f"palette_v2 validator rejected perturbed row (stem={stem}, "
            f"plugin={plugin_name}, rule_id={rule_id}): {errors}"
        )
    return row


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule-id", required=True)
    ap.add_argument("--plugin", required=True, choices=list(PALETTE_V2_PLUGINS))
    args = ap.parse_args()
    payload = perturb_v2_payload(args.rule_id, args.plugin)
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
