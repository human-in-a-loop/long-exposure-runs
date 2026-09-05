---
title: "Kauai Coastal Field Guide — cycles 1–3"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Kauai Coastal Field Guide — cycles 1–3

## Abstract

Three cycles of a six-cycle run have produced a working, offline HTML field guide to the plants of Kauai's unpopulated coast. The site now covers **30 species** (12 common, 9 notable, 9 rare & exotic) toward a final target of ≥45, carries **72 license-verified photographs** and 18 hand-authored SVG identification diagrams, and passes a full suite of mechanical validators for schema completeness, offline safety, link integrity, and image licensing. Every profile carries at least two visuals and a structured "How to identify" block. All photographs come from the openly licensed pool the directive requires: 67 under CC-BY 3.0 (Forest & Kim Starr's Hawaii Plant Image Archive on Wikimedia Commons), 3 under CC0 (Smithsonian NMNH herbarium sheets), and 2 under CC-BY-SA 3.0. The site is shippable at the cycle-3 boundary; remaining work is species breadth (8 more common, 6 more notable, 1 more rare & exotic minimum) and a deep verification pass against primary flora.

## 1. Introduction

The directive asks for a picture-driven, offline field guide to the plants of Kauai's roadless coasts — the Nā Pali cliffs and valleys (Kalalau, Honopū, Nuʻalolo Kai, Miloliʻi, Awaʻawapuhi), Māhāʻulepū, and the Nā Pali–Kona strand. Coverage is organized into three tiers: **common** plants a hiker or boater actually meets on beaches, dunes, cliffs, and valley mouths; **notable** natives (endemic and indigenous) and Polynesian canoe plants; and **rare & exotic**, mixing rare cliff endemics (including federally listed species) with invasives that now dominate or threaten these habitats.

The site must open from `file://` with no external dependencies — no CDNs, no hotlinked images, no web fonts. Every image must be verifiably in the public domain, CC0, CC-BY, or CC-BY-SA; where no such photograph exists for a species, hand-authored SVG diagrams substitute so that the two-visual minimum still holds. Every species profile carries a structured "How to identify" block, biogeographic status, habitat placement on the unpopulated coast, cultural framing, hazards, and numbered citations tied to `REFERENCES.md`.

This report covers the first three cycles: cycle 1 laid the end-to-end pipeline and a 10-species vertical slice; cycle 2 fanned out three parallel workers to expand each tier; cycle 3 performed a post-merge integration and closed the residual reconciliation debt.

## 2. Approach

### 2.1 Data-driven pipeline

The site is not hand-written HTML. Every species page and index is rendered by `scripts/build_site.py` from four inputs:

- `data/species/<slug>.yaml` — one YAML file per species, holding scientific and common names, family and authority, biogeographic and conservation status, habitat and coastal zone, the "How to identify" block, hazards, cultural notes, an image list, look-alikes, and citation numbers.
- `data/images.json` (plus sharded `data/images.branch-*.json` manifests, introduced in cycle 2) — the image manifest, one entry per photograph, carrying the local file path, source page URL, photographer, license, and caption.
- `data/glossary.yaml` — botanical and Hawaiian terms.
- `REFERENCES.md` (plus sharded `data/references/branch-*.md`) — the numbered bibliography.

Every rendered page is a static HTML file under `site/`, and every asset (photos, diagrams, CSS, the vanilla-JS filter script) is a relative-local file under `site/assets/` or `site/`.

### 2.2 License-verify-closed image pipeline

Photographs enter the site through `scripts/fetch_images.py`, which refuses any image whose license is not in the locked allow-list: `{CC0, PD, CC-BY-3.0, CC-BY-4.0, CC-BY-SA-3.0, CC-BY-SA-4.0, USGov-PD}`. The downloader pulls Wikimedia Commons thumbnails at the 1280-pixel size permitted for bulk clients, downscales with Pillow to a 150–400 KB target, and writes an entry to `data/images.lock.json`. Discovery of candidate images is a separate hand-driven step (`scripts/discover_images.py`) so that curation stays in human hands and the manifest is never scraped blindly.

