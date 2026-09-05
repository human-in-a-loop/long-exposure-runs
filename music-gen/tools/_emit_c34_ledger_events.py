#!/usr/bin/python3
# ---
# created: 2026-09-05T07:30:00Z
# cycle: 34
# run_id: run-2026-09-05T070000Z
# agent: worker
# milestone: _plan/register-c34-sub-leaves
# ---
"""c34 ledger emitter — idempotent per-turn guard.

Per music_gen_v4_prompt.md c34 brief:
    Priority 0 (BLOCKED): 6 escalations preserved verbatim (no emissions)
    Priority 1: OPT_B forked (long_exposure/ absent). Emits:
        _infra/emitter-writer-boundary-exemption-c34
        _selection/c34-emitter-writer-boundary
    Priority 2: Empirical proof landed with amended attribution. Emits:
        _selection/c34-por-drift-empirical-proof
        (supersedes c33 event via str `supersedes_path` per c14 lemma)
    Priority 3: CONTINGENT (no operator adjudication) - skipped
    Priority 4: Peach Dream disclosure carried on deferral row
    Priority 5: 4 honest-deferral rows (Track B/C/D)
    Priority 6: POR shadow-zone hold verified (parseable=759 delta 0 vs c33)
    Priority 7: Extended tests/test_c30_legacy_mode_regression.py in-place
                (test_17 + test_18) now 18/18 PASS
    Housekeeping tail:
        _plan/register-c34-sub-leaves
        _run/cycle_34_closed
        _archive/cycle-34-scratch
        _infra/adopt-cycle34-tests

Adheres to the emitter exemption policy (docs/emitter_exemption_policy.md):
    - UUID5 content-hash event_id
    - _STATUS_ENUM values only
    - supersedes_path str or None, never list
    - nested confidence {level, rationale, assessor}
    - canonical-JSON serialization
    - sentinel-guarded idempotency (tools/.c34_ledger_emitted)
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
RUN_ID = "run-2026-09-05T070000Z"
CYCLE = 34
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T07:30:00Z"

_GUARD = ROOT / "tools" / ".c34_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c34_ledger_events: guard present at {_GUARD} - skipping")
    sys.exit(0)


def _mk(mid: str, status: str, level: str, narrative: str,
        artifacts: list[str] | None = None,
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
            "rationale": "c34 substantive-cycle deliverable per music_gen_v4_prompt.md c34 brief Priority 0-7",
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


EVENTS: list[dict] = [
    # -- Priority 1: OPT_B emitter exemption policy + fork --
    _mk(
        "_infra/emitter-writer-boundary-exemption-c34",
        "validated", "high",
        "c34 Priority 1 OPT_B (auto-resolved). long_exposure/ package NOT importable "
        "in workspace (probe: `ls long_exposure/` -> 'No such file or directory'); "
        "OPT_A (route c34 emitter through long_exposure.workspace_bootstrap."
        "append_ledger_event) is unreachable. Formal exemption for the "
        "tools/_emit_c*_ledger_events chain landed at docs/emitter_exemption_policy.md "
        "(sha fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b). "
        "Doc codifies the 8-item contract the exempted chain honors: UUID5 content-hash "
        "event_id, _STATUS_ENUM status, supersedes_path str|null, nested confidence, "
        "canonical-JSON serialization, pinned run_id + env_pin + cycle, "
        "sentinel-guarded idempotency. Fork event at "
        "data/v4/_selection/c34-emitter-writer-boundary.json invariant-compliant.",
        artifacts=[
            "docs/emitter_exemption_policy.md",
            "data/v4/_selection/c34-emitter-writer-boundary.json",
        ],
    ),
    _mk(
        "_selection/c34-emitter-writer-boundary",
        "validated", "high",
        "c34 Priority 1 fork registration. CHOSEN=OPT_B (document formal exemption); "
        "REJECTED=OPT_A (long_exposure/ absent, unreachable) + OPT_C (would leave the "
        "c33 MODERATE as debt, below-line per invariant (b)). AUTHORITY: campaign "
        "prompt anti-stall rule + operator directive 2026-09-03 part 2 + agent-picks "
        "invariants (a)-(e). supersedes_path=null (new escalation class).",
        artifacts=[
            "data/v4/_selection/c34-emitter-writer-boundary.json",
        ],
    ),

    # -- Priority 2: empirical proof with amended attribution --
    _mk(
        "_selection/c34-por-drift-empirical-proof",
        "validated", "high",
        "c34 Priority 2 LANDED. Empirical proof of c31-close (728) -> c32-open (732) "
        "+4 parseable-Milestones delta. c33 hypothesis MAGNITUDE correct (+4) but "
        "ATTRIBUTION wrong: c33 attributed to housekeeping tail rows "
        "(_plan/register-c31-sub-leaves + _run/cycle_31_closed + _archive/"
        "cycle-31-scratch + _infra/adopt-cycle31-tests). Fresh probe shows: those 4 "
        "rows exist as LEDGER events but NOT as parseable-head or shadow-zone POR "
        "rows. Alternate hypothesis CONFIRMED: +4 delta = 4 c31 Track B/C/D "
        "honest-deferral rows (disco-a-bass-stage2-deferred-c31, rome-bass-stage2-"
        "deferred-c31, peach-dream-bass-stage2-deferred-c31, wig-disco-a-drums-"
        "stage1-deferred-c31). c33 event content byte-identical pre==post per FD-1 + "
        "invariant (d); correction stacks via supersede. Diagnostic at "
        "data/v4/diagnostics/c34_por_delta_proof.json (sha "
        "3b0e4d95061a8ad767ce524ae9ffbe1f71fc25a9f8101cd7ed843d5599a78561).",
        artifacts=[
            "data/v4/_selection/c34-por-drift-empirical-proof.json",
            "data/v4/diagnostics/c34_por_delta_proof.json",
        ],
        supersedes_path="data/v4/_selection/c33-por-shadow-drift-disclosure-retroactive-for-c32.json",
        extra={"carried_from_cycle": 33},
    ),

    # -- Priority 5: honest deferrals (Track B/C/D) --
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c34",
        "in-progress", "medium",
        "c34 Track B Disco A bass stage-2 DEFERRED to c35+ per Priority 3 gating "
        "(contingent on operator adjudication of _manager/M-V4-CERT-composite-fp-"
        "drift-adjudication-c32). No adjudication landed in live_guidance this cycle. "
        "Resume command: detached launch of `fine_fit_sf2_v2.py --song-sha16 "
        "cdd2717e52820ff6` wrapped in OP-1 SerialLock sentinel (post-c32 sha "
        "6c80c438...). SF2_CONFIRMED remains FORBIDDEN on non-CG bass per preserved "
        "M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy escalation.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c34",
        "in-progress", "medium",
        "c34 Track B Rome bass stage-2 DEFERRED to c35+ (blocked on Priority 3 "
        "operator adjudication). c23 stage-1 emb_cos_dist=0.5145 predicts "
        "SF2_RULED_OUT under distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c34",
        "in-progress", "medium",
        "c34 Track B Peach Dream bass stage-2 DEFERRED to c35+ (blocked on Priority "
        "3 operator adjudication). c23 stage-1 emb_cos_dist=0.4437 predicts "
        "SF2_RULED_OUT. Priority 4 path-divergence note carried forward: "
        "data/v4/profiles/88d247468cb6d49f/stem_manifest.json records "
        "operator_section_c25_checkpointed/rc9_6stem/ non-standard path per "
        "invariant (d) disclosure from c19 opening; sha c4944ee80dfe446b... verified "
        "byte-identical pre==post this cycle (READ-ONLY anchor).",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c34",
        "in-progress", "medium",
        "c34 Track B WIG + Disco A drums stage-1 DEFERRED to c35+. "
        "coarse_sweep_sf2_drums.py green regression at c30 (8/8 byte-identical); "
        "coarse sweeps do not require OP-1 (per-song scope, not fine-fit "
        "VGGish-heavy). Additive --song-sha16 kwarg thread required per c28 "
        "precedent for cross-song reuse.",
    ),

    # -- Priority 6: POR shadow-zone hold verified --
    _mk(
        "_plan/por-shadow-zone-hold-verified-c34",
        "validated", "high",
        "c34 Priority 6: POR shadow-zone hold verified. tools/_c32_por_count.py "
        "reports parseable Milestones=759 at c34 open (matches c33-close baseline "
        "of 759 per c33 rollup post-registration). Delta 0 vs c33 close. "
        "tools/_por_shadow_consolidate_c31.py NOT re-run per one-shot c14+ "
        "convention.",
    ),

    # -- Priority 7: Track F extended --
    _mk(
        "_infra/c34-track-f-legacy-regression-test-suite-extended",
        "validated", "high",
        "c34 Priority 7 (Track F) landed. Extended "
        "tests/test_c30_legacy_mode_regression.py in-place with 2 new c34 cases "
        "(test_17 c34 emitter-exemption OPT_B doc + fork event; test_18 c34 "
        "empirical proof landing with amended attribution). Now 18/18 PASS. "
        "tests/test_fine_fit_serial_lock_c32.py unchanged at 8/8 PASS. "
        "Cross-cycle total advances c33 24 -> c34 26 (18 in-place + 8 standalone).",
        artifacts=["tests/test_c30_legacy_mode_regression.py"],
    ),

    # -- Housekeeping tail --
    _mk(
        "_plan/register-c34-sub-leaves",
        "validated", "high",
        "c34 POR registration row: new c34 milestone_ids registered inline in the "
        "`## Milestones` section to satisfy the promise_check POR parser boundary "
        "before `## Sub-milestones`. Priority 1 emitter-exemption + fork (2 rows) + "
        "Priority 2 empirical proof supersede (1 row) + Priority 5 honest deferrals "
        "(4 rows) + Priority 6 POR shadow-zone hold + Priority 7 Track F extension + "
        "housekeeping tail (register + closed + scratch + adopt-tests).",
    ),
    _mk(
        "_run/cycle_34_closed",
        "validated", "high",
        "c34 CLOSED. Priority 0 status: BLOCKED_ON_OPERATOR - all 6 escalation memos "
        "preserved verbatim on disk and in-ledger (SHOWCASE-1-non-cg-bass-acceptance-"
        "policy c7, METRIC-SEMANTICS-c16 c16, CERT-fine-fit-sf2-drums-legacy-halt "
        "c30, CERT-fine-fit-sf2-v2-legacy-halt c31, CERT-fine-fit-sf2-guitar-legacy-"
        "halt c31, CERT-composite-fp-drift-adjudication-c32 c32). Priority 1 fork "
        "outcome: OPT_B (long_exposure/ absent from workspace, auto-resolved). "
        "Priority 2 empirical proof: LANDED with amended attribution (c33 hypothesis "
        "MAGNITUDE correct, ATTRIBUTION wrong; corrected via supersede pointing at "
        "the 4 c31 Track B/C/D deferral rows). Priority 3 CONTINGENT: no operator "
        "adjudication in live_guidance this cycle -> skipped; Track A remains "
        "BLOCKED. Priority 4 Peach Dream stem-manifest divergence (sha c4944ee80..) "
        "carried on deferral row byte-identical. Priority 5 Track B/C/D honestly "
        "deferred (4 rows). Priority 6 POR shadow-zone hold verified (parseable "
        "Milestones = 759, delta 0 vs c33 close). Priority 7 Track F test-suite "
        "extended to 18 in-place + 8 standalone = 26/26 PASS. NO wait-on-operator "
        "memo emitted (BANNED per operator directive 2026-09-03 part 2; genuine "
        "operator-authority carve-out satisfied by preserved consolidation memo). "
        "All READ-ONLY anchors byte-identical pre==post: objective.py 8087ce80..., "
        "_sweep_hygiene_c27.py 771ff42b..., _serial_lock_op1.py 121809db..., "
        "agent_picks_selection_invariants.md 29a1610b..., cg_ab_mix.wav 6e13e007..., "
        "3 fine-fit drivers 6c80c438/a432e1d1/40dbb673, 3 coarse-sweep drivers "
        "3f8bfa08/26aa754c/d6c54f21, Peach Dream stem_manifest c4944ee8.... "
        "env_pin_sha256=2ac444c3... unchanged. Operator ear remains LANDS authority "
        "post-hoc per FD-6.",
    ),
    _mk(
        "_archive/cycle-34-scratch",
        "validated", "high",
        "c34 scratch archival housekeeping. tools/_emit_c34_ledger_events.py "
        "retained in-tree per c14+ pattern. Priority 2 empirical-probe scratch "
        "(probe_por*.py) lives under session-scoped scratchpad (harness-managed). "
        "No workspace scratch to move to `tools/stale/`.",
    ),
    _mk(
        "_infra/adopt-cycle34-tests",
        "validated", "high",
        "c34 test-adoption housekeeping. Extended "
        "tests/test_c30_legacy_mode_regression.py in-place with 2 new c34 cases "
        "(test_17 + test_18). Standalone tests/test_fine_fit_serial_lock_c32.py "
        "unchanged. No new test file introduced this cycle (per c18 additive-in-"
        "place pattern). Cross-cycle regression total: 18 in-place + 8 standalone = "
        "26 (advances c33 baseline of 24).",
    ),
]


def main() -> None:
    ledger = ROOT / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    _GUARD.write_text("emitted\n")
    print(f"_emit_c34_ledger_events: {len(EVENTS)} events appended to {ledger}")


if __name__ == "__main__":
    main()
