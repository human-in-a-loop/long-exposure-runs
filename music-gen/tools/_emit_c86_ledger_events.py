#!/usr/bin/python3
"""c86 one-shot ledger emitter — v5 REOPENING cycle 8 (F2 bass + melody + dynamics as iteration 3; F4 CLOSE per operator addendum;
P0 cheap fixes; guidance adoption; bookkeeping).

created: 2026-09-10T00:20:00Z
cycle: 86
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _archive/cycle-86-scratch

Every event carries `agent` (REQUIRED_EVENT_FIELDS); UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts);
idempotent by milestone_id; supersedes_path is str|None (c14 lemma). Status convention (L2): `validated` for a RECORDED
pre-registered verdict (PARTIAL / MEMORIZES / OVERFITS are recorded outcomes, not tuned away); `in-progress` for iteration-03
(no passer). Reads every number from disk at emit time. Retained in-tree per docs/emitter_exemption_policy.md.
"""
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 86
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
G_F2 = "docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt"
G_BL = "docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt"
FROZEN_EXPECTED = {
    "docs/v3_determinism_certificate.md": "a6876911", "data/v3/rules/rules_artifact.jsonl": "e19fb205",
    "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav": "6e13e007", "data/v4/profiles/31a164f845f8e27e/bass_v2.json": "2a1cb340",
    "data/v4/profiles/88d247468cb6d49f/stem_manifest.json": "d483f2bf", "data/v4/ear/exemplar_set.json": "31c10dfb",
    "scripts/ear/v4_ear.py": "e775621b", "scripts/gen/iterate_v4.py": "8f1f0b88", "scripts/gen/interpolate_v4.py": "2359f35d",
    "docs/v4_completion_report_v3.md": "b900b0ee", "scripts/v3_spine/recreate_v3.py": "b1490874",
    "scripts/v3_spine/stage_cache.py": "33435a84", "scripts/v3_spine/midi_from_json_events.py": "bbff015f",
    "scripts/sound_match/_sweep_hygiene_c27.py": "771ff42b", "data/v5/corpus/corpus_manifest.json": "73362136",
    "data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json": "2fbabc07", "data/v5/corpus/content_blocked.json": "fc07a138",
    "data/v5/rules/harmony_markov_v5_full.json": "a984ee17", "data/v5/rules/groove_v5_v2_full.json": "faa0e76e",
    "data/v5/rules/harmony_markov_v5.json": "9785a907", "data/v5/rules/harmony_prereg_c84.json": "db71346b", "data/v5/rules/groove_prereg_c84.json": "b5cb6f39",
    "data/v5/rules/form_plan_v5.json": "d6c14f9a", "data/v5/rules/eligible_c84.json": "e62c6ef3", "data/v4/gen/donor_profile_map.json": "8c0b54cd",
    "data/v5/gen/iteration_02/gen_v5_song_1_donor_31a164f845f8e27e/ab_mix.wav": "240b893a", "data/v5/gen/iteration_02/gen_v5_song_2_donor_252eb21ce7df7328/ab_mix.wav": "9b1812c0",
    "data/v5/gen/iteration_02/gen_v5_song_3_donor_51e433ade2a845e1/ab_mix.wav": "ac01eb92", "data/v5/gen/iteration_02/gen_v5_song_4_donor_88d247468cb6d49f/ab_mix.wav": "940227fb",
    "data/v5/gen/iteration_02/gen_v5_song_5_donor_cdd2717e52820ff6/ab_mix.wav": "330916d5",
}
SCRATCH = Path("/tmp/claude-0/-home-user-long-exposure-runs-music-gen/91e08ad5-010d-493f-8731-a2fb2b572632/scratchpad")
FOCUS = ["252eb21ce7df7328", "31a164f845f8e27e", "51e433ade2a845e1", "88d247468cb6d49f", "cdd2717e52820ff6"]
NAMES = {"252eb21ce7df7328": "WIG", "31a164f845f8e27e": "CG", "51e433ade2a845e1": "Rome", "88d247468cb6d49f": "PD", "cdd2717e52820ff6": "Disco A"}


def _sha(p) -> str:
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


def _df():
    st = os.statvfs(".")
    avail = st.f_bavail * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return round(100 * used / (used + avail), 2), round(avail / 1e9, 3)


