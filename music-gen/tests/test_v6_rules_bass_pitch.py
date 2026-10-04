#!/usr/bin/python3
"""v6 rules tests — bass_pitch_v6: onset pitch picking (Viterbi-voiced median in the post-attack window), the sibling chords_v6
adapter (grid_beat / legacy stream-beat + phase / time layouts, 'N' handling), tick mapping, cache invalidation, and the written
bass_pitch_v5.json (schema the composer reads, smoothed rows, register in the GM bass range, per-song chord sources).

Run: /usr/bin/python3 tests/test_v6_rules_bass_pitch.py      or      /usr/bin/python3 -m pytest tests/test_v6_rules_bass_pitch.py -q
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

import numpy as np  # noqa: E402

from scripts.v5 import bass_pitch_v5 as V5  # noqa: E402
from scripts.v6.rules import bass_pitch_v6 as BP  # noqa: E402
from scripts.v6.v6_data_common import write_json_atomic  # noqa: E402

V5_FILE = _ROOT / "data/v5/rules/bass_pitch_v5.json"
V6_FILE = _ROOT / "data/v6/rules/bass_pitch_v6.json"
GRID = {"phase": 2, "hypermeter_offset": 1, "beat_times": [0.5 * i for i in range(64)]}


def test_01_hz_to_midi_and_pitch_at_onsets() -> None:
    assert BP.hz_to_midi(440.0) == 69 and BP.hz_to_midi(55.0) == 33 and BP.hz_to_midi(41.2) == 28
    t = np.arange(0, 2.0, 0.01)
    f0 = np.full(t.size, np.nan)
    voiced = np.zeros(t.size, dtype=bool)
    f0[50:80], voiced[50:80] = 110.0, True            # a note at 0.5 s: 300 ms of A2
    f0[52], voiced[52] = 55.0, True                   # one octave-error frame in the attack (skipped by the 20 ms window start)
    f0[120:125], voiced[120:125] = 82.4, True         # a short E2 at 1.2 s
    midi = BP.pitch_at_onsets(f0, voiced, t, [0.5, 1.2, 1.5, 0.49])
    assert midi == [45, 40, None, 45], midi
    assert BP.pitch_at_onsets(f0, voiced, t, [0.5], win_s=(0.0, 0.03)) == [45], "median over 3 frames (110, 110, 55) is 110"
    print(f"test_01 PASS: onset pitches {midi}")


def test_02_adapter_sibling_grid_beat_layout() -> None:
    seq = [{"bar": 0, "beat": 0, "grid_beat": 2, "chord": "N", "quality": "N", "root": None, "silent": True},
           {"bar": 0, "beat": 1, "grid_beat": 3, "chord": "G:maj", "quality": "maj", "root": 7, "silent": False},
           {"bar": 0, "beat": 2, "grid_beat": 4, "chord": "C:maj7", "quality": "maj7", "root": 12 + 0, "silent": False}]
    d = {"chords": {"chord_stream": seq, "n_changes": 1}, "key": {"tonic": 7, "mode": "major", "corr": 0.8},
         "grid": {"phase": 2, "bar_convention": "stream beat = grid beat - phase; bar = beat // 4"}}
    stream, key, notes = BP.adapt_sibling_chords(d, GRID)
    assert [c["beat"] for c in stream] == [2, 3, 4] and notes["by_grid_beat"] == 3 and notes["by_stream_beat"] == 0
    assert stream[0] == {"beat": 2, "root": None, "quality": None, "state": "N"} and stream[1]["root"] == 7 and stream[2]["root"] == 0
    assert stream[1]["state"] == "ok" and stream[2]["quality"] == "maj7" and key["tonic"] == 7 and key["mode"] == "major"
    print("test_02 PASS: sibling chords.chord_stream[].grid_beat adapted onto the grid beat index")


def test_03_adapter_legacy_layouts_and_fallback_error() -> None:
    legacy = {"chord_stream": [{"beat": 0, "root": 0}, {"beat": 1, "root": None}, {"beat": 2, "root": 5, "state": "ok", "quality": "min"}],
              "grid": {"phase": 3, "bar_convention": "stream beat = grid beat - phase"}, "tonic": 0, "mode": "minor"}
    stream, key, notes = BP.adapt_sibling_chords(legacy, GRID)
    assert [c["beat"] for c in stream] == [3, 4, 5] and notes["stream_beat_phase_added"] == 3 and key == {"tonic": 0, "mode": "minor"}
    assert stream[1]["state"] == "N" and stream[2]["root"] == 5
    plain = {"beats": [{"beat": 7, "root_pc": 19}]}  # no grid block -> no phase added
    stream, key, notes = BP.adapt_sibling_chords(plain, GRID)
    assert stream == [{"beat": 7, "root": 7, "quality": None, "state": "ok"}] and key is None and notes["stream_beat_phase_added"] == 0
    timed = {"stream": [{"time": 1.01, "root": 2}, {"time": 99.0, "root": 4}]}  # 99 s is beyond the fitted beats -> dropped
    stream, _k, notes = BP.adapt_sibling_chords(timed, GRID)
    assert stream == [{"beat": 2, "root": 2, "quality": None, "state": "ok"}] and notes["by_time"] == 1
    try:
        BP.adapt_sibling_chords({"chords": {"chord_counts": {}}}, GRID)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "chord_stream" in str(exc)
    print("test_03 PASS: legacy / time / malformed layouts handled")


def test_04_onset_ticks_bar_slot_to_grid_tick() -> None:
    rows = [[0, 0, 0.0, 0.0, -20.0], [0, 5, 0.0, 0.0, -20.0], [2, 15, 0.0, 0.0, -20.0]]
    ticks = BP.onset_ticks(rows, [40, None, 43], GRID)
    # beat = (bar + hoff) * 4 + slot // 4 + phase ; tick = beat * 480 + (slot % 4) * 120
    assert ticks == [(((0 + 1) * 4 + 0 + 2) * 480, 40), (((2 + 1) * 4 + 3 + 2) * 480 + 3 * 120, 43)] == [(6 * 480, 40), (17 * 480 + 360, 43)], ticks
    print("test_04 PASS: ticks on the grid beat index (phase + hypermeter offset applied), unpitched onsets dropped")


def test_05_cache_valid_rejects_stale_params() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x_bass.json"
        write_json_atomic(p, {"pyin": dict(BP.PITCH_PARAMS), "n_onsets": 3, "midi": [1, 2, 3]})
        assert BP.cache_valid(p, BP.PITCH_PARAMS, 3)["midi"] == [1, 2, 3]
        assert BP.cache_valid(p, BP.PITCH_PARAMS, 4) is None and BP.cache_valid(p, dict(BP.PITCH_PARAMS, frame_length=2048), 3) is None
        assert BP.cache_valid(Path(td) / "missing.json", BP.PITCH_PARAMS) is None
    print("test_05 PASS: stale pitch caches are recomputed")


def test_06_analyze_song_classes_on_synthetic_stream() -> None:
    stream = [{"beat": b, "root": 0 if b < 4 else 7, "quality": "maj", "state": "ok"} for b in range(8)]
    onsets = [(0 * 480, 36), (1 * 480, 43), (2 * 480, 40), (3 * 480, 50), (3 * 480 + 360, 42), (4 * 480, 43), (5 * 480, 50)]
    a = V5.analyze_song(onsets, stream, 0)
    cls = [e["cls"] for e in a["events"]]
    assert cls == ["root", "fifth", "third", "other", "approach", "root", "fifth"], cls  # pc 2 over C = other; 42 -> G = approach
    assert a["register"]["median"] == 43.0 and a["n_used"] == 7
    print(f"test_06 PASS: v5 classifier on the grid ticks -> {cls}")


def test_07_written_files_schema_and_coverage() -> None:
    if not (V5_FILE.exists() and V6_FILE.exists()):
        print("test_07 SKIP: bass_pitch files not built yet")
        return
    v5, v6 = json.loads(V5_FILE.read_text()), json.loads(V6_FILE.read_text())
    assert v5["class_order"] == list(V5.CLASS_ORDER) and set(v5["conditional"]) == {f"{s}|{c}" for s in range(4) for c in (0, 1)}
    for row in list(v5["conditional"].values()) + [v5["marginal"]]:
        assert abs(sum(row["probs"].values()) - 1.0) < 1e-6 and set(row["counts"]) == set(V5.CLASS_ORDER)
    reg = v5["register"]["corpus"]
    assert V5.GM_BASS_LO <= reg["iqr_lo"] <= reg["median"] <= reg["iqr_hi"] <= V5.GM_BASS_HI, reg
    assert v5["n_songs"] == len(v5["per_song"]) == v6["n_songs"] and v5["sampling_check"]["n"] == V5.N_CHECK
    srcs = {a["chord_source"] for a in v6["per_song"].values()}
    assert srcs <= {"chords_v6", "fallback_chroma_viterbi"} and set(v6["chord_sources"]) == srcs
    assert all(0 <= a["voiced_coverage"] <= 1 and a["n_used"] <= a["n_pitched"] <= a["n_bass_onsets"] for a in v6["per_song"].values())
    assert v5["marginal"]["n"] == v6["n_events"] > 0
    print(f"test_07 PASS: {v5['n_songs']} songs; marginal {v6['marginal_fractions']}; chord sources {{k: len(v) for k, v in v6['chord_sources'].items()}}")


if __name__ == "__main__":
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        fn()
    print("ALL PASS")
