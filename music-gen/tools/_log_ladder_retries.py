"""One-shot: log successful torchcrepe install retry rows to ladder."""
import json, pathlib, time
ladder = pathlib.Path('data/rc10_learned_survey/fetchability_ladder.jsonl')
rows = [
    {'family': 'bass_vocals_torchcrepe', 'rung': '1_retry_cpu_torch',
     'method': 'pip install --index-url pytorch cpu torch (as prereq)',
     'url': 'https://download.pytorch.org/whl/cpu',
     'http_status': '200',
     'sha256_if_success': None, 'failure_mode_if_fail': None, 'success': True,
     'note': 'cpu-only torch avoids 423MB nvidia_cublas wheel that timed out on default PyPI resolution',
     'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},
    {'family': 'bass_vocals_torchcrepe', 'rung': '1_retry',
     'method': 'pip install torchcrepe==0.0.24 soundfile librosa',
     'url': 'pypi:torchcrepe==0.0.24',
     'http_status': '200', 'sha256_if_success': None, 'failure_mode_if_fail': None,
     'success': True,
     'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},
    {'family': 'bass_vocals_torchcrepe', 'rung': 2,
     'method': 'import torchcrepe; weights bundled/downloaded on first call',
     'url': 'local:torchcrepe_weights_bundled',
     'http_status': 'n/a', 'sha256_if_success': None, 'failure_mode_if_fail': None,
     'success': True,
     'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},
]
with ladder.open('a') as f:
    for r in rows:
        f.write(json.dumps(r, sort_keys=True) + '\n')
print('logged', len(rows), 'rows')
