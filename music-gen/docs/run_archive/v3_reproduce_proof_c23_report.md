---
created: 2026-09-02T22:57:00Z
run_id: run-2026-09-02T225700Z-c23
agent: worker
cycle: 23
milestone: M-V3-SPINE-2/reproduce-proof-chicken-grease + /reproduce-proof-rome
fork: d5530f8d1ccc
clone: clone-0
---

# c23 v3 Reproduce-Proof Report — Chicken Grease + Rome

**Verdict summary**

| song           | sha16              | verdict                | panel_equal_all_keys | env_pin identical | anchor pre==post |
|----------------|--------------------|------------------------|----------------------|-------------------|------------------|
| Chicken Grease | `31a164f845f8e27e` | `REPRODUCE_PANEL_ONLY` | true                 | false (pre-c22)   | true             |
| Rome           | `51e433ade2a845e1` | `REPRODUCE_PANEL_ONLY` | true                 | false (pre-c22)   | true             |

Both reproduce-proofs LAND on the panel-equal criterion. Env-pin drift is the
documented expected state: both anchor deliveries pre-date the c22 unified
driver and therefore carry no `env_pin.json` for comparison. Per the c23
rubric §Downstream unblock, this **authorizes c24 execution of the
`_infra/retire-oneoff-drivers-c22` deletion contract** (37 per-song scripts
per catalog `data/v3/recreate_v3/retirement_catalog_c22.json`).

## 1. Scope executed

Two songs, one section each, one c22 unified-driver invocation per song:

```
scripts/v3_reproduce_c23/run_reproduce.py --song <sha16>
  → scripts/v3_spine/recreate_v3.py --song <sha16> --section operator ...
  → scripts/v3_reproduce_c23/emit_reproduce_report.py ...
```

- Chicken Grease operator section `t = 233.639 .. 263.639 s` (from
  `data/recreate_v2/focus_set_v2.json`).
- Rome operator section `t = 62.740 .. 92.740 s`.

## 2. Three-way `rubric_hash_v3_reproduce` chain

Chain holds byte-identically for both songs' reproduce reports:

    docs/v3_reproduce_proof_c23_rubric.md (SHA-256)
      == data/v3_reproduce_c23/rubric_hash.txt (content)
      == data/v3/reproduce/c23/<sha16>/reproduce_report.json.rubric_hash_v3_reproduce

    rubric_hash_v3_reproduce = 3fe5545bfce62723a9c9faf7391e6ad8f31a1731cde18641569e419d772f792e

mtime hard-gate: rubric doc mtime `1788388016.161693` precedes every script
mtime under `scripts/v3_reproduce_c23/`; 0 violations recorded.

## 3. READ-ONLY anchor pre==post

| anchor                                                                                            | expected SHA-256 (prefix) | observed pre | observed post | matches |
|---------------------------------------------------------------------------------------------------|---------------------------|--------------|---------------|---------|
| `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav`   | `cc919559b4508b6b…`       | ✓            | ✓             | ✓       |
| `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json`                                        | `d2c2d704ce910fde…`       | ✓            | ✓             | ✓       |

Both READ-ONLY anchors byte-identical pre==post. Zero drift.

## 4. Per-key panel diff

### Chicken Grease

Anchor: `data/v3/deliveries/31a164f845f8e27e/operator_section/panel.json`
New:    `data/v3/deliveries/31a164f845f8e27e/cycle23_reproduce/panel.json`

| key                          | new                    | old                    | delta_abs   | tolerance | within |
|------------------------------|------------------------|------------------------|-------------|-----------|--------|
| mel_l1_db                    | 8.786022822062174      | 8.786022822062174      | 0.0         | 0.05      | ✓      |
| spectral_centroid_rmse_hz    | 3254.471208475288      | 3254.4710754437547     | 1.33e-04    | 2.0       | ✓      |
| rms_env_rmse                 | 0.14728470146656036    | 0.14728470146656036    | 0.0         | 0.002     | ✓      |
| lufs_m_rmse_lu               | 7.275522708892822      | 7.2755231857299805     | 4.77e-07    | 0.05      | ✓      |
| embedding_cosine_distance    | 0.18761603218358625    | 0.18761604806002197    | 1.59e-08    | 0.005     | ✓      |
| n_samples_compared           | 1323000                | 1323000                | 0           | 0 exact   | ✓      |
| sr_hz                        | 44100                  | 44100                  | 0           | 0 exact   | ✓      |
| section                      | "operator_section"     | "operator_section"     | –           | exact str | ✓      |

`panel_equal_all_keys = true` (8/8).

### Rome

Anchor: `data/v3/deliveries/51e433ade2a845e1/panel.json`
New:    `data/v3/deliveries/51e433ade2a845e1/cycle23_reproduce/panel.json`

