#!/usr/bin/python3
# c50 close-correction tests.
# Created: 2026-08-29
# Cycle: 50
# Run id: run-2026-08-28T040704Z
# Agent: worker
# Milestone: _infra/adopt-cycle50-tests
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_ledger():
    return [json.loads(l) for l in (ROOT / "promise_ledger.jsonl").read_text().splitlines() if l.strip()]


def test_01_promise_check_zero_error_via_cli():
    result = subprocess.run(
        ["/usr/bin/python3", "-m", "long_exposure.tools.promise_check", "."],
        cwd=str(ROOT), capture_output=True, text=True, timeout=180,
    )
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    err_lines = [l for l in combined.splitlines() if l.lstrip().startswith("x ERROR")]
    assert len(err_lines) == 0, f"promise_check `x ERROR` lines: {err_lines[:5]}"


def test_02_six_c49_correction_rows_in_plan_of_record():
    plan = (ROOT / "plan_of_record.md").read_text()
    for mid in [
        "M-RECREATE-2/accurate-small-set/rubric-committed",
        "M-RECREATE-2/accurate-small-set/focus-set-selected",
        "M-RECREATE-2/accurate-small-set/rc0-baseline-captured",
        "M-RECREATE-2/accurate-small-set/rc-stubs-registered",
        "M-INGEST-1/egress-probe-cycle49",
        "M-INGEST-1/egress-probe-cycle48-clone-1",
    ]:
        assert f"| {mid} " in plan, f"missing plan-of-record row: {mid}"


def test_03_supersede_event_carries_str_supersedes_path():
    rows = read_ledger()
    hits = [r for r in rows if r["milestone_id"] == "_plan/m-recreate-2-rubric-v2-supersede"]
    assert len(hits) >= 1, "supersede event missing"
    ev = hits[-1]
    sp = ev.get("supersedes_path")
    assert isinstance(sp, str), f"c14 lemma: supersedes_path must be str, got {type(sp)}"
    assert sp == "docs/m_recreate_2_accurate_small_set_rubric.md"


def test_04_v1_rubric_sha_byte_equal():
    v1_hash = (ROOT / "data/recreate_v2/rubric_hash.txt").read_text().strip()
    v1_doc_sha = hashlib.sha256(
        (ROOT / "docs/m_recreate_2_accurate_small_set_rubric.md").read_bytes()
    ).hexdigest()
    assert v1_hash == v1_doc_sha, "c49 v1 chain broken"
    assert v1_hash == "958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d"


def test_05_c50_ledger_event_count():
    rows = read_ledger()
    c50_count = sum(1 for r in rows if r.get("cycle") == 50)
    assert c50_count >= 10, f"expected >=10 c50 events, got {c50_count}"


def test_06_c49_report_addendum_present():
    txt = (ROOT / "docs/c49_worker_report.md").read_text()
    assert "## §11 — c49-close correction (c50 addendum)" in txt
    assert "Priority 1 fix" in txt
    assert "Priority 2 test-scope mismatch" in txt
    assert "OPERATOR UPDATE" in txt


def test_07_c49_report_first_15_lines_stable():
    # Prior §1 header + first §10 handoff seed must survive. First 15 lines is
    # a conservative header-region check (title + metadata + Overview intro).
    b = b"\n".join(
        (ROOT / "docs/c49_worker_report.md").read_bytes().splitlines()[:15]
    ) + b"\n"
    sha = hashlib.sha256(b).hexdigest()
    assert sha == "f637b284f6d3ac41229be6062e21ef113aa1d95472c58eeefab70d5932bfbd3e", (
        f"c49 report head drift: {sha}"
    )


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            fails += 1
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    sys.exit(1 if fails else 0)
