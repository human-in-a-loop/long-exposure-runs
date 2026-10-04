#!/usr/bin/python3
"""Phase 4 (instrument realism) — deterministic smoke-render of one inventory entry.

created: 2026-10-04
milestone: M-V6-INSTRUMENTS-1

Given an entry of workspace/instruments/INVENTORY.json (library slug + instrument name),
write a deterministic 4-bar test MIDI (mido; 100 BPM, 4/4, three velocity levels, a
role-appropriate register) and render it through the right backend:

  * .sfz  -> sfizz_render --sfz <file> --midi <mid> --wav <out> --samplerate 44100
  * .sf2  -> fluidsynth -ni -F out.wav -r 44100 -g 0.8 -o synth.reverb.active=false
             -o synth.chorus.active=false <sf2> <mid>   (bank/program forced inside the MIDI)
  * dawdreamer (Surge XT / Dexed VST3) -> delegated to scripts/v6/render_vst_test.py

Outputs workspace/instruments/_renders/<slug>__<instrument>.wav and .json with RMS dBFS,
peak dBFS, duration and a "silent"/"ok"/"error" status.

Usage:
  render_patch_test.py --slug finger_bass_yr --instrument "FingerBassYR"
  render_patch_test.py --all [--verify-determinism SLUG::INSTRUMENT]
  render_patch_test.py --all --prune        # rewrite INVENTORY.json: move failures to "rejected"

Both samplers are deterministic for identical inputs; --verify-determinism renders an entry
twice and asserts the wav bytes are sha256-identical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import mido
import numpy as np
import soundfile as sf

WS = Path(__file__).resolve().parent.parent.parent  # .../music-gen
INSTR_ROOT = WS / "workspace" / "instruments"
INVENTORY = INSTR_ROOT / "INVENTORY.json"
RENDERS = INSTR_ROOT / "_renders"

SAMPLE_RATE = 44100
BPM = 100
BARS = 4
TAIL_SEC = 1.5
VELOCITIES = (48, 84, 120)      # three velocity levels, cycled
TPB = 480                       # ticks per beat
GM_DRUM_KEYS = (36, 38, 42, 46, 49)
SILENT_RMS_DBFS = -60.0
SILENT_PEAK_DBFS = -45.0

ROLE_FAMILY = {
    "bass": "bass", "electric_bass": "bass", "acoustic_bass": "bass", "synth_bass": "bass",
    "piano": "keys", "electric_piano": "keys", "organ": "keys", "keys": "keys", "clav": "keys",
    "electric_guitar": "guitar", "acoustic_guitar": "guitar", "guitar": "guitar",
    "drums": "drums",
    "pad": "pad", "strings_pad": "pad", "strings": "pad", "choir": "pad",
    "lead": "lead", "synth_lead": "lead",
    "brass": "brass", "horns": "brass",
    "percussion": "percussion",
}


# --------------------------------------------------------------------------- MIDI

def _beat(t: float) -> int:
    return int(round(t * TPB))


def _events_for_family(family: str, keys: list[int] | None) -> list[tuple[float, int, int, float]]:
    """(start_beat, note, velocity, duration_beats) — 4 bars of 4/4 = 16 beats."""
    ev: list[tuple[float, int, int, float]] = []
    vel = lambda i: VELOCITIES[i % 3]  # noqa: E731
    if family == "bass":
        # E1..G2 riff: E1 E1 G1 A1 | B1 D2 E2 G2 | ... eighth notes, 3 velocity tiers
        riff = [28, 28, 31, 33, 35, 38, 40, 43, 40, 38, 35, 33, 31, 35, 28, 31]
        for bar in range(BARS):
            for k in range(8):
                i = bar * 8 + k
                ev.append((bar * 4 + k * 0.5, riff[i % len(riff)], vel(i), 0.45))
    elif family == "keys":
        # C3..C5: single-note riff for 2 bars, then block triads for 2 bars
        riff = [48, 52, 55, 60, 64, 67, 72, 67, 64, 60, 55, 52, 48, 55, 60, 64]
        for k in range(16):
            ev.append((k * 0.5, riff[k], vel(k), 0.45))
        chords = [(48, 55, 64), (53, 60, 65), (55, 59, 62), (48, 52, 55)]
        for c, chord in enumerate(chords):
            for n in chord:
                ev.append((8 + c * 2, n, vel(c), 1.9))
    elif family == "guitar":
        # E2..E4: arpeggiated eighths then strummed chord shapes
        riff = [40, 47, 52, 55, 59, 64, 59, 55, 52, 47, 40, 45, 50, 54, 57, 62]
        for k in range(16):
            ev.append((k * 0.5, riff[k], vel(k), 0.45))
        chords = [(40, 47, 52, 56, 59), (45, 52, 57, 61, 64), (43, 50, 55, 59, 62), (40, 47, 52, 55, 59)]
        for c, chord in enumerate(chords):
            for j, n in enumerate(chord):
                ev.append((8 + c * 2 + j * 0.02, n, vel(c), 1.8))
    elif family == "drums":
        kick, snare, hh_c, hh_o, crash = GM_DRUM_KEYS
        for bar in range(BARS):
            b0 = bar * 4
            if bar == 0:
                ev.append((b0, crash, 110, 1.0))
            for k in range(8):
                ev.append((b0 + k * 0.5, hh_o if k == 7 else hh_c, vel(k + bar), 0.2))
            ev.append((b0 + 0.0, kick, 120, 0.3))
            ev.append((b0 + 2.5, kick, 100, 0.3))
            ev.append((b0 + 1.0, snare, VELOCITIES[(bar + 1) % 3], 0.3))
            ev.append((b0 + 3.0, snare, VELOCITIES[(bar + 2) % 3], 0.3))
    elif family == "pad":
        chords = [(48, 55, 64, 67), (53, 60, 65, 69), (55, 59, 62, 67), (48, 52, 55, 60)]
        for c, chord in enumerate(chords):
            for n in chord:
                ev.append((c * 4, n, vel(c), 3.9))
    elif family == "lead":
        mel = [60, 62, 64, 67, 69, 72, 69, 67, 64, 62, 60, 67, 72, 76, 72, 67]
        for k in range(16):
            ev.append((k * 1.0 if k < 8 else 8 + (k - 8) * 1.0, mel[k], vel(k), 0.9))
    elif family == "brass":
        chords = [(48, 55, 60, 64), (53, 57, 60, 65), (50, 55, 59, 62), (48, 52, 55, 60)]
        for c, chord in enumerate(chords):
            for n in chord:
                ev.append((c * 4, n, vel(c), 0.7))
                ev.append((c * 4 + 1.5, n, vel(c + 1), 0.4))
                ev.append((c * 4 + 2.5, n, vel(c + 2), 1.3))
    elif family == "percussion":
        ks = keys or [60, 61, 62, 63, 64, 65, 66, 67]
        for k in range(32):
            ev.append((k * 0.5, ks[k % len(ks)], vel(k), 0.3))
    else:
        raise ValueError(f"unknown family {family!r}")
    return ev


def write_test_midi(path: Path, role: str, *, bank: int | None = None, program: int | None = None,
                    channel: int = 0, keys: list[int] | None = None) -> Path:
    """Deterministic 4-bar MIDI; bank/program forced via CC0/CC32 + program_change when given."""
    family = ROLE_FAMILY.get(role, role)
    mid = mido.MidiFile(ticks_per_beat=TPB, type=0)
    trk = mido.MidiTrack()
    mid.tracks.append(trk)
    trk.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    trk.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    if bank is not None:
        trk.append(mido.Message("control_change", channel=channel, control=0, value=min(bank, 127), time=0))
        trk.append(mido.Message("control_change", channel=channel, control=32, value=0, time=0))
    if program is not None:
        trk.append(mido.Message("program_change", channel=channel, program=program, time=0))
    trk.append(mido.Message("control_change", channel=channel, control=7, value=100, time=0))
    abs_events: list[tuple[int, int, str, int, int]] = []  # (tick, order, kind, note, vel)
    for start, note, vel, dur in _events_for_family(family, keys):
        abs_events.append((_beat(start), 1, "on", note, vel))
        abs_events.append((_beat(start + dur), 0, "off", note, 0))
    abs_events.sort()
    t_prev = 0
    for tick, _order, kind, note, vel in abs_events:
        delta = tick - t_prev
        t_prev = tick
        if kind == "on":
            trk.append(mido.Message("note_on", channel=channel, note=note, velocity=vel, time=delta))
        else:
            trk.append(mido.Message("note_off", channel=channel, note=note, velocity=0, time=delta))
    end_tick = _beat(BARS * 4 + TAIL_SEC * BPM / 60.0)
    trk.append(mido.MetaMessage("end_of_track", time=max(0, end_tick - t_prev)))
    path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(str(path))
    return path


# --------------------------------------------------------------------------- backends

def _run(cmd: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    env = dict(os.environ, LC_ALL="C")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)


def render_sfz(sfz: Path, mid: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    r = _run(["sfizz_render", "--sfz", str(sfz), "--midi", str(mid), "--wav", str(out),
              "--samplerate", str(SAMPLE_RATE)])
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"sfizz_render rc={r.returncode}: {(r.stderr or r.stdout)[-600:]}")


def render_sf2(sf2: Path, mid: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    r = _run(["fluidsynth", "-ni", "-F", str(out), "-r", str(SAMPLE_RATE), "-g", "0.8",
              "-o", "synth.reverb.active=false", "-o", "synth.chorus.active=false",
              str(sf2), str(mid)])
    if r.returncode != 0 or not out.exists():
        raise RuntimeError(f"fluidsynth rc={r.returncode}: {(r.stderr or r.stdout)[-600:]}")


def analyze_wav(path: Path) -> dict:
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    if data.size == 0:
        return {"rms_dbfs": -np.inf, "peak_dbfs": -np.inf, "duration_sec": 0.0, "samplerate": sr, "channels": data.shape[1]}
    rms = float(np.sqrt(np.mean(np.square(data, dtype=np.float64))))
    peak = float(np.max(np.abs(data)))
    to_db = lambda x: float(20 * np.log10(x)) if x > 0 else -np.inf  # noqa: E731
    return {"rms_dbfs": round(to_db(rms), 2), "peak_dbfs": round(to_db(peak), 2),
            "duration_sec": round(data.shape[0] / sr, 3), "samplerate": sr, "channels": data.shape[1],
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def render_entry(lib: dict, inst: dict, out_dir: Path = RENDERS, midi_dir: Path | None = None) -> dict:
    """Render one inventory entry; returns the result record (also written as JSON next to the wav)."""
    slug = lib["slug"]
    name = inst["name"]
    role = inst["role"]
    base = f"{slug}__{_slugify(name)}"
    out_wav = out_dir / f"{base}.wav"
    out_json = out_dir / f"{base}.json"
    midi_dir = midi_dir or (out_dir / "_midi")
    mid = midi_dir / f"{base}.mid"
    rec = {"slug": slug, "instrument": name, "role": role, "backend": inst.get("backend") or lib.get("format"),
           "wav": str(out_wav.relative_to(INSTR_ROOT)), "midi": str(mid.relative_to(INSTR_ROOT))}
    try:
        fmt = inst.get("backend") or lib.get("format")
        if fmt == "sfz":
            sfz = INSTR_ROOT / inst["path"]
            write_test_midi(mid, role, channel=0, keys=inst.get("keys"))
            render_sfz(sfz, mid, out_wav)
        elif fmt == "sf2":
            sf2 = inst["path"] if os.path.isabs(inst["path"]) else str(INSTR_ROOT / inst["path"])
            bank, program = int(inst["bank"]), int(inst["program"])
            channel = 9 if bank == 128 else 0
            write_test_midi(mid, role, bank=None if bank == 128 else bank, program=program,
                            channel=channel, keys=inst.get("keys"))
            render_sf2(Path(sf2), mid, out_wav)
        elif fmt == "dawdreamer":
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from render_vst_test import render_vst_entry  # lazy: dawdreamer is optional
            write_test_midi(mid, role, channel=0, keys=inst.get("keys"))
            render_vst_entry(inst, mid, out_wav)
        else:
            raise ValueError(f"unknown backend/format {fmt!r}")
        rec.update(analyze_wav(out_wav))
        silent = (rec["rms_dbfs"] < SILENT_RMS_DBFS) or (rec["peak_dbfs"] < SILENT_PEAK_DBFS)
        rec["status"] = "silent" if silent else "ok"
    except Exception as exc:  # noqa: BLE001 - we want the reason in the record
        rec["status"] = "error"
        rec["error"] = f"{type(exc).__name__}: {str(exc)[-700:]}"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return rec


def load_inventory(path: Path = INVENTORY) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def iter_entries(inv: dict):
    for lib in inv["libraries"]:
        for inst in lib.get("instruments", []):
            yield lib, inst


def verify_determinism(lib: dict, inst: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="detcheck_", dir=str(RENDERS.parent)) as td:
        a = render_entry(lib, inst, out_dir=Path(td) / "a")
        b = render_entry(lib, inst, out_dir=Path(td) / "b")
    ok = a.get("sha256") and a.get("sha256") == b.get("sha256")
    return {"slug": lib["slug"], "instrument": inst["name"], "identical": bool(ok),
            "sha256_a": a.get("sha256"), "sha256_b": b.get("sha256"), "status_a": a["status"], "status_b": b["status"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inventory", default=str(INVENTORY))
    ap.add_argument("--slug")
    ap.add_argument("--instrument")
    ap.add_argument("--all", action="store_true", help="render every inventory entry")
    ap.add_argument("--only-backend", choices=["sfz", "sf2", "dawdreamer"])
    ap.add_argument("--prune", action="store_true",
                    help="rewrite INVENTORY.json moving silent/error entries to 'rejected'")
    ap.add_argument("--verify-determinism", metavar="SLUG::INSTRUMENT",
                    help="render this entry twice and compare sha256")
    args = ap.parse_args(argv)

    inv = load_inventory(Path(args.inventory))
    RENDERS.mkdir(parents=True, exist_ok=True)

    if args.verify_determinism:
        slug, name = args.verify_determinism.split("::", 1)
        for lib, inst in iter_entries(inv):
            if lib["slug"] == slug and inst["name"] == name:
                res = verify_determinism(lib, inst)
                print(json.dumps(res, indent=2))
                return 0 if res["identical"] else 2
        print("entry not found", file=sys.stderr)
        return 1

    results = []
    for lib, inst in iter_entries(inv):
        if not args.all and (lib["slug"] != args.slug or (args.instrument and inst["name"] != args.instrument)):
            continue
        if args.only_backend and (inst.get("backend") or lib.get("format")) != args.only_backend:
            continue
        rec = render_entry(lib, inst)
        results.append(rec)
        flag = rec["status"].upper()
        extra = f"rms={rec.get('rms_dbfs')} peak={rec.get('peak_dbfs')} dur={rec.get('duration_sec')}" \
            if rec["status"] != "error" else rec.get("error", "")[:160]
        print(f"[{flag:6}] {lib['slug']:28} {inst['name'][:40]:40} {extra}", flush=True)

    summary_path = RENDERS / "_render_summary.json"
    prev = json.load(open(summary_path)) if summary_path.exists() else {}
    for r in results:
        prev[f"{r['slug']}::{r['instrument']}"] = r
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(prev, fh, indent=2, sort_keys=True)
        fh.write("\n")

    if args.prune:
        bad = {(r["slug"], r["instrument"]): r for r in results if r["status"] != "ok"}
        rejected = inv.setdefault("rejected", [])
        for lib in inv["libraries"]:
            keep = []
            for inst in lib.get("instruments", []):
                r = bad.get((lib["slug"], inst["name"]))
                if r is None:
                    keep.append(inst)
                else:
                    rejected.append({"slug": lib["slug"], "instrument": inst["name"], "role": inst["role"],
                                     "path": inst.get("path"), "reason": r["status"],
                                     "detail": r.get("error") or f"rms_dbfs={r.get('rms_dbfs')} peak_dbfs={r.get('peak_dbfs')}"})
            lib["instruments"] = keep
        with open(args.inventory, "w", encoding="utf-8") as fh:
            json.dump(inv, fh, indent=2, sort_keys=False, ensure_ascii=False)
            fh.write("\n")
        print(f"pruned {len(bad)} entries -> rejected")
    n_ok = sum(1 for r in results if r["status"] == "ok")
    print(f"rendered {len(results)} entries: {n_ok} ok, {len(results) - n_ok} silent/error")
    return 0


if __name__ == "__main__":
    sys.exit(main())
