#!/usr/bin/python3
# created: 2026-08-29T17:31:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-registration-gate-policy-scope-verification-clone-1
"""Two-signal commit classifier per c47 Branch B rubric §Session-context classes.

Signal (a): author-email pattern → email_class ∈ {bot, human}.
Signal (b): commit-subject regex → marker_class ∈ {periodic-sweep,
            merge-integration, worker-turn, auditor-turn,
            researcher-turn, harness-auto-write, unknown}.

session_context is derived from marker_class (email cannot distinguish
worker-turn from periodic-sweep in this session — all commits carry the
bot email `noreply@anthropic.com`). confidence:
  high   — bot email + non-unknown marker.
  medium — bot email + unknown marker OR disagreement.
  low    — reserved for future human contributor rows.

Deterministic; no PRNG; interpreter-guarded.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

_ALLOWED = ("/usr/bin/python3",)
if sys.executable not in _ALLOWED and not os.environ.get("PRE_REG_POLICY_VERIFY_ALLOW_ANY_PYTHON"):
    print(f"[pre_reg_policy_verify.classify_commits] interpreter guard: expected one of "
          f"{_ALLOWED}, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

BANNER = "[pre_reg_policy_verify.classify_commits] c47 Branch B — starting"
print(BANNER)

ROOT = Path(__file__).resolve().parent.parent.parent

# Ordered regex table — FIRST match wins. Anchors are intentional.
_MARKER_RULES = [
    # merge-integration must be checked BEFORE periodic-sweep because
    # some commits carry both markers ("periodic sweep" + "post-merge").
    ("merge-integration", re.compile(r"\((post-merge cycle \d+|cycle \d+ merge[^)]*)\)", re.I)),
    ("periodic-sweep", re.compile(r"\(periodic sweep\)", re.I)),
    ("auditor-turn", re.compile(r"^(audit:|AUDIT:|_manager/audit-)", re.I)),
    ("researcher-turn", re.compile(r"^(researcher:|plan:|_plan/)", re.I)),
    ("worker-turn", re.compile(
        r"^(M-[A-Z]+-?\d*(?:/[A-Za-z0-9_-]+)*:|_infra/|_manager/|_archive/|_run/|commit\s+[a-z])")),
    # harness-auto-write: a bare "Add music-gen run artifacts" with no envelope.
    ("harness-auto-write", re.compile(r"^Add music-gen run artifacts\s*$")),
]

# Human-readable bot marker.
_BOT_EMAIL = "noreply@anthropic.com"


def classify_email(email: str) -> str:
    return "bot" if email.strip().lower() == _BOT_EMAIL else "human"


def classify_marker(subject: str) -> str:
    s = subject.strip()
    for label, rx in _MARKER_RULES:
        if rx.search(s):
            return label
    return "unknown"


def derive_session_context(email_class: str, marker_class: str) -> tuple[str, str]:
    """Return (session_context, confidence)."""
    if marker_class == "unknown":
        return "unknown", "medium"
    if email_class == "bot":
        return marker_class, "high"
    # human email — reserved; not observed in this session.
    return marker_class, "low"


def parse_row(line: str) -> tuple[str, str, str, str] | None:
    line = line.rstrip("\n")
    if not line:
        return None
    parts = line.split("\t", 3)
    if len(parts) != 4:
        return None
    sha, email, ts, subject = parts
    return sha, email, ts, subject


def classify_file(raw_tsv: Path, out_tsv: Path) -> int:
    header = ("commit_sha\tauthor_email\tiso_ts\tsubject_first_60\t"
              "email_class\tmarker_class\tsession_context\tconfidence\n")
    lines = [header]
    n = 0
    for line in raw_tsv.read_text().splitlines():
        row = parse_row(line)
        if row is None:
            continue
        sha, email, ts, subject = row
        subject_short = subject[:60].replace("\t", " ")
        ec = classify_email(email)
        mc = classify_marker(subject)
        sc, conf = derive_session_context(ec, mc)
        lines.append(f"{sha}\t{email}\t{ts}\t{subject_short}\t{ec}\t{mc}\t{sc}\t{conf}\n")
        n += 1
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    out_tsv.write_text("".join(lines))
    print(f"[pre_reg_policy_verify.classify_commits] classified {n} commits -> {out_tsv}")
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "git_log_raw.tsv")
    ap.add_argument("--out", type=Path,
                    default=ROOT / "data" / "pre_reg_policy_verify" / "commit_classification.tsv")
    args = ap.parse_args()
    classify_file(args.raw, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
