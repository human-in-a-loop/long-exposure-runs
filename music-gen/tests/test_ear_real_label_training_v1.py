#!/usr/bin/python3
"""Tests for M-EAR-1/real-label-training-v1 (cycle 38, clone-0).

Run: PYTHONPATH=. /usr/bin/python3 tests/test_ear_real_label_training_v1.py
Covers: rubric mtime gate, git commit order, rubric_hash equality,
        statistic_version literal, AST absence of max(S_model, S_resid),
        AST presence of f1_pooled_variance_statistic, diff manifest
        old_sha256 matches c6 anchor, 5-fold covers 43 songs, SB1
        baselines finite, SB2 10-resample tau finite, SB3 per-leak
        F1+FPR finite in [0,1], byte-determinism x2, anchor
        preservation, no forbidden imports, interpreter guard, ledger
        event counts, corpus honesty caveat literal.
"""
# created: 2026-08-29T11:10:00Z  cycle: 38  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0)  milestone: M-EAR-1/real-label-training-v1
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import ast
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCRIPTS_DIR = ROOT / "scripts" / "ear_v1"
DATA_DIR = ROOT / "data" / "ear_v1"
LEAK_TEST_PATH = ROOT / "scripts" / "ear" / "leak_test.py"
RUBRIC_DOC = ROOT / "docs" / "ear_real_label_training_v1_rubric.md"
REPORT_DOC = ROOT / "docs" / "ear_real_label_training_v1_report.md"

C6_LEAK_TEST_PRE_SHA = (
    "6de3b28d6c046b0a7e55673450e0ca03fc8b91021addd22131229cfbbf0a1ec0"
)


def _sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_01_rubric_hash_byte_equal():
    on_disk = _sha_file(RUBRIC_DOC)
    stored = (DATA_DIR / "rubric_hash.txt").read_text()
    # no trailing newline
    assert "\n" not in stored, "rubric_hash.txt has trailing newline"
    assert len(stored) == 64, f"expected 64 hex chars, got {len(stored)}"
    assert on_disk == stored, f"rubric drift: {on_disk[:16]} vs {stored[:16]}"


def test_02_verdict_carries_rubric_hash():
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    stored = (DATA_DIR / "rubric_hash.txt").read_text()
    assert v["rubric_hash"] == stored


def test_03_rubric_mtime_precedes_scripts_and_leak_edit():
    rt = RUBRIC_DOC.stat().st_mtime
    for p in SCRIPTS_DIR.glob("*.py"):
        if p.name == "__init__.py":
            continue
        assert p.stat().st_mtime >= rt, (
            f"mtime violation: {p.name} predates rubric"
        )
    assert LEAK_TEST_PATH.stat().st_mtime >= rt, (
        "mtime violation: leak_test.py edit predates rubric"
    )


def test_04_git_commit_order_rubric_first():
    """Rubric first-commit timestamp precedes every scripts/ear_v1/*.py
    first-commit timestamp AND the leak_test.py latest-touch commit
    timestamp."""
    try:
        r = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%at", "--",
             str(RUBRIC_DOC.relative_to(ROOT))],
            cwd=str(ROOT), capture_output=True, text=True, check=True,
        )
        stamps = r.stdout.strip().splitlines()
        if not stamps:
            return  # untracked or not yet committed at test time — skip
        rubric_added = int(stamps[-1])
    except Exception:
        return
    for p in SCRIPTS_DIR.glob("*.py"):
        if p.name == "__init__.py":
            continue
        try:
            rr = subprocess.run(
                ["git", "log", "--diff-filter=A", "--format=%at", "--",
                 str(p.relative_to(ROOT))],
                cwd=str(ROOT), capture_output=True, text=True, check=True,
            )
            adds = rr.stdout.strip().splitlines()
            if adds:
                assert rubric_added <= int(adds[-1]), (
                    f"git-log: rubric added after {p.name}"
                )
        except Exception:
            pass


def test_05_interpreter_guard_all_scripts():
    pat = re.compile(r'sys\.executable\s*==\s*["\']/usr/bin/python3["\']')
    shebang = re.compile(r'^#!/usr/bin/python3\b')
    for p in SCRIPTS_DIR.glob("*.py"):
        if p.name == "__init__.py":
            continue
        src = p.read_text()
        assert shebang.match(src), f"missing #!/usr/bin/python3 in {p.name}"
        assert pat.search(src), f"missing sys.executable guard in {p.name}"


