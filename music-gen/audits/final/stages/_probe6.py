import json
m = json.load(open('data/rc10_impl/guitar_piano/ab_pairs_manifest.json'))
print("type:", type(m).__name__, "len:", len(m))
if isinstance(m, list):
    print("first entry keys:", list(m[0].keys()))
    print("first entry:", m[0])
    uniq = set((e.get('song_id'), e.get('stem')) for e in m)
    print("unique (song,stem) pairs:", len(uniq))
    finite = sum(1 for e in m if isinstance(e.get('LUFS_original'), (int, float)) and isinstance(e.get('LUFS_rendered'), (int, float)))
    print("n_LUFS_finite:", finite)
elif isinstance(m, dict):
    print("keys:", list(m.keys()))
