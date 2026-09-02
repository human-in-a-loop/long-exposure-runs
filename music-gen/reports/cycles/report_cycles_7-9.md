---
title: "Music-Gen v3 SPINE Milestone — Cycles 7–9"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 SPINE Milestone — Cycles 7–9

## Abstract

This report covers three consecutive cycles of work on the M-V3-SPINE milestone of the Music-Gen v3 campaign on the reference track *Chicken Grease* (source SHA-16 `31a164f845f8e27e`). Cycle 6 had closed with two byte-deterministic reconstructions on disk, a mechanistically attributed environment-drift explanation for the Cycle 3–4 guitar hash divergence, and the milestone's positive-verdict authority resting on operator ear judgment that had not yet arrived. Cycles 7–9 continue in that same operator-blocked state and, importantly, formalize the campaign's steady-state behavior under continued operator absence: Cycle 7 delivers a third and final substantive-track cycle (dry-run reproduction probe, canonicality characterization note, and empty-stem duration sanity check); Cycle 8 fixes a moderate append-only integrity finding surfaced against the Cycle 7 verdict, refreshes the dry-run probe, and lands a written cadence policy that switches the campaign into a heartbeat rhythm from Cycle 9 onward; Cycle 9 is the first cycle to fire under that policy, delivering liveness and housekeeping only, exactly as the policy prescribes. All three cycles land with `blocked_on_operator=true`; all three preserve every earlier delivery byte-identically; all pass their independent audits with zero critical or moderate findings.

## 1. Introduction and continuity from Cycles 4–6

By the end of Cycle 6 the spine pipeline was complete on both the 0–30 s compatibility window and the operator-chosen 233.64–263.64 s exposed section, byte-deterministic within any given cycle, structurally sound, and preserved cycle-over-cycle by an anchor integrity chain. Three operator-facing decisions were queued: (1) an ear verdict on either of the two A/B pairs; (2) approval to execute the drafted torch-2.13 reproduction; and (3) a canonicity choice between the plain broadband RMS-match chain (Method A, Cycle 5) and the twelve-band iirpeak-plus-loudness chain (Method B, Cycle 6). None of the three had arrived at the start of Cycle 7.

The campaign's operating rule under this condition — that the researcher must, at each cycle, either find operator input or produce substantive work without manufacturing a false lock decision — is what shapes the three-cycle arc reported here. Cycle 7 executes the last three substantive tracks that can be run without operator input while remaining honest about Fixed Decision 1's ban on retuning without an ear verdict. Cycle 8 closes an integrity finding surfaced against Cycle 7 and, having observed four consecutive substantive cycles with no operator input (Cycles 5–8), lands a written policy switching subsequent cycles into a heartbeat mode. Cycle 9 fires under that policy and produces the smaller, quieter deliverable set the policy calls for.

## 2. Methodology carried across all three cycles

The determinism protocol, environment pins, interpreter guard, anchor preservation snapshot mechanism, and three-way rubric-v2 hash integrity chain established in Cycles 4–6 are unchanged. Rubric v2 (`c49db5a12e955f26…451a`) remains the acceptance authority; the three-way byte-equality assertion among the rubric document, its pinned hash file, and each cycle's verdict.rubric_hash_v2 field holds across all three cycles. Every new script sets `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, and single-threaded BLAS via `os.environ.setdefault`. Every top-level invocation uses `/usr/bin/python3` (verified by an AST test guard). Every new deliverable is generated twice into fresh temporary directories and its SHA-256 asserted equal across runs. AST tests scan every new script for network-import symbols (`urllib`, `requests`, `httpx`, `socket`, `http`, `aiohttp`) and PRNG symbols, and fail on any hit.

Two integrity-chain mechanisms new to this arc:

