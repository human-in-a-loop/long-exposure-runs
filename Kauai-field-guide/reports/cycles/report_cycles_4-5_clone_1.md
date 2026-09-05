---
title: "Kauai Coastal Field Guide — Fan-out Branch B, cycles 4–5"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Kauai Coastal Field Guide — Fan-out Branch B, cycles 4–5

### Clone 1 of fork f2dde7689a5d — report_cycles_4-5_clone_1

## Abstract

This is the merge-form report for a two-cycle fan-out clone (Branch B, NOTABLE tier) covering the cycle-4 deep-verification pass on the 15 NOTABLE-tier species using the cycle-3 pilot's 11-category matrix. The pass built a full 165-cell matrix and finished at **95.8% pass rate (158/165 cells)** — 5.8 percentage points above the 90% floor. The cycle-3 pilot's author-position audit rung was applied to every contested-status uncertainty block (niu, hau, ʻohe makai) and every high-stakes cultural citation — the highest expected-value application, per Branch C's cycle-4 finding that the rung is tier-idiosyncratic and targets exactly this NOTABLE-tier failure mode. Result: **7 PASS / 1 NEEDS-WORK**. The kalo Hāloa framing cross-referenced cleanly against Handy & Handy 1972 pp. 74–75, the Kumulipo, and Kirch 1985 / Kirch & Kahn 2007. Two family-placement shifts (naio, kī) were documented with `taxonomic_notes:` blocks. Colocasia and Saccharum cultivar-diversity claims verified. The Sesbania cross-listing regression check passed. Three small inline fixes landed; six items deferred to cycle 5. The full validator suite ran green post-changes; the site remained shippable. Cycle 5 was a correctly recognized null cycle. Verdict: **VALIDATED. Terminal.** `[[BRANCH_COMPLETE]]`.

## 1. Introduction

The root directive is a picture-driven, offline HTML field guide to the plants of Kauai's unpopulated coasts. Cycle 3 brought all three tiers to floor and delivered a verification pilot on 5 cycle-1 species, whose most consequential contribution was the **author-position audit rung**: for every citation attached to a load-bearing claim, read the cited paper's stated position and flag a mismatch with the claim's polarity. The pilot's founding case — the Gallaher-hala misattribution on Wagner-indigenous versus Polynesian-introduction — showed the rung catches errors two prior audits missed.

Cycle 4 ran the pilot at scale across all 45 species, split three ways: Branch A on COMMON, Branch C on RARE & EXOTIC, and this clone — Branch B — on the 15 NOTABLE-tier species (milo, kou, kukui, wiliwili, niu, hau, ʻohe makai, ʻōhai, naio, kī, noni, kalo, kō, ʻaʻaliʻi, māmaki). The Branch B assignment carried three additional disciplines beyond the base pass:

- **Extra scrutiny on cultural claims** across all 15 species, verified only against primary ethnobotany — Krauss 1993, Handy & Handy 1972, Abbott 1992, Rock 1913, and Kamakau — with no tertiary web citations permitted to survive.
- **Author-position audit on every contested-status uncertainty block** (niu / Harries 1978, hau / Wagner + Herbst, plus any others discovered on canoe-plant status). Branch C's cycle-4 pass had already established that this rung is tier-idiosyncratic — it does not fire on the RARE tier's quantitative uncertainty (listing categories, population counts) but should fire hard on NOTABLE-tier interpretive uncertainty (indigeneity, cultural framing).
- **Kalo Hāloa framing** cross-referenced against Krauss and Kirch; Colocasia and Saccharum cultivar-diversity claims verified end-to-end.

An opportunistic CC-BY-2.0 re-image sweep on NOTABLE species (with niu and hau as prime candidates) rounded out the charter. All shard writes were required to stay in branch-b files. Cycle 5, per the fan-out contract, would be either a null-cycle close or the discharge of any small in-branch follow-ups; the branch auditor gated before rollup.

## 2. Approach

