#!/usr/bin/env /usr/bin/python3
"""c20 clone-2: fluidsynth per-track render for Peach Dream merged.mid x2.

Per-song sibling of scripts/v3_spine/render_per_track_operator_section.py (READ-ONLY).
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import mido

SEC = Path("data/v3_spine/88d247468cb6d49f/chosen_section")
DEL = Path("data/v3/deliveries/88d247468cb6d49f")
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
MERGED = SEC / "merged.mid"
OUT_DIR = SEC / "render" / "per_track"
DEL_PT = DEL / "per_track"
TRACKS = [("drums", 9), ("bass", 0), ("guitar", 1), ("piano", 2), ("other", 4)]


def split_track(source: Path, name: str, dst: Path):
    mf = mido.MidiFile(source)
    new_mf = mido.MidiFile(type=1, ticks_per_beat=mf.ticks_per_beat)
    new_mf.tracks.append(mf.tracks[0])
    for tr in mf.tracks[1:]:
        tn = None
        for m in tr:
            if m.type == "track_name":
                tn = m.name; break
        if tn == name:
            new_mf.tracks.append(tr); break
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".mid.tmp")
    new_mf.save(tmp)
    tmp.replace(dst)


def fluid(midi: Path, wav: Path):
    env = os.environ.copy()
    env.update({"PYTHONHASHSEED":"0","SOURCE_DATE_EPOCH":"1756463424","TZ":"UTC","LC_ALL":"C.UTF-8"})
    wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["fluidsynth","-ni","-F",str(wav),"-r","44100","-o","synth.cpu-cores=1",
           "-o","synth.reverb.active=false","-o","synth.chorus.active=false",
           SF2, str(midi)]
    r = subprocess.run(cmd, env=env, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"fluidsynth rc={r.returncode}: {r.stderr.decode()[-500:]}")


def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DEL_PT.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, _ in TRACKS:
        single = OUT_DIR / f"{name}.mid"
        split_track(MERGED, name, single)
        with tempfile.TemporaryDirectory(prefix=f"pd_r_{name}_r1_") as d1:
            w1 = Path(d1)/f"{name}.wav"
            fluid(single, w1)
            s1 = sha(w1)
            final = OUT_DIR/f"{name}.wav"
            shutil.copy2(w1, final)
            shutil.copy2(w1, DEL_PT / f"{name}.wav")
        with tempfile.TemporaryDirectory(prefix=f"pd_r_{name}_r2_") as d2:
            w2 = Path(d2)/f"{name}.wav"
            fluid(single, w2)
            s2 = sha(w2)
        results[name] = {"wav_path": str(final), "sha_r1": s1, "sha_r2": s2, "equal": s1==s2}
        print(f"{name:10s} r1={s1[:12]} r2={s2[:12]} equal={s1==s2}")

    out = SEC / "render" / "per_track_determinism.json"
    out.write_text(json.dumps({
        "cycle": 20, "clone": "clone-2", "song_sha16": "88d247468cb6d49f",
        "sf2_path": SF2, "sf2_sha256": sha(Path(SF2)),
        "results": results,
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
