---
created: 2026-08-28T04:00:00Z
cycle: 3
run_id: run-2026-08-28T005658Z
agent: worker
milestone: M-common-tier-broaden
branch: A
fork: 1a2a754ccd76
clone: 0
---

# Cycle 3, Branch A — COMMON Tier Expansion (+8, target 20 hit)

## Summary

Branch A cycle 3 adds 8 well-documented indigenous COMMON-tier species,
bringing the COMMON tier to 20 (directive floor). All 8 are Wagner /
Herbst / Sohmer + NTBG + Smithsonian FHI attested, all photos are
CC-BY-3.0 Starr Environmental via Wikimedia Commons, and all edits
respect the sharded-manifest discipline. Branch A itself is validation-
green in scope; cross-branch contamination is documented separately
below.

## Species Landed

| Slug | Scientific name | Hawaiian | Family (APG) | Zone(s) | Photos | Look-alikes |
|------|-----------------|----------|--------------|---------|:------:|:-----------:|
| chenopodium-oahuense | *Chenopodium oahuense* (Meyen) Aellen | ʻāweoweo | Amaranthaceae | strand, sea_cliff, valley_mouth | 3 | 2 |
| heliotropium-anomalum | *Heliotropium anomalum* Hook. & Arn. var. *argenteum* A.Gray | hinahina kū kahakai | Boraginaceae | strand, dune | 3 | 2 |
| sesuvium-portulacastrum | *Sesuvium portulacastrum* (L.) L. | ʻākulikuli kai | Aizoaceae | strand | 3 | 2 |
| waltheria-indica | *Waltheria indica* L. | ʻuhaloa | Malvaceae | strand, sea_cliff, valley_mouth | 3 | 2 |
| portulaca-lutea | *Portulaca lutea* Sol. ex G.Forst. | ʻihi | Portulacaceae | strand, sea_cliff, dune | 3 | 3 |
| cassytha-filiformis | *Cassytha filiformis* L. | kaunaʻoa pehu | Lauraceae | strand, sea_cliff, valley_mouth | 3 | 2 |
| cyperus-polystachyos | *Cyperus polystachyos* Rottb. | puʻukaʻa | Cyperaceae | strand, valley_mouth | 3 | 3 |
| ipomoea-imperati | *Ipomoea imperati* (Vahl) Griseb. | hunakai | Convolvulaceae | strand, dune | 3 | 3 |

**Totals:** 8 species × 3 photos = 24 new image entries; 20 look-alikes;
5 new references (A:10–A:14).

## Visual Coverage & Licensing

- **All 24 photos** are CC-BY-3.0, author Forest & Kim Starr, source
  Wikimedia Commons (Starr Environmental). No CC-BY-2.x used (Branch C
  handles the allow-list extension).
- All entries in `data/images.branch-a.json`; all downloaded to
  `site/assets/photos/<sha256[:12]>.jpg` and recorded in
  `data/images.lock.json`.
- Every species has a habit shot + a diagnostic-feature close-up
  (flower / leaf / rosette / seedhead) + a supplementary view.
- Notable image picks:
  - `a-heliotropium-anomalum-flowers-01` — shows both the tiny white
    yellow-throated flowers and the diagnostic scorpioid coiled cyme.
  - `a-cassytha-filiformis-on-host-01` — smothering an ʻaʻaliʻi;
    haustorial attachments visible.
  - `a-ipomoea-imperati-habit-flowers-01` — shows the WHITE funnel
    flowers alongside variable leaves (entire ovate + lobed on the
    same runner), the strongest single ID cue vs. pōhuehue.
  - `a-cyperus-polystachyos-seedheads-01` — leaf-like bracts overtop
    the head, the diagnostic contrast against Fimbristylis.

## Verification Methodology (per species)

