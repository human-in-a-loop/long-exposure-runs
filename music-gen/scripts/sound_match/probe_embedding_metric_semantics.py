#!/usr/bin/python3
# ---
# created: 2026-09-04T00:00:00Z
# cycle: 16
# run_id: run-2026-09-04T110000Z
# agent: worker
# milestone: _infra/embedding-metric-semantics-diagnosed-c16
# ---
"""c16 Track 1 CRITICAL diagnostic probe.

Empirically settles whether the panel's `embedding_cosine_distance` field
(propagated into profile/verdict JSONs as `embedding_cos_vggish`) is a
distance (lower=better) or a similarity (higher=better).

Deterministic; no PRNG; no `sidecar_nonfactor`; no VST3 state APIs.
Reads reference bass stem READ-ONLY. Imports embedding_panel READ-ONLY.

Output:
  data/v4/diagnostics/embedding_metric_semantics.json
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

# Env pins BEFORE any observed import
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

# Interpreter guard
if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(
        f"probe requires /usr/bin/python3 (got {sys.executable})"
    )

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

# READ-ONLY imports from c14 anchor embedding_panel
from scripts.texture.embedding_panel import (  # noqa: E402
    embedding_cosine_distance,
    get_rung,
)


ENV_PIN_KEYS = [
    "PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
]


def _env_pin_sha256() -> str:
    payload = {k: os.environ.get(k, "") for k in ENV_PIN_KEYS}
    canon = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _sine(freq_hz: float, dur_s: float, sr: int) -> np.ndarray:
    n = int(round(dur_s * sr))
    t = np.arange(n, dtype=np.float64) / float(sr)
    return (np.sin(2.0 * np.pi * float(freq_hz) * t) * 0.5).astype(np.float32)


def _load_stem_slice(
    stem_name: str, sr_out: int, dur_s: float = 6.0
) -> np.ndarray:
    stem_wav = ROOT / "data" / "v3" / "deliveries" / "31a164f845f8e27e" / \
        "cert_run1" / "stems_6s" / f"{stem_name}.wav"
    y, sr = sf.read(str(stem_wav), always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    y = y.astype(np.float32)
    if sr != sr_out:
        raise RuntimeError(
            f"{stem_name} stem sr={sr} != expected {sr_out}"
        )
    n_target = int(round(dur_s * sr_out))
    if len(y) < n_target:
        raise RuntimeError(
            f"{stem_name} stem too short ({len(y)} < {n_target})"
        )
    return y[:n_target]


def _load_bass_slice(sr_out: int, dur_s: float = 6.0) -> np.ndarray:
    return _load_stem_slice("bass", sr_out, dur_s)


def _interpret(pair_a_dist, pair_c_dist) -> str:
    """Decide by which interpretation matches Pair A and Pair C.

    - Distance semantics predicts: Pair A ~ 0, Pair C > Pair A.
    - Similarity semantics predicts: Pair A ~ 1, Pair C < Pair A.

    Pair A on an identical input is the primary discriminator: distance
    zero and similarity one are decisively different. Pair C serves as
    the secondary ordering check (distinct content should give a value
    farther from identity's value under either interpretation).
    """
    if pair_a_dist is None or pair_c_dist is None:
        return "ambiguous"
    # Identity => distance ~0 or similarity ~1. Threshold at midpoint.
    identity_is_zero = pair_a_dist < 0.10
    identity_is_one = pair_a_dist > 0.90
    # Ordering: distinct-content pair should be farther from identity's
    # value than identity itself.
    c_farther_from_zero = pair_c_dist > pair_a_dist + 0.10
    c_farther_from_one = pair_c_dist < pair_a_dist - 0.10
    if identity_is_zero and c_farther_from_zero:
        return "distance"
    if identity_is_one and c_farther_from_one:
        return "similarity"
    return "ambiguous"


def main(out_path: Path) -> int:
    sr = 44100

    # Pair A: identity (bass slice vs itself)
    bass = _load_bass_slice(sr_out=sr, dur_s=6.0)
    pair_a_dist, rung_a = embedding_cosine_distance(bass, bass.copy(), sr)

    # Pair B: near-identity numerical perturbation
    bass_perturbed = bass + np.full_like(bass, 1e-6, dtype=np.float32)
    pair_b_dist, rung_b = embedding_cosine_distance(bass, bass_perturbed, sr)

    # Pair C: distinct-content — bass stem 6s vs drums stem 6s. Real
    # instrument content is more discriminative for VGGish than pure sines
    # (VGGish embeds sines very tightly). No PRNG; both stems READ-ONLY.
    drums = _load_stem_slice("drums", sr_out=sr, dur_s=6.0)
    pair_c_dist, rung_c = embedding_cosine_distance(bass, drums, sr)

    metric_is = _interpret(pair_a_dist, pair_c_dist)

    result = {
        "schema": "v4_embedding_metric_semantics_diagnostic_v1",
        "cycle": 16,
        "milestone_id": "_infra/embedding-metric-semantics-diagnosed-c16",
        "env_pin_sha256": _env_pin_sha256(),
        "env_pin_keys": ENV_PIN_KEYS,
        "embedding_rung": get_rung(),
        "pair_a_identity": {
            "description": "bass stem 6s vs itself",
            "value": pair_a_dist,
            "rung": rung_a,
            "interpretation_if_distance": (
                "~0.0 (identical → distance zero)"
            ),
            "interpretation_if_similarity": (
                "~1.0 (identical → similarity one)"
            ),
        },
        "pair_b_near_identity": {
            "description": "bass stem 6s vs bass + 1e-6 constant",
            "value": pair_b_dist,
            "rung": rung_b,
            "note": (
                "Numerical self-distance under perceptually imperceptible "
                "perturbation; expected extremely small under either "
                "interpretation."
            ),
        },
        "pair_c_orthogonal": {
            "description": "bass stem 6s vs drums stem 6s (distinct real content)",
            "value": pair_c_dist,
            "rung": rung_c,
            "interpretation_if_distance": (
                "farther from 0 than Pair A (distinct → larger distance)"
            ),
            "interpretation_if_similarity": (
                "farther from 1 than Pair A (distinct → lower similarity)"
            ),
        },
        "metric_is": metric_is,
        "interpretation_consequence_table": {
            "distance": (
                "Field is a distance (lower=better). Verdict thresholds "
                "(≥0.60 CONFIRMED / <0.40 RULED_OUT) as-worded are inverted "
                "in interpretation: they gate as if the value were "
                "similarity. Under corrected reading, RULED_OUT should fire "
                "on distance > 0.60, not < 0.40."
            ),
            "similarity": (
                "Field is a similarity (higher=better). Panel implementation "
                "or objective usage needs `similarity = 1 - distance` "
                "correction to match the wording. Thresholds stand."
            ),
            "ambiguous": (
                "Empirical response did not match either interpretation "
                "cleanly. Further probing required."
            ),
        },
        "escalation_note": (
            "This diagnostic MUST NOT rewrite any prior verdict or "
            "acceptance-fork; Track 2 owns the operator-authority "
            "escalation."
        ),
        "read_only_anchors": {
            "embedding_panel_path": "scripts/texture/embedding_panel.py",
            "objective_path": "scripts/sound_match/objective.py",
            "bass_stem_path": (
                "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/"
                "bass.wav"
            ),
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    print(f"WROTE {out_path}")
    print(f"metric_is={metric_is}")
    print(
        f"pair_a={pair_a_dist!r} pair_b={pair_b_dist!r} "
        f"pair_c={pair_c_dist!r}"
    )
    return 0


if __name__ == "__main__":
    default_out = ROOT / "data" / "v4" / "diagnostics" / \
        "embedding_metric_semantics.json"
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else default_out
    raise SystemExit(main(out))