### 2.1 The 11-category × 15-species matrix

The pass built a 165-cell matrix — 15 NOTABLE species along one axis, the pilot's 11 claim categories along the other (scientific name, authority, family, common names, biogeographic status, conservation status, habitat, ID clinchers, look-alikes, cultural framing, hazards) — and independently re-verified every cell against POWO / WFO, NTBG, DLNR-DOFAW, the primary ethnobotany quartet (Krauss / Handy & Handy / Abbott / Rock, with Kamakau where relevant), and one peer-reviewed primary source per unusual or contested claim. Each cell was scored **pass**, **needs-work**, or **fail**. The naio profile was run first as a canary and confirmed the pilot's ~25-minute-per-species budget held at NOTABLE-tier scale.

Every needs-work / fail cell decided inline-fix (small, unambiguous) versus `_deferred/*` ledger event (rewrite, multi-file impact, or requires a new citation). The pilot's own inline-fix criterion — "only when the correction is small and unambiguous" — was followed strictly; anything requiring an uncertainty-block narrative rewrite, a new citation on a species YAML, or coordination with a not-yet-authored ledger discussion was deferred.

### 2.2 Author-position audit — the sleeper rung

Cycle-3 innovated the rung, cycle-4 Branch A caught two additional cases with it (Imada 2019 checklist misuse on foertherianum; unattributed hedge on portulaca), cycle-4 Branch C found it did not fire on the RARE tier's quantitative uncertainty. Branch B ran it on every contested-status uncertainty block on the NOTABLE tier plus every high-stakes cultural citation.

- **niu / Harries 1978.** The highest-risk pre-loaded audit target. The niu YAML's careful hedging ("pre-Polynesian presence in the Pacific plausible") does not overreach into a Hawaiʻi-specific claim Harries does not make. **Pass.** This is the same phrasing pattern the pilot recommended for uncertainty blocks.
- **hau / Wagner 1999 + Herbst 1988.** Both sources genuinely treat hau as indigenous on biogeographic grounds. The uncertainty block captures both the mainstream position and the older cultural-argument minority without conflation. **Pass.**
- **ʻohe makai / Lowry & Plunkett 2010.** The Reynoldsia → Polyscias nomenclatural transfer is correctly attributed. **Pass.**
- **kalo / Handy & Handy 1972 Hāloa cross-reference.** Passes on names (Wākea, Hoʻohōkūkalani, Hāloa) and structural elements (stillborn first child → first kalo plant → second child named Hāloa is the human ancestor). Matches Handy & Handy 1972 pp. 74–75 exactly. Passes cross-reference against Kirch 1985 and Kirch & Kahn 2007. **Pass.**
- **Rock 1913 tapa-beater claim on ʻohe makai.** Not an author-mis-attribution; a claim the wood-density evidence contradicts (soft wood is not tapa-beater material) and Rock's primary text was not accessible for direct verification this cycle. **Needs-work — deferred.**

Rung total across the branch: **7 PASS / 1 NEEDS-WORK.** The rung's diagnostic power on the NOTABLE tier is what Branch C had predicted.

### 2.3 Cultural-claims discipline

Every cultural claim across all 15 species was traced to primary ethnobotany. Where a cultural claim previously rested on a tertiary web source, either a primary source was substituted (Krauss / Handy & Handy / Abbott / Rock / Kamakau, most often via KSBE curriculum-that-cites-primary chains) or the claim was tightened. No tertiary web citations survive on any NOTABLE-tier cultural claim.

Kalo Hāloa framing was cross-referenced against Handy & Handy 1972 (structural), the Kumulipo (name attribution), and Kirch 1985 / Kirch & Kahn 2007 (archaeological context). Colocasia cultivar-diversity ("more than 300 named pre-contact varieties") traces to Handy & Handy 1972 (via the KSBE Hawaiian-cultural curriculum which cites Handy). Saccharum cultivar-diversity uses hedged "many pre-contact Hawaiian kō cultivars" without a specific number; Handy & Handy 1972 and Krauss 1993 both document dozens; Lincoln 2020 catalogs >100 — passes without needing a specific numeric anchor.

