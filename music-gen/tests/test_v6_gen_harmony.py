#!/usr/bin/python3
"""v6 Phase 2 tests — harmony: chain schema parity with v5, backward messages, cadence conditioning on the fixture chain.

Run: /usr/bin/python3 tests/test_v6_gen_harmony.py      or      /usr/bin/python3 -m pytest tests/test_v6_gen_harmony.py -q
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

from scripts.v6.gen import common as C  # noqa: E402
from scripts.v6.gen import harmony as H  # noqa: E402
from scripts.v6.gen import planner as PL  # noqa: E402
from scripts.v6.gen.fixtures import build_fixtures, fixtures_sha256  # noqa: E402

FX = build_fixtures()


def test_01_qualities_match_v5_and_fixture_schema() -> None:
    from scripts.v5.harmony_v5 import QUALITIES as V5Q  # READ-ONLY
    assert dict(C.QUALITIES) == dict(V5Q), "QUALITIES drifted from scripts/v5/harmony_v5.py"
    ch = FX["chain"]
    n = len(ch["states"])
    for k in ("states", "beat_level_counts", "beat_level_row_normalized", "segment_level_counts", "stationary_distribution", "chain_definition", "per_song"):
        assert k in ch, k
    assert len(ch["segment_level_counts"]) == n and all(len(r) == n for r in ch["beat_level_row_normalized"])
    assert abs(sum(ch["stationary_distribution"].values()) - 1.0) < 1e-3
    assert "N" in ch["states"] and all(s == "N" or s.split(":")[1] in C.QUALITIES for s in ch["states"])
    assert fixtures_sha256() == fixtures_sha256(), "fixtures must be deterministic"
    print("test_01 PASS: QUALITIES == v5; fixture chain schema; fixtures deterministic")


def test_02_backward_messages_equal_brute_force_reach_probability() -> None:
    """beta_0(s) with no penultimate mask must equal P(X_{T-1} in FINAL | X_0 = s) = (P^(T-1) 1_FINAL)(s)."""
    states = ["a", "b", "c"]
    P = {"a": {"a": 0.0, "b": 0.7, "c": 0.3}, "b": {"a": 0.5, "b": 0.0, "c": 0.5}, "c": {"a": 0.2, "b": 0.8, "c": 0.0}}
    T = 5
    beta = H.backward_messages([P] * T, states, set(states), {"c"})
    # brute force: vector iteration
    v = {s: 1.0 if s == "c" else 0.0 for s in states}
    for _ in range(T - 1):
        v = {s: sum(P[s][t] * v[t] for t in states) for s in states}
    for s in states:
        assert abs(beta[0][s] - v[s]) < 1e-12, (s, beta[0][s], v[s])
    # the penultimate mask zeroes beta_{T-2} outside PENULT
    beta2 = H.backward_messages([P] * T, states, {"a"}, {"c"})
    assert beta2[T - 2]["b"] == 0.0 and beta2[T - 2]["a"] == P["a"]["c"]
    # 'N' can never be a terminal state
    beta3 = H.backward_messages([{"N": {"N": 0.0, "x": 1.0}, "x": {"N": 1.0, "x": 0.0}}] * 3, ["N", "x"], {"N", "x"}, {"N", "x"})
    assert beta3[2]["N"] == 0.0 and beta3[2]["x"] == 1.0
    print("test_02 PASS: backward messages == P^(T-1) 1_FINAL; penultimate mask; N masked")


def test_03_conditioned_sampling_ends_on_the_cadence_100pct() -> None:
    chain = FX["chain"]
    n_ok = n = 0
    for seed in range(40):
        for cad in PL.CADENCES:
            for hr in ([1, 2, 2, 1], [2, 4, 2, 2], [1, 1, 1, 1], [4, 2, 1, 2]):
                slots = H.phrase_slots(hr, 0)
                r = H.sample_phrase_chords(chain, slots, cad, "major", f"test|{seed}|{cad}|{hr}", prev_state="0:maj" if seed % 2 else None)
                n += 1
                assert r["conditioning_ok"], (cad, r)
                assert r["cadence_realized"] == cad, (cad, r["chords"])
                assert "N" not in r["chords"][-2:]
                # no immediate repeats except at a repeat-allowed slot (hr == 1 bar start)
                for i in range(1, len(r["chords"])):
                    if r["chords"][i] == r["chords"][i - 1]:
                        assert slots[i][2], (hr, r["chords"])
                n_ok += 1
    assert n_ok == n and n == 40 * 4 * 4
    print(f"test_03 PASS: {n_ok}/{n} conditioned phrases realised their planned cadence (4 types x 4 harmonic rhythms x 40 seeds)")


def test_04_cadence_targets_and_classifier() -> None:
    st = FX["chain"]["states"]
    pen, fin = H.cadence_targets("authentic", st, "major")
    assert pen == {"7:7", "7:maj"} and fin == {"0:maj", "0:maj7"}
    assert H.classify_cadence("7:7", "0:maj", st, "major") == "authentic"
    assert H.classify_cadence("5:maj", "0:maj", st, "major") == "plagal"
    assert H.classify_cadence("7:maj", "9:min", st, "major") == "deceptive"
    assert H.classify_cadence("2:min", "7:7", st, "major") == "half"
    assert H.classify_cadence("0:maj", "9:min", st, "major") == "none"
    # minor-mode sets fall back to the root when the chain has no such quality
    pen_m, fin_m = H.cadence_targets("authentic", st, "minor")
    assert fin_m == {"0:maj", "0:maj7"} and pen_m  # fixture chain has no 0:min -> root fallback
    print("test_04 PASS: cadence target sets + classifier")


def test_05_harmonic_rhythm_distribution_learned_and_prior() -> None:
    d, src = PL.harmonic_rhythm_distribution(FX["chord_streams"])
    assert set(d) == {1, 2, 4} and abs(sum(d.values()) - 1.0) < 1e-3 and src.startswith("learned_from_3")
    d0, src0 = PL.harmonic_rhythm_distribution({})
    assert d0 == PL.HR_PRIOR and src0 == "prior"
    plan = PL.build_plan(FX, "t|seed=1", 120.0, 32)
    for lab, lp in plan["label_plans"].items():
        assert len(lp["phrases"]) == 2 and all(h in (1, 2, 4) for h in lp["harmonic_rhythm"])
        for ph in lp["phrases"]:
            assert lp["harmonic_rhythm"][ph["start_bar"] + ph["n_bars"] - 1] in (1, 2), "cadence bar must have <= 2 chords"
            assert ph["cadence"] in PL.CADENCES
    ballad = PL.build_plan(FX, "t|seed=1", 70.0, 32)
    assert ballad["ballad"] and all(len(lp["phrases"]) == 1 and lp["phrases"][0]["n_bars"] == 8 for lp in ballad["label_plans"].values())
    bc = H.beat_chords([{"bar": 0, "beat": 0, "state": "0:maj"}, {"bar": 0, "beat": 2, "state": "7:7"}, {"bar": 1, "beat": 0, "state": "5:maj"}], 2)
    assert bc == [["0:maj", "0:maj", "7:7", "7:7"], ["5:maj"] * 4]
    print(f"test_05 PASS: harmonic rhythm learned {d} / prior; phrase plans; ballad = 1 phrase of 8 bars; beat_chords")


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


def test_06_seventh_mask_zeroes_only_unresolvable_changes_and_keeps_rows_stochastic() -> None:
    """Phase 5: resolvable_matrix removes exactly the changes voicing.seventh_resolvable rejects and renormalises."""
    from scripts.v6.gen.common import seg_matrix
    from scripts.v6.gen.voicing import seventh_resolvable
    P = seg_matrix(FX["chain"])
    M, info = H.resolvable_matrix(P)
    assert set(M) == set(P) and info["n_zeroed"] >= 0
    for s, row in M.items():
        assert abs(sum(row.values()) - 1.0) < 1e-9, s
        for t, p in row.items():
            if not seventh_resolvable(s, t) and s not in info["rows_kept_unmasked"]:
                assert p == 0.0, (s, t)
            elif P[s][t] == 0.0:
                assert p == 0.0
    r = H.sample_phrase_chords(FX["chain"], H.phrase_slots([2, 2, 2, 2], 0), "authentic", "major", "test|mask")
    assert "seventh_mask" in r and r["conditioning_ok"]
    for a, b in zip(r["chords"], r["chords"][1:]):
        assert seventh_resolvable(a, b), (a, b)
    print(f"test_06 PASS: seventh mask zeroed {info['n_zeroed']} transitions, rows stochastic, sampled changes all resolvable")

