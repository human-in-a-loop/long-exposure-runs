#!/usr/bin/python3
"""c85 one-shot POR registration: insert the F1..F7 backlog rows + c85 sub-leaf rows inline in the `## Milestones` parseable region
(before `## Sub-milestones`). Idempotent; re-runnable (adds only missing rows). Retained in-tree per c14+ emitter-exemption pattern."""
import json, os
from pathlib import Path
os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")


def j(p):
    return json.loads(Path(p).read_text())


def main() -> int:
    roll = j("data/v5/gen/iteration_02/iteration_rollup.json"); fp = j("data/v5/rules/form_plan_v5.json"); v = j("data/v5/corpus/tempo_f4_verdict_c85.json")
    stall = j("data/v5/gen/stall_counter.json"); sc = j("data/v5/gen/gen_v5_iter02_ear_scores_c85.json")
    rbd = j("data/v5/rules/byte_determinism_c85.json")["harmony_eligible_from_c84"]
    r1 = fp["R1"]["focus_songs"]
    G = "docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt"
    rows = [
     ("_plan/adopt-operator-guidance-2026-09-09-F1-F7", "G1", f"c85 adoption of OPERATOR GUIDANCE 2026-09-09 (`{G}`, sha cf7296cfcf70c277…): the ear ≥6 count is NOT the progress gate; iterations 2..12 are FEATURE iterations (F1 length/form/arrangement → F2 bass/melody/dynamics → F3 guitar/piano/other → F4 tempo fix PD/Disco A → F5 interpolation demo → F6 iteration schedule → F7 close docs); every worker cycle lands one feature (code + test + rendered iteration to data/v4/generated/v5_iter_NN/); determinism/no-PRNG/env pins/replay proofs/frozen v4 unchanged. F2 velocity-source disclosure (MuScriptor starts carry no velocity; no full-length stems survive) recorded in the ledger event; the operator's F2 velocity guidance (Route 1 / Route 2) governs the F2 cycle.", "Guidance quoted verbatim in the ledger event; F1..F7 rows below.", "—"),
     ("M-V5-GEN-1/F1-form-arrangement", "G5", f"c85 F1 LENGTH + FORM + ARRANGEMENT landed as iteration 2 (seed 1; c84 rules): pre-registered `form_prereg_c85.json`; corpus form-plan model `scripts/v5/form_plan_v5.py` → `form_plan_v5.json` (n=21; length distribution {fp['length_distribution']}; R1 at the fixed 0.85 threshold FAILED — CG `{r1['31a164f845f8e27e']['form']}`, Rome `{r1['51e433ade2a845e1']['form']}`, WIG `{r1['252eb21ce7df7328']['form']}` — so the pre-declared template A A B A B C A A truncated to the corpus-drawn length governs labels); every label generated once and repeated literally (core-MIDI byte-equality); contrast rule (harmony start root ≠ A's dominant root at ≥8 segments; drum-density tercile ≠ A's via an 8-candidate filter) TRUE for every non-A section 5/5; arrangement intro (bass-only; corpus intro quantile {fp['intro_density_quantile']}) / outro (melody muted, final bar held) / breakdown (first non-A in the middle half, drums muted 4 bars) / fills (boundary pool of {len(fp['boundary_fill_pool'])}). Enum **{roll['f1_enum']}** ({roll['f1_songs_all_clauses']}/5): song 4 drew 4 sections (32 bars, 65 s < 90 s, 2 labels). 5/5 REPLAY_PROOF_HOLDS; flag-off replay reproduces the 5 c84 WAV SHAs. Informational scores ≥6 {sc['n_gen_ge_6']}/5 (not passers, FD-6).", "Prereg < outputs; enum recorded from the prereg; 5 renders byte-det x2; iteration-1 WAVs byte-identical with the flag off; both figures on disk; listening copies delivered; stall 2/12.", "M-V5-GEN-1"),
     ("M-V5-GEN-1/F2-bass-melody-dynamics", "G5", "F2 BASS LINE + MELODY MODELS WITH DYNAMICS (pending, c86 iteration 3): bass pitch model conditioned on chord (root/5th/octave/approach) from corpus bass MIDI; melody VOMM over scale degrees + onset rhythm from melodic stems; register profile per song; dynamics via Route 1 (stem-audio RMS at onsets, 5 focus songs, score-and-delete) or Route 2 (rule-based accent model from groove_v5_v2_full.json) per `docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt` — decided in the first 10 minutes of the F2 cycle, one ledger line. Disclosure: MuScriptor start events carry no velocity and no full-length stem audio survives the stage cache.", "Velocities present in generated MIDI for all stems; rendered iteration using them; test that uniform-velocity and F2 renders differ in per-stem RMS variance.", "M-V5-GEN-1/F1-form-arrangement"),
     ("M-V5-GEN-1/F3-guitar-piano-other", "G5", "F3 GUITAR / PIANO / OTHER PARTS (pending, c87 iteration 4): emit guitar and/or piano parts through donor pinned profiles where present (Rome piano/other, Disco A guitar/piano, CG guitar), else GM shim; comping rhythm from corpus guitar/piano onset stats.", "Parts present in generated MIDI + rendered iteration + replay proof.", "M-V5-GEN-1/F2-bass-melody-dynamics"),
     ("M-V5-GEN-1/F4-tempo-fix", "G5", f"F4 TEMPO FIX for Peach Dream + Disco A: c85 pre-registered operator adjudication (`tempo_f4_prereg_c85.json`; adopted mechanism = READ-ONLY c83 tempo_v5d refined-lag dominant PD 122.197271 / Disco A 120.272335; check = T/2 and 2T refined candidates both lower under s_ref AND drum onsets/beat ∈ [0.5,4] AND within ±2 BPM of the c22 anchor) → **{v['verdict']}**: onsets/beat 2.32 / 3.76 pass, anchor Δ −0.85 / +0.09 pass, but the 2T candidate (≈61/60 BPM) out-scores the adopted lag under the harmonic sum on BOTH songs (1.398 vs 1.352; 1.401 vs 1.321). FD-1: nothing retuned; both songs stay MUST-NOT-CONSUME; `recanonicalization_blocked.json` byte-identical (2fbabc07…); no n=23 rules re-run; iteration 3 proceeds on n=21. Next (c86, new prereg): onsets-per-beat half/double check + beat-tracker consensus.", "Prereg < verdict; enum recorded; blocked file untouched; figure on disk.", "M-V5-CORPUS-1"),
     ("M-V5-GEN-1/F5-interpolation-demo", "G5", "F5 v5 INTERPOLATION DEMO (pending, c88 iteration 5; decision #7 still owed): two donors (CG ↔ PD), t=0.5 blend of groove + harmony models, rendered with the v5 generator, replay proof.", "Demo rendered byte-det x2 with manifest + replay proof; delivered to data/v4/generated/.", "M-V5-GEN-1/F3-guitar-piano-other"),
     ("M-V5-GEN-1/F6-iteration-schedule", "G5", f"F6 ITERATION SCHEDULE landed c85: `stall_counter.json` history entries carry feature / donor_map_sha256 / form_plan_sha256 / rules_sha256 / seed + top-level ts (history[-1]: iteration {stall['history'][-1]['iteration']}, feature {stall['history'][-1]['feature']}). Schedule: iter 3 F2, iter 4 F3, iter 5 F5, seed = iteration − 1, donors fixed.", "Schema present on every new history entry.", "M-V5-GEN-1"),
     ("M-V5-GEN-1/F7-close", "G1", "F7 M-V5-CLOSE-1 docs (report amendment, OPERATOR_DECISIONS, codebase guide) only after F1–F5 have landed.", "Docs updated; clean re-close.", "M-V5-GEN-1/F1-form-arrangement, M-V5-GEN-1/F2-bass-melody-dynamics, M-V5-GEN-1/F3-guitar-piano-other, M-V5-GEN-1/F4-tempo-fix, M-V5-GEN-1/F5-interpolation-demo"),
     ("M-V5-GEN-1/form-preregistered-c85", "G5", "c85 P1: `data/v5/gen/form_prereg_c85.json` BEFORE any output — segmentation, form-plan model, contrast rule, arrangement, enum, diagnostic ladder R1/R2, held-constant list.", "Prereg mtime < model + every iteration-2 output.", "M-V5-GEN-1/F1-form-arrangement"),
     ("M-V5-GEN-1/form-plan-model-c85", "G5", f"c85 P1: `scripts/v5/form_plan_v5.py` → `data/v5/rules/form_plan_v5.json` byte-det x2 on n=21; R1 FAILED at 0.85 (recorded, no sweep) → fixed template fallback; per-label tercile/harmony-region targets, intro density quantile {fp['intro_density_quantile']}, boundary fill pool {len(fp['boundary_fill_pool'])}; figure `fig_form_plan_corpus_c85.png` + `plot_form_plan_corpus_c85.py`.", "Byte-det x2; R1 verdict recorded; figure on disk.", "M-V5-GEN-1/form-preregistered-c85"),
     ("M-V5-GEN-1/iteration-02-c85", "G5", f"c85 P1 iteration 2 (seed 1, form plan ON, c84 rules): 5 renders under `data/v5/gen/iteration_02/` each REPLAY_PROOF_HOLDS; forms " + ", ".join(''.join(s['form']) for s in roll['songs']) + f"; durations " + ", ".join(str(s['duration_s']) for s in roll['songs']) + f" s; informational scores ≥6 {sc['n_gen_ge_6']}/5 (FD-6, no passer); listening copies → `data/v4/generated/v5_iter_02/`; stall {stall['iterations']}/{stall['budget']}.", "5 renders + proofs on disk; scores recorded; listening copies listed in the event artifacts.", "M-V5-GEN-1/F1-form-arrangement"),
     ("M-V5-CORPUS-1/tempo-f4-preregistered-c85", "G4", "c85 P2: `tempo_f4_prereg_c85.json` BEFORE output — operator adjudication (not a criterion); scope PD + Disco A; adopted mechanism c83 tempo_v5d; verbatim half/double check; enum; FD-1.", "Prereg mtime < verdict.", "M-V5-CORPUS-1/tempo_v5d-verdict-c83"),
     ("M-V5-CORPUS-1/tempo-f4-adjudication-c85", "G4", f"c85 P2 **{v['verdict']}** (`scripts/v5/tempo_f4_adjudicate_c85.py` → `tempo_f4_verdict_c85.json`, byte-det x2): PD adopted 122.197 s 1.3516 — T/2 lower True, 2T (61.08 BPM) s 1.3983 lower False; Disco A adopted 120.272 s 1.3209 — T/2 lower True, 2T (60.04 BPM) s 1.4008 lower False; onsets/beat 2.32 / 3.76 pass; anchor Δ pass. Nothing retuned; blocked file byte-identical; no recanonicalization. Figure `fig_tempo_f4_c85.png`.", "Verdict ∈ enum; blocked file untouched; byte-det x2.", "M-V5-CORPUS-1/tempo-f4-preregistered-c85"),
     ("M-V5-RULES-1/harmony-eligible-from-c85", "G4", f"c85 M5: `harmony_v5.py --eligible-from data/v5/rules/eligible_c84.json` reproduces the c84 chain sha {rbd['run1_sha256'][:16]}… in two fresh tempdirs (21/21 per-song files byte-identical); flag-off path unchanged.", "Chain sha == c84 anchor x2.", "M-V5-RULES-1/harmony-full-corpus-c84"),
     ("_infra/cheap-fixes-M2-M4-c85", "G1", "c85 P0: M2 byte_determinism_c85.json in data/v5/{gen,rules,corpus} for every x2 claim (run SHAs + tempdirs); M3 N/A (no per-song rows this cycle); M4 no groove-model copy in iteration_02 (c84 copy under iteration_01/ reclaimable, never deleted); score_gen_batch_v5.py + deliver_v5_listening.py --cycle/--milestone.", "Files present; test_05 green.", "—"),
     ("_plan/register-c85-sub-leaves", "G1", "c85 POR registration row: F1..F7 backlog rows + c85 sub-leaves inserted inline via `tools/_register_c85_por_rows.py` (idempotent).", "Rows added.", "—"),
     ("_infra/adopt-cycle85-tests", "G1", "c85 test-adoption: `tests/test_c85_landing.py` (10) + `tests/test_c85_f4_m5.py` (5) new; adopted suite re-run under /usr/bin/python3 (counts in the work output; ADOPTED suite, not tests/ as a whole).", "New tests green + regression green.", "—"),
     ("_archive/cycle-85-scratch", "G1", "c85 scratch archival: emitter + registrar retained in-tree per emitter-exemption pattern and listed as artifacts (L1); scratchpad runners not in workspace; plot scripts co-located with data + figures.", "No workspace scratch to archive.", "—"),
     ("_run/cycle_85_closed", "G1", "c85 CLOSED — v5 REOPENING cycle 7 (feature cycle: F1 iteration 2 + F4 adjudication + P0 fixes). See ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c85 POR rows present"); return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    main()
