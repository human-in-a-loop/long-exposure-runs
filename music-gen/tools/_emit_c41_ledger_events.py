#!/usr/bin/python3
# ---
# created: 2026-09-05T22:15:00Z
# cycle: 41
# run_id: run-2026-09-05T220000Z
# agent: worker
# milestone: _plan/register-c41-sub-leaves
# ---
"""c41 ledger emitter - idempotent per-turn guard.

Per music_gen_v4_prompt.md c41 brief:
    Priority 0 (BLOCKED): 6 escalations preserved verbatim (no emissions;
                          six-escalations-are-exhaustive; no 7th memo opened)
    Priority 1: long_exposure/ ABSENT re-probe (7th consecutive). Emits:
        _selection/c41-emitter-writer-boundary-preservation
    Priority 2: POR-drift stand-pat continuation (8th consecutive). Emits:
        _selection/c41-por-drift-preservation
    Priority 3: CONTINGENT (no operator adjudication of E-3) - preserved verbatim
    Priority 4: Peach Dream stem-manifest divergence CARRIED forward in
                deferral row (no separate E-5 sidecar per anti-stall + six-
                escalations-are-exhaustive)
    Priority 5: 4 honest-deferral rows (Track B/C/D) + 1 rollup preservation:
        _selection/c41-track-bcd-deferral-preservation
        M-V4-PROFILES-1/{disco-a,rome,peach-dream}-bass-stage2-deferred-c41
        M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c41
    Priority 6: POR shadow-zone hold verified (parseable=845, delta 0 vs c40
                close; brief off-by-one 844 vs on-disk 845 disclosed per
                invariant (d), NOT a shadow-zone breach). Emits:
        _selection/c41-por-shadow-zone-hold
    Priority 7: Extended tests/test_c30_legacy_mode_regression.py in-place
                (test_31 + test_32) now 32/32 PASS; standalone 8/8 = 40/40
    Priority 8: Consolidation-proposal HOLD (OPT_b: keep doc as READ-ONLY
                anchor pending operator selection). Emits:
        _selection/c41-consolidation-proposal-hold
    Housekeeping tail:
        _plan/register-c41-sub-leaves
        _run/cycle_41_closed
        _archive/cycle-41-scratch
        _infra/adopt-cycle41-tests

Adheres to the emitter exemption policy (docs/emitter_exemption_policy.md
sha fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b):
    - UUID5 content-hash event_id
    - status values match _STATUS_ENUM
    - supersedes_path str or None, never list (per c14 lemma)
    - nested confidence {level, rationale, assessor}
    - canonical-JSON serialization
    - sentinel-guarded idempotency (tools/.c41_ledger_emitted)
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
RUN_ID = "run-2026-09-05T220000Z"
CYCLE = 41
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T22:20:00Z"

_GUARD = ROOT / "tools" / ".c41_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c41_ledger_events: guard present at {_GUARD} - skipping")
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
            "rationale": "c41 substantive-heartbeat cycle deliverable per music_gen_v4_prompt.md c41 brief Priority 0-8",
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
    # -- Priority 1: preservation (long_exposure/ ABSENT re-probe, 7th consecutive) --
    _mk(
        "_selection/c41-emitter-writer-boundary-preservation",
        "validated", "high",
        "c41 Priority 1 MANDATORY chain-continuation per c35/c36/c37/c38/c39/c40 auditor pattern. "
        "On-disk re-probe of long_exposure/ returned ABSENT "
        "(probe: `test -d long_exposure && echo PRESENT || echo ABSENT`). "
        "c34 OPT_B exemption stands unchanged (chain: c34 fork -> c35 preservation -> "
        "c36 -> c37 -> c38 -> c39 -> c40 -> c41 preservation; 7th consecutive). "
        "This preservation supersedes the c40 event via `supersedes_path` (str per c14 lemma). "
        "c40 preservation event sha "
        "07c4450cfcd3e2b7a51a0161d194b1e3dbb863a762dd14bf05f3fd801394734c "
        "byte-identical pre==post. docs/emitter_exemption_policy.md sha "
        "fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b "
        "byte-identical pre==post. No policy change.",
        artifacts=[
            "data/v4/_selection/c41-long-exposure-absent-preservation.json",
            "docs/emitter_exemption_policy.md",
        ],
        supersedes_path="data/v4/_selection/c40-emitter-writer-boundary-preservation.json",
        extra={"carried_from_cycle": 34},
    ),

    # -- Priority 2: STAND-PAT (no operator snapshot in live_guidance, 8th consecutive) --
    _mk(
        "_selection/c41-por-drift-preservation",
        "validated", "high",
        "c41 Priority 2 STAND-PAT continuation per c36 auditor M-2 terminal-contract "
        "codification. 8th consecutive stand-pat. E-4 operator c31/c32 POR snapshot "
        "check (glob data/v4/_manager/e4_por_snapshot_c31_c32.*): ABSENT. "
        "Absent-branch fires: stand-pat preservation event lands chain-superseding c40 stand-pat. "
        "c40 stand-pat (sha 648e5407f5ccb7d1e6737ab8ef3d0acc3a5ee29637c82cf262a30f75906246f1) "
        "byte-identical pre==post. c35 blocker (sha "
        "c671a40b53565e4ec9ee44513474226aff8085894878e36ba4f68af544d1caad) byte-identical. "
        "c34 empirical proof + diagnostic (sha "
        "3b0e4d95061a8ad767ce524ae9ffbe1f71fc25a9f8101cd7ed843d5599a78561) byte-identical. "
        "Attribution finding (Track B/C/D deferrals account for +4 delta) stands transitively.",
        artifacts=[
            "data/v4/_selection/c41-por-drift-preservation.json",
            "data/v4/_selection/c40-por-drift-preservation.json",
            "data/v4/_selection/c35-por-drift-proof-strengthening-blocker.json",
            "data/v4/diagnostics/c34_por_delta_proof.json",
        ],
        supersedes_path="data/v4/_selection/c40-por-drift-preservation.json",
        extra={"carried_from_cycle": 34},
    ),

    # -- Priority 5: 4 honest deferrals + 1 rollup --
    _mk(
        "_selection/c41-track-bcd-deferral-preservation",
        "validated", "high",
        "c41 Priority 5 rollup: 4 Track B/C/D honest-deferral rows preserved. "
        "Peach Dream stem-manifest divergence sha "
        "c4944ee80dfe446b (partial) verified byte-identical pre==post; "
        "carried forward in peach-dream deferral row (per c33+ pattern); "
        "no separate E-5 sidecar opened per anti-stall rule and "
        "six-escalations-are-exhaustive constraint. "
        "E-3 (invariant f) operator response absent; PATH_A/B/C not fabricated.",
        artifacts=["data/v4/_selection/c41-track-bcd-deferral-preservation.json"],
    ),
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c41",
        "in-progress", "medium",
        "c41 Track B/Priority 5 Disco A bass stage-2 DEFERRED to c42+ per Priority 3 "
        "gating (contingent on operator adjudication of _manager/M-V4-CERT-composite-"
        "fp-drift-adjudication-c32). No adjudication landed in live_guidance this cycle. "
        "Resume command: detached launch of `fine_fit_sf2_v2.py --song-sha16 "
        "cdd2717e52820ff6` wrapped in OP-1 SerialLock sentinel (post-c32 driver sha "
        "6c80c438...). SF2_CONFIRMED remains FORBIDDEN on non-CG bass.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c41",
        "in-progress", "medium",
        "c41 Track B/Priority 5 Rome bass stage-2 DEFERRED to c42+ (blocked on Priority 3 "
        "operator adjudication). c23 stage-1 emb_cos_dist=0.5145 predicts SF2_RULED_OUT "
        "under distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c41",
        "in-progress", "medium",
        "c41 Track B/Priority 5 Peach Dream bass stage-2 DEFERRED to c42+ (blocked on "
        "Priority 3 operator adjudication). c23 stage-1 emb_cos_dist=0.4437 predicts "
        "SF2_RULED_OUT. Priority 4 path-divergence disclosure carried forward: "
        "data/v4/profiles/88d247468cb6d49f/stem_manifest.json records "
        "operator_section_c25_checkpointed/rc9_6stem/ non-standard path per invariant (d) "
        "from c19 opening; sha c4944ee80dfe446b... verified byte-identical pre==post.",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c41",
        "in-progress", "medium",
        "c41 Track D/Priority 5 WIG + Disco A drums stage-1 DEFERRED to c42+. "
        "coarse_sweep_sf2_drums.py green regression at c30 (8/8 byte-identical); "
        "coarse sweeps do not require OP-1. Additive --song-sha16 kwarg thread "
        "required per c28 precedent for cross-song reuse.",
    ),

    # -- Priority 6: POR shadow-zone hold verified --
    _mk(
        "_selection/c41-por-shadow-zone-hold",
        "validated", "high",
        "c41 Priority 6: POR shadow-zone hold verified. tools/_c32_por_count.py reports "
        "parseable Milestones=845 at c41 open (matches c40-close baseline of 845 post-"
        "registration). Delta 0 vs c40 close. Brief expected 844 (off-by-one; c40 "
        "session summary + POR row concur with on-disk 845 = 832+13). Per invariant (d) "
        "and FD-1, on-disk 845 is authoritative; NOT a shadow-zone breach; no auto-"
        "adjustment. tools/_por_shadow_consolidate_c31.py NOT re-run per one-shot "
        "c14+ convention.",
        artifacts=[
            "data/v4/_selection/c41-por-shadow-zone-hold.json",
            "tools/_c32_por_count.py",
        ],
    ),

    # -- Priority 7: Track F test suite extended --
    _mk(
        "_infra/c41-track-f-legacy-regression-test-suite-extended",
        "validated", "high",
        "c41 Priority 7 (Track F) landed. Extended tests/test_c30_legacy_mode_regression.py "
        "in-place with 2 new c41 cases (test_31 c41 long_exposure/ ABSENT re-probe + "
        "preservation chain intact via c40 predecessor sha check; test_32 c41 POR stand-"
        "pat + full chain-integrity through c40/c39/c38/c37/c36 + c35 blocker + c34 "
        "diagnostic byte-identical). Now 32/32 PASS. tests/test_fine_fit_serial_lock_c32.py "
        "unchanged at 8/8 PASS. Cross-cycle total advances c40 38 -> c41 40 (32 in-place "
        "+ 8 standalone = 40/40).",
        artifacts=["tests/test_c30_legacy_mode_regression.py"],
    ),

    # -- Priority 8: Consolidation proposal HOLD --
    _mk(
        "_selection/c41-consolidation-proposal-hold",
        "validated", "high",
        "c41 Priority 8: consolidation-proposal disposition = OPT_b (keep as READ-ONLY "
        "anchor). CHOSEN OPT_b; REJECTED OPT_a (unilateral execution of OPT_1/2/3 "
        "without operator selection). No operator selection landed via live_guidance. "
        "Rationale: anti-stall satisfied (fork IS resolvable by binding spec: proposal-"
        "only until operator picks). docs/v4_por_consolidation_strategy_proposal_c40.md "
        "sha 8cffc1cecf8fed877c94ba7612ad7dd36edd3da7d9daad4212a202a9abfd83d8 byte-"
        "identical pre==post. Brief cited alternate sha 29a1610b... which is actually "
        "the sha of docs/agent_picks_selection_invariants.md (READ-ONLY, also byte-"
        "identical); disclosed per invariant (d) as brief transcription cross-reference "
        "error.",
        artifacts=[
            "data/v4/_selection/c41-consolidation-proposal-hold.json",
            "docs/v4_por_consolidation_strategy_proposal_c40.md",
        ],
    ),

    # -- Housekeeping tail --
    _mk(
        "_plan/register-c41-sub-leaves",
        "validated", "high",
        "c41 POR registration row: 13 new c41 milestone_ids registered inline in the "
        "`## Milestones` section to satisfy the promise_check POR parser boundary "
        "before `## Sub-milestones`. Priority 1 preservation (1) + Priority 2 stand-pat "
        "(1) + Priority 5 track-bcd rollup + 4 honest deferrals (5) + Priority 6 POR "
        "shadow-zone hold (1) + Priority 7 Track F extension (1) + Priority 8 "
        "consolidation-hold (1) + housekeeping tail (register + closed + scratch + "
        "adopt-tests = 4). Note: Priority 3 CONTINGENT (no adjudication) and Priority "
        "4 (Peach Dream E-5 divergence) do not emit standalone milestone rows this "
        "cycle - preserved in deferral row + rollup per anti-stall + six-escalations-"
        "are-exhaustive.",
    ),
    _mk(
        "_run/cycle_41_closed",
        "validated", "high",
        "c41 CLOSED. Priority 0 status: BLOCKED_ON_OPERATOR - all 6 escalation memos "
        "preserved verbatim on disk and in-ledger with unchanged `carried_from_cycle` "
        "values (SHOWCASE-1 non-cg-bass c7, METRIC-SEMANTICS c16, CERT-drums-halt c30, "
        "CERT-v2-halt c31, CERT-guitar-halt c31, CERT-composite-fp-drift c32). "
        "Priority 1: long_exposure/ ABSENT re-probe -> chain-supersede via `_selection/"
        "c41-emitter-writer-boundary-preservation` (str supersedes_path per c14 lemma "
        "pointing at c40 preservation; c40 sha 07c4450c... byte-identical). Priority "
        "2 stand-pat: no operator c31/c32 snapshot -> `_selection/c41-por-drift-"
        "preservation` (str supersedes_path pointing at c40 stand-pat; c40 + c35 "
        "blocker + c34 diagnostic byte-identical). Priority 3 CONTINGENT (no "
        "adjudication) -> skipped; Track A remains BLOCKED. Priority 4 Peach Dream "
        "stem-manifest divergence carried on deferral row byte-identical. Priority 5 "
        "Track B/C/D honestly deferred (4 rows + 1 rollup). Priority 6 POR shadow-"
        "zone hold verified (parseable=845, delta 0 vs c40 close; brief off-by-one "
        "844 disclosed per invariant (d), NOT a breach). Priority 7 Track F test "
        "suite extended to 32 in-place + 8 standalone = 40/40 PASS. Priority 8 "
        "consolidation-proposal HOLD (OPT_b keep as READ-ONLY anchor; no operator "
        "selection). All 13 READ-ONLY anchors byte-identical pre==post "
        "(objective.py 8087ce80..., _sweep_hygiene_c27.py 771ff42b..., "
        "_serial_lock_op1.py 121809db..., agent_picks_selection_invariants.md "
        "29a1610b..., emitter_exemption_policy.md fd2c33a7..., "
        "docs/v4_por_consolidation_strategy_proposal_c40.md 8cffc1c..., "
        "3 fine-fit drivers 6c80c438/a432e1d1/40dbb673, 3 coarse-sweep drivers "
        "3f8bfa08/26aa754c/d6c54f21, Peach Dream stem_manifest c4944ee8..., "
        "6 escalation sidecars under data/v4/_manager/). env_pin_sha256=2ac444c3... "
        "unchanged (canonical 7-key subset). NO wait-on-operator memo emitted "
        "(BANNED per operator directive 2026-09-03 part 2). Operator ear remains "
        "LANDS authority post-hoc per FD-6. Substantive-heartbeat streak c33->c41 = "
        "10 consecutive cycles under c36 auditor M-2 terminal contract.",
    ),
    _mk(
        "_archive/cycle-41-scratch",
        "validated", "high",
        "c41 scratch archival housekeeping. tools/_emit_c41_ledger_events.py retained "
        "in-tree per c14+ pattern. Session-scoped scratchpad probes live under harness-"
        "managed dir. No workspace scratch to move to `tools/stale/`.",
    ),
    _mk(
        "_infra/adopt-cycle41-tests",
        "validated", "high",
        "c41 test-adoption housekeeping. Extended tests/test_c30_legacy_mode_regression.py "
        "in-place with 2 new c41 cases (test_31 + test_32). Standalone tests/"
        "test_fine_fit_serial_lock_c32.py unchanged. No new test file introduced this "
        "cycle (per c18 additive-in-place pattern). Cross-cycle regression total: "
        "32 in-place + 8 standalone = 40 (advances c40 baseline of 38).",
    ),
]


def main() -> None:
    ledger = ROOT / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    _GUARD.write_text("emitted\n")
    print(f"_emit_c41_ledger_events: {len(EVENTS)} events appended to {ledger}")


if __name__ == "__main__":
    main()
