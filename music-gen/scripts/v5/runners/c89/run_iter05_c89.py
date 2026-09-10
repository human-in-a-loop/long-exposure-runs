"""c89 iteration-5 pipeline (run detached): generate (F2 + F3 + F5 demo, replay x2, --cycle 89) -> independent second process x2 ->
flag-off iteration-4 regression -> score x2 -> listening copies (keep-top 6) -> demo delivery -> figure -> byte-det assembly."""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W)
S = Path(__file__).resolve().parent
LOG = Path('data/v5/logs')
MS = 'M-V5-GEN-1/F5-interpolation-demo'
ENV = dict(os.environ, PYTHONPATH=str(W))
def run(cmd, log):
    t0 = time.time()
    with open(log, 'w') as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True, env=ENV)
    print(f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] rc={r.returncode} {round(time.time()-t0,1)}s {' '.join(cmd)[:160]} -> {log}", flush=True)
    if r.returncode != 0:
        print(Path(log).read_text()[-3000:], flush=True)
        sys.exit(r.returncode)
cmd = json.loads(Path('data/v5/gen/f5_prereg_c89.json').read_text())['generator_flags']['iteration_5_command'].split()
run(cmd, LOG / 'generate_v5_iter05_c89.log')
print(Path(LOG / 'generate_v5_iter05_c89.log').read_text()[-3500:], flush=True)
run(['/usr/bin/python3', str(S / 'indep_c89.py')], LOG / 'indep_c89.log')
print(Path(LOG / 'indep_c89.log').read_text()[-800:], flush=True)
run(['/usr/bin/python3', str(S / 'flagoff_c89.py')], LOG / 'flagoff_c89.log')
print(Path(LOG / 'flagoff_c89.log').read_text()[-800:], flush=True)
run(['/usr/bin/python3', 'scripts/v5/score_gen_batch_v5.py', '--renders-glob', 'data/v5/gen/iteration_05/*/ab_mix.wav', '--cycle', '89',
     '--milestone', MS, '--table-out', 'data/v5/gen/gen_v5_iter05_ear_scores_c89.json'], LOG / 'score_gen_v5_iter05_c89_run1.log')
td = tempfile.mkdtemp(prefix='score_iter05_c89_run2_')
run(['/usr/bin/python3', 'scripts/v5/score_gen_batch_v5.py', '--renders-glob', 'data/v5/gen/iteration_05/*/ab_mix.wav', '--cycle', '89',
     '--milestone', MS, '--table-out', f'{td}/table.json', '--no-siblings'], LOG / 'score_gen_v5_iter05_c89_run2.log')
run(['/usr/bin/python3', 'scripts/v5/deliver_v5_listening.py', '--iteration', '5', '--cycle', '89', '--milestone', MS, '--keep-top', '6',
     '--scores', 'data/v5/gen/gen_v5_iter05_ear_scores_c89.json'], LOG / 'deliver_v5_iter05_c89.log')
run(['/usr/bin/python3', str(S / 'deliver_f5_demo_c89.py')], LOG / 'deliver_f5_demo_c89.log')
run(['/usr/bin/python3', 'data/v5/gen/plot_iter05_parts_c89.py', '--out', 'data/v5/gen/fig_iter05_parts_c89.png'], LOG / 'plot_iter05_parts_c89.log')
run(['/usr/bin/python3', str(S / 'bytedet_c89.py')], LOG / 'bytedet_c89.log')
print(Path(LOG / 'bytedet_c89.log').read_text()[-1500:], flush=True)
print('PIPELINE_DONE', flush=True)
