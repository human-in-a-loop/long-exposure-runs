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

---

## Section: c78 Interpolation-hybrid demo (optional post-close deliverable)

Appended v3.1 amendment per c78 research brief. This section is **additive**:
the c77 clean-close verdicts above (v3 §1-§7) stand unchanged; the 76-rule
artifact and the 24 pending_operator A/Bs are unchanged; the six binding-spec
lands (CERT, PROFILES, SHOWCASE, RULES, EAR, GEN, CLOSE) hold.

### Deliverable

The M-V4-GEN-1 interpolation-hybrid demo (originally deferred from c74 P6
through c75/c76/c77) lands as a **single additional optional artifact**
alongside the 15 iter-01/02/03 gen renders. It does NOT re-open the campaign.

Path: `data/v4/gen/interpolation_demo/interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/`

| Artifact                 | SHA-256                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| `ab_mix.wav`             | `b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a`        |
| `ab_mix.manifest.json`   | `10b298c387a67de8ef78c362bac5849a8f72e7226d2d9e3d8ec1c92fa8c82689`        |
| `ab_mix.replay_proof.json` | `ac85dbe915218da56b5b1476ce31de65fc0f6d861cdb32e936d8a77dff89c99c`       |
| `scripts/gen/interpolate_v4.py` | `2359f35d2355647d7b4a692d9b0d303e8bf040671d4ab28cadfa25a0277f6653`   |

REPLAY_PROOF_HOLDS byte-deterministic ×2 in fresh `tempfile.mkdtemp()`
under 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
(unchanged c22→c78 = 57 cycles).

### Interpolation semantics (pre-registered in c78 brief §P1)

VOMM samples 24 rules for donor A (CG, sha16 `31a164f845f8e27e`) under seed
string `interp_demo|donor=31a164f845f8e27e|seed=0`, then 24 rules for donor
B (Peach Dream, sha16 `88d247468cb6d49f`) under `interp_demo|donor=88d247468cb6d49f|seed=0`.

Rules are corpus-selected instances (content-hashed `rule_id`), not
parameter-tunable per position. Arithmetic mean on rule-parameter vectors
would fabricate new rules absent from the corpus, violating FD-1 (no
fabrication). Per the pre-registered fallback (c78 brief §P1 step 2), the
driver falls back to per-position SHA-256 tiebreak at threshold t=0.5:

    r = int.from_bytes(sha256(f'{donor_a}|{donor_b}|pos{i:03d}|seed{seed}').digest()[:8], 'big') / (1<<64)
    pick rules_A[i] if r < (1 - t) else rules_B[i]

At t=0.5 the observed mix on this run is: **6 positions from donor A only,
10 positions from donor B only, 8 positions from rules present in both
donor pools (ambiguous)** — total 24. All picked `rule_id`s are subset of
`union(rules_A, rules_B)`; test_02 asserts this by grep as an anti-
fabrication guard.

### Rendering pipeline

Same VOMM→canonical MIDI→SF2 replay pipeline as iter-01/02/03. Donor A (CG)
supplies the bass profile at `data/v4/profiles/31a164f845f8e27e/bass_v2.json`
(sha `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462`).
Drums use the c14 OPT3 GM Standard Kit shim (CG lacks pinned drums profile).
Sum via float accumulate + 0.99 peak-limit + max-length zero-pad per c71
policy. No PRNG, no sidecar_nonfactor, no VST3 state APIs (AST-verified in
test_03).

### Anchor preservation

All 23 v4 audio anchors + 6 c77 anchors + rules artifact + SF2 verified
byte-identical pre==post via `sha256sum`:

- `docs/v4_completion_report_v3.md` pre-append sha `d920c93328930556…`
  (this v3.1 amendment is an additive append below the horizontal rule
  above; header 8-KB region unchanged)
