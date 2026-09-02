#!/usr/bin/env python3
"""Append 3 closure_note findings for verify slice 22/23."""
import json, time
from pathlib import Path

FINDINGS = Path("/home/user/long-exposure-runs/music-gen/audits/final/findings.jsonl")

ts = "2026-09-02T00:00:00Z"
rows = [
    {
        "ts": ts,
        "milestone_id": "M-SEP-1/alternative",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "verdict": "CONFIRMED",
        "narrative": (
            "closure_verified. c5 validated/high. On-disk: scripts/separation/run_alternative.py "
            "(70 LOC, openunmix.umxhq call at L44); scripts/separation/verify_umxhq_determinism.py "
            "(146 LOC, SHA-256 byte-identity harness); data/separation/results.tsv carries 12 "
            "UMXHQ rows across synth_030s/060s/090s, 12 htdemucs, 12 naive_copy_third baseline; "
            "TSV schema separator,mix_id,stem,sdr_db,sir_db,sar_db,est_energy_dBFS matches "
            "htdemucs. No PRNG; SF2 sha 74594e8f...1cb0 pinned in synth_gt.py. 0 defects."
        ),
        "stage": "verify_22of23",
    },
    {
        "ts": ts,
        "milestone_id": "M-HEUR-1/meta-tracker",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "verdict": "CONFIRMED",
        "narrative": (
            "closure_verified. c4 validated/high. On-disk: scripts/heuristics/meta_tracker.py "
            "(193 LOC, anchored_tail_weight at L38). 3 seed meta_descriptors.json present "
            "(d15d5c009a70cc32, d251556aedfe35ef, d60cead66dbd0b95). 87-s seed carries "
            "clip_weights[3] = 0.23333333333333334 (matches plan-of-record reference 0.2333...). "
            "All 4 macro descriptors present (dynamics_trajectory, form_coherence, "
            "peak_location_fraction, heuristic_variance_across_clips). Anchored-tail formula "
            "stored verbatim in descriptor JSON. tests/test_heuristics_isolation.py (166 LOC) "
            "guards sidecar_nonfactor. No PRNG. 0 defects."
        ),
        "stage": "verify_22of23",
    },
    {
        "ts": ts,
        "milestone_id": "M-RULES-1/schema/ledger-writer",
        "finding_kind": "closure_note",
        "severity": "INFO",
        "verdict": "CONFIRMED",
        "narrative": (
            "closure_verified. c6 validated/high. On-disk: scripts/rules/ledger.py (193 LOC). "
            "Append-only invariant syntactically enforced: single open() call at L185 in mode "
            "'a'; grep-zero for 'w' or 'r+'. Duplicate rule_id rejection at L107; "
            "supersede-target-missing rejection at L126; self-supersede rejection at L130. "
            "Public API write_rule/write_supersede/effective_rules(L152)/LedgerError(L89) "
            "matches plan-of-record. data/rules/ledger.jsonl carries 76 rows; sample "
            "rule_0271c7a9f3b5f606 and rule_821a916f5a58a283 are content-derived. "
            "tests/test_rules_schema.py 413 LOC plain-assert suite (no pytest dep). "
            "Downstream: every M-RULES-1/extraction event, ledger_i3_dminor.jsonl (86 rows), "
            "and every c34+ palette assignment resolve provenance through this writer. "
            "No PRNG. 0 defects."
        ),
        "stage": "verify_22of23",
    },
]

with FINDINGS.open("a", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"Appended {len(rows)} findings.")
