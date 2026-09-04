#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-04T01:00:00Z
# cycle: 14
# run_id: run-2026-09-04T003000Z
# agent: worker
# milestone: _run/cycle_14_closed
# ---
"""Emit cycle-14 ledger events (append to promise_ledger.jsonl).

Events emitted (in order):
 1. M-V4-SHOWCASE-1/cg-drums-acceptance-revised-c14 (Track 1 CRITICAL closure — OPT3)
 2. _plan/cg-drums-acceptance-revise-c14 (fork registration)
 3. _infra/agent-picks-selection-invariants-c14 (codification doc)
 4. M-V4-PROFILES-1/cg-piano-null-finding-grounded-c14 (Track 2)
 5. M-V4-PROFILES-1/cg-other-null-finding-c14 (Track 2 symmetry)
 6. M-V4-PROFILES-1/cg-guitar-stage2-launched (Track 3)
 7. _infra/adopt-cycle12-tests-c14-fillin (Track 4)
 8. _infra/adopt-cycle13-tests-c14-fillin (Track 4)
 9. _plan/register-c14-cg-drums-revise-guitar-stage2-null-grounding-sub-leaves
10. _archive/cycle-14-scratch
11. _infra/adopt-cycle14-tests
12. _run/cycle_14_closed (parent-rollup)

UUID5 event_id auto-derived via canonical-JSON content hash.
"""
from __future__ import annotations
import hashlib, json, sys, uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "promise_ledger.jsonl"
NS_LEDGER = uuid.uuid5(uuid.NAMESPACE_DNS, "music-gen.v4.ledger")


def sha256_hex(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def _event_id(body: dict) -> str:
    payload = {k: v for k, v in body.items() if k not in ("event_id", "ts")}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(NS_LEDGER, canonical))


