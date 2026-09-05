#!/usr/bin/python3
# ---
# created: 2026-09-05T06:00:00Z
# cycle: 33
# run_id: run-2026-09-05T060000Z
# agent: worker
# milestone: _plan/register-c33-sub-leaves
# ---
"""c33 ledger emitter — idempotent per-turn guard.

Emits the c33 substantive + housekeeping ledger events per cycle-33 brief:
    Priority 0 (BLOCKED): 6 escalations preserved verbatim (no emissions)
    Priority 1: _manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt      (backfill)
                 _manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt  (backfill)
                 _plan/register-c33-manager-json-sidecar-backfill
    Priority 2: _selection/c33-por-shadow-drift-disclosure-retroactive-for-c32
    Priority 3: CONTINGENT (no operator adjudication) — skipped
    Priority 4: Peach Dream disclosure carried on deferral row
    Priority 5: 4 honest-deferral rows (Track B/C/D)
    Priority 6: _plan/por-shadow-zone-hold-verified-c33
    Priority 7: _infra/c33-track-f-legacy-regression-test-suite-extended
    Housekeeping tail:
        _plan/register-c33-sub-leaves
        _run/cycle_33_closed
        _archive/cycle-33-scratch
        _infra/adopt-cycle33-tests
"""
from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

_NAMESPACE = uuid.NAMESPACE_URL


def _event_id(ev: dict) -> str:
    body = {k: v for k, v in ev.items() if k not in ("event_id", "ts")}
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(_NAMESPACE, payload))


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "run-2026-09-05T060000Z"
CYCLE = 33
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T06:30:00Z"

