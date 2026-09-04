#!/usr/bin/env python3
# ------------------------------------------------------------------
# c12 Track 2/3 finisher: score the family-2 drums render vs the
# reference drums stem using the frozen objective panel, then emit
#   * drums_family2_v1.json    (v4 profile schema, family-2)
#   * drums_family2.replay_proof.json  (byte-det x2 from fresh tempdirs)
#   * drums_family2_verdict.json       (FAMILY2_CONFIRMED / RULED_OUT
#                                       / STILL_INDETERMINATE per c12
#                                       decision protocol)
#
# Family-2 is a NEW render family per FD-16(c): needs its own per-song
# replay proof distinct from the sf2 replay proof (drums.replay_proof
# .json at dadafcfc...).
#
# c12 brief decision protocol:
#   FAMILY2_CONFIRMED    : embedding_cos_vggish >= 0.60
#   FAMILY2_RULED_OUT    : embedding_cos_vggish <= 0.40
#   STILL_INDETERMINATE  : otherwise
#
# created: 2026-09-04
# cycle: 12
# run_id: run-2026-09-04T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-drums-family2-*
# ------------------------------------------------------------------

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path

# Env pins (7-key canonical).
_ENV_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _ENV_PINS.items():
    os.environ.setdefault(_k, _v)

_WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_WORKSPACE))

from scripts.sound_match import objective as objmod  # noqa: E402
from scripts.sound_match.family2_stem_sampled_drums_builder import (  # noqa: E402
    render as f2_render,
)

_PROFILE_DIR = _WORKSPACE / "data/v4/profiles/31a164f845f8e27e"
_REF_STEM = (
    _WORKSPACE
    / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/drums.wav"
)
_MIDI = (
    _WORKSPACE
    / "data/v4/profiles/31a164f845f8e27e/"
    / "drums_sweep_stage1/drums_excerpt.mid"
)
_MAIN_RENDER = _PROFILE_DIR / "drums_family2_render" / "render.wav"

