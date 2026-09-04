#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T00:00:00Z
# cycle: 13
# run_id: run-2026-09-04T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-guitar-sweep-launched
# ---
"""Family-1 coarse sweep — GUITAR variant.

Sibling to `coarse_sweep_sf2.py` (c1 anchor, READ-ONLY) and
`coarse_sweep_sf2_drums.py` (c10 anchor, READ-ONLY). Same discipline:
env pins BEFORE any observed import, no PRNG, panel objective READ-ONLY,
leaderboard TSV ranked by composite. FD-1: no tuning, no retry, no fallback.

Key differences from bass sweep:
    - Extracts 'guitar' track from merged.mid (channel 1 in v3 output).
    - Remaps guitar note events to channel 0 so the existing bank+PC
      insertion logic can be reused without change.
    - GM guitar program set (24..31: acoustic-nylon, acoustic-steel,
      electric-jazz, electric-clean, electric-muted, overdriven, distortion,
      harmonics).
    - Sweep-storage hygiene: --score-and-delete removes each render WAV
      immediately after scoring; only the top-K by composite are retained.
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
        f"coarse_sweep_sf2_guitar requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import mido  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.objective import score_pair  # noqa: E402

DEFAULT_GUITAR_PROGRAMS = [24, 25, 26, 27, 28, 29, 30, 31]
EXPECTED_SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_guitar_midi(merged_midi: Path, out_midi: Path) -> int:
    """Extract 'guitar' track from merged.mid, remap all notes to channel 0.

    Returns note_on count.
    """
    m = mido.MidiFile(str(merged_midi))
    guitar_track = None
    for t in m.tracks:
        if getattr(t, "name", "") and t.name.lower() == "guitar":
            guitar_track = t
            break
    if guitar_track is None:
        raise ValueError("no 'guitar' track in merged.mid")

    out = mido.MidiFile(ticks_per_beat=m.ticks_per_beat)
    meta = mido.MidiTrack()
    for msg in m.tracks[0]:
        if msg.is_meta and msg.type in ("set_tempo", "time_signature"):
            meta.append(msg.copy())
    out.tracks.append(meta)

    gt = mido.MidiTrack()
    n_notes = 0
    for msg in guitar_track:
        if msg.is_meta:
            gt.append(msg.copy())
            continue
        if hasattr(msg, "channel"):
            gt.append(msg.copy(channel=0))
        else:
            gt.append(msg.copy())
        if msg.type == "note_on" and msg.velocity > 0:
            n_notes += 1
    out.tracks.append(gt)
    out_midi.parent.mkdir(parents=True, exist_ok=True)
    out.save(str(out_midi))
    return n_notes


def _rewrite_with_program(src: Path, dst: Path, bank: int, program: int) -> None:
    """Insert bank+program change on channel 0 into the track carrying note_on ch0."""
    m = mido.MidiFile(str(src))

    def track_has_ch0_notes(track):
        return any(
            msg.type == "note_on" and getattr(msg, "channel", None) == 0
            for msg in track
        )

    target = None
    for i, t in enumerate(m.tracks):
        if track_has_ch0_notes(t):
            target = i
            break
    if target is None:
        raise ValueError("no track carries note_on events on channel 0")

    t = m.tracks[target]
    kept = []
    for msg in t:
        if msg.type == "program_change" and msg.channel == 0:
            continue
        if msg.type == "control_change" and msg.channel == 0 and msg.control in (0, 32):
            continue
        kept.append(msg)
    t.clear()
    t.append(mido.Message("control_change", channel=0, control=0, value=bank, time=0))
    t.append(mido.Message("control_change", channel=0, control=32, value=0, time=0))
    t.append(mido.Message("program_change", channel=0, program=program, time=0))
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


def _disk_ok(path: Path, budget_bytes: int, safety_factor: float = 2.0) -> bool:
    if budget_bytes <= 0:
        return True
    st = os.statvfs(str(path))
    avail_bytes = st.f_bavail * st.f_frsize
    return avail_bytes >= budget_bytes * safety_factor


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Family-1 coarse SF2 preset sweep (guitar).")
    ap.add_argument("--song", required=True)
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--reference-stem", required=True, type=Path)
    ap.add_argument("--midi-source", type=Path, default=None,
                    help="MIDI file to extract guitar track from (e.g. merged.mid).")
    ap.add_argument("--midi-excerpt", type=Path, default=None)
    ap.add_argument("--sf2", required=True, type=Path)
    ap.add_argument("--programs", default=",".join(str(p) for p in DEFAULT_GUITAR_PROGRAMS))
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--sample-rate", type=int, default=44100)
    ap.add_argument("--score-and-delete", action="store_true")
    ap.add_argument("--keep-top", type=int, default=3)
    ap.add_argument("--max-audio-mb", type=int, default=500)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    renders_dir = out_dir / "renders"
    renders_dir.mkdir(exist_ok=True)
    prune_log = out_dir / "SWEEP_WAVS_PRUNED.txt"
    prune_log.touch()

    for k, v in _PINS.items():
        got = os.environ.get(k)
        if got != v:
            raise RuntimeError(f"env pin drift {k}={got!r} expected {v!r}")

    budget_bytes = int(args.max_audio_mb) * 1024 * 1024
    if not args.dry_run and not _disk_ok(out_dir, budget_bytes, safety_factor=2.0):
        st = os.statvfs(str(out_dir))
        avail_gb = st.f_bavail * st.f_frsize / (1024 ** 3)
        raise RuntimeError(
            f"insufficient disk for sweep: need {2 * args.max_audio_mb} MB, "
            f"have {avail_gb:.2f} GB available"
        )

    if args.midi_excerpt is not None:
        guitar_midi = args.midi_excerpt
    else:
        if args.midi_source is None:
            raise SystemExit("need --midi-excerpt or --midi-source")
        guitar_midi = out_dir / "guitar_excerpt.mid"
        _extract_guitar_midi(args.midi_source, guitar_midi)

    gm = mido.MidiFile(str(guitar_midi))
    n_note_on = sum(
        1 for tr in gm.tracks for msg in tr if msg.type == "note_on" and msg.velocity > 0
    )
    if n_note_on == 0:
        (out_dir / "leaderboard.tsv").write_text(
            "rank\tbank\tprogram\tcomposite\tstatus\n1\t-\t-\tNaN\tNULL_MIDI_EMPTY\n"
        )
        (out_dir / "run_manifest.json").write_text(json.dumps(
            {"aborted": True, "reason": "NULL_MIDI_EMPTY", "guitar_midi": str(guitar_midi)},
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
    guitar_midi_sha = sha256_of_file(guitar_midi)

    if args.dry_run:
        (out_dir / "run_manifest.json").write_text(json.dumps(
            {"dry_run": True, "n_programs": len(programs), "n_note_on": n_note_on,
             "sf2_sha256": sf2_sha, "ref_stem_sha256": ref_stem_sha,
             "guitar_midi_sha256": guitar_midi_sha,
             "env_pins": {k: os.environ.get(k) for k in _PINS}},
            sort_keys=True, indent=2,
        ))
        print(f"DRY-RUN OK n_notes={n_note_on} n_programs={len(programs)}")
        return 0

    rows = []
    t_start = time.time()
    for program in programs:
        bank = 0
        cell = renders_dir / f"bank{bank}_prog{program:03d}"
        cell.mkdir(exist_ok=True)
        rewritten_midi = cell / "guitar_with_program.mid"
        _rewrite_with_program(guitar_midi, rewritten_midi, bank, program)
        out_wav = cell / "render.wav"
        try:
            _fluidsynth_render(args.sf2, rewritten_midi, out_wav, sr=args.sample_rate)
            render_sha = sha256_of_file(out_wav)
            scores = score_pair(out_wav, args.reference_stem)
            status = "OK"
        except Exception as exc:
            render_sha = None
            scores = {"mel_l1_db": float("nan"),
                      "spectral_centroid_rmse_hz": float("nan"),
                      "embedding_cos_vggish": None,
                      "embedding_cos_clap_or_none": None,
                      "embedding_component": None,
                      "composite": float("nan"),
                      "weights": {}, "embedding_rung": "error",
                      "sr_hz": 0, "n_samples_compared": 0}
            status = f"ERROR:{type(exc).__name__}:{str(exc)[:80]}"
        rows.append({"bank": bank, "program": program, "render_wav_sha": render_sha,
                     "render_path": str(out_wav), "status": status, **scores})

    def _key(r):
        c = r["composite"]
        return (float("inf") if c != c else c)
    rows.sort(key=_key)

    # Score-and-delete: prune renders beyond keep-top
    if args.score_and_delete:
        keep_shas = {r["render_wav_sha"] for r in rows[:max(0, args.keep_top)]}
        pruned = []
        for r in rows:
            p = Path(r["render_path"])
            if p.exists() and r["render_wav_sha"] not in keep_shas:
                p.unlink()
                pruned.append(str(p))
        with open(prune_log, "a") as f:
            for p in pruned:
                f.write(p + "\n")

    tsv_path = out_dir / "leaderboard.tsv"
    with open(tsv_path, "w") as f:
        f.write("rank\tbank\tprogram\tcomposite\tmel_l1_db\t"
                "spectral_centroid_rmse_hz\tembedding_cos_vggish\t"
                "embedding_cos_clap_or_none\tembedding_rung\tstatus\trender_sha\n")
        for i, r in enumerate(rows, start=1):
            f.write(f"{i}\t{r['bank']}\t{r['program']}\t{r['composite']:.6g}\t"
                    f"{r['mel_l1_db']:.6g}\t{r['spectral_centroid_rmse_hz']:.6g}\t"
                    f"{r['embedding_cos_vggish']}\t{r['embedding_cos_clap_or_none']}\t"
                    f"{r['embedding_rung']}\t{r['status']}\t{r['render_wav_sha']}\n")

    manifest = {
        "song_sha16": args.song,
        "instrument": args.instrument,
        "sf2_path": str(args.sf2),
        "sf2_sha256": sf2_sha,
        "reference_stem": str(args.reference_stem),
        "reference_stem_sha256": ref_stem_sha,
        "midi_excerpt_path": str(guitar_midi),
        "midi_excerpt_sha256": guitar_midi_sha,
        "n_programs": len(programs),
        "n_note_on": n_note_on,
        "sample_rate": args.sample_rate,
        "elapsed_s": time.time() - t_start,
        "env_pins": {k: os.environ.get(k) for k in _PINS},
        "objective_weights_frozen": {
            "mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25,
        },
        "leaderboard_tsv": str(tsv_path),
    }
    with open(out_dir / "run_manifest.json", "w") as f:
        json.dump(manifest, f, sort_keys=True, indent=2)
    print(f"DONE: leaderboard at {tsv_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
