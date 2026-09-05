#!/usr/bin/python3
"""c24 post-run verification: anchor SHAs + artifact presence + verdict states."""
import hashlib, json, subprocess
from pathlib import Path

anchors = {
    "bass_v2_c9": "data/v4/deliveries/31a164f845f8e27e/bass_v2.json",
    "cg_bass_pinned_c9": "data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile.json",
    "cg_drums_pinned_c14": "data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json",
    "cg_guitar_pinned_c15": "data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile.json",
    "cg_ab_mix_c17": "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav",
    "objective_py": "scripts/sound_match/objective.py",
    "replay_py": "scripts/sound_match/replay.py",
}
print("=== Anchor SHAs (post-c24) ===")
for k, p in anchors.items():
    if Path(p).exists():
        h = hashlib.sha256(open(p,'rb').read()).hexdigest()[:20]
        print(f"  {h} {k}")

print("\n=== c24 artifacts on disk ===")
paths = [
    "stale/what_if_i_go_bass_family_verdict.c23_scope_extension_disclosed.json",
    "stale/rome_bass_family_verdict.c23_scope_extension_disclosed.json",
    "stale/peach_dream_bass_family_verdict.c23_scope_extension_disclosed.json",
    "stale/disco_a_bass_family_verdict.c23_scope_extension_disclosed.json",
    "data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json",
    "data/v4/deliveries/31a164f845f8e27e/cg_drums_acceptance_c22_corrected_disclosure.json",
    "data/v4/deliveries/31a164f845f8e27e/cg_guitar_acceptance_c22_corrected_disclosure.json",
    "docs/v4_closure_completion_report_c24_amendment.md",
    "data/v4/deliveries/31a164f845f8e27e/cycle24/track_a_d_closeout.json",
]
for p in paths:
    exists = Path(p).exists()
    mark = "OK" if exists else "MISSING"
    print(f"  [{mark}] {p}")

print("\n=== Revised verdicts on disk ===")
for sha16 in ["252eb21ce7df7328", "51e433ade2a845e1", "88d247468cb6d49f", "cdd2717e52820ff6"]:
    d = json.load(open(f"data/v4/profiles/{sha16}/bass_family_verdict_c23.json"))
    sp = d.get('supersedes_path')
    sp_type = type(sp).__name__
    print(f"  {sha16}: verdict={d['verdict']}, supersedes_path[{sp_type}]={sp}")

r = subprocess.run(["grep", "-c", '"cycle":24,', "promise_ledger.jsonl"], capture_output=True, text=True)
c24_count_a = r.stdout.strip()
r = subprocess.run(["grep", "-c", '"cycle": 24', "promise_ledger.jsonl"], capture_output=True, text=True)
c24_count_b = r.stdout.strip()
print(f"\nc24 ledger event rows: canonical-json={c24_count_a} indent-json={c24_count_b}")

# Sanity check: no SF2_CONFIRMED emitted this cycle
r = subprocess.run(["grep", '"cycle":24,', "promise_ledger.jsonl"], capture_output=True, text=True)
lines = r.stdout.strip().split("\n") if r.stdout.strip() else []
sf2conf_c24 = [l for l in lines if "SF2_CONFIRMED" in l]
print(f"\nSF2_CONFIRMED mentions in c24 events: {len(sf2conf_c24)} (should be 0 unless in disclosure narrative)")
