"""c89 independent second process: the exact iteration-5 command into a fresh tempfile.mkdtemp() (no --prove-replay, --no-stall-update);
compares ab_mix + all per-stem MIDI SHAs of all 6 renders with the on-disk iteration_05. Writes indep_c89.json next to this script."""
import hashlib, json, os, subprocess, tempfile, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W)
S = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
cmd5 = json.loads(Path('data/v5/gen/f5_prereg_c89.json').read_text())['generator_flags']['iteration_5_command'].split()
td = tempfile.mkdtemp(prefix='gen_v5_indep_c89_iteration_05_')
cmd = [c for c in cmd5 if c != '--prove-replay']
cmd[cmd.index('--out') + 1] = td
cmd += ['--no-stall-update']
t0 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=str(W)))
assert r.returncode == 0, r.stderr[-2000:]
roll = json.loads(Path('data/v5/gen/iteration_05/iteration_rollup.json').read_text())
per = {}
for s in roll['songs']:
    k = f"{s['generated_song_id']}_donor_{s['donor']}"
    m1 = json.loads(Path(f'data/v5/gen/iteration_05/{k}/ab_mix.manifest.json').read_text())
    m2 = json.loads(Path(td, k, 'ab_mix.manifest.json').read_text())
    per[k] = {'on_disk_sha256': sha(f'data/v5/gen/iteration_05/{k}/ab_mix.wav'), 'independent_sha256': sha(Path(td, k, 'ab_mix.wav')),
              'midi_equal': m1['midi_sha256'] == m2['midi_sha256'], 'per_track_equal': m1['per_track_wav_sha256'] == m2['per_track_wav_sha256'], 'is_demo': 'f5' in s}
    per[k]['equal'] = per[k]['on_disk_sha256'] == per[k]['independent_sha256'] and per[k]['midi_equal'] and per[k]['per_track_equal']
    if 'f5' in s:
        per[k]['f5_blend_json_equal'] = sha(f'data/v5/gen/iteration_05/{k}/f5_blend.json') == sha(Path(td, k, 'f5_blend.json'))
        per[k]['equal'] = per[k]['equal'] and per[k]['f5_blend_json_equal']
out = {'checked_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'generate_v5_sha256': sha('scripts/v5/generate_v5.py'), 'command': ' '.join(cmd), 'tempdir': td,
       'wall_s': round(time.time() - t0, 1), 'per_song': per, 'n_equal': sum(v['equal'] for v in per.values()), 'n_songs': len(per), 'all_equal': all(v['equal'] for v in per.values())}
(S / 'indep_c89.json').write_text(json.dumps(out, indent=1) + '\n')
print(f"independent process: {out['n_equal']}/{out['n_songs']} equal ({out['wall_s']} s)")
