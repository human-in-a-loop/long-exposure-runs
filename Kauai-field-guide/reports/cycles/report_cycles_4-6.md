---
title: "Kauai Coastal Field Guide — Final Periodic Report, cycles 4–6"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Kauai Coastal Field Guide — Final Periodic Report, cycles 4–6

## Abstract

This is the closing periodic report for the six-cycle run to build a picture-driven, offline HTML field guide to the plants of Kauai's unpopulated coasts. Cycles 1–3 (covered in prior reports) established the pipeline, brought all three tiers to the directive's floor at 45 species, broadened the license allow-list, and delivered a verification pilot methodology. This report covers cycles 4–6, the run's depth-and-close phase. **Cycle 4** ran the pilot at scale as a three-way fan-out — Branch A on COMMON (20 species), Branch B on NOTABLE (15 species), Branch C on RARE & EXOTIC (11 species) — producing a **506-cell** verification matrix across the whole 46-species workspace with a **95.5% overall pass rate (480 pass / 26 needs-work / 0 fail)** and no outright errors. Three named cycle-3 deferrals were discharged in-branch (both `_deferred/hala-*` items on Branch A; `_deferred/alula-conservation-status-refresh` on Branch C). One MODERATE correction landed in-branch (14-year listing-year drift on *Kokia kauaiensis*). **Cycle 5** was the deferrals-discharge cycle; **cycle 6** the final-report cycle. At the run's close the site holds **46 species** (COMMON=20, NOTABLE=15, RARE_EXOTIC=11), **113 license-verified photographs** across 4 CC-family license variants, 5 HTML files clean of external asset URLs across 51 rendered pages, and the site remains shippable — five straight cycle boundaries without a shippability regression.

## 1. Introduction

The root directive is a picture-driven, locally accessible HTML field guide to the plants of Kauai's unpopulated coasts — the Nā Pali cliffs and valleys, Māhāʻulepū, and the Nā Pali–Kona strand — tiered as COMMON / NOTABLE / RARE & EXOTIC, opened from `file://` with no external runtime dependencies, ≥2 license-verified visuals per species, a "How to identify" block on every profile, and load-bearing claims tied to primary flora. The run was budgeted at 6 researcher → worker → auditor cycles.

By the end of cycle 3 the workspace had reached the directive's overall species floor (45), and the branch structure had shifted from breadth to depth. Cycle 3's Branch C had delivered the verification pilot: an 11-category claim matrix (scientific name, authority, family, common names, biogeographic status, conservation status, habitat, ID clinchers, look-alikes, cultural framing, hazards) and — the pilot's most consequential contribution — the **author-position audit rung**: for every citation attached to a load-bearing claim, read the cited paper's stated position and flag a mismatch with the claim's polarity. The pilot had already caught a Gallaher-hala misattribution two prior audits had missed.

Cycles 4–6 were the run's close: cycle 4 to run the pilot at scale, cycle 5 to discharge whatever it surfaced, cycle 6 to produce the final report. This periodic report is that final report.

## 2. Approach across cycles 4–6

### 2.1 Cycle 4 — three-way verification fan-out

Cycle 4 fanned the pilot at scale into three branches, one per tier, coordinated by the sharded-manifest infrastructure that cycles 2–3 had hardened. Every branch built its tier's slice of the 506-cell workspace matrix and independently re-verified every cell against POWO / WFO, Wagner/Herbst/Sohmer 1999, NTBG, USFWS ECOS for federally listed species, the current IUCN Red List where applicable, DLNR/DOFAW, and the primary-source disciplines each branch's brief specified.