Each anchor from the research brief was verified against Wagner,
Herbst, and Sohmer (1999) *Manual of the Flowering Plants of Hawaiʻi*
(A:1), the Smithsonian *Flora of the Hawaiian Islands* online database
(A:12), NTBG plant profiles (A:7), and — where relevant — the Bishop
Museum Checklist (A:6). Nāpali Coast occurrence for ʻāweoweo, hinahina
kū kahakai, and kaunaʻoa pehu is corroborated by Wood 2007 NTBG survey
report (A:14). The Krauss 1993 *Plants in Hawaiian Culture* reference
(A:11) grounds the ʻuhaloa lāʻau lapaʻau significance; the Hawaiʻi DOA
extension bulletin (A:13) grounds the Cassytha alkaloid toxicity note.
APG IV (A:10) grounds both family-placement notes.

## Bidirectional Look-Alike Edits (auditor-checked)

- **`data/species/pohuehue.yaml`** gains an `Ipomoea imperati (hunakai)`
  entry in `look_alikes`, with a distinguishing note: white vs magenta
  flowers, polymorphic leaves.
- **`data/species/fimbristylis-cymosa.yaml`**'s Cyperus polystachyos
  entry rewritten with the puʻukaʻa Hawaiian name and the overtopping-
  bracts / substrate distinction (previously mislabeled with a different
  Hawaiian name).

## Cassytha Hazards Discipline

The `hazards` field of `cassytha-filiformis.yaml` opens with:

```
<strong>TOXIC — do not consume.</strong> The vine and its small white
berries contain alkaloids (including aporphine-type alkaloids) and
are not edible.
```

This lands at the top of the hazards field (not buried in ecology),
per the brief. Cycle-2's `.hazards` CSS sharpening renders the block
prominently.

## Family-Placement (APG IV vs Wagner)

Both APG discrepancies are handled via a new `taxonomic_notes:` field
on the affected species records:

- **`chenopodium-oahuense`** → `family: Amaranthaceae` +
  `taxonomic_notes: "Wagner treats as Chenopodiaceae; the current APG IV
  classification merges Chenopodiaceae into Amaranthaceae s.l."`
- **`waltheria-indica`** → `family: Malvaceae` + parallel note for
  Sterculiaceae → Malvaceae. Consistent with milo (`Thespesia populnea`)
  already Malvaceae in the guide.

`taxonomic_notes` is an optional new schema field; the current
`build_site.py` will pass it through if it recognizes the key, otherwise
the data is preserved for later rendering. `check_coverage.py` does not
enforce nor forbid it (it is not in `REQUIRED_TOP`).

## Ledger Events Emitted

6 canonical-schema events via `ledger_append`:

1. `M-common-tier-broaden` — status `validated` (target 20 reached).
2. `_infra/branch-a-cycle-3-bidirectional-look-alikes` — validated.
3. `_infra/branch-a-cycle-3-family-placement` — validated.
4. `_infra/branch-a-cycle-3-hazards-placement` — validated.
5. `_orphan/branch-a-cycle-3-cross-branch-contamination-observed` —
   in-progress (documents observations for root-conductor rollup).
6. `_run/branch-a-cycle-3-close` — validated.

All events carry `event_id`, `ts`, `run_id`, `cycle: 3`, `agent: worker`,
`confidence.assessor: worker`, and appropriate namespace prefixes.

## Validator Run Summary (workspace-wide)

| Validator | Result | Notes |
|-----------|--------|-------|
| `check_coverage.py` | 39 species; common=20 notable=9 rare_exotic=10; 2 errors | **Both errors from `kokia-kauaiensis` (cross-branch, not Branch A)**: missing SVG `flower-kokia-red-spiral.svg`, unresolved citation `C:7`. |
| `build_site.py` | Fails on kokia-kauaiensis unresolved C:7 | Cross-branch; Branch A species all render. |
| `lint_site.py` | OK — 43 HTML files, no external URLs | Green. |
| `check_offline.py` | OK — safe for file:// | Green. |
| `check_links.py` | 7 broken links | **All cross-branch**: 3× kokia species page missing (build failed on it), 2× broken `references.html#ref-46` / `#ref-48` on `hibiscus-waimeae-hannerae` and `mauritian-hemp` (appears to be partial rollback of cycle-2 shard migration), 2× missing `6098886469ff.jpg` for panicum-niihauense. **None on Branch A species.** |

