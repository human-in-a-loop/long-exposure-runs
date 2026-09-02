"""M-V3-RULES-1 test suite — see docs/v3_rules_deterministic_extractor_spec_c23.md.

≥12/15 green required. Each test corresponds to a numbered rubric case.
"""
import ast
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
EXTRACTOR = REPO / "scripts" / "v3_rules" / "extract_rules.py"
RUBRIC = REPO / "docs" / "v3_rules_deterministic_extractor_spec_c23.md"
RUBRIC_HASH_TXT = REPO / "data" / "v3" / "rules" / "rubric_hash.txt"
VERDICT = REPO / "data" / "v3" / "rules" / "verdict.json"
ARTIFACT = REPO / "data" / "v3" / "rules" / "rules_artifact.jsonl"
ARTIFACT_SHA = REPO / "data" / "v3" / "rules" / "rules_artifact.sha256"
FETCHABILITY = REPO / "data" / "v3" / "rules" / "fetchability_ladder.jsonl"
V3_RULES_DIR = REPO / "scripts" / "v3_rules"

SONG_SHAS = ("31a164f845f8e27e", "252eb21ce7df7328",
             "51e433ade2a845e1", "cdd2717e52820ff6")
RULE_TYPES = {"harmonic", "rhythmic", "melodic", "form", "arrangement"}
STEMS = {"bass", "drums", "guitar", "piano", "vocals", "other", "full_mix"}

C9_LEDGERS = (
    REPO / "data" / "rules" / "ledger.jsonl",
    REPO / "data" / "rules" / "ledger_i3_dminor.jsonl",
    REPO / "data" / "rules" / "ledger_rated_corpus.jsonl",
)


def _run_env():
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", TZ="UTC", LC_ALL="C.UTF-8",
               SOURCE_DATE_EPOCH="1756463424")
    return env


def _read_rules():
    return [json.loads(line) for line in ARTIFACT.read_text().splitlines() if line]


# --- 1 ---
def test_interpreter_guard_present():
    for p in V3_RULES_DIR.rglob("*.py"):
        head = p.read_text().splitlines()[:5]
        joined = "\n".join(head)
        if p.name == "__init__.py":
            continue
        assert "/usr/bin/python3" in joined, f"missing interpreter guard: {p}"


# --- 2 ---
def test_no_prng_imports():
    forbidden = {"random", "secrets"}
    for p in V3_RULES_DIR.rglob("*.py"):
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    top = a.name.split(".")[0]
                    assert top not in forbidden, f"{p}: import {a.name}"
                    assert not a.name.endswith(".random"), f"{p}: {a.name}"
            if isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                assert top not in forbidden, f"{p}: from {node.module}"
                assert not node.module.endswith(".random"), f"{p}: {node.module}"


# --- 3 ---
def test_no_sidecar_nonfactor_imports():
    for p in V3_RULES_DIR.rglob("*.py"):
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert "sidecar_nonfactor" not in a.name, f"{p}: import {a.name}"
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "sidecar_nonfactor" not in node.module, f"{p}: from {node.module}"
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    assert node.value.id != "sidecar_nonfactor", f"{p}: attr access"


# --- 4 ---
def test_no_vst3_state_apis():
    pat = re.compile(r"\.(get_state|save_state|save_preset|load_state|set_state)\s*\(")
    for p in V3_RULES_DIR.rglob("*.py"):
        assert not pat.search(p.read_text()), f"{p} touches VST3 state APIs"


# --- 5 ---
def test_rubric_doc_mtime_before_scripts():
    rubric_mtime = RUBRIC.stat().st_mtime
    for p in V3_RULES_DIR.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        assert rubric_mtime < p.stat().st_mtime, (
            f"rubric mtime not before {p} (rubric={rubric_mtime}, script={p.stat().st_mtime})"
        )


# --- 6 ---
def test_rubric_hash_v3_rules_three_way_byte_equality():
    a = hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
    b = RUBRIC_HASH_TXT.read_text().strip()
    assert VERDICT.exists(), "verdict.json missing — run extraction + verdict emit first"
    c = json.loads(VERDICT.read_text())["rubric_hash_v3_rules"]
    assert a == b == c, f"chain mismatch: A={a} B={b} C={c}"


