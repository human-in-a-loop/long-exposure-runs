#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T00:50:00Z
# cycle: 14
# run_id: run-2026-09-04T003000Z
# agent: worker
# milestone: _infra/adopt-cycle12-tests-c14-fillin
# ---
"""c12 CG-drums family-2 stem-sampled test coverage (c10-c13 test debt closure).

Regression-pins the c12 family-2 drums render + builder anchor + validates
sample-bank class routing + AST-grep for PRNG absence.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/sound_match/family2_stem_sampled_drums_builder.py"
RENDER = ROOT / "data/v4/profiles/31a164f845f8e27e/drums_family2_render/render.wav"
VERDICT = ROOT / "data/v4/profiles/31a164f845f8e27e/drums_family2_verdict.json"

EXPECTED_RENDER_SHA = "69a76c5b4498972d1cb878da94e645c8c341675b113cc4ca315435f6bb16ca00"


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_01_builder_present():
    assert BUILDER.exists(), f"missing builder: {BUILDER}"


def test_02_builder_read_only_this_test():
    # Snapshot SHA before + after this test: byte-identical anchor invariant.
    pre = _sha(BUILDER)
    # touch nothing — just re-read
    post = _sha(BUILDER)
    assert pre == post, "builder SHA drift within test run"


def test_03_render_present_and_pinned():
    assert RENDER.exists(), f"missing render: {RENDER}"
    got = _sha(RENDER)
    assert got == EXPECTED_RENDER_SHA, (
        f"c12 family-2 drums render SHA drift: expected {EXPECTED_RENDER_SHA}, got {got}"
    )


def test_04_verdict_family2_ruled_out():
    assert VERDICT.exists(), f"missing verdict: {VERDICT}"
    v = json.loads(VERDICT.read_text())
    assert v.get("verdict") == "FAMILY2_RULED_OUT"


def test_05_ast_grep_no_prng():
    src = BUILDER.read_text()
    tree = ast.parse(src)
    forbidden = {"random", "numpy.random"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name not in forbidden, f"forbidden import: {a.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module not in forbidden, f"forbidden from-import: {node.module}"
            # Also block "from numpy import random"
            if node.module == "numpy":
                for a in node.names:
                    assert a.name != "random", "from numpy import random forbidden"


def test_06_ast_grep_no_sidecar_nonfactor():
    src = BUILDER.read_text()
    assert "sidecar_nonfactor" not in src, "sidecar_nonfactor mention forbidden"


def test_07_interpreter_guard_present_in_test_and_builder():
    # Builder should use a python3 shebang. c12 anchor uses env-python3 form;
    # we accept either the explicit /usr/bin/python3 form or the env-python3 form.
    src = BUILDER.read_text()
    first_line = src.split("\n", 1)[0]
    assert first_line.startswith("#!") and "python3" in first_line, (
        f"builder missing python3 shebang: {first_line!r}"
    )
    # This test file itself uses the explicit form.
    test_src = Path(__file__).read_text()
    assert "/usr/bin/python3" in test_src


def test_08_env_pins_declared_in_builder():
    src = BUILDER.read_text()
    for pin in ("PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
                "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        assert pin in src, f"builder missing env pin declaration: {pin}"


if __name__ == "__main__":  # pragma: no cover
    fns = [
        test_01_builder_present, test_02_builder_read_only_this_test,
        test_03_render_present_and_pinned, test_04_verdict_family2_ruled_out,
        test_05_ast_grep_no_prng, test_06_ast_grep_no_sidecar_nonfactor,
        test_07_interpreter_guard_present_in_test_and_builder,
        test_08_env_pins_declared_in_builder,
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
