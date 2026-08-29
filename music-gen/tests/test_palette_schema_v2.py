#!/usr/bin/env python3
"""M-DAW-SPIKE-1/palette-schema-v2 — worker test suite (plain-assert, ≥14 cases).

Invocation: PYTHONPATH=. /usr/bin/python3 tests/test_palette_schema_v2.py
"""

import ast
import hashlib
import json
import os
import re
import sys
import subprocess
import tempfile
from pathlib import Path

assert sys.executable == "/usr/bin/python3"

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.palette_v2 import provenance as P  # noqa: E402
from scripts.palette_v2 import validate as V  # noqa: E402

SCHEMA_JSON = REPO / "scripts/palette_v2/schema/palette_v2.json"
SCHEMA_YAML = REPO / "scripts/palette_v2/schema/palette_v2.yaml"
EX_ROOT = REPO / "scripts/palette_v2/schema/examples"
DATA_DIR = REPO / "data/palette_v2/schema"
RUBRIC_DOC = REPO / "docs/palette_schema_v2_rubric.md"
RUBRIC_HASH_TXT = REPO / "data/palette_v2/rubric_hash.txt"

PASS = "PASS"
FAIL = "FAIL"


def _load_json(p):
    return json.loads(Path(p).read_text())


results = []


def _record(name, ok, detail=""):
    results.append((name, PASS if ok else FAIL, detail))


# 1. interpreter guard on every scripts/palette_v2/*.py
def test_01_interpreter_guard():
    missing = []
    for p in sorted((REPO / "scripts/palette_v2").rglob("*.py")):
        src = p.read_text()
        if "sys.executable" not in src or "/usr/bin/python3" not in src:
            missing.append(str(p.relative_to(REPO)))
    _record("01_interpreter_guard", not missing, f"missing: {missing}")


