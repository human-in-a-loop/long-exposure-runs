#!/usr/bin/env python3
import json
d = json.load(open('data/gen/batch_v6/collision_analysis.json'))
for k in ['coerced','raw']:
    sub = d[k]
    if isinstance(sub, dict):
        print('---'+k+'---')
        for kk,v in sub.items():
            if isinstance(v,(int,float,str)):
                print(f'  {kk}: {v}')
            elif isinstance(v,dict):
                print(f'  {kk}: {v}')
            else:
                print(f'  {kk}: <list len={len(v)}>')
