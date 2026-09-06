#!/usr/bin/python3
"""c80 P5 tests for scripts/v5/harmony_v5.py (>=2 named cases).

created: 2026-09-06T16:30:00Z
cycle: 80
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle80-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_harmony_v5.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v5 import harmony_v5 as H  # noqa: E402


def _chord_notes(root: int, intervals, beats: int = 4, octave: int = 60):
    return [(float(b), float(b + 1), octave + root + iv, 100) for b in range(beats) for iv in intervals]


def test_01_template_matching_recovers_c_maj7() -> None:
    notes = _chord_notes(0, (0, 4, 7, 11))
    pcp = H.beat_pcps(notes)
    assert pcp.shape == (4, 12)
    for b in range(4):
        m = H.match_beat("test", b, pcp[b])
        assert (m["root"], m["quality"]) == (0, "maj7"), m
        assert abs(m["sim"] - 1.0) < 1e-6
    assert H.match_beat("test", 0, np.zeros(12))["quality"] == "N"
    print("test_01 PASS: synthetic C-maj7 -> (root 0, maj7, sim 1.0); zero beat -> N")


def test_02_transposition_invariance_of_functional_states() -> None:
    prog = [(0, (0, 4, 7)), (9, (0, 3, 7)), (5, (0, 4, 7)), (7, (0, 4, 7, 10))]  # I vi IV V7 in C
    states_by_shift = []
    for shift in (0, 2, 5, 9):
        notes = []
        for i, (root, ivs) in enumerate(prog):
            notes += [(float(i), float(i + 1), 60 + (root + shift) % 12 + iv, 100) for iv in ivs]
        pcp = H.beat_pcps(notes)
        key = H.estimate_key(pcp.sum(axis=0))
        assert key["mode"] == "major" and key["tonic"] == shift % 12, (shift, key)
        st = []
        for b in range(len(pcp)):
            m = H.match_beat("test", b, pcp[b])
            st.append(f"{(m['root'] - key['tonic']) % 12}:{m['quality']}")
        states_by_shift.append(st)
    assert all(s == states_by_shift[0] for s in states_by_shift), states_by_shift
    assert states_by_shift[0] == ["0:maj", "9:min", "5:maj", "7:7"]
    print(f"test_02 PASS: I-vi-IV-V7 invariant under 4 transpositions -> {states_by_shift[0]}")


def test_03_markov_degeneracy_thresholds_pre_declared() -> None:
    streams = {"a": ["0:maj"] * 10, "b": ["0:maj"] * 10}
    segs = {"a": ["0:maj"], "b": ["0:maj"]}
    mk = H.markov(streams, segs)
    assert mk["degeneracy_verdict"] == "DEGENERATE" and mk["max_stationary_mass"] == 1.0
    assert mk["degeneracy_thresholds"] == {"max_stationary_mass_lt": 0.60, "min_distinct_qualities": 4, "min_quality_segment_count": 8}
    cyc = ["0:maj", "9:min", "5:maj7", "7:7", "2:min7", "0:sus"]
    streams = {"a": cyc * 20}
    segs = {"a": cyc * 20}
    mk = H.markov(streams, segs)
    assert mk["degeneracy_verdict"] == "NON_DEGENERATE" and mk["max_stationary_mass"] < 0.60
    assert len(mk["qualities_with_count_ge_threshold"]) >= 4
    out = _ROOT / "data/v5/rules"
    gated, full = out / "harmony_v5_gated.json", out / "harmony_markov_v5.json"
    assert gated.exists() or full.exists(), "P3 must have written either the gated record or the corpus chain"
    if full.exists():
        d = json.loads(full.read_text())
        assert d["degeneracy_verdict"] in ("DEGENERATE", "NON_DEGENERATE") and d["gate"]["n_used"] >= 3
    else:
        d = json.loads(gated.read_text())
        assert d["verdict"] == "GATED_INSUFFICIENT_UNBLOCKED_SONGS" and d["n_used"] < 3
    print(f"test_03 PASS: pre-declared degeneracy thresholds; on-disk P3 record = {'chain' if full.exists() else 'gated'}")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} harmony_v5 tests PASS")
