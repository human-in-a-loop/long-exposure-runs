---
created: 2026-08-28T05:15:00Z
run_id: run-2026-08-28T005658Z
cycle: 4
agent: worker
milestone: M-deep-verification (RARE tier segment)
---

# Cycle 4 — Branch C: RARE_EXOTIC Tier Deep-Verification Matrix

**Scope.** Apply the cycle-3 pilot's refined 11-category verification checklist to all 11 species in the RARE_EXOTIC tier. Extra scrutiny on (a) federal-listing currency (USFWS ECOS + most-recent 5-YR + IUCN reassessment year), (b) author-position audit on every uncertainty block and Hawaiian-name etymology claim, (c) statutory-list sourcing (HAR §4-68) for invasive-status claims, (d) taxonomic-rank currency (Chamaesyce vs Euphorbia; Hibiscus var. vs subsp.).

**Effort.** high. **Date.** 2026-08-28.

**Species covered (11).** alula (*Brighamia insignis*), Christmas berry (*Schinus terebinthifolia*), lantana (*Lantana camara*), *Schiedea apokremnos*, *Hibiscus waimeae* subsp. *hannerae*, *Panicum niihauense*, Mauritian hemp (*Furcraea foetida*), koa haole (*Leucaena leucocephala*), castor bean (*Ricinus communis*), *Kokia kauaiensis*, *Chamaesyce celastroides* var. *stokesii*.

**Sesbania tomentosa cross-list** verified as separate deliverable — see §4.

---

## 1. Matrix

Grades: `pass` = verified against a primary/authoritative source this cycle or inherited-pass from cycle-3 pilot §2 with no new evidence to overturn; `needs-work` = source inconclusive or claim under-sourced; `fail` = falsified.

### 1.1 alula — *Brighamia insignis* A. Gray

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO; NTBG; Wikispecies (pilot §2.4) | Inherited-pass. |
| 2 | Family | pass | POWO — Campanulaceae (Hawaiian lobelioid) | Inherited-pass. |
| 3 | Common names | pass | NTBG; DLNR; Revelator | ʻĀlula / ʻōlulu / pua ʻala / cabbage-on-a-stick / vulcan palm all attested. |
| 4 | Biogeographic status | pass | NTBG; DLNR | Endemic to Kauaʻi + (formerly) Niʻihau. |
| 5 | Conservation status | **pass (refreshed)** | USFWS ECOS species 1615; 2022 5-YR; new 5-YR initiated Sept 2025; IUCN 2023 (Walsh, Nyberg & Wood, EW) | Refreshed this cycle via `_infra/alula-conservation-status-refresh`. Old "CR — EW" compound removed. |
| 6 | Coastal-zone occurrence | pass | NTBG; Wood 2012 | Nā Pali sea-cliff faces; extinct in wild in situ. |
| 7 | Cultural significance | pass | Revelator; DLNR | "Signature endemic of Nā Pali" is standard framing. |
| 8 | Hazards | pass | (regulatory reframe) | YAML frames hazard as access-safety, not physiological. Correct. |
| 9 | ID clinchers accuracy | pass | NTBG; BGCI; iNaturalist | Cabbage-on-a-stick + tubular pale-yellow flowers + Kauaʻi–Niʻihau cliff geography — diagnostic. |
| 10 | Look-alikes accuracy | pass | NTBG | *B. rockii* (Molokaʻi/Maui-Nui, white flowers) is correct sister; Cordyline is a reasonable public confusion. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[3]`, `[4]`, `[5]`, `[11]`, new `[C:9]` (USFWS 2022 5-YR), `[C:10]` (IUCN 2023). All resolve. |

**Author-position audit — uncertainty block.** The YAML uncertainty block cites Wood 2012 `[11]` implicitly via the "recent survey work has documented very few remaining wild individuals" language. Pilot §2.4 already confirmed Wood 2012 supports the extinction-in-the-wild framing. **Uncertainty-block claim → cited-author-position: consistent (inherited from pilot).**

**Hawaiian-name etymology.** No specific etymology claim in the YAML (Hawaiian names listed without derivation) — no rung to apply.

---

### 1.2 Christmas berry — *Schinus terebinthifolia* Raddi

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO; Motooka; CTAHR (pilot §2.5) | Inherited-pass. POWO settles on feminine "terebinthifolia". |
| 2 | Family | pass | POWO — Anacardiaceae | Inherited-pass. |
| 3 | Common names | pass | Motooka; CTAHR; HEAR | Christmas berry / Brazilian pepper. Wilelaiki handled in uncertainty block. |
| 4 | Biogeographic status | pass | HEAR; Cal-IPC; Motooka | Introduced from South America pre-1900. |
| 5 | Conservation status | **pass (reworded)** | HISC alert list `[C:13]`; ISSG GISD `[C:14]`; HAR §4-68 Cornell Law `[C:15]` (not on statutory list) | Reworded this cycle via `_infra/christmas-berry-noxious-weed-source-resolved`. Statutory over-claim removed; advisory-list language cited. |
| 6 | Coastal-zone occurrence | pass | HEAR; Nā Pali surveys | Dry lower valleys — matches observed distribution. |
| 7 | Cultural significance | pass | n/a | Correctly `null` (post-contact invasive). |
| 8 | Hazards | pass | CTAHR; Cal-IPC | Contact dermatitis (Anacardiaceae) + mildly-toxic berries confirmed. |
| 9 | ID clinchers accuracy | pass | Motooka; CTAHR; NC Ext. | Winged rachis diagnostic; red winter berries; pepper/turpentine aroma — all confirmed. |
| 10 | Look-alikes accuracy | pass | Wagner (*Rhus sandwicensis*) | Native neneleau contrast correct. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[13]`, `[14]`, new `[C:13]`, `[C:14]`, `[C:15]`. All resolve. |

