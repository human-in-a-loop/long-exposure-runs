#!/usr/bin/python3
"""c90 one-shot POR registrar (two idempotent phases): `--close-amend` appends an additive `c90 CLOSED` clause to the existing
`M-V5-CLOSE-1` and `M-V5-GEN-1/F7-close` rows (existing wording kept verbatim); default phase inserts the c90 sub-leaf rows inline
in the `## Milestones` parseable region (before `## Sub-milestones`). Fail-closed on missing artifacts.

created: 2026-09-10T04:20:34Z
cycle: 90
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _plan/register-c90-sub-leaves
"""
import hashlib
import json
import os
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")
ROWS_TO_AMEND = {"| M-V5-CLOSE-1 | G1 |": "M-V5-CLOSE-1", "| M-V5-GEN-1/F7-close | G1 |": "M-V5-GEN-1/F7-close"}


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


def amend_close() -> int:
    bd = j("data/v5/gen/byte_determinism_c90.json")
    ap = bd["doc_appends"]
    v = j("data/v5/logs/validators_c90.json")
    rd = j("data/v5/logs/runners_decision_c90.json")
    clause_close = (f" **c90 CLOSED (= harness c134)**: completion-report v5 section appended additively to `docs/v4_completion_report_v3.md` (pre {ap['docs/v4_completion_report_v3.md']['pre_sha256'][:16]}… → post {ap['docs/v4_completion_report_v3.md']['post_sha256'][:16]}…), "
                    f"OPERATOR_DECISIONS #21 (pre {ap['docs/OPERATOR_DECISIONS.md']['pre_sha256'][:16]}… → post {ap['docs/OPERATOR_DECISIONS.md']['post_sha256'][:16]}…), codebase-guide v5 section (pre {ap['docs/CODEBASE_GUIDE.md']['pre_sha256'][:16]}… → post {ap['docs/CODEBASE_GUIDE.md']['post_sha256'][:16]}…) — all prefix byte-equal; "
                    f"parent roll-ups CORPUS_LANDED_TEMPO_AXIS_STOPPED / RULES_LANDED_WITH_HONEST_GAPS / EAR_RESTORED_INFORMATIONAL_ONLY / FEATURES_F1_F5_LANDED_HONEST_BEST_OF_AT_STALL_5_OF_12; validators promise_check {v['after_adopt']['promise_check']['error']} ERROR / {v['after_adopt']['promise_check']['warn']} WARN after the adopt event (open 156 / 8960), org_check {v['after_adopt']['org_check']['error']} / {v['after_adopt']['org_check']['warn']}; "
                    f"runners decision (a) ({rd['runner_module_sha256'][:16]}…); frozen close enum V5_CLOSE_LANDS / V5_CLOSE_PARTIAL / V5_CLOSE_FAILS recorded in the ledger event `M-V5-CLOSE-1` (c90). The run re-closes cleanly; a later guidance file may reopen it (c79 str-supersede pattern).")
    clause_f7 = (" **c90 LANDED (= harness c134)**: report amendment + OPERATOR_DECISIONS #21 + codebase guide appended additively (prefix byte-equality asserted by tests/test_c90_close.py); "
                 "F1 FORM_PLAN_PARTIAL c85 / F2 F2_PARTIAL c87 / F3 F3_LANDS c88 / F4 CLOSED c86 / F5 F5_LANDS c89 stated with their landing-cycle enums; WARN triage + adopt event; runners (a); clean re-close.")
    lines = POR.read_text().splitlines(keepends=True)
    changed = 0
    for prefix, name in ROWS_TO_AMEND.items():
        hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        assert len(hits) == 1, (name, hits)
        i = hits[0]
        marker = "c90 CLOSED" if name == "M-V5-CLOSE-1" else "c90 LANDED"
        if marker in lines[i]:
            print(f"IDEMPOTENT: {name} row already amended")
            continue
        cells = lines[i].rstrip("\n").split(" | ")
        assert len(cells) == 5, (name, len(cells))
        cells[2] = cells[2] + (clause_close if name == "M-V5-CLOSE-1" else clause_f7)
        lines[i] = " | ".join(cells) + "\n"
        changed += 1
        print(f"{name} row amended at line {i + 1}")
    if changed:
        POR.write_text("".join(lines))
    return 0


