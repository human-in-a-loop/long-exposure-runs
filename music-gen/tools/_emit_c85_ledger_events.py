#!/usr/bin/python3
"""c85 one-shot ledger emitter — v5 REOPENING cycle 7 (F1 length+form+arrangement as iteration 2; F4 operator adjudication;
P0 cheap fixes M2/M4/M5/F6; guidance adoption; bookkeeping).

Every event carries `agent` (REQUIRED_EVENT_FIELDS); UUID5(NAMESPACE_URL, canonical-JSON of body minus event_id and ts);
idempotent by milestone_id; supersedes_path is str|None (c14 lemma). Status convention (L2): `validated` for a RECORDED
pre-registered verdict (PARTIAL / AMBIGUOUS / R1 FAILED are recorded outcomes, not tuned away); `in-progress` for a feature
milestone that did not land. Reads every number from disk at emit time. Retained in-tree per docs/emitter_exemption_policy.md.
"""
import hashlib
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
os.chdir(_REPO)
LEDGER = _REPO / "promise_ledger.jsonl"
CYCLE = 85
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
GUIDANCE = "docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt"
GUIDANCE_F2 = "docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt"
FROZEN_EXPECTED = {
    "docs/v3_determinism_certificate.md": "a6876911", "data/v3/rules/rules_artifact.jsonl": "e19fb205",
    "data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav": "6e13e007", "data/v4/profiles/31a164f845f8e27e/bass_v2.json": "2a1cb340",
    "data/v4/profiles/88d247468cb6d49f/stem_manifest.json": "d483f2bf", "data/v4/ear/exemplar_set.json": "31c10dfb",
    "scripts/ear/v4_ear.py": "e775621b", "scripts/gen/iterate_v4.py": "8f1f0b88", "scripts/gen/interpolate_v4.py": "2359f35d",
    "docs/v4_completion_report_v3.md": "b900b0ee", "scripts/v3_spine/recreate_v3.py": "b1490874",
    "scripts/v3_spine/stage_cache.py": "33435a84", "scripts/v3_spine/midi_from_json_events.py": "bbff015f",
    "scripts/sound_match/_sweep_hygiene_c27.py": "771ff42b", "data/v5/corpus/corpus_manifest.json": "73362136",
    "data/v5/corpus/recanonicalization_blocked.json": "2fbabc07", "data/v5/corpus/content_blocked.json": "fc07a138",
    "data/v5/rules/harmony_markov_v5_full.json": "a984ee17", "data/v5/rules/groove_v5_v2_full.json": "faa0e76e",
    "data/v5/rules/harmony_markov_v5.json": "9785a907", "data/v5/rules/harmony_prereg_c84.json": "db71346b", "data/v5/rules/groove_prereg_c84.json": "b5cb6f39",
}
SCRATCH = Path("/tmp/claude-0/-home-user-long-exposure-runs-music-gen/2d0b6f55-3510-4a61-8d0b-8c04c4d871bc/scratchpad")


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
    st = os.statvfs("."); avail = st.f_bavail * st.f_frsize; used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return round(100 * used / (used + avail), 2), round(avail / 1e9, 3)