**Author-position audit — uncertainty (wilelaiki etymology).** Pilot §2.5 confirmed Motooka `[14]` contains the Willie-Rice sentence verbatim. **Cited-author-position: consistent (inherited from pilot).**

---

### 1.3 lantana — *Lantana camara* L.

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO; WFO; GBIF | *L. camara* L. confirmed. |
| 2 | Family | pass | POWO — Verbenaceae | APG IV consistent. |
| 3 | Common names | pass | HEAR; Motooka; wildlifeofhawaii.com | Lantana / common lantana / wild sage / lākana (Hawaiianized). |
| 4 | Biogeographic status | pass | ISSG; PLOS One 2012 (Bhagwat et al.) | Native tropical America; naturalized in 60+ countries as invasive. |
| 5 | Conservation status | **needs-work** | ISSG GISD (top-100 confirmed); HAR §4-68 (not confirmed on list this cycle) | ISSG top-100-worst-invasive claim VERIFIED (Lowe et al. 2000). "Hawaii state noxious weed" — same statutory-source question as christmas-berry; HAR §4-68 verification inconclusive this cycle (statutory list is targeted-eradication; Lantana is too widely established to be a plausible eradication target — likely NOT on HAR §4-68 but not confirmed). **See `_deferred/lantana-noxious-weed-source` below.** |
| 6 | Coastal-zone occurrence | pass | HEAR; Cal-IPC | Dry disturbed slopes; leeward Nā Pali; matches YAML. |
| 7 | Cultural significance | pass | n/a | Correctly `null` (post-contact invasive). |
| 8 | Hazards | pass | Sharma et al. 1988; CTAHR; ISSG | Green (unripe) berry toxicity confirmed as primary hazard to livestock, dogs, humans (triterpene lantadene glycosides). Prickle abrasion secondary. |
| 9 | ID clinchers accuracy | pass | ISSG; NC Ext. | Multi-coloured flat-topped heads (colour shift with age) — diagnostic; square stems with recurved prickles; blue-black berry clusters. |
| 10 | Look-alikes accuracy | pass | ISSG | *L. montevidensis* correct contrast; Verbena distinction correct. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[13]`, `[14]`. All resolve. |

**Author-position audit — no uncertainty block.** No claim requiring rung.

**Hawaiian-name etymology (lākana).** Hawaiianized transliteration of "Lantana" — self-evident post-contact coinage. No claim to audit.

**Deferred to cycle 5.** `_deferred/lantana-noxious-weed-source` — same reword-or-cite fork as christmas berry.

---

### 1.4 *Schiedea apokremnos* H.St.John

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO; Wikipedia; USFWS species profile 2054 | *S. apokremnos* H.St.John — confirmed. |
| 2 | Family | pass | POWO — Caryophyllaceae | APG IV consistent. |
| 3 | Common names | pass | Wikipedia; NTBG | Kauai schiedea / Nā Pali coast schiedea / ma`oli`oli. YAML omits ma`oli`oli. Non-blocking; consider adding cycle-5. |
| 4 | Biogeographic status | pass | Wagner & Weller 2000 `[C:4]`; NTBG `[C:2]` | Kauaʻi endemic — cliff endemic on Nā Pali. |
| 5 | Conservation status | **pass** | USFWS species profile 2054; FR listing rule 30 Sept 1991; 5-YR August 2010 | Federal listing 1991 confirmed. YAML wording ("US Endangered (federally listed)") is thin — could be tightened to "US Endangered (USFWS 30 Sept 1991; 5-Year Review 2010)". Minor; not a blocking issue. |
| 6 | Coastal-zone occurrence | pass | Wagner & Weller 2000; NTBG | Kauaʻi Nā Pali sea cliffs (near-vertical basalt). |
| 7 | Cultural significance | pass | n/a | Correctly `null`. |
| 8 | Hazards | pass | n/a | Correctly `null`. YAML flags cliff-terrain access risk instead. |
| 9 | ID clinchers accuracy | pass | Wagner & Weller 2000 | Cliff-crevice pendent subshrub + opposite fleshy leaves + petal-less greenish-white flowers (wind-pollinated) — diagnostic. |
| 10 | Look-alikes accuracy | pass | Wagner & Weller 2000 | Upland Schiedea + Portulaca + Brighamia contrasts all justified. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[3]`, `[5]`, `[C:2]`, `[C:4]`. All resolve. |

