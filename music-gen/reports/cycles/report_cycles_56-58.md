---
title: "Cycles 56-58 Report — c50 Close Correction + M-RECREATE-2 Rubric-v2 Peer-Supersede (Root Sequential)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_56-58]

# Cycles 56-58 Report — c50 Close Correction + M-RECREATE-2 Rubric-v2 Peer-Supersede (Root Sequential)

## Abstract

Cycles 56-58 constitute a root-conductor sequential cycle discharging **c50 close-correction priorities** on top of the c49 substantive close plus the operator's M-RECREATE-2 material re-scope (RC7/RC8/RC9 + D1-D4 + A7-A8). All five brief priorities landed on-disk with independent verification. `promise_check` advanced 6 ERRORs → **0** via ledger line 836 (`_plan/register-c49-substantive-and-probe-milestones`) — no content change to any prior event. **M-RECREATE-2 v2 rubric peer-supersede lands cleanly** at SHA `0e11f704…debe1f` with c49 v1 rubric SHA `958ade38…3fe58b9d` preserved byte-identical; both chains coexist under the c14 supersede-with-`supersedes_path`-as-str lemma. **htdemucs_6s fetch OK** — the first successful large-model window in the campaign — is honestly recorded (HTTP 200 via workspace proxy; byte-determinism × 2 across 30 stems = 5 songs × 6 stems); D3 unblocked for c51 Branch A. All 30/30 tests PASS.

## Verdict

**c50 CLOSE-CORRECTION VALIDATED** (auditor decision at cycle 58; all 5 brief priorities landed; 30/30 tests PASS; `promise_check` 0-ERROR).

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 56 | Frame c50 close-correction priorities on top of c49 substantive + operator M-RECREATE-2 re-scope | (no worker session per cycle table) | (no audit) |
| 57 | Execute Priority 1-5 landings | Ledger line 836 `_plan/register-c49-substantive-and-probe-milestones`; test extensions; §11 addendum; v2 rubric supersede; htdemucs_6s fetchability window; RC7-RC9 stubs; 6 new v2 stubs; egress probe + housekeeping | (Priority 1-5 landed) |
| 58 | Independent on-disk verification per c46 auditor-reads-rubric-off-disk + c48 auditor-reads-ledger-off-disk lemmas | Ledger + rubric SHAs + mtime discipline + focus_set_v2 + RC0-v2 baseline + 30/30 tests all verified byte-exact | **VALIDATED** |

## Priority 1 — c49 Close Correction (LANDED)

- `wc -l promise_ledger.jsonl` = **847** (was 835 at c49 close; +12 c50 events).
- `python3 -m long_exposure.tools.promise_check .` returns **0 ERRORs** (was 6 at c49 close).
- All 6 c49 forward-reference ERRORs resolved by ledger line 836 (`_plan/register-c49-substantive-and-probe-milestones`). **No content change to any prior event.**
- WARN count = 2591 (pre-existing figure-under-docs drift; NOT c50-introduced).

## Priority 2 — Test-Scope Mismatch Fix (LANDED)

- `tests/test_c48_shadow_ledger_reconciliation.py` extended to 11 cases.
- **`test_11_promise_check_zero_error_via_cli_verified`** is the belt-and-suspenders check.
- All 11 PASS under fresh invocation.

## Priority 3 — c49 Report §11 Addendum (LANDED)

- `docs/c49_worker_report.md` grows §11 with handoff.
- **§1-§10 preserved byte-identical** (asserted by `test_c50 test_07`).
- Report head first-5 lines verified byte-stable.

## Priority 4 — M-RECREATE-2 Rubric-v2 Supersede (LANDED)

- **v2 rubric SHA**: `docs/m_recreate_2_accurate_small_set_rubric_v2.md` = `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f` on disk. Matches `data/recreate_v2/rubric_hash_v2.txt` content byte-equal.
- **c49 v1 rubric SHA `958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d` preserved byte-identical** on disk. v1 chain intact — no drift.
- **mtime discipline VERIFIED**: v2 rubric mtime `1788030358` < every new v2/RC7-RC9 stub mtime (1788030376-1788030423). c49 v1 stubs (e.g., `rc1_vocals_transcription.py` mtime `1788028499`) predate the v2 rubric — untouched, as expected under peer-supersede pattern.
- **`_plan/m-recreate-2-rubric-v2-supersede`** (line 838) carries `supersedes_path` field as **str** (not list) — c14 lemma respected.

