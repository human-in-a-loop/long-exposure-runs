#!/usr/bin/python3
"""c80 — re-index chunk-merged MuScriptor JSON and re-serialize canonical MIDI (defect fix).

created: 2026-09-06T16:45:00Z
cycle: 80
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/canonical-midi-index-collision-c80

DEFECT (first-class finding, c80): the READ-ONLY c22 `recreate_v3._merge_chunk_events`
re-offsets chunk times but never re-numbers `index` / `start_event_index`, so a
full-length song transcribed in 30 s chunks carries colliding indices. The
READ-ONLY c4 serializer keys starts by `index` in a dict, keeping ONE start per
index, so c79's `canonical_midi_full/*.mid` silently dropped most notes (WIG
other: 1799 JSON starts -> 395 MIDI note_on). 30 s v3 sections were single-chunk
and unaffected. MuScriptor JSON is intact (all starts + ends present).

FIX (pure function of the JSON; neither READ-ONLY module is modified):
  1. sort starts by (start_time, instrument, pitch, original index);
  2. for each start, pair the earliest unconsumed end with the same chunk-local
     `start_event_index`, end_time > start_time and end_time - start_time <= CHUNK_LEN
     (30 s, the maximum span of a chunk-local pair); unmatched -> no end event
     (serializer applies its 100 ms synthetic duration, as before);
  3. assign sequential indices 0..N-1, rewrite `start_event_index` accordingly;
  4. call the READ-ONLY c4 `serialize()` at bpm_v5 / 4-4 into
     data/v5/corpus/<sha16>/canonical_v5_reindexed/<probe>.mid (+ the re-indexed
     JSON alongside, so the MIDI provenance is inspectable).
Pairing is a deterministic greedy heuristic (disclosed); it recovers every
start (no note is lost) and can only mis-assign durations where two chunks
emitted the same chunk-local index within 30 s of each other.

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state
APIs; canonical_midi_full/ (c79) is left untouched as the lossy anchor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_WS))
from scripts.v3_spine.midi_from_json_events import serialize as canonical_midi_serialize  # noqa: E402  READ-ONLY

PROBES = ["drums", "bass", "guitar", "other", "piano", "vocals", "full_mix"]
CHUNK_LEN_S = 30.0
OUT_SUBDIR = "canonical_v5_reindexed"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def reindex(events: list) -> tuple[list, dict]:
    starts = [e for e in events if e.get("type") == "start"]
    ends = [e for e in events if e.get("type") == "end"]
    starts.sort(key=lambda e: (float(e["start_time"]), str(e.get("instrument")), int(e["pitch"]), int(e["index"])))
    ends_by_sei: dict[int, list] = {}
    for e in ends:
        ends_by_sei.setdefault(int(e["start_event_index"]), []).append(e)
    for lst in ends_by_sei.values():
        lst.sort(key=lambda e: float(e["end_time"]))
    consumed: set[int] = set()
    out: list = []
    stats = {"n_starts_in": len(starts), "n_ends_in": len(ends), "n_distinct_index_in": len({int(e["index"]) for e in starts}),
             "n_paired": 0, "n_unpaired_starts": 0, "n_unconsumed_ends": 0}
    for new_i, s in enumerate(starts):
        s2 = dict(s)
        s2["index"] = new_i
        s2["original_index"] = int(s["index"])
        out.append(s2)
        st = float(s["start_time"])
        cands = ends_by_sei.get(int(s["index"]), [])
        for e in cands:
            if id(e) in consumed:
                continue
            et = float(e["end_time"])
            if et > st and et - st <= CHUNK_LEN_S:
                consumed.add(id(e))
                e2 = dict(e)
                e2["start_event_index"] = new_i
                e2["original_start_event_index"] = int(e["start_event_index"])
                out.append(e2)
                stats["n_paired"] += 1
                break
        else:
            stats["n_unpaired_starts"] += 1
    stats["n_unconsumed_ends"] = len(ends) - len(consumed)
    return out, stats


def process_song(sha16: str, corpus: Path) -> dict:
    d = corpus / sha16
    tm = json.loads((d / "transcription_manifest.json").read_text())
    bpm = float(tm["bpm_v5"])
    out_dir = d / OUT_SUBDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = {"sha16": sha16, "bpm_v5": bpm, "probes": {}}
    for p in PROBES:
        ev = json.loads((d / "muscriptor_full" / f"{p}.json").read_text())
        re_ev, stats = reindex(ev)
        rj = out_dir / f"{p}.reindexed.json"
        rj.write_text(json.dumps(re_ev, sort_keys=True, separators=(",", ":")))
        rm = out_dir / f"{p}.mid"
        canonical_midi_serialize(str(rj), str(rm), bpm, (4, 4))
        old = d / "canonical_midi_full" / f"{p}.mid"
        stats.update({"reindexed_json_sha256": sha(rj), "midi_sha256": sha(rm),
                      "c79_lossy_midi_sha256": sha(old) if old.exists() else None})
        rec["probes"][p] = stats
    rec["note"] = "c79 canonical_midi_full/ left untouched (lossy anchor); consumers should read canonical_v5_reindexed/"
    (out_dir / "reindex_manifest.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--songs", nargs="*", default=None, help="default: every song with transcription_manifest.json")
    args = ap.parse_args()
    os.chdir(_WS)
    corpus = Path(args.corpus_dir)
    songs = args.songs or sorted(p.parent.name for p in corpus.glob("*/transcription_manifest.json"))
    for s in songs:
        rec = process_song(s, corpus)
        print(f"{s}: " + "; ".join(f"{p} {v['n_starts_in']}->{v['n_paired']} paired/{v['n_unpaired_starts']} unpaired "
                                   f"(distinct idx {v['n_distinct_index_in']})" for p, v in rec["probes"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
