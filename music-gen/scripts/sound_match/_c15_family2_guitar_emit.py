#!/usr/bin/python3
"""c15 Tracks 2/3/4 runner: emit family-2 guitar profile + replay proof +
verdict + arc closeout + acceptance policy + pinned showcase profile.

Not a permanent module — one-shot emitter archived to tools/stale/ after.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

for _k, _v in {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}.items():
    os.environ.setdefault(_k, _v)

_HERE = Path(__file__).resolve().parent
_WORKSPACE = _HERE.parents[1]
sys.path.insert(0, str(_WORKSPACE))

from scripts.sound_match.family2_stem_sampled_guitar_builder import (  # noqa: E402
    render as guitar_render,
)
from scripts.sound_match.objective import score_pair  # noqa: E402


ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
RUN_ID = "run-2026-09-04T100000Z"
CYCLE = 15
SONG_SHA16 = "31a164f845f8e27e"
NAMESPACE_PROFILE = uuid.UUID("00000000-0000-0000-0000-000000000004")

REF_STEM = (
    _WORKSPACE
    / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav"
)
MIDI = (
    _WORKSPACE
    / "data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage1/guitar_excerpt.mid"
)
PROFILES_DIR = _WORKSPACE / "data/v4/profiles/31a164f845f8e27e"
DELIVERIES_DIR = _WORKSPACE / "data/v4/deliveries/31a164f845f8e27e"


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _write_json(path: Path, obj: dict) -> str:
    """Write canonical JSON; return sha256 of file bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    path.write_text(body)
    return _sha256_bytes(body.encode("utf-8"))


def determinism_x2():
    """Run render into two fresh tempdirs; assert byte-equal."""
    shas = []
    for i in range(2):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "render.wav"
            r = guitar_render(REF_STEM, MIDI, out)
            shas.append(r["render_sha256"])
    return shas[0], shas[1]


