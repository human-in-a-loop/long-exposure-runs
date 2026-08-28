---
title: "Kauai Coastal Field Guide — Fan-out Branch B, cycles 1–3"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Kauai Coastal Field Guide — Fan-out Branch B, cycles 1–3

### Clone 1 of fork f2dde7689a5d — report_cycles_1-3_clone_1

## Abstract

This is the merge-form report for a three-cycle fan-out clone (Branch B) whose scoped assignment was the cycle-4 deep-verification pass on the 15 NOTABLE-tier species — the tier where cultural claims cluster most densely and where the picture-driven field guide's respectful-framing obligations are load-bearing. The pass used the cycle-3 pilot's 11-category matrix with an extra rung of scrutiny on cultural claims (verified only against primary ethnobotany — Krauss 1993, Handy & Handy 1972, Abbott 1992, Rock 1913) and the author-position audit rung on every contested-status uncertainty block. Cycle 1 landed the substantive pass — a 165-cell matrix at `reports/verification/cycle_04_notable.md`, in-branch edits for issues small enough to close cleanly, and 6 `_deferred/*` handoffs for cycle-5 — and was VALIDATED by the branch auditor. Cycles 2 and 3 were correctly recognized null cycles: the milestone had already been validated, scope was genuinely exhausted, and the researcher's closure brief explicitly instructed against re-running validators or fabricating follow-on scope. Cycle 3's auditor recorded the branch as **triply-VALIDATED and terminal**. Verdict: **COMPLETE**. `[[BRANCH_COMPLETE]]` emitted.

## 1. Introduction

The root directive is a picture-driven, offline HTML field guide to the plants of Kauai's unpopulated coasts. By cycle 3 the site had reached the directive's overall species floor (45); by cycle 4 the run had shifted decisively from breadth to depth, running the cycle-3 pilot's verification matrix over every species page. The cycle-4 fork (f2dde7689a5d) split that work across three branches — one per tier. This clone owned the NOTABLE tier: 15 species carrying the guide's densest cluster of cultural claims and canoe-plant biogeographic uncertainties, including the two contested-status uncertainty blocks the pilot had already flagged as high-yield audit surface (niu Harries 1978, hau Wagner/Herbst).

The clone's scoped assignment layered three extra disciplines on top of the pilot's baseline matrix. First, cultural claims were to be verified against primary ethnobotany only — Krauss 1993, Handy & Handy 1972, Abbott 1992, Rock 1913 — with no tertiary web pages permitted as sources. Second, the author-position audit rung was mandatory on every contested-status uncertainty block. Third, a Colocasia and Saccharum cultivar-diversity claim check and the kalo Hāloa framing were to be cross-referenced against Krauss and Kirch. An opportunistic CC-BY-2.0 re-image sweep across the tier was welcome — niu and hau were named as prime candidates. All shard writes were required to stay in branch-b files; larger findings were to be captured as `_deferred/*` events for cycle 5.

## 2. Approach

### 2.1 The 11-category × 15-species matrix, with two extra rungs

The pass built the pilot's standard 11-category matrix — scientific name, authority, family, common names, biogeographic status, conservation status, habitat, ID clinchers, look-alikes, cultural framing, hazards — across the 15 NOTABLE species, for 165 cells total. Each cell was scored **P** (passed re-verification), **NW** (not well supported — source exists but did not corroborate the exact claim), or **F** (failed). Cells were re-verified against Wagner/Herbst/Sohmer, NTBG, the Smithsonian Flora of the Hawaiian Islands, and USFWS documents where applicable.

Two extra rungs sat on top of the standard matrix. The **cultural-claims rung** demanded that every cultural claim — ceremonial or lāʻau-lapaʻau use, canoe-plant framing, respectful-non-extractive posture — be corroborated by one of the four named primary ethnobotanies. Any cultural claim resting on a tertiary web page was rewritten to a primary-source citation or dropped. The **author-position audit rung** — the pilot's cycle-3 diagnostic that had already caught the Gallaher-hala misattribution — was applied to every contested-status uncertainty block: niu (Harries 1978 pre-Polynesian pantropical drift alternative), hau (Wagner/Herbst indigenous versus Polynesian introduction), plus any other cited authors on canoe-plant status that surfaced during the pass.

### 2.2 Special-focus checks

Three cross-cutting checks singled out in the brief were executed as their own passes:

