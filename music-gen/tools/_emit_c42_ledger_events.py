#!/usr/bin/python3
# ---
# created: 2026-09-05T23:00:00Z
# cycle: 42
# run_id: run-2026-09-05T230000Z
# agent: worker
# milestone: _plan/register-c42-sub-leaves
# ---
"""c42 ledger emitter - idempotent per-turn guard (sentinel: tools/.c42_ledger_emitted).

Mirrors tools/_emit_c41_ledger_events.py shape. Per c42 brief:
    P0 BLOCKED: 6 escalations preserved verbatim (no emissions).
    P1: long_exposure/ ABSENT re-probe (8th consecutive) ->
        _selection/c42-emitter-writer-boundary-preservation
    P2: POR-drift stand-pat (9th consecutive) ->
        _selection/c42-por-drift-preservation
    P3: CONTINGENT - no operator adjudication - preserved verbatim.
    P4: Peach Dream stem-manifest divergence CARRIED forward in deferral row.
    P5: 4 honest deferrals + 1 rollup preservation:
        _selection/c42-track-bcd-deferral-preservation
        M-V4-PROFILES-1/{disco-a,rome,peach-dream}-bass-stage2-deferred-c42
        M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c42
    P6: POR shadow-zone hold (on-disk 859; brief expected 858; disclose +1) ->
        _selection/c42-por-shadow-zone-hold
    P7: Tests extended in-place (test_33 + test_34) 34/34 + 8/8 = 42/42 PASS ->
        _infra/c42-track-f-legacy-regression-test-suite-extended
    P8: Consolidation-proposal HOLD (OPT_b) ->
        _selection/c42-consolidation-proposal-hold
    Housekeeping tail:
        _plan/register-c42-sub-leaves
        _run/cycle_42_closed
        _archive/cycle-42-scratch
        _infra/adopt-cycle42-tests

Emitter exemption policy (docs/emitter_exemption_policy.md sha
fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b) honored:
    UUID5 content-hash event_id; nested confidence; str-or-null supersedes_path
    (c14 lemma); canonical-JSON; sentinel guard.
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
RUN_ID = "run-2026-09-05T230000Z"
CYCLE = 42
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T23:05:00Z"

_GUARD = ROOT / "tools" / ".c42_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c42_ledger_events: guard present at {_GUARD} - skipping")
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
            "rationale": "c42 substantive-heartbeat cycle deliverable per music_gen_v4_prompt.md c42 brief Priority 0-8",
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
    # -- P1: preservation (8th consecutive) --
    _mk(
        "_selection/c42-emitter-writer-boundary-preservation",
        "validated", "high",
        "c42 P1 MANDATORY chain-continuation (8th consecutive). "
        "long_exposure/ probe -> ABSENT. Chain: c34 fork -> c35..c41 preservations "
        "-> c42. c41 predecessor uses on-disk actual filename "
        "c41-long-exposure-absent-preservation.json (sha "
        "bf9ca459339a7f487a20e851248f668fa9696f24a4305244aad5da77590226c7); "
        "c42 adopts canonical -emitter-writer-boundary-preservation naming per "
        "brief M-1 codification. Naming-convention disclosure recorded in the "
        "on-disk file per invariant (d). docs/emitter_exemption_policy.md sha "
        "fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b "
        "byte-identical pre==post. No policy change.",
        artifacts=[
            "data/v4/_selection/c42-emitter-writer-boundary-preservation.json",
            "docs/emitter_exemption_policy.md",
        ],
        supersedes_path="data/v4/_selection/c41-long-exposure-absent-preservation.json",
        extra={"carried_from_cycle": 34, "chain_length_cycles": 8},
    ),

    # -- P2: STAND-PAT (9th consecutive) --
    _mk(
        "_selection/c42-por-drift-preservation",
        "validated", "high",
        "c42 P2 STAND-PAT continuation (9th consecutive). E-4 operator c31/c32 "
        "POR snapshot ABSENT (glob + content-scan). Absent-branch fires; stand-"
        "pat chain-supersedes c41 stand-pat. c41 sha "
        "578ceec4d7c660ee8eb7a5133ad02c30c8c41147d0740203042825707d9b53e0 "
        "byte-identical. c35 blocker (c671a40b...) + c34 empirical proof + "
        "diagnostic (3b0e4d95...) byte-identical. Attribution finding stands "
        "transitively.",
        artifacts=[
            "data/v4/_selection/c42-por-drift-preservation.json",
            "data/v4/_selection/c41-por-drift-preservation.json",
            "data/v4/_selection/c35-por-drift-proof-strengthening-blocker.json",
            "data/v4/diagnostics/c34_por_delta_proof.json",
        ],
        supersedes_path="data/v4/_selection/c41-por-drift-preservation.json",
        extra={"carried_from_cycle": 34, "chain_length_cycles": 9},
    ),

    # -- P5: rollup + 4 honest deferrals --
    _mk(
        "_selection/c42-track-bcd-deferral-preservation",
        "validated", "high",
        "c42 P5 rollup: 4 Track B/C/D honest-deferral rows preserved. Peach Dream "
        "stem-manifest sha c4944ee80dfe446b... byte-identical pre==post; carried "
        "on peach-dream deferral row (c33+ pattern); no separate E-5 sidecar per "
        "anti-stall + six-escalations-are-exhaustive constraint.",
        artifacts=["data/v4/_selection/c42-track-bcd-deferral-preservation.json"],
        supersedes_path="data/v4/_selection/c41-track-bcd-deferral-preservation.json",
    ),
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c42",
        "in-progress", "medium",
        "c42 Track B/P5 Disco A bass stage-2 DEFERRED to c43+ per P3 gating "
        "(no operator adjudication of _manager/M-V4-CERT-composite-fp-drift-"
        "adjudication-c32 in live_guidance). Resume: detached launch "
        "fine_fit_sf2_v2.py --song-sha16 cdd2717e52820ff6 wrapped in OP-1 "
        "SerialLock (post-c32 driver sha 6c80c438...). SF2_CONFIRMED remains "
        "FORBIDDEN on non-CG bass.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c42",
        "in-progress", "medium",
        "c42 Track B/P5 Rome bass stage-2 DEFERRED to c43+ (blocked on P3 "
        "operator adjudication). c23 stage-1 emb_cos_dist=0.5145 predicts "
        "SF2_RULED_OUT under distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c42",
        "in-progress", "medium",
        "c42 Track B/P5 Peach Dream bass stage-2 DEFERRED to c43+. c23 stage-1 "
        "emb_cos_dist=0.4437 predicts SF2_RULED_OUT. P4 path-divergence "
        "disclosure carried: data/v4/profiles/88d247468cb6d49f/stem_manifest.json "
        "records operator_section_c25_checkpointed/rc9_6stem/ non-standard path "
        "per invariant (d) from c19 opening; sha c4944ee80dfe446b... byte-"
        "identical pre==post.",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c42",
        "in-progress", "medium",
        "c42 Track D/P5 WIG + Disco A drums stage-1 DEFERRED to c43+. "
        "coarse_sweep_sf2_drums.py green regression at c30 (8/8 byte-identical); "
        "coarse sweeps do not require OP-1. Additive --song-sha16 kwarg thread "
        "required per c28 precedent.",
    ),

    # -- P6: POR shadow-zone hold (on-disk 859 vs brief 858 disclosed per (d)) --
    _mk(
        "_selection/c42-por-shadow-zone-hold",
        "validated", "high",
        "c42 P6: POR shadow-zone hold verified. tools/_c32_por_count.py reports "
        "parseable Milestones=859 at c42 open. Delta 0 vs c41 close baseline "
        "(859). Brief expected 858; +1 off-by-one disclosed per invariant (d) - "
        "brief accounting projected c41-open=845 + 13 rows = 858 whereas on-disk "
        "c41-close/c42-open = 859 (matches c41 session summary + POR row). "
        "Per FD-1, on-disk 859 is authoritative; NOT a shadow-zone breach; no "
        "auto-consolidation. supersedes_path=null (new-attestation-per-cycle "
        "pattern from c37 onwards).",
        artifacts=[
            "data/v4/_selection/c42-por-shadow-zone-hold.json",
            "tools/_c32_por_count.py",
        ],
    ),

    # -- P7: Test suite extension --
    _mk(
        "_infra/c42-track-f-legacy-regression-test-suite-extended",
        "validated", "high",
        "c42 P7 landed. Extended tests/test_c30_legacy_mode_regression.py in-"
        "place with 2 new c42 cases (test_33 c42 long_exposure/ ABSENT re-probe "
        "+ preservation chain intact via c41 predecessor sha check + M-1 naming "
        "codification assert; test_34 c42 POR stand-pat + full chain-integrity "
        "through c41/c40/c39/c38/c37/c36 + c35 blocker + c34 diagnostic byte-"
        "identical). Now 34/34 PASS. tests/test_fine_fit_serial_lock_c32.py "
        "unchanged at 8/8 PASS. Cross-cycle total advances c41 40 -> c42 42 "
        "(34 in-place + 8 standalone = 42/42).",
        artifacts=["tests/test_c30_legacy_mode_regression.py"],
    ),

    # -- P8: Consolidation-proposal HOLD (OPT_b) --
    _mk(
        "_selection/c42-consolidation-proposal-hold",
        "validated", "high",
        "c42 P8: consolidation-proposal disposition = OPT_b (keep as READ-ONLY "
        "anchor). CHOSEN OPT_b; REJECTED OPT_a (unilateral execution without "
        "operator selection). No operator selection landed via live_guidance. "
        "docs/v4_por_consolidation_strategy_proposal_c40.md sha "
        "8cffc1cecf8fed877c94ba7612ad7dd36edd3da7d9daad4212a202a9abfd83d8 byte-"
        "identical pre==post. Brief cross-reference-error re-disclosed per "
        "invariant (d): brief cited alt sha 29a1610b... which is actually "
        "docs/agent_picks_selection_invariants.md sha (also READ-ONLY, byte-"
        "identical) - same class as c41.",
        artifacts=[
            "data/v4/_selection/c42-consolidation-proposal-hold.json",
            "docs/v4_por_consolidation_strategy_proposal_c40.md",
        ],
        supersedes_path="data/v4/_selection/c41-consolidation-proposal-hold.json",
    ),

    # -- Housekeeping tail --
    _mk(
        "_plan/register-c42-sub-leaves",
        "validated", "high",
        "c42 POR registration row: 13 new c42 milestone_ids registered inline "
        "in the `## Milestones` section (P1 preservation + P2 stand-pat + P5 "
        "track-bcd rollup + 4 honest deferrals + P6 POR shadow-zone hold + P7 "
        "Track F extension + P8 consolidation-hold + housekeeping tail 4 rows). "
        "P3 CONTINGENT and P4 Peach Dream E-5 disclosure do not emit standalone "
        "milestone rows this cycle (preserved in deferral row + rollup).",
    ),
    _mk(
        "_run/cycle_42_closed",
        "validated", "high",
        "c42 CLOSED. Priority 0 status: BLOCKED_ON_OPERATOR - all 6 escalation "
        "memos preserved verbatim (SHOWCASE-1 non-cg-bass c7 [counter 13], "
        "METRIC-SEMANTICS c16 [counter 13], CERT-drums-halt c30 [counter 13], "
        "CERT-v2-halt c31 [counter 12], CERT-guitar-halt c31 [counter 12], "
        "CERT-composite-fp-drift c32 [counter 11]). P1 preservation: "
        "long_exposure/ ABSENT re-probe -> chain-supersede via _selection/"
        "c42-emitter-writer-boundary-preservation (adopts canonical M-1 naming; "
        "supersedes_path points at c41 actual on-disk filename per FD-1 + "
        "invariant (d)). P2 stand-pat continuation: chain-supersede via "
        "_selection/c42-por-drift-preservation. P3 CONTINGENT: no operator "
        "adjudication -> skipped; Track A remains BLOCKED. P4 Peach Dream "
        "stem-manifest divergence (sha c4944ee80...) carried on deferral row. "
        "P5 Track B/C/D honestly deferred (4 rows + 1 rollup). P6 POR shadow-"
        "zone hold verified (parseable=859; brief 858 off-by-one disclosed per "
        "invariant (d); delta 0 vs c41 close; NOT a breach). P7 Track F test "
        "suite extended to 34 in-place + 8 standalone = 42/42 PASS. P8 "
        "consolidation-proposal HOLD (OPT_b keep as READ-ONLY anchor). All 13 "
        "READ-ONLY anchors byte-identical pre==post (objective.py 8087ce80..., "
        "_sweep_hygiene_c27.py 771ff42b..., _serial_lock_op1.py 121809db..., "
        "agent_picks_selection_invariants.md 29a1610b..., "
        "emitter_exemption_policy.md fd2c33a7..., "
        "v4_por_consolidation_strategy_proposal_c40.md 8cffc1c..., 3 fine-fit "
        "drivers 6c80c438/a432e1d1/40dbb673, 3 coarse drivers 3f8bfa08/26aa754c/"
        "d6c54f21, Peach Dream stem_manifest c4944ee8..., 6 escalation "
        "sidecars). env_pin_sha256=2ac444c3... unchanged (canonical 7-key). "
        "NO wait-on-operator memo emitted (BANNED per operator directive "
        "2026-09-03 part 2). Operator ear remains LANDS authority post-hoc "
        "per FD-6. Substantive-heartbeat streak c33->c42 = 11 consecutive "
        "cycles under c36 auditor M-2 terminal contract.",
    ),
    _mk(
        "_archive/cycle-42-scratch",
        "validated", "high",
        "c42 scratch archival housekeeping. tools/_emit_c42_ledger_events.py "
        "retained in-tree per c14+ pattern. Session-scoped scratchpad probes "
        "under harness-managed dir. No workspace scratch to move to "
        "tools/stale/.",
    ),
    _mk(
        "_infra/adopt-cycle42-tests",
        "validated", "high",
        "c42 test-adoption housekeeping. Extended tests/test_c30_legacy_mode_"
        "regression.py in-place with 2 new c42 cases (test_33 + test_34). "
        "Standalone tests/test_fine_fit_serial_lock_c32.py unchanged. No new "
        "test file introduced this cycle (c18 additive-in-place pattern). "
        "Cross-cycle regression total: 34 in-place + 8 standalone = 42 "
        "(advances c41 baseline of 40).",
    ),
]


def main() -> None:
    ledger = ROOT / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    _GUARD.write_text("emitted\n")
    print(f"_emit_c42_ledger_events: {len(EVENTS)} events appended to {ledger}")


if __name__ == "__main__":
    main()
