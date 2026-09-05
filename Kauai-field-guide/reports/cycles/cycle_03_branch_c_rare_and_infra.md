---
created: 2026-08-28T03:45:00Z
cycle: 3
run_id: run-2026-08-28T005658Z
agent: worker
milestone: _run/cycle-3-branch-c-close
branch: C (RARE +2 + license allow-list + verification pilot + re-imaging)
---

# Cycle 3 — Branch C — RARE Tier +2, License Allow-List Extension, Verification Pilot

Fan-out clone 2 of fork `1a2a754ccd76`. Four tasks, all closed green.
Species count 30 → 40 (RARE 9 → 11; branch A's cycle-3 photos also fetched
this cycle as a side-effect of the shared build). Full validator + test
suite is green: `check_coverage` OK, `lint_site` OK, `check_links` OK,
`check_offline` OK, `test_validators` 5/5 PASS including the new
CC-BY-NC-* negative fixture, and `build_site.py` renders 45 HTML files
with 36 citation tokens resolved.

## Task-by-task summary

### Task 1 — License allow-list extension ✅

- Created `scripts/_licenses.py` as the **single source of truth** for the
  license allow-list. Previously duplicated in `scripts/fetch_images.py`
  and `scripts/check_coverage.py`; both now import from the shared module.
  `tests/test_validators.py` was updated to copy `_licenses.py` alongside
  the validators into the tmp workspace it builds each run.
- Added `CC-BY-2.0` and `CC-BY-2.5` to `ALLOWED_LICENSES` per brief.
- Added **negative fixture** `test_coverage_rejects_nc_license` proving
  `CC-BY-NC-4.0` and `CC-BY-NC-SA-4.0` are still rejected — the extension
  broadened attribution-only *versions*, not permission *scope*.
- End-to-end verification: fetched 3 CC-BY-2.0 photos through
  `scripts/fetch_images.py`, all landed on disk, all pass
  `check_coverage.py`.
- Ledger event: `_infra/license-allowlist-cc-by-2` (validated, high).

### Task 2 — Re-image *Panicum niihauense* and *Hibiscus waimeae* subsp. *hannerae* ✅

Positive result — cycle 2's blocker (CC-BY-2.0 outside allow-list) was
exactly the case here.

- **Panicum niihauense**: retired `panicum-niihauense-specimen-02`
  (redundant second herbarium sheet — deleted from disk + lock);
  added two David Eickhoff CC-BY-2.0 living-plant photographs:
  `panicum-niihauense-living-habit-01` (5249464569, coarse bunchgrass
  habit) and `panicum-niihauense-living-flowers-01` (5250066904, open
  airy panicle). Retained one CC0 Smithsonian NMNH herbarium sheet
  (`panicum-niihauense-specimen-01`) as taxonomic anchor. Net: 3
  photographs + 2 SVG diagrams (was 2 herbarium + 2 SVG).
- **Hibiscus waimeae subsp. *hannerae***: added one supplemental Eickhoff
  CC-BY-2.0 photograph (`hibiscus-hannerae-eickhoff-01`, 5188167760)
  as a third image. Kept both existing Starr CC-BY-3.0 photos on merit —
  they already showed the diagnostic pink staminal column and the
  smaller-narrower leaf shape distinguishing this subspecies from subsp.
  *waimeae*. Net: 3 photographs (was 2).
- `image_search_notes:` blocks on both YAMLs updated to reflect the
  cycle-3 broadening; the honest limitation — no wild-Polihale or
  wild-Nā Pali photo available under any allow-listed license — is
  preserved so a future cycle can revisit.

### Task 3 — Add 2 RARE Kauaʻi endemics ✅ — with documented scope-check divergence