def emit_all():
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z")
    ref_stem_sha = _sha256_file(REF_STEM)
    midi_sha = _sha256_file(MIDI)
    spike_sha = _sha256_file(_HERE / "family2_stem_sampled_guitar_spike.py")
    builder_sha = _sha256_file(
        _HERE / "family2_stem_sampled_guitar_builder.py")

    # ============================================================
    # Track 2: build persistent render + byte-det ×2 replay proof
    # ============================================================
    render_dir = PROFILES_DIR / "guitar_family2_render"
    render_wav = render_dir / "render.wav"
    r_persist = guitar_render(REF_STEM, MIDI, render_wav)
    persist_sha = r_persist["render_sha256"]
    print(f"[persist] render.wav sha={persist_sha[:16]}")

    r1_sha, r2_sha = determinism_x2()
    print(f"[det x2] r1={r1_sha[:16]} r2={r2_sha[:16]} eq={r1_sha == r2_sha}")
    assert r1_sha == r2_sha, "byte-det ×2 FAILED"
    assert r1_sha == persist_sha, "persist vs tempdir SHA mismatch"

    # Profile emission (family-2 v1)
    profile_body = {
        "schema_version": "v4.0",
        "manifest_kind": "cg_guitar_family2_profile_v1",
        "song_sha16": SONG_SHA16,
        "instrument": "guitar",
        "family": "family2_stem_sampled",
        "created": now,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "env_pin_sha256": ENV_PIN_SHA,
        "params": {
            "classifier": "onset_pitch_shift_concatenative",
            "slice_ms": 400,
            "sample_rate": 44100,
            "midi_channel": 0,
            "voicing_min": 0.5,
            "pyin_fmin_hz": 41.0,
            "pyin_fmax_hz": 2637.0,
        },
        "render_sha256_canonical_replay": persist_sha,
        "bank_diagnostics": r_persist["bank_diagnostics"],
        "provenance": {
            "reference_stem_path":
                "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav",
            "reference_stem_sha256": ref_stem_sha,
            "midi_path":
                "data/v4/profiles/31a164f845f8e27e/"
                "guitar_sweep_stage1/guitar_excerpt.mid",
            "midi_sha256": midi_sha,
            "spike_script_sha256": spike_sha,
            "builder_script_sha256": builder_sha,
        },
    }
    # Profile id: UUID5 over canonical JSON with render_sha256 excluded.
    id_body = {k: v for k, v in profile_body.items() if not k.startswith(
        "render_sha256")}
    profile_id = str(uuid.uuid5(
        NAMESPACE_PROFILE,
        json.dumps(id_body, sort_keys=True, separators=(",", ":"))))
    profile_body["profile_id"] = profile_id
    profile_path = PROFILES_DIR / "guitar_family2_v1.json"
    profile_sha = _write_json(profile_path, profile_body)
    print(f"[profile] {profile_path.name} id={profile_id} sha={profile_sha[:16]}")

    # Replay proof
    replay_body = {
        "schema_version": "v4.0",
        "manifest_kind": "cg_guitar_family2_replay_proof",
        "song_sha16": SONG_SHA16,
        "instrument": "guitar",
        "family": "family2_stem_sampled",
        "created": now,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "env_pin_sha256": ENV_PIN_SHA,
        "profile_id": profile_id,
        "profile_relpath": "data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.json",
        "profile_sha256": profile_sha,
        "midi_relpath":
            "data/v4/profiles/31a164f845f8e27e/"
            "guitar_sweep_stage1/guitar_excerpt.mid",
        "midi_sha256": midi_sha,
        "run1_sha256": r1_sha,
        "run2_sha256": r2_sha,
        "canonical_replay_sha256": r1_sha,
        "verdict": "REPLAY_PROOF_HOLDS",
        "verdict_reason": (
            "run1_sha256 == run2_sha256 in fresh tempfile.mkdtemp() dirs "
            "under 7-key env pins; family-2 stem_sampled is a distinct "
            "render family from sf2 per FD-16(c) so this per-song proof "
            "is authoritative for family-2 guitar on CG."),
    }
    replay_path = PROFILES_DIR / "guitar_family2_v1.replay_proof.json"
    replay_sha = _write_json(replay_path, replay_body)
    print(f"[replay ] {replay_path.name} sha={replay_sha[:16]}")

    # ============================================================
    # Track 3: score panel + verdict + arc closeout
    # ============================================================
    scores = score_pair(render_wav, REF_STEM)
    print(f"[score  ] mel_l1={scores['mel_l1_db']:.3f} "
          f"centroid_rmse={scores['spectral_centroid_rmse_hz']:.2f} "
          f"emb_cos_vggish={scores['embedding_cos_vggish']}")
    print(f"[score  ] composite={scores['composite']:.3f}")

    emb = scores.get("embedding_cos_vggish")
    if emb is None:
        verdict = "STILL_INDETERMINATE"
        verdict_reason = "embedding rung unavailable; cannot apply floor"
    elif emb >= 0.60:
        verdict = "FAMILY2_CONFIRMED"
        verdict_reason = f"emb_cos_vggish {emb:.4f} >= 0.60 CONFIRMED gate"
    elif emb < 0.40:
        verdict = "FAMILY2_RULED_OUT"
        verdict_reason = (
            f"emb_cos_vggish {emb:.4f} < 0.40 retained absolute floor")
    else:
        verdict = "STILL_INDETERMINATE"
        verdict_reason = (
            f"emb_cos_vggish {emb:.4f} in [0.40, 0.60) — neither "
            "CONFIRMED nor RULED_OUT")

    systematic_note = (
        "Predicted per systematic 4-arc pattern (bass family-2 0.0896 at c6; "
        "drums family-2 0.0372 at c12; sf2 arcs all ranked non-source-of-truth "
        "ahead of source-of-truth). Actual outcome recorded honestly.")

    verdict_body = {
        "schema_version": "v1.0",
        "manifest_kind": "cg_guitar_family2_verdict",
        "milestone_id": "M-V4-PROFILES-1/cg-guitar-family2-verdict",
        "song_sha16": SONG_SHA16,
        "instrument": "guitar",
        "family": "stem_sampled",
        "created": now,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "env_pin_sha256": ENV_PIN_SHA,
        "profile_id": profile_id,
        "profile_relpath": "data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.json",
        "profile_sha256": profile_sha,
        "profile_render_sha256": persist_sha,
        "replay_proof_relpath":
            "data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.replay_proof.json",
        "replay_proof_sha256": replay_sha,
        "replay_proof_verdict": "REPLAY_PROOF_HOLDS",
        "decision_protocol": {
            "family2_confirmed_floor_embedding_cos_vggish": 0.60,
            "family2_ruled_out_floor_embedding_cos_vggish": 0.40,
        },
        "scoring": scores,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "systematic_pattern_note": systematic_note,
        "sf2_family_context": {
            "sf2_family_verdict": "SF2_RULED_OUT",
            "sf2_family_verdict_source":
                "data/v4/profiles/31a164f845f8e27e/guitar_family_verdict.json",
            "sf2_top1_embedding_cos_vggish": 0.2584307290812553,
        },
    }
    verdict_path = PROFILES_DIR / "guitar_family2_verdict.json"
    verdict_sha = _write_json(verdict_path, verdict_body)
    print(f"[verdict] {verdict_path.name} verdict={verdict} sha={verdict_sha[:16]}")

    # Arc closeout emitted only for RULED_OUT (parallels c7/c12 shape).
    arc_sha = None
    if verdict == "FAMILY2_RULED_OUT":
        arc_body = {
            "schema_version": "v1.0",
            "manifest_kind": "cg_guitar_arc_closeout",
            "milestone_id": "M-V4-PROFILES-1/cg-guitar-arc-closeout",
            "song_sha16": SONG_SHA16,
            "instrument": "guitar",
            "created": now,
            "cycle": CYCLE,
            "run_id": RUN_ID,
            "verdict": "CG_GUITAR_ARC_EXHAUSTED_NO_CONFIRMED",
            "arcs_exhausted": [
                {
                    "family": "sf2",
                    "verdict": "SF2_RULED_OUT",
                    "verdict_source":
                        "data/v4/profiles/31a164f845f8e27e/guitar_family_verdict.json",
                    "best_available_profile":
                        "data/v4/profiles/31a164f845f8e27e/guitar.json",
                    "best_embedding_cos_vggish": 0.2584307290812553,
                },
                {
                    "family": "family2_stem_sampled",
                    "verdict": "FAMILY2_RULED_OUT",
                    "verdict_source":
                        "data/v4/profiles/31a164f845f8e27e/guitar_family2_verdict.json",
                    "best_available_profile":
                        "data/v4/profiles/31a164f845f8e27e/guitar_family2_v1.json",
                    "best_embedding_cos_vggish": emb,
                },
            ],
            "systematic_finding": (
                "Third CG-instrument arc exhausted with no CONFIRMED family "
                "(bass c7, drums c12, guitar c15). Parallel structural shape "
                "across all three CG-instrument arcs."),
        }
        arc_path = PROFILES_DIR / "guitar_arc_closeout.json"
        arc_sha = _write_json(arc_path, arc_body)
        print(f"[arc    ] {arc_path.name} sha={arc_sha[:16]}")

    # ============================================================
    # Track 4: escalation policy + auto-resolved pinned profile
    # ============================================================
    escalation_body = {
        "schema_version": "v1.0",
        "manifest_kind": "cg_guitar_acceptance_policy",
        "milestone_id":
            "_manager/M-V4-SHOWCASE-1-cg-guitar-acceptance-policy",
        "created": now,
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "song_sha16": SONG_SHA16,
        "instrument": "guitar",
        "status": (
            "resolved_via_agent_picks_invariants"
            if verdict == "FAMILY2_RULED_OUT" else "action_required"),
        "authority": (
            "agent_via_invariants_a_b_c_d + "
            "campaign_prompt_anti_stall_rule + "
            "operator_directive_2026-09-03_part_2"
            if verdict == "FAMILY2_RULED_OUT"
            else "OPERATOR"),
        "invariants_doc":
            "docs/agent_picks_selection_invariants.md",
        "options": [
            {
                "id": "OPT1",
                "text": (
                    "Accept sf2 top-1 (bank 0 program 28 Muted Electric "
                    "Guitar [GM 0-indexed; c14 profile label 'Jazz Guitar' "
                    "was a cosmetic mislabel — GM prog 26 is Jazz], "
                    "emb_cos_vggish 0.2584) as CG-guitar WINNER via "
                    "composite-relative extension. Extends bass_v2 c9 "
                    "precedent."),
                "invariant_compliance": {
                    "invariant_a_no_operator_scope_extension": False,
                    "invariant_a_note": (
                        "requires operator threshold-retirement scope "
                        "extension — currently CG-bass ONLY per c9"),
                    "invariant_b_above_floor": False,
                    "invariant_b_note": (
                        "0.2584 < 0.40 retained absolute floor"),
                    "invariant_c_verbatim_read": True,
                    "invariant_d_disclosure": True,
                },
                "reason_rejected_if_not_chosen": (
                    "violates (a) — requires operator-scope extension; "
                    "violates (b) — below-floor candidate"),
            },
            {
                "id": "OPT2",
                "text": (
                    "Accept family-2 stem-sampled render "
                    f"(emb_cos_vggish {emb}) as WINNER via embedding-first "
                    "tiebreak. Uses this cycle's replay proof."),
                "invariant_compliance": {
                    "invariant_a_no_operator_scope_extension": (
                        emb is not None and emb >= 0.40),
                    "invariant_b_above_floor": (
                        emb is not None and emb >= 0.40),
                    "invariant_c_verbatim_read": True,
                    "invariant_d_disclosure": True,
                },
                "reason_rejected_if_not_chosen": (
                    "violates (b) — family-2 emb_cos {} < 0.40 floor"
                    .format(emb) if verdict == "FAMILY2_RULED_OUT"
                    else "not chosen this cycle — sibling to OPT3 pending "
                    "operator direction"),
            },
            {
                "id": "OPT3",
                "text": (
                    "Refuse guitar showcase — deliver CG A/B using htdemucs "
                    "`data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/"
                    "guitar.wav` verbatim in the mix. Parallel to c14 revised "
                    "CG-drums acceptance."),
                "invariant_compliance": {
                    "invariant_a_no_operator_scope_extension": True,
                    "invariant_b_above_floor": True,
                    "invariant_c_verbatim_read": True,
                    "invariant_d_disclosure": True,
                },
                "reason_chosen_if_selected": (
                    "satisfies (a)+(b)+(c)+(d); anti-stall-preferred; "
                    "no candidate below floor; no operator-scope extension"),
            },
        ],
    }

    # Manager escalation dir
    mgr_dir = PROFILES_DIR / "_manager"
    mgr_dir.mkdir(parents=True, exist_ok=True)
    escalation_path = mgr_dir / (
        "M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json")
    escalation_sha = _write_json(escalation_path, escalation_body)
    print(f"[escalation] {escalation_path.name} status={escalation_body['status']} "
          f"sha={escalation_sha[:16]}")

    pinned_sha = None
    pinned_path = None
    if verdict == "FAMILY2_RULED_OUT":
        guitar_source_relpath = (
            "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav")
        guitar_source_sha = _sha256_file(_WORKSPACE / guitar_source_relpath)
        pinned_body = {
            "schema_version": "v1.0",
            "manifest_kind": "cg_guitar_pinned_profile",
            "milestone_id":
                "M-V4-PROFILES-1/cg-guitar-showcase-accepted",
            "song_sha16": SONG_SHA16,
            "instrument": "guitar",
            "created": now,
            "cycle": CYCLE,
            "run_id": RUN_ID,
            "acceptance_option": "OPT3",
            "acceptance_option_verbatim": (
                "Refuse guitar showcase — deliver CG A/B using htdemucs "
                "`data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/"
                "guitar.wav` verbatim in the mix."),
            "guitar_source_for_showcase": guitar_source_relpath,
            "guitar_source_sha256": guitar_source_sha,
            "family_verdicts_pinned": {
                "sf2": {
                    "verdict": "SF2_RULED_OUT",
                    "top_1_embedding_cos_vggish": 0.2584307290812553,
                    "source":
                        "data/v4/profiles/31a164f845f8e27e/guitar_family_verdict.json",
                },
                "family2_stem_sampled": {
                    "verdict": verdict,
                    "top_1_embedding_cos_vggish": emb,
                    "source":
                        "data/v4/profiles/31a164f845f8e27e/guitar_family2_verdict.json",
                },
            },
            "acceptance_fork": {
                "chosen": {
                    "option_id": "OPT3",
                    "invariant_compliance": (
                        "invariants (a)+(b)+(c)+(d) all satisfied; "
                        "anti-stall-preferred"),
                    "rationale": (
                        "Both explored render families (sf2 c14; "
                        "family2_stem_sampled c15) landed RULED_OUT under "
                        "the retained 0.40 emb_cos_vggish absolute floor. "
                        "No above-floor candidate exists; no operator-scope "
                        "extension is compatible with c9-scoped composite-"
                        "relative WINNER precedent. OPT3 satisfies all "
                        "c14/c15 agent-picks invariants and is the unique "
                        "anti-stall-preferred pick."),
                },
                "rejected": [
                    {
                        "option_id": "OPT1",
                        "reason":
                            "violates invariant (a) — requires operator-"
                            "scope extension; violates invariant (b) — "
                            "0.2584 < 0.40 floor",
                    },
                    {
                        "option_id": "OPT2",
                        "reason": (
                            f"violates invariant (b) — family-2 emb_cos "
                            f"{emb} < 0.40 floor"),
                    },
                ],
                "authority": (
                    "campaign prompt music_gen_v4_prompt.md BINDING "
                    "anti-stall rule + operator directive 2026-09-03 "
                    "part (2), applied under c14-codified agent-picks "
                    "selection invariants (docs/agent_picks_selection_"
                    "invariants.md) extended with c15 invariant (d)"),
            },
            "operator_veto_post_hoc": True,
            "supersedes_path": str(
                escalation_path.relative_to(_WORKSPACE)),
            "honest_disclosure": (
                "OPT3 means CG showcase A/B uses operator-heard reference "
                "guitar stem as-is; family exploration arc closed as "
                "documented; no guitar profile is emitted as WINNER for "
                "CG-guitar. M-V4-PROFILES-1 CG-guitar cell status = "
                "NO_WINNER_GUITAR_ACCEPTED_AS_HTDEMUCS_STEM_SUBSTITUTION "
                "(parallels c14 drums cell)."),
            "cosmetic_label_note": (
                "c14 guitar.json labels top-1 program 28 as 'Jazz Guitar'. "
                "GM standard 0-indexed program 28 is 'Muted Electric "
                "Guitar'; program 26 is 'Jazz Guitar'. Cosmetic-only "
                "label mislabel in c14 profile; profile params unchanged; "
                "c14 guitar.json remains READ-ONLY per FD-1; the correct "
                "GM name is recorded here in c15 for future reference."),
        }
        pinned_path = DELIVERIES_DIR / "cg_guitar_pinned_profile.json"
        pinned_sha = _write_json(pinned_path, pinned_body)
        print(f"[pinned ] {pinned_path.name} sha={pinned_sha[:16]}")

    summary = {
        "verdict": verdict,
        "profile_id": profile_id,
        "profile_sha256": profile_sha,
        "profile_render_sha256": persist_sha,
        "replay_proof_sha256": replay_sha,
        "verdict_sha256": verdict_sha,
        "arc_closeout_sha256": arc_sha,
        "escalation_sha256": escalation_sha,
        "pinned_profile_sha256": pinned_sha,
        "pinned_profile_path": (
            str(pinned_path.relative_to(_WORKSPACE)) if pinned_path else None),
        "score": scores,
    }
    summary_path = PROFILES_DIR / "_c15_guitar_family2_summary.json"
    _write_json(summary_path, summary)
    print(f"\n=== SUMMARY ===\n{json.dumps(summary, indent=2)}")
    return summary


if __name__ == "__main__":
    emit_all()
