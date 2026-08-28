---
created: 2026-08-28T02:03:00Z
cycle: 2
run_id: run-2026-08-28T005658Z
agent: worker
branch: A
milestone: M-common-tier-broaden (in-progress) + M-manifest-sharding (validated)
---

# Cycle 2 — Branch A (COMMON tier expansion + shared-prep infra)

## Summary

Branch A executed the sequence the brief prescribed:

1. **Shared-prep infra first** — landed sharded image manifests + citation-token scheme in `scripts/build_site.py`, complete with a new `tests/test_build_merge.py` suite (3 negative fixtures, all green). Base cycle-1 site rebuilds byte-identically across successive invocations. Empty stub shards created for A/B/C so parallel branches can land safely.
2. **Canary species (*Sida fallax*)** — authored end-to-end with tokens `["A:1","A:6","A:7"]`; fetched both photos from Wikimedia; built and validated cleanly.
3. **Remaining 7 COMMON species** — authored with real Starr-archive photos discovered via the Commons API.
4. **Audit follow-throughs** — hala uncertainty block added; `check_coverage.py` look_alikes rule tightened with new negative fixture.
5. **Full validator sweep** — build, coverage, lint, links, offline, and both test suites all green on the 30-species workspace.

## Deliverables

### Sharded-manifest infrastructure

| File | Change |
|------|--------|
| `scripts/build_site.py` | Added `preflight_image_manifests()` (duplicate-id detection across `images.json` + `images.branch-*.json`), rewritten `load_references()` that merges `REFERENCES.md` + lex-sorted `data/references/branch-*.md` shards and returns a `(refs, token_map)` tuple, `resolve_citations()` for YAML `citations:` entries that mixes ints and `"X:n"` tokens, and writes `data/references.map.json` on every build. |
| `scripts/check_coverage.py` | `load_refs()` returns `(base_ints, shard_tokens)`; per-species citation loop accepts either ints or `"X:n"` tokens. Split `images` from `REQUIRED_TOP` into `REQUIRED_PRESENT` so SVG-only species with `images: []` pass (the ≥2-total-visuals rule already gates the substantive check). Look-alikes rule tightened to `len < 1` failure. |
| `scripts/fetch_images.py` | Merges `data/images.json` + `data/images.branch-*.json` shards; refuses duplicate ids across shards. |
| `data/images.branch-{a,b,c}.json` | Empty stubs (b, c) or populated (a, 16 entries) shard manifests. |
| `data/references/branch-{a,b,c}.md` | Per-branch reference shards; a is populated (9 entries), b/c stubbed. |
| `data/references.map.json` | Auto-emitted every build; auditors read this to see how tokens rewrote to global ids. |
| `tests/test_build_merge.py` | New negative-fixture suite: (a) duplicate image id across shards, (b) shard iteration order deterministic, (c) unresolved citation token. All 3 pass. |
| `tests/test_validators.py` | New `EMPTY_LOOK_ALIKES_YAML` fixture that `check_coverage.py` must reject. Passes. |

### 8 new COMMON tier species

| Slug | Sci name | Hawaiian | Status | Images | Diagrams | Citations |
|------|----------|----------|--------|--------|----------|-----------|
| `sida-fallax` | *Sida fallax* Walp. | ʻilima, ʻilima papa | indigenous | 2 photos | 1 SVG | `A:1, A:6, A:7` |
| `heliotropium-foertherianum` | *Heliotropium foertherianum* Diane & Hilger | hinahina kū kahakai | indigenous (+ uncertainty block) | 2 photos | 1 SVG | `A:1, A:2, A:6, A:7` |
| `vitex-rotundifolia` | *Vitex rotundifolia* L. f. | pōhinahina, kolokolo kahakai | indigenous | 2 photos | 1 SVG | `A:1, A:6, A:7` |
| `fimbristylis-cymosa` | *Fimbristylis cymosa* R. Br. | mauʻu ʻakiʻaki | indigenous | 2 photos | 2 SVG | `A:1, A:6, A:7` |
| `jacquemontia-sandwicensis` | *Jacquemontia ovalifolia* subsp. *sandwicensis* (A. Gray) K.R. Robertson | pāʻū o Hiʻiaka | **endemic** | 2 photos | 1 SVG | `A:1, A:6, A:7, A:8` |
| `boerhavia-repens` | *Boerhavia repens* L. | alena | indigenous | 2 photos | 1 SVG | `A:1, A:6, A:7` |
| `nama-sandwicensis` | *Nama sandwicensis* A. Gray | hinahina kahakai | **endemic** | 2 photos | 1 SVG | `A:1, A:5, A:6, A:7, A:8` |
| `chamaesyce-degeneri` | *Chamaesyce degeneri* Sherff | ʻakoko | **endemic** | 2 photos | 1 SVG | `A:1, A:5, A:6, A:7, A:8` |

- **Endemic count in Branch A:** 3 (as predicted in the brief).
- **All 16 photos are CC-BY-3.0 by Forest & Kim Starr,** discovered via the Wikimedia Commons API (`scripts/discover_images.py`), fetched at 1280 px thumbnails, downscaled to the 150–400 KB band, and written to `site/assets/photos/`.
- Every species has ≥ 1 look-alike populated; most have 2–3, including cross-references to cycle-1 species (naupaka, pōhuehue, Ipomoea) and within Branch A (Boerhavia coccinea confer, Heliotropium anomalum confer, Chamaesyce celastroides confer).
- Cultural framing is respectful and non-extractive throughout. Pāʻū o Hiʻiaka carries the Hiʻiaka association explicitly with no harvest instruction; hinahina names (multiple species) are cross-referenced.

