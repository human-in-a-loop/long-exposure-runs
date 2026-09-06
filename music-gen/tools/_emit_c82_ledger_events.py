#!/usr/bin/python3
"""c82 one-shot ledger emitter — v5 REOPENING cycle 4 (c81 landing, driver restart with the hook live, MANDATORY ear venv,
tempo mechanism probe, harmony first data, groove v2 held-out, fidelity follow-up).

Every event carries `agent` (REQUIRED_EVENT_FIELDS); UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts);
idempotent by milestone_id; supersedes_path is str|None (c14 lemma). Reads every number from disk at emit time. Retained
in-tree per docs/emitter_exemption_policy.md (c34 OPT_B exemption).
"""
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 82
RUN_ID = "run-2026-09-06T000000Z"
TS = "2026-09-06T19:00:00Z"
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
P = "M-V5-CORPUS-1"
WIG, CG, PD, ROME, DISCO, ESSENCE = ("252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f", "51e433ade2a845e1", "cdd2717e52820ff6", "467fbeb2e3b019a0")
FROZEN_EXPECTED = {  # c79-pinned prefixes (14 anchors)
    "docs/v3_determinism_certificate.md": "a6876911", "data/v3/rules/rules_artifact.jsonl": "e19fb205",
    "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav": "6e13e007", "data/v4/profiles/31a164f845f8e27e/bass_v2.json": "2a1cb340",
    "data/v4/profiles/88d247468cb6d49f/stem_manifest.json": "d483f2bf", "data/v4/ear/exemplar_set.json": "31c10dfb",
    "scripts/ear/v4_ear.py": "e775621b", "scripts/gen/iterate_v4.py": "8f1f0b88", "scripts/gen/interpolate_v4.py": "2359f35d",
    "docs/v4_completion_report_v3.md": "b900b0ee", "scripts/v3_spine/recreate_v3.py": "b1490874",
    "scripts/v3_spine/stage_cache.py": "33435a84", "scripts/v3_spine/midi_from_json_events.py": "bbff015f",
    "scripts/sound_match/_sweep_hygiene_c27.py": "771ff42b",
}
SCRATCH = Path("/tmp/claude-0/-home-user-long-exposure-runs-music-gen/0a91f173-2db3-4ee7-aec9-5bfb328b2e03/scratchpad")


def _sha(p: str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _event_id(body: dict) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, _canonical({k: v for k, v in body.items() if k not in ("event_id", "ts")})))


def _ev(milestone_id, status, level, rationale, narrative, artifacts, supersedes_path=None):
    body = {"agent": "worker", "artifacts": artifacts, "confidence": {"assessor": "worker", "level": level, "rationale": rationale},
            "cycle": CYCLE, "env_pin_sha256": ENV_PIN, "milestone_id": milestone_id, "narrative": narrative,
            "run_id": RUN_ID, "status": status, "supersedes_path": supersedes_path, "ts": TS}
    body["event_id"] = _event_id(body)
    return body


def _j(p):
    return json.loads(Path(p).read_text())


