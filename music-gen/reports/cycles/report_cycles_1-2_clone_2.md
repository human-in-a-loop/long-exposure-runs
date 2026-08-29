---
title: "Cycles 1-2 Clone 2 Report — M-RECREATE-1/second-real-audio-batch (Fork 33a2a8003c84)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-2_clone_2]

# Cycles 1-2 Clone 2 Report — M-RECREATE-1/second-real-audio-batch (Fork 33a2a8003c84)

## Abstract

Cycles 1-2 of clone-2 (fork `33a2a8003c84`) close `M-RECREATE-1/second-real-audio-batch` at **BATCH_LANDS**. Cycle 1 executed the 5-song batch pipeline via SHA-256 tiebreak per rating bucket (excluding the c37 clone-0 song), consuming c37 `scripts/recreate_v0/*` machinery read-only, using the Stage-06 pretty_midi fallback as-is, and producing positive `mel_l1_db` effects deltas on all 5 songs (+2.879 to +7.983 dB; mean +5.04 dB). Cycle 2 is c30-codified verification-only standby (zero writes; auditor decision **COMPLETE**; `[[BRANCH_COMPLETE]]` emitted). 15/16 in-clone rubric criteria PASS; the 16th (git-log gate) is legitimately `MERGE_DEFERRED` to the root conductor per known clone-environment `git add` refusal.

## Verdict

**BATCH_LANDS** (VALIDATED at cycle 1; **COMPLETE** at cycle 2 standby; `[[BRANCH_COMPLETE]]`).

## Rubric SHA Anchor Chain (Three-Way Byte-Equal)

| Location | SHA-256 |
| --- | --- |
| `docs/recreate_v0_batch_rubric.md` | `be65f7cb37f71c4613afceb70dafa03a1bc68a384f4b51639127b4d5256b718d` |
| `data/recreate_v0_batch/rubric_hash.txt` | `be65f7cb…b718d` |
| `verdict.json.rubric_hash` | `be65f7cb…b718d` |

Rubric mtime `08:50` < earliest `scripts/recreate_v0_batch/*.py` mtime `08:51+`. git-log gate **MERGE_DEFERRED** (clone environment refuses `git add`/`git commit`; worker honestly recorded rather than fabricating; conductor verifies rubric-first commit order post-integration per c38 precedent).

## 5-Song Selection (SHA-256 Tiebreak Per Bucket; c37 Clone-0 Song Excluded)

Songs selected via SHA-256 tiebreak from each of the four rating buckets (band-4, band-5, band-6, band-7) with an extra tiebreak within the largest bucket, excluding `corpus/ratings/7/016__LOCAL__05_02.mp3` (c37 clone-0 song). All 5 songs complete the 8-stage c37 pipeline (decode → chunker → tagger sidecar → htdemucs → basic-pitch × 3 → score merge → fluidsynth bare-MIDI → cycle-9 DawDreamer effects).

## Batch Verdict Numerics

| Metric | Result |
| --- | --- |
| n_pipeline_ok | **5/5** |
| n_byte_det_x2 | **5/5** |
| n_positive_mel_delta | **5/5** (per-song mel deltas +2.879 to +7.983 dB; mean +5.04) |
| Cross-band table dimensions | 5 rows × 14 numeric cols |

Cross-band table includes `mel_l1_db + spectral_centroid_rmse_hz + rms_env_rmse + lufs_m_rmse` per the brief, plus `n=5 exploratory caveat` literal on every correlation row.

## Cross-Band Correlations (n=5 Sample-Size Caveat Literal on Every Row)

On-disk `data/recreate_v0_batch/cross_band_correlation.json` and `docs/recreate_v0_batch_report.md` (correct values):

| Metric | r (band vs improvement) |
| --- | --- |
| mel_l1_db | −0.483 |
| spectral_centroid_rmse_hz | +0.911 |
| rms_env_rmse | −0.199 |
| lufs_m_rmse | −0.695 |

MINOR-tier drift note: worker's prior compacted-session narrative-to-auditor text cited stale correlation numbers (mel −0.180, spec +0.858, rms −0.535, lufs −0.826); on-disk artefacts show the correct values above. All on-disk consumers internally coherent; narrative-vs-artefact drift only, not a scientific defect.

## Byte-Determinism × 2 (20/20 SHA Pairs Matched)