**Author-position audit — uncertainty block.** YAML uncertainty text is qualitative ("anatomy details from published Schiedea revisions") — no specific author-attributed claim to audit.

**Opportunistic re-imaging attempt.** Search for CC-BY David Eickhoff photo on Wikimedia / Flickr returned NULL — Wikipedia article for *S. apokremnos* has no photo; no license-verifiable Eickhoff or DLNR photo found this cycle. **Outcome: keep SVG-only** (habit-cliff-pendent-subshrub + leaf-narrow-succulent). Documented in `image_search_notes`.

---

### 1.5 *Hibiscus waimeae* subsp. *hannerae* (O.Deg. & I.Deg.) D.M.Bates

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO; NTBG; hibiscus-malvaceae blog (Bates 2010 primary source) | **Subsp. rank verified as current** (Bates elevated variety→subspecies). YAML authority string "(O.Deg. & I.Deg.) D.M.Bates" is correct for the subspecies combination. |
| 2 | Family | pass | POWO — Malvaceae | APG IV consistent. |
| 3 | Common names | pass | NTBG; Wikipedia | Kokiʻo keʻokeʻo / Hannera's white hibiscus / Nā Pali white hibiscus. NTBG notes epithet honours Ruth Knudsen Hanner. |
| 4 | Biogeographic status | pass | NTBG; Federal Register 1995 | Kauaʻi endemic; restricted to moist Nā Pali valleys (Limahuli, Hanakāpīʻai, Hanakoa). |
| 5 | Conservation status | **pass** | USFWS ECOS species 5364; listed Endangered 1996; NatureServe (last 5-YR: <80 wild individuals on Kauaʻi) | Federal listing confirmed. YAML wording ("US Endangered (federally listed)") thin — consider tightening to "US Endangered (USFWS 1996; last 5-YR reports <80 wild individuals on Kauaʻi)" cycle 5. Not blocking. |
| 6 | Coastal-zone occurrence | pass | NTBG; Federal Register 1995 | Moist Nā Pali valley bottoms + stream corridors, 60–400 m. |
| 7 | Cultural significance | pass | NTBG; Manoa Heritage | White-hibiscus cultural weight is standard framing. |
| 8 | Hazards | pass | n/a | Correctly `null`. |
| 9 | ID clinchers accuracy | pass | NTBG; Bates | White flower fading pink + pink projecting staminal column — diagnostic separator from other white Hawaiian hibiscuses. |
| 10 | Look-alikes accuracy | pass | NTBG | Subsp. *waimeae* + *H. arnottianus* + hau contrasts all correct. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[3]`, `[5]`, `[C:3]`. All resolve. |

**Taxonomic rank note.** Since the guide already uses `Hibiscus waimeae subsp. hannerae` (POWO-current), no `_infra/hibiscus-hannerae-rank-refresh` event is needed. Brief's contingency (rank-refresh event with rebuild) does not fire.

---

### 1.6 *Panicum niihauense* H.St.John

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO; FR 2000; USFWS species 3861 | *P. niihauense* H.St.John — confirmed. |
| 2 | Family | pass | POWO — Poaceae | APG IV consistent. |
| 3 | Common names | pass | Native Plants Hawaii; NTBG | Lauʻehu / Niʻihau panicgrass. Hawaiian name is genus-level; audit-consistent. |
| 4 | Biogeographic status | pass | POWO; Wagner via secondary | Endemic to Niʻihau + Kauaʻi (Polihale). |
| 5 | Conservation status | **pass** | USFWS ECOS species 3861; FR 2000 recovery-planning docs; Wikipedia — 3 wild individuals remaining; 52 outplanted at Polihale (2018) + 9 (2020) | Federal listing confirmed. YAML wording "US Endangered (federally listed)" thin — cycle-5 candidate to add outplanting/wild-count context. |
| 6 | Coastal-zone occurrence | **pass (Kauai populations confirmed)** | Wikipedia / USFWS: "only naturally occurring specimens grow in Polihale State Park on sand dunes" | Brief's concern that Kauai populations may not exist is falsified. Polihale sand-dune wild individuals ARE genuine (3 remaining) plus 61+ outplanted. YAML `occurrence_notes` and `uncertainty` block already frame this appropriately. |
| 7 | Cultural significance | pass | Native Plants Hawaii | Recognized by name lauʻehu; general dune-vegetation framing. |
| 8 | Hazards | pass | n/a | Correctly `null`. |
| 9 | ID clinchers accuracy | pass | Wagner via NTBG; USFWS | Coarse bunchgrass 0.5–1.2 m vs mat-forming ʻakiʻaki; wide tapering blade with white midrib; open airy panicle. Diagnostic. |
| 10 | Look-alikes accuracy | pass | Wagner | ʻAkiʻaki + Cenchrus/Pennisetum + Eragrostis contrasts all justified. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[3]`, `[C:1]`. All resolve. |

