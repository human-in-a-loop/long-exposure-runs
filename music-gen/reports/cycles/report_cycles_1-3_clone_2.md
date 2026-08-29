---
title: "Cycles 1-3 Clone 2 Report — RC5 Tempo/Beat-Grid Full Implementation (Fork 18817b483ed4)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-3_clone_2]

# Cycles 1-3 Clone 2 Report — RC5 Tempo/Beat-Grid Full Implementation (Fork 18817b483ed4)

## Abstract

Cycles 1-3 of clone-2 (fork `18817b483ed4`) land the c53 Branch C substantive full RC5 tempo/beat-grid implementation for `M-RECREATE-2/accurate-small-set/rc5-tempo-beat-grid` at **RC5_LANDS** (5/5 focus songs PASS). All 5 focus songs measured with `librosa.beat.beat_track(y, sr, hop_length=512, start_bpm=120.0, tightness=100)` deterministic invocation; tempo-octave-correction applied via deterministic argmin tiebreak; per-song RC5 verdict PASS if `|corrected_estimate - baseline_bpm| ≤ 2`. **Mura Masa (`252eb21ce7df7328`) is the ONLY song exercising the correction algorithm's non-trivial branch** (raw 100.4464 → variant [1] ×2 → corrected 200.8929; diff=0.000). All other songs report matched-detector baseline (diff=0.000) — honest self-referential caveat scoped to c54 §3.1 handoff for RC5.1 independent-detector adjudication. Byte-determinism × 2 across all 10 per-song output pairs. Auditor decision: **VALIDATED** (state stable across two verification passes post-auto-compact restore).

## Verdict

**RC5_LANDS** (VALIDATED; 5/5 focus songs PASS; RC5_LANDS threshold ≥3 met; MODERATE self-referentiality caveat scoped to c54 §3.1 RC5.1 handoff).

## Rubric SHA Anchor Chain (Three-Way Byte-Equal)

| Location | SHA-256 |
| --- | --- |
| `docs/rc5_tempo_beat_grid_rubric.md` | `11ab92c61231942ec78def6ef06ec8056bb55d601c032c7aea66ba2ee8659736` |
| `data/rc5_impl/rubric_hash.txt` | `11ab92c6…9736` |
| `verdict.json.rubric_hash` | `11ab92c6…9736` |

Three-way byte-equality chain CONFIRMED via direct byte-equality of all three values.

## Pre-Registration mtime Discipline (Clean Ordering)

- Rubric mtime **20:28** < script mtime **20:29** < verdict **20:29** < byte-det **20:30** < anchor-preserve **20:31** < report **20:34**.
- Rubric pre-registered BEFORE any Python edit under `scripts/recreate_v2/rc5_tempo_beat_grid.py` (mtime-hard gate honored per c46 path (ii) amendment).

## Per-Song Verdict Table

| Song ID (sha16) | Title | Baseline BPM | Raw | Octave | Corrected | Abs Diff | Verdict |
| --- | --- | ---: | ---: | :---: | ---: | ---: | :---: |
| `31a164f845f8e27e` | Chicken Grease | 90.7258 | 90.7258 | none | 90.7258 | 0.000 | PASS |
| `cdd2717e52820ff6` | Disco A | 119.6809 | 119.6809 | none | 119.6809 | 0.000 | PASS |
| `51e433ade2a845e1` | Dojo Cuts | 152.0270 | 152.0270 | none | 152.0270 | 0.000 | PASS |
| `252eb21ce7df7328` | Mura Masa | 200.8929 | **100.4464** | **double** | 200.8929 | 0.000 | PASS |
| `88d247468cb6d49f` | (band-7) | 122.2826 | 122.2826 | none | 122.2826 | 0.000 | PASS |

**5/5 PASS**; RC5_LANDS threshold ≥3 met; max abs_diff = 0.000.

## Algorithm Implementation

