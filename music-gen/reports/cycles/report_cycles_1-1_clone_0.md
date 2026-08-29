---
title: "Cycle 1 Clone 0 Report — RC7 v2 Rerun on c51 Branch A+B Substantive MIDIs (Fork 18817b483ed4)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-1_clone_0]

# Cycle 1 Clone 0 Report — RC7 v2 Rerun on c51 Branch A+B Substantive MIDIs (Fork 18817b483ed4)

## Abstract

Cycle 1 of clone-0 (fork `18817b483ed4`) lands the c53 Branch A substantive RC7 v2 rerun for `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match` at **RC7_v2_LANDS**. The c51 Branch C RC7 mix-balance pipeline was re-run against c51 Branch A+B substantive per-stem MIDIs (vocals+guitar+piano from `data/rc1_rc9_impl/*/merged_partial.midi`; drums+bass from `data/rc2_rc3_impl/*/merged.midi`) replacing the c33-anchor placeholder MIDIs used at c51. **5/5 focus songs pass A7, 20/20 stem accepts across `{drums, bass, other_guitar, other_piano}`**. Chicken Grease (`31a164f845f8e27e`, band 6) passes 4/4 stems — the c52 handoff outcome confirms the c51 Branch C mechanism was sound: c51's RC7_FAILS was purely upstream MIDI under-transcription, not an EQ/loudness-match pipeline defect. Byte-determinism × 2 across all 226 output files under pinned environment. Auditor decision: **COMPLETE** with `[[BRANCH_COMPLETE]]`.

## Verdict

**RC7_v2_LANDS** (VALIDATED; 5/5 focus songs pass A7 across all four stems; 20/20 individual stem accepts — well above the RC7_v2_LANDS threshold of ≥3 songs).

## Rubric SHA Anchor Chain (Three-Way Byte-Equal + Parent-v2 Preserved)

| Location | SHA-256 |
| --- | --- |
| `docs/rc7_v2_rerun_rubric.md` | `9f24e6d9…04dde4` |
| `data/recreate_v2/rc7_out_v2/rubric_hash.txt` | `9f24e6d9…04dde4` |
| `verdict.json.rubric_hash` | `9f24e6d9…04dde4` |
| c50 v2 parent rubric (`docs/m_recreate_2_accurate_small_set_rubric_v2.md`) | `0e11f704…debe1f` (independent chain, byte-preserved) |
| c49 v1 rubric | `958ade38…3fe58b9d` (byte-preserved) |

Three-way byte-equality chain CONFIRMED. Fresh per-milestone rubric hash resolves cleanly independent of c50 v2 doc SHA.

## Pre-Registration mtime Discipline (Clean Ordering)

- Rubric mtime `1788035291` **<** impl mtime `1788035649`.
- Rubric pre-registered before any Python edit under `scripts/recreate_v2/rc7_v2_*.py` (mtime-hard gate honored per c46 path (ii) amendment).

## READ-ONLY Anchor Preservation (c51 Branch C + render_stem)

