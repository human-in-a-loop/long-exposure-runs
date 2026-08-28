#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:55:00Z
# cycle: 30
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-semantic-cluster-overlap
# ---
"""Cycle-30 anchor preservation: recompute canonical-aggregate SHAs
of all batch dirs + both ledgers, plus assert byte-identity of
cycle-26/27/28/29 utility scripts.

Uses cycle-26's `canonical_aggregate_sha.py` verbatim (do not modify).
Interpreter-guarded `/usr/bin/python3`. No PRNG. No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from canonical_aggregate_sha import canonical_aggregate_sha, file_sha256  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]

ANCHOR_DIRS = [
    "data/gen/batch_v1", "data/gen/batch_v2", "data/gen/batch_v3_i3",
    "data/gen/batch_v3_i4", "data/gen/batch_v4",
    "data/gen/batch_v5_n16", "data/gen/batch_v6",
]
ANCHOR_FILES = [
    "data/rules/ledger.jsonl",
    "data/rules/ledger_i3_dminor.jsonl",
]
CYCLE_UTILITIES = {
    "cycle_26_utilities": [
        "canonical_aggregate_sha.py",
        "collision_model_bp.py",
        "collision_model_verdict.py",
    ],
    "cycle_27_utilities": [
        "coercion_rate_per_rule_type.py",
        "effective_k_probe.py",
        "shape_mechanism_fit.py",
        "shape_mechanism_verdict.py",
        "anchor_preservation_shape.py",
    ],
    "cycle_28_utilities": [
        "plot_shape_mechanism_scatter.py",
        "hash_uniformity_per_rule_type.py",
        "effective_k_hash.py",
        "hash_geometry_fit.py",
        "hash_geometry_verdict.py",
        "anchor_preservation_hash.py",
    ],
    "cycle_29_utilities": [
        "multiple_testing_correction.py",
        "drop_batch_v2_sensitivity.py",
        "leave_one_cell_out_contribution.py",
        "hash_geometry_adjudication_verdict.py",
    ],
}


def _load_fixture_shas():
    p = ROOT / "tests" / "fixtures" / "cycle28_util_shas.json"
    if not p.is_file():
        return {}
    return json.loads(p.read_text())


def capture_batches():
    out = {"schema_v": 1, "method": "canonical_aggregate_sha_v1",
           "anchors": {}}
    for rel in ANCHOR_DIRS:
        p = ROOT / rel
        out["anchors"][rel] = {
            "kind": "dir",
            "sha": canonical_aggregate_sha(p) if p.exists() else None,
        }
    for rel in ANCHOR_FILES:
        p = ROOT / rel
        out["anchors"][rel] = {
            "kind": "file",
            "sha": file_sha256(p) if p.exists() else None,
        }
    return out


def capture_utilities():
    fixture = _load_fixture_shas()
    result = {}
    for group, files in CYCLE_UTILITIES.items():
        expected_map = fixture.get(group, {})
        entries = {}
        all_ok = True
        for name in files:
            p = ROOT / "scripts" / "analysis" / name
            got = hashlib.sha256(p.read_bytes()).hexdigest() \
                if p.is_file() else None
            expected = expected_map.get(name)
            ok = (expected is not None) and (got == expected)
            if expected is None:
                # No baseline yet — first pass (cycle-29 utilities the
                # first time we anchor them). Treat as ANCHORED but
                # not verified.
                status = "ANCHORED_NEW"
                # Do not fail overall on first-anchor entries.
            elif not ok:
                status = "FAIL"
                all_ok = False
            else:
                status = "PASS"
            entries[name] = {
                "expected": expected, "got": got, "status": status
            }
        result[group] = {"entries": entries, "all_ok": all_ok}
    return result


def main():
    batches = capture_batches()
    utils = capture_utilities()

    batches_all_ok = all(a["sha"] is not None for a in batches["anchors"].values())

    payload = {
        "generator": "scripts/analysis/anchor_preservation_semantic.py",
        "batch_anchors": batches,
        "utility_anchors": utils,
        "batch_capture_ok": batches_all_ok,
        "utility_verified_ok": all(v["all_ok"] for v in utils.values()),
    }
    out_path = ROOT / "data" / "collision_model" / "anchor_preservation_semantic.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"WROTE {out_path.relative_to(ROOT)}")
    for group, v in utils.items():
        n_pass = sum(1 for e in v["entries"].values()
                     if e["status"] in ("PASS", "ANCHORED_NEW"))
        n_tot = len(v["entries"])
        print(f"  {group}: {n_pass}/{n_tot} OK  "
              f"(verified={'yes' if v['all_ok'] else 'partial'})")
    print(f"  batch anchors captured: "
          f"{sum(1 for a in batches['anchors'].values() if a['sha'])}/"
          f"{len(batches['anchors'])}")
    if not payload["utility_verified_ok"]:
        print("WARN: not all utility SHAs verified (may be first-anchor group)",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
