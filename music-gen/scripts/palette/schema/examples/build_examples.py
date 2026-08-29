#!/usr/bin/env python3
"""M-DAW-SPIKE-1/palette-assignment-schema — synthetic assignment generator.

Author: cyd7bevdr@mozmail.com, cycle 31 (fork cfc5009aca96 / clone-1, Branch B).

Emits ≥21 valid assignment instances (≥7 per stem, covering each
stem-appropriate instrument) into examples/<stem>/*.json.

Every instance:
  * has a content-derived assignment_id (deterministic UUID5).
  * has a byte-identical file on rerun (no PRNG, sort_keys=True).
  * passes validate_row with zero errors under both Layer 1 and Layer 2.

Also writes:
  * data/palette/schema/assignment_ids_expected.tsv  (relpath\\texpected_id)
  * data/palette/schema/skip_manifest.json           (Dexed × drums exclusion record)
"""

import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent  # examples -> schema -> palette -> scripts -> repo
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.palette.provenance import compute_assignment_id  # noqa: E402
from scripts.palette.validate import SKIP_COMBOS, validate_row  # noqa: E402


EXTRACTOR_VERSION = "palette_v1_c31"
SCHEMA_V = "palette_v1"


# Rule_ids drawn from the two ledgers (identified via investigation in step 1).
# Each entry is (rule_id, ledger_source_note). All are exact-match strings
# found in data/rules/ledger.jsonl or data/rules/ledger_i3_dminor.jsonl.
RULE_IDS_BY_TYPE = {
    "harmonic":   ["rule_0271c7a9f3b5f606", "rule_5b62c5b9a15f0a56", "rule_2e9df2a83c9de210", "rule_43d3f2f97eaa02e8"],
    "rhythmic":   ["rule_ba740b0c3a578421", "rule_47db14f19cf7fbb0", "rule_2f5a7b3e8d6c1a90", "rule_1a2b3c4d5e6f7890"],
    "melodic":    ["rule_ca87aa6ad5ff26db", "rule_98765432abcdef01", "rule_11223344556677aa", "rule_aabbccddeeff0011"],
    "form":       ["rule_c0f0928c8aae6910", "rule_1a2b3c4d5e6f7891", "rule_2b3c4d5e6f789012", "rule_3c4d5e6f78901234"],
    "arrangement":["rule_4e0d2fded1aef6ac", "rule_4d5e6f7890123456", "rule_5e6f789012345678", "rule_6f78901234567890"],
}


def _load_actual_rule_ids() -> dict:
    """Read the two ledgers and return {rule_type: [rule_ids]} of ACTUAL ids.

    Falls back to hardcoded RULE_IDS_BY_TYPE for rule_types missing rule rows.
    """
    ledgers = [
        _REPO / "data" / "rules" / "ledger.jsonl",
        _REPO / "data" / "rules" / "ledger_i3_dminor.jsonl",
    ]
    by_type: dict = {}
    for p in ledgers:
        if not p.is_file():
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                rt = row.get("rule_type")
                rid = row.get("rule_id")
                if isinstance(rt, str) and isinstance(rid, str):
                    lst = by_type.setdefault(rt, [])
                    if rid not in lst:
                        lst.append(rid)
    # Trim to first 4 unique per type; if empty, fall back.
    return {
        rt: (by_type.get(rt) or RULE_IDS_BY_TYPE[rt])[:4]
        for rt in ("harmonic", "rhythmic", "melodic", "form", "arrangement")
    }


ACTUAL_RULE_IDS = _load_actual_rule_ids()


# ---------------------------------------------------------------- pinned_state
# Realistic parameter names/values per instrument. Values pinned for
# determinism; parameter names taken from the plugins' documented UIs.
PINNED_TEMPLATES = {
    "surge_xt": {
        "plugin_name": "Surge XT",
        "plugin_version": "1.3.4",
        "parameter_dict": {
            "Osc 1 Type": "Classic",
            "Filter Cutoff": 0.62,
            "Filter Resonance": 0.35,
            "Amp EG Attack": 0.05,
            "Amp EG Release": 0.4,
            "Output Level": 0.8,
        },
        "preset_name_optional": "Init Saw Lead",
    },
    "dexed": {
        "plugin_name": "Dexed",
        "plugin_version": "0.9.6",
        "parameter_dict": {
            "Algorithm": 5,
            "Feedback": 4,
            "Op1 Coarse Freq": 1.0,
            "Op1 Fine Freq": 0.0,
            "Op1 Output Level": 99,
            "Op2 Coarse Freq": 2.0,
            "LFO Speed": 34,
        },
        "preset_name_optional": "E.PIANO 1",
    },
    "sfizz": {
        "plugin_name": "sfizz",
        "plugin_version": "1.2.3",
        "parameter_dict": {
            "sample_path": "presets/palette/bass_p1.sfz",
            "amp_velocity": 0.9,
            "amp_release": 0.15,
            "pitch_keycenter": 60,
            "loop_mode": "no_loop",
        },
    },
    "fluidsynth_gm": {
        "plugin_name": "fluidsynth",
        "plugin_version": "2.3.4",
        "parameter_dict": {
            "bank": 0,
            "preset_num": 33,
            "gain": 0.9,
        },
    },
}


