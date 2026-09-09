#!/usr/bin/python3
"""c82 one-shot POR registration: insert c82 sub-leaf rows inline in the `## Milestones` parseable region
(before `## Sub-milestones`). Idempotent. Retained in-tree per c14+ emitter-exemption pattern."""
import json, os, sys
from pathlib import Path
os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")
P = "M-V5-CORPUS-1"
C = Path("data/v5/corpus")
WIG, CG, PD, ROME, DISCO = ("252eb21ce7df7328", "31a164f845f8e27e", "88d247468cb6d49f", "51e433ade2a845e1", "cdd2717e52820ff6")


def j(p):
    return json.loads(Path(p).read_text())


def main() -> int:
    v = j(C / "tempo_mechanism_c82_verdict.json")
    mk = j("data/v5/rules/harmony_markov_v5.json")
    g2 = j("data/v5/rules/groove_v5_v2.json")
    f5 = j(C / WIG / "reindex_fidelity_c82.json")
    vb_p = Path("data/v5/ear/venv_build_c82.json")
    vb = j(vb_p) if vb_p.exists() else {"status": "NOT_ATTEMPTED"}
    probe_p = Path("data/v5/ear/ear_probe_c82.json")
    probe = j(probe_p) if probe_p.exists() else {"status": "NOT_RUN"}
    amend_p, probe2_p = Path("data/v5/ear/venv_amend_c82.json"), Path("data/v5/ear/ear_probe_c82_amended.json")
    amend = j(amend_p) if amend_p.exists() else None
    probe2 = j(probe2_p) if probe2_p.exists() else None
    gate_p = Path("data/v5/ear/ear_gate_v5_c82.json")
    launch_p = Path("data/v5/logs/transcribe_full_c82.launch.json")
    launch = j(launch_p) if launch_p.exists() else None
    ac = v["anchor_checks"]
    rows = [
     ("_infra/emitter-agent-field-c82", "G1", "c82 P0.2 DISCLOSURE: the c78-c80 emitter chain omitted the REQUIRED `agent` field — 98 ledger rows (c78 lines 1757-1759 + 1791-1812, c79 1896-1935, c80 1968-2000; the brief estimated 33) fail promise_check; history NOT rewritten. Template fixed: the c81 emitter (re-run at c82 with `agent=worker`, Rome per-song row skipped, Disco A excluded from the c81 sidecar list) and `tools/_emit_c82_ledger_events.py` carry `agent` on every event; one fixture event validated against `REQUIRED_EVENT_FIELDS` (test_01).", "Every c81/c82 event carries agent; fixture validates.", "—"),
     (f"{P}/transcription-liveness-c82", "G4", "c82 P0.3/P0.4: PID 5201 (old image, no hook) verified ALIVE at open on Essence; Disco A (landed 17:25Z lossy) re-indexed + sidecar by the catch-up loop (idempotent on re-run); " + (f"Essence (18:13Z) + Desire (18:58Z) also landed lossy under the old image and were caught up by the same idempotent hook run at 19:44Z; old driver stopped at the {launch['song_boundary']} boundary ({launch['pause_window_start']} -> {launch['pause_window_stop']}, os.killpg SIGTERM), venv built inside the window, relaunched via READ-ONLY `launch_detached` with the pinned c79 command: new PID {launch['new_pid']}, hook live at birth; `data/v5/logs/transcribe_full_c82.launch.json`." if launch else "driver restart NOT performed at registration time (Essence had not landed)."), "Liveness file; catch-up idempotent; launch JSON with old/new PIDs + pause window.", f"{P}/transcription-liveness-c81"),
     (f"{P}/{DISCO}-reindexed-c82", "G4", "c82 per-song lossless record: Disco A (cdd2717e52820ff6) landed 17:25:30Z under the OLD image (lossy `canonical_midi_full/` only); c82 catch-up `reindex_hook.reindex_landed()` -> `canonical_v5_reindexed/` + sidecar; MIDI note_on == JSON starts per probe (test_02 re-run). BLOCKED for rules (bpm_v5 80.75 vs anchor 120.19).", "Sidecar SHAs match disk; note_on == starts.", f"{P}/reindex-hygiene-c81"),
    ]
    if vb.get("status") == "EAR_VENV_BUILT":
        rows.append(("M-V5-EAR-1/ear-venv-built-c82", "G3", f"c82 P1 MANDATORY (operator note 2026-09-06 17:20Z) — isolated ear venv BUILT at `workspace/ear_venv` inside the stopped-driver window: pre-registration `data/v5/ear/venv_build_c82_preregistration.json` written BEFORE pip (df at open {j('data/v5/ear/venv_build_c82_preregistration.json')['df_at_open']['used_pct']} %, predicted post-build {j('data/v5/ear/venv_build_c82_preregistration.json')['predicted_post_build_used_pct']} %); steps {[(s['step'], s['df']['used_pct']) for s in vb['steps']]} (all < 90 %); versions {vb['versions']}; pip-freeze sha matches c79 receipt: {vb['pip_freeze_matches_c79']}; main-env freeze unchanged: {vb['main_env_unchanged']}. First probe `scripts/v5/ear_probe_v5.py` x2 fresh mkdtemp under the pinned-command venv: **{probe['status']}** (READ-ONLY c74 extractor imports librosa; the c79-pinned command omits it — receipt bug, record kept byte-identical). DISCLOSED AMENDMENT `scripts/v5/ear_venv_amend_c82.py` -> `venv_amend_c82.json`: {(amend['status'] + ', +' + str(len(amend['added_packages'])) + ' packages (librosa 0.11.0 + deps), freeze sha ' + amend['pip_freeze_sha256_pre'][:12] + '… -> ' + amend['pip_freeze_sha256_post'][:12] + '…, df ' + str(amend['df_pre']['used_pct']) + ' -> ' + str(amend['df_final']['used_pct']) + ' %, main env unchanged ' + str(amend['main_env_unchanged'])) if amend else 'NOT on disk'}. Probe under the amended venv (`ear_probe_c82_amended.json`): **{probe2['status'] if probe2 else 'NOT_RUN'}** (run1==run2 {probe2.get('run1_eq_run2') if probe2 else None}). Receipts: `ear_venv_pip_freeze_c82.txt`, `env_pin_ear_venv_c82.json`. str-supersedes `ear-venv-blocked-disk-c81`.", "Prereg before pip; df < 90 % at every step; probe enum recorded; main env unchanged.", "M-V5-EAR-1/ear-venv-blocked-disk-c81"))
        if gate_p.exists() and j(gate_p).get("status") == "EAR_GATE_RUN":
            g = j(gate_p)
            rows.append(("M-V5-EAR-1/ear-gate-v5-c82", "G3", f"c82 P1.6: c76 v2 wider-linear LOO sanity gate through the venv subprocess on FRESH embeddings (not the cache): LOO {g['loo_fresh_v2']} -> gate_passes {g['sanity_gate_fresh']['gate_passes']}; cached-embedding LOO {g['loo_cached_v2']}; band-4 spot check {g['band4_spot_check_fresh_v2']}; L119 informational ({g['l119_check']['passes']}) per the c76 infeasibility proof. First step of restoring the >= 6 gate; band-4-vs-band-7 fallback stays documented.", "Gate record on disk from READ-ONLY c74/c76 code on fresh embeddings.", "M-V5-EAR-1/ear-venv-built-c82"))
    else:
        rows.append(("M-V5-EAR-1/ear-venv-aborted-df-c82", "G3", f"c82 P1 MANDATORY venv: honest record — status {vb.get('status')} ({({k: vb.get(k) for k in ('abort_step', 'abort_reading') if k in vb})}); pre-registration on disk; no retry this cycle.", "Abort record with df reading.", "M-V5-EAR-1/ear-venv-blocked-disk-c81"))
    rows += [
     (f"{P}/tempo-mechanism-preregistered-c82", "G4", "c82 P2.1: `data/v5/corpus/tempo_mechanism_probe_c82_preregistration.json` written BEFORE any output (mtime gate in the verdict JSON). MEASUREMENT of the integer-lag quantization mechanism, NOT a criterion (meta-gate after v5/v5b/v5c): every local maximum in [40,240] BPM refined by a 3-point parabola; s_ref = ac(T)+½ac(T/2)+½ac(2T) at the refined lags; dominant refined candidate over [70,180]; beat_track drums-stem vs full-mix. Pre-declared enum CONFIRMED / PARTIAL / REFUTED (A: all five anchors within ±1 BPM of the nearest refined candidate; B: Disco A s_ref(~120.2) > s_ref(~80.75)). No bpm_v5 changes on any outcome; no tempo_v5d.", "Prereg mtime precedes every output; 26/26; byte-det x2.", f"{P}/tempo_v5c-verdict-c81"),
     (f"{P}/tempo-mechanism-verdict-c82", "G4", f"c82 P2.2 VERDICT = **{v['verdict']}** (A={v['condition_A_all_five_anchors_within_1bpm']}, B={v['condition_B_disco_a_refined_120_beats_80_75']}). Nearest refined candidate vs anchor: WIG {ac[WIG]['nearest_refined_bpm']:.2f} (Δ {ac[WIG]['abs_delta_bpm']:.2f}), CG {ac[CG]['nearest_refined_bpm']:.2f} (Δ {ac[CG]['abs_delta_bpm']:.2f}), PD {ac[PD]['nearest_refined_bpm']:.2f} (Δ {ac[PD]['abs_delta_bpm']:.2f}), **Rome {ac[ROME]['nearest_refined_bpm']:.2f} (Δ {ac[ROME]['abs_delta_bpm']:.2f} — MISS; ±1 BPM at 152 BPM is ±0.11 frames, below 3-point-parabola resolution on a broad peak)**, Disco A {ac[DISCO]['nearest_refined_bpm']:.2f} (Δ {ac[DISCO]['abs_delta_bpm']:.2f}). **Disco A mechanism confirmed as diagnosed**: refined lag 21.48 reads 2T at 42.97 (ac 0.715 vs 0.466 at integer 42), s_ref(120.27)={v['disco_a']['refined_near_120']['s_ref']} > s_ref(80.22)={v['disco_a']['refined_near_80_75']['s_ref']} (margin {v['disco_a']['margin_ref']}); the refined dominant for Disco A is 120.27. Secondary: {v['secondary_non_anchor_refinement_flips_gt_2bpm']['n']}/21 non-anchor dominants move > 2 BPM. Drums-stem beat_track: WIG 49.69 (half; c20 artifact), Rome 103.36 (two-thirds = the v5b hemiola value), PD same, Disco A 117.45. Byte-det x2 28/28. Figure `fig_tempo_mechanism_c82.png`. No criterion; blocked file untouched; PD + Disco A stay out of rules.", "Verdict ∈ enum; anchor table verbatim; no retune; no criterion.", f"{P}/tempo-mechanism-preregistered-c82"),
     ("M-V5-RULES-1/harmony_v5-first-data-c82", "G4", f"c82 P3 FIRST DATA: `harmony_v5.py` (cycle 82; pre-declared input-artifact exclusion: a beat is dropped when one stem has ≥ 12 simultaneous starts) on {mk['gate']['used']} -> `harmony_markov_v5.json`: {len(mk['states'])} functional states; max stationary {mk['max_stationary_state']} = {mk['max_stationary_mass']}; qualities ≥ 8 segments {mk['qualities_with_count_ge_threshold']}; c80 pre-declared verdict **{mk['degeneracy_verdict']}**. Keys: " + "; ".join(f"{x['title']} {x['key']['tonic_name']} {x['key']['mode']}" for x in mk['per_song'].values()) + f". FIRST-CLASS FINDING: the exclusion catches the Rome bass tail (beat 544, 141 starts) but also dense strummed-guitar beats (12-36 starts/beat) — excluded beats {({s: j(f'data/v5/rules/{s}/harmony_v5.json')['exclusion_rule']['n_excluded_beats'] for s in mk['gate']['used']})} of {({s: mk['per_song'][s]['n_beats'] for s in mk['gate']['used']})}; not retuned (FD-1); labelled sensitivity diagnostic (threshold 100, `data/v5/rules/diagnostic_exclusion_100_c82/`) excludes only the Rome tail with the same keys and verdict. Byte-det x2. Nothing fed to a generator.", "Chain on ≥ 3 lossless songs; exclusion counts disclosed; byte-det x2.", "M-V5-RULES-1/harmony_v5-gated-c81"),
     ("M-V5-RULES-1/groove_v5-v2-heldout-c82", "G4", f"c82 P4: `scripts/v5/groove_v5_v2.py` (sibling; c81 `groove_v5.py` untouched): bar-phase alignment (offsets {({s: r['phase']['offset'] for s, r in g2['per_song'].items()})}), 8th-note kick alphabet, α = 0.5 additive smoothing; train WIG + CG, evaluate ROME held out. Pre-declared verdict **{g2['verdict']}**: Rome backbeat {g2['heldout_stats']['backbeat_ratio']:.3f} vs sampled {g2['sample_stats']['backbeat_ratio']:.3f} (Δ {g2['validation']['backbeat_ratio']['abs_diff']:.3f} ≤ 0.15), lock {g2['heldout_stats']['bass_kick_lock']:.3f} vs {g2['sample_stats']['bass_kick_lock']:.3f} (Δ {g2['validation']['bass_kick_lock']['abs_diff']:.3f}), distinct kick8 {g2['sample_stats']['distinct_kick_patterns']} / bass16 {g2['sample_stats']['distinct_bass_patterns']}, BUT singleton-context fraction {g2['singleton_context_fraction']} ≥ 0.5 -> OVERFITS: held-out statistics reproduce, yet the conditional tables are mostly one-shot contexts (memorization signal). Byte-det x2. Nothing fed to a generator.", "Held-out verdict from the enum; byte-det x2; c81 script untouched.", "M-V5-RULES-1/groove_v5-first-data-c81"),
     (f"{P}/reindex-fidelity-c82", "G4", f"c82 P5 (M-3 follow-up): `tests/test_reindex_fidelity_c82.py` asserts DURATIONS on synthetic two-chunk fixtures (unambiguous 6/6 within 1 tick; ambiguous long-note fixture reproduces the c81 DEGRADED greedy class). Per-chunk ground truth: **{f5['verdict']}** — stage_cache holds only the merged `other.json` (sha == muscriptor_full), no chunk field, 0 chunk-named files; per-chunk outputs die with the transient dir. The c81 DEGRADED verdict stays attributed to transcription variance; c83 candidates: cache per-chunk outputs at the muscriptor stage, or pre-declared chunk-window-constrained pairing.", "Fixture asserts durations; per-chunk enum recorded.", f"{P}/reindex-fidelity-c81"),
     ("_plan/register-c82-sub-leaves", "G1", f"c82 POR registration row: c82 sub-leaves inserted inline in the `## Milestones` parseable region via `tools/_register_c82_por_rows.py` (idempotent). M-V5-CORPUS-1: {len(list(C.glob('*/canonical_v5_reindexed_sha256.json')))} of 26 landed at registration ({sorted(p.parent.name for p in C.glob('*/canonical_v5_reindexed_sha256.json'))}), all lossless + sidecar; driver restarted with the hook live; M-V5-EAR-1: venv per row above; M-V5-RULES-1: harmony first data on 3 songs (NON_DEGENERATE with disclosed exclusion breadth), groove v2 held-out OVERFITS; tempo meta-gate: mechanism PARTIAL, no criterion; PD + Disco A remain blocked.", "Rows added.", "—"),
     ("_infra/adopt-cycle82-tests", "G1", "c82 test-adoption: `tests/test_c82_landing.py` (6: emitter agent field + schema validation; reindex hook idempotent on Disco A; venv probe enum + main-env freeze; parabolic refinement recovers a 21.48-frame synthetic period ±0.05 and beats the 3:2 lag; groove v2 phase alignment recovers a known offset; harmony exclusion drops a synthetic 12-start beat) + `tests/test_reindex_fidelity_c82.py` (3) = 9 new; c81 `test_ear_venv_c81.py` test_03 additively reads the newest probe record when the venv exists. Regression 68/68 pre-c82 -> 77 cross-cycle.", "9/9 new + regression green.", "—"),
     ("_archive/cycle-82-scratch", "G1", "c82 scratch archival: `tools/_emit_c82_ledger_events.py` + `tools/_register_c82_por_rows.py` retained in-tree per emitter-exemption pattern; session scratchpad runners (write_preregs, run_tests, bytedet_p3_p4_c82, bytedet_probe_c82, p5_per_chunk_check, restart_driver_c82) not in workspace; `data/v5/corpus/plot_tempo_mechanism_c82.py` co-located with its data + figure; `data/v5/rules/diagnostic_exclusion_100_c82/` is a labelled diagnostic.", "No workspace scratch to archive.", "—"),
     ("_run/cycle_82_closed", "G1", "c82 CLOSED — v5 REOPENING cycle 4. See ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    PROV = {"467fbeb2e3b019a0": "landed 18:13Z lossy under the OLD image; re-indexed by the c82 idempotent catch-up hook run (19:44Z)",
            "2b0370d9d0162c98": "landed 18:58Z lossy under the OLD image; re-indexed by the c82 idempotent catch-up hook run (19:44Z)",
            "a9587ccde1b333f5": "manifest written 19:58:30Z by the OLD image (the restart boundary); the restarted driver re-walked it from stage_cache and its live hook wrote the sidecar at 19:59:33Z (no separate catch-up)"}
    for side_p in sorted(C.glob("*/canonical_v5_reindexed_sha256.json")):
        s = side_p.parent.name
        if s in (WIG, CG, PD, ROME, DISCO):
            continue
        rm = j(C / s / "canonical_v5_reindexed/reindex_manifest.json")
        tm = j(C / s / "transcription_manifest.json")
        tot = {k: sum(x[k] for x in rm["probes"].values()) for k in ("n_starts_in", "n_paired", "n_unpaired_starts")}
        rows.append((f"{P}/{s}-reindexed-c82", "G4", f"c82 per-song lossless record: {tm.get('title')} ({s}, bpm_v5 {tm['bpm_v5']}): {PROV.get(s, 'landed under the restarted driver with the reindex hook live at birth (no catch-up run)')}; `canonical_v5_reindexed/` starts {tot['n_starts_in']} -> paired {tot['n_paired']} / unpaired {tot['n_unpaired_starts']}; sidecar `canonical_v5_reindexed_sha256.json`; stage-cache manifests + reindexed MIDI/JSON adopted.", "Sidecar SHAs match disk; MIDI note_on == JSON starts.", f"{P}/transcription-liveness-c82"))
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c82 POR rows present"); return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
