#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:15:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-schema-v2-hydration-render
# ---
"""Palette-v2 hydration-render orchestrator (c35 Branch A, clone-0).

Sequence:
  0. Load rubric hash; snapshot anchor mtimes+SHAs (READ-ONLY anchors).
  1. Build 3 assignment_v2 rows; validate through both layers of
     scripts.palette_v2.validate; write assignments_v2.jsonl.
  2. Two independent runs. For each run: for each stem, invoke
     scripts/palette_v2_render/render_stem_v2.py via SUBPROCESS into a
     fresh tempfile.mkdtemp() dir (subprocess isolation is REQUIRED for
     DawDreamer determinism — consecutive in-process VST3 renders are
     NOT byte-identical).
  3. Sum stems to bare_combined.wav per run; capture SHAs.
  4. Persist per-stem SHAs + pinned_state.json to
     data/palette_v2_render/per_stem/<stem>/.
  5. Measure M-TEX-1/panel on three pairs:
       (original, v1-bare)  -> baseline for the 5% floor
       (original, v2-bare)  -> panel_original_vs_v2.tsv
       (v1-bare, v2-bare)   -> panel_v1_vs_v2.tsv
  6. Resolve verdict; write verdict.json with rubric_hash embedded.
  7. Re-snapshot anchor mtimes/SHAs; write anchor_preservation.json;
     drift is a fatal RENDER_FAILS signal.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# BLAS pins BEFORE numeric imports.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Read-only anchor imports.
from scripts.texture.panel import texture_distance, PUBLIC_KEYS  # noqa: E402
from scripts.palette_v2_render.build_assignments_v2 import (  # noqa: E402
    build_and_write, probe_fetchability,
)

OUT_DIR = _REPO / "data" / "palette_v2_render"
RENDER_STEM_SCRIPT = _REPO / "scripts" / "palette_v2_render" / "render_stem_v2.py"

SAMPLE_RATE = 44100
SAMPLE_COUNT = int(SAMPLE_RATE * 30)
NUMERIC_KEYS = ("mel_l1_db", "spectral_centroid_rmse_hz",
                "rms_env_rmse", "lufs_m_rmse_lu")
V2_DELTA_PCT = 0.05
SILENT_PEAK_ABS = 1e-4

# c9 read-only anchors (same as c33).
C9_ORIGINAL = _REPO / "data" / "tex" / "renders" / "synth_030s" / "original.wav"
C9_V1_BARE = _REPO / "data" / "tex" / "renders" / "synth_030s" / "bare_midi.wav"

# READ-ONLY anchor dirs (rubric §Anchor preservation).
_ANCHOR_DIRS = (
    "scripts/palette",
    "scripts/palette_probe",
    "scripts/palette_render",
    "scripts/palette_v2",
    "scripts/dawdreamer_state",
    "data/dawdreamer_state/per_plugin/surge_xt",
    "data/dawdreamer_state/per_plugin/dexed",
    "data/palette/schema",
    "data/palette_probe",
    "data/palette_render",
    "data/palette_v2/schema",
)


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _snapshot_anchors() -> dict:
    """SHA + mtime of every file under _ANCHOR_DIRS. Excludes __pycache__."""
    out = {}
    for d in _ANCHOR_DIRS:
        base = _REPO / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            rel = str(p.relative_to(_REPO))
            if "__pycache__" in rel or rel.endswith(".pyc"):
                continue
            out[rel] = {
                "sha256": _sha256_file(p),
                "mtime": int(p.stat().st_mtime),
            }
    return out


def _read_wav(p: Path):
    y, sr = sf.read(str(p), always_2d=True)
    return y, sr


def _sum_stems(stem_wavs: list[Path], out_path: Path) -> str:
    accum = np.zeros((SAMPLE_COUNT, 2), dtype=np.float32)
    for sw in stem_wavs:
        y, sr = _read_wav(sw)
        if sr != SAMPLE_RATE:
            raise RuntimeError(f"stem sr={sr}, expected {SAMPLE_RATE}")
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
        n = min(y.shape[0], SAMPLE_COUNT)
        accum[:n, :] += y[:n, :].astype(np.float32)
    scipy_wav.write(str(out_path), SAMPLE_RATE, accum)
    return hashlib.sha256(out_path.read_bytes()).hexdigest()


def _subprocess_render(stem: str, instrument: str, out_wav: Path,
                        env: dict | None = None) -> dict:
    """Invoke render_stem_v2.py in a fresh subprocess.

    Returns the parsed JSON output {..., 'sha256', 'wav_path', 'peak_abs', 'silent'}.
    """
    # Inherit parent env (VST3 plugins may require HOME / LD_LIBRARY_PATH /
    # XDG_* to locate factory patches). Pin BLAS to 1 thread on top.
    _env = dict(os.environ)
    _env["OMP_NUM_THREADS"] = "1"
    _env["MKL_NUM_THREADS"] = "1"
    _env["OPENBLAS_NUM_THREADS"] = "1"
    if env:
        _env.update(env)
    r = subprocess.run(
        ["/usr/bin/python3", str(RENDER_STEM_SCRIPT),
         "--stem", stem, "--instrument", instrument,
         "--out-wav", str(out_wav)],
        capture_output=True, text=True, env=_env, check=False,
    )
    if r.returncode != 0:
        return {"stem": stem, "instrument": instrument,
                "error": f"subprocess rc={r.returncode}",
                "stderr": r.stderr[-2000:], "stdout": r.stdout[-500:],
                "silent": True, "sha256": None}
    try:
        parsed = json.loads(r.stdout)
    except Exception:
        return {"stem": stem, "instrument": instrument,
                "error": "json parse", "raw": r.stdout[:500], "silent": True,
                "sha256": None}
    parsed["stem"] = stem
    parsed["instrument"] = instrument
    return parsed


def _run_one_pipeline(assignments: list[dict], tag: str) -> dict:
    """One independent run: subprocess-render each stem into a fresh tempdir,
    sum to bare_combined.wav, return {'combined_sha', 'combined_wav', 'per_stem'}."""
    tmp = Path(tempfile.mkdtemp(prefix=f"palette_v2_render_{tag}_"))
    per_stem = []
    stem_wavs = []
    for a in assignments:
        stem = a["stem"]
        inst = a["instrument"]
        out_wav = tmp / stem / "render.wav"
        r = _subprocess_render(stem, inst, out_wav)
        per_stem.append(r)
        if r.get("sha256") is None:
            # Render failed for this stem — return partial data; caller
            # will treat as RENDER_FAILS.
            combined_wav = tmp / "bare_combined.wav"
            return {"tag": tag, "per_stem": per_stem,
                    "combined_sha": None, "combined_wav": str(combined_wav),
                    "tempdir": str(tmp), "failed_stem": stem,
                    "failed_reason": r.get("error", "unknown")}
        stem_wavs.append(out_wav)
    combined = tmp / "bare_combined.wav"
    combined_sha = _sum_stems(stem_wavs, combined)
    # Preserve combined outside tempdir for panel measurement.
    keep = OUT_DIR / f"_tmp_combined_{tag}.wav"
    shutil.copy2(combined, keep)
    return {"tag": tag, "per_stem": per_stem,
            "combined_sha": combined_sha, "combined_wav": str(keep),
            "tempdir": str(tmp)}


def _write_tsv(out_path: Path, panel_dict: dict) -> None:
    keys = sorted(PUBLIC_KEYS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\t".join(keys) + "\n")
        row = [("" if panel_dict.get(k) is None else str(panel_dict.get(k))) for k in keys]
        f.write("\t".join(row) + "\n")


def _panel(a: Path, b: Path) -> dict:
    ya, sra = _read_wav(a)
    yb, srb = _read_wav(b)
    if sra != srb:
        raise RuntimeError(f"SR mismatch: {a}={sra} vs {b}={srb}")
    return texture_distance(ya, yb, sra)


def _resolve_verdict(r1: dict, r2: dict,
                     panel_orig_v2: dict, panel_v1_v2: dict,
                     panel_baseline: dict,
                     anchor_pre: dict, anchor_post: dict) -> tuple[str, dict]:
    """Apply the 3-way frozen rubric."""
    reasons: dict = {}

    # A) Per-stem cross-run byte-determinism.
    per_stem_sha_pairs: dict = {}
    for a_r1 in r1["per_stem"]:
        stem = a_r1["stem"]
        match = next((x for x in r2["per_stem"] if x["stem"] == stem), None)
        if match is None:
            reasons["missing_run2_stem"] = stem
            return "RENDER_FAILS", reasons
        sha_r1 = a_r1.get("sha256")
        sha_r2 = match.get("sha256")
        per_stem_sha_pairs[stem] = {"run1": sha_r1, "run2": sha_r2,
                                     "equal": sha_r1 == sha_r2}
        if sha_r1 is None or sha_r2 is None:
            reasons["per_stem_render_error"] = {"stem": stem,
                "run1_sha": sha_r1, "run2_sha": sha_r2,
                "run1_err": a_r1.get("error"), "run2_err": match.get("error")}
            return "RENDER_FAILS", reasons
        if sha_r1 != sha_r2:
            reasons["per_stem_determinism_failure"] = {"stem": stem,
                "run1_sha": sha_r1, "run2_sha": sha_r2}
            return "RENDER_FAILS", reasons
        # Silence gate applies ONLY to VST3 hydration path (rubric §Render
        # mechanism). Drums fluidsynth may render quietly when basic-pitch
        # transcription yields low-velocity percussion notes on GM channel;
        # that is normal upstream noise and NOT a v2-hydration failure.
        inst = a_r1.get("instrument")
        if inst in ("surge_xt", "dexed") and (
                a_r1.get("silent", False) or match.get("silent", False)):
            reasons["vst3_hydration_silent"] = {"stem": stem, "instrument": inst,
                "run1_peak_abs": a_r1.get("peak_abs"),
                "run2_peak_abs": match.get("peak_abs")}
            return "RENDER_FAILS", reasons

    # B) Combined byte-determinism.
    if r1.get("combined_sha") is None or r2.get("combined_sha") is None:
        reasons["combined_render_error"] = {
            "run1_failed_stem": r1.get("failed_stem"),
            "run2_failed_stem": r2.get("failed_stem")}
        return "RENDER_FAILS", reasons
    if r1["combined_sha"] != r2["combined_sha"]:
        reasons["combined_determinism_failure"] = {
            "run1_sha": r1["combined_sha"], "run2_sha": r2["combined_sha"]}
        return "RENDER_FAILS", reasons

    # C) Panels must have 8 keys, numeric-family finite.
    for tag, panel in (("orig_vs_v2", panel_orig_v2),
                       ("v1_vs_v2", panel_v1_v2)):
        if set(panel.keys()) != set(PUBLIC_KEYS):
            reasons["panel_key_contract"] = {"tag": tag, "keys": sorted(panel.keys())}
            return "RENDER_FAILS", reasons
        for k in NUMERIC_KEYS:
            v = panel.get(k)
            if v is None or not np.isfinite(v):
                reasons["non_finite_numeric_key"] = {"tag": tag, "key": k, "value": v}
                return "RENDER_FAILS", reasons

    # D) Anchor preservation drift.
    drift = {rel: (anchor_pre.get(rel), anchor_post.get(rel))
             for rel in anchor_pre
             if anchor_pre.get(rel, {}).get("sha256") != anchor_post.get(rel, {}).get("sha256")}
    if drift:
        reasons["anchor_preservation_drift"] = {k: {"pre_sha": v[0].get("sha256") if v[0] else None,
                                                     "post_sha": v[1].get("sha256") if v[1] else None}
                                                 for k, v in list(drift.items())[:5]}
        return "RENDER_FAILS", reasons

    # E) V2_MOVES_PANEL vs V2_NEUTRAL:
    #    At least one numeric key on panel_v1_v2 exceeds
    #    5% × baseline_self_distance from panel_baseline (original vs v1-bare).
    deltas = {}
    any_moved = False
    for k in NUMERIC_KEYS:
        baseline = panel_baseline.get(k)
        v2_delta = panel_v1_v2.get(k)
        if baseline is None or not np.isfinite(baseline):
            reasons["baseline_missing"] = k
            return "RENDER_FAILS", reasons
        threshold = abs(baseline) * V2_DELTA_PCT
        moved = abs(v2_delta) >= threshold
        deltas[k] = {"panel_v1_vs_v2": float(v2_delta),
                     "baseline_original_vs_v1_bare": float(baseline),
                     "threshold_5pct": float(threshold),
                     "moved": bool(moved)}
        if moved:
            any_moved = True

    if any_moved:
        return "V2_MOVES_PANEL", {"deltas": deltas,
                                   "per_stem_sha": per_stem_sha_pairs}
    return "V2_NEUTRAL", {"deltas": deltas,
                          "per_stem_sha": per_stem_sha_pairs}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ladder = OUT_DIR / "fetchability_ladder.jsonl"
    fetch = probe_fetchability(ladder)

    # 1. Build assignments (validated through both layers of palette_v2.validate).
    assignments = build_and_write(OUT_DIR / "assignments_v2.jsonl", fetch)

    # 2. Anchor snapshot BEFORE the render.
    anchor_pre = _snapshot_anchors()

    # 3. Two independent temp-dir pipeline runs (subprocess-isolated per stem).
    print(f"[c35-BA] run1 starting @ {time.strftime('%H:%M:%S')}", flush=True)
    r1 = _run_one_pipeline(assignments, "run1")
    print(f"[c35-BA] run2 starting @ {time.strftime('%H:%M:%S')}", flush=True)
    r2 = _run_one_pipeline(assignments, "run2")

    # 4. Persist per-stem SHAs into stable location + pinned_state.json.
    for a_r1 in r1["per_stem"]:
        stem = a_r1["stem"]
        stem_out = OUT_DIR / "per_stem" / stem
        stem_out.mkdir(parents=True, exist_ok=True)
        (stem_out / "render_run1.wav.sha").write_text(
            (a_r1.get("sha256") or "RENDER_ERROR") + "\n")
        match = next((x for x in r2["per_stem"] if x["stem"] == stem), {})
        (stem_out / "render_run2.wav.sha").write_text(
            (match.get("sha256") or "RENDER_ERROR") + "\n")
        pinned = {
            "stem": stem,
            "instrument": a_r1.get("instrument"),
            "sample_rate": SAMPLE_RATE,
            "sample_count": SAMPLE_COUNT,
            "run1_sha": a_r1.get("sha256"),
            "run2_sha": match.get("sha256"),
            "sha_equal": (a_r1.get("sha256") == match.get("sha256")),
            "run1_dispatch": {kk: a_r1.get(kk) for kk in
                              ("path", "peak_abs", "silent",
                               "n_params_anchor", "n_params_set",
                               "n_params_skipped", "n_samples")},
            "run2_dispatch": {kk: match.get(kk) for kk in
                              ("path", "peak_abs", "silent",
                               "n_params_anchor", "n_params_set",
                               "n_params_skipped", "n_samples")},
        }
        (stem_out / "pinned_state.json").write_text(
            json.dumps(pinned, sort_keys=True, indent=2) + "\n")

    # 5. bare_combined SHAs as top-level artifacts.
    (OUT_DIR / "bare_combined.wav.sha.run1").write_text(
        (r1.get("combined_sha") or "RENDER_ERROR") + "\n")
    (OUT_DIR / "bare_combined.wav.sha.run2").write_text(
        (r2.get("combined_sha") or "RENDER_ERROR") + "\n")

    # 6. Panel measurements.
    baseline = _panel(C9_ORIGINAL, C9_V1_BARE)
    _write_tsv(OUT_DIR / "panel_original_vs_v1_bare_baseline.tsv", baseline)

    combined_wav = Path(r1["combined_wav"]) if r1.get("combined_wav") else None
    if combined_wav and combined_wav.exists():
        panel_orig_v2 = _panel(C9_ORIGINAL, combined_wav)
        panel_v1_v2 = _panel(C9_V1_BARE, combined_wav)
    else:
        panel_orig_v2 = {k: None for k in PUBLIC_KEYS}
        panel_v1_v2 = {k: None for k in PUBLIC_KEYS}
    _write_tsv(OUT_DIR / "panel_original_vs_v2.tsv", panel_orig_v2)
    _write_tsv(OUT_DIR / "panel_v1_vs_v2.tsv", panel_v1_v2)

    # 7. Verdict.
    anchor_post = _snapshot_anchors()
    verdict, justification = _resolve_verdict(
        r1, r2, panel_orig_v2, panel_v1_v2, baseline,
        anchor_pre, anchor_post)

    rubric_hash = (OUT_DIR / "rubric_hash.txt").read_text().strip()

    def _dj(panel):
        return {k: (float(v) if isinstance(v, (int, float)) and v is not None else v)
                for k, v in panel.items()}

    verdict_json = {
        "verdict": verdict,
        "rubric_hash": rubric_hash,
        "v2_delta_pct": V2_DELTA_PCT,
        "assignments": [{"stem": a["stem"], "instrument": a["instrument"],
                         "assignment_id_v2": a["assignment_id_v2"],
                         "pinned_state_format": a["pinned_state"]["format"],
                         "plugin_name": a["pinned_state"].get("plugin_name"),
                         "provenance_pointers": a["provenance_pointers"]}
                        for a in assignments],
        "per_stem": [{"stem": a_r1["stem"],
                      "instrument": a_r1.get("instrument"),
                      "run1_sha": a_r1.get("sha256"),
                      "run2_sha": next((x.get("sha256") for x in r2["per_stem"]
                                        if x["stem"] == a_r1["stem"]), None),
                      "run1_peak_abs": a_r1.get("peak_abs"),
                      "run1_silent": a_r1.get("silent"),
                      "n_params_set": a_r1.get("n_params_set")}
                     for a_r1 in r1["per_stem"]],
        "bare_combined_sha_run1": r1.get("combined_sha"),
        "bare_combined_sha_run2": r2.get("combined_sha"),
        "bare_combined_sha_equal": (r1.get("combined_sha") ==
                                    r2.get("combined_sha") and
                                    r1.get("combined_sha") is not None),
        "panels": {
            "panel_original_vs_v1_bare_baseline": _dj(baseline),
            "panel_original_vs_v2": _dj(panel_orig_v2),
            "panel_v1_vs_v2": _dj(panel_v1_v2),
        },
        "justification": justification,
        "fetchability": fetch,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (OUT_DIR / "verdict.json").write_text(
        json.dumps(verdict_json, sort_keys=True, indent=2) + "\n")

    (OUT_DIR / "anchor_preservation.json").write_text(
        json.dumps({"pre": anchor_pre, "post": anchor_post,
                    "unchanged": anchor_pre == anchor_post},
                   sort_keys=True, indent=2) + "\n")

    # Cleanup temp combined WAVs.
    for tag in ("run1", "run2"):
        p = OUT_DIR / f"_tmp_combined_{tag}.wav"
        if p.exists():
            p.unlink()

    print(json.dumps({"verdict": verdict, "rubric_hash": rubric_hash,
                      "combined_sha_equal": r1.get("combined_sha") == r2.get("combined_sha")},
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
