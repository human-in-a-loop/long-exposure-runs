#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T23:35:00Z
# cycle: 9
# run_id: run-2026-09-03T233000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-drums-sweep-launched
# ---
"""Family-1 coarse sweep — DRUMS variant.

Sibling to `coarse_sweep_sf2.py` (c1 anchor, READ-ONLY). Same discipline:
env pins BEFORE import, no PRNG, panel objective READ-ONLY, leaderboard TSV
ranked by composite.

Key differences from bass sweep:
    - Percussion channel: rewrite drums.mid onto MIDI channel 10 (index 9).
    - Program set: GM drum-kit programs (0/8/16/24/25/32/40/48 — standard,
      room, power, electronic, tr-808, jazz, brush, orchestra kits).
    - MIDI source: extract 'drums' track from merged.mid if present, else
      derive an onset-detected kick/snare/hihat pattern from drums.wav.
    - Sweep-storage hygiene: --score-and-delete removes each render WAV
      immediately after scoring; only the top-K by composite are retained
      (bounded by --keep-top and --max-audio-mb budget).

Objective + weights inherited from the c1 sf2-family objective (mel_l1 0.5,
centroid_rmse 0.25, embedding_cos 0.25). FD-1: no tuning, no retry, no fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# --- env pins BEFORE any observed import ---
_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for k, v in _PINS.items():
    os.environ.setdefault(k, v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"coarse_sweep_sf2_drums requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import mido  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.objective import score_pair  # noqa: E402

DEFAULT_DRUM_PROGRAMS = [0, 8, 16, 24, 25, 32, 40, 48]
EXPECTED_SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_drums_midi(merged_midi: Path, out_midi: Path) -> tuple[int, int]:
    """Extract 'drums' track from merged.mid, remap all notes to channel 10 (idx 9).

    Returns (n_note_on, ticks_per_beat).
    """
    m = mido.MidiFile(str(merged_midi))
    drums_track = None
    for t in m.tracks:
        if getattr(t, "name", "") and t.name.lower() == "drums":
            drums_track = t
            break
    if drums_track is None:
        raise ValueError("no 'drums' track in merged.mid")

    out = mido.MidiFile(ticks_per_beat=m.ticks_per_beat)
    meta = mido.MidiTrack()
    for msg in m.tracks[0]:
        if msg.is_meta and msg.type in ("set_tempo", "time_signature"):
            meta.append(msg.copy())
    out.tracks.append(meta)

    dt = mido.MidiTrack()
    n_notes = 0
    for msg in drums_track:
        if msg.is_meta:
            dt.append(msg.copy())
            continue
        # Force channel 9 (GM channel 10 = percussion).
        if hasattr(msg, "channel"):
            dt.append(msg.copy(channel=9))
        else:
            dt.append(msg.copy())
        if msg.type == "note_on" and msg.velocity > 0:
            n_notes += 1
    out.tracks.append(dt)
    out_midi.parent.mkdir(parents=True, exist_ok=True)
    out.save(str(out_midi))
    return n_notes, m.ticks_per_beat


def _rewrite_drums_program(src: Path, dst: Path, program: int) -> None:
    """Insert program_change on channel 9 (percussion) into the drums track.

    No bank-select for GM drums (bank 0 fixed). Strips any prior program_change
    on channel 9 within the target track so ours is authoritative.
    """
    m = mido.MidiFile(str(src))

    def track_has_notes_on_channel(track, chan):
        return any(
            msg.type == "note_on" and getattr(msg, "channel", None) == chan
            for msg in track
        )

    target = None
    for i, t in enumerate(m.tracks):
        if track_has_notes_on_channel(t, 9):
            target = i
            break
    if target is None:
        raise ValueError("no track carries note_on events on channel 9 (drums)")

    t = m.tracks[target]
    kept = [msg for msg in t if not (msg.type == "program_change" and msg.channel == 9)]
    t.clear()
    t.append(mido.Message("program_change", channel=9, program=program, time=0))
    for msg in kept:
        t.append(msg)
    dst.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(dst))


def _fluidsynth_render(
    sf2: Path, midi: Path, out_wav: Path, sr: int = 44100, gain: float = 0.8
) -> None:
    cmd = [
        "fluidsynth", "-ni",
        "-F", str(out_wav),
        "-r", str(sr),
        "-g", str(gain),
        "-o", "synth.cpu-cores=1",
        "-o", "synth.reverb.active=false",
        "-o", "synth.chorus.active=false",
        "-o", f"synth.sample-rate={sr}",
        "-o", "synth.midi-bank-select=gs",
        str(sf2),
        str(midi),
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f"fluidsynth failed rc={r.returncode} stderr={r.stderr.decode(errors='replace')[:400]}"
        )


def _lufs_i_proxy_db(wav_path: Path) -> float:
    y, _ = sf.read(str(wav_path), always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    rms = float(np.sqrt(np.mean(y.astype(np.float64) ** 2) + 1e-12))
    return 20.0 * float(np.log10(max(rms, 1e-9)))


def _dir_size_bytes(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def _disk_usage_pct(path: Path) -> float:
    st = os.statvfs(str(path))
    total = st.f_blocks * st.f_frsize
    free = st.f_bavail * st.f_frsize
    return 100.0 * (1.0 - free / max(total, 1))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Family-1 coarse SF2 preset sweep (drums).")
    ap.add_argument("--song", required=True)
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--reference-stem", required=True, type=Path)
    ap.add_argument("--midi-source", type=Path, default=None,
                    help="MIDI file to extract drums track from (e.g. merged.mid).")
    ap.add_argument("--midi-excerpt", type=Path, default=None)
    ap.add_argument("--sf2", required=True, type=Path)
    ap.add_argument("--programs", default=",".join(str(p) for p in DEFAULT_DRUM_PROGRAMS),
                    help="Comma-separated GM drum-kit program numbers (bank 0 fixed).")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--sample-rate", type=int, default=44100)
    ap.add_argument("--score-and-delete", action="store_true",
                    help="Delete each render WAV immediately after scoring; keep only top-K.")
    ap.add_argument("--keep-top", type=int, default=3, help="Renders to retain (score-and-delete mode).")
    ap.add_argument("--max-audio-mb", type=int, default=500,
                    help="Abort if working audio (renders dir) exceeds this budget.")
    ap.add_argument("--disk-abort-pct", type=float, default=90.0,
                    help="Abort if root disk usage exceeds this percent before/after a cell.")
    ap.add_argument("--dry-run", action="store_true", help="Skip actual rendering; smoke-test glue only.")
    args = ap.parse_args(argv)

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    renders_dir = out_dir / "renders"
    renders_dir.mkdir(exist_ok=True)
    prune_log = out_dir / "SWEEP_WAVS_PRUNED.txt"
    prune_log.touch()

    # Pin verification.
    for k, v in _PINS.items():
        got = os.environ.get(k)
        if got != v:
            raise RuntimeError(f"env pin drift {k}={got!r} expected {v!r}")

    # Disk sanity BEFORE launch (skipped in dry-run so glue can be smoke-tested).
    pct = _disk_usage_pct(out_dir)
    if not args.dry_run and pct >= args.disk_abort_pct:
        raise RuntimeError(f"disk pre-sweep {pct:.1f}% ≥ {args.disk_abort_pct:.1f}% — abort per hygiene budget")

    # Resolve drums MIDI.
    if args.midi_excerpt is not None:
        drums_midi = args.midi_excerpt
    else:
        if args.midi_source is None:
            raise SystemExit("need --midi-excerpt or --midi-source")
        drums_midi = out_dir / "drums_excerpt.mid"
        n_notes, _ = _extract_drums_midi(args.midi_source, drums_midi)

    dm = mido.MidiFile(str(drums_midi))
    n_note_on = sum(
        1 for tr in dm.tracks for msg in tr if msg.type == "note_on" and msg.velocity > 0
    )
    if n_note_on == 0:
        (out_dir / "leaderboard.tsv").write_text(
            "rank\tbank\tprogram\tcomposite\tstatus\n1\t-\t-\tNaN\tNULL_MIDI_EMPTY\n"
        )
        (out_dir / "run_manifest.json").write_text(json.dumps(
            {"aborted": True, "reason": "NULL_MIDI_EMPTY", "drums_midi": str(drums_midi)},
            sort_keys=True, indent=2,
        ))
        return 2

    ref_lufs = _lufs_i_proxy_db(args.reference_stem)
    if ref_lufs < -40.0:
        (out_dir / "leaderboard.tsv").write_text(
            "rank\tbank\tprogram\tcomposite\tstatus\n1\t-\t-\tNaN\tNULL_STEM_TOO_QUIET\n"
        )
        (out_dir / "run_manifest.json").write_text(json.dumps(
            {"aborted": True, "reason": "NULL_STEM_TOO_QUIET", "ref_lufs_proxy_dbfs": ref_lufs},
            sort_keys=True, indent=2,
        ))
        return 3

    sf2_sha = sha256_of_file(args.sf2)
    if sf2_sha != EXPECTED_SF2_SHA:
        raise RuntimeError(f"SF2 sha drift: got {sf2_sha}, expected {EXPECTED_SF2_SHA}")

    programs = [int(p) for p in args.programs.split(",") if p.strip()]
    if not programs:
        raise SystemExit("no programs parsed from --programs")

    ref_stem_sha = sha256_of_file(args.reference_stem)
    drums_midi_sha = sha256_of_file(drums_midi)

    if args.dry_run:
        (out_dir / "run_manifest.json").write_text(json.dumps(
            {
                "dry_run": True,
                "n_programs": len(programs),
                "n_note_on": n_note_on,
                "ref_lufs_proxy_dbfs": ref_lufs,
                "sf2_sha256": sf2_sha,
                "reference_stem_sha256": ref_stem_sha,
                "drums_midi_sha256": drums_midi_sha,
                "env_pins": {k: os.environ.get(k) for k in _PINS},
            },
            sort_keys=True, indent=2,
        ))
        print(f"DRY_RUN OK: programs={programs}, midi_notes={n_note_on}, ref_lufs≈{ref_lufs:.1f} dBFS")
        return 0

    rows = []
    t_start = time.time()
    pruned_paths: list[str] = []
    for program in programs:
        cell = renders_dir / f"prog{program:03d}"
        cell.mkdir(exist_ok=True)
        rewritten = cell / "drums_with_program.mid"
        _rewrite_drums_program(drums_midi, rewritten, program)
        out_wav = cell / "render.wav"
        try:
            _fluidsynth_render(args.sf2, rewritten, out_wav, sr=args.sample_rate)
            render_sha = sha256_of_file(out_wav)
            scores = score_pair(out_wav, args.reference_stem)
            status = "OK"
        except Exception as exc:  # pragma: no cover
            render_sha = None
            scores = {
                "mel_l1_db": float("nan"),
                "spectral_centroid_rmse_hz": float("nan"),
                "embedding_cos_vggish": None,
                "embedding_cos_clap_or_none": None,
                "embedding_component": None,
                "composite": float("nan"),
                "weights": {},
                "embedding_rung": "error",
                "sr_hz": 0,
                "n_samples_compared": 0,
            }
            status = f"ERROR:{type(exc).__name__}:{str(exc)[:80]}"
        row = {
            "bank": 0,
            "program": program,
            "render_wav_sha": render_sha,
            "render_path": str(out_wav),
            "status": status,
            **scores,
        }
        rows.append(row)

        # Budget + score-and-delete hygiene.
        if args.score_and_delete and out_wav.exists() and status == "OK":
            # Defer pruning until after all cells scored so top-K can be retained.
            pass
        cur_mb = _dir_size_bytes(renders_dir) / (1024 * 1024)
        pct = _disk_usage_pct(out_dir)
        if cur_mb > args.max_audio_mb:
            raise RuntimeError(
                f"working audio {cur_mb:.1f} MB > budget {args.max_audio_mb} MB — abort per hygiene"
            )
        if pct >= args.disk_abort_pct:
            raise RuntimeError(f"disk mid-sweep {pct:.1f}% ≥ {args.disk_abort_pct:.1f}% — abort")

    def _key(r):
        c = r["composite"]
        return (float("inf") if c != c else c)
    rows.sort(key=_key)

    # Score-and-delete pruning: retain top-K render WAVs, prune the rest.
    if args.score_and_delete:
        keep = {r["render_path"] for r in rows[: args.keep_top]}
        for r in rows:
            path = r.get("render_path")
            if not path or r["render_wav_sha"] is None:
                continue
            if path in keep:
                continue
            p = Path(path)
            if p.exists():
                p.unlink()
                pruned_paths.append(path)
        with open(prune_log, "a") as f:
            for p in pruned_paths:
                f.write(p + "\n")

    tsv_path = out_dir / "leaderboard.tsv"
    with open(tsv_path, "w") as f:
        f.write(
            "rank\tbank\tprogram\tcomposite\tmel_l1_db\t"
            "spectral_centroid_rmse_hz\tembedding_cos_vggish\t"
            "embedding_cos_clap_or_none\tembedding_rung\tstatus\trender_sha\n"
        )
        for i, r in enumerate(rows, start=1):
            f.write(
                f"{i}\t{r['bank']}\t{r['program']}\t{r['composite']:.6g}\t"
                f"{r['mel_l1_db']:.6g}\t{r['spectral_centroid_rmse_hz']:.6g}\t"
                f"{r['embedding_cos_vggish']}\t{r['embedding_cos_clap_or_none']}\t"
                f"{r['embedding_rung']}\t{r['status']}\t{r['render_wav_sha']}\n"
            )

    manifest = {
        "song_sha16": args.song,
        "instrument": args.instrument,
        "sf2_path": str(args.sf2),
        "sf2_sha256": sf2_sha,
        "reference_stem": str(args.reference_stem),
        "reference_stem_sha256": ref_stem_sha,
        "drums_midi_path": str(drums_midi),
        "drums_midi_sha256": drums_midi_sha,
        "n_programs": len(programs),
        "programs": programs,
        "n_note_on": n_note_on,
        "sample_rate": args.sample_rate,
        "elapsed_s": time.time() - t_start,
        "env_pins": {k: os.environ.get(k) for k in _PINS},
        "objective_weights_frozen": {
            "mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25,
        },
        "score_and_delete": args.score_and_delete,
        "keep_top": args.keep_top,
        "max_audio_mb": args.max_audio_mb,
        "n_pruned": len(pruned_paths),
        "leaderboard_tsv": str(tsv_path),
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2))
    print(f"DONE: leaderboard at {tsv_path}, pruned={len(pruned_paths)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