- `docs/OPERATOR_DECISIONS.md` sha `b563caee0f81db96…`
- `scripts/ear/v4_ear.py` sha `e775621bff1c9560…`
- `data/v4/ear/exemplar_set.json` sha `31c10dfb80355181…`
- `data/v3/rules/rules_artifact.jsonl` sha `e19fb205b282dabb…`
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` sha `6e13e0075c5d8116…`
- 8 focus A/B mixes (v1+v2 for WIG/Rome/PD/Disco A) — SHAs unchanged
- 15 gen renders (iter-01/02/03 × 5 songs) — 15/15 anchors byte-identical
  under `test_05_c72_c73_c74_iteration_anchors_byte_identical`
- Peach Dream `stem_manifest.json` sha `d483f2bf0b09389b…` (P0 Branch C
  canonical, 20th-cycle stable per invariant (d))

### Test suite

`tests/test_gen_interpolate_v4.py` lands with 6 named cases per c78
brief §P3:

1. **test_01** — interpolation deterministic under identical (donor, t, seed)
   via fresh subprocess into fresh tempdir. PASS.
2. **test_02** — at t=0.5, sampled mix contains rules only-in-A and
   only-in-B; anti-fabrication guard (mix rule_ids ⊆ union(A, B)). PASS.
3. **test_03** — AST scan of `scripts/gen/interpolate_v4.py`: no PRNG, no
   sidecar_nonfactor, no VST3 state APIs. PASS.
4. **test_04** — env_pin_sha256 in manifest matches campaign anchor. PASS.
5. **test_05** — regression pin on 15 iter-01/02/03 A/B SHAs byte-identical.
   PASS.
6. **test_06** — on-disk replay_proof.json is HOLDS + shape valid + SHA
   matches anchor. PASS.

**6/6 PASS** via `PYTHONPATH=. /usr/bin/python3 tests/test_gen_interpolate_v4.py`.
Regression: 9/9 c76 v2 calibration + 8/8 c75 batch scoring + 5/5 c74 ear
scaffold + 7/7 c72-c74 gen iterate = 29/29 pre-c78 tests still green.
Cross-cycle total: **35/35** green.

### Verdict

**INTERPOLATION_DEMO_DELIVERED_pending_operator**. Per FD-6, operator ear on
the demo audio is the only LANDS authority; the automated gate produces the
byte-deterministic delivery + replay proof, not an ear verdict. This
augments the c77 close with one additional `pending_operator` A/B (24 → 25
delivered candidates awaiting operator ear); the campaign remains cleanly
closed at all seven M-V4-* verdicts. Ledger cross-link:
`M-V4-GEN-1/interpolation-demo-delivered-c78`.

### What this demo demonstrates

The generator produces a novel rule sequence `r_mix = f(rules_A, rules_B,
t=0.5)` distinct from both `rules_A` and `rules_B`: 8 positions carry rules
present in both donor pools (ambiguous), 6 draw exclusively from A, and 10
draw exclusively from B. The rendered mix is neither `iter-01/song_1`
(CG-only donor) nor a Peach Dream render — it is a per-position hybrid at
t=0.5 that lands byte-deterministically through the same pipeline the 15
accepted iter renders use. The mechanism claim in the c78 brief holds under
the SHA-tiebreak fallback: **the rule-set representation is composable at
position granularity**, even though the corpus-content constraint blocks
arithmetic-mean-on-parameters composition.


---

## Section: v5 REOPENING (c79–c90) — feature backlog F1–F7 close

*Appended additively at c90 (= harness c134, offset 44) under `M-V5-CLOSE-1/completion-report-v5-section-c90`; v3 §1–§7 and the c78
section above are byte-identical (prefix byte-equality asserted by `tests/test_c90_close.py`). Every number below was read from disk
at c90; where a brief and disk disagreed, disk governs (one line each in the c90 work output). Nothing was rendered, retuned or
re-verdicted this cycle.*

### Cycle counter and outage

On-disk cycles c79–c90 correspond to harness cycles c123–c134 (offset 44, disclosed every cycle, never reconciled). Harness
cycles c100–c127 were lost to an outage (rate limit + researcher context overflow; engine dead 2026-09-07 03:32Z → 2026-09-09
20:40Z); the ledger carries the single line `_infra/c100-c127-lost-to-outage`. Last real work before the outage was on-disk
c82/c83; execution resumed at c84 (= harness c128).

### M-V5-CORPUS-1 — CORPUS_LANDED_TEMPO_AXIS_STOPPED

- Corpus: 26 songs enumerated in `data/v5/corpus/corpus_manifest.json` (`733621366c023e3800d753d44eebb15cf091fc72353b1ead29ab26600c2e4bfb`) —
  13 band-6 + 10 band-7 + 3 band-5 focus (the operator's "~7" was a receipt under-count; nothing truncated).
  26/26 transcribed full-length through the checkpointed driver (per-song `transcription_manifest.json`) and 26/26 reindexed
  lossless with `canonical_v5_reindexed_sha256.json` sidecars.
- The c80 index-collision defect: the READ-ONLY c22 chunk merger re-offsets times but never re-numbers `index`, and the READ-ONLY
  c4 serializer keys starts by `index`, so c79's full-length `canonical_midi_full/*.mid` silently dropped most notes (WIG other
  1799 JSON starts → 395 MIDI note_on). Fix: `scripts/v5/reindex_canonical_v5.py` (`08e94008a79ce2c05e1c370d0ccc0aa09062270bd61b93bc63b087c297b18115`)
  re-pairs starts/ends deterministically and re-serializes into `canonical_v5_reindexed/`; `scripts/v5/reindex_hook.py`
  (`a63434a60cc12b83a9c704a296dd2a8468941242676c01b76d5a12cb69941ad2`) makes every later landing lossless at birth; `harmony_v5.py` refuses the lossy dir.
- Content gate (c84, pre-registered): 1 song blocked — `ae1b65eaf1560951` (Shaolin Monk Motherfunk Nai Palm Commentary,
  NON_MUSIC_CONTENT_R1_AND_R2); `data/v5/corpus/content_blocked.json` `fc07a13891e1b6b1b35fa338a56f5e58515e6a8dbc4bc2ded53db5e72ee3af6a`.
- Tempo axis STOPPED. Four pre-registered criteria, four frozen-enum falsifications, none retuned (FD-1):
  v5 flat-band autocorrelation → `RULES_OUT_CRITERION_TOO_PERMISSIVE` (PD / Disco A 3:2 regression);
  v5b harmonic sum → `RULES_OUT_HARMONIC_SUM` (Rome regressed to 103.36);
  v5c autocorr-direct → `RULES_OUT_AUTOCORR_DIRECT` (4/5 anchors; Disco A missed by 0.006);
  v5d refined lag → `RULES_OUT_REFINED_LAG` (4/5 anchors; Rome 76.9 vs 152.0). The c82 mechanism probe
  (`data/v5/corpus/tempo_mechanism_c82_verdict.json`, `a21e325da3310a2adc829a1bd187854860f80fa35ff5b22ca4cb2fea22f3ddaa`) landed
  `MECHANISM_PARTIAL` (integer-lag quantization confirmed as the Disco A mechanism; Rome ±1 BPM missed). The c85 F4 adjudication
  (`bec3631aafbbcb401789c2a061396e97c03da6c4a935d4f5f45d35c61d284cb0`) read `F4_HALF_DOUBLE_AMBIGUOUS`; the operator
  addendum of 2026-09-09 overruled it (guidance sha16 `8677bb0cd3f240a0`):
  Peach Dream **122.197271** / Disco A **120.272335** BPM adopted (F4 CLOSED c86).
  `data/v5/corpus/recanonicalization_blocked.json` was amended in place: live file `eb78cfc0ce57dc9f50c68e2c683378cd0fe32a6feb4ab55276002ce64e6aa972`,
  the prior blocked file preserved as the stale copy `data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json`
  `2fbabc07849dbe238545b9e629f91cd81746c6216e5db3027e88f4e9313f8a8e`; `canonical_v5c_reindexed/` exists for both songs at the adopted BPM.

### M-V5-RULES-1 — RULES_LANDED_WITH_HONEST_GAPS

| Model | File | SHA-256 | Recorded verdict (never retuned) |
|---|---|---|---|
| harmony n=23 Markov chain (ROOT+QUALITY functional states) | `data/v5/rules/harmony_markov_v5_full_c86.json` | `330b9d46f715d2a6851221aa02b1bd49889cd039a6256a70c2af71448c7a785a` | `NON_DEGENERATE` — 81 states, max stationary `0:maj` 0.069317 |
| groove v2 n=23 (kick8 / snare16\|kick8 / hat16\|kick8,snare16 / bass16\|kick8) | `data/v5/rules/groove_v5_v2_full_c86.json` | `570720255a6eed6d99e10f24f1249bb0a8c3a2e525504608f17e1c6f3b2caaf6` | `GROOVE_V2_OVERFITS` — singleton-context fraction 0.637448; the hat\|kick8,snare16 granularity, not n |
| comping statistics (guitar / piano / other) | `data/v5/rules/comping_v5.json` | `010242548c5dc540ae8b0fa0c50e72b54b153b2b78168c2447f4626126376c62` | `COMPING_NON_DEGENERATE` — pooled 16th-slot histogram STRUCTURELESS (pooled max slot mass 0.065174 vs the 0.5 degeneracy line; per-stem slot masses 0.0530–0.0726); the IOI histogram is the structured axis (47.5% at one 16th) |
| form plan | `data/v5/rules/form_plan_v5.json` | `d6c14f9a7b921cffe0311561d1e2f1272a7304924ba2c8184272d2ada35f3682` | R1 FAILED at 0.85 (`pass` False: CG `ABBBBBBBBBBBB`, Rome `AAAAAAAAAAAAAAAAA`, WIG `ABCDEFGDH`) → the fixed template `AABABCAA` governs labels; length draws from the corpus |
| velocity profiles (Route 1 stem audio) | `data/v5/rules/velocity_profiles_v5.json` | `6b2fc502f065d0ca961c907e93a3c02f80618a1afc34015b4057dd513cb314a8` | R2 structureless — drums slot std 2.506 (< 5); backbeat−odd -1.894 |
| bass pitch model | `data/v5/rules/bass_pitch_v5.json` | `96d34b3bb8fc8b280fdd8ad8ff7b7fb38fdcbac37c94f8b624901096a0e4809c` | root-on-downbeat corpus 0.336 vs sampled 0.29 (pass); 6426 onsets on null-chord beats skipped |
| melody VOMM (order ≤ 3) | `data/v5/rules/melody_vomm_v5.json` | `48157c6f04eab5b1f661f47a843aa60e75d2298019a8a4bdee42a4e287b1e9fa` | `MEMORIZES` — order-3 singleton fraction 0.720574 |

Pre-registrations that gate these files: `data/v5/rules/harmony_prereg_c86.json` `b32cf3977c2319a38e1c525d3a28bf650eb5ee8cf7816b28a73ee92f06a02b18`,
`data/v5/rules/groove_prereg_c86.json` `995acc5bf4f33e363c2380173bb58a3806635d661618a3bbe93098cae0f58a4b`, `data/v5/rules/comping_prereg_c87.json`
`0deb5f24afb36ce4ce4db28d30adb24ef7328ff53e728b7edc68392bec7316f9`, `data/v5/gen/form_prereg_c85.json` `e71eda9b7c44137c94144d0a2f63431cbfb3b6910d692c72a844cde844a37da9`,
`data/v5/gen/f2_prereg_c86.json` `2e17ea57ca32398bf789586cbe9d175c6216e8553c1cea487e99f0fed8c3ac5d`. Every "recorded, not retuned" stays that way.

### M-V5-EAR-1 — EAR_RESTORED_INFORMATIONAL_ONLY

- Isolated venv `workspace/ear_venv` built at c82 from the pinned c79 command (receipt `data/v5/ear/env_pin_ear_venv_c82.json`) and
  amended with librosa (`EAR_VENV_AMENDED`; freeze sha `2228bfcf96d89a65…` → `40243a564ad69d5c…`;
  main-env freeze unchanged True); amended receipt `data/v5/ear/env_pin_ear_venv_c82_amended.json`
  `f31922c8a3fa4d36da744d55b8d851f5277b4c07c0180c1f97d794c0497df47d`.
- c76 v2 wider-linear LOO gate on FRESH embeddings (`data/v5/ear/ear_gate_v5_c82.json` `c3ead2120dcfdbb8b764a28b38877c025265e7785fe537552409d0318950dba6`):
  5/5 ≥ 6, min 6.2095 (Desire), max 6.8313 (Essence); gate passes.
- Band-4 spot check FAILS under v2 (`data/v4/ear/band4_spot_check_v2_c76.json` `d8fcea2a5409410ebe0d5fb427f79f100aca090f17ec68320bcb08af743b30a7`;
  fresh re-run at c82: aguanile 5.7042, stay_live 6.7199, wagon_wheel 6.1876):
  band4_max 6.7199 > loo_min − 0.5 = 5.7095. The c76 L119 monotone-infeasibility proof
  (`data/v4/ear/l119_infeasibility_proof_c76.json` `ada44349277b17e0b2043c419403b2eed5f99046972aa31f94708f411b15a68a`) stands: no monotone calibration
  of the VGGish statistic satisfies both the sanity gate and L119.
- Consequence, stated plainly: **ear scores are informational only (FD-6, c76 L119) and never a passer gate; an informational
  score ≥ 6 on a generated song lies inside the band-4 context range 5.70–6.72 and is not evidence that the song passes.**

### M-V5-GEN-1 — FEATURES_F1_F5_LANDED_HONEST_BEST_OF_AT_STALL_5_OF_12

Feature verdicts are the LANDING-cycle enum values; later iteration outcomes are reported as data, not re-verdicts.

| Feature | Verdict (landing cycle) | Cycle | Iteration | Seed | Rollup SHA-256 | Notes |
|---|---|---|---|---|---|---|
| F1 length + form + arrangement | `FORM_PLAN_PARTIAL` (4/5) | c85 | 2 | 1 | `3b0a36fe59a8d7b8bdeceb0dac3150e8fcd4548a3be76284f088d4b5c84019c8` | song 4 drew 4 sections (32 bars, 65 s); iterations 3–5 recorded `FORM_PLAN_LANDS` 5/5 on their own draws (data) |
| F2 bass + melody + dynamics | `F2_PARTIAL` | c86/c87 | 3 | 2 | `2777917a3b785805e47a9fd796f0ee36be45dafd202810b84fcea6fbc3f66e4b` | velocities 5/5, replay 5/5, RMS-variance ≥ 1.5 0/5 (drums < 1.0 every song); no retune |
| F3 guitar / piano / other | `F3_LANDS` (5/5 per-song, F3-off reproduces iteration 3 5/5) | c88 | 4 | 3 | `47efe6dd1a562c6f2bf1c024ed4fc399c67fe3f86661fc70a85a9af4fd72b289` | parts ≥ 32 note_on + audible + replay on every song |
| F4 tempo fix PD / Disco A | `F4_HALF_DOUBLE_AMBIGUOUS` (c85) → CLOSED by operator addendum | c85 → c86 | — | — | — | PD 122.197271 / Disco A 120.272335 adopted; n=23 chain consumed from iteration 4 |
| F5 interpolation demo CG ↔ PD, t = 0.5 | `F5_LANDS` | c89 | 5 | 4 | `4787a346af5aef34bddccd09914b41445dedfcfe4ef2c8ba7659eb4aa1d86cec` | demo `947b348a10ab8c5c…`, byte-det ×2 in-process + independent process, flag-off 5/5, raw-render clauses (i)(ii)(iii) all True |
| F6 iteration schedule | landed | c85 | 2–5 | — | — | every `stall_counter.json` history entry since iteration 2 carries feature / donor_map / form / rules SHAs / seed |
| F7 close docs | this section | c90 | — | — | — | OPERATOR_DECISIONS #21 + codebase-guide v5 section appended the same cycle |

Iteration-1 rollup (pre-F1, c84): `958c78b5ab5c291b5dcf24fc7916315fdad9d9273d298badf3d5f8458b3939e4`. Stall counter `data/v5/gen/stall_counter.json` `4b87958fd14c2364f2e10088baffa5fa58ef0f1f76237648932b054dbd585e69`:
**5/12**, passers **0** — by FD-6 design, no passer is declared from an informational score. The operator's rule
(guidance 2026-09-09, sha16 `cf7296cfcf70c277`): the ear ≥ 6 count is NOT the progress gate; feature landings are.
A sixth iteration is not opened (preservation-spin under c47 part 4).

Renders (every `ab_mix.wav` REPLAY_PROOF_HOLDS ×2 in a fresh tempdir; the iteration-5 six also equal from an independent second process):

| Iter | Song | Donor | Seed | Form | Duration s | ab_mix SHA | Replay |
|---|---|---|---|---|---|---|---|
| 1 | `gen_v5_song_1` | Chicken Grease (CG) | 0 | (16-bar A A B A, pre-F1) | 44.1629 | `f4cdb2947227a6cb…` | REPLAY_PROOF_HOLDS |
| 1 | `gen_v5_song_2` | What If I Go (WIG) | 0 | (16-bar A A B A, pre-F1) | 41.2038 | `953dbffc886359bb…` | REPLAY_PROOF_HOLDS |
| 1 | `gen_v5_song_3` | Rome | 0 | (16-bar A A B A, pre-F1) | 28.1295 | `0a95411b2d20d177…` | REPLAY_PROOF_HOLDS |
| 1 | `gen_v5_song_4` | Peach Dream (PD) | 0 | (16-bar A A B A, pre-F1) | 34.113 | `2f21412805edc127…` | REPLAY_PROOF_HOLDS |
| 1 | `gen_v5_song_5` | Disco A | 0 | (16-bar A A B A, pre-F1) | 34.8067 | `aa1da38f94b09eea…` | REPLAY_PROOF_HOLDS |
| 2 | `gen_v5_song_1` | Chicken Grease (CG) | 1 | AABABCAA | 168.5769 | `240b893ab0afde36…` | REPLAY_PROOF_HOLDS |
| 2 | `gen_v5_song_2` | What If I Go (WIG) | 1 | AABABCAA | 156.7739 | `9b1812c09d257f9d…` | REPLAY_PROOF_HOLDS |
| 2 | `gen_v5_song_3` | Rome | 1 | AABABCAA | 103.2388 | `ac01eb926aaeadfd…` | REPLAY_PROOF_HOLDS |
| 2 | `gen_v5_song_4` | Peach Dream (PD) | 1 | AABA | 65.3192 | `940227fb120e2bf0…` | REPLAY_PROOF_HOLDS |
| 2 | `gen_v5_song_5` | Disco A | 1 | AABABCAA | 130.0071 | `330916d5ecabe49b…` | REPLAY_PROOF_HOLDS |
| 3 | `gen_v5_song_1` | Chicken Grease (CG) | 2 | AABABCAA | 168.6451 | `b6a83535cbc1c835…` | REPLAY_PROOF_HOLDS |
| 3 | `gen_v5_song_2` | What If I Go (WIG) | 2 | AABABCAA | 156.7739 | `c247fe0772e841cb…` | REPLAY_PROOF_HOLDS |
| 3 | `gen_v5_song_3` | Rome | 2 | AABABCAA | 103.204 | `085ded8dfd9d4532…` | REPLAY_PROOF_HOLDS |
| 3 | `gen_v5_song_4` | Peach Dream (PD) | 2 | AABABCAA | 127.8346 | `7c0d1b18864f715a…` | REPLAY_PROOF_HOLDS |
| 3 | `gen_v5_song_5` | Disco A | 2 | AABABCAA | 130.0071 | `2fce495969a067e1…` | REPLAY_PROOF_HOLDS |
| 4 | `gen_v5_song_1` | Chicken Grease (CG) | 3 | AABABCAA | 172.4096 | `a501df3ccbe9d8d6…` | REPLAY_PROOF_HOLDS |
| 4 | `gen_v5_song_2` | What If I Go (WIG) | 3 | AABABCAA | 160.0639 | `fe36692611462cfc…` | REPLAY_PROOF_HOLDS |
| 4 | `gen_v5_song_3` | Rome | 3 | AABABCAA | 106.5419 | `19b0f51d3a53639f…` | REPLAY_PROOF_HOLDS |
| 4 | `gen_v5_song_4` | Peach Dream (PD) | 3 | AABABCAA | 130.5527 | `99e3ee69583651f7…` | REPLAY_PROOF_HOLDS |
| 4 | `gen_v5_song_5` | Disco A | 3 | AABABCAA | 132.3639 | `313b98bd7d68ae8a…` | REPLAY_PROOF_HOLDS |
| 5 | `gen_v5_song_1` | Chicken Grease (CG) | 4 | AABABCAA | 173.7099 | `eae40e284e09c6d2…` | REPLAY_PROOF_HOLDS |
| 5 | `gen_v5_song_2` | What If I Go (WIG) | 4 | AABABCAA | 159.6111 | `c9b65ce997b0dbf9…` | REPLAY_PROOF_HOLDS |
| 5 | `gen_v5_song_3` | Rome | 4 | AABABCAA | 106.06 | `9d91390a8bb601a5…` | REPLAY_PROOF_HOLDS |
| 5 | `gen_v5_song_4` | Peach Dream (PD) | 4 | AABABCAA | 130.5527 | `28e18c110f98bf60…` | REPLAY_PROOF_HOLDS |
| 5 | `gen_v5_song_5` | Disco A | 4 | AABABCAA | 132.6498 | `45f10a8ab2b53b2f…` | REPLAY_PROOF_HOLDS |
| 5 | `gen_v5_interp_CG_PD_t050` | Chicken Grease (CG) | 4 | AABABCAA | 171.4808 | `947b348a10ab8c5c…` | REPLAY_PROOF_HOLDS |

Informational ear scores (c76 v2 wider-linear via the isolated venv; FD-6): iteration 1 ≥ 6 on 4/5 (6.242, 6.293, 5.823, 6.377, 6.28); 2 ≥ 6 on 5/5 (6.318, 6.239, 6.105, 6.37, 6.406); 3 ≥ 6 on 4/5 (6.347, 6.253, 5.926, 6.365, 6.41);
4 ≥ 6 on 5/5 (6.453, 6.417, 6.227, 6.516, 6.533); 5 ≥ 6 on 6/6 (6.409, 6.462, 6.42, 6.219, 6.562, 6.497) — every value inside the band-4 context range 5.70–6.72.
Listening copies: 26 renders under `data/v4/generated/v5_iter_01..05/` (5+5+5+5+6, each with a SHA-verified `listening_manifest.json`) plus the
demo delivery `data/v4/generated/f5_interp_CG_PD_t050_c89/` (`delivery_manifest.json` `7cddb63a16a850272262d03f8dba5f0b846ba0c57ca5912b3829a71184bc8402`),
all pending operator ear.

### F5 caveat (verbatim from the c89 audit; carried forward)

The groove half of the F5 blend is a **union-vocabulary mixture**, not a mixture over shared contexts. Each of the four groove
tables has exactly 1 context seen in both donors (the `kick_marginal` "*" context); the three conditional tables have
55/14 (snare|kick8), 73/29 (hat16|kick8,snare16), 55/14 (bass16|kick8) A-only/B-only contexts and 0 shared.
Under the pre-declared `row_for` convention every conditional row is 0.5 × donor row + 0.5 × uniform over the other donor's vocabulary.
The harmony blend is a true mixture on 53/81 states (A 41, B 27), n=23 backoff on 12 (A) / 26 (B),
28 both-unseen uniform states. Decoding stayed SHA-256 inverse-CDF (prereg-declared deviation from the brief's argmax, which collapses a chain
to a cycle). **Any future t-sweep or second donor pair must pre-declare shared-context conditioning (coarser contexts) or the c78
per-position SHA-256 fallback** before rendering.

### Carry-forward hygiene (c89 audit MINORs, folded in)

- `blend_record_sha256` (`0bc6f353f82cbb88f2afe270641731583806af63ae4425fc317487ae41fad790`) is the SHA-256 of the **compact canonical JSON of the blend record**, not of the
  on-disk `f5_blend.json` bytes (`72d9cdcd4790a6c06e868397a09ec793d273a07cd19956ffa0c4d8823de55d1e`, indent=2); the delivery manifest carries the file-byte SHA.
- The blended chain's `degeneracy_verdict` = `NON_DEGENERATE` is **inherited** from the n=23 chain with a `not re-verdicted` note; it was not re-measured.
- Demo bass / drums normalisation gains hit the 4.0 cap (gains bass 4.0, drums 4.0; raw -31.86 / -30.912 dBFS vs the −18 dBFS target),
  leaving those stems ~1–2 dB under target; no pre-registered clause governs this and none was added post hoc.

### Program coverage and density

14/15 (song, F3-part) cells render through GM shims (guitar 27, piano 0, other 89); only CG guitar has a pinned profile
(`data/v4/profiles/31a164f845f8e27e/guitar.json`, prog 28, c14 `SF2_RULED_OUT` family verdict — timbre weakness, FD-6 governs). Bass/drums use the
donors' pinned v4 profiles on 4/5 songs (CG drums = the c14 OPT3 htdemucs decision → GM Standard Kit shim); keys / melody are GM shims on every song.
Generated F3 parts are dense (demo guitar 2160 / piano 1644 / other 2514 note_on over 64 bars); not retuned per FD-1.

### Determinism receipts

- `env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` unchanged from c22 to c90 (69 on-disk cycles, counted
  inclusively as in the c78 section); FD-16(a) (certificate re-issue on env_pin change) never fired.
- Every iteration byte-deterministic ×2 in fresh tempdirs (`byte_determinism_c85/c86/c88/c89.json`); FD-16(c) one replay proof per new code path
  (F1 c85, F2 c87, F3 c88, F5 c89 — plus the independent-process check at c89); flag-off regressions reproduce the previous iteration under every post-edit
  generator image (c85 → iteration 1, c87 → iterations 1+2, c88 → iteration 3, c89 → iteration 4).
- Generator lineage `scripts/v5/generate_v5.py`: `3fbd98ca…` (c84) → `b3473fd2…` (c85) → `f261690c…` (c87) → `3d0f3a24…` (c88) → `94c8ba99eac98eee1f88d871cfc520507ddf253d3962287f50a7a368fdaaa055` (c89, current; no edit at c90).

### Validators (P3) and the WARN series

| Cycle | promise_check ERROR | promise_check WARN | org_check |
|---|---|---|---|
| c85 | 156 | 8543 | — |
| c86 | 156 | not recorded | — |
| c87 | 156 | not recorded | — |
| c88 | 156 | 8707 | 0 / 54 |
| c89 | 156 | 8960 | 0 / 54 |
| c90 open | 156 | 8960 | 0 / 54 |
| c90 after the adopt event | 156 | 8731 | 0 / 54 |

The growth class is `orphan artifact in managed path` (7076 of the 8960 WARNs at open; data/v5/gen 725,
data/v4/generated 112); zero WARNs sit on c89 ledger lines themselves. Decision: the fail-closed emitter carries ≥ 250 paths, so
`_infra/adopt-cycle89-gen-artifacts-c90` (280 paths: `data/v5/gen/iteration_05/**`, the demo delivery, the iteration-5 listening copies) was
emitted and the counts re-measured (Δ -229). The ERROR baseline of 156 is entirely pre-c90 (98 missing required field agent (c78-c80 emitter chain, lines 1757-2000), 16 status not in unified vocabulary (closed_by_operator/retired/registered, c70-c73), 42 milestone_id not registered (c23-c70 ids + _launches/*), 2 illegal action_required->action_required transitions; all pre-c90, 0 on lines >= 2153). The
close-time counts are recorded in `_run/cycle_90_closed` and `data/v5/logs/validators_c90.json` (`final`).

### Runners decision (P4)

Option **(a)**: `scripts/v5/runners/run_from_launch_json.py` (`9c6f464ebfac72a847ba1dbd0463b9a4df3f904081fea910efb4857c102ec246`) prints or launches detached the exact
command pinned in any `data/v5/logs/*.launch.json` / `byte_determinism_cNN.json` entry (dry-run reproduces the pinned string byte-for-byte; refuses to
execute on a drifted `generate_v5.py` or without a fresh `--out`); `scripts/v5/runners/README.md` (`10c7235558447a70e307f61c226374dfc29c7e832993aaa774c04e272454c325`); the ten c89 session-scratchpad
runners were copied verbatim to `scripts/v5/runners/c89/` (originals were still on disk at c90 open; SHAs in the README). Record:
`data/v5/logs/runners_decision_c90.json`.

### Deliverable index (v5 artifact classes; SHA-256 on disk at c90)

| Artifact | SHA-256 |
|---|---|
| `data/v5/corpus/corpus_manifest.json` | `733621366c023e3800d753d44eebb15cf091fc72353b1ead29ab26600c2e4bfb` |
| `data/v5/corpus/content_blocked.json` | `fc07a13891e1b6b1b35fa338a56f5e58515e6a8dbc4bc2ded53db5e72ee3af6a` |
| `data/v5/corpus/recanonicalization_blocked.json` | `eb78cfc0ce57dc9f50c68e2c683378cd0fe32a6feb4ab55276002ce64e6aa972` |
| `data/v5/corpus/stale/recanonicalization_blocked.c80_c85.json` | `2fbabc07849dbe238545b9e629f91cd81746c6216e5db3027e88f4e9313f8a8e` |
| `data/v5/corpus/tempo_overrides_c86.json` | `ef52f2a032c68b100db717f173eddff25341a1f53adb452de7a591caf81f0109` |
| `data/v5/corpus/tempo_v5_falsification.json` | `767b0ca4d37df4e4fa610949a91440576a8da83092a4e0ec032c0391a1b2b8c4` |
| `data/v5/corpus/tempo_v5b_falsification.json` | `cd5a2f1955d9111510130c7ed004275247b67a6770a9072e49b459e9e5d1610a` |
| `data/v5/corpus/tempo_v5c_falsification.json` | `3efd16d3f117dad55f7a885d79cdcfe068d305ca6ab9900076f37b47afe1996a` |
| `data/v5/corpus/tempo_v5d_falsification.json` | `7b8886ba6779ff14a60d9e4ff1e079d7a56689b25eb8a87f8939055386bf301d` |
| `data/v5/corpus/tempo_mechanism_c82_verdict.json` | `a21e325da3310a2adc829a1bd187854860f80fa35ff5b22ca4cb2fea22f3ddaa` |
| `data/v5/corpus/tempo_f4_verdict_c85.json` | `bec3631aafbbcb401789c2a061396e97c03da6c4a935d4f5f45d35c61d284cb0` |
| `data/v5/corpus/tempo_f4_operator_resolution_c86.json` | `793ee0e166ab054da3c662fceb928730161e53d0d529c8b5e57b3de1928673b3` |
| `data/v5/rules/harmony_markov_v5_full_c86.json` | `330b9d46f715d2a6851221aa02b1bd49889cd039a6256a70c2af71448c7a785a` |
| `data/v5/rules/groove_v5_v2_full_c86.json` | `570720255a6eed6d99e10f24f1249bb0a8c3a2e525504608f17e1c6f3b2caaf6` |
| `data/v5/rules/comping_v5.json` | `010242548c5dc540ae8b0fa0c50e72b54b153b2b78168c2447f4626126376c62` |
| `data/v5/rules/form_plan_v5.json` | `d6c14f9a7b921cffe0311561d1e2f1272a7304924ba2c8184272d2ada35f3682` |
| `data/v5/rules/velocity_profiles_v5.json` | `6b2fc502f065d0ca961c907e93a3c02f80618a1afc34015b4057dd513cb314a8` |
| `data/v5/rules/bass_pitch_v5.json` | `96d34b3bb8fc8b280fdd8ad8ff7b7fb38fdcbac37c94f8b624901096a0e4809c` |
| `data/v5/rules/melody_vomm_v5.json` | `48157c6f04eab5b1f661f47a843aa60e75d2298019a8a4bdee42a4e287b1e9fa` |
| `data/v5/rules/harmony_markov_v5_full.json` | `a984ee17b1b8e2cf7529b95eff5650c66188b6d8578f31862c3f7e2c73305232` |
| `data/v5/rules/groove_v5_v2_full.json` | `faa0e76e4866e370896adc4a87d4ace31b497bb654df6e1a48d044e5234022da` |
| `data/v5/rules/eligible_c84.json` | `e62c6ef3e5f00364814aef6b981df6de5494d714919b220bbec5a1f99a382d85` |
| `data/v5/rules/eligible_c86.json` | `55037c2fc4d80a33f085a1322ebad44b9cd85d1366ca8cf9ab719efde18c9496` |
| `data/v5/rules/harmony_prereg_c86.json` | `b32cf3977c2319a38e1c525d3a28bf650eb5ee8cf7816b28a73ee92f06a02b18` |
| `data/v5/rules/groove_prereg_c86.json` | `995acc5bf4f33e363c2380173bb58a3806635d661618a3bbe93098cae0f58a4b` |
| `data/v5/rules/comping_prereg_c87.json` | `0deb5f24afb36ce4ce4db28d30adb24ef7328ff53e728b7edc68392bec7316f9` |
| `data/v5/gen/form_prereg_c85.json` | `e71eda9b7c44137c94144d0a2f63431cbfb3b6910d692c72a844cde844a37da9` |
| `data/v5/gen/f2_prereg_c86.json` | `2e17ea57ca32398bf789586cbe9d175c6216e8553c1cea487e99f0fed8c3ac5d` |
| `data/v5/gen/f3_prereg_c88.json` | `1f2853259198dc95bf3a43f57005085845e224042c9081d88f5fba9181539a93` |
| `data/v5/gen/f5_prereg_c89.json` | `fb6148435c15b8bbff64dc13e4b3d8cd5501f00ab182b4de757dd9897dd2c16e` |
| `data/v5/gen/stall_counter.json` | `4b87958fd14c2364f2e10088baffa5fa58ef0f1f76237648932b054dbd585e69` |
| `data/v5/gen/byte_determinism_c85.json` | `649c03e629a330e4a6bb464a9f3ae6c50401ce6ebb2df16efd6eac381f985d5e` |
| `data/v5/gen/byte_determinism_c86.json` | `fd9b6cf073ecb1e7407dba8de952572d24c549e1dd2864b6561df58405091597` |
| `data/v5/gen/byte_determinism_c88.json` | `e32805a7f55b7079e7ef88cca8d37647db0c816540eb0e5d17c92bbce9591b13` |
| `data/v5/gen/byte_determinism_c89.json` | `476269f381241406c8cbf2880d801fd7a66d0d457bf73401296f1e18a67c64f3` |
| `data/v5/gen/iteration_01/iteration_rollup.json` | `958c78b5ab5c291b5dcf24fc7916315fdad9d9273d298badf3d5f8458b3939e4` |
| `data/v5/gen/iteration_02/iteration_rollup.json` | `3b0a36fe59a8d7b8bdeceb0dac3150e8fcd4548a3be76284f088d4b5c84019c8` |
| `data/v5/gen/iteration_03/iteration_rollup.json` | `2777917a3b785805e47a9fd796f0ee36be45dafd202810b84fcea6fbc3f66e4b` |
| `data/v5/gen/iteration_04/iteration_rollup.json` | `47efe6dd1a562c6f2bf1c024ed4fc399c67fe3f86661fc70a85a9af4fd72b289` |
| `data/v5/gen/iteration_05/iteration_rollup.json` | `4787a346af5aef34bddccd09914b41445dedfcfe4ef2c8ba7659eb4aa1d86cec` |
| `data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_31a164f845f8e27e/ab_mix.wav` | `947b348a10ab8c5c89491cf1a88eeabda680dbbb4f7d8620899a846ec0d7ddb8` |
| `data/v5/gen/iteration_05/gen_v5_interp_CG_PD_t050_donor_31a164f845f8e27e/f5_blend.json` | `72d9cdcd4790a6c06e868397a09ec793d273a07cd19956ffa0c4d8823de55d1e` |
| `data/v4/generated/v5_iter_01/listening_manifest.json` | `95965775a6e55daba234b21922e00f9baec52412d80a3a88371a34a7d610bf35` |
| `data/v4/generated/v5_iter_02/listening_manifest.json` | `56a6e38969cd2d12b24db796efdb4e4a96a90206067d6c44519980568cbd602b` |
| `data/v4/generated/v5_iter_03/listening_manifest.json` | `67faebcdbd02d9341b87c6bdcb06a85551495aca7d9ded000c33ae17bea8b4a4` |
| `data/v4/generated/v5_iter_04/listening_manifest.json` | `96b73d34512490a0bdbf165de9021c8d08f1aed0fbb081c35d1b5a1cab935ebb` |
| `data/v4/generated/v5_iter_05/listening_manifest.json` | `d8647e7af8fe50a6028a606a24918a074c967979c619556ea668eabb00e30fc9` |
| `data/v4/generated/f5_interp_CG_PD_t050_c89/delivery_manifest.json` | `7cddb63a16a850272262d03f8dba5f0b846ba0c57ca5912b3829a71184bc8402` |
| `data/v5/ear/ear_gate_v5_c82.json` | `c3ead2120dcfdbb8b764a28b38877c025265e7785fe537552409d0318950dba6` |
| `data/v5/ear/venv_amend_c82.json` | `46b818f8d16372686570b1c8bb5b5cf87183c7381c3b02afe9d81930bf910cd2` |
| `data/v5/ear/env_pin_ear_venv_c82_amended.json` | `f31922c8a3fa4d36da744d55b8d851f5277b4c07c0180c1f97d794c0497df47d` |
| `data/v4/ear/band4_spot_check_v2_c76.json` | `d8fcea2a5409410ebe0d5fb427f79f100aca090f17ec68320bcb08af743b30a7` |
| `data/v4/ear/l119_infeasibility_proof_c76.json` | `ada44349277b17e0b2043c419403b2eed5f99046972aa31f94708f411b15a68a` |
| `data/v5/logs/validators_c90.json` | `9f0db6e2ed1150e7c879f25c8461838d08e767410e2db242431222f4e052d354` |
| `data/v5/logs/runners_decision_c90.json` | `75404fc761e1c332e6dd01e2eeaca522b408db3121aa8b02c6a23bafe365f897` |
| `data/v5/logs/c90_prune.json` | `1fdf766ccb8b6c8c321cabc6b83a4f174bfb54712c3d621d492ffeb44a21748c` |
| `scripts/v5/generate_v5.py` | `94c8ba99eac98eee1f88d871cfc520507ddf253d3962287f50a7a368fdaaa055` |
| `scripts/v5/interpolate_v5.py` | `177ac5c6c3f2d7ceebb2110cdb336ea05e414cfd155a962a2e2a0237caab624b` |
| `scripts/v5/repo_root.py` | `d012e5105c838355893f9a5bf7cccf00a387b7689defc230dbf83060743a2804` |
| `scripts/v5/comping_gen_v5.py` | `571cc0a4376741c888e1f455a69b8cb4ffa12680586a1135abba5cd34ba59360` |
| `scripts/v5/velocity_v5.py` | `dd94336de4e09fcec3e34d8ec1bbe9db18a0462398e709f0e3dc3a8281b7169a` |
| `scripts/v5/midi_from_json_events_v5.py` | `4ea85e0bc54e22aca48bb7a7a153cf3f560d0c945168c864df493cdc936efc9b` |
| `scripts/v5/runners/run_from_launch_json.py` | `9c6f464ebfac72a847ba1dbd0463b9a4df3f904081fea910efb4857c102ec246` |

Figures (each co-located with its plot script and data):

| Figure | SHA-256 |
|---|---|
| `data/v5/corpus/fig_tempo_f4_c85.png` | `04fd275829e235b3805df4ab765b65270cf49b20abdbe8dd81f68f867e2fe4f2` |
| `data/v5/corpus/fig_tempo_mechanism_c82.png` | `f66ae33495e7ce74b80416e57ccc623d95aacd8dc2dc078dd02dae4a048531a8` |
| `data/v5/corpus/fig_tempo_v5_autocorr.png` | `eb1664927ff05df092dade49286384402fbf95529954af538c98072fdc926880` |
| `data/v5/corpus/fig_tempo_v5b_scores.png` | `89344d27a06b49173a101f2646c9d3e1b4aa016439933455cce9cfecf2b07175` |
| `data/v5/corpus/fig_tempo_v5c_scores.png` | `8540255fe9e983d10e45f5630b90aeaf20d56aeb6d72e3728f35e434d1161ecb` |
| `data/v5/corpus/fig_unpaired_starts_c83.png` | `929f5b94cdbea2f99a80f81506cc1d4b12b5095c1d8a97f5657314cc164f941a` |
| `data/v5/gen/fig_iter05_parts_c89.png` | `2668bed30cc90832899fb2ffae62edaf97e312cbc0cb9923de55973b512cc1d7` |
| `data/v5/gen/iteration_02/fig_iter02_arrangement_c85.png` | `1c34f0f508d11ee9e53bb4b76af9f0efc8f881f165485e7d158c8e613fa68722` |
| `data/v5/gen/iteration_03/fig_iter03_velocity_c86.png` | `418840fd4f32ec7dc2776755e40c3aba2f39b8079866036e2c1d061b90b77b66` |
| `data/v5/gen/iteration_04/fig_iter04_parts_c88.png` | `3838695c528299156b608d5f807810021dd871777f7b31829676fe8a46890a1e` |
| `data/v5/rules/fig_comping_v5_c87.png` | `0e9274090376a9b02dcb0a61a38730b6aeffdc8d241bb2d8343365167cc36305` |
| `data/v5/rules/fig_form_plan_corpus_c85.png` | `f61c80324e8c15edbf66af7f4076811d33b1ee76e48ceec5aaf333ee56f0b69f` |
| `data/v5/rules/fig_groove_v2_full_c84.png` | `ac1724116c077a7110b7aec3e3e63c05893bba5824650911e7961414b577a152` |
| `data/v5/rules/fig_harmony_full_c84.png` | `9024cd6ce562647603effb8bd17ad4d9a5d180c011a884b9d05893708587a59b` |
| `data/v5/rules/fig_harmony_n23_vs_n21_c86.png` | `19e75e19a6ca0ac5cc874260b8e7b2c13e08be2b318a8f76af9e79448251df6e` |
| `data/v5/rules/fig_velocity_profiles_c86.png` | `61947c87550b35671ce90f67547c48712b14ef8f9b19db8cb06de13182a8e409` |

Tests (adopted v5 suites; c90 re-run results in `data/v5/logs/test_results_c90.json`):

| Test file | SHA-256 |
|---|---|
| `tests/test_c84_landing.py` | `f22bf709685a890a469683d413986777b739dbe7d2327269f64b1ee60223ac2f` |
| `tests/test_c85_f4_m5.py` | `26c0b63ec87310095601a41b2963309b9100c32fc05ccf4e96438bae5d57e339` |
| `tests/test_c85_landing.py` | `adfed20bc6c1fb4e53cd6633b49bff00bcb413e3350692aabadc3d9233618817` |
| `tests/test_c86_f2_models.py` | `4a06ac587e4ab045e9853c0299bda439369957ddecaaaf752b59d71fb0c760dd` |
| `tests/test_c86_f4_close.py` | `c862e2a060c0d5a17d8c0d2b15312d318fb10c5a437b57a3e1391aeabc139436` |
| `tests/test_c86_landing.py` | `c6acb6c128f8404afd61d7c65b70706c542346e96845c36bd4e2f3f4919fa675` |
| `tests/test_c87_comping.py` | `221174a926a41627d4152ebadefc25317c971e7845b523b6ee7e199584dd927e` |
| `tests/test_c87_f3_gen.py` | `0cd83b8977b3b37f023db04deb0afdc899a50f3f0ddac63d3decdc84aeb3e307` |
| `tests/test_c87_landing.py` | `62372974c706213e61d9c036082585818fd9a7eeb42acfbf7fb155ef9f39f981` |
| `tests/test_c88_landing.py` | `926aa951acb901f1a4b8c655b2fd37613a5ab4e4f03f4e35177796613e92adb0` |
| `tests/test_c89_landing.py` | `167ee2931de8ec934163e4772f54ec2a3574a9d8251c11796aba00c2280bfd98` |
| `tests/test_c82_landing.py` | `ea223bd0881203231f3f624ca466d1a55ca1b720f6904889d509bd83a83d8f3b` |
| `tests/test_c83_landing.py` | `cc2dd7d66497ceff838976fb04c172a97dde0b9e3443223a8645ceedb385f4ef` |
| `tests/test_tempo_v5.py` | `e135392bb9b22873059b42503e914303ba26dc46521b2ca5d74b295b9675d9fe` |
| `tests/test_tempo_v5b.py` | `2c748d585f2d259d8d4372488d2f9b9b49b79ffe12d520c5c6576e094d6b5cdd` |
| `tests/test_tempo_v5c.py` | `b971b4f17c345e6c8b2255de2c4524a76fb764b8e3d2795741eccdd2daffdb7d` |
| `tests/test_harmony_v5.py` | `ce624b9f2148aa15e22392291e98faf2a60fbfafcfe2e6b53d4734f67fc22f9e` |
| `tests/test_groove_v5.py` | `1d11298c51705c5363f75c7be79c41946fb9a5f2e95ee5a7f0e3d7fca8868993` |
| `tests/test_ear_venv_c81.py` | `5faa8ee41b088a974041e978eb926948d915d687ecf5bea6a228782d98416c6a` |
| `tests/test_reindex_hygiene_c81.py` | `096fbe25f74375d0d63922ac850cf1a51d5b6626ceb6f6bdc6ffa16ddb4b8b3d` |
| `tests/test_reindex_fidelity_c82.py` | `c8a33afe46451bf272311ad27f4795ca05a91adf084a63bb2e4a1ce047eea5ed` |

Operator guidance files governing v5 (`docs/guidance/`):

| Guidance | SHA-256 |
|---|---|
| `docs/guidance/guidance_2026-09-06_disk_headroom_restored_rebuild_ear_venv.txt` | `114d48a4d5f0ab2ec190de200035be53386fed24d6a0031b237860af85d7704c` |
| `docs/guidance/guidance_2026-09-06_v5_rules_gen_reopening.txt` | `186c07ae20020d1ac178f755e4711b7278d791df7352c3cf8c73421c7693b1b5` |
| `docs/guidance/guidance_2026-09-09_F2_velocity_decision.txt` | `8677bb0cd3f240a0b64ce6c392db2506a58b63f93cd1e4d236f26b32d6ccf7d2` |
| `docs/guidance/guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt` | `fed27e550e9f7c75c04cf11b842877a41de3c48e56f1b00a6d1eea4115e3878c` |
| `docs/guidance/guidance_2026-09-09_finish_features_backlog_F1-F7.txt` | `cf7296cfcf70c27757e5dda55edd758cc3cbc3d854c253f3d726603c05b283b7` |
| `docs/guidance/guidance_2026-09-09_outage_recovery_c128.txt` | `033671f1a610d6c5c21b10eb377d13b6b4b17e09418161f550b27fc003bd842e` |

### Honest gaps

- Tempo axis stopped after four falsified criteria; PD / Disco A tempos rest on operator adoption, not on a supported criterion.
- Groove overfits at n=23 (singleton contexts 0.637448); comping slot histogram structureless; form R1 failed at 0.85; melody VOMM memorises.
- The ear is non-discriminative on this content (L119 monotone-infeasible under VGGish); F2's RMS-variance clause unmet (F2_PARTIAL); GM timbre on 14/15 F3 cells.
- No operator ear verdict yet on the 26 v5 renders + the 25 v4 A/Bs; demo stem gains at the 4.0 cap; blended-chain degeneracy inherited.
- The n=25 sibling artifacts (harmony / groove / comping on n=23 ∪ 0e1e8f20592db366, cc0693b4a24f64b2) were never built — deferred at c88 and c89, skipped at c90.
- promise_check WARN growth is triaged, not eliminated (7,076 orphan-artifact WARNs at open, mostly pre-v5 sweep renders under data/v4/profiles).
- `MANIFEST.md` and `scripts/v5/midi_from_json_events_v5.py` show as modified vs the last commit while their live SHAs equal the c88 pins — commit lag, not drift; no commit was made this cycle.

### Close rationale

Features F1–F5 landed with frozen-enum verdicts, F6 entries are complete on every iteration since c85, F7 is this section (plus
OPERATOR_DECISIONS #21 and the codebase-guide section, all additive). M-V5-GEN-1 closes as an honest best-of at stall 5/12 with
passers delegated to FD-6; M-V5-CORPUS-1 / M-V5-RULES-1 / M-V5-EAR-1 roll up with the verdicts named in their headings; M-V5-CLOSE-1 carries the
frozen enum `V5_CLOSE_LANDS / V5_CLOSE_PARTIAL / V5_CLOSE_FAILS` in the ledger. The run re-closes cleanly at c90; the operator verifies
post-close. A later operator guidance file may reopen it again exactly as c79 did (str-supersede pattern).
