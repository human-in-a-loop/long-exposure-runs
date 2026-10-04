#!/usr/bin/python3
"""v6 rules tests — groove_v6: bitmasks match groove_v5_v2.bar_patterns, SHA-ranked fold, held-out log-likelihood, lean tables
(rounded probs rows still sum to 1; variants carry counts only), and the written composer file (schema, verdict, sizes).

Run: /usr/bin/python3 tests/test_v6_rules_groove.py      or      /usr/bin/python3 -m pytest tests/test_v6_rules_groove.py -q
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

from scripts.v5 import groove_v5_v2 as G  # noqa: E402
from scripts.v6.rules import groove_v6 as GV  # noqa: E402

V5_FILE = _ROOT / "data/v5/rules/groove_v5_v2_full.json"
V6_FILE = _ROOT / "data/v6/rules/groove_v6.json"
VAR_FILE = _ROOT / "data/v6/rules/groove_v6_variants.json"
GM = {"kick": 36, "snare": 38, "hat": 42}


def _streams() -> dict:
    """Three bars: backbeat + hats, one bar with a kick-only pickup, bass locked to kicks; bar 5 has only bass (not a corpus bar)."""
    kick = [[0, 0], [0, 8], [1, 0], [1, 7], [1, 8], [2, 0], [2, 10], [3, 1]]
    snare = [[0, 4], [0, 12], [1, 4], [1, 12], [2, 4], [2, 12], [2, 14]]
    hat = [[b, s] for b in range(3) for s in range(0, 16, 2)]
    bass = [[0, 0], [0, 8], [1, 0], [1, 6], [2, 0], [2, 11], [5, 0]]
    pad = lambda rows: [[b, s, 0.0, 0.0, -20.0] for b, s in rows]  # noqa: E731
    return {"kick": pad(kick), "snare": pad(snare), "hat": pad(hat), "bass": pad(bass)}


def _v5_bars(streams: dict) -> list:
    drums = sorted((b * 16 + s, GM[k]) for k in ("kick", "snare", "hat") for b, s, *_ in streams[k])
    bass = sorted((b * 16 + s, 40) for b, s, *_ in streams["bass"])
    return G.bar_patterns(drums, bass, 0)


def test_01_bitmasks_match_groove_v5_v2_bar_patterns() -> None:
    st = _streams()
    ours, ref = GV.bars_from_streams(st), _v5_bars(st)
    assert ours == ref, (ours, ref)
    assert [b["bar"] for b in ours] == [0, 1, 2, 3] and ours[1]["kick"] == 0b00011001  # 8th alphabet: slots 0, 7, 8 -> bits 0, 3, 4
    assert ours[0]["snare"] == (1 << 4) | (1 << 12) and ours[2]["bass"] == (1 << 0) | (1 << 11)
    assert all(b["bar"] != 5 for b in ours), "a bass-only bar is not a corpus bar"
    print("test_01 PASS: bitmasks == groove_v5_v2.bar_patterns on the aligned grid")


def test_02_fold_is_sha_ranked_and_disjoint() -> None:
    elig = [f"{i:016x}" for i in range(12)]
    train, held, ranks = GV.fold(elig)
    assert len(held) == 3 and not set(train) & set(held) and sorted(train + held) == elig
    assert held == sorted(elig, key=lambda s: GV.SC.sha_rank(GV.FOLD_TAG, s))[:3] and all(len(v) == 16 for v in ranks.values())
    assert GV.fold(list(reversed(elig)))[1] == held, "fold is independent of input order"
    print(f"test_02 PASS: fold held-out {held}")


def test_03_loglik_joint_beats_independent_and_oov_floor() -> None:
    bars = GV.bars_from_streams(_streams()) * 4
    model, indep = GV.build_model(bars), GV.independent_model(bars)
    ll_j, ll_i = GV.loglik(model, bars), GV.loglik_independent(indep, bars)
    assert ll_j["n_bars"] == 16 and ll_j["n_oov_outcomes"] == 0 and ll_j["loglik_per_bar"] > ll_i["loglik_per_bar"], (ll_j, ll_i)
    assert abs(sum(ll_j["per_stream_per_bar"].values()) - ll_j["loglik_per_bar"]) < 1e-6
    lp, oov = GV._logp(model["snare_given_kick"], "17", 0xFFFF)  # unseen outcome in a seen context -> alpha floor
    tbl = model["snare_given_kick"]
    n_row = sum(tbl["counts"]["17"].values())
    assert oov and abs(lp - GV.math.log(tbl["alpha"] / (n_row + tbl["alpha"] * len(tbl["vocab"])))) < 1e-12
    print(f"test_03 PASS: LL/bar joint {ll_j['loglik_per_bar']} > independent {ll_i['loglik_per_bar']}; OOV floor ok")


def test_04_round_probs_keeps_rows_and_variant_has_no_probs() -> None:
    bars = GV.bars_from_streams(_streams()) * 3
    model = GV.build_model(bars)
    lean = GV.round_probs(model)
    for t, tbl in model.items():
        assert set(lean[t]) == set(tbl) and set(lean[t]["probs"]) == set(tbl["probs"]) and lean[t]["counts"] == tbl["counts"]
        for ctx, row in lean[t]["probs"].items():
            assert set(row) == set(tbl["vocab"]) and abs(sum(row.values()) - 1.0) < 1e-6 and all(len(str(p).split(".")[-1]) <= GV.PROB_DECIMALS for p in row.values())
    songs = {"a": {"bars": bars, "band": 5, "bpm_v5": 100.0}}
    var = GV._variant(["a"], songs, 100.0)
    assert var["n_bars"] == len(bars) and all("probs" not in tbl and "counts" in tbl and "vocab" in tbl for tbl in var["model"].values())
    assert var["sample_stats"]["n_bars"] == G.N_SAMPLE
    print("test_04 PASS: rounded rows sum to 1 over the vocabulary; variant tables are counts-only")


def test_05_backbeat_block_and_inventory() -> None:
    bars = GV.bars_from_streams(_streams())
    bb = GV.backbeat_block(bars)
    assert bb["n_bars"] == 4 and bb["snare_on_both_backbeats_frac"] == 0.75
    assert bb["kick_on_downbeat_frac"] == 1.0, "slot 1 folds into 8th-note bit 0 (v5 kick alphabet)"
    inv = GV.inventory(bars, top_n=2)
    assert len(inv["kick"]) == 2 and inv["kick"][0]["count"] >= inv["kick"][1]["count"] and len(inv["snare"][0]["pattern"]) == 16 and len(inv["kick"][0]["pattern"]) == 8
    assert GV.pattern_str(0b1001, 8) == "x..x...."
    print(f"test_05 PASS: backbeat {bb['snare_on_both_backbeats_frac']} kick-on-1 {bb['kick_on_downbeat_frac']}; top kick {inv['kick'][0]['pattern']}")


def test_06_written_files_schema_verdict_and_size() -> None:
    if not (V5_FILE.exists() and V6_FILE.exists()):
        print("test_06 SKIP: groove files not built yet")
        return
    v5 = json.loads(V5_FILE.read_text())
    assert v5["schema_version"] == 1 and v5["verdict"] in G.ENUM and v5["verdict"] != "GROOVE_V2_DEGENERATE", v5["verdict"]
    assert v5["n_heldout_songs"] == 3 and v5["n_train_songs"] + 3 == len(v5["per_song"]) == v5["gate"]["n_eligible"]
    for t in ("kick_marginal",) + GV.COND:
        tbl = v5["model"][t]
        assert set(tbl["probs"]) == set(tbl["counts"]) and tbl["vocab"] == sorted(tbl["vocab"], key=int) and tbl["n_contexts"] == len(tbl["counts"])
        ctx = next(iter(tbl["probs"]))
        assert set(tbl["probs"][ctx]) == set(tbl["vocab"]) and abs(sum(tbl["probs"][ctx].values()) - 1.0) < 1e-6
    assert all("bars" not in r and "inventory" not in r for r in v5["per_song"].values()), "composer file carries no per-song bar lists"
    ll = v5["heldout_loglik"]
    assert ll["heldout_joint"]["n_bars"] == v5["n_heldout_bars"] and ll["heldout_conditional_gain_per_bar"] is not None
    v6 = json.loads(V6_FILE.read_text())
    assert v6["verdict"] == v5["verdict"] and v6["n_songs"] == len(v5["per_song"]) and set(v6["per_song"]) == set(v5["per_song"])
    assert v6["pooled_all"]["backbeat"]["n_bars"] == sum(r["n_bars"] for r in v6["per_song"].values())
    sizes = {p.name: p.stat().st_size for p in (V5_FILE, V6_FILE, VAR_FILE) if p.exists()}
    assert sizes[V6_FILE.name] < 5_000_000 and sizes.get(VAR_FILE.name, 0) < 30_000_000, sizes
    print(f"test_06 PASS: verdict {v5['verdict']}; heldout {v5['fold']['heldout']}; sizes {sizes}")


if __name__ == "__main__":
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)):
        fn()
    print("ALL PASS")