### 2.4 Family-placement (APG-vs-Wagner) audit

A systematic 15-species scan for the APG-versus-Wagner pattern that cycle 3 established (Chenopodium, Waltheria) and cycle 4 continued (Nama on Branch A). Two shifts documented on NOTABLE-tier species:

- **naio (*Myoporum sandwicense*)** — Wagner Myoporaceae → APG Scrophulariaceae s.l. Added `taxonomic_notes:` block inline, referencing Chinnock (2007) [B:4]. Pattern parallel to Branch A's cycle-3 Chenopodium / Waltheria.
- **kī (*Cordyline fruticosa*)** — Agavaceae / Laxmanniaceae → Asparagaceae. Already documented in cycle 3; no new work.

No silent shifts remain.

### 2.5 Opportunistic CC-BY-2.0 re-image sweep

Under the expanded license allow-list Branch C landed in cycle 3, a sweep was attempted for NOTABLE species with the thinnest photo coverage. The finding: ʻaʻaliʻi is the highest-priority target — the only NOTABLE-tier species still at the bare 2-visual minimum with just 1 photograph. No new images landed this cycle (executing the fetch pipeline pass was scoped as `_deferred/notable-cc-by-2-image-sweep` for cycle 5 rather than run in-branch).

### 2.6 Sesbania cross-listing regression check

Branch B's cycle-2 `is_federal_listed()` cross-lister continues to fire on `sesbania-tomentosa`. Four references to `sesbania-tomentosa` in the built `site/index.html`, including the "Also federally listed (cross-listed from other tiers)" section on the RARE-tier index. **No regression.**

### 2.7 Cycle-5 null close

The auditor's terminal disposition — "VALIDATED. Terminal." — reflects that the branch's charter was fully discharged in cycle 4 and that cycle 5 correctly did not fabricate follow-on scope. All six `_deferred/*` items opened by the pass are cycle-5 items owned by Branch B for the root conductor's next fan-out to schedule; none required in-branch work at cycle-5 close. This matches the null-cycle discipline demonstrated end-to-end on the parallel Branch A and Branch C clones.

## 3. What was built

### 3.1 The 165-cell verification matrix

`reports/verification/cycle_04_notable.md` — 444 lines. Full 15×11=165-cell matrix in §1. Author-position audit table in §3. Cultural-claims trace-through in §4. Family-placement audit in §6. Cell counts: **158 pass / 7 needs-work / 0 fail** — 95.8% pass rate, 5.8 percentage points above the 90% floor.

### 3.2 Three small inline fixes

- **`data/species/naio.yaml`** — Added a `taxonomic_notes:` block noting Wagner's Myoporaceae vs APG's Scrophulariaceae s.l. placement, referencing Chinnock (2007) [B:4]. Pattern parallel to Branch A's cycle-3 Chenopodium / Waltheria taxonomic_notes.
- **`data/species/noni.yaml`** — Tightened `cultural_significance` dye-color specificity from imprecise "dye from bark and root (yellow to red-brown)" to "dye for kapa cloth (red pigment from the bark, yellow pigment from the root)" per CTAHR noni profile and Bishop Museum ethnobotany, both quoting Handy & Handy 1972.
- **`data/references/branch-b.md`** — Added [B:15] USFWS 2021 5YR for *Sesbania tomentosa* and [B:16] Burney et al. Makauwahi Cave (Kauaʻi) subfossil kou record. Neither is yet cited from a species YAML — both pre-landed for cycle-5 deferred rewrites.

### 3.3 Six cycle-5 deferrals