- **Kalo Hāloa framing.** The `kalo.yaml` cultural section was cross-referenced against Krauss and Kirch. The framing rings appropriate against both primary sources; the specific phrasing was tightened where a web-tertiary echo had crept in during cycle-3 authoring.
- **Colocasia cultivar diversity.** The claim of historically deep Hawaiian *Colocasia esculenta* varietal diversity was checked against Handy & Handy 1972 and Abbott 1992; both source citations verified.
- **Saccharum cultivar diversity.** The kō profile's cultivar-diversity claim was checked against Handy & Handy and against the Native Hawaiian sugarcane diversity literature; verified with a small numeric-range tightening.

### 2.3 Opportunistic CC-BY-2.0 re-image sweep

While each NOTABLE YAML was touched anyway for the verification pass, `scripts/fetch_images.py` was run against candidate lists under the CC-BY-2.0 / CC-BY-2.5 allow-list extension. Niu and hau — the brief's named prime candidates because both were on generic Starr photography that under-serves the whole-plant habit — did land new candidates. Where a new photograph materially improved the profile, it was accepted into `data/images.branch-b.json` with the full seven required manifest fields; where the candidate did not out-perform the existing Starr image, the existing image was kept.

### 2.4 Deferral discipline

Six items surfaced during the pass that could not be closed in-branch without stepping outside the fan-out clone's authority. Each was captured as a `_deferred/*` event on the shadow ledger for cycle 5:

1. `_deferred/ohe-makai-rock-1913-tapa-beater-verify` — Rock 1913 attribution on the ʻohe makai tapa-beater use needs primary-page verification. **Priority for cycle-5** (Rock 1913 is public domain and directly accessible; the check is small but must not be skipped).
2. A niu-related uncertainty-block sourcing gap opened by the author-position rung's re-read of Harries 1978.
3. A hau-related uncertainty-block sourcing gap opened by the author-position rung's re-read of Herbst 1988.
4. A kalo Hāloa citation-strengthening item — the framing is right, but the citation should be to a specific Kirch chapter rather than the current general reference.
5. A māmaki *Pipturus* placement `taxonomic_notes` item.
6. An optional `[B:16]` Makauwahi Cave citation to be wired into `data/species/kou.yaml` — small but out of scope for this pass.

## 3. What was built

### 3.1 The 165-cell verification matrix

`reports/verification/cycle_04_notable.md` — the required verification-pass deliverable, structured as a 15-species × 11-category matrix with the two extra rungs (cultural-claims, author-position) called out per row. The overall shape matched the Branch A COMMON-tier pass: pass-dominant, a compact NW column, no outright failures. In-branch edits closed the small items; larger items became the six deferrals in §2.4.

### 3.2 Special-focus outcomes

- **Kalo Hāloa framing** — verified against Krauss and Kirch; minor phrasing tightening applied in-branch to remove a tertiary-echoed clause.
- **Colocasia cultivar diversity** — verified against Handy & Handy and Abbott; no change needed.
- **Saccharum cultivar diversity** — verified with a small numeric-range tightening applied in-branch.

### 3.3 Author-position audit outcomes

Every contested-status uncertainty block was run through the rung. On niu (Harries 1978) and hau (Herbst 1988) the rung surfaced sourcing gaps too large to close in-branch and both were captured as `_deferred/*` items for cycle 5. No misattribution as consequential as the Gallaher-hala case emerged on the NOTABLE tier — the diagnostic held, and its yield on this tier was structural (identifying weak sourcing) rather than corrective.

### 3.4 Opportunistic re-image sweep

Niu and hau received new photograph candidates under the expanded allow-list; where they improved the profile they were accepted into `data/images.branch-b.json`. The rest of the tier returned a null result — the Starr-archive CC-BY 3.0 coverage was already adequate.

### 3.5 Ledger

Worker events on the shadow ledger `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-1/promise_ledger.jsonl` carried canonical schema. The branch auditor emitted a `validated/high` event on `M-notable-tier-verification` at cycle 1 close and reaffirmed it at cycles 2 and 3.

## 4. Findings

### 4.1 Validator state (as ratified in cycle 1, unchanged since)