- **Append-only discipline for delivered verdicts.** Once a cycle's `verdict.json` is emitted, its SHA-256 is pinned by every subsequent cycle and any change is treated as drift rather than as a normal update. Cycles 8 and 9 both pin the Cycle 7 verdict SHA `82d2b58924…5b75` and independently re-verify it byte-identical.
- **Amendment-by-sibling.** When a value pinned inside an already-emitted verdict cannot be reproduced from disk (as happened once in Cycle 8), the fix ships as a sibling JSON file at the same directory, carrying an explicit twelve-key amendment schema, rather than mutating the original verdict.

The anchor snapshot count grew from 87 (Cycle 7) to 103 (Cycle 8) to 116 (Cycle 9). Every locked script and every earlier delivery was byte-identical pre-versus-post at every cycle.

## 3. Cycle 7: three substantive tracks, executed linearly

Cycle 7 is the last cycle in this arc to run substantive tracks. Its verdict is `V3_SPINE_C7_THREE_TRACK_LANDS_pending_operator`.

### 3.1 Track A — Torch 2.13.0+cpu dry-run reproduction probe

The Cycle 6 attribution finding — that a c3-era `torch 2.13.0+cpu` is present at the system interpreter path — was formalized this cycle as an executable probe with a spec document (`docs/v3_spine_torch213_reproduce_spec.md`, SHA `820da97690893fa9…`) whose hash is pinned in `data/v3_spine/torch213_reproduce_spec_hash.txt`. The implementation `scripts/v3_spine/torch213_reproduce_probe.py` supports two modes gated by an `--execute` flag that defaults to false. Mode 1 (the only mode this cycle runs) captures the observed torch version and file path, records the c3 and c4 guitar JSON anchor hashes, drafts the reproduction command verbatim, and confirms that no network syscall was attempted and the venv is unchanged. The output pins:

| Field | Value |
|---|---|
| `torch_version_observed` | `2.13.0+cpu` |
| `torch_file_observed` | `/usr/local/lib/python3.11/dist-packages/torch/__init__.py` |
| `c3_guitar_json_sha_anchor` | `97b5a598db8424bb…` |
| `c4_guitar_json_sha_anchor` | `3107ba21e10acc70…` |
| `stem_input_sha256` | `bc01ff1f6ed4e778…` |
| `network_syscall_attempted` | `false` |
| `attribution_verdict` | `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_DRY_RUN` |

The drafted command uses `/usr/bin/python3` to invoke the venv-installed `muscriptor` binary directly, so the interpreter that imports torch is the system interpreter (which sees `2.13.0+cpu` from `dist-packages`) rather than the venv interpreter (which sees `2.14.0+cpu` from `site-packages`). This "interpreter-swap variant" is what allows the reproduction to run without any package install. Mode 2 execution is gated on a live-guidance operator directive; the campaign's rule is that a user prompt alone does not authorize it. Cycle 7 had no such directive.

### 3.2 Track B — rc7 canonicality decision note

`docs/v3_spine_rc7_canonicality_decision_note.md` is a one-page side-by-side characterization of the two mix chains, backed by numeric metrics computed in `data/v3_spine/cycle7/rc7_canonicality_metrics.json`. Under Fixed Decision 1 the note does not recommend either chain; it is explicitly grep-verified free of the tokens `LANDS`, `PARTIAL`, and `FAILS`, so it cannot masquerade as an authoritative verdict.

| Metric | Method A (Cycle 5 plain-RMS, SHA `cc919559…`) | Method B (Cycle 6 iirpeak+RMS+LUFS-S, SHA `f40796be…`) |
|---|---:|---:|
| Integrated LUFS | −19.95 LU | −17.87 LU |
| Short-term LUFS mean | −20.02 LU | −18.02 LU |
| Short-term LUFS std | 0.640 LU | 0.889 LU |
| Short-term LUFS max | −19.07 LU | −17.06 LU |
| True peak | −3.01 dBFS | −0.01 dBFS |
| Max absolute sample | 0.7070 | 0.9990 |
| Spectral centroid mean | 3 910 Hz | 2 353 Hz |
| Spectral centroid std | 2 740 Hz | 1 619 Hz |
| Spectral flatness mean | 0.03025 | 0.00684 |
| Mel-L1 vs original (0–30 s) | 8.73 dB | 7.49 dB |

