#!/usr/bin/env python3
"""End-to-end driver: read observations.json, fit, verdict, write artifacts.

Idempotent + analytic; safe to rerun.

Usage:
  PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure /usr/bin/python3 \
      scripts/analysis/run_bp_fit.py

Reads:  data/collision_model/observations.json
Writes: data/collision_model/bp_fit_results.json
        data/collision_model/verdict.json
        data/collision_model/per_batch_predictions.tsv
        data/collision_model/per_rule_type_v6.tsv
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.analysis import collision_model_bp as bp  # noqa: E402
from scripts.analysis import collision_model_verdict as verdict_mod  # noqa: E402


DATA_DIR = ROOT / "data" / "collision_model"


def write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


def write_per_batch_tsv(fit: dict, path: pathlib.Path) -> None:
    hdr = "batch_id\tN\tsampler\tK_H\tK_R\tK_M\tK_F\tK_A\tpredicted_pure\tpredicted_scaled\tobserved\tresidual_pure\tresidual_scaled\n"
    lines = [hdr]
    for b in fit["per_batch"]:
        K = b["K_by_rule_type"]
        pp = b["predicted_total_pure"]
        ps = b.get("predicted_total_scaled", 0.0)
        obs = b["observed_total"]
        lines.append(
            f"{b['batch_id']}\t{b['N']}\t{b['sampler']}\t{K.get('H',0)}\t{K.get('R',0)}\t{K.get('M',0)}\t{K.get('F',0)}\t{K.get('A',0)}\t{pp:.4f}\t{ps:.4f}\t{obs}\t{obs - pp:.4f}\t{obs - ps:.4f}\n"
        )
    path.write_text("".join(lines))


def write_shape_tsv(fit: dict, path: pathlib.Path, batch_id: str = "batch_v6") -> None:
    shape = fit.get("shape_fits", {}).get(batch_id)
    if not shape:
        return
    lines = ["rule_type\tK\tobserved\tpredicted_pure\tpredicted_scaled\tresidual_scaled\n"]
    for r, obs, pp, ps in zip(
        shape["rule_types"], shape["observed"], shape["predicted_pure"], shape["predicted_scaled"]
    ):
        # Find K from batch entry
        K_by_type = next(
            (b["K_by_rule_type"] for b in fit["per_batch"] if b["batch_id"] == batch_id), {}
        )
        Kr = K_by_type.get(r, 0)
        lines.append(f"{r}\t{Kr}\t{obs}\t{pp:.4f}\t{ps:.4f}\t{obs - ps:.4f}\n")
    path.write_text("".join(lines))


def main() -> int:
    obs = json.loads((DATA_DIR / "observations.json").read_text())
    fit = bp.fit_bp(obs)
    write_json(DATA_DIR / "bp_fit_results.json", fit)

    v = verdict_mod.apply_verdict(fit, shape_batch_id="batch_v6")
    write_json(DATA_DIR / "verdict.json", v)

    write_per_batch_tsv(fit, DATA_DIR / "per_batch_predictions.tsv")
    write_shape_tsv(fit, DATA_DIR / "per_rule_type_v6.tsv", "batch_v6")

    print(f"verdict={v['verdict']}  shape={v['shape_verdict']}  alpha={v['alpha_hat']}  r2_scaled={v['r2_scaled']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
