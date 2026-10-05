#!/usr/bin/python3
"""v6 Phase 5 tests — corpus_accompaniment_v6 (the vocal-free reference) + scorecard per-reference gates + chords_v6 parsimony gate.

Run: /usr/bin/python3 -m pytest tests/test_v6_corpus_accomp.py -q
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
from scripts.v6 import corpus_accompaniment_v6 as ca  # noqa: E402
from scripts.v6 import scorecard as sc  # noqa: E402
from scripts.v6.rules import chords_v6 as C  # noqa: E402


def test_sum_stems_scales_only_when_clipping() -> None:
    n = 2205
    a = {"drums": np.full(n, 0.3, np.float32), "bass": np.full(n, 0.3, np.float32), "other": np.full(n, 0.3, np.float32)}
    y, gain, peak = ca.sum_stems(a)
    assert gain == 1.0 and abs(peak - 0.9) < 1e-6 and abs(float(y.max()) - 0.9) < 1e-6 and y.dtype == np.float32
    b = dict(a, other=np.full(n, 0.5, np.float32))
    y2, gain2, peak2 = ca.sum_stems(b)
    assert abs(peak2 - 1.1) < 1e-6 and abs(gain2 - ca.PEAK_CEILING / 1.1) < 1e-6 and abs(float(np.abs(y2).max()) - ca.PEAK_CEILING) < 1e-6
    # unequal lengths: truncated to the shortest, vocals never summed
    c = dict(a, drums=np.zeros(n - 100, np.float32), vocals=np.ones(n, np.float32))
    y3, _, _ = ca.sum_stems(c)
    assert len(y3) == n - 100 and abs(float(y3.max()) - 0.6) < 1e-6


def test_build_writes_wavs_and_manifest(tmp_path) -> None:
    stems = tmp_path / "stems"
    sr = 22050
    for sha in ("aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb"):
        (stems / sha).mkdir(parents=True)
        t = np.arange(sr) / sr
        for k, f in (("drums", 110.0), ("bass", 55.0), ("other", 440.0), ("vocals", 880.0)):
            sf.write(str(stems / sha / f"{k}.wav"), (0.3 * np.sin(2 * np.pi * f * t)).astype(np.float32), sr, subtype="PCM_16")
    man = {"schema_version": 1, "songs": {s: {"audio_path": f"corpus/{s}.mp3", "band": 5, "title": s.upper()} for s in ("aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb")}}
    (stems / "manifest.json").write_text(json.dumps(man))
    out = tmp_path / "accomp"
    rec = ca.build(stems / "manifest.json", out, log=lambda *a: None)
    assert rec["n_songs"] == 2 and sorted(rec["songs"]) == ["aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb"]
    x, sr2 = sf.read(str(out / "aaaaaaaaaaaaaaaa.wav"), dtype="float32")
    assert sr2 == sr and x.ndim == 1 and len(x) == sr
    t = np.arange(sr) / sr
    expect = 0.3 * (np.sin(2 * np.pi * 110 * t) + np.sin(2 * np.pi * 55 * t) + np.sin(2 * np.pi * 440 * t))
    assert np.abs(x - expect).max() < 2e-4, "sum of drums+bass+other, vocals excluded, 16-bit"
    items = ca.reference_items(out / "manifest.json")
    assert len(items) == 2 and items[0]["label"] == "AAAAAAAAAAAAAAAA" and items[0]["sha16"] == rec["songs"]["aaaaaaaaaaaaaaaa"]["sha16"]
    # a second build keeps the files (same sha16) and is idempotent on the manifest's song ids
    rec2 = ca.build(stems / "manifest.json", out, log=lambda *a: None)
    assert {s: v["sha16"] for s, v in rec2["songs"].items()} == {s: v["sha16"] for s, v in rec["songs"].items()}


def test_gates_for_reference_falls_back_to_full_mix_floor() -> None:
    gates = {"schema_version": sc.GATES_SCHEMA_VERSION, "backbones": {"clap": {"a": 1}},
             "references": {"corpus_accomp": {"backbones": {"clap": {"a": 2}}}}}
    assert sc.gates_for_reference(gates, "corpus") == ({"clap": {"a": 1}}, "backbones")
    assert sc.gates_for_reference(gates, "musdb") == ({"clap": {"a": 1}}, "backbones")
    assert sc.gates_for_reference(gates, "corpus_accomp") == ({"clap": {"a": 2}}, "references.corpus_accomp")
    assert sc.gates_for_reference({"backbones": {"clap": {}}}, "corpus_accomp") == ({"clap": {}}, "backbones")


def test_store_gates_adds_reference_block(tmp_path) -> None:
    from test_v6_scorecard_driver import fake_summary
    gates_path = tmp_path / "gates.json"
    base = sc.derive_gates(fake_summary(), "fake/summary.json")
    gates_path.write_text(json.dumps(base))
    summ = fake_summary()
    summ["backbones"]["mert"]["split_half"]["aggregate"]["c2st_balanced_accuracy"]["p97_5"] = 0.61
    out = ca.store_gates(summ, gates_path, tmp_path / "summary.json", log=lambda *a: None)
    g = json.loads(gates_path.read_text())
    assert g["schema_version"] == sc.GATES_SCHEMA_VERSION and g["backbones"] == base["backbones"], "the full-mix floor is untouched"
    ref = g["references"]["corpus_accomp"]
    assert ref["backbones"]["mert"]["c2st_balanced_accuracy"]["threshold"] == 0.61 and ref["reference"] == "corpus_accomp"
    assert out["references"]["corpus_accomp"]["backbones"]["clap"]["kid_song"]["p97_5"] == 2e-4


def test_parsimony_gate_clamps_rich_states_without_extra_tone_energy() -> None:
    # beat 0: a clean C major triad (C E G) -> every rich C state is gated below the best triad; beat 1: C E G B at equal
    # energy -> C:maj7 keeps its cosine and wins; beat 2: C F G (sus) with the 4th above the 3rd -> C:sus allowed
    bc = np.zeros((3, 12))
    bc[0, [0, 4, 7]] = 1.0
    bc[1, [0, 4, 7, 11]] = 1.0
    bc[2, [0, 5, 7]] = 1.0
    bc += 0.05  # leaky floor
    U = C.unit_chroma(bc)
    raw = U @ C.TEMPLATES.T
    adj, gated = C.parsimony_gate(U, raw)
    i_maj, i_maj7, i_sus, i_7 = (C.STATE_INDEX[(0, q)] for q in ("maj", "maj7", "sus", "7"))
    assert gated[0, i_maj7] and gated[0, i_sus] and gated[0, i_7] and not gated[0, i_maj]
    assert adj[0, i_maj7] < adj[0, i_maj] and int(np.argmax(adj[0])) == i_maj
    assert not gated[1, i_maj7] and int(np.argmax(adj[1])) == i_maj7 and adj[1, i_maj7] == raw[1, i_maj7]
    assert not gated[2, i_sus] and int(np.argmax(adj[2])) == i_sus
    long = np.repeat(bc, 8, axis=0)  # 8 beats per chord so Viterbi's self-transition prior does not override the emissions
    rec = C.recognise(long, np.full(24, -10.0))
    assert [C.STATES[int(s)] for s in rec["path"][::8]] == [(0, "maj"), (0, "maj7"), (0, "sus")] and len(set(rec["path"][:8])) == 1
    assert rec["parsimony_changed_argmax_fraction"] is not None and 0.0 <= rec["gated_state_fraction"] <= 1.0
    # the bias the gate removes: a triad whose 7th bin leaks at half the triad level (> 0.464x, the analytic cosine break-even
    # for a 4- vs 3-note binary template) is a maj7 by plain cosine, but 0.5 < margin 0.6 so the gate hands it back to the triad
    leaky = np.zeros((1, 12)); leaky[0, [0, 4, 7]] = 1.0; leaky[0, 11] = 0.5
    Ul = C.unit_chroma(leaky); rawl = Ul @ C.TEMPLATES.T; adjl, gl = C.parsimony_gate(Ul, rawl)
    assert int(np.argmax(rawl[0])) == i_maj7 and gl[0, i_maj7] and int(np.argmax(adjl[0])) == i_maj
    leaky[0, 11] = 0.7  # above the margin: a real maj7 keeps winning
    Ul = C.unit_chroma(leaky); rawl = Ul @ C.TEMPLATES.T; adjl, gl = C.parsimony_gate(Ul, rawl)
    assert not gl[0, i_maj7] and int(np.argmax(adjl[0])) == i_maj7
