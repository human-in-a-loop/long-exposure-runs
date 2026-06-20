#!/usr/bin/env python3
"""Quick probe to verify family attribution + per-family assertion counts.
Read-only against phytograph_dataset/.
"""
import pandas as pd, json, collections, sys

he = pd.read_parquet('phytograph_dataset/hyperedges.parquet')
n = pd.read_parquet('phytograph_dataset/nodes.parquet')

par = he[he['edge_type']=='taxonomic_parentage']
child2parent = {}
for c in par['canonical_node_ids_json']:
    a = json.loads(c) if isinstance(c, str) else c
    if len(a) == 2:
        child2parent[a[0]] = a[1]

fam_ids = set(n[n['node_type']=='family']['node_id'])
fam_label = dict(zip(n[n['node_type']=='family']['node_id'], n[n['node_type']=='family']['label']))

def find_family(k, max_hops=10):
    cur = k
    for _ in range(max_hops):
        if cur in fam_ids:
            return cur
        nxt = child2parent.get(cur)
        if nxt is None or nxt == cur:
            return None
        cur = nxt
    return None

resolved = he[(he['edge_type'].isin(['phytochemical_assertion','ethnobotanical_use_assertion'])) & (~he['pending_crosswalk'])].copy()
keys = set(resolved['accepted_taxon_key'].unique())
print('Resolved Track5 rows:', len(resolved))
print('Unique resolved taxa:', len(keys))
k2f = {k: find_family(k) for k in keys}
mapped = sum(1 for v in k2f.values() if v)
print('Mapped to family:', mapped)
resolved['family_id'] = resolved['accepted_taxon_key'].map(k2f)
resolved['family'] = resolved['family_id'].map(fam_label)

# Family x edge_type assertion counts
print('Family x edge_type counts (top 30 families):')
g = resolved.groupby(['family','edge_type']).size().unstack(fill_value=0)
g['total'] = g.sum(axis=1)
g = g.sort_values('total', ascending=False)
print(g.head(30))
print()
print('Family cells with >=100 assertions:')
cell = resolved.groupby(['family','edge_type']).size().reset_index(name='n')
cell_100 = cell[cell['n']>=100]
print(len(cell_100))
print(cell_100.head(20))
print()
print('per-source breakdown:')
print(resolved.groupby('source_id').size())