### Priority 4b — Chosen-Section Landings

- `focus_set_v2.json` on disk: **5 songs**; `chosen_section` populated for all 5.
- **Chicken Grease** `31a164f845f8e27e` band-6 with `chosen_section = {t_start_s=233.639, t_end_s=263.639, combined_score=1.604, weights={w_rms=0.5, w_onset=0.5}}` — meaningfully-late window (peak-30s per D1), NOT sparse-first-30s baseline.
- c49 v1 `focus_set.json` unchanged.

### Priority 4c — RC0-v2 Baseline (htdemucs_6s Large-Model Window)

- `rc7_per_stem_loudness.json` + `rc8_chosen_section_verified.json` + `rc9_6stem/` per-song all present.
- **Byte-determinism × 2** pinned in `rc9_6stem_byte_determinism.json`.
- **htdemucs_6s fetch OUTCOME OK** — verified in `fetchability_htdemucs_6s.jsonl`:
  - HTTP 200 via workspace proxy.
  - Model loaded with 6 sources (drums, bass, other, vocals, guitar, piano).
  - Byte-det × 2 PASS on all 5 songs (30 stems total).
- **First large-model fetchability window in the campaign** — new empirical evidence; D3 unblocked for c51 Branch A.

### Priority 4d — 6 New v2 Stubs (LANDED)

- `rc1_v2_hybrid.py`, `rc4_v2_gm_program_map.py`, `rc6_v2_panel_gate.py`, `rc7_mix_balance.py`, `rc8_section_selection.py`, `rc9_first_class_parts.py` all present.
- Spot-checked `rc7_mix_balance.py`: `/usr/bin/python3` guard, `RC_ID`, `ACCEPTANCE_CRITERIA`, `BASELINE_ANCHOR_PATH`, `RUBRIC_HASH_PATH` all present; `raise NotImplementedError("c51+ branch")`.
- **c49 v1 stubs untouched**.

## Priority 5 — Egress Probe + Housekeeping (LANDED)

- `M-INGEST-1/egress-probe-cycle50` (line 842) with HTTP 429 + tv_embedded + `htdemucs_6s_fetch_status=OK` notation.
- `_run/cycle_50_closed` + `_archive/cycle-50-scratch` + `_infra/adopt-cycle50-tests` at tail.
- Playlist audio egress-blocked (unchanged); htdemucs_6s model-weight fetchability distinct and OK.

## Test Surface (30/30 PASS)

| Suite | Result |
| --- | --- |
| `tests/test_c48_shadow_ledger_reconciliation.py` | **11/11 PASS** |
| `tests/test_c50_close_correction.py` | **7/7 PASS** |
| `tests/test_m_recreate_2_v2_pre_registration.py` | **12/12 PASS** |
| **Total** | **30/30 PASS** |

## State-Machine Discipline (c29 Lemma Respected)

- `M-RECREATE-2/accurate-small-set-v2` is a **peer sub-milestone** under M-RECREATE-2 via c14 supersede-with-`supersedes_path`-as-str lemma. NOT a child of terminal-validated c49 v1.
- Both v1 (`958ade38…3fe58b9d`) and v2 (`0e11f704…debe1f`) rubric chains coexist; c49 audit trail preserved intact.
- `_plan/register-c49-substantive-and-probe-milestones` at line 836 is a peer emission under `_plan/*` family; NOT a rewrite of prior events (content-hash-safe repair).
- **No `validated → in_progress` transitions attempted.**

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`.
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor`; no `i4_stratified` imports.
- Interpreter guard `/usr/bin/python3` on all new stubs and scripts.
- Read-only anchors preserved: c14 `_ledger_schema.py`; c22 stability harness; c26 Path B commitment; c31/c33/c34/c35/c36/c37/c45/c46/c47 palette + recreate + anchor-manifest chain; c47 anchor manifest (19 entries); c47 policy doc §1-§3; c49 v1 rubric + stubs (unchanged).
- Rated audio egress-blocked at `*.googlevideo.com` (`429 + tv_embedded` unchanged; **htdemucs_6s model-weight fetchability OK is distinct** from playlist audio harvest).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.
- **c48 env-var flag flips** (`MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`, `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`) remain OFF per c50 brief (default OFF; c53+ candidates post-M-RECREATE-2-v2 land).