Method A produces a darker, less-loud, more-flatly-shaped reconstruction; Method B produces a louder, more focused-centroid reconstruction closer in mel-L1 to the original. Both remain byte-deterministic within their originating cycles. The choice between them is now an operator-audible one.

### 3.3 Track C — empty-stem duration sanity

The Cycle 6 auditor had raised a watch item that the per-track render for stems whose canonical MIDI is empty emits a nominally 2-second silent WAV rather than a 30-second silent one, and asked whether this could truncate the summed full mix. `scripts/v3_spine/empty_stem_duration_sanity.py` measured every relevant file with librosa and closed the item cleanly:

| File | Samples | Duration | Sample rate |
|---|---:|---:|---:|
| Method A full-mix reconstruction | 1 323 000 | 30.000 s | 44 100 Hz |
| Method B full-mix reconstruction | 1 323 000 | 30.000 s | 44 100 Hz |
| Per-track `other.wav` (empty MIDI) | 88 320 | 2.003 s | 44 100 Hz |
| Per-track `piano.wav` (empty MIDI) | 88 320 | 2.003 s | 44 100 Hz |

The full-mix arithmetic is safe because the mix stage gain-clamps and sums the short empty-stem WAVs in place rather than concatenating them; the 30-second contract on the full mix holds. The short duration is fluidsynth's tail-flush length on empty MIDI input, which is expected. The watch item closed as `PASS`.

### 3.4 Discipline

Byte-determinism ×2 held on all three Cycle 7 JSONs; the roll-up sidecar `data/v3_spine/cycle7/byte_determinism.json` records `all_equal=true`. Anchor preservation held at 87 of 87 (target ≥75). Seventeen unit tests passed, covering the Track A dry-run schema and execute-guard, the Track B note contents and forbidden tokens, the Track C measurements, the locked-script SHAs, the Cycle 4/5/6 delivery SHAs, the three-way rubric chain, verdict shape, `blocked_on_operator`, byte-determinism sidecars, interpreter guards, and absence of PRNG.

Ten ledger events landed in strict order, including a single-emission `_archive/cycle-7-scratch` written *after* the physical move (fixing a double-emission pattern the Cycle 6 auditor had noted). `promise_check` reported zero errors. The Cycle 7 delivery landed at `data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.json` following the emergent `cycle<N>/` subdirectory convention.

## 4. Cycle 8: append-only integrity fix, dry-run refresh, cadence policy

Cycle 8 delivers three tracks under the verdict `V3_SPINE_C8_MODERATE_FIX_LANDS_pending_operator`. Its distinguishing move is the formalization of the campaign's steady-state cadence under operator absence.

### 4.1 Track 1 — Verdict-SHA drift and generic invariant test

At Cycle 8's top-of-cycle audit the Cycle 7 verdict was checked against its own pinned self-references. The Cycle 7 `verdict.json` had pinned `rc7_canonicality_note.sha256 = 3f8d5908…fa96e`, but the on-disk SHA of the note at Cycle 8's top-of-cycle was `451d20c0…320e`. The note had been touched during Cycle 7's close-out — a normal editing action from the researcher's point of view, but from the append-only-integrity point of view it was drift. `git cat-file -p 3f8d5908…fa96e` returned "Not a valid object name": the prior blob was not recoverable.

The response followed the amendment-by-sibling pattern. The Cycle 7 `verdict.json` was left byte-identical (its SHA `82d2b58924…5b75` is pinned in Cycle 8 and independently re-verified pre-versus-post). A sibling file `data/v3/deliveries/31a164f845f8e27e/cycle7/verdict.c8_amendment.json` was written carrying a twelve-key schema — `cycle`, `amends`, `amended_field`, pinned SHA, on-disk SHA, `prior_version_recoverable=false`, `diff_summary=null`, `canonical_designation=current_on_disk`, `root_cause`, `closure_action`, and provenance pins.

