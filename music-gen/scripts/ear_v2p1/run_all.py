#!/usr/bin/python3
"""v2.1 orchestrator — pre-manifest → train × 2 → SB3 × 2 → verdict → post-manifest."""
# created: 2026-08-29T17:10:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2.1
from __future__ import annotations

import sys

print("[c47:run_all] starting", flush=True)
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
DATA_DIR = WS / "data/ear_v2p1"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ENV_PINS = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "PYTHONPATH": str(WS),
}


def _env() -> dict:
    e = os.environ.copy()
    e.update(ENV_PINS)
    return e


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    print(f"[run_all] $ {' '.join(cmd)} (cwd={cwd or WS})", flush=True)
    r = subprocess.run(cmd, cwd=cwd or WS, env=_env(), check=True,
                       capture_output=True, text=True)
    print(r.stdout, flush=True)
    if r.stderr:
        print("stderr:", r.stderr, file=sys.stderr, flush=True)
    return r


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    # 1. Pre-manifest snapshot.
    pre_path = DATA_DIR / "anchor_preservation_pre.json"
    _run(["/usr/bin/python3", "-m", "scripts.ear_v2p1.anchor_manifest_v2p1",
          "--out", str(pre_path), "--phase", "pre"])

    # 2. Training × 2 into fresh temp dirs, then copy stable output back to DATA_DIR.
    t1 = Path(tempfile.mkdtemp(prefix="ear_v2p1_train_1_"))
    t2 = Path(tempfile.mkdtemp(prefix="ear_v2p1_train_2_"))
    # We run training in-place (writes DATA_DIR) since it's deterministic;
    # then snapshot to t1. Then re-run training and snapshot to t2. Compare SHAs.
    _run(["/usr/bin/python3", "-m", "scripts.ear_v2p1.train_v2p1"])
    ch_1 = _sha(DATA_DIR / "corn_head_v2p1.pt")
    tr_1 = _sha(DATA_DIR / "training_result_v2p1.json")
    shutil.copy2(DATA_DIR / "corn_head_v2p1.pt", t1 / "corn_head_v2p1.pt")
    shutil.copy2(DATA_DIR / "training_result_v2p1.json",
                 t1 / "training_result_v2p1.json")

    _run(["/usr/bin/python3", "-m", "scripts.ear_v2p1.train_v2p1"])
    ch_2 = _sha(DATA_DIR / "corn_head_v2p1.pt")
    tr_2 = _sha(DATA_DIR / "training_result_v2p1.json")
    shutil.copy2(DATA_DIR / "corn_head_v2p1.pt", t2 / "corn_head_v2p1.pt")
    shutil.copy2(DATA_DIR / "training_result_v2p1.json",
                 t2 / "training_result_v2p1.json")

    train_det = {
        "corn_head_v2p1_run_1_sha256": ch_1,
        "corn_head_v2p1_run_2_sha256": ch_2,
        "corn_head_v2p1_byte_det_x2": ch_1 == ch_2,
        "training_result_v2p1_run_1_sha256": tr_1,
        "training_result_v2p1_run_2_sha256": tr_2,
        "training_result_v2p1_byte_det_x2": tr_1 == tr_2,
        "run_1_tmpdir": str(t1),
        "run_2_tmpdir": str(t2),
    }
    (DATA_DIR / "training_determinism_check.json").write_text(
        json.dumps(train_det, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(train_det, indent=2))

    # 3. SB3 × 2 into fresh temp dirs. Each subprocess CWDs into the temp dir.
    r1_dir = DATA_DIR / "sb3_50ctl_run_1"
    r2_dir = DATA_DIR / "sb3_50ctl_run_2"
    r1_dir.mkdir(parents=True, exist_ok=True)
    r2_dir.mkdir(parents=True, exist_ok=True)
    sb1_tmp = Path(tempfile.mkdtemp(prefix="ear_v2p1_sb3_run_1_"))
    sb2_tmp = Path(tempfile.mkdtemp(prefix="ear_v2p1_sb3_run_2_"))

    _run(["/usr/bin/python3", "-m", "scripts.ear_v2p1.sb3_50ctl_reverdict",
          "--out", str(sb1_tmp), "--run-id", "1"], cwd=WS)
    for f in ("sb3_50ctl_verdict_v2p1.json", "run_manifest.json"):
        shutil.copy2(sb1_tmp / f, r1_dir / f)

    _run(["/usr/bin/python3", "-m", "scripts.ear_v2p1.sb3_50ctl_reverdict",
          "--out", str(sb2_tmp), "--run-id", "2"], cwd=WS)
    for f in ("sb3_50ctl_verdict_v2p1.json", "run_manifest.json"):
        shutil.copy2(sb2_tmp / f, r2_dir / f)

    r1_sha = _sha(r1_dir / "sb3_50ctl_verdict_v2p1.json")
    r2_sha = _sha(r2_dir / "sb3_50ctl_verdict_v2p1.json")
    sb3_det = {
        "sb3_50ctl_verdict_v2p1_run_1_sha256": r1_sha,
        "sb3_50ctl_verdict_v2p1_run_2_sha256": r2_sha,
        "byte_determinism_x2": r1_sha == r2_sha,
        "run_1_tmpdir": str(sb1_tmp),
        "run_2_tmpdir": str(sb2_tmp),
    }
    (DATA_DIR / "sb3_determinism_check.json").write_text(
        json.dumps(sb3_det, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(sb3_det, indent=2))

    # 4. Emit verdict.
    _run(["/usr/bin/python3", "-m", "scripts.ear_v2p1.emit_verdict",
          "--run1", str(r1_dir), "--run2", str(r2_dir)])

    # 5. Post-manifest snapshot + drift check.
    post_path = DATA_DIR / "anchor_preservation_v2p1.json"
    _run(["/usr/bin/python3", "-m", "scripts.ear_v2p1.anchor_manifest_v2p1",
          "--out", str(post_path), "--phase", "final",
          "--pre-manifest", str(pre_path)])

    print("[run_all] complete.", flush=True)


if __name__ == "__main__":
    main()
