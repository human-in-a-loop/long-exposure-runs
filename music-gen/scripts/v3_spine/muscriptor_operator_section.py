#!/usr/bin/env python3
"""c5 Track B: run MuScriptor --format json on the 6 operator-section stems + full-mix slice, x2.

Also emits the MuScriptor --format midi sidecar per c4 operator directive
(non_factor_debug — canonical serializer owns the authoritative MIDI).
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
SEC_DIR = Path("data/v3_spine/31a164f845f8e27e/operator_section")
STEM_DIR = SEC_DIR / "rc9_6stem"
SECTION_WAV = SEC_DIR / "section.wav"
OUT_MUS = SEC_DIR / "muscriptor"
OUT_MUS.mkdir(parents=True, exist_ok=True)

# Whitelist mapping from cycle 3 doc (docs/v3_spine_instrument_whitelist_mapping.md).
WHITELIST = {
    "drums": None,  # drums stem: full vocab (drums-only mapping post-canonicalize)
    "bass": "acoustic_bass,electric_bass",
    "guitar": "clean_electric_guitar,distorted_electric_guitar,acoustic_guitar",
    "other": "clean_electric_guitar,distorted_electric_guitar,acoustic_guitar,synth_lead,synth_pad",
    "piano": "acoustic_piano,electric_piano,organ",
    "vocals": "acoustic_piano,synth_lead",  # vocals-symbolic placeholder per c3
    "full_mix": None,
}

# 7 probes: 6 stems + full-mix slice
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
    e.update(
        {
            "PYTHONHASHSEED": "0",
            "SOURCE_DATE_EPOCH": "1756463424",
            "TZ": "UTC",
            "LC_ALL": "C.UTF-8",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
        }
    )
    return e


def run_muscriptor(wav: Path, out_path: Path, instruments: str | None, fmt: str):
    cmd = [
        MUSCRIPTOR, "transcribe",
        str(wav),
        "--format", fmt,
        "--output", str(out_path),
        "--model", MODEL,
        "--device", "cpu",
        "--detect-tempo", "best-effort",
    ]
    if instruments:
        cmd += ["--instruments", instruments]
    r = subprocess.run(cmd, env=env(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"muscriptor failed rc={r.returncode}: {r.stderr.decode('utf-8','replace')[-2000:]}")


def main():
    t0 = time.time()
    report = {"cycle": 5, "probes": {}}
    for name, wav in PROBES:
        white = WHITELIST[name]
        t_probe = time.time()
        # Run 1 into fresh tempdir
        with tempfile.TemporaryDirectory(prefix=f"v3_c5_{name}_r1_") as d1:
            p1 = Path(d1) / "events.json"
            run_muscriptor(wav, p1, white, "json")
            sha_r1 = hashlib.sha256(p1.read_bytes()).hexdigest()
            r1_data = p1.read_bytes()
        # Run 2 into fresh tempdir
        with tempfile.TemporaryDirectory(prefix=f"v3_c5_{name}_r2_") as d2:
            p2 = Path(d2) / "events.json"
            run_muscriptor(wav, p2, white, "json")
            sha_r2 = hashlib.sha256(p2.read_bytes()).hexdigest()
        equal = sha_r1 == sha_r2

        # Persist canonical JSON winner (both equal iff determinism holds)
        canonical_json = OUT_MUS / f"{name}.json"
        canonical_json.write_bytes(r1_data)

        # Also emit --format midi sidecar (non_factor_debug per c4 directive)
        try:
            with tempfile.TemporaryDirectory(prefix=f"v3_c5_{name}_mid_") as dm:
                pm = Path(dm) / "events.mid"
                run_muscriptor(wav, pm, white, "midi")
                mid_sha = hashlib.sha256(pm.read_bytes()).hexdigest()
                shutil.copy2(pm, OUT_MUS / f"{name}.mid")
        except Exception as e:
            mid_sha = f"ERROR:{type(e).__name__}"
        report["probes"][name] = {
            "input_wav": str(wav),
            "instruments_whitelist": white,
            "run1_json_sha256": sha_r1,
            "run2_json_sha256": sha_r2,
            "byte_deterministic": equal,
            "midi_debug_sha256": mid_sha,
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
    out.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(f"[t={time.time()-t0:6.1f}s] wrote {out} — {n_equal}/{n_probes} probes deterministic")
    if not report["all_deterministic"]:
        print("STOP: MuScriptor operator-section JSON nondeterministic", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
