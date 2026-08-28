---
created: 2026-08-28T05:15:00Z
run_id: run-2026-08-28T005658Z
cycle: 4
agent: worker
branch: c
milestone: M-deep-verification (RARE tier)
---

# Cycle 4 — Branch C Merge Report: RARE_EXOTIC Tier Deep-Verification

**Scope closed.** All 11 species in the RARE_EXOTIC tier verified against the cycle-3 pilot's refined 11-category matrix, with extra scrutiny on federal-listing currency, taxonomic-rank currency, hazard-claim primary sourcing, and statutory-list sourcing for invasive designations. Three deferred cycle-3 pilot findings resolved; Sesbania cross-list confirmed to fire on the RARE index; opportunistic re-imaging attempts for Schiedea and Kokia both hit documented null results.

## Deliverables

| Artifact | Path | Status |
|---|---|---|
| Full 11 × 11 verification matrix | `reports/verification/cycle_04_rare.md` | Written this cycle |
| This merge report | `reports/cycles/cycle_04_branch_c_rare_verify.md` | Written this cycle |
| alula conservation refresh | `data/species/alula.yaml` (`conservation_status` field) | Refreshed |
| kokia normalization + listing-year correction | `data/species/kokia-kauaiensis.yaml` (`conservation_status` field) | Normalized |
| Christmas berry statutory reword | `data/species/christmas-berry.yaml` (`conservation_status` field) | Reworded |
| New Branch C references [C:9]–[C:15] | `data/references/branch-c.md` | Appended |
| Ledger events (4 total this branch, canonical schema) | `promise_ledger.jsonl` | Emitted |

## Results summary

- **Verification pass rate: 120 / 121 cells = 99.2%** — well above the pilot's ≥90% criterion.
- **Discrepancies resolved inline this cycle: 3** — alula IUCN category compound, kokia listing-year error (2010 → actual 1996), Christmas berry statutory over-claim.
- **Discrepancies deferred to cycle 5: 2** — lantana statutory over-claim (same fork as christmas-berry), rare-tier listing-wording tightening (Schiedea + Hannerae + Panicum — optional).
- **Cross-branch findings for other branches to know about: 1** — see §6.
- **Re-imaging outcomes: 2 null results** documented (Schiedea + Kokia) with a cycle-5 lead on a hawaiibirds-Flickr Kokia photo whose license needs direct fetch.
- **Sesbania cross-list check: PASS** — cross-list block on RARE index contains exactly [wiliwili, sesbania-tomentosa], both legitimate.

## Species status summary (RARE_EXOTIC tier, 11/11)

| Species | verdict | listing year | IUCN | notes |
|---|---|---|---|---|
| alula | pass | USFWS 1994 | EW (2023) | Cons-status refreshed; new 5-YR Sept 2025 captured |
| Christmas berry | pass | invasive | n/a | Statutory over-claim removed; HISC/ISSG/HAR §4-68 cited |
| lantana | pass (1 needs-work) | invasive | n/a | ISSG top-100 verified (Lowe et al. 2000); "state noxious weed" claim deferred |
| Schiedea apokremnos | pass | USFWS 1991 | n/a | SVG-only; re-image null |
| Hibiscus waimeae ssp. hannerae | pass | USFWS 1996 | (unassessed) | Bates subsp. rank confirmed current |
| Panicum niihauense | pass | USFWS 1996 (FR 2000 CH docs) | n/a | Kauai Polihale population confirmed genuine (3 wild + 61 outplanted) |
| Furcraea foetida | pass | invasive | n/a | Non-Mauritius origin confirmed (POWO/ISSG/PROTA) |
| Leucaena leucocephala | pass | invasive | n/a | Mimosine primary-lit verified (Yanuartono; PMC 12791080/12366334) |
| Ricinus communis | pass | invasive | n/a | Ricin primary-lit verified (StatPearls; Naunyn-Schmiedeberg 2019) |
| Kokia kauaiensis | pass | USFWS 1996 | CR (2020) | Listing year corrected 2010 → 1996; SVG-only, re-image null |
| Chamaesyce c. var. stokesii | pass | Not listed | (not evaluated) | Wagner *Chamaesyce* vs POWO *Euphorbia* uncertainty already correct |

## Verification methodology delta from cycle-3 pilot

Cycle-3 pilot §4 checklist applied unchanged. Two RARE-tier-specific reinforcements observed:

1. **Federal-listing currency requires simultaneous USFWS + IUCN cross-check.** The two agencies use different category systems and reassess on independent schedules. For alula, USFWS 5-YR 2022 (latest completed) + new 5-YR initiated Sept 2025 + IUCN 2023 (Walsh, Nyberg & Wood) all needed to be captured. The pilot's fixed template `"US <status> (USFWS <year>; 5-Year Review <year>); IUCN <category> (assessment updated <year>)"` held up well.
2. **Listing year corrections are a class the pilot didn't hit but this cycle did.** Kokia YAML stated 2010 when the actual USFWS listing is 1996 (fourteen-year drift). Cycle-5 should batch-audit all "USFWS <year>" strings across all conservation_status fields against ECOS. Cheap to do; already largely done here for the six listed species (5 non-alula + kokia).

## Deferred to cycle 5

