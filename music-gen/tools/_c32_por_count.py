#!/usr/bin/python3
"""c32 helper: count parseable Milestones-section rows in plan_of_record.md."""
import re
import pathlib

por = pathlib.Path('plan_of_record.md').read_text()
m = re.search(r'^## Milestones\s*\n(.*?)^## Sub-milestones', por, re.M | re.S)
assert m, 'Milestones section not found'
body = m.group(1)
rows = [l for l in body.splitlines()
        if l.startswith('|') and '---' not in l and 'Milestone ID' not in l]
print('parseable_milestones:', len(rows))
