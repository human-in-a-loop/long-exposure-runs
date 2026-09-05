#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-05T19:00:00Z
# cycle: 71
# run_id: run-2026-09-05T190000Z
# agent: worker
# milestone: _archive/cycle-71-scratch
# ---
"""c71 ledger event emitter (one-shot, per c14+ emitter-exemption).

Emits 12 events: 1 driver-fix + 4 v2 render sub-leaves + 1 completion-report
amendment + 1 WIG v1 manifest supersede-note + 1 gen iteration-01 deferral +
1 POR-register + 1 cycle-closed + 2 housekeeping.

Discipline:
  - UUID5 content-hash event_id (canonical-JSON minus event_id + ts)
  - `_STATUS_ENUM` per c14 str-supersede lemma (str, never list)
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

if sys.executable != "/usr/bin/python3":
    raise RuntimeError("emit_c71 requires /usr/bin/python3")

ROOT = Path("/home/user/long-exposure-runs/music-gen")
LEDGER = ROOT / "promise_ledger.jsonl"
NS = uuid.UUID("00000000-0000-0000-0000-000000000000")
CYCLE = 71
RUN_ID = "run-2026-09-05T190000Z"
TS = "2026-09-05T19:00:00Z"
ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"


def _cid(event: dict) -> str:
    payload = {k: v for k, v in event.items() if k not in ("event_id", "ts")}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return str(uuid.uuid5(NS, body))


def E(milestone_id, status, narrative, supersedes_path, artifacts=None, confidence="high"):
    ev = {
        "milestone_id": milestone_id,
        "status": status,
        "confidence": {
            "level": confidence,
            "rationale": (
                "c71 substantive render-defect fix per OPERATOR DIRECTIVE 2026-09-05; "
                "byte-det ×2 replay proof HOLDS on 4 v2 renders; v1 anchors byte-identical; "
                "10/10 tests green; env_pin canonical 7-key subset unchanged."
            ),
            "assessor": "worker",
        },
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


EVENTS = [
    E(
        "_infra/deliver-ab-v4-render-defect-fix-c71",
        "validated",
        (
            "c71 P1 CRITICAL: fixed scripts/sound_match/deliver_ab_v4.py render path per OPERATOR "
            "DIRECTIVE 2026-09-05. c63 skip-close policy was documented (htdemucs stem substitution "
            "as default for unprofiled audible stems per c14 CG-drums + c15 CG-guitar OPT3 precedent) "
            "but c69 driver implemented only the absent-silent branch. Additive fix: (i) new "
            "_absent_stem_dispatch(stem_name, stems_dir, root) helper gates on "
            "measure_stem_audibility.measure().verdict_audible (silence floor -60 dBFS per c14); "
            "(ii) 3 new branches (guitar/piano/other) in _render_ab_mix call the dispatch — "
            "AUDIBLE branch splices htdemucs stereo int16 into mix with rms_normalize_gain=1.0 "
            "(reference IS source); SILENT branch retains c69 absent semantics with new "
            "absent_no_audible_signal label + audibility fields; (iii) truncation policy "
            "min(bass,drums,vocals) → max(bass,drums,vocals,*audible), shorter cells zero-pad to "
            "longest (fixes WIG partial-mix as side effect: 11.249s → 30.000s); (iv) --out-suffix "
            "CLI flag (default empty preserves c69 output naming; 'v2' → sibling files); "
            "(v) _mix.sum_method string updated to float_accumulate_peaklimit_099_max_len_zero_pad. "
            "Pre-edit sha 52ff05e28d2feb551e6bad03fa4115399fb7fc554fc7c3ab5351882affc92aec; "
            "post-edit sha 937f99a80ce23cfd3255f9133ec564230a0ca1b9fa9b45707b0eed2c453b094c. "
            "AST-parse PASS. Smoke: Rome v2 render (fastest, guitar-only substitution) end-to-end "
            "PASS. READ-ONLY anchors byte-identical pre==post: deliver_cg_ab_v4.py "
            "(3c45465284e2f78a…), replay.py (1f43027039c45f5e…), measure_stem_audibility.py "
            "(c40b76e4f7f1af7c…), objective.py (8087ce80…), _sweep_hygiene_c27.py, "
            "_serial_lock_op1.py. supersedes_path=null (new fix class per c14 lemma)."
        ),
        None,
        artifacts=["scripts/sound_match/deliver_ab_v4.py"],
    ),
    E(
        "M-V4-SHOWCASE-1/wig-ab-full-render-v2",
        "validated",
        (
            "c71 P3 WIG (sha16 252eb21ce7df7328) v2 A/B mix landing. Delivery trio at "
            "data/v4/deliveries/252eb21ce7df7328/ab_mix_v2.{wav,manifest.json,replay_proof.json}. "
            "WAV sha 29de5ee222f2d8489dcc15caedc33908bfaa72c9094ee299318457cbae060918, 30.000s "
            "@ 44.1 kHz stereo. REPLAY_PROOF_HOLDS byte-det ×2 (run1==run2). Audible substitutions "
            "per c71 P2 empirical audibility probe: piano (rms_dbfs=-36.05 dBFS, NEW c71 finding "
            "vs brief expectation 'probe and record'; above -60 dB floor) + other (rms_dbfs=-19.40 "
            "dBFS, matches operator's -19.1 LOUD). Silent: guitar (rms_dbfs=-69.55). Bass+drums "
            "via c69 sf2 profiles unchanged. Vocals htdemucs hybrid overlay per campaign L59-60. "
            "c69 v1 anchor 6feca5d1fb41ee149e727b6ec2a61d2a006b4bc0b2a0aff62f2ef8946f47e3e9 "
            "byte-identical pre==post. v1 duration 11.249s → v2 30.000s (bass/drums MIDI ~9s "
            "zero-pad up to vocals 30s under max-truncation). supersedes_path str per c14 lemma."
        ),
        "data/v4/deliveries/252eb21ce7df7328/ab_mix.wav",
        artifacts=[
            "data/v4/deliveries/252eb21ce7df7328/ab_mix_v2.wav",
            "data/v4/deliveries/252eb21ce7df7328/ab_mix_v2.manifest.json",
            "data/v4/deliveries/252eb21ce7df7328/ab_mix_v2.replay_proof.json",
            "data/v4/deliveries/252eb21ce7df7328/audibility_v2.json",
        ],
    ),
    E(
        "M-V4-SHOWCASE-1/rome-ab-full-render-v2",
        "validated",
        (
            "c71 P3 Rome (sha16 51e433ade2a845e1) v2 A/B mix landing. WAV sha "
            "9ea1fe324677b01e623dc1c2a4a7d409182f03c494d7a8d4ee110eca6dfad14f, 32.707s "
            "(max-truncation preserves SF2 release tail on bass/drums render past 30s reference "
            "stems — HALT-HONEST per FD-1, brief expected 30s but SF2 tail dominates; not a "
            "defect). REPLAY_PROOF_HOLDS byte-det ×2. Audible substitutions: guitar only "
            "(rms_dbfs=-26.21 dBFS, matches operator's -24.0 AUDIBLE). Silent: piano (-72.42), "
            "other (-78.15). c69 v1 anchor 81e2ef1525ed4485a497c60dece0e29dffc0b1fedfa593ac8a457f70541b26b0 "
            "byte-identical pre==post. supersedes_path str per c14 lemma."
        ),
        "data/v4/deliveries/51e433ade2a845e1/ab_mix.wav",
        artifacts=[
            "data/v4/deliveries/51e433ade2a845e1/ab_mix_v2.wav",
            "data/v4/deliveries/51e433ade2a845e1/ab_mix_v2.manifest.json",
            "data/v4/deliveries/51e433ade2a845e1/ab_mix_v2.replay_proof.json",
            "data/v4/deliveries/51e433ade2a845e1/audibility_v2.json",
        ],
    ),
    E(
        "M-V4-SHOWCASE-1/peach-dream-ab-full-render-v2",
        "validated",
        (
            "c71 P3 Peach Dream (sha16 88d247468cb6d49f) v2 A/B mix via _resolve_stems_root "
            "invariant (d) fallback (stems live at operator_section_c25_checkpointed/rc9_6stem/). "
            "WAV sha e164c42bc192de789984267f45c5acc16da3f845debba18415685d50b0afa7ce, 32.695s "
            "(SF2 tail preserved). REPLAY_PROOF_HOLDS byte-det ×2. Audible substitutions: other "
            "only (rms_dbfs=-19.65 dBFS, matches operator's -17.7 LOUD). Silent: guitar (-79.81), "
            "piano (-70.09). c69 v1 anchor a300cf4ca12f132e24dc34bcafb4cf4bc621d9529f9de67442afeac3cc02d806 "
            "byte-identical pre==post. stem_manifest.json sha "
            "d483f2bf0b09389bec5186cdbde8a89393dbedc8288a7805c72f13bf3634cdd4 byte-identical "
            "(c65 P0 Branch C canonical). supersedes_path str per c14 lemma."
        ),
        "data/v4/deliveries/88d247468cb6d49f/ab_mix.wav",
        artifacts=[
            "data/v4/deliveries/88d247468cb6d49f/ab_mix_v2.wav",
            "data/v4/deliveries/88d247468cb6d49f/ab_mix_v2.manifest.json",
            "data/v4/deliveries/88d247468cb6d49f/ab_mix_v2.replay_proof.json",
            "data/v4/deliveries/88d247468cb6d49f/audibility_v2.json",
        ],
    ),
    E(
        "M-V4-SHOWCASE-1/disco-a-ab-full-render-v2",
        "validated",
        (
            "c71 P3 Disco A (sha16 cdd2717e52820ff6) v2 A/B mix landing. WAV sha "
            "77cd593a48dbbb27efcd07c87a840d96d841e7eb29b3aee1f46b4531f8feb5f6, 36.476s (all 3 "
            "unprofiled stems audible + SF2 tail preserved). REPLAY_PROOF_HOLDS byte-det ×2. "
            "Audible substitutions: guitar (rms_dbfs=-25.08 dBFS, matches operator's -24.8) + "
            "piano (-21.82, matches -21.6) + other (-20.95, matches -20.8). No silent stems "
            "this song — every unprofiled cell substituted. c69 v1 anchor "
            "1b673106aae19b9ccd6f9d81333eae9e906a1dba1e85df38fb3041c8ea494080 byte-identical "
            "pre==post. supersedes_path str per c14 lemma."
        ),
        "data/v4/deliveries/cdd2717e52820ff6/ab_mix.wav",
        artifacts=[
            "data/v4/deliveries/cdd2717e52820ff6/ab_mix_v2.wav",
            "data/v4/deliveries/cdd2717e52820ff6/ab_mix_v2.manifest.json",
            "data/v4/deliveries/cdd2717e52820ff6/ab_mix_v2.replay_proof.json",
            "data/v4/deliveries/cdd2717e52820ff6/audibility_v2.json",
        ],
    ),
    E(
        "_plan/completion-report-v2-c71-amendment",
        "validated",
        (
            "c71 P4 amendment: appended '## Section: c71 render-defect fix: c63 skip-close "
            "policy application deferred at c69, honored at c71' to docs/v4_completion_report_v2.md. "
            "Pre-append sha 500068c663ba1d168c8ee2eacc7c387c547504cc53959d58a4f7b2b550daef20; "
            "post-append sha 341d5bbaf859c8cadc9a9f4b661b51d72f23a508f2296f28c6ab532a6a8b4bd9. "
            "Contents: operator directive verbatim, root cause, fix summary (5 additive changes "
            "+ pre/post SHAs), per-song audibility measurements table (12 probes), per-song v2 "
            "delivery table (4 SHAs + durations + audible substitutions + replay verdicts), "
            "honest disclosures (Rome/PD/Disco A v2 32-36s from SF2 tail preservation is "
            "HALT-HONEST per FD-1, not a defect), env_pin unchanged, test coverage 10/10. "
            "Append-only; supersedes_path=null."
        ),
        None,
        artifacts=["docs/v4_completion_report_v2.md"],
    ),
    E(
        "_selection/wig-v1-manifest-superseded-by-v2-note",
        "validated",
        (
            "c71 P3 §5 follow-up: appended superseded_by_v2_max_truncation block to "
            "data/v4/deliveries/252eb21ce7df7328/ab_mix.manifest.json. WAV bytes byte-identical "
            "pre==post (6feca5d1fb41ee149e727b6ec2a61d2a006b4bc0b2a0aff62f2ef8946f47e3e9 asserted "
            "after write). Block cites v2 sibling wav sha "
            "29de5ee222f2d8489dcc15caedc33908bfaa72c9094ee299318457cbae060918, v2 manifest + "
            "replay-proof paths, v2 duration 30.000s, cycle 71. c70 P1 wig_duration_diagnostic "
            "block preserved verbatim within manifest. Append-only annotation; supersedes_path=null."
        ),
        None,
        artifacts=["data/v4/deliveries/252eb21ce7df7328/ab_mix.manifest.json"],
    ),
    E(
        "M-V4-GEN-1/iteration-01-deferred-c71",
        "in-progress",
        (
            "c71 P5 HONEST DEFERRAL. M-V4-GEN-1 iteration 1 (Anticipation primary generator per "
            "c70 survey score 4.7/5, on CG donor sha16 31a164f845f8e27e, seed=0, detached driver "
            "launch per c24 checkpointed-driver policy) DEFERRED to c72 per c71 wall budget "
            "compression (P1-P4 fix work absorbed the cycle; single-cycle preemption budget per "
            "operator directive #4 explicitly authorized). Disk at c71 open 85% > 82% precondition "
            "— c72 first-act must prune disk before detached launch per c47+ sweep-hygiene policy. "
            "Stall counter remains 0/8 (not incremented; iteration 1 has not run). Resume command "
            "for c72: `nohup /usr/bin/python3 scripts/gen/iterate_v4.py --iteration 1 --generator "
            "anticipation --donor 31a164f845f8e27e --seed 0 --out data/v4/gen/iteration_01 > "
            "data/v4/logs/gen_iter_01_c72.log 2>&1 &`. NOT preservation-spin — operator directive #4 "
            "authorizes single-cycle preemption for the render-defect fix. All 4 M-V4-GEN-1 c70 "
            "sub-milestone scaffolds preserved byte-identical."
        ),
        None,
        artifacts=[],
    ),
    E(
        "_plan/register-c71-render-defect-fix-and-v2-renders",
        "validated",
        (
            "c71 POR registration row: 9 new c71 substantive milestone_ids added inline in the "
            "## Milestones section (parseable region) to satisfy promise_check POR parser boundary "
            "before ## Sub-milestones. Enumerated per c71 §4 P8 narrative discipline: driver-fix "
            "(1) + 4 v2-render sub-leaves + completion-report-amendment (1) + WIG-v1-manifest-"
            "supersede-note (1) + gen-iteration-01-deferred (1) + this register row (9 total "
            "substantive) plus 3 housekeeping tail rows (_run/cycle_71_closed + _archive/cycle-71-"
            "scratch + _infra/adopt-cycle71-tests). NO preservation-spin (BANNED per c47 operator "
            "omnibus part 4). NO wait-on-operator memo (BANNED per operator directive 2026-09-03 "
            "part 2). c71 is SUBSTANTIVE render-defect-fix cycle per OPERATOR DIRECTIVE 2026-09-05."
        ),
        None,
        artifacts=["plan_of_record.md"],
    ),
    E(
        "_run/cycle_71_closed",
        "validated",
        (
            "c71 CLOSED. SUBSTANTIVE PIVOT per OPERATOR DIRECTIVE 2026-09-05. LANDED per priority: "
            "(P1) deliver_ab_v4.py render-path fix (pre 52ff05e2… → post 937f99a8…; AST+smoke PASS). "
            "(P2) 12 audibility probes; per-song audibility_v2.json emitted; findings — Rome "
            "+guitar; PD +other; Disco A +guitar+piano+other; WIG +piano+other (piano AUDIBLE at "
            "-36.05 dBFS is new c71 finding). (P3) 4 v2 A/B mixes REPLAY_PROOF_HOLDS ×4: WIG "
            "29de5ee2… 30.000s, Rome 9ea1fe32… 32.707s, PD e164c42b… 32.695s, Disco A 77cd593a… "
            "36.476s; c69 v1 anchors byte-identical (6feca5d1…, 81e2ef15…, a300cf4c…, 1b673106…). "
            "(P4) POR entry + docs/v4_completion_report_v2.md amended (pre 500068c6… post "
            "341d5bba…) + WIG v1 manifest superseded_by_v2_max_truncation block appended (WAV "
            "byte-identical). (P5) M-V4-GEN-1 iteration 1 HONESTLY DEFERRED to c72 (single-cycle "
            "preemption per operator directive #4). (P6) tests/test_deliver_ab_v4.py extended "
            "in-place 6→10 cases; 10/10 PASS. (P7) housekeeping tail: this row + _archive/cycle-71-"
            "scratch + _infra/adopt-cycle71-tests. (P8) narrative discipline enforced. DISCIPLINE: "
            "FD-1 halt-honest (Rome/PD/Disco A v2 32-36s from SF2 tail preservation disclosed as "
            "HALT-HONEST, not defect); FD-6 operator ear = LANDS authority post-hoc; FD-16(a) "
            "env_pin cert unchanged (2ac444c3…922ca); FD-16(c) 4 replay proofs per-family+per-song "
            "for NEW code path; c14 str-supersede lemma respected (4 v2 render rows str "
            "supersedes_path); c47 preservation-spin BAN honored; OP-1 N/A; OP-2 REMAINS RETIRED. "
            "READ-ONLY anchors byte-identical pre==post. No operator ear verdict yet on 4 v2 A/Bs "
            "(all pending_operator per FD-6). 13th consecutive cycle compliance with 9-header "
            "closing-summary contract (c59-c71). Honesty disclosures: (a) WIG piano AUDIBLE at "
            "-36.05 dBFS is a NEW c71 empirical finding beyond brief expectation of just probing "
            "guitar+piano for completeness; (b) Rome/PD/Disco A v2 durations 32.707-36.476s "
            "exceed brief P3 §4 predicted 30.000s because SF2 release tail on bass/drums render "
            "extends past reference stem duration and max-truncation preserves it — HALT-HONEST "
            "per FD-1, not a defect."
        ),
        None,
        artifacts=[],
    ),
    E(
        "_archive/cycle-71-scratch",
        "validated",
        (
            "c71 scratch archival housekeeping. tools/_emit_c71_ledger_events.py retained "
            "in-tree per c14+ emitter-exemption pattern (docs/emitter_exemption_policy.md sha "
            "fd2c33a78d147341ebfa8df84e80002ff6337779bb3e58e1305de9e936e4eb6b). Session-scoped "
            "scratchpad files (probe_audibility.py, wig_v1_manifest_append.py, insert_c71_rows.py) "
            "live under harness-managed dir and are not part of the workspace. No workspace scratch "
            "moved to tools/stale/."
        ),
        None,
        artifacts=["tools/_emit_c71_ledger_events.py"],
    ),
    E(
        "_infra/adopt-cycle71-tests",
        "validated",
        (
            "c71 test-adoption housekeeping. No new test file this cycle; "
            "tests/test_deliver_ab_v4.py extended in-place with 4 new c71 cases (test_07 htdemucs "
            "substitution when audible + test_08 stays silent when below floor + test_09 "
            "max-truncation policy + test_10 v2 output suffix sibling files) per c18 additive "
            "pattern. Cross-cycle file total: 9 pre-c71 + 1 (extended in-place, not new file) = "
            "9/9 file gate holds. In-place case count: 6 pre-c71 + 4 c71 = 10/10 PASS via "
            "PYTHONPATH=. /usr/bin/python3 tests/test_deliver_ab_v4.py. Closes c70 auditor P2 "
            "test debt for the new c71 render-defect fix code path."
        ),
        None,
        artifacts=["tests/test_deliver_ab_v4.py"],
    ),
]


def main() -> int:
    for k, v in _PINS.items():
        if os.environ.get(k) != v:
            raise RuntimeError("env pin drift " + k)
    lines_before = sum(1 for _ in LEDGER.open())
    with LEDGER.open("a") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True) + "\n")
    lines_after = sum(1 for _ in LEDGER.open())
    print("APPENDED " + str(len(EVENTS)) + " events")
    print("Ledger lines: " + str(lines_before) + " → " + str(lines_after))
    for ev in EVENTS:
        print(ev["milestone_id"] + " " + ev["event_id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
