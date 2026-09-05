#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES/cg-bass-sweep-launched
# ---
"""Family-1 coarse sweep: render a fixed MIDI excerpt through each candidate
SF2 preset and score against the operator-section stem.

Discipline:
    - env pins (BLAS single-thread + PYTHONHASHSEED + SOURCE_DATE_EPOCH
      + TZ=UTC + LC_ALL=C.UTF-8) MUST be set BEFORE any observed import.
      The wrapping launch script sets them; this module ALSO enforces
      via os.environ.setdefault as a belt-and-braces.
    - No PRNG in production code paths.
    - Panel objective is READ-ONLY over scripts.texture.panel.
    - Emits a leaderboard TSV ranked by composite; honest NULL_STEM_TOO_QUIET
      sentinel row if reference stem is quieter than -40 LUFS-I proxy.
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
for k, v in _PINS.items():
    os.environ.setdefault(k, v)

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"coarse_sweep_sf2 requires /usr/bin/python3 (got {sys.executable})"
    )

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import mido  # noqa: E402

# repo-root scripts.* imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.sound_match.objective import score_pair  # noqa: E402
# c28: canonical sweep-hygiene helpers per POR 2026-09-05 (adoption of c27 module).
from scripts.sound_match._sweep_hygiene_c27 import (  # noqa: E402
    RunningTopK, df_guard_before_stage, prune_after_pin,
    DEFAULT_KEEP_TOP, DEFAULT_MAX_AUDIO_MB,
)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_presets(spec: str) -> list[tuple[int, int]]:
    """Parse `bank0:programs=32,33,...` into a list of (bank, program) tuples."""
    out = []
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        head, _, tail = chunk.partition(":")
        if not head.startswith("bank"):
            raise ValueError(f"bad preset spec: {chunk!r}")
        bank = int(head[4:])
        for kv in tail.split(","):
            kv = kv.strip()
            if kv.startswith("programs="):
                progs = kv[len("programs="):]
                for p in progs.split(","):
                    out.append((bank, int(p)))
            else:
                out.append((bank, int(kv)))
    return out


def _rewrite_bass_midi_with_program(
    src_midi: Path, dst_midi: Path, bank: int, program: int
) -> None:
    """Copy src_midi, rewriting/inserting bank+program change on channel 0.

    The bank-select + program-change must land in the track that actually
    carries the note events for channel 0; inserting into a meta-only
    track leaves fluidsynth on the default program 0 (piano) at playback
    start.
    """
    m = mido.MidiFile(str(src_midi))
    if len(m.tracks) == 0:
        raise ValueError("empty MIDI")

    def track_has_notes_on_channel(track, chan):
        return any(
            msg.type == "note_on" and getattr(msg, "channel", None) == chan
            for msg in track
        )

    target_idx = None
    for i, t in enumerate(m.tracks):
        if track_has_notes_on_channel(t, 0):
            target_idx = i
            break
    if target_idx is None:
        raise ValueError("no track carries note_on events on channel 0")

    t = m.tracks[target_idx]
    # Strip any existing bank-select / program-change on channel 0 in this
    # track so ours is authoritative.
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

    dst_midi.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(dst_midi))


def _fluidsynth_render(
    sf2: Path, midi: Path, out_wav: Path, sr: int = 44100, gain: float = 0.8
) -> None:
    cmd = [
        "fluidsynth",
        "-ni",
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
    """A cheap LUFS-I proxy (peak-normalized RMS in dBFS)."""
    y, _ = sf.read(str(wav_path), always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    rms = float(np.sqrt(np.mean(y.astype(np.float64) ** 2) + 1e-12))
    return 20.0 * float(np.log10(max(rms, 1e-9)))


def _extract_bass_midi(merged_midi: Path, out_midi: Path) -> None:
    """Extract track named 'bass' from merged.mid as a stand-alone MIDI on ch0."""
    m = mido.MidiFile(str(merged_midi))
    bass_track = None
    for t in m.tracks:
        if t.name == "bass":
            bass_track = t
            break
    if bass_track is None:
        raise ValueError("no 'bass' track found in merged.mid")
    out = mido.MidiFile(ticks_per_beat=m.ticks_per_beat)
    # Keep tempo from track 0 if present.
    meta = mido.MidiTrack()
    for msg in m.tracks[0]:
        if msg.is_meta and msg.type in ("set_tempo", "time_signature"):
            meta.append(msg.copy())
    out.tracks.append(meta)
    # Remap bass_track messages to channel 0 (already channel 0).
    bt = mido.MidiTrack()
    for msg in bass_track:
        bt.append(msg.copy())
    out.tracks.append(bt)
    out_midi.parent.mkdir(parents=True, exist_ok=True)
    out.save(str(out_midi))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Family-1 coarse SF2 preset sweep (bass, cycle-1 CG target).",
    )
    ap.add_argument("--song", required=True, help="song sha16")
    ap.add_argument("--instrument", required=True, help="e.g. bass")
    ap.add_argument("--reference-stem", required=True, type=Path)
    ap.add_argument(
        "--midi-source", type=Path, default=None,
        help="MIDI file to extract bass track from (e.g. merged.mid).",
    )
    ap.add_argument(
        "--midi-excerpt", type=Path, default=None,
        help="Pre-built bass-only MIDI; if set, skips extraction.",
    )
    ap.add_argument("--sf2", required=True, type=Path)
    ap.add_argument("--presets", required=True, help="bank0:programs=32,33,...")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--sample-rate", type=int, default=44100)
    # c28 hygiene flags (default: per-candidate render->score->delete).
    ap.add_argument("--score-and-delete-per-candidate", action="store_true",
                    default=True,
                    help="c27 default: render->score->delete each candidate; "
                         "retain running top-K only.")
    ap.add_argument("--legacy-batch-render", action="store_true", default=False,
                    help="c26 legacy: batch-render then prune. Regression only; "
                         "forbidden in production per operator directive 2026-09-05.")
    ap.add_argument("--keep-top-c27", type=int, default=DEFAULT_KEEP_TOP)
    args = ap.parse_args(argv)

    out_dir: Path = args.out
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

    # Pre-launch sanity: verify env pins hold their target values.
    for k, v in _PINS.items():
        got = os.environ.get(k)
        if got != v:
            raise RuntimeError(f"env pin drift {k}={got!r} expected {v!r}")

    # Resolve bass MIDI.
    if args.midi_excerpt is not None:
        bass_midi = args.midi_excerpt
    else:
        if args.midi_source is None:
            raise SystemExit("need --midi-excerpt or --midi-source")
        bass_midi = out_dir / "bass_excerpt.mid"
        _extract_bass_midi(args.midi_source, bass_midi)

    # Note-count probe (Rung-1 sanity, special-point (i) from the brief).
    bm = mido.MidiFile(str(bass_midi))
    n_bass_notes = sum(
        1 for tr in bm.tracks
        for msg in tr if msg.type == "note_on" and msg.velocity > 0
    )
    if n_bass_notes == 0:
        with open(out_dir / "leaderboard.tsv", "w") as f:
            f.write(
                "rank\tbank\tprogram\tcomposite\tstatus\n"
                "1\t-\t-\tNaN\tNULL_MIDI_EMPTY\n"
            )
        with open(out_dir / "run_manifest.json", "w") as f:
            json.dump(
                {"aborted": True, "reason": "NULL_MIDI_EMPTY", "bass_midi": str(bass_midi)},
                f, sort_keys=True, indent=2,
            )
        return 2

    # LUFS-I proxy on reference stem (Rung-1 sanity, special-point (v)).
    ref_lufs = _lufs_i_proxy_db(args.reference_stem)
    if ref_lufs < -40.0:
        with open(out_dir / "leaderboard.tsv", "w") as f:
            f.write(
                "rank\tbank\tprogram\tcomposite\tstatus\n"
                "1\t-\t-\tNaN\tNULL_STEM_TOO_QUIET\n"
            )
        with open(out_dir / "run_manifest.json", "w") as f:
            json.dump(
                {
                    "aborted": True, "reason": "NULL_STEM_TOO_QUIET",
                    "reference_stem": str(args.reference_stem),
                    "ref_lufs_proxy_dbfs": ref_lufs,
                },
                f, sort_keys=True, indent=2,
            )
        return 3

    # SF2 SHA anchor check (special-point (iii)).
    sf2_sha = sha256_of_file(args.sf2)
    expected_sf2_sha = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
    if sf2_sha != expected_sf2_sha:
        raise RuntimeError(
            f"SF2 sha drift: got {sf2_sha}, expected {expected_sf2_sha}"
        )

    presets = _parse_presets(args.presets)
    if not presets:
        raise SystemExit("no presets parsed from --presets")

    ref_stem_sha = sha256_of_file(args.reference_stem)
    bass_midi_sha = sha256_of_file(bass_midi)

    rows = []
    t_start = time.time()
    for (bank, program) in presets:
        cell = renders_dir / f"bank{bank}_prog{program:03d}"
        cell.mkdir(exist_ok=True)
        rewritten_midi = cell / "bass_with_program.mid"
        _rewrite_bass_midi_with_program(bass_midi, rewritten_midi, bank, program)
        out_wav = cell / "render.wav"
        try:
            _fluidsynth_render(args.sf2, rewritten_midi, out_wav, sr=args.sample_rate)
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
            "bank": bank,
            "program": program,
            "render_wav_sha": render_sha,
            "render_path": str(out_wav),
            "status": status,
            **scores,
        }
        rows.append(row)
        # c28: per-candidate top-K displacement (deletes evicted/rejected WAVs).
        if topk is not None:
            topk.push(row)

    # Rank by composite ascending (lower = better). NaN sinks to bottom.
    def _key(r):
        c = r["composite"]
        return (float("inf") if c != c else c)  # NaN != NaN

    rows.sort(key=_key)

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
        "midi_excerpt_path": str(bass_midi),
        "midi_excerpt_sha256": bass_midi_sha,
        "n_presets": len(presets),
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
    # c28: post-pin cleanup - top-1 render is "pinned"; delete other kept WAVs.
    if topk is not None and rows:
        try:
            top1_render_path = rows[0].get("render_path", "")
            pinned_paths = {top1_render_path} if top1_render_path else set()
            _deleted = prune_after_pin(topk.kept_rows(), pinned_paths)
            (out_dir / "post_pin_cleanup.json").write_text(json.dumps({
                "pinned_paths": sorted(pinned_paths),
                "n_deleted": len(_deleted),
                "deleted_paths": _deleted[:20],
                "topk_stats": topk.stats(),
            }, sort_keys=True, indent=2))
        except Exception:  # pragma: no cover
            pass
    print(f"DONE: leaderboard at {tsv_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
