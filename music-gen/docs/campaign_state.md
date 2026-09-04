---
created: 2026-09-04T05:20:00Z
cycle: 19
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/state
---

# Music-Gen v4 closure campaign — state snapshot

Refreshed at c19. Ceremony docs like this live next to the on-disk
artifacts they summarize; the promise ledger is authoritative for
per-milestone status.

## Focus songs (5) — skeleton coverage 5/5

| SHA-16              | Title                | Section        | v4 status           |
|:--------------------|:---------------------|:---------------|:--------------------|
| `31a164f845f8e27e`  | Chicken Grease       | 233.64..263.64 | **SHOWCASE render LANDS_pending_operator** (c17); test-anchored c18; LUFS c18; LUFS test-anchored c19 |
| `252eb21ce7df7328`  | What If I Go (WIG)   | 72.77..102.77  | stem manifest opened c17; blocked on M-V4-METRIC-SEMANTICS-c16 |
| `51e433ade2a845e1`  | Rome                 | 62.74..92.74   | stem manifest opened c18; blocked on M-V4-METRIC-SEMANTICS-c16 |
| `cdd2717e52820ff6`  | Disco A              | 21.92..51.92   | stem manifest opened c19; blocked on M-V4-METRIC-SEMANTICS-c16 |
| `88d247468cb6d49f`  | Peach Dream          | 172.87..202.87 | stem manifest opened c19 (non-standard path via c25-checkpointed run; invariant (d) disclosed); blocked on M-V4-METRIC-SEMANTICS-c16 |

## Milestones

| Milestone                | Status                            | Notes |
|:-------------------------|:----------------------------------|:------|
| M-V4-CERT-1              | validated/high (E2E holds 2026-09-03) | env_pin_sha256 `623df01f…` |
| M-V4-PROFILES-1          | in-progress (5/5 focus-song skeletons opened; CG cells terminal) | stage-1 sweeps for WIG/Rome/Disco A/Peach Dream blocked on Track 2 metric-semantics |
| M-V4-SHOWCASE-1          | **LANDS_pending_operator (rendered + regression-tested)** | cg_ab_mix.wav SHA `6e13e007…f9484b`; 12/12 c18 tests green; LUFS diagnostic 7/7 c19 tests green |
| M-V4-RULES-1             | schema v1 + validator + rationale doc landed | permissive per invariants (d)+(e); scaffold deferred from c19 → c20 |
| M-V4-EAR-1               | not started                       | exemplar-based per operator simplification 2026-09-03 |
| M-V4-GEN-1               | not started                       | opens on M-V4-RULES + M-V4-EAR lands |
| M-V4-CLOSE-1             | not started                       | opens on M-V4-GEN lands |
| _manager/M-V4-METRIC-SEMANTICS-c16 | blocked_on_operator (unchanged) | Path A vs Path B; c17/c18/c19 do not adjudicate |

## Chicken Grease (mandatory focus) — instrument cells

| Cell   | Verdict / disposition                                      |
|:-------|:-----------------------------------------------------------|
| bass   | `bass_v2` sf2 accepted as WINNER (composite-relative per operator directive 2026-09-03 part 1) |
| drums  | OPT3 (htdemucs stem substitution, per c14 acceptance fork) |
| guitar | OPT3 (htdemucs stem substitution, per c15 acceptance fork) |
| piano  | NULL (audibility-grounded c14; reference stem LUFS-I = -∞) |
| other  | NULL (audibility-grounded c14; reference stem LUFS-I ≈ -69.7) |
| vocals | htdemucs hybrid overlay (per campaign prompt L59-60)       |

## c18 deliverables (this cycle)

1. `tests/test_deliver_cg_ab_v4_full_render.py` — 12 regression cases green
2. `docs/sound_match/cg_ab_bass_gain_clarification_c18.md` — closes c17 auditor MODERATE #1 (narrative "attenuation" → artifact "amplification 2.688385")
3. `data/v4/profiles/51e433ade2a845e1/stem_manifest.json` — Rome skeleton opened
4. `docs/pinned_profile_schema_v1_rationale.md` — closes c17 auditor MODERATE #2 ("fabricated invariant" wording); invariants (d)+(e) formally cited
5. `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.lufs_diagnostic.json` — LUFS-I sidecar (diagnostic only, does not mutate audio)
6. Ledger events + this state snapshot + housekeeping

## Discipline anchors preserved byte-identical pre==post c18

- `cg_ab_mix.wav` (sha `6e13e0075c5d8116…`)
- `cg_ab_mix.manifest.json` (sha `f9f1c9edce944c27…`)
- `cg_ab_mix.replay_proof.json` (sha `fcd8e6878b13818f…`)
- `pinned_profile_schema_v1.json` (sha `8f61d9391a5a3bcf…`)
- `profile_validator.py` (sha `cd17106f651e9de7…`)
- `test_pinned_profile_schema.py` (sha `9450ca4eb599fa4b…`)
- CG c9 bass, c14 drums, c15 guitar pinned profiles
- `embedding_panel.py`, `objective.py` — c14/c1 READ-ONLY anchors

## Operator authority

Operator ear on `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav`
remains the only authority for M-V4-SHOWCASE-1 LANDS per FD-6. All
internal gates green; no wait-on-operator memo emitted (BANNED per
operator directive 2026-09-03 part 2).
