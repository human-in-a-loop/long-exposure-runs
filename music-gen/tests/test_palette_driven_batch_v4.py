#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T09:20:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-v4
# ---
"""Test suite for M-GEN-1/palette-driven-batch-v4 (≥ 16 cases).

Plain-assert style, no pytest. Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_palette_driven_batch_v4.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))

from scripts.palette_render_v4.derive_parameter_dict_8x8 import (
    FLUIDSYNTH_TABLE_V4, SFIZZ_TABLE_V4,
    derive_for_instrument, derive_per_salt, payload_sha256,
)
from scripts.palette_render_v4.extend_sfizz_opcode_rewrite import (
    rewrite_sfz_content, _absolutize_sample_paths,
)

RUBRIC_HASH_TXT = _REPO / "data" / "palette_render_v4" / "rubric_hash.txt"
RUBRIC_DOC = _REPO / "docs" / "palette_driven_batch_v4_rubric.md"
REPORT_DOC = _REPO / "docs" / "palette_driven_batch_v4_report.md"
VERDICT_JSON = _REPO / "data" / "palette_render_v4" / "verdict.json"
BC_JSON = _REPO / "data" / "palette_render_v4" / "backwards_compat_check.json"
BATCH_MANIFEST = _REPO / "data" / "palette_render_v4" / "batch_manifest.json"
SPREAD_JSON = _REPO / "data" / "palette_render_v4" / "spread_analysis.json"
ANCHOR_JSON = _REPO / "data" / "palette_render_v4" / "anchor_preservation.json"
SUMMARY_TSV = _REPO / "data" / "palette_render_v4" / "summary.tsv"

# c33 anchor SHAs (from directive).
C33_ANCHOR_SHAS = {
    "bass":     "6b9a5219e761854bdcf42a87f370a283e3fb096faf64648eb198c98520540280",
    "other":    "a2e5d0585404b448a2120c3c4bd6432ec1962ed82c3a7a74dd7518ed3d10f621",
    "combined": "a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794",
}

# Anti-pattern locks.
FORBIDDEN_IMPORTS = (
    "sidecar_nonfactor",
    "scripts.tex.render_effects_layered",
    "scripts.gen.batch_v2",
    "i4_stratified",
)


def test_01_rubric_hash_matches_doc():
    got = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    on_disk = RUBRIC_HASH_TXT.read_text().strip()
    assert got == on_disk, f"rubric_hash.txt drift: {got} vs {on_disk}"


def test_02_rubric_mtime_precedes_scripts():
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    for p in sorted((_REPO / "scripts" / "palette_render_v4").rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        assert rubric_mtime <= p.stat().st_mtime, (
            f"rubric doc must mtime-precede {p.relative_to(_REPO)}"
        )


def test_03_backwards_compat_all_match():
    bc = json.loads(BC_JSON.read_text())
    assert bc["all_match"] is True, bc
    for k in ("bass", "other", "combined"):
        assert bc["observed"][k] == C33_ANCHOR_SHAS[k], (k, bc["observed"][k])
        assert bc["matches"][k] is True


def test_04_verdict_is_param_moves_audio():
    v = json.loads(VERDICT_JSON.read_text())
    assert v["verdict"] == "PARAM_MOVES_AUDIO", v["verdict"]
    assert v["rubric_hash"] == RUBRIC_HASH_TXT.read_text().strip()


def test_05_per_salt_determinism_all_pass():
    v = json.loads(VERDICT_JSON.read_text())
    per = v["per_salt_determinism"]
    for s in range(8):
        assert per[str(s)] is True, (s, per)


def test_06_cross_salt_28_distinct():
    v = json.loads(VERDICT_JSON.read_text())
    assert v["cross_salt_pair_count"] == 28
    assert v["cross_salt_distinct_count"] >= 22, v["cross_salt_distinct_count"]
    # In practice we expect exactly 28 for this run — assert as a signal.
    assert v["cross_salt_distinct_count"] == 28


def test_07_panels_all_8_keys_finite():
    from math import isfinite
    v = json.loads(VERDICT_JSON.read_text())
    numeric = ("mel_l1_db", "spectral_centroid_rmse_hz",
               "rms_env_rmse", "lufs_m_rmse_lu")
    for s in range(8):
        for panel_name in ("panel_original", "panel_fluidsynth"):
            p = v["per_salt_panels"][str(s)][panel_name]
            assert len(p) == 8, (s, panel_name, len(p))
            for k in numeric:
                assert isfinite(p[k]), (s, panel_name, k, p[k])


def test_08_vst3_branches_raise_notimplemented():
    for inst in ("surge_xt", "dexed"):
        try:
            derive_for_instrument("any-rule-id", inst)
        except NotImplementedError:
            continue
        raise AssertionError(f"{inst} should have raised NotImplementedError")


def test_09_derive_is_deterministic():
    a = derive_for_instrument("test-rule-abc", "fluidsynth")
    b = derive_for_instrument("test-rule-abc", "fluidsynth")
    assert a == b
    c = derive_for_instrument("test-rule-abc", "sfizz")
    d = derive_for_instrument("test-rule-abc", "sfizz")
    assert c == d


def test_10_8x8_table_shape():
    # 5 fluidsynth params × 8 values + 3 sfizz params × 8 values = 8×8 total.
    assert len(FLUIDSYNTH_TABLE_V4) == 5
    assert len(SFIZZ_TABLE_V4) == 3
    assert len(FLUIDSYNTH_TABLE_V4) + len(SFIZZ_TABLE_V4) == 8
    for vals in FLUIDSYNTH_TABLE_V4.values():
        assert len(vals) == 8, vals
    for vals in SFIZZ_TABLE_V4.values():
        assert len(vals) == 8, vals


def test_11_opcode_rewrite_injects_both_opcodes():
    src = "<region>\nsample=test_saw.wav\npitch_keycenter=60\n"
    out = rewrite_sfz_content(src, cutoff=1234.5, resonance=6.5)
    assert "fil_cutoff=1234.500000" in out
    assert "fil_resonance=6.500000" in out


def test_12_opcode_rewrite_noop_when_both_none():
    src = "<region>\nsample=test_saw.wav\n"
    out = rewrite_sfz_content(src, cutoff=None, resonance=None)
    assert "fil_cutoff" not in out
    assert "fil_resonance" not in out


def test_13_absolutize_sample_paths():
    src = "<region>\nsample=test_saw.wav\nfoo=bar\n"
    out = _absolutize_sample_paths(src, _REPO / "data" / "texture")
    assert "sample=/" in out, out
    assert "test_saw.wav" in out
    # Absolute paths pass through untouched.
    src_abs = "sample=/etc/passwd\n"
    out2 = _absolutize_sample_paths(src_abs, _REPO)
    assert out2 == src_abs


def test_14_anchor_preservation_only_render_stem_edited():
    a = json.loads(ANCHOR_JSON.read_text())
    assert a["unchanged_except_render_stem_edit"] is True, a
    assert (a["intentional_render_stem_edit"]["path"]
            == "scripts/palette_render/render_stem.py")


def test_15_no_forbidden_imports_in_v4():
    """Import-statement-shaped occurrences only — docstring mentions are fine."""
    import re
    v4_dir = _REPO / "scripts" / "palette_render_v4"
    patterns = [re.compile(rf"^\s*(?:from\s+\S*{re.escape(b)}|import\s+\S*{re.escape(b)})",
                            re.MULTILINE) for b in FORBIDDEN_IMPORTS]
    for p in v4_dir.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        text = p.read_text()
        for bad, pat in zip(FORBIDDEN_IMPORTS, patterns):
            assert not pat.search(text), (
                f"{p.relative_to(_REPO)} imports {bad}"
            )


def test_16_no_prng_in_v4():
    """No use of `random`, `numpy.random`, or `os.urandom` in v4."""
    v4_dir = _REPO / "scripts" / "palette_render_v4"
    banned = ("import random", "from random", "np.random", "numpy.random",
              "os.urandom", "secrets.")
    for p in v4_dir.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        text = p.read_text()
        for b in banned:
            assert b not in text, f"{p.relative_to(_REPO)} contains {b!r}"


def test_17_interpreter_guard_present_in_every_script():
    guard = 'assert sys.executable == "/usr/bin/python3"'
    v4_dir = _REPO / "scripts" / "palette_render_v4"
    for p in v4_dir.rglob("*.py"):
        if "__pycache__" in p.parts or p.name == "__init__.py":
            continue
        text = p.read_text()
        assert guard in text, f"{p.relative_to(_REPO)} missing interpreter guard"


def test_18_summary_tsv_has_8_data_rows():
    text = SUMMARY_TSV.read_text().strip().split("\n")
    header, *rows = text
    assert "salt" in header
    assert len(rows) == 8, len(rows)
    for i, row in enumerate(rows):
        cells = row.split("\t")
        assert cells[0] == str(i), (i, cells[0])
        assert cells[3] == "True", (i, cells)  # per-salt determinism cell


def test_19_batch_manifest_shape():
    m = json.loads(BATCH_MANIFEST.read_text())
    assert m["salts"] == [0, 1, 2, 3, 4, 5, 6, 7]
    assert m["cross_salt_pair_count"] == 28
    assert m["cross_salt_distinct_count"] >= 22
    # 8 salts × 3 stems = 24 assignment SHAs indirectly available.
    assert len(m["assignments_shas_by_salt"]) == 8


def test_20_spread_v4_dominates_v3_on_ge_majority():
    s = json.loads(SPREAD_JSON.read_text())
    # Corroborating signal (not a hard gate).
    assert s["iqr_v4_wins_of_8"] >= s["iqr_v3_wins_of_8"], s


def test_21_report_document_exists():
    assert REPORT_DOC.is_file(), "report doc missing"
    text = REPORT_DOC.read_text()
    assert "PARAM_MOVES_AUDIO" in text
    assert "palette-driven-batch-v4" in text


def _run_all():
    tests = [(name, obj) for name, obj in sorted(globals().items())
             if name.startswith("test_") and callable(obj)]
    passed = 0
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
            failed.append(name)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {name}: {type(e).__name__}: {e}")
            failed.append(name)
    print(f"---\n{passed}/{len(tests)} PASS")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
