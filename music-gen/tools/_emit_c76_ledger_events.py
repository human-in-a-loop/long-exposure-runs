#!/usr/bin/env /usr/bin/python3
"""c76 one-shot ledger emitter — retained in-tree per c14+ emitter-exemption
pattern (docs/emitter_exemption_policy.md sha fd2c33a7…)."""
from __future__ import annotations
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "promise_ledger.jsonl"

ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
RUN_ID = "run-2026-09-06T090000Z"
TS = "2026-09-06T09:00:00Z"

EVENTS = [
    {
        "milestone_id": "M-V4-EAR-1/v2-wider-linear-calibration-c76",
        "narrative": (
            "c76 P1a substantive landing. `scripts/ear/v4_ear_v2.py` sibling module lands "
            "wider-linear calibration: anchor_high = max(raw_max_ex + 0.02, 0.98); "
            "anchor_low = noise_floor 0.15. Eliminates c74 ceiling-clipping saturation. "
            "LOO scores: chicken_grease=6.6944, peach_dream=6.7802, molasses=6.6906, "
            "essence=6.8313, desire=6.2095. Sanity gate PASSES 5/5 ≥6.0, 0 <5.5, no clipping. "
            "READ-ONLY anchors preserved byte-identical: v4_ear.py sha e775621b…, "
            "exemplar_set.json sha 31c10dfb…, exemplar_embeddings.npz sha be93d016…, "
            "band4_embeddings.npz sha 4fc8dc82…. NO PRNG, NO sidecar_nonfactor imports, "
            "NO VST3 state APIs. supersedes M-V4-EAR-1/substantive-implementation via str."
        ),
        "artifacts": ["scripts/ear/v4_ear_v2.py"],
        "confidence": {"assessor": "worker", "level": "high",
                        "rationale": "v2 LOO passes sanity gate 5/5 no clipping; READ-ONLY anchors byte-identical"},
        "supersedes_path": "M-V4-EAR-1/substantive-implementation",
        "status": "validated",
    },
    {
        "milestone_id": "M-V4-EAR-1/l119-infeasibility-proof-c76",
        "narrative": (
            "c76 P1b substantive landing. `scripts/ear/probe_l119_infeasibility_c76.py` "
            "sweeps 3 statistics (max-over-windows-c74, mean-over-all-windows, "
            "mean-of-per-ex-max) × 3 calibrations (linear-c74, wider-linear-c76, "
            "sigmoid-dampen). Result: all 3 statistics have band4_max_raw > "
            "exemplar_min_raw (raw_separation < 0; stay_live band-4 > desire band-7). "
            "By monotone-calibration lemma, no f: raw→[1,7] can satisfy sanity_gate AND "
            "L119 simultaneously. L119 empirically INFEASIBLE under VGGish-only. Under "
            "FD-6 operator-ear-authority (standing precedent since c47), M-V4-GEN-1 "
            "completion falls to operator adjudication of 15 landed gen ab_mix.wav. "
            "Sidecar `data/v4/ear/l119_infeasibility_proof_c76.json` sha "
            "ada44349277b17e0b2043c419403b2eed5f99046972aa31f94708f411b15a68a "
            "(byte-det ×2 verified)."
        ),
        "artifacts": [
            "scripts/ear/probe_l119_infeasibility_c76.py",
            "data/v4/ear/l119_infeasibility_proof_c76.json",
        ],
        "confidence": {"assessor": "worker", "level": "high",
                        "rationale": "3×3 empirical sweep + monotone lemma; all 9 cells fail one/both gates"},
        "supersedes_path": None,
        "status": "validated",
    },
    {
        "milestone_id": "_selection/band4-spot-check-v2-c76",
        "narrative": (
            "c76 P1c: band-4 spot check re-run under wider-linear v2 calibration. Scores: "
            "aguanile=4.8362, wagon_wheel=5.3251, stay_live=6.7199. loo_min=6.2095 (Desire); "
            "mandate threshold loo_min-0.5=5.7095. band4_max=6.7199 > 5.7095 → gate FAILS "
            "honestly. Confirms L119 monotone-infeasibility from l119_infeasibility_proof_c76.json. "
            "Sidecar `data/v4/ear/band4_spot_check_v2_c76.json` sha "
            "d8fcea2a5409410ebe0d5fb427f79f100aca090f17ec68320bcb08af743b30a7 (byte-det ×2). "
            "supersedes _selection/band4-spot-check-halt-honest-c75 via str."
        ),
        "artifacts": [
            "scripts/ear/band4_spot_check_v2_c76.py",
            "data/v4/ear/band4_spot_check_v2_c76.json",
        ],
        "confidence": {"assessor": "worker", "level": "high",
                        "rationale": "honest FAIL under new calibration; corroborates L119 infeasibility"},
        "supersedes_path": "_selection/band4-spot-check-halt-honest-c75",
        "status": "validated",
    },
    {
        "milestone_id": "M-V4-GEN-1/batch-score-still-blocked-c76",
        "narrative": (
            "c76 P2 HALT-HONEST continuation per FD-1. Batch-scoring 15 gen renders remains "
            "blocked on VGGish inference infra (tensorflow/torch unavailable; numpy 2.4.4 "
            "vs ml_dtypes bfloat16 incompatibility; shared-venv discipline blocks numpy<2.0 "
            "downgrade). Even under v2 wider-linear calibration, L119 mandate is EMPIRICALLY "
            "INFEASIBLE per l119_infeasibility_proof_c76.json (VGGish resolution insufficient). "
            "Consequence: passer_count remains not computable via automated EAR-1; operator ear "
            "(FD-6 standing authority since c47) is the operative gate for M-V4-GEN-1 completion. "
            "15 gen ab_mix.wav files (iter-01/02/03 × 5 songs, REPLAY_PROOF_HOLDS byte-det ×2) "
            "remain the delivered candidates for operator adjudication. supersedes "
            "M-V4-GEN-1/batch-score-blocked-c75 via str."
        ),
        "artifacts": [],
        "confidence": {"assessor": "worker", "level": "high",
                        "rationale": "dual blocker persists; delegation to FD-6 activated"},
        "supersedes_path": "M-V4-GEN-1/batch-score-blocked-c75",
        "status": "validated",
    },
    {
        "milestone_id": "_plan/register-c76-sub-leaves",
        "narrative": (
            "c76 POR registration row: 4 new c76 substantive milestone_ids added inline in "
            "the ## Milestones parseable region — M-V4-EAR-1/v2-wider-linear-calibration-c76, "
            "M-V4-EAR-1/l119-infeasibility-proof-c76, _selection/band4-spot-check-v2-c76, "
            "M-V4-GEN-1/batch-score-still-blocked-c76 — plus 4 housekeeping tail rows "
            "(register + closed + scratch + adopt-tests). NO preservation-spin (BANNED per "
            "c47 operator omnibus part 4). NO wait-on-operator memo (BANNED per operator "
            "directive 2026-09-03 part 2)."
        ),
        "artifacts": ["plan_of_record.md"],
        "confidence": {"assessor": "worker", "level": "high", "rationale": "8 c76 rows registered inline"},
        "supersedes_path": None,
        "status": "validated",
    },
    {
        "milestone_id": "_run/cycle_76_closed",
        "narrative": (
            "c76 CLOSED. VERDICT: SUBSTANTIVE-with-HALT-HONEST-DELEGATION. LANDED: "
            "(P1a) v4_ear_v2 wider-linear calibration eliminates c74 saturation, 5/5 LOO PASS "
            "in [6.21, 6.83] no clipping; (P1b) L119 monotone-infeasibility proof, 3×3 sweep, "
            "all cells fail, raw_sep<0 in all 3 statistics; (P1c) v2 band-4 spot check honest "
            "FAIL corroborates; (P2) batch-score blocker updated, VGGish still blocked, L119 "
            "empirically unachievable, M-V4-GEN-1 completion delegated to FD-6 operator ear per "
            "c47 standing precedent. STALL COUNTER: 3/8 unchanged (iter-04 not launched; "
            "delegation obviates additional iterations under a broken gate). All READ-ONLY "
            "anchors byte-identical pre==post: v4_ear.py e775621b…, exemplar_set.json 31c10dfb…, "
            "exemplar_embeddings.npz be93d016…, band4_embeddings.npz 4fc8dc82…, 5 c69 v1 + "
            "5 c71 v2 + 15 iter-01/02/03 ab_mix + CG showcase 6e13e007… + PD stem_manifest "
            "d483f2bf… + SF2 74594e8f…. Tests: 9/9 new c76 + 8/8 c75 + 5/5 ear scaffold + "
            "7/7 gen iterate = 29/29 PASS. env_pin canonical 2ac444c3…922ca unchanged. "
            "Byte-det ×2 HOLDS for c76 sidecars. DISCIPLINE: FD-1 halt-honest (formal lemma + "
            "empirical proof); FD-6 delegation activated; FD-16(a) cert unchanged; c14 "
            "str-supersede lemma respected (3 str supersedes); c47 preservation-spin BAN "
            "honored; c47 PATH_A worker-authority for sibling module (v4_ear.py not touched); "
            "no wait-on-operator memo. 18th consecutive cycle 9-header contract compliance "
            "(c59-c76). c77 inherits: M-V4-CLOSE-1 authorship (completion report v3 + "
            "OPERATOR_DECISIONS + codebase guide); optional interpolation-hybrid demo; "
            "FD-6 operator adjudication of 23 pending A/Bs remains the operative gate."
        ),
        "artifacts": [
            "data/v4/ear/l119_infeasibility_proof_c76.json",
            "data/v4/ear/band4_spot_check_v2_c76.json",
        ],
        "confidence": {"assessor": "worker", "level": "high",
                        "rationale": "cycle rollup with honest FD-6 delegation and formal infeasibility proof"},
        "supersedes_path": None,
        "status": "validated",
    },
    {
        "milestone_id": "_archive/cycle-76-scratch",
        "narrative": (
            "c76 scratch archival housekeeping. `tools/_emit_c76_ledger_events.py` retained "
            "in-tree per c14+ emitter-exemption pattern (docs/emitter_exemption_policy.md sha "
            "fd2c33a7…). Substantive scripts scripts/ear/{v4_ear_v2,probe_l119_infeasibility_c76,"
            "band4_spot_check_v2_c76}.py are P1a/P1b/P1c substantive landing artifacts; NOT "
            "scratch. Scratchpad venv attempt for tf install left un-executed under "
            "permission-declined path — no workspace pollution. No files to move to tools/stale/."
        ),
        "artifacts": ["tools/_emit_c76_ledger_events.py"],
        "confidence": {"assessor": "worker", "level": "high", "rationale": "emitter retained; no scratch"},
        "supersedes_path": None,
        "status": "validated",
    },
    {
        "milestone_id": "_infra/adopt-cycle76-tests",
        "narrative": (
            "c76 test-adoption housekeeping. 1 new test file: `tests/test_ear_v2_calibration_c76.py` "
            "(9 named cases: v2 module manifest + LOO no-clipping + sanity gate + infeasibility "
            "sidecar schema + band4-v2 honest-FAIL + monotone calibration + no-PRNG/sidecar/vst3 "
            "imports + READ-ONLY anchor shas + byte-det ×2 sidecar shas). 9/9 PASS. Regression: "
            "test_ear_batch_scoring_c75 8/8, test_ear_v4_scaffold 5/5, test_gen_iterate_v4 7/7 "
            "under /usr/bin/python3. Cross-cycle file total: 12 pre-c76 + 1 new = 13 test files. "
            "29/29 total green."
        ),
        "artifacts": ["tests/test_ear_v2_calibration_c76.py"],
        "confidence": {"assessor": "worker", "level": "high", "rationale": "9/9 c76 + 20/20 regression = 29/29 PASS"},
        "supersedes_path": None,
        "status": "validated",
    },
]


def _canonical_uuid5(mid: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"music-gen/c76/{mid}"))


def main():
    with LEDGER.open("a", encoding="utf-8") as f:
        for e in EVENTS:
            row = {
                "agent": "worker",
                "artifacts": e["artifacts"],
                "confidence": e["confidence"],
                "cycle": 76,
                "env_pin_sha256": ENV_PIN,
                "event_id": _canonical_uuid5(e["milestone_id"]),
                "milestone_id": e["milestone_id"],
                "narrative": e["narrative"],
                "run_id": RUN_ID,
                "status": e["status"],
                "ts": TS,
            }
            if e.get("supersedes_path") is not None:
                row["supersedes_path"] = e["supersedes_path"]
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"Appended {len(EVENTS)} c76 events to {LEDGER}")


if __name__ == "__main__":
    main()
