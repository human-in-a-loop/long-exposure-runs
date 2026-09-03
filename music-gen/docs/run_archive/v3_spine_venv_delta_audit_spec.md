# v3 Spine Venv Delta Audit Specification (cycle 5)

**Purpose.** Empirically characterize the cross-cycle guitar JSON drift
between cycle 3 (`sha16 97b5a598`) and cycle 4 (`sha16 3107ba21`) MuScriptor
outputs on Chicken Grease guitar stem. Cycle 4 established that intra-cycle
MuScriptor JSON is byte-deterministic ×2 (both c4 runs identical). The
cross-cycle drift therefore attributes to *some* environmental delta between
cycles, most plausibly a torch/BLAS package version change.

## Sources snapshotted

- `workspace/learned_transcribers_venv/bin/python` (interpreter)
- `workspace/learned_transcribers_venv/bin/muscriptor` (CLI)
- `pip freeze` output from that venv (every installed package × version)

## Comparison methodology

Per-package: `{name, current_version, prior_version, delta_class}` where
`delta_class ∈ {none, patch, minor, major, missing_prior}`.

- `none`: identical semver.
- `patch`: `MAJOR.MINOR` equal, `PATCH` differs.
- `minor`: `MAJOR` equal, `MINOR` differs.
- `major`: `MAJOR` differs.
- `missing_prior`: package present now, absent in prior snapshot.

If no prior snapshot exists (first observation), snapshot the current state
as `c5_baseline` for future cycles and mark `baseline_established=true`.

## Probe methodology (c3 guitar reproduce)

1. Enumerate discoverable c3-era package versions from:
   - `~/.pip/log` (if present)
   - `workspace/learned_transcribers_venv/_pip_history.log` (if present)
   - Any `data/v3_spine/venv_snapshots/*.json` (if present)
2. Identify local wheel cache (`~/.cache/pip/wheels/`, `~/.pip/cache/`).
3. If plausible c3 versions AND local wheels: install into a scratch venv
   `workspace/scratch_c3_pin_venv/` (do NOT touch primary venv), re-run
   MuScriptor on the c4 guitar stem, hash the JSON output.
4. If wheels not locally cached: mark `probe_status=deferred_egress_blocked`.
   **Egress fetch is forbidden.**

## Probe verdicts (frozen)

- `reproduced` — probe re-produced c3 SHA `97b5a598db8424bb…` byte-exact.
- `drifted_still` — probe ran under pinned versions but produced a different
  SHA than c3 (new investigation needed).
- `deferred_egress_blocked` — cannot install c3-era wheels; not a failure.

## Pre-registration invariant

This document's mtime MUST precede every mtime under
`scripts/v3_spine/venv_delta_audit*` and
`scripts/v3_spine/c3_guitar_reproduce_probe*`. Doc SHA-256 is pinned to
`data/v3_spine/venv_delta_audit_spec_hash.txt` before any script executes.

## Impact on OPTION A

The canonical MIDI serializer is a **pure function** of its JSON input.
Cross-cycle JSON drift does not invalidate OPTION A because the c4 gate
is *intra-cycle byte-determinism*. Attribution matters for M-V3-FOCUS-1
planning: if drift is env-attributable, we pin the transcribers venv going
forward; if not, we log a first-class investigation lead for cycle 6.
