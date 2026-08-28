<!--
created: 2026-08-28T04:50:00Z
cycle: 4
run_id: run-2026-08-28T005658Z
fork: fork-f2dde7689a5d
branch: B
agent: worker
milestone: M-deep-verification (NOTABLE-tier scope, Branch B)
-->

# Cycle 4 — Branch B: NOTABLE Tier Verification Merge Report

## Directive alignment

Branch B scope: Verify the 15 NOTABLE-tier species (milo, kou, kukui, wiliwili, niu, hau, ʻohe makai, ʻōhai, naio, kī, noni, kalo, kō, ʻaʻaliʻi, māmaki) against the cycle-3 pilot's 11-category matrix. Author-position audit on every contested-status uncertainty block; kalo Hāloa framing cross-referenced against Krauss/Handy/Kirch; Colocasia and Saccharum cultivar-diversity claims verified; Sesbania cross-listing regression check; opportunistic CC-BY-2.0 re-image sweep on niu and hau. Deliverable: `reports/verification/cycle_04_notable.md` + this merge report.

**Status: complete.**

## Sufficiency criteria (all met)

- [x] 15-species × 11-category matrix produced at `reports/verification/cycle_04_notable.md` (165 cells).
- [x] ≥90% pass rate: **95.8% (158/165) — exceeds the floor by 5.8 pp**.
- [x] Every contested-status uncertainty block passes author-position audit (niu Harries 1978, hau Wagner/Herbst, plus incidental Lowry & Plunkett nomenclatural claim on ʻohe makai) — see §3 of the verification report.
- [x] Cultural claims across all 15 species traced to primary ethnobotany (Krauss / Handy & Handy / Abbott / Rock / Kamakau) — no tertiary web citations survive. See §4 of the verification report.
- [x] Kalo Hāloa framing cross-referenced against Handy & Handy 1972 pp. 74–75 and Kumulipo primary source; matches on all named elements (Wākea, Hoʻohōkūkalani, first Hāloa → first kalo → second Hāloa → Hawaiian people). Passes cross-reference against Kirch 1985 and Kirch & Kahn 2007 as well.
- [x] Family-placement APG-vs-Wagner audit run across all 15 species (§6 of the verification report). Two shifts documented: naio (Myoporaceae → Scrophulariaceae s.l., fixed inline this cycle) and kī (Agavaceae/Laxmanniaceae → Asparagaceae, already documented in cycle 3). No silent shifts remain.
- [x] Colocasia (kalo) cultivar-diversity claim verified: "more than 300 named pre-contact varieties" traces to Handy & Handy 1972 (via KSBE Hawaiian-cultural curriculum which cites Handy). Passes.
- [x] Saccharum (kō) cultivar-diversity claim verified: YAML uses hedged "many pre-contact Hawaiian kō cultivars" without a specific number; Handy & Handy 1972 and Krauss 1993 both document dozens; Lincoln 2020 catalogues >100. Passes without needing a specific numeric anchor.
- [x] Sesbania cross-listing (`is_federal_listed()` on `data/species/sesbania-tomentosa.yaml`) verified rendering: 4 references to sesbania-tomentosa on the built `site/index.html`, including the "Also federally listed" cross-list section on the RARE-tier index. No regression.
- [x] CC-BY-2.0 opportunistic re-image sweep attempted; documented as `_deferred/notable-cc-by-2-image-sweep` with prime candidates listed (ʻaʻaliʻi highest priority — only NOTABLE-tier species still at the bare 2-visual minimum with just 1 photo). No new images landed this cycle (fetch pipeline pass out of scope).
- [x] Discrepancies logged as `_deferred/*` events for cycle 5 (6 total; see below).
- [x] Full validator suite green post-changes.
- [x] Merge report present (this file).
- [x] Cycle-close ledger event with canonical schema (below).

## Small inline fixes applied (Branch B files only)

1. **`data/species/naio.yaml`** — Added a `taxonomic_notes:` block noting Wagner's Myoporaceae vs APG's Scrophulariaceae s.l. placement, referencing Chinnock (2007) [B:4]. Pattern parallel to branch-a's cycle-3 Chenopodium / Waltheria taxonomic_notes.
2. **`data/species/noni.yaml`** — Tightened `cultural_significance` dye-color specificity from imprecise "dye from bark and root (yellow to red-brown)" to "dye for kapa cloth (red pigment from the bark, yellow pigment from the root)" per CTAHR noni profile and Bishop Museum ethnobotany, both quoting Handy & Handy 1972.
3. **`data/references/branch-b.md`** — Added [B:15] USFWS 2021 5YR for Sesbania tomentosa and [B:16] Burney et al. Makauwahi Cave (Kauaʻi) subfossil kou record. Neither reference is yet cited from a species YAML — both pre-landed for cycle-5 deferred rewrites.

Rationale for keeping inline scope small: the pilot's guidance is *"inline fixes are only when the correction is small and unambiguous"*. Anything requiring an uncertainty-block narrative rewrite, a new citation on a species YAML, or coordination with a not-yet-authored ledger discussion → `_deferred/*`.

