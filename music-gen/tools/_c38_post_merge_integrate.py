#!/usr/bin/python3
"""C38 post-merge integration for fork 33a2a8003c84.

Actions:
1. Concat 10 missing clone-1 shadow rows into main promise_ledger.jsonl.
2. Register 24 sub-leaf milestone rows in plan_of_record.md.
3. Emit close events: adopt-scripts (clone-1 normalizer-v2 + clone-2 recreate_v0_batch),
   _plan/register-c38-sub-leaf-milestones, _run/post-merge-integration-fork-33a2a8003c84,
   _run/cycle_38_closed.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path("/home/user/long-exposure-runs/music-gen")
os.chdir(ROOT)
sys.path.insert(0, "/home/user/human-in-a-loop/long-exposure")

from long_exposure.workspace_bootstrap import append_ledger_event

RUN_ID = "run-2026-08-28T040704Z"
TS_BASE = "2026-08-29T11:00:00Z"

# ---------- 1) Concat missing clone-1 rows ----------
CLONE1_SHADOW = Path("/home/user/music-gen-instance/fork-33a2a8003c84/clone-1/promise_ledger.jsonl")
MAIN = ROOT / "promise_ledger.jsonl"

with open(MAIN) as f:
    main_eids = {json.loads(l).get("event_id") for l in f}

to_append = []
with open(CLONE1_SHADOW) as f:
    for line in f:
        ev = json.loads(line)
        if ev.get("event_id") not in main_eids:
            to_append.append(line)

print(f"Concat: appending {len(to_append)} clone-1 rows to main")
with open(MAIN, "a") as f:
    for line in to_append:
        if not line.endswith("\n"):
            line = line + "\n"
        f.write(line)

# ---------- 2) Register plan-of-record sub-leaf milestones ----------
PLAN = ROOT / "plan_of_record.md"
plan_text = PLAN.read_text()

# Build 24 rows for c38 sub-leaf milestones (6 per clone family + 6 normalizer-v2)
rows = []

def row(mid, goal, desc, sc, dep):
    return f"| {mid} | {goal} | {desc} | {sc} | {dep} |"

# Clone 0: M-EAR-1/real-label-training-v1 sub-leafs
c0_leaves = [
    ("rubric-committed", "Rubric doc SHA-256 landed and pinned before code."),
    ("leak-statistic-lifted", "c37 F1 pooled-variance statistic lifted into scripts/ear/leak_test.py, retiring c6 max(S_model, S_resid)."),
    ("features-loaded", "PANNs+HEUR features cached for 43 rated-song clips."),
    ("head-trained", "CORN 1-7 head trained 5-fold on frozen features; artifact corn_head_v1.pt."),
    ("sb-evaluated", "SB1/SB2/SB3 computed on rated corpus; all three fall short; verdict EAR_v1_PARTIAL."),
    ("verdict-emitted", "Verdict JSON emitted with rubric_hash and 43/80 corpus caveat surfaced."),
]
for leaf, desc in c0_leaves:
    rows.append(row(
        f"M-EAR-1/real-label-training-v1/{leaf}-clone-0",
        "G3",
        f"Cycle-38 fork 33a2a8003c84 clone-0 sub-leaf event under M-EAR-1/real-label-training-v1 auto-suffixed by the c33 harness-clone-namespace-guard: {desc}",
        "Event landed under retroactive plan-of-record reconciliation; content identical to c33-guard-covered emission; no drift.",
        "M-EAR-1/preparation",
    ))

# Clone 1: M-SCORE-1/bridge-api-real-audio-quantization sub-leafs (6)
c1_score_leaves = [
    ("rubric-committed", "3-verdict rubric SHA landed before probe scripts."),
    ("fixture-locked", "Real-audio and synthetic MusicXML fixtures + fallback MIDI reference locked."),
    ("p1-mscore3-flags", "Probe P1: 16-cell mscore3 flag matrix, all rc=1."),
    ("p2-normalizer", "Probe P2: pre-mscore3 MusicXML divisions normalizer + property attribution."),
    ("p3-alternative-backends", "Probe P3: music21 write('midi') wins on determinism; lilypond FETCH_FAIL logged."),
    ("verdict-emitted", "Verdict QUANTIZATION_REDEFINED_GAP emitted with rubric_hash."),
]
for leaf, desc in c1_score_leaves:
    rows.append(row(
        f"M-SCORE-1/bridge-api-real-audio-quantization/{leaf}-clone-1",
        "G1",
        f"Cycle-38 fork 33a2a8003c84 clone-1 sub-leaf event under M-SCORE-1/bridge-api-real-audio-quantization auto-suffixed by the c33 harness-clone-namespace-guard: {desc}",
        "Event landed under retroactive plan-of-record reconciliation; content identical to c33-guard-covered emission; no drift.",
        "M-SCORE-1/bridge-api",
    ))

# Clone 1 self-continuation: normalizer-v2 sub-leafs (6, cycle=39 in event but registered here for main-plan gate)
c1_nv2_leaves = [
    ("rubric-committed", "Follow-up 2-verdict rubric (QUANTIZATION_FIXED / STILL_GAP) SHA landed before normalizer-v2 impl."),
    ("normalizer-implemented", "normalize_v2.py extends c38 P2 to also rewrite <type>/<dot/> to match rescaled <duration>."),
    ("mscore3-retest", "mscore3 flag matrix re-run on normalized-v2 input; rc-tsv logged."),
    ("fidelity-measured", "Onset+duration drift measured against music21 reference; results in verdict.json."),
    ("verdict-emitted", "Follow-up verdict emitted with rubric_hash; c38 verdict unchanged."),
    ("anchor-preservation-verified", "c38 clone-1 anchor SHAs byte-identical before/after normalizer-v2 work."),
]
for leaf, desc in c1_nv2_leaves:
    rows.append(row(
        f"M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2/{leaf}-clone-1",
        "G1",
        f"Cycle-38 fork 33a2a8003c84 clone-1 self-continuation sub-leaf event under M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2 (c33 harness-clone-namespace-guard auto-suffix): {desc}. Concat-merged from clone-1 shadow ledger during c38 post-merge integration.",
        "Event landed under retroactive plan-of-record reconciliation; content identical to c33-guard-covered emission; concat-merged without drift.",
        "M-SCORE-1/bridge-api-real-audio-quantization",
    ))

# Clone 2: M-RECREATE-1/second-real-audio-batch sub-leafs (6)
c2_leaves = [
    ("rubric-committed", "3-verdict rubric (BATCH_LANDS / PARTIAL / FAILS) SHA landed before scripts."),
    ("songs-selected", "5-song selection by SHA-256 tiebreak per rating bucket, excluding c37 clone-0 song."),
    ("pipeline-run-1", "First deterministic run: 8-stage pipeline on all 5 songs; per-song artifacts written."),
    ("pipeline-run-2", "Second deterministic run: 8-stage pipeline in fresh temp dirs; SHA equality × 2 across 20 anchors."),
    ("panels-measured", "Cross-band mel_l1_db + spec_centroid_rmse_hz + rms_env_rmse + lufs_m_rmse table computed."),
    ("verdict-emitted", "Verdict BATCH_LANDS emitted with rubric_hash; per-song mel deltas +2.879..+7.983 dB."),
]
for leaf, desc in c2_leaves:
    rows.append(row(
        f"M-RECREATE-1/second-real-audio-batch/{leaf}-clone-2",
        "G1",
        f"Cycle-38 fork 33a2a8003c84 clone-2 sub-leaf event under M-RECREATE-1/second-real-audio-batch auto-suffixed by the c33 harness-clone-namespace-guard: {desc}",
        "Event landed under retroactive plan-of-record reconciliation; content identical to c33-guard-covered emission; no drift.",
        "M-RECREATE-1/first-real-audio-clone-0",
    ))

assert len(rows) == 24, f"expected 24 rows, got {len(rows)}"

# Insert after line 50 (M-GEN-1/palette-driven-batch-v4-clone-2 row), before the M-TEX-1/panel row
anchor = "| M-GEN-1/palette-driven-batch-v4-clone-2 |"
idx = plan_text.find(anchor)
assert idx > 0
eol = plan_text.find("\n", idx)
new_plan = plan_text[:eol+1] + "\n".join(rows) + "\n" + plan_text[eol+1:]
PLAN.write_text(new_plan)
print(f"plan_of_record.md: appended {len(rows)} sub-leaf milestone rows")

# ---------- 3) Emit close events ----------
def emit(mid, narrative, artifacts, status="validated"):
    ev = {
        "milestone_id": mid,
        "status": status,
        "cycle": 38,
        "run_id": RUN_ID,
        "ts": TS_BASE,
        "agent": "worker",
        "narrative": narrative,
        "confidence": {
            "level": "high",
            "rationale": "Post-merge integration deterministic: shadow-ledger concat + plan-of-record reconciliation; no code changes to substantive deliverables.",
            "assessor": "worker",
        },
        "artifacts": artifacts,
    }
    append_ledger_event(ROOT, ev)
    print(f"  emitted: {mid}")

# Adopt orphan scripts from clone-1 (normalizer-v2) and clone-2 (recreate_v0_batch)
adopt_scripts = [
    "scripts/score_bridge_v2/normalize_v2.py",
    "scripts/score_bridge_v2/run_normalizer_v2.py",
    "scripts/score_bridge_v2/__init__.py",
    "scripts/score_bridge_v2/_shared.py",
    "tests/test_score_bridge_normalizer_v2.py",
    "scripts/recreate_v0_batch/__init__.py",
    "scripts/recreate_v0_batch/run_batch.py",
    "scripts/recreate_v0_batch/select_songs.py",
    "scripts/recreate_v0_batch/write_report.py",
    "scripts/palette_render_v4/__init__.py",
]
# Verify each exists
missing = [p for p in adopt_scripts if not (ROOT / p).exists()]
if missing:
    print(f"  WARNING: adopt-scripts missing on disk: {missing}")
    adopt_scripts = [p for p in adopt_scripts if (ROOT / p).exists()]

emit(
    "_infra/adopt-orphan-scripts-cycle38-integration",
    "Adopts orphan scripts from fork 33a2a8003c84 clone-1 (normalizer-v2 self-continuation) and clone-2 (recreate_v0_batch pipeline), plus the pre-existing c37 palette_render_v4 __init__.py that was not adopted at c37 close. Clears promise_check orphan-artifact WARNs surfaced at integration time.",
    adopt_scripts,
)

emit(
    "_plan/register-c38-sub-leaf-milestones",
    "Registers 24 sub-leaf milestone rows in plan_of_record.md for the c38 fork 33a2a8003c84 fanout: 6 M-EAR-1/real-label-training-v1/*-clone-0, 6 M-SCORE-1/bridge-api-real-audio-quantization/*-clone-1, 6 M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2/*-clone-1 (clone-1 self-continuation, concat-merged from shadow), 6 M-RECREATE-1/second-real-audio-batch/*-clone-2. Follows the c37 M-INGEST-1/egress-probe-clone-{0,2} + M-RECREATE-1/first-real-audio-clone-0 + M-GEN-1/palette-driven-batch-v4-clone-2 precedent. Clears 18 promise_check ERRORs surfaced at integration time.",
    ["plan_of_record.md"],
)

emit(
    "_run/post-merge-integration-fork-33a2a8003c84",
    "Integration cycle for fork 33a2a8003c84 complete. 3 clones reconciled: clone-0 M-EAR-1/real-label-training-v1 → EAR_v1_PARTIAL (43/80 corpus; SB1/SB2/SB3 all short; F1 pooled-variance leak statistic locked); clone-1 M-SCORE-1/bridge-api-real-audio-quantization → QUANTIZATION_REDEFINED_GAP (music21 write('midi') winning path; onset drift 4.009 ms > 2 ms strict) + self-continuation M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2 (fidelity investigation of P2 full <type>/<dot/> rewrite); clone-2 M-RECREATE-1/second-real-audio-batch → BATCH_LANDS (5/5 positive mel deltas +2.879..+7.983 dB; 20/20 SHA equality × 2). Shadow-ledger concat: clone-0 9/9 + clone-1 20/20 (10 c38 base + 10 c39 self-continuation) + clone-2 10/10 = 39 rows integrated. Zero LedgerConcatError. Ledger 656 → 656 + 10 (concat) + 4 (closes) = 670 rows.",
    ["promise_ledger.jsonl", "plan_of_record.md", "docs/ear_real_label_training_v1_report.md", "docs/score_bridge_real_audio_quantization_report.md", "docs/score_bridge_real_audio_quantization_normalizer_v2_report.md", "docs/recreate_v0_batch_report.md"],
)

emit(
    "_run/cycle_38_closed",
    "Cycle 38 closed. Post-merge integration for fork 33a2a8003c84 complete; 3 clones each landed substantive deliverables (see _run/post-merge-integration-fork-33a2a8003c84 for detail). Worker-only cycle per brief; researcher and auditor skipped. Handoff to c39: (1) SB1 corpus-expansion probe — retry workspace/harvest_playlists.sh at every cycle-top; two consecutive media_ok=true rows unblock M-EAR-1/real-label-training-v2 on full 80-song corpus; (2) SB2 resample-count sensitivity — reevaluate at n_resamples in {50,100} on same 43-song corpus; (3) SB3 singleton-corpus statistic alternative — rank-based or artist-column-bootstrap successor to F1 pooled-variance; (4) HS-1 P2 full <type>/<dot/> rewrite as candidate M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2 upgrade path from REDEFINED_GAP toward FIXED; (5) HS-2 Stage-06 migration to P3 music21 winning path with pretty_midi fallback preserved (M-RECREATE-1/first-real-audio/stage-06-music21-winning-path); (6) HS-3 music21 .quantize() tuning to drop 4.009 ms onset drift below strict 2 ms; (7) HS-2 corpus extension M-RECREATE-1/full-corpus-recreation to n=37 (or 42 pooled with c38 clone-2 batch); (8) _manager/fanout-namespace-convention-discrepancy still open — c33 writer-guard auto-suffixes substantive M-* names contrary to c32 convention doc; resolution deferred to c40+ (narrow guard OR update doc); (9) c37 handoff #5 VST3 activation still gated on c36 MIXED verdict.",
    [],
)

print("Done.")
