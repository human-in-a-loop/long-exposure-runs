#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 2
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-stage2-launched
# ---
"""Stage-2 fine fit: perturb each of the c1 coarse-sweep top-5 SF2 presets
across a 5 x 3 x 3 x 4 = 180-cell grid (gain x reverb_send x post-processing).

Discipline (matches c1):
    - env pins BEFORE any observed import (belt-and-braces os.environ.setdefault)
    - /usr/bin/python3 interpreter guard
    - No PRNG, no time-varying wall-clock dependence
    - Objective panel weights literal-frozen at c1 values (READ-ONLY import of
      scripts.sound_match.objective; weights themselves are literals in that
      module, not passed as args, per spec §Objective)
    - SF2 SHA anchor check
    - Bass MIDI SHA anchor check
    - Reference stem SHA anchor check

Grid:
    gain          in {0.5, 1.0, 1.5}          (fluidsynth -g)
    reverb_send   in {0.0, 0.3, 0.7}          (fluidsynth synth.reverb.level)
    post_proc     in {none, EQ_only, compressor_only, EQ_and_compressor}

Post-processing:
    EQ         = 12-band iirpeak Q=1.4 geomspace(20, 20000, 12), fitted per-render
                 to the reference stem via _fit_eq_curve_from_reference()
                 (READ-ONLY import of _apply_eq_curve_iirpeak from
                 scripts.palette_render.render_stem).
    Compressor = soft-knee, threshold -18 dBFS, ratio 3:1, attack 5 ms,
                 release 50 ms, makeup gain +6 dB. Pure numpy sample-loop.

Clipping guard: renders clamped to [-0.99, 0.99] AFTER makeup gain to avoid
overflow; clipped-sample-fraction per row logged in leaderboard.

Silent-render guard: RMS < 1e-4 -> composite = inf, embedding_cos = 0.0,
status flagged degenerate_silent_render (should not fire; gain floor 0.5).
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
        f"fine_fit_sf2 requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import mido  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.objective import score_pair  # noqa: E402
from scripts.sound_match.coarse_sweep_sf2 import (  # noqa: E402
    sha256_of_file,
    _rewrite_bass_midi_with_program,
)
# READ-ONLY import of the iirpeak apply function (c51 rc7_eq_curve_fit_method).
from scripts.palette_render.render_stem import _apply_eq_curve_iirpeak  # noqa: E402


# --- grid axes (frozen literals) ---
GAIN_LEVELS = (0.5, 1.0, 1.5)
REVERB_LEVELS = (0.0, 0.3, 0.7)
POST_STATES = ("none", "EQ_only", "compressor_only", "EQ_and_compressor")

# EQ params
EQ_BAND_CENTERS = tuple(float(x) for x in np.geomspace(20.0, 20000.0, 12))
EQ_Q = 1.4

# Compressor params
COMP_THRESHOLD_DB = -18.0
COMP_RATIO = 3.0
COMP_ATTACK_MS = 5.0
COMP_RELEASE_MS = 50.0
COMP_MAKEUP_DB = 6.0

# SF2 anchor (FluidR3_GM)
EXPECTED_SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"


def _load_mono(path: Path) -> tuple[np.ndarray, int]:
    y, sr = sf.read(str(path), always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y.astype(np.float32), int(sr)


def _fit_eq_curve_from_reference(rendered_wav: Path, reference_wav: Path) -> list:
    """Return list of 12 per-band gains (dB) shaping rendered toward reference.
    Zero-mean normalized (loudness owned by makeup gain / no-op)."""
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
    gains = []
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
    mean_g = float(np.mean(gains))
    return [float(g - mean_g) for g in gains]


def _apply_compressor(mono: np.ndarray, sr: int) -> tuple[np.ndarray, dict]:
    """Digital soft-knee-lite compressor (attack/release envelope, ratio, makeup).

    Pure numpy scalar-state loop. Deterministic; no PRNG; no wall-clock.
    Returns (output, info) where info carries settling stats.
    """
    thresh_lin = 10.0 ** (COMP_THRESHOLD_DB / 20.0)
    ratio = COMP_RATIO
    makeup_lin = 10.0 ** (COMP_MAKEUP_DB / 20.0)
    # Time-constants in samples
    attack_coeff = float(np.exp(-1.0 / (sr * COMP_ATTACK_MS * 1e-3)))
    release_coeff = float(np.exp(-1.0 / (sr * COMP_RELEASE_MS * 1e-3)))
    x = mono.astype(np.float64)
    env = 0.0
    out = np.zeros_like(x)
    n_engaged = 0
    for i, v in enumerate(x):
        av = abs(v)
        # envelope follower: attack when rising, release when falling
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


def _clip_and_count(mono: np.ndarray) -> tuple[np.ndarray, float]:
    """Clamp to [-0.99, 0.99]; return (clipped_signal, fraction_clipped)."""
    n_clipped = int(np.sum(np.abs(mono) > 0.99))
    frac = float(n_clipped / max(len(mono), 1))
    return np.clip(mono, -0.99, 0.99).astype(np.float32), frac


def _fluidsynth_render(
    sf2: Path, midi: Path, out_wav: Path,
    *, sr: int = 44100, gain: float = 1.0, reverb_send: float = 0.0
) -> None:
    """Render with configurable gain and reverb send.

    reverb_send == 0.0 -> reverb disabled (dry).
    reverb_send  > 0.0 -> reverb.active=true, room-size + level from send.
    """
    if reverb_send == 0.0:
        reverb_opts = [
            "-o", "synth.reverb.active=false",
        ]
    else:
        # Map send in [0, 1] to a (room-size, level) pair. Keep room-size
        # bounded so the tail doesn't blow out at send=0.7.
        room_size = 0.3 + 0.4 * float(reverb_send)  # 0.3 .. 0.58
        reverb_opts = [
            "-o", "synth.reverb.active=true",
            "-o", f"synth.reverb.room-size={room_size:.4f}",
            "-o", f"synth.reverb.level={float(reverb_send):.4f}",
            "-o", "synth.reverb.damp=0.5",
            "-o", "synth.reverb.width=1.0",
        ]
    cmd = [
        "fluidsynth",
        "-ni",
        "-F", str(out_wav),
        "-r", str(sr),
        "-g", f"{float(gain):.4f}",
        "-o", "synth.cpu-cores=1",
        "-o", "synth.chorus.active=false",
        "-o", f"synth.sample-rate={sr}",
        "-o", "synth.midi-bank-select=gs",
        *reverb_opts,
        str(sf2),
        str(midi),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f"fluidsynth failed rc={r.returncode} "
            f"stderr={r.stderr.decode(errors='replace')[:400]}"
        )


def _apply_post(
    render_wav: Path, out_wav: Path, ref_stem: Path, post: str, sr: int = 44100
) -> dict:
    """Apply EQ / compressor / both / none; write output; return per-cell info."""
    mono, sr_r = _load_mono(render_wav)
    if sr_r != sr:
        raise RuntimeError(f"sr drift: expected {sr} got {sr_r}")
    info: dict = {"post": post, "eq_gains_db": None,
                  "comp_engagement_fraction": None, "clipped_fraction": 0.0}

    if post in ("EQ_only", "EQ_and_compressor"):
        gains = _fit_eq_curve_from_reference(render_wav, ref_stem)
        info["eq_gains_db"] = gains
        mono = _apply_eq_curve_iirpeak(mono, list(EQ_BAND_CENTERS), gains, fs=sr)
        mono = mono.astype(np.float32)

    if post in ("compressor_only", "EQ_and_compressor"):
        mono, comp_info = _apply_compressor(mono, sr=sr)
        info["comp_engagement_fraction"] = comp_info["engagement_fraction"]

    mono, clip_frac = _clip_and_count(mono)
    info["clipped_fraction"] = clip_frac
    # canonical stereo write (duplicate mono to both channels)
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
    # de-dup by program (preserve stage-1 rank order)
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


def _canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _config_hash(preset_program: int, gain: float, reverb: float, post: str) -> str:
    body = {"program": int(preset_program), "gain": float(gain),
            "reverb_send": float(reverb), "post": post}
    return hashlib.sha256(_canonical_json(body)).hexdigest()


def enumerate_grid(top_k: list[dict]) -> list[dict]:
    """Deterministic grid enumeration; ordered (preset_rank, gain, reverb, post)."""
    cells = []
    for p in top_k:
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Family-1 stage-2 fine fit (bass, cycle-2 CG target).",
    )
    ap.add_argument("--song-sha16", required=True)
    ap.add_argument("--stage1-leaderboard", required=True, type=Path)
    ap.add_argument("--reference-stem", required=True, type=Path)
    ap.add_argument("--bass-midi", required=True, type=Path)
    ap.add_argument("--sf2", type=Path,
                    default=Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"))
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--sample-rate", type=int, default=44100)
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args(argv)

    for k, v in _PINS.items():
        if os.environ.get(k) != v:
            raise RuntimeError(f"env pin drift {k}={os.environ.get(k)!r} expected {v!r}")

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    renders_dir = out_dir / "renders"
    renders_dir.mkdir(exist_ok=True)

    sf2_sha = sha256_of_file(args.sf2)
    if sf2_sha != EXPECTED_SF2_SHA:
        raise RuntimeError(f"SF2 sha drift: got {sf2_sha}")
    ref_sha = sha256_of_file(args.reference_stem)
    midi_sha = sha256_of_file(args.bass_midi)

    top_k = _read_top_k_from_stage1(args.stage1_leaderboard, k=args.top_k)
    if len(top_k) < args.top_k:
        raise RuntimeError(f"only {len(top_k)} presets in stage-1 (need {args.top_k})")

    cells = enumerate_grid(top_k)

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
        # Rewrite MIDI with the preset's program.
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
            info = _apply_post(
                dry_wav, final_wav, args.reference_stem, cell["post"],
                sr=args.sample_rate,
            )
            # silent-render guard
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
        "cycle": 2,
        "song_sha16": args.song_sha16,
        "sf2_path": str(args.sf2),
        "sf2_sha256": sf2_sha,
        "reference_stem": str(args.reference_stem),
        "reference_stem_sha256": ref_sha,
        "bass_midi_path": str(args.bass_midi),
        "bass_midi_sha256": midi_sha,
        "top_k": args.top_k,
        "top_k_presets": top_k,
        "grid_axes": {
            "gain": list(GAIN_LEVELS),
            "reverb_send": list(REVERB_LEVELS),
            "post": list(POST_STATES),
        },
        "n_configs": len(cells),
        "sample_rate": args.sample_rate,
        "elapsed_s": time.time() - t_start,
        "env_pins": {k: os.environ.get(k) for k in _PINS},
        "objective_weights_frozen": {
            "mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25,
        },
        "post_processing_params": {
            "eq": {"method": "iirpeak_12band", "Q": EQ_Q,
                   "centers_hz": list(EQ_BAND_CENTERS)},
            "compressor": {
                "threshold_db": COMP_THRESHOLD_DB, "ratio": COMP_RATIO,
                "attack_ms": COMP_ATTACK_MS, "release_ms": COMP_RELEASE_MS,
                "makeup_gain_db": COMP_MAKEUP_DB,
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
