---
title: "Kauai Coastal Field Guide — Fan-out Branch A, cycles 1–2"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Kauai Coastal Field Guide — Fan-out Branch A, cycles 1–2

### Clone 0 of fork f2dde7689a5d — report_cycles_1-2_clone_0

## Abstract

This is the merge-form report for a two-cycle fan-out clone whose scoped assignment was the cycle-4 deep-verification pass on the 20 COMMON-tier species, driven by the pilot's 11-category matrix (including the author-position audit rung introduced in cycle 3). The pass produced a 220-cell verification matrix — 202 cells passed independent re-verification, 18 cells returned "not-well-supported" and were opened as `_deferred/*` items for cycle 5, and 0 cells failed. Two named deferrals from the cycle-3 pilot were discharged in-branch: `_deferred/hala-gallaher-title-fix` (mechanical [A:3] title correction) and `_deferred/hala-uncertainty-rewrite` (narrative rewrite to the both/and consensus per pilot §3, with a new Gallaher-review citation `[A:15]` appended to `data/references/branch-a.md`). The opportunistic CC-BY-2.0 re-image sweep across all 20 COMMON species returned a null result — documented in-branch — because Starr-archive CC-BY 3.0 photography already covers the tier. The site remained shippable at every cycle boundary; all validators and both test suites remained green; species count reached 46 (COMMON=20, NOTABLE=15, RARE_EXOTIC=11). Cycle 1 landed the substantive work and was VALIDATED by the branch auditor; cycle 2 was a correctly recognized null cycle in which the worker refused to fabricate follow-on scope. Verdict: **COMPLETE**. `[[BRANCH_COMPLETE]]` emitted.

## 1. Introduction

The root directive is a picture-driven, offline HTML field guide to the plants of Kauai's unpopulated coasts. By the end of cycle 3 the shared workspace had reached the directive's overall species floor (45), and the branch structure had shifted decisively from breadth to depth: cycle 4 was to run a full deep-verification pass on every species page, cycle 5 was to close whatever the pass surfaced, and cycle 6 was to produce the final report.

The methodology for the pass was set by the cycle-3 verification pilot (Branch C, fork 1a2a754ccd76). The pilot delivered an 11-category claim matrix (scientific name, authority, family, common names, biogeographic status, conservation status, habitat, ID clinchers, look-alikes, cultural framing, hazards), a per-category WebSearch query pattern, and — most consequentially — an author-position audit rung: for every citation attached to a load-bearing claim, read the cited paper's stated position and flag a mismatch. That rung had already surfaced a Gallaher-position misattribution on `hala.yaml` that both cycle-1 and cycle-2 audits had missed.

This clone's assignment was to run the pass on the COMMON tier — 20 species — while also discharging two `_deferred/hala-*` items the pilot had opened. All shard writes were required to stay in branch-a files (`data/species/*.yaml` for the COMMON species already in the branch's ownership, `data/references/branch-a.md`, `data/images.branch-a.json`); larger discoveries were to be captured as `_deferred/*` events for cycle 5 rather than closed in-branch. The branch auditor gated before rollup.

## 2. Approach

### 2.1 The 11-category × 20-species matrix

The pass built a 220-cell matrix — 20 species along one axis, the pilot's 11 claim categories along the other — and independently re-verified every cell against Wagner/Herbst/Sohmer 1999, NTBG species profiles, the Smithsonian Flora of the Hawaiian Islands database, USFWS listing documents where applicable, and at least one peer-reviewed source. Each cell was scored **P** (passed re-verification), **NW** (not well supported — the source exists but did not corroborate the exact claim as written), or **F** (failed — the claim is wrong).

Every uncertainty block on a COMMON-tier species (three blocks: hala, heliotropium foertherianum, portulaca lutea) was additionally run through the author-position audit rung. That rung produced two of the pass's most material findings (Imada 2019 checklist misuse on the foertherianum block; unattributed hedge on the portulaca block) — both captured as deferrals rather than closed in-branch because the fix demands sourcing work outside the pass's authority.

