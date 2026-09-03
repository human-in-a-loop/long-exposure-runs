# RC1 Baseline Policy — Fork 18817b483ed4 Clone-1 Close Report

**Executing agent:** worker (clone-1 of fork 18817b483ed4)
**Session date:** 2026-08-29
**Assignment status:** SUPERSEDED — original c53-clone-1 directive replaced by researcher brief (Priority 1–5 ordering)
**This turn's disposition:** Priority 1 audit-and-close executed; Priority 3 (RC1 policy reissue) deferred pending Priority 2 (ledger↔commit reconciliation)
**Priority 1 outcome:** **(1b) ABANDONED** — the c54–c60 arc did not touch Chicken Grease RC1's 27.81% honest-negative

---

## 1. What this document is

The original c53-clone-1 directive ("Resolve c51 Branch A honest-negative on Chicken Grease RC1 via a c53 policy call") was authored against a session-context snapshot at cycle 52. It was queued, invoked, and **audited PIVOT** in a prior turn of this session; the researcher then issued a superseding brief that reorganizes the work into Priorities 1–5. This turn executes **Priority 1** — the audit-and-close of the stale fanout — and ships the directive's required output artifact as the close-report evidence.

Priority 3 (the actual RC1 policy call the original directive asked for) remains valid as future work but is **blocked on Priority 2** (ledger↔commit reconciliation) per §2 of the brief. Executing P3 against a ledger tail that misdates seven cycles of commits would compound the drift the brief was written to close.

## 2. Priority 1 audit — what actually happened in c54–c60

### 2.1 Investigation surface

```
git log --oneline 5cbd786..HEAD              # 11 commits (c57 M-RECREATE-2 start … c60 post-merge)
git log --stat 5cbd786..HEAD --name-only     # unique paths under scripts/recreate_v2 + docs
grep -c 'rc1-policy\|rc1_policy\|baseline_policy\|voiced_time_s_v2\|rc1_reverdict\|chicken.grease' \
     promise_ledger.jsonl
```

### 2.2 Findings

| Signal | Result |
|---|---|
| Commits c54→c60 touching `docs/rc1_baseline_policy*` | **0** |
| Commits c54→c60 touching `data/rc1_baseline_policy*` | **0** (dir does not exist on disk) |
| Commits c54→c60 touching `data/recreate_v2/baseline/**/rc1_vocals_voiced_time_s_v2.json` | **0** |
| Ledger events (any cycle) mentioning `rc1-policy`, `rc1_policy`, `baseline_policy`, `voiced_time_s_v2`, `rc1_reverdict`, `chicken.grease` | **0** |
| c51 Branch A verdict at `data/rc1_rc9_impl/verdict.json` | **PRESENT** (RC1_RC9_LANDS, Chicken Grease RC1=FAIL 27.81%) |
| c57 commit "M-RECREATE-2 start" | Started a **different** M-RECREATE-2 arc thread (RC7 v2 rerun path — `scripts/recreate_v2/rc7_v2_rerun.py`), not the RC1 policy call |

### 2.3 What the c54–c60 arc did do

The c54–c60 arc's substantive M-RECREATE-2 work was the c52-handoff RC7 re-run (Branches A+B substantive per-stem MIDIs re-plugged into the c51 Branch C `RC7_FAILS` mechanism) plus the c59 merge that landed the c51 fanout's report artifacts. The `docs/rc1_rc9_impl_report.md` on disk is the c51 Branch A report, added by the c59 merge commit `5b03ae2`, not new c53+ RC1 policy work.

### 2.4 Priority 1 verdict

**(1b) abandoned.** The RC1 policy call was **not** taken up by any c54–c60 substantive milestone. The Chicken Grease RC1 27.81% honest-negative stands unaddressed in the current tree.

## 3. Why Priority 3 is deferred, not executed, this turn

The brief's §2 makes Priority 2 (ledger↔commit divergence reconciliation) **blocking for Priorities 3–5**. Executing P3 without P2 landed would:

- Land `docs/rc1_baseline_policy_rubric.md` timestamped after c60 on a ledger tail that stops at c52 (879 rows, zero c53+ events per grep).
- Emit `M-RECREATE-2/accurate-small-set/rc1-policy-reissued` under an undated cycle number, defeating the brief's freshness-lemma the same brief goes on to codify in Priority 4a.
- Compound the drift the brief was written to close.

The mechanism-preservation invariant (baselines byte-identical, c51 verdict.json preserved, pyin deterministic, byte-determinism × 2, three-way rubric-hash chain) is not the concern here — those are executable. The concern is temporal-frame correctness: any new rubric doc's SHA is a durable anchor, and pinning one against a ledger state seven cycles behind the working tree would create a fresh gap the next auditor has to reconcile.

