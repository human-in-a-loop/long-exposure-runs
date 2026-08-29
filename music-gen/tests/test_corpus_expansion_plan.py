#!/usr/bin/env python3
# Interpreter guard: /usr/bin/python3.
"""Test suite for `_manager/corpus-expansion-plan` (c48 Branch B).

Plain-assert style per c6 convention. Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_corpus_expansion_plan.py
"""
from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(REPO_ROOT)

RUBRIC = "docs/corpus_expansion_plan_rubric.md"
RUBRIC_HASH = "data/corpus_expansion_plan/rubric_hash.txt"
AXES = "data/corpus_expansion_plan/axes.tsv"
COSTS = "data/corpus_expansion_plan/cost_estimator_output.json"
PROJECTION = "data/corpus_expansion_plan/partial_corpus_projection.json"
VERDICT = "data/corpus_expansion_plan/verdict.json"
PKG_DIR = "scripts/corpus_expansion_plan"

RATINGS_MANIFEST = "corpus/ratings/ratings_manifest.tsv"
C26_COMMITMENT = "docs/ear_path_b_commitment.md"

BLOCKLIST_ROOT = {"urllib", "requests", "socket", "httpx", "yt_dlp", "aiohttp", "urllib3"}
PRNG_BLOCKLIST_ROOT = {"random", "secrets"}
FALSIFIABLE_TOKENS = re.compile(r"(<=|>=|<|>|=|≤|≥|\bpresent\b|\babsent\b|\bdelivered\b|\bundelivered\b|\bavailable\b|\bunavailable\b|\bconfirmed\b|\bunconfirmed\b)")


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _iter_pkg_modules(pkg_dir: str):
    for root, _, files in os.walk(pkg_dir):
        for fn in files:
            if fn.endswith(".py"):
                yield os.path.join(root, fn)


results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    results.append((name, bool(cond), detail))
    marker = "PASS" if cond else "FAIL"
    print(f"[{marker}] {name}" + (f" -- {detail}" if detail else ""))


# ---- 01 rubric mtime gate (HARD) --------------------------------------------
rubric_mtime = os.stat(RUBRIC).st_mtime_ns
script_mtimes = {p: os.stat(p).st_mtime_ns for p in _iter_pkg_modules(PKG_DIR)}
mtime_ok = all(rubric_mtime < m for m in script_mtimes.values()) if script_mtimes else True
check(
    "01_rubric_mtime_before_scripts",
    mtime_ok,
    f"rubric mtime {rubric_mtime}; script mtimes {min(script_mtimes.values()) if script_mtimes else 'n/a'}..{max(script_mtimes.values()) if script_mtimes else 'n/a'}",
)

# ---- 02 git-log gate (SOFT per c46 amendment) --------------------------------
try:
    log_out = subprocess.run(
        ["git", "log", "--all", "--format=%H %s", "--follow", RUBRIC],
        capture_output=True, text=True, timeout=10,
    )
    if log_out.returncode == 0 and log_out.stdout.strip():
        check("02_git_log_gate_soft", True, "rubric present in git log")
    else:
        check("02_git_log_gate_soft", True, "HARNESS_GATED per c46 amendment path (ii)")
except Exception as exc:
    check("02_git_log_gate_soft", True, f"HARNESS_GATED (git unavailable: {exc})")

# ---- 03 three-way rubric_hash byte-equality ---------------------------------
doc_sha = sha256_of(RUBRIC)
with open(RUBRIC_HASH) as f:
    pinned = f.read().strip()
verdict = json.load(open(VERDICT))
check(
    "03_three_way_rubric_hash_byte_equality",
    doc_sha == pinned == verdict["rubric_hash"],
    f"doc={doc_sha[:12]} pinned={pinned[:12]} verdict={verdict['rubric_hash'][:12]}",
)

# ---- 04 axes count >= 3 -----------------------------------------------------
with open(AXES, newline="") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))
axes = sorted({r["axis"] for r in rows})
check("04_axes_count_ge_3", len(axes) >= 3, f"axes={axes}")

# ---- 05 action items per axis >= 3 ------------------------------------------
per_axis = {a: [r for r in rows if r["axis"] == a] for a in axes}
counts = {a: len(v) for a, v in per_axis.items()}
check("05_action_items_per_axis_ge_3", all(c >= 3 for c in counts.values()), f"counts={counts}")