5 songs × 4 anchors (`merged.musicxml`, `merged.midi`, `bare_midi.wav`, `effects.wav`) = 20 anchor SHAs; all byte-equal across two independent runs (`determinism_check.json.all_equal = true`).

## Anchor Preservation (18/18 c37 Read-Only Anchors Byte-Identical)

`anchor_preservation.json`: 18 anchors under `scripts/recreate_v0/*`, `unchanged: true`, `changed: {}`. Zero writes under c37 clone-0's machinery; read-only import via `PYTHONPATH` per rubric §7.

## preview_untrained_ear Caveat (v1-Branch Conditional Handling)

Branch A's v1 report landed mid-execution at 09:07; clone-2 report cites `docs/ear_real_label_training_v1_report.md` **by document path only**, never programmatically importing v1 model, `verdict.json`, or `corn_head_v1.pt`. Falls back to v0 caveat citation (`M-EAR-1/real-label-training-v0 → EAR_v0_INSUFFICIENT` per c36) if the v1 report path is not present. Pattern crystallised for reuse across c39 HS-2 and future recreation cycles.

## Test Surface

| Suite | Result |
| --- | --- |
| `tests/test_recreate_v0_batch.py` | **15/15 PASS** (exceeds ≥12 minimum) |
| `python3 -m long_exposure.tools.promise_check .` | **0 ERRORs** (pre-existing WARNs only; no new WARNs) |
| `org_check` | **0 ERRORs** (no new WARNs introduced) |

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | Ship the milestone under frozen 3-verdict rubric | 5-song batch pipeline; BATCH_LANDS with 5/5 positive mel deltas; 10 shadow-ledger rows | VALIDATED |
| 2 | Verification-only standby | Honest low-output; refused to fabricate activity or adopt forward-looking c39 scope | **COMPLETE** (`[[BRANCH_COMPLETE]]`) |

## State-Machine Discipline (c29 Lemma Respected)

`M-RECREATE-1/second-real-audio-batch` is a peer sub-milestone under M-RECREATE-1. NOT a child of terminal-validated c37 clone-0 `M-RECREATE-1/first-real-audio`. c29 lemma preserved; ledger topology stays a DAG.

## Ledger Events (10 Shadow Rows Under `-clone-2` Suffix; Cycle 2: 0)

Six substantive `M-RECREATE-1/second-real-audio-batch/*` events auto-suffixed `-clone-2` + 4 housekeeping under `-clone-2` per c33 writer-guard behavior:

1. `_run/cycle_38_launched-clone-2` (`status: validated` per c35 Branch C codified convention)
2. `_plan/recreate_v0_batch_rubric_frozen-clone-2`
3. `_infra/egress-probe-cycle-38-clone-2`
4. `M-RECREATE-1/second-real-audio-batch-clone-2` (in-progress; auto-suffixed by c33 writer-guard)
5. `M-RECREATE-1/second-real-audio-batch/song-selection-clone-2`
6. `M-RECREATE-1/second-real-audio-batch/pipeline-executed-clone-2`
7. `M-RECREATE-1/second-real-audio-batch/byte-determinism-verified-clone-2`
8. `M-RECREATE-1/second-real-audio-batch-clone-2` (validated verdict roll-up, `BATCH_LANDS`)
9. `_run/cycle_38_closed-clone-2`
10. `_archive/cycle-38-scratch-clone-2` + `_infra/adopt-cycle38-tests-clone-2` (housekeeping pair)

Cycle 2: zero. `validated → in_progress` forbidden per c29 lesson.

## Merge Disposition (Root-Conductor Post-Merge Validation Checklist)

Merge report at `/home/user/music-gen-instance/fork-33a2a8003c84/clone-2/merge_report.md` for root conductor pickup.

