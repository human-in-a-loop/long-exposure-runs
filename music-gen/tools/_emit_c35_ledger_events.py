#!/usr/bin/python3
# ---
# created: 2026-09-05T08:45:00Z
# cycle: 35
# run_id: run-2026-09-05T083000Z
# agent: worker
# milestone: _plan/register-c35-sub-leaves
# ---
"""c35 ledger emitter — idempotent per-turn guard.

Per music_gen_v4_prompt.md c35 brief:
    Priority 0 (BLOCKED): 6 escalations preserved verbatim (no emissions)
    Priority 1: long_exposure/ ABSENT re-probe -> OPT_B preservation. Emits:
        _selection/c35-emitter-writer-boundary-preservation
    Priority 2: strengthening BLOCKED (no reconstructable snapshot). Emits:
        _selection/c35-por-drift-proof-strengthening-blocker
        (supersedes c34 empirical proof at strengthening-request scope only;
         attribution finding preserved byte-identical)
    Priority 3: CONTINGENT (no operator adjudication) - skipped
    Priority 4: DEFERRED (contingent on Priority 3 PATH_A)
    Priority 5: 4 honest-deferral rows (Track B/C/D)
    Priority 6: POR shadow-zone hold verified (parseable=772 delta 0 vs c34)
    Priority 7: Extended tests/test_c30_legacy_mode_regression.py in-place
                (test_19 + test_20) now 20/20 PASS
    Housekeeping tail:
        _plan/register-c35-sub-leaves
        _run/cycle_35_closed
        _archive/cycle-35-scratch
        _infra/adopt-cycle35-tests

Adheres to the emitter exemption policy (docs/emitter_exemption_policy.md):
    - UUID5 content-hash event_id
    - _STATUS_ENUM values only
    - supersedes_path str or None, never list
    - nested confidence {level, rationale, assessor}
    - canonical-JSON serialization
    - sentinel-guarded idempotency (tools/.c35_ledger_emitted)
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
RUN_ID = "run-2026-09-05T083000Z"
CYCLE = 35
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T08:45:00Z"

_GUARD = ROOT / "tools" / ".c35_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c35_ledger_events: guard present at {_GUARD} - skipping")
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
            "rationale": "c35 substantive-cycle deliverable per music_gen_v4_prompt.md c35 brief Priority 0-7",
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
        "_selection/c35-emitter-writer-boundary-preservation",
        "validated", "high",
        "c35 Priority 1 preservation. On-disk re-probe of long_exposure/ returned "
        "ABSENT (probe: `test -d long_exposure && echo PRESENT || echo ABSENT`); "
        "c34 OPT_B exemption stands unchanged. This preservation event supersedes "
        "the c34 fork via `supersedes_path` (str per c14 lemma) so the escalation "
        "chain remains traceable and a future c36+ probe finding long_exposure/ "
        "PRESENT can supersede with an OPT_A adjudication. No policy change. "
        "docs/emitter_exemption_policy.md sha fd2c33a78d147341ebfa8df84e80002ff633"
        "7779bb3e58e1305de9e936e4eb6b byte-identical pre==post.",
        artifacts=[
            "data/v4/_selection/c35-emitter-writer-boundary-preservation.json",
            "docs/emitter_exemption_policy.md",
        ],
        supersedes_path="data/v4/_selection/c34-emitter-writer-boundary.json",
        extra={"carried_from_cycle": 34},
    ),

    # -- Priority 2: strengthening BLOCKED --
    _mk(
        "_selection/c35-por-drift-proof-strengthening-blocker",
        "validated", "high",
        "c35 Priority 2 (RECOMMENDED strengthening of c34 empirical proof) BLOCKED. "
        "Attempted to reconstruct c31-close and c32-open POR row-set snapshots from "
        "`_archive/cycle-31-scratch/` and `_archive/cycle-32-scratch/`. Neither "
        "directory exists as filesystem subtree; the `_archive/cycle-<N>-scratch` "
        "identifiers are ledger milestone_id labels for housekeeping-tail events, "
        "not staged snapshot paths. tools/stale/cycle31_scratch/ is essentially "
        "empty (`_scratch` subdir only). Git-blob reconstruction blocked (no c31/"
        "c32 sweep commits — first sweep after c20 is c37, matching c34 empirical-"
        "proof method note). Per FD-1 (halt-honest, no fabricated diff), no row-"
        "set diff produced. c34 attribution finding (Track B/C/D deferral rows "
        "account for +4 delta) preserved byte-identical: c34 selection event and "
        "diagnostic (`data/v4/diagnostics/c34_por_delta_proof.json` sha "
        "3b0e4d95061a8ad767ce524ae9ffbe1f71fc25a9f8101cd7ed843d5599a78561) unchanged "
        "pre==post. Supersede scope limited to the strengthening-request; "
        "attribution finding survives transitively.",
        artifacts=[
            "data/v4/_selection/c35-por-drift-proof-strengthening-blocker.json",
            "data/v4/_selection/c34-por-drift-empirical-proof.json",
            "data/v4/diagnostics/c34_por_delta_proof.json",
        ],
        supersedes_path="data/v4/_selection/c34-por-drift-empirical-proof.json",
        extra={"carried_from_cycle": 34},
    ),

    # -- Priority 5: honest deferrals (Track B/C/D) --
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c35",
        "in-progress", "medium",
        "c35 Track B/Priority 5 Disco A bass stage-2 DEFERRED to c36+ per Priority 3 "
        "gating (contingent on operator adjudication of _manager/M-V4-CERT-composite-"
        "fp-drift-adjudication-c32). No adjudication landed in live_guidance this "
        "cycle. Resume command: detached launch of `fine_fit_sf2_v2.py --song-sha16 "
        "cdd2717e52820ff6` wrapped in OP-1 SerialLock sentinel (post-c32 driver sha "
        "6c80c438...). SF2_CONFIRMED remains FORBIDDEN on non-CG bass per preserved "
        "M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy escalation.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c35",
        "in-progress", "medium",
        "c35 Track B/Priority 5 Rome bass stage-2 DEFERRED to c36+ (blocked on "
        "Priority 3 operator adjudication). c23 stage-1 emb_cos_dist=0.5145 predicts "
        "SF2_RULED_OUT under distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c35",
        "in-progress", "medium",
        "c35 Track B/Priority 5 Peach Dream bass stage-2 DEFERRED to c36+ (blocked "
        "on Priority 3 operator adjudication). c23 stage-1 emb_cos_dist=0.4437 "
        "predicts SF2_RULED_OUT. Priority 4 path-divergence disclosure carried "
        "forward: data/v4/profiles/88d247468cb6d49f/stem_manifest.json records "
        "operator_section_c25_checkpointed/rc9_6stem/ non-standard path per "
        "invariant (d) from c19 opening; sha c4944ee80dfe446b... verified byte-"
        "identical pre==post this cycle (READ-ONLY anchor).",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c35",
        "in-progress", "medium",
        "c35 Track D/Priority 5 WIG + Disco A drums stage-1 DEFERRED to c36+. "
        "coarse_sweep_sf2_drums.py green regression at c30 (8/8 byte-identical); "
        "coarse sweeps do not require OP-1 (per-song scope, not fine-fit VGGish-"
        "heavy). Additive --song-sha16 kwarg thread required per c28 precedent for "
        "cross-song reuse.",
    ),

    # -- Priority 6: POR shadow-zone hold verified --
    _mk(
        "_plan/por-shadow-zone-hold-verified-c35",
        "validated", "high",
        "c35 Priority 6: POR shadow-zone hold verified. tools/_c32_por_count.py "
        "reports parseable Milestones=772 at c35 open (matches c34-close baseline "
        "of 772 per c34 rollup post-registration). Delta 0 vs c34 close. "
        "tools/_por_shadow_consolidate_c31.py NOT re-run per one-shot c14+ "
        "convention.",
    ),

    # -- Priority 7: Track F extended --
    _mk(
        "_infra/c35-track-f-legacy-regression-test-suite-extended",
        "validated", "high",
        "c35 Priority 7 (Track F) landed. Extended tests/test_c30_legacy_mode_"
        "regression.py in-place with 2 new c35 cases (test_19 c35 long_exposure/ "
        "ABSENT re-probe + OPT_B preservation event; test_20 c35 POR strengthening "
        "blocker + c34 empirical proof byte-identical preservation). Now 20/20 "
        "PASS. tests/test_fine_fit_serial_lock_c32.py unchanged at 8/8 PASS. "
        "Cross-cycle total advances c34 26 -> c35 28 (20 in-place + 8 standalone).",
        artifacts=["tests/test_c30_legacy_mode_regression.py"],
    ),

    # -- Housekeeping tail --
    _mk(
        "_plan/register-c35-sub-leaves",
        "validated", "high",
        "c35 POR registration row: new c35 milestone_ids registered inline in the "
        "`## Milestones` section to satisfy the promise_check POR parser boundary "
        "before `## Sub-milestones`. Priority 1 preservation (1 row) + Priority 2 "
        "blocker supersede (1 row) + Priority 5 honest deferrals (4 rows) + "
        "Priority 6 POR shadow-zone hold + Priority 7 Track F extension + "
        "housekeeping tail (register + closed + scratch + adopt-tests).",
    ),
    _mk(
        "_run/cycle_35_closed",
        "validated", "high",
        "c35 CLOSED. Priority 0 status: BLOCKED_ON_OPERATOR - all 6 escalation "
        "memos preserved verbatim on disk and in-ledger (SHOWCASE-1-non-cg-bass-"
        "acceptance-policy c7, METRIC-SEMANTICS-c16 c16, CERT-fine-fit-sf2-drums-"
        "legacy-halt c30, CERT-fine-fit-sf2-v2-legacy-halt c31, CERT-fine-fit-sf2-"
        "guitar-legacy-halt c31, CERT-composite-fp-drift-adjudication-c32 c32). "
        "Priority 1 preservation: long_exposure/ ABSENT re-probe -> OPT_B "
        "exemption preserved via `_selection/c35-emitter-writer-boundary-"
        "preservation` (str supersedes_path per c14 lemma pointing at c34 fork). "
        "Priority 2 strengthening: BLOCKED (no reconstructable c31/c32 POR "
        "snapshot; git-blob reconstruction blocked per c34 method note); FD-1 "
        "halt-honest disclosure via `_selection/c35-por-drift-proof-strengthening-"
        "blocker` (str supersedes_path pointing at c34 empirical proof at "
        "strengthening-request scope only; attribution finding preserved byte-"
        "identical). Priority 3 CONTINGENT: no operator adjudication in "
        "live_guidance this cycle -> skipped; Track A remains BLOCKED. Priority 4 "
        "Peach Dream stem-manifest divergence (sha c4944ee80..) carried on "
        "deferral row byte-identical. Priority 5 Track B/C/D honestly deferred (4 "
        "rows). Priority 6 POR shadow-zone hold verified (parseable Milestones = "
        "772, delta 0 vs c34 close). Priority 7 Track F test-suite extended to 20 "
        "in-place + 8 standalone = 28/28 PASS. NO wait-on-operator memo emitted "
        "(BANNED per operator directive 2026-09-03 part 2; genuine operator-"
        "authority carve-out satisfied by preserved consolidation memo). All "
        "READ-ONLY anchors byte-identical pre==post: objective.py 8087ce80..., "
        "_sweep_hygiene_c27.py 771ff42b..., _serial_lock_op1.py 121809db..., "
        "agent_picks_selection_invariants.md 29a1610b..., emitter_exemption_"
        "policy.md fd2c33a7..., cg_ab_mix.wav 6e13e007..., 3 fine-fit drivers "
        "6c80c438/a432e1d1/40dbb673, 3 coarse-sweep drivers 3f8bfa08/26aa754c/"
        "d6c54f21, Peach Dream stem_manifest c4944ee8..., 6 escalation sidecars "
        "under data/v4/_manager/ byte-identical. env_pin_sha256=2ac444c3... "
        "unchanged. Operator ear remains LANDS authority post-hoc per FD-6.",
    ),
    _mk(
        "_archive/cycle-35-scratch",
        "validated", "high",
        "c35 scratch archival housekeeping. tools/_emit_c35_ledger_events.py "
        "retained in-tree per c14+ pattern. Session-scoped scratchpad probes "
        "live under harness-managed dir. No workspace scratch to move to "
        "`tools/stale/`.",
    ),
    _mk(
        "_infra/adopt-cycle35-tests",
        "validated", "high",
        "c35 test-adoption housekeeping. Extended tests/test_c30_legacy_mode_"
        "regression.py in-place with 2 new c35 cases (test_19 + test_20). "
        "Standalone tests/test_fine_fit_serial_lock_c32.py unchanged. No new "
        "test file introduced this cycle (per c18 additive-in-place pattern). "
        "Cross-cycle regression total: 20 in-place + 8 standalone = 28 (advances "
        "c34 baseline of 26).",
    ),
]


def main() -> None:
    ledger = ROOT / "promise_ledger.jsonl"
    with open(ledger, "a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    _GUARD.write_text("emitted\n")
    print(f"_emit_c35_ledger_events: {len(EVENTS)} events appended to {ledger}")


if __name__ == "__main__":
    main()
