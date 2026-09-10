#!/usr/bin/python3
"""c87 one-shot POR registration: insert the c87 sub-leaf rows inline in the `## Milestones` parseable region (before `## Sub-milestones`).
Idempotent; fail-closed on missing artifacts. Retained in-tree per the emitter-exemption pattern.

created: 2026-09-10T01:58:00Z
cycle: 87
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _plan/register-c87-sub-leaves
"""
import json
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")


class MissingArtifact(FileNotFoundError):
    pass


def j(p):
    if not Path(p).exists():
        raise MissingArtifact(str(p))
    return json.loads(Path(p).read_text())


def main() -> int:
    roll = j("data/v5/gen/iteration_03/iteration_rollup.json")
    bd = j("data/v5/gen/byte_determinism_c86.json")["entries"]
    comp = j("data/v5/rules/comping_v5.json")
    g23 = j("data/v5/rules/groove_v5_v2_full_c86.json")
    stall = j("data/v5/gen/stall_counter.json")
    sc = j("data/v5/gen/gen_v5_iter03_ear_scores_c86.json")
    f2 = roll["f2"]
    v = comp["verdict"]
    rows = [
     ("_plan/adopt-operator-guidance-2026-09-09-c131", "G1", "c87 (= harness c131) adoption of OPERATOR GUIDANCE 2026-09-09 (c131) `docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt` (sha16 fed27e550e9f7c75; quoted verbatim in the ledger event): finish F2 iteration 3 FIRST consuming the landed velocities.json as-is, cross-cycle stem mismatch ACCEPTED (one line, no memo), then F3; long subprocesses detached at turn start.", "Guidance quoted verbatim in the ledger event.", "—"),
     ("M-V5-GEN-1/iteration-03-c87", "G5", f"c87 iteration 3 RENDERED (seed 2, form plan ON, `--f2 --velocity-mode f2 --rms-variance-test --prove-replay --cycle 87`, c84 n=21 rules by design): 5/5 REPLAY_PROOF_HOLDS under generator sha {roll['generator_hash'][:16]}…; F2 enum **{f2['f2_enum']}** (velocities 5/5, replay 5/5, RMS-variance ≥1.5 {f2['n_rms_variance_pass']}/5 — drums < 1.0 on every song); flag-off under the FINAL image reproduces iteration 2 5/5 AND iteration 1 5/5; informational scores ≥6 {sc['n_gen_ge_6']}/5 (FD-6); listening copies → `data/v4/generated/v5_iter_03/`; stall {stall['iterations']}/{stall['budget']}; `byte_determinism_c86.json` + figures on disk.", "5 renders + proofs + flag-off ×2 sets + listening copies on disk; enum from the prereg.", "M-V5-GEN-1/iteration-03-c86"),
     ("M-V5-RULES-1/groove-n23-c86", "G4", f"c86 groove re-measured at n=23 (`groove_prereg_c86.json`; PD/Disco A via `--tempo-overrides`): **{g23['verdict']}**, singleton-context fraction {g23['singleton_context_fraction']} (recorded, not tuned); iteration 3 still consumed the c84 n=21 model faa0e76e… by design; consumed from iteration 4.", "Enum from the prereg; byte-det ×2.", "M-V5-CORPUS-1/tempo-f4-operator-resolved-c86"),
     ("M-V5-RULES-1/comping-stats-c87", "G4", f"c87 F3 comping statistics `scripts/v5/comping_v5.py` → `data/v5/rules/comping_v5.json` on the n=23 eligible set (guitar+piano+other; v5c dirs for PD/Disco A): **{v['enum']}** — {v['n_songs_with_ge_16_pooled_bars']}/23 songs ≥16 pooled bars, pooled max 16th-slot mass {v['pooled_max_slot_mass']} (<0.5); pooled onsets/bar {comp['stats']['pooled']['onset_density_onsets_per_bar']}, chord size {comp['stats']['pooled']['chord_size_mean']}; IOI histogram strongly structured (44.7 % at one 16th) while the 16th-slot histogram is NEAR-UNIFORM (0.0599..0.0652, structureless — disclosed). Prereg `comping_prereg_c87.json` before the run; byte-det ×2; figure `fig_comping_v5_c87.png` + `plot_comping_v5_c87.py --out`; 5 tests.", "Prereg mtime < outputs; ×2 equal; figure on disk.", "M-V5-RULES-1/harmony-n23-c86"),
     ("_infra/cheap-fixes-P0-c87", "G1", "c87 P0: `created:` stamps fixed on the three unpinned files (serializer + two plot scripts; velocity_v5.py NOT edited — 120 s test tolerance instead); `/usr/bin/python3` guard added to the sibling serializer; argparse error for `--velocity-mode f2`/`--rms-variance-test` without `--f2`; sibling-serializer byte-equality re-run 56/56; iter03 plot repo-root path bug fixed; emitters/registrars fail closed (MissingArtifact) and read test results from a workspace path; df via `df -P` driver semantics.", "Tests green; SHAs pinned in byte_determinism_c86.json.", "—"),
     ("_plan/register-c87-sub-leaves", "G1", "c87 POR registration row: c87 sub-leaves inserted inline via `tools/_register_c87_por_rows.py` (idempotent; fail-closed).", "Rows added.", "—"),
     ("_infra/adopt-cycle87-tests", "G1", "c87 test-adoption: `tests/test_c87_landing.py` (10) + `tests/test_c87_comping.py` (5) + `tests/test_c87_f3_gen.py` (4) new; c86 landing tests re-pinned to the c87 render (cycle 87, flag-off record schema, F2_PARTIAL live test, null degenerate flag, single route event); c85 stall test re-pinned to history[1]; adopted suite re-run under /usr/bin/python3 (counts in the work output).", "New tests green + regression green.", "—"),
     ("_archive/cycle-87-scratch", "G1", "c87 scratch archival: `tools/_emit_c87_early_events.py` + `tools/_emit_c87_ledger_events.py` + `tools/_register_c87_por_rows.py` retained in-tree per the emitter-exemption pattern; pipeline runners (run_iter03_c87 / tail / flagoff / bytedet / run_tests) in the session scratchpad only.", "No workspace scratch to archive.", "—"),
     ("_run/cycle_87_closed", "G1", "c87 CLOSED — v5 REOPENING cycle 9 (= harness c131): F2 iteration 3 rendered and recorded F2_PARTIAL (no retune); F4 CLOSED; F3 comping statistics landed (NON_DEGENERATE, slot histogram structureless disclosed) + standalone builder; `--f3` wiring deferred to c88. See the ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c87 POR rows present")
        return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    main()