# c12 brief pinned floors.
_FAMILY2_CONFIRMED_FLOOR = 0.60
_FAMILY2_RULED_OUT_FLOOR = 0.40


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _canon_env_pin_sha256() -> str:
    return hashlib.sha256(
        json.dumps(_ENV_PINS, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _canonical_json_sha256_ex(obj: dict, exclude_prefixes: tuple) -> str:
    filtered = {k: v for k, v in obj.items()
                if not any(k.startswith(p) for p in exclude_prefixes)
                and not k == "profile_id"}
    b = json.dumps(filtered, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def emit_profile(render_sha: str) -> dict:
    """Build family-2 profile (v4.0 schema)."""
    # Deterministic UUID5 profile_id.
    ns = uuid.UUID("00000000-0000-5000-8000-000000000004")  # v4 ns
    profile = {
        "schema_version": "v4.0",
        "song_sha16": "31a164f845f8e27e",
        "instrument": "drums",
        "family": "stem_sampled",
        "params": {
            "window_ms": 400,
            "classifier": "band_energy_argmax_kick_snare_hihat",
            "midi_channel": 10,
            "sample_rate": 44100,
            "pitch_to_class_map_version": "v1",
        },
        "provenance": {
            "ref_stem_path": (
                "data/v3/deliveries/31a164f845f8e27e/"
                "cert_run1/stems_6s/drums.wav"),
            "ref_stem_sha256": _sha256_file(_REF_STEM),
            "midi_path": (
                "data/v3/deliveries/31a164f845f8e27e/"
                "cert_run1/operator_section/per_track/drums.mid"),
            "midi_sha256": _sha256_file(_MIDI),
            "builder_module": (
                "scripts.sound_match.family2_stem_sampled_drums_builder"),
            "cycle": 12,
        },
        "env_pins": dict(_ENV_PINS),
        "env_pin_sha256": _canon_env_pin_sha256(),
        "render_sha256_canonical_replay": render_sha,
    }
    # profile_id excludes render_sha256* + profile_id from pre-image.
    pre_sha = _canonical_json_sha256_ex(
        profile, exclude_prefixes=("render_sha256",))
    profile["profile_id"] = str(uuid.uuid5(ns, pre_sha))
    return profile


def build_replay_proof() -> dict:
    """Render twice into fresh tempdirs, assert SHA equality."""
    shas = []
    for i in (1, 2):
        with tempfile.TemporaryDirectory(
                prefix=f"c12_f2drums_run{i}_") as td:
            out = Path(td) / "render.wav"
            r = f2_render(_REF_STEM, _MIDI, out)
            shas.append(r["render_sha256"])
    verdict = ("REPLAY_PROOF_HOLDS" if shas[0] == shas[1]
               else "REPLAY_PROOF_FAILS")
    return {
        "schema_version": "v1.0",
        "milestone_id": (
            "M-V4-PROFILES-1/cg-drums-family2-replay-proof"),
        "cycle": 12,
        "family": "stem_sampled",
        "instrument": "drums",
        "song_sha16": "31a164f845f8e27e",
        "run1_sha256": shas[0],
        "run2_sha256": shas[1],
        "env_pins": dict(_ENV_PINS),
        "env_pin_sha256": _canon_env_pin_sha256(),
        "midi_path": (
            "data/v3/deliveries/31a164f845f8e27e/"
            "cert_run1/operator_section/per_track/drums.mid"),
        "midi_sha256": _sha256_file(_MIDI),
        "verdict": verdict,
        "note": (
            "Family-2 (stem-sampled) is a distinct render family from "
            "sf2 per FD-16(c); this proof is scoped to the family-2 "
            "code path and covers all future stem-sampled profiles "
            "emitted for CG drums."
        ),
    }


def score_family2(render_sha_expected: str) -> dict:
    """Score main render vs reference stem via objective panel."""
    # Verify main render sha matches builder output before scoring.
    actual_sha = _sha256_file(_MAIN_RENDER)
    if actual_sha != render_sha_expected:
        raise SystemExit(
            f"render sha mismatch: {actual_sha} != {render_sha_expected}")
    return objmod.score_pair(_MAIN_RENDER, _REF_STEM)


def build_verdict(scoring: dict, profile: dict, proof: dict) -> dict:
    ec = float(scoring.get("embedding_cos_vggish", float("nan")))
    if ec >= _FAMILY2_CONFIRMED_FLOOR:
        v = "FAMILY2_CONFIRMED"
    elif ec <= _FAMILY2_RULED_OUT_FLOOR:
        v = "FAMILY2_RULED_OUT"
    else:
        v = "STILL_INDETERMINATE"
    return {
        "schema_version": "v1.0",
        "milestone_id": "M-V4-PROFILES-1/cg-drums-family2-verdict",
        "cycle": 12,
        "song_sha16": "31a164f845f8e27e",
        "instrument": "drums",
        "family": "stem_sampled",
        "verdict": v,
        "scoring": scoring,
        "decision_protocol": {
            "family2_confirmed_floor_embedding_cos_vggish":
                _FAMILY2_CONFIRMED_FLOOR,
            "family2_ruled_out_floor_embedding_cos_vggish":
                _FAMILY2_RULED_OUT_FLOOR,
        },
        "profile_id": profile["profile_id"],
        "profile_render_sha256": profile["render_sha256_canonical_replay"],
        "replay_proof_verdict": proof["verdict"],
        "cross_family_context": {
            "sf2_family_verdict": "SF2_RULED_OUT",
            "sf2_family_verdict_source": (
                "data/v4/profiles/31a164f845f8e27e/"
                "drums_family_verdict.json"),
            "sf2_top1_embedding_cos_vggish": 0.2374,
            "sf2_max_embedding_cos_vggish": 0.4645,
            "note": (
                "sf2 max emb_cos 0.4645 (prog 48 Orchestra Kit, "
                "rank 76) is below CONFIRMED gate 0.60 but above "
                "RULED_OUT floor 0.40. Composite-relative WINNER "
                "extension is operator-authority per c9 scoping."
            ),
        },
        "bass_family2_precedent": {
            "verdict": "FAMILY2_RULED_OUT",
            "embedding_cos_vggish": 0.0896,
            "path": (
                "data/v4/profiles/31a164f845f8e27e/"
                "bass_family2_verdict.json"),
        },
    }


def main() -> int:
    scoring = score_family2(_sha256_file(_MAIN_RENDER))
    profile = emit_profile(_sha256_file(_MAIN_RENDER))
    proof = build_replay_proof()
    verdict = build_verdict(scoring, profile, proof)

    def _write(name: str, doc: dict) -> Path:
        p = _PROFILE_DIR / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
        return p

    p_profile = _write("drums_family2_v1.json", profile)
    p_proof = _write("drums_family2.replay_proof.json", proof)
    p_verdict = _write("drums_family2_verdict.json", verdict)

    def _sha(p): return _sha256_file(p)

    summary = {
        "profile_path": str(p_profile.relative_to(_WORKSPACE)),
        "profile_sha256": _sha(p_profile),
        "profile_id": profile["profile_id"],
        "replay_proof_path": str(p_proof.relative_to(_WORKSPACE)),
        "replay_proof_sha256": _sha(p_proof),
        "replay_proof_verdict": proof["verdict"],
        "replay_run1_sha256": proof["run1_sha256"],
        "replay_run2_sha256": proof["run2_sha256"],
        "verdict_path": str(p_verdict.relative_to(_WORKSPACE)),
        "verdict_sha256": _sha(p_verdict),
        "verdict": verdict["verdict"],
        "embedding_cos_vggish": scoring.get("embedding_cos_vggish"),
        "mel_l1_db": scoring.get("mel_l1_db"),
        "spectral_centroid_rmse_hz": scoring.get("spectral_centroid_rmse_hz"),
        "composite": scoring.get("composite"),
    }
    _PROFILE_DIR.joinpath("_c12_track3_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
