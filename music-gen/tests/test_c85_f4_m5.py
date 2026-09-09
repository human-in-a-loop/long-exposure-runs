#!/usr/bin/python3
"""c85 worker p2 tests — F4 tempo adjudication (prereg mtime gate, enum, blocked file untouched, synthetic half/double check),
M5 harmony --eligible-from reproduces the c84 chain, score_gen_batch_v5 --cycle/--milestone, discipline on the new scripts.

created: 2026-09-09T22:06:53Z
cycle: 85
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle85-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_c85_f4_m5.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("SUPPRESS_INTERPRETER_GUARD", "1")
TEMPO_BLOCKED_C80_SHA_PREFIX = "2fbabc07849dbe23"
C84_ANCHOR = "a984ee17b1b8e2cf7529b95eff5650c66188b6d8578f31862c3f7e2c73305232"
NEW_SCRIPTS = ["scripts/v5/tempo_f4_adjudicate_c85.py", "data/v5/corpus/plot_tempo_f4_c85.py", "scripts/v5/harmony_v5.py", "scripts/v5/score_gen_batch_v5.py"]


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_01_f4_prereg_gate_enum_and_blocked_file_untouched() -> None:
    pre = _ROOT / "data/v5/corpus/tempo_f4_prereg_c85.json"
    out = _ROOT / "data/v5/corpus/tempo_f4_verdict_c85.json"
    assert pre.stat().st_mtime < out.stat().st_mtime
    p, v = json.loads(pre.read_text()), json.loads(out.read_text())
    assert v["verdict"] in p["verdict_enum"] == ["F4_RESOLVED", "F4_HALF_DOUBLE_AMBIGUOUS", "F4_FAILS"]
    assert v["prereg_sha256"] == _sha(pre) and v["authority"]["sha256"] == p["authority"]["sha256"] == _sha(p["authority"]["path"])
    assert sorted(v["per_song"]) == ["88d247468cb6d49f", "cdd2717e52820ff6"] and v["blocked_file_touched"] is False
    assert _sha("data/v5/corpus/recanonicalization_blocked.json").startswith(TEMPO_BLOCKED_C80_SHA_PREFIX)
    assert v["recanonicalization_blocked_sha256"] == _sha("data/v5/corpus/recanonicalization_blocked.json")
    # not resolved -> nothing else written; resolved -> unblocked record exists
    unblocked = (_ROOT / "data/v5/corpus/recanonicalization_unblocked_c85.json").exists()
    assert unblocked == (v["verdict"] == "F4_RESOLVED")
    for s in v["per_song"].values():
        assert s["all_three_pass"] == (s["half_double"]["passes"] and s["onsets_per_beat"]["passes"] and s["anchor"]["passes"])
    bd = json.loads((_ROOT / "data/v5/corpus/byte_determinism_c85.json").read_text())["tempo_f4_verdict_c85"]
    assert bd["equal"] and bd["real_equals_runs"] and bd["run1_sha256"] == _sha(out)
    print(f"test_01 PASS: F4 verdict {v['verdict']}; prereg predates verdict; blocked file {TEMPO_BLOCKED_C80_SHA_PREFIX}… unchanged; byte-det x2 equal")


def test_02_synthetic_half_double_check() -> None:
    from scripts.v5.tempo_f4_adjudicate_c85 import half_double_check, verdict_of
    adopted = {"lag_ref": 21.0, "bpm_ref": 123.0, "s_ref": 1.35}
    failing = [{"lag_ref": 10.5, "bpm_ref": 246.0, "s_ref": 1.19}, adopted, {"lag_ref": 32.0, "bpm_ref": 80.7, "s_ref": 1.20},
               {"lag_ref": 42.0, "bpm_ref": 61.5, "s_ref": 1.40}]  # 3:2 set: 2T scores HIGHER
    r = half_double_check(failing, adopted)
    assert r["half"]["candidate"]["lag_ref"] == 10.5 and r["half"]["scores_lower"] is True
    assert r["double"]["candidate"]["lag_ref"] == 42.0 and r["double"]["scores_lower"] is False and r["passes"] is False
    passing = [{"lag_ref": 10.5, "bpm_ref": 246.0, "s_ref": 1.19}, adopted, {"lag_ref": 32.0, "bpm_ref": 80.7, "s_ref": 1.20},
               {"lag_ref": 42.0, "bpm_ref": 61.5, "s_ref": 1.30}]
    r2 = half_double_check(passing, adopted)
    assert r2["passes"] is True and r2["half"]["scores_lower"] and r2["double"]["scores_lower"]
    # strict inequality: equal s_ref does not score lower; absent 2T candidate fails
    tie = [{"lag_ref": 10.5, "bpm_ref": 246.0, "s_ref": 1.19}, adopted, {"lag_ref": 42.0, "bpm_ref": 61.5, "s_ref": 1.35}]
    assert half_double_check(tie, adopted)["passes"] is False
    absent = [{"lag_ref": 10.5, "bpm_ref": 246.0, "s_ref": 1.19}, adopted]
    ra = half_double_check(absent, adopted)
    assert ra["double"]["candidate"] is None and ra["passes"] is False
    mk = lambda hd, on, an: {"half_double": {"passes": hd}, "onsets_per_beat": {"passes": on}, "anchor": {"passes": an}, "all_three_pass": hd and on and an}  # noqa: E731
    assert verdict_of([mk(True, True, True), mk(True, True, True)]) == "F4_RESOLVED"
    assert verdict_of([mk(False, True, True), mk(True, False, True)]) == "F4_HALF_DOUBLE_AMBIGUOUS"
    assert verdict_of([mk(True, True, True), mk(True, True, False)]) == "F4_FAILS"
    print("test_02 PASS: synthetic 3:2 set -> half/double False; passing set -> True; strict tie False; absent 2T False; verdict enum mapping")


def test_03_harmony_eligible_from_reproduces_c84_chain() -> None:
    e = json.loads((_ROOT / "data/v5/rules/eligible_c84.json").read_text())
    assert len(e["gate"]["used"]) == 21 and e["gate"]["n_used"] == 21 and e["gate"]["cycle"] == 84
    full = json.loads((_ROOT / "data/v5/rules/harmony_markov_v5_full.json").read_text())
    assert e["gate"] == full["gate"] and _sha("data/v5/rules/harmony_markov_v5_full.json") == C84_ANCHOR
    bd = json.loads((_ROOT / "data/v5/rules/byte_determinism_c85.json").read_text())["harmony_eligible_from_c84"]
    assert bd["equal"] and bd["matches_c84_anchor"] and bd["per_song_equal"] and bd["run1_sha256"] == bd["run2_sha256"] == C84_ANCHOR
    assert bd["harmony_markov_v5_full_unchanged"] and "--eligible-from data/v5/rules/eligible_c84.json" in bd["command"]
    h = subprocess.run(["/usr/bin/python3", "scripts/v5/harmony_v5.py", "--help"], capture_output=True, text=True)
    assert h.returncode == 0 and "--eligible-from" in h.stdout
    print("test_03 PASS: --eligible-from x2 == c84 anchor a984ee17…; eligible_c84.json lists 21 songs")


def test_04_score_gen_batch_cycle_milestone_flags() -> None:
    src = Path("scripts/v5/score_gen_batch_v5.py").read_text()
    ast.parse(src)
    h = subprocess.run(["/usr/bin/python3", "scripts/v5/score_gen_batch_v5.py", "--help"], capture_output=True, text=True)
    assert h.returncode == 0 and "--cycle" in h.stdout and "--milestone" in h.stdout, h.stderr[-400:]
    main_src = src[src.index("def main("):]
    assert '"cycle": 83' not in main_src and "informational-c83\"," not in main_src.replace("default=\"M-V5-GEN-1/gen-renders-ear-scored-informational-c83\",", "")
    assert main_src.count("a.cycle") >= 3 and main_src.count("a.milestone") >= 2
    print("test_04 PASS: score_gen_batch_v5 --cycle/--milestone present; main() stamps a.cycle / a.milestone")


def test_05_discipline_ast_and_guards() -> None:
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
        assert "/usr/bin/python3" in src.splitlines()[0] and "SUPPRESS_INTERPRETER_GUARD" in src, p  # docstrings may NAME the bans; imports may not
    print(f"test_05 PASS: discipline on {len(NEW_SCRIPTS)} c85 scripts")


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
