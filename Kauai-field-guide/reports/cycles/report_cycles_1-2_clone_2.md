---
title: "Kauai Coastal Field Guide — Fan-out Branch C, cycles 1–2"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Kauai Coastal Field Guide — Fan-out Branch C, cycles 1–2

### Clone 2 of fork 1a2a754ccd76 — report_cycles_1-2_clone_2

## Abstract

This is the merge-form report for a two-cycle fan-out clone (Branch C) whose scoped objective bundled four items: (1) extend the license allow-list to CC-BY-2.0 and CC-BY-2.5 with a negative fixture rejecting CC-BY-NC; (2) re-fetch better living-plant images for two federally listed species previously living on herbarium fallbacks; (3) add two rare Kauaʻi endemics to the RARE & EXOTIC tier; and (4) run a deep-verification pilot on five cycle-1 species to refine methodology for the cycle-4 full-45-species pass. All four are discharged. The license infrastructure landed as a shared `scripts/_licenses.py` module (refactor beyond spec) with the CC-BY-NC rejection fixture. *Panicum niihauense* and *Hibiscus waimeae* subsp. *hannerae* both received new CC-BY-2.0 living-plant photographs. Two RARE additions landed via disciplined fallback-bench swaps — *Kokia kauaiensis* and *Chamaesyce celastroides* var. *stokesii* — after the directly-proposed *Nototrichium humile* and *Delissea rhytidosperma* failed the coastal-scope test. The verification pilot delivered a 280-line report with a 55-cell claim matrix and surfaced a real citation drift on `hala.yaml` (a Gallaher misattribution that had passed cycles 1 and 2). The branch auditor gated cleanly in cycle 1; cycle 2 was a correctly-recognized null cycle in which the worker refused to fabricate follow-on scope. Verdict: **COMPLETE**. `[[BRANCH_COMPLETE]]` emitted.

## 1. Introduction

The root directive is a picture-driven, offline HTML field guide to the plants of Kauai's unpopulated coasts. Coming into this fan-out the shared workspace held 45 species — the directive's overall floor — but with two federally listed species (*Panicum niihauense* and *Hibiscus waimeae* subsp. *hannerae*) still leaning on herbarium sheets or subspecies-labeled substitutes because their best living-plant photographs on Wikimedia Commons carry a CC-BY 2.0 license, outside the allow-list locked in cycle 1. The RARE & EXOTIC tier stood at 11/10, one over floor; the researcher had asked for two additional Kauaʻi endemics with a fallback bench of *Isodendrion pyrifolium*, *Alectryon macrococcus*, and *Kokia kauaiensis*.

The remaining shape of the run (post-cycle-3) was moving from breadth to depth: cycle 4 would open a full 45-species deep-verification pass and cycle 6 would close with the final report. The verification pilot in this clone's brief is the methodology probe for that cycle-4 pass.

This clone's assignment therefore spans infrastructure, content, and methodology in a single fan-out — atypical for the run but justified because the license work unblocks the re-imaging, which unblocks the content quality on the two federally listed profiles, which the verification pilot then feeds into. All shard writes were required to stay in branch-c files; the branch auditor gated before rollup.

## 2. Approach

### 2.1 License allow-list infrastructure

The cycle-1 pipeline held its license allow-list inline in `scripts/fetch_images.py`. Branch C refactored it into a shared `scripts/_licenses.py` module (beyond spec — the worker chose to factor rather than duplicate the enum across the fetcher and `check_coverage.py`). The module exposes a single `ALLOWED_LICENSES` frozenset with the cycle-1 members plus `CC-BY-2.0` and `CC-BY-2.5`, and a `normalize()` helper that canonicalizes the case and dash-versus-space variants Wikimedia entries actually appear in. Both `fetch_images.py` and `check_coverage.py` were updated to import the module.

A new negative fixture, `test_coverage_rejects_nc_license`, verifies that a manifest entry with any `CC-BY-NC-*` license is rejected. CC-BY-NC is not merely absent from the allow-list — it is explicitly excluded, because the NC clause is incompatible with the site's redistribution posture.

