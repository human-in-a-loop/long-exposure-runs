#!/usr/bin/env python3
# ---
# created: 2026-08-28T14:15:00Z
# cycle: 27
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-shape-mechanism
# ---
"""Effective-K probe per rule_type per batch (Mechanism M2).

For each batch, for each salt, for each rule_type, count how many rules
of that rule_type are 'admissible' — i.e. would NOT trigger any coherence-
gate coercion given the OTHER rule_types' actual chosen picks.  Average
over salts to get K_eff per rule_type per batch.

Coercion trigger definitions (from scripts/gen/coherence_gate.py):

  c1 arrangement_silence_vs_pitched_melodic
      TRIGGER: arrangement.instrumentation excludes both {bass, piano}
               AND melodic.pitch_class_histogram has any nonzero bin.
      MUTATES: arrangement.

  c2 harmonic_progression_shorter_than_form
      TRIGGER: max(form.sections[*].end_measure) > len(harmonic.chord_progression).
      MUTATES: harmonic.

  c3 drums_pattern_empty_fallback_to_bass
      TRIGGER: 'drums' in arrangement.instrumentation
               AND rhythmic.pattern is empty or contains only 'rest' tokens.
      MUTATES: arrangement.

Admissibility rule per rule_type:
  arrangement admissible under (melodic_pick, rhythmic_pick):
    - would NOT trigger c1: arrangement.instrumentation contains bass or piano
                            OR melodic_pick's PCH is all zero
    - AND would NOT trigger c3: 'drums' not in arrangement.instrumentation
                            OR rhythmic_pick's pattern has non-rest onsets
  harmonic admissible under (form_pick):
    - would NOT trigger c2: len(chord_progression) >= max(form.sections end_measure)
  form/melodic/rhythmic: never themselves mutated -> K_eff = K.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"effective_k_probe requires /usr/bin/python3, got {sys.executable}"
)

RULE_TYPES = ("arrangement", "form", "harmonic", "melodic", "rhythmic")

# Which batches use which rules ledger (see observations.json).
BATCH_LEDGER = {
    "batch_v1": "data/rules/ledger.jsonl",
    "batch_v2": "data/rules/ledger.jsonl",
    "batch_v3_i3": "data/rules/ledger_i3_dminor.jsonl",
    "batch_v3_i4": "data/rules/ledger.jsonl",
    "batch_v4": "data/rules/ledger_i3_dminor.jsonl",
    "batch_v6": "data/rules/ledger_i3_dminor.jsonl",
}

BATCH_DIRS = {bid: f"data/gen/{bid}" for bid in BATCH_LEDGER}


def load_rules(ledger_path: pathlib.Path) -> dict:
    """Return {rule_type: {rule_id: parameters_dict}}."""
    out: dict[str, dict] = {rt: {} for rt in RULE_TYPES}
    for line in ledger_path.open():
        r = json.loads(line)
        if r.get("event_type") != "rule":
            continue
        rt = r.get("rule_type")
        rid = r.get("rule_id")
        if rt in RULE_TYPES and rid:
            out[rt][rid] = r.get("parameters") or {}
    return out


def _c1_triggers(arr_params: dict, mel_params: dict) -> bool:
    instr = list(arr_params.get("instrumentation") or [])
    pch = list(mel_params.get("pitch_class_histogram") or [])
    pitched_present = any(i in ("bass", "piano") for i in instr)
    melodic_nonzero = any(float(p) > 0.0 for p in pch)
    return (not pitched_present) and melodic_nonzero


def _c2_triggers(har_params: dict, form_params: dict) -> bool:
    progression = list(har_params.get("chord_progression") or [])
    sections = list(form_params.get("sections") or [])
    if not progression or not sections:
        return False
    max_end = max(int(s.get("end_measure", 0)) for s in sections)
    return max_end > 0 and len(progression) < max_end


def _c3_triggers(arr_params: dict, rhy_params: dict) -> bool:
    instr = list(arr_params.get("instrumentation") or [])
    pattern = list(rhy_params.get("pattern") or [])
    if "drums" not in instr:
        return False
    onsets = [t for t in pattern if t != "rest"]
    return len(onsets) == 0


SAMPLE_STAGES = ("sample_rules", "sample_rules_unconditioned", "sample_rules_i4")


def load_salt_picks(batch_dir: pathlib.Path) -> list[dict]:
    """Return list of {salt: int, rule_ids: {rule_type: rule_id}} from
    provenance sample_rules* events (batches use different stage names)."""
    prov = batch_dir / "provenance.jsonl"
    if not prov.exists():
        return []
    picks = []
    for line in prov.open():
        e = json.loads(line)
        if e.get("stage") in SAMPLE_STAGES:
            picks.append({
                "salt": e.get("salt"),
                "rule_ids": dict(e.get("output_shas", {}).get("chosen_rule_ids") or {}),
            })
    # Sort by salt for determinism
    picks.sort(key=lambda x: (x["salt"] is None, x["salt"]))
    return picks


def k_eff_for_batch(batch_id: str) -> dict:
    """Return {K_raw, K_eff_per_salt, K_eff_mean_per_rule_type, n_salts}."""
    ledger_path = pathlib.Path(BATCH_LEDGER[batch_id])
    rules = load_rules(ledger_path)
    K_raw = {rt: len(rules[rt]) for rt in RULE_TYPES}

    picks = load_salt_picks(pathlib.Path(BATCH_DIRS[batch_id]))
    if not picks:
        return {
            "K_raw": K_raw,
            "K_eff_per_salt": [],
            "K_eff_mean_per_rule_type": {rt: float(K_raw[rt]) for rt in RULE_TYPES},
            "n_salts": 0,
            "status": "NO_PROVENANCE",
        }

    per_salt = []
    for p in picks:
        rids = p["rule_ids"]
        # Fetch parameters of the actual picks for other rule_types.
        mel_pick = rules["melodic"].get(rids.get("melodic"), {})
        rhy_pick = rules["rhythmic"].get(rids.get("rhythmic"), {})
        form_pick = rules["form"].get(rids.get("form"), {})

        # arrangement admissible under (melodic pick, rhythmic pick).
        arr_eff = 0
        for _rid, arr_p in rules["arrangement"].items():
            if _c1_triggers(arr_p, mel_pick):
                continue
            if _c3_triggers(arr_p, rhy_pick):
                continue
            arr_eff += 1

        # harmonic admissible under (form pick).
        har_eff = 0
        for _rid, har_p in rules["harmonic"].items():
            if _c2_triggers(har_p, form_pick):
                continue
            har_eff += 1

        per_salt.append({
            "salt": p["salt"],
            "K_eff_arrangement": arr_eff,
            "K_eff_harmonic": har_eff,
            "K_eff_form": K_raw["form"],
            "K_eff_melodic": K_raw["melodic"],
            "K_eff_rhythmic": K_raw["rhythmic"],
        })

    n = len(per_salt)
    mean = {}
    for rt in RULE_TYPES:
        key = f"K_eff_{rt}"
        mean[rt] = sum(row[key] for row in per_salt) / n

    return {
        "K_raw": K_raw,
        "K_eff_per_salt": per_salt,
        "K_eff_mean_per_rule_type": mean,
        "n_salts": n,
    }


def run() -> dict:
    out = {"rule_types": list(RULE_TYPES), "batches": {}}
    for bid in BATCH_LEDGER:
        out["batches"][bid] = k_eff_for_batch(bid)
    out["methodology_note"] = (
        "K_eff per rule_type per salt = number of rules that would NOT "
        "trigger any coherence-gate coercion given the OTHER rule_types' "
        "actual chosen picks. Only arrangement (c1, c3) and harmonic (c2) "
        "can be constrained by the gate; form/melodic/rhythmic K_eff = K_raw."
    )
    return out


def _write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


def _write_tsv(path: pathlib.Path, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["batch_id\trule_type\tK_raw\tK_eff_mean\tK_eff_over_K_raw\n"]
    for bid in sorted(summary["batches"]):
        b = summary["batches"][bid]
        K_raw = b["K_raw"]
        K_eff = b["K_eff_mean_per_rule_type"]
        for rt in RULE_TYPES:
            kr = K_raw[rt]
            ke = K_eff[rt]
            ratio = (ke / kr) if kr else 0.0
            lines.append(f"{bid}\t{rt}\t{kr}\t{ke:.6f}\t{ratio:.6f}\n")
    with path.open("w") as fh:
        fh.writelines(lines)


if __name__ == "__main__":  # pragma: no cover
    summary = run()
    _write_json(pathlib.Path("data/collision_model/effective_k_summary.json"), summary)
    _write_tsv(pathlib.Path("data/collision_model/effective_k_per_batch.tsv"), summary)
    print("effective-K probe complete; batches analyzed:", len(summary["batches"]))
