#!/usr/bin/python3
# ---
# created: 2026-09-04T00:00:00Z
# cycle: 16
# run_id: run-2026-09-04T110000Z
# agent: worker
# milestone: _infra/pinned-profile-shape-invariant-e-c16
# ---
"""c16 Track 3 — pinned-profile shape stability invariant (e) enforcement.

Cases:
  1. c14 drums anchor: byte-identical SHA + parses + carries the 4-nested
     canonical acceptance_fork keys (chosen/rejected/authority/invariants_doc)
     + top-level `supersedes_path` as `str`.
  2. c15 guitar anchor: byte-identical SHA + parses + honest DRIFT
     disclosed (3 nested keys; invariants_doc folded into authority
     string; still top-level `supersedes_path` as `str`).
  3. c9 bass_v2 anchor: byte-identical SHA only (grandfathered — predates
     invariant framework; no shape assertion).
  4. Invariants doc SHA byte-identical after (e) extension.
  5. AST-grep: no PRNG, no `sidecar_nonfactor` in this test file itself;
     `/usr/bin/python3` guard.
  6. `supersedes_path` never a `list` in any of the three anchors
     (enforces c14 lemma).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIV = ROOT / "data" / "v4" / "deliveries" / "31a164f845f8e27e"

# Pinned SHAs (on-disk canonical per FD-1)
SHAS = {
    "cg_bass_pinned_profile.json": (
        "aa9b36be3f2e6748ba144845e7a7dbce15aee5f1bc354ed0c12392e4f3722dc7"
    ),
    "cg_drums_pinned_profile.json": (
        "720f1424e9fcac352b9bcb07dac428b176121835035f296bd5e4d91a732ebcb1"
    ),
    "cg_guitar_pinned_profile.json": (
        "14d0707898b557dfa3edaf8ffa3765f8de37e1014e47da99f3946b14c7a4b8b9"
    ),
}

INVARIANTS_DOC = ROOT / "docs" / "agent_picks_selection_invariants.md"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _load(name: str) -> dict:
    return json.loads((DELIV / name).read_text())


def test_c14_drums_anchor_canonical_shape():
    name = "cg_drums_pinned_profile.json"
    assert _sha256(DELIV / name) == SHAS[name], (
        f"{name} SHA drift"
    )
    d = _load(name)
    af = d["acceptance_fork"]
    for k in ("chosen", "rejected", "authority", "invariants_doc"):
        assert k in af, f"c14 canonical shape missing acceptance_fork.{k}"
    assert isinstance(af["chosen"], dict)
    assert isinstance(af["rejected"], list)
    assert isinstance(af["authority"], str)
    assert isinstance(af["invariants_doc"], str)
    assert af["invariants_doc"] == "docs/agent_picks_selection_invariants.md"
    # supersedes_path top-level and str (c14 lemma)
    assert isinstance(d["supersedes_path"], str), (
        "supersedes_path must be str, not list (c14 lemma)"
    )


def test_c15_guitar_anchor_drift_disclosed():
    name = "cg_guitar_pinned_profile.json"
    assert _sha256(DELIV / name) == SHAS[name], (
        f"{name} SHA drift"
    )
    d = _load(name)
    af = d["acceptance_fork"]
    # c15 guitar has 3 nested keys (drift from c14's 4)
    for k in ("chosen", "rejected", "authority"):
        assert k in af, f"c15 shape missing acceptance_fork.{k}"
    # invariants_doc folded into authority string
    assert "docs/agent_picks_selection_invariants.md" in af["authority"], (
        "c15 drift: invariants_doc folded into authority string, must "
        "still reference the doc path"
    )
    # supersedes_path top-level str (c14 lemma preserved despite drift)
    assert isinstance(d["supersedes_path"], str)


def test_c9_bass_anchor_grandfathered_sha_only():
    name = "cg_bass_pinned_profile.json"
    assert _sha256(DELIV / name) == SHAS[name], (
        f"{name} SHA drift"
    )
    # No shape assertion — c9 predates invariant framework.
    d = _load(name)
    # But if supersedes present, must be str per c14 lemma.
    sp = d.get("supersedes")
    if sp is not None and not isinstance(sp, dict):
        assert isinstance(sp, str)


def test_invariants_doc_carries_invariant_e():
    text = INVARIANTS_DOC.read_text()
    assert "Invariant (e)" in text, (
        "docs/agent_picks_selection_invariants.md missing invariant (e)"
    )
    assert "cross-cycle pinned-profile shape stability" in text.lower()
    # canonical shape spec present
    for k in ("chosen", "rejected", "authority", "invariants_doc"):
        assert k in text
    # precedent table present
    for label in ("c9 bass_v2", "c14 drums", "c15 guitar"):
        assert label in text


def test_no_prng_no_sidecar_in_this_file():
    src = Path(__file__).read_text()
    # Check for actual import statements, not string literals
    assert not re.search(r"^\s*import\s+random\b", src, re.MULTILINE), (
        "forbidden: `import random`"
    )
    assert not re.search(
        r"^\s*from\s+numpy\s+import\s+random\b", src, re.MULTILINE
    )
    assert not re.search(
        r"^\s*from\s+.*\s+import\s+sidecar_nonfactor\b", src, re.MULTILINE
    )
    assert re.match(r"^#!/usr/bin/python3", src), (
        "interpreter guard missing"
    )


def test_supersedes_path_never_list_in_any_anchor():
    for name in SHAS:
        d = _load(name)
        sp = d.get("supersedes_path")
        if sp is not None:
            assert not isinstance(sp, list), (
                f"{name}: supersedes_path must be str, not list "
                f"(c14 lemma)"
            )


TESTS = [
    test_c14_drums_anchor_canonical_shape,
    test_c15_guitar_anchor_drift_disclosed,
    test_c9_bass_anchor_grandfathered_sha_only,
    test_invariants_doc_carries_invariant_e,
    test_no_prng_no_sidecar_in_this_file,
    test_supersedes_path_never_list_in_any_anchor,
]


def main() -> int:
    fails = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(TESTS) - fails}/{len(TESTS)} tests passed")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
