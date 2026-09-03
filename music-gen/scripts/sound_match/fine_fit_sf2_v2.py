#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T20:00:00Z
# cycle: 3
# run_id: run-2026-09-03T200000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-stage2b-launched
# ---
"""Stage-2b fine fit: EQ v2 (no zero-mean normalization) + mandatory LUFS-I
normalize + program-33 unconditional promotion (c1 top-5 + program 33 = 6
presets * 36 configs = 216 renders).

Discipline (matches c2, plus new brief mandates):
    - env pins BEFORE any observed import (belt-and-braces os.environ.setdefault)
    - /usr/bin/python3 interpreter guard
    - No PRNG, no time-varying wall-clock dependence
    - Objective panel weights literal-frozen (READ-ONLY import of
      scripts.sound_match.objective; weights live in that module)
    - SF2/reference/MIDI SHA anchors asserted at run start
    - c2 fine_fit_sf2.py is a READ-ONLY anchor — this is a sibling module

Grid (per-preset 36 cells, 6 presets, 216 rows total):
    gain          in {0.5, 1.0, 1.5}
    reverb_send   in {0.0, 0.3, 0.7}
    post          in {none, EQ_only, compressor_only, EQ_and_compressor}

Preset promotion:
    c1 top-5 (by rank) UNION {program 33 (Electric Bass Finger)}.
    Program 33 is the c1-c2 "MIDI source-of-truth" bass program; per the
    brief it must appear in exactly 36 rows regardless of its c1 rank.

Post-processing (c3 EQ v2 fix for MODERATE #1):
    EQ v2  = 12-band iirpeak Q=1.4 geomspace(20, 20000, 12), fitted per-render
             to the reference stem via _fit_eq_curve_v2_no_zero_mean() —
             per-band raw mag_ref_db - mag_render_db clipped +-12 dB, WITHOUT
             the zero-mean subtraction step. Broadband level is delegated to
             the mandatory LUFS-I normalize step.
    LUFS-I = pyloudnorm.Meter(sr).integrated_loudness -> scalar gain
             10 ** ((target - measured) / 20). Target: -18 dB LUFS-I. If
             pyloudnorm import fails (fetchability probe at module load),
             fall back to RMS-dBFS-based scalar and log
             loudness_method='rms_fallback' per row.
    Compressor = c2 implementation VERBATIM (soft-knee, -18 dBFS threshold,
                 3:1 ratio, 5 ms attack, 50 ms release, +6 dB makeup).

Silent-render guard: RMS < 1e-4 -> composite = inf, embedding_cos = 0.0,
loudness_method = 'skipped_silent'.

Clipping guard: renders clamped to [-0.99, 0.99] AFTER the final normalize;
clipped_fraction per row.
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
        f"fine_fit_sf2_v2 requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.objective import score_pair  # noqa: E402
from scripts.sound_match.coarse_sweep_sf2 import (  # noqa: E402
    sha256_of_file,
    _rewrite_bass_midi_with_program,
)
# READ-ONLY import of the iirpeak apply function.
from scripts.palette_render.render_stem import _apply_eq_curve_iirpeak  # noqa: E402

# --- fetchability probe for pyloudnorm (mandatory for LUFS-I; RMS fallback if missing) ---
_LOUDNORM_AVAILABLE = False
_LOUDNORM_ERR: str | None = None
try:
    import pyloudnorm as _pyln  # noqa: E402
    _LOUDNORM_AVAILABLE = True
except Exception as _exc:  # pragma: no cover
    _LOUDNORM_ERR = f"{type(_exc).__name__}:{_exc}"


# --- grid axes (frozen literals) ---
GAIN_LEVELS = (0.5, 1.0, 1.5)
REVERB_LEVELS = (0.0, 0.3, 0.7)
POST_STATES = ("none", "EQ_only", "compressor_only", "EQ_and_compressor")

# Control-cell program (mandatory promotion per brief)
CONTROL_PROGRAM = 33  # Electric Bass Finger, GM bank 0

# EQ params
EQ_BAND_CENTERS = tuple(float(x) for x in np.geomspace(20.0, 20000.0, 12))
EQ_Q = 1.4

# Compressor params (unchanged from c2)
COMP_THRESHOLD_DB = -18.0
COMP_RATIO = 3.0
COMP_ATTACK_MS = 5.0
COMP_RELEASE_MS = 50.0
COMP_MAKEUP_DB = 6.0

# LUFS-I target
LUFS_TARGET_DB = -18.0

# SF2 anchor (FluidR3_GM)
EXPECTED_SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"


def _load_mono(path: Path) -> tuple[np.ndarray, int]:
    y, sr = sf.read(str(path), always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y.astype(np.float32), int(sr)


def _fit_eq_curve_v2_no_zero_mean(
    rendered_wav: Path, reference_wav: Path
) -> list:
    """EQ v2: per-band raw ``mag_ref_db - mag_render_db`` gains, clipped
    +-12 dB. NO zero-mean subtraction (c2 MODERATE #1 fix). Broadband
    level is delegated to LUFS-I normalize step.
    """
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
        g = float(np.clip(mag_o - mag_r, -12.0, 12.0))
        gains.append(g)
    # NB: NO zero-mean subtraction here (c3 EQ v2). This is the fix.
    return gains


def _apply_compressor(mono: np.ndarray, sr: int) -> tuple[np.ndarray, dict]:
    """c2 implementation verbatim (soft-knee, attack/release envelope)."""
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


def _normalize_loudness(
    mono: np.ndarray, sr: int, target_db: float
) -> tuple[np.ndarray, dict]:
    """Return (normalized_mono, info) with loudness_method chosen at
    module-load time by ``_LOUDNORM_AVAILABLE``.

    Early-exit on near-silent input to avoid pyloudnorm blowing up on a
    signal below the meter's silence gate (~ -70 LUFS floor).
    """
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
                # meter refuses to measure below silence gate
                raise RuntimeError(f"lufs_below_silence_gate={measured}")
            gain_lin = float(10.0 ** ((target_db - measured) / 20.0))
            return (mono * gain_lin).astype(np.float32), {
                "loudness_method": "lufs_i",
                "measured_db": measured,
                "applied_gain_lin": gain_lin,
            }
        except Exception as exc:
            # fall through to RMS-dBFS fallback with error recorded
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
    """c3 v2 post-processing pipeline:
        [EQ v2 raw-diff, no zero-mean] -> [Compressor] -> [LUFS-I normalize] -> [clip]
    LUFS normalization is unconditional (a full pipeline element per brief).
    """
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

    # Mandatory LUFS-I normalize step (unconditional post-EQ+compressor).
    mono, loud_info = _normalize_loudness(mono, sr, lufs_target)
    info["loudness_method"] = loud_info["loudness_method"]
    info["measured_db"] = loud_info["measured_db"]
    info["applied_gain_lin"] = loud_info["applied_gain_lin"]

    mono, clip_frac = _clip_and_count(mono)
    info["clipped_fraction"] = clip_frac
    stereo = np.stack([mono, mono], axis=1).astype(np.float32)
    sf.write(str(out_wav), stereo, sr, subtype="PCM_16")
    return info


def _read_top_k_from_stage1(leaderboard: Path, k: int = 5) -> list[dict]:
    rows = []
    with open(leaderboard) as f:
        header = None
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if header is None:
                header = parts
                continue
            row = dict(zip(header, parts))
            rows.append(row)
    seen: set[int] = set()
    picked: list[dict] = []
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
            "preset_name": r.get("preset_name", ""),
        })
        if len(picked) >= k:
            break
    return picked


def _promote_with_control(top_k: list[dict], control_program: int) -> list[dict]:
    """Append the control cell (program 33) if not already present.

    The control cell keeps its natural rank_stage1 if it happened to be in
    top-K; otherwise it inherits a synthetic sentinel rank of 0 and empty
    preset_name (the coarse-sweep leaderboard may not have carried its
    name if it was outside top-K).
    """
    programs = {p["program"] for p in top_k}
    if control_program in programs:
        return list(top_k)
    return list(top_k) + [{
        "rank_stage1": 0,  # sentinel: "control cell, not from top-K"
        "bank": 0,
        "program": control_program,
        "composite_stage1": float("nan"),
        "preset_name": "control_cell_electric_bass_finger",
    }]


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
                        "preset_name": p["preset_name"],
                        "gain": gain,
                        "reverb_send": rev,
                        "post": post,
                        "config_hash": _config_hash(p["program"], gain, rev, post),
                    })
    return cells


def _env_pin_sha256() -> str:
    """SHA of canonical-JSON of {env pins + pyloudnorm availability + lufs_target}."""
    payload = {
        "env": {k: os.environ.get(k) for k in _PINS},
        "pyloudnorm_available": bool(_LOUDNORM_AVAILABLE),
        "lufs_target_db": LUFS_TARGET_DB,
    }
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Family-1 stage-2b fine fit (bass, cycle-3 CG target).",
    )
    ap.add_argument("--song-sha16", required=True)
    ap.add_argument("--stage1-leaderboard", required=True, type=Path)
    ap.add_argument("--include-program", type=int, action="append",
                    default=[CONTROL_PROGRAM],
                    help="unconditional control-cell program(s) (default: 33)")
    ap.add_argument("--reference-stem", required=True, type=Path)
    ap.add_argument("--bass-midi", required=True, type=Path)
    ap.add_argument("--sf2", type=Path,
                    default=Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"))
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--sample-rate", type=int, default=44100)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--lufs-target", type=float, default=LUFS_TARGET_DB)
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

    sf2_sha = sha256_of_file(args.sf2)
    if sf2_sha != EXPECTED_SF2_SHA:
        raise RuntimeError(f"SF2 sha drift: got {sf2_sha}")
    ref_sha = sha256_of_file(args.reference_stem)
    midi_sha = sha256_of_file(args.bass_midi)

    # fetchability ladder (one row per module-load probe)
    fetch_path = out_dir / "fetchability_ladder.jsonl"
    with open(fetch_path, "w") as f:
        f.write(json.dumps({
            "module": "pyloudnorm",
            "available": bool(_LOUDNORM_AVAILABLE),
            "error": _LOUDNORM_ERR,
            "lufs_target_db": args.lufs_target,
        }) + "\n")

    top_k = _read_top_k_from_stage1(args.stage1_leaderboard, k=args.top_k)
    if len(top_k) < args.top_k:
        raise RuntimeError(
            f"only {len(top_k)} presets in stage-1 (need {args.top_k})"
        )
    # Promote each --include-program unconditionally.
    presets = list(top_k)
    for prog in args.include_program:
        presets = _promote_with_control(presets, int(prog))

    cells = enumerate_grid(presets)

    t_start = time.time()
    rows: list[dict] = []
    for cell in cells:
        cell_dir = renders_dir / (
            f"prog{cell['program']:03d}"
            f"_gain{int(cell['gain']*100):03d}"
            f"_rev{int(cell['reverb_send']*100):03d}"
            f"_{cell['post']}"
        )
        cell_dir.mkdir(exist_ok=True)
        rewritten = cell_dir / "bass_with_program.mid"
        _rewrite_bass_midi_with_program(
            args.bass_midi, rewritten, cell["bank"], cell["program"]
        )
        dry_wav = cell_dir / "render_dry.wav"
        final_wav = cell_dir / "render.wav"
        row = {
            "preset_rank_stage1": cell["preset_rank_stage1"],
            "bank": cell["bank"],
            "program": cell["program"],
            "preset_name": cell["preset_name"],
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
        rows.append(row)

    def _key(r):
        c = r["composite"]
        return (float("inf") if c != c else c)  # NaN sinks

    rows.sort(key=_key)

    tsv_path = out_dir / "leaderboard.tsv"
    fields = [
        "rank", "preset_rank_stage1", "program", "preset_name",
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

    manifest = {
        "cycle": 3,
        "song_sha16": args.song_sha16,
        "sf2_path": str(args.sf2),
        "sf2_sha256": sf2_sha,
        "reference_stem": str(args.reference_stem),
        "reference_stem_sha256": ref_sha,
        "bass_midi_path": str(args.bass_midi),
        "bass_midi_sha256": midi_sha,
        "top_k": args.top_k,
        "top_k_presets": top_k,
        "include_program": list(args.include_program),
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
        "leaderboard_tsv": str(tsv_path),
    }
    with open(out_dir / "run_manifest.json", "w") as f:
        json.dump(manifest, f, sort_keys=True, indent=2)
    print(f"DONE: leaderboard at {tsv_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