# --- 7 ---
def test_fetchability_ladder_no_fetch_attempts():
    assert FETCHABILITY.exists(), "fetchability_ladder.jsonl missing"
    rows = [json.loads(l) for l in FETCHABILITY.read_text().splitlines() if l]
    assert rows, "fetchability_ladder.jsonl is empty"
    for r in rows:
        assert r.get("no_fetch_attempts") is True, r
        assert r["candidate"] in {"music21", "mingus", "jsonschema", "sklearn"}


# --- 8 ---
def test_rules_artifact_schema_conforms_to_c9_types():
    for r in _read_rules():
        assert r["schema_v"] == 1
        assert r["event_type"] == "rule"
        assert r["rule_type"] in RULE_TYPES, r["rule_type"]
        assert r["rule_id"].startswith("rule_") and len(r["rule_id"]) == 21
        assert len(r["event_id"]) == 32
        assert r["parameters_random_state"] == 0
        assert r["ts"] == "2026-09-02T00:00:00Z"


# --- 9 ---
def test_per_stem_provenance_present():
    for r in _read_rules():
        for pp in r["provenance_pointers"]:
            assert "stem" in pp and pp["stem"] in STEMS, pp
            assert pp["song_sha16"] in SONG_SHAS, pp


# --- 10 ---
def test_byte_determinism_two_fresh_runs():
    env = _run_env()
    shas = []
    for i in range(2):
        d = tempfile.mkdtemp(prefix=f"pytest_det_{i}_")
        subprocess.run(
            ["/usr/bin/python3", str(EXTRACTOR), "--out-dir", d],
            env=env, check=True, cwd=str(REPO), capture_output=True,
        )
        shas.append(hashlib.sha256((Path(d) / "rules_artifact.jsonl").read_bytes()).hexdigest())
    assert shas[0] == shas[1], f"byte-det mismatch: {shas}"


# --- 11 ---
def test_rules_artifact_self_anchor_sha():
    expected = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    pinned = ARTIFACT_SHA.read_text().strip()
    assert expected == pinned, f"artifact SHA mismatch: {expected} vs {pinned}"


# --- 12 ---
def test_readonly_anchor_preservation():
    snap = REPO / "data" / "v3" / "rules" / "anchor_preservation_c23.json"
    assert snap.exists(), "anchor_preservation_c23.json missing"
    d = json.loads(snap.read_text())
    assert len(d["anchors"]) >= 30, len(d["anchors"])
    for a in d["anchors"]:
        p = REPO / a["path"]
        assert p.exists(), a["path"]
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual == a["sha256"], f"anchor drift: {a['path']}"


# --- 13 ---
def test_c9_c15_c40_ledgers_untouched():
    snap = REPO / "data" / "v3" / "rules" / "anchor_preservation_c23.json"
    d = json.loads(snap.read_text())
    pinned = {a["path"]: a["sha256"] for a in d["anchors"]}
    for lp in C9_LEDGERS:
        rel = str(lp.relative_to(REPO))
        assert rel in pinned, f"{rel} not in anchor snapshot"
        actual = hashlib.sha256(lp.read_bytes()).hexdigest()
        assert actual == pinned[rel], f"{rel} drifted"


# --- 14 ---
def test_ledger_events_have_agent_and_clone_fields():
    lp = REPO / "data" / "v3" / "rules" / "ledger_c23_clone_2.jsonl"
    assert lp.exists(), "ledger_c23_clone_2.jsonl missing"
    rows = [json.loads(l) for l in lp.read_text().splitlines() if l]
    assert len(rows) >= 8, f"expected ≥8 events, got {len(rows)}"
    for r in rows:
        assert r.get("agent") == "worker", r
        assert r.get("agent_original", "").startswith("worker-clone-"), r
        assert r.get("clone") == "2", r
        assert r["event_type"].startswith("M-V3-RULES-1/") or \
               r["event_type"].startswith("_archive/") or \
               r["event_type"].startswith("_infra/"), r


# --- 15 ---
def test_corpus_covers_four_operator_approved_songs():
    seen = set()
    for r in _read_rules():
        for pp in r["provenance_pointers"]:
            seen.add(pp["song_sha16"])
    assert seen == set(SONG_SHAS), f"missing songs: {set(SONG_SHAS) - seen}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
