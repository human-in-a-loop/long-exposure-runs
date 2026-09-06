---
created: 2026-09-06T00:00:00Z
cycle: 77
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V4-CLOSE-1/completion-report-v3-emitted-c77
supersedes_path: docs/v4_completion_report_v2.md
---

# Music-Gen v4 Closure — Completion Report v3 (c77)

Final closure report authored per c76 handoff. Supersedes
`docs/v4_completion_report_v2.md` (c29) via c14 str-supersede lemma;
v2 preserved byte-identical as historical anchor. **State at c77 close.**
All SHAs freshly disk-read at c77 open (zero drift vs c76 pins).

Report authorship (c77) is a bookkeeping cycle — no new sweeps, no new
renders, no touched READ-ONLY anchors. Every M-V4-* milestone is closed
below with an honest verdict.

---

## §1 Milestone Status Matrix

| Milestone | Verdict | Blocker (if any) |
|---|---|---|
| M-V4-CERT | **LANDS** | — E2E_DETERMINISM_HOLDS in `docs/v3_determinism_certificate.md` §2 (2026-09-03), env_pin `2ac444c3…922ca` unchanged. |
| M-V4-PROFILES | **LANDS_WITH_HONEST_GAPS** | CG bass/drums/guitar profiled (c9/c11/c14); WIG bass landed c28; Rome/PD/Disco A bass fine-fits deferred repeatedly (disk gate + operator strict-order); non-CG drums stage-1 deferred. All non-CG SF2 verdicts under c47 OPT1-extended (composite-relative winner, best-of-search). c15 non-CG guitar SF2 SKIPs auto-closed. Vocals htdemucs-hybrid campaign-wide per operator directive L59-60. |
| M-V4-SHOWCASE | **LANDS_pending_operator** | CG A/B `cg_ab_mix.wav` sha `6e13e007…f9484b` (c17); 4 non-CG v1 A/Bs (c69) + v2 A/Bs (c71). All 9 A/Bs REPLAY_PROOF_HOLDS byte-det ×2. Operator ear = LANDS authority post-hoc per FD-6. |
| M-V4-RULES | **LANDS** | v3 rules artifact `data/v3/rules/rules_artifact.jsonl` sha `e19fb205b282dabb…` (76 rules across 5 doctrine categories) from c23. v4 scaffold at c20 documented. VOMM CA-substitute serving as generator input (see M-V4-GEN). |
| M-V4-EAR | **HALT-HONEST** | c76 P1b formal proof: L119 mandate `band4_max < loo_min - 0.5` empirically infeasible under VGGish-only backbone (monotone-calibration lemma). CLAP backbone blocked on torchvision::nms; VGGish-only forced. Ear model builds (5/5 sanity PASS under c76 v2 wider-linear calibration) but cannot discriminate band-4 from band-7 at the required threshold. See §3. |
| M-V4-GEN | **HALT-HONEST_DELIVER_15** | 3 iterations completed (c72/c73/c74), each 5 songs × REPLAY_PROOF_HOLDS byte-det ×2 = 15 gen `ab_mix.wav` renders delivered. Batch-scoring blocked on M-V4-EAR (P1b infeasibility). Under FD-6, delegated to operator ear authority — 15 candidates handed off to operator. Stall counter 3/8; iter-04+ would not change the blocker. Interpolation-hybrid demo NOT authored (optional per campaign; c74+ has spec at `M-V4-GEN-1/interpolation-demo-spec` — a c78+ item if operator requests). |
| M-V4-CLOSE | **LANDS** | This report + OPERATOR_DECISIONS amendment (#19 c77) + POR c77 rows. Codebase guide byte-identical (no shape change). |

---

## §2 c30-c77 Amendments Summary

Consolidating everything after v2 report (which covered c22-c28).

- **c30 Track A**: coarse_sweep_sf2 15/15 legacy-mode byte-identical vs c1
  anchor; coarse_sweep_sf2_drums 8/8 vs c10; coarse_sweep_sf2_guitar 8/8
  vs c13. fine_fit_sf2_drums MIXED (render 216/216 byte-identical,
  composite 143/216 strict-equal + 73 FP-drift ~1e-6) → HALT + escalation.
- **c31**: fine_fit_sf2_v2 (216/109 pattern) + fine_fit_sf2_guitar
  (180/98 pattern) also HALT-escalated under same composite-FP-drift class.
- **c32**: consolidation memo M-V4-CERT-composite-fp-drift-adjudication-c32
  with 3 named paths (A accept render-level bar; B hold strict composite;
  C harden objective.py under READ-ONLY lift).
- **c47 OPERATOR OMNIBUS 2026-09-05**: PATH_A adopted; invariant (f)
  codified (legacy-mode regression bar = bit-identical audio output;
  composite tolerance |delta| ≤ 1e-5 with matching render SHAs). Cascade-
  closes 3 predecessor HALTs. METRIC-SEMANTICS closed (2026-09-04 distance
  ruling). SHOWCASE-1-non-cg-bass OPT1 EXTENDED campaign-wide.
  Preservation-spin BANNED. **6 escalation memos CLOSED**.
- **c48-c68**: preservation-cadence terminal contract per c36 auditor;
  disk-blocked sweeps deferred with concrete resume commands; WIG-piano-
  stage1 blocked_on_operator chain-continued 7×; long_exposure/ absent
  chain-preserved 12×. **All heartbeat/preservation-spin retired at c47**;
  cycles c48-c68 that continued preservation carry-forward operated under
  a superseded doctrine (retired by operator directive #4).
- **c69 OPERATOR PIVOT 2026-09-05**: 4 non-CG A/B mixes delivered via new
  `scripts/sound_match/deliver_ab_v4.py` sibling driver; bass+drums sf2
  replay + vocals htdemucs-hybrid + absent stems silent. All 4
  REPLAY_PROOF_HOLDS byte-det ×2. Retires WIG-piano-stage1 (absent-stem
  policy) + OP-2 Monitor (foreground renders don't need it) + PD stem-
  manifest attribution carry chains.
- **c70**: WIG duration diagnostic (HONEST_SPARSE_CANONICAL_MIDI: 4
  canonical MIDI durations pinned; 6 chains explicitly retired with str
  supersede per c14 lemma). M-V4-GEN-1 scaffold opened (Anticipation
  survey winner; VOMM secondary; 5-donor map).
- **c71 render-defect fix**: `deliver_ab_v4.py` extended with
  `_absent_stem_dispatch` (audibility-gated htdemucs stem substitution)
  + max-truncation policy. 4 v2 A/B mixes rendered with audible
  substitutions (WIG piano+other; Rome guitar; PD other; Disco A guitar+
  piano+other). All 4 REPLAY_PROOF_HOLDS byte-det ×2. c69 v1 anchors
  byte-identical pre==post as siblings.
- **c72 M-V4-GEN iteration 1**: Anticipation weights fetch failed (PyPI
  404 + git-clone dry-run resolves but weights ~200MB out of budget).
  VOMM(K=4) primary. 5/5 songs REPLAY_PROOF_HOLDS byte-det ×2. Stall 0/8
  → 1/8.
- **c73 iteration 2**: Anticipation formally abandoned via
  `_gen/anticipation-abandoned-weights-unfetchable`. VOMM seed=1 iteration
  landed 5/5 byte-det ×2 with SHAs distinct from iter-01. Stall 1/8 → 2/8.
  iter-01 manifest back-fill. M-V4-EAR-1 scaffold opened.
- **c74 iteration 3 + EAR-1 substantive impl**: VOMM seed=2 landed 5/5
  byte-det ×2 with SHAs distinct from iter-01+02 (15/15 distinct). Stall
  2/8 → 3/8. Molasses/Essence/Desire exemplar sha16 resolved from
  `corpus/ratings/7`. CLAP fetch FAILED (torchvision::nms) → VGGish-only
  fallback authorized. `scripts/ear/v4_ear.py` substantive impl landed;
  sanity gate PASS 5/5 (min=6.44 > 6); byte-det ×2 HOLDS.
- **c75 HALT-HONEST**: band-4 spot check FAIL (band4_max=7.0 > loo_min-0.5
  = 5.94 threshold). LOO self-include audit PASS. Calibration saturation
  probe characterized as `wide_span_ceiling_from_anchor_choice`; 3
  variants computed (all fail either sanity or discrimination). Exemplar
  band-metadata realignment: Essence + Desire raised 6→7 per filesystem
  authority (`corpus/ratings/7/`).
- **c76 formal infeasibility proof**: `scripts/ear/v4_ear_v2.py` sibling
  wider-linear calibration (`anchor_high = max(raw_max_ex + 0.02, 0.98)`)
  eliminates c74 ceiling saturation → LOO 5/5 in [6.21, 6.83]. Sanity
  PASS. But P1b sweep across 3 statistics × 3 calibrations (9 cells) shows
  every raw statistic has `band4_max_raw > exemplar_min_raw` (inverted
  sign). Monotone-calibration lemma: no `f: raw → [1,7]` satisfies both
  sanity gate AND L119 simultaneously. Band-4 v2 spot check FAILS honestly
  (b4_max=6.72 > loo_min-0.5=5.71). L119 empirically infeasible under
  VGGish-only backbone. **First-class negative finding**. Batch-scoring
  delegated to FD-6 operator ear authority.
- **c77 this cycle**: authorship-only. This report + OPERATOR_DECISIONS
  #19 amendment + POR rows + `_run/cycle_77_closed` rollup. No sweeps,
  no renders, no touched READ-ONLY anchors.

---

## §3 M-V4-EAR Gap: L119 Infeasibility Under VGGish-Only

`data/v4/ear/l119_infeasibility_proof_c76.json` records the formal
lemma. Under CLAP-blocked-torchvision reality, VGGish-only 128-D
embeddings do not resolve band-4 vs band-7 at the granularity the L119
mandate requires. Per-statistic table (raw values):

| Statistic | band4_max_raw | exemplar_min_raw | raw_sign | verdict |
|---|---|---|---|---|
| max_over_windows_c74 | 0.9413 | 0.8706 | INVERTED | infeasible |
| mean_of_per_ex_max | 0.8892 | 0.7836 | INVERTED | infeasible |
| mean_over_all_windows | 0.8169 | 0.6945 | INVERTED | infeasible |

Any monotone calibration `f: raw → [1,7]` preserves the ordering; if
`band4_max_raw > exemplar_min_raw` then `f(band4_max_raw) > f(exemplar_min_raw)`,
which forces `band4_max_score > loo_min_score`, contradicting the L119
mandate `band4_max < loo_min - 0.5`. Therefore no calibration exists.

**Resolution paths** (all requiring c78+ operator action or infra unblock):
1. **CLAP unblock**: fix torchvision::nms (numpy 2.x cascade or torch/
   torchvision version pin) → ensemble backbone → likely resolves.
2. **Alternative backbone**: swap VGGish for a higher-resolution
   embedding (MERT, MULE, HTS-AT); requires operator-approved model
   choice + env_pin re-issue per FD-16(a).
3. **Rubric revision**: operator declares L119 threshold advisory (not
   strict); ear model builds under wider calibration; passer-count trust
   comes from operator ear.

Under FD-6 (operator ear = LANDS authority post-hoc) + c47 OPT1 extension,
path 3 is the current de facto policy. All 15 gen `ab_mix.wav` renders +
9 focus-song A/Bs (5 v1 + 4 v2) sit `pending_operator` — 24 A/Bs total
awaiting ear verdict.

---

## §4 Deliverable Index

**Focus-song A/B mixes (9 files)**:
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` (c17 sha `6e13e007…f9484b`)
- `data/v4/deliveries/252eb21ce7df7328/ab_mix.wav` (c69 v1 sha `6feca5d1…`)
- `data/v4/deliveries/252eb21ce7df7328/ab_mix_v2.wav` (c71 v2 sha `29de5ee2…`)
- `data/v4/deliveries/51e433ade2a845e1/ab_mix.wav` (c69 v1 sha `81e2ef15…`)
- `data/v4/deliveries/51e433ade2a845e1/ab_mix_v2.wav` (c71 v2 sha `9ea1fe32…`)
- `data/v4/deliveries/88d247468cb6d49f/ab_mix.wav` (c69 v1 sha `a300cf4c…`)
- `data/v4/deliveries/88d247468cb6d49f/ab_mix_v2.wav` (c71 v2 sha `e164c42b…`)
- `data/v4/deliveries/cdd2717e52820ff6/ab_mix.wav` (c69 v1 sha `1b673106…`)
- `data/v4/deliveries/cdd2717e52820ff6/ab_mix_v2.wav` (c71 v2 sha `77cd593a…`)

**Gen batch (15 files, 3 iterations × 5 songs)** under
`data/v4/gen/iteration_{01,02,03}/gen_v4_song_{1..5}_donor_<sha16>/ab_mix.wav`.
Per-song mix SHAs pinned in each iteration's `iteration_rollup.json`.

**Pinned profiles** under `data/v4/profiles/<sha16>/{bass,drums,guitar}.json`
for each CG + WIG + Rome + PD + Disco A cell that landed (with
per-family replay proofs).

**Certificates & specs**: `docs/v3_determinism_certificate.md` §2
LANDS; `docs/specs/v4_sound_matching_layer_spec.md`; `docs/specs/v4_rules_and_ear_spec.md`.

**Test suites** (all green at c77 close): `tests/test_ear_v4_scaffold.py`
5/5, `tests/test_ear_batch_scoring_c75.py` 8/8, `tests/test_gen_iterate_v4.py`
7/7, `tests/test_deliver_ab_v4.py` 10/10, `tests/test_c30_legacy_mode_regression.py`
30/30, `tests/test_fine_fit_serial_lock_c32.py` 8/8, `tests/test_sweep_hygiene_c27.py`
18/18.

---

## §5 env_pin & Discipline

- `env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
  (7-key canonical subset). Held byte-identical c22 → c77 = 56 cycles.
  FD-16(a) cert re-issue trigger never fired.
- FD-1 halt-honest: c75 band-4 fail + c76 L119 infeasibility both landed
  as first-class negative findings, not gamed metrics.
- FD-6 operator ear authority: 24 A/Bs stand `pending_operator`.
- FD-16(c) replay-proof scoping: one proof per RENDER FAMILY per SONG,
  not per profile. All families proven.
- c14 str-supersede lemma respected throughout (never list form).
- c47 preservation-spin BAN honored from c69 onward. (c48-c68 cycles
  operated under superseded preservation doctrine; retired by c47.)
- No wait-on-operator memos emitted since c47 (BANNED per operator
  directive 2026-09-03 part 2).
- No PRNG, no `sidecar_nonfactor` imports, no VST3 state APIs in any v4
  code path (AST-verified).

---

## §6 Gaps (honest)

1. **Ear-model batch scoring unavailable**: 15 gen renders + 4 non-CG v1
   + 4 v2 focus A/Bs = 23 A/Bs cannot be auto-scored. FD-6 delegation
   active.
2. **Non-CG bass fine-fits deferred**: Rome/PD/Disco A bass stage-2
   sweeps never launched (disk-blocked + operator strict-order). Under
   c47 OPT1 extension, this doesn't block SHOWCASE — c69/c71 A/B mixes
   consume best-available profiles.
3. **Non-CG drums stage-1 deferred**: WIG + Disco A drums coarse sweep
   never launched (strict-order gating). c14/c15/c17 CG-drums OPT3
   (htdemucs stem substitution) pattern applied campaign-wide by default.
4. **Interpolation-hybrid demo NOT authored**: optional per campaign;
   spec at `data/v4/gen/interpolation_demo_spec.json` (c70). c78+ item
   if operator requests.
5. **CLAP backbone blocked**: torchvision::nms failure prevents CLAP
   ensemble; VGGish-only forced. Resolution requires operator-approved
   torch/torchvision pin change + env_pin re-issue.

---

## §7 Clean-Close Rationale

Every remaining item is either (a) blocked on operator authority that
never idled the run (FD-6 delegation active on 24 A/Bs), (b) blocked on
infra unblock that requires operator env_pin adjudication, or (c)
optional per campaign. The stall rule fires at 8 iterations without 5
passers; we have 3 iterations without ear-scoring, and additional
iterations would not resolve the ear blocker. Continuing to iterate
under the same blocker is itself a preservation-spin pattern which
operator directive 2026-09-03 part 2 BANNED.

Per campaign L145-147: "STOP iterating — deliver the best 5 by ear score
with an honest gap analysis and proceed to close. Do not wait for
operator input to close." We have delivered all 15 candidates + 9 focus
A/Bs; the ear model gap is documented; the report closes cleanly.

**M-V4-CLOSE-1 LANDS at c77.** Run ends here per campaign L151-152:
"declare the topic complete and stop cleanly. The operator verifies
everything after close."