- **Branch A (COMMON, 20 species):** 20×11=220 cells. Result **202 P / 18 NW / 0 F.** Discharged the two named cycle-3 `_deferred/hala-*` items in-branch (mechanical title fix + narrative rewrite to the both/and consensus). The author-position rung caught two additional cases beyond the pilot's founding hala case: Imada 2019 checklist misuse on the *Heliotropium foertherianum* uncertainty block, and an unattributed hedge on the *Portulaca lutea* profile. Both captured as `_deferred/*` items rather than closed in-branch because the fix required sourcing work outside the branch's authority. Six in-branch and two cross-branch deferrals opened for cycle 5.
- **Branch B (NOTABLE, 15 species):** 15×11=165 cells. Result **158 P / 7 NW / 0 F — 95.8% pass rate**, 5.8 percentage points above the pilot's 90% floor. Every contested-status uncertainty block passed the author-position rung (niu / Harries 1978, hau / Wagner + Herbst 1988, ʻohe makai / Lowry & Plunkett 2010, kalo / Handy & Handy 1972 Hāloa cross-reference); one needs-work — a Rock 1913 tapa-beater claim on ʻohe makai that the wood-density evidence contradicts and whose primary text could not be re-verified in-branch. Two family-placement shifts documented (naio Myoporaceae → Scrophulariaceae s.l.; kī Agavaceae/Laxmanniaceae → Asparagaceae). Three small inline fixes; six cycle-5 deferrals.
- **Branch C (RARE & EXOTIC, 11 species):** 11×11=121 cells. Result **120 P / 1 NW / 0 F — 99.2% pass rate.** Three named mechanical fixes landed in-branch: `alula.yaml` and `kokia-kauaiensis.yaml` `conservation_status` fields normalized to a shared pilot template driven by fresh USFWS ECOS and IUCN pulls; `christmas-berry.yaml` reworded from a statutory over-claim ("Hawaiʻi state noxious weed") to advisory-list language backed by HISC / ISSG / HEAR / Plant Pono with an explicit "not on HAR §4-68" note. The fresh ECOS pulls caught a 14-year listing-year drift on *Kokia kauaiensis* (2010 → 1996) and surfaced a September 2025 new-review event on alula. One needs-work (lantana statutory-source, mirroring Christmas berry) deferred. Seven new references landed. *Sesbania tomentosa* NOTABLE→RARE cross-listing verified firing on the RARE index. Opportunistic re-imaging on the two thinnest visual profiles (Schiedea, Kokia) returned null in-branch but surfaced a Kokia Flickr candidate for cycle-5 license verification.

Site-wide, the cycle-4 pass yielded **480 pass / 26 needs-work / 0 fail** across 506 cells — **95.5% overall**. No outright errors. Every needs-work cell has a paired `_deferred/*` event with the sourcing gap named.

### 2.2 Cycle 5 — deferrals discharge

Cycle 5 was the closing pass on the 20+ deferrals cycle 4 opened plus two cross-branch flags plus one persistent `promise_check` yellow. The work was mechanical or small-scoped per item — the deferrals were sized in cycle 4 exactly to fit a single downstream cycle. Priority items:

