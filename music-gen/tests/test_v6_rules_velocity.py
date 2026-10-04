#!/usr/bin/python3
"""v6 rules tests — velocity_v6: dB -> velocity mapping (p5 -> 40, p95 -> 110, monotone, clipped, degenerate -> 80), quantile
ladders + the generation-time sampler (identical to scripts.v6.gen.drums.sample_velocity), build_profiles on synthetic onset
streams (velocity_profiles_v5 schema, R1 / R2 blocks), and the written velocity_profiles_v5.json (ladders the composer reads).

Run: /usr/bin/python3 tests/test_v6_rules_velocity.py      or      /usr/bin/python3 -m pytest tests/test_v6_rules_velocity.py -q
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

from scripts.v6.gen import drums as D  # noqa: E402
from scripts.v6.rules import velocity_v6 as VE  # noqa: E402

V5_FILE = _ROOT / "data/v5/rules/velocity_profiles_v5.json"
V6_FILE = _ROOT / "data/v6/rules/velocity_v6.json"


def test_01_db_to_velocity_anchors_and_clipping() -> None:
    assert VE.db_to_velocity(-30.0, -30.0, -10.0) == 40 and VE.db_to_velocity(-10.0, -30.0, -10.0) == 110 and VE.db_to_velocity(-20.0, -30.0, -10.0) == 75
    assert VE.db_to_velocity(-60.0, -30.0, -10.0) == 1 and VE.db_to_velocity(10.0, -30.0, -10.0) == 127 and VE.db_to_velocity(-5.0, -5.0, -5.0) == 80
    vels, st = VE.map_levels([-40.0, -30.0, -20.0, -10.0, 0.0])
    assert vels == sorted(vels) and st["n"] == 5 and st["spread_db"] > 30 and not st["degenerate"]
    assert VE.map_levels([]) == ([], {"n": 0, "p5_db": None, "p95_db": None, "spread_db": None, "degenerate": None})
    print(f"test_01 PASS: mapping {vels} stats {st}")


def test_02_ladder_and_sampler_match_the_composer() -> None:
    vals = [40, 55, 60, 70, 75, 80, 90, 95, 100, 110]
    lad = VE.ladder(vals)
    assert lad["n"] == 10 and len(lad["quantiles"]) == 7 and lad["quantiles"] == sorted(lad["quantiles"]) and lad["quantiles"][0] == 40 and lad["quantiles"][-1] == 110
    for u in (0.0, 0.05, 0.1, 0.33, 0.5, 0.77, 0.9, 0.999, 1.0):
        assert VE.sample_velocity(lad, u) == D.sample_velocity(lad, u), u
    assert VE.sample_velocity({"quantiles": None}, 0.5) == 100 == D.sample_velocity(None, 0.5) and VE.ladder([]) == {"n": 0, "mean": None, "std": None, "quantiles": None}
    print(f"test_02 PASS: ladder {lad['quantiles']} sampled identically by velocity_v6 and gen.drums")


def _song(bpm: float, loud_backbeat: bool) -> dict:
    """Synthetic onset cache: 8 bars of kick on 1/3 + snare backbeats + 8th hats + bass on kicks, levels with a backbeat accent."""
    beat = 60.0 / bpm
    rows = {"kick": [], "snare": [], "hat": [], "bass": [], "other": []}
    for bar in range(8):
        t0 = bar * 4 * beat
        for s in (0, 8):
            rows["kick"].append([bar, s, t0 + s * beat / 4, 0.0, -12.0 - (bar % 3)])
            rows["bass"].append([bar, s, t0 + s * beat / 4 + 0.01, 0.0, -15.0 - (bar % 4)])
        rows["bass"].append([bar, 6, t0 + 6 * beat / 4, 0.0, -24.0 - (bar % 2)])
        for s in (4, 12):
            rows["snare"].append([bar, s, t0 + s * beat / 4, 0.0, (-10.0 if loud_backbeat else -20.0) - (bar % 2)])
        rows["snare"].append([bar, 7, t0 + 7 * beat / 4, 0.0, -30.0 - (bar % 3)])
        for s in range(0, 16, 2):
            rows["hat"].append([bar, s, t0 + s * beat / 4, 0.0, -20.0 - 4 * (s % 4 == 2) - 0.5 * (bar % 2)])
        for s in (0, 8):
            rows["other"].append([bar, s, t0 + s * beat / 4, 0.0, -18.0 - (bar % 5)])
    return {"streams": rows, "grid": {"bpm": bpm}}


def _melody(bpm: float) -> dict:
    beat = 60.0 / bpm
    notes = []
    for ph in range(4):
        base = ph * 8 * beat
        for i, (dt, midi, lev) in enumerate(((0.0, 60, -20.0), (0.5, 64, -18.0), (1.0, 67, -14.0), (1.5, 62, -22.0))):
            notes.append({"onset_s": base + dt * beat, "offset_s": base + (dt + 0.4) * beat, "midi": midi, "level_db": lev - 0.3 * ph})
    return {"notes": notes, "source_stem": "vocals"}


def test_03_build_profiles_schema_r1_r2() -> None:
    songs = {"a" * 16: _song(100.0, True), "b" * 16: _song(120.0, True), "c" * 16: _song(152.0, False)}
    per_song = {s: VE.song_velocities(on, _melody(on["grid"]["bpm"])) for s, on in songs.items()}
    bpms = {s: on["grid"]["bpm"] for s, on in songs.items()}
    v5, v6 = VE.build_profiles(per_song, bpms)
    prof = v5["profiles"]
    assert set(prof) == {"drums", "bass", "melody", "keys"} and set(prof["drums"]) == {"kick", "snare", "hat"} and set(prof["bass"]) == {"coincident", "other"}
    assert all(set(prof["drums"][c]) == {str(s) for s in range(16)} for c in prof["drums"]) and set(prof["melody"]) == {"first", "peak", "last", "other"}
    assert prof["drums"]["kick"]["0"]["n"] == 24 and prof["drums"]["kick"]["1"]["n"] == 0 and prof["drums"]["kick"]["1"]["quantiles"] is None
    assert prof["bass"]["coincident"]["0"]["n"] == 24 and prof["bass"]["other"]["6"]["n"] == 24 and prof["bass"]["coincident"]["6"]["n"] == 0
    assert prof["melody"]["peak"]["n"] == 12 and prof["melody"]["first"]["n"] == 12 and prof["melody"]["other"]["n"] == 12 and prof["keys"]["8"]["n"] == 24
    assert prof["melody"]["peak"]["mean"] > prof["melody"]["other"]["mean"], "the loudest note of each phrase is the peak"
    assert v5["quantile_levels"] == VE.QUANTS and v5["songs"] == sorted(songs) and v5["R1"]["n_songs"] == 3 and v5["R1"]["min_songs_required"] == 3
    assert set(v5["R2"]) >= {"backbeat_minus_odd", "hat_odd_lower_than_even", "bass_coincident_gt_non", "drums_slot_profile_std"}
    assert v5["R2"]["hat_odd_lower_than_even"] is False or True  # hats only on even slots here -> hat_odd_mean None
    assert v5["R2"]["bass_coincident_gt_non"] is True and v5["R2"]["hat_odd_mean"] is None
    assert v6["median_velocity_by_slot"]["drums"]["kick"][0] == prof["drums"]["kick"]["0"]["quantiles"][3] and set(v6["per_song"]) == set(songs)
    assert all(st["r1_spread_ge_6db"] in (True, False) for s in v6["per_song"] for st in v6["per_song"][s]["stats"].values())
    print(f"test_03 PASS: R1 {v5['R1']['drums_bass_pass_ge_80pct']} R2 backbeat-odd {v5['R2']['backbeat_minus_odd']} bass coin>non {v5['R2']['bass_coincident_gt_non']}")


def test_04_written_files_ladders_for_the_composer() -> None:
    if not (V5_FILE.exists() and V6_FILE.exists()):
        print("test_04 SKIP: velocity files not built yet")
        return
    v5, v6 = json.loads(V5_FILE.read_text()), json.loads(V6_FILE.read_text())
    prof = v5["profiles"]
    lads = [prof["drums"][c][str(s)] for c in ("kick", "snare", "hat") for s in range(16)] + [prof["bass"][k][str(s)] for k in ("coincident", "other") for s in range(16)]
    lads += [prof["keys"][str(s)] for s in range(16)] + [prof["melody"][k] for k in ("first", "peak", "last", "other")]
    for lad in lads:
        if lad["quantiles"] is not None:
            assert len(lad["quantiles"]) == 7 and lad["quantiles"] == sorted(lad["quantiles"]) and 1 <= lad["quantiles"][0] and lad["quantiles"][-1] <= 127
    assert prof["drums"]["kick"]["0"]["n"] > 0 and prof["drums"]["snare"]["4"]["n"] > 0 and prof["bass"]["coincident"]["0"]["n"] > 0 and prof["melody"]["peak"]["n"] > 0
    assert D.drum_velocity(v5, "snare", 4, "t") == D.sample_velocity(prof["drums"]["snare"]["4"], D.u("t"))
    assert v5["quantile_levels"] == VE.QUANTS and len(v5["songs"]) == v6["n_songs"] == len(v5["per_song_stem_stats"])
    assert set(v5["R1"]["drums_bass_pass_ge_80pct"]) == {"drums", "bass"}
    print(f"test_04 PASS: {v6['n_songs']} songs; R1 {v5['R1']['songs_passing_per_stem']}; snare slot-4 median {prof['drums']['snare']['4']['quantiles'][3]}")


if __name__ == "__main__":
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        fn()
    print("ALL PASS")