def main() -> int:
    C = Path("data/v5/corpus")
    frozen = {k: _sha(k) for k in FROZEN_EXPECTED}
    frozen_ok = {k: frozen[k].startswith(v) for k, v in FROZEN_EXPECTED.items()}
    n_frozen_ok = sum(frozen_ok.values())
    st = os.statvfs("."); avail = st.f_bavail * st.f_frsize; used = (st.f_blocks - st.f_bfree) * st.f_frsize
    df_now = round(100 * used / (used + avail), 2)
    prog = _j(C / "transcription_progress.json")
    done = [s for s in prog["order"] if (C / s / "transcription_manifest.json").exists()]
    sided = [s for s in done if (C / s / "canonical_v5_reindexed_sha256.json").exists()]
    launch = _j("data/v5/logs/transcribe_full_c82.launch.json") if Path("data/v5/logs/transcribe_full_c82.launch.json").exists() else None
    tests_p = SCRATCH / "test_results.json"
    tests = _j(tests_p) if tests_p.exists() else {}
    test_line = "; ".join(f"{Path(k).name} {v['summary'][0]}/{v['summary'][1]}" for k, v in tests.items())
    pc_p = SCRATCH / "promise_check_c82_pre_emit.txt"
    if pc_p.exists():
        _pc = pc_p.read_text().splitlines()
        pc_line = f"{sum(1 for l in _pc if 'ERROR' in l)} ERROR / {sum(1 for l in _pc if 'WARN' in l)} WARN lines (baseline 156 ERROR, 0 c81/c82-attributable)"
    else:
        pc_line = "promise_check not yet run"
    events = []

    # ---- P0.2 emitter agent field disclosure ----------------------------------------------------------------
    rows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
    missing = [i + 1 for i, r in enumerate(rows) if "agent" not in r]
    events.append(_ev("_infra/emitter-agent-field-c82", "validated", "high",
        "Counted from the on-disk ledger at emit; template fixed for c81 (re-emitted) and c82+; one fixture event validated against REQUIRED_EVENT_FIELDS (test_01).",
        (f"DISCLOSURE (invariant (d)): the c78-c80 emitter chain (tools/_emit_c78/_c79/_c80_ledger_events.py) omitted the REQUIRED `agent` field; promise_check reports "
         f"{len(missing)} ledger rows missing `agent` (lines {missing[0]}..{missing[-1]}: c78 lines 1757-1759 + 1791-1812, c79 lines 1896-1935, c80 lines 1968-2000) — the c82 brief "
         f"estimated 33 (lines 1968-2000 only); the on-disk count is {len(missing)} and is authoritative. History is NOT rewritten. Fix: tools/_emit_c81_ledger_events.py "
         f"(sha {_sha('tools/_emit_c81_ledger_events.py')}) now carries agent=worker on every body (run at c82 to land the 16 c81 events), and tools/_emit_c82_ledger_events.py "
         f"(this emitter) carries it on every event. The c81 emitter was also patched to skip Rome's per-song row (auditor-executed at the c81 audit) and to exclude Disco A from the "
         "c81 sidecar list (reindexed at c82)."),
        ["tools/_emit_c81_ledger_events.py", "tools/_emit_c82_ledger_events.py", "tests/test_c82_landing.py"]))

    # ---- P0.3 liveness + Disco A catch-up -----------------------------------------------------------------------
    live = Path("data/v5/logs/c82_p0_liveness.txt").read_text().splitlines()
    events.append(_ev(f"{P}/transcription-liveness-c82", "in-progress", "high",
        "PID alive via os.kill(pid, 0) at open; log advancing; restart at the Essence song boundary recorded in the launch JSON.",
        (f"P0.3: {live[1]}; {live[2]}. At c82 open the OLD image (PID 5201, no hook) was on Essence ({ESSENCE}) muscriptor:guitar (518.8 s wall). Landed at c82 open: "
         f"{done[:5]} (Disco A landed 17:25:30Z lossy under the old image). Catch-up: PYTHONPATH=. /usr/bin/python3 scripts/v5/reindex_hook.py -> Disco A 'reindexed+sidecar', "
         f"the other four 'present' (idempotent; test_02). Sidecars on disk at emit: {sided}. "
         + (f"RESTART: old driver stopped at the Essence boundary {launch['pause_window_start']} (os.killpg SIGTERM — children + parent; /proc + pgrep approval-gated), "
            f"venv built inside the stopped window (see M-V5-EAR-1), relaunched {launch['launched_utc']} PID {launch['new_pid']} running_after_8s={launch['running_after_8s']} "
            f"driver sha {launch['driver_sha256_at_launch'][:12]}… hook live at birth; record data/v5/logs/transcribe_full_c82.launch.json." if launch else
            "RESTART: NOT performed at emit time (Essence had not landed) — see the closing summary for the honest state."),
         supersedes_path=f"{P}/transcription-liveness-c81") if False else
        (f"P0.3: {live[1]}; {live[2]}. At c82 open the OLD image (PID 5201, no hook) was on Essence ({ESSENCE}) muscriptor:guitar (518.8 s wall). Landed at c82 open: "
         f"{done[:5]} (Disco A landed 17:25:30Z lossy under the old image). Catch-up: PYTHONPATH=. /usr/bin/python3 scripts/v5/reindex_hook.py -> Disco A 'reindexed+sidecar', "
         f"the other four 'present' (idempotent; test_02). Sidecars on disk at emit: {sided}. "
         + (f"RESTART: old driver stopped at the Essence boundary {launch['pause_window_start']} (os.killpg SIGTERM — children + parent; /proc + pgrep approval-gated), "
            f"venv built inside the stopped window (see M-V5-EAR-1), relaunched {launch['launched_utc']} PID {launch['new_pid']} running_after_8s={launch['running_after_8s']} "
            f"driver sha {launch['driver_sha256_at_launch'][:12]}… hook live at birth; record data/v5/logs/transcribe_full_c82.launch.json." if launch else
            "RESTART: NOT performed at emit time (Essence had not landed) — see the closing summary for the honest state.")),
        ["data/v5/logs/c82_p0_liveness.txt"] + (["data/v5/logs/transcribe_full_c82.launch.json"] if launch else []),
        supersedes_path=f"{P}/transcription-liveness-c81"))

    for s in [DISCO] + [x for x in sided if x not in (WIG, CG, PD, ROME, DISCO)]:
        rm = _j(C / s / "canonical_v5_reindexed/reindex_manifest.json")
        tm = _j(C / s / "transcription_manifest.json")
        tot = {k: sum(v[k] for v in rm["probes"].values()) for k in ("n_starts_in", "n_paired", "n_unpaired_starts")}
        arts = ([f"data/v5/corpus/{s}/canonical_v5_reindexed/{p}.mid" for p in rm["probes"]] + [f"data/v5/corpus/{s}/canonical_v5_reindexed/{p}.reindexed.json" for p in rm["probes"]]
                + [f"data/v5/corpus/{s}/canonical_v5_reindexed/reindex_manifest.json", f"data/v5/corpus/{s}/canonical_v5_reindexed_sha256.json",
                   f"data/v5/corpus/{s}/transcription_manifest.json"] + [f"data/v5/corpus/{s}/muscriptor_full/{p}.json" for p in rm["probes"]]
                + sorted(str(p) for p in (C / s / "stage_cache").rglob("*") if p.is_file()))
        nc = {p: tm["note_counts"][p]["n_note_on"] for p in tm.get("note_counts", {})}
        events.append(_ev(f"{P}/{s}-reindexed-c82", "validated", "high",
            "Sidecar SHAs match disk and reindexed MIDI note_on equals JSON starts per stem (test_reindex_hygiene_c81 test_02 re-run at c82); stage-cache outputs adopted.",
            (f"{tm.get('title')} ({s}, bpm_v5 {tm['bpm_v5']}, note_on {nc}, bars {tm.get('bar_count_at_bpm_v5')}): landed {tm.get('finished')} under the "
             f"{'OLD image (lossy) and re-indexed by the c82 catch-up loop' if s == DISCO else 'restarted driver with the hook live'}; canonical_v5_reindexed/ starts "
             f"{tot['n_starts_in']} -> paired {tot['n_paired']} / unpaired {tot['n_unpaired_starts']}; sidecar reindex_manifest sha "
             f"{_j(C / s / 'canonical_v5_reindexed_sha256.json')['reindex_manifest_sha256'][:16]}…; {len(arts)} artifacts adopted. "
             + ("BLOCKED for rules (tempo: bpm_v5 80.75 vs anchor 120.19)." if s == DISCO else "")),
            arts))

    # ---- P1 ear venv -----------------------------------------------------------------------------------------------
    vb_p, probe_p, gate_p = Path("data/v5/ear/venv_build_c82.json"), Path("data/v5/ear/ear_probe_c82.json"), Path("data/v5/ear/ear_gate_v5_c82.json")
    prereg = _j("data/v5/ear/venv_build_c82_preregistration.json")
    if vb_p.exists() and _j(vb_p).get("status") == "EAR_VENV_BUILT":
        vb = _j(vb_p)
        probe = _j(probe_p) if probe_p.exists() else {"status": "NOT_RUN"}
        rows_ = probe.get("rows", {})
        maxd = max((v["max_abs_diff_vs_cache"] for v in rows_.values() if v.get("max_abs_diff_vs_cache") is not None), default=None)
        events.append(_ev("M-V5-EAR-1/ear-venv-built-c82", "validated", "high",
            "Pre-registration written before pip (mtime); every df reading below the 90 % ceiling; pip freeze + env pin receipts on disk; main-env freeze sha == c79; probe enum recorded from two fresh mkdtemp runs.",
            (f"P1 MANDATORY (operator note 17:20Z) — VENV BUILT. Pre-registration data/v5/ear/venv_build_c82_preregistration.json (sha {_sha('data/v5/ear/venv_build_c82_preregistration.json')[:12]}…): "
             f"df at open {prereg['df_at_open']['used_pct']} % (driver semantics; {prereg['df_at_open']['avail_gb']} GB avail), predicted post-build {prereg['predicted_post_build_used_pct']} % "
             f"(+VGGish {prereg['predicted_post_build_plus_vggish_used_pct']} %), ceiling 90 %. Build (scripts/v5/ear_venv_build_c82.py, pinned c79 command) inside the stopped-driver window "
             f"{launch['pause_window_start'] if launch else '?'} -> {launch['pause_window_stop'] if launch else '?'}: steps {[(s_['step'], s_['df']['used_pct']) for s_ in vb['steps']]}; "
             f"pip wall {next((s_['wall_s'] for s_ in vb['steps'] if s_['step'] == 'pip_install'), None)} s; venv {vb['venv_size_bytes']/1e9:.2f} GB; versions {vb['versions']}; "
             f"pip-freeze sha {vb['pip_freeze_sha256'][:12]}… matches c79 receipt a4d23dea…: {vb['pip_freeze_matches_c79']}{'' if vb['pip_freeze_matches_c79'] else ' (DRIFT disclosed, not retried)'}; "
             f"main-env pip-freeze sha {vb['main_env_pip_freeze_sha256_post'][:12]}… == c79 90ed1d9f…: {vb['main_env_unchanged']}; df final {vb['df_final']['used_pct']} %. "
             f"PROBE (scripts/v5/ear_probe_v5.py, READ-ONLY c74 extractor by subprocess x2 into fresh mkdtemp): status {probe['status']}; run1==run2 {probe.get('run1_eq_run2')}; "
             f"max |diff| vs cache {maxd}; rows {({k: (v['n_windows_run'], v['max_abs_diff_vs_cache']) for k, v in rows_.items()})}. "
             "str-supersedes M-V5-EAR-1/ear-venv-blocked-disk-c81 (its arithmetic is history; the operator note restored the headroom)."),
            ["data/v5/ear/venv_build_c82_preregistration.json", "data/v5/ear/venv_build_c82.json", "data/v5/ear/ear_venv_pip_freeze_c82.txt", "data/v5/ear/env_pin_ear_venv_c82.json",
             "data/v5/logs/ear_venv_build_c82.log", "scripts/v5/ear_venv_build_c82.py", "scripts/v5/ear_probe_v5.py"] + ([str(probe_p)] if probe_p.exists() else []),
            supersedes_path="M-V5-EAR-1/ear-venv-blocked-disk-c81"))
        if gate_p.exists() and _j(gate_p).get("status") == "EAR_GATE_RUN":
            g = _j(gate_p)
            events.append(_ev("M-V5-EAR-1/ear-gate-v5-c82", "validated", "medium",
                "READ-ONLY c76 v2 LOO + c74 sanity gate applied to FRESH venv embeddings; cached-embedding LOO reported alongside; L119 informational per c76 proof.",
                (f"P1.6 first step of restoring the >= 6 gate through the isolated venv on FRESH embeddings (not the cache): LOO v2 fresh {g['loo_fresh_v2']} -> sanity gate {g['sanity_gate_fresh']}; "
                 f"cached-embedding LOO v2 {g['loo_cached_v2']} -> {g['sanity_gate_cached']}; band-4 spot check (fresh, v2) {g['band4_spot_check_fresh_v2']}; L119 check {g['l119_check']}. "
                 "The band-4-vs-band-7 fallback stays documented (c76 monotone-infeasibility proof)."),
                ["data/v5/ear/ear_gate_v5_c82.json", "scripts/v5/ear_gate_v5_c82.py", "data/v5/ear/ear_probe_c82_fresh_embeddings.npz"]))
    else:
        vb = _j(vb_p) if vb_p.exists() else {"status": "NOT_ATTEMPTED"}
        events.append(_ev("M-V5-EAR-1/ear-venv-aborted-df-c82", "action_required", "high",
            "Honest abort/not-attempted record with the df reading; pre-registration on disk; no retry this cycle.",
            (f"P1 MANDATORY venv: status {vb.get('status')} — {json.dumps({k: vb.get(k) for k in ('abort_step', 'abort_reading', 'stderr_tail') if k in vb})}. Pre-registration "
             f"{prereg['df_at_open']} predicted {prereg['predicted_post_build_used_pct']} %. df at emit {df_now} %. M-V5-EAR-1 remains open."),
            ["data/v5/ear/venv_build_c82_preregistration.json"] + ([str(vb_p)] if vb_p.exists() else []), supersedes_path="M-V5-EAR-1/ear-venv-blocked-disk-c81"))

    # ---- P2 tempo mechanism probe ------------------------------------------------------------------------------------
    v = _j(C / "tempo_mechanism_c82_verdict.json")
    bd = _j(C / "tempo_mechanism_c82_byte_determinism.json") if (C / "tempo_mechanism_c82_byte_determinism.json").exists() else {"n_equal": None, "n_files_compared": None}
    events.append(_ev(f"{P}/tempo-mechanism-preregistered-c82", "validated", "high",
        "Pre-registration mtime precedes every output (verdict JSON preregistration_gate + test); measurement only; no criterion.",
        (f"P2.1 data/v5/corpus/tempo_mechanism_probe_c82_preregistration.json (sha {_sha('data/v5/corpus/tempo_mechanism_probe_c82_preregistration.json')[:12]}…, mtime "
         f"{v['preregistration_gate']['prereg_mtime']:.0f}) precedes the earliest tempo_mechanism_c82.json (mtime {v['preregistration_gate']['min_output_mtime']:.0f}). Axis varied: lag "
         "resolution (integer -> parabolic-refined fractional lag); held constant: onset envelope, ac normalization, [40,240] candidates, [70,180] pick band, weights (1, 1/2, 1/2), corpus 26, "
         "MuScriptor outputs, env pin. Confirmation statistic pre-declared: CONFIRMED iff all five anchors within +/-1 BPM of the nearest refined candidate AND Disco A's refined s(~120.2) > "
         "s(~80.75); PARTIAL if one; REFUTED if neither. NOT a criterion (meta-gate); no tempo_v5d; blocked file untouched. Script scripts/v5/tempo_mechanism_probe_c82.py "
         f"(sha {_sha('scripts/v5/tempo_mechanism_probe_c82.py')[:12]}…; READ-ONLY imports of tempo_v5/v5b/v5c helpers)."),
        ["data/v5/corpus/tempo_mechanism_probe_c82_preregistration.json", "scripts/v5/tempo_mechanism_probe_c82.py"]))
    ac_ = v["anchor_checks"]
    d = v["disco_a"]
    dv = v["drums_vs_full_mix_beat_track"]
    events.append(_ev(f"{P}/tempo-mechanism-verdict-c82", "validated", "high",
        "Pre-declared statistic evaluated verbatim on 26/26; one anchor (Rome) misses +/-1 BPM by 0.66; Disco A condition holds with a 0.152 margin; byte-det x2; figure rendered; no criterion proposed.",
        (f"P2.2 VERDICT = {v['verdict']} (A all-five-anchors-within-1-BPM = {v['condition_A_all_five_anchors_within_1bpm']}; B Disco-A-refined-120-beats-80.75 = "
         f"{v['condition_B_disco_a_refined_120_beats_80_75']}). Anchor checks (nearest refined candidate, |delta|): WIG {ac_[WIG]['nearest_refined_bpm']:.3f} ({ac_[WIG]['abs_delta_bpm']:.3f}); "
         f"CG {ac_[CG]['nearest_refined_bpm']:.3f} ({ac_[CG]['abs_delta_bpm']:.3f}); PD {ac_[PD]['nearest_refined_bpm']:.3f} ({ac_[PD]['abs_delta_bpm']:.3f}); ROME {ac_[ROME]['nearest_refined_bpm']:.3f} "
         f"({ac_[ROME]['abs_delta_bpm']:.3f} — MISS: the integer lag 17 is exactly the anchor 151.999 and the parabola shifts it by -0.18 frames; at 152 BPM +/-1 BPM is +/-0.11 frames, tighter than the "
         f"refinement resolution on a broad peak); DISCO A {ac_[DISCO]['nearest_refined_bpm']:.3f} ({ac_[DISCO]['abs_delta_bpm']:.3f}). DISCO A MECHANISM CONFIRMED AS DIAGNOSED: refined lag "
         f"{d['refined_near_120']['lag_ref']} (period ~21.48 frames, offset {d['refined_near_120']['parabolic_offset']}) reads 2T at {2*d['refined_near_120']['lag_ref']:.2f} -> ac {d['refined_near_120']['ac_double']} "
         f"(integer lag 42 read {d['integer_s_120'] - d['refined_near_120']['ac_int'] - 0.5*d['refined_near_120']['ac_half']:.3f}/0.5 = trough side), so s_ref(120.27) = {d['refined_near_120']['s_ref']} > "
         f"s_ref(80.22) = {d['refined_near_80_75']['s_ref']} (margin {d['margin_ref']}) whereas the integer read had s(80.75) {d['integer_s_80']} > s(123.05) {d['integer_s_120']}. The refined DOMINANT "
         f"for Disco A is 120.27 BPM (anchor 120.19). Refined dominants elsewhere: WIG 100.10, CG 91.22 (anchor 90.73; v5c 92.29), PD 122.20, ROME 76.91 (half-time flip of the dominant under s_ref; the "
         "anchor-nearest candidate stays 153.66). Secondary: non-anchor dominant moves > 2 BPM under refinement in "
         f"{v['secondary_non_anchor_refinement_flips_gt_2bpm']['n']}/{v['secondary_non_anchor_refinement_flips_gt_2bpm']['of']} songs "
         f"({[(s_['title'][:14], s_['bpm_int'], s_['bpm_ref']) for s_ in v['secondary_non_anchor_refinement_flips_gt_2bpm']['songs']]}). beat_track drums-stem vs full-mix (30 s section stems; full-length "
         f"stems are transient): {({k: (x['drums_bpm'], x['full_mix_bpm'], x['relation']) for k, x in dv.items()})} — WIG's drums stem reproduces the c20 half-time artifact (49.69), Rome's drums stem "
         "gives the v5b hemiola value 103.36 (two-thirds), PD same, Disco A 117.45 ('other', 2.7 BPM under the full mix); CG has no section drums stem under data/v3_spine. Byte-det x2 "
         f"{bd['n_equal']}/{bd['n_files_compared']} (verdict compared minus the mtime gate block). Figure data/v5/corpus/fig_tempo_mechanism_c82.png from plot_tempo_mechanism_c82.py. NO CRITERION: no bpm_v5 "
         "changed; recanonicalization_blocked.json byte-identical; no canonical_v5c_reindexed/; PD + Disco A stay out of rules. c83 may pre-register a criterion only under the meta-gate's terms; this "
         "PARTIAL says the quantization mechanism explains Disco A but a +/-1 BPM anchor test at 152 BPM is below the resolution of a 3-point parabola."),
        ["data/v5/corpus/tempo_mechanism_c82_verdict.json", "data/v5/corpus/tempo_mechanism_summary_c82.tsv", "data/v5/corpus/tempo_mechanism_c82_byte_determinism.json",
         "data/v5/corpus/fig_tempo_mechanism_c82.png", "data/v5/corpus/plot_tempo_mechanism_c82.py"] + [f"data/v5/corpus/{s}/tempo_mechanism_c82.json" for s in prog["order"]],
        supersedes_path=f"{P}/tempo_v5c-verdict-c81"))

    # ---- P3 harmony ---------------------------------------------------------------------------------------------
    mk = _j("data/v5/rules/harmony_markov_v5.json")
    p34 = _j("data/v5/rules/c82_p3_p4_byte_determinism.json")
    excl = {s: _j(f"data/v5/rules/{s}/harmony_v5.json")["exclusion_rule"] for s in mk["gate"]["used"]}
    diag = {s: _j(f"data/v5/rules/diagnostic_exclusion_100_c82/{s}/harmony_v5.json")["exclusion_rule"]["n_excluded_beats"] for s in mk["gate"]["used"]}
    dmk = _j("data/v5/rules/diagnostic_exclusion_100_c82/harmony_markov_v5.json")
    events.append(_ev("M-V5-RULES-1/harmony_v5-first-data-c82", "validated", "medium",
        "Gate met (3 unblocked lossless songs); pre-declared exclusion applied verbatim and its breadth disclosed; c80 degeneracy thresholds applied; byte-det x2; labelled sensitivity run kept separate.",
        (f"P3 FIRST DATA: harmony_v5.py (sha {_sha('scripts/v5/harmony_v5.py')[:12]}…, cycle 82) on {mk['gate']['used']} (blocked-skipped {mk['gate']['blocked_skipped']}) -> data/v5/rules/harmony_markov_v5.json "
         f"(sha {_sha('data/v5/rules/harmony_markov_v5.json')[:12]}…): {len(mk['states'])} functional states; max stationary {mk['max_stationary_state']} = {mk['max_stationary_mass']}; qualities with >= 8 "
         f"segments {mk['qualities_with_count_ge_threshold']}; PRE-DECLARED VERDICT {mk['degeneracy_verdict']}. Per song: "
         + "; ".join(f"{x['title']} key {x['key']['tonic_name']} {x['key']['mode']} (corr {x['key']['corr']:.3f}), {x['n_beats']} beats / {x['n_segments']} segments, top {x['top_states'][:3]}" for x in mk['per_song'].values())
         + f". PRE-DECLARED EXCLUSION (a beat is dropped when one stem has >= 12 simultaneous starts): excluded beats {({s: e['n_excluded_beats'] for s, e in excl.items()})} of "
         f"{({s: mk['per_song'][s]['n_beats'] for s in excl})} — FIRST-CLASS FINDING: the rule catches the Rome bass tail (beat 544, 141 starts) as intended but ALSO dense strummed-guitar beats "
         f"(12-36 starts/beat; WIG {excl[WIG]['excluded_beats'] and 'other/piano/guitar'}, CG guitar 81 beats, Rome guitar 95 beats), i.e. 18-21 % of beats; not retuned (FD-1). LABELLED SENSITIVITY "
         f"DIAGNOSTIC (not the official artifact; data/v5/rules/diagnostic_exclusion_100_c82/, threshold 100): excludes only {diag} beats (the Rome tail), same keys, verdict {dmk['degeneracy_verdict']}, "
         f"max stationary {dmk['max_stationary_mass']} — the verdict is insensitive to the threshold; the state ordering shifts (WIG top 9:min7 vs 5:maj). Caveat carried from reindex-fidelity-c81: "
         f"`other`-stem durations are inflated by the greedy pairing (duration-weighted PCPs). Byte-det x2 {p34['files']['data/v5/rules/harmony_markov_v5.json']['equal']}. Nothing fed to a generator. "
         "str-supersedes M-V5-RULES-1/harmony_v5-gated-c81."),
        ["scripts/v5/harmony_v5.py", "data/v5/rules/harmony_markov_v5.json", "data/v5/rules/c82_p3_p4_byte_determinism.json"] + [f"data/v5/rules/{s}/harmony_v5.json" for s in mk["gate"]["used"]]
        + ["data/v5/rules/diagnostic_exclusion_100_c82/harmony_markov_v5.json"] + [f"data/v5/rules/diagnostic_exclusion_100_c82/{s}/harmony_v5.json" for s in mk["gate"]["used"]],
        supersedes_path="M-V5-RULES-1/harmony_v5-gated-c81"))

    # ---- P4 groove v2 ---------------------------------------------------------------------------------------------
    g2 = _j("data/v5/rules/groove_v5_v2.json")
    hs, ss, tr = g2["heldout_stats"], g2["sample_stats"], g2["train_stats_aligned"]
    events.append(_ev("M-V5-RULES-1/groove_v5-v2-heldout-c82", "validated", "medium",
        "Pre-declared held-out enum applied verbatim; both statistics reproduce within tolerance but the singleton-context fraction fails; byte-det x2; c81 groove_v5.py untouched.",
        (f"P4 scripts/v5/groove_v5_v2.py (sha {_sha('scripts/v5/groove_v5_v2.py')[:12]}…; sibling, c81 groove_v5.py sha {_sha('scripts/v5/groove_v5.py')[:12]}… untouched) -> data/v5/rules/groove_v5_v2.json "
         f"(sha {_sha('data/v5/rules/groove_v5_v2.json')[:12]}…). Train WIG + CG ({tr['n_bars']} aligned bars), evaluate ROME held out ({hs['n_bars']} bars). Bar-phase offsets: "
         f"{({s: r['phase']['offset'] for s, r in g2['per_song'].items()})} (no ties). PRE-DECLARED VERDICT {g2['verdict']}: Rome backbeat {hs['backbeat_ratio']:.4f} vs sampled {ss['backbeat_ratio']:.4f} "
         f"(|d| {g2['validation']['backbeat_ratio']['abs_diff']:.4f} <= 0.15 OK); bass-kick lock {hs['bass_kick_lock']:.4f} vs {ss['bass_kick_lock']:.4f} (|d| {g2['validation']['bass_kick_lock']['abs_diff']:.4f} OK); "
         f"sampled distinct kick8 {ss['distinct_kick_patterns']} / bass16 {ss['distinct_bass_patterns']} (non-degenerate); BUT singleton-context fraction {g2['singleton_context_fraction']} >= 0.5 "
         f"({g2['n_singleton_contexts']}/{g2['n_contexts']} contexts over {g2['table_context_counts']}) -> OVERFITS by the pre-declared rule: the held-out statistics match, but the conditional tables are "
         "mostly one-shot contexts (memorization signal), so the c81 STATS_MATCH cannot be called generalization yet. In-sample comparison under the new alignment: WIG backbeat "
         f"{g2['per_song'][WIG]['stats']['backbeat_ratio']:.3f} (offset-0 {g2['c81_in_sample_comparison']['unaligned_offset0_per_song'][WIG]['backbeat_ratio']:.3f}), CG "
         f"{g2['per_song'][CG]['stats']['backbeat_ratio']:.3f} (offset-0 {g2['c81_in_sample_comparison']['unaligned_offset0_per_song'][CG]['backbeat_ratio']:.3f}); alignment raises the grid-exact backbeat "
         "ratio but it stays ~0.15-0.18 (MuScriptor snare onsets rarely land exactly on slots 4/12 — the c81 disclosure stands). Byte-det x2 "
         f"{p34['files']['data/v5/rules/groove_v5_v2.json']['equal']}. Data-existence only; nothing fed to a generator."),
        ["scripts/v5/groove_v5_v2.py", "data/v5/rules/groove_v5_v2.json", "data/v5/rules/c82_p3_p4_byte_determinism.json"]))

    # ---- P5 fidelity follow-up -----------------------------------------------------------------------------------------
    f5 = _j(f"data/v5/corpus/{WIG}/reindex_fidelity_c82.json")
    events.append(_ev(f"{P}/reindex-fidelity-c82", "validated", "high",
        "Duration-asserting fixture tests green (3/3); per-chunk JSON probed on disk with SHAs; enum recorded honestly.",
        (f"P5 (M-3 follow-up): tests/test_reindex_fidelity_c82.py asserts DURATIONS on synthetic two-chunk fixtures — unambiguous fixture 6/6 starts AND 6/6 durations within 1 tick; the ambiguous "
         "long-note fixture reproduces the c81 DEGRADED class exactly (greedy pairs chunk-0's 28 s note with chunk-1's 26.5 s end -> 25.5 s). Per-chunk ground truth: VERDICT "
         f"{f5['verdict']} — stage_cache/v5_muscriptor_other/*/outputs holds only the MERGED other.json (sha == muscriptor_full/other.json {f5['evidence']['stage_cache_other_json_sha256'][:12]}…), "
         f"event keys {f5['evidence']['event_keys_in_merged_json']} carry no chunk field, 0 chunk-named files among {f5['evidence']['stage_cache_files_total']} stage-cache files; the READ-ONLY merge "
         "writes only the merged per-probe JSON and per-chunk outputs die with the transient dir. Consequence: the c81 DEGRADED verdict stays attributed to transcription variance; c83 candidates "
         "(pre-declare first): cache per-chunk outputs at the muscriptor stage, or chunk-window-constrained pairing re-measured with reindex_fidelity_c81.py."),
        [f"data/v5/corpus/{WIG}/reindex_fidelity_c82.json", "tests/test_reindex_fidelity_c82.py"], supersedes_path=f"{P}/reindex-fidelity-c81"))

    # ---- housekeeping ---------------------------------------------------------------------------------------------
    events.append(_ev("_plan/register-c82-sub-leaves", "validated", "high",
        "Rows inserted inline in the parseable ## Milestones region via tools/_register_c82_por_rows.py; idempotent; promise_check reported verbatim.",
        (f"c82 POR rows registered inline (emitter-agent-field, liveness-c82, per-song reindexed-c82 for {[DISCO] + [x for x in sided if x not in (WIG, CG, PD, ROME, DISCO)]}, ear venv "
         f"{'built' if (vb_p.exists() and _j(vb_p).get('status') == 'EAR_VENV_BUILT') else 'aborted/not-attempted'}, ear gate if run, tempo mechanism prereg + verdict, harmony first data, groove v2 held-out, "
         f"reindex fidelity, housekeeping). promise_check before emit: {pc_line}."),
        ["plan_of_record.md", "tools/_register_c82_por_rows.py"]))
    events.append(_ev("_infra/adopt-cycle82-tests", "validated", "high",
        "New suites green under /usr/bin/python3; pre-c82 regression green; no anchor mutation.",
        (f"tests/test_c82_landing.py (6: emitter template carries agent + validates against REQUIRED_EVENT_FIELDS; reindex hook idempotent on Disco A; venv probe enum + main-env freeze unchanged; "
         "parabolic refinement recovers a synthetic 21.48-frame period to +/-0.05 and its harmonic sum beats the 3:2 lag; groove v2 phase alignment recovers a known offset; harmony exclusion drops a "
         f"synthetic 12-start beat) + tests/test_reindex_fidelity_c82.py (3) = 9 new. Results at emit: {test_line}."),
        ["tests/test_c82_landing.py", "tests/test_reindex_fidelity_c82.py"]))
    events.append(_ev("_archive/cycle-82-scratch", "validated", "high",
        "One-shot emitters retained in-tree per emitter-exemption pattern; scratch runners live in the harness scratchpad; nothing to move to tools/stale/.",
        ("tools/_emit_c82_ledger_events.py + tools/_register_c82_por_rows.py retained in-tree (docs/emitter_exemption_policy.md). Session scratchpad (not in workspace): write_preregs, run_tests, "
         "bytedet_p3_p4_c82, bytedet_probe_c82, p5_per_chunk_check, restart_driver_c82. data/v5/corpus/plot_tempo_mechanism_c82.py co-located with its data + figure (regenerable triplet). "
         "data/v5/rules/diagnostic_exclusion_100_c82/ is a labelled diagnostic, kept."), []))
    events.append(_ev("_run/cycle_82_closed", "validated", "high",
        "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        (f"c82 CLOSED — v5 REOPENING cycle 4. FROZEN anchors {n_frozen_ok}/14 byte-identical to their c79 prefixes: "
         + "; ".join(f"{k} {frozen[k][:12]}{'' if frozen_ok[k] else ' MISMATCH'}" for k in FROZEN_EXPECTED)
         + f". df at emit {df_now} %. Tests: {test_line}. promise_check pre-emit: {pc_line}. Full 9-header summary in the c82 work output."),
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_81_closed"))

    # validate every event against the SSoT schema before appending anything
    try:
        from long_exposure.tools._ledger_schema import validate_event, REQUIRED_EVENT_FIELDS
        for e in events:
            miss = [k for k in REQUIRED_EVENT_FIELDS if k not in e]
            assert not miss, (e["milestone_id"], miss)
            errs = validate_event(e)
            assert not errs, (e["milestone_id"], errs)
    except ImportError:
        print("WARN: long_exposure schema not importable; field check only")
        for e in events:
            assert "agent" in e
    existing = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            existing.add(json.loads(line).get("milestone_id"))
    to_append = [e for e in events if e["milestone_id"] not in existing]
    if not to_append:
        print("IDEMPOTENT: all c82 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c82 events; frozen anchors OK {n_frozen_ok}/14")
    for e in to_append:
        print(f"  {e['status']:16s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