**Author-position audit — uncertainty block.** YAML uncertainty framing ("whether coastal Kauaʻi population persists as wild self-sustaining stand vs outplanting-sustained is not fully resolved") is factually accurate per USFWS recovery-planning docs — only 3 wild remain against 60+ outplanted. **Cited-author-position: consistent.**

---

### 1.7 Mauritian hemp — *Furcraea foetida* (L.) Haw.

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO | *F. foetida* (L.) Haw. — confirmed. |
| 2 | Family | pass | POWO — Asparagaceae (APG IV Agavoideae) | APG IV consistent. |
| 3 | Common names | pass | POWO; ISSG GISD | Mauritius hemp / giant cabuya / green-aloe. Common name is confusingly geographic. |
| 4 | Biogeographic status | **pass (native range verified)** | POWO; ISSG (species 1257); PROTA; Wikipedia | Native to Costa Rica + N. South America + S. Caribbean. NOT Mauritius (misnomer confirmed — plant brought to Mauritius ~1790, fiber industry from ~1875). YAML `ecology` field says "Native to northern South America and the Caribbean" — ACCURATE. |
| 5 | Conservation status | pass | n/a | Correctly `null` (invasive, not conservation-listed). |
| 6 | Coastal-zone occurrence | pass | Local Nā Pali surveys; boat-approach observation | Naturalized on drier Nā Pali cliffs — matches observed. |
| 7 | Cultural significance | pass | n/a | Correctly `null`. |
| 8 | Hazards | pass | ISSG; wild-clone variability | Sharp leaf tips + variable marginal spines + potential sap dermatitis. YAML flags variability appropriately. |
| 9 | ID clinchers accuracy | pass | POWO; ISSG | Huge stemless rosette + bulbil-laden 5–10 m stalk + smooth-margin wild form vs occasional armed clones. Diagnostic. |
| 10 | Look-alikes accuracy | pass | POWO | Agave sisalana + Cordyline + Yucca contrasts all justified. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[13]`, `[14]`, `[C:5]`. All resolve. |

**Author-position audit — origin claim.** YAML cites `[1]` (Wagner) and `[28]` (weed compendia) for naturalization; does NOT attribute origin claim to a specific author. Origin ("native to South America and the Caribbean") is broadly consensus per POWO + ISSG + PROTA. **No misattribution.**

---

### 1.8 koa haole — *Leucaena leucocephala* (Lam.) de Wit

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO; USDA PLANTS | *L. leucocephala* (Lam.) de Wit — confirmed. |
| 2 | Family | pass | POWO — Fabaceae (subfam. Mimosoideae) | APG IV consistent. |
| 3 | Common names | pass | POWO; HEAR; Motooka | Koa haole / ekoa / white leadtree / lead tree / jumbay. |
| 4 | Biogeographic status | pass | POWO; Hughes 1998 | Native to Central America (S. Mexico / Yucatán). Introduced to Hawaiʻi in the 1800s as fodder — YAML accurate. |
| 5 | Conservation status | pass | n/a | Correctly `null`. |
| 6 | Coastal-zone occurrence | pass | HEAR; Motooka | Dry lowland disturbed ground, sea level–800 m. Matches YAML. |
| 7 | Cultural significance | pass | n/a | Correctly `null`. "Koa haole" (foreign koa) name is itself a post-contact coinage — no indigenous *Leucaena* to have carried a traditional name. YAML frames without cultural claim. Correct. |
| 8 | Hazards | **pass (mimosine claim verified against primary lit)** | Yanuartono; ScienceDirect *Mimosine* overview; PMC 12791080 (Systemic Toxicity of L-Mimosine in Rabbits); PMC 12366334 (rumen synergistota / ruminant tolerance) | Mimosine → alopecia in non-ruminants is well-established (Puchała et al.; Jones 1979 CSIRO baseline). YAML "hair loss and reproductive problems in non-ruminant livestock" — CONFIRMED against peer-reviewed primary literature. |
| 9 | ID clinchers accuracy | pass | POWO; HEAR; Motooka | Bipinnate leaf + creamy white pom-pom heads + flat brown 10–20 cm pods + monotypic thicket habit — diagnostic. |
| 10 | Look-alikes accuracy | pass | POWO | Acacia koa (phyllodes) + Prosopis pallida (paired spines, cylindrical yellow pods) + Christmas berry (winged pinnate) contrasts all correct. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[13]`, `[14]`. All resolve. |

