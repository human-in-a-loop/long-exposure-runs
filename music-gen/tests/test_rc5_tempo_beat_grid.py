#!/usr/bin/env python3
"""Tests for RC5 tempo/beat-grid implementation (c53 clone-2).

Target: >=12/15 green. Run: PYTHONPATH=. /usr/bin/python3 tests/test_rc5_tempo_beat_grid.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/recreate_v2"))

RUBRIC_DOC = ROOT / "docs/rc5_tempo_beat_grid_rubric.md"
RUBRIC_PIN = ROOT / "data/rc5_impl/rubric_hash.txt"
SCRIPT = ROOT / "scripts/recreate_v2/rc5_tempo_beat_grid.py"
VERDICT = ROOT / "data/rc5_impl/verdict.json"
BYTE_DET = ROOT / "data/rc5_impl/byte_determinism.json"
ANCHOR = ROOT / "data/rc5_impl/anchor_preservation.json"

FOCUS_SHAS = [
    "31a164f845f8e27e",
    "cdd2717e52820ff6",
    "51e433ade2a845e1",
    "252eb21ce7df7328",
    "88d247468cb6d49f",
]

CHICKEN_GREASE = "31a164f845f8e27e"


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, msg: str = "") -> None:
    results.append((name, cond, msg))


# 01 — rubric doc mtime < script mtime (pre-registration gate)
def t01():
    doc_m = RUBRIC_DOC.stat().st_mtime
    scr_m = SCRIPT.stat().st_mtime
    check("01_rubric_mtime_before_script", doc_m < scr_m,
          f"doc_m={doc_m} script_m={scr_m}")


# 02 — three-way rubric_hash byte-equality chain
def t02():
    doc_sha = sha256(RUBRIC_DOC)
    pin_sha = RUBRIC_PIN.read_text().strip()
    v = json.loads(VERDICT.read_text())
    ok = doc_sha == pin_sha == v["rubric_hash"]
    check("02_three_way_rubric_hash_chain", ok,
          f"doc={doc_sha[:16]} pin={pin_sha[:16]} v={v['rubric_hash'][:16]}")


# 03 — verdict is one of the frozen values
def t03():
    v = json.loads(VERDICT.read_text())
    check("03_verdict_enum", v["verdict"] in {"RC5_LANDS", "RC5_PARTIAL", "RC5_FAILS"},
          f"got {v['verdict']}")


# 04 — 5 focus songs present in verdict
def t04():
    v = json.loads(VERDICT.read_text())
    ids = [r["song_id"] for r in v["per_song"]]
    check("04_five_focus_songs", set(ids) == set(FOCUS_SHAS), f"{sorted(ids)}")


# 05 — Chicken Grease included (mandatory)
def t05():
    v = json.loads(VERDICT.read_text())
    ids = [r["song_id"] for r in v["per_song"]]
    check("05_chicken_grease_present", CHICKEN_GREASE in ids)


# 06 — Octave-correction algebra: variant index selects smallest |diff|
def t06():
    from rc5_tempo_beat_grid import octave_correct
    corrected, label, idx = octave_correct(100.0, 200.0)
    check("06_octave_double_selected", (idx == 1 and label == "double" and abs(corrected - 200.0) < 1e-9),
          f"corr={corrected} label={label} idx={idx}")


# 07 — Deterministic index tiebreak: smallest index wins on tie
def t07():
    from rc5_tempo_beat_grid import octave_correct
    # raw=100, baseline=100 -> all variants at [100, 200, 50]; diffs [0, 100, 50] -> idx 0
    corrected, label, idx = octave_correct(100.0, 100.0)
    check("07_deterministic_tiebreak_smallest_idx", (idx == 0 and label == "none"))


# 08 — Per-song PASS threshold logic
def t08():
    v = json.loads(VERDICT.read_text())
    for r in v["per_song"]:
        want = "PASS" if r["abs_diff_vs_baseline"] <= 2.0 else "FAIL"
        if r["verdict"] != want:
            check(f"08_threshold_{r['song_id']}", False,
                  f"got {r['verdict']} want {want}")
            return
    check("08_threshold_all_songs", True)


# 09 — Aggregate verdict from per-song counts
def t09():
    from rc5_tempo_beat_grid import aggregate_verdict
    ok = (aggregate_verdict([{"verdict": "PASS"}] * 3) == "RC5_LANDS"
          and aggregate_verdict([{"verdict": "PASS"}, {"verdict": "FAIL"}] * 1 + [{"verdict": "FAIL"}]) == "RC5_PARTIAL"
          and aggregate_verdict([{"verdict": "FAIL"}] * 5) == "RC5_FAILS")
    check("09_aggregate_verdict_logic", ok)


# 10 — Every per-song rc5_tempo_estimate.json has required schema keys
def t10():
    keys = {"song_id", "raw_estimate", "corrected_estimate", "octave_correction_applied",
            "baseline_bpm", "abs_diff_vs_baseline", "sample_rate", "hop_length",
            "start_bpm", "tightness"}
    for sha in FOCUS_SHAS:
        p = ROOT / f"data/rc5_impl/{sha}/rc5_tempo_estimate.json"
        if not p.exists():
            check(f"10_schema_{sha}", False, "missing file")
            return
        d = json.loads(p.read_text())
        missing = keys - set(d.keys())
        if missing:
            check(f"10_schema_{sha}", False, f"missing {missing}")
            return
    check("10_per_song_schema", True)


# 11 — merged_retempo.{midi,musicxml} exist per song
def t11():
    for sha in FOCUS_SHAS:
        for f in ("merged_retempo.midi", "merged_retempo.musicxml"):
            p = ROOT / f"data/rc5_impl/{sha}/{f}"
            if not p.exists():
                check(f"11_artifact_{sha}_{f}", False, "missing")
                return
    check("11_retempo_artifacts_present", True)


# 12 — Byte-determinism × 2 all_equal True
def t12():
    d = json.loads(BYTE_DET.read_text())
    check("12_byte_determinism_all_equal", d["all_equal"] is True)


# 13 — Anchor preservation: c49 v1 + c50 v2 rubric SHAs unchanged
def t13():
    d = json.loads(ANCHOR.read_text())
    by_path = {e["path"]: e for e in d["entries"]}
    v2 = by_path["docs/m_recreate_2_accurate_small_set_rubric_v2.md"]["sha256"]
    v2_pin = by_path["data/recreate_v2/rubric_hash_v2.txt"]["sha256"]
    ok = (v2 == "0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f"
          and v2_pin is not None)
    check("13_v2_rubric_anchor_preserved", ok, f"v2={v2[:16] if v2 else None}")


# 14 — NO PRNG (AST-grep on the script)
def t14():
    src = SCRIPT.read_text()
    tree = ast.parse(src)
    forbidden = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            # detect random.*, np.random.*, numpy.random.*, torch.rand*
            chain = []
            cur = node
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                chain.append(cur.id)
            joined = ".".join(reversed(chain))
            for bad in ("random.", "np.random.", "numpy.random.", "torch.rand"):
                if bad in joined:
                    forbidden.add(joined)
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "random":
                    forbidden.add("import random")
    check("14_no_prng", not forbidden, f"found {forbidden}")


# 15 — /usr/bin/python3 interpreter guard present
def t15():
    src = SCRIPT.read_text()
    check("15_interpreter_guard",
          "/usr/bin/python3" in src and "_interpreter_guard" in src)


for fn in [t01, t02, t03, t04, t05, t06, t07, t08, t09, t10, t11, t12, t13, t14, t15]:
    try:
        fn()
    except Exception as e:
        results.append((fn.__name__, False, f"EXC {type(e).__name__}: {e}"))

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\n=== RC5 tempo/beat-grid tests: {passed}/{total} PASS ===")
for name, ok, msg in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {msg}")

sys.exit(0 if passed >= 12 else 1)
