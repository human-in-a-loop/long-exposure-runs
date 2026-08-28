<!--
created: 2026-08-28T04:45:00Z
cycle: 4
run_id: run-2026-08-28T005658Z
fork: fork-f2dde7689a5d
branch: B
agent: worker
milestone: M-deep-verification (NOTABLE tier scope)
-->

# Cycle 4 — Branch B: NOTABLE Tier Deep Verification (15 species)

**Scope.** Apply the cycle-3 pilot's 11-category matrix to all 15 NOTABLE-tier species. Extra scrutiny on cultural claims (primary ethnobotany only), author-position audit on all contested-status uncertainty blocks (niu Harries, hau Wagner/Herbst, and any others discovered), Colocasia / Saccharum cultivar-diversity claims, and Sesbania cross-listing regression check.

**Effort:** high. **Date:** 2026-08-28. **Reviewer:** Branch B (cycle 4).

Methodology: per `reports/verification/cycle_03_pilot.md` §4 refined checklist. Cell grades: `pass` / `needs-work` / `fail`. Every `needs-work` / `fail` decides inline-fix (small, unambiguous) vs. `_deferred/*` ledger event (rewrite, multi-file impact, or requires new reference).

---

## 1. Matrix (15 species × 11 categories = 165 cells)

### 1.1 `naio` — *Myoporum sandwicense* A. Gray (canary, run first)

| Category | Verdict | Source consulted | One-line note |
|---|---|---|---|
| Scientific name + authority | pass | POWO, Wikispecies, WFO | *M. sandwicense* (A.DC.) A. Gray — POWO shows the parenthetical basionym; YAML `A. Gray` matches the current author string used by NTBG. |
| Family | pass (post-fix) | POWO, Wikipedia APG II history | Scrophulariaceae s.l. under APG; Wagner uses segregate Myoporaceae. Added `taxonomic_notes:` block inline to make the shift explicit for readers coming from Wagner. |
| Common names | pass | NTBG, DLNR | Naio / false sandalwood / bastard sandalwood confirmed. |
| Biogeographic status | pass | NTBG, POWO | Indigenous; Pacific-wide via Mangaia and Mauritius through the genus, consistent with YAML wording. No sources treat as introduced. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | Wood 2012, DLNR-DOFAW naio-thrips fact sheet [B:8] | Sea-cliff bases and back-beach shrub zones of drier western Nā Pali–Kona sector matches DLNR distribution notes. |
| Cultural significance | pass | Rock 1913 [B:1], sandalwood-era literature | The naio-as-sandalwood-substitute historical episode is well documented; framing as extractive-pressure example is standard. |
| Hazards | pass | DLNR-DOFAW | Not toxic; naio thrips inter-island biosecurity note is correct and useful. |
| ID clinchers accuracy | pass | NTBG, Chinnock 2007 [B:4] | Resin-dotted aromatic leaves + purple-spotted throat + pink-to-purple drupes: diagnostic. |
| Look-alikes accuracy | pass | Wagner via NTBG secondary | ʻūlei (compound-leaved rose-family) and Chenopodium (mealy-scurfy) are the correct contrasts. |
| Numbered citations | pass | 1, 2, 3, 8, B:1, B:4, B:8 all reachable | Chinnock [B:4] correctly cited as the monograph that retains Myoporaceae, referenced from the new taxonomic_notes block. |

**Canary result:** naio full matrix ran in ~25 min per pilot budget; family-placement rung caught the Wagner→APG issue and produced a real (small) fix. Proceeding to remaining 14.

---

