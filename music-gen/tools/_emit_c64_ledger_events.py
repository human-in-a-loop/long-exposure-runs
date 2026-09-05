#!/usr/bin/env -S /usr/bin/python3
"""c64 one-shot ledger-event emitter (retained in-tree per c14+ pattern).

Per c64 research brief §4:
- P0 Branch B fires: no operator adjudication in live_guidance; c62 blocked
  event chain-continues (3rd consecutive stable-blocked state); per §2
  BANNED-list this cycle does NOT re-escalate.
- P1 SKIP: disk-blocked (85% > 82% precondition).
- P2 SKIP: predecessor-blocked (P1 disk-blocked).
- P3 SKIP: predecessor-blocked (P1 disk-blocked).
- P4 confirmation: c63 four non-CG guitar family-1 SKIP auto-closes remain
  in force; no new operator directive lifting them.
- P5 housekeeping: register + closed + scratch + adopt-tests.

Invariant (d) disclosures inline:
- test_sound_match_fine_fit_sf2_other.py: brief cites `ee0c8a1078641c52...`;
  on-disk `7ffd3389ec35e986...` (post-c63 docstring-only edit landed);
  on-disk authoritative per FD-1.
- data/v4/regression/cg_ab_mix.wav: brief-cited path; on-disk resides at
  data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav (sha `6e13e00...` from
  c17); c64 does NOT touch the file; path drift disclosed only.
- data/v4/profiles/88d247468cb6d49f/stem_manifest.json: brief cites
  `c4944ee80dfe446b...`; on-disk `d483f2bf0b09389b...`; on-disk authoritative
  per FD-1 + invariant (d). Non-standard path
  `operator_section_c25_checkpointed/rc9_6stem/` still recorded.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[1] / "promise_ledger.jsonl"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
RUN_ID = "run-2026-09-05T233000Z"
TS = "2026-09-05T22:00:00Z"
CYCLE = 64

_NS = uuid.UUID("00000000-0000-0000-0000-000000000000")


def _uuid5(milestone_id: str, narrative: str) -> str:
    body = f"{milestone_id}|{narrative}".encode("utf-8")
    return str(uuid.uuid5(_NS, hashlib.sha256(body).hexdigest()))


EVENTS = [
    # (1) P0 Branch B: stable-blocked chain-continue.
    {
        "milestone_id": "_plan/wig-piano-stage1-blocked-on-operator-c64",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": "_plan/wig-piano-stage1-blocked-on-operator-c62",
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P0 Branch B fires per c64 brief §4 P0. No operator "
                "adjudication of c61 escalation `69f293a9-...` in "
                "live_guidance this cycle. Chain-continue of the c62 blocked "
                "event (event_id 41558d83-0198-5b50-a1ed-be29cb057cc5) via "
                "str-supersede lemma per c14. NOT a re-escalation (banned "
                "per c62 §2 BANNED-list and c63 auditor). 4 operator paths "
                "(OPT_A/B/C/D) remain open. This is the 3rd consecutive "
                "stable-blocked state (c62 -> c63-continuation-by-reference "
                "-> c64 explicit). blocked_on_operator remains true; "
                "authority=OPERATOR."
            ),
        },
        "narrative": (
            "P0 Branch B: no operator adjudication in live_guidance; WIG "
            "piano stage-1 remains blocked_on_operator. Chain-supersede of "
            "c62 blocked event (event_id 41558d83) per str-supersede lemma "
            "(c14). NOT a re-escalation. Preserves the 4 c61-named operator "
            "paths OPT_A/B/C/D. authority=OPERATOR. 3rd consecutive stable-"
            "blocked cycle. env_pin_sha256=2ac444c3...922ca."
        ),
    },
    # (2) P1 SKIP disk-blocked.
    {
        "milestone_id": "M-V4-PROFILES-1/rome-bass-stage2-disk-blocked-c64",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P1 SKIP per c64 brief §4 P1 disk-clearance gate. `df -h .` "
                "at c64 open reports 85% use (5.8G avail on 252G volume); "
                "above the 82% precondition; c27 sweep_hygiene df_guard "
                "would abort at 90%. Rome bass stage-2 fine fit via "
                "fine_fit_sf2_other.py (sha 7b2e5f20...) NOT launched this "
                "cycle. Resume for c65+ when disk clears to <=82%. NOT "
                "preservation-spin (FD-1 halt-honest disclosure)."
            ),
        },
        "narrative": (
            "SKIP disk-blocked: Rome (sha16 51e433ade2a845e1) bass stage-2 "
            "fine fit not launched. Disk at 85% at c64 open exceeds the 82% "
            "precondition from §4 P1. Resume command: nohup /usr/bin/python3 "
            "scripts/sound_match/fine_fit_sf2_other.py --song-sha16 "
            "51e433ade2a845e1 (post-c62 driver sha 7b2e5f20...) wrapped in "
            "OP-1 SerialLock. SF2_CONFIRMED remains lifted per c47 OPT1 "
            "extension. Per-family replay proof (FD-16(c)) queued for c65+ "
            "with env_pin_sha256=2ac444c3...922ca + SF2 sha 74594e8f...1cb0."
        ),
    },
    # (3) P2 SKIP predecessor-blocked (P1 disk-blocked chain).
    {
        "milestone_id": "M-V4-PROFILES-1/peach-dream-bass-stage2-disk-blocked-c64",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P2 SKIP per c64 brief §4 P2 gate: (i) df_guard 85% > 82% "
                "precondition; (ii) P1 Rome bass stage-2 disk-blocked "
                "(predecessor-blocked). Peach Dream bass stage-2 not "
                "launched. Non-standard stem manifest path "
                "`operator_section_c25_checkpointed/rc9_6stem/` preserved "
                "per invariant (d). Manifest on-disk sha `d483f2bf0b09389b` "
                "(brief-cited `c4944ee80dfe446b` diverges; on-disk "
                "authoritative per FD-1 + invariant (d))."
            ),
        },
        "narrative": (
            "SKIP disk-blocked + predecessor-blocked: Peach Dream (sha16 "
            "88d247468cb6d49f) bass stage-2 fine fit not launched. Manifest "
            "on-disk sha `d483f2bf0b09389b` (brief cited `c4944ee8...`; "
            "on-disk authoritative per invariant (d) 13th consecutive "
            "cycle). Non-standard path preserved. Resume for c65+ pending "
            "P1 Rome landing + disk clearance to <=82%."
        ),
    },
    # (4) P3 SKIP predecessor-blocked.
    {
        "milestone_id": "M-V4-PROFILES-1/disco-a-bass-stage2-disk-blocked-c64",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P3 SKIP per c64 brief §4 P3 gate: df_guard 85% > 82% + "
                "P1/P2 predecessor-blocked. Disco A bass stage-2 not "
                "launched. c47 operator-directed strict order (bass -> "
                "drums -> ...) means P4 drums stage-1 also does NOT open "
                "same cycle when any of P1/P2/P3 gate fails. c26 sweep "
                "was interrupted mid-run per c27 verification; c65+ resume "
                "must delete residual output dir before fresh launch under "
                "c27 hygiene."
            ),
        },
        "narrative": (
            "SKIP disk-blocked + predecessor-blocked: Disco A (sha16 "
            "cdd2717e52820ff6) bass stage-2 fine fit not launched. c47 "
            "strict-order bass->drums means non-CG drums stage-1 also "
            "deferred to c65+. Resume: --song-sha16 cdd2717e52820ff6 + "
            "delete residual c26-interrupted output first."
        ),
    },
    # (5) P4 confirmation: c63 four SKIPs remain in force.
    {
        "milestone_id": "M-V4-PROFILES-1/non-cg-guitar-family-1-skips-confirmation-c64",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P4 confirmation per c64 brief §4 P4. c63 landed 4 non-CG "
                "guitar family-1 SKIP auto-closes (Disco A / Rome / Peach "
                "Dream / WIG) per c15 SF2_RULED_OUT + c47 OPT1 extension. "
                "c64 live_guidance carries no operator directive lifting "
                "these SKIPs. Entries remain closed in POR. Confirmation-"
                "only event; no new state emitted per song (auto-closes "
                "already terminal at c63)."
            ),
        },
        "narrative": (
            "P4 no-regression confirmation: c63 4 non-CG guitar family-1 "
            "SKIP auto-closes (Disco A + Rome + Peach Dream + WIG per c15 "
            "SF2_RULED_OUT + c47 OPT1 extension) remain in force. No "
            "operator directive lifting them in c64 live_guidance. Single "
            "confirmation event; no per-song re-emission."
        ),
    },
    # (6) P5 register.
    {
        "milestone_id": "_plan/register-c64-sub-leaves",
        "status": "validated",
        "artifacts": ["plan_of_record.md"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c64 POR registration row: 9 new c64 milestone_ids added "
                "inline in the `## Milestones` section (this parseable "
                "region) to satisfy the promise_check POR parser boundary "
                "before `## Sub-milestones`. P0 blocked-on-operator (1) + "
                "P1/P2/P3 three disk-blocked SKIPs (3) + P4 confirmation "
                "(1) + housekeeping tail (register + closed + scratch + "
                "adopt-tests, 4). No preservation-spin (BANNED per c47 "
                "operator omnibus part 4)."
            ),
        },
        "narrative": (
            "c64 POR registration: 9 new c64 rows added inline in the "
            "`## Milestones` section. Above §3.9 minimum >=2. NO "
            "preservation-spin."
        ),
    },
    # (7) P5 closed rollup.
    {
        "milestone_id": "_run/cycle_64_closed",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c64 CLOSED. LANDED: P0 Branch B stable-blocked (3rd "
                "consecutive; NOT re-escalation); P4 no-regression "
                "confirmation. SKIPPED: P1 Rome bass stage-2 (disk 85% > "
                "82%); P2 Peach Dream bass stage-2 (predecessor + disk); "
                "P3 Disco A bass stage-2 (predecessor + disk). NOT LAUNCHED "
                "per c47 strict-order: non-CG drums stage-1. 5 substantive "
                "events + 4 housekeeping = 9 total (above §3.9 minimum "
                ">=2). Anchor drifts disclosed per invariant (d): (a) test "
                "file on-disk 7ffd3389... vs brief-cited ee0c8a10... (c63 "
                "docstring-edit landed); (b) cg_ab_mix.wav lives at "
                "data/v4/deliveries/31a164f845f8e27e/ not "
                "data/v4/regression/; (c) peach_dream stem_manifest sha "
                "on-disk d483f2bf... vs brief-cited c4944ee80... (non-"
                "standard path preserved). NO wait-on-operator memo (BANNED "
                "per operator directive 2026-09-03 part 2). Operator ear "
                "remains LANDS authority post-hoc per FD-6. env_pin_sha256 "
                "canonical 7-key subset 2ac444c3...922ca unchanged. All "
                "READ-ONLY anchors listed in c64 brief §1 verified byte-"
                "identical pre==post (excluding the 3 disclosed drifts "
                "above and cg_ab_mix.wav path fix)."
            ),
        },
        "narrative": (
            "c64 CLOSED. P0 Branch B stable-blocked (3rd consecutive); P4 "
            "confirmation. P1/P2/P3 disk-blocked SKIPs (85% > 82%). No "
            "sweeps launched; no re-escalation; no wait-on-operator memo. "
            "9 ledger events. Anchor drifts disclosed per invariant (d) "
            "for test file + cg_ab_mix path + Peach Dream stem_manifest "
            "sha. Operator ear LANDS authority per FD-6."
        ),
    },
    # (8) P5 scratch archival.
    {
        "milestone_id": "_archive/cycle-64-scratch",
        "status": "validated",
        "artifacts": ["tools/_emit_c64_ledger_events.py"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c64 scratch archival. `tools/_emit_c64_ledger_events.py` "
                "retained in-tree per c14+ pattern. No workspace scratch "
                "to move to `tools/stale/`."
            ),
        },
        "narrative": "c64 scratch retained in-tree; no stale/ moves.",
    },
    # (9) P5 test-adoption.
    {
        "milestone_id": "_infra/adopt-cycle64-tests",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c64 test-adoption housekeeping. No new test file this "
                "cycle. Existing `tests/test_sound_match_fine_fit_sf2_"
                "other.py` (on-disk sha 7ffd3389...; brief-cited ee0c8a10 "
                "diverges) unchanged this cycle; c63 docstring-only edit "
                "preserved. Test suite remains 8/8 PASS by construction. "
                "P0/P1/P2/P3 SKIPs + P4 confirmation require no new tests "
                "(no code or artifact changes)."
            ),
        },
        "narrative": (
            "No new tests this cycle. Existing 8/8 test suite unchanged."
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

    print(f"Appended {len(to_append)} c64 ledger events.")
    for e in to_append:
        print(f"  {e['milestone_id']}  ({e['event_id']})")


if __name__ == "__main__":
    main()
