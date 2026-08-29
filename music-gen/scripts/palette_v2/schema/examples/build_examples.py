#!/usr/bin/env python3
"""Deterministic builder — palette_v2 valid + planted-invalid example instances.

SHA-256 tiebreak, NO PRNG. Emits:
  - ≥16 valid v2 instances (4 stems × {surge_xt,dexed} × 2 = 16)
  - 8 planted-invalid instances (one per rejection class in rubric §5)

Determinism proof: two independent runs into fresh tempdirs produce
byte-identical output when copied to the same path.

Interpreter-guarded /usr/bin/python3.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3"

_REPO = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from scripts.palette_v2.provenance import (  # noqa: E402
    compute_assignment_id_v2,
    canonical_json_iterated_params,
    sha256_iterated_params,
    known_rule_ids,
    anchor_iterated_params,
)

_HERE = Path(__file__).resolve().parent

_STEMS = ("drums", "bass", "other", "mono")
_VST3 = ("surge_xt", "dexed")

# Anchor plugin_version manifest (mirrors provenance._ANCHOR_PLUGIN_VERSIONS)
_ANCHOR_VERSIONS = {"surge_xt": "1.3.4", "dexed": "0.9.9"}


def _tiebreak_pick(items, n, seed_str):
    """SHA-256 tiebreak — pick n items from items deterministically."""
    keyed = [(hashlib.sha256((seed_str + ":" + str(x)).encode()).hexdigest(), x)
             for x in items]
    keyed.sort()
    return [x for _, x in keyed[:n]]


def _load_anchor_params(plugin_name):
    """Return the FULL c33 P1-output param dict {name: value}."""
    path = _REPO / "data" / "dawdreamer_state" / "per_plugin" / plugin_name / "p1_state_v2.json"
    with open(path, "r") as f:
        return json.load(f)


def _build_v2_iterated_pinned_state(plugin_name, seed_str):
    """Build a v2_iterated_params pinned_state using the full anchor param set.
    Values come straight from the anchor (byte-deterministic per plugin)."""
    params = _load_anchor_params(plugin_name)
    iter_size = len(params)
    iter_sha = sha256_iterated_params(params)
    return {
        "format": "v2_iterated_params",
        "plugin_name": plugin_name,
        "plugin_version": _ANCHOR_VERSIONS[plugin_name],
        "iterated_params": params,
        "iteration_size": iter_size,
        "iteration_sha_256": iter_sha,
    }


def _build_valid_row(stem, plugin_name, salt_idx, all_rule_ids):
    """Build one valid v2_iterated_params row for VST3 plugin."""
    seed = f"palette_v2::{stem}::{plugin_name}::{salt_idx}"
    picked = _tiebreak_pick(sorted(all_rule_ids), 2, seed)
    pointers = sorted(picked)
    pinned = _build_v2_iterated_pinned_state(plugin_name, seed)
    row = {
        "schema_v": "palette_v2",
        "stem": stem,
        "instrument": plugin_name,
        "pinned_state": pinned,
        "provenance_pointers": pointers,
        "extractor_version": "palette_v2_c34",
    }
    row["assignment_id_v2"] = compute_assignment_id_v2(row)
    return row


def build_valid_instances(out_root=None):
    """≥16 valid instances: 4 stems × 2 VST3 plugins × 2 salts = 16 rows."""
    out_root = Path(out_root) if out_root else _HERE
    all_rule_ids = sorted(known_rule_ids())
    if len(all_rule_ids) < 2:
        raise RuntimeError(f"insufficient rule_ids in ledgers: {len(all_rule_ids)}")
    written = []
    for stem in _STEMS:
        stem_dir = out_root / stem
        stem_dir.mkdir(parents=True, exist_ok=True)
        for plugin in _VST3:
            for salt in (1, 2):
                row = _build_valid_row(stem, plugin, salt, all_rule_ids)
                aid = row["assignment_id_v2"]
                fname = f"{stem}_{plugin}_{salt:02d}_{aid[:12]}.json"
                fpath = stem_dir / fname
                with open(fpath, "w") as f:
                    json.dump(row, f, indent=2, sort_keys=True)
                    f.write("\n")
                written.append(fpath)
    return written


def build_planted_invalid(out_root=None):
    """Emit exactly 8 planted-invalid instances covering rubric §5 classes."""
    out_root = Path(out_root) if out_root else _HERE
    inv_dir = out_root / "planted_invalid"
    inv_dir.mkdir(parents=True, exist_ok=True)
    all_rule_ids = sorted(known_rule_ids())
    good_ptr = sorted(_tiebreak_pick(all_rule_ids, 2, "invalid_seed"))
    surge_pinned = _build_v2_iterated_pinned_state("surge_xt", "invalid::surge")

    written = []

    # 1. missing_format_discriminator — pinned_state without 'format'
    bad = {
        "schema_v": "palette_v2",
        "assignment_id_v2": "00000000000000000000000000000001",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": {
            # 'format' missing
            "plugin_name": "surge_xt",
            "plugin_version": "1.3.4",
            "parameter_dict": {"cutoff": 0.5},
        },
        "provenance_pointers": good_ptr,
        "extractor_version": "palette_v2_c34",
    }
    fpath = inv_dir / "01_missing_format_discriminator.json"
    fpath.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
    written.append(fpath)

    # 2. v2_iterated_with_v1_fields — format=v2_iterated_params + parameter_dict
    bad_ps = dict(surge_pinned)
    bad_ps["parameter_dict"] = {"cutoff": 0.5}
    bad = {
        "schema_v": "palette_v2",
        "assignment_id_v2": "00000000000000000000000000000002",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": bad_ps,
        "provenance_pointers": good_ptr,
        "extractor_version": "palette_v2_c34",
    }
    fpath = inv_dir / "02_v2_iterated_with_v1_fields.json"
    fpath.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
    written.append(fpath)

    # 3. iterated_params_key_set_mismatch — extra bogus key
    params = dict(_load_anchor_params("surge_xt"))
    params["99999:BOGUS_KEY"] = 0.42  # not in anchor
    bad_ps = {
        "format": "v2_iterated_params",
        "plugin_name": "surge_xt",
        "plugin_version": "1.3.4",
        "iterated_params": params,
        "iteration_size": len(params),
        "iteration_sha_256": sha256_iterated_params(params),
    }
    bad = {
        "schema_v": "palette_v2",
        "assignment_id_v2": "00000000000000000000000000000003",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": bad_ps,
        "provenance_pointers": good_ptr,
        "extractor_version": "palette_v2_c34",
    }
    fpath = inv_dir / "03_iterated_params_key_set_mismatch.json"
    fpath.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
    written.append(fpath)

    # 4. iteration_sha_256_mismatch — wrong SHA
    bad_ps = dict(surge_pinned)
    bad_ps["iteration_sha_256"] = "0" * 64
    bad = {
        "schema_v": "palette_v2",
        "assignment_id_v2": "00000000000000000000000000000004",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": bad_ps,
        "provenance_pointers": good_ptr,
        "extractor_version": "palette_v2_c34",
    }
    fpath = inv_dir / "04_iteration_sha_256_mismatch.json"
    fpath.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
    written.append(fpath)

    # 5. plugin_version_mismatch
    bad_ps = dict(surge_pinned)
    bad_ps["plugin_version"] = "9.9.9"
    bad = {
        "schema_v": "palette_v2",
        "assignment_id_v2": "00000000000000000000000000000005",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": bad_ps,
        "provenance_pointers": good_ptr,
        "extractor_version": "palette_v2_c34",
    }
    fpath = inv_dir / "05_plugin_version_mismatch.json"
    fpath.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
    written.append(fpath)

    # 6. unknown_plugin_name — v2_iterated_params variant with plugin_name
    #    not in {surge_xt, dexed, sfizz, fluidsynth_gm}. Layer 2 §6 rejects.
    bad_ps = dict(surge_pinned)
    bad_ps["plugin_name"] = "foobar"
    bad = {
        "schema_v": "palette_v2",
        "assignment_id_v2": "00000000000000000000000000000006",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": bad_ps,
        "provenance_pointers": good_ptr,
        "extractor_version": "palette_v2_c34",
    }
    fpath = inv_dir / "06_unknown_plugin_name.json"
    fpath.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
    written.append(fpath)

    # 7. provenance_pointer_not_found — bogus rule_id
    bad = {
        "schema_v": "palette_v2",
        "assignment_id_v2": "00000000000000000000000000000007",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": surge_pinned,
        "provenance_pointers": ["rule_deadbeefdeadbeef"],
        "extractor_version": "palette_v2_c34",
    }
    fpath = inv_dir / "07_provenance_pointer_not_found.json"
    fpath.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
    written.append(fpath)

    # 8. provenance_pointer_unsorted — reverse-sorted good ptrs
    unsorted_ptrs = sorted(good_ptr, reverse=True)
    if unsorted_ptrs == sorted(good_ptr):
        # in case sort was already reversed; pick two distinct ids and reverse
        unsorted_ptrs = list(reversed(_tiebreak_pick(all_rule_ids, 3, "unsorted_seed")))
    bad = {
        "schema_v": "palette_v2",
        "assignment_id_v2": "00000000000000000000000000000008",
        "stem": "mono",
        "instrument": "surge_xt",
        "pinned_state": surge_pinned,
        "provenance_pointers": unsorted_ptrs,
        "extractor_version": "palette_v2_c34",
    }
    fpath = inv_dir / "08_provenance_pointer_unsorted.json"
    fpath.write_text(json.dumps(bad, indent=2, sort_keys=True) + "\n")
    written.append(fpath)

    return written


def main():
    valid = build_valid_instances()
    invalid = build_planted_invalid()
    print(f"valid: {len(valid)}")
    print(f"invalid: {len(invalid)}")


if __name__ == "__main__":
    main()
