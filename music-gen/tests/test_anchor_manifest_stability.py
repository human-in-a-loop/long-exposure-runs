#!/usr/bin/env python3
# tests/test_anchor_manifest_stability.py — Cycle 35 clone-2.
# Verifies frozen anchor manifest schema, byte-determinism, rubric SHA trail,
# and read-only invariants. ≥12 named cases.
# created: 2026-08-29
# cycle: 35
# agent: worker
# milestone: _infra/anchor-manifest-v1-clone-2
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

WS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS))

from scripts.anchor_manifest.enumerate_anchors import enumerate_anchors, LONG_EXPOSURE_PREFIX  # noqa: E402
from scripts.anchor_manifest.compute_sha_manifest import compute_anchor  # noqa: E402
from scripts.anchor_manifest.run_freeze import build_manifest, serialize_manifest  # noqa: E402


RUBRIC_MD = WS / "docs" / "anchor_manifest_v1_rubric.md"
RUBRIC_HASH = WS / "data" / "anchor_manifest_v1" / "rubric_hash.txt"
MANIFEST_JSON = WS / "data" / "anchor_manifest_v1.json"
SCRIPTS = [
    WS / "scripts/anchor_manifest/__init__.py",
    WS / "scripts/anchor_manifest/enumerate_anchors.py",
    WS / "scripts/anchor_manifest/compute_sha_manifest.py",
    WS / "scripts/anchor_manifest/run_freeze.py",
]

failures = []
passes = []


def _check(name, cond, detail=""):
    if cond:
        passes.append(name)
        print(f"PASS {name}")
    else:
        failures.append((name, detail))
        print(f"FAIL {name}: {detail}")


# 1. Rubric SHA matches rubric_hash.txt
def test_01_rubric_hash_matches():
    doc_sha = hashlib.sha256(RUBRIC_MD.read_bytes()).hexdigest()
    txt = RUBRIC_HASH.read_text().strip()
    _check("test_01_rubric_hash_matches", doc_sha == txt, f"doc={doc_sha[:16]} file={txt[:16]}")


# 2. Manifest JSON present and parses
def test_02_manifest_json_present():
    _check("test_02_manifest_json_present", MANIFEST_JSON.exists(), str(MANIFEST_JSON))
    if MANIFEST_JSON.exists():
        m = json.loads(MANIFEST_JSON.read_bytes())
        _check("test_02b_manifest_anchor_count", m.get("anchor_count") == 18, f"got {m.get('anchor_count')}")


# 3. Freeze produces byte-identical output twice
def test_03_freeze_byte_determinism():
    m1 = build_manifest()
    m2 = build_manifest()
    b1 = serialize_manifest(m1)
    b2 = serialize_manifest(m2)
    sha1 = hashlib.sha256(b1).hexdigest()
    sha2 = hashlib.sha256(b2).hexdigest()
    _check("test_03_freeze_byte_determinism", sha1 == sha2, f"a={sha1[:16]} b={sha2[:16]}")
    on_disk = hashlib.sha256(MANIFEST_JSON.read_bytes()).hexdigest()
    _check("test_03b_freeze_matches_on_disk", on_disk == sha1, f"disk={on_disk[:16]}")


# 4. All 18 anchor entries present with required schema keys
def test_04_anchor_schema_keys():
    m = json.loads(MANIFEST_JSON.read_bytes())
    required = {"anchor_id", "cycle", "kind", "paths", "sha_per_path",
                "dir_manifest_sha_per_dir", "is_readonly", "file_count", "path_entries"}
    ok = True
    detail = []
    for a in m["anchors"]:
        missing = required - set(a.keys())
        if missing:
            ok = False
            detail.append(f"{a['anchor_id']}: missing {missing}")
    _check("test_04_anchor_schema_keys", ok, "; ".join(detail))
    _check("test_04b_anchor_count_18", len(m["anchors"]) == 18, f"got {len(m['anchors'])}")


# 5. is_readonly=True for all
def test_05_is_readonly_all():
    m = json.loads(MANIFEST_JSON.read_bytes())
    ok = all(a["is_readonly"] is True for a in m["anchors"])
    _check("test_05_is_readonly_all", ok, "some anchor is not is_readonly=True")


# 6. sha_per_path non-empty per anchor
def test_06_sha_per_path_nonempty():
    m = json.loads(MANIFEST_JSON.read_bytes())
    bad = [a["anchor_id"] for a in m["anchors"] if not a["sha_per_path"]]
    _check("test_06_sha_per_path_nonempty", not bad, f"empty: {bad}")


