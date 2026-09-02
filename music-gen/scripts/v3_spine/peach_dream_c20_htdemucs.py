#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: htdemucs_6s on Peach Dream chosen section + full song, byte-det x2.

Per-song sibling of scripts/v3_spine/rehtdemucs_operator_section.py (READ-ONLY).
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

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

MP3 = "corpus/ratings/6/015__wXvX1vOe0rQ__Peach_Dream.mp3"
T_START = 172.87256235827664
T_DUR = 30.0
STEMS = ["bass", "drums", "guitar", "other", "piano", "vocals"]
CHOSEN_DIR = Path("data/v3_spine/88d247468cb6d49f/chosen_section")
FULL_DIR = Path("data/v3_spine/88d247468cb6d49f/full_song")
DEL_STEMS_CHOSEN = Path("data/v3/deliveries/88d247468cb6d49f/stems_6s")
DEL_STEMS_FULL = Path("data/v3/deliveries/88d247468cb6d49f/stems_6s_full_song")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def slice_mp3(dst_wav: Path, t_start: float, t_dur: float | None):
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    if t_start is not None:
        cmd += ["-ss", f"{t_start}"]
    cmd += ["-i", MP3]
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
        sources = apply_model(model, wav_norm[None], device="cpu", split=True, overlap=0.25, shifts=0)[0]
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


def process_scope(scope: str, t_start, t_dur, canon_stems_dir: Path, del_stems_dir: Path):
    t0 = time.time()
    with tempfile.TemporaryDirectory() as td_slice:
        slice_wav = Path(td_slice) / f"{scope}.wav"
        slice_mp3(slice_wav, t_start, t_dur)
        slice_sha = sha(slice_wav)
        print(f"[{scope} t={time.time()-t0:6.1f}s] slice sha={slice_sha[:16]} size={slice_wav.stat().st_size}")

        canon_stems_dir.parent.mkdir(parents=True, exist_ok=True)
        section_dst = canon_stems_dir.parent / "section.wav"
        shutil.copy2(slice_wav, section_dst)

        with tempfile.TemporaryDirectory() as td1:
            shas1, outdir1 = run_htdemucs(slice_wav, Path(td1))
            print(f"[{scope} t={time.time()-t0:6.1f}s] run1 " + " ".join(f"{k}={v[:12]}" for k,v in shas1.items()))
        with tempfile.TemporaryDirectory() as td2:
            shas2, outdir2 = run_htdemucs(slice_wav, Path(td2))
            print(f"[{scope} t={time.time()-t0:6.1f}s] run2 " + " ".join(f"{k}={v[:12]}" for k,v in shas2.items()))
            canon_stems_dir.mkdir(parents=True, exist_ok=True)
            del_stems_dir.mkdir(parents=True, exist_ok=True)
            for s in STEMS:
                shutil.copy2(outdir2 / f"{s}.wav", canon_stems_dir / f"{s}.wav")
                shutil.copy2(outdir2 / f"{s}.wav", del_stems_dir / f"{s}.wav")

    all_equal = all(shas1[s] == shas2[s] for s in STEMS)
    return {
        "scope": scope,
        "slice": {"t_start": t_start, "t_dur": t_dur, "sha256": slice_sha},
        "runs": {"run1": shas1, "run2": shas2},
        "byte_determinism_holds": all_equal,
        "n_mismatch": sum(1 for s in STEMS if shas1[s] != shas2[s]),
        "mismatch_stems": [s for s in STEMS if shas1[s] != shas2[s]],
        "wall_time_s": round(time.time() - t0, 2),
    }


def main():
    chosen_report = process_scope("chosen_section", T_START, T_DUR, CHOSEN_DIR / "rc9_6stem", DEL_STEMS_CHOSEN)
    full_report = process_scope("full_song", 0.0, None, FULL_DIR / "rc9_6stem", DEL_STEMS_FULL)
    report = {
        "cycle": 20,
        "clone": "clone-2",
        "song_sha16": "88d247468cb6d49f",
        "input_mp3": MP3,
        "chosen_section": chosen_report,
        "full_song": full_report,
        "byte_determinism_holds_all_24_stems": (
            chosen_report["byte_determinism_holds"] and full_report["byte_determinism_holds"]
        ),
    }
    out_path = Path("data/v3_spine/88d247468cb6d49f/htdemucs_determinism.json")
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"htdemucs done: chosen_det={chosen_report['byte_determinism_holds']} full_det={full_report['byte_determinism_holds']}")


if __name__ == "__main__":
    main()