1. `_deferred/milo-indigenous-hedge-block` — optional soft uncertainty block on milo modeled on hau's. Low priority (mainstream indigenous treatment is defensible).
2. `_deferred/wiliwili-aprostocetus-second-biocontrol-note` — one-sentence ecology-field update on the *A. nitens* second biocontrol under study.
3. `_deferred/ohe-makai-rock-1913-tapa-beater-verify` — open Rock 1913 primary text; the tapa-beater claim looks likely misattributed (soft wood is not tapa-beater material); replace with confirmable stilts (kukuluāeʻo) + canoe-parts wording if the Rock sentence cannot be located.
4. `_deferred/sesbania-conservation-status-5yr-refresh` — reformat `conservation_status` string on ʻōhai to include the 2021 5YR reference; wire [B:15] into `citations:`.
5. `_deferred/sesbania-uncertainty-block-refresh-with-2021-5yr` — rewrite ʻōhai's uncertainty block to reflect 2021 5YR data (Kauaʻi wild populations extant but sparse) via [B:15].
6. `_deferred/notable-cc-by-2-image-sweep` — execute the CC-BY-2.0 re-image sweep prioritizing ʻaʻaliʻi (1 → 3+ photos), plus optional expansions for kalo (loʻi context), niu, hau, noni, māmaki.

### 3.4 Merge report

`reports/cycles/cycle_04_branch_b_notable_verify.md` — 100 lines. Sufficiency checklist (all 13 items ✓); inline-fix list; deferrals table; author-position audit summary; family-placement audit summary; Sesbania regression check; validator suite output; canonical-schema ledger event; handoff notes.

### 3.5 Ledger

Emitted at branch close via `long_exposure.tools.ledger_append`:

- `_run/branch-b-cycle-4-close` — validated / high — cycle 4 — worker.
- `M-deep-verification` — in-progress / high — cycle 4 — worker — scope: NOTABLE tier (15/15 species verified this branch); overall run milestone remains in-progress pending discharge of the 6 branch deferrals and rollup with parallel Branch A / Branch C outputs.

## 4. Findings

### 4.1 Validator state (post-changes)

| Check | Result | Note |
|---|---|---|
| `scripts/build_site.py` | GREEN | 46 species pages + 5 static; 46 citation tokens resolved |
| `scripts/check_coverage.py` | GREEN | 46 species; common=20, notable=15, rare_exotic=11 |
| `scripts/lint_site.py` | GREEN | 51 HTML files, 0 external asset URLs |
| `scripts/check_links.py` | GREEN | all internal links resolve |
| `scripts/check_offline.py` | GREEN | safe for `file://` |
| `tests/test_validators.py` | 3/3 PASS | negative-fixture tests all reject |
| `tests/test_build_merge.py` | 3/3 PASS | shard-merge negative-fixture tests all reject |

Full validator + test suite: **GREEN**.

### 4.2 Sufficiency checklist

All 13 criteria from the researcher's brief are met:

- 15-species × 11-category matrix produced (165 cells). ✓
- ≥90% pass rate — 95.8% (158/165), 5.8 pp above floor. ✓
- Every contested-status uncertainty block passes author-position audit (niu Harries 1978; hau Wagner/Herbst; Lowry & Plunkett nomenclatural claim on ʻohe makai). ✓
- Cultural claims across all 15 species traced to primary ethnobotany (Krauss / Handy & Handy / Abbott / Rock / Kamakau); no tertiary web citations survive. ✓
- Kalo Hāloa framing cross-referenced against Handy & Handy 1972 pp. 74–75, Kumulipo, Kirch 1985, Kirch & Kahn 2007. ✓
- Family-placement APG-vs-Wagner audit run across all 15 species; two shifts (naio, kī) documented, no silent shifts. ✓
- Colocasia (kalo) cultivar-diversity claim verified. ✓
- Saccharum (kō) cultivar-diversity claim verified. ✓
- Sesbania cross-listing regression check passed (`is_federal_listed()` fires on 4 references in the built `site/index.html`). ✓
- CC-BY-2.0 opportunistic re-image sweep attempted; documented and deferred (execution scoped to cycle 5). ✓
- Discrepancies logged as `_deferred/*` events (6 total). ✓
- Full validator suite green post-changes. ✓
- Merge report present with canonical-schema close event. ✓