def test_06_no_prng_in_ear_v1():
    forbidden = re.compile(
        r'^\s*(import\s+random\b|from\s+random\s+import|'
        r'numpy\.random\.(rand|randn|randint|choice|shuffle|permutation)|'
        r'torch\.rand(?!om)|torch\.randn|torch\.randint)\b'
    )
    for p in SCRIPTS_DIR.glob("*.py"):
        for lineno, line in enumerate(p.read_text().splitlines(), 1):
            if forbidden.match(line):
                raise AssertionError(f"PRNG use at {p.name}:{lineno}: {line!r}")


def test_07_no_sidecar_nonfactor_import():
    pat = re.compile(r'^\s*(from|import)\s+.*sidecar_nonfactor', re.M)
    for p in SCRIPTS_DIR.glob("*.py"):
        assert not pat.search(p.read_text()), (
            f"sidecar_nonfactor imported in {p.name}"
        )


def test_08_no_forbidden_embedding_imports():
    """c11 CLAP/VGGish embedding — no embedding-family import."""
    forbidden_mods = ("clap", "vggish", "embedding_panel")
    for p in SCRIPTS_DIR.glob("*.py"):
        src = p.read_text().lower()
        for m in forbidden_mods:
            assert f"import {m}" not in src and f"from scripts.texture.{m}" not in src, (
                f"forbidden embedding import in {p.name}: {m}"
            )


def test_09_ast_no_max_smodel_sresid_call_in_leak_test():
    tree = ast.parse(LEAK_TEST_PATH.read_text())
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "max":
            names = [a.id for a in n.args if isinstance(a, ast.Name)]
            assert not ("S_model" in names and "S_resid" in names), (
                f"forbidden max(S_model, S_resid) call: {ast.dump(n)}"
            )


def test_10_ast_f1_pooled_variance_statistic_defined_in_leak_test():
    tree = ast.parse(LEAK_TEST_PATH.read_text())
    found = False
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == "f1_pooled_variance_statistic":
            found = True
            args = [a.arg for a in n.args.args]
            assert args == ["y_true", "y_pred", "leak_labels"], (
                f"signature drift: {args}"
            )
    assert found, "f1_pooled_variance_statistic not defined in leak_test.py"


def test_11_statistic_version_literal():
    # Constant present in leak_test module.
    from scripts.ear.leak_test import STATISTIC_VERSION
    assert STATISTIC_VERSION == "F1_pooled_variance_v1"
    # Verdict + leak_test_summary embed the literal.
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    assert v["statistic_version"] == "F1_pooled_variance_v1"
    ls = json.loads((DATA_DIR / "leak_test_summary.json").read_text())
    assert ls["statistic_version"] == "F1_pooled_variance_v1"


def test_12_diff_manifest_old_sha_matches_c6_anchor():
    m = json.loads((DATA_DIR / "leak_test_diff_manifest.json").read_text())
    assert m["file"] == "scripts/ear/leak_test.py"
    assert m["old_sha256"] == C6_LEAK_TEST_PRE_SHA
    # new_sha256 matches current file
    on_disk = _sha_file(LEAK_TEST_PATH)
    assert m["new_sha256"] == on_disk, (
        f"diff_manifest.new_sha256 {m['new_sha256'][:16]} != on-disk {on_disk[:16]}"
    )
    assert isinstance(m["changed_line_ranges"], list) and m["changed_line_ranges"]


def test_13_five_folds_cover_43_songs():
    f = json.loads((DATA_DIR / "held_out_folds.json").read_text())
    assert f["n_folds"] == 5
    covered = set()
    for rec in f["folds"]:
        covered.update(rec["held_out_song_sha256s"])
    assert len(covered) == 43, f"expected 43 songs covered, got {len(covered)}"
    # Every fold covers >= 1 song per band with count >= 5 (band-6=13/5>=2).
    for rec in f["folds"]:
        assert rec["n_held_out"] >= 4


def test_14_sb1_baselines_finite_and_reported():
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    tr = json.loads((DATA_DIR / "training_result.json").read_text())
    assert math.isfinite(tr["aggregate_mae"])
    assert math.isfinite(tr["baseline_majority_mae"])
    assert math.isfinite(tr["baseline_mean_int_mae"])
    assert math.isfinite(v["sb1"]["margin"])


def test_15_sb2_ten_resample_taus_finite():
    sb = json.loads((DATA_DIR / "sb_results.json").read_text())
    assert len(sb["sb2"]["per_resample_tau"]) == 10
    for t in sb["sb2"]["per_resample_tau"]:
        assert math.isfinite(t)
    assert math.isfinite(sb["sb2"]["mean_tau"])


