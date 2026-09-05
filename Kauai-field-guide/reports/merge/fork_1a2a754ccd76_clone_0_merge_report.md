---
fork_id: "1a2a754ccd76"
clone_k: 0
cycle_range: "cycles 1-1 [merge]"
deliverable_path: "reports/cycles/cycle_03_branch_a_common.md"
deliverable_exists: true
verdict: "unknown"
generated_at: "2026-08-28T03:16:22.060755+00:00"
---
# Kauai Coastal Field Guide — Fan-out Branch A, cycle 3 [merge]
### Clone 0 of fork 1a2a754ccd76 — report_cycles_1-1_clone_0

## Abstract

This is the merge-form report for a single-cycle fan-out clone whose scoped objective was to extend the COMMON tier of the Kauai coastal field guide by eight named indigenous species, from 12 to 20, hitting the directive's floor for that tier. All eight target species landed with three license-verified photographs each, complete "How to identify" blocks, bidirectional look-alike cross-references to two prior common-tier species, and family-placement notes covering the two APG-versus-Wagner discrepancies the brief flagged. A cross-branch total of **45/45 species** is now on the site, meeting the directive's overall species-count floor. Every workspace-wide validator ran green at cycle close. One MODERATE finding — literal HTML markup embedded in the *Cassytha* hazards field, which the build script HTML-escapes at render time — was found and fixed in-audit. The branch auditor gated and the clone closed with verdict **VALIDATED**. `[[BRANCH_COMPLETE]]` was emitted for the root conductor.

## 1. Introduction

The root directive is a picture-driven, offline HTML field guide to the plants of Kauai's unpopulated coasts, tiered as COMMON / NOTABLE / RARE & EXOTIC. At the start of this fan-out the shared workspace held 30 species (12 common, 9 notable, 9 rare & exotic) with a locked data-driven pipeline, a license-verify-closed image path, and a sharded-manifest scheme that lets parallel clones write into per-branch image and reference files (`data/images.branch-a.json`, `data/references/branch-a.md`) without contending with one another.

This clone's scoped assignment was Branch A cycle 3: add eight named indigenous coastal common-tier species — *Chenopodium oahuense*, *Heliotropium anomalum* var. *argenteum*, *Sesuvium portulacastrum*, *Waltheria indica*, *Portulaca lutea*, *Cassytha filiformis*, *Cyperus polystachyos*, *Ipomoea imperati* — each with at least two Starr/Wikimedia photographs, correct authority citations, look-alike cross-references, family-placement notes on the Wagner-versus-APG-IV drift for two of them, prominent hazards placement for *Cassytha*, and canonical-schema ledger events written to the shadow ledger for the fork. All shard writes were required to stay in the branch-a files; the branch auditor gated before rollup.

## 2. Approach

The cycle used the pipeline that cycle 1 stood up and cycle 2 hardened: eight new YAML species records under `data/species/`, twenty-four new photograph entries in `data/images.branch-a.json`, five new references appended to `data/references/branch-a.md` as tokens `A:10`–`A:14`, and a canonical-schema worker event per species written to the shadow ledger at `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-1a2a754ccd76/clone-0/promise_ledger.jsonl`.

Two structural moves are worth naming:

- A new optional `taxonomic_notes:` field on the species schema records the Wagner-versus-APG-IV family placement for *Chenopodium oahuense* (Wagner Chenopodiaceae → APG-IV Amaranthaceae) and *Waltheria indica* (Wagner Sterculiaceae → APG-IV Malvaceae). The field is optional so `check_coverage.py` neither requires nor forbids it; the rendered page shows the drift as a sourced callout rather than picking one placement silently. Milo remains in Malvaceae so the family label for *Thespesia* and the new *Waltheria* is internally consistent.
- Bidirectional look-alike edits landed on the two paired species already on the site: `pohuehue.yaml` gained *Ipomoea imperati* (hunakai) as a look-alike; `fimbristylis-cymosa.yaml` gained *Cyperus polystachyos* (puʻukaʻa). Each direction carries a `how_to_distinguish` prose distinction so the pair reads consistently from either end.

