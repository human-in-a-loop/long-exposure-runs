#!/usr/bin/python3
"""v6 Phase 3 tests — humanize: Box-Muller determinism + distribution, offsets clipped, swing only on odd 8ths, recurrences keep
harmony / bass roots / melody skeleton while the surface differs, v5 serializer carries the humanized timing to the tick,
compose_v6 --humanize --fixtures byte-deterministic (and different from the Phase-2 output), microtiming_v6 recovers a
known +20 ms odd-8th swing from a synthetic drum stem within 5 ms.

Run: /usr/bin/python3 tests/test_v6_humanize.py      or      /usr/bin/python3 -m pytest tests/test_v6_humanize.py -q
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.gen import humanize as H  # noqa: E402
from scripts.v6.gen import microtiming_model as M  # noqa: E402
from scripts.v6.gen import validators as V  # noqa: E402
from scripts.v6.gen.compose_v6 import compose_song, to_events  # noqa: E402
from scripts.v6.gen.fixtures import load_models  # noqa: E402

PY = "/usr/bin/python3"
CLI = ["scripts/v6/gen/compose_v6.py", "--iteration", "1", "--seed", "7", "--fixtures", "--bars", "32", "--bpm", "100,120,152", "--no-render"]
_RUNS: dict = {}
_MODELS = load_models(None, fixtures=True)


def _run(tag: str, humanize: bool = True) -> Path:
    key = (tag, humanize)
    if key not in _RUNS:
        d = Path(tempfile.mkdtemp(prefix=f"v6hum_{tag}_"))
        cmd = [PY] + CLI + (["--humanize"] if humanize else []) + ["--out", str(d)]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(_ROOT))
        assert r.returncode == 0, r.stdout + r.stderr
        _RUNS[key] = d
    return _RUNS[key]


def _shas(d: Path) -> dict:
    return {str(p.relative_to(d)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.rglob("*")) if p.is_file() and p.suffix in (".json", ".mid")}


def _flat_model(swing_ratio: float, std_ms: float, resid_ms: float = 0.0) -> dict:
    pool = M.prior_model(120.0)
    for st in pool["streams"].values():
        st["slot_resid_mean_ms"] = [resid_ms] * 16
        st["slot_std_ms"] = [std_ms] * 16
    pool["swing_ratios_drums"]["0.5"] = swing_ratio
    pool["bass_kick_lag_ms"] = {"n": 0, "mean": 0.0, "std": 0.0}
    return pool


def test_01_box_muller_deterministic_and_normal() -> None:
    zs = [H.z(f"bm|{i}") for i in range(6000)]
    assert zs == [H.z(f"bm|{i}") for i in range(6000)]
    assert len({round(x, 9) for x in zs}) > 5900 and all(-3.0 <= x <= 3.0 for x in zs)
    m = sum(zs) / len(zs)
    sd = math.sqrt(sum((x - m) ** 2 for x in zs) / len(zs))
    assert abs(m) < 0.05 and abs(sd - 1.0) < 0.05, (m, sd)
    inside = sum(1 for x in zs if abs(x) < 1.0) / len(zs)
    assert abs(inside - 0.6827) < 0.03, inside
    print(f"test_01 PASS: Box-Muller deterministic; mean={m:.4f} std={sd:.4f} P(|z|<1)={inside:.3f}")


def test_02_offsets_clipped_to_35pct_of_a_16th() -> None:
    res = compose_song(_MODELS, "gen_v6_song_1", "fixture_a", 3, 120.0, 32)
    song = res["song"]
    H.apply(song, _flat_model(1.0, 400.0), "clip-test")
    clip = 0.35 * (60000.0 / 120.0 / 4)
    offs = [n["offset_ms"] for stem in ("drums", "bass", "keys", "melody") for n in song[stem]]
    assert offs and max(abs(o) for o in offs) <= clip + 1e-9
    assert sum(1 for o in offs if abs(abs(o) - clip) < 1e-6) > len(offs) * 0.5, "huge std should pin most offsets at the clip"
    print(f"test_02 PASS: {len(offs)} offsets, max |offset| {max(abs(o) for o in offs):.3f} ms <= clip {clip:.3f} ms")


def test_03_swing_only_on_odd_8ths() -> None:
    res = compose_song(_MODELS, "gen_v6_song_1", "fixture_a", 3, 120.0, 32)
    song = res["song"]
    r = 1.2
    H.apply(song, _flat_model(r, 0.0), "swing-test")
    s16 = 60000.0 / 120.0 / 4
    expect = 2 * (r - 1) / (r + 1) * s16
    odd = [h["offset_ms"] for h in song["drums"] if h["slot"] % 16 in (2, 6, 10, 14)]
    even = [h["offset_ms"] for h in song["drums"] if h["slot"] % 16 not in (2, 6, 10, 14)]
    assert odd and even
    assert all(abs(o - expect) < 1e-6 for o in odd), (odd[:5], expect)
    assert all(abs(o) < 1e-6 for o in even), even[:5]
    bass_odd = [n["offset_ms"] for n in song["bass"] if n["slot"] % 16 in (2, 6, 10, 14)]
    assert all(abs(o - expect) < 1e-6 for o in bass_odd)
    val = V.validate_humanized(song, _flat_model(r, 0.0))
    assert abs(val["detail"]["humanize"]["swing"]["ratio"] - r) < 0.02
    print(f"test_03 PASS: {len(odd)} odd-8th hits at +{expect:.2f} ms, {len(even)} others at 0; measured ratio {val['detail']['humanize']['swing']['ratio']}")


def test_04_recurrences_keep_skeleton_roots_harmony_surface_differs() -> None:
    res = compose_song(_MODELS, "gen_v6_song_2", "fixture_b", 5, 120.0, 64, hz={"mt": None})
    song, var = res["song"], res["humanize"]["variation"]
    labels = [s["label"] for s in song["sections"]]
    assert labels == ["A", "A", "B", "A", "B", "C", "A", "A"] and sum(1 for v in var.values() if v["varied"]) == 5
    rep = res["validators"]["detail"]["humanize"]["section_repeat_relaxed"]
    assert rep["skeleton_ok"] and rep["surface_differs"] is True and rep["n_comparable_stem_pairs"] >= 8
    mel_pairs = [p for p in rep["pairs"] if p["stems"]["melody"]["comparable"]]
    assert mel_pairs and all(p["stems"]["melody"]["skeleton_identical"] for p in mel_pairs) and any(p["stems"]["melody"]["surface_differs"] for p in mel_pairs)
    assert all(p["harmony_ok"] for p in rep["pairs"]) and all(p["stems"]["bass"]["skeleton_identical"] for p in rep["pairs"] if p["stems"]["bass"]["comparable"])
    # direct check on two unmuted A recurrences (sections 1 and 3): skeleton notes identical, non-skeleton melody notes differ
    nb = song["bars_per_section"]

    def mel(sec: int, roles) -> list:
        s0 = sec * nb * 16
        return sorted((n["slot"] - s0, n["pitch"]) for n in song["melody"] if s0 <= n["slot"] < s0 + nb * 16 and (n.get("role") in roles) == True)
    skel = H.SKELETON_ROLES
    assert mel(1, skel) == mel(3, skel) and mel(1, skel)
    non1 = sorted((n["slot"] - 1 * nb * 16, n["pitch"], n.get("role")) for n in song["melody"] if nb * 16 <= n["slot"] < 2 * nb * 16 and n.get("role") not in skel)
    non3 = sorted((n["slot"] - 3 * nb * 16, n["pitch"], n.get("role")) for n in song["melody"] if 3 * nb * 16 <= n["slot"] < 4 * nb * 16 and n.get("role") not in skel)
    assert non1 != non3
    bass1 = sorted((n["slot"] - nb * 16, n["pitch"]) for n in song["bass"] if nb * 16 <= n["slot"] < 2 * nb * 16)
    bass3 = sorted((n["slot"] - 3 * nb * 16, n["pitch"]) for n in song["bass"] if 3 * nb * 16 <= n["slot"] < 4 * nb * 16)
    assert bass1 == bass3 and bass1
    keys1 = sorted({(n["slot"] // 16 - nb, n["pitch"]) for n in song["keys"] if nb * 16 <= n["slot"] < 2 * nb * 16})
    keys3 = sorted({(n["slot"] // 16 - 3 * nb, n["pitch"]) for n in song["keys"] if 3 * nb * 16 <= n["slot"] < 4 * nb * 16})
    assert keys1 == keys3 and keys1
    assert var["3"]["comping_templates"] != var["1"]["comping_templates"] or var["3"]["n_hat_bars_changed"] + var["1"]["n_hat_bars_changed"] > 0
    print(f"test_04 PASS: 5 varied recurrences; skeleton/bass/keys-pitch-sets identical across A(1) vs A(3), {len(non1)} vs {len(non3)} non-skeleton melody notes differ; "
          f"{rep['n_comparable_stem_pairs']} comparable stem pairs, {rep['n_surface_differing']} differ")


def test_05_serializer_tick_round_trip_and_fractional_timing() -> None:
    import mido
    d = _run("a")
    n_checked = n_offgrid = 0
    for sd in sorted(p for p in d.iterdir() if p.is_dir()):
        man = json.loads((sd / "ab_mix.manifest.json").read_text())
        bpm = float(man["tempo_bpm"])
        s16 = 60.0 / bpm / 4
        for stem in ("drums", "bass", "keys", "melody"):
            ev = json.loads((sd / "generated_json" / f"{stem}.json").read_text())
            starts = [e for e in ev if e["type"] == "start"]
            expected = sorted(round(e["start_time"] * bpm / 60.0 * 480) for e in starts)
            m = mido.MidiFile(str(sd / "generated_midi" / f"{stem}.mid"))
            assert m.ticks_per_beat == 480
            ticks, t = [], 0
            for msg in m.tracks[1]:
                t += msg.time
                if msg.type == "note_on":
                    ticks.append(t)
            ticks.sort()
            assert len(ticks) == len(expected)
            assert all(abs(a - b) <= 1 for a, b in zip(ticks, expected)), stem
            n_checked += len(ticks)
            n_offgrid += sum(1 for e in starts if abs((e["start_time"] / s16) - round(e["start_time"] / s16)) > 0.01)
    assert n_offgrid > n_checked * 0.5, "humanized starts should mostly be off the 16th grid"
    print(f"test_05 PASS: {n_checked} note-ons within 1 tick of round(start_time -> 480 PPQ); {n_offgrid} off the 16th grid")


def test_06_cli_humanize_byte_deterministic_and_differs_from_phase2() -> None:
    a, b = _shas(_run("a")), _shas(_run("b"))
    assert set(a) == set(b) and a
    diff = [k for k in a if a[k] != b[k] and not k.endswith("iteration_rollup.json")]
    assert not diff, diff[:10]
    assert sum(1 for k in a if k.endswith("humanize_manifest.json")) == 3
    p2 = _shas(_run("p2", humanize=False))
    for k in a:
        if k.endswith((".mid", "generated_json/drums.json", "generated_json/melody.json")):
            assert a[k] != p2[k], k
    rows = json.loads((_run("a") / "validators_table.json").read_text())
    for name in V.HUMANIZE_CAPS:
        assert name in rows["validators"] and rows["cap_pass_counts"][name] == 3, (name, rows["cap_pass_counts"])
    assert rows["cap_pass_counts"]["section_repeat_integrity"] == 3
    for sd in sorted(p for p in _run("a").iterdir() if p.is_dir()):
        hm = json.loads((sd / "humanize_manifest.json").read_text())
        assert hm["model"]["variant"] == "prior" and hm["schema_version"] == 1 and hm["offset_stats"]["hat"]["n"] > 0
        assert (sd / "humanize_manifest.json").read_text() == json.dumps(hm, sort_keys=True, indent=2) + "\n"
    print(f"test_06 PASS: {len(a)} JSON/MIDI files byte-identical across two --humanize runs; MIDI differs from Phase 2; humanize caps 3/3")


def test_07_microtiming_recovers_synthetic_swing() -> None:
    import numpy as np
    from scripts.v6.microtiming_v6 import SR, analyze_arrays
    bpm, n_bars, swing_ms, lag_ms = 120.0, 24, 20.0, 8.0
    s16 = 60.0 / bpm / 4
    rng = np.random.default_rng(0)  # test-only noise source (the generator itself has no PRNG)
    L = int((n_bars * 16 + 8) * s16 * SR)
    drums, bass = np.zeros(L, np.float32), np.zeros(L, np.float32)

    def burst(y, t, sig):
        s = int(round(t * SR))
        n = min(sig.size, y.size - s)
        if n > 0:
            y[s:s + n] += sig[:n]

    def shaped(sig, dur_s, decay):
        tt = np.arange(int(dur_s * SR)) / SR
        env = np.exp(-tt * decay) * np.hanning(2 * tt.size)[tt.size:] ** 0.25
        return (sig[: tt.size] * env).astype(np.float32)
    kick = shaped(np.sin(2 * np.pi * 55 * np.arange(int(0.15 * SR)) / SR), 0.15, 20)
    snare = shaped(rng.standard_normal(int(0.12 * SR)) * 0.6, 0.12, 30)
    from scipy.signal import butter, sosfilt
    hat = shaped(sosfilt(butter(4, 6000 / (SR / 2), "highpass", output="sos"), rng.standard_normal(int(0.05 * SR))) * 0.6, 0.05, 60)
    bass_note = shaped(np.sin(2 * np.pi * 55 * np.arange(int(0.35 * SR)) / SR) * 0.8, 0.35, 5)
    for bar in range(n_bars):
        for slot in range(16):
            t = (bar * 16 + slot) * s16 + 0.5
            if slot in (0, 8) or (slot == 10 and bar % 2):
                burst(drums, t, kick)
            if slot in (4, 12):
                burst(drums, t, snare)
            if slot % 2 == 0:
                burst(drums, t + (swing_ms / 1000 if slot in (2, 6, 10, 14) else 0.0), hat)
            if slot in (0, 6, 8, 12):
                burst(bass, t + lag_ms / 1000, bass_note)
    e = analyze_arrays(drums, bass, bpm)
    g = e["grid"]
    assert abs(g["tempo_ratio"] - 1.0) < 0.005 and g["beat_hit_frac"] > 0.9 and g["confidence"] in ("high", "medium"), g
    hat_sw = e["swing"]["hat"]
    assert hat_sw["offset_ms"] is not None and abs(hat_sw["offset_ms"] - swing_ms) <= 5.0, hat_sw
    kick_sw = e["swing"]["kick"]
    assert kick_sw["offset_ms"] is None or abs(kick_sw["offset_ms"]) <= 8.0, kick_sw
    lag = e["bass_kick_lag"]
    assert lag["n"] >= 20 and abs(lag["mean_ms"] - lag_ms) <= 6.0, lag
    pool = M.pool({"synthetic": e}, "all")
    assert abs(pool["streams"]["hat"]["swing"]["offset_ms"] - swing_ms) <= 5.0
    assert sum(e["streams"]["hat"]["hist_f16"]) == e["streams"]["hat"]["n_assigned"]
    print(f"test_07 PASS: synthetic +{swing_ms} ms odd-8th swing recovered as {hat_sw['offset_ms']} ms (hat), kick {kick_sw['offset_ms']} ms, bass-kick lag {lag['mean_ms']} ms "
          f"(true {lag_ms}); grid conf={g['confidence']} contrast={g['beat_contrast']}")


def test_08_validators_contract_unchanged_for_phase2_and_extended_under_humanize() -> None:
    res = compose_song(_MODELS, "gen_v6_song_1", "fixture_a", 1, 100.0, 32)
    assert set(res["validators"]["metrics"]) == set(V.CAPS) and "humanized" not in res["validators"]
    assert not any("offset_ms" in n for stem in ("drums", "bass", "keys", "melody") for n in res["song"][stem])
    ev = to_events(res["song"], "drums")
    assert all(abs(e["start_time"] * 100.0 / 60.0 * 4 - round(e["start_time"] * 100.0 / 60.0 * 4)) < 1e-6 for e in ev if e["type"] == "start")
    resh = compose_song(_MODELS, "gen_v6_song_1", "fixture_a", 1, 100.0, 32, hz={"mt": None})
    assert set(resh["validators"]["metrics"]) == set(V.ALL_CAPS) and resh["validators"]["humanized"]
    assert resh["validators"]["metrics"]["velocity_std_min"] >= 8.0 and resh["validators"]["metrics"]["timing_ks_max"] <= 0.25
    for k, c in V.HUMANIZE_CAPS.items():
        assert c["op"] in ("<=", ">=", "==") and {"op", "cap", "per", "doc"} <= set(c), k
    assert (Path("scripts/v6/gen/humanize.py").read_text().count("random") == 0)
    v5 = subprocess.run(["git", "status", "--porcelain", "--", "scripts/v5"], capture_output=True, text=True, cwd=str(_ROOT)).stdout.strip()
    assert v5 == "", f"scripts/v5 modified: {v5}"
    print("test_08 PASS: Phase-2 validate() keys unchanged, no offsets without --humanize, 16th-grid starts; humanized metrics = ALL_CAPS; scripts/v5 untouched")


def _run_all() -> int:
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
        except AssertionError as exc:
            fails += 1
            print(f"{name} FAIL: {exc}")
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"{name} ERROR: {type(exc).__name__}: {exc}")
    print("ALL PASS" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_run_all())
