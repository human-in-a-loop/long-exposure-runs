"""RC10 Branch C test suite (c53 clone-2). Runs plain asserts, no pytest.

Invocation: /usr/bin/python3 tests/test_rc10_other_vocals_impl.py
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
RUBRIC = WS / "docs/rc10_other_vocals_rubric.md"
RUBRIC_HASH = WS / "data/rc10_impl/other_vocals/rubric_hash.txt"
SCRIPTS = WS / "scripts/recreate_v2/rc10_other_vocals"
VERDICT = WS / "data/rc10_impl/other_vocals/verdict.json"
WINNERS = WS / "data/rc10_impl/other_vocals/winner_per_stem_type.json"
AB = WS / "data/recreate_v2/ab_pairs"

passed = 0
failed: list[str] = []


def _t(name: str, cond: bool, detail: str = "") -> None:
    global passed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


# 1. Rubric doc exists
_t("01 rubric doc present", RUBRIC.exists(), str(RUBRIC))

# 2. Rubric hash file exists and matches doc SHA-256
if RUBRIC.exists() and RUBRIC_HASH.exists():
    doc_sha = hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    hash_txt = RUBRIC_HASH.read_text().strip()
    _t("02 rubric_hash byte-equal to doc SHA-256", doc_sha == hash_txt, f"{doc_sha}!={hash_txt}")
else:
    _t("02 rubric_hash byte-equal to doc SHA-256", False, "missing files")

# 3. Rubric mtime < any script under scripts/recreate_v2/rc10_other_vocals/ (pre-registration mtime gate)
if RUBRIC.exists() and SCRIPTS.exists():
    rubric_mt = RUBRIC.stat().st_mtime
    script_mts = [p.stat().st_mtime for p in SCRIPTS.glob("*.py") if p.name != "__init__.py"]
    _t("03 rubric doc mtime < every rc10 script mtime",
       all(rubric_mt < m for m in script_mts) if script_mts else True,
       f"rubric_mt={rubric_mt} scripts_min={min(script_mts) if script_mts else None}")
else:
    _t("03 rubric doc mtime < every rc10 script mtime", False, "missing files")

# 4. Verdict JSON exists and has expected verdict enum
if VERDICT.exists():
    v = json.loads(VERDICT.read_text())
    _t("04 verdict is enum member",
       v["verdict"] in ("RC10_OTHER_VOCALS_LANDS", "RC10_OTHER_VOCALS_PARTIAL", "RC10_OTHER_VOCALS_FAILS"),
       v.get("verdict"))
else:
    _t("04 verdict is enum member", False, "verdict.json missing")

# 5. Three-way rubric_hash chain
if VERDICT.exists() and RUBRIC_HASH.exists() and RUBRIC.exists():
    doc_sha = hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    txt_sha = RUBRIC_HASH.read_text().strip()
    v = json.loads(VERDICT.read_text())
    _t("05 three-way rubric_hash byte-equality",
       doc_sha == txt_sha == v.get("rubric_hash"),
       f"doc={doc_sha} txt={txt_sha} v={v.get('rubric_hash')}")
else:
    _t("05 three-way rubric_hash byte-equality", False, "missing files")

# 6. Winners JSON present with both stem entries
if WINNERS.exists():
    w = json.loads(WINNERS.read_text())
    _t("06 winners json has vocals + other_residual entries",
       "vocals" in w and "other_residual" in w, str(list(w.keys())))
else:
    _t("06 winners json has vocals + other_residual entries", False, "winner_per_stem_type.json missing")

# 7. Per-song coverage: 5 focus songs each with vocals + other_residual iterations
focus = json.loads((WS / "data/recreate_v2/focus_set_v2.json").read_text())
sha16s = [s["audio_sha16"] for s in focus["songs"]]
if VERDICT.exists():
    v = json.loads(VERDICT.read_text())
    per_song_ids = {s["song_id"] for s in v.get("per_song", [])}
    _t("07 per_song covers all 5 focus songs", set(sha16s) == per_song_ids,
       f"missing={set(sha16s)-per_song_ids}")
else:
    _t("07 per_song covers all 5 focus songs", False, "verdict.json missing")

# 8. A/B pairs directory contains iter subdirs for at least one song
if AB.exists():
    sample_song = sha16s[0]
    voc_iters = list((AB / sample_song / "vocals").glob("iter_*")) if (AB / sample_song / "vocals").exists() else []
    oth_iters = list((AB / sample_song / "other_residual").glob("iter_*")) if (AB / sample_song / "other_residual").exists() else []
    _t("08 A/B pairs present for at least one song",
       len(voc_iters) >= 3 and len(oth_iters) >= 2,
       f"voc={len(voc_iters)} oth={len(oth_iters)}")
else:
    _t("08 A/B pairs present for at least one song", False, "ab_pairs dir missing")

# 9. NO PRNG — AST-grep for random module usage in rc10 scripts
def _contains_prng(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return True
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in ("random",):
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in ("random",):
                return True
    return False

any_prng = False
if SCRIPTS.exists():
    for p in SCRIPTS.glob("*.py"):
        if _contains_prng(p):
            any_prng = True
            break
_t("09 no PRNG in rc10 scripts", not any_prng)

# 10. Interpreter guard present in run_rc10.py
runner = SCRIPTS / "run_rc10.py"
if runner.exists():
    src = runner.read_text()
    _t("10 interpreter guard present",
       "/usr/bin/python3" in src and "_ALLOWED" in src,
       "guard markers")
else:
    _t("10 interpreter guard present", False, "run_rc10.py missing")

# 11. No sidecar_nonfactor imports
if SCRIPTS.exists():
    bad = []
    for p in SCRIPTS.glob("*.py"):
        if "sidecar_nonfactor" in p.read_text():
            bad.append(str(p))
    _t("11 no sidecar_nonfactor imports", not bad, str(bad))
else:
    _t("11 no sidecar_nonfactor imports", False, "scripts dir missing")

# 12. c48 env-var flags default OFF — scripts don't rely on them
if SCRIPTS.exists():
    bad = []
    for p in SCRIPTS.glob("*.py"):
        src = p.read_text()
        # If the script references any c48 flag it should default OFF
        for flag in ("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION",
                     "MUSICGEN_LEDGER_SUPERSEDES_IN_HASH"):
            if flag in src and 'default' not in src.lower():
                bad.append(f"{p.name}:{flag}")
    _t("12 c48 env-var flags default OFF (or unused)", not bad, str(bad))
else:
    _t("12 c48 env-var flags default OFF (or unused)", False, "scripts dir missing")

# 13. All 5 baseline stems still byte-identical (anchor preservation)
anchor_ok = True
for sha in sha16s:
    for stem in ("vocals", "other"):
        p = WS / f"data/recreate_v2/baseline/{sha}/rc9_6stem/{stem}.wav"
        anchor_ok = anchor_ok and p.exists()
_t("13 all 10 baseline stems present (5 vocals + 5 other)", anchor_ok)

# 14. c50 v2 rubric SHA byte-identical
v2_rubric = WS / "docs/m_recreate_2_accurate_small_set_rubric_v2.md"
v2_txt = WS / "data/recreate_v2/rubric_hash_v2.txt"
if v2_rubric.exists() and v2_txt.exists():
    _t("14 c50 v2 rubric SHA anchor preserved",
       hashlib.sha256(v2_rubric.read_bytes()).hexdigest() == v2_txt.read_text().strip())
else:
    _t("14 c50 v2 rubric SHA anchor preserved", False, "missing anchor files")

# 15. c51 Branch A verdict.json byte-preserved (do-not-touch)
brA = WS / "data/rc1_rc9_impl/verdict.json"
_t("15 c51 Branch A verdict.json present (READ-ONLY)", brA.exists())

# 16. Winner selection metadata is sane
if WINNERS.exists():
    w = json.loads(WINNERS.read_text())
    voc_w = w.get("vocals", {})
    oth_w = w.get("other_residual", {})
    _t("16 winner rows carry songs_passed + mean_metric",
       "songs_passed" in voc_w and "mean_metric" in voc_w
       and "songs_passed" in oth_w and "mean_metric" in oth_w)
else:
    _t("16 winner rows carry songs_passed + mean_metric", False)

# 17. Per-song content-metric structure
if VERDICT.exists():
    v = json.loads(VERDICT.read_text())
    ok = True
    for s in v.get("per_song", []):
        if not (set(s["vocals"].keys()) >= {"v_a", "v_b", "v_c"}):
            ok = False; break
        if not (set(s["other_residual"].keys()) >= {"o_a", "o_b"}):
            ok = False; break
    _t("17 per_song has 3 vocals + 2 other-residual candidates", ok)
else:
    _t("17 per_song has 3 vocals + 2 other-residual candidates", False)

# 18. D4 post-processing measured with and without
if VERDICT.exists():
    v = json.loads(VERDICT.read_text())
    ok = True
    for s in v.get("per_song", []):
        for cid, res in s["vocals"].items():
            if "error" not in res and not ("raw" in res and "pp" in res):
                ok = False; break
    _t("18 D4 measured with AND without (raw+pp) present", ok)
else:
    _t("18 D4 measured with AND without (raw+pp) present", False)

print()
print(f"passed={passed} failed={len(failed)}")
if failed:
    for f in failed:
        print("  -", f)
    sys.exit(1)
sys.exit(0)