def main() -> int:
    frozen = {k: _sha(k) for k in FROZEN_EXPECTED}
    frozen_ok = {k: frozen[k].startswith(v) for k, v in FROZEN_EXPECTED.items()}
    n_frozen_ok = sum(frozen_ok.values())
    df_now, avail_now = _df()
    gate = _j("data/v5/gen/f2_route_gate_c86.json")
    prof = _j("data/v5/rules/velocity_profiles_v5.json")
    bass = _j("data/v5/rules/bass_pitch_v5.json")
    vomm = _j("data/v5/rules/melody_vomm_v5.json")
    bd_models = _j("data/v5/rules/byte_determinism_c86_f2models.json")["entries"]
    bd_gen = _j("data/v5/gen/byte_determinism_c86.json")["entries"]
    bd_f4 = _j("data/v5/rules/byte_determinism_c86_f4.json")
    bd_corpus = _j("data/v5/corpus/byte_determinism_c86.json")
    roll = _j("data/v5/gen/iteration_03/iteration_rollup.json")
    stall = _j("data/v5/gen/stall_counter.json")
    sc = _j("data/v5/gen/gen_v5_iter03_ear_scores_c86.json")
    lm = _j("data/v4/generated/v5_iter_03/listening_manifest.json")
    res = _j("data/v5/corpus/tempo_f4_operator_resolution_c86.json")
    h23 = _j("data/v5/rules/harmony_markov_v5_full_c86.json")
    g23 = _j("data/v5/rules/groove_v5_v2_full_c86.json")
    diff = _j("data/v5/rules/harmony_n23_vs_n21_diff_c86.json")
    elig = _j("data/v5/rules/eligible_c86.json")
    tests = _j(SCRATCH / "test_results.json") if (SCRATCH / "test_results.json").exists() else {}
    n_tests_pass = sum(v["n_pass_lines"] for v in tests.values())
    g_f2_text = Path(G_F2).read_text()
    vel = {s: _j(f"data/v5/corpus/{s}/velocity_v5/velocities.json") for s in FOCUS}
    sep_x = {s: vel[s]["separation"]["cross_cycle_x2_holds"] for s in FOCUS}
    wig_in = vel["252eb21ce7df7328"]["separation"].get("in_cycle_x2_holds")
    r1 = prof["R1"]
    r2 = prof["R2"]
    f2 = roll["f2"]
    it3_wavs = [f"data/v5/gen/iteration_03/{s['generated_song_id']}_donor_{s['donor']}/ab_mix.wav" for s in roll["songs"]]
    it3_art = it3_wavs + [w.replace("ab_mix.wav", "ab_mix.manifest.json") for w in it3_wavs] + [w.replace("ab_mix.wav", "ab_mix.replay_proof.json") for w in it3_wavs]
    listening = [r["dest"] + "/ab_mix.wav" for r in lm["samples"]] + ["data/v4/generated/v5_iter_03/listening_manifest.json"]
    rms = {NAMES[s["donor"]]: s.get("rms_variance_test") for s in roll["songs"]}
    onset_ratios = {}
    for s in roll["songs"]:
        man = _j(f"data/v5/gen/iteration_03/{s['generated_song_id']}_donor_{s['donor']}/ab_mix.manifest.json")
        onset_ratios[NAMES[s["donor"]]] = {k: v.get("onset_rms_informational", {}).get("ratio_f2_over_uniform") for k, v in man["f2"]["rms_variance_test"]["per_stem"].items() if "f2" in v}
    per_stem_vel = {NAMES[s["donor"]]: {k: (v["velocity_min"], v["velocity_max"], v["n_distinct_velocities"]) for k, v in s["f2_per_stem"].items()} for s in roll["songs"]}
    events = []

    events.append(_ev("_plan/adopt-operator-guidance-2026-09-09-F2-and-F4-addendum", "validated", "high",
        "both operator blocks quoted verbatim from the on-disk file; sha16 pinned; the auditor-side sha mismatch disclosed.",
        f"c86 adoption of OPERATOR GUIDANCE 2026-09-09 F2 VELOCITY DECISION + F4 ADDENDUM (`{G_F2}`, sha256 {_sha(G_F2)}, sha16 8677bb0cd3f240a0, "
        f"{Path(G_F2).stat().st_size} B; the c85 auditor cited e9f67abb… which is a commit-side sha — the on-disk file governs, disclosed in one line). "
        f"VERBATIM: <<<{g_f2_text}>>> Backlog guidance `{G_BL}` sha {_sha(G_BL)[:16]}… (cf7296cfcf70c277) remains binding. Consequences this cycle: Route 1 decided "
        f"by the pre-registered gate (`M-V5-GEN-1/F2-velocity-route-decided-c86`); F4 adopted 122.197271 (PD) / 120.272335 (Disco A) with the unblock recorded IN the "
        f"blocked file (not deleted), harmony re-run at n=23 this cycle (cost {bd_f4.get('entries', bd_f4).get('harmony_markov_v5_full_c86', {}).get('wall_s_run1', 'few')} s) and consumed from iteration 4; "
        f"iteration 3 consumes the c84 n=21 rules by design (single-axis F2). No infeasibility memo written.",
        [G_F2, G_BL, "data/v5/gen/f2_prereg_c86.json"]))

    events.append(_ev("M-V5-GEN-1/F2-velocity-route-decided-c86", "validated", "high", "one ledger line per the operator's 10-minute rule; gate readings from data/v5/gen/f2_route_gate_c86.json.",
        f"ROUTE DECIDED = {gate['route']} (guidance sha16 8677bb0cd3f240a0): df {gate['df_used_pct_driver_semantics']} % ≤ 85 (driver semantics) ✓; htdemucs importable under "
        f"/usr/bin/python3 + sub_env (torch {gate['torch_version']}) ✓; full-song WIG separation {gate['separation_wall_s']} s ≤ 300 ✓ (decode {gate['decode_wall_s']} s, "
        f"full.wav sha == c79 {gate['full_wav_sha256'][:12]}…); stems deleted after hashing. Fresh stems did NOT match the c79 stage-cache SHAs (6/6 differ) → the pre-registered "
        f"fallback (in-cycle ×2 on WIG) applies; recorded in `M-V5-GEN-1/velocity-extraction-c86`.",
        ["data/v5/gen/f2_route_gate_c86.json", "scripts/v5/f2_route_gate_c86.py", "data/v5/logs/f2_route_gate_c86.log"]))

    events.append(_ev("M-V5-GEN-1/f2-preregistered-c86", "validated", "high", "prereg mtime precedes every F2 model/profile/render output (tests/test_c86_landing.py::test_01).",
        f"c86 F2 pre-registration `data/v5/gen/f2_prereg_c86.json` (sha {_sha('data/v5/gen/f2_prereg_c86.json')[:16]}…) written BEFORE any F2 output: Route-1 gate, 50 ms onset RMS, "
        "per-(song, stem) midrank normalization p5→40 / p95→110 with the degenerate guard (constant 80 + flag), profile definitions (drums GM class × 16th slot, bass by "
        "kick-coincidence, melody by phrase position, keys by slot), bass interval-class model, melody VOMM (order ≤ 3, escape), generator flags, the render-level clause (c) "
        "(frame-RMS variance ratio ≥ 1.5 per stem with notes, 5/5), enum F2_LANDS / F2_PARTIAL / F2_FAILS, diagnostic ladder R1/R2/R3, held-constant list. The route-gate JSON "
        "predates the prereg by construction of the 10-minute rule (disclosed).", ["data/v5/gen/f2_prereg_c86.json"]))

    r1s = {NAMES[s]: {st: vel[s]['stem_stats'][st]['spread_db'] for st in ('drums', 'bass', 'guitar', 'other', 'piano', 'vocals')} for s in FOCUS}
    walls = {NAMES[s]: vel[s]['separation']['wall_s'] for s in FOCUS}
    events.append(_ev("M-V5-GEN-1/velocity-extraction-c86", "validated", "high",
        "Route 1 executed on all 5 focus songs; in-cycle ×2 holds on WIG (three independent runs incl. the gate); cross-cycle mismatch vs the c79 cache recorded as a first-class finding, not retuned.",
        f"c86 F2 Route 1 (`scripts/v5/velocity_v5.py` sha {_sha('scripts/v5/velocity_v5.py')[:16]}…; separation in a pinned subprocess of the READ-ONLY recreate_v3._run_htdemucs_once; "
        f"score-and-delete; df peak {max(v['df_pct_peak'] for v in vel.values())} %). Separation walls {walls} s. CROSS-CYCLE ×2 vs the c79 stage-cache stem SHAs: "
        f"{ {NAMES[s]: sep_x[s] for s in FOCUS} } (FIRST-CLASS FINDING: every song's fresh stems differ from the c79 cache while the decoded full.wav SHAs match; candidate cause is "
        f"process-level torch/BLAS state at the c79 driver's load time vs now — not retuned, not chased this cycle); IN-CYCLE ×2 on WIG: {wig_in} (gate run + extractor run1 + run2 "
        f"{'all equal' if bd_gen['route1_separation']['wig_gate_run_equals_extractor_runs'] else 'DIFFER'}). Per-(song, stem) onset-RMS spread p95−p5 (dB): {r1s}. R1 (≥ 6 dB on ≥ 4/5): "
        f"drums {r1['songs_passing_per_stem']['drums']}/5, bass {r1['songs_passing_per_stem']['bass']}/5 → {r1['drums_bass_pass_ge_4_of_5']}; Route-2 fallback stems: {r1['route_2_fallback_stems']}. "
        f"Degenerate guard fired: {[(NAMES[s], st) for s in FOCUS for st in vel[s]['stem_stats'] if vel[s]['stem_stats'][st]['degenerate']]}. Outputs per song: "
        f"`velocity_v5/velocities.json` + sibling `canonical_v5_velocity/<stem>.mid` (the reindexed events with velocities, serialized by the sibling serializer at the grid tempo — "
        f"PD/Disco A at the operator-adopted 122.197271 / 120.272335); `canonical_v5_reindexed/*.mid` NEVER written (tested sidecar anchors) — the operator's 'write velocities into "
        f"canonical_v5_reindexed' is read as 'into the same song directory, sibling dir' (disclosed).",
        [f"data/v5/corpus/{s}/velocity_v5/velocities.json" for s in FOCUS] + [f"data/v5/corpus/{s}/canonical_v5_velocity/{st}.mid" for s in FOCUS for st in ("drums", "bass", "guitar", "other", "piano", "vocals")]
        + ["scripts/v5/velocity_v5.py", "scripts/v5/midi_from_json_events_v5.py", "tools/_launch_velocity_c86.py", "data/v5/logs/velocity_v5_c86.log", "data/v5/logs/velocity_v5_c86.launch.json", "data/v5/logs/velocity_v5_c86.progress.json"]))

    events.append(_ev("M-V5-RULES-1/velocity-profiles-c86", "validated", "high", "profiles byte-det ×2 (--profiles-only rebuild); R2 diagnostics recorded from the prereg; figure + --out plot script on disk.",
        f"c86 F2 velocity profiles `data/v5/rules/velocity_profiles_v5.json` (sha {_sha('data/v5/rules/velocity_profiles_v5.json')[:16]}…, byte-det ×2 {bd_gen['velocity_profiles_v5']['equal']}): "
        f"drums per GM class × 16th slot (phase offset from groove per_song; 0 for PD/Disco A), bass by kick-coincidence (±30 ms) × slot, melody by phrase position, keys by slot; "
        f"quantile ladders [0,10,25,50,75,90,100] sampled by SHA-256 inverse-CDF at generation. R2: backbeat(slots 4,12) − odd = {r2['backbeat_minus_odd']} (≥ +10: {r2['backbeat_ge_plus_10']}); "
        f"hat odd {r2['hat_odd_mean']} < even {r2['hat_even_mean']}: {r2['hat_odd_lower_than_even']}; bass kick-coincident {r2['bass_kick_coincident_mean']} > non {r2['bass_non_coincident_mean']}: "
        f"{r2['bass_coincident_gt_non']}; drum slot-profile std {r2['drums_slot_profile_std']} (structureless < 5: {r2['structureless_std_lt_5']}). Figure `fig_velocity_profiles_c86.png` "
        "(caption: per-stem mean velocity by 16th slot, 5 songs overlaid, pooled ladder median thick, backbeat slots shaded).",
        ["data/v5/rules/velocity_profiles_v5.json", "data/v5/rules/fig_velocity_profiles_c86.png", "data/v5/rules/plot_velocity_profiles_c86.py"]))

    sc_b = bass["sampling_check"]
    events.append(_ev("M-V5-RULES-1/bass-pitch-model-c86", "validated", "high", "byte-det ×2 with the script sha recorded; root-on-downbeat reproduction within ±0.15 (pre-registered).",
        f"c86 F2 bass pitch model `scripts/v5/bass_pitch_v5.py` (sha {bd_models['bass_pitch_v5']['script_sha256'][:16]}…) → `data/v5/rules/bass_pitch_v5.json` (sha {_sha('data/v5/rules/bass_pitch_v5.json')[:16]}…, "
        f"byte-det ×2 {bd_models['bass_pitch_v5']['equal']}) on the n=21 eligible_c84 corpus: {bass['n_onsets_total']} bass onsets, {bass['n_events']} classified ({bass['n_skipped_null_chord_total']} skipped on null-chord beats — "
        f"disclosed); interval-class marginal {bass['marginal']['probs']}; conditionals keyed (slot-in-beat | chord-change) with α = 0.5; corpus root-on-downbeat {sc_b['corpus_downbeat_root_pc_fraction']} vs "
        f"sampled {sc_b['sampled_root_pc_fraction']} (|Δ| {sc_b['abs_diff']} ≤ 0.15: {sc_b['pass']}); corpus register median {bass['register']['corpus']['median']} IQR "
        f"[{bass['register']['corpus']['iqr_lo']}, {bass['register']['corpus']['iqr_hi']}]; per-donor registers used by the generator (PD/Disco A fall back to the corpus register, disclosed). "
        f"Exports sample_interval_class / interval_to_pitch (GM bass range 28..60).", ["scripts/v5/bass_pitch_v5.py", "data/v5/rules/bass_pitch_v5.json", "data/v5/rules/byte_determinism_c86_f2models.json"]))

    os3 = vomm["order_stats"]["3"]
    events.append(_ev("M-V5-RULES-1/melody-vomm-c86", "validated", "high", "byte-det ×2 with the script sha; MEMORIZES is the recorded pre-registered outcome (not tuned).",
        f"c86 F2 melody VOMM `scripts/v5/melody_vomm_v5.py` (sha {bd_models['melody_vomm_v5']['script_sha256'][:16]}…) → `data/v5/rules/melody_vomm_v5.json` (sha {_sha('data/v5/rules/melody_vomm_v5.json')[:16]}…, "
        f"byte-det ×2 {bd_models['melody_vomm_v5']['equal']}): tokens '<scale degree 0..6 | c>|<IOI bucket in 16ths {{1,2,3,4,6,8,12}}>' from vocals + other synth_lead starts on n=21 "
        f"({vomm['n_songs_with_events']} songs with events, vocab {len(vomm['vocab'])}); order ≤ 3 with escape; singleton-context fraction order 3 = {os3['singleton_context_fraction']} "
        f"({os3['n_singleton_contexts']}/{os3['n_contexts']}) → **{vomm['verdict']}** (pre-declared threshold 0.5; recorded, not tuned); order-2 {vomm['order_stats']['2']['singleton_context_fraction']}. "
        f"c72 vomm_generator NOT reused ({vomm['vomm_generator_reuse_reason'][:120]}…). Sampling check L1 to unigram {vomm['sampling_check']['l1_to_corpus_unigram']} (informational). "
        f"Disclosure: chromatic 16th runs ('c|1', vocal pitch-bend transcription artefacts) dominate transitions.",
        ["scripts/v5/melody_vomm_v5.py", "data/v5/rules/melody_vomm_v5.json"]))

    events.append(_ev("M-V5-GEN-1/iteration-03-c86", "in-progress", "high",
        "5 renders byte-det ×2 in fresh tempdirs under the post-edit generator sha; flag-off replay reproduces iteration 2 5/5; informational scores only (FD-6: no passer declared).",
        f"c86 iteration 3 (seed 2, `--form-plan --f2 --velocity-mode f2 --rms-variance-test --prove-replay`, rules = c84 n=21 harmony a984ee17… + groove faa0e76e… — the n=23 chain is consumed "
        f"from iteration 4 per the operator addendum; generator sha {roll['generator_hash'][:16]}… == on-disk {bd_gen['iteration_03_renders']['generate_v5_sha256'] == roll['generator_hash']}): "
        f"5/5 REPLAY_PROOF_HOLDS ({bd_gen['iteration_03_renders']['all_equal']}); forms {[''.join(s['form']) for s in roll['songs']]}; durations {[s['duration_s'] for s in roll['songs']]} s; "
        f"per-stem velocity (min, max, distinct) {per_stem_vel}; velocities present on every stem with notes {f2['n_velocities_present']}/5. RMS-variance clause (c) — pre-registered frame-RMS "
        f"variance ratio F2/uniform over active frames: {rms}; passes 5/5: {f2['clauses']['rms_variance_5_of_5']} ({f2['n_rms_variance_pass']}/5). Informational onset-window ratio "
        f"(not the clause): {onset_ratios}. Flag-off replay under this generator image reproduces the 5 iteration-2 WAV SHAs ({bd_gen['iteration_02_flag_off_replay']['all_equal']}). "
        f"Informational ear scores (venv, c76 v2; NOT passers, FD-6 + c76 L119): ≥ 6 {sc['n_gen_ge_6']}/5, {[round(v['ear_score_v2'], 3) for v in sc['scores'].values()]}, table byte-det ×2 "
        f"{bd_gen['iteration_03_ear_scores_table']['equal']}. Listening copies → data/v4/generated/v5_iter_03/ ({len(lm['samples'])} songs). Stall {stall['iterations']}/{stall['budget']}; "
        f"history[-1] feature '{stall['history'][-1]['feature']}' with route + model SHAs (F6). Figure `iteration_03/fig_iter03_velocity_c86.png` (caption: F2 velocities vs the uniform twin — "
        "per-stem frame-RMS variance and ratio with the 1.5 gate and the exact-null line).",
        it3_art + listening + ["data/v5/gen/iteration_03/iteration_rollup.json", "data/v5/gen/gen_v5_iter03_ear_scores_c86.json", "data/v5/gen/stall_counter.json",
                              "data/v5/gen/iteration_03/fig_iter03_velocity_c86.png", "data/v5/gen/iteration_03/plot_iter03_velocity_c86.py", "data/v5/gen/byte_determinism_c86.json",
                              "data/v5/logs/generate_v5_iter03_c86.log", "data/v5/logs/score_gen_v5_iter03_c86_run1.log", "data/v5/logs/score_gen_v5_iter03_c86_run2.log"],
        supersedes_path="M-V5-GEN-1/iteration-02-c85"))

    events.append(_ev("M-V5-GEN-1/F2-bass-melody-dynamics", "validated", "high",
        f"enum {f2['f2_enum']} recorded from the pre-registered clauses; operator clauses (a) velocities in generated MIDI for all stems, (b) rendered iteration, (c) RMS-variance test all executed.",
        f"c86 F2 BASS + MELODY + DYNAMICS landed as iteration 3 — enum **{f2['f2_enum']}** (clauses {f2['clauses']}). Route 1 (stem audio) velocities for ALL stems incl. drums/keys; bass pitches "
        f"from the chord-conditioned interval model in the donor register; melody from the order-3 VOMM per section run (literal repeats reproduce; muted per the F1 arrangement); "
        f"sibling serializer with the velocity field (byte-equal to the READ-ONLY c4 serializer without velocities, 56/56 on the iteration-2 event JSON). Operator clause (a) velocities present "
        f"{f2['n_velocities_present']}/5; (b) iteration 3 rendered 5/5 byte-det ×2; (c) uniform-vs-F2 render differ: frame-RMS variance ratios {rms} (pre-registered ≥ 1.5 gate passes "
        f"{f2['n_rms_variance_pass']}/5; the uniform twin is the exact null, velocity 100 everywhere). Diagnostic ladder: R1 {r1['drums_bass_pass_ge_4_of_5']}; R2 backbeat {r2['backbeat_ge_plus_10']} / "
        f"std {r2['drums_slot_profile_std']}; R3 {f2['clauses']['rms_variance_5_of_5']}. VOMM {vomm['verdict']} (recorded). Iteration 3 still consumes n=21 (single-axis).",
        ["scripts/v5/generate_v5.py", "scripts/v5/midi_from_json_events_v5.py", "data/v5/gen/f2_prereg_c86.json", "data/v5/gen/iteration_03/iteration_rollup.json"]))

    pre_sha, post_sha = "2fbabc07849dbe238545b9e629f91cd81746c6216e5db3027e88f4e9313f8a8e", _sha("data/v5/corpus/recanonicalization_blocked.json")
    events.append(_ev("M-V5-CORPUS-1/tempo-f4-operator-resolved-c86", "validated", "high",
        "operator adjudication recorded verbatim; blocked file amended in place per the operator with the pre-amend bytes preserved as a stale copy; v5c canonical dirs byte-det ×2.",
        f"c86 F4 operator adjudication (guidance 8677bb0cd3f240a0 addendum) overrules c85 F4_HALF_DOUBLE_AMBIGUOUS — the failing 'T/2 and 2T score lower under s_ref' clause is a defect of the "
        f"criterion for a 4/4 groove with a strong 2-bar period; refined-lag dominant and the independent c22 anchor agree within 1 BPM. Adopted PD {res['adopted_bpm']['88d247468cb6d49f']} "
        f"(Δ −0.850 vs c22) and Disco A {res['adopted_bpm']['cdd2717e52820ff6']} (Δ +0.087), recorded in `tempo_f4_operator_resolution_c86.json` ({_sha('data/v5/corpus/tempo_f4_operator_resolution_c86.json')[:16]}…). "
        f"`recanonicalization_blocked.json` amended IN PLACE, additively (pre-amend {pre_sha[:16]}… preserved byte-identical as `stale/recanonicalization_blocked.c80_c85.json`; post {post_sha[:16]}…): "
        f"`unblocked_c86` for both songs, `blocked_songs_effective []`, `blocked_songs` kept as history and as generate_v5.donor_tempo's frozen-anchor source (iteration 3 unchanged). "
        f"`scripts/v5/recanonicalize_tempo_v5.py` wrote `canonical_v5c_reindexed/` for both songs at the adopted BPM via the READ-ONLY c80 reindex + c4 serializer: note_on == JSON starts on all 14 probes, "
        f"set_tempo == bpm2tempo(adopted) (SMF integer µs/beat quantization disclosed: 122.197271 → 491009 µs), byte-det ×2 equal, `canonical_v5_reindexed/` untouched. No external criterion, no v5e, no further tempo prereg.",
        ["data/v5/corpus/tempo_f4_operator_resolution_c86.json", "data/v5/corpus/recanonicalization_blocked.json", "data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json",
         "data/v5/corpus/tempo_overrides_c86.json", "scripts/v5/recanonicalize_tempo_v5.py", "data/v5/corpus/byte_determinism_c86.json",
         "data/v5/corpus/88d247468cb6d49f/canonical_v5c_reindexed_sha256.json", "data/v5/corpus/cdd2717e52820ff6/canonical_v5c_reindexed_sha256.json",
         "data/v5/corpus/88d247468cb6d49f/canonical_v5c_reindexed/reindex_manifest.json", "data/v5/corpus/cdd2717e52820ff6/canonical_v5c_reindexed/reindex_manifest.json",
         "data/v5/corpus/f4_close_report_c86.md"],
        supersedes_path="data/v5/corpus/tempo_f4_verdict_c85.json"))

    events.append(_ev("M-V5-RULES-1/harmony-n23-c86", "validated", "high", "prereg before the run; enum from the prereg; chain byte-det ×2 with the post-edit script sha; c84 chain reproduced byte-identically by the edited script.",
        f"c86 harmony re-run at n=23 (c84's 21 + unblocked PD/Disco A; `eligible_c86.json` {_sha('data/v5/rules/eligible_c86.json')[:16]}…; `harmony_prereg_c86.json` before the run; c84 rule + threshold 12 unchanged) "
        f"with the additive `--tempo-overrides` (asserts canonical_v5c_reindexed served the song): **{h23['degeneracy_verdict']}** — {len(h23['states'])} states (n=21 {diff['n21']['n_states']}; union {diff['union_states']}), "
        f"max stationary {h23['max_stationary_state']} = {h23['max_stationary_mass']} (n=21 {diff['n21']['max_stationary_mass']}; max |Δπ| {diff['max_abs_stationary_delta']}), top-10 transition mass {diff['n23']['top10_transition_mass']} (n=21 {diff['n21']['top10_transition_mass']}), "
        f"qualities ≥ 8 segs {h23['qualities_with_count_ge_threshold']}; PD key {h23['per_song']['88d247468cb6d49f']['key']['tonic_name']} {h23['per_song']['88d247468cb6d49f']['key']['mode']} {h23['per_song']['88d247468cb6d49f']['n_segments']} segments, "
        f"Disco A {h23['per_song']['cdd2717e52820ff6']['key']['tonic_name']} {h23['per_song']['cdd2717e52820ff6']['key']['mode']} {h23['per_song']['cdd2717e52820ff6']['n_segments']} segments. Chain `harmony_markov_v5_full_c86.json` "
        f"{_sha('data/v5/rules/harmony_markov_v5_full_c86.json')[:16]}… byte-det ×2 (post-edit harmony_v5.py {_sha('scripts/v5/harmony_v5.py')[:16]}…); the edited script still replays the c84 chain a984ee17… via --eligible-from eligible_c84.json; "
        f"c84 artifacts untouched. GROOVE n=23 (`groove_prereg_c86.json`, same SHA-256 fold, wrapper `data/v5/rules/groove_v5_full_c86.py`): **{g23['verdict']}** singleton {g23['singleton_context_fraction']} (c84 0.642813), "
        f"held-out within tol; `groove_v5_v2_full_c86.json` {_sha('data/v5/rules/groove_v5_v2_full_c86.json')[:16]}… byte-det ×2. DISCLOSURE: the brief's '26 − 1 − 0 = 23' is a slip — 25 landed music songs are eligible; the two "
        f"late landers 0e1e8f20592db366 / cc0693b4a24f64b2 stay deferred (gate `late_landed_deferred`) so n=23 is exactly the operator's set; n=25 is a one-command follow-up. Figure `fig_harmony_n23_vs_n21_c86.png` "
        "(caption: n=23 chain differs from n=21 only where PD/Disco A contribute; rule unchanged). Consumed from iteration 4.",
        ["data/v5/rules/eligible_c86.json", "data/v5/rules/harmony_prereg_c86.json", "data/v5/rules/harmony_markov_v5_full_c86.json", "data/v5/rules/byte_determinism_c86_f4.json",
         "data/v5/rules/groove_prereg_c86.json", "data/v5/rules/groove_v5_full_c86.py", "data/v5/rules/groove_v5_v2_full_c86.json", "data/v5/rules/fig_harmony_n23_vs_n21_c86.png",
         "data/v5/rules/plot_harmony_n23_vs_n21_c86.py", "data/v5/rules/harmony_n23_vs_n21_diff_c86.json", "scripts/v5/harmony_v5.py", "scripts/v5/groove_v5_v2.py",
         "data/v5/rules/per_song_c86/88d247468cb6d49f/harmony_v5.json", "data/v5/rules/per_song_c86/cdd2717e52820ff6/harmony_v5.json"]))

    events.append(_ev("M-V5-GEN-1/F4-tempo-fix", "validated", "high", "F4 CLOSED by operator adjudication: unblock recorded, v5c recanonicalization ×2, n=23 chain NON_DEGENERATE ×2, operator-required test green.",
        f"F4 TEMPO FIX CLOSED (c86): both tempo-blocked focus songs unblocked at 122.197271 / 120.272335 under operator authority (8677bb0cd3f240a0 addendum), re-canonicalized losslessly and "
        f"byte-deterministically into canonical_v5c_reindexed/, consumed by the rules layer at n=23 ({h23['degeneracy_verdict']}; groove re-measured {g23['verdict']}); harmony_v5.py / groove_v5_v2.py "
        f"honour the unblock additively and assert the v5c dir under --tempo-overrides. generate_v5.donor_tempo untouched (reads blocked_songs) so the flag-off replay of iteration 2 is byte-identical and "
        f"iteration 3 consumes n=21 by design; the n=23 chain + v5c tempos are iteration 4's inputs. Tests: tests/test_c86_f4_close.py {tests.get('tests/test_c86_f4_close.py', {}).get('n_pass_lines', '?')}/6 "
        f"(operator-required adopted-BPM + eligibility test included), tests/test_c85_f4_m5.py re-pinned {tests.get('tests/test_c85_f4_m5.py', {}).get('n_pass_lines', '?')}/5; "
        "test_c84_landing::test_02 + test_c85_landing::test_01/test_08 re-pinned to the stale copy + amended schema (disclosed). Tempo axis remains STOPPED (no criterion, no v5e).",
        ["data/v5/corpus/tempo_f4_operator_resolution_c86.json", "data/v5/rules/harmony_markov_v5_full_c86.json", "tests/test_c86_f4_close.py", "tests/test_c85_f4_m5.py"]))

    events.append(_ev("_infra/cheap-fixes-M1-M2-c86", "validated", "high", "each fix verified by a test or a recorded SHA.",
        f"c86 P0: M1 `data/v5/corpus/plot_tempo_f4_c85.py` gained a REQUIRED `--out` (re-emitted `fig_tempo_f4_c85.png` sha {_sha('data/v5/corpus/fig_tempo_f4_c85.png')[:16]}… pinned in byte_determinism_c85.json entry `c86_reissue`; "
        "the previous on-disk PNG was an auditor-regenerated copy — disclosed); every new c86 plot script takes `--out`; `score_gen_batch_v5.py` + `deliver_v5_listening.py` `--cycle` REQUIRED (argparse error on omission, test_07); "
        "`form_plan_v5.py` asserts new_output_mtime > prereg_mtime after the write (MINOR 2); sibling serializer `scripts/v5/midi_from_json_events_v5.py` (velocity field; byte-equal to c4 without velocities). "
        "MINOR 7 (AABC/ABAC 4-section fallback) deliberately NOT this cycle (second axis under iteration 3; queued for the F5 cycle with its own prereg). M2 byte-determinism files: gen/ (this worker), "
        "corpus/ + rules/…_f4 (F4 teammate), rules/…_f2models (models teammate) — split by owner to avoid write collisions (disclosed).",
        ["data/v5/corpus/plot_tempo_f4_c85.py", "data/v5/corpus/fig_tempo_f4_c85.png", "data/v5/corpus/byte_determinism_c85.json", "scripts/v5/score_gen_batch_v5.py", "scripts/v5/deliver_v5_listening.py",
         "scripts/v5/form_plan_v5.py", "scripts/v5/midi_from_json_events_v5.py"]))

    events.append(_ev("_plan/register-c86-sub-leaves", "validated", "high", "rows inserted inline in the parseable region by tools/_register_c86_por_rows.py (idempotent).",
        "c86 POR registration row: c86 sub-leaves inserted inline before `## Sub-milestones` (F2 route / prereg / extraction / profiles / bass / VOMM / iteration-03 / F2 landed; F4 resolved / harmony n=23 / F4 CLOSED; "
        "cheap fixes; housekeeping). F1..F7 backlog rows updated by reference in the ledger (F2 landed, F4 CLOSED; F3 next).", ["plan_of_record.md", "tools/_register_c86_por_rows.py"]))

    events.append(_ev("_infra/adopt-cycle86-tests", "validated", "high", "adopted suite re-run under /usr/bin/python3; counts from the run record (ADOPTED suite, not tests/ as a whole).",
        f"c86 test-adoption: `tests/test_c86_landing.py` ({tests.get('tests/test_c86_landing.py', {}).get('n_pass_lines', '?')}) + `tests/test_c86_f4_close.py` ({tests.get('tests/test_c86_f4_close.py', {}).get('n_pass_lines', '?')}) + "
        f"`tests/test_c86_f2_models.py` ({tests.get('tests/test_c86_f2_models.py', {}).get('n_pass_lines', '?')}) new; `tests/test_c85_f4_m5.py::test_01`, `tests/test_c84_landing.py::test_02`, "
        f"`tests/test_c85_landing.py::test_01/test_08` re-pinned to the stale blocked copy + amended schema + v5c dirs (disclosed). Adopted suite {len(tests)} files / {n_tests_pass} PASS lines, all rc=0: {all(v['rc'] == 0 for v in tests.values())}.",
        ["tests/test_c86_landing.py", "tests/test_c86_f4_close.py", "tests/test_c86_f2_models.py", "tests/test_c85_f4_m5.py", "tests/test_c84_landing.py", "tests/test_c85_landing.py"]))

    events.append(_ev("_archive/cycle-86-scratch", "validated", "high", "one-shot emitter + registrar + launcher retained in-tree per emitter-exemption policy and listed as artifacts (L1).",
        "c86 scratch archival: `tools/_emit_c86_ledger_events.py` + `tools/_register_c86_por_rows.py` + `tools/_launch_velocity_c86.py` retained in-tree per docs/emitter_exemption_policy.md; session-scoped scratchpad "
        "runners (probe1-3, ser_check, flagoff_check_c86, f2_smoke, bytedet_gen_c86, run_tests) not in the workspace; plot scripts co-located with their data + figures; the F4 teammate's groove wrapper lives at "
        "data/v5/rules/groove_v5_full_c86.py (its write scope; disclosed). Stale /tmp tempdirs from ×2 runs are reclaimable.",
        ["tools/_emit_c86_ledger_events.py", "tools/_register_c86_por_rows.py", "tools/_launch_velocity_c86.py"]))

    events.append(_ev("_run/cycle_86_closed", "validated", "high", "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        f"c86 CLOSED — v5 REOPENING cycle 8 (feature cycle: F2 {f2['f2_enum']} as iteration 3 via Route 1; F4 CLOSED by operator adjudication with n=23 harmony {h23['degeneracy_verdict']}; P0 fixes). "
        f"FROZEN/READ-ONLY anchors {n_frozen_ok}/{len(FROZEN_EXPECTED)} byte-identical: " + "; ".join(f"{k} {frozen[k][:12]}{'' if frozen_ok[k] else ' MISMATCH'}" for k in FROZEN_EXPECTED)
        + f". env_pin_sha256 {ENV_PIN[:8]}…922ca unchanged. df at emit {df_now} % (avail {avail_now} GB); never ≥ 90 %. Cycle counter: on-disk c86, harness c130 (offset 44, disclosed, not reconciled). "
        "Status convention (L2): `validated` for recorded PARTIAL / MEMORIZES / OVERFITS verdicts; `in-progress` for iteration-03 (no passer). Full 9-header summary in the c86 work output.",
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_85_closed"))

    _le = os.environ.get("LONG_EXPOSURE_PKG_PATH", "/home/user/human-in-a-loop/long-exposure")
    if _le not in sys.path:
        sys.path.append(_le)
    existing_ids = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            existing_ids.add(json.loads(line).get("milestone_id"))
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
    for e in events:
        for a in e["artifacts"]:
            assert Path(a).exists(), (e["milestone_id"], a)
    if "--dry-run" in sys.argv:
        print(f"DRY RUN: {len(events)} events validated; frozen OK {n_frozen_ok}/{len(FROZEN_EXPECTED)}; would append {[e['milestone_id'] for e in events if e['milestone_id'] not in existing_ids]}")
        return 0
    to_append = [e for e in events if e["milestone_id"] not in existing_ids]
    if not to_append:
        print("IDEMPOTENT: all c86 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c86 events; frozen anchors OK {n_frozen_ok}/{len(FROZEN_EXPECTED)}")
    for e in to_append:
        print(f"  {e['status']:16s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