_GUARD = ROOT / "tools" / ".c33_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c33_ledger_events: guard present at {_GUARD} — skipping (idempotent)")
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
            "rationale": "c33 substantive-cycle deliverable per music_gen_v4_prompt.md c33 brief Priority 0-7",
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
    # -- Priority 1: JSON sidecar backfill (bass v2 + guitar halt memos) --
    _mk(
        "_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt",
        "action_required", "high",
        "c33 Priority 1 JSON sidecar backfill (closes c32 auditor MODERATE #1). "
        "Escalation was previously ledger-event-only (c31 event_id "
        "1c288c4f-eb82-525a-95bb-402b17bab776); on-disk sidecar authored to mirror "
        "drums-halt (c30) shape verbatim. Content sourced from c31 ledger event "
        "narrative + related _infra/c31-cg-anchor-regression-fine-fit-sf2-v2 "
        "diagnostic (216/216 render byte-identical, 109/216 composite strict-equal, "
        "107 FP-drift ~1e-6 with matching render SHAs). "
        "status=action_required, authority=OPERATOR, blocked_on_operator=true, "
        "carried_from_cycle=31 (original escalation cycle preserved per FD-1 honesty). "
        "Cross-linked from consolidation memo M-V4-CERT-composite-fp-drift-adjudication-c32.",
        artifacts=["data/v4/_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt.json"],
        extra={"authority": "OPERATOR", "blocked_on_operator": True, "carried_from_cycle": 31},
    ),
    _mk(
        "_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt",
        "action_required", "high",
        "c33 Priority 1 JSON sidecar backfill (closes c32 auditor MODERATE #1). "
        "Escalation was previously ledger-event-only (c31 event_id "
        "43830b3b-938f-5f0f-b92d-9a58ab742f8f); on-disk sidecar authored to mirror "
        "drums-halt (c30) shape verbatim. Content: 180/180 render byte-identical, "
        "98/180 composite strict-equal, 82 FP-drift cells. "
        "status=action_required, authority=OPERATOR, blocked_on_operator=true, "
        "carried_from_cycle=31. Cross-linked from consolidation memo "
        "M-V4-CERT-composite-fp-drift-adjudication-c32. All six escalations now "
        "discoverable via `ls data/v4/_manager/` in addition to ledger grep.",
        artifacts=["data/v4/_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt.json"],
        extra={"authority": "OPERATOR", "blocked_on_operator": True, "carried_from_cycle": 31},
    ),
    _mk(
        "_plan/register-c33-manager-json-sidecar-backfill",
        "validated", "high",
        "c33 Priority 1 rollup: 2 JSON sidecars authored on-disk under "
        "data/v4/_manager/ to close c32 auditor MODERATE #1 (JSON sidecar hygiene "
        "backfill for bass-v2 + guitar halt escalations). Both memos mirror the c30 "
        "drums-halt shape verbatim (13 top-level keys incl. status/authority/"
        "blocked_on_operator/three-path structure/diagnostic evidence/invariants "
        "analysis/neutral recommendation). Cross-linked from consolidation memo "
        "(link SHAs verified valid post-backfill). The three predecessor halt "
        "memos remain OPEN (blocked_on_operator=true, unchanged); consolidation "
        "memo remains OPEN. No operator adjudication landed this cycle.",
        artifacts=[
            "data/v4/_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt.json",
            "data/v4/_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt.json",
        ],
    ),

    # -- Priority 2: retroactive _selection/ event for c31->c32 POR delta --
    _mk(
        "_selection/c33-por-shadow-drift-disclosure-retroactive-for-c32",
        "validated", "high",
        "c33 Priority 2 (closes c32 auditor MODERATE #2 retroactively). First-class "
        "_selection/ event capturing the 4-row POR-parseable-milestones delta "
        "between c31-close (728) and c32-open (732). Attributed to counting-method "
        "drift (baseline-measurement-timing inconsistency): the 4 rows correspond "
        "exactly to the c31 housekeeping tail (_plan/register-c31-sub-leaves + "
        "_run/cycle_31_closed + _archive/cycle-31-scratch + "
        "_infra/adopt-cycle31-tests). Not substantive accretion. c32-close 745 = "
        "c32-open 732 + 13 c32 rows; c33-open 745 (no drift). Precedent set for "
        "future cycles: parseable-count measurement should be canonicalized as "
        "IMMEDIATELY AFTER housekeeping tail lands at cycle close.",
        artifacts=[
            "data/v4/_selection/c33-por-shadow-drift-disclosure-retroactive-for-c32.json",
        ],
        extra={"carried_from_cycle": 32},
    ),

    # -- Priority 5: honest deferrals (Track B/C/D) --
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c33",
        "in-progress", "medium",
        "c33 Track B Disco A bass stage-2 DEFERRED to c34+ per Priority 3 gating "
        "(contingent on operator adjudication of _manager/"
        "M-V4-CERT-composite-fp-drift-adjudication-c32). No adjudication landed "
        "in live_guidance this cycle. Resume command: detached launch of "
        "`fine_fit_sf2_v2.py --song-sha16 cdd2717e52820ff6` wrapped in OP-1 "
        "SerialLock sentinel (post-c32 sha 6c80c438...). SF2_CONFIRMED remains "
        "FORBIDDEN on non-CG bass per preserved M-V4-SHOWCASE-1-non-cg-bass-"
        "acceptance-policy escalation.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c33",
        "in-progress", "medium",
        "c33 Track B Rome bass stage-2 DEFERRED to c34+ (blocked on Priority 3 "
        "operator adjudication). c23 stage-1 emb_cos_dist=0.5145 predicts "
        "SF2_RULED_OUT under distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c33",
        "in-progress", "medium",
        "c33 Track B Peach Dream bass stage-2 DEFERRED to c34+ (blocked on Priority "
        "3 operator adjudication). c23 stage-1 emb_cos_dist=0.4437 predicts "
        "SF2_RULED_OUT. Priority 4 path-divergence note carried forward: "
        "data/v4/profiles/88d247468cb6d49f/stem_manifest.json records "
        "operator_section_c25_checkpointed/rc9_6stem/ non-standard path per "
        "invariant (d) disclosure from c19 opening; sha c4944ee80dfe446b... "
        "verified byte-identical pre==post this cycle (READ-ONLY anchor).",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c33",
        "in-progress", "medium",
        "c33 Track B WIG + Disco A drums stage-1 DEFERRED to c34+. "
        "coarse_sweep_sf2_drums.py green regression at c30 (8/8 byte-identical); "
        "coarse sweeps do not require OP-1 (per-song scope, not fine-fit "
        "VGGish-heavy). Additive --song-sha16 kwarg thread required per c28 "
        "precedent for cross-song reuse.",
    ),

    # -- Priority 6: POR shadow-zone hold verified --
    _mk(
        "_plan/por-shadow-zone-hold-verified-c33",
        "validated", "high",
        "c33 Priority 6: POR shadow-zone hold verified. tools/_c32_por_count.py "
        "reports parseable Milestones=745 at c33 open (matches c32-close baseline "
        "of 745 per c32 rollup post-registration). Delta 0 vs c32 close. "
        "tools/_por_shadow_consolidate_c31.py NOT re-run per one-shot c14+ "
        "convention.",
    ),

    # -- Priority 7: Track F extended --
    _mk(
        "_infra/c33-track-f-legacy-regression-test-suite-extended",
        "validated", "high",
        "c33 Priority 7 (Track F) landed. Extended "
        "tests/test_c30_legacy_mode_regression.py in-place with 2 new c33 cases "
        "(test_15 JSON sidecar shape-parity: bass-v2 + guitar mirror drums-halt "
        "canonical shape; test_16 _selection/ POR shadow-drift event on disk with "
        "4-row diff). Now 16/16 PASS. tests/test_fine_fit_serial_lock_c32.py "
        "unchanged at 8/8 PASS. Cross-cycle total advances c32 22 -> c33 24 "
        "(16 in-place + 8 standalone).",
        artifacts=["tests/test_c30_legacy_mode_regression.py"],
    ),

    # -- Housekeeping tail --
    _mk(
        "_plan/register-c33-sub-leaves",
        "validated", "high",
        "c33 POR registration row: new c33 milestone_ids registered inline in the "
        "`## Milestones` section to satisfy the promise_check POR parser boundary "
        "before `## Sub-milestones`. Priority 1 backfills (2 escalation JSONs) + "
        "Priority 2 retroactive selection event + Priority 5 honest deferrals (4) "
        "+ Priority 6 POR shadow-zone hold + Priority 7 Track F extension + "
        "housekeeping tail (register + closed + scratch + adopt-tests).",
    ),
    _mk(
        "_run/cycle_33_closed",
        "validated", "high",
        "c33 CLOSED. Priority 0 (composite-FP-drift adjudication) status: "
        "BLOCKED_ON_OPERATOR — all 6 escalation memos preserved verbatim on disk "
        "and in-ledger (SHOWCASE-1-non-cg-bass-acceptance-policy c7, "
        "METRIC-SEMANTICS-c16 c16, CERT-fine-fit-sf2-drums-legacy-halt c30, "
        "CERT-fine-fit-sf2-v2-legacy-halt c31, CERT-fine-fit-sf2-guitar-legacy-halt "
        "c31, CERT-composite-fp-drift-adjudication-c32 c32). Priority 1 JSON "
        "sidecar backfill status: LANDED (2 sidecars authored, shape-parity "
        "tested). Priority 2 POR _selection/ retroactive emission status: LANDED "
        "(4-row diff + counting-method-drift hypothesis + procedural amendment "
        "recommendation). Priority 3 CONTINGENT: no operator adjudication in "
        "live_guidance this cycle -> skipped; Track A remains BLOCKED. Priority 4 "
        "Peach Dream stem-manifest divergence carried on deferral row (sha "
        "c4944ee80dfe446b... byte-identical). Priority 5 Track B/C/D honestly "
        "deferred (4 rows). Priority 6 POR shadow-zone hold verified (parseable "
        "Milestones = 745, delta 0 vs c32 close). Priority 7 Track F test-suite "
        "extended to 16 cases + 8 standalone = 24/24 PASS. NO wait-on-operator "
        "memo emitted (BANNED per operator directive 2026-09-03 part 2 EXCEPT "
        "the Priority 0 carve-out; consolidation memo satisfies that carve-out). "
        "All READ-ONLY anchors byte-identical pre==post: objective.py 8087ce80..., "
        "_sweep_hygiene_c27.py 771ff42b..., _serial_lock_op1.py 121809db..., "
        "cg_ab_mix.wav 6e13e007..., agent_picks_selection_invariants.md "
        "29a1610b..., 3 fine-fit drivers (post-OP-1 SHAs 6c80c438/a432e1d1/"
        "40dbb673), 3 coarse-sweep drivers (3f8bfa08/26aa754c/d6c54f21). "
        "env_pin_sha256=2ac444c3... unchanged. Operator ear remains LANDS "
        "authority post-hoc per FD-6.",
    ),
    _mk(
        "_archive/cycle-33-scratch",
        "validated", "high",
        "c33 scratch archival housekeeping. `tools/_emit_c33_ledger_events.py` "
        "retained in-tree per c14+ pattern. No workspace scratch to move to "
        "`tools/stale/`.",
    ),
    _mk(
        "_infra/adopt-cycle33-tests",
        "validated", "high",
        "c33 test-adoption housekeeping. Extended "
        "tests/test_c30_legacy_mode_regression.py in-place with 2 new c33 cases "
        "(test_15 + test_16). Standalone c32 tests/test_fine_fit_serial_lock_c32.py "
        "unchanged. No new test file introduced this cycle (per c18 additive-in-"
        "place pattern). Cross-cycle regression total: 16 in-place + 8 standalone "
        "= 24 (advances c32 baseline of 22).",
    ),
]


def main() -> None:
    ledger = ROOT / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    _GUARD.write_text("emitted\n")
    print(f"_emit_c33_ledger_events: {len(EVENTS)} events appended to {ledger}")


if __name__ == "__main__":
    main()
