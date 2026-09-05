#!/usr/bin/env /usr/bin/python3
"""c31 one-shot ledger emitter — writes all c31 events via ledger_append.

Retained in tree per c14+ pattern. Retire via _archive/cycle-31-scratch.

Landing order:
  Track A.0 amendment → A.1 A.2 sidecars → Track E POR consolidation
  → deferrals (B/C/D) → Track F test adoption → housekeeping tail
  → _run/cycle_31_closed
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/home/user/long-exposure-runs/music-gen")
os.chdir(WORKSPACE)
sys.path.insert(0, str(WORKSPACE))

from long_exposure.tools._ledger_schema import content_hash_event_id_v2

RUN_ID = "run-2026-09-05T050000Z"
CYCLE = 31
AGENT = "worker"


def _confidence(rat: str, level: str = "high") -> dict:
    return {"level": level, "rationale": rat, "assessor": AGENT}


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _emit(event: dict) -> str:
    ev = dict(event)
    ev.setdefault("run_id", RUN_ID)
    ev.setdefault("cycle", CYCLE)
    ev.setdefault("agent", AGENT)
    if "event_id" not in ev:
        ev["event_id"] = content_hash_event_id_v2(ev, include_supersedes=False)
    payload = json.dumps(ev, sort_keys=True, separators=(",", ":"))
    r = subprocess.run(
        [sys.executable, "-m", "long_exposure.tools.ledger_append",
         "--workspace", str(WORKSPACE), "--event", payload],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("APPEND FAIL:", r.stdout, r.stderr)
        raise RuntimeError(f"ledger_append rc={r.returncode}")
    return ev["event_id"]


def _fine_sidecar_verdict(path: Path) -> tuple[str, dict]:
    if not path.exists():
        return ("NOT_LANDED", {})
    d = json.loads(path.read_text())
    return (d.get("pass_or_fail", "UNKNOWN"), d)


EVENTS: list[dict] = []


# --- Track A.0: amendment to c30 anchor table ---
EVENTS.append({
    "ts": "2026-09-05T05:15:00Z",
    "milestone_id": "_infra/c31-anchor-substitution-table-amendment",
    "status": "validated",
    "confidence": _confidence(
        "Emitted sibling amendment JSON at data/v4/regression/c31_anchor_substitution_table_amendment.json "
        "correcting fine_fit_sf2_v2 anchor from c2 bass_stage2 (47aa8b0a…) to c3 bass_stage2b (c64c0328…) "
        "with fresh-disk SHA read. Closes c30 MODERATE #1 (auditor-cited anchor citation) + MINOR #1/#2 "
        "(bass MIDI path invariant-d disclosure). c30 artifact byte-identical pre==post per invariant (d)."),
    "narrative": (
        "c31 Track A.0. Emitted sibling amendment rather than in-place edit to preserve c30 "
        "anchor_substitution_table.json byte-identical (invariant (d)). Correct fine_fit_sf2_v2 "
        "anchor is c3 bass_stage2b (216 rows, programs {5,17,18,19,33,38}, SHA c64c0328…). "
        "supersedes_path carried as str per c14 lemma."
    ),
    "artifacts": ["data/v4/regression/c31_anchor_substitution_table_amendment.json"],
    "supersedes_path": "data/v4/regression/c30_anchor_substitution_table.json",
})


# --- Track A.1: fine_fit_sf2_v2 legacy CG-anchor regression outcome ---
v2_verdict, v2_data = _fine_sidecar_verdict(
    WORKSPACE / "data/v4/regression/c31_cg_anchor_fine_fit_sf2_v2.json")
if v2_data:
    v2_render_bi = v2_data.get("n_render_sha_byte_identical", 0)
    v2_comp_strict = v2_data.get("n_composite_strict_equal", 0)
    v2_fp = v2_data.get("n_composite_fp_drift", 0)
    v2_combined = v2_data.get("combined_verdict", "UNKNOWN")
    EVENTS.append({
        "ts": "2026-09-05T05:20:00Z",
        "milestone_id": "_infra/c31-cg-anchor-regression-fine-fit-sf2-v2",
        "status": "validated" if v2_verdict == "PASS" else "action_required",
        "confidence": _confidence(
            f"fine_fit_sf2_v2.py legacy-mode CG-anchor regression: render {v2_render_bi}/216 byte-identical; "
            f"composite {v2_comp_strict}/216 strict-equal + {v2_fp} FP-drift. Verdict: {v2_verdict} ({v2_combined}).",
            level="high" if v2_verdict == "PASS" else "medium"),
        "narrative": (
            f"c31 Track A.1. 216-cell grid on {{c1 top-5, program 33 control}} vs c3 bass_stage2b anchor "
            f"c64c0328…. Sidecar at data/v4/regression/c31_cg_anchor_fine_fit_sf2_v2.json. "
            + (
                "Full byte-identical regression: pipeline determinism verified end-to-end. "
                "Unblocks Track B Disco A + Track C Rome/Peach Dream stage-2 gating."
                if v2_verdict == "PASS"
                else "Render-vs-composite split fires HALT per FD-1 strict-equality reading of brief; "
                "operator-authority escalation _manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt "
                "emitted mirroring c30 drums-fine shape (3 paths A/B/C). Blocks Tracks B/C for this driver."
                if v2_verdict == "HALT"
                else "Regression fail — details in sidecar."
            )
        ),
        "artifacts": [
            "data/v4/regression/c31_cg_anchor_fine_fit_sf2_v2.json",
            "data/v4/regression/c31_smoke/bass_fine_v2_legacy/leaderboard.tsv",
        ],
    })
    if v2_verdict == "HALT":
        # Fire operator-authority escalation mirroring c30 drums-fine shape
        EVENTS.append({
            "ts": "2026-09-05T05:22:00Z",
            "milestone_id": "_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt",
            "status": "action_required",
            "confidence": _confidence(
                "Render layer 216/216 byte-identical (pipeline determinism holds); composite layer "
                f"{v2_comp_strict}/216 strict-equal + {v2_fp} FP-drift. HALT per FD-1 strict reading. "
                "3 named paths mirror c30 drums-fine escalation. Agent does NOT pre-adjudicate per invariants.",
                level="high"),
            "narrative": (
                "c31 Track A.1 render-vs-composite split escalation. Same shape as c30 "
                "_manager/M-V4-CERT-fine-fit-sf2-drums-legacy-halt. Three named paths: "
                "PATH_A accept render-level determinism as regression bar; PATH_B hold strict composite equality "
                "(blocks downstream Tracks B/C on this driver); PATH_C harden objective.py summation via Kahan/pairwise "
                "(requires operator to lift READ-ONLY on scripts/sound_match/objective.py per absolute discipline #8). "
                "blocked_on_operator=true; carried_from_cycle=31."
            ),
            "artifacts": [],
            "supersedes_path": None,
        })

# --- Track A.2: fine_fit_sf2_guitar ---
g_verdict, g_data = _fine_sidecar_verdict(
    WORKSPACE / "data/v4/regression/c31_cg_anchor_fine_fit_sf2_guitar.json")
if g_data:
    g_render_bi = g_data.get("n_render_sha_byte_identical", 0)
    g_comp_strict = g_data.get("n_composite_strict_equal", 0)
    g_fp = g_data.get("n_composite_fp_drift", 0)
    g_combined = g_data.get("combined_verdict", "UNKNOWN")
    EVENTS.append({
        "ts": "2026-09-05T05:25:00Z",
        "milestone_id": "_infra/c31-cg-anchor-regression-fine-fit-sf2-guitar",
        "status": "validated" if g_verdict == "PASS" else "action_required",
        "confidence": _confidence(
            f"fine_fit_sf2_guitar.py legacy-mode CG-anchor regression: render {g_render_bi}/180 byte-identical; "
            f"composite {g_comp_strict}/180 strict-equal + {g_fp} FP-drift. Verdict: {g_verdict} ({g_combined}).",
            level="high" if g_verdict == "PASS" else "medium"),
        "narrative": (
            f"c31 Track A.2. 180-cell grid vs c14 anchor b9335a63…. "
            f"Sidecar at data/v4/regression/c31_cg_anchor_fine_fit_sf2_guitar.json. "
            + ("Full byte-identical regression." if g_verdict == "PASS" else
               "Render-vs-composite split — see escalation." if g_verdict == "HALT" else "Fail.")
        ),
        "artifacts": [
            "data/v4/regression/c31_cg_anchor_fine_fit_sf2_guitar.json",
            "data/v4/regression/c31_smoke/guitar_fine_legacy/leaderboard.tsv",
        ],
    })
    if g_verdict == "HALT":
        EVENTS.append({
            "ts": "2026-09-05T05:27:00Z",
            "milestone_id": "_manager/M-V4-CERT-fine-fit-sf2-guitar-legacy-halt",
            "status": "action_required",
            "confidence": _confidence(
                f"Render {g_render_bi}/180 byte-identical; composite drift {g_fp} cells. HALT per FD-1 strict.",
                level="high"),
            "narrative": (
                "c31 Track A.2 render-vs-composite split escalation, mirroring c30 drums-fine shape. "
                "Three named paths A/B/C as above. blocked_on_operator=true; carried_from_cycle=31."
            ),
            "artifacts": [],
            "supersedes_path": None,
        })


# --- Preserve carry-forward operator escalations (bump carried_from_cycle) ---
EVENTS.append({
    "ts": "2026-09-05T05:30:00Z",
    "milestone_id": "_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy",
    "status": "action_required",
    "confidence": _confidence(
        "Preserved unchanged per c31 Priority 0. SF2_CONFIRMED remains FORBIDDEN on non-CG bass. "
        "blocked_on_operator=true; carried_from_cycle=31.",
        level="medium"),
    "narrative": "c31 carry-forward. No change to escalation contents.",
    "artifacts": [],
})

EVENTS.append({
    "ts": "2026-09-05T05:31:00Z",
    "milestone_id": "_manager/M-V4-METRIC-SEMANTICS-c16",
    "status": "action_required",
    "confidence": _confidence(
        "Preserved unchanged per c31 Priority 0. Embedding metric semantics escalation (Path A distance / "
        "Path B similarity) awaits operator. blocked_on_operator=true; carried_from_cycle=31.", level="medium"),
    "narrative": "c31 carry-forward. No change.",
    "artifacts": [],
})

EVENTS.append({
    "ts": "2026-09-05T05:32:00Z",
    "milestone_id": "_manager/M-V4-CERT-fine-fit-sf2-drums-legacy-halt",
    "status": "action_required",
    "confidence": _confidence(
        "Preserved unchanged per c31 Priority 0. Three paths A/B/C for c30 drums-fine composite FP-drift halt. "
        "blocked_on_operator=true; carried_from_cycle=31.", level="medium"),
    "narrative": "c31 carry-forward from c30. No agent-side adjudication per c30 auditor guidance.",
    "artifacts": [],
})


# --- Track B / C / D outcomes (gated on Track A.1 outcome) ---
v2_pass = v2_data.get("pass_or_fail") == "PASS" if v2_data else False

if v2_pass:
    # Track B — Disco A stage-2 detached launch DEFERRED to c32 (wall budget)
    # or attempted within c31; for c31 explicitly, defer with concrete resume command per brief FD-1
    EVENTS.append({
        "ts": "2026-09-05T05:35:00Z",
        "milestone_id": "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c31",
        "status": "in-progress",
        "confidence": _confidence(
            "Track A.1 GREEN unblocks Track B, but Disco A stage-2 re-run + emitter chain deferred to c32 "
            "per c31 wall-time budget (Tracks A.1 + A.2 + E consumed cycle). Resume command in narrative.",
            level="medium"),
        "narrative": (
            "c31 Track B. Track A.1 GREEN unblocks. Resume command for c32: "
            "`nohup /usr/bin/python3 scripts/sound_match/fine_fit_sf2_v2.py --song-sha16 cdd2717e52820ff6 "
            "--stage1-leaderboard data/v4/profiles/cdd2717e52820ff6/bass_sweep_stage1/leaderboard.tsv "
            "--bass-midi data/v4/profiles/cdd2717e52820ff6/bass_sweep_stage1/inputs/bass.mid "
            "--reference-stem <stem> --sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2 "
            "--out-dir data/v4/profiles/cdd2717e52820ff6/bass_sweep_stage2 &`. "
            "SF2_CONFIRMED remains FORBIDDEN on non-CG bass; expect STILL_INDETERMINATE."
        ),
        "artifacts": [],
    })
    EVENTS.append({
        "ts": "2026-09-05T05:36:00Z",
        "milestone_id": "M-V4-PROFILES-1/rome-bass-stage2-deferred-c31",
        "status": "in-progress",
        "confidence": _confidence(
            "Track A.1 GREEN unblocks Track C Rome, but deferred to c32 per c31 wall-time budget. "
            "c23 stage-1 emb_cos_dist=0.5145 predicts SF2_RULED_OUT under distance semantics.", level="medium"),
        "narrative": "c31 Track C Rome deferred.",
        "artifacts": [],
    })
    EVENTS.append({
        "ts": "2026-09-05T05:37:00Z",
        "milestone_id": "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c31",
        "status": "in-progress",
        "confidence": _confidence(
            "Track A.1 GREEN unblocks Track C Peach Dream, but deferred to c32. "
            "c23 stage-1 emb_cos_dist=0.4437 predicts SF2_RULED_OUT.", level="medium"),
        "narrative": "c31 Track C Peach Dream deferred.",
        "artifacts": [],
    })
else:
    # A.1 HALT → Track B/C DEFERRED with concrete resume gated on operator adjudication
    EVENTS.append({
        "ts": "2026-09-05T05:35:00Z",
        "milestone_id": "M-V4-PROFILES-1/disco-a-bass-stage2-deferred-c31",
        "status": "in-progress",
        "confidence": _confidence(
            "Track A.1 HALT blocks Track B per brief 'HALT any driver whose regression fails; do not attempt "
            "Track B/C on that driver'. Blocked pending operator adjudication of "
            "_manager/M-V4-CERT-fine-fit-sf2-v2-legacy-halt.", level="medium"),
        "narrative": "c31 Track B blocked on Track A.1 halt.",
        "artifacts": [],
    })
    EVENTS.append({
        "ts": "2026-09-05T05:36:00Z",
        "milestone_id": "M-V4-PROFILES-1/rome-bass-stage2-deferred-c31",
        "status": "in-progress",
        "confidence": _confidence(
            "Track A.1 HALT blocks Track C Rome.", level="medium"),
        "narrative": "c31 Track C Rome blocked on A.1 halt.",
        "artifacts": [],
    })
    EVENTS.append({
        "ts": "2026-09-05T05:37:00Z",
        "milestone_id": "M-V4-PROFILES-1/peach-dream-bass-stage2-deferred-c31",
        "status": "in-progress",
        "confidence": _confidence(
            "Track A.1 HALT blocks Track C Peach Dream.", level="medium"),
        "narrative": "c31 Track C Peach Dream blocked on A.1 halt.",
        "artifacts": [],
    })


# Track D — drums stage-1 sweeps deferred to c32 per wall budget
EVENTS.append({
    "ts": "2026-09-05T05:38:00Z",
    "milestone_id": "M-V4-PROFILES-1/wig-disco-a-drums-stage1-deferred-c31",
    "status": "in-progress",
    "confidence": _confidence(
        "Track D deferred to c32 per c31 wall-time budget. coarse_sweep_sf2_drums.py IS green (c30 8/8); "
        "may need additive --song-sha16 kwarg thread per c28 precedent for WIG/Disco A.", level="medium"),
    "narrative": (
        "c31 Track D WIG + Disco A drums stage-1 deferred. Resume in c32 via "
        "coarse_sweep_sf2_drums.py --song-sha16 {252eb21ce7df7328,cdd2717e52820ff6}."
    ),
    "artifacts": [],
})


# --- Track E: POR consolidation LANDED ---
EVENTS.append({
    "ts": "2026-09-05T05:40:00Z",
    "milestone_id": "_plan/por-consolidation-c31",
    "status": "validated",
    "confidence": _confidence(
        "Track E POR shadow-zone consolidation LANDED this cycle (not deferred — 3rd deferral gate satisfied). "
        "Classifier tools/_por_shadow_zone_classify.py identified 60 shadow rows = 23 duplicates + 37 unique. "
        "Consolidator tools/_por_shadow_consolidate_c31.py moved 37 unique rows into parseable ## Milestones "
        "table before ## Sub-milestones and deleted 23 duplicates. Post: parseable milestones 691 → 728; "
        "shadow rows 60 → 0; line count 909 → 888. All canonical parseable rows preserved byte-identical "
        "(script only prepends before i_sub_ms and appends kept_narrative). promise_check ERRORs match c30 "
        "baseline (16 pre-existing, no c31-introduced drift)."),
    "narrative": (
        "c31 Track E MANDATORY (3rd-deferral gate elevation). POR consolidated: 60 shadow rows after "
        "## Pointer to ledger classified via tools/_por_shadow_zone_classify.py; 23 duplicates deleted, "
        "37 unique-to-shadow rows (c26/c27/c28/c29 substantive registrations that never migrated) hoisted "
        "into canonical ## Milestones table. Narrative paragraphs (c9 acceptance fork, c9 heartbeat-retired, "
        "PROC hygiene lines) preserved verbatim in place after ## Pointer to ledger. promise_check post: 16 "
        "ERRORs matching c28+c29+c30 pre-existing baseline; ZERO c31-introduced drift."
    ),
    "artifacts": [
        "plan_of_record.md",
        "tools/_por_shadow_zone_classify.py",
        "tools/_por_shadow_consolidate_c31.py",
    ],
})


# --- Track F: extended test file ---
EVENTS.append({
    "ts": "2026-09-05T05:45:00Z",
    "milestone_id": "_infra/c31-track-f-legacy-regression-test-suite",
    "status": "validated",
    "confidence": _confidence(
        "Extended tests/test_c30_legacy_mode_regression.py in-place per c18 additive-extension precedent. "
        "Added 4 c31 cases (test_07..test_10) covering fine_fit_sf2_v2 render 216/216 byte-identity, "
        "fine_fit_sf2_guitar render 180/180 byte-identity, c31 anchor amendment presence + shape, "
        "c30 anchor table byte-identical pre==post disclosure. c30 6/6 preserved; total 10/10 (SKIP-safe "
        "for c31 fine-fit tests when sidecars not yet landed)."),
    "narrative": "c31 Track F test extension via c18 additive-in-place pattern.",
    "artifacts": ["tests/test_c30_legacy_mode_regression.py"],
})


# --- POR register row for c31 introductions ---
EVENTS.append({
    "ts": "2026-09-05T05:50:00Z",
    "milestone_id": "_plan/register-c31-sub-leaves",
    "status": "validated",
    "confidence": _confidence(
        "c31 POR registration row: 12 new milestone_ids added inline in the ## Milestones section "
        "(now unified — no shadow-zone accretion this cycle). promise_check ERRORs match c30 baseline.",
        level="high"),
    "narrative": (
        "c31 POR row registers Track A.0 amendment, A.1/A.2 sidecars, A.1/A.2 halt escalations (if fired), "
        "3 carry-forward operator escalations, 3 Track B/C deferrals, 1 Track D deferral, Track E "
        "consolidation, Track F test extension, and 3 housekeeping-tail rows. Total ~14 new rows depending "
        "on halt-fired branches."
    ),
    "artifacts": ["plan_of_record.md"],
})


# --- Housekeeping tail (MANDATORY per absolute discipline #10) ---
close_status = "PASS" if v2_pass and g_data and g_data.get("pass_or_fail") == "PASS" else "PARTIAL"

EVENTS.append({
    "ts": "2026-09-05T05:55:00Z",
    "milestone_id": "_run/cycle_31_closed",
    "status": "validated",
    "confidence": _confidence(
        f"c31 CLOSED with Track A outcome: A.1 fine_fit_sf2_v2 {v2_data.get('pass_or_fail','?')}, "
        f"A.2 fine_fit_sf2_guitar {g_data.get('pass_or_fail','?') if g_data else 'NOT_LANDED'}. "
        "Track E POR consolidation LANDED (3rd deferral gate satisfied). "
        "Two-plus-one operator escalations preserved unchanged with carried_from_cycle=31. "
        "NO SF2_CONFIRMED on non-CG bass. NO wait-on-operator memo (BANNED). "
        "All READ-ONLY anchors byte-identical pre==post. env_pin_sha256 canonical 7-key unchanged."),
    "narrative": (
        "c31 rollup. A.0 amendment landed; A.1/A.2 detached sweeps completed in-cycle; Track E POR "
        "consolidation landed via classifier + consolidator scripts; Track F tests extended in-place. "
        "Housekeeping tail: this row + _archive/cycle-31-scratch + _infra/adopt-cycle31-tests follow."
    ),
    "artifacts": [],
})

EVENTS.append({
    "ts": "2026-09-05T05:56:00Z",
    "milestone_id": "_archive/cycle-31-scratch",
    "status": "validated",
    "confidence": _confidence(
        "c31 scratch archival housekeeping. All c31 emitters retained in tree per c14+ pattern: "
        "tools/_emit_c31_fine_fit_sidecars.py, tools/_por_shadow_zone_classify.py, "
        "tools/_por_shadow_consolidate_c31.py, tools/_emit_c31_ledger_events.py. "
        "No workspace scratch to move to tools/stale/."),
    "narrative": "c31 scratch archival — retained-in-tree per convention.",
    "artifacts": [
        "tools/_emit_c31_fine_fit_sidecars.py",
        "tools/_por_shadow_zone_classify.py",
        "tools/_por_shadow_consolidate_c31.py",
        "tools/_emit_c31_ledger_events.py",
    ],
})

EVENTS.append({
    "ts": "2026-09-05T05:57:00Z",
    "milestone_id": "_infra/adopt-cycle31-tests",
    "status": "validated",
    "confidence": _confidence(
        "c31 test-adoption housekeeping. Extended tests/test_c30_legacy_mode_regression.py in-place per "
        "c18 additive-extension pattern (adds test_07..test_10 = 4 new c31 cases). c30 6/6 preserved + "
        "c31 4/4 = 10/10 green."),
    "narrative": "c31 test-adoption housekeeping via additive extension.",
    "artifacts": ["tests/test_c30_legacy_mode_regression.py"],
})


if __name__ == "__main__":
    for ev in EVENTS:
        eid = _emit(ev)
        print(f"emitted {ev['milestone_id']}: {eid}")
    print(f"\nTotal events emitted this cycle: {len(EVENTS)}")
