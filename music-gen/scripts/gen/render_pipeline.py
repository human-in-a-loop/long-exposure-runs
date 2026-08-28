#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:20:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 00b3ae64444c)
# milestone: M-GEN-1/first-generation
# ---
"""Render pipeline for M-GEN-1: MusicXML -> MIDI -> bare WAV -> effects WAV.

    render(xml_path, out_dir) -> RenderManifest
        - out_dir/generated.mid
        - out_dir/bare_midi.wav (44.1 kHz stereo, SF2 sha 74594e8f...1cb0)
        - out_dir/effects_layered.wav (cycle-9 DawDreamer chain, numpy fallback)

Chains:
  * xml_to_midi from scripts.score.bridge (M-SCORE-1/bridge-api).
  * render_bare_midi from scripts.tex.render_bare_midi (cycle 9,
    fluidsynth SF2-pinned).
  * apply_effects_layered from scripts.tex.render_effects_layered
    (DawDreamer chain, numpy fallback when Surge XT missing).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict

# Determinism pins BEFORE any downstream import may pull in torch/numpy.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

from scripts.score.bridge import xml_to_midi
from scripts.tex.render_bare_midi import render_bare_midi
from scripts.tex.render_effects_layered import apply_effects_layered


SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class RenderManifest:
    xml_path: str
    xml_sha256: str
    midi_path: str
    midi_sha256: str
    bare_wav_path: str
    bare_wav_sha256: str
    effects_wav_path: str
    effects_wav_sha256: str
    effects_rung: str
    sr: int = 44100
    sf2_sha256: str = ""


def render(xml_path: Path, out_dir: Path, *, duration_s: float | None = 30.0) -> RenderManifest:
    xml_path = Path(xml_path)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    mid = out_dir / "generated.mid"
    bare = out_dir / "bare_midi.wav"
    fx = out_dir / "effects_layered.wav"

    xml_to_midi(xml_path, mid)
    render_bare_midi(mid, bare, SF2_PATH, sr=44100, duration_s=duration_s)
    rung = apply_effects_layered(bare, fx)

    return RenderManifest(
        xml_path=str(xml_path), xml_sha256=_sha256(xml_path),
        midi_path=str(mid), midi_sha256=_sha256(mid),
        bare_wav_path=str(bare), bare_wav_sha256=_sha256(bare),
        effects_wav_path=str(fx), effects_wav_sha256=_sha256(fx),
        effects_rung=rung, sr=44100,
        sf2_sha256=_sha256(SF2_PATH),
    )


def _main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", type=Path, default=Path("data/gen/generated.musicxml"))
    ap.add_argument("--out-dir", type=Path, default=Path("data/gen/renders"))
    ap.add_argument("--duration-s", type=float, default=30.0)
    ap.add_argument("--manifest-out", type=Path,
                    default=Path("data/gen/render_manifest.json"))
    args = ap.parse_args(argv)
    m = render(args.xml, args.out_dir, duration_s=args.duration_s)
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.write_text(json.dumps(asdict(m), indent=2, sort_keys=True))
    print(f"[render_pipeline] rung={m.effects_rung}")
    print(f"[render_pipeline] xml sha  = {m.xml_sha256[:16]}...")
    print(f"[render_pipeline] mid sha  = {m.midi_sha256[:16]}...")
    print(f"[render_pipeline] bare sha = {m.bare_wav_sha256[:16]}...")
    print(f"[render_pipeline] fx   sha = {m.effects_wav_sha256[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
