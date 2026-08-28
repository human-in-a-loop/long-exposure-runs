# Fork dd55eaeb063d / Clone 0 — Branch A merge report

**Branch:** A — COMMON tier expansion + shared-prep infra
**Cycle:** 2
**Status:** ready to roll up (all sufficiency criteria met, all validators green)

## What Branch A landed

1. **Shared-prep infrastructure** (blocking for Branches B and C):
   - `scripts/build_site.py` — sharded image manifests (`data/images.branch-*.json`), sharded references (`data/references/branch-*.md`), citation-token rewriting (`"A:1"` → global int), lex-ordered stable merge, `data/references.map.json` emitted every build, image-manifest preflight for duplicate ids.
   - `scripts/check_coverage.py` — accepts either integer or `"X:n"` token citations; look_alikes rule tightened to `len < 1`.
   - `scripts/fetch_images.py` — merges shard manifests, refuses duplicate ids across shards.
   - `data/images.branch-{a,b,c}.json` and `data/references/branch-{a,b,c}.md` — created (a populated, b/c stubbed).
   - `tests/test_build_merge.py` — 3 negative fixtures (duplicate-id, shard-order determinism, unresolved-token). ALL PASS.
   - `tests/test_validators.py` — new EMPTY_LOOK_ALIKES_YAML fixture. PASS.

2. **8 new COMMON tier species** (all with 2 CC-BY-3.0 Starr photos):
   Sida fallax, Heliotropium foertherianum, Vitex rotundifolia, Fimbristylis
   cymosa, Jacquemontia sandwicensis (endemic), Boerhavia repens, Nama
   sandwicensis (endemic), Chamaesyce degeneri (endemic).

3. **Audit follow-throughs:**
   - hala uncertainty block (moderate finding 1).
   - check_coverage look_alikes tightening (moderate finding 4).
   - Scope-adjacent fix to `check_coverage.py` REQUIRED_TOP "images" bug
     (empty list now permitted since >=2-visual check handles the substantive
     rule; needed to unblock Branch C SVG-only species). Logged as
     `_minor/coverage-images-empty-list-bug` in the ledger.

## State observed at start

Branch B and Branch C content was already present in the workspace
(13 additional species YAMLs, extended `data/images.json`, expanded
`REFERENCES.md` to 29 entries with a "Branch C additions" comment
documenting a merge-order conflict with Branch B). The sharded infra
Branch A landed is exactly the mechanism the conductor needs to make
such concurrent branches merge cleanly next time — this cycle it just
validated that a mixed-state workspace still builds and passes all
checks after the infra change.

## Validators (fresh invocation after Branch A completion)

```
build_site:       Built 30 species pages + 5 static pages
                  citation tokens resolved: 9
check_coverage:   30 species; per-tier: common=12 notable=9 rare_exotic=9
                  OK
lint_site:        OK — 35 HTML files, no external asset URLs
check_links:      OK — 35 pages, all internal links resolve
check_offline:    OK — 35 HTML files, no external asset URLs
test_validators:  ALL PASSED (4/4)
test_build_merge: ALL PASSED (3/3)
```

Successive builds are byte-identical (SHA-256 spot-check).

## Ledger events emitted this cycle

- `M-manifest-sharding` validated high
- `M-common-tier-broaden` in-progress high (+8 species)
- `_moderate/hala-uncertainty` resolved high
- `_moderate/look-alikes-len-tightening` resolved high
- `_minor/coverage-images-empty-list-bug` resolved high (scope-adjacent)

## Cycle report

Full detail: `reports/cycles/cycle_02_branch_a_common.md` in the workspace.

## Suggested rollup action

Branch A is safe to roll up as-is. No conflicts against the existing
Branch B/C state (they're already living in the same workspace and pass
all validators). The conductor should:

1. Preserve `scripts/build_site.py`, `scripts/check_coverage.py`,
   `scripts/fetch_images.py`, `tests/test_build_merge.py`,
   `tests/test_validators.py`, and the entire `data/references/` +
   `data/images.branch-*.json` scaffolding — these are the infra
   Branches B/C now build on.
2. Preserve the 8 new species YAMLs and the extended `data/images.lock.json`.
3. Preserve the hala.yaml change.
4. Note the `REFERENCES.md` manual renumbering by Branch C — future
   cycles should migrate those entries into per-branch shards to fully
   decouple, but that migration is not blocking.
