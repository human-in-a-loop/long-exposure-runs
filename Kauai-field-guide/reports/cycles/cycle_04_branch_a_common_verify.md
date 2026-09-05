---
created: 2026-08-28T05:20:00Z
run_id: run-2026-08-28T005658Z
cycle: 4
agent: worker
milestone: M-deep-verification
branch: A (COMMON tier verification)
---

# Cycle 4 — Branch A merge report (COMMON-tier verification)

## Scope

Verify the 20 COMMON-tier species per the cycle-3 pilot's 11-category matrix, resolve the two `_deferred/*` hala items owned by Branch A, opportunistically upgrade photos under the CC-BY-2.0 allow-list, and produce a branch-scoped merge report ready for root integration.

## Deliverables shipped

| Artifact | Path | Status |
|---|---|---|
| Verification report | `reports/verification/cycle_04_common.md` | shipped |
| Branch merge report | `reports/cycles/cycle_04_branch_a_common_verify.md` | this file |
| Hala Gallaher [A:3] title fix | `data/references/branch-a.md` | shipped |
| Hala uncertainty rewrite | `data/species/hala.yaml` | shipped |
| New Gallaher review ref [A:15] | `data/references/branch-a.md` | shipped |
| Nama family placement fix | `data/species/nama-sandwicensis.yaml` | shipped |
| Ledger events (this cycle) | `promise_ledger.jsonl` | 3 `_infra/*` + 6 `_deferred/*` + 1 close = 10 events |

## Verdict summary

**220 verification cells across 20 species × 11 categories: 202 pass (91.8%), 18 needs-work (8.2%), 0 fail.**

- 3 needs-work items were fixed inline this branch (2 hala + 1 Nama).
- The other 15 cells cluster in 6 species-level findings, all deferred to cycle 5 via `_deferred/*` events.
- Site is shippable at file:// with the current state; no deferral is blocking.

## Validator state (post-verification)

Full suite green:

```
Built 46 species pages + 5 static pages
check_coverage: 46 species; per-tier: common=20 notable=15 rare_exotic=11
check_coverage: OK — all species pass required-field + visual + citation checks
check_links: OK — 51 pages, all internal links resolve
check_offline: OK — 51 HTML files, no external asset URLs (safe for file://)
lint_site: OK — 51 HTML files, no external asset URLs
test_validators: ALL PASSED (5/5)
test_build_merge: ALL PASSED (3/3)
```

Citation-token count grew 37 → 44 following the hala rewrite (added `[11]` and `[A:15]` to hala's citations list; new `[A:15]` reference in branch-a.md).

## Shard discipline

- Only `data/references/branch-a.md` was edited (added `[A:15]`; corrected `[A:3]` title).
- Species-YAML edits were confined to Branch A COMMON species: `hala.yaml` (uncertainty rewrite + citations), `nama-sandwicensis.yaml` (family + taxonomic_notes).
- No writes to `data/references/branch-b.md`, `branch-c.md`, `REFERENCES.md`, or any Branch B/C species YAML.
- No writes to `data/images.branch-*.json`.

## Cross-branch flags

Observed but not actioned per shard discipline:

1. `_deferred/alula-conservation-status-refresh` (Branch C shard, RARE tier) — still open per ledger; pilot §3 discrepancy #3.
2. `_deferred/christmas-berry-noxious-weed-source` (Branch C shard, RARE tier) — still open per ledger; pilot §3 discrepancy #4.
3. No sibling-clone workspace contamination observed at cycle start (contrast cycle 3).

## CC-BY-2.0 opportunistic sweep — null pass

All 20 Branch A COMMON species already carry ≥3 license-verified Starr Environmental CC-BY-3.0 photos. No species is on SVG-only fallback; no photo is low-quality or provisional. A CC-BY-2.0 augmentation would be additive but not corrective, and would churn 20 image manifests for negligible reader benefit. Documented as null pass; recommend a workspace-wide sweep in cycle 5 or the final report if visual-diversity is a final-cycle goal.

## Author-position audit rung — outcomes

Applied to every uncertainty block on Branch A COMMON species:

- **hala** — fired → fixed this branch.
- **heliotropium-foertherianum** — fired → deferred (`_deferred/heliotropium-foertherianum-uncertainty-audit`).
- **portulaca-lutea** — fired → deferred (`_deferred/portulaca-lutea-kauai-occurrence-audit`).

`taxonomic_notes` blocks on chenopodium-oahuense and waltheria-indica are family-placement notes, not contested-status uncertainty blocks; the parallel Nama placement was fixed this branch to match.

## Deferrals emitted (cycle 5)

| Milestone | Summary | Scope |
|---|---|---|
| `_deferred/pohuehue-subspecies-rank-note` | POWO synonymizes subsp. brasiliensis under species | 1 YAML |
| `_deferred/heliotropium-foertherianum-uncertainty-audit` | Uncertainty misattributes Imada checklist; real basis is Hillebrand/Rock | 1 YAML + 1 new ref |
| `_deferred/fimbristylis-cymosa-subspecies-note` | Hawaiian populations are subsp. spathacea / umbellato-capitata, not nominal | 1 YAML |
| `_deferred/jacquemontia-rank-preference` | Species vs. subspecies rank — POWO carries both | 1 YAML |
| `_deferred/chamaesyce-degeneri-occurrence-source` | Public-source Nāpali occurrence thin beyond [A:8] Wood | 1 YAML |
| `_deferred/portulaca-lutea-kauai-occurrence-audit` | Kauaʻi occurrence contested; NPHI flags absence | 1 YAML (potentially tier change) |

None blocks the site; all are single-YAML edits or narrative rewrites of an existing block.

## Recommendations for root integration / cycle 5

1. **No merge conflicts anticipated.** Branch A's writes are confined to Branch A shards.
2. **Cycle-5 researcher should discharge the 6 deferrals** listed above. Total scope is small (~1–2 hours single-worker); can go in one branch or be split across Branch A + Branch C in a next fan-out.
3. **Persistent yellow state on `promise_check`** (lines 12–16, 32–38) is unchanged per brief; still waived under `_orphan/cycle-2-immutable-exceptions`.
4. **CC-BY-2.0 workspace-wide sweep** — deferrable to cycle 6 final-report prep; not urgent.
5. **NOTABLE-tier and RARE-tier verification passes** are the other cycle-4 branches (B and C); cycle 5 should synthesize all three matrices into a coverage table for the final report.

## Ledger events emitted this branch (canonical schema)

Three `_infra/*` events (validated), six `_deferred/*` events (in-progress), one `_run/branch-a-cycle-4-close` event (validated). All use `uuid.uuid4()` event_ids, ISO-8601 timestamps in the `2026-08-28T05:*Z` window, `confidence` as an object with level/rationale/assessor, and `agent: worker`.

---

*End of Cycle 4 Branch A merge report.*
