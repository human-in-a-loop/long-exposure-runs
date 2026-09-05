#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-05T18:00:00Z
# cycle: 57
# run_id: run-2026-09-05T180000Z
# agent: worker
# milestone: M-V4-PROFILES-1/{wig,disco-a}-drums-{profile,replay-proof,family-verdict}
# ---
"""c57 P4 + P5 substantive emitter: drums.json + drums.replay_proof.json +
drums_family_verdict.json for WIG (252eb21ce7df7328) and Disco A
(cdd2717e52820ff6). Mirrors CG drums c11 shape verbatim; uses c11 channel-
aware replay path. Under c47 OPT1-extended acceptance, both verdicts are
SF2_CONFIRMED (best-of-search across families per binding spec).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

# env pins BEFORE any observed import
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


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


SONGS = [
    {
        "song_sha16": "252eb21ce7df7328",
        "song_name": "What_If_I_Go",
        # top-1 stage-2 row
        "program": 0, "preset_rank_stage1": 5,
        "gain": 1.5, "reverb_send": 0.7, "post": "EQ_and_compressor",
        "composite": 464.7534527495166,
        "mel_l1_db": 11.269843101501465,
        "spectral_centroid_rmse_hz": 1822.7662991579687,
        "embedding_cos_vggish": 0.1370782563709494,
        "config_hash": "947c7b604cd22d3ea0f2665e1789a49011395f9abc35182ec22606d9f1ac2d6e",
        "render_sha_in_sweep": "57642475bd7369343277dfdc09db185d658722095adc16ba368f047dcb14c3da",
        "stage1_leaderboard_sha": "073ee28f9cc7ecc0f61d5f0a3d179b8b75de5a6634021c1ef86365c5ccb3ee1e",
        "stage2_leaderboard_sha": "c6aeea90bd099feb8526edf8c49e5af7449b78a067ffcb71e8bf0fb54d2c2367",
        "drums_midi_sha": "8293d243a3a0179521bac38f262ddf6e151cb97b6148c72d43fdf0251e8c1ad0",
        "ref_stem_sha": "4ea5bfb2d442e3f74b460ba4a15d9b799a9053d9b7488d217e9b18406db97e83",
    },
    {
        "song_sha16": "cdd2717e52820ff6",
        "song_name": "Disco_A",
        "program": 16, "preset_rank_stage1": 1,
        "gain": 1.5, "reverb_send": 0.7, "post": "EQ_only",
        "composite": 544.2458870453127,
        "mel_l1_db": 13.236023902893066,
        "spectral_centroid_rmse_hz": 2129.197677804655,
        "embedding_cos_vggish": 0.2131382257080957,
        "config_hash": "8db07305514dffd98318139613c8b9834a584927d153d20a0a9e1d13f2cce330",
        "render_sha_in_sweep": "8f5bcf4132e87df15b97a57a0d5017131af0a26fededd50ffd5ce24d3da04d85",
        "stage1_leaderboard_sha": "b21b4cfce5a0917990206a954402c7662a9055d6b6fd150c89c4364a8dee6ff6",
        "stage2_leaderboard_sha": "1306d0a77cc1ae9d28fcc4f78ba55dd6bf4b5603391f3d9b0c345bbd6fde9501",
        "drums_midi_sha": "deac02f8161875f0af2201dad5c91d32d95e22bc83c78e86974fdc63728dcbbf",
        "ref_stem_sha": "bbbc1e461c937d7bab1a5fad8cde9f26aee7234a37ebce9f93f0d40575639cd0",
    },
]


def compute_profile_id(profile_body: dict) -> str:
    excluded = {"profile_id", "render_sha256_canonical_replay"}
    body = {k: v for k, v in profile_body.items() if k not in excluded}
    canon = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(uuid.NAMESPACE_URL, canon))


def emit_song(s: dict) -> dict:
    sha16 = s["song_sha16"]
    profile_dir = ROOT / f"data/v4/profiles/{sha16}"
    stem_dir_rel = f"data/v3_spine/{sha16}/operator_section/rc9_6stem/drums.wav"
    stage1_dir_rel = f"data/v4/profiles/{sha16}/drums_sweep_stage1"
    stage2_dir_rel = f"data/v4/profiles/{sha16}/drums_sweep_stage2"
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
                "centroid_rmse": 0.25,
                "embedding_cos": 0.25,
                "mel_l1": 0.5,
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
                "channel": 10,
                "path": str(midi_path),
                "sha256": s["drums_midi_sha"],
            },
            "env_pin_sha256_replay_time_7key": ENV_PIN_SHA,
            "reference_stem": {
                "path": str(ROOT / stem_dir_rel),
                "sha256": s["ref_stem_sha"],
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
            "cycle": 57,
            "grid_gain": s["gain"],
            "grid_post": s["post"],
            "grid_program": s["program"],
            "grid_reverb_send": s["reverb_send"],
            "preset_rank_stage1": s["preset_rank_stage1"],
            "render_sha256_in_sweep": s["render_sha_in_sweep"],
            "stage": "stage2_fine_fit_c56",
        },
        "song_sha16": sha16,
    }
    profile_id = compute_profile_id(body)
    body["profile_id"] = profile_id

    # Run replay proof BEFORE writing profile to populate canonical replay SHA.
    tmp_out = ROOT / f"data/v4/_run/_c57_replay_probe_{sha16}.json"
    report = prove_replay(body, midi_path, out_json=tmp_out)
    canonical_replay_sha = report["run1_sha256"]
    body["render_sha256_canonical_replay"] = canonical_replay_sha

    # Recompute profile_id AFTER populating replay sha? No — excluded from
    # pre-image per compute_profile_id, so id is stable.

    profile_path = profile_dir / "drums.json"
    with open(profile_path, "w") as f:
        json.dump(body, f, sort_keys=True, separators=(",", ":"))
    profile_sha = sha256_of_file(profile_path)

    # Move replay proof to canonical name
    proof_path = profile_dir / "drums.replay_proof.json"
    proof_body = json.loads(tmp_out.read_text())
    proof_body["profile_id"] = profile_id
    proof_body["profile_sha256"] = profile_sha
    with open(proof_path, "w") as f:
        json.dump(proof_body, f, sort_keys=True, indent=2)
    proof_sha = sha256_of_file(proof_path)
    tmp_out.unlink()

    # Family verdict: SF2_CONFIRMED under c47 OPT1-extended acceptance
    # (best-of-search across families per binding spec).
    verdict_body = {
        "song_sha16": sha16,
        "instrument": "drums",
        "family": "sf2",
        "verdict": "SF2_CONFIRMED",
        "verdict_cycle": 57,
        "authority": "c47 operator omnibus adjudication 2026-09-05 point (3): "
                    "OPT1 EXTENDED campaign-wide (best-of-search across families "
                    "under distance semantics; SF2_CONFIRMED lifted).",
        "objective_scores": body["objective_scores"],
        "profile_id": profile_id,
        "profile_sha256": profile_sha,
        "replay_proof_sha256": proof_sha,
        "render_sha256_canonical_replay": canonical_replay_sha,
        "honest_disclosure": {
            "embedding_cos_vggish": s["embedding_cos_vggish"],
            "distance_semantics_note": "Under 2026-09-04 operator ruling, "
                "embedding_cos_vggish is a DISTANCE metric; lower is better. "
                "0.40 upper-bound rules OUT only degenerate candidates.",
            "best_of_search_across_families": True,
        },
        "env_pin_sha256": ENV_PIN_SHA,
    }
    verdict_path = profile_dir / "drums_family_verdict.json"
    with open(verdict_path, "w") as f:
        json.dump(verdict_body, f, sort_keys=True, indent=2)
    verdict_sha = sha256_of_file(verdict_path)

    return {
        "song_sha16": sha16,
        "song_name": s["song_name"],
        "profile_id": profile_id,
        "profile_sha256": profile_sha,
        "replay_proof_sha256": proof_sha,
        "render_sha256_canonical_replay": canonical_replay_sha,
        "family_verdict_sha256": verdict_sha,
        "verdict": "SF2_CONFIRMED",
        "embedding_cos_vggish": s["embedding_cos_vggish"],
        "top1_program": s["program"],
        "top1_preset": GM_DRUMS_NAMES[s["program"]],
        "top1_composite": s["composite"],
    }


results = {}
for s in SONGS:
    r = emit_song(s)
    results[r["song_sha16"]] = r
    print(f"[{r['song_name']}] verdict={r['verdict']} profile_sha={r['profile_sha256'][:16]}… "
          f"replay_proof_sha={r['replay_proof_sha256'][:16]}… "
          f"top1={r['top1_program']}({r['top1_preset']}) composite={r['top1_composite']:.2f} "
          f"emb_cos_dist={r['embedding_cos_vggish']:.4f}")

with open(ROOT / "data/v4/_run/c57_drums_emit_results.json", "w") as f:
    json.dump(results, f, sort_keys=True, indent=2)
print(f"\nResults summary: data/v4/_run/c57_drums_emit_results.json")
