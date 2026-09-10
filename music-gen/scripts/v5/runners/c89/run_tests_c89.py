"""Run the adopted test suite under /usr/bin/python3 and write data/v5/logs/test_results_c89.json ({file: {rc, n_pass_lines, n_tests_defined, wall_s, tail}})."""
import json, os, re, subprocess, sys, time
from pathlib import Path
W = Path('/home/user/long-exposure-runs/music-gen'); os.chdir(W)
FILES = sys.argv[1:] or ["tests/test_c89_landing.py", "tests/test_c88_landing.py", "tests/test_c87_landing.py", "tests/test_c87_comping.py", "tests/test_c87_f3_gen.py", "tests/test_c86_landing.py",
                         "tests/test_c86_f4_close.py", "tests/test_c86_f2_models.py", "tests/test_c85_landing.py", "tests/test_c85_f4_m5.py", "tests/test_c84_landing.py"]
OUT = Path("data/v5/logs/test_results_c89.json")
res = json.loads(OUT.read_text()) if OUT.exists() else {}
env = dict(os.environ, PYTHONPATH=str(W))
for f in FILES:
    if not Path(f).exists():
        res[f] = {"rc": None, "n_pass_lines": 0, "n_tests_defined": 0, "wall_s": 0.0, "tail": "MISSING FILE"}
        print(f, "MISSING"); continue
    t0 = time.time()
    r = subprocess.run(["/usr/bin/python3", f], capture_output=True, text=True, env=env, timeout=1500)
    out = r.stdout + r.stderr
    n_pass = len(re.findall(r"^test_\d+ PASS", out, re.M))
    n_def = len(re.findall(r"^def test_\d+", Path(f).read_text(), re.M))
    res[f] = {"rc": r.returncode, "n_pass_lines": n_pass, "n_tests_defined": n_def, "wall_s": round(time.time() - t0, 1), "tail": out[-1500:],
              "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(f"{f}: rc={r.returncode} pass={n_pass}/{n_def} {round(time.time()-t0,1)}s", flush=True)
    if r.returncode != 0:
        print(out[-2500:], flush=True)
OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
print("TOTAL pass lines", sum(v["n_pass_lines"] for v in res.values()), "all rc0", all(v["rc"] == 0 for v in res.values()))
