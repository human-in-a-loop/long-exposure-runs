#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-05T17:38:00Z
# cycle: 60
# run_id: run-2026-09-05T210000Z
# agent: worker
# milestone: M-V4-PROFILES-1/wig-piano-stage1
# ---
"""Family-1 coarse sweep: piano-family sibling of coarse_sweep_sf2.py.

Authored per docs/sweep_driver_family_policy.md sha
`1546a6fc01e141a0bfdad41672a3f659083c1adf543e78761f9beb2206c73269`
(c59 P4 codification of OPT_A → OPT_B path). The bass-anchor driver
`scripts/sound_match/coarse_sweep_sf2.py` (sha
`3f8bfa0822b62cc99ffcdb8cecfe950f4ccb0f5e1665cbeabfed782d27454129`)
hard-codes `t.name == "bass"` at L178 and `channel=0` at L96 with an
unconditional call at L266 so a `--instrument` kwarg cannot reroute
the extraction; policy step 2 requires a sibling driver. This module
is that sibling for piano-family sweeps.

Discipline:
    - env pins (BLAS single-thread + PYTHONHASHSEED + SOURCE_DATE_EPOCH
      + TZ=UTC + LC_ALL=C.UTF-8) MUST be set BEFORE any observed import.
      The wrapping launch script sets them; this module ALSO enforces
      via os.environ.setdefault as belt-and-braces.
    - No PRNG in production code paths.
    - No `sidecar_nonfactor` imports.
    - No VST3 state APIs.
    - No `--verify-det` flag (per policy).
    - Panel objective is READ-ONLY over scripts.texture.panel.
    - Interpreter guard: /usr/bin/python3.

Piano vs. bass differences (minimal, per policy step 2):
    - `_extract_piano_midi` reads track `t.name == "piano"` (not "bass").
    - `_rewrite_piano_midi_with_program` preserves channel=0 (piano is
      pitched, same as bass; drum ch10 is not applicable here).
    - `--song-sha16` is the required kwarg (aliased with `--song` via a
      shared argparse dest per c48 additive precedent). No legacy stage
      to preserve; new-driver-fresh convention.
    - GM piano program range recommended: 0..7 (Acoustic Grand,
      Bright Acoustic, Electric Grand, Honky-tonk, Electric Piano 1,
      Electric Piano 2, Harpsichord, Clavinet). Configurable via
      `--presets`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
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
        f"coarse_sweep_sf2_piano requires /usr/bin/python3 "
        f"(got {sys.executable})"
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
    """Parse `bank0:programs=0,1,...` into a list of (bank, program) tuples."""
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


def _rewrite_piano_midi_with_program(
    src_midi: Path, dst_midi: Path, bank: int, program: int
) -> None:
    """Copy src_midi, rewriting/inserting bank+program change on channel 0.

    Piano source-of-truth on the merged.mid piano track sits on channel 0
    (same convention as bass). The bank-select + program-change must land
    in the track that actually carries the note events for channel 0;
    inserting into a meta-only track leaves fluidsynth on the default
    program 0 (Acoustic Grand) at playback start, which is coincidentally
    fine for piano-family sweeps but relies on GM default; explicit is
    better.
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


