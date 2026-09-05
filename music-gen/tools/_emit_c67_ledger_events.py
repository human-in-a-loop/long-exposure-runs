#!/usr/bin/env -S /usr/bin/python3
"""c67 one-shot ledger-event emitter (retained in-tree per c14+ pattern).

Per c67 research brief §4:
- P0: lightweight MODERATE carry-forward per c66 auditor guidance #1.
  on-disk sha d483f2bf... remains canonical for c67+ downstream.
  supersedes_path = c66 lightweight MODERATE carry event (str per
  c14 lemma).
- P1 Branch B fires: no operator adjudication in live_guidance;
  6th consecutive stable-blocked state (c62 -> c63 chain-continue-
  by-reference -> c64 explicit -> c65 explicit -> c66 explicit -> c67
  explicit). Chain-continue via str-supersede lemma per c14; do NOT
  re-escalate per §2 BANNED-list + c66 auditor forward-guidance.
- P2 Branch B fires: cleaner framing preserved from c66. No detached
  processes launched this cycle (P3/P4a/P4b all disk-blocked); OP-2
  Monitor policy applies only when detached sweeps launch.
  supersedes_path=null new milestone_id distinct from c66's row.
- P3 SKIP: df 85% > 82% precondition; 5th consecutive skip (c63 ->
  c64 -> c65 -> c66 -> c67); NOT preservation-spin per FD-1.
- P4a Peach Dream SKIP: gated on df + P3 predecessor-blocked.
  On-disk manifest sha d483f2bf... is P0-canonical from c65.
- P4b Disco A SKIP: predecessor-blocked + df.
- P5 housekeeping: register + closed + scratch + adopt-tests.

Invariant (d) disclosures carried transitively (orthogonal to c67):
- test_sound_match_fine_fit_sf2_other.py on-disk 7ffd3389... (c63
  docstring-only edit landed; brief §1 pin never updated; on-disk
  authoritative per FD-1). Test suite 8/8 unchanged.
- data/v4/profiles/88d247468cb6d49f/stem_manifest.json on-disk sha
  d483f2bf0b09389b... = c65 Branch C canonical pinned; non-standard
  path operator_section_c25_checkpointed/rc9_6stem/ preserved.
- docs/agent_picks_selection_invariants.md on-disk 7df72aee...
  (inherited drift; on-disk authoritative).
- scripts/sound_match/fine_fit_sf2_v2.py on-disk 15cbf8b69c...
  (inherited drift; on-disk authoritative).

10 events land: 6 substantive + 4 housekeeping.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[1] / "promise_ledger.jsonl"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
RUN_ID = "run-2026-09-05T235000Z"
TS = "2026-09-05T23:50:00Z"
CYCLE = 67

_NS = uuid.UUID("00000000-0000-0000-0000-000000000000")


def _uuid5(milestone_id: str, narrative: str) -> str:
    body = f"{milestone_id}|{narrative}".encode("utf-8")
    return str(uuid.uuid5(_NS, hashlib.sha256(body).hexdigest()))


EVENTS = [
    # (1) P0: lightweight MODERATE carry-forward per c66 pattern.
    {
        "milestone_id": "_selection/c67-peach-dream-stem-manifest-attribution-carry-moderate",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": "_selection/c66-peach-dream-stem-manifest-attribution-carry-moderate",
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P0 lightweight MODERATE carry-forward per c66 auditor "
                "guidance #1. c65 Branch C already closed the git-"
                "attribution question halt-honest; c66 pinned the "
                "lightweight carry pattern. Do NOT re-run git probes "
                "(conclusive at c65) and do NOT normalize the file "
                "(invariant (d) DO-NOT-TOUCH per FD-1). Attribution "
                "genuinely unknown; on-disk sha "
                "d483f2bf0b09389bec5186cdbde8a89393dbedc8288a7805c72f13"
                "bf3634cdd4 is canonical for c67+ downstream. MODERATE "
                "remains open for future auditor scrutiny but is NOT "
                "re-litigated cycle-over-cycle. Chain-supersede of c66 "
                "carry event (str per c14 lemma)."
            ),
        },
        "narrative": (
            "P0 MODERATE carry-forward (c67, 2nd consecutive light-"
            "weight): (i) c65 Branch C halt-honest CLOSED; (ii) "
            "attribution genuinely unknown; (iii) on-disk "
            "d483f2bf0b09389bec5186cdbde8a89393dbedc8288a7805c72f13bf"
            "3634cdd4 canonical for c67+ downstream; (iv) MODERATE "
            "not re-litigated. supersedes_path = c66 carry event "
            "(str per c14 lemma). env_pin_sha256=2ac444c3...922ca."
        ),
    },
    # (2) P1 Branch B: WIG piano stage-1 blocked (6th consecutive).
    {
        "milestone_id": "_plan/wig-piano-stage1-blocked-on-operator-c67",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": "_plan/wig-piano-stage1-blocked-on-operator-c66",
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P1 Branch B fires per c67 brief §4 P1: live_guidance "
                "carries no new operator input on WIG piano this cycle "
                "-> Branch B is the expected disposition. Chain-"
                "continue of c66 blocked event via str-supersede lemma "
                "per c14. NOT a re-escalation (BANNED per c62 §2 + "
                "c63/c64/c65/c66 auditor guidance). 4 operator paths "
                "(OPT_A/B/C/D) remain open per c61-named list. This is "
                "the 6th consecutive stable-blocked state (c62 -> c63-"
                "continuation-by-reference -> c64 -> c65 -> c66 -> "
                "c67). blocked_on_operator remains true; authority="
                "OPERATOR. c67 §6 forward-guidance flags that if the "
                "chain reaches 7 consecutive blocked at c68, prepare "
                "c69 operator memo draft — chain-continue only until "
                "then."
            ),
            "consequence_of_ban": (
                "Per c62 §2 BANNED-list carried through c67: even at 6 "
                "consecutive stable-blocked cycles the escalation is "
                "NOT re-issued; only chain-continues via str-supersede."
            ),
        },
        "narrative": (
            "P1 Branch B: no operator adjudication in live_guidance; "
            "WIG piano stage-1 remains blocked_on_operator (6th "
            "consecutive stable-blocked cycle). Chain-supersede of c66 "
            "blocked event per str-supersede lemma (c14). NOT a re-"
            "escalation (BANNED per c62 §2). Preserves the 4 c61-named "
            "operator paths OPT_A/B/C/D. authority=OPERATOR. "
            "env_pin_sha256=2ac444c3...922ca."
        ),
    },
    # (3) P2 Branch B: OP-2 Monitor N/A (no detached processes launched).
    {
        "milestone_id": "_infra/op-2-monitor-not-applicable-c67",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P2 Branch B fires per c67 brief §4 P2: OP-2 Monitor "
                "policy applies when detached sweeps launch. c67 "
                "launches NO detached processes (P3 Rome + P4a Peach "
                "Dream + P4b Disco A all disk-blocked at 85% > 82% "
                "precondition; non-CG drums stage-1 also gated per "
                "c47 strict order when bass stage-2 fails to launch). "
                "Cleaner framing per c66 pattern: OP-2 does NOT need "
                "reload when there is nothing to monitor. Disposition "
                "= 'N/A no detached processes launched this cycle'. "
                "supersedes_path=null (new milestone id per c65 "
                "auditor framing note carried through c66)."
            ),
        },
        "narrative": (
            "P2 Branch B: no detached processes launched this cycle "
            "(P3/P4a/P4b all disk-blocked at 85% > 82%); OP-2 Monitor "
            "policy is inapplicable when there is nothing to monitor. "
            "Cleaner framing per c66 pattern. Disposition = N/A. "
            "env_pin_sha256=2ac444c3...922ca."
        ),
    },
    # (4) P3 SKIP disk-blocked: Rome bass stage-2 (5th consecutive skip).
    {
        "milestone_id": "M-V4-PROFILES-1/rome-bass-stage2-disk-blocked-c67",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P3 SKIP per c67 brief §4 P3 disk-clearance gate. "
                "`df -h .` at c67 open reports 85% use (5.8G avail on "
                "252G volume); above the 82% precondition; c27 "
                "_sweep_hygiene_c27.py df_guard would abort at 90%. "
                "Rome bass stage-2 fine fit via fine_fit_sf2_other.py "
                "(READ-ONLY sha 7b2e5f20...) NOT launched. 5th "
                "consecutive skip (c63 -> c64 -> c65 -> c66 -> c67). "
                "NOT preservation-spin (brief §4 P3 explicit disk-"
                "blocked branch; FD-1 halt-honest). SF2_CONFIRMED "
                "remains lifted per c47 OPT1 extension."
            ),
        },
        "narrative": (
            "SKIP disk-blocked (5th consecutive): Rome (sha16 "
            "51e433ade2a845e1) bass stage-2 fine fit not launched. "
            "Disk at 85% at c67 open exceeds the 82% precondition. "
            "Resume command: nohup /usr/bin/python3 scripts/sound_"
            "match/fine_fit_sf2_other.py --song-sha16 51e433ade2a845e1 "
            "(post-c62 driver sha 7b2e5f20...) wrapped in OP-1 "
            "SerialLock. Per-family replay proof (FD-16(c)) queued "
            "for c68+ with env_pin_sha256=2ac444c3...922ca + SF2 sha "
            "74594e8f...1cb0."
        ),
    },
    # (5) P4a SKIP disk-blocked + predecessor-blocked: Peach Dream.
    {
        "milestone_id": "M-V4-PROFILES-1/peach-dream-bass-stage2-disk-blocked-c67",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P4a SKIP per c67 brief §4 P4a gate: (i) df_guard 85% "
                "> 82% precondition; (ii) P3 Rome bass stage-2 disk-"
                "blocked (predecessor-blocked); (iii) P0 MODERATE "
                "carry-forward this cycle: on-disk sha d483f2bf... "
                "already pinned canonical at c65 Branch C; downstream "
                "references cite it safely. Peach Dream bass stage-2 "
                "not launched. Non-standard stem manifest path "
                "`operator_section_c25_checkpointed/rc9_6stem/` "
                "preserved per invariant (d) (16th-cycle-stable since "
                "c19 opening)."
            ),
        },
        "narrative": (
            "SKIP disk-blocked + predecessor-blocked: Peach Dream "
            "(sha16 88d247468cb6d49f) bass stage-2 fine fit not "
            "launched. Manifest on-disk sha d483f2bf0b09389b... is "
            "c65 Branch C canonical (P0 MODERATE carried forward this "
            "cycle). Non-standard path preserved. Resume for c68+ "
            "pending P3 Rome landing + disk clearance to <=82%."
        ),
    },
    # (6) P4b SKIP disk-blocked + predecessor-blocked: Disco A.
    {
        "milestone_id": "M-V4-PROFILES-1/disco-a-bass-stage2-disk-blocked-c67",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P4b SKIP per c67 brief §4 P4b gate: df_guard 85% > "
                "82% + P3/P4a predecessor-blocked. Disco A bass "
                "stage-2 not launched. c47 operator-directed strict "
                "order (bass -> drums -> ...) means non-CG drums "
                "stage-1 also does NOT open this cycle when any of "
                "P3/P4a/P4b gate fails. c26 sweep was interrupted "
                "mid-run per c27 verification; c68+ resume must "
                "delete residual output dir before fresh launch "
                "under c27 hygiene."
            ),
        },
        "narrative": (
            "SKIP disk-blocked + predecessor-blocked: Disco A (sha16 "
            "cdd2717e52820ff6) bass stage-2 fine fit not launched. "
            "c47 strict-order bass->drums means non-CG drums stage-1 "
            "also deferred to c68+. Resume: --song-sha16 "
            "cdd2717e52820ff6 + delete residual c26-interrupted "
            "output first."
        ),
    },
    # (7) P5 register.
    {
        "milestone_id": "_plan/register-c67-sub-leaves",
        "status": "validated",
        "artifacts": ["plan_of_record.md"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c67 POR registration row: 10 new c67 milestone_ids "
                "added inline in the `## Milestones` section (this "
                "parseable region) to satisfy the promise_check POR "
                "parser boundary before `## Sub-milestones`. P0 "
                "MODERATE carry-forward (1) + P1 Branch B blocked-on-"
                "operator (1) + P2 Branch B N/A (1) + P3/P4a/P4b "
                "three disk-blocked SKIPs (3) + housekeeping tail "
                "(register + closed + scratch + adopt-tests, 4). "
                "NO preservation-spin (BANNED per c47 operator "
                "omnibus part 4)."
            ),
        },
        "narrative": (
            "c67 POR registration: 10 new c67 rows added inline in "
            "the `## Milestones` section. NO preservation-spin."
        ),
    },
    # (8) P5 closed rollup.
    {
        "milestone_id": "_run/cycle_67_closed",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c67 CLOSED. LANDED: P0 MODERATE carry-forward (Peach "
                "Dream stem_manifest attribution unknown; on-disk "
                "d483f2bf... canonical per c65 Branch C; chain-"
                "supersede of c66 carry event; not re-litigated); P1 "
                "Branch B stable-blocked (6th consecutive; NOT re-"
                "escalation, str-supersede chain-continue of c66 "
                "blocked event per c14 lemma); P2 Branch B N/A (no "
                "detached processes launched -> OP-2 Monitor "
                "inapplicable). SKIPPED: P3 Rome bass stage-2 (disk "
                "85% > 82%, 5th consecutive); P4a Peach Dream bass "
                "stage-2 (predecessor + disk); P4b Disco A bass "
                "stage-2 (predecessor + disk). NOT LAUNCHED per c47 "
                "strict-order: non-CG drums stage-1. 6 substantive "
                "events + 4 housekeeping = 10 total. Anchor drifts "
                "disclosed per invariant (d) transitively (test file "
                "on-disk 7ffd3389... vs brief-cited ee0c8a10...; "
                "peach_dream stem_manifest sha on-disk d483f2bf... = "
                "c65 Branch C canonical; agent_picks 7df72aee... on-"
                "disk; fine_fit_sf2_v2.py 15cbf8b6... on-disk). All "
                "§1 READ-ONLY anchors verified byte-identical pre==post "
                "(objective.py 8087ce80..., profile_writer.py "
                "b36dc448..., _sweep_hygiene_c27.py 771ff42b..., "
                "fine_fit_sf2_other.py 7b2e5f20..., cg_ab_mix.wav "
                "6e13e007...). NO wait-on-operator memo emitted "
                "(BANNED per operator directive 2026-09-03 part 2). "
                "Operator ear remains LANDS authority post-hoc per "
                "FD-6. env_pin_sha256 canonical 7-key subset "
                "2ac444c3...922ca unchanged."
            ),
        },
        "narrative": (
            "c67 CLOSED. P0 MODERATE carry-forward (chain-supersede "
            "of c66 carry event); P1 Branch B stable-blocked (6th "
            "consecutive); P2 Branch B N/A. P3/P4a/P4b disk-blocked "
            "SKIPs (85% > 82%; P3 5th consecutive). No sweeps "
            "launched; no re-escalation; no wait-on-operator memo. "
            "10 total ledger events (6 substantive + 4 housekeeping). "
            "All §1 READ-ONLY anchors byte-identical pre==post. "
            "Operator ear LANDS authority per FD-6."
        ),
    },
    # (9) P5 scratch archival.
    {
        "milestone_id": "_archive/cycle-67-scratch",
        "status": "validated",
        "artifacts": ["tools/_emit_c67_ledger_events.py"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c67 scratch archival. `tools/_emit_c67_ledger_"
                "events.py` retained in-tree per c14+ pattern. No "
                "workspace scratch to move to `tools/stale/`."
            ),
        },
        "narrative": "c67 scratch retained in-tree; no stale/ moves.",
    },
    # (10) P5 test-adoption.
    {
        "milestone_id": "_infra/adopt-cycle67-tests",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c67 test-adoption housekeeping. No new test file "
                "this cycle. Existing `tests/test_sound_match_fine_"
                "fit_sf2_other.py` (on-disk sha 7ffd3389...; brief-"
                "cited ee0c8a10... diverges per invariant (d)) "
                "unchanged this cycle. Test suite remains 8/8 PASS "
                "by construction. P0 MODERATE carry + P1 chain-"
                "supersede + P2 N/A + P3/P4a/P4b SKIPs require no "
                "new tests (no code or artifact changes)."
            ),
        },
        "narrative": (
            "No new tests this cycle. Existing 8/8 test suite "
            "unchanged."
        ),
    },
]


def _canonical(event: dict) -> str:
    return json.dumps(event, sort_keys=True, separators=(",", ":"))


def main() -> None:
    to_append = []
    for spec in EVENTS:
        e = dict(spec)
        e["cycle"] = CYCLE
        e["ts"] = TS
        e["run_id"] = RUN_ID
        e["env_pin_sha256"] = ENV_PIN
        e["agent"] = "worker"
        e["event_id"] = _uuid5(e["milestone_id"], e["narrative"])
        to_append.append(e)

    with LEDGER.open("a") as f:
        for e in to_append:
            f.write(_canonical(e) + "\n")

    print(f"Appended {len(to_append)} c67 ledger events.")
    for e in to_append:
        print(f"  {e['milestone_id']}  ({e['event_id']})")


if __name__ == "__main__":
    main()