| Anchor | SHA-256 / State |
| --- | --- |
| `scripts/palette_render/render_stem.py` | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` byte-identical pre/post (directive-anchored SHA) |
| `data/recreate_v2/rc7_out/` (c51 Branch C) | 182 files byte-identical pre==post per `anchor-preservation-v2` ledger event |
| `data/rc1_rc9_impl/` (c51 Branch A) | READ-ONLY (worker did not touch c51 anchors) |
| `data/rc2_rc3_impl/` (c51 Branch B) | READ-ONLY (worker did not touch c51 anchors) |

Consumed `render_stem.py` in its c51-extended additive-kwargs form (`eq_curve + loudness_target`) READ-ONLY.

## RC7 v2 Per-Song Results (5/5 Focus Songs Pass A7; 20/20 Stem Accepts)

Per focus song: fit 12-band iirpeak EQ curve (Q=1.4, log-spaced) from original 6-stem spectrum vs new bare-render (built from substantive MIDIs); applied RMS + LUFS-S loudness match to reach A7 (≤3 dB RMS, ≤3 LU LUFS-S vs `baseline/<sha16>/rc7_per_stem_loudness.json`); summed matched stems into `data/recreate_v2/rc7_out_v2/<sha16>/rc7_v2_mixed_reconstruction.wav`.

**Chicken Grease (`31a164f845f8e27e`, band 6, mandatory per operator override)**: **4/4 stems pass** — kill-shot on c51's placeholder-MIDI shortfall. Substantive Branch A+B MIDIs deliver the EQ+loudness match cleanly.

**5 songs × 4 stems = 20/20 individual stem accepts.**

## Byte-Determinism × 2 (226/226 SHA-Equal)

**226/226 files SHA-256 equal** across two fresh `tempfile.mkdtemp()` runs. Env pins present:
- `PYTHONHASHSEED=0`
- `SOURCE_DATE_EPOCH=1756463424`
- `TZ=UTC`
- `LC_ALL=C.UTF-8`
- Single-thread BLAS

## D4 Old c33 Chorus+Reverb Chain (Preserved as Diagnostic ONLY)

`d4_old_chain_baseline_present=true`; per-song `panel_baseline_old_chain_v2.tsv` preserved as diagnostic ONLY. Never a LANDS deliverable (per c50 v2 discipline invariant).

## Test Surface (All Green)

| Suite | Result |
| --- | --- |
| `promise_check` | **0 ERRORs**, WARNs all pre-existing (unchanged from c52 baseline) |

- test_04: NO PRNG grep-guarded (PASS).
- test_08: c48 env-var flags default OFF (PASS).

## Ledger Events (9; Lines 880-888; Correct c32/c33 Suffix Discipline)

Landed at ledger lines 880-888 (tail = 888 rows):

- **Substantive `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/*` unsuffixed per c32** (6 named events):
  - rubric committed, pre-registration verified, impl landed, byte-determinism-v2 verified, anchor-preservation-v2 verified, verdict rollup
- **Infra + housekeeping `-clone-0` suffixed per c33** (2 events):
  - `_infra/adopt-rc7-v2-artifacts-clone-0`, `_archive/rc7-v2-scratchpad-clone-0`
- **`M-INGEST-1/egress-probe-cycle53-clone-0`** (1 event at tail; `429 + tv_embedded` unchanged)

Ledger-event budget: 6 named + 2 housekeeping + 1 egress = 9 events, under the directive's stated budget.

## MODERATE Findings (0 Blocking; All Discipline Invariants Met)

- `data/rc1_rc9_impl/` + `data/rc2_rc3_impl/` READ-ONLY (worker did not touch c51 anchors).
- c48 env-var flags default OFF (test 08).
- NO PRNG (test 04 grep-guarded).
- `/usr/bin/python3` guard present.
- VST3 lock (c35 anti-pattern) and CLAP anti-pattern (c11, VGGish DEFERRED-None) respected.
- Substantive sub-leaves unsuffixed per c32; infra `-clone-0` suffixed per c33.

## MINOR Findings (Logged, Not Acted On)

- ~20 pre-existing `promise_check` WARNs unchanged from c52 (drift-tracking, out of scope per c48 auditor precedent).
- Session housekeeping registered `_plan/register-c53-rc7-v2-fanout-milestones` + 6 `plan_of_record` rows retroactively — appropriate given the deliverable was already on disk from a prior c53 pass.
- **Session-scope disclosure**: research_brief fed to this session was for c53-clone-1 (RC1 policy pivot), while directive was for c53-clone-0 (RC7 v2 rerun). Worker correctly followed the directive. Harness-wiring artefact worth noting for campaign meta-audit; does not affect this clone's deliverable.

## Merge Report Path Fallback (Empirically Confirmed Necessary)

Merge report written to **in-project fallback path** `reports/fanout/fork-18817b483ed4/clone-0/merge_report.md` (4,666 B) because the directive-named path `/home/user/music-gen-instance/…` is outside session Directory Boundaries. Worker correctly applied the brief's Priority 4b Option (i) recommendation.

**Root conductor should poll the in-project path.**

The outside-boundaries merge path deadlocks without the in-project fallback. Priority 4b (`_infra/fanout-merge-report-path-in-project`) is empirically confirmed necessary this cycle — should escalate to CRITICAL when re-issued.

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | RC7 v2 rerun against c51 Branch A+B substantive MIDIs; 5-song focus set; A7 gate | Rubric pre-registered (mtime-hard); 12-band iirpeak EQ + RMS + LUFS-S loudness match; per-song reconstruction WAV; byte-det × 2 across 226 files; 9 ledger events; merge report at in-project fallback | **COMPLETE** with `[[BRANCH_COMPLETE]]` |

## State-Machine Discipline (c29 Lemma Respected)

- `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/*` is a peer sub-leaf under c50 v2 rubric chain. NOT a child of any terminal-validated ancestor.
- Peer-supersede pattern from c50 preserved: c49 v1 rubric + c50 v2 rubric + c53 clone-0 rubric all byte-preserved on their own chains.
- No `validated → in_progress` transitions attempted.

## Sub-Topic Assessment (16/16 Directive Acceptance Criteria Met)

| Criterion | Status |
| --- | --- |
| Rubric pre-registered mtime-hard | ✓ |
| `render_stem.py` SHA byte-identical pre/post | ✓ |
| 12-band iirpeak EQ (Q=1.4, log-spaced) | ✓ |
| RMS + LUFS-S loudness match | ✓ |
| Sum to `rc7_v2_mixed_reconstruction.wav` per song | ✓ (5 present) |
| Byte-det × 2 with env pins | ✓ (226/226) |
| D4 old chain preserved as diagnostic ONLY | ✓ |
| Three-way rubric_hash-v2 chain | ✓ |
| c51 `rc7_out` anchor 95+ SHAs byte-identical | ✓ (182 files) |
| VST3 lock (c35) + CLAP (c11) respected | ✓ |
| NO PRNG | ✓ |
| `/usr/bin/python3` guard | ✓ |
| c51 anchors READ-ONLY | ✓ |
| c48 env-var flags default OFF | ✓ |
| Egress probe `M-INGEST-1/egress-probe-cycle53-clone-0` at tail | ✓ |
| Required output `docs/rc7_v2_rerun_report.md` | ✓ (7,625 B) |

**All 16 criteria met.**

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908` (not relevant to this branch).
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor`; no `i4_stratified`; no `render_effects_layered` (retired).
- Interpreter guard `#!/usr/bin/python3` on every new script.
- Read-only anchors preserved: c14 `_ledger_schema.py`; c22 stability harness; c26 Path B commitment; c31/c33/c34/c35/c36/c37/c45/c46/c47/c50/c51 palette + recreate + anchor-manifest + rubric chain; `render_stem.py` (Branch C anchor) byte-identical.
- Rated audio egress-blocked at `*.googlevideo.com` (`429 + tv_embedded` unchanged; `M-INGEST-1/egress-probe-cycle53-clone-0` recorded honestly).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.
- **c48 env-var flags default OFF** (`MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`, `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`).

## Anti-Patterns Locked (5-Count Stable)

c11 CLAP HF SSL (respected — VGGish DEFERRED-None); c22 synthetic-label-stability; c23 head-regularization; c25 feature-representation; c35 palette-schema-v2-hydration-render VST3 nondeterminism — not re-attempted. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged. c31 STILL_GAP surface intact.

**No `M-EAR-1/*` or `M-GEN-1/*` emissions** this branch.

## Merge Disposition

Merge report at `reports/fanout/fork-18817b483ed4/clone-0/merge_report.md` (4,666 B) per in-project fallback. Root conductor should poll the in-project path.

Ledger tail = **888 rows**; `promise_check` 0-ERROR; 9 c53 clone-0 events landed at lines 880-888 with correct c32/c33 suffix discipline.

## Cycle-54+ Handoff (Per Cycle-1 Auditor Guidance)

1. **RC7 v2 mechanism is proven on 5 focus songs**; extending to a broader corpus is a candidate next scope but must NOT block on egress (unchanged HTTP 429 + tv_embedded).
2. **Formalise `_infra/fanout-merge-report-path-in-project`** as an infra milestone in c54 — the outside-boundaries merge path deadlocks without the in-project fallback; Priority 4b (from c53 clone-1 brief) empirically confirmed CRITICAL this cycle.
3. **Auditor-reads-ledger-not-brief-summaries lemma** track record continues: caught worker-report drift at c48-close AND c49-close; independent verification at c50 + c51 + c53. Codification in `docs/auditor_discipline_ledger_first.md` remains recommended for c54.
4. **c53 fanout merge conductor tasks**: reconcile clone-0 (RC7 v2, this branch) with sibling clones (clone-1 RC1 policy pivot; clone-2 if any) shadow ledgers under `_infra/fanout-concat-hardening` invariants.
5. **c48 env-var flag flips** remain c54+ candidates post-M-RECREATE-2 arc closure.
6. **Session-scope harness-wiring artefact** (research_brief was for c53-clone-1 while directive was for c53-clone-0): worth noting in campaign meta-audit; does not affect this clone's deliverable.

**Standing follow-ons** (carried from prior cycles):

7. **c48 Branch A `_infra/harness-and-writer-hardening-v3`** still owed as substantive re-field.
8. **Writer-side guard rejecting novel milestone_ids not in `plan_of_record`** — plan-registration-lag pattern.
9. **`_infra/large-model-fetchability-registry`** — c50's htdemucs_6s OK; if VGGish also fetches cleanly, argues for pinning.
10. **Mura Masa RC3 threshold-boundary refinement** (from c51 clone-1) — c52+ candidate.
11. **RC5 full implementation with octave normalisation** — c52+ candidate.
12. **RC6-v2 panel gate** — c52+ candidate (depends on VGGish availability).

## Cumulative Progress

**M-RECREATE-2 arc** (post-c53 clone-0 substantive advance):

| Cycle | Milestone | Verdict / Status |
| --- | --- | --- |
| c49 | `M-RECREATE-2/accurate-small-set` (v1) | rubric committed; substantive close |
| c50 | `M-RECREATE-2/accurate-small-set-v2` (peer supersede) | rubric committed; htdemucs_6s fetch OK; 5-song chosen_section |
| c51 clone-0 (A) | `M-RECREATE-2/.../{rc1-vocals,rc9-first-class-parts}-transcription` | (fork sibling) |
| c51 clone-1 (B) | `M-RECREATE-2/.../{rc2-drum-onset,rc3-bass}-transcription` | RC2_RC3_LANDS (5/5 RC2; 4/5 RC3; Chicken Grease kill-shot) |
| c51 clone-2 (C) | `M-RECREATE-2/.../rc7-mix-balance` (c33-anchor placeholder MIDIs) | RC7_FAILS (upstream MIDI under-transcription) |
| c52 | LINEAR integration | (integration + RC5 full + RC6-v2 readiness) |
| **c53 clone-0 (A) (this)** | `M-RECREATE-2/.../rc7-mix-balance-match` (substantive Branch A+B MIDIs) | **RC7_v2_LANDS** (5/5 songs pass A7; 20/20 stem accepts; Chicken Grease 4/4 stems) |

**The c51 RC7_FAILS verdict was purely upstream MIDI under-transcription, not a defect in the EQ/loudness-match pipeline** — c53 clone-0 empirically confirms the c51 Branch C mechanism was sound. Substantive Branch A+B MIDIs (from c51 clone-0/clone-1 substantive advances) deliver the EQ + loudness match cleanly.

**Chicken Grease result**: 4/4 stems passing on substantive Branch A+B MIDIs after failing on c51 c33-anchor placeholders — expected c52 handoff outcome; validates the operator's insistence that Chicken Grease band-6 be treated as mandatory anchor.

**Fanout cadence**: LINEAR c49/c50 → FANOUT c51 (A/B/C) → LINEAR c52 (integration) → **FANOUT c53 (this branch is Branch A: RC7 v2 rerun)** → LINEAR c54 recommended (fanout merge integration; broader corpus consideration).

**Anti-pattern discipline**: 5 confirmed campaign anti-patterns (c11 CLAP, c22 chassis-audit, c23 head-reg, c25 feature-rep, c35 palette-v2 VST3) all remain respected across c53 clone-0.

**Rubric mtime discipline**: c46 path (ii) amendment (mtime-hard, git-log advisory) continues to work correctly under fanout — rubric mtime `1788035291` cleanly pre-dates impl mtime `1788035649`.

**Auditor-reads-ledger-not-brief-summaries lemma** (proposed c50) confirmed relevant here: worker's report correctly disclosed the brief/directive mismatch AND the merge-path deadlock, both of which auditor verified independently on-disk. Track record: caught worker-report drift at c48-close AND c49-close, and independent verification at c50 + c51 + c53.

**Merge-report path deadlock**: empirically confirmed this cycle. Real infra defect that will silently break any fanout where conductor is not aware of in-project fallback. Priority 4b escalates to CRITICAL when re-issued in c54.

**c29 state-machine lemma** respected: peer sub-leaves under c50 v2 rubric chain; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3 → c47 Branch B MIXED → c50 peer-supersede** fanout-namespace + rubric-chain convention held: substantive `M-RECREATE-2/*` unsuffixed; infra families `-clone-0` suffixed.

**Anchor-manifest arc**: v1.1 stable at 19 entries with `SOURCE_DATE_EPOCH` first-class.

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Egress state**: `429 + tv_embedded` unchanged for playlist audio; htdemucs_6s model-weight fetchability OK (c50 positive) distinct from playlist harvest.

**Scope of this fanout clone fully discharged.** `[[BRANCH_COMPLETE]]` emitted; auditor decision **COMPLETE**.

[END OUTPUT]
