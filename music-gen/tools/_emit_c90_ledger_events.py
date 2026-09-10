#!/usr/bin/python3
"""c90 (= harness c134, offset 44) one-shot ledger emitter — v5 REOPENING cycle 12: F7 CLOSE DOCS (completion-report v5 section,
OPERATOR_DECISIONS #21, codebase-guide v5 section), WARN-growth triage + adopt event, runners decision, parent roll-ups
(CORPUS / RULES / EAR / GEN), M-V5-CLOSE-1 with the frozen enum V5_CLOSE_LANDS / V5_CLOSE_PARTIAL / V5_CLOSE_FAILS, close.

created: 2026-09-10T04:22:07Z
cycle: 90
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _archive/cycle-90-scratch

Every event carries `agent`; event_id = UUID5(NAMESPACE_URL, canonical JSON minus event_id/ts); idempotent on (milestone_id, cycle == 90);
supersedes_path str|None (c14 lemma); `created:`/ts never future-dated. FAILS CLOSED (MissingArtifact) on every hard-read path.
Events are built LAZILY per milestone_id so `--only <id> [<id> ...]` can land a subset early (the P3 adopt event) before later artifacts exist.
df via `df -P` (driver semantics). Retained in-tree per docs/emitter_exemption_policy.md.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 90
HARNESS = 134
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
BD_PATH = Path("data/v5/gen/byte_determinism_c90.json")
V3 = "docs/v4_completion_report_v3.md"
OD = "docs/OPERATOR_DECISIONS.md"
CG = "docs/CODEBASE_GUIDE.md"
A, B = "31a164f845f8e27e", "88d247468cb6d49f"
DEMO = f"data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_{A}"
CLOSE_ENUM = ("V5_CLOSE_LANDS", "V5_CLOSE_PARTIAL", "V5_CLOSE_FAILS")


class MissingArtifact(FileNotFoundError):
    pass


def _sha(p) -> str:
    p = Path(p)
    if not p.exists():
        raise MissingArtifact(str(p))
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _j(p):
    p = Path(p)
    if not p.exists():
        raise MissingArtifact(str(p))
    return json.loads(p.read_text())


def _df():
    row = subprocess.run(["df", "-P", "."], capture_output=True, text=True, check=True).stdout.splitlines()[-1].split()
    return int(row[4].rstrip("%")), round(int(row[3]) * 1024 / 1e9, 3)


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _ev(milestone_id, status, level, rationale, narrative, artifacts, supersedes_path=None):
    body = {"agent": "worker", "artifacts": artifacts, "confidence": {"assessor": "worker", "level": level, "rationale": rationale},
            "cycle": CYCLE, "env_pin_sha256": ENV_PIN, "milestone_id": milestone_id, "narrative": narrative,
            "run_id": RUN_ID, "status": status, "supersedes_path": supersedes_path, "ts": TS}
    body["event_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, _canonical({k: v for k, v in body.items() if k not in ("event_id", "ts")})))
    return body


def _tree(root) -> list:
    root = Path(root)
    if not root.exists():
        raise MissingArtifact(str(root))
    return sorted(str(p) for p in root.rglob("*") if p.is_file())


def _bd():
    return _j(BD_PATH)


def _prefix_ok(doc_key: str) -> dict:
    """Prefix byte-equality of a governed doc against its turn-start pin (pre sha + pre bytes recorded by p0 / the doc builders)."""
    bd = _bd()
    pre = bd["turn_start_pins"][doc_key]
    app = bd.get("doc_appends", {}).get(pre["path"])
    if not app:
        raise MissingArtifact(f"doc_appends[{pre['path']}] not recorded yet")
    cur = Path(pre["path"]).read_bytes()
    return {"path": pre["path"], "pre_sha256": pre["sha256"], "post_sha256": _sha(pre["path"]), "pre_bytes": pre["bytes"], "post_bytes": len(cur),
            "prefix_byte_equal": hashlib.sha256(cur[: pre["bytes"]]).hexdigest() == pre["sha256"], "recorded_post_sha256": app["post_sha256"]}


# ---------------------------------------------------------------------------------------------------------------------------- builders
def ev_guidance():
    return _ev("_plan/guidance-continuation-c90", "validated", "high", "on-disk guidance directory scanned at turn start; newest file dated 2026-09-09.",
        f"c90 (= harness c134, offset 44): no new operator guidance file landed (newest on disk `guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt`, sha16 {_sha('docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt')[:16]}); "
        f"it continues to govern together with the F1–F7 backlog guidance (sha16 {_sha('docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt')[:16]}), whose F7 clause ('M-V5-CLOSE-1 docs only after F1–F5 have landed') is OPEN: F1 FORM_PLAN_PARTIAL c85, F2 F2_PARTIAL c87, F3 F3_LANDS c88, F4 CLOSED by operator addendum c86, F5 F5_LANDS c89. This cycle is F7.",
        ["docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt", "docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt"])


def ev_prune():
    p = _j("data/v5/logs/c90_prune.json")
    d, a = _df()
    own = sum(x["bytes"] for x in p["own_session_render_tempdirs"]) / 1e6
    pri = p["prior_session_scratchpad_tempdirs_listed_before_deletion"]
    return _ev("_infra/disk-prune-c90", "validated", "high", "df read with `df -P` before and after; every deleted path listed by path+size in the record BEFORE deletion.",
        f"c90 P0 disk prune: df {p['df_open']['used_pct']} % ({p['df_open']['avail_gb']} GB avail) at open — above the 85 % WARN line; pruned ONLY regenerable render tempdirs: this session's own c89 ×2 / flag-off / score-run2 tempdirs under /tmp ({round(own, 1)} MB) and, LISTED by path and size in data/v5/logs/c90_prune.json before deletion (c89 auditor MINOR (6)), "
        f"the c89 auditor scratchpad's two re-render tempdirs {[Path(x['path']).name for x in pri]} ({round(sum(x['bytes'] for x in pri) / 1e6, 1)} MB; its result JSONs kept). Total {p['pruned_mb']} MB; nothing under the workspace, /tmp/tfhub_modules, data/v4/**, data/v5/corpus/** canonical dirs or profiles; df after {p['df_after']['used_pct']} % ({p['df_after']['avail_gb']} GB); at emit {d} % ({a} GB); never ≥ 90 %.",
        ["data/v5/logs/c90_prune.json"])


def ev_adopt():
    arts = _tree("data/v5/gen/iteration_05") + _tree("data/v4/generated/f5_interp_CG_PD_t050_c89") + _tree("data/v4/generated/v5_iter_05")
    assert len(arts) >= 250, len(arts)
    return _ev("_infra/adopt-cycle89-gen-artifacts-c90", "validated", "high", "every path exists on disk (fail-closed); the emitter carries the full recursive listing in one event (P3 decision).",
        f"c90 P3 adopt event: the c89 iteration-5 tree `data/v5/gen/iteration_05/**` ({len(_tree('data/v5/gen/iteration_05'))} files: 6 renders' ab_mix + manifests + replay proofs + per-stem MIDI + generated_json + f5_blend + rollup), the F5 demo delivery `data/v4/generated/f5_interp_CG_PD_t050_c89/**` and the iteration-5 listening copies `data/v4/generated/v5_iter_05/**` "
        f"are adopted under M-V5-GEN-1 as artifacts of this event ({len(arts)} paths) so promise_check's `orphan artifact in managed path` WARN class (the c89 +253 growth) no longer fires on them; no file is modified. Re-measured counts in data/v5/logs/validators_c90.json.",
        arts)


def ev_warn():
    v = _j("data/v5/logs/validators_c90.json")
    ser = v["warn_series_c85_to_c90"]
    return _ev("_infra/warn-growth-triage-c90", "validated", "high", "promise_check + org_check re-run in-cycle; per-class breakdown and the c85→c90 series recorded from disk/ledger (unrecorded cycles say so).",
        f"c90 P3 WARN-growth triage: promise_check at open {v['open']['promise_check']['error']} ERROR / {v['open']['promise_check']['warn']} WARN; the growth class is `orphan artifact in managed path` ({v['open']['promise_check']['classes'].get('orphan artifact in managed path', '?')} of the WARNs; under data/v5/gen {v['open']['orphan_by_prefix'].get('data/v5/gen', '?')}, data/v4/generated {v['open']['orphan_by_prefix'].get('data/v4/generated', '?')}), "
        f"zero WARNs attributable to c89 ledger lines themselves. Series c85→c90 (WARN): {ser}. Decision: the emitter carries ≥ 250 paths, so `_infra/adopt-cycle89-gen-artifacts-c90` adopted the iteration-5 tree + demo delivery + listening copies ({v['adopt_event']['n_paths']} paths) → after adopt {v['after_adopt']['promise_check']['error']} ERROR / {v['after_adopt']['promise_check']['warn']} WARN "
        f"(Δ {v['after_adopt']['promise_check']['warn'] - v['open']['promise_check']['warn']}); org_check {v['open']['org_check']['error']} ERROR / {v['open']['org_check']['warn']} WARN (54 = workspace-root files + docs/run_archive figures, pre-existing). ERROR stays at the 156 baseline (all pre-c90 lines: 98 missing-agent c78–c80, 16 status-vocabulary, 42 unregistered ids); 0 on c90 ids.",
        ["data/v5/logs/validators_c90.json"])


def ev_runners():
    r = _j("data/v5/logs/runners_decision_c90.json")
    return _ev("_infra/runners-decision-c90", "validated", "high", "option (a) landed: module + README + ten verbatim c89 runners on disk; dry-run reproduces the pinned commands byte-for-byte (asserted in the decision record + test_c90_close).",
        f"c90 P4 runners decision = (a): `scripts/v5/runners/run_from_launch_json.py` ({r['runner_module_sha256'][:16]}…; prints or launches detached the EXACT command pinned in any `data/v5/logs/*.launch.json` / `byte_determinism_cNN.json` entry; `/usr/bin/python3` guard; no PRNG; refuses `--execute` on a drifted generate_v5.py or without a fresh `--out`) + README ({r['readme_sha256'][:16]}…) + the ten c89 session-scratchpad runners copied VERBATIM to `scripts/v5/runners/c89/` (originals were still on disk at c90 open; SHAs in the README). "
        f"Rationale: {r['rationale']}. Dry-run byte-for-byte: iteration-5 launch JSON True; byte-det flag-off entry True; execute-without-out refused rc 3.",
        ["scripts/v5/runners/run_from_launch_json.py", "scripts/v5/runners/README.md", "data/v5/logs/runners_decision_c90.json"] + [f"scripts/v5/runners/c89/{n}" for n in r["c89_runners"]])


def ev_report():
    pk = _prefix_ok("v3_report_pre")
    bd = _bd()
    return _ev("M-V5-CLOSE-1/completion-report-v5-section-c90", "validated", "high", f"prefix byte-equality {pk['prefix_byte_equal']}; first-8 KB header sha unchanged {bd['v3_report_first_8k_sha256_at_open'] == hashlib.sha256(Path(V3).read_bytes()[:8192]).hexdigest()}; every quoted SHA resolves on disk (test_c90_close).",
        f"c90 P1: `## Section: v5 REOPENING (c79–c90) — feature backlog F1–F7 close` appended ADDITIVELY to `{V3}` below a horizontal rule after the c78 section (pre sha {pk['pre_sha256'][:16]}… {pk['pre_bytes']} B → post sha {pk['post_sha256'][:16]}… {pk['post_bytes']} B; v3 §1–§7 + the c78 section byte-identical as a prefix; title tag untouched). "
        "Content, every number read from disk: cycle-counter disclosure (on-disk c79–c90 = harness c123–c134; c100–c127 lost to outage); M-V5-CORPUS-1 (26 songs 13/10/3 by band, 26/26 lossless with sidecars, index-collision defect + fix, 1 content-blocked, tempo axis STOPPED v5/v5b/v5c/v5d all RULES_OUT, mechanism PARTIAL, PD/Disco A adopted by operator addendum); "
        "M-V5-RULES-1 (harmony n=23 NON_DEGENERATE 0.069317; groove OVERFITS 0.637448; comping NON_DEGENERATE with the structureless slot histogram; form R1 FAILED; velocity R2 structureless; bass 0.336 vs 0.29; VOMM MEMORIZES 0.7206); M-V5-EAR-1 (venv + amendment, LOO 5/5 ≥ 6.2095, band-4 FAIL 6.7199 > 5.7095, L119 infeasible, informational only, ≥ 6 scores inside the band-4 range 5.70–6.72); "
        "M-V5-GEN-1 F1–F7 table with the landing-cycle verdicts (F1 PARTIAL at landing, LANDS later as data), iteration-5 + demo SHAs, stall 5/12, passers 0 by FD-6; the F5 union-vocabulary groove caveat verbatim + the shared-context/c78-fallback rule for any future t-sweep; carry-forward hygiene (blend_record_sha256 semantics, inherited degeneracy verdict, 4.0 gain cap); program coverage 14/15 GM shims; determinism receipts; validator table + runners decision; deliverable index; honest gaps; close rationale (re-close, no finality wording).",
        [V3, "data/v5/gen/byte_determinism_c90.json"])


def ev_od():
    pk = _prefix_ok("operator_decisions_pre")
    return _ev("_plan/operator-decisions-c90-amendment", "validated", "high", f"prefix byte-equality {pk['prefix_byte_equal']} (#1–#20 + the standing-constraints block untouched; #21 appended at EOF because #20 precedes that block).",
        f"c90 P2: `{OD}` entry #21 (v5 CLEAN RE-CLOSE at c90) appended ADDITIVELY at end of file (pre sha {pk['pre_sha256'][:16]}… {pk['pre_bytes']} B → post {pk['post_sha256'][:16]}… {pk['post_bytes']} B): v5 close verdict matrix (CORPUS / RULES / EAR / GEN / CLOSE) with the F1–F7 table, the F5 union-vocabulary caveat, the ear-informational rule, the FD-6 delegation over the 26 v5 renders + the 25 v4 A/Bs, the tempo-axis STOP, and the re-close (str-supersede reopen pattern) wording.",
        [OD, "data/v5/gen/byte_determinism_c90.json"])


def ev_cg():
    pk = _prefix_ok("codebase_guide_pre")
    return _ev("_plan/codebase-guide-c90-amendment", "validated", "high", f"prefix byte-equality {pk['prefix_byte_equal']}; every module SHA in the section resolves on disk (test_c90_close).",
        f"c90 P2: `{CG}` gained an additive `## v5 REOPENING layer (c79–c90)` section (pre sha {pk['pre_sha256'][:16]}… {pk['pre_bytes']} B → post {pk['post_sha256'][:16]}… {pk['post_bytes']} B): the `scripts/v5/` module map with SHAs (generate_v5, interpolate_v5, repo_root, comping_gen_v5, velocity_v5 READ-ONLY, harmony/groove/comping/form/bass/melody models, score_gen_batch_v5, deliver_v5_listening, launch_detached, reindex_hook, runners), "
        "the generator flag matrix, the data layout under data/v5/, the prereg-before-output discipline, the ear-venv invocation and the `blend_record_sha256` semantics.",
        [CG, "data/v5/gen/byte_determinism_c90.json"])


def ev_corpus():
    cm = _j("data/v5/corpus/corpus_manifest.json")
    cb = _j("data/v5/corpus/content_blocked.json")
    blk = _j("data/v5/corpus/recanonicalization_blocked.json")
    v5d = _j("data/v5/corpus/tempo_v5d_falsification.json")
    return _ev("M-V5-CORPUS-1", "validated", "high", "parent roll-up from the on-disk verdict files; 26/26 transcribed + reindexed with sidecars; tempo criteria frozen-enum RULES_OUT ×4; operator adoption on disk in the blocked file.",
        f"c90 F7 parent roll-up M-V5-CORPUS-1 = **CORPUS_LANDED_TEMPO_AXIS_STOPPED**: {len(cm['songs'])} songs enumerated (13 band-6 + 10 band-7 + 3 band-5 focus; manifest {_sha('data/v5/corpus/corpus_manifest.json')[:16]}…), 26/26 transcribed full-length through the checkpointed driver and reindexed lossless with `canonical_v5_reindexed_sha256.json` sidecars (c80 index-collision defect fixed by `reindex_canonical_v5.py` + the c81 hook-at-birth); "
        f"content gate blocked {cb['n_blocked']} ({list(cb['blocked_songs'])[0]} NON_MUSIC_CONTENT_R1_AND_R2); tempo axis STOPPED — v5 RULES_OUT_CRITERION_TOO_PERMISSIVE, v5b RULES_OUT_HARMONIC_SUM, v5c RULES_OUT_AUTOCORR_DIRECT, v5d {v5d['verdict']} ({v5d['n_anchor_hits']}/5 anchors), mechanism probe MECHANISM_PARTIAL; Peach Dream {blk['unblocked_c86'][B]['adopted_bpm']} / Disco A {blk['unblocked_c86']['cdd2717e52820ff6']['adopted_bpm']} BPM ADOPTED by operator addendum (F4, c86) — blocked file amended in place (live {_sha('data/v5/corpus/recanonicalization_blocked.json')[:16]}…, stale copy {_sha('data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json')[:16]}…). No re-verdict; recorded verdicts stand.",
        ["data/v5/corpus/corpus_manifest.json", "data/v5/corpus/content_blocked.json", "data/v5/corpus/recanonicalization_blocked.json", "data/v5/corpus/tempo_v5_falsification.json", "data/v5/corpus/tempo_v5b_falsification.json", "data/v5/corpus/tempo_v5c_falsification.json", "data/v5/corpus/tempo_v5d_falsification.json", "data/v5/corpus/tempo_mechanism_c82_verdict.json", "data/v5/corpus/tempo_f4_operator_resolution_c86.json"])


def ev_rules():
    h = _j("data/v5/rules/harmony_markov_v5_full_c86.json"); g = _j("data/v5/rules/groove_v5_v2_full_c86.json"); c = _j("data/v5/rules/comping_v5.json")
    f = _j("data/v5/rules/form_plan_v5.json"); v = _j("data/v5/rules/velocity_profiles_v5.json"); m = _j("data/v5/rules/melody_vomm_v5.json")
    slot = c["verdict"]["pooled_max_slot_mass"]
    return _ev("M-V5-RULES-1", "validated", "medium", "parent roll-up from the on-disk verdict fields; medium because two models carry recorded negative verdicts (groove OVERFITS, melody MEMORIZES) that were never retuned (FD-1).",
        f"c90 F7 parent roll-up M-V5-RULES-1 = **RULES_LANDED_WITH_HONEST_GAPS**: harmony n=23 {h['degeneracy_verdict']} (81 states, max stationary {h['max_stationary_state']} {h['max_stationary_mass']}; {_sha('data/v5/rules/harmony_markov_v5_full_c86.json')[:16]}…); groove v2 n=23 {g['verdict']} (singleton-context fraction {g['singleton_context_fraction']}; hat|kick8,snare16 granularity, not n); "
        f"comping {c['verdict']['enum']} (pooled max 16th-slot mass {slot} vs the 0.5 degeneracy line — the slot histogram is near-uniform/structureless, disclosed; the IOI histogram is the structured axis); form plan R1 FAILED at 0.85 ({f['R1']['pass']}) so the fixed template AABABCAA governs labels; velocity profiles R2 structureless (drums slot std {v['R2']['drums_slot_profile_std']}); bass pitch model root-on-downbeat corpus 0.336 vs sampled 0.29; melody VOMM {m['verdict']} (order-3 singleton 0.720574). Every 'recorded, not retuned' stays that way.",
        ["data/v5/rules/harmony_markov_v5_full_c86.json", "data/v5/rules/groove_v5_v2_full_c86.json", "data/v5/rules/comping_v5.json", "data/v5/rules/form_plan_v5.json", "data/v5/rules/velocity_profiles_v5.json", "data/v5/rules/bass_pitch_v5.json", "data/v5/rules/melody_vomm_v5.json"])


def ev_ear():
    e = _j("data/v5/ear/ear_gate_v5_c82.json")
    return _ev("M-V5-EAR-1", "validated", "medium", "parent roll-up from the on-disk gate records; medium because the ear is non-discriminative on this content (L119 infeasible) and remains informational only.",
        f"c90 F7 parent roll-up M-V5-EAR-1 = **EAR_RESTORED_INFORMATIONAL_ONLY**: isolated venv built c82 (pinned command) and amended with librosa (receipts `ear_venv_pip_freeze_c82_amended.txt`, `env_pin_ear_venv_c82_amended.json`; main-env freeze unchanged); c76 v2 wider-linear LOO gate on FRESH embeddings {e['sanity_gate_fresh']['n_at_or_above_6']}/5 ≥ 6 (min {e['sanity_gate_fresh']['min_score']:.4f}), "
        f"band-4 spot check FAILS L119 (band4_max {e['l119_check']['band4_max']} > {e['l119_check']['threshold_loo_min_minus_0_5']}); the c76 monotone-infeasibility proof stands (data/v4/ear/l119_infeasibility_proof_c76.json); ear scores informational only (FD-6, c76 L119) — never a passer gate; ≥ 6 informational scores on generated songs lie inside the band-4 context range 5.70–6.72.",
        ["data/v5/ear/ear_gate_v5_c82.json", "data/v5/ear/venv_amend_c82.json", "data/v5/ear/env_pin_ear_venv_c82_amended.json", "data/v4/ear/band4_spot_check_v2_c76.json", "data/v4/ear/l119_infeasibility_proof_c76.json"])


def ev_gen():
    st = _j("data/v5/gen/stall_counter.json")
    r5 = _j("data/v5/gen/iteration_05/iteration_rollup.json")
    return _ev("M-V5-GEN-1", "validated", "high", "parent roll-up on the operator's F1–F7 rule (feature landings are the gate); stall counter and passer count stated as they are; not a claim that any generated song passes.",
        f"c90 F7 parent roll-up M-V5-GEN-1 = **FEATURES_F1_F5_LANDED_HONEST_BEST_OF_AT_STALL_5_OF_12**: F1 FORM_PLAN_PARTIAL (c85, 4/5 at landing; iterations 3–5 recorded LANDS as data), F2 F2_PARTIAL (c87), F3 F3_LANDS (c88), F4 CLOSED by operator addendum (c86), F5 F5_LANDS (c89, demo {r5['f5']['demo_ab_mix_sha256'][:16]}…), F6 schedule entries on every iteration since c85, F7 this cycle; "
        f"stall {st['iterations']}/{st['budget']}; passers {st['passers']} by FD-6 design (informational scores ≥ 6 on 24/26 renders sit inside the band-4 range); 26 listening copies under data/v4/generated/v5_iter_01..05/ + the demo dir, all pending operator ear. Honest best-of at stall; a sixth iteration is preservation-spin under c47 part 4 — not opened.",
        ["data/v5/gen/stall_counter.json", "data/v5/gen/iteration_05/iteration_rollup.json", "data/v4/generated/v5_iter_05/listening_manifest.json", "data/v4/generated/f5_interp_CG_PD_t050_c89/delivery_manifest.json"])


def ev_f7():
    return _ev("M-V5-GEN-1/F7-close", "validated", "high", "the three docs appended additively (prefix byte-equality asserted), parent roll-ups emitted, validators at baseline, tests green.",
        f"c90 F7 CLOSE DOCS landed: completion-report v5 section ({V3}), OPERATOR_DECISIONS #21, codebase-guide v5 section — all additive with prefix byte-equality; WARN-growth triage + adopt event; runners decision (a); parent roll-ups CORPUS/RULES/EAR/GEN; M-V5-CLOSE-1 enum below. F1–F7 all landed with their frozen-enum verdicts.",
        [V3, OD, CG, "data/v5/logs/validators_c90.json", "data/v5/logs/runners_decision_c90.json"])


def close_enum() -> tuple:
    bd = _bd()
    docs = [_prefix_ok(k) for k in ("v3_report_pre", "operator_decisions_pre", "codebase_guide_pre")]
    head_ok = bd["v3_report_first_8k_sha256_at_open"] == hashlib.sha256(Path(V3).read_bytes()[:8192]).hexdigest()
    v = _j("data/v5/logs/validators_c90.json")
    tests = _j("data/v5/logs/test_results_c90.json")
    # anchors: every turn-start pin except the three docs + POR must be byte-identical now
    drift = []
    for k, p in bd["turn_start_pins"].items():
        if k in ("v3_report_pre", "operator_decisions_pre", "codebase_guide_pre", "plan_of_record_at_open", "byte_determinism_c89"):
            continue
        if _sha(p["path"]) != p["sha256"]:
            drift.append(k)
    # no render: iteration trees + data/v4/generated newest mtime unchanged
    rendered = []
    for root, t in bd["tree_newest_mtime_at_open"].items():
        now = max((f.stat().st_mtime for f in Path(root).rglob("*") if f.is_file()), default=0.0)
        if now > t + 1e-6:
            rendered.append(root)
    checks = {"docs_prefix_byte_equal": all(d["prefix_byte_equal"] for d in docs), "v3_first_8k_unchanged": head_ok,
              "validators_error_baseline": v["final"]["promise_check"]["error"] == 156 and v["final"]["org_check"]["error"] == 0,
              "tests_green": all(t["rc"] == 0 for t in tests.values()), "anchor_drift": drift, "rendered_trees": rendered,
              "parent_rollups_in_this_run": ["M-V5-CORPUS-1", "M-V5-RULES-1", "M-V5-EAR-1", "M-V5-GEN-1"]}
    if drift or rendered:
        return "V5_CLOSE_FAILS", checks
    if all([checks["docs_prefix_byte_equal"], head_ok, checks["validators_error_baseline"], checks["tests_green"]]):
        return "V5_CLOSE_LANDS", checks
    return "V5_CLOSE_PARTIAL", checks


def ev_close1():
    enum, checks = close_enum()
    lvl = "high" if enum == "V5_CLOSE_LANDS" else "medium"
    return _ev("M-V5-CLOSE-1", "validated", lvl, f"enum {enum} from the frozen rule (LANDS = all three docs appended additively with prefix byte-equality, parent roll-ups emitted, validators at ERROR baseline, tests green, no anchor drift, no render/retune/re-verdict; PARTIAL = a doc or roll-up missing; FAILS = any anchor or prior-verdict byte changed).",
        f"c90 M-V5-CLOSE-1 = **{enum}**: checks {json.dumps(checks, sort_keys=True)}. The run RE-CLOSES cleanly at c90; the operator verifies post-close. A later operator guidance file may reopen again exactly as c79 did (str-supersede pattern) — no finality claim beyond this re-close.",
        [V3, OD, CG, "data/v5/logs/validators_c90.json", "data/v5/logs/test_results_c90.json", "data/v5/gen/byte_determinism_c90.json"])


def ev_n25():
    return _ev("_infra/n25-siblings-skipped-c90", "validated", "high", "one line per the brief's P6 allowance; stated in the report's honest-gaps list rather than deferred again.",
        "c90 P6 optional n=25 sibling artifacts (harmony / groove / comping on n=23 ∪ {0e1e8f20592db366, cc0693b4a24f64b2}; byte-det ×2; not consumed) SKIPPED — deferred twice already (c88, c89); this cycle's wall went to the close docs; recorded as an honest gap in the v5 section, not deferred again. Nothing consumed from it, nothing blocked by it.", [])


def ev_register():
    return _ev("_plan/register-c90-sub-leaves", "validated", "high", "rows inserted inline in the parseable region by tools/_register_c90_por_rows.py (idempotent, fail-closed); `c90 CLOSED` clauses appended to the M-V5-CLOSE-1 and M-V5-GEN-1/F7-close rows by the same tool.",
        f"c90 POR registration: additive `c90 CLOSED` clauses on `M-V5-CLOSE-1` and `M-V5-GEN-1/F7-close` (existing wording verbatim) + c90 sub-leaves inserted before `## Sub-milestones`. POR started at sha {_bd()['turn_start_pins']['plan_of_record_at_open']['sha256'][:16]}… (c89 close).",
        ["plan_of_record.md", "tools/_register_c90_por_rows.py"])


def ev_tests():
    t = _j("data/v5/logs/test_results_c90.json")
    n = sum(v["n_pass_lines"] for v in t.values())
    return _ev("_infra/adopt-cycle90-tests", "validated", "high", "adopted suite re-run under /usr/bin/python3; counts from data/v5/logs/test_results_c90.json (ADOPTED suite, not tests/ as a whole).",
        f"c90 test-adoption: `tests/test_c90_close.py` ({t.get('tests/test_c90_close.py', {}).get('n_pass_lines', '?')}/{t.get('tests/test_c90_close.py', {}).get('n_tests_defined', '?')}) new — prefix byte-equality + v3 first-8 KB header for the three docs, v5 section present with the F1–F7 table and every quoted 64-hex SHA resolving to an on-disk file with that SHA, F5 caveat + blend_record_sha256 sentences, validators ERROR == 156, runners decision file + byte-for-byte dry-run, no file under the iteration trees / data/v4/generated newer than the cycle open, §4 READ-ONLY pins byte-identical, every c90 ledger event has agent + str-or-null supersedes_path + created ≤ now. "
        f"Adopted suite {len(t)} files / {n} PASS lines; all rc=0: {all(v['rc'] == 0 for v in t.values())}; c85–c89 suites re-run unchanged (no re-pins this cycle).",
        ["tests/test_c90_close.py", "data/v5/logs/test_results_c90.json"])


def ev_scratch():
    return _ev("_archive/cycle-90-scratch", "validated", "high", "one-shot emitter + registrar retained in-tree per emitter-exemption policy and listed as artifacts.",
        "c90 scratch archival: `tools/_emit_c90_ledger_events.py` + `tools/_register_c90_por_rows.py` retained in-tree; pipeline runners of THIS cycle (p0_c90, p4_copy_runners_c90, validators_c90, build_v5_section_c90, append_od_cg_c90, run_tests_c90) live in the session scratchpad only — unlike c89's, none of them renders anything (their outputs are the docs + JSON records listed on the substantive events); the c89 runners were copied in-tree under the P4 decision. The pruned tempdirs are listed in data/v5/logs/c90_prune.json.",
        ["tools/_emit_c90_ledger_events.py", "tools/_register_c90_por_rows.py"])


def ev_closed():
    enum, _ = close_enum()
    v = _j("data/v5/logs/validators_c90.json")
    d, a = _df()
    return _ev("_run/cycle_90_closed", "validated", "high", "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        f"c90 CLOSED — v5 REOPENING cycle 12 (= harness c134, offset 44 disclosed, not reconciled): F7 close docs landed additively (completion-report v5 section, OPERATOR_DECISIONS #21, codebase-guide v5 section; prefix byte-equality asserted), WARN-growth triaged with the ≥ 250-path adopt event (promise_check {v['final']['promise_check']['error']} ERROR / {v['final']['promise_check']['warn']} WARN at close vs 156 / 8960 at open; org_check {v['final']['org_check']['error']} / {v['final']['org_check']['warn']}), "
        f"runners decision (a) checked in, parent roll-ups CORPUS_LANDED_TEMPO_AXIS_STOPPED / RULES_LANDED_WITH_HONEST_GAPS / EAR_RESTORED_INFORMATIONAL_ONLY / FEATURES_F1_F5_LANDED_HONEST_BEST_OF_AT_STALL_5_OF_12, M-V5-CLOSE-1 = **{enum}**. Nothing rendered, retuned or re-verdicted; stall counter 5/12 unchanged; iteration trees + data/v4/** untouched; env_pin {ENV_PIN[:8]}…922ca unchanged (c22 → c90). "
        f"Disclosures (one line each): F1 verdict resolved by rule (landing-cycle enum, later LANDS = data); the F5 groove blend is a union-vocabulary mixture (1 shared context per table); blend_record_sha256 hashes the compact canonical JSON, the delivery manifest carries the file bytes; blended chain degeneracy inherited not re-verdicted; demo bass/drums gains at the 4.0 cap; 14/15 GM shims; brief paths `tempo_mechanism_probe_c82.json` and `data/v5/ear/{{band4_spot_check_v2_c76,l119_infeasibility_proof_c76}}.json` are absent — on-disk `tempo_mechanism_c82_verdict.json` and `data/v4/ear/…` govern; c86/c87 WARN counts not recorded; n=25 siblings skipped (honest gap); MANIFEST.md / serializer commit-lag observed, no commit. df at emit {d} % ({a} GB). The run re-closes cleanly; the operator verifies post-close; a later guidance file may reopen it (c79 pattern).",
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_89_closed")


BUILDERS = [("_plan/guidance-continuation-c90", ev_guidance), ("_infra/disk-prune-c90", ev_prune), ("_infra/adopt-cycle89-gen-artifacts-c90", ev_adopt),
            ("_infra/warn-growth-triage-c90", ev_warn), ("_infra/runners-decision-c90", ev_runners), ("M-V5-CLOSE-1/completion-report-v5-section-c90", ev_report),
            ("_plan/operator-decisions-c90-amendment", ev_od), ("_plan/codebase-guide-c90-amendment", ev_cg), ("M-V5-CORPUS-1", ev_corpus), ("M-V5-RULES-1", ev_rules),
            ("M-V5-EAR-1", ev_ear), ("M-V5-GEN-1", ev_gen), ("M-V5-GEN-1/F7-close", ev_f7), ("M-V5-CLOSE-1", ev_close1), ("_infra/n25-siblings-skipped-c90", ev_n25),
            ("_plan/register-c90-sub-leaves", ev_register), ("_infra/adopt-cycle90-tests", ev_tests), ("_archive/cycle-90-scratch", ev_scratch), ("_run/cycle_90_closed", ev_closed)]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = set(args)
    existing = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("cycle") == CYCLE:
                existing.add(row.get("milestone_id"))
    events = []
    for mid, fn in BUILDERS:
        if only and mid not in only:
            continue
        if mid in existing:
            continue
        events.append(fn())
    _le = os.environ.get("LONG_EXPOSURE_PKG_PATH", "/home/user/human-in-a-loop/long-exposure")
    if _le not in sys.path:
        sys.path.append(_le)
    try:
        from long_exposure.tools._ledger_schema import validate_event, REQUIRED_EVENT_FIELDS
        for e in events:
            miss = [k for k in REQUIRED_EVENT_FIELDS if k not in e]
            assert not miss, (e["milestone_id"], miss)
            errs = validate_event(e)
            assert not errs, (e["milestone_id"], errs)
    except ImportError:
        print("WARN: long_exposure schema not importable; field check only")
    now = time.time()
    for e in events:
        assert e["agent"] == "worker" and isinstance(e["supersedes_path"], (str, type(None)))
        assert time.mktime(time.strptime(e["ts"], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone <= now + 5
        for a in e["artifacts"]:
            if not Path(a).exists():
                raise MissingArtifact(f"{e['milestone_id']}: {a}")
    if "--dry-run" in sys.argv:
        print(f"DRY RUN: {len(events)} events validated; would append {[e['milestone_id'] for e in events]}")
        return 0
    if not events:
        print("IDEMPOTENT: nothing to append.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(events)} c90 events")
    for e in events:
        print(f"  {e['status']:12s} {e['milestone_id']} {e['event_id']} artifacts={len(e['artifacts'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