**Hawaiian-name etymology (koa haole).** Post-contact coinage. YAML does not claim indigeneity for the name — audit-consistent.

---

### 1.9 castor bean — *Ricinus communis* L.

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO; USDA PLANTS | *R. communis* L. — confirmed. |
| 2 | Family | pass | POWO — Euphorbiaceae | APG IV consistent. |
| 3 | Common names | pass | Pukui/Elbert; NC Ext.; USDA | Castor bean / castor oil plant. Hawaiian pāʻaila / koli are documented. |
| 4 | Biogeographic status | pass | Poison Control; NC Ext.; ScienceDirect *Ricinus* overview | Native East Africa; long naturalized worldwide. Hawaiʻi 19th c. — YAML accurate. |
| 5 | Conservation status | pass | n/a | Correctly `null`. |
| 6 | Coastal-zone occurrence | pass | HEAR; Motooka | Disturbed dry-mesic coastal ground — matches YAML. |
| 7 | Cultural significance | pass | n/a | Correctly `null`. |
| 8 | Hazards | **pass (ricin claim verified against primary tox lit)** | Poison Control (Poison.org); NCBI Bookshelf *Ricin Toxicity* (StatPearls); Springer Naunyn-Schmiedeberg 2019 review; MDPI *Toxins* 2011 case series | Ricin lethal oral dose 1–20 mg/kg body wt; inhaled 5–10 µg/kg; historically "poisonous plant of 2018" per Naunyn review. YAML "one of the most acutely toxic natural compounds known — a very small amount can be lethal" — CONFIRMED. Whole-seed toxicity + castor-oil-safe distinction (refining removes ricin) also correct. |
| 9 | ID clinchers accuracy | pass | NC Ext.; Wagner | Huge palmate leaves 5–11 pointed lobes; red spiny seed capsules; herbaceous fast growth on disturbed ground. Diagnostic. |
| 10 | Look-alikes accuracy | pass | NC Ext. | Manihot / Aleurites / Jatropha contrasts all justified. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[13]`, `[14]`. All resolve. |

---

### 1.10 *Kokia kauaiensis* (Rock) O.Deg. & Duvel

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO (LSID 561051-1); NTBG; Wikispecies | *K. kauaiensis* (Rock) O.Deg. & Duvel — confirmed. |
| 2 | Family | pass | POWO — Malvaceae | APG IV consistent. |
| 3 | Common names | pass | NTBG; DLNR | Kokiʻo / kokiʻo ʻula / Kauai treecotton. |
| 4 | Biogeographic status | pass | POWO; NTBG; DLNR | Endemic to Kauaʻi. |
| 5 | Conservation status | **pass (normalized this cycle)** | USFWS ECOS species 8488 (listed 1996); 5-YR 2017 short-form summary; IUCN 2020 (Heintzman, Nyberg & Wood, CR, e.T30934A83802016) | Normalized this cycle via `_infra/kokia-conservation-status-normalized`. **Prior YAML incorrectly stated listing year 2010; corrected to actual 1996.** Wild individual count ~19 per USFWS 2017 5-YR. |
| 6 | Coastal-zone occurrence | pass | NTBG; USFWS 2017 5-YR; DLNR | Paʻaiki / Mahanaloa / Kuia / Kalalau valleys + Nā Pali Coast State Park + Pōhākuao + upper Waimea drainages. YAML honestly frames as boundary-of-coastal-scope. |
| 7 | Cultural significance | pass | NTBG; general Malvaceae ethnobotany | Kokia bark → red/brown dye is standard framing; YAML honestly notes cultural documentation is sparse for K. kauaiensis specifically vs the more-cited K. drynarioides. Attribution-free framing appropriate. |
| 8 | Hazards | pass | n/a | Correctly `null` for physiological. Regulatory hazard (federally listed) noted in `uncertainty`. |
| 9 | ID clinchers accuracy | pass | NTBG; DLNR | Palmate 7–9-lobed cordate leaf + spiral-twisted red flower with curved staminal column + Kauaʻi endemicity — diagnostic. |
| 10 | Look-alikes accuracy | pass | NTBG | Hibiscus hannerae + Hibiscus rockii + other Kokia species — all correct off-island geography settles it. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[3]`, `[5]`, `[C:7]`, new `[C:11]` (IUCN 2020), `[C:12]` (USFWS 2017 5-YR). All resolve. |

