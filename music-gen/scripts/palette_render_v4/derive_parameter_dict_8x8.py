#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T09:09:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v4
# ---
"""8×8 parameter_dict derivation for palette-driven-batch-v4.

Total surface = 8 params × 8 values = 64 index slots.
- fluidsynth (5 params): gain, chorus_level, reverb_level, lp_cutoff, hp_cutoff
- sfizz     (3 params): master_volume, cutoff, resonance

Per-(rule_id, param_name) value pick via
    int.from_bytes(sha256(f"{rule_id}|{param_name}").digest()[:4], "big") % 8

NO PRNG. NO network. No sidecar_nonfactor imports.
"""
from __future__ import annotations

import hashlib
import json
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

# Frozen 8-value tables — copied verbatim from
# docs/palette_driven_batch_v4_rubric.md §1 (implied by param names) with
# canonical value ladders below.
FLUIDSYNTH_TABLE_V4: dict[str, list[float]] = {
    "gain":          [0.55, 0.65, 0.75, 0.85, 0.95, 1.05, 1.15, 1.25],
    "chorus_level":  [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00, 1.15],
    "reverb_level":  [0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90, 1.00],
    # Recorded for provenance; the fluidsynth CLI on this workspace does
    # not expose direct LP/HP-cutoff opcodes. Threaded through the
    # dispatch summary only. C38+ can promote via `-o synth.reverb.damp`
    # / `-o synth.chorus.speed` once fluidsynth CLI options are stable.
    "lp_cutoff":     [500.0, 1000.0, 2000.0, 3000.0, 4500.0, 6000.0, 8000.0, 12000.0],
    "hp_cutoff":     [20.0, 40.0, 80.0, 120.0, 200.0, 300.0, 500.0, 800.0],
}

SFIZZ_TABLE_V4: dict[str, list[float]] = {
    "master_volume": [-6.0, -4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5],
    # Threaded via the c37 opcode-file-rewrite fallback in
    # extend_sfizz_opcode_rewrite.py (SFZ fil_cutoff opcode, Hz).
    "cutoff":        [400.0, 800.0, 1500.0, 2500.0, 4000.0, 6000.0, 9000.0, 14000.0],
    # SFZ fil_resonance opcode, dB.
    "resonance":     [0.0, 1.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0],
}

INSTRUMENT_TO_TABLE = {
    "fluidsynth": FLUIDSYNTH_TABLE_V4,
    "fluidsynth_gm": FLUIDSYNTH_TABLE_V4,
    "sfizz": SFIZZ_TABLE_V4,
}


def _pick_index(rule_id: str, param_name: str) -> int:
    key = f"{rule_id}|{param_name}".encode("utf-8")
    digest = hashlib.sha256(key).digest()
    return int.from_bytes(digest[:4], "big") % 8


def derive_for_instrument(rule_id: str, instrument: str) -> dict:
    if instrument in ("surge_xt", "dexed"):
        raise NotImplementedError(
            "VST3 param derivation deferred; c35 A anti-pattern locked"
        )
    if instrument not in INSTRUMENT_TO_TABLE:
        raise RuntimeError(f"unsupported instrument {instrument}")
    table = INSTRUMENT_TO_TABLE[instrument]
    return {pname: values[_pick_index(rule_id, pname)]
            for pname, values in table.items()}


def derive_per_salt(rule_triple: dict[str, str],
                    per_stem_dispatch: dict[str, str]) -> dict:
    """Same stem/rule_type mapping as v3: harmonic→other, rhythmic→drums,
    arrangement→bass. Per-stem parameter_dict has 5 keys (fluidsynth) or
    3 keys (sfizz). Total per-salt surface: 5 + 3 + 3 = 11 threaded params
    (one fluidsynth stem, two sfizz stems)."""
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


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule-id", required=True)
    ap.add_argument("--instrument", required=True)
    a = ap.parse_args()
    print(json.dumps(derive_for_instrument(a.rule_id, a.instrument),
                     sort_keys=True, indent=2))
