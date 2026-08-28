"""Driver for M-EAR-1/head-regularization-audit.

For each of the three regularized-head variants (ridge, bottleneck,
frozen_projector):

  1. Verify harness anchor SHAs (stability_audit.py, synthetic_labels.py,
     stability_metrics.py, model.py, corn.py, features.py) match the
     cycle-22 clone-2 recorded values. Refuse to run on any mismatch.
  2. Snapshot the pre-run SHA-256 manifest of ``data/ear/features/``.
  3. Monkey-patch ``scripts.ear.model._fit`` and
     ``scripts.ear.stability_audit.train_and_eval`` with the variant's
     versions so the frozen cycle-22 harness's local
     ``from .model import _fit`` picks up the variant chassis.
  4. Invoke ``stability_audit.run_audit`` TWICE into per-variant temp
     out-dirs and check byte-determinism (C3').
  5. Emit ``data/ear/head_regularization_audit/stability_report_v2_<variant>.json``
     from the second (canonical) run.
  6. Verify post-run feature-cache SHA-manifest byte-identical to pre-run.

Emits under ``data/ear/head_regularization_audit/``:
  stability_report_v2_ridge.json
  stability_report_v2_bottleneck.json
  stability_report_v2_frozen_projector.json
  variant_verdicts.json
  harness_anchor_manifest.json
  feature_cache_pre_post_shas.json

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: /usr/bin/python3.
"""
# created: 2026-08-28T20:35:00Z  cycle: 23  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 3fbd8c1ab57c)  milestone: M-EAR-1/head-regularization-audit
from __future__ import annotations
from . import _interp  # noqa: F401

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

# Cycle-22 clone-2 anchor SHAs (from docs/ear_stability_audit_report.md
# provenance + this driver's initial handshake at cycle-23 start).
HARNESS_ANCHOR_SHAS = {
    "scripts/ear/stability_audit.py":  "b1ce5137b665a962657f1ee128db4d36abcb6d2174f57101b354a3194ea02e4c",
    "scripts/ear/synthetic_labels.py": "b71f194ef97e8936bb8942d5fccba899e6efe47e292cca185728d1cd9f41fb4d",
    "scripts/ear/stability_metrics.py":"6a5cb5183fdc77e80677ef01bb47f777a2662404f737f8aa74287f30cf97dc27",
    "scripts/ear/model.py":            "d4322a95fc2328b201b4040713dfdf8e294d8d0ae31db7e81c6390371492b552",
    "scripts/ear/corn.py":             "5028c58c20f23cd62c94789fad3522f94953417b79dec33b8506704b83a9921b",
    "scripts/ear/features.py":         "5e7cbf33cd81b501368f6334b2e5c67c41172c4d9e60bb34154274897c611f53",
}

VARIANTS = ("ridge", "bottleneck", "frozen_projector")

OUT_DIR = Path("data/ear/head_regularization_audit")
DEFAULT_CYCLE6_MAE = 0.890909090909091


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_harness_anchors(workspace: Path = Path(".")) -> dict[str, str]:
    """Refuse to run if any anchored file's SHA has drifted."""
    observed: dict[str, str] = {}
    for rel, want in HARNESS_ANCHOR_SHAS.items():
        p = workspace / rel
        if not p.exists():
            raise SystemExit(f"[stability_audit_v2] anchor missing: {p}")
        got = _sha256_of_file(p)
        observed[rel] = got
        if got != want:
            raise SystemExit(
                f"[stability_audit_v2] REFUSING to run: {rel} SHA drift "
                f"(observed={got}, cycle-22-anchor={want})."
            )
    return observed


def feature_cache_manifest(cache_dir: Path = Path("data/ear/features")) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for p in sorted(cache_dir.glob("*.npz")):
        manifest[p.name] = _sha256_of_file(p)
    return manifest


