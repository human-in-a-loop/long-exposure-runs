#!/usr/bin/python3
# ---
# created: 2026-09-05T21:15:00Z
# cycle: 40
# run_id: run-2026-09-05T210000Z
# agent: worker
# milestone: _plan/register-c40-sub-leaves
# ---
"""c40 ledger emitter — idempotent per-turn guard.

Per music_gen_v4_prompt.md c40 brief:
    Priority 0 (BLOCKED): 6 escalations preserved verbatim (no emissions)
    Priority 1: long_exposure/ ABSENT re-probe -> OPT_B chain-supersede. Emits:
        _selection/c40-emitter-writer-boundary-preservation
    Priority 2: STAND-PAT continuation per c36 auditor M-2 terminal contract. Emits:
        _selection/c40-por-drift-preservation
    Priority 3: CONTINGENT (no operator adjudication) - skipped
    Priority 4: DEFERRED (contingent on Priority 3 PATH_A)
    Priority 5: 4 honest-deferral rows (Track B/C/D)
    Priority 6: POR shadow-zone hold verified (parseable=832 delta 0 vs c39)
    Priority 7: Extended tests/test_c30_legacy_mode_regression.py in-place
                (test_29 + test_30) now 30/30 PASS; standalone 8/8 = 38/38
    Priority 8: POR consolidation strategy proposal doc landed (proposal-only,
                7 sections, NEUTRAL recommendation, supersedes_path=null).
    Housekeeping tail:
        _plan/register-c40-sub-leaves
        _run/cycle_40_closed
        _archive/cycle-40-scratch
        _infra/adopt-cycle40-tests

Adheres to the emitter exemption policy (docs/emitter_exemption_policy.md):
    - UUID5 content-hash event_id
    - _STATUS_ENUM values only
    - supersedes_path str or None, never list
    - nested confidence {level, rationale, assessor}
    - canonical-JSON serialization
    - sentinel-guarded idempotency (tools/.c40_ledger_emitted)
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
RUN_ID = "run-2026-09-05T210000Z"
CYCLE = 40
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T21:20:00Z"

_GUARD = ROOT / "tools" / ".c40_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c40_ledger_events: guard present at {_GUARD} - skipping")
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
            "rationale": "c40 substantive-heartbeat cycle deliverable per music_gen_v4_prompt.md c40 brief Priority 0-8",
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
    # -- Priority 1: preservation (long_exposure/ ABSENT re-probe) --
    _mk(
        "_selection/c40-emitter-writer-boundary-preservation",
        "validated", "high",
        "c40 Priority 1 MANDATORY chain-continuation per c35/c36/c37/c38/c39 auditor pattern. "
        "On-disk re-probe of long_exposure/ returned ABSENT "
        "(probe: `test -d long_exposure && echo PRESENT || echo ABSENT`). "
        "c34 OPT_B exemption stands unchanged (chain: c34 fork -> c35 preservation "
        "-> c36 preservation -> c37 preservation -> c38 preservation -> c39 preservation "
        "-> c40 preservation; 6th consecutive). "
        "This preservation event supersedes the c39 event via `supersedes_path` (str "
        "per c14 lemma). No policy change. c39 preservation event sha "
        "a005b75c97bc83fefe29d0bed63aaf3c4189e53e42d39e6119c89df6bed734fd "
        "byte-identical pre==post. docs/emitter_exemption_policy.md sha "
        "fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b "
        "byte-identical pre==post.",
        artifacts=[
            "data/v4/_selection/c40-emitter-writer-boundary-preservation.json",
            "docs/emitter_exemption_policy.md",
        ],
        supersedes_path="data/v4/_selection/c39-emitter-writer-boundary-preservation.json",
        extra={"carried_from_cycle": 34},
    ),

    # -- Priority 2: STAND-PAT (no operator snapshot in live_guidance) --
    _mk(
        "_selection/c40-por-drift-preservation",
        "validated", "high",
        "c40 Priority 2 STAND-PAT continuation per c36 auditor M-2 terminal-"
        "contract codification ('stand-pat remains the correct terminal state "
        "absent operator-supplied snapshot; c37+ mechanically repeats the "
        "pattern'). 7th consecutive stand-pat. live_guidance scanned for "
        "operator-supplied c31/c32 POR snapshot: NONE PRESENT (guidance content "
        "is parallel_cycle_fanout_guidance + campaign_anti_patterns registry only). "
        "Absent-branch of Priority 2 fires: stand-pat preservation event lands "
        "chain-superseding c39 stand-pat. c39 stand-pat (sha "
        "cae433897bd353a8f6c5685916180699eb8ed9e373478f97b27c6553728bce37) "
        "byte-identical pre==post. c38 stand-pat (sha "
        "678307e2a59e85c9e85966b132fe0a4d03ae0cd733d1785e84f12dfaca958e49) "
        "byte-identical pre==post. c35 blocker (sha "
        "c671a40b53565e4ec9ee44513474226aff8085894878e36ba4f68af544d1caad) "
        "byte-identical pre==post. c34 empirical proof + diagnostic (sha "
        "3b0e4d95061a8ad767ce524ae9ffbe1f71fc25a9f8101cd7ed843d5599a78561) "
        "byte-identical pre==post. Attribution finding (Track B/C/D deferrals "
        "account for +4 delta) stands transitively.",
        artifacts=[
            "data/v4/_selection/c40-por-drift-preservation.json",
            "data/v4/_selection/c39-por-drift-preservation.json",
            "data/v4/_selection/c38-por-drift-preservation.json",
            "data/v4/_selection/c35-por-drift-proof-strengthening-blocker.json",
            "data/v4/_selection/c34-por-drift-empirical-proof.json",
            "data/v4/diagnostics/c34_por_delta_proof.json",
        ],
        supersedes_path="data/v4/_selection/c39-por-drift-preservation.json",
        extra={"carried_from_cycle": 34},
    ),

    # -- Priority 5: honest deferrals (Track B/C/D) --
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c40",
        "in-progress", "medium",
        "c40 Track B/Priority 5 Disco A bass stage-2 DEFERRED to c41+ per "
        "Priority 3 gating (contingent on operator adjudication of _manager/"
        "M-V4-CERT-composite-fp-drift-adjudication-c32). No adjudication landed "
        "in live_guidance this cycle. Resume command: detached launch of "
        "`fine_fit_sf2_v2.py --song-sha16 cdd2717e52820ff6` wrapped in OP-1 "
        "SerialLock sentinel (post-c32 driver sha 6c80c438...). SF2_CONFIRMED "
        "remains FORBIDDEN on non-CG bass per preserved M-V4-SHOWCASE-1-non-cg-"
        "bass-acceptance-policy escalation.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c40",
        "in-progress", "medium",
        "c40 Track B/Priority 5 Rome bass stage-2 DEFERRED to c41+ (blocked on "
        "Priority 3 operator adjudication). c23 stage-1 emb_cos_dist=0.5145 "
        "predicts SF2_RULED_OUT under distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c40",
        "in-progress", "medium",
        "c40 Track B/Priority 5 Peach Dream bass stage-2 DEFERRED to c41+ "
        "(blocked on Priority 3 operator adjudication). c23 stage-1 "
        "emb_cos_dist=0.4437 predicts SF2_RULED_OUT. Priority 4 path-divergence "
        "disclosure carried forward: data/v4/profiles/88d247468cb6d49f/"
        "stem_manifest.json records operator_section_c25_checkpointed/rc9_6stem/ "
        "non-standard path per invariant (d) from c19 opening; sha "
        "c4944ee80dfe446b118cf2584e29fa432cc33f21ecdcbe96cc2b63fe946a3b9e "
        "verified byte-identical pre==post this cycle (READ-ONLY anchor).",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c40",
        "in-progress", "medium",
        "c40 Track D/Priority 5 WIG + Disco A drums stage-1 DEFERRED to c41+. "
        "coarse_sweep_sf2_drums.py green regression at c30 (8/8 byte-identical); "
        "coarse sweeps do not require OP-1 (per-song scope, not fine-fit VGGish-"
        "heavy). Additive --song-sha16 kwarg thread required per c28 precedent "
        "for cross-song reuse.",
    ),

    # -- Priority 6: POR shadow-zone hold verified --
    _mk(
        "_selection/c40-por-shadow-zone-hold",
        "validated", "high",
        "c40 Priority 6: POR shadow-zone hold verified. tools/_c32_por_count.py "
        "reports parseable Milestones=832 at c40 open (matches c39-close "
        "baseline of 832 post-registration; c39 open was 820, +12 c39 rows -> "
        "832). Delta 0 vs c39 close. tools/_por_shadow_consolidate_c31.py NOT "
        "re-run per one-shot c14+ convention. c39 auditor M-1 codified 4-point "
        "+12/cycle heartbeat pattern (c36=796 -> c37=808 -> c38=820 -> c39=832) "
        "as structurally honest; c40 continues unchanged mechanically. Priority "
        "8 consolidation-strategy proposal doc landed this cycle at "
        "docs/v4_por_consolidation_strategy_proposal_c40.md (proposal-only, "
        "NEUTRAL, operator/auditor policy call).",
        artifacts=[
            "data/v4/_selection/c40-por-shadow-zone-hold.json",
            "tools/_c32_por_count.py",
        ],
    ),

    # -- Priority 7: Track F extended --
    _mk(
        "_infra/c40-track-f-legacy-regression-test-suite-extended",
        "validated", "high",
        "c40 Priority 7 (Track F) landed. Extended tests/test_c30_legacy_mode_"
        "regression.py in-place with 2 new c40 cases (test_29 c40 long_exposure/ "
        "ABSENT re-probe + preservation chain intact via c39 predecessor sha "
        "check; test_30 c40 POR stand-pat landed + full chain-integrity c39 "
        "predecessor + c38 + c37 + c36 + c35 blocker + c34 diagnostic byte-identical). "
        "Now 30/30 PASS. tests/test_fine_fit_serial_lock_c32.py unchanged at 8/8 PASS. "
        "Cross-cycle total advances c39 36 -> c40 38 (30 in-place + 8 standalone).",
        artifacts=["tests/test_c30_legacy_mode_regression.py"],
    ),

    # -- Priority 8: POR consolidation strategy proposal (NEW artifact class) --
    _mk(
        "_selection/c40-por-consolidation-strategy-proposal",
        "validated", "high",
        "c40 Priority 8: POR consolidation strategy proposal doc landed at "
        "docs/v4_por_consolidation_strategy_proposal_c40.md per c39 auditor M-1 "
        "projection-window recommendation. Doc contains all 7 required sections: "
        "(§1) Problem statement with +12/cycle growth pattern (c36=796 -> c39=832); "
        "(§2) Attribution decomposition (6 structural + 4 deferral + 2 housekeeping); "
        "(§3) Three named consolidation options (OPT_1 rolling-window preservation, "
        "OPT_2 deferral-row rollup, OPT_3 do nothing); (§4) Per-option invariant "
        "compliance (all three PASS under invariants a-e; trade-off does not "
        "resolve via agent-picks); (§5) Chain-integrity concern (all options must "
        "preserve c34 + c35 + c36->c39 lineage byte-identical per FD-1; supersede "
        "via str per c14 lemma, no rewrite); (§6) NEUTRAL recommendation "
        "(operator/auditor policy call parallels c32 composite-FP-drift memo "
        "shape); (§7) Contingent trigger (proposal scoped to sustained-blocked "
        "branch; if operator adjudicates c32 composite-FP-drift, most Priority "
        "4/5 rows retire organically and consolidation becomes moot). This event "
        "has supersedes_path=null (NEW artifact class; no predecessor). NO "
        "consolidation action taken this cycle. Doc becomes READ-ONLY anchor at "
        "c41+ if operator/auditor concurs.",
        artifacts=["docs/v4_por_consolidation_strategy_proposal_c40.md"],
    ),

    # -- Housekeeping tail --
    _mk(
        "_plan/register-c40-sub-leaves",
        "validated", "high",
        "c40 POR registration row: 13 new c40 milestone_ids registered inline in "
        "the `## Milestones` section to satisfy the promise_check POR parser "
        "boundary before `## Sub-milestones`. Priority 1 preservation (1 row) + "
        "Priority 2 stand-pat (1 row) + Priority 5 honest deferrals (4 rows) + "
        "Priority 6 POR shadow-zone hold (1 row) + Priority 7 Track F extension "
        "(1 row) + Priority 8 consolidation-strategy proposal (1 row) + "
        "housekeeping tail (register + closed + scratch + adopt-tests = 4 rows).",
    ),
    _mk(
        "_run/cycle_40_closed",
        "validated", "high",
        "c40 CLOSED. Priority 0 status: BLOCKED_ON_OPERATOR - all 6 escalation "
        "memos preserved verbatim on disk and in-ledger with `carried_from_cycle` "
        "values: SHOWCASE-1-non-cg-bass-acceptance-policy (c7), METRIC-SEMANTICS-"
        "c16 (c16), CERT-fine-fit-sf2-drums-legacy-halt (c30), CERT-fine-fit-sf2-"
        "v2-legacy-halt (c31), CERT-fine-fit-sf2-guitar-legacy-halt (c31), "
        "CERT-composite-fp-drift-adjudication-c32 (c32). Priority 1 preservation: "
        "long_exposure/ ABSENT re-probe -> chain-supersede via `_selection/c40-"
        "emitter-writer-boundary-preservation` (str supersedes_path per c14 lemma "
        "pointing at c39 preservation). Priority 2 stand-pat continuation: no "
        "operator c31/c32 snapshot in live_guidance -> `_selection/c40-por-drift-"
        "preservation` (str supersedes_path pointing at c39 stand-pat; c39 + c38 "
        "+ c37 + c35 blocker + c34 diagnostic all preserved byte-identical). "
        "Priority 3 CONTINGENT: no operator adjudication -> skipped; Track A "
        "remains BLOCKED. Priority 4 Peach Dream stem-manifest divergence (sha "
        "c4944ee80...) carried on deferral row byte-identical. Priority 5 Track "
        "B/C/D honestly deferred (4 rows). Priority 6 POR shadow-zone hold "
        "verified (parseable Milestones=832, delta 0 vs c39 close). Priority 7 "
        "Track F test-suite extended to 30 in-place + 8 standalone = 38/38 PASS. "
        "Priority 8 POR consolidation strategy proposal doc landed (7 sections, "
        "NEUTRAL, supersedes_path=null). NO wait-on-operator memo emitted (BANNED "
        "per operator directive 2026-09-03 part 2). All 13 READ-ONLY anchors "
        "byte-identical pre==post: objective.py 8087ce80..., _sweep_hygiene_c27.py "
        "771ff42b..., _serial_lock_op1.py 121809db..., "
        "agent_picks_selection_invariants.md 29a1610b..., "
        "emitter_exemption_policy.md fd2c33a7..., cg_ab_mix.wav 6e13e007..., "
        "3 fine-fit drivers 6c80c438/a432e1d1/40dbb673, 3 coarse-sweep drivers "
        "3f8bfa08/26aa754c/d6c54f21, Peach Dream stem_manifest c4944ee8..., "
        "6 escalation sidecars under data/v4/_manager/ byte-identical. "
        "env_pin_sha256=2ac444c3... unchanged (canonical 7-key subset). "
        "Operator ear remains LANDS authority post-hoc per FD-6.",
    ),
    _mk(
        "_archive/cycle-40-scratch",
        "validated", "high",
        "c40 scratch archival housekeeping. tools/_emit_c40_ledger_events.py "
        "retained in-tree per c14+ pattern. Session-scoped scratchpad probes "
        "live under harness-managed dir. No workspace scratch to move to "
        "`tools/stale/`.",
    ),
    _mk(
        "_infra/adopt-cycle40-tests",
        "validated", "high",
        "c40 test-adoption housekeeping. Extended tests/test_c30_legacy_mode_"
        "regression.py in-place with 2 new c40 cases (test_29 + test_30). "
        "Standalone tests/test_fine_fit_serial_lock_c32.py unchanged. No new "
        "test file introduced this cycle (per c18 additive-in-place pattern). "
        "Cross-cycle regression total: 30 in-place + 8 standalone = 38 (advances "
        "c39 baseline of 36).",
    ),
]


def main() -> None:
    ledger = ROOT / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    _GUARD.write_text("emitted\n")
    print(f"_emit_c40_ledger_events: {len(EVENTS)} events appended to {ledger}")


if __name__ == "__main__":
    main()
