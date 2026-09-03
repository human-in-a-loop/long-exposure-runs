# v3 Spine — Cycle 7 report

**Cycle:** 7 (three-track substantive; linear execution — fanout self-check
factors all fail per c6 auditor and re-verified here).
**Song:** Chicken Grease (`sha16 = 31a164f845f8e27e`).
**Milestone:** `M-V3-SPINE-1`.
**Verdict:** `V3_SPINE_C7_THREE_TRACK_LANDS_pending_operator`.
**Blocked on operator:** `true` (per FD-6; operator ear on Chicken Grease A/B
is the only authoritative gate).

## Executive summary

- **Track A (torch-2.13 dry-run reproduction probe)** — dry-run mode only,
  no operator directive present in `live_guidance`. Candidate confirmed on
  disk (`/usr/local/lib/python3.11/dist-packages/torch/__init__.py` version
  `2.13.0+cpu`). Reproduction command drafted verbatim. `venv_unchanged=true`,
  `network_syscall_attempted=false`.
  `attribution_verdict = ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_DRY_RUN`.
- **Track B (rc7 canonicality decision note)** — one-page characterization
  of Method A (c5 plain RMS-match) and Method B (c6 iirpeak+RMS+LUFS-S)
  with LUFS-I/S, true-peak, spectral centroid, spectral flatness, mel-L1.
  No aggregate, no recommendation. Both required SHAs pinned verbatim.
  Note grep-verified free of `LANDS`/`PARTIAL`/`FAILS` tokens.
- **Track C (empty-stem duration sanity)** — `full_mix_duration_correct=true`
  (both Method A + B full-mix WAVs at 1_323_000 samples @ 44.1 kHz = 30 s);
  `empty_stem_shorts_expected=true` (other + piano per-track WAVs at 88_320
  samples ≈ 2.003 s — fluidsynth tail-flush on empty MIDIs). Closes c6
  auditor watch item cleanly.
- **Determinism + anchors + tests** — 17/17 c7 tests PASS; byte-det ×2 holds
  on all three c7 JSONs; 87-anchor preservation `all_match=true, n_diff=0`
  (target ≥75).
- **promise_check** — 0-ERROR post-registration.

## 1. Track A — torch 2.13.0+cpu dry-run reproduction probe

**Spec doc:** `docs/v3_spine_torch213_reproduce_spec.md` (SHA
`820da97690893fa9…`). SHA pinned in
`data/v3_spine/torch213_reproduce_spec_hash.txt`.
**Impl:** `scripts/v3_spine/torch213_reproduce_probe.py` — two-mode
`--execute`-guarded, default False.
**Output:** `data/v3_spine/cycle7/torch213_reproduce_probe.json` +
`.byte_determinism.json` sidecar.

### Mode-1 (dry-run) findings

| Field | Value |
|---|---|
| `torch_version_observed` | `2.13.0+cpu` (matches c3-era hypothesis) |
| `torch_file_observed` | `/usr/local/lib/python3.11/dist-packages/torch/__init__.py` |
| `stem_input_sha256` | `bc01ff1f6ed4e778…` |
| `c3_guitar_json_sha_anchor` | `97b5a598db8424bbca725c1fbbc4854e4cb39297aae390dc84f760056f4ddabc` |
| `c4_guitar_json_sha_anchor` | `3107ba21e10acc7025a84105fe1e9500b87f49d6361f1716a8b1d98a224069cb` |
| `venv_unchanged` | `true` |
| `network_syscall_attempted` | `false` |
| `attribution_verdict` | `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_DRY_RUN` |
| `probe_status` | `awaiting_operator_green_light` |

### Drafted reproduction command (Mode 2 preview)

```
PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 \
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/usr/bin/python3 workspace/learned_transcribers_venv/bin/muscriptor transcribe \
  data/v3_spine/31a164f845f8e27e/stems_6s/guitar.wav \
  --format json --output <tempdir>/guitar.json \
  --model workspace/models/muscriptor-medium/model.safetensors \
  --device cpu --detect-tempo best-effort
```

Mechanism of the interpreter-swap variant: `/usr/bin/python3` imports torch
2.13.0+cpu directly from `dist-packages` WITHOUT activating
`workspace/learned_transcribers_venv`. Executing the drafted command uses
that interpreter and torch — the point of the c7 auditor-carried variant.