To prevent the same class of drift going forward, a new generic test `tests/test_verdict_sha_fields_resolve_on_disk.py` was written. It walks the newest delivered verdict JSON under `data/v3/deliveries/**/cycle*/verdict.json` and, for every field pair it finds, resolves the SHA claim to the referenced on-disk file and asserts byte equality. The walker distinguishes bare `sha256`/`path` pairings from prefixed `<stem>_sha256`/`<stem>_path` pairings, so the walker cannot misattribute an SHA across a multi-artifact dict. The rubric hash chain gets its own three-way test. The suite runs eight cases; it passes on the Cycle 8 verdict when Cycle 8 is newest, and it reports the Cycle 7 drift as a first-class failure when Cycle 7 is newest — proving the walker catches historical drift as well as new drift.

A ledger event `M-V3-SPINE-1/verdict-c7-sha-drift-amended` was emitted carrying a `supersedes_path` field.

### 4.2 Track 2 — Torch-2.13 dry-run refresh

The Cycle 7 probe module (`torch213_reproduce_probe.py`, SHA `b54adadd…9af3d`) was re-invoked from a Cycle 8 caller (`torch213_reproduce_probe_c8.py`) in Mode 1 with all four baseline checks recorded:

| Check | Cycle 7 baseline | Cycle 8 observed |
|---|---|---|
| `torch.__version__` | `2.13.0+cpu` | `2.13.0+cpu` |
| `torch.__file__` | `/usr/local/lib/python3.11/dist-packages/torch/__init__.py` | identical |
| Drafted reproduction command | pinned | byte-identical |
| Venv (`workspace/learned_transcribers_venv/`) directory manifest SHA | `a86205175728…f83a74` | identical |

`network_syscall_attempted=false`. `attribution_verdict = ENV_DRIFT_PROBE_CANDIDATE_FOUND_C8_DRY_RUN_ROLL_FORWARD`. Mode 2 execution remains gated on a live-guidance operator directive.

### 4.3 Track 3 — Wait-on-operator cadence policy

Four consecutive substantive-track cycles (5→6→7→8) had produced work without receiving operator input. Under the Cycle 6 auditor's precedent for exactly this pattern, the policy fires:

`docs/wait_on_operator_cadence_policy.md` (SHA `0be540365c8c03ad38a15478fbad0fe32bf5ea4118e33ef3eeed62dbd9a0c7f2`), with its hash pinned to `data/v3_spine/wait_on_operator_cadence_policy_hash.txt`, defines three clauses:

- **Cadence rule.** From Cycle 9 onward, absent a live-guidance operator directive, the default cycle is heartbeat only — an egress probe row, an archived scratch move row, an adopt-cycle-tests row, a plan-of-record registration row, and a torch-213 dry-run liveness re-run. No new substantive tracks are manufactured.
- **Break-glass.** An operator directive or an auditor CRITICAL finding reopens the cycle to substantive work.
- **Non-blocking.** The policy does not close M-V3-SPINE-1 and does not invalidate any of the `V3_SPINE_C{4,5,6,7}_..._LANDS_pending_operator` verdicts.

The policy sets `cycles_since_last_operator_input=4` and `flag_status=active`.

### 4.4 Discipline

Anchor preservation held at 103 of 103 (target ≥90). Fourteen new Cycle 8 tests, seventeen prior Cycle 7 tests, and eight generic-invariant tests all passed. `promise_check` reported zero errors. Every locked script remained byte-identical; the Cycle 7 verdict remained byte-identical; the amendment landed as a sibling, not as an in-place edit. Ten ledger events landed in strict order.

## 5. Cycle 9: first heartbeat under the new policy

Cycle 9 fires under the Cycle 8-landed policy. No operator directive was present in `live_guidance` and no auditor CRITICAL had surfaced, so the policy prescribes heartbeat scope: liveness + housekeeping, no fourth substantive M-V3-SPINE track manufactured. The verdict is `V3_SPINE_C9_HEARTBEAT_pending_operator`.

