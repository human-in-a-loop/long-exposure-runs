#!/usr/bin/env python3
"""c8 Track 2: torch 2.13.0+cpu reproduction dry-run refresh.

Re-invokes the c7-landed, SHA-anchored probe module `torch213_reproduce_probe`
in Mode 1 dry-run. Verifies:
    - torch.__version__ == "2.13.0+cpu" via /usr/bin/python3 bare
    - torch.__file__   == "/usr/local/lib/python3.11/dist-packages/torch/__init__.py"
    - Drafted reproduction command byte-identical to c7 spec output
    - Venv (workspace/learned_transcribers_venv/) dir-manifest SHA byte-identical
      vs c7 snapshot (still torch 2.14.0+cpu; not activated by dry-run)
    - No network syscall attempted (AST re-verified by test suite)

Attribution verdict on success: ENV_DRIFT_PROBE_CANDIDATE_FOUND_C8_DRY_RUN_ROLL_FORWARD.
Any divergence → first-class finding (system torch changed, venv drifted, or
reproduction command spec broke). No tuning to make it match — FD-1.

Milestone: M-V3-SPINE-1/torch213-reproduce-probe-c8-completed.

Mode 2 execution deferred to operator green-light in live_guidance.
User prompt alone does NOT count per c7 lock.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"torch213_reproduce_probe_c8 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)
sys.path.insert(0, str(_REPO / "scripts"))

# c7 probe module — READ-ONLY import (SHA-anchored by tests).
from v3_spine import torch213_reproduce_probe as c7_probe  # noqa: E402

C7_JSON = _REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json"
OUT_JSON = _REPO / "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--execute", action="store_true",
        help="Mode 2 — only permitted with an operator directive in live_guidance.",
    )
    args = ap.parse_args()

    if args.execute:
        raise RuntimeError(
            "c8 Mode 2 execution requires operator directive in live_guidance; "
            "user prompt alone does NOT count per c7 lock."
        )

    if not C7_JSON.is_file():
        raise RuntimeError(f"c7 baseline probe missing: {C7_JSON}")
    c7_out = json.loads(C7_JSON.read_text())

    muscriptor_bin, model_path = c7_probe._resolve_muscriptor_paths()
    venv_pre = c7_probe._venv_signature()
    result = c7_probe.mode_dry_run(muscriptor_bin, model_path)
    venv_post = c7_probe._venv_signature()

    # Compare vs c7 baseline.
    check_torch_version = (
        result.get("torch_version_observed") == c7_out["torch_version_observed"]
        == "2.13.0+cpu"
    )
    check_torch_file = (
        result.get("torch_file_observed") == c7_out["torch_file_observed"]
        == "/usr/local/lib/python3.11/dist-packages/torch/__init__.py"
    )
    check_command_drafted = (
        result.get("command_string_drafted") == c7_out["command_string_drafted"]
    )
    venv_manifest_c7 = c7_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c8_pre = venv_pre.get("dir_manifest_sha256")
    venv_manifest_c8_post = venv_post.get("dir_manifest_sha256")
    check_venv_unchanged_vs_c7 = (
        venv_manifest_c8_pre == venv_manifest_c7 == venv_manifest_c8_post
    )

    all_checks_pass = (
        check_torch_version
        and check_torch_file
        and check_command_drafted
        and check_venv_unchanged_vs_c7
    )
    if all_checks_pass:
        attribution = "ENV_DRIFT_PROBE_CANDIDATE_FOUND_C8_DRY_RUN_ROLL_FORWARD"
        probe_status = "awaiting_operator_green_light"
    else:
        attribution = "ENV_DRIFT_PROBE_C8_DIVERGENCE_FIRST_CLASS_FINDING"
        probe_status = "divergence_from_c7_baseline"

    out = {
        "cycle": 8,
        "mode": "dry_run",
        "probe_status": probe_status,
        "attribution_verdict": attribution,
        "network_syscall_attempted": False,
        "torch_version_observed": result.get("torch_version_observed"),
        "torch_file_observed": result.get("torch_file_observed"),
        "command_string_drafted": result.get("command_string_drafted"),
        "command_string_drafted_module_form":
            result.get("command_string_drafted_module_form"),
        "stem_input_path": result.get("stem_input_path"),
        "stem_input_sha256": result.get("stem_input_sha256"),
        "c3_guitar_json_sha_anchor": result.get("c3_guitar_json_sha_anchor"),
        "c4_guitar_json_sha_anchor": result.get("c4_guitar_json_sha_anchor"),
        "venv_signature_pre": venv_pre,
        "venv_signature_post": venv_post,
        "venv_unchanged": venv_pre == venv_post,
        "checks_vs_c7_baseline": {
            "torch_version_matches": check_torch_version,
            "torch_file_matches": check_torch_file,
            "command_drafted_matches": check_command_drafted,
            "venv_manifest_matches_c7": check_venv_unchanged_vs_c7,
            "all_pass": all_checks_pass,
        },
        "c7_baseline_probe_sha256": _sha256(C7_JSON),
        "c7_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe.py"),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"attribution_verdict: {attribution}")


if __name__ == "__main__":
    main()
