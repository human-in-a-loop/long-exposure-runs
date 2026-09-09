#!/usr/bin/python3
"""c84 landing tests — content gate fixture + refusal in all three rules scripts, harmony full-corpus enum, groove held-out
fold determinism, generator byte-det, hook-at-birth baseline extension, discipline.

created: 2026-09-09T21:50:00Z
cycle: 84
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle84-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c84_landing.py
"""
from __future__ import annotations

import ast
import hashlib
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
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
NEW_SCRIPTS = ["scripts/v5/content_gate_v5.py", "scripts/v5/content_blocked.py", "scripts/v5/hook_at_birth_c84.py", "scripts/v5/restart_driver_c84.py",
               "scripts/v5/groove_v5_full_c84.py", "scripts/v5/generate_v5.py", "scripts/v5/deliver_v5_listening.py"]
TEMPO_BLOCKED_C80_SHA_PREFIX = "2fbabc07849dbe23"


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _fixture_corpus() -> Path:
    td = Path(tempfile.mkdtemp(prefix="c84_fixture_"))
    (td / "recanonicalization_blocked.json").write_text(json.dumps({"blocked_songs": {}}))
    (td / "content_blocked.json").write_text(json.dumps({"blocked_songs": {"fixture_nonmusic": {"verdict": "NON_MUSIC_CONTENT_R1_AND_R2"}}}))
    return td


def test_01_content_gate_fixture_rules() -> None:
    from scripts.v5.content_gate_v5 import classify
    td = Path(tempfile.mkdtemp(prefix="c84_gate_"))
    nm = td / "nm"; nm.mkdir()
    (nm / "transcription_manifest.json").write_text(json.dumps({"note_counts": {k: {"n_note_on": 0} for k in ("full_mix", "drums", "bass", "guitar", "other", "piano")} | {"vocals": {"n_note_on": 300}}}))
    mu = td / "mu"; mu.mkdir()
    (mu / "transcription_manifest.json").write_text(json.dumps({"note_counts": {k: {"n_note_on": 5} for k in ("full_mix", "drums", "bass", "guitar", "other", "piano", "vocals")}}))
    r1 = classify({"sha16": "nm", "title": "Some Interview", "band": 7}, td)
    r2 = classify({"sha16": "mu", "title": "Let's Talk About Love", "band": 6}, td)  # title hit, notes present -> NOT blocked
    r3 = classify({"sha16": "zz", "title": "A Podcast", "band": 6}, td)  # not landed
    assert r1["blocked"] and r1["verdict"] == "NON_MUSIC_CONTENT_R1_AND_R2"
    assert not r2["blocked"] and r2["verdict"] == "R2_ONLY_NOT_BLOCKED"
    assert not r3["blocked"] and r3["verdict"] == "R2_PENDING_TRANSCRIPTION"
    print("test_01 PASS: fixture R1/R2 semantics")


def test_02_content_gate_output_exactly_expected_and_tempo_file_untouched() -> None:
    pre = _ROOT / "data/v5/corpus/content_gate_prereg_c84.json"
    out = _ROOT / "data/v5/corpus/content_blocked.json"
    assert pre.stat().st_mtime < out.stat().st_mtime
    d = json.loads(out.read_text())
    assert sorted(d["blocked_songs"]) == ["ae1b65eaf1560951"] and d["matches_expectation"] and d["prereg_sha256"] == _sha(pre)
    b = d["blocked_songs"]["ae1b65eaf1560951"]
    assert b["verdict"] == "NON_MUSIC_CONTENT_R1_AND_R2" and b["note_counts"]["vocals"] > 0 and b["sidecar_present"] and b["hook_at_birth"]
    # c86 re-pin (disclosed): the operator F4 adjudication amended the tempo-blocked file IN PLACE (additive unblocked_c86 block);
    # the c80-c85 bytes live on as data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json and must still carry the c80 sha.
    assert _sha("data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json").startswith(TEMPO_BLOCKED_C80_SHA_PREFIX)
    tb = json.loads(Path("data/v5/corpus/recanonicalization_blocked.json").read_text())
    assert sorted(tb["blocked_songs"]) == ["88d247468cb6d49f", "cdd2717e52820ff6"] and sorted(tb["unblocked_c86"]) == ["88d247468cb6d49f", "cdd2717e52820ff6"]
    print(f"test_02 PASS: content gate blocks exactly ae1b65eaf1560951; c80-c85 tempo-blocked bytes preserved as stale copy ({TEMPO_BLOCKED_C80_SHA_PREFIX}…); c86 amended file carries unblocked_c86")


