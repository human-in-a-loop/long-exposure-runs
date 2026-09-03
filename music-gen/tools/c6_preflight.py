#!/usr/bin/env -S /usr/bin/python3
"""c6 pre-flight: anchor SHAs, replay.py pre-fix SHA, df, archive pre-fix proofs."""
import hashlib, json, subprocess, shutil
from pathlib import Path

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

WS = Path(".")
anchors = {
    "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav": None,
    "data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json": None,
    "data/v4/profiles/31a164f845f8e27e/bass.json": None,
    "data/v4/profiles/31a164f845f8e27e/bass_v2.json": None,
}
for k in list(anchors):
    anchors[k] = sha(WS / k)

replay_pre = sha(WS / "scripts/sound_match/replay.py")
spike_pre = sha(WS / "scripts/sound_match/family2_stem_sampled_spike.py")
df = subprocess.check_output(["df", "-h", "."]).decode().splitlines()[1].split()

out = {
    "anchors": anchors,
    "replay_py_pre_sha": replay_pre,
    "family2_spike_pre_sha": spike_pre,
    "df_pct": df[4],
    "cycle": 6,
}
p = WS / "data/v4/profiles/31a164f845f8e27e/anchor_preservation_pre_c6.json"
p.write_text(json.dumps(out, sort_keys=True, indent=2))

for f in ["bass.replay_proof.json", "bass_v2.replay_proof.json"]:
    src = WS / "data/v4/profiles/31a164f845f8e27e" / f
    dst = WS / "data/v4/profiles/31a164f845f8e27e/pre_c6_fix" / f
    shutil.copy2(src, dst)

print(json.dumps(out, sort_keys=True, indent=2))