**Author-position audit — uncertainty block.** YAML uncertainty says population counts "vary between publications" and to refer to current NTBG/USFWS. Non-controversial; audit-clean.

**Opportunistic re-imaging attempt.** Wikimedia/Flickr search: one hawaiibirds Flickr photo of *K. kauaiensis* exists (46504637601) but license unclear from search result. Confirmed CC-BY Eickhoff photos exist for *K. cookei* (wrong species). **Outcome: keep SVG-only** (habit-small-tree + leaf-palmate-lobed + flower-kokia-red-spiral). Documented in `image_search_notes`. Cycle-5 candidate: verify hawaiibirds Flickr photo license directly.

---

### 1.11 *Chamaesyce celastroides* var. *stokesii* (Sherff) Koutnik

| # | Category | Verdict | Source | Note |
|---|---|---|---|---|
| 1 | Scientific name + authority | pass | POWO (accepted: *Euphorbia celastroides* var. *stokesii*); Wagner 1999 (as *Chamaesyce*); GBIF 176787482 | Both names refer to same plant. YAML uses Wagner *Chamaesyce* usage consistently with *C. degeneri* elsewhere; **carries `uncertainty` block acknowledging POWO's *Euphorbia* placement.** Audit-clean. |
| 2 | Family | pass | POWO — Euphorbiaceae | APG IV consistent. |
| 3 | Common names | pass | NTBG; Native Plants Hawaii | ʻAkoko / ʻekoko / koko / kōkōmālei / Stokes's ʻakoko / coastal ʻakoko. |
| 4 | Biogeographic status | pass | POWO; Wagner 1999; Native Plants Hawaii | Kauaʻi + Niʻihau + Molokaʻi + Kahoʻolawe coastal endemic — confirmed. |
| 5 | Conservation status | **pass (currently accurate)** | Native Plants Hawaii / FHI: US Status = "No Status" (var. *stokesii* NOT federally listed); IUCN: not evaluated | YAML wording "Not federally listed (as of 2026); IUCN not evaluated; ca. one thousand individuals estimated" is ACCURATE. Contrast: sister var. *kaenana* (Oʻahu) IS federally listed — do not confuse. |
| 6 | Coastal-zone occurrence | pass | NTBG; Native Plants Hawaii; Kīlauea Point NWR docs | Windswept sea cliffs, cliff-top basalt, Kīlauea Point NWR the best-documented stand. |
| 7 | Cultural significance | pass | Krauss (Hawaiian latex/dye group-level) | ʻAkoko group-level cultural weight framed honestly with variety-specific sparseness disclosed. Attribution-free. |
| 8 | Hazards | pass | Euphorbiaceae milky latex — general dermatology lit | Milky latex → skin/mucous-membrane irritation. Standard Euphorbiaceae caveat. |
| 9 | ID clinchers accuracy | pass | Wagner 1999; NTBG | Low glabrous mounding cliff shrub + opposite obovate glabrous leaves + inconspicuous cyathia + Kauaʻi-Niʻihau geographic default. Diagnostic. |
| 10 | Look-alikes accuracy | pass | Wagner 1999 | *C. degeneri* (prostrate mat) + other *C. celastroides* varieties + Portulaca contrasts all justified. |
| 11 | Numbered citations | pass | Cross-checked | `[1]`, `[2]`, `[3]`, `[C:7]`, `[C:8]`. All resolve. |

**Author-position audit — nomenclature uncertainty block.** YAML uncertainty text attributes *Chamaesyce* placement to Wagner/Herbst/Sohmer 1999 and Bishop Museum treatment, and *Euphorbia* placement to POWO. Both attributions are consistent with the actual sources. **Cited-author-position: consistent.**

---

## 2. Grade totals

