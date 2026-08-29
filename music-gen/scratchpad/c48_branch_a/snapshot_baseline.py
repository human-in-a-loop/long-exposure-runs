#!/usr/bin/env python3
"""Snapshot per-row SHA-256 of promise_ledger.jsonl BEFORE any edit to long_exposure/*.

Also captures re-derived event_ids under both the c47-verbatim (current) writer
and the anticipated c48 flag-OFF / flag-ON semantics so the report §5 can pin
the divergence marker precisely.
"""
import hashlib
import json
import os
import pathlib
import sys

WS = pathlib.Path('/home/user/long-exposure-runs/music-gen')
LEDGER = WS / 'promise_ledger.jsonl'
OUT_DIR = WS / 'data' / 'harness_and_writer_hardening_v3'
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("c48 Branch A — baseline snapshot (pre-edit)")
print("=" * 60)

sys.path.insert(0, '/home/user/human-in-a-loop/long-exposure')
from long_exposure.tools._ledger_schema import content_hash_event_id, canonical_json  # noqa

lines = LEDGER.read_bytes().splitlines(keepends=True)
print(f"loaded {len(lines)} raw lines")

manifest_path = OUT_DIR / 'baseline_replay_manifest.jsonl'
with open(manifest_path, 'wb') as f:
    for i, raw in enumerate(lines):
        row = json.loads(raw)
        rec = {
            'lineno': i + 1,
            'event_id': row.get('event_id'),
            'milestone_id': row.get('milestone_id'),
            'canonical_sha256_pre_edit': hashlib.sha256(raw.rstrip(b'\n')).hexdigest(),
        }
        f.write((json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode('utf-8'))

manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
(OUT_DIR / 'baseline_manifest_sha.txt').write_text(manifest_sha + '\n')
print(f"manifest SHA: {manifest_sha}")

# Line-745 evidence for report §5
line_745 = json.loads(lines[744])
line_745_stripped = {k: v for k, v in line_745.items() if k != 'supersedes'}
evidence = {
    'lineno': 745,
    'milestone_id': line_745['milestone_id'],
    'on_disk_event_id': line_745['event_id'],
    'supersedes': line_745.get('supersedes'),
    'supersedes_path': line_745.get('supersedes_path'),
    're_derived_supersedes_IN_hash': content_hash_event_id(line_745),
    're_derived_supersedes_OUT_hash': content_hash_event_id(line_745_stripped),
}
(OUT_DIR / 'line_745_divergence.json').write_text(
    json.dumps(evidence, indent=2, sort_keys=True) + '\n'
)
print("line-745 divergence evidence:")
print(json.dumps(evidence, indent=2, sort_keys=True))

# Pre-edit SHAs of the two files we're about to edit, for the anchor manifest.
pre_edit = {}
for label, p in [
    ('workspace_bootstrap.py', '/home/user/human-in-a-loop/long-exposure/long_exposure/workspace_bootstrap.py'),
    ('_ledger_schema.py', '/home/user/human-in-a-loop/long-exposure/long_exposure/tools/_ledger_schema.py'),
]:
    pre_edit[label] = hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

(OUT_DIR / 'pre_edit_module_shas.json').write_text(
    json.dumps(pre_edit, indent=2, sort_keys=True) + '\n'
)
print("pre-edit module SHAs:")
print(json.dumps(pre_edit, indent=2, sort_keys=True))
