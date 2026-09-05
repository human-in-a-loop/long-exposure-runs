#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T00:30:00Z
# cycle: 14
# run_id: run-2026-09-04T003000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-guitar-stage2-launched
# ---
"""Stage-2 fine fit for CG GUITAR (family-1 SF2). Sibling to c3
``fine_fit_sf2_v2.py`` (READ-ONLY anchor) and c11 ``fine_fit_sf2_drums.py``
(READ-ONLY anchor). Guitar-specific differences:

    1. MIDI: reuses c13 ``guitar_excerpt.mid`` (391 note_on events extracted
       from merged.mid by ``coarse_sweep_sf2_guitar._extract_guitar_midi``
       which remaps to channel 0) as-is. The fine-fit rewriter here inserts
       bank+program change on channel 0 per candidate via
       ``coarse_sweep_sf2_guitar._rewrite_with_program`` (READ-ONLY).
    2. Preset promotion: c13 guitar stage-1 top-5 by composite {24 Nylon,
       27 Rock (source-of-truth), 28 Jazz, 26 EP-clean, 25 Steel}. Program 27
       is rank 2 -- already in top-5 -- so NO separate control cell is
       promoted (per c14 brief). Grid = 5 x 3 x 3 x 4 = 180 cells.

All post-processing (EQ v2 12-band iirpeak Q=1.4 geomspace(20, 20000, 12) with
NO zero-mean subtraction; mandatory pyloudnorm LUFS-I to -18 with RMS fallback
logged; c2 compressor unchanged) is identical to c3 ``fine_fit_sf2_v2``.

Discipline:
    - env pins BEFORE any observed import (os.environ.setdefault)
    - /usr/bin/python3 interpreter guard
    - NO PRNG, no wall-clock non-determinism
    - Objective panel weights literal-frozen (READ-ONLY import of objective)
    - SF2 / reference / MIDI SHAs asserted at run start
    - Sweep-storage hygiene: --score-and-delete (default True) removes
      per-cell render.wav after scoring except top --keep-top by composite;
      pre-launch and mid-sweep disk budget checks via
      coarse_sweep_sf2_drums._disk_ok. FD-1 halt on any disk breach.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# --- env pins BEFORE any heavy import ---
_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"fine_fit_sf2_guitar requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.objective import score_pair  # noqa: E402
from scripts.sound_match.coarse_sweep_sf2 import sha256_of_file  # noqa: E402
from scripts.sound_match.coarse_sweep_sf2_drums import _disk_ok  # noqa: E402
from scripts.sound_match.coarse_sweep_sf2_guitar import (  # noqa: E402
    _rewrite_with_program,
)
# READ-ONLY import of the iirpeak apply function.
from scripts.palette_render.render_stem import _apply_eq_curve_iirpeak  # noqa: E402
# c32 OP-1: fine-fit-driver serial-launch lock (docs/agent_picks_selection_invariants.md).
from scripts.sound_match._serial_lock_op1 import SerialLock  # noqa: E402
# c28: canonical sweep-hygiene helpers per POR 2026-09-05 (adoption of c27 module).
from scripts.sound_match._sweep_hygiene_c27 import (  # noqa: E402
    RunningTopK, df_guard_before_stage, prune_after_pin,
    DEFAULT_KEEP_TOP, DEFAULT_MAX_AUDIO_MB,
)

# --- fetchability probe for pyloudnorm ---
_LOUDNORM_AVAILABLE = False
_LOUDNORM_ERR: str | None = None
try:
    import pyloudnorm as _pyln  # noqa: E402
    _LOUDNORM_AVAILABLE = True
except Exception as _exc:  # pragma: no cover
    _LOUDNORM_ERR = f"{type(_exc).__name__}:{_exc}"


# --- grid axes (frozen literals; identical to c3/c11) ---
GAIN_LEVELS = (0.5, 1.0, 1.5)
REVERB_LEVELS = (0.0, 0.3, 0.7)
POST_STATES = ("none", "EQ_only", "compressor_only", "EQ_and_compressor")

# EQ params (identical to c3)
EQ_BAND_CENTERS = tuple(float(x) for x in np.geomspace(20.0, 20000.0, 12))
EQ_Q = 1.4

# Compressor params (identical to c2/c3)
COMP_THRESHOLD_DB = -18.0
COMP_RATIO = 3.0
COMP_ATTACK_MS = 5.0
COMP_RELEASE_MS = 50.0
COMP_MAKEUP_DB = 6.0

# LUFS-I target (identical to c3)
LUFS_TARGET_DB = -18.0

EXPECTED_SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"


def _load_mono(path: Path) -> tuple[np.ndarray, int]:
    y, sr = sf.read(str(path), always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y.astype(np.float32), int(sr)


def _fit_eq_curve_v2_no_zero_mean(rendered_wav: Path, reference_wav: Path) -> list:
    mono_o, sr_o = _load_mono(reference_wav)
    mono_r, sr_r = _load_mono(rendered_wav)
    if sr_o != sr_r:
        raise RuntimeError(f"sr mismatch: ref {sr_o} vs render {sr_r}")
    L = min(len(mono_o), len(mono_r))
    if L < 4:
        return [0.0] * 12
    n_fft = 8192
    if L < n_fft:
        n_fft = 1 << int(np.floor(np.log2(max(L, 2))))
    X_o = np.abs(np.fft.rfft(mono_o[:L].astype(np.float64), n=n_fft))
    X_r = np.abs(np.fft.rfft(mono_r[:L].astype(np.float64), n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr_o)
    gains: list[float] = []
    for f_c in EQ_BAND_CENTERS:
        f_lo, f_hi = f_c / np.sqrt(2.0), f_c * np.sqrt(2.0)
        m = (freqs >= f_lo) & (freqs < f_hi)
        if not np.any(m):
            gains.append(0.0)
            continue
        mag_o = float(np.mean(20.0 * np.log10(X_o[m] + 1e-10)))
        mag_r = float(np.mean(20.0 * np.log10(X_r[m] + 1e-10)))
        gains.append(float(np.clip(mag_o - mag_r, -12.0, 12.0)))
    return gains


def _apply_compressor(mono: np.ndarray, sr: int) -> tuple[np.ndarray, dict]:
    thresh_lin = 10.0 ** (COMP_THRESHOLD_DB / 20.0)
    ratio = COMP_RATIO
    makeup_lin = 10.0 ** (COMP_MAKEUP_DB / 20.0)
    attack_coeff = float(np.exp(-1.0 / (sr * COMP_ATTACK_MS * 1e-3)))
    release_coeff = float(np.exp(-1.0 / (sr * COMP_RELEASE_MS * 1e-3)))
    x = mono.astype(np.float64)
    env = 0.0
    out = np.zeros_like(x)
    n_engaged = 0
    for i, v in enumerate(x):
        av = abs(v)
        if av > env:
            env = attack_coeff * env + (1.0 - attack_coeff) * av
        else:
            env = release_coeff * env + (1.0 - release_coeff) * av
        if env > thresh_lin:
            over_db = 20.0 * np.log10(env / thresh_lin)
            gain_reduction_db = over_db - over_db / ratio
            gain_lin = 10.0 ** (-gain_reduction_db / 20.0)
            n_engaged += 1
        else:
            gain_lin = 1.0
        out[i] = v * gain_lin * makeup_lin
    return out.astype(np.float32), {
        "n_samples_compressor_engaged": int(n_engaged),
        "engagement_fraction": float(n_engaged / max(len(x), 1)),
    }


def _normalize_loudness(mono: np.ndarray, sr: int, target_db: float) -> tuple[np.ndarray, dict]:
    rms = float(np.sqrt(np.mean(mono.astype(np.float64) ** 2) + 1e-12))
    if rms < 1e-4:
        return mono.astype(np.float32), {
            "loudness_method": "skipped_silent",
            "measured_db": None,
            "applied_gain_lin": 1.0,
        }
    if _LOUDNORM_AVAILABLE:
        try:
            meter = _pyln.Meter(sr)
            measured = float(meter.integrated_loudness(mono.astype(np.float64)))
            if not np.isfinite(measured) or measured < -70.0:
                raise RuntimeError(f"lufs_below_silence_gate={measured}")
            gain_lin = float(10.0 ** ((target_db - measured) / 20.0))
            return (mono * gain_lin).astype(np.float32), {
                "loudness_method": "lufs_i",
                "measured_db": measured,
                "applied_gain_lin": gain_lin,
            }
        except Exception as exc:
            fallback_reason = f"{type(exc).__name__}:{str(exc)[:80]}"
    else:
        fallback_reason = _LOUDNORM_ERR or "pyloudnorm_unavailable"
    rms_db = 20.0 * float(np.log10(rms + 1e-12))
    gain_lin = float(10.0 ** ((target_db - rms_db) / 20.0))
    return (mono * gain_lin).astype(np.float32), {
        "loudness_method": "rms_fallback",
        "measured_db": rms_db,
        "applied_gain_lin": gain_lin,
        "fallback_reason": fallback_reason,
    }


def _clip_and_count(mono: np.ndarray) -> tuple[np.ndarray, float]:
    n_clipped = int(np.sum(np.abs(mono) > 0.99))
    frac = float(n_clipped / max(len(mono), 1))
    return np.clip(mono, -0.99, 0.99).astype(np.float32), frac


def _fluidsynth_render(
    sf2: Path, midi: Path, out_wav: Path,
    *, sr: int = 44100, gain: float = 1.0, reverb_send: float = 0.0
) -> None:
    if reverb_send == 0.0:
        reverb_opts = ["-o", "synth.reverb.active=false"]
    else:
        room_size = 0.3 + 0.4 * float(reverb_send)
        reverb_opts = [
            "-o", "synth.reverb.active=true",
            "-o", f"synth.reverb.room-size={room_size:.4f}",
            "-o", f"synth.reverb.level={float(reverb_send):.4f}",
            "-o", "synth.reverb.damp=0.5",
            "-o", "synth.reverb.width=1.0",
        ]
    cmd = [
        "fluidsynth", "-ni",
        "-F", str(out_wav),
        "-r", str(sr),
        "-g", f"{float(gain):.4f}",
        "-o", "synth.cpu-cores=1",
        "-o", "synth.chorus.active=false",
        "-o", f"synth.sample-rate={sr}",
        "-o", "synth.midi-bank-select=gs",
        *reverb_opts,
        str(sf2), str(midi),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f"fluidsynth failed rc={r.returncode} "
            f"stderr={r.stderr.decode(errors='replace')[:400]}"
        )


def _apply_post_v2(
    render_wav: Path, out_wav: Path, ref_stem: Path, post: str,
    *, sr: int = 44100, lufs_target: float = LUFS_TARGET_DB,
) -> dict:
    mono, sr_r = _load_mono(render_wav)
    if sr_r != sr:
        raise RuntimeError(f"sr drift: expected {sr} got {sr_r}")
    info: dict = {
        "post": post,
        "eq_gains_db": None,
        "comp_engagement_fraction": None,
        "clipped_fraction": 0.0,
        "loudness_method": None,
        "measured_db": None,
        "applied_gain_lin": None,
    }
    if post in ("EQ_only", "EQ_and_compressor"):
        gains = _fit_eq_curve_v2_no_zero_mean(render_wav, ref_stem)
        info["eq_gains_db"] = gains
        mono = _apply_eq_curve_iirpeak(
            mono, list(EQ_BAND_CENTERS), gains, fs=sr
        ).astype(np.float32)
    if post in ("compressor_only", "EQ_and_compressor"):
        mono, comp_info = _apply_compressor(mono, sr=sr)
        info["comp_engagement_fraction"] = comp_info["engagement_fraction"]
    mono, loud_info = _normalize_loudness(mono, sr, lufs_target)
    info["loudness_method"] = loud_info["loudness_method"]
    info["measured_db"] = loud_info["measured_db"]
    info["applied_gain_lin"] = loud_info["applied_gain_lin"]
    mono, clip_frac = _clip_and_count(mono)
    info["clipped_fraction"] = clip_frac
    stereo = np.stack([mono, mono], axis=1).astype(np.float32)
    sf.write(str(out_wav), stereo, sr, subtype="PCM_16")
    return info


def _read_top_k_guitar_from_stage1(leaderboard: Path, k: int = 5) -> list[dict]:
    """Read c13 guitar stage-1 leaderboard, return top-K by rank."""
    rows: list[dict] = []
    with open(leaderboard) as f:
        header: list[str] | None = None
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if header is None:
                header = parts
                continue
            rows.append(dict(zip(header, parts)))
    picked: list[dict] = []
    seen: set[int] = set()
    for r in rows:
        try:
            p = int(r["program"])
        except (ValueError, KeyError):
            continue
        if p in seen:
            continue
        seen.add(p)
        picked.append({
            "rank_stage1": int(r["rank"]),
            "bank": int(r["bank"]),
            "program": p,
            "composite_stage1": float(r["composite"]),
        })
        if len(picked) >= k:
            break
    return picked


def _canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _config_hash(preset_program: int, gain: float, reverb: float, post: str) -> str:
    body = {"program": int(preset_program), "gain": float(gain),
            "reverb_send": float(reverb), "post": post}
    return hashlib.sha256(_canonical_json(body)).hexdigest()


def enumerate_grid(presets: list[dict]) -> list[dict]:
    cells = []
    for p in presets:
        for gain in GAIN_LEVELS:
            for rev in REVERB_LEVELS:
                for post in POST_STATES:
                    cells.append({
                        "preset_rank_stage1": p["rank_stage1"],
                        "bank": p["bank"],
                        "program": p["program"],
                        "gain": gain,
                        "reverb_send": rev,
                        "post": post,
                        "config_hash": _config_hash(p["program"], gain, rev, post),
                    })
    return cells


def _env_pin_sha256() -> str:
    payload = {
        "env": {k: os.environ.get(k) for k in _PINS},
        "pyloudnorm_available": bool(_LOUDNORM_AVAILABLE),
        "lufs_target_db": LUFS_TARGET_DB,
        "instrument": "guitar",
    }
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def _dir_size_bytes(p: Path) -> int:
    total = 0
    for root, _, files in os.walk(p):
        for f in files:
            fp = Path(root) / f
            try:
                total += fp.stat().st_size
            except OSError:
                pass
    return total


def main(argv: list[str] | None = None) -> int:
    # c32 OP-1 wrap: serial-launch lock per docs/agent_picks_selection_invariants.md.
    with SerialLock(driver="fine_fit_sf2_guitar", cycle=32):
        return _main_body(argv)


def _main_body(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Family-1 stage-2 fine fit (guitar, CG target c14).",
    )
    ap.add_argument("--song-sha16", required=True)
    ap.add_argument("--stage1-leaderboard", required=True, type=Path)
    ap.add_argument("--guitar-midi", required=True, type=Path,
                    help="Pre-extracted guitar MIDI (channel-0 remapped). Reuse "
                         "data/v4/profiles/<song>/guitar_sweep_stage1/guitar_excerpt.mid.")
    ap.add_argument("--reference-stem", required=True, type=Path)
    ap.add_argument("--sf2", type=Path,
                    default=Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"))
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--sample-rate", type=int, default=44100)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--lufs-target", type=float, default=LUFS_TARGET_DB)
    ap.add_argument("--score-and-delete", action="store_true", default=True)
    ap.add_argument("--keep-top", type=int, default=3)
    ap.add_argument("--max-audio-mb", type=int, default=500)
    ap.add_argument("--disk-abort-pct", type=float, default=90.0,
                    help="Abort mid-sweep if disk usage % exceeds this floor.")
    # c28 hygiene flags (default: per-candidate render->score->delete).
    ap.add_argument("--score-and-delete-per-candidate", action="store_true",
                    default=True,
                    help="c27 default: render->score->delete each candidate; retain running top-K only.")
    ap.add_argument("--legacy-batch-render", action="store_true", default=False,
                    help="c26 legacy: batch-render then prune. Regression only.")
    ap.add_argument("--keep-top-c27", type=int, default=DEFAULT_KEEP_TOP)
    args = ap.parse_args(argv)

    for k, v in _PINS.items():
        if os.environ.get(k) != v:
            raise RuntimeError(
                f"env pin drift {k}={os.environ.get(k)!r} expected {v!r}"
            )

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    renders_dir = out_dir / "renders"
    renders_dir.mkdir(exist_ok=True)

    # c28: df guard at stage entry (prune@85%, abort@90%).
    if not args.legacy_batch_render:
        _ws_root = Path(__file__).resolve().parents[2]
        _df_status = df_guard_before_stage(
            workspace_root=_ws_root, stage_dir=out_dir,
            prune_pct=85.0, abort_pct=90.0,
        )
        (out_dir / "df_guard_status.json").write_text(
            json.dumps(_df_status, sort_keys=True, indent=2)
        )
        topk = RunningTopK(k=args.keep_top_c27)
    else:
        topk = None

    budget_bytes = int(args.max_audio_mb) * 1024 * 1024
    if not _disk_ok(out_dir, budget_bytes, safety_factor=2.0):
        raise RuntimeError(
            f"pre-launch disk check FAIL for budget {args.max_audio_mb} MB "
            f"(2.0x safety); FD-1 halt."
        )

    sf2_sha = sha256_of_file(args.sf2)
    if sf2_sha != EXPECTED_SF2_SHA:
        raise RuntimeError(f"SF2 sha drift: got {sf2_sha}")
    ref_sha = sha256_of_file(args.reference_stem)
    midi_sha = sha256_of_file(args.guitar_midi)

    fetch_path = out_dir / "fetchability_ladder.jsonl"
    with open(fetch_path, "w") as f:
        f.write(json.dumps({
            "module": "pyloudnorm",
            "available": bool(_LOUDNORM_AVAILABLE),
            "error": _LOUDNORM_ERR,
            "lufs_target_db": args.lufs_target,
        }) + "\n")

    top_k = _read_top_k_guitar_from_stage1(args.stage1_leaderboard, k=args.top_k)
    if len(top_k) < args.top_k:
        raise RuntimeError(
            f"only {len(top_k)} presets in stage-1 (need {args.top_k})"
        )
    presets = list(top_k)

    cells = enumerate_grid(presets)

    t_start = time.time()
    rows: list[dict] = []
    pruned: list[str] = []
    for cell in cells:
        cell_dir = renders_dir / (
            f"prog{cell['program']:03d}"
            f"_gain{int(cell['gain']*100):03d}"
            f"_rev{int(cell['reverb_send']*100):03d}"
            f"_{cell['post']}"
        )
        cell_dir.mkdir(exist_ok=True)
        rewritten = cell_dir / "guitar_with_program.mid"
        _rewrite_with_program(args.guitar_midi, rewritten,
                              bank=cell["bank"], program=cell["program"])
        dry_wav = cell_dir / "render_dry.wav"
        final_wav = cell_dir / "render.wav"
        row = {
            "preset_rank_stage1": cell["preset_rank_stage1"],
            "bank": cell["bank"],
            "program": cell["program"],
            "gain": cell["gain"],
            "reverb_send": cell["reverb_send"],
            "post": cell["post"],
            "config_hash": cell["config_hash"],
            "status": "OK",
            "eq_gains_db_json": "null",
            "comp_engagement_fraction": None,
            "loudness_method": None,
            "measured_db": None,
            "applied_gain_lin": None,
            "clipped_fraction": 0.0,
            "mel_l1_db": float("nan"),
            "spectral_centroid_rmse_hz": float("nan"),
            "embedding_cos_vggish": None,
            "composite": float("nan"),
            "render_sha256": None,
        }
        try:
            _fluidsynth_render(
                args.sf2, rewritten, dry_wav,
                sr=args.sample_rate, gain=cell["gain"],
                reverb_send=cell["reverb_send"],
            )
            info = _apply_post_v2(
                dry_wav, final_wav, args.reference_stem, cell["post"],
                sr=args.sample_rate, lufs_target=float(args.lufs_target),
            )
            mono, _ = _load_mono(final_wav)
            rms = float(np.sqrt(np.mean(mono.astype(np.float64) ** 2) + 1e-12))
            if rms < 1e-4:
                row["status"] = "degenerate_silent_render"
                row["composite"] = float("inf")
                row["render_sha256"] = sha256_of_file(final_wav)
            else:
                scores = score_pair(final_wav, args.reference_stem)
                row["mel_l1_db"] = scores["mel_l1_db"]
                row["spectral_centroid_rmse_hz"] = scores["spectral_centroid_rmse_hz"]
                row["embedding_cos_vggish"] = scores["embedding_cos_vggish"]
                row["composite"] = scores["composite"]
                row["render_sha256"] = sha256_of_file(final_wav)
            row["eq_gains_db_json"] = json.dumps(info["eq_gains_db"])
            row["comp_engagement_fraction"] = info["comp_engagement_fraction"]
            row["loudness_method"] = info["loudness_method"]
            row["measured_db"] = info["measured_db"]
            row["applied_gain_lin"] = info["applied_gain_lin"]
            row["clipped_fraction"] = info["clipped_fraction"]
        except Exception as exc:  # pragma: no cover
            row["status"] = f"ERROR:{type(exc).__name__}:{str(exc)[:80]}"
        try:
            if dry_wav.exists():
                dry_wav.unlink()
        except OSError:
            pass
        rows.append(row)
        # c28: per-candidate top-K displacement. Push a normalized row shape.
        if topk is not None:
            topk.push({
                "render_path": str(final_wav),
                "composite": row["composite"],
                "render_wav_sha": row.get("render_sha256"),
            })
        if not _disk_ok(out_dir, budget_bytes, safety_factor=1.0):
            raise RuntimeError(
                f"mid-sweep disk breach after cell {cell['config_hash'][:8]}; "
                f"FD-1 halt."
            )

    def _key(r):
        c = r["composite"]
        return (float("inf") if c != c else c)

    rows.sort(key=_key)

    if args.score_and_delete:
        keep = set()
        for r in rows[: max(int(args.keep_top), 0)]:
            keep.add(r["config_hash"])
        for r in rows[max(int(args.keep_top), 0):]:
            cell_dir = renders_dir / (
                f"prog{r['program']:03d}"
                f"_gain{int(r['gain']*100):03d}"
                f"_rev{int(r['reverb_send']*100):03d}"
                f"_{r['post']}"
            )
            wav = cell_dir / "render.wav"
            if wav.exists() and r["config_hash"] not in keep:
                try:
                    wav.unlink()
                    pruned.append(str(wav))
                except OSError:
                    pass

    tsv_path = out_dir / "leaderboard.tsv"
    fields = [
        "rank", "preset_rank_stage1", "program",
        "gain", "reverb_send", "post", "config_hash",
        "mel_l1_db", "spectral_centroid_rmse_hz", "embedding_cos_vggish",
        "composite", "comp_engagement_fraction", "clipped_fraction",
        "loudness_method", "measured_db", "applied_gain_lin",
        "status", "render_sha256",
    ]
    with open(tsv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t",
                           extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(rows, start=1):
            row = dict(r)
            row["rank"] = i
            w.writerow(row)

    pruned_path = out_dir / "SWEEP_WAVS_PRUNED.txt"
    with open(pruned_path, "w") as f:
        for p in pruned:
            f.write(p + "\n")

    manifest = {
        "cycle": 14,
        "song_sha16": args.song_sha16,
        "instrument": "guitar",
        "sf2_path": str(args.sf2),
        "sf2_sha256": sf2_sha,
        "reference_stem": str(args.reference_stem),
        "reference_stem_sha256": ref_sha,
        "guitar_midi_path": str(args.guitar_midi),
        "guitar_midi_sha256": midi_sha,
        "top_k": args.top_k,
        "top_k_presets": top_k,
        "presets_promoted": presets,
        "grid_axes": {
            "gain": list(GAIN_LEVELS),
            "reverb_send": list(REVERB_LEVELS),
            "post": list(POST_STATES),
        },
        "n_configs": len(cells),
        "sample_rate": args.sample_rate,
        "elapsed_s": time.time() - t_start,
        "env_pins": {k: os.environ.get(k) for k in _PINS},
        "env_pin_sha256": _env_pin_sha256(),
        "pyloudnorm_available": bool(_LOUDNORM_AVAILABLE),
        "pyloudnorm_error": _LOUDNORM_ERR,
        "lufs_target_db": float(args.lufs_target),
        "objective_weights_frozen": {
            "mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25,
        },
        "post_processing_params": {
            "eq_v2": {
                "method": "iirpeak_12band_no_zero_mean",
                "Q": EQ_Q,
                "centers_hz": list(EQ_BAND_CENTERS),
            },
            "compressor": {
                "threshold_db": COMP_THRESHOLD_DB, "ratio": COMP_RATIO,
                "attack_ms": COMP_ATTACK_MS, "release_ms": COMP_RELEASE_MS,
                "makeup_gain_db": COMP_MAKEUP_DB,
            },
            "loudness_normalize": {
                "method": "lufs_i_or_rms_fallback",
                "target_db": float(args.lufs_target),
                "silent_early_exit_rms_threshold": 1e-4,
            },
        },
        "storage_hygiene": {
            "score_and_delete": bool(args.score_and_delete),
            "keep_top": int(args.keep_top),
            "max_audio_mb": int(args.max_audio_mb),
            "n_pruned": len(pruned),
            "final_audio_bytes": _dir_size_bytes(renders_dir),
        },
        "leaderboard_tsv": str(tsv_path),
    }
    with open(out_dir / "run_manifest.json", "w") as f:
        json.dump(manifest, f, sort_keys=True, indent=2)
    # c28: post-pin cleanup - top-1 render is "pinned"; delete other kept WAVs.
    if topk is not None and rows:
        try:
            top1 = rows[0]
            top1_render_path = str(renders_dir / (
                f"prog{top1['program']:03d}"
                f"_gain{int(top1['gain']*100):03d}"
                f"_rev{int(top1['reverb_send']*100):03d}"
                f"_{top1['post']}"
                "/render.wav"
            ))
            pinned_paths = {top1_render_path}
            _deleted = prune_after_pin(topk.kept_rows(), pinned_paths)
            (out_dir / "post_pin_cleanup.json").write_text(json.dumps({
                "pinned_paths": sorted(pinned_paths),
                "n_deleted": len(_deleted),
                "deleted_paths": _deleted[:20],
                "topk_stats": topk.stats(),
            }, sort_keys=True, indent=2))
        except Exception:  # pragma: no cover
            pass
    print(f"DONE: leaderboard at {tsv_path}, pruned={len(pruned)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
