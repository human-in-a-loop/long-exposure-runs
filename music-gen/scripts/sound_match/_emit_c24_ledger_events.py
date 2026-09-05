#!/usr/bin/python3
"""Emit c24 ledger events via long_exposure.tools.ledger_append.

Events:
  1-4. M-V4-PROFILES-1/<sha16>-bass-family-verdict-revised-c24 (×4)
  5.   _manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy
  6.   M-V4-SHOWCASE-1/cg-drums-acceptance-c22-corrected-disclosure-c24
  7.   M-V4-SHOWCASE-1/cg-guitar-acceptance-c22-corrected-disclosure-c24
  8.   M-V4-CLOSE-1/c24-amendment
  9.   _plan/register-c24-non-cg-bass-verdicts-revised-and-cg-drums-guitar-c22-corrected-disclosures
  10.  _archive/cycle-24-scratch
  11.  _infra/adopt-cycle24-tests
  12.  _run/cycle_24_closed

event_id: UUID5 from content hash.
supersedes_path: str per c14 lemma.
"""
import hashlib, json, os, subprocess, uuid
from pathlib import Path

WS = Path("/home/user/long-exposure-runs/music-gen")
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
CREATED = "2026-09-05T00:00:00Z"
TS = "2026-09-05T00:00:00Z"
RUN_ID = "run-2026-09-05T000000Z"

def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def event_id(milestone_id, narrative, i):
    h = f"{milestone_id}|{narrative[:200]}|{RUN_ID}|{TS}|{i}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, h))

