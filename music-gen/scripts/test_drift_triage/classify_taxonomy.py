#!/usr/bin/python3
# created: 2026-08-29T18:33:00Z  cycle: 48  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _infra/pre-existing-test-drift-triage-clone-2
"""Classify each failure per the c48 Branch C rubric taxonomy with
priority-ordered first-match wins:
    c47-non-orthogonal > infra-brittleness > environmental-drift > c47-orthogonal.

Reads captured_failures.jsonl READ-ONLY.
Writes triage_taxonomy.tsv (canonical column order, sorted rows).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

print("[test_drift_triage.classify_taxonomy] startup", flush=True)

_ALLOWED = ("/usr/bin/python3",)
if sys.executable not in _ALLOWED and not os.environ.get("TEST_DRIFT_TRIAGE_ALLOW_ANY_PYTHON"):
    print(
        f"[test_drift_triage.classify_taxonomy] interpreter guard: expected one of "
        f"{_ALLOWED}, got {sys.executable!r}",
        file=sys.stderr,
    )
    sys.exit(2)

# Frozen c47 lock-set (verbatim from rubric §c47 lock-set)
C47_LOCK_SET = (
    "c47", "v2p1", "policy", "deprecation", "anchor.pin",
    "source.date", "source_date", "ear_v2p1", "adjudication",
)

# Frozen transient-state patterns (rubric §infra-brittleness)
BRITTLE_PATTERNS = [
    (r"\btempfile\b", "tempfile"),
    (r"\bpid\b", "pid"),
    (r"\bwall.clock\b", "wall-clock"),
    (r"\bport\b", "port"),
    (r"\bnetwork\b", "network"),
    (r"\btimeout\b", "timeout"),
    (r"\bhostname\b", "hostname"),
    (r"\brace\b", "race"),
]

# Frozen environmental-drift patterns (rubric §environmental-drift)
ENV_PATTERNS = [
    (r"\bversion\b", "dependency-version"),
    (r"\bimport\b", "dependency-import"),
    (r"\bModuleNotFoundError\b", "dependency-ModuleNotFoundError"),
    (r"\bImportError\b", "dependency-ImportError"),
    (r"\bnumpy\b", "dependency-numpy"),
    (r"\btorch\b", "dependency-torch"),
    (r"\bbasic-pitch\b", "dependency-basic-pitch"),
    (r"\bmscore3\b", "dependency-mscore3"),
    (r"\bdemucs\b", "dependency-demucs"),
    (r"\blibrosa\b", "dependency-librosa"),
    (r"\bpyloudnorm\b", "dependency-pyloudnorm"),
    (r"\bmusic21\b", "dependency-music21"),
    (r"\bNo such file\b", "path-No such file"),
    (r"\bFileNotFoundError\b", "path-FileNotFoundError"),
    (r"\bpath\b", "path-path"),
    (r"\banchor\b", "path-anchor"),
    (r"\bpresent\b", "path-present"),  # c9-onward "artifact X present" convention
    (r"\bmtime\b", "mtime-mtime"),
    (r"\bmodification time\b", "mtime-modification-time"),
    (r"\bfile.time\b", "mtime-file-time"),
]


def classify_one(identifier: str, message: str) -> tuple[str, str, str]:
    """Return (taxonomy_label, signal_source, signal_matched_pattern)."""
    ident_lc = identifier.lower()
    for tok in C47_LOCK_SET:
        if tok in ident_lc:
            return ("c47-non-orthogonal", "identifier", tok)
    for pat, name in BRITTLE_PATTERNS:
        if re.search(pat, message, re.IGNORECASE):
            return ("infra-brittleness", "message", name)
    for pat, name in ENV_PATTERNS:
        if re.search(pat, message, re.IGNORECASE):
            return ("environmental-drift", "message", name)
    return ("c47-orthogonal", "fall-through", "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = []
    with args.in_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    classified = []
    for r in rows:
        label, src, pat = classify_one(r["identifier"], r["message"])
        classified.append({
            "identifier": r["identifier"],
            "line": r["line"],
            "taxonomy_label": label,
            "signal_source": src,
            "signal_matched_pattern": pat,
        })

    # Canonical sort: by line then identifier (stable, deterministic)
    classified.sort(key=lambda x: (x["line"], x["identifier"]))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        f.write("identifier\tline\ttaxonomy_label\tsignal_source\tsignal_matched_pattern\n")
        for r in classified:
            f.write(
                f"{r['identifier']}\t{r['line']}\t{r['taxonomy_label']}\t"
                f"{r['signal_source']}\t{r['signal_matched_pattern']}\n"
            )
    print(f"[test_drift_triage.classify_taxonomy] classified {len(classified)} rows", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
