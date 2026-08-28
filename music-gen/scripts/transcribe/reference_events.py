"""
M-TRANS-1 ground-truth note-event recovery.

Decodes the loop/tile policy of `scripts/separation/synth_gt.py`:

- Each MIDI is a 4-bar phrase at 120 BPM (LOOP_S = 8.0 s).
- The rendered stem is: fluidsynth output truncated to the first
  LOOP_S seconds, then TILED in the audio domain enough times to
  cover duration_s, then trimmed to duration_s*SR samples.

Consequence at the note-event layer: the ground-truth note sequence
for a stem of duration D is the original MIDI's note list, replicated
at time offsets {0, LOOP_S, 2*LOOP_S, ...} for as many repetitions as
fit, with every note whose start >= D dropped and any note whose end
> D clipped to D.

Output per (duration, stem): a canonical newline-delimited JSONL of
records with fields
    {pitch, onset_s, offset_s, velocity, is_drum}
Sorted by (onset_s, pitch) so SHA-256 is deterministic.

Stems on disk are named drums.wav / bass.wav / other.wav / vocals.wav.
`other.wav` was rendered from `piano.mid` (see synth_gt.py line 166).
The mapping stem -> midi:
    drums  -> drums.mid   (is_drum=True; pitch = GM drum note)
    bass   -> bass.mid    (is_drum=False)
    other  -> piano.mid   (is_drum=False)
    vocals -> (no midi; zero WAV)  -- treated as no-notes reference.

Interpreter: /usr/bin/python3 (asserted).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pretty_midi

assert sys.executable == "/usr/bin/python3", f"interpreter guard: {sys.executable}"

ROOT = Path("/home/user/long-exposure-runs/music-gen")
MIDI_DIR = ROOT / "data/separation/synth_mix/midi"
OUT_ROOT = ROOT / "data/transcribe/reference"

LOOP_S = 8.0  # matches synth_gt.py BAR_S*BARS_PER_LOOP (0.5s * 4beats * 4bars = 8.0s)
DURATIONS = [30, 60, 90]

# Stem -> source MIDI mapping. 'vocals' has no MIDI (zero stem).
STEM_TO_MIDI = {
    "drums": "drums.mid",
    "bass": "bass.mid",
    "other": "piano.mid",
    # vocals intentionally absent.
}


def tile_notes(midi_path: Path, duration_s: float) -> list[dict]:
    """Return note events, tiled at LOOP_S offsets, clipped to duration_s."""
    pm = pretty_midi.PrettyMIDI(str(midi_path))
    base_notes: list[tuple[int, float, float, int, bool]] = []
    for inst in pm.instruments:
        for n in inst.notes:
            base_notes.append((n.pitch, float(n.start), float(n.end),
                               int(n.velocity), bool(inst.is_drum)))
    if not base_notes:
        return []
    # Tile by loop.
    n_reps = int((duration_s + LOOP_S - 1e-9) // LOOP_S) + 1
    tiled: list[dict] = []
    for k in range(n_reps):
        offset = k * LOOP_S
        for (pitch, s, e, vel, is_drum) in base_notes:
            s2 = s + offset
            e2 = e + offset
            if s2 >= duration_s:
                continue
            if e2 > duration_s:
                e2 = duration_s
            tiled.append({
                "pitch": pitch,
                "onset_s": round(s2, 6),
                "offset_s": round(e2, 6),
                "velocity": vel,
                "is_drum": is_drum,
            })
    tiled.sort(key=lambda r: (r["onset_s"], r["pitch"]))
    return tiled


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    manifest = {
        "loop_s": LOOP_S,
        "durations_s": DURATIONS,
        "stem_to_midi": STEM_TO_MIDI,
        "files": [],
    }
    for d in DURATIONS:
        mix_id = f"synth_{d:03d}s"
        out_dir = OUT_ROOT / mix_id
        out_dir.mkdir(parents=True, exist_ok=True)
        for stem, midi_name in STEM_TO_MIDI.items():
            midi_path = MIDI_DIR / midi_name
            notes = tile_notes(midi_path, float(d))
            # Serialize canonically (sorted keys, no trailing whitespace).
            lines = [json.dumps(n, sort_keys=True, separators=(",", ":")) for n in notes]
            payload = ("\n".join(lines) + "\n").encode("utf-8")
            out_path = out_dir / f"{stem}.reference.jsonl"
            out_path.write_bytes(payload)
            manifest["files"].append({
                "mix": mix_id,
                "stem": stem,
                "midi": str(midi_path.relative_to(ROOT)),
                "path": str(out_path.relative_to(ROOT)),
                "n_notes": len(notes),
                "sha256": sha256_bytes(payload),
            })
        # Vocals: emit empty reference (silent stem, zero notes).
        vocals_path = out_dir / "vocals.reference.jsonl"
        vocals_path.write_bytes(b"")
        manifest["files"].append({
            "mix": mix_id,
            "stem": "vocals",
            "midi": None,
            "path": str(vocals_path.relative_to(ROOT)),
            "n_notes": 0,
            "sha256": sha256_bytes(b""),
        })

    manifest_path = OUT_ROOT / "reference_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