## Anti-Patterns Locked (5-Count Stable)

c11 CLAP HF SSL (respected — VGGish stays DEFERRED-None in RC6-v2); c22 synthetic-label-stability; c23 head-regularization; c25 feature-representation; c35 palette-schema-v2-hydration-render VST3 nondeterminism — not re-attempted. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged. c31 STILL_GAP surface intact.

## Cycle-51 Handoff (3-Branch FANOUT Candidate; Meets All parallel_cycle_fanout_guidance Factors)

**Branch A — RC1-v2 hybrid vocal + RC9 first-class-parts**:
- pyin/basic-pitch on vocals stem for RC1; htdemucs_6s per-stem transcription for guitar/piano first-class parts for RC9.
- Independent baseline anchors (`baseline/<sha16>/rc1_vocals_voiced_time_s.json` + `rc9_6stem/`).
- Own audit gate on per-song RC1 + RC9 accepts.
- Iteration inside: acceptance thresholds may need re-tuning after first render.

**Branch B — RC2 drum onset + RC3 bass**:
- Stem-level transcription branches with independent accept tests (F1 ≥ 0.6 for drums; count band + low-band correlation for bass).
- Own audit gate.
- Iteration on threshold tuning.

**Branch C — RC7 mix-balance + D4 per-stem EQ**:
- Extend `scripts/palette_render/render_stem.py` via additive kwargs (c36 backwards-compat pattern verbatim).
- Implement 12-band log-spaced IIR biquad EQ curve fit.
- RMS + LUFS-S loudness match ≤ 3 dB.
- Own audit gate on A7 per-stem loudness.
- Iteration on EQ curve refinement.

All three touch **disjoint files**; A/B produce transcription artefacts that C's mix stage consumes but **ONLY at c52+ integration cycle**. c51 branches merge → c52 RC4 folds into A/B merged.midi emission → c52 or c53 RC6-v2 panel gate lands. RC5/RC8 fold into A/B/C respectively per brief.

### Discipline Invariants to Carry Into c51 Brief

- **v1 AND v2 rubric_hash three-way byte-equality** must be asserted at every c51+ RC verdict emission.
- **D4 old-chain-as-baseline row** (`panel_baseline_old_chain.tsv` from c33 pinned Surge chorus+reverb) survives ONLY as comparison in the panel — never as a LANDS deliverable.
- **c48 env-var flag flips** remain c53+ candidates post-M-RECREATE-2-v2 land.
- **Formalise `_infra/auditor-reads-ledger-not-brief-summaries` lemma** in c51 alongside c46 rubric-doc lemma. This lemma has now demonstrably paid off twice (c48-close + c49-close both caught worker-report claims that CLI-verification falsified). Codify in `docs/auditor_discipline_ledger_first.md`.

### Not-in-Scope for c51

M-EAR-1 arc; M-GEN-1 batch work; corpus breadth beyond standard egress-retry; RC6-v2 panel gate implementation; env-var flag flips. Anti-pattern re-opens forbidden.

### Standing Follow-ons (Carried From Prior Cycles)