def test_03_refusal_in_all_three_rules_scripts() -> None:
    td = _fixture_corpus()
    from scripts.v5 import harmony_v5 as H
    try:
        H.analyse_song("fixture_nonmusic", td)
        raise AssertionError("harmony did not refuse")
    except H.ContentBlockedError:
        pass
    for cmd in (["/usr/bin/python3", "scripts/v5/groove_v5.py", "--corpus-dir", str(td), "--songs", "fixture_nonmusic", "--out", str(td / "g.json")],
                ["/usr/bin/python3", "scripts/v5/groove_v5_v2.py", "--corpus-dir", str(td), "--train", "fixture_nonmusic", "--heldout", "x", "--out", str(td / "g2.json")]):
        r = subprocess.run(cmd, capture_output=True, text=True)
        assert r.returncode != 0 and "ContentBlockedError" in r.stderr and "MISSING_REINDEX" not in r.stderr, (cmd[1], r.stderr[-300:])
    print("test_03 PASS: harmony_v5 / groove_v5 / groove_v5_v2 refuse before reading any MIDI")


def test_04_harmony_full_corpus_enum_and_prereg() -> None:
    pre = _ROOT / "data/v5/rules/harmony_prereg_c84.json"
    out = _ROOT / "data/v5/rules/harmony_markov_v5_full.json"
    assert pre.stat().st_mtime < out.stat().st_mtime
    h = json.loads(out.read_text())
    assert h["degeneracy_verdict"] in ("NON_DEGENERATE", "DEGENERATE") and h["cycle"] == 84
    assert h["gate"]["content_blocked_skipped"] == ["ae1b65eaf1560951"] and set(h["gate"]["blocked_skipped"]) == {"88d247468cb6d49f", "cdd2717e52820ff6"}
    assert h["gate"]["n_used"] >= 18 and all("excluded_beat_fraction" in v for v in h["per_song"].values())
    assert h["degeneracy_thresholds"]["max_stationary_mass_lt"] == 0.60
    # c82 anchor untouched
    c82 = json.loads((_ROOT / "data/v5/rules/harmony_markov_v5.json").read_text())
    assert c82["gate"]["n_used"] == 3 and c82["cycle"] == 82
    assert (_ROOT / "data/v5/rules/fig_harmony_full_c84.png").exists()
    print(f"test_04 PASS: harmony full corpus n={h['gate']['n_used']} verdict {h['degeneracy_verdict']} max {h['max_stationary_mass']}")


def test_05_groove_heldout_fold_deterministic() -> None:
    from scripts.v5.groove_v5_full_c84 import fold, FOLD_TAG
    pre = _ROOT / "data/v5/rules/groove_prereg_c84.json"
    out = _ROOT / "data/v5/rules/groove_v5_v2_full.json"
    assert pre.stat().st_mtime < out.stat().st_mtime
    g = json.loads(out.read_text())
    train, held, ranks = fold(g["gate"]["eligible"])
    assert held == g["fold"]["heldout"] and train == g["fold"]["train"] and len(held) == 3
    assert held == sorted(g["gate"]["eligible"], key=lambda s: hashlib.sha256(f"{FOLD_TAG}|{s}".encode()).hexdigest())[:3]
    assert g["verdict"] in ("GROOVE_V2_GENERALIZES", "GROOVE_V2_OVERFITS", "GROOVE_V2_DEGENERATE")
    assert "ae1b65eaf1560951" not in g["gate"]["eligible"] and "88d247468cb6d49f" not in g["gate"]["eligible"]
    assert (_ROOT / "data/v5/rules/fig_groove_v2_full_c84.png").exists()
    print(f"test_05 PASS: fold {held} deterministic; verdict {g['verdict']} singleton {g['singleton_context_fraction']}")