Verification for every species referenced Wagner/Herbst/Sohmer, National Tropical Botanical Garden, Smithsonian Flora of the Hawaiian Islands, and the Hawaiʻi Department of Agriculture hazardous-plant bulletins (for *Cassytha*). Where the biogeographic status was thin — *Portulaca lutea* — a defensive `uncertainty:` block was placed on the species record rather than picking a side silently.

## 3. What was built

### 3.1 Eight new COMMON species

| Slug | Species | Hawaiian | Family (guide) | Zones | Photos | Cites |
|------|---------|----------|---------------|-------|:------:|:-----:|
| `chenopodium-oahuense` | *Chenopodium oahuense* (Meyen) Aellen | ʻāheahea, ʻāweoweo | Amaranthaceae (APG IV) | strand, sea cliff, valley mouth | 3 | 6 |
| `heliotropium-anomalum` | *Heliotropium anomalum* Hook. & Arn. var. *argenteum* A. Gray | hinahina kū kahakai | Boraginaceae | strand, dune | 3 | 5 |
| `sesuvium-portulacastrum` | *Sesuvium portulacastrum* (L.) L. | ʻākulikuli | Aizoaceae | strand | 3 | 4 |
| `waltheria-indica` | *Waltheria indica* L. | ʻuhaloa, hiʻaloa | Malvaceae (APG IV) | strand, sea cliff, valley mouth | 3 | 6 |
| `portulaca-lutea` | *Portulaca lutea* Sol. ex G. Forst. | ʻihi | Portulacaceae | strand, sea cliff, dune | 3 | 4 |
| `cassytha-filiformis` | *Cassytha filiformis* L. | kaunaʻoa pehu, pololo | Lauraceae | strand, sea cliff, valley mouth | 3 | 6 |
| `cyperus-polystachyos` | *Cyperus polystachyos* Rottb. | puʻukaʻa | Cyperaceae | strand, valley mouth | 3 | 4 |
| `ipomoea-imperati` | *Ipomoea imperati* (Vahl) Griseb. | hunakai | Convolvulaceae | strand, dune | 3 | 4 |

Each new profile carries three clinchers and two to three look-alikes with `how_to_distinguish` prose. *Sesuvium portulacastrum* is the first Aizoaceae in the guide; the family label rendered cleanly, confirming the schema's family enum was not implicitly closed.

### 3.2 Image manifest

