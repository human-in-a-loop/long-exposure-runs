"""c89 flag-off regression under the POST-EDIT generator image: the iteration-4 command (seed 3, --f2 --f3 --tempo-overrides, NO --f5;
--prove-replay omitted — result-neutral) must reproduce the 5 iteration-4 ab_mix.wav SHAs. Writes flagoff_c89.json next to this script."""
import hashlib, json, os, subprocess, tempfile, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W)
S = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
cmd4 = json.loads(Path('data/v5/gen/f3_prereg_c88.json').read_text())['generator_flags']['iteration_4_command'].split()
td = tempfile.mkdtemp(prefix='gen_v5_flagoff_c89_iteration_04_')
cmd = [c for c in cmd4 if c != '--prove-replay']
cmd[cmd.index('--out') + 1] = td
cmd += ['--no-stall-update']
assert '--f5' not in cmd
t0 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=str(W)))
assert r.returncode == 0, r.stderr[-2000:]
anchors = {f"{s['generated_song_id']}_donor_{s['donor']}": s['ab_mix_sha256'] for s in json.loads(Path('data/v5/gen/iteration_04/iteration_rollup.json').read_text())['songs']}
per = {}
for k, a in anchors.items():
    s = sha(Path(td, k, 'ab_mix.wav'))
    per[k] = {'recorded_sha256': a, 'flag_off_sha256': s, 'equal': s == a, 'on_disk_now_sha256': sha(f'data/v5/gen/iteration_04/{k}/ab_mix.wav')}
run = {'command': ' '.join(cmd), 'tempdir': td, 'wall_s': round(time.time() - t0, 1), 'per_song': per, 'n_equal': sum(v['equal'] for v in per.values()), 'all_equal': all(v['equal'] for v in per.values())}
out = {'checked_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'generate_v5_sha256': sha('scripts/v5/generate_v5.py'), 'runs': {'iteration_04': run}}
(S / 'flagoff_c89.json').write_text(json.dumps(out, indent=1) + '\n')
print(f"iteration_04 flag-off: {run['n_equal']}/5 equal ({run['wall_s']} s)")
