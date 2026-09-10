"""c89 P3: copy the F5 demo trio (+ f5_blend.json + prereg copy) to data/v4/generated/f5_interp_CG_PD_t050_c89/ with a delivery manifest. Nothing else under data/v4/** is touched."""
import hashlib, json, os, shutil, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
src = Path('data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_31a164f845f8e27e')
dst = Path('data/v4/generated/f5_interp_CG_PD_t050_c89')
dst.mkdir(parents=True, exist_ok=True)
copied = {}
for name in ('ab_mix.wav', 'ab_mix.manifest.json', 'ab_mix.replay_proof.json', 'f5_blend.json', 'ear_score_v5.json'):
    if (src / name).exists():
        shutil.copyfile(src / name, dst / name)
        copied[name] = sha(dst / name)
shutil.copyfile('data/v5/gen/f5_prereg_c89.json', dst / 'f5_prereg_c89.json')
copied['f5_prereg_c89.json'] = sha(dst / 'f5_prereg_c89.json')
man = json.loads((src / 'ab_mix.manifest.json').read_text())
rec = {'schema_version': 1, 'cycle': 89, 'harness_cycle': 133, 'agent': 'worker', 'run_id': 'run-2026-09-06T000000Z', 'milestone': 'M-V5-GEN-1/F5-interpolation-demo',
       'source_dir': str(src), 'copied_sha256': copied, 'demo': {'donor_A': man['f5']['donor_A'], 'donor_B': man['f5']['donor_B'], 't': man['f5']['t'], 'ab_mix_sha256': man['ab_mix_sha256'],
       'duration_s': man['ab_mix_duration_s'], 'tempo_bpm': man['tempo_bpm'], 'tonic': man['tonic'], 'form': man['form_plan'], 'audibility_clauses': man['f5']['audibility']['clauses']},
       'replay_proof': json.loads((src / 'ab_mix.replay_proof.json').read_text())['verdict'], 'listening_note': 'FD-6: operator ear is the only listening authority; ear score informational',
       'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
(dst / 'delivery_manifest.json').write_text(json.dumps(rec, sort_keys=True, indent=2) + '\n')
print(json.dumps({'dest': str(dst), 'n_copied': len(copied), 'ab_mix': copied.get('ab_mix.wav', '')[:16]}))
