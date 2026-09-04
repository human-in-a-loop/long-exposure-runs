#!/usr/bin/env python3
# ------------------------------------------------------------------
# c12 Track 4: CG drums arc closeout + operator escalation.
#
# Both sf2 and family-2 arcs for CG drums have exhausted without a
# CONFIRMED gate:
#   sf2   : SF2_RULED_OUT  (c11; top-1 embedding_cos_vggish=0.2374)
#   family2: FAMILY2_RULED_OUT (c12; embedding_cos_vggish=0.1195)
#
# Emits:
#   * drums_arc_closeout.json  (parallel to c7 bass_arc_closeout.json)
#   * _manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json
#     (3 named options for operator per c11 auditor guidance)
#
# Per FD-6 + c9 scoping: the acceptance-policy call is OPERATOR
# authority; bass_v2 composite-relative WINNER precedent is scoped
# to CG bass acceptance only and does NOT auto-carry to drums.
#
# created: 2026-09-04
# cycle: 12
# ------------------------------------------------------------------

from __future__ import annotations

import hashlib
import json
from pathlib import Path

_WORKSPACE = Path(__file__).resolve().parents[2]
_PROFILE_DIR = _WORKSPACE / "data/v4/profiles/31a164f845f8e27e"


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _load(p: Path) -> dict:
    with open(p) as f:
        return json.load(f)


