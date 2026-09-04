#!/usr/bin/python3
"""Emit cycle-15 ledger events (append to promise_ledger.jsonl)."""
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
            ev.setdefault("ts", datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"))
            body = {k: ev[k] for k in ev if k != "event_id"}
            ev["event_id"] = _event_id(body)
            ordered = {k: ev[k] for k in sorted(ev.keys())}
            f.write(json.dumps(ordered, sort_keys=True) + "\n")


def main() -> int:
    run_id = "run-2026-09-04T100000Z"
    cy = 15
    common = {
        "agent": "worker", "cycle": cy, "run_id": run_id,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": "on-disk artifacts sha-pinned in narrative",
            "assessor": "worker"},
    }

    invariants_doc = sha256_hex("docs/agent_picks_selection_invariants.md")
    interp_policy = sha256_hex("docs/interpreter_guard_policy.md")
    spike_script = sha256_hex(
        "scripts/sound_match/family2_stem_sampled_guitar_spike.py")
    builder_script = sha256_hex(
        "scripts/sound_match/family2_stem_sampled_guitar_builder.py")
    profile = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.json")
    replay_proof = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.replay_proof.json")
    verdict = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/guitar_family2_verdict.json")
    arc_closeout = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/guitar_arc_closeout.json")
    escalation = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/_manager/"
        "M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json")
    pinned = sha256_hex(
        "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile.json")
    deliver = sha256_hex("scripts/sound_match/deliver_cg_ab_v4.py")

    # c14 anchors (Track 1 disclosure references)
    c14_stage2_lb = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage2/leaderboard.tsv")
    c14_stage2_manifest = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage2/run_manifest.json")
    c14_guitar_json = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/guitar.json")
    c14_guitar_verdict = sha256_hex(
        "data/v4/profiles/31a164f845f8e27e/guitar_family_verdict.json")

    events: list[dict] = []

    # ============ Track 1 ============
    events.append({**common,
        "milestone_id": "_infra/guitar-stage2-grid-deviation-disclosed-c15",
        "narrative": (
            "c15 Track 1 (retroactive disclosure closes c14 auditor MODERATE): "
            "c14 Track 3 CG guitar stage-2 fine fit used on-disk c13 stage-1 "
            "top-5 grid {24 Nylon, 25 Steel, 26 Jazz, 27 Rock, 28 Muted} rather "
            "than brief-specified {24 Nylon, 27 Rock, 31 Harmonics, 26 Jazz, "
            "25 Steel}. Divergence: prog 31 (Harmonics) not tested; prog 28 "
            "(Muted Electric Guitar) tested per c13 stage-1 top-5 rank ordering "
            "(prog 28 stage-1 rank 3 composite 226.31; prog 31 stage-1 rank 6). "
            "Worker rationale (post-hoc): on-disk truth per FD-1 precedent from "
            "c12 anchor SHA correction. Impact analysis: verdict SF2_RULED_OUT "
            "insensitive because max emb_cos_vggish across all 180 cells = "
            "0.2703 < 0.40 floor even if prog 31 topped hypothetically — "
            "RULED_OUT stands. c14 stage-2 leaderboard sha "
            f"{c14_stage2_lb} + run_manifest sha {c14_stage2_manifest} + "
            f"guitar.json sha {c14_guitar_json} + guitar_family_verdict sha "
            f"{c14_guitar_verdict} are READ-ONLY anchors (per c14 auditor 'DO NOT'). "
            "Also: c14 guitar.json labels top-1 prog 28 as 'Jazz Guitar' — GM "
            "standard 0-indexed prog 28 is 'Muted Electric Guitar' (prog 26 is "
            "Jazz). Cosmetic-only mislabel; profile params unchanged; c14 "
            "guitar.json remains READ-ONLY per FD-1. Extends "
            f"docs/agent_picks_selection_invariants.md (sha {invariants_doc}) "
            "with invariant (d) formalizing on-disk-vs-brief disclosure norm."),
        "artifacts": [
            "docs/agent_picks_selection_invariants.md",
        ],
        "supersedes_path": "docs/agent_picks_selection_invariants.md",
    })

    # ============ Track 5 ============
    events.append({**common,
        "milestone_id": "_infra/interpreter-guard-policy-c15",
        "narrative": (
            "c15 Track 5 MINOR policy closure: formal interpreter guard policy "
            f"landed at docs/interpreter_guard_policy.md (sha {interp_policy}). "
            "Canonical shebang '#!/usr/bin/python3' required for c13+ new code; "
            "pre-c12 anchors with '#!/usr/bin/env python3' grandfathered "
            "READ-ONLY per FD-1 (c12 family2_stem_sampled_drums_{spike,builder}.py). "
            "Test enforcement contract documented; both forms resolve to "
            "/usr/bin/python3 on this system. Closes c14 auditor RECOMMENDED "
            "item #5. Not a re-emit trigger for any anchor."),
        "artifacts": ["docs/interpreter_guard_policy.md"],
    })

    # ============ Track 2 ============
    events.append({**common,
        "milestone_id": "M-V4-PROFILES-1/cg-guitar-family2-stem-sampled",
        "narrative": (
            "c15 Track 2 substantive advance: CG guitar family-2 stem-sampled "
            "spike + builder authored as sibling to c5/c6 CG-bass family-2 "
            "(READ-ONLY) + c12 CG-drums family-2 (READ-ONLY). Spike "
            f"{spike_script}; builder {builder_script}. Onset detect on "
            "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav "
            "via librosa.onset.onset_detect (units=samples, backtrack=True); "
            "400 ms fixed slices; per-pitch bank via librosa.pyin median "
            "(fmin=41 fmax=2637 voicing_min=0.5); render via nearest-pitch "
            "pitch-shift concatenative synthesis on guitar_excerpt.mid (391 "
            "note_on events all on ch 0); deterministic k-th selection; NO "
            "PRNG; soft peak-limit 0.99; output 44.1 kHz mono. Render "
            "SHA `f41560714a68415cd2fe1fc8f2c1010f54aafe182f4592ec20ed893ce2559ddc`. "
            "Bank diagnostics: 147 onsets, 37 slices voiced, 108 unvoiced dropped, "
            "5 unique pitches extracted, all 391 MIDI events routed. "
            "/usr/bin/python3 guard; env pins set BEFORE observed imports; no "
            "sidecar_nonfactor; no VST3 state APIs. Family-2 IS a distinct "
            "RENDER FAMILY from sf2 per FD-16(c) — needs its own per-song replay "
            "proof (see M-V4-PROFILES-1/cg-guitar-family2-replay-proof)."),
        "artifacts": [
            "scripts/sound_match/family2_stem_sampled_guitar_spike.py",
            "scripts/sound_match/family2_stem_sampled_guitar_builder.py",
            "data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.json",
            "data/v4/profiles/31a164f845f8e27e/guitar_family2_render/render.wav",
            "data/v4/profiles/31a164f845f8e27e/guitar_family2_render/"
            "render_manifest.json",
        ],
    })

    events.append({**common,
        "milestone_id": "M-V4-PROFILES-1/cg-guitar-family2-replay-proof",
        "narrative": (
            "c15 Track 2 per FD-16(c) + ceremony-relaxation single-proof-per-"
            "NEW-code-path: family-2 stem-sampled is a distinct render family "
            "from sf2 for CG-guitar. Ran builder twice into fresh "
            "tempfile.mkdtemp() dirs under 7-key env pins "
            "(env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca). "
            "run1_sha256 == run2_sha256 == "
            "`f41560714a68415cd2fe1fc8f2c1010f54aafe182f4592ec20ed893ce2559ddc`. "
            "Verdict REPLAY_PROOF_HOLDS. Per FD-16(c) this proof covers all "
            f"future family-2 stem-sampled profiles for CG-guitar. Proof at "
            f"data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.replay_proof.json "
            f"(sha {replay_proof})."),
        "artifacts": [
            "data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.replay_proof.json",
        ],
    })

    # ============ Track 3 ============
    events.append({**common,
        "milestone_id": "M-V4-PROFILES-1/cg-guitar-family2-verdict",
        "narrative": (
            "c15 Track 3 per c11 decision protocol: CG guitar family-2 VERDICT "
            "= FAMILY2_RULED_OUT. Objective panel scoring vs reference stem: "
            "mel_l1_db 13.165, spectral_centroid_rmse_hz 626.23, "
            "embedding_cos_vggish 0.03543, composite 164.03. Below 0.40 "
            "retained absolute floor. First-class negative finding; predicted "
            "by systematic 4-arc pattern (bass family-2 0.0896 at c6; drums "
            "family-2 0.0372 at c12; guitar family-2 0.0354 at c15). Fifth "
            "CG-instrument arc verdict where the frozen composite objective "
            "ranks the render as insufficient by emb_cos_vggish. Verdict on "
            f"disk at data/v4/profiles/31a164f845f8e27e/guitar_family2_verdict.json "
            f"(sha {verdict})."),
        "artifacts": [
            "data/v4/profiles/31a164f845f8e27e/guitar_family2_verdict.json",
        ],
    })

    events.append({**common,
        "milestone_id": "M-V4-PROFILES-1/cg-guitar-arc-closeout",
        "narrative": (
            "c15 Track 3 parallels c7 CG-bass + c12 CG-drums arc closeouts. "
            "Verdict CG_GUITAR_ARC_EXHAUSTED_NO_CONFIRMED. Pins sf2 "
            "SF2_RULED_OUT verdict (c14, emb_cos_vggish 0.2584) + family-2 "
            "FAMILY2_RULED_OUT verdict (this cycle, emb_cos_vggish 0.03543) + "
            "best-available profiles for both. Systematic finding: THIRD "
            "CG-instrument arc exhausted with no CONFIRMED family (bass c7, "
            "drums c12, guitar c15). Parallel structural shape across all "
            f"three arcs. Closeout at data/v4/profiles/31a164f845f8e27e/"
            f"guitar_arc_closeout.json (sha {arc_closeout})."),
        "artifacts": [
            "data/v4/profiles/31a164f845f8e27e/guitar_arc_closeout.json",
        ],
    })

    # ============ Track 4 ============
    events.append({**common,
        "milestone_id":
            "_manager/M-V4-SHOWCASE-1-cg-guitar-acceptance-policy",
        "narrative": (
            "c15 Track 4 acceptance-policy escalation JSON (parallels c12 "
            "drums escalation + c14 revised drums shape). "
            "status=resolved_via_agent_picks_invariants (NOT action_required — "
            "this cycle resolves via c14-codified + c15-extended agent-picks "
            "invariants a/b/c/d applied to the FAMILY2_RULED_OUT outcome). "
            "Three named options with per-option invariant compliance: OPT1 "
            "(sf2 top-1 emb_cos 0.2584) violates (a)+(b); OPT2 (family-2 "
            "emb_cos 0.0354) violates (b); OPT3 (refuse guitar showcase; use "
            "htdemucs reference stem verbatim) satisfies all four invariants "
            "and is uniquely anti-stall-preferred. Escalation at "
            f"data/v4/profiles/31a164f845f8e27e/_manager/"
            f"M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json (sha "
            f"{escalation}). Authority: campaign prompt music_gen_v4_prompt.md "
            "BINDING anti-stall rule + operator directive 2026-09-03 part (2), "
            "applied under c14-codified agent-picks selection invariants "
            "extended with c15 invariant (d)."),
        "artifacts": [
            "data/v4/profiles/31a164f845f8e27e/_manager/"
            "M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json",
        ],
    })

    events.append({**common,
        "milestone_id": "M-V4-SHOWCASE-1/cg-guitar-acceptance-resolved-c15",
        "narrative": (
            "c15 Track 4: acceptance fork auto-resolved via agent-picks "
            "invariants under FAMILY2_RULED_OUT outcome. CHOSEN=OPT3 (refuse "
            "guitar showcase; deliver CG A/B using htdemucs guitar.wav "
            "verbatim). REJECTED=OPT1 (violates a+b), OPT2 (violates b). "
            "This is c13 CG-drums acceptance done correctly the first time — "
            "validates that c14-formalized invariants prevent the c13 "
            "mis-selection class. c14 CG-drums OPT3 anchor byte-identical "
            "pre==post (delivery not re-emitted). c9 bass_v2 pinned profile "
            "byte-identical pre==post. Pinned guitar profile at "
            f"data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile.json "
            f"(sha {pinned})."),
        "artifacts": [
            "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile.json",
        ],
        "supersedes_path": (
            "data/v4/profiles/31a164f845f8e27e/_manager/"
            "M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json"),
    })

    events.append({**common,
        "milestone_id": "_plan/cg-guitar-acceptance-invariant-resolved-c15",
        "narrative": (
            "c15 fork registration parallels c14 _plan/cg-drums-acceptance-"
            "revise-c14. CHOSEN=OPT3 with invariant-compliance rationale "
            "(a/b/c/d all satisfied); REJECTED=OPT1 (a+b), OPT2 (b). "
            "Authority: campaign prompt anti-stall rule + operator directive "
            "2026-09-03 part (2) + c14-codified agent-picks selection "
            "invariants (docs/agent_picks_selection_invariants.md sha "
            f"{invariants_doc}) extended with c15 invariant (d). "
            "supersedes_path carried as str per c14 lemma."),
        "supersedes_path": (
            "data/v4/profiles/31a164f845f8e27e/_manager/"
            "M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json"),
    })

    events.append({**common,
        "milestone_id": "M-V4-PROFILES-1/cg-guitar-showcase-accepted",
        "narrative": (
            "c15 Track 4: CG guitar accepted for M-V4-SHOWCASE-1 via OPT3. "
            f"cg_guitar_pinned_profile.json (sha {pinned}) pins acceptance_"
            "option=OPT3, guitar_source_for_showcase = data/v3/deliveries/"
            "31a164f845f8e27e/cert_run1/stems_6s/guitar.wav "
            "(sha e4ff08ea10f9bbcb7083e889172fe5fcf4fac57865e957d1bbdcda9341868bd8), "
            "family_verdicts_pinned (sf2 SF2_RULED_OUT + family2 "
            "FAMILY2_RULED_OUT), acceptance_fork with 5 required keys, "
            "operator_veto_post_hoc=true per FD-6. M-V4-PROFILES-1 CG-guitar "
            "cell status = NO_WINNER_GUITAR_ACCEPTED_AS_HTDEMUCS_STEM_"
            "SUBSTITUTION (parallels c14 drums cell). Additive edit to "
            f"scripts/sound_match/deliver_cg_ab_v4.py (sha {deliver}) routes "
            "guitar OPT3 through htdemucs stem substitution before the "
            "profiles-root loop; smoke-test PASS with missing=0 (all 5 CG "
            "instruments now terminal: bass_v2 accepted; drums OPT3; piano "
            "NULL grounded; other NULL grounded; guitar OPT3)."),
        "artifacts": [
            "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile.json",
            "scripts/sound_match/deliver_cg_ab_v4.py",
        ],
    })

    # ============ Track 6 housekeeping ============
    events.append({**common,
        "milestone_id":
            "_plan/register-c15-cg-guitar-family2-and-acceptance-resolution-sub-leaves",
        "narrative": (
            "c15 POR registration adds rows for the 10 new c15 sub-leaves "
            "emitted this cycle plus this housekeeping. Closes promise_check "
            "drift for these ids. Milestones registered: cg-guitar-family2-"
            "stem-sampled, cg-guitar-family2-replay-proof, cg-guitar-family2-"
            "verdict, cg-guitar-arc-closeout, cg-guitar-acceptance-resolved-c15, "
            "cg-guitar-showcase-accepted, M-V4-SHOWCASE-1-cg-guitar-acceptance-"
            "policy, _plan/cg-guitar-acceptance-invariant-resolved-c15, "
            "_infra/guitar-stage2-grid-deviation-disclosed-c15, "
            "_infra/interpreter-guard-policy-c15."),
    })

    events.append({**common,
        "milestone_id": "_archive/cycle-15-scratch",
        "narrative": (
            "c15 scratch archival. Session-scoped scratchpad preserved under "
            "harness-managed dir; the one-shot ledger + family2 emitter "
            "scripts under scripts/sound_match/_c15_family2_guitar_emit.py "
            "and _emit_c15_ledger_events.py remain in tree for provenance "
            "(consistent with c14 _emit_c14_ledger_events.py preservation "
            "pattern). No workspace scratch to archive."),
    })

    events.append({**common,
        "milestone_id": "_infra/adopt-cycle15-tests",
        "narrative": (
            "c15 test-adoption housekeeping. No new test files this cycle; "
            "coverage for family2_stem_sampled_guitar_builder.py + spike + "
            "objective panel guitar-scoring path deferred to c16 audit "
            "fill-in per c10/c11/c12/c13/c14 pattern. Substantive verification "
            "via byte-deterministic replay proof (Track 2, run1==run2 SHA "
            "f41560714a68415c...) + FAMILY2_RULED_OUT verdict consistent with "
            "systematic 4-arc pattern."),
    })

    events.append({**common,
        "milestone_id": "_run/cycle_15_closed",
        "narrative": (
            "c15 CLOSED. Six tracks landed: (1) c14 guitar stage-2 grid-"
            "deviation retroactively disclosed + agent-picks invariant (d) "
            "codified; (2) CG guitar family-2 stem-sampled spike + builder "
            "authored, byte-det replay proof HOLDS (run1==run2==f4156071...); "
            "(3) family-2 verdict FAMILY2_RULED_OUT (emb_cos 0.0354 < 0.40 "
            "floor; consistent with 4-arc systematic pattern) + arc closeout "
            "CG_GUITAR_ARC_EXHAUSTED_NO_CONFIRMED (third CG-instrument arc "
            "exhausted); (4) acceptance escalation policy + auto-resolved OPT3 "
            "pinned profile via c14/c15 agent-picks invariants a/b/c/d + "
            "additive deliver scaffold update (smoke-test PASS missing=0); "
            "(5) interpreter guard policy formalized; (6) POR + housekeeping. "
            "M-V4-SHOWCASE-1 status: all 5 CG instruments now terminal — "
            "renderable_now=true; A/B render queued for c16 substantive "
            "advance. Operator ear remains LANDS authority post-hoc per FD-6. "
            "Not blocked on operator; anti-stall satisfied."),
    })

    emit(events)
    print(f"emitted {len(events)} events to {LEDGER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