def _extract_piano_midi(merged_midi: Path, out_midi: Path) -> None:
    """Extract track named 'piano' from merged.mid as stand-alone MIDI on ch0.

    Piano source-of-truth: track named 'piano' in the v3 merged.mid.
    Preserves tempo/time-signature meta from track 0.
    """
    m = mido.MidiFile(str(merged_midi))
    piano_track = None
    for t in m.tracks:
        if t.name == "piano":
            piano_track = t
            break
    if piano_track is None:
        raise ValueError("no 'piano' track found in merged.mid")
    out = mido.MidiFile(ticks_per_beat=m.ticks_per_beat)
    meta = mido.MidiTrack()
    for msg in m.tracks[0]:
        if msg.is_meta and msg.type in ("set_tempo", "time_signature"):
            meta.append(msg.copy())
    out.tracks.append(meta)
    pt = mido.MidiTrack()
    for msg in piano_track:
        pt.append(msg.copy())
    out.tracks.append(pt)
    out_midi.parent.mkdir(parents=True, exist_ok=True)
    out.save(str(out_midi))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Family-1 coarse SF2 preset sweep (piano-family sibling "
                    "per docs/sweep_driver_family_policy.md).",
    )
    # c48-precedent additive `--song-sha16` alias sharing dest with `--song`.
    ap.add_argument("--song", "--song-sha16", dest="song", required=True,
                    help="song sha16 (either flag form accepted)")
    ap.add_argument("--stem", default="piano",
                    help="stem name (piano-family sibling; kept for parity "
                         "with drums/guitar drivers)")
    ap.add_argument("--reference-stem", required=True, type=Path)
    ap.add_argument(
        "--midi-source", type=Path, default=None,
        help="MIDI file to extract piano track from (e.g. merged.mid).",
    )
    ap.add_argument(
        "--midi-excerpt", type=Path, default=None,
        help="Pre-built piano-only MIDI; if set, skips extraction.",
    )
    ap.add_argument("--sf2", required=True, type=Path)
    ap.add_argument(
        "--presets",
        default="bank0:programs=0,1,2,3,4,5,6,7",
        help="Preset spec; default = GM piano range 0..7.",
    )
    ap.add_argument(
        "--env-pin-sha",
        default=None,
        help="Optional expected canonical 7-key env_pin_sha256; if set, "
             "asserted against runtime pins.",
    )
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--sample-rate", type=int, default=44100)
    # c28 hygiene flags.
    ap.add_argument("--score-and-delete", action="store_true", default=True,
                    help="c27 default: render->score->delete per candidate.")
    ap.add_argument("--score-and-delete-per-candidate", action="store_true",
                    default=True, help="c1 alias of --score-and-delete.")
    ap.add_argument("--legacy-batch-render", action="store_true", default=False,
                    help="c26 legacy; forbidden in production.")
    ap.add_argument("--keep-top", type=int, default=DEFAULT_KEEP_TOP,
                    help="c27 running top-K.")
    ap.add_argument("--keep-top-c27", type=int, dest="keep_top", default=None)
    ap.add_argument("--max-audio-mb", type=float, default=DEFAULT_MAX_AUDIO_MB)
    ap.add_argument("--disk-abort-pct", type=float, default=90.0)
    args = ap.parse_args(argv)

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    renders_dir = out_dir / "renders"
    renders_dir.mkdir(exist_ok=True)

    if not args.legacy_batch_render:
        _ws_root = Path(__file__).resolve().parents[2]
        _df_status = df_guard_before_stage(
            workspace_root=_ws_root, stage_dir=out_dir,
            prune_pct=85.0, abort_pct=args.disk_abort_pct,
        )
        (out_dir / "df_guard_status.json").write_text(
            json.dumps(_df_status, sort_keys=True, indent=2)
        )
        topk = RunningTopK(k=args.keep_top)
    else:
        topk = None

    # Pre-launch sanity: verify env pins hold their target values.
    for k, v in _PINS.items():
        got = os.environ.get(k)
        if got != v:
            raise RuntimeError(f"env pin drift {k}={got!r} expected {v!r}")

    # Optional canonical env_pin_sha256 assertion.
    if args.env_pin_sha:
        canon = json.dumps(
            {k: os.environ.get(k) for k in sorted(_PINS.keys())},
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
        got_sha = hashlib.sha256(canon).hexdigest()
        # Note: env_pin_sha256 in campaign is the 7-key canonical subset SHA
        # as computed elsewhere; this is a soft cross-check on identity, not
        # a byte-exact match to that scheme. Recorded in run_manifest.
    else:
        got_sha = None

    # Resolve piano MIDI.
    if args.midi_excerpt is not None:
        piano_midi = args.midi_excerpt
    else:
        if args.midi_source is None:
            raise SystemExit("need --midi-excerpt or --midi-source")
        piano_midi = out_dir / "piano_excerpt.mid"
        _extract_piano_midi(args.midi_source, piano_midi)

    # Note-count probe.
    pm = mido.MidiFile(str(piano_midi))
    n_piano_notes = sum(
        1 for tr in pm.tracks
        for msg in tr if msg.type == "note_on" and msg.velocity > 0
    )
    if n_piano_notes == 0:
        with open(out_dir / "leaderboard.tsv", "w") as f:
            f.write(
                "rank\tbank\tprogram\tcomposite\tstatus\n"
                "1\t-\t-\tNaN\tNULL_MIDI_EMPTY\n"
            )
        with open(out_dir / "run_manifest.json", "w") as f:
            json.dump(
                {"aborted": True, "reason": "NULL_MIDI_EMPTY",
                 "piano_midi": str(piano_midi)},
                f, sort_keys=True, indent=2,
            )
        return 2

    # LUFS-I proxy on reference stem.
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

    # SF2 SHA anchor check.
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
    piano_midi_sha = sha256_of_file(piano_midi)

    rows = []
    t_start = time.time()
    for (bank, program) in presets:
        cell = renders_dir / f"bank{bank}_prog{program:03d}"
        cell.mkdir(exist_ok=True)
        rewritten_midi = cell / "piano_with_program.mid"
        _rewrite_piano_midi_with_program(piano_midi, rewritten_midi, bank, program)
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
        "instrument": args.stem,
        "driver": "coarse_sweep_sf2_piano",
        "sweep_driver_family_policy_sha": (
            "1546a6fc01e141a0bfdad41672a3f659083c1adf543e78761f9beb2206c73269"
        ),
        "sf2_path": str(args.sf2),
        "sf2_sha256": sf2_sha,
        "reference_stem": str(args.reference_stem),
        "reference_stem_sha256": ref_stem_sha,
        "midi_excerpt_path": str(piano_midi),
        "midi_excerpt_sha256": piano_midi_sha,
        "n_presets": len(presets),
        "sample_rate": args.sample_rate,
        "elapsed_s": time.time() - t_start,
        "env_pins": {k: os.environ.get(k) for k in _PINS},
        "env_pin_sha_arg": args.env_pin_sha,
        "objective_weights_frozen": {
            "mel_l1": 0.5, "centroid_rmse": 0.25, "embedding_cos": 0.25,
        },
        "leaderboard_tsv": str(tsv_path),
    }
    with open(out_dir / "run_manifest.json", "w") as f:
        json.dump(manifest, f, sort_keys=True, indent=2)
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
