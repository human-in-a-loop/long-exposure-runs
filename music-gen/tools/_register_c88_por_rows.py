#!/usr/bin/python3
"""c88 one-shot POR registrar (two idempotent phases): `--f4-amend` appends the `c86 RESOLVED` clause to the existing
`M-V5-GEN-1/F4-tempo-fix` row (additive text only; the c85 AMBIGUOUS wording is kept verbatim); default phase inserts the c88 sub-leaf
rows inline in the `## Milestones` parseable region (before `## Sub-milestones`). Fail-closed on missing artifacts.

created: 2026-09-10T06:20:00Z
cycle: 88
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _plan/register-c88-sub-leaves
"""
import json
import os
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")
F4_ROW = "| M-V5-GEN-1/F4-tempo-fix | G5 |"
F4_CLAUSE = (" **c86 RESOLVED (amended c88 = harness c132)**: the operator addendum (guidance sha16 8677bb0cd3f240a0) overruled the AMBIGUOUS verdict — PD 122.197271 / "
             "Disco A 120.272335 ADOPTED; `recanonicalization_blocked.json` amended in place (pre 2fbabc07… kept as `stale/recanonicalization_blocked.c80_c85.json`, post eb78cfc0ce57dc9f…); "
             "`canonical_v5c_reindexed/` for both songs; harmony n=23 NON_DEGENERATE + groove n=23 OVERFITS consumed from iteration 4; F4 CLOSED (ledger `M-V5-GEN-1/F4-tempo-fix` validated/high, c87; "
             "see `M-V5-CORPUS-1/tempo-f4-operator-resolved-c86`). Iteration 4 (c88) switches the PD / Disco A donor tempo to the adopted values via `--tempo-overrides tempo_overrides_c86.json`.")


class MissingArtifact(FileNotFoundError):
    pass


def j(p):
    if not Path(p).exists():
        raise MissingArtifact(str(p))
    return json.loads(Path(p).read_text())


def amend_f4() -> int:
    lines = POR.read_text().splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if l.startswith(F4_ROW)]
    assert len(hits) == 1, hits
    i = hits[0]
    if "c86 RESOLVED" in lines[i]:
        print("IDEMPOTENT: F4 row already amended")
        return 0
    cells = lines[i].rstrip("\n").split(" | ")
    assert len(cells) == 5, len(cells)  # id | goal | description | criteria | deps
    cells[2] = cells[2] + F4_CLAUSE
    lines[i] = " | ".join(cells) + "\n"
    POR.write_text("".join(lines))
    print(f"F4 row amended at line {i + 1}")
    return 0