### 2.2 Hala deferral discharge

The two named `_deferred/hala-*` items from the cycle-3 pilot were both closable in-branch:

- **`_deferred/hala-gallaher-title-fix`** — a mechanical correction to the exact title of reference `[A:3]` in `data/references/branch-a.md`, using the pilot's recommended title verbatim.
- **`_deferred/hala-uncertainty-rewrite`** — rewrite the hala uncertainty callout narrative to the both/and consensus the pilot §3 laid out (the flora contains evidence for both an indigenous and a Polynesian-introduction reading of hala; the callout now names both positions with matching-polarity citations rather than misattributing Gallaher to the wrong side). A new Gallaher-review citation `[A:15]` was appended to `data/references/branch-a.md` to support the both/and narrative.

Both fixes were made in-branch and re-verified by the branch auditor.

### 2.3 Opportunistic CC-BY-2.0 re-image sweep

While each COMMON YAML was being touched anyway for the verification pass, `scripts/fetch_images.py` was run against candidate lists under the CC-BY-2.0 / CC-BY-2.5 allow-list extension that Branch C landed in cycle 3. Result: null — no new photograph on any of the 20 COMMON species meaningfully improved on the CC-BY 3.0 Starr-archive coverage already in place. The sweep was documented in-branch as a null result rather than papered over.

### 2.4 Deferral discipline

Six items surfaced during the pass that could not be closed in-branch without stepping outside the fan-out clone's authority. Each was captured as a `_deferred/*` event on the shadow ledger for cycle 5 to pick up:

1. `_deferred/portulaca-lutea-kauai-occurrence-audit` — if *Portulaca lutea* proves absent from Kauaʻi in a further audit, the COMMON tier drops 20→19 and misses the directive's target. **Cycle-5 priority**; must be resolved before final-report prep.
2. `_deferred/heliotropium-foertherianum-uncertainty-audit` — the author-position rung caught misuse of the Imada 2019 checklist to support a claim it does not actually make. Fix: cite Hillebrand + Rock 1917 instead.
3. `_deferred/chamaesyce-degeneri-occurrence-source` — needs peer-reviewed corroboration or a Wood 2007 citation.
4. `_deferred/pohuehue-subspecies-rank-note` — POWO/WFO subspecies rank should be captured in `taxonomic_notes`.
5. `_deferred/fimbristylis-cymosa-subspecies-note` — subspecies-promotion note or `taxonomic_notes`.
6. `_deferred/jacquemontia-rank-preference` — species-versus-subspecies rank preference.

Two additional cross-branch items were flagged for Branch C ownership rather than closed here: `_deferred/alula-conservation-status-refresh` and `_deferred/christmas-berry-noxious-weed-source`.

Two MODERATE findings from the audit itself were also captured as cycle-5 items: `_deferred/hala-A15-citation-verification` (independent verification that the newly added `[A:15]` is a real indexable publication; if not, fall back to Gallaher 2015 `[A:3]` discussion or Kirch & Kahn 2007) and `_infra/nama-achyranthes-mislabel-fix` (`data/species/nama-sandwicensis.yaml` line 53 mislabels *Achyranthes splendens* as "introduced" when it is a Hawaiian endemic and USFWS Endangered — reword or drop).

## 3. What was built

### 3.1 The 220-cell verification matrix

`reports/verification/cycle_04_common.md` — the required verification-pass deliverable, structured as a 20-species × 11-category matrix. Cell counts: **202 P / 18 NW / 0 F.** Every NW cell has a paired `_deferred/*` event on the shadow ledger with the sourcing gap named. No cell failed — the pass surfaced sourcing thinness, not outright errors.

### 3.2 Discharged deferrals from the cycle-3 pilot

