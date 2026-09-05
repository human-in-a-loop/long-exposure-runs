#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-05T21:00:00Z
# cycle: 59
# run_id: run-2026-09-05T210000Z
# agent: worker
# milestone: M-V4-PROFILES-1/pd-drums-{profile,replay-proof,family-verdict}
# ---
"""c59 P2 emitter: Peach Dream (88d247468cb6d49f) drums.json + drums.replay_proof.json +
drums_family_verdict.json. Mirrors c58 Rome shape verbatim with invariant (d)
stem_source_divergence_note field pinning the non-standard
`operator_section_c25_checkpointed/rc9_6stem/` path (c25 checkpointed run;
disclosed on-disk at PD stem_manifest.json cycle 19)."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.sound_match.replay_proof import prove_replay  # noqa: E402

SF2_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

GM_DRUMS_NAMES = {
    0: "Standard Kit", 8: "Room Kit", 16: "Power Kit", 24: "Electronic Kit",
    25: "TR-808 Kit", 32: "Jazz Kit", 40: "Brush Kit", 48: "Orchestra Kit",
}

STEM_DIVERGENCE_NOTE = (
    "Peach Dream htdemucs stems live at "
    "`data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/rc9_6stem/` "
    "per c25 checkpointed-driver run. The standard "
    "`operator_section/rc9_6stem/` path does NOT exist for this song (unlike "
    "CG/WIG/Rome/Disco A). Disclosed per invariant (d) on-disk-vs-brief "
    "divergence norm; brief specified the standard path but on-disk reality "
    "prevails per FD-1. Stem source registered in "
    "data/v4/profiles/88d247468cb6d49f/stem_manifest.json (sha c4944ee80…) "
    "at cycle 19 opening."
)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


PD = {
    "song_sha16": "88d247468cb6d49f",
    "song_name": "Peach Dream",
    # top-1 from data/v4/profiles/88d247468cb6d49f/drums_sweep_stage2/leaderboard.tsv
    "program": 16, "preset_rank_stage1": 1,
    "gain": 0.5, "reverb_send": 0.7, "post": "EQ_only",
    "composite": 987.5397852590627,
    "mel_l1_db": 20.446773529052734,
    "spectral_centroid_rmse_hz": 3889.482230978669,
    "embedding_cos_vggish": 0.19783362999476017,
    "config_hash": "edecdafd9fb00a188bb2534bf225e2166bcea5107a534a56e8558087a0a83a98",
    "render_sha_in_sweep": "84dafa54ba31c47094e354b1b82c23223caddba5723fb4e246bff0f30c8714db",
    "stage1_leaderboard_sha": "b1b69b61ef8c926e1d873c5b15f32ba58724fab59e657076bca6fca1c5c1717b",
    "stage2_leaderboard_sha": "c64a25a223f24724a9ef830b6e48de62b198c190783f6940e04a425b0fe0face",
    "drums_midi_sha": "e03458aaff684da6854508dbc32bd2acbd67ff3391233d6831fbd128840bad90",
    "ref_stem_sha": "5cce25ad039bd4abdb15cf501cca94c029648d11e2ca27fa61ae1cb8d7bcc58c",
}


def compute_profile_id(body):
    excluded = {"profile_id", "render_sha256_canonical_replay"}
    b = {k: v for k, v in body.items() if k not in excluded}
    canon = json.dumps(b, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(uuid.NAMESPACE_URL, canon))


def emit(s):
    sha16 = s["song_sha16"]
    profile_dir = ROOT / f"data/v4/profiles/{sha16}"
    stage1_dir_rel = f"data/v4/profiles/{sha16}/drums_sweep_stage1"
    stage2_dir_rel = f"data/v4/profiles/{sha16}/drums_sweep_stage2"
    # NON-STANDARD PATH per invariant (d):
    stem_dir_rel = (
        f"data/v3_spine/{sha16}/operator_section_c25_checkpointed/rc9_6stem/drums.wav"
    )
    midi_path = ROOT / f"{stage1_dir_rel}/drums_excerpt.mid"

    body = {
        "deps_sha256": {
            "drums_midi_sha256": s["drums_midi_sha"],
            "reference_stem_sha256": s["ref_stem_sha"],
            "sf2_sha256": SF2_SHA,
        },
        "family": "sf2",
        "identity": {
            "bank": 0,
            "preset_name": GM_DRUMS_NAMES[s["program"]],
            "program": s["program"],
            "sf2_path": SF2_PATH,
            "sf2_sha256": SF2_SHA,
        },
        "instrument": "drums",
        "objective_scores": {
            "composite": s["composite"],
            "embedding_cos_vggish": s["embedding_cos_vggish"],
            "mel_l1_db": s["mel_l1_db"],
            "objective_weights_frozen": {
                "centroid_rmse": 0.25, "embedding_cos": 0.25, "mel_l1": 0.5,
            },
            "spectral_centroid_rmse_hz": s["spectral_centroid_rmse_hz"],
        },
        "params": {
            "gain": s["gain"],
            "lufs_target_db": -18.0,
            "midi_channel": 10,
            "post": s["post"],
            "reverb_send": s["reverb_send"],
            "sample_rate": 44100,
        },
        "provenance": {
            "drums_midi_source": {
                "channel": 10, "path": str(midi_path), "sha256": s["drums_midi_sha"],
            },
            "env_pin_sha256_replay_time_7key": ENV_PIN_SHA,
            "reference_stem": {
                "path": str(ROOT / stem_dir_rel), "sha256": s["ref_stem_sha"],
            },
            "sf2": {"path": SF2_PATH, "sha256": SF2_SHA},
            "stage1_leaderboard": {
                "path": str(ROOT / f"{stage1_dir_rel}/leaderboard.tsv"),
                "sha256": s["stage1_leaderboard_sha"],
            },
            "stage2_leaderboard": {
                "path": str(ROOT / f"{stage2_dir_rel}/leaderboard.tsv"),
                "sha256": s["stage2_leaderboard_sha"],
            },
        },
        "render_replayable": True,
        "schema_v": "v4.0",
        "search_metadata": {
            "config_hash": s["config_hash"],
            "cycle": 59,
            "grid_gain": s["gain"],
            "grid_post": s["post"],
            "grid_program": s["program"],
            "grid_reverb_send": s["reverb_send"],
            "preset_rank_stage1": s["preset_rank_stage1"],
            "render_sha256_in_sweep": s["render_sha_in_sweep"],
            "stage": "stage2_fine_fit_c58",
        },
        "song_sha16": sha16,
        "stem_source_divergence_note": STEM_DIVERGENCE_NOTE,
    }
    profile_id = compute_profile_id(body)
    body["profile_id"] = profile_id

    tmp_out = ROOT / f"data/v4/_run/_c59_replay_probe_{sha16}.json"
    tmp_out.parent.mkdir(parents=True, exist_ok=True)
    report = prove_replay(body, midi_path, out_json=tmp_out)
    canonical_replay_sha = report["run1_sha256"]
    body["render_sha256_canonical_replay"] = canonical_replay_sha

    profile_path = profile_dir / "drums.json"
    with open(profile_path, "w") as f:
        json.dump(body, f, sort_keys=True, separators=(",", ":"))
    profile_sha = sha256_of_file(profile_path)

    proof_path = profile_dir / "drums.replay_proof.json"
    proof_body = json.loads(tmp_out.read_text())
    proof_body["profile_id"] = profile_id
    proof_body["profile_sha256"] = profile_sha
    with open(proof_path, "w") as f:
        json.dump(proof_body, f, sort_keys=True, indent=2)
    proof_sha = sha256_of_file(proof_path)
    tmp_out.unlink()

    replay_holds = (report["run1_sha256"] == report["run2_sha256"])
    if not replay_holds:
        raise RuntimeError(
            f"REPLAY_PROOF_FAILS: run1={report['run1_sha256']} run2={report['run2_sha256']}"
        )

    verdict_body = {
        "song_sha16": sha16,
        "instrument": "drums",
        "family": "sf2",
        "verdict": "SF2_CONFIRMED",
        "verdict_cycle": 59,
        "authority": (
            "c47 operator omnibus adjudication 2026-09-05 point (3): "
            "OPT1 EXTENDED campaign-wide (best-of-search across families "
            "under distance semantics; SF2_CONFIRMED lifted)."
        ),
        "objective_scores": body["objective_scores"],
        "profile_id": profile_id,
        "profile_sha256": profile_sha,
        "replay_proof_sha256": proof_sha,
        "render_sha256_canonical_replay": canonical_replay_sha,
        "honest_disclosure": {
            "embedding_cos_vggish": s["embedding_cos_vggish"],
            "distance_semantics_note": (
                "Under 2026-09-04 operator ruling, embedding_cos_vggish is a "
                "DISTANCE metric; lower is better. 0.40 upper-bound rules OUT "
                "only degenerate candidates."
            ),
            "best_of_search_across_families": True,
            "stem_source_divergence_note": STEM_DIVERGENCE_NOTE,
        },
        "env_pin_sha256": ENV_PIN_SHA,
    }
    verdict_path = profile_dir / "drums_family_verdict.json"
    with open(verdict_path, "w") as f:
        json.dump(verdict_body, f, sort_keys=True, indent=2)
    verdict_sha = sha256_of_file(verdict_path)

    return {
        "song_sha16": sha16, "song_name": s["song_name"],
        "profile_id": profile_id, "profile_sha256": profile_sha,
        "replay_proof_sha256": proof_sha,
        "render_sha256_canonical_replay": canonical_replay_sha,
        "family_verdict_sha256": verdict_sha,
        "verdict": "SF2_CONFIRMED",
        "embedding_cos_vggish": s["embedding_cos_vggish"],
        "top1_program": s["program"], "top1_preset": GM_DRUMS_NAMES[s["program"]],
        "top1_composite": s["composite"],
        "run1_sha256": report["run1_sha256"],
        "run2_sha256": report["run2_sha256"],
    }


r = emit(PD)
out = ROOT / "data/v4/_run/c59_pd_drums_emit_results.json"
with open(out, "w") as f:
    json.dump(r, f, sort_keys=True, indent=2)
print(
    f"[{r['song_name']}] verdict={r['verdict']} "
    f"profile_sha={r['profile_sha256'][:16]}… "
    f"replay_proof_sha={r['replay_proof_sha256'][:16]}… "
    f"top1={r['top1_program']}({r['top1_preset']}) "
    f"composite={r['top1_composite']:.2f} "
    f"emb_cos_dist={r['embedding_cos_vggish']:.4f}"
)
print(
    f"REPLAY_PROOF: run1={r['run1_sha256'][:16]}… run2={r['run2_sha256'][:16]}…  "
    f"HOLDS={r['run1_sha256']==r['run2_sha256']}"
)
print(f"Summary: {out.relative_to(ROOT)}")