Deliverables:

1. **Torch-213 liveness roll-forward.** `data/v3_spine/cycle9/torch213_reproduce_probe_c9.json` re-runs the Cycle 7 probe module and re-checks all four baselines. All four match Cycle 7 and Cycle 8 identically: torch version `2.13.0+cpu`, torch file at `/usr/local/lib/python3.11/dist-packages/torch/__init__.py`, drafted command in both binary and module forms byte-identical, venv directory manifest SHA `a86205175728…f83a74` identical. `network_syscall_attempted=false`. Attribution verdict `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C9_DRY_RUN_ROLL_FORWARD`.
2. **Anchor preservation.** 116 of 116 anchors byte-identical pre-versus-post (target ≥110). Every locked script — `render_stem.py`, `rc7_v2_rerun.py`, `rc7_mix_balance.py`, `mix_match_operator_section.py`, `rc7_v2_rerun_v3_paths.py`, `torch213_reproduce_probe.py`, `torch213_reproduce_probe_c8.py` — preserved. Every prior delivery (Cycles 4/5/6/7/8) preserved. The Cycle 7 verdict is preserved at SHA `82d2b58924…5b75` and the Cycle 8 amendment intact.
3. **Verdict emission.** Placed at `data/v3/deliveries/31a164f845f8e27e/cycle9/verdict.json`. Three-way rubric chain byte-equal. `blocked_on_operator=true`.
4. **Housekeeping.** Egress probe row appended (HTTP 429 + tv_embedded response unchanged); `_archive/cycle-9-scratch` written after the physical move; `_infra/adopt-cycle9-tests` row for the new Cycle 9 test suite; `_plan/register-c9-v3-spine-sub-leaves` row for the four sub-leaves plus the egress row.

Test suites: 12/12 Cycle 9 tests green, 14/14 Cycle 8 sanity-floor, 8/8 generic-invariant on the Cycle 9 verdict, 17/17 Cycle 7 sanity-floor — 51/51 total. Eight ledger events landed in strict order, with the `_archive/cycle-9-scratch` row timestamped one second after the others to reflect its post-move placement.

The Cycle 9 audit noted three cumulative properties worth recording:

- Five consecutive cycles (5–9) have passed independent SHA spot-checks with zero fabrications detected across 30-plus verifications. Trust ledger is holding; the auditor plans to maintain rather than escalate spot-check density.
- The anchor-set growth curve is flattening (87 → 103 → 116; deltas +16, +13), consistent with heartbeat cycles adding fewer new anchors than substantive cycles. Growth will asymptote as heartbeats consume the cadence.
- The torch-2.13 environment is stable across three cycles: identical venv directory manifest, identical torch version, identical file location. Environment drift is not accumulating during the wait.

## 6. Current state and open decisions

The M-V3-SPINE-1 milestone remains gated on operator ear per Fixed Decision 6. Five verdicts of the form `V3_SPINE_C{5,6,7,8,9}_..._LANDS_pending_operator` sit on disk, all byte-identical to their emission-time hashes, all with `blocked_on_operator=true`, all with the three-way rubric integrity chain byte-equal. Two byte-deterministic reconstructions remain the operator-facing A/B candidates: `data/v3/deliveries/31a164f845f8e27e/operator_section/reconstruction_ab_operator_section.wav` (Method A) and `data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav` (Method B).

Three operator-facing decisions remain queued, unchanged from the end of Cycles 4–6:

1. **Ear verdict on either A/B pair.** A positive verdict opens `M-V3-FOCUS-1` (Chicken Grease anchor plus four SHA-256-tiebreak picks from `data/recreate_v2/focus_set_v2.json`); a negative verdict pivots to the operator-named failure axis.
2. **Approval to run torch-2.13 reproduction Mode 2.** The drafted commands are pinned in the probe JSONs of Cycles 7/8/9 byte-identically. Any of the three verdicts the reproduction can produce — `ENV_DRIFT_CONFIRMED_TORCH_MINOR_VERSION`, `ENV_DRIFT_NOT_TORCH_ALONE`, or `ENV_DRIFT_THIRD_STATE` — is first-class per Fixed Decision 1.
3. **Canonicality choice between the two mix chains.** The characterization note is landed; the choice awaits ear input.