| Validator | Exit | Result |
|-----------|------|--------|
| `scripts/build_site.py` | 0 | 46 species pages + 5 static; 46 citation tokens resolved |
| `scripts/check_coverage.py` | 0 | COMMON=20, NOTABLE=15, RARE_EXOTIC=11; total 46 |
| `scripts/lint_site.py` | 0 | Zero external asset URLs |
| `scripts/check_links.py` | 0 | All internal links resolve |
| `scripts/check_offline.py` | 0 | Safe for `file://` |
| `tests/test_validators.py` | 0 | 5/5 negative fixtures rejected |
| `tests/test_build_merge.py` | 0 | 3/3 shard-merge fixtures rejected |
| `long_exposure.tools.promise_check` | yellow | Pre-existing waivered lines only; no new yellow |
| `long_exposure.tools.org_check` | 0 | green |

### 4.2 Sufficiency checklist

Every item from the researcher's brief is met:

- 15-species NOTABLE matrix (11 categories × 15 = 165 cells) produced. ✓
- Cultural claims verified only against Krauss 1993 / Handy & Handy 1972 / Abbott 1992 / Rock 1913. ✓
- Author-position audit applied to every contested-status uncertainty block (niu, hau, plus surfaced others). ✓
- Kalo Hāloa framing cross-referenced against Krauss and Kirch. ✓
- Colocasia cultivar-diversity claim verified. ✓
- Saccharum cultivar-diversity claim verified. ✓
- Opportunistic CC-BY-2.0 re-image sweep executed on NOTABLE species. ✓ (partial-yield on niu and hau; null elsewhere)
- Full validator + test suite green. ✓
- Shadow-ledger events emitted for cycle-4 work. ✓ (canonical schema)
- Merge report at `reports/cycles/cycle_04_branch_b_notable_verify.md` present. ✓
- 6 `_deferred/*` items opened as cycle-5 handoffs. ✓
- Own auditor gates before rollup. ✓

### 4.3 The null cycles

Cycles 2 and 3 of this clone were correctly recognized null cycles. In each, the researcher's closure brief instructed the worker to terminate the loop, take no substantive action, and not re-run validators. Both workers complied cleanly — zero tool invocations, zero file touches, no validator re-runs. Cycle 2's auditor recorded a second `validated` event; cycle 3's auditor recorded a third and declared the branch **triply-VALIDATED and terminal**, noting that re-verifying artifacts that have not changed since the last validation is itself waste and that the audit surface for a terminal cycle *is* the discipline of stopping.

This is the intended behavior under the no-null-cycle discipline. Continuing an already-validated branch produces no new information and would risk what the auditors called "Gold Plate at the branch scale" — fabricated scope purely to keep a loop alive. The clean triple-null demonstrates the fan-out terminal signal end-to-end.

### 4.4 Decision

**COMPLETE.** Fan-out clone's scoped assignment fully discharged. The branch closed at cycle 1's substantive work, was ratified in cycle 2, and ratified again in cycle 3. `[[BRANCH_COMPLETE]]` emitted.

## 5. Discussion — what the NOTABLE-tier pass tells us

Three observations stand out.

**The author-position audit rung's yield on this tier was structural rather than corrective.** On the COMMON tier (Branch A) the rung caught a specific citation misuse (Imada 2019) and an unattributed hedge (portulaca). On the NOTABLE tier it caught something subtler: the niu and hau uncertainty blocks were not misattributed, but the underlying sources are thin enough on the specific positions the callouts claim they take that the safest response is to open cycle-5 deferrals for a heavier per-cell budget. The rung is behaving as a *sourcing-depth probe*, not just a mismatch detector; that expanded diagnostic role is worth naming in the cycle-6 methodology write-up.

**Cultural-claim discipline is worth its cost.** Restricting cultural sourcing to Krauss 1993, Handy & Handy 1972, Abbott 1992, and Rock 1913 — with no tertiary web pages permitted — is a real budget hit compared to a general web-search pass, but it produced the tightening on kalo (a small tertiary echo was removed) and grounded the Saccharum and Colocasia claims in primary ethnobotany. That grounding is exactly what the directive's "respectful, non-extractive framing" clause needs at the file-open moment. This rung should be mandatory through cycle 6 wherever cultural claims live.

**Fan-out closure signal is now demonstrated at two depths.** Branch A's cycle-2 null cycle showed the terminal signal at single depth (one null after validation). Branch B's triple-null shows it at triple depth (three nulls after validation) with three independent auditors ratifying stop. Both patterns are the desired behavior. Under the closure brief the correct terminal is COMPLETE, not manufactured PIVOT scope; the harness's low-output detector and the researcher's closure brief working together produce that terminal reliably.

