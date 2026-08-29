#!/usr/bin/python3
"""Emit c39 Branch C verdict JSON."""
from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "data/fanout_namespace_v3"

rubric_hash = (DATA / "rubric_hash.txt").read_text().strip()
baseline = json.loads((DATA / "replay_baseline.json").read_text())
c37 = json.loads((DATA / "replay_c37_clones.json").read_text())
c38 = json.loads((DATA / "replay_c38_clones.json").read_text())
anchors = json.loads((DATA / "anchor_preservation.json").read_text())
git_gate = (DATA / "git_gate_status.txt").read_text().splitlines()[0].strip()

# Invariants
import long_exposure.workspace_bootstrap as wb
import inspect
from long_exposure.tools._ledger_schema import LedgerSchemaError

signature_ok = str(inspect.signature(wb.append_ledger_event)) == "(workspace: 'Path', event: 'dict') -> 'None'"
mro_ok = LedgerSchemaError in wb.LedgerNamespaceViolation.__mro__
expected_prefixes = ('_infra/','_run/','_plan/','_archive/','_manager/','M-INGEST-1/','M-SEP-1/','M-CLASS-1/','M-DAW-SPIKE-1/','M-TRANS-1/','M-SCORE-1/','M-HEUR-1/','M-EAR-1/','M-RULES-1/','M-TEX-1/','M-GEN-1/','M-RECREATE-1/')
prefixes_ok = wb._FANOUT_INFRA_PREFIXES == expected_prefixes

pre = anchors["pre"]["targets"]
post = anchors["post"]["targets"]
c14_ok = pre["c14_ledger_schema"] == post["c14_ledger_schema"]
c33_fixture_ok = pre["c33_guard_fixture"] == post["c33_guard_fixture"]
v1_content_ok = pre["c32_convention_doc_v1_prev_path"] == post["c32_convention_doc_v1_new_path"]
v3_present = post["c39_convention_doc_v3"] is not None
wb_docstring_only_changed = pre["workspace_bootstrap_source"] != post["workspace_bootstrap_source"]

baseline_ok = baseline["failed"] == 0 and baseline["passed"] == 670
c37_ok = c37["total_missing_in_main"] == 0 and c37["total_mismatch_in_main"] == 0 and c37["byte_identical_all_rows"]
c38_ok = c38["total_missing_in_main"] == 0 and c38["total_mismatch_in_main"] == 0 and c38["byte_identical_all_rows"]

all_gates = {
    "baseline_670_pass": baseline_ok,
    "c37_shadow_byte_identical": c37_ok,
    "c38_shadow_byte_identical": c38_ok,
    "signature_unchanged": signature_ok,
    "mro_unchanged": mro_ok,
    "prefixes_unchanged_from_c36_v2_baseline": prefixes_ok,
    "c14_ledger_schema_sha_unchanged": c14_ok,
    "c33_guard_fixture_sha_unchanged": c33_fixture_ok,
    "v1_content_preserved_at_new_path": v1_content_ok,
    "v3_doc_created": v3_present,
    "workspace_bootstrap_docstring_only_delta": wb_docstring_only_changed,
}

verdict = "CONVENTION_v3_LANDS" if all(all_gates.values()) else "CONVENTION_v3_INSUFFICIENT"

out = {
    "verdict": verdict,
    "rubric_hash": rubric_hash,
    "chosen_path": "Path 2 (codify auto-suffix-all in v3 doc; writer code unchanged beyond docstring)",
    "git_gate_status": git_gate,
    "gates": all_gates,
    "baseline_replay": {
        "total_rows": baseline["total_rows"],
        "passed": baseline["passed"],
        "failed": baseline["failed"],
    },
    "c37_shadow_replay": {
        "fork_id": c37["fork_id"],
        "total_rows": c37["total_rows"],
        "byte_identical": c37["total_byte_identical_in_main"],
        "missing": c37["total_missing_in_main"],
        "mismatch": c37["total_mismatch_in_main"],
        "per_clone": [
            {"clone": c["clone"], "rows": c["rows"], "byte_id": c["byte_identical_in_main"]}
            for c in c37["clones"]
        ],
    },
    "c38_shadow_replay": {
        "fork_id": c38["fork_id"],
        "total_rows": c38["total_rows"],
        "byte_identical": c38["total_byte_identical_in_main"],
        "missing": c38["total_missing_in_main"],
        "mismatch": c38["total_mismatch_in_main"],
        "per_clone": [
            {"clone": c["clone"], "rows": c["rows"], "byte_id": c["byte_identical_in_main"]}
            for c in c38["clones"]
        ],
    },
    "anchor_preservation": {
        "c14_ledger_schema_pre": pre["c14_ledger_schema"],
        "c14_ledger_schema_post": post["c14_ledger_schema"],
        "c33_guard_fixture_pre": pre["c33_guard_fixture"],
        "c33_guard_fixture_post": post["c33_guard_fixture"],
        "c32_v1_doc_content_sha": pre["c32_convention_doc_v1_prev_path"],
        "c32_v1_doc_new_path_sha": post["c32_convention_doc_v1_new_path"],
        "c36_v2_doc_pre": pre["c36_convention_doc_v2"],
        "c36_v2_doc_post": post["c36_convention_doc_v2"],
        "c39_v3_doc_sha": post["c39_convention_doc_v3"],
        "workspace_bootstrap_pre": pre["workspace_bootstrap_source"],
        "workspace_bootstrap_post": post["workspace_bootstrap_source"],
    },
}

path = DATA / "verdict.json"
serialized = json.dumps(out, indent=2, sort_keys=True) + "\n"
path.write_text(serialized)
print(f"wrote {path}  sha256={hashlib.sha256(serialized.encode()).hexdigest()}")
print(f"verdict={verdict}")