## Deferrals to cycle 5 (`_deferred/*`)

1. `_deferred/milo-indigenous-hedge-block` — Optional soft uncertainty block on milo modeled on hau's. Low priority (mainstream indigenous treatment is defensible).
2. `_deferred/wiliwili-aprostocetus-second-biocontrol-note` — One-sentence ecology-field update on the *A. nitens* second biocontrol under study.
3. `_deferred/ohe-makai-rock-1913-tapa-beater-verify` — Open Rock 1913 primary text; the tapa-beater claim looks likely misattributed (soft wood is not tapa-beater material); replace with confirmable stilts (kukuluāeʻo) + canoe-parts wording if the Rock sentence cannot be located.
4. `_deferred/sesbania-conservation-status-5yr-refresh` — Reformat `conservation_status` string on ʻōhai to include the 2021 5YR reference; wire [B:15] into `citations:`.
5. `_deferred/sesbania-uncertainty-block-refresh-with-2021-5yr` — Rewrite ʻōhai's uncertainty block to reflect 2021 5YR data (Kauaʻi wild populations extant but sparse) via [B:15].
6. `_deferred/notable-cc-by-2-image-sweep` — Execute the CC-BY-2.0 re-image sweep prioritising ʻaʻaliʻi (1 → 3+ photos), plus optional expansions for kalo (loʻi context), niu, hau, noni, māmaki.

## Author-position audit — the sleeper rung

Following the cycle-3 pilot's Gallaher-drift finding, an author-position audit was applied to every contested-status uncertainty block and every high-stakes cultural citation this cycle. Results: **7 PASS, 1 NEEDS-WORK** (Rock 1913 tapa-beater claim on ʻohe makai — deferred; not an author-mis-attribution but a claim the wood-density evidence contradicts and Rock's primary text was not accessible for direct verification).

The niu / Harries 1978 case — the highest-risk pre-loaded author-position audit target — **passed cleanly**. The niu YAML's careful hedging ("pre-Polynesian presence in the Pacific plausible") does not overreach into a Hawaiʻi-specific claim Harries doesn't make. This is the same pattern the pilot recommended for uncertainty-block phrasing, and it worked here.

The hau / Wagner+Herbst pair also **passed**: both Wagner 1999 [1] and Herbst 1988 [B:5] genuinely treat hau as indigenous on biogeographic grounds. The uncertainty block captures both the mainstream position and the older cultural-argument minority without conflation.

The kalo / Handy & Handy Hāloa cross-reference **passed** on names (Wākea, Hoʻohōkūkalani, Hāloa) and structural elements (stillborn first child → first kalo plant → second child named Hāloa is the human ancestor). No modern-attribution drift; matches Handy & Handy 1972 pp. 74–75 exactly.

## Family-placement (APG-vs-Wagner) audit

Systematic 15-species scan; two shifts documented (naio, kī); both now carry `taxonomic_notes:`. No silent shifts survive. See §6 of the verification report for the full table.

## Sesbania cross-listing regression check

`is_federal_listed()` continues to fire on `sesbania-tomentosa`. 4 references in the built `site/index.html`, including the "Also federally listed (cross-listed from other tiers)" section. Cross-lister is Branch B's cycle-2 feature and remains sound at cycle 4. No regression.

## Validator + test suite (post-changes)

```
build_site.py:      46 species pages + 5 static pages; 46 citation tokens resolved
check_coverage.py:  46 species (common=20 notable=15 rare_exotic=11); OK
check_links.py:     51 pages, all internal links resolve; OK
check_offline.py:   51 HTML files, no external asset URLs; OK
lint_site.py:       51 HTML files, no external asset URLs; OK
test_validators.py: ALL PASSED (3 negative-fixture tests)
test_build_merge.py: ALL PASSED (3 shard-merge negative-fixture tests)
```

Full validator + test suite: **GREEN**.

## Ledger event (canonical schema)

Emitted at branch close via `long_exposure.tools.ledger_append`:

- `_run/branch-b-cycle-4-close` — validated / high — cycle 4 — worker
- `M-deep-verification` — in-progress / high — cycle 4 — worker — scope: NOTABLE tier (15/15 species verified this branch); overall run milestone remains in-progress pending cycle-4 Branch A (COMMON) and Branch C (RARE) verifications and cycle-5 discharge of the 6 deferrals above.

## Handoff to root conductor

Cycle 4 Branch B is complete and shippable-at-branch-close. Site remains fully offline, all validators green, no cross-branch touches. Cycle 5 (integration) can pick up:

- Discharge the 6 `_deferred/*` items above (Branch B ownership on all 6 since they touch Branch-B-owned species YAMLs and Branch-B references).
- Consider integrating [B:16] Makauwahi Cave into `data/species/kou.yaml` as a strengthening citation on the indigenous-status treatment (Branch B action; NTBG/Burney evidence pre-dates human arrival on Kauaʻi).
- Merge with parallel Branch A (COMMON tier) and Branch C (RARE tier) verification outputs; expect similar shape (matrix + small inline fixes + deferrals).

*End of Cycle 4 Branch B NOTABLE-tier merge report.*
