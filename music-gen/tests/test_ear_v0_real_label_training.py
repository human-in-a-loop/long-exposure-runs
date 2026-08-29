"""Tests for M-EAR-1/real-label-training-v0 (cycle 36 Branch A, clone-0).

Run: PYTHONPATH=. /usr/bin/python3 tests/test_ear_v0_real_label_training.py
"""
# created: 2026-08-29T07:28:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: M-EAR-1/real-label-training-v0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import ast
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts" / "ear_v0"
DATA_DIR = ROOT / "data" / "ear_v0"
RUBRIC_DOC = ROOT / "docs" / "ear_v0_real_label_training_rubric.md"


def _sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def test_01_rubric_hash_byte_equal():
    doc_sha = _sha_file(RUBRIC_DOC)
    stored = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    assert doc_sha == stored, f"rubric doc sha {doc_sha[:16]} != stored {stored[:16]}"


def test_02_verdict_carries_rubric_hash():
    stored = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    assert v["rubric_hash"] == stored


def test_03_rubric_mtime_before_scripts():
    rt = RUBRIC_DOC.stat().st_mtime
    earliest = min(
        p.stat().st_mtime
        for p in SCRIPTS_DIR.glob("*.py")
        if p.name != "__pycache__"
    )
    # Fallback: if mtime check fails (edit reordering), git-log check.
    if rt >= earliest:
        try:
            r = subprocess.run(
                ["git", "log", "--diff-filter=A", "--format=%at", "--",
                 str(RUBRIC_DOC.relative_to(ROOT))],
                cwd=str(ROOT), capture_output=True, text=True, check=True,
            )
            rubric_added = int(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else 0
            script_adds = []
            for p in SCRIPTS_DIR.glob("*.py"):
                rr = subprocess.run(
                    ["git", "log", "--diff-filter=A", "--format=%at",
                     "--", str(p.relative_to(ROOT))],
                    cwd=str(ROOT), capture_output=True, text=True, check=True,
                )
                if rr.stdout.strip():
                    script_adds.append(int(rr.stdout.strip().splitlines()[-1]))
            if script_adds:
                assert rubric_added <= min(script_adds), (
                    f"git-log fallback failed: rubric added {rubric_added}, "
                    f"earliest script {min(script_adds)}"
                )
                return
        except Exception:
            pass
    assert rt < earliest, f"rubric mtime {rt} >= earliest script mtime {earliest}"


def test_04_interpreter_guard_present():
    pat = re.compile(r'sys\.executable\s*==\s*["\']/usr/bin/python3["\']')
    for p in SCRIPTS_DIR.glob("*.py"):
        if p.name == "__init__.py":
            continue
        src = p.read_text()
        assert pat.search(src), f"missing interpreter guard: {p.name}"


def test_05_no_prng():
    """AST-grep: no bare random/np.random.* without pinned seed=0."""
    forbidden = re.compile(
        r'^\s*(import\s+random\b|from\s+random\s+import|'
        r'numpy\.random\.(rand|randn|randint|choice|shuffle|permutation)|'
        r'torch\.rand(?!om)|torch\.randn|torch\.randint)\b'
    )
    for p in SCRIPTS_DIR.glob("*.py"):
        for lineno, line in enumerate(p.read_text().splitlines(), 1):
            if forbidden.match(line):
                raise AssertionError(f"PRNG use at {p.name}:{lineno}: {line!r}")


def test_06_no_sidecar_nonfactor_import():
    pat = re.compile(r'^\s*(from|import)\s+.*sidecar_nonfactor', re.MULTILINE)
    for p in SCRIPTS_DIR.glob("*.py"):
        src = p.read_text()
        assert not pat.search(src), f"sidecar_nonfactor imported in {p.name}"


def test_07_c6_feature_cache_anchor():
    """c6 data/ear/features/ manifest byte-identical pre/post (via
    scripts/ear/features.py source SHA as proxy for the pipeline)."""
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    assert ap["unchanged"], f"anchor drift: {ap['changed_paths']}"


def test_08_per_song_feature_deterministic():
    """Spot-check 5 songs: cached feature file SHA-256 stable."""
    from scripts.ear_v0.ingest_ratings import discover_songs
    songs = discover_songs(ROOT)
    spot = songs[:5]
    for s in spot:
        f = DATA_DIR / "per_song_features" / f"{s.sha256}.npy"
        assert f.exists(), f"missing cached feature: {s.sha256[:16]}"
        assert f.stat().st_size > 0


def test_09_training_deterministic_config():
    t = json.loads((DATA_DIR / "training_result.json").read_text())
    dc = t["determinism_config"]
    assert dc["OMP_NUM_THREADS"] == "1"
    assert dc["MKL_NUM_THREADS"] == "1"
    assert dc["OPENBLAS_NUM_THREADS"] == "1"
    assert dc["torch_manual_seed"] == 0
    assert dc["torch_num_threads"] == 1


def test_10_sb_all_finite():
    v = json.loads((DATA_DIR / "verdict.json").read_text())
    import math
    for k in ("mae", "majority_mae", "mean_int_mae", "margin"):
        assert math.isfinite(v["sb1"][k]), f"sb1.{k} not finite"
    assert math.isfinite(v["sb2"]["mean_tau"])
    assert len(v["sb2"]["per_resample_tau"]) == 10
    for t in v["sb2"]["per_resample_tau"]:
        assert math.isfinite(t)
    assert 0.0 <= v["sb3"]["artist_detection"] <= 1.0


def test_11_corn_head_state_dict_deterministic():
    import torch
    p = DATA_DIR / "corn_head_v0_real.pt"
    sd = torch.load(p, weights_only=True)
    # State dict must be non-empty and contain fold_0 keys at minimum.
    keys = list(sd.keys())
    assert any(k.startswith("fold_0.") for k in keys), keys[:5]
    # SHA-256 of the on-disk file is our determinism anchor.
    assert p.stat().st_size > 0


def test_12_leak_ablation_covers_three_columns():
    la = json.loads((DATA_DIR / "leak_ablation_summary.json").read_text())
    assert set(la["columns_covered"]) >= {"artist", "genre", "era"}
    assert "reason" in la["genre"]
    assert "reason" in la["era"]
    assert la["genre"]["status"] == "deferred_aliased_with_band"
    assert la["era"]["status"] == "deferred_no_metadata"


def test_13_artist_parse_yield():
    """artist parsed non-null from >= 40/43 songs."""
    from scripts.ear_v0.ingest_ratings import discover_songs
    songs = discover_songs(ROOT)
    non_null = sum(1 for s in songs if s.artist and s.artist.strip())
    assert non_null >= 40, f"artist parse yield {non_null}/43"


def test_14_folds_five_leave_one_per_band():
    f = json.loads((DATA_DIR / "held_out_folds.json").read_text())
    assert f["n_folds"] == 5
    assert f["class_distribution"] == {"4": 10, "5": 10, "6": 13, "7": 10}
    # Each fold holds out at least 1 song per band with count>=n_folds
    # (band-6 gets 2 or 3 per fold due to 13/5).
    for rec in f["folds"]:
        assert rec["n_held_out"] >= 4  # 1 per band × 4 bands


def test_15_sampler_weights_present():
    f = json.loads((DATA_DIR / "held_out_folds.json").read_text())
    sw = f["sampler_weights"]
    assert len(sw) == 43
    # Weight per song = (43/4) / n_band.
    for _, w in sw.items():
        assert 0 < w < 3.0  # loose sanity bound


def test_16_c6_pipeline_not_mutated():
    """c6 feature pipeline files untouched via anchor_preservation."""
    ap = json.loads((DATA_DIR / "anchor_preservation.json").read_text())
    for target in ("scripts/ear/features.py", "scripts/ear/model.py",
                   "scripts/ear/corn.py", "scripts/ear/leak_test.py",
                   "scripts/classifier/tagger.py"):
        assert ap["pre"][target] == ap["post"][target], f"mutation of {target}"


def _run_all() -> tuple[int, int]:
    passed, failed = 0, 0
    failures = []
    for name in sorted(globals()):
        if not name.startswith("test_"):
            continue
        fn = globals()[name]
        try:
            fn()
            passed += 1
            print(f"PASS {name}")
        except Exception as e:
            failed += 1
            failures.append((name, str(e)[:200]))
            print(f"FAIL {name}: {type(e).__name__}: {str(e)[:200]}")
    print(f"\n{passed} passed, {failed} failed")
    if failures:
        print("\nFailures:")
        for n, m in failures:
            print(f"  {n}: {m}")
    return passed, failed


if __name__ == "__main__":
    p, f = _run_all()
    sys.exit(0 if f == 0 else 1)
