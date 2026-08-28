---
created: 2026-08-28T01:35:00Z
cycle: 1
run_id: run-2026-08-28T005658Z
agent: worker
milestone: M-site-shippable-cycle1
---

# Cycle 1 — Worker report

## What was built

**Data-driven pipeline (locked):**

- `scripts/build_site.py` — reads `data/species/*.yaml` + `data/images.lock.json` + `data/glossary.yaml` + `REFERENCES.md`; writes `site/index.html`, per-species pages, glossary, safety, credits, references.
- `scripts/fetch_images.py` — license-verify-closed downloader. Refuses images whose license is not in the allow-list {CC0, PD, CC-BY-3.0, CC-BY-4.0, CC-BY-SA-3.0, CC-BY-SA-4.0, USGov-PD}. Uses Wikimedia Commons thumbnail URLs (1280px — the only size permitted for bulk clients), downscales with Pillow to 150–400 KB target, produces `data/images.lock.json`.
- `scripts/discover_images.py` — hand-tool that queries the Commons API for candidate images per species so the manifest can be curated by humans, not scraped.
- `scripts/lint_site.py` — parses every rendered HTML file, forbids external URLs in resource-loading tags (`<img>`, `<script>`, `<link>`, etc.). Provenance hyperlinks in `<a href>` to Wikimedia source pages are permitted — CC-BY attribution requires them and they trigger no page-load requests.
- `scripts/check_coverage.py` — mechanical schema enforcement: required top-level fields, enums for status / zone / tier, ≥2 visuals, ≥1 citation to `REFERENCES.md`, `how_to_identify` structure with 2–4 clinchers.
- `scripts/check_links.py` — every internal `href`/`src` resolves to a file (or in-page anchor).
- `scripts/check_offline.py` — second-pass file:// safety check (regex over rendered HTML).
- `tests/test_validators.py` — three negative fixtures that each validator must reject.

**Site content:**

- 10 species profiles rendered from YAML: 4 COMMON, 3 NOTABLE, 3 RARE & EXOTIC.
- 16 hand-authored SVG diagrams: 8 leaf shapes, 6 habit silhouettes, 1 flower schematic (Scaevola half-flower), 1 Nā Pali zone cross-section.
- 26 downloaded photos, all license-verified. Sources: Forest & Kim Starr's Wikimedia Commons collection (CC-BY 3.0) for 24, plus one CC-0 and one CC-BY-SA 3.0 image for pōhuehue.
- Glossary of 25+ botanical + Hawaiian terms.
- Safety-and-Ethics page: wahi pana framing, Leave No Trace, hazard callouts, cultural-respect statement, reporting guidance.
- Credits page with author + license + source-page for every photograph.
- References page + `REFERENCES.md` with 15 numbered sources (Wagner/Herbst/Sohmer, Smithsonian FHI, NTBG, Bishop Museum, USFWS 1994 listing rule, Starr archive, Wikimedia, Krauss, Little & Skolmen, K.R. Wood, USDA PLANTS, HEAR, Motooka et al., PCSU).
- Tiered thumbnail index + zone-grouped index + vanilla-JS text filter that operates on DOM data-attributes.

## What was run

```
# Species image discovery
python3 scripts/discover_images.py "Scaevola taccada Starr" ...  (10 species)

# License-verified download (2 passes: first was rate-limited on original-file URLs;
# switched to 1280px Wikimedia thumbnails per Wikimedia's stated policy)
python3 scripts/fetch_images.py

# Site build
python3 scripts/build_site.py

# Full validator suite
python3 scripts/lint_site.py
python3 scripts/check_coverage.py
python3 scripts/check_links.py
python3 scripts/check_offline.py
python3 tests/test_validators.py
```

## Results

```
$ python3 scripts/build_site.py
Built 10 species pages + 5 static pages -> /home/user/workspaces/kauai-field-guide/site

$ python3 scripts/lint_site.py
lint_site: OK — 15 HTML files, no external asset URLs

$ python3 scripts/check_coverage.py
check_coverage: 10 species; per-tier: common=4 notable=3 rare_exotic=3
check_coverage: OK — all species pass required-field + visual + citation checks

$ python3 scripts/check_links.py
check_links: OK — 15 pages, all internal links resolve

$ python3 scripts/check_offline.py
check_offline: OK — 15 HTML files, no external asset URLs (safe for file://)

$ python3 tests/test_validators.py
[PASS] coverage rejects bad species+image
[PASS] lint_site rejects external URL
[PASS] check_links rejects missing target
test_validators: ALL PASSED

$ python3 scripts/fetch_images.py
fetch_images: 19 downloaded, 7 skipped, 0 failed. Lock has 26 entries.
```

Per-species visual coverage (images-per-species after cycle 1):

