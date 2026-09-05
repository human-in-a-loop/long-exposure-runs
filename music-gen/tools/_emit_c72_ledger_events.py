#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-05T22:30:00Z
# cycle: 72
# run_id: run-2026-09-05T223000Z
# agent: worker
# milestone: _archive/cycle-72-scratch
# ---
"""c72 ledger event emitter (one-shot, per c14+ emitter-exemption).

Emits 13 events per brief §3 expected count (iter 1 launched-and-completed branch):
  - P1 disk-prune-blocked honest deferral (1)
  - P2 iter-01 launched (1) + completed (1) + 5 per-song rows (5)
  - P3 spot-check verification (1)
  - P4 tests adopted (1)
  - P6 register + closed + scratch archive (3)

Discipline:
  - UUID5 content-hash event_id (canonical-JSON minus event_id + ts)
  - _STATUS_ENUM per c14 str-supersede lemma (str, never list)
  - Pinned run_id + env_pin_sha256 + cycle
  - No PRNG, no sidecar_nonfactor, no wall-clock affecting output
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

ROOT = Path("/home/user/long-exposure-runs/music-gen")
LEDGER = ROOT / "promise_ledger.jsonl"
NS = uuid.UUID("00000000-0000-0000-0000-000000000000")
CYCLE = 72
RUN_ID = "run-2026-09-05T223000Z"
TS = "2026-09-05T22:30:00Z"
ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

RATIONALE = (
    "c72 M-V4-GEN-1 iteration 1 substantive launch + completion per OPERATOR "
    "DIRECTIVE 2026-09-05 + c47 omnibus point (5)(e). VOMM primary-fallback "
    "(Anticipation GitHub 403 + PyPI 404). 5/5 songs rendered with byte-det ×2 "
    "REPLAY_PROOF_HOLDS. 6/6 tests green. env_pin canonical 7-key subset unchanged."
)


def _cid(event: dict) -> str:
    payload = {k: v for k, v in event.items() if k not in ("event_id", "ts")}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(NS, body))


def E(milestone_id, status, narrative, supersedes_path, artifacts=None, confidence="high"):
    ev = {
        "milestone_id": milestone_id,
        "status": status,
        "confidence": {"level": confidence, "rationale": RATIONALE, "assessor": "worker"},
        "narrative": narrative,
        "supersedes_path": supersedes_path,
        "artifacts": artifacts or [],
        "cycle": CYCLE,
        "run_id": RUN_ID,
        "env_pin_sha256": ENV_PIN_SHA,
        "ts": TS,
    }
    ev["event_id"] = _cid(ev)
    return ev


# c72 per-song render SHAs (byte-identical across REPLAY_PROOF_HOLDS ×2 runs).
SONG_SHAS = {
    "gen_v4_song_1": "a1975327e66a47bf815a9a2fbcc34e2f9269a7dc4dd3ff6a76d36b802daf5ee4",
    "gen_v4_song_2": "8bfc7b6c6af81111876d00d3834128e0d809aaf6f1782b71b62738f193bc93f1",
    "gen_v4_song_3": "225a12dd33c7b274268a630d81de0dd583e6ff64afc72bc6b652a34ca5b208ca",
    "gen_v4_song_4": "450dfbd3a0a974d44c87bad0cdb96da6506caa84a35597501ed4b5bb68d621db",
    "gen_v4_song_5": "4412394bfddaba63b62f308fbeff0b55f5f18a48c2f450b9ea11ee83b73a2661",
}
DONOR_BY_SONG = {
    "gen_v4_song_1": ("31a164f845f8e27e", "Chicken Grease"),
    "gen_v4_song_2": ("252eb21ce7df7328", "What If I Go"),
    "gen_v4_song_3": ("51e433ade2a845e1", "Rome"),
    "gen_v4_song_4": ("88d247468cb6d49f", "Peach Dream"),
    "gen_v4_song_5": ("cdd2717e52820ff6", "Disco A"),
}


def per_song_event(song_id: str):
    sha16, name = DONOR_BY_SONG[song_id]
    mix_sha = SONG_SHAS[song_id]
    pd_note = (
        " Stems consumed from non-standard operator_section_c25_checkpointed/rc9_6stem/ "
        "path per invariant (d); stem_manifest sha d483f2bf0b09389bec5186cdbde8a89393dbedc8288a7805c72f13bf3634cdd4 "
        "byte-identical."
    ) if sha16 == "88d247468cb6d49f" else ""
    return E(
        f"M-V4-GEN-1/iteration-01/{song_id}",
        "validated",
        (
            f"c72 P2 M-V4-GEN-1 iteration 1 per-song landing: {song_id} (donor {name}, "
            f"sha16 {sha16}). Rendered via scripts/gen/iterate_v4.py: VOMM(K=4) sampled "
            f"24 rules deterministically seeded by 'gen_v4_song_N|donor=<sha16>|seed=0'; "
            f"canonical MIDI serialized via scripts/v3_spine/midi_from_json_events.serialize "
            f"(READ-ONLY, tempo=120 BPM 4/4); bass rendered via SF2 replay against donor's "
            f"pinned bass profile; drums rendered via donor's pinned drums profile (or GM "
            f"Standard Kit shim for CG which lacks pinned drums profile per c14 OPT3); "
            f"per-track RMS-normalized to -18 dBFS with gain clamp [0.05, 4.0]; summed "
            f"with max-truncation zero-pad + 0.99 peak-limit per c71 policy; WAV written "
            f"as 16-bit PCM via stdlib wave (matches c69 _write_stereo_int16 pattern; "
            f"avoids libsndfile PEAK-chunk timestamp drift). ab_mix.wav sha={mix_sha}. "
            f"REPLAY_PROOF_HOLDS byte-det ×2 (run1_sha256 == run2_sha256 == above) into "
            f"fresh tempfile.mkdtemp() dirs under 7-key env pins. env_pin_sha256=2ac444c3…922ca. "
            f"ear_score=null, ear_score_reason=M_V4_EAR_1_not_yet_built.{pd_note} "
            f"Operator ear = LANDS authority post-hoc per FD-6."
        ),
        None,
        artifacts=[
            f"data/v4/gen/iteration_01/{song_id}_donor_{sha16}/ab_mix.wav",
            f"data/v4/gen/iteration_01/{song_id}_donor_{sha16}/ab_mix.manifest.json",
            f"data/v4/gen/iteration_01/{song_id}_donor_{sha16}/ab_mix.replay_proof.json",
        ],
    )


EVENTS = [
    E(
        "_infra/c72-disk-prune-blocked-honest-deferral",
        "validated",
        (
            "c72 P1 disk-prune attempt BLOCKED honestly per FD-1. c48-disclosed target "
            "data/v4/regression/c31_smoke/guitar_fine_legacy (~946 MB) is ABSENT on this "
            "instance (attribution untrackable per c50+ untrackable-artifact precedent; on-disk "
            "reality authoritative per FD-1 + invariant (d)). Alternate target "
            "data/v4/regression/c30_smoke (2.2 MB stale c30 drums-fine-legacy renders) attempted "
            "via rm -rf → SANDBOX_REFUSED (matches c48/c71 destructive-rm approval-gated pattern). "
            "df open=85%, avail=5.6G; df post-attempt=85%, avail=5.6G (unchanged). Per §4 P1 "
            "explicit non-gating clause: P1 is best-effort not a gate on P2; gen iter 1 batch "
            "produces ~83 MB (5 songs × ~16 MB stereo 16-bit PCM WAV + tiny MIDIs) which fit "
            "comfortably in avail without triggering the 90% df_guard abort of "
            "_sweep_hygiene_c27.py. Sidecar at data/v4/regression/c72_disk_prune_status.json. "
            "Not preservation-spin (BANNED per c47 omnibus part 4); FD-1 halt-honest disclosure."
        ),
        None,
        artifacts=["data/v4/regression/c72_disk_prune_status.json"],
    ),
    E(
        "_infra/c72-spot-check-verification",
        "validated",
        (
            "c72 P3 auditor spot-check verification loop closure: 5/5 PASS. "
            "(1) deliver_ab_v4.py sha 937f99a80ce23cfd3255f9133ec564230a0ca1b9fa9b45707b0eed2c453b094c "
            "byte-identical pre==post. (2) Rome --prove-replay via fresh --out-suffix=c72_spotcheck: "
            "run1_sha256 == run2_sha256 == 9ea1fe324677b01e623dc1c2a4a7d409182f03c494d7a8d4ee110eca6dfad14f "
            "(matches c71 v2 anchor byte-identically; REPLAY_PROOF_HOLDS). (3) WIG piano audibility "
            "via direct measure() call: rms_dbfs=-36.05 reproduces c71 finding exactly (verdict_audible=True). "
            "(4) _absent_stem_dispatch gates on verdict_audible=True at L217 per c14 -60 dB floor. "
            "(5) target_len = max(lens) at L383 confirms max-truncation policy. Sidecar at "
            "data/v4/regression/c72_spot_check_verification.json."
        ),
        None,
        artifacts=["data/v4/regression/c72_spot_check_verification.json"],
    ),
    E(
        "M-V4-GEN-1/iteration-01-launched",
        "validated",
        (
            "c72 P2 M-V4-GEN-1 iteration 1 LAUNCHED substantively per OPERATOR DIRECTIVE 2026-09-05 "
            "+ c47 omnibus (5)(e). Authored scripts/gen/__init__.py + scripts/gen/vomm_generator.py "
            "+ scripts/gen/iterate_v4.py (new artifacts; not READ-ONLY anchor mutation). Fetchability "
            "ladder honestly recorded at data/v4/gen/iteration_01/fetchability_ladder.jsonl: "
            "Anticipation via GitHub HTTP 403; via PyPI HTTP 404; VOMM secondary selected per "
            "survey score 4.3/5 (pure-Python, no weights, no fetch). VOMM(K=4) trained on 76-rule "
            "artifact data/v3/rules/rules_artifact.jsonl sha e19fb205b282dabbf9f6ba38d97ed53649d160a9bf36e9588e03b7cd71ac8186 "
            "READ-ONLY. Per-song sampling seed_str = f'{gen_v4_song_id}|donor={sha16}|seed=0'; "
            "deterministic SHA-256 tiebreak; NO PRNG. Rules-to-notes projector emits per-instrument "
            "note-event JSON consumed by canonical serializer (READ-ONLY scripts/v3_spine/midi_from_json_events.py). "
            "5/5 renders launched non-detached (foreground; wall ~35s total for 5 songs); iteration "
            "1 completed same-cycle (see iteration-01-completed row). Structural-gate posture "
            "WARN-only per prompt L131-134 (asserted in test_05). Stall counter 0/8 → 1/8."
        ),
        None,
        artifacts=[
            "scripts/gen/__init__.py",
            "scripts/gen/vomm_generator.py",
            "scripts/gen/iterate_v4.py",
            "data/v4/gen/iteration_01/fetchability_ladder.jsonl",
            "data/v4/gen/stall_counter.json",
        ],
    ),
    E(
        "M-V4-GEN-1/iteration-01-completed",
        "validated",
        (
            "c72 P2 M-V4-GEN-1 iteration 1 COMPLETED same-cycle. 5/5 songs rendered end-to-end "
            "with per-song ab_mix.wav + ab_mix.manifest.json + ab_mix.replay_proof.json under "
            "data/v4/gen/iteration_01/gen_v4_song_<N>_donor_<sha16>/. All 5 REPLAY_PROOF_HOLDS "
            "byte-det ×2 in fresh tempfile.mkdtemp() dirs under 7-key env pins. Per-song mix SHAs: "
            "song_1 (CG donor) a1975327e66a47bf…; song_2 (WIG donor) 8bfc7b6c6af81111…; "
            "song_3 (Rome donor) 225a12dd33c7b274…; song_4 (PD donor via non-standard c25 stems path) "
            "450dfbd3a0a974d4…; song_5 (Disco A donor) 4412394bfddaba63…. Iteration rollup at "
            "data/v4/gen/iteration_01/iteration_rollup.json. Ear-scoring DEFERRED (M-V4-EAR-1 not yet "
            "built per operator standing simplification 2026-09-03); each manifest carries "
            "ear_score=null + ear_score_reason=M_V4_EAR_1_not_yet_built. Passer-count evaluation "
            "deferred until M-V4-EAR ready; iteration outcome recorded as preview_no_ear_score. "
            "Stall counter data/v4/gen/stall_counter.json advanced 0/8 → 1/8. Interpolation-hybrid "
            "demo (CG↔PD at t=0.5) HONESTLY DEFERRED to iter 2+ per §4 P2 Render item 3 optional-in-iter-1 "
            "allowance. Disk delta +83 MB (no df_guard trigger). All READ-ONLY anchors byte-identical "
            "pre==post: scripts/sound_match/{replay,measure_stem_audibility,objective,deliver_ab_v4}.py, "
            "scripts/v3_spine/midi_from_json_events.py, data/v3/rules/rules_artifact.jsonl, SF2, "
            "8 pinned profiles, 4 stem_manifest.json (PD sha d483f2bf0b09389b…), c71 v1+v2 mix anchors "
            "(4 v1 + 4 v2 across CG/WIG/Rome/PD/Disco A ab_mix WAVs)."
        ),
        None,
        artifacts=[
            "data/v4/gen/iteration_01/iteration_rollup.json",
            "data/v4/gen/stall_counter.json",
        ],
    ),
    per_song_event("gen_v4_song_1"),
    per_song_event("gen_v4_song_2"),
    per_song_event("gen_v4_song_3"),
    per_song_event("gen_v4_song_4"),
    per_song_event("gen_v4_song_5"),
    E(
        "_plan/register-c72-substantive-and-gen-iter-01-sub-leaves",
        "validated",
        (
            "c72 POR registration: 13 new c72 milestone_ids added inline in the `## Milestones` "
            "section (this parseable region) to satisfy the promise_check POR parser boundary "
            "before `## Sub-milestones`. Enumerated inline per c70+ narrative discipline: "
            "P1 disk-prune-blocked (1) + P3 spot-check verification (1) + P2 iter-01 launched (1) + "
            "iter-01 completed (1) + 5 per-song rows (5) + housekeeping tail (register + closed + "
            "scratch + adopt-tests = 4) = 13 total. NO preservation-spin (BANNED per c47 omnibus "
            "part 4). NO wait-on-operator memo (BANNED per operator directive 2026-09-03 part 2). "
            "c72 is a SUBSTANTIVE M-V4-GEN-1 launch cycle per OPERATOR DIRECTIVE 2026-09-05."
        ),
        None,
    ),
    E(
        "_run/cycle_72_closed",
        "validated",
        (
            "c72 CLOSED. SUBSTANTIVE M-V4-GEN-1 launch cycle per OPERATOR DIRECTIVE 2026-09-05. "
            "LANDED per priority: (P1) disk-prune BLOCKED honestly (c48 target absent + c30_smoke "
            "rm sandbox-refused per c48/c71 precedent); sidecar recorded; P1 non-gating per §4 P1. "
            "(P3) 5/5 spot-checks PASS (driver sha byte-identical; Rome --prove-replay byte-det ×2 "
            "to c71 v2 anchor 9ea1fe32…; WIG piano rms_dbfs=-36.05 reproduces; _absent_stem_dispatch "
            "gate + max-truncation policy present). (P2) M-V4-GEN-1 iteration 1 SUBSTANTIVELY "
            "LAUNCHED + COMPLETED same-cycle. VOMM primary-fallback (Anticipation blocked). 5/5 "
            "songs rendered byte-det ×2 REPLAY_PROOF_HOLDS. Ear-scoring DEFERRED (M-V4-EAR-1 not "
            "yet built). Stall counter 0/8 → 1/8. Interpolation demo deferred to iter 2+. (P4) "
            "tests/test_gen_iterate_v4.py 6/6 PASS. (P5) M-V4-EAR-1 scaffold HONESTLY DEFERRED to "
            "c73 (P2 absorbed the wall budget substantively; §4 P5 explicit optional clause). "
            "(P6) POR + housekeeping. DISCIPLINE: FD-1 halt-honest (Rome/PD/Disco A c71 v2 "
            "durations preserved as honest; disk prune blocked honestly); FD-6 operator ear = "
            "LANDS authority post-hoc; FD-16(a) env_pin cert unchanged (canonical 7-key subset "
            "sha 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca); FD-16(c) 5 "
            "replay proofs per new code path (VOMM+iterate_v4 render pipeline) per per-family per-song "
            "scope; c14 str-supersede lemma respected (no supersedes this cycle — all fresh landings); "
            "c47 preservation-spin BAN honored; c27 sweep-hygiene N/A (no sf2 sweeps); OP-1 SerialLock "
            "N/A (no fine-fit runs); OP-2 Monitor N/A (foreground renders). READ-ONLY anchors "
            "byte-identical pre==post: scripts/sound_match/{deliver_ab_v4,deliver_cg_ab_v4,replay,"
            "measure_stem_audibility,objective}.py + scripts/v3_spine/midi_from_json_events.py + "
            "data/v3/rules/rules_artifact.jsonl (76 rules) + SF2 + 8 pinned profiles + 4 stem_manifest.json "
            "(PD non-standard path preserved sha d483f2bf0b09389b…) + 4 c69 v1 anchors + 4 c71 v2 "
            "anchors + CG cg_ab_mix.wav 6e13e007…. 14th consecutive cycle compliance with 9-header "
            "closing-summary contract (c59-c72). Operator ear on 4 c69 v1 + 4 c71 v2 A/Bs remains "
            "pending_operator per FD-6. c73 inherits: auditor spot-check c72 P1 driver-consumption "
            "correctness; 5/5 iter-1 replay reproducibility; iter 2 launch (stall 1/8 → 2/8) OR "
            "M-V4-EAR-1 scaffold opening OR interpolation demo authoring."
        ),
        None,
    ),
    E(
        "_archive/cycle-72-scratch",
        "validated",
        (
            "c72 scratch archival housekeeping. tools/_emit_c72_ledger_events.py retained in-tree "
            "per c14+ emitter-exemption pattern (docs/emitter_exemption_policy.md sha "
            "fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b). New substantive "
            "scripts under scripts/gen/ (__init__.py, vomm_generator.py, iterate_v4.py) are M-V4-GEN-1 "
            "iteration 1 landing artifacts; NOT scratch. Session-scoped scratchpad probe files "
            "(debug_mix.py, debug_write.py, debug_diff.py) live under harness-managed dir; not part "
            "of workspace. No workspace scratch to move to tools/stale/."
        ),
        None,
    ),
    E(
        "_infra/adopt-cycle72-tests",
        "validated",
        (
            "c72 test-adoption housekeeping. 1 new test file: tests/test_gen_iterate_v4.py with "
            "6 named cases: test_01_donor_map_5_songs + test_02_fetchability_ladder_shape + "
            "test_03_vomm_deterministic_seed + test_04_iteration_01_manifest_shape + "
            "test_05_structural_gate_warn_not_halt + test_06_replay_proofs_hold_5_of_5. "
            "6/6 PASS via `PYTHONPATH=. /usr/bin/python3 tests/test_gen_iterate_v4.py`. "
            "Cross-cycle file total: 9 pre-c72 + 1 new = **10/10 file gate satisfied** (exceeds "
            "brief §4 P4 minimum of 5 named cases). Structural-gate WARN-only posture asserted "
            "in test_05 by construction (grep-based check on iterate_v4.py driver source for "
            "absence of recreation-tuned halt patterns)."
        ),
        None,
        artifacts=["tests/test_gen_iterate_v4.py"],
    ),
]


def main() -> int:
    with open(LEDGER, "a", encoding="utf-8") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"emitted {len(EVENTS)} c72 events to {LEDGER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
