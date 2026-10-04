#!/usr/bin/python3
"""v6 rules tests — audio form + comping: form_v6 recovers an ABAB block form and the 8-bar boundaries from synthetic bar
features (novelty at hypermetric 4-bar candidates), the form_plan_v5 model block (length, label Markov, R1, fill pool);
comping_v6 slot assignment / rejection on the shared grid, comping_v5 key sets, the pre-registered verdict; on-disk
outputs when present (form_plan_v5.json planner keys, comping_v5.json verdict enum + IOI histogram).

Run: /usr/bin/python3 -m pytest tests/test_v6_rules_form_comping.py -q      or      /usr/bin/python3 tests/test_v6_rules_form_comping.py
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
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np  # noqa: E402

from scripts.v5 import comping_v5 as C5  # noqa: E402
from scripts.v6.rules import comping_v6 as CP  # noqa: E402
from scripts.v6.rules import form_v6 as F  # noqa: E402

FOCUS = ("252eb21ce7df7328", "51e433ade2a845e1", "cdd2717e52820ff6")
PLANNER_KEYS = ("length_distribution", "start_distribution", "transition_probs", "R1", "intro_density_quantile", "boundary_fill_pool")
V5_FORM_KEYS = ("schema_version", "cycle", "agent", "run_id", "milestone", "env_pin_sha256", "prereg_path", "prereg_sha256", "chain_path", "chain_sha256", "eligible",
                "n_eligible", "excluded_disclosed", "params", "length_distribution", "n_songs_in_transition_corpus", "labels", "start_counts", "start_distribution",
                "transition_counts", "transition_probs", "repeat_A_probability", "density_tercile_bounds", "n_blocks_total", "per_label", "intro_density_quantile",
                "boundary_fill_pool", "n_boundary_bars", "fill_pool_fallback_used", "R1", "per_song")


def _skip(msg: str) -> None:
    try:
        import pytest
        pytest.skip(msg)
    except ImportError:
        print(f"SKIP: {msg}")


# ------------------------------------------------------------------------------------------------------- form ----
SECTION = {"A": {"chroma": (0, 4, 7), "mfcc": 1.0, "kick": 0x0101, "snare": 0x1010, "hat": 0x5555, "root": 0, "levels": (1.0, 0.8, 0.6, 0.0)},
           "B": {"chroma": (6, 10, 1), "mfcc": -1.0, "kick": 0x0901, "snare": 0x1010, "hat": 0xFFFF, "root": 5, "levels": (1.0, 0.9, 0.9, 0.9)},
           "C": {"chroma": (2, 5, 9), "mfcc": 0.0, "kick": 0x0001, "snare": 0x0000, "hat": 0x1111, "root": 2, "levels": (0.3, 0.7, 0.9, 0.2)}}


def synthetic_record(sha: str, form: str, phase: int = 1, hoff: int = 0, bars_per_section: int = 8) -> tuple:
    """A chords_v6-like record + beat MFCC / levels for `form` (one letter per section of bars_per_section bars)."""
    n_bars = hoff + bars_per_section * len(form)
    n_beats = phase + 4 * n_bars + 1
    chroma, mfcc, levels = np.zeros((n_beats, 12)), np.zeros((n_beats, 20)), np.zeros((n_beats, 4))
    masks = {k: [0] * n_bars for k in ("kick", "snare", "hat")}
    stream = []
    for b in range(n_bars):
        lab = form[max(0, (b - hoff) // bars_per_section)] if b >= hoff else "C"
        sec = SECTION[lab]
        for k in ("kick", "snare", "hat"):
            masks[k][b] = sec[k]
        for bt in range(4):
            gi = phase + 4 * b + bt
            for pc in sec["chroma"]:
                chroma[gi, pc] = 1.0
            chroma[gi, (sec["chroma"][0] + bt) % 12] += 0.1
            mfcc[gi, :] = sec["mfcc"] * np.linspace(1, 0.2, 20) + 0.05 * np.sin(gi)
            levels[gi, :] = sec["levels"]
            stream.append({"beat": gi - phase, "grid_beat": gi, "bar": b, "root": sec["root"], "quality": "maj", "sim": 0.9, "margin_root": 0.1, "rms_db": -20.0})
    rec = {"sha16": sha, "title": sha, "bpm": 120.0, "beat_chroma": chroma.tolist(), "drum_masks": masks,
           "key": {"tonic": 0, "tonic_name": "C", "mode": "major"},
           "grid": {"phase": phase, "hypermeter_offset": hoff, "n_bars_from_first_downbeat": n_bars, "n_beats": n_beats},
           "chords": {"chord_stream": stream}}
    return rec, mfcc, levels


def test_01_block_form_segments_and_boundaries() -> None:
    rec, mfcc, levels = synthetic_record("s1", "ABAB")
    r = F.analyse_record("s1", rec, mfcc, levels)
    assert r["form"] == "ABAB" and r["n_blocks"] == 4 and r["n_labels"] == 2 and r["has_literal_repeat"] and r["in_transition_corpus"]
    assert r["boundaries_form_bars"] == [8, 16, 24], (r["boundaries_form_bars"], r["novelty"])
    assert r["form_segments"] == "A:8 B:8 A:8 B:8" and r["boundaries_on_8bar_multiple"] == 3
    assert r["block_root"] == [0, 5, 0, 5] and r["block_density"][0] < r["block_density"][1]
    assert all(abs(x) <= 1.0 + 1e-9 for row in r["similarity"] for x in row) and r["similarity"][0][2] > 0.99 > r["similarity"][0][1]
    # hypermeter offset: lead-in bars are dropped from the form grid, boundaries stay on 4-bar multiples of the FORM grid
    rec2, m2, l2 = synthetic_record("s2", "AABC", phase=2, hoff=3)
    r2 = F.analyse_record("s2", rec2, m2, l2)
    assert r2["n_lead_bars"] == 3 and r2["n_form_bars"] == 32 and r2["form"] == "AABC"
    assert r2["boundaries_form_bars"] == [16, 24] and all(b % 4 == 0 for b in r2["boundaries_form_bars"]), r2["boundaries_form_bars"]
    assert r2["form_segments"] == "A:16 B:8 C:8"
    # novelty helpers on an explicit block-diagonal similarity
    S = np.ones((16, 16)) * 0.2
    S[:8, :8] = S[8:, 8:] = 1.0
    nov = F.novelty_curve(S)
    assert [b for b, _v in nov] == [4, 8, 12] and F.pick_boundaries(nov) == [8]
    assert F.pick_boundaries(nov, thr=10.0) == []
    print(f"test_01 PASS: ABAB blocks + boundaries {r['boundaries_form_bars']}; offset grid -> {r2['form_segments']}")


def test_02_corpus_model_keys_r1_and_fill_pool() -> None:
    per_song = {}
    for sha, form in (("252eb21ce7df7328", "ABABCAAB"), ("51e433ade2a845e1", "AABBCCAA"), ("cdd2717e52820ff6", "ABCABC"), ("other1", "AAAA"), ("short1", "AB")):
        rec, m, l = synthetic_record(sha, form)
        per_song[sha] = F.analyse_record(sha, rec, m, l)
    eligible = list(per_song)
    model = F.corpus_model(per_song, eligible, FOCUS)
    assert set(PLANNER_KEYS) <= set(model)
    assert model["length_distribution"] == {"4": 2, "6": 1, "8": 2}  # round(bars/8) clipped to [4, 8]
    assert model["n_songs_in_transition_corpus"] == 4 and model["labels"] == ["A", "B", "C"]
    assert abs(sum(model["start_distribution"].values()) - 1.0) < 1e-9
    for a, row in model["transition_probs"].items():
        assert abs(sum(row.values()) - 1.0) < 1e-9, (a, row)
    assert model["R1"]["pass"] and model["R1"]["fallback_template"] is None and set(model["R1"]["focus_songs"]) == set(FOCUS)
    assert model["boundary_fill_pool"] and all({"snare", "hat", "count"} <= set(e) for e in model["boundary_fill_pool"]) and not model["fill_pool_fallback_used"]
    assert 0.0 <= model["intro_density_quantile"] <= 1.0 and len(model["density_tercile_bounds"]) == 2
    assert model["per_label"]["A"]["harmony_region"] == 0 and model["per_label"]["B"]["harmony_region"] == 5
    # R1 fails when a focus song has no literal repeat -> fallback template recorded
    per_song["cdd2717e52820ff6"] = F.analyse_record("x", *synthetic_record("x", "ABC"))
    m2 = F.corpus_model(per_song, eligible, FOCUS)
    assert not m2["R1"]["pass"] and m2["R1"]["fallback_template"] == ["A", "A", "B", "A", "B", "C", "A", "A"]
    print(f"test_02 PASS: planner keys present; lengths {model['length_distribution']}; R1 pass/fail logic; fill pool {len(model['boundary_fill_pool'])}")


# ---------------------------------------------------------------------------------------------------- comping ----
def test_03_slot_assignment_rejection_and_stem_stats() -> None:
    beats = np.arange(0.0, 40.0, 0.5)  # 120 BPM grid, 80 beats, phase 0
    s16 = 0.125
    times = np.array([8.0, 8.0 + 3 * s16, 8.0 + 6 * s16, 8.0 + 6.5 * s16, 9.0 + 5 * s16, 8.0 + 3 * s16 + 0.004, 100.0])
    placed = CP.assign_slots(times, beats, phase=0)
    cells = sorted({(b, s) for b, s, _d in placed})
    assert cells == [(4, 0), (4, 3), (4, 6), (4, 13)], placed  # 6.5 slots -> |dev| 0.5 rejected; out-of-grid dropped; 4 ms dup -> same cell
    assert len(placed) == 5
    st = CP.analyse_stem(placed, n_bars=10)
    v5_keys = set(C5.analyse_stem([], 120.0))
    assert v5_keys <= set(st), sorted(v5_keys - set(st))
    assert st["n_onset_groups"] == 4 and st["n_duplicate_cells"] == 1 and st["n_bars_with_onsets"] == 1 and st["bars"] == [4]
    assert st["slot_counts"][0] == st["slot_counts"][3] == st["slot_counts"][6] == st["slot_counts"][13] == 1
    assert st["ioi_counts"][2] == 2 and st["ioi_counts"][6] == 1  # IOIs 3, 3, 7
    assert st["bar_masks"][4] == (1 | 1 << 3 | 1 << 6 | 1 << 13) and st["onsets_per_bar"] == 4.0 and st["chord_size_mean"] is None
    # phase: onsets before the first downbeat are dropped, bars count from it
    placed2 = CP.assign_slots(np.array([0.5, 1.0, 3.0]), beats, phase=2)
    assert [(b, s) for b, s, _d in placed2] == [(0, 0), (1, 0)]
    print("test_03 PASS: slot assignment / rejection / dedup on the shared grid; comping_v5 stem keys present")


def _song(sha: str, n_bars: int, slots: tuple) -> dict:
    placed = [(b, s, 0.0) for b in range(n_bars) for s in slots]
    st = CP.analyse_stem(placed, n_bars)
    return {"sha16": sha, "title": sha, "band": 5, "per_stem": {"other": st}, "n_bars_with_onsets_pooled": st["n_bars_with_onsets"]}


def test_04_pool_and_verdict_rule() -> None:
    songs = {f"s{i:02d}": _song(f"s{i:02d}", 20, (0, 4, 8, 12) if i % 2 else (0, 6, 10)) for i in range(9)}
    pooled = CP.pool(songs, ("other",))
    v5_keys = set(C5.pool({}, ("other",)))
    assert v5_keys <= set(pooled), sorted(v5_keys - set(pooled))
    assert pooled["n_songs"] == 9 and pooled["n_bars"] == 180 and abs(sum(pooled["slot16_histogram"]) - 1.0) < 1e-6
    assert pooled["slot16_argmax"] == 0 and pooled["slot16_max_mass"] < 0.5 and pooled["bar_mask_counts_top"][0]["count"] in (80, 100)
    v = CP.verdict_of(songs, pooled)
    assert v["enum"] == "COMPING_NON_DEGENERATE" and v["n_songs_with_ge_16_pooled_bars"] == 9 and v["thresholds"] == C5.THRESHOLDS
    few = {k: songs[k] for k in sorted(songs)[:7]}
    assert CP.verdict_of(few, CP.pool(few, ("other",)))["enum"] == "COMPING_DEGENERATE"
    flat = {f"f{i}": _song(f"f{i}", 20, (0,)) for i in range(9)}
    assert CP.verdict_of(flat, CP.pool(flat, ("other",)))["enum"] == "COMPING_DEGENERATE"
    prereg = json.loads(Path("data/v5/rules/comping_prereg_c87.json").read_text()) if Path("data/v5/rules/comping_prereg_c87.json").exists() else None
    if prereg:
        assert prereg["thresholds"] == C5.THRESHOLDS and sorted(prereg["enum"]) == sorted(C5.ENUM)
    print(f"test_04 PASS: pooled keys superset of comping_v5; verdict rule (9 songs ok / 7 songs degenerate / one-slot degenerate)")


# ---------------------------------------------------------------------------------------------------- on-disk ----
def test_05_on_disk_form_plan_and_form_v6() -> None:
    fp, f6 = Path("data/v5/rules/form_plan_v5.json"), Path("data/v6/rules/form_v6.json")
    if not (fp.exists() and f6.exists()):
        return _skip("form outputs not built yet")
    d = json.loads(fp.read_text())
    assert set(V5_FORM_KEYS) <= set(d), sorted(set(V5_FORM_KEYS) - set(d))
    assert d["params"]["similarity_threshold"] == 0.85 and d["params"]["bars_per_block"] == 8
    assert all(k in ("4", "5", "6", "7", "8") for k in d["length_distribution"]) and sum(d["length_distribution"].values()) == d["n_eligible"]
    for a, row in d["transition_probs"].items():
        assert abs(sum(row.values()) - 1.0) < 1e-6, a
    assert d["boundary_fill_pool"] and all(0 <= e["snare"] < 1 << 16 and 0 <= e["hat"] < 1 << 16 for e in d["boundary_fill_pool"])
    for s, p in d["per_song"].items():
        assert set(p["form"]) <= set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") and len(p["form"]) == p["n_blocks"] and len(p["block_density"]) == p["n_blocks"]
    v6 = json.loads(f6.read_text())
    assert set(v6["per_song"]) == set(d["per_song"]) and v6["summary"]["form_strings"]
    for s, p in v6["per_song"].items():
        assert all(g["n_bars"] % 4 == 0 or g is p["segments"][-1] for g in p["segments"]), s
        assert sum(g["n_bars"] for g in p["segments"]) == p["n_form_bars"], s
        assert all(b % 4 == 0 for b in p["boundaries_form_bars"]), s
    present = [f for f in FOCUS if f in d["per_song"]]
    print(f"test_05 PASS: form_plan_v5 keys; R1 pass={d['R1']['pass']}; focus forms " + ", ".join(f"{f[:6]}={d['per_song'][f]['form']}" for f in present))


def test_06_on_disk_comping() -> None:
    p5, p6 = Path("data/v5/rules/comping_v5.json"), Path("data/v6/rules/comping_v6.json")
    if not (p5.exists() and p6.exists()):
        return _skip("comping outputs not built yet")
    d = json.loads(p5.read_text())
    assert d["verdict"]["enum"] in C5.ENUM and d["verdict"]["thresholds"] == C5.THRESHOLDS
    pooled = d["stats"]["pooled"]
    assert abs(sum(pooled["ioi16_histogram"]) - 1.0) < 1e-6 and len(pooled["ioi16_histogram"]) == 16 and abs(sum(pooled["slot16_histogram"]) - 1.0) < 1e-6
    assert pooled["n_songs"] == len(d["per_song"]) >= 8 and d["stems"] == ["other"] and "bars" not in d["per_song"][next(iter(d["per_song"]))]["per_stem"]["other"]
    assert d["verdict"]["n_songs_with_ge_16_pooled_bars"] == sum(1 for r in d["per_song"].values() if r["n_bars_with_onsets_pooled"] >= 16)
    d6 = json.loads(p6.read_text())
    assert d6["verdict"] == d["verdict"] and all("bar_masks" in r["per_stem"]["other"] for r in d6["per_song"].values())
    print(f"test_06 PASS: comping verdict {d['verdict']['enum']} over {pooled['n_songs']} songs; max slot mass {pooled['slot16_max_mass']} at slot {pooled['slot16_argmax']}")


if __name__ == "__main__":
    fails = 0
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"{fn.__name__} FAIL: {type(exc).__name__}: {exc}")
    sys.exit(1 if fails else 0)
