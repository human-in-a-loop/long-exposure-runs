# Cycle 3 — Branch C Task 4: Deep-Verification Pilot (5 species)

**Scope.** Stress-test the claim × source verification matrix against 5 species (`naupaka-kahakai`, `hala`, `kukui`, `alula`, `christmas-berry`) so cycle 4 can apply a refined checklist to all 45+ species. Deliverable is a methodology, not a per-species audit — species verdicts exist to shake bugs out of the process.

**Effort:** high. **Date:** 2026-08-28. **Reviewer:** Branch C (cycle 3).

---

## 1. Methodology

### 1.1 The 11 claim categories (matrix as workflow)

Every species pass loops through the same 11 categories in this order — earlier categories cheaply gate later ones (a bad authority string is often a symptom of a stale source that will also produce bad status claims):

1. **Scientific name + authority** — cross-check against POWO (Kew), World Flora Online (WFO), and the Smithsonian FHI checklist. Wagner 1999 is the branch anchor but is 27 years old; use it for the reference frame and note nomenclatural changes since (e.g., *Scaevola sericea* → *S. taccada*; *Tournefortia argentea* → *Heliotropium foertherianum*).
2. **Family** — verify APG IV placement via Wikispecies or WFO. Wagner predates APG IV; families almost always agree for the plants in this guide but the check is cheap.
3. **Common names (Hawaiian, English)** — Wagner + NTBG profile + Krauss 1993. Cross-check any Hawaiian name against Pukui/Elbert or a Bishop Museum Hawaiian-name index when disputed.
4. **Biogeographic status** — Wagner + NTBG + Imada 2019 checklist. If two of these disagree, the YAML MUST carry an `uncertainty:` block. Both simple-indigenous and simple-Polynesian-introduction stories often hide a "both/and" reality (see hala below) — the uncertainty block should reflect that, not force a false dichotomy.
5. **Conservation status** — this is a **live-updated field**. USFWS ECOS species page (`ecos.fws.gov/ecp/species/<id>`) AND the most recent 5-Year Review, plus current IUCN Red List assessment (check assessment year — reassessment is common), plus Hawaii DLNR-DOFAW fact sheet. Never rely on the historical listing rule alone.
6. **Coastal-zone occurrence on unpopulated Kauaʻi coast** — NTBG range narrative + Wood 2012 + Hawaii Biodiversity Mapping Project. For rare cliff endemics, cross-check Wood & Perlman NTBG field notes.
7. **Cultural significance** — primary ethnobotany: Krauss 1993; Handy & Handy 1972; Abbott 1992. Never cite a modern blog or ornamental-plant page as ethnobotanical primary. For moʻolelo, prefer traditional attribution ("Hawaiian tradition holds…") over any single modern retelling.
8. **Hazards** — Wagner + DOH/DOA/CTAHR bulletins + a peer-reviewed toxicology reference for anything ingested. For contact dermatitis (Anacardiaceae), a bulletin suffices.
9. **ID clinchers accuracy** — NTBG + Little & Skolmen 1989 (for trees) or Rock 1913 (older but still consulted for canoe plants). Verify each clincher is *diagnostic* against the look-alike list (i.e., the look-alike does not also have that trait).
10. **Look-alikes accuracy** — Wagner + field-key logic check: for each pairing, confirm at least one clincher separates them, and that no more-likely confusion pair is missing.
11. **Numbered citations do what they claim** — the highest-yield check. For every `[N]` on the species page, open the numbered source via WebSearch and confirm the specific claim is in it. This catches *citation drift* — where the correct reference number sits next to a claim the reference does not actually support.

### 1.2 Sources used and their reliability in practice

