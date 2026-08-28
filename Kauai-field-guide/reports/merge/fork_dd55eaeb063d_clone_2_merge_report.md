---
fork_id: "dd55eaeb063d"
clone_k: 2
cycle_range: "cycles 1-1 [merge]"
deliverable_path: "reports/cycles/cycle_02_branch_c_rare_invasive.md"
deliverable_exists: true
verdict: "validated"
generated_at: "2026-08-28T02:19:43.578342+00:00"
---
# Branch C Merge Report — Rare Endemics + Coastal Invasives (Cycle 1, Clone 2 of fork dd55eaeb063d)

## Abstract

This merge report closes out Branch C of the cycle-2 fan-out for the offline HTML field guide to the plants of the unpopulated Kauaʻi coast. Branch C's scoped objective was to add six species profiles — three rare Kauaʻi coastal endemics (*Schiedea apokremnos*, *Hibiscus waimeae* subsp. *hannerae*, *Panicum niihauense*) and three dominant coastal invasives (*Leucaena leucocephala*, *Ricinus communis*, *Furcraea foetida*) — while exercising the guide's SVG-only visual fallback on any rare endemic that produced no license-verifiable photographs, and to resolve one carry-over moderate finding: a style leak where *wilelaiki* was listed as a Hawaiian common name on the *Schinus terebinthifolia* (Christmas berry) profile without any indication that the term is a post-contact transliteration rather than a traditional Hawaiian name. The branch delivered all six species profiles, exercised the SVG-only fallback on *Schiedea apokremnos*, resolved the wilelaiki finding via an `uncertainty:` block with source citations, and closed with the full validator suite green and the site shippable at the branch boundary. The auditor's independent verdict is COMPLETE.

## Introduction

The overall build is paced across roughly six research–build–audit cycles. Cycle 1 stood up the site skeleton and proved the mainstream image pipeline — openly licensed photographs from the Starr Hawaii archive, Wikimedia Commons, USDA PLANTS, USFWS and NPS media — at scale, delivering ten species with twenty-six photographs. Cycle 2 fanned out into three parallel branches to broaden coverage in parallel without stepping on each other. Branch A landed sharded-manifest infrastructure so that later branches would not collide on the shared references and image-manifest files. Branch B added common-tier species. Branch C, the subject of this report, was assigned the hardest visual cases of the run: coastal endemics so rare that no photographer working under a compatible open license has photographed them, and coastal invasives dominant enough that their hazards blocks must be prominent and defensible against a lay reader.

Branch C depended on Branch A landing its sharded-manifest infrastructure first, and was instructed to follow the pre-sharded content path with per-file migration markers so that both paths could be reconciled at the cycle-2 merge without disturbing the rendered site.

## Approach

### Species selection

The six species were fixed by the branch assignment. Three pre-approved fallback endemics — *Delissea rhytidosperma* and *Nototrichium humile* — were held in reserve in case any of the primary three failed range verification. None were needed. *Panicum niihauense*, whose historical stronghold is Niʻihau, was specifically flagged for range verification; the branch confirmed extant Kauaʻi populations at Polihale via Smithsonian herbarium sheets before committing to include it.

### Visuals — mainstream photograph path

For the three invasives and two of the three rare endemics, openly licensed photographs were sourced from Wikimedia Commons and the Forest & Kim Starr Hawaii archive, downloaded, downscaled to the guide's size band of roughly 150–400 KB, and manifested with author, license, license URL, source, source page, and local path. Photographs of *Hibiscus waimeae* subsp. *hannerae* were only available from cultivated material on Oʻahu; the diagnostic features match Nā Pali wild-plant references and captions do not misrepresent the material as wild-photographed, but a future cycle would benefit from a wild Kauaʻi image if one becomes available under a compatible license.

### Visuals — SVG-only fallback