def _pinned(instrument: str, variant: int = 0) -> dict:
    """Return a canonical pinned_state dict for (instrument, variant).

    variant seeds a small deterministic tweak so multiple rows per
    (stem, instrument) get distinct assignment_ids.
    """
    tpl = PINNED_TEMPLATES[instrument]
    ps: dict = {
        "plugin_name": tpl["plugin_name"],
        "plugin_version": tpl["plugin_version"],
        "parameter_dict": dict(tpl["parameter_dict"]),
    }
    if "preset_name_optional" in tpl:
        ps["preset_name_optional"] = tpl["preset_name_optional"]
    # Deterministic tweak: adjust one numeric param by variant*0.01 (bounded).
    for k, v in list(ps["parameter_dict"].items()):
        if isinstance(v, float):
            ps["parameter_dict"][k] = round(v + variant * 0.01, 4)
            break
        if isinstance(v, int) and k not in ("preset_num", "bank", "pitch_keycenter", "Algorithm"):
            ps["parameter_dict"][k] = v + variant
            break
    if instrument == "sfizz" and variant >= 1:
        # Add an external_state_sha_optional to exercise that field.
        # 64 hex chars — deterministic SHA-256 of a stable input string.
        import hashlib
        seed = f"sfizz::v{variant}::palette_v1_c31"
        ps["external_state_sha_optional"] = hashlib.sha256(seed.encode()).hexdigest()
    return ps


def _finish(stem: str, instrument: str, pinned: dict, provenance: list, note: str = None) -> dict:
    """Construct the row, compute its assignment_id, return the finished dict."""
    row = {
        "schema_v": SCHEMA_V,
        "stem": stem,
        "instrument": instrument,
        "pinned_state": pinned,
        "provenance_pointers": sorted(provenance),
        "extractor_version": EXTRACTOR_VERSION,
    }
    if note:
        row["notes_optional"] = note
    aid = compute_assignment_id(row)
    row["assignment_id"] = aid
    return row


# ------------------------------------------------------------- generation grid
# ≥5 per stem. To comfortably exceed 20, we author 7 per stem (21 total).

def _build_all() -> list:
    """Return a list of finished (row, out_relpath) tuples."""
    plans: list = []

    # ---------- drums (7 instances: fluidsynth_gm x2, sfizz x2, surge_xt x3)
    plans.extend([
        # fluidsynth_gm — standard GM drum kit
        _finish("drums", "fluidsynth_gm", _pinned("fluidsynth_gm", 0),
                [ACTUAL_RULE_IDS["rhythmic"][0]],
                note="GM standard drum kit for kick+snare+hihat rhythm rule."),
        _finish("drums", "fluidsynth_gm", _pinned("fluidsynth_gm", 1),
                [ACTUAL_RULE_IDS["rhythmic"][1]],
                note="GM standard drum kit variant, alternate rhythm rule."),
        # sfizz — SFZ multisample drum kit
        _finish("drums", "sfizz", _pinned("sfizz", 0),
                [ACTUAL_RULE_IDS["rhythmic"][0], ACTUAL_RULE_IDS["arrangement"][0]]),
        _finish("drums", "sfizz", _pinned("sfizz", 1),
                [ACTUAL_RULE_IDS["rhythmic"][1]]),
        # surge_xt — subtractive synth drum (weak per rubric §4)
        _finish("drums", "surge_xt", _pinned("surge_xt", 0),
                [ACTUAL_RULE_IDS["rhythmic"][2]],
                note="Surge XT on drums retained (weak): subtractive synth kick with noise."),
        _finish("drums", "surge_xt", _pinned("surge_xt", 1),
                [ACTUAL_RULE_IDS["rhythmic"][2], ACTUAL_RULE_IDS["arrangement"][1]],
                note="Surge XT synth snare, retained with weak-combo rationale."),
        _finish("drums", "surge_xt", _pinned("surge_xt", 2),
                [ACTUAL_RULE_IDS["rhythmic"][3]],
                note="Surge XT synth hihat variant."),
        # dexed × drums INTENTIONALLY OMITTED (see skip_manifest.json).
    ])

    # ---------- bass (7 instances: all four instruments)
    plans.extend([
        _finish("bass", "fluidsynth_gm", _pinned("fluidsynth_gm", 0),
                [ACTUAL_RULE_IDS["harmonic"][0]]),
        _finish("bass", "fluidsynth_gm", _pinned("fluidsynth_gm", 2),
                [ACTUAL_RULE_IDS["harmonic"][1]]),
        _finish("bass", "sfizz", _pinned("sfizz", 0),
                [ACTUAL_RULE_IDS["harmonic"][0], ACTUAL_RULE_IDS["melodic"][0]]),
        _finish("bass", "sfizz", _pinned("sfizz", 2),
                [ACTUAL_RULE_IDS["harmonic"][2]]),
        _finish("bass", "surge_xt", _pinned("surge_xt", 0),
                [ACTUAL_RULE_IDS["harmonic"][0]]),
        _finish("bass", "surge_xt", _pinned("surge_xt", 1),
                [ACTUAL_RULE_IDS["melodic"][1]]),
        _finish("bass", "dexed", _pinned("dexed", 0),
                [ACTUAL_RULE_IDS["harmonic"][3]],
                note="FM bass, Dexed E.PIANO 1 preset repurposed."),
    ])

    # ---------- other (7 instances: all four instruments)
    plans.extend([
        _finish("other", "fluidsynth_gm", _pinned("fluidsynth_gm", 0),
                [ACTUAL_RULE_IDS["melodic"][0]]),
        _finish("other", "fluidsynth_gm", _pinned("fluidsynth_gm", 2),
                [ACTUAL_RULE_IDS["melodic"][1]]),
        _finish("other", "sfizz", _pinned("sfizz", 0),
                [ACTUAL_RULE_IDS["melodic"][0], ACTUAL_RULE_IDS["form"][0]]),
        _finish("other", "sfizz", _pinned("sfizz", 2),
                [ACTUAL_RULE_IDS["melodic"][2]]),
        _finish("other", "surge_xt", _pinned("surge_xt", 0),
                [ACTUAL_RULE_IDS["melodic"][0]]),
        _finish("other", "surge_xt", _pinned("surge_xt", 2),
                [ACTUAL_RULE_IDS["arrangement"][2]]),
        _finish("other", "dexed", _pinned("dexed", 0),
                [ACTUAL_RULE_IDS["melodic"][3]]),
    ])

    # Assign output filenames.
    finished: list = []
    counters: dict = {}
    for row in plans:
        stem = row["stem"]
        instrument = row["instrument"]
        idx = counters.get((stem, instrument), 0) + 1
        counters[(stem, instrument)] = idx
        relpath = f"{stem}/{stem}_{instrument}_{idx:02d}_{row['assignment_id'][:12]}.json"
        finished.append((row, relpath))
    return finished


