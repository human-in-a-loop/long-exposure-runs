# Test 1 of 5 — Adversarial Pass on Cycles c1–c5 (Delta Audit)

**Stage**: 7 of 12
**Scope**: Adversarial sweep across v4 cycles c1–c5 (CG bass sf2 arc + family-2 arc). Delta-audit mode: baseline `audits/final/final_audit_report.md` treated as canonical for pre-existing work.

## Validators

- **`promise_check`**: 0 ERROR, 49 pre-existing WARN (all missing-artifact WARNs from c6–c15 cycles, well before delta baseline; not new findings).
- **`org_check`**: 0 ERROR, 49 pre-existing WARN (figures colocated under `docs/run_archive/figures/` — inherited from pre-delta baseline).

Neither validator surfaces a new drift class introduced by the c1–c20 delta.

## Adversarial cross-checks performed

Cross-checked POR narrative claims against on-disk artifacts for c1–c5 (CG bass arc):

| Artifact | POR-narrative SHA | On-disk SHA (full) | Match? |
|---|---|---|---|
| bass.json (c2) | 11747a42cb1a8f7f... | 11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9 | ✅ |
| bass_v2.json (c4) | 2a1cb340bffd1101... | 2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462 | ✅ |
| bass_v2.replay_proof.json (c4) | 86948709746b966a... | 4b9eea98052d6b2f54dcc7b87af334614c5ad56fb8c159eb6563c21533d5817f | ❌ (Slice D MINOR already filed) |
| bass.replay_proof.json (c2) internal run_sha | 832868d0ea8a81ca... | c69775040c325b865be029316d5ccbaff6b3d2393b238c877bae3f1b74ff019c | ❌ (**new MINOR filed this stage**) |
| bass.json profile_id (c2) | 56cdc50a-dbbc-5a49-afc9-f3cf93a25c7d | 56cdc50a-dbbc-5a49-afc9-f3cf93a25c7d | ✅ |
| bass_v2.json profile_id (c4) | d62cd3b6-4521-5d4f-b840-87ef7800c48d | d62cd3b6-4521-5d4f-b840-87ef7800c48d | ✅ |
| bass_v2.replay_proof internal run_sha (c4) | 832868d0ea8a81ca... | 832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5 | ✅ |

Substantive REPLAY_PROOF_HOLDS claims (both runs SHA-equal, verdict field correct) are TRUE across all three replay-proof artifacts. Every profile_id is byte-exact.

## New finding filed this stage

**+1 MINOR** appended to `audits/final/findings.jsonl` (now 4 total):

`M-V4-PROFILES-1/cg-bass-sf2-replay-proof` — `por_anchor_drift` MINOR:
- POR c2 narrative pins internal `run1_sha256 == run2_sha256 == 832868d0…`
- On-disk `bass.replay_proof.json` actually holds internal runs at `c69775040c325b86…`
- File mtime `Sep 3 21:12` postdates `bass.json` write (`Sep 3 19:20`) — consistent with regeneration after `_infra/replay-channel-aware-fix-c11` changed sf2 dispatch semantics.
- Substantive REPLAY_PROOF_HOLDS claim intact (both runs match; verdict matches).
- Same drift class as the two prior findings; on-disk artifact authoritative per FD-1.

## Silent-supersession sweep

Checked for closure-doc mtime drift with no `_plan/` event: none found in c1–c5 range. The c9 acceptance-fork (`_plan/cg-bass-acceptance-fork-and-threshold-retirement-c9`) is properly registered per POR narrative. `_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy` was properly superseded via c9 fork.

## Orphan milestone sweep

No orphan c1–c5 milestone_ids surfaced (all sub-leaves accounted for in POR c1..c9 rows). c8 wait-on-operator heartbeat retired at c9 per operator directive; c8 anchor artifact preserved READ-ONLY as documented.

## Cycle status

Test 1/5 complete. Adversarial pass surfaces 1 new POR-anchor drift MINOR (same class as prior 2 findings). No CRITICAL or MODERATE issues found in c1–c5 range. Substantive verdict claims (REPLAY_PROOF_HOLDS, family FAMILY2_RULED_OUT, arc EXHAUSTED_NO_CONFIRMED, acceptance-fork OPT1+OPT3) all coherent with on-disk state.