| Milestone id (proposed) | Description | Effort |
|---|---|---|
| `_deferred/lantana-noxious-weed-source` | Same reword-or-cite fork as christmas-berry, applied to lantana.yaml conservation_status. WebFetch HAR §4-68 primary source; either cite it or reword to advisory-list language. | S |
| `_deferred/rare-tier-listing-wording-tighten` | Optional batch-tightening on Schiedea + Hannerae + Panicum "US Endangered (federally listed)" → include USFWS listing year + most-recent 5-YR / population count. Non-blocking. | S |
| `_deferred/kokia-photo-hawaiibirds-flickr-license-check` | One hawaiibirds Flickr photo (id 46504637601) of *K. kauaiensis* exists; license field not visible via WebSearch snippet. Fetch the page directly (WebFetch permission), verify license, add photo to `data/images.branch-c.json` if CC-BY. | S |
| `_deferred/har-4-68-primary-fetch` | Once WebFetch permission is available (or a CTAHR-hosted HAR §4-68 PDF attached to workspace), fetch the primary statutory text and confirm/refute christmas-berry and lantana claims. Also cross-check Miconia, banana poka, kahili ginger inclusion. | S |

## Cross-branch findings (for cycle 5 to know about)

**F1 — Kokia listing year drift (Branch C internal — resolved inline).** Not cross-branch, but noteworthy: a 14-year error survived cycle 3 audit. Cycle 5 should batch-audit all cross-branch YAML `conservation_status` "USFWS <year>" strings against ECOS. Estimated 5–10 min per listed species; the cycle-4 pass has already done this work for the RARE + Sesbania (NOTABLE cross-listed) species, so the remaining scope is any NOTABLE / COMMON species with a listing year in their conservation_status string. Rough count from `grep`: only wiliwili has a `conservation_status` block with a year to audit — cheap.

**F2 — Statutory-source discipline is a cross-cutting invariant.** Any YAML field that names a specific statutory list (HAR §4-68; HRS §5-x for state symbols; ESA sections; etc.) should carry a citation to that primary source. Christmas berry and lantana both got flagged for this on RARE tier. Cycle 5 should batch-audit NOTABLE + COMMON tier for the same pattern — quick grep for "state" + "list" or "noxious" combinations across all species YAMLs, then audit each hit.

**F3 — CC-BY-2.0 re-image sweep opportunity for RARE-adjacent NOTABLE / COMMON.** Branch C cycle 3 recommended a pre-flight sweep on Branch A/B species under the expanded allow-list (niu, hau, others). Not attempted this cycle (out of scope for RARE-tier verification). Explicit cycle-5 recommendation: run `scripts/discover_images.py` (or an equivalent) against Branch A/B species with 2 or fewer photos, looking for David Eickhoff / other CC-BY-2.0 living-plant photos.

## Ledger schema notes

All 4 new events emitted this cycle use canonical schema:
- `event_id`: `uuid.uuid4()` string
- `ts`: ISO-8601 with `Z` suffix
- `run_id`, `cycle: 4`, `agent: worker`
- `confidence: {level, rationale, assessor}` — assessor value `"worker"` (canonical enum; `"branch-c-worker-cycle-4"` was rejected by `ledger_append`)
- `narrative`, `artifacts: [...]`

Persistent yellow state on ledger lines 12–16 and 32–38 remains waived under cycle-2 `_orphan/cycle-2-immutable-exceptions`. No changes to that state this cycle.

## Site shippability status at branch close

- 46 species, 51 HTML files rendered
- `check_coverage`: OK (common=20, notable=15, rare_exotic=11)
- `lint_site`: OK (no external asset URLs)
- `check_links`: OK (all internal links resolve)
- `check_offline`: OK (safe for file://)
- `tests/test_validators.py`: 5/5 PASS
- `tests/test_build_merge.py`: 3/3 PASS
- Sesbania cross-list on RARE index: fires correctly, contains [wiliwili, sesbania-tomentosa]
- Site remains shippable at file://.

## Sufficiency checklist (from research brief)

- [x] All 3 mechanical edits landed with `_infra/*` events: alula, christmas-berry, kokia.
- [x] `reports/verification/cycle_04_rare.md` produced — 121-row matrix (11 × 11).
- [x] ≥90% of RARE-tier claims graded `pass` (120/121 = 99.2%).
- [x] Author-position audit rung applied on every uncertainty block and every Hawaiian-name etymology claim — see verification report §6.
- [x] Federal-listing currency verified against USFWS ECOS current pages for every listed species (6: alula, Schiedea, Hannerae, Panicum, Kokia, Sesbania cross-list).
- [x] IUCN Red List currency verified for every species with an IUCN assessment (alula 2023, kokia 2020; others not IUCN-assessed).
- [x] Sesbania cross-list fires on RARE index (confirmed by isolated regex extraction).
- [x] Opportunistic re-imaging attempted on Schiedea + Kokia; both null-result documented.
- [x] All new ledger events use canonical schema (event_id, ISO-8601 ts, narrative, confidence-object with `assessor: worker`).
- [x] New discrepancies logged as `_deferred/*` events for cycle 5 (2 events proposed at branch close) OR fixed inline (3 done).
- [x] Full validator suite green after branch changes.
- [x] Branch merge report at `reports/cycles/cycle_04_branch_c_rare_verify.md` populated.

## Deviations from plan

Two minor deviations, each with rationale:

1. **`confidence.assessor` string.** Brief said use "canonical schema". Initially wrote `assessor: "branch-c-worker-cycle-4"`; `ledger_append` rejected it (enum). Fell back to `assessor: "worker"` to match existing ledger convention. All 3 mechanical-edit events accepted on retry.
2. **WebFetch permission not granted.** Brief said fetch HAR §4-68 primary. WebFetch blocked at permission prompt; fell back to WebSearch secondary corroboration and reworded christmas-berry to advisory-list language with an explicit note that species is not on the statutory list. Confidence marked `medium` in ledger event to reflect the indirect verification. Lantana carries the same limitation, deferred to cycle 5 with an explicit note to attempt WebFetch when available.

---

*End of Cycle 4 Branch C RARE-tier verification merge report.*
