---
created: 2026-08-28T02:16:00Z
run_id: run-2026-08-28T005658Z
cycle: 2
agent: worker
branch: B
fork: dd55eaeb063d
clone: 1
---

# Merge Report — Fork dd55eaeb063d / Clone 1 / Branch B — Cycle 2

**Scope:** NOTABLE tier expansion + housekeeping.
**Status:** COMPLETE. All 6 target species landed, both deferred markers closed, housekeeping done, full validator suite green.
**Root conductor:** ready to merge.

---

## Species added (6)

All under `data/species/`, all with `tier: notable`, all with 3-4 Starr CC-BY-3.0 photos + 2 SVG diagrams (habit + leaf), all citing shard-local Branch B refs via `"B:N"` tokens per Branch A's sharded-manifest infra.

| slug | scientific name | status | conservation | photos | uncertainty block |
|---|---|---|---|---|---|
| `naio` | *Myoporum sandwicense* (A.Gray) A.Gray | indigenous | least concern | 3 | - |
| `wiliwili` | *Erythrina sandwicensis* O.Deg. | endemic | least concern (gall-wasp threatened) | 3 | - |
| `niu` | *Cocos nucifera* L. | Polynesian introduction | least concern | 3 | **YES** - Polynesian-vs-natural distribution (Harries 1978 alt.) |
| `hau` | *Hibiscus tiliaceus* L. | indigenous | least concern | 4 | **YES** - contested indigenous vs. Polynesian |
| `ohe-makai` | *Polyscias sandwicensis* (A.Gray) Lowry & G.M.Plunkett | endemic | vulnerable | 3 | nomenclatural note (*Reynoldsia* synonym) |
| `sesbania-tomentosa` | *Sesbania tomentosa* Hook. & Arn. | endemic | **US Endangered** (USFWS 1994) | 3 | Kauaʻi contemporary-population evidence hedged |

Uncertainty-block exercise: **niu and hau** as directed. `ohe-makai` also carries an uncertainty note (nomenclatural, not status).

## Sesbania cross-listing

`sesbania-tomentosa.yaml` lives at `tier: notable` (cultural framing decision). Added `is_federal_listed()` filter block to `render_index()` in `scripts/build_site.py` so the RARE-tier index page surfaces federally listed species regardless of authored tier. Verified: sesbania appears in both the notable grid and the "Federally Listed" cross-list on the built index (6 hits in `site/index.html`).

## Image coverage

- Manifest shard: `data/images.branch-b.json` = 19 entries (was 0; migrated from base via `stale/scripts/branch_b_shard_migrate.py`).
- Base manifest `data/images.json` reduced from 56 to 37 entries.
- Lock file `data/images.lock.json` = 72 total entries including all 19 Branch B fetches; all `license: CC-BY-3.0`, `attribution: Forest & Kim Starr`, `source: Wikimedia Commons`.
- All 19 images downloaded, downscaled, and validated in `site/assets/photos/`.

## References shard

`data/references/branch-b.md` - 8 new refs, cited from Branch B species via `"B:1"`...`"B:8"` tokens. Global-integer assignment handled by `build_site.py`'s `resolve_citations()`; ran build, 17 citation tokens resolved cleanly.

| token | reference (abbreviated) |
|---|---|
| B:1 | Rock 1913 *Indigenous Trees of the Hawaiian Islands* |
| B:2 | Harries 1978 - Cocos evolution / natural distribution |
| B:3 | Lowry & Plunkett 2010 - *Polyscias* generic circumscription |
| B:4 | Chinnock 2007 *Eremophila and Allied Genera* monograph |
| B:5 | Herbst 1988 - Hawaiian strand biogeography |
| B:6 | Rubinoff et al. 2010 - Erythrina gall wasp |
| B:7 | USFWS 1994 - *Sesbania tomentosa* endangered listing |
| B:8 | DLNR-DOFAW naio thrips advisory |

Root `REFERENCES.md`: NOT modified for Branch B refs. A single marker comment notes the shard migration. Branch C's [24]-[29] entries in root REFERENCES.md left untouched (their scope).

## Housekeeping (moderate finding 3)

- `scripts/emit_cycle1_events.py` -> `stale/scripts/emit_cycle1_events.py`. Ledger event `_stale/emit_cycle1_events` (status=validated) recorded the move.
- `reports/cycles/cycle_01_worker.md`: NOT moved (canonical cycle-1 report). Bound to a milestone via `_run/cycle-1-close` ledger event (status=validated) with the file in `artifacts` - `promise_check` no longer flags it as orphan.

## Deferred markers (moderate finding 5)

Opened at branch resumption:

- `_deferred/niu-status-uncertainty` - status=deferred
- `_deferred/hala-status-uncertainty` - status=deferred (noted Branch A owns hala.yaml)

Closed at branch end (status=validated):

