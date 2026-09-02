#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: MuScriptor per-stem JSON+MID x2 for Peach Dream chosen section.

Per-song sibling of scripts/v3_spine/muscriptor_operator_section.py (READ-ONLY).
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

MUSCRIPTOR = "workspace/learned_transcribers_venv/bin/muscriptor"
MODEL = "workspace/models/muscriptor-medium/model.safetensors"
SEC_DIR = Path("data/v3_spine/88d247468cb6d49f/chosen_section")
STEM_DIR = SEC_DIR / "rc9_6stem"
SECTION_WAV = SEC_DIR / "section.wav"
OUT_MUS = SEC_DIR / "muscriptor"
OUT_MUS.mkdir(parents=True, exist_ok=True)
DEL_MUS = Path("data/v3/deliveries/88d247468cb6d49f/muscriptor_operator_section")
DEL_MUS.mkdir(parents=True, exist_ok=True)

WHITELIST = {
    "drums": None,
    "bass": "acoustic_bass,electric_bass",
    "guitar": "clean_electric_guitar,distorted_electric_guitar,acoustic_guitar",
    "other": "clean_electric_guitar,distorted_electric_guitar,acoustic_guitar,synth_lead,synth_pad",
    "piano": "acoustic_piano,electric_piano,organ",
    "vocals": "acoustic_piano,synth_lead",
    "full_mix": None,
}

PROBES = [
    ("drums", STEM_DIR / "drums.wav"),
    ("bass", STEM_DIR / "bass.wav"),
    ("guitar", STEM_DIR / "guitar.wav"),
    ("other", STEM_DIR / "other.wav"),
    ("piano", STEM_DIR / "piano.wav"),
    ("vocals", STEM_DIR / "vocals.wav"),
    ("full_mix", SECTION_WAV),
]


def env():
    e = os.environ.copy()
    e.update({"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
              "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
              "OPENBLAS_NUM_THREADS": "1"})
    return e


def run_muscriptor(wav: Path, out_path: Path, instruments, fmt: str):
    cmd = [MUSCRIPTOR, "transcribe", str(wav), "--format", fmt, "--output", str(out_path),
           "--model", MODEL, "--device", "cpu", "--detect-tempo", "best-effort"]
    if instruments:
        cmd += ["--instruments", instruments]
    r = subprocess.run(cmd, env=env(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"muscriptor rc={r.returncode}: {r.stderr.decode('utf-8','replace')[-2000:]}")


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    t0 = time.time()
    report = {"cycle": 20, "clone": "clone-2", "song_sha16": "88d247468cb6d49f", "probes": {}}
    for name, wav in PROBES:
        white = WHITELIST[name]
        t_probe = time.time()
        with tempfile.TemporaryDirectory(prefix=f"pd_c20_{name}_r1_") as d1:
            p1 = Path(d1) / "events.json"
            run_muscriptor(wav, p1, white, "json")
            sha_r1 = sha(p1); r1_data = p1.read_bytes()
        with tempfile.TemporaryDirectory(prefix=f"pd_c20_{name}_r2_") as d2:
            p2 = Path(d2) / "events.json"
            run_muscriptor(wav, p2, white, "json")
            sha_r2 = sha(p2)
        equal = sha_r1 == sha_r2

        canonical_json = OUT_MUS / f"{name}.json"
        canonical_json.write_bytes(r1_data)
        if name != "full_mix":
            shutil.copy2(canonical_json, DEL_MUS / f"{name}.json")

        try:
            with tempfile.TemporaryDirectory(prefix=f"pd_c20_{name}_mid_") as dm:
                pm = Path(dm) / "events.mid"
                run_muscriptor(wav, pm, white, "midi")
                mid_sha = sha(pm)
                shutil.copy2(pm, OUT_MUS / f"{name}.mid")
                if name != "full_mix":
                    shutil.copy2(pm, DEL_MUS / f"{name}.mid")
        except Exception as e:
            mid_sha = f"ERROR:{type(e).__name__}"
        report["probes"][name] = {
            "input_wav": str(wav), "instruments_whitelist": white,
            "run1_json_sha256": sha_r1, "run2_json_sha256": sha_r2,
            "byte_deterministic": equal, "midi_debug_sha256": mid_sha,
            "wall_s": round(time.time() - t_probe, 1),
        }
        print(f"[t={time.time()-t0:6.1f}s] {name:10s} equal={equal} json_sha={sha_r1[:16]} mid_sha={str(mid_sha)[:16]}")

    n_probes = len(PROBES)
    n_equal = sum(1 for p in report["probes"].values() if p["byte_deterministic"])
    report["n_probes"] = n_probes
    report["n_deterministic"] = n_equal
    report["all_deterministic"] = n_equal == n_probes
    report["wall_time_s"] = round(time.time() - t0, 2)
    out = SEC_DIR / "muscriptor_determinism.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"muscriptor done: {n_equal}/{n_probes} deterministic")


if __name__ == "__main__":
    main()