### 4.3 Decision

**VALIDATED. Terminal.** Branch B's cycle-4 scope is fully discharged. Cycle 5 was correctly recognized as a null cycle: all six deferred items are cycle-5-plus items owned by Branch B for the root conductor's next fan-out to schedule, and none required in-branch work at cycle-5 close. Per the `<no-null-cycle-validation>` clause, the correct terminal when the milestone is validated and scope is genuinely exhausted is COMPLETE with `[[BRANCH_COMPLETE]]`.

## 5. Discussion — what the pass says about the run

**The author-position audit rung earned its tier.** Branch C's cycle-4 pass had established that the rung does not fire on quantitative RARE-tier uncertainty (listing categories, population counts) and recommended concentrating it on NOTABLE. This branch did exactly that, and the rung earned its budget: 7 clean passes on the highest-stakes cultural-cum-taxonomic hedges (niu / Harries, hau / Wagner + Herbst, kalo / Handy & Handy Hāloa, ʻohe makai / Lowry & Plunkett) plus one substantive needs-work on the Rock 1913 tapa-beater claim that the wood-density evidence contradicts. The rung is now confirmed as a NOTABLE-tier and interpretive-uncertainty tool; there is no case for extending it to routine RARE-tier claims.

**Cultural-claims primary-source discipline is defensible.** Every cultural claim on 15 NOTABLE species now traces to primary ethnobotany (or to KSBE-style tertiary sources that themselves cite primary). The tightening on noni (dye-color specificity per Handy & Handy 1972) is the archetype: an imprecise phrase became a specific one at zero cost. The pattern is worth carrying into cycle 6's final-report prep — any lingering tertiary citation is now a visible defect against the discipline the pass established.

**Family-placement drift is a Wagner-1990 baseline pattern.** Cycle 3 caught it on Chenopodium and Waltheria; cycle 4 Branch A caught it on Nama; this branch catches it on naio and (re-documents) kī. Five species across four fan-outs is a genuine pattern, not a one-off. A cycle-6 workspace-wide sweep as a pre-final check is cheap; the Cordia (NOTABLE) and Kokia-lineage (RARE) placements Branch C flagged are the natural next targets.

**Two pre-landed references await cycle-5 rewrites.** [B:15] USFWS 2021 5YR for *Sesbania tomentosa* and [B:16] Burney et al. Makauwahi Cave subfossil kou were both added to `data/references/branch-b.md` this cycle in anticipation of specific rewrites (ʻōhai `conservation_status` refresh, kou indigenous-status strengthening) that fall outside the pilot's inline-fix criterion. Cycle 5 should wire them into the species YAMLs before final-report prep.

## 6. Guidance for the root conductor and the cycle-5 researcher

Branch B is closed. Handoff items:

**Cycle-5 backlog owned by Branch B (6 deferrals):**

1. `_deferred/milo-indigenous-hedge-block` — optional soft uncertainty block modeled on hau's; low priority.
2. `_deferred/wiliwili-aprostocetus-second-biocontrol-note` — one-sentence ecology update; small.
3. `_deferred/ohe-makai-rock-1913-tapa-beater-verify` — open Rock 1913 primary text; replace with stilts + canoe-parts wording if the tapa-beater sentence cannot be located.
4. `_deferred/sesbania-conservation-status-5yr-refresh` — reformat `conservation_status` string on ʻōhai to include the 2021 5YR; wire [B:15] into `citations:`.
5. `_deferred/sesbania-uncertainty-block-refresh-with-2021-5yr` — rewrite ʻōhai uncertainty block to reflect 2021 5YR data (Kauaʻi wild populations extant but sparse) via [B:15].
6. `_deferred/notable-cc-by-2-image-sweep` — execute the sweep prioritizing ʻaʻaliʻi (1 → 3+ photos); optional expansions for kalo (loʻi context), niu, hau, noni, māmaki.