| key                          | new                    | old                    | delta_abs   | tolerance | within |
|------------------------------|------------------------|------------------------|-------------|-----------|--------|
| mel_l1_db                    | 9.322155952453613      | 9.322155634562174      | 3.18e-07    | 0.05      | ✓      |
| spectral_centroid_rmse_hz    | 3101.5860468287988     | 3101.5847635878754     | 1.28e-03    | 2.0       | ✓      |
| rms_env_rmse                 | 0.11502177268266678    | 0.11502177268266678    | 0.0         | 0.002     | ✓      |
| lufs_m_rmse_lu               | 7.554287433624268      | 7.554287910461426      | 4.77e-07    | 0.05      | ✓      |
| embedding_cosine_distance    | 0.085742948468154      | 0.08574265096864908    | 2.97e-07    | 0.005     | ✓      |
| n_samples_compared           | 1323000                | 1323000                | 0           | 0 exact   | ✓      |
| sr_hz                        | 44100                  | 44100                  | 0           | 0 exact   | ✓      |
| section                      | "operator_section"     | "operator_section"     | –           | exact str | ✓      |

`panel_equal_all_keys = true` (8/8).

## 5. Per-stage byte-equality

All comparable stage artifacts show byte drift, which under env-pin-drift
(both anchors are pre-c22) is expected and per rubric §Byte-equal contract
downgrades to `REPRODUCE_PANEL_ONLY`, not `REPRODUCE_FAILS`.

### Chicken Grease

| stage_file              | new_sha (prefix)   | old_sha (prefix)   | size_new  | size_old  | byte_equal | comparable |
|-------------------------|--------------------|--------------------|-----------|-----------|------------|------------|
| merged.mid              | `0087064f7980…`    | (n/a in anchor)    | 5151      | –         | –          | false      |
| original_ab.wav         | `b2f7cc1adfa3…`    | `575af6cedb80…`    | 5292216   | 5292216   | false      | true       |
| reconstruction_ab.wav   | `64921467a735…`    | `cc919559b450…`    | 5292044   | 5292044   | false      | true       |
| full_reconstruction.wav | `64921467a735…`    | `cc919559b450…`    | 5292044   | 5292044   | false      | true       |

Note: `reconstruction_ab.wav` and `full_reconstruction.wav` share the same
SHA on the new side (deterministic identity per c22 driver `assemble_delivery`
copy) — anchor differ in filename but map via `_operator_section` suffix.

### Rome

| stage_file              | new_sha (prefix)   | old_sha (prefix)   | size_new  | size_old  | byte_equal | comparable |
|-------------------------|--------------------|--------------------|-----------|-----------|------------|------------|
| merged.mid              | `e3d056296a34…`    | `c28b8686684f…`    | 5093      | 5093      | false      | true       |
| original_ab.wav         | `c3a65202a884…`    | `6548da39f97b…`    | 5292202   | 5292202   | false      | true       |
| reconstruction_ab.wav   | `6722c6c99925…`    | `c710dcb9eeb5…`    | 5292044   | 5292044   | false      | true       |
| full_reconstruction.wav | `6722c6c99925…`    | `c710dcb9eeb5…`    | 5292044   | 5292044   | false      | true       |

All four canonical-name stage anchors are comparable for Rome (the c20 delivery
carries them at the parent dir alongside `panel.json`). Sizes match exactly on
every comparable pair; byte drift is under env-pin drift only.

## 6. Env-pin diff-vs-original-manifest

Both songs share the same c23 env_pin manifest (identical env pins across the
two driver invocations, same interpreter, same session):

    env_pin_sha256 (new, both songs) = 623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d
    env_pin_sha256 (old, both songs) = null (pre-c22 anchor — no env_pin.json)

`per_field_deltas = {}` because no old field is available for pointwise
comparison. The `identical=false, note="no env_pin.json in existing delivery
(pre-c22)"` state is what rubric §Env-pin diff explicitly names as the
expected outcome for both Chicken Grease (c5 operator-blessed) and Rome (c20)
anchors.

## 7. Structural gate

`merged.mid` structural gate (4/4) passes on both songs per the c22 driver
`stage_merge` output; propagated to `structural_gate_ok = true` in both
`reproduce_report.json` files.

## 8. Emitter-side defect covers (documented)

Two correctness fixes landed in `scripts/v3_reproduce_c23/emit_reproduce_report.py`
during c23 to make the emitter honestly reflect the delivery-panel shape;
neither is a tuning knob or a rubric-threshold change.

1. **Panel-nested key extraction.** Existing panel.json files (both c22 driver
   `stage_panel` output and pre-c22 c5/c20 anchor deliveries) put the 8-key
   panel dict under `"panel": {...}` rather than at top level. The emitter's
   `diff_panel` originally read `pn.get(key)` at top level, which returned
   `None` for every key and caused a spurious `REPRODUCE_FAILS`. Fix: extract
   `panel = raw.get("panel", raw)` for both sides. Correctness-only.

