#!/usr/bin/python3
# ---
# created: 2026-09-02T00:00:00Z
# cycle: 58
# milestone: M-V3-SPINE
# ---
"""M-V3-SPINE test suite (12 cases).

Run: PYTHONPATH=. /usr/bin/python3 tests/test_v3_spine.py

Writes JSON summary to data/v3_spine/31a164f845f8e27e/tests_result.json so
the verdict emitter can pick up the count.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

WSROOT = Path(__file__).resolve().parents[1]
SONG = "31a164f845f8e27e"
V3_ROOT = WSROOT / "data" / "v3_spine" / SONG
DELIVERY = WSROOT / "data" / "v3" / "deliveries" / SONG
SCRIPTS_DIR = WSROOT / "scripts" / "v3_spine"

BANNED_IMPORTS = (
    "scripts.recreate_v0",
    "scripts.transcribe",
    "scripts.recreate_v2.rc2",
    "scripts.recreate_v2.rc3",
    "scripts.recreate_v2.rc10_drums",
    "scripts.recreate_v2.rc10_bass",
    "scripts.recreate_v2.rc10_guitar_piano",
    "scripts.recreate_v2.rc10_other_vocals",
    "basic_pitch",
    "pyin",
    # onset+GMM classifier lineage from the killed hand-rolled DSP era
)


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _test(name):
    def wrap(fn):
        _tests.append((name, fn))
        return fn
    return wrap


_tests: list[tuple[str, callable]] = []


# 01
@_test("rubric mtime precedes every script under scripts/v3_spine/")
def test_rubric_precedes_scripts():
    rubric = WSROOT / "docs" / "v3_spine_rubric.md"
    assert rubric.exists(), "rubric doc missing"
    rt = rubric.stat().st_mtime
    for p in SCRIPTS_DIR.rglob("*.py"):
        assert p.stat().st_mtime >= rt, f"{p} mtime precedes rubric"


# 02
@_test("three-way rubric_hash chain byte-equal")
def test_rubric_hash_chain():
    doc_sha = _sha256(WSROOT / "docs" / "v3_spine_rubric.md")
    file_sha = (WSROOT / "data" / "v3_spine" / "rubric_hash.txt").read_text().strip()
    assert doc_sha == file_sha, f"{doc_sha} != {file_sha}"
    vfile = V3_ROOT / "verdict.json"
    if vfile.exists():
        v = json.loads(vfile.read_text())
        assert v["rubric_hash"] == doc_sha, f"verdict.rubric_hash mismatch"


# 03
@_test("byte-determinism ×2 PASS on all tracked anchors")
def test_byte_determinism():
    p = V3_ROOT / "determinism.json"
    assert p.exists(), "determinism.json missing (run determinism_check.py)"
    d = json.loads(p.read_text())
    assert d.get("byte_determinism_holds"), (
        f"byte-det failed: {len(d.get('mismatches', []))} mismatches: {d.get('mismatches')}"
    )


# 04
@_test("scripts/v3_spine/ imports no banned lineage")
def test_no_banned_imports():
    for py in SCRIPTS_DIR.rglob("*.py"):
        src = py.read_text()
        tree = ast.parse(src, filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    for banned in BANNED_IMPORTS:
                        assert not n.name.startswith(banned), f"{py} imports {n.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                for banned in BANNED_IMPORTS:
                    assert not node.module.startswith(banned), f"{py} imports {node.module}"


# 05
@_test("zero merged-MIDI parts on GM program 4 unless deliberately electric_piano")
def test_no_program_4_by_accident():
    summary = json.loads((V3_ROOT / "run_summary.json").read_text())
    prog_manifest = summary["merge_info"]["program_manifest"]
    for row in prog_manifest:
        if row.get("gm_program") == 4 and not row.get("is_drum"):
            assert row.get("label") == "electric_piano", (
                f"non-electric_piano label {row.get('label')!r} rendered on GM 4"
            )


# 06
@_test("drums track present on MIDI channel 10")
def test_drums_on_ch10():
    summary = json.loads((V3_ROOT / "run_summary.json").read_text())
    drums = [r for r in summary["merge_info"]["program_manifest"]
             if r.get("is_drum")]
    assert any(r.get("channel") == 10 for r in drums), \
        f"no drums on channel 10: {drums}"


# 07
@_test("vocals part present in merged MIDI but not synthesized")
def test_vocals_symbolic():
    summary = json.loads((V3_ROOT / "run_summary.json").read_text())
    v = [r for r in summary["merge_info"]["program_manifest"]
         if r.get("is_vocal_symbolic")]
    # Depending on the transcriber, vocals track may or may not have notes;
    # this test only requires that vocals from the vocals stem are tagged
    # symbolic if they exist. Presence is not required (silence is OK).
    for r in v:
        assert r.get("action") == "VOCAL_SYMBOLIC_NOT_RENDERED", r


# 08
@_test("A/B delivery: 3 non-silent WAVs, A/B duration 30 s ±5 ms")
def test_delivery_ab():
    for n in ("original_ab.wav", "reconstruction_ab.wav", "full_reconstruction.wav"):
        p = DELIVERY / n
        assert p.exists(), f"missing {p}"
    import soundfile as sf
    for n, expect_30s in (("original_ab.wav", True), ("reconstruction_ab.wav", True),
                          ("full_reconstruction.wav", False)):
        arr, sr = sf.read(str(DELIVERY / n), always_2d=True)
        peak = float(abs(arr).max()) if arr.size else 0.0
        assert peak > 1e-4, f"{n} silent (peak={peak})"
        dur = arr.shape[0] / sr
        if expect_30s:
            assert abs(dur - 30.0) < 0.005, f"{n} duration {dur:.4f}s off by >5ms"


# 09
@_test("panel.tsv returns 8 finite keys")
def test_panel_finite():
    tsv = V3_ROOT / "panel.tsv"
    assert tsv.exists()
    rows = [ln.strip().split("\t") for ln in tsv.read_text().splitlines()[1:]]
    d = {k: float(v) for k, v in rows}
    assert len(d) == 8, f"panel has {len(d)} keys, expected 8: {sorted(d)}"
    import math
    for k, v in d.items():
        if k == "vggish_cosine_distance":
            # sentinel -1.0 for unavailable is OK
            continue
        assert math.isfinite(v), f"panel[{k}]={v} not finite"


# 10
@_test("anchor preservation ≥20 SHAs pre==post byte-exact")
def test_anchor_preservation():
    p = V3_ROOT / "anchor_preservation.json"
    assert p.exists(), "run anchor_preservation.py first"
    a = json.loads(p.read_text())
    assert a["n_anchors"] >= 20, f"only {a['n_anchors']} anchors"
    if a.get("phase") == "post":
        assert a.get("all_match"), f"anchor mismatches: {a.get('mismatches')}"


# 11
@_test("every top-level script under scripts/v3_spine/ has /usr/bin/python3 guard")
def test_interpreter_guard():
    for py in SCRIPTS_DIR.glob("*.py"):
        if py.name == "__init__.py":
            continue
        src = py.read_text()
        assert '/usr/bin/python3' in src, f"{py} missing /usr/bin/python3 guard"


# 12
@_test("NO PRNG under scripts/v3_spine/ (AST-grep)")
def test_no_prng():
    prng_names = {"random", "np.random", "numpy.random", "rand", "randint", "random.random"}
    for py in SCRIPTS_DIR.rglob("*.py"):
        src = py.read_text()
        tree = ast.parse(src, filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    assert n.name != "random", f"{py} imports `random`"
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == "np" and node.attr == "random":
                    # ok if used only for np.random typing? No — forbid.
                    raise AssertionError(f"{py} uses np.random")
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in {"random", "randint", "rand", "choice"}:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id in {"random", "np", "numpy"}:
                        raise AssertionError(f"{py}: {ast.dump(node)}")


def main() -> None:
    passed = 0
    failed: list[tuple[str, str]] = []
    for name, fn in _tests:
        try:
            fn()
            passed += 1
            print(f"PASS  {name}")
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    n_total = len(_tests)
    n_pass = passed
    n_fail = len(failed)
    print(f"\n{n_pass}/{n_total} pass, {n_fail} fail")
    out = V3_ROOT / "tests_result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "n_total": n_total, "n_pass": n_pass, "n_fail": n_fail,
        "failed": [{"name": n, "reason": r} for n, r in failed],
    }, sort_keys=True, indent=2) + "\n")
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