Downstream milestones `M-V3-FOCUS-1`, `M-V3-CORPUS-1`, `M-V3-RULES-1`, `M-V3-EAR-1`, and `M-V3-GEN-1` remain frozen. Under the Cycle 8-landed policy, subsequent cycles (Cycle 10 and beyond) will fire as heartbeats until an operator directive or an auditor CRITICAL finding breaks the glass. There is no cycle-count ceiling on the heartbeat cadence; the campaign's steady state under operator absence is quiet by design.

## 7. Conclusions

The arc from Cycle 7 to Cycle 9 is the campaign's transition from "pursue substantive work while waiting" to "run quiet, verifiable heartbeats while waiting", executed transparently through a written policy rather than through drift or abandonment. Cycle 7 finished the substantive tracks that could honestly be run without operator input. Cycle 8 caught and disclosed the one moderate integrity finding of the arc — a Cycle 7 sibling artifact touched after emission — repaired it by an append-only amendment rather than by an in-place mutation, and generalized the fix into a walker test that any future cycle will inherit for free. Cycle 9 demonstrated the heartbeat mode working exactly as specified, producing the small, honest, four-slot deliverable set the policy calls for and no manufactured substance.

Two properties of the milestone worth naming explicitly at this point: first, the byte-integrity chain is now robust enough that five consecutive cycles of independent SHA spot-checks turned up zero fabrications, and the append-only invariance of prior verdicts has survived one deliberate perturbation and been tested against future ones; second, the environment-drift attribution has held stable across three re-checks with an identical venv manifest, confirming that the campaign is not accumulating hidden variance during the wait. What remains is not code — it is operator judgment. The pipeline stands ready to consume any of the three queued decisions in a single subsequent cycle.

## Appendix: Implementation Details

### A.1 Delivered artifacts by cycle

Cycle 7, under `data/v3/deliveries/31a164f845f8e27e/cycle7/`:
`verdict.json`, `torch213_reproduce_probe.json`, `rc7_canonicality_metrics.json`, `empty_stem_duration_sanity.json`, `v3_spine_rc7_canonicality_decision_note.md` (also under `docs/`), and (added in Cycle 8) `verdict.c8_amendment.json`.

Cycle 8, under `data/v3/deliveries/31a164f845f8e27e/cycle8/`:
`verdict.json`. Additional cycle work under `data/v3_spine/cycle8/torch213_reproduce_probe_c8.json`, and policy artifacts at `docs/wait_on_operator_cadence_policy.md` + `data/v3_spine/wait_on_operator_cadence_policy_hash.txt`.

Cycle 9, under `data/v3/deliveries/31a164f845f8e27e/cycle9/`:
`verdict.json`. Additional cycle work under `data/v3_spine/cycle9/torch213_reproduce_probe_c9.json` and `data/v3_spine/cycle9/anchor_preservation_{pre,post,}_c9.json`.

Cycle-scoped reports on disk at `docs/v3_spine_report_cycle7.md`, `docs/v3_spine_report_cycle8.md`, `docs/v3_spine_report_cycle9.md`.

### A.2 Scripts and specs

Added or extended: `docs/v3_spine_torch213_reproduce_spec.md`; `scripts/v3_spine/torch213_reproduce_probe.py`; `scripts/v3_spine/torch213_reproduce_probe_c8.py`; the Cycle 9 caller; `scripts/v3_spine/empty_stem_duration_sanity.py`; the byte-determinism roll-up scripts; `docs/wait_on_operator_cadence_policy.md`; anchor preservation drivers per cycle; `docs/v3_spine_rc7_canonicality_decision_note.md`.

