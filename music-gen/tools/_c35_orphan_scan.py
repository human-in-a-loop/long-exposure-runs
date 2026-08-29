"""Scan c35 output directories for orphan artifacts not in the main ledger."""
import json
from pathlib import Path

WS = Path('/home/user/long-exposure-runs/music-gen')
tracked = set()
with open(WS / 'promise_ledger.jsonl') as f:
    for line in f:
        r = json.loads(line)
        for a in r.get('artifacts') or []:
            if isinstance(a, str):
                tracked.add(a.rstrip('/'))

targets = [
    'data/palette_v2_render',
    'data/gen_palette_batch_v2',
    'data/anchor_manifest_v1',
    'scripts/palette_v2_render',
    'scripts/gen_palette_batch_v2',
    'scripts/anchor_manifest',
]
for tgt in targets:
    root = WS / tgt
    if not root.exists():
        print(f'{tgt}: NOT PRESENT')
        continue
    files = [str(p.relative_to(WS)) for p in sorted(root.rglob('*')) if p.is_file()]
    orphans = [f for f in files if f not in tracked]
    print(f'{tgt}: {len(files)} files, {len(orphans)} orphans')
    for o in orphans[:8]:
        print(f'  ORPHAN: {o}')
    if len(orphans) > 8:
        print(f'  ... and {len(orphans)-8} more')

# top-level artifact files
for p in [
    'data/anchor_manifest_v1.json',
    'docs/anchor_manifest_v1.md',
    'docs/fanout_launched_event_convention.md',
    'docs/palette_v2_hydration_render_report.md',
    'docs/palette_v2_hydration_render_rubric.md',
    'docs/palette_driven_batch_v2_sampler_diversified_report.md',
    'docs/palette_driven_batch_v2_sampler_diversified_rubric.md',
    'docs/anchor_manifest_v1_report.md',
    'docs/anchor_manifest_v1_rubric.md',
]:
    if (WS / p).exists():
        status = 'tracked' if p in tracked else 'ORPHAN'
        print(f'{p}: {status}')
    else:
        print(f'{p}: NOT PRESENT')
