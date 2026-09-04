#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T00:50:00Z
# cycle: 14
# run_id: run-2026-09-04T003000Z
# agent: worker
# milestone: _infra/adopt-cycle13-tests-c14-fillin
# ---
"""c13 CG-guitar stage-1 SF2 coarse sweep test coverage (c13 test debt).

Regression-pins the c13 leaderboard + run_manifest SHAs + top-1 program 24
+ source-of-truth program 27 rank + AST-grep discipline invariants.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/sound_match/coarse_sweep_sf2_guitar.py"
LEADERBOARD = ROOT / "data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage1/leaderboard.tsv"
MANIFEST = ROOT / "data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage1/run_manifest.json"

# On-disk anchors pinned at c14 test authoring.
EXPECTED_LEADERBOARD_SHA = "0ee5e767edff8dcb2864d5466f331a4ffacca7f5fa4b64949684dcb1db052bfc"
EXPECTED_MANIFEST_SHA = "5a3cf11d1241228823039c0bd14d7e8e890edd043963e868a38092f9b355ac0f"
EXPECTED_SCRIPT_SHA = "9ddf692f0a903875bbae537bebba6265649b4bfb4dec6b979084a4cb42e96055"


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_01_script_present_and_pinned():
    assert SCRIPT.exists(), f"missing script: {SCRIPT}"
    got = _sha(SCRIPT)
    assert got == EXPECTED_SCRIPT_SHA, (
        f"c13 guitar coarse sweep SHA drift: expected {EXPECTED_SCRIPT_SHA}, got {got}"
    )


def test_02_leaderboard_pinned():
    assert LEADERBOARD.exists(), f"missing leaderboard: {LEADERBOARD}"
    got = _sha(LEADERBOARD)
    assert got == EXPECTED_LEADERBOARD_SHA, (
        f"leaderboard SHA drift: expected {EXPECTED_LEADERBOARD_SHA}, got {got}"
    )


def test_03_manifest_pinned():
    assert MANIFEST.exists(), f"missing manifest: {MANIFEST}"
    got = _sha(MANIFEST)
    assert got == EXPECTED_MANIFEST_SHA, (
        f"manifest SHA drift: expected {EXPECTED_MANIFEST_SHA}, got {got}"
    )


def _read_leaderboard():
    rows = []
    with open(LEADERBOARD) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            rows.append(r)
    return rows


def test_04_eight_rows_distinct_render_shas():
    rows = _read_leaderboard()
    assert len(rows) == 8, f"expected 8 rows, got {len(rows)}"
    shas = {r["render_sha"] for r in rows}
    assert len(shas) == 8, f"expected 8/8 distinct render SHAs, got {len(shas)}"


def test_05_top_1_prog_24_nylon():
    rows = _read_leaderboard()
    top = rows[0]
    assert int(top["program"]) == 24, f"top-1 expected prog 24, got {top['program']}"


def test_06_prog_27_rock_rank_2():
    rows = _read_leaderboard()
    prog_to_rank = {int(r["program"]): int(r["rank"]) for r in rows}
    assert prog_to_rank.get(27) == 2, (
        f"program 27 (Rock Guitar source-of-truth) expected rank 2, "
        f"got {prog_to_rank.get(27)}"
    )


def test_07_spread_ratio_ge_2_79():
    rows = _read_leaderboard()
    composites = [float(r["composite"]) for r in rows]
    ratio = max(composites) / min(composites)
    assert ratio >= 2.79, f"spread ratio {ratio:.3f} < 2.79 (Rung-3 spread PASS)"


def test_08_ast_grep_no_prng():
    src = SCRIPT.read_text()
    tree = ast.parse(src)
    forbidden = {"random", "numpy.random"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name not in forbidden, f"forbidden import: {a.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module not in forbidden, f"forbidden from-import: {node.module}"
            if node.module == "numpy":
                for a in node.names:
                    assert a.name != "random", "from numpy import random forbidden"


def test_09_ast_grep_no_sidecar_nonfactor_and_interpreter_guard():
    src = SCRIPT.read_text()
    assert "sidecar_nonfactor" not in src, "sidecar_nonfactor forbidden"
    assert "/usr/bin/python3" in src, "interpreter guard missing"


def test_10_manifest_env_pins_present():
    m = json.loads(MANIFEST.read_text())
    envp = m.get("env_pins", {})
    for k in ("PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
              "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        assert k in envp, f"manifest env_pins missing {k}"


if __name__ == "__main__":  # pragma: no cover
    fns = [
        test_01_script_present_and_pinned, test_02_leaderboard_pinned,
        test_03_manifest_pinned, test_04_eight_rows_distinct_render_shas,
        test_05_top_1_prog_24_nylon, test_06_prog_27_rock_rank_2,
        test_07_spread_ratio_ge_2_79, test_08_ast_grep_no_prng,
        test_09_ast_grep_no_sidecar_nonfactor_and_interpreter_guard,
        test_10_manifest_env_pins_present,
    ]
    n_ok = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
            n_ok += 1
        except AssertionError as e:
            print(f"FAIL {fn.__name__}: {e}")
    print(f"{n_ok}/{len(fns)} passed")
    sys.exit(0 if n_ok == len(fns) else 1)
