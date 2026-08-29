#!/usr/bin/env python3
"""Emit ≥10 planted-invalid palette assignment instances covering ≥8 distinct
rejection classes. Deterministic; no PRNG."""

import copy
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette.provenance import compute_assignment_id  # noqa: E402


PLANTED_DIR = _HERE / "planted_invalid"


def _base_valid() -> dict:
    row = {
        "schema_v": "palette_v1",
        "stem": "bass",
        "instrument": "sfizz",
        "pinned_state": {
            "plugin_name": "sfizz",
            "plugin_version": "1.2.3",
            "parameter_dict": {
                "sample_path": "presets/palette/base.sfz",
                "amp_velocity": 0.9,
            },
        },
        "provenance_pointers": ["rule_0271c7a9f3b5f606"],
        "extractor_version": "palette_v1_c31",
    }
    row["assignment_id"] = compute_assignment_id(row)
    return row


def build():
    PLANTED_DIR.mkdir(parents=True, exist_ok=True)
    invalid_specs = []

    # Class 1: missing assignment_id.
    r = _base_valid()
    del r["assignment_id"]
    invalid_specs.append(("01_missing_assignment_id.json", r,
                          "missing_assignment_id", "assignment_id"))

    # Class 2: malformed assignment_id (non-hex).
    r = _base_valid()
    r["assignment_id"] = "not-a-hex-string!!!!!!!!!!!!!!!!"
    invalid_specs.append(("02_malformed_assignment_id_nonhex.json", r,
                          "malformed_assignment_id", "assignment_id"))

    # Class 3: wrong stem (not in enum).
    r = _base_valid()
    r["stem"] = "vocals"
    r["assignment_id"] = compute_assignment_id(r)
    invalid_specs.append(("03_wrong_stem_enum.json", r,
                          "wrong_stem", "stem"))

    # Class 4: wrong instrument (not in enum).
    r = _base_valid()
    r["instrument"] = "moog_minimoog"
    r["assignment_id"] = compute_assignment_id(r)
    invalid_specs.append(("04_wrong_instrument_enum.json", r,
                          "wrong_instrument", "instrument"))

    # Class 5: 63-char hex external_state_sha_optional.
    r = _base_valid()
    r["pinned_state"]["external_state_sha_optional"] = "a" * 63
    r["assignment_id"] = compute_assignment_id(r)
    invalid_specs.append(("05_external_state_sha_63hex.json", r,
                          "external_state_sha_63hex", "external_state_sha_optional"))

    # Class 6: pinned_state has an extra top-level key.
    r = _base_valid()
    r["pinned_state"]["unknown_field"] = "surprise"
    r["assignment_id"] = compute_assignment_id(r)
    invalid_specs.append(("06_pinned_state_extra_key.json", r,
                          "pinned_state_extra_key", "unknown_field"))

    # Class 7: assignment_id mismatch (present but wrong hash).
    r = _base_valid()
    # Force a wrong id: use uuid5 of a different string.
    r["assignment_id"] = "deadbeefdeadbeefdeadbeefdeadbeef"
    invalid_specs.append(("07_assignment_id_mismatch.json", r,
                          "assignment_id_mismatch", "assignment_id"))

    # Class 8: provenance_pointers with unresolvable rule_id.
    r = _base_valid()
    r["provenance_pointers"] = ["rule_ffffffffffffffff"]  # 16 hex, not in ledger
    r["assignment_id"] = compute_assignment_id(r)
    invalid_specs.append(("08_provenance_unresolvable.json", r,
                          "provenance_unresolvable", "provenance_pointers"))

    # Class 9: Dexed × drums combo.
    r = _base_valid()
    r["stem"] = "drums"
    r["instrument"] = "dexed"
    r["pinned_state"] = {
        "plugin_name": "Dexed",
        "plugin_version": "0.9.6",
        "parameter_dict": {"Algorithm": 5},
    }
    r["provenance_pointers"] = ["rule_0271c7a9f3b5f606"]
    r["assignment_id"] = compute_assignment_id(r)
    invalid_specs.append(("09_dexed_drums_skip.json", r,
                          "dexed_drums_skip", "instrument"))

    # Class 10: duplicate assignment_id — batch-level. Ship two rows with
    # colliding ids by manually forcing the same id string.
    r_a = _base_valid()
    r_b = _base_valid()
    r_b["notes_optional"] = "different note"  # notes excluded from hash, so id matches r_a
    # Both r_a and r_b now share the same assignment_id since notes are
    # excluded — this is the DUPLICATE scenario. Write them under a
    # sub-directory so validate_all knows they form a batch.
    invalid_specs.append(("10a_duplicate_assignment_id.json", r_a,
                          "duplicate_assignment_id", "assignment_id"))
    invalid_specs.append(("10b_duplicate_assignment_id.json", r_b,
                          "duplicate_assignment_id", "assignment_id"))

    total = 0
    for fname, row, class_label, offending_field in invalid_specs:
        outpath = PLANTED_DIR / fname
        with open(outpath, "w") as f:
            json.dump({
                "_planted_class": class_label,
                "_offending_field": offending_field,
                "row": row,
            }, f, sort_keys=True, indent=2)
            f.write("\n")
        total += 1
    print(f"Wrote {total} planted-invalid instances into {PLANTED_DIR}")
    # Confirm ≥8 distinct classes.
    classes = {spec[2] for spec in invalid_specs}
    assert len(classes) >= 8, f"only {len(classes)} distinct classes"
    print(f"Distinct rejection classes: {len(classes)}")


if __name__ == "__main__":
    build()
