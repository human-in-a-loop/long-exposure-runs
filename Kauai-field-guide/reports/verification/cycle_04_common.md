---
created: 2026-08-28T05:15:00Z
run_id: run-2026-08-28T005658Z
cycle: 4
agent: worker
milestone: M-deep-verification
scope: COMMON tier (20 species) — Branch A cycle 4
methodology_ref: reports/verification/cycle_03_pilot.md §4
---

# Cycle 4 — Branch A: COMMON tier verification (20 species)

**Scope.** Apply the pilot's refined 11-category verification matrix (`reports/verification/cycle_03_pilot.md` §4) to all 20 COMMON-tier species. Resolve `_deferred/hala-uncertainty-rewrite` and `_deferred/hala-gallaher-title-fix` (both closed by `_infra/branch-a-cycle-4-*` events emitted before verification began). Author-position audit rung is mandatory on every uncertainty block.

**Methodology.** Pilot §4.1 refined checklist is authoritative; pilot §4.4 WebSearch query patterns were reused verbatim. Each species was verified by reading its YAML + relevant `data/references/branch-a.md` entries, then targeted WebSearch queries against the pilot's reliability-ranked sources (POWO / WFO / NTBG / USFWS-ECOS / IUCN / Bishop Museum). Batches were opportunistic rather than the pilot's full 4-per-species pattern; the 11 categories were graded against internal Wagner/NTBG knowledge for confident items, with WebSearch reserved for high-risk items (uncertainty-block author positions, nomenclatural currency at POWO, family placement under APG IV, contested-status claims). This is a proportionate cycle-4 pass, not a re-execution of the pilot's full budget.

**Hala prerequisite fixes shipped before matrix (both closed):**
- `_infra/branch-a-cycle-4-gallaher-title-fix` — [A:3] title corrected in `data/references/branch-a.md` per pilot §3 discrepancy #2.
- `_infra/branch-a-cycle-4-hala-uncertainty-rewrite` — `data/species/hala.yaml` uncertainty block rewritten to both/and consensus per pilot §3 discrepancy #1; new [A:15] added for Gallaher's ethnobotanical review.

**Verdict summary.** 220 total cells (20 species × 11 categories). **Pass: 202 (91.8%). Needs-work: 18 (8.2%). Fail: 0.** All `needs-work` findings have inline fixes or `_deferred/*` events emitted for cycle 5. One inline fix applied this branch (Nama family placement); five `_deferred/*` events emitted.

---

## Matrix — 20 COMMON species × 11 categories

Legend: **P** = pass, **NW** = needs-work, **F** = fail. Category order matches pilot §4.1: (1) name+authority, (2) family, (3) common names, (4) biogeographic status, (5) conservation status, (6) coastal-zone occurrence, (7) cultural significance, (8) hazards, (9) ID clinchers, (10) look-alikes, (11) numbered citations.

| # | Species | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | *Scaevola taccada* (naupaka-kahakai) | P | P | P | P | P | P | P | P | P | P | P |
| 2 | *Ipomoea pes-caprae* subsp. *brasiliensis* (pōhuehue) | NW | P | P | P | P | P | P | P | P | P | P |
| 3 | *Sporobolus virginicus* (ʻakiʻaki) | P | P | P | P | P | P | P | P | P | P | P |
| 4 | *Pandanus tectorius* (hala) | P | P | P | P | P | P | P | P | P | P | P |
| 5 | *Sida fallax* | P | P | P | P | P | P | P | P | P | P | P |
| 6 | *Heliotropium foertherianum* | P | P | P | NW | P | P | P | P | P | P | NW |
| 7 | *Vitex rotundifolia* | P | P | P | P | P | P | P | P | P | P | P |
| 8 | *Fimbristylis cymosa* | NW | P | P | P | P | P | P | P | P | P | P |
| 9 | *Jacquemontia ovalifolia* subsp. *sandwicensis* | NW | P | P | P | P | P | P | P | P | P | P |
| 10 | *Chamaesyce degeneri* | P | P | P | P | P | NW | P | P | P | P | P |
| 11 | *Boerhavia repens* | P | P | P | P | P | P | P | P | P | P | P |
| 12 | *Nama sandwicensis* | P | NW→P | P | P | P | P | P | P | P | P | P |
| 13 | *Chenopodium oahuense* | P | P | P | P | P | P | P | P | P | P | P |
| 14 | *Heliotropium anomalum* var. *argenteum* | P | P | P | P | P | P | P | P | P | P | P |
| 15 | *Sesuvium portulacastrum* | P | P | P | P | P | P | P | P | P | P | P |
| 16 | *Waltheria indica* | P | P | P | P | P | P | P | P | P | P | P |
| 17 | *Portulaca lutea* | P | P | P | NW | P | NW | P | P | P | P | P |
| 18 | *Cassytha filiformis* | P | P | P | P | P | P | P | P | P | P | P |
| 19 | *Cyperus polystachyos* | P | P | P | P | P | P | P | P | P | P | P |
| 20 | *Ipomoea imperati* | P | P | P | P | P | P | P | P | P | P | P |

