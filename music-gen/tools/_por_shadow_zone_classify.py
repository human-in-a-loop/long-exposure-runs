#!/usr/bin/env /usr/bin/python3
"""c31 Track E POR shadow-zone classifier.

Reads plan_of_record.md, identifies rows in the shadow zone
(after ## Pointer to ledger) and classifies each as duplicate-of-parseable
or unique. Used to plan safe deletion or comment conversion.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lines = (ROOT / "plan_of_record.md").read_text().splitlines(keepends=True)

boundary = None
sub_ms = None
for i, l in enumerate(lines):
    if l.startswith("## Pointer to ledger"):
        boundary = i
    if l.startswith("## Sub-milestones") and sub_ms is None:
        sub_ms = i

parseable_ids = set()
for i in range(sub_ms):
    m = re.match(r"^\| ([^|]+) \|", lines[i])
    if m:
        mid = m.group(1).strip()
        if mid.startswith(("M-", "_")):
            parseable_ids.add(mid)

shadow_ids = []
for i in range(boundary, len(lines)):
    m = re.match(r"^\| ([^|]+) \|", lines[i])
    if m:
        mid = m.group(1).strip()
        if mid.startswith(("M-", "_")):
            shadow_ids.append((i + 1, mid))

dupes = [(ln, mid) for ln, mid in shadow_ids if mid in parseable_ids]
uniques = [(ln, mid) for ln, mid in shadow_ids if mid not in parseable_ids]

print(f"boundary line: {boundary+1}")
print(f"sub_milestones line: {sub_ms+1}")
print(f"Parseable-zone milestone_ids: {len(parseable_ids)}")
print(f"Shadow-zone rows (after Pointer to ledger): {len(shadow_ids)}")
print(f"  - Duplicates of parseable: {len(dupes)}")
print(f"  - Unique to shadow: {len(uniques)}")
if uniques:
    print()
    print("UNIQUE-TO-SHADOW rows (MUST NOT be deleted without registering canonical row first):")
    for ln, mid in uniques:
        print(f"  line {ln}: {mid}")