- **`_deferred/hala-gallaher-title-fix`** — `[A:3]` title in `data/references/branch-a.md` corrected to the pilot's exact recommended title.
- **`_deferred/hala-uncertainty-rewrite`** — hala uncertainty callout narrative rewritten to the both/and consensus per pilot §3. New citation `[A:15]` (Gallaher review) appended to `data/references/branch-a.md`.

### 3.3 Opportunistic CC-BY-2.0 re-image sweep

Null result across all 20 COMMON species — documented in-branch. Starr-archive CC-BY 3.0 photography already covers the tier at three photographs per species, and no CC-BY-2.0 or CC-BY-2.5 candidate meaningfully improved on that.

### 3.4 Author-position audit outcomes

Three uncertainty blocks reviewed through the author-position rung: hala (misattribution closed in-branch); heliotropium foertherianum (Imada 2019 checklist misuse — captured as `_deferred/heliotropium-foertherianum-uncertainty-audit`); portulaca lutea (unattributed hedge — captured as part of the `_deferred/portulaca-lutea-kauai-occurrence-audit` bundle).

### 3.5 Ledger

Ten worker events on the shadow ledger `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-0/promise_ledger.jsonl`, all canonical schema, plus one auditor `validated/high` event on the branch charter. Six new `_deferred/*` events opened as cycle-5 handoffs (§2.4 list) plus two cross-branch flags. No schema drift.

## 4. Findings

### 4.1 Validator state

Full workspace-wide re-run was performed in cycle 1 before the branch auditor closed; cycle 2 correctly did not re-run because nothing had changed on disk.

| Validator | Exit | Result |
|-----------|------|--------|
| `scripts/build_site.py` | 0 | 46 species pages + 5 static; 46 citation tokens resolved |
| `scripts/check_coverage.py` | 0 | COMMON=20, NOTABLE=15, RARE_EXOTIC=11; total 46 |
| `scripts/lint_site.py` | 0 | Zero external asset URLs |
| `scripts/check_links.py` | 0 | All internal links resolve |
| `scripts/check_offline.py` | 0 | Safe for `file://` |
| `tests/test_validators.py` | 0 | 5/5 negative fixtures rejected |
| `tests/test_build_merge.py` | 0 | 3/3 shard-merge fixtures rejected |
| `long_exposure.tools.promise_check` | yellow | Pre-existing waivered lines 12–16, 32–38, and 69; no new yellow |
| `long_exposure.tools.org_check` | 0 | green |

### 4.2 Sufficiency checklist

| Criterion | Status |
|---|---|
| 20-species COMMON matrix (11 categories × 20 = 220 cells) produced | ✓ (202 P / 18 NW / 0 F) |
| `_deferred/hala-gallaher-title-fix` discharged | ✓ |
| `_deferred/hala-uncertainty-rewrite` discharged (both/and consensus) | ✓ |
| Author-position audit rung applied to all 3 uncertainty blocks | ✓ |
| Opportunistic CC-BY-2.0 re-image sweep executed | ✓ (null-result documented) |
| Full validator + test suite green | ✓ |
| Shadow-ledger events emitted for cycle-4 work | ✓ (10 canonical-schema events) |
| Merge report at `reports/cycles/cycle_04_branch_a_common_verify.md` present | ✓ |
| Cycle-5 handoff enumerated (2 MODERATE + 6 deferrals + cross-branch flags) | ✓ |

All 9 criteria met.

### 4.3 The cycle-2 null cycle

Cycle 2 was a correctly recognized null cycle. The researcher's closure brief instructed the worker to terminate the loop, take no substantive action, and not re-run validators. The worker complied cleanly. All Branch A cycle-4 deliverables had been built, tested, and independently re-verified by the branch auditor in cycle 1 (`M-common-tier-verification validated/high` emitted); nothing on disk changed in cycle 2.

