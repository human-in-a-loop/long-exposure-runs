#!/usr/bin/env -S /usr/bin/python3
"""c6 refresh both sf2 replay proofs post-fix."""
import json, os, sys
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
from scripts.sound_match.replay_proof import prove_replay

BASS_MIDI = REPO / "data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid"
PROF_DIR = REPO / "data/v4/profiles/31a164f845f8e27e"

for pname, out in [("bass.json", "bass.replay_proof.json"),
                   ("bass_v2.json", "bass_v2.replay_proof.json")]:
    prof = json.loads((PROF_DIR / pname).read_text())
    report = prove_replay(prof, BASS_MIDI, out_json=PROF_DIR / out)
    print(f"{pname} → {report['verdict']} sha={report['run1_sha256'][:16]}")

# Cross-proof assertion: SHAs must now differ
b = json.loads((PROF_DIR / "bass.replay_proof.json").read_text())
b2 = json.loads((PROF_DIR / "bass_v2.replay_proof.json").read_text())
assert b["run1_sha256"] != b2["run1_sha256"], (
    f"CRITICAL: post-fix bass.sha == bass_v2.sha == {b['run1_sha256']}. "
    "Fix took no effect."
)
print(f"CROSS-PROOF: bass.sha={b['run1_sha256'][:16]} != bass_v2.sha={b2['run1_sha256'][:16]} OK")