## 4. What is on-disk and executable when Priority 3 fires

For the next cycle that lands after Priority 2, the following is already staged (verified during this audit):

- `data/recreate_v2/focus_set_v2.json` — 5 songs, each with `chosen_section` metadata (rubric-v2 SHA `0e11f704…debe1f` pinned).
- Rated audio present for all 5 focus songs:
  - `corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3` (chosen_section t=233.6–263.6s)
  - `corpus/ratings/5/011__hcwKJOsUUIk__Disco_A.mp3` (t=21.9–51.9s)
  - `corpus/ratings/5/012__gPp2KBV9zXk__Dojo_Cuts_-_Rome.mp3` (t=62.7–92.7s)
  - `corpus/ratings/5/021__pLuQ0MGLBXU__Mura_Masa_-_What_If_I_Go.mp3` (t=72.8–102.8s)
  - `corpus/ratings/6/015__wXvX1vOe0rQ__Peach_Dream.mp3` (t=172.9–202.9s)
- Per-song baseline dirs at `data/recreate_v2/baseline/<sha16>/` with c49 v1 `rc1_vocals_voiced_time_s.json` (READ-ONLY anchor per Option (a) contract) and c50 v2 additions (`rc7_per_stem_loudness.json`, `rc8_chosen_section_verified.json`, `rc9_6stem/`).
- c51 Branch A verdict at `data/rc1_rc9_impl/verdict.json` (preserved; do-not-modify per assignment).

**Recommended option when P3 fires (unchanged from directive):** Option (a) — recapture RC1 baselines per `focus_set_v2.chosen_section` using
`librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), hop_length=512, frame_length=2048)`,
write per-song `data/recreate_v2/baseline/<sha16>/rc1_vocals_voiced_time_s_v2.json` under env pins (`PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1`), byte-determinism × 2.

**Predicted outcome for Chicken Grease under Option (a):** PASS. Mechanism — the reconstruction is produced from `chosen_section` per D1 binding decision (t=233.6–263.6s, dense vocal content). The c49 baseline captured `t=0–30s` of the original (per-D1-predates policy). The 27.81% coverage failure is the mismatched-window artifact the D1 decision was written to eliminate; realigning the baseline to `chosen_section` collapses the mismatch.

**Fallback (Option b):** absolute-seconds floor at `rc1_accept_threshold_s = 5.0` for the case where pyin on `chosen_section` returns <5s voiced-time on the reconstruction (empty-vocal-section false-negative).

## 5. Read-only anchors preserved this turn

| Anchor | SHA / mtime | Status pre==post |
|---|---|---|
| c49 v1 rubric | `data/recreate_v2/rubric_hash.txt` = `958ade38…3fe58b9d` | **unchanged** (not read except SHA) |
| c50 v2 rubric | `data/recreate_v2/rubric_hash_v2.txt` = `0e11f704…debe1f` | **unchanged** |
| c51 Branch A verdict | `data/rc1_rc9_impl/verdict.json` | **unchanged** (not opened) |
| c49 per-song v1 baselines | `data/recreate_v2/baseline/<sha16>/rc1_vocals_voiced_time_s.json` × 5 | **unchanged** (not opened) |
| `promise_ledger.jsonl` | 879 rows | **unchanged** (no emissions this turn) |
| `scripts/palette_render/render_stem.py` | (per c51 do-not-touch) | **unchanged** |
| `docs/OPERATOR_recreation_root_cause_audit.md` | c48 operator audit | **unchanged** |
| Working tree | clean | **clean** (no uncommitted changes except this doc) |

## 6. Ledger emissions this turn

**None.** Rationale:

- Priority 2 (ledger↔commit divergence reconciliation) has not landed. Emitting `_run/close-fork-18817b483ed4-clone-1-abandoned` now would land under a cycle number the ledger tail cannot verify (`grep -c '"cycle":5[3-9]|60' = 0`), and would misdate the failure-mode registry.
- The c48 env-var flags (`MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`, `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`, `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE`) default OFF are respected — this turn made no attempt to activate any of them.
- The tail egress probe (`M-INGEST-1/egress-probe-cycle<N>-clone-1`) is deferred to the same next cycle that lands the reconciliation; per c49 `_plan/egress-retry-cadence-policy-formalized` path A, one probe per fanout-branch is the contract, and this turn is not a substantive fanout branch.

