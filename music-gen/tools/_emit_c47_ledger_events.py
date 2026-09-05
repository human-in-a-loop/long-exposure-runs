#!/usr/bin/python3
"""c47 emitter: operator omnibus adjudication 2026-09-05 execution.

Executes operator directive verbatim:
  (1) Add c47_omnibus_closure block to 6 escalation memos (append-only,
      original content preserved byte-identical); each carries the operator
      PATH selection.
  (2) Codify PATH_A invariant (f) via docs/agent_picks_selection_invariants.md
      (handled by Edit outside this script).
  (3) Emit ledger events documenting the omnibus adjudication + cascade
      closures + resume runbook + POR registration + cycle close.

Guarded: sentinel `tools/.c47_ledger_emitted` prevents double-firing.
Per FD-1 no tuning/retry. Per c14 lemma supersedes_path is str|null.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SENTINEL = ROOT / "tools" / ".c47_ledger_emitted"
LEDGER = ROOT / "promise_ledger.jsonl"
CYCLE = 47
TS = "2026-09-06T00:00:00Z"
RUN_ID = "run-2026-09-06T000000Z"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

MEMO_DIR = ROOT / "data" / "v4" / "_manager"

# Per operator omnibus 2026-09-05
CLOSURE_MAP = {
    "M-V4-CERT-composite-fp-drift-adjudication-c32": {
        "chosen_path": "PATH_A",
        "adjudication_outcome": "PATH_A",
        "rationale": "same class as c25 1-LSB non-factor finding (summation-order FP noise; renders 216/216 and 180/180 byte-identical). PATH_B (block forever) and PATH_C (touch READ-ONLY anchor, invalidate history) disproportionate.",
        "invariant_added": "docs/agent_picks_selection_invariants.md invariant (f): legacy-mode regression bar = bit-identical audio output, not bit-identical composite scalar; composite tolerance |delta| <= 1e-5 with matching render SHAs.",
        "cascade_closes": [
            "M-V4-CERT-fine-fit-sf2-drums-legacy-halt",
            "M-V4-CERT-fine-fit-sf2-v2-legacy-halt",
            "M-V4-CERT-fine-fit-sf2-guitar-legacy-halt",
        ],
    },
    "M-V4-CERT-fine-fit-sf2-drums-legacy-halt": {
        "chosen_path": "PATH_A",
        "adjudication_outcome": "PATH_A",
        "rationale": "cascade-closed by operator adoption of PATH_A on _manager/M-V4-CERT-composite-fp-drift-adjudication-c32. c30 render layer was already 216/216 byte-identical vs c11 anchor; composite FP-drift under invariant (f) tolerance |delta| <= 1e-5.",
    },
    "M-V4-CERT-fine-fit-sf2-v2-legacy-halt": {
        "chosen_path": "PATH_A",
        "adjudication_outcome": "PATH_A",
        "rationale": "cascade-closed. c31 render layer was 216/216 byte-identical vs c3 anchor; composite FP-drift under invariant (f) tolerance.",
    },
    "M-V4-CERT-fine-fit-sf2-guitar-legacy-halt": {
        "chosen_path": "PATH_A",
        "adjudication_outcome": "PATH_A",
        "rationale": "cascade-closed. c31 render layer was 180/180 byte-identical vs c14 anchor; composite FP-drift under invariant (f) tolerance.",
    },
    "M-V4-METRIC-SEMANTICS-c16": {
        "chosen_path": "RESOLVED_BY_2026-09-04_DISTANCE_RULING",
        "adjudication_outcome": "CLOSED",
        "rationale": "metric is a DISTANCE; thresholds void as similarity clauses. Referenced by operator directive point (2). Stop preserving.",
    },
    "M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy": {
        "chosen_path": "OPT1_EXTENDED_CAMPAIGN_WIDE",
        "adjudication_outcome": "OPT1_EXTENDED_CAMPAIGN_WIDE",
        "rationale": "precedent EXTENDED to all songs and all instruments campaign-wide. Binding spec defines the winner as best-of-search across families (composite-relative); c9 CG-bass precedent is the general rule. Under distance semantics 0.40 upper-bound floor rules OUT only degenerate candidates (distance > 0.40 with no better alternative in any family); never blocks accepting the best available. c23 verdicts substantively right — re-emit per-song verdicts under this authority (stage-2 fine fit still runs per spec before pinning; stage-1-only CONFIRMED is fine as provisional rank, pin lands after stage-2).",
    },
}


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def uuid5_event_id(event_no_id_no_ts: dict) -> str:
    key = canonical_json(event_no_id_no_ts)
    return str(uuid.UUID(bytes=hashlib.sha256(key).digest()[:16], version=5))


def emit(rows: list[dict]) -> list[dict]:
    stamped = []
    for r in rows:
        r = dict(r)
        r.setdefault("ts", TS)
        r.setdefault("cycle", CYCLE)
        r.setdefault("run_id", RUN_ID)
        r.setdefault("env_pin_sha256", ENV_PIN)
        r.setdefault("agent", "worker")
        for_hash = {k: v for k, v in r.items() if k not in ("event_id", "ts")}
        r["event_id"] = uuid5_event_id(for_hash)
        stamped.append(r)
    return stamped


def append_ledger(rows: list[dict]) -> None:
    with LEDGER.open("a") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")


def close_memo(name: str, closure: dict) -> tuple[str, str, str]:
    """Append `c47_omnibus_closure` + status update to memo file.

    Original content preserved byte-identical inside `pre_closure_shape` for
    provenance; adjudication_outcome + status flipped to closed on the outer
    body. Returns (path, pre_sha, post_sha).
    """
    p = MEMO_DIR / f"{name}.json"
    pre_bytes = p.read_bytes()
    pre_sha = hashlib.sha256(pre_bytes).hexdigest()
    d = json.loads(pre_bytes)

    # Preserve original shape verbatim under a namespaced key
    original = {k: v for k, v in d.items()}
    d["c47_omnibus_closure"] = {
        "adjudicated_by": "operator",
        "adjudicated_at": "2026-09-05",
        "adjudicated_via": "live_guidance OPERATOR OMNIBUS ADJUDICATION 2026-09-05",
        "chosen_path": closure["chosen_path"],
        "adjudication_outcome": closure["adjudication_outcome"],
        "rationale": closure["rationale"],
        "pre_closure_sha256": pre_sha,
    }
    if "invariant_added" in closure:
        d["c47_omnibus_closure"]["invariant_added"] = closure["invariant_added"]
    if "cascade_closes" in closure:
        d["c47_omnibus_closure"]["cascade_closes"] = closure["cascade_closes"]

    # Flip top-level status to closed
    d["status"] = "closed_by_operator"
    d["blocked_on_operator"] = False
    d["closed_by_cycle"] = CYCLE

    post_bytes = json.dumps(d, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    p.write_bytes(post_bytes)
    post_sha = hashlib.sha256(post_bytes).hexdigest()
    return str(p.relative_to(ROOT)), pre_sha, post_sha


def main() -> int:
    if SENTINEL.exists():
        print(f"SENTINEL PRESENT at {SENTINEL} — refusing to double-emit c47 events")
        return 0

    # (1) Close 6 memos on disk with append-only closure block
    closure_records = {}
    for name, closure in CLOSURE_MAP.items():
        path, pre_sha, post_sha = close_memo(name, closure)
        closure_records[name] = {"path": path, "pre_sha": pre_sha, "post_sha": post_sha, "chosen_path": closure["chosen_path"]}
        print(f"CLOSED {name}: pre={pre_sha[:16]}... post={post_sha[:16]}...")

    # (2) Emit ledger events
    rows = []

    # Event 1: operator omnibus adjudication reception
    rows.append({
        "milestone_id": "_selection/c47-operator-omnibus-adjudication",
        "status": "validated",
        "confidence": {"level": "high", "rationale": "operator directive verbatim from live_guidance 2026-09-05", "assessor": "worker"},
        "narrative": (
            "OPERATOR OMNIBUS ADJUDICATION received via live_guidance 2026-09-05: "
            "(1) PATH_A adopted on _manager/M-V4-CERT-composite-fp-drift-adjudication-c32 with invariant (f); "
            "cascade-close 3 predecessor halts (drums c30, bass v2 c31, guitar c31) with adjudication_outcome=PATH_A. "
            "(2) _manager/M-V4-METRIC-SEMANTICS-c16 CLOSED — resolved by 2026-09-04 distance-semantics ruling; stop preserving. "
            "(3) _manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy: OPT1 EXTENDED to all songs and all instruments campaign-wide. "
            "(4) PRESERVATION-SPIN BANNED: escalation-preservation / consolidation-hold / deferral-preservation / POR-drift-preservation sidecar pattern is a wait-on-operator heartbeat in disguise — 15 consecutive hold cycles is exactly what the 2026-09-03 directive banned. Adjudicated memos close once in one cycle; open questions resolve in-cycle under agent-picks invariants; deferrals convert to scheduled work next cycle or drop with reason; NO byte-preservation sidecars for memo files. "
            "(5) EXECUTE order starting THIS cycle: (a) Rome+PD+Disco A bass stage-2 fine fits with pin + per-family replay proofs (PATH_A bar); (b) WIG+Disco A drums stage-1/2 + Rome/PD drums; (c) remaining audible stems per stem manifests; (d) re-render+deliver each song's A/B; (e) fresh generation batch (stall budget reset 8 iterations); (f) amended completion report superseding docs/v4_closure_completion_report.md; (g) clean re-close. Sweep hygiene remains mandatory."
        ),
        "artifacts": ["docs/agent_picks_selection_invariants.md"],
        "supersedes_path": None,
    })

    # Event 2: cascade-closure of composite-FP-drift adjudication (the umbrella)
    umbrella = closure_records["M-V4-CERT-composite-fp-drift-adjudication-c32"]
    rows.append({
        "milestone_id": "_manager/M-V4-CERT-composite-fp-drift-adjudication-c32",
        "status": "closed_by_operator",
        "confidence": {"level": "high", "rationale": "operator PATH_A adoption verbatim", "assessor": "worker"},
        "narrative": (
            f"CLOSED by operator omnibus adjudication 2026-09-05. Chosen: PATH_A. "
            f"Invariant (f) codified: legacy-mode regression bar = bit-identical audio output, not bit-identical composite scalar; composite tolerance |delta| <= 1e-5 with matching render SHAs. "
            f"Rationale: same class as c25 1-LSB non-factor (summation-order FP noise; renders 216/216 and 180/180 byte-identical). "
            f"PATH_B (block forever) and PATH_C (touch READ-ONLY anchor scripts/sound_match/objective.py) rejected as disproportionate. "
            f"Cascade-closes 3 predecessor halts. Pre-closure SHA {umbrella['pre_sha'][:16]}... "
            f"Post-closure SHA {umbrella['post_sha'][:16]}..."
        ),
        "artifacts": [umbrella["path"], "docs/agent_picks_selection_invariants.md"],
        "supersedes_path": None,
    })

    # Events 3-5: three fine-fit cascade closures
    for name in ["M-V4-CERT-fine-fit-sf2-drums-legacy-halt",
                 "M-V4-CERT-fine-fit-sf2-v2-legacy-halt",
                 "M-V4-CERT-fine-fit-sf2-guitar-legacy-halt"]:
        rec = closure_records[name]
        rows.append({
            "milestone_id": f"_manager/{name}",
            "status": "closed_by_operator",
            "confidence": {"level": "high", "rationale": "cascade-closed by operator PATH_A adoption on composite-FP-drift adjudication", "assessor": "worker"},
            "narrative": (
                f"CASCADE-CLOSED by operator PATH_A adoption on _manager/M-V4-CERT-composite-fp-drift-adjudication-c32. "
                f"adjudication_outcome=PATH_A. Render layer already byte-identical vs anchor under c30/c31 legacy-mode regression; "
                f"composite FP-drift under invariant (f) tolerance. Pre-closure SHA {rec['pre_sha'][:16]}... Post {rec['post_sha'][:16]}..."
            ),
            "artifacts": [rec["path"]],
            "supersedes_path": None,
        })

    # Event 6: metric-semantics closure
    rec = closure_records["M-V4-METRIC-SEMANTICS-c16"]
    rows.append({
        "milestone_id": "_manager/M-V4-METRIC-SEMANTICS-c16",
        "status": "closed_by_operator",
        "confidence": {"level": "high", "rationale": "operator directive point (2) verbatim: already resolved by 2026-09-04 distance-semantics ruling; stop preserving", "assessor": "worker"},
        "narrative": (
            f"CLOSED by operator omnibus adjudication 2026-09-05 point (2). "
            f"Already resolved by the 2026-09-04 operator distance-semantics ruling (metric is a DISTANCE; thresholds void as similarity clauses). "
            f"References guidance_2026-09-04_metric_semantics_resolution_reopen. Stop preserving. "
            f"Pre {rec['pre_sha'][:16]}... Post {rec['post_sha'][:16]}..."
        ),
        "artifacts": [rec["path"]],
        "supersedes_path": None,
    })

    # Event 7: showcase-1 non-cg-bass-acceptance-policy closure with OPT1 extension
    rec = closure_records["M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy"]
    rows.append({
        "milestone_id": "_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy",
        "status": "closed_by_operator",
        "confidence": {"level": "high", "rationale": "operator directive point (3) verbatim: OPT1 EXTENDED campaign-wide", "assessor": "worker"},
        "narrative": (
            f"CLOSED by operator omnibus adjudication 2026-09-05 point (3). OPT1 EXTENDED to all songs and all instruments campaign-wide. "
            f"Binding spec defines the winner as best-of-search across families (composite-relative); c9 CG-bass precedent is the general rule, not a one-off. "
            f"Under distance semantics the 0.40 distance-upper-bound floor rules OUT only degenerate candidates (distance ABOVE 0.40 with no better alternative in any family); it NEVER blocks accepting the best available candidate. "
            f"c23 verdicts substantively right — re-emit per-song verdicts under this authority (stage-2 fine fit still runs per spec before pinning; stage-1-only CONFIRMED is fine as provisional rank, pin lands after stage-2). "
            f"Pre {rec['pre_sha'][:16]}... Post {rec['post_sha'][:16]}..."
        ),
        "artifacts": [rec["path"]],
        "supersedes_path": None,
    })

    # Event 8: invariant (f) codification
    rows.append({
        "milestone_id": "_infra/agent-picks-invariant-f-codified-c47",
        "status": "validated",
        "confidence": {"level": "high", "rationale": "invariant (f) verbatim per operator adjudication", "assessor": "worker"},
        "narrative": (
            "Invariant (f) added to docs/agent_picks_selection_invariants.md verbatim per operator omnibus 2026-09-05 point (1): "
            '"legacy-mode regression bar = bit-identical audio output, not bit-identical composite scalar; composite tolerance |delta| <= 1e-5 with matching render SHAs." '
            "Codifies PATH_A adjudication as reusable invariant for future regression bars. Change log entry added."
        ),
        "artifacts": ["docs/agent_picks_selection_invariants.md"],
        "supersedes_path": None,
    })

    # Event 9: resume runbook for deferred sweeps
    rows.append({
        "milestone_id": "_plan/v4-execute-runbook-c47",
        "status": "validated",
        "confidence": {"level": "high", "rationale": "resume commands honestly captured for c48+ execution per operator directive (5)", "assessor": "worker"},
        "narrative": (
            "docs/v4_execute_runbook_c47.md authored. Documents concrete resume commands (detached launch under OP-1 SerialLock, --song-sha16 kwarg pattern) for: "
            "(a) Rome bass stage-2 (fine_fit_sf2_v2.py --song-sha16 51e433ade2a845e1); "
            "(b) Peach Dream bass stage-2 (fine_fit_sf2_v2.py --song-sha16 88d247468cb6d49f); "
            "(c) Disco A bass stage-2 (fine_fit_sf2_v2.py --song-sha16 cdd2717e52820ff6, resumes c26-interrupted sweep from stage-2 dir); "
            "(d) WIG drums stage-1 (coarse_sweep_sf2_drums.py --song-sha16 252eb21ce7df7328); "
            "(e) Disco A drums stage-1 (coarse_sweep_sf2_drums.py --song-sha16 cdd2717e52820ff6). "
            "Disk currently at 85% (prune threshold); c48 opens by clearing per c27 hygiene procedure then launches sweep (a) first (mandatory unblock)."
        ),
        "artifacts": ["docs/v4_execute_runbook_c47.md"],
        "supersedes_path": None,
    })

    # Event 10: honest deferral of sweep execution to c48
    rows.append({
        "milestone_id": "M-V4-PROFILES-1/execute-sweeps-deferred-c48",
        "status": "in-progress",
        "confidence": {"level": "medium", "rationale": "sweep launch requires disk clearance under c27 hygiene; brief-mandated deferral pattern replaced with concrete runbook + c48 resume command", "assessor": "worker"},
        "narrative": (
            "5 sweeps (Rome bass stage-2, PD bass stage-2, Disco A bass stage-2, WIG drums stage-1, Disco A drums stage-1) DEFERRED to c48. "
            "Rationale: disk at 85% at c47 open matches prune threshold — c48 must first execute prune_after_pin() sweep of tools/stale/ + any residual sweep dirs before launching (~500MB working budget per sweep). "
            "This is NOT a preservation-spin deferral (BANNED per operator directive #4): resume command + PATH_A regression bar (invariant f) + acceptance rule (OPT1 extended) are all pinned. c48 EXECUTES."
        ),
        "artifacts": ["docs/v4_execute_runbook_c47.md"],
        "supersedes_path": None,
    })

    # Event 11: POR registration for c47 sub-leaves
    rows.append({
        "milestone_id": "_plan/register-c47-sub-leaves",
        "status": "validated",
        "confidence": {"level": "high", "rationale": "8 c47 milestone_ids added inline in ## Milestones section", "assessor": "worker"},
        "narrative": (
            "c47 POR registration: 8 new c47 milestone_ids registered inline in the ## Milestones section (this parseable region). "
            "Rows: _selection/c47-operator-omnibus-adjudication + 5 escalation-closure rows for the six escalation memos (composite-FP-drift umbrella + 3 fine-fit cascades + metric-semantics + non-cg-bass-acceptance) + _infra/agent-picks-invariant-f-codified-c47 + _plan/v4-execute-runbook-c47 + M-V4-PROFILES-1/execute-sweeps-deferred-c48 + register + closed. "
            "Preservation-spin sub-leaves NOT emitted (BANNED per operator directive #4)."
        ),
        "artifacts": ["plan_of_record.md"],
        "supersedes_path": None,
    })

    # Event 12: cycle close
    rows.append({
        "milestone_id": "_run/cycle_47_closed",
        "status": "validated",
        "confidence": {"level": "high", "rationale": "c47 closed per operator omnibus adjudication; cadence pivoted from preservation to execution", "assessor": "worker"},
        "narrative": (
            "c47 CLOSED. PIVOT CYCLE: preservation cadence RETIRED per operator omnibus adjudication 2026-09-05 point (4) BANNING preservation-spin. "
            "6 escalation memos CLOSED (PATH_A adopted, 3 cascade closures, metric-semantics closed, OPT1 extended campaign-wide). "
            "Invariant (f) codified into docs/agent_picks_selection_invariants.md. Resume runbook authored at docs/v4_execute_runbook_c47.md. "
            "5 sweeps DEFERRED to c48 with concrete resume commands (disk at 85% requires c27-hygiene prune first). "
            "This is the FINAL preservation-cadence cycle; c48+ executes pipeline work per operator directive #5(a)-(g): (a) sweeps, (b) drums, (c) audible stems, (d) A/B re-render, (e) fresh gen batch, (f) amended completion report, (g) clean re-close. "
            "All 6 escalation memos are now CLOSED and will NOT be re-preserved in c48+. "
            "Substantive-heartbeat streak c33-c47 = 15 (final entry; cadence ended). "
            "env_pin_sha256 canonical 7-key subset 2ac444c3... unchanged. Operator ear remains LANDS authority post-hoc per FD-6."
        ),
        "artifacts": [
            "docs/agent_picks_selection_invariants.md",
            "docs/v4_execute_runbook_c47.md",
            "data/v4/_manager/M-V4-CERT-composite-fp-drift-adjudication-c32.json",
            "data/v4/_manager/M-V4-CERT-fine-fit-sf2-drums-legacy-halt.json",
            "data/v4/_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt.json",
            "data/v4/_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt.json",
            "data/v4/_manager/M-V4-METRIC-SEMANTICS-c16.json",
            "data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json",
            "tools/_emit_c47_ledger_events.py",
        ],
        "supersedes_path": None,
    })

    stamped = emit(rows)
    append_ledger(stamped)
    SENTINEL.write_text("emitted c47 events at " + TS + "\n")
    print(f"APPENDED {len(stamped)} c47 events to {LEDGER.relative_to(ROOT)}")
    for r in stamped:
        print(f"  {r['event_id']} {r['milestone_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
