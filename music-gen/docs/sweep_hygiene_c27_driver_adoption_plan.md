# c27 Sweep-Hygiene Driver-Adoption Plan

**Cycle:** c27 (author) → c28+ (integration)
**Authority:** OPERATOR DIRECTIVE 2026-09-05 (live_guidance)
**Canonical module:** `scripts/sound_match/_sweep_hygiene_c27.py`
**POR entry:** `PROC 2026-09-05 SWEEP-HYGIENE FIX: …` (tail of plan_of_record.md)

## Scope

c27 landed the canonical hygiene module + full test coverage (10/10 PASS).
Because Tracks C/D deferred this cycle (no new sweep launches — disk at 87 %
still above the 85 % prune threshold at cycle open, operator pruned c26
scored renders + tombstones), integration into the 4 sweep drivers rolls to
c28 first-sweep-launch. This document pre-registers each driver's exact
edit shape so c28+ is mechanical.

## Drivers to patch

| Driver | Anchor Cycle | c27 state |
|---|---|---|
| `scripts/sound_match/coarse_sweep_sf2.py` | c1 (bass coarse) | READ-ONLY, needs full hygiene wiring |
| `scripts/sound_match/coarse_sweep_sf2_drums.py` | c10 (drums coarse) | READ-ONLY, has legacy post-sweep prune only |
| `scripts/sound_match/coarse_sweep_sf2_guitar.py` | c13 (guitar coarse) | READ-ONLY, has legacy post-sweep prune only |
| `scripts/sound_match/fine_fit_sf2_v2.py` | c3 (bass fine) | READ-ONLY, no hygiene flags |
| `scripts/sound_match/fine_fit_sf2_drums.py` | c11 (drums fine) | READ-ONLY, has legacy post-sweep prune only |
| `scripts/sound_match/fine_fit_sf2_guitar.py` | c14 (guitar fine) | READ-ONLY, has legacy post-sweep prune only |

## Reference integration shape (applies to all 6 drivers)

**1. Import** (top of module, after existing imports):

```python
from scripts.sound_match._sweep_hygiene_c27 import (
    RunningTopK, df_guard_before_stage, prune_after_pin,
    DEFAULT_KEEP_TOP, DEFAULT_MAX_AUDIO_MB,
)
```

**2. New flags** (in `main()` argparse, alongside existing hygiene flags):

```python
ap.add_argument("--score-and-delete-per-candidate", action="store_true",
                default=True,
                help="c27 default: render->score->delete each candidate; "
                     "retain running top-K only. Opt out with --legacy-batch-render.")
ap.add_argument("--legacy-batch-render", action="store_true", default=False,
                help="c26 legacy: batch-render all cells, prune post-sweep. "
                     "Regression only; forbidden in production per operator "
                     "directive 2026-09-05.")
ap.add_argument("--keep-top-c27", type=int, default=DEFAULT_KEEP_TOP)
```

**3. df guard at entry** (before the per-cell loop, after out_dir mkdir):

```python
if not args.legacy_batch_render:
    workspace_root = Path(__file__).resolve().parents[2]
    df_status = df_guard_before_stage(
        workspace_root=workspace_root,
        stage_dir=out_dir,
        prune_pct=85.0, abort_pct=90.0,
    )
    (out_dir / "df_guard_status.json").write_text(
        json.dumps(df_status, sort_keys=True, indent=2)
    )
```

**4. Per-cell hook** (inside the per-cell loop, replacing the deferred-prune pattern):

```python
if not args.legacy_batch_render:
    if "topk" not in locals():
        topk = RunningTopK(k=args.keep_top_c27)
    topk.push({
        "render_path": str(final_wav),
        "composite": row["composite"],
        "render_wav_sha": row.get("render_wav_sha") or row.get("render_sha256"),
    })
```

**5. Post-pin cleanup** (after profile emission, before final leaderboard write):

```python
if not args.legacy_batch_render and "topk" in locals():
    pinned_paths = {top1_render_path}  # winner selected by leaderboard sort
    deleted = prune_after_pin(topk.kept_rows(), pinned_paths)
    (out_dir / "post_pin_cleanup.json").write_text(
        json.dumps({
            "pinned_paths": list(pinned_paths),
            "n_deleted": len(deleted),
            "deleted_paths": deleted[:20],
        }, sort_keys=True, indent=2)
    )
```

**6. Deprecate legacy behavior:** the existing `--score-and-delete` flag stays
for backward-compat but its "defer to end" semantics is superseded when
`--score-and-delete-per-candidate` (new default) is active. Legacy behavior
only fires under explicit `--legacy-batch-render`, which is regression-only
and forbidden in production per operator directive.

## SHA drift disclosure per invariant (d)

Every driver edit lands as an anchor-SHA-drift event, disclosed at that
cycle's ledger emission. New driver SHAs land in the next cycle's
anchor_preservation snapshot; old SHAs preserved in ledger narratives for
provenance walk-back.

## Test gate

Every driver integration ships with a regression test asserting:
1. Under default flags (per-candidate mode): peak WAVs on disk ≤ keep_top_c27
   throughout the sweep (mocked); `df_guard_status.json` present with pre/post
   usage pct.
2. Under `--legacy-batch-render`: pre-c27 behavior byte-preserved on the
   frozen 1-cell smoke test (SHA regression).

## Non-goals

- This plan does NOT change any pinned profile, verdict, or replay proof.
- This plan does NOT change the composite formula or its 3-metric weighting.
- This plan does NOT re-run any c22-c26 verdict.

## References

- Operator directive verbatim: c27 research_brief live_guidance section
- c27 module: `scripts/sound_match/_sweep_hygiene_c27.py`
- c27 tests: `tests/test_sweep_hygiene_c27.py` (10/10 PASS)
- POR entry: `plan_of_record.md` tail `PROC 2026-09-05 SWEEP-HYGIENE FIX: …`
