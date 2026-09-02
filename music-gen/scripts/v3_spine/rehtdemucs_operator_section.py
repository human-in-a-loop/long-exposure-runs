#!/usr/bin/env python3
"""c5 Track B: run htdemucs_6s on Chicken Grease t=233.63918..263.63918s x2."""
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

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

MP3 = "corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3"
T_START = 233.63918367346938
T_DUR = 30.0
STEMS = ["bass", "drums", "guitar", "other", "piano", "vocals"]
CANON_OUT = Path("data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem")


def slice_mp3(dst_wav: Path):
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{T_START}",
        "-i", MP3,
        "-t", f"{T_DUR}",
        "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2",
        str(dst_wav),
    ]
    subprocess.run(cmd, check=True)


def run_htdemucs(in_wav: Path, tmpdir: Path) -> dict[str, str]:
    """Run htdemucs_6s and return {stem: sha256} for the 6 stems."""
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

    data, sr = sf.read(str(in_wav), always_2d=True)  # (samples, channels)
    wav = torch.from_numpy(data.T.astype(np.float32))  # (channels, samples)
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
        stem_wav = sources[i].cpu().numpy().T  # (samples, channels)
        path = outdir / f"{name}.wav"
        sf.write(str(path), stem_wav, sr, subtype="PCM_16")
        shas[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return shas, outdir


def main():
    t0 = time.time()
    with tempfile.TemporaryDirectory() as td_slice:
        slice_wav = Path(td_slice) / "operator_section.wav"
        slice_mp3(slice_wav)
        slice_sha = hashlib.sha256(slice_wav.read_bytes()).hexdigest()
        print(f"[t={time.time()-t0:6.1f}s] slice ok sha={slice_sha[:16]} size={slice_wav.stat().st_size}")

        # Persist the slice for the deliver step (READ-ONLY afterwards).
        CANON_OUT.parent.mkdir(parents=True, exist_ok=True)
        section_dst = CANON_OUT.parent / "section.wav"
        shutil.copy2(slice_wav, section_dst)

        # Run 1
        with tempfile.TemporaryDirectory() as td1:
            shas1, outdir1 = run_htdemucs(slice_wav, Path(td1))
            print(f"[t={time.time()-t0:6.1f}s] run1 done: " + " ".join(f"{k}={v[:12]}" for k,v in shas1.items()))
            run1_dir_copy = CANON_OUT.parent / "_run1_stems"
            if run1_dir_copy.exists():
                shutil.rmtree(run1_dir_copy)
            shutil.copytree(outdir1, run1_dir_copy)

        # Run 2 (fresh tempdir)
        with tempfile.TemporaryDirectory() as td2:
            shas2, outdir2 = run_htdemucs(slice_wav, Path(td2))
            print(f"[t={time.time()-t0:6.1f}s] run2 done: " + " ".join(f"{k}={v[:12]}" for k,v in shas2.items()))

            # Determinism
            all_equal = all(shas1[s] == shas2[s] for s in STEMS)
            # Promote run2 as canonical (arbitrary; both equal iff determinism holds)
            CANON_OUT.mkdir(parents=True, exist_ok=True)
            for s in STEMS:
                shutil.copy2(outdir2 / f"{s}.wav", CANON_OUT / f"{s}.wav")

        report = {
            "cycle": 5,
            "input_mp3": MP3,
            "slice": {"t_start": T_START, "t_dur": T_DUR, "sha256": slice_sha},
            "runs": {
                "run1": {s: shas1[s] for s in STEMS},
                "run2": {s: shas2[s] for s in STEMS},
            },
            "byte_determinism_holds": all_equal,
            "n_mismatch": sum(1 for s in STEMS if shas1[s] != shas2[s]),
            "mismatch_stems": [s for s in STEMS if shas1[s] != shas2[s]],
            "wall_time_s": round(time.time() - t0, 2),
        }
        out_path = Path("data/v3_spine/31a164f845f8e27e/operator_section/htdemucs_determinism.json")
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True))
        print(f"[t={time.time()-t0:6.1f}s] determinism: all_equal={all_equal} n_mismatch={report['n_mismatch']}")

        if not all_equal:
            print("STOP: htdemucs operator-section nondeterministic", file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    main()
