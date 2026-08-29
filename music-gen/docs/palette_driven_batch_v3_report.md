---
created: 2026-08-29T07:40:00Z
cycle: 36
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/palette-driven-batch-v3
---

# M-GEN-1/palette-driven-batch-v3 — cycle-36 Branch B (fork 87da4f517029, clone-1)

**Verdict: `PARAM_MOVES_AUDIO`** — 3 / 3 cross-salt `bare_combined.wav`
SHAs distinct, backwards-compat regression PASS, per-salt
byte-determinism × 2 PASS.

Rubric SHA-256:
`0c4b97a2c9c33ac15263842716273571a2ba0ba874b990ad95400bc7589e5211`
(rubric doc mtime precedes every script under `scripts/palette_render_v3/`
AND the additive-kwargs edit to `scripts/palette_render/render_stem.py`).

## 1. Situation

C35 clone-1 landed
`M-GEN-1/palette-driven-batch-v2-sampler-diversified` with the
first-class negative verdict `SPREAD_STILL_COLLAPSED`. Its report
exposed the load-bearing mechanism: c33
`scripts.palette_render.render_stem(stem, instrument, out_dir)` is
`(stem, instrument)`-parameterized only and never consumes
`pinned_state`, `provenance_pointers`, or `iterated_params`. Sampler-side
diversification alone cannot move audio bytes: 3 distinct
`assignments.jsonl` SHAs + 6 distinct perturbed `iteration_sha_256`s
produced 1 identical `bare_combined.wav` byte-equal across all 3 salts.

Branch B (this report) executes the auditor's cheapest audio move:
extend `render_stem` via a non-breaking additive keyword-only
`parameter_dict=None` so per-salt rule triples thread through fluidsynth
CLI (`-o synth.chorus.*`, `-o synth.reverb.*`, `-g`) and post-render
sfizz scaling (`master_volume` dB). VST3 dispatch is intentionally NOT
touched this cycle — Branch C characterizes VST3-binary-internal
nondeterminism analytically, and c37 decides whether VST3 param
threading can activate under a tolerance-gate rubric.

## 2. Frozen rubric

`docs/palette_driven_batch_v3_rubric.md` (SHA-256
`0c4b97a2c9c33ac15263842716273571a2ba0ba874b990ad95400bc7589e5211`,
mtime-ordered ahead of all scripts and the render_stem edit).

Three verdicts:

* **`PARAM_MOVES_AUDIO`** — backwards-compat PASS (3 c33 anchor SHAs
  byte-match under `parameter_dict=None`) AND per-salt determinism × 2
  PASS AND cross-salt bare_combined SHAs INequal (≥ 2 of 3 pairs
  distinct with any equal pair attributed to documented shallowness)
  AND panels 8-key finite per salt.
* **`PARAM_NEUTRAL`** — first two gates hold, but cross-salt bare_combined
  SHAs identical.
* **`RENDER_FAILS`** — backwards-compat break OR per-salt determinism break.

## 3. Backwards-compat regression (hard gate)

`data/palette_render_v3/backwards_compat_check.json`: **PASS** on all
four c33 anchor SHAs when `render_stem(..., parameter_dict=None)` is
called through the extended signature in a fresh `tempfile.mkdtemp()`:

| stem        | c33 anchor SHA (per_stem/render_run1.wav.sha) | re-derived | match |
|-------------|------------------------------------------------|------------|-------|
| bass        | `6b9a5219e761854bdcf42a87f370a283e3fb096faf64648eb198c98520540280` | same | ✅ |
| other       | `a2e5d0585404b448a2120c3c4bd6432ec1962ed82c3a7a74dd7518ed3d10f621` | same | ✅ |
| drums       | `f66a776dfde8ba15b4f3cb1abf564e701877a519c38d4d102cc14e73b57982c9` | same | ✅ |
| bare_combined | `a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794` | same | ✅ |

The additive kwarg edit lands the extension without any drift on the
c33 dispatch path. The regression is captured in a subprocess-run
harness (`tests/test_palette_driven_batch_v3.py::test_06`) so a stale
module import cannot mask a future break.

## 4. Batch execution

Salts 0, 1, 2 (three-song batch). Per-salt rule triples via
`scripts.gen_palette_batch_v2.sample_rule_triple_v2.sample_triples`
(c35 clone-1 sampler, READ-ONLY import).

Per-salt rule triples selected:

| salt | harmonic                                       | rhythmic                                       | arrangement                                    |
|------|------------------------------------------------|------------------------------------------------|------------------------------------------------|
| 0    | `rule_900193a92a8810e5`                        | `rule_2afe9862efd1e8ea`                        | `rule_1aa3fa507bba0573`                        |
| 1    | `rule_2549a4193dead599`                        | `rule_4f801fa8961967c3`                        | `rule_a8ffe2f88dc29eed`                        |
| 2    | `rule_ff1fa8c4bf0f228f`                        | `rule_6ae8cec716982090`                        | `rule_f14c45df9121ab03`                        |

