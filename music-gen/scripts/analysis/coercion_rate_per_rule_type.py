#!/usr/bin/env python3
# ---
# created: 2026-08-28T14:10:00Z
# cycle: 27
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-shape-mechanism
# ---
"""Coercion-rate per rule_type per batch (Mechanism M1).

Reads each batch's provenance.jsonl coherence_gate events and each
batch_manifest.json's per-song n_coercions / coercions block, then
tallies c1/c2/c3 firing counts per rule_type per batch.

Contract: c1 (arrangement_silence_vs_pitched_melodic) is attributed
to *arrangement* (the rule_type whose parameters were mutated).
c2 (harmonic_progression_shorter_than_form) is attributed to
*harmonic*. c3 (drums_pattern_empty_fallback_to_bass) is attributed
to *arrangement*.  This mapping matches the coercion-gate source
(scripts/gen/coherence_gate.py) where only arrangement/harmonic rows
are ever mutated by the gate; form/melodic/rhythmic rules are never
themselves mutated.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"coercion_rate_per_rule_type requires /usr/bin/python3, got {sys.executable}"
)

RULE_TYPES = ("arrangement", "form", "harmonic", "melodic", "rhythmic")

BATCHES = (
    ("batch_v1", "data/gen/batch_v1"),
    ("batch_v2", "data/gen/batch_v2"),
    ("batch_v3_i3", "data/gen/batch_v3_i3"),
    ("batch_v3_i4", "data/gen/batch_v3_i4"),
    ("batch_v4", "data/gen/batch_v4"),
    ("batch_v5_n16", "data/gen/batch_v5_n16"),
    ("batch_v6", "data/gen/batch_v6"),
)

# c1 → arrangement (arrangement.instrumentation mutated)
# c2 → harmonic   (harmonic.chord_progression mutated)
# c3 → arrangement (arrangement.instrumentation mutated)
COERCION_TO_RULE_TYPE = {
    "arrangement_silence_vs_pitched_melodic": "arrangement",
    "harmonic_progression_shorter_than_form": "harmonic",
    "drums_pattern_empty_fallback_to_bass": "arrangement",
}


def analyze_batch(batch_dir: pathlib.Path) -> dict:
    """Return per-batch dict: {n_salts, per_rule_type_coercion_count,
    per_rule_type_coercion_rate, per_rule_type_rule_id_change_count}."""
    prov = batch_dir / "provenance.jsonl"
    coerce_events = []
    if prov.exists():
        for line in prov.open():
            e = json.loads(line)
            if e.get("stage") == "coherence_gate":
                coerce_events.append(e)

    per_type_coerce_count = {rt: 0 for rt in RULE_TYPES}
    per_type_rule_id_change_count = {rt: 0 for rt in RULE_TYPES}
    n_salts = len(coerce_events)

    # Provenance only records n_coercions (scalar) + coerced/raw rule ids per
    # event; per-coercion which-rule detail lives in batch_manifest.json for
    # some batches. Pull applied_coercions if present.
    bmp = batch_dir / "batch_manifest.json"
    manifest = json.loads(bmp.read_text()) if bmp.exists() else None
    # per-song rows may sit under per_song or per_salt or similar
    applied_by_salt = {}
    if manifest:
        per_song_key = None
        for k in ("per_song", "songs", "per_salt", "song_records"):
            if k in manifest:
                per_song_key = k
                break
        if per_song_key:
            for row in manifest[per_song_key]:
                salt = row.get("salt")
                applied = None
                # Try common shapes
                if isinstance(row.get("coercions"), list):
                    applied = [c.get("coercion") for c in row["coercions"] if c.get("coercion")]
                elif isinstance(row.get("applied_coercions"), list):
                    applied = list(row["applied_coercions"])
                elif isinstance(row.get("coherence_gate"), dict):
                    applied = list(row["coherence_gate"].get("applied_coercions") or [])
                if salt is not None and applied is not None:
                    applied_by_salt[salt] = applied

    # Fall back to provenance n_coercions if manifest lacks named-coercion detail.
    # In this case we can only attribute totals — we distribute the count
    # uniformly across the union of possible coercions (this is the
    # conservative reading and matches the observed behavior since all three
    # coercions map to arrangement or harmonic only).
    for e in coerce_events:
        salt = e.get("salt")
        raw = e.get("input_shas", {}).get("chosen_rule_ids", {})
        cor = e.get("output_shas", {}).get("coerced_rule_ids", {})
        for rt in RULE_TYPES:
            if raw.get(rt) is not None and cor.get(rt) is not None:
                if raw[rt] != cor[rt]:
                    per_type_rule_id_change_count[rt] += 1

        applied = applied_by_salt.get(salt)
        n_coercions_scalar = e.get("output_shas", {}).get("n_coercions", 0)
        if applied is not None:
            for c in applied:
                rt = COERCION_TO_RULE_TYPE.get(c)
                if rt:
                    per_type_coerce_count[rt] += 1
        else:
            # Manifest lacks per-salt named coercions. All three coercion
            # rules mutate either arrangement or harmonic. Without named
            # detail we cannot split c1/c3 vs c2 exactly, so we record the
            # *scalar* as a "coercions attributed to {arrangement, harmonic}
            # collectively" and split evenly as a documented reading.
            share = n_coercions_scalar / 2.0
            per_type_coerce_count["arrangement"] += share  # type: ignore[operator]
            per_type_coerce_count["harmonic"] += share  # type: ignore[operator]

    per_type_coerce_rate = {
        rt: (per_type_coerce_count[rt] / n_salts if n_salts else 0.0)
        for rt in RULE_TYPES
    }
    return {
        "n_salts": n_salts,
        "per_rule_type_coercion_count": per_type_coerce_count,
        "per_rule_type_coercion_rate": per_type_coerce_rate,
        "per_rule_type_rule_id_change_count": per_type_rule_id_change_count,
        "manifest_had_named_coercions": bool(applied_by_salt),
    }


def run() -> dict:
    batches_out = {}
    for batch_id, rel in BATCHES:
        batch_dir = pathlib.Path(rel)
        if not batch_dir.exists():
            batches_out[batch_id] = {"status": "MISSING"}
            continue
        batches_out[batch_id] = analyze_batch(batch_dir)
    return {
        "rule_types": list(RULE_TYPES),
        "coercion_to_rule_type_map": COERCION_TO_RULE_TYPE,
        "batches": batches_out,
        "methodology_note": (
            "Coercion rate per rule_type = count of c1/c2/c3 firings that "
            "mutate that rule_type's parameters, divided by n_salts. "
            "c1 and c3 mutate arrangement; c2 mutates harmonic. "
            "form/melodic/rhythmic are never themselves mutated by the "
            "coherence gate — their coercion rate is always 0."
        ),
    }


def _write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


def _write_tsv(path: pathlib.Path, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["batch_id\trule_type\tcoercion_count\tcoercion_rate\trule_id_change_count\n"]
    for bid in sorted(summary["batches"]):
        b = summary["batches"][bid]
        if b.get("status") == "MISSING":
            continue
        for rt in RULE_TYPES:
            c = b["per_rule_type_coercion_count"][rt]
            r = b["per_rule_type_coercion_rate"][rt]
            chg = b["per_rule_type_rule_id_change_count"][rt]
            lines.append(f"{bid}\t{rt}\t{c:.6f}\t{r:.6f}\t{chg}\n")
    with path.open("w") as fh:
        fh.writelines(lines)


if __name__ == "__main__":  # pragma: no cover
    summary = run()
    _write_json(pathlib.Path("data/collision_model/coercion_rate_summary.json"), summary)
    _write_tsv(pathlib.Path("data/collision_model/coercion_rate_per_rule_type.tsv"), summary)
    total_changes = sum(
        sum(b["per_rule_type_rule_id_change_count"].values())
        for b in summary["batches"].values()
        if b.get("status") != "MISSING"
    )
    print(f"coercion rate summary written; total rule_id changes across all batches = {total_changes}")
