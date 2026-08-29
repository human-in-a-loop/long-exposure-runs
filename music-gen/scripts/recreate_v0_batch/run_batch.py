#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T10:38:00Z
# cycle: 38
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/second-real-audio-batch
# fork: 33a2a8003c84
# clone: 2
# ---
"""5-song batch driver — reuses c37 clone-0 `run_pipeline` READ-ONLY.

For each song in `data/recreate_v0_batch/chosen_songs.json`:
  - Runs pipeline twice into
    data/recreate_v0_batch/per_song/<band>/<sha16>/per_stage/  (run 1)
    data/recreate_v0_batch/per_song/<band>/<sha16>/_run2/       (run 2)
  - Compares SHA-256 across the 4 deterministic anchors per song.
  - Measures M-TEX-1/panel on (original, bare) AND (original, effects).
  - Writes per-song verdict record.

Aggregates:
  - data/recreate_v0_batch/cross_band_table.tsv
  - data/recreate_v0_batch/cross_band_correlation.json
  - data/recreate_v0_batch/verdict.json
  - data/recreate_v0_batch/anchor_preservation.json

Resumable: skips per_stage runs whose pipeline_run.json shows failed_stage=null
and all four anchors already exist.
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

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DATA_ROOT = REPO_ROOT / "data" / "recreate_v0_batch"
PER_SONG_ROOT = DATA_ROOT / "per_song"

RUBRIC_HASH = (DATA_ROOT / "rubric_hash.txt").read_text().strip()

ANCHOR_FILES = [
    "scripts/ingest/chunker.py",
    "scripts/classifier/tagger.py",
    "scripts/classifier/sidecar_nonfactor.py",
    "scripts/separation/run_htdemucs.py",
    "scripts/transcribe/basic_pitch_baseline.py",
    "scripts/transcribe/_bp_call.py",
    "scripts/score/bridge.py",
    "scripts/tex/render_bare_midi.py",
    "scripts/tex/render_effects_layered.py",
    "scripts/texture/panel.py",
    "scripts/ear/features.py",
    "scripts/ear/model.py",
    # c37 recreate_v0 stage scripts
    "scripts/recreate_v0/__init__.py",
    "scripts/recreate_v0/select_song.py",
    "scripts/recreate_v0/run_all.py",
    "scripts/recreate_v0/run_pipeline.py",
    # c37 data anchors
    "data/recreate_v0/rubric_hash.txt",
    "data/recreate_v0/verdict.json",
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


def run_pipeline_subprocess(song_relpath: str, out_root: Path) -> dict:
    """Invoke scripts.recreate_v0.run_pipeline.run_pipeline in a fresh subprocess."""
    out_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["REPO_ROOT"] = str(REPO_ROOT)
    env["SONG_RELPATH"] = song_relpath
    env["OUT_ROOT"] = str(out_root)
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
        env=env, capture_output=True, text=True,
    )
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


def process_song(song: dict) -> dict:
    band = song["band"]
    relpath = song["relpath"]
    sha16 = song["sha256"][:16]
    song_root = PER_SONG_ROOT / str(band) / sha16
    per_stage = song_root / "per_stage"
    run2_root = song_root / "_run2"

    result: dict = {"band": band, "relpath": relpath, "sha256": song["sha256"],
                    "sha16": sha16, "slot_kind": song["slot_kind"]}

    # Run 1
    if pipeline_already_ok(per_stage):
        print(f"[batch] band {band} {sha16} run1: cached OK", flush=True)
        run1 = json.loads((per_stage / "pipeline_run.json").read_text())
    else:
        print(f"[batch] band {band} {sha16} run1: launching...", flush=True)
        t0 = time.perf_counter()
        run1 = run_pipeline_subprocess(relpath, per_stage)
        print(f"[batch] band {band} {sha16} run1: {round(time.perf_counter()-t0,1)}s "
              f"failed_stage={run1.get('failed_stage')}", flush=True)
    result["run1_failed_stage"] = run1.get("failed_stage")

    # Determinism run 2 (only if run 1 succeeded)
    determinism: dict = {"attempted": False}
    if run1.get("failed_stage") is None:
        if pipeline_already_ok(run2_root):
            print(f"[batch] band {band} {sha16} run2: cached OK", flush=True)
            run2 = json.loads((run2_root / "pipeline_run.json").read_text())
        else:
            print(f"[batch] band {band} {sha16} run2: launching...", flush=True)
            if run2_root.exists():
                shutil.rmtree(run2_root)
            t0 = time.perf_counter()
            run2 = run_pipeline_subprocess(relpath, run2_root)
            print(f"[batch] band {band} {sha16} run2: {round(time.perf_counter()-t0,1)}s "
                  f"failed_stage={run2.get('failed_stage')}", flush=True)
        determinism["attempted"] = True
        determinism["run2_failed_stage"] = run2.get("failed_stage")

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

    (song_root / "per_song_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def aggregate_cross_band_table(results: list) -> Path:
    keys = ["band", "song_sha16",
            "mel_l1_db_bare", "mel_l1_db_effects", "mel_l1_db_delta",
            "spectral_centroid_rmse_hz_bare", "spectral_centroid_rmse_hz_effects",
            "spectral_centroid_rmse_hz_delta",
            "rms_env_rmse_bare", "rms_env_rmse_effects", "rms_env_rmse_delta",
            "lufs_m_rmse_bare", "lufs_m_rmse_effects", "lufs_m_rmse_delta"]
    lines = ["\t".join(keys)]
    for r in results:
        p = r.get("panels", {})
        pb = p.get("original_vs_bare", {}) or {}
        pe = p.get("original_vs_effects", {}) or {}

        def _delta(k):
            b = pb.get(k)
            e = pe.get(k)
            if isinstance(b, (int, float)) and isinstance(e, (int, float)):
                return b - e
            return None

        row = [
            str(r["band"]), r["sha16"],
            str(pb.get("mel_l1_db")), str(pe.get("mel_l1_db")),
            str(_delta("mel_l1_db")),
            str(pb.get("spectral_centroid_rmse_hz")),
            str(pe.get("spectral_centroid_rmse_hz")),
            str(_delta("spectral_centroid_rmse_hz")),
            str(pb.get("rms_env_rmse")), str(pe.get("rms_env_rmse")),
            str(_delta("rms_env_rmse")),
            str(pb.get("lufs_m_rmse_lu")), str(pe.get("lufs_m_rmse_lu")),
            str(_delta("lufs_m_rmse_lu")),
        ]
        lines.append("\t".join(row))
    p = DATA_ROOT / "cross_band_table.tsv"
    p.write_text("\n".join(lines) + "\n")
    return p


def compute_correlations(results: list) -> Path:
    """Pearson + Spearman of (band, metric_delta) for four families, n=5."""
    import math
    xs = [r["band"] for r in results]

    def _extract(delta_key):
        ys = []
        for r in results:
            p = r.get("panels", {})
            pb = p.get("original_vs_bare", {}) or {}
            pe = p.get("original_vs_effects", {}) or {}
            b = pb.get(delta_key)
            e = pe.get(delta_key)
            if isinstance(b, (int, float)) and isinstance(e, (int, float)):
                ys.append(b - e)
            else:
                ys.append(None)
        return ys

    def _pearson(a, b):
        pairs = [(x, y) for x, y in zip(a, b) if y is not None]
        if len(pairs) < 3:
            return None
        n = len(pairs)
        xs2 = [p[0] for p in pairs]
        ys2 = [p[1] for p in pairs]
        mx = sum(xs2) / n
        my = sum(ys2) / n
        num = sum((x - mx) * (y - my) for x, y in pairs)
        dx = math.sqrt(sum((x - mx) ** 2 for x in xs2))
        dy = math.sqrt(sum((y - my) ** 2 for y in ys2))
        if dx == 0 or dy == 0:
            return None
        return num / (dx * dy)

    def _spearman(a, b):
        pairs = [(x, y) for x, y in zip(a, b) if y is not None]
        if len(pairs) < 3:
            return None
        xs2 = [p[0] for p in pairs]
        ys2 = [p[1] for p in pairs]

        def _ranks(vals):
            order = sorted(range(len(vals)), key=lambda i: vals[i])
            ranks = [0.0] * len(vals)
            i = 0
            while i < len(vals):
                j = i
                while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
                    j += 1
                r = (i + j) / 2.0 + 1.0
                for k in range(i, j + 1):
                    ranks[order[k]] = r
                i = j + 1
            return ranks
        rx = _ranks(xs2)
        ry = _ranks(ys2)
        return _pearson(rx, ry)

    families = {
        "mel_l1_db": _extract("mel_l1_db"),
        "spectral_centroid_rmse_hz": _extract("spectral_centroid_rmse_hz"),
        "rms_env_rmse": _extract("rms_env_rmse"),
        "lufs_m_rmse_lu": _extract("lufs_m_rmse_lu"),
    }
    out = {}
    for name, ys in families.items():
        out[name] = {
            "n": sum(1 for y in ys if y is not None),
            "band_values": xs,
            "delta_values": ys,
            "pearson_r": _pearson(xs, ys),
            "spearman_rho": _spearman(xs, ys),
            "n_too_small_caveat":
                "n=5; correlation is exploratory only, not inferentially valid",
        }
    p = DATA_ROOT / "cross_band_correlation.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return p


def compute_verdict(results: list, anchors_unchanged: bool) -> dict:
    n_ok = sum(1 for r in results if r["run1_failed_stage"] is None)
    n_det_ok = sum(1 for r in results
                   if r["determinism"].get("all_deterministic_anchors_equal"))
    n_positive_delta = 0
    per_song_findings = []
    for r in results:
        p = r.get("panels", {})
        pb = p.get("original_vs_bare", {}) or {}
        pe = p.get("original_vs_effects", {}) or {}
        b = pb.get("mel_l1_db")
        e = pe.get("mel_l1_db")
        delta = None
        if isinstance(b, (int, float)) and isinstance(e, (int, float)):
            delta = b - e
        if delta is not None and delta > 0:
            n_positive_delta += 1
        per_song_findings.append({
            "band": r["band"], "sha16": r["sha16"], "relpath": r["relpath"],
            "run1_failed_stage": r["run1_failed_stage"],
            "byte_det_x2": r["determinism"].get("all_deterministic_anchors_equal", False),
            "mel_l1_db_delta_bare_minus_effects": delta,
            "delta_positive": (delta is not None and delta > 0),
        })
    n = len(results)
    if n_ok < n:
        verdict = "BATCH_FAILS"
        reason = f"{n - n_ok}/{n} songs failed a pipeline stage"
    elif n_det_ok < n or n_positive_delta < n:
        verdict = "BATCH_PARTIAL"
        reason = (f"pipeline 5/5 OK; byte-det {n_det_ok}/{n}; "
                  f"positive_mel_delta {n_positive_delta}/{n}")
    else:
        verdict = "BATCH_LANDS"
        reason = "5/5 pipeline OK, 20/20 byte-det anchors, 5/5 positive mel delta"

    return {
        "verdict": verdict,
        "reason": reason,
        "n_songs": n,
        "n_pipeline_ok": n_ok,
        "n_byte_det_x2": n_det_ok,
        "n_positive_mel_delta": n_positive_delta,
        "per_song_findings": per_song_findings,
        "anchors_unchanged": anchors_unchanged,
        "rubric_hash": RUBRIC_HASH,
        "rubric_verdicts": ["BATCH_LANDS", "BATCH_PARTIAL", "BATCH_FAILS"],
        "milestone": "M-RECREATE-1/second-real-audio-batch",
        "fork": "33a2a8003c84",
        "clone": 2,
        "cycle": 38,
        "run_id": "run-2026-08-28T040704Z",
    }


def main() -> int:
    t_all = time.perf_counter()
    chosen = json.loads((DATA_ROOT / "chosen_songs.json").read_text())
    songs = chosen["chosen_songs"]

    anchors_pre = snapshot_anchors()

    results = []
    for song in songs:
        r = process_song(song)
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

    aggregate_cross_band_table(results)
    compute_correlations(results)

    verdict_payload = compute_verdict(results, len(anchor_diff) == 0)
    verdict_payload["total_wall_seconds"] = round(time.perf_counter() - t_all, 3)
    (DATA_ROOT / "verdict.json").write_text(
        json.dumps(verdict_payload, indent=2, sort_keys=True) + "\n")

    print(f"[batch] VERDICT: {verdict_payload['verdict']} — "
          f"{verdict_payload['reason']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
