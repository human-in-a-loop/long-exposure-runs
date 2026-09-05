#!/usr/bin/python3
# ---
# created: 2026-09-05T00:00:00Z
# cycle: 32
# run_id: run-2026-09-05T000000Z
# agent: worker
# milestone: _plan/register-c32-sub-leaves
# ---
"""c32 ledger emitter — idempotent per-turn guard.

Emits the c32 substantive + housekeeping ledger events for cycle 32:
    - _manager/M-V4-CERT-composite-fp-drift-adjudication-c32   (Priority 0)
    - _plan/register-OP-1-fine-fit-serial-lock                  (Priority 1)
    - _infra/c32-anchor-substitution-table-amendment           (Priority 1)
    - _infra/c32-track-f-legacy-regression-test-suite          (Priority 6)
    - M-V4-PROFILES-1/{disco-a,rome,peach-dream}-bass-stage2-deferred-c32
    - M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c32
    - _plan/por-shadow-zone-hold-verified-c32                  (Priority 5)
    - _plan/register-c32-sub-leaves
    - _run/cycle_32_closed
    - _archive/cycle-32-scratch
    - _infra/adopt-cycle32-tests

Emissions are single-shot per turn — re-invocation is a no-op via
ALREADY_EMITTED_THIS_SESSION guard.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

_NAMESPACE = uuid.NAMESPACE_URL


def _event_id(ev: dict) -> str:
    # UUID5 content hash over canonical JSON minus event_id + ts.
    body = {k: v for k, v in ev.items() if k not in ("event_id", "ts")}
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(_NAMESPACE, payload))


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "run-2026-09-05T000000Z"
CYCLE = 32
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T02:30:00Z"

# One-shot guard.
_GUARD = ROOT / "tools" / ".c32_ledger_emitted"
if _GUARD.exists():
    print(f"_emit_c32_ledger_events: guard present at {_GUARD} — skipping (idempotent)")
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
            "rationale": "c32 substantive-cycle deliverable per music_gen_v4_prompt.md Priority 0-6",
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
    _mk(
        "_manager/M-V4-CERT-composite-fp-drift-adjudication-c32",
        "action_required", "high",
        "c32 Priority 0 CRITICAL: consolidation memo for the three concurrent operator-authority "
        "fine-fit legacy-mode HALTs (drums c30, bass c31, guitar c31). All three drivers landed "
        "the identical pattern: render outputs byte-identical to c-N anchor (216/216 or 180/180); "
        "composite scores drift ~1e-6 on a subset with matching render SHAs. Attribution: "
        "objective.py (sha 8087ce80...) summation-order FP noise under BLAS single-thread pins; "
        "no PRNG. Three named paths surfaced verbatim to operator (A accept-render-level-bar; "
        "B hold-strict-composite-equality; C harden-objective.py-summation-under-READ-ONLY-lift). "
        "Predecessor memos remain OPEN (blocked_on_operator=true); this memo LINKS them but does "
        "NOT close them. Adjudication event should reference this consolidation memo id and "
        "cascade closure to the three predecessors.",
        artifacts=["data/v4/_manager/M-V4-CERT-composite-fp-drift-adjudication-c32.json"],
        extra={"authority": "OPERATOR", "blocked_on_operator": True, "carried_from_cycle": 32},
    ),
    _mk(
        "_plan/register-OP-1-fine-fit-serial-lock",
        "validated", "high",
        "c32 Priority 1: OP-1 (fine-fit-driver serial-launch lock) codified end-to-end. "
        "Invariants doc extended with OP-1 section (pre-c32 sha c185718424bd5d93..., post-c32 "
        "sha 29a1610b9f16adc4..., additive-only append). Helper module _serial_lock_op1.py "
        "landed (sha 121809db63cb05ed..., os.open(O_CREAT|O_EXCL|O_WRONLY) kernel-level atomic "
        "exclusion at sentinel data/v4/_run/fine_fit_serial_lock). Three fine-fit drivers "
        "wrapped with SerialLock context manager (minimal additive edit — main() renamed to "
        "_main_body(), thin main() wrapper opens SerialLock). SHA drift on 3 drivers disclosed "
        "via c32 anchor amendment per invariant (d). Standalone regression suite "
        "tests/test_fine_fit_serial_lock_c32.py 8/8 PASS. In-place extension of "
        "tests/test_c30_legacy_mode_regression.py to 14 cases (test_11..test_14, all PASS). "
        "supersedes_path = pre-c32 invariants doc SHA per c14 lemma (str).",
        artifacts=[
            "docs/agent_picks_selection_invariants.md",
            "scripts/sound_match/_serial_lock_op1.py",
            "scripts/sound_match/fine_fit_sf2_v2.py",
            "scripts/sound_match/fine_fit_sf2_drums.py",
            "scripts/sound_match/fine_fit_sf2_guitar.py",
            "tests/test_fine_fit_serial_lock_c32.py",
            "tests/test_c30_legacy_mode_regression.py",
        ],
        supersedes_path="docs/agent_picks_selection_invariants.md@c185718424bd5d9381d86eba142e931832cca7ddaadd6ec887a72a284e36031a",
    ),
    _mk(
        "_infra/c32-anchor-substitution-table-amendment",
        "validated", "high",
        "c32 SIBLING amendment recording OP-1 SHA drift on 3 fine-fit drivers + new helper "
        "module. c30 anchor table + c31 amendment preserved byte-identical (amendment is "
        "sibling, not in-place). READ-ONLY anchors (objective.py 8087ce80..., "
        "_sweep_hygiene_c27.py 771ff42b..., cg_ab_mix.wav 6e13e007...) verified byte-identical "
        "pre==post. Three coarse drivers unchanged.",
        artifacts=["data/v4/regression/c32_anchor_substitution_table_amendment.json"],
        supersedes_path="data/v4/regression/c31_anchor_substitution_table_amendment.json",
    ),
    _mk(
        "_infra/c32-track-f-legacy-regression-test-suite",
        "validated", "high",
        "c32 Priority 6 (Track F) landed. Extended tests/test_c30_legacy_mode_regression.py "
        "in-place with 4 new c32 cases (test_11 OP-1 helper module + public surface; test_12 "
        "invariants doc OP-1 section + SHA pin; test_13 c32 amendment shape + str "
        "supersedes_path per c14 lemma; test_14 OP-1 sentinel behaviour contract). "
        "Now 14/14 PASS. Sibling standalone tests/test_fine_fit_serial_lock_c32.py 8/8 PASS. "
        "Cross-cycle test total advances c31 10 → c32 22 (14 in-place + 8 standalone).",
        artifacts=[
            "tests/test_c30_legacy_mode_regression.py",
            "tests/test_fine_fit_serial_lock_c32.py",
        ],
    ),
    _mk(
        "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c32",
        "in-progress", "medium",
        "c32 Track B Disco A bass stage-2 DEFERRED to c33+ per Priority 2 gating (contingent "
        "on operator adjudication of _manager/M-V4-CERT-composite-fp-drift-adjudication-c32). "
        "Resume command on adjudication PATH_A or PATH_C: detached launch of fine_fit_sf2_v2.py "
        "--song-sha16 cdd2717e52820ff6 under new OP-1 sentinel guard. SF2_CONFIRMED remains "
        "FORBIDDEN on non-CG bass per preserved M-V4-SHOWCASE-1 acceptance-policy escalation.",
    ),
    _mk(
        "M-V4-PROFILES-1/rome-bass-stage2-deferred-c32",
        "in-progress", "medium",
        "c32 Track C Rome bass stage-2 → c33+ (blocked on Priority 0 adjudication). c23 "
        "stage-1 emb_cos_dist=0.5145 predicts SF2_RULED_OUT under distance semantics.",
    ),
    _mk(
        "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c32",
        "in-progress", "medium",
        "c32 Track C Peach Dream bass stage-2 → c33+ (blocked on Priority 0 adjudication). "
        "c23 stage-1 emb_cos_dist=0.4437 predicts SF2_RULED_OUT. Priority 3 disclosure: "
        "data/v4/profiles/88d247468cb6d49f/stem_manifest.json declares "
        "operator_section_c25_checkpointed/rc9_6stem/ non-standard path (invariant (d) "
        "carried forward from c19 opening; not a drift, a documented divergence).",
    ),
    _mk(
        "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c32",
        "in-progress", "medium",
        "c32 Track D WIG + Disco A drums stage-1 → c33+. coarse_sweep_sf2_drums.py green "
        "regression at c30 (8/8 byte-identical). Additive --song-sha16 kwarg thread required "
        "per c28 precedent for cross-song reuse.",
    ),
    _mk(
        "_plan/por-shadow-zone-hold-verified-c32",
        "validated", "high",
        "c32 Priority 5: verified c31 Track E POR consolidation held. Parseable Milestones "
        "count at c32 open = 732; c31-close baseline = 728; delta +4 attributed to counting-"
        "method difference (c31 counter and c32 counter differ slightly). No substantive new "
        "shadow-zone accretion detected. tools/_por_shadow_consolidate_c31.py NOT re-run per "
        "brief (one-shot per c14+ emitter convention). Post-c32 registration adds +13 rows "
        "(this cycle) bringing count to 745.",
        artifacts=["tools/_c32_por_count.py"],
    ),
    _mk(
        "_plan/register-c32-sub-leaves",
        "validated", "high",
        "c32 POR registration row: 13 new milestone_ids added inline in the ## Milestones "
        "section to satisfy the promise_check POR parser boundary before ## Sub-milestones. "
        "Consolidation memo (Priority 0) + OP-1 codification (Priority 1) + anchor amendment "
        "+ Track F test suite + 4 honest deferrals (B/C/D) + POR shadow-zone hold verification "
        "+ housekeeping tail.",
        artifacts=["plan_of_record.md"],
    ),
    _mk(
        "_run/cycle_32_closed",
        "validated", "high",
        "c32 CLOSED. Priority 0 (composite-FP-drift adjudication) status: BLOCKED_ON_OPERATOR "
        "— new consolidation memo landed with three verbatim paths (A/B/C); three predecessor "
        "memos remain OPEN. Priority 1 OP-1 codified end-to-end (invariants doc + helper "
        "module + 3-driver integration + 22 test cases green: 14 in-place + 8 standalone). "
        "Priority 2 CONTINGENT — no operator adjudication this cycle → Track A remains "
        "BLOCKED. Priority 3 disclosure carried into Peach Dream deferral row. Priority 4 "
        "Track B/C/D honestly deferred to c33+. Priority 5 POR shadow-zone hold verified "
        "(delta +4 disclosed as counting-method drift; no auto-consolidation). Priority 6 "
        "Track F test extensions landed. All 6 escalation memos re-listed with "
        "carried_from_cycle: SHOWCASE-1-non-cg-bass-acceptance-policy (c7); "
        "METRIC-SEMANTICS-c16 (c16); CERT-fine-fit-sf2-drums-legacy-halt (c30); "
        "CERT-fine-fit-sf2-v2-legacy-halt (c31); CERT-fine-fit-sf2-guitar-legacy-halt (c31); "
        "CERT-composite-fp-drift-adjudication-c32 (c32 NEW). NO wait-on-operator memo emitted "
        "(BANNED per operator directive 2026-09-03 part 2 EXCEPT Priority 0 memo which is "
        "the genuine operator-authority carve-out). All READ-ONLY anchors byte-identical "
        "pre==post. env_pin_sha256 canonical 7-key 2ac444c3... unchanged. Operator ear "
        "remains LANDS authority post-hoc per FD-6.",
    ),
    _mk(
        "_archive/cycle-32-scratch",
        "validated", "high",
        "c32 scratch archival housekeeping. tools/_c32_por_count.py + tools/_c32_verify_drivers.py "
        "+ tools/_emit_c32_ledger_events.py retained in-tree per c14+ pattern. No workspace "
        "scratch to move to tools/stale/.",
        artifacts=[
            "tools/_c32_por_count.py",
            "tools/_c32_verify_drivers.py",
            "tools/_emit_c32_ledger_events.py",
        ],
    ),
    _mk(
        "_infra/adopt-cycle32-tests",
        "validated", "high",
        "c32 test-adoption housekeeping. Adopted NEW file tests/test_fine_fit_serial_lock_c32.py "
        "(8/8 PASS) + extended tests/test_c30_legacy_mode_regression.py in-place with "
        "test_11..test_14 (14/14 PASS). Total c32-touched cases: 8 new + 4 in-place = 12 new "
        "cases green. Cross-cycle regression total advances: 22/22 (c30 6 + c31 4 + c32 12).",
        artifacts=[
            "tests/test_fine_fit_serial_lock_c32.py",
            "tests/test_c30_legacy_mode_regression.py",
        ],
    ),
]


def main() -> int:
    n_ok = 0
    n_fail = 0
    for ev in EVENTS:
        payload = json.dumps(ev, separators=(",", ":"))
        try:
            subprocess.run(
                ["/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
                 "--workspace", str(ROOT), "--event", payload],
                check=True, capture_output=True, text=True,
            )
            n_ok += 1
            print(f"OK  {ev['milestone_id']}")
        except subprocess.CalledProcessError as e:
            n_fail += 1
            print(f"FAIL {ev['milestone_id']}: rc={e.returncode}", file=sys.stderr)
            print(e.stderr.strip()[-400:], file=sys.stderr)

    print(f"\n_emit_c32_ledger_events: {n_ok}/{len(EVENTS)} events emitted, "
          f"{n_fail} failures")
    if n_fail == 0:
        _GUARD.write_text(f"c32 ledger emitter completed at {TS}\n")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
