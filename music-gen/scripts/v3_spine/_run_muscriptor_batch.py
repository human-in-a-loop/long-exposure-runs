"""Serial in-turn MuScriptor batch runner. Reads (stem, fmt) targets from argv."""
from __future__ import annotations
import subprocess, os, sys, time, hashlib, pathlib, json

env = os.environ.copy()
env.update({
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
})

MODEL = pathlib.Path("workspace/models/muscriptor-medium/model.safetensors").resolve()
OUT_DIR = pathlib.Path("data/v3_spine/31a164f845f8e27e/muscriptor").resolve()
STEMS = pathlib.Path("data/v3_spine/31a164f845f8e27e/stems_6s").resolve()
SECTION = pathlib.Path("data/v3_spine/31a164f845f8e27e/section.wav").resolve()

WHITELIST = {
    "drums": "drums",
    "bass": "electric_bass,acoustic_bass",
    "guitar": "acoustic_guitar,clean_electric_guitar,distorted_electric_guitar",
    "other": "synth_lead,synth_pad,synth_strings,orchestra_hit,chromatic_percussion",
    "piano": "acoustic_piano,electric_piano,organ",
    "vocals": "voice",
    "full_mix": None,
}

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = [t.split(":") for t in sys.argv[1:]]
    results: dict = {}
    for stem, fmt in targets:
        ext = "mid" if fmt == "midi" else "json"
        out = OUT_DIR / f"{stem}.{ext}"
        if out.exists():
            results[f"{stem}.{ext}"] = {"skipped": "exists", "sha": hashlib.sha256(out.read_bytes()).hexdigest()}
            continue
        src = SECTION if stem == "full_mix" else (STEMS / f"{stem}.wav")
        args = [
            "workspace/learned_transcribers_venv/bin/muscriptor",
            "transcribe", str(src),
            "-o", str(out),
            "-f", fmt,
            "-m", str(MODEL),
            "-d", "cpu",
            "--detect-tempo", "best-effort",
        ]
        wl = WHITELIST.get(stem)
        if wl is not None:
            args += ["--instruments", wl]
        t0 = time.time()
        r = subprocess.run(args, capture_output=True, text=True, env=env, timeout=400)
        wall = time.time() - t0
        entry: dict = {"wall_s": round(wall, 1), "rc": r.returncode}
        if r.returncode == 0 and out.exists():
            entry["sha"] = hashlib.sha256(out.read_bytes()).hexdigest()
        else:
            entry["stderr_tail"] = r.stderr[-800:]
        results[f"{stem}.{ext}"] = entry
        print(f"{stem}.{ext}: wall={wall:.1f}s rc={r.returncode}", flush=True)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
