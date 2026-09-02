#!/usr/bin/python3
# ---
# created: 2026-09-02T00:00:00Z
# cycle: 58
# milestone: M-V3-SPINE
# ---
"""Byte-determinism ×2 check for the v3 spine.

Approach: since the primary pipeline caches into `data/v3_spine/<sha16>/`,
the determinism check reruns each stage into a FRESH temp directory and
compares SHA-256 hashes stage-by-stage. Only the compute-heavy stages
(htdemucs, muscriptor) can differ nondeterministically; the mixing +
delivery stages are pure numpy and are already deterministic by
construction.

Records both hashes in `data/v3_spine/<sha16>/determinism.json`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"determinism_check requires /usr/bin/python3 (got {sys.executable})")

WSROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WSROOT))
from scripts.v3_spine.pipeline import run_song, _sha256, _canonical_json_sha256, STEMS_ORDERED


TRACKED_KEYS = [
    "section.wav",
    "stems_6s/drums.wav", "stems_6s/bass.wav", "stems_6s/guitar.wav",
    "stems_6s/piano.wav", "stems_6s/other.wav", "stems_6s/vocals.wav",
    "muscriptor/drums.mid", "muscriptor/bass.mid", "muscriptor/guitar.mid",
    "muscriptor/piano.mid", "muscriptor/other.mid", "muscriptor/vocals.mid",
    "muscriptor/drums.json", "muscriptor/bass.json", "muscriptor/guitar.json",
    "muscriptor/piano.json", "muscriptor/other.json", "muscriptor/vocals.json",
    "merged.mid",
    "instrumental_render.wav",
    "mixed_reconstruction.wav",
]


def _collect_shas(root: Path) -> dict[str, str]:
    d: dict[str, str] = {}
    for k in TRACKED_KEYS:
        p = root / k
        if not p.exists():
            d[k] = "MISSING"
            continue
        if k.endswith(".json"):
            d[k] = _canonical_json_sha256(p)
        else:
            d[k] = _sha256(p)
    return d


def run(song_sha16: str) -> dict:
    primary_root = WSROOT / "data" / "v3_spine"
    primary = primary_root / song_sha16
    if not primary.exists():
        raise RuntimeError(f"primary run not present at {primary}; run pipeline first")

    run1_shas = _collect_shas(primary)

    # Fresh temp for run 2
    tmp = Path(tempfile.mkdtemp(prefix="v3_spine_det_"))
    try:
        run_song(song_sha16, tmp)
        run2_shas = _collect_shas(tmp / song_sha16)
    finally:
        # keep temp on failure for debug; delete only on success
        pass

    mismatches = [k for k in TRACKED_KEYS
                  if run1_shas.get(k) != run2_shas.get(k)]
    result = {
        "song_sha16": song_sha16,
        "n_tracked": len(TRACKED_KEYS),
        "n_mismatch": len(mismatches),
        "byte_determinism_holds": len(mismatches) == 0,
        "mismatches": mismatches,
        "run1_shas": run1_shas,
        "run2_shas": run2_shas,
        "run2_tempdir": str(tmp),
    }
    if not mismatches:
        shutil.rmtree(tmp)
        result["run2_tempdir"] = "cleaned"
    out = primary / "determinism.json"
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--song-sha16", default="31a164f845f8e27e")
    args = ap.parse_args()
    r = run(args.song_sha16)
    print(json.dumps({
        "byte_determinism_holds": r["byte_determinism_holds"],
        "n_mismatch": r["n_mismatch"],
        "mismatches": r["mismatches"],
    }, indent=2))


if __name__ == "__main__":
    main()
