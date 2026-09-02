#!/usr/bin/env /usr/bin/python3
"""c22 M-V3-SPINE-2/env-pin-manifest: deterministic environment-pin manifest generator.

Emits data/v3/deliveries/<sha16>/<cycle>/env_pin.json (also inlined under
manifest.json.env_pins) capturing exact versions + hashes of every non-trivial
runtime dependency that influences byte-identity of the v3 per-stem chain.

Fields (frozen key order, sort_keys=True JSON):
    - python.version, python.executable
    - torch.version, torch.commit
    - numpy.version, numpy.blas
    - librosa.version
    - muscriptor.version+sha  (executable-file sha256)
    - htdemucs.weights_sha    (per-file sha256 of every weight in htdemucs_6s bundle)
    - soundfont.sha256        (FluidR3_GM.sf2)
    - fluidsynth.version
    - model_safetensors.sha256 (MuScriptor medium model)
    - env vars (PYTHONHASHSEED, SOURCE_DATE_EPOCH, TZ, LC_ALL,
                OMP_NUM_THREADS, MKL_NUM_THREADS, OPENBLAS_NUM_THREADS)
    - env_pin.sha256          (self-anchor: sha256 of canonical-JSON of the above,
                               with this key stripped)

Cross-cycle torch/BLAS drift is detectable-by-diff on env_pin.sha256 alone.

Located under scripts/v3_spine/v3_pipeline/ instead of long_exposure/v3_pipeline/
because long_exposure/ is an external read-only orchestrator package. All
consumers import from scripts.v3_spine.v3_pipeline.env_pin.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


SF2_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
MUSCRIPTOR_MODEL = "workspace/models/muscriptor-medium/model.safetensors"
MUSCRIPTOR_BIN = "workspace/learned_transcribers_venv/bin/muscriptor"

# htdemucs_6s bundle discovery — checkpoint locations vary by torch hub cache
HTDEMUCS_CACHE_CANDIDATES = [
    Path.home() / ".cache" / "torch" / "hub" / "checkpoints",
    Path("/root/.cache/torch/hub/checkpoints"),
]


def _sha256(path: Path | str) -> str:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return f"MISSING:{p}"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _try_import_version(mod_name: str) -> str:
    try:
        m = __import__(mod_name)
        return str(getattr(m, "__version__", "unknown"))
    except Exception as e:  # noqa: BLE001
        return f"IMPORT_FAIL:{type(e).__name__}:{str(e)[:100]}"


def _numpy_blas() -> str:
    try:
        import numpy as np
        try:
            info = np.show_config(mode="dicts")  # numpy>=1.25
            blas = info.get("Build Dependencies", {}).get("blas", {})
            return f"{blas.get('name','?')}:{blas.get('version','?')}"
        except Exception:
            import io
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                np.show_config()
            txt = buf.getvalue().lower()
            for hint in ("openblas", "mkl", "blis", "accelerate", "atlas"):
                if hint in txt:
                    return hint
            return "unknown"
    except Exception as e:  # noqa: BLE001
        return f"IMPORT_FAIL:{type(e).__name__}"


def _torch_info() -> dict[str, str]:
    try:
        import torch
        return {
            "version": torch.__version__,
            "commit": getattr(torch.version, "git_version", "unknown"),
            "file": torch.__file__,
        }
    except Exception as e:  # noqa: BLE001
        return {"version": f"IMPORT_FAIL:{type(e).__name__}", "commit": "unknown", "file": "unknown"}


def _fluidsynth_version() -> str:
    try:
        r = subprocess.run(["fluidsynth", "--version"], capture_output=True, timeout=5)
        return (r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")).splitlines()[0].strip() if (r.stdout or r.stderr) else "unknown"
    except Exception as e:  # noqa: BLE001
        return f"EXEC_FAIL:{type(e).__name__}"


def _htdemucs_weights_sha() -> dict[str, str]:
    out: dict[str, str] = {}
    for cache in HTDEMUCS_CACHE_CANDIDATES:
        if not cache.exists():
            continue
        # htdemucs_6s bundle: 4 checkpoint files typically prefixed 'htdemucs_6s'
        for f in sorted(cache.glob("*.th")):
            if "htdemucs" in f.name.lower():
                out[f.name] = _sha256(f)
    if not out:
        out["_status"] = "no_checkpoints_found"
    return out


def _muscriptor_version() -> str:
    try:
        r = subprocess.run([MUSCRIPTOR_BIN, "--version"], capture_output=True, timeout=5)
        s = (r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")).strip()
        return s.splitlines()[0] if s else "unknown"
    except Exception as e:  # noqa: BLE001
        return f"EXEC_FAIL:{type(e).__name__}"


def build_env_pin_manifest() -> dict[str, Any]:
    """Build the env_pin manifest dict (self-anchor NOT yet included).

    Note: subprocess-derived version strings (muscriptor --version,
    fluidsynth --version) are EXCLUDED from the hashed body because
    subprocess timeouts introduce non-determinism between calls.
    Binary integrity is captured via binary_sha256 (muscriptor) and
    file-level SF2 sha256. Version strings are surfaced by
    write_env_pin() in a separate 'diagnostic' block that is NOT
    part of env_pin_sha256.
    """
    torch_info = _torch_info()
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "python": {
            "version": sys.version.split()[0],
            "executable": sys.executable,
        },
        "torch": {
            "version": torch_info["version"],
            "commit": torch_info["commit"],
            "file": torch_info["file"],
        },
        "numpy": {
            "version": _try_import_version("numpy"),
            "blas": _numpy_blas(),
        },
        "librosa": {
            "version": _try_import_version("librosa"),
        },
        "mido": {
            "version": _try_import_version("mido"),
        },
        "soundfile": {
            "version": _try_import_version("soundfile"),
        },
        "scipy": {
            "version": _try_import_version("scipy"),
        },
        "muscriptor": {
            "binary_path": MUSCRIPTOR_BIN,
            "binary_sha256": _sha256(MUSCRIPTOR_BIN),
        },
        "htdemucs": {
            "weights_sha256_per_file": _htdemucs_weights_sha(),
        },
        "soundfont": {
            "path": SF2_PATH,
            "sha256": _sha256(SF2_PATH),
        },
        "fluidsynth": {
            "binary_path": "/usr/bin/fluidsynth",
        },
        "model_safetensors": {
            "path": MUSCRIPTOR_MODEL,
            "sha256": _sha256(MUSCRIPTOR_MODEL),
        },
        "env": {
            "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "unset"),
            "SOURCE_DATE_EPOCH": os.environ.get("SOURCE_DATE_EPOCH", "unset"),
            "TZ": os.environ.get("TZ", "unset"),
            "LC_ALL": os.environ.get("LC_ALL", "unset"),
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS", "unset"),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS", "unset"),
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS", "unset"),
        },
    }
    body = json.dumps(manifest, sort_keys=True, indent=2)
    manifest["env_pin_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return manifest


def write_env_pin(out_path: Path) -> dict[str, Any]:
    """Write env_pin.json. Includes hashed manifest plus a 'diagnostic'
    block (subprocess-derived version strings) that is NOT part of
    env_pin_sha256 — those strings are informational only."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    m = build_env_pin_manifest()
    # Diagnostic block: NOT hashed (see docstring on build_env_pin_manifest)
    m_with_diag = dict(m)
    m_with_diag["diagnostic"] = {
        "muscriptor_version_string": _muscriptor_version(),
        "fluidsynth_version_string": _fluidsynth_version(),
        "diagnostic_note": "not part of env_pin_sha256 hash",
    }
    tmp = out_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(m_with_diag, sort_keys=True, indent=2) + "\n")
    tmp.replace(out_path)
    return m


if __name__ == "__main__":
    m = build_env_pin_manifest()
    print(json.dumps(m, sort_keys=True, indent=2))
    print(f"\nenv_pin_sha256 = {m['env_pin_sha256']}", file=sys.stderr)
