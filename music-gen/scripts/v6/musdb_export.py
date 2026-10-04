#!/usr/bin/python3
"""v6 Phase 1B — export MUSDB18 stems (.stem.mp4) to WAV + manifest for the scorecard reference set.

created: 2026-10-04
milestone: M-V6-SCORECARD-1B

Source: workspace/public/musdb18/{train,test}/*.stem.mp4 (150 songs; NI stems format, 5 stereo
AAC streams at 44.1 kHz: 0=mix, 1=drums, 2=bass, 3=other, 4=vocals). Decoded with
stempeg.read_stems(path, stem_id=[0..4], sample_rate=44100) -> (5, T, 2) float64.

Output: data/v6/public/musdb18/<split>/<song_slug>/
    accompaniment.wav   drums+bass+other summed (what our instrumental generator is compared to):
                        ALWAYS stereo 44.1 kHz 16-bit, both splits
    drums.wav, bass.wav, other.wav   TRAIN split only (the per-instrument timbre reference)
    song.json           per-song record (checkpoint; makes the export resumable/idempotent)
  data/v6/public/musdb18/manifest.json   aggregate: layout decision, per-song records, footprint

Disk budget: 150 songs x ~4 min x 6 stereo 44.1k wavs is ~25 GB; the box had ~16 GB free, and
dropped to ~6 GB mid-export (a concurrent agent). The script therefore probes every song's duration
first (stempeg.Info, no decode) and estimates the footprint of two layouts, picking the first under
--budget-gb (default 9):
    A  everything stereo 44.1 kHz 16-bit
    B  accompaniment stereo 44.1k; the 3 stems mono 22.05 kHz 16-bit (embedding downmixes and
       resamples anyway: CLAP 48k mono, MERT 24k mono, so stems lose nothing the scorecard uses)
  If even B exceeds the budget the run continues with a WARNING recorded in the manifest.
The full mix is NOT written (no consumer: the generator is instrumental, and vocals are never
written either); its RMS/peak are still measured and recorded, and a mix.wav left by an earlier
layout is pruned on resume so the footprint stays within budget. Mixes written before 2026-10-04
19:55 UTC carried a mono 22.05k mix.wav; those were pruned.

Per song the manifest records duration, per-stem RMS dBFS and peak (measured on the full-rate
stereo decode, so independent of the written format), sha256/sha16/bytes of every written wav,
and the count of samples clipped by the 16-bit write (accompaniment = mix - vocals can exceed 1.0
where vocals are out of phase; levels are preserved, clipping is recorded, never rescaled).

Idempotent: a song whose song.json exists and whose listed files exist with matching byte sizes
is skipped (extra files not in the current layout are deleted and dropped from the record).
--verify-and-delete-sources: after an export, re-check every song (files present, sizes AND
sha256 match the manifest) and only then delete the source .stem.mp4 files (README.md is kept);
refuses if any song is missing or mismatched. Deterministic: no PRNG; soxr_hq resampling;
sorted-key atomic JSON. Discipline: /usr/bin/python3 guard; writes only under data/v6; the only
thing it ever removes outside data/v6 is the source .stem.mp4 set, and only on that explicit flag.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402

from scripts.v6.v6_common import env_record, read_json, sha16_of, sha256_file, write_json_atomic  # noqa: E402

SCHEMA_VERSION = "v6.musdb_export.1"
DEFAULT_SOURCE = _WS / "workspace" / "public" / "musdb18"
DEFAULT_OUT = _WS / "data" / "v6" / "public" / "musdb18"
STEM_NAMES = ("mix", "drums", "bass", "other", "vocals")
INSTRUMENT_STEMS = ("drums", "bass", "other")
SR = 44100
FORMATS = {"stereo44k": {"sr": 44100, "channels": 2}, "mono22k": {"sr": 22050, "channels": 1}}
BYTES_PER_SAMPLE = 2  # PCM_16
WAV_HEADER_BYTES = 44


# ----------------------------------------------------------------------------- helpers
def slugify(title: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", title.strip().lower()).strip("_")
    return re.sub(r"_+", "_", s) or "untitled"


def song_title(path: Path) -> str:
    name = path.name
    return name[: -len(".stem.mp4")] if name.endswith(".stem.mp4") else path.stem


def rms_dbfs(x: np.ndarray) -> float:
    r = float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if x.size else 0.0
    return 20.0 * float(np.log10(max(r, 1e-12)))


def wav_bytes(duration_s: float, fmt: str) -> int:
    f = FORMATS[fmt]
    return WAV_HEADER_BYTES + int(round(duration_s * f["sr"])) * f["channels"] * BYTES_PER_SAMPLE


def files_for_split(split: str) -> list[str]:
    """Which wavs a split gets: train = accompaniment + 3 instrument stems; test = accompaniment."""
    return ["accompaniment"] + list(INSTRUMENT_STEMS) if split == "train" else ["accompaniment"]


def layout_formats(layout: str) -> dict:
    """Per-file wav format for layouts A/B (see module docstring)."""
    if layout == "A":
        return {name: "stereo44k" for name in ("accompaniment",) + INSTRUMENT_STEMS}
    fmts = {"accompaniment": "stereo44k"}
    fmts.update({s: "mono22k" for s in INSTRUMENT_STEMS})
    return fmts


def estimate_footprint(durations: dict[str, list[float]], layout: str) -> int:
    fmts = layout_formats(layout)
    total = 0
    for split, durs in durations.items():
        for d in durs:
            total += sum(wav_bytes(d, fmts[name]) for name in files_for_split(split))
    return total


def choose_layout(durations: dict[str, list[float]], budget_bytes: int) -> tuple[str, dict]:
    est = {lay: estimate_footprint(durations, lay) for lay in ("A", "B")}
    chosen = "A" if est["A"] <= budget_bytes else "B"
    note = ("all stereo 44.1k fits the budget" if chosen == "A" else
            "stereo-44.1k-everything exceeds the budget; stems written mono 22.05k, accompaniment kept stereo 44.1k")
    if est[chosen] > budget_bytes:
        note += f"; WARNING smallest layout still exceeds budget by {(est[chosen] - budget_bytes) / 1e9:.2f} GB"
    return chosen, {"estimate_bytes": est, "budget_bytes": int(budget_bytes), "note": note}


def probe_duration(path: Path) -> float:
    import stempeg
    info = stempeg.Info(str(path))
    return float(info.duration(0))


def list_sources(source: Path, splits: list[str], limit: int | None = None) -> dict[str, list[Path]]:
    out = {}
    for split in splits:
        files = sorted(p for p in (source / split).glob("*.stem.mp4") if p.is_file())
        out[split] = files[:limit] if limit else files
    return out


# ----------------------------------------------------------------------------- audio
def decode_stems(path: Path) -> np.ndarray:
    """(5, T, 2) float64 at 44.1 kHz: 0=mix, 1=drums, 2=bass, 3=other, 4=vocals."""
    import stempeg
    S, rate = stempeg.read_stems(str(path), stem_id=[0, 1, 2, 3, 4], sample_rate=SR)
    if int(rate) != SR or S.ndim != 3 or S.shape[0] != 5:
        raise ValueError(f"unexpected stems shape/rate {S.shape} @ {rate} for {path}")
    return np.asarray(S, dtype=np.float64)


def to_format(x: np.ndarray, fmt: str) -> np.ndarray:
    """(T, 2) float at 44.1k -> array in the target format (float32)."""
    f = FORMATS[fmt]
    y = x.mean(axis=1) if f["channels"] == 1 else x
    if f["sr"] != SR:
        import librosa
        y = librosa.resample(np.ascontiguousarray(y.T if y.ndim == 2 else y, dtype=np.float32),
                             orig_sr=SR, target_sr=f["sr"], res_type="soxr_hq")
        y = y.T if y.ndim == 2 else y
    return np.ascontiguousarray(y, dtype=np.float32)


def write_wav(path: Path, y: np.ndarray, sr: int) -> dict:
    """PCM_16 write via a temp file + os.replace; returns {bytes, sha256, sha16, clipped_samples, sr, channels}."""
    import soundfile as sf
    clipped = int(np.count_nonzero(np.abs(y) > 1.0))
    tmp = path.with_name(path.name + ".tmp.wav")
    sf.write(str(tmp), np.clip(y, -1.0, 1.0), sr, subtype="PCM_16")
    os.replace(tmp, path)
    sha = sha256_file(path)
    return {"path": str(path.relative_to(_WS)) if path.is_relative_to(_WS) else str(path),
            "bytes": int(path.stat().st_size), "sha256": sha, "sha16": sha16_of(sha),
            "clipped_samples": clipped, "sr": int(sr), "channels": int(y.shape[1] if y.ndim == 2 else 1),
            "format": "PCM_16"}


# ----------------------------------------------------------------------------- per song
def song_outputs(song_dir: Path, split: str) -> dict[str, Path]:
    return {name: song_dir / f"{name}.wav" for name in files_for_split(split)}


def already_done(song_dir: Path, split: str, log=print) -> dict | None:
    """Return the existing song.json if every listed file exists with its recorded size. Files recorded
    under names that are no longer part of the layout (e.g. an old mix.wav) are deleted and dropped
    from the record, which is rewritten (footprint control on resume)."""
    side = song_dir / "song.json"
    if not side.exists():
        return None
    try:
        rec = read_json(side)
    except Exception:
        return None
    wanted = files_for_split(split)
    for name in wanted:
        f = rec.get("files", {}).get(name)
        p = song_dir / f"{name}.wav"
        if not f or not p.exists() or p.stat().st_size != f.get("bytes"):
            return None
    extra = [name for name in rec.get("files", {}) if name not in wanted]
    if extra:
        for name in extra:
            p = song_dir / f"{name}.wav"
            if p.exists():
                p.unlink()
            rec["files"].pop(name)
        rec["bytes_total"] = int(sum(f["bytes"] for f in rec["files"].values()))
        rec["pruned"] = sorted(set(rec.get("pruned", [])) | set(extra))
        write_json_atomic(side, rec)
        log(f"[export] pruned {extra} from {song_dir.name}")
    return rec


def verify_song(song_dir: Path, rec: dict, split: str, check_sha: bool = True) -> list[str]:
    """Problems with a song's exported files versus its record (empty list = verified)."""
    problems = []
    for name in files_for_split(split):
        f = rec.get("files", {}).get(name)
        p = song_dir / f"{name}.wav"
        if not f:
            problems.append(f"{name}: not in record")
        elif not p.exists():
            problems.append(f"{name}: missing")
        elif p.stat().st_size != f.get("bytes"):
            problems.append(f"{name}: size {p.stat().st_size} != {f.get('bytes')}")
        elif check_sha and sha256_file(p) != f.get("sha256"):
            problems.append(f"{name}: sha256 mismatch")
    return problems


