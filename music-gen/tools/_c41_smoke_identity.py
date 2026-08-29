#!/usr/bin/env python3
import sys, json
sys.path.insert(0, '.')
import music21
from scripts.rules.extract import harmonic as c9h
from scripts.rules_harmonic_window_v2 import harmonic_wrapper as w
from scripts.rules.extract._common import FIXED_TS, event_id_for
from scripts.rules.rule_id import derive_rule_id

score = music21.converter.parse('data/score/merged_synth030s.musicxml')
c9_rows = c9h.extract(score)
raw_rows = w._raw_c9(score)

def finish(r):
    r = dict(r)
    r['event_type'] = 'rule'
    r['schema_v'] = 1
    r['ts'] = FIXED_TS
    r['extractor'] = c9h.EXTRACTOR
    r['extractor_version'] = c9h.EXTRACTOR_VERSION
    rid = derive_rule_id(r)
    r['rule_id'] = rid
    r['event_id'] = event_id_for(rid)
    return r

c9_ids = sorted(finish(r)['rule_id'] for r in c9_rows)
w_ids = sorted(finish(r)['rule_id'] for r in raw_rows)
print('c9 count', len(c9_ids), 'wrapper count', len(w_ids))
print('c9 raw = wrapper raw:', c9_ids == w_ids)

with open('data/rules/ledger.jsonl') as f:
    ledger_rows = [json.loads(l) for l in f if l.strip()]
h_ids = sorted(r['rule_id'] for r in ledger_rows if r.get('rule_type') == 'harmonic')
print('ledger harmonic count', len(h_ids))
in_ledger = [i for i in c9_ids if i in h_ids]
print('c9_synth_ids in ledger:', len(in_ledger), '/', len(c9_ids))
print('c9_ids:', c9_ids)
print('in_ledger:', in_ledger)
