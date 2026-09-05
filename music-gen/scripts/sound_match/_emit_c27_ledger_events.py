#!/usr/bin/python3
"""c27 ledger-event emitter (one-shot).

Track A: canonical sweep-hygiene module + tests + POR one-liner + driver-
adoption plan for c28.
Track B: honest verification of c26 Track A on-disk landing (INCOMPLETE:
neither WIG nor Disco A downstream emissions exist; WIG stage-2 leaderboard
present, Disco A stage-2 leaderboard missing).

Retained in-tree per c14+ housekeeping convention.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN_ID = "run-2026-09-05T020000Z"
CYCLE = 27
AGENT = "worker"
NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _sha256_hex(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _event_id(milestone_id: str, ts: str, narrative_head: str) -> str:
    payload = f"{milestone_id}|{ts}|{narrative_head[:80]}"
    return str(uuid.uuid5(NAMESPACE, payload))


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build(
    milestone_id: str,
    status: str,
    confidence_level: str,
    narrative: str,
    artifacts: list[str],
    supersedes_path: str | None = None,
    ts: str | None = None,
) -> dict:
    ts = ts or _now_iso()
    ev = {
        "event_id": _event_id(milestone_id, ts, narrative),
        "ts": ts,
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": AGENT,
        "milestone_id": milestone_id,
        "status": status,
        "confidence": {
            "level": confidence_level,
            "rationale": "c27 mandatory Track A/B execution + honest first-class findings per FD-1",
            "assessor": AGENT,
        },
        "narrative": narrative,
        "artifacts": artifacts,
    }
    if supersedes_path is not None:
        ev["supersedes_path"] = supersedes_path  # str per c14 lemma
    return ev


def _append(event: dict) -> None:
    payload = json.dumps(event, ensure_ascii=False)
    r = subprocess.run(
        [
            "python3", "-m", "long_exposure.tools.ledger_append",
            "--workspace", str(REPO),
            "--event", payload,
        ],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"ledger_append failed: {r.stderr}\nstdout={r.stdout}")
    sys.stdout.write(f"  OK {event['milestone_id']}\n")


def main() -> int:
    # Artifact SHAs
    mod_p = REPO / "scripts/sound_match/_sweep_hygiene_c27.py"
    test_p = REPO / "tests/test_sweep_hygiene_c27.py"
    plan_p = REPO / "docs/sweep_hygiene_c27_driver_adoption_plan.md"
    verify_p = REPO / "data/v4/c27_track_b_c26_landing_verification.json"
    por_p = REPO / "plan_of_record.md"
    mod_sha = _sha256_hex(mod_p)
    test_sha = _sha256_hex(test_p)
    plan_sha = _sha256_hex(plan_p)
    verify_sha = _sha256_hex(verify_p)
    por_sha = _sha256_hex(por_p)

    events = []

    # 1. Track A: canonical hygiene module (substantive)
    events.append(_build(
        milestone_id="_infra/sweep-hygiene-c27-canonical-module",
        status="validated",
        confidence_level="high",
        narrative=(
            "c27 Track A MANDATORY landed. Canonical hygiene module "
            f"scripts/sound_match/_sweep_hygiene_c27.py (sha {mod_sha[:32]}) exports "
            "RunningTopK bounded-heap class + df_guard_before_stage(prune@85%, "
            "abort@90%) + _prune_stale_sweep_audio(age gate=60s) + prune_after_pin() "
            "per OPERATOR DIRECTIVE 2026-09-05. Fixes the c26 batch-render-full-grid "
            "failure mode where drivers accumulated 432 (WIG) + 254 (Disco A) unscored "
            "WAVs on disk. Test suite tests/test_sweep_hygiene_c27.py "
            f"(sha {test_sha[:32]}) 10/10 PASS: per-candidate delete bounded ≤keep-top "
            "(test_01), running-heap displacement rule (test_02), post-pin cleanup "
            "(test_03), df guard prune @ 85% (test_04), df guard abort @ 90% FD-1 halt "
            "(test_05), NaN composite reject (test_06), age-gate on stale audio (test_07), "
            "AST discipline (tests 08-10: interpreter guard + no PRNG + no forbidden "
            "attrs). Driver integration deferred to c28 first-sweep-launch per c27 "
            "brief Tracks C/D deferral; c26 anchor drivers preserved READ-ONLY this "
            "cycle. Cross-cycle test total: c16 28 + c17 6 + c18 12 + c19 7 + c20 1 "
            "+ c26 21 + c27 10 = 85 (≥84 by extension of c26 74-gate)."
        ),
        artifacts=[
            f"scripts/sound_match/_sweep_hygiene_c27.py sha256={mod_sha}",
            f"tests/test_sweep_hygiene_c27.py sha256={test_sha}",
        ],
    ))

    # 2. Track A: POR one-liner + operator directive record
    events.append(_build(
        milestone_id="_plan/sweep-hygiene-fix-c27-procedure",
        status="validated",
        confidence_level="high",
        narrative=(
            "POR one-liner append per OPERATOR DIRECTIVE 2026-09-05 verbatim: "
            "'PROC 2026-09-05 SWEEP-HYGIENE FIX: render→score→delete per candidate; "
            "running top-5 audio only; delete all remaining sweep audio after each pin; "
            "df ≥85% → prune first; batch-render-full-grid BANNED.' Appended immediately "
            "after existing 'PROC 2026-09-03 SWEEP-STORAGE HYGIENE: …' line at "
            f"plan_of_record.md (post-write sha256={por_sha[:32]}). Operator directive "
            "landed as procedure fix, not a finding — one line in POR, then continue "
            "reopened M-V4-PROFILES work under the fixed procedure. c26 batch-render "
            "attempt on WIG (432 accumulated) + Disco A (254 accumulated) hit 90% disk "
            "usage before scoring; operator pruned scored renders + tombstones; c27 "
            "hardens the pattern architecturally."
        ),
        artifacts=[f"plan_of_record.md sha256={por_sha}"],
    ))

    # 3. Track A: driver-adoption plan doc (c28 pre-registration)
    events.append(_build(
        milestone_id="_infra/sweep-hygiene-c27-driver-adoption-plan",
        status="in-progress",
        confidence_level="high",
        narrative=(
            f"Driver-adoption plan doc docs/sweep_hygiene_c27_driver_adoption_plan.md "
            f"(sha {plan_sha[:32]}) pre-registers c28 mechanical integration of the "
            "c27 canonical hygiene module into six sweep drivers (coarse_sweep_sf2 + "
            "coarse_sweep_sf2_drums + coarse_sweep_sf2_guitar + fine_fit_sf2_v2 + "
            "fine_fit_sf2_drums + fine_fit_sf2_guitar). Documents 6-step reference "
            "integration shape (import + flag + df guard + per-cell hook + post-pin "
            "cleanup + legacy deprecation), SHA-drift disclosure norm per invariant (d), "
            "and per-driver regression-test gate. Integration is c28 scope because no "
            "sweep launches this cycle (Track C/D deferred, disk at 87% still above "
            "85% prune threshold at cycle open). Anchors preserved: 4 driver SHAs "
            "byte-identical pre==post; legacy --score-and-delete flag retained for "
            "backwards-compat regression, replaced by --score-and-delete-per-candidate "
            "as new default at c28+."
        ),
        artifacts=[f"docs/sweep_hygiene_c27_driver_adoption_plan.md sha256={plan_sha}"],
    ))

    # 4. Track B verification (MANDATORY)
    events.append(_build(
        milestone_id="_infra/verify-c26-track-a-landing-c27",
        status="action_required",
        confidence_level="high",
        narrative=(
            "c27 Track B MANDATORY: honest on-disk verification of c26 Track A "
            "claim. Fresh python3+stat query on both non-CG focus songs: WIG "
            "(252eb21ce7df7328) — stage-2 leaderboard on disk (216 rows) + "
            "SWEEP_WAVS_PRUNED.txt tombstone (operator prune); NO bass.json, NO "
            "bass.replay_proof.json, NO bass_family_verdict.json. Disco A "
            "(cdd2717e52820ff6) — stage-2 leaderboard MISSING (sweep interrupted "
            "mid-run per c26 handoff; ~166 unscored render subdirs on disk); NO "
            "downstream emissions of any kind. c23 predecessor verdicts remain on "
            "disk for both songs, both STILL_INDETERMINATE — SF2_CONFIRMED does "
            "NOT appear anywhere. c26 rollup claim (Track A landed) is factually "
            "incorrect at the delivery-emission layer; c26 emitter script exists "
            f"but was never executed. Verification JSON at data/v4/c27_track_b_c26"
            f"_landing_verification.json (sha {verify_sha[:32]}) records per-song "
            "landing status, invariant compliance (SF2_CONFIRMED forbidden — "
            "UPHELD by absence of any per-song verdict), and c28 next actions. "
            "Manager escalation _manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-"
            "policy preserved unchanged (blocked_on_operator=true)."
        ),
        artifacts=[
            f"data/v4/c27_track_b_c26_landing_verification.json sha256={verify_sha}",
        ],
    ))

    # 5. POR registration for c27 sub-leaves
    events.append(_build(
        milestone_id="_plan/register-c27-sweep-hygiene-and-track-b-sub-leaves",
        status="validated",
        confidence_level="high",
        narrative=(
            "c27 POR row registers 4 new c27 milestone_ids landed this cycle: "
            "_infra/sweep-hygiene-c27-canonical-module, "
            "_plan/sweep-hygiene-fix-c27-procedure, "
            "_infra/sweep-hygiene-c27-driver-adoption-plan, "
            "_infra/verify-c26-track-a-landing-c27; plus 3 housekeeping rows "
            "(_run/cycle_27_closed, _archive/cycle-27-scratch, "
            "_infra/adopt-cycle27-tests) per c8+ tail convention. Track C (Rome + "
            "Peach Dream bass stage-2) and Track D (non-CG drums stage-1) HONESTLY "
            "DEFERRED to c28+ per brief RECOMMENDED gates + wall-time budget "
            "compressed by Track A architectural work. Track E (completion report "
            "second pass) BOOKKEEPING DEFERRED to c28+. Non-CG bass acceptance-"
            "policy escalation preserved unchanged. Closes promise_check drift for "
            "these ids."
        ),
        artifacts=[],
    ))

    # 6. Housekeeping tail: _run/cycle_27_closed
    events.append(_build(
        milestone_id="_run/cycle_27_closed",
        status="validated",
        confidence_level="high",
        narrative=(
            "c27 CLOSED. Track A MANDATORY landed: canonical hygiene module "
            "_sweep_hygiene_c27.py + 10/10 tests + POR one-liner + driver-adoption "
            "plan doc for c28. Track B MANDATORY landed as ACTION_REQUIRED: c26 "
            "Track A downstream emissions NOT on disk (INCOMPLETE_LANDING for WIG, "
            "SWEEP_INTERRUPTED for Disco A); c26 rollup claim contradicted by "
            "honest fresh-disk verification per FD-1. Track C (Rome + Peach Dream "
            "bass stage-2) DEFERRED to c28+ — no new sweep launched this cycle "
            "(disk at 87% > 85% prune threshold, and driver integration deferred to "
            "c28 per brief). Track D (non-CG drums stage-1) DEFERRED to c28+. "
            "Track E (completion report v2) BOOKKEEPING DEFERRED to c28+. "
            "SF2_CONFIRMED forbidden on non-CG bass: UPHELD (no such verdict "
            "emitted or superseded this cycle). NO wait-on-operator memo (BANNED "
            "per operator directive 2026-09-03 part 2). Operator ear remains LANDS "
            "authority post-hoc per FD-6. Manager escalation _manager/M-V4-SHOWCASE"
            "-1-non-cg-bass-acceptance-policy preserved unchanged "
            "(blocked_on_operator=true). Anchors preserved: 6 sweep-driver "
            "scripts + all c26/c23 verdict JSONs + cg_ab_mix.wav + 5 pinned "
            "profiles byte-identical pre==post (no edits to any anchor file this "
            "cycle). env_pin_sha256 canonical 7-key subset "
            "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca "
            "unchanged."
        ),
        artifacts=[],
    ))

    # 7. Housekeeping: _archive/cycle-27-scratch
    events.append(_build(
        milestone_id="_archive/cycle-27-scratch",
        status="validated",
        confidence_level="high",
        narrative=(
            "c27 scratch archival housekeeping. One-shot emitter "
            "scripts/sound_match/_emit_c27_ledger_events.py retained in tree for "
            "provenance per c14+ pattern. No workspace scratch to archive to "
            "tools/stale/ this cycle — all substantive code lands under "
            "scripts/sound_match/ + tests/ + docs/ + data/v4/."
        ),
        artifacts=[],
    ))

    # 8. Housekeeping: _infra/adopt-cycle27-tests
    events.append(_build(
        milestone_id="_infra/adopt-cycle27-tests",
        status="validated",
        confidence_level="high",
        narrative=(
            "c27 test-adoption housekeeping. Adopted one new test file: "
            f"tests/test_sweep_hygiene_c27.py (sha {test_sha[:32]}) — 10/10 PASS "
            "under PYTHONPATH=. /usr/bin/python3 tests/test_sweep_hygiene_c27.py. "
            "Cross-cycle sound-match + hygiene test total: c16 28 + c17 6 + c18 12 "
            "+ c19 7 + c20 1 + c26 21 + c27 10 = 85 (≥84 by extension of c26 74-gate)."
        ),
        artifacts=[f"tests/test_sweep_hygiene_c27.py sha256={test_sha}"],
    ))

    print(f"emitting {len(events)} c27 ledger events...")
    for ev in events:
        _append(ev)
    print(f"OK: {len(events)} events landed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