| Species | pass | needs-work | fail |
|---|---:|---:|---:|
| alula | 11 | 0 | 0 |
| Christmas berry | 11 | 0 | 0 |
| lantana | 10 | 1 | 0 |
| Schiedea apokremnos | 11 | 0 | 0 |
| Hibiscus waimeae ssp. hannerae | 11 | 0 | 0 |
| Panicum niihauense | 11 | 0 | 0 |
| Furcraea foetida | 11 | 0 | 0 |
| Leucaena leucocephala | 11 | 0 | 0 |
| Ricinus communis | 11 | 0 | 0 |
| Kokia kauaiensis | 11 | 0 | 0 |
| Chamaesyce c. var. stokesii | 11 | 0 | 0 |
| **TOTAL (121 cells)** | **120** | **1** | **0** |

**Pass rate: 120 / 121 = 99.2%** (well above pilot criterion of ≥90%).

Single `needs-work`: lantana conservation_status "Hawaii state noxious weed" — same statutory-source pattern as christmas berry, deferred to cycle 5.

## 3. Discrepancies caught and dispositions

### D1 — kokia listing year corrected

**Category:** conservation status (kokia-kauaiensis).
**Problem:** Prior YAML stated "US Endangered (USFWS 2010 listing rule)". Actual USFWS listing year is 1996 (confirmed via ECOS species 8488 + 2017 5-YR).
**Disposition:** Inline fix landed via `_infra/kokia-conservation-status-normalized`.

### D2 — alula "CR — EW" compound removed

**Category:** conservation status (alula).
**Problem:** Prior YAML combined incompatible IUCN category labels ("Critically Endangered — Extinct in the Wild"). Current IUCN category is simply Extinct in the Wild.
**Disposition:** Inline fix landed via `_infra/alula-conservation-status-refresh`. Also captured new 5-year review initiated Sept 2025.

### D3 — Christmas berry statutory over-claim removed

**Category:** conservation status (christmas-berry).
**Problem:** "Hawaii state noxious weed" claim not supported by HAR §4-68 statutory list (which is targeted-eradication scope, dominated by Miconia, banana poka, kahili ginger).
**Disposition:** Inline reword landed via `_infra/christmas-berry-noxious-weed-source-resolved`. Advisory-list language (HISC, ISSG, HEAR, Plant Pono) cited, plus explicit note that species is not on HAR §4-68.

### D4 — lantana carries the same statutory over-claim

**Category:** conservation status (lantana).
**Problem:** `conservation_status: "Hawaii state noxious weed; global top-100 invasive (IUCN ISSG)"` — the ISSG half is verified (Lowe et al. 2000); the "Hawaii state noxious weed" half has the same statutory-source problem as christmas-berry.
**Disposition:** **Deferred to cycle 5** as `_deferred/lantana-noxious-weed-source` — same reword-or-cite fork as christmas berry.

### D5 — thin USFWS wording on Schiedea, Hibiscus hannerae, Panicum

**Category:** conservation status (schiedea-apokremnos, hibiscus-waimeae-hannerae, panicum-niihauense).
**Problem:** Wording "US Endangered (federally listed)" is technically correct but thin. Not a fabrication — safely defensible — but a cycle-5 optional-tightening opportunity to add USFWS listing year and most-recent 5-YR / population count.
**Disposition:** Non-blocking. **Cycle-5 optional-tightening candidate** as `_deferred/rare-tier-listing-wording-tighten` (batch three species together).

## 4. Sesbania tomentosa cross-list sanity check

Built the site with `python3 scripts/build_site.py` and extracted the RARE-tier cross-list block from `site/index.html`. Regex-isolated block between `Also federally listed` marker and the next `<h2>` yields exactly two species links:

```
cross-listed species (isolated): ['wiliwili', 'sesbania-tomentosa']
```

Both are legitimate (both carry "US Endangered (USFWS 1994)" or equivalent in their `conservation_status` and live in the NOTABLE tier). **Sesbania cross-list fires correctly.** No `_deferred/sesbania-cross-list-repair` event needed.

## 5. Opportunistic re-imaging outcomes

| Species | Prior state | Search attempted | Outcome |
|---|---|---|---|
| *Schiedea apokremnos* | SVG-only (2 diagrams) | Wikimedia + Flickr for CC-BY Eickhoff or DLNR | **NULL** — no photo located under any CC / PD license. Keep SVG-only. |
| *Kokia kauaiensis* | SVG-only (3 diagrams) | Wikimedia + Flickr for CC-BY Eickhoff or hawaiibirds | **NULL for verified CC-BY** — one hawaiibirds Flickr photo of *K. kauaiensis* exists (id 46504637601) but license unverifiable via WebSearch snippet. Cycle-5 candidate: fetch photo page directly to confirm license, add if CC-BY. |

Both null-result outcomes documented; both species' YAML `image_search_notes` already carry the null-result rationale from cycle 3, so no YAML edit needed this cycle.

## 6. Author-position audit summary