Both directly-proposed species **failed the worker's scope verification**
and were replaced from the fallback bench, in accordance with the brief's
escalation rule ("If both proposed fail scope, pull two from the fallback
bench in order").

**Directly-proposed species dropped:**

| Species | Fail mode | Verification sources |
|---|---|---|
| *Nototrichium humile* | Endemic to Oʻahu (Waianae range), not Kauaʻi. Brief's speculative "Kauaʻi + historically Oʻahu Waianae range" is inverted — Oʻahu is the current range, Maui the extirpated historical range; Kauaʻi is not documented. Clean scope-fail. | Wikipedia; iNaturalist; USFWS Kuluʻī species page (fws.gov/species/kului-nototrichium-humile) |
| *Delissea rhytidosperma* | Endemic Kauaʻi but restricted to rocky-cliffside *Acacia koa* moist forest in Kuia Gulch (Kuia NAR) and Nā Pali–Kona Forest Reserve — **inland montane**, not coastal. Additionally status is contested ("critically endangered or extinct in the wild" per USFWS/DLNR-DOFAW). Marginal scope + status ambiguity = drop per brief's "do not publish an ambiguous conservation claim" rule. | NTBG plant profile; USFWS ECOS species page; DLNR-DOFAW fact sheet; SavePlants.org |

**Fallback bench navigation:**

The brief's fallback order was Kokia → Isodendrion → Alectryon → Chamaesyce
coastal endemics → ʻohai-type. Working down the order:

1. *Kokia kauaiensis* — brief itself calls coastal fit "weak (dry forest);
   use only if desperate". **Re-verification during scope-check revealed
   NTBG documents Kokia populations in Kalalau Valley and Nā Pali Coast
   State Park** — directly named in the guide's directive. So Kokia is
   in-scope after all, at the upper end of Nā Pali valleys (350–660 m
   mesic forest). Retained. **SVG-only** — no license-verified photo
   exists (best Flickr candidate is All-Rights-Reserved Jim Denny).
2. *Isodendrion pyrifolium* — currently no known Kauaʻi population
   (rediscovered on Hawaiʻi Island 1993, Oʻahu 2015; historical Kauaʻi
   pre-1970 only). Fails present-day Kauaʻi scope. Skipped.
3. *Alectryon macrococcus* — dry forest, weak coastal fit per brief.
   Skipped.
4. *Chamaesyce celastroides var. **stokesii*** — clean coastal fit
   (endemic Niʻihau / Kauaʻi / Molokaʻi / Kahoʻolawe as a "beach form" on
   "windswept cliffs and ledges above the ocean"), **6 wild-Kauaʻi
   CC-BY-2.0 photographs available on Wikimedia (Eickhoff, Kīlauea Point
   NWR)**. Selected as the second RARE species — the only fallback with
   both strong coastal-scope fit AND license-verified in-situ Kauaʻi
   photographs.

**Species delivered:**

- **`kokia-kauaiensis.yaml`** — Kauaʻi treecotton. Endemic mesic-forest
  tree; ~180 individuals across 11 populations including Kalalau and
  Nā Pali Coast State Park. US Endangered. SVG-only visuals:
  reused `habit-small-tree.svg` + `leaf-palmate-lobed.svg` + one newly
  authored `flower-kokia-red-spiral.svg` capturing the diagnostic
  spiral-petaled red flower with curved staminal column. Cultural
  documentation is deliberately sparse — the widely-cited *K. drynarioides*
  ethnobotany does not transfer to *K. kauaiensis*, and we do not
  invent uses.
- **`chamaesyce-celastroides-stokesii.yaml`** — coastal ʻakoko. Companion
  to the existing common-tier *Chamaesyce degeneri*. Three CC-BY-2.0
  wild-Kauaʻi Kīlauea Point NWR photographs (Eickhoff): habit, leaves
  + cyathia, habitat context showing plant growing with naupaka kahakai.
  Nomenclature footnote in `uncertainty:` block acknowledges Wagner's
  *Chamaesyce* placement vs. modern APG's *Euphorbia* — same plant,
  we follow *Chamaesyce* for consistency with existing degeneri.

**Coverage impact:** RARE tier 9 → 11 (target 10+, cleared with margin).

Two new references added to `data/references/branch-c.md`: `C:7` (USFWS
ECOS species profiles), `C:8` (Wagner 1999 + Kew POWO nomenclature).

### Task 4 — Deep-verification pilot on 5 cycle-1 species ✅

Dispatched to a general-purpose teammate. Product: `reports/verification/cycle_03_pilot.md`
(280 lines). Coverage: 5 species × 11 claim categories = 55 rows.
Verdict totals: **51 pass, 4 needs-work, 0 fail**.

**Three headline findings that shape the refined checklist:**

1. **Citation drift hides in author-position, not in reference numbers.**
   The `hala` uncertainty block correctly cites Gallaher et al. 2015
   `[A:3]` but *inverts what Gallaher argues*: Gallaher supports pre-human
   natural dispersal (evidenced by a >1.2 Myr Kauaʻi *Pandanus* fossil),
   not the Polynesian-introduction position the block attributes. Cycle 4's
   checklist now includes a cited-author-position audit as a distinct
   step. As a bonus catch, the pilot found that the `[A:3]` **reference
   title itself** in `branch-a.md` is fabricated ("A long history of
   dispersal and vicariance …" — the actual title is "A long distance
   dispersal hypothesis for the Pandanaceae and the origins of the
   *Pandanus tectorius* complex").

2. **Conservation-status strings need a versioning template.** The `alula`
   `conservation_status` string conflates two IUCN category labels
   ("Critically Endangered — Extinct in the Wild") — since ~2020 the
   category is simply Extinct in the Wild (EW), and the 2022 USFWS 5-Year
   Review adds information the 1994 listing date cannot convey. Cycle 4
   will use a fixed template: `US <status> (USFWS <listing year>; 5-Year
   Review <year>); IUCN <current category> (assessment updated <year>)`.

3. **Statutory-label claims need statutory citations.** The claim that
   *Schinus terebinthifolia* is a "Hawaii state noxious weed" could not
   be verified from HDOA HAR §4-68 primary source in the pilot's search
   reach — the phrase is popular but the statutory list is narrower than
   advisory lists (HISC / Plant Pono / PIER). Cycle 4 must open the
   HAR §4-68 PDF directly.

**Cycle-4 budget estimate (from pilot):** ~15 hours wall-time for a single
researcher across ~45 species (25 min/species × 45, plus a reference-title
audit pass and a statutory-list audit pass).

**Four discrepancies caught, all four deferred to cycle 4** via
`_deferred/*` ledger events (see below). The two nominally "inline"
fixes (Discrepancy #2 in `branch-a.md`, Discrepancy #3 in `alula.yaml`)
were deferred rather than applied because both target files live outside
Branch C's shard-write scope — `branch-a.md` is Branch A's shard, and
`alula.yaml` is a cycle-1 base file authored under no branch's ownership.
Per the brief's "Shard writes only" rule, cross-branch corrections are a
merge/integration action for cycle 4 to sequence properly.

## Sufficiency checklist (from brief)

| Criterion | Status |
|---|---|
| License allow-list extended in all relevant files with a single source of truth | ✅ `scripts/_licenses.py` |
| `_infra/license-allowlist-cc-by-2` event emitted | ✅ (ledger, shadow) |
| Negative fixture rejects CC-BY-NC-4.0 | ✅ (`test_coverage_rejects_nc_license`) |
| Re-imaging attempted for panicum + hibiscus; new photos landed OR null result documented | ✅ 3 new CC-BY-2.0 photos landed |
| 2 RARE Kauai endemics added with ≥2 verified-license visuals, How-to-identify, look-alikes, ≥1 `C:N` token, honest sparse cultural section | ✅ Kokia (SVG-only, 3 visuals) + Chamaesyce stokesii (3 photos + 2 SVGs) |
| `check_coverage.py` reports RARE_EXOTIC ≥ 11 | ✅ 11/10+ |
| Verification pilot report present with methodology + 5-species matrix + refined checklist | ✅ 280-line report |
| Any inline fixes have ledger events; any deferrals have `_deferred/*` events | ✅ (4 `_deferred/*` events; no inline fixes because target files are cross-branch) |
| All new ledger events use canonical schema | ✅ event_id, ts, narrative, confidence-object with assessor |
| `data/images.branch-c.json` and `data/references/branch-c.md` updated; base manifests untouched | ✅ |
| Full validator suite green | ✅ 40 species, 45 HTML, 5/5 tests PASS, 0 lint errors |
| Branch merge report populated | ✅ (this file) |

## Ledger events emitted (10)

Routed through `long_exposure.tools.ledger_append` (auto-routes to
per-clone shadow ledger under fan-out). All events use canonical schema
(event_id, ISO-8601 ts, run_id, cycle, agent, milestone_id, status,
confidence-object with assessor, narrative, artifacts).

1. `_infra/license-allowlist-cc-by-2` — validated/high (Task 1)
2. `_orphan/cycle-3-branch-c-reimage-panicum-hibiscus` — validated/high (Task 2)
3. `M-rare-tier-broaden` — in-progress/high, 11/10+ (Task 3, with divergence narrative)
4. `_orphan/cycle-3-branch-c-verification-pilot` — validated/high (Task 4)
5. `_deferred/hala-uncertainty-rewrite` — in-progress/high (pilot discrepancy #1)
6. `_deferred/hala-gallaher-title-fix` — in-progress/high (pilot discrepancy #2)
7. `_deferred/alula-conservation-status-refresh` — in-progress/high (pilot discrepancy #3)
8. `_deferred/christmas-berry-noxious-weed-source` — in-progress/high (pilot discrepancy #4)
9. `_plan/cycle-3-branch-c-emergent-milestones` — validated/high (plan-of-record extension)
10. `_run/cycle-3-branch-c-close` — validated/high (branch close)

## Plan-of-record updates

Added 8 documenting entries to the milestones table (one for the `_infra`
milestone, one for each `_orphan/*` and each `_deferred/*`, and one for
the `_plan/*` housekeeping edit itself). Follows the cycle-2 pattern that
kept `promise_check` quiet on "milestone not in plan" for emergent items.

## Known deferrals for cycle 4

- The four pilot discrepancies above.
- Broader deep-verification pass across all 45 species (per pilot's refined
  checklist — cycle 4 primary work).
- CC-BY-2.0-unlocked photo revisit for other species not covered in Task 2
  (Branch B's niu/hau or Branch A's newer additions may now have better
  living-plant options).
- Persistent `promise_check` yellow state on lines 12-16 / 32-38 unchanged
  (out of scope per brief).

## Divergences from brief (all documented)

1. **Two directly-proposed RARE species swapped for fallbacks** — full
   rationale in Task 3 above. Both proposed species failed
   worker-verified scope tests; the swap follows the brief's own
   fallback rule.
2. **All four pilot discrepancies deferred (not just the pilot's 2
   nominal inline-fix items)** — cross-branch write boundary. The pilot
   teammate did not have the branch-scope context to know this;
   deferring all four is the correct interpretation of the brief's
   "shard writes only" rule.

## Divergences from research brief that are **NOT** divergences

- The brief mentioned `long_exposure/tools/promise_check.py` as out-of-scope; no changes made.
- The brief prohibited touching base manifests or other branches' shards; all writes stayed within Branch C's scope (plan_of_record.md and cycle-1 base files were only edited for the plan-of-record documentation entries — cycle-2 precedent).

## Handoff notes for cycle 4

- **Cycle-4 primary product:** full 45-species deep-verification pass
  using the pilot's refined checklist. Budget ~15 hours single-researcher.
- **Cycle-4 discrepancy backlog:** the four `_deferred/*` events from
  this pilot land in cycle 4's queue. Two are mechanical field-swaps
  (`_deferred/hala-gallaher-title-fix`, `_deferred/alula-conservation-status-refresh`)
  and can be batched with the deep-verification pass. Two require
  narrative rewrites or primary-source fetches
  (`_deferred/hala-uncertainty-rewrite`, `_deferred/christmas-berry-noxious-weed-source`).
- **RARE-tier count now at 11**; the brief's `10+` target is cleared with
  margin. Cycle 4 does not need to add more RARE species unless the
  deep-verification pass invalidates one (e.g., if a rare-tier species'
  scope-fit fails on closer inspection).
- **Kokia kauaiensis is SVG-only** — the pattern schiedea-apokremnos
  established works and is now used by two species. Both `image_search_notes:`
  blocks explicitly list the sources checked so a future cycle can
  revisit efficiently.
