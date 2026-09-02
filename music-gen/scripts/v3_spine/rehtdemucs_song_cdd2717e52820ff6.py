#!/usr/bin/env python3
"""c20 Disco A (sha16 cdd2717e52820ff6): htdemucs_6s on chosen section + full song x2.

Thin sibling of c5 rehtdemucs_operator_section.py (READ-ONLY reference).
Chosen section from focus_set_v2.json D1 auto-picker output.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

SHA16 = "cdd2717e52820ff6"
MP3 = "corpus/ratings/5/011__hcwKJOsUUIk__Disco_A.mp3"
T_START = 21.91963718820862
T_END = 51.91963718820862
T_DUR = 30.0
STEMS = ["bass", "drums", "guitar", "other", "piano", "vocals"]
BASE = Path(f"data/v3_spine/{SHA16}/operator_section")
CANON_OUT = BASE / "rc9_6stem"
FULL_BASE = Path(f"data/v3_spine/{SHA16}/full_song")
FULL_OUT = FULL_BASE / "rc9_6stem"


def slice_mp3(dst_wav: Path, t_start: float, t_dur: float | None):
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{t_start}",
        "-i", MP3,
    ]
    if t_dur is not None:
        cmd += ["-t", f"{t_dur}"]
    cmd += ["-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(dst_wav)]
    subprocess.run(cmd, check=True)


def run_htdemucs(in_wav: Path, tmpdir: Path):
    import torch
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    import soundfile as sf
    import numpy as np

    torch.manual_seed(0)
    torch.set_num_threads(1)
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass

    model = get_model("htdemucs_6s")
    model.cpu().eval()

    data, sr = sf.read(str(in_wav), always_2d=True)
    wav = torch.from_numpy(data.T.astype(np.float32))
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)
    if wav.shape[0] == 1:
        wav = wav.repeat(2, 1)
    ref = wav.mean(0)
    wav_norm = (wav - ref.mean()) / (ref.std() + 1e-8)
    with torch.no_grad():
        sources = apply_model(
            model, wav_norm[None], device="cpu", split=True, overlap=0.25, shifts=0
        )[0]
    sources = sources * ref.std() + ref.mean()

    outdir = tmpdir / "stems"
    outdir.mkdir()
    shas = {}
    for i, name in enumerate(model.sources):
        stem_wav = sources[i].cpu().numpy().T
        path = outdir / f"{name}.wav"
        sf.write(str(path), stem_wav, sr, subtype="PCM_16")
        shas[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return shas, outdir


def run_target(mode: str, canon_out: Path, base: Path, t_start: float, t_dur: float | None, det_report: Path):
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix=f"rome_{mode}_slice_") as td_slice:
        slice_wav = Path(td_slice) / "section.wav"
        slice_mp3(slice_wav, t_start, t_dur)
        slice_sha = hashlib.sha256(slice_wav.read_bytes()).hexdigest()
        print(f"[{mode} t={time.time()-t0:6.1f}s] slice sha={slice_sha[:16]} size={slice_wav.stat().st_size}")
        canon_out.parent.mkdir(parents=True, exist_ok=True)
        section_dst = canon_out.parent / "section.wav"
        shutil.copy2(slice_wav, section_dst)

        with tempfile.TemporaryDirectory(prefix=f"rome_{mode}_r1_") as td1:
            shas1, outdir1 = run_htdemucs(slice_wav, Path(td1))
            print(f"[{mode} t={time.time()-t0:6.1f}s] r1 " + " ".join(f"{k}={v[:12]}" for k,v in shas1.items()))
        with tempfile.TemporaryDirectory(prefix=f"rome_{mode}_r2_") as td2:
            shas2, outdir2 = run_htdemucs(slice_wav, Path(td2))
            print(f"[{mode} t={time.time()-t0:6.1f}s] r2 " + " ".join(f"{k}={v[:12]}" for k,v in shas2.items()))
            all_equal = all(shas1[s] == shas2[s] for s in STEMS)
            canon_out.mkdir(parents=True, exist_ok=True)
            for s in STEMS:
                shutil.copy2(outdir2 / f"{s}.wav", canon_out / f"{s}.wav")

    report = {
        "cycle": 20,
        "mode": mode,
        "input_mp3": MP3,
        "slice": {"t_start": t_start, "t_dur": t_dur, "sha256": slice_sha},
        "runs": {"run1": shas1, "run2": shas2},
        "byte_determinism_holds": all_equal,
        "n_mismatch": sum(1 for s in STEMS if shas1[s] != shas2[s]),
        "mismatch_stems": [s for s in STEMS if shas1[s] != shas2[s]],
        "wall_time_s": round(time.time() - t0, 2),
    }
    det_report.parent.mkdir(parents=True, exist_ok=True)
    det_report.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(f"[{mode} t={time.time()-t0:6.1f}s] det={all_equal} mismatches={report['n_mismatch']}")
    if not all_equal:
        print(f"STOP: {mode} htdemucs nondeterministic", file=sys.stderr)
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["section", "full", "both"], default="both")
    args = ap.parse_args()
    if args.mode in ("section", "both"):
        run_target("section", CANON_OUT, BASE, T_START, T_DUR, BASE / "htdemucs_determinism.json")
    if args.mode in ("full", "both"):
        run_target("full", FULL_OUT, FULL_BASE, 0.0, None, FULL_BASE / "htdemucs_determinism.json")


if __name__ == "__main__":
    main()
