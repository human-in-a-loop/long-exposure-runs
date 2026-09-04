---
created: 2026-09-04T06:00:00Z
cycle: 20
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/state
---

# Music-Gen v4 closure campaign — state snapshot

Refreshed at c20. Ceremony docs like this live next to the on-disk
artifacts they summarize; the promise ledger is authoritative for
per-milestone status.

## Focus songs (5) — skeleton coverage 5/5 (unchanged since c19)

| SHA-16              | Title                | Section        | v4 status           |
|:--------------------|:---------------------|:---------------|:--------------------|
| `31a164f845f8e27e`  | Chicken Grease       | 233.64..263.64 | **SHOWCASE render LANDS_pending_operator** (c17); regression-tested c18; LUFS diagnostic c18; LUFS test-anchored c19; FETCH_FAIL fixture c20 |
| `252eb21ce7df7328`  | What If I Go (WIG)   | 72.77..102.77  | stem manifest opened c17; blocked on M-V4-METRIC-SEMANTICS-c16 |
| `51e433ade2a845e1`  | Rome                 | 62.74..92.74   | stem manifest opened c18; blocked on M-V4-METRIC-SEMANTICS-c16 |
| `cdd2717e52820ff6`  | Disco A              | 21.92..51.92   | stem manifest opened c19; blocked on M-V4-METRIC-SEMANTICS-c16 |
| `88d247468cb6d49f`  | Peach Dream          | 172.87..202.87 | stem manifest opened c19 (non-standard path via c25-checkpointed run; invariant (d) disclosed); blocked on M-V4-METRIC-SEMANTICS-c16 |

## Milestones

| Milestone                | Status                            | Notes |
|:-------------------------|:----------------------------------|:------|
| M-V4-CERT-1              | validated/high (E2E holds 2026-09-03) | env_pin_sha256 `623df01f…` |
| M-V4-PROFILES-1          | in-progress (5/5 focus-song skeletons opened; CG cells terminal) | stage-1 sweeps for WIG/Rome/Disco A/Peach Dream blocked on Track 2 metric-semantics |
| M-V4-SHOWCASE-1          | **LANDS_pending_operator (rendered + regression-tested)** | cg_ab_mix.wav SHA `6e13e007…f9484b`; 12/12 c18 tests green; LUFS 8/8 tests green (c19 7 + c20 FETCH_FAIL 1) |
| M-V4-RULES-1             | **scaffold landed c20**; substantive extraction queued c21+ | `scripts/v4_rules/{__init__,extract_v4}.py` stubs raise `NotImplementedError('c21+ substantive implementation')`; `data/v4/rules/scaffold_smoke_test.json` records fetchability + env_pin |
| M-V4-EAR-1               | not started                       | exemplar-based per operator simplification 2026-09-03 |
| M-V4-GEN-1               | not started                       | opens on M-V4-RULES + M-V4-EAR lands |
| M-V4-CLOSE-1             | not started                       | opens on M-V4-GEN lands |
| _manager/M-V4-METRIC-SEMANTICS-c16 | blocked_on_operator (unchanged) | Path A vs Path B; c17→c20 do not adjudicate |

## Chicken Grease (mandatory focus) — instrument cells (unchanged)

| Cell   | Verdict / disposition                                      |
|:-------|:-----------------------------------------------------------|
| bass   | `bass_v2` sf2 accepted as WINNER (composite-relative per operator directive 2026-09-03 part 1) |
| drums  | OPT3 (htdemucs stem substitution, per c14 acceptance fork) |
| guitar | OPT3 (htdemucs stem substitution, per c15 acceptance fork) |
| piano  | NULL (audibility-grounded c14; reference stem LUFS-I = -∞) |
| other  | NULL (audibility-grounded c14; reference stem LUFS-I ≈ -69.7) |
| vocals | htdemucs hybrid overlay (per campaign prompt L59-60)       |

## c20 deliverables (this cycle)

1. **Track 1 (PRIMARY)** — M-V4-RULES-1 scaffold. `scripts/v4_rules/__init__.py`
   + `scripts/v4_rules/extract_v4.py` (stubs, `NotImplementedError('c21+
   substantive implementation')`); `data/v4/rules/scaffold_smoke_test.json`
   (fetchability probe outcomes for music21/mingus/jsonschema/sklearn — no
   fetch attempted; env_pin canonical 7-key `2ac444c3…922ca`; stub contract
   verified).
2. **Track 2 (SECONDARY)** — LUFS-diagnostic FETCH_FAIL negative fixture. Extended
   `tests/test_measure_cg_ab_mix_lufs.py` from 7 → 8 cases (test_08 simulates
   `pyloudnorm` unavailability via `sys.modules` shim in an isolated
   `tempfile.mkdtemp()` tree; asserts FETCH_FAIL row shape + audio bytes
   unchanged; c18 anchor JSON + c17 mix WAV byte-identical pre==post).
3. **Track 3 (this doc)** — campaign_state.md refresh.
4. **Track 4** — POR rows + ledger events + housekeeping.

## Discipline anchors preserved byte-identical pre==post c20

- `cg_ab_mix.wav` (sha `6e13e0075c5d8116…f9484b`)
- `cg_ab_mix.lufs_diagnostic.json` (sha `6810d5056edf5889…647b6b`)
- 4 stem manifests: `13e21d69…` (WIG), `e00bd15d…` (Rome), `acadbf25…` (Disco A), `c4944ee8…` (Peach Dream)
- `pinned_profile_schema_v1.json` (sha `8f61d9391a5a3bcf…`)
- `profile_validator.py` (sha `cd17106f651e9de7…`)
- `test_deliver_cg_ab_v4_full_render.py` (sha `97fc6253…`)
- `test_pinned_profile_schema.py` (sha `9450ca4e…`)
- READ-ONLY c23 v3-rules anchors: `scripts/v3_rules/extract_rules.py`
  (sha `9af3e37c…`) + `data/v3/rules/rules_artifact.jsonl` (sha `e19fb205…`)
- CG c9 bass, c14 drums, c15 guitar pinned profiles
- `embedding_panel.py`, `objective.py` — c14/c1 READ-ONLY anchors

## Cross-cycle test coverage

53 (c16 28 + c17 6 + c18 12 + c19 7) + c20 1 = **54 cross-cycle tests green**.

## Operator authority

Operator ear on `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav`
remains the only authority for M-V4-SHOWCASE-1 LANDS per FD-6. All
internal gates green; no wait-on-operator memo emitted (BANNED per
operator directive 2026-09-03 part 2). M-V4-RULES-1 substantive
implementation (Model A statistical + Model B CA/VOMM sequence) is
c21+ scope per campaign prompt closure-milestone ordering.