When no license-verifiable photograph can be found for a species, the pipeline falls back to SVG diagrams so that the two-visual minimum still holds. One species — *Schiedea apokremnos*, a Nā Pali sea-cliff endemic — travels the SVG-only path.

### 2.3 Validators

Five mechanical checks run every cycle:

- `check_coverage.py` — required-field schema enforcement, tier and zone enum enforcement, ≥2 visuals per species, ≥1 valid citation, and structural checks on the "How to identify" block (2–4 clinchers, non-empty look-alikes).
- `lint_site.py` — every rendered HTML file is parsed and any external URL in a resource-loading tag (`<img>`, `<script>`, `<link>`) is a failure. Provenance hyperlinks in `<a href>` to Wikimedia source pages are permitted because CC-BY attribution requires them and they trigger no page loads.
- `check_links.py` — every internal `href`/`src` resolves to a file or an in-page anchor.
- `check_offline.py` — a second-pass regex sweep over rendered HTML confirming safety under `file://`.
- Two test suites (`tests/test_validators.py`, `tests/test_build_merge.py`) exercise negative fixtures — a schema-violating species, an external-URL leak, a broken internal link, an empty look-alikes list, a duplicate image id across shards, a non-deterministic shard order, an unresolved citation token — and each validator is required to reject them.

### 2.4 Citation discipline

Every load-bearing botanical claim in a species YAML is tied to a numbered reference in `REFERENCES.md`. The primary sources are Wagner, Herbst & Sohmer's *Manual of the Flowering Plants of Hawaiʻi* (1999); the Smithsonian's online Flora of the Hawaiian Islands checklist; National Tropical Botanical Garden species profiles; USFWS listing rules; Bishop Museum records; the Starr Environmental image archive; Krauss's *Plants in Hawaiian Culture*; Little & Skolmen's *Common Forest Trees of Hawaii*; K. R. Wood's rare-plant rediscovery notes; Motooka et al. on Hawaiian weeds; and USDA PLANTS. Where sources disagree, the disagreement is recorded in an `uncertainty:` block on the species record and rendered as a callout on the species page rather than silently resolved.

## 3. What was built, cycle by cycle

### 3.1 Cycle 1 — pipeline and 10-species vertical slice

Cycle 1 stood up the whole pipeline described above and shipped a 10-species vertical slice spanning all three tiers:

- **Common** (4): *Scaevola taccada* (naupaka kahakai), *Ipomoea pes-caprae* (pōhuehue), *Sporobolus virginicus* (ʻakiʻaki), *Pandanus tectorius* (hala).
- **Notable** (3): *Thespesia populnea* (milo), *Cordia subcordata* (kou), *Aleurites moluccanus* (kukui).
- **Rare & exotic** (3): *Brighamia insignis* (ʻālula) — the emblematic Nā Pali cliff endemic; *Schinus terebinthifolia* (Christmas berry) — a dominant coastal invasive; *Lantana camara* (lantana) — another aggressive invasive.

The cycle produced 26 downloaded photographs (24 Starr-archive CC-BY 3.0, one CC0, one CC-BY-SA 3.0), a library of 16 hand-authored SVG diagrams (8 leaf shapes, 6 habit silhouettes, a *Scaevola* half-flower schematic, and a Nā Pali coastal-zone cross-section), a 25-term glossary, a safety-and-ethics page framed around *wahi pana* and Leave No Trace, a credits page listing every photograph's author and license, and a references section with 15 numbered sources. The tiered thumbnail index, the zone-grouped index, and a vanilla-JS text filter operating on DOM data-attributes all landed.

A rate-limit incident during image fetching led to a policy fix: the pipeline was switched from original Wikimedia file URLs to the 1280-pixel thumbnail endpoint that Wikimedia permits for bulk clients. Every downstream cycle has used this endpoint without incident.

At cycle close every validator ran green: 15 HTML files, no external asset URLs, 10 species passing required-field and visual checks, all internal links resolving, all three negative-fixture tests rejecting.

### 3.2 Cycle 2 — three-way fan-out

Cycle 2 fanned out three parallel workers, one per tier, coordinated by a sharded-manifest scheme so that they could land without stepping on one another. Each branch used its own image manifest (`data/images.branch-{a,b,c}.json`) and its own reference shard (`data/references/branch-{a,b,c}.md`) with per-branch citation tokens (`"A:n"`, `"B:n"`, `"C:n"`) that the build script rewrites to global reference numbers.

