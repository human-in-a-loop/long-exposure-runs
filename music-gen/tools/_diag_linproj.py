"""Diagnose why r2 == r3."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
import numpy as np
from scripts.ear.stability_audit import load_features
from scripts.ear.synthetic_labels import _linear_coefs, _rank_to_7bins

clip_ids, features, X = load_features(Path("data/classifier/valset/valset_manifest.tsv"))
Xf = X.astype(np.float64)
print("X shape", Xf.shape, "nan?", np.isnan(Xf).any(), "std_min", Xf.std(axis=0).min())

# How many axes have effectively-zero std?
sd = Xf.std(axis=0)
print("axes with std < 1e-6:", (sd < 1e-6).sum())
print("axes with std < 1e-3:", (sd < 1e-3).sum())

mu = Xf.mean(axis=0, keepdims=True)
Xz = (Xf - mu) / (Xf.std(axis=0, keepdims=True) + 1e-8)

for salt in ("stab-audit-2", "stab-audit-3"):
    c = _linear_coefs(salt, Xf.shape[1])
    scores = Xz @ c
    print(f"{salt} scores[:5]={scores[:5]}  norm_c={np.linalg.norm(c):.4f}")
    # Rank
    ranked = _rank_to_7bins({cid: float(scores[i]) for i, cid in enumerate(clip_ids)}, salt)
    yv = np.array([ranked[c_] for c_ in clip_ids])
    print(f"   labels[:20]={yv[:20]}")

# Compare coef vectors
c2 = _linear_coefs("stab-audit-2", Xf.shape[1])
c3 = _linear_coefs("stab-audit-3", Xf.shape[1])
print("coef corr:", np.corrcoef(c2, c3)[0,1])
print("coef Hamming sign:", (np.sign(c2) != np.sign(c3)).mean())

# Are scores actually identical?
s2 = Xz @ c2
s3 = Xz @ c3
print("scores corr:", np.corrcoef(s2, s3)[0,1])
print("scores rank same?", (np.argsort(s2) == np.argsort(s3)).all())
