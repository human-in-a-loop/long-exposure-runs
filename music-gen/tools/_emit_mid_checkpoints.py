"""One-shot mid-cycle ledger event emitter for M-EAR-1/head-regularization-audit."""
# created: 2026-08-28T20:55:00Z  cycle: 23  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 3fbd8c1ab57c)  milestone: M-EAR-1/head-regularization-audit
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")
from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402

WS = Path("/home/user/long-exposure-runs/music-gen")


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


EVENTS = [
    {
        "milestone_id": "M-EAR-1/head-regularization-audit",
        "status": "in-progress",
        "confidence": {"level": "medium",
                       "rationale": "Three variant modules built; PCA basis pinned; ridge single-recipe smoke matches expected shape.",
                       "assessor": "worker"},
        "narrative": ("Built scripts/ear/_variant_core.py plus model_v2_ridge, model_v2_bottleneck, and "
                      "model_v2_frozen_projector. PCA-64 basis fit deterministically via "
                      "numpy.linalg.svd(full_matrices=True) on the 55-clip cache's 2048-D PANNs component "
                      "(mean-centered) and pinned at data/ear/head_regularization_audit/pca_basis.npz with "
                      "SHA-256 sidecar. Ridge single-recipe smoke on stab-audit-0 = mean-MAE 1.82 vs "
                      "baseline cycle-22 clone-2 1.98, indicating the higher-dropout + wd=1e-2 "
                      "regularization exerts a measurable effect."),
        "assessment": "variant heads and PCA basis ready; full 3-variant x 2-run audit next.",
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 23,
        "agent": "worker",
        "artifacts": [
            "scripts/ear/_variant_core.py",
            "scripts/ear/model_v2_ridge.py",
            "scripts/ear/model_v2_bottleneck.py",
            "scripts/ear/model_v2_frozen_projector.py",
            "data/ear/head_regularization_audit/pca_basis.npz",
            "data/ear/head_regularization_audit/pca_basis.sha256",
        ],
    },
    {
        "milestone_id": "M-EAR-1/head-regularization-audit",
        "status": "in-progress",
        "confidence": {"level": "medium",
                       "rationale": "All three variants' first-run (tau, MAE) tuples measured; harness anchor SHAs still match cycle-22 recorded values.",
                       "assessor": "worker"},
        "narrative": ("All three variants first-run complete under the UNCHANGED cycle-22 stability harness. "
                      "Frontier tuples (mean tau, median MAE): ridge (0.0766, 1.391); bottleneck (0.0605, 1.455); "
                      "frozen_projector (0.0612, 1.573); cycle-6 baseline reference (0.059, 0.891). Harness "
                      "anchor SHAs verified match cycle-22 clone-2 (stability_audit.py=b1ce5137..., "
                      "synthetic_labels.py=b71f194e..., stability_metrics.py=6a5cb518...). Ridge marginally "
                      "lifts tau above baseline (0.077 vs 0.059) but all three variants sit ~5x below the "
                      "frozen C2' threshold of 0.4."),
        "assessment": "first-run tuples captured; running byte-determinism verification.",
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 23,
        "agent": "worker",
        "artifacts": [
            "data/ear/head_regularization_audit/_run1_ridge/stability_report.json",
            "data/ear/head_regularization_audit/_run1_bottleneck/stability_report.json",
            "data/ear/head_regularization_audit/_run1_frozen_projector/stability_report.json",
            "data/ear/head_regularization_audit/harness_anchor_manifest.json",
        ],
    },
    {
        "milestone_id": "M-EAR-1/head-regularization-audit",
        "status": "in-progress",
        "confidence": {"level": "medium",
                       "rationale": "Byte-determinism × 2 confirmed per variant; feature-cache SHA-manifest unchanged pre/post.",
                       "assessor": "worker"},
        "narrative": ("Second byte-determinism run agrees per variant. Per-variant (run1 SHA, run2 SHA): "
                      "ridge (be9a750ed169adfa..., be9a750ed169adfa...); bottleneck (f224157c7b571ce3..., "
                      "f224157c7b571ce3...); frozen_projector (5dd1c9dabfcee1cd..., 5dd1c9dabfcee1cd...). "
                      "All three C3' PASS. Feature-cache SHA-manifest byte-identical before/after audit."),
        "assessment": "byte-determinism x 2 verified; cross-branch S34 + tests + report next.",
        "run_id": "run-2026-08-28T040704Z",
        "cycle": 23,
        "agent": "worker",
        "artifacts": [
            "data/ear/head_regularization_audit/stability_report_v2_ridge.json",
            "data/ear/head_regularization_audit/stability_report_v2_bottleneck.json",
            "data/ear/head_regularization_audit/stability_report_v2_frozen_projector.json",
            "data/ear/head_regularization_audit/feature_cache_pre_post_shas.json",
            "data/ear/head_regularization_audit/variant_verdicts.json",
        ],
    },
]


def main() -> int:
    for e in EVENTS:
        event = dict(e)
        event["ts"] = _ts()
        append_ledger_event(WS, event)
        print("appended", event["milestone_id"], event["assessment"][:60])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
