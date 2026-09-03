# Stage-checkpointed Unified Driver — Spec

**Cycle:** c24 (post-c23 fanout integration)
**Supersedes (evolutionary sibling, not replacement):** `docs/v3_spine_unified_driver_spec.md` (c22)
**Applies to:** `scripts/v3_spine/recreate_v3_checkpointed.py` (this cycle) — composes with c22 stage functions in `scripts/v3_spine/recreate_v3.py` + `scripts/v3_spine/v3_pipeline/*` (READ-ONLY anchors).

## Motivation (verbatim operator decision, 2026-09-03)

> Make the unified driver STAGE-CHECKPOINTED and finish [Peach Dream]. Add per-stage
> content-addressed caching to `scripts/v3_spine/recreate_v3.py` — each of the 9 stages
> writes outputs plus a stage manifest keyed on the sha256 of its inputs (audio slice,
> model weights, config, env pins); on re-invocation the driver verifies the key and
> SKIPS completed stages, so a session-budget kill costs nothing and re-running twice
> still proves byte-determinism (cached stage outputs ARE the determinism evidence
> when keys match; force a `--no-cache` full rerun only for the final ×2 proof if the
> ledger requires it). This is squarely within the determinism doctrine: a cached
> stage is a pure function of its hashed inputs.

## Contract

### Stage-cache primitive

Every stage is a pure function of a tuple of hashable inputs. `stage_cache.compute_key(stage_name, inputs)` returns

    sha256(canonical_json({
      "stage": stage_name,
      "inputs":  {name: sha256_of_file_or_scalar for name, value in inputs.items()},
      "env_pins": build_env_pin_manifest(),   # already deterministic per c22
      "spec_version": "checkpointed_v1",
    }))

The cache directory is `<work_dir>/stage_cache/<stage_name>/<key[:16]>/`. Each successful
stage write produces:

- `outputs/…` — the stage's real outputs (WAVs, MIDs, JSONs)
- `stage_manifest.json` — schema:

      {
        "stage": <str>,
        "input_key": <hex64>,
        "outputs": {<relpath>: <sha256>, …},
        "wall_seconds": <float>,
        "ts": "<iso8601>",
        "env_pin_sha256": <hex64>,     # cross-ref to the delivery's env_pins block
        "cache_spec_version": "checkpointed_v1"
      }

`stage_cache.check(stage_name, inputs, work_dir)` returns either

- `None` — no cached manifest, or the manifest's `input_key` disagrees with the
  freshly computed one; caller must run the stage
- `dict` — the cached manifest and a resolved absolute path to `outputs/`; caller
  copies (or hard-links) into the delivery layout and skips the stage.

### Skip semantics

A cache HIT is a byte-for-byte substitute for a fresh run **provided every
tracked input's sha256 is unchanged AND `env_pin_sha256` is unchanged**. If either
changes, the cache MISSES and the stage re-runs; the old manifest is left in place
under a different `<key[:16]>` directory (no destructive overwrite).

### `--no-cache`

The driver accepts `--no-cache` which force-invalidates every cache probe. Reserved
for the ledger-required two-fresh-runs byte-determinism proof; the two clean runs are
still executed against fresh `tempfile.mkdtemp()` working directories, exactly as
the c22 spec required. In normal operation the driver uses cache.

### The 9 stages (unchanged from c22)

    slice → rehtdemucs → muscriptor → tempo_map → canonicalize
          → merge → render_per_track → mix_match → panel

Each stage's inputs are enumerated in `recreate_v3_checkpointed.STAGE_INPUTS`. The
tuple is stable — adding an input to a stage bumps `cache_spec_version` (documented
above) and invalidates all prior manifests.

## Detached launch

`scripts/v3_spine/launch_detached.py` provides

    launch_detached(cmd: list[str], logfile: Path, workdir: Path | None = None) -> int

which forks under `setsid` and redirects stdout+stderr to `logfile`. Returns the
child PID. The parent may then poll `os.kill(pid, 0)` and tail the logfile. A
session boundary in the launching agent no longer kills the computation.

## Backwards compatibility

The c22 driver `scripts/v3_spine/recreate_v3.py` and pipeline module
`scripts/v3_spine/v3_pipeline/*` are **READ-ONLY anchors** (SHA-preserved this
cycle and every future cycle). The checkpointed driver imports their stage_*
functions verbatim; adding checkpointing is composition, not replacement.

The c22 delivery `manifest.json.env_pins` block is unchanged. The delivery's
`stage_cache/` subtree is a new sibling — the delivery-facing shape of
`per_track/`, `stems_6s/`, `merged.mid`, `panel.{json,tsv}`, `verdict.json`,
etc. is identical to c22.

## Verdict

A verdict emitted by the checkpointed driver carries the same
`V3_FOCUS_SONG_LANDS_pending_operator / PARTIAL / FAILS` enum and the same
`rubric_hash_v2` + `rubric_hash_v3` chains. An additional field
`verdict.cache_summary` records `{stages_hit: int, stages_miss: int, wall_saved_seconds: float}`
for after-action analysis.

## Falsifiability

The primary correctness gate is `cache-hit_bytes_equal_fresh-run_bytes` for every
stage output. `tests/test_stage_cache_roundtrip.py` proves this on a synthetic
stage under fresh temp dirs.
