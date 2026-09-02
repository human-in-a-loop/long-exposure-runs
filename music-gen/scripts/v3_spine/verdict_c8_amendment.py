#!/usr/bin/env python3
"""c8 Track 1: Emit verdict.c8_amendment.json (append-only sibling to c7 verdict).

Records SHA drift on docs/v3_spine_rc7_canonicality_decision_note.md between
the c7-pinned value (verdict.rc7_canonicality_note.sha256) and on-disk SHA at
c8 top-of-cycle. Attempts git-log recovery of the prior blob; if unavailable,
treats current on-disk as canonical per c7 auditor guidance.

Does NOT modify data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json
in place — this is an append-only sibling.

Milestone: M-V3-SPINE-1/verdict-c7-sha-drift-amended

FD-1: no method tuning; drift is a first-class finding.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"verdict_c8_amendment requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

C7_VERDICT = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json"
NOTE_PATH = _REPO / "docs/v3_spine_rc7_canonicality_decision_note.md"
OUT_JSON = _REPO / "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.c8_amendment.json"
SNAPSHOT_OUT = _REPO / "data/v3_spine/cycle8/rc7_note_c7_snapshot.md"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _try_git_blob_recover(sha: str) -> bool:
    """Attempt to recover blob `sha` via `git cat-file`. Returns True on success."""
    try:
        r = subprocess.run(
            ["git", "cat-file", "-p", sha],
            capture_output=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout:
            SNAPSHOT_OUT.parent.mkdir(parents=True, exist_ok=True)
            SNAPSHOT_OUT.write_bytes(r.stdout)
            return True
    except Exception:
        pass
    return False


def main() -> None:
    if not C7_VERDICT.is_file():
        raise RuntimeError(f"c7 verdict missing: {C7_VERDICT}")
    if not NOTE_PATH.is_file():
        raise RuntimeError(f"rc7 note missing: {NOTE_PATH}")

    c7_verdict = json.loads(C7_VERDICT.read_text())
    pinned = c7_verdict["rc7_canonicality_note"]["sha256"]
    on_disk = _sha256(NOTE_PATH)

    prior_recoverable = False
    diff_summary: str | None = None

    if pinned != on_disk:
        # Try git-log recovery.
        prior_recoverable = _try_git_blob_recover(pinned)
        if prior_recoverable:
            try:
                r = subprocess.run(
                    ["diff", "-u", str(SNAPSHOT_OUT), str(NOTE_PATH)],
                    capture_output=True, timeout=10, text=True,
                )
                # count changed lines (lines starting with + or -, excluding header)
                n_changed = sum(
                    1 for ln in (r.stdout or "").splitlines()
                    if (ln.startswith("+") or ln.startswith("-"))
                    and not ln.startswith("+++") and not ln.startswith("---")
                )
                diff_summary = f"{n_changed}_lines_changed"
            except Exception:
                diff_summary = "diff_failed"

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "cycle": 8,
        "amends": "cycle7/verdict.json",
        "amended_field": "rc7_canonicality_note.sha256",
        "pinned_sha_from_c7": pinned,
        "on_disk_sha_at_c8": on_disk,
        "prior_version_recoverable": prior_recoverable,
        "diff_summary": diff_summary,
        "canonical_designation": "current_on_disk",
        "root_cause": (
            "post-emission edit to docs/v3_spine_rc7_canonicality_decision_note.md; "
            "c7 test suite did not enforce verdict_sha ↔ on_disk equality"
        ),
        "closure_action": "c8_generic_invariant_test_lands",
        "note_path": "docs/v3_spine_rc7_canonicality_decision_note.md",
        "c7_verdict_path": "data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json",
        "c7_verdict_sha256": _sha256(C7_VERDICT),
        "drift_detected": (pinned != on_disk),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_JSON}")
    print(f"drift_detected={payload['drift_detected']} "
          f"prior_recoverable={prior_recoverable}")


if __name__ == "__main__":
    main()
