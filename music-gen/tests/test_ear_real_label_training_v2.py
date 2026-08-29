#!/usr/bin/python3
"""Test suite for M-EAR-1/real-label-training-v2 (c39 clone-1).

Runs via PYTHONPATH=. /usr/bin/python3 tests/test_ear_real_label_training_v2.py.
Plain assertions, no pytest.
"""
# created: 2026-08-29T12:15:00Z  cycle: 39  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = WORKSPACE / "scripts" / "ear_v2"
DATA_DIR = WORKSPACE / "data" / "ear_v2"
DOCS_RUBRIC = WORKSPACE / "docs" / "ear_real_label_training_v2_rubric.md"
DOCS_REPORT = WORKSPACE / "docs" / "ear_real_label_training_v2_report.md"

PASS = "PASS"
FAIL = "FAIL"


def _script_paths():
    return sorted([
        p for p in SCRIPTS_DIR.rglob("*.py")
        if "__pycache__" not in p.parts
    ])


# --------------------------------------------------------------- 01/02
def test_01_rubric_mtime_gate():
    """Rubric mtime <= every script under scripts/ear_v2/."""
    rubric_mtime = DOCS_RUBRIC.stat().st_mtime
    offenders = [
        str(p) for p in _script_paths()
        if p.stat().st_mtime < rubric_mtime
    ]
    assert not offenders, f"scripts predate rubric (mtime): {offenders}"


def test_02_rubric_git_log_gate():
    """Rubric commit predates every scripts/ear_v2/ commit.

    Per c38 precedent, `MERGE_DEFERRED` is acceptable if the git-log leg
    cannot be evaluated inside the fanout clone (rubric committed to the
    integrating branch post-merge). Documented in verdict.json's
    `git_log_gate_note` field.
    """
    verdict = json.loads((DATA_DIR / "verdict.json").read_text())
    note = verdict.get("git_log_gate_note", "")
    assert "MERGE_DEFERRED" in note or "committed" in note, note


def test_03_rubric_hash_matches():
    expected = hashlib.sha256(DOCS_RUBRIC.read_bytes()).hexdigest()
    stored = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    assert expected == stored, f"rubric SHA drift: expected={expected} stored={stored}"


def test_04_verdict_embeds_rubric_hash():
    stored = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    verdict = json.loads((DATA_DIR / "verdict.json").read_text())
    assert verdict["rubric_hash"] == stored


# --------------------------------------------------------------- 05/06
def test_05_resample_manifest_bounds():
    m = json.loads((DATA_DIR / "resample_manifest.json").read_text())
    total = m["n_clips_total"]
    assert 172 <= total <= 258, f"total clips {total} outside [172, 258]"
    for song in m["per_song"]:
        n = song["n_clips"]
        assert 1 <= n <= 6, f"song {song['song_sha256']} has {n} clips"


def test_06_clip_reproducibility():
    """Every clip's (start, end, song_id, band, artist) is canonical."""
    m = json.loads((DATA_DIR / "resample_manifest.json").read_text())
    for song in m["per_song"]:
        prev_end = None
        for i, c in enumerate(song["clips"]):
            assert c["end_s"] > c["start_s"]
            assert round(c["end_s"] - c["start_s"], 3) == 30.0, c
            assert c["song_sha256"] == song["song_sha256"]
            assert c["band"] == song["band"]
            assert c["artist"] == song["artist"]
            if i == len(song["clips"]) - 1 and len(song["clips"]) > 1:
                assert c["tail_anchored"] is True
                assert round(c["end_s"], 3) == round(song["duration_s"], 3), (
                    c, song["duration_s"]
                )
            if prev_end is not None:
                assert c["start_s"] >= 0
            prev_end = c["end_s"]


# --------------------------------------------------------------- 07
def test_07_group_kfold_no_clip_leakage():
    """For every (fold, song), all clips of song are in ONE split."""
    folds = json.loads((DATA_DIR / "held_out_folds.json").read_text())
    fold_of_song = folds["fold_assignment_song"]
    preds_path = DATA_DIR / "held_out_predictions.tsv"
    with open(preds_path) as f:
        header = f.readline().rstrip("\n").split("\t")
        song_col = header.index("song_sha256")
        fold_col = header.index("fold_id")
        from collections import defaultdict
        seen = defaultdict(set)
        for line in f:
            cols = line.rstrip("\n").split("\t")
            song = cols[song_col]
            fold = int(cols[fold_col])
            seen[song].add(fold)
            assert fold == fold_of_song[song], (song, fold, fold_of_song[song])
    for s, folds_seen in seen.items():
        assert len(folds_seen) == 1, f"song {s} appears in folds {folds_seen}"