def build_events():
    closeout = json.loads((WS / "data/v4/deliveries/31a164f845f8e27e/cycle24/track_a_d_closeout.json").read_text())
    ta = closeout["track_a_results"]
    td = closeout["track_d_result"]
    esc_sha = closeout["track_a_escalation_sha256"]
    amend_sha = sha256_file(WS / "docs/v4_closure_completion_report_c24_amendment.md")

    events = []
    # 1-4: revised bass verdicts
    for i, r in enumerate(ta):
        mid = f"M-V4-PROFILES-1/{r['sha16']}-bass-family-verdict-revised-c24"
        narr = (
            f"{r['name']} bass verdict revised c24: c23 SF2_CONFIRMED reversed to {r['verdict']} "
            f"under corrected 0.40 distance-upper-bound reading (emb_cos_dist={r['emb_dist']:.4f}). "
            f"c23 artifact preserved byte-identical at {r['stale_path']} (sha256 {r['stale_c23_sha'][:16]}…). "
            f"New verdict sha256 {r['new_verdict_sha'][:16]}…."
        )
        events.append({
            "event_id": event_id(mid, narr, i),
            "milestone_id": mid,
            "status": "validated",
            "cycle": 24,
            "agent": "worker",
            "run_id": RUN_ID,
            "ts": TS,
            "confidence": {"level": "high", "rationale": "on-disk emb_cos_dist byte-verified vs brief; verdict follows corrected distance-upper-bound reading", "assessor": "worker"},
            "narrative": narr,
            "artifacts": [
                f"data/v4/profiles/{r['sha16']}/bass_family_verdict_c23.json",
                r["stale_path"],
            ],
            "supersedes_path": r["stale_path"],
        })

    # 5. escalation
    mid = "_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy"
    narr = (
        f"c24 operator-authority escalation: composite-relative WINNER precedent scope-extension "
        f"from c9 CG-bass to non-CG bass requires operator authority per FD-6. "
        f"blocked_on_operator=true; 3 named options (OPT1 extend, OPT2 refuse fallback OPT3, "
        f"OPT3 case-by-case). Escalation sha256 {esc_sha[:16]}…."
    )
    events.append({
        "event_id": event_id(mid, narr, 5),
        "milestone_id": mid,
        "status": "action_required",
        "cycle": 24,
        "agent": "worker",
        "run_id": RUN_ID,
        "ts": TS,
        "confidence": {"level": "high", "rationale": "parallel to c7 CG-bass shape; blocked_on_operator=true per FD-6", "assessor": "worker"},
        "narrative": narr,
        "artifacts": ["data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json"],
        "supersedes_path": None,
    })

    # 6. drums disclosure
    mid = "M-V4-SHOWCASE-1/cg-drums-acceptance-c22-corrected-disclosure-c24"
    narr = (
        f"CG drums acceptance corrected-disclosure: c14 OPT3 stands under corrected distance "
        f"semantics per invariants (a)/(b)/(c); composite-relative WINNER precedent scope-extension "
        f"from c9 CG-bass to CG-drums still requires operator authority. Sibling (supersedes_path=null). "
        f"Disclosure sha256 {td['drums_disclosure_sha'][:16]}…. c14 pinned byte-identical."
    )
    events.append({
        "event_id": event_id(mid, narr, 6),
        "milestone_id": mid,
        "status": "validated",
        "cycle": 24,
        "agent": "worker",
        "run_id": RUN_ID,
        "ts": TS,
        "confidence": {"level": "high", "rationale": "sibling disclosure per Track D wording; c14 anchor byte-identical", "assessor": "worker"},
        "narrative": narr,
        "artifacts": ["data/v4/deliveries/31a164f845f8e27e/cg_drums_acceptance_c22_corrected_disclosure.json"],
        "supersedes_path": None,
    })

    # 7. guitar disclosure
    mid = "M-V4-SHOWCASE-1/cg-guitar-acceptance-c22-corrected-disclosure-c24"
    narr = (
        f"CG guitar acceptance corrected-disclosure: c15 OPT3 stands under corrected distance "
        f"semantics per invariants (a)/(b)/(c); composite-relative WINNER precedent scope-extension "
        f"from c9 CG-bass to CG-guitar still requires operator authority. Sibling (supersedes_path=null). "
        f"Disclosure sha256 {td['guitar_disclosure_sha'][:16]}…. c15 pinned byte-identical."
    )
    events.append({
        "event_id": event_id(mid, narr, 7),
        "milestone_id": mid,
        "status": "validated",
        "cycle": 24,
        "agent": "worker",
        "run_id": RUN_ID,
        "ts": TS,
        "confidence": {"level": "high", "rationale": "sibling disclosure per Track D wording; c15 anchor byte-identical", "assessor": "worker"},
        "narrative": narr,
        "artifacts": ["data/v4/deliveries/31a164f845f8e27e/cg_guitar_acceptance_c22_corrected_disclosure.json"],
        "supersedes_path": None,
    })

    # 8. amendment
    mid = "M-V4-CLOSE-1/c24-amendment"
    narr = (
        f"c24 closure completion report amendment appended (7 sections: c23-reversal, "
        f"Rome+PD RULED_OUT, WIG+DiscoA STILL_INDETERMINATE, escalation, CG drums+guitar OPT3 stands, "
        f"substantive advance status, ear-plausibility flag). Amendment sha256 {amend_sha[:16]}…. "
        f"c22 report + c23 amendment READ-ONLY byte-identical."
    )
    events.append({
        "event_id": event_id(mid, narr, 8),
        "milestone_id": mid,
        "status": "validated",
        "cycle": 24,
        "agent": "worker",
        "run_id": RUN_ID,
        "ts": TS,
        "confidence": {"level": "high", "rationale": "amendment doc landed with 7 mandated sections", "assessor": "worker"},
        "narrative": narr,
        "artifacts": ["docs/v4_closure_completion_report_c24_amendment.md"],
        "supersedes_path": None,
    })

    # 9. POR row
    mid = "_plan/register-c24-non-cg-bass-verdicts-revised-and-cg-drums-guitar-c22-corrected-disclosures"
    narr = (
        f"c24 POR registration: 4 revised non-CG bass verdicts (Rome+PD RULED_OUT above-floor; "
        f"WIG+DiscoA STILL_INDETERMINATE below-floor), 1 escalation JSON (blocked_on_operator=true), "
        f"2 CG drums+guitar corrected-disclosure siblings, 1 amendment doc, "
        f"3 housekeeping rows. supersedes_path in each of the 4 revised verdicts = "
        f"stale/<song>_bass_family_verdict.c23_scope_extension_disclosed.json (str per c14 lemma)."
    )
    events.append({
        "event_id": event_id(mid, narr, 9),
        "milestone_id": mid,
        "status": "validated",
        "cycle": 24,
        "agent": "worker",
        "run_id": RUN_ID,
        "ts": TS,
        "confidence": {"level": "high", "rationale": "POR row per c14+ pattern", "assessor": "worker"},
        "narrative": narr,
        "artifacts": ["plan_of_record.md"],
        "supersedes_path": None,
    })

    # 10. archive housekeeping
    mid = "_archive/cycle-24-scratch"
    narr = (
        "c24 scratch archival housekeeping. Emitter scripts (_emit_c24_track_a_d.py, "
        "_emit_c24_ledger_events.py) retained in-tree under scripts/sound_match/ for provenance "
        "per c14-c23 pattern; no workspace scratch to move to tools/stale/."
    )
    events.append({
        "event_id": event_id(mid, narr, 10),
        "milestone_id": mid,
        "status": "validated",
        "cycle": 24,
        "agent": "worker",
        "run_id": RUN_ID,
        "ts": TS,
        "confidence": {"level": "high", "rationale": "housekeeping per convention", "assessor": "worker"},
        "narrative": narr,
        "artifacts": [],
        "supersedes_path": None,
    })

    # 11. adopt-cycle-tests
    mid = "_infra/adopt-cycle24-tests"
    narr = (
        "c24 test-adoption housekeeping. No new test file this cycle; test coverage for c23 "
        "scripts + c24 Track A/D emitter deferred to c25 audit fill-in per c10-c22 pattern. "
        "Substantive verification of c24 discipline-reset via assert-based emitter + anchor "
        "preservation pre==post."
    )
    events.append({
        "event_id": event_id(mid, narr, 11),
        "milestone_id": mid,
        "status": "validated",
        "cycle": 24,
        "agent": "worker",
        "run_id": RUN_ID,
        "ts": TS,
        "confidence": {"level": "high", "rationale": "housekeeping per convention", "assessor": "worker"},
        "narrative": narr,
        "artifacts": [],
        "supersedes_path": None,
    })

    # 12. cycle-closed rollup
    mid = "_run/cycle_24_closed"
    narr = (
        "c24 CLOSED. Five tracks: (A) MUST-LAND — 4 non-CG bass verdicts reversed (Rome+PD "
        "SF2_RULED_OUT above the retained 0.40 distance-upper-bound floor; WIG+DiscoA "
        "STILL_INDETERMINATE below-floor pending stage-2 + operator authority); c23 artifacts "
        "preserved byte-identical to stale/; escalation JSON blocked_on_operator=true. "
        "(D) MUST-LAND — 2 CG drums+guitar corrected-disclosure siblings (c14/c15 OPT3 stands). "
        "(E) MUST-LAND — c24 amendment doc appended. (B) DEFERRED c25 — stage-2 WIG+DiscoA. "
        "(C) DEFERRED c25 — non-CG drums+guitar stage-1 sweeps. All 8 anchors byte-identical "
        "pre==post; c17 cg_ab_mix.wav sha 6e13e007…f9484b unchanged. NO SF2_CONFIRMED verdicts "
        "emitted this cycle. env_pin canonical 7-key. Operator ear = LANDS authority post-hoc."
    )
    events.append({
        "event_id": event_id(mid, narr, 12),
        "milestone_id": mid,
        "status": "validated",
        "cycle": 24,
        "agent": "worker",
        "run_id": RUN_ID,
        "ts": TS,
        "confidence": {"level": "high", "rationale": "cycle rollup per c8+ convention", "assessor": "worker"},
        "narrative": narr,
        "artifacts": [
            "data/v4/deliveries/31a164f845f8e27e/cycle24/track_a_d_closeout.json",
            "docs/v4_closure_completion_report_c24_amendment.md",
        ],
        "supersedes_path": None,
    })

    return events

def main():
    events = build_events()
    print(f"Built {len(events)} events")
    ok = 0
    for i, e in enumerate(events):
        payload = json.dumps(e, sort_keys=True, default=str)
        cmd = [
            "/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
            "--workspace", str(WS),
            "--event", payload,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WS))
        if r.returncode != 0:
            print(f"[{i+1}/{len(events)}] {e['milestone_id']}: FAIL")
            print("  stdout:", r.stdout[-500:])
            print("  stderr:", r.stderr[-500:])
        else:
            print(f"[{i+1}/{len(events)}] {e['milestone_id']}: OK")
            ok += 1
    print(f"\n{ok}/{len(events)} events landed")

if __name__ == "__main__":
    main()
