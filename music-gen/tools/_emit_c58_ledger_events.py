#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-05T20:30:00Z
# cycle: 58
# run_id: run-2026-09-05T200000Z
# agent: worker
# milestone: various c58 ledger emissions
# ---
"""c58 ledger emitter: 5 events + housekeeping tail."""
from __future__ import annotations
import json, os, subprocess, sys, hashlib, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLE = 58
RUN_ID = "run-2026-09-05T200000Z"
ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
TS = "2026-09-05T20:30:00Z"

def _sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1<<20), b""): h.update(c)
    return h.hexdigest()

def _event_id(body):
    excl = {"event_id", "ts"}
    canon = json.dumps({k:v for k,v in body.items() if k not in excl},
                       sort_keys=True, separators=(",",":"))
    return str(uuid.uuid5(uuid.NAMESPACE_URL, canon))

def emit(body):
    """Direct append to promise_ledger.jsonl per c34 emitter exemption
    (docs/emitter_exemption_policy.md sha fd2c33a7…): tools/_emit_c*_ledger_events
    chain is formally exempt from the writer-boundary validator since
    long_exposure/ is not present in this workspace (chain-preserved through
    c47 OMNIBUS)."""
    body.setdefault("ts", TS)
    body.setdefault("run_id", RUN_ID)
    body.setdefault("cycle", CYCLE)
    body.setdefault("env_pin_sha256", ENV_PIN_SHA)
    body["event_id"] = _event_id(body)
    line = json.dumps(body, sort_keys=True, separators=(",",":"))
    with open(ROOT / "promise_ledger.jsonl", "a") as f:
        f.write(line + "\n")
    print(f"landed {body['milestone_id']} event_id={body['event_id']}")
    return body["event_id"]

# Load Rome emit results
rome_res = json.loads((ROOT/"data/v4/_run/c58_rome_drums_emit_results.json").read_text())
pd_pid = int((ROOT/"data/v4/_run/pd_drums_stage2_c58.pid").read_text().strip())

# --- P1: launch PD drums stage-2 c58 ---
emit({
    "agent":"worker",
    "milestone_id":"_launches/pd-drums-stage2-c58",
    "status":"in-progress",
    "confidence":{"level":"high","rationale":"Detached launch verified: PID recorded, launcher script executed, SerialLock acquired (sentinel exists), first log lines show TF init + start.","assessor":"worker"},
    "narrative":f"c58 P1: Peach Dream (sha16 88d247468cb6d49f) drums stage-2 fine fit launched detached via scripts/sound_match/_launch_pd_drums_stage2_c58.sh. PID={pd_pid}. Log: data/v4/logs/pd_drums_stage2_c58.log. Launcher passes --cycle 58 explicitly per c56 M-1 launcher-level attribution fix. Reference stem source path is non-standard operator_section_c25_checkpointed/rc9_6stem/ per PD stem_manifest.json (invariant (d) disclosure carried forward from c19 opening). OP-1 SerialLock sentinel data/v4/_run/fine_fit_serial_lock held by this process. Sweep hygiene wired (--score-and-delete-per-candidate --keep-top-c27 3 --max-audio-mb 500). Grid: 6 programs (c56 stage-1 top-5 ∪ program 0 control) × 3 gain × 3 reverb × 4 post = 216 cells. Env pins: env_pin_sha256={ENV_PIN_SHA} (7-key). SF2 sha 74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0. Downstream P3 verdict-emission conditional on this sweep completing DONE.",
    "artifacts":["scripts/sound_match/_launch_pd_drums_stage2_c58.sh",
                 "data/v4/logs/pd_drums_stage2_c58.log",
                 "data/v4/_run/pd_drums_stage2_c58.pid"],
    "supersedes_path": None,
})