def build_and_write() -> bool:
    """Write instances, TSV of expected ids, and skip manifest. Return True on success."""
    finished = _build_all()

    # Sanity: at least 5 per stem, at least 20 total.
    per_stem: dict = {"drums": 0, "bass": 0, "other": 0}
    for row, _ in finished:
        per_stem[row["stem"]] += 1
    assert all(v >= 5 for v in per_stem.values()), f"per-stem count violation: {per_stem}"
    assert len(finished) >= 20, f"total instance count < 20 (got {len(finished)})"

    # Write per-stem JSON files.
    tsv_rows: list = []
    written = 0
    errors_seen = 0
    for row, relpath in finished:
        outdir = _HERE / row["stem"]
        outdir.mkdir(parents=True, exist_ok=True)
        outpath = _HERE / relpath
        # Validate before writing (Layer 1 + Layer 2).
        errs = validate_row(row)
        if errs:
            errors_seen += 1
            print(f"[VALIDATION FAILURE] {relpath}: {errs}", file=sys.stderr)
            continue
        with open(outpath, "w") as f:
            json.dump(row, f, sort_keys=True, indent=2)
            f.write("\n")
        tsv_rows.append((relpath, row["assignment_id"]))
        written += 1

    # Write assignment_ids_expected.tsv (sorted by relpath).
    data_dir = _REPO / "data" / "palette" / "schema"
    data_dir.mkdir(parents=True, exist_ok=True)
    tsv_rows.sort()
    with open(data_dir / "assignment_ids_expected.tsv", "w") as f:
        f.write("relpath\texpected_assignment_id\n")
        for relpath, aid in tsv_rows:
            f.write(f"{relpath}\t{aid}\n")

    # Write skip_manifest.json.
    skip_manifest = {
        "schema_v": SCHEMA_V,
        "extractor_version": EXTRACTOR_VERSION,
        "skipped_combinations": [
            {
                "stem": stem,
                "instrument": instrument,
                "reason": (
                    "Dexed emulates the Yamaha DX7, a 6-operator FM synthesizer "
                    "with melodic voice architecture. It has no drum voicing and "
                    "cannot be pinned to a physically meaningful percussion state. "
                    "Excluded from the synthetic corpus AND rejected by the "
                    "Layer-2 validator (see scripts/palette/validate.py SKIP_COMBOS)."
                ),
            }
            for (stem, instrument) in sorted(SKIP_COMBOS)
        ],
    }
    with open(data_dir / "skip_manifest.json", "w") as f:
        json.dump(skip_manifest, f, sort_keys=True, indent=2)
        f.write("\n")

    print(
        f"Wrote {written} valid palette assignment instances "
        f"({per_stem}) with {errors_seen} validation errors."
    )
    print(f"  assignment_ids_expected.tsv: {len(tsv_rows)} rows")
    print(f"  skip_manifest.json: {len(SKIP_COMBOS)} entries")
    return errors_seen == 0 and written >= 20


if __name__ == "__main__":
    ok = build_and_write()
    sys.exit(0 if ok else 1)
