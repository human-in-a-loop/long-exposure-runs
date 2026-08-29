---
created: 2026-08-29T00:00:00Z
cycle: 53
run_id: run-2026-08-29T000000Z
agent: worker
fork: fork-18817b483ed4
clone: clone-0
branch: A
milestone: M-RECREATE-2/accurate-small-set/rc7-mix-balance-match
verdict: RC7_v2_LANDS
---

# Merge report — fork-18817b483ed4 clone-0 (RC7 v2 rerun)

## Directory-boundary note (auditor CRITICAL Priority 4b)

The directive requests this report at
`/home/user/music-gen-instance/fork-18817b483ed4/clone-0/merge_report.md`,
which lies OUTSIDE this session's Directory Boundaries
(`/home/user/long-exposure-runs/music-gen`). `mkdir` on the outside
path was refused. Per the c53-clone-1 pivot brief's Priority 4b Option
(i) (`_infra/fanout-merge-report-path-in-project`) this report is
written to the in-project fallback path:
`reports/fanout/fork-18817b483ed4/clone-0/merge_report.md`. Root
conductor should read this path if the outside path is missing.

## Scope executed

Re-invocation of an already-completed RC7 v2 rerun. On entry the ledger
carried 9 c53 events for this milestone (lines 880-888 of
`promise_ledger.jsonl` at session start); all substantive deliverables
were already on disk. Under efficient-philosophy discipline this
session did NOT re-run the pipeline. It verified integrity, closed
the promise-check gap, and emitted one housekeeping ledger event.

## Verdict

**`RC7_v2_LANDS`** — 5/5 focus songs pass A7, 20/20 individual stem
accepts across `{drums, bass, other_guitar, other_piano}`.

| song_id | per_stem_pass | song_pass |
| :--- | :---: | :---: |
| 31a164f845f8e27e (Chicken Grease band 6) | 4/4 | ✓ |
| cdd2717e52820ff6 (Disco A band 5) | 4/4 | ✓ |
| 51e433ade2a845e1 | 4/4 | ✓ |
| 252eb21ce7df7328 | 4/4 | ✓ |
| 88d247468cb6d49f | 4/4 | ✓ |

## Byte-determinism × 2

226/226 output files SHA-256 equal across two fresh `tempfile.mkdtemp()`
runs under all env pins (`PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424
TZ=UTC LC_ALL=C.UTF-8` + single-thread BLAS). `mismatch_files=[]`.
`data/recreate_v2/rc7_out_v2/byte_determinism.json`.

## Anchor preservation

- `data/recreate_v2/rc7_out/` (c51 Branch C anchor, 182 files):
  ALL SHAs byte-identical pre==post. `anchor_preservation_v2.json`
  `preservation_holds=true`.
- `scripts/palette_render/render_stem.py` SHA
  `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
  byte-identical (c51-extended additive-kwargs form).
- `data/rc1_rc9_impl/`, `data/rc2_rc3_impl/`, `data/recreate_v2/baseline/`,
  `data/recreate_v2/focus_set_v2.json`: READ-ONLY throughout.
- Three-way rubric_hash chain preserved:
  `docs/rc7_v2_rerun_rubric.md` SHA = `9f24e6d9…04dde4` ==
  `data/recreate_v2/rc7_out_v2/rubric_hash.txt` content ==
  `data/recreate_v2/rc7_out_v2/verdict.json.rubric_hash`.

## Ledger events

- 9 c53 events pre-existing on disk under `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/*`
  and `M-INGEST-1/egress-probe-cycle53-clone-0`, plus infra
  `_infra/adopt-rc7-v2-artifacts-clone-0` and `_archive/rc7-v2-scratchpad-clone-0`
  (lines 880-888 of `promise_ledger.jsonl`).
- 1 new c53 event this session: `_plan/register-c53-rc7-v2-fanout-milestones`
  (retroactive plan-of-record registration to clear 6 pre-registration
  ERRORs). Written to per-clone shadow ledger via `AGENT_FORK_ID`
  routing; will merge into main at fanout barrier collapse.

## Housekeeping performed

Six c53 sub-leaf milestone rows added to `plan_of_record.md`
Milestones table (below the c52 `_run/post-merge-integration-cycle-51`
row): `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/{pre-registration,
impl, tests, byte-determinism-v2, anchor-preservation-v2}` +
`M-INGEST-1/egress-probe-cycle53-clone-0`. Same registration pattern
as c52 `_plan/register-c51-fanout-milestones`.

`promise_check` transitioned from 6-ERROR to 0-ERROR. ~7 pre-existing
WARNs remain (pre-c51 ledger-tracked files missing on disk; out of
scope, same as c52).

## Handoffs to root conductor

1. **Merge-report path deadlock**: consider adopting brief Priority 4b
   Option (i) in-project convention permanently. This clone's report
   is at `reports/fanout/fork-18817b483ed4/clone-0/merge_report.md`
   rather than the requested outside path.
2. **Shadow-ledger merge**: the `_plan/register-c53-rc7-v2-fanout-milestones`
   event is queued in this clone's shadow ledger; concatenate into
   `promise_ledger.jsonl` at merge time.
3. **c54 handoff (Chicken Grease RC7)**: Chicken Grease (band 6)
   PASSED all 4 stems under RC7_v2 on the substantive MIDIs. This
   pass supersedes the c51 Branch A RC1 honest-negative concern for
   the RC7 gate only; the RC1 policy call (research brief Priority 3)
   remains open per the c53 pivot brief.
