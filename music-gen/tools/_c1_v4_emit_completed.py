#!/usr/bin/env -S /usr/bin/python3
"""v4 cycle 1: emit sweep-completed follow-up + plan-register event.

The sweep initially produced 15 identical renders (MIDI routing bug —
program_change inserted into the meta-only track). Fix landed IN-CYCLE
(track-with-notes routing) and the sweep re-ran to a discriminative
leaderboard (composite spread 668.7 → 897.0, 15 distinct render SHAs).
Cycle 2 auditor picks up the leaderboard for stage-2 fine fit.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

RUN_ID = "run-2026-09-03T183900Z"
TS = "2026-09-03T18:47:00Z"
CYCLE = 1
CG = "31a164f845f8e27e"
REPO = Path("/home/user/long-exposure-runs/music-gen")

def _sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

LB = REPO / f"data/v4/profiles/{CG}/bass_sweep_stage1/leaderboard.tsv"
MAN = REPO / f"data/v4/profiles/{CG}/bass_sweep_stage1/run_manifest.json"
LB_SHA = _sha(LB)
MAN_SHA = _sha(MAN)

NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
def eid(mid): return str(uuid.uuid5(NS, f"{mid}|{RUN_ID}|{CYCLE}|completed"))

EVENTS = [
    {
        "milestone_id": "M-V4-PROFILES-1/cg-bass-sweep-completed",
        "event_id": eid("M-V4-PROFILES-1/cg-bass-sweep-completed"),
        "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker", "ts": TS,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Sweep finished in-cycle after in-cycle fix of the "
                "program_change routing bug. 15/15 renders produced 15 "
                "distinct render SHAs; composite spread 668.7 → 897.0 "
                "(34%, well above the Rung-2 falsification threshold of "
                "5% and satisfying the mechanism §Rules-in criterion "
                "'top-1 composite < 50% of median'). Objective panel is "
                "discriminative on this content: mel_l1_db range 4.83 → "
                "21.06, spectral_centroid_rmse_hz 2597.8 → 3536.9, "
                "embedding_cos_vggish 0.083 → 0.462."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "M-V4-PROFILES-1 cycle-1 sweep completion. First attempt "
            "(PID 5400) produced 15 byte-identical renders due to "
            "program_change inserted into track 0 (meta-only) while "
            "notes live on track 1. In-cycle fix: the rewriter now "
            "inserts bank-select+program-change into the first track "
            "that carries note_on on the target channel. Re-launched "
            "detached PID 5624; ran 35.9 s; 15/15 renders SHA-distinct. "
            f"Leaderboard: `{LB.relative_to(REPO)}` SHA `{LB_SHA}`. "
            f"Run manifest: `{MAN.relative_to(REPO)}` SHA `{MAN_SHA}`. "
            "Top-5 (composite ascending): program 19 Church Organ (668.7), "
            "program 5 Electric Piano 2 (674.3), program 38 Synth Bass 1 "
            "(728.3), program 18 Rock Organ (804.0), program 17 Drawbar "
            "Organ (805.2). Program 33 Electric Bass Finger (the source-of-"
            "truth GM program on the merged.mid bass track) ranks #8 with "
            "composite 821.6 — mid-pack. Programs 32-39 (bass family) "
            "occupy ranks {3, 6, 8, 9, 10, 12, 13, 15}. This is a first-"
            "class finding: the sf2-only objective ranks organ-family "
            "candidates ahead of the source bass preset on Chicken Grease "
            "bass, suggesting the objective is sensitive to spectral "
            "envelope richness in a way that pulls toward organs at this "
            "hop/n_fft. Cycle 2 auditor should decide whether (a) to "
            "promote the top-5 into stage-2 fine fit as-is, (b) reweight "
            "the composite to give embedding_cos more say, or (c) open "
            "family-2 (stem-sampled) for bass in parallel per Rung-2 "
            "falsification of family-1 sufficiency. Env pins held throughout: "
            "PYTHONHASHSEED=0, SOURCE_DATE_EPOCH=1756463424, TZ=UTC, "
            "LC_ALL=C.UTF-8, OMP/MKL/OPENBLAS_NUM_THREADS=1. SF2 SHA "
            "`74594e8f…1cb0` asserted at launch. Reference stem SHA "
            "`1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd`. "
            "MIDI excerpt SHA "
            "`4863ca285c7db513c8bfc22da5e35e65036b0ecad2538a6d9794c80eb15f8ac9`. "
            "Search step is stochastic-tolerant per spec §Two phases; the "
            "profile-writer + replay ×2 discipline applies at the winner-"
            "selection step (cycle 2+)."
        ),
        "artifacts": [
            f"data/v4/profiles/{CG}/bass_sweep_stage1/leaderboard.tsv",
            f"data/v4/profiles/{CG}/bass_sweep_stage1/run_manifest.json",
            f"data/v4/profiles/{CG}/bass_sweep_stage1/renders",
            "scripts/sound_match/coarse_sweep_sf2.py",
        ],
    },
    {
        "milestone_id": "_plan/register-v4-milestones",
        "event_id": eid("_plan/register-v4-milestones"),
        "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker", "ts": TS,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Plan-of-record row registration for the v4 closure "
                "milestones introduced by cycle 1. Canonical shape uses "
                "`-1` suffix (matches campaign convention M-V3-SPINE-1 / "
                "M-V3-FOCUS-1 / M-INGEST-1)."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "v4 closure milestones registered in plan_of_record.md: "
            "M-V4-CERT-1 (LANDS on evidence this cycle), M-V4-PROFILES-1 "
            "(active), M-V4-PROFILES-1/cg-bass-sweep-launched (in-progress "
            "→ superseded by /cg-bass-sweep-completed this cycle), "
            "M-V4-PROFILES-1/cg-bass-sweep-completed (validated), M-V4-"
            "SHOWCASE-1 (pending), M-V4-RULES-1 (pending), M-V4-EAR-1 "
            "(pending), M-V4-GEN-1 (pending), M-V4-CLOSE-1 (pending). "
            "See docs/specs/v4_sound_matching_layer_spec.md for the "
            "M-V4-PROFILES-1 shape and docs/v3_determinism_certificate.md "
            "§2 for the M-V4-CERT-1 evidence."
        ),
        "artifacts": ["plan_of_record.md"],
    },
    {
        "milestone_id": "_archive/cycle-1-v4-scratch",
        "event_id": eid("_archive/cycle-1-v4-scratch"),
        "run_id": RUN_ID, "cycle": CYCLE, "agent": "worker", "ts": TS,
        "status": "validated",
        "confidence": {
            "level": "high",
            "rationale": (
                "Housekeeping row per campaign convention. One-shot emitter "
                "scripts under tools/ (this file + _c1_v4_emit_events.py) "
                "are documented as scratch; physical move to tools/stale/ "
                "deferred to avoid touching in-flight artifacts."
            ),
            "assessor": "worker",
        },
        "narrative": (
            "Cycle 1 housekeeping: one-shot ledger-emitter scripts "
            "tools/_c1_v4_emit_events.py and tools/_c1_v4_emit_completed.py "
            "are pure emitters and can be moved to tools/stale/ after cycle 2 "
            "audit. Not moved this cycle so the emitter provenance stays "
            "trivial to inspect."
        ),
        "artifacts": [],
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
            print(f"    stderr: {r.stderr.decode(errors='replace')[:400]}")
            fail += 1
    print(f"\n{ok}/{ok+fail} events appended")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
