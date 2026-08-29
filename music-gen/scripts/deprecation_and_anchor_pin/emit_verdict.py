#!/usr/bin/env /usr/bin/python3
"""Cycle 47 Branch C: emit verdict.json for the combined deprecation +
SOURCE_DATE_EPOCH-pin milestone.

Three-way rubric_hash byte-equality: doc SHA == rubric_hash.txt ==
verdict.json.rubric_hash. Verdict ∈ {DEPRECATION_LANDS_AND_ANCHOR_PINNED,
DEPRECATION_PARTIAL}.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

if not sys.executable.startswith("/usr/bin/python"):
    print(f"[verdict] REFUSE: interpreter {sys.executable!r} is not /usr/bin/python3",
          file=sys.stderr)
    sys.exit(2)

WS = "/home/user/long-exposure-runs/music-gen"
RUBRIC_DOC = os.path.join(WS, "docs/deprecation_and_anchor_pin_rubric.md")
RUBRIC_HASH_TXT = os.path.join(WS, "data/deprecation_and_anchor_pin/rubric_hash.txt")
DEPRECATION_CHECK = os.path.join(WS, "data/deprecation_and_anchor_pin/deprecation_check.json")
SDE_PIN = os.path.join(WS, "data/deprecation_and_anchor_pin/source_date_epoch_pin.json")
DET_CHECK = os.path.join(WS, "data/deprecation_and_anchor_pin/determinism_check.json")
ANCHOR_PRESERVATION = os.path.join(WS, "data/deprecation_and_anchor_pin/anchor_preservation.json")
OUT = os.path.join(WS, "data/deprecation_and_anchor_pin/verdict.json")


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main() -> int:
    doc_sha = sha256_file(RUBRIC_DOC)
    txt_content = open(RUBRIC_HASH_TXT).read().strip()

    dep = json.load(open(DEPRECATION_CHECK))
    sde = json.load(open(SDE_PIN))
    det = json.load(open(DET_CHECK))
    anp = json.load(open(ANCHOR_PRESERVATION))

    # Gate (a): file moved with SHA preserved + mtime advanced.
    gate_a = bool(dep["sha_preserved"]) and bool(dep["mtime_advanced"])
    # Gate (b): grep-zero c45 imports.
    gate_b = bool(dep["grep_zero_imports"])
    # Gate (c): c46 canonical preserved.
    gate_c = bool(anp["c46_canonical_preserved"])
    # Gate (d): SOURCE_DATE_EPOCH entry appended, value + hashes correct, 18 -> 19.
    entry = sde["entry"]
    expected_value_sha = hashlib.sha256(str(entry["value"]).encode("utf-8")).hexdigest()
    canonical_core = json.dumps(
        {"key": entry["key"], "value": entry["value"], "value_sha256": entry["value_sha256"]},
        sort_keys=True, separators=(",", ":"),
    )
    expected_entry_sha = hashlib.sha256(canonical_core.encode("utf-8")).hexdigest()
    gate_d = (
        entry["value"] == 1756463424
        and entry["value_sha256"] == expected_value_sha
        and entry["entry_sha256"] == expected_entry_sha
        and sde["anchor_count_post"] - sde["anchor_count_pre"] == 1
        and anp["n_preserved"] == 18
    )
    # Gate (e): byte-determinism × 2.
    gate_e = bool(det["byte_deterministic_x2"])

    all_pass = gate_a and gate_b and gate_c and gate_d and gate_e
    verdict = "DEPRECATION_LANDS_AND_ANCHOR_PINNED" if all_pass else "DEPRECATION_PARTIAL"

    per_gate = [
        {"gate": "a_c45_moved", "passed": gate_a,
         "evidence": "data/deprecation_and_anchor_pin/deprecation_check.json",
         "detail": {"sha_preserved": dep["sha_preserved"],
                    "mtime_advanced": dep["mtime_advanced"]}},
        {"gate": "b_grep_zero_imports", "passed": gate_b,
         "evidence": "data/deprecation_and_anchor_pin/deprecation_check.json",
         "detail": {"imports_matches": dep["imports_scan"]["count"]}},
        {"gate": "c_c46_canonical_unchanged", "passed": gate_c,
         "evidence": "data/deprecation_and_anchor_pin/anchor_preservation.json",
         "detail": {"c46_pre_sha": anp["c46_pre_sha"],
                    "c46_post_sha": anp["c46_post_sha"]}},
        {"gate": "d_source_date_epoch_pinned", "passed": gate_d,
         "evidence": "data/deprecation_and_anchor_pin/source_date_epoch_pin.json",
         "detail": {"anchor_count_pre": sde["anchor_count_pre"],
                    "anchor_count_post": sde["anchor_count_post"],
                    "value_sha256": entry["value_sha256"],
                    "entry_sha256": entry["entry_sha256"]}},
        {"gate": "e_byte_determinism_x2", "passed": gate_e,
         "evidence": "data/deprecation_and_anchor_pin/determinism_check.json",
         "detail": {"on_disk_post_sha": det["on_disk_post_sha"],
                    "tmpdir_post_sha": det["tmpdir_post_sha"]}},
    ]

    verdict_json = {
        "cycle": 47,
        "branch": "C",
        "clone": 2,
        "milestone_family": [
            "_archive/deprecate-c45-determinism-check-clone-2",
            "_infra/pin-source-date-epoch-anchor-clone-2",
        ],
        "verdict": verdict,
        "rubric_hash": doc_sha,
        "rubric_hash_txt": txt_content,
        "three_way_rubric_hash_equal": (doc_sha == txt_content),
        "per_gate": per_gate,
        "closes_c46_audit_minor": [2, 3],
        "env_pins": {
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "PYTHONHASHSEED": "0",
            "SOURCE_DATE_EPOCH": "1756463424",
            "TZ": "UTC",
            "LC_ALL": "C.UTF-8",
        },
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(verdict_json, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"[verdict] verdict={verdict}")
    print(f"[verdict] rubric_hash={doc_sha}")
    print(f"[verdict] three_way_equal={verdict_json['three_way_rubric_hash_equal']}")
    for g in per_gate:
        print(f"[verdict]   {g['gate']}: {'PASS' if g['passed'] else 'FAIL'}")
    print(f"[verdict] wrote {OUT}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