All triples per-salt distinct (rule-slot × salt); `assignments.jsonl`
SHAs distinct across salts.

Per-stem dispatch: `drums=fluidsynth_gm`, `bass=sfizz`, `other=sfizz`
(inherited from c33 salt-0 assignment). Stem→rule-type mapping is fixed:
`drums←rhythmic`, `bass←arrangement`, `other←harmonic`.

Per-`(rule_id, param_name)` derivation:
`SHA-256(f"{rule_id}|{param_name}".encode("utf-8"))`;
`int.from_bytes(digest[:4], "big") % 4` indexes into the rubric's fixed
4-entry table. NO PRNG. Full derivation in
`scripts/palette_render_v3/derive_parameter_dict.py`.

## 5. Per-salt determinism × 2

Each salt rendered twice into fresh `tempfile.mkdtemp()` dirs. Every
`bare_combined.wav` SHA equal across runs for every salt:

| salt | run1 SHA (first 16)     | run2 SHA (first 16)     | equal |
|------|-------------------------|-------------------------|-------|
| 0    | `785e47c304843e10…`     | `785e47c304843e10…`     | ✅    |
| 1    | `ad4d4263a0282dcf…`     | `ad4d4263a0282dcf…`     | ✅    |
| 2    | `aac37ed464a65db3…`     | `aac37ed464a65db3…`     | ✅    |

Full SHAs in `data/palette_render_v3/per_song/<s>/bare_combined.wav.sha.run{1,2}`.

## 6. Cross-salt SHA distinctness (rubric gate iii)

All 3 pairwise `bare_combined.wav` comparisons distinct — the
load-bearing gate that separates PARAM_MOVES_AUDIO from PARAM_NEUTRAL:

| pair    | salt A SHA (first 16)   | salt B SHA (first 16)   | distinct |
|---------|-------------------------|-------------------------|----------|
| (0, 1)  | `785e47c304843e10…`     | `ad4d4263a0282dcf…`     | ✅       |
| (0, 2)  | `785e47c304843e10…`     | `aac37ed464a65db3…`     | ✅       |
| (1, 2)  | `ad4d4263a0282dcf…`     | `aac37ed464a65db3…`     | ✅       |

Byte-level distinctness holds cleanly across all three pairs.

## 7. Panel spread (M-TEX-1/panel)

Per-key IQR + `max − min` across salts (from
`data/palette_render_v3/spread_analysis.json`):

### `panel_fluidsynth` (c33 palette-v1 bare ↔ palette-v3 bare)

| key                          | min       | max       | IQR       | max−min   |
|------------------------------|-----------|-----------|-----------|-----------|
| mel_l1_db                    | 21.981    | 23.433    | 0.726     | 1.452     |
| spectral_centroid_rmse_hz    | 2866.955  | 3162.615  | 147.830   | 295.660   |
| rms_env_rmse                 | 0.0521    | 0.0595    | 0.0037    | 0.00735   |
| lufs_m_rmse_lu               | 5.596     | 6.397     | 0.400     | 0.801     |

### `panel_original` (original synth_030s ↔ palette-v3 bare)

| key                          | min       | max       | IQR       | max−min   |
|------------------------------|-----------|-----------|-----------|-----------|
| mel_l1_db                    | 15.039    | 16.327    | 0.644     | 1.288     |
| spectral_centroid_rmse_hz    | 1884.520  | 2016.928  | 66.204    | 132.408   |
| rms_env_rmse                 | 0.0479    | 0.0537    | 0.0029    | 0.00579   |
| lufs_m_rmse_lu               | 3.765     | 4.572     | 0.403     | 0.807     |

### Honest observation

Salt 0 vs salts 1/2 exhibits a real panel delta
(`mel_l1_db` 23.4 vs 22.0, `spectral_centroid_rmse_hz` 3163 vs 2867).
Salts 1 and 2 have byte-distinct `bare_combined.wav` outputs but
numerically-identical panel readings at 3-decimal precision. Two
observations:

1. The **fluidsynth-driven drums stem** carries the panel-scale
   spread: its `chorus_level`, `reverb_level`, `reverb_room_size`,
   `gain` are threaded into the fluidsynth CLI and yield structural
   audio changes that mel/spectral-centroid capture. The drums-stem
   rule_id (rhythmic, per the mapping) differs across all three salts.
