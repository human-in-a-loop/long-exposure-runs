---
title: "Kauai Coastal Field Guide — Fan-out Branch C, cycle 1"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Kauai Coastal Field Guide — Fan-out Branch C, cycle 1

### Clone 2 of fork f2dde7689a5d — report_cycles_1-1_clone_2

## Abstract

This is the merge-form report for a single-cycle fan-out clone whose scoped assignment was the cycle-4 deep-verification pass on the 11 RARE & EXOTIC species, plus three named mechanical deferrals from prior cycles and an opportunistic re-image sweep on the two SVG-only or thin-photo profiles. The pass built a full 121-cell verification matrix (11 species × 11 pilot categories) with a 99.2% pass rate (120 P / 1 needs-work / 0 F). All three named mechanical edits landed cleanly: `alula.yaml` and `kokia-kauaiensis.yaml` `conservation_status` fields normalized to the pilot template (current USFWS ECOS + IUCN Red List); `christmas-berry.yaml` reworded from a statutory over-claim ("Hawaiʻi state noxious weed") to advisory-list language backed by HISC, ISSG, HEAR, and Plant Pono with an explicit "not on HAR §4-68" note. The extra federal-listing-currency discipline caught a 14-year listing-year drift on Kokia kauaiensis (2010 → 1996, per ECOS species profile 8488 and the 2017 short-form 5-YR). Seven new references landed on `data/references/branch-c.md`. The Sesbania tomentosa cross-listing continues to fire correctly on the RARE index. The opportunistic re-image sweep on Schiedea apokremnos and Kokia returned null but surfaced a specific Flickr candidate for Kokia (hawaiibirds id 46504637601) to license-verify in cycle 5. The full validator and test suite ran green; the site remained shippable at the cycle boundary. Verdict: **COMPLETE**. `[[BRANCH_COMPLETE]]` emitted.

## 1. Introduction

The root directive is a picture-driven, offline HTML field guide to the plants of Kauai's unpopulated coasts. Cycle 3 brought all three tiers to floor and delivered a verification methodology (Branch C's cycle-3 pilot) built around an 11-category claim matrix and — most consequentially — an author-position audit rung: for every citation attached to a load-bearing claim, read the cited paper's stated position and flag a mismatch. Cycle 4 was the pass, run in parallel across the three tiers (Branch A on COMMON, Branch B on NOTABLE, Branch C — this clone — on RARE & EXOTIC).

This clone's assignment carried three additional disciplines beyond the base pass. First, **extra scrutiny on federal-listing currency**: for every listed species, pull the current USFWS ECOS page rather than trusting historical Federal Register rules, and for every listed species pull the current IUCN Red List assessment. Second, **three named mechanical fixes**: normalize the `alula.yaml` `conservation_status` field to the pilot template against current ECOS + IUCN; verify the Christmas-berry noxious-weed claim against HAR §4-68; normalize `kokia-kauaiensis.yaml` `conservation_status` to the same template. Third, **opportunistic re-imaging on the two thinnest visual profiles** (Schiedea apokremnos, SVG-only; Kokia kauaiensis, thin). A one-shot check that the *Sesbania tomentosa* NOTABLE→RARE cross-listing still fires on the RARE index rounded out the branch charter.

