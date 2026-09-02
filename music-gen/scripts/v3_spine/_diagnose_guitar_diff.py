"""Diagnose whether c3 vs c4 guitar JSON differs in ordering or in content."""
import hashlib
import json
import os
import subprocess
import tempfile


def canon(events):
    return json.dumps(events, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def sort_key(e):
    if e.get('type') == 'start':
        return ('start', e['index'])
    return ('end', e['start_event_index'])


def main():
    env = os.environ.copy()
    env.update({
        'PYTHONHASHSEED': '0', 'SOURCE_DATE_EPOCH': '1756463424',
        'TZ': 'UTC', 'LC_ALL': 'C.UTF-8',
        'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
    })
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'g.json')
        subprocess.run([
            'workspace/learned_transcribers_venv/bin/muscriptor', 'transcribe',
            'data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/guitar.wav',
            '--format', 'json', '--output', out,
            '--model', 'workspace/models/muscriptor-medium/model.safetensors',
            '--device', 'cpu', '--detect-tempo', 'best-effort',
            '--instruments', 'clean_electric_guitar,distorted_electric_guitar,acoustic_guitar',
        ], env=env, check=True, capture_output=True)
        ev_c4 = json.load(open(out))

    ev_c3 = json.load(open('data/v3_spine/31a164f845f8e27e/muscriptor/guitar.json'))
    print('c3 n_events:', len(ev_c3), 'c4 n_events:', len(ev_c4))
    c3_canon = canon(ev_c3)
    c4_canon = canon(ev_c4)
    print('c3 canonical sha:', hashlib.sha256(c3_canon.encode()).hexdigest()[:32])
    print('c4 canonical sha:', hashlib.sha256(c4_canon.encode()).hexdigest()[:32])
    c3_s = sorted(ev_c3, key=sort_key)
    c4_s = sorted(ev_c4, key=sort_key)
    print('sorted c3 canonical:', hashlib.sha256(canon(c3_s).encode()).hexdigest()[:32])
    print('sorted c4 canonical:', hashlib.sha256(canon(c4_s).encode()).hexdigest()[:32])
    print('sorted-events equal:', c3_s == c4_s)
    # Show first divergence in original list
    for i, (a, b) in enumerate(zip(ev_c3, ev_c4)):
        if a != b:
            print(f'first divergence at position {i}:')
            print('  c3:', a)
            print('  c4:', b)
            break
    else:
        print('(no divergence found in overlapping range)')

    if len(ev_c3) != len(ev_c4):
        print(f'lengths differ: c3={len(ev_c3)}, c4={len(ev_c4)}')

    # Count start events per instrument
    from collections import Counter
    c3_insts = Counter(e.get('instrument', '') for e in ev_c3 if e.get('type') == 'start')
    c4_insts = Counter(e.get('instrument', '') for e in ev_c4 if e.get('type') == 'start')
    print('c3 start counts by instrument:', dict(c3_insts))
    print('c4 start counts by instrument:', dict(c4_insts))


if __name__ == '__main__':
    main()
