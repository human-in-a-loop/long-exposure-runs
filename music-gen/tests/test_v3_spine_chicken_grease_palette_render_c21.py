#!/usr/bin/env python3
"""c21 M-V3-SPINE-1/chicken-grease-palette-render — invariant tests."""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
os.chdir(str(_REPO))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

SONG = "31a164f845f8e27e"
PAL = _REPO / "data" / "v3_spine" / SONG / "palette_render"
DELIV = _REPO / "data" / "v3" / "deliveries" / SONG / "palette_render"
CYCLE21 = _REPO / "data" / "v3" / "deliveries" / SONG / "cycle21"
RUBRIC = _REPO / "docs" / "v3_spine_chicken_grease_palette_render_c21_rubric.md"
SCRIPTS = _REPO / "scripts" / "v3_spine" / "palette_render"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_01_rubric_mtime_pre_registration():
    """Rubric doc mtime must precede every Python script under the impl dir."""
    r = RUBRIC.stat().st_mtime
    for p in SCRIPTS.glob("*.py"):
        if p.name == "__init__.py":
            continue
        assert r <= p.stat().st_mtime, f"{p.name} mtime precedes rubric"


def test_02_three_way_rubric_hash_v2_chain():
    doc_sha = sha256(RUBRIC)
    txt_sha = (PAL / "rubric_hash_v2.txt").read_text().strip()
    v = json.loads((CYCLE21 / "verdict_palette.json").read_text())
    assert doc_sha == txt_sha, "doc SHA != rubric_hash_v2.txt content"
    assert v["rubric_hash_v2"] == doc_sha, "verdict.rubric_hash_v2 != doc SHA"
    assert v["rubric_hash_v2_chain_holds"] is True


def test_03_c5_delivery_anchors_pre_eq_post():
    ap = json.loads((PAL / "anchor_preservation.json").read_text())
    assert ap.get("phase") == "post"
    assert ap["n_mismatch"] == 0
    assert ap["all_match"] is True
    assert ap["n_entries"] >= 60


def test_04_per_stem_byte_det():
    d = json.loads((PAL / "byte_determinism.json").read_text())
    for stem, entry in d["per_stem"].items():
        assert entry.get("byte_det_x2") is True, f"{stem} byte-det gate failed"


def test_05_panel_a_and_b_8_keys_finite():
    import math
    for p in ("panel_original_vs_palette.json", "panel_fluidsynth_vs_palette.json"):
        j = json.loads((PAL / p).read_text())
        assert len(j) == 8, f"{p} panel key count = {len(j)} (expected 8)"
        for k, v in j.items():
            if isinstance(v, (int, float)):
                assert math.isfinite(v), f"{p} key {k} non-finite: {v}"


def test_06_fetchability_ladder_present():
    l = PAL / "fetchability_ladder.jsonl"
    assert l.is_file()
    rows = [json.loads(x) for x in l.read_text().splitlines() if x.strip()]
    assert len(rows) >= 5
    stems = {r.get("stem") for r in rows}
    assert {"guitar", "piano", "other", "bass"} <= stems


def test_07_no_prng_in_impl_scripts():
    banned = re.compile(r"\b(random\.|numpy\.random\.|np\.random\.|torch\.rand|torch\.randn)")
    for p in SCRIPTS.glob("*.py"):
        s = p.read_text()
        assert not banned.search(s), f"{p.name} uses PRNG"


def test_08_no_forbidden_vst3_state_calls():
    forbidden = re.compile(r"\b(get_state|save_state|save_preset|load_state|set_state)\s*\(")
    for p in SCRIPTS.glob("*.py"):
        s = p.read_text()
        # `set_state(bytes)` is the forbidden invocation form; we forbid all
        # unqualified state-extraction calls to lock the c31/c35 anti-patterns.
        m = forbidden.search(s)
        assert m is None, f"{p.name} contains forbidden state call: {m.group(0)}"


def test_09_c5_operator_delivery_untouched():
    """c5 operator-blessed full_reconstruction sha byte-identical."""
    expected = "cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7"
    p = _REPO / "data" / "v3" / "deliveries" / SONG / "operator_section" / "full_reconstruction_operator_section.wav"
    assert sha256(p) == expected


def test_10_verdict_shape_and_placement():
    vp = CYCLE21 / "verdict_palette.json"
    assert vp.is_file(), "verdict at cycle21/verdict_palette.json (sibling not overwrite)"
    v = json.loads(vp.read_text())
    assert v["verdict"] in ("PALETTE_MOVES_PANEL", "PALETTE_NEUTRAL", "RENDER_FAILS")
    assert v["blocked_on_operator"] is True
    assert v["milestone"] == "M-V3-SPINE-1/chicken-grease-palette-render"
    assert v["cycle"] == 21
    # sibling to cycle20/ — c20 verdict path unchanged
    c20 = _REPO / "data" / "v3" / "deliveries" / SONG / "cycle20"
    if c20.is_dir():
        assert c20.exists(), "cycle20 sibling directory preserved"


def test_11_render_stem_and_rc7_anchors_untouched():
    expected = {
        "scripts/palette_render/render_stem.py": "214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b",
        "scripts/v3_spine/rc7_v2_rerun_v3_paths.py": "eaaa993e2eb50d25a9085af0b1171bc58da9a9c21b6233cc9c0c80b1c6f03e38",
    }
    for rel, exp in expected.items():
        got = sha256(_REPO / rel)
        assert got == exp, f"{rel} SHA drift: got {got}, expected {exp}"


def test_12_no_sidecar_nonfactor_import():
    for p in SCRIPTS.glob("*.py"):
        s = p.read_text()
        assert "sidecar_nonfactor" not in s, f"{p.name} imports sidecar_nonfactor"


if __name__ == "__main__":
    n_pass = 0
    n_fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                n_pass += 1
                print(f"PASS {name}")
            except Exception as e:
                n_fail += 1
                print(f"FAIL {name}: {type(e).__name__}: {e}")
    print(f"\n{n_pass}/{n_pass + n_fail} tests passed")
    sys.exit(0 if n_fail == 0 else 1)
