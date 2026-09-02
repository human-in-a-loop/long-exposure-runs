---
title: "Music-Gen v3 SPINE Milestone — Cycles 11–13"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 SPINE Milestone — Cycles 11–13

## Abstract

This report covers three consecutive heartbeat cycles of the M-V3-SPINE milestone on the reference track *Chicken Grease* (source SHA-16 `31a164f845f8e27e`). All three cycles operate under the wait-on-operator cadence policy landed in Cycle 8 and observe its two break-glass triggers — a live-guidance operator directive, or an auditor CRITICAL finding — as absent throughout the arc. The policy prescribes, in that condition, a small four-slot deliverable set repeated verbatim each cycle: (1) a Mode-1-only dry-run of the torch-2.13.0+cpu reproduction probe, (2) a pre-versus-post anchor preservation snapshot, (3) a verdict emission, and (4) four housekeeping ledger rows. Cycles 11, 12, and 13 land that shape three times, extending the campaign's consecutive-heartbeat streak from two (through Cycle 10) to five. Every earlier verdict remains byte-identical on disk; the anchor snapshot grew from 126 anchors at Cycle 10 through 136, 146, and 156 across this arc; the three-way rubric-v2 integrity chain, the seven-cycle venv byte-identity, and the Mode-2 lock on the torch reproduction all remain intact. Nine consecutive audit cycles (5–13) now pass independent SHA spot-checks with zero fabrications detected across roughly seventy verifications. M-V3-SPINE-1 remains gated on operator ear per Fixed Decision 6; all five downstream milestones remain frozen.

## 1. Introduction and continuity from Cycles 7–9

By the end of Cycle 9 the campaign had transitioned from substantive-track cycles into steady-state heartbeats under a written policy. The policy's cadence rule is that in any cycle where `live_guidance` carries no operator directive and the immediately-preceding cycle's audit report carries no CRITICAL finding, the researcher must run a heartbeat rather than manufacture a fresh substantive track. The policy's break-glass rule is that either an operator directive or an auditor CRITICAL reopens substantive work. The policy is non-blocking: it does not close M-V3-SPINE-1 and does not invalidate any of the earlier `V3_SPINE_C{4..7}_..._LANDS_pending_operator` verdicts, all of which remain on disk byte-identical.

Cycle 10 (not covered here) fired as the second heartbeat under the policy and, per the auditor of the Cycles 7–9 arc, extended the anchor list by +10 to 126. This report picks up at Cycle 11 (third heartbeat) and covers Cycles 11, 12, and 13 (fifth heartbeat).

## 2. Methodology carried across all three cycles

The determinism protocol, environment pins, interpreter guard, anchor snapshot mechanism, three-way rubric-v2 hash chain, append-only verdict discipline, and generic verdict-SHA-resolution walker test established across Cycles 4–9 are unchanged. Every new script sets `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, and single-threaded BLAS via `os.environ.setdefault`. Every top-level invocation uses `/usr/bin/python3`. AST tests scan every new script for network-import and PRNG symbols and fail on any hit.

Three particularly load-bearing invariants for a heartbeat cycle are worth restating:

- **Rubric-v2 three-way chain.** The rubric document at `docs/v3_spine_rubric_v2.md` has SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`; the pinned hash file at `data/v3_spine/rubric_hash_v2.txt` must contain that exact string; each cycle's emitted `verdict.json` must carry that string in `rubric_hash_v2`. Any of the three failing to match halts the cycle.
- **Cadence-policy hash chain.** The policy document at `docs/wait_on_operator_cadence_policy.md` has SHA `0be540365c8c03ad38a15478fbad0fe32bf5ea4118e33ef3eeed62dbd9a0c7f2`; the pinned hash file at `data/v3_spine/wait_on_operator_cadence_policy_hash.txt` must contain that string. This chain is a compact machine-readable assertion that the policy under which this heartbeat cycle is running has not itself been mutated.
- **Torch-213 Mode-2 lock.** The Mode-1 dry-run of the torch reproduction probe is always run and always produces `attribution_verdict = ENV_DRIFT_PROBE_CANDIDATE_FOUND_C<N>_DRY_RUN_ROLL_FORWARD`. The Mode-2 execution — the branch that would actually re-run MuScriptor under the system-Python torch 2.13.0+cpu — is gated on a live-guidance operator directive. A per-turn user prompt does not authorize it; only a live-guidance operator directive counts. This is a durable lock inherited from Cycle 7.

