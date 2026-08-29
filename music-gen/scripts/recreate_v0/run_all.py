#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T08:00:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/first-real-audio
# fork: 675abd086911
# clone: 0
# ---
"""End-to-end driver for M-RECREATE-1/first-real-audio.

Sequence:
    1. select_song    (SHA-256 tiebreak → chosen_song.json)
    2. run_pipeline   (8 stages → per_stage/pipeline_run.json)
    3. Determinism    (rerun pipeline into per_stage/_run2/ and diff
                       bare_midi.wav + effects.wav SHAs)
    4. panel_measure  (M-TEX-1/panel on original-vs-bare & original-vs-effects)
    5. heuristics     (M-HEUR-1 battery on original + effects)
    6. ear_untrained  (M-EAR-1/preparation model on original; label
                       preview_untrained_ear=true, cite cycle-36 EAR_v0_INSUFFICIENT)
    7. anchor_preserve (SHA-manifest of read-only upstream scripts)
    8. verdict        (rubric-frozen 3-way + rubric_hash embed)
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

DATA_ROOT = REPO_ROOT / "data" / "recreate_v0"
PER_STAGE = DATA_ROOT / "per_stage"

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
]

MEL_DELTA_LANDS_DB = 0.5   # (effects mel < bare mel) - MEL_DELTA_LANDS_DB → LANDS


def sha256_bytes(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_anchors() -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in ANCHOR_FILES:
        p = REPO_ROOT / rel
        out[rel] = sha256_bytes(p) if p.exists() else "MISSING"
    return out


def run_pipeline_once(out_root: Path) -> dict[str, Any]:
    """Run scripts.recreate_v0.run_pipeline as an out-of-process subprocess.

    We keep it in-process where possible for speed but must NOT reuse cached
    torch/tensorflow modules between the two determinism runs. Run as
    subprocess to guarantee a fresh interpreter each time.
    """
    out_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["RECREATE_V0_OUT"] = str(out_root)
    env["OMP_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    # Copy chosen_song.json into out_root's data-analog if run is diverted.
    proc = subprocess.run(
        ["/usr/bin/python3", "-c",
         "import sys, os, json, pathlib; "
         "sys.path.insert(0, os.environ['REPO_ROOT']); "
         "from scripts.recreate_v0 import run_pipeline as rp; "
         "out = pathlib.Path(os.environ['RECREATE_V0_OUT']); "
         "chosen = json.loads((pathlib.Path(os.environ['REPO_ROOT'])/'data/recreate_v0/chosen_song.json').read_text()); "
         "song = pathlib.Path(os.environ['REPO_ROOT']) / chosen['chosen_relpath']; "
         "res = rp.run_pipeline(song, out); "
         "(out / 'pipeline_run.json').write_text(json.dumps(res, indent=2, sort_keys=True) + '\\n'); "
         "print(json.dumps({'failed_stage': res['failed_stage'], 'total_wall_seconds': res['total_wall_seconds']}))",
        ],
        env={**env, "REPO_ROOT": str(REPO_ROOT)},
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return {
            "failed_stage": "orchestrator_subprocess",
            "returncode": proc.returncode,
            "stderr_tail": proc.stderr[-2000:],
        }
    return json.loads((out_root / "pipeline_run.json").read_text())


def read_wav_pair(a: Path, b: Path) -> tuple[Any, Any, int]:
    import numpy as np
    import soundfile as sf
    ya, sra = sf.read(str(a), always_2d=True)
    yb, srb = sf.read(str(b), always_2d=True)
    assert sra == srb, f"sr mismatch: {sra} vs {srb}"
    n = min(ya.shape[0], yb.shape[0])
    return ya[:n], yb[:n], sra


def measure_panel(original_wav: Path, other_wav: Path, tsv_path: Path) -> dict[str, Any]:
    from scripts.texture.panel import texture_distance
    ya, yb, sr = read_wav_pair(original_wav, other_wav)
    res = texture_distance(ya, yb, sr)
    # Write TSV row + header
    keys = ["mel_l1_db", "spectral_centroid_rmse_hz", "rms_env_rmse",
            "lufs_m_rmse_lu", "embedding_cosine_distance",
            "embedding_rung", "sr_hz", "n_samples_compared"]
    header = "\t".join(keys) + "\n"
    row = "\t".join(str(res.get(k)) for k in keys) + "\n"
    tsv_path.write_text(header + row)
    return {k: res.get(k) for k in keys}


def measure_heuristics(original_wav: Path, effects_wav: Path, out_path: Path) -> dict[str, Any]:
    import numpy as np
    import soundfile as sf
    try:
        from scripts.heuristics.battery import battery
    except Exception:
        try:
            from scripts.heuristics.battery import run_battery as battery
        except Exception:
            battery = None
    result: dict[str, Any] = {}
    for label, wav in (("original", original_wav), ("effects_layered", effects_wav)):
        y, sr = sf.read(str(wav), always_2d=True)
        mono = y.mean(axis=1).astype(np.float32)
        if battery is not None:
            try:
                result[label] = battery(mono, sr)
            except Exception as exc:
                result[label] = {"error": repr(exc)}
        else:
            result[label] = {"note": "heuristics.battery.battery not found; skipped"}
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    return result


def measure_ear_untrained(original_wav: Path, out_path: Path) -> dict[str, Any]:
    """Emit preview_untrained_ear preview score with prominent caveat."""
    payload: dict[str, Any] = {
        "preview_untrained_ear": True,
        "caveat": (
            "Cycle-36 M-EAR-1/real-label-training-v0 verdict was "
            "EAR_v0_INSUFFICIENT. This score is a preview number from an "
            "un-calibrated head and MUST NOT influence the recreation verdict."
        ),
        "cycle_36_reference": "M-EAR-1/real-label-training-v0 → EAR_v0_INSUFFICIENT",
    }
    try:
        import numpy as np
        import soundfile as sf
        import torch
        from scripts.ear.features import extract_features
        from scripts.ear.model import CornHead
        from scripts.ear.corn import predict_rank
        y, sr = sf.read(str(original_wav), always_2d=True)
        mono = y.mean(axis=1).astype(np.float32)
        feats = extract_features(mono, sr)
        model = CornHead(feats.shape[-1])
        model.eval()
        with torch.no_grad():
            logits = model(torch.from_numpy(feats.astype("float32")).unsqueeze(0))
        rank = predict_rank(logits).item() + 1  # 1..7
        payload["preview_rank_1_to_7"] = int(rank)
        payload["feat_dim"] = int(feats.shape[-1])
    except Exception as exc:
        payload["preview_error"] = repr(exc)
        payload["preview_rank_1_to_7"] = None
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def main() -> int:
    t_all = time.perf_counter()
    DATA_ROOT.mkdir(parents=True, exist_ok=True)

    # Step 1 — song select (idempotent, force refresh)
    subprocess.run(["/usr/bin/python3",
                    str(REPO_ROOT / "scripts/recreate_v0/select_song.py")],
                   check=True, capture_output=True)
    chosen = json.loads((DATA_ROOT / "chosen_song.json").read_text())

    # Anchor snapshot BEFORE anything runs
    anchors_pre = snapshot_anchors()

    # Step 2 — Run 1
    print("[recreate_v0] pipeline run 1 (primary)…", flush=True)
    run1 = run_pipeline_once(PER_STAGE)
    print("[recreate_v0] run 1 failed_stage:", run1.get("failed_stage"), flush=True)

    # Step 3 — Byte-determinism run 2 (only if run 1 reached stage 7a/b)
    determinism: dict[str, Any] = {"attempted": False}
    if run1.get("failed_stage") is None:
        run2_root = PER_STAGE.parent / "_run2"
        if run2_root.exists():
            shutil.rmtree(run2_root)
        print("[recreate_v0] pipeline run 2 (determinism)…", flush=True)
        run2 = run_pipeline_once(run2_root)
        determinism["attempted"] = True
        determinism["run2_failed_stage"] = run2.get("failed_stage")
        # Compare deterministic-stage SHAs
        anchors = [
            "07_render/bare_midi.wav",
            "07_render/effects.wav",
            "06_score/merged.midi",
            "06_score/merged.musicxml",
        ]
        det_pairs: dict[str, dict[str, str]] = {}
        all_equal = True
        for rel in anchors:
            a = PER_STAGE / rel
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

    # Step 4 — panels (only if run1 succeeded)
    panel_bare = panel_effects = None
    if run1.get("failed_stage") is None:
        try:
            panel_bare = measure_panel(
                PER_STAGE / "01_decode/original_30s.wav",
                PER_STAGE / "07_render/bare_midi.wav",
                DATA_ROOT / "panel_original_vs_bare.tsv",
            )
        except Exception as exc:
            panel_bare = {"error": repr(exc)}
        try:
            panel_effects = measure_panel(
                PER_STAGE / "01_decode/original_30s.wav",
                PER_STAGE / "07_render/effects.wav",
                DATA_ROOT / "panel_original_vs_effects.tsv",
            )
        except Exception as exc:
            panel_effects = {"error": repr(exc)}

    # Step 5 — heuristics
    heur = None
    if run1.get("failed_stage") is None:
        try:
            heur = measure_heuristics(
                PER_STAGE / "01_decode/original_30s.wav",
                PER_STAGE / "07_render/effects.wav",
                DATA_ROOT / "heuristics_scores.json",
            )
        except Exception as exc:
            heur = {"error": repr(exc)}
            (DATA_ROOT / "heuristics_scores.json").write_text(
                json.dumps(heur, indent=2, sort_keys=True) + "\n")

    # Step 6 — ear preview (always emit, even if pipeline failed early)
    original_wav = PER_STAGE / "01_decode/original_30s.wav"
    if original_wav.exists():
        measure_ear_untrained(original_wav, DATA_ROOT / "ear_score_untrained.json")
    else:
        (DATA_ROOT / "ear_score_untrained.json").write_text(json.dumps({
            "preview_untrained_ear": True,
            "preview_rank_1_to_7": None,
            "caveat": "original_30s.wav not produced (stage 01_decode failed)",
        }, indent=2, sort_keys=True) + "\n")

    # Step 7 — anchor preservation
    anchors_post = snapshot_anchors()
    anchor_diff = {k: v for k, v in anchors_post.items() if anchors_pre.get(k) != v}
    (DATA_ROOT / "anchor_preservation.json").write_text(json.dumps({
        "anchors_pre": anchors_pre,
        "anchors_post": anchors_post,
        "changed": anchor_diff,
        "unchanged": len(anchor_diff) == 0,
        "n_anchors": len(anchors_pre),
    }, indent=2, sort_keys=True) + "\n")

    # Step 8 — verdict
    failed_stage = run1.get("failed_stage")
    verdict = "RECREATION_FAILS"
    reason = ""
    if failed_stage is not None:
        verdict = "RECREATION_FAILS"
        reason = f"stage {failed_stage} did not reach status=ok"
    else:
        # Check panel finiteness
        finite_bare = (isinstance(panel_bare, dict) and
                       all(panel_bare.get(k) is not None for k in
                           ("mel_l1_db", "spectral_centroid_rmse_hz",
                            "rms_env_rmse", "lufs_m_rmse_lu")))
        finite_eff = (isinstance(panel_effects, dict) and
                      all(panel_effects.get(k) is not None for k in
                          ("mel_l1_db", "spectral_centroid_rmse_hz",
                           "rms_env_rmse", "lufs_m_rmse_lu")))
        if not (finite_bare and finite_eff):
            verdict = "RECREATION_FAILS"
            reason = "panel comparisons did not both produce 8 finite keys"
        else:
            det_ok = determinism.get("all_deterministic_anchors_equal", False)
            mel_delta = panel_bare["mel_l1_db"] - panel_effects["mel_l1_db"]
            if not det_ok:
                # Determinism drift on WAVs → FAILS unless only MIDI/XML drifted
                per_anc = determinism.get("per_anchor", {})
                wav_ok = all(per_anc.get(k, {}).get("equal", False)
                             for k in ("07_render/bare_midi.wav",
                                       "07_render/effects.wav"))
                if wav_ok:
                    verdict = "RECREATION_PARTIAL"
                    reason = ("determinism × 2 holds on WAVs; drifted on "
                              "MusicXML/MIDI — documented in report")
                else:
                    verdict = "RECREATION_FAILS"
                    reason = "byte-determinism × 2 failed on rendered WAVs (F2)"
            elif mel_delta >= MEL_DELTA_LANDS_DB:
                verdict = "RECREATION_LANDS"
                reason = (f"effects layer narrows mel_l1_db by "
                          f"{mel_delta:.3f} dB (≥ {MEL_DELTA_LANDS_DB})")
            elif mel_delta > 0:
                verdict = "RECREATION_PARTIAL"
                reason = (f"effects layer narrows mel_l1_db by "
                          f"{mel_delta:.3f} dB (< {MEL_DELTA_LANDS_DB}) — P1")
            else:
                verdict = "RECREATION_PARTIAL"
                reason = (f"effects layer did NOT narrow mel_l1_db "
                          f"(delta={mel_delta:.3f} dB) — P1")

    verdict_payload: dict[str, Any] = {
        "verdict": verdict,
        "reason": reason,
        "failed_stage": failed_stage,
        "chosen_song": chosen,
        "panel_original_vs_bare": panel_bare,
        "panel_original_vs_effects": panel_effects,
        "mel_l1_db_delta_bare_minus_effects":
            (panel_bare["mel_l1_db"] - panel_effects["mel_l1_db"])
            if (isinstance(panel_bare, dict) and isinstance(panel_effects, dict)
                and panel_bare.get("mel_l1_db") is not None
                and panel_effects.get("mel_l1_db") is not None)
            else None,
        "determinism": determinism,
        "anchors_unchanged": len(anchor_diff) == 0,
        "rubric_hash": RUBRIC_HASH,
        "rubric_verdicts": ["RECREATION_LANDS", "RECREATION_PARTIAL", "RECREATION_FAILS"],
        "preview_untrained_ear": True,
        "cycle_36_ear_reference": "M-EAR-1/real-label-training-v0 → EAR_v0_INSUFFICIENT",
        "total_wall_seconds": round(time.perf_counter() - t_all, 3),
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 37,
        "fork": "675abd086911",
        "clone": 0,
        "milestone": "M-RECREATE-1/first-real-audio",
    }
    (DATA_ROOT / "verdict.json").write_text(
        json.dumps(verdict_payload, indent=2, sort_keys=True) + "\n")
    print(f"[recreate_v0] VERDICT: {verdict} — {reason}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
