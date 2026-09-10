#!/usr/bin/python3
"""c87 (= harness c131, offset 44) one-shot ledger emitter — v5 REOPENING cycle 9: F2 iteration 3 RENDERED + recorded (F2_PARTIAL, no retune);
F3 comping statistics + standalone builder; disclosures as one-line events; P0 fixes; tests; POR; close.

created: 2026-09-10T02:00:00Z
cycle: 87
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _archive/cycle-87-scratch

Every event carries `agent`; event_id = UUID5(NAMESPACE_URL, canonical JSON minus event_id/ts); idempotent on (milestone_id, cycle == 87);
supersedes_path str|None (c14 lemma). FAILS CLOSED (MissingArtifact) on every hard-read path. df via `df -P` (driver semantics).
Retained in-tree per docs/emitter_exemption_policy.md.
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
CYCLE = 87
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
FOCUS = ["252eb21ce7df7328", "31a164f845f8e27e", "51e433ade2a845e1", "88d247468cb6d49f", "cdd2717e52820ff6"]
NAMES = {"252eb21ce7df7328": "WIG", "31a164f845f8e27e": "CG", "51e433ade2a845e1": "Rome", "88d247468cb6d49f": "PD", "cdd2717e52820ff6": "Disco A"}
TEST_RESULTS = Path("data/v5/logs/test_results_c87.json")


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


def main() -> int:
    roll = _j("data/v5/gen/iteration_03/iteration_rollup.json")
    bd = _j("data/v5/gen/byte_determinism_c86.json")
    ent = bd["entries"]
    stall = _j("data/v5/gen/stall_counter.json")
    sc = _j("data/v5/gen/gen_v5_iter03_ear_scores_c86.json")
    lm = _j("data/v4/generated/v5_iter_03/listening_manifest.json")
    launch = _j("data/v5/logs/gen_iter03_c87.launch.json")
    prof = _j("data/v5/rules/velocity_profiles_v5.json")
    bass = _j("data/v5/rules/bass_pitch_v5.json")
    vomm = _j("data/v5/rules/melody_vomm_v5.json")
    elig = _j("data/v5/rules/eligible_c86.json")
    g23 = _j("data/v5/rules/groove_v5_v2_full_c86.json")
    comp = _j("data/v5/rules/comping_v5.json")
    bdc = _j("data/v5/rules/byte_determinism_c87_comping.json")
    tests = _j(TEST_RESULTS)
    vel = {s: _j(f"data/v5/corpus/{s}/velocity_v5/velocities.json") for s in FOCUS}
    df_now, avail_now = _df()
    f2 = roll["f2"]
    r2 = prof["R2"]
    rms = {NAMES[s["donor"]]: s.get("rms_variance_test") for s in roll["songs"]}
    it3 = ent["iteration_03_renders"]
    fo2, fo1 = ent["iteration_02_flag_off_replay"], ent["iteration_01_flag_off_replay"]
    it3_wavs = [f"data/v5/gen/iteration_03/{s['generated_song_id']}_donor_{s['donor']}/ab_mix.wav" for s in roll["songs"]]
    it3_art = it3_wavs + [w.replace("ab_mix.wav", "ab_mix.manifest.json") for w in it3_wavs] + [w.replace("ab_mix.wav", "ab_mix.replay_proof.json") for w in it3_wavs]
    listening = [r["dest"] + "/ab_mix.wav" for r in lm["samples"]] + ["data/v4/generated/v5_iter_03/listening_manifest.json"]
    n_tests_pass = sum(v["n_pass_lines"] for v in tests.values())
    cv = comp["verdict"]
    cp = comp["stats"]["pooled"]
    events = []

    events.append(_ev("M-V5-GEN-1/iteration-03-c87", "validated", "high",
        "5/5 REPLAY_PROOF_HOLDS in fresh tempdirs under the FINAL generator image; flag-off replays reproduce iteration 2 AND iteration 1 5/5; enum recorded from the prereg (F2_PARTIAL — not retuned); scores informational only (FD-6).",
        f"c87 iteration 3 RENDERED (detached at turn start, PID {launch['pid']}, `{launch['log']}`; generate wall 170.5 s): `{launch['generate_command']}` under generator sha {roll['generator_hash'][:16]}… "
        f"(== on-disk {it3['generate_v5_sha256'] == roll['generator_hash']}; serializer {it3['serializer_v5_sha256'][:16]}…; velocity_v5 {f2['models_sha256']['velocity_v5_script'][:16]}… consumed AS-IS with the five landed velocities.json "
        f"+ profiles {f2['models_sha256']['velocity_profiles'][:16]}…; rules n=21 harmony a984ee17… / groove faa0e76e… by design). 5/5 REPLAY_PROOF_HOLDS ({it3['all_equal']}); forms {[''.join(s['form']) for s in roll['songs']]}; "
        f"durations {[s['duration_s'] for s in roll['songs']]} s. F2 enum **{f2['f2_enum']}** — clauses {f2['clauses']}: velocities present 5/5, replay 5/5, frame-RMS variance ratio ≥ 1.5 on every stem {f2['n_rms_variance_pass']}/5 "
        f"(per song {rms}; drums < 1.0 on all 5 — the F2 drum velocities do NOT add frame-level dynamics over the uniform twin; keys/melody pass on some songs; bass on 4/5). FD-1: recorded, NOT retuned. "
        f"Flag-off regression under the FINAL image: iteration 2 {fo2['n_equal']}/5 (tempdir {fo2['tempdir']}), iteration 1 {fo1['n_equal']}/5 (tempdir {fo1['tempdir']}). Informational ear scores (venv c76 v2; FD-6, no passer): ≥ 6 {sc['n_gen_ge_6']}/5, "
        f"{[round(v['ear_score_v2'], 3) for v in sc['scores'].values()]}, table byte-det ×2 {ent['iteration_03_ear_scores_table']['equal']}. Listening copies → data/v4/generated/v5_iter_03/ ({len(lm['samples'])} songs, SHA-verified). "
        f"Stall {stall['iterations']}/{stall['budget']} with the F6 history entry (feature '{stall['history'][-1]['feature']}', seed 2, rules/form/donor SHAs, model SHAs). Figures `fig_velocity_profiles_c86.png` + `iteration_03/fig_iter03_velocity_c86.png` via `--out`. "
        f"Iteration 3 was rendered in c87 for the c86 milestone (the c130 worker turn ended before the render) — disclosed; the c86 `M-V5-GEN-1/iteration-03-c86` in-progress record is superseded by this line.",
        it3_art + listening + ["data/v5/gen/iteration_03/iteration_rollup.json", "data/v5/gen/byte_determinism_c86.json", "data/v5/gen/stall_counter.json", "data/v5/gen/gen_v5_iter03_ear_scores_c86.json",
                               "data/v5/rules/fig_velocity_profiles_c86.png", "data/v5/gen/iteration_03/fig_iter03_velocity_c86.png", "data/v5/logs/gen_iter03_c87.launch.json", "data/v5/logs/gen_iter03_c87.log",
                               "data/v5/logs/gen_iter03_tail_c87.launch.json", "data/v5/logs/gen_iter03_tail_c87.log", "data/v5/logs/generate_v5_iter03_c87.log", "data/v5/logs/flagoff_c87.log"],
        supersedes_path="M-V5-GEN-1/iteration-03-c86"))

    sep = ent["route1_separation"]["per_song"]
    events.append(_ev("_infra/cross-cycle-stem-sha-mismatch-accepted-c86", "validated", "high", "operator-accepted finding (c131 guidance item 2); one line, no memo, no regression bar.",
        f"Cross-cycle htdemucs_6s stem SHA mismatch vs the c79 stage cache on all 5 focus songs ({ {NAMES[s]: sep[s]['cross_cycle_x2_holds_vs_c79_cache'] for s in FOCUS} }; decoded full.wav SHAs match) ACCEPTED by the operator: "
        f"the artifacts of record are the five velocities.json ({ {NAMES[s]: sep[s]['velocities_json_sha256'][:12] for s in FOCUS} }) and their sibling MIDI SHAs — in-cycle ×2 on WIG holds (gate + run1 + run2 {ent['route1_separation']['wig_gate_run_equals_extractor_runs']}). "
        "The velocities.json wall-clock fields (separation wall_s, ts) are not anchors; the arrays + sibling MIDI SHAs are. Not chased; no memo.",
        [f"data/v5/corpus/{s}/velocity_v5/velocities.json" for s in FOCUS] + ["data/v5/gen/byte_determinism_c86.json"]))

    events.append(_ev("M-V5-RULES-1/groove-n23-c86", "validated", "high", "verdict from the c86 prereg; recorded, not tuned; consumed from iteration 4.",
        f"c86 groove re-measured at n=23 (`groove_prereg_c86.json` {g23['prereg_sha256'][:16]}…; PD/Disco A via `--tempo-overrides` from canonical_v5c_reindexed): **{g23['verdict']}** — singleton-context fraction {g23['singleton_context_fraction']} "
        f"over {g23['n_contexts']} contexts (n=21 model faa0e76e… still consumed by iteration 3 by design). Ledgered c87 as its own line (the c86 harmony event folded it in).",
        ["data/v5/rules/groove_v5_v2_full_c86.json", "data/v5/rules/groove_prereg_c86.json", "data/v5/rules/groove_v5_full_c86.py"]))

    events.append(_ev("_infra/velocity-profiles-structureless-shipped-c86", "validated", "high", "R2 diagnostics recorded from the prereg; profiles shipped as the pre-registered artifact (disclose, still ship).",
        f"DISCLOSURE: the Route-1 velocity profiles are STRUCTURELESS on the pooled drum accent diagnostic — pooled backbeat(slots 4,12) − odd = {r2['backbeat_minus_odd']} (≥ +10: {r2['backbeat_ge_plus_10']}), "
        f"drum slot-profile std {r2['drums_slot_profile_std']} (structureless < 5: {r2['structureless_std_lt_5']}), hat odd {r2['hat_odd_mean']} vs even {r2['hat_even_mean']} ({r2['hat_odd_lower_than_even']}), "
        f"bass kick-coincident {r2['bass_kick_coincident_mean']} vs non {r2['bass_non_coincident_mean']} ({r2['bass_coincident_gt_non']}). Consistent with the iteration-3 outcome (drums RMS ratio < 1.0 on 5/5). Shipped as pre-registered; not retuned.",
        ["data/v5/rules/velocity_profiles_v5.json", "data/v5/rules/fig_velocity_profiles_c86.png"]))

    events.append(_ev("_infra/bass-pitch-null-chord-skips-c86", "validated", "high", "numbers read from bass_pitch_v5.json at emit time.",
        f"DISCLOSURE: the bass interval-class model skipped {bass['n_skipped_null_chord_total']}/{bass['n_onsets_total']} = {100 * bass['n_skipped_null_chord_total'] / bass['n_onsets_total']:.1f} % of corpus bass onsets that fall on null-chord ('N') beats "
        f"({bass['n_events']} classified). The model is conditioned on the surviving half; recorded, not tuned.", ["data/v5/rules/bass_pitch_v5.json"]))

    events.append(_ev("_infra/melody-vomm-memorizes-c86", "validated", "high", "pre-declared threshold 0.5; recorded outcome.",
        f"DISCLOSURE: the melody VOMM verdict is **{vomm['verdict']}** — order-3 singleton-context fraction {vomm['order_stats']['3']['singleton_context_fraction']} (> 0.5): the order-3 model reproduces corpus runs rather than generalising; "
        "iteration-3 melodies are therefore closer to recombined corpus fragments than to a learned style. Recorded, not tuned.", ["data/v5/rules/melody_vomm_v5.json"]))

    events.append(_ev("_infra/eligible-c86-late-landed-deferred", "validated", "high", "derivation quoted from eligible_c86.json.",
        f"DISCLOSURE: n=23 = c84's 21 + PD + Disco A DEFERS two late-landed songs (0e1e8f20592db366, cc0693b4a24f64b2; disk-derived eligibility is 25) so the n=23 vs n=21 diff attributes every change to the F4 unblock; "
        f"the F3 comping statistics also ran on this n=23 set. Adding them is a one-command n=25 follow-up. Derivation: {elig['derivation'][:300]}", ["data/v5/rules/eligible_c86.json"]))

    events.append(_ev("_infra/cheap-fixes-P0-c87", "validated", "high", "each fix verified by a test (tests/test_c87_landing.py::test_06/07, test_c86_landing::test_02/08) or a recorded SHA.",
        f"c87 P0 (BEFORE the launch so the recorded script SHAs are final): `created:` stamps fixed on the three unpinned files (`scripts/v5/midi_from_json_events_v5.py` → sha {_sha('scripts/v5/midi_from_json_events_v5.py')[:16]}…, "
        f"`plot_velocity_profiles_c86.py`, `plot_iter03_velocity_c86.py`); `/usr/bin/python3` guard added to the sibling serializer (56/56 byte-equality vs c4 re-run after the edit); `scripts/v5/velocity_v5.py` NOT edited (sha dd94336d… pinned inside every velocities.json) — "
        f"test_c86_landing::test_08 tolerates its 36 s stamp skew at 120 s for that file only; `generate_v5.py` (sha {_sha('scripts/v5/generate_v5.py')[:16]}…) gained a one-line argparse error for `--velocity-mode f2` / `--rms-variance-test` without `--f2` (flag-off output unchanged: iteration 2 + 1 SHAs reproduced); "
        "the iter03 plot script's repo-root path (one parent short) fixed after it failed in the pipeline head (tail re-launched detached); emitters/registrars fail closed (MissingArtifact) and read test results from `data/v5/logs/test_results_c87.json`; df via `df -P` (driver semantics) not os.statvfs.",
        ["scripts/v5/midi_from_json_events_v5.py", "scripts/v5/generate_v5.py", "data/v5/rules/plot_velocity_profiles_c86.py", "data/v5/gen/iteration_03/plot_iter03_velocity_c86.py", "tools/_emit_c86_ledger_events.py", "tools/_register_c86_por_rows.py", "tests/test_c86_landing.py"]))

    events.append(_ev("M-V5-RULES-1/comping-stats-c87", "validated", "high", "prereg before the run (mtime asserted); enum from the prereg thresholds; byte-det ×2 with the script sha; figure + --out plot; 5 tests (teammate-built, lead-verified).",
        f"c87 F3 comping statistics `scripts/v5/comping_v5.py` (sha {bdc['script_sha256'][:16]}…) → `data/v5/rules/comping_v5.json` (sha {bdc['run1_sha256'][:16]}…, byte-det ×2 {bdc['equal']}) on the n=23 eligible set (guitar + piano + other; "
        f"`--tempo-overrides` → PD/Disco A from canonical_v5c_reindexed; deferred pair not used): **{cv['enum']}** — {cv['n_songs_with_ge_16_pooled_bars']}/23 songs contribute ≥ 16 pooled bars, pooled max 16th-slot mass {cv['pooled_max_slot_mass']} (< 0.5). "
        f"Pooled: {cp['n_bars']} bars, {cp['n_onset_groups']} onset groups, {cp['onset_density_onsets_per_bar']} onsets/bar, chord size {cp['chord_size_mean']}, sustain {cp['sustain_ratio']} beats; per stem guitar 21 songs / 1381 bars, piano 17 / 641, other 20 / 1243. "
        f"DISCLOSURE: the 16th-slot histograms are NEAR-UNIFORM (pooled {min(cp['slot16_histogram'])}..{max(cp['slot16_histogram'])} vs 0.0625) — the < 0.5 criterion is met trivially and carries little metrical evidence (plausibly bpm drift over full-length songs with no per-bar beat tracking + no drum phase alignment); "
        f"the IOI histogram is strongly structured ({cp['ioi16_histogram'][0]:.3f} at one 16th, {cp['ioi16_histogram'][1]:.3f} at two) and is what the builder uses. ~12.8 % unpaired starts excluded from sustain only. Prereg `comping_prereg_c87.json` ({_sha('data/v5/rules/comping_prereg_c87.json')[:16]}…) mtime < outputs. "
        f"Figure `fig_comping_v5_c87.png` + `plot_comping_v5_c87.py --out`. Tests `tests/test_c87_comping.py` {tests.get('tests/test_c87_comping.py', {}).get('n_pass_lines', '?')}/5.",
        ["scripts/v5/comping_v5.py", "data/v5/rules/comping_v5.json", "data/v5/rules/comping_prereg_c87.json", "data/v5/rules/byte_determinism_c87_comping.json", "data/v5/rules/fig_comping_v5_c87.png", "data/v5/rules/plot_comping_v5_c87.py", "tests/test_c87_comping.py"]))

    events.append(_ev("M-V5-GEN-1/F3-guitar-piano-other", "in-progress", "medium", "statistics + standalone builder landed and tested; the generator flag is deferred (enum F3_FLAG_WIRING_DEFERRED_c88) to keep the pinned iteration-3 generator image final.",
        f"c87 F3 GUITAR / PIANO / OTHER: comping statistics landed ({cv['enum']}, `M-V5-RULES-1/comping-stats-c87`) and a STANDALONE comping event builder `scripts/v5/comping_gen_v5.py` (sha {_sha('scripts/v5/comping_gen_v5.py')[:16]}…: per-bar IOI walk sampled by SHA-256 inverse-CDF from the stem's 16th-IOI histogram, "
        f"chord-tone voicings of round(chord_size_mean) capped at 6, duration min(sustain, ioi), 'N' bars rest, F2 velocity hook; canonical event schema serialized byte-equal by the c4 and v5 serializers; tests `tests/test_c87_f3_gen.py` {tests.get('tests/test_c87_f3_gen.py', {}).get('n_pass_lines', '?')}/4). "
        f"DEVIATION from the brief's P5 (disclosed): the `--f3` default-off flag was NOT wired into `scripts/v5/generate_v5.py` this cycle — doing so would change the generator sha pinned by the iteration-3 rollup, the byte-determinism record and the listening manifests rendered ~15 min earlier, and re-proving flag-off under a third image did not fit the turn; "
        f"enum **F3_FLAG_WIRING_DEFERRED_c88**. c88: wire `--f3` (default off; flag-off must reproduce the iteration-3 SHAs) + render iteration 4 on the n=23 chain with GM shims (guitar 27 / piano 0 / other 89) or donor profiles where present. The near-uniform slot histogram is NOT used by the builder (IOI walk instead) — disclosed.",
        ["scripts/v5/comping_gen_v5.py", "tests/test_c87_f3_gen.py", "data/v5/rules/comping_v5.json"]))

    events.append(_ev("_plan/register-c87-sub-leaves", "validated", "high", "rows inserted inline in the parseable region by tools/_register_c87_por_rows.py (idempotent, fail-closed); the c86 rows by the patched c86 registrar (route row renamed to the ledgered id).",
        f"c87 POR registration: c86 sub-leaves (15 rows, `tools/_register_c86_por_rows.py`; route row id `M-V5-GEN-1/F2-route-decided-c86`) + c87 sub-leaves (`tools/_register_c87_por_rows.py`) inserted before `## Sub-milestones`. "
        f"POR started byte-identical to commit d8af1dcc (sha a1ed63a37a663bef…). F3 row `M-V5-GEN-1/F3-guitar-piano-other` (c85) reused — no duplicate row.", ["plan_of_record.md", "tools/_register_c86_por_rows.py", "tools/_register_c87_por_rows.py"]))

    events.append(_ev("_infra/adopt-cycle87-tests", "validated", "high", "adopted suite re-run under /usr/bin/python3; counts from data/v5/logs/test_results_c87.json (ADOPTED suite, not tests/ as a whole).",
        f"c87 test-adoption: `tests/test_c87_landing.py` ({tests.get('tests/test_c87_landing.py', {}).get('n_pass_lines', '?')}/10) + `tests/test_c87_comping.py` ({tests.get('tests/test_c87_comping.py', {}).get('n_pass_lines', '?')}/5) + `tests/test_c87_f3_gen.py` ({tests.get('tests/test_c87_f3_gen.py', {}).get('n_pass_lines', '?')}/4) new; "
        f"`tests/test_c86_landing.py` re-pinned to the c87 render ({tests.get('tests/test_c86_landing.py', {}).get('n_pass_lines', '?')}/10: cycle 87, flag-off record schema, F2_PARTIAL live test asserts reproduction not passing, null degenerate flag on empty stems, single route event), `tests/test_c86_f4_close.py` {tests.get('tests/test_c86_f4_close.py', {}).get('n_pass_lines', '?')}/6, "
        f"`tests/test_c86_f2_models.py` {tests.get('tests/test_c86_f2_models.py', {}).get('n_pass_lines', '?')}/5, `tests/test_c85_landing.py` {tests.get('tests/test_c85_landing.py', {}).get('n_pass_lines', '?')}/10 (stall test re-pinned to history[1]), `tests/test_c85_f4_m5.py` {tests.get('tests/test_c85_f4_m5.py', {}).get('n_pass_lines', '?')}/5, "
        f"`tests/test_c84_landing.py` {tests.get('tests/test_c84_landing.py', {}).get('n_pass_lines', '?')}/8. Adopted suite {len(tests)} files / {n_tests_pass} PASS lines; all rc=0: {all(v['rc'] == 0 for v in tests.values())}. Every re-pin is commented in place as a c87 re-pin (disclosed).",
        ["tests/test_c87_landing.py", "tests/test_c87_comping.py", "tests/test_c87_f3_gen.py", "tests/test_c86_landing.py", "tests/test_c85_landing.py", "data/v5/logs/test_results_c87.json"]))

    events.append(_ev("_archive/cycle-87-scratch", "validated", "high", "one-shot emitters + registrar retained in-tree per emitter-exemption policy and listed as artifacts.",
        "c87 scratch archival: `tools/_emit_c87_early_events.py` + `tools/_emit_c87_ledger_events.py` + `tools/_register_c87_por_rows.py` retained in-tree; pipeline runners (run_iter03_c87, run_iter03_tail_c87, flagoff_c87, bytedet_gen_c87, launch_*, run_tests_c87) live in the session scratchpad only "
        "(their commands and outputs are pinned in byte_determinism_c86.json + the launch JSONs). Stale /tmp tempdirs from ×2 runs are reclaimable.",
        ["tools/_emit_c87_early_events.py", "tools/_emit_c87_ledger_events.py", "tools/_register_c87_por_rows.py"]))

    events.append(_ev("_run/cycle_87_closed", "validated", "high", "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        f"c87 CLOSED — v5 REOPENING cycle 9 (= harness c131, offset 44 disclosed, not reconciled): F2 iteration 3 rendered and recorded **{f2['f2_enum']}** (RMS-variance {f2['n_rms_variance_pass']}/5; no retune; flag-off ×2 sets 10/10); F4 CLOSED (early trio); "
        f"F3 comping statistics {cv['enum']} + standalone builder, `--f3` wiring deferred to c88; disclosures ledgered as one-line events (structureless profiles, 52.7 % bass null-chord skips, VOMM MEMORIZES 0.7206, n=23 defers two songs, cross-cycle stem mismatch ACCEPTED, velocities wall-clock fields non-anchors). "
        f"env_pin {ENV_PIN[:8]}…922ca unchanged. df at emit {df_now} % (avail {avail_now} GB, driver semantics); never ≥ 90 %. Next (c88): wire `--f3`, iteration 4 on the n=23 chain, F5 prereg.",
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_86_closed"))

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
    for e in events:
        assert e["agent"] == "worker" and isinstance(e["supersedes_path"], (str, type(None)))
        for a in e["artifacts"]:
            if not Path(a).exists():
                raise MissingArtifact(f"{e['milestone_id']}: {a}")
    existing = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("cycle") == CYCLE:
                existing.add(row.get("milestone_id"))
    to_append = [e for e in events if e["milestone_id"] not in existing]
    if "--dry-run" in sys.argv:
        print(f"DRY RUN: {len(events)} events validated; would append {[e['milestone_id'] for e in to_append]}")
        return 0
    if not to_append:
        print("IDEMPOTENT: all c87 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c87 events")
    for e in to_append:
        print(f"  {e['status']:12s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
