#!/usr/bin/env /usr/bin/python3
# RC10 Drums v2 — per-song 3-component GMM classifier with multi-label emission.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-0
# milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-v2
import sys
import numpy as np
from sklearn.mixture import GaussianMixture  # PRNG allowlist: random_state=0
from sklearn.preprocessing import StandardScaler

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"interpreter guard: expected /usr/bin/python3, got {sys.executable}")

KICK, SNARE, HAT = 36, 38, 42
LABEL_TO_PITCH = {"kick": KICK, "snare": SNARE, "hat": HAT}
POSTERIOR_THRESHOLD = 0.35


def fit_and_label(features, onsets_s):
    """Fit per-song 3-component GMM on standardized features; map by
    ascending mean centroid on ORIGINAL centroid column.

    Returns dict with keys: cluster_to_label, posteriors, features_raw,
    features_std, class_pitches_by_onset, notes (multi-label), fallback_reason.
    """
    N = features.shape[0]
    result = {
        "n_onsets": int(N),
        "cluster_to_label": None,
        "cluster_mean_centroid_hz": None,
        "posteriors": None,
        "notes": [],
        "fallback_reason": None,
    }

    if N < 3:
        # too few onsets to fit 3 components — fallback
        result["fallback_reason"] = f"n_onsets={N}<3"
        for k, t in enumerate(onsets_s):
            # fallback to kick (matches c54 v1 collapsed behavior)
            result["notes"].append({
                "onset_s": float(t),
                "duration_s": 0.15,
                "labels": ["kick"],
                "posteriors": {"kick": 1.0, "snare": 0.0, "hat": 0.0},
                "velocity": 90,
            })
        return result

    scaler = StandardScaler().fit(features)
    X = scaler.transform(features)

    gmm = GaussianMixture(
        n_components=3, covariance_type="diag", random_state=0,
        max_iter=100, tol=1e-4, init_params="kmeans",
    )
    try:
        gmm.fit(X)
    except Exception as e:
        result["fallback_reason"] = f"gmm_fit_error:{type(e).__name__}"
        for k, t in enumerate(onsets_s):
            result["notes"].append({
                "onset_s": float(t),
                "duration_s": 0.15,
                "labels": ["kick"],
                "posteriors": {"kick": 1.0, "snare": 0.0, "hat": 0.0},
                "velocity": 90,
            })
        return result

    # Cluster means on ORIGINAL centroid column, computed via per-cluster
    # weighted assignment of hard-labeled points (avoids inversion of scaler).
    hard = gmm.predict(X)
    original_centroids = features[:, 0]
    cluster_mean_c = []
    for c in range(3):
        m = hard == c
        if m.any():
            cluster_mean_c.append(float(original_centroids[m].mean()))
        else:
            # empty cluster — fall back to scaler-inverted mean centroid
            inv = scaler.inverse_transform(gmm.means_)
            cluster_mean_c.append(float(inv[c, 0]))

    # Detect strict tie (two clusters have identical mean centroid) → fallback
    sorted_means = sorted(cluster_mean_c)
    if any(abs(sorted_means[i + 1] - sorted_means[i]) < 1e-9 for i in range(2)):
        result["fallback_reason"] = "centroid_tie"
        for k, t in enumerate(onsets_s):
            result["notes"].append({
                "onset_s": float(t),
                "duration_s": 0.15,
                "labels": ["kick"],
                "posteriors": {"kick": 1.0, "snare": 0.0, "hat": 0.0},
                "velocity": 90,
            })
        return result

    # Map clusters ascending by centroid → kick, snare, hat
    order = np.argsort(cluster_mean_c)  # deterministic
    cluster_to_label = {int(order[0]): "kick", int(order[1]): "snare", int(order[2]): "hat"}

    post = gmm.predict_proba(X)  # (N, 3)
    result["cluster_to_label"] = cluster_to_label
    result["cluster_mean_centroid_hz"] = {
        int(c): float(cluster_mean_c[c]) for c in range(3)
    }
    # Sorted per-cluster centroid for gate G4:
    result["median_centroid_by_label"] = {}

    per_onset_labels = []
    for k, t in enumerate(onsets_s):
        p_per_label = {"kick": 0.0, "snare": 0.0, "hat": 0.0}
        for c in range(3):
            lab = cluster_to_label[c]
            p_per_label[lab] += float(post[k, c])
        labels = [lab for lab, p in p_per_label.items() if p >= POSTERIOR_THRESHOLD]
        if not labels:
            # numerical safety — take argmax
            labels = [max(p_per_label.items(), key=lambda kv: kv[1])[0]]
        result["notes"].append({
            "onset_s": float(t),
            "duration_s": 0.15,
            "labels": sorted(labels),
            "posteriors": {k2: round(v, 6) for k2, v in p_per_label.items()},
            "velocity": 90,
        })
        per_onset_labels.append(labels)

    # Median centroid by (primary) label — computed on ORIGINAL centroid
    # column using ALL onsets whose primary label matches.
    for lab in ("kick", "snare", "hat"):
        primary_c = [
            int(hard[k]) for k in range(N)
            if lab == max(
                {"kick": 0.0, "snare": 0.0, "hat": 0.0} | {  # noqa: RUF005
                    cluster_to_label[c]: float(post[k, c]) for c in range(3)
                },
                key=lambda kv: 0.0,  # placeholder; superseded by explicit primary below
            )
        ]
        # simpler: primary is the highest-posterior label
        primary_c = []
        for k in range(N):
            per_lab = {"kick": 0.0, "snare": 0.0, "hat": 0.0}
            for c in range(3):
                per_lab[cluster_to_label[c]] += float(post[k, c])
            top = max(per_lab.items(), key=lambda kv: kv[1])[0]
            if top == lab:
                primary_c.append(float(original_centroids[k]))
        if primary_c:
            result["median_centroid_by_label"][lab] = float(np.median(primary_c))
        else:
            result["median_centroid_by_label"][lab] = None

    return result
