import json
pre=json.load(open('data/ear_v2p1/anchor_preservation_pre.json'))
post=json.load(open('data/ear_v2p1/anchor_preservation_v2p1.json'))
pre_ent = pre['entries']
post_ent = post['entries']
print('pre n_anchors:', pre['n_anchors'], 'entries:', len(pre_ent))
print('post n_anchors:', post['n_anchors'], 'entries:', len(post_ent), 'drift:', post.get('drift'))
pre_map = {e['path']: e for e in pre_ent}
post_map = {e['path']: e for e in post_ent}
missing = [p for p in pre_map if p not in post_map]
diffs = []
for p, ep in pre_map.items():
    if p in post_map:
        if ep.get('sha256') != post_map[p].get('sha256'):
            diffs.append((p, ep.get('sha256'), post_map[p].get('sha256')))
print('missing_in_post:', len(missing))
print('sha_diffs:', len(diffs))
if diffs: print('sample:', diffs[:3])
