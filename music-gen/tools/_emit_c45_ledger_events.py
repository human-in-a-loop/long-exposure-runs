#!/usr/bin/python3
# ---
# created: 2026-09-05T23:45:00Z
# cycle: 45
# run_id: run-2026-09-05T234500Z
# agent: worker
# milestone: _plan/register-c45-sub-leaves
# ---
"""c45 ledger emitter - idempotent per-turn guard (sentinel: tools/.c45_ledger_emitted).

Mirrors tools/_emit_c44_ledger_events.py shape. Per c45 brief:
    P0 BLOCKED: 6 escalations preserved byte-identical + narrative counter +1 vs c44
        (recorded in _selection/c45-escalation-preservation sidecar; carried in
        _run/cycle_45_closed narrative). Memos unchanged on disk.
    P1: long_exposure/ ABSENT re-probe (11th consecutive) ->
        _selection/c45-emitter-writer-boundary-preservation
    P2: POR-drift stand-pat (12th consecutive) ->
        _selection/c45-por-drift-preservation
    P3: CONTINGENT - no operator adjudication - preserved verbatim (skipped).
    P4: Peach Dream stem-manifest divergence CARRIED forward in deferral row.
    P5: 4 honest deferrals + 1 rollup preservation:
        _selection/c45-track-bcd-deferral-preservation
        M-V4-PROFILES-1/{disco-a,rome,peach-dream}-bass-stage2-deferred-c45
        M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c45
    P6: POR shadow-zone hold (parseable=901; matches brief expectation) ->
        _selection/c45-por-shadow-zone-hold
    P7: Tests extended in-place (test_39 + test_40) 40/40 + 8/8 = 48/48 PASS ->
        _infra/c45-track-f-legacy-regression-test-suite-extended
    P8: Consolidation-proposal HOLD (OPT_b) ->
        _selection/c45-consolidation-proposal-hold
    Housekeeping tail:
        _plan/register-c45-sub-leaves
        _run/cycle_45_closed
        _archive/cycle-45-scratch
        _infra/adopt-cycle45-tests

Emitter exemption policy honored (UUID5 content-hash event_id; nested confidence;
str-or-null supersedes_path per c14 lemma; canonical-JSON; sentinel guard).
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

_NAMESPACE = uuid.NAMESPACE_URL


def _event_id(ev: dict) -> str:
    body = {k: v for k, v in ev.items() if k not in ("event_id", "ts")}
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(_NAMESPACE, payload))


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "run-2026-09-05T234500Z"
CYCLE = 45
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T23:45:00Z"

_GUARD = ROOT / "tools" / ".c45_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c45_ledger_events: guard present at {_GUARD} - skipping")
    sys.exit(0)


def _mk(mid: str, status: str, level: str, narrative: str,
        artifacts: list | None = None,
        supersedes_path: str | None = None,
        extra: dict | None = None) -> dict:
    ev = {
        "milestone_id": mid,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "ts": TS,
        "agent": "worker",
        "status": status,
        "confidence": {
            "level": level,
            "rationale": "c45 substantive-heartbeat cycle deliverable per music_gen_v4_prompt.md c45 brief Priority 0-8",
            "assessor": "worker",
        },
        "narrative": narrative,
        "artifacts": artifacts or [],
        "env_pin_sha256": ENV_PIN,
    }
    if supersedes_path is not None:
        ev["supersedes_path"] = supersedes_path
    if extra:
        ev.update(extra)
    ev["event_id"] = _event_id(ev)
    return ev


EVENTS: list = [
    # -- P1: preservation (11th consecutive) --
    _mk(
        "_selection/c45-emitter-writer-boundary-preservation",
        "validated", "high",
        "c45 P1 MANDATORY chain-continuation (11th consecutive). "
        "long_exposure/ probe -> ABSENT. Chain: c34 fork -> c35..c44 preservations "
        "-> c45. c44 predecessor sha "
        "53faa9a2aa6a1b7fd4f93b21fe6728b9cc9b2d02606023af21fe06619ef56bbd "
        "byte-identical pre==post. docs/emitter_exemption_policy.md sha "
        "fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b "
        "byte-identical pre==post. No policy change.",
        artifacts=[
            "data/v4/_selection/c45-emitter-writer-boundary-preservation.json",
            "docs/emitter_exemption_policy.md",
        ],
        supersedes_path="data/v4/_selection/c44-emitter-writer-boundary-preservation.json",
        extra={"carried_from_cycle": 34, "chain_length_cycles": 11},
    ),

    # -- P2: STAND-PAT (12th consecutive) --
    _mk(
        "_selection/c45-por-drift-preservation",
        "validated", "high",
        "c45 P2 STAND-PAT continuation (12th consecutive). E-4 operator c31/c32 "
        "POR snapshot ABSENT (glob + content-scan). Absent-branch fires; stand-"
        "pat chain-supersedes c44 stand-pat. c44 sha 98e01b20... byte-identical. "
        "c35 blocker (c671a40b...) + c34 empirical proof + diagnostic "
        "(3b0e4d95...) byte-identical. Attribution finding stands transitively.",
        artifacts=[
            "data/v4/_selection/c45-por-drift-preservation.json",
            "data/v4/_selection/c44-por-drift-preservation.json",
            "data/v4/_selection/c35-por-drift-proof-strengthening-blocker.json",
            "data/v4/diagnostics/c34_por_delta_proof.json",
        ],
        supersedes_path="data/v4/_selection/c44-por-drift-preservation.json",
        extra={"carried_from_cycle": 34, "chain_length_cycles": 12},
    ),

    # -- P5: rollup + 4 honest deferrals --
    _mk(
        "_selection/c45-track-bcd-deferral-preservation",
        "validated", "high",
        "c45 P5 rollup: 4 Track B/C/D honest-deferral rows preserved. Peach Dream "
        "stem-manifest sha c4944ee80dfe446b... byte-identical pre==post; carried "
        "on peach-dream deferral row (c33+ pattern); no separate E-5 sidecar per "
        "anti-stall + six-escalations-exhaustive constraint.",
        artifacts=["data/v4/_selection/c45-track-bcd-deferral-preservation.json"],
        supersedes_path="data/v4/_selection/c44-track-bcd-deferral-preservation.json",
    ),
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c45",
        "in-progress", "medium",
        "c45 Track B/P5 Disco A bass stage-2 DEFERRED to c46+ per P3 gating "
        "(no operator adjudication of _manager/M-V4-CERT-composite-fp-drift-"
        "adjudication-c32 in live_guidance). Resume: detached launch "
        "fine_fit_sf2_v2.py --song-sha16 cdd2717e52820ff6 wrapped in OP-1 "
        "SerialLock (post-c32 driver sha 6c80c438...). SF2_CONFIRMED remains "
        "FORBIDDEN on non-CG bass.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c45",
        "in-progress", "medium",
        "c45 Track B/P5 Rome bass stage-2 DEFERRED to c46+ (blocked on P3 "
        "operator adjudication). c23 stage-1 emb_cos_dist=0.5145 predicts "
        "SF2_RULED_OUT under distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c45",
        "in-progress", "medium",
        "c45 Track B/P5 Peach Dream bass stage-2 DEFERRED to c46+. c23 stage-1 "
        "emb_cos_dist=0.4437 predicts SF2_RULED_OUT. P4 path-divergence "
        "disclosure carried: data/v4/profiles/88d247468cb6d49f/stem_manifest.json "
        "records operator_section_c25_checkpointed/rc9_6stem/ non-standard path "
        "per invariant (d) from c19 opening; sha c4944ee80dfe446b... byte-"
        "identical pre==post.",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c45",
        "in-progress", "medium",
        "c45 Track D/P5 WIG + Disco A drums stage-1 DEFERRED to c46+. "
        "coarse_sweep_sf2_drums.py green regression at c30 (8/8 byte-identical); "
        "coarse sweeps do not require OP-1. Additive --song-sha16 kwarg thread "
        "required per c28 precedent.",
    ),

    # -- P6: POR shadow-zone hold (parseable=901; matches brief expectation) --
    _mk(
        "_selection/c45-por-shadow-zone-hold",
        "validated", "high",
        "c45 P6: POR shadow-zone hold verified. tools/_c32_por_count.py reports "
        "parseable Milestones=901 at c45 open (matches c44-close baseline of 901 "
        "= c44-open 887 + 14 c44 rows). Delta 0 vs c44 close. Delta 0 vs brief "
        "expectation of 901. Expected c45-close: 915 after registering 14 c45 "
        "rows. supersedes_path=null (new-attestation-per-cycle pattern).",
        artifacts=[
            "data/v4/_selection/c45-por-shadow-zone-hold.json",
            "tools/_c32_por_count.py",
        ],
    ),

    # -- P7: Test suite extension --
    _mk(
        "_infra/c45-track-f-legacy-regression-test-suite-extended",
        "validated", "high",
        "c45 P7 landed. Extended tests/test_c30_legacy_mode_regression.py in-"
        "place with 2 new c45 cases (test_39 c45 chain-supersede invariant "
        "across all 4 chain sidecars + 2 new-attestation sidecars carry "
        "supersedes_path=null; test_40 c45 P0 sidecar shape assertion I-2 "
        "canonical adoption: before/after SHA table for 6 memos + str "
        "supersedes_path to c44 sidecar + before == after no-mutation). Now "
        "40/40 PASS. tests/test_fine_fit_serial_lock_c32.py unchanged at 8/8 "
        "PASS. Cross-cycle total advances c44 46 -> c45 48 (40 in-place + 8 "
        "standalone = 48/48).",
        artifacts=["tests/test_c30_legacy_mode_regression.py"],
    ),

    # -- P8: Consolidation-proposal HOLD (OPT_b) --
    _mk(
        "_selection/c45-consolidation-proposal-hold",
        "validated", "high",
        "c45 P8: consolidation-proposal disposition = OPT_b (keep as READ-ONLY "
        "anchor; 14th cycle). CHOSEN OPT_b; REJECTED OPT_a (unilateral execution "
        "without operator selection). No operator selection landed via "
        "live_guidance. docs/v4_por_consolidation_strategy_proposal_c40.md sha "
        "8cffc1cecf8fed877c94ba7612ad7dd36edd3da7d9daad4212a202a9abfd83d8 byte-"
        "identical pre==post. Brief cross-reference-error re-disclosed per "
        "invariant (d): brief cited alt sha 29a1610b... which is actually "
        "docs/agent_picks_selection_invariants.md sha (also READ-ONLY, byte-"
        "identical) - 5th cycle of this class (c41+c42+c43+c44+c45). I-5 "
        "forward: v4_sound_matching_layer_spec.md observed PRESENT (not absent "
        "as brief flagged).",
        artifacts=[
            "data/v4/_selection/c45-consolidation-proposal-hold.json",
            "docs/v4_por_consolidation_strategy_proposal_c40.md",
        ],
        supersedes_path="data/v4/_selection/c44-consolidation-proposal-hold.json",
    ),

    # -- Housekeeping tail --
    _mk(
        "_plan/register-c45-sub-leaves",
        "validated", "high",
        "c45 POR registration row: 13 new c45 milestone_ids registered inline "
        "in the `## Milestones` section (P1 preservation + P2 stand-pat + P5 "
        "track-bcd rollup + 4 honest deferrals + P6 POR shadow-zone hold + P7 "
        "Track F extension + P8 consolidation-hold + housekeeping tail 4 rows). "
        "Escalation-preservation sidecar (P0) recorded as file artifact only; "
        "no separate ledger event for it (kept 14-event count).",
    ),
    _mk(
        "_run/cycle_45_closed",
        "validated", "high",
        "c45 CLOSED. Priority 0 status: BLOCKED_ON_OPERATOR - all 6 escalation "
        "memos preserved byte-identical (16th consecutive cycle). Narrative "
        "counters bumped +1 vs c44: SHOWCASE-1 non-cg-bass c7 [counter 16], "
        "METRIC-SEMANTICS c16 [counter 16], CERT-drums-halt c30 [counter 16], "
        "CERT-v2-halt c31 [counter 15], CERT-guitar-halt c31 [counter 15], "
        "CERT-composite-fp-drift c32 [counter 14]. P0 verification sidecar at "
        "data/v4/_selection/c45-escalation-preservation.json with SHA before/"
        "after table (I-2 canonical shape adopted from c44; chain-supersedes "
        "c44 sidecar per str-supersede lemma). Invariant (d) note: c44-of-"
        "record chain projection {16,16,16,15,15,14} matches brief P0 "
        "expectation this cycle (c44 auditor I-1 realignment adopted). P1 "
        "preservation: long_exposure/ ABSENT re-probe -> chain-supersede via "
        "_selection/c45-emitter-writer-boundary-preservation (supersedes_path "
        "points at c44 canonical predecessor). P2 stand-pat continuation: "
        "chain-supersede via _selection/c45-por-drift-preservation. P3 "
        "CONTINGENT: no operator adjudication -> skipped; Track A remains "
        "BLOCKED. P4 Peach Dream stem-manifest divergence (sha c4944ee80...) "
        "carried on deferral row. P5 Track B/C/D honestly deferred (4 rows + 1 "
        "rollup). P6 POR shadow-zone hold verified (parseable=901; delta 0 vs "
        "c44 close; delta 0 vs brief expectation). P7 Track F test suite "
        "extended to 40 in-place + 8 standalone = 48/48 PASS. P8 "
        "consolidation-proposal HOLD (OPT_b keep as READ-ONLY anchor; 14th "
        "cycle of brief-crossref-error disclosure). All 9 READ-ONLY anchors "
        "byte-identical pre==post (objective.py 8087ce80..., "
        "_sweep_hygiene_c27.py 771ff42b..., _serial_lock_op1.py 121809db..., "
        "agent_picks_selection_invariants.md 29a1610b..., "
        "emitter_exemption_policy.md fd2c33a7..., "
        "v4_por_consolidation_strategy_proposal_c40.md 8cffc1c..., c34_por_"
        "delta_proof.json 3b0e4d95..., Peach Dream stem_manifest c4944ee8..., "
        "cg_ab_mix.wav 6e13e007...). env_pin_sha256=2ac444c3... unchanged "
        "(canonical 7-key). NO wait-on-operator memo emitted (BANNED per "
        "operator directive 2026-09-03 part 2). Operator ear remains LANDS "
        "authority post-hoc per FD-6. Substantive-heartbeat streak c33->c45 = "
        "14 consecutive cycles under c36 auditor M-2 terminal contract. I-5 "
        "note: v4_sound_matching_layer_spec.md observed PRESENT this cycle "
        "(brief flagged absent at c43+c44); disclosed per invariant (d).",
        artifacts=[
            "data/v4/_selection/c45-escalation-preservation.json",
            "data/v4/_selection/c45-emitter-writer-boundary-preservation.json",
            "data/v4/_selection/c45-por-drift-preservation.json",
            "data/v4/_selection/c45-track-bcd-deferral-preservation.json",
            "data/v4/_selection/c45-por-shadow-zone-hold.json",
            "data/v4/_selection/c45-consolidation-proposal-hold.json",
        ],
    ),
    _mk(
        "_archive/cycle-45-scratch",
        "validated", "high",
        "c45 scratch archival housekeeping. tools/_emit_c45_ledger_events.py "
        "retained in-tree per c14+ pattern. Session-scoped scratchpad probes "
        "under harness-managed dir. No workspace scratch to move to "
        "tools/stale/.",
    ),
    _mk(
        "_infra/adopt-cycle45-tests",
        "validated", "high",
        "c45 test-adoption housekeeping. Extended tests/test_c30_legacy_mode_"
        "regression.py in-place with 2 new c45 cases (test_39 + test_40). "
        "Standalone tests/test_fine_fit_serial_lock_c32.py unchanged. No new "
        "test file introduced this cycle (c18 additive-in-place pattern). "
        "Cross-cycle regression total: 40 in-place + 8 standalone = 48 "
        "(advances c44 baseline of 46).",
    ),
]


def main() -> None:
    assert len(EVENTS) == 14, f"c45 must emit exactly 14 ledger events, got {len(EVENTS)}"
    ledger = ROOT / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    _GUARD.write_text("emitted\n")
    print(f"_emit_c45_ledger_events: {len(EVENTS)} events appended to {ledger}")


if __name__ == "__main__":
    main()
