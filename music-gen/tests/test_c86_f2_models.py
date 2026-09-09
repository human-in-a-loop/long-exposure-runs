#!/usr/bin/python3
"""c86 worker P2b tests — F2 bass pitch model + melody VOMM: synthetic root-on-downbeat reproduction, sampler determinism
and class coverage, VOMM cross-process determinism, escape backoff on unseen contexts, discipline scan.

created: 2026-09-09T23:30:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F2-bass-melody-dynamics

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c86_f2_models.py
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

from scripts.v5 import bass_pitch_v5 as bp  # noqa: E402
from scripts.v5 import melody_vomm_v5 as mv  # noqa: E402

NEW_SCRIPTS = ["scripts/v5/bass_pitch_v5.py", "scripts/v5/melody_vomm_v5.py"]


def _synthetic_bass() -> tuple[list[tuple[int, int]], list[dict]]:
    """16 bars, chord alternates C (root 0) / G (root 7) every 4 beats; bass plays root on slot 0 of every beat, fifth on
    slot 2 of every beat, and an octave on slot 1 of every downbeat. Known root-on-downbeat fraction = 0.5 root + 0.5 octave
    -> root-pc fraction 1.0 among downbeat onsets... reduced by an 'other' note on slot 0 of every 4th downbeat (-> 0.875)."""
    chord_stream, onsets = [], []
    for beat in range(64):
        root = 0 if (beat // 4) % 2 == 0 else 7
        chord_stream.append({"beat": beat, "root": root, "quality": "major", "state": "C"})
        base = beat * 480
        low = 36 + root  # C2 / G2
        if beat % 16 == 12:
            onsets.append((base, low + 2))  # 'other' on slot 0 of every 4th downbeat
        else:
            onsets.append((base, low))  # root on slot 0
        if beat % 4 == 0:
            onsets.append((base + 120, low + 12))  # octave on slot 1 of downbeats
        onsets.append((base + 240, low + 7))  # fifth on slot 2
    return onsets, chord_stream


def test_01_bass_synthetic_root_on_downbeat_reproduced() -> None:
    onsets, cs = _synthetic_bass()
    tmp = tempfile.mkdtemp(prefix="c86_f2_synth_")
    Path(tmp, "synthetic.json").write_text(json.dumps({"onsets": onsets, "chord_stream": cs}))
    a = bp.analyze_song(onsets, cs, phase_offset=0)
    assert a["n_skipped_null_chord"] == 0 and a["n_used"] == len(onsets)
    counts = {}
    for e in a["events"]:
        counts[e["cls"]] = counts.get(e["cls"], 0) + 1
    # the fifth of G (D, pc 2) sits 2 semitones from the next root C on the G->C change beats -> approach (precedence);
    # beats 7,15,...,55 = 7 such beats (beat 63 is the last beat: no next chord -> chg = 0)
    assert counts["octave"] == 16 and counts["fifth"] == 57 and counts["approach"] == 7 and counts["other"] == 4, counts
    assert counts["root"] == 60 and sum(counts.values()) == len(onsets), counts
    model = bp.build_model({"synthetic": a})
    db = model["downbeat"]["aligned"]
    assert db["n_onsets"] == 16 and abs(db["root_pc_fraction"] - 12 / 16) < 1e-9, db
    chk = bp.run_sampling_check(model)
    assert chk["n"] == 2000 and chk["abs_diff"] <= 0.15 and chk["pass"] is True, chk
    assert chk == bp.run_sampling_check(model)  # deterministic
    print(f"test_01 PASS: synthetic downbeat root-pc {db['root_pc_fraction']} vs sampled {chk['sampled_root_pc_fraction']} (tmp {tmp})")


def test_02_sample_interval_class_deterministic_and_covers_all_classes() -> None:
    row = {"n": 6, "counts": {c: 1 for c in bp.CLASS_ORDER}, "probs": {c: 1 / 6 for c in bp.CLASS_ORDER}}
    model = {"class_order": list(bp.CLASS_ORDER), "conditional": {"0|1": row}, "marginal": row}
    seen = {bp.sample_interval_class(model, 0, True, i / 1000.0) for i in range(1000)}
    assert seen == set(bp.CLASS_ORDER), seen
    assert [bp.sample_interval_class(model, 0, True, u) for u in (0.0, 0.2, 0.5, 0.99)] == \
           [bp.sample_interval_class(model, 0, True, u) for u in (0.0, 0.2, 0.5, 0.99)]
    assert bp.sample_interval_class(model, 2, False, 0.5) == bp.sample_interval_class(model, 2, False, 0.5)  # marginal fallback
    reg = {"median": 40, "iqr_lo": 36, "iqr_hi": 45}
    for cls in bp.CLASS_ORDER:
        for u in (0.1, 0.9):
            p = bp.interval_to_pitch(cls, 0, 7, reg, u)
            assert 28 <= p <= 60, (cls, p)
    assert bp.interval_to_pitch("root", 0, None, reg, 0.3) == 36
    assert bp.interval_to_pitch("octave", 0, None, reg, 0.3) == 48
    assert bp.interval_to_pitch("fifth", 0, None, reg, 0.3) == 43
    assert bp.interval_to_pitch("approach", 0, 7, reg, 0.1) == 42 and bp.interval_to_pitch("approach", 0, 7, reg, 0.9) == 41
    assert bp.interval_to_pitch("approach", 0, None, reg, 0.1) == 36  # no next root -> root placement
    print("test_02 PASS: sample_interval_class covers 6 classes deterministically; interval_to_pitch in 28..60")


def test_03_vomm_determinism_across_fresh_subprocesses() -> None:
    model_p = _ROOT / "data/v5/rules/melody_vomm_v5.json"
    assert model_p.exists(), model_p
    code = ("import json,sys;sys.path.insert(0,'.');from scripts.v5.melody_vomm_v5 import generate_sequence;"
            f"m=json.load(open('{model_p}'));print(json.dumps(generate_sequence(m,50,'c86_det_seed')))")
    env = dict(os.environ, PYTHONPATH=".", SUPPRESS_INTERPRETER_GUARD="1")
    outs = [subprocess.run(["/usr/bin/python3", "-c", code], capture_output=True, text=True, check=True, cwd=_ROOT, env=env).stdout
            for _ in range(2)]
    assert outs[0] == outs[1] and len(json.loads(outs[0])) == 50, outs
    assert json.loads(outs[0]) == mv.generate_sequence(json.loads(model_p.read_text()), 50, "c86_det_seed")
    print(f"test_03 PASS: 50-token VOMM sequence identical across 2 fresh subprocesses (first 4: {json.loads(outs[0])[:4]})")


def test_04_escape_falls_back_to_shorter_context() -> None:
    seqs = [["0|4", "2|4", "4|4", "0|4", "2|4", "4|4", "5|2"]]
    counts = mv.train_counts(seqs)
    model = {"max_order": 3, "counts": counts}
    assert mv.sample_next(model, ("0|4", "2|4", "4|4"), 0.99) in {"0|4", "5|2"}  # order-3 context seen
    # unseen order-3 and order-2 contexts, but order-1 context '2|4' is seen -> always '4|4'
    assert all(mv.sample_next(model, ("c|1", "c|1", "2|4"), u) == "4|4" for u in (0.0, 0.5, 0.999))
    # nothing matches at any order > 0 -> unigram row (order 0)
    toks = {mv.sample_next(model, ("c|1", "c|1", "c|1"), i / 200.0) for i in range(200)}
    assert toks == {"0|4", "2|4", "4|4", "5|2"}, toks
    assert mv.sample_next({"max_order": 3, "counts": {"0": {}, "1": {}, "2": {}, "3": {}}}, (), 0.5) == "0|4"
    # fold (0: 60,64 -> 64 = pc 4 = degree 2), gap 480 -> 4; 62 = degree 1, gap 960 -> 8; 61 chromatic, last -> 12
    assert mv.tokenize([(0, 60), (0, 64), (480, 62), (1440, 61)], 0, "major") == ["2|4", "1|8", "c|12"]
    assert mv.token_pitch("2|4", 0, "major", 60, 72, 62) == 64 and mv.token_pitch("4|4", 0, "major", 60, 72, 62) == 67
    assert mv.token_pitch("c|1", 0, "major", 60, 72, 72) == 72 and mv.token_pitch("0|4", 0, "minor", 48, 60, None) == 48  # midpoint 54 tie -> lower
    st = mv.order_stats(counts)
    # order-3 contexts: (0|4 2|4 4|4) x2, (2|4 4|4 0|4), (4|4 0|4 2|4) -> 3 contexts, 2 singletons
    assert st["3"]["n_contexts"] == 3 and st["3"]["n_singleton_contexts"] == 2 and st["0"]["n_events"] == 7, st
    assert abs(st["3"]["singleton_context_fraction"] - 2 / 3) < 1e-9, st
    print("test_04 PASS: escape backs off order 3 -> 2 -> 1 -> 0; empty model -> '0|4'")


def test_05_discipline_scan_of_both_scripts() -> None:
    bad_mods = {"random", "numpy.random", "sidecar_nonfactor"}
    for p in NEW_SCRIPTS:
        src = Path(p).read_text()
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                assert not any(a.name in bad_mods or "sidecar_nonfactor" in a.name or a.name.endswith(".random") for a in n.names), p
            if isinstance(n, ast.ImportFrom):
                assert n.module not in bad_mods and "sidecar_nonfactor" not in (n.module or ""), p
                assert not any(a.name == "random" for a in n.names), p
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                assert n.func.attr not in {"get_state", "save_state", "save_preset", "load_state", "set_state"}, (p, n.func.attr)
        assert "/usr/bin/python3" in src.splitlines()[0] and "SUPPRESS_INTERPRETER_GUARD" in src, p
        assert 'setdefault("PYTHONHASHSEED"' in src.replace("os.environ.setdefault(_k, _v)", "") or "PYTHONHASHSEED" in src, p
        for stem in ("bass_pitch_v5", "melody_vomm_v5"):
            if stem in p:
                art = json.loads(Path(f"data/v5/rules/{stem}.json").read_text())
                assert art["script_sha256"] == bp.sha_file(Path(p)), (p, "artifact script_sha256 stale")
    print(f"test_05 PASS: discipline on {len(NEW_SCRIPTS)} c86 scripts; artifact script_sha256 matches on-disk images")


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