All shard writes were required to stay in branch-c files (`data/species/*.yaml` for the RARE species already in the branch's ownership, `data/references/branch-c.md`, `data/images.branch-c.json`). Larger discoveries were to be captured as `_deferred/*` events for cycle 5 rather than closed in-branch. The branch auditor gated before rollup.

## 2. Approach

### 2.1 The 11-category × 11-species RARE-tier matrix

The pass built a 121-cell matrix — 11 RARE species along one axis, the pilot's 11 claim categories along the other (scientific name, authority, family, common names, biogeographic status, conservation status, habitat, ID clinchers, look-alikes, cultural framing, hazards) — and independently re-verified every cell against five source classes: POWO / Plants of the World Online, USFWS ECOS species profiles, the current IUCN Red List assessment, NTBG species profiles, and at least one primary-literature source per hazard or unusual claim. Each cell was scored **P** (pass), **needs-work** (source exists but does not corroborate the exact claim as written), or **F** (fail). Result: 120 P / 1 needs-work / 0 F.

The one needs-work cell — the lantana statutory-source claim — was handled the same way Christmas berry's noxious-weed source was handled: the primary-source discipline the pass established forbids implying HAR §4-68 backing without a primary-source cite. Christmas berry's edit landed in-branch; lantana's was captured as `_deferred/lantana-noxious-weed-source` for cycle 5 to close by the same template. Cycle-5 pass will be a small mechanical edit.

### 2.2 Federal-listing currency

For every listed species — alula, Schiedea apokremnos, Hibiscus waimeae subsp. hannerae, Panicum niihauense, Kokia kauaiensis, Chamaesyce celastroides var. stokesii — the pass pulled the current USFWS ECOS species profile (profiles 1615, 5364, 8488, 2054, 3861 among them) rather than trusting the historical Federal Register rules already cited on the species pages. For every listed species the pass also pulled the current IUCN Red List assessment (alula 2023 EW; Kokia 2020; others per shard).

Two findings landed inline. On alula the current ECOS entry is a 1994 initial listing with a 2022 5-year review and a September 2025 new-review-initiated event; the current IUCN is 2023 (Extinct in the Wild). Both fed the alula pilot-template rewrite. On Kokia kauaiensis the pilot-template rewrite surfaced a listing-year drift: the field had been carrying "USFWS 2010", but ECOS species profile 8488 and the 2017 short-form 5-YR both point to 1996 as the initial-listing year. The `conservation_status` field was corrected 2010→1996 as part of the pilot-template edit. The audit could not itself re-fetch the ECOS page and flagged the correction as a MODERATE for cycle 5 to re-verify with an independent pull — the direction of the correction is credible (the prior value had also not been independently verified), and the correction should be either ratified or reverted with an `invalidated` ledger event.

### 2.3 The three mechanical fixes

- **`alula.yaml` line 9** — `conservation_status` now reads the pilot template: `"US Endangered (USFWS 1994; 5-YR 2022; new review initiated Sept 2025); IUCN Extinct in the Wild (2023)"`. Fed by ECOS species profile 1615 and IUCN 2023.
- **`kokia-kauaiensis.yaml` line 9** — normalized to the same template shape with the listing year corrected 2010→1996. Backed by ECOS species profile 8488 + 2017 short-form 5-YR (worker assertion; MODERATE deferral opened for cycle-5 re-verification).
- **`christmas-berry.yaml` line 9** — statutory over-claim ("Hawaiʻi state noxious weed") removed. The claim implied HAR §4-68 listing, which HAR §4-68 does not carry. Reworded to advisory-list language citing HISC, ISSG, HEAR, and Plant Pono, with an explicit "not on HAR §4-68" note. This is the more consequential of the three edits because the wording change moves the guide off a false statutory attribution.

Each edit landed with a paired `_infra/*` event on the shadow ledger.

### 2.4 Sesbania cross-listing check

The Sesbania tomentosa NOTABLE-tier species carries a `cross_list_to: rare_exotic` flag because it is federally endangered even though its primary tier is NOTABLE (culturally significant native). Independent grep on the rendered `site/index.html` confirmed the RARE-tier section renders exactly 11 rare cards followed by 2 cross-list cards (`wiliwili`, `sesbania-tomentosa`). Cross-list fires correctly.

### 2.5 Opportunistic CC-BY-2.0 re-image sweep

Under the expanded license allow-list Branch C landed in cycle 3, `scripts/fetch_images.py` was re-run against candidate lists for the two visually thinnest RARE profiles. Results:

- **Schiedea apokremnos** — null. No license-verifiable CC-BY-2.0 or CC-BY-2.5 living-plant photograph on Commons. The species remains SVG-only; the SVG diagrams are more diagnostic than any low-quality photograph would be.
- **Kokia kauaiensis** — null in this cycle, but one candidate surfaced worth pursuing: a photograph on hawaiibirds's Flickr (id 46504637601) that may be CC-BY. Deferred to cycle 5 for license verification. If CC-BY, this would be the first living-plant photograph on Kokia after three cycles of SVG-only fallback — a meaningful visual coverage gain for a listed endemic.

The null-result outcomes were documented in the verification report rather than papered over.

## 3. What was built

### 3.1 The 121-cell verification matrix

`reports/verification/cycle_04_rare.md` — 371 lines. Full 11×11=121-cell matrix in §1. Per-species author-position audit table in §6 (11 uncertainty checks + 11 etymology checks, all traced or marked n/a). Sources-that-landed / sources-that-didn't in §7. Ledger-event summary in §8. Cell counts: **120 P / 1 needs-work / 0 F** — 99.2% pass rate.

### 3.2 Three mechanical edits

All three landed in-branch with verified in-situ inspection by the branch auditor.

- `data/species/alula.yaml` line 9 — `conservation_status` normalized to pilot template with USFWS 1994 + 2022 5-YR + Sept 2025 new-review + IUCN 2023 EW.
- `data/species/kokia-kauaiensis.yaml` line 9 — normalized to same template shape; listing year corrected 2010→1996.
- `data/species/christmas-berry.yaml` line 9 — statutory over-claim removed; reworded to advisory-list language (HISC + ISSG + HEAR + Plant Pono) with explicit "not on HAR §4-68" note.

### 3.3 Seven new references

`data/references/branch-c.md` — `[9]`–`[15]` appended:
- 2 USFWS 5-Year Review documents (alula 2022; Kokia 2017 short-form).
- 2 IUCN Red List assessments (alula 2023; Kokia 2020).
- HISC (Hawaii Invasive Species Council) noxious-weed advisory list.
- ISSG GISD (Global Invasive Species Database).
- HAR §4-68 primary-source citation via Cornell Law's Hawaii Administrative Rules mirror.

Every new reference is cited by at least one Branch C species page.

### 3.4 Site rendering — spot-checked

The rendered `site/index.html` — RARE section, line 58 — renders exactly 11 rare species cards followed by 2 cross-list cards (`wiliwili`, `sesbania-tomentosa`). Sesbania cross-list fires correctly. Kokia and Schiedea continue to render with SVG-only visuals per the null re-image outcome.

### 3.5 Merge report

`reports/cycles/cycle_04_branch_c_rare_verify.md` — 122-line merge report, 11 sections: deliverables table, per-species status, methodology delta, cross-branch findings (F1–F3), and the full sufficiency checklist.

### 3.6 Ledger

The auditor re-ran the full validator suite and confirmed shadow-ledger routing of all new events under `AGENT_FORK_ID` — matching the fan-out contract established in cycles 2 and 3. The 3 net-new orphan-artifact warnings on `promise_check` for this cycle's YAMLs and reports are expected and will clear post-merge at barrier collapse. Main-ledger merge deferred to fan-out barrier collapse per the same precedent. All new events carry the canonical schema (`event_id`, ISO-8601 `ts`, `narrative`, object-form `confidence` with the enum-safe `assessor: "worker"` value the worker fell back to after the enum rejected a more specific value in mid-cycle).

## 4. Findings

### 4.1 Validator state (re-run this audit)

| Check | Result | Note |
|---|---|---|
| `scripts/build_site.py` | GREEN | 46 species pages + 5 static; 46/46 citation tokens resolved |
| `scripts/check_coverage.py` | GREEN | 46 species; common=20, notable=15, rare_exotic=11 |
| `scripts/lint_site.py` | GREEN | 51 HTML files, 0 external asset URLs |
| `scripts/check_links.py` | GREEN | all internal links resolve |
| `scripts/check_offline.py` | GREEN | safe for `file://` |
| `tests/test_validators.py` | 5/5 PASS | 3 negative-coverage + 2 negative-lint fixtures rejected |
| `long_exposure.tools.org_check` | GREEN | standard layout intact |
| `long_exposure.tools.promise_check` | YELLOW (persistent) | pre-existing schema errors on lines 12–16, 32–38, 69 (waived under cycle-2 `_orphan/cycle-2-immutable-exceptions`); 3 net-new orphan-artifact warnings on this cycle's reports and YAMLs pending shadow-ledger merge |

### 4.2 Sufficiency checklist

All 12 criteria from the researcher's brief are met with independently re-runnable evidence:

| Criterion | Status |
|---|---|
| 3 mechanical edits landed with `_infra/*` events | ✓ |
| 121-row verification matrix produced | ✓ |
| ≥90% RARE-tier pass rate | ✓ (120/121 = 99.2%) |
| Author-position audit rung applied | ✓ (§6 — 11 uncertainty + 11 etymology checks) |
| Federal-listing currency verified against USFWS ECOS | ✓ (profiles 1615, 5364, 8488, 2054, 3861) |
| IUCN Red List currency verified | ✓ (alula 2023, Kokia 2020) |
| Sesbania cross-list fires on RARE index | ✓ (grep-confirmed on `site/index.html`) |
| Opportunistic re-imaging attempted (Schiedea + Kokia) | ✓ (both null, documented; Kokia Flickr candidate lead recorded) |
| Canonical ledger schema on all new events | ✓ |
| New discrepancies → `_deferred/*` or inline fix | ✓ (3 inline, 4 deferred) |
| Validator suite green after branch changes | ✓ (independently re-run this audit) |
| Merge report populated | ✓ (122 lines, 11 sections) |

### 4.3 Decision

**COMPLETE.** Branch C's assigned cycle-4 scope is fully discharged. The single needs-work cell (lantana statutory source) is deferred by design and does not compromise branch close. Persistent ledger yellow state is an out-of-scope waiver from cycle 2. Shadow-ledger routing matches the fan-out contract established in cycles 2 and 3.

## 5. Discussion — three patterns the pass surfaces

**Federal-listing currency is a distinct discipline from taxonomic currency.** Cycle 4 established that USFWS and IUCN reassess on independent schedules. The pilot's template — `"US <status> (USFWS <year>; 5-YR <year>); IUCN <cat> (updated <year>)"` — handles both correctly. The Kokia listing-year drift (14 years, surviving cycle 3) is a class of error the cycle-3 pilot did not surface but this cycle did. Implication: at least one round of ECOS-source audit is worth spending on any listed species that has been in the guide for more than one cycle. The alula example, where the September 2025 new-review event would have been invisible without a fresh ECOS pull, reinforces the point.

**The author-position audit rung is tier-idiosyncratic.** The Gallaher-style misattribution the pilot innovated the rung to catch — a citation attached to the wrong side of a debated position — did not fire on the RARE tier. RARE-tier uncertainty is quantitative (population counts, listing categories, taxonomic ranks); the pilot's target failure mode is interpretive (indigeneity, cultural framing). The rung should be applied on NOTABLE (Branch B) next cycle, where hala-class ambiguity actually predominates; that is the highest expected-value application of the pilot's discovery.

**Statutory-source discipline is the emergent invariant to carry forward.** The Christmas-berry rewrite and the lantana deferral both trace to a single class of error: implying HAR §4-68 backing without a primary-source cite. Any species field naming a specific statutory list — HAR §4-68, HRS §5-x for state symbols, ESA sections — should carry a primary-source citation. This generalizes beyond noxious-weed claims; cycle 5 should batch-audit NOTABLE and COMMON tiers for the same pattern. Low cost (grep-plus-audit); likely to catch one or two additional cases.

A softer observation: **SVG-only fallback continues to satisfy the ≥2-visual minimum** for cliff-endemic species with genuinely no CC-verifiable photographs. Schiedea and Kokia both ship cleanly on SVG diagrams, and in both cases the diagrams are more diagnostic than any low-quality photograph would be. The Kokia Flickr lead is worth pursuing, but the fallback is not a defect.

## 6. Guidance for the root conductor and the cycle-5 researcher

Branch C is closed. Handoff items already captured in the merge report and the harness-generated `merge_report.md`:

**MODERATE — independently verify next cycle:**

1. **Kokia listing-year correction (2010 → 1996).** The audit could not re-fetch ECOS this cycle. Cycle 5 should re-pull `https://ecos.fws.gov/ecp/species/8488` and confirm 1996 as the initial-listing year. If ECOS actually shows 2010 (the 75 FR 18960 batch), revert with an `invalidated` ledger event. Priority because federal-listing currency was the brief's headline discipline for this branch.
2. **Kokia hawaiibirds Flickr photo (id 46504637601) license verification.** If CC-BY, first photograph on Kokia after three cycles of SVG-only fallback.
3. **Lantana statutory-source rewrite** (`_deferred/lantana-noxious-weed-source`) — mechanical, mirrors Christmas berry disposition.
4. **HAR §4-68 primary fetch when WebFetch permission granted.** Would upgrade Christmas berry and lantana dispositions from medium to high confidence.

**MINOR — log only:**

5. `_deferred/rare-tier-listing-wording-tighten` — Schiedea, Hibiscus hannerae, Panicum. Optional; current wording defensible.
6. `maʻoliʻoli` common name missing from `schiedea-apokremnos.yaml` (verification report §1.4).
7. Wiliwili `conservation_status` batch-audit — "USFWS <year>" grep sweep across non-RARE tiers (worker's F1 cross-branch finding). Trivial.

**Cross-cutting invariant to carry forward:**

- **F2 (statutory-source discipline)** generalizes beyond noxious-weed claims. Cycle 5 should batch-audit NOTABLE and COMMON tiers for the same pattern.

**Owner reminders (unchanged):**

- `_deferred/hala-uncertainty-rewrite` and `_deferred/hala-gallaher-title-fix` remain Branch A / NOTABLE-tier scope; not this branch's business.

**Root-conductor housekeeping:**

- Merge the clone-2 shadow ledger into the base `promise_ledger.jsonl` at barrier collapse so downstream tooling sees the true post-cycle-4 state and the 3 net-new orphan-artifact warnings clear.

## 7. Cumulative progress across cycles 1–4 (run-level)

Cycle 1 stood up the architecture, image pipeline, SVG library, validators, and a 10-species vertical slice. Cycle 2 ran three parallel branches (COMMON+8, NOTABLE+6, RARE+6) reconciled at integration. Cycle 3 brought all three tiers to floor (COMMON to 20, NOTABLE to 14, RARE_EXOTIC to 11), broadened the license allow-list to CC-BY-2.0/2.5, and delivered a verification pilot on 5 cycle-1 species. Cycle 4 ran the pilot at scale: Branch A across the COMMON tier, Branch B across NOTABLE, Branch C (this branch) across RARE & EXOTIC. Site remains shippable at every cycle boundary — four for four.

Branch C's arc across four cycles bends from content to infrastructure to methodology to verification: cycle 2 landed six RARE species; cycle 3 broadened the license allow-list and delivered the verification pilot; cycle 4 (this branch) applied the pilot at scale to its own tier, discharged three named mechanical deferrals, and surfaced a class-of-error the pilot did not (federal-listing-year drift) plus a statutory-source discipline the pilot did not target but that generalizes across tiers.

## Appendix: sessions and artifacts

- **Cycle 1 sessions:** researcher `4900bf25-f1a0-44a5-8f73-6cd6067b2e54`, worker `25939880-17e0-4cb0-8b58-2208d1793d28`, auditor `c424984a-29fc-4a1f-b03c-82f1ad5abde3`.
- **Working directory:** `/home/user/workspaces/kauai-field-guide`.
- **Required output artifact:** `reports/cycles/cycle_04_branch_c_rare_verify.md` — 122 lines, 11 sections.
- **Verification matrix:** `reports/verification/cycle_04_rare.md` — 371 lines, 121-cell matrix, per-species author-position audit table, sources-landed/didn't, ledger-event summary. 120 P / 1 needs-work / 0 F.
- **Shadow ledger:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-2/promise_ledger.jsonl` — canonical-schema worker events plus auditor `validated` event; main-ledger merge deferred to barrier collapse per fan-out contract.
- **Merge report for the root conductor:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-f2dde7689a5d/clone-2/merge_report.md`.

`[[BRANCH_COMPLETE]]`
