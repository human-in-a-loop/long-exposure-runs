# v3_spine c7 Track A — torch 2.13.0+cpu reproduction probe spec

Pinned pre-code. Any Python file under `scripts/v3_spine/torch213_reproduce_probe*`
inherits this contract. `data/v3_spine/torch213_reproduce_spec_hash.txt` records this
document's SHA-256; the probe script asserts equality at import time.

## Fixed decisions in force

- FD-1 no hand-rolled DSP transcription; no tuning around failures.
- FD-6 panel is never a LANDS gate; operator ear is the only LANDS authority.
- Egress BLOCKED. No `pip install`, no PyPI fetch, no proxy bypass.
- Sub-process-serial in-turn only.
- Interpreter guard: every top-level script asserts `sys.executable == "/usr/bin/python3"`.
- Env pins: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
  `LC_ALL=C.UTF-8`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`.
- No PRNG. No `sidecar_nonfactor` imports.

## Two-mode operation

The probe is guarded by an `--execute` flag, default `False`.

### Mode 1 (default — no operator green-light needed)

- Verify c3-era torch is still on disk: import `torch` under `/usr/bin/python3`
  and record `torch.__version__` + `torch.__file__`. Required equalities:
    - `torch.__version__ == "2.13.0+cpu"`
    - `torch.__file__ == "/usr/local/lib/python3.11/dist-packages/torch/__init__.py"`
  If either differs, `probe_status = "candidate_disappeared"` and the probe
  stops without executing anything else.
- Draft the reproduction command string verbatim. Resolve `<muscriptor entrypoint>`
  by reading `scripts/v3_spine/muscriptor_operator_section.py` for the constants
  `MUSCRIPTOR` (path to the `muscriptor` binary) and `MODEL` (path to the
  safetensors model). Resolve `<c4 guitar stem path>` from the same source
  (`data/v3_spine/31a164f845f8e27e/stems_6s/guitar.wav`, matching c3's
  input). Do NOT interpolate temporary directory paths into the string;
  leave a placeholder `<tempdir>`.
- Record:
    - `mode: "dry_run"`
    - `probe_status: "awaiting_operator_green_light"`
    - `attribution_verdict: "ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_DRY_RUN"`
    - `torch_version_observed`, `torch_file_observed`
    - `command_string_drafted`
    - `c3_guitar_json_sha_anchor` (full 64-hex from
      `data/v3_spine/31a164f845f8e27e/muscriptor/guitar.json`)
    - `c4_guitar_json_sha_anchor` (full 64-hex from
      `data/v3_spine/31a164f845f8e27e/muscriptor/guitar.json` — this file
      currently holds the c3-era bytes on disk; the c4-era 3107ba21… SHA is
      pinned from ledger record `muscriptor_c4_within_cycle_check.json`)
    - `stem_input_path`, `stem_input_sha256`

### Mode 2 (`--execute`, only if operator directive in live_guidance)

- Run the drafted command twice into two fresh `tempfile.mkdtemp()` dirs
  under the env pins above.
- SHA-256 compare the resulting `guitar.json` against the c3 anchor
  `97b5a598db8424bbca725c1fbbc4854e4cb39297aae390dc84f760056f4ddabc`
  and the c4 anchor
  `3107ba21e10acc7025a84105fe1e9500b87f49d6361f1716a8b1d98a224069cb`.
- Three-way outcome:
    - Matches c3 anchor → `attribution_verdict = "ENV_DRIFT_CONFIRMED_TORCH_MINOR_VERSION"`.
    - Matches c4 anchor → `attribution_verdict = "ENV_DRIFT_NOT_TORCH_ALONE"` (first-class
      negative; do NOT tune to force c3).
    - Matches neither → `attribution_verdict = "ENV_DRIFT_THIRD_STATE"` (also first-class;
      publish the observed SHA).
- Byte-determinism sidecar for the two runs.

## Forbidden

- `pip install` anything.
- Mutating `workspace/learned_transcribers_venv/` (mtime + directory-manifest
  SHA pre==post required).
- Attempting egress (AST guard on `urllib`, `urllib3`, `requests`, `httpx`,
  `socket`, `http`, `aiohttp`).
- Bypassing the `--execute` guard from a user prompt alone. Only a
  `live_guidance` operator directive counts.

## Outputs

- `data/v3_spine/cycle7/torch213_reproduce_probe.json`
- `data/v3_spine/cycle7/torch213_reproduce_probe_byte_determinism.json`
  (Mode 1: single-run baseline SHA; Mode 2: two-run equality record).