def emit(events: list[dict]) -> None:
    with open(LEDGER, "a") as f:
        for ev in events:
            ev.setdefault("ts", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
            body = {k: ev[k] for k in ev if k != "event_id"}
            ev["event_id"] = _event_id(body)
            ordered = {k: ev[k] for k in sorted(ev.keys())}
            f.write(json.dumps(ordered, sort_keys=True) + "\n")


def main() -> int:
    run_id = "run-2026-09-04T003000Z"
    cy = 14
    common = {"agent": "worker", "cycle": cy, "run_id": run_id,
              "status": "validated",
              "confidence": {"level": "high",
                             "rationale": "on-disk artifacts sha-pinned in narrative",
                             "assessor": "worker"}}

    pinned_new = sha256_hex("data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json")
    pinned_stale = sha256_hex("data/v4/deliveries/31a164f845f8e27e/stale/cg_drums_pinned_profile.c13_opt1_below_floor.json")
    invariants_doc = sha256_hex("docs/agent_picks_selection_invariants.md")
    piano_new = sha256_hex("data/v4/profiles/31a164f845f8e27e/piano_null_finding.json")
    piano_stale = sha256_hex("data/v4/profiles/31a164f845f8e27e/stale/piano_null_finding.c13_ungrounded.json")
    other_new = sha256_hex("data/v4/profiles/31a164f845f8e27e/other_null_finding.json")
    piano_aud = sha256_hex("data/v4/profiles/31a164f845f8e27e/audibility/piano_stem_audibility.json")
    other_aud = sha256_hex("data/v4/profiles/31a164f845f8e27e/audibility/other_stem_audibility.json")
    measure_script = sha256_hex("scripts/sound_match/measure_stem_audibility.py")
    guitar_fit_script = sha256_hex("scripts/sound_match/fine_fit_sf2_guitar.py")
    guitar_launch = sha256_hex("scripts/sound_match/_launch_cg_guitar_stage2_c14.sh")
    test_family2 = sha256_hex("tests/test_sound_match_family2_drums.py")
    test_guitar = sha256_hex("tests/test_sound_match_guitar_sweep.py")

    events: list[dict] = []

    # (1) Track 1 — drums acceptance revised to OPT3
    events.append({**common,
        "milestone_id": "M-V4-SHOWCASE-1/cg-drums-acceptance-revised-c14",
        "narrative": (
            "c14 Track 1 CRITICAL closure: revised CG-drums acceptance from c13 OPT1 to OPT3 "
            "per c13 auditor guidance (CRITICAL #1 below-floor + CRITICAL #2 OPT3 misread) "
            "under c13-formalized agent-picks selection invariants. NEW pinned profile at "
            "data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json (sha "
            f"{pinned_new}). PRESERVED c13 OPT1 artifact byte-identical at "
            "data/v4/deliveries/31a164f845f8e27e/stale/cg_drums_pinned_profile.c13_opt1_below_floor.json "
            f"(sha {pinned_stale} == c13 delivery sha 1fcb2e4660058ff9...). OPT3 verbatim: "
            "'Refuse drums showcase — deliver CG A/B without drums recreation. Original htdemucs "
            "drums track used as-is in the mix.' drums_source_for_showcase = "
            "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/drums.wav "
            "(sha 34492c03f301b6eac3a75343b61244193889d039ae4ccce4c35cc44d568ac835 — operator-heard "
            "reference stem). c11 SF2_RULED_OUT + c12 FAMILY2_RULED_OUT verdicts preserved as terminal. "
            "M-V4-PROFILES-1 CG-drums cell marked NO_WINNER_DRUMS_ACCEPTED_AS_HTDEMUCS_STEM_SUBSTITUTION. "
            "supersedes_path pinned as str per c14 lemma. deliver_cg_ab_v4.py scaffold updated (additive) "
            "to route CG-drums through htdemucs stem substitution when acceptance_option==OPT3. "
            "Operator veto post-hoc via ear per FD-6."
        ),
        "artifacts": [
            "data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json",
            "data/v4/deliveries/31a164f845f8e27e/stale/cg_drums_pinned_profile.c13_opt1_below_floor.json",
            "scripts/sound_match/deliver_cg_ab_v4.py",
        ]})

    # (2) _plan/cg-drums-acceptance-revise-c14
    events.append({**common,
        "milestone_id": "_plan/cg-drums-acceptance-revise-c14",
        "narrative": (
            "c14 Track 1 fork registration. Chosen OPT3 (refuse drums showcase; htdemucs stem "
            "substitution); rejected OPT1 (violates retained 0.40 RULED_OUT floor + requires "
            "operator-scope extension of c9 composite-relative WINNER rule currently CG-bass ONLY) "
            "and OPT2 (above-floor but elevates emb_cos weight above 0.25; fresh-profile path "
            "deferred to c15 if operator overrides OPT3). c13 auditor CRITICAL #1 (below-floor) + "
            "CRITICAL #2 (OPT3 misread) CLOSED. c13 auditor MODERATE #1 (OPT2 rejection rationale "
            "technically incorrect) ACKNOWLEDGED; corrected in acceptance_fork.rejected. "
            "authority = campaign prompt anti-stall rule + operator directive 2026-09-03 part (2) + "
            "c13-formalized agent-picks selection invariants (docs/agent_picks_selection_invariants.md). "
            "supersedes_path pinned as str per c14 lemma."
        ),
        "supersedes_path": "data/v4/profiles/31a164f845f8e27e/_manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json",
        "artifacts": ["data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json"]})

    # (3) _infra/agent-picks-selection-invariants-c14
    events.append({**common,
        "milestone_id": "_infra/agent-picks-selection-invariants-c14",
        "narrative": (
            "c14 codification of three-point agent-picks selection invariants per c13 auditor "
            "recommendation: (a) prefer no operator-scope extension; (b) prefer above-floor over "
            "below-floor; (c) do not reject an option based on misreading its own definition. "
            f"docs/agent_picks_selection_invariants.md (sha {invariants_doc}). Retroactively "
            "compliant with c9 CG-bass fork. Non-compliant on all three at c13 CG-drums fork; "
            "formal reason for the c14 Track 1 revise to OPT3. Referenced by future "
            "acceptance-fork events under _manager/*acceptance-fork* going forward."
        ),
        "artifacts": ["docs/agent_picks_selection_invariants.md"]})

    # (4) Track 2 — piano grounded
    events.append({**common,
        "milestone_id": "M-V4-PROFILES-1/cg-piano-null-finding-grounded-c14",
        "narrative": (
            "c14 Track 2: piano NULL finding GROUNDED per c13 auditor MODERATE #2. "
            "Author scripts/sound_match/measure_stem_audibility.py (sha "
            f"{measure_script}) measuring rms_dbfs/peak_dbfs/lufs_i with silence floor -60 dB. "
            "Piano audibility on data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/piano.wav: "
            "rms_dbfs=-81.53, peak_dbfs=-55.82, lufs_i=None (pyloudnorm returned -inf → RMS fallback), "
            "verdict_audible=False. New verdict: "
            "PIANO_NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE. c13 ungrounded artifact "
            f"preserved byte-identical at stale/piano_null_finding.c13_ungrounded.json (sha {piano_stale}). "
            f"NEW: data/v4/profiles/31a164f845f8e27e/piano_null_finding.json (sha {piano_new}). "
            f"Audibility sidecar: data/v4/profiles/31a164f845f8e27e/audibility/piano_stem_audibility.json (sha {piano_aud}). "
            "supersedes_path pinned as str per c14 lemma. Cosmetic MINOR #3 fixed: same_song_siblings "
            "key snake-case."
        ),
        "supersedes_path": "data/v4/profiles/31a164f845f8e27e/stale/piano_null_finding.c13_ungrounded.json",
        "artifacts": [
            "scripts/sound_match/measure_stem_audibility.py",
            "data/v4/profiles/31a164f845f8e27e/piano_null_finding.json",
            "data/v4/profiles/31a164f845f8e27e/stale/piano_null_finding.c13_ungrounded.json",
            "data/v4/profiles/31a164f845f8e27e/audibility/piano_stem_audibility.json",
        ]})

    # (5) Track 2 — other NULL symmetry
    events.append({**common,
        "milestone_id": "M-V4-PROFILES-1/cg-other-null-finding-c14",
        "narrative": (
            "c14 Track 2 symmetry per c13 auditor MINOR #1: other-residual NULL finding emitted "
            "mirroring piano artifact shape. Other-residual (merged.mid track 4, 0 note_on) "
            "audibility on data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/other.wav: "
            "rms_dbfs=-81.73, peak_dbfs=-55.82, lufs_i=None (fallback), verdict_audible=False. "
            "Verdict OTHER_NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE. NEW: "
            f"data/v4/profiles/31a164f845f8e27e/other_null_finding.json (sha {other_new}). "
            f"Audibility sidecar (sha {other_aud}). Same-song siblings block mirrors piano's "
            "shape. Showcase mix uses original htdemucs other stem (empty MIDI → silent per-track "
            "per v3-spine default). Not blocking on M-V4-SHOWCASE-1."
        ),
        "artifacts": [
            "data/v4/profiles/31a164f845f8e27e/other_null_finding.json",
            "data/v4/profiles/31a164f845f8e27e/audibility/other_stem_audibility.json",
        ]})

    # (6) Track 3 — guitar stage-2 launched
    events.append({**common,
        "milestone_id": "M-V4-PROFILES-1/cg-guitar-stage2-launched",
        "narrative": (
            "c14 Track 3 substantive advance: CG guitar stage-2 fine fit LAUNCHED DETACHED. "
            f"scripts/sound_match/fine_fit_sf2_guitar.py (sha {guitar_fit_script}) authored as "
            "sibling to c3 fine_fit_sf2_v2.py (READ-ONLY) + c11 fine_fit_sf2_drums.py (READ-ONLY). "
            "Grid: c13 stage-1 top-5 programs [24 Nylon, 27 Rock (source-of-truth, rank 2 already "
            "in top-5 → no separate control cell), 28 Jazz, 26 EP-clean, 25 Steel] × gain {0.5, 1.0, "
            "1.5} × reverb {0.0, 0.3, 0.7} × post {none, EQ_only, compressor_only, EQ_and_compressor} "
            "= 180 cells. EQ v2 (12-band iirpeak Q=1.4 geomspace 20-20kHz, no zero-mean); mandatory "
            "pyloudnorm LUFS-I to -18 with RMS fallback logged; c2 compressor unchanged. Storage "
            "hygiene --score-and-delete --keep-top 3 --max-audio-mb 500. Detached-launch helper "
            f"scripts/sound_match/_launch_cg_guitar_stage2_c14.sh (sha {guitar_launch}) — "
            "nohup+setsid+logfile pattern per c8 policy. PID 26452, log "
            "data/v4/logs/cg_guitar_stage2_c14.log. Reference stem "
            "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav "
            "(sha bc01ff1f...). Guitar excerpt "
            "data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage1/guitar_excerpt.mid (391 note_on, "
            "channel-0 remapped per c13 anchor). env_pin_sha256 will differ from c11 drums by design "
            "(instrument axis in env_pin payload). Stage-2 completion + profile emission + family "
            "verdict roll to c15 first-act if not in-cycle. Per FD-16(c) sf2 replay proof for CG "
            "already scoped by c11 anchor (832868d0...) covering all sf2 profiles on CG."
        ),
        "artifacts": [
            "scripts/sound_match/fine_fit_sf2_guitar.py",
            "scripts/sound_match/_launch_cg_guitar_stage2_c14.sh",
            "data/v4/logs/cg_guitar_stage2_c14.log",
            "data/v4/logs/cg_guitar_stage2_c14.pid",
        ]})

    # (7) Track 4 — family2 drums tests
    events.append({**common,
        "milestone_id": "_infra/adopt-cycle12-tests-c14-fillin",
        "narrative": (
            "c14 Track 4: closes c12 test debt (deferred c10 → c11 → c12 → c13). "
            f"tests/test_sound_match_family2_drums.py (sha {test_family2}) — 8/8 tests PASS: "
            "regression pin on family-2 drums render sha "
            "69a76c5b4498972d1cb878da94e645c8c341675b113cc4ca315435f6bb16ca00; builder anchor "
            "byte-identity within test run; FAMILY2_RULED_OUT verdict enum; AST-grep for PRNG absence "
            "and sidecar_nonfactor absence; python3 shebang guard; env pin declarations. "
            "Anchor c12 family2_stem_sampled_drums_builder.py READ-ONLY (on-disk sha "
            "295e5501b9e4e01691eaaf2065596465e5b75c5e17a871118252ebc9749f53eb — differs from brief-"
            "hardcoded 'eaa8fb6c…' which is stale/transcription-error; on-disk sha is authoritative "
            "per FD-1)."
        ),
        "artifacts": ["tests/test_sound_match_family2_drums.py"]})

    # (8) Track 4 — guitar sweep tests
    events.append({**common,
        "milestone_id": "_infra/adopt-cycle13-tests-c14-fillin",
        "narrative": (
            "c14 Track 4: closes c13 test debt. "
            f"tests/test_sound_match_guitar_sweep.py (sha {test_guitar}) — 10/10 tests PASS: "
            "regression pin on c13 leaderboard sha 0ee5e767edff8dcb2864d5466f331a4ffacca7f5fa4b64949684dcb1db052bfc "
            "+ run_manifest sha 5a3cf11d1241228823039c0bd14d7e8e890edd043963e868a38092f9b355ac0f "
            "+ coarse sweep script anchor sha 9ddf692f0a903875bbae537bebba6265649b4bfb4dec6b979084a4cb42e96055 "
            "(all READ-ONLY, verified byte-identical); 8/8 distinct render SHAs asserted; program 24 "
            "Nylon top-1 asserted; program 27 Rock rank 2 asserted; spread ratio ≥ 2.79 (Rung-3 spread "
            "PASS documented); AST-grep for PRNG + sidecar_nonfactor absence; interpreter guard; env pins "
            "in run_manifest."
        ),
        "artifacts": ["tests/test_sound_match_guitar_sweep.py"]})

    # (9) POR register
    events.append({**common,
        "milestone_id": "_plan/register-c14-cg-drums-revise-guitar-stage2-null-grounding-sub-leaves",
        "narrative": (
            "c14 plan-of-record registration adds rows for the new c14 milestone events: "
            "M-V4-SHOWCASE-1/cg-drums-acceptance-revised-c14, "
            "M-V4-PROFILES-1/cg-piano-null-finding-grounded-c14, "
            "M-V4-PROFILES-1/cg-other-null-finding-c14, "
            "M-V4-PROFILES-1/cg-guitar-stage2-launched, "
            "_infra/agent-picks-selection-invariants-c14, "
            "_infra/adopt-cycle12-tests-c14-fillin, "
            "_infra/adopt-cycle13-tests-c14-fillin, "
            "plus housekeeping rows. Closes promise_check drift for these ids."
        ),
        "artifacts": ["plan_of_record.md"]})

    # (10) housekeeping — scratch archival
    events.append({**common,
        "milestone_id": "_archive/cycle-14-scratch",
        "narrative": (
            "c14 scratch archival. Session-scoped scratchpad preserved under harness-managed dir; "
            "no in-workspace scratch this cycle — all c14 code lands under scripts/sound_match/. "
            "Log file data/v4/logs/cg_guitar_stage2_c14.log preserved for provenance."
        ),
        "artifacts": []})

    # (11) housekeeping — test adoption
    events.append({**common,
        "milestone_id": "_infra/adopt-cycle14-tests",
        "narrative": (
            "c14 test-adoption housekeeping. Closes cross-cycle test-debt accounting; carries the "
            "two new test files landed under Track 4 (test_sound_match_family2_drums.py + "
            "test_sound_match_guitar_sweep.py). c15+ will fill in coverage for "
            "fine_fit_sf2_guitar.py + measure_stem_audibility.py per c14 auditor recommendation."
        ),
        "artifacts": [
            "tests/test_sound_match_family2_drums.py",
            "tests/test_sound_match_guitar_sweep.py",
        ]})

    # (12) _run/cycle_14_closed rollup
    events.append({**common,
        "milestone_id": "_run/cycle_14_closed",
        "narrative": (
            "c14 CLOSED. Tracks landed: (1) CG-drums acceptance revised to OPT3 (CRITICAL closure "
            "of c13 audit); (2) piano+other NULL findings GROUNDED with audibility measurements "
            "(both stems inaudible: rms_dbfs ~-81 dB below -60 dB silence floor); (3) CG guitar "
            "stage-2 fine fit LAUNCHED DETACHED (PID 26452, 180 cells); (4) accumulated test-debt "
            "cleanup landed (18/18 tests green across two files); (5) POR + housekeeping. "
            "M-V4-SHOWCASE-1 status: blocked_on_remaining_cg_instruments (drums resolved via OPT3 "
            "htdemucs substitution; piano/other NULL grounded; guitar stage-2 in-progress; not "
            "blocked on operator). Operator ear remains LANDS authority post-hoc per FD-6."
        ),
        "artifacts": []})

    emit(events)
    print(f"emitted {len(events)} c14 events")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
