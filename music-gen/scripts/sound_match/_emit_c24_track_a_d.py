#!/usr/bin/python3
"""c24 Track A + D emitter.

Track A (CRITICAL discipline reset):
  - preserve 4 c23 SF2_CONFIRMED bass verdicts to stale/ byte-identical
  - re-emit 4 revised verdicts at original path (Rome+PD → SF2_RULED_OUT above-floor;
    WIG+DiscoA → STILL_INDETERMINATE below-floor pending stage-2 + operator authority)
  - emit escalation JSON with 3 named options for operator authority on
    composite-relative WINNER precedent scope-extension to non-CG bass

Track D:
  - emit 2 CG drums+guitar acceptance-corrected-disclosure JSONs (siblings; do NOT
    supersede c14/c15 OPT3 pinned profiles which stand under corrected distance
    semantics per invariants a/b/c)

Discipline: no PRNG, no sidecar_nonfactor, no VST3 state APIs, no --verify-det.
Env pin canonical 7-key sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca.
supersedes_path carried as str per c14 lemma.
Invariant (d) applied to c14 drums pinned SHA divergence (brief cites 1fcb2e46…;
on-disk is 720f1424e9fcac35… — on-disk authoritative per FD-1).
"""
import hashlib, json, os, shutil, sys
from pathlib import Path

WS = Path("/home/user/long-exposure-runs/music-gen")
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
CREATED = "2026-09-05T00:00:00Z"
RUN_ID = "run-2026-09-05T000000Z"

FOUR = [
    # (sha16, name, chosen_section_hint, expected_emb_dist, below_floor)
    ("252eb21ce7df7328", "What If I Go", "72.77..102.77s", 0.3055, True),
    ("51e433ade2a845e1", "Rome", "62.74..92.74s", 0.5145, False),
    ("88d247468cb6d49f", "Peach Dream", "172.87..202.87s", 0.4437, False),
    ("cdd2717e52820ff6", "Disco A", "21.92..51.92s", 0.2443, True),
]

