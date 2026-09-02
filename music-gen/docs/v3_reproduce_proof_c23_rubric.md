# v3 Reproduce-Proof Rubric — c23 (Chicken Grease + Rome)

Frozen rubric for the c22-deferred reproduce-proofs, executed via
`scripts/v3_spine/recreate_v3.py --song <sha16> --section operator
--reproduce-check <existing-delivery-dir>`.

This document is the **pinned root** of the three-way
`rubric_hash_v3_reproduce` chain:

    SHA-256(this file, byte-for-byte)
      == data/v3_reproduce_c23/rubric_hash.txt (content)
      == verdict.rubric_hash_v3_reproduce (each per-song reproduce_report.json)

The chain is a mtime-hard, git-log-advisory pre-registration (c46 policy). Any
downstream script under `scripts/v3_reproduce_c23/` MUST have mtime strictly
greater than this doc's mtime. Any drift in this chain is a c23 protocol
violation surfaced at the verdict emitter.

## Scope

Two songs, one section each, one driver invocation per song:

| song_sha16          | title           | anchor delivery dir                                        |
|---------------------|-----------------|------------------------------------------------------------|
| `31a164f845f8e27e`  | Chicken Grease  | `data/v3/deliveries/31a164f845f8e27e/operator_section/`    |
| `51e433ade2a845e1`  | Rome            | `data/v3/deliveries/51e433ade2a845e1/cycle20/`             |

The reproduce-proofs are executed **exactly once per song** under the c22
unified driver — no per-song bespoke logic, no hand orchestration, no tuning,
no retry, no fallback. FD-1 halt discipline applies.

## READ-ONLY anchor SHAs (byte-identical pre==post)

Two files are byte-identical anchors. Their SHA-256 MUST match at both
snapshot points (before and after the reproduce runs). Any drift halts.

| anchor                                                                                            | SHA-256 (prefix)       |
|---------------------------------------------------------------------------------------------------|------------------------|
| `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav`   | `cc919559b4508b6b…`    |
| `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json`                                        | `d2c2d704ce910fde…`    |

## Verdict enum (frozen; exactly three)

Each per-song `data/v3/reproduce/c23/<sha16>/reproduce_report.json` MUST
carry a `verdict` field equal to one of:

- `REPRODUCE_LANDS`
  - All comparable stage artifacts byte-equal to anchor, AND
  - Panel diff (8-key) equals anchor within `panel_equal_tolerance`, AND
  - `env_pin_sha256` identical to anchor's `env_pin.json` when present, AND
  - READ-ONLY anchor SHA pre==post
- `REPRODUCE_PANEL_ONLY`
  - Panel diff equals anchor within tolerance AND READ-ONLY anchor
    pre==post, BUT one or more of {stage byte-equality, env_pin_sha256}
    differs. Env-pin drift downgrades to PANEL_ONLY even when audio panels
    agree; this is the intended state when a legitimate env change has
    occurred and the operator has separately blessed the drift.
- `REPRODUCE_FAILS`
  - Panel drift beyond tolerance in any of the 8 panel keys, OR
  - READ-ONLY anchor SHA drift (any byte), OR
  - Driver exit code non-zero, OR
  - Structural gate on `merged.mid` violated, OR
  - Interpreter guard, PRNG, or sidecar_nonfactor anti-pattern trip.

There is **no fourth verdict**. There is no `REPRODUCE_PARTIAL`, no
`REPRODUCE_INCONCLUSIVE`. If the pipeline cannot complete, verdict is
`REPRODUCE_FAILS` with `failure_mode` populated.

## Panel-equal contract

The 8-key panel comes from `stage_panel` in the c22 driver:

    mel_l1_db, spectral_centroid_rmse_hz, rms_env_rmse, lufs_m_rmse_lu,
    embedding_cosine_distance, n_samples_compared, sr_hz, section

`panel_equal_tolerance` per key (absolute unless noted):

    mel_l1_db                   : 0.05 dB
    spectral_centroid_rmse_hz   : 2.0 Hz
    rms_env_rmse                : 0.002
    lufs_m_rmse_lu              : 0.05 LU
    embedding_cosine_distance   : 0.005
    n_samples_compared          : exact equality (integer)
    sr_hz                       : exact equality (integer)
    section                     : exact equality (string)

Tolerances reflect measured c22 A/B numerical jitter across kernel-scheduler
non-determinism; they are NOT a fitting knob. Any per-key delta beyond
tolerance is panel drift and halts per FD-1.

## Byte-equal contract