The **backref pattern** used from Cycle 10 onward pins the immediately-preceding cycle's `verdict.json` SHA into the current cycle's verdict as `c<N-1>_backref_sha`, resolved at emit time from disk rather than fabricated. Combined with the generic `test_verdict_sha_fields_resolve_on_disk.py` walker, this makes silent mutation of a previously delivered verdict a first-class failure at any future cycle.

## 3. Heartbeat shape (identical across Cycles 11, 12, 13)

Each of the three cycles delivers exactly four artifacts, four housekeeping ledger rows, and a small test suite of the same twelve-case shape.

### 3.1 Track 1 — Torch-213 dry-run liveness roll-forward

A new small caller script imports the read-only Cycle 7 probe module (`torch213_reproduce_probe.py`, SHA `b54adadd1f4f04028d4d931710cc02b722c82ebee027728a97adfa8b20c9af3d`) and runs Mode 1 only. Four checks are asserted against a cumulative baseline that grows by one cycle each pass:

| Check | Baseline value |
|---|---|
| `torch.__version__` | `2.13.0+cpu` |
| `torch.__file__` | `/usr/local/lib/python3.11/dist-packages/torch/__init__.py` |
| Drafted reproduction command (binary form and `-m muscriptor.cli` module form) | byte-identical to the Cycle 7 pin |
| Venv (`workspace/learned_transcribers_venv/`) directory-manifest SHA | `a86205175728…f83a74` |

All four passed in each of Cycles 11, 12, and 13. The attribution verdict fields at each cycle:

| Cycle | `attribution_verdict` | Baseline chain |
|---|---|---|
| 11 | `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C11_DRY_RUN_ROLL_FORWARD` | vs c7+c8+c9+c10 |
| 12 | `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C12_DRY_RUN_ROLL_FORWARD` | vs c7+c8+c9+c10+c11 |
| 13 | `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C13_DRY_RUN_ROLL_FORWARD` | vs c7+c8+c9+c10+c11+c12 |