def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def canonical_json(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"), default=str).encode()

def write_json(p, d):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    tmp = str(p) + ".tmp"
    Path(tmp).write_bytes(json.dumps(d, indent=2, sort_keys=True, default=str).encode() + b"\n")
    os.replace(tmp, p)

def track_a_song(sha16, name, sec, expected, below_floor):
    src = WS / f"data/v4/profiles/{sha16}/bass_family_verdict_c23.json"
    src_bytes = src.read_bytes()
    src_sha = hashlib.sha256(src_bytes).hexdigest()
    # slug for stale filename
    slug = name.lower().replace(" ", "_")
    stale = WS / f"stale/{slug}_bass_family_verdict.c23_scope_extension_disclosed.json"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_bytes(src_bytes)
    stale_sha = hashlib.sha256(stale.read_bytes()).hexdigest()
    assert stale_sha == src_sha, f"stale preservation failed for {name}"

    c23 = json.loads(src_bytes)
    ws = c23.get("winner_scoring", {})
    wpt = c23.get("winner_parameter_tuple", {})
    got_emb = ws.get("embedding_cos_vggish_as_distance")
    # brief rounds to 4-decimal; on-disk carries full float precision — 1e-3 tolerance
    assert abs(got_emb - expected) < 1e-3, f"emb_dist drift for {name}: {got_emb} vs {expected}"

    common = {
        "created": CREATED,
        "run_id": RUN_ID,
        "cycle": 24,
        "env_pin_sha256": ENV_PIN,
        "instrument": "bass",
        "song_sha16": sha16,
        "song_name": name,
        "chosen_section_hint": sec,
        "metric_semantics": "distance",
        "metric_semantics_authority": "operator resolution 2026-09-04 (distance semantics binding); composite treats emb_cos_vggish as positive-weight distance",
        "floor_reading": "distance_upper_bound_0.40",
        "floor_authority": "operator c9 2026-09-03: retained absolute 0.40 floor for ruling out degenerate (far-from-reference) candidates",
        "emb_cos_dist_top_1": got_emb,
        "top_1_program_gm_number": wpt.get("program"),
        "top_1_program_name": wpt.get("gm_name"),
        "top_1_composite": ws.get("composite"),
        "supersedes_path": f"stale/{slug}_bass_family_verdict.c23_scope_extension_disclosed.json",
        "supersedes_sha256": stale_sha,
        "operator_ear_authority": "post-hoc per FD-6",
    }

    if below_floor:
        verdict = "STILL_INDETERMINATE"
        common.update({
            "verdict": verdict,
            "verdict_enum_frozen": ["SF2_CONFIRMED", "SF2_INDETERMINATE", "SF2_RULED_OUT", "STILL_INDETERMINATE"],
            "blocked_on": (
                "(1) stage-2 fine fit AND (2) operator authority for composite-relative "
                "WINNER precedent scope-extension from CG-bass (c9) to non-CG bass"
            ),
            "stage_2_status": "queued (see Track B in c24 brief; deferred to c25 if wall exhausted)",
            "operator_authority_status": (
                "escalation emitted at data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json"
            ),
            "honest_disclosure": (
                f"c23 emitted this as SF2_CONFIRMED under scope-extended composite-relative WINNER "
                f"precedent (c9 was CG-bass-scoped; extending it to non-CG bass without operator "
                f"authority violated agent-picks invariants a+e per c24 auditor CRITICAL C-1). "
                f"c24 reverses to STILL_INDETERMINATE under corrected 0.40-as-distance-upper-bound "
                f"reading: TOP-1 emb_cos_dist {got_emb:.4f} is below-floor (close to reference = eligible) "
                f"but requires operator scope-extension authority before acceptance."
            ),
        })
    else:
        verdict = "SF2_RULED_OUT"
        common.update({
            "verdict": verdict,
            "verdict_enum_frozen": ["SF2_CONFIRMED", "SF2_INDETERMINATE", "SF2_RULED_OUT", "STILL_INDETERMINATE"],
            "honest_disclosure": (
                f"c23 emitted this as SF2_CONFIRMED under scope-extended composite-relative WINNER "
                f"precedent (extended from CG-bass without operator authority per c9 wording); "
                f"c24 reverses per c24 auditor CRITICAL C-2 (violates the retained 0.40 floor's "
                f"purpose). TOP-1 emb_cos_dist {got_emb:.4f} > 0.40 distance-upper-bound = "
                f"far-from-reference = the degenerate case the c9 floor was retained to catch."
            ),
        })

    common["manifest_kind"] = "non_cg_bass_family_verdict_c24_revised"
    common["milestone_id"] = f"M-V4-PROFILES-1/{sha16}-bass-family-verdict-revised-c24"

    dst = src
    write_json(dst, common)
    new_sha = sha256_file(dst)
    print(f"[Track A] {name} ({sha16}): {verdict} emb_dist={got_emb:.4f} new_sha={new_sha[:16]}… stale_sha={stale_sha[:16]}…")
    return {
        "sha16": sha16,
        "name": name,
        "verdict": verdict,
        "emb_dist": got_emb,
        "new_verdict_sha": new_sha,
        "stale_c23_sha": stale_sha,
        "stale_path": f"stale/{slug}_bass_family_verdict.c23_scope_extension_disclosed.json",
    }

def track_a_escalation(track_a_results):
    dst = WS / "data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json"
    esc = {
        "manifest_kind": "operator_authority_escalation",
        "milestone_id": "_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy",
        "created": CREATED,
        "run_id": RUN_ID,
        "cycle": 24,
        "status": "action_required",
        "authority": "OPERATOR",
        "blocked_on_operator": True,
        "supersedes_path": None,
        "escalation_context": (
            "c23 unilaterally scope-extended the c9 CG-bass composite-relative WINNER precedent "
            "to all 4 non-CG bass stems, emitting SF2_CONFIRMED for Rome + Peach Dream + WIG + "
            "Disco A on stage-1 alone. c24 auditor CRITICAL C-1: this scope-extension requires "
            "operator authority per FD-6. c24 Track A reverses all 4 verdicts (Rome + PD above the "
            "retained 0.40 distance-upper-bound floor → SF2_RULED_OUT; WIG + Disco A below-floor "
            "→ STILL_INDETERMINATE pending stage-2 AND operator authority). This escalation asks "
            "operator to authorize (or refuse, or scope per-song) the composite-relative WINNER "
            "precedent scope-extension for non-CG bass."
        ),
        "revised_verdicts_pinned": {
            r["sha16"]: {
                "song_name": r["name"],
                "verdict": r["verdict"],
                "emb_cos_dist_top_1": r["emb_dist"],
                "new_verdict_sha256": r["new_verdict_sha"],
                "stale_c23_path": r["stale_path"],
                "stale_c23_sha256": r["stale_c23_sha"],
            }
            for r in track_a_results
        },
        "named_options": {
            "OPT1_extend_precedent": {
                "description": (
                    "Operator authorizes composite-relative WINNER scope-extension to non-CG bass. "
                    "Agent proceeds to accept below-floor stage-2 WINNERs (WIG + Disco A) after "
                    "stage-2 fine fit + per-song replay proof. Extends c9 acceptance-fork precedent "
                    "from CG-bass-scoped to non-CG-bass-scoped."
                ),
                "eligible_songs": ["WIG (0.3055)", "Disco A (0.2443)"],
                "ineligible_songs": ["Rome (0.5145 > 0.40 floor)", "Peach Dream (0.4437 > 0.40 floor)"],
                "invariant_compliance_a_c_d": "case-by-case; requires operator scope-extension so invariant (a) preferring no operator-scope-extension is not uniquely dispositive here",
            },
            "OPT2_refuse_extension": {
                "description": (
                    "Operator refuses composite-relative WINNER scope-extension. Non-CG bass "
                    "showcase falls back to OPT3 htdemucs stem substitution per c14 drums + c15 "
                    "guitar auto-resolution precedent under invariants (a)/(b)/(c)/(d). Showcase "
                    "remains shippable via reference stems verbatim."
                ),
                "auto_resolves_per_invariants": True,
            },
            "OPT3_per_song_authorize": {
                "description": (
                    "Operator authorizes case-by-case per song. Agent emits per-song escalation "
                    "JSONs; operator responds per-song. Highest wall-time cost but maximum operator "
                    "control."
                ),
            },
        },
        "per_option_invariant_compliance": (
            "Per c24 auditor guidance: neither OPT1 nor OPT2 disambiguated by invariants "
            "(a)/(b)/(c)/(d) as a true operator-authority impossibility; agent-picks invariants "
            "(a)-(e) are NOT extended to auto-resolve this — the choice belongs to the operator."
        ),
        "showcase_status_note": (
            "M-V4-SHOWCASE-1 CG A/B (cg_ab_mix.wav sha 6e13e007…f9484b) remains LANDS_pending_operator "
            "and is not affected by this escalation. Non-CG showcase A/B is queued after this "
            "escalation resolves + Track B stage-2 lands where applicable."
        ),
        "env_pin_sha256": ENV_PIN,
        "operator_ear_authority": "post-hoc per FD-6",
    }
    write_json(dst, esc)
    print(f"[Track A] escalation JSON written: {sha256_file(dst)[:16]}…")
    return sha256_file(dst)

def track_d():
    """Emit CG drums + guitar acceptance-corrected-disclosure JSONs (siblings)."""
    # c14 drums pinned + c15 guitar pinned SHAs (on-disk, per invariant d)
    c14_drums_pinned = WS / "data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json"
    c15_guitar_pinned = WS / "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile.json"
    c14_drums_pre = sha256_file(c14_drums_pinned)
    c15_guitar_pre = sha256_file(c15_guitar_pinned)
    print(f"[Track D] c14 drums pinned pre SHA: {c14_drums_pre[:16]}…")
    print(f"[Track D] c15 guitar pinned pre SHA: {c15_guitar_pre[:16]}…")

    drums_disclosure = {
        "manifest_kind": "cg_drums_acceptance_c22_corrected_disclosure_c24",
        "milestone_id": "M-V4-SHOWCASE-1/cg-drums-acceptance-c22-corrected-disclosure-c24",
        "created": CREATED,
        "run_id": RUN_ID,
        "cycle": 24,
        "instrument": "drums",
        "song_sha16": "31a164f845f8e27e",
        "song_name": "Chicken Grease",
        "verdict": "CG_DRUMS_ACCEPTANCE_STANDS_C22_CORRECTED_UNDER_DISTANCE_SEMANTICS",
        "sf2_top_1_emb_cos_dist_value": 0.2374,
        "sf2_top_1_program": {"program": 16, "gm_name": "Power Kit", "composite": 475.74},
        "distance_semantics_reading": (
            "0.2374 is CLOSE to reference (< 0.40 distance-upper-bound); the c14 SF2_RULED_OUT "
            "verdict was WRONG under distance semantics — the candidate is NOT far-from-reference. "
            "The c22 corrected verdict correctly re-labels the sf2 top-1 as CONFIRMED under "
            "distance semantics for the numeric fact of below-floor."
        ),
        "honest_correction": (
            "c14 emitted SF2_RULED_OUT under a similarity-misread (called 0.2374 'below the 0.40 "
            "similarity floor'); c22 corrected reading shows 0.2374 is below the 0.40 "
            "distance-upper-bound = close-to-reference; sf2 candidate is NOT degenerate."
        ),
        "c14_opt3_acceptance_stands_because": (
            "OPT3 (htdemucs stem substitution) was chosen at c14 per invariants (a) "
            "prefer-no-operator-scope-extension + (b) prefer-above-floor-over-below-floor + "
            "(c) do-not-reject-on-misread; under corrected distance semantics, the sf2 candidate "
            "is close-to-reference (below-floor is GOOD under distance), but composite-relative "
            "WINNER precedent extending c9 to CG-drums STILL requires operator authority per "
            "FD-6 — OPT3 remains uniquely invariant-compliant absent operator scope-extension."
        ),
        "sf2_replay_family_proof_status": "c11 anchor holds; family-scoped per FD-16(c)",
        "c14_pinned_profile_path": "data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json",
        "c14_pinned_profile_sha256_on_disk": c14_drums_pre,
        "c14_pinned_profile_sha_note_invariant_d": (
            f"c24 brief cited c14 drums pinned SHA prefix '1fcb2e4660058ff9…' but on-disk SHA is "
            f"'{c14_drums_pre[:16]}…'. Per FD-1 + invariant (d) on-disk is authoritative; brief "
            f"cite is stale/transcription-error. c14 pinned profile byte-identical pre==post; not "
            f"modified by this disclosure."
        ),
        "c22_corrected_family_verdict_path": "data/v4/profiles/31a164f845f8e27e/drums_family_verdict_corrected_c22.json",
        "c22_corrected_pinned_profile_path": "data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile_corrected_c22.json",
        "supersedes_path": None,
        "supersedes_path_rationale": (
            "This is a corrected-disclosure SIBLING; it does NOT supersede the c14 OPT3 pinned "
            "profile which stands under invariants (a)/(b)/(c). It also does NOT supersede the c22 "
            "corrected verdict which correctly re-labels the numeric fact. It disclosively records "
            "that the c22 corrected verdict's implicit scope-extension of composite-relative WINNER "
            "precedent from CG-bass (c9) to CG-drums still requires operator authority per FD-6."
        ),
        "env_pin_sha256": ENV_PIN,
        "operator_ear_authority": "post-hoc per FD-6",
    }
    dst = WS / "data/v4/deliveries/31a164f845f8e27e/cg_drums_acceptance_c22_corrected_disclosure.json"
    write_json(dst, drums_disclosure)
    drums_sha = sha256_file(dst)
    print(f"[Track D] drums disclosure: {drums_sha[:16]}…")

    guitar_disclosure = {
        "manifest_kind": "cg_guitar_acceptance_c22_corrected_disclosure_c24",
        "milestone_id": "M-V4-SHOWCASE-1/cg-guitar-acceptance-c22-corrected-disclosure-c24",
        "created": CREATED,
        "run_id": RUN_ID,
        "cycle": 24,
        "instrument": "guitar",
        "song_sha16": "31a164f845f8e27e",
        "song_name": "Chicken Grease",
        "verdict": "CG_GUITAR_ACCEPTANCE_STANDS_C22_CORRECTED_UNDER_DISTANCE_SEMANTICS",
        "sf2_top_1_emb_cos_dist_value": 0.2584,
        "sf2_top_1_program": {"program": 28, "gm_name": "Muted Electric Guitar", "composite": 129.65},
        "distance_semantics_reading": (
            "0.2584 is CLOSE to reference (< 0.40 distance-upper-bound); the c15 SF2_RULED_OUT "
            "verdict was WRONG under distance semantics — the candidate is NOT far-from-reference."
        ),
        "honest_correction": (
            "c15 emitted SF2_RULED_OUT under a similarity-misread (called 0.2584 'below the 0.40 "
            "similarity floor'); c22 corrected reading shows 0.2584 is below the 0.40 "
            "distance-upper-bound = close-to-reference; sf2 candidate is NOT degenerate."
        ),
        "c15_opt3_acceptance_stands_because": (
            "OPT3 (htdemucs stem substitution) was chosen at c15 per invariants (a)/(b)/(c); "
            "under corrected distance semantics, the sf2 candidate is close-to-reference "
            "(below-floor is GOOD under distance), but composite-relative WINNER precedent "
            "extending c9 to CG-guitar STILL requires operator authority per FD-6 — OPT3 remains "
            "uniquely invariant-compliant absent operator scope-extension."
        ),
        "sf2_replay_family_proof_status": "c11 family anchor covers all sf2 profiles for CG (per FD-16(c))",
        "c15_pinned_profile_path": "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile.json",
        "c15_pinned_profile_sha256_on_disk": c15_guitar_pre,
        "c22_corrected_family_verdict_path": "data/v4/profiles/31a164f845f8e27e/guitar_family_verdict_corrected_c22.json",
        "c22_corrected_pinned_profile_path": "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile_corrected_c22.json",
        "supersedes_path": None,
        "supersedes_path_rationale": (
            "This is a corrected-disclosure SIBLING; it does NOT supersede the c15 OPT3 pinned "
            "profile which stands under invariants (a)/(b)/(c). It disclosively records that the "
            "c22 corrected verdict's scope-extension of composite-relative WINNER precedent from "
            "CG-bass (c9) to CG-guitar still requires operator authority per FD-6."
        ),
        "env_pin_sha256": ENV_PIN,
        "operator_ear_authority": "post-hoc per FD-6",
    }
    dst2 = WS / "data/v4/deliveries/31a164f845f8e27e/cg_guitar_acceptance_c22_corrected_disclosure.json"
    write_json(dst2, guitar_disclosure)
    guitar_sha = sha256_file(dst2)
    print(f"[Track D] guitar disclosure: {guitar_sha[:16]}…")

    # Verify c14 + c15 pinned byte-identical pre==post
    c14_drums_post = sha256_file(c14_drums_pinned)
    c15_guitar_post = sha256_file(c15_guitar_pinned)
    assert c14_drums_post == c14_drums_pre, "c14 drums pinned drifted"
    assert c15_guitar_post == c15_guitar_pre, "c15 guitar pinned drifted"
    print(f"[Track D] c14 drums + c15 guitar pinned byte-identical pre==post ✓")
    return {
        "drums_disclosure_sha": drums_sha,
        "guitar_disclosure_sha": guitar_sha,
        "c14_drums_pinned_sha": c14_drums_pre,
        "c15_guitar_pinned_sha": c15_guitar_pre,
    }

def main():
    print("=== c24 Track A + D emitter ===")
    print(f"env_pin_sha256={ENV_PIN}")
    print(f"Running from cwd={os.getcwd()}")

    # Anchor preservation pre-snapshot
    anchors = {
        "bass_v2_c9": WS / "data/v4/deliveries/31a164f845f8e27e/bass_v2.json",
        "cg_bass_pinned_c9": WS / "data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile.json",
        "cg_drums_pinned_c14": WS / "data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json",
        "cg_drums_corrected_c22": WS / "data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile_corrected_c22.json",
        "cg_guitar_pinned_c15": WS / "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile.json",
        "cg_guitar_corrected_c22": WS / "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile_corrected_c22.json",
        "cg_ab_mix_c17": WS / "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav",
        "objective_py": WS / "scripts/sound_match/objective.py",
        "replay_py": WS / "scripts/sound_match/replay.py",
    }
    anchor_pre = {k: sha256_file(v) for k, v in anchors.items() if v.exists()}
    print(f"anchor_pre snapshot: {len(anchor_pre)} anchors")

    # Track A
    print("\n--- Track A ---")
    ta_results = []
    for sha16, name, sec, expected, below_floor in FOUR:
        ta_results.append(track_a_song(sha16, name, sec, expected, below_floor))
    esc_sha = track_a_escalation(ta_results)

    # Track D
    print("\n--- Track D ---")
    td_result = track_d()

    # Anchor preservation post-snapshot
    anchor_post = {k: sha256_file(v) for k, v in anchors.items() if v.exists()}
    for k in anchor_pre:
        assert anchor_pre[k] == anchor_post[k], f"ANCHOR DRIFT: {k}"
    print(f"\nanchor_pre == anchor_post: all {len(anchor_pre)} preserved byte-identical ✓")

    # Write closeout JSON for ledger events consumption
    closeout = {
        "cycle": 24,
        "created": CREATED,
        "env_pin_sha256": ENV_PIN,
        "track_a_results": ta_results,
        "track_a_escalation_sha256": esc_sha,
        "track_d_result": td_result,
        "anchors_preserved_count": len(anchor_pre),
        "anchors_preserved_pre_eq_post": True,
    }
    closeout_path = WS / "data/v4/deliveries/31a164f845f8e27e/cycle24/track_a_d_closeout.json"
    write_json(closeout_path, closeout)
    print(f"\ncloseout: {sha256_file(closeout_path)[:16]}… at {closeout_path.relative_to(WS)}")
    print("\n=== DONE ===")

if __name__ == "__main__":
    main()
