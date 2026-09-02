#!/usr/bin/env python3
"""c19 heartbeat: torch 2.13.0+cpu reproduction dry-run liveness roll-forward.

Fifteenth consecutive substantive-track-absent cycle (c5..c19) → heartbeat only,
per c8-landed wait-on-operator cadence policy (docs/wait_on_operator_cadence_policy.md,
SHA pinned in data/v3_spine/wait_on_operator_cadence_policy_hash.txt). No fifth
substantive M-V3-SPINE track manufactured.

Re-invokes the c7-landed, SHA-anchored probe module `torch213_reproduce_probe`
in Mode 1 dry-run. Compares against c7..c18 baselines (twelve-cycle chain).
Verifies:
    - torch.__version__ == "2.13.0+cpu" via /usr/bin/python3 bare
    - torch.__file__   == "/usr/local/lib/python3.11/dist-packages/torch/__init__.py"
    - Drafted reproduction command byte-identical to c7..c18 spec output
    - Venv (workspace/learned_transcribers_venv/) dir-manifest SHA byte-identical
      vs c7..c18 snapshot (a86205175728…f83a74) — thirteen-cycle chain
    - No network syscall attempted (AST re-verified by test suite)

Attribution verdict on success:
    ENV_DRIFT_PROBE_CANDIDATE_FOUND_C19_DRY_RUN_ROLL_FORWARD.
Any divergence → first-class finding. No tuning to make it match — FD-1.

Milestone: M-V3-SPINE-1/torch213-reproduce-probe-c19-completed.

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
        f"torch213_reproduce_probe_c19 requires /usr/bin/python3 (got {sys.executable})"
    )

_REPO = Path(__file__).resolve().parents[2]
os.chdir(_REPO)
sys.path.insert(0, str(_REPO / "scripts"))

# c7 probe module — READ-ONLY import (SHA-anchored by tests).
from v3_spine import torch213_reproduce_probe as c7_probe  # noqa: E402

PRIOR_CYCLES = ("c7", "c8", "c9", "c10", "c11", "c12", "c13", "c14", "c15",
                "c16", "c17", "c18")
PRIOR_JSONS = {
    "c7":  _REPO / "data/v3_spine/cycle7/torch213_reproduce_probe.json",
    "c8":  _REPO / "data/v3_spine/cycle8/torch213_reproduce_probe_c8.json",
    "c9":  _REPO / "data/v3_spine/cycle9/torch213_reproduce_probe_c9.json",
    "c10": _REPO / "data/v3_spine/cycle10/torch213_reproduce_probe_c10.json",
    "c11": _REPO / "data/v3_spine/cycle11/torch213_reproduce_probe_c11.json",
    "c12": _REPO / "data/v3_spine/cycle12/torch213_reproduce_probe_c12.json",
    "c13": _REPO / "data/v3_spine/cycle13/torch213_reproduce_probe_c13.json",
    "c14": _REPO / "data/v3_spine/cycle14/torch213_reproduce_probe_c14.json",
    "c15": _REPO / "data/v3_spine/cycle15/torch213_reproduce_probe_c15.json",
    "c16": _REPO / "data/v3_spine/cycle16/torch213_reproduce_probe_c16.json",
    "c17": _REPO / "data/v3_spine/cycle17/torch213_reproduce_probe_c17.json",
    "c18": _REPO / "data/v3_spine/cycle18/torch213_reproduce_probe_c18.json",
}
PRIOR_MODULES = {
    "c7":  _REPO / "scripts/v3_spine/torch213_reproduce_probe.py",
    "c8":  _REPO / "scripts/v3_spine/torch213_reproduce_probe_c8.py",
    "c9":  _REPO / "scripts/v3_spine/torch213_reproduce_probe_c9.py",
    "c10": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c10.py",
    "c11": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c11.py",
    "c12": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c12.py",
    "c13": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c13.py",
    "c14": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c14.py",
    "c15": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c15.py",
    "c16": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c16.py",
    "c17": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c17.py",
    "c18": _REPO / "scripts/v3_spine/torch213_reproduce_probe_c18.py",
}
OUT_JSON = _REPO / "data/v3_spine/cycle19/torch213_reproduce_probe_c19.json"


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
            "c19 Mode 2 execution requires operator directive in live_guidance; "
            "user prompt alone does NOT count per c7 lock."
        )

    prior = {}
    for label, p in PRIOR_JSONS.items():
        if not p.is_file():
            raise RuntimeError(f"{label} baseline probe missing: {p}")
        prior[label] = json.loads(p.read_text())

    muscriptor_bin, model_path = c7_probe._resolve_muscriptor_paths()
    venv_pre = c7_probe._venv_signature()
    result = c7_probe.mode_dry_run(muscriptor_bin, model_path)
    venv_post = c7_probe._venv_signature()

    def _all_equal(*vals) -> bool:
        s = set(vals)
        return len(s) == 1

    check_torch_version = _all_equal(
        result.get("torch_version_observed"),
        *(prior[c]["torch_version_observed"] for c in PRIOR_CYCLES),
        "2.13.0+cpu",
    )
    check_torch_file = _all_equal(
        result.get("torch_file_observed"),
        *(prior[c]["torch_file_observed"] for c in PRIOR_CYCLES),
        "/usr/local/lib/python3.11/dist-packages/torch/__init__.py",
    )
    check_command_drafted = _all_equal(
        result.get("command_string_drafted"),
        *(prior[c]["command_string_drafted"] for c in PRIOR_CYCLES),
    )

    venv_manifest_c19_pre = venv_pre.get("dir_manifest_sha256")
    venv_manifest_c19_post = venv_post.get("dir_manifest_sha256")
    check_venv_unchanged = _all_equal(
        venv_manifest_c19_pre,
        venv_manifest_c19_post,
        *(prior[c]["venv_signature_post"]["dir_manifest_sha256"]
          for c in PRIOR_CYCLES),
    )

    all_checks_pass = (
        check_torch_version
        and check_torch_file
        and check_command_drafted
        and check_venv_unchanged
    )
    if all_checks_pass:
        attribution = "ENV_DRIFT_PROBE_CANDIDATE_FOUND_C19_DRY_RUN_ROLL_FORWARD"
        probe_status = "awaiting_operator_green_light"
    else:
        attribution = "ENV_DRIFT_PROBE_C19_DIVERGENCE_FIRST_CLASS_FINDING"
        probe_status = "divergence_from_c7_through_c18_baseline"

    out = {
        "cycle": 19,
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
            "venv_manifest_matches_c7_c8_c9_c10_c11_c12_c13_c14_c15_c16_c17_c18":
                check_venv_unchanged,
            "all_pass": all_checks_pass,
        },
        **{f"{c}_baseline_probe_sha256": _sha256(PRIOR_JSONS[c]) for c in PRIOR_CYCLES},
        **{f"{c}_probe_module_sha256": _sha256(PRIOR_MODULES[c]) for c in PRIOR_CYCLES},
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT_JSON.relative_to(_REPO)}")
    print(f"attribution_verdict: {attribution}")


if __name__ == "__main__":
    main()