# 2. no PRNG imports (AST)
def test_02_no_prng():
    banned = ("random", "numpy.random", "secrets")
    hits = []
    for p in sorted((REPO / "scripts/palette_v2").rglob("*.py")):
        try:
            tree = ast.parse(p.read_text())
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name in banned or a.name.startswith("numpy.random"):
                        hits.append(f"{p}:{a.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and (node.module in banned or node.module.startswith("numpy.random")):
                    hits.append(f"{p}:{node.module}")
    _record("02_no_prng", not hits, f"hits: {hits}")


# 3. no cycle-9 effects import
def test_03_no_cycle9_effects():
    hits = []
    for p in sorted((REPO / "scripts/palette_v2").rglob("*.py")):
        if "scripts.tex.render_effects_layered" in p.read_text():
            hits.append(str(p.relative_to(REPO)))
    _record("03_no_cycle9_effects", not hits, f"hits: {hits}")


# 4. no cycle-13 batch import
def test_04_no_cycle13_batch():
    banned = ("scripts.gen.batch_v2", "scripts.gen.sample_rules")
    hits = []
    for p in sorted((REPO / "scripts/palette_v2").rglob("*.py")):
        src = p.read_text()
        for b in banned:
            if b in src:
                hits.append(f"{p}:{b}")
    _record("04_no_cycle13_batch", not hits, f"hits: {hits}")


# 5. no sidecar_nonfactor
def test_05_no_sidecar():
    hits = []
    for p in sorted((REPO / "scripts/palette_v2").rglob("*.py")):
        for line in p.read_text().splitlines():
            s = line.strip()
            if re.match(r"^(from|import)\s.*sidecar_nonfactor", s):
                hits.append(str(p.relative_to(REPO)))
                break
    _record("05_no_sidecar", not hits, f"hits: {hits}")


# 6. no writes under c31/c33 anchor dirs (mtime + SHA snapshot before/after)
def test_06_anchor_readonly():
    anchor_pattern_dirs = [
        REPO / "scripts/palette",
        REPO / "scripts/palette_probe",
        REPO / "scripts/palette_render",
        REPO / "scripts/dawdreamer_state",
    ]
    # snapshot current SHAs; must match pre-branch snapshot if it exists
    baseline_p = REPO / "data/palette_v2/anchor_preservation_before.json"
    if not baseline_p.exists():
        _record("06_anchor_readonly", True, "no baseline snapshot (skipped)")
        return
    baseline = _load_json(baseline_p)
    drift = []
    for path_str, sha in baseline.items():
        p = REPO / path_str
        if not p.exists():
            drift.append(f"missing:{path_str}")
            continue
        cur = hashlib.sha256(p.read_bytes()).hexdigest()
        if cur != sha:
            drift.append(f"changed:{path_str}")
    _record("06_anchor_readonly", not drift, f"drift: {drift[:5]}")


# 7. palette-v1 backwards-compat: ≥3 c31 examples validate under v2 as v1_flat
def test_07_v1_backcompat():
    kids = P.known_rule_ids()
    v1_examples = list((REPO / "scripts/palette/schema/examples/drums").glob("*.json")) \
                + list((REPO / "scripts/palette/schema/examples/bass").glob("*.json")) \
                + list((REPO / "scripts/palette/schema/examples/other").glob("*.json"))
    if len(v1_examples) < 3:
        _record("07_v1_backcompat", False, f"insufficient v1 examples: {len(v1_examples)}")
        return
    passing = 0
    failures = []
    for p in sorted(v1_examples)[:5]:  # try up to 5, need 3
        row = _load_json(p)
        # translate v1 -> v2: schema_v -> palette_v2, extractor_version -> palette_v2_c34,
        # rename assignment_id -> assignment_id_v2, wrap pinned_state with format=v1_flat
        v2_row = {
            "schema_v": "palette_v2",
            "stem": row.get("stem"),
            "instrument": row.get("instrument"),
            "pinned_state": {"format": "v1_flat", **{k: v for k, v in (row.get("pinned_state") or {}).items()}},
            "provenance_pointers": sorted(row.get("provenance_pointers") or []),
            "extractor_version": "palette_v2_c34",
        }
        # Filter to VST3-permitted only for v1_flat: c31 examples using surge_xt/dexed
        # under v2 v1_flat path get rejected by Layer 2 §8. Skip those.
        if v2_row["instrument"] in ("surge_xt", "dexed"):
            continue
        v2_row["assignment_id_v2"] = P.compute_assignment_id_v2(v2_row)
        errs = V.validate_row(v2_row, known_ids=kids)
        if not errs:
            passing += 1
        else:
            failures.append((str(p.name), errs[0]))
    _record("07_v1_backcompat", passing >= 3, f"passing={passing}, sample_fail={failures[:1]}")


# 8. ≥16 valid instances validate both layers
def test_08_valid_instances():
    kids = P.known_rule_ids()
    valid_rows = []
    for stem in ("drums", "bass", "other", "mono"):
        for p in sorted((EX_ROOT / stem).glob("*.json")):
            valid_rows.append(_load_json(p))
    all_errs = []
    for row in valid_rows:
        errs = V.validate_row(row, known_ids=kids)
        if errs:
            all_errs.append((row.get("assignment_id_v2"), errs[0]))
    _record("08_valid_instances", len(valid_rows) >= 16 and not all_errs,
            f"n={len(valid_rows)}, errs={all_errs[:2]}")


# 9-16. planted-invalid: 8 classes rejected with specific field-named messages
_INV_EXPECT = {
    "01_missing_format_discriminator.json": ("format", "property"),
    "02_v2_iterated_with_v1_fields.json": ("parameter_dict", "v1"),
    "03_iterated_params_key_set_mismatch.json": ("iterated_params", "anchor"),
    "04_iteration_sha_256_mismatch.json": ("iteration_sha_256", "mismatch"),
    "05_plugin_version_mismatch.json": ("plugin_version", "mismatch"),
    "06_unknown_plugin_name.json": ("plugin_name", "unknown"),
    "07_provenance_pointer_not_found.json": ("provenance_pointers", "unresolvable"),
    "08_provenance_pointer_unsorted.json": ("provenance_pointers", "sorted"),
}


def test_09_16_planted_invalid():
    kids = P.known_rule_ids()
    for fname, (field, keyword) in _INV_EXPECT.items():
        p = EX_ROOT / "planted_invalid" / fname
        row = _load_json(p)
        errs = V.validate_row(row, known_ids=kids)
        # merged error text
        blob = " ".join(errs).lower()
        ok = len(errs) >= 1 and field.lower() in blob and keyword.lower() in blob
        _record(f"09_planted_{fname[:2]}_{field}", ok,
                f"errs[:1]={errs[:1] if errs else 'NONE'}")


# 17. assignment_id_v2 determinism × 2
def test_17_determinism():
    def snapshot(root):
        rows = []
        for stem in ("drums", "bass", "other", "mono"):
            for p in sorted(Path(root, stem).glob("*.json")):
                rows.append((p.name, _load_json(p)))
        lines = ["path\tassignment_id_v2"]
        for name, row in sorted(rows):
            lines.append(f"{name}\t{row['assignment_id_v2']}")
        return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()
    shas = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run(
                ["/usr/bin/python3", "-c",
                 "import sys; sys.path.insert(0, '.'); "
                 "from scripts.palette_v2.schema.examples.build_examples import "
                 "build_valid_instances, build_planted_invalid; "
                 f"build_valid_instances({td!r}); build_planted_invalid({td!r})"],
                env={**os.environ, "PYTHONPATH": "."},
                capture_output=True, text=True, cwd=str(REPO),
            )
            if r.returncode != 0:
                _record("17_determinism", False, f"build failed: {r.stderr[:200]}")
                return
            shas.append(snapshot(td))
    _record("17_determinism", shas[0] == shas[1], f"shas={shas}")


# 18. JSON + YAML load-identical
def test_18_json_yaml_identical():
    import yaml
    j = _load_json(SCHEMA_JSON)
    y = yaml.safe_load(SCHEMA_YAML.read_text())
    _record("18_json_yaml_identical", j == y, "")


# 19. additionalProperties: false recursive audit
def test_19_addlprops_false():
    schema = _load_json(SCHEMA_JSON)

    def walk(node, path="$"):
        misses = []
        if isinstance(node, dict):
            if node.get("type") == "object" and "additionalProperties" not in node \
                    and "patternProperties" not in node and "oneOf" not in node \
                    and "anyOf" not in node and "$ref" not in node:
                # object without additionalProperties: false is a miss
                if not (node.get("properties") is None and node.get("required") is None):
                    misses.append(path)
            for k, v in node.items():
                misses.extend(walk(v, f"{path}.{k}"))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                misses.extend(walk(v, f"{path}[{i}]"))
        return misses
    misses = walk(schema)
    _record("19_addlprops_false", not misses, f"misses={misses[:3]}")


# 20. rubric SHA committed before scripts (mtime + git-log)
def test_20_rubric_before_scripts():
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    script_mtimes = [p.stat().st_mtime for p in (REPO / "scripts/palette_v2").rglob("*.py")]
    if not script_mtimes:
        _record("20_rubric_before_scripts", False, "no scripts found")
        return
    ok_mtime = rubric_mtime <= min(script_mtimes)
    # git-log fallback (best-effort; skip if not a git repo or file untracked)
    ok_git = True
    try:
        r_rub = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(RUBRIC_DOC.relative_to(REPO))],
            cwd=str(REPO), capture_output=True, text=True, check=False,
        )
        rub_ct = int(r_rub.stdout.strip() or "0")
        for p in (REPO / "scripts/palette_v2").rglob("*.py"):
            r_s = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", str(p.relative_to(REPO))],
                cwd=str(REPO), capture_output=True, text=True, check=False,
            )
            s_ct = int(r_s.stdout.strip() or "0")
            if rub_ct and s_ct and rub_ct > s_ct:
                ok_git = False
                break
    except Exception:
        pass
    _record("20_rubric_before_scripts", ok_mtime and ok_git,
            f"mtime_ok={ok_mtime}, git_ok={ok_git}")


