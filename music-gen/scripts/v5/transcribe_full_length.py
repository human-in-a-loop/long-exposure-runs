#!/usr/bin/python3
"""c79 P3 — full-length corpus transcription driver (checkpointed, detached-safe).

created: 2026-09-06T00:00:00Z
cycle: 79
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/full-length-transcription-launched-c79

Composes the c22/c24 READ-ONLY building blocks — `scripts/v3_spine/recreate_v3.py`
stage functions (slice / htdemucs_6s / chunked MuScriptor) and
`scripts/v3_spine/stage_cache.py` — into a per-song full-length pipeline:

    decode_full  ->  htdemucs_6s  ->  muscriptor x7 (per-probe cached)
                 ->  canonicalize (c4 serializer @ bpm_v5)  ->  transcription_manifest.json
                 ->  delete transient full-length audio (storage hygiene)

Why a sibling and not `recreate_v3_checkpointed.py`: that driver only accepts
`--section operator` (a 30 s window from focus_set_v2.json; `auto` raises
NotImplementedError) and always renders/mixes. v5 needs whole songs from the
26-song corpus manifest, tempo from `tempo_v5.json` (never librosa default,
never 120), per-probe resumability, and delete-after-transcribe hygiene.

Storage hygiene (BINDING): songs run sequentially; df checked before every
stage (85 % warn / 90 % abort). The c27 `df_guard_before_stage` prune step is
NOT used because it deletes `data/v4/profiles/**` sweep WAVs, which are FROZEN
under the v5 reopening; only this driver's own transient audio is ever removed.
Transient audio per song <= ~330 MB (full.wav + 6 stems for a 5-min song).

Determinism: every stage is a pure function of hashed inputs + env pin; the
stage_cache manifest IS the determinism record (c24 doctrine). verify_det x2 is
NOT run in-line (it would double a multi-hour job); a `--verify-det` flag is
reserved for a future cycle's two-fresh-runs proof on one song.

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state
APIs; v3/v4 anchors READ-ONLY (imported, never written).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
         "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
         "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
sys.path.insert(0, str(_WS))

from scripts.v3_spine import recreate_v3 as _v3  # noqa: E402  READ-ONLY
from scripts.v3_spine import stage_cache as _sc  # noqa: E402  READ-ONLY
from scripts.v3_spine.midi_from_json_events import serialize as canonical_midi_serialize  # noqa: E402
from scripts.v3_spine.v3_pipeline.env_pin import build_env_pin_manifest  # noqa: E402
from scripts.sound_match._sweep_hygiene_c27 import _disk_used_pct_user  # noqa: E402  READ-ONLY (no prune)

CANONICAL_ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
STEMS = ["drums", "bass", "guitar", "other", "piano", "vocals"]
PROBES = STEMS + ["full_mix"]
# c3 vocab mapping (docs/specs/v3_spine_instrument_whitelist_mapping.md) — v5 uses it verbatim.
WHITELIST_V5 = {
    "drums": "drums",
    "bass": "electric_bass,acoustic_bass",
    "guitar": "acoustic_guitar,clean_electric_guitar,distorted_electric_guitar",
    "piano": "acoustic_piano,electric_piano,organ",
    "other": "synth_lead,synth_pad,synth_strings,orchestra_hit,chromatic_percussion",
    "vocals": "voice",
    "full_mix": None,
}
DRUM_CLASSES = {"kick": (35, 36), "snare": (37, 38, 39, 40), "hat": (42, 44, 46)}
DF_WARN = 85.0
DF_ABORT = 90.0
TRANSIENT_BUDGET_MB = 500

_MAX_DF = {"pct": 0.0}
_MODEL_SHA = {"v": ""}  # MuScriptor model sha256, hashed once per run (1.2 GB file)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def df_check(stage: str, path: Path) -> float:
    pct = _disk_used_pct_user(path if path.exists() else _WS)
    _MAX_DF["pct"] = max(_MAX_DF["pct"], pct)
    if pct >= DF_ABORT:
        raise RuntimeError(f"df-guard abort before {stage}: {pct:.1f}% >= {DF_ABORT}% (FD-1 halt)")
    if pct >= DF_WARN:
        print(f"  [df] WARN {pct:.1f}% >= {DF_WARN}% before {stage} (prune disabled: v4 profiles FROZEN)")
    return pct


def dir_mb(d: Path) -> float:
    return sum(p.stat().st_size for p in d.rglob("*") if p.is_file()) / 1e6 if d.exists() else 0.0


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(msg: str) -> None:
    print(f"[{now()}] {msg}", flush=True)


# ---------------------------------------------------------------------------
def decode_full(mp3: Path, dst: Path) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".wav.tmp")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(mp3),
                    "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", "-f", "wav", str(tmp)],
                   check=True, env=_v3.sub_env())
    tmp.replace(dst)
    return sha(dst)


def count_notes(events: list) -> dict:
    starts = [e for e in events if e.get("type") == "start"]
    by_inst: dict[str, int] = {}
    for e in starts:
        by_inst[str(e.get("instrument"))] = by_inst.get(str(e.get("instrument")), 0) + 1
    return {"n_note_on": len(starts), "by_instrument": dict(sorted(by_inst.items()))}


def drum_classes(events: list) -> dict:
    out = {k: 0 for k in DRUM_CLASSES}
    out["other_pitches"] = 0
    for e in events:
        if e.get("type") != "start":
            continue
        p = e.get("pitch")
        hit = False
        for k, pitches in DRUM_CLASSES.items():
            if p in pitches:
                out[k] += 1
                hit = True
                break
        if not hit:
            out["other_pitches"] += 1
    return out


# ---------------------------------------------------------------------------
def process_song(song: dict, tempo_dir: Path, env_pin_sha: str, keep_audio: bool,
                 dry_run: bool) -> dict:
    sha16 = song["sha16"]
    mp3 = Path(song["audio_path"])
    work = Path("data/v5/corpus") / sha16
    work.mkdir(parents=True, exist_ok=True)
    tempo_json = tempo_dir / sha16 / "tempo_v5.json"
    if not tempo_json.exists():
        raise RuntimeError(f"{sha16}: tempo_v5.json missing at {tempo_json} — bar grid needs bpm_v5 (RC5 class); halting song per FD-1")
    tempo = json.loads(tempo_json.read_text())
    bpm_v5 = float(tempo["bpm_v5"])
    rec: dict = {"sha16": sha16, "title": song.get("title"), "audio_sha256": song["audio_sha256"],
                 "duration_s": song["duration_s"], "bpm_v5": bpm_v5, "tempo_v5_json_sha256": sha(tempo_json),
                 "stages": {}, "cache_keys": {}, "started": now()}
    if dry_run:
        rec["dry_run"] = True
        return rec

    tmp_dir = work / "_transient"
    full_wav = tmp_dir / "full.wav"
    stem_dir = tmp_dir / "stems_full"
    ms_dir = work / "muscriptor_full"
    canon_dir = work / "canonical_midi_full"

    # --- stage 1: decode_full (manifest-only cache; audio is transient) ---------
    df_check("decode_full", work)
    t0 = time.time()
    inputs = {"mp3": mp3}
    hit = _sc.check("v5_decode_full", inputs, env_pin_sha, work)
    need_wav = not (full_wav.exists() and hit and sha(full_wav) == hit.get("result", {}).get("full_wav_sha256"))
    full_sha = None
    if not need_wav:
        full_sha = hit["result"]["full_wav_sha256"]
        rec["stages"]["decode_full"] = {"cache_hit": True}
    else:
        full_sha = decode_full(mp3, full_wav)
        m = _sc.record("v5_decode_full", inputs, env_pin_sha, work, {}, time.time() - t0,
                       {"full_wav_sha256": full_sha, "note": "audio transient; not copied into cache"})
        rec["stages"]["decode_full"] = {"cache_hit": False, "wall_s": round(time.time() - t0, 1)}
    rec["cache_keys"]["decode_full"] = _sc.compute_key("v5_decode_full", inputs, env_pin_sha)
    rec["full_wav_sha256"] = full_sha
    log(f"{sha16} decode_full {rec['stages']['decode_full']} sha={full_sha[:12]}")

    # --- stage 2: htdemucs_6s full-length -------------------------------------
    df_check("htdemucs_6s", work)
    t0 = time.time()
    inputs = {"full_wav_sha256": full_sha, "model": "htdemucs_6s"}
    hit = _sc.check("v5_htdemucs_6s", inputs, env_pin_sha, work)
    stems_ok = (hit is not None and all((stem_dir / f"{s}.wav").exists() for s in STEMS)
                and all(sha(stem_dir / f"{s}.wav") == hit.get("result", {}).get("stems", {}).get(s) for s in STEMS))
    # MuScriptor may already be fully cached -> stems are not needed at all.
    ms_all_cached = all((ms_dir / f"{p}.json").exists() for p in PROBES) and hit is not None
    if stems_ok or ms_all_cached:
        rec["stages"]["htdemucs_6s"] = {"cache_hit": True, "stems_present": stems_ok}
        stem_shas = hit["result"]["stems"]
    else:
        if not full_wav.exists():
            full_sha = decode_full(mp3, full_wav)
        stem_dir.mkdir(parents=True, exist_ok=True)
        stem_shas = _v3._run_htdemucs_once(full_wav, stem_dir)
        _sc.record("v5_htdemucs_6s", inputs, env_pin_sha, work, {}, time.time() - t0,
                   {"stems": stem_shas, "note": "stems transient; deleted after canonicalize"})
        rec["stages"]["htdemucs_6s"] = {"cache_hit": False, "wall_s": round(time.time() - t0, 1)}
    rec["cache_keys"]["htdemucs_6s"] = _sc.compute_key("v5_htdemucs_6s", inputs, env_pin_sha)
    rec["stem_sha256"] = stem_shas
    log(f"{sha16} htdemucs_6s {rec['stages']['htdemucs_6s']} transient={dir_mb(tmp_dir):.0f}MB")
    if dir_mb(tmp_dir) > TRANSIENT_BUDGET_MB:
        log(f"  [hygiene] transient {dir_mb(tmp_dir):.0f} MB exceeds {TRANSIENT_BUDGET_MB} MB budget — disclosed, continuing (single song in flight)")

    # --- stage 3: MuScriptor per probe (cached at probe granularity) ----------
    ms_dir.mkdir(parents=True, exist_ok=True)
    rec["stages"]["muscriptor"] = {}
    with cf.ThreadPoolExecutor(max_workers=max(1, min(4, os.cpu_count() or 2))) as pool:
        for probe in PROBES:
            df_check(f"muscriptor:{probe}", work)
            wav_sha = full_sha if probe == "full_mix" else stem_shas[probe]
            inputs = {"wav_sha256": wav_sha, "instruments": WHITELIST_V5[probe] or "ALL",
                      "chunk_s": _v3.CHUNK_LEN_S, "overlap_s": _v3.CHUNK_OVERLAP_S,
                      "muscriptor_model_sha256": _MODEL_SHA["v"]}
            out_json = ms_dir / f"{probe}.json"
            hit = _sc.check(f"v5_muscriptor_{probe}", inputs, env_pin_sha, work)
            t0 = time.time()
            if hit is not None and out_json.exists() and sha(out_json) == hit["outputs"].get(f"{probe}.json"):
                rec["stages"]["muscriptor"][probe] = {"cache_hit": True}
            else:
                wav = full_wav if probe == "full_mix" else stem_dir / f"{probe}.wav"
                if not wav.exists():
                    raise RuntimeError(f"{sha16}: {wav} missing for probe {probe} (stems deleted?) — rerun htdemucs stage")
                _v3._muscriptor_chunked(wav, out_json, WHITELIST_V5[probe], pool)
                _sc.record(f"v5_muscriptor_{probe}", inputs, env_pin_sha, work,
                           {f"{probe}.json": out_json}, time.time() - t0)
                rec["stages"]["muscriptor"][probe] = {"cache_hit": False, "wall_s": round(time.time() - t0, 1)}
            rec["cache_keys"][f"muscriptor_{probe}"] = _sc.compute_key(f"v5_muscriptor_{probe}", inputs, env_pin_sha)
            log(f"{sha16} muscriptor {probe:8s} {rec['stages']['muscriptor'][probe]}")

    # --- stage 4: canonicalize @ bpm_v5 ----------------------------------------
    df_check("canonicalize", work)
    canon_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    inputs = {f"json_{p}": ms_dir / f"{p}.json" for p in PROBES}
    inputs.update({"bpm_v5": round(bpm_v5, 6), "meter": "4/4", "serializer": Path("scripts/v3_spine/midi_from_json_events.py")})
    hit = _sc.check("v5_canonicalize", inputs, env_pin_sha, work)
    if hit is not None and all((canon_dir / f"{p}.mid").exists() and sha(canon_dir / f"{p}.mid") == hit["outputs"].get(f"{p}.mid") for p in PROBES):
        rec["stages"]["canonicalize"] = {"cache_hit": True}
    else:
        for p in PROBES:
            canonical_midi_serialize(str(ms_dir / f"{p}.json"), str(canon_dir / f"{p}.mid"), bpm_v5, (4, 4))
        _sc.record("v5_canonicalize", inputs, env_pin_sha, work, {f"{p}.mid": canon_dir / f"{p}.mid" for p in PROBES},
                   time.time() - t0)
        rec["stages"]["canonicalize"] = {"cache_hit": False, "wall_s": round(time.time() - t0, 1)}
    rec["cache_keys"]["canonicalize"] = _sc.compute_key("v5_canonicalize", inputs, env_pin_sha)
    rec["canonical_midi_sha256"] = {p: sha(canon_dir / f"{p}.mid") for p in PROBES}
    rec["muscriptor_json_sha256"] = {p: sha(ms_dir / f"{p}.json") for p in PROBES}

    # --- per-stem note counts (honest, incl. other/piano) ---------------------
    counts = {}
    for p in PROBES:
        ev = json.loads((ms_dir / f"{p}.json").read_text())
        c = count_notes(ev)
        if p == "drums":
            c["gm_classes"] = drum_classes(ev)
        counts[p] = c
    rec["note_counts"] = counts
    rec["other_piano_zero_finding"] = {"other_n_note_on": counts["other"]["n_note_on"],
                                       "piano_n_note_on": counts["piano"]["n_note_on"],
                                       "either_zero": counts["other"]["n_note_on"] == 0 or counts["piano"]["n_note_on"] == 0}
    rec["bar_count_at_bpm_v5"] = round(song["duration_s"] * bpm_v5 / 60.0 / 4.0, 2)

    # --- hygiene: delete transient audio ---------------------------------------
    deleted = []
    if not keep_audio and not song.get("asset_inventory", {}).get("full_length_stems_present"):
        for p in list(stem_dir.glob("*.wav")) + [full_wav]:
            if p.exists():
                deleted.append({"path": str(p), "bytes": p.stat().st_size})
                p.unlink()
        shutil.rmtree(tmp_dir, ignore_errors=True)
    rec["transient_audio_deleted"] = deleted
    rec["df_max_pct_observed_so_far"] = round(_MAX_DF["pct"], 2)
    rec["finished"] = now()
    rec["whitelist_v5"] = WHITELIST_V5
    rec["env_pin_sha256_cache_key"] = env_pin_sha
    rec["env_pin_sha256_canonical_7key"] = CANONICAL_ENV_PIN_SHA256
    (work / "transcription_manifest.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    log(f"{sha16} DONE notes={ {p: counts[p]['n_note_on'] for p in PROBES} } bars={rec['bar_count_at_bpm_v5']} df_max={_MAX_DF['pct']:.1f}%")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description="v5 full-length corpus transcription (checkpointed)")
    ap.add_argument("--manifest", default="data/v5/corpus/corpus_manifest.json")
    ap.add_argument("--tempo-dir", default="data/v5/corpus")
    ap.add_argument("--songs", nargs="*", default=None)
    ap.add_argument("--max-songs", type=int, default=None)
    ap.add_argument("--keep-audio", action="store_true", help="do NOT delete transient stems (debug only)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    man = json.loads(Path(args.manifest).read_text())
    songs = sorted([s for s in man["songs"] if s.get("in_v5_corpus")], key=lambda s: s["v5_priority_rank"])
    if args.songs:
        songs = [s for s in songs if s["sha16"] in set(args.songs)]
    if args.max_songs:
        songs = songs[: args.max_songs]

    env_manifest = build_env_pin_manifest()
    env_pin_sha = env_manifest["env_pin_sha256"]
    _MODEL_SHA["v"] = sha(Path(_v3.MUSCRIPTOR_MODEL))
    progress_path = Path("data/v5/corpus/transcription_progress.json")
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else {"songs": {}}
    progress.update({"pid": os.getpid(), "env_pin_sha256_cache_key": env_pin_sha,
                     "canonical_7key_env_pin_sha256": CANONICAL_ENV_PIN_SHA256,
                     "order": [s["sha16"] for s in songs], "last_update": now()})
    log(f"launch pid={os.getpid()} songs={len(songs)} env_pin(cache)={env_pin_sha[:16]} df={_disk_used_pct_user(_WS):.1f}%")
    for s in songs:
        try:
            rec = process_song(s, Path(args.tempo_dir), env_pin_sha, args.keep_audio, args.dry_run)
            progress["songs"][s["sha16"]] = {"status": "done" if not args.dry_run else "dry_run",
                                             "finished": rec.get("finished"), "bpm_v5": rec.get("bpm_v5")}
        except Exception as exc:  # FD-1: record honestly, stop (no retry)
            progress["songs"][s["sha16"]] = {"status": "failed", "error": str(exc)[:500], "at": now()}
            progress["df_max_pct_observed"] = round(_MAX_DF["pct"], 2)
            progress["last_update"] = now()
            progress_path.write_text(json.dumps(progress, sort_keys=True, indent=2) + "\n")
            log(f"{s['sha16']} FAILED: {exc}")
            return 1
        progress["df_max_pct_observed"] = round(_MAX_DF["pct"], 2)
        progress["last_update"] = now()
        progress_path.write_text(json.dumps(progress, sort_keys=True, indent=2) + "\n")
    log("ALL REQUESTED SONGS COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
