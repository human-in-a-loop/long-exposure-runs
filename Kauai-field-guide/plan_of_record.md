---
created: 2026-08-28T00:56:58Z
run_id: run-2026-08-28T005658Z
agent: researcher
---

# Plan of Record — Develop a comprehensive, locally accessible, HTML-based fiel

**Created:** 2026-08-28T00:56:58Z
**Run id:** run-2026-08-28T005658Z

## Directive (verbatim)

Develop a comprehensive, locally accessible, HTML-based field guide to the plants of the unpopulated coast of Kauai, Hawaii — the roadless Nā Pali Coast (Kalalau, Honopū, Nuʻalolo Kai, Miloliʻi, and the Awaʻawapuhi valley mouths) and other remote, uninhabited coastal stretches of the island (for example the Māhāʻulepū coastline and the Nā Pali–Kona coastal strand). Cover three clearly labeled tiers of species: (1) COMMON — plants a hiker or boater will actually encounter on beaches, dunes, sea cliffs, and valley mouths; (2) NOTABLE — culturally or ecologically significant natives (indigenous and endemic) and Polynesian-introduced canoe plants; (3) RARE & EXOTIC — rare endemics of the Nā Pali coastal cliffs (including federally listed species) plus notable exotic/invasive plants that now dominate or threaten these habitats.

The guide is visuals-first: it must work as a picture-driven identification tool, not a text catalog.

Deliverable and constraints:

