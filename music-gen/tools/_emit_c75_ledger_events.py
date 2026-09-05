#!/usr/bin/env /usr/bin/python3
"""c75 ledger emitter — appends c75 events with UUID5 content-hash event_ids."""
from __future__ import annotations
import hashlib
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "promise_ledger.jsonl"
RUN_ID = "run-2026-09-06T000500Z"
CYCLE = 75
TS = "2026-09-06T00:05:00Z"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def make_event(mid: str, narrative: str, status: str, level: str,
               rationale: str, artifacts=None, supersedes_path=None):
    body = {
        "milestone_id": mid, "narrative": narrative, "status": status,
        "confidence": {"level": level, "rationale": rationale, "assessor": "worker"},
        "cycle": CYCLE, "artifacts": artifacts or [], "run_id": RUN_ID,
        "env_pin_sha256": ENV_PIN, "agent": "worker", "ts": TS,
    }
    if supersedes_path is not None:
        body["supersedes_path"] = supersedes_path
    ev_id = str(uuid.uuid5(NS, _canonical({k: v for k, v in body.items() if k != "event_id"}).decode("utf-8")))
    body["event_id"] = ev_id
    return body


EVENTS = [
    # P1 halt-honest blocker
    make_event(
        "M-V4-GEN-1/batch-score-blocked-c75",
        (
            "c75 P1 HALT-HONEST per FD-1. Batch-score all 15 gen renders BLOCKED on two "
            "independent gates: (i) VGGish inference infra unavailable — `tensorflow_hub` "
            "loads but `tensorflow` triggers ml_dtypes/numpy>=2.0 incompatibility "
            "(`np.dtype(bfloat16)` -> `TypeError: expected 0 arguments, got 1`); CLAP still "
            "fails on torchvision::nms per c74 anchor; (ii) P4 band-4 spot check FAILS — "
            "band-4 songs score 6.0-7.0 above campaign-L119 mandate `band4_max < loo_min - 0.5`. "
            "Calibration cannot distinguish band-4 from band-7 exemplars under current "
            "linear-anchor scheme. Even if VGGish inference were available, passer-count "
            "trust for gen renders is BROKEN. Per brief P4 halt-honest branch: P2 iter-04 "
            "NOT launched; passer_count = null (not computed); 15 gen manifests NOT modified "
            "this cycle (calibration honesty preserved). Blocker sidecar at "
            "`data/v4/gen/batch_score_blocker_c75.json`. Substantive scaffold "
            "`scripts/ear/score_gen_batch.py` lands with `--unblocked` resume path for c76+ "
            "after calibration-anchor fix. c74 READ-ONLY anchors byte-identical pre==post "
            "(v4_ear.py, exemplar_set.json, exemplar_embeddings.npz, band4_embeddings.npz)."
        ),
        "in-progress", "high",
        "P1 halt-honest per FD-1 (band-4 gate FAIL + infra unavailable); block P2 iter-04",
        artifacts=[
            "scripts/ear/score_gen_batch.py",
            "data/v4/gen/batch_score_blocker_c75.json",
        ],
    ),
    # P3.a + P3.b diagnostic
    make_event(
        "_selection/ear-1-loo-selfinclude-audit-c75",
        (
            "c75 P3.a diagnostic AUDIT: `scripts/ear/v4_ear.py::leave_one_out` code inspected "
            "(line 166: `remaining = {k: v for k, v in exemplar_signatures.items() if k != held_out}`) "
            "— the held-out exemplar is correctly EXCLUDED from the reference bank. NO "
            "self-include bug; pattern is genuine saturation. v4_ear.py NOT touched. "
            "P3.b diagnostic probe `scripts/ear/probe_calibration_saturation_c75.py` computed "
            "raw stats under 3 variants (current linear-anchor / sigmoid dampening 0.9 ceiling / "
            "percentile calibration). Raw span = 0.086 absolute (9% relative) on [0.87, 0.96]; "
            "4/5 exemplars clip to 7.0 under current linear-anchor because loo-mean anchor sits "
            "BELOW most exemplars' raw stats — `characterization = wide_span_ceiling_from_anchor_choice`. "
            "Fix proposed for c76: scale anchor_high above the raw ceiling OR switch to sigmoid/percentile "
            "calibration. This event is DIAGNOSTIC only; does NOT alter v4_ear.py or exemplar_set.json."
        ),
        "validated", "high",
        "P3 diagnostic; LOO code correct; anchor-choice drives saturation, not fundamental",
        artifacts=[
            "scripts/ear/probe_calibration_saturation_c75.py",
            "data/v4/ear/calibration_saturation_probe_c75.json",
        ],
    ),
    # P4 halt-honest band-4 spot check
    make_event(
        "_selection/band4-spot-check-halt-honest-c75",
        (
            "c75 P4 HALT-HONEST per FD-1 + campaign L119 mandate. Band-4 spot check on 3 "
            "pre-computed band-4 songs (aguanile, stay_live, wagon_wheel) via c74 EAR-1 impl "
            "READ-ONLY. Scores: aguanile=6.00, stay_live=7.00 (clips), wagon_wheel=6.52. "
            "loo_min=6.44 (Desire). Mandate `band4_max < loo_min - 0.5` requires band4_max < 5.94; "
            "observed band4_max=7.00. Gate FAILS: calibration is NOT distinguishing band-4 from "
            "band-7 exemplars. Corroborates c74 auditor P2 saturation finding. Blocks P1 passer "
            "trust and P2 iter-04 launch. Hand calibration-anchor fix to c76. v4_ear.py + "
            "exemplar_embeddings.npz + band4_embeddings.npz all READ-ONLY (byte-identical "
            "pre==post; asserted via sha256sum). `supersedes_path=null` (new escalation class)."
        ),
        "invalidated", "high",
        "P4 gate FAIL is a first-class negative finding; blocks P1 trust; hand to c76",
        artifacts=[
            "scripts/ear/band4_spot_check_c75.py",
            "data/v4/ear/band4_spot_check_c75.json",
        ],
        supersedes_path=None,
    ),
    # P5 exemplar band metadata realignment
    make_event(
        "_selection/ear-1-exemplar-band-metadata-realignment-c75",
        (
            "c75 P5 per c74 auditor P3 recommendation. Records c74 unilateral realignment of "
            "Essence (6→7) + Desire (6→7) exemplar bands based on filesystem placement in "
            "`corpus/ratings/7/`. Molasses was already band 7. Exemplar-set mix now reads "
            "accurately as `2x band 6 (CG, PD) + 3x band 7 (Molasses, Essence, Desire)`. "
            "Authority: invariant (d) filesystem-authoritative (on-disk placement > brief "
            "metadata). Operator ear post-hoc verification per FD-6 remains authoritative. "
            "Sidecar at `data/v4/ear/_selection/exemplar-band-metadata-realignment-c75.json`."
        ),
        "validated", "high",
        "P5 records c74 realignment with filesystem-evidence rationale; str supersede per c14 lemma",
        artifacts=[
            "data/v4/ear/_selection/exemplar-band-metadata-realignment-c75.json",
        ],
        supersedes_path="M-V4-EAR-1/exemplar-sha16-resolved",
    ),
    # P7 housekeeping — register
    make_event(
        "_plan/register-c75-sub-leaves",
        (
            "c75 POR registration row: 5 new c75 milestone_ids added inline in the ## Milestones "
            "section: M-V4-GEN-1/batch-score-blocked-c75, _selection/ear-1-loo-selfinclude-audit-c75, "
            "_selection/band4-spot-check-halt-honest-c75, _selection/ear-1-exemplar-band-metadata-realignment-c75, "
            "plus housekeeping tail (register + closed + scratch + adopt-tests = 4). Interpolation-"
            "hybrid demo (P6) DEFERRED to c76+ per brief optional allowance (P4 gate FAIL absorbed "
            "wall budget; c76 must land calibration fix before any downstream scoring). NO preservation-"
            "spin (BANNED per c47 operator omnibus part 4)."
        ),
        "validated", "high",
        "P7 register: 5 substantive c75 rows + 4 housekeeping tail; NO preservation-spin",
    ),
    # P7 closed
    make_event(
        "_run/cycle_75_closed",
        (
            "c75 CLOSED. VERDICT: HALT-HONEST (P1 blocked on calibration + infra). LANDED: (P3) "
            "LOO self-include audit PASS (code correct at v4_ear.py:166; saturation is anchor-choice "
            "driven not fundamental) + calibration-saturation probe with 3 variants + raw stats. "
            "(P4) Band-4 spot check FAIL — band4_max=7.00 > 5.94 mandate threshold; corroborates "
            "c74 P2 saturation finding. (P5) Exemplar band metadata realignment recorded with str "
            "supersede per c14 lemma. (P7) Housekeeping 4 rows + 1/1 new test file 8/8 PASS. "
            "BLOCKED: (P1) Batch-score 15 gen renders — dual-blocker (band-4 gate FAIL + VGGish "
            "infra unavailable via ml_dtypes/numpy 2.x cascade). (P2) iter-04 launch — conditional "
            "on P1 passer count; not launched. (P6) Interpolation-hybrid demo — DEFERRED to c76+. "
            "PASSER COUNT: null (not computable this cycle). STALL COUNTER: 3/8 unchanged (iter-03 "
            "was c74; iter-04 blocked). All READ-ONLY anchors byte-identical pre==post: "
            "`scripts/ear/v4_ear.py`, `data/v4/ear/exemplar_set.json` (post-c74 sha), "
            "`data/v4/ear/exemplar_embeddings.npz`, `data/v4/ear/band4_embeddings.npz`, "
            "5 c69 v1 anchors, 5 c71 v2 anchors, 15 iter-01+02+03 ab_mix.wav anchors, CG showcase, "
            "PD stem_manifest, SF2. env_pin_sha256 canonical 7-key subset `2ac444c3...922ca` "
            "unchanged. Tests: 8/8 new + 7/7 gen + 5/5 ear = 20/20 PASS. DISCIPLINE: FD-1 halt-honest; "
            "FD-6 operator ear = LANDS authority post-hoc; FD-16(a) env_pin cert unchanged; c14 "
            "str-supersede lemma respected (P5 str supersede); c47 preservation-spin BAN honored; "
            "no wait-on-operator memo (BANNED per operator directive 2026-09-03 part 2). c76 "
            "inherits: (i) calibration-anchor fix (sigmoid/percentile or wider linear) to unblock "
            "batch-scoring; (ii) if fix lands, resume via `python3 scripts/ear/score_gen_batch.py "
            "--unblocked`; (iii) VGGish infra unblock (numpy<2.0 OR ml_dtypes upgrade) still "
            "required for new inference on gen ab_mix files; (iv) c74 forward-guidance items 1-5 "
            "remain open. 17th consecutive cycle compliance with 9-header closing-summary contract "
            "(c59-c75)."
        ),
        "validated", "high",
        "cycle rollup with honest HALT verdict + halt-honest blockers enumerated + resume plan for c76",
    ),
    # P7 scratch
    make_event(
        "_archive/cycle-75-scratch",
        (
            "c75 scratch archival housekeeping. `tools/_emit_c75_ledger_events.py` retained in-tree "
            "per c14+ emitter-exemption pattern (`docs/emitter_exemption_policy.md` sha fd2c33a7...). "
            "New substantive scripts `scripts/ear/probe_calibration_saturation_c75.py` + "
            "`scripts/ear/band4_spot_check_c75.py` + `scripts/ear/score_gen_batch.py` are P3/P4/P1 "
            "substantive landing artifacts; NOT scratch. No workspace scratch to move to tools/stale/."
        ),
        "validated", "high",
        "one-shot emitter retained per c14+ pattern; no scratch archived",
        artifacts=["tools/_emit_c75_ledger_events.py"],
    ),
    # P7 adopt tests
    make_event(
        "_infra/adopt-cycle75-tests",
        (
            "c75 test-adoption housekeeping. 1 new test file: `tests/test_ear_batch_scoring_c75.py` "
            "with 8 named cases (batch_scorer surface, no-PRNG/sidecar_nonfactor guard, band4 schema, "
            "calibration probe schema, selection sidecar str-supersede per c14 lemma, blocker sidecar "
            "honest verdict, LOO no-self-include grep, env_pin canonical across 4 sidecars). 8/8 PASS "
            "via `PYTHONPATH=. /usr/bin/python3 tests/test_ear_batch_scoring_c75.py`. Regression: "
            "`tests/test_gen_iterate_v4.py` 7/7 unchanged; `tests/test_ear_v4_scaffold.py` 5/5 unchanged. "
            "Cross-cycle file total: 11 pre-c75 + 1 new = 12 test files."
        ),
        "validated", "high",
        "1 new test file, 8/8 PASS; regressions 12/12 clean",
        artifacts=["tests/test_ear_batch_scoring_c75.py"],
    ),
]


def main():
    with LEDGER.open("a", encoding="utf-8") as f:
        for ev in EVENTS:
            f.write(json.dumps(ev, sort_keys=True) + "\n")
    print(f"appended {len(EVENTS)} events")


if __name__ == "__main__":
    main()