def test_06_generator_replay_proofs_and_form_repetition() -> None:
    it = _ROOT / "data/v5/gen/iteration_01"
    roll = json.loads((it / "iteration_rollup.json").read_text())
    assert len(roll["songs"]) == 5 and roll["harmony_verdict"] == "NON_DEGENERATE"
    for s in roll["songs"]:
        d = it / f"{s['generated_song_id']}_donor_{s['donor']}"
        pr = json.loads((d / "ab_mix.replay_proof.json").read_text())
        assert pr["verdict"] == "REPLAY_PROOF_HOLDS" and pr["run1_sha256"] == pr["run2_sha256"] == _sha(d / "ab_mix.wav")
        m = json.loads((d / "ab_mix.manifest.json").read_text())
        ch = m["chord_sequence"]
        assert ch[0:4] == ch[4:8] == ch[12:16] and m["form_plan"] == ["A", "A", "B", "A"]  # forced literal repetition
        # c85: generate_v5.py evolved additively (--form-plan); the c84 manifests pin the c84 script sha (3fbd98ca…) and the c85
        # flag-off replay reproduces their WAV SHAs (tests/test_c85_landing.py test_05) — so accept the pinned c84 hash here.
        assert m["env_pin_sha256"] == ENV_PIN and m["seed"] == 0 and m["generator_hash"] in (_sha("scripts/v5/generate_v5.py"), "3fbd98ca308ffb8b1dc82cb72b46ce86e9de62bf14f974391f24806c7a33390a")
        assert m["rules_sha256"]["harmony_chain"] == _sha("data/v5/rules/harmony_markov_v5_full.json")
        assert not list((d / "per_track").glob("*.wav")), "per-track WAVs must be deleted after the mix (score-and-delete)"
    sc = json.loads((_ROOT / "data/v5/gen/stall_counter.json").read_text())
    assert sc["iterations"] >= 1 and sc["budget"] == 12 and sc["passers"] == 0 and sc["history"][0]["iteration"] == 1  # c85: counter advances by design
    print(f"test_06 PASS: 5/5 REPLAY_PROOF_HOLDS; A A B A literal repetition; stall {sc['iterations']}/12 (iteration-1 entry present)")


def test_07_hook_at_birth_baseline_extension() -> None:
    r = json.loads((_ROOT / "data/v5/corpus/hook_at_birth_c84.json").read_text())
    assert len(r["baseline_known_at_c83_close"]) == 9 and "1d9ac896511ebcd4" in r["baseline_known_at_c83_close"]
    assert len(r["new_landings_since_c83"]) >= 15 and r["all_new_hook_at_birth"] is True and r["catch_up_is_noop"]
    assert not set(r["new_landings_since_c83"]) & set(r["baseline_known_at_c83_close"])
    print(f"test_07 PASS: {len(r['new_landings_since_c83'])} post-c83 landings, all hook_at_birth")


def test_08_discipline_ast_and_guards() -> None:
    bad_mods = {"random", "numpy.random"}
    for p in NEW_SCRIPTS:
        src = Path(p).read_text()
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                assert not any(a.name in bad_mods for a in n.names), p
            if isinstance(n, ast.ImportFrom):
                assert n.module not in bad_mods and "sidecar_nonfactor" not in (n.module or ""), p
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                assert n.func.attr not in {"get_state", "save_state", "save_preset", "load_state", "set_state"}, (p, n.func.attr)
        assert "/usr/bin/python3" in src.splitlines()[0]
    print(f"test_08 PASS: discipline on {len(NEW_SCRIPTS)} c84 scripts")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"{name} FAIL: {e!r}")
    print(f"{8 - fails}/8 PASS")
    sys.exit(1 if fails else 0)
