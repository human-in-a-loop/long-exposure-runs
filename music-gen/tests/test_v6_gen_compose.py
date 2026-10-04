#!/usr/bin/python3
"""v6 Phase 2 tests — compose_v6 end to end on fixtures: byte determinism (two runs -> identical sha of every JSON + MIDI),
output layout, v5 event format, serializer round trip, rollup/table, no PRNG in scripts/v6/gen, module size budget.

Run: /usr/bin/python3 tests/test_v6_gen_compose.py      or      /usr/bin/python3 -m pytest tests/test_v6_gen_compose.py -q
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

PY = "/usr/bin/python3"
CLI = ["scripts/v6/gen/compose_v6.py", "--iteration", "1", "--seed", "7", "--fixtures", "--bars", "32", "--bpm", "100,120,152", "--no-render"]
_RUNS: dict = {}


def _run(tag: str) -> Path:
    if tag not in _RUNS:
        d = Path(tempfile.mkdtemp(prefix=f"v6gen_{tag}_"))
        r = subprocess.run([PY] + CLI + ["--out", str(d)], capture_output=True, text=True, cwd=str(_ROOT))
        assert r.returncode == 0, r.stdout + r.stderr
        _RUNS[tag] = d
    return _RUNS[tag]


def _shas(d: Path) -> dict:
    out = {}
    for p in sorted(d.rglob("*")):
        if p.is_file() and p.suffix in (".json", ".mid"):
            out[str(p.relative_to(d))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def test_01_byte_determinism_two_runs() -> None:
    a, b = _shas(_run("a")), _shas(_run("b"))
    assert set(a) == set(b) and a
    diff = [k for k in a if a[k] != b[k] and not k.endswith("iteration_rollup.json")]
    assert not diff, diff[:10]
    ra, rb = json.loads((_run("a") / "iteration_rollup.json").read_text()), json.loads((_run("b") / "iteration_rollup.json").read_text())
    for sa, sb in zip(ra["songs"], rb["songs"]):
        assert {k: v for k, v in sa.items() if k not in ("compose_wall_s", "render_wall_s", "dir")} == {k: v for k, v in sb.items() if k not in ("compose_wall_s", "render_wall_s", "dir")}
    n_mid = sum(1 for k in a if k.endswith(".mid"))
    assert n_mid == 12, n_mid
    print(f"test_01 PASS: {len(a)} JSON/MIDI files byte-identical across two runs ({n_mid} MIDI stems)")


def test_02_layout_event_format_and_serializer_round_trip() -> None:
    import mido
    d = _run("a")
    songs = sorted(p for p in d.iterdir() if p.is_dir())
    assert len(songs) == 3
    for sd in songs:
        for f in ("plan.json", "validators.json", "ab_mix.manifest.json"):
            j = json.loads((sd / f).read_text())
            assert j.get("schema_version") == 1, f
            assert (sd / f).read_text() == json.dumps(j, sort_keys=True, indent=2) + "\n", f"{f} not sorted-key canonical"
        for stem in ("drums", "bass", "keys", "melody"):
            ev = json.loads((sd / "generated_json" / f"{stem}.json").read_text())
            starts = [e for e in ev if e["type"] == "start"]
            ends = [e for e in ev if e["type"] == "end"]
            assert len(starts) == len(ends) and starts, stem
            for e in starts:
                assert set(e) == {"index", "instrument", "pitch", "start_time", "type", "velocity"} and 1 <= e["velocity"] <= 127
            m = mido.MidiFile(str(sd / "generated_midi" / f"{stem}.mid"))
            n_on = sum(1 for tr in m.tracks for msg in tr if msg.type == "note_on")
            assert n_on == len(starts), (stem, n_on, len(starts))
            ch = {msg.channel for tr in m.tracks for msg in tr if msg.type == "note_on"}
            assert ch == ({9} if stem == "drums" else {0} if stem == "bass" else {2} if stem == "keys" else {4}), (stem, ch)
        plan = json.loads((sd / "plan.json").read_text())
        assert plan["form"]["labels"] == ["A", "A", "B", "A"] and len(plan["phrases"]) == 8 and all("voicing" in c for c in plan["chord_slots"])
        assert all(c["cost"] is None or "total_step" in c["cost"] for c in plan["chord_slots"])
        assert {p["cadence_planned"] for p in plan["phrases"]} <= {"authentic", "half", "plagal", "deceptive"}
        assert plan["arrangement"]["outro"]["final_bar_held"] and plan["arrangement"]["fills"]
        man = json.loads((sd / "ab_mix.manifest.json").read_text())
        assert man["fixtures_sha256"] and man["model_sources"]["chain"] == "fixture" and "render" not in man
    tbl = json.loads((d / "validators_table.json").read_text())
    assert tbl["n_songs"] == 3 and set(tbl["rows"]) == {"gen_v6_song_1", "gen_v6_song_2", "gen_v6_song_3"}
    print("test_02 PASS: per-song layout, v5 event format, MIDI note counts/channels, plan + manifest contents, validators table")


def test_03_no_prng_guard_pins_and_module_budget() -> None:
    gen = Path("scripts/v6/gen")
    for p in sorted(gen.glob("*.py")):
        txt = p.read_text()
        assert not re.search(r"\brandom\b|np\.random|numpy\.random|secrets\.|uuid4", txt), f"PRNG use in {p}"
        n = len(txt.splitlines())
        assert n < 450, f"{p} has {n} lines (budget 450)"
    common = (gen / "common.py").read_text()
    assert 'sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ' in common
    assert "os.environ.setdefault" in common and all(k in common for k in ("PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"))
    from scripts.v6.gen.common import ENV_PIN_SHA256, PINS
    assert hashlib.sha256(json.dumps(PINS, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == ENV_PIN_SHA256
    # scripts/v5 is never modified by this phase: only read-only imports
    v5_status = subprocess.run(["git", "status", "--porcelain", "--", "scripts/v5"], capture_output=True, text=True, cwd=str(_ROOT)).stdout.strip()
    assert v5_status == "", f"scripts/v5 modified: {v5_status}"
    print("test_03 PASS: no PRNG; guard + 7-key env pin (sha matches); every module < 450 lines; scripts/v5 untouched")


def test_04_real_model_loader_paths_and_fixture_fallback() -> None:
    from scripts.v6.gen.fixtures import load_models
    with tempfile.TemporaryDirectory() as td:
        rd = Path(td)
        try:
            load_models(rd, fixtures=False)
            raise AssertionError("expected FileNotFoundError without fixtures")
        except FileNotFoundError:
            pass
        m = load_models(rd, fixtures=True)
        assert m["sources"]["chain"] == "fixture" and m["sources"]["form_plan"].startswith("absent") and m["fixtures_sha256"]
        # fixture mode is hermetic: a real file under rules-dir is IGNORED while fixtures=True ...
        from scripts.v6.gen.fixtures import fixture_chain, fixture_groove, fixture_bass_model, fixture_melody_vomm
        (rd / "harmony_markov_v5_full.json").write_text(json.dumps(fixture_chain()))
        m2 = load_models(rd, fixtures=True)
        assert m2["sources"]["chain"] == "fixture"
        # ... and read when fixtures=False (same loader, path args); the other required models must then exist too
        (rd / "groove_v5_v2_full.json").write_text(json.dumps(fixture_groove()))
        (rd / "bass_pitch_v5.json").write_text(json.dumps(fixture_bass_model()))
        (rd / "melody_vomm_v5.json").write_text(json.dumps(fixture_melody_vomm()))
        m3 = load_models(rd, fixtures=False)
        assert m3["sources"]["chain"].endswith("harmony_markov_v5_full.json") and "chain" in m3["input_sha256"]
    print("test_04 PASS: fixture mode hermetic; real files read with fixtures=False")


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
