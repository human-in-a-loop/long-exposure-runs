import os, json
harness_boundary = ['periodic-sweep', 'merge-integration', 'harness-auto-write', 'unknown']
in_turn_capable = ['worker-turn', 'auditor-turn', 'researcher-turn']
observed = {
    'periodic-sweep': 105,
    'merge-integration': 36,
    'worker-turn': 9,
    'auditor-turn': 0,
    'researcher-turn': 0,
    'harness-auto-write': 0,
    'unknown': 94,
}
total = sum(observed.values())
hb = sum(observed[k] for k in harness_boundary)
it = sum(observed[k] for k in in_turn_capable)
print('Total:', total, '(claim=244)')
print('Harness-boundary bucket sum:', hb)
print('In-turn-capable bucket sum:', it)
all_assigned = set(harness_boundary) | set(in_turn_capable)
observed_keys = set(observed.keys())
missing_from_partition = observed_keys - all_assigned
extra_in_partition = all_assigned - observed_keys
print('Partition covers all observed classes:', missing_from_partition == set())
print('Missing (observed but unpartitioned):', missing_from_partition)
print('Partition classes not observed:', extra_in_partition)
p1 = 'data/pre_reg_policy_verify/commit_classification.tsv'
p2 = 'data/pre_reg_policy_verify/verdict.json'
print('TSV exists:', os.path.exists(p1))
print('Verdict exists:', os.path.exists(p2))
if os.path.exists(p2):
    with open(p2) as f:
        v = json.load(f)
    print('verdict:', v.get('verdict'))
    print('keys:', list(v.keys())[:20])
