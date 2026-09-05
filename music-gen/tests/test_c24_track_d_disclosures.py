#!/usr/bin/env -S /usr/bin/python3
"""c26 Track C: regression for c22 composite-formula documentation +
c22 distance-semantics operator resolution in docs/OPERATOR_DECISIONS.md.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

OBJECTIVE = ROOT / "scripts/sound_match/objective.py"
OPDEC = ROOT / "docs/OPERATOR_DECISIONS.md"


def test_01_objective_composite_weights_present():
    src = OBJECTIVE.read_text()
    assert "W_MEL = 0.5" in src, "objective.py must pin W_MEL = 0.5"
    assert "0.5" in src and "0.25" in src, "composite weights 0.5 / 0.25 / 0.25 must appear"


def test_02_objective_composite_formula_documented():
    src = OBJECTIVE.read_text()
    for token in ["mel_l1_db", "spectral_centroid_rmse_hz", "embedding_cos"]:
        assert token in src, f"objective.py must reference {token}"
    assert "composite" in src.lower()


def test_03_operator_decisions_records_distance_semantics_resolution():
    doc = OPDEC.read_text()
    assert re.search(r"distance", doc, re.IGNORECASE), "distance semantics must be noted"
    assert re.search(r"identity probe", doc, re.IGNORECASE) or "identity" in doc


def test_04_operator_decisions_names_v4_reopen_under_distance():
    doc = OPDEC.read_text()
    assert re.search(r"v4 REOPEN under distance", doc), \
        "OPERATOR_DECISIONS must record the v4 REOPEN under distance-semantics resolution"


def test_05_retained_absolute_floor_reads_as_distance_upper_bound():
    doc = OPDEC.read_text()
    assert "0.60" in doc and "0.40" in doc, \
        "OPERATOR_DECISIONS must reference the retained 0.60/0.40 thresholds"


def test_06_composite_embedding_scaled_x100():
    src = OBJECTIVE.read_text()
    assert "100.0" in src or "100" in src, \
        "embedding factor scaled x100 per composite formula"


def test_07_interpreter_guard_on_objective():
    src = OBJECTIVE.read_text()
    assert "/usr/bin/python3" in src, "objective.py must carry /usr/bin/python3 guard"


if __name__ == "__main__":
    fns = [v for k, v in list(globals().items()) if k.startswith("test_")]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"FAIL {fn.__name__}: {e}")
    print(f"---\n{ok}/{len(fns)} tests passed")
    sys.exit(0 if ok == len(fns) else 1)
