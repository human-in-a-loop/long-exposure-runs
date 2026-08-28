"""Diagnostic — inspect per-recipe predictions."""
import json
import numpy as np

r = json.load(open("data/ear/stability_audit/stability_report.json"))
prs = r["per_recipe"]
p2 = prs[2]["predicted_ranks"]
p6 = prs[6]["predicted_ranks"]
print("r2 preds:", p2[:20])
print("r6 preds:", p6[:20])
print("identical preds?", p2 == p6)
y2 = [prs[2]["labels_by_clip"][c] for c in r["clip_ids"]]
y6 = [prs[6]["labels_by_clip"][c] for c in r["clip_ids"]]
print("y2==y6?", y2 == y6)
print("r2 y:", y2[:20])
print("r6 y:", y6[:20])
print("unique preds r2:", np.unique(p2, return_counts=True))
print("unique preds r6:", np.unique(p6, return_counts=True))