**Branch A — common tier expansion.** Landed the sharded-manifest infrastructure first, then added 8 common species: *Sida fallax* (ʻilima), *Heliotropium foertherianum* (hinahina kū kahakai), *Vitex rotundifolia* (pōhinahina), *Fimbristylis cymosa* (mauʻu ʻakiʻaki), *Jacquemontia ovalifolia* subsp. *sandwicensis* (pāʻū o Hiʻiaka, endemic), *Boerhavia repens* (alena), *Nama sandwicensis* (hinahina kahakai, endemic), and *Chamaesyce degeneri* (ʻakoko, endemic). Three of the eight are Kauai/Hawaii endemics. A new test suite (`tests/test_build_merge.py`) exercises the shard infrastructure with three negative fixtures — duplicate image id across shards, non-deterministic shard iteration order, and an unresolved citation token — all of which the build script must reject.

**Branch B — notable tier expansion.** Added 6 species: *Myoporum sandwicense* (naio), *Erythrina sandwicensis* (wiliwili, endemic), *Cocos nucifera* (niu, Polynesian introduction), *Hibiscus tiliaceus* (hau), *Polyscias sandwicensis* (ʻohe makai, endemic — with a note on the *Reynoldsia* → *Polyscias* nomenclatural transfer), and *Sesbania tomentosa* (ʻōhai, endemic and federally endangered). The `uncertainty:` block was exercised on niu (Polynesian introduction versus pre-Polynesian pantropical drift per Harries 1978) and hau (indigenous versus Polynesian introduction per Herbst 1988).

