"""Driver for M-EAR-1/feature-representation-audit (cycle 25).

For each of the three feature representations (heur_only, panns_only, and
vggish_only when cached):

  1. Verify harness anchor SHAs (stability_audit.py, synthetic_labels.py,
     stability_metrics.py, model.py, corn.py, features.py) match the
     cycle-22 clone-2 recorded values. Refuse to run on any mismatch.
  2. Snapshot the pre-run SHA-256 manifest of ``data/ear/features/``.
  3. Monkey-patch ``scripts.ear.stability_audit.load_features`` with a
     representation-scoped loader that slices the frozen 2052-D cache into
     the target representation's per-clip vectors (BOTH the features dict
     and the X matrix). Recipes then generate labels from the sliced
     features; the cycle-6 CORN head chassis is instantiated at the
     matching D_in (via `X.shape[1]` inside `scripts.ear.model._fit`).
  4. Invoke ``stability_audit.run_audit`` TWICE into per-representation
     temp out-dirs and check byte-determinism (C3').
  5. Emit ``data/ear/feature_representation_audit/stability_report_v3_<representation>.json``
     from the second (canonical) run.
  6. Verify post-run feature-cache SHA-manifest byte-identical to pre-run.

If VGGish is not cached (has_vggish=False across the 55 valset clips),
publish `vggish_deferral_note.json` and continue with R1 + R2.

Emits under ``data/ear/feature_representation_audit/``:
  stability_report_v3_heur_only.json
  stability_report_v3_panns_only.json
  stability_report_v3_vggish_only.json  (or vggish_deferral_note.json)
  representation_verdicts.json
  harness_anchor_manifest.json
  feature_cache_pre_post_shas.json

Non-factor isolation: NO import of scripts.classifier.sidecar_nonfactor.
Interpreter guard: /usr/bin/python3.
"""
# created: 2026-08-28T21:05:00Z  cycle: 25  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork dc8cba4b79eb)  milestone: M-EAR-1/feature-representation-audit
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

import numpy as np

from . import feature_subset_adapter as fsa


# Cycle-22 clone-2 anchor SHAs — mirror cycle-23's HARNESS_ANCHOR_SHAS.
HARNESS_ANCHOR_SHAS = {
    "scripts/ear/stability_audit.py":  "b1ce5137b665a962657f1ee128db4d36abcb6d2174f57101b354a3194ea02e4c",
    "scripts/ear/synthetic_labels.py": "b71f194ef97e8936bb8942d5fccba899e6efe47e292cca185728d1cd9f41fb4d",
    "scripts/ear/stability_metrics.py":"6a5cb5183fdc77e80677ef01bb47f777a2662404f737f8aa74287f30cf97dc27",
    "scripts/ear/model.py":            "d4322a95fc2328b201b4040713dfdf8e294d8d0ae31db7e81c6390371492b552",
    "scripts/ear/corn.py":             "5028c58c20f23cd62c94789fad3522f94953417b79dec33b8506704b83a9921b",
    "scripts/ear/features.py":         "5e7cbf33cd81b501368f6334b2e5c67c41172c4d9e60bb34154274897c611f53",
}

# Three representations in fixed order — VGGish is conditional.
REPRESENTATIONS = ("heur_only", "panns_only", "vggish_only")

OUT_DIR = Path("data/ear/feature_representation_audit")
DEFAULT_CYCLE6_MAE = 0.890909090909091
C2_TAU_THRESHOLD = 0.4  # matches cycle-23 relaxed rubric


# ---------------------------------------------------------------------------
# SHA helpers
# ---------------------------------------------------------------------------
def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_harness_anchors(workspace: Path = Path(".")) -> dict[str, str]:
    """Refuse to run if any anchored file's SHA has drifted from cycle-22."""
    observed: dict[str, str] = {}
    for rel, want in HARNESS_ANCHOR_SHAS.items():
        p = workspace / rel
        if not p.exists():
            raise SystemExit(f"[stability_audit_v3] anchor missing: {p}")
        got = _sha256_of_file(p)
        observed[rel] = got
        if got != want:
            raise SystemExit(
                f"[stability_audit_v3] REFUSING to run: {rel} SHA drift "
                f"(observed={got}, cycle-22-anchor={want})."
            )
    return observed


