#!/usr/bin/python3
"""v6 Phase 5 (iteration 05) — scorecard FAIR scoring mode: match the candidates' audio format to the reference's.

created: 2026-10-05
milestone: M-V6-ITER-05/localize

Why: `corpus_accomp` (the fair instrumental reference) is Demucs output, mono 22.05 kHz, while the generator renders
44.1 kHz stereo. Iteration 04 (doc 8.4) showed that band-limiting + mono-ing the candidates removes ~40 % of the CLAP
distance to that reference, i.e. the scorecard was partly measuring the reference's own format. `scorecard.py
--match-reference-format` calls this module: the reference's modal (sample_rate, channels) is probed, every candidate is
resampled (soxr_hq, per channel) and down-mixed (channel mean) / duplicated to that format, written once as 16-bit PCM
under data/v6/scorecard/format_cache/<source sha16>_<sr>hz_<ch>ch.wav with a sidecar, and the TRANSFORMED file (its own
sha256 -> sha16) is what gets embedded, so the embedding cache (keyed by the file's sha) stays reusable across runs and
iterations. A candidate that already has the reference format is used as is (no copy). The run name carries a `_fmt`
suffix and scorecard.json records `candidate_format` (target, per-file source/transformed sha16, cache paths).

Deterministic (soxr is deterministic for a fixed input; the writer is 16-bit PCM with dither off via soundfile); no PRNG;
sorted-key atomic JSON sidecars; never touches the reference audio.
"""
from __future__ import annotations

import time
from collections import Counter
from pathlib import Path

import numpy as np

from scripts.v6.v6_common import env_record, read_json, sha16_of, sha256_file, write_json_atomic

SCHEMA_VERSION = "v6.scorecard_format.1"
RUN_SUFFIX = "_fmt"
SUBTYPE = "PCM_16"


def probe_format(path: Path) -> dict:
    import soundfile as sf
    info = sf.info(str(path))
    return {"sample_rate": int(info.samplerate), "channels": int(info.channels), "subtype": str(info.subtype)}


def reference_format(items: list) -> dict:
    """Modal (sample_rate, channels) over the reference files; `uniform` says whether every file shares it."""
    fmts = [probe_format(Path(it["path"])) for it in items]
    if not fmts:
        raise ValueError("reference set is empty: no format to match")
    counts = Counter((f["sample_rate"], f["channels"]) for f in fmts)
    (sr, ch), n = counts.most_common(1)[0]
    return {"sample_rate": int(sr), "channels": int(ch), "n_files": len(fmts), "n_modal": int(n), "uniform": len(counts) == 1,
            "formats": {f"{k[0]}hz_{k[1]}ch": int(v) for k, v in sorted(counts.items())}}


def transform_audio(x: np.ndarray, sr: int, target_sr: int, target_ch: int) -> np.ndarray:
    """(n, ch) float32 at sr -> (m, target_ch) float32 at target_sr. Channel mean for a down-mix, duplication for an
    up-mix, librosa soxr_hq per channel for the resample. Pure; testable."""
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = x[:, None]
    ch = x.shape[1]
    if target_ch == 1 and ch > 1:
        x = x.mean(axis=1, keepdims=True)
    elif target_ch > ch:
        x = np.repeat(x[:, :1], target_ch, axis=1) if ch == 1 else np.concatenate([x] + [x[:, -1:]] * (target_ch - ch), axis=1)
    elif target_ch < ch:
        x = x[:, :target_ch]
    if int(sr) != int(target_sr):
        import librosa
        x = librosa.resample(np.ascontiguousarray(x.T), orig_sr=int(sr), target_sr=int(target_sr), res_type="soxr_hq").T
    return np.ascontiguousarray(np.clip(x, -1.0, 1.0), dtype=np.float32)


def cache_path(cache_dir: Path, source_sha16: str, fmt: dict) -> Path:
    return Path(cache_dir) / f"{source_sha16}_{fmt['sample_rate']}hz_{fmt['channels']}ch.wav"