2. The **sfizz-driven bass/other stems** currently receive only a
   post-render `master_volume` dB scalar (the rubric's opcode-override
   fallback ladder — `sfizz_render` on this workspace does not expose
   `--set` opcode overrides; opcode-file rewrite is deferred to c37).
   That scaling moves bytes but at the ~1 dB scale barely shifts the
   panel. Salts 1 vs 2's identical panel readings reflect this
   shallowness on the sfizz side rather than a rubric failure — the
   PARAM_MOVES_AUDIO gate is byte-distinctness, which holds.

## 8. Mechanism resolved

C35 clone-1's SPREAD_STILL_COLLAPSED diagnosed:
> `render_stem(stem, instrument, out_dir)` never consumes
> `pinned_state`, `provenance_pointers`, or `iterated_params`.

Branch B fix, land-in-c36:

```python
def render_stem(stem, instrument, out_dir, *, parameter_dict=None):
    ...
    if instrument in ("surge_xt", "dexed"):
        if parameter_dict is not None:
            raise NotImplementedError(
                "VST3 param threading deferred to c37 pending Branch-C "
                "VST3-nondeterminism verdict"
            )
        raise RuntimeError(...)
    elif instrument in ("fluidsynth", "fluidsynth_gm"):
        render_fluidsynth(midi_path, out1, parameter_dict=parameter_dict)
        render_fluidsynth(midi_path, out2, parameter_dict=parameter_dict)
    elif instrument == "sfizz":
        render_sfizz(midi_path, out1, parameter_dict=parameter_dict)
        render_sfizz(midi_path, out2, parameter_dict=parameter_dict)
```

