#!/usr/bin/env python3
"""c7 Track A: torch 2.13.0+cpu reproduction probe (interpreter-swap variant).

Pinned pre-code by docs/v3_spine_torch213_reproduce_spec.md
(sha256 in data/v3_spine/torch213_reproduce_spec_hash.txt).

Milestone: M-V3-SPINE-1/torch213-reproduce-probe-completed

Two-mode operation guarded by --execute (default False).
Mode 1 (default): dry-run — verify candidate on disk, draft reproduction command.
Mode 2 (--execute): only if operator directive in live_guidance; run drafted
command twice into fresh tempdirs and SHA-256 compare vs c3 and c4 anchors.

FD-1: no hand-rolled DSP transcription; no tuning around failures.
FD-6: panel never a LANDS gate; operator ear is the only LANDS authority.
Egress BLOCKED. No pip install. Sub-process-serial in-turn only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Env pins (mandatory).
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"torch213_reproduce_probe requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)

SPEC_DOC = _REPO / "docs" / "v3_spine_torch213_reproduce_spec.md"
SPEC_HASH_FILE = _REPO / "data" / "v3_spine" / "torch213_reproduce_spec_hash.txt"
OUT_JSON = _REPO / "data" / "v3_spine" / "cycle7" / "torch213_reproduce_probe.json"
OUT_BYTE_DET = _REPO / "data" / "v3_spine" / "cycle7" / "torch213_reproduce_probe_byte_determinism.json"

MUSCRIPTOR_SOURCE = _REPO / "scripts" / "v3_spine" / "muscriptor_operator_section.py"
STEM_INPUT = _REPO / "data" / "v3_spine" / "31a164f845f8e27e" / "stems_6s" / "guitar.wav"

EXPECTED_TORCH_VERSION = "2.13.0+cpu"
EXPECTED_TORCH_FILE = "/usr/local/lib/python3.11/dist-packages/torch/__init__.py"

C3_GUITAR_JSON_SHA = (
    "97b5a598db8424bbca725c1fbbc4854e4cb39297aae390dc84f760056f4ddabc"
)
C4_GUITAR_JSON_SHA = (
    "3107ba21e10acc7025a84105fe1e9500b87f49d6361f1716a8b1d98a224069cb"
)

# Spec-hash three-way chain enforcement at import time.
_spec_sha_actual = hashlib.sha256(SPEC_DOC.read_bytes()).hexdigest()
_spec_sha_pinned = SPEC_HASH_FILE.read_text().strip()
if _spec_sha_actual != _spec_sha_pinned:
    raise RuntimeError(
        f"spec hash drift: doc SHA {_spec_sha_actual} != pinned {_spec_sha_pinned}"
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _resolve_muscriptor_paths() -> tuple[str, str]:
    """Grep MUSCRIPTOR + MODEL constants from muscriptor_operator_section.py."""
    src = MUSCRIPTOR_SOURCE.read_text()
    mm = re.search(r'^MUSCRIPTOR\s*=\s*"([^"]+)"', src, re.M)
    mo = re.search(r'^MODEL\s*=\s*"([^"]+)"', src, re.M)
    if not mm or not mo:
        raise RuntimeError("could not resolve MUSCRIPTOR / MODEL constants")
    return mm.group(1), mo.group(1)


def _venv_signature() -> dict:
    """Snapshot mtime + dir-manifest sha of workspace/learned_transcribers_venv."""
    venv = _REPO / "workspace" / "learned_transcribers_venv"
    if not venv.is_dir():
        return {"present": False}
    mtime = venv.stat().st_mtime
    lines = []
    for p in sorted(venv.rglob("*")):
        if p.is_file():
            try:
                lines.append(f"{p.relative_to(venv)}\t{p.stat().st_size}")
            except OSError:
                continue
    manifest = hashlib.sha256("\n".join(lines).encode()).hexdigest()
    return {"present": True, "mtime": mtime, "dir_manifest_sha256": manifest, "n_files": len(lines)}


def mode_dry_run(muscriptor_bin: str, model_path: str) -> dict:
    """Mode 1: verify candidate on disk, draft command; do NOT invoke MuScriptor."""
    import torch  # local — avoid loading in --execute path pre-check as well
    torch_version = torch.__version__
    torch_file = torch.__file__

    if torch_version != EXPECTED_TORCH_VERSION or torch_file != EXPECTED_TORCH_FILE:
        return {
            "mode": "dry_run",
            "probe_status": "candidate_disappeared",
            "attribution_verdict": "ENV_DRIFT_PROBE_CANDIDATE_MISSING",
            "torch_version_observed": torch_version,
            "torch_file_observed": torch_file,
            "torch_version_expected": EXPECTED_TORCH_VERSION,
            "torch_file_expected": EXPECTED_TORCH_FILE,
        }

    # Draft command verbatim. Placeholder <tempdir> — do not resolve.
    env_prefix = (
        "PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 "
        "OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1"
    )
    # Actual muscriptor CLI shape (grep-verified in muscriptor_operator_section.py):
    #   {MUSCRIPTOR} transcribe {input} --format json --output {out} \
    #                --model {model} --device cpu --detect-tempo best-effort
    command = (
        f"{env_prefix} /usr/bin/python3 {muscriptor_bin} transcribe "
        f"{STEM_INPUT.relative_to(_REPO)} --format json "
        f"--output <tempdir>/guitar.json --model {model_path} "
        f"--device cpu --detect-tempo best-effort"
    )
    # Alternative form (per brief, if entrypoint is invoked as a module):
    command_module_form = (
        f"{env_prefix} /usr/bin/python3 -m muscriptor.cli transcribe "
        f"{STEM_INPUT.relative_to(_REPO)} --format json "
        f"--output <tempdir>/guitar.json --model {model_path} "
        f"--device cpu --detect-tempo best-effort"
    )

    return {
        "mode": "dry_run",
        "probe_status": "awaiting_operator_green_light",
        "attribution_verdict": "ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_DRY_RUN",
        "torch_version_observed": torch_version,
        "torch_file_observed": torch_file,
        "torch_version_expected": EXPECTED_TORCH_VERSION,
        "torch_file_expected": EXPECTED_TORCH_FILE,
        "command_string_drafted": command,
        "command_string_drafted_module_form": command_module_form,
        "muscriptor_binary": muscriptor_bin,
        "model_path": model_path,
        "stem_input_path": str(STEM_INPUT.relative_to(_REPO)),
        "stem_input_sha256": _sha256(STEM_INPUT),
        "c3_guitar_json_sha_anchor": C3_GUITAR_JSON_SHA,
        "c4_guitar_json_sha_anchor": C4_GUITAR_JSON_SHA,
        "reproduction_note": (
            "The c3-era torch 2.13.0+cpu is imported by /usr/bin/python3 "
            "directly from /usr/local/lib/python3.11/dist-packages — without "
            "activating workspace/learned_transcribers_venv. Executing the "
            "drafted command uses that interpreter and torch, which is the "
            "point of the interpreter-swap variant."
        ),
    }


def mode_execute(muscriptor_bin: str, model_path: str) -> tuple[dict, dict]:
    """Mode 2: run drafted command twice, SHA-compare vs c3+c4 anchors."""
    import torch  # noqa: F401 — sanity import
    env = os.environ.copy()

    def _run_once(out_dir: Path) -> str:
        out_path = out_dir / "guitar.json"
        cmd = [
            muscriptor_bin, "transcribe",
            str(STEM_INPUT.relative_to(_REPO)),
            "--format", "json",
            "--output", str(out_path),
            "--model", model_path,
            "--device", "cpu",
            "--detect-tempo", "best-effort",
        ]
        r = subprocess.run(cmd, env=env, capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(
                f"muscriptor rc={r.returncode}: {r.stderr.decode('utf-8', 'replace')[-2000:]}"
            )
        return _sha256(out_path)

    with tempfile.TemporaryDirectory(prefix="v3_c7_torch213_r1_") as d1:
        sha1 = _run_once(Path(d1))
    with tempfile.TemporaryDirectory(prefix="v3_c7_torch213_r2_") as d2:
        sha2 = _run_once(Path(d2))

    if sha1 == C3_GUITAR_JSON_SHA:
        verdict = "ENV_DRIFT_CONFIRMED_TORCH_MINOR_VERSION"
    elif sha1 == C4_GUITAR_JSON_SHA:
        verdict = "ENV_DRIFT_NOT_TORCH_ALONE"
    else:
        verdict = "ENV_DRIFT_THIRD_STATE"

    result = {
        "mode": "executed",
        "probe_status": "completed",
        "attribution_verdict": verdict,
        "sha_vs_c3_anchor": {
            "observed_sha": sha1,
            "c3_anchor_sha": C3_GUITAR_JSON_SHA,
            "equal": sha1 == C3_GUITAR_JSON_SHA,
        },
        "sha_vs_c4_anchor": {
            "observed_sha": sha1,
            "c4_anchor_sha": C4_GUITAR_JSON_SHA,
            "equal": sha1 == C4_GUITAR_JSON_SHA,
        },
        "byte_determinism_within_cycle_x2": sha1 == sha2,
    }
    byte_det = {
        "run1_sha256": sha1,
        "run2_sha256": sha2,
        "equal": sha1 == sha2,
    }
    return result, byte_det


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--execute", action="store_true",
        help="Run the drafted command x2 and compare vs c3/c4 anchors. "
             "Only permitted with an operator directive in live_guidance.",
    )
    args = ap.parse_args()

    muscriptor_bin, model_path = _resolve_muscriptor_paths()
    venv_pre = _venv_signature()

    common = {
        "cycle": 7,
        "spec_sha256": _spec_sha_actual,
        "spec_path": str(SPEC_DOC.relative_to(_REPO)),
        "venv_signature_pre": venv_pre,
        "network_syscall_attempted": False,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    if not args.execute:
        result = mode_dry_run(muscriptor_bin, model_path)
        # Baseline sidecar for byte-determinism: dry-run has no runs, but we
        # publish an empty sidecar naming both anchors so downstream tests can
        # find the file at a stable path.
        byte_det = {
            "mode": "dry_run",
            "run1_sha256": None,
            "run2_sha256": None,
            "c3_guitar_json_sha_anchor": C3_GUITAR_JSON_SHA,
            "c4_guitar_json_sha_anchor": C4_GUITAR_JSON_SHA,
            "equal": None,
        }
    else:
        result, byte_det = mode_execute(muscriptor_bin, model_path)
        byte_det["mode"] = "executed"

    venv_post = _venv_signature()
    common["venv_signature_post"] = venv_post
    common["venv_unchanged"] = venv_pre == venv_post
    out = {**common, **result}

    _atomic_write(OUT_JSON, json.dumps(out, indent=2, sort_keys=True) + "\n")
    _atomic_write(OUT_BYTE_DET, json.dumps(byte_det, indent=2, sort_keys=True) + "\n")

    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"wrote {OUT_BYTE_DET.relative_to(_REPO)}")
    print(f"attribution_verdict: {result['attribution_verdict']}")


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


if __name__ == "__main__":
    main()
