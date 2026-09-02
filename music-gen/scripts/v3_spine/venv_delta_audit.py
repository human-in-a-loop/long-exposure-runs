#!/usr/bin/env python3
"""c5 Track A: snapshot the muscriptor venv and diff against any prior snapshot."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

VENV = Path("workspace/learned_transcribers_venv")
SNAP_DIR = Path("data/v3_spine/venv_snapshots")
OUT = Path("data/v3_spine/venv_delta_audit.json")


def freeze_venv() -> dict[str, str]:
    r = subprocess.run(
        [str(VENV / "bin" / "pip"), "freeze"], capture_output=True, text=True, check=True
    )
    pkgs = {}
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Handle name==version, name @ url, name==version ; markers
        m = re.match(r"^([A-Za-z0-9_.\-]+)\s*==\s*([^;\s]+)", line)
        if m:
            pkgs[m.group(1).lower().replace("_", "-")] = m.group(2)
    return pkgs


def semver_class(prior: str | None, current: str) -> str:
    if prior is None:
        return "missing_prior"
    if prior == current:
        return "none"

    def parts(v: str) -> list[int]:
        digits = re.findall(r"\d+", v)
        return [int(x) for x in digits[:3]] + [0, 0, 0][: 3 - len(digits[:3])]

    pp, cp = parts(prior), parts(current)
    if pp[0] != cp[0]:
        return "major"
    if pp[1] != cp[1]:
        return "minor"
    if pp[2] != cp[2]:
        return "patch"
    return "prerelease"


def main():
    snap = freeze_venv()
    SNAP_DIR.mkdir(parents=True, exist_ok=True)

    # Find any prior snapshot
    prior_files = sorted(SNAP_DIR.glob("*.json"))
    prior = None
    prior_name = None
    if prior_files:
        prior_name = prior_files[-1].name
        prior = json.loads(prior_files[-1].read_text())

    # Pin baseline if none
    baseline_established = False
    if prior is None:
        baseline_path = SNAP_DIR / "c5_baseline.json"
        baseline_path.write_text(
            json.dumps({"cycle": 5, "packages": snap}, indent=2, sort_keys=True)
        )
        baseline_established = True
        prior_name = "c5_baseline.json (just created)"
        prior = {"cycle": 5, "packages": snap}

    prior_pkgs = prior.get("packages", {})
    all_names = sorted(set(snap.keys()) | set(prior_pkgs.keys()))
    deltas = []
    for n in all_names:
        cur = snap.get(n)
        pri = prior_pkgs.get(n)
        cls = semver_class(pri, cur or "")
        deltas.append(
            {
                "name": n,
                "prior_version": pri,
                "current_version": cur,
                "delta_class": cls,
            }
        )

    result = {
        "cycle": 5,
        "prior_snapshot": prior_name,
        "baseline_established": baseline_established,
        "n_packages_c5": len(snap),
        "n_packages_prior": len(prior_pkgs),
        "snapshot_c5": snap,
        "delta_per_pkg": deltas,
        "n_delta_none": sum(1 for d in deltas if d["delta_class"] == "none"),
        "n_delta_nonzero": sum(1 for d in deltas if d["delta_class"] not in ("none",)),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))
    out_sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(
        f"packages_c5={len(snap)} baseline_established={baseline_established} "
        f"prior={prior_name} out_sha={out_sha[:16]}"
    )


if __name__ == "__main__":
    main()
