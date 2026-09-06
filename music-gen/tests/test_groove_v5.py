#!/usr/bin/python3
"""c81 P5 tests for scripts/v5/groove_v5.py (synthetic backbeat corpus reproduces the ratio; degenerate fixture rejected).

created: 2026-09-06T17:20:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle81-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_groove_v5.py
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
from scripts.v5 import groove_v5 as G  # noqa: E402


def _mask(*pos: int) -> int:
    return sum(1 << p for p in pos)


def _model(bars: list) -> dict:
    return {"kick_marginal": G.table([("*", b["kick"]) for b in bars]),
            "snare_given_kick": G.table([(str(b["kick"]), b["snare"]) for b in bars]),
            "hat_given_kick_snare": G.table([(f"{b['kick']}|{b['snare']}", b["hat"]) for b in bars]),
            "bass_given_kick": G.table([(str(b["kick"]), b["bass"]) for b in bars])}


def test_01_synthetic_backbeat_corpus_reproduces_statistics() -> None:
    """10 kick variants (>= 8 contexts), snare ALWAYS on 4 and 12, bass on the kicks -> backbeat 1.0, lock 1.0."""
    bars = []
    for v in range(10):
        kick = _mask(0, 8) | (1 << (v + 1)) if v + 1 not in (4, 8, 12) else _mask(0, 8, 14 - v)
        for rep in range(3):
            bars.append({"bar": len(bars), "kick": kick, "snare": _mask(4, 12), "hat": _mask(*range(0, 16, 2)), "bass": kick})
    cs = G.stats(bars)
    assert cs["backbeat_ratio"] == 1.0 and cs["bass_kick_lock"] == 1.0 and cs["distinct_kick_patterns"] >= 8
    m = _model(bars)
    assert all(m[k]["n_contexts"] >= 8 for k in ("snare_given_kick", "hat_given_kick_snare", "bass_given_kick"))
    smp = G.sample(m, 64)
    ss = G.stats(smp)
    assert ss["backbeat_ratio"] == 1.0 and ss["bass_kick_lock"] == 1.0 and ss["distinct_kick_patterns"] >= 3
    assert G.sample(m, 64) == smp, "SHA-256 inverse-CDF sampling must be deterministic"
    print(f"test_01 PASS: synthetic corpus backbeat 1.0 / lock 1.0 reproduced on 64 sampled bars ({ss['distinct_kick_patterns']} distinct kicks)")


def test_02_degenerate_fixture_rejected_by_pre_declared_rule() -> None:
    bars = [{"bar": i, "kick": _mask(0, 8), "snare": _mask(4, 12), "hat": 0, "bass": _mask(0)} for i in range(20)]
    m = _model(bars)
    smp = G.sample(m, 64)
    ss = G.stats(smp)
    ctx = {k: m[k]["n_contexts"] for k in ("snare_given_kick", "hat_given_kick_snare", "bass_given_kick")}
    degenerate = (ss["distinct_kick_patterns"] < G.MIN_DISTINCT or ss["distinct_bass_patterns"] < G.MIN_DISTINCT
                  or any(n < G.MIN_CONTEXTS for n in ctx.values()))
    assert degenerate and ss["distinct_kick_patterns"] == 1 and all(n == 1 for n in ctx.values())
    on_disk = json.loads((_ROOT / "data/v5/rules/groove_v5.json").read_text())
    assert on_disk["verdict"] in on_disk["pre_declared"]["enum"]
    blocked = json.loads((_ROOT / "data/v5/corpus/recanonicalization_blocked.json").read_text())["blocked_songs"]
    assert not set(on_disk["songs"]) & set(blocked), "groove model must never consume blocked songs"
    assert on_disk["pre_declared"]["degeneracy"] == {"min_distinct_kick_patterns": 3, "min_distinct_bass_patterns": 3, "min_contexts_per_table": 8}
    if on_disk["verdict"] != "GROOVE_DEGENERATE":
        assert all(n >= 8 for n in on_disk["table_context_counts"].values())
        assert on_disk["sample_stats"]["distinct_kick_patterns"] >= 3 and on_disk["sample_stats"]["distinct_bass_patterns"] >= 3
    print(f"test_02 PASS: single-pattern fixture -> degenerate (1 context per table); on-disk verdict {on_disk['verdict']} on {on_disk['songs']}")


def test_03_hash_uniform_and_inverse_cdf() -> None:
    u1, u2 = G.hash_uniform("groove_v5|0|kick|*"), G.hash_uniform("groove_v5|0|kick|*")
    assert u1 == u2 and 0.0 <= u1 < 1.0 and G.hash_uniform("x") != G.hash_uniform("y")
    row = {"1": 0.25, "2": 0.5, "3": 0.25}
    assert G.draw(row, 0.0) == 1 and G.draw(row, 0.3) == 2 and G.draw(row, 0.9) == 3 and G.draw(row, 0.999999) == 3
    assert G.popcount(_mask(4, 12)) == 2 and G.bits(_mask(4, 12)) == [4, 12]
    print("test_03 PASS: SHA-256 uniform deterministic in [0,1); inverse-CDF draw correct on boundaries")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} groove_v5 tests PASS")