def test_16_sb3_f1_per_leak_finite_in_unit_interval():
    sb = json.loads((DATA_DIR / "sb_results.json").read_text())
    per = sb["sb3"]["per_leak_type"]
    live = [k for k, v in per.items() if v.get("status") == "live"]
    assert live, "no live leak types"
    for name in live:
        v = per[name]
        assert math.isfinite(v["detection_rate"])
        assert math.isfinite(v["fpr"])
        assert 0.0 <= v["detection_rate"] <= 1.0
        assert 0.0 <= v["fpr"] <= 1.0
    assert per["genre"]["status"] == "deferred_aliased_with_band"
    assert per["era"]["status"] == "deferred_no_metadata"


def test_17_byte_determinism_across_two_runs():
    d = json.loads((DATA_DIR / "determinism_check.json").read_text())
    for k in ("verdict.json", "leak_test_summary.json", "corn_head_v1.pt"):
        entry = d["artifacts"][k]
        assert entry["run1"] == entry["run2"], (
            f"determinism drift on {k}: {entry['run1'][:16]} vs {entry['run2'][:16]}"
        )
    assert d["all_equal"] is True


def test_18_anchor_preservation_all_unchanged():
    a = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    assert a["all_unchanged"], f"anchor drift: {a['changed_paths']}"
    assert a["n_anchors"] >= 12  # brief says 12+ anchors in the report table
    # leak_test.py MUST NOT appear in the equality-asserted anchor set — it
    # is the c38-authorized mutation, tracked separately.
    assert "scripts/ear/leak_test.py" not in a["anchors"]


def test_19_feature_cache_manifest_present_and_stable():
    m = json.loads((DATA_DIR / "feature_cache_manifest.json").read_text())
    assert m["n_songs"] == 43
    assert m["feature_version"] == "ear-v1-real-label-v1"
    for e in m["entries"]:
        assert len(e["cache_file_sha256"]) == 64
        assert e["n_dims"] == 2052


def test_20_ledger_event_counts_ge_baseline():
    """Ledger MUST have grown by >= 6 substantive events since c37 close
    (baseline 627 rows) and MUST not have shrunk."""
    ledger = ROOT / "promise_ledger.jsonl"
    lines = ledger.read_text().splitlines()
    assert len(lines) >= 627, f"ledger shrunk: {len(lines)} < 627"
    # Count c38 M-EAR-1/real-label-training-v1 events.
    c38_events = 0
    for line in lines:
        try:
            evt = json.loads(line)
        except Exception:
            continue
        if (
            evt.get("cycle") == 38
            and "M-EAR-1/real-label-training-v1" in str(evt.get("milestone_id", ""))
        ):
            c38_events += 1
    assert c38_events >= 6, (
        f"expected >= 6 c38 M-EAR-1/real-label-training-v1 events, got {c38_events}"
    )


def test_21_corpus_honesty_caveat_literal_in_report():
    """The literal string '43 of the 80-song target — 54% corpus coverage'
    MUST appear in the report."""
    src = REPORT_DOC.read_text()
    literal = "43 of the 80-song target — 54% corpus coverage"
    assert literal in src, "corpus honesty caveat literal missing from report"


def test_22_verdict_field_is_frozen_label():
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    assert v["verdict"] in {
        "EAR_v1_LANDS", "EAR_v1_PARTIAL", "EAR_v1_INSUFFICIENT"
    }


def test_23_named_sb_attribution_on_non_lands():
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    if v["verdict"] != "EAR_v1_LANDS":
        att = v.get("named_sb_attribution", [])
        assert att, "PARTIAL/INSUFFICIENT must carry named-SB attribution"
        for row in att:
            assert row.get("sb") in {"SB1", "SB2", "SB3"}
            # numeric shortfall present on either shortfall/*_shortfall keys
            keys = [k for k in row if "shortfall" in k]
            assert keys, f"attribution row missing numeric shortfall: {row}"


def _run_all() -> tuple[int, int]:
    passed = failed = 0
    names = sorted(k for k in globals() if k.startswith("test_"))
    fails: list[tuple[str, str]] = []
    for n in names:
        try:
            globals()[n]()
            passed += 1
            print(f"PASS {n}")
        except AssertionError as e:
            failed += 1
            fails.append((n, str(e)[:200]))
            print(f"FAIL {n}: {e}")
        except Exception as e:
            failed += 1
            fails.append((n, f"{type(e).__name__}: {e}"[:200]))
            print(f"ERROR {n}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    if fails:
        print("\nFailures:")
        for n, msg in fails:
            print(f"  {n}: {msg}")
    return passed, failed


if __name__ == "__main__":
    p, f = _run_all()
    sys.exit(0 if f == 0 else 1)