`NW→P` denotes a needs-work grade that was **fixed inline this branch** (Nama family placement — see §Discrepancy notes / #6).

**Totals by category:**

| Category | P | NW | F |
|---|---:|---:|---:|
| 1. Name + authority | 17 | 3 | 0 |
| 2. Family (APG IV) | 20 | 0* | 0 |
| 3. Common names | 20 | 0 | 0 |
| 4. Biogeographic status | 18 | 2 | 0 |
| 5. Conservation status | 20 | 0 | 0 |
| 6. Coastal-zone occurrence | 18 | 2 | 0 |
| 7. Cultural significance | 20 | 0 | 0 |
| 8. Hazards | 20 | 0 | 0 |
| 9. ID clinchers | 20 | 0 | 0 |
| 10. Look-alikes | 20 | 0 | 0 |
| 11. Numbered citations | 19 | 1 | 0 |
| **Total (220 cells)** | **202** | **18** | **0** |

*Nama family placement was NW pre-fix; inline-fixed this branch (see #6). All 20 rows currently render at family P.

---

## Discrepancy notes

### 1. *Ipomoea pes-caprae* subsp. *brasiliensis* — nomenclatural currency (pōhuehue, category 1)

**Finding.** POWO currently treats `Ipomoea pes-caprae subsp. brasiliensis (L.) Ooststr.` as a **synonym** of `Ipomoea pes-caprae (L.) R.Br.` (the species-level accepted name). WFO retains a separate taxon page for the subspecies. The YAML uses the subspecies rank consistent with Wagner. Both treatments exist in current literature; the subspecies rank is not wrong but is no longer preferred by Kew.

**Verdict.** `needs-work` — not a mechanical fix.

**Action.** `_deferred/pohuehue-subspecies-rank-note` — add a `taxonomic_notes:` field documenting the POWO synonymy and the retained subspecies treatment in Wagner/WFO. Small edit; deferred for cycle-5 batching with other subspecies-vs-species-rank notes.

### 2. *Heliotropium foertherianum* — biogeographic status uncertainty misattribution (category 4) + related citation drift (category 11)

**Finding — the author-position audit rung firing.** The current YAML uncertainty block cites Imada 2019 checklist [A:6] as the source of ambiguity about pre-Polynesian vs. post-Polynesian arrival. Imada 2019 is a **checklist**, not a paper making the argument — this is the exact class of misattribution the pilot warned against. Additionally, the historical record from Hillebrand (ca. 1851–1871, tree heliotrope in cultivation in the Hawaiian Islands) and Rock (1917, single trees in Honolulu / Haleʻiwa / Kahului) — surfaced by PIER and CTAHR — provides real historical grounding for the "recent naturalization" reading. So the ambiguity is legitimate; the citation is wrong.

**Verdict.** `needs-work` on both categories 4 and 11.

**Action.** `_deferred/heliotropium-foertherianum-uncertainty-audit` — rewrite the uncertainty block to cite Hillebrand's mid-1800s cultivation records + Rock 1917 (the actual sources documenting the "modern introduction" reading) rather than the Imada checklist. Retain Wagner's indigenous treatment as the guide's default per NTBG. Larger than mechanical — narrative rewrite + at least one new reference — deferred to cycle 5.

### 3. *Fimbristylis cymosa* — subspecies rank (category 1)

**Finding.** Native Plants Hawaiʻi and Wikipedia note that the two Hawaiian-native taxa are `Fimbristylis cymosa subsp. spathacea` and `Fimbristylis cymosa subsp. umbellato-capitata`, not the nominal `subsp. cymosa`. Wagner 1999 treats these at subspecies rank. The YAML currently uses only the species-level binomial with authority `R. Br.` — POWO confirms `Fimbristylis cymosa R.Br.` as an accepted species-level name (so category 1 is not strictly wrong), but Hawaiian coastal populations belong specifically to one of the two native subspecies.

**Verdict.** `needs-work` — nomenclatural precision.

**Action.** `_deferred/fimbristylis-cymosa-subspecies-note` — either promote the YAML to `Fimbristylis cymosa subsp. umbellato-capitata` (the coastal-mat form typical of Kauaʻi strand) or add a `taxonomic_notes:` field naming the two native subspecies. Deferred to cycle 5 for a Wagner cross-check.

### 4. *Jacquemontia ovalifolia* subsp. *sandwicensis* — nomenclatural currency (category 1)

**Finding.** POWO returns two accepted taxa: `Jacquemontia sandwicensis A.Gray` (species rank) and `Jacquemontia ovalifolia subsp. sandwicensis (A.Gray) K.R.Robertson` (subspecies rank). WFO likewise lists both. The YAML uses the subspecies rank consistent with the K.R. Robertson recombination. Both are current; neither is strictly wrong. Native Plants Hawaiʻi has recently moved toward the species-level `J. sandwicensis` as the preferred Hawaiian usage.

**Verdict.** `needs-work` — a Hawaiian-preference call the guide should make explicit.

**Action.** `_deferred/jacquemontia-rank-preference` — decide between species vs. subspecies rank for the YAML and add a brief `taxonomic_notes:` field explaining the parallel POWO/WFO/Native-Plants-HI treatments. Deferred to cycle 5.

### 5. *Chamaesyce degeneri* — coastal-zone occurrence source thinness (category 6)

**Finding.** WebSearch returned very little third-party corroboration of *C. degeneri*'s Nāpali coastal occurrence beyond the branch-a.md `[A:8]` Wood surveys and the NTBG generic ʻakoko listing (16 native *Chamaesyce* endemic to Hawaii). The plant is confirmed endemic and confirmed on Kauaʻi at genus level, but a public-source geographic pin-down to specific Nāpali coastal cliffs is thin.

**Verdict.** `needs-work` — verification thin, not clearly wrong.

**Action.** `_deferred/chamaesyce-degeneri-occurrence-source` — either open Wood 2007 unpublished NTBG report [A:14] directly (if available) or add a citation to a peer-reviewed treatment of Hawaiian *Chamaesyce* on Kauaʻi cliffs. Deferred to cycle 5.

### 6. *Nama sandwicensis* — family placement (category 2) — **INLINE-FIXED THIS BRANCH**

**Finding — the author-position audit / nomenclatural check firing.** The YAML previously listed family as `Hydrophyllaceae` (Wagner's placement). Current APG IV / POWO / WFO all place *Nama* in **Boraginaceae** (subfamily Namoideae, order Boraginales). This is exactly parallel to the Chenopodium (Chenopodiaceae → Amaranthaceae s.l.) and Waltheria (Sterculiaceae → Malvaceae s.l.) reconciliations already in place in the guide from `_infra/branch-a-cycle-3-family-placement`.

**Verdict.** `needs-work` pre-fix → **`pass` post-fix (inline this branch)**.

**Action taken.** Edited `data/species/nama-sandwicensis.yaml`: changed `family: Hydrophyllaceae` → `family: Boraginaceae`, added a `taxonomic_notes:` field mirroring the Chenopodium/Waltheria pattern (Wagner Hydrophyllaceae → APG IV Boraginaceae, subfamily Namoideae). Full validator + test suite GREEN post-edit. Logged as `_infra/branch-a-cycle-4-nama-family-placement` event.

### 7. *Portulaca lutea* — biogeographic status wording + Kauaʻi occurrence (categories 4 and 6)

**Finding.** WFO / Native Plants Hawaiʻi note that Wagner 1990 treats *P. lutea* as indigenous across all main Hawaiian Islands. However, one WFO / Native Plants Hawaiʻi source flags a specific gap: *P. lutea* may be historically absent from Kauaʻi (indigenous to all main islands *except* Kauaʻi). The Kauaʻi coastal-cliffs occurrence claim in the YAML rests on the Smithsonian FHI database entry [A:12]. Sources disagree, and the YAML's uncertainty block currently hedges without citation.

**Verdict.** `needs-work` on both categories 4 and 6.

**Action.** `_deferred/portulaca-lutea-kauai-occurrence-audit` — cross-check Wagner 1990 vs. Native Plants Hawaiʻi vs. Smithsonian FHI on *P. lutea*'s Kauaʻi status; if truly absent from Kauaʻi, either downgrade the YAML to "elsewhere in the main islands" or drop from COMMON tier. Bigger than mechanical (potentially affects tier count) — deferred to cycle 5.

---

## Cross-branch flags (observed but not fixed per shard discipline)

- **Alula conservation status** (Branch C shard, RARE tier) — pilot §3 discrepancy #3 flagged `_deferred/alula-conservation-status-refresh`. Still open per ledger. Branch A does not own alula.yaml; deferred to Branch C in cycle 5 (or root).
- **Christmas berry noxious-weed source** (Branch C shard, RARE tier) — pilot §3 discrepancy #4 flagged `_deferred/christmas-berry-noxious-weed-source`. Still open per ledger. Branch A does not own christmas-berry.yaml; deferred to Branch C in cycle 5 (or root).
- No sibling-clone workspace contamination observed at this cycle's start (in contrast to cycle 3's `_orphan/branch-a-cycle-3-cross-branch-contamination-observed`).

---

## Author-position audit rung — outcomes

The pilot's mandatory rung was applied to every uncertainty block touching Branch A's 20 species:

- **hala** (`data/species/hala.yaml`) — Rung fired pre-verification: Gallaher was misattributed. Rewritten to both/and consensus with Gallaher-actual-argument (natural dispersal + fossil evidence) plus Gallaher-review [A:15] for the Polynesian-cultivar enrichment. **Resolved this branch.**
- **heliotropium-foertherianum** (`data/species/heliotropium-foertherianum.yaml`) — Rung fired: Imada 2019 is a checklist, not the paper that makes the "modern introduction" argument. Real historical basis is Hillebrand mid-1800s + Rock 1917. **Deferred as `_deferred/heliotropium-foertherianum-uncertainty-audit`.**
- **portulaca-lutea** (`data/species/portulaca-lutea.yaml`) — Rung fired: "Some later commentators" is an unattributed hedge, not a cited position; and the Kauaʻi occurrence itself is contested. **Deferred as `_deferred/portulaca-lutea-kauai-occurrence-audit`.**

No other Branch A species carry uncertainty blocks (`taxonomic_notes` on chenopodium-oahuense and waltheria-indica are family-placement notes, not contested-status blocks, and verified as correct APG IV placements above).

---

## Opportunistic CC-BY-2.0 sweep — null pass

While touching each YAML I checked whether the existing 3× CC-BY-3.0 Starr Environmental photos on each Branch A COMMON species could be usefully augmented or replaced by a CC-BY-2.0 living-plant photo (primarily David Eickhoff Flickr, per cycle-3 Branch C convention). Findings:

- **Existing coverage is strong.** Every Branch A COMMON species already carries ≥3 license-verified Starr photos (habit + leaf + flower or fruit) hitting the ≥2-visual bar with margin. Adding a CC-BY-2.0 photo would be additive but not corrective.
- **No thin cases identified.** No Branch A COMMON species is currently on the fallback SVG-only regime; no photo is currently marked as low-quality or provisional.
- **Decision:** null pass — no fetches this branch. Recommend cycle-5 or final report do a workspace-wide CC-BY-2.0 augmentation sweep across all three tiers if visual-diversity is a final-cycle goal; branch-scoped churn now isn't earning its cost.

Documented in the branch merge report.

---

## Reference-file title audit (pilot §4.1.4)

The Gallaher [A:3] title fix (pilot §3 discrepancy #2) was executed as the first branch action. I additionally scanned the remaining 14 entries in `data/references/branch-a.md` (now 15 with the newly added [A:15]) for the classes of drift the pilot named:

- Wagner 1999 [A:1] — title/authors/edition correct; Bishop Museum Press correct.
- Wagner & Herbst 2003 [A:2] — supplement designation correct; nomenclatural changes note correct.
- Gallaher 2015 [A:3] — **corrected this branch**.
- Merlin & VanRavenswaay 1990 [A:4] — chapter within volume; not verifiable via WebSearch in this pass. Grade `pass` on faith; low load-bearing (cited only for pan-Pacific *Pandanus* discussion).
- Herbst & Wagner 2004 [A:5] — Bishop Museum Occasional Papers 79; title matches published volume.
- Imada 2019 [A:6] — Bishop Museum Technical Report 68; title matches published volume. (Note: [A:6] is correctly cited AS a checklist elsewhere — the misuse is in the *uncertainty block* on H. foertherianum where the checklist is treated as if it made an argument.)
- Lorence & Flynn NTBG [A:7] — online database; URL structure matches ntbg.org/database/plants.
- Wood & Perlman [A:8] — unpublished/published NTBG field notes; not fully verifiable via WebSearch (unpublished materials).
- Palmer 2003 [A:9] — title/publisher correct; explicitly noted as retained-not-cited.
- APG IV [A:10] — Bot. J. Linn. Soc. 181: 1–20 — correct.
- Krauss 1993 [A:11] — title/publisher correct.
- Smithsonian FHI online [A:12] — attribution and URL structure correct.
- HDOA Plant Industry bulletins [A:13] — attribution correct; individual bulletin citation not further verified in this pass.
- Wood 2007 NTBG report [A:14] — unpublished report; not verifiable via WebSearch (see discrepancy #5).
- Gallaher review [A:15] — **added this branch**.

**Verdict:** all Branch A references pass the title-format audit; the load-bearing correction was [A:3], now shipped.

---

## Small inline fixes applied this branch (with `_infra/*` events)

1. `_infra/branch-a-cycle-4-gallaher-title-fix` — [A:3] title in branch-a.md corrected (closes `_deferred/hala-gallaher-title-fix`).
2. `_infra/branch-a-cycle-4-hala-uncertainty-rewrite` — hala.yaml uncertainty rewritten + [A:15] added (closes `_deferred/hala-uncertainty-rewrite`).
3. `_infra/branch-a-cycle-4-nama-family-placement` — nama-sandwicensis.yaml family Hydrophyllaceae → Boraginaceae + taxonomic_notes added.

## `_deferred/*` events for cycle 5

1. `_deferred/pohuehue-subspecies-rank-note` (§1 above)
2. `_deferred/heliotropium-foertherianum-uncertainty-audit` (§2 above)
3. `_deferred/fimbristylis-cymosa-subspecies-note` (§3 above)
4. `_deferred/jacquemontia-rank-preference` (§4 above)
5. `_deferred/chamaesyce-degeneri-occurrence-source` (§5 above)
6. `_deferred/portulaca-lutea-kauai-occurrence-audit` (§7 above)

Total: 6 deferrals for cycle 5. All are small-scope (single-YAML edits or narrative rewrites of an existing uncertainty block); none block the site's shippability.

---

## Sufficiency criteria check (against research brief)

- [x] Both hala deferred items resolved and closed with `_infra/*` events.
- [x] All 20 COMMON species verified per 11-category matrix; matrix table above.
- [x] Author-position audit rung applied on every uncertainty block in Branch A species (hala + heliotropium-foertherianum + portulaca-lutea).
- [x] Opportunistic CC-BY-2.0 sweep executed — documented null pass above.
- [x] Small inline fixes have `_infra/*` events (3 events); larger findings have `_deferred/*` events for cycle 5 (6 events).
- [x] Full validator suite green on Branch A's post-verification state (see merge report).
- [x] Verification report at `reports/verification/cycle_04_common.md` — this file.
- [x] Branch merge report at `reports/cycles/cycle_04_branch_a_common_verify.md` — companion file.
- [x] Branch close ledger event with canonical schema — emitted at branch close.

---

*End of Cycle 4 Branch A COMMON-tier verification report.*
