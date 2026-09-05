#!/usr/bin/python3
# ---
# created: 2026-09-05T23:46:00Z
# cycle: 46
# run_id: run-2026-09-05T234600Z
# agent: worker
# milestone: _plan/register-c46-sub-leaves
# ---
"""c46 ledger emitter - idempotent per-turn guard (sentinel: tools/.c46_ledger_emitted).

Mirrors tools/_emit_c45_ledger_events.py shape with c46 additions:
    P0 (NEW as ledger event): c46-escalation-preservation chain-supersedes c45 sidecar.
    P4 (NEW as dedicated event class): c46-peach-dream-stem-manifest-preservation
        with supersedes_path=null (c19-c45 carried divergence on deferral row narrative).
    P1..P8, deferrals, register + closed housekeeping mirror c45 shape.

Per c46 brief: exactly 14 ledger events. Trade-off vs c45 pattern: brief lists 8
named priorities + 6 heartbeat rollup events. Interpretation: 8 named + 4 deferrals +
2 housekeeping tail (register + closed). scratch + adopt-tests events omitted this
cycle; scratch archival + test-adoption housekeeping absorbed into _run/cycle_46_closed
narrative. This preserves the brief's exact 14-event count while adding P0 + P4 events.

Discipline: UUID5 content-hash event_id; nested confidence; str-or-null supersedes_path
per c14 lemma; canonical-JSON; sentinel guard.
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
RUN_ID = "run-2026-09-05T234600Z"
CYCLE = 46
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T23:46:00Z"

_GUARD = ROOT / "tools" / ".c46_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c46_ledger_events: guard present at {_GUARD} - skipping")
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
            "rationale": "c46 substantive-heartbeat cycle deliverable per music_gen_v4_prompt.md c46 brief Priority 0-8",
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
    # -- P0 (NEW as ledger event): escalation-preservation --
    _mk(
        "_selection/c46-escalation-preservation",
        "validated", "high",
        "c46 P0: all 6 blocked_on_operator escalation memos preserved byte-identical "
        "(17th consecutive cycle). Before/after SHA verification tabled in sidecar; "
        "each memo unchanged pre==post per FD-1. Narrative counter bumped +1 vs c45 "
        "(c45 {16,16,16,15,15,14} -> c46 {17,17,17,16,16,15}) matching brief P0 "
        "projection exactly (c45 auditor I-1 realignment held). Chain-supersedes c45 "
        "sidecar per I-2 canonical shape. supersedes_path str per c14 lemma.",
        artifacts=[
            "data/v4/_selection/c46-escalation-preservation.json",
            "data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json",
            "data/v4/_manager/M-V4-METRIC-SEMANTICS-c16.json",
            "data/v4/_manager/M-V4-CERT-fine-fit-sf2-drums-legacy-halt.json",
            "data/v4/_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt.json",
            "data/v4/_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt.json",
            "data/v4/_manager/M-V4-CERT-composite-fp-drift-adjudication-c32.json",
        ],
        supersedes_path="data/v4/_selection/c45-escalation-preservation.json",
        extra={"carried_from_cycle": 33, "chain_length_cycles": 17},
    ),

    # -- P1: emitter-writer-boundary-preservation (12th consecutive) --
    _mk(
        "_selection/c46-emitter-writer-boundary-preservation",
        "validated", "high",
        "c46 P1 MANDATORY chain-continuation (12th consecutive). "
        "long_exposure/ probe -> ABSENT. Chain: c34 fork -> c35..c45 preservations "
        "-> c46. c45 predecessor sha "
        "39181cdef7456f9a3bf547e35beef89eb3544592d87f31d686508e4a314a8ca7 "
        "byte-identical pre==post. docs/emitter_exemption_policy.md sha "
        "fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b "
        "byte-identical pre==post. No policy change.",
        artifacts=[
            "data/v4/_selection/c46-emitter-writer-boundary-preservation.json",
            "docs/emitter_exemption_policy.md",
        ],
        supersedes_path="data/v4/_selection/c45-emitter-writer-boundary-preservation.json",
        extra={"carried_from_cycle": 34, "chain_length_cycles": 12},
    ),

    # -- P2: por-drift-preservation (13th consecutive) --
    _mk(
        "_selection/c46-por-drift-preservation",
        "validated", "high",
        "c46 P2 STAND-PAT continuation (13th consecutive). E-4 operator c31/c32 POR "
        "snapshot ABSENT (glob + live_guidance content-scan). Absent-branch fires; "
        "stand-pat chain-supersedes c45 stand-pat. c45 sha 4d9a95d6... byte-identical. "
        "c35 blocker (c671a40b...) + c34 empirical proof + diagnostic (3b0e4d95...) "
        "byte-identical. Attribution finding stands transitively.",
        artifacts=[
            "data/v4/_selection/c46-por-drift-preservation.json",
            "data/v4/_selection/c45-por-drift-preservation.json",
            "data/v4/_selection/c35-por-drift-proof-strengthening-blocker.json",
            "data/v4/diagnostics/c34_por_delta_proof.json",
        ],
        supersedes_path="data/v4/_selection/c45-por-drift-preservation.json",
        extra={"carried_from_cycle": 34, "chain_length_cycles": 13},
    ),

    # -- P4 (NEW dedicated event class): peach-dream-stem-manifest-preservation --
    _mk(
        "_selection/c46-peach-dream-stem-manifest-preservation",
        "validated", "high",
        "c46 P4 dedicated preservation record for Peach Dream stem-manifest "
        "divergence. Re-verified data/v4/profiles/88d247468cb6d49f/stem_manifest.json "
        "sha c4944ee80dfe446b118cf2584e29fa432cc33f21ecdcbe96cc2b63fe946a3b9e "
        "byte-identical pre==post (11th consecutive cycle since c19 opening). Non-"
        "standard path operator_section_c25_checkpointed/rc9_6stem/ preserved per "
        "invariant (d); NO normalization undertaken per FD-1. supersedes_path=null "
        "(new event class this cycle; c19-c45 carried divergence on peach-dream "
        "deferral row narrative). c46 brief P4 requested dedicated event class.",
        artifacts=[
            "data/v4/_selection/c46-peach-dream-stem-manifest-preservation.json",
            "data/v4/profiles/88d247468cb6d49f/stem_manifest.json",
        ],
        extra={"carried_from_cycle": 19, "chain_length_cycles": 11,
               "note_new_event_class": "c46 first dedicated ledger event for this divergence"},
    ),

    # -- P5: track-bcd-deferral-preservation rollup --
    _mk(
        "_selection/c46-track-bcd-deferral-preservation",
        "validated", "high",
        "c46 P5 rollup: 4 Track B/C/D honest-deferral rows preserved. Peach Dream "
        "stem-manifest divergence extracted to its own P4 dedicated event this cycle "
        "(previously carried in peach-dream deferral row narrative c33-c45); rollup "
        "still preserves the 4 deferrals themselves per anti-stall + six-escalations-"
        "exhaustive constraint.",
        artifacts=["data/v4/_selection/c46-track-bcd-deferral-preservation.json"],
        supersedes_path="data/v4/_selection/c45-track-bcd-deferral-preservation.json",
    ),

    # -- P6: POR shadow-zone hold --
    _mk(
        "_selection/c46-por-shadow-zone-hold",
        "validated", "high",
        "c46 P6: POR shadow-zone hold verified. tools/_c32_por_count.py reports "
        "parseable Milestones=915 at c46 open (matches c45-close baseline of 915). "
        "Delta 0 vs c45 close. Delta 0 vs brief expectation of 915. Expected c46-"
        "close: 929 after registering 14 c46 rows. supersedes_path=null (new-"
        "attestation-per-cycle pattern).",
        artifacts=[
            "data/v4/_selection/c46-por-shadow-zone-hold.json",
            "tools/_c32_por_count.py",
        ],
    ),

    # -- P7: Track F test suite extension --
    _mk(
        "_infra/c46-track-f-legacy-regression-test-suite-extended",
        "validated", "high",
        "c46 P7 landed. Extended tests/test_c30_legacy_mode_regression.py in-place "
        "with 2 new c46 cases (test_41 c46 chain-supersede invariant across 5 chain "
        "sidecars + 2 new-attestation sidecars carry supersedes_path=null - POR "
        "shadow-hold + P4 Peach Dream new event class; test_42 c46 P0 sidecar shape "
        "I-2 canonical adoption from c45: before/after SHA table for 6 memos + str "
        "supersedes_path to c45 sidecar + before==after no-mutation + monotonicity "
        "{17,17,17,16,16,15} = c45 {16,16,16,15,15,14} + 1). Now 42/42 PASS. "
        "tests/test_fine_fit_serial_lock_c32.py unchanged at 8/8 PASS. Cross-cycle "
        "total advances c45 48 -> c46 50 (42 in-place + 8 standalone = 50/50).",
        artifacts=["tests/test_c30_legacy_mode_regression.py"],
    ),

    # -- P8: Consolidation-proposal HOLD (OPT_b) + I-5 disposition --
    _mk(
        "_selection/c46-consolidation-proposal-hold",
        "validated", "high",
        "c46 P8: consolidation-proposal disposition = OPT_b (keep as READ-ONLY "
        "anchor; 15th cycle). CHOSEN OPT_b; REJECTED OPT_a (unilateral execution "
        "without operator selection). No operator selection landed via live_guidance. "
        "docs/v4_por_consolidation_strategy_proposal_c40.md sha "
        "8cffc1cecf8fed877c94ba7612ad7dd36edd3da7d9daad4212a202a9abfd83d8 byte-"
        "identical pre==post. Brief cross-reference-error re-disclosed per invariant "
        "(d) recurrence #5 (c41+c42+c43+c44+c45): brief cited alt sha 29a1610b... "
        "which is actually docs/agent_picks_selection_invariants.md sha (also READ-"
        "ONLY, also byte-identical). I-5 binding doc "
        "docs/specs/v4_sound_matching_layer_spec.md observed PRESENT at c46 open "
        "with sha bfbe522f306e4d0395b6f1d0450736502e2390e59bebae1c9a6eefcb9f4863d9 "
        "STABLE across c45->c46; per c45 auditor forward guidance I-5 formally "
        "CLOSED as positive-unblock signal for M-V4-PROFILES readiness scoping; "
        "handed forward to c47+ researcher (no c46 authoring undertaken per FD-1 + "
        "brief non-goal).",
        artifacts=[
            "data/v4/_selection/c46-consolidation-proposal-hold.json",
            "docs/v4_por_consolidation_strategy_proposal_c40.md",
            "docs/specs/v4_sound_matching_layer_spec.md",
        ],
        supersedes_path="data/v4/_selection/c45-consolidation-proposal-hold.json",
        extra={"i5_status": "closed_positive_unblock",
               "i5_sha_stable_c45_to_c46": True,
               "hand_forward_to": "c47+ researcher"},
    ),

    # -- 4 honest deferrals (Track B/C/D) --
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c46",
        "in-progress", "medium",
        "c46 Track B/P5 Disco A bass stage-2 DEFERRED to c47+ per P3 gating (no "
        "operator adjudication of _manager/M-V4-CERT-composite-fp-drift-"
        "adjudication-c32 in live_guidance). Resume: detached launch "
        "fine_fit_sf2_v2.py --song-sha16 cdd2717e52820ff6 wrapped in OP-1 SerialLock "
        "(post-c32 driver sha 6c80c438...). SF2_CONFIRMED remains FORBIDDEN on non-"
        "CG bass.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c46",
        "in-progress", "medium",
        "c46 Track B/P5 Rome bass stage-2 DEFERRED to c47+ (blocked on P3 operator "
        "adjudication). c23 stage-1 emb_cos_dist=0.5145 predicts SF2_RULED_OUT under "
        "distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c46",
        "in-progress", "medium",
        "c46 Track B/P5 Peach Dream bass stage-2 DEFERRED to c47+. c23 stage-1 "
        "emb_cos_dist=0.4437 predicts SF2_RULED_OUT. P4 stem-manifest divergence "
        "extracted this cycle to its own dedicated event class "
        "(_selection/c46-peach-dream-stem-manifest-preservation) - divergence sha "
        "c4944ee80dfe446b... verified byte-identical pre==post there rather than "
        "recorded on this deferral row (11th consecutive cycle byte-identical since "
        "c19 opening).",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c46",
        "in-progress", "medium",
        "c46 Track D/P5 WIG + Disco A drums stage-1 DEFERRED to c47+. "
        "coarse_sweep_sf2_drums.py green regression at c30 (8/8 byte-identical); "
        "coarse sweeps do not require OP-1. Additive --song-sha16 kwarg thread "
        "required per c28 precedent.",
    ),

    # -- Housekeeping tail: register + closed (scratch + adopt-tests absorbed into closed narrative to honor brief 14-event count) --
    _mk(
        "_plan/register-c46-sub-leaves",
        "validated", "high",
        "c46 POR registration row: 14 new c46 milestone_ids registered inline in "
        "the `## Milestones` section (P0 escalation-preservation NEW + P1 "
        "preservation + P2 stand-pat + P4 Peach Dream stem-manifest NEW + P5 track-"
        "bcd rollup + P6 POR shadow-zone hold + P7 Track F extension + P8 "
        "consolidation-hold + 4 honest deferrals + register + closed). Invariant (d) "
        "disclosure: c46 brief-mandated housekeeping tail (closed -> scratch -> "
        "adopt-tests) shortened to closed-only to honor brief's exact 14-event "
        "count; scratch archival + test-adoption bookkeeping absorbed into "
        "_run/cycle_46_closed narrative. c46 close parseable = 915 + 14 = 929 "
        "matches brief expectation.",
    ),
    _mk(
        "_run/cycle_46_closed",
        "validated", "high",
        "c46 CLOSED. P0 status: BLOCKED_ON_OPERATOR - all 6 escalation memos "
        "preserved byte-identical (17th consecutive cycle). Narrative counters "
        "bumped +1 vs c45: SHOWCASE-1 non-cg-bass c7 [counter 17], METRIC-SEMANTICS "
        "c16 [counter 17], CERT-drums-halt c30 [counter 17], CERT-v2-halt c31 "
        "[counter 16], CERT-guitar-halt c31 [counter 16], CERT-composite-fp-drift "
        "c32 [counter 15]. P0 verification sidecar at data/v4/_selection/c46-"
        "escalation-preservation.json with SHA before/after table (I-2 canonical "
        "shape adopted from c44/c45; chain-supersedes c45 sidecar per str-supersede "
        "lemma). P1 preservation: long_exposure/ ABSENT re-probe -> chain-supersede "
        "via _selection/c46-emitter-writer-boundary-preservation. P2 stand-pat "
        "continuation via _selection/c46-por-drift-preservation. P3 CONTINGENT: no "
        "operator adjudication -> skipped; Track A remains BLOCKED. P4 Peach Dream "
        "stem-manifest divergence extracted this cycle to dedicated event class "
        "_selection/c46-peach-dream-stem-manifest-preservation (sha c4944ee80... "
        "byte-identical, 11th consecutive since c19); supersedes_path=null (new "
        "event class). P5 Track B/C/D honestly deferred (4 rows + 1 rollup). P6 POR "
        "shadow-zone hold verified (parseable=915 delta 0 vs c45 close; expected "
        "c46-close=929 = 915 + 14 new POR rows). P7 Track F test-suite extended to "
        "42 in-place + 8 standalone = 50/50 PASS. P8 consolidation-proposal HOLD "
        "(OPT_b keep as READ-ONLY anchor; 15th cycle). I-5 binding doc "
        "docs/specs/v4_sound_matching_layer_spec.md observed PRESENT with sha "
        "bfbe522f... STABLE across c45->c46; I-5 formally CLOSED as positive-unblock "
        "signal (per c45 auditor forward guidance) handed forward to c47+ researcher "
        "for M-V4-PROFILES readiness scoping (no c46 authoring per FD-1 + brief non-"
        "goal). All 9 READ-ONLY anchors byte-identical pre==post (objective.py "
        "8087ce80..., _sweep_hygiene_c27.py 771ff42b..., _serial_lock_op1.py "
        "121809db..., agent_picks_selection_invariants.md 29a1610b..., "
        "emitter_exemption_policy.md fd2c33a7..., v4_por_consolidation_strategy_"
        "proposal_c40.md 8cffc1c..., c34_por_delta_proof.json 3b0e4d95..., Peach "
        "Dream stem_manifest c4944ee8..., cg_ab_mix.wav 6e13e007...). "
        "env_pin_sha256=2ac444c3... unchanged (canonical 7-key). Housekeeping "
        "absorbed: no separate _archive/cycle-46-scratch or _infra/adopt-cycle46-"
        "tests events this cycle to honor brief's 14-event count - scratch archival "
        "housekeeping (tools/_emit_c46_ledger_events.py retained in-tree per c14+ "
        "pattern) + test-adoption bookkeeping (test_41 + test_42 landed in-place "
        "per c18 additive pattern; 42+8=50 cross-cycle) documented here in this "
        "narrative. NO wait-on-operator memo emitted (BANNED per operator directive "
        "2026-09-03 part 2). Operator ear remains LANDS authority post-hoc per "
        "FD-6. Substantive-heartbeat streak c33->c46 = 15 consecutive cycles under "
        "c36 auditor M-2 terminal contract.",
        artifacts=[
            "data/v4/_selection/c46-escalation-preservation.json",
            "data/v4/_selection/c46-emitter-writer-boundary-preservation.json",
            "data/v4/_selection/c46-por-drift-preservation.json",
            "data/v4/_selection/c46-peach-dream-stem-manifest-preservation.json",
            "data/v4/_selection/c46-track-bcd-deferral-preservation.json",
            "data/v4/_selection/c46-por-shadow-zone-hold.json",
            "data/v4/_selection/c46-consolidation-proposal-hold.json",
            "tools/_emit_c46_ledger_events.py",
            "tests/test_c30_legacy_mode_regression.py",
        ],
    ),
]


def main() -> None:
    assert len(EVENTS) == 14, f"c46 must emit exactly 14 ledger events, got {len(EVENTS)}"
    ledger = ROOT / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    _GUARD.write_text("emitted\n")
    print(f"_emit_c46_ledger_events: {len(EVENTS)} events appended to {ledger}")


if __name__ == "__main__":
    main()