- `_deferred/niu-status-uncertainty` - closed by `data/species/niu.yaml`; uncertainty block cites B:2 (Harries 1978).
- `_deferred/hala-status-uncertainty` - closed BY REFERENCE to Branch A's `data/species/hala.yaml` (cf. `_moderate/hala-uncertainty` validated 2026-08-28T02:03:20Z). No edit to Branch A's file.

## Milestone progress

Ledger event `M-notable-tier-broaden` status=in-progress, high confidence:

- NOTABLE tier: **3 -> 9 species** (cycle-1 milo, kou, kukui + Branch B six).
- Root plan target: ~15 total NOTABLE by run end. **+6 more needed** across remaining cycles (out of Branch B scope).

## Validation

Ran full suite; all green:

```
python3 scripts/build_site.py    -> 30 species pages + 5 static pages; 17 citation tokens resolved
python3 scripts/check_coverage.py -> 30 species; common=12 notable=9 rare_exotic=9; OK
python3 scripts/lint_site.py     -> 35 HTML files, no external asset URLs
python3 scripts/check_links.py   -> 35 pages, all internal links resolve
python3 scripts/check_offline.py -> 35 HTML files, safe for file://
python3 tests/test_validators.py -> 4/4 PASS (including new EMPTY_LOOK_ALIKES fixture)
```

## Cultural framing (wahi pana discipline)

Held. For each Branch B species:
- Named practice categories in cultural notes (e.g., wiliwili wood historically used for surfboards and net floats; kapa dye from naio heartwood) without harvest/preparation/shaping instructions.
- Credited keepers: Native Hawaiian communities, cultural practitioners, and named ethnobotanical sources (Handy & Handy, Krauss, Abbott) as attribution, not as instruction.
- No collecting guidance, no processing steps, no ceremonial detail beyond what published sources publicly attribute.

## Species-safety notes surfaced

- `niu`: **falling coconut hazard** placed prominently in `hazards:` field (not buried in ecology).
- `wiliwili`: gall-wasp ecological threat noted in `ecology`.
- `hau`: soft-branch drop, minor irritant sap noted.
- `sesbania-tomentosa`: no user-facing hazard; conservation-status warning against any interaction ("look, do not touch").
- `naio`: naio thrips (*Klambothrips myopori*) noted as conservation threat.
- `ohe-makai`: no known hazards; rare, do-not-disturb note.

## Files touched - summary

**Added:**
- `data/species/{naio,wiliwili,niu,hau,ohe-makai,sesbania-tomentosa}.yaml` (6)
- `data/references/branch-b.md` (populated with 8 refs)
- `data/images.branch-b.json` (19 entries)
- `reports/cycles/cycle_02_branch_b_notable.md` (canonical Branch B cycle report)
- `stale/scripts/{emit_cycle1_events,branch_b_open,branch_b_add_images,branch_b_shard_migrate}.py`

**Modified:**
- `scripts/build_site.py` (added `is_federal_listed()` cross-listing block)
- `REFERENCES.md` (marker comment only; no new entries)
- `data/images.json` (Branch B entries removed after shard migration)
- `data/images.lock.json` (populated by fetch)

**Moved:**
- `scripts/emit_cycle1_events.py` -> `stale/scripts/emit_cycle1_events.py`

**Not touched (out of scope / other-branch ownership):**
- `data/species/hala.yaml` (Branch A)
- Root REFERENCES.md entries [24]-[29] (Branch C)

## Ledger events opened / closed by Branch B

Opened at resumption:
- `_deferred/niu-status-uncertainty` (deferred)
- `_deferred/hala-status-uncertainty` (deferred)
- `_run/cycle-1-close` (validated, cycle-1 report binding)
- `_stale/emit_cycle1_events` (validated, orphan move)

Closed / progress at end:
- `_deferred/niu-status-uncertainty` (validated)
- `_deferred/hala-status-uncertainty` (validated, by reference)
- `M-notable-tier-broaden` (in-progress, 9/~15)

## Species dropped

None. All 6 target species landed.

## Known gaps / carryovers

- NOTABLE tier still short of ~15 target (currently 9). Six more NOTABLE species needed across future cycles - outside Branch B scope.
- Deep source verification (`M-deep-verification`) not run for Branch B species yet; auditor pass expected in a later cycle.
- `sesbania-tomentosa` Kauaʻi contemporary-population documentation is thin; uncertainty block hedges appropriately.

## Cross-branch dependencies used

- Branch A's sharded-manifest infra (`M-manifest-sharding`, validated 01:50:12Z) - Branch B's `"B:N"` citation tokens and `images.branch-b.json` rely on this.
- Branch A's `_moderate/hala-uncertainty` artifact (`data/species/hala.yaml`) - Branch B's `_deferred/hala-status-uncertainty` closes by reference.

## Sign-off

Branch B has satisfied every criterion in its scoped objective. Handing to root conductor.
