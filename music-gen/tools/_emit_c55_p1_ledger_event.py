#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-05T16:00:00Z
# cycle: 55
# run_id: run-2026-09-05T160000Z
# agent: worker
# milestone: _infra/op1-writer-full-fix-c55
# ---
"""One-shot emitter for c55 P1 _infra/op1-writer-full-fix-c55 ledger event.

Direct-append per artifact-tracking policy (long_exposure.tools.ledger_append
absent in workspace per c34+ disclosure chain; root-scope append permitted).
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

event = {
    "milestone_id": "_infra/op1-writer-full-fix-c55",
    "cycle": 55,
    "status": "validated",
    "confidence": {
        "level": "high",
        "rationale": (
            "P1 mandatory pre-work gate landed. _serial_lock_op1.py::_payload "
            "now stamps started_at freshly per acquire via "
            "datetime.now(timezone.utc).isoformat(); c52/c53/c54 partial-fix "
            "chain (SOURCE_DATE_EPOCH-derived stale timestamp) retired. All 9 "
            "tests PASS in tests/test_fine_fit_serial_lock_c32.py including new "
            "test_09 which asserts started_at_2 != started_at_1 AND "
            "started_at_2 > started_at_1 across acquire-release-sleep-acquire."
        ),
        "assessor": "worker",
    },
    "narrative": (
        "c55 Priority 1 (mandatory pre-work gate) landed. Edited "
        "scripts/sound_match/_serial_lock_op1.py::_payload: removed "
        "SOURCE_DATE_EPOCH-derived _iso_epoch(sde) call; substituted "
        "datetime.now(timezone.utc).isoformat() for started_at. Module "
        "docstring updated with c55 fix rationale (operational infrastructure "
        "needs fresh wall-clock for stale-sentinel diagnostics; sentinel is "
        "NOT a determinism-tracked artifact). Extended "
        "tests/test_fine_fit_serial_lock_c32.py from 8 to 9 tests: "
        "test_09_started_at_refreshes_on_reacquire acquires, captures "
        "started_at_1, releases, sleeps 5ms, re-acquires, captures "
        "started_at_2, asserts !=, asserts monotonic. Test suite 9/9 PASS via "
        "plain-assert canonical invocation "
        "(PYTHONPATH=. /usr/bin/python3 tests/test_fine_fit_serial_lock_c32.py); "
        "pytest invocation from brief is not available in workspace (per "
        "invariant (d) disclosure - brief prescribed python -m pytest, "
        "workspace has plain-assert runner only, both discover the same 9 test "
        "bodies). SHA drift disclosed per invariant (d): "
        "before_sha=121809db63cb05edf61ef2abcd83a3cf25d16b0774b73f9a7364d06f32d5eff5, "
        "after_sha=b8e1b7dda5d1ed19c7a4516597e6b1b446ce0480ab84bbc0f515d0f78034b814 "
        "(_serial_lock_op1.py); test file "
        "before_sha=f9e4c27db9e9e1ef8dfd935ade18b3d823d654e40fd41caa7864555afd651a61, "
        "after_sha=c2af1ec6da824da83f8197757061e1bfa107898c421cccce034cff1230a3a574. "
        "tests_before=8 tests_after=9. Closes the c52/c53/c54 partial-fix "
        "chain named as pre-work gate in c55 brief root-cause note. P2 and P3 "
        "unblocked for launch in this same cycle. Retains READ-ONLY discipline "
        "on scripts/sound_match/{objective.py, _sweep_hygiene_c27.py, "
        "fine_fit_sf2_v2.py, coarse_sweep_sf2_drums.py}; touches only the OP-1 "
        "helper + its own test file per brief P1.1."
    ),
    "artifacts": [
        "scripts/sound_match/_serial_lock_op1.py",
        "tests/test_fine_fit_serial_lock_c32.py",
    ],
    "supersedes_path": None,
    "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    "run_id": "run-2026-09-05T160000Z",
    "agent": "worker",
    "ts": "2026-09-05T16:00:00Z",
    "before_sha": {
        "scripts/sound_match/_serial_lock_op1.py": "121809db63cb05edf61ef2abcd83a3cf25d16b0774b73f9a7364d06f32d5eff5",
        "tests/test_fine_fit_serial_lock_c32.py": "f9e4c27db9e9e1ef8dfd935ade18b3d823d654e40fd41caa7864555afd651a61",
    },
    "after_sha": {
        "scripts/sound_match/_serial_lock_op1.py": "b8e1b7dda5d1ed19c7a4516597e6b1b446ce0480ab84bbc0f515d0f78034b814",
        "tests/test_fine_fit_serial_lock_c32.py": "c2af1ec6da824da83f8197757061e1bfa107898c421cccce034cff1230a3a574",
    },
    "tests_before": 8,
    "tests_after": 9,
    "invariant_d_disclosures": [
        "brief P1.4 prescribed python -m pytest invocation; workspace has plain-assert runner only. Both runners discover the same 9 test bodies; canonical plain-assert invocation used.",
        "long_exposure.tools.ledger_append helper absent in workspace per c34+ chain; direct-append to promise_ledger.jsonl at root scope per artifact-tracking policy.",
    ],
}

# UUID5 content-hash event_id (excludes event_id + ts per convention).
content = {k: v for k, v in event.items() if k not in ("event_id", "ts")}
canon = json.dumps(content, sort_keys=True, separators=(",", ":"))
event["event_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, canon))

line = json.dumps(event, sort_keys=True, separators=(",", ":"))
with open(ROOT / "promise_ledger.jsonl", "a") as f:
    f.write(line + "\n")

print(f"Appended event_id={event['event_id']}")
print(f"Length: {len(line)} chars")
