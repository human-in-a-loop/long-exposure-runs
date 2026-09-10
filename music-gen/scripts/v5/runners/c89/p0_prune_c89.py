#!/usr/bin/python3
"""c89 P0: prune regenerable old-session scratchpad tempdirs (auditor render tempdirs) under /tmp/claude-0; nothing in the workspace."""
import json, os, shutil, subprocess, time
ROOT = '/tmp/claude-0/-home-user-long-exposure-runs-music-gen'
KEEP = 'd01bfa74-52ed-4193-afa8-b9da1c56eb02'  # this session
def df():
    out = subprocess.run(['df', '-P', '/home/user/long-exposure-runs/music-gen'], capture_output=True, text=True).stdout.strip().splitlines()[-1].split()
    return {'used_pct': int(out[4].rstrip('%')), 'avail_gb': round(int(out[3]) / 1e6, 3)}
def dsize(p):
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs if os.path.exists(os.path.join(r, f)))
rec = {'kind': 'c89 P0 disk prune', 'cycle': 89, 'harness_cycle': 133, 'agent': 'worker', 'df_open': df(), 'pruned': [], 'skipped_note': 'nothing under the workspace; /tmp/tfhub_modules (VGGish cache) and older non-session /tmp render dirs left untouched'}
for d in sorted(os.listdir(ROOT)):
    if d == KEEP:
        continue
    p = os.path.join(ROOT, d)
    sz = dsize(p)
    if sz > 50e6:
        shutil.rmtree(p, ignore_errors=True)
        rec['pruned'].append({'path': p, 'bytes': sz})
rec['pruned_mb'] = round(sum(x['bytes'] for x in rec['pruned']) / 1e6, 1)
rec['df_after'] = df()
rec['ts'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
os.makedirs('/home/user/long-exposure-runs/music-gen/data/v5/logs', exist_ok=True)
with open('/home/user/long-exposure-runs/music-gen/data/v5/logs/c89_prune.json', 'w') as f:
    json.dump(rec, f, indent=2)
print(json.dumps(rec, indent=1))
