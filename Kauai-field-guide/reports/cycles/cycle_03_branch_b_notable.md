---
created: 2026-08-28T03:45:00Z
cycle: 3
run_id: run-2026-08-28T005658Z
agent: worker
milestone: M-notable-tier-broaden
---

# Cycle 3 — Branch B — NOTABLE tier expansion (+6 → 15)

## Summary

Branch B added the six culturally significant natives and canoe plants
called for by the parent brief. NOTABLE tier now sits at **15/15**
(target hit). Total species across all tiers: **46** (common=20,
notable=15, rare_exotic=11 — comfortably above the 45-species run-end
minimum). Full validator suite is green.

## Species added

| Slug   | Scientific name            | Status                  | Zones                    | Photos | SVGs |
|--------|----------------------------|-------------------------|--------------------------|--------|------|
| aalii  | *Dodonaea viscosa* Jacq.   | indigenous              | sea_cliff, valley_mouth  | 1      | 2    |
| ki     | *Cordyline fruticosa*      | polynesian_introduction | valley_mouth, riparian   | 2      | 2    |
| noni   | *Morinda citrifolia*       | polynesian_introduction | valley_mouth, strand     | 3      | 1    |
| ko     | *Saccharum officinarum*    | polynesian_introduction | valley_mouth, riparian   | 2      | 2    |
| mamaki | *Pipturus albidus*         | endemic                 | valley_mouth, riparian   | 2      | 1    |
| kalo   | *Colocasia esculenta*      | polynesian_introduction | valley_mouth, riparian   | 2      | 1    |

Every species passes the ≥2-visual floor and carries a full
`how_to_identify` block with 2–4 clinchers plus at least one
look-alike.

## Image coverage and licenses

All 12 landed photos are Forest & Kim Starr, CC-BY-3.0, sourced via
Wikimedia Commons and downloaded through `scripts/fetch_images.py` with
full attribution/license/source metadata in `data/images.lock.json`.
Shard manifest is `data/images.branch-b.json`.

Six candidate images 404-failed at fetch (bad filenames from search-
based candidate selection) and were pruned from the shard manifest.
The SVG diagram fallback (part of the sharded infrastructure locked in
cycle 1) held the ≥2-visual floor for every species — most cleanly
visible on ʻaʻaliʻi (1 photo + 2 SVG = 3 visuals).

## References added

Six new references appended to `data/references/branch-b.md` as
`[B:9]`–`[B:14]`:

- **[B:9]** Handy, E. S. C. & Handy, E. G., with Pukui, M. K. (1972).
  *Native Planters in Old Hawaii*. Bishop Museum Bulletin 233. — Source
  of the kalo Hāloa tradition and cultivar diversity treatment; cited
  throughout the branch for cultural framing.
- **[B:10]** Krauss, B. H. (1993). *Plants in Hawaiian Culture*.
  University of Hawaiʻi Press.
- **[B:11]** Abbott, I. A. (1992). *Lāʻau Hawaiʻi: Traditional Hawaiian
  Uses of Plants*. Bishop Museum Press.
- **[B:12]** Kamakau, S. M. (1976). *The Works of the People of Old*.
  Bishop Museum Press.
- **[B:13]** National Tropical Botanical Garden. *Meet the Plants*.
- **[B:14]** Rock, J. F. (1913, reprinted 1974). *The Indigenous Trees
  of the Hawaiian Islands*. (Wood-use / material-culture claims for
  ʻaʻaliʻi and māmaki.)

## Kalo cultural-framing notes

Kalo was authored last, per the diagnostic ladder in the research
brief. The extended-checklist items are all satisfied and traceable in
`data/species/kalo.yaml`:

1. **Hāloa tradition present as sourced sidebar**, attributed to Handy
   & Handy 1972 [B:9] and the Kumulipo, framed as genealogical kin
   ("elder sibling of humankind") — not as an origin story about food.
   Presented in the `cultural_significance` field per the schema
   recommendation, not spread across ecology/notes.
2. **300+ pre-contact cultivar diversity** acknowledged with the
   loʻi-as-technology framing.