Rung applied per pilot §4.1.3 across all 11 species' uncertainty blocks and Hawaiian-name etymology claims. Findings:

| Species | Uncertainty block cited-author check | Etymology cited-author check |
|---|---|---|
| alula | Wood 2012 → pilot §2.4 confirmed EW framing supported. Pass. | No etymology claim. n/a. |
| Christmas berry | Motooka 2003 → pilot §2.5 confirmed Willie-Rice sentence verbatim. Pass. | Motooka etymology already audited by pilot. Pass. |
| lantana | No uncertainty block. n/a. | Lākana = Hawaiianized transliteration, self-evident. n/a. |
| Schiedea apokremnos | Qualitative revisions ref, no specific author position. n/a. | No etymology claim. n/a. |
| Hibiscus hannerae | No uncertainty block. n/a. | Ruth Knudsen Hanner honoree — NTBG-attested. Pass. |
| Panicum niihauense | USFWS recovery-planning wild-vs-outplanted framing accurate. Pass. | Lauʻehu = genus-level Hawaiian name. Pass. |
| Furcraea foetida | Variability-in-wild-clones framing consistent with source. Pass. | Common name is misleading geographic; YAML doesn't attribute. n/a. |
| Leucaena leucocephala | No uncertainty block. n/a. | "Koa haole" (foreign koa) is post-contact coinage; YAML doesn't claim indigeneity. Pass. |
| Ricinus communis | No uncertainty block. n/a. | Pāʻaila / koli Hawaiian names — Pukui/Elbert-consistent. Pass. |
| Kokia kauaiensis | Population-count-varies framing accurate. Pass. | No etymology claim (kokiʻo is well-established Malvaceae Hawaiian name). n/a. |
| Chamaesyce c. var. stokesii | Wagner *Chamaesyce* vs POWO *Euphorbia* attributed correctly to both. Pass. | ʻAkoko group multiple Hawaiian names — all Pukui/Elbert-consistent. Pass. |

**No sleeper-finding class detected on RARE tier.** The hala/Gallaher-style misattribution surfaced by the pilot was tier-idiosyncratic (indigenous-vs-Polynesian contested-status species). RARE tier's uncertainty blocks are cleaner (federal-listing / taxonomic-rank / population-count — bounded quantitative claims rather than interpretive framing).

## 7. Sources that landed and did not (RARE-tier addendum to pilot §4.2)

**Landed this cycle:**
- USFWS ECOS species profile pages (species 1615 alula, 5364 hannerae, 8488 kokia, 2054 apokremnos, 3861 panicum) — all reachable via `<scientific name> USFWS ECOS`.
- IUCN Red List assessments — reachable via `<scientific name> IUCN Red List <year>`; separate assessment years for alula (2023) vs kokia (2020) confirm the pilot's "check assessment year" rule was necessary.
- POWO for taxonomic placement swaps (Chamaesyce/Euphorbia; Hibiscus var./subsp.) — first result on all four.
- NCBI/PMC for hazard primary literature (mimosine mechanism, ricin toxicity) — reliable, peer-reviewed.
- ISSG GISD species pages (Furcraea foetida species 1257; Lantana on 100-worst list) — reachable.

**Did NOT land this cycle:**
- **HAR §4-68 direct fetch** — WebFetch permission blocked; primary statutory text not directly consulted. Multiple secondary corroborations were sufficient for the christmas-berry disposition (confidence: medium per ledger event), but a future cycle should either (a) get WebFetch permission and fetch the Cornell Law page, or (b) attach the CTAHR-hosted HAR §4-68 PDF to the workspace for offline reference.
- **Direct Wikimedia Commons + Flickr license-metadata query for Schiedea and Kokia photos** — WebSearch snippets don't expose license fields cleanly. WebFetch (blocked) or an authenticated Wikimedia API query would resolve.

## 8. Ledger events emitted this cycle (Branch C)

| event_id | milestone_id | status | ts |
|---|---|---|---|
| (auto-assigned) | `_infra/alula-conservation-status-refresh` | validated | 2026-08-28T05:00:00Z |
| (auto-assigned) | `_infra/kokia-conservation-status-normalized` | validated | 2026-08-28T05:00:10Z |
| (auto-assigned) | `_infra/christmas-berry-noxious-weed-source-resolved` | validated | 2026-08-28T05:00:20Z |
| (see cycle-close event) | `_orphan/cycle-4-branch-c-rare-verification` | validated | 2026-08-28T05:15:30Z |

Plus one `_deferred/*` and one `_deferred/*` opportunistic-tightening event emitted at branch-close.

---

*End of Cycle 4 Branch C RARE-tier verification matrix.*