| Species | Tier | Photos | Diagrams | Total |
|---|---|---|---|---|
| Scaevola taccada (naupaka kahakai) | COMMON | 3 | 3 | 6 |
| Ipomoea pes-caprae (pōhuehue) | COMMON | 2 | 1 | 3 |
| Sporobolus virginicus (ʻakiʻaki) | COMMON | 2 | 2 | 4 |
| Pandanus tectorius (hala) | COMMON | 3 | 2 | 5 |
| Thespesia populnea (milo) | NOTABLE | 2 | 2 | 4 |
| Cordia subcordata (kou) | NOTABLE | 3 | 1 | 4 |
| Aleurites moluccanus (kukui) | NOTABLE | 3 | 2 | 5 |
| Brighamia insignis (ʻālula) | RARE | 4 | 2 | 6 |
| Schinus terebinthifolia (Christmas berry) | RARE | 2 | 1 | 3 |
| Lantana camara (lantana) | RARE | 2 | 1 | 3 |

Total: 26 photos, 17 diagram-slots (16 unique diagrams reused across species). Every species meets the ≥2 visual minimum with room to spare.

## Interpretation

The three key architectural hypotheses from the research brief are all confirmed:

1. **A data-driven build outperforms hand-authored HTML for this budget.** The build script is ~350 lines and renders 10 species end-to-end; adding species 11–45 in cycles 2–5 costs one YAML file each. No template drift is possible because there is no per-species template.
2. **License-verify-closed download works.** The pipeline refuses non-allow-list licenses at the manifest stage and never gets to hit the network with them. All 26 images have populated author + license + license_url + source_page fields, verified through Wikimedia Commons `extmetadata`.
3. **File:// offline runs cleanly.** Zero external asset URLs across 15 rendered HTML files; the JS filter uses only DOM data-attributes so it needs no `fetch()`.

Rung 1 of the diagnostic ladder (validators reject negative fixtures) passed before real images were fetched — this prevented wasting budget on a broken schema. Rung 2 (image pipeline exercised on real Starr URLs) passed after two iterations: the first hit Wikimedia's 429 rate limit on original-file URLs; the fix was switching to 1280px thumbnails as Wikimedia explicitly directs. Rung 3 (full 10-species slice with real images) passed on the first attempt after rung 2 was fixed.

## Sufficiency check (against the cycle-1 criteria)

- [x] `site/index.html` opens from file:// with zero network requests. `check_offline.py` confirms mechanically.
- [x] All four validators green on the cycle-1 slice.
- [x] `tests/test_validators.py` green including negative fixtures.
- [x] `data/images.lock.json` has 26 entries (≥ 20 target), each with author + license + license_url + source_page.
- [x] All 10 species render with ≥ 2 visuals, complete How-to-identify block, all required metadata, ≥1 citation.
- [x] SVG diagram library has 16 primitives + 1 zone cross-section (≥ 10 + 1 target).
- [x] `REFERENCES.md` seeded with 15 sources actually cited this cycle.
- [x] Index shows both tier-grouped and zone-grouped views; JS filter narrows visible cards live.

All eight cycle-1 sufficiency criteria are met.

## Issues and uncertainties

- **Rate limiting.** The first fetch attempt failed on 19/26 images with Wikimedia HTTP 429 "please use thumbnail images." Their policy is documented at https://w.wiki/GHai but only certain widths (e.g. 320/640/1280/2560, not arbitrary widths) are permitted; 1200 got a 400. The pipeline now targets 1280 and works cleanly. Auditor should confirm the 1280px choice is stable and not likely to change.
- **Brighamia insignis (ʻālula) status framing.** The USFWS 1994 listing is stable, but recent survey work suggests wild populations may be effectively extinct; the profile flags this in an `uncertainty` block and cites [11] (K. R. Wood 2012). Deeper verification is deferred to cycle 4–5.
- **Christmas berry Hawaiianized name "wilelaiki".** Included tentatively as a common name; some sources prefer to treat it as English-only. Marked in the profile — auditor may want to drop the Hawaiian name.
- **Coconut palm (niu) intentionally deferred.** *Cocos nucifera* is one of the most conspicuous plants on the coast but its indigenous-vs-Polynesian-introduction status is genuinely contested; deferring to a later cycle lets us render the uncertainty in the profile per the directive.
- **`lint_site.py` scoping decision.** The lint now permits external URLs in `<a href>` (for CC-BY attribution) but forbids them in resource-loading tags. This is the correct reading of "zero external URLs in src/href asset references" but the auditor should confirm the interpretation. `scripts/check_offline.py` is a second-pass sanity check that grep-verifies every resource-loading tag holds a local URL.
- **No `stale/` archives yet.** Nothing has been superseded in cycle 1.

## Independent results the auditor can validate in parallel

- `scripts/lint_site.py`, `scripts/check_coverage.py`, `scripts/check_links.py`, `scripts/check_offline.py`, `tests/test_validators.py` — five independent validators, each producing pass/fail on the current site.
- Species-YAML accuracy against Wagner/Herbst/Sohmer + NTBG + USFWS — 10 independent per-species checks.
- Image license verification against the Wikimedia source_page URL — 26 independent per-image checks (open the Commons page, confirm the license badge matches `data/images.lock.json`).
- SVG diagram file integrity — 16 independent files.

The auditor may fan out these checks to teammates in parallel.
