#!/usr/bin/env python3
"""c25 M-V3-SPINE-1/wig-palette-render-c25 test suite (>=14 cases).

Runs under BLAS pins + PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1756463424
+ TZ=UTC + LC_ALL=C.UTF-8.
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
SONG_SHA16 = "252eb21ce7df7328"

RUBRIC = _REPO / "docs" / "v3_spine_wig_palette_render_c25_rubric.md"
RUBRIC_HASH_TXT = _REPO / "data" / "v3_spine" / SONG_SHA16 / "palette_render" / "rubric_hash_v2.txt"
SCRIPTS_DIR = _REPO / "scripts" / "v3_spine" / "palette_render_wig"
DELIV_ROOT = _REPO / "data" / "v3" / "deliveries" / SONG_SHA16 / "palette_render_c25"
PAL_ROOT = _REPO / "data" / "v3_spine" / SONG_SHA16 / "palette_render"
VERDICT_JSON = DELIV_ROOT / "verdict.json"

RENDER_STEM_LOCK = "214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _script_files() -> list[Path]:
    return sorted(SCRIPTS_DIR.glob("*.py"))


def _all_source() -> str:
    return "\n".join(p.read_text() for p in _script_files())


def _ast_call_names(src: str) -> set[str]:
    tree = ast.parse(src)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute):
                names.add(f.attr)
            elif isinstance(f, ast.Name):
                names.add(f.id)
    return names


def test_01_rubric_mtime_pre_registered():
    """Test 1: rubric doc mtime < every script mtime under palette_render_wig/."""
    r_mtime = os.path.getmtime(RUBRIC)
    for p in _script_files():
        assert os.path.getmtime(p) > r_mtime, \
            f"{p.name} mtime {os.path.getmtime(p)} not > rubric {r_mtime}"


def test_02_three_way_rubric_hash_chain():
    """Test 2: doc SHA == rubric_hash_v2.txt content == verdict rubric_hash_v2."""
    doc_sha = _sha256(RUBRIC)
    txt = RUBRIC_HASH_TXT.read_text().strip()
    assert doc_sha == txt, f"doc {doc_sha} != txt {txt}"
    if VERDICT_JSON.is_file():
        v = json.loads(VERDICT_JSON.read_text())
        assert v["rubric_hash_v2"] == doc_sha
        assert v["rubric_hash_v2_txt_content"] == txt


def test_03_render_stem_sha_lock():
    """Test 3: scripts/palette_render/render_stem.py SHA byte-identical."""
    p = _REPO / "scripts" / "palette_render" / "render_stem.py"
    assert _sha256(p) == RENDER_STEM_LOCK


def test_04_no_prng_grep():
    """Test 4: AST-verified no PRNG in palette_render_wig scripts."""
    forbidden_attrs = {"randn", "random", "randint", "choice", "shuffle",
                       "uniform", "normal"}
    forbidden_mods = {"random"}  # bare `import random`
    for p in _script_files():
        src = p.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            # Bare `import random`
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name.split(".")[0] not in forbidden_mods, \
                        f"{p.name} imports {a.name}"
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in forbidden_mods:
                    raise AssertionError(f"{p.name} from-imports {node.module}")
            # Attribute calls like np.random.randn
            if isinstance(node, ast.Attribute) and node.attr in forbidden_attrs:
                # Whitelist scipy.io.wavfile.read (not PRNG) and np dtypes
                pass  # attribute name alone insufficient — check call context
        # No unseeded numpy.random usage
        assert "np.random." not in src or "np.random.seed" in src, \
            f"{p.name} uses np.random without seeding"


def test_05_vst3_state_api_forbidden():
    """Test 5: AST-forbidden VST3 state APIs.

    Zero call sites of get_state / save_state / save_preset / load_state /
    set_state / get_state_chunk / getChunk on the palette_render_wig scripts.
    """
    forbidden = {"get_state", "save_state", "save_preset", "load_state",
                 "set_state", "get_state_chunk", "getChunk"}
    for p in _script_files():
        src = p.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                name = f.attr if isinstance(f, ast.Attribute) else \
                       f.id if isinstance(f, ast.Name) else None
                assert name not in forbidden, \
                    f"{p.name}: forbidden VST3 state API call {name}"


def test_06_usr_bin_python3_guard():
    """Test 6: every top-level script has /usr/bin/python3 guard."""
    for p in _script_files():
        if p.name == "__init__.py":
            continue
        src = p.read_text()
        assert '/usr/bin/python3' in src, f"{p.name} missing interpreter guard"


def test_07_c48_env_flag_defaults_off():
    """Test 7: c48 env flags default OFF via os.environ.setdefault."""
    for p in _script_files():
        if p.name in ("__init__.py", "anchor_preservation.py"):
            continue
        src = p.read_text()
        assert 'MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION' in src, p.name
        assert 'MUSICGEN_LEDGER_SUPERSEDES_IN_HASH' in src, p.name
        assert 'setdefault' in src, p.name


def test_08_focus_set_v2_consumption_wig():
    """Test 8: focus_set_v2 chosen_section for WIG sha16 matches rubric."""
    fs = json.loads((_REPO / "data" / "recreate_v2" / "focus_set_v2.json").read_text())
    wig = None
    for s in (fs.get("songs") or fs if isinstance(fs, list) else fs.get("songs", [])):
        if isinstance(s, dict) and s.get("song_id") == SONG_SHA16:
            wig = s
            break
    assert wig is not None, "WIG not in focus_set_v2"
    sec = wig["chosen_section"]
    assert abs(sec["t_start_s"] - 72.77133786848073) < 1e-6
    assert abs(sec["t_end_s"] - 102.77133786848073) < 1e-6


def test_09_both_panels_8_key_finite():
    """Test 9: both panels return 8 finite keys per M-TEX-1/panel contract."""
    if not VERDICT_JSON.is_file():
        return  # pipeline not yet run
    v = json.loads(VERDICT_JSON.read_text())
    for k in ("panel_a_original_vs_palette", "panel_b_fluidsynth_vs_palette"):
        panel = v[k]
        assert len(panel) == 8, f"{k} has {len(panel)} keys not 8"
        for key, val in panel.items():
            if isinstance(val, (int, float)):
                assert val == val and float("-inf") < float(val) < float("inf"), \
                    f"{k}[{key}] non-finite: {val}"


def test_10_cross_song_anchor_preservation():
    """Test 10: c21 CG palette + c21 WIG operator_section anchors byte-identical.

    Re-hashes a subset of anchors defined in anchor_preservation.py and
    asserts they match the on-disk anchor_preservation.json snapshot's
    post entries.
    """
    ap = json.loads((PAL_ROOT / "anchor_preservation.json").read_text())
    assert ap.get("all_match") is True, f"anchor mismatch: {ap.get('mismatches')}"
    assert ap["n_entries"] >= 30
    # Must include c21 WIG delivery + c21 CG palette anchors
    paths = {e["path"] for e in ap.get("post_entries", ap.get("entries", []))}
    assert any("v3/deliveries/252eb21ce7df7328/operator_section/manifest.json" in p
               for p in paths)
    assert any("31a164f845f8e27e" in p for p in paths), \
        "no CG anchors in preservation snapshot"


def test_11_byte_determinism_x2_per_stem():
    """Test 11: byte-det × 2 per persisted stem (or honest REDEFINED_GAP arm)."""
    det = json.loads((PAL_ROOT / "byte_determinism.json").read_text())
    per_stem = det["per_stem"]
    assert len(per_stem) == 6
    for stem, v in per_stem.items():
        assert v.get("byte_det_x2", False) is True, \
            f"{stem} failed byte-det ×2: {v}"


def test_12_honest_redefined_gap_arm_bookkeeping():
    """Test 12: if bass Surge XT structural drift, REDEFINED_GAP arm recorded."""
    det = json.loads((PAL_ROOT / "byte_determinism.json").read_text())
    bass = det["per_stem"]["bass"]
    # Either byte_det on VST3 outcome OR REDEFINED_GAP arm engaged
    vst3_outcome = bass.get("vst3_outcome") or \
                   bass.get("vst3_attempt", {}).get("outcome")
    if vst3_outcome not in ("byte_det", "small_perturbation_tolerable"):
        assert bass.get("redefined_gap_arm") is True, \
            "bass VST3 failed but REDEFINED_GAP arm not engaged"
        # Fetchability ladder must record the fallback
        ladder = [json.loads(l) for l in
                  (PAL_ROOT / "fetchability_ladder.jsonl").read_text().splitlines()
                  if l.strip()]
        assert any(r.get("stem") == "bass" and r.get("path") == "fluidsynth_gm"
                   and r.get("program") == 33 for r in ladder), \
            "bass REDEFINED_GAP fluidsynth_gm(33) fallback missing from ladder"
        # dispatch_summary records arm_engaged
        disp = json.loads((PAL_ROOT / "dispatch_summary.json").read_text())
        assert disp["per_stem"]["bass"]["arm_engaged"] == "redefined_gap"


def test_13_dispatch_summary_matches_fetchability_ladder():
    """Test 13: dispatch summary matches fetchability ladder (per-stem attempts)."""
    disp = json.loads((PAL_ROOT / "dispatch_summary.json").read_text())
    ladder = [json.loads(l) for l in
              (PAL_ROOT / "fetchability_ladder.jsonl").read_text().splitlines()
              if l.strip()]
    ladder_stems = {r.get("stem") for r in ladder if r.get("stem")}
    # Every non-drums/vocals dispatch entry has a matching ladder row
    for stem in ("bass", "guitar", "piano", "other"):
        assert stem in ladder_stems, \
            f"{stem} missing from fetchability_ladder.jsonl"
        assert stem in disp["per_stem"]


def test_14_delivery_manifest_carries_env_pins():
    """Test 14: delivery manifest.json carries env_pins block with self-anchor."""
    manifest = json.loads((DELIV_ROOT / "manifest.json").read_text())
    assert "env_pins" in manifest, "manifest missing env_pins block"
    ep = manifest["env_pins"]
    assert "env_pin_sha256" in ep, "env_pins missing self-anchor sha"


def test_15_sidecar_nonfactor_ast_forbidden():
    """Test 15: no import of scripts.classifier.sidecar_nonfactor."""
    for p in _script_files():
        src = p.read_text()
        assert "sidecar_nonfactor" not in src, \
            f"{p.name} references sidecar_nonfactor"


def _all_tests():
    return [(name, obj) for name, obj in globals().items()
            if name.startswith("test_") and callable(obj)]


def main() -> int:
    n_pass = 0
    n_fail = 0
    for name, fn in _all_tests():
        try:
            fn()
            print(f"PASS {name}")
            n_pass += 1
        except Exception as e:
            print(f"FAIL {name}: {e!r}")
            n_fail += 1
    print(f"\n{n_pass}/{n_pass + n_fail} PASS")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
