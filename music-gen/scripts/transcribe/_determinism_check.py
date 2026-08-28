"""One-shot: rerun basic-pitch on one pair, compare SHA + F1 jitter."""
import hashlib
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, "scripts/transcribe")
from eval_transcription import load_jsonl, eval_pair  # type: ignore

ref = load_jsonl(pathlib.Path("data/transcribe/reference/synth_030s/bass.reference.jsonl"))
cur = pathlib.Path("data/transcribe/basic_pitch/synth_030s/bass.jsonl")
h1 = hashlib.sha256(cur.read_bytes()).hexdigest()
est1 = load_jsonl(cur)
f1_a = eval_pair(ref, est1, is_drum=False)["f1"]

subprocess.run([
    "workspace/basic_pitch_venv/bin/python3",
    "scripts/transcribe/_bp_call.py",
    "data/separation/synth_mix/gt/synth_030s/bass.wav",
    "/tmp/rerun.mid",
    "/tmp/rerun.jsonl",
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

rerun = pathlib.Path("/tmp/rerun.jsonl")
h2 = hashlib.sha256(rerun.read_bytes()).hexdigest()
est2 = load_jsonl(rerun)
f1_b = eval_pair(ref, est2, is_drum=False)["f1"]

out = {
    "sha1_prefix": h1[:16],
    "sha2_prefix": h2[:16],
    "bit_identical": h1 == h2,
    "n_notes_1": len(est1),
    "n_notes_2": len(est2),
    "f1_1": round(f1_a, 4),
    "f1_2": round(f1_b, 4),
    "f1_delta": round(abs(f1_a - f1_b), 4),
}
print(json.dumps(out, indent=2))