**Branch C — rare and invasive expansion.** Added 6 species: three coastal invasives — *Leucaena leucocephala* (koa haole), *Ricinus communis* (castor bean, with a lethal-toxin hazard callout), and *Furcraea foetida* (Mauritian hemp) — and three rare endemics — *Hibiscus waimeae* subsp. *hannerae* (koki'o ke'oke'o, federally endangered), *Panicum niihauense* (federally endangered), and *Schiedea apokremnos* (federally endangered, the Nā Pali sea-cliff schiedea). *Panicum niihauense* took the herbarium-sheet fallback because the best living-plant photographs on Commons are CC-BY 2.0, outside the locked allow-list; *Schiedea apokremnos* took the SVG-only fallback because no license-verifiable photograph could be found at all. Both fallback paths are documented in the species records under `image_search_notes:`.

Branch C also closed a cycle-1 audit finding: the Christmas-berry profile had carried "wilelaiki (occasional Hawaiianized name)" as a Hawaiian common name. Wagner and Krauss do not treat it as a traditional Hawaiian botanical name; the weed literature records it as a Hawaiianized transliteration reportedly of "Willie Rice". The term was moved out of the Hawaiian names list into a sourced `uncertainty:` callout.

### 3.3 Cycle 3 — post-merge integration

The three branches did not merge cleanly on their own. Cycle 3, a worker-only cycle, reconciled the divergences.

The largest was **shard-migration debt** in Branch C: 11 image manifest entries were still sitting in the base `data/images.json` and references [24]–[29] were still in the root `REFERENCES.md`, even though the sharded infrastructure Branch A landed was meant to hold them. Cycle 3 migrated the 11 image entries into `data/images.branch-c.json`, moved the six references into `data/references/branch-c.md`, and rewrote citation lists in the four affected species records (`panicum-niihauense`, `hibiscus-waimeae-hannerae`, `mauritian-hemp`, `schiedea-apokremnos`) to the `"C:n"` token form the sharded infrastructure expects. After migration, the build script resolves 23 citation tokens (up from 17), and successive builds are byte-identical.

Three other divergences were also closed:

- **CSS.** The `.hazards` block — used most visibly on the castor-bean lethal-toxin warning — was visually too light. Branch C had deferred sharpening it to avoid a parallel-branch stylesheet conflict. Cycle 3 widened the border, tightened the padding, and reddened the strong-tag color.
- **Milestone bookkeeping.** Cycle 2 emergent milestones (the sharded-manifest infrastructure itself, the hala indigenous-versus-Polynesian uncertainty block, the look-alikes-length tightening, the wilelaiki style leak, an SVG-only-fallback coverage-rule split, and cross-referenced status uncertainty for niu and hau) were absent from the plan of record and therefore surfaced as bookkeeping errors on every cross-check. Cycle 3 extended the plan of record's milestones table to document all seven, clearing the errors.
- **Orphan scripts.** Five one-shot audit-emit scripts left over from cycles 1 and 2 were archived under `stale/tools/`.

Cycle 3 also introduced a validator quirk that is worth naming honestly. Twenty schema errors on the earliest ledger events remain — they are pre-normalization events that cannot be rewritten without violating the append-only rule. A waiver file (`reports/promise_check_immutable_exceptions.json`) records the intent to exempt them, but the current cross-check tool only honors waivers on invalid-UUID errors, so the yellow state persists in the report even though it is documented and non-blocking.

## 4. Findings

### 4.1 Species coverage per tier

| Tier | Current | Target | Remaining |
|------|---------|--------|-----------|
| Common | 12 | ~20 | 8 |
| Notable | 9 | ~15 | 6 |
| Rare & exotic | 9 | ≥10 | 1 |
| **Total** | **30** | **≥45** | **15+** |

**Common tier (12):** naupaka kahakai, pōhuehue, ʻakiʻaki, hala, ʻilima, hinahina kū kahakai, pōhinahina, mauʻu ʻakiʻaki, pāʻū o Hiʻiaka, alena, hinahina kahakai, ʻakoko. Of these, four are Kauai/Hawaii endemics (pāʻū o Hiʻiaka, hinahina kahakai, ʻakoko, and — depending on treatment — hinahina kū kahakai).

**Notable tier (9):** milo, kou, kukui, naio, wiliwili, niu, hau, ʻohe makai, ʻōhai. Includes the two Polynesian canoe plants the directive singles out (kukui and niu), three Hawaii endemics (wiliwili, ʻohe makai, ʻōhai), and one federally endangered species (ʻōhai).

**Rare & exotic tier (9):** ʻālula, koki'o ke'oke'o (*Hibiscus waimeae* subsp. *hannerae*), *Panicum niihauense*, *Schiedea apokremnos*, Christmas berry, lantana, koa haole, castor bean, Mauritian hemp. Four rare Nā Pali endemics (all four federally listed) and five naturalized invasives that now dominate or threaten these habitats.

### 4.2 Visual coverage

- **72 photographs** across 30 species, all license-verified.
- **License mix:** 67 CC-BY 3.0 (Forest & Kim Starr, via Wikimedia Commons), 3 CC0 (Smithsonian NMNH herbarium sheets, used for *Panicum niihauense*), 2 CC-BY-SA 3.0 (one pōhuehue photograph, one Mauritian hemp photograph).
- **SVG diagrams:** 18 files under `site/assets/diagrams/`, reused across species. The library includes leaf-shape primitives, habit silhouettes, a *Scaevola* half-flower schematic, and a Nā Pali coastal-zone cross-section.
- **Visual-minimum compliance:** every profile carries at least two visuals. One species — *Schiedea apokremnos* — carries SVG diagrams only; every other profile carries at least one photograph.

### 4.3 Verification methodology and known gaps

Every species record is grounded in the primary sources listed in §2.4. Where sources disagree, the disagreement is recorded on the species page as an `uncertainty:` callout rather than silently resolved: currently in place on hala (Wagner indigenous versus Gallaher-et-al Polynesian introduction), niu (Wagner Polynesian introduction versus Harries pre-Polynesian pantropical drift), hau (indigenous versus Polynesian introduction), hinahina kū kahakai (nomenclatural change *Tournefortia argentea* → *Heliotropium foertherianum*), ʻohe makai (nomenclatural change *Reynoldsia* → *Polyscias*), and Christmas berry (the wilelaiki common-name provenance).

Two known gaps remain for future cycles to address:

1. **Species breadth.** The site needs 8 more common, 6 more notable, and at least 1 more rare & exotic species to hit the ≥45 target. Two pre-approved fallback rare endemics — *Delissea rhytidosperma* and *Nototrichium humile* — are untouched and available.
2. **Deep verification.** A systematic cross-check against Wagner/Herbst/Sohmer and NTBG profiles for every claim on every species page — the `M-deep-verification` milestone — has not yet been executed. It is scoped for the later cycles.

One image-licensing decision is also open: whether to admit CC-BY 2.0 into the allow-list. Doing so would unlock better living-plant photographs for *Panicum niihauense* and *Hibiscus waimeae* subsp. *hannerae*, both of which currently rely on herbarium sheets or subspecies-labeled substitutes.

## 5. Discussion

The pipeline-first strategy in cycle 1 paid for itself in cycle 2. Because the build was already data-driven and validator-gated, three workers could add fifteen new species in parallel with no hand-editing of HTML and no last-minute correctness triage; the shard scheme let each branch write into its own manifest and reference file without touching the others'. The cost showed up as integration debt in cycle 3 — one branch had not migrated its manifests into the shards it was supposed to use — but the debt was mechanical and closed in a single cycle without touching content.

The uncertainty renderer, introduced in cycle 1 for the ʻālula profile, has become the single most exercised piece of the schema. Six of the thirty species now carry `uncertainty:` callouts. That density suggests the coastal flora of Hawaii is under active nomenclatural and biogeographic revision, and that a picture-driven field guide can serve its readers by naming the disagreement openly rather than picking one side silently.

Two structural pieces are still weaker than they should be. The `promise_check` cross-check reports twenty residual errors on pre-normalization records that cannot be edited in place; the intent to exempt them is recorded but the tool does not yet consume the exemption for non-UUID errors, so the yellow state persists in reports. And the deep-verification pass — a systematic reading of every load-bearing claim against Wagner/Herbst/Sohmer, NTBG, and USFWS — has not yet begun. Both are named work items for cycles 4–6.

## 6. Open questions for the remaining cycles

- Which 15+ additional species should fill the tier targets, and in what order? The remaining common-tier slots (8) are the largest single lift.
- Should CC-BY 2.0 be admitted to the license allow-list to unlock living-plant photographs for two federally listed species now relying on herbarium fallbacks?
- What is the acceptance criterion for the deep-verification pass? A defensible answer is "every claim in every profile carries either a Wagner-page citation or an explicit uncertainty block".
- Should the residual ledger cross-check errors be closed by extending the exemption mechanism, or accepted as a documented yellow state through run end?

## References

The references below are the numbered global bibliography used throughout the site as of cycle 3. Branch-local reference shards (`data/references/branch-{a,b,c}.md`) contribute additional citations remapped into this numbering at build time.

[1] Wagner, W. L., Herbst, D. R., & Sohmer, S. H. (1999). *Manual of the Flowering Plants of Hawaiʻi*, Revised Edition. Bishop Museum Press, Honolulu. Two volumes.

[2] Smithsonian National Museum of Natural History. *Flora of the Hawaiian Islands* (online checklist).

[3] National Tropical Botanical Garden. *Meet the Plants* (species profiles database).

[4] Bishop Museum. *Herbarium Pacificum and Flora of the Hawaiian Islands.*

[5] U.S. Fish and Wildlife Service. (1994). Endangered and Threatened Wildlife and Plants; Determination of Endangered or Threatened Status for 21 Plants from the Island of Kauai, Hawaii. Federal Register 59: 9304–9329.

[6] Starr, F. & Starr, K. *Hawaii Plant Image Archive* (Starr Environmental). Images on Wikimedia Commons under CC-BY 3.0.

[7] Wikimedia Commons contributors. Per-image photograph pages; licenses recorded in `data/images.lock.json`.

[8] Hawaii Department of Land and Natural Resources, Division of Forestry and Wildlife. *Rare Plants of Hawaii.*

[9] Little, E. L. Jr. & Skolmen, R. G. (1989, reprinted 2003). *Common Forest Trees of Hawaii (Native and Introduced).* USDA Forest Service Agriculture Handbook 679. Public domain.

[10] Krauss, B. H. (1993). *Plants in Hawaiian Culture.* University of Hawaiʻi Press, Honolulu.

[11] Wood, K. R. (2012). Possible extinctions, rediscoveries, and new plant records within the Hawaiian Islands. *Bishop Museum Occasional Papers* 113: 91–102.

[12] USDA, NRCS. *PLANTS Database.*

[13] Hawaiian Ecosystems at Risk project (HEAR). Invasive plant species information.

[14] Motooka, P., Castro, L., Nelson, D., Nagai, G., & Ching, L. (2003). *Weeds of Hawaii's Pastures and Natural Areas: An Identification and Management Guide.* CTAHR, University of Hawaii at Manoa.

[15] Pacific Cooperative Studies Unit. Nā Pali Coast vegetation surveys and rare plant monitoring reports. University of Hawaii at Manoa.

Branch B additions (rendered globally via `"B:n"` tokens): Rock 1913 *Indigenous Trees of the Hawaiian Islands*; Harries 1978 on *Cocos nucifera* evolution; Lowry & Plunkett 2010 on the *Polyscias* recircumscription; Chinnock 2007 on Myoporaceae; Herbst 1988 on Hawaiian strand-plant biogeography; Rubinoff et al. 2010 on the erythrina gall wasp; USFWS 1994 *Sesbania tomentosa* listing rule; DLNR *Naio Thrips* fact sheets.

Branch C additions (rendered globally via `"C:n"` tokens): USFWS 1996 Federal Register listing for *Panicum niihauense*; NTBG species profiles for *Schiedea apokremnos* and *Hibiscus waimeae* subsp. *hannerae*; Wagner & Weller 2000 revision of *Schiedea*; multi-agency Hawaii weed compendia on *Furcraea foetida*; Wagner & Herbst 2003 *Supplement to the Manual*.

## Appendix: Implementation Details

**Workspace layout.**

- `site/` — 35 rendered HTML files (30 species pages + index, glossary, safety-and-ethics, credits, references).
- `site/assets/photos/` — 72 downscaled photographs (150–400 KB each).
- `site/assets/diagrams/` — 18 hand-authored SVG files.
- `data/species/` — 30 YAML species records.
- `data/images.json` + `data/images.branch-{a,b,c}.json` — sharded image manifests.
- `data/references/branch-{a,b,c}.md` — per-branch reference shards.
- `scripts/` — `build_site.py`, `fetch_images.py`, `discover_images.py`, `lint_site.py`, `check_coverage.py`, `check_links.py`, `check_offline.py`, plus one-shot ledger emitters.
- `tests/` — `test_validators.py` (4 negative fixtures) and `test_build_merge.py` (3 negative fixtures).

**Validator state at cycle-3 close.**

- `build_site`: 30 species pages + 5 static pages; 23 citation tokens resolved.
- `check_coverage`: 30 species; common=12, notable=9, rare_exotic=9; every profile passes required-field, visual, and citation checks.
- `lint_site`: 35 HTML files, 0 external asset URLs.
- `check_links`: 35 pages, all internal links resolve.
- `check_offline`: 35 HTML files, safe for `file://`.
- `tests/test_validators.py`: 4 of 4 pass.
- `tests/test_build_merge.py`: 3 of 3 pass.
- `promise_check`: 20 residual errors on pre-normalization ledger events; documented via `reports/promise_check_immutable_exceptions.json`; non-blocking.

**Ledger state.** 49 events. Milestones `M-arch-pipeline`, `M-schema`, `M-image-pipeline`, `M-svg-library`, `M-validators`, `M-slice-10-species`, `M-site-shippable-cycle1`, and `M-manifest-sharding` are validated. Milestones `M-common-tier-broaden` (12/20), `M-notable-tier-broaden` (9/15), and `M-rare-tier-broaden` (9/10) are in progress. Milestone `M-deep-verification` and `M-final-report` are not yet started.

**Source sessions.** Cycle 1 researcher `3e7bfc7e`; cycle 1 worker `7995fec9`; cycle 1 auditor `f8434645`; cycle 2 researcher `ca753f84` (whose plan produced the three-way fan-out); cycle 3 worker `3bbec44f` (the post-merge integration). Per-cycle reports live under `reports/cycles/`.