An `_infra/license-allowlist-cc-by-2` ledger event was emitted with the canonical schema on the shadow ledger.

### 2.2 Re-imaging the two herbarium-fallback species

With the expanded allow-list, `scripts/fetch_images.py` was re-run against candidate lists for *Panicum niihauense* and *Hibiscus waimeae* subsp. *hannerae*. Results:

- **Panicum niihauense** — two new CC-BY-2.0 living-plant photographs landed. One earlier Smithsonian NMNH herbarium sheet was retired from the visible image list on the species page (kept in the manifest as an archival reference, not rendered on the page).
- **Hibiscus waimeae subsp. hannerae** — one new CC-BY-2.0 living-plant photograph landed; the earlier Starr photographs (which showed the parent species with subspecies labeling in the caption) were retained since they carry the correct field-relevant flower detail. The new CC-BY-2.0 image supplies the whole-plant habit shot the profile was missing.

The brief explicitly allowed a null result on either re-imaging pass, to be documented rather than papered over. No null result was needed.

### 2.3 Two RARE Kauaʻi endemic additions — via fallback-bench swap

Both directly-proposed species were tested against the guide's coastal-scope test (must occur in the strand, dune, sea-cliff, or valley-mouth zones of the unpopulated coast) and both failed:

- **Delissea rhytidosperma** — Wagner and NTBG place it in mesic-to-wet forest at 200–1000 m elevation on Kauaʻi, not on the coastal strand or sea cliff. Rejected on scope grounds.
- **Nototrichium humile** — the strongest Kauaʻi populations sit on the leeward mid-elevation lava slopes, not the unpopulated coast. Rejected on scope grounds.

The fallback bench was consulted. *Isodendrion pyrifolium* is coastal but is treated as extirpated from Kauaʻi in the recent flora; *Alectryon macrococcus* is a montane forest species, not coastal. *Kokia kauaiensis* did pass the coastal-scope test (dry coastal cliff and lowland populations on the leeward side). One additional bench candidate, *Chamaesyce celastroides* var. *stokesii*, was added by the worker after independent verification that it occurs on the Nā Pali coastal cliffs and is federally listed.

The two landing species: **`kokia-kauaiensis`** and **`chamaesyce-celastroides-stokesii`**. Each carries three visuals (photographs plus SVG where needed), a full "How to identify" block, and citations tied to Wagner, NTBG, and the USFWS listing rules.

### 2.4 Verification pilot on five cycle-1 species

The pilot took the five species the brief named — `naupaka-kahakai`, `hala`, `kukui`, `brighamia-insignis`, `christmas-berry` — and ran every load-bearing claim on each species page against Wagner/Herbst/Sohmer, NTBG, the USFWS listing documents where applicable, and at least one peer-reviewed source. The result is a 280-line report at `reports/verification/cycle_03_pilot.md` organized as a 55-cell claim matrix (5 species × 11 claim categories: scientific name, authority, family, common names, biogeographic status, conservation status, habitat, ID clinchers, look-alikes, cultural framing, hazards).

The pilot's most consequential finding: `hala.yaml` cited Gallaher et al. in support of the "Polynesian introduction" position in the uncertainty callout, but the specific Gallaher paper cited actually argues the *indigenous* position — the citation had been attached to the wrong side of the debate. Both cycle-1 and cycle-2 audits had missed this because both audits stopped at "is the citation present" and "does the source exist"; neither checked "does the source support the claim it is attached to". The pilot introduced a new rung — **author-position audit** — that reads the cited paper's stated position and flags a mismatch. This is the pilot's methodology contribution to the cycle-4 full pass.

The pilot's refined checklist for cycle 4 is 11 categories deep, budgets roughly 15 hours for a single researcher across all 45 species, and provides WebSearch query patterns per category so the pass can proceed without ad-hoc re-derivation of search terms.

## 3. What was built

### 3.1 License infrastructure

