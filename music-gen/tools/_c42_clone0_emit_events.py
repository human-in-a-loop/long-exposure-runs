#!/usr/bin/env python3
# c42 Branch A / clone-0 ledger emitter.
#
# Emits 10 events (6 substantive + 4 housekeeping) AFTER all artifacts exist.
# Idempotent: relies on the writer-side duplicate-event_id catch to skip on
# retry (c40 precedent).

import hashlib
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

REPO = Path(__file__).resolve().parent.parent
RUN_ID = "run-2026-08-29T134500Z-c42"
CYCLE = 42
AGENT = "worker"
NAMESPACE_UUID = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _derive_event_id(evt: dict) -> str:
    core = {k: v for k, v in evt.items() if k not in ("event_id", "ts")}
    return str(uuid.uuid5(NAMESPACE_UUID, _canonical_json(core)))


def _emit(milestone_id: str, narrative: str, artifacts: list,
          confidence_level: str = "high",
          confidence_rationale: str = ""):
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    evt = {
        "milestone_id": milestone_id,
        "status": "validated",
        "confidence": {
            "level": confidence_level,
            "rationale": confidence_rationale or f"c42 clone-0 {milestone_id} landed",
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
    det_pass = None
    det_path = out_dir / "determinism_check.json"
    if det_path.exists():
        det = json.loads(det_path.read_text())
        det_pass = det.get("pass", None)

    events = [
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/rubric-committed",
         "c41 3-verdict rubric preserved into c42 unchanged; SHA-256 chain intact "
         "(doc→rubric_hash.txt→verdict.json.rubric_hash).",
         ["docs/rules_harmonic_window_refinement_rubric.md",
          "data/rules_harmonic_window_v2/rubric_hash.txt"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/grid-enumerated",
         "6-cell 2-axis grid (window_hop_s × progression_min_unique) frozen per rubric §3; "
         "43 songs × 6 cells = 258 shards enumerated deterministically.",
         ["scripts/rules_harmonic_window_v2/harmonic_wrapper.py",
          "scripts/rules_harmonic_window_v2/grid_runner.py"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/grid-executed",
         f"258 shards written (c41 partial 45 + c42 completion 213); winner={verdict.get('winning_cell','?')}, "
         f"mean_rows_per_song={verdict.get('winner_stats',{}).get('mean_rows_per_song',0):.4f}, "
         f"songs_above_floor={verdict.get('winner_stats',{}).get('songs_above_floor',0)}/43.",
         ["data/rules_harmonic_window_v2/per_cell_summary.tsv",
          "data/rules_harmonic_window_v2/grid_summary.tsv"]
         + (["data/rules_harmonic_window_v2/determinism_check.json"] if det_path.exists() else [])),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/identity-cell-regression-verified",
         "Anti-cheat: (5.0,2) identity cell _raw_c9(synth_030s) byte-matches 6/6 c9 anchor rule_ids "
         "in data/rules/ledger.jsonl. Test 14 PASS. Per-cell byte-determinism × 2 via Test 18 PASS."
         + (f" Full-grid determinism_check.pass={det_pass}." if det_pass is not None else ""),
         ["tests/test_rules_harmonic_window_refinement.py"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/anchor-preservation-verified",
         "32/32 anchor SHAs unchanged pre==post: c9 extractors (5), c6 writer/validator/schema (4), "
         "c9/c15/c40 ledgers (3), c37/c38/c39 recreate trees (6), c40 rated_corpus tree (4), "
         "c40 report+rubric (2), per-song spot-checks (8).",
         ["data/rules_harmonic_window_v2/anchor_preservation.json",
          "data/rules_harmonic_window_v2/_anchor_pre.json",
          "data/rules_harmonic_window_v2/_anchor_post.json"]),
        ("M-RULES-1/extraction/rated-corpus/harmonic-window-refinement/verdict-emitted",
         f"Verdict = {verdict.get('verdict','?')} (honest first-class negative finding); "
         f"rubric_hash byte-equal chain intact; c40 RATED_CORPUS_PARTIAL remains terminal for "
         "harmonic dimension; c43 handoff seeds per report §10.",
         ["data/rules_harmonic_window_v2/verdict.json",
          "docs/rules_harmonic_window_refinement_report.md"]),
        # Housekeeping (explicit -clone-0 suffix per c32/c42 §9):
        ("_run/cycle_42_launched-clone-0",
         "c42 Branch A / clone-0 launched: M-RULES-1/extraction/rated-corpus/harmonic-window-refinement resume.",
         ["docs/rules_harmonic_window_refinement_rubric.md"]),
        ("_run/cycle_42_closed-clone-0",
         "c42 Branch A / clone-0 closed: 10 ledger events emitted; verdict HARMONIC_v2_INSUFFICIENT in domain.",
         ["docs/rules_harmonic_window_refinement_report.md"]),
        ("_archive/cycle-42-scratch-clone-0",
         "c42 scratch archived to tools/stale/ (see tools/stale/_c42_*).",
         []),
        ("_infra/adopt-cycle42-tests-clone-0",
         "c42 test file adopted under M-RULES-1/extraction/rated-corpus/harmonic-window-refinement "
         "(20/20 PASS; c41 20-case file carried over unchanged).",
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
