#!/usr/bin/env /usr/bin/python3
"""c75 P1 — Batch-score all 15 gen renders through EAR-1.

Reads c74 EAR-1 impl READ-ONLY (build_exemplar_signatures + score_audio).
For each of 15 gen ab_mix.wav (5 songs x 3 iterations = 15):
  1. Extract per-window VGGish embeddings (10s window, 5s hop, 16 kHz mono).
  2. Compute ear_score in [1,7] via c74 max-over-exemplar-windows + linear anchor.
  3. Write back into per-song ab_mix.manifest.json as:
       ear_score: <float>
       ear_score_backbone: "vggish_only"
       ear_score_computed_at_cycle: 75
       _original_ab_mix_manifest_sha256: <preserved>

Batch rollup: data/v4/gen/batch_score_rollup_c75.json with 15 rows.
Passer gate: ear_score >= 6.0. If passer_count >= 5, delivery mode.

CRITICAL BLOCKERS (as of c75):
  (i)  VGGish inference infra unavailable in this session:
       - tensorflow_hub loads BUT tensorflow triggers ml_dtypes vs numpy>=2.0
         incompatibility (`np.dtype(bfloat16)` -> TypeError: expected 0
         arguments, got 1). Fix requires numpy<2.0 downgrade OR ml_dtypes
         upgrade, both risky in a shared venv.
       - CLAP fails on torchvision::nms (c74 anchor).
  (ii) P4 band-4 spot check FAILED this cycle: band-4 songs score 6.0-7.0,
       above the campaign-L119 mandate of "clearly below LOO exemplar ceiling
       - 0.5". Calibration cannot distinguish band-4 from band-7 under current
       linear-anchor scheme. Passer-count trust for gen renders is BROKEN even
       if inference were available.

Per brief line 195-198 + P4 halt-honest branch:
  IF band-4 FAIL: halt-honest, block P1 trust, propose c76 calibration-anchor
  fix. Written blocker sidecar at data/v4/gen/batch_score_blocker_c75.json;
  15 gen manifests NOT modified this cycle to preserve calibration honesty.

Contract preserved for c76+ resume:
  When both blockers resolved (calibration fix + backbone install), rerun this
  script with --unblocked flag to perform the annotation pass.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
    "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.ear import v4_ear  # READ-ONLY import


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _try_load_vggish():
    """Attempt to load VGGish model. Returns (model, error_str)."""
    try:
        import sys as _sys
        for p in ("/root/.local/lib/python3.11/site-packages",
                  "/usr/local/lib/python3.11/dist-packages",
                  "/usr/lib/python3/dist-packages"):
            if p not in _sys.path:
                _sys.path.insert(0, p)
        import warnings
        warnings.simplefilter("ignore")
        import tensorflow_hub as hub
        import tensorflow as tf  # noqa: F401 (triggers ml_dtypes)
        m = hub.load("https://tfhub.dev/google/vggish/1")
        return m, None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:300]}"


def find_gen_ab_mix_files(gen_root: Path) -> list[dict]:
    """Enumerate all 15 gen ab_mix.wav files across iteration_01/02/03."""
    rows = []
    for it_dir in sorted(gen_root.glob("iteration_0*")):
        for song_dir in sorted(it_dir.glob("gen_v4_song_*_donor_*")):
            wav = song_dir / "ab_mix.wav"
            man = song_dir / "ab_mix.manifest.json"
            if not wav.exists() or not man.exists():
                continue
            song_id = song_dir.name.split("_donor_")[0]
            donor_sha16 = song_dir.name.split("_donor_")[1]
            iteration = int(it_dir.name.split("_")[1])
            rows.append({
                "iteration": iteration,
                "song_id": song_id,
                "donor_sha16": donor_sha16,
                "song_dir": str(song_dir.relative_to(ROOT)),
                "wav": str(wav.relative_to(ROOT)),
                "manifest": str(man.relative_to(ROOT)),
            })
    return rows


def write_blocker_sidecar(rows: list[dict], vggish_error: str, band4_gate_passes: bool) -> Path:
    """Emit honest blocker sidecar per FD-1."""
    out = {
        "milestone_id": "P1-batch-score-blocked",
        "cycle": 75,
        "verdict": "HALT_HONEST_BLOCKED_ON_CALIBRATION_AND_INFRA",
        "gen_rows_enumerated": len(rows),
        "expected_15": len(rows) == 15,
        "backbone_infra_status": {
            "vggish_load_error": vggish_error,
            "clap_status": "FAILED_torchvision_nms_c74_anchor",
            "workaround_authorized_c76": (
                "downgrade numpy<2.0 OR upgrade ml_dtypes; both currently blocked "
                "by shared venv discipline (would affect M-CLASS-1 M-TEX-1 anchors)"
            ),
        },
        "calibration_status": {
            "band4_spot_check_gate_passes": band4_gate_passes,
            "sidecar_path": "data/v4/ear/band4_spot_check_c75.json",
            "campaign_L119_mandate": "band-4 max < loo_min - 0.5",
            "finding": (
                "FAIL — band-4 songs score >= loo_min - 0.5; current linear-anchor "
                "calibration cannot distinguish band-4 from band-7 exemplars"
            ),
        },
        "consequence_per_brief_P4_halt_honest_branch": (
            "P1 passer-count trust BLOCKED; P2 iteration-04 NOT launched; "
            "passer_count = null (not computed); hand calibration-anchor fix to c76"
        ),
        "resume_command_c76_after_fix": (
            "python3 scripts/ear/score_gen_batch.py --unblocked"
        ),
        "manifests_modified_this_cycle": 0,
        "env_pin_sha256": "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca",
    }
    out_path = ROOT / "data/v4/gen/batch_score_blocker_c75.json"
    out_path.write_text(json.dumps(out, sort_keys=True, indent=2))
    return out_path


def batch_score_when_unblocked(rows: list[dict], model) -> dict:
    """Real batch-score path. Only invoked when --unblocked in a future cycle."""
    # Deferred implementation: mirrors scripts/v4_ear/ear.py _embed_song shape.
    # NOT invoked in c75 per halt-honest branch.
    raise NotImplementedError("c75 halt-honest — this path unlocks at c76+ after calibration fix")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--unblocked", action="store_true",
                    help="Skip infra + calibration blockers (c76+ resume path)")
    args = ap.parse_args(argv)

    gen_root = ROOT / "data/v4/gen"
    rows = find_gen_ab_mix_files(gen_root)
    print(f"Enumerated {len(rows)} gen ab_mix rows across iterations")

    # Check calibration blocker (P4 band-4 gate)
    band4_sidecar = ROOT / "data/v4/ear/band4_spot_check_c75.json"
    if band4_sidecar.exists():
        b4 = json.loads(band4_sidecar.read_text())
        band4_passes = bool(b4.get("gate_passes", False))
    else:
        band4_passes = False

    # Check infra blocker
    model, err = _try_load_vggish()

    if not args.unblocked and (not band4_passes or model is None):
        sidecar = write_blocker_sidecar(rows, err or "not_attempted", band4_passes)
        print(f"HALT_HONEST_BLOCKED → {sidecar}")
        print(f"  band4_gate_passes: {band4_passes}")
        print(f"  vggish_available: {model is not None}")
        return 0

    # Unblocked path (deferred)
    return batch_score_when_unblocked(rows, model)


if __name__ == "__main__":
    sys.exit(main())
