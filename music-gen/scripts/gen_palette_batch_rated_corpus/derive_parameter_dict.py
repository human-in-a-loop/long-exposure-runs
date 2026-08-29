#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T14:34:20Z
# cycle: 43
# run_id: fork-c320de981fda-clone-0
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-rated-corpus
# ---
"""Derive a deterministic per-rule parameter_dict from the frozen 4×4 table.

Verbatim clone of scripts/palette_render_v3/derive_parameter_dict.py
(c36 v3). Kept local to this cycle's tree per rubric §Preservation
invariants — the c36 module is READ-ONLY.

NO PRNG. No network. No non-factor sidecar imports.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

# Frozen table — copied verbatim from
# docs/palette_driven_batch_rated_corpus_rubric.md §3.
FLUIDSYNTH_TABLE: dict[str, list[float]] = {
    "chorus_level":     [0.3, 0.5, 0.7, 0.9],
    "reverb_level":     [0.2, 0.4, 0.6, 0.8],
    "reverb_room_size": [0.4, 0.5, 0.6, 0.7],
    "gain":             [0.6, 0.75, 0.9, 1.05],
}

SFIZZ_TABLE: dict[str, list[float]] = {
    "master_volume":         [-3.0, -1.5, 0.0, 1.5],
    "master_pitch_offset":   [-2.0, 0.0, 2.0, 4.0],
    "envelope_attack_mult":  [0.5, 0.75, 1.0, 1.25],
    "envelope_release_mult": [0.75, 1.0, 1.25, 1.5],
}


def _pick_index(rule_id: str, param_name: str) -> int:
    key = f"{rule_id}|{param_name}".encode("utf-8")
    digest = hashlib.sha256(key).digest()
    return int.from_bytes(digest[:4], "big") % 4


def derive_for_instrument(rule_id: str, instrument: str) -> dict:
    """Return the parameter_dict for one (rule_id, instrument) pair."""
    if instrument in ("fluidsynth", "fluidsynth_gm"):
        table = FLUIDSYNTH_TABLE
    elif instrument == "sfizz":
        table = SFIZZ_TABLE
    elif instrument in ("surge_xt", "dexed"):
        raise NotImplementedError(
            "VST3 param derivation deferred (c35 anti-pattern locked)"
        )
    else:
        raise RuntimeError(f"unsupported instrument {instrument}")

    out = {}
    for pname, values in table.items():
        idx = _pick_index(rule_id, pname)
        out[pname] = values[idx]
    return out


def derive_per_salt(rule_triple: dict[str, str],
                    per_stem_dispatch: dict[str, str]) -> dict:
    """For one salt: build stem-keyed parameter_dicts.

    Convention (c36 verbatim): harmonic→other, rhythmic→drums,
    arrangement→bass.
    """
    stem_from_rt = {"harmonic": "other", "rhythmic": "drums", "arrangement": "bass"}
    out: dict[str, dict] = {}
    for rt, stem in stem_from_rt.items():
        rid = rule_triple[rt]
        inst = per_stem_dispatch[stem]
        out[stem] = {
            "rule_type": rt,
            "rule_id": rid,
            "instrument": inst,
            "parameter_dict": derive_for_instrument(rid, inst),
        }
    return out


def canonical_json(payload) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def payload_sha256(payload) -> str:
    return hashlib.sha256(canonical_json(payload).encode("ascii")).hexdigest()


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule-id", required=True)
    ap.add_argument("--instrument", required=True)
    a = ap.parse_args()
    out = derive_for_instrument(a.rule_id, a.instrument)
    print(json.dumps(out, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
