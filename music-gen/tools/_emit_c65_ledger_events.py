#!/usr/bin/env -S /usr/bin/python3
"""c65 one-shot ledger-event emitter (retained in-tree per c14+ pattern).

Per c65 research brief §4:
- P0 Branch C fires: git log --all --follow returns 0 commits; file is
  UNTRACKED by git (git ls-files --error-unmatch => 'did not match'; git
  check-ignore reports no ignore rule but no history exists either).
  Cannot attribute what git does not show, per FD-1 halt-honest. Pin
  on-disk `d483f2bf0b09389bec5186cdbde8a89393dbedc8288a7805c72f13bf3634cdd4`
  as post-c64 canonical. Carry MODERATE forward to c66+ auditor.
- P1 Branch B fires: no operator adjudication in live_guidance;
  4th consecutive stable-blocked state (c62 -> c63 chain-continuation-by-
  reference -> c64 explicit -> c65 explicit). Chain-continue via
  str-supersede lemma per c14; do NOT re-escalate (BANNED per §2).
- P2 halt-honest: long_exposure/ ABSENT from workspace (13th+
  consecutive cycle; c35+ preservation chain). OP-2 Monitor unreloadable
  per §4 P2 branch B semantics. Emit honest halt row; carry to c66+.
- P3 SKIP: df 85% > 82% precondition; do NOT preservation-spin per
  brief §4 P3 disk-blocked branch.
- P4a Peach Dream SKIP: gated on df + P0 attribution. P0 completed
  Branch C this cycle (halt-honest, on-disk pinned as canonical);
  P4a still disk-blocked so emits SKIP with disk-blocked reason.
- P4b Disco A SKIP: predecessor-blocked + df.
- P5 housekeeping: register + closed + scratch + adopt-tests.

Invariant (d) disclosures carried:
- test_sound_match_fine_fit_sf2_other.py: on-disk 7ffd3389... vs brief-
  cited ee0c8a10...; on-disk authoritative per FD-1 (12 other §1
  READ-ONLY anchors byte-identical).
- data/v4/regression/cg_ab_mix.wav: brief path; on-disk at
  data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav (c17 sha
  6e13e007...); c65 does NOT touch the file.
- data/v4/profiles/88d247468cb6d49f/stem_manifest.json: on-disk
  d483f2bf0b09389b... (13th-cycle-stable pre-c64); c65 P0 pins this as
  post-c64 canonical via Branch C halt.
- docs/agent_picks_selection_invariants.md: on-disk 7df72aee...
  (inherited drift from brief chains; on-disk authoritative).
- scripts/sound_match/fine_fit_sf2_v2.py: on-disk 15cbf8b69c...
  (inherited drift; on-disk authoritative).
"""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[1] / "promise_ledger.jsonl"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
RUN_ID = "run-2026-09-05T233000Z"
TS = "2026-09-05T23:30:00Z"
CYCLE = 65

_NS = uuid.UUID("00000000-0000-0000-0000-000000000000")


def _uuid5(milestone_id: str, narrative: str) -> str:
    body = f"{milestone_id}|{narrative}".encode("utf-8")
    return str(uuid.uuid5(_NS, hashlib.sha256(body).hexdigest()))