2. **`section` derivation fallback.** The c22 driver's `stage_panel` does not
   emit `section` in `panel.json` (only via outer wrapper of the c5 anchor
   and via manifest.json for c22 deliveries). The rubric names `section` as
   one of the 8 panel keys. The emitter now falls back to reading `section`
   from the same-directory `manifest.json` (via `ab_window_operator_section`
   or `artifacts.*_operator_section_*` key presence) or `run_report.json`.
   Only `"operator_section"` can be produced by the c22 driver today (`auto`
   raises `NotImplementedError`). This is a defect cover for the driver's
   missing panel-field emission, applied uniformly to both new and anchor
   sides, not a fabrication of missing data.

Both fixes preserve the mtime-hard rubric-precedes-script ordering (script
mtimes strictly greater than rubric doc mtime `1788388016.161693`).

The proper long-term fix is to add `section` to `stage_panel` output in the
c22 driver directly. That is a c22 driver correctness fix, not a c23 change,
and is queued as a handoff to c24 or later.

## 9. Rome anchor delivery dir correction

The initial `run_reproduce.py` `ANCHOR_DELIVERY` map pointed Rome to
`data/v3/deliveries/51e433ade2a845e1/cycle20/` — which contains only
`verdict.json`. The full c20 delivery (panel.json, original_ab.wav,
full_reconstruction.wav, merged.mid) lives at the parent
`data/v3/deliveries/51e433ade2a845e1/`. The map now points there.

The READ-ONLY anchor SHA `d2c2d704…` still applies to
`cycle20/verdict.json` and is checked separately by
`snapshot_readonly_anchor()`; the two pieces of Rome anchor state are
decoupled and both verified pre==post.

## 10. Downstream unblock

Per rubric §Downstream unblock, both `REPRODUCE_PANEL_ONLY` verdicts under
the expected pre-c22 env-pin drift **authorize** c24 execution of the
`_infra/retire-oneoff-drivers-c22` deletion contract per the catalog
`data/v3/recreate_v3/retirement_catalog_c22.json` (37 scripts).

Deletion contract execution is queued for c24; c23 catalogs authorization
but does not itself delete. This matches the c22 catalog's explicit
deferral note ("Deletion queued for the first cycle after reproduce-proof
PASS on both CG and Rome").

## 11. Anti-pattern discipline

- Zero PRNG in `scripts/v3_reproduce_c23/*.py` (deterministic SHA-256 +
  file-order sort only).
- Zero `sidecar_nonfactor` imports.
- Zero VST3 state-extraction API calls (no `save_state`, `get_state`,
  `load_state`, `set_state(bytes)` — this cycle uses fluidsynth-only paths
  in the c22 driver).
- `/usr/bin/python3` interpreter guard present in every c23 script.
- c32 fanout-namespace convention observed: infra-family ledger events
  (`_archive`, `_run`, `_plan`, `_manager`, `_infra`) carry `-clone-0`
  suffix; substantive `M-V3-SPINE-2/*` sub-leaves remain unsuffixed.
- FD-1 honored: no tuning, no retry, no fallback. The two emitter fixes are
  legitimacy repairs (correctness bugs blocking honest comparison), not
  tuning of thresholds or "close enough" nudges. Rubric thresholds are
  unchanged.

## 12. Ledger events

Six named + two housekeeping events emitted under `-clone-0` suffix per
c32:

Named (3 per song × 2 songs = 6):
- `M-V3-SPINE-2/reproduce-proof-chicken-grease/rubric-committed`
- `M-V3-SPINE-2/reproduce-proof-chicken-grease/driver-invoked`
- `M-V3-SPINE-2/reproduce-proof-chicken-grease/verdict-emitted`
- `M-V3-SPINE-2/reproduce-proof-rome/rubric-committed`
- `M-V3-SPINE-2/reproduce-proof-rome/driver-invoked`
- `M-V3-SPINE-2/reproduce-proof-rome/verdict-emitted`

Housekeeping:
- `_archive/cycle-23-scratch-clone-0`
- `_infra/adopt-cycle23-tests-clone-0` (honest empty — no new tests
  landed this cycle; the c22 driver test suite covers reproduce-check
  contract at 20/20 already)

## 13. Handoffs to c24

1. **`_infra/retire-oneoff-drivers-c22` deletion contract execution.** All
   preconditions met (both songs `REPRODUCE_PANEL_ONLY`, anchors byte-
   identical). Execute per catalog.
2. **c22 driver correctness fix**: extend `stage_panel` in
   `scripts/v3_spine/recreate_v3.py` to include `section` in `panel.json`
   output. Retires the c23 emitter-side derivation fallback.
3. **Env-pin identity gate**: once ≥1 delivery is produced by the c22
   driver from a fresh clone AND compared against another c22-driver
   delivery, exercise the `REPRODUCE_LANDS` path (env_pin.identical=true +
   byte-equal). This cycle could not exercise it because both anchors
   pre-date c22.
