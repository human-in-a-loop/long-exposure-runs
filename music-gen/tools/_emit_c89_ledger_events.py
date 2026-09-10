#!/usr/bin/python3
"""c89 (= harness c133, offset 44) one-shot ledger emitter — v5 REOPENING cycle 11: F5 interpolation demo (CG <-> PD, t = 0.5) pre-registered,
wired (`--f5` default off), rendered as the 6th song of iteration 5 (seed 4), byte-det x2 + independent process + F5-off regression, verdict;
disk prune; repo-root helper; stall 5/12; n=25 deferral; tests; POR; close.

created: 2026-09-10T03:50:00Z
cycle: 89
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _archive/cycle-89-scratch

Every event carries `agent`; event_id = UUID5(NAMESPACE_URL, canonical JSON minus event_id/ts); idempotent on (milestone_id, cycle == 89);
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
CYCLE = 89
RUN_ID = "run-2026-09-06T000000Z"
TS = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
NAMES = {"252eb21ce7df7328": "WIG", "31a164f845f8e27e": "CG", "51e433ade2a845e1": "Rome", "88d247468cb6d49f": "PD", "cdd2717e52820ff6": "Disco A"}
A, B = "31a164f845f8e27e", "88d247468cb6d49f"
DEMO = f"data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_{A}"
TEST_RESULTS = Path("data/v5/logs/test_results_c89.json")


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
    roll = _j("data/v5/gen/iteration_05/iteration_rollup.json")
    bd = _j("data/v5/gen/byte_determinism_c89.json")
    ent = bd["entries"]
    stall = _j("data/v5/gen/stall_counter.json")
    sc = _j("data/v5/gen/gen_v5_iter05_ear_scores_c89.json")
    lm = _j("data/v4/generated/v5_iter_05/listening_manifest.json")
    dm = _j("data/v4/generated/f5_interp_CG_PD_t050_c89/delivery_manifest.json")
    launch = _j("data/v5/logs/gen_iter05_c89.launch.json")
    prereg = _j("data/v5/gen/f5_prereg_c89.json")
    prune = _j("data/v5/logs/c89_prune.json")
    man = _j(f"{DEMO}/ab_mix.manifest.json")
    tests = _j(TEST_RESULTS)
    df_now, avail_now = _df()
    it5, ind, fo = ent["iteration_05_renders"], ent["iteration_05_independent_process"], ent["iteration_04_flag_off_replay"]
    post = bd["post_edit_script_sha256"]["generate_v5"]
    assert post == _sha("scripts/v5/generate_v5.py") == roll["generator_hash"], "generator image drifted after the render"
    pre = bd["turn_start_pins"]["generate_v5_pre_edit"]["sha256"]
    final = bd["f5_enum_final"]
    au = man["f5"]["audibility"]
    raw = {k: v["raw_render_rms_dbfs"] for k, v in man["f5"]["raw_render_rms_dbfs"].items()}
    it5_wavs = [f"data/v5/gen/iteration_05/{s['generated_song_id']}_donor_{s['donor']}/ab_mix.wav" for s in roll["songs"]]
    it5_art = it5_wavs + [w.replace("ab_mix.wav", "ab_mix.manifest.json") for w in it5_wavs] + [w.replace("ab_mix.wav", "ab_mix.replay_proof.json") for w in it5_wavs]
    listening = [r["dest"] + "/ab_mix.wav" for r in lm["samples"]] + ["data/v4/generated/v5_iter_05/listening_manifest.json"]
    demo_deliv = [f"data/v4/generated/f5_interp_CG_PD_t050_c89/{n}" for n in dm["copied_sha256"]] + ["data/v4/generated/f5_interp_CG_PD_t050_c89/delivery_manifest.json"]
    n_tests_pass = sum(v["n_pass_lines"] for v in tests.values())
    por_rows = [l for l in Path("plan_of_record.md").read_text().splitlines() if l.startswith("| M-V5-GEN-1/F5-interpolation-demo | G5 |")]
    assert len(por_rows) == 1 and "c89 LANDED" in por_rows[0]
    hb = man["f5"]["blend_record_sha256"]
    gb, hbl = roll["f5"]["groove_blend"]["per_table"], roll["f5"]["harmony_blend"]
    gb_txt = ", ".join(f"{k}: {v['contexts_seen_in_both']}" for k, v in gb.items())
    events = []

    events.append(_ev("_plan/guidance-continuation-c89", "validated", "high", "on-disk guidance directory scanned at turn start; no file newer than the c131 guidance.",
        f"c89 (= harness c133, offset 44): no new operator guidance file landed (newest on disk dated 2026-09-09); the c131 guidance (sha16 {_sha('docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt')[:16]}) and the F1–F7 backlog guidance "
        f"(sha16 {_sha('docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt')[:16]}) continue to govern — this cycle is F5 (interpolation demo, own prereg; c86 MINOR 7 discharged). c88 audited VALIDATED (reporter cycles 137-139 on disk, no CRITICAL/MODERATE); the c88 MINORs (a) raw-render audibility, (b) repo-root helper are closed below.",
        ["docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt", "docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt"]))

    events.append(_ev("_infra/disk-prune-c89", "validated", "high", "df read with `df -P` before and after; prune record on disk.",
        f"c89 P0 disk prune: df {prune['df_open']['used_pct']} % ({prune['df_open']['avail_gb']} GB avail) at open — above the 85 % prune threshold; pruned ONLY regenerable old-session scratchpad tempdirs under /tmp/claude-0 ({prune['pruned_mb']} MB: prior-cycle auditor/worker render tempdirs); "
        f"nothing under the workspace; /tmp/tfhub_modules (VGGish cache) and older non-session /tmp render dirs untouched. df after {prune['df_after']['used_pct']} % ({prune['df_after']['avail_gb']} GB); at emit {df_now} % ({avail_now} GB); never ≥ 90 %.", ["data/v5/logs/c89_prune.json"]))

    events.append(_ev("M-V5-GEN-1/f5-prereg-written-c89", "validated", "high", "prereg mtime precedes every iteration-5 output AND the F5 code (test_c89_landing::test_01); sha pinned in the rollup, every manifest and the byte-det record.",
        f"c89 P0: `data/v5/gen/f5_prereg_c89.json` (sha {_sha('data/v5/gen/f5_prereg_c89.json')[:16]}…, created {prereg['created']}) written BEFORE any F5 code edit or render output: donors CG ({A}) ↔ PD ({B}), t 0.5, iteration 5, seed 4; blend semantics per model — groove: t-mixture of the donor-conditioned conditional tables "
        "(each donor's own bars through the n=23 construction via READ-ONLY groove_v5_v2.load_song/table; union vocab; row_for uniform for unseen contexts), harmony: t-mixture of the donor segment-level rows over the 81 n=23 states (READ-ONLY harmony_v5.analyse_song; n=23 segment row as backoff, listed per state; counts = n_mix·row_mix so the F1 ≥ 8-segment rule reads the blended support; pi_mix = t·pi_A + (1−t)·pi_B); "
        "NO note-level mean (c78 ban); decoding = the generator's SHA-256 inverse-CDF (deviation from the brief's argmax recommendation DECLARED in the prereg — argmax collapses a Markov chain to a fixed cycle); tempo / tonic / profiles = donor A (tempi not averaged); F2 + F3 on; held-constant SHAs; frozen enum F5_LANDS / F5_PARTIAL / F5_FAILS; "
        f"raw-render audibility clauses (i) every stem raw RMS > −60 dBFS (c88 MINOR (a): measured BEFORE normalisation), (ii) |d_mix − mixture(d_A, d_B)| ≤ 2.0 drum onsets/bar, (iii) 0 < h_A, h_B < 1 and |h_A − h_B| ≤ 0.35; expected_outputs computed from the deterministic form-plan draws ({prereg['expected_outputs']['iteration_05_dir_total']} files under iteration_05 + figure + plot = {prereg['expected_outputs']['count_with_figure']}; c88 MINOR 7 closed); "
        f"iteration-4 regression targets; generator PRE {pre[:16]}… (== brief).", ["data/v5/gen/f5_prereg_c89.json", "data/v5/gen/byte_determinism_c89.json"]))

    events.append(_ev("_infra/f5-wiring-and-repo-root-helper-c89", "validated", "high", "pre/post SHAs pinned; flag-off reproduction under the post-edit image recorded ×5 for iteration 4; argparse guards tested (test_02); helper used by the plot script (test_08).",
        f"c89 P1: `scripts/v5/generate_v5.py` edited ADDITIVELY (pre {pre[:16]}… → post {post[:16]}…): `--f5` default OFF with sub-flags `--interp-a/--interp-b/--interp-t/--f5-prereg` (argparse error without `--f5`; `--f5` requires all four + `--f2 --f3 --form-plan`); with `--f5` the 5 regular songs render unchanged and ONE demo spec is appended with the blended models; "
        "manifest `f5` block (raw render RMS of every stem, density + Hamming statistics vs the A-only (t=1) / B-only (t=0) compositions on the same tags via the new `f5_compose` mirror of render_song's section composition — asserted equal to the demo's own composition, blend record); F1/F2/F3 enums over the 5 regular songs (identical list when the flag is absent). "
        f"New `scripts/v5/interpolate_v5.py` ({_sha('scripts/v5/interpolate_v5.py')[:16]}…; imported only under `--f5`; self-check on a synthetic pair) and shared `scripts/v5/repo_root.py` ({_sha('scripts/v5/repo_root.py')[:16]}…; marker walk-up; the c89 plot script uses it — c88 MINOR (b) closed, no `parents[N]` literal). "
        f"One in-cycle slip disclosed: the smoke render named the demo `t500` (t·1000); fixed to `t050` (t·100, the prereg id) before the launch; the smoke tempdir was pruned. Flag-off: iteration-4 command under the post-edit image reproduces iteration 4 {fo['n_equal']}/5 ({fo['wall_s']} s, tempdir {fo['tempdir']}). `/usr/bin/python3` guard + `created:` stamps; no PRNG; `velocity_v5.py` untouched.",
        ["scripts/v5/generate_v5.py", "scripts/v5/interpolate_v5.py", "scripts/v5/repo_root.py", "data/v5/gen/byte_determinism_c89.json", "data/v5/logs/flagoff_c89.log"]))

    events.append(_ev("M-V5-GEN-1/f5-iter05-rendered-c89", "validated", "high", "6/6 REPLAY_PROOF_HOLDS in fresh tempdirs + 6/6 equal from an independent second process under the post-edit image; scores informational only (FD-6).",
        f"c89 iteration 5 RENDERED (detached at turn start, PID {launch['pid']}, `{launch['log']}`): `{launch['generate_command']}` under generator sha {post[:16]}… — 5 regular songs (unblended n=23 models, seed 4) + the demo `{man['generated_song_id']}` (donor A profiles/tempo/tonic; groove tables + harmony chain = t=0.5 blend, record sha {hb[:16]}…). "
        f"{it5['n_equal']}/{it5['n_songs']} REPLAY_PROOF_HOLDS (in-process second render into mkdtemp); independent second process (`{ind['tempdir']}`, {ind['wall_s']} s) {ind['n_equal']}/{ind['n_songs']} equal on ab_mix + per-stem MIDI + per-track SHAs (+ f5_blend.json for the demo). "
        f"Demo ab_mix {man['ab_mix_sha256'][:16]}… ({man['ab_mix_duration_s']} s, form {''.join(man['form_plan'])}, {man['tempo_bpm']} BPM, tonic {man['tonic']} F# minor); raw render dBFS {raw}; groove density mix {au['groove']['d_mix']} vs A-only {au['groove']['d_A_only_t1']} / B-only {au['groove']['d_B_only_t0']} (expected mixture {au['groove']['expected_mixture']}, dev {au['groove']['abs_dev']} ≤ 2.0); "
        f"chord Hamming h_A {au['harmony']['h_A']} / h_B {au['harmony']['h_B']} (band 0.35); bass-kick lock mix/A/B {au['groove']['bass_kick_lock_informational']}. Blend support: groove contexts seen in both donors per table {{{gb_txt}}} "
        f"(the two donors share almost no exact groove contexts — the mixture is a union-vocab blend, disclosed); harmony states with support A {hbl['states_with_support_A']} / B {hbl['states_with_support_B']} / blended {hbl['states_with_blended_support']} of 81, n=23 backoff rows A {len(hbl['backoff_to_n23_row_for_A'])} / B {len(hbl['backoff_to_n23_row_for_B'])}. "
        f"Regular songs: F1 {roll['f1_enum']}, F2 {roll['f2']['f2_enum']}, F3 per-song {roll['f3']['n_songs_all_per_song_clauses']}/5; forms {[''.join(s['form']) for s in roll['songs']]}; durations {[s['duration_s'] for s in roll['songs']]} s. Informational ear scores (venv c76 v2; FD-6, no passer): ≥ 6 {sc['n_gen_ge_6']}/{len(sc['scores'])}, "
        f"{[round(v['ear_score_v2'], 3) for v in sc['scores'].values()]}, table ×2 {ent['iteration_05_ear_scores_table']['equal']}. Listening copies → data/v4/generated/v5_iter_05/ ({len(lm['samples'])} incl. the demo, SHA-verified); demo trio + f5_blend.json + prereg copy → data/v4/generated/f5_interp_CG_PD_t050_c89/. "
        f"Figure `data/v5/gen/fig_iter05_parts_c89.png` via `plot_iter05_parts_c89.py --out` (reference lines = the prereg clauses; repo_root helper).",
        it5_art + listening + demo_deliv + [f"{DEMO}/f5_blend.json", "data/v5/gen/iteration_05/iteration_rollup.json", "data/v5/gen/byte_determinism_c89.json", "data/v5/gen/gen_v5_iter05_ear_scores_c89.json",
                                          "data/v5/gen/fig_iter05_parts_c89.png", "data/v5/gen/plot_iter05_parts_c89.py", "data/v5/logs/gen_iter05_c89.launch.json", "data/v5/logs/gen_iter05_c89.log",
                                          "data/v5/logs/generate_v5_iter05_c89.log", "data/v5/logs/indep_c89.log"]))

    events.append(_ev("M-V5-GEN-1/f5-flagoff-regression-c89", "validated", "high", "5/5 iteration-4 SHAs reproduced in a fresh tempdir under the post-edit image (test_04).",
        f"c89 P2 flag-off regression: the iteration-4 command (seed 3, `--f2 --f3 --tempo-overrides`, no `--f5`; `--prove-replay` omitted as result-neutral) under the post-edit image {post[:16]}… reproduces the 5 c88 iteration-4 `ab_mix.wav` SHAs {fo['n_equal']}/5 ({fo['wall_s']} s, tempdir {fo['tempdir']}) — the additive edit is inert when off; iteration-4 anchors byte-identical on disk.",
        ["data/v5/gen/byte_determinism_c89.json", "data/v5/logs/flagoff_c89.log", "data/v5/gen/iteration_04/iteration_rollup.json"]))

    v_status, v_level = ("validated", "high") if final == "F5_LANDS" else ("validated", "medium")
    events.append(_ev("M-V5-GEN-1/f5-verdict-c89", v_status, v_level, f"enum {final} from the pre-registered mechanical clauses; recorded, not retuned (FD-1); ear score informational (FD-6).",
        f"c89 F5 VERDICT = **{final}**: demo byte-det ×2 — in-process replay {bd['f5_demo_byte_det_x2']['in_process_replay']}, independent process {bd['f5_demo_byte_det_x2']['independent_process']}; replay proofs 6/6; iteration-4 flag-off regression 5/5 {bd['f5_flag_off_regression_5_of_5']}; "
        f"raw-render audibility clauses {bd['f5_audibility_clauses']} (all {bd['f5_audibility_all_clauses']}). Rule: {bd['f5_enum_rule']}", ["data/v5/gen/byte_determinism_c89.json", f"{DEMO}/ab_mix.manifest.json", f"{DEMO}/ab_mix.replay_proof.json"]))

    events.append(_ev("M-V5-GEN-1/F5-interpolation-demo", v_status, v_level, f"POR-row milestone: {final} under the frozen enum; all brief §6 sufficiency items on disk; operator ear remains the only listening authority.",
        f"c89 F5 INTERPOLATION DEMO {final}: CG ↔ PD at t = 0.5, groove + harmony models blended at parameter level (no note-level mean), rendered through `generate_v5.py --f5` as the 6th song of iteration 5 with replay proof ×2 (in-process + independent process), F5-off reproduces iteration 4 5/5, raw-render audibility clauses {bd['f5_audibility_clauses']}; "
        f"delivered to data/v4/generated/f5_interp_CG_PD_t050_c89/ (+ v5_iter_05/). Decision #7 discharged; c86 MINOR 7 (own prereg) discharged. Supersedes the c85 'pending' description of this row (POR row amended additively with the verdict + SHAs).",
        ["data/v5/gen/f5_prereg_c89.json", "scripts/v5/interpolate_v5.py", "scripts/v5/generate_v5.py", f"{DEMO}/ab_mix.wav", "data/v4/generated/f5_interp_CG_PD_t050_c89/delivery_manifest.json", "tests/test_c89_landing.py"]))

    events.append(_ev("M-V5-GEN-1/stall-counter-5of12-c89", "validated", "high", "stall counter advanced by the generator; verdict stamped into the F5 history entry by bytedet_c89 (test_09).",
        f"c89 F6: `stall_counter.json` {stall['iterations']}/{stall['budget']} with the history entry {{iteration 5, cycle 89, seed 4, feature '{stall['history'][-1]['feature']}', donors CG/PD, t 0.5, form d6c14f9a… / harmony 330b9d46… / groove 57072025… / comping 01024254… / prereg {stall['history'][-1]['f5']['prereg_sha256'][:8]}… / blend {stall['history'][-1]['f5']['blend_record_sha256'][:8]}… SHAs, verdict {stall['history'][-1]['f5']['verdict']}}}; passers 0 (FD-6). "
        "Schedule after F5: F7 close docs (c90) contingent on this verdict (any enum value is closable honestly under FD-1).", ["data/v5/gen/stall_counter.json"]))

    events.append(_ev("_infra/n25-siblings-deferred-c89", "validated", "high", "one deferral line per the brief's P5 allowance; nothing consumed from it.",
        "c89 P5 (optional, wall permitting) SKIPPED: the n=25 sibling artifacts (eligible = n=23 ∪ {0e1e8f20592db366, cc0693b4a24f64b2}; harmony / groove / comping re-run, byte-det ×2, NOT consumed) roll to F7 / c90 — P0–P4 absorbed the wall budget; nothing consumed from it, nothing blocked by it.", []))

    events.append(_ev("_plan/register-c89-sub-leaves", "validated", "high", "rows inserted inline in the parseable region by tools/_register_c89_por_rows.py (idempotent, fail-closed); F5 row amended by the same tool (`--f5-amend`).",
        f"c89 POR registration: F5 row `M-V5-GEN-1/F5-interpolation-demo` amended additively with the `c89 LANDED` clause (verdict {final} + SHAs; c85 wording kept verbatim) + c89 sub-leaves inserted before `## Sub-milestones`. POR started at sha {bd['turn_start_pins']['plan_of_record_at_open']['sha256'][:16]}… (c88 close).",
        ["plan_of_record.md", "tools/_register_c89_por_rows.py"]))

    events.append(_ev("_infra/adopt-cycle89-tests", "validated", "high", "adopted suite re-run under /usr/bin/python3; counts from data/v5/logs/test_results_c89.json (ADOPTED suite, not tests/ as a whole).",
        f"c89 test-adoption: `tests/test_c89_landing.py` ({tests.get('tests/test_c89_landing.py', {}).get('n_pass_lines', '?')}/11) new — prereg mtime gate + not-future-dated + frozen enum, argparse default-off + sub-flag guards, byte-det ×2 (in-process + independent process), F5-off reproduces iteration 4, PRE/POST + module SHAs recorded, raw-render audibility statistics recomputed within the prereg bands + blend record and composition reproduced from a fresh build, "
        "expected-outputs count == disk incl. the figure, discipline scan + repo_root helper (no parents[N]), stall 5/12 + listening + demo delivery SHA-verified, verdict consistency + POR row, iteration 1–4 WAVs + READ-ONLY pins byte-identical. "
        "Re-pins (commented in place as c89 re-pins, disclosed): generator-sha pins in the c86/c87/c88 suites now assert the c88 post-edit record == the c89 turn-start pin `generate_v5_pre_edit` (chain) and the c89 post-edit record == on-disk; `test_c88_landing::test_09` stall pin `iterations == 4` → `>= 4` + history index 3 (the counter advances by design). "
        f"Adopted suite {len(tests)} files / {n_tests_pass} PASS lines; all rc=0: {all(v['rc'] == 0 for v in tests.values())}.",
        ["tests/test_c89_landing.py", "tests/test_c88_landing.py", "tests/test_c87_landing.py", "tests/test_c87_f3_gen.py", "tests/test_c86_landing.py", "data/v5/logs/test_results_c89.json"]))

    events.append(_ev("_archive/cycle-89-scratch", "validated", "high", "one-shot emitter + registrar retained in-tree per emitter-exemption policy and listed as artifacts.",
        "c89 scratch archival: `tools/_emit_c89_ledger_events.py` + `tools/_register_c89_por_rows.py` retained in-tree; pipeline runners (p0_prune_c89, p0_pins_prereg_c89, smoke_f5_c89, run_iter05_c89, launch_iter05_c89, indep_c89, flagoff_c89, deliver_f5_demo_c89, bytedet_c89, run_tests_c89) live in the session scratchpad only "
        "(their commands and outputs are pinned in byte_determinism_c89.json + the launch JSON). The smoke tempdir was pruned at launch; the independent-process, flag-off and score-run2 tempdirs under /tmp are reclaimable.", ["tools/_emit_c89_ledger_events.py", "tools/_register_c89_por_rows.py"]))

    events.append(_ev("_run/cycle_89_closed", "validated", "high", "All MANDATORY brief items landed or halt-honestly recorded; see the 9-header closing summary in the work output.",
        f"c89 CLOSED — v5 REOPENING cycle 11 (= harness c133, offset 44 disclosed, not reconciled): F5 interpolation demo pre-registered before code, `--f5` wired default-off (+ interpolate_v5.py + repo_root helper), rendered as the 6th song of iteration 5 → **{final}**; demo byte-det ×2 (in-process + independent process); F5-off reproduces iteration 4 {fo['n_equal']}/5; stall 5/12; n=25 siblings deferred to c90/F7. "
        "Disclosures (one line each): harmony decoding kept SHA-256 inverse-CDF (prereg-declared deviation from the brief's argmax); the donors share almost no exact groove contexts (union-vocab mixture); 28/81 harmony states unseen in both donors keep the uniform-row convention; the demo's drum density (13.6/bar) lies ABOVE both donors' A-only/B-only compositions (12.4 / 11.6) yet within the pre-declared ±2.0 mixture tolerance (recorded, not retuned); "
        "the in-cycle `t500` id slip fixed before launch; F2_PARTIAL stands; groove n=23 OVERFITS (0.637) and melody VOMM MEMORIZES (0.72) disclosed; GM shims on 14/15 (song, part) cells; cross-cycle stem mismatch ACCEPTED; figure/plot paths follow the brief (data/v5/gen/, not iteration_05/); df 86 % → 84 % after a 565 MB /tmp prune (never ≥ 90 %); "
        f"cycle counter c89 on disk vs c133 harness. env_pin {ENV_PIN[:8]}…922ca unchanged. df at emit {df_now} % ({avail_now} GB). Next (c90): F7 close docs (report amendment, OPERATOR_DECISIONS, codebase guide), n=25 sibling artifacts, comping slot-histogram diagnostic, WARN-trend tabulation c85 → c89.",
        ["promise_ledger.jsonl", "plan_of_record.md"], supersedes_path="_run/cycle_88_closed"))

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
        print("IDEMPOTENT: all c89 milestone_ids already present.")
        return 0
    with open(LEDGER, "a", encoding="utf-8") as f:
        for e in to_append:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    print(f"APPENDED {len(to_append)} c89 events")
    for e in to_append:
        print(f"  {e['status']:12s} {e['milestone_id']} {e['event_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
