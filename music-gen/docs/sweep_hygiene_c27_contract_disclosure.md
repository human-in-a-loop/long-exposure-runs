# c27 Sweep-Hygiene Contract Disclosure (c50)

Companion to `scripts/sound_match/_sweep_hygiene_c27.py`. This document is
the on-disk sibling for the c50 O-2 hygiene disclosure per **invariant (d)**
(on-disk-vs-brief divergence disclosure norm from
`docs/agent_picks_selection_invariants.md`).

## Why the disclosure is here, not in the module docstring

c50 brief Track 4 directed a one-liner append to the hygiene module docstring,
but the module SHA is pinned by two test surfaces:

- `tests/test_c30_legacy_mode_regression.py` line 32
  `CANON_HYGIENE_SHA = "771ff42b768d9c44dd96bc9066666bcaa3d6b81ebdc6930fea07f452a3fa51c4"`
  (asserted directly by `test_05_hygiene_module_anchor_preserved`)
- The same constant is asserted in the c30 anchor-substitution sidecars
  (`data/v4/regression/c30_cg_anchor_coarse_sweep_*.json` and family) via
  `_check_landed_sidecar(sidecar["hygiene_module_sha256"] == CANON_HYGIENE_SHA)`
  (`test_02`/`test_03`/`test_04`).

Editing the module drifts its SHA to `06c942f7…` and breaks the anchor
lineage without provable substantive benefit (the disclosure text does not
change behavior). Reverting the module + landing the disclosure here
preserves the c30 anchor line-up while still recording the finding per
invariant (d). This is invariant (a) (prefer no scope extension) applied to
the c50 brief: the brief's mechanism target (module docstring) collided
with the test-lineage; the sibling-doc mechanism preserves everything.

## Contract observations (c50 grep + c49 sweep behaviour)

- The argparse flag `--score-and-delete-per-candidate` on the three fine-fit
  drivers (`fine_fit_sf2_v2.py`, `fine_fit_sf2_drums.py`,
  `fine_fit_sf2_guitar.py`) is **decorative**: it defaults to `True` and is
  never read after parse. `grep -n 'score_and_delete\|args.score' scripts/sound_match/fine_fit_sf2_v2.py`
  returns zero hits inside the driver body (only the argparse
  `add_argument` line at 461).
- The actual hygiene mechanism is `RunningTopK.push()` (line 596) +
  `prune_after_pin()` (line 688), gated on `not args.legacy_batch_render`
  (line 481). This is wired for both stage-1 coarse and stage-2 fine
  drivers under default (non-legacy) mode.
- **c49 Rome observation** (from restored context): 217 in-flight WAVs
  accumulated before pin. `RunningTopK`'s displacement-triggered delete
  only fires when the top-K set changes. Cells that lose the top-K race
  are recorded but their audio is not immediately unlinked; `prune_after_pin()`
  handles the cleanup at end. Callers who need strict in-flight
  per-candidate cleanup should implement a driver-level hook, not rely on
  the decorative flag.

## Scope of the observation

- Applies to `fine_fit_sf2_v2.py` (verified via grep this cycle).
- Same pattern held for the other two fine-fit drivers by their shared
  `_sweep_hygiene_c27.RunningTopK` import at line 490 in each; not
  separately grepped this cycle.
- **Not** a rewire: c50 does not touch stage-2 mechanism. If a future cycle
  wants strict per-candidate cleanup, it can add a hook without renaming
  the flag; the flag stays informational for backwards-compatible CLI.

## Reference

- Brief target (Item 4, c50 first-act): "If flag is decorative: append a
  one-liner to `scripts/sound_match/_sweep_hygiene_c27.py` module docstring…"
- On-disk lineage that constrained the change: `test_c30_legacy_mode_regression`
  lines 32/45/114.
- Invariant (d) precedent: c14 audit closure — brief-vs-on-disk divergence
  disclosed in-work, on-disk value pinned by SHA.
- Sha pin `06c942f7…` for the modified module was **not** landed; the
  on-disk hygiene module SHA remains `771ff42b768d9c44…` (test_05 green,
  test_02–test_04 sidecar chain intact).
