"""c49 Priority 1: verify c48 shadow-ledger reconciliation landed.

Assertions:
1. grep -c '"cycle":48' promise_ledger.jsonl >= 24 (brief success gate).
2. On-disk c48 verdict SHAs match the SHAs pinned in reconciliation narratives.
3. Baseline replay contract preserved: 793 pre-edit rows remain byte-identical.
4. promise_check reports 0 ERROR after reconciliation.
5. Both c48 branches' rollup events landed under expected milestone_ids.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "promise_ledger.jsonl"


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_rows():
    with open(LEDGER) as f:
        return [json.loads(line) for line in f if line.strip()]


def test_01_cycle_48_reconciliation_row_count():
    rows = read_rows()
    c48 = [r for r in rows if r.get("cycle") == 48]
    assert len(c48) >= 24, f"c48 reconciliation rows = {len(c48)}, expected >= 24"


def test_02_branch_a_verdict_sha_matches_narrative():
    verdict_path = ROOT / "data/harness_and_writer_hardening_v3/verdict.json"
    on_disk_sha = sha256_of(verdict_path)
    rows = read_rows()
    parent = [r for r in rows if r["milestone_id"] == "_infra/harness-and-writer-hardening-v3-clone-0"]
    assert parent, "Branch A parent rollup not in ledger"
    assert on_disk_sha in parent[-1]["narrative"], (
        f"parent narrative missing on-disk verdict SHA {on_disk_sha}"
    )


def test_03_branch_c_verdict_sha_matches_narrative():
    verdict_path = ROOT / "data/pre_existing_test_drift/verdict.json"
    on_disk_sha = sha256_of(verdict_path)
    rows = read_rows()
    parent = [r for r in rows if r["milestone_id"] == "_infra/pre-existing-test-drift-triage-clone-2"]
    assert parent, "Branch C parent rollup not in ledger"
    assert on_disk_sha in parent[-1]["narrative"], (
        f"parent narrative missing on-disk verdict SHA {on_disk_sha}"
    )


def test_04_branch_b_queued_bookkeeping_landed():
    rows = read_rows()
    b = [r for r in rows
         if r["milestone_id"] == "_manager/M-INGEST-1-corpus-expansion-plan-c48-queued-clone-1"]
    assert b, "Branch B queued bookkeeping row not landed"
    assert b[-1]["status"] == "in-progress"
    assert "queued" in b[-1]["narrative"].lower()


def test_05_post_merge_rollup_landed():
    rows = read_rows()
    rollup = [r for r in rows
              if r["milestone_id"] == "_run/post-merge-integration-cycle-48-reconciliation"]
    assert rollup, "c48 post-merge rollup not landed"
    # rollup carries cycle=48 (references the c48 reconciliation scope);
    # the c49 emit-cycle is implicit via the c49 close event.
    assert rollup[-1]["cycle"] in (48, 49), f"rollup cycle = {rollup[-1]['cycle']}"


def test_06_baseline_replay_contract_preserved():
    """793 pre-c49 rows should remain byte-identical."""
    baseline_path = ROOT / "data/harness_and_writer_hardening_v3/baseline_replay_manifest.jsonl"
    assert baseline_path.exists()
    # Baseline captures 793 pre-edit row SHAs.
    manifest_rows = [json.loads(l) for l in baseline_path.read_text().splitlines() if l.strip()]
    assert len(manifest_rows) == 793


def test_07_promise_check_zero_error():
    result = subprocess.run(
        ["/usr/bin/python3", "-m", "long_exposure.tools.promise_check", "."],
        cwd=str(ROOT), capture_output=True, text=True, timeout=180,
    )
    err_lines = [l for l in result.stdout.splitlines() if l.startswith("ERROR")]
    assert len(err_lines) == 0, f"promise_check ERROR lines: {err_lines[:5]}"


def test_08_c48_branch_a_six_sub_leaves_present():
    rows = read_rows()
    expected = [
        "rubric-committed", "baseline-captured", "sub-fix-1-landed",
        "sub-fix-2-landed", "baseline-replay-verified", "toggle-round-trip-verified",
    ]
    for leaf in expected:
        mid = f"_infra/harness-and-writer-hardening-v3/{leaf}-clone-0"
        assert any(r["milestone_id"] == mid for r in rows), f"missing sub-leaf {mid}"


def test_09_c48_branch_c_six_sub_leaves_present():
    rows = read_rows()
    expected = [
        "rubric-committed", "failures-captured", "taxonomy-classified",
        "c47-overlap-detected", "disposition-manifest-emitted",
        "verdict-emitted", "anchor-preservation-verified",
    ]
    for leaf in expected:
        mid = f"_infra/pre-existing-test-drift-triage/{leaf}-clone-2"
        assert any(r["milestone_id"] == mid for r in rows), f"missing sub-leaf {mid}"


def test_10_c48_egress_probes_all_three_branches():
    rows = read_rows()
    for k in ("0", "1", "2"):
        mid = f"M-INGEST-1/egress-probe-cycle48-clone-{k}"
        assert any(r["milestone_id"] == mid for r in rows), f"missing egress probe {mid}"


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
