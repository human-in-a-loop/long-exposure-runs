"""c89 smoke: AST parse, interpolate_v5 self-check, argparse guards, then the demo ONLY (--songs 0 --f5) into a tempdir with --prove-replay."""
import ast, json, os, subprocess, sys, tempfile, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W)
for f in ('scripts/v5/generate_v5.py', 'scripts/v5/interpolate_v5.py', 'scripts/v5/repo_root.py'):
    ast.parse(Path(f).read_text()); print('AST OK', f)
env = dict(os.environ, PYTHONPATH=str(W))
r = subprocess.run(['/usr/bin/python3', 'scripts/v5/interpolate_v5.py'], capture_output=True, text=True, env=env); print('selfcheck rc', r.returncode, r.stdout[-300:], r.stderr[-500:])
assert r.returncode == 0
r = subprocess.run(['/usr/bin/python3', 'scripts/v5/repo_root.py'], capture_output=True, text=True, env=env); print('repo_root', r.stdout.strip()); assert r.stdout.strip() == str(W)
G = ['/usr/bin/python3', 'scripts/v5/generate_v5.py']
for extra in (['--interp-a', 'CG', '--out', '/tmp/never'], ['--f5', '--interp-a', 'CG', '--interp-b', 'PD', '--interp-t', '0.5', '--out', '/tmp/never'],
              ['--f5', '--interp-a', 'CG', '--interp-b', 'PD', '--interp-t', '1.5', '--f5-prereg', 'data/v5/gen/f5_prereg_c89.json', '--form-plan', 'x', '--f2', '--f3', '--out', '/tmp/never']):
    r = subprocess.run(G + extra, capture_output=True, text=True, env=env)
    print('guard rc', r.returncode, r.stderr.strip().splitlines()[-1][:160])
    assert r.returncode == 2 and not Path('/tmp/never').exists()
r = subprocess.run(G + ['--help'], capture_output=True, text=True, env=env); assert r.returncode == 0 and '--f5' in r.stdout and '--interp-t' in r.stdout
td = tempfile.mkdtemp(prefix='gen_v5_smoke_f5_c89_')
cmd = json.loads(Path('data/v5/gen/f5_prereg_c89.json').read_text())['generator_flags']['iteration_5_command'].split()
cmd = [c for c in cmd]
cmd[cmd.index('--out') + 1] = td
cmd += ['--songs', '0', '--no-stall-update']
t0 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True, env=env)
print('smoke rc', r.returncode, round(time.time() - t0, 1), 's'); print(r.stdout[-2500:]); print(r.stderr[-2500:])
assert r.returncode == 0
roll = json.loads(Path(td, 'iteration_rollup.json').read_text())
print(json.dumps(roll['f5'], indent=1)[:3000])
d = Path(td) / 'gen_v5_interp_CG_PD_t050_donor_31a164f845f8e27e'
man = json.loads((d / 'ab_mix.manifest.json').read_text())
print('demo sha', man['ab_mix_sha256'], 'dur', man['ab_mix_duration_s'], 'bpm', man['tempo_bpm'], 'tonic', man['tonic'], man['tonic_source'])
print('raw', {k: v['raw_render_rms_dbfs'] for k, v in man['f5']['raw_render_rms_dbfs'].items()})
print('files', sum(1 for p in d.rglob('*') if p.is_file()), 'tempdir', td)
