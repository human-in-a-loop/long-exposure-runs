"""Detached launch of the c89 iteration-5 pipeline; pins PID + log + post-edit SHAs in data/v5/logs/gen_iter05_c89.launch.json; prunes the smoke tempdir."""
import ast, glob, hashlib, json, os, shutil, sys, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W); sys.path.insert(0, str(W))
from scripts.v3_spine.launch_detached import launch_detached
S = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ast.parse(Path('scripts/v5/generate_v5.py').read_text())
assert not Path('data/v5/gen/iteration_05').exists(), 'iteration_05 already exists'
for d in glob.glob('/tmp/gen_v5_smoke_f5_c89_*'):
    shutil.rmtree(d, ignore_errors=True)
prereg = json.loads(Path('data/v5/gen/f5_prereg_c89.json').read_text())
log = Path('data/v5/logs/gen_iter05_c89.log')
pid = launch_detached(['/usr/bin/python3', str(S / 'run_iter05_c89.py')], log, W)
rec = {'pid': pid, 'log': str(log), 'launched_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'cycle': 89, 'harness_cycle': 133, 'agent': 'worker',
       'pipeline_script': str(S / 'run_iter05_c89.py'), 'generate_command': prereg['generator_flags']['iteration_5_command'],
       'generate_v5_sha256_post_edit': sha('scripts/v5/generate_v5.py'), 'generate_v5_sha256_pre_edit': prereg['generator_pre_edit_sha256'],
       'interpolate_v5_sha256': sha('scripts/v5/interpolate_v5.py'), 'repo_root_sha256': sha('scripts/v5/repo_root.py'),
       'f5_prereg_sha256': sha('data/v5/gen/f5_prereg_c89.json'), 'comping_gen_v5_sha256': sha('scripts/v5/comping_gen_v5.py'),
       'midi_from_json_events_v5_sha256': sha('scripts/v5/midi_from_json_events_v5.py'), 'harmony_n23_sha256': sha('data/v5/rules/harmony_markov_v5_full_c86.json'),
       'groove_n23_sha256': sha('data/v5/rules/groove_v5_v2_full_c86.json'), 'tempo_overrides_sha256': sha('data/v5/corpus/tempo_overrides_c86.json'),
       'form_plan_sha256': sha('data/v5/rules/form_plan_v5.json'),
       'smoke': {'demo_only_render_wall_s': 79.2, 'replay': 'REPLAY_PROOF_HOLDS', 'audibility_clauses': 'i/ii/iii all True', 'tempdir_pruned': True,
                 'note': 'smoke ran with the t500 id slip (fixed before this launch: t*100 -> t050 per the prereg); demo sha under the slip 5f22c2f57c66… not an anchor'}}
Path('data/v5/logs/gen_iter05_c89.launch.json').write_text(json.dumps(rec, indent=1) + '\n')
print(json.dumps(rec))
