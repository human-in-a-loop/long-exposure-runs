#!/usr/bin/python3
# ---
# created: 2026-09-02T00:00:00Z
# cycle: 58
# milestone: M-V3-SPINE
# ---
"""Emit M-V3-SPINE verdict.json with three-way rubric_hash byte-equality."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"verdict requires /usr/bin/python3 (got {sys.executable})")

WSROOT = Path(__file__).resolve().parents[2]
RUBRIC_DOC = WSROOT / "docs" / "v3_spine_rubric.md"
RUBRIC_HASH_PATH = WSROOT / "data" / "v3_spine" / "rubric_hash.txt"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _run_promise_check() -> tuple[int, int, str]:
    """Return (n_error, n_warn, tail) from promise_check."""
    try:
        r = subprocess.run(
            [sys.executable, "-m", "long_exposure.tools.promise_check", str(WSROOT)],
            capture_output=True, text=True, timeout=120,
        )
        out = (r.stdout or "") + (r.stderr or "")
        n_err = out.count("ERROR")
        n_warn = out.count("WARN")
        return n_err, n_warn, out[-2000:]
    except Exception as e:
        return -1, -1, f"promise_check unavailable: {e}"


def _classify(pipeline_summary_path: Path, det_path: Path, anchor_path: Path,
              tests_path: Path) -> tuple[str, dict]:
    """Apply frozen 3-verdict rubric."""
    reasons: dict = {}
    # (a) chain ran + delivery present
    summary = json.loads(pipeline_summary_path.read_text()) if pipeline_summary_path.exists() else None
    deliver_dir = WSROOT / "data" / "v3" / "deliveries" / summary["song_sha16"]
    delivery_ok = all((deliver_dir / n).exists() for n in
                      ("original_ab.wav", "reconstruction_ab.wav",
                       "full_reconstruction.wav", "manifest.json"))
    reasons["delivery_present"] = delivery_ok

    # non-silent + duration check
    from scripts.v3_spine.pipeline import _read_wav_stereo_f32, SR_MIX
    import numpy as np
    peaks = {}
    durations = {}
    for name in ("original_ab.wav", "reconstruction_ab.wav", "full_reconstruction.wav"):
        p = deliver_dir / name
        if p.exists():
            arr, sr = _read_wav_stereo_f32(p)
            peaks[name] = float(np.max(np.abs(arr)))
            durations[name] = arr.shape[0] / sr
    reasons["peaks"] = peaks
    reasons["durations"] = durations
    ab_dur_ok = (abs(durations.get("original_ab.wav", 0) - 30.0) < 0.005 and
                 abs(durations.get("reconstruction_ab.wav", 0) - 30.0) < 0.005)
    non_silent = all(p > 1e-4 for p in peaks.values())
    reasons["ab_duration_ok"] = ab_dur_ok
    reasons["non_silent"] = non_silent

    # (b) byte determinism
    det = json.loads(det_path.read_text()) if det_path.exists() else None
    byte_det = bool(det and det.get("byte_determinism_holds"))
    reasons["byte_determinism_holds"] = byte_det
    reasons["byte_determinism_mismatches"] = det.get("mismatches", []) if det else "MISSING"

    # (d) panel finite
    panel = summary.get("panel", {})
    finite = all(isinstance(v, (int, float)) and v == v for v in panel.values())
    reasons["panel_finite"] = finite
    reasons["panel"] = panel

    # (e) zero GM 4 unless intended; drums on ch10
    prog_manifest = summary.get("merge_info", {}).get("program_manifest", [])
    non_intended_prog4 = [p for p in prog_manifest
                          if p.get("gm_program") == 4 and p.get("label") != "electric_piano"
                          and not p.get("is_drum")]
    drums_ch10 = [p for p in prog_manifest if p.get("is_drum") and p.get("channel") == 10]
    reasons["non_intended_program_4"] = non_intended_prog4
    reasons["drums_on_channel_10"] = len(drums_ch10) > 0
    reasons["vocals_symbolic_present"] = any(p.get("is_vocal_symbolic") for p in prog_manifest)

    # (f) tests
    tests_result = json.loads(tests_path.read_text()) if tests_path.exists() else None
    tests_ok = bool(tests_result and tests_result.get("n_pass", 0) >= tests_result.get("n_total", 0)
                    and tests_result.get("n_total", 0) >= 12)
    reasons["tests"] = tests_result

    # (g) anchor preservation
    anchor = json.loads(anchor_path.read_text()) if anchor_path.exists() else None
    anchor_ok = bool(anchor and anchor.get("all_match") and anchor.get("n_anchors", 0) >= 20)
    reasons["anchor_preservation"] = anchor

    # (h) promise_check
    n_err, n_warn, pc_tail = _run_promise_check()
    reasons["promise_check_errors"] = n_err
    reasons["promise_check_warns"] = n_warn

    hard_fail = (not delivery_ok) or (not ab_dur_ok) or (not non_silent)
    if hard_fail:
        return "V3_SPINE_CHAIN_FAILS", reasons

    green_bars = [byte_det, finite, tests_ok, anchor_ok, len(non_intended_prog4) == 0,
                  reasons["drums_on_channel_10"], n_err == 0]
    n_green = sum(green_bars)
    if n_green == len(green_bars):
        return "V3_SPINE_CHAIN_LANDS", reasons
    if n_green >= len(green_bars) - 1:
        return "V3_SPINE_CHAIN_PARTIAL", reasons
    return "V3_SPINE_CHAIN_FAILS", reasons


def emit(song_sha16: str) -> dict:
    root = WSROOT / "data" / "v3_spine" / song_sha16
    doc_sha = _sha256(RUBRIC_DOC)
    file_sha = RUBRIC_HASH_PATH.read_text().strip()
    if doc_sha != file_sha:
        raise RuntimeError(
            f"rubric hash chain broken: docs/v3_spine_rubric.md sha={doc_sha} "
            f"vs data/v3_spine/rubric_hash.txt={file_sha}"
        )

    verdict, reasons = _classify(
        root / "run_summary.json",
        root / "determinism.json",
        root / "anchor_preservation.json",
        root / "tests_result.json",
    )

    v = {
        "milestone": "M-V3-SPINE",
        "song_sha16": song_sha16,
        "verdict": verdict,
        "rubric_hash": doc_sha,
        "operator_listening_status": "pending",
        "reasons": reasons,
    }
    out = root / "verdict.json"
    out.write_text(json.dumps(v, sort_keys=True, indent=2) + "\n")
    return v


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--song-sha16", default="31a164f845f8e27e")
    args = ap.parse_args()
    v = emit(args.song_sha16)
    print(json.dumps({"verdict": v["verdict"],
                      "operator_listening_status": v["operator_listening_status"],
                      "rubric_hash_prefix": v["rubric_hash"][:16]}, indent=2))


if __name__ == "__main__":
    main()