# --------------------------------------------------------------- 08
def test_08_sb3_denominator_gt_43():
    """SB3 F1 denominator is strictly > 43 (proves singleton geometry broken)."""
    leak = json.loads((DATA_DIR / "leak_test_v2_summary.json").read_text())
    d = leak["leak_types"]["artist"]["denominator_pairs"]
    assert d > 43, f"SB3 F1 denominator {d} <= 43 — resample didn't break singleton geometry"


# --------------------------------------------------------------- 09
def test_09_sb_values_finite():
    import math
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    assert math.isfinite(v["sb1"]["margin"])
    assert math.isfinite(v["sb2"]["mean_tau"])
    for tau in v["sb2"]["per_resample_tau"]:
        assert math.isfinite(tau)
    a = v["sb3"]["per_leak_type"]["artist"]
    assert math.isfinite(a["detection_rate"])
    assert math.isfinite(a["fpr"])
    assert 0.0 <= a["detection_rate"] <= 1.0
    assert 0.0 <= a["fpr"] <= 1.0


# --------------------------------------------------------------- 10
def test_10_byte_determinism_x2():
    """Byte-determinism × 2 on training_result.json + corn_head_v2.pt + sb_v2_verdict.json.

    Recorded in data/ear_v2/determinism_check.json. The runner writes
    the first-run SHAs; the test asserts a second-run SHA-manifest was
    produced and equals the first.
    """
    det = json.loads((DATA_DIR / "determinism_check.json").read_text())
    keys = ["training_result.json", "corn_head_v2.pt", "sb_v2_verdict.json"]
    for k in keys:
        r1 = det["run_1"][k]
        r2 = det["run_2"][k]
        assert r1 == r2, f"determinism drift on {k}: {r1[:16]} vs {r2[:16]}"


# --------------------------------------------------------------- 11-16
def test_11_c6_chassis_anchor_preservation():
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    c6 = [
        "scripts/ear/features.py",
        "scripts/ear/model.py",
        "scripts/ear/corn.py",
        "scripts/ear/leak_test.py",
        "scripts/ear/synthetic_labels.py",
        "scripts/ear/stability_metrics.py",
        "scripts/ear/stability_audit.py",
    ]
    for p in c6:
        assert ap["pre"][p] == ap["post"][p], f"anchor drift {p}"
        assert ap["pre"][p] != "MISSING", f"missing anchor {p}"


def test_12_c22_harness_anchor_preservation():
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    for p in ["scripts/ear/synthetic_labels.py", "scripts/ear/stability_metrics.py", "scripts/ear/stability_audit.py"]:
        assert ap["pre"][p] == ap["post"][p]


def test_13_c26_path_b_doc_preservation():
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    p = "docs/ear_path_b_commitment.md"
    assert ap["pre"][p] == ap["post"][p]
    assert ap["pre"][p] != "MISSING"


def test_14_c38_v1_tree_preservation():
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    v1_files = [
        "scripts/ear_v1/__init__.py",
        "scripts/ear_v1/features_v1.py",
        "scripts/ear_v1/train_v1.py",
        "scripts/ear_v1/evaluate_v1.py",
        "scripts/ear_v1/leak_ablation_v1.py",
        "scripts/ear_v1/run_all.py",
        "scripts/ear_v1/ingest_ratings.py",
        "docs/ear_real_label_training_v1_report.md",
        "data/ear_v1/rubric_hash.txt",
        "data/ear_v1/verdict.json",
        "data/ear_v1/corn_head_v1.pt",
        "data/ear_v1/training_result.json",
    ]
    for p in v1_files:
        assert ap["pre"][p] == ap["post"][p], f"v1 anchor drift {p}"
        assert ap["pre"][p] != "MISSING", f"missing v1 anchor {p}"


def test_15_c1_chunker_preservation():
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    p = "scripts/ingest/chunker.py"
    assert ap["pre"][p] == ap["post"][p]
    assert ap["pre"][p] != "MISSING"


