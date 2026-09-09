#!/usr/bin/python3
"""c86 worker P1 tests — F4 CLOSE: operator-adopted BPMs + eligibility (the operator-required test), canonical_v5c_reindexed
tempo meta + lossless note counts, harmony n=23 prereg mtime gate + enum, c84 chain unchanged, --tempo-overrides asserts the
v5c dir, additive unblock rule, discipline on the new scripts.

created: 2026-09-09T23:40:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F4-tempo-fix

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c86_f4_close.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")

import mido  # noqa: E402

PD, DA = "88d247468cb6d49f", "cdd2717e52820ff6"
ADOPTED = {PD: 122.197271, DA: 120.272335}
C84_ANCHOR = "a984ee17b1b8e2cf7529b95eff5650c66188b6d8578f31862c3f7e2c73305232"
C84_GROOVE = "faa0e76e4866e370896adc4a87d4ace31b497bb654df6e1a48d044e5234022da"
STALE_PREFIX = "2fbabc07849dbe23"
GUIDANCE_PREFIX = "8677bb0cd3f240a0"
PROBES = ["drums", "bass", "guitar", "other", "piano", "vocals", "full_mix"]
NEW_SCRIPTS = ["scripts/v5/recanonicalize_tempo_v5.py", "scripts/v5/harmony_v5.py", "scripts/v5/groove_v5_v2.py",
               "data/v5/rules/groove_v5_full_c86.py", "data/v5/rules/plot_harmony_n23_vs_n21_c86.py"]
CORPUS = _ROOT / "data/v5/corpus"


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _j(p) -> dict:
    return json.loads((_ROOT / p).read_text())


def test_01_adopted_bpms_and_both_songs_eligible() -> None:
    """The operator-required test: adopted BPMs read from the resolution JSON, and both songs eligible at n=23."""
    r = _j("data/v5/corpus/tempo_f4_operator_resolution_c86.json")
    assert r["adopted_bpm"] == ADOPTED and r["authority"] == "OPERATOR" and r["cycle"] == 86
    assert r["guidance"]["sha256"] == _sha(r["guidance"]["path"]) and r["guidance"]["sha256"].startswith(GUIDANCE_PREFIX)
    assert "DECISION: adopt 122.197271 (PD) and 120.272335 (Disco A)" in r["adjudication_text_verbatim"]
    assert r["supersedes"]["path"] == "data/v5/corpus/tempo_f4_verdict_c85.json" and r["supersedes"]["sha256"] == _sha(r["supersedes"]["path"])
    assert r["c22_anchor_bpm"] == {PD: 123.046875, DA: 120.18531976744185}
    assert all(abs(ADOPTED[s] - r["c22_anchor_bpm"][s]) < 1.0 for s in ADOPTED)  # two independent estimators agree within 1 BPM
    e = _j("data/v5/rules/eligible_c86.json")["gate"]
    assert PD in e["used"] and DA in e["used"] and e["n_used"] == len(e["used"]) == 23 and e["cycle"] == 86
    assert e["blocked_skipped"] == [] and e["content_blocked_skipped"] == ["ae1b65eaf1560951"] and e["n_landed"] == 26
    assert set(e["used"]) == set(_j("data/v5/rules/eligible_c84.json")["gate"]["used"]) | {PD, DA}
    assert sorted(e["late_landed_deferred"]) == ["0e1e8f20592db366", "cc0693b4a24f64b2"]
    assert e["tempo_overrides"]["sha256"] == _sha(e["tempo_overrides"]["path"]) and _j(e["tempo_overrides"]["path"]) == ADOPTED
    ov = _j("data/v5/corpus/tempo_overrides_c86.json")
    assert ov == ADOPTED
    print(f"test_01 PASS: adopted PD {ADOPTED[PD]} / Disco A {ADOPTED[DA]} (OPERATOR, guidance {GUIDANCE_PREFIX}…); both in eligible_c86 gate.used (n=23)")


def test_02_v5c_tempo_meta_and_lossless_counts() -> None:
    for s, bpm in ADOPTED.items():
        d = CORPUS / s / "canonical_v5c_reindexed"
        man = json.loads((d / "reindex_manifest.json").read_text())
        side = _j(f"data/v5/corpus/{s}/canonical_v5c_reindexed_sha256.json")
        assert man["bpm_v5c_adopted"] == bpm == side["adopted_bpm"] and man["bpm_v5_superseded"] == 80.749512 and man["authority"]["kind"] == "OPERATOR"
        tm = _j(f"data/v5/corpus/{s}/transcription_manifest.json")
        assert side["bars_at_adopted_bpm"] == round(tm["duration_s"] * bpm / 240.0, 6)
        for p in PROBES:
            m = mido.MidiFile(str(d / f"{p}.mid"))
            assert m.ticks_per_beat == 480
            tempos = [msg.tempo for tr in m.tracks for msg in tr if msg.type == "set_tempo"]
            # SMF set_tempo is an integer microsecond count: exact on the integer; the float round-trip is quantized (~2.5e-4 BPM),
            # so the brief's 1e-6 tolerance is asserted on |bpm2tempo| identity + a quantization-bounded round-trip (disclosed).
            assert tempos and all(t == mido.bpm2tempo(bpm) for t in tempos), (s, p, tempos)
            assert abs(mido.tempo2bpm(tempos[0]) - bpm) <= 5e-4
            n_on = sum(1 for tr in m.tracks for msg in tr if msg.type == "note_on" and msg.velocity > 0)
            n_json = sum(1 for e in json.loads((CORPUS / s / "muscriptor_full" / f"{p}.json").read_text()) if e.get("type") == "start")
            assert n_on == n_json == man["probes"][p]["n_midi_note_on"] == tm["note_counts"][p]["n_note_on"], (s, p, n_on, n_json)
            assert _sha(d / f"{p}.mid") == side["midi_sha256"][p]
        assert side["reindex_manifest_sha256"] == _sha(d / "reindex_manifest.json")
        # c80 dir untouched: its sidecar still describes its bytes
        old = _j(f"data/v5/corpus/{s}/canonical_v5_reindexed_sha256.json")
        assert all(_sha(CORPUS / s / "canonical_v5_reindexed" / f"{p}.mid") == old["midi_sha256"][p] for p in PROBES)
    bd = _j("data/v5/corpus/byte_determinism_c86.json")["recanonicalize_tempo_v5"]
    assert bd["equal"] and bd["script_sha256_final_image_saved_before_runs"] == bd["script_sha256_after_runs"] == _sha("scripts/v5/recanonicalize_tempo_v5.py")
    print("test_02 PASS: v5c set_tempo == bpm2tempo(adopted) on 14 probe files; note_on == JSON starts == manifest counts; c80 dir untouched; byte-det x2")


def test_03_harmony_prereg_mtime_gate_and_enum() -> None:
    pre, out = _ROOT / "data/v5/rules/harmony_prereg_c86.json", _ROOT / "data/v5/rules/harmony_markov_v5_full_c86.json"
    assert pre.stat().st_mtime < out.stat().st_mtime
    p, ck = json.loads(pre.read_text()), json.loads(out.read_text())
    enum = "HARMONY_NONDEGENERATE" if ck["degeneracy_verdict"] == "NON_DEGENERATE" else "HARMONY_DEGENERATE"
    assert enum in p["enum"] == ["HARMONY_NONDEGENERATE", "HARMONY_DEGENERATE"]
    assert ck["gate"] == _j("data/v5/rules/eligible_c86.json")["gate"] and ck["gate"]["n_used"] == 23 and ck["cycle"] == 86
    assert ck["tempo_overrides_c86"]["overrides"] == ADOPTED and sorted(ck["tempo_overrides_c86"]["applied_to"]) == [PD, DA]
    assert p["held_constant"]["exclusion_threshold"] == 12 and ck["degeneracy_thresholds"]["max_stationary_mass_lt"] == 0.60
    for s in (PD, DA):
        ps = _j(f"data/v5/rules/per_song_c86/{s}/harmony_v5.json")
        assert ps["bpm_v5"] == ADOPTED[s] and ps["midi_dir"].endswith("canonical_v5c_reindexed") and ps["tempo_override_c86"]["bpm_v5_manifest"] == 80.749512
    bd = _j("data/v5/rules/byte_determinism_c86_f4.json")["harmony_n23_c86"]
    assert bd["equal"] and bd["per_song_equal"] and bd["run1_sha256"] == bd["run2_sha256"] == _sha(out) and bd["enum"] == enum
    assert bd["harmony_v5_py_sha256_post_edit"] == _sha("scripts/v5/harmony_v5.py") and bd["prereg_sha256"] == _sha(pre)
    g_pre, g_out = _ROOT / "data/v5/rules/groove_prereg_c86.json", _ROOT / "data/v5/rules/groove_v5_v2_full_c86.json"
    if g_out.exists():
        g = json.loads(g_out.read_text())
        assert g_pre.stat().st_mtime < g_out.stat().st_mtime and g["verdict"] in g["pre_declared"]["enum"] and g["prereg_sha256"] == _sha(g_pre)
        assert set(g["gate"]["used"]) == set(ck["gate"]["used"]) and g["fold"]["tag"] == "groove_fold_c84" and g["n_heldout_songs"] == 3
    print(f"test_03 PASS: harmony prereg predates n=23 chain; {enum} ({ck['degeneracy_verdict']}, {len(ck['states'])} states, max {ck['max_stationary_mass']}); byte-det x2")


def test_04_c84_chain_unchanged() -> None:
    assert _sha("data/v5/rules/harmony_markov_v5_full.json") == C84_ANCHOR
    assert _sha("data/v5/rules/groove_v5_v2_full.json") == C84_GROOVE
    assert _j("data/v5/rules/eligible_c84.json")["gate"] == _j("data/v5/rules/harmony_markov_v5_full.json")["gate"]
    bd = _j("data/v5/rules/byte_determinism_c86_f4.json")
    r = bd["harmony_eligible_from_c84_replay_post_edit"]
    assert r["matches_c84_anchor"] and r["per_song_equal"] and r["replay_sha256"] == C84_ANCHOR and r["n_per_song_compared"] == 21
    assert bd["c84_artifacts_untouched"]["unchanged"] and bd["c84_artifacts_untouched"]["per_song_c84_unchanged"]
    n21, n23 = _j("data/v5/rules/harmony_markov_v5_full.json"), _j("data/v5/rules/harmony_markov_v5_full_c86.json")
    assert n21["states"] == n23["states"] and n21["degeneracy_thresholds"] == n23["degeneracy_thresholds"]
    print(f"test_04 PASS: c84 chain {C84_ANCHOR[:8]}… + groove {C84_GROOVE[:8]}… unchanged; post-edit harmony_v5.py replays the c84 chain byte-identically")


def test_05_tempo_overrides_assert_v5c_dir_and_unblock_rule() -> None:
    from scripts.v5 import harmony_v5 as H
    from scripts.v5 import groove_v5_v2 as G
    assert H.tempo_blocked_effective(CORPUS) == set() and G.tempo_blocked_effective(CORPUS) == set()
    live = _j("data/v5/corpus/recanonicalization_blocked.json")
    assert sorted(live["blocked_songs"]) == [PD, DA] and live["blocked_songs"][PD]["anchor_bpm"] == 123.046875  # generate_v5.donor_tempo source intact
    assert _sha("data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json").startswith(STALE_PREFIX)
    # positive fixture: PD with an override -> served from canonical_v5c_reindexed/ (asserted), bpm overridden
    r = H.analyse_song(PD, CORPUS, {PD: ADOPTED[PD]})
    assert r["midi_dir"].endswith("canonical_v5c_reindexed") and r["bpm_v5"] == ADOPTED[PD] and r["tempo_override_c86"]["midi_dir_asserted"] == "canonical_v5c_reindexed"
    g = G.load_song(CORPUS, PD, {PD: ADOPTED[PD]})
    assert g["midi_dir"].endswith("canonical_v5c_reindexed") and g["bpm_v5"] == ADOPTED[PD]
    # no override -> no override keys (flag-off records byte-identical in shape); v5c still preferred by the tuple
    assert "tempo_override_c86" not in H.analyse_song(PD, CORPUS) and "tempo_override_c86" not in G.load_song(CORPUS, PD)
    # negative fixture: a corpus copy where PD has ONLY canonical_v5_reindexed/ -> TempoOverrideDirError in both loaders
    td = Path(tempfile.mkdtemp(prefix="c86_override_neg_"))
    (td / PD).mkdir()
    shutil.copy(CORPUS / PD / "transcription_manifest.json", td / PD / "transcription_manifest.json")
    shutil.copytree(CORPUS / PD / "canonical_v5_reindexed", td / PD / "canonical_v5_reindexed")
    for fn, err in ((lambda: H.analyse_song(PD, td, {PD: ADOPTED[PD]}), H.TempoOverrideDirError), (lambda: G.load_song(td, PD, {PD: ADOPTED[PD]}), G.TempoOverrideDirError)):
        try:
            fn()
            raise AssertionError("expected TempoOverrideDirError")
        except err as e:
            assert "canonical_v5c_reindexed" in str(e)
    assert H.analyse_song(PD, td)["midi_dir"].endswith("canonical_v5_reindexed")  # without an override the c80 dir is served
    shutil.rmtree(td)
    for s in ("scripts/v5/harmony_v5.py", "scripts/v5/groove_v5_v2.py"):
        h = subprocess.run(["/usr/bin/python3", s, "--help"], capture_output=True, text=True)
        assert h.returncode == 0 and "--tempo-overrides" in h.stdout, s
    print("test_05 PASS: unblock rule effective (blocked_songs historical intact); --tempo-overrides asserts canonical_v5c_reindexed in harmony + groove loaders")


def test_06_discipline_ast_and_guards() -> None:
    bad_mods = {"random", "numpy.random"}
    for p in NEW_SCRIPTS:
        src = Path(p).read_text()
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                assert not any(a.name in bad_mods or "sidecar_nonfactor" in a.name for a in n.names), p
            if isinstance(n, ast.ImportFrom):
                assert n.module not in bad_mods and "sidecar_nonfactor" not in (n.module or ""), p
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                assert n.func.attr not in {"get_state", "save_state", "save_preset", "load_state", "set_state"}, (p, n.func.attr)
        assert "/usr/bin/python3" in src.splitlines()[0] and "SUPPRESS_INTERPRETER_GUARD" in src, p
    for p in ("data/v5/corpus/f4_close_report_c86.md",):
        if Path(p).exists():
            head = Path(p).read_text()[:400]
            assert head.startswith("---") and "cycle: 86" in head and "run_id: run-2026-09-06T000000Z" in head
    print(f"test_06 PASS: discipline on {len(NEW_SCRIPTS)} c86 scripts")


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