def main() -> int:
    sf2_verdict = _load(_PROFILE_DIR / "drums_family_verdict.json")
    family2_verdict = _load(_PROFILE_DIR / "drums_family2_verdict.json")
    drums_profile = _load(_PROFILE_DIR / "drums.json")
    family2_profile = _load(_PROFILE_DIR / "drums_family2_v1.json")

    closeout = {
        "schema_version": "v1.0",
        "milestone_id": "M-V4-PROFILES-1/cg-drums-arc-closeout",
        "cycle": 12,
        "song_sha16": "31a164f845f8e27e",
        "instrument": "drums",
        "verdict": "CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED",
        "arc_summary": {
            "sf2": {
                "verdict": sf2_verdict["verdict"],
                "verdict_source": (
                    "data/v4/profiles/31a164f845f8e27e/"
                    "drums_family_verdict.json"),
                "verdict_sha256": _sha256_file(
                    _PROFILE_DIR / "drums_family_verdict.json"),
                "top1_embedding_cos_vggish": (
                    sf2_verdict.get("scoring", {})
                    .get("embedding_cos_vggish")
                    or 0.2374),
                "top1_profile": (
                    "data/v4/profiles/31a164f845f8e27e/drums.json"),
                "top1_params": {
                    "bank": drums_profile["params"].get("bank"),
                    "program": drums_profile["params"].get("program"),
                    "program_name": "Power Kit (GM prog 16)",
                    "gain": drums_profile["params"].get("gain"),
                    "reverb_send": drums_profile["params"].get(
                        "reverb_send"),
                    "post": drums_profile["params"].get("post"),
                },
                "max_embedding_cos_across_216_cells": 0.4645,
                "max_embedding_cos_program": (
                    "48 (Orchestra Kit), rank 76"),
            },
            "family2_stem_sampled": {
                "verdict": family2_verdict["verdict"],
                "verdict_source": (
                    "data/v4/profiles/31a164f845f8e27e/"
                    "drums_family2_verdict.json"),
                "verdict_sha256": _sha256_file(
                    _PROFILE_DIR / "drums_family2_verdict.json"),
                "embedding_cos_vggish": (
                    family2_verdict["scoring"].get(
                        "embedding_cos_vggish")),
                "profile": (
                    "data/v4/profiles/31a164f845f8e27e/"
                    "drums_family2_v1.json"),
                "profile_id": family2_profile["profile_id"],
                "profile_render_sha256": family2_profile[
                    "render_sha256_canonical_replay"],
            },
        },
        "decision_protocol_pinned_floors": {
            "family_confirmed_floor_embedding_cos_vggish": 0.60,
            "family_ruled_out_floor_embedding_cos_vggish": 0.40,
        },
        "cross_song_parallel_findings": {
            "cg_bass_arc": {
                "verdict": "CG_BASS_ARC_EXHAUSTED_NO_CONFIRMED at c7",
                "resolution": (
                    "OPERATOR DIRECTIVE 2026-09-03 (c9) accepted "
                    "bass_v2 as CG-bass WINNER via composite-"
                    "relative extension.  Kill gate 0.60 retired "
                    "for CG-bass acceptance scope only; 0.40 floor "
                    "retained globally."),
            },
            "cg_bass_family2": {
                "verdict": "FAMILY2_RULED_OUT",
                "embedding_cos_vggish": 0.0896,
            },
            "systematic_finding": (
                "Second CG-instrument arc exhausted (bass first at "
                "c7). Pattern accumulating; may cascade to piano/"
                "guitar/other.  First-class characterization of "
                "the sf2 objective's discriminative behaviour on "
                "CG content — NOT a defect."
            ),
        },
        "showcase_impact": {
            "m_v4_showcase_1_tally": (
                "2/5 CG instruments have verdicts (bass_v2 accepted; "
                "drums both families RULED_OUT).  Piano, guitar, "
                "other-residual remain PENDING.  Full A/B render "
                "gated on operator drums-acceptance decision."
            ),
        },
    }

    escalation = {
        "schema_version": "v1.0",
        "milestone_id": (
            "_manager/M-V4-SHOWCASE-1-cg-drums-acceptance-policy"),
        "cycle": 12,
        "action_required": True,
        "authority": "OPERATOR",
        "scope": "CG drums acceptance policy for M-V4-SHOWCASE-1",
        "context": {
            "sf2_verdict": "SF2_RULED_OUT",
            "sf2_top1_emb_cos": 0.2374,
            "sf2_max_emb_cos_across_216": 0.4645,
            "family2_verdict": "FAMILY2_RULED_OUT",
            "family2_emb_cos": (
                family2_verdict["scoring"].get(
                    "embedding_cos_vggish")),
            "note": (
                "Per c11 auditor guidance: agent does NOT "
                "unilaterally invoke OPT1+OPT3 composite-relative "
                "WINNER precedent for drums — operator authority "
                "required per c9 scoping."
            ),
        },
        "named_options": [
            {
                "id": "OPT1",
                "label": "Accept sf2 top-1 as CG-drums WINNER "
                         "(composite-relative extension)",
                "profile_path": (
                    "data/v4/profiles/31a164f845f8e27e/drums.json"),
                "profile_params": (
                    "bank 0, program 16 (Power Kit), gain 1.0, "
                    "reverb 0.7, post EQ_only"),
                "profile_embedding_cos_vggish": 0.2374,
                "consequence": (
                    "Extends bass_v2 c9 precedent (composite-"
                    "relative WINNER across families).  Retains 0.40 "
                    "floor for RULED_OUT (family2 already below).  "
                    "Requires operator threshold-retirement scope "
                    "extension: currently CG-bass ONLY per c9 wording."
                ),
            },
            {
                "id": "OPT2",
                "label": "Accept sf2 max-emb_cos candidate "
                         "(embedding-first tiebreak)",
                "profile_params": (
                    "bank 0, program 48 (Orchestra Kit), rank 76 "
                    "by composite but max_emb_cos=0.4645 across "
                    "all 216 stage-2 cells"),
                "profile_embedding_cos_vggish": 0.4645,
                "note": (
                    "Requires reissuing a new drums profile with "
                    "the prog-48 top-emb_cos parameter tuple + "
                    "fresh replay proof.  Below 0.60 CONFIRMED "
                    "floor but above 0.40 RULED_OUT floor.  Does "
                    "NOT rely on composite-relative extension."
                ),
                "cost": "small (single fine-fit lookup + 1 render + 1 replay proof)",
            },
            {
                "id": "OPT3",
                "label": "Refuse drums showcase — deliver CG A/B "
                         "without drums recreation",
                "consequence": (
                    "M-V4-SHOWCASE-1 delivers with 4 CG "
                    "instruments (bass_v2 + piano + guitar + "
                    "other-residual, once profiled).  Original "
                    "htdemucs drums track used as-is in the mix.  "
                    "Honest acknowledgement that CG drums cannot "
                    "be sound-matched under either family with the "
                    "0.60 kill gate held in place globally."
                ),
            },
        ],
        "unilateral_action_taken_this_cycle": (
            "NONE — arc closeout + escalation only.  Do NOT choose "
            "an option; wait for operator directive in live_guidance."
        ),
    }

    def _write(name: str, doc: dict) -> Path:
        p = _PROFILE_DIR / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n")
        return p

    p_close = _write("drums_arc_closeout.json", closeout)
    p_esc = _write(
        "_manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json",
        escalation,
    )

    summary = {
        "closeout_path": str(p_close.relative_to(_WORKSPACE)),
        "closeout_sha256": _sha256_file(p_close),
        "escalation_path": str(p_esc.relative_to(_WORKSPACE)),
        "escalation_sha256": _sha256_file(p_esc),
    }
    (_PROFILE_DIR / "_c12_track4_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
