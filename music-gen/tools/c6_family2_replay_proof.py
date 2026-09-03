#!/usr/bin/env -S /usr/bin/python3
"""Emit family-2 replay proof for bass_family2_v1.json (byte-det ×2)."""
import hashlib, json, os, sys, tempfile, time
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
from scripts.sound_match.replay_family2 import replay_family2

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

PROF_DIR = REPO / "data/v4/profiles/31a164f845f8e27e"
prof = json.loads((PROF_DIR / "bass_family2_v1.json").read_text())
midi = REPO / "data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid"

t0 = time.time()
with tempfile.TemporaryDirectory(prefix="v4_family2_r1_") as td1, \
     tempfile.TemporaryDirectory(prefix="v4_family2_r2_") as td2:
    w1 = Path(td1) / "render.wav"
    w2 = Path(td2) / "render.wav"
    s1 = replay_family2(prof, midi, w1)
    s2 = replay_family2(prof, midi, w2)
    verdict = "REPLAY_PROOF_HOLDS" if s1 == s2 else "REPLAY_PROOF_FAILS"

env_pin_body = json.dumps({k: os.environ.get(k) for k in _PINS},
                          sort_keys=True, separators=(",", ":")).encode("utf-8")
env_pin_sha = hashlib.sha256(env_pin_body).hexdigest()

report = {
    "verdict": verdict,
    "run1_sha256": s1,
    "run2_sha256": s2,
    "midi_path": str(midi),
    "midi_sha256": sha(midi),
    "env_pin_sha256": env_pin_sha,
    "env_pins": {k: os.environ.get(k) for k in _PINS},
    "profile_id": prof["profile_id"],
    "render_family": prof["render_family"],
    "wall_seconds": time.time() - t0,
}
out = PROF_DIR / "bass_family2_v1.replay_proof.json"
out.write_text(json.dumps(report, sort_keys=True, indent=2))
print(json.dumps(report, sort_keys=True, indent=2))
if verdict != "REPLAY_PROOF_HOLDS":
    sys.exit(1)