# 7. dir_manifest_sha present for every directory path
def test_07_dir_manifest_sha_where_dir():
    m = json.loads(MANIFEST_JSON.read_bytes())
    bad = []
    for a in m["anchors"]:
        for p, e in a["path_entries"].items():
            if e["kind"] == "dir" and not e["dir_manifest_sha"]:
                bad.append(f"{a['anchor_id']}/{p}")
    _check("test_07_dir_manifest_sha_where_dir", not bad, f"missing: {bad}")


# 8. No sidecar_nonfactor imports in scripts
def test_08_no_sidecar_nonfactor():
    bad = []
    for p in SCRIPTS:
        src = p.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "sidecar_nonfactor" in node.module:
                bad.append(str(p))
            if isinstance(node, ast.Import):
                for al in node.names:
                    if "sidecar_nonfactor" in al.name:
                        bad.append(str(p))
    _check("test_08_no_sidecar_nonfactor", not bad, f"offenders: {bad}")


# 9. No PRNG in scripts (AST-grep clean for random/numpy.random/torch.random)
def test_09_no_prng():
    forbidden_mods = {"random", "numpy.random", "torch.random"}
    forbidden_attr = {"random", "randint", "shuffle", "choice", "rand", "randn", "seed"}
    bad = []
    for p in SCRIPTS:
        src = p.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for al in node.names:
                    if al.name in forbidden_mods:
                        bad.append(f"{p.name}:{al.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in forbidden_mods:
                    bad.append(f"{p.name}:{node.module}")
    _check("test_09_no_prng", not bad, f"offenders: {bad}")


# 10. Interpreter guard present in each non-init script
def test_10_interpreter_guard():
    bad = []
    for p in SCRIPTS:
        if p.name == "__init__.py":
            continue
        src = p.read_text()
        if "sys.executable" not in src or "/usr/bin/python3" not in src:
            bad.append(str(p))
    _check("test_10_interpreter_guard", not bad, f"missing guard: {bad}")


# 11. long_exposure/* exemption documented via env-var reachability check
def test_11_long_exposure_exemption():
    p = Path(LONG_EXPOSURE_PREFIX) / "long_exposure" / "workspace_bootstrap.py"
    _check("test_11_long_exposure_exemption", p.exists(), f"{p} not reachable")
    m = json.loads(MANIFEST_JSON.read_bytes())
    _check("test_11b_prefix_in_manifest",
           m.get("long_exposure_prefix") == LONG_EXPOSURE_PREFIX,
           f"got {m.get('long_exposure_prefix')}")
    _check("test_11c_exemption_key_in_manifest",
           "long_exposure_outside_workspace" in m.get("exemptions", {}),
           "exemption entry missing")


# 12. Verdict resides in the report + rubric hash consistency
def test_12_verdict_and_rubric_hash():
    report = (WS / "docs/anchor_manifest_v1_report.md").read_text()
    ok = "MANIFEST_LOCKED" in report or "MANIFEST_DRIFTS" in report
    _check("test_12_verdict_present", ok, "no verdict token in report")
    rubric_hash = RUBRIC_HASH.read_text().strip()
    _check("test_12b_rubric_hash_in_report", rubric_hash in report,
           f"rubric hash {rubric_hash[:16]} not in report")


# 13. Fresh subprocess freeze equals on-disk JSON (external process determinism)
def test_13_subprocess_freeze_matches():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "m.json"
        outmd = Path(td) / "m.md"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(WS)
        r = subprocess.run(
            ["/usr/bin/python3", str(WS / "scripts/anchor_manifest/run_freeze.py"),
             "--out-json", str(out), "--out-md", str(outmd)],
            capture_output=True, text=True, env=env, cwd=str(WS),
        )
        _check("test_13_subprocess_freeze_ok", r.returncode == 0, r.stderr[-200:])
        if r.returncode == 0:
            sha_sub = hashlib.sha256(out.read_bytes()).hexdigest()
            sha_disk = hashlib.sha256(MANIFEST_JSON.read_bytes()).hexdigest()
            _check("test_13b_subprocess_matches_on_disk", sha_sub == sha_disk,
                   f"sub={sha_sub[:16]} disk={sha_disk[:16]}")


# Run all
def main():
    tests = [t for name, t in sorted(globals().items()) if name.startswith("test_") and callable(t)]
    for t in tests:
        try:
            t()
        except Exception as e:
            failures.append((t.__name__, f"exception: {e}"))
            print(f"FAIL {t.__name__}: exception {e}")
    print(f"\n{len(passes)} passed, {len(failures)} failed")
    if failures:
        for n, d in failures:
            print(f"  - {n}: {d}")
        sys.exit(1)


if __name__ == "__main__":
    main()