def match_item(item: dict, fmt: dict, cache_dir: Path, log=print) -> dict:
    """Return a scorecard item ({path, sha16, label} + source fields) in the reference format. Cache hit when the sidecar's
    source sha256 and target match; a file already in the target format (and 16-bit PCM) passes through untouched."""
    import soundfile as sf
    src = Path(item["path"])
    src_sha = sha256_file(src)
    src16 = sha16_of(src_sha)
    pf = probe_format(src)
    base = {"label": item["label"], "source_path": str(src), "source_sha16": src16,
            "source_format": pf, "target_format": {"sample_rate": fmt["sample_rate"], "channels": fmt["channels"]}}
    if pf["sample_rate"] == fmt["sample_rate"] and pf["channels"] == fmt["channels"] and pf["subtype"] == SUBTYPE:
        return dict(base, path=str(src), sha16=src16, transformed=False, cache_hit=None)
    out = cache_path(cache_dir, src16, fmt)
    side = out.with_suffix(".json")
    hit = False
    if out.exists() and side.exists():
        try:
            s = read_json(side)
            hit = s.get("source_sha256") == src_sha and s.get("target_format") == base["target_format"] and s.get("schema_version") == SCHEMA_VERSION
        except Exception:
            hit = False
    if not hit:
        t0 = time.time()
        x, sr = sf.read(str(src), dtype="float32", always_2d=True)
        y = transform_audio(x, sr, fmt["sample_rate"], fmt["channels"])
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp.wav")
        sf.write(str(tmp), y if fmt["channels"] > 1 else y[:, 0], fmt["sample_rate"], subtype=SUBTYPE)
        tmp.replace(out)
        write_json_atomic(side, {"schema_version": SCHEMA_VERSION, "source_path": str(src), "source_sha256": src_sha, "source_format": pf,
                                 "target_format": base["target_format"], "subtype": SUBTYPE, "n_samples": int(len(y)),
                                 "output_sha256": sha256_file(out), "resampler": "librosa soxr_hq", "downmix": "channel mean",
                                 "env": env_record(), "wall_s": round(time.time() - t0, 3)})
        log(f"[fmt] {src16} {item['label']} {pf['sample_rate']}hz/{pf['channels']}ch -> {fmt['sample_rate']}hz/{fmt['channels']}ch ({time.time() - t0:.1f}s)")
    return dict(base, path=str(out), sha16=sha16_of(sha256_file(out)), transformed=True, cache_hit=bool(hit))


def match_items(items: list, fmt: dict, cache_dir: Path, log=print) -> tuple[list, dict]:
    """All candidates -> (matched items, candidate_format block for scorecard.json)."""
    matched = [match_item(it, fmt, cache_dir, log) for it in items]
    block = {"schema_version": SCHEMA_VERSION, "matched": True, "reference_format": fmt, "cache_dir": str(cache_dir), "subtype": SUBTYPE,
             "n_transformed": sum(1 for m in matched if m["transformed"]), "n_passthrough": sum(1 for m in matched if not m["transformed"]),
             "files": [{k: m[k] for k in ("label", "source_sha16", "sha16", "path", "source_format", "transformed", "cache_hit")} for m in matched]}
    return matched, block


def cached_item(source_sha16: str, fmt: dict, cache_dir: Path, label: str) -> dict | None:
    """The cache entry for a source file that may no longer exist (scratch audio deleted after embedding), or None."""
    out = cache_path(cache_dir, source_sha16, fmt)
    side = out.with_suffix(".json")
    if not (out.exists() and side.exists()):
        return None
    s = read_json(side)
    target = {"sample_rate": fmt["sample_rate"], "channels": fmt["channels"]}
    if s.get("schema_version") != SCHEMA_VERSION or s.get("target_format") != target:
        return None
    return {"label": label, "path": str(out), "sha16": sha16_of(s["output_sha256"]), "source_path": s.get("source_path"), "source_sha16": source_sha16,
            "source_format": s.get("source_format"), "target_format": target, "transformed": True, "cache_hit": True}


def run_name(name: str, matched: bool) -> str:
    """`<name>_fmt` in fair mode (idempotent), the name itself otherwise."""
    if not matched or name.endswith(RUN_SUFFIX):
        return name
    return name + RUN_SUFFIX
