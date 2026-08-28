"""Check label diversity across the 10 recipes without training."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
import numpy as np
from scripts.ear.stability_audit import load_features
from scripts.ear.synthetic_labels import RECIPES, apply_recipe

clip_ids, features, X = load_features(Path("data/classifier/valset/valset_manifest.tsv"))
print(f"{len(clip_ids)} clips, feat_dim={X.shape[1]}")

labels = []
for r in RECIPES:
    y = apply_recipe(r, features)
    yv = np.array([y[c] for c in clip_ids])
    labels.append(yv)
    print(f"r{r['idx']} {r['family']:20s} salt={r['salt']:16s} hist={np.bincount(yv, minlength=8)[1:]}")

# Pairwise Hamming distance (fraction of differing labels)
n = len(labels)
print("\nPairwise Hamming distance (fraction differing):")
for i in range(n):
    row = []
    for j in range(n):
        if i == j:
            row.append("  --  ")
        else:
            frac = float(np.mean(labels[i] != labels[j]))
            row.append(f"{frac:.2f}")
    print(f"r{i}: " + " ".join(row))

# Confirm no two recipes produce identical labels
for i in range(n):
    for j in range(i+1, n):
        if np.array_equal(labels[i], labels[j]):
            print(f"WARNING: r{i} == r{j} exactly")
print("\nDeterminism check: re-apply and compare")
for r in RECIPES[:3]:
    y1 = apply_recipe(r, features)
    y2 = apply_recipe(r, features)
    assert y1 == y2, f"NON-DETERMINISTIC recipe {r['idx']}"
print("determinism OK")
