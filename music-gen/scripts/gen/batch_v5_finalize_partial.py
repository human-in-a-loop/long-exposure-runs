#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T22:30:00Z
# cycle: 23
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 3fbd8c1ab57c)
# milestone: M-GEN-1/batch-v5-n16
# ---
"""Build partial batch-v5 manifest after the I4 sampler exhausts at salt=15.

Cycle-23 first-class finding: the I4 stratified rejection sampler
raises I4SamplerError at salt=15 on rule_type=form because K_form=15
and all 15 form rules have been consumed by salts 0..14's
`already_picked` exclusion set. Salts 0..14 (N=15) rendered
successfully in both run 1 (default) and run 2 (tmp dir) with
identical SHAs and identical failure at salt=15. This directly
demonstrates the cycle-14 construction proof: at N > K per rule_type,
the I4 exclusion mechanism converts pigeonhole collision into
sampler exhaustion.

Emits (in each of run 1 and run 2 roots):
    batch_manifest_partial.json   -- salts 0..14 SHAs + failure record
    anchor_regression.json         -- salts 0..7 vs batch_v4 (32/32)
    determinism_run1_vs_run2.json  -- salts 0..14 SHA-agreement
    hypothesis_verdict.json        -- NOT_TESTABLE_SAMPLER_EXHAUSTS + interpretation
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
V5_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v5_n16"
V5_RUN2_ROOT = _REPO / "tools" / "tmp_batch_v5_run2"
V4_MANIFEST = _REPO / "data" / "gen" / "batch_v4" / "batch_manifest.json"

FILE_KINDS = ("musicxml", "midi", "bare_wav", "effects_wav")
FILE_NAMES = {
    "musicxml": "generated.musicxml",
    "midi": "generated.mid",
    "bare_wav": "bare_midi.wav",
    "effects_wav": "effects_layered.wav",
}
RENDERED_SALTS = tuple(range(15))  # 0..14 succeeded; 15 exhausted.
FAILED_SALT = 15
FAILED_RULE_TYPE = "form"
FAILED_K = 15


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_partial_manifest(batch_root: Path, label: str) -> Dict:
    per_song = []
    for s in RENDERED_SALTS:
        sd = batch_root / f"song_{s}"
        sha = {}
        for fk, fn in FILE_NAMES.items():
            p = sd / fn
            if not p.is_file():
                raise SystemExit(f"missing {p}")
            sha[fk] = _sha256(p)
        # Try to include rule ids where available.
        sm_path = sd / "sampling_manifest.json"
        raw = coerced = None
        if sm_path.is_file():
            sm = json.loads(sm_path.read_text())
            raw = sm.get("raw_rule_ids")
            coerced = sm.get("chosen_rule_ids")
        per_song.append({
            "salt": s,
            "sha": sha,
            "raw_rule_ids": raw,
            "coerced_rule_ids": coerced,
        })

    manifest = {
        "milestone": "M-GEN-1/batch-v5-n16",
        "label": label,
        "target_n_salts": 16,
        "salts_rendered": list(RENDERED_SALTS),
        "n_rendered": len(RENDERED_SALTS),
        "sampler_failure": {
            "salt": FAILED_SALT,
            "rule_type": FAILED_RULE_TYPE,
            "K_for_rule_type": FAILED_K,
            "exception_class": "scripts.rules.sampling.i4_stratified.I4SamplerError",
            "message": (
                "I4 stratified rejection sampler exhausted rule_type=form "
                "at salt=15: 15 candidates, 15 already picked. "
                "This is a FAIL of the intervention as specified."
            ),
            "source_line": "scripts/rules/sampling/i4_stratified.py:127-133",
            "cause": (
                "The I4 sampler's cumulative already_picked exclusion set "
                "removes every rule_id sampled at prior salts. After salts "
                "0..14, all 15 form rules are excluded; salt=15 has zero "
                "candidates. Same holds for K=15 rule_types (arrangement, "
                "rhythmic, melodic) at N=16 by symmetry -- form is only "
                "the FIRST to fail in RULE_TYPES declaration order."
            ),
        },
        "per_song": per_song,
        "K_distribution": {
            "harmonic": 20,
            "rhythmic": 15,
            "melodic": 15,
            "form": 15,
            "arrangement": 15,
        },
    }
    return manifest


def _anchor_regression(v5_manifest: Dict) -> Dict:
    v4 = json.loads(V4_MANIFEST.read_text())
    v4_by_salt = {int(r["salt"]): r["sha"] for r in v4["per_song"]}
    v5_by_salt = {int(r["salt"]): r["sha"] for r in v5_manifest["per_song"]}

    rows = []
    n_pass = n_fail = 0
    for s in range(8):
        for fk in FILE_KINDS:
            a = v4_by_salt[s][fk]
            b = v5_by_salt[s][fk]
            ok = (a == b)
            n_pass += ok
            n_fail += (not ok)
            rows.append({
                "salt": s, "file_kind": fk,
                "batch_v4_sha256": a, "batch_v5_sha256": b,
                "verdict": "PASS" if ok else "FAIL",
            })
    return {
        "n_cells": len(rows),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "all_pass": n_fail == 0,
        "rows": rows,
    }


def _determinism_check(run1: Dict, run2: Dict) -> Dict:
    r1 = {int(r["salt"]): r["sha"] for r in run1["per_song"]}
    r2 = {int(r["salt"]): r["sha"] for r in run2["per_song"]}

    rows = []
    n_pass = n_fail = 0
    for s in sorted(r1):
        for fk in FILE_KINDS:
            a = r1[s][fk]
            b = r2[s][fk]
            ok = (a == b)
            n_pass += ok
            n_fail += (not ok)
            rows.append({
                "salt": s, "file_kind": fk,
                "run1_sha256": a, "run2_sha256": b,
                "verdict": "PASS" if ok else "FAIL",
            })
    return {
        "n_cells": len(rows),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "all_pass": n_fail == 0,
        "note": (
            "Byte-determinism proof for salts 0..14 across two independent "
            "runs of scripts/gen/batch_v5_n16.py. Both runs also failed "
            "identically at salt=15 with I4SamplerError on rule_type=form."
        ),
        "rows": rows,
    }


def _hypothesis_verdict(v5_manifest: Dict,
                        anchor: Dict,
                        determinism: Dict,
                        coll_partial: Dict) -> Dict:
    return {
        "target_N": 16,
        "N_actually_rendered": len(RENDERED_SALTS),
        "verdict": "NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K",
        # Schema-compatibility fields for cross-branch integration test §33g.
        # These reflect the partial N=15 batch (see collision_analysis_partial_N15).
        "observed_pairs": int(coll_partial["total_pairs"]),
        "attribution": {rt: int(coll_partial["primary_histogram_tiebreak"][rt])
                        for rt in ("harmonic", "rhythmic", "melodic", "form",
                                   "arrangement")},
        "attribution_any_rt": {rt: int(coll_partial["histogram_any_rt"][rt])
                               for rt in ("harmonic", "rhythmic", "melodic",
                                          "form", "arrangement")},
        "form_arrangement_fraction": float(
            coll_partial["form_arrangement_primary_fraction"]),
        "N": 15,  # actual N rendered; target N=16 in target_N.
        "note": (
            "The I4 stratified rejection sampler exhausts at salt=15 on "
            "rule_type=form: with K_form=15, all 15 form rules are excluded "
            "after salts 0..14, leaving zero candidates for salt=15. Because "
            "the sampler is a load-bearing pre-existing artifact and MUST "
            "NOT be modified (research brief §Standing anti-patterns), the "
            "cycle-14 construction proof is NOT DIRECTLY TESTABLE at N=16 "
            "via the pigeonhole-collision-count rubric using this sampler. "
            "However, the exhaustion is itself a positive empirical "
            "manifestation of the construction proof: at N > K per "
            "rule_type, the I4 exclusion mechanism converts the pigeonhole "
            "floor from `must-collide` into `cannot-sample`. Same holds for "
            "the other three K=15 rule_types (arrangement, rhythmic, "
            "melodic) at N=16 by symmetry."
        ),
        "sampler_exhaustion": v5_manifest["sampler_failure"],
        "anchor_regression": {
            "n_cells": anchor["n_cells"],
            "n_pass": anchor["n_pass"],
            "n_fail": anchor["n_fail"],
            "all_pass": anchor["all_pass"],
        },
        "byte_determinism_x2": {
            "n_cells": determinism["n_cells"],
            "n_pass": determinism["n_pass"],
            "all_pass": determinism["all_pass"],
        },
        "collision_analysis_partial_N15": coll_partial,
        "frozen_rubric": {
            "CONFIRMS_CONSTRUCTION": ">=0.90 fraction pairs in {form, arrangement}",
            "PARTIAL_CONFIRM": "[0.60, 0.90)",
            "CONFIRMS_H2_LARGER": "<0.60",
            "NULL_RESULT_NO_COLLISIONS_AT_N16": "total_pairs == 0",
            "NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K": (
                "sampler raises before N=16 can be reached"),
        },
        "cycle_24_recommendation": (
            "Two orthogonal paths to test the pigeonhole prediction at "
            "N>K: (a) implement a range-extensible variant of the I4 "
            "sampler (e.g., allow repeats past N=K with an explicit "
            "collision-recording branch) as a NEW sibling module -- do NOT "
            "touch scripts/rules/sampling/i4_stratified.py; (b) run the "
            "N=16 test with the UNCONDITIONED sampler "
            "(scripts/rules/sampling/sample_rules.py) which permits "
            "collisions -- this is the direct test of the pigeonhole "
            "prediction and would produce a testable pair count."
        ),
    }


def _collision_analysis_partial(batch_root: Path) -> Dict:
    """Compute collision analysis on the N=15 partial batch as a bonus finding."""
    RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
    salts = list(RENDERED_SALTS)
    coerced: Dict[int, Dict[str, str]] = {}
    for s in salts:
        sm = json.loads((batch_root / f"song_{s}" / "sampling_manifest.json").read_text())
        coerced[s] = sm["chosen_rule_ids"]

    total_pairs = 0
    primary: Dict[str, int] = {rt: 0 for rt in RULE_TYPES}
    any_hist: Dict[str, int] = {rt: 0 for rt in RULE_TYPES}
    for i, si in enumerate(salts):
        for j, sj in enumerate(salts):
            if i >= j:
                continue
            matches = {rt: coerced[si][rt] == coerced[sj][rt] for rt in RULE_TYPES}
            if not any(matches.values()):
                continue
            total_pairs += 1
            for rt in RULE_TYPES:
                if matches[rt]:
                    any_hist[rt] += 1
            for rt in RULE_TYPES:
                if matches[rt]:
                    primary[rt] += 1
                    break

    form_arr = primary["form"] + primary["arrangement"]
    frac = (form_arr / total_pairs) if total_pairs else 0.0
    return {
        "N_partial": len(salts),
        "total_pairs": total_pairs,
        "primary_histogram_tiebreak": primary,
        "histogram_any_rt": any_hist,
        "form_arrangement_primary_fraction": frac,
        "interpretation": (
            "At N=15, the I4 sampler produces exactly one rule per "
            "rule_type without repetition (K>=15 for every rule_type). "
            "Zero within-rule_type collisions is the DEFINITION of a "
            "stratified rejection sampler operating within its "
            "K-envelope. The observation confirms the sampler behaves "
            "as designed at N<=K for every rule_type."
            if total_pairs == 0 else
            "Non-zero collision pairs at N=15 requires investigation."
        ),
    }


def _main(argv):
    for root, label in ((V5_BATCH_ROOT, "run1_default_dir"),
                        (V5_RUN2_ROOT, "run2_tmp_dir")):
        if not root.is_dir():
            print(f"[WARN] {root} not found; skipping.")
            continue
        m = _build_partial_manifest(root, label)
        (root / "batch_manifest_partial.json").write_text(
            json.dumps(m, indent=2, sort_keys=True))
        print(f"[WROTE] {root/'batch_manifest_partial.json'}")

    m1 = json.loads((V5_BATCH_ROOT / "batch_manifest_partial.json").read_text())
    m2 = json.loads((V5_RUN2_ROOT / "batch_manifest_partial.json").read_text())

    anchor = _anchor_regression(m1)
    (V5_BATCH_ROOT / "anchor_regression.json").write_text(
        json.dumps(anchor, indent=2, sort_keys=True))
    print(f"[anchor_regression] {anchor['n_pass']}/{anchor['n_cells']} PASS "
          f"({anchor['n_fail']} FAIL)")

    determinism = _determinism_check(m1, m2)
    (V5_BATCH_ROOT / "determinism_run1_vs_run2.json").write_text(
        json.dumps(determinism, indent=2, sort_keys=True))
    print(f"[determinism_x2] {determinism['n_pass']}/{determinism['n_cells']} PASS "
          f"({determinism['n_fail']} FAIL)")

    coll_partial = _collision_analysis_partial(V5_BATCH_ROOT)
    (V5_BATCH_ROOT / "collision_analysis_partial_N15.json").write_text(
        json.dumps(coll_partial, indent=2, sort_keys=True))
    print(f"[collision_analysis_partial_N15] pairs={coll_partial['total_pairs']}")

    verdict = _hypothesis_verdict(m1, anchor, determinism, coll_partial)
    (V5_BATCH_ROOT / "hypothesis_verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True))
    print(f"[verdict] {verdict['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