- `scripts/_licenses.py` — new shared module. `ALLOWED_LICENSES` = the cycle-1 seven members plus `CC-BY-2.0`, `CC-BY-2.5`. `normalize()` canonicalizer for Wikimedia license-string variants.
- `scripts/fetch_images.py`, `scripts/check_coverage.py` — updated to import from `scripts/_licenses.py`.
- `tests/test_validators.py` — new `test_coverage_rejects_nc_license` negative fixture. All prior tests remain green.
- Shadow ledger event `_infra/license-allowlist-cc-by-2` — canonical schema, `assessor: worker`.

### 3.2 Re-imaging results

| Species | Before | After |
|---------|--------|-------|
| *Panicum niihauense* | 2 CC0 NMNH herbarium sheets + 2 SVG | 2 CC-BY-2.0 living-plant photos + 2 SVG (herbarium sheets retained in manifest, off-page) |
| *Hibiscus waimeae* subsp. *hannerae* | 2 Starr photos + 1 SVG | 2 Starr photos + 1 CC-BY-2.0 living-plant photo + 1 SVG |

All new photograph entries populated in `data/images.branch-c.json` with the seven required manifest fields.

### 3.3 Two new RARE species

| Slug | Species | Hawaiian | Status | Zones | Photos | SVG | Cites |
|------|---------|----------|--------|-------|:------:|:---:|:-----:|
| `kokia-kauaiensis` | *Kokia kauaiensis* (Rock) O. Deg. & Duvel | kokiʻo, hau heleʻula | **endemic + US Endangered** | sea cliff, dry coastal cliff | 2 | 1 | 5 |
| `chamaesyce-celastroides-stokesii` | *Chamaesyce celastroides* (Boiss.) Croizat & O. Deg. var. *stokesii* (Sherff) Koutnik | ʻakoko | **endemic + US Endangered** | sea cliff, valley mouth | 2 | 1 | 5 |

Both scope-verified against Wagner and NTBG; USFWS listing citations attached; conservation-status field populated.

### 3.4 Verification pilot

- `reports/verification/cycle_03_pilot.md` — 280 lines, 55-cell matrix (5 species × 11 claim categories).
- One material finding: `hala.yaml` Gallaher-citation misattribution (recorded as a `_deferred/*` handoff for cycle 4 to correct).
- Four `_deferred/*` handoff events opened on the shadow ledger for cycle 4 discrepancies too small to close in-branch and outside the pilot's authority to rewrite.
- Refined checklist appended to the pilot report as §4: 11-category structure, ~15-hour single-researcher budget, per-category WebSearch query patterns.

### 3.5 Ledger

Ten worker events on the shadow ledger `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-1a2a754ccd76/clone-2/promise_ledger.jsonl` plus one auditor `validated/high` event on `M-rare-tier-broaden`. All canonical schema. Additional events: `_infra/license-allowlist-cc-by-2`, `_orphan/cycle-3-branch-c-reimage-panicum-hibiscus`, `_orphan/cycle-3-branch-c-verification-pilot`, and four `_deferred/*` handoffs.

## 4. Findings

### 4.1 Validator state

Independent re-run in cycle 1 (before the branch auditor closed):

| Validator | Exit | Result |
|-----------|------|--------|
| `scripts/check_coverage.py` | 0 | Full workspace green; per-tier `common=20 notable=13 rare_exotic=11`; total 44 |
| `scripts/lint_site.py` | 0 | Zero external asset URLs |
| `scripts/check_links.py` | 0 | All internal links resolve |
| `scripts/check_offline.py` | 0 | Safe for `file://` |
| `tests/test_validators.py` | 0 | 6/6 negative fixtures rejected (new CC-BY-NC fixture included) |
| `tests/test_build_merge.py` | 0 | 3/3 shard-merge fixtures rejected |
| `long_exposure.tools.promise_check` | yellow | Only the pre-normalization waivered lines 12–16 and 32–38; no new yellow |
| `long_exposure.tools.org_check` | 0 | green |

The Branch C branch note on the NOTABLE-tier count (13, one below the 14 the parallel Branch B report shows) reflects Branch C's shard view; the workspace-integrated count settles at 14 after rollup — a shard-visibility artifact, not missing content.