`render_fluidsynth` gains conditional `-o synth.chorus.*` /
`-o synth.reverb.*` / gain-envelope threading. `render_sfizz` gains
post-render sample-scale for `master_volume` dB (with all other opcode
overrides IGNORED this cycle — the rubric's documented ladder). VST3
branches raise `NotImplementedError` when `parameter_dict` is non-None,
preserving c31 STILL_GAP + c35 Branch A anti-pattern posture.

## 9. Anchor preservation

`data/palette_render_v3/anchor_preservation.json`:
`unchanged_except_render_stem_edit == true`. Every file under
`scripts/palette{,_v2,_probe,_render,/dawdreamer_state,/gen_palette_batch_v{1,2}}/`
has byte-identical SHA-256 pre and post the batch run, with the sole
documented exception of the intentional additive-kwargs edit to
`scripts/palette_render/render_stem.py` (both pre-edit and post-edit
SHAs recorded).

## 10. Tests

* `tests/test_palette_driven_batch_v3.py` — 20/20 PASS covering rubric
  SHA equality, mtime ordering, backwards-compat regression via
  subprocess, `render_stem.__signature__` (keyword-only
  `parameter_dict=None`), VST3 `NotImplementedError` raise, per-salt
  determinism × 2, 3-distinct-per-salt assignments, ≥4-of-6-distinct
  per-salt-per-stem parameter_dicts (honest bound on the 256-slot
  derivation surface), 8-key panel finiteness per salt, AST-grep no
  PRNG / no `sidecar_nonfactor` / no c9 chain / no `i4_stratified` /
  no `collision_model` / no `hash_geometry` / no `stability_audit` /
  no `canonical_aggregate_sha` / no `ledger_i3_dminor`, interpreter
  guard, anchor preservation, verdict enum + count.

* `tests/test_integration_cross_branch.py` §58 — 8/8 PASS covering
  rubric doc + hash + verdict enum + per-salt determinism +
  backwards-compat PASS + anchor preservation flag.

The two integration test failures observed at run time (`§57 ear-v0`,
`§59 vst3-nondet`) belong to c36 sibling clones (Branches A and C
respectively). Their §-blocks landed in the shared file concurrently
with this branch's; the corresponding artifacts arrive with those
clones at merge.

## 11. Promise-check

`0 ERRORs, 141 WARNs`. All ERRORs cleared. WARN inventory:

* Ledger-tracked artifacts under `long_exposure/*` (upstream exemption,
  established since c22).
* `reports/cycles/report_cycles_13-15_clone_1.md` missing (pre-existing).
* Orphan-artifact warnings for concurrent-clone artifacts under
  `scripts/vst3_nondeterminism/`, `tests/test_ear_v0_*`, `tools/_c36c_*`,
  etc. (Branches A + C, resolved at merge).
* `tests/test_palette_driven_batch_v3.py` orphan WARN — an artifact of
  the shadow-vs-main split (my `_infra/adopt-cycle36-tests-clone-1`
  event lives in the per-clone shadow ledger and merges to main at
  fanout barrier).
* 6 legacy trailing-slash path warnings (pre-existing).

## 12. Ledger events emitted (in shadow, `-clone-1` suffixed)

Six named + two housekeeping:

| # | milestone_id                                              | status         |
|---|-----------------------------------------------------------|----------------|
| 1 | `_run/cycle_36_launched-clone-1`                          | validated      |
| 2 | `_plan/register-palette-driven-batch-v3-clone-1`          | validated      |
| 3 | `_infra/render-stem-signature-extension-clone-1`          | validated      |
| 4 | `M-GEN-1/palette-driven-batch-v3`                         | in-progress    |
| 5 | `_infra/cross-branch-integration-test-cycle36-clone-1`    | validated      |
| 6 | `M-GEN-1/palette-driven-batch-v3`                         | validated (PARAM_MOVES_AUDIO) |
| 7 | `_run/cycle_36_closed-clone-1`                            | validated      |
| 8 | `_archive/cycle-36-scratch-clone-1`                       | validated      |
| 9 | `_infra/adopt-cycle36-tests-clone-1`                      | validated      |

Substantive `M-GEN-1/palette-driven-batch-v3` unsuffixed per c32
convention; infra families suffixed `-clone-1`. UUID5 content-hash
`event_id` auto-derived by `workspace_bootstrap.append_ledger_event`.
Nested `confidence: {level, rationale, assessor}`, `narrative` field,
pinned `run_id = "run-2026-08-28T040704Z"`.

## 13. C37 handoff candidates

Given **PARAM_MOVES_AUDIO**:

1. **`M-GEN-1/palette-driven-batch-v4`** — expand the perturbation
   surface. Concrete moves: (a) deeper fluidsynth CLI table (add
   chorus depth/speed, reverb damping/width — fluidsynth exposes at
   least a dozen more `-o synth.*` knobs); (b) opcode-file rewrite
   for sfizz — write a fresh SFZ per rule to a temp dir with per-region
   `<control>` and `<region>` overrides derived from the rule_id, then
   pass that path to `sfizz_render`; (c) per-note velocity / pitch
   modulation via MIDI file rewrite before render (byte-safe against
   the canonicalizer because the modification lands in MIDI).
2. **`M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization`** — c37
   Branch C's SMALL_PERTURBATION_TOLERABLE / STRUCTURAL_DRIFT / MIXED
   verdict determines whether Surge XT / Dexed can activate under a
   tolerance-gate rubric. If TOLERABLE, c37 attempts VST3 param
   threading (unblocks the Surge XT bass slot from sfizz to a richer
   subtractive synth palette). If STRUCTURAL_DRIFT, VST3 palette route
   is permanently gapped.
3. **`_manager/palette-render-v3-sfizz-opcode-fallback-triage`** — the
   sfizz stem's panel-scale stagnation (byte-distinct but panel-identical
   for salts 1 vs 2) is the load-bearing symptom pointing at
   opcode-file rewrite. Concrete triage: probe `sfizz_render` version
   for `--set` support (this workspace's binary lacks it); if absent,
   commit to the opcode-file-rewrite path in v4.

Non-scope-of-this-branch infra hygiene (opportunistic, root-scope):

* Merge-time reconciliation of §57 (Branch A ear-v0) + §59 (Branch C
  vst3-nondet) tests when their artifacts land.
* Consider a promise_check enhancement that recognises `-clone-<k>`
  suffix families to reduce shadow-vs-main orphan WARNs.

## 14. Files shipped

Docs:
* `docs/palette_driven_batch_v3_rubric.md`
* `docs/palette_driven_batch_v3_report.md` (this file)

Scripts:
* `scripts/palette_render_v3/__init__.py`
* `scripts/palette_render_v3/extend_render_stem.py`
* `scripts/palette_render_v3/derive_parameter_dict.py`
* `scripts/palette_render_v3/run_batch_v3.py`
* `scripts/palette_render_v3/spread_analysis_v3.py`
* `scripts/palette_render/render_stem.py` (additive-kwargs edit)

Data (`data/palette_render_v3/`):
* `rubric_hash.txt`, `backwards_compat_baseline.json`,
  `backwards_compat_check.json`, `batch_manifest.json`,
  `summary.tsv`, `spread_analysis.json`, `verdict.json`,
  `anchor_preservation.json`
* `per_song/<s>/{assignments.jsonl, parameter_dict.json,
  dispatch_summary.json, panel_original.tsv, panel_fluidsynth.tsv,
  bare_combined.wav.sha.run{1,2}, per_stem/<stem>/{render_run{1,2}.wav.sha,
  pinned_state.json}}` for s ∈ {0, 1, 2}

Tests:
* `tests/test_palette_driven_batch_v3.py` (20 cases)
* `tests/test_integration_cross_branch.py` (§58 added, 8 checks)

Plan of record updated with new `M-GEN-1/palette-driven-batch-v3` row.