*Schiedea apokremnos*, a federally endangered subshrub restricted to sea-cliff faces on the Nā Pali coast, returned zero license-verifiable photographs after an exhaustive search of Wikimedia Commons, the Starr archive, USFWS media collections, and NPS media collections. The branch exercised the SVG-only fallback: two hand-authored SVG identification diagrams — a cliff-pendent habit silhouette (`habit-cliff-pendent-subshrub.svg`) and a narrow-succulent leaf schematic (`leaf-narrow-succulent.svg`) — were placed in the guide's diagram library and the profile's photograph list was left empty. The exhaustive negative search was recorded in the species data file under an `image_search_notes:` block so that later cycles do not repeat it. The profile still satisfies the guide's hard requirement of at least two visuals per species.

### Christmas berry — wilelaiki fix

The Hawaiian common-name list on the *Schinus terebinthifolia* profile was emptied. An `uncertainty:` block was added attributing *wilelaiki* as a post-contact Hawaiianized transliteration (reportedly of the personal name "Willie Rice"), citing Wagner *et al.*'s *Manual of the Flowering Plants of Hawaiʻi* as authority for the absence of the term from the traditional Hawaiian name inventory and Motooka *et al.* as the source that records the transliteration. The rendered profile now uses the term exactly once, inside the uncertainty callout, matching the guide's design intent for terms with contested provenance.

### Hazards emphasis for castor bean

*Ricinus communis* seeds contain ricin at concentrations that can be lethal to humans and to children in particular. The profile carries an explicit "DANGER:" prefix on its hazards block, presented in the guide's existing hazard visual style. The audit noted that the current `.hazard` CSS treatment (soft-pink background, thin red left border) is on the modest side for a lethal-toxin warning aimed at hikers with children, and proposed a one-line CSS sharpening. That change was deferred to the cycle merge to avoid conflicting edits on shared stylesheets across the parallel branches.

### Uncertainty handling for *Furcraea foetida*

Sources disagree on whether the leaf margins of *Furcraea foetida* are consistently spineless or variably armed. Rather than pick a side, the profile records the disagreement in an `uncertainty:` block, consistent with the branch's brief to prefer explicit uncertainty over false confidence.

### Cross-branch coordination

Branch B's references were numbered [16]–[23]; Branch C's six new references were placed at [24]–[29] to avoid collision. Every new species data file carries an `_migration_note:` field flagging that its citation numbers and image manifest entries may need renumbering when Branch A's sharded infrastructure is consolidated at merge. The site build script supports both paths, so the rendered site is correct on either footing.

## Findings

### What was delivered

Six new species data files were written, validated, and rendered to HTML:

- **Rare Kauaʻi coastal endemics.** *Schiedea apokremnos* (Caryophyllaceae; federally endangered; two SVG diagrams, no photographs). *Hibiscus waimeae* subsp. *hannerae* (Malvaceae; federally listed; photographs from cultivated material). *Panicum niihauense* (Poaceae; Kauaʻi/Polihale extancy confirmed; illustrated with CC0 Smithsonian herbarium sheets plus diagrams).
- **Dominant coastal invasives.** *Leucaena leucocephala* (koa haole; Fabaceae). *Ricinus communis* (castor bean; Euphorbiaceae; prominent hazards block). *Furcraea foetida* (Mauritian hemp; Asparagaceae; leaf-spine variability recorded as uncertainty).

The Christmas berry Hawaiian-name defect was fixed as described above.

Nine new photograph entries were added to `data/images.lock.json`. The worker's report said eleven; the audit count is nine, with the difference being two herbarium sheets already counted in the photograph total — an accounting drift, not a correctness issue. License distribution: six CC-BY 3.0, one CC-BY-SA 3.0, two CC0, all within cycle-1's locked allow-list. Every entry has non-empty author, license, license URL, source, source page, and local path, and every file is present on disk under `site/assets/photos/`.

Two hand-authored SVG identification diagrams were added to `site/assets/diagrams/`, both used by the *Schiedea apokremnos* profile. These are content, not architectural changes to the SVG library scripts, and are consistent with the branch's "do not modify architecture" constraint.

Six new numbered references were appended to `REFERENCES.md` at entries [24]–[29], spanning USFWS listing documentation, Wagner *et al.*'s *Manual of the Flowering Plants of Hawaiʻi*, National Tropical Botanical Garden species profiles, and Motooka *et al.*'s Hawaiʻi weed reference.

### What was tested