# ---------------------------------------------------------------------------
# Variant-monkey-patched audit invocation
# ---------------------------------------------------------------------------
def _load_variant(name: str):
    if name == "ridge":
        from . import model_v2_ridge as m
    elif name == "bottleneck":
        from . import model_v2_bottleneck as m
    elif name == "frozen_projector":
        from . import model_v2_frozen_projector as m
        m.ensure_pca_basis()
    else:
        raise ValueError(f"unknown variant {name!r}")
    return m


def _run_variant_once(variant_name: str, tmp_out_dir: Path, *, epochs: int) -> tuple[str, dict]:
    """Run the cycle-22 harness with the variant patched in.

    Returns (sha256 of stability_report.json, parsed report dict).
    """
    from . import model as _model
    from . import stability_audit as _sa
    variant = _load_variant(variant_name)

    # Preserve originals, patch, run, restore.
    orig_fit = _model._fit
    orig_train = _model.train_and_eval
    orig_sa_train = _sa.train_and_eval
    try:
        _model._fit = variant._fit
        _model.train_and_eval = variant.train_and_eval
        _sa.train_and_eval = variant.train_and_eval

        tmp_out_dir.mkdir(parents=True, exist_ok=True)
        result = _sa.run_audit(
            out_dir=tmp_out_dir,
            epochs=epochs,
            cycle6_mae=DEFAULT_CYCLE6_MAE,
        )
    finally:
        _model._fit = orig_fit
        _model.train_and_eval = orig_train
        _sa.train_and_eval = orig_sa_train

    report_path = tmp_out_dir / "stability_report.json"
    return _sha256_of_file(report_path), result["report"]


# ---------------------------------------------------------------------------
# Verdict rubric (frozen; locked before the run)
# ---------------------------------------------------------------------------
C2_TAU_THRESHOLD = 0.4


def _verdict_c1(cycle6_mae: float, envelope: dict) -> str:
    return "PASS" if envelope["p05"] <= cycle6_mae <= envelope["p95"] else "FAIL"


def _verdict_c2(mean_tau: float) -> str:
    return "PASS" if mean_tau >= C2_TAU_THRESHOLD else "FAIL"


