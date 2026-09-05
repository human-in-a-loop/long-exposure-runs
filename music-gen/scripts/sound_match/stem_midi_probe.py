#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-05T00:00:00Z
# cycle: 23
# run_id: run-2026-09-05T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/non-cg-stem-midi-probe-c23
# ---
"""Per-stem MIDI probe: enumerate note_on events per track in merged.mid.

Discipline: env pins BEFORE any observed import; interpreter guard; no PRNG.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

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
    raise RuntimeError(f"stem_midi_probe requires /usr/bin/python3 (got {sys.executable})")

import mido  # noqa: E402


def sha16(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def probe_merged(merged_midi: Path, stems: list[str]) -> dict:
    m = mido.MidiFile(str(merged_midi))
    per_stem = {}
    for stem in stems:
        matched_tracks = []
        for idx, tr in enumerate(m.tracks):
            name = tr.name.strip().lower()
            if stem.lower() == name:
                note_on = sum(1 for msg in tr if msg.type == "note_on" and msg.velocity > 0)
                channels = sorted({msg.channel for msg in tr if hasattr(msg, "channel")})
                programs = sorted({msg.program for msg in tr if msg.type == "program_change"})
                matched_tracks.append({
                    "track_idx": idx,
                    "track_name": tr.name,
                    "n_note_on": note_on,
                    "channels": channels,
                    "gm_programs": programs,
                })
        n_note_on_total = sum(t["n_note_on"] for t in matched_tracks)
        per_stem[stem] = {
            "n_matching_tracks": len(matched_tracks),
            "matching_tracks": matched_tracks,
            "n_note_on_total": n_note_on_total,
            "is_empty": n_note_on_total == 0,
        }
    return per_stem


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Probe merged.mid per-stem note_on counts.")
    ap.add_argument("--song-sha16", required=True)
    ap.add_argument("--merged-midi", required=True, type=Path)
    ap.add_argument("--stems", default="bass,drums,guitar,piano,other,vocals")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    stems = [s.strip() for s in args.stems.split(",") if s.strip()]
    per_stem = probe_merged(args.merged_midi, stems)

    manifest = {
        "manifest_kind": "stem_midi_probe_c23",
        "milestone_id": "M-V4-PROFILES-1/non-cg-stem-midi-probe-c23",
        "cycle": 23,
        "created": "2026-09-05T00:00:00Z",
        "run_id": "run-2026-09-05T000000Z",
        "song_sha16": args.song_sha16,
        "merged_midi_path": str(args.merged_midi),
        "merged_midi_sha256_16": sha16(args.merged_midi),
        "stems_probed": stems,
        "per_stem": per_stem,
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    with open(args.out, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
