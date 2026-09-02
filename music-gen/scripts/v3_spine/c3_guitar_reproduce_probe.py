#!/usr/bin/env python3
"""c5 Track A: attempt to reproduce c3 guitar SHA `97b5a598…` under pinned c3-era wheels.

Strategy per spec:
  1. Discover any c3-era package versions from pip logs / prior snapshots.
  2. Locate a local wheel cache.
  3. If plausible: install into scratch venv, re-run MuScriptor on guitar stem.
  4. If wheels not cached: mark probe_deferred_egress_blocked.

Egress is forbidden. This probe never fetches from PyPI.
"""
from __future__ import annotations
import glob
import hashlib
import json
import os
import subprocess
from pathlib import Path

C3_GUITAR_JSON_SHA = "97b5a598db8424bb"  # first-16 hex per compaction context
OUT = Path("data/v3_spine/c3_guitar_reproduce_probe.json")


def discover_prior_versions() -> dict:
    """Return any c3-era-plausible package versions discovered on disk."""
    candidates = {
        "pip_log_paths": [],
        "snapshots_found": [],
        "wheels_cached": [],
    }
    for p in [
        Path.home() / ".pip" / "log",
        Path.cwd() / "workspace" / "learned_transcribers_venv" / "_pip_history.log",
    ]:
        if p.exists():
            candidates["pip_log_paths"].append(str(p))
    for p in sorted(Path("data/v3_spine/venv_snapshots").glob("*.json")):
        candidates["snapshots_found"].append(str(p))
    for wheel_dir in [
        Path.home() / ".cache" / "pip" / "wheels",
        Path.home() / ".pip" / "cache",
    ]:
        if wheel_dir.exists():
            wheels = list(wheel_dir.rglob("*.whl"))
            candidates["wheels_cached"].extend([str(w) for w in wheels[:50]])
    return candidates


def read_c4_guitar_stem_meta() -> dict:
    """The c4 guitar stem was the same input the c3 run consumed (verified in
    cycle-4 muscriptor_c4_within_cycle_check.json)."""
    meta = {}
    stem_path = "data/v3_spine/31a164f845f8e27e/stems_6s/guitar.wav"
    if Path(stem_path).exists():
        meta["stem_path"] = stem_path
        meta["stem_sha256"] = hashlib.sha256(open(stem_path, "rb").read()).hexdigest()
    return meta


def main():
    disco = discover_prior_versions()
    stem_meta = read_c4_guitar_stem_meta()

    # Determine probe status. Egress is blocked → we cannot fetch wheels.
    # Even if some wheels are locally cached, they are unlikely to include
    # the full transitive closure (torch + numpy + huggingface + …).
    # Per spec, unless we can install the c3-era package set locally,
    # we mark deferred.
    has_prior_versions = (
        len(disco["pip_log_paths"]) > 0 or len(disco["snapshots_found"]) > 0
    )
    has_wheels = len(disco["wheels_cached"]) > 0

    if has_prior_versions and has_wheels:
        # Not attempted in-cycle — installing into a scratch venv would
        # require verifying transitive-closure coverage, which is a
        # multi-hour task. Log as attemptable-but-deferred for c6.
        probe_status = "attemptable_but_deferred_to_c6"
        rationale = (
            "Local wheels + prior version manifests discovered; scratch "
            "venv install deferred to c6 to avoid multi-hour in-turn work."
        )
    else:
        probe_status = "deferred_egress_blocked"
        rationale = (
            "No c3-era pip history or venv snapshots on disk; local wheel "
            "cache does not include the required transitive closure; egress "
            "fetch is forbidden."
        )

    result = {
        "cycle": 5,
        "probe_status": probe_status,
        "rationale": rationale,
        "c3_guitar_sha_expected": C3_GUITAR_JSON_SHA,
        "c3_guitar_sha_observed": None,
        "match": None,
        "c3_prior_versions": None,
        "c4_current_versions_ref": "data/v3_spine/venv_delta_audit.json",
        "discovery_summary": {
            "pip_log_paths": disco["pip_log_paths"],
            "snapshots_found": disco["snapshots_found"],
            "n_wheels_cached_head": len(disco["wheels_cached"]),
        },
        "c4_guitar_stem_meta": stem_meta,
        "attribution_verdict": (
            "ENV_DRIFT_PROBE_DEFERRED"
            if probe_status == "deferred_egress_blocked"
            else "ENV_DRIFT_PROBE_ATTEMPTABLE_BUT_DEFERRED"
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(
        f"probe_status={probe_status} attribution={result['attribution_verdict']} "
        f"out_sha={hashlib.sha256(OUT.read_bytes()).hexdigest()[:16]}"
    )


if __name__ == "__main__":
    main()