def register() -> int:
    bd = j("data/v5/gen/byte_determinism_c90.json")
    ap = bd["doc_appends"]
    v = j("data/v5/logs/validators_c90.json")
    rd = j("data/v5/logs/runners_decision_c90.json")
    pr = j("data/v5/logs/c90_prune.json")
    rows = [
     ("_plan/guidance-continuation-c90", "G1", "c90 (= harness c134): no new operator guidance file landed (newest on disk dated 2026-09-09); the c131 guidance (sha16 fed27e550e9f7c75) + the F1–F7 backlog guidance (sha16 cf7296cfcf70c277) continue to govern; the F7 clause is OPEN (F1–F5 landed) — this cycle is F7 close docs.", "One line; guidance SHAs quoted.", "—"),
     ("_infra/disk-prune-c90", "G1", f"c90 P0: df {pr['df_open']['used_pct']} % ({pr['df_open']['avail_gb']} GB, `df -P`) at open; pruned ONLY regenerable render tempdirs — this session's c89 ×2 / flag-off / score-run2 tempdirs + the c89 auditor scratchpad's two re-render tempdirs LISTED by path and size in data/v5/logs/c90_prune.json before deletion ({pr['pruned_mb']} MB total); nothing under the workspace, /tmp/tfhub_modules, data/v4/**, data/v5/corpus/** canonical dirs or profiles; df after {pr['df_after']['used_pct']} % ({pr['df_after']['avail_gb']} GB); never ≥ 90 %.", "Record at data/v5/logs/c90_prune.json.", "—"),
     ("_infra/adopt-cycle89-gen-artifacts-c90", "G1", f"c90 P3 adopt event: data/v5/gen/iteration_05/** + data/v4/generated/f5_interp_CG_PD_t050_c89/** + data/v4/generated/v5_iter_05/** ({v['adopt_event']['n_paths']} paths) adopted under M-V5-GEN-1 so the `orphan artifact in managed path` WARN class no longer fires on them; promise_check 156 / 8960 → {v['after_adopt']['promise_check']['error']} / {v['after_adopt']['promise_check']['warn']} (Δ {v['adopt_event']['warn_delta_vs_open']}); no file modified.", "Event carries ≥ 250 existing paths; ERROR unchanged.", "M-V5-GEN-1"),
     ("_infra/warn-growth-triage-c90", "G1", f"c90 P3 WARN-growth triage (data/v5/logs/validators_c90.json): class = `orphan artifact in managed path` ({v['open']['promise_check']['classes']['orphan artifact in managed path']} of 8960 at open; data/v5/gen {v['open']['orphan_by_prefix']['data/v5/gen']}, data/v4/generated {v['open']['orphan_by_prefix']['data/v4/generated']}); zero WARNs on c89 ledger lines; series c85 8543 / c86 not recorded / c87 not recorded / c88 8707 / c89 8960 / c90 open 8960 / after adopt {v['after_adopt']['promise_check']['warn']}; ERROR baseline 156 entirely pre-c90 (0 on c90 ids or ledger lines ≥ 2153); org_check 0 / 54.", "Table in the report section; ERROR == 156.", "—"),
     ("_infra/runners-decision-c90", "G1", f"c90 P4 runners decision = (a): scripts/v5/runners/run_from_launch_json.py ({rd['runner_module_sha256'][:16]}…; dry-run reproduces any pinned launch/byte-det command byte-for-byte; `--execute` detached via launch_detached; refuses drifted generate_v5.py or a missing fresh --out; /usr/bin/python3 guard; no PRNG) + README ({rd['readme_sha256'][:16]}…) + the ten c89 scratchpad runners copied verbatim to scripts/v5/runners/c89/ (originals still on disk at c90 open).", "Module + README + c89 runners on disk; dry-run byte-for-byte asserted.", "—"),
     ("M-V5-CLOSE-1/completion-report-v5-section-c90", "G1", f"c90 P1: `## Section: v5 REOPENING (c79–c90) — feature backlog F1–F7 close` appended ADDITIVELY to docs/v4_completion_report_v3.md (pre {ap['docs/v4_completion_report_v3.md']['pre_sha256'][:16]}… {ap['docs/v4_completion_report_v3.md']['pre_bytes']} B → post {ap['docs/v4_completion_report_v3.md']['post_sha256'][:16]}… {ap['docs/v4_completion_report_v3.md']['post_bytes']} B; v3 §1–§7 + c78 section byte-identical prefix; first 8 KB unchanged): cycle-counter/outage disclosure, CORPUS / RULES / EAR / GEN sections with every number from disk, the F1–F7 table (landing-cycle verdicts), the F5 union-vocabulary caveat + future-sweep rule, carry-forward hygiene, program coverage 14/15 shims, determinism receipts, validator table + WARN series, runners decision, deliverable index (every SHA resolves on disk), honest gaps, close rationale.", "Prefix byte-equal; SHAs resolve; sentences present (tests).", "M-V5-CLOSE-1"),
     ("_plan/operator-decisions-c90-amendment", "G1", f"c90 P2: docs/OPERATOR_DECISIONS.md entry #21 (v5 CLEAN RE-CLOSE at c90) appended additively at EOF (pre {ap['docs/OPERATOR_DECISIONS.md']['pre_sha256'][:16]}… → post {ap['docs/OPERATOR_DECISIONS.md']['post_sha256'][:16]}…; #1–#20 + the standing-constraints block untouched): verdict matrix CORPUS / RULES / EAR / GEN / CLOSE, F1–F7 table, F5 caveat, ear-informational rule, FD-6 delegation over 26 v5 renders + 25 v4 A/Bs, tempo-axis STOP, re-close wording.", "Additive append; pre/post SHAs pinned.", "—"),
     ("_plan/codebase-guide-c90-amendment", "G1", f"c90 P2: docs/CODEBASE_GUIDE.md gained the additive `## v5 REOPENING layer (c79–c90)` section (pre {ap['docs/CODEBASE_GUIDE.md']['pre_sha256'][:16]}… → post {ap['docs/CODEBASE_GUIDE.md']['post_sha256'][:16]}…): scripts/v5 module map with SHAs, generator flag matrix, data/v5 layout, prereg-before-output discipline, ear-venv invocation, blend_record_sha256 semantics.", "Additive append; module SHAs resolve on disk.", "—"),
     ("_infra/n25-siblings-skipped-c90", "G1", "c90 P6 optional n=25 sibling artifacts SKIPPED (deferred c88 + c89; stated in the report's honest-gaps list, not deferred again); nothing consumed from it.", "One line.", "—"),
     ("_plan/register-c90-sub-leaves", "G1", "c90 POR registration row: `c90 CLOSED` / `c90 LANDED` clauses appended additively to the M-V5-CLOSE-1 and M-V5-GEN-1/F7-close rows (`--close-amend`) + c90 sub-leaves inserted inline via tools/_register_c90_por_rows.py (idempotent; fail-closed).", "Rows added.", "—"),
     ("_infra/adopt-cycle90-tests", "G1", "c90 test-adoption: tests/test_c90_close.py new (prefix byte-equality + first-8 KB header of the three docs; v5 section F1–F7 table + every quoted SHA resolves; F5 caveat + blend_record_sha256 sentences; validators ERROR == 156; runners decision + byte-for-byte dry-run; no file under the iteration trees / data/v4/generated newer than the cycle open; §4 pins byte-identical; c90 ledger events agent + str-or-null supersedes_path + created ≤ now); c85–c89 suites + the adopted suite re-run → data/v5/logs/test_results_c90.json.", "New tests green + regression green.", "—"),
     ("_archive/cycle-90-scratch", "G1", "c90 scratch archival: tools/_emit_c90_ledger_events.py + tools/_register_c90_por_rows.py retained in-tree per the emitter-exemption pattern; this cycle's scratchpad runners render nothing (docs + JSON records are the outputs); pruned tempdirs listed in data/v5/logs/c90_prune.json.", "No workspace scratch to archive.", "—"),
     ("_run/cycle_90_closed", "G1", "c90 CLOSED — v5 REOPENING cycle 12 (= harness c134): F7 close docs landed additively, WARN growth triaged with the adopt event, runners (a) checked in, parent roll-ups + M-V5-CLOSE-1 enum emitted; nothing rendered / retuned / re-verdicted; stall 5/12 unchanged; str-supersedes _run/cycle_89_closed. See the ledger event narrative + work output for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
    ]
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c90 POR rows present")
        return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0


if __name__ == "__main__":
    sys.exit(amend_close() if "--close-amend" in sys.argv else register())
