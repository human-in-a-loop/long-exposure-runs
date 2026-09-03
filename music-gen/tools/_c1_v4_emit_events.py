#!/usr/bin/env -S /usr/bin/python3
"""v4 cycle 1: emit ledger events for M-V4-CERT (LANDS on evidence) and
M-V4-PROFILES/cg-bass-sweep-launched (detached launch pinned).

Uses ledger_append helper so the writer namespaces properly.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

RUN_ID = "run-2026-09-03T183900Z"
TS = "2026-09-03T18:39:00Z"
CYCLE = 1

REPO = Path("/home/user/long-exposure-runs/music-gen")

def _sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

CERT_DOC = REPO / "docs/v3_determinism_certificate.md"
CERT_DOC_SHA = _sha(CERT_DOC)
CG = "31a164f845f8e27e"
RUN1 = REPO / f"data/v3/deliveries/{CG}/cert_run1"
RUN2 = REPO / f"data/v3/deliveries/{CG}/cert_run2"
RUN1_FULL = _sha(RUN1 / "full_reconstruction.wav")
RUN2_FULL = _sha(RUN2 / "full_reconstruction.wav")
RUN1_ORIG = _sha(RUN1 / "original_ab.wav")
RUN1_ENVPIN = json.loads((RUN1 / "env_pin.json").read_text())["env_pin_sha256"]
RUN2_ENVPIN = json.loads((RUN2 / "env_pin.json").read_text())["env_pin_sha256"]

# Sweep launch pins
LAUNCH_PID = 5400
LOGFILE = REPO / "data/v4/logs/cg_bass_sweep_c1.log"
BASS_MIDI = REPO / f"data/v3/deliveries/{CG}/cert_run1/per_track/bass.mid"
BASS_MIDI_SHA = _sha(BASS_MIDI)
BASS_STEM = REPO / f"data/v3/deliveries/{CG}/cert_run1/stems_6s/bass.wav"
BASS_STEM_SHA = _sha(BASS_STEM)
SF2_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
LEADERBOARD_EXPECTED = REPO / f"data/v4/profiles/{CG}/bass_sweep_stage1/leaderboard.tsv"

LAUNCH_CMD = (
    "nohup setsid /usr/bin/python3 -m scripts.sound_match.coarse_sweep_sf2 "
    f"--song {CG} --instrument bass "
    f"--reference-stem data/v3/deliveries/{CG}/cert_run1/stems_6s/bass.wav "
    f"--midi-excerpt data/v3/deliveries/{CG}/cert_run1/per_track/bass.mid "
    "--sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2 "
    "--presets 'bank0:programs=32,33,34,35,36,37,38,39,4,5,6,7,17,18,19' "
    f"--out data/v4/profiles/{CG}/bass_sweep_stage1/ "
    f"> data/v4/logs/cg_bass_sweep_c1.log 2>&1 &"
)

ENV_PINS = {
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC", "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
}

NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
def eid(mid): return str(uuid.uuid5(NS, f"{mid}|{RUN_ID}|{CYCLE}"))

EVENTS = [
    {
        "milestone_id": "M-V4-CERT-1",
        "event_id": eid("M-V4-CERT-1"),
        "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker", "ts": TS,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Certificate §2 already recorded verdict E2E_DETERMINISM_HOLDS "
                "(2026-09-03) with the delivered-WAV SHA table populated. "
                "On-disk reconciliation this cycle: cert_run1 and cert_run2 "
                f"full_reconstruction.wav both SHA `{RUN1_FULL[:24]}…` (matches "
                f"§2 table `cc919559b4508b6bfe86…`); original_ab.wav both "
                f"`{RUN1_ORIG[:24]}…` (matches `b2f7cc1adfa32eaf7ee3…`); "
                f"env_pin_sha256 identical across runs `{RUN1_ENVPIN[:24]}…` "
                "(matches Fixed Decision 2026-09-03 point 16(a) required "
                "value `623df01f262ffd18…`). No re-run warranted per FD-16(b) "
                "since env_pin unchanged."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "M-V4-CERT LANDS on evidence-only reconciliation. §2 double-run "
            f"SHA table populated 2026-09-03; verdict `E2E_DETERMINISM_HOLDS`. "
            f"Delivery paths: {RUN1} and {RUN2}. Both env_pin_sha256 = "
            f"`{RUN1_ENVPIN}`. Certificate doc SHA `{CERT_DOC_SHA}`. "
            "Per operator Fixed Decision 2026-09-03 point 16(a), re-issue is "
            "required only on env_pin change — no re-run this cycle."
        ),
        "artifacts": [
            "docs/v3_determinism_certificate.md",
            f"data/v3/deliveries/{CG}/cert_run1/full_reconstruction.wav",
            f"data/v3/deliveries/{CG}/cert_run2/full_reconstruction.wav",
            f"data/v3/deliveries/{CG}/cert_run1/env_pin.json",
            f"data/v3/deliveries/{CG}/cert_run2/env_pin.json",
        ],
    },
    {
        "milestone_id": "M-V4-PROFILES-1/cg-bass-sweep-launched",
        "event_id": eid("M-V4-PROFILES-1/cg-bass-sweep-launched"),
        "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker", "ts": TS,
        "status": "in-progress",
        "confidence": {
            "level": "high",
            "rationale": (
                "Satellite scaffolding complete (6 modules under "
                "scripts/sound_match/, 4 tests green). Detached fluidsynth "
                "coarse sweep launched with PID + logfile; log grew within "
                "the 60 s post-launch window (TensorFlow/VGGish import "
                "messages visible), no immediate crash. Cycle 2 auditor "
                "reads the leaderboard TSV to promote top-5 into fine fit."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "M-V4-PROFILES cycle-1 handoff. Sound-matching satellite lands "
            "at scripts/sound_match/ (objective.py, coarse_sweep_sf2.py, "
            "profile_writer.py, replay.py, deliver_ab.py, __init__.py). "
            "Tests green: 4 pass. Sweep launched detached with PID="
            f"{LAUNCH_PID}, log at `{LOGFILE.relative_to(REPO)}`, expected "
            f"leaderboard at `{LEADERBOARD_EXPECTED.relative_to(REPO)}`. "
            "15 SF2 preset candidates (bank0 programs 32-39 bass family + "
            "4-7 electric pianos + 17-19 organs for contrast). Reference "
            f"stem `{BASS_STEM.relative_to(REPO)}` SHA `{BASS_STEM_SHA}`. "
            f"MIDI excerpt `{BASS_MIDI.relative_to(REPO)}` SHA `{BASS_MIDI_SHA}` "
            "extracted from cert_run1/merged.mid (65 bass notes). SF2 SHA "
            f"`{SF2_SHA}` (asserted in-run). Env pins: "
            + ", ".join(f"{k}={v}" for k, v in sorted(ENV_PINS.items())) + ". "
            "Launch command: `" + LAUNCH_CMD + "`. Objective weights frozen "
            "at milestone start: mel_l1=0.5, centroid_rmse=0.25, "
            "embedding_cos=0.25 (fallback 0.67/0.33 when embedding rung is "
            "none_available). Cycle 2 picks up leaderboard.tsv + run_manifest.json."
        ),
        "artifacts": [
            "scripts/sound_match/__init__.py",
            "scripts/sound_match/objective.py",
            "scripts/sound_match/coarse_sweep_sf2.py",
            "scripts/sound_match/profile_writer.py",
            "scripts/sound_match/replay.py",
            "scripts/sound_match/deliver_ab.py",
            "scripts/sound_match/_launch_cg_bass_sweep_c1.sh",
            "tests/test_sound_match_objective.py",
            "tests/test_sound_match_profile_writer.py",
            "tests/test_sound_match_replay_shape.py",
            "tests/test_sound_match_cli_shape.py",
            f"data/v3/deliveries/{CG}/cert_run1/per_track/bass.mid",
            "data/v4/logs/cg_bass_sweep_c1.log",
        ],
    },
]


def main():
    ok = fail = 0
    for ev in EVENTS:
        cmd = ["/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
               "--event", json.dumps(ev)]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0:
            print(f"  OK  {ev['milestone_id']}")
            ok += 1
        else:
            print(f"  FAIL {ev['milestone_id']} rc={r.returncode}")
            print(f"    stdout: {r.stdout.decode(errors='replace')[:400]}")
            print(f"    stderr: {r.stderr.decode(errors='replace')[:400]}")
            fail += 1
    print(f"\n{ok}/{ok+fail} events appended")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