**Branch A itself is validation-green in scope.** All 8 new species
pass coverage individually; all photos downloaded and license-verified;
all citations resolve.

## Cross-Branch Contamination (out of scope for Branch A)

The workspace has picked up in-flight edits from parallel fan-out
clones that produce validation errors. Enumerated in
`_orphan/branch-a-cycle-3-cross-branch-contamination-observed`:

1. **`data/species/kokia-kauaiensis.yaml`** — added at 02:57 by another
   clone (Branch C most likely; token prefix is `C:`), cites `C:7` but
   `data/references/branch-c.md` has only 6 refs. Also cites diagram
   `flower-kokia-red-spiral.svg` which is absent from
   `site/assets/diagrams/`. → Root conductor / Branch C should complete
   these before rollup.
2. **Reverted citations on Branch C species** — `hibiscus-waimeae-hannerae`
   and `mauritian-hemp` now reference bare integers 46 and 48 that have
   no anchors in `references.html`. Cycle-2 close reported these as
   correctly migrated to `A:*`/`C:*` tokens; the current state looks
   like a partial rollback.
3. **Missing photo file** — `site/assets/photos/6098886469ff.jpg`
   (panicum-niihauense) is referenced by `credits.html` and
   `panicum-niihauense.html` but does not exist on disk.

Branch A did not touch any of these files or shard manifests, per the
branch discipline in the brief. All 3 items are documented on the
ledger for root-conductor triage.

## Sufficiency Criteria Check (from the brief)

| Criterion | Result |
|-----------|:------:|
| 8 new YAML files land under `data/species/` (8 slugs listed) | ✅ |
| Each new species: ≥2 verified-license photos (target 3) | ✅ (3 each) |
| Each new species: full "How to identify" block | ✅ |
| Each new species: ≥1 look-alike | ✅ (2–3 each) |
| Each new species: populated all required fields | ✅ |
| Each new species: ≥1 `A:N` citation | ✅ |
| `data/images.branch-a.json` gains ≥16 new entries with full attribution/license | ✅ (24 entries) |
| `data/references/branch-a.md` gains new `A:N` refs actually cited | ✅ (A:10–A:14) |
| Bidirectional look-alike edits on `fimbristylis-cymosa` and `pohuehue` | ✅ |
| Family-placement `taxonomic_notes` for Chenopodium and Waltheria | ✅ |
| Cassytha hazards prominent, not buried | ✅ |
| `check_coverage.py` reports `common >= 20` | ✅ (common=20) |
| Full validator suite green on Branch A scope | ✅ (workspace-wide has cross-branch contamination) |
| All new Branch A ledger events use canonical schema | ✅ (6 events, all with `event_id`, `ts`, `confidence.assessor: worker`) |
| Merge report at this path | ✅ |

## Known Gaps

- `taxonomic_notes` is a new optional schema field. The current
  `build_site.py` may not render it as a labeled section on the species
  page. This is a future rendering polish item; the data is present
  and preserved for downstream cycles.
- `Portulaca lutea` carries a small `uncertainty:` block. Wagner
  treatment is followed (indigenous) — the block is defensive and can
  be dropped in a future cycle if a firmer consensus is confirmed.
- Cross-branch contamination will need coordination at rollup: Branch C
  should finish `kokia-kauaiensis` (add SVG, add C:7 ref, or drop the
  bad citation) and re-migrate `hibiscus-waimeae-hannerae` /
  `mauritian-hemp` citations, and restore the missing panicum photo.

## Next Cycle Handoff

- COMMON tier: **DONE** (20/20). Any further COMMON additions are
  optional beyond the directive.
- NOTABLE tier: 9/15 — 6 species remain (researcher should surface
  candidates such as ʻohai, ʻūlei, alahe`e-kuahiwi, kolomona-a-Wai`ale`ale).
- RARE tier: 10/10 (with the disputed kokia counted) — the directive
  target is met once kokia's issues are fixed; otherwise 9/10 with
  Delissea rhytidosperma / Nototrichium humile in reserve.
- Deep verification pass (`M-deep-verification`) remains queued.