def register() -> int:
    roll = j("data/v5/gen/iteration_04/iteration_rollup.json")
    bd = j("data/v5/gen/byte_determinism_c88.json")
    ent = bd["entries"]
    stall = j("data/v5/gen/stall_counter.json")
    sc = j("data/v5/gen/gen_v5_iter04_ear_scores_c88.json")
    f3 = roll["f3"]
    fo3 = ent["iteration_03_flag_off_replay"]
    it4 = ent["iteration_04_renders"]
    rows = [
     ("_plan/f4-tempo-fix-por-row-amended-c88", "G1", "c88 P0b: the `M-V5-GEN-1/F4-tempo-fix` POR row (c85 AMBIGUOUS wording kept verbatim) gained an additive `c86 RESOLVED` clause via the idempotent registrar `tools/_register_c88_por_rows.py --f4-amend`: operator adopted PD 122.197271 / Disco A 120.272335, blocked file amended eb78cfc0…, F4 CLOSED (see `M-V5-CORPUS-1/tempo-f4-operator-resolved-c86`); closes the c87 auditor MODERATE. `supersedes_path` = `data/v5/corpus/tempo_f4_verdict_c85.json` (str per c14 lemma).", "Row contains the clause; ledger event with str supersedes_path.", "M-V5-GEN-1/F4-tempo-fix"),
     ("M-V5-GEN-1/f3-preregistered-c88", "G5", "c88 P0d: `data/v5/gen/f3_prereg_c88.json` written BEFORE any F3 output (mtime gate, test-asserted): part definitions (IOI-walk comping from the corpus IOI histogram, NOT the structureless slot histogram; chord-tone voicings over the chain state; register profiles guitar 52 / piano 60 / other 48; other = sustained pad per the corpus sustain 8.95 beats), program policy (donor pinned `<part>.json` if present — only CG guitar.json prog 28 — else GM shims 27/0/89, disclosed per song), velocities via the F2 keys-by-slot ladder, SHA-256 inverse-CDF only, per-song render clauses (≥ 32 note_on per part, −60 dB audibility floor, replay ×2) + iteration clause (F3-off reproduces iteration 3), frozen enum F3_LANDS / F3_PARTIAL / F3_FAILS, held-constant list.", "Prereg mtime < every iteration-4 output.", "M-V5-GEN-1/F3-guitar-piano-other"),
     ("M-V5-GEN-1/iteration-04-c88", "G5", f"c88 iteration 4 RENDERED (seed 3, form plan ON, `--f2 --velocity-mode f2 --f3 --tempo-overrides --prove-replay --cycle 88`, n=23 harmony 330b9d46… + groove 57072025…): {it4['n_equal']}/5 REPLAY_PROOF_HOLDS under the post-edit generator sha {bd['post_edit_script_sha256']['generate_v5'][:16]}…; F3 per-song {f3['n_songs_all_per_song_clauses']}/5 (parts ≥32 note_on + audible + replay), F3-off reproduces iteration 3 {fo3['n_equal']}/5 → enum **{bd['f3_enum_final']}**; PD / Disco A rendered at the adopted tempos {roll['tempo_overrides']['overrides']}; informational scores ≥6 {sc['n_gen_ge_6']}/5 (FD-6); listening copies → `data/v4/generated/v5_iter_04/`; stall {stall['iterations']}/{stall['budget']} with the F6 entry; figure `fig_iter04_parts_c88.png` via `--out`.", "5 renders + proofs + flag-off set + listening copies on disk; enum from the prereg.", "M-V5-GEN-1/F3-guitar-piano-other"),
     ("_infra/f3-wiring-and-tempo-overrides-c88", "G1", f"c88 P0e: `scripts/v5/generate_v5.py` edited ADDITIVELY (pre f261690c1f534611… → post {bd['post_edit_script_sha256']['generate_v5'][:16]}…): `--f3` default OFF consuming the READ-ONLY c87 builder, `--comping-model` sub-flag rejected without `--f3`, independent `--tempo-overrides`, pin-path args `--harmony-prereg`/`--groove-prereg` (c84 defaults); flag-off under the post-edit image reproduces iteration 3 {fo3['n_equal']}/5" + (f" and iteration 2 {ent['iteration_02_flag_off_replay']['n_equal']}/5" if 'iteration_02_flag_off_replay' in ent else "") + ".", "Post-edit sha pinned; flag-off SHAs reproduced.", "—"),
     ("_plan/guidance-continuation-c88", "G1", "c88 (= harness c132): no new operator guidance file landed; the c131 guidance (`docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt`, sha16 fed27e550e9f7c75) continues to govern — F2 done (F2_PARTIAL stands, no retune), this cycle is F3; the c85 backlog guidance (sha16 cf7296cfcf70c277) sets one feature per cycle (code + test + rendered iteration to data/v4/generated/v5_iter_NN/).", "One line; guidance SHAs quoted.", "—"),
     ("_infra/disk-prune-c88", "G1", "c88 P0a: df 86 % (5.97 GB avail, `df -P` driver semantics) at open; pruned only regenerable transients — the c85–c87 ×2 render tempdirs under /tmp (377 MB; flag-off, uniform-twin, score run2, profiles run2); nothing under data/v4/**, data/v5/corpus/** canonical dirs or profiles; no `_transient/` dirs or stale per-track WAVs under data/v5; the 48 MB c84 groove-model copy under iteration_01/ left in place (worker never deletes workspace artifacts; disclosed). df after 85 % (6.35 GB avail); never ≥ 90 %.", "Record at data/v5/logs/c88_prune.json.", "—"),
     ("_infra/n25-follow-up-deferred-c88", "G1", "c88 P4 (optional) DEFERRED in one line: the n=25 sibling artifacts (eligible_c88 = n=23 ∪ {0e1e8f20592db366, cc0693b4a24f64b2}; harmony / groove / comping re-run, byte-det ×2, NOT consumed by iteration 4) roll to the F5 cycle (c89) — P1–P3 absorbed the wall budget; nothing consumed from it, nothing blocked by it.", "One deferral line; no artifact.", "—"),
     ("_plan/register-c88-sub-leaves", "G1", "c88 POR registration row: F4 row amendment + c88 sub-leaves inserted inline via `tools/_register_c88_por_rows.py` (idempotent; fail-closed).", "Rows added.", "—"),
     ("_infra/adopt-cycle88-tests", "G1", "c88 test-adoption: `tests/test_c88_landing.py` new; c85/c86/c87 stall-counter pins (iterations == 3) re-pinned to ≥ 3 / history index (disclosed in place as c88 re-pins — the counter advances by design); adopted suite re-run under /usr/bin/python3 (counts in the work output).", "New tests green + regression green.", "—"),
     ("_archive/cycle-88-scratch", "G1", "c88 scratch archival: `tools/_emit_c88_ledger_events.py` + `tools/_register_c88_por_rows.py` retained in-tree per the emitter-exemption pattern; pipeline runners (p0_prune_pins / p0_prereg / smoke_f3 / run_iter04 / launch / bytedet / run_tests) in the session scratchpad only; stale c85–c87 ×2 tempdirs under /tmp pruned (377 MB).", "No workspace scratch to archive.", "—"),
     ("_run/cycle_88_closed", "G1", f"c88 CLOSED — v5 REOPENING cycle 10 (= harness c132): F3 wired (`--f3` default off) and iteration 4 rendered on the n=23 chain with the adopted PD / Disco A tempos; F3 enum {bd['f3_enum_final']}; F4 POR row amended; n=25 follow-up deferred to the F5 cycle. See the ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c88 POR rows present")
        return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    sys.exit(amend_f4() if "--f4-amend" in sys.argv else register())
