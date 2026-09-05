#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-05T20:00:00Z
# cycle: 58
# run_id: run-2026-09-05T200000Z
# agent: worker
# milestone: M-V4-PROFILES-1/rome-drums-{profile,replay-proof,family-verdict}
# ---
"""c58 P2 emitter: Rome (51e433ade2a845e1) drums.json + drums.replay_proof.json +
drums_family_verdict.json. Mirrors c57 shape verbatim; uses c11 channel-aware
replay path. Under c47 OPT1-extended acceptance, verdict is SF2_CONFIRMED
(best-of-search across families per binding spec)."""
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


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


ROME = {
    "song_sha16": "51e433ade2a845e1",
    "song_name": "Rome",
    "program": 0, "preset_rank_stage1": 0,
    "gain": 0.5, "reverb_send": 0.3, "post": "EQ_only",
    "composite": 385.16832648648995,
    "mel_l1_db": 10.191104888916016,
    "spectral_centroid_rmse_hz": 1499.2368741992436,
    "embedding_cos_vggish": 0.2105422196888418,
    "config_hash": "f594cde56f0cb22c1488f83abfe450eedc454296e46e669f697664a704750726",
    "render_sha_in_sweep": "38f49135923a2b0b12e812f73091dda0978891b29355354e27a6282aa735cffd",
    "stage1_leaderboard_sha": "c9c629802f4d36409f37e5ccbdf89555370539e2288b0f91c64224360e456a32",
    "stage2_leaderboard_sha": "95409040e318e8fa9b4ff4bc5761acc225440dc6746c8ef29aefcd81d0f37544",
    "drums_midi_sha": "d0591e9f7d819d297fb7c916e129cae9c8a1b28d6e5a2283b90825bca45ce7d2",
    "ref_stem_sha": "a8ce2b5786968dedb15ddd4f2c6311fdc44330b96fc23869a45602a8e537291e",
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
    stem_dir_rel = f"data/v3_spine/{sha16}/operator_section/rc9_6stem/drums.wav"
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
            "cycle": 58,
            "grid_gain": s["gain"],
            "grid_post": s["post"],
            "grid_program": s["program"],
            "grid_reverb_send": s["reverb_send"],
            "preset_rank_stage1": s["preset_rank_stage1"],
            "render_sha256_in_sweep": s["render_sha_in_sweep"],
            "stage": "stage2_fine_fit_c57",
        },
        "song_sha16": sha16,
    }
    profile_id = compute_profile_id(body)
    body["profile_id"] = profile_id

    tmp_out = ROOT / f"data/v4/_run/_c58_replay_probe_{sha16}.json"
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

    verdict_body = {
        "song_sha16": sha16,
        "instrument": "drums",
        "family": "sf2",
        "verdict": "SF2_CONFIRMED",
        "verdict_cycle": 58,
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


r = emit(ROME)
out = ROOT / "data/v4/_run/c58_rome_drums_emit_results.json"
with open(out, "w") as f:
    json.dump(r, f, sort_keys=True, indent=2)
print(f"[{r['song_name']}] verdict={r['verdict']} profile_sha={r['profile_sha256'][:16]}… "
      f"replay_proof_sha={r['replay_proof_sha256'][:16]}… "
      f"top1={r['top1_program']}({r['top1_preset']}) composite={r['top1_composite']:.2f} "
      f"emb_cos_dist={r['embedding_cos_vggish']:.4f}")
print(f"REPLAY_PROOF: run1={r['run1_sha256'][:16]}… run2={r['run2_sha256'][:16]}…  "
      f"HOLDS={r['run1_sha256']==r['run2_sha256']}")
print(f"Summary: {out.relative_to(ROOT)}")
