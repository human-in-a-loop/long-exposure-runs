"""Summarize the stability_report.json for prose in the audit report."""
import json
import hashlib
from pathlib import Path

R = json.load(open("data/ear/stability_audit/stability_report.json"))
print("SHA report:", hashlib.sha256(Path("data/ear/stability_audit/stability_report.json").read_bytes()).hexdigest())
print("n_recipes:", R["n_recipes"], " n_clips:", R["n_clips"], " feat_dim:", R["feat_dim"])
print("\n--- Per-recipe MAE table ---")
for pr in R["per_recipe"]:
    fold_ma = [f"{x:.3f}" for x in pr["per_fold_mae"]]
    import numpy as np
    print(f"{pr['idx']:>2} | {pr['family']:20s} | {pr['salt']:16s} | mean={pr['mean_mae']:.4f} | std={pr['std_mae']:.4f} | folds={fold_ma}")
print("\n--- MAE envelope ---")
env = R["mae_envelope"]
for k, v in env.items():
    if isinstance(v, (list, dict, bool)):
        print(f"  {k}: {v}")
    else:
        print(f"  {k}: {v:.6f}")
print("\n--- Tau summary ---")
for k, v in R["tau_summary"].items():
    print(f"  {k}: {v}")
print("\n--- Verdicts ---")
for cid, c in R["criteria"].items():
    print(f"  {cid} ({c['name']}): {c['verdict']}")
    for k, v in c.items():
        if k not in ("name", "verdict"):
            print(f"     {k}: {v}")
print("\n--- Top-5 highest band variance clips ---")
sortv = sorted(R["per_clip_band_variance"], key=lambda x: -x["band_variance"])
for row in sortv[:5]:
    print(f"  {row['clip_id']:40s} mean={row['mean_rank']:.2f} var={row['band_variance']:.4f}")
print("\n--- Top-5 lowest band variance clips ---")
for row in sortv[-5:]:
    print(f"  {row['clip_id']:40s} mean={row['mean_rank']:.2f} var={row['band_variance']:.4f}")
# Family-level rollup
from collections import defaultdict
famma = defaultdict(list)
for pr in R["per_recipe"]:
    famma[pr["family"]].append(pr["mean_mae"])
print("\n--- Per-family mean-MAE range ---")
for fam, vs in famma.items():
    import numpy as np
    print(f"  {fam:22s} n={len(vs)} min={min(vs):.3f} mean={np.mean(vs):.3f} max={max(vs):.3f}")