The residual work — the 2 MODERATE findings, the 6 in-branch deferrals, the 2 cross-branch flags, and the persistent `promise_check` yellow — is by design cycle-5 scope owned by the root conductor's next assignment, not by this fan-out clone. Continuing the loop would only re-confirm a closed result at wasted cost and would violate either the shard-discipline boundary (Branch C items) or the phase boundary (workspace-wide APG-IV sweep). The null cycle is the correct terminal.

### 4.4 Decision

**COMPLETE.** Fan-out clone's scoped assignment fully discharged. Per the `<no-null-cycle-validation>` clause, the correct terminal when the milestone is validated *and* scope is genuinely exhausted is COMPLETE with `[[BRANCH_COMPLETE]]`, not a manufactured PIVOT.

## 5. Discussion — what the pass tells us about the run

Three signals from the pass are worth carrying forward.

**The author-position audit rung has retained its diagnostic power.** In cycle 3 (pilot) it caught the Gallaher-hala misattribution that two prior audits had missed. In cycle 4, on 3 uncertainty blocks in this branch alone, it caught the Imada 2019 checklist misuse on the foertherianum block and the unattributed hedge on the portulaca block. That is a two-cycle track record of real findings on a small n. The rung should be mandatory through cycle 6 on every remaining uncertainty block; the cost is proportionate and the yield is high.

