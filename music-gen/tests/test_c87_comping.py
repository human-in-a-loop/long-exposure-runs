#!/usr/bin/python3
"""c87 worker P3 tests — F3 comping statistics: prereg-before-output + pinned prereg sha, byte-determinism record + live
script sha, verdict enum consistency with the recorded counts/thresholds, tempo-override application + v5c dir, discipline.

created: 2026-09-10T01:50:00Z
cycle: 87
harness_cycle: 131
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F3-comping-statistics-c87

Run: /usr/bin/python3 tests/test_c87_comping.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

PREREG = Path("data/v5/rules/comping_prereg_c87.json")
OUT = Path("data/v5/rules/comping_v5.json")
FIG = Path("data/v5/rules/fig_comping_v5_c87.png")
BYTEDET = Path("data/v5/rules/byte_determinism_c87_comping.json")
SCRIPT = Path("scripts/v5/comping_v5.py")
PLOT = Path("data/v5/rules/plot_comping_v5_c87.py")
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
OVERRIDE_SONGS = ["88d247468cb6d49f", "cdd2717e52820ff6"]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_01_prereg_before_output_and_sha_pinned() -> None:
    for p in (PREREG, OUT, FIG):
        assert p.exists(), p
    pm, om, fm = PREREG.stat().st_mtime, OUT.stat().st_mtime, FIG.stat().st_mtime
    assert pm < om, ("PREREG_AFTER_OUTPUT", pm, om)
    assert pm < fm, ("PREREG_AFTER_FIGURE", pm, fm)
    prereg = json.loads(PREREG.read_text())
    out = json.loads(OUT.read_text())
    assert out["prereg_sha256"] == _sha(PREREG), "prereg_sha256 in output != on-disk prereg"
    assert out["prereg_path"] == str(PREREG)
    assert prereg["written_before_any_output"] is True and prereg["cycle"] == 87 and prereg["agent"] == "worker"
    assert prereg["env_pin_sha256"] == ENV_PIN == out["env_pin_sha256"]
    assert prereg["thresholds"] == out["verdict"]["thresholds"], "thresholds retuned after prereg"
    assert prereg["held_constant"]["eligible"]["sha256"] == out["eligible"]["sha256"] == _sha(Path(out["eligible"]["path"]))
    assert prereg["held_constant"]["tempo_overrides"]["sha256"] == out["tempo_overrides_c86"]["sha256"]
    assert out["cycle"] == 87 and out["agent"] == "worker" and out["run_id"] == "run-2026-09-06T000000Z"
    print(f"test_01 PASS: prereg mtime < output mtime (dt {om - pm:.1f}s) and < figure mtime; prereg sha {out['prereg_sha256'][:12]} pinned")


def test_02_byte_determinism_record_and_live_script_sha() -> None:
    bd = json.loads(BYTEDET.read_text())
    assert bd["equal"] is True and bd["run1_sha256"] == bd["run2_sha256"], bd
    assert bd["run1_sha256"] == _sha(OUT), "byte-det run1 sha != on-disk comping_v5.json"
    live = _sha(SCRIPT)
    assert bd["script_sha256"] == live == bd["script_sha256_after_runs"], ("script sha stale", bd["script_sha256"], live)
    assert json.loads(OUT.read_text())["script_sha256"] == live, "artifact script_sha256 stale"
    for k in ("tempdir_run2", "command", "checked_utc", "env_pin_sha256", "agent", "cycle"):
        assert k in bd, k
    assert bd["env_pin_sha256"] == ENV_PIN and bd["agent"] == "worker" and bd["cycle"] == 87
    assert "--out <out>" in bd["command"] and bd["tempdir_run2"] in bd["command_run2"]
    print(f"test_02 PASS: byte-det x2 equal ({bd['run1_sha256'][:12]}); script sha {live[:12]} matches record + artifact")


def test_03_verdict_enum_consistent_with_counts() -> None:
    out = json.loads(OUT.read_text())
    v = out["verdict"]
    assert v["enum"] in {"COMPING_NON_DEGENERATE", "COMPING_DEGENERATE"}, v["enum"]
    assert sorted(v["enum_values"]) == ["COMPING_DEGENERATE", "COMPING_NON_DEGENERATE"]
    th = v["thresholds"]
    assert th == {"min_songs": 8, "min_bars_with_onsets_per_song": 16, "pooled_max_slot_mass_lt": 0.5, "chord_window_ms": 30}, th
    # recompute the counts from the per-song records and the pooled histogram
    ge = sorted(s for s, r in out["per_song"].items() if r["n_bars_with_onsets_pooled"] >= th["min_bars_with_onsets_per_song"])
    assert ge == v["songs_with_ge_16_pooled_bars"] and len(ge) == v["n_songs_with_ge_16_pooled_bars"], (ge, v)
    h = out["stats"]["pooled"]["slot16_histogram"]
    assert len(h) == 16 and abs(sum(h) - 1.0) < 1e-4, sum(h)
    assert abs(max(h) - v["pooled_max_slot_mass"]) < 1e-9 and out["stats"]["pooled"]["slot16_max_mass"] == v["pooled_max_slot_mass"]
    expected = "COMPING_NON_DEGENERATE" if (len(ge) >= th["min_songs"] and max(h) < th["pooled_max_slot_mass_lt"]) else "COMPING_DEGENERATE"
    assert v["enum"] == expected, (v["enum"], expected)
    assert v["songs_ok"] == (len(ge) >= th["min_songs"]) and v["slot_mass_ok"] == (max(h) < th["pooled_max_slot_mass_lt"])
    # per-stem bookkeeping: n_bars = sum over contributing songs of their per-stem bar counts; pooled n_songs = 23 eligible
    for stem in ("guitar", "piano", "other"):
        st = out["stats"][stem]
        n_bars = sum(r["per_stem"][stem]["n_bars_with_onsets"] for r in out["per_song"].values())
        n_songs = sum(1 for r in out["per_song"].values() if r["per_stem"][stem]["n_onset_groups"] > 0)
        assert st["n_bars"] == n_bars and st["n_songs"] == n_songs, (stem, st["n_bars"], n_bars, st["n_songs"], n_songs)
        assert len(st["ioi16_histogram"]) == 16 and (st["n_ioi"] == 0 or abs(sum(st["ioi16_histogram"]) - 1.0) < 1e-4)
    assert out["stats"]["pooled"]["n_bars"] == sum(r["n_bars_with_onsets_pooled"] for r in out["per_song"].values())
    assert out["eligible"]["n_used"] == len(out["per_song"]) == 23
    print(f"test_03 PASS: verdict {v['enum']} consistent: {len(ge)} songs >= 16 bars (min 8), max slot mass {max(h)} (< 0.5)")


def test_04_tempo_overrides_applied_and_v5c_dir() -> None:
    out = json.loads(OUT.read_text())
    to = out["tempo_overrides_c86"]
    assert to["applied_to"] == OVERRIDE_SONGS, to["applied_to"]
    assert sorted(to["overrides"]) == OVERRIDE_SONGS and to["midi_dir_asserted"] == "canonical_v5c_reindexed"
    assert to["sha256"] == _sha(Path(to["path"]))
    live = {k: float(v) for k, v in json.loads(Path(to["path"]).read_text()).items()}
    assert sorted(live) == OVERRIDE_SONGS
    for s, r in out["per_song"].items():
        if s in OVERRIDE_SONGS:
            assert Path(r["midi_dir"]).name == "canonical_v5c_reindexed", (s, r["midi_dir"])
            assert "tempo_override_c86" in r and abs(r["bpm_used"] - live[s]) < 1e-6, (s, r["bpm_used"], live[s])
            assert r["tempo_override_c86"]["bpm_override"] != r["tempo_override_c86"]["bpm_v5_manifest"]
        else:
            assert "tempo_override_c86" not in r and Path(r["midi_dir"]).name == "canonical_v5_reindexed", (s, r["midi_dir"])
    assert set(out["eligible"]["used"]) == set(out["per_song"]) and not set(out["eligible"]["late_landed_deferred"]) & set(out["per_song"])
    print(f"test_04 PASS: overrides applied to exactly {OVERRIDE_SONGS} at {[out['per_song'][s]['bpm_used'] for s in OVERRIDE_SONGS]} BPM from canonical_v5c_reindexed/")


def test_05_discipline_and_plot_out_required() -> None:
    bad_mods = {"random", "numpy.random", "sidecar_nonfactor"}
    for p in (SCRIPT, PLOT, Path(__file__)):
        src = p.read_text()
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                assert not any(a.name in bad_mods or a.name.endswith(".random") or "sidecar_nonfactor" in a.name for a in n.names), p
            if isinstance(n, ast.ImportFrom):
                assert n.module not in bad_mods and "sidecar_nonfactor" not in (n.module or ""), p
                assert not any(a.name == "random" for a in n.names), p
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                assert n.func.attr not in {"get_state", "save_state", "save_preset", "load_state", "set_state"}, (p, n.func.attr)
        assert src.splitlines()[0] == "#!/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" in src, p
        assert 'sys.executable != "/usr/bin/python3"' in src, p
    src = SCRIPT.read_text()
    assert "datetime" not in src and "time.time" not in src, "wall-clock in comping_v5.py"
    assert "sort_keys=True" in src and "PYTHONHASHSEED" in src
    env = dict(os.environ, SUPPRESS_INTERPRETER_GUARD="1")
    r = subprocess.run(["/usr/bin/python3", str(PLOT)], capture_output=True, text=True, cwd=_ROOT, env=env)
    assert r.returncode == 2 and "--out" in r.stderr, (r.returncode, r.stderr[-300:])
    # the plot script reads only comping_v5.json
    assert PLOT.read_text().count("read_text()") == 1 and "comping_v5.json" in PLOT.read_text()
    print("test_05 PASS: discipline on comping_v5.py / plot_comping_v5_c87.py / this test (no PRNG, guard, no wall-clock); plot --out required -> rc 2")


if __name__ == "__main__":
    fails = 0
    tests = sorted((k, v) for k, v in globals().items() if k.startswith("test_"))
    for name, fn in tests:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"{name} FAIL: {e!r}")
    print(f"{len(tests) - fails}/{len(tests)} PASS")
    sys.exit(1 if fails else 0)