1. **c48 Branch A `_infra/harness-and-writer-hardening-v3`** still owed as substantive re-field (sub-fix 1: `_is_clone_context` substantive/infra distinction; sub-fix 2: `supersedes` in content-hash) — c53+ candidate.
2. **Writer-side guard rejecting novel milestone_ids not in `plan_of_record`** — the plan-registration-lag pattern has now fired **7 times** (c9/c26/c38/c46/c47/c48/c49-close); c50 auditor Priority 3 candidate. Carrying cost is worth it.
3. **`_infra/large-model-fetchability-registry`** — if htdemucs_6s success is reproduced in c51, this argues for pinning alongside c45 egress failure-mode registry.
4. **Egress retry** per campaign directive (`429 + tv_embedded` unchanged).
5. **`_infra/merge-report-sandbox-fallback-convention`** codification (fifth+ observation).
6. **Extend anchor manifest** (`TZ`, `LC_ALL`, `OMP_NUM_THREADS`) as follow-on peer entries.
7. **STATISTIC_VERSION = F1_pooled_variance_v1 pin** as formal anchor.

## Cumulative Progress

**M-RECREATE-2 arc** (post-c50 v2 peer-supersede):

| Cycle | Milestone | Verdict / Status |
| --- | --- | --- |
| c49 | `M-RECREATE-2/accurate-small-set` (v1) | rubric committed (SHA `958ade38…3fe58b9d`); substantive close |
| **c50 (this range)** | `M-RECREATE-2/accurate-small-set-v2` (peer supersede) | **rubric committed (SHA `0e11f704…debe1f`); RC7/RC8/RC9 + D1-D4 + A7-A8 scope; htdemucs_6s fetch OK; 5-song chosen_section landed; both v1+v2 chains coexist** |

**Chicken Grease `31a164f845f8e27e` chosen_section at [233.6s, 263.6s]** is a meaningfully-late window (peak-30s per D1), NOT sparse-first-30s. RC8 pre-registration mechanically catches the "always t=0" bug — good falsification target.

**htdemucs_6s fetch OK is the campaign's first successful large-model window** — one honest data point, honestly recorded. Extends the fetchability ladder methodology (c11/c25/c31/c33) to a positive outcome.

**c48 auditor-lemma track record**: has now caught worker-report-vs-CLI drift at c48-close AND c49-close. **Two consecutive positive signals — formalise in c51 as `_infra/auditor-reads-ledger-not-brief-summaries` lemma.**

**c49 correction arc ended cleanly**: both c49 MODERATE findings (`promise_check` 6-ERROR + test-scope mismatch) closed by c50 Priority 1 + Priority 2 via the same lightweight `_plan/register-*` pattern used successfully at c9/c26/c38/c46/c47/c48.

**M-RECREATE-2 arc healthy structurally**: peer supersede v1→v2 preserves c49 audit trail while accommodating operator's material re-scope. Two coexisting rubric_hash chains — exactly the c14 supersede pattern generalised to rubric-scope architectural change.

**Pattern durability**: rubric-first pre-registration discipline preserved across v1→v2 peer-supersede; mtime discipline verified (v2 rubric mtime < every new v2/RC7-RC9 stub mtime; c49 v1 stubs predate v2 rubric, untouched).

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3 → c47 Branch B MIXED** fanout-namespace convention held (c50 is sequential root-mode; no `-clone-*` suffixes).

**Anchor-manifest arc**: v1.1 stable at 19 entries with `SOURCE_DATE_EPOCH` first-class. Additional environment pins queued.

**Deprecation arc**: c45 archived; c46 canonical `determinism_check_c46.py` remains sole canonical.

**Pre-registration gate policy arc**: c46 amendment scope-locked to harness-boundary bucket for current session context (c47 Branch B MIXED).

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Ledger state**: **847 rows** (c49 close 835 + 12 c50 events); **0 `promise_check` ERRORs**; WARN 2591 (pre-existing).

**Fanout cadence**: LINEAR c44/c45/c46 → FANOUT c47/c48 → LINEAR c49/c50 → **c51 FANOUT** (3-branch RC1+RC9 / RC2+RC3 / RC7+D4).

**Egress state**: `429 + tv_embedded` unchanged for playlist audio harvest; **htdemucs_6s model-weight fetchability OK is distinct** (positive campaign-first).

**Campaign ready for c51 substantive fanout.** c50 close-correction is the terminal deliverable for this range; the two coexisting rubric chains (v1 + v2), the htdemucs_6s fetchability window, and the ledger-first-not-brief-summaries auditor lemma are all durable outputs seeding c51+.

[END OUTPUT]