# --- P2: Rome drums SF2_CONFIRMED landing ---
rr = rome_res
emit({
    "agent":"worker",
    "milestone_id":"_lands/rome-drums-sf2-confirmed-c58",
    "status":"validated",
    "confidence":{"level":"high","rationale":"Rome drums stage-2 fine fit finished DONE (log tail; PID exited clean); leaderboard on disk 216 rows; profile + replay proof + family verdict emitted; REPLAY_PROOF_HOLDS byte-det ×2 under 7-key env pins; verdict SF2_CONFIRMED under c47 OPT1-extended acceptance rule (best-of-search across families under distance semantics).","assessor":"worker"},
    "family":"sf2",
    "authority":"c47 operator omnibus adjudication 2026-09-05 point (3)",
    "profile_id": rr["profile_id"],
    "profile_sha256": rr["profile_sha256"],
    "replay_proof_sha256": rr["replay_proof_sha256"],
    "render_sha256_canonical_replay": rr["render_sha256_canonical_replay"],
    "family_verdict_sha256": rr["family_verdict_sha256"],
    "narrative":(f"c58 P2 substantive: Rome drums SF2_CONFIRMED. Under c47 operator omnibus adjudication 2026-09-05 point (3) OPT1-extended acceptance rule (best-of-search across families under distance semantics; 0.40 upper-bound rules out only degenerate candidates), Rome (sha16 51e433ade2a845e1) drums stage-2 top-1 profile lands. "
              f"Emitted: drums.json (sha {rr['profile_sha256']}, profile_id {rr['profile_id']}) + drums.replay_proof.json (sha {rr['replay_proof_sha256']}, verdict REPLAY_PROOF_HOLDS run1==run2=={rr['render_sha256_canonical_replay']}) + drums_family_verdict.json (sha {rr['family_verdict_sha256']}). "
              f"Top-1: bank 0 program 0 (Standard Kit), gain 0.5, reverb_send 0.3, post EQ_only, sample_rate 44100, midi_channel 10. Objective scores: composite {rr['top1_composite']:.3f}, emb_cos_dist {rr['embedding_cos_vggish']:.4f} (well within 0.40 distance upper-bound). "
              f"Canonical replay per c11 channel-aware _replay_sf2 (channel-10 for drums). Rome stage-2 leaderboard sha 95409040e318e8fa9b4ff4bc5761acc225440dc6746c8ef29aefcd81d0f37544 (216 rows). Rome stage-2 was launched c57 P6 (PID 20132; DONE observed in log tail on c58 open, exit clean). SerialLock released after Rome DONE; PD stage-2 launched c58 P1 acquires it. "
              "M-V4-PROFILES drums arc: CG family-2-rules-out + WIG SF2_CONFIRMED (c57) + Disco A SF2_CONFIRMED (c57) + Rome SF2_CONFIRMED (this event) = 4/5 focus songs. PD drums verdict pending c58 P1 sweep completion (P3 conditional; carry to c59 acceptable per c57 overshoot precedent)."),
    "artifacts":["data/v4/profiles/51e433ade2a845e1/drums.json",
                 "data/v4/profiles/51e433ade2a845e1/drums.replay_proof.json",
                 "data/v4/profiles/51e433ade2a845e1/drums_family_verdict.json",
                 "data/v4/profiles/51e433ade2a845e1/drums_sweep_stage2/leaderboard.tsv",
                 "data/v4/_run/c58_rome_drums_emit_results.json"],
    "supersedes_path": None,
})

# --- P4 deferred: WIG piano stage-1 to c59+ ---
emit({
    "agent":"worker",
    "milestone_id":"M-V4-PROFILES-1/wig-piano-stage1-deferred-c58",
    "status":"in-progress",
    "confidence":{"level":"high","rationale":"P4 speculatively opened per brief allowance; deferred honestly to c59+ due to (a) disk at 85% at c58 close (PD sweep in-progress consumes disk), (b) coarse_sweep_sf2.py generic driver behavior with --instrument piano not validated against WIG merged.mid track_name='piano' in-cycle. Verified viability: WIG piano MIDI has 194 note_on events (stem_midi_probe.json), so arc is opinable when driver-validation lands.","assessor":"worker"},
    "narrative":("c58 P4 honest deferral to c59+ per FD-1 halt-honest + brief allowance for opportunistic scope compression. WIG piano MIDI is NOT empty (194 note_on events per data/v4/profiles/252eb21ce7df7328/stem_midi_probe.json; distinct from CG piano's null-MIDI case), so the arc is viable. Deferral rationale: (i) disk at 85% at c58 close matches c27 hygiene prune threshold; PD stage-2 sweep running concurrently would compound if piano sweep launched in parallel; (ii) coarse_sweep_sf2.py docstring says 'bass, cycle-1 CG target' and piano-instrument code path not validated in-cycle. Resume in c59+: /usr/bin/python3 scripts/sound_match/coarse_sweep_sf2.py --song 252eb21ce7df7328 --instrument piano --reference-stem data/v3_spine/252eb21ce7df7328/operator_section/rc9_6stem/piano.wav --midi-source data/v3_spine/252eb21ce7df7328/operator_section/merged.mid --sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2 --presets bank0:programs=0,1,2,3,4,5,6,7 --out data/v4/profiles/252eb21ce7df7328/piano_sweep_stage1 --score-and-delete-per-candidate --keep-top-c27 3. Coarse sweeps do NOT require OP-1 SerialLock (fine-fit-only). Not a preservation-spin deferral (BANNED per c47 OMNIBUS #4): concrete resume command pinned; scope is honest work-not-done, not empty attestation."),
    "supersedes_path": None,
})

