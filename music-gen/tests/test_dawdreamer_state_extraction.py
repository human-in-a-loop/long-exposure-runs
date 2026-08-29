#!/usr/bin/env -S /usr/bin/python3
"""Cycle-33 clone-1 test suite for M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround.

Run: PYTHONPATH=. /usr/bin/python3 tests/test_dawdreamer_state_extraction.py
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS))
DR = WS / "scripts" / "dawdreamer_state"
DD = WS / "data" / "dawdreamer_state"
RUB = WS / "docs" / "dawdreamer_state_extraction_rubric.md"
RH = DD / "rubric_hash.txt"
VJP = DD / "verdict.json"

fail = 0
def check(cond, msg):
    global fail
    if cond:
        print("PASS", msg)
    else:
        print("FAIL", msg); fail += 1


PROBE_SCRIPTS = [
    "_shared.py",
    "probe_p1_iterate_parameters.py",
    "probe_p2_save_preset.py",
    "probe_p3_metadata_inspection.py",
    "run_all.py",
]

# 1. Interpreter guard present in every script under scripts/dawdreamer_state/*.py
for fn in PROBE_SCRIPTS:
    p = DR / fn
    if not p.is_file():
        check(False, f"1. missing {fn}"); continue
    src = p.read_text()
    check("assert sys.executable == '/usr/bin/python3'" in src or
          'assert sys.executable == "/usr/bin/python3"' in src,
          f"1. interpreter guard present in {fn}")

# 2. AST no-PRNG grep clean across scripts/dawdreamer_state/*
for fn in PROBE_SCRIPTS:
    p = DR / fn
    if not p.is_file(): continue
    src = p.read_text()
    bad = [tok for tok in ("random.", "numpy.random.", "torch.rand", "random_state=")
           if tok in src]
    check(not bad, f"2. no-PRNG grep clean in {fn} (bad={bad})")

# 3. No import of scripts.tex.render_effects_layered (AST-checked, not docstring-mentioned).
for fn in PROBE_SCRIPTS:
    p = DR / fn
    if not p.is_file(): continue
    src = p.read_text()
    tree = ast.parse(src)
    bad = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if "render_effects_layered" in a.name or a.name.startswith("scripts.tex"):
                    bad = True
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if "render_effects_layered" in mod or mod.startswith("scripts.tex"):
                bad = True
    check(not bad, f"3. no cycle-9 effects chain import in {fn} (AST)")

# 4. No import of scripts.classifier.sidecar_nonfactor
for fn in PROBE_SCRIPTS:
    p = DR / fn
    if not p.is_file(): continue
    src = p.read_text()
    check("sidecar_nonfactor" not in src,
          f"4. no sidecar_nonfactor import in {fn}")

# 5. No writes under c31 palette anchor directories.
# Enforced by checking for write-side call patterns co-located with anchor
# paths. Documentation mentions of the paths are allowed (this file
# describes the read-only-anchor contract in its own docstrings).
anchor_prefixes = ("scripts/palette/", "scripts/palette_probe/",
                   "scripts/tex/", "scripts/ear/", "scripts/gen/",
                   "data/palette/", "data/palette_probe/")
write_verbs = ("write_text(", "write_bytes(", "mkdir(", 'open(', ".dump(", ".dumps(")
for fn in PROBE_SCRIPTS:
    p = DR / fn
    if not p.is_file(): continue
    src = p.read_text()
    hit = []
    for ap in anchor_prefixes:
        # Look for lines that contain the anchor prefix AND a write verb.
        for line in src.splitlines():
            if ap in line and any(v in line for v in write_verbs):
                # Allow the interpreter guard's `open(` on paths we own.
                hit.append((ap, line.strip()[:80]))
    check(not hit,
          f"5. no writes co-located with anchor path in {fn} (hit={hit})")

# 6. Byte-determinism × 2 on P1 for Surge XT (from persisted verdict.json).
# 7. Byte-determinism × 2 on P1 for Dexed.
# 8. Byte-determinism × 2 on P2 or documented fetchability row.
# 9. Byte-determinism × 2 on P3 for both plugins.
if VJP.is_file():
    vj = json.loads(VJP.read_text())
    pp = vj["per_plugin"]
    check(pp["surge_xt"]["P1"]["equal"] and not pp["surge_xt"]["P1"]["empty"],
          "6. P1 byte-deterministic non-empty on surge_xt")
    check(pp["dexed"]["P1"]["equal"] and not pp["dexed"]["P1"]["empty"],
          "7. P1 byte-deterministic non-empty on dexed")
    # P2 partial acceptance: at least one plugin passes OR fetchability row present.
    p2_any = any(pp[k]["P2"]["equal"] and not pp[k]["P2"]["empty"]
                 for k in ("surge_xt", "dexed"))
    fp = DD / "fetchability_ladder.jsonl"
    fp_has_p2 = fp.is_file() and any(
        json.loads(ln).get("probe") == "P2"
        for ln in fp.read_text().splitlines() if ln.strip()
    )
    check(p2_any or fp_has_p2,
          "8. P2 either byte-deterministic on ≥1 plugin OR fetchability documented")
    check(pp["surge_xt"]["P3"]["equal"] and not pp["surge_xt"]["P3"]["empty"],
          "9a. P3 byte-deterministic non-empty on surge_xt")
    check(pp["dexed"]["P3"]["equal"] and not pp["dexed"]["P3"]["empty"],
          "9b. P3 byte-deterministic non-empty on dexed")
else:
    check(False, "6-9. verdict.json missing")

# 10. Rubric SHA committed before probe scripts land (file-mtime ordering).
if RUB.is_file():
    rmt = RUB.stat().st_mtime
    emts = [(DR / fn).stat().st_mtime for fn in PROBE_SCRIPTS if (DR / fn).is_file()]
    check(all(rmt <= e for e in emts),
          f"10. rubric mtime <= earliest probe script mtime")
else:
    check(False, "10. rubric doc missing")

# 11. Verdict JSON schema-conformant.
if VJP.is_file():
    vj = json.loads(VJP.read_text())
    required = ("rubric_hash", "verdict", "per_plugin", "per_path",
                "midi_input_sha256", "committed_at", "winning_path")
    for k in required:
        check(k in vj, f"11. verdict.json has key {k!r}")
    check(vj["verdict"] in {"WORKAROUND_FOUND", "PARTIAL_WORKAROUND", "NO_WORKAROUND"},
          f"11. verdict enum ({vj.get('verdict')})")
    # Rubric hash chain: doc ↔ rubric_hash.txt ↔ verdict.json.rubric_hash
    if RUB.is_file() and RH.is_file():
        doc_sha = hashlib.sha256(RUB.read_bytes()).hexdigest()
        file_sha = RH.read_text().strip()
        check(doc_sha == file_sha, "11. doc SHA == rubric_hash.txt")
        check(vj["rubric_hash"] == file_sha, "11. verdict.json rubric_hash == rubric_hash.txt")

# 12. Three probe modules callable in isolation.
env = dict(os.environ)
env["PYTHONPATH"] = str(WS)
for mod in ("probe_p1_iterate_parameters",
            "probe_p2_save_preset",
            "probe_p3_metadata_inspection"):
    r = subprocess.run(
        ["/usr/bin/python3", "-c",
         f"from scripts.dawdreamer_state.{mod} import main; assert callable(main)"],
        env=env, capture_output=True, text=True, cwd=str(WS),
    )
    check(r.returncode == 0,
          f"12. isolation import: {mod} (rc={r.returncode}, err={r.stderr.strip()[:120]})")

# Bonus 13: every probe script has `if __name__ == \"__main__\": main()` (or SystemExit variant).
for fn in ("probe_p1_iterate_parameters.py",
           "probe_p2_save_preset.py",
           "probe_p3_metadata_inspection.py",
           "run_all.py"):
    p = DR / fn
    if not p.is_file(): continue
    src = p.read_text()
    check('if __name__ == "__main__":' in src,
          f"13. {fn} has `if __name__ == \"__main__\":` guard")

print()
print(f"result: {'PASS' if fail == 0 else 'FAIL'} ({fail} failures)")
sys.exit(1 if fail else 0)
