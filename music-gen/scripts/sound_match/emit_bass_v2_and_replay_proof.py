#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 4
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-profile-v2-emitted
# ---
"""c4 conditional: emit bass_v2.json sibling profile from c3 top-1-by-composite
tuple (prog 33 gain 0.5 rev 0.3 post EQ_only), run fresh sf2 replay proof
under c3 env pin, populate render_sha256_canonical_replay, and rewrite the
profile with the canonical replay SHA. c1 hygiene: bass.json READ-ONLY.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
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

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(f"require /usr/bin/python3 (got {sys.executable})")

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.profile_writer import build_profile, write_profile  # noqa: E402
from scripts.sound_match.replay_proof import prove_replay  # noqa: E402


SONG_SHA16 = "31a164f845f8e27e"
SF2_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
SF2_SHA256 = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
REF_STEM_SHA = "1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd"
BASS_MIDI_PATH = Path(f"data/v4/profiles/{SONG_SHA16}/bass_sweep_stage1/inputs/bass.mid")
BASS_MIDI_SHA = "4863ca285c7db513c8bfc22da5e35e65036b0ecad2538a6d9794c80eb15f8ac9"
STAGE2B_LEADERBOARD = Path(f"data/v4/profiles/{SONG_SHA16}/bass_stage2b/leaderboard.tsv")
STAGE2B_MANIFEST = Path(f"data/v4/profiles/{SONG_SHA16}/bass_stage2b/run_manifest.json")
STAGE1_LEADERBOARD = Path(f"data/v4/profiles/{SONG_SHA16}/bass_sweep_stage1/leaderboard.tsv")
V2_PROFILE_OUT = Path(f"data/v4/profiles/{SONG_SHA16}/bass_v2.json")
V2_REPLAY_PROOF_OUT = Path(f"data/v4/profiles/{SONG_SHA16}/bass_v2.replay_proof.json")


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_top1_by_composite(path: Path) -> dict:
    with open(path) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for r in rows:
        r["composite"] = float(r["composite"])
        r["program"] = int(r["program"])
        r["gain"] = float(r["gain"])
        r["reverb_send"] = float(r["reverb_send"])
        r["mel_l1_db"] = float(r["mel_l1_db"])
        r["spectral_centroid_rmse_hz"] = float(r["spectral_centroid_rmse_hz"])
        r["embedding_cos_vggish"] = float(r["embedding_cos_vggish"])
    return sorted(rows, key=lambda r: r["composite"])[0]


def build_v2_profile(top1: dict, canonical_replay_sha: str | None) -> dict:
    identity = {
        "bank": 0,
        "preset_name": top1["preset_name"],
        "program": top1["program"],
        "sf2_path": SF2_PATH,
        "sf2_sha256": SF2_SHA256,
    }
    params = {
        "compressor": None,
        "eq_curve_gains_db": None,  # sweep-time EQ v2 gains not persisted in leaderboard TSV; replay uses raw sf2 dispatch (see replay._replay_sf2)
        "gain": top1["gain"],
        "post_processing": top1["post"],
        "reverb_send": top1["reverb_send"],
        "sample_rate": 44100,
    }
    deps_sha256 = {
        "bass_midi_excerpt": BASS_MIDI_SHA,
        "reference_stem": REF_STEM_SHA,
        "sf2": SF2_SHA256,
    }
    objective_scores = {
        "composite": top1["composite"],
        "embedding_cos_vggish": top1["embedding_cos_vggish"],
        "embedding_rung": "vggish",
        "mel_l1_db": top1["mel_l1_db"],
        "rank_stage1": int(top1["preset_rank_stage1"]) if top1.get("preset_rank_stage1", "").strip().lstrip("-").isdigit() else None,
        "rank_stage2b": 1,
        "spectral_centroid_rmse_hz": top1["spectral_centroid_rmse_hz"],
        "weights_frozen": {
            "centroid_rmse": 0.25,
            "embedding_cos": 0.25,
            "mel_l1": 0.5,
        },
    }
    search_metadata = {
        "config_hash": top1["config_hash"],
        "cycle": 3,
        "grid_size": 216,
        "instrument": "bass",
        "render_sha256_in_sweep": top1["render_sha256"],
        "song_sha16": SONG_SHA16,
        "stage1_top_k": 5,
        "sweep_stage": "2b",
    }
    provenance = {
        "stage1_leaderboard_path": str(STAGE1_LEADERBOARD.resolve()),
        "stage1_leaderboard_sha256": _sha256_of_file(STAGE1_LEADERBOARD),
        "stage2b_leaderboard_path": str(STAGE2B_LEADERBOARD.resolve()),
        "stage2b_leaderboard_sha256": _sha256_of_file(STAGE2B_LEADERBOARD),
        "stage2b_run_manifest_path": str(STAGE2B_MANIFEST.resolve()),
        "stage2b_run_manifest_sha256": _sha256_of_file(STAGE2B_MANIFEST),
        "supersedes_profile_v1_id": "56cdc50a-dbbc-5a49-afc9-f3cf93a25c7d",
        "supersedes_profile_v1_sha256": "11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9",
    }
    return build_profile(
        song_sha16=SONG_SHA16,
        instrument="bass",
        family="sf2",
        identity=identity,
        params=params,
        deps_sha256=deps_sha256,
        objective_scores=objective_scores,
        search_metadata=search_metadata,
        provenance=provenance,
        render_sha256_canonical_replay=canonical_replay_sha,
    )


def main() -> int:
    top1 = _read_top1_by_composite(STAGE2B_LEADERBOARD)
    print(f"top-1 by composite: prog={top1['program']} gain={top1['gain']} "
          f"rev={top1['reverb_send']} post={top1['post']} comp={top1['composite']:.3f}")

    # Phase 1: build v2 profile without canonical replay field, so we can invoke replay
    profile_stage1 = build_v2_profile(top1, canonical_replay_sha=None)
    profile_id_stage1 = profile_stage1["profile_id"]

    # Phase 2: run fresh replay proof against bass.mid
    tmp_report_path = V2_REPLAY_PROOF_OUT
    report = prove_replay(profile_stage1, BASS_MIDI_PATH, out_json=tmp_report_path)
    canonical_replay_sha = report["run1_sha256"]
    print(f"replay proof verdict={report['verdict']} run1_sha256={canonical_replay_sha}")
    print(f"env_pin_sha256 (replay_proof, 7-key)={report['env_pin_sha256']}")

    # Phase 3: rebuild v2 with canonical_replay_sha populated; profile_id invariant
    profile_final = build_v2_profile(top1, canonical_replay_sha=canonical_replay_sha)
    assert profile_final["profile_id"] == profile_id_stage1, (
        f"profile_id changed: {profile_id_stage1} -> {profile_final['profile_id']}"
    )
    write_profile(profile_final, V2_PROFILE_OUT)
    v2_sha = _sha256_of_file(V2_PROFILE_OUT)
    print(f"bass_v2.json written; sha256={v2_sha} profile_id={profile_final['profile_id']}")

    # Sanity: c2 bass.json byte-identical (READ-ONLY)
    c2_sha = _sha256_of_file(Path(f"data/v4/profiles/{SONG_SHA16}/bass.json"))
    assert c2_sha == "11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9", (
        f"c2 bass.json drifted! sha={c2_sha}"
    )
    print(f"c2 bass.json sha byte-identical OK ({c2_sha})")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
