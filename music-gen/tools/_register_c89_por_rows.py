#!/usr/bin/python3
"""c89 one-shot POR registrar (two idempotent phases): `--f5-amend` appends the `c89 LANDED` clause (verdict + SHAs) to the existing
`M-V5-GEN-1/F5-interpolation-demo` row (additive text only; the c85 wording is kept verbatim); default phase inserts the c89 sub-leaf
rows inline in the `## Milestones` parseable region (before `## Sub-milestones`). Fail-closed on missing artifacts.

created: 2026-09-10T03:45:00Z
cycle: 89
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _plan/register-c89-sub-leaves
"""
import hashlib
import json
import os
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")
F5_ROW = "| M-V5-GEN-1/F5-interpolation-demo | G5 |"
A, B = "31a164f845f8e27e", "88d247468cb6d49f"
DEMO = f"data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_{A}"


class MissingArtifact(FileNotFoundError):
    pass


def j(p):
    if not Path(p).exists():
        raise MissingArtifact(str(p))
    return json.loads(Path(p).read_text())


def sha(p):
    if not Path(p).exists():
        raise MissingArtifact(str(p))
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def amend_f5() -> int:
    bd = j("data/v5/gen/byte_determinism_c89.json")
    man = j(f"{DEMO}/ab_mix.manifest.json")
    fo = bd["entries"]["iteration_04_flag_off_replay"]
    au = man["f5"]["audibility"]
    clause = (f" **c89 LANDED (= harness c133)**: pre-registered in `data/v5/gen/f5_prereg_c89.json` ({sha('data/v5/gen/f5_prereg_c89.json')[:16]}…) BEFORE any code or output; "
              f"blend = t-weighted MODEL-PARAMETER mixture of the two donor-conditioned models (groove tables + harmony segment rows over the n=23 state set, n=23 row backoff; "
              f"`scripts/v5/interpolate_v5.py` {sha('scripts/v5/interpolate_v5.py')[:16]}…; no note-level mean; SHA-256 inverse-CDF sampling; tempo/tonic/profiles = donor A); rendered as the 6th song of iteration 5 "
              f"(seed 4, generator {bd['post_edit_script_sha256']['generate_v5'][:16]}…, pre {bd['turn_start_pins']['generate_v5_pre_edit']['sha256'][:16]}…): demo `ab_mix.wav` {man['ab_mix_sha256'][:16]}… "
              f"({man['ab_mix_duration_s']} s, {''.join(man['form_plan'])}, {man['tempo_bpm']} BPM) byte-det ×2 in-process {bd['f5_demo_byte_det_x2']['in_process_replay']} + independent process {bd['f5_demo_byte_det_x2']['independent_process']}; "
              f"F5-off (iteration-4 command) reproduces iteration 4 {fo['n_equal']}/5; raw-render audibility clauses {au['clauses']} (density mix {au['groove']['d_mix']} vs A {au['groove']['d_A_only_t1']} / B {au['groove']['d_B_only_t0']}; "
              f"Hamming h_A {au['harmony']['h_A']} / h_B {au['harmony']['h_B']}) → **{bd['f5_enum_final']}**. Delivered to `data/v4/generated/f5_interp_CG_PD_t050_c89/` + `v5_iter_05/`. Decision #7 discharged; c86 MINOR 7 (own prereg) discharged.")
    lines = POR.read_text().splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if l.startswith(F5_ROW)]
    assert len(hits) == 1, hits
    i = hits[0]
    if "c89 LANDED" in lines[i]:
        print("IDEMPOTENT: F5 row already amended")
        return 0
    cells = lines[i].rstrip("\n").split(" | ")
    assert len(cells) == 5, len(cells)
    cells[2] = cells[2] + clause
    lines[i] = " | ".join(cells) + "\n"
    POR.write_text("".join(lines))
    print(f"F5 row amended at line {i + 1}")
    return 0