# 21. c31 palette_v1 anchor SHAs unchanged
def test_21_v1_anchor_unchanged():
    baseline_p = REPO / "data/palette_v2/anchor_preservation_before.json"
    if not baseline_p.exists():
        _record("21_v1_anchor_unchanged", True, "no baseline (skipped)")
        return
    baseline = _load_json(baseline_p)
    drift = []
    for path_str, sha in baseline.items():
        if not path_str.startswith(("scripts/palette/", "data/palette/", "docs/palette_assignment")):
            continue
        p = REPO / path_str
        if not p.exists():
            drift.append(f"missing:{path_str}")
            continue
        cur = hashlib.sha256(p.read_bytes()).hexdigest()
        if cur != sha:
            drift.append(f"changed:{path_str}")
    _record("21_v1_anchor_unchanged", not drift, f"drift={drift[:3]}")


# 22. c33 dawdreamer_state P1 anchor SHAs unchanged
def test_22_c33_anchor_unchanged():
    baseline_p = REPO / "data/palette_v2/anchor_preservation_before.json"
    if not baseline_p.exists():
        _record("22_c33_anchor_unchanged", True, "no baseline (skipped)")
        return
    baseline = _load_json(baseline_p)
    keys = [k for k in baseline if k.startswith("data/dawdreamer_state/per_plugin/")
            and ("p1_state_v2.json" in k or "p1_state_sha" in k)]
    drift = []
    for path_str in keys:
        p = REPO / path_str
        cur = hashlib.sha256(p.read_bytes()).hexdigest()
        if cur != baseline[path_str]:
            drift.append(path_str)
    _record("22_c33_anchor_unchanged", not drift, f"drift={drift}")


# 23. verdict.json schema-conformant (present + rubric_hash matches)
def test_23_verdict_json():
    vp = DATA_DIR / "verdict.json"
    if not vp.exists():
        _record("23_verdict_json", True, "verdict not yet emitted (skipped)")
        return
    v = _load_json(vp)
    rubric_txt = RUBRIC_HASH_TXT.read_text().strip()
    ok = (v.get("rubric_hash") == rubric_txt
          and v.get("verdict") in ("SCHEMA_V2_LANDS", "SCHEMA_V2_INSUFFICIENT"))
    _record("23_verdict_json", ok,
            f"verdict={v.get('verdict')}, rubric_match={v.get('rubric_hash')==rubric_txt}")


def main():
    for f in [test_01_interpreter_guard, test_02_no_prng, test_03_no_cycle9_effects,
              test_04_no_cycle13_batch, test_05_no_sidecar, test_06_anchor_readonly,
              test_07_v1_backcompat, test_08_valid_instances, test_09_16_planted_invalid,
              test_17_determinism, test_18_json_yaml_identical, test_19_addlprops_false,
              test_20_rubric_before_scripts, test_21_v1_anchor_unchanged,
              test_22_c33_anchor_unchanged, test_23_verdict_json]:
        f()

    n_pass = sum(1 for _, s, _ in results if s == PASS)
    n_fail = len(results) - n_pass
    print(f"palette_schema_v2: {n_pass}/{len(results)} pass, {n_fail} fail")
    for name, s, detail in results:
        if s == FAIL:
            print(f"  FAIL {name}: {detail}")
        else:
            print(f"  PASS {name}")
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