Locked (read-only, byte-identical across all three cycles): `scripts/palette_render/render_stem.py` = `214372d9…5b2b`; `scripts/v3_spine/mix_match_operator_section.py` = `4f47fbcd…`; `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` = `eaaa993e…`; `scripts/recreate_v2/rc7_v2_rerun.py` = `7a5fbef0…`; `scripts/v3_spine/rc7_mix_balance.py`. Probe modules become locked at their emission cycle: Cycle 7 probe `b54adadd…9af3d`, Cycle 8 probe `c207a00a…70334`.

### A.3 Tests

`tests/test_v3_spine_c7.py` (17 cases); `tests/test_v3_spine_c8.py` (14 cases); `tests/test_v3_spine_c9.py` (12 cases); `tests/test_verdict_sha_fields_resolve_on_disk.py` (8 cases, generic across every future verdict). Fifty-one tests total in the current sanity-floor cumulative set; all passed on independent auditor re-run at Cycle 9 under the mandated environment.

### A.4 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; single-threaded BLAS via `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3` (guard verified by AST test); `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`.

### A.5 Integrity chains and invariants

Three-way rubric-v2 chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26…451a` == `data/v3_spine/rubric_hash_v2.txt` content == each cycle's `verdict.rubric_hash_v2`. Cadence-policy chain (Cycle 8+): doc SHA `0be540365c8c03ad…c7f2` == `data/v3_spine/wait_on_operator_cadence_policy_hash.txt` content. Torch-213 spec chain (Cycle 7+): doc SHA `820da97690893fa9…` == `data/v3_spine/torch213_reproduce_spec_hash.txt` content. Cycle 7 verdict SHA pinned by every subsequent cycle: `82d2b58924…5b75`. Cycle 8 verdict SHA pinned by Cycle 9: `314ae6ee…38a9`. Venv directory-manifest SHA stable across Cycles 7/8/9: `a86205175728…f83a74`.

Anchor snapshot counts (pre == post at every cycle): 87 (Cycle 7), 103 (Cycle 8), 116 (Cycle 9). Auditor spot-checks ≥5–12 per cycle across five cycles found zero fabrications.

### A.6 Ledger events

Cycle 7 ledger events (ts `2026-09-02T13:00:00Z`): three substantive-track completions, anchor-preservation pre/post, verdict emission (`action_required`), `_infra/adopt-cycle7-tests`, `M-INGEST-1/egress-probe-cycle7`, `_plan/register-c7-v3-spine-sub-leaves`, and a single-emission `_archive/cycle-7-scratch` after the physical move.

Cycle 8 ledger events (ts `2026-09-02T13:00:00Z`): `M-V3-SPINE-1/verdict-c7-sha-drift-amended`, `M-V3-SPINE-1/torch213-reproduce-probe-c8-completed`, `_plan/wait-on-operator-cadence-flag`, anchor pre/post, verdict emission (`action_required`), egress probe, plan-of-record register, adopt-tests, and post-move archive.

Cycle 9 ledger events (ts `2026-09-02T14:00:00Z` × 7 + `T14:00:01Z` × 1 for the post-move archive): torch-213 probe completion, anchor pre/post, verdict emission (`action_required`), egress probe, plan-of-record register, adopt-tests, and post-move archive.

### A.7 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 7 | ec193c47-509d-4929-925d-5cd1f0b1a2e6 | 8b84be92-8f1b-42fc-9133-ad36ea7a6103 | 9c847691-0be9-4ec4-b56b-17033da4b664 |
| 8 | 42634954-95c5-4c38-85af-0be437cfd111 | 1e0bda20-222a-4449-91da-56c2f1cf6ca5 | c344d9f4-a946-4d81-926b-2b160119db9a |
| 9 | 71e4354b-c460-4b8c-af61-fcad6abafec4 | cdcbfeab-66fe-4a67-b028-852ea2d6f915 | fb47cc03-996c-4ea3-8c44-cd6ef064257e |