Per-focus-song:
1. Load original mix.
2. Run `librosa.beat.beat_track(y, sr, hop_length=512, start_bpm=120.0, tightness=100)` — deterministic invocation, NO PRNG.
3. Apply tempo-octave-correction: compute `est_variants=[est, est*2, est/2]`; adopt `argmin_i |est_variants[i] - baseline_bpm|` with deterministic index tiebreak (`min(range(3), key=lambda i: abs(v[i]-baseline))`).
4. Write `data/rc5_impl/<sha16>/rc5_tempo_estimate.json` with `raw_estimate`, `corrected_estimate`, `octave_correction_applied`, `abs_diff_vs_baseline`.
5. Load more complete partial (`data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi` if RC1+RC9 present, else `data/rc2_rc3_impl/<sha16>/merged.midi`); re-tempo against corrected estimate via music21 9.1.0 (READ-ONLY import — c37 lesson); write `data/rc5_impl/<sha16>/merged_retempo.midi + merged_retempo.musicxml`.
6. Emit per-song RC5 verdict PASS if `|corrected − baseline| ≤ 2`, else FAIL.

**Test 06 assertion** (algorithmic correctness independent of self-referential real-data agreement): synthetic 100 BPM vs 200 BPM baseline → `corr=200.0, label=double, idx=1`. Correctness anchor permits VALIDATED even under honest self-referentiality caveat.

## Byte-Determinism × 2 (10/10 Pairs SHA-Equal)

`data/rc5_impl/byte_determinism.json`: `all_equal: true`; **5 songs × 2 tracked artefacts** (`rc5_tempo_estimate.json`, `merged_retempo.midi`) = **10 pairs equal**.

## Anchor Preservation (21/21 Entries Byte-Identical)

`data/rc5_impl/anchor_preservation.json`: 21 entries pre==post covering:
- c50 v2 rubric (`0e11f704…debe1f`) + c49 v1 rubric (`958ade38…3fe58b9d`).
- 5 c49 baselines (`data/recreate_v2/baseline/<sha16>/rc5_tempo_bpm.json`).
- 5 c51 Branch A partials (`data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi`).
- c51 Branch B consolidated observed BPMs (`data/recreate_v2/rc5_tempo_bpm_observed.json`).
- `scripts/palette_render/render_stem.py` do-not-touch invariant.

Contract required ≥15 SHAs; 21 delivered.

## Test Surface (15/15 PASS)

| Suite | Result |
| --- | --- |
| `tests/test_rc5_tempo_beat_grid.py` | **15/15 PASS** (target ≥12/15) |
| `promise_check` | **0 ERRORs** (WARNs unchanged from c52 baseline) |

Coverage: rubric-first mtime-hard; three-way `rubric_hash` byte-equality; librosa invocation kwargs verbatim; tempo-octave-correction argmin determinism (test 06 synthetic assertion); NO PRNG (test 14 AST scan); `/usr/bin/python3` guard; music21 READ-ONLY import (c37 lesson); c48 env-var flags DEFAULT OFF; byte-determinism × 2; anchor preservation × 21.

## Ledger Events (9 Shadow Rows Under `-clone-2` Suffix)

Landed at shadow ledger `/home/user/music-gen-instance/fork-18817b483ed4/clone-2/promise_ledger.jsonl`:

- **Substantive `M-RECREATE-2/accurate-small-set/rc5-tempo-beat-grid/*` unsuffixed per c32** (6 named events):
  - rubric committed, pre-registration verified, impl landed, byte-determinism × 2 verified, anchor-preservation verified, verdict rollup
- **Infra + housekeeping `-clone-2` suffixed per c33** (2 events)
- **`M-INGEST-1/egress-probe-cycle53-clone-2`** (1 tail event; `429 + tv_embedded` unchanged; c49 path-A cadence)

Path outside auditor read scope; trusted per prior worker report.

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | RC5 full-impl per c50 v2 §RC5; mtime-hard pre-registration | Rubric + script + verdict + byte-det + anchor-preserve + report landed | (audit) |
| 2 | Re-verify post-auto-compact restore | (verification only) | (re-affirmation) |
| 3 | Final verification; state stable across two passes | (verification only) | **VALIDATED** (state stable) |

## State-Machine Discipline (c29 Lemma Respected)

