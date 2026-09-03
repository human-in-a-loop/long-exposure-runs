#!/usr/bin/env python3
"""Content-addressed stage-cache primitives for the checkpointed v3 driver.

Contract: see docs/v3_spine_stage_checkpointed_driver_spec.md.

A stage is a pure function of a tuple of hashable inputs. compute_key() derives a
deterministic sha256 over (stage_name, per-input file/scalar SHAs, env pins,
spec_version). check() either returns a matching cached manifest (skip the stage)
or None (run the stage). record() writes a fresh manifest under a keyed subdir.

No PRNG. No wall-clock in the hash. `SOURCE_DATE_EPOCH`-derived ts fields only.
Interpreter guarded to /usr/bin/python3.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"interpreter guard: expected /usr/bin/python3, got {sys.executable}")


CACHE_SPEC_VERSION = "checkpointed_v1"


def _sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha_scalar(v: Any) -> str:
    payload = json.dumps(v, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _resolve_input(v: Any) -> str:
    """Files hash by content; everything else hashes as canonical-JSON scalar."""
    if isinstance(v, (Path, str)) and (isinstance(v, Path) or Path(v).is_file()):
        p = Path(v)
        if p.is_file():
            return f"file:{_sha_file(p)}"
    return f"scalar:{_sha_scalar(v)}"


def compute_key(stage_name: str, inputs: dict[str, Any], env_pin_sha: str) -> str:
    """Deterministic sha256 identifier for one (stage, inputs, env) tuple."""
    canon = {
        "stage": stage_name,
        "inputs": {k: _resolve_input(v) for k, v in sorted(inputs.items())},
        "env_pin_sha256": env_pin_sha,
        "spec_version": CACHE_SPEC_VERSION,
    }
    payload = json.dumps(canon, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cache_dir(work_dir: Path, stage_name: str, key: str) -> Path:
    return work_dir / "stage_cache" / stage_name / key[:16]


def check(stage_name: str, inputs: dict[str, Any], env_pin_sha: str,
          work_dir: Path) -> dict[str, Any] | None:
    """Return the cached manifest dict if inputs match, else None.

    The returned dict carries an extra key `_cache_dir` (Path) pointing to the
    directory whose `outputs/` subtree holds the frozen stage output. Callers
    copy or hard-link those files into the delivery layout.
    """
    key = compute_key(stage_name, inputs, env_pin_sha)
    d = _cache_dir(work_dir, stage_name, key)
    manifest = d / "stage_manifest.json"
    if not manifest.is_file():
        return None
    try:
        m = json.loads(manifest.read_text())
    except json.JSONDecodeError:
        return None
    if m.get("input_key") != key:
        return None  # partially written or manifest-key drift
    # verify every claimed output still exists with the claimed sha
    outputs_dir = d / "outputs"
    for relpath, want_sha in m.get("outputs", {}).items():
        got = outputs_dir / relpath
        if not got.is_file() or _sha_file(got) != want_sha:
            return None
    m["_cache_dir"] = d
    return m


def record(stage_name: str, inputs: dict[str, Any], env_pin_sha: str,
           work_dir: Path, produced_files: dict[str, Path],
           wall_seconds: float) -> dict[str, Any]:
    """Freeze a completed stage's outputs under the cache directory.

    produced_files maps `relpath` (as it will live inside outputs/) to absolute
    source paths. Copies (not hard-links, to survive cross-filesystem work dirs).
    Returns the written manifest.
    """
    key = compute_key(stage_name, inputs, env_pin_sha)
    d = _cache_dir(work_dir, stage_name, key)
    outputs = d / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    out_shas: dict[str, str] = {}
    for relpath, src in produced_files.items():
        dst = outputs / relpath
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        out_shas[relpath] = _sha_file(dst)
    # SOURCE_DATE_EPOCH-derived ts (no wall clock in the hashed manifest)
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", str(int(time.time()))))
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))
    manifest = {
        "stage": stage_name,
        "input_key": key,
        "outputs": out_shas,
        "wall_seconds": round(wall_seconds, 3),
        "ts": ts_iso,
        "env_pin_sha256": env_pin_sha,
        "cache_spec_version": CACHE_SPEC_VERSION,
    }
    manifest_path = d / "stage_manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2))
    return manifest


def stage_names_hit(work_dir: Path) -> list[str]:
    """Enumerate stage names with at least one manifest under work_dir/stage_cache/."""
    root = work_dir / "stage_cache"
    if not root.is_dir():
        return []
    return sorted([p.name for p in root.iterdir() if p.is_dir()])


if __name__ == "__main__":
    # tiny smoke test — non-destructive
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        src = wd / "src.txt"
        src.write_text("hello")
        env_sha = _sha_scalar({"env": "test"})
        inputs = {"in": src, "n": 3}
        assert check("smoke", inputs, env_sha, wd) is None
        prod = wd / "prod.bin"
        prod.write_bytes(b"\x00\x01\x02")
        record("smoke", inputs, env_sha, wd, {"out.bin": prod}, wall_seconds=0.001)
        m = check("smoke", inputs, env_sha, wd)
        assert m is not None, "cache should HIT after record"
        assert list(m["outputs"].keys()) == ["out.bin"]
        # mutate input → MISS
        src.write_text("hello, world")
        assert check("smoke", inputs, env_sha, wd) is None, "cache must MISS on input drift"
    print("stage_cache smoke test: PASS")