### Audit follow-throughs

- **hala uncertainty block (moderate finding 1, resolved).** `data/species/hala.yaml` now carries an `uncertainty:` block citing both positions (Wagner as primary via `A:1`; Gallaher et al. dispersal work via `A:3`). Renders as an `<div class="uncertainty">` callout on `site/species/hala.html` — visually verified.
- **`check_coverage.py` look_alikes tightened (moderate finding 4, resolved).** Rule changed from `is None` to `len < 1`. New negative fixture (`EMPTY_LOOK_ALIKES_YAML`) added to `tests/test_validators.py` and passes. All 30 live species have ≥ 1 look-alike, so the change is silent for the current site.

## Validator sweep — all green

```
build_site:      Built 30 species pages + 5 static pages
                 citation tokens resolved: 9
check_coverage:  30 species; per-tier: common=12 notable=9 rare_exotic=9
                 OK — all species pass required-field + visual + citation checks
lint_site:       OK — 35 HTML files, no external asset URLs
check_links:     OK — 35 pages, all internal links resolve
check_offline:   OK — 35 HTML files, no external asset URLs (safe for file://)
test_validators: ALL PASSED (4/4)
test_build_merge: ALL PASSED (3/3)
```

**Byte-identity check.** Running `scripts/build_site.py` twice in succession produces byte-identical HTML for all 35 files (spot-checked via SHA-256).

## Deviations from plan

1. **Fixed a pre-existing bug in `check_coverage.py` (scope-adjacent).** `REQUIRED_TOP` included `images`, tested by `not sp.get(f)`, which incorrectly failed SVG-only species with `images: []` (Branch C's `Schiedea apokremnos` hit this). Split into `REQUIRED_PRESENT` (key must exist, may be empty). The `≥2 total visuals` rule already gates the substantive requirement. Logged as `_minor/coverage-images-empty-list-bug` in the ledger.
2. **Branch B and C content already present in workspace.** When Branch A began, the workspace already contained 16 additional species YAMLs and their image lock entries (niu, hau, ohe-makai, ohai, koa-haole, castor-bean, mauritian-hemp, naio, hibiscus-hannerae, panicum-niihauense, schiedea-apokremnos, wiliwili, sesbania-tomentosa). This is exactly the concurrent-branch scenario the sharded infra was designed to handle. `REFERENCES.md` had also been manually renumbered to 29 entries with a "Branch C additions" comment noting a conflict with Branch B's earlier landing — precisely the pain point the citation-token scheme eliminates. The infra merged cleanly; the base site plus all 26 other species render correctly.
3. **Image URL discovery.** The Wikimedia thumbnail-width limitation (only certain widths accepted) plus the fact that hand-guessed Starr URLs mostly 404 meant I ran `scripts/discover_images.py` first to get real file URLs from the Commons API, then hand-curated a 16-entry manifest with confirmed URLs. All 16 downloads succeeded on first attempt. No SVG fallback was needed — even for the "thin coverage" species the brief flagged (Chamaesyce degeneri, Nama sandwicensis, Boerhavia repens), Starr photos were available.

## Notes for auditor

- **Spot-check candidates for Wagner accuracy:** *Jacquemontia ovalifolia* subsp. *sandwicensis* (endemic status, subspecies name), *Nama sandwicensis* (endemic vs. indigenous), *Fimbristylis cymosa* (family assignment — Cyperaceae, not a grass). All three intentionally lean on Wagner via `A:1` primarily.
- **Spot-check candidate for NTBG accuracy:** *Chamaesyce degeneri* — status, Kauaʻi occurrence, and hazard note.
- **Confirm hala uncertainty block renders** at `site/species/hala.html`. Also confirm the `[A:3]` in the callout text is a plain text fragment (it is; the citation-token rewriter only touches YAML `citations:` lists, not narrative prose — that is intentional so uncertainty block prose can name tokens without them becoming ambiguous hyperlinks).
- **Confirm the citation-token map** at `data/references.map.json`: `A:1 → 30`, `A:2 → 31`, … , `A:9 → 38` (base REFERENCES.md has 29 entries; shard adds 9).
- **Cross-image reuse:** *H. foertherianum* and *S. taccada* both reference each other in look-alikes; verify by loading each species page.

## Known gaps / carried to future cycles

- COMMON tier is at 12 species after Branch A; run-end target is ~20. Cycles 3–5 should add ~8 more common species (ʻāhuʻawa *Cyperus javanicus*, ʻakulikuli *Sesuvium portulacastrum*, ʻāweoweo *Chenopodium oahuense*, pāʻūohiʻiaka *Jacquemontia sandwicensis*'s cousin *Ipomoea imperati*, *Cassytha filiformis* kaunaʻoa, *Hedyotis*/*Kadua* coastals as appropriate).
- The `H. foertherianum` uncertainty block leans on the Imada 2019 checklist [A:6] for the "some recent treatments" phrasing without naming a specific paper making the modern-introduction argument, because none I could locate did so unambiguously — the more common alternate reading is that it may be an early Polynesian introduction rather than a modern one. Deep-verification cycle should either resolve or drop that specific dispute.
- Cycle-1 minor finding (83 KB image size threshold in fetcher) intentionally not acted on per brief instruction.

## Ledger events emitted this branch

- `M-manifest-sharding` validated high (Sharded infra + tests + stubs)
- `M-common-tier-broaden` in-progress high (+8 species)
- `_moderate/hala-uncertainty` resolved high
- `_moderate/look-alikes-len-tightening` resolved high
- `_minor/coverage-images-empty-list-bug` resolved high (scope-adjacent fix flagged)