def register() -> int:
    roll = j("data/v5/gen/iteration_05/iteration_rollup.json")
    bd = j("data/v5/gen/byte_determinism_c89.json")
    ent = bd["entries"]
    stall = j("data/v5/gen/stall_counter.json")
    sc = j("data/v5/gen/gen_v5_iter05_ear_scores_c89.json")
    prune = j("data/v5/logs/c89_prune.json")
    man = j(f"{DEMO}/ab_mix.manifest.json")
    fo, it5, ind = ent["iteration_04_flag_off_replay"], ent["iteration_05_renders"], ent["iteration_05_independent_process"]
    final = bd["f5_enum_final"]
    au = man["f5"]["audibility"]
    post = bd["post_edit_script_sha256"]["generate_v5"][:16]
    raw_txt = ", ".join(f"{k}: {v['raw_render_rms_dbfs']}" for k, v in man["f5"]["raw_render_rms_dbfs"].items())
    rows = [
     ("_plan/guidance-continuation-c89", "G1", "c89 (= harness c133): no new operator guidance file landed (newest on disk dated 2026-09-09); the c131 guidance (sha16 fed27e550e9f7c75) + the F1–F7 backlog guidance (sha16 cf7296cfcf70c277) continue to govern — this cycle is F5 (interpolation demo, own prereg; c86 MINOR 7 discharged).", "One line; guidance SHAs quoted.", "—"),
     ("_infra/disk-prune-c89", "G1", f"c89 P0: df {prune['df_open']['used_pct']} % ({prune['df_open']['avail_gb']} GB avail, `df -P`) at open; pruned ONLY regenerable old-session scratchpad tempdirs under /tmp/claude-0 ({prune['pruned_mb']} MB: prior-cycle auditor/worker render tempdirs); nothing under the workspace, /tmp/tfhub_modules (VGGish cache) untouched; df after {prune['df_after']['used_pct']} % ({prune['df_after']['avail_gb']} GB); never ≥ 90 %.", "Record at data/v5/logs/c89_prune.json.", "—"),
     ("M-V5-GEN-1/f5-prereg-written-c89", "G5", f"c89 P0: `data/v5/gen/f5_prereg_c89.json` (sha {sha('data/v5/gen/f5_prereg_c89.json')[:16]}…) written BEFORE any F5 code edit or render output (mtime gate test-asserted over every iteration-5 file + the new code): donors CG ↔ PD, t 0.5, seed 4, blend semantics per model (groove: t-mixture of donor-conditioned conditional tables over the union vocab; harmony: t-mixture of donor segment rows over the 81 n=23 states with n=23 row backoff; NO note-level mean; decoding = SHA-256 inverse-CDF — deviation from the brief's argmax recommendation declared), demo policy (tempo/tonic/profiles = donor A; F2 + F3 on), held-constant SHAs, frozen enum F5_LANDS / F5_PARTIAL / F5_FAILS, raw-render audibility clauses (i) every stem raw RMS > −60 dBFS, (ii) |d_mix − mixture(d_A, d_B)| ≤ 2.0 onsets/bar, (iii) 0 < h_A, h_B < 1 and |h_A − h_B| ≤ 0.35, expected_outputs computed from the deterministic form-plan draws ({j('data/v5/gen/f5_prereg_c89.json')['expected_outputs']['iteration_05_dir_total']} files + figure), iteration-4 regression targets, generator PRE 3d0f3a24….", "Prereg mtime < every iteration-5 output and the F5 code.", "M-V5-GEN-1/F5-interpolation-demo"),
     ("_infra/f5-wiring-and-repo-root-helper-c89", "G1", f"c89 P1: `scripts/v5/generate_v5.py` edited ADDITIVELY (pre 3d0f3a24c2b87ed9… → post {post}…): `--f5` default OFF with sub-flags `--interp-a/--interp-b/--interp-t/--f5-prereg` (argparse error without `--f5`; `--f5` requires all four + `--f2 --f3 --form-plan`), one extra demo spec rendered with the blended models, manifest `f5` block (raw render RMS of every stem, density + Hamming statistics vs the A-only/B-only compositions on the same tags, blend record), F1/F2/F3 enums over the 5 regular songs; new `scripts/v5/interpolate_v5.py` ({sha('scripts/v5/interpolate_v5.py')[:16]}…, imported only under `--f5`) + shared `scripts/v5/repo_root.py` ({sha('scripts/v5/repo_root.py')[:16]}…) used by the c89 plot script (c88 MINOR (b)); flag-off: iteration-4 command under the post-edit image reproduces iteration 4 {fo['n_equal']}/5 (tempdir {fo['tempdir']}).", "Post-edit sha pinned; flag-off SHAs reproduced.", "—"),
     ("M-V5-GEN-1/f5-iter05-rendered-c89", "G5", f"c89 iteration 5 RENDERED (seed 4; `--f2 --velocity-mode f2 --f3 --tempo-overrides --f5 --interp-a CG --interp-b PD --interp-t 0.5 --prove-replay --cycle 89`): 5 regular songs + the demo `gen_v5_interp_CG_PD_t050` = {it5['n_equal']}/{it5['n_songs']} REPLAY_PROOF_HOLDS in fresh tempdirs; independent second process {ind['n_equal']}/{ind['n_songs']} equal (ab_mix + per-stem MIDI + per-track + f5_blend.json); demo ab_mix {man['ab_mix_sha256'][:16]}… ({man['ab_mix_duration_s']} s, {''.join(man['form_plan'])}, {man['tempo_bpm']} BPM, tonic {man['tonic']} F# minor); raw render dBFS {{{raw_txt}}}; density mix {au['groove']['d_mix']} vs A {au['groove']['d_A_only_t1']} / B {au['groove']['d_B_only_t0']}; Hamming h_A {au['harmony']['h_A']} / h_B {au['harmony']['h_B']}; F1 {roll['f1_enum']}, F2 {roll['f2']['f2_enum']}, F3 per-song {roll['f3']['n_songs_all_per_song_clauses']}/5 on the regular songs; informational scores ≥ 6 {sc['n_gen_ge_6']}/{len(sc['scores'])} (FD-6); listening copies → `data/v4/generated/v5_iter_05/` (6) + demo → `f5_interp_CG_PD_t050_c89/`; figure `data/v5/gen/fig_iter05_parts_c89.png` via `plot_iter05_parts_c89.py --out` (repo_root helper).", "6 renders + proofs + independent x2 + listening + demo delivery + figure on disk.", "M-V5-GEN-1/F5-interpolation-demo"),
     ("M-V5-GEN-1/f5-flagoff-regression-c89", "G5", f"c89 P2 flag-off regression: the iteration-4 command (seed 3, `--f2 --f3 --tempo-overrides`, no `--f5`, `--prove-replay` omitted as result-neutral) under the post-edit image {post}… reproduces the 5 iteration-4 `ab_mix.wav` SHAs {fo['n_equal']}/5 ({fo['wall_s']} s, tempdir {fo['tempdir']}) — the additive edit is inert when off.", "5/5 recorded in byte_determinism_c89.json.", "M-V5-GEN-1/F5-interpolation-demo"),
     ("M-V5-GEN-1/f5-verdict-c89", "G5", f"c89 F5 VERDICT = **{final}** from the frozen enum: demo byte-det ×2 in-process {bd['f5_demo_byte_det_x2']['in_process_replay']} + independent process {bd['f5_demo_byte_det_x2']['independent_process']}; flag-off 5/5 {bd['f5_flag_off_regression_5_of_5']}; raw-render audibility clauses {bd['f5_audibility_clauses']} (all {bd['f5_audibility_all_clauses']}). Recorded, not retuned (FD-1); ear score informational (FD-6).", "Verdict ∈ enum; consistent with the mechanical clauses.", "M-V5-GEN-1/F5-interpolation-demo"),
     ("M-V5-GEN-1/stall-counter-5of12-c89", "G5", f"c89 F6: `stall_counter.json` {stall['iterations']}/{stall['budget']} with the history entry {{iteration 5, cycle 89, seed 4, feature 'F5 interpolation demo', donors CG/PD, t 0.5, form/harmony/groove/comping/prereg/blend SHAs, verdict {stall['history'][-1]['f5']['verdict']}}}; passers 0 (FD-6, no passer declared).", "Schema present on the new history entry.", "M-V5-GEN-1/F6-iteration-schedule"),
     ("_infra/n25-siblings-deferred-c89", "G1", "c89 P5 (optional, wall permitting) SKIPPED in one line: the n=25 sibling artifacts (eligible = n=23 ∪ {0e1e8f20592db366, cc0693b4a24f64b2}; harmony / groove / comping byte-det ×2, not consumed) roll to F7 / c90 — P0–P4 absorbed the wall budget; nothing consumed from it, nothing blocked by it.", "One deferral line; no artifact.", "—"),
     ("_plan/register-c89-sub-leaves", "G1", "c89 POR registration row: F5 row amendment (`--f5-amend`, additive `c89 LANDED` clause with verdict + SHAs) + c89 sub-leaves inserted inline via `tools/_register_c89_por_rows.py` (idempotent; fail-closed).", "Rows added.", "—"),
     ("_infra/adopt-cycle89-tests", "G1", "c89 test-adoption: `tests/test_c89_landing.py` (11) new — prereg mtime gate + not-future-dated + enum, argparse default-off + sub-flag guards, byte-det ×2 (in-process + independent process), F5-off reproduces iteration 4, PRE/POST + module SHAs recorded, raw-render audibility statistics within the prereg bands + blend reproducible from a fresh build, expected-outputs count == disk incl. figure, discipline scan + repo_root helper, stall 5/12 + listening + demo delivery, verdict consistency + POR row, iteration 1–4 + READ-ONLY pins byte-identical; c88 stall pin re-pinned (≥ 4 / history index, disclosed); adopted suite re-run under /usr/bin/python3 (counts in the work output).", "New tests green + regression green.", "—"),
     ("_archive/cycle-89-scratch", "G1", "c89 scratch archival: `tools/_emit_c89_ledger_events.py` + `tools/_register_c89_por_rows.py` retained in-tree per the emitter-exemption pattern; pipeline runners (p0_prune / p0_pins_prereg / smoke_f5 / run_iter05 / launch / indep / flagoff / deliver_f5_demo / bytedet / run_tests) in the session scratchpad only (commands pinned in byte_determinism_c89.json + the launch JSON); the smoke tempdir pruned at launch.", "No workspace scratch to archive.", "—"),
     ("_run/cycle_89_closed", "G1", f"c89 CLOSED — v5 REOPENING cycle 11 (= harness c133): F5 interpolation demo pre-registered, wired (`--f5` default off), rendered as the 6th song of iteration 5 and verdicted **{final}**; F5-off reproduces iteration 4 {fo['n_equal']}/5; stall 5/12; n=25 siblings deferred to c90/F7. See the ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c89 POR rows present")
        return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    sys.exit(amend_f5() if "--f5-amend" in sys.argv else register())
