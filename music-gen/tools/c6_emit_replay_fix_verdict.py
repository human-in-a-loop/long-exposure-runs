#!/usr/bin/env -S /usr/bin/python3
"""Emit replay_fix_verdict.json for c6 Task 1."""
import hashlib, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROF_DIR = REPO / "data/v4/profiles/31a164f845f8e27e"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

rubric_doc_sha = sha(REPO / "docs/sound_match/replay_program_invariance_fix_c6_rubric.md")
rubric_hash_txt = (PROF_DIR / "replay_fix_c6_rubric_hash.txt").read_text().strip()
assert rubric_doc_sha == rubric_hash_txt, f"rubric drift {rubric_doc_sha} != {rubric_hash_txt}"

replay_post_sha = sha(REPO / "scripts/sound_match/replay.py")
replay_pre_sha = json.loads((PROF_DIR / "anchor_preservation_pre_c6.json").read_text())["replay_py_pre_sha"]

test_matrix = json.loads((PROF_DIR / "replay_fix_test_matrix.json").read_text())["test_matrix"]
b = json.loads((PROF_DIR / "bass.replay_proof.json").read_text())
b2 = json.loads((PROF_DIR / "bass_v2.replay_proof.json").read_text())

all_tests_pass = all(v == "pass" for v in test_matrix.values())
both_proofs_hold = (b["verdict"] == "REPLAY_PROOF_HOLDS" and b2["verdict"] == "REPLAY_PROOF_HOLDS")
proofs_differ = b["run1_sha256"] != b2["run1_sha256"]

if all_tests_pass and both_proofs_hold and proofs_differ:
    verdict = "REPLAY_FIX_LANDS"
elif all_tests_pass and (b["verdict"] == "REPLAY_PROOF_HOLDS") ^ (b2["verdict"] == "REPLAY_PROOF_HOLDS"):
    verdict = "REPLAY_FIX_PARTIAL"
else:
    verdict = "REPLAY_FIX_FAILS"

out = {
    "verdict": verdict,
    "rubric_hash": rubric_doc_sha,
    "pre_fix_replay_shas": {
        "bass": "832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5",
        "bass_v2": "832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5",
    },
    "post_fix_replay_shas": {
        "bass": b["run1_sha256"],
        "bass_v2": b2["run1_sha256"],
    },
    "test_matrix": test_matrix,
    "env_pin_sha256": b["env_pin_sha256"],
    "replay_py_pre_sha": replay_pre_sha,
    "replay_py_post_sha": replay_post_sha,
    "cross_proof_shas_differ": proofs_differ,
    "cycle": 6,
}
p = PROF_DIR / "replay_fix_verdict.json"
p.write_text(json.dumps(out, sort_keys=True, indent=2))
print(json.dumps(out, sort_keys=True, indent=2))
