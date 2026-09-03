#!/usr/bin/env -S /usr/bin/python3
"""Compute family-2 panel + emit verdict."""
import hashlib, json, os, sys
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
    "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for k, v in _PINS.items():
    os.environ.setdefault(k, v)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from scripts.sound_match.objective import score_pair

PROF_DIR = REPO / "data/v4/profiles/31a164f845f8e27e"
REF = REPO / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav"
CAND = PROF_DIR / "bass_family2_v1/render.wav"

panel = score_pair(CAND, REF)
prof = json.loads((PROF_DIR / "bass_family2_v1.json").read_text())
proof = json.loads((PROF_DIR / "bass_family2_v1.replay_proof.json").read_text())

emb = float(panel.get("embedding_cos_vggish", float("nan")))
all_finite = all(
    isinstance(panel.get(k), (int, float)) and panel.get(k) == panel.get(k)  # nan check
    for k in ["mel_l1_db", "spectral_centroid_rmse_hz", "embedding_cos_vggish"]
)
proof_holds = proof["verdict"] == "REPLAY_PROOF_HOLDS"

if all_finite and proof_holds and emb >= 0.60:
    verdict = "FAMILY2_CONFIRMED"
elif all_finite and proof_holds and emb <= 0.40:
    verdict = "FAMILY2_RULED_OUT"
else:
    verdict = "FAMILY2_INDETERMINATE"

rubric_sha = hashlib.sha256(
    (REPO / "docs/sound_match/family2_stem_sampled_builder_c6_rubric.md").read_bytes()
).hexdigest()
rubric_pinned = (PROF_DIR / "family2_builder_c6_rubric_hash.txt").read_text().strip()
assert rubric_sha == rubric_pinned, f"rubric drift {rubric_sha} != {rubric_pinned}"

out = {
    "verdict": verdict,
    "panel": {
        "mel_l1_db": panel.get("mel_l1_db"),
        "spectral_centroid_rmse_hz": panel.get("spectral_centroid_rmse_hz"),
        "embedding_cos_vggish": panel.get("embedding_cos_vggish"),
    },
    "rubric_hash": rubric_sha,
    "render_family": "stem_sampled_v1",
    "profile_id": prof["profile_id"],
    "replay_proof_status": proof["verdict"],
    "env_pin_sha256": proof["env_pin_sha256"],
    "comparison_vs_sf2": {
        "sf2_top1_embedding_cos": 0.4946,
        "family2_embedding_cos": panel.get("embedding_cos_vggish"),
        "delta": float(panel.get("embedding_cos_vggish", 0.0)) - 0.4946,
    },
    "cycle": 6,
}
p = PROF_DIR / "bass_family2_verdict.json"
p.write_text(json.dumps(out, sort_keys=True, indent=2))
print(json.dumps(out, sort_keys=True, indent=2))
