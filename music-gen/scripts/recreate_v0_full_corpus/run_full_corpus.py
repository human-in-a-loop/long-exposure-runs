#!/usr/bin/python3
# ---
# created: 2026-08-29T12:20:00Z
# cycle: 39
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/full-corpus-recreation
# fork: c320de981fda
# clone: 0
# ---
"""37-song full-corpus driver — READ-ONLY import of c37 clone-0
`scripts.recreate_v0.run_pipeline`.

Per song (canonical SHA order): runs the c37 8-stage pipeline twice
into isolated temp-dir roots, asserts byte-determinism on 4 anchors,
measures M-TEX-1/panel on (original, bare) AND (original, effects),
and writes per-song result JSON + stage manifest.

Per-song wall-clock early-exit at 6x c38 clone-2 per-song per-run
median (~82.2 s * 6 = 493.2 s). Silent song drops FORBIDDEN.

Resumable: skips per_stage runs whose pipeline_run.json shows
failed_stage=null and all four anchors already exist.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

assert sys.executable == "/usr/bin/python3", sys.executable

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1735689600")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DATA_ROOT = REPO_ROOT / "data" / "recreate_v0_full_corpus"
PER_SONG_ROOT = DATA_ROOT / "per_song"
CHOSEN_JSON = DATA_ROOT / "chosen_songs_full.json"
RUBRIC_HASH = (DATA_ROOT / "rubric_hash.txt").read_text().strip()

# c38 clone-2 published per-run median wall-clock ~82.2 s (from run_batch.log).
# Early-exit multiplier: 6x. Guard against silent drops.
C38_CLONE2_MEDIAN_WALL_S = 82.2
EARLY_EXIT_WALL_S = 6.0 * C38_CLONE2_MEDIAN_WALL_S  # 493.2 s

ANCHOR_FILES = [
    # c37 recreate_v0 scripts
    "scripts/recreate_v0/__init__.py",
    "scripts/recreate_v0/select_song.py",
    "scripts/recreate_v0/run_all.py",
    "scripts/recreate_v0/run_pipeline.py",
    # c37 data anchors
    "data/recreate_v0/rubric_hash.txt",
    "data/recreate_v0/verdict.json",
    "data/recreate_v0/chosen_song.json",
    # c37 report
    "docs/recreate_v0_first_real_audio_report.md",
    # c38 clone-2 scripts
    "scripts/recreate_v0_batch/__init__.py",
    "scripts/recreate_v0_batch/select_songs.py",
    "scripts/recreate_v0_batch/run_batch.py",
    "scripts/recreate_v0_batch/write_report.py",
    # c38 clone-2 data anchors
    "data/recreate_v0_batch/rubric_hash.txt",
    "data/recreate_v0_batch/verdict.json",
    "data/recreate_v0_batch/chosen_songs.json",
    "data/recreate_v0_batch/cross_band_table.tsv",
    "data/recreate_v0_batch/cross_band_correlation.json",
    # c38 clone-2 reports
    "docs/recreate_v0_batch_rubric.md",
    "docs/recreate_v0_batch_report.md",
    # c38 clone-0 v1 report (document-path reference only)
    "docs/ear_real_label_training_v1_report.md",
    # c38 clone-1 reports (document-path reference only)
    "docs/score_bridge_real_audio_quantization_report.md",
    "docs/score_bridge_real_audio_quantization_normalizer_v2_report.md",
    # c8 score bridge
    "scripts/score/bridge.py",
    # c9 effects chain
    "scripts/tex/render_effects_layered.py",
]

DET_ANCHORS = [
    "06_score/merged.musicxml",
    "06_score/merged.midi",
    "07_render/bare_midi.wav",
    "07_render/effects.wav",
]


def sha256_bytes(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_anchors() -> dict:
    return {rel: (sha256_bytes(REPO_ROOT / rel) if (REPO_ROOT / rel).exists()
                  else "MISSING")
            for rel in ANCHOR_FILES}


def run_pipeline_subprocess(song_relpath: str, out_root: Path,
                            timeout_s: float) -> dict:
    """Invoke scripts.recreate_v0.run_pipeline.run_pipeline in fresh subprocess.

    Returns {failed_stage, total_wall_seconds, ...} or an error record on
    timeout / crash / early_exit.
    """
    out_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["SOURCE_DATE_EPOCH"] = "1735689600"
    env["TZ"] = "UTC"
    env["LC_ALL"] = "C.UTF-8"
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["REPO_ROOT"] = str(REPO_ROOT)
    env["SONG_RELPATH"] = song_relpath
    env["OUT_ROOT"] = str(out_root)
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            ["/usr/bin/python3", "-c",
             "import sys, os, json, pathlib; "
             "sys.path.insert(0, os.environ['REPO_ROOT']); "
             "from scripts.recreate_v0 import run_pipeline as rp; "
             "song = pathlib.Path(os.environ['REPO_ROOT']) / os.environ['SONG_RELPATH']; "
             "out = pathlib.Path(os.environ['OUT_ROOT']); "
             "res = rp.run_pipeline(song, out); "
             "(out / 'pipeline_run.json').write_text(json.dumps(res, indent=2, sort_keys=True) + '\\n'); "
             "print(json.dumps({'failed_stage': res['failed_stage'], 'total_wall_seconds': res['total_wall_seconds']}))"
            ],
            env=env, capture_output=True, text=True, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return {"failed_stage": "early_exit:wall_clock_exceeded",
                "wall_clock_s_observed": round(time.perf_counter() - t0, 2),
                "wall_clock_s_threshold": timeout_s}
    if proc.returncode != 0:
        return {"failed_stage": "orchestrator_subprocess",
                "returncode": proc.returncode,
                "stderr_tail": proc.stderr[-2000:]}
    try:
        return json.loads((out_root / "pipeline_run.json").read_text())
    except Exception as exc:
        return {"failed_stage": "orchestrator_json_read",
                "error": repr(exc),
                "stderr_tail": proc.stderr[-2000:]}


def measure_panel(original_wav: Path, other_wav: Path, tsv_path: Path) -> dict:
    import numpy as np
    import soundfile as sf
    from scripts.texture.panel import texture_distance
    ya, sra = sf.read(str(original_wav), always_2d=True)
    yb, srb = sf.read(str(other_wav), always_2d=True)
    assert sra == srb, f"sr mismatch {sra} vs {srb}"
    n = min(ya.shape[0], yb.shape[0])
    res = texture_distance(ya[:n], yb[:n], sra)
    keys = ["mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
            "lufs_m_rmse_lu", "embedding_cosine_distance",
            "embedding_rung", "sr_hz", "n_samples_compared"]
    tsv_path.write_text("\t".join(keys) + "\n" +
                        "\t".join(str(res.get(k)) for k in keys) + "\n")
    return {k: res.get(k) for k in keys}


def pipeline_already_ok(per_stage_root: Path) -> bool:
    pr = per_stage_root / "pipeline_run.json"
    if not pr.exists():
        return False
    try:
        data = json.loads(pr.read_text())
    except Exception:
        return False
    if data.get("failed_stage") is not None:
        return False
    return all((per_stage_root / rel).exists() for rel in DET_ANCHORS)


def process_song(song: dict, wall_budget_s: float) -> dict:
    band = song["rating_bucket"]
    relpath = song["relpath"]
    sha16 = song["file_sha256"][:16]
    song_root = PER_SONG_ROOT / str(band) / sha16
    per_stage = song_root / "per_stage"
    run2_root = song_root / "_run2"

    result: dict = {
        "band": band, "relpath": relpath,
        "sha256": song["file_sha256"], "sha16": sha16,
        "canonical_index": song["canonical_index"],
    }

    # Run 1
    if pipeline_already_ok(per_stage):
        print(f"[full] band {band} {sha16} run1: cached OK", flush=True)
        run1 = json.loads((per_stage / "pipeline_run.json").read_text())
        wall1 = run1.get("total_wall_seconds", None)
    else:
        print(f"[full] band {band} {sha16} run1: launching (budget {wall_budget_s:.0f}s)...",
              flush=True)
        t0 = time.perf_counter()
        run1 = run_pipeline_subprocess(relpath, per_stage, wall_budget_s)
        wall1 = round(time.perf_counter() - t0, 2)
        print(f"[full] band {band} {sha16} run1: {wall1}s "
              f"failed_stage={run1.get('failed_stage')}", flush=True)
    result["run1_failed_stage"] = run1.get("failed_stage")
    result["run1_wall_clock_s"] = wall1

    # Determinism run 2 (only if run 1 succeeded)
    determinism: dict = {"attempted": False}
    if run1.get("failed_stage") is None:
        if pipeline_already_ok(run2_root):
            print(f"[full] band {band} {sha16} run2: cached OK", flush=True)
            run2 = json.loads((run2_root / "pipeline_run.json").read_text())
            wall2 = run2.get("total_wall_seconds", None)
        else:
            print(f"[full] band {band} {sha16} run2: launching...", flush=True)
            if run2_root.exists():
                shutil.rmtree(run2_root)
            t0 = time.perf_counter()
            run2 = run_pipeline_subprocess(relpath, run2_root, wall_budget_s)
            wall2 = round(time.perf_counter() - t0, 2)
            print(f"[full] band {band} {sha16} run2: {wall2}s "
                  f"failed_stage={run2.get('failed_stage')}", flush=True)
        determinism["attempted"] = True
        determinism["run2_failed_stage"] = run2.get("failed_stage")
        result["run2_wall_clock_s"] = wall2

        det_pairs: dict = {}
        all_equal = True
        for rel in DET_ANCHORS:
            a = per_stage / rel
            b = run2_root / rel
            if a.exists() and b.exists():
                ha, hb = sha256_bytes(a), sha256_bytes(b)
                det_pairs[rel] = {"run1": ha, "run2": hb, "equal": (ha == hb)}
                if ha != hb:
                    all_equal = False
            else:
                det_pairs[rel] = {"run1": "MISSING" if not a.exists() else "present",
                                  "run2": "MISSING" if not b.exists() else "present",
                                  "equal": False}
                all_equal = False
        determinism["per_anchor"] = det_pairs
        determinism["all_deterministic_anchors_equal"] = all_equal
    result["determinism"] = determinism

    # Panels
    panels: dict = {"attempted": False}
    if run1.get("failed_stage") is None:
        panels["attempted"] = True
        orig = per_stage / "01_decode" / "original_30s.wav"
        bare = per_stage / "07_render" / "bare_midi.wav"
        eff = per_stage / "07_render" / "effects.wav"
        try:
            panels["original_vs_bare"] = measure_panel(
                orig, bare, song_root / "panel_original_vs_bare.tsv")
        except Exception as exc:
            panels["original_vs_bare"] = {"error": repr(exc)}
        try:
            panels["original_vs_effects"] = measure_panel(
                orig, eff, song_root / "panel_original_vs_effects.tsv")
        except Exception as exc:
            panels["original_vs_effects"] = {"error": repr(exc)}
    result["panels"] = panels

    # Compact per-song stage manifest
    stage_manifest = {
        "song_sha16": sha16, "band": band, "relpath": relpath,
        "canonical_index": song["canonical_index"],
        "run1_failed_stage": run1.get("failed_stage"),
        "run1_wall_clock_s": wall1,
        "run2_failed_stage": run2.get("failed_stage") if determinism["attempted"] else None,
        "run2_wall_clock_s": result.get("run2_wall_clock_s"),
        "stages_run1": run1.get("stages", []),
        "pretty_midi_fallback_used_run1": any(
            s.get("xml_to_midi_status") == "fallback_pretty_midi_concat"
            for s in run1.get("stages", []) if isinstance(s, dict)
        ),
        "early_exit_threshold_s": wall_budget_s,
    }
    (song_root / "stage_manifest.json").write_text(
        json.dumps(stage_manifest, indent=2, sort_keys=True) + "\n")

    (song_root / "per_song_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    t_all = time.perf_counter()
    chosen = json.loads(CHOSEN_JSON.read_text())
    songs = chosen["chosen_songs"]
    print(f"[full] processing {len(songs)} songs with early-exit budget "
          f"{EARLY_EXIT_WALL_S:.1f}s per run", flush=True)

    anchors_pre = snapshot_anchors()

    results = []
    for song in songs:
        try:
            r = process_song(song, EARLY_EXIT_WALL_S)
        except Exception as exc:
            r = {"band": song["rating_bucket"], "relpath": song["relpath"],
                 "sha256": song["file_sha256"], "sha16": song["file_sha256"][:16],
                 "canonical_index": song["canonical_index"],
                 "run1_failed_stage": "driver_exception",
                 "driver_error": repr(exc),
                 "determinism": {"attempted": False},
                 "panels": {"attempted": False}}
        results.append(r)

    anchors_post = snapshot_anchors()
    anchor_diff = {k: (anchors_pre.get(k), anchors_post.get(k))
                   for k in anchors_pre
                   if anchors_pre.get(k) != anchors_post.get(k)}
    (DATA_ROOT / "anchor_preservation.json").write_text(json.dumps({
        "anchors_pre": anchors_pre,
        "anchors_post": anchors_post,
        "changed": anchor_diff,
        "unchanged": (len(anchor_diff) == 0),
        "n_anchors": len(anchors_pre),
    }, indent=2, sort_keys=True) + "\n")

    (DATA_ROOT / "all_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n")

    total_wall = round(time.perf_counter() - t_all, 2)
    print(f"[full] done in {total_wall}s; n_songs={len(results)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
