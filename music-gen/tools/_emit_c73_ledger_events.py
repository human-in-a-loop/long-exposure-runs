#!/usr/bin/env /usr/bin/python3
"""c73 ledger event emitter (one-shot, per c14+ emitter-exemption).

Emits 15 events per brief §3 expected count:
  P1 disk-prune known-blocked-class supersede (1)
  P2.a vomm-promoted-primary supersede of c70 anticipation (1)
  P2.b iter-02 launched (1) + completed (1) + 5 per-song (5)
  P2.c iter-01 manifests backfilled (1)
  P3 M-V4-EAR-1 scaffold opened (1)
  P5 register + closed + scratch + adopt-tests (4)
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
    "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

ROOT = Path("/home/user/long-exposure-runs/music-gen")
LEDGER = ROOT / "promise_ledger.jsonl"
NS = uuid.UUID("00000000-0000-0000-0000-000000000000")
CYCLE = 73
RUN_ID = "run-2026-09-05T235500Z"
TS = "2026-09-05T23:55:00Z"
ENV_PIN_SHA = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"

RATIONALE = (
    "c73 substantive: (P1) disk-prune consolidated to known-blocked class; "
    "(P2.a) Anticipation retry partial (git resolves, weights out-of-budget) -> VOMM promoted primary; "
    "(P2.b) iter-02 launched+completed, 5/5 REPLAY_PROOF_HOLDS with distinct SHAs; "
    "(P2.c) iter-01 manifests backfilled with c69-shape provenance, WAV bytes preserved; "
    "(P3) M-V4-EAR-1 scaffold opened (3-cycle defer streak broken); 5/5 tests green."
)

ITER02 = "data/v4/gen/iteration_02"

PER_SONG_SHAS = {
    "gen_v4_song_1": ("31a164f845f8e27e", "f43a570122722bbeff3c16029a1fbf01ff08cfa910d2b6b203a5bbab27051ee6"),
    "gen_v4_song_2": ("252eb21ce7df7328", "f7a5085a9bf7a970521d6f5da7aa89fe54b53c1e0fc229b5e293a59f1ed772cc"),
    "gen_v4_song_3": ("51e433ade2a845e1", "e40c7bcf14b48c6f4f8d6241ddcc9b516ed556040e98e0864d7d898e4fdb4b70"),
    "gen_v4_song_4": ("88d247468cb6d49f", "00e5887246b6ebbd95aec47c14a50447c99c2cfa34d5a24c51805a3aaea8d569"),
    "gen_v4_song_5": ("cdd2717e52820ff6", "156ad1555151cfa8e9e0df83eabb08d60cbcfc74d9605acced558a50f717a438"),
}


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


def per_song_event(sid: str):
    donor, sha = PER_SONG_SHAS[sid]
    return E(
        f"M-V4-GEN-1/iteration-02/{sid}",
        "validated",
        (
            f"c73 P2.b iter-02 per-song landing: {sid} (donor sha16 {donor}, seed=1). "
            f"VOMM-sampled 24 rules seeded '{sid}|donor={donor}|seed=1'. "
            f"ab_mix.wav sha {sha}. REPLAY_PROOF_HOLDS byte-det x2. ear_score=null (M-V4-EAR-1 scaffold-only)."
        ),
        None,
        artifacts=[
            f"{ITER02}/{sid}_donor_{donor}/ab_mix.wav",
            f"{ITER02}/{sid}_donor_{donor}/ab_mix.manifest.json",
            f"{ITER02}/{sid}_donor_{donor}/ab_mix.replay_proof.json",
        ],
    )


EVENTS = [
    E(
        "_infra/disk-prune-known-blocked-class",
        "validated",
        (
            "c73 P1 consolidation supersede. c48/c71/c72 have all halt-honest-deferred the same "
            "df>=85% prune with the same rationale (no regenerable sweep audio to prune; deliveries/"
            "corpus/weights/model caches are prohibited targets per campaign prompt L155). Attempts "
            "at rm sandbox-refused; c48-disclosed target data/v4/regression/c31_smoke/guitar_fine_legacy "
            "(~946 MB) is absent on this instance. Promoted to known-blocked class; operator adjudication "
            "owns any prune from here (guidance channel). Stop retrying per-cycle. NOT preservation-spin: "
            "this is the terminal disposition of a repeating-blocked pattern, not per-cycle carry."
        ),
        "_infra/c72-disk-prune-blocked-honest-deferral",
    ),
    E(
        "_gen/vomm-promoted-primary",
        "validated",
        (
            "c73 P2.a supersede of c70 M-V4-GEN-1/generator-survey primary designation. "
            "Anticipation retry executed once: PyPI HTTP 404 no-matching-distribution; "
            "git-clone dry-run RESOLVES (commit af37397922665a0fb8d474d7988b0f3755a38d45) but "
            "pretrained weights fetch out of single-cycle preemption budget. VOMM continues primary "
            "for c73+ per brief rule 'if it fails, emit _gen/vomm-promoted-primary and stop retrying'. "
            "Anticipation code-fetch viable for c74+ if weights probe succeeds. "
            "VOMM generator_hash e25b520372ff6abd63a5636342ff7735f85d07509776db91682a19a861054e38 pinned."
        ),
        "M-V4-GEN-1/generator-survey",
    ),
    E(
        "M-V4-GEN-1/iteration-02-launched",
        "validated",
        (
            "c73 P2.b iteration 2 LAUNCHED (foreground; wall ~40s). Driver "
            "scripts/gen/iterate_v4.py --iteration 2 --generator vomm --seed 1 --out "
            "data/v4/gen/iteration_02 --prove-replay. Same 5 donors as iter-01. Seed shift "
            "0->1 per brief rule ensures each song produces distinct novel MIDI vs iter-01. "
            "env_pin canonical 7-key subset unchanged. Rules artifact sha e19fb205b282dabb... "
            "unchanged. All READ-ONLY anchors byte-identical pre==post. Stall counter 1/8 -> 2/8."
        ),
        None,
        artifacts=[
            f"{ITER02}/fetchability_ladder.jsonl",
            "data/v4/gen/stall_counter.json",
        ],
    ),
    E(
        "M-V4-GEN-1/iteration-02-completed",
        "validated",
        (
            "c73 P2.b iteration 2 COMPLETED. 5/5 songs REPLAY_PROOF_HOLDS byte-det x2. Per-song "
            "mix SHAs distinct from iter-01 anchors: song_1 f43a5701..., song_2 f7a5085a..., "
            "song_3 e40c7bcf..., song_4 00e58872..., song_5 156ad155.... Iteration rollup at "
            f"{ITER02}/iteration_rollup.json. Ear-scoring DEFERRED (each manifest carries "
            "ear_score=null + ear_score_reason=M_V4_EAR_1_not_yet_built). Interpolation-hybrid "
            "demo (CG<->PD t=0.5) still deferred per optional clause. Disk delta +83 MB."
        ),
        None,
        artifacts=[f"{ITER02}/iteration_rollup.json"],
    ),
    per_song_event("gen_v4_song_1"),
    per_song_event("gen_v4_song_2"),
    per_song_event("gen_v4_song_3"),
    per_song_event("gen_v4_song_4"),
    per_song_event("gen_v4_song_5"),
    E(
        "M-V4-GEN-1/iteration-01-manifests-backfilled",
        "validated",
        (
            "c73 P2.c iter-01 manifest back-fill. 5/5 ab_mix.manifest.json files annotated in-place "
            "with provenance.<stem>.render_family (vomm_generated_midi_via_sf2 for bass+drums; "
            "absent_no_generator_output for guitar/piano/other/vocals per campaign L64 'generated "
            "songs are INSTRUMENTAL') + per-stem 'audible' flag + preserved-original-sha field "
            "_original_ab_mix_manifest_sha256. WAV bytes verified byte-identical pre==post "
            "(5/5 asserted in-script). Manifest sha drifts by design. Backfill via "
            "tools/_backfill_iter01_manifests_c73.py."
        ),
        None,
        artifacts=[
            "data/v4/gen/iteration_01/gen_v4_song_1_donor_31a164f845f8e27e/ab_mix.manifest.json",
            "data/v4/gen/iteration_01/gen_v4_song_2_donor_252eb21ce7df7328/ab_mix.manifest.json",
            "data/v4/gen/iteration_01/gen_v4_song_3_donor_51e433ade2a845e1/ab_mix.manifest.json",
            "data/v4/gen/iteration_01/gen_v4_song_4_donor_88d247468cb6d49f/ab_mix.manifest.json",
            "data/v4/gen/iteration_01/gen_v4_song_5_donor_cdd2717e52820ff6/ab_mix.manifest.json",
        ],
    ),
    E(
        "M-V4-EAR-1/scaffold-opened",
        "validated",
        (
            "c73 P3 M-V4-EAR-1 scaffold OPENED (3-consecutive-defer streak c70/c71/c72 broken). "
            "Ships: (a) scripts/ear/v4_ear.py CLAP+VGGish ensemble stub with public API "
            "build_exemplar_signatures/score_audio/leave_one_out all raising "
            "NotImplementedError('c74+ substantive implementation'); (b) data/v4/ear/exemplar_set.json "
            "with 5 exemplars per campaign L112 (CG+PD sha16 resolved; Molasses/Essence/Desire "
            "sha16=PENDING_c74_lookup honest); (c) tests/test_ear_v4_scaffold.py 5/5 PASS. "
            "Spec constants pinned per campaign L114: WINDOW_SECONDS=10, BEST_FRACTION=0.5, "
            "RATING_ANCHOR_HIGH=7, NOISE_FLOOR_DEFAULT=0.15. Sanity gate per campaign L115-117: "
            ">=4/5 exemplars >=6, none < 5.5. NO corpus calibration (operator simplification 2026-09-03). "
            "CLAP/VGGish fetchability probe deferred to c74+."
        ),
        None,
        artifacts=[
            "scripts/ear/v4_ear.py",
            "data/v4/ear/exemplar_set.json",
            "tests/test_ear_v4_scaffold.py",
        ],
    ),
    E(
        "_plan/register-c73-substantive-and-gen-iter-02-sub-leaves",
        "validated",
        (
            "c73 POR registration: 13 new c73 milestone_ids added inline in the ## Milestones "
            "section (parseable region) to satisfy the promise_check POR parser boundary before "
            "## Sub-milestones. Enumerated: P1 disk-prune known-blocked-class (1) + P2.a "
            "vomm-promoted-primary (1) + P2.b iter-02 launched (1) + completed (1) + 5 per-song "
            "(5) + P2.c iter-01 backfill (1) + P3 EAR-1 scaffold (1) + housekeeping (register + "
            "closed + scratch + adopt-tests = 4) = 13 total. NO preservation-spin (BANNED per c47 "
            "omnibus part 4). NO wait-on-operator memo (BANNED per operator directive 2026-09-03 part 2). "
            "c73 is a SUBSTANTIVE iteration-2 launch + EAR-1 scaffold-opening cycle."
        ),
        None,
    ),
    E(
        "_run/cycle_73_closed",
        "validated",
        (
            "c73 CLOSED. SUBSTANTIVE cycle: iteration 2 landed 5/5 REPLAY_PROOF_HOLDS + EAR-1 "
            "scaffold opened. LANDED per priority: (P1) _infra/disk-prune-known-blocked-class "
            "consolidation supersede - c48/c71/c72 pattern retired; per-cycle retry stops. "
            "(P2.a) Anticipation retry executed once: PyPI still 404; git-clone dry-run RESOLVES "
            "(partial - commit af37397922665a0f...) but weights out of budget; _gen/vomm-promoted-primary "
            "supersede emitted; VOMM continues primary. (P2.b) M-V4-GEN-1 iteration 2 launched+completed "
            "via VOMM seed=1: 5/5 songs REPLAY_PROOF_HOLDS byte-det x2 with distinct SHAs from iter-01. "
            "Stall counter 1/8 -> 2/8. Interpolation demo still deferred. (P2.c) iter-01 manifest "
            "back-fill: 5/5 annotated with c69-shape provenance; WAV bytes byte-identical. (P3) M-V4-EAR-1 "
            "scaffold opened: v4_ear.py + exemplar_set.json + 5/5 test cases; defer-streak broken. "
            "(P4) Freshness cache skipped re-audit (no input sha drift). (P5) housekeeping. "
            "DISCIPLINE: FD-1 halt-honest (Anticipation partial-viability recorded; disk-prune consolidated); "
            "FD-6 operator ear = LANDS authority post-hoc; FD-16(a) env_pin cert unchanged (2ac444c3...922ca); "
            "FD-16(c) 5 replay proofs (same code path as iter-01 so no NEW proof required per relaxation, "
            "but proofs emitted anyway as strong evidence); c14 str-supersede lemma respected (2 supersedes: "
            "disk-prune + vomm-primary, both str); c47 preservation-spin BAN honored; c27 sweep-hygiene N/A; "
            "OP-1 SerialLock N/A; OP-2 Monitor N/A. READ-ONLY anchors byte-identical pre==post: "
            "scripts/sound_match/{deliver_ab_v4 937f99a8...,deliver_cg_ab_v4 3c454652...,replay 1f430270...,"
            "measure_stem_audibility c40b76e4...,objective 8087ce80...}.py + scripts/v3_spine/"
            "midi_from_json_events.py + data/v3/rules/rules_artifact.jsonl e19fb205... (76 rules) + SF2 "
            "74594e8f...1cb0 + 8 pinned profiles + 4 stem_manifest.json (PD d483f2bf...) + 4 c69 v1 anchors + "
            "4 c71 v2 anchors + CG cg_ab_mix.wav 6e13e007... + scripts/gen/{__init__,vomm_generator,iterate_v4}.py "
            "(c72-landed, byte-identical). 15th consecutive cycle compliance with 9-header closing-summary "
            "contract (c59-c73). Operator ear on 4 c69 v1 + 4 c71 v2 + 5 c72 iter-01 + 5 c73 iter-02 A/Bs "
            "remains pending_operator per FD-6. c74 inherits: (i) auditor spot-check c73 iter-02; (ii) fetch "
            "CLAP/VGGish weights + wire ear scoring end-to-end; (iii) resolve Molasses/Essence/Desire sha16 "
            "from corpus manifest; (iv) iter-03 launch (stall 2/8 -> 3/8) OR interpolation-hybrid demo authoring; "
            "(v) if disk hits 90% df_guard, request operator prune approval per P1 consolidation."
        ),
        None,
    ),
    E(
        "_archive/cycle-73-scratch",
        "validated",
        (
            "c73 scratch archival housekeeping. tools/_emit_c73_ledger_events.py + "
            "tools/_backfill_iter01_manifests_c73.py retained in-tree per c14+ emitter-exemption "
            "pattern (docs/emitter_exemption_policy.md sha fd2c33a7...). New substantive scripts "
            "scripts/ear/v4_ear.py + data data/v4/ear/exemplar_set.json are M-V4-EAR-1 "
            "scaffold-opening landing artifacts; NOT scratch. No workspace scratch to move to tools/stale/."
        ),
        None,
    ),
    E(
        "_infra/adopt-cycle73-tests",
        "validated",
        (
            "c73 test-adoption housekeeping. 1 new test file: tests/test_ear_v4_scaffold.py "
            "with 5 named cases: test_01_module_imports_and_stubs_raise + "
            "test_02_exemplar_set_structural_validation + test_03_spec_compliant_window_size_constant + "
            "test_04_no_prng_no_sidecar_no_vst3_state + test_05_env_pin_manifest_canonical. "
            "5/5 PASS via PYTHONPATH=. /usr/bin/python3 tests/test_ear_v4_scaffold.py. "
            "Cross-cycle file total: 10 pre-c73 + 1 new = 11/11 file gate satisfied. Regression: "
            "tests/test_gen_iterate_v4.py 6/6 PASS unchanged (test_04 iter-01 manifest shape still "
            "validates after c73 P2.c backfill - asserts structural fields, not manifest SHA)."
        ),
        None,
        artifacts=["tests/test_ear_v4_scaffold.py"],
    ),
]


def main() -> int:
    with open(LEDGER, "a", encoding="utf-8") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"emitted {len(EVENTS)} c73 events to {LEDGER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
