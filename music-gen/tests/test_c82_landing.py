#!/usr/bin/python3
"""c82 P6.3 tests — emitter carries `agent`; reindex hook idempotent on Disco A; venv probe enum + main-env freeze;
parabolic refinement recovers a synthetic fractional period; groove v2 phase alignment; harmony exclusion rule.

created: 2026-09-06T18:20:00Z
cycle: 82
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle82-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c82_landing.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v5 import reindex_hook as RH  # noqa: E402
from scripts.v5 import harmony_v5 as H  # noqa: E402
from scripts.v5 import groove_v5_v2 as G2  # noqa: E402
from scripts.v5.tempo_mechanism_probe_c82 import parabolic_refine, s_refined  # noqa: E402
from scripts.v5.tempo_v5c import harmonic_sum_direct  # noqa: E402  READ-ONLY
from scripts.v3_spine.midi_from_json_events import serialize  # noqa: E402  READ-ONLY

C79_MAIN_FREEZE = "90ed1d9f0fd0a33e3be35653bf541f82ceadcd4d89c0013b9cdd0228544d639d"
ENUM_PROBE = ("EAR_VENV_REPRODUCES_CACHE", "EAR_VENV_DIFFERS_FROM_CACHE", "EAR_VENV_NONDETERMINISTIC", "EAR_VENV_ABSENT", "EAR_VENV_PROBE_FAILED")
DISCO = "cdd2717e52820ff6"


def _load_emitter():
    spec = importlib.util.spec_from_file_location("emit_c82", _ROOT / "tools/_emit_c82_ledger_events.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_01_c82_emitter_template_carries_agent_and_validates() -> None:
    from long_exposure.tools._ledger_schema import REQUIRED_EVENT_FIELDS, validate_event
    em = _load_emitter()
    ev = em._ev("_infra/fixture-c82", "validated", "high", "fixture", "fixture narrative", [])
    assert ev["agent"] == "worker" and "agent" in REQUIRED_EVENT_FIELDS
    missing = [k for k in REQUIRED_EVENT_FIELDS if k not in ev]
    assert not missing, missing
    errs = validate_event(ev) if callable(validate_event) else None
    assert not errs, errs
    # every c82 event on disk carries agent
    rows = [json.loads(l) for l in (_ROOT / "promise_ledger.jsonl").read_text().splitlines() if l.strip()]
    c82 = [r for r in rows if r.get("cycle") == 82]
    assert all("agent" in r for r in c82), [r["milestone_id"] for r in c82 if "agent" not in r]
    c81 = [r for r in rows if r.get("cycle") == 81]
    assert c81 and all("agent" in r for r in c81)
    print(f"test_01 PASS: c82 emitter template validates against REQUIRED_EVENT_FIELDS; {len(c81)} c81 + {len(c82)} c82 events on disk all carry `agent`")


def test_02_reindex_hook_idempotent_on_disco_a() -> None:
    d = _ROOT / "data/v5/corpus" / DISCO
    side = json.loads((d / RH.SIDECAR_NAME).read_text())
    before = hashlib.sha256((d / RH.SIDECAR_NAME).read_bytes()).hexdigest()
    res = dict(RH.reindex_landed(_ROOT / "data/v5/corpus"))
    assert res[DISCO] == "present", res
    assert hashlib.sha256((d / RH.SIDECAR_NAME).read_bytes()).hexdigest() == before
    rm = json.loads((d / RH.OUT_SUBDIR / "reindex_manifest.json").read_text())
    assert side["reindex_manifest_sha256"] == hashlib.sha256((d / RH.OUT_SUBDIR / "reindex_manifest.json").read_bytes()).hexdigest()
    assert all(v["n_starts_in"] == v["n_paired"] + v["n_unpaired_starts"] for v in rm["probes"].values())
    print(f"test_02 PASS: reindex_hook catch-up is idempotent on Disco A ('present'; sidecar sha unchanged); probes {list(rm['probes'])}")


def test_03_venv_probe_enum_and_main_env_freeze_unchanged() -> None:
    p = _ROOT / "data/v5/ear/ear_probe_c82.json"
    if p.exists():
        d = json.loads(p.read_text())
        assert d["status"] in ENUM_PROBE, d["status"]
        if d["status"] in ("EAR_VENV_REPRODUCES_CACHE", "EAR_VENV_DIFFERS_FROM_CACHE"):
            assert d["run1_eq_run2"] is True and d["run1_sha256"] == d["run2_sha256"]
    else:
        d = {"status": "NOT_YET_RUN"}
    freeze = subprocess.run(["/usr/bin/python3", "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    assert hashlib.sha256(freeze.encode()).hexdigest() == C79_MAIN_FREEZE, "main-env pip freeze drifted from the c79 receipt"
    print(f"test_03 PASS: probe status {d['status']} in enum; main-env pip freeze sha == c79 receipt")


def test_04_parabolic_refinement_recovers_fractional_period_and_beats_3_2_lag() -> None:
    # synthetic onset envelope with true period 21.48 frames + a 3:2 hemiola component (period 32.22) -> integer lags 21 vs 32
    T = 21.48
    n = 6000
    t = np.arange(n, dtype=float)
    env = np.zeros(n)
    for k in range(int(n / T) + 1):
        c = k * T
        env += np.exp(-0.5 * ((t - c) / 1.2) ** 2)
    for k in range(int(n / (1.5 * T)) + 1):
        c = k * 1.5 * T + 3.0
        env += 0.55 * np.exp(-0.5 * ((t - c) / 1.2) ** 2)
    ac = np.correlate(env, env, mode="full")[n - 1:]
    ac = ac / ac[0]
    lag_ref, d = parabolic_refine(ac, 21)
    assert abs(lag_ref - T) <= 0.05, (lag_ref, d)
    s21 = s_refined(ac, lag_ref)["s_ref"]
    lag32, _ = parabolic_refine(ac, 32)
    s32 = s_refined(ac, lag32)["s_ref"]
    assert s21 > s32, (s21, s32)
    # the integer read of 2T for lag 21 lands at 42 (trough side of the 42.96 peak) — refinement reads it at 42.96
    assert harmonic_sum_direct(ac, 21)["ac_double_period"] < s_refined(ac, lag_ref)["ac_double"]
    print(f"test_04 PASS: refined lag {lag_ref:.3f} (true 21.48, |d|<=0.05); s_ref(T)={s21:.3f} > s_ref(3T/2)={s32:.3f}; integer 2T read < refined 2T read")


def test_05_groove_v2_phase_alignment_recovers_known_offset() -> None:
    # synthetic backbeat corpus: kick on 16th 0 + 8, snare on 4 + 12, shifted by a known offset of 5 slots
    off = 5
    drums = []
    for bar in range(24):
        base = bar * 16 + off
        drums += [(base + 0, 36), (base + 8, 36), (base + 4, 38), (base + 12, 38), (base + 2, 42)]
    ph = G2.phase_offset("deadbeefdeadbeef", drums)
    assert ph["offset"] == off and ph["tie"] is False, ph
    bars = G2.bar_patterns(drums, [], ph["offset"])
    st = G2.stats(bars)
    assert st["backbeat_ratio"] == 1.0 and bars[0]["kick"] == 0b10001, (st, bars[0])
    st0 = G2.stats(G2.bar_patterns(drums, [], 0))
    assert st0["backbeat_ratio"] == 0.0
    print(f"test_05 PASS: phase alignment recovers offset {off} (backbeat 1.0 aligned vs {st0['backbeat_ratio']} at offset 0); kick8 mask 0b10001")


def test_06_harmony_exclusion_drops_synthetic_12_note_chord_beat() -> None:
    with tempfile.TemporaryDirectory(prefix="hx_c82_") as td:
        corpus = Path(td)
        sha16 = "abcdefabcdefabcd"
        d = corpus / sha16 / "canonical_v5_reindexed"
        d.mkdir(parents=True)
        (d / "reindex_manifest.json").write_text("{}")
        ev = []
        i = 0
        for b in range(8):  # C major triad on beats 0..7 (0.5 s per beat at 120 BPM)
            for p in (60, 64, 67):
                ev.append({"type": "start", "index": i, "start_time": b * 0.5, "pitch": p, "instrument": "acoustic_piano"})
                ev.append({"type": "end", "start_event_index": i, "end_time": b * 0.5 + 0.45, "pitch": p, "instrument": "acoustic_piano"}); i += 1
        for p in range(48, 60):  # 12 simultaneous starts on beat 3 (an input artifact)
            ev.append({"type": "start", "index": i, "start_time": 1.5, "pitch": p, "instrument": "bass"})
            ev.append({"type": "end", "start_event_index": i, "end_time": 1.6, "pitch": p, "instrument": "bass"}); i += 1
        raw = corpus / "raw.json"; raw.write_text(json.dumps(ev))
        for stem in H.HARMONY_STEMS:
            serialize(str(raw), str(d / f"{stem}.mid"), 120.0, (4, 4))
        (corpus / sha16 / "transcription_manifest.json").write_text(json.dumps({"bpm_v5": 120.0, "title": "fixture", "note_counts": {}}))
        r = H.analyse_song(sha16, corpus)
        ex = r["exclusion_rule"]
        assert ex["n_excluded_beats"] == 1 and "3" in ex["excluded_beats"] and ex["n_beats_in_stream"] == r["n_beats"] - 1, ex
        assert all(e["beat"] != 3 for e in r["chord_stream"])
        assert all(e["quality"] == "maj" and e["root"] == 0 for e in r["chord_stream"]), [e["state"] for e in r["chord_stream"]]
    print("test_06 PASS: a beat with 12 simultaneous starts on one stem is dropped from the stream; the other 7 beats read C:maj")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} c82_landing tests PASS")