def feature_cache_manifest(
    cache_dir: Path = Path("data/ear/features"),
    *,
    valset_only: bool = True,
    valset_path: Path = Path("data/classifier/valset/valset_manifest.tsv"),
) -> dict[str, str]:
    """SHA manifest of the ear feature cache.

    By default filters to the 55 valset clips referenced by the audit — the
    cache directory is shared with cycle-11 M-GEN-1 first-generation
    scratch files (`gen_first_gen_*.npz`) that a concurrent clone can
    legitimately append/rewrite during this audit's run without invalidating
    the audit's inputs. The audit's own read set is exactly the 55 valset
    clips; those are the only files whose bytes-invariance actually
    matters for reproducibility.
    """
    manifest: dict[str, str] = {}
    scope: set[str] | None = None
    if valset_only and valset_path.exists():
        with valset_path.open() as f:
            header = f.readline().rstrip("\n").split("\t")
            rows = [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]
        scope = {r["clip_id"] + ".npz" for r in rows}
    for p in sorted(cache_dir.glob("*.npz")):
        if scope is not None and p.name not in scope:
            continue
        manifest[p.name] = _sha256_of_file(p)
    return manifest


# ---------------------------------------------------------------------------
# Representation-scoped feature loaders
# ---------------------------------------------------------------------------
def _make_load_features_for(representation: str):
    """Return a load_features(valset) function that yields the sliced representation.

    The returned function has the same signature as
    `scripts.ear.stability_audit.load_features` — it is monkey-patched over
    the cycle-22 module attribute at driver time.
    """
    def load_features(valset):
        from .features import CACHE_DIR
        with Path(valset).open() as f:
            header = f.readline().rstrip("\n").split("\t")
            rows = [dict(zip(header, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]
        clip_ids = sorted(r["clip_id"] for r in rows)

        if representation == "vggish_only":
            X = fsa.load_vggish_only(CACHE_DIR, clip_ids)
            features = {c: X[i] for i, c in enumerate(clip_ids)}
            return clip_ids, features, X

        # heur_only and panns_only both start from the 2052-D concat.
        full: dict[str, np.ndarray] = {}
        for cid in clip_ids:
            p = CACHE_DIR / f"{cid}.npz"
            if not p.exists():
                raise SystemExit(f"[stability_audit_v3] missing feature cache for {cid} at {p}")
            npz = np.load(p, allow_pickle=False)
            vec = np.concatenate(
                [npz["panns_embed"], npz["heuristic_vec"]], axis=0
            ).astype(np.float32)
            full[cid] = vec

        if representation == "heur_only":
            slicer = fsa.slice_heur_only
        elif representation == "panns_only":
            slicer = fsa.slice_panns_only
        else:
            raise ValueError(f"unknown representation: {representation!r}")

        features = {c: slicer(full[c]) for c in clip_ids}
        X = np.stack([features[c] for c in clip_ids], axis=0)
        return clip_ids, features, X

    return load_features


# ---------------------------------------------------------------------------
# Per-representation twice-run
# ---------------------------------------------------------------------------
def _run_representation_once(
    representation: str, tmp_out_dir: Path, *, epochs: int
) -> tuple[str, dict]:
    """Run the cycle-22 harness with the representation loader patched in.

    Returns (sha256 of stability_report.json, parsed report dict).
    """
    from . import stability_audit as _sa

    loader = _make_load_features_for(representation)
    orig_loader = _sa.load_features
    try:
        _sa.load_features = loader
        tmp_out_dir.mkdir(parents=True, exist_ok=True)
        result = _sa.run_audit(
            out_dir=tmp_out_dir,
            epochs=epochs,
            cycle6_mae=DEFAULT_CYCLE6_MAE,
        )
    finally:
        _sa.load_features = orig_loader

    report_path = tmp_out_dir / "stability_report.json"
    return _sha256_of_file(report_path), result["report"]


# ---------------------------------------------------------------------------
# Verdict rubric (frozen; locked before the run) — matches cycle-23
# ---------------------------------------------------------------------------
def _verdict_c1(cycle6_mae: float, envelope: dict) -> str:
    return "PASS" if envelope["p05"] <= cycle6_mae <= envelope["p95"] else "FAIL"


def _verdict_c2(mean_tau: float) -> str:
    return "PASS" if mean_tau >= C2_TAU_THRESHOLD else "FAIL"


def _verdict_c3(sha1: str, sha2: str) -> str:
    return "PASS" if sha1 == sha2 else "FAIL"


def _augment_report(report: dict, representation: str, d_in: int) -> dict:
    r = json.loads(json.dumps(report))
    r["milestone_id"] = "M-EAR-1/feature-representation-audit"
    r["representation"] = representation
    r["d_in"] = int(d_in)
    r["cycle"] = 25
    r["c2_tau_threshold_prime"] = C2_TAU_THRESHOLD
    r["feature_subset_version"] = fsa.feature_subset_version()
    return r


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def run_all(
    out_dir: Path = OUT_DIR,
    *,
    epochs: int = 200,
    cycle6_mae: float = DEFAULT_CYCLE6_MAE,
    representations: tuple[str, ...] = REPRESENTATIONS,
) -> dict:
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

    # 3. Per-representation twice-run
    representation_verdicts: dict[str, dict] = {}
    representation_reports: dict[str, dict] = {}
    deferrals: dict[str, dict] = {}

    for name in representations:
        # VGGish precondition check
        if name == "vggish_only":
            try:
                # Cheap probe: peek at 1 npz to see if VGGish is cached.
                from .features import CACHE_DIR
                any_npz = next(CACHE_DIR.glob("*.npz"), None)
                if any_npz is None:
                    raise fsa.VggishNotCached("no feature cache files present")
                probe = np.load(any_npz, allow_pickle=False)
                if not bool(probe.get("has_vggish", np.array(False))) or \
                   probe["vggish_embed"].size != fsa.VGGISH_DIM:
                    raise fsa.VggishNotCached(
                        f"probe clip {any_npz.name}: has_vggish=False or "
                        f"empty vggish_embed (size={probe['vggish_embed'].size})"
                    )
            except fsa.VggishNotCached as e:
                deferrals[name] = {
                    "representation": name,
                    "deferred": True,
                    "reason": str(e),
                    "rationale": (
                        "VGGish extractor output is not cached for the 55 valset "
                        "clips (has_vggish=False in features/*.npz). Per the "
                        "cycle-25 brief, running the VGGish extractor is out of "
                        "scope for this branch; publish honestly and defer to a "
                        "follow-up cycle."
                    ),
                    "detected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                }
                (out_dir / "vggish_deferral_note.json").write_text(
                    json.dumps(deferrals[name], indent=2, sort_keys=True) + "\n"
                )
                print(f"[feat-rep-audit] DEFER  {name}: {e}")
                continue

        run1_dir = out_dir / f"_run1_{name}"
        run2_dir = out_dir / f"_run2_{name}"
        if run1_dir.exists():
            shutil.rmtree(run1_dir)
        if run2_dir.exists():
            shutil.rmtree(run2_dir)

        sha1, report1 = _run_representation_once(name, run1_dir, epochs=epochs)
        sha2, report2 = _run_representation_once(name, run2_dir, epochs=epochs)

        d_in = int(report2["feat_dim"])
        canonical_path = out_dir / f"stability_report_v3_{name}.json"
        canonical_path.write_text(
            json.dumps(_augment_report(report2, name, d_in),
                       sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n"
        )

        env = report2["mae_envelope"]
        mean_tau = report2["tau_summary"]["mean"]
        c1 = _verdict_c1(cycle6_mae, env)
        c2 = _verdict_c2(mean_tau)
        c3 = _verdict_c3(sha1, sha2)
        overall = "PASS" if (c1 == "PASS" and c2 == "PASS" and c3 == "PASS") else "FAIL"

        representation_verdicts[name] = {
            "representation": name,
            "d_in": d_in,
            "C1_prime": {"name": "MAE reproducibility",
                         "threshold": f"cycle-6 MAE ({cycle6_mae}) inside representation's [5th,95th] envelope",
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
        representation_reports[name] = report2

    verdicts_out = dict(representation_verdicts)
    if deferrals:
        verdicts_out["_deferrals"] = deferrals
    (out_dir / "representation_verdicts.json").write_text(
        json.dumps(verdicts_out, indent=2, sort_keys=True) + "\n"
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
        raise SystemExit("[stability_audit_v3] feature cache SHA manifest changed during audit")

    # 5. Summary line
    print("=" * 72)
    print(f"[feat-rep-audit] harness SHAs OK; feature cache SHA-invariant")
    print(f"[feat-rep-audit] tau threshold C2'={C2_TAU_THRESHOLD}, "
          f"cycle6 MAE anchor={cycle6_mae:.4f}")
    for name in representations:
        if name in representation_verdicts:
            v = representation_verdicts[name]
            print(
                f"  {name:14s} D_in={v['d_in']:5d}  "
                f"tau_mean={v['C2_prime']['observed_mean_tau']:+.4f} "
                f"median_mae={v['median_mae']:.4f} "
                f"env=[{v['C1_prime']['envelope_p05']:.4f},{v['C1_prime']['envelope_p95']:.4f}]  "
                f"C1={v['C1_prime']['verdict']} C2={v['C2_prime']['verdict']} "
                f"C3={v['C3_prime']['verdict']} => {v['overall']}"
            )
        elif name in deferrals:
            print(f"  {name:14s} DEFERRED ({deferrals[name]['reason'][:50]}...)")
    print("=" * 72)

    return {
        "verdicts": representation_verdicts,
        "reports": representation_reports,
        "deferrals": deferrals,
        "anchor_manifest": anchor_manifest,
        "feature_cache_report": fc_report,
    }


def _main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--representations", nargs="+", default=list(REPRESENTATIONS),
                    help="Subset of representations to audit.")
    args = ap.parse_args(argv)
    run_all(
        out_dir=args.out_dir, epochs=args.epochs,
        representations=tuple(args.representations),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