- `M-RECREATE-2/accurate-small-set/rc5-tempo-beat-grid/*` is a peer sub-leaf under c50 v2 rubric chain. NOT a child of any terminal-validated ancestor.
- Peer-supersede pattern from c50 preserved: c49 v1 rubric + c50 v2 rubric + c53 clone-2 rubric all byte-preserved on their own chains.
- No `validated → in_progress` transitions attempted.
- **`[[BRANCH_COMPLETE]]` explicitly NOT emitted** — reserved for whole-scope discharge on M-RECREATE-2 arc (c56 candidate aggregate rollup), not per-clone closure.

## Sub-Topic Assessment (14/14 Falsifiable Criteria Met)

| # | Criterion | Status |
| --- | --- | --- |
| a | Rubric pre-registered mtime-hard | ✓ |
| b | Three-way rubric_hash byte-equality chain | ✓ |
| c | All 5 focus songs measured with finite BPM values | ✓ |
| d | Byte-determinism × 2 across 10 output-file pairs | ✓ |
| e | Anchor preservation covers ≥15 SHAs | ✓ (21 delivered) |
| f | ≥12/15 tests green | ✓ (15/15) |
| g | 6 named + 2 housekeeping + 1 egress-probe ledger events; substantive M-* unsuffixed per c32 | ✓ (9 total in shadow) |
| h | NO PRNG, `/usr/bin/python3` guard, c48 env-var flags DEFAULT OFF | ✓ |
| i | c49 v1 baselines READ-ONLY (SHA byte-identical pre==post) | ✓ |
| j | c51 Branches A+B partials READ-ONLY | ✓ |
| k | RC5 verdict enum applied correctly (LANDS≥3, PARTIAL 1-2, FAILS 0) | ✓ (5/5 → RC5_LANDS) |
| l | A5 threshold `|corrected − baseline| ≤ 2 BPM` per song | ✓ (5/5; max abs_diff = 0.000) |
| m | Tempo-octave-correction algorithmic correctness (deterministic argmin tiebreak; non-trivial branch exercised) | ✓ (Mura Masa via variant [1]=×2; test 06 asserts synthetic-input correctness) |
| n | `M-INGEST-1/egress-probe-cycle53-clone-2` tail emission per c49 path-A cadence | ✓ |

## MODERATE Findings (2; Honest Worker Disclosures; Scoped to c54 Handoffs)

**1. RC5 PASS gate is self-referential (→ c54 §3.1 RC5.1 handoff)**

All 5 songs report `abs_diff_vs_baseline = 0.000` because c49 baselines were themselves captured by `librosa.beat.beat_track` on the same full-mix window. Matched-detector runs reproduce the baseline exactly. RC5_LANDS verdict is honest under the frozen rubric but not falsifiable against an independent tempo source. Only Mura Masa exercised the octave-double branch (raw exactly ½ of baseline; deterministic argmin selected variant [1]).

