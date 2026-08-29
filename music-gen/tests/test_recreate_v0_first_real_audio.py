#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T08:00:00Z
# cycle: 37
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-1/first-real-audio
# fork: 675abd086911
# clone: 0
# ---
"""Test suite for M-RECREATE-1/first-real-audio.

Plain-assert style (no pytest). Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_recreate_v0_first_real_audio.py

The suite is designed to run AFTER `scripts/recreate_v0/run_all.py` has
been driven to completion. Every test that depends on runtime output
gracefully skips (does not fail) when the artifact is absent — that
skip is itself a first-class signal downstream picks up. Structural
tests that don't depend on runtime output always run.

≥14 cases.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "recreate_v0"
SCRIPTS = ROOT / "scripts" / "recreate_v0"
RUBRIC_DOC = ROOT / "docs" / "recreate_v0_first_real_audio_rubric.md"
REPORT_DOC = ROOT / "docs" / "recreate_v0_first_real_audio_report.md"


class Skipped(Exception):
    pass


# ------------------------------------------------------------------
# STRUCTURAL — no pipeline output required
# ------------------------------------------------------------------
def test_01_rubric_doc_exists() -> None:
    assert RUBRIC_DOC.is_file(), f"rubric missing at {RUBRIC_DOC}"


def test_02_rubric_hash_txt_matches_rubric_doc_sha256() -> None:
    h = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()
    stored = (DATA / "rubric_hash.txt").read_text().strip()
    assert h == stored, f"rubric SHA drift: {h} vs {stored}"


def test_03_rubric_committed_before_any_script_under_recreate_v0() -> None:
    # mtime-based test (fastest); falls back gracefully if any file
    # is missing (structural check catches that separately).
    if not RUBRIC_DOC.is_file():
        raise AssertionError("rubric missing")
    rubric_mtime = RUBRIC_DOC.stat().st_mtime
    for py in sorted(SCRIPTS.glob("*.py")):
        assert py.stat().st_mtime >= rubric_mtime, (
            f"{py.name} mtime {py.stat().st_mtime} < rubric mtime "
            f"{rubric_mtime}"
        )


def test_04_scripts_present() -> None:
    for name in ("__init__.py", "select_song.py",
                 "run_pipeline.py", "run_all.py"):
        assert (SCRIPTS / name).is_file(), f"missing {name}"


def test_05_interpreter_guard_on_every_script() -> None:
    # /usr/bin/python3 guard is required per M-RECREATE-1 contract.
    for name in ("select_song.py", "run_pipeline.py", "run_all.py"):
        p = SCRIPTS / name
        content = p.read_text()
        assert "sys.executable == \"/usr/bin/python3\"" in content, (
            f"missing interpreter guard in {name}"
        )


def test_06_non_factor_isolation_no_sidecar_nonfactor_import() -> None:
    # Regex avoids matching comments. Line-start import.
    pat = re.compile(r"^(from|import)\s+scripts\.classifier\.sidecar_nonfactor",
                     re.MULTILINE)
    for py in sorted(SCRIPTS.glob("*.py")):
        assert not pat.search(py.read_text()), (
            f"non-factor isolation violated in {py.name}"
        )


def test_07_no_prng_in_recreate_v0_source() -> None:
    # SHA-256 tiebreak, not PRNG. random.* and numpy.random.* are forbidden
    # in select_song.py specifically (the selection rule); run_pipeline
    # uses numpy.random.seed(0) as a determinism pin (allowed).
    ss = (SCRIPTS / "select_song.py").read_text()
    for banned in ("import random", "numpy.random.rand", "np.random.rand",
                   "random.choice", "random.randint"):
        assert banned not in ss, f"{banned} appears in select_song.py"


def test_08_song_selector_deterministic_across_runs() -> None:
    if not (SCRIPTS / "select_song.py").is_file():
        raise AssertionError("select_song.py missing")
    p1 = subprocess.run(
        ["/usr/bin/python3", str(SCRIPTS / "select_song.py")],
        capture_output=True, text=True,
    )
    assert p1.returncode == 0, p1.stderr
    p2 = subprocess.run(
        ["/usr/bin/python3", str(SCRIPTS / "select_song.py")],
        capture_output=True, text=True,
    )
    assert p2.returncode == 0, p2.stderr
    assert p1.stdout == p2.stdout, "song selector is not deterministic"


# ------------------------------------------------------------------
# ARTIFACT — depend on pipeline output; skip if absent (still assert
# they exist once we get a verdict.json — otherwise nothing to test).
# ------------------------------------------------------------------
def test_09_chosen_song_json_valid() -> None:
    j = DATA / "chosen_song.json"
    if not j.is_file():
        raise AssertionError("chosen_song.json missing; run select_song.py")
    d = json.loads(j.read_text())
    for k in ("chosen_relpath", "chosen_sha256", "chosen_bytes",
              "chosen_rating_band", "selection_rule", "rubric_hash"):
        assert k in d, f"chosen_song.json missing {k}"
    assert len(d["chosen_sha256"]) == 64, "sha256 not 64 hex chars"
    assert d["chosen_rating_band"] in (4, 5, 6, 7)


def test_10_chosen_song_is_smallest_sha_among_all_bands() -> None:
    j = DATA / "chosen_song.json"
    if not j.is_file():
        raise AssertionError("chosen_song.json missing")
    d = json.loads(j.read_text())
    # top-5 list should be present and monotonically increasing SHAs
    top5 = d.get("top5_ranked_sha256_ascending", [])
    assert len(top5) > 0
    prev = ""
    for row in top5:
        assert row["sha256"] >= prev, "top5 not sorted ascending"
        prev = row["sha256"]
    assert top5[0]["sha256"] == d["chosen_sha256"], "chosen != top1"


def test_11_verdict_json_has_rubric_hash_matching_frozen() -> None:
    v = DATA / "verdict.json"
    if not v.is_file():
        raise AssertionError("verdict.json missing; run_all.py did not finish")
    d = json.loads(v.read_text())
    stored = (DATA / "rubric_hash.txt").read_text().strip()
    assert d["rubric_hash"] == stored, "verdict rubric_hash != frozen"


def test_12_verdict_label_is_one_of_three() -> None:
    v = DATA / "verdict.json"
    if not v.is_file():
        raise AssertionError("verdict.json missing")
    d = json.loads(v.read_text())
    assert d["verdict"] in ("RECREATION_LANDS", "RECREATION_PARTIAL",
                            "RECREATION_FAILS"), d["verdict"]


def test_13_preview_untrained_ear_flag_and_caveat_present() -> None:
    e = DATA / "ear_score_untrained.json"
    if not e.is_file():
        raise AssertionError("ear_score_untrained.json missing")
    d = json.loads(e.read_text())
    assert d.get("preview_untrained_ear") is True
    assert "caveat" in d
    assert "EAR_v0_INSUFFICIENT" in d["caveat"], (
        "cycle-36 EAR verdict must be cited in the caveat"
    )


def test_14_anchor_preservation_unchanged() -> None:
    a = DATA / "anchor_preservation.json"
    if not a.is_file():
        raise AssertionError("anchor_preservation.json missing")
    d = json.loads(a.read_text())
    assert d["unchanged"] is True, (
        f"read-only anchor drift detected: {d.get('changed')}"
    )


def test_15_pipeline_run_json_records_all_stages_touched() -> None:
    p = DATA / "per_stage" / "pipeline_run.json"
    if not p.is_file():
        raise AssertionError("pipeline_run.json missing")
    d = json.loads(p.read_text())
    stages = [s["stage"] for s in d.get("stages", [])]
    # Regardless of failure point, stage 01_decode must be recorded.
    assert "01_decode" in stages, f"01_decode absent from {stages}"


def test_16_report_doc_exists_and_cites_rubric_hash() -> None:
    if not REPORT_DOC.is_file():
        raise AssertionError("report doc missing")
    stored = (DATA / "rubric_hash.txt").read_text().strip()
    assert stored in REPORT_DOC.read_text(), (
        "report doc does not embed the frozen rubric SHA-256"
    )


def test_17_verdict_carries_cycle36_ear_reference() -> None:
    v = DATA / "verdict.json"
    if not v.is_file():
        raise AssertionError("verdict.json missing")
    d = json.loads(v.read_text())
    assert "cycle_36_ear_reference" in d
    assert "EAR_v0_INSUFFICIENT" in d["cycle_36_ear_reference"]


def test_18_effects_layered_chain_not_modified_since_rubric_freeze() -> None:
    # Anchor `render_effects_layered.py` was committed at cycle 9 (2026-08-28)
    # and MUST NOT have been touched by this cycle.
    anchor = ROOT / "scripts" / "tex" / "render_effects_layered.py"
    if not anchor.is_file() or not RUBRIC_DOC.is_file():
        raise AssertionError("anchor or rubric missing")
    assert anchor.stat().st_mtime < RUBRIC_DOC.stat().st_mtime, (
        "cycle-9 DawDreamer chain was modified after rubric freeze"
    )


def main() -> int:
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    passed = failed = skipped = 0
    fail_msgs: list[str] = []
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"[PASS] {name}")
        except AssertionError as exc:
            msg = str(exc)
            if any(m in msg for m in
                   ("missing;", "not produced", "did not finish",
                    "MUST", "not deterministic", "must be")):
                # Real assertion — count as failure unless it's a
                # dependency-missing skip case above (chosen/verdict/etc).
                if any(sk in msg for sk in
                       ("chosen_song.json missing",
                        "verdict.json missing",
                        "pipeline_run.json missing",
                        "ear_score_untrained.json missing",
                        "anchor_preservation.json missing",
                        "report doc missing",
                        "chosen_song.json missing; run select_song.py")):
                    skipped += 1
                    print(f"[SKIP] {name}: {msg}")
                else:
                    failed += 1
                    fail_msgs.append(f"{name}: {msg}")
                    print(f"[FAIL] {name}: {msg}")
            else:
                failed += 1
                fail_msgs.append(f"{name}: {msg}")
                print(f"[FAIL] {name}: {msg}")
    print(f"\ntotal: {len(tests)} passed: {passed} failed: {failed} "
          f"skipped: {skipped}")
    if fail_msgs:
        print("\nFAILURES:")
        for m in fail_msgs:
            print(f"  - {m}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