Byte-equality is REQUIRED where `env_pin_sha256(new) == env_pin_sha256(old)`
across these stage artifacts, when both files exist under matching names:

    merged.mid
    reconstruction_ab_*.wav
    full_reconstruction*.wav
    stems_6s/*.wav
    per_track/*.wav
    muscriptor/*.json

Anchor deliveries pre-c22 may name reconstruction/full_reconstruction files
with `_operator_section` suffix; the emitter maps these by (basename-suffix-
stripped) canonical name. Missing counterpart in the anchor is not a
byte-drift — it is a `not_comparable` entry.

Byte-drift under env-pin-identical is a `REPRODUCE_FAILS` per FD-1. Byte-
drift under env-pin-different downgrades to `REPRODUCE_PANEL_ONLY`.

## Env-pin diff-vs-original-manifest

Anchor `env_pin.json` is compared field-by-field against the freshly produced
one. Fields tracked:

- `env_pin_sha256` (self-anchor)
- `python_version`, `platform`, `torch_version`, `numpy_version`,
  `librosa_version`, `soundfile_version`
- `PYTHONHASHSEED`, `SOURCE_DATE_EPOCH`, `TZ`, `LC_ALL`,
  `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`
- `sf2_sha256`, `muscriptor_model_sha256`

The diff shape emitted in `reproduce_report.json`:

    "env_pin_diff": {
      "new_sha": <hex or null>,
      "old_sha": <hex or null>,
      "identical": <bool>,
      "per_field_deltas": { "<field>": { "new": ..., "old": ... }, ... },
      "note": <string or absent>
    }

When the anchor delivery has no `env_pin.json` (pre-c22), `identical` is
`false` and `note` is `"no env_pin.json in existing delivery (pre-c22)"`.
That is the expected state for both Chicken Grease (c5-blessed operator
section) and Rome (c20 verdict) anchors.

## Per-stage diff shape

    "per_stage": {
      "<stage_file>": {
        "new_sha": <hex>,
        "old_sha": <hex or null>,
        "byte_equal": <bool>,
        "comparable": <bool>,
        "size_new": <int>,
        "size_old": <int or null>
      }, ...
    }

`comparable=false` when the anchor lacks a counterpart file (e.g. Rome
cycle20 verdict-only anchor). Only comparable entries contribute to the
verdict.

## Per-key panel diff shape

    "panel_diff": {
      "panel_tsv_byte_equal": <bool>,
      "panel_json_byte_equal": <bool>,
      "per_key": {
        "<key>": {
          "new": <value>,
          "old": <value>,
          "delta_abs": <number>,
          "tolerance": <number>,
          "within_tolerance": <bool>
        }, ...
      },
      "panel_equal_all_keys": <bool>
    }

`panel_equal_all_keys` requires `within_tolerance == true` for every one of
the 8 keys.

## Halt discipline (FD-1)

The reproduce-proof does not tune, retry, or fall back. On drift the emitter
sets `verdict = REPRODUCE_FAILS` and populates `failure_mode`. No second run
under different pins. No parameter search. No "close enough" nudge. The
operator decides.

## Downstream unblock

If BOTH per-song verdicts are `REPRODUCE_LANDS` OR `REPRODUCE_PANEL_ONLY`
under an operator-blessed env-pin drift, this rubric authorizes c24
execution of the `_infra/retire-oneoff-drivers-c22` deletion contract (37
per-song scripts per catalog `data/v3/recreate_v3/retirement_catalog_c22.json`).

If EITHER verdict is `REPRODUCE_FAILS`, c24 is BLOCKED and the retirement
catalog stays pending. The failed song surfaces to the operator; no agent
initiates retirement without operator sign-off.

## Anti-patterns (inherited, non-exhaustive)

- No PRNG in pipeline scripts. `torch.manual_seed(0)` is a seed pin, not
  RNG use.
- No `sidecar_nonfactor` imports.
- VST3 `get_state` / `save_state` / `save_preset` / `load_state` /
  `set_state(bytes)` AST-forbidden (c31 STILL_GAP + c35 A locked).
- `/usr/bin/python3` interpreter guard mandatory on every pipeline script.
- No hand orchestration of song recreation (c22 operator directive).
- No CLAP HF fetch (c11 SSL fail anti-pattern).
- c32 fanout-namespace convention: `_infra`/`_run`/`_plan`/`_archive`/
  `_manager` require `-clone-<k>` suffix in clone contexts; substantive
  `M-*` milestones remain unsuffixed.