`network_syscall_attempted=false` at each cycle (independently verified by the auditor's AST scan). `venv_unchanged=true` at each cycle. Mode 2 remains `awaiting_operator_green_light` at each cycle.

### 3.2 Track 2 — Anchor preservation

At the start of each cycle every read-only artifact is snapshotted; at end of cycle every anchor is re-hashed and byte equality asserted. The list grows by roughly ten anchors per cycle as the previous cycle's own artifacts (its verdict, its torch-probe JSON, its anchor-preservation JSONs, its driver script, its emitter script, its test file, and its report) join the list.

| Cycle | Anchor count | `all_match` | `n_diff` | Target |
|---|---:|:---:|:---:|---:|
| 11 | 136 | true | 0 | ≥125 |
| 12 | 146 | true | 0 | ≥145 |
| 13 | 156 | true | 0 | ≥155 |

Every locked script remained byte-identical across all three cycles: `render_stem.py = 214372d9…5b2b`, `mix_match_operator_section.py = 4f47fbcd…`, `rc7_v2_rerun.py = 7a5fbef0…`, `rc7_v2_rerun_v3_paths.py = eaaa993e…`, `rc7_mix_balance.py`, both torch probe modules (Cycle 7 probe `b54adadd…9af3d` and Cycle 12 probe `71da91b3…03bc1`), and every prior delivered verdict.

### 3.3 Track 3 — Verdict emission

Each cycle emits its verdict at `data/v3/deliveries/31a164f845f8e27e/cycle<N>/verdict.json` following the stable `cycle<N>/` subdirectory convention. The three verdict SHAs on disk at the end of this arc:

| Cycle | Verdict | On-disk SHA | `cycles_since_last_operator_input` |
|---|---|---|---:|
| 11 | `V3_SPINE_C11_HEARTBEAT_pending_operator` | `<pinned by c12 backref>` | 7 |
| 12 | `V3_SPINE_C12_HEARTBEAT_pending_operator` | `d6b67b232b1765b32b5eed91f3b76c7a6038bf71435256561d403752fcf60093` | 8 |
| 13 | `V3_SPINE_C13_HEARTBEAT_pending_operator` | `0f0143e6591441bd5da889d4c436de99b11d65a1b056bf0fef49a1455f69ef80` | 9 |

Each verdict carries `blocked_on_operator=true`, `cadence_mode=heartbeat`, a `prior_cycles` list enumerating every earlier cycle in the arc (Cycle 13's is `[c4, c5, c6, c7, c8, c9, c10, c11, c12]`), the `c<N-1>_backref_sha` pinned from the previous cycle's verdict file resolved at emit time, and Method A and Method B WAV SHAs pinned verbatim (Method A `cc919559b4508b6b…`; Method B `f40796be982998b0…`) with the `operator_ear_pending_fd6` status. The three-way rubric-v2 chain is byte-equal at each emission.

### 3.4 Track 4 — Housekeeping

Each cycle emits eight ledger events in strict order under a single cycle-scoped `run_id` (`run-2026-09-02T<HH>0000Z`):

1. `M-V3-SPINE-1/torch213-reproduce-probe-c<N>-completed`
2. `M-V3-SPINE-1/anchor-preservation-pre-c<N>-verified`
3. `M-V3-SPINE-1/anchor-preservation-post-c<N>-verified`
4. `M-V3-SPINE-1/verdict-c<N>-emitted` (`status=action_required`)
5. `M-INGEST-1/egress-probe-cycle<N>`
6. `_plan/register-c<N>-v3-spine-sub-leaves`
7. `_infra/adopt-cycle<N>-tests`
8. `_archive/cycle-<N>-scratch` (timestamped `ts+1s` after the physical move, per the Cycle 8 convention that fixed the earlier double-emission pattern)

The egress probe row records the persistent HTTP 429 + `tv_embedded` response (unchanged since Cycle 47 of the pre-pivot campaign); no unblock has appeared. The `_plan/register-<N>-v3-spine-sub-leaves` row registers the four sub-leaves and the egress-probe row into the plan-of-record. The `_infra/adopt-cycle<N>-tests` row adopts the twelve-case test file for the cycle. `promise_check` reports zero errors at each cycle.

### 3.5 Test discipline

Each cycle ships a fresh twelve-case test file (`tests/test_v3_spine_c<N>.py`) plus retains the earlier heartbeat suites and the generic invariant walker. Cumulative sanity-floor test counts through this arc:

| Cycle | New cases | Regression suites re-run | Total green |
|---|---:|---|---:|
| 11 | 12 | c10 + c9 + generic | 44/44 |
| 12 | 12 | c11 + c10 + c9 + generic | 56/56 |
| 13 | 12 | c12 + c11 + c10 + c9 + generic | 68/68 |

The auditor independently re-ran the newest cycle's suite and the generic invariant suite at each cycle under the mandated environment; all runs passed live. Regression suites for cycles ≥3 back were trusted based on worker output plus the anti-fabrication trust floor established across the arc.

## 4. Cycle-specific notes

The three cycles are structurally identical; the differences are cosmetic. The auditor's three cycle reports for this arc surface no critical or moderate findings and exactly one minor observation, on Cycle 12.

**Cycle 11.** Third consecutive heartbeat; anchor list grows to 136 (+10 from Cycle 10). Torch dry-run baseline chain extends to `vs c7+c8+c9+c10`.

**Cycle 12.** Fourth consecutive heartbeat; anchor list grows to 146 (+10). One minor auditor observation: the anchor-preservation diff sidecar this cycle used a filename variant. The finding was cosmetic (functionally correct; the JSON was pinned by an explicit path field in the verdict rather than by filename convention), and the Cycle 13 brief formally acknowledged the precedent, allowing either filename form going forward provided the actual path is pinned in the verdict.

**Cycle 13.** Fifth consecutive heartbeat; anchor list grows to 156 (+10). Cycle 13 explicitly exercised the Cycle 12 minor-fix precedent, landing the diff at `data/v3_spine/cycle13/anchor_preservation_c13.json` with its path pinned in the verdict. A cosmetic-only observation from the Cycle 13 audit: worker's declared `promise_check` baseline of 2768 pre-existing warnings was 2769 on the auditor's live re-run — a delta of +1 warning attributable to the cycle's own test file landing without full per-file adoption, consistent with the policy's honesty caveat, and unrelated to any content correctness of the emitted artifacts.

## 5. Cumulative state at end of arc

The M-V3-SPINE-1 milestone continues to be gated on operator ear per Fixed Decision 6. Nine `LANDS_pending_operator` verdicts now sit on disk covering Cycles 4–13, all byte-identical to their emission-time hashes. Both operator-facing A/B candidates remain unchanged: Method A at `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav` (SHA `cc919559b4508b6b…`) and Method B at `data/v3_spine/rc7_v2_v3_paths/rc7_v2_v3_paths_full_reconstruction.wav` (SHA `f40796be982998b0…`).

The three operator-facing decisions queued at the end of the Cycles 4–6 arc remain queued:

1. **Ear verdict on either A/B pair.** A positive verdict opens M-V3-FOCUS-1 (Chicken Grease anchor plus four SHA-256-tiebreak picks from `data/recreate_v2/focus_set_v2.json`).
2. **Approval to execute the torch-2.13 reproduction (Mode 2).** The drafted commands in both binary and module forms remain pinned byte-identically across Cycles 7 through 13.
3. **Canonicality choice between the two mix chains.**

Downstream milestones M-V3-FOCUS-1, M-V3-CORPUS-1, M-V3-RULES-1, M-V3-EAR-1, and M-V3-GEN-1 remain frozen.

Two properties of the heartbeat mode are now proven empirically. First, five consecutive heartbeats produce zero drift on any load-bearing anchor and zero fabrications on any spot-checked SHA (roughly seventy independent verifications across Cycles 5–13). Second, the heartbeat's growth profile is a stable +10 anchors per cycle, projecting to about 166 anchors at a hypothetical Cycle 14 heartbeat and continuing linearly thereafter. The cadence is deliberately quiet; it does not close the milestone and does not itself accumulate technical debt.

## 6. Conclusions

The arc from Cycle 11 to Cycle 13 is the campaign's proof that a steady-state operator-blocked mode can hold indefinitely without either drift or false progress. Every discipline invariant established during the substantive-track cycles — the three-way rubric integrity chain, the byte-identical venv manifest, the append-only verdict chain, the interpreter guard, the AST prohibition on network and PRNG imports, the anchor preservation snapshot, the generic verdict-walker test — remains automatically enforced by every heartbeat cycle at essentially zero engineering cost. The one observed minor variance across the arc — a cosmetic filename choice on the Cycle 12 anchor diff — cost nothing to acknowledge and was resolved cleanly by allowing either form provided the emitted verdict pins the actual path.

The unresolved work remains not code but operator judgment. Any single one of the three queued decisions — an ear verdict on either A/B pair, a Mode-2 green-light, or a canonicality preference — arriving in a subsequent cycle's `live_guidance` immediately breaks the glass and reopens substantive work. Until then the heartbeat cadence continues linearly, and the campaign's audit trail continues to accrete without regression.

## Appendix: Implementation Details

### A.1 Delivered artifacts by cycle

Cycle 11, under `data/v3/deliveries/31a164f845f8e27e/cycle11/verdict.json` (plus working artifacts at `data/v3_spine/cycle11/torch213_reproduce_probe_c11.json` and `anchor_preservation_{pre,post,}_c11.json`).

Cycle 12, under `data/v3/deliveries/31a164f845f8e27e/cycle12/verdict.json` (SHA `d6b67b232b1765b3…`) plus `data/v3_spine/cycle12/torch213_reproduce_probe_c12.json` and anchor snapshots.

Cycle 13, under `data/v3/deliveries/31a164f845f8e27e/cycle13/verdict.json` (SHA `0f0143e6591441bd…`) plus `data/v3_spine/cycle13/torch213_reproduce_probe_c13.json` (SHA `ea321953cb89910b…`), anchor snapshots, and a diff summary at SHA `6eaf9cb1f489d7bf…`.

Cycle-scoped reports on disk at `docs/v3_spine_report_cycle11.md`, `docs/v3_spine_report_cycle12.md`, `docs/v3_spine_report_cycle13.md`.

### A.2 Scripts and probe modules

Cycle 7 probe module (locked, seven-cycle byte-identity): `scripts/v3_spine/torch213_reproduce_probe.py`, SHA `b54adadd1f4f04028d4d931710cc02b722c82ebee027728a97adfa8b20c9af3d`.

Cycle 12 probe module (added to locked list): `scripts/v3_spine/torch213_reproduce_probe_c12.py`, SHA `71da91b3e4755e8ad881fa561884ce136aa61d6526bee2ba4fa5f98ef3e03bc1`.

Per-cycle callers: `scripts/v3_spine/torch213_reproduce_probe_c<N>.py`, `scripts/v3_spine/anchor_preservation_c<N>.py`, `scripts/v3_spine/verdict_c<N>.py` for each of N ∈ {11, 12, 13}. One-shot ledger emitters born under `tools/stale/cycle<N>_v3_spine_scratch/` per cycle.

Continued locked (byte-identical across the entire arc): `scripts/palette_render/render_stem.py = 214372d9…5b2b`; `scripts/v3_spine/mix_match_operator_section.py = 4f47fbcd…`; `scripts/v3_spine/rc7_v2_rerun_v3_paths.py = eaaa993e…`; `scripts/recreate_v2/rc7_v2_rerun.py = 7a5fbef0…`; `scripts/v3_spine/rc7_mix_balance.py`.

### A.3 Tests

New per cycle: `tests/test_v3_spine_c11.py`, `tests/test_v3_spine_c12.py`, `tests/test_v3_spine_c13.py` — twelve cases each. Continuing: `tests/test_verdict_sha_fields_resolve_on_disk.py` — eight generic-invariant cases walking the newest delivered verdict. Sanity-floor regression suites re-run at each cycle. All test runs green.

### A.4 Integrity chains

Three-way rubric-v2 chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` content == each cycle's `verdict.rubric_hash_v2`.

Cadence-policy chain: `docs/wait_on_operator_cadence_policy.md` SHA `0be540365c8c03ad38a15478fbad0fe32bf5ea4118e33ef3eeed62dbd9a0c7f2` == `data/v3_spine/wait_on_operator_cadence_policy_hash.txt` content.

Venv directory-manifest byte-identity across seven cycles (Cycles 7–13): `a86205175728…f83a74`.

Verdict backref chain (each cycle pins the previous): Cycle 12 pins Cycle 11's verdict SHA; Cycle 13 pins Cycle 12's `d6b67b232b1765b3…`; the auditor re-verifies the backref resolves on disk at each pass.

### A.5 Ledger event schedule

Each cycle emits exactly eight ledger events under a cycle-scoped `run_id = run-2026-09-02T<HH>0000Z` (HH = 15/16/17 for C11/C12/C13 respectively). Timestamps are `T<HH>:00:00Z` for the first seven events; `T<HH>:00:01Z` for the `_archive/cycle-<N>-scratch` row, reflecting its post-move placement per the Cycle 8 convention.

### A.6 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; single-threaded BLAS via `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`. All set via `os.environ.setdefault` in every top-level script.

### A.7 Anchor growth profile

The +10 per cycle profile from Cycle 10 onward corresponds to the ten heartbeat-cycle-specific artifacts that lock at cycle close: the cycle's verdict, its torch-probe JSON, three anchor-preservation JSONs (pre, post, diff), three driver scripts (torch caller, anchor driver, verdict emitter), its twelve-case test file, and its cycle-scoped report document. Substantive-cycle jumps (Cycles 7 +16, Cycle 8 +16, Cycle 9 +13) reflect additional specs and doc landings not present in heartbeat cycles.

### A.8 Auditor spot-check totals

Approximately seventy independent SHA spot-checks across Cycles 5–13 with zero fabrications detected. Nine consecutive audit cycles (5, 6, 7, 8, 9, 10, 11, 12, 13) have passed with `VALIDATED` decisions and zero critical or moderate findings. Cycle 13's audit spot-checked ten SHAs live, all matching worker claims.

### A.9 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 11 | 7ed5cb09-f77c-4178-8011-c6455b9cc696 | 8272caab-36f2-4391-8834-6cfd13de05a3 | b5893a21-759a-4e97-8235-4f20c638094b |
| 12 | 81099ea1-1b9a-4cbc-96ae-d88ddbf4915e | 7d47d59a-a762-42d5-95b0-cb21484e378e | 7dc0d5f8-3b65-484c-9d47-42b68f5f1e14 |
| 13 | af2cdab0-3617-4ce1-85a1-33310d279477 | 931c417e-8931-4e5e-94a4-6dc3086d8997 | f8025562-d6ea-4c5b-bb0c-0be496a03343 |