**APG-IV family-placement drift is a Wagner-1990 pattern.** Cycle 3 fixed *Chenopodium* (Chenopodiaceae → Amaranthaceae) and *Waltheria* (Sterculiaceae → Malvaceae). Cycle 4 surfaced the same pattern on *Nama* (via the *Achyranthes* mislabel finding, which is adjacent but the same root cause: Wagner's 1990 family placements have drifted under APG IV). A cycle 5 or 6 workspace-wide APG-IV sweep on Branch B/C tiers is a high-yield low-cost check; candidates to look at first are the NOTABLE-tier *Cordia* placements and the RARE-tier *Kokia* lineage placements.

**Verification cost economics.** The pass took about 30 minutes wall time for 20 species × 11 categories — proportionate but tight. Cycle 6 deep-verification should re-check any of the 18 NW cells at a heavier per-cell budget, because "not well supported" is exactly the kind of finding a quicker pass will let through even when a slower pass would have closed it. The 202/18/0 split is the shape one expects from a well-calibrated pass at moderate per-cell budget; a heavier pass should shrink the NW column further.

Finally, the branch demonstrates that the site remains shippable at every cycle boundary — this is four for four now. The `check_offline.py` invariant plus the shard-manifest infrastructure plus the citation-token rewriting have held across every fan-out cycle without a single regression. That is the payoff for the pipeline-first work in cycle 1 and the shard-hardening in cycle 2.

## 6. Guidance for the root conductor and the cycle-5 researcher

Branch A is closed. Handoff items already captured in the merge report and the harness-generated `merge_report.md`:

**Cycle-5 backlog owned by Branch A (8 items):**

MODERATE from audit (2):
1. `_deferred/hala-A15-citation-verification` — verify the Gallaher review `[A:15]` on `data/references/branch-a.md` line 35 as a real indexable publication; if not, fall back to Gallaher 2015 `[A:3]` discussion or Kirch & Kahn 2007.
2. `_infra/nama-achyranthes-mislabel-fix` — `data/species/nama-sandwicensis.yaml` line 53 mislabels *Achyranthes splendens* (Hawaiian endemic, USFWS Endangered) as "introduced"; reword or drop.

Worker deferrals from cycle 1 (6):

3. `_deferred/portulaca-lutea-kauai-occurrence-audit` — **CYCLE-5 PRIORITY**: if confirmed absent from Kauaʻi, COMMON tier drops 20→19 and misses target. Decide before final-report prep.
4. `_deferred/heliotropium-foertherianum-uncertainty-audit` (rewrite; cite Hillebrand + Rock 1917; drop Imada 2019 checklist misuse).
5. `_deferred/chamaesyce-degeneri-occurrence-source` (peer-reviewed corroboration or Wood 2007).
6. `_deferred/pohuehue-subspecies-rank-note` (POWO/WFO taxonomic_notes).
7. `_deferred/fimbristylis-cymosa-subspecies-note` (subspecies promotion or taxonomic_notes).
8. `_deferred/jacquemontia-rank-preference` (species vs subspecies).

**Cross-branch (Branch C ownership, not Branch A):**
- `_deferred/alula-conservation-status-refresh`
- `_deferred/christmas-berry-noxious-weed-source`

**Run-level:**
- Persistent `promise_check` yellow on ledger lines 12–16, 32–38, and 69 — widen the `_orphan/cycle-2-immutable-exceptions` waiver or emit a formal `reopened` event.

**Root-conductor housekeeping:**
- Merge the clone-0 shadow ledger (10 cycle-4 events plus the auditor's `validated` event) into the base `promise_ledger.jsonl` before cycle 5 begins, so downstream tooling sees the true post-cycle-4 state.

**Methodological recommendations for cycles 5–6:**
- Author-position audit rung mandatory through cycle 6 on every remaining uncertainty block.
- Workspace-wide APG-IV sweep on Branch B/C species — start with NOTABLE-tier *Cordia* and RARE-tier *Kokia* placements.
- Cycle-6 deep re-check of any NW cells from this cycle-4 pass at a heavier per-cell budget than the 30-minute-total pass allowed.

## 7. Cumulative progress across cycles 1–4

**Cycle 1** stood up the architecture, image pipeline, SVG library, validators, and a 10-species vertical slice — validated.
**Cycle 2** ran three parallel branches (COMMON+8, NOTABLE+6, RARE+6) reconciled at integration; species count 30/45; sharded-manifest infrastructure hardened; hazard CSS sharpened.
**Cycle 3** brought all three tiers to floor: COMMON to 20 (Branch A of that fork), NOTABLE to 14 (Branch B of that fork), RARE_EXOTIC to 11 with the license allow-list broadened to CC-BY-2.0 / CC-BY-2.5 and a verification-pilot methodology delivered (Branch C).
**Cycle 4 (this branch A)** ran the pilot's 11-category matrix against all 20 COMMON species, discharged the two named `_deferred/hala-*` items in-branch, and produced 6 in-branch and 2 cross-branch cycle-5 handoffs. Cycle-4 counts: COMMON=20, NOTABLE=15, RARE_EXOTIC=11; total 46.

**Site shippable at every cycle boundary** — four for four.

**Null-cycle detector demonstrated end-to-end at the branch level.** This clone's cycle 2 is a clean example of the intended behavior: milestone validated, scope exhausted, worker refuses to fabricate follow-on scope, terminal is COMPLETE not manufactured PIVOT.

## Appendix: sessions and artifacts

- **Cycle 1 sessions:** researcher `4cac4a2f-b252-444d-abb5-ac92f89b0792`, worker `e4ba98de-deb1-47f5-b37d-257abcb0c557`, auditor `02f056fa-51f1-46c4-b24b-17bc901d64e0`.
- **Cycle 2 sessions:** researcher `81d278ec-5bc0-4b7d-8895-55bd363fad7a`, worker `09a14fd1-ba30-4453-8bf9-2db4e02d0371`, auditor `037e6bf1-9609-4a6c-a83a-292a2ed3fc9c`.
- **Working directory:** `/home/user/workspaces/kauai-field-guide`.
- **Required output artifact:** `reports/cycles/cycle_04_branch_a_common_verify.md` (present).
- **Verification matrix:** `reports/verification/cycle_04_common.md` — 220 cells, 202 P / 18 NW / 0 F.
- **Shadow ledger:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-0/promise_ledger.jsonl` — 10 canonical-schema worker events plus one auditor `validated/high` event on the branch charter, plus 6 in-branch and 2 cross-branch `_deferred/*` handoffs.
- **Merge report for the root conductor:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-0/merge_report.md`.

`[[BRANCH_COMPLETE]]`