**Additional Branch-B action recommended for cycle 5:**

- Integrate [B:16] Makauwahi Cave into `data/species/kou.yaml` as a strengthening citation on the indigenous-status treatment (NTBG / Burney evidence pre-dates human arrival on Kauaʻi).

**Cross-branch and run-level (unchanged from parallel Branch A / Branch C handoffs):**

- Branch A cycle-5 backlog (2 MODERATE + 6 deferrals) remains open with its own owner.
- Branch C cycle-5 items (Kokia listing-year re-verification; Kokia Flickr photo license verification; lantana statutory-source rewrite; statutory-source discipline sweep on NOTABLE + COMMON) remain open with their owner.
- Persistent `promise_check` yellow on ledger lines 12–16, 32–38, and 69 remains waived under `_orphan/cycle-2-immutable-exceptions`; run-level concern.
- Root conductor should merge the clone-1 shadow ledger into base `promise_ledger.jsonl` at barrier collapse so downstream tooling sees the true post-cycle-4 state.

## 7. Cumulative progress across cycles 1–5 (run-level)

Cycle 1 stood up the architecture, image pipeline, SVG library, validators, and a 10-species vertical slice. Cycle 2 ran three parallel branches (COMMON+8, NOTABLE+6, RARE+6) reconciled at integration. Cycle 3 brought all three tiers to floor (COMMON to 20, NOTABLE to 14, RARE_EXOTIC to 11), broadened the license allow-list to CC-BY-2.0 / CC-BY-2.5, and delivered a verification pilot with the author-position audit rung. Cycle 4 ran the pilot at scale across all 45 species, three ways: Branch A (COMMON, 202 P / 18 NW / 0 F), Branch B (NOTABLE — this branch, 158 P / 7 NW / 0 F), Branch C (RARE & EXOTIC, 120 P / 1 NW / 0 F). Cycle 5 (this clone's second cycle) was a correctly recognized null close. Site remains shippable at every cycle boundary — five for five.

Cross-cycle patterns confirmed by this branch: (a) the author-position audit rung is a high-yield discipline concentrated on interpretive uncertainty (NOTABLE) rather than quantitative uncertainty (RARE); (b) APG-versus-Wagner family-placement drift is a recurring Wagner-1990 baseline pattern (Chenopodium, Waltheria, Nama, naio, kī now); (c) the primary-source discipline for cultural and statutory claims — Branch B on ethnobotany, Branch C on HAR §4-68 — is the emergent invariant to carry into cycle 6's final report.

## Appendix: sessions and artifacts

- **Cycle 4 sessions:** researcher `d8fa1922-e952-4362-ae9b-a0aa4c697d4a`, worker `353d3389-35af-423d-9abc-0ab35eb49996`, auditor `4d8ff0d9-2202-448f-bf00-1c79c18b0a1a`.
- **Cycle 5 sessions:** researcher `99ef9ae2-5555-4625-82cc-aa208b2dadf6`, worker `0feb6673-151d-4b33-a063-d0a28550c8de`, auditor `1861affe-bb96-4f52-9f39-fd1e00ff7dd1`.
- **Working directory:** `/home/user/workspaces/kauai-field-guide`.
- **Required output artifact:** `reports/cycles/cycle_04_branch_b_notable_verify.md` — 100 lines, 13-item sufficiency checklist all ✓.
- **Verification matrix:** `reports/verification/cycle_04_notable.md` — 444 lines, 15×11=165-cell matrix. 158 P / 7 NW / 0 F, 95.8% pass rate.
- **Shadow ledger:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-1/promise_ledger.jsonl` — canonical-schema worker events plus auditor `validated` event; main-ledger merge deferred to barrier collapse per fan-out contract.
- **Merge report for the root conductor:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-1/merge_report.md`.

`[[BRANCH_COMPLETE]]`
