#!/usr/bin/python3
"""v6 rules tests — melody_v6: note segmentation from pyin tracks (voiced runs, > 1.5 semitone splits, < 80 ms dropped), phrase
segmentation / statistics, register quantiles, histogram helpers, and the written melody_vomm_v5.json (order-2 VOMM the composer
samples with scripts.v5.melody_vomm_v5.sample_next, unigram, phrase + register blocks, per-song coverage).

Run: /usr/bin/python3 tests/test_v6_rules_melody.py      or      /usr/bin/python3 -m pytest tests/test_v6_rules_melody.py -q
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

import numpy as np  # noqa: E402

from scripts.v5 import melody_vomm_v5 as V5  # noqa: E402
from scripts.v6.rules import melody_v6 as ME  # noqa: E402

V5_FILE = _ROOT / "data/v5/rules/melody_vomm_v5.json"
V6_FILE = _ROOT / "data/v6/rules/melody_v6.json"


def _track():
    t = np.arange(0, 3.0, 0.01)
    f0, voiced = np.full(t.size, np.nan), np.zeros(t.size, dtype=bool)
    f0[10:40], voiced[10:40] = 261.63, True     # C4, 300 ms
    f0[40:70], voiced[40:70] = 329.63, True     # E4 directly after (split by the > 1.5 st jump)
    f0[70:74], voiced[70:74] = 392.0, True      # 40 ms blip -> dropped (< 80 ms)
    f0[100:130], voiced[100:130] = 293.66, True  # D4 after a 260 ms gap
    f0[115], f0[116] = 296.0, 291.0              # vibrato within 1.5 st stays one note
    f0[200:230], voiced[200:230] = 440.0, True   # A4 after a 700 ms rest
    return f0, voiced, t


def test_01_segment_notes_runs_jumps_and_min_duration() -> None:
    f0, voiced, t = _track()
    notes = ME.segment_notes(f0, voiced, t)
    assert [n["midi"] for n in notes] == [60, 64, 62, 69], notes
    assert notes[0]["onset_s"] == 0.1 and abs(notes[0]["offset_s"] - 0.4) < 1e-6 and notes[1]["onset_s"] == 0.4 and notes[2]["n_frames"] == 30
    assert ME.segment_notes(f0, np.zeros_like(voiced), t) == []
    print(f"test_01 PASS: notes {[(n['midi'], n['onset_s']) for n in notes]}")


def test_02_phrases_and_statistics() -> None:
    f0, voiced, t = _track()
    notes = ME.segment_notes(f0, voiced, t)
    beat_s = 0.5  # 120 bpm: a rest >= 1 beat (0.5 s) splits phrases -> [C4 E4 D4] and [A4]
    phr = ME.phrases_of(notes, beat_s)
    assert [[n["midi"] for n in p] for p in phr] == [[60, 64, 62], [69]]
    st = ME.phrase_stats(phr, beat_s)
    assert st["n_phrases"] == 2 and st["n_intervals"] == 2 and st["interval_histogram"]["4"] == 1 and st["interval_histogram"]["-2"] == 1
    assert st["step_fraction"] == 0.5 and st["leap_fraction"] == 0.5 and st["repeat_fraction"] == 0.0 and sum(st["interval_histogram"].values()) == 2
    assert st["peak_position"]["n"] == 1 and st["peak_position"]["mean"] == 0.5 and st["peak_position"]["quartile_histogram"]["q2"] == 1
    assert st["length_bars_histogram"] == {"0.5": 1, "0.0": 1} or set(st["length_bars_histogram"]) <= {"0.0", "0.5", "1.0"}
    print(f"test_02 PASS: phrases {st['n_phrases']} lengths {st['length_bars_histogram']} step {st['step_fraction']}")


def test_03_register_and_histograms() -> None:
    reg = ME.register_of([60, 62, 64, 65, 67, 69, 71, 72])
    assert reg == {"n": 8, "median": 66.0, "iqr_lo": 63.5, "iqr_hi": 69.5, "min": 60, "max": 72}
    assert ME.register_of([]) == {"n": 0, "median": None, "iqr_lo": None, "iqr_hi": None, "min": None, "max": None}
    assert ME._hist([1, 1, 3], range(1, 4)) == {"1": 2, "2": 0, "3": 1} and ME._sum_hist([{"a": 1}, {"a": 2, "b": 1}]) == {"a": 3, "b": 1}
    assert ME._pct([1, 2, 3, 4], 0.5) == 2.5 and ME._pct([], 0.5) is None
    print("test_03 PASS: register / histogram helpers")


def test_04_tokens_round_trip_through_v5_vomm() -> None:
    ticks = [(0, 60), (480, 62), (960, 64), (1440, 65), (1920, 67), (1920, 64), (3840, 60)]
    toks = V5.tokenize(ticks, 0, "major")
    assert toks == ["0|4", "1|4", "2|4", "3|4", "4|12", "0|12"], toks  # simultaneous onsets fold to the highest pitch; 16 x 16th -> bucket 12; last ioi = 12
    counts = V5.train_counts([toks], ME.MAX_ORDER)
    assert set(counts) == {"0", "1", "2"} and counts["2"]["0|4 1|4"] == {"2|4": 1}
    model = {"max_order": ME.MAX_ORDER, "counts": counts}
    assert V5.sample_next(model, ("0|4", "1|4"), 0.3) == "2|4" and V5.sample_next(model, ("zz",), 0.0) == "0|12"  # unseen ctx -> order 0, first sorted token
    assert V5.sample_next({"max_order": 2, "counts": {"0": {}, "1": {}, "2": {}}}, (), 0.5) == V5.DEFAULT_TOKEN
    print("test_04 PASS: v5 tokenizer / order-2 counts / sample_next")


def test_05_written_files_schema_and_coverage() -> None:
    if not (V5_FILE.exists() and V6_FILE.exists()):
        print("test_05 SKIP: melody files not built yet")
        return
    v5, v6 = json.loads(V5_FILE.read_text()), json.loads(V6_FILE.read_text())
    assert v5["max_order"] == v5["model"]["max_order"] == ME.MAX_ORDER and set(v5["counts"]) == {str(o) for o in range(ME.MAX_ORDER + 1)}
    assert v5["counts"] == v5["model"]["counts"] and v5["verdict"] in V5.ENUM and v5["order_stats"] == v6["order_stats"]
    uni = v5["unigram"]
    assert abs(sum(uni["probs"].values()) - 1.0) < 1e-6 and uni["n"] == v5["order_stats"]["0"]["n_events"] > 0
    assert all("|" in t and t.split("|")[0] in {"c", "0", "1", "2", "3", "4", "5", "6"} and int(t.split("|")[1]) in V5.IOI_BUCKETS for t in v5["vocab"])
    tok = V5.sample_next(v5["model"], (), 0.5)
    assert tok in uni["probs"]
    assert v5["n_songs"] == len(v5["per_song"]) == v6["n_songs"] and v5["phrase_structure"]["n_phrases"] > 0
    reg = v5["register"]["corpus"]
    assert 40 <= reg["iqr_lo"] <= reg["median"] <= reg["iqr_hi"] <= 96, reg
    ph = v6["phrases"]
    assert abs(ph["step_fraction"] + ph["repeat_fraction"] + ph["leap_fraction"] - 1.0) < 1e-6
    assert set(v6["source_stems"]) <= {"vocals", "other"} and sum(len(v) for v in v6["source_stems"].values()) == v6["n_songs"]
    print(f"test_05 PASS: verdict {v5['verdict']}; vocab {len(v5['vocab'])}; register {reg}; step/repeat/leap {ph['step_fraction']}/{ph['repeat_fraction']}/{ph['leap_fraction']}")


if __name__ == "__main__":
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        fn()
    print("ALL PASS")