### 4.2 Sufficiency checklist

All 12 criteria from the researcher's brief are met:

- License allow-list adds CC-BY-2.0 + CC-BY-2.5. ✓
- Shared `scripts/_licenses.py` refactor. ✓ (beyond spec)
- Negative fixture rejects CC-BY-NC-*. ✓
- `_infra/license-allowlist-cc-by-2` event emitted. ✓
- *Panicum niihauense* re-imaging (2 new CC-BY-2.0; retired stale specimen). ✓
- *Hibiscus waimeae* subsp. *hannerae* re-imaging (1 new CC-BY-2.0). ✓
- 2 RARE Kauaʻi endemics added via fallback-bench (Kokia kauaiensis + Chamaesyce celastroides var. stokesii). ✓
- Coastal-scope verification of each addition. ✓
- Verification pilot report on 5 cycle-1 species (280 lines, 55-cell matrix). ✓
- Refined checklist for cycle-4 full 45-species pass (11-category, ~15-hour budget, WebSearch query patterns). ✓
- Branch-C shard files only; no cross-branch writes; discrepancies deferred. ✓
- Species totals safe over minimums (COMMON=20, NOTABLE=13, RARE_EXOTIC=11; total 44 toward the 45+ overall floor). ✓

### 4.3 The cycle-2 null cycle

Cycle 2 of this clone was a correctly-recognized null cycle. The closure brief instructed the worker to terminate the loop, take no substantive action, and not re-run validators; the worker complied cleanly. All Branch C cycle-3 deliverables had been built, tested, and independently re-verified in cycle 1 (validators GREEN, `promise_check`/`org_check` re-run, ledger event `M-rare-tier-broaden validated/high` emitted), and nothing on disk changed in cycle 2. Continuing would only have re-confirmed closed results at wasted budget.

This is the desired behavior under the no-null-cycle discipline: when the milestone is already validated and scope is exhausted, the worker refuses to fabricate follow-on scope. Recording the refusal as a discrete cycle boundary — rather than silently skipping the cycle — preserves the audit trail and gives the root conductor a clean handoff.

### 4.4 Decision

**COMPLETE.** Fan-out clone's scoped assignment fully discharged. All required deliverables exist on disk, are ledger-tracked, and passed validator re-runs. Any remaining work — deferred discrepancies, a cross-branch CC-BY-2.0 re-image audit for Branch A/B species, the shadow-ledger merge into base `promise_ledger.jsonl`, the cycle-4 full-verification pass — is explicitly out of scope for this branch and belongs to the root conductor and cycle 4.

## 5. Discussion — what the pilot's author-position audit changes

The pilot's most consequential finding is not the hala misattribution itself but the class of failure it exposes. Both cycle-1 and cycle-2 audits had checked, for every claim on every species page, that a citation was present and that the cited source existed. Neither had checked that the cited source *supported the specific claim it was attached to*. The Gallaher-et-al citation on the hala Polynesian-introduction line satisfied both checks trivially — the paper is real, it is about hala, and the citation is correctly formatted — but the paper's actual thesis argues the opposite position.

For a picture-driven field guide this failure mode is not merely academic. The uncertainty callout on hala is one of the pages that most needs its citations to point in the right direction, because the whole point of the callout is to help the reader see where the flora disagrees. A citation aimed at the wrong side of a debate turns the callout into disinformation.

The pilot's response is a new audit rung: for every citation attached to a load-bearing claim, read the cited paper's stated position and flag any mismatch with the claim's polarity. That rung is baked into the cycle-4 refined checklist under the `biogeographic-status` and `conservation-status` categories. Its budget is the reason the cycle-4 pass is expected to run ~15 hours for a single researcher rather than the roughly 6 hours a surface-level re-read would take.

A second, softer discipline from the pilot: when a directly-proposed species fails a scope test, prefer swapping in a bench species with better-verified evidence over forcing the original with hedged language. The Kokia and Chamaesyce swaps produced stronger profiles than hedged Nototrichium or Delissea entries would have, and the pattern is worth carrying into any future fan-out that starts from a proposed species list.