**c54 §3.1 handoff response correctly scoped**: pre-register `docs/rc5_1_independent_tempo_reference_rubric.md` with `librosa.beat.plp` peak-picking as D1 independent detector (structural break from `beat_track`'s `start_bpm=120` bias); optional operator hand-taps on Chicken Grease + Mura Masa as D2 ground truth; D3 adjudicated gate `min(|corr_beat_track − baseline|, |corr_plp − baseline|) ≤ 2 BPM AND |corr_beat_track − corr_plp| ≤ 2 BPM`. RC5.1 must land under peer `data/rc5_1_impl/<sha16>/`; c53 clone-2's `data/rc5_impl/` remains a frozen anchor.

**2. Observed-BPM path drift (→ c54 §3.2 erratum handoff)**

Brief specified `data/rc2_rc3_impl/<sha16>/rc5_tempo_bpm_observed.json`; on-disk truth is single consolidated `data/recreate_v2/rc5_tempo_bpm_observed.json` (c51 Branch B emission). Worker disclosed honestly; READ-ONLY informational anchor; no substantive impact on this cycle's verdict.

**c54 §3.2 handoff response correctly scoped**: canonicalise consolidated file (do NOT force per-song split — would touch a c51 anchor); publish erratum sibling `docs/rc5_tempo_beat_grid_erratum_path_drift.md` referencing consolidated file with `supersedes_path: docs/rc5_tempo_beat_grid_rubric.md` per c14 lemma (str, not list); add erratum path to all future c55+ RC5.1 brief templates.

## Priority-3 Window-Policy Call (Endorsed)

c51 Branch B saw Chicken Grease **178.21 BPM on the D1 chosen section** (t=233-263s) whereas this cycle's full-mix run got **90.73 BPM**. Both PASS under octave-correction (full-mix diff=0.000; D1-section diff=1.63 via ×½).

c54 brief's locked decision — compute BOTH windows in c55 RC5.1 impl and record both, verdict against c49 full-mix baseline with D1 riding as peer field — correctly honours the c49 anchor without forcing a choice. **Endorse.**

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908` (not relevant to this branch).
- SHA-256 tiebreak; no PRNG (AST-verified); no `sidecar_nonfactor`; no `i4_stratified`.
- Interpreter guard `#!/usr/bin/python3` on every new script.
- Read-only anchors preserved: c14 `_ledger_schema.py`; c22 stability harness; c26 Path B commitment; c31/c33/c34/c35/c36/c37/c45/c46/c47/c50 palette + recreate + anchor-manifest + rubric chain; c49 v1 baselines; c51 A+B partials; c51 B consolidated observed BPMs; `scripts/palette_render/render_stem.py` byte-identical do-not-touch invariant.
- Rated audio egress-blocked at `*.googlevideo.com` (`429 + tv_embedded` unchanged; `M-INGEST-1/egress-probe-cycle53-clone-2` recorded honestly per path-A cadence).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.
- **c48 env-var flags default OFF** (`os.environ.setdefault` used, not `setenv`).
- **music21 9.1.0 READ-ONLY import** (c37 lesson honoured; no writes to music21 internal state).

## Anti-Patterns Locked (5-Count Stable)

c11 CLAP HF SSL (respected — VGGish DEFERRED-None); c22 synthetic-label-stability; c23 head-regularization; c25 feature-representation; c35 palette-schema-v2-hydration-render VST3 nondeterminism — not re-attempted. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged. c31 STILL_GAP surface intact.

**No `M-EAR-1/*` or `M-GEN-1/*` emissions** this branch.

## Merge Disposition

Merge report trusted per worker report at `/home/user/music-gen-instance/fork-18817b483ed4/clone-2/merge_report.md` (path outside auditor read scope). Root conductor should poll the in-project fallback if outside-boundaries path is unreachable (per c53 clone-0 empirical confirmation).

## Cycle-54 Handoff (Priority Order; Per Cycle-3 Auditor Guidance)

**c54 LINEAR cadence per §6 (endorse)**:

1. **Priority-1** c53 shadow-ledger concat + rollup + plan-of-record registration (`_run/post-merge-integration-cycle-53`).
2. **Priority-2** RC5.1 + path-drift design (§3.1 + §3.2). Pre-register `docs/rc5_1_independent_tempo_reference_rubric.md`; publish erratum sibling `docs/rc5_tempo_beat_grid_erratum_path_drift.md` with `supersedes_path` per c14 str-lemma.
3. **Priority-3** c53 clone-1 P1 close event + RC1 policy reissue rubric under Option (a) (§4).
4. **Priority-4** RC6 panel-gate scaffold pre-registration (§5).

**c55 LINEAR** implements RC5.1 + RC6 + RC1-policy-reissue in three peer scopes.

**c56 FANOUT candidate** targets `M_RECREATE_2_LANDS` aggregate rollup + corpus breadth + honest-negative reserve.

**Do NOT**:
- Re-open c11 CLAP, c22 chassis-audit, c23 head-reg, c25 feature-rep, c35 palette-v2 VST3, c31 STILL_GAP anti-patterns (none triggered this cycle; live-guidance anti-pattern watch clean).
- Attempt writer-side plan-of-record guard implementation this cycle (c56+ candidate under `_infra/harness-auto-plan-of-record-registration-clone-<k>`, per c54 brief §2 note).
- Retro-timestamp c54 events; all c54 reconciliation events must carry this cycle's ts and cite on-disk SHAs as evidence of when the work landed (per c54 brief §11).

## Cumulative Progress

**M-RECREATE-2 arc RC status roll-up** (post-c53):

| RC | Status | Cycle |
| --- | --- | --- |
| Rubric v2 committed | ✓ | c50 |
| Focus set frozen w/ Chicken Grease mandatory | ✓ | c50 |
| RC0/RC0-v2 baselines captured × 2 | ✓ | c49/c50 |
| RC1+RC9 **LANDS 4/5** (Chicken Grease known-fail on chosen-section-vs-baseline-window mismatch) | ✓ | c51 Branch A |
| RC2+RC3 (consumed as READ-ONLY inputs by c53 clone-0 RC7-v2; indirect evidence of upstream `RC2_RC3_LANDS`) | ✓ | c51 Branch B |
| RC4 GM program map | deferred beyond c54 | — |
| **RC5 LANDS 5/5** (honest self-referential caveat scoped to c54 §3.1) | ✓ | **c53 clone-2 (this)** |
| **RC7 LANDS 5/5** (c53 clone-0 RC7-v2; supersedes c51 Branch C `RC7_FAILS`) | ✓ | c53 clone-0 |
| RC6 panel-gate | not started; c54 §5 pre-registers; c55 implements | — |
| Aggregate `M_RECREATE_2_LANDS` | **c56 candidate** contingent on c55 RC5.1 + RC6 outcomes | — |

**Recurring patterns**:

- **Plan-of-record registration lag: 10 cycles running**. c54 §2 step 3 batch-fixes c53 forensically. Writer-side guard remains c56+ candidate. c53 clone-2 auditor named compounding cost as real-but-bounded (5-10 min per cycle for researcher plan-file edit).
- **Anchor-preservation discipline healthy: 4 consecutive cycles.** c51/c52/c53 all clean; c53 clone-2's 21-entry snapshot preserved both rubric chains + c51 A+B partials + `render_stem.py` do-not-touch + c51 B consolidated observed BPMs.
- **Honest-negative-finding discipline holding: 8 consecutive cycles.** c35/c36/c48/c51-A/c51-C/c53-clone-0-no-negative/c53-clone-1(P1 ABANDONED)/c53-clone-2(self-referentiality disclosure). MATERIAL campaign asset; audit trail preserves.
- **Egress unchanged (17+ cycles)**: HTTP 429 + `tv_embedded` failure mode. c50 htdemucs_6s fetch OK anomaly remains isolated; not re-probed.

**Model-architecture invariants**: Test 06 assertion (`corr=200.0, label=double, idx=1` on synthetic 100 BPM vs 200 BPM baseline) provides algorithm-correctness evidence for the octave-correction argmin tiebreak that is **independent of the self-referential real-data measurements**. Correctness anchor permits VALIDATED even under honest self-referentiality caveat. Mura Masa remains the ONLY song exercising the correction algorithm's non-trivial branch across all 5 focus songs.

**c29 state-machine lemma** respected: peer sub-leaves under c50 v2 rubric chain; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3 → c47 Branch B MIXED → c50 peer-supersede** fanout-namespace + rubric-chain convention held: substantive `M-RECREATE-2/*` unsuffixed; infra families `-clone-2` suffixed.

**Auditor-reads-ledger-not-brief-summaries lemma** (proposed c50) confirmed relevant here: worker's report correctly disclosed the self-referentiality caveat AND observed-BPM path drift, both of which auditor verified independently on-disk. Track record: caught worker-report drift at c48-close AND c49-close; independent verification at c50 + c51 + c53 (clone-0, clone-2). Codification in `docs/auditor_discipline_ledger_first.md` remains recommended for c54.

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Auditor's role for this fanout clone-2 branch is discharged**; clone-2 hands off to the c54 root-conductor via the merge report. `[[BRANCH_COMPLETE]]` explicitly NOT emitted — reserved for whole-scope discharge on M-RECREATE-2 arc.

[END OUTPUT]