def verify_and_delete_sources(manifest_path: Path, source: Path, out_root: Path, log=print) -> dict:
    """Verify every manifest song (presence, size, sha256) and only then delete the .stem.mp4 sources."""
    man = read_json(manifest_path)
    by_source = {}
    problems = {}
    for rec in man["songs"]:
        song_dir = out_root / rec["split"] / rec["slug"]
        pr = verify_song(song_dir, rec, rec["split"])
        if pr:
            problems[f"{rec['split']}/{rec['slug']}"] = pr
        by_source[rec["source"]] = rec
    expected = {str(p.relative_to(_WS)) if p.is_relative_to(_WS) else str(p)
                for sp in man["n_songs"] for p in (source / sp).glob("*.stem.mp4")}
    missing = sorted(expected - set(by_source))
    if problems or missing:
        log(f"[verify] REFUSING to delete sources: {len(problems)} songs with problems, {len(missing)} sources not in manifest")
        return {"verified": False, "problems": problems, "sources_not_in_manifest": missing, "deleted": []}
    deleted, freed = [], 0
    for src in sorted(by_source):
        p = _WS / src
        if p.exists():
            freed += p.stat().st_size
            p.unlink()
            deleted.append(src)
    log(f"[verify] {len(by_source)} songs verified (size + sha256); deleted {len(deleted)} sources, freed {freed / 1e9:.2f} GB")
    man["sources_deleted"] = {"n": len(deleted), "freed_bytes": int(freed), "when_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                             "verification": "every song: files present, byte sizes and sha256 equal to the record"}
    write_json_atomic(manifest_path, man)
    return {"verified": True, "problems": {}, "sources_not_in_manifest": [], "deleted": deleted, "freed_bytes": int(freed)}


def export_song(src: Path, split: str, out_root: Path, layout: str, log=print) -> dict:
    title = song_title(src)
    slug = slugify(title)
    song_dir = out_root / split / slug
    rec = already_done(song_dir, split, log)
    if rec is not None:
        rec = dict(rec, skipped=True)
        log(f"[export] skip {split}/{slug} (complete)")
        return rec
    t0 = time.time()
    song_dir.mkdir(parents=True, exist_ok=True)
    S = decode_stems(src)
    signals = {name: S[i] for i, name in enumerate(STEM_NAMES)}
    signals["accompaniment"] = S[1] + S[2] + S[3]
    duration_s = S.shape[1] / SR
    rms = {name: round(rms_dbfs(x), 3) for name, x in signals.items()}
    peak = {name: round(float(np.abs(x).max()) if x.size else 0.0, 5) for name, x in signals.items()}
    residual = float(np.abs(signals["mix"] - signals["accompaniment"] - signals["vocals"]).max())
    fmts = layout_formats(layout)
    files = {}
    for name, path in song_outputs(song_dir, split).items():
        y = to_format(signals[name], fmts[name])
        files[name] = write_wav(path, y, FORMATS[fmts[name]]["sr"])
        files[name]["source_stem_format"] = fmts[name]
    rec = {"schema_version": SCHEMA_VERSION, "song": title, "slug": slug, "split": split,
           "source": str(src.relative_to(_WS)) if src.is_relative_to(_WS) else str(src),
           "source_sha16": sha16_of(sha256_file(src)),
           "duration_s": round(duration_s, 3), "n_samples_44k": int(S.shape[1]),
           "rms_dbfs": rms, "peak": peak, "mix_minus_stems_residual_peak": round(residual, 6),
           "layout": layout, "files": files, "bytes_total": int(sum(f["bytes"] for f in files.values())),
           "wall_s": round(time.time() - t0, 2)}
    write_json_atomic(song_dir / "song.json", rec)
    log(f"[export] {split}/{slug} dur={duration_s:.0f}s bytes={rec['bytes_total'] / 1e6:.0f}MB "
        f"acc_rms={rms['accompaniment']:.1f}dBFS clipped={files['accompaniment']['clipped_samples']} wall={rec['wall_s']}s")
    rec["skipped"] = False
    return rec


# ----------------------------------------------------------------------------- driver
def build_manifest(records: list[dict], source: Path, out_root: Path, layout: str, decision: dict,
                   durations: dict[str, list[float]], wall_s: float) -> dict:
    songs = sorted(({k: v for k, v in r.items() if k != "skipped"} for r in records),
                   key=lambda r: (r["split"], r["slug"]))
    footprint = int(sum(r["bytes_total"] for r in songs))
    return {"schema_version": SCHEMA_VERSION, "source_dir": str(source), "out_dir": str(out_root),
            "layout": layout, "layout_formats": layout_formats(layout), "decision": decision,
            "files_per_split": {sp: files_for_split(sp) for sp in durations},
            "n_songs": {sp: len(d) for sp, d in durations.items()},
            "duration_s": {sp: round(sum(d), 1) for sp, d in durations.items()},
            "footprint_bytes": footprint, "footprint_gb": round(footprint / 1e9, 3),
            "songs": songs, "wall_s": round(wall_s, 1), "env": env_record()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--source", default=str(DEFAULT_SOURCE))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--splits", default="train,test")
    ap.add_argument("--budget-gb", type=float, default=9.0, help="footprint budget that selects the layout")
    ap.add_argument("--layout", choices=["auto", "A", "B"], default="auto",
                    help="A: all stereo 44.1k; B: stems+mix mono 22.05k, accompaniment stereo 44.1k")
    ap.add_argument("--limit", type=int, default=0, help="first N songs per split (smoke runs)")
    ap.add_argument("--dry-run", action="store_true", help="probe + estimate only, write nothing")
    ap.add_argument("--verify-and-delete-sources", action="store_true",
                    help="verify every exported song against manifest.json (sizes + sha256), then delete the .stem.mp4 sources")
    args = ap.parse_args(argv)

    def log(msg):
        print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)

    source, out_root = Path(args.source), Path(args.out)
    if args.verify_and_delete_sources:
        res = verify_and_delete_sources(out_root / "manifest.json", source, out_root, log)
        for k, v in sorted(res["problems"].items()):
            log(f"  {k}: {v}")
        return 0 if res["verified"] else 1
    splits = [s.strip() for s in args.splits.split(",") if s.strip()]
    sources = list_sources(source, splits, args.limit or None)
    if not any(sources.values()):
        print(f"no .stem.mp4 files under {source}", file=sys.stderr)
        return 1
    t0 = time.time()
    durations = {sp: [probe_duration(p) for p in files] for sp, files in sources.items()}
    layout, decision = choose_layout(durations, int(args.budget_gb * 1e9))
    if args.layout != "auto":
        layout = args.layout
        decision["note"] += f"; layout forced to {layout} by --layout"
    log(f"probed {sum(len(v) for v in sources.values())} songs in {time.time() - t0:.1f}s; "
        f"estimates A={decision['estimate_bytes']['A'] / 1e9:.2f}GB B={decision['estimate_bytes']['B'] / 1e9:.2f}GB "
        f"budget={args.budget_gb}GB -> layout {layout}: {decision['note']}")
    if args.dry_run:
        return 0
    records = []
    for sp in splits:
        for src in sources[sp]:
            records.append(export_song(src, sp, out_root, layout, log))
    manifest = build_manifest(records, source, out_root, layout, decision, durations, time.time() - t0)
    write_json_atomic(out_root / "manifest.json", manifest)
    log(f"done: {len(records)} songs ({sum(1 for r in records if r['skipped'])} skipped), "
        f"footprint {manifest['footprint_gb']} GB -> {out_root / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