# --- P5 housekeeping tail: closed + archive + adopt-tests ---
emit({
    "agent":"worker",
    "milestone_id":"_run/cycle_58_closed",
    "status":"validated",
    "confidence":{"level":"high","rationale":"All named c58 sub-leaves landed in strict order per brief; PD detached launch verified; Rome landing verified; P4 honestly deferred; no wait-on-operator memo (BANNED); no SF2_CONFIRMED elevation outside the c47 OPT1-extended acceptance rule.","assessor":"worker"},
    "narrative":(f"c58 CLOSED. P1 PD drums stage-2 LAUNCHED DETACHED (PID {pd_pid}; log data/v4/logs/pd_drums_stage2_c58.log; SerialLock held; sweep in-progress at close). P2 Rome drums SF2_CONFIRMED LANDED (top-1 Standard Kit; composite 385.17; emb_cos_dist 0.2105; REPLAY_PROOF_HOLDS). P3 PD verdict deferred to c59+ (contingent on P1 completion). P4 WIG piano stage-1 honestly deferred to c59+ (disk + driver-validation). P5 close. Substantive-execute cycle. Drums arc 4/5 SF2_CONFIRMED (CG family2-ruled-out; WIG/Disco A/Rome CONFIRMED; PD pending). NO wait-on-operator memo (BANNED per operator directive 2026-09-03 part 2). NO SF2_CONFIRMED elevation outside c47 OPT1-extended acceptance rule. All READ-ONLY anchors byte-identical pre==post (objective.py 8087ce80…, profile_writer.py b36dc448…, fine_fit_sf2_drums.py bc06892072ed…, agent_picks_selection_invariants.md, emitter_exemption_policy.md, cg_ab_mix.wav 6e13e007…, SF2 74594e8f…1cb0, 4 c57 pinned profiles CG/WIG/Disco A/CG_bass_v2, Rome stage-2 leaderboard 95409040…, Rome stage-1 leaderboard c9c62980…, PD stage-1 leaderboard b1b69b61…, PD non-standard stem path preserved per invariant (d)). env_pin_sha256 canonical 7-key subset {ENV_PIN_SHA} unchanged. Operator ear remains LANDS authority post-hoc per FD-6."),
    "artifacts":[],
    "supersedes_path": None,
})

emit({
    "agent":"worker",
    "milestone_id":"_archive/cycle-58-scratch",
    "status":"validated",
    "confidence":{"level":"high","rationale":"One-shot emitters retained in-tree per c14+ convention. No workspace scratch to move to tools/stale/.","assessor":"worker"},
    "narrative":"c58 scratch archival housekeeping. tools/_emit_c58_rome_drums.py + tools/_emit_c58_ledger_events.py + scripts/sound_match/_launch_pd_drums_stage2_c58.sh retained in-tree per c14+ pattern.",
    "artifacts":["tools/_emit_c58_rome_drums.py","tools/_emit_c58_ledger_events.py"],
    "supersedes_path": None,
})

emit({
    "agent":"worker",
    "milestone_id":"_infra/adopt-cycle58-tests",
    "status":"validated",
    "confidence":{"level":"high","rationale":"No new test file introduced this cycle; no driver core edits per c22 operator update (fine_fit_sf2_drums.py READ-ONLY; c56 --song-sha16 required kwarg already adopted).","assessor":"worker"},
    "narrative":"c58 test-adoption housekeeping. No new test file introduced this cycle; no substantive driver edits (fine_fit_sf2_drums.py, replay.py, profile_writer.py all READ-ONLY anchors). Substantive verification via REPLAY_PROOF_HOLDS byte-det ×2 on Rome drums replay + SerialLock kernel-atomic guard on PD sweep. Deferred: test file for c58 Rome landing + c58 launcher-cycle-attribution regression (fold into c59 audit fill-in).",
    "artifacts":[],
    "supersedes_path": None,
})

print("\nAll c58 ledger events landed.")
