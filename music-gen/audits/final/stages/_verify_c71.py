#!/usr/bin/env python3
"""Verify c71 audibility-gated render fix chain (M-V4-SHOWCASE-1 v2 renders)."""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path("/home/user/long-exposure-runs/music-gen")


def sha(p):
    try:
        return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
    except FileNotFoundError:
        return "MISSING"


DRIVER_POST_C71 = "937f99a80ce23cfd3255f9133ec564230a0ca1b9fa9b45707b0eed2c453b094c"
d_sha = sha(ROOT / "scripts/sound_match/deliver_ab_v4.py")
print(f"[1] deliver_ab_v4.py post-c71 sha match: {d_sha == DRIVER_POST_C71} ({d_sha[:16]})")

C17_ANCHOR = "3c45465284e2f78a"
c17_sha = sha(ROOT / "scripts/sound_match/deliver_cg_ab_v4.py")
print(f"[2] deliver_cg_ab_v4.py c17 anchor preserved: {c17_sha.startswith(C17_ANCHOR)} ({c17_sha[:16]})")

REPLAY_ANCHOR = "1f43027039c45f5e"
r_sha = sha(ROOT / "scripts/sound_match/replay.py")
print(f"[3] replay.py c11 anchor preserved: {r_sha.startswith(REPLAY_ANCHOR)} ({r_sha[:16]})")

MSA_ANCHOR = "c40b76e4f7f1af7c"
m_sha = sha(ROOT / "scripts/sound_match/measure_stem_audibility.py")
print(f"[4] measure_stem_audibility.py c14 anchor preserved: {m_sha.startswith(MSA_ANCHOR)} ({m_sha[:16]})")

V2_ANCHORS = {
    "252eb21ce7df7328": ("WIG",       "29de5ee222f2d8489dcc15caedc33908bfaa72c9094ee299318457cbae060918"),
    "51e433ade2a845e1": ("Rome",      "9ea1fe324677b01e623dc1c2a4a7d409182f03c494d7a8d4ee110eca6dfad14f"),
    "88d247468cb6d49f": ("PD",        "e164c42bc192de789984267f45c5acc16da3f845debba18415685d50b0afa7ce"),
    "cdd2717e52820ff6": ("Disco A",   "77cd593a48dbbb27efcd07c87a840d96d841e7eb29b3aee1f46b4531f8feb5f6"),
}
print("[5] c71 v2 A/B WAV SHA anchors:")
v2_pass = 0
for sha16, (name, expected) in V2_ANCHORS.items():
    p = ROOT / f"data/v4/deliveries/{sha16}/ab_mix_v2.wav"
    actual = sha(p)
    ok = actual == expected
    v2_pass += ok
    print(f"    {name} ({sha16}): {ok} (on-disk {actual[:16]})")

V1_ANCHORS = {
    "252eb21ce7df7328": ("WIG",     "6feca5d1fb41ee149e727b6ec2a61d2a006b4bc0b2a0aff62f2ef8946f47e3e9"),
    "51e433ade2a845e1": ("Rome",    "81e2ef1525ed4485a497c60dece0e29dffc0b1fedfa593ac8a457f70541b26b0"),
    "88d247468cb6d49f": ("PD",      "a300cf4ca12f132e24dc34bcafb4cf4bc621d9529f9de67442afeac3cc02d806"),
    "cdd2717e52820ff6": ("Disco A", "1b673106aae19b9ccd6f9d81333eae9e906a1dba1e85df38fb3041c8ea494080"),
}
print("[6] c69 v1 A/B WAV anchors preserved:")
v1_pass = 0
for sha16, (name, expected) in V1_ANCHORS.items():
    p = ROOT / f"data/v4/deliveries/{sha16}/ab_mix.wav"
    actual = sha(p)
    ok = actual == expected
    v1_pass += ok
    print(f"    {name}: {ok} (on-disk {actual[:16]})")

print("[7] v2 replay proofs:")
rp_pass = 0
for sha16, (name, expected_wav) in V2_ANCHORS.items():
    p = ROOT / f"data/v4/deliveries/{sha16}/ab_mix_v2.replay_proof.json"
    if p.exists():
        try:
            data = json.loads(p.read_text())
            r1 = data.get("run1_sha256") or data.get("run1_sha")
            r2 = data.get("run2_sha256") or data.get("run2_sha")
            verdict = str(data.get("verdict", ""))
            holds = (r1 == r2 == expected_wav) and "HOLDS" in verdict.upper()
            rp_pass += holds
            print(f"    {name}: verdict={verdict}, holds={holds}, r1={str(r1)[:16]}")
        except Exception as e:
            print(f"    {name}: parse error {e}")
    else:
        d = ROOT / f"data/v4/deliveries/{sha16}"
        alts = list(d.glob("ab_mix_v2*.json")) if d.exists() else []
        print(f"    {name}: proof file missing; sibling jsons: {[a.name for a in alts]}")

print("[8] WIG v1 manifest superseded_by_v2 annotation:")
mp = ROOT / "data/v4/deliveries/252eb21ce7df7328/ab_mix.manifest.json"
try:
    mm = json.loads(mp.read_text())
    keys = [k for k in mm.keys() if "supersed" in k.lower() or "v2" in k.lower()]
    has_diag = "wig_duration_diagnostic" in mm
    print(f"    keys with v2/supersede: {keys}")
    print(f"    c70 wig_duration_diagnostic preserved: {has_diag}")
except Exception as e:
    print(f"    error: {e}")

tp = ROOT / "tests/test_deliver_ab_v4.py"
if tp.exists():
    content = tp.read_text()
    test_defs = re.findall(r"def (test_\d+_[a-zA-Z0-9_]+)", content)
    print(f"[9] tests/test_deliver_ab_v4.py test functions: {len(test_defs)}")
    for t in test_defs:
        print(f"    {t}")

print("[10] Discipline scan on deliver_ab_v4.py:")
content = (ROOT / "scripts/sound_match/deliver_ab_v4.py").read_text()
prng_flags = [k for k in ["import random", "np.random", "torch.random"] if k in content]
sidecar = "sidecar_nonfactor" in content
vst3 = any(k in content for k in ["get_state", "save_state", "load_state", "save_preset"])
guard = "/usr/bin/python3" in content or "usr/bin/env python3" in content
print(f"    PRNG hits: {prng_flags}")
print(f"    sidecar_nonfactor import: {sidecar}")
print(f"    VST3 state APIs: {vst3}")
print(f"    interpreter guard present: {guard}")

EXPECTED_ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
print("[11] env_pin_sha256 canonical in v2 manifests:")
env_pass = 0
for sha16, (name, _) in V2_ANCHORS.items():
    mp = ROOT / f"data/v4/deliveries/{sha16}/ab_mix_v2.manifest.json"
    if mp.exists():
        try:
            m = json.loads(mp.read_text())
            s = json.dumps(m)
            hit = EXPECTED_ENV_PIN in s
            env_pass += hit
            print(f"    {name}: canonical env_pin present: {hit}")
        except Exception as e:
            print(f"    {name}: parse error {e}")

print(f"\nSUMMARY: driver={d_sha == DRIVER_POST_C71}, c17={c17_sha.startswith(C17_ANCHOR)}, "
      f"replay={r_sha.startswith(REPLAY_ANCHOR)}, msa={m_sha.startswith(MSA_ANCHOR)}, "
      f"v2_pass={v2_pass}/4, v1_preserved={v1_pass}/4, env_pin={env_pass}/4")