`data/images.branch-a.json` grew from 16 to 40 entries (24 new for this cycle, exactly three per new species). Every new entry is CC-BY 3.0 (Forest & Kim Starr's Hawaii Plant Image Archive via Wikimedia Commons). All seven required manifest fields — `slug`, `path`, `author`, `license`, `license_url`, `source`, `source_page` — are populated on every entry. All 24 photograph files are on disk under `site/assets/photos/`.

### 3.3 References

Five new references landed as tokens `A:10`–`A:14` in `data/references/branch-a.md`, each cited by at least one new Branch A species:

- **A:10** APG IV (2016) update of the angiosperm classification, cited on both `taxonomic_notes` fields.
- **A:11** Krauss, B. H. (1993). *Plants in Hawaiian Culture.* Non-extractive framing for ʻuhaloa (*Waltheria indica*) as a lāʻau lapaʻau plant.
- **A:12** Smithsonian Flora of the Hawaiian Islands online database, cited on range statements.
- **A:13** Hawaiʻi Department of Agriculture hazardous-plant bulletins, cited on the *Cassytha* alkaloid warning.
- **A:14** Wood, K. R. (2007) National Tropical Botanical Garden Nā Pali coast botanical survey, cited for coastal-strand community composition on the roadless coast.

### 3.4 Bidirectional look-alike cross-references

Both required look-alike pairs landed in both directions:

- **hunakai ↔ pōhuehue.** `ipomoea-imperati.yaml` lists *Ipomoea pes-caprae* (pōhuehue); `pohuehue.yaml` was edited to list *Ipomoea imperati* (hunakai) — 3 total look-alikes on pōhuehue now. Each entry carries a `how_to_distinguish` note keying on leaf shape (deeply lobed vs. two-lobed), corolla color, and dune position.
- **puʻukaʻa ↔ mauʻu ʻakiʻaki.** `cyperus-polystachyos.yaml` lists *Fimbristylis cymosa* (mauʻu ʻakiʻaki); `fimbristylis-cymosa.yaml` was edited to list *Cyperus polystachyos* (puʻukaʻa) — 2 total look-alikes on mauʻu ʻakiʻaki now. Each carries a `how_to_distinguish` note keying on the inflorescence arrangement diagnostic of the two sedges.

### 3.5 Family-placement notes

The two APG-versus-Wagner discrepancies flagged in the brief carry sourced `taxonomic_notes:` blocks: *Chenopodium oahuense* (Wagner Chenopodiaceae → APG-IV Amaranthaceae, cited to A:10) and *Waltheria indica* (Wagner Sterculiaceae → APG-IV Malvaceae, cited to A:10). Both records show the modern family label prominently and the historical placement in the callout.

### 3.6 Hazards placement

*Cassytha filiformis* carries its toxicity note — aporphine alkaloids; an actionable "orange twining vine with white berries — do not consume the berries" warning — in the `hazards:` field as the first entry, per the brief. See §5 for the in-audit fix that resolved a rendering bug on this specific field.

### 3.7 Ledger

Six worker events were written to the shadow ledger at `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-1a2a754ccd76/clone-0/promise_ledger.jsonl`. Every event carries the canonical schema — `event_id`, `ts`, `narrative`, object-form `confidence` with `assessor: worker`, `run_id`, and `cycle: 3`. No schema drift; the immutable-exceptions waiver was not needed for any new event. The auditor appended a `validated` event on `M-common-tier-broaden` (`event_id: 9d94d805-d539-40b4-8116-74d14f8259ce`, `confidence.assessor: auditor`) before closing the branch.

## 4. Findings

### 4.1 Validator state (workspace-wide, at audit time)

| Validator | Exit | Result |
|-----------|------|--------|
| `scripts/check_coverage.py` | 0 | 45 species; per-tier `common=20 notable=14 rare_exotic=11`; COMMON floor met |
| `scripts/lint_site.py` | 0 | 50 HTML files, zero external asset URLs |
| `scripts/check_links.py` | 0 | 50 pages, all internal links resolve |
| `scripts/check_offline.py` | 0 | safe for `file://` |
| `tests/test_validators.py` | 0 | 5 of 5 negative fixtures rejected |
| `tests/test_build_merge.py` | 0 | 3 of 3 shard-merge fixtures rejected |
| `long_exposure.tools.promise_check` | yellow | Errors strictly on pre-normalization ledger lines 12–16 and 32–38 — 12 unique lines, all covered by the 20-entry `reports/promise_check_immutable_exceptions.json` waiver. No new yellow. |
| `long_exposure.tools.org_check` | 0 | green |

### 4.2 Content spot-check (Branch A scope)

| Species | Family | Zones | Clinchers | Look-alikes | Photos | Cites | Notes |
|---------|--------|-------|:---------:|:-----------:|:------:|:-----:|-------|
| chenopodium-oahuense | Amaranthaceae | strand, sea cliff, valley mouth | 3 | 2 | 3 | 6 | Wagner→APG drift recorded in `taxonomic_notes` |
| heliotropium-anomalum | Boraginaceae | strand, dune | 3 | 2 | 3 | 5 | var. *argenteum* authority correct |
| sesuvium-portulacastrum | Aizoaceae | strand | 3 | 2 | 3 | 4 | First Aizoaceae in the guide; renders cleanly |
| waltheria-indica | Malvaceae | strand, sea cliff, valley mouth | 3 | 2 | 3 | 6 | Wagner→APG drift recorded; ʻuhaloa medicinal culture framed non-extractively |
| portulaca-lutea | Portulacaceae | strand, sea cliff, dune | 3 | 3 | 3 | 4 | Defensive `uncertainty:` block on debated Kauaʻi status |
| cassytha-filiformis | Lauraceae | strand, sea cliff, valley mouth | 3 | 2 | 3 | 6 | Hazards prominent after in-audit fix (§5) |
| cyperus-polystachyos | Cyperaceae | strand, valley mouth | 3 | 3 | 3 | 4 | Bidirectional look-alike ↔ *Fimbristylis cymosa* both directions |
| ipomoea-imperati | Convolvulaceae | strand, dune | 3 | 3 | 3 | 4 | Bidirectional look-alike ↔ *pōhuehue* both directions |

### 4.3 Sufficiency checklist

Every item from the research brief is met:

- Eight new YAML files under `data/species/` with correct slugs. ✓
- ≥2 verified-license photos per new species (three each = 24 total). ✓
- Full "How to identify" block per new species (three clinchers each). ✓
- ≥1 look-alike per new species (two to three each). ✓
- All required fields populated per new species (`check_coverage` green). ✓
- ≥1 `A:N` citation per new species (four to six each). ✓
- `data/images.branch-a.json` gains ≥16 new entries with attribution and license (achieved 24). ✓
- `data/references/branch-a.md` gains new `A:N` refs actually cited (A:10–A:14). ✓
- Bidirectional look-alike edits landed on `fimbristylis-cymosa.yaml` and `pohuehue.yaml`. ✓
- Family-placement `taxonomic_notes` for *Chenopodium oahuense* and *Waltheria indica* with Wagner-versus-APG explanation. ✓
- *Cassytha filiformis* hazards prominent (fixed in-audit; see §5). ✓
- `check_coverage.py` reports `common >= 20`. ✓
- Full validator suite green on the workspace. ✓
- Branch A ledger events use canonical schema. ✓
- Merge report at `reports/cycles/cycle_03_branch_a_common.md` present. ✓

### 4.4 Cross-branch state (context; out of Branch A scope)

At audit time, the contamination the worker had reported at branch close — an unresolved `C:7` token on `kokia-kauaiensis`, bare-integer citation reversions on `hibiscus-waimeae-hannerae` and `mauritian-hemp`, a missing *Panicum niihauense* photograph — was no longer visible. The workspace had converged with all validators green. Noted here so the finding is not re-raised in the next integration cycle; it was outside Branch A's scope regardless.

### 4.5 Decision

**VALIDATED.** Branch A cycle-3 scope fully met. COMMON tier hits the directive floor of 20/20. Total species at cycle close: **45/45**, meeting the directive's overall species-count floor. Per the fan-out-clone contract, this clone's scope is exhausted; the branch auditor gated cleanly and the branch closed.

## 5. Discussion — the in-audit *Cassytha* fix

One MODERATE finding was closed in-audit with a minimal, scoped patch.

`data/species/cassytha-filiformis.yaml` opened its hazards field with literal `<strong>TOXIC — do not consume.</strong>` markup. `scripts/build_site.py:495` HTML-escapes hazard strings at render time, so the rendered page displayed the actual `&lt;strong&gt;...&lt;/strong&gt;` tag text as visible characters — the intended visual emphasis broke and the reader saw markup as prose. The fix stripped the literal tags. The `.hazards` CSS block (warn-red border, colored fill, semibold weight — sharpened in cycle 2) plus the opening ALL-CAPS "TOXIC — do not consume." carry the visual prominence the brief asked for. The toxicity content itself — aporphine alkaloids, the actionable "orange twining vine with white berries — do not consume the berries" warning — was unchanged. A rebuild confirmed the toxicity note is now clean, prominent, and still first in the hazards field.

This is the same failure mode the cycle-2 auditors caught on the Christmas-berry wilelaiki style leak: an author's YAML string was written expecting one rendering behavior when the pipeline actually applied another. The pattern suggests a small preventive lint pass that scans YAML string fields for embedded `<[a-z]+>` markup and flags it before render. This clone did not add that lint (out of scope); the recommendation is passed forward for cycle 4.

## 6. Guidance for the root conductor and the cycle-4 researcher

Branch A is closed. The remaining shape of the run:

- **COMMON tier: 20/20.** Do not schedule further COMMON species without an explicit directive amendment.
- **NOTABLE tier: 14/15.** Cycle 4 should land the final NOTABLE species and open the deep-verification pass (`M-deep-verification`).
- **RARE & EXOTIC tier: 11/10.** Over floor; no further rare & exotic species are needed unless the researcher identifies a specific gap.
- **Total species: 45/45.** The directive floor is met. Remaining cycles should shift from breadth to depth — a claim-by-claim citation audit against Wagner, NTBG, Smithsonian FHI, and USFWS (`M-deep-verification`), then the cycle-6 final report (`M-final-report`).

**Housekeeping carried forward** (MODERATE, non-blocking):

- `scripts/emit_branch_a_events.py` is flagged by `promise_check` as an orphan-in-managed-path; the more recent version lives at `stale/scripts/emit_cycle3_branch_a_events.py`. Recommend moving or deleting the `scripts/` copy at the next integration pass, along with `scripts/emit_branch_c_event.py`.
- Two branch-a YAMLs (`sesuvium-portulacastrum.yaml`, `waltheria-indica.yaml`) are flagged as orphan artifacts because no worker event lists them by name in its `artifacts` array. Cosmetic — either extend a worker event's `artifacts` at merge time or accept as a `promise_check` false positive.
- The defensive `uncertainty:` block on `portulaca-lutea` can be dropped in a future cycle if the researcher confirms a Wagner-Kauaʻi consensus, or left in place as harmless.

## 7. Cumulative progress across cycles 1–3

**Cycle 1** stood up the architecture, image pipeline, SVG library, validators, and a 10-species vertical slice — validated. **Cycle 2** ran three parallel branches (COMMON+8, NOTABLE+6, RARE+6), reconciled at integration; species count reached 30/45, two orphan CRITICAL fixes landed (an inline citation-token leak and a ledger-schema normalization), the sharded-manifest infrastructure was hardened, and the hazard CSS was sharpened. **Cycle 3, this branch,** extended the COMMON tier to 20 (directive floor met), introduced the optional `taxonomic_notes:` field for APG-versus-Wagner drift, established Aizoaceae as a working family in the guide, and carried a canonical ledger schema throughout — the drift that cycles 1–2 auditors had to normalize did not recur.

**Pattern emerging across cycles.** Branch fan-out scales the content axis efficiently on the frozen architecture — marginal per-species cost is roughly one YAML plus three photographs plus a validator run. Ledger schema drift, the recurring cross-branch failure mode of cycles 1–2, appears to have converged: the immutable-exceptions waiver plus canonical-schema enforcement in this cycle held. Cross-branch contamination is a real cost of parallel fan-out but recoverable in the integration cycle; documenting it via `_orphan/*` events lets the root triage without polluting the affected branch. Anchor drift — an author writing YAML strings expecting one rendering behavior when the pipeline applies another — is the current recurring content-quality failure mode; the *Cassytha* `<strong>` case this cycle mirrors the wilelaiki style leak from cycle 2, and a YAML-field markup lint would prevent both.

The remaining work is depth, not breadth. Deep verification (`M-deep-verification`) and final report (`M-final-report`) are the natural cycle-4-through-6 arc.

## Appendix: sessions and artifacts

- **Cycle 1 sessions (this fan-out clone):** researcher `cc0a0fac-d868-4680-8ae5-71b4cc51ed92`, worker `63e70390-65ae-4700-96b4-2520d2b4e4eb`, auditor `dfa11a5c-ee98-4d11-b2fc-2c3091c7b040`.
- **Working directory:** `/home/user/workspaces/kauai-field-guide`.
- **Required output artifact:** `reports/cycles/cycle_03_branch_a_common.md` (present).
- **Shadow ledger:** `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-1a2a754ccd76/clone-0/promise_ledger.jsonl` — six canonical-schema worker events plus one auditor `validated` event.
- **Merge report for the root conductor:** written to `/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-1a2a754ccd76/clone-0/merge_report.md`.

`[[BRANCH_COMPLETE]]`