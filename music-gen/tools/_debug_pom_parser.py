#!/usr/bin/env -S /usr/bin/python3
import re
text = open("plan_of_record.md").read()
m = re.search(r"## Milestones\s*\n(.+?)(?:\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
sec = m.group(1)
print("section length lines:", len(sec.splitlines()))
last_lines = sec.splitlines()[-5:]
for i, ln in enumerate(last_lines):
    print(f"last-{5-i}: starts_with_pipe={ln.startswith('|')} len={len(ln)} preview={ln[:80]!r}")
print("---")
saw_sep = False
for i, line in enumerate(sec.splitlines()):
    line2 = line.strip()
    if not line2.startswith("|"):
        continue
    if "palette" in line2:
        cells = [c.strip() for c in line2.strip("|").split("|")]
        print(f"line-idx {i}: cells={len(cells)}, first={cells[0][:60]!r}")