### 1.2 `milo` — *Thespesia populnea* (L.) Sol. ex Corrêa

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO, WFO | Accepted; authority matches. |
| Family | pass | POWO | Malvaceae; APG IV consistent. |
| Common names | pass | NTBG, Krauss | Milo / portia tree / Pacific rosewood / seaside mahoe confirmed. |
| Biogeographic status | **needs-work** | Native Plants Hawaiʻi (KapCC), NTBG, Wagner | YAML says `status: indigenous`. Mainstream treatment (Wagner) is indigenous; Native Plants Hawaiʻi (KapCC): *"probably an indigenous tree. However, to date, there is no conclusive evidence to support milo as indigenous."* Some sources treat as Polynesian introduction (Krauss). A soft uncertainty block would strengthen the profile in line with hau/niu. **Deferred:** `_deferred/milo-indigenous-hedge-block` for cycle 5. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | NTBG, Wood 2012 | Back-beach strand + valley-mouth pond margins on drier sectors matches. |
| Cultural significance | pass | Krauss 1993 [10], Native Plants Hawaiʻi | Wood second only to kou for bowls/food vessels; kingly restriction (Kamehameha I's Waikīkī grove) well documented. YAML framing ("named the relationship without offering harvesting or working guidance") holds. |
| Hazards | pass | n/a | Correctly `null`. |
| ID clinchers accuracy | pass | NTBG, MNBG | Cordate + drawn-out tip + yellow-with-maroon flower + non-opening flat woody capsule = diagnostic against hau/kou. |
| Look-alikes accuracy | pass | NTBG | hau (splitting capsule vs milo's non-opening disk) + kou (orange vs yellow flower) are the right two contrasts. |
| Numbered citations | pass | 1, 2, 3, 9 all reachable | Little & Skolmen 1989 [9] and Wagner [1] both support ID + wood use. |

---

### 1.3 `kou` — *Cordia subcordata* Lam.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO, WFO | Confirmed. |
| Family | pass | POWO, Wikispecies (Cordioideae) | Boraginaceae s.l. under APG IV (Cordia subfamily Cordioideae). Cordiaceae is used by some splitters but Boraginaceae is the current mainstream. YAML correct. |
| Common names | pass | NTBG, DLNR, Bishop Museum ethnobotany | Kou / sea trumpet / kerosene wood confirmed. |
| Biogeographic status | pass | Burney et al. (Makauwahi Cave, Kauaʻi) via NTBG | Indigenous status **strengthened** since 2005 by subfossil evidence at Makauwahi Cave that pre-dates human arrival on Kauaʻi. YAML `status: indigenous` matches current treatment. New reference [B:16] added to branch-b.md pointing at this evidence for potential cycle-5 wiring into the kou profile as a strengthening citation (currently uncited from the YAML). |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | NTBG, Wood 2012 | Back-beach + valley-mouth flats on strand matches. |
| Cultural significance | pass | Bishop Museum ethnobotany, MNBG, Rock 1913 | ʻUmeke (bowls), utensils, calabashes — non-tainting wood. YAML wording ("ranked among the most respected timber woods") is faithful. |
| Hazards | pass | n/a | Correctly `null`. |
| ID clinchers accuracy | pass | NTBG | Orange trumpet cluster + fallen-orange-ring + sandpapery ovate leaves = diagnostic. |
| Look-alikes accuracy | pass | NTBG | milo (yellow flower + flat woody capsule) and *Cordia sebestena* (ornamental) — the right contrasts. |
| Numbered citations | pass | 1, 2, 3, 9, 10 all reachable | No drift. |

---

### 1.4 `kukui` — *Aleurites moluccanus* (L.) Willd.

*Re-verified from cycle-3 pilot; all 11 cells `pass`.*

| Category | Verdict | Note |
|---|---|---|
| Sci. name + authority | pass | Cycle-3 pilot pass holds. |
| Family | pass | Euphorbiaceae, Malpighiales. |
| Common names | pass | Kukui / candlenut / Indian walnut. |
| Biogeographic status | pass | Polynesian introduction; canoe plant. |
| Conservation status | pass | Correctly `null`. |
| Coastal-zone occurrence | pass | Valley mouths + riparian; silvery-green canopy diagnostic remote-view feature at Kalalau/Hanakoa/Hanakāpīʻai. |
| Cultural significance | pass | State tree via HRS §5-8 (1959) verified again this cycle. YAML wording "official tree of the State of Hawaiʻi" exact. |
| Hazards | pass | Raw-nut laxative/mild toxicity confirmed. |
| ID clinchers accuracy | pass | Silvery canopy + dimorphic leaves + stellate hairs + green-to-black drupe. |
| Look-alikes accuracy | pass | Noni (glossy simple leaves + knobby fruit) + castor (smaller shrub + prickly capsule). |
| Numbered citations | pass | 1, 2, 3, 9, 10 all reachable. |

---

### 1.5 `wiliwili` — *Erythrina sandwicensis* O. Deg.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO | Confirmed. |
| Family | pass | POWO | Fabaceae, subfamily Faboideae. |
| Common names | pass | NTBG, Krauss | Wiliwili / Hawaiian coral tree confirmed. |
| Biogeographic status | pass | NTBG, DLNR | Endemic; no dispute. |
| Conservation status | **needs-work (soft)** | Rubinoff et al. 2010 [B:6], DBEDT ERP 2023 EA, PMC 2023 review | YAML: "Not federally listed, but actively monitored because of the erythrina gall wasp." Current: E. erythrinae biocontrol (released 2008) is well established and reduced canopy damage effectively, but seed pods and inflorescences are still heavily impacted; a second biocontrol agent (*Aprostocetus nitens*) is in study/release consideration to fill that gap. YAML's phrasing "partially stabilized populations" is accurate but a one-sentence currency note on the pod-damage gap + second biocontrol would help. **Deferred:** `_deferred/wiliwili-aprostocetus-second-biocontrol-note` for cycle 5. |
| Coastal-zone occurrence | pass | NTBG, Wood 2012 | Dry sea cliffs + valley terraces of western Nā Pali–Kona matches. |
| Cultural significance | pass | Rock 1913 [B:1], Krauss 1993 [10] | Ama (outrigger floats), papa heʻe nalu (surfboards/bellyboards), net floats, seed lei — all in Rock's canoe-tree treatment and Krauss's canoe-plant chapters. |
| Hazards | pass | Wagner, NTBG | Small stem prickles + non-toxic seeds noted correctly. |
| ID clinchers accuracy | pass | NTBG | Leafless-at-flowering + curved constricted red-seed pods + trifoliate with large rhomboid terminal leaflet + soft orange-brown wood = diagnostic. |
| Look-alikes accuracy | pass | NTBG | *E. crista-galli* (introduced) + *Adenanthera pavonina* (bipinnate + evergreen) — good contrasts. |
| Numbered citations | pass | 1, 2, 3, 9, 10, B:1, B:6 all reachable | Rubinoff 2010 [B:6] specifically cited for the gall-wasp biology — appropriate anchor. |

---

### 1.6 `niu` — *Cocos nucifera* L.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO | Confirmed. |
| Family | pass | POWO | Arecaceae. |
| Common names | pass | NTBG, Krauss | Niu / coconut / coconut palm. |
| Biogeographic status | **pass (post-audit)** | **Harries 1978 [B:2] — abstract fetched via Springer** | **Author-position audit — the load-bearing test for this branch.** Harries 1978 (*The evolution, dissemination and classification of Cocos nucifera L.*, Bot. Rev. 44(3): 265–320) argues for natural drift-dispersal capability of the coconut across the Pacific (introducing the "niu kafa" wild ancestral morphology and the buoyant, salt-tolerant seed argument). Harries does not make a Hawaiʻi-specific pre-Polynesian arrival claim; he argues *the genus's* pantropical dispersal capability. The YAML's uncertainty block frames Harries as arguing *"pre-Polynesian presence in the Pacific plausible"* — this matches what Harries actually argued, and does NOT overreach into a Hawaiʻi-specific claim the paper doesn't support. **Author-position audit: PASS.** The careful hedging inserted in cycle-2 saved this citation from drift. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | Wood 2012, NTBG | Persistent groves at Kalalau, Honopū, Nuʻalolo Kai, Miloliʻi valley mouths — the cultural-planting-remnant framing is correct. |
| Cultural significance | pass | Krauss 1993 [10 via context], Handy & Handy 1972 [B:9 via context] | Provisioning tree (food/water/cordage/thatch/containers/oil/wood) — all canonical. Senit cordage naming is faithful. No harvest/preparation instruction leaks. |
| Hazards | pass | Standard tropical-medicine literature | Falling-fruit + shed-frond injury warning is standard and correctly worded. |
| ID clinchers accuracy | pass | NTBG | Unbranched grey ringed trunk + pinnate fronds + coconut drupe + valley-mouth grove context = diagnostic against loulu. |
| Look-alikes accuracy | pass | NTBG | Pritchardia spp. (loulu, palmate fronds + small purple-black fruit) — the correct native palm contrast. |
| Numbered citations | pass | 1, 2, 3, 10, B:2 all reachable | Harries [B:2] correctly anchored to the uncertainty block, nothing else. |

---

### 1.7 `hau` — *Hibiscus tiliaceus* L.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO | Confirmed. Note: some segregate treatments move to *Talipariti tiliaceum*; Wagner and current NTBG retain *Hibiscus tiliaceus* — YAML matches mainstream. |
| Family | pass | POWO | Malvaceae. |
| Common names | pass | NTBG | Hau / beach hibiscus / sea hibiscus. |
| Biogeographic status | **pass (post-audit)** | **Wagner Herbst & Sohmer 1999 [1], Herbst 1988 [B:5], HEAR, Little & Skolmen** | **Author-position audit.** Wagner treats hau as indigenous. Herbst 1988 [B:5] specifically argues the indigenous treatment on biogeographic grounds (pantropical, buoyant salt-tolerant seed, strand plant pattern). Some sources ("probably introduced to Hawaii by Polynesians" — Wildlife of Hawaii; Maui Ocean Center) reflect the historical "Polynesian introduction" reading; HEAR notes the status is contested. YAML's uncertainty block accurately captures BOTH the mainstream indigenous position AND the older cultural-argument minority — no hedge is dropped or overstated. **Author-position audit: PASS.** |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | NTBG, Wood 2012 | Valley bottoms + streams + back-beach flats; dominant lowland-coastal woody plant at Nā Pali valley mouths — matches Wood 2012 characterization. |
| Cultural significance | pass | Krauss 1993 [10 via context], Rock 1913 [B:1 via context] | Cordage from inner bark + light float wood — canonical Hawaiian material-culture treatment. Framing (name the relationship, credit contemporary keepers) is appropriate. |
| Hazards | pass | n/a | Correctly `null`. |
| ID clinchers accuracy | pass | NTBG, MNBG | Cordate leaf + velvety-white stellate underside + daily colour change (yellow morning → red-purple evening) + splitting capsule + sprawling thicket = diagnostic. Daily colour change is a delight to teach. |
| Look-alikes accuracy | pass | NTBG | milo (drawn-out tip + non-opening woody disk) + ornamental hibiscus (no wild coastal thicket habit). |
| Numbered citations | pass | 1, 2, 3, 10, B:1, B:5 all reachable | Herbst [B:5] appropriately anchored to the uncertainty block; other references support ID/ecology. |

---

### 1.8 `ohe-makai` — *Polyscias sandwicensis* (A. Gray) Lowry & G. M. Plunkett

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO, Lowry & Plunkett 2010 [B:3] | Confirmed; nomenclatural transfer *Reynoldsia* → *Polyscias* documented in YAML's uncertainty block. |
| Family | pass | POWO | Araliaceae; APG IV consistent. |
| Common names | pass | NTBG, Bishop Museum ethnobotany, Wikipedia | ʻohe makai / ʻohe kukuluāeʻo (stilts). Guide gives ʻohe makai as primary — appropriate. Optional enhancement: add ʻohe kukuluāeʻo as a second Hawaiian name (referencing the historical stilt-game use). Not required. |
| Biogeographic status | pass | NTBG, USFWS species profile | Endemic; no dispute. |
| Conservation status | pass | USFWS species profile | Correctly `null` — not federally listed (though rare and declining). |
| Coastal-zone occurrence | pass | NTBG, Wood 2012 | Dry sea-cliff bases + rocky slopes above strand on western/leeward sector matches. |
| Cultural significance | **needs-work (soft)** | Rock 1913 [B:1] (YAML anchor), Bishop Museum ethnobotany | YAML claim: "wood was used historically for tapa beaters, canoe parts, and other implements per Rock (1913)." Bishop Museum ethnobotany record confirms wood was used for *kukuluāeʻo* (walking stilts) and medicinal use of fruit for infants (pāʻaoʻao and ʻea). I could NOT independently confirm the tapa-beater claim from Rock's actual text without primary-text access (Rock is not full-text online); the wood is soft and light per multiple sources, which is *inconsistent* with a tapa-beater (which needs dense hardwood — *Kauila* or *ʻūlei* are the canonical tapa-beater woods). **Deferred:** `_deferred/ohe-makai-rock-1913-tapa-beater-verify` — cycle 5 should either open Rock 1913 directly and confirm the tapa-beater sentence, or rephrase to "canoe parts and stilts (kukuluāeʻo) per Rock 1913; Bishop Museum ethnobotany" and drop the tapa-beater claim as likely misattributed. |
| Hazards | pass | n/a | Correctly `null`. |
| ID clinchers accuracy | pass | NTBG | Swollen juvenile water-storing trunk + pinnately compound leaves at branch tips + large yellowish panicle + dry-season deciduous = diagnostic. |
| Look-alikes accuracy | pass | NTBG | "No close coastal look-alike" is honest and correct. |
| Numbered citations | pass (with the tapa-beater caveat above) | 1, 2, 3, B:1, B:3 all reachable | Lowry & Plunkett [B:3] correctly anchored to the nomenclatural note; Rock [B:1] flagged for verification of the tapa-beater claim. |

---

### 1.9 `sesbania-tomentosa` (ʻōhai) — *Sesbania tomentosa* Hook. & Arn.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO, USFWS 1994 [7], USFWS 2021 5YR [B:15 new] | Confirmed. |
| Family | pass | POWO | Fabaceae. |
| Common names | pass | NTBG, USFWS | ʻōhai / Hawaiʻi riverhemp confirmed. |
| Biogeographic status | pass | NTBG, Wagner | Endemic; no dispute. |
| Conservation status | pass | USFWS ECOS 1994 rule [7], USFWS 2021 5YR [B:15 new] | YAML says "US Endangered (USFWS 1994)". Still current; 2021 5YR retains endangered listing. YAML template does not include the 5YR date but is not incorrect — pilot recommendation to write `"US <status> (USFWS <year listing>; 5-Year Review <year>); IUCN <cat> (<year>)"` template style is a **soft deferred enhancement**: `_deferred/sesbania-conservation-status-5yr-refresh` — cycle 5 should reformat to include 5YR 2021 and IUCN status (species is not on IUCN Red List separately from USFWS listing per my search — worth confirming). **Reference [B:15] pre-landed in branch-b.md for this refresh.** |
| Coastal-zone occurrence | **needs-work** | USFWS 2021 5YR [B:15] | YAML's uncertainty block says "Kauaʻi-specific present-day wild populations are thinly documented in the literature accessible for this cycle." The 2021 5YR is now accessible and does report extant Kauaʻi wild populations (part of the ~700-plant main-Hawaiian-Islands total). The uncertainty-block hedge is stronger than the current evidence warrants. **Deferred:** `_deferred/sesbania-uncertainty-block-refresh-with-2021-5yr` — cycle 5 should rewrite the uncertainty block to reflect the 2021 5YR data (Kauaʻi wild populations extant but small and site-specific; visitors should still photograph-and-report rather than treat sightings as confirmed records). Kept as deferred rather than inline because it changes claim substance and needs the [B:15] anchor stitched into the YAML `citations:` array in a coordinated way. |
| Cultural significance | pass | Krauss 1993 [10], Abbott 1992 [11 via context] | Lei-making tradition + mele association. Guide's "sacred associations vary by place and lineage — Hawaiian cultural practitioners are the appropriate keepers of that knowledge" framing is the correct-shape restraint (the pilot noted this shape as the right pattern). |
| Hazards | pass | USFWS 1994 [7] | Regulatory-warning framing ("do not disturb, collect, or trample") is exactly the right hazard reframe for a federally-listed species. |
| ID clinchers accuracy | pass | NTBG, Native Plants of Hawaiʻi | Silvery-hairy whole-plant + pinnately compound many-leaflet + pea-family raceme (red/orange/salmon/yellow) + slender legume pod = diagnostic. |
| Look-alikes accuracy | pass | Wagner | *S. grandiflora* (much larger tree, cultivated) + introduced Fabaceae shrubs (not silvery-hairy) — good contrasts. |
| Numbered citations | pass | 1, 2, 3, 5, 10, B:7 all reachable | USFWS 1994 [7] and [B:7] anchor the endangered listing; [B:15] pre-landed for the 5YR refresh. |
| **Cross-listing regression** | **pass** | site/index.html grep + build_site.py line 390 | `is_federal_listed()` still fires on `"US Endangered (USFWS 1994)"` (matches lowercased "us endangered"). `sesbania-tomentosa` correctly renders in NOTABLE tier main grid AND in the "Also federally listed (cross-listed from other tiers)" section on the RARE-tier index. No regression. |

---

### 1.10 `naio` — see §1.1 above (canary).

### 1.11 `ki` (kī) — *Cordyline fruticosa* (L.) A.Chev.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO, WFO | Confirmed. *C. terminalis* Kunth is a nom. illeg. superfl. synonym; YAML's taxonomic_notes covers this correctly. |
| Family | pass | POWO | Asparagaceae under APG IV. YAML's taxonomic_notes covers older Laxmanniaceae/Agavaceae placements. |
| Common names | pass | NTBG, Krauss | Kī / ti / ti plant / cabbage palm. |
| Biogeographic status | pass | NTBG, Krauss | Polynesian introduction; canoe plant. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | Wood 2012, NTBG | Valley bottoms and stream margins at Nā Pali valley mouths; the "signals a former Hawaiian dwelling or garden site as strongly as any single plant species" framing matches archaeological consensus. |
| Cultural significance | pass | Krauss 1993 [10], Abbott 1992 [11 via context], Handy & Handy 1972 [B:9 via context] | Leaves for wrapping food (laulau, kūlolo), hula skirts (pāʻū), sandals, thatch, ceremonial protection; roots fermented into ʻōkolehao after Western contact. All in Krauss/Abbott/Handy. Note that the guide correctly attributes ʻōkolehao to *post-contact* fermentation (this is the correct historical placement — distillation technology arrived with Westerners); a common tertiary-source error is to attribute this to pre-contact tradition. |
| Hazards | pass | n/a | Correctly `null`. |
| ID clinchers accuracy | pass | NTBG | Single unbranched stem topped by lanceolate leaf rosette + ring-scarred stem + drooping panicle / red berries = diagnostic. |
| Look-alikes accuracy | pass | NTBG | Dracaena (ornamental with different fruit) + young Pandanus tectorius (spiny strap leaves + prop roots) — the right two contrasts. |
| Numbered citations | pass | 1, 2, B:10, B:11, B:13 all reachable | Krauss + Abbott + NTBG anchor cultural claims; no drift. |

---

### 1.12 `noni` — *Morinda citrifolia* L.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO, CTAHR | Confirmed. |
| Family | pass | POWO | Rubiaceae. |
| Common names | pass | NTBG, CTAHR | Noni / Indian mulberry / cheese fruit. |
| Biogeographic status | pass | NTBG, Handy & Handy 1972 [B:9] | Polynesian introduction; canoe plant. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | NTBG, Wood 2012 | Persistent + naturalizing on valley mouths and back-beach strand throughout the coast. |
| Cultural significance | pass (post-fix) | Handy & Handy 1972 [B:9], CTAHR noni profile, Krauss 1993 [10 via context] | **Inline fix applied**: tightened dye claim from "dye from bark and root (yellow to red-brown)" to "dye for kapa cloth (red pigment from the bark, yellow pigment from the root)" per CTAHR noni profile and Bishop Museum ethnobotany, which specifically document bark=red and root=yellow. Handy & Handy 1972 records noni as a well-established Hawaiian ethnobotanical plant with the same red-bark/yellow-root split. |
| Hazards | pass | NTBG | Non-toxic; smell attracts flies; fallen fruit slippery underfoot — correct. |
| ID clinchers accuracy | pass | NTBG | Knobby-warty compound fruit-head + large opposite arcuate-veined glossy leaves + tubular flowers projecting from the fruit-head + "aged-cheese" smell = unambiguously diagnostic. |
| Look-alikes accuracy | pass | NTBG | "No Rubiaceae on the coast produces the knobby compound fruit" — accurate. |
| Numbered citations | pass | 1, 2, B:9, B:10, B:13 all reachable | Handy & Handy [B:9] correctly anchors the ethnobotanical claim; NTBG [B:13] for description. |

---

### 1.13 `kalo` — *Colocasia esculenta* (L.) Schott

*Highest-scrutiny species; cultural claims audited against Krauss 1993 [10], Handy & Handy 1972 [B:9], and Kamakau 1976 [B:12].*

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO, WFO | Confirmed. |
| Family | pass | POWO | Araceae; APG IV consistent. |
| Common names | pass | NTBG, Handy & Handy 1972 [B:9] | Kalo / taro. |
| Biogeographic status | pass | Wagner, Handy & Handy 1972 [B:9] | Polynesian introduction. YAML's taxonomic_notes correctly identifies the fringe pre-Polynesian-drift position as such and does not adopt it. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | Wood 2012, Kirch & Kahn 2007, Handy & Handy 1972 [B:9], Kamakau 1976 [B:12] | Kalalau loʻi terraces are the flagship archaeological example of the wet-cultivation complex; extensive throughout every wet Nā Pali valley pre-depopulation matches Handy & Handy's mapping. Contemporary Kalalau loʻi restoration is well documented in Hawaiian community-organization literature. |
| Cultural significance — **Hāloa framing cross-reference vs Krauss/Handy/Kirch** | **pass** | Handy & Handy 1972 [B:9] (canonical Hāloa source), Krauss 1993 [10 via context], Kumulipo | **Highest-priority audit item this branch.** YAML's Hāloa sidebar reads: *"In Hawaiian cosmology recorded in the Kumulipo and in Handy & Handy 1972 [B:9], kalo is genealogically kin to the Hawaiian people. Hāloa, the stillborn first child of Wākea (Sky Father) and Hoʻohōkūkalani, is buried and grows into the first kalo plant; the second child (also named Hāloa) is the ancestor of the Hawaiian people."* Handy & Handy 1972 pp. 74–75 is the canonical modern record of this genealogy; the Kumulipo is the primary chant source. Two names (Wākea, Hoʻohōkūkalani) match Handy & Handy exactly. The "stillborn first child" → kalo → "second child named Hāloa" → Hawaiian people structure matches Handy & Handy's telling. No modern-attribution drift. **Passes cultural cross-reference.** |
| Cultural significance — **cultivar-diversity claim** | **pass** | Handy & Handy 1972 [B:9], KSBE "How to Harvest and Replant Kalo" (source citation of Handy) | YAML says "Hawaiian cultivation traditions describe more than 300 named pre-contact varieties of kalo." Handy & Handy 1972 states "hundreds of varieties adapted to planting in every type of soil and on every type of terrain"; the "more than 300 varieties" figure is a widely-cited derivative of Handy's account (KSBE Hawaiian-cultural curriculum uses "more than 300 varieties of taro" and cites Handy). Roughly 87 varieties are recognized in living cultivation today. YAML's "more than 300" figure is defensible with Handy & Handy 1972 as the anchor. **Passes cultivar-diversity audit.** |
| Cultural significance — general framing | pass | Handy & Handy 1972 [B:9], Krauss 1993 [10], Kirch & Kahn 2007 [B:11 via context] | Restoration framing ("ongoing cultural stewardship effort … working cultural site, not a historical artifact") is exactly the correct-shape restraint. No harvest / preparation / poi-making instruction leaks. Guide's "That knowledge lives in Hawaiian hands" closing is appropriate. |
| Hazards | pass | NTBG, CTAHR | Calcium oxalate raw irritant warning is standard and correctly worded. |
| ID clinchers accuracy | pass | NTBG | Peltate leaf attachment (single most diagnostic) + water-repellent surface + horizontal blade position + wet-ground habitat = diagnostic. |
| Look-alikes accuracy | pass | NTBG | ʻape (larger + upright + cordate-not-peltate + toxic raw), *Xanthosoma* (cordate attachment), other ornamental Colocasia — correct three-way contrast. The toxicity distinction on ʻape is critical and correctly foregrounded. |
| Numbered citations | pass | 1, 2, B:9, B:10, B:11, B:12, B:13 all reachable | Handy & Handy [B:9] is correctly the primary Hāloa anchor; Krauss [B:10], Abbott [B:11], Kamakau [B:12], NTBG [B:13] all support secondary claims. |

---

### 1.14 `ko` (kō) — *Saccharum officinarum* L.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO | Confirmed. |
| Family | pass | POWO | Poaceae. |
| Common names | pass | NTBG, Krauss | Kō / sugarcane. |
| Biogeographic status | pass | Handy & Handy 1972 [B:9], Wagner | Polynesian introduction. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | Wood 2012, Handy & Handy 1972 [B:9] | Persistent remnants of pre-depopulation cultivation at Kalalau, Nuʻalolo Kai, Miloliʻi valley bottoms — matches Handy's cultivation-record mapping. |
| Cultural significance — **cultivar-diversity claim** | **pass** | Handy & Handy 1972 [B:9], Krauss 1993 [10], Lincoln 2020 "Kō" (UH Press) | YAML says "Handy & Handy 1972 and Krauss 1993 record many pre-contact Hawaiian kō cultivars, named by stem colour, sweetness, joint pattern, and specific use." Handy & Handy 1972 records dozens of named varieties; Krauss 1993 has a canoe-plants chapter listing many; Lincoln 2020 catalogues more than 100 native and heirloom kō varieties. YAML uses hedged "many" — safer than a specific number and defensible against the primary ethnobotanical record. **Passes cultivar-diversity audit.** (No specific numeric claim to audit; the pilot brief's "40 named pre-contact cultivars" claim is not authored in the current YAML — the hedged "many" phrasing avoids the trap.) |
| Cultural significance — general framing | pass | Handy & Handy 1972 [B:9], Krauss 1993 [10] | Integrated with kalo loʻi complex; grown in dedicated patches and on paths; cultivar-conservation efforts appropriately credited to Hawaiian practitioners. No preparation instruction leaks. |
| Hazards | pass | Krauss 1993 | Silica leaf-edge cuts are the standard warning; "these are heritage plants at wahi pana sites, do not attempt to break or taste stems" is the right restraint. |
| ID clinchers accuracy | pass | NTBG | Very tall stout jointed cane (2–5 m grass) + long broad arching pale-midrib leaves + silvery plumose panicle = diagnostic against Miscanthus/Pennisetum/bamboo. |
| Look-alikes accuracy | pass | Wagner, CTAHR | Miscanthus (thinner + not sweet + shorter) + napier grass (thinner + bottlebrush panicle) + bamboo (hollow woody culms + paired branches) — right three contrasts. |
| Numbered citations | pass | 1, 2, B:9, B:10, B:11 all reachable | Handy [B:9] + Krauss [B:10] + Abbott [B:11] anchor cultural claims. |

---

### 1.15 `aalii` (ʻaʻaliʻi) — *Dodonaea viscosa* Jacq.

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO | Confirmed. |
| Family | pass | POWO | Sapindaceae. |
| Common names | pass | NTBG, Krauss | ʻAʻaliʻi / hopbush / hopseed bush. |
| Biogeographic status | pass | Wagner, NTBG | Indigenous; polymorphic pantropical species. YAML's taxonomic_notes correctly captures the Wagner sensu-lato treatment. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | Wood 2012, NTBG | Dry Nā Pali–Kona coastal cliffs + valley mouths + thin cliff-face soils — matches. |
| Cultural significance | pass | Krauss 1993 [B:10], Rock 1913 [B:14], Bishop Museum ethnobotany | Fruit clusters + flowers used in lei (holds colour well); wood used for tool handles, digging-stick shafts, house posts, weapons; kapa dye from fruit capsules. All specifically confirmed in Bishop Museum ethnobotany record and Krauss 1993. YAML's framing (name practices, credit contemporary practitioners) holds. |
| Hazards | pass | n/a | Correctly `null`. |
| ID clinchers accuracy | pass | NTBG, Wagner | Papery 3-winged fruit capsule in red/pink/yellow clustered at shoot tips + sticky-resinous young leaves + dry wind-exposed position + "colour on the plant is in the fruit not the flower" = unmistakable. |
| Look-alikes accuracy | pass | NTBG | Introduced legumes (pinnate + hanging pods vs simple leaves + radial 3-winged capsules) + purple-leaved cultivars (garden only, not wild coastal). |
| Numbered citations | pass | 1, 2, 3, B:10, B:13, B:14 all reachable | Krauss [B:10] + Rock [B:14] + NTBG [B:13] all anchor to appropriate claims. |

---

### 1.16 `mamaki` (māmaki) — *Pipturus albidus* (Hook. & Arn.) A.Gray

| Category | Verdict | Source | Note |
|---|---|---|---|
| Sci. name + authority | pass | POWO | Confirmed. |
| Family | pass | POWO | Urticaceae. |
| Common names | pass | NTBG, Krauss | Māmaki / waimea pipturus / mamaki. (Note: Plant Pono and MDPI 2023 review use "māmaki" as the standard Hawaiian orthography; guide uses it correctly.) |
| Biogeographic status | pass | NTBG, Wagner | Endemic (P. albidus + several congeners are Hawaiian endemics). YAML's taxonomic_notes on species-level treatment is appropriate for field-guide scope. |
| Conservation status | pass | n/a | Correctly `null`. |
| Coastal-zone occurrence | pass | Wood 2012, NTBG | Moist stream drainages reaching the coast; just above the beach where streams reach — matches. |
| Cultural significance | pass | Krauss 1993 [B:10], MDPI 2023 comprehensive review, Bishop Museum ethnobotany | Bark fibre for tapa (secondary to wauke — this is the canonical framing); leaves brewed as māmaki tea (traditional + contemporary commercial industry); fruit occasionally eaten. All confirmed in the peer-reviewed 2023 ethnomedicinal review (Plants 12(16):2924) and Bishop Museum record. YAML wording ("supplementary material to wauke") is the exact framing used across primary ethnobotany. Kamehameha butterfly (*Vanessa tameamea*) host-plant note is correct and useful field-ecology detail. |
| Hazards | pass | (Urticaceae stinging-hair caveat) | The "no stinging hairs" note is critically important — Urticaceae elsewhere in the world sting, and a hiker's prior conditioning may lead them to expect stings. Foregrounding "if your palm brushed a leaf and there was no sting, you have not ruled it out" is excellent field-guide teaching. |
| ID clinchers accuracy | pass | NTBG | Three-veined leaf base + pale-whitish underside + small white fleshy compound fruit + no stinging = diagnostic. |
| Look-alikes accuracy | pass | NTBG, Wagner | Introduced Boehmeria (pinnate venation) + olonā (single midrib + narrower leaves) + Cecropia (much larger + palmately lobed) — good three-way contrast. Olonā note appropriately flags a native Urticaceae not otherwise in the guide. |
| Numbered citations | pass | 1, 2, B:10, B:11, B:13, B:14 all reachable | Krauss [B:10] + Abbott [B:11] + NTBG [B:13] + Rock [B:14] all support tea-and-bark-fibre claims. |

---

## 2. Matrix totals

**165 cells graded.**

| Verdict | Count | Percent |
|---|---|---|
| pass | 158 | 95.8% |
| needs-work | 7 | 4.2% |
| fail | 0 | 0.0% |

**Sufficiency criterion (≥90% pass): met with margin (95.8% vs 90.0% floor).**

`needs-work` cells:
1. **milo — biogeographic status** — soft uncertainty-block missing (mainstream indigenous but some sources hedge). Deferred `_deferred/milo-indigenous-hedge-block`.
2. **wiliwili — conservation status** — currency note on second biocontrol (*Aprostocetus nitens*). Deferred `_deferred/wiliwili-aprostocetus-second-biocontrol-note`.
3. **ʻohe makai — cultural significance** — Rock 1913 tapa-beater claim unverified; wood-density evidence weakly against. Deferred `_deferred/ohe-makai-rock-1913-tapa-beater-verify`.
4. **naio — family** — Wagner→APG shift not previously flagged. **Fixed inline** (added `taxonomic_notes:` block). Grade advanced from needs-work → pass in the table above.
5. **noni — cultural significance** — dye color specificity ("yellow to red-brown" was imprecise). **Fixed inline** (rephrased to "red pigment from bark, yellow pigment from root"). Grade advanced from needs-work → pass.
6. **sesbania — conservation status** — 5YR 2021 not yet cited from YAML. Deferred `_deferred/sesbania-conservation-status-5yr-refresh` (reference [B:15] pre-landed in branch-b.md).
7. **sesbania — coastal-zone occurrence** — uncertainty block hedge stronger than current 2021 5YR warrants. Deferred `_deferred/sesbania-uncertainty-block-refresh-with-2021-5yr`.

**Inline fixes applied this cycle (2):** naio family taxonomic_notes; noni dye color specificity.

**Deferred to cycle 5 (5):** listed above; all logged as `_deferred/*` ledger events.

---

## 3. Author-position audit findings

Every contested-status uncertainty block in the NOTABLE tier was audited against the source-author's actual position:

| Species | Cited author | Claim in YAML | Author-position verdict |
|---|---|---|---|
| niu | Harries 1978 [B:2] | "coconut's buoyant, salt-tolerant seed and documented long-distance ocean drift ecology make pre-Polynesian presence in the Pacific plausible" | **PASS** — Harries argues natural drift-dispersal capability of the genus across the Pacific (niu kafa wild-ancestral morphology; buoyant thick-husked ridged fruit). YAML's careful "in the Pacific plausible" hedge does not overreach into Hawaiʻi-specific claims Harries doesn't make. Citation faithful. |
| hau | Wagner et al. 1999 [1] | "current standard treatment of hau as indigenous to Hawaiʻi" | **PASS** — Wagner does treat hau as indigenous. |
| hau | Herbst 1988 [B:5] | "argument for treating *Hibiscus tiliaceus* as indigenous" | **PASS** — Herbst 1988 makes the pantropical / buoyant-seed / strand-plant biogeographic argument for indigenous treatment. |
| kalo | Handy & Handy 1972 [B:9] | Hāloa genealogy + 300+ cultivars | **PASS** — Handy & Handy pp. 74–75 canonical Hāloa telling; "hundreds of varieties" phrasing matches the "more than 300" figure derived across secondary ethnobotanical curriculum. |
| naio | (no author-position claim; taxonomic_notes only) | Wagner Myoporaceae vs APG Scrophulariaceae | **PASS** — both treatments accurately attributed. |
| ʻohe makai | Lowry & Plunkett 2010 [B:3] | *Reynoldsia* → *Polyscias* nomenclatural transfer | **PASS** — Lowry & Plunkett 2010 recircumscribed *Polyscias* to include *Reynoldsia*. |
| ʻohe makai | Rock 1913 [B:1] | Wood used for "tapa beaters, canoe parts, and other implements" | **NEEDS-WORK** — Rock discusses ʻohe makai but the specific tapa-beater claim is inconsistent with the species' soft/light wood (tapa beaters need hardwood); could not confirm the sentence in Rock 1913 without primary-text access. Deferred `_deferred/ohe-makai-rock-1913-tapa-beater-verify`. |
| ʻōhai | USFWS 1994 [7] | "US Endangered (USFWS 1994)" | **PASS** — original listing rule as cited. |

**Author-position audit result: 7 PASS / 1 NEEDS-WORK.** No blocking failure. The single needs-work is Rock-primary-text-access-limited, not an author-mis-attribution — deferred for cycle 5 verification against the actual Rock 1913 pages.

---

## 4. Cultural-claim primary-source audit

Cycle-3 pilot flagged "tertiary web citations survive" as a failure mode. Audit result for NOTABLE tier:

- **kalo, kō, kī, māmaki, ʻaʻaliʻi, noni, kukui** — Cultural claims trace to Krauss 1993 [10 / B:10], Handy & Handy 1972 [B:9], Abbott 1992 [11 / B:11], Rock 1913 [B:1 / B:14], or Kamakau 1976 [B:12]. **No tertiary web-only citations found.** All primary-ethnobotany-anchored.
- **milo, kou, wiliwili, niu, hau, ʻōhai, naio, ʻohe makai** — Cultural claims trace to the same primary ethnobotany set plus Bishop Museum ethnobotany database (peer-vetted institutional resource, acceptable). No tertiary web citations.

Kalo's Hāloa framing was the highest-scrutiny item: **cross-referenced against Handy & Handy 1972 pp. 74–75 (canonical modern source of the tradition) and the Kumulipo (primary chant source). Names (Wākea, Hoʻohōkūkalani, Hāloa) and structure (stillborn first child → first kalo plant → second child named Hāloa is the human ancestor) match Handy & Handy exactly. Passes cultural cross-reference against Kirch's ethno-archaeological framing (Kirch 1985; Kirch & Kahn 2007) as well.**

---

## 5. CC-BY-2.0 opportunistic re-image sweep

Opportunistic sweep documented but not executed this cycle (image-fetch pipeline requires a dedicated pass; deferred to keep cycle 4 within scope). Prime NOTABLE-tier candidates for cycle 5 image expansion under the extended CC-BY-2.0 allow-list (`scripts/_licenses.py`):

| Species | Current photo count | Opportunity | Preferred CC-BY-2.0 target |
|---|---|---|---|
| niu | 3 | already at bar; a David Eickhoff Flickr living-plant flower cluster would strengthen | Eickhoff (Flickr) — coconut flower cluster |
| hau | 4 | already strong; morning-yellow vs afternoon-red comparison photo pair from Eickhoff would clinch the daily-colour-change teaching visual | Eickhoff — hau flower yellow morning / red evening |
| kalo | 2 | thin; a Kalalau loʻi terrace context photo would immensely strengthen the site-specific claim | Kalalau NPS / DLNR / Eickhoff |
| noni | 3 | already at bar; a fruit close-up showing knobby surface + tubular flowers projecting would add pedagogical value | Eickhoff — noni fruit close |
| ʻaʻaliʻi | **1 photo only** (plus 2 SVG diagrams) | highest priority NOTABLE-tier re-image candidate; the winged-capsule colour variation is a defining feature and warrants a red-capsule + yellow-capsule photo pair | Eickhoff or Starr — ʻaʻaliʻi fruit capsule reds and yellows |
| māmaki | 2 | at bar; a 3-veined-base leaf close-up would strengthen the ID clincher | Eickhoff — Pipturus leaf close |

**Recommendation:** cycle 5 image sweep should prioritise **ʻaʻaliʻi (1 → 3+ photos)** as the only NOTABLE-tier species currently at the bare 2-visual minimum with just 1 photo. All others are at 2+ photos already.

`_deferred/notable-cc-by-2-image-sweep` logged with this candidate list.

---

## 6. Family-placement (APG-vs-Wagner) audit

Systematic check across all 15 species for Wagner/APG divergence:

| Species | Wagner | APG IV | YAML uses | Verdict |
|---|---|---|---|---|
| milo | Malvaceae | Malvaceae | Malvaceae | agree |
| kou | Boraginaceae | Boraginaceae (Cordia subfam. Cordioideae) | Boraginaceae | agree |
| kukui | Euphorbiaceae | Euphorbiaceae | Euphorbiaceae | agree |
| wiliwili | Fabaceae | Fabaceae | Fabaceae | agree |
| niu | Arecaceae | Arecaceae | Arecaceae | agree |
| hau | Malvaceae | Malvaceae | Malvaceae | agree |
| ʻohe makai | Araliaceae | Araliaceae | Araliaceae | agree |
| ʻōhai | Fabaceae | Fabaceae | Fabaceae | agree |
| naio | **Myoporaceae** | **Scrophulariaceae s.l.** | Scrophulariaceae + new taxonomic_notes | **shift documented (fixed this cycle)** |
| kī | Agavaceae / Laxmanniaceae | Asparagaceae | Asparagaceae + existing taxonomic_notes | shift documented |
| noni | Rubiaceae | Rubiaceae | Rubiaceae | agree |
| kalo | Araceae | Araceae | Araceae | agree |
| kō | Poaceae | Poaceae | Poaceae | agree |
| ʻaʻaliʻi | Sapindaceae | Sapindaceae | Sapindaceae | agree |
| māmaki | Urticaceae | Urticaceae | Urticaceae | agree |

**Two Wagner/APG shifts in the NOTABLE tier: naio (documented this cycle) and kī (documented in cycle 3). Both now carry taxonomic_notes.** No shifts left silent.

---

## 7. Sesbania cross-listing regression check

`is_federal_listed()` (`scripts/build_site.py` line 390) matches on lowercased `"us endangered"` in the `conservation_status` field. `sesbania-tomentosa.yaml` field: `"US Endangered (USFWS 1994)"` — matches.

`grep -n "sesbania" site/index.html` shows the species rendered 4 times: NOTABLE tier grid, cross-listed section on the RARE-tier index, and both habitat-zone groupings (strand, dune). Cross-lister continues to fire correctly. **Regression check: PASS. No change to `is_federal_listed()` needed.**

---

## 8. Discrepancies deferred to cycle 5

Logged as `_deferred/*` ledger events with milestone id, narrative, and specific edit target:

1. `_deferred/milo-indigenous-hedge-block` — Add an uncertainty block on milo modeled on hau's, noting the mainstream-indigenous treatment vs. minority Polynesian-introduction reading. Low-priority; mainstream is defensible without the block.
2. `_deferred/wiliwili-aprostocetus-second-biocontrol-note` — Add a one-sentence currency note to the ecology field: "A second biocontrol agent (*Aprostocetus nitens*) is under study to address the seed-pod / inflorescence damage that *E. erythrinae* does not fully control." Small enhancement.
3. `_deferred/ohe-makai-rock-1913-tapa-beater-verify` — Open Rock 1913 primary text; either confirm the tapa-beater sentence and retain, or replace with "canoe parts and stilts (kukuluāeʻo) per Rock 1913 and Bishop Museum ethnobotany." Author-position audit follow-through.
4. `_deferred/sesbania-conservation-status-5yr-refresh` — Reformat conservation_status to pilot template: `"US Endangered (USFWS 1994; 5-Year Review 2021)"`. Add `"B:15"` to `citations:` array. Reference [B:15] pre-landed in branch-b.md this cycle.
5. `_deferred/sesbania-uncertainty-block-refresh-with-2021-5yr` — Rewrite the uncertainty block to reflect the 2021 5YR: Kauaʻi wild populations extant (part of the ~700-plant main-Hawaiian-Islands total) but sparse; visitors should still photograph-and-report rather than treat sightings as confirmed records. Reference [B:15] anchor.
6. `_deferred/notable-cc-by-2-image-sweep` — Opportunistic CC-BY-2.0 sweep prioritising ʻaʻaliʻi (1→3+ photos), plus optional expansions for kalo (Kalalau loʻi context), niu, hau, noni, māmaki per §5 target list.

---

## 9. What this branch did NOT touch (cross-branch discipline held)

Per shard discipline, Branch B modified only Branch B's own files:
- `data/species/naio.yaml` (Branch B species; small inline fix, new taxonomic_notes)
- `data/species/noni.yaml` (Branch B species; small inline fix, dye color tightening)
- `data/references/branch-b.md` (Branch B references; added [B:15] USFWS 2021 5YR + [B:16] Makauwahi Cave)
- New: `reports/verification/cycle_04_notable.md` (this file)
- New: `reports/cycles/cycle_04_branch_b_notable_verify.md` (merge report)

No touches on Branch A species (`hala`, `naupaka-kahakai`, `pōhuehue`, `ʻakiʻaki`, `sida-fallax`, etc.), Branch C species (`alula`, `panicum-niihauense`, `hibiscus-waimeae-hannerae`, `kokia-kauaiensis`, etc.), shared build tooling (`scripts/build_site.py`, `_licenses.py`), test fixtures, or the persistent-yellow `promise_check` state. No cycle-3 deferred items owned by other branches were touched.

Cross-branch findings surfaced (not fixed by Branch B):
- **kou paleobotanical strengthening opportunity**: Burney et al. Makauwahi Cave (Kauaʻi) subfossil evidence pre-dating human arrival supports kou's indigenous status. Reference [B:16] pre-landed in branch-b.md for potential future wiring into `data/species/kou.yaml` (Branch B species — Branch B could integrate in cycle 5 if desired). Not fixed inline because the wiring involves an uncertainty block scoped decision that a researcher should choose framing for.

---

*End of Cycle 4 Branch B NOTABLE-tier verification report.*
