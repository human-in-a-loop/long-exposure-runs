import json, hashlib, os
ap = json.load(open('data/rc10_impl/guitar_piano/anchor_preservation.json'))
print("top-level keys:", list(ap.keys()))
print("reported n_entries:", ap.get('n_entries'))
print("reported n_mismatch:", ap.get('n_mismatch'))
entries = None
for k in ('anchors', 'per_entry', 'entries', 'anchor_entries', 'anchor_shas'):
    if k in ap:
        entries = ap[k]
        print("found under", k)
        break
if entries is None:
    print("could not find entries; showing raw sample:")
    print(json.dumps(ap, indent=2)[:800])
else:
    if isinstance(entries, list):
        print("first entry:", entries[0] if entries else "empty")
        print("count:", len(entries))
    elif isinstance(entries, dict):
        first = next(iter(entries.items()))
        print("first key/val:", first)
        print("count:", len(entries))