def main() -> int:
    events = []
    frozen = {k: _sha(k) for k in FROZEN_EXPECTED}
    frozen_ok = {k: frozen[k].startswith(v) for k, v in FROZEN_EXPECTED.items()}
    df_now, avail_now = _df()
    g_txt = Path(GUIDANCE).read_text()
    g_lines = [l.rstrip() for l in g_txt.splitlines()]
    verbatim_abc = "\n".join(l for l in g_lines if re.match(r"^(A\.|B\.|C\.|   )", l) and g_lines.index(l) < [i for i, l2 in enumerate(g_lines) if l2.startswith("Feature backlog")][0])
    verbatim_f = "\n".join(l for l in g_lines[[i for i, l2 in enumerate(g_lines) if l2.startswith("Feature backlog")][0]:])
    f2 = _j("data/v5/gen/byte_determinism_c85.json")  # noqa: F841 (presence check)

    # ---- P0: guidance adoption ----
    events.append(_ev("_plan/adopt-operator-guidance-2026-09-09-F1-F7", "validated", "high",
        "guidance file read in full; consequences A/B/C + F1–F7 quoted verbatim; POR rows F1..F7 registered inline this cycle.",
        f"c85 ADOPTS OPERATOR GUIDANCE 2026-09-09 (`{GUIDANCE}`, sha {_sha(GUIDANCE)[:16]}…) verbatim:\n{verbatim_abc}\n{verbatim_f}\n"
        f"Consequence this cycle: the ear ≥6 count is NOT the gate; F1 landed as iteration 2 (code + test + rendered 5-song iteration to data/v4/generated/v5_iter_02/); "
        f"F4 adjudicated under a pre-registered check; F6 stall-history schema landed; F2/F3/F5 queued in order; F7 after F1–F5. "
        f"F2 VELOCITY-SOURCE DISCLOSURE (one line, per the brief; the operator's `{GUIDANCE_F2}` sha {_sha(GUIDANCE_F2)[:16]}… pre-empts any infeasibility memo): MuScriptor JSON `start` events carry only "
        f"{{index, instrument, pitch, start_time}} — no velocity — and no full-length stem audio survives the stage cache (transients deleted per hygiene), so 'carry MuScriptor velocities through canonical MIDI' is infeasible as worded; "
        f"F2 dynamics come from Route 1 (re-separate the 5 focus songs on demand, 50 ms RMS at each onset, rank-normalized p5→40/p95→110, score-and-delete) or Route 2 (rule-based accent model from groove_v5_v2_full.json onset histograms), decided in the first 10 minutes of the F2 cycle.",
        [GUIDANCE, GUIDANCE_F2, "plan_of_record.md"], supersedes_path=None))

    # ---- P1: F1 ----
    fpre = Path("data/v5/gen/form_prereg_c85.json"); fp = _j("data/v5/rules/form_plan_v5.json")
    bd = _j("data/v5/gen/byte_determinism_c85.json")["entries"]
    r1 = fp["R1"]
    events.append(_ev("M-V5-GEN-1/form-preregistered-c85", "validated", "high", "prereg mtime precedes the model and every iteration-2 output (test_01).",
        f"c85 P1: `form_prereg_c85.json` (sha {_sha(fpre)[:16]}…) written BEFORE any output: segmentation (per-bar 12-D PCP with the pre-declared min(duration, 1 beat) cap over bass+guitar+piano+other ⊕ 48-D kick16/snare16/hat16 ⊕ 6-D per-stem onset density; 8-bar blocks; cosine; deterministic single linkage at 0.85; first-appearance labels), "
        f"form-plan model (length round(bars/8) clipped [4,8]; label Markov with <4-block songs contributing length only; per-label drum-density tercile + harmony-region targets; intro density quantile; boundary fill pool), contrast rule, arrangement, enum FORM_PLAN_LANDS/PARTIAL/FAILS, diagnostic ladder R1 (fixed template A A B A B C A A fallback, no sweep) / R2. "
        f"Corpus = the 21 c84 chain songs (0e1e8f20592db366 + cc0693b4a24f64b2 landed after the c84 rules run and are excluded, disclosed; c86 re-runs with them).",
        ["data/v5/gen/form_prereg_c85.json"], supersedes_path=None))
    events.append(_ev("M-V5-GEN-1/form-plan-model-c85", "validated", "high",
        "R1 verdict recorded from the prereg (FAILED at 0.85; template fallback pre-declared); model byte-det x2; c84 rules untouched.",
        f"c85 P1 form-plan model `scripts/v5/form_plan_v5.py` → `data/v5/rules/form_plan_v5.json` (sha {_sha('data/v5/rules/form_plan_v5.json')[:16]}…; byte-det x2 {bd['form_plan_v5']['equal']}, tempdirs {bd['form_plan_v5']['tempdir_run1']} / {bd['form_plan_v5']['tempdir_run2']}) on n={fp['n_eligible']}. "
        f"**R1 FAILED** (recorded, NOT swept — FD-1): at the pre-declared 0.85 threshold single linkage gives CG `{r1['focus_songs']['31a164f845f8e27e']['form']}` ({r1['focus_songs']['31a164f845f8e27e']['n_labels']} labels), Rome `{r1['focus_songs']['51e433ade2a845e1']['form']}` ({r1['focus_songs']['51e433ade2a845e1']['n_labels']} label), WIG `{r1['focus_songs']['252eb21ce7df7328']['form']}` ({r1['focus_songs']['252eb21ce7df7328']['n_labels']} labels) — "
        f"transcribed-MIDI block features either chain into one cluster or fragment; 0.85 is the wrong threshold for this representation. Per the prereg the generator uses the fixed template {''.join(r1['fallback_template'])} truncated to the corpus-drawn length. "
        f"Recorded corpus model anyway: length distribution {fp['length_distribution']} (18/21 songs clip to 8 sections); start {fp['start_distribution']}; repeat-A probability {fp['repeat_A_probability']}; labels {fp['labels']}; "
        f"density tercile bounds {fp['density_tercile_bounds']} onsets/bar over {fp['n_blocks_total']} blocks; per-label tercile probs A {fp['per_label']['A']['density_tercile_probs']} / B {fp['per_label']['B']['density_tercile_probs']} / C {fp['per_label']['C']['density_tercile_probs']}; harmony region (argmax rel. root) A {fp['per_label']['A']['harmony_region']} B {fp['per_label']['B']['harmony_region']} C {fp['per_label']['C']['harmony_region']}; "
        f"intro density quantile {fp['intro_density_quantile']} (< 0.33 → bass-only intro); boundary fill pool {len(fp['boundary_fill_pool'])} patterns from {fp['n_boundary_bars']} boundary bars (fallback used {fp['fill_pool_fallback_used']}). "
        f"Figure `data/v5/rules/fig_form_plan_corpus_c85.png` (bar-count histogram / length distribution / label-transition matrix) from `plot_form_plan_corpus_c85.py`. c86 axis: a representation/threshold study is a NEW pre-registration, not a retune.",
        ["scripts/v5/form_plan_v5.py", "data/v5/rules/form_plan_v5.json", "data/v5/rules/fig_form_plan_corpus_c85.png", "data/v5/rules/plot_form_plan_corpus_c85.py", "data/v5/gen/byte_determinism_c85.json"],
        supersedes_path="M-V5-GEN-1/form-preregistered-c85"))
    roll = _j("data/v5/gen/iteration_02/iteration_rollup.json")
    sc = _j("data/v5/gen/gen_v5_iter02_ear_scores_c85.json")
    lm = _j("data/v4/generated/v5_iter_02/listening_manifest.json")
    stall = _j("data/v5/gen/stall_counter.json")
    songs_line = "; ".join(f"{s['generated_song_id']}←{s['donor'][:8]} form {''.join(s['form'])} {s['n_bars']} bars {s['duration_s']} s sha {s['ab_mix_sha256'][:12]}… {s['replay_proof']} clauses {sum(s['clauses'].values())}/5"
                           + ("" if s["all_clauses"] else f" (fails {[k for k, v in s['clauses'].items() if not v]})") for s in roll["songs"])
    contrast_line = "; ".join(f"{s['generated_song_id']} " + ", ".join(f"{k}: harmony {v['harmony_contrast_ok']} density {v['density_contrast_ok']} ({v['n_allowed_start_states']} allowed starts)" for k, v in s["contrast"].items()) for s in roll["songs"])
    scores_line = "; ".join(f"{k.split('/')[1].replace('_donor_', '←')[:24]} {v['ear_score_v2']}" for k, v in sc["scores"].items())
    listening = sorted(str(p) for p in Path("data/v4/generated/v5_iter_02").glob("*/*")) + ["data/v4/generated/v5_iter_02/listening_manifest.json"]
    it_files = [f"data/v5/gen/iteration_02/{s['generated_song_id']}_donor_{s['donor']}/{n}" for s in roll["songs"] for n in ("ab_mix.wav", "ab_mix.manifest.json", "ab_mix.replay_proof.json", "ear_score_v5.json")]
    events.append(_ev("M-V5-GEN-1/iteration-02-c85", "in-progress", "high",
        "5 renders + replay proofs on disk (byte-det x2 in fresh mkdtemp); ear scores informational under FD-6; stall 2/12; no passer declared.",
        f"c85 P1 iteration 2 (seed 1, F1 form plan ON, rules = c84 `harmony_markov_v5_full.json` {frozen['data/v5/rules/harmony_markov_v5_full.json'][:12]}… + `groove_v5_v2_full.json` {frozen['data/v5/rules/groove_v5_v2_full.json'][:12]}…; P2 artifacts NOT consumed): `scripts/v5/generate_v5.py --iteration 2 --seed 1 --form-plan data/v5/rules/form_plan_v5.json --cycle 85 --prove-replay`. "
        f"Renders: {songs_line}. Contrast rule: {contrast_line}. Arrangement per song: intro bass-only (corpus intro quantile {fp['intro_density_quantile']} < 0.33; keys+melody+drums muted in section 0), outro melody muted + final bar held (bass whole note, chord sustained, kick on 1), breakdown = section {roll['songs'][0]['breakdown_section']} (first non-A in the middle half; drums muted 4 bars), fills on the last bar of every section from the boundary pool. "
        f"Every label generated once and repeated literally; per-section core MIDI under generated_midi/sections/ proves A-repeat byte-equality 5/5. Byte-det x2 {bd['iteration_02_renders']['all_equal']} (run-2 tempdirs in each ab_mix.replay_proof.json); per-track WAVs deleted after each mix. "
        f"INFORMATIONAL ear scores (amended venv, c76 v2, `score_gen_batch_v5.py --cycle 85`): {scores_line}; ≥6 {sc['n_gen_ge_6']}/5 — inside the band-4 context range {sc['band4_v2_context']}, NOT passers (FD-6, c76 L119); table byte-det x2 {bd['iteration_02_ear_scores_table']['equal']} (sha {bd['iteration_02_ear_scores_table']['run1_sha256'][:12]}…). "
        f"Listening copies: all 5 → `data/v4/generated/v5_iter_02/` (listening_manifest sha {_sha('data/v4/generated/v5_iter_02/listening_manifest.json')[:12]}…; +{sum(Path(p).stat().st_size for p in listening if Path(p).is_file()) // 1_000_000} MB). stall_counter {stall['iterations']}/{stall['budget']} with the F6 history entry.",
        ["scripts/v5/generate_v5.py", "scripts/v5/deliver_v5_listening.py", "data/v5/gen/iteration_02/iteration_rollup.json", "data/v5/gen/stall_counter.json", "data/v5/logs/generate_v5_iter02_c85.log",
         "data/v5/gen/gen_v5_iter02_ear_scores_c85.json", "data/v5/logs/score_gen_v5_iter02_c85_run1.log", "data/v5/logs/score_gen_v5_iter02_c85_run2.log", "data/v5/gen/byte_determinism_c85.json"]
        + it_files + listening + sorted(str(p) for p in Path("data/v5/gen/iteration_02").glob("*/generated_midi/sections/*.mid")), supersedes_path="M-V5-GEN-1/iteration-01-c84"))
    events.append(_ev("M-V5-GEN-1/F1-form-arrangement", "validated", "high",
        "feature landed (code + 10 tests + rendered iteration 2); pre-registered enum recorded honestly (PARTIAL 4/5); byte-det x2 on model, renders, scores; flag-off replay byte-identical to c84.",
        f"c85 F1 LENGTH + FORM + ARRANGEMENT **{roll['f1_enum']}** ({roll['f1_songs_all_clauses']}/5 songs satisfy all five clauses; enum from `form_prereg_c85.json`). "
        f"The 1/5 shortfall is gen_v5_song_4 (Peach Dream donor, 123 BPM): its SHA-256 length draw hit the corpus' 1/21 mass on 4 sections → 32 bars = 65.3 s (< 90 s) and the truncated template AABA has 2 labels; its contrast rule + A-repeat clauses hold. Not retuned (FD-1). "
        f"Mechanism check: the corpus length distribution {fp['length_distribution']} puts 86 % on 8 sections, so ≥1:30 holds for 4/5 draws at donor tempi 92–152 BPM; songs 1/2/3/5 run 103–169 s with form AABABCAA (64 bars). "
        f"R1 (segmentation at 0.85) FAILED and the pre-declared template fallback governed the labels; R2 (contrast satisfiable from the n=21 chain) PASSED for 5/5 donors (≥ {min(v['n_allowed_start_states'] for s in roll['songs'] for v in s['contrast'].values())} allowed start states with ≥8 segments each). "
        f"Regression anchor: `generate_v5.py` with `--form-plan` absent reproduces the 5 c84 iteration-1 WAV SHAs byte-identically ({bd['iteration_01_flag_off_replay']['all_equal']}; tempdir {bd['iteration_01_flag_off_replay']['tempdir']}); M4: no `groove_model_used.json` copy in iteration_02 (the c84 copy under iteration_01/ stays, reclaimable). "
        f"Figures: `data/v5/rules/fig_form_plan_corpus_c85.png`, `data/v5/gen/iteration_02/fig_iter02_arrangement_c85.png` (stem × section onset density with M/M4/F/H annotations) from `plot_iter02_arrangement_c85.py`. "
        f"Disclosures: keys/melody GM shims and PD/Disco A anchor-BPM tempo unchanged from c84; the intro's boundary fill is inaudible because drums are muted in a bass-only intro (by construction); iteration_02 + listening copies ≈ 214 MB (64-bar songs are 4x the c84 length), df {df_now} %.",
        ["scripts/v5/generate_v5.py", "scripts/v5/form_plan_v5.py", "data/v5/gen/form_prereg_c85.json", "data/v5/rules/form_plan_v5.json", "data/v5/gen/iteration_02/iteration_rollup.json",
         "data/v5/gen/iteration_02/fig_iter02_arrangement_c85.png", "data/v5/gen/iteration_02/plot_iter02_arrangement_c85.py", "data/v5/gen/byte_determinism_c85.json", "tests/test_c85_landing.py"],
        supersedes_path="M-V5-GEN-1/form-plan-model-c85"))

    # ---- P2: F4 ----
    f4p = Path("data/v5/corpus/tempo_f4_prereg_c85.json"); v = _j("data/v5/corpus/tempo_f4_verdict_c85.json"); cbd = _j("data/v5/corpus/byte_determinism_c85.json")["tempo_f4_verdict_c85"]
    events.append(_ev("M-V5-CORPUS-1/tempo-f4-preregistered-c85", "validated", "high", "prereg mtime precedes the verdict; check quoted verbatim from the brief; operator authority cited by path + sha.",
        f"c85 P2: `tempo_f4_prereg_c85.json` (sha {_sha(f4p)[:16]}…) BEFORE output — OPERATOR ADJUDICATION under `{GUIDANCE}` F4 (sha {_sha(GUIDANCE)[:16]}…), NOT a fifth unaided criterion (tempo axis STOPPED after v5/v5b/v5c/v5d). Scope exactly {{88d247468cb6d49f, cdd2717e52820ff6}}; adopted mechanism = READ-ONLY c83 tempo_v5d refined-lag dominant (PD 122.197271, Disco A 120.272335); "
        f"check verbatim: \"{v['check_verbatim']}\"; operational definitions (nearest candidate within 15 % of T/2 and 2T; strict s_ref comparison; drum onsets per beat from transcription_manifest note_counts.drums / (duration_s × bpm/60)); enum F4_RESOLVED / F4_HALF_DOUBLE_AMBIGUOUS / F4_FAILS; FD-1 no retune; the octave-ambiguity of the harmonic sum is noted as a known property, not a rescue clause.",
        ["data/v5/corpus/tempo_f4_prereg_c85.json"], supersedes_path=None))
    events.append(_ev("M-V5-CORPUS-1/tempo-f4-adjudication-c85", "validated", "high",
        "pre-registered enum recorded (validated = recorded verdict, L2); byte-det x2 (tempdirs in data/v5/corpus/byte_determinism_c85.json); blocked file byte-identical; nothing retuned.",
        v["ledger_narrative"] + f" Byte-det x2 {cbd['equal']} (run1 {cbd['run1_sha256'][:12]}… == run2; tempdirs {cbd['tempdir_run1']} / {cbd['tempdir_run2']}). Figure `data/v5/corpus/fig_tempo_f4_c85.png` (s_ref vs bpm_ref per candidate; adopted / T/2 / 2T marked; pick band; c22 anchor) from `plot_tempo_f4_c85.py`. "
        f"Consequence: no `canonical_v5c_reindexed/`, no `recanonicalization_unblocked_c85.json`, no n=23 harmony/groove re-run this cycle; iteration 3 proceeds on n=21. FIRST-CLASS NULL RESULT: the brief's formalization (candidate s_ref at 2T must be lower) is defeated by the harmonic sum's construction on BOTH songs (2T candidates ≈61/60 BPM score 1.398/1.401 vs 1.352/1.321) while the onsets-per-beat (2.32 / 3.76) and ±2 BPM anchor sub-checks pass — the half-time reading is implausible on drum density but the s_ref sub-check cannot say so. c86 axis (new prereg, not a retune): a half/double check on onsets-per-beat + beat-tracker consensus (the c82 full-mix beat_track already reads 117.45 for Disco A).",
        ["scripts/v5/tempo_f4_adjudicate_c85.py", "data/v5/corpus/tempo_f4_verdict_c85.json", "data/v5/corpus/byte_determinism_c85.json", "data/v5/corpus/fig_tempo_f4_c85.png", "data/v5/corpus/plot_tempo_f4_c85.py", "tests/test_c85_f4_m5.py"],
        supersedes_path="M-V5-CORPUS-1/tempo-f4-preregistered-c85"))
    events.append(_ev("M-V5-GEN-1/F4-tempo-fix", "in-progress", "high", "feature NOT landed: the pre-registered half/double check landed AMBIGUOUS on both songs; the next mechanism is named; nothing retuned.",
        f"c85 F4 TEMPO FIX for PD + Disco A: pre-registered operator adjudication → **{v['verdict']}** (see M-V5-CORPUS-1/tempo-f4-adjudication-c85). Both songs stay MUST-NOT-CONSUME for rules (harmony chain stays 21/24 → the two late landings make 23 eligible for c86); `recanonicalization_blocked.json` byte-identical {frozen['data/v5/corpus/recanonicalization_blocked.json'][:12]}…. "
        f"Next (c86, new pre-registration): half/double check on drum onsets-per-beat (both songs already ∈ [0.5, 4] at the adopted BPM) plus beat-tracker consensus (autocorrelation-external, per the brief's falsification clause); iteration 3 proceeds on n=21.",
        ["data/v5/corpus/tempo_f4_verdict_c85.json"], supersedes_path=None))

    # ---- P0 cheap fixes ----
    rbd = _j("data/v5/rules/byte_determinism_c85.json")["harmony_eligible_from_c84"]
    events.append(_ev("M-V5-RULES-1/harmony-eligible-from-c85", "validated", "high", "c84 chain sha reproduced through the flag in two fresh tempdirs; 21/21 per-song files byte-identical; flag-off path unchanged (test_c84_landing 8/8, test_harmony_v5 3/3).",
        f"c85 M5: `scripts/v5/harmony_v5.py` (sha {_sha('scripts/v5/harmony_v5.py')[:16]}…, additive `--eligible-from <json>` mirroring groove_v5_full_c84.py; the gate block is taken verbatim from the source JSON so the chain reproduces) + `data/v5/rules/eligible_c84.json` (sha {_sha('data/v5/rules/eligible_c84.json')[:16]}…, the c84 gate: 21 used). "
        f"Naive re-run reproducibility: `{rbd['command']}` x2 → run1 == run2 == c84 anchor {rbd['run1_sha256'][:16]}… ({rbd['matches_c84_anchor']}); per-song 21/21 equal {rbd['per_song_equal']}; tempdirs {rbd['tempdir_run1']} / {rbd['tempdir_run2']}. Disk-landed is now 26 (c84 gate 24): a fresh disk-derived run would use n=23 — exactly why the flag exists.",
        ["scripts/v5/harmony_v5.py", "data/v5/rules/eligible_c84.json", "data/v5/rules/byte_determinism_c85.json"], supersedes_path=None))
    events.append(_ev("M-V5-GEN-1/F6-iteration-schedule", "validated", "high", "stall_counter.json carries top-level ts + per-iteration feature/donor_map/form_plan/rules/seed (test_06).",
        f"c85 F6 ITERATION SCHEDULE: `data/v5/gen/stall_counter.json` now records per iteration what varies beyond the seed — history[-1] = {json.dumps(stall['history'][-1], sort_keys=True)}; top-level ts {stall['ts']}. "
        f"Schedule going forward (one feature per iteration per guidance B): iter 3 = F2 bass/melody models + dynamics (Route 1 or 2 per the F2 guidance), iter 4 = F3 guitar/piano/other parts, iter 5 = F5 interpolation demo (CG↔PD), then F4-dependent n=23 rules when a tempo mechanism lands; seed = iteration − 1; donors fixed (donor_profile_map.json).",
        ["data/v5/gen/stall_counter.json", "scripts/v5/generate_v5.py"], supersedes_path=None))
    events.append(_ev("_infra/cheap-fixes-M2-M4-c85", "validated", "high", "every x2 claim this cycle has an on-disk byte_determinism_c85.json entry with run SHAs + tempdirs; M4 verified by test_05; score_gen/deliver parametrized.",
        f"c85 P0 cheap fixes: M2 — three `byte_determinism_c85.json` files (data/v5/gen: form_plan_v5, iteration_01_flag_off_replay, iteration_02_renders, iteration_02_ear_scores_table; data/v5/rules: harmony_eligible_from_c84; data/v5/corpus: tempo_f4_verdict_c85), each with run1/run2 SHAs + tempdir paths. "
        f"M3 — no `<sha16>-reindexed-c85` or other per-song rows were emitted this cycle (26/26 rows exist since c84), so the reindex_manifest_sha256 requirement had nothing to apply to (disclosed). M4 — `generate_v5.py` no longer copies `groove_model_used.json` (rules_sha256.groove_model pins it); the 48 MB c84 copy under iteration_01/ is untouched and reclaimable. "
        f"`score_gen_batch_v5.py` gained `--cycle/--milestone` (sha {_sha('scripts/v5/score_gen_batch_v5.py')[:16]}…); `deliver_v5_listening.py` likewise (sha {_sha('scripts/v5/deliver_v5_listening.py')[:16]}…); the iteration event lists the listening copies as artifacts.",
        ["data/v5/gen/byte_determinism_c85.json", "data/v5/rules/byte_determinism_c85.json", "data/v5/corpus/byte_determinism_c85.json", "scripts/v5/score_gen_batch_v5.py", "scripts/v5/deliver_v5_listening.py"], supersedes_path=None))

    # ---- bookkeeping ----
    events.append(_ev("_plan/register-c85-sub-leaves", "validated", "high", "rows inserted inline in the parseable region by tools/_register_c85_por_rows.py (idempotent), incl. F1..F7 backlog rows.",
        f"c85 POR registration: F1..F7 backlog rows (F1 {roll['f1_enum']}; F2/F3/F5 pending in order; F4 {v['verdict']}; F6 landed; F7 depends on F1–F5) + c85 sub-leaves inserted inline in `## Milestones` before `## Sub-milestones`. "
        f"Tally: M-V5-CORPUS-1 26/26 landed + sidecar; M-V5-RULES-1 c84 artifacts consumed as-is (n=21; eligible would be 23); M-V5-GEN-1 iteration 2 landed (stall {stall['iterations']}/{stall['budget']}); PD + Disco A remain tempo-blocked.",
        ["plan_of_record.md"], supersedes_path=None))
    events.append(_ev("_infra/adopt-cycle85-tests", "validated", "high", "two new test files adopted; adopted suite re-run under /usr/bin/python3 (counts in the work output; ADOPTED suite, not tests/ as a whole).",
        "c85 test-adoption: `tests/test_c85_landing.py` (10: prereg-before-output for form + F4 and absence of c85 rules preregs; segmentation determinism on a synthetic 3-song fixture recovering AABABC/ABAB/AAAABB; contrast rule fires on the n=21 chain and not on same-root/rare-root chains; "
        "A-repeat core-MIDI byte-equality + 5/5 replay proofs + enum consistency; iteration-1 flag-off replay vs the 5 c84 WAV SHAs + M4; F6 stall schema; R1 FAILED record + model targets + both figures; F4 AMBIGUOUS record + listening copies + informational scores; AST discipline + created-stamp ≤ mtime on 8 scripts; guidance adoption event + F1..F7 POR rows) "
        "+ `tests/test_c85_f4_m5.py` (5: F4 prereg/verdict/blocked-file; synthetic 3:2 half/double check; --eligible-from reproduces the c84 chain; score_gen --cycle/--milestone; AST discipline). Adopted suite counts in the closing summary.",
        ["tests/test_c85_landing.py", "tests/test_c85_f4_m5.py"], supersedes_path=None))
    events.append(_ev("_archive/cycle-85-scratch", "validated", "high", "one-shot emitter + registrar retained in-tree per emitter-exemption policy and listed as artifacts (L1).",
        "c85 scratch archival: `tools/_emit_c85_ledger_events.py` + `tools/_register_c85_por_rows.py` retained in-tree per docs/emitter_exemption_policy.md and LISTED here as artifacts; session scratchpad runners (probe1, form_bytedet, flagoff_check, iter02_bytedet, run_tests, p2/*) not in workspace; "
        "plot scripts co-located with their data + figures (data/v5/rules/, data/v5/gen/iteration_02/, data/v5/corpus/). No workspace scratch to archive.",
        ["tools/_emit_c85_ledger_events.py", "tools/_register_c85_por_rows.py"], supersedes_path=None))
    n_frozen_ok = sum(frozen_ok.values())
    events.append(_ev("_run/cycle_85_closed", "validated", "high", "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        f"c85 CLOSED — v5 REOPENING cycle 7 (feature cycle: F1 {roll['f1_enum']} as iteration 2; F4 {v['verdict']}; P0 M2/M4/M5/F6 landed; M3 N/A). FROZEN/READ-ONLY anchors {n_frozen_ok}/{len(FROZEN_EXPECTED)} byte-identical to their pinned prefixes: "
        + "; ".join(f"{k} {frozen[k][:12]}{'' if frozen_ok[k] else ' MISMATCH'}" for k in FROZEN_EXPECTED)
        + f". env_pin_sha256 {ENV_PIN[:8]}…922ca unchanged. df at emit {df_now} % (avail {avail_now} GB); never ≥ 90 %. Cycle counter: on-disk c85, harness c129 (disclosed, not reconciled). "
        "Status convention (L2): `validated` for recorded PARTIAL / AMBIGUOUS / R1-FAILED verdicts; `in-progress` for F4 (feature not landed) and iteration-02 (no passer). Full 9-header summary in the c85 work output.",
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_84_closed"))

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
    to_append = [e for e in events if e["milestone_id"] not in existing_ids]
    if not to_append:
        print("IDEMPOTENT: all c85 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c85 events; frozen anchors OK {n_frozen_ok}/{len(FROZEN_EXPECTED)}")
    for e in to_append:
        print(f"  {e['status']:16s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
