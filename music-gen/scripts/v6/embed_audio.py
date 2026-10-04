#!/usr/bin/python3
"""v6 Phase 1A — window-level audio embeddings (CLAP / MERT) for distribution-level scoring.

created: 2026-10-04
milestone: M-V6-SCORECARD-1A

What: for every input audio file, decode to mono, resample per backbone, cut fixed windows
(default 10 s, hop 5 s; last partial window dropped; windows quieter than -60 dBFS RMS skipped),
embed each window and write one npz per (file, backbone):

    <out-dir>/<backbone>/<sha16>.npz      arrays: emb (n_windows, d), window_start_s (n_windows,)
    <out-dir>/<backbone>/<sha16>.json     sidecar: path, duration, n_windows, sha256, env, model id/rev

Why windows, not whole songs: the scorecard (distribution_metrics.py) compares *sets* of
embeddings, so a 29-song corpus becomes ~1500 window samples per backbone — enough for
kernel two-sample statistics, while keeping song identity so bootstraps can resample songs.

Backbones (verified API, transformers 5.18):
    clap  laion/clap-htsat-unfused, 48 kHz, pooler_output (512, unit-norm)
    mert  m-a-p/MERT-v1-95M, 24 kHz, last_hidden_state mean||std pooled over frames (1536)

Cache: a file is skipped when its npz+sidecar already exist with matching sha256 and
identical window/hop/silence settings (use --force to re-embed).

Tags (Phase 1B): --tag <label> stores the label in the sidecar ("tag") and writes under a
subdirectory, e.g. <out-dir>/clap/stem=drums/<sha16>.npz, so per-instrument stem embeddings never
mix with full-mix embeddings in the flat <out-dir>/<backbone>/ layout (untagged = unchanged layout;
old sidecars without "tag" are read as untagged).

Determinism: torch.set_num_threads(4), torch.manual_seed(0), inference_mode, eval(); no PRNG
in windowing. HF_HUB_OFFLINE=1 is set by default (models are already cached); set
V6_ALLOW_HF_NETWORK=1 to permit downloads.

Discipline: /usr/bin/python3 guard; outputs under data/v6 (gitignored); never writes audio.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "4", "MKL_NUM_THREADS": "4", "OPENBLAS_NUM_THREADS": "4"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)
if os.environ.get("V6_ALLOW_HF_NETWORK") != "1":
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402

from scripts.v6.v6_common import (  # noqa: E402
    env_record, iter_audio_files, read_json, sha16_of, sha256_file, write_json_atomic)

SCHEMA_VERSION = "v6.embed.1"
DEFAULT_OUT_DIR = _WS / "data" / "v6" / "embeddings"
MODEL_IDS = {"clap": "laion/clap-htsat-unfused", "mert": "m-a-p/MERT-v1-95M"}
BACKBONE_SR = {"clap": 48000, "mert": 24000}


# ----------------------------------------------------------------------------- audio / windows
def load_mono(path: str | os.PathLike, target_sr: int) -> tuple[np.ndarray, float]:
    """Decode with soundfile (handles mp3/wav/flac/ogg), downmix to mono, resample (soxr_hq).
    Returns (float32 mono at target_sr, duration_s of the original)."""
    import soundfile as sf
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    duration_s = float(x.shape[0]) / float(sr)
    x = x.mean(axis=1)
    if sr != target_sr:
        import librosa
        x = librosa.resample(x, orig_sr=sr, target_sr=target_sr, res_type="soxr_hq")
    return np.ascontiguousarray(x, dtype=np.float32), duration_s


def rms_dbfs(x: np.ndarray) -> float:
    r = float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if x.size else 0.0
    return 20.0 * np.log10(max(r, 1e-12))


def cut_windows(x: np.ndarray, sr: int, window_s: float = 10.0, hop_s: float = 5.0,
                silence_dbfs: float = -60.0, max_windows: int | None = None
                ) -> tuple[np.ndarray, np.ndarray]:
    """Fixed windows; drop the trailing partial window; skip windows with RMS < silence_dbfs.
    Returns (windows (n, L) float32, window_start_s (n,) float64). n may be 0."""
    L = int(round(window_s * sr))
    H = int(round(hop_s * sr))
    if L <= 0 or H <= 0:
        raise ValueError("window and hop must be positive")
    starts = list(range(0, len(x) - L + 1, H))
    keep, t0 = [], []
    for s in starts:
        w = x[s:s + L]
        if rms_dbfs(w) < silence_dbfs:
            continue
        keep.append(w)
        t0.append(s / sr)
        if max_windows is not None and len(keep) >= max_windows:
            break
    if not keep:
        return np.zeros((0, L), np.float32), np.zeros((0,), np.float64)
    return np.stack(keep).astype(np.float32), np.asarray(t0, dtype=np.float64)


# ----------------------------------------------------------------------------- backbones
def _snapshot_revision(model_id: str) -> str | None:
    """Commit hash of the cached snapshot actually used (from the resolved config.json path)."""
    try:
        from transformers.utils.hub import cached_file
        p = Path(cached_file(model_id, "config.json"))
        parts = p.parts
        return parts[parts.index("snapshots") + 1] if "snapshots" in parts else None
    except Exception:
        return None


class _Backbone:
    name: str
    sr: int
    dim: int

    def embed(self, windows: np.ndarray, batch_size: int) -> np.ndarray:  # (n, L) -> (n, d)
        raise NotImplementedError

    def info(self) -> dict:
        return {"model_id": MODEL_IDS[self.name], "revision": _snapshot_revision(MODEL_IDS[self.name]),
                "sample_rate": self.sr, "dim": self.dim}


class ClapBackbone(_Backbone):
    name, sr, dim = "clap", 48000, 512

    def __init__(self) -> None:
        import torch
        from transformers import ClapModel, ClapProcessor
        self.torch = torch
        self.model = ClapModel.from_pretrained(MODEL_IDS["clap"]).eval()
        self.proc = ClapProcessor.from_pretrained(MODEL_IDS["clap"])

    def embed(self, windows: np.ndarray, batch_size: int) -> np.ndarray:
        outs = []
        with self.torch.inference_mode():
            for i in range(0, len(windows), batch_size):
                batch = [w for w in windows[i:i + batch_size]]
                inp = self.proc(audio=batch, sampling_rate=self.sr, return_tensors="pt")
                out = self.model.get_audio_features(**inp)
                e = out.pooler_output if hasattr(out, "pooler_output") else out
                outs.append(e.float().cpu().numpy())
        return np.concatenate(outs, axis=0).astype(np.float32)


class MertBackbone(_Backbone):
    name, sr, dim = "mert", 24000, 1536

    def __init__(self) -> None:
        import torch
        from transformers import AutoModel, Wav2Vec2FeatureExtractor
        self.torch = torch
        self.model = AutoModel.from_pretrained(MODEL_IDS["mert"], trust_remote_code=True).eval()
        self.fe = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_IDS["mert"], trust_remote_code=True)

    def embed(self, windows: np.ndarray, batch_size: int) -> np.ndarray:
        outs = []
        with self.torch.inference_mode():
            for i in range(0, len(windows), batch_size):
                batch = [w for w in windows[i:i + batch_size]]
                inp = self.fe(batch, sampling_rate=self.sr, return_tensors="pt")
                frames = self.model(**inp).last_hidden_state  # (b, T, 768)
                pooled = self.torch.cat([frames.mean(dim=1), frames.std(dim=1, unbiased=False)], dim=1)
                outs.append(pooled.float().cpu().numpy())
        return np.concatenate(outs, axis=0).astype(np.float32)


BACKBONES = {"clap": ClapBackbone, "mert": MertBackbone}


def load_backbone(name: str) -> _Backbone:
    from scripts.v6.v6_common import set_torch_determinism
    set_torch_determinism(threads=4, seed=0)
    if name not in BACKBONES:
        raise KeyError(f"unknown backbone {name!r}; choose from {sorted(BACKBONES)}")
    return BACKBONES[name]()


# ----------------------------------------------------------------------------- driver
def embeddings_dir(out_dir: Path, backbone_name: str, tag: str | None = None) -> Path:
    """<out_dir>/<backbone>/ for untagged embeddings, <out_dir>/<backbone>/<tag>/ for tagged ones."""
    if tag is not None and ("/" in tag or tag in ("", ".", "..")):
        raise ValueError(f"invalid tag {tag!r}")
    return Path(out_dir) / backbone_name / tag if tag else Path(out_dir) / backbone_name


def _cache_hit(npz_path: Path, side_path: Path, sha256: str, settings: dict) -> bool:
    if not (npz_path.exists() and side_path.exists()):
        return False
    try:
        side = read_json(side_path)
    except Exception:
        return False
    return side.get("sha256") == sha256 and side.get("settings") == settings


def embed_files(files: list[Path], backbone_name: str, out_dir: Path, window_s: float = 10.0,
                hop_s: float = 5.0, silence_dbfs: float = -60.0, max_windows: int | None = None,
                batch_size: int = 8, force: bool = False, backbone: _Backbone | None = None,
                log=print, tag: str | None = None) -> list[dict]:
    """Embed `files` with one backbone; returns per-file records (also written as sidecars).
    `backbone` may be injected (tests use a fake); otherwise loaded lazily on first miss.
    `tag` (optional) selects the <out_dir>/<backbone>/<tag>/ subdirectory and is stored in the sidecar."""
    settings = {"window_s": window_s, "hop_s": hop_s, "silence_dbfs": silence_dbfs,
                "max_windows": max_windows}
    bdir = embeddings_dir(out_dir, backbone_name, tag)
    bdir.mkdir(parents=True, exist_ok=True)
    records = []
    for f in files:
        t0 = time.time()
        sha = sha256_file(f)
        s16 = sha16_of(sha)
        npz_path, side_path = bdir / f"{s16}.npz", bdir / f"{s16}.json"
        if not force and _cache_hit(npz_path, side_path, sha, settings):
            rec = read_json(side_path)
            rec["cache_hit"] = True
            records.append(rec)
            log(f"[embed:{backbone_name}] cache hit {s16} {f.name}")
            continue
        if backbone is None:
            backbone = load_backbone(backbone_name)
        x, duration_s = load_mono(f, backbone.sr)
        windows, starts = cut_windows(x, backbone.sr, window_s, hop_s, silence_dbfs, max_windows)
        emb = backbone.embed(windows, batch_size) if len(windows) else np.zeros((0, backbone.dim), np.float32)
        tmp = npz_path.with_name(npz_path.name + ".tmp.npz")
        np.savez(tmp, emb=emb, window_start_s=starts)
        os.replace(tmp, npz_path)
        rec = {"schema_version": SCHEMA_VERSION, "backbone": backbone_name, "model": backbone.info(),
               "path": str(f), "name": f.name, "sha256": sha, "sha16": s16, "tag": tag,
               "duration_s": round(duration_s, 3), "n_windows": int(len(windows)),
               "n_windows_total": int(max(0, (len(x) - int(round(window_s * backbone.sr)))
                                           // int(round(hop_s * backbone.sr)) + 1)),
               "dim": int(emb.shape[1]), "settings": settings, "env": env_record(),
               "wall_s": round(time.time() - t0, 3), "npz": str(npz_path)}
        write_json_atomic(side_path, rec)
        rec["cache_hit"] = False
        records.append(rec)
        log(f"[embed:{backbone_name}] {s16} {f.name} n_windows={rec['n_windows']} "
            f"dur={duration_s:.1f}s wall={rec['wall_s']:.1f}s")
    return records


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--inputs", nargs="+", required=True, help="audio files and/or directories")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--backbones", default="clap,mert")
    ap.add_argument("--window", type=float, default=10.0, help="window length in seconds")
    ap.add_argument("--hop", type=float, default=5.0, help="hop in seconds")
    ap.add_argument("--max-windows", type=int, default=None)
    ap.add_argument("--silence-dbfs", type=float, default=-60.0)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--force", action="store_true", help="ignore cache")
    ap.add_argument("--tag", default=None, help="label stored in the sidecar; outputs go to <out-dir>/<backbone>/<tag>/")
    ap.add_argument("--summary-json", default=None, help="optional path for a run summary JSON")
    args = ap.parse_args(argv)

    files = iter_audio_files(args.inputs)
    if not files:
        print("no audio files found", file=sys.stderr)
        return 1
    out_dir = Path(args.out_dir)
    summary = {"schema_version": SCHEMA_VERSION, "env": env_record(), "backbones": {}, "tag": args.tag,
               "inputs": [{"path": str(f), "sha16": sha16_of(sha256_file(f))} for f in files]}
    for name in [b.strip() for b in args.backbones.split(",") if b.strip()]:
        t0 = time.time()
        recs = embed_files(files, name, out_dir, args.window, args.hop, args.silence_dbfs,
                           args.max_windows, args.batch_size, args.force, tag=args.tag)
        summary["backbones"][name] = {
            "n_files": len(recs), "n_windows": int(sum(r["n_windows"] for r in recs)),
            "wall_s": round(time.time() - t0, 2),
            "cache_hits": int(sum(1 for r in recs if r.get("cache_hit"))),
            "files": [{"sha16": r["sha16"], "n_windows": r["n_windows"], "wall_s": r.get("wall_s")}
                      for r in recs]}
    if args.summary_json:
        write_json_atomic(args.summary_json, summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "inputs"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