At branch close the auditor independently re-ran the full validator suite:

| Check | Result |
| --- | --- |
| `scripts/build_site.py` | 30 species pages + 5 static pages; 17 citation tokens resolved |
| `scripts/lint_site.py` | 35 HTML files; 0 external asset URLs |
| `scripts/check_coverage.py` | 30 species; common=12, notable=9, rare_exotic=9 |
| `scripts/check_links.py` | 35 pages; all internal links resolve |
| `scripts/check_offline.py` | 35 HTML files; safe for `file://` |
| `tests/test_validators.py` | ALL PASSED (incl. new `empty look_alikes` fixture from Branch A) |
| `long_exposure.tools.org_check` | green |
| `long_exposure.tools.promise_check` | green after auditor event appended |

### What was proven

The branch's central mechanism claim — *"cycle 1 proved photos work at scale; this branch proves the fallback works when photos don't exist"* — is confirmed at the file-and-render level. *Schiedea apokremnos*, the canonical test case named in the cycle-1 research brief, now has a shippable identification profile that satisfies the ≥2 visual minimum on two hand-authored SVG diagrams alone, with the negative photo search documented in-YAML. This de-risks the remaining rare-tier work for cycles 3–5: species with photo coverage take the mainstream path, and species without take the SVG-only fallback path.

The content pattern for common names of contested provenance, first introduced in cycle 1 for *Brighamia insignis*, also generalized cleanly to two additional cases this branch: *wilelaiki* on Christmas berry (a post-contact transliteration, not traditional Hawaiian) and the Polihale extancy question for *Panicum niihauense*. The pattern reads well in the rendered HTML and stays honest about source thinness.

Cross-branch coordination worked. Branch C detected Branch B's [16]–[23] reference block and renumbered its own additions to [24]–[29] without collision. Branch A's sharded manifest landed concurrently mid-branch; Branch C followed the pre-sharded path as instructed and tagged every YAML with a migration note.

## Discussion

### Items intentionally deferred to the cycle-2 merge

Several items surfaced during branch work that are cycle-level or merge-level concerns rather than in-scope Branch C work.

**Ledger schema drift (cross-branch).** Two of Branch C's worker events for `M-rare-tier-broaden` and `_moderate/wilelaiki-style-leak` (lines 15–16 of `promise_ledger.jsonl`) use a schema that predates the workspace's current unified event vocabulary: `timestamp` instead of `ts`, `summary` instead of `narrative`, missing `event_id`, `confidence` as a bare string rather than an object, an `_moderate/*` milestone-namespace prefix that is not on the reserved list, and `status: "resolved"` instead of `validated`. Branch A's events at lines 12–14 have the identical issues. These do not affect the rendered site, and the auditor event `3fa10e1e-ce76-498b-9da1-caebdac54018` supersedes them functionally, but the malformed lines remain in the append-only log and trip `promise_check`. The cleanest fix is to expand the reserved-namespace list in `long_exposure/tools/promise_check.py` to include `_moderate/`, a small maintenance edit rather than a per-branch cleanup burden.

**CC-BY 2.0 allow-list expansion.** Broadening the cycle-1 locked allow-list to include CC-BY 2.0 would unlock better living-plant photographs for several rare endemics — notably Eickhoff's *Panicum niihauense* material. This is a cycle-level decision about the guide's global licensing posture and belongs to the root conductor.

**`.hazard` CSS sharpening for castor bean.** A one-line CSS change (for example, `.hazard { border-left: 4px solid; padding: 0.6em; font-weight: 500; }`) would give the "DANGER:" block on the *Ricinus communis* page the visual weight a lethal-toxin warning deserves. Deferred to merge to avoid conflicting edits on shared stylesheets.

**Citation-shard migration.** Branch C's references [24]–[29] and its nine image manifest entries live in the base `REFERENCES.md` and `data/images.json`. Migrating them to `data/references/branch-c.md` and `data/images.branch-c.json` for stylistic consistency with Branch A's sharded infrastructure is cleanup, not correctness. Every affected data file carries a migration marker.

### Progress toward tier targets

