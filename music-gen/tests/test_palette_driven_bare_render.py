#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T04:40:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render
# ---
"""Tests for M-TEX-1/palette-driven-bare-render (cycle 33 Branch A).

Run: PYTHONPATH=. /usr/bin/python3 tests/test_palette_driven_bare_render.py

Contract: plain-assert, no pytest, ≥10 named cases per research brief.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS))

fails: list[str] = []


def check(cond, msg):
    global fails
    if cond:
        print("PASS", msg)
    else:
        print("FAIL", msg)
        fails.append(msg)


BR_A_SCRIPTS = sorted((WS / "scripts" / "palette_render").glob("*.py"))
RUBRIC = WS / "docs" / "palette_driven_bare_render_rubric.md"
DATA = WS / "data" / "palette_render"


# 1) Interpreter guard on every Branch A script.
for p in BR_A_SCRIPTS:
    txt = p.read_text()
    check("assert sys.executable == \"/usr/bin/python3\"" in txt,
          f"interpreter guard present in {p.name}")

# 2) No PRNG (AST) on every Branch A script.
BAD_MODS = {"random", "numpy.random", "secrets"}
BAD_FROM = {"random", "numpy.random", "secrets"}
for p in BR_A_SCRIPTS:
    tree = ast.parse(p.read_text())
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name in BAD_MODS or n.name.startswith("numpy.random"):
                    bad.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod in BAD_FROM or mod.startswith("numpy.random"):
                bad.append(mod)
    check(not bad, f"no-PRNG AST-clean in {p.name} (found {bad})")

# 3) No cycle-9 effects import in any Branch A script.
for p in BR_A_SCRIPTS:
    txt = p.read_text()
    # We allow the string as a documented comment. We forbid an actual
    # import/from statement.
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        check("render_effects_layered" not in s or "import" not in s,
              f"{p.name}: no cycle-9 render_effects_layered import ({s[:70]!r})")

# 4) No cycle-13 batch pipeline import.
BAD_C13 = ("scripts.gen.batch_v2", "scripts.rules.sampling.i4_stratified")
for p in BR_A_SCRIPTS:
    txt = p.read_text()
    for pat in BAD_C13:
        # allow in comments/docstrings.
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith("#") or s.startswith('"'):
                continue
            check(pat not in s or "import" not in s,
                  f"{p.name}: no c13 {pat} import ({s[:70]!r})")

# 5) No sidecar_nonfactor imports (regex on line-start).
_SN_RE = re.compile(r"^\s*(from|import)\s+.*sidecar_nonfactor", re.MULTILINE)
for p in BR_A_SCRIPTS:
    check(_SN_RE.search(p.read_text()) is None,
          f"{p.name}: no sidecar_nonfactor imports")

# 6) No writes under scripts/palette/ or scripts/palette_probe/: anchor
#    preservation snapshot recorded pre/post-run.
_APREV = DATA / "anchor_preservation.json"
if _APREV.is_file():
    _ap = json.loads(_APREV.read_text())
    check(_ap.get("unchanged") is True,
          f"anchor preservation: c31 palette + palette_probe mtimes unchanged")
else:
    check(False, "anchor_preservation.json present after run_all.py")

# 7) Palette validator round-trip.
from scripts.palette.validate import validate_row
from scripts.palette.provenance import compute_assignment_id
_AJ = DATA / "assignments.jsonl"
if _AJ.is_file():
    rows = [json.loads(l) for l in _AJ.read_text().splitlines() if l.strip()]
    check(len(rows) == 3, f"assignments.jsonl has 3 rows (got {len(rows)})")
    for r in rows:
        errs = validate_row(r)
        check(not errs, f"assignment {r.get('stem')}: validate_row zero errors ({errs[:1]})")
        recomputed = compute_assignment_id(r)
        check(recomputed == r.get("assignment_id"),
              f"assignment_id round-trip for stem={r.get('stem')} "
              f"(declared={r.get('assignment_id')}, computed={recomputed})")
else:
    check(False, "assignments.jsonl present after run_all.py")

# 8) Byte-determinism × 2 on bare_combined.wav, per-stem too.
_sha1 = (DATA / "bare_combined.wav.sha.run1").read_text().strip() if (DATA / "bare_combined.wav.sha.run1").is_file() else None
_sha2 = (DATA / "bare_combined.wav.sha.run2").read_text().strip() if (DATA / "bare_combined.wav.sha.run2").is_file() else None
check(_sha1 is not None and _sha1 == _sha2,
      f"bare_combined SHA equal across runs (r1={_sha1}, r2={_sha2})")

for stem in ("drums", "bass", "other"):
    p1 = DATA / "per_stem" / stem / "render_run1.wav.sha"
    p2 = DATA / "per_stem" / stem / "render_run2.wav.sha"
    if p1.is_file() and p2.is_file():
        s1, s2 = p1.read_text().strip(), p2.read_text().strip()
        check(s1 == s2, f"per-stem {stem} SHA equal (r1={s1[:12]}, r2={s2[:12]})")
    else:
        check(False, f"per-stem {stem} SHA files present")

# 9) 8-key finite panel on both TSVs.
import math

def _read_tsv(p: Path) -> dict:
    lines = p.read_text().splitlines()
    hdr = lines[0].split("\t")
    row = lines[1].split("\t")
    return dict(zip(hdr, row))

NUM_KEYS = {"mel_l1_db", "spectral_centroid_rmse_hz",
            "rms_env_rmse", "lufs_m_rmse_lu"}
for tsv_name in ("panel_original_vs_palette.tsv", "panel_fluidsynth_vs_palette.tsv"):
    p = DATA / tsv_name
    if p.is_file():
        d = _read_tsv(p)
        check(len(d) == 8, f"{tsv_name}: exactly 8 keys (got {len(d)})")
        for k in NUM_KEYS:
            v = d.get(k, "")
            try:
                x = float(v)
                check(math.isfinite(x), f"{tsv_name}: {k}={x} finite")
            except Exception:
                check(False, f"{tsv_name}: {k} numeric-finite (got {v!r})")
    else:
        check(False, f"{tsv_name} present after run_all.py")

# 10) Rubric mtime precedes earliest script mtime under scripts/palette_render/.
if RUBRIC.is_file() and BR_A_SCRIPTS:
    rubric_mtime = RUBRIC.stat().st_mtime
    earliest_script = min(p.stat().st_mtime for p in BR_A_SCRIPTS)
    check(rubric_mtime < earliest_script,
          f"rubric mtime {rubric_mtime:.2f} < earliest script mtime {earliest_script:.2f}")
    # git-log fallback: if git available, compare first-add times.
    try:
        r_rub = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%at", "--", str(RUBRIC.relative_to(WS))],
            cwd=str(WS), capture_output=True, text=True, timeout=5)
        r_scripts = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%at", "--", "scripts/palette_render"],
            cwd=str(WS), capture_output=True, text=True, timeout=5)
        rub_add = [int(x) for x in r_rub.stdout.splitlines() if x.strip()]
        scr_add = [int(x) for x in r_scripts.stdout.splitlines() if x.strip()]
        if rub_add and scr_add:
            check(min(rub_add) <= min(scr_add),
                  f"git-log: rubric first-add {min(rub_add)} <= scripts first-add {min(scr_add)}")
        else:
            print("SKIP git-log fallback (rubric or scripts not yet in git)")
    except Exception as e:
        print(f"SKIP git-log fallback ({e})")

# 11) Verdict JSON schema-conformant.
_VJ = DATA / "verdict.json"
if _VJ.is_file():
    v = json.loads(_VJ.read_text())
    hashed = (DATA / "rubric_hash.txt").read_text().strip()
    check(v.get("rubric_hash") == hashed,
          f"verdict.rubric_hash == rubric_hash.txt")
    check(v.get("verdict") in {"PALETTE_MOVES_PANEL", "PALETTE_NEUTRAL", "RENDER_FAILS"},
          f"verdict in enum (got {v.get('verdict')})")
    doc_hash = hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    check(doc_hash == hashed,
          f"rubric doc SHA == rubric_hash.txt")
else:
    check(False, "verdict.json present after run_all.py")

# 12) Fetchability ladder present.
_FL = DATA / "fetchability_ladder.jsonl"
check(_FL.is_file(), "fetchability_ladder.jsonl present")

print()
print(f"result: {'PASS' if not fails else 'FAIL'} ({len(fails)} failures)")
sys.exit(1 if fails else 0)
