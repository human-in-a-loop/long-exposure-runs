#!/usr/bin/python3
# created: 2026-08-29T17:31:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-registration-gate-policy-scope-verification-clone-1
"""Apply the c47 Branch B rubric to the classified table → verdict.json.

Rules (from docs/pre_registration_gate_policy_scope_verification_rubric.md):
  worker_in_turn_count == 0                 → HARNESS_CONSTRAINT_CONFIRMED
  worker_in_turn_count > 0 AND sweep > 0    → MIXED
  worker_in_turn_count > 0 AND sweep == 0   → HARNESS_CONSTRAINT_LIFTED

`sweep` here is `periodic-sweep + merge-integration + harness-auto-write`
(all three represent commits landed by the harness, not inside a worker
turn). `worker_in_turn_count` is the sum of `worker-turn + auditor-turn
+ researcher-turn` in the session_context matrix.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_ALLOWED = ("/usr/bin/python3",)
if sys.executable not in _ALLOWED and not os.environ.get("PRE_REG_POLICY_VERIFY_ALLOW_ANY_PYTHON"):
    print("[pre_reg_policy_verify.verdict] interpreter guard failed", file=sys.stderr)
    sys.exit(2)

BANNER = "[pre_reg_policy_verify.verdict] c47 Branch B — starting"
print(BANNER)

ROOT = Path(__file__).resolve().parent.parent.parent

_SWEEP_CLASSES = ("periodic-sweep", "merge-integration", "harness-auto-write")
_IN_TURN_CLASSES = ("worker-turn", "auditor-turn", "researcher-turn")


def load_matrix(matrix_tsv: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    lines = matrix_tsv.read_text().splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        counts[parts[0]] = int(parts[1])
    return counts


def sample_evidence(class_tsv: Path, wanted_classes: tuple[str, ...], k: int = 5) -> list[dict]:
    """Deterministic first-k sample per class (input order preserved)."""
    seen: dict[str, int] = {c: 0 for c in wanted_classes}
    out: list[dict] = []
    lines = class_tsv.read_text().splitlines()
    header = lines[0].split("\t") if lines else []
    idx_sc = header.index("session_context")
    idx_sha = header.index("commit_sha")
    idx_ts = header.index("iso_ts")
    idx_sub = header.index("subject_first_60")
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        sc = parts[idx_sc]
        if sc in seen and seen[sc] < k:
            out.append({
                "commit_sha": parts[idx_sha],
                "iso_ts": parts[idx_ts],
                "subject": parts[idx_sub],
                "session_context": sc,
            })
            seen[sc] += 1
    return out


def compute_verdict(counts: dict[str, int]) -> tuple[str, str]:
    sweep = sum(counts.get(c, 0) for c in _SWEEP_CLASSES)
    in_turn = sum(counts.get(c, 0) for c in _IN_TURN_CLASSES)
    if in_turn == 0:
        return "HARNESS_CONSTRAINT_CONFIRMED", (
            "worker_in_turn_count == 0 across git-log history")
    if sweep == 0:
        return "HARNESS_CONSTRAINT_LIFTED", (
            "worker_in_turn_count > 0 and periodic-sweep envelope absent")
    return "MIXED", (
        f"worker_in_turn_count={in_turn} > 0 AND sweep_count={sweep} > 0")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "session_context_matrix.tsv")
    ap.add_argument("--classified", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "commit_classification.tsv")
    ap.add_argument("--rubric", type=Path,
                    default=ROOT / "docs" / "pre_registration_gate_policy_scope_verification_rubric.md")
    ap.add_argument("--rubric-hash", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "rubric_hash.txt")
    ap.add_argument("--out", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "verdict.json")
    args = ap.parse_args()

    counts = load_matrix(args.matrix)
    verdict_label, rule_applied = compute_verdict(counts)

    disk_hash = args.rubric_hash.read_text().strip()
    doc_hash = hashlib.sha256(args.rubric.read_bytes()).hexdigest()
    assert disk_hash == doc_hash, (
        f"three-way rubric_hash byte-equality failure: disk={disk_hash} doc={doc_hash}")

    evidence = sample_evidence(args.classified,
                               _SWEEP_CLASSES + _IN_TURN_CLASSES + ("unknown",), k=3)

    doc = {
        "verdict": verdict_label,
        "rubric_hash": doc_hash,
        "counts_by_context": counts,
        "sweep_total": sum(counts.get(c, 0) for c in _SWEEP_CLASSES),
        "in_turn_total": sum(counts.get(c, 0) for c in _IN_TURN_CLASSES),
        "evidence_commits_sample": evidence,
        "decision_rule_applied": rule_applied,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"[pre_reg_policy_verify.verdict] verdict={verdict_label} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