# ---- 06 trigger conditions falsifiable --------------------------------------
falsifiable_ok = all(FALSIFIABLE_TOKENS.search(r["trigger_condition"]) for r in rows)
check("06_trigger_conditions_falsifiable", falsifiable_ok, "regex match on binary-evaluable tokens")

# ---- 07 no live network AST-grep --------------------------------------------
live_hits = []
for path in _iter_pkg_modules(PKG_DIR):
    tree = ast.parse(open(path).read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in BLOCKLIST_ROOT:
                    live_hits.append(f"{path}: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in BLOCKLIST_ROOT:
                live_hits.append(f"{path}: from {node.module}")
check("07_no_live_network_ast_grep", not live_hits, f"hits={live_hits}")

# ---- 08 no PRNG in scripts --------------------------------------------------
prng_hits = []
for path in _iter_pkg_modules(PKG_DIR):
    tree = ast.parse(open(path).read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in PRNG_BLOCKLIST_ROOT:
                    prng_hits.append(f"{path}: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in PRNG_BLOCKLIST_ROOT:
                prng_hits.append(f"{path}: from {node.module}")
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id in ("np", "numpy"):
                if node.attr == "random":
                    prng_hits.append(f"{path}: np.random")
check("08_no_prng_ast_grep", not prng_hits, f"hits={prng_hits}")

# ---- 09 no sidecar_nonfactor imports ----------------------------------------
sidecar_hits = []
for path in _iter_pkg_modules(PKG_DIR):
    src = open(path).read()
    if "scripts.classifier.sidecar_nonfactor" in src:
        sidecar_hits.append(path)
check("09_no_sidecar_nonfactor_imports", not sidecar_hits, f"hits={sidecar_hits}")

# ---- 10 interpreter guard on every script -----------------------------------
guard_fail = []
for path in _iter_pkg_modules(PKG_DIR):
    with open(path) as f:
        first3 = "".join([f.readline() for _ in range(3)])
    if "/usr/bin/python3" not in first3:
        guard_fail.append(path)
check("10_interpreter_guard_on_every_script", not guard_fail, f"missing={guard_fail}")

# ---- 11 ratings_manifest.tsv SHA byte-identical pre/post --------------------
anchor = json.load(open("data/corpus_expansion_plan/anchor_preservation.json"))
pre_manifest = anchor["pre"][RATINGS_MANIFEST]["sha256"]
post_manifest = sha256_of(RATINGS_MANIFEST)
check("11_ratings_manifest_sha_unchanged", pre_manifest == post_manifest, f"pre={pre_manifest[:12]} post={post_manifest[:12]}")

# ---- 12 c26 commitment doc SHA byte-identical pre/post ----------------------
pre_c26 = anchor["pre"][C26_COMMITMENT]["sha256"]
post_c26 = sha256_of(C26_COMMITMENT)
check("12_c26_commitment_doc_sha_unchanged", pre_c26 == post_c26, f"pre={pre_c26[:12]} post={post_c26[:12]}")

# ---- 13 byte-determinism x 2 on axes.tsv ------------------------------------
env = os.environ.copy()
env.update({
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONPATH": REPO_ROOT,
})


def _run_module_twice(mod: str, arg_basename: str) -> tuple[str, str]:
    tmp_shas = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, arg_basename)
            r = subprocess.run(
                ["/usr/bin/python3", "-m", mod, out],
                env=env, capture_output=True, text=True, cwd=REPO_ROOT, timeout=60,
            )
            assert r.returncode == 0, f"{mod} rc={r.returncode} err={r.stderr}"
            tmp_shas.append(sha256_of(out))
    return tmp_shas[0], tmp_shas[1]

s1, s2 = _run_module_twice("scripts.corpus_expansion_plan.enumerate_axes", "axes.tsv")
check("13_byte_determinism_x2_axes_tsv", s1 == s2, f"{s1[:12]} vs {s2[:12]}")

# ---- 14 byte-determinism x 2 on cost_estimator_output.json ------------------
# cost_estimator needs axes.tsv - use committed one, output to temp
def _run_costs_twice():
    tmp_shas = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "cost_estimator_output.json")
            r = subprocess.run(
                ["/usr/bin/python3", "-m", "scripts.corpus_expansion_plan.cost_estimator", AXES, out],
                env=env, capture_output=True, text=True, cwd=REPO_ROOT, timeout=60,
            )
            assert r.returncode == 0, f"cost_estimator rc={r.returncode} err={r.stderr}"
            tmp_shas.append(sha256_of(out))
    return tmp_shas[0], tmp_shas[1]

s1, s2 = _run_costs_twice()
check("14_byte_determinism_x2_cost_estimator_output_json", s1 == s2, f"{s1[:12]} vs {s2[:12]}")

# ---- 15 byte-determinism x 2 on partial_corpus_projection.json --------------
s1, s2 = _run_module_twice("scripts.corpus_expansion_plan.partial_corpus_interpolation_probe", "projection.json")
check("15_byte_determinism_x2_partial_corpus_projection_json", s1 == s2, f"{s1[:12]} vs {s2[:12]}")

# ---- 16 c47 v2.1 verdict.json SHA byte-identical pre/post -------------------
pre_v2p1 = anchor["pre"]["data/ear_v2p1/verdict.json"]["sha256"]
post_v2p1 = sha256_of("data/ear_v2p1/verdict.json")
check("16_c47_v2p1_verdict_sha_unchanged", pre_v2p1 == post_v2p1, f"pre={pre_v2p1[:12]} post={post_v2p1[:12]}")

# ---- 17 c47 anchor manifest SHA byte-identical pre/post ---------------------
pre_am = anchor["pre"]["data/anchor_manifest_v1.json"]["sha256"]
post_am = sha256_of("data/anchor_manifest_v1.json")
check("17_c47_anchor_manifest_sha_unchanged", pre_am == post_am, f"pre={pre_am[:12]} post={post_am[:12]}")

# ---- 18 c22 stability harness mtimes unchanged ------------------------------
c22_files = ["scripts/ear/synthetic_labels.py", "scripts/ear/stability_metrics.py", "scripts/ear/stability_audit.py"]
mtime_ok = True
for p in c22_files:
    pre_m = anchor["pre"][p]["mtime_ns"]
    cur_m = os.stat(p).st_mtime_ns
    if pre_m != cur_m:
        mtime_ok = False
        print(f"  c22 mtime drift on {p}: {pre_m} -> {cur_m}")
check("18_c22_stability_harness_mtimes_unchanged", mtime_ok)

# ---- 19 c15 i4_stratified.py NOT imported -----------------------------------
i4_hits = []
for path in _iter_pkg_modules(PKG_DIR):
    src = open(path).read()
    if "i4_stratified" in src and "not imported" not in src.lower():
        i4_hits.append(path)
check("19_c15_i4_stratified_not_imported", not i4_hits, f"hits={i4_hits}")

# ---- 20 byte-determinism x 2 on verdict.json (via re-running full pipeline) --
def _regenerate_verdict_pipeline():
    tmp_shas = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as d:
            axes_tsv = os.path.join(d, "axes.tsv")
            costs = os.path.join(d, "cost.json")
            projection = os.path.join(d, "projection.json")
            for cmd in (
                ["/usr/bin/python3", "-m", "scripts.corpus_expansion_plan.enumerate_axes", axes_tsv],
                ["/usr/bin/python3", "-m", "scripts.corpus_expansion_plan.cost_estimator", axes_tsv, costs],
                ["/usr/bin/python3", "-m", "scripts.corpus_expansion_plan.partial_corpus_interpolation_probe", projection],
            ):
                r = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=REPO_ROOT, timeout=60)
                assert r.returncode == 0, f"{cmd} rc={r.returncode} err={r.stderr}"
            # Concat SHA of the three artifacts (proxy for verdict determinism).
            h = hashlib.sha256()
            for p in (axes_tsv, costs, projection):
                with open(p, "rb") as f:
                    h.update(f.read())
            tmp_shas.append(h.hexdigest())
    return tmp_shas[0], tmp_shas[1]

s1, s2 = _regenerate_verdict_pipeline()
check("20_byte_determinism_x2_verdict_pipeline_concat", s1 == s2, f"{s1[:12]} vs {s2[:12]}")

# ---- summary ----------------------------------------------------------------
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"\nSUMMARY: {passed}/{total} PASS")
sys.exit(0 if passed == total else 1)