3. **Kalalau loʻi restoration** framed as ongoing stewardship
   ("visitors ... should understand they are looking at a working
   cultural site, not a historical artifact"), not history.
4. **Contemporary keepers** credited generally (Hawaiian
   practitioners, community organisations), no individual
   name-checking.
5. **No harvest, preparation, or poi-making instructions** anywhere.
   Explicit identification-only closing paragraph: "This guide
   provides identification only. … That knowledge lives in Hawaiian
   hands."
6. **Raw-corm/leaf calcium-oxalate hazard populated** in the
   `hazards` field with clear "do not sample" guidance.
7. **ʻape look-alike** (*Alocasia macrorrhizos*) present with the
   erect-leaf + raw-toxic distinction called out explicitly.

The `taxonomic_notes` field notes the fringe pre-Polynesian-arrival
position and states that the guide follows the mainstream Wagner /
Handy & Handy treatment. Per the brief's guidance we did **not**
render this as an `uncertainty:` block — the mainstream position is
strongly held and using the uncertainty renderer here would dilute the
pattern.

## Non-kalo cultural framing

The lighter cultural-framing checklist (name practice, credit keepers,
no harvest instructions, no sacred-context leak) was applied uniformly
to kī, noni, kō, ʻaʻaliʻi, and māmaki. In each species the
`cultural_significance` field names the practice and closes by
attributing transmission to "Hawaiian cultural practitioners" (and to
contemporary industries where relevant, e.g. commercial noni juice and
māmaki tea).

## Notable identification hooks

- **kī**: single unbranched palm-like stem topped by a rosette; ring-
  scarred stem; drooping panicle of small white-pink flowers; wild
  populations at Nā Pali valley bottoms are almost certainly Hawaiian
  planting remnants.
- **noni**: knobby-warty compound fruit-head with tubular white
  flowers projecting from it — no other Kauaʻi coastal plant has this.
- **kalo**: peltate leaf attachment (petiole meets underside of blade,
  not margin) + water-repellent leaf surface + wet-ground habitat.
- **kō**: giant grass 2–5 m tall with stout jointed cane and long
  arching leaves; distinct from *Miscanthus* / napier grass by cane
  thickness (finger-thick or thicker) and stem sweetness.
- **ʻaʻaliʻi**: papery three-winged fruit capsule in red/pink/yellow
  clustered at shoot tips — the colour on the plant is in the fruit,
  not the flower. Sticky-resinous leaves confirm.
- **māmaki**: three main veins emerge together from the leaf base;
  underside pale-whitish; **no stinging hairs** (worth calling out
  explicitly since it is in the nettle family).

## Look-alike bidirectionality

- māmaki mentions olonā (*Touchardia latifolia*) — not currently in the
  guide; one-way reference is fine.
- kalo mentions ʻape (*Alocasia macrorrhizos*) — not in the guide;
  one-way reference is fine and the toxicity note in the look-alike
  block is safety-critical.
- kō mentions *Miscanthus* and *Pennisetum purpureum* — not in the
  guide; one-way reference is fine.

## Dropped species

None. All 6 targets landed on the first pass.

## Shard-write discipline

- Wrote only to `data/images.branch-b.json` (added 18 entries, kept 12
  after fetch pruning).
- Wrote only to `data/references/branch-b.md` (appended [9]–[14]).
- Added 6 new species YAMLs under `data/species/` — the standard
  location; no shard-specific species dir exists.
- Species citations use `B:N` tokens exclusively for branch-local
  references; core references (1, 2, 3) are used by number as before.

## Ledger events (canonical schema, worker assessor)

Emitted via `long_exposure.tools.ledger_append` (routes to per-clone
shadow ledger under `AGENT_FORK_ID=1a2a754ccd76`, clone-1):

- `eea7793a-b7bb-4909-b0ce-4ff12e9c86db` — Branch B canary (ʻaʻaliʻi)
  end-to-end. Milestone: M-notable-tier-broaden. Status: in-progress.
- `358dfd64-c382-47d9-a57e-e378048c1c1e` — Branch B NOTABLE-tier
  expansion +6 complete. Milestone: M-notable-tier-broaden. Status:
  validated.
- `757d883b-9d07-46a6-a092-f9e9eef5e47d` — Kalo cultural-framing
  checklist held. Milestone: M-notable-tier-broaden. Status:
  validated.
- `de542c66-f8a3-493f-acd7-27f07a8a1895` — Image fetch summary
  (12 landed, 6 pruned). Milestone: M-image-pipeline. Status:
  validated.
- `19017386-5b17-42ef-88d5-807895e97fc5` — Branch B cycle-3 close.
  Milestone: `_run/branch-b-cycle-3-close`. Status: validated.

## Validator results

- `scripts/build_site.py`: 46 species pages + 5 static; 36 citation
  tokens resolved.
- `scripts/check_coverage.py`: 46 species; per-tier common=20
  notable=15 rare_exotic=11; OK.
- `scripts/lint_site.py`: 51 HTML, 0 external asset URLs.
- `scripts/check_links.py`: 51 pages, all internal links resolve.
- `scripts/check_offline.py`: 51 HTML, safe for `file://`.
- `tests/test_validators.py`: 5/5 PASS (bad species, empty
  look_alikes, non-allowed license, external URL, missing link).
- `tests/test_build_merge.py`: 3/3 PASS (duplicate id, shard order,
  unresolved token).

## Handoff to branch auditor

Branch B invites the branch auditor to spot-check:

1. **Kalo cultural section** — most important. Verify Hāloa framing
   reads as genealogical kin (not food narrative), verify no harvest
   instructions have leaked in.
2. **māmaki "no stinging hairs" call-out** — verify this is presented
   as a positive ID feature, not buried.
3. **ʻaʻaliʻi three-winged fruit** — verify this reads as *the*
   diagnostic feature (colour is on the fruit, not the flower).
4. **Look-alike blocks** — verify all 6 species have at least one
   populated look-alike (they do).
5. **Photo license spot-check** — pick 3 random branch-b image ids
   and confirm CC-BY-3.0 Starr Environmental provenance in
   `data/images.lock.json`.