### FD-1 compliance

The probe takes no reproduction action. `--execute` is guarded off by
default; only a live_guidance operator directive counts (user prompt alone
does not). This cycle has no such directive. On operator green-light in a
future cycle, Mode 2 runs the drafted command twice into fresh
`tempfile.mkdtemp()` dirs and produces one of three attribution verdicts:
`ENV_DRIFT_CONFIRMED_TORCH_MINOR_VERSION` (matches c3),
`ENV_DRIFT_NOT_TORCH_ALONE` (matches c4 — first-class negative), or
`ENV_DRIFT_THIRD_STATE` (matches neither — also first-class).

## 2. Track B — rc7 canonicality decision note

**Deliverable:** `docs/v3_spine_rc7_canonicality_decision_note.md` — one page,
no code, no verdict-shifting artifact. Backing metrics at
`data/v3_spine/cycle7/rc7_canonicality_metrics.json`.

Two reconstructions characterized side-by-side, per FD-1 no method retuning
without operator ear input:

| Metric | Method A (c5 plain RMS-match `cc919559…`) | Method B (c6 iirpeak+RMS+LUFS-S `f40796be…`) |
|---|---:|---:|
| LUFS-I (LU) | −19.95 | −17.87 |
| LUFS-S mean (LU) | −20.02 | −18.02 |
| LUFS-S std (LU) | 0.640 | 0.889 |
| LUFS-S max (LU) | −19.07 | −17.06 |
| True peak (dBFS) | −3.01 | −0.01 |
| Max abs sample | 0.7070 | 0.9990 |
| Spectral centroid mean (Hz) | 3910.1 | 2353.2 |
| Spectral centroid std (Hz) | 2740.0 | 1619.2 |
| Spectral flatness mean | 0.03025 | 0.00684 |
| Mel-L1 vs original (0..30 s, dB) | 8.727 | 7.489 |

Both are internally consistent and byte-deterministic within their own
cycle. Neither is preferred here. Operator ear on the two A/B pairs remains
the only authoritative gate per FD-6.

## 3. Track C — empty-stem duration sanity

**Impl:** `scripts/v3_spine/empty_stem_duration_sanity.py`.
**Output:** `data/v3_spine/cycle7/empty_stem_duration_sanity.json`.

| File | Samples | Duration (s) | Sample rate (Hz) |
|---|---:|---:|---:|
| `.../operator_section/full_reconstruction_operator_section.wav` (Method A) | 1_323_000 | 30.000 | 44100 |
| `.../rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav` (Method B) | 1_323_000 | 30.000 | 44100 |
| `.../operator_section/render/per_track/other.wav` | 88_320 | 2.003 | 44100 |
| `.../operator_section/render/per_track/piano.wav` | 88_320 | 2.003 | 44100 |

Both full-mixes match the 30-s @ 44.1 kHz contract; both empty-stem
per-track WAVs sit at fluidsynth's nominal ~2 s tail-flush length (Method
A gain-clamps and sums these in-place — they do not truncate the full mix).
c6 auditor watch item CLOSED as `PASS`.

## 4. Determinism, anchors, tests

- **Byte-determinism ×2** on all three c7 JSONs verified by
  `scripts/v3_spine/byte_det_c7.py`. Per-artifact sidecars at
  `data/v3_spine/cycle7/*.byte_determinism.json`; roll-up at
  `data/v3_spine/cycle7/byte_determinism.json` (`all_equal=true`).
- **Anchor preservation** at
  `data/v3_spine/31a164f845f8e27e/anchor_preservation_c7.json`:
  `n_pre=87, n_post=87, n_diff=0, all_match=true` (target ≥75).
  Includes all locked scripts (`render_stem.py` `214372d9…5b2b`,
  `rc7_v2_rerun.py`, `rc7_mix_balance.py`,
  `mix_match_operator_section.py`, `rc7_v2_rerun_v3_paths.py`),
  c4/c5/c6 delivery WAVs + verdicts, SF2, all `docs/v3_spine_*.md`,
  all `data/v3_spine/*_hash.txt`, `data/recreate_v2/focus_set_v2.json`.
