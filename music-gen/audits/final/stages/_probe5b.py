import json, hashlib, os
ap = json.load(open('data/rc10_impl/guitar_piano/anchor_preservation.json'))
post = ap['post']; pre = ap['pre']
print("n_entries:", ap['n_entries'], "diff_count:", ap['diff_count'])
print("pre==post?:", pre == post)
mismatches = []
missing = []
for path, expected in post.items():
    if not os.path.exists(path):
        missing.append(path); continue
    actual = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if actual != expected:
        mismatches.append((path, expected[:16], actual[:16]))
print("live_mismatch:", len(mismatches))
print("live_missing:", len(missing))
if mismatches: print("first 3:", mismatches[:3])
if missing: print("first 3 missing:", missing[:3])
# also check c33 render_stem invariant
rs = "scripts/palette_render/render_stem.py"
if os.path.exists(rs):
    actual = hashlib.sha256(open(rs,'rb').read()).hexdigest()
    print("render_stem.py SHA:", actual)
    print("in anchor?", rs in post, "match?", post.get(rs) == actual)
