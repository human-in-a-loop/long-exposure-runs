#!/usr/bin/python3
"""c82 P5 tests — reindex fidelity: DURATIONS (not just counts) on synthetic two-chunk fixtures; per-chunk-JSON check record.

created: 2026-09-06T18:05:00Z
cycle: 82
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle82-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_reindex_fidelity_c82.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v5 import reindex_hook as RH  # noqa: E402
from scripts.v5 import reindex_canonical_v5 as RC  # noqa: E402
import mido  # noqa: E402

PPQ = 480


def _notes_seconds(mid: Path, bpm: float) -> list[tuple[float, float, int]]:
    """(start_s, duration_s, pitch) from a canonical MIDI serialized at `bpm`."""
    m = mido.MidiFile(str(mid))
    spb = 60.0 / bpm
    out = []
    for tr in m.tracks:
        t = 0
        open_: dict[int, list[int]] = {}
        for msg in tr:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                open_.setdefault(msg.note, []).append(t)
            elif msg.type in ("note_off", "note_on") and open_.get(msg.note):
                t0 = open_[msg.note].pop(0)
                out.append((t0 / PPQ * spb, (t - t0) / PPQ * spb, msg.note))
    return sorted(out)


def _fixture(specs: list[tuple[float, float, int, int]]) -> list:
    """specs = [(start_s, dur_s, pitch, chunk_local_index)] -> MuScriptor-shaped events (two chunks, colliding indices)."""
    ev = []
    for st, du, p, i in specs:
        ev.append({"type": "start", "index": i, "start_time": st, "pitch": p, "instrument": "acoustic_piano"})
        ev.append({"type": "end", "start_event_index": i, "end_time": round(st + du, 6), "pitch": p, "instrument": "acoustic_piano"})
    return ev


def _run_hook(specs, bpm=120.0) -> list[tuple[float, float, int]]:
    with tempfile.TemporaryDirectory(prefix="fid_c82_") as td:
        corpus = Path(td)
        sha16 = "c0ffeec0ffeec0ff"
        d = corpus / sha16
        (d / "muscriptor_full").mkdir(parents=True)
        for p in RH.PROBES:
            (d / "muscriptor_full" / f"{p}.json").write_text(json.dumps(_fixture(specs) if p == "piano" else []))
        (d / "transcription_manifest.json").write_text(json.dumps({"bpm_v5": bpm, "title": "fixture"}))
        RH.post_canonicalize(sha16, corpus)
        return _notes_seconds(d / RH.OUT_SUBDIR / "piano.mid", bpm)


def test_01_two_chunks_sharing_indices_recover_known_durations() -> None:
    # chunk 0 (t in [0,30)) and chunk 1 (t in [25,55)) share chunk-local indices 0..2; short notes, distinct pitches
    specs = [(1.0, 0.5, 60, 0), (2.0, 0.75, 62, 1), (3.0, 1.25, 64, 2),
             (26.0, 0.5, 65, 0), (27.0, 0.75, 67, 1), (28.0, 1.25, 69, 2)]
    got = _run_hook(specs)
    assert len(got) == 6, got
    tick = 60.0 / 120.0 / PPQ  # one tick in seconds
    for (st, du, p, _i), (gs, gd, gp) in zip(sorted(specs), got):
        assert gp == p and abs(gs - st) <= tick and abs(gd - du) <= tick, ((st, du, p), (gs, gd, gp))
    print("test_01 PASS: two-chunk fixture with colliding indices — 6/6 starts AND 6/6 durations recovered (<= 1 tick)")


def test_02_ambiguous_long_note_documents_the_c81_degraded_pairing_class() -> None:
    # chunk-0 index 0 is a LONG note (28 s); chunk-1 index 0 starts inside that span with a short duration. The c80 greedy
    # pairing (earliest end > start within 30 s) assigns chunk-1's end to chunk-0's start: onsets lossless, duration wrong.
    specs = [(1.0, 28.0, 60, 0), (26.0, 0.5, 65, 0)]
    got = _run_hook(specs)
    assert [g[2] for g in got] == [60, 65] and len(got) == 2, got  # onsets + pitches lossless
    tick = 60.0 / 120.0 / PPQ
    first_dur = got[0][1]
    assert abs(first_dur - 25.5) <= tick, first_dur  # greedy took the 26.5 s end (chunk 1) instead of the true 29.0 s end
    r, st = RC.reindex(_fixture(specs))
    assert st["n_paired"] == 2 and st["n_unpaired_starts"] == 0
    print(f"test_02 PASS: ambiguous long-note fixture reproduces the c81 DEGRADED class — first duration {first_dur:.3f} s vs true 28.0 s "
          "(counts lossless, duration wrong); chunk-window-constrained pairing is the pre-declared c83 candidate fix")


def test_03_per_chunk_json_check_record_on_disk() -> None:
    p = _ROOT / "data/v5/corpus/252eb21ce7df7328/reindex_fidelity_c82.json"
    assert p.exists(), p
    d = json.loads(p.read_text())
    assert d["verdict"] in ("REINDEX_PAIRING_HOLDS", "REINDEX_PAIRING_DEGRADED", "PER_CHUNK_JSON_ABSENT")
    if d["verdict"] == "PER_CHUNK_JSON_ABSENT":
        ev = d["evidence"]
        assert ev["stage_cache_outputs_for_other"] == ["other.json"] and ev["chunk_field_in_events"] is False
        assert ev["stage_cache_other_json_sha256"] == ev["muscriptor_full_other_json_sha256"]
    print(f"test_03 PASS: reindex_fidelity_c82.json verdict {d['verdict']}")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} reindex_fidelity_c82 tests PASS")