- **Tests** at `tests/test_v3_spine_c7.py`: 17/17 PASS covering Track A
  dry-run schema + execute-guard + no-network-imports + venv-unchanged;
  Track B note contents + no-verdict-tokens; Track C full-mix + shorts;
  locked-script SHAs unchanged; c4/c5/c6 delivery SHAs unchanged; 87-anchor
  preservation; three-way `rubric_hash_v2` chain; verdict shape;
  `blocked_on_operator`; byte-det sidecars; interpreter guards; no PRNG.

## 5. Ledger events, plan-of-record

10 c7 ledger events landed (run_id `run-2026-09-02T130000Z`,
ts `2026-09-02T13:00:00Z`):

1. `M-V3-SPINE-1/torch213-reproduce-probe-completed`
2. `M-V3-SPINE-1/rc7-canonicality-note-completed`
3. `M-V3-SPINE-1/empty-stem-duration-sanity-completed`
4. `M-V3-SPINE-1/anchor-preservation-pre-c7-verified`
5. `M-V3-SPINE-1/anchor-preservation-post-c7-verified`
6. `M-V3-SPINE-1/verdict-c7-emitted` (`status=action_required`)
7. `_infra/adopt-cycle7-tests`
8. `M-INGEST-1/egress-probe-cycle7` (linear path B per c49 policy)
9. `_plan/register-c7-v3-spine-sub-leaves`
10. `_archive/cycle-7-scratch` (**single emission** AFTER physical move —
    fix c6 double-emission pattern per c7 brief)

Plan-of-record updated with 8 new rows (6 M-V3-SPINE-1 sub-leaves +
egress-probe-cycle7 + register-c7). promise_check 0-ERROR
post-registration.

## 6. Verdict

`data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json` —
verdict placement follows the `cycle<N>/` convention per c6 auditor MINOR
fix. Grep-check of `scripts/` for `verdict_c6` showed only the self-emitter
(`scripts/v3_spine/verdict_c6.py`) and its test (`tests/test_v3_spine_c6.py`)
consuming the flat path; no downstream scripts require the flat form, so
no flat mirror is created for c7.

**Verdict:** `V3_SPINE_C7_THREE_TRACK_LANDS_pending_operator`.
**Three-way `rubric_hash_v2` chain:** doc SHA ==
`data/v3_spine/rubric_hash_v2.txt` == `verdict.rubric_hash_v2` ==
`c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`.
**Blocked on operator:** `true`. FD-6: operator ear on Chicken Grease
A/B is the only authoritative gate. M-V3-SPINE-1 cannot be marked LANDS
by any auditor — only an operator ear verdict on
`data/v3/deliveries/31a164f845f8e27e/operator_section/{original_ab,reconstruction_ab}_operator_section.wav`
can flip `blocked_on_operator=true → false`.

## 7. Issues, uncertainties, and handoffs

- **Auditor scrutiny points for c8:**
  1. **Method A vs Method B is not resolved.** Track B publishes
     characterization only — the operator still owes ear verdict on which
     candidate to promote. If c8 arrives without operator input,
     `_plan/wait-on-operator-cadence-flag` proposal fires per c6 auditor
     handoff.
  2. **Track A dry-run drafted the command; execution is deferred to
     operator directive.** The drafted command uses the raw muscriptor
     binary via `/usr/bin/python3` (interpreter-swap variant per brief).
     A second command form is also recorded (`-m muscriptor.cli`) in case
     the entrypoint is invoked as a module in a future cycle.
  3. **Three-way chain three-way byte-equality** enforced at emit
     (`verdict_c7.py` raises on drift). Auditor may spot-check by
     re-hashing `docs/v3_spine_rubric_v2.md`.
  4. **Anchor preservation** at 87/87 exceeds ≥75 target. Auditor may
     spot-check ≥12 anchors via `anchor_preservation_pre_c7.json` +
     `anchor_preservation_c7.json`.
- **Cycle-count meta observation:** per c6 auditor, if c8 also arrives
  without operator input, propose `_plan/wait-on-operator-cadence-flag`
  rather than manufacture a fourth substantive track. This cycle (c7) is
  the second consecutive substantive-track cycle with no operator input;
  the flag proposal is on-deck for c8 if the pattern persists.
- **Path forward:** M-V3-SPINE-1 remains blocked on operator ear.
  Downstream milestones (`M-V3-FOCUS-1`, `M-V3-CORPUS-1`, `M-V3-RULES-1`,
  `M-V3-EAR-1`, `M-V3-GEN-1`) frozen until operator lands the Chicken
  Grease spine.
