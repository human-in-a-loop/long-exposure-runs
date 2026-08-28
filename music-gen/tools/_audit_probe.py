import json
p = '/home/user/music-gen-instance/fork-3fbd8c1ab57c/clone-1/promise_ledger.jsonl'
with open(p) as f:
    events = [json.loads(l) for l in f]
term = events[-2]
print('Terminal event artifacts:')
for a in term.get('artifacts', []):
    print(' ', a)
print()
print('Terminal narrative:')
print(term.get('narrative', '')[:1200])