| Source | Reliability in the pilot |
|---|---|
| **NTBG "Meet the Plants" (ntbg.org/database/plants/detail/…)** | Consistently reachable, primary-quality, descriptions match Wagner. First stop for every species. |
| **Kew POWO (powo.science.kew.org)** | Best single check for accepted name + authority + synonymy. Reachable. |
| **World Flora Online (worldfloraonline.org)** | Corroborates POWO. Reachable. |
| **Smithsonian FHI (naturalhistory.si.edu / botany.si.edu)** | Not always deep-indexed by WebSearch; the checklist itself is a PDF/DB. Usable as a name-and-status confirmation, not for narrative. |
| **USFWS ECOS species page** | Authoritative for federal listing status; each species has a numeric endpoint (e.g., `ecos.fws.gov/ecp/species/1615` for *Brighamia insignis*). The 5-Year Review PDF is the current-status document — read it, do not rely on the original 1994 listing rule. |
| **IUCN Red List (iucnredlist.org)** | Authoritative but versioned — always note the assessment year; a plant's category can move (e.g., CR possibly-EW → EW). |
| **DLNR-DOFAW fact sheets** | Useful cross-check; sometimes outdated relative to USFWS/IUCN. |
| **Wagner 1999 (Manual)** | Not full-text online; cite it from secondary confirmation (NTBG, POWO, native-plant databases that quote it). |
| **Motooka et al. 2003 (Weeds of Hawaii's Pastures)** | Full text at CTAHR `www3.ctahr.hawaii.edu/invweed/`. Reachable and quotable. |
| **Krauss 1993 / Handy & Handy 1972 / Abbott 1992** | Not full-text online. Cross-check ethnobotanical claims against Bishop Museum, Kapiʻolani CC campus-garden pages, and Manoa Heritage Center. |
| **Wikipedia** | *Direction-finder only.* Use it to locate primary sources (its references section is the value); never quote it as a citation. |
| **Popular blogs (Big Island Bees, statesymbolsusa, ornamental-plant vendors)** | Not citations. Useful only to triangulate popular etymologies before validating against a proper source. |
| **`hear.org` (Hawaii Ecosystems at Risk)** | Reachable but the site is legacy; several links now redirect. Usable for weed-status claims with a live-URL check. |

### 1.3 Verification workflow (replayable)

For each species:

1. Read `data/species/<slug>.yaml`. Extract: scientific name, authority, family, all common names, status, conservation_status, cultural claims (list them), hazard claims, every clincher, every look-alike, every uncertainty block, and the `citations:` array.
2. Open the numbered references (`REFERENCES.md` for `[N]`, `data/references/branch-<x>.md` for `"X:N"` tokens). Note what each cited source actually is.
3. Run WebSearch batches of 3–4 parallel queries per species covering: (a) name + authority + family; (b) conservation status current + IUCN + USFWS; (c) NTBG profile + cultural claim; (d) each cited-source-does-what-it-claims check.
4. Grade each of the 11 categories `pass / needs-work / fail`. Rule: if the source is unreachable or the check inconclusive, grade `needs-work` — never `pass` on faith.
5. For every `needs-work` / `fail`, decide inline-YAML-fix vs. deferred ledger event. Inline fixes are only when the correction is small and unambiguous; anything requiring narrative rewrite or multi-species impact goes to `_deferred/`.

Budget observed in the pilot: **~20–30 min per species** (5 min YAML read + claim extraction; 15–20 min WebSearch batches; 5 min grading and note-writing). Faster for a common indigenous species with no uncertainty block (naupaka: 15 min); slower for a species with citation drift or a live-updated conservation status (hala: 35 min; alula: 30 min).

---

## 2. Per-species results

### 2.1 `naupaka-kahakai` — *Scaevola taccada* (Gaertn.) Roxb.

| Claim category | Verdict | Source(s) checked | Notes |
|---|---|---|---|
| Scientific name + authority | pass | POWO, NTBG, DLNR | *S. taccada* (Gaertn.) Roxb. is the current accepted name (was *S. sericea* in older Wagner). |
| Family | pass | POWO, Wikispecies | Goodeniaceae, APG IV consistent. |
| Common names | pass | NTBG, DLNR, Krauss | Naupaka kahakai / beach naupaka / half-flower / sea lettuce all in wide use. |
| Biogeographic status | pass | NTBG, DLNR | Indigenous; buoyant-fruit pantropical distribution. |
| Conservation status | pass | n/a | Correctly `null`; species is not listed. |
| Coastal-zone occurrence | pass | NTBG, DLNR, general Nā Pali surveys | Strand + dune matches all sources. |
| Cultural significance | pass | Manoa Heritage Center, Maui Ocean Center, KapCC gardens | Half-flower moʻolelo is traditional and multi-versioned (Pele version, star-crossed-lovers version, jealous-woman version); YAML wording "in Hawaiian tradition … often told with…" is appropriately un-attributed. Good pattern for other moʻolelo claims. |
| Hazards | pass | n/a | Correctly `null`. |
| ID clinchers accuracy | pass | NTBG description | Half-flower + obovate fleshy leaves + white succulent drupe + mounding-shrub habit — all confirmed diagnostic. |
| Look-alikes accuracy | pass | NTBG, Wagner via secondary | Mountain naupaka + tree heliotrope are the right two to call out. |
| Numbered citations | pass | `[1]` Wagner, `[2]` Smithsonian FHI, `[3]` NTBG, `[6]` Starr — all reasonable placements | No citation drift observed. |

### 2.2 `hala` — *Pandanus tectorius* Parkinson ex Du Roi

| Claim category | Verdict | Source(s) checked | Notes |
|---|---|---|---|
| Scientific name + authority | pass | POWO, WFO, GBIF | *P. tectorius* Parkinson ex Du Roi confirmed. |
| Family | pass | POWO | Pandanaceae, APG IV: Pandanales. |
| Common names | pass | NTBG, Krauss | Hala / pū hala / screwpine confirmed. |
| Biogeographic status | **needs-work** | Gallaher 2015 (paper), Gallaher "Past and Future of Hala" review, NTBG | See discrepancy #1 — uncertainty block **misattributes the Polynesian-introduction argument to Gallaher**, who in fact supports natural pre-human dispersal (1.2 Myr fossil on Kauaʻi) with additional canoe-plant cultivars added later. Framing is a false dichotomy. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | NTBG, DLNR | Valley-mouth prop-rooted stands well-documented. |
| Cultural significance | pass | Krauss, Manoa Heritage | Lauhala/hīnano weaving and mele well-attested. Guide's stance of naming relationships without harvest instructions is appropriate. |
| Hazards | pass | NTBG | Sharp recurved marginal + midrib spines confirmed. |
| ID clinchers accuracy | pass | NTBG, NC Extension | Prop roots, 3-ranked strap leaves with spines both sides + midrib, wedge-key syncarp — diagnostic. |
| Look-alikes accuracy | pass | NTBG | Coconut and kī are reasonable coastal-tree confusions. |
| Numbered citations | **needs-work** | `[A:3]` — Gallaher 2015 title in `data/references/branch-a.md` reads *"A long history of dispersal and vicariance driving diversification of Pandanus"*. Actual paper title is *"A long distance dispersal hypothesis for the Pandanaceae and the origins of the Pandanus tectorius complex"* (Mol. Phylogenet. Evol. 83: 20–32). Authors, volume, pages correct; **title wrong**. See discrepancy #2. Also `[A:3]` is used to support a "Polynesian introduction" argument that the paper does not make — this is the more serious drift. |

### 2.3 `kukui` — *Aleurites moluccanus* (L.) Willd.

| Claim category | Verdict | Source(s) checked | Notes |
|---|---|---|---|
| Scientific name + authority | pass | POWO, USDA-NRCS, MoBot | *A. moluccanus* (L.) Willd. confirmed. |
| Family | pass | POWO | Euphorbiaceae; APG IV places order Malpighiales. |
| Common names | pass | NTBG, Krauss | Kukui / candlenut / Indian walnut confirmed. |
| Biogeographic status | pass | NTBG, Manoa Heritage | Polynesian introduction / canoe plant confirmed. |
| Conservation status | pass | n/a | Not listed. |
| Coastal-zone occurrence | pass | NTBG | Valley-mouth / riparian; absence from strand correct. |
| Cultural significance | pass | statesymbolsusa.org, HRS §5-8, Netstate | **State tree of Hawaiʻi (designated 1959)** verified via Hawaii Revised Statutes §5-8. YAML wording ("official tree of the State of Hawaiʻi") is exact. |
| Hazards | pass | Wisdomlib, Vitalibrary, Kuki'olani CC | Raw nut laxative + mildly toxic (saponins, phorbol esters) confirmed. Traditional processing (roasting for ʻinamona) is the standard framing. |
| ID clinchers accuracy | pass | NTBG, MoBot | Silvery-green canopy, dimorphic leaves (palmate juvenile/simple adult), stellate hairs, green-to-black drupe — all diagnostic. |
| Look-alikes accuracy | pass | NTBG | Noni + castor are reasonable coastal-valley pairs; castor toxicity note is warranted. |
| Numbered citations | pass | `[1]` Wagner, `[2]` FHI, `[3]` NTBG, `[9]` Little & Skolmen, `[10]` Krauss — all appropriate | No drift. |

### 2.4 `alula` — *Brighamia insignis* A. Gray

| Claim category | Verdict | Source(s) checked | Notes |
|---|---|---|---|
| Scientific name + authority | pass | POWO, NTBG, Wikispecies | *B. insignis* A. Gray confirmed. |
| Family | pass | POWO | Campanulaceae (Hawaiian lobelioid). |
| Common names | pass | NTBG, DLNR, Revelator | ʻĀlula / ʻōlulu / pua ʻala / cabbage-on-a-stick / vulcan palm confirmed. |
| Biogeographic status | pass | NTBG, DLNR | Endemic to Kauaʻi + (formerly) Niʻihau. |
| Conservation status | **needs-work** | USFWS ECOS species 1615; USFWS 5-Year Review 2022; IUCN Red List 2020 assessment; NTBG | YAML says *"US Endangered (USFWS 1994); IUCN Critically Endangered — Extinct in the Wild"*. Two issues: (a) the IUCN category is now simply **Extinct in the Wild (EW)** — the 2016 assessment was "CR possibly-extinct in the wild" but the current listing is EW; the compound "Critically Endangered — Extinct in the Wild" is not a valid IUCN category. (b) USFWS listing date is correct (1994) but a reader benefits from noting the 2022 5-Year Review's confirmation that no wild individuals remain. See discrepancy #3. |
| Coastal-zone occurrence | pass | NTBG, Wood 2012 | Nā Pali sea-cliff faces; effectively extinct in wild — the YAML already flags this in its own uncertainty block. |
| Cultural significance | pass | Revelator, DLNR | "Signature endemic of Nā Pali" is standard framing in conservation writing. |
| Hazards | pass | (none physiological) | YAML correctly reframes hazard as regulatory / access-safety — do not approach. |
| ID clinchers accuracy | pass | NTBG, BGCI, iNaturalist | Cabbage-on-a-stick silhouette, tubular pale-yellow flowers, cliff habitat, Kauaʻi–Niʻihau restriction — diagnostic. |
| Look-alikes accuracy | pass | NTBG | *B. rockii* (Molokaʻi/Maui-Nui, white flowers) is the correct sister. Cordyline is a coarser but reasonable public confusion. |
| Numbered citations | pass | `[1]` Wagner, `[2]` FHI, `[3]` NTBG, `[4]` Bishop Museum, `[5]` USFWS 1994 listing rule, `[11]` Wood 2012 | All match. Consider adding a `[C:?]` for the USFWS 2022 5-Year Review — currently no reference points to it. See discrepancy #3. |

### 2.5 `christmas-berry` — *Schinus terebinthifolia* Raddi

| Claim category | Verdict | Source(s) checked | Notes |
|---|---|---|---|
| Scientific name + authority | pass | POWO, Motooka, CTAHR | *S. terebinthifolia* Raddi confirmed. Note: literature commonly uses both "terebinthifolia" and "terebinthifolius"; POWO settles on the feminine "terebinthifolia" — YAML matches current usage. |
| Family | pass | POWO | Anacardiaceae. |
| Common names | pass | Motooka, CTAHR, HEAR | Christmas berry / Brazilian pepper (+ wilelaiki handled in uncertainty block). |
| Biogeographic status | pass | HEAR, Cal-IPC, Motooka | Introduced from South America pre-1900. |
| Conservation status | **needs-work** | HDOA HAR §4-68; HEAR; Plant Pono | YAML says *"Hawaii state noxious weed"*. Schinus is *widely called* a noxious weed and is on multiple invasive lists (HEAR, HISC, Plant Pono high-risk), but I could not verify from primary source (HAR Chapter 4-68) that *S. terebinthifolia* is specifically on the HDOA official noxious-weed-for-eradication-or-control list. Chapter 68 is a targeted list (kahili ginger, miconia, etc.), not a comprehensive invasive registry. Grade `needs-work` pending direct read of HAR §4-68. See discrepancy #4. |
| Coastal-zone occurrence | pass | HEAR, Nā Pali vegetation surveys | Widespread in drier lower valleys; matches observed distribution. |
| Cultural significance | pass | n/a | Correctly `null` (post-contact invasive). |
| Hazards | pass | CTAHR, Cal-IPC | Contact dermatitis (Anacardiaceae — poison-ivy cousin) and mildly-toxic berries confirmed. |
| ID clinchers accuracy | pass | Motooka, CTAHR, NC Ext. | Winged rachis between leaflets is the key clincher; red winter berries; pepper/turpentine aroma. All diagnostic. |
| Look-alikes accuracy | pass | Wagner (*Rhus sandwicensis*) | Native neneleau contrast is correct (wingless rachis, upland). Toxicodendron footnote is defensible — same family, same rash mechanism. |
| Numbered citations | pass | `[1]` Wagner, `[2]` FHI, `[13]` HEAR, `[14]` Motooka — all placements match | Motooka *does* contain the Willie-Rice etymology per its own text: *"'wilelaiki' deriving from a local political figure, Willie Rice, who used to wear the berries on his hat."* Uncertainty-block citation to `[14]` is faithful. |

**Verdict totals: pass = 45, needs-work = 4, fail = 0.**

---

## 3. Discrepancies caught

### Discrepancy #1 — `hala` uncertainty block misattributes Gallaher

**Category:** biogeographic status (hala).
**Problem:** The `uncertainty:` block on `data/species/hala.yaml` says Gallaher et al. "argue instead that Hawaiian hala is a Polynesian introduction". Gallaher's 2015 paper argues the *opposite*: long-distance natural dispersal explains *P. tectorius* distribution, and >1.2 Myr fossil *Pandanus* fruit on Kauaʻi's north shore is direct evidence for pre-human presence. Gallaher's separate review "The Past and Future of Hala in Hawaiʻi" frames hala as *both* indigenous (via natural dispersal) *and* enriched by Polynesian cultivar introductions — not a strict either/or.

**Recommended fix — deferred ledger event (not an inline fix):**
- **Milestone id:** `_deferred/hala-uncertainty-rewrite`
- **Narrative:** "Cycle-3 pilot verification found that the hala.yaml uncertainty block misattributes a Polynesian-introduction argument to Gallaher et al. 2015 (`[A:3]`). Gallaher in fact supports pre-human natural dispersal (>1.2 Myr Kauaʻi fossil evidence) while noting that additional cultivars arrived with Polynesian settlers. Rewrite the uncertainty block to reflect the both/and consensus: *hala is indigenous via natural long-distance dispersal of buoyant fruit, and a subset of modern Hawaiian hala varieties represent Polynesian-introduced cultivars grafted onto that indigenous stock; the earlier framing of a clean dispute between Wagner-indigenous vs. Gallaher-Polynesian-introduction was a mis-reading of Gallaher.* Retain `[A:1]` and `[A:3]` citations; add a citation to Gallaher's 'Past and Future of Hala in Hawaiʻi' review as `[A:?]` (new)."
- **Why deferred, not inline:** rewrite touches narrative interpretation and requires adding a new numbered reference; too large for a mechanical field-swap.

### Discrepancy #2 — Gallaher 2015 title in `data/references/branch-a.md`

**Category:** numbered citations do what they claim (hala).
**Problem:** `[A:3]` currently reads: *"Gallaher, T. J., Callmander, M. W., Buerki, S., & Keeley, S. C. (2015). A long history of dispersal and vicariance driving diversification of Pandanus (Pandanaceae). Molecular Phylogenetics and Evolution 83: 20–32."*
**Actual title:** *"A long distance dispersal hypothesis for the Pandanaceae and the origins of the Pandanus tectorius complex."*
Authors, journal, volume, and pages are correct.

**Recommended fix — inline YAML/reference-file edit:**
- **File:** `data/references/branch-a.md`
- **Field:** entry `[A:3]` (line 11)
- **Old:** `A long history of dispersal and vicariance driving diversification of *Pandanus* (Pandanaceae).`
- **New:** `A long distance dispersal hypothesis for the Pandanaceae and the origins of the *Pandanus tectorius* complex.`
- **Also update** the descriptive tail from *"Provides evidence used in the modern-introduction argument for hala's presence in Hawaiʻi"* to *"Provides evidence for natural long-distance dispersal of Pandanus (relevant to the indigenous-vs-canoe-plant discussion of hala in Hawaiʻi)."* (this second edit depends on discrepancy #1 being resolved consistently).

### Discrepancy #3 — `alula` conservation_status wording

**Category:** conservation status (alula).
**Problem:** YAML string *"US Endangered (USFWS 1994); IUCN Critically Endangered — Extinct in the Wild"* combines two IUCN category labels. Since ~2020 the IUCN Red List category for *B. insignis* is simply **Extinct in the Wild (EW)**. "CR possibly-EW" was the 2016 wording. Additionally, USFWS listing is still Endangered (species profile 1615), and the 2022 5-Year Review explicitly confirms no known wild individuals — a fact worth capturing.

**Recommended fix — inline YAML fix:**
- **File:** `data/species/alula.yaml`
- **Field:** `conservation_status` (line 9)
- **Old:** `"US Endangered (USFWS 1994); IUCN Critically Endangered — Extinct in the Wild"`
- **New:** `"US Endangered (USFWS 1994; 5-Year Review 2022 confirms no known wild individuals); IUCN Extinct in the Wild (assessment updated 2020)"`
- **Second fix (optional, cycle-4 candidate):** add a new reference to `data/references/branch-c.md` for the USFWS 2022 5-Year Review and the IUCN 2020 assessment, and append `"C:?"` to the `citations:` list. This is a small enough edit to inline, but I'm flagging it as cycle-4 work because Branch A owns the alula.yaml file and would want to coordinate the reference add.

### Discrepancy #4 — `christmas-berry` "Hawaii state noxious weed"

**Category:** conservation status (christmas-berry).
**Problem:** Claim that Schinus terebinthifolia is a "Hawaii state noxious weed" could not be verified against the primary source (HDOA HAR §4-68 list of Plant Species Designated as Noxious Weeds for Eradication or Control). Schinus is on many invasive-plant advisory lists (HISC, Plant Pono, HEAR, Cal-IPC) but the HAR §4-68 statutory list is narrower.

**Recommended fix — deferred ledger event (verify then edit):**
- **Milestone id:** `_deferred/christmas-berry-noxious-weed-source`
- **Narrative:** "Verify against primary source (HDOA HAR §4-68 current text — via `hdoa.hawaii.gov/pi/ppc/noxious-weed-list/` or law.cornell.edu) whether Schinus terebinthifolia is on the official Hawaii state noxious weed list. If YES, add a citation to HAR §4-68 as a new reference (`[C:?]` in branch-c.md) and leave the YAML wording alone. If NO, rewrite `conservation_status:` to *'Widely designated invasive (Hawaii Invasive Species Council Priority; PIER high-risk); not on HDOA HAR §4-68 noxious-weed-for-eradication list'* and add HISC / Plant Pono citations. Either way, the current wording is under-sourced."
- **Why deferred:** requires reading a specific statutory document and the correction depends on the answer; not a mechanical field-swap.

---

## 4. Refined checklist for cycle 4's full pass

This is the section the pilot exists to produce. Cycle-4 researchers should treat this as the working script.

### 4.1 New verification steps the pilot revealed as necessary

1. **Conservation status is a live field, not a historical one.** For every species with a non-null `conservation_status`, cycle 4 MUST:
   - Open the current USFWS ECOS species page (`ecos.fws.gov/ecp/species/<id>`) AND its most recent 5-Year Review PDF. Never rely on the original listing rule alone.
   - Check the IUCN Red List assessment year — reassessment happens (alula: 2016 CR-PE → 2020 EW).
   - Cross-check DLNR-DOFAW fact sheet.
   - Write the YAML string as `"US <status> (USFWS <year of listing>; 5-Year Review <year>); IUCN <current category> (assessment updated <year>)"`. Fixed template — avoids conflating categories the way alula did.
2. **State/agency weed and status labels need statutory citation.** "Hawaii state noxious weed" is not a claim; it's a statutory position under HAR §4-68. Before writing that phrase, open HAR §4-68 and confirm the species is on the list. If a species is invasive but not on the statutory list, phrase it as "Widely designated invasive (HISC/HEAR/Plant Pono/PIER); not statutorily listed under HAR §4-68". Same discipline for state tree / state flower / state symbol claims — cite HRS section.
3. **Uncertainty blocks need author-position verification, not just reference-drop.** The most damaging citation drift in the pilot (hala/Gallaher) was not a wrong reference number but a wrong *reading* of what the reference argues. For every `uncertainty:` block, cycle 4 must read enough of the cited paper (abstract + relevant section) to confirm the cited author actually holds the position the block attributes to them. Cite the paper's actual argument in one sentence within the block.
4. **Reference-file entries need title verification.** Cycle 4 must open `data/references/branch-*.md` and `REFERENCES.md`, and for every entry with a paper title, run a WebSearch to confirm title-authors-journal-volume-pages agree. The Gallaher entry drifted on title only, which is easy to miss but exactly the kind of thing an auditor will catch later. Budget ~1 min per reference entry.
5. **Common-name etymologies need a primary-lit source, not a blog.** Willie-Rice / wilelaiki etymology is well-sourced (Motooka 2003), but a similar claim from a beekeeping blog would not qualify. Verify the primary source *actually contains* the etymology sentence, not just the common name.
6. **Nomenclatural currency check.** For every species, run `<scientific name>` through Kew POWO (`powo.science.kew.org`). If POWO shows a different accepted name, the YAML must either match POWO or carry an uncertainty block explaining the divergence. Wagner 1999 will disagree with POWO for a handful of species (e.g., *Scaevola sericea* / *S. taccada*, *Tournefortia argentea* / *Heliotropium foertherianum*, *Schinus terebinthifolius* / *S. terebinthifolia*). These are already handled correctly in the pilot species but likely lurk in cycle-2 species not yet audited.
7. **Moʻolelo / traditional-knowledge claims should be attribution-free.** The naupaka half-flower moʻolelo pattern in this guide is the right model: "In Hawaiian tradition… often told with…" rather than citing a specific 20th/21st-century retelling. Cycle 4 should audit every cultural claim for accidental attribution to a modern author.

### 4.2 Sources that proved unreliable / should NOT be used

- **Popular blogs, beekeeping sites, ornamental-plant vendors** (Big Island Bees, Melvea, Melisse & Co., DavesGarden, wildflowersearch.org) — direction-finders only. Never cite.
- **Wikipedia** — direction-finder to primary sources; never cite. Use its references section.
- **Grokipedia and other AI-generated compilations** — do not cite; content is unverified.
- **`hear.org` legacy URLs** — many now redirect or 404. If citing HEAR, verify the URL resolves at the time of writing; prefer `plantpono.org` and `www3.ctahr.hawaii.edu/invweed/` for equivalent invasive-plant content.
- **Smithsonian FHI website's search UI** — the checklist itself is authoritative but the site's live search is unreliable via WebSearch; use POWO/WFO as a proxy and cite FHI only for name+status confirmations.

### 4.3 Budget estimate

Pilot observed **20–30 min per species**, distributed:
- 5 min: YAML read + claim extraction
- 15–20 min: 4 batches × 3–4 parallel WebSearch calls
- 5 min: grading + notes + discrepancy write-up

Cycle 4 will apply the refined checklist to ~45 species (45 – 5 pilot species = 40 remaining, but re-verifying the 5 pilot species post-fix is also cheap).

**Estimate: 45 species × 25 min = ~19 hours of researcher time.** Realistically, parallel WebSearch batches (this pilot did 4-way parallel queries per batch) cut wall time to **~12 hours**. Add ~3 hours for reference-file title-audit (item 4.1.4) and ~2 hours for reviewing/queuing deferred ledger events. **Total budget: ~15 hours wall time for a single researcher, or two half-days for a pair reviewing in parallel.**

Species tier affects speed:
- COMMON indigenous, no uncertainty block, no conservation status: **15 min** (naupaka pattern).
- COMMON/NOTABLE with cultural weight or Polynesian-introduction status: **25 min** (kukui pattern).
- RARE endemic with live conservation status: **30–35 min** (alula pattern — most of the extra time on ECOS/IUCN currency checks).
- Species with existing uncertainty block: **+10 min** to verify the block's cited-author-position (hala pattern).
- Invasive species: **25 min** (christmas-berry pattern — extra time on statutory list verification).

### 4.4 WebSearch query patterns

**Patterns that landed:**

- `<scientific name> IUCN Red List <year> critically endangered extinct wild` — lands the current IUCN category cleanly. *Example: `Brighamia insignis IUCN Red List 2024 critically endangered extinct wild` landed the current EW status and the 2020 reassessment date.*
- `<scientific name> USFWS ECOS current status endangered species` — lands the ECOS species profile URL. *Example: `Brighamia insignis USFWS ECOS current status endangered species` landed `ecos.fws.gov/ecp/species/1615` and the 2022 5-Year Review.*
- `<scientific name> NTBG <hawaiian name> site:ntbg.org` — lands the NTBG species profile directly. *Example: `Scaevola taccada NTBG naupaka kahakai site:ntbg.org` landed the NTBG detail page as the first hit.*
- `"<Author> <year>" <specific claim from citation>` — lands whether a cited author actually holds the position attributed. *Example: `"Gallaher" Pandanus tectorius Hawaii before human settlement indigenous` landed the direct quote showing Gallaher supports pre-human presence, catching the citation drift.*
- `"<common name>" "<supposed etymology source person>" Hawaii etymology` — lands community/blog attributions that can then be triangulated against Motooka/Wagner. *Example: `Schinus terebinthifolia "wilelaiki" "Willie Rice" Hawaii etymology` landed both Motooka's entry and popular corroboration.*
- `"<Author> <year>" "<book title>" <species> <specific fact>` — lands whether a book actually contains a claim. *Example: `"Motooka" 2003 "Weeds of Hawaii's Pastures" Schinus wilelaiki entry` landed the exact Motooka sentence on the Willie-Rice etymology.*
- `<scientific name> "<Authority>" <family> APG` — lands the authority string cleanly (POWO/GBIF/WFO all surface). *Example: `Pandanus tectorius "Parkinson ex Du Roi" authority Pandanaceae APG` landed POWO and WFO.*

**Patterns that did NOT land:**

- `site:naturalhistory2.si.edu "<scientific name>"` — Smithsonian FHI is not deeply indexed for WebSearch; returns few hits. Substitute with POWO / WFO.
- `site:dlnr.hawaii.gov "<scientific name>"` — inconsistent; DLNR fact sheets are PDFs and often don't rank. Better: `<scientific name> DLNR DOFAW Hawaii fact sheet`.
- Very generic conservation queries like `<species> conservation status` — return a mix of tourism blogs. Always attach source names (IUCN, USFWS, ECOS) to disambiguate.
- `<scientific name> Wagner Manual 1999` — Wagner is not full-text online; the query returns secondary discussions but not Wagner's text. Skip; rely on NTBG/POWO/Imada 2019 as Wagner-consistent secondaries.
- Statutory-list queries like `HAR 4-68 species list <scientific name>` — the statutory PDFs are not indexed by common-name search; open the HAR §4-68 PDF directly via `hdoa.hawaii.gov` and grep.

### 4.5 Order of operations for cycle 4 (checklist form)

For each of the remaining ~40 species, in one working session per species:

1. Open `data/species/<slug>.yaml` and `REFERENCES.md` + relevant `data/references/branch-*.md`.
2. Extract claims to a scratchpad list (11 categories).
3. Fire parallel WebSearch batch 1: name/authority/family (POWO + WFO + NTBG).
4. Fire parallel WebSearch batch 2: conservation status current (USFWS ECOS + IUCN + DLNR) — only if `conservation_status` is non-null.
5. Fire parallel WebSearch batch 3: cultural claims + Hawaiian-name attributions (Krauss/Handy/Manoa Heritage/statutory citations).
6. Fire parallel WebSearch batch 4: for each numbered citation supporting a load-bearing claim, verify the source's actual argument. This is where the drift lives.
7. Verify any `uncertainty:` block's cited-author-position (item 4.1.3).
8. Grade the 11 categories.
9. For every `needs-work`/`fail`, decide inline-fix vs. deferred ledger; write both formats precisely so the lead can act without follow-up.
10. Move to next species.

At the end of the cycle-4 pass, also run:
- **Reference-file title audit** (item 4.1.4) — one pass over all `[N]` and `[X:N]` entries.
- **Statutory-list audit** — a single read of HAR §4-68 and HRS §5-x to resolve deferred items from noxious-weed / state-symbol claims across all species at once.

---

*End of Cycle 3 Branch C Task 4 pilot report.*