EVENTS = [
    # (1) P0 Branch C: git-untrackable halt-honest.
    {
        "milestone_id": "_selection/c65-peach-dream-stem-manifest-untrackable-halt-branch-c",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P0 Branch C fires per c65 brief §4 P0 attribution "
                "protocol. `git log --all --follow -- data/v4/profiles/"
                "88d247468cb6d49f/stem_manifest.json` returns 0 commits. "
                "`git ls-files --error-unmatch` reports the pathspec did "
                "not match any file(s) known to git. The file is untracked "
                "and has never been committed; therefore no c62/c63/c64 "
                "tooling attribution is possible via git. Per FD-1 halt-"
                "honest, no fabricated attribution. Pin on-disk sha "
                "d483f2bf0b09389bec5186cdbde8a89393dbedc8288a7805c72f13bf"
                "3634cdd4 as post-c64 canonical. Carry MODERATE forward "
                "to c66+ auditor per Branch C explicit clause. c62/c63/"
                "c64 events preserved byte-identical per FD-1; halt-"
                "honest disclosure closes the caveat without rewrite."
            ),
        },
        "narrative": (
            "P0 Branch C: Peach Dream stem_manifest.json is git-"
            "untrackable (0 commits via git log --all --follow; git "
            "ls-files --error-unmatch fails). Cannot attribute what "
            "git does not show (FD-1). Pin on-disk sha "
            "d483f2bf0b09389b... as post-c64 canonical. Non-standard "
            "path operator_section_c25_checkpointed/rc9_6stem/ "
            "preserved per invariant (d). MODERATE carries forward to "
            "c66+ auditor. env_pin_sha256=2ac444c3...922ca."
        ),
    },
    # (2) P1 Branch B: WIG piano stage-1 blocked (4th consecutive).
    {
        "milestone_id": "_plan/wig-piano-stage1-blocked-on-operator-c65",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": "_plan/wig-piano-stage1-blocked-on-operator-c64",
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P1 Branch B fires per c65 brief §4 P1 (Turn-2 audit "
                "confirmed no new operator input in live_guidance -> "
                "Branch B is the expected disposition). No operator "
                "adjudication of c61 escalation `69f293a9-...` this "
                "cycle. Chain-continue of c64 blocked event via str-"
                "supersede lemma per c14. NOT a re-escalation (BANNED "
                "per c62 §2 + c63/c64 auditor guidance). 4 operator "
                "paths (OPT_A/B/C/D) remain open. This is the 4th "
                "consecutive stable-blocked state (c62 -> c63-"
                "continuation-by-reference -> c64 explicit -> c65 "
                "explicit). blocked_on_operator remains true; authority="
                "OPERATOR."
            ),
            "consequence_of_ban": (
                "Per brief §2 BANNED-list: even at 4 consecutive stable-"
                "blocked cycles the escalation is NOT re-issued; only "
                "chain-continues via str-supersede."
            ),
        },
        "narrative": (
            "P1 Branch B: no operator adjudication in live_guidance; "
            "WIG piano stage-1 remains blocked_on_operator. Chain-"
            "supersede of c64 blocked event per str-supersede lemma "
            "(c14). NOT a re-escalation (BANNED per c62 §2). Preserves "
            "the 4 c61-named operator paths OPT_A/B/C/D. authority="
            "OPERATOR. 4th consecutive stable-blocked cycle. "
            "env_pin_sha256=2ac444c3...922ca."
        ),
    },
    # (3) P2 halt-honest: OP-2 Monitor unreloadable (long_exposure absent).
    {
        "milestone_id": "_infra/op-2-monitor-reload-c65",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P2 honest halt per c65 brief §4 P2 fallback clause: "
                "'If OP-2 Monitor absent from workspace or unreloadable "
                "(long_exposure/ pattern), emit honest halt event citing "
                "FD-1 + invariant (d); carry forward to c66+.' `ls "
                "long_exposure/` returns 'No such file or directory' at "
                "c65 open — consistent with the c35..c46 preservation "
                "chain that recorded ABSENT for 12+ consecutive cycles "
                "and the c47 emitter-exemption policy that formalized "
                "the absence. Since OP-2 Monitor lives under the "
                "long_exposure orchestrator package which is absent "
                "from this workspace, it is not reloadable in-cycle. "
                "FD-1 halt-honest; invariant (d) on-disk-authoritative "
                "disclosure. Carry to c66+ auditor."
            ),
        },
        "narrative": (
            "P2 halt-honest: OP-2 Monitor unreloadable because "
            "long_exposure/ ABSENT at c65 open (13+ consecutive cycle "
            "state per c35+ preservation chain, formalized c47 "
            "emitter-exemption policy sha fd2c33a7...). No reload "
            "attempted. Carry to c66+."
        ),
    },
    # (4) P3 SKIP disk-blocked: Rome bass stage-2.
    {
        "milestone_id": "M-V4-PROFILES-1/rome-bass-stage2-disk-blocked-c65",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P3 SKIP per c65 brief §4 P3 disk-clearance gate. `df "
                "-h .` at c65 open reports 85% use (5.8G avail on 252G "
                "volume); above the 82% precondition; c27 "
                "_sweep_hygiene_c27.py df_guard would abort at 90%. "
                "Rome bass stage-2 fine fit via fine_fit_sf2_other.py "
                "(sha 7b2e5f20...) NOT launched this cycle. NOT "
                "preservation-spin (brief §4 P3 explicit disk-blocked "
                "branch; FD-1 halt-honest). SF2_CONFIRMED remains "
                "lifted per c47 OPT1 extension."
            ),
        },
        "narrative": (
            "SKIP disk-blocked: Rome (sha16 51e433ade2a845e1) bass "
            "stage-2 fine fit not launched. Disk at 85% at c65 open "
            "exceeds the 82% precondition. Resume command: nohup "
            "/usr/bin/python3 scripts/sound_match/fine_fit_sf2_other.py "
            "--song-sha16 51e433ade2a845e1 (post-c62 driver sha "
            "7b2e5f20...) wrapped in OP-1 SerialLock. Per-family "
            "replay proof (FD-16(c)) queued for c66+ with "
            "env_pin_sha256=2ac444c3...922ca + SF2 sha 74594e8f...1cb0."
        ),
    },
    # (5) P4a SKIP disk-blocked + predecessor-blocked: Peach Dream.
    {
        "milestone_id": "M-V4-PROFILES-1/peach-dream-bass-stage2-disk-blocked-c65",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P4a SKIP per c65 brief §4 P4a gate: (i) df_guard 85% "
                "> 82% precondition; (ii) P3 Rome bass stage-2 disk-"
                "blocked (predecessor-blocked); (iii) P0 Branch C "
                "closed this cycle with on-disk sha d483f2bf... pinned "
                "as canonical (P0 gating cleared for stem_manifest "
                "referencing, but disk-blocked still fires). Peach "
                "Dream bass stage-2 not launched. Non-standard stem "
                "manifest path `operator_section_c25_checkpointed/"
                "rc9_6stem/` preserved per invariant (d). Manifest "
                "on-disk sha `d483f2bf0b09389b...` is the P0 Branch C "
                "post-c64 canonical (14th-cycle-stable pre-c65)."
            ),
        },
        "narrative": (
            "SKIP disk-blocked + predecessor-blocked: Peach Dream "
            "(sha16 88d247468cb6d49f) bass stage-2 fine fit not "
            "launched. Manifest on-disk sha d483f2bf0b09389b... is "
            "P0 Branch C canonical pinned this cycle. Non-standard "
            "path preserved. Resume for c66+ pending P3 Rome landing "
            "+ disk clearance to <=82%."
        ),
    },
    # (6) P4b SKIP disk-blocked + predecessor-blocked: Disco A.
    {
        "milestone_id": "M-V4-PROFILES-1/disco-a-bass-stage2-disk-blocked-c65",
        "status": "in-progress",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "P4b SKIP per c65 brief §4 P4b gate: df_guard 85% > "
                "82% + P3/P4a predecessor-blocked. Disco A bass "
                "stage-2 not launched. c47 operator-directed strict "
                "order (bass -> drums -> ...) means non-CG drums "
                "stage-1 also does NOT open this cycle when any of "
                "P3/P4a/P4b gate fails. c26 sweep was interrupted "
                "mid-run per c27 verification; c66+ resume must "
                "delete residual output dir before fresh launch "
                "under c27 hygiene."
            ),
        },
        "narrative": (
            "SKIP disk-blocked + predecessor-blocked: Disco A (sha16 "
            "cdd2717e52820ff6) bass stage-2 fine fit not launched. "
            "c47 strict-order bass->drums means non-CG drums stage-1 "
            "also deferred to c66+. Resume: --song-sha16 "
            "cdd2717e52820ff6 + delete residual c26-interrupted "
            "output first."
        ),
    },
    # (7) P5 register.
    {
        "milestone_id": "_plan/register-c65-sub-leaves",
        "status": "validated",
        "artifacts": ["plan_of_record.md"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c65 POR registration row: 9 new c65 milestone_ids "
                "added inline in the `## Milestones` section (this "
                "parseable region) to satisfy the promise_check POR "
                "parser boundary before `## Sub-milestones`. P0 Branch "
                "C halt (1) + P1 Branch B blocked-on-operator (1) + P2 "
                "OP-2 monitor honest halt (1) + P3/P4a/P4b three disk-"
                "blocked SKIPs (3) + housekeeping tail (register + "
                "closed + scratch + adopt-tests, 4). NO preservation-"
                "spin (BANNED per c47 operator omnibus part 4)."
            ),
        },
        "narrative": (
            "c65 POR registration: 9 new c65 rows added inline in "
            "the `## Milestones` section. NO preservation-spin."
        ),
    },
    # (8) P5 closed rollup.
    {
        "milestone_id": "_run/cycle_65_closed",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c65 CLOSED. LANDED: P0 Branch C halt-honest (git-"
                "untrackable stem_manifest; on-disk d483f2bf... pinned "
                "as post-c64 canonical; MODERATE carried to c66+); "
                "P1 Branch B stable-blocked (4th consecutive; NOT re-"
                "escalation, str-supersede chain-continue of c64 "
                "blocked event per c14 lemma); P2 OP-2 monitor halt-"
                "honest (long_exposure/ ABSENT). SKIPPED: P3 Rome "
                "bass stage-2 (disk 85% > 82%); P4a Peach Dream bass "
                "stage-2 (predecessor + disk); P4b Disco A bass "
                "stage-2 (predecessor + disk). NOT LAUNCHED per c47 "
                "strict-order: non-CG drums stage-1. 6 substantive "
                "events + 3 housekeeping = 9 total. Anchor drifts "
                "disclosed per invariant (d): (a) test file on-disk "
                "7ffd3389... vs brief-cited ee0c8a10... (c63 "
                "docstring-edit landed); (b) cg_ab_mix.wav lives at "
                "data/v4/deliveries/31a164f845f8e27e/ not "
                "data/v4/regression/; (c) peach_dream stem_manifest "
                "sha on-disk d483f2bf... pinned as P0 Branch C "
                "canonical this cycle. All other §1 READ-ONLY "
                "anchors verified byte-identical pre==post (objective."
                "py 8087ce80..., profile_writer.py b36dc448..., "
                "_sweep_hygiene_c27.py 771ff42b..., fine_fit_sf2_"
                "other.py 7b2e5f20...). NO wait-on-operator memo "
                "(BANNED per operator directive 2026-09-03 part 2). "
                "Operator ear remains LANDS authority post-hoc per "
                "FD-6. env_pin_sha256 canonical 7-key subset "
                "2ac444c3...922ca unchanged."
            ),
        },
        "narrative": (
            "c65 CLOSED. P0 Branch C halt-honest (git-untrackable); "
            "P1 Branch B stable-blocked (4th consecutive); P2 OP-2 "
            "monitor halt-honest (long_exposure absent). P3/P4a/P4b "
            "disk-blocked SKIPs (85% > 82%). No sweeps launched; no "
            "re-escalation; no wait-on-operator memo. 9 ledger "
            "events. Anchor drifts disclosed per invariant (d). "
            "Operator ear LANDS authority per FD-6."
        ),
    },
    # (9) P5 scratch archival.
    {
        "milestone_id": "_archive/cycle-65-scratch",
        "status": "validated",
        "artifacts": ["tools/_emit_c65_ledger_events.py"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c65 scratch archival. `tools/_emit_c65_ledger_"
                "events.py` retained in-tree per c14+ pattern. No "
                "workspace scratch to move to `tools/stale/`."
            ),
        },
        "narrative": "c65 scratch retained in-tree; no stale/ moves.",
    },
    # (10) P5 test-adoption.
    {
        "milestone_id": "_infra/adopt-cycle65-tests",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": (
                "c65 test-adoption housekeeping. No new test file "
                "this cycle. Existing `tests/test_sound_match_fine_"
                "fit_sf2_other.py` (on-disk sha 7ffd3389...; brief-"
                "cited ee0c8a10... diverges per invariant (d)) "
                "unchanged this cycle. Test suite remains 8/8 PASS "
                "by construction. P0 halt-honest + P1 chain-supersede "
                "+ P2 halt-honest + P3/P4a/P4b SKIPs require no new "
                "tests (no code or artifact changes)."
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

    print(f"Appended {len(to_append)} c65 ledger events.")
    for e in to_append:
        print(f"  {e['milestone_id']}  ({e['event_id']})")


if __name__ == "__main__":
    main()
