#!/usr/bin/python3
"""v6 Phase 3 — separate_corpus_v6: detached-capable htdemucs driver producing the stem cache data/v6/stems/<sha16>/.

created: 2026-10-04
milestone: M-V6-GEN-3/humanization

  /usr/bin/python3 scripts/v6/separate_corpus_v6.py --detach          # nohup-style background run, returns at once
  /usr/bin/python3 scripts/v6/separate_corpus_v6.py --run             # foreground (what --detach spawns)
  /usr/bin/python3 scripts/v6/separate_corpus_v6.py --status          # print progress.json

Per song (corpus_manifest_v6.json order, skip when all 4 stems exist and are recorded in data/v6/stems/manifest.json):
mp3 -> ffmpeg pcm_s16le 44.1 kHz stereo (scratch) -> htdemucs (4 stems; torch.manual_seed(0), shifts=0, overlap=0.25,
split=True, set_num_threads(2) — the scripts/v3_spine/recreate_v3.py:150-183 settings with 2 threads) -> each stem MONO
(channel mean) -> 22.05 kHz (scipy resample_poly 1/2, deterministic) -> 16-bit PCM WAV data/v6/stems/<sha16>/<stem>.wav.
progress: data/v6/stems/progress.json (atomic, after every song); log: data/v6/logs/separate.log. Disk guard: the stage
aborts (status "aborted_disk") when df of the workspace is >= 90 % before a song. Nothing outside data/v6/stems is deleted.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.gen.common import WS, read_json, sha_file, write_json_atomic  # noqa: E402  (env pins + interpreter guard)

STEMS_DIR = WS / "data/v6/stems"
LOG = WS / "data/v6/logs/separate.log"
MANIFEST = WS / "data/v6/corpus/corpus_manifest_v6.json"
STEM_NAMES = ("drums", "bass", "other", "vocals")
OUT_SR = 22050
DEMUCS = {"model": "htdemucs", "shifts": 0, "overlap": 0.25, "split": True, "manual_seed": 0, "num_threads": 2, "device": "cpu"}
DISK_ABORT_PCT = 90.0


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    if not os.environ.get("SEPARATE_V6_DETACHED"):  # the detached child's stdout IS the log file
        print(line, flush=True)


def disk_pct(path: Path = WS) -> float:
    """df's Use%: used / (used + available) — on thin-provisioned roots shutil.disk_usage's total overstates the backing store."""
    st = os.statvfs(str(path))
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    avail = st.f_bavail * st.f_frsize
    return 100.0 * used / max(1, used + avail)


def load_stem_manifest() -> dict:
    p = STEMS_DIR / "manifest.json"
    if p.exists():
        return read_json(p)
    return {"schema_version": 1, "generator": "scripts/v6/separate_corpus_v6.py", "demucs": DEMUCS, "format": f"mono {OUT_SR} Hz 16-bit PCM WAV",
            "stems": list(STEM_NAMES), "songs": {}}


def song_done(sha16: str, man: dict) -> bool:
    rec = man["songs"].get(sha16)
    if not rec:
        return False
    return all((STEMS_DIR / sha16 / f"{s}.wav").exists() for s in STEM_NAMES)


def decode_mp3(mp3: Path, dst: Path) -> None:
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp3), "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", "-f", "wav", str(dst)]
    subprocess.run(cmd, check=True)


def separate_one(in_wav: Path, out_dir: Path, model) -> dict:
    import numpy as np
    import soundfile as sf
    import torch
    from demucs.apply import apply_model
    from scipy.signal import resample_poly

    torch.manual_seed(DEMUCS["manual_seed"])
    data, sr = sf.read(str(in_wav), always_2d=True, dtype="float32")
    wav = torch.from_numpy(np.ascontiguousarray(data.T))
    if wav.shape[0] == 1:
        wav = wav.repeat(2, 1)
    ref = wav.mean(0)
    wav_norm = (wav - ref.mean()) / (ref.std() + 1e-8)
    with torch.no_grad():
        sources = apply_model(model, wav_norm[None], device=DEMUCS["device"], split=DEMUCS["split"], overlap=DEMUCS["overlap"], shifts=DEMUCS["shifts"], progress=False)[0]
    sources = sources * ref.std() + ref.mean()
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = {"stems": {}, "sr_in": int(sr), "sr_out": OUT_SR, "duration_s": round(data.shape[0] / sr, 3)}
    for i, name in enumerate(model.sources):
        if name not in STEM_NAMES:
            continue
        mono = sources[i].cpu().numpy().mean(axis=0).astype(np.float64)
        if sr != OUT_SR:
            assert sr % OUT_SR == 0, (sr, OUT_SR)
            mono = resample_poly(mono, 1, sr // OUT_SR)
        mono = np.clip(mono, -1.0, 1.0)
        tmp = out_dir / f"{name}.wav.tmp"
        sf.write(str(tmp), mono.astype(np.float32), OUT_SR, subtype="PCM_16", format="WAV")
        os.replace(tmp, out_dir / f"{name}.wav")
        rec["stems"][name] = {"sha256": sha_file(out_dir / f"{name}.wav"), "bytes": (out_dir / f"{name}.wav").stat().st_size, "n_samples": int(mono.shape[0])}
    return rec


def run(limit: int | None = None) -> int:
    import torch
    torch.set_num_threads(DEMUCS["num_threads"])
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:  # pragma: no cover
        pass
    from demucs.pretrained import get_model
    songs = read_json(MANIFEST)["songs"]
    man = load_stem_manifest()
    STEMS_DIR.mkdir(parents=True, exist_ok=True)
    scratch = STEMS_DIR / "_scratch"
    scratch.mkdir(exist_ok=True)
    prog = {"schema_version": 1, "status": "running", "pid": os.getpid(), "n_songs": len(songs), "n_done": sum(1 for s in songs if song_done(s["sha16"], man)),
            "current": None, "done": [], "failed": [], "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "disk_pct": round(disk_pct(), 2), "per_song_wall_s": {}}
    write_json_atomic(STEMS_DIR / "progress.json", prog)
    log(f"START pid={os.getpid()} n_songs={len(songs)} already_done={prog['n_done']} disk={prog['disk_pct']:.1f}% threads={DEMUCS['num_threads']}")
    model = get_model(DEMUCS["model"])
    model.cpu().eval()
    n_run = 0
    for s in songs:
        sha16 = s["sha16"]
        if song_done(sha16, man):
            continue
        if limit is not None and n_run >= limit:
            break
        d = disk_pct()
        prog["disk_pct"] = round(d, 2)
        if d >= DISK_ABORT_PCT:
            prog["status"] = "aborted_disk"
            write_json_atomic(STEMS_DIR / "progress.json", prog)
            log(f"ABORT disk {d:.1f}% >= {DISK_ABORT_PCT}%")
            return 3
        prog["current"] = sha16
        write_json_atomic(STEMS_DIR / "progress.json", prog)
        t0 = time.time()
        mp3 = WS / s["audio_path"]
        tmp_wav = scratch / f"{sha16}.wav"
        try:
            log(f"SONG {sha16} {s.get('title', '')!r} band={s.get('band')} dur={s.get('duration_s')}s disk={d:.1f}%")
            decode_mp3(mp3, tmp_wav)
            rec = separate_one(tmp_wav, STEMS_DIR / sha16, model)
            rec.update({"audio_path": s["audio_path"], "audio_sha256": s.get("audio_sha256"), "band": s.get("band"), "title": s.get("title"), "wall_s": round(time.time() - t0, 1)})
            man["songs"][sha16] = rec
            write_json_atomic(STEMS_DIR / "manifest.json", man)
            prog["done"].append(sha16)
            prog["n_done"] += 1
            prog["per_song_wall_s"][sha16] = rec["wall_s"]
            log(f"DONE {sha16} wall={rec['wall_s']}s bytes={sum(v['bytes'] for v in rec['stems'].values())} n_done={prog['n_done']}/{len(songs)}")
        except Exception as exc:  # keep going; record the failure
            prog["failed"].append({"sha16": sha16, "error": f"{type(exc).__name__}: {exc}"})
            log(f"FAIL {sha16} {type(exc).__name__}: {exc}")
        finally:
            if tmp_wav.exists():
                tmp_wav.unlink()
        n_run += 1
        prog["current"] = None
        write_json_atomic(STEMS_DIR / "progress.json", prog)
    prog["status"] = "done" if prog["n_done"] == len(songs) else ("partial" if limit is not None else "done_with_failures")
    prog["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    prog["disk_pct"] = round(disk_pct(), 2)
    write_json_atomic(STEMS_DIR / "progress.json", prog)
    log(f"END status={prog['status']} n_done={prog['n_done']}/{len(songs)} failed={len(prog['failed'])} disk={prog['disk_pct']:.1f}%")
    return 0 if prog["status"] == "done" else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 corpus stem separation (htdemucs, deterministic, detached-capable)")
    ap.add_argument("--run", action="store_true", help="run in the foreground")
    ap.add_argument("--detach", action="store_true", help="spawn --run in a new session with output to data/v6/logs/separate.log")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="separate at most N pending songs")
    args = ap.parse_args(argv)
    if args.status:
        p = STEMS_DIR / "progress.json"
        print(p.read_text() if p.exists() else "no progress.json")
        return 0
    if args.detach:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, str(Path(__file__).resolve()), "--run"] + (["--limit", str(args.limit)] if args.limit is not None else [])
        env = dict(os.environ, SEPARATE_V6_DETACHED="1")
        with open(LOG, "a") as lf:
            p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True, cwd=str(WS), env=env)
        print(f"detached pid={p.pid} log={LOG}")
        return 0
    if args.run:
        return run(args.limit)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