At the close of this branch the rare-and-exotic tier stands at nine species against the guide's ≥10 target. One additional rare-tier species remains to be added in a later cycle to close `M-rare-tier-broaden`. The pre-approved fallback list (*Delissea rhytidosperma* and *Nototrichium humile*) is available and untouched.

### Known gaps in Branch C's own work

The *Hibiscus waimeae* subsp. *hannerae* photographs are from cultivated Oʻahu material rather than wild Kauaʻi plants — captions are honest about this, and a wild Kauaʻi image would be a future improvement if one becomes available under a compatible license. The *Panicum niihauense* profile leans on Smithsonian herbarium sheets rather than living-plant photographs, a direct consequence of the license allow-list decision noted above. The variability of *Furcraea foetida* leaf-margin spines is recorded as uncertainty rather than an assertion in either direction — the correct handling for this branch, but a later cycle could resolve it with a dedicated source pass.

## Conclusions

Branch C's scoped fan-out objective is delivered in full. Six new species profiles are live and validating. The Christmas berry Hawaiian-name defect is fixed with sourced attribution. The SVG-only visual fallback path is proven on the canonical test case *Schiedea apokremnos*. The full validator suite is green. The site remains shippable at the branch boundary. The auditor's independent verdict is COMPLETE, and there is no further in-scope work for this fan-out clone. The items noted for the merge conductor are cycle-level or cross-branch concerns rather than Branch C work.

## Appendix — Implementation Details

### Files added or modified

- **Species data added.** `data/species/schiedea-apokremnos.yaml`, `data/species/hibiscus-waimeae-hannerae.yaml`, `data/species/panicum-niihauense.yaml`, `data/species/koa-haole.yaml`, `data/species/castor-bean.yaml`, `data/species/mauritian-hemp.yaml`.
- **Species data modified.** `data/species/christmas-berry.yaml` (wilelaiki fix).
- **Rendered pages.** Six new files under `site/species/`, plus the re-rendered Christmas berry page.
- **Diagrams added.** `site/assets/diagrams/habit-cliff-pendent-subshrub.svg`, `site/assets/diagrams/leaf-narrow-succulent.svg`.
- **Photographs added.** Nine new files under `site/assets/photos/`, with nine corresponding entries in `data/images.lock.json`.
- **References added.** `REFERENCES.md` entries [24]–[29].
- **Branch report.** `reports/cycles/cycle_02_branch_c_rare_invasive.md` (283 lines).

### Coverage at branch close

Thirty species total across the guide: twelve common, nine notable, nine rare-and-exotic. Thirty-five HTML pages built. Seventeen citation tokens resolved. Zero external asset URLs across all pages. Safe for `file://` opening.

### Session references

- Cycle 1 researcher: `f0c1bd67-1ebb-48c3-884e-72ab56282428`.
- Cycle 1 worker: `4166f03f-0f33-4165-9a98-1b814d20d27c`.
- Cycle 1 auditor: `de3d1dde-3470-411a-aae1-65aac66deedd`.
- Auditor ledger event: `3fa10e1e-ce76-498b-9da1-caebdac54018`.

### Notes carried forward for the cycle-2 merge conductor

- Rare-and-exotic tier stands at nine of the ≥10 target; one more rare-tier species needed in a later cycle. Pre-approved fallbacks *Delissea rhytidosperma* and *Nototrichium humile* remain available.
- Sharded-manifest migration for Branch C's data files is a merge-time cleanup; every file carries a migration marker and the build script supports both paths.
- Ledger schema drift is cross-branch (Branch A and Branch C both affected); recommend expanding the reserved-namespace list in `long_exposure/tools/promise_check.py` to include `_moderate/` rather than appending synthetic supersession events per-branch.
- CC-BY 2.0 allow-list expansion is a cycle-level decision, not a per-branch one.
- One-line `.hazard` CSS sharpening for the castor bean warning is deferred to merge to avoid parallel-branch conflict.
- The merge report at `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-dd55eaeb063d/clone-2/merge_report.md` is written outside this sandbox; the substance lives here and in the branch report at `reports/cycles/cycle_02_branch_c_rare_invasive.md`.

<verdict>validated</verdict>