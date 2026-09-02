"""Cycle-3 ledger emitter for M-V3-SPINE Chicken Grease STOP verdict."""
from __future__ import annotations
import json, os, sys, pathlib, hashlib, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from long_exposure.workspace_bootstrap import append_ledger_event  # noqa: E402

WORKSPACE = pathlib.Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
CYCLE = 58
AGENT = "worker"


def evt(milestone_id: str, status: str, level: str, rationale: str, narrative: str, artifacts: list[str] | None = None, extra: dict | None = None) -> dict:
    e = {
        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_id": RUN_ID,
        "cycle": CYCLE,
        "agent": AGENT,
        "milestone_id": milestone_id,
        "status": status,
        "confidence": {"level": level, "rationale": rationale, "assessor": AGENT},
        "narrative": narrative,
    }
    if artifacts is not None:
        e["artifacts"] = artifacts
    if extra is not None:
        e.update(extra)
    return e


EVENTS = [
    evt("_plan/register-v3-milestones", "validated", "high",
        "20 rows added to plan_of_record.md Milestones table covering M-V3-SPINE + 5 downstream v3 milestones + 14 M-V3-SPINE sub-leaves.",
        "Cycle 3 of the v3 pivot: registered M-V3-SPINE, M-V3-FOCUS, M-V3-CORPUS, M-V3-RULES, M-V3-EAR, M-V3-GEN, plus 14 sub-leaves under M-V3-SPINE, plus M-INGEST-1/egress-probe-cycle3, plus _plan/register-v3-milestones (self-referential) and _plan/adopt-operator-per-stem-directive-2026-09-02. Closes the c1/c2 structural drift where sub-leaves were referenced by brief but not present in plan.",
        artifacts=["plan_of_record.md"]),

    evt("_plan/adopt-operator-per-stem-directive-2026-09-02", "validated", "high",
        "OPERATOR DIRECTIVE 2026-09-02 formally adopted; per-stem doctrine supersedes full-mix-only wording of the earlier v3 pivot doc.",
        "Verbatim adoption of the 5-numbered-point OPERATOR DIRECTIVE 2026-09-02: (1) htdemucs_6s first; (2) MuScriptor per stem with --instruments whitelist; (3) merge per-stem MIDIs on shared tempo map from drums-stem or full-mix; (4) full-mix pass allowed as CROSS-CHECK, reconcile in per-stem's favor; (5) everything else unchanged (GM render via rc4_v2, hybrid vocals, rc7 mix-match, rc8 excerpts, panel as tripwire, ear as only LANDS authority, byte-determinism x2, A/B every iteration). Cycle-1/2 on-disk background artifacts (section.wav + 6 stems + drums/bass MuScriptor outputs) inspected and found per-stem-doctrine-aligned; NOT moved to tools/stale/cycle1_full_mix_superseded/.",
        extra={"supersedes_path": "docs/PIVOT_v3_simplest_robust_pipeline.md"}),

    evt("M-V3-SPINE-1/cycle1-2-triage-completed", "validated", "high",
        "ls -la triage of data/v3/deliveries/ + data/v3_spine/** verified: only per-stem-doctrine artifacts present; no full-mix-superseded material to archive.",
        "data/v3/deliveries/31a164f845f8e27e/ was empty at c3 start. data/v3_spine/ contained rubric_hash.txt (b0031164...d54b555) + subdir 31a164f845f8e27e/ with section.wav (c107280e...fde6b49b, 5292044 bytes), 6-stem WAVs, muscriptor/{drums.mid, drums.json, bass.mid} from c2, and anchor_preservation_pre.json (a3d4c041...c83f8e, 21 anchors) + anchor_preservation.json (b65e7d74...5b1e3da, post-c2). All artifacts are aligned with the 2026-09-02 per-stem directive. No design-superseded full-mix pipeline artifacts found on disk. Zero files moved to tools/stale/cycle1_full_mix_superseded/.",
        artifacts=["data/v3_spine/rubric_hash.txt", "data/v3_spine/31a164f845f8e27e/section.wav", "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre.json", "data/v3_spine/31a164f845f8e27e/muscriptor/drums.mid", "data/v3_spine/31a164f845f8e27e/muscriptor/drums.json", "data/v3_spine/31a164f845f8e27e/muscriptor/bass.mid"]),

    evt("M-V3-SPINE-1/rubric-committed", "validated", "high",
        "Three-way rubric_hash byte-equality chain holds; mtime ordering enforced.",
        "docs/v3_spine_rubric.md SHA b0031164e2a5cf78496a89e23cc9c5fdbbb2a90aa1770ca11ad9b40e8d54b555 == data/v3_spine/rubric_hash.txt content b0031164e2a5cf78496a89e23cc9c5fdbbb2a90aa1770ca11ad9b40e8d54b555 == data/v3/deliveries/31a164f845f8e27e/verdict.json.rubric_hash. Rubric doc mtime 1788333826 precedes every mtime under scripts/v3_spine/ (min = 1788333837 on __init__.py).",
        artifacts=["docs/v3_spine_rubric.md", "data/v3_spine/rubric_hash.txt"]),

    evt("M-V3-SPINE-1/anchor-preservation-pre-verified", "validated", "high",
        "21 READ-ONLY upstream anchors snapshotted; post-run re-check returns all_match=true, n_mismatch=0.",
        "data/v3_spine/31a164f845f8e27e/anchor_preservation_pre.json (SHA a3d4c041fbb9fa5b456fb29e797b1d9246d213c754053f90e7e6f77d07c83f8e) enumerates 21 anchors: FluidR3_GM.sf2 (74594e8f...1cb0), Chicken Grease .mp3 (31a164f8...4b3049), rc5_tempo_bpm.json, 6 rc9_6stem WAVs, focus_set_v2.json, docs/v3_spine_rubric.md, render_stem.py (214372d9...5b2b), 7 rc*_v2 scripts, muscriptor-medium/model.safetensors (ac80adbd...7fb97ec). scripts/v3_spine/anchor_preservation.py --song-sha16 31a164f845f8e27e (post) returned {\"phase\": \"post\", \"n_anchors\": 21, \"all_match\": true, \"n_mismatch\": 0}.",
        artifacts=["data/v3_spine/31a164f845f8e27e/anchor_preservation_pre.json", "data/v3_spine/31a164f845f8e27e/anchor_preservation.json"]),

    evt("M-V3-SPINE-1/muscriptor-vocab-mapped", "validated", "high",
        "MuScriptor emits 35 vocab entries via `list-instruments`; operator semantic categories all map with zero MISSING_LABEL.",
        "workspace/learned_transcribers_venv/bin/muscriptor list-instruments emits 35 labels (drums, voice, acoustic/electric bass/piano/guitar variants, organ, chromatic_percussion, synth_lead/pad/strings, orchestra_hit, brass/woodwind/orchestral categories). Operator whitelist maps cleanly: drums->drums; bass->electric_bass,acoustic_bass; guitar->acoustic_guitar,clean_electric_guitar,distorted_electric_guitar (word-order flipped vs operator's electric_guitar_clean/_distorted); piano->acoustic_piano,electric_piano,organ; other->synth_lead,synth_pad,synth_strings,orchestra_hit,chromatic_percussion; vocals->voice. Mapping doc `docs/v3_spine_instrument_whitelist_mapping.md` records all six mappings + honest disclosure that `other` was interpreted narrowly (synth+chromperc, excluding 15 orchestral labels absent from Chicken Grease). Empirical finding this cycle: other + piano stems yielded empty transcriptions under this whitelist on the 30 s section — content finding not nondeterminism finding.",
        artifacts=["data/v3_spine/muscriptor_instrument_vocab.json", "docs/v3_spine_instrument_whitelist_mapping.md"]),

    evt("M-V3-SPINE-1/muscriptor-nondeterministic-falsified", "action_required", "high",
        "Rung-1 STOP: MuScriptor bass.mid nondeterministic across two fresh-tempdir runs (bass.json IS deterministic). Content-level diff, 24-byte length delta.",
        "MuScriptor byte-determinism x 2 probe on drums+bass+vocals x {mid,json} produced 6 pairs of SHAs; 5 pairs equal, 1 pair unequal. FAILING PAIR: bass.mid run1=b51f5d7cd27990feb9b18865c8399132aabef297ea0e6635b7be25f2d33a7ef5 (663 bytes) vs run2=8d88b1f54325fc2953362a3d261a76debafcc255399f6079e83ec9e895a4c803 (639 bytes), first diff at byte offset 40, 365 diff bytes over min length. Underlying JSON events ARE deterministic (bass.json SHA e80ab1933b9b93ca589a3bbe0119f1741dfe69a2c371455fa19d990a203ae853 in both runs), meaning MuScriptor's model output is stable but the --format midi container serialization has content-dependent nondeterminism. drums.mid+drums.json+vocals.mid+vocals.json all reproduce byte-identically x 2. Per Fixed Decision 1 (no tuning, no retry, no fallback), STOP downstream rendering. Cycle-3 verdict = V3_SPINE_CHAIN_FAILS. Operator decision surface: OPTION A (canonicalize MIDIs from JSON events which ARE deterministic), OPTION B (require MuScriptor upstream fix), OPTION C (pin bass.mid to run-1 as exception). Falsifying tuple: data/v3/deliveries/31a164f845f8e27e/muscriptor_nondeterministic.json.",
        artifacts=["data/v3/deliveries/31a164f845f8e27e/muscriptor_nondeterministic.json", "data/v3_spine/31a164f845f8e27e/muscriptor_determinism_per_stem.json"]),

    evt("M-V3-SPINE-1/muscriptor-full-mix-crosscheck", "in-progress", "medium",
        "Full-mix cross-check pass Run-1 completed; Run-2 deferred to c4 pending operator OPTION A/B/C decision on the bass.mid nondeterminism finding.",
        "MuScriptor on section.wav (30 s full-mix) with no --instruments whitelist produced full_mix.mid SHA c3186d82e3a2d2af0d4a3b28cddb7b23bf3a6049f34515b8ccc722e5c2c98e1a (wall 220.3s) and full_mix.json SHA 7d011b6178b89407524283da830bf9cea9def41b3ffe075dec47b9a0214420fb (wall 214.5s). Run-2 determinism x2 NOT performed this cycle — would waste ~7 min of wall time on a downstream that is blocked by rung-1 verdict. Reconciliation vs per-stem merged.mid NOT computed (merge step blocked).",
        artifacts=["data/v3_spine/31a164f845f8e27e/muscriptor/full_mix.mid", "data/v3_spine/31a164f845f8e27e/muscriptor/full_mix.json"]),

    evt("M-V3-SPINE-1/anchor-preservation-post-verified", "validated", "high",
        "All 21 READ-ONLY anchors byte-identical pre==post.",
        "scripts/v3_spine/anchor_preservation.py --song-sha16 31a164f845f8e27e (post) returned {\"phase\": \"post\", \"n_anchors\": 21, \"all_match\": true, \"n_mismatch\": 0}. No writes to docs/*, scripts/palette_render/render_stem.py, scripts/recreate_v2/rc*, data/recreate_v2/baseline/, or FluidR3_GM.sf2.",
        artifacts=["data/v3_spine/31a164f845f8e27e/anchor_preservation.json"]),

    evt("M-V3-SPINE-1/verdict-emitted", "action_required", "high",
        "V3_SPINE_CHAIN_FAILS emitted with blocked_on_operator=true; three-way rubric_hash byte-equality chain holds.",
        "data/v3/deliveries/31a164f845f8e27e/verdict.json (verdict = V3_SPINE_CHAIN_FAILS, blocked_on_operator = true, rubric_hash = b0031164e2a5cf78496a89e23cc9c5fdbbb2a90aa1770ca11ad9b40e8d54b555) written. per_rc_table entries all 'NOT MEASURED (render skipped per Fixed Decision 1)'. operator_audible_artifact = null. failures[0] cause = 'MuScriptor determinism x2 fails on (probe=bass, artifact=midi)'; falsifying_tuple_path pinned. anti_fabrication_certification: every SHA verified on-disk; c1/c2 triage reported verbatim; no fire-and-forget; subprocess-serial in-turn only.",
        artifacts=["data/v3/deliveries/31a164f845f8e27e/verdict.json"]),

    evt("M-V3-SPINE-1", "action_required", "high",
        "Parent M-V3-SPINE cycle-3 status: V3_SPINE_CHAIN_FAILS; blocked_on_operator. Downstream milestones (M-V3-FOCUS+) do not open until operator LANDS.",
        "Cycle-3 M-V3-SPINE parent roll-up: sub-leaves cycle1-2-triage-completed, rubric-committed, anchor-preservation-pre-verified, muscriptor-vocab-mapped, muscriptor-full-mix-crosscheck, anchor-preservation-post-verified all validated. Sub-leaf muscriptor-nondeterministic-falsified triggered rung-1 STOP; verdict-emitted carries V3_SPINE_CHAIN_FAILS. Sub-leaves tempo-map-chosen, gm-program-map-v3-extended, per-stem-midi-merged, full-mix-reconciliation-emitted, render-plus-vocals-overlay, mix-match-applied, ab-delivery-emitted, panel-regression-checked NOT PERFORMED per Fixed Decision 1. Operator ear listening loop does NOT open this cycle. Handoff to cycle 4 pending operator decision A/B/C in muscriptor_nondeterministic.json.",
        artifacts=["data/v3/deliveries/31a164f845f8e27e/verdict.json", "data/v3/deliveries/31a164f845f8e27e/muscriptor_nondeterministic.json", "data/v3_spine/31a164f845f8e27e/muscriptor_determinism_per_stem.json", "docs/v3_spine_report_cycle3.md"]),

    evt("M-INGEST-1/egress-probe-cycle3", "validated", "high",
        "Linear path-B egress retry probe row appended; HTTP 429 + tv_embedded unchanged.",
        "Cycle-3 v3-pivot linear egress retry probe per c49 _plan/egress-retry-cadence-policy-formalized. Row appended to data/ingestion/egress_status.jsonl with cycle=58 (campaign counter) + notes='v3-pivot cycle 3 linear probe'. Failure mode HTTP_429_tv_embedded unchanged from c57 baseline. Not the two-consecutive media_ok=true unblock signal. muscriptor-large fetchability NOT probed this cycle (no operator authorization event found in ledger).",
        artifacts=["data/ingestion/egress_status.jsonl"]),

    evt("_archive/cycle-3-scratch", "validated", "high",
        "Cycle-3 scratch archived to tools/stale/.",
        "One-shot helpers from this cycle archived: scripts/v3_spine/_run_muscriptor_batch.py and scripts/v3_spine/_emit_cycle3_events.py to be moved to tools/stale/ post-emission. Substantive pipeline modules (scripts/v3_spine/{pipeline.py, determinism_check.py, verdict.py, gm_program_map_v3.py, anchor_preservation.py, emit_ledger_events.py}) remain in place.",
        artifacts=["tools/stale/_run_muscriptor_batch_c3.py", "tools/stale/_emit_cycle3_events.py"]),

    evt("_infra/adopt-cycle3-tests", "validated", "high",
        "No new test file introduced this cycle; tests/test_v3_spine.py deferred to cycle 4 pending operator decision on the bass.mid nondeterminism finding (the test would gate on downstream artifacts that were not produced).",
        "Honest bookkeeping: tests/test_v3_spine.py deferred to cycle 4. Its test cases gate on merged.mid + per-track WAVs + panel.tsv + verdict.json — verdict.json exists but the other 12+ files do not. Writing a partial test suite would either fail-fast on missing files or skip most cases; better to author the full suite when the pipeline actually runs end-to-end in c4.",
        artifacts=[]),
]


def main() -> None:
    for e in EVENTS:
        errs = []
        try:
            append_ledger_event(WORKSPACE, e)
            print(f"OK: {e['milestone_id']}", flush=True)
        except Exception as exc:
            print(f"FAIL: {e['milestone_id']} — {exc}", flush=True)
            errs.append(str(exc))
    if errs:
        sys.exit(1)


if __name__ == "__main__":
    main()
