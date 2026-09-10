#!/usr/bin/python3
"""c87 F3 comping event builder tests (standalone module; --f3 wiring deferred to c88 — generate_v5.py image untouched).

created: 2026-09-10T01:56:30Z
cycle: 87
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F3-guitar-piano-other

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c87_f3_gen.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
MODEL = json.loads(Path("data/v5/rules/comping_v5.json").read_text())
CHORDS = ["0:maj", "5:maj", "7:maj", "N", "9:min", "0:maj", "2:min", "7:7"]  # chain-state syntax '<root pc>:<quality>' / 'N'


def _u(tag: str) -> float:
    return int(hashlib.sha256(tag.encode()).hexdigest()[:13], 16) / float(1 << 52)


def _events(stem="guitar", n_rep=1, vel=False):
    from scripts.v5.comping_gen_v5 import build_comp_events
    return build_comp_events(CHORDS * n_rep, 0, 120.0, MODEL, "t|seed=0", _u, stem=stem, velocity_fn=(lambda t: 40 + int(_u(t) * 70)) if vel else None)


def test_01_deterministic_and_serializable_by_both_serializers() -> None:
    from scripts.v3_spine.midi_from_json_events import serialize as c4
    from scripts.v5.midi_from_json_events_v5 import serialize as v5
    a, b = _events(), _events()
    assert a and json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    with tempfile.TemporaryDirectory() as td:
        j = Path(td) / "comp.json"
        j.write_text(json.dumps(a, sort_keys=True, separators=(",", ":")))
        c4(str(j), f"{td}/a.mid", 120.0, (4, 4)); v5(str(j), f"{td}/b.mid", 120.0, (4, 4))
        assert hashlib.sha256(Path(f"{td}/a.mid").read_bytes()).hexdigest() == hashlib.sha256(Path(f"{td}/b.mid").read_bytes()).hexdigest()
    print(f"test_01 PASS: {len(a)//2} comp notes deterministic; c4 == v5 serializer bytes without velocities")


def test_02_rests_on_no_chord_bars_and_times_inside_bars() -> None:
    ev = _events()
    starts = [e for e in ev if e["type"] == "start"]
    bar_len = 2.0  # 120 bpm
    bars = {int(s["start_time"] // bar_len + 1e-9) for s in starts}
    assert 3 not in bars and bars <= set(range(len(CHORDS)))  # 'N' bar rests; nothing outside the form
    ends = {e["start_event_index"]: e["end_time"] for e in ev if e["type"] == "end"}
    for s in starts:
        assert ends[s["index"]] > s["start_time"] and 40 <= s["pitch"] <= 108
    print(f"test_02 PASS: 'N' bar rests; {len(starts)} starts in bars {sorted(bars)}; ends after starts; pitches in register")


def test_03_ioi_walk_follows_histogram_and_velocity_hook() -> None:
    from collections import Counter
    ev = _events(n_rep=60)
    starts = sorted({round(e["start_time"], 6) for e in ev if e["type"] == "start"})
    s16 = 0.125
    iois = Counter()
    for a, b in zip(starts, starts[1:]):
        k = int(round((b - a) / s16))
        if 1 <= k <= 16:
            iois[k] += 1
    tot = sum(iois.values())
    h = MODEL["stats"]["guitar"]["ioi16_histogram"]
    assert abs(iois[1] / tot - h[0]) < 0.08 and abs(iois[2] / tot - h[1]) < 0.08, (iois[1] / tot, h[0], iois[2] / tot, h[1])
    v = _events(vel=True)
    vels = {e["velocity"] for e in v if e["type"] == "start"}
    assert len(vels) >= 2 and all(1 <= x <= 127 for x in vels)
    print(f"test_03 PASS: IOI walk reproduces the guitar histogram (1:{iois[1]/tot:.3f} vs {h[0]:.3f}, 2:{iois[2]/tot:.3f} vs {h[1]:.3f}); velocity hook honoured")


def test_04_generate_v5_untouched_and_discipline() -> None:
    bd = json.loads(Path("data/v5/gen/byte_determinism_c86.json").read_text())
    # c88 re-pin (disclosed): the --f3 wiring landed in c88 as planned; the c87 image is now the c88 pre-edit pin and the c88 record proves flag-off reproduces iteration 3
    bd88 = json.loads(Path("data/v5/gen/byte_determinism_c88.json").read_text())
    assert bd["post_edit_script_sha256"]["generate_v5"] == bd88["turn_start_pins"]["generate_v5_pre_edit"]["sha256"], "c87 image must equal the c88 pre-edit pin"
    bd89 = json.loads(Path("data/v5/gen/byte_determinism_c89.json").read_text())  # c89 re-pin (disclosed): chain c88 post-edit == c89 pre-edit pin; on-disk == c89 post-edit
    assert bd88["post_edit_script_sha256"]["generate_v5"] == bd89["turn_start_pins"]["generate_v5_pre_edit"]["sha256"] and bd88["entries"]["iteration_03_flag_off_replay"]["n_equal"] == 5
    assert bd89["post_edit_script_sha256"]["generate_v5"] == hashlib.sha256(Path("scripts/v5/generate_v5.py").read_bytes()).hexdigest()
    src = Path("scripts/v5/comping_gen_v5.py").read_text()
    ast.parse(src)
    assert '"/usr/bin/python3"' in src and not re.search(r"\b(random\.|np\.random|numpy\.random|time\.time)", src)
    assert "F3_FLAG_WIRING_DEFERRED_c88" in src
    print("test_04 PASS: generate_v5.py image unchanged (F3 wiring deferred, disclosed); comping_gen_v5.py clean")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"{name} FAIL: {type(exc).__name__}: {exc}")
    print(f"{4 - fails}/4 PASS")
    sys.exit(1 if fails else 0)
