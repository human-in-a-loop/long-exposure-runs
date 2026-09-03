# v3 Spine — Env Drift Deep Dive Spec (Cycle 6, Track A)

Pinned pre-code per FD-1 discipline.

## Objective

Enumerate every on-disk wheel/dist-info candidate that could reproduce the
c3-era torch build (hypothesised `torch 2.13.0+cpu` per the compaction
summary) WITHOUT any network activity. Emit `data/v3_spine/env_drift_deep_dive.json`.

## Method

1. Scan the following roots via `os.walk` inside a `/usr/bin/python3`
   subprocess. No `pip`, no `urllib`, no `socket`, no `subprocess` to any
   network binary:
   - `/root`, `/home`
   - `/var/cache/apt`, `/var/lib/apt`, `/var/lib/dpkg`
   - `/var/lib/docker` (if present)
   - `/opt`
   - `/usr/lib`, `/usr/local/lib`
   - `/tmp`
   - Skip `/proc`, `/sys`, `/dev`.
2. For each matched file (`torch-*.whl`, `torch-*.dist-info` directory,
   `torch-*.tar.gz`, `torch-*.zip`), record:
   - `path` (absolute)
   - `filename`
   - `filetype` ∈ {wheel, dist_info_dir, sdist, egg_info, other}
   - `size_bytes`
   - `sha256` (only for regular files; directories carry `null`)
   - `version` (parsed from filename via regex `torch-([\d.+a-zA-Z]+)-*`)
   - `matches_c3_baseline_hypothesis` — True iff parsed version starts
     with `2.13`
3. Also enumerate `PIP_INDEX_URL` / `pip.conf` / `wheelhouse/` directories
   that exist locally, and inspect `~/.cache/pip/http*` and `.cache/pip/wheels`.
4. Cross-reference against `data/v3_spine/venv_snapshots/c5_baseline.json`
   (torch entry) so the JSON carries the c5 baseline torch pin for
   comparison.
5. Emit `data/v3_spine/env_drift_deep_dive.json` with:
   - `cycle: 6`, `run_id`, `spec_sha256`
   - `scan_roots_attempted`, `scan_roots_skipped_denied`
   - `candidates` (list of records above)
   - `probe_status`: `candidate_found` if ≥1 candidate with
     `matches_c3_baseline_hypothesis=True`; `no_local_candidate` otherwise.
   - `attribution_verdict`:
       - `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_REPRODUCE` (with
         `reproduction_command`) when at least one 2.13.x wheel exists
       - `ENV_DRIFT_PROBE_EXHAUSTED_LOCAL` otherwise
   - `network_syscall_attempted: false` (asserted)
   - `c5_torch_baseline` (from c5_baseline.json)

## Determinism

Two runs into fresh `tempfile.mkdtemp()` dirs must produce byte-identical
JSON when `keys` sorted, timestamps fixed via `SOURCE_DATE_EPOCH`, and
scan order is `sorted()`. Byte-det ×2 recorded in
`data/v3_spine/env_drift_deep_dive_byte_det.json`.

## Anti-instructions

- No `pip install`. No `pip download`. No `apt-get`.
- No mutation of `workspace/learned_transcribers_venv/`.
- Do not claim drift is "resolved" from a file scan — the strongest
  positive verdict is "candidate found, reproduction command drafted for
  operator-approved c7 execution".