def _verdict_c3(sha1: str, sha2: str) -> str:
    return "PASS" if sha1 == sha2 else "FAIL"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def run_all(out_dir: Path = OUT_DIR, *, epochs: int = 200,
            cycle6_mae: float = DEFAULT_CYCLE6_MAE) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # 1. Harness anchor SHAs
    anchors = verify_harness_anchors()
    anchor_manifest = {
        "verified_at": ts_start,
        "cycle22_anchor_shas": HARNESS_ANCHOR_SHAS,
        "observed_shas": anchors,
        "match": True,
    }
    (out_dir / "harness_anchor_manifest.json").write_text(
        json.dumps(anchor_manifest, indent=2, sort_keys=True) + "\n"
    )

    # 2. Feature-cache SHA manifest (pre-run)
    pre_manifest = feature_cache_manifest()

    # 3. Per-variant twice-run
    variant_verdicts: dict[str, dict] = {}
    variant_reports: dict[str, dict] = {}
    for name in VARIANTS:
        run1_dir = out_dir / f"_run1_{name}"
        run2_dir = out_dir / f"_run2_{name}"
        # Wipe temp scratch to guarantee a clean write.
        if run1_dir.exists():
            shutil.rmtree(run1_dir)
        if run2_dir.exists():
            shutil.rmtree(run2_dir)

        sha1, report1 = _run_variant_once(name, run1_dir, epochs=epochs)
        sha2, report2 = _run_variant_once(name, run2_dir, epochs=epochs)

        # Frozen report file lives in the main out_dir; carries variant tag.
        canonical_path = out_dir / f"stability_report_v2_{name}.json"
        # Report from run2 is byte-identical to run1 if C3' PASSes; either is fine.
        canonical_path.write_text(
            json.dumps(_augment_report(report2, name), sort_keys=True,
                       ensure_ascii=False, separators=(",", ":")) + "\n"
        )

        # C1' / C2' / C3'
        env = report2["mae_envelope"]
        mean_tau = report2["tau_summary"]["mean"]
        c1 = _verdict_c1(cycle6_mae, env)
        c2 = _verdict_c2(mean_tau)
        c3 = _verdict_c3(sha1, sha2)
        overall = "PASS" if (c1 == "PASS" and c2 == "PASS" and c3 == "PASS") else "FAIL"
        variant_verdicts[name] = {
            "variant": name,
            "C1_prime": {"name": "MAE reproducibility",
                         "threshold": f"cycle-6 MAE ({cycle6_mae}) inside variant's [5th,95th] envelope",
                         "envelope_p05": env["p05"], "envelope_p95": env["p95"],
                         "cycle6_mae": cycle6_mae, "verdict": c1},
            "C2_prime": {"name": "Rank stability",
                         "threshold": f"mean pairwise Kendall tau >= {C2_TAU_THRESHOLD}",
                         "observed_mean_tau": mean_tau, "verdict": c2},
            "C3_prime": {"name": "Byte-determinism x 2",
                         "threshold": "SHA-256 equal on two independent runs",
                         "run1_sha256": sha1, "run2_sha256": sha2, "verdict": c3},
            "overall": overall,
            "median_mae": env["p50"],
            "min_mae": env["min"],
            "max_mae": env["max"],
        }
        variant_reports[name] = report2

    (out_dir / "variant_verdicts.json").write_text(
        json.dumps(variant_verdicts, indent=2, sort_keys=True) + "\n"
    )

    # 4. Feature-cache SHA manifest (post-run) + invariance check
    post_manifest = feature_cache_manifest()
    ts_end = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    fc_report = {
        "pre_run_sha_manifest": pre_manifest,
        "post_run_sha_manifest": post_manifest,
        "n_files": len(pre_manifest),
        "byte_identical": pre_manifest == post_manifest,
        "verified_pre": ts_start,
        "verified_post": ts_end,
    }
    (out_dir / "feature_cache_pre_post_shas.json").write_text(
        json.dumps(fc_report, indent=2, sort_keys=True) + "\n"
    )
    if not fc_report["byte_identical"]:
        raise SystemExit("[stability_audit_v2] feature cache SHA manifest changed during audit")

    # 5. Print summary
    print("=" * 72)
    print(f"[head-reg-audit] harness SHAs OK; feature cache SHA-invariant")
    print(f"[head-reg-audit] tau threshold C2'={C2_TAU_THRESHOLD}, "
          f"cycle6 MAE anchor={cycle6_mae:.4f}")
    for name in VARIANTS:
        v = variant_verdicts[name]
        print(f"  {name:20s} "
              f"tau_mean={v['C2_prime']['observed_mean_tau']:+.4f} "
              f"median_mae={v['median_mae']:.4f} "
              f"env=[{v['C1_prime']['envelope_p05']:.4f},{v['C1_prime']['envelope_p95']:.4f}]  "
              f"C1={v['C1_prime']['verdict']} C2={v['C2_prime']['verdict']} "
              f"C3={v['C3_prime']['verdict']} => {v['overall']}")
    print("=" * 72)

    return {
        "verdicts": variant_verdicts,
        "reports": variant_reports,
        "anchor_manifest": anchor_manifest,
        "feature_cache_report": fc_report,
    }


def _augment_report(report: dict, variant_name: str) -> dict:
    """Deep-copy report + inject variant identity for downstream tooling."""
    r = json.loads(json.dumps(report))
    r["milestone_id"] = "M-EAR-1/head-regularization-audit"
    r["variant"] = variant_name
    r["cycle"] = 23
    r["c2_tau_threshold_prime"] = C2_TAU_THRESHOLD
    return r


def _main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--epochs", type=int, default=200)
    args = ap.parse_args(argv)
    run_all(out_dir=args.out_dir, epochs=args.epochs)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
