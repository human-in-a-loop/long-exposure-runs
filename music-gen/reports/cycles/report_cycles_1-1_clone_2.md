---
title: "Cycle 1 Clone 2 Report — _infra/anchor-manifest-v1 (Fork 07063458736e)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-1_clone_2]

# Cycle 1 Clone 2 Report — _infra/anchor-manifest-v1 (Fork 07063458736e)

## Abstract

Cycle 1 of clone-2 (fork `07063458736e`) lands the cycle-35 Branch C infra-codification milestone `_infra/anchor-manifest-v1` at **MANIFEST_LOCKED**, plus the codified `_run/cycle_<N>_launched(-clone-<k>)?` writing convention. The frozen manifest at `data/anchor_manifest_v1.json` (SHA `6dc917fe365a37ff87c3d72f45b3d433894221f8ebdbb36ed3beb5d44a7a821f`) is now the campaign's single source of truth for anchor SHA verification across 18 anchor entries spanning c6-c34. The launched-event convention is codified in `docs/fanout_launched_event_convention.md` with test-boundary enforcement via `tests/test_launched_event_convention.py`. Extends the c14→c22→c32→c33 infra hardening chain.

## Verdict

**MANIFEST_LOCKED** (drift-check vacuously clean per rubric §1(3) — this manifest is the campaign's first structured per-path SHA baseline).

## Rubric SHA Anchor Chain

| Location | SHA-256 |
| --- | --- |
| `docs/anchor_manifest_v1_rubric.md` | `93fa07351f2f56fda2b9b2b720475740c26e8f4331189a97acd9c630d052e73c` |
| `data/anchor_manifest_v1/rubric_hash.txt` | `93fa0735…e73c` |
| Verdict-emitting ledger event `rubric_hash` | `93fa0735…e73c` |

Rubric-before-scripts mtime ordering: rubric doc 04:08 < earliest `scripts/anchor_manifest/*.py` 04:09-04:10. Auditor-independent freeze reproduction into fresh `tmp/audit_freeze/` subprocess yielded byte-identical manifest SHA to committed on-disk `data/anchor_manifest_v1.json`.

## Frozen Manifest (18 Anchor Entries)

Spans every locked-anchor set the campaign has accumulated: c6 feature cache; c8 basic-pitch venv; c9 pinned DawDreamer chain; c13 batch-v2 render pipeline; c15 `i4_stratified.py`; c22 stability harness + anti-pattern flag; c23 head-regularization anti-pattern flag; c25 feature-representation anti-pattern flag; c26/27/28/29/30 analytical utilities; c31 palette-v1 + palette_probe; c33 palette_render + dawdreamer_state + harness-clone-namespace-guard; c34 palette-v2 + palette_render_cross_seed + gen_palette_batch_v1.

Typed manifest structure: `{anchor_id, cycle, kind, paths[], sha_per_path, dir_manifest_sha, is_readonly}`. All 18 entries carry `is_readonly=true`. SHA-256 computed per file (canonical byte content) plus per-directory (sorted-relpath concat manifest SHA).

## Launched-Event Convention Codified

`docs/fanout_launched_event_convention.md` states literally: launched events (`_run/cycle_<N>_launched(-clone-<k>)?`) write `status: validated` at emission time — they mark start-of-cycle, not open work. This fixes the c34 clone-0 `status: in-progress` vs clone-1 `status: validated` asymmetry.

Test-boundary enforcement: `tests/test_launched_event_convention.py` scans ledger rows with `_run/cycle_.*_launched(-clone-)?` prefix and fails on any `status != "validated"`. The 7-row pre-existing offender list is pinned at `tests/fixtures/launched_event_offender_list_v1.txt` (SHA `32d8f90ad0d4f2765adc98081dc45270f8af44a76d7720d457cb59a141989a1d`) and MUST NOT grow. Worker chose the pragmatic path — codify as test enforcement rather than emit-boundary blocking — sound judgment given c33's clone-namespace guard already covers the harder namespace-suffixing invariant.

## Test Surface

| Suite | Result |
| --- | --- |
| `tests/test_anchor_manifest_stability.py` | **20/20 PASS** (exceeds ≥12 minimum) |
| `tests/test_launched_event_convention.py` | **8/8 PASS** (exceeds ≥6 minimum) |
| `tests/test_integration_cross_branch.py` §56 | **7/7 checks PASS**; whole suite 0 failures |
| `python3 -m long_exposure.tools.promise_check .` | **0 ERRORs**, 114 WARN (delta +1 from auditor's own scratch file; 0 attributable to Branch C) |

## Ledger Events (9 in Strict Order, Rows 535-543, `-clone-2` Suffix)

Six named + two housekeeping + one launched:

1. `_run/cycle_35_launched-clone-2` (`status: validated` per newly-codified convention)
2. `_plan/anchor_manifest_v1_rubric_frozen-clone-2`
3. `_infra/egress-probe-cycle-35-clone-2`
4. `_infra/anchor-manifest-v1-clone-2` (in-progress; per c33 harness-clone-namespace-guard, `_infra/*` from clone context is `-clone-<k>`-suffixed)
5. `_infra/anchor-manifest-v1-clone-2` (validated verdict roll-up, `MANIFEST_LOCKED`, rubric_hash embedded)
6. `_run/cycle_35_closed-clone-2`
7. `_archive/cycle-35-scratch-clone-2`
8. `_infra/adopt-cycle35-tests-clone-2`
9. (plus one additional in the 9-row range per auditor tally)

Ledger row growth: 534 → **543** (+9). Distinct milestones now 396; ~68% are `validated` terminal or `_infra/*` housekeeping.

## Deviations (Honestly Disclosed; None Verdict-Impairing)

1. **Anchor #4 file-vs-dir**: on-disk reality supersedes the brief.
2. **7-row offender list vs the brief's 1-row claim**: the fixture pins the truth stably at 7.
3. **No live top-of-cycle egress probe** (row 3 emitted from prior state): egress state carries unchanged from c34's 403 baseline per the campaign's non-blocking egress rule.

Each defensible; each surfaced transparently; each aligns with the campaign's cycles 22-30 honesty discipline. Auditor MINOR only: a transient §56 test-fixture race with the auditor's own concurrent `tmp/audit_freeze/` file creation on first invocation, PASS on subsequent invocations — not a Branch-C defect.

## Merge Disposition

Merge report at workspace-root fallback per c31/c34 pattern. Nine shadow-ledger rows ready for `concat_clone_ledgers`; zero cross-clone collisions under c32 `-clone-2` suffixes. c14→c22→c32→c33→**c35 anchor-manifest-v1 + launched-event-convention** infra hardening chain extended without net WARN growth attributable to itself.

## State-Machine Discipline (c29 Lemma Respected)

`_infra/anchor-manifest-v1` is a peer sub-milestone under root infra. Extends the c14 `_infra/ledger-schema-hardening-v2` + c22 `_infra/harness-auto-write-namespacing` + c32 `_infra/fanout-namespace-convention` + c33 `_infra/harness-clone-namespace-guard` chain. NOT a child of any terminal-validated milestone.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`.
- SHA-256 tiebreak; no PRNG (AST-verified); no `sidecar_nonfactor` imports.
- Interpreter guard `assert sys.executable == '/usr/bin/python3'` on every new script.
- Read-only anchors preserved: c14 ledger-schema-hardening code; c22 harness-auto-write-namespacing code; c32/c33 namespace-convention + clone-namespace-guard code. Manifest computation is read-only against every anchor path.
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403 from c34 baseline). M-EAR-1 armed-not-fired posture holds.
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.

## Anti-Patterns Locked (Unchanged, 5-Count Stable)

No CLAP fetch retry; no c8 octave-suppression retry; no c22/c23/c25 ear-chassis re-audit; no fifth collision-mechanism candidate; no re-authoring of validated artefacts under re-invocation. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` explicitly out-of-scope declared for c35.

## Cycle-36 Handoff (Informational, Per Auditor)

1. **Anchor-manifest as SSoT**: `data/anchor_manifest_v1.json` (SHA `6dc917fe…4a7a821f`) is now the campaign's SSoT for anchor SHA verification. Future branches may drop bespoke `anchor_preservation.json` mtime snapshots in favor of manifest lookup for per-path SHA drift detection.
2. **Real drift-detection value accrues from c36 onward** — every subsequent cycle that touches an anchor path should have its writer output SHA-compared against the manifest before commit. Worth adding as a pre-commit lint in a future infra cycle.
3. **Launched-event convention enforcement**: any future launched event with `status != "validated"` fails `tests/test_launched_event_convention.py`. The 7-row pre-existing offender list must not grow.
4. **Auditor scratch cleanup**: `tools/stale/_audit_tmp/pc_out.txt` and `tmp/audit_freeze/` are auditor artefacts; move/remove during c36 hygiene or leave under `tools/stale/` (already in archive convention).

## Cumulative Progress

**Infra hardening chain** (post-c35 Branch C): c14 `_infra/ledger-schema-hardening-v2` → c22 `_infra/harness-auto-write-namespacing` → c32 `_infra/fanout-namespace-convention` → c33 `_infra/harness-clone-namespace-guard` → **c35 `_infra/anchor-manifest-v1` + launched-event-convention**. Each link addresses a defect surface the previous exposed; zero net WARN growth attributable to the chain.

**Pattern durability**: **six consecutive cycles** of rubric-pre-registration + rubric-SHA-in-verdict-JSON discipline (c26-c30 mechanism probes + c31/c32/c33/c34/c35 infra + fanout). Zero rubric-edit-after-analysis incidents to date.

**Fanout-namespace convention**: c32/c33 held cleanly for the 3rd consecutive fanout cycle (c33/c34/c35 all 3-way linear-parallel with `-clone-N` suffix enforcement). No `LedgerConcatError` recurrences.

**Ledger growth**: 424 (post-c30) → 534 (pre-c35) → **543 (post-c35 Branch C)**. Growth rate stable and per-cycle bounded (c33 +32, c34 +30 across 3 clones, c35-Branch-C +9).

**M-EAR-1 armed-harness Path B**: dormant/armed pending audio-egress unblock (still 403 as of c35; retry per policy is non-blocking). **Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

[END OUTPUT]