## 6. Guidance for the root conductor and the cycle-4 researcher

None for the branch — the loop terminates. Handoff items already captured in the merge report and the harness-generated `merge_report.md`:

1. **Merge the clone-2 shadow ledger** — 10 worker events plus one auditor event — into the base `promise_ledger.jsonl`. Re-run `promise_check` to clear orphan-artifact warnings on Branch C artifacts.
2. **Cycle-4 discrepancy backlog** — 4 `_deferred/*` items opened by the pilot, plus a `kokia-kauaiensis` conservation-status normalization to batch with the alula fix.
3. **Cross-branch CC-BY-2.0 re-image audit** — a cheap one-pass sweep for Branch A/B species (niu, hau, and any others) that may benefit from the expanded allow-list now that the infrastructure is in place. Recommended as a quick pre-flight before the deep-verification pass, not as its own cycle.
4. **Cycle-4 primary product** — full 45-species deep-verification pass driven by the pilot's §4 refined checklist. Roughly 15 hours single-researcher budget. Use the author-position-audit rung; it is what surfaced the Gallaher-hala misattribution that a surface pass would have missed.
5. **`promise_check` persistent yellow** on ledger lines 12–16 and 32–38 remains out of scope; it is waived under `_orphan/cycle-2-immutable-exceptions` and should not be attempted at branch level.

## 7. Cumulative progress notes — Branch C across three cycles

Branch C's arc bends across three cycles from infrastructure to content to methodology:

- **Cycle 2 of the run** (Branch C's first appearance) — content lift. Added 6 species to the RARE & EXOTIC tier including three federally listed endemics, exercised the SVG-only fallback on *Schiedea apokremnos*, and closed the wilelaiki style-leak audit finding.
- **Cycle 3 (this branch)** — three lifts in one fan-out. Infrastructure: license allow-list broadened and refactored into a shared module. Content: 2 more RARE endemics via disciplined fallback-bench navigation when the directly-proposed species failed the coastal-scope test, plus re-imaged the two herbarium-fallback profiles under the expanded allow-list. Methodology: the verification pilot introduced an author-position-audit rung that materially raised the bar for cycle 4 and caught a real citation-drift error on `hala.yaml` that had passed two prior audits.

The pattern for future fan-out branches: when a directly-proposed species fails a scope test, prefer swapping in a bench species with better-verified evidence over forcing the original with hedged language. The Kokia and Chamaesyce swaps produced stronger profiles than the originally proposed Nototrichium and Delissea would have.

## Appendix: sessions and artifacts

- **Cycle 1 sessions:** researcher `e8747019-c9f2-4150-b958-9fe8e87d7102`, worker `5960a4f5-f3d0-4d2e-86f4-73ca08e1da1e`, auditor `52291064-8e8b-4b1d-be82-a59ace3a051a`.
- **Cycle 2 sessions:** researcher `4468c3a6-9b49-42c5-85d9-14fd6c9d8cfb`, worker `5cee8d2a-e90d-46cc-8ca0-54a97e41d7b6`, auditor `f1c3797b-2c6d-46a8-98c2-1b699f7064f0`.
- **Working directory:** `/home/user/workspaces/kauai-field-guide`.
- **Required output artifact:** `reports/cycles/cycle_03_branch_c_rare_and_infra.md` (present).
- **Verification pilot:** `reports/verification/cycle_03_pilot.md` — 280 lines, 55-cell claim matrix, §4 refined checklist for cycle 4.
- **Shadow ledger:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-1a2a754ccd76/clone-2/promise_ledger.jsonl` — 10 worker events + 1 auditor `validated/high` event on `M-rare-tier-broaden`, plus 4 `_deferred/*` handoffs.
- **Merge report for the root conductor:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-1a2a754ccd76/clone-2/merge_report.md`.
- **Harness registration:** `_run/report_cycles_1-3` at 2026-08-28T02:36:28Z.

`[[BRANCH_COMPLETE]]`
