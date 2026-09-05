#!/usr/bin/env /usr/bin/python3
"""c31 Track E — POR shadow-zone consolidation.

Moves all 37 unique-to-shadow milestone rows from below `## Pointer to ledger`
into the parseable `## Milestones` table (immediately before `## Sub-milestones`).
Deletes the 23 duplicate rows. Preserves narrative paragraphs (c9 acceptance
fork, c9 heartbeat-retired, PROC lines, etc.) verbatim in place.

Contract:
  - Every canonical parseable-zone row: BYTE-IDENTICAL pre==post.
  - Every unique-to-shadow row: MOVED verbatim (same text) into parseable zone.
  - Every duplicate shadow row: DELETED.
  - Every non-row line in shadow zone (narrative, blanks, PROC): preserved verbatim.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POR = ROOT / "plan_of_record.md"
text = POR.read_text()
lines = text.splitlines(keepends=True)

# Locate section boundaries
i_milestones = None
i_sub_ms = None
i_pointer = None
for i, l in enumerate(lines):
    if l.startswith("## Milestones") and i_milestones is None:
        i_milestones = i
    if l.startswith("## Sub-milestones") and i_sub_ms is None:
        i_sub_ms = i
    if l.startswith("## Pointer to ledger") and i_pointer is None:
        i_pointer = i

assert i_milestones and i_sub_ms and i_pointer
assert i_milestones < i_sub_ms < i_pointer

# Build parseable-zone milestone_id set
parseable_ids = set()
for i in range(i_milestones, i_sub_ms):
    m = re.match(r"^\| ([^|]+) \|", lines[i])
    if m:
        mid = m.group(1).strip()
        if mid.startswith(("M-", "_")):
            parseable_ids.add(mid)

# Partition shadow zone (after pointer-to-ledger) into row lines (dupes / uniques)
# and non-row lines (narrative/PROC/blank/heading).
shadow_lines = lines[i_pointer:]
kept_narrative = []          # lines to preserve in shadow zone
moved_to_parseable = []      # unique rows to inject before ## Sub-milestones
for l in shadow_lines:
    m = re.match(r"^\| ([^|]+) \|", l)
    if m:
        mid = m.group(1).strip()
        if mid.startswith(("M-", "_")):
            if mid in parseable_ids:
                # Duplicate — drop
                continue
            else:
                # Unique — inject into parseable
                moved_to_parseable.append(l)
                continue
        # Non-milestone table row (header, separator) — keep as narrative
    kept_narrative.append(l)

# Reassemble file:
#   [0..i_sub_ms)    parseable ## Milestones — verbatim
#   + moved rows (unique-to-shadow, now hoisted into canonical section)
#   + [i_sub_ms..i_pointer)  ## Sub-milestones + Housekeeping + Out-of-scope — verbatim
#   + kept_narrative (## Pointer to ledger onward, minus the 60 old shadow rows)
new_lines = (
    lines[:i_sub_ms]
    + ["\n"]
    + moved_to_parseable
    + ["\n"]
    + lines[i_sub_ms:i_pointer]
    + kept_narrative
)

new_text = "".join(new_lines)

# Write back
POR.write_text(new_text)

# Post-check: re-count
lines2 = new_text.splitlines(keepends=True)
sub_ms2 = None
pointer2 = None
for i, l in enumerate(lines2):
    if l.startswith("## Sub-milestones") and sub_ms2 is None:
        sub_ms2 = i
    if l.startswith("## Pointer to ledger") and pointer2 is None:
        pointer2 = i

parseable_ids_post = set()
for i in range(sub_ms2):
    m = re.match(r"^\| ([^|]+) \|", lines2[i])
    if m:
        mid = m.group(1).strip()
        if mid.startswith(("M-", "_")):
            parseable_ids_post.add(mid)

shadow_ids_post = []
for i in range(pointer2, len(lines2)):
    m = re.match(r"^\| ([^|]+) \|", lines2[i])
    if m:
        mid = m.group(1).strip()
        if mid.startswith(("M-", "_")):
            shadow_ids_post.append(mid)

print(f"Pre-consolidation parseable-zone milestones: {len(parseable_ids)}")
print(f"Post-consolidation parseable-zone milestones: {len(parseable_ids_post)}")
print(f"Rows moved from shadow to parseable: {len(moved_to_parseable)}")
print(f"Rows deleted (duplicates): 23 (60 total shadow rows - {len(moved_to_parseable)} moved)")
print(f"Shadow-zone rows remaining: {len(shadow_ids_post)}")
print(f"Line-count delta: {len(lines)} → {len(lines2)}")
