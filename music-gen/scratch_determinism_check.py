"""Byte-determinism x 2 check: SHA the three key artifacts from run 1,
rerun in a fresh temp dir, SHA them from run 2, compare."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
KEY_ARTIFACTS = ("verdict.json", "leak_test_summary.json", "corn_head_v1.pt")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# Run-1 SHAs (from the just-completed run under data/ear_v1/).
run1 = {k: _sha(ROOT / "data" / "ear_v1" / k) for k in KEY_ARTIFACTS}

# Run-2: fresh temp dir, copy the necessary source + feature-cache inputs,
# re-run scripts.ear_v1.run_all, then SHA outputs.
scratch = Path(tempfile.mkdtemp(prefix="ear_v1_det2_"))
try:
    # Copy scripts, corpus, and pre-extracted per-song feature cache
    # (which is the c6 v0 cache — read-only).
    for sub in ["scripts", "corpus", "docs"]:
        shutil.copytree(ROOT / sub, scratch / sub, dirs_exist_ok=True)
    # Copy per-song feature cache from data/ear_v0/per_song_features/.
    dst_cache = scratch / "data" / "ear_v0" / "per_song_features"
    dst_cache.mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "data" / "ear_v0" / "per_song_features").glob("*.npy"):
        shutil.copy2(f, dst_cache / f.name)
    # Copy the frozen rubric_hash + diff manifest (both frozen at commit).
    dst_v1 = scratch / "data" / "ear_v1"
    dst_v1.mkdir(parents=True, exist_ok=True)
    for f in ["rubric_hash.txt", "leak_test_diff_manifest.json"]:
        shutil.copy2(ROOT / "data" / "ear_v1" / f, dst_v1 / f)

    env = os.environ.copy()
    env.update({
        "PYTHONPATH": str(scratch),
        "PYTHONHASHSEED": "0",
        "SOURCE_DATE_EPOCH": "1756800000",
        "TZ": "UTC",
        "LC_ALL": "C.UTF-8",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
    })
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "scripts.ear_v1.run_all"],
        cwd=str(scratch), env=env, capture_output=True, text=True, timeout=1200,
    )
    print("[run2 stdout tail]", r.stdout[-500:])
    if r.returncode != 0:
        print("[run2 stderr tail]", r.stderr[-2000:])
        sys.exit(f"run2 failed rc={r.returncode}")

    run2 = {k: _sha(scratch / "data" / "ear_v1" / k) for k in KEY_ARTIFACTS}

    result = {
        "artifacts": {
            k: {"run1": run1[k], "run2": run2[k], "equal": run1[k] == run2[k]}
            for k in KEY_ARTIFACTS
        },
        "all_equal": all(run1[k] == run2[k] for k in KEY_ARTIFACTS),
        "envelope": {
            "PYTHONHASHSEED": "0",
            "SOURCE_DATE_EPOCH": "1756800000",
            "TZ": "UTC", "LC_ALL": "C.UTF-8",
            "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "torch_manual_seed": 0, "torch_num_threads": 1,
        },
        "scratch_root_probe": str(scratch),
    }
    (ROOT / "data" / "ear_v1" / "determinism_check.json").write_text(
        json.dumps(result, indent=2, sort_keys=True)
    )
    print(json.dumps({k: v["equal"] for k, v in result["artifacts"].items()},
                     indent=2))
    print("all_equal:", result["all_equal"])
finally:
    shutil.rmtree(scratch, ignore_errors=True)