- The primary artifact is a self-contained static HTML field guide at `site/index.html` in the workspace (with per-species pages or a well-organized single-page layout under `site/`). It must open offline from the local filesystem (file://) with NO external runtime dependencies: no CDN links, no hotlinked images, no web fonts; all CSS/JS inline or relative-local, all images stored locally under `site/assets/`.
- VISUALS (hard requirement): every species profile must carry at least 2 and ideally 3–5 pictures, chosen to support field identification — whole-plant habit, leaf close-up, flower, fruit/seed, and habitat context. Two permitted sources, in order of preference: (a) openly licensed photographs — public domain / CC0 / CC-BY / CC-BY-SA only (strong sources for Hawaiian coastal flora: Forest & Kim Starr's Hawaii plant image archive (CC-BY), Wikimedia Commons, USDA PLANTS, USFWS and NPS media) — downloaded via scripts into `site/assets/`, downscaled to a sensible size (~150–400 KB each), each embedded with a caption and a per-image attribution + license entry; and (b) locally generated SVG identification diagrams (habit silhouette, leaf shape/margin/venation, flower and fruit schematics, cliff-zone placement diagrams). Never embed an image whose license you could not verify; if verified open photos cannot be found for a species, substitute clean SVG diagrams so the 2-visual minimum still holds. The guide must include an image-credits section listing every photograph's author, source, and license.
- HOW TO IDENTIFY (hard requirement): every species profile must include a dedicated "How to identify" block — step-by-step field marks in plain language (growth form, leaves, flowers, fruit, bark/stem, size, where it sits in the coastal zone), the 2–4 features that clinch the ID, and look-alikes with exactly how to tell them apart. Visuals and ID notes should reference each other (e.g., captions that point at the diagnostic feature).
- Each species profile must also include: scientific name with authority; family; Hawaiian and English common names; biogeographic status (endemic / indigenous / Polynesian introduction / modern introduction / invasive); conservation status where applicable; habitat and where on the unpopulated coast it occurs (zone: strand, dune, sea cliff, valley mouth, riparian); notes on ecology, cultural significance (respectful, non-extractive framing), and hazards (e.g., toxicity, spines); and numbered citations tied to REFERENCES.md.
- Ground every species and every load-bearing claim in verifiable sources via WebSearch (e.g., Bishop Museum's Flora of the Hawaiian Islands records, the Smithsonian Flora of the Hawaiian Islands checklist, National Tropical Botanical Garden plant profiles, USFWS listing documents, Hawaii DLNR/DOFAW resources, and peer-reviewed flora). No fabricated species, names, ranges, or statuses; where sources disagree or are thin, mark the uncertainty explicitly in the guide, then resolve it or drop the claim.
- Target breadth: at least 45 species total across the three tiers by run end (roughly 20 common, 15 notable, 10+ rare/exotic), with accuracy always taking priority over count.
- The guide must include: a browsable, thumbnail-forward index grouped by tier and by habitat zone; a client-side text filter in vanilla JS; a "how to use this guide" introduction; a safety-and-ethics note (no collecting, Leave No Trace, cultural respect for wahi pana); a glossary of botanical and Hawaiian terms; an image-credits page; and a references section generated from REFERENCES.md.
- Validation is part of the work: write and run scripts that lint the HTML (well-formedness, internal link integrity, and zero external URLs in src/href asset references), verify species-count coverage per tier, check that every species profile carries the required fields, and check the visual minimums (≥2 local images per species, every photograph carrying an attribution + license entry). Auditors should run these checks each cycle.
- Pacing: this run is budgeted at approximately 6 researcher → worker → auditor cycles. Stand up a working end-to-end site with the image pipeline within the first one or two cycles, then broaden species coverage and deepen verification; keep the site shippable at every cycle boundary.

The final report should summarize species coverage per tier, visual coverage (images per species, licenses used), the verification methodology, and known gaps.

## Goals

| Goal ID | Goal | Owner |
|---------|------|-------|
| G1      | Ship a self-contained, offline HTML field guide to Kauai's unpopulated-coast plants covering ≥45 species across three clearly labeled tiers, every profile carrying ≥2 license-verified visuals and a full "How to identify" block. | researcher |
| G2      | All species records, images, and pages are mechanically validated: no external URLs, all required fields present, image licenses in the CC allow-list, internal links resolve. | worker + auditor |
| G3      | Every load-bearing botanical claim is tied to a numbered reference from Wagner/Herbst/Sohmer, Smithsonian FHI, NTBG, USFWS, or peer-reviewed flora. | researcher + auditor |

## Milestones

| Milestone ID | Goal | Description | Success criteria (falsifiable) | Dependencies |
|--------------|------|-------------|--------------------------------|--------------|
| M-arch-pipeline    | G1,G2 | Data-driven build: YAML species records + image manifest + build script + validators. | `scripts/build_site.py` renders the site from `data/` without hand-editing HTML; all three validator scripts exist and run. | — |
| M-schema           | G1    | Species YAML schema locked (fields, enums, "How to identify" block). | `scripts/check_coverage.py` enforces the schema; negative fixtures rejected. | M-arch-pipeline |
| M-image-pipeline   | G1,G2 | License-verify-closed image download pipeline that produces `data/images.lock.json`. | `scripts/fetch_images.py` refuses non-allow-list licenses; downloads Wikimedia thumbnails; retries on 429. | M-arch-pipeline |
| M-svg-library      | G1    | ≥10 reusable SVG diagram primitives + 1 Nā Pali zone cross-section, all under `site/assets/diagrams/`. | Files present; render inline in species pages; no external assets. | — |
| M-validators       | G2    | lint_site, check_coverage, check_links, test_validators. | All exit 0 on the current site; negative fixtures rejected. | M-arch-pipeline |
| M-slice-10-species | G1,G3 | 10-species vertical slice across all three tiers with ≥2 visuals and citations. | 10 YAMLs present; each references verified images and citations; check_coverage green. | M-schema, M-image-pipeline |
| M-site-shippable-cycle1 | G1,G2 | Full site renders and opens under `file://` with no external requests. | Every anchor/link resolves locally; no `http://` src/href in rendered HTML. | M-slice-10-species, M-validators |
| M-common-tier-broaden  | G1 | Grow COMMON tier toward ~20 species. | check_coverage reports COMMON count ≥ 20. | M-site-shippable-cycle1 |
| M-notable-tier-broaden | G1 | Grow NOTABLE tier toward ~15 species. | check_coverage reports NOTABLE count ≥ 15. | M-site-shippable-cycle1 |
| M-rare-tier-broaden    | G1 | Grow RARE & EXOTIC tier to ≥10 species. | check_coverage reports RARE count ≥ 10. | M-site-shippable-cycle1 |
| M-deep-verification    | G3 | Deep verification pass against Wagner/Herbst/Sohmer + NTBG + USFWS for every claim. | Auditor sign-off; ≥90% of claims tied to primary source. | broaden milestones |
| M-final-report         | —  | Cycle 6 final report: species coverage per tier, image licenses, methodology, gaps. | Report present at `reports/final/final_report.md`. | deep-verification |
| M-manifest-sharding    | G2 | Sharded-manifest infra: per-branch `data/images.branch-*.json` + `data/references/branch-*.md` + citation-token rewriting in `build_site.py`. Enables cycle-2 fan-out to merge without conflict. | Successive builds byte-identical; 3 negative fixtures (duplicate id, shard order, unresolved token) all reject. | M-arch-pipeline |
| _moderate/hala-uncertainty              | G3 | Emergent cycle-2 finding: hala.yaml carries an `uncertainty:` block on Wagner-indigenous vs. Gallaher-et-al Polynesian-introduction contested status. | Rendered on the hala page as a callout with sourced citations. | — |
| _moderate/look-alikes-len-tightening    | G2 | Emergent cycle-2 finding: `check_coverage.py` look_alikes rule tightened to `len < 1`. | Negative fixture rejects species with empty look_alikes list. | M-validators |
| _moderate/wilelaiki-style-leak          | G3 | Emergent cycle-2 finding: wilelaiki removed from Christmas berry hawaiian names; provenance recorded in `uncertainty:` block citing Wagner + Motooka. | Rendered page shows `wilelaiki` only inside the uncertainty callout. | — |
| _minor/coverage-images-empty-list-bug   | G2 | Emergent cycle-2 finding: split `check_coverage.py` REQUIRED_TOP so `images: []` is permitted (needed for SVG-only fallback). | SVG-only species (schiedea-apokremnos) passes coverage. | M-validators |
| _deferred/niu-status-uncertainty        | G3 | Emergent cycle-2 finding: niu (Cocos nucifera) status uncertainty block cites Harries 1978 pantropical-natural alternative. | Rendered on niu page. | — |
| _deferred/hala-status-uncertainty       | G3 | Emergent cycle-2 finding: closed by reference to `_moderate/hala-uncertainty` (same underlying resolution). | Same rendering. | _moderate/hala-uncertainty |
| _stale/emit_cycle1_events               | —  | Emergent cycle-2 housekeeping: cycle-1 one-shot ledger seeder retained under `stale/scripts/` for audit trail. | Physical file present at `stale/scripts/emit_cycle1_events.py`. | — |
| _infra/license-allowlist-cc-by-2        | G2 | Emergent cycle-3 Branch C: extend image license allow-list to include CC-BY-2.0 and CC-BY-2.5; factor duplicated allow-list into shared `scripts/_licenses.py`; add negative fixture rejecting CC-BY-NC-*. | `scripts/_licenses.py` present; both `fetch_images.py` and `check_coverage.py` import from it; negative fixture passes. | M-image-pipeline, M-validators |
| _orphan/cycle-3-branch-c-reimage-panicum-hibiscus | G1 | Emergent cycle-3 Branch C: re-imaged *Panicum niihauense* and *Hibiscus waimeae* subsp. *hannerae* under the extended CC-BY-2.0 allow-list. | Three CC-BY-2.0 photos in `data/images.branch-c.json`; retired-photo removed from disk; YAML `images:` lists updated. | _infra/license-allowlist-cc-by-2 |
| _orphan/cycle-3-branch-c-verification-pilot | G3 | Emergent cycle-3 Branch C: 5-species deep-verification pilot producing refined checklist for cycle 4's full 45-species pass. | Report present at `reports/verification/cycle_03_pilot.md`; 55-row matrix; refined checklist section; 4 discrepancies logged via `_deferred/*` events. | M-slice-10-species |
| _deferred/hala-uncertainty-rewrite       | G3 | Emergent cycle-3 pilot finding: hala uncertainty block misattributes Gallaher 2015 (Gallaher supports pre-human natural dispersal, not Polynesian introduction). Rewrite to reflect both/and consensus. | Uncertainty block reworded on `data/species/hala.yaml`; new Gallaher-review citation added. | _orphan/cycle-3-branch-c-verification-pilot |
| _deferred/hala-gallaher-title-fix        | G3 | Emergent cycle-3 pilot finding: `[A:3]` title in `data/references/branch-a.md` is a fabricated/malformed title (should be "A long distance dispersal hypothesis for the Pandanaceae and the origins of the Pandanus tectorius complex"). | Title corrected in `branch-a.md` `[A:3]`. | _orphan/cycle-3-branch-c-verification-pilot |
| _deferred/alula-conservation-status-refresh | G3 | Emergent cycle-3 pilot finding: alula `conservation_status` string conflates two IUCN categories. Refresh against current USFWS 5-Year Review (2022) and IUCN Red List (2020 assessment: EW). | `conservation_status:` reworded on `data/species/alula.yaml`. | _orphan/cycle-3-branch-c-verification-pilot |
| _deferred/christmas-berry-noxious-weed-source | G3 | Emergent cycle-3 pilot finding: "Hawaii state noxious weed" claim on christmas-berry could not be verified against HDOA HAR §4-68. Fetch primary source; either cite it or reword to advisory-list language. | `conservation_status:` reworded and cited on `data/species/christmas-berry.yaml`. | _orphan/cycle-3-branch-c-verification-pilot |
| _plan/cycle-3-branch-c-emergent-milestones | — | Emergent-milestones documentation edit for cycle 3 Branch C. | This table row and its five siblings above are present. | — |

## Out of scope (explicit)

- Not a substitute for a botanist's field key — the guide is picture-driven and complements, does not replace, primary flora.
- No live server; the acceptance test is `file://` local file access.
- Not a harvest guide — cultural framing is respectful and non-extractive.

## Pointer to ledger

Every milestone status, history, and judgment lives in `promise_ledger.jsonl`,
filtered by `milestone_id`. Run `promise_check` to materialize the current
state for the human; agents call it via Bash:

    python3 -m long_exposure.tools.promise_check .

The directive section above is **immutable** after creation. Goals and
milestones tables are mutable, but every edit must emit a ledger event with
`milestone_id: "_plan/<descriptive-change-name>"` so the audit trail is
complete.