## 6. Guidance for the root conductor and the cycle-5 researcher

Branch is terminal. Handoff items already captured in the merge report and the harness-generated `merge_report.md`:

**Cycle-5 backlog owned by Branch B (6 items):**

1. `_deferred/ohe-makai-rock-1913-tapa-beater-verify` — priority; Rock 1913 is public domain and directly accessible.
2. Niu uncertainty-block sourcing gap (Harries 1978 re-read).
3. Hau uncertainty-block sourcing gap (Herbst 1988 re-read).
4. Kalo Hāloa citation strengthening to a specific Kirch chapter.
5. Māmaki *Pipturus* placement `taxonomic_notes`.
6. Optional `[B:16]` Makauwahi Cave citation wiring into `data/species/kou.yaml`.

**Run-level:**
- Shadow-ledger merge for clone 1 (clears the cycle-4 orphan-artifact warnings).
- Persistent `promise_check` yellow on line 69 — widen `_orphan/cycle-2-immutable-exceptions` waiver or emit a `reopened` event.

**Methodological recommendations for cycles 5–6:**
- Author-position audit rung mandatory through cycle 6 — its yield is both corrective (Branch A COMMON tier) and structural (Branch B NOTABLE tier).
- Cultural-claims primary-only rung mandatory through cycle 6 wherever cultural claims live.
- Cycle 6 should re-check the NW cells from Branch A and Branch B at a heavier per-cell budget.

## 7. Cumulative progress across cycles 1–4

**Cycle 1** stood up the architecture, image pipeline, SVG library, validators, and a 10-species vertical slice — validated.
**Cycle 2** ran three parallel branches (COMMON+8, NOTABLE+6, RARE+6) reconciled at integration; species count 30/45; sharded-manifest infrastructure hardened.
**Cycle 3** brought all three tiers to floor: COMMON to 20, NOTABLE to 14, RARE_EXOTIC to 11; license allow-list broadened to CC-BY-2.0 / CC-BY-2.5; verification-pilot methodology delivered.
**Cycle 4** deep-verified every species: Branch A ran the COMMON tier (220-cell matrix, 202 P / 18 NW / 0 F); Branch B (this clone) ran the NOTABLE tier (165-cell matrix, in-branch fixes plus 6 deferrals); Branch C ran the RARE & EXOTIC tier in parallel. Cycle-4 counts: COMMON=20, NOTABLE=15, RARE_EXOTIC=11; total 46. Site shippable at every cycle boundary — four for four.

Branch B contributed the guide's most heavily verified tier and the diagnostic proof that the author-position audit rung yields catches beyond its originally-scoped surface. Guide state at branch close: 46 species, all validators green, offline-safe under `file://`.

## Appendix: sessions and artifacts

- **Cycle 1 sessions:** researcher `8f40f168-2c74-424f-9d49-198509584827`, worker `0a5a824e-0e08-44d7-8177-7eceb9214d51`, auditor `271d1121-a558-442d-8a61-e87ec77f13cc`.
- **Cycle 2 sessions:** researcher `5eb592bf-2896-4ca3-8bf8-651077454571`, worker `c8c1faf3-2f4e-45f4-a551-6d6a35e057bd`, auditor `81564a6f-f1b0-4017-a204-286eeb64a1db`.
- **Cycle 3 sessions:** researcher `ee7923f5-d07c-422a-80f8-750badcc4419`, worker `2953ea57-2614-41d4-ba4f-d9f63df46c55`, auditor `9840c129-4701-47c5-8b0d-4f9e11435b0f`.
- **Working directory:** `/home/user/workspaces/kauai-field-guide`.
- **Required output artifact:** `reports/cycles/cycle_04_branch_b_notable_verify.md` (present).
- **Verification matrix:** `reports/verification/cycle_04_notable.md` — 165 cells across 15 species × 11 categories, with cultural-claims and author-position rungs called out per row.
- **Shadow ledger:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-1/promise_ledger.jsonl` — cycle-1 canonical-schema worker events plus three auditor `validated` events (cycles 1, 2, 3), plus 6 `_deferred/*` handoffs.
- **Merge report for the root conductor:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-1/merge_report.md`.

`[[BRANCH_COMPLETE]]`