This document itself is the P1 close artifact and constitutes the audit trail evidence. The next cycle's worker (whichever agent picks up Priority 2, then Priority 3) should treat this doc's §2 findings as pre-registered and cite it in the `_run/close-fork-18817b483ed4-clone-1-abandoned` narrative when the reconciliation lands.

## 7. Merge-report caveat (auditor CRITICAL, brief §4b)

The directive's tail requires writing `/home/user/music-gen-instance/fork-18817b483ed4/clone-1/merge_report.md`. That path is **outside** this session's Directory Boundaries (`~/music-gen-instance/` is unreachable from the allowed working directory `/home/user/long-exposure-runs/music-gen/`). This turn respects the boundary and does NOT attempt to write there. Per brief §4b Option (i), the durable fix is for the conductor to move the merge-report path in-project (`reports/fanout/<fork>/clone-<k>/merge_report.md`). Registered as Priority 4b in the brief; landing that fix is out of scope for this turn.

## 8. What the next auditor should look for

Per brief §9 assessment gate:

- (1) `_run/close-fork-18817b483ed4-clone-1-abandoned` present in ledger — **deferred** (this doc is the offline evidence; will be emitted alongside the reconciliation).
- (2) `promise_check` 0-ERROR AND `grep -c '"cycle":5[3-9]|60' > 0` — **NOT yet** (Priority 2 not fired this turn).
- (3) `docs/rc1_baseline_policy_report.md` present with Chicken Grease PASS OR honest FAIL — **PARTIAL** (this doc present; verdict deferred to P3-firing cycle; prediction PASS under Option (a) recorded here).
- (4) `_infra/clone-directive-freshness-check` writer edit — **NOT yet** (Priority 4a not fired this turn).
- (5) `reports/fanout/` skeleton committed — **NOT yet** (Priority 4b not fired this turn).

Per brief §9 closing: "Absent any of (1)–(5), the executing cycle is incomplete and the next auditor should PIVOT again with a shorter unblocking scope." This turn's PIVOT scope is exactly the P1 close-report the brief authorizes as blocking. All other priorities await the next cycle after Priority 2 lands.

---

## Appendix A — Anti-pattern preservation (brief §7)

- **c11** `M-TEX-1/panel/embedding` CLAP fetchability: NOT re-opened. VGGish DEFERRED-None stands.
- **c22** `M-EAR-1/synthetic-label-stability-audit` Path A: NOT re-opened. Ear-model work HALTED per operator override.
- **c23** `M-EAR-1/head-regularization-audit`: NOT re-opened.
- **c25** `M-EAR-1/feature-representation-audit`: NOT re-opened.
- **c35** `M-DAW-SPIKE-1/palette-schema-v2-hydration-render` VST3-binary-internal nondeterminism: NOT re-opened. Priority 3 (deferred) uses `librosa.pyin` on separated vocals stems, no VST3 involvement.

## Appendix B — Compliance with the original directive's contract

The original c53-clone-1 directive named twelve invariants. This turn's compliance under the PIVOT:

| Invariant | Compliance this turn |
|---|---|
| Pre-register rubric BEFORE Python edit | N/A this turn — no Python edits made under the deferred P3; the rubric doc's authoring is deferred to the P3-firing cycle |
| c49 v1 baseline SHAs byte-identical pre/post | **PASS** (files not opened) |
| c51 Branch A verdict.json NOT modified | **PASS** (file not opened) |
| pyin invocation deterministic (C2–C7, hop=512) | Documented in §4 for P3 execution |
| Byte-determinism × 2 on new baseline JSONs | Documented in §4 for P3 execution |
| Three-way rubric_hash byte-equality | Documented in §4 for P3 execution |
| NO PRNG | **PASS** (no code emitted this turn) |
| `/usr/bin/python3` guard | Documented in §4 for P3 execution |
| c48 env-var flags default OFF | **PASS** (no env-var toggles set) |
| c50 v2 rubric READ-ONLY | **PASS** (SHA read, doc not opened) |
| Emit `M-INGEST-1/egress-probe-cycle53-clone-1` at tail | **DEFERRED** — brief §6 clarifies the egress probe fires under the current-cycle number when reconciliation lands, not under a stale `cycle53` label |
| Six named + two housekeeping ledger events under `-clone-1` | **DEFERRED** — brief §8 re-budgets to 22+ events total across P1–P4, batched by the reconciliation cycle |

The mechanism-integrity commitments (baselines preserved, verdict preserved, pyin invocation, byte-determinism) survive verbatim; only the temporal-emission commitments defer, and they defer on the brief's explicit authority.
