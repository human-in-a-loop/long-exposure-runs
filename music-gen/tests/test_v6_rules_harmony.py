#!/usr/bin/python3
"""v6 rules tests — audio harmony: chords_v6 recovers a synthetic triad progression + key on the shared grid (grid view for the
sibling scripts), key_v6 (global key, 8-bar track / modulation flag, chord-fit cross-check), harmony_rules_v6 (functional
transposition, segments, harmony_v5 per-song schema, add-alpha LOO cross-entropy), on-disk outputs when present (29 chord
files, chain in the harmony_v5 schema, per-song files, LOO below uniform), composer loads the real files, discipline.

Run: /usr/bin/python3 -m pytest tests/test_v6_rules_harmony.py -q      or      /usr/bin/python3 tests/test_v6_rules_harmony.py
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np  # noqa: E402

from scripts.v5.harmony_v5 import KK_MAJOR, QUALITY_ORDER, markov  # noqa: E402
from scripts.v6 import microtiming_v6 as MT  # noqa: E402
from scripts.v6.rules import chords_v6 as C  # noqa: E402
from scripts.v6.rules import harmony_rules_v6 as H  # noqa: E402
from scripts.v6.rules import key_v6 as K  # noqa: E402

PY = "/usr/bin/python3"
SR = MT.SR
FOCUS = ("252eb21ce7df7328", "51e433ade2a845e1", "cdd2717e52820ff6")
CHORDS_DIR = Path("data/v6/rules/chords")
CHAIN = Path("data/v5/rules/harmony_markov_v5_full.json")
PER_SONG = Path("data/v5/rules/per_song_c84")
V5_PER_SONG_KEYS = ("schema_version", "cycle", "sha16", "title", "bpm_v5", "midi_dir", "env_pin_sha256", "stems", "per_stem", "velocity_values_seen",
                    "velocity_uniform", "weighting", "key", "n_beats", "n_segments", "exclusion_rule", "chord_stream", "segments")
V5_CHAIN_KEYS = ("states", "beat_level_counts", "beat_level_row_normalized", "segment_level_counts", "stationary_distribution", "max_stationary_state",
                 "max_stationary_mass", "segment_counts_by_quality", "qualities_with_count_ge_threshold", "degeneracy_thresholds", "degeneracy_verdict",
                 "chain_definition", "schema_version", "cycle", "env_pin_sha256", "gate", "per_song", "qualities", "notes")
_CACHE: dict = {}


def _skip(msg: str) -> None:
    try:
        import pytest
        pytest.skip(msg)
    except ImportError:  # plain-script mode
        print(f"SKIP: {msg}")


# ------------------------------------------------------------------------------------------------- synthetic song ----
def _burst(y: np.ndarray, t: float, sig: np.ndarray) -> None:
    s = int(round(t * SR))
    n = min(sig.size, y.size - s)
    if n > 0:
        y[s:s + n] += sig[:n]


def _tone(midi: int, dur_s: float, amp: float) -> np.ndarray:
    tt = np.arange(int(dur_s * SR)) / SR
    f = 440.0 * 2 ** ((midi - 69) / 12.0)
    env = np.minimum(1.0, tt / 0.01) * np.exp(-tt * 1.5)
    return (amp * env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt))).astype(np.float32)


PROGRESSION = [(0, "maj"), (9, "min"), (5, "maj"), (7, "maj")]  # C, Am, F, G — two bars each


def synthetic_song(bpm: float = 120.0, n_bars: int = 24) -> tuple:
    s16 = 60.0 / bpm / 4
    L = int((n_bars * 16 + 8) * s16 * SR)
    drums, harm = np.zeros(L, np.float32), np.zeros(L, np.float32)
    kick, snare, hat = MT._hit("kick"), MT._hit("snare"), MT._hit("hat")
    truth = []
    for bar in range(n_bars):
        root, q = PROGRESSION[(bar // 2) % 4]
        truth.append(root)
        for slot in range(16):
            t = (bar * 16 + slot) * s16 + 0.5
            if slot in (0, 8):
                _burst(drums, t, kick)
            if slot in (4, 12):
                _burst(drums, t, snare)
            if slot % 2 == 0:
                _burst(drums, t, hat)
        t0 = bar * 16 * s16 + 0.5
        for iv in C.QUALITIES[q]:
            _burst(harm, t0, _tone(60 + root + iv, 4 * 60.0 / bpm, 0.25))
            _burst(harm, t0 + 2 * 60.0 / bpm, _tone(60 + root + iv, 2 * 60.0 / bpm, 0.2))
        _burst(harm, t0, _tone(36 + root, 4 * 60.0 / bpm, 0.3))
    return drums, harm, truth


def _analysis() -> dict:
    if "a" not in _CACHE:
        drums, harm, truth = synthetic_song()
        _CACHE["a"] = (C.analyse_arrays(drums, harm, 120.0, "synthetic"), truth)
    return _CACHE["a"]


def test_01_chords_recover_synthetic_progression_and_key() -> None:
    out, truth = _analysis()
    g, st = out["grid"], out["chords"]["chord_stream"]
    assert abs(g["fit"]["tempo_ratio"] - 1.0) < 0.01 and g["fit"]["beat_hit_frac"] > 0.9, g["fit"]
    by_bar: dict = {}
    for e in st:
        if e["root"] is not None:
            by_bar.setdefault(e["bar"], []).append(e["root"])
    hits = [max(set(r), key=r.count) == truth[b] for b, r in by_bar.items() if b < len(truth)]
    acc = sum(hits) / len(hits)
    assert acc >= 0.8, (acc, {b: max(set(r), key=r.count) for b, r in by_bar.items()}, truth)
    assert out["chords"]["n_fraction"] < 0.15, out["chords"]["n_fraction"]
    assert out["key"]["tonic"] == 0 and out["key"]["mode"] == "major", out["key"]
    assert out["key"]["chord_fit"]["agrees_with_ks"] and not out["key"]["low_confidence"]
    assert out["chords"]["harmonic_rhythm"]["planner_classes_124"]["1"] >= 0.6 * out["chords"]["harmonic_rhythm"]["n_bars"]
    print(f"test_01 PASS: bar-root accuracy {acc:.2f}, key {out['key']['tonic_name']} {out['key']['mode']} conf {out['key']['confidence']:.3f}, N {out['chords']['n_fraction']:.3f}")


def test_02_grid_view_and_stream_conventions() -> None:
    out, _truth = _analysis()
    g, view, st = out["grid"], out["chord_stream"], out["chords"]["chord_stream"]
    assert len(view) == g["n_beats"] and [e["beat"] for e in view] == list(range(g["n_beats"]))
    assert {e["state"] for e in view} <= {"ok", "N"} and all((e["root"] is None) == (e["state"] == "N") for e in view)
    assert [e["grid_beat"] for e in st] == list(range(g["phase"], g["n_beats"])) and all(e["beat"] == e["grid_beat"] - g["phase"] for e in st)
    assert all(e["bar"] == e["beat"] // 4 for e in st)
    assert all(view[e["grid_beat"]]["chord"] == e["chord"] for e in st), "grid view disagrees with the analysis stream"
    assert C.TEMPLATES.shape == (85, 12) and np.allclose(np.linalg.norm(C.TEMPLATES, axis=1), 1.0)
    assert out["chords"]["vocabulary"][-1] == "N" and len(out["chords"]["vocabulary"]) == 12 * len(QUALITY_ORDER) + 1
    # silence rule: a silent stretch is forced to N, Viterbi ties resolve to the lowest state index
    sims = np.zeros((6, 85))
    sims[:, 3] = 1.0
    path = C.viterbi(sims / C.TAU)
    assert list(path) == [3] * 6
    rec = C.recognise(np.ones((8, 12)) * 0.1, np.array([-10.0] * 4 + [-90.0] * 4))
    assert all(rec["path"][4:] == C.N_INDEX) and all(rec["silent"][4:]) and not any(rec["silent"][:4])
    print("test_02 PASS: grid view covers every grid beat; stream beat = grid beat - phase; silence -> N")


# ------------------------------------------------------------------------------------------------------------ key ----
def test_03_key_global_track_and_chord_fit() -> None:
    prof = np.roll(np.asarray(KK_MAJOR), 7)
    chroma = np.tile(prof, (64, 1))
    k = K.global_key(chroma)
    assert (k["tonic"], k["mode"]) == (7, "major") and k["confidence"] > 0 and k["runner_up"]["tonic"] != 7
    mod = np.vstack([np.tile(np.roll(np.asarray(KK_MAJOR), 0), (64, 1)), np.tile(prof, (64, 1))])
    tr = K.key_track(mod, 0, 0)
    assert tr["n_windows"] >= 8 and tr["modulation_flag"] and tr["modulation_spans"][-1]["tonic"] == 7, tr
    assert not K.key_track(chroma, 0, 7)["modulation_flag"]
    stream = [{"root": r, "quality": q} for r, q in [(0, "maj"), (5, "maj"), (7, "7"), (9, "min")] * 8] + [{"root": None, "quality": "N"}]
    fit = K.chord_fit_key(stream, 0, "major")
    assert fit["agrees_with_ks"] and fit["fit"] == 1.0 and fit["n_sounding_beats"] == 32
    fit2 = K.chord_fit_key(stream, 9, "minor")  # relative minor of the detected chords
    assert fit2["relative_of_ks"] and fit2["tonic"] == 0 and fit2["mode"] == "major"
    print("test_03 PASS: KK key G major; modulation flagged on a C->G switch; chord-fit cross-check + relative-key flag")


# ------------------------------------------------------------------------------------------------- harmony rules ----
def _fake_rec(sha: str, tonic: int, roots: list, quality: str = "maj") -> dict:
    st = [{"beat": i, "grid_beat": i + 1, "bar": i // 4, "root": r, "quality": "N" if r is None else quality, "sim": 0.9, "margin_root": 0.1, "rms_db": -20.0}
          for i, r in enumerate(roots)]
    return {"sha16": sha, "title": sha, "bpm": 120.0, "inputs_sha256": {}, "beat_chroma": [[0.0] * 12] * (len(roots) + 1),
            "key": {"tonic": tonic, "tonic_name": K.PC_NAMES[tonic], "mode": "major", "corr": 0.9, "confidence": 0.1, "mode_margin": 0.2, "method": "test",
                    "track": {"modulation_flag": False}},
            "grid": {"bpm": 120.0, "phase": 1, "hypermeter_offset": 0, "n_beats": len(roots) + 1, "bar_convention": "test"},
            "chords": {"chord_stream": st, "n_pickup_beats_dropped": 1, "n_silent_beats": 0, "n_fraction": sum(r is None for r in roots) / len(roots), "change_rate_per_bar": 0.5}}


def test_04_functional_states_per_song_schema_and_loo() -> None:
    assert H.functional_state(7, "maj", 7) == "0:maj" and H.functional_state(0, "min7", 7) == "5:min7" and H.functional_state(None, "N", 3) == "N"
    assert H.segments_of([{"state": "0:maj", "beat": 0}, {"state": "0:maj", "beat": 1}, {"state": "7:maj", "beat": 2}]) == \
        [{"state": "0:maj", "start_beat": 0, "n_beats": 2}, {"state": "7:maj", "start_beat": 2, "n_beats": 1}]
    with tempfile.TemporaryDirectory() as td:
        rec = _fake_rec("deadbeefdeadbeef", 7, [7, 7, 0, 0, 2, 2, 7, 7, None, 7, 7, 7])
        p = Path(td) / "chords_v6.json"
        p.write_text(json.dumps(rec))
        r = H.per_song_record(rec, p)
    assert set(V5_PER_SONG_KEYS) <= set(r), sorted(set(V5_PER_SONG_KEYS) - set(r))
    assert [e["state"] for e in r["chord_stream"]][:5] == ["0:maj", "0:maj", "5:maj", "5:maj", "7:maj"] and r["key"]["tonic"] == 7
    assert r["n_beats"] == 12 and r["n_segments"] == 6 and r["segments"][0] == {"state": "0:maj", "start_beat": 0, "n_beats": 2}
    assert r["source"]["kind"] == "audio" and r["midi_dir"] is None and r["exclusion_rule"]["n_beats_in_stream"] == 12
    # LOO: a corpus of identical deterministic cycles is far below uniform; the smoothed rows are distributions
    cyc = ["0:maj", "0:maj", "5:maj", "5:maj", "7:maj", "7:maj", "9:min", "9:min"] * 6
    streams = {f"s{i}": list(cyc) for i in range(4)}
    segs = {k: [g["state"] for g in H.segments_of([{"state": s, "beat": i} for i, s in enumerate(v)])] for k, v in streams.items()}
    loo = H.loo_cross_entropy(streams, segs)
    assert loo["n_states"] == 4 and abs(loo["uniform_bits"] - 2.0) < 1e-9
    assert loo["mean_beat_level_bits"] < 1.2 and loo["mean_segment_level_bits"] < 0.3, loo
    L = H.smoothed_log2(list(streams.values()), sorted({s for v in streams.values() for s in v}), H.ALPHA)
    assert np.allclose((2.0 ** L).sum(axis=1), 1.0)
    mk = markov(streams, segs)
    assert set(V5_CHAIN_KEYS[:12]) <= set(mk) and mk["degeneracy_verdict"] in ("NON_DEGENERATE", "DEGENERATE")
    print(f"test_04 PASS: per-song schema superset of harmony_v5; LOO beat {loo['mean_beat_level_bits']} / segment {loo['mean_segment_level_bits']} bits vs uniform 2.0")


# ----------------------------------------------------------------------------------------------------- on-disk ----
def test_05_on_disk_chords_for_every_song() -> None:
    man = Path("data/v6/stems/manifest.json")
    if not man.exists() or not CHORDS_DIR.exists():
        return _skip("corpus stems / chords outputs absent (data/ is gitignored)")
    songs = sorted(json.loads(man.read_text())["songs"])
    files = {s: CHORDS_DIR / s / "chords_v6.json" for s in songs}
    missing = [s for s, p in files.items() if not p.exists()]
    if missing:
        return _skip(f"{len(missing)} chord files not built yet: {missing[:3]}")
    mt = json.loads(Path("data/v6/rules/microtiming_v6.json").read_text())["per_song"] if Path("data/v6/rules/microtiming_v6.json").exists() else {}
    rows = {}
    for s, p in files.items():
        d = json.loads(p.read_text())
        assert d["schema_version"] == 1 and d["sha16"] == s and "chord_fit" in d["key"] and "track" in d["key"]
        assert list(d) == sorted(d), "keys not sorted"
        g, view, st = d["grid"], d["chord_stream"], d["chords"]["chord_stream"]
        assert len(view) == g["n_beats"] and len(st) == g["n_beats"] - g["phase"] and len(d["beat_chroma"]) == g["n_beats"]
        if s in mt:
            assert (g["phase"], g["hypermeter_offset"], g["n_beats"]) == (mt[s]["grid"]["phase"], mt[s]["grid"]["hypermeter_offset"], mt[s]["grid"]["n_beats"]), s
            assert g["matches_microtiming"]["matches"], s
        rows[s] = (d["key"]["tonic_name"], d["key"]["mode"], d["chords"]["n_fraction"])
    assert len(rows) == 29
    for f in FOCUS:
        assert f in rows
    print(f"test_05 PASS: 29 chord files on the microtiming grid; focus keys " + ", ".join(f"{f[:6]}={rows[f][0]} {rows[f][1]}" for f in FOCUS))


def test_06_on_disk_chain_per_song_and_loo() -> None:
    if not CHAIN.exists():
        return _skip("harmony chain not built yet")
    mk = json.loads(CHAIN.read_text())
    assert set(V5_CHAIN_KEYS) <= set(mk), sorted(set(V5_CHAIN_KEYS) - set(mk))
    assert mk["degeneracy_verdict"] in ("NON_DEGENERATE", "DEGENERATE") and mk["degeneracy_thresholds"] == {"max_stationary_mass_lt": 0.60, "min_distinct_qualities": 4, "min_quality_segment_count": 8}
    S = mk["states"]
    assert len(mk["beat_level_counts"]) == len(S) and all(abs(sum(r) - 1.0) < 1e-3 for r in mk["beat_level_row_normalized"])
    assert abs(sum(mk["stationary_distribution"].values()) - 1.0) < 1e-3 and "N" in S
    used = mk["gate"]["used"]
    assert len(used) >= 3 and set(used) <= set(mk["per_song"])
    for s in used:
        p = PER_SONG / s / "harmony_v5.json"
        assert p.exists(), p
        d = json.loads(p.read_text())
        assert set(V5_PER_SONG_KEYS) <= set(d) and {e["state"] for e in d["chord_stream"]} <= set(S)
        assert d["key"]["tonic"] == mk["per_song"][s]["key"]["tonic"]
    loo = mk["loo_cross_entropy"]
    assert loo["mean_beat_level_bits"] < loo["uniform_bits"] and loo["mean_segment_level_bits"] < loo["uniform_bits"]
    assert set(loo["per_song"]) == set(used)
    summ = Path("data/v6/rules/harmony_v6_summary.json")
    if summ.exists():
        sm = json.loads(summ.read_text())
        assert sm["chain"]["degeneracy_verdict"] == mk["degeneracy_verdict"] and set(sm["per_song"]) >= set(used)
    print(f"test_06 PASS: chain {len(S)} states, verdict {mk['degeneracy_verdict']}, {len(used)} per-song files, LOO beat {loo['mean_beat_level_bits']} < uniform {loo['uniform_bits']}")


def test_07_composer_loads_real_harmony_form_comping() -> None:
    rd = Path("data/v5/rules")
    if not (CHAIN.exists() and (rd / "form_plan_v5.json").exists() and (rd / "comping_v5.json").exists()):
        return _skip("harmony / form / comping files not built yet")
    from scripts.v6.gen.fixtures import load_models
    m = load_models(rd, fixtures=True)
    for k in ("chain", "comping", "form_plan", "chord_streams"):
        assert m["sources"][k] not in ("fixture", "absent") and not str(m["sources"][k]).startswith("absent"), (k, m["sources"][k])
    assert m["chord_streams"] and all(set(v) == {"chord_stream", "key"} for v in m["chord_streams"].values())
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run([PY, "scripts/v6/gen/compose_v6.py", "--donors", ",".join(FOCUS), "--rules-dir", str(rd), "--fixtures", "--no-render", "--bars", "16", "--out", td],
                           capture_output=True, text=True, cwd=str(_ROOT))
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
        roll = json.loads((Path(td) / "iteration_rollup.json").read_text())
        assert len(roll["songs"]) == 3 and roll["model_sources"]["chain"].endswith("harmony_markov_v5_full.json")
    print(f"test_07 PASS: composer loaded {m['sources']['chain']}, {m['sources']['form_plan']}, {m['sources']['comping']} and composed the 3 focus donors")


def test_08_discipline() -> None:
    for name in ("chords_v6", "key_v6", "harmony_rules_v6", "form_v6", "comping_v6"):
        p = Path("scripts/v6/rules") / f"{name}.py"
        src = p.read_text()
        assert src.startswith("#!/usr/bin/python3"), name
        assert len(src.splitlines()) < 450, (name, len(src.splitlines()))
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                assert "random" not in names, (name, names)
            if isinstance(node, ast.Attribute):
                assert not (node.attr == "random" and isinstance(node.value, ast.Name) and node.value.id == "np"), name
        assert "interpreter_guard()" in src and "pin_env()" in src, name
    print("test_08 PASS: shebang, < 450 lines, no PRNG, guard + env pins in every harmony/form/comping rule module")


if __name__ == "__main__":
    fails = 0
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"{fn.__name__} FAIL: {type(exc).__name__}: {exc}")
    sys.exit(1 if fails else 0)