1. Read 10-row shadow ledger; reconcile with clone-0's ledger for the same fork.
2. `git add` + `git commit` on-disk artefacts in rubric-first order (`docs/recreate_v0_batch_rubric.md` first, then `scripts/recreate_v0_batch/*`, then `data/recreate_v0_batch/*`, then `docs/recreate_v0_batch_report.md`, then `tests/test_recreate_v0_batch.py`); validate git-log gate post-commit.
3. Run `promise_check`; expect 0 ERRORs.
4. Verify `_manager/fanout-namespace-convention-discrepancy` open ticket (c33 writer-guard auto-suffixes substantive `M-*` labels contrary to c32 convention doc); resolution deferred to c40+ (narrow guard OR update doc).
5. Write `merge_report.md` at the fork-clone path for root conductor pickup.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908` (not relevant to this branch).
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor`.
- Interpreter guard `#!/usr/bin/python3` on every new script.
- Read-only anchors preserved: 18/18 under `scripts/recreate_v0/*` (c37 clone-0 machinery), c9 DawDreamer effects chain, c22 stability harness, c26 Path B commitment, c31/c33/c34/c35/c36 palette anchors.
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403; retry cadence at conductor level; not required — 5 songs are on-disk operator-delivered corpus).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.

## Anti-Patterns Locked (5-Count Stable)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted. c31 STILL_GAP / c35 A anti-pattern surface intact. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged.

**Cycle-2 discipline** correctly avoided the "gold plate" anti-pattern by refusing to re-do validated work, refusing to adopt forward-looking c39 scope not assigned to this clone, and refusing to fabricate an activity log where none was warranted.

## Effects-Chain Band-Selectivity Signal (Deferred to c40+)

Per-song mel deltas span 2.7× (+2.88 to +7.98 dB across 5 songs), suggesting the c9 pinned effects chain is not equally-well-tuned across musical-content classes. Queued as `_manager/effects-chain-band-selectivity` for c40+ opportunistic pickup, or promoted to urgent if c39 HS-2 (n=37) shows per-band mel-delta failures.

## Cycle-39 Handoff (Forward-Looking, Owned by c39 Fanout Not This Branch)

Per research brief:

1. **HS-1 `M-EAR-1/real-label-training-v1/out-of-fold-cross-band`** — analytical study of the SB1/SB2 partial-corpus failures under out-of-fold band evaluation.
2. **HS-2 `M-RECREATE-1/full-corpus-recreation`** — extend to n=37 (or 42 pooled with c38 clone-2 batch) to establish first full-corpus real-audio recreation measurement with cross-band effects-delta trends. G1 spine promotion: c37 (n=1) → c38 (n=5) → c39 (n=37/42).

**c39 workers accept whatever the writer emits** re namespace convention; merge conductor to resolve `_manager/fanout-namespace-convention-discrepancy` durably at c40+.

## Cumulative Progress

**M-RECREATE-1 arc**:

| Cycle | Milestone | Verdict | Songs |
| --- | --- | --- | --- |
| c37 clone-0 | `M-RECREATE-1/first-real-audio` | RECREATION_LANDS | n=1 (band-7 song 016) |
| c38 clone-2 (this) | `M-RECREATE-1/second-real-audio-batch` | **BATCH_LANDS** | n=5 (SHA-256 tiebreak per bucket) |
| c39 HS-2 (forward) | `M-RECREATE-1/full-corpus-recreation` | (target) | n=37 (or 42 pooled) |

**G1 spine promotion is on track**: c37 (n=1) → c38 (n=5) → c39 HS-2 (n=37 target) will establish the first full-corpus real-audio recreation measurement, complete with cross-band effects-delta trends.

**Pre-registration discipline holds** across three consecutive real-audio recreation cycles: frozen rubric-first commit order + mtime-gate + git-log-gate (with MERGE_DEFERRED clone-env accommodation) has become the campaign's stable pattern for adjudication-heavy work.

**preview_untrained_ear caveat handling** crystallised: v1-branch cites Branch A v1 report by document path only, never imports v1 model or verdict.json programmatically; v0-branch cites c36 M-EAR-1/real-label-training-v0 INSUFFICIENT verdict. Pattern reusable across c39 HS-2 and future recreation cycles.

**Verification-only cycle discipline** reinforced at cycle 2: worker's honest "no new work performed this session" self-report is correct professional conduct at cycle tail. `[[BRANCH_COMPLETE]]` emitted per auditor role definition (milestone validated AND scope fully discharged).

**Namespace convention discrepancy** (c33 writer-guard auto-suffixes substantive `M-*` while c32 convention doc says unsuffixed) remains open as `_manager/fanout-namespace-convention-discrepancy`; merge conductor to resolve durably at c40+.

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG. **G5 collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

[END OUTPUT]