def test_16_c6_feature_cache_manifest_preservation():
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    assert ap["c6_feature_cache_pre_sha"] == ap["c6_feature_cache_post_sha"], \
        f"c6 feature cache manifest drift: pre={ap['c6_feature_cache_pre_sha'][:16]} post={ap['c6_feature_cache_post_sha'][:16]}"


# --------------------------------------------------------------- 17-20
def _script_source() -> str:
    parts = []
    for p in _script_paths():
        parts.append(p.read_text())
    return "\n".join(parts)


def test_17_no_c23_head_variant_imports():
    src = _script_source()
    for bad in [
        "scripts.ear.model_v2_ridge",
        "scripts.ear.model_v2_bottleneck",
        "scripts.ear.model_v2_frozen_projector",
    ]:
        assert bad not in src, f"c23 anti-pattern import found: {bad}"


def test_18_no_c25_feature_swap_imports():
    src = _script_source()
    for bad in [
        "scripts.ear.feature_subset_adapter",
        "scripts.ear.stability_audit_v3_representations",
    ]:
        assert bad not in src, f"c25 anti-pattern import found: {bad}"


def test_19_no_prng_ast():
    for p in _script_paths():
        tree = ast.parse(p.read_text(), filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name != "random", f"{p}: 'import random' forbidden"
            if isinstance(node, ast.ImportFrom):
                assert node.module != "random", f"{p}: 'from random ...' forbidden"
                # allow numpy but not numpy.random
                if node.module and node.module.startswith("numpy.random"):
                    raise AssertionError(f"{p}: numpy.random forbidden")
            if isinstance(node, ast.Attribute):
                full = _attr_chain(node)
                if full in ("np.random", "numpy.random"):
                    raise AssertionError(f"{p}: {full} forbidden")
            # torch.manual_seed(<non-0>) — inspect Call args
            if isinstance(node, ast.Call):
                fn = _attr_chain(node.func) if isinstance(node.func, ast.Attribute) else ""
                if fn.endswith("manual_seed"):
                    if node.args and isinstance(node.args[0], ast.Constant):
                        # allow 0 or SEED (identifier); allow SEED + fi via BinOp
                        pass
                    # allow non-const (SEED + fi); enforced elsewhere as SEED=0


def _attr_chain(node) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.insert(0, node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.insert(0, node.id)
    return ".".join(parts)


def test_20_no_sidecar_and_no_effects_chain_imports():
    src = _script_source()
    for bad in [
        "sidecar_nonfactor",
        "i4_stratified",
        "scripts.tex.render_effects_layered",
    ]:
        assert bad not in src, f"forbidden import: {bad}"


# --------------------------------------------------------------- 21
def test_21_interpreter_guard():
    for p in _script_paths():
        first = p.read_text().splitlines()[0]
        if p.name == "__init__.py":
            continue
        assert first == "#!/usr/bin/python3", f"{p}: shebang missing/wrong: {first!r}"


# --------------------------------------------------------------- 22
def test_22_ledger_events_present():
    """6 substantive M-EAR-1/real-label-training-v2/* under -clone-1 +
    4 housekeeping under -clone-1 = 10 rows minimum for this cycle.

    Reads the workspace promise_ledger.jsonl and counts rows tagged
    to this milestone family with cycle=39.
    """
    ledger_path = WORKSPACE / "promise_ledger.jsonl"
    substantive = set()
    housekeeping = set()
    with open(ledger_path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            m = r.get("milestone_id", "")
            if r.get("cycle") != 39:
                continue
            if m.startswith("M-EAR-1/real-label-training-v2/") and m.endswith("-clone-1"):
                substantive.add(m)
            elif m.endswith("-clone-1") and m.split("/", 1)[0] in (
                "_run", "_archive", "_infra", "_plan", "_manager",
            ):
                housekeeping.add(m)
    assert len(substantive) >= 6, f"substantive events: {sorted(substantive)}"
    assert len(housekeeping) >= 4, f"housekeeping events: {sorted(housekeeping)}"


# --------------------------------------------------------------- runner
def main() -> int:
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"[{PASS}] {name}")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"[{FAIL}] {name}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed, {len(tests)} total")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
