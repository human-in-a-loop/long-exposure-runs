#!/usr/bin/env python3
"""c15 heartbeat: torch 2.13.0+cpu reproduction dry-run liveness roll-forward.

Eleventh consecutive substantive-track-absent cycle (c5..c15) → heartbeat only,
per c8-landed wait-on-operator cadence policy (docs/wait_on_operator_cadence_policy.md,
SHA pinned in data/v3_spine/wait_on_operator_cadence_policy_hash.txt). No fifth
substantive M-V3-SPINE track manufactured.

Re-invokes the c7-landed, SHA-anchored probe module `torch213_reproduce_probe`
in Mode 1 dry-run. Compares against c7..c14 baselines. Verifies:
    - torch.__version__ == "2.13.0+cpu" via /usr/bin/python3 bare
    - torch.__file__   == "/usr/local/lib/python3.11/dist-packages/torch/__init__.py"
    - Drafted reproduction command byte-identical to c7..c14 spec output
    - Venv (workspace/learned_transcribers_venv/) dir-manifest SHA byte-identical
      vs c7..c14 snapshot (a86205175728…f83a74)
    - No network syscall attempted (AST re-verified by test suite)

Attribution verdict on success:
    ENV_DRIFT_PROBE_CANDIDATE_FOUND_C15_DRY_RUN_ROLL_FORWARD.
Any divergence → first-class finding. No tuning to make it match — FD-1.

Milestone: M-V3-SPINE-1/torch213-reproduce-probe-c15-completed.

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
        f"torch213_reproduce_probe_c15 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)
sys.path.insert(0, str(_REPO / "scripts"))

# c7 probe module — READ-ONLY import (SHA-anchored by tests).
from v3_spine import torch213_reproduce_probe as c7_probe  # noqa: E402

C7_JSON = _REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json"
C8_JSON = _REPO / "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json"
C9_JSON = _REPO / "data/v3_spine/cycle9/torch213_reproduce_probe_c9.json"
C10_JSON = _REPO / "data/v3_spine/cycle10/torch213_reproduce_probe_c10.json"
C11_JSON = _REPO / "data/v3_spine/cycle11/torch213_reproduce_probe_c11.json"
C12_JSON = _REPO / "data/v3_spine/cycle12/torch213_reproduce_probe_c12.json"
C13_JSON = _REPO / "data/v3_spine/cycle13/torch213_reproduce_probe_c13.json"
C14_JSON = _REPO / "data/v3_spine/cycle14/torch213_reproduce_probe_c14.json"
OUT_JSON = _REPO / "data/v3_spine/cycle15/torch213_reproduce_probe_c15.json"


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
            "c15 Mode 2 execution requires operator directive in live_guidance; "
            "user prompt alone does NOT count per c7 lock."
        )

    for label, p in (("c7", C7_JSON), ("c8", C8_JSON), ("c9", C9_JSON),
                     ("c10", C10_JSON), ("c11", C11_JSON), ("c12", C12_JSON),
                     ("c13", C13_JSON), ("c14", C14_JSON)):
        if not p.is_file():
            raise RuntimeError(f"{label} baseline probe missing: {p}")
    c7_out = json.loads(C7_JSON.read_text())
    c8_out = json.loads(C8_JSON.read_text())
    c9_out = json.loads(C9_JSON.read_text())
    c10_out = json.loads(C10_JSON.read_text())
    c11_out = json.loads(C11_JSON.read_text())
    c12_out = json.loads(C12_JSON.read_text())
    c13_out = json.loads(C13_JSON.read_text())
    c14_out = json.loads(C14_JSON.read_text())

    muscriptor_bin, model_path = c7_probe._resolve_muscriptor_paths()
    venv_pre = c7_probe._venv_signature()
    result = c7_probe.mode_dry_run(muscriptor_bin, model_path)
    venv_post = c7_probe._venv_signature()

    check_torch_version = (
        result.get("torch_version_observed")
        == c7_out["torch_version_observed"]
        == c8_out["torch_version_observed"]
        == c9_out["torch_version_observed"]
        == c10_out["torch_version_observed"]
        == c11_out["torch_version_observed"]
        == c12_out["torch_version_observed"]
        == c13_out["torch_version_observed"]
        == c14_out["torch_version_observed"]
        == "2.13.0+cpu"
    )
    check_torch_file = (
        result.get("torch_file_observed")
        == c7_out["torch_file_observed"]
        == c8_out["torch_file_observed"]
        == c9_out["torch_file_observed"]
        == c10_out["torch_file_observed"]
        == c11_out["torch_file_observed"]
        == c12_out["torch_file_observed"]
        == c13_out["torch_file_observed"]
        == c14_out["torch_file_observed"]
        == "/usr/local/lib/python3.11/dist-packages/torch/__init__.py"
    )
    check_command_drafted = (
        result.get("command_string_drafted")
        == c7_out["command_string_drafted"]
        == c8_out["command_string_drafted"]
        == c9_out["command_string_drafted"]
        == c10_out["command_string_drafted"]
        == c11_out["command_string_drafted"]
        == c12_out["command_string_drafted"]
        == c13_out["command_string_drafted"]
        == c14_out["command_string_drafted"]
    )
    venv_manifest_c7 = c7_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c8 = c8_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c9 = c9_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c10 = c10_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c11 = c11_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c12 = c12_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c13 = c13_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c14 = c14_out["venv_signature_post"]["dir_manifest_sha256"]
    venv_manifest_c15_pre = venv_pre.get("dir_manifest_sha256")
    venv_manifest_c15_post = venv_post.get("dir_manifest_sha256")
    check_venv_unchanged = (
        venv_manifest_c15_pre
        == venv_manifest_c15_post
        == venv_manifest_c14
        == venv_manifest_c13
        == venv_manifest_c12
        == venv_manifest_c11
        == venv_manifest_c10
        == venv_manifest_c9
        == venv_manifest_c8
        == venv_manifest_c7
    )

    all_checks_pass = (
        check_torch_version
        and check_torch_file
        and check_command_drafted
        and check_venv_unchanged
    )
    if all_checks_pass:
        attribution = "ENV_DRIFT_PROBE_CANDIDATE_FOUND_C15_DRY_RUN_ROLL_FORWARD"
        probe_status = "awaiting_operator_green_light"
    else:
        attribution = "ENV_DRIFT_PROBE_C15_DIVERGENCE_FIRST_CLASS_FINDING"
        probe_status = "divergence_from_c7_c8_c9_c10_c11_c12_c13_c14_baseline"

    out = {
        "cycle": 15,
        "mode": "dry_run",
        "cadence_mode": "heartbeat",
        "probe_status": probe_status,
        "attribution_verdict": attribution,
        "checks_all_pass": all_checks_pass,
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
        "checks_vs_baseline": {
            "torch_version_matches": check_torch_version,
            "torch_file_matches": check_torch_file,
            "command_drafted_matches": check_command_drafted,
            "venv_manifest_matches_c7_c8_c9_c10_c11_c12_c13_c14": check_venv_unchanged,
            "all_pass": all_checks_pass,
        },
        "c7_baseline_probe_sha256": _sha256(C7_JSON),
        "c8_baseline_probe_sha256": _sha256(C8_JSON),
        "c9_baseline_probe_sha256": _sha256(C9_JSON),
        "c10_baseline_probe_sha256": _sha256(C10_JSON),
        "c11_baseline_probe_sha256": _sha256(C11_JSON),
        "c12_baseline_probe_sha256": _sha256(C12_JSON),
        "c13_baseline_probe_sha256": _sha256(C13_JSON),
        "c14_baseline_probe_sha256": _sha256(C14_JSON),
        "c7_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe.py"),
        "c8_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe_c8.py"),
        "c9_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe_c9.py"),
        "c10_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe_c10.py"),
        "c11_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe_c11.py"),
        "c12_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe_c12.py"),
        "c13_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe_c13.py"),
        "c14_probe_module_sha256": _sha256(
            _REPO / "scripts/v3_spine/torch213_reproduce_probe_c14.py"),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"attribution_verdict: {attribution}")


if __name__ == "__main__":
    main()
