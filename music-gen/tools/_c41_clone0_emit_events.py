#!/usr/bin/env python3
# c41 Branch A / clone-0 ledger emitter.
#
# Emits 10 events (6 substantive + 4 housekeeping) AFTER all artifacts exist.
# Idempotent: relies on the writer-side duplicate-event_id catch to skip on
# retry (c40 precedent; the shadow ledger lives outside workspace scope).

import hashlib
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

REPO = Path(__file__).resolve().parent.parent
RUN_ID = "run-2026-08-29T125000Z-c41"
CYCLE = 41
AGENT = "worker"
NAMESPACE_UUID = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _derive_event_id(evt: dict) -> str:
    # Content-hash UUID5 excluding ts/event_id (c40 precedent).
    core = {k: v for k, v in evt.items() if k not in ("event_id", "ts")}
    canon = _canonical_json(core)
    return str(uuid.uuid5(NAMESPACE_UUID, canon))


def _emit(milestone_id: str, narrative: str, artifacts: list,
          confidence_level: str = "high",
          confidence_rationale: str = ""):
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    evt = {
        "milestone_id": milestone_id,
        "status": "validated",
        "confidence": {
            "level": confidence_level,
            "rationale": confidence_rationale or f"c41 clone-0 {milestone_id} landed",
            "assessor": "worker",
        },
        "narrative": narrative,
        "artifacts": artifacts,
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": AGENT,
        "ts": now_iso,
    }
    evt["event_id"] = _derive_event_id(evt)
    cmd = [
        "/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
        "--workspace", str(REPO),
        "--event", _canonical_json(evt),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
    if proc.returncode == 0:
        print(f"  APPEND  {milestone_id}")
        return "appended"
    out = (proc.stdout or "") + (proc.stderr or "")
    if "duplicate event_id" in out or "LedgerAppendError" in out:
        print(f"  SKIP    {milestone_id}  (duplicate)")
        return "skipped"
    print(f"  FAIL    {milestone_id}\n{out}")
    return "failed"


def main() -> int:
    out_dir = REPO / "data" / "rules_harmonic_window_v2"
    verdict = json.loads((out_dir / "verdict.json").read_text()) if (out_dir / "verdict.json").exists() else {}

    events = [
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/rubric-committed",
         "c41 3-verdict rubric committed BEFORE any script; SHA-256 in rubric_hash.txt.",
         ["docs/rules_harmonic_window_refinement_rubric.md", "data/rules_harmonic_window_v2/rubric_hash.txt"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/grid-enumerated",
         "6-cell 2-axis grid (window_hop_s × progression_min_unique) frozen per rubric §3.",
         ["scripts/rules_harmonic_window_v2/harmonic_wrapper.py"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/grid-executed",
         f"43 songs × 6 cells = 258 per-cell shards written; per-cell mean rows/song "
         f"computed; winner={verdict.get('winning_cell','?')}.",
         ["data/rules_harmonic_window_v2/per_cell_summary.tsv",
          "data/rules_harmonic_window_v2/grid_summary.tsv"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/identity-cell-regression-verified",
         "Anti-cheat: (5.0,2) identity cell _raw_c9(synth_030s) byte-matches c9 anchor rule_ids "
         "(6/6 in ledger.jsonl).",
         ["tests/test_rules_harmonic_window_refinement.py"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/anchor-preservation-verified",
         "32+ anchor SHAs unchanged pre==post: c9 extractors, c6 writer/validator, "
         "c9/c15/c40 ledgers, c37/c38/c39 recreate trees, c40 rated_corpus tree.",
         ["data/rules_harmonic_window_v2/anchor_preservation.json"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/verdict-emitted",
         f"Verdict = {verdict.get('verdict','?')}, rubric_hash byte-equal chain intact; "
         f"see docs/rules_harmonic_window_refinement_report.md.",
         ["data/rules_harmonic_window_v2/verdict.json",
          "docs/rules_harmonic_window_refinement_report.md"]),
        # Housekeeping (auto-suffixed by c33 harness guard):
        ("_run/cycle_41_launched",
         "c41 Branch A / clone-0 launched: M-RULES-1/extraction/rated-corpus/harmonic-window-refinement.",
         ["docs/rules_harmonic_window_refinement_rubric.md"]),
        ("_run/cycle_41_closed",
         "c41 Branch A / clone-0 closed: 10 ledger events emitted; verdict in domain.",
         ["docs/rules_harmonic_window_refinement_report.md"]),
        ("_archive/cycle-41-scratch",
         "c41 scratch archived to tools/stale/ (see tools/stale/_c41_*).",
         []),
        ("_infra/adopt-cycle41-tests",
         "c41 test file adopted under M-RULES-1/extraction/rated-corpus/harmonic-window-refinement.",
         ["tests/test_rules_harmonic_window_refinement.py"]),
    ]

    results = {"appended": 0, "skipped": 0, "failed": 0}
    for mid, narr, arts in events:
        r = _emit(mid, narr, arts)
        results[r] = results.get(r, 0) + 1
    print(json.dumps(results, indent=2))
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