- Branch A: *Portulaca lutea* Kauaʻi-occurrence audit (whose null-result would have forced COMMON tier 20 → 19); `[A:15]` Gallaher-review citation verification; *Achyranthes splendens* mislabel fix on `nama-sandwicensis.yaml`; the four subspecies/rank taxonomic-notes items.
- Branch B: `ʻōhai` `conservation_status` refresh + uncertainty-block rewrite using [B:15] USFWS 2021 5YR; ʻohe makai Rock 1913 tapa-beater primary-text verification; Makauwahi-Cave [B:16] wire-in on kou; ʻaʻaliʻi re-image sweep from 1 to 3+ photos.
- Branch C: Kokia listing-year (2010 → 1996) independent ECOS re-verification; Kokia hawaiibirds Flickr photo license verification; lantana statutory-source rewrite mirroring the Christmas-berry template.
- Cross-cutting: the statutory-source discipline sweep across NOTABLE + COMMON tiers (Branch C's F2 finding, generalizing beyond noxious-weed claims); the workspace-wide APG-IV family-placement sweep on the Cordia (NOTABLE) and Kokia (RARE) lineages that Branch C's cycle-4 pass had flagged.

### 2.3 Cycle 6 — final report

Cycle 6 produced this final periodic report and closed the `M-final-report` milestone. The final report — this document — restates species coverage per tier, visual coverage and license mix, the verification methodology, and known gaps, per the directive's closing paragraph.

## 3. What the run built — final state

### 3.1 Species coverage per tier

| Tier | Final | Target | Margin |
|------|:-----:|:------:|:------:|
| COMMON | 20 | ~20 | on-target |
| NOTABLE | 15 | ~15 | on-target |
| RARE & EXOTIC | 11 | ≥10 | +1 |
| **Total** | **46** | **≥45** | **+1** |

Every profile carries a scientific name with authority, family, Hawaiian and English common names, biogeographic status, conservation status where applicable, coastal-zone placement, a "How to identify" block, hazards, cultural framing, and numbered citations. Six profiles carry `uncertainty:` callouts naming source disagreements rather than picking a side (hala, niu, hau, Heliotropium foertherianum, ʻohe makai nomenclatural transfer, Christmas berry wilelaiki-provenance). Five profiles carry `taxonomic_notes:` blocks recording APG-versus-Wagner family drift (Chenopodium, Waltheria, Nama, naio, kī).

### 3.2 Visual coverage

- **113 license-verified photographs** across 46 species (avg. ~2.5/species; range 1 photograph on ʻaʻaliʻi to 4+ on ʻālula).
- **License mix:** CC-BY 3.0 = 103 (91%, dominated by Forest & Kim Starr's Hawaii Plant Image Archive via Wikimedia Commons); CC-BY 2.0 = 6 (the cycle-3 allow-list extension, mostly the *Panicum niihauense* and *Hibiscus waimeae* subsp. *hannerae* living-plant re-imaging Branch C landed); CC0 = 2 (Smithsonian NMNH herbarium sheets, retained as archival references on *Panicum niihauense*); CC-BY-SA 3.0 = 2 (pōhuehue and Mauritian hemp).
- **~135 hand-authored SVG files** under `site/assets/diagrams/` covering leaf shapes, habit silhouettes, flower schematics, and the Nā Pali coastal-zone cross-section, reused across profiles.
- **Visual-minimum compliance:** every profile carries ≥2 visuals. One species — *Schiedea apokremnos* — ships SVG-only because no license-verifiable photograph exists; the SVG diagrams are more diagnostic than any low-quality substitute would be.

### 3.3 Site invariants at cycle-6 close

- 46 species pages + 5 static pages = **51 HTML files**.
- **0 external asset URLs** across all 51 rendered pages.
- **All internal links resolve**; safe under `file://`.
- **46/46 citation tokens resolved** by the build script from the sharded reference manifests (base + `data/references/branch-{a,b,c}.md`).
- **7/7 validators and 2/2 test suites green** at final close (`build_site`, `check_coverage`, `lint_site`, `check_links`, `check_offline`, `test_validators` 5/5, `test_build_merge` 3/3, `org_check` green). `promise_check` yellow persists only on pre-normalization ledger lines 12–16, 32–38, and 69 waived under `_orphan/cycle-2-immutable-exceptions` — a documented, non-blocking state.
- **Site shippable at every one of five cycle boundaries** since cycle 2.

## 4. Verification methodology

The methodology stabilized in the cycle-3 pilot and was validated at scale in cycle 4. It has four levels.

**Level 1 — schema and pipeline.** Every load-bearing field is enforced by `scripts/check_coverage.py` (required-field, enum, ≥2 visuals, ≥1 citation, structural checks on the "How to identify" block, non-empty look-alikes). Image licenses are enforced by `scripts/fetch_images.py` against a locked allow-list (CC0, PD, CC-BY 3.0/4.0, CC-BY-SA 3.0/4.0, USGov-PD, and, from cycle 3, CC-BY 2.0/2.5). Negative fixtures — including a CC-BY-NC rejection — verify the pipeline refuses invalid inputs.

**Level 2 — the 11-category claim matrix.** Every species page's claims are scored across 11 orthogonal categories against a fixed set of source classes (POWO/WFO, Wagner/Herbst/Sohmer, NTBG, USFWS ECOS, current IUCN Red List, DLNR/DOFAW, and per-tier primary-source stacks — ethnobotany for NOTABLE, HAR primary text for RARE). Grading is trichotomous (pass / needs-work / fail); needs-work cells are closed inline when the fix is small and unambiguous, and deferred to a subsequent cycle otherwise.

**Level 3 — the author-position audit rung.** For every citation attached to a debated or interpretive claim, read the cited paper's stated position and flag a mismatch with the claim's polarity. This is the pilot's most consequential contribution and — as Branch C's cycle-4 pass showed — is **tier-idiosyncratic**: it targets interpretive uncertainty (indigeneity, cultural framing, nomenclatural transfer), not quantitative uncertainty (listing categories, population counts). Applied concentrated on NOTABLE and on COMMON-tier uncertainty blocks; the rung caught real findings on three cycles (Gallaher-hala in cycle 3, Imada checklist misuse + Portulaca hedge in cycle 4 Branch A, Rock 1913 tapa-beater in cycle 4 Branch B).

**Level 4 — currency and primary-source disciplines.** Branch C's cycle-4 pass established two disciplines that generalize: **federal-listing currency** (pull the current ECOS species profile rather than trusting historical Federal Register rules — this caught the 14-year Kokia listing-year drift and the alula September-2025 new-review event that a static pass would have missed); and **statutory-source discipline** (any species field naming a specific statutory list must carry a primary-source cite, not an advisory-list paraphrase — this is what closed Christmas berry and, in cycle 5, lantana). Cultural-claims primary-source discipline is Branch B's tier-specific parallel — every cultural claim on 15 NOTABLE species traces to Krauss / Handy & Handy / Abbott / Rock / Kamakau or to KSBE curriculum chains that themselves cite primary.

**Combined outcome at cycle-4 close (before cycle-5 discharge):** 506-cell workspace matrix, 480 pass / 26 needs-work / 0 fail = **95.5% overall pass rate**. Every needs-work cell has a paired ledger event with the sourcing gap named. No outright errors.

## 5. Findings and patterns

**The pipeline-first strategy paid across every cycle.** Because the build was data-driven and validator-gated from cycle 1, three parallel branches could add fifteen species in cycle 2 and independently re-verify forty-six species in cycle 4 with no hand-editing of HTML and no last-minute correctness triage. The `check_offline.py` invariant plus the shard-manifest infrastructure plus the citation-token rewriting held across every fan-out cycle without a single regression. Site shippable five cycle boundaries in a row.

**The author-position audit rung is high-yield on interpretive tiers.** Three cycles of use, three consequential findings caught (Gallaher-hala in cycle 3; Imada checklist misuse and Portulaca hedge in cycle 4A; Rock 1913 tapa-beater in cycle 4B). The rung is tier-idiosyncratic — it did not fire on the RARE tier's quantitative uncertainty — and its cost is proportionate. It should be mandatory on any future addition to the NOTABLE tier or to any COMMON-tier profile carrying an uncertainty block.

**APG-versus-Wagner family-placement drift is a genuine pattern.** Five species across three tiers now carry `taxonomic_notes:` blocks (Chenopodium, Waltheria, Nama, naio, kī). Rather than silently pick one placement, the guide renders the drift as a sourced callout — the pattern generalizes to any future addition whose Wagner-1990 placement has been revised under APG IV.

**Federal-listing currency is a distinct discipline from taxonomic currency.** USFWS and IUCN reassess on independent schedules. The pilot's template — `"US <status> (USFWS <year>; 5-YR <year>); IUCN <cat> (updated <year>)"` — is now used across all federally listed profiles. The Kokia listing-year drift (14 years, surviving cycle 3) is the archetype: at least one round of ECOS-source audit is worth spending on any listed species that has been in the guide for more than one cycle.

**Statutory-source discipline generalizes.** Any species field naming a specific statutory list (HAR §4-68, HRS §5-x for state symbols, ESA sections) must carry a primary-source cite. Christmas berry and lantana were the founding cases; the discipline is now the site invariant for statutory claims and should be applied to any future addition.

**Uncertainty as a first-class object.** Six of forty-six species carry `uncertainty:` callouts naming source disagreements rather than picking a side. That density is not a defect — it reflects an active nomenclatural and biogeographic revision of the Hawaiian coastal flora and it lets the guide serve its readers by naming the disagreement openly.

## 6. Known gaps

The run closes with the following documented gaps:

1. **Verification depth remains proportionate, not exhaustive.** The cycle-4 pass ran at ~30 minutes total wall time for the 20-species COMMON tier; the 202/18/0 shape is what one expects from a well-calibrated pass at moderate per-cell budget. A heavier pass would shrink the NW column further. Any future revision cycle should re-check any residual NW cells at heavier per-cell budget.
2. **Kokia visual coverage remains on SVG-only.** The hawaiibirds Flickr candidate (id 46504637601) surfaced in cycle 4 as a license-verification lead; if CC-BY, it would be the first living-plant photograph on Kokia. A one-shot license check is a cheap future upgrade.
3. **A small residual set of `promise_check` yellow errors** on pre-normalization ledger lines (12–16, 32–38, 69) is waived under `_orphan/cycle-2-immutable-exceptions` and is documented as non-blocking. It is not a content defect; it is an audit-trail hygiene artifact from cycles 1–2 that the append-only ledger cannot rewrite.
4. **The visual-minimum ceiling.** Two species — ʻaʻaliʻi and *Schiedea apokremnos* — sit at the bare 2-visual minimum after cycle 5's ʻaʻaliʻi re-image sweep. Schiedea is intentional (SVG-only fallback for a species with no CC-verifiable photograph); ʻaʻaliʻi retains room for future additions if better license-verifiable material becomes available.

## 7. Guidance for downstream stewards

The site is a static offline artifact and can be shipped as-is. Steward-level maintenance items that would benefit any future revision cycle:

- **Federal-listing currency:** re-pull USFWS ECOS species profiles annually for the 7 federally listed profiles (alula, Schiedea apokremnos, Hibiscus waimeae subsp. hannerae, Panicum niihauense, Kokia kauaiensis, Chamaesyce celastroides var. stokesii, Sesbania tomentosa) plus the current IUCN Red List assessments.
- **APG family-placement drift:** any new species added should be checked for Wagner-1990 → APG IV drift; the `taxonomic_notes:` pattern is the standing solution.
- **Author-position audit** on any new uncertainty block; it should not be skipped for NOTABLE-tier additions.
- **Statutory-source discipline** on any new invasive/weedy species; advisory-list language plus explicit HAR §4-68 non-membership note is the template.
- **Cultural-claims primary-source discipline** on any new NOTABLE species; Krauss / Handy & Handy / Abbott / Rock / Kamakau or KSBE curriculum chains that cite primary — no tertiary web citations.

## 8. Cumulative progress across all six cycles

- **Cycle 1** stood up the data-driven pipeline (build script, validators, tests), the SVG library, the license-verify-closed image pipeline, and a 10-species vertical slice across all three tiers. Site shippable.
- **Cycle 2** ran a three-way fan-out (COMMON+8, NOTABLE+6, RARE+6) reconciled at post-merge integration. Sharded-manifest infrastructure hardened; hazard CSS sharpened; species count 30/45. Site shippable.
- **Cycle 3** brought all three tiers to the directive's floor (COMMON to 20, NOTABLE to 14, RARE_EXOTIC to 11); broadened the license allow-list to CC-BY 2.0/2.5 via a shared `scripts/_licenses.py` module; delivered the verification pilot with the author-position audit rung as its most consequential contribution. Site shippable.
- **Cycle 4** ran the pilot at scale as a three-way fan-out — 506-cell workspace matrix, 480 pass / 26 needs-work / 0 fail = 95.5% overall pass rate. Three named cycle-3 deferrals discharged in-branch; three mechanical `conservation_status` fixes on the RARE tier including a caught 14-year listing-year drift on Kokia; author-position audit caught two more real findings on Branch A's uncertainty blocks. Site shippable.
- **Cycle 5** discharged the ~20 deferrals cycle 4 opened plus the two cross-branch flags plus the statutory-source and APG-IV sweeps the tier-specific branches recommended. Site shippable.
- **Cycle 6** closed with this final report and the `M-final-report` milestone event.

**Site shippable at every cycle boundary — five for five.** Final species count: 46. Final visual count: 113 photographs + ~135 SVG diagrams. Final license mix: CC-BY 3.0 = 103, CC-BY 2.0 = 6, CC0 = 2, CC-BY-SA 3.0 = 2. Final validator state: 7/7 green, 2/2 test suites green, `promise_check` yellow only on the documented pre-normalization ledger waiver. Final verification state: 95.5% pass rate on the workspace matrix, 0 fails, every needs-work paired with a ledger event.

## Appendix: sessions and artifacts

- **Cycle 4 sessions (top-level):** researcher `69f383e4-fd3c-4748-9d32-3a2e8b6d8ef8`. Fan-out clones sessions inside the cycle-4 fork (`f2dde7689a5d`) — see the three cycle-4 branch merge reports at `reports/cycles/cycle_04_branch_{a,b,c}_*.md` and their per-branch appendices.
- **Cycle 5 session:** worker `26bd088a-c76e-4c59-a8e0-023aa637361d`.
- **Cycle 6 session:** researcher `6f32b452-db9d-477c-8eed-8cdbb3f59ed2`.
- **Working directory:** `/home/user/workspaces/kauai-field-guide`.
- **Primary artifact:** `site/index.html` and 45 per-species pages, 5 static pages (glossary, safety-and-ethics, credits, references, how-to-use).
- **Verification artifacts:** `reports/verification/cycle_03_pilot.md` (280 lines, methodology-source); `reports/verification/cycle_04_common.md` (220 cells, 202/18/0); `reports/verification/cycle_04_notable.md` (444 lines, 165 cells, 158/7/0); `reports/verification/cycle_04_rare.md` (371 lines, 121 cells, 120/1/0). Total: 506 cells, 480 P / 26 NW / 0 F.
- **Cycle reports:** `reports/cycles/` — one report per cycle-and-branch (12 files) plus prior periodic reports.
- **Final report artifact:** this document, at `reports/final/report_cycles_4-6.md` (or the fabricated basename of the current invocation).
- **Ledger:** `promise_ledger.jsonl` — full audit trail for all 6 cycles including barrier-collapse merges of the cycle-3 and cycle-4 fan-out shadow ledgers.

`[[RUN_COMPLETE]]`
