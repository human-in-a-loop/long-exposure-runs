#!/usr/bin/env python3
"""One-shot: remove partial batch_v5_n16 song folders and tmp_batch_v5_run2."""
import os, shutil, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for i in range(16):
    p = os.path.join(REPO, f'data/gen/batch_v5_n16/song_{i}')
    if os.path.isdir(p):
        shutil.rmtree(p)
        print('REMOVED', p)
t = os.path.join(REPO, 'tools/tmp_batch_v5_run2')
if os.path.isdir(t):
    shutil.rmtree(t)
    print('REMOVED', t)
# Also remove any batch_manifest.json (stale from potential prior run).
for name in ('batch_manifest.json','summary.tsv','provenance.jsonl','collision_analysis.json','collision_matrix.tsv','anchor_regression.json','hypothesis_verdict.json'):
    p = os.path.join(REPO, f'data/gen/batch_v5_n16/{name}')
    if os.path.isfile(p):
        os.remove(p)
        print('REMOVED', p)
print('done.')
