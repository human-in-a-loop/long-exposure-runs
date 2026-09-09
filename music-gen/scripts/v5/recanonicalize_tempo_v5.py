#!/usr/bin/python3
"""c86 F4 CLOSE — re-canonicalize the two operator-adjudicated songs at their ADOPTED tempo (canonical_v5c_reindexed/).

created: 2026-09-09T23:05:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo-f4-operator-resolved-c86

Authority: OPERATOR addendum 2026-09-09 in docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt (sha 8677bb0c…),
recorded verbatim in data/v5/corpus/tempo_f4_operator_resolution_c86.json: Peach Dream 88d247468cb6d49f = 122.197271 BPM,
Disco A cdd2717e52820ff6 = 120.272335 BPM (the READ-ONLY c83 tempo_v5d refined-lag dominants).

Per song, for PROBES = drums/bass/guitar/other/piano/vocals/full_mix:
  1. READ-ONLY import scripts.v5.reindex_canonical_v5.reindex (the c80 lossless index/pairing fix) applied to
     data/v5/corpus/<sha16>/muscriptor_full/<probe>.json (never modified);
  2. READ-ONLY c4 serializer scripts.v3_spine.midi_from_json_events.serialize(json, mid, adopted_bpm, (4, 4)) into
     <out-root>/<sha16>/canonical_v5c_reindexed/<probe>.mid (+ <probe>.reindexed.json alongside);
  3. VERIFY MIDI note_on count == JSON start count per probe (lossless), and the set_tempo meta == adopted BPM;
  4. reindex_manifest.json mirroring reindex_canonical_v5.process_song's record, with bpm_v5c_adopted / bpm_v5_superseded /
     authority; sidecar <out-root>/<sha16>/canonical_v5c_reindexed_sha256.json {adopted_bpm, bars_at_adopted_bpm =
     duration_s * bpm / 240, per-file sha256s, reindex_manifest sha}.
canonical_v5_reindexed/ (c80, bpm_v5) is NEVER touched. --out-root <tempdir> gives the byte-determinism second run; every
path recorded inside the outputs is corpus-relative so the two runs are byte-comparable.

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; env pins; READ-ONLY inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
         "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

import mido  # noqa: E402

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v3_spine.midi_from_json_events import serialize as canonical_midi_serialize  # noqa: E402  READ-ONLY (c4)
from scripts.v5.reindex_canonical_v5 import PROBES, reindex  # noqa: E402  READ-ONLY (c80)

ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
OUT_SUBDIR = "canonical_v5c_reindexed"
SIDECAR_NAME = "canonical_v5c_reindexed_sha256.json"
RESOLUTION_DEFAULT = "data/v5/corpus/tempo_f4_operator_resolution_c86.json"
PPQ = 480
CYCLE = 86


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def midi_note_on_count_and_tempo(mid_path: Path) -> tuple[int, int]:
    """(note_on count, first set_tempo meta in integer microseconds per beat)."""
    m = mido.MidiFile(str(mid_path))
    assert m.ticks_per_beat == PPQ, f"{mid_path}: PPQ {m.ticks_per_beat} != {PPQ}"
    n_on, tempo = 0, None
    for tr in m.tracks:
        for msg in tr:
            if msg.type == "note_on" and msg.velocity > 0:
                n_on += 1
            elif msg.type == "set_tempo" and tempo is None:
                tempo = msg.tempo
    return n_on, tempo


def process_song(sha16: str, corpus: Path, out_root: Path, adopted_bpm: float, authority: dict) -> dict:
    d = corpus / sha16
    tm_p = d / "transcription_manifest.json"
    tm = json.loads(tm_p.read_text())
    bpm_v5 = float(tm["bpm_v5"])
    duration_s = float(tm["duration_s"])
    out_dir = out_root / sha16 / OUT_SUBDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = {"schema_version": 1, "cycle": CYCLE, "sha16": sha16, "title": tm.get("title"), "out_subdir": OUT_SUBDIR,
           "bpm_v5c_adopted": adopted_bpm, "bpm_v5_superseded": bpm_v5, "authority": authority,
           "reindex": "scripts.v5.reindex_canonical_v5.reindex (c80, READ-ONLY) on muscriptor_full/<probe>.json",
           "serializer": "scripts.v3_spine.midi_from_json_events.serialize (c4, READ-ONLY) at bpm_v5c_adopted, 4/4, PPQ 480",
           "env_pin_sha256": ENV_PIN_SHA256, "probes": {}}
    for p in PROBES:
        ev = json.loads((d / "muscriptor_full" / f"{p}.json").read_text())
        re_ev, stats = reindex(ev)
        rj = out_dir / f"{p}.reindexed.json"
        rj.write_text(json.dumps(re_ev, sort_keys=True, separators=(",", ":")))
        rm = out_dir / f"{p}.mid"
        canonical_midi_serialize(str(rj), str(rm), adopted_bpm, (4, 4))
        n_on, tempo_us = midi_note_on_count_and_tempo(rm)
        n_json_starts = sum(1 for e in ev if e.get("type") == "start")
        if n_on != n_json_starts or n_on != stats["n_starts_in"]:
            raise SystemExit(f"LOSSY: {sha16}/{p}: MIDI note_on {n_on} != JSON starts {n_json_starts} (reindex n_starts_in {stats['n_starts_in']})")
        # SMF set_tempo is an INTEGER microseconds-per-beat (mido.bpm2tempo rounds): the exact check is on the integer; the
        # float round-trip differs from the adopted BPM by up to ~2.5e-4 BPM at 120 BPM (quantization, disclosed; same for c80).
        expected_us = mido.bpm2tempo(float(adopted_bpm))
        if tempo_us != expected_us:
            raise SystemExit(f"TEMPO_META: {sha16}/{p}: set_tempo {tempo_us} us != bpm2tempo({adopted_bpm}) = {expected_us}")
        bpm_roundtrip = float(mido.tempo2bpm(tempo_us))
        v5_mid = d / "canonical_v5_reindexed" / f"{p}.mid"  # READ-ONLY reference (c80, bpm_v5)
        stats.update({"n_midi_note_on": n_on, "n_json_starts": n_json_starts, "note_on_equals_json_starts": True,
                      "set_tempo_us": tempo_us, "set_tempo_us_equals_bpm2tempo_adopted": True,
                      "set_tempo_bpm_roundtrip": round(bpm_roundtrip, 6), "set_tempo_quantization_delta_bpm": round(bpm_roundtrip - adopted_bpm, 9),
                      "reindexed_json_sha256": sha(rj), "midi_sha256": sha(rm),
                      "c80_bpm_v5_midi_sha256": sha(v5_mid) if v5_mid.exists() else None})
        rec["probes"][p] = stats
    rec["note"] = ("canonical_v5_reindexed/ (c80, bpm_v5) left untouched; consumers prefer canonical_v5c_reindexed/ via the "
                   "MIDI_DIR_PREFERENCE tuple (harmony_v5.py, groove_v5_v2.py)")
    man = out_dir / "reindex_manifest.json"
    man.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    side = {"schema_version": 1, "cycle": CYCLE, "hook_version": "c86.v5c", "sha16": sha16, "title": tm.get("title"),
            "adopted_bpm": adopted_bpm, "bpm_v5_superseded": bpm_v5, "duration_s": duration_s,
            "bars_at_adopted_bpm": round(duration_s * adopted_bpm / 240.0, 6),
            "beats_at_adopted_bpm": round(duration_s * adopted_bpm / 60.0, 6),
            "authority": authority, "env_pin_sha256": ENV_PIN_SHA256,
            "reindexed_dir": f"data/v5/corpus/{sha16}/{OUT_SUBDIR}",
            "midi_sha256": {p: rec["probes"][p]["midi_sha256"] for p in PROBES},
            "reindexed_json_sha256": {p: rec["probes"][p]["reindexed_json_sha256"] for p in PROBES},
            "n_midi_note_on": {p: rec["probes"][p]["n_midi_note_on"] for p in PROBES},
            "reindex_manifest_sha256": sha(man), "transcription_manifest_sha256": sha(tm_p),
            "note": "additive sidecar; transcription_manifest.json and canonical_v5_reindexed/ bytes are never rewritten"}
    (out_root / sha16 / SIDECAR_NAME).write_text(json.dumps(side, sort_keys=True, indent=2) + "\n")
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="c86: re-canonicalize operator-adjudicated songs at the adopted tempo (canonical_v5c_reindexed/)")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--out-root", default=None, help="default: --corpus-dir (real run); a fresh tempdir for the byte-det second run")
    ap.add_argument("--resolution", default=RESOLUTION_DEFAULT, help="operator resolution JSON carrying adopted_bpm {sha16: bpm}")
    ap.add_argument("--songs", nargs="*", default=None, help="default: every song in the resolution's adopted_bpm")
    args = ap.parse_args(argv)
    os.chdir(_WS)
    corpus = Path(args.corpus_dir)
    out_root = Path(args.out_root) if args.out_root else corpus
    res_p = Path(args.resolution)
    res = json.loads(res_p.read_text())
    adopted = {str(k): float(v) for k, v in res["adopted_bpm"].items()}
    authority = {"kind": res.get("authority", "OPERATOR"), "resolution_path": str(res_p), "resolution_sha256": sha(res_p),
                 "guidance_path": res["guidance"]["path"], "guidance_sha256": res["guidance"]["sha256"],
                 "supersedes_path": res["supersedes"]["path"], "supersedes_sha256": res["supersedes"]["sha256"]}
    songs = args.songs or sorted(adopted)
    for s in songs:
        if s not in adopted:
            raise SystemExit(f"NO_ADOPTED_BPM: {s} is not in {res_p}")
        rec = process_song(s, corpus, out_root, adopted[s], authority)
        print(f"{s} {rec['title']}: bpm_v5 {rec['bpm_v5_superseded']} -> v5c {rec['bpm_v5c_adopted']}; " +
              "; ".join(f"{p} {v['n_json_starts']}->{v['n_midi_note_on']} note_on ({v['n_paired']} paired/{v['n_unpaired_starts']} unpaired)"
                        for p, v in rec["probes"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
