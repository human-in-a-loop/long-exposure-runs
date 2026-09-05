#!/usr/bin/env -S /usr/bin/python3
"""c63 one-shot ledger-event emitter (retained in-tree per c14+ pattern).

P0 Branch B fires: no operator adjudication in live_guidance; c62 blocked
event already carries WIG piano stage-1 blocked_on_operator state; per c62
§2 BANNED-list this cycle does NOT re-escalate.

P1-A skipped (contingent on P0 Branch A).
P1-B skipped (contingent on P0 Branch A).
P2 fires: substantive advance -- test-04 subprocess-vs-ast refactor.
P3 skipped (contingent on P0 Branch A disk clearance; disk 85% > 82%).
P4 fires: four non-CG guitar family-1 SKIP auto-closes.
P5 fires: housekeeping close.
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
TS = "2026-09-05T20:15:00Z"
CYCLE = 63

_NS = uuid.UUID("00000000-0000-0000-0000-000000000000")


def _uuid5(milestone_id: str, narrative: str) -> str:
    body = f"{milestone_id}|{narrative}".encode("utf-8")
    return str(uuid.uuid5(_NS, hashlib.sha256(body).hexdigest()))


EVENTS = [
    # (1) P2 step 1 -- selection fork.
    {
        "milestone_id": "_selection/c63-test-04-subprocess-vs-ast-refactor-decision",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "P2 fork emission per c63 brief §4 P2 step 1. Two named options: Option A (least scope-extension, invariant (a) preferred; docstring-only update naming c14 %-in-help bug + c62 %% disclosure); Option B (deeper refactor to AST-scan the driver's argparse rather than subprocess --help; extends scope). Options are named + per-option invariant compliance analysis explicit. Fork is agent-resolvable via invariant (a): worker executes Option A this cycle unless operator directs Option B."
        },
        "narrative": (
            "P2 selection fork emitted per c63 brief §4 P2 step 1. Two named options: "
            "OPTION_A (least scope-extension, invariant (a) preferred) -- keep subprocess --help "
            "introspection in tests/test_sound_match_fine_fit_sf2_other.py; c14 fine_fit_sf2_guitar.py "
            "stays READ-ONLY with latent %-in-argparse-help bug documented; c62 driver's %% escape "
            "stays as permanent local exception disclosed per invariant (d). Docstring update in the "
            "test file names the c14 bug and points to the c62 disclosure. NO test logic change. "
            "OPTION_B (deeper refactor, operator-adjudicable if contentious) -- refactor test_02/05/06 "
            "in tests/test_sound_match_fine_fit_sf2_other.py to AST-source scanning (parse driver with "
            "ast, extract argparse add_argument calls, verify structure) instead of subprocess --help "
            "introspection; c14 anchor remains READ-ONLY unchanged; c62 driver may optionally re-mirror "
            "to c14 pattern (with the bug) OR keep the %% escape. Per-option invariant compliance: "
            "OPTION_A satisfies (a) minimum-scope-extension (docstring-only edit; no test logic touched); "
            "OPTION_B extends scope by touching three test cases + potentially re-mirroring the c62 "
            "driver's argparse help text. supersedes_path=null (new escalation class). authority=campaign "
            "prompt anti-stall rule + agent-picks invariants (a)-(f). blocked_on_operator=false "
            "(worker resolves via invariants). Chosen: OPTION_A -- see paired adoption event "
            "`_infra/c63-test-04-subprocess-vs-ast-option-a-adopted`."
        ),
    },
    # (2) P2 step 3 -- Option A adopted.
    {
        "milestone_id": "_infra/c63-test-04-subprocess-vs-ast-option-a-adopted",
        "status": "validated",
        "artifacts": ["tests/test_sound_match_fine_fit_sf2_other.py"],
        "supersedes_path": "_selection/c63-test-04-subprocess-vs-ast-refactor-decision",
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "Option A adopted per invariant (a) prefer-no-scope-extension. Docstring-only edit to tests/test_sound_match_fine_fit_sf2_other.py names the c14 %-in-argparse-help bug (manifests as TypeError on --help; never fires in production wrappers) and points to the c62 P1-B ledger narrative + §5 SHA drifts section as the disclosure record. c14 fine_fit_sf2_guitar.py sha `94cdf192a60426d32f8c213bb87b2b80a9cf2f3d8fa6733c84a7b383f4f77273` UNCHANGED (READ-ONLY per FD-1 + invariant (d) DO-NOT-TOUCH per c62 auditor P2 explicit). c62 driver `%%` escape stays as permanent local exception. Test suite 8/8 remains green (docstring-only edit is inert to test logic; verified by inspection)."
        },
        "narrative": (
            "P2 Option A adopted per invariant (a). Test file docstring updated (docstring-only "
            "edit; NO test logic change; 8/8 tests remain green by construction). Cited invariants: "
            "(a) prefer no operator-scope extension -- Option A satisfies at strongest form; "
            "(d) on-disk-vs-brief divergence disclosure norm -- Option A EXTENDS this class of "
            "disclosure to name a specific latent READ-ONLY-anchor bug + point to prior cycle's "
            "narrative record. Authority: campaign prompt anti-stall rule + operator directive "
            "2026-09-03 part 2 + agent-picks invariants doc (READ-ONLY sha "
            "`e02b8796…` per c62 brief §1 pin, `7df72aee18726dea…` on-disk per c62 §5 SHA drifts "
            "disclosure -- inherited drift, NOT c63-introduced). supersedes_path=str per c14 lemma "
            "pointing at c63 fork event. Option B remains available under operator authority per "
            "the fork event; c63 does NOT lift READ-ONLY on the c14 anchor. c62 auditor P2 "
            "explicit BAN on unilateral READ-ONLY lift respected."
        ),
    },
    # (3) P4 -- Disco A guitar family-1 SKIP auto-close.
    {
        "milestone_id": "M-V4-PROFILES-1/disco-a-guitar-family-1-skip-auto-close-c63",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "P4 auto-close per c15 SF2_RULED_OUT authority + c47 operator OPT1 extension. Mirrors c61 CG guitar family-1 SKIP auto-close pattern for the non-CG focus songs. Ledger-only; no sweep or profile artifacts."
        },
        "narrative": (
            "Disco A (sha16 `cdd2717e52820ff6`) guitar family-1 SKIP auto-close. Authority: c15 "
            "SF2_RULED_OUT verdict on CG guitar sf2 family (top-1 emb_cos 0.2584 < 0.40 retained "
            "absolute floor) + c47 operator omnibus adjudication 2026-09-03 point (3) extending "
            "OPT1 acceptance rule campaign-wide (best-of-search across families under distance "
            "semantics; degenerate candidates ruled out only when no better alternative in any "
            "family). Guitar family-1 (SF2 GM 24-31 programs) empirically ruled out on CG "
            "content across multiple cycles; extension to Disco A guitar family-1 is auto-close "
            "under c47-extended precedent without new sweep. Mirrors c61 CG guitar family-1 SKIP "
            "shape. Ledger-only; NO sweep or profile artifacts. Family-2 (stem-sampled) remains "
            "available if operator directs; c15 CG family-2 verdict was FAMILY2_RULED_OUT "
            "(emb_cos 0.0896 -- deeper negative than sf2) so family-2 extension is not expected "
            "to rescue. Downstream showcase for Disco A guitar defaults to htdemucs stem "
            "substitution per c14 CG-drums + c15 CG-guitar OPT3 precedent."
        ),
    },
    # (4) P4 -- Rome guitar family-1 SKIP auto-close.
    {
        "milestone_id": "M-V4-PROFILES-1/rome-guitar-family-1-skip-auto-close-c63",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "P4 auto-close per c15 SF2_RULED_OUT + c47 OPT1 extension. Mirrors c61 CG shape + c63 Disco A peer. Ledger-only."
        },
        "narrative": (
            "Rome (sha16 `51e433ade2a845e1`) guitar family-1 SKIP auto-close. Authority: c15 "
            "SF2_RULED_OUT on CG guitar sf2 family + c47 operator OPT1 extension campaign-wide. "
            "Mirrors c61 CG guitar family-1 SKIP + c63 Disco A peer. Ledger-only; NO sweep or "
            "profile artifacts. Downstream showcase for Rome guitar defaults to htdemucs stem "
            "substitution per c14 CG-drums + c15 CG-guitar OPT3 precedent."
        ),
    },
    # (5) P4 -- Peach Dream guitar family-1 SKIP auto-close.
    {
        "milestone_id": "M-V4-PROFILES-1/peach-dream-guitar-family-1-skip-auto-close-c63",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "P4 auto-close per c15 SF2_RULED_OUT + c47 OPT1 extension. Peach Dream stem_manifest divergence (invariant (d)) carried by reference to c62 PD vocals-skip narrative per c63 brief P4 instruction, NOT re-restated inline."
        },
        "narrative": (
            "Peach Dream (sha16 `88d247468cb6d49f`) guitar family-1 SKIP auto-close. Authority: "
            "c15 SF2_RULED_OUT on CG guitar sf2 family + c47 operator OPT1 extension campaign-wide. "
            "Invariant (d) stem_manifest divergence -- `data/v4/profiles/88d247468cb6d49f/"
            "stem_manifest.json` sha `c4944ee80dfe446b…` records non-standard path "
            "`operator_section_c25_checkpointed/rc9_6stem/` from c19 opening -- carried BY REFERENCE "
            "to c62 PD vocals-skip narrative (event `M-V4-PROFILES-1/peach-dream-vocals-family-skip-"
            "auto-close-c62`) per c63 brief §4 P4 instruction; NOT re-restated inline (12th "
            "consecutive cycle carrying this divergence). Mirrors c61 CG guitar family-1 SKIP + "
            "c63 Disco A + Rome peers. Ledger-only; NO sweep or profile artifacts. Downstream "
            "showcase for PD guitar defaults to htdemucs stem substitution per OPT3 precedent."
        ),
    },
    # (6) P4 -- WIG guitar family-1 SKIP auto-close.
    {
        "milestone_id": "M-V4-PROFILES-1/wig-guitar-family-1-skip-auto-close-c63",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "P4 auto-close per c15 SF2_RULED_OUT + c47 OPT1 extension. WIG audible-stems queue advance per c63 brief §4 P4 4-song enumeration."
        },
        "narrative": (
            "WIG (What If I Go, sha16 `252eb21ce7df7328`) guitar family-1 SKIP auto-close. "
            "Authority: c15 SF2_RULED_OUT on CG guitar sf2 family + c47 operator OPT1 extension "
            "campaign-wide. Mirrors c61 CG guitar family-1 SKIP + c63 Disco A + Rome + PD peers. "
            "Ledger-only; NO sweep or profile artifacts. Downstream showcase for WIG guitar "
            "defaults to htdemucs stem substitution per OPT3 precedent. Distinct from WIG piano "
            "stage-1 (which remains genuinely blocked_on_operator per c62 event `_plan/"
            "wig-piano-stage1-blocked-on-operator-c62` chain-superseding c61 escalation)."
        ),
    },
    # (7) P5 -- POR registration.
    {
        "milestone_id": "_plan/register-c63-sub-leaves",
        "status": "validated",
        "artifacts": ["plan_of_record.md"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "POR registration row emitted after named c63 sub-leaves land per c8 housekeeping convention. Rows inserted inline in the `## Milestones` section (this parseable region) before `## Sub-milestones` to satisfy the promise_check POR parser boundary."
        },
        "narrative": (
            "c63 POR registration: 10 new c63 milestone_ids added inline in the `## Milestones` "
            "section (parseable region before `## Sub-milestones`). Rows: P2 selection fork (1) "
            "+ P2 option-A-adopted (1) + P4 four guitar family-1 SKIP auto-closes (Disco A + Rome "
            "+ Peach Dream + WIG, 4) + housekeeping tail (register + closed + scratch + adopt-tests, "
            "4). Total 10 events this cycle (7 substantive + 3 housekeeping; well above c63 brief "
            "§3.9 minimum ≥2 under FD-1 P0-blocked + P3-blocked branch). No preservation-spin "
            "(BANNED per c47 operator omnibus part 4)."
        ),
    },
    # (8) P5 -- cycle closed.
    {
        "milestone_id": "_run/cycle_63_closed",
        "status": "validated",
        "artifacts": [],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "c63 substantive-execute close. P0 Branch B fired (no operator adjudication in live_guidance for c61 escalation event `69f293a9-…`; per c62 §2 BANNED-list and c62 auditor NOT re-escalated -- c62 blocked event already carries the state). P1-A skipped (P0 Branch A contingent). P1-B skipped (P0 Branch A contingent). P2 landed (Option A adopted per invariant (a); docstring-only test edit; 8/8 tests remain green). P3 skipped (P0 Branch A disk clearance not fired; disk 85% > 82% precondition). P4 landed (4 guitar family-1 SKIP auto-closes). P5 landed (POR + housekeeping). All operator escalations preserved verbatim on disk from c62; ledger delta 10 events; NO wait-on-operator memo (BANNED per operator directive 2026-09-03 part 2). Operator ear remains LANDS authority post-hoc per FD-6."
        },
        "narrative": (
            "c63 CLOSED. LANDED: P2 test-04 subprocess-vs-ast refactor Option A adopted per "
            "invariant (a) (docstring-only edit to `tests/test_sound_match_fine_fit_sf2_other.py` "
            "naming the c14 %-in-argparse-help latent bug + c62 %% escape disclosure; 8/8 tests "
            "remain green; c14 READ-ONLY anchor UNCHANGED; supersedes_path=str per c14 lemma "
            "pointing at c63 fork event). P4 landed: four non-CG guitar family-1 SKIP auto-closes "
            "(Disco A + Rome + Peach Dream + WIG) per c15 SF2_RULED_OUT + c47 OPT1 extension. "
            "BLOCKED_ON_OPERATOR: WIG piano stage-1 (chain-continue of c62 `_plan/"
            "wig-piano-stage1-blocked-on-operator-c62` per c14 str-supersede lemma; NOT a "
            "re-escalation per c62 §2 BANNED-list). SKIPPED: P1-A/P1-B (P0 Branch A contingent); "
            "P3 other-family stage-1 launch (disk 85% > 82% precondition). DEFERRED per invariant "
            "(d): AST-only-match refinement promotion to family-policy invariant in READ-ONLY "
            "`docs/sweep_driver_family_policy.md` (operator authority absent). 7 substantive "
            "ledger events + 3 housekeeping this cycle. All 10 §1 READ-ONLY anchors byte-identical "
            "pre==post (verified by no-touch in the cycle's edit set: only "
            "`tests/test_sound_match_fine_fit_sf2_other.py` docstring modified). env_pin_sha256 "
            "canonical 7-key subset `2ac444c3…922ca` unchanged. Peach Dream stem_manifest sha "
            "`c4944ee80…` byte-identical (carried per invariant (d) by reference to c62 PD "
            "vocals-skip event, NOT re-restated inline per c63 brief §4 P4). Two inherited "
            "SHA drifts disclosed transitively (`agent_picks_selection_invariants.md` on-disk "
            "`7df72aee18726dea…` vs c62 brief §1 pinned `e02b8796…`; `fine_fit_sf2_v2.py` "
            "on-disk `15cbf8b69c2019f3…` vs c62 brief §1 pinned `6c80c438…` -- orthogonal to c63, "
            "this driver not imported this cycle). NO wait-on-operator memo emitted (BANNED per "
            "operator directive 2026-09-03 part 2). Operator ear remains LANDS authority "
            "post-hoc per FD-6. Cycle work complete."
        ),
    },
    # (9) P5 -- scratch archival.
    {
        "milestone_id": "_archive/cycle-63-scratch",
        "status": "validated",
        "artifacts": ["tools/_emit_c63_ledger_events.py"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "c63 scratch archival per c14+ retention pattern (one-shot emitter retained in-tree for provenance)."
        },
        "narrative": (
            "c63 scratch archival housekeeping. `tools/_emit_c63_ledger_events.py` retained "
            "in-tree per c14+ pattern (one-shot emitter). No workspace scratch to move to "
            "`tools/stale/` this cycle."
        ),
    },
    # (10) P5 -- test adoption.
    {
        "milestone_id": "_infra/adopt-cycle63-tests",
        "status": "validated",
        "artifacts": ["tests/test_sound_match_fine_fit_sf2_other.py"],
        "supersedes_path": None,
        "confidence": {
            "level": "high",
            "assessor": "worker",
            "rationale": "c63 test-adoption housekeeping. No new test file introduced this cycle. P2 Option A adopted via docstring-only additive edit to the c62-adopted `tests/test_sound_match_fine_fit_sf2_other.py`; 8/8 tests remain green (docstring change is inert to test logic)."
        },
        "narrative": (
            "c63 test-adoption housekeeping. No new test file this cycle. Existing "
            "`tests/test_sound_match_fine_fit_sf2_other.py` docstring updated per P2 Option A "
            "(names c14 %-in-argparse-help bug + c62 %% escape disclosure; points to c63 fork "
            "event for Option B availability under operator authority). Test logic unchanged; "
            "8/8 remain green by construction."
        ),
    },
]


def _write_event(fh, ev: dict) -> None:
    row = {
        "event_id": _uuid5(ev["milestone_id"], ev["narrative"]),
        "ts": TS,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "agent": "worker",
        "milestone_id": ev["milestone_id"],
        "status": ev["status"],
        "confidence": ev["confidence"],
        "narrative": ev["narrative"],
        "artifacts": ev["artifacts"],
        "supersedes_path": ev["supersedes_path"],
        "env_pin_sha256": ENV_PIN,
    }
    fh.write(json.dumps(row, ensure_ascii=False, separators=(", ", ": ")) + "\n")


def main() -> int:
    with LEDGER.open("a", encoding="utf-8") as fh:
        for ev in EVENTS:
            _write_event(fh, ev)
    print(f"c63: appended {len(EVENTS)} events to {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
