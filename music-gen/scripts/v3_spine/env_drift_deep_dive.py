#!/usr/bin/env python3
"""c6 Track A: env-drift deep-dive local wheel/dist-info scan (no network).

Pinned pre-code by docs/v3_spine_env_drift_deep_dive_spec.md
(sha256 in data/v3_spine/env_drift_deep_dive_spec_hash.txt).

Milestone: M-V3-SPINE-1/env-drift-deep-dive-completed
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

# Env pins.
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"env_drift_deep_dive requires /usr/bin/python3 (got {sys.executable})")

REPO = Path(__file__).resolve().parents[2]
OUT_JSON = REPO / "data" / "v3_spine" / "env_drift_deep_dive.json"
OUT_BYTE_DET = REPO / "data" / "v3_spine" / "env_drift_deep_dive_byte_det.json"
SPEC_HASH_FILE = REPO / "data" / "v3_spine" / "env_drift_deep_dive_spec_hash.txt"
C5_BASELINE = REPO / "data" / "v3_spine" / "venv_snapshots" / "c5_baseline.json"

SCAN_ROOTS = [
    "/root",
    "/home",
    "/var/cache/apt",
    "/var/lib/apt",
    "/var/lib/dpkg",
    "/var/lib/docker",
    "/opt",
    "/usr/lib",
    "/usr/local/lib",
    "/tmp",
]

SKIP_PREFIXES = ("/proc", "/sys", "/dev")

TORCH_FILE_RE = re.compile(r"^torch(-[a-zA-Z_]+)?-([0-9][0-9.a-zA-Z+_]*?)(-|\.whl|\.tar\.gz|\.zip|$)")
TORCH_DIST_INFO_RE = re.compile(r"^(torch(?:-[a-zA-Z_]+)?)-([0-9][0-9.a-zA-Z+_]*)\.dist-info$")


def _sha256_file(p: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def _classify(name: str) -> str:
    if name.endswith(".whl"):
        return "wheel"
    if name.endswith(".dist-info") or TORCH_DIST_INFO_RE.match(name):
        return "dist_info_dir"
    if name.endswith(".tar.gz") or name.endswith(".zip"):
        return "sdist"
    if name.endswith(".egg-info"):
        return "egg_info"
    return "other"


def _parse_version(name: str) -> str | None:
    m = TORCH_DIST_INFO_RE.match(name)
    if m:
        return m.group(2)
    m = TORCH_FILE_RE.match(name)
    if m:
        return m.group(2)
    return None


def scan(roots: list[str]) -> tuple[list[dict], list[str], list[str]]:
    candidates: list[dict] = []
    attempted: list[str] = []
    denied: list[str] = []
    seen_paths: set[str] = set()

    for root in roots:
        if not os.path.isdir(root):
            denied.append(root + " (missing)")
            continue
        try:
            os.listdir(root)
        except (OSError, PermissionError) as e:
            denied.append(f"{root} ({type(e).__name__})")
            continue
        attempted.append(root)

        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            if any(dirpath.startswith(s) for s in SKIP_PREFIXES):
                dirnames[:] = []
                continue
            # Also skip these once we cross into them.
            dirnames[:] = sorted([d for d in dirnames
                                  if not d.startswith(".git")
                                  and d not in ("proc", "sys", "dev")])
            # Match dist-info directories.
            for d in dirnames:
                m = TORCH_DIST_INFO_RE.match(d)
                if not m:
                    continue
                full = os.path.join(dirpath, d)
                if full in seen_paths:
                    continue
                seen_paths.add(full)
                version = m.group(2)
                candidates.append({
                    "path": full,
                    "filename": d,
                    "filetype": "dist_info_dir",
                    "size_bytes": None,
                    "sha256": None,
                    "version": version,
                    "matches_c3_baseline_hypothesis": version.startswith("2.13"),
                })
            for fn in sorted(filenames):
                if not fn.startswith("torch"):
                    continue
                if not (fn.endswith(".whl") or fn.endswith(".tar.gz") or fn.endswith(".zip")):
                    continue
                full = os.path.join(dirpath, fn)
                if full in seen_paths:
                    continue
                seen_paths.add(full)
                try:
                    sz = os.path.getsize(full)
                except (OSError, PermissionError):
                    sz = None
                ver = _parse_version(fn)
                candidates.append({
                    "path": full,
                    "filename": fn,
                    "filetype": _classify(fn),
                    "size_bytes": sz,
                    "sha256": _sha256_file(Path(full)) if sz is not None and sz < (2 << 30) else None,
                    "version": ver,
                    "matches_c3_baseline_hypothesis": (ver or "").startswith("2.13"),
                })

    # Deterministic order.
    candidates.sort(key=lambda r: (r["path"], r["filename"]))
    return candidates, sorted(attempted), sorted(denied)


def load_c5_torch_baseline() -> dict:
    try:
        d = json.loads(C5_BASELINE.read_text())
        pkgs = d.get("packages", {})
        return {k: v for k, v in pkgs.items() if "torch" in k.lower()}
    except (OSError, json.JSONDecodeError):
        return {}


def build_report() -> dict:
    candidates, attempted, denied = scan(SCAN_ROOTS)
    n_matches = sum(1 for c in candidates if c["matches_c3_baseline_hypothesis"])
    if n_matches > 0:
        probe_status = "candidate_found"
        first = next(c for c in candidates if c["matches_c3_baseline_hypothesis"])
        attribution = "ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_REPRODUCE"
        reproduction = (
            f"# c7 reproduction (requires operator approval; do NOT run in c6):\n"
            f"/usr/bin/python3 -m pip install --no-deps --no-index "
            f"--find-links={os.path.dirname(first['path'])} "
            f"torch=={first['version']}"
        )
    else:
        probe_status = "no_local_candidate"
        attribution = "ENV_DRIFT_PROBE_EXHAUSTED_LOCAL"
        reproduction = None

    spec_sha = SPEC_HASH_FILE.read_text().strip()

    return {
        "cycle": 6,
        "milestone_id": "M-V3-SPINE-1/env-drift-deep-dive-completed",
        "spec_sha256": spec_sha,
        "network_syscall_attempted": False,
        "scan_roots_attempted": attempted,
        "scan_roots_skipped_denied": denied,
        "candidates": candidates,
        "n_candidates_total": len(candidates),
        "n_candidates_matching_c3_hypothesis": n_matches,
        "probe_status": probe_status,
        "attribution_verdict": attribution,
        "reproduction_command_for_c7_operator_approved": reproduction,
        "c5_torch_baseline": load_c5_torch_baseline(),
    }


def _write(path: Path, obj: dict) -> str:
    payload = json.dumps(obj, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload)
    tmp.replace(path)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    report = build_report()

    tmp1 = Path(tempfile.mkdtemp(prefix="env_drift_r1_")) / "env_drift_deep_dive.json"
    tmp2 = Path(tempfile.mkdtemp(prefix="env_drift_r2_")) / "env_drift_deep_dive.json"
    sha1 = _write(tmp1, build_report())
    sha2 = _write(tmp2, build_report())

    final_sha = _write(OUT_JSON, report)

    byte_det = {
        "cycle": 6,
        "run1_sha256": sha1,
        "run2_sha256": sha2,
        "final_sha256": final_sha,
        "byte_deterministic_x2": sha1 == sha2 == final_sha,
    }
    _write(OUT_BYTE_DET, byte_det)

    print(json.dumps({
        "probe_status": report["probe_status"],
        "attribution_verdict": report["attribution_verdict"],
        "n_candidates": report["n_candidates_total"],
        "n_matches_c3": report["n_candidates_matching_c3_hypothesis"],
        "byte_det_x2": byte_det["byte_deterministic_x2"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
