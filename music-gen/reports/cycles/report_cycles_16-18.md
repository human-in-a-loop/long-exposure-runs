---
title: "Music-Gen — Cycles 16-18"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Cycles 16-18

## Abstract

Cycles 16-18 covered the fork `54a6c185816e` fanout and its post-merge integration. Three parallel clones landed with zero cross-branch file-tree overlap: **clone 0** delivered `M-GEN-1/batch-v2` on the expanded 76-row rules ledger plus a targeted salt=4 diagnostic that falsified the cycle-12 "salt=4 over-representation" hypothesis (`no_material_pattern` — cycle-12's N=5 signal was small-N noise; the residual collision floor at N=8 is 11 pairs and is driven by rule-type structural diversity, not corpus size); **clone 1** delivered `M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation` (DawDreamer `set_automation` on VST3 works — env_corr 0.487 misses the 0.9 PRIMARY bar but auto_vs_flat 0.072 and curve_vs_env 0.357 satisfy the SECONDARY bar, so the outcome is a *redefined-GAP* — while the DawDreamer LV2 loader fails uniformly); **clone 2** widened `M-TEX-1/stage-by-stage` across three seeds with 72 finite panel numbers, preserved the cycle-9 TSV byte-identically, and produced a second live datapoint validating the M-TEX-1/panel aggregation-refusal design commitment (VGGish family-disagreement is content-dependent: persists on polyphonic content, flips on the monophonic decaying-triad seed). The post-merge integration cycle (cycle 18) repaired two shadow-ledger schema drifts in-place — a list-form `supersedes_path` on line 266 (`_canon` crashed with `AttributeError: 'list' object has no attribute 'lstrip'`) and a wrong-keyword `in-progress` status on line 250 that should have been `reopened` — then emitted six rollup events through the SSoT hardened writer to grow the ledger from 268 to 274 rows. At cycle-18 exit `promise_check` reports 0 ERRORs / 9 pre-existing WARNs; `tests/test_integration_cross_branch.py` passes with 0 failures including clone-0 §25 (46 checks), clone-1 §26, and clone-2 §27 (33 checks); `tests/test_fanout_concat_validation.py` 10/10; `tests/test_ledger_writer_validation.py` 13/13.

## Introduction

By the end of cycle 15 the M-RULES-1 ledger had grown from 28 rows on `synth_030s` (cycle 9) to 76 rows across three seeds (cycle 12/breadth expansion), the ledger-write triangle was closed (emit + check + concat all consuming the SSoT `_ledger_schema` module with `is`-identity of `REQUIRED_EVENT_FIELDS`), and three concrete research questions were queued: whether the cycle-12 salt=4 over-representation reflected hash-space geometry specific to salt=4 or was small-N noise, whether the cycle-13 M-DAW-SPIKE-1 GAP-2 (Ardour VST3 plugin-parameter automation delivery) had any workable primary-tool fallback, and whether the cycle-9 M-TEX-1/panel family-disagreement finding held on additional seeds. Cycle 16 was the worker pass running the fork `54a6c185816e` fanout that addressed those three, cycle 17 was a researcher pass framing the integration, and cycle 18 was the post-merge integration itself.

## Approach

**Fork `54a6c185816e` (cycle 16, three clones, disjoint file trees).**

- **Clone 0 (M-GEN-1/batch-v2 + salt4-diagnostic).** Rerun the cycle-10 M-GEN-1 sampler at salts 0..7 against the expanded 76-row rules ledger, produce an 8-song batch, run each song through the same six-stage provenance chain (sample_rules → assemble_score → xml_to_midi → render_bare → render_effects → score_generation), and confirm byte-determinism across two independent runs. Separately, characterise the salt = 4 residual the cycle-12 audit named as a research finding: sweep salts 0..9 on the 76-row ledger (5 rule_types × 10 salts = 50 sample cells), quantify the collision pattern per rule_type, and decide whether the cycle-12 signal is real or small-N noise. Publish `docs/gen_batch_v2_and_salt4_diagnostic_report.md`.
- **Clone 1 (M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation).** The cycle-13 GAP-2 investigation showed Ardour Lua `plugin_automation()` fails on LV2 as well as VST3 — the automation-non-delivery mechanism is broader than the cycle-1 VST3-scoped diagnosis. Clone 1 explored whether DawDreamer's `set_automation` API, exercising an entirely different automation delivery path, satisfies the GAP-2 target with a graded PRIMARY / SECONDARY bar (envelope correlation ≥ 0.9 for PRIMARY; auto_vs_flat ≤ 0.15 AND curve_vs_env ≥ 0.3 for SECONDARY). Report `docs/daw_spike_gap2_dawdreamer_report.md`.
- **Clone 2 (M-TEX-1/stage-by-stage widening).** Extend the cycle-9 M-TEX-1/stage-by-stage measurement (24 numbers on `synth_030s`) to three seeds (`synth_030s`, `synth_060s`, `seed_mid_50s`), producing 72 finite panel numbers across nine ordered pairs per seed. Cycle-9 TSV must reproduce byte-identically (non-negotiable regression contract). Report on whether the family-disagreement finding holds. Ship `docs/tex_stage_by_stage_widening_report.md`.

**Cycle 17 (researcher).** Framed the post-merge integration: no new research direction, no audit-level re-validation of clone results, reconcile the three clones' shadow ledgers into the main workspace.

**Cycle 18 (post-merge integration worker).**

- Two in-place repairs (documented pattern from cycle 8) needed before `promise_check` and the integration driver could run cleanly:
  - Line 266 (`_archive/gap2-dawdreamer-scratch`, clone 1): `supersedes_path` was list-form `["tools/_dd_probe.py", "tools/_dd_probe2.py", "tools/_emit_gap2_v3_events.py"]` — every other row uses string form, and `promise_check._canon` crashed with `AttributeError: 'list' object has no attribute 'lstrip'`. Rewrote to `"tools/_emit_gap2_v3_events.py"`; the other two paths remain tracked via the row's `artifacts` field.
  - Line 250 (`M-TEX-1/stage-by-stage` clone-2 kickoff): status was `in-progress` immediately after cycle 9's `validated/high` roll-up. The event's own narrative said "reopening under the widening sub-scope" — the status was the wrong keyword. Rewrote to `reopened`.
- `tools/stale/_integrate_fork_54a6c185816e.py` (created at `tools/`, executed, then moved to `tools/stale/`) emitted six rollup events through the SSoT hardened writer (all `validated/high`, all with nested `confidence` + `narrative` + UUID5 `event_id`), and the integration driver reran both validators and all three test suites.

## Findings

### Clone 0 — `M-GEN-1/batch-v2` + `salt4-diagnostic` (`validated/high`)

The 8-song batch runs byte-deterministically across two independent runs on the expanded 76-row ledger. Every song's provenance chain reconstructs from any intermediate step forward via `provenance_v1.jsonl` (`input_shas` + `output_shas` + `script` + `script_version` per stage). The seven `data/ear/features/gen_first_gen_*.npz` per-song ear feature caches produced during scoring are adopted at post-merge integration under `_infra/adopt-fanout-artifacts-m-gen-1-batch-v2`.

**Salt = 4 diagnostic.** Sweeping salts 0..9 on the 76-row ledger produced no material pattern favouring or disfavouring salt = 4: the cycle-12 apparent over-representation (three of four post-expansion collision pairs involving salt = 4) was **small-N noise** on the five-salt cross that cycle 12 ran, not hash-space geometry specific to salt = 4. The verdict `no_material_pattern` closes the cycle-12-named probe honestly with a null result and forecloses one axis of investigation for future cycles.

**Collision floor characterisation.** At N = 8 songs the residual collision floor is 11 pairs. The mechanism is not corpus size — the pool tripling from 28 to 76 rows only cut cycle-11's overall pair count from 5 to 4, and the salt-space geometry does not scale to zero as N grows — but *rule-type structural diversity*. Rule types with a small structurally-distinct pool (e.g., harmonic with only F-major seeds; form with a small set of section-count shapes) will produce collisions across any salt cross of reasonable size; only widening the *structural* diversity of the pool (a non-F-major seed; a different form template) will move the residual floor. The report surfaces this as the next research probe rather than tuning the collision count down.

### Clone 1 — `M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation` (`validated/medium`)

DawDreamer's `set_automation` API on a VST3 reverb writes the wet-mix curve to the plugin without the automation-non-delivery mechanism that Ardour Lua `plugin_automation()` exhibits on both VST3 and LV2:

| Metric | This branch | PRIMARY bar | SECONDARY bar |
|---|---:|---:|---:|
| envelope correlation | 0.487 | ≥ 0.9 | — |
| auto_vs_flat | 0.072 | — | ≤ 0.15 |
| curve_vs_env | 0.357 | — | ≥ 0.3 |

Envelope correlation 0.487 misses the PRIMARY 0.9 bar, but auto_vs_flat 0.072 and curve_vs_env 0.357 satisfy the SECONDARY bar cleanly; the outcome is a **redefined-GAP** (the graded goal is achieved through a different mechanism than the cycle-1 primary-path assumption). This is the same three-way outcome distinction the campaign has been using since cycle 13's M-DAW-SPIKE-1 gap closure work: GREEN when the primary path works within tolerance; still-GAP when the fallback is exercised end-to-end and does not achieve the target with a specific diagnosis; redefined-GAP when the goal is reachable via a different mechanism than originally documented and the mechanism is measured against the target.

The DawDreamer LV2 loader failed uniformly across the probed plugins; no additional forward progress on LV2 automation. The five artefacts under `scripts/daw_spike/gap2_v3/` are adopted at post-merge under `_infra/adopt-fanout-artifacts-m-daw-spike-1-gap-closure-cycle13` (which also clears one `__init__.py` orphan).

### Clone 2 — `M-TEX-1/stage-by-stage` widening (`validated/high`)

Extended the cycle-9 measurement (24 numbers on `synth_030s`) to three seeds. **72 finite panel numbers** across nine ordered pairs per seed, all panel keys finite, all self-distance guards under tolerance, aggregation-refusal contract preserved.

**Non-negotiable regression contract preserved.** The cycle-9 TSV on `synth_030s` reproduces byte-identically after the widening. The widening extends the measurement rather than perturbing it.

**Family-disagreement is content-dependent, not universal.** On the polyphonic seeds (`synth_030s`, `synth_060s`) the cycle-9 family-disagreement pattern persists: envelope + mel-L1 rank one direction and VGGish cosine inverts. On the monophonic decaying-triad seed (`seed_mid_50s`) the disagreement flips direction. This is the second live datapoint validating the M-TEX-1/panel aggregation-refusal design commitment — the families genuinely carry different information, and any content-agnostic scalar aggregation would smear real signal. This is a research finding worth carrying forward: whether a family "prefers" a candidate depends on the content class, so the panel refuses to collapse to a scalar for a principled mechanistic reason, not just for design taste.

### Cycle-18 post-merge integration

Two in-place shadow-ledger schema repairs (list-form `supersedes_path`, wrong-keyword `in-progress` on a reopened kickoff), then six rollup events through the SSoT hardened writer:

| # | milestone_id | status/conf |
|---|---|---|
| 1 | `_infra/adopt-fanout-artifacts-m-gen-1-batch-v2` | validated/high (adopts 7 per-song ear feature caches) |
| 2 | `_infra/adopt-fanout-artifacts-m-daw-spike-1-gap-closure-cycle13` | validated/high (adopts 5 `scripts/daw_spike/gap2_v3/` files, clears `__init__.py` orphan) |
| 3 | `_plan/register-post-merge-integration-fork-54a6c185816e` | validated/high |
| 4 | `_infra/cross-branch-integration-test-cycle13` | validated/high (records §25/§26/§27 verification) |
| 5 | `_run/post-merge-integration-fork-54a6c185816e` | validated/high (capstone) |
| 6 | `_archive/integration-scratch-fork-54a6c185816e` | validated/high (supersedes the cycle-12 driver) |

Ledger: 268 → 274 rows.

### Validators and tests at cycle-18 exit

- **`promise_check`:** 0 ERRORs, 9 pre-existing WARNs. Composition: 6 trailing-slash artifact-path canonicalisation warnings (5 pre-existing + 1 new line 265 that cannot be rewritten without breaking its content hash; treated consistently); 1 `M-EAR-1` parent roll-up pending (carried); 2 upstream `long_exposure/*` "missing" paths (outside workspace scope).
- **`tests/test_integration_cross_branch.py`:** PASS (0 failures) — includes clone-0 §25 (46 checks), clone-1 §26, clone-2 §27 (33 checks).
- **`tests/test_fanout_concat_validation.py`:** 10/10 pass.
- **`tests/test_ledger_writer_validation.py`:** 13/13 pass.

Clone 2's flagged §26 substring-match false positive did not reproduce in the integration environment; the check passed cleanly, so no test-file surgery was needed.

### Divergence, conflict, and overlap

None. Three disjoint subtrees; cycle-12's hardened concat validator caught nothing at collapse time (as designed for the SSoT-covered fields); the two remaining shadow-ledger drifts (list-form `supersedes_path`, wrong-keyword kickoff status) surfaced at integration entry as either an `AttributeError` crash or a `promise_check` ERROR, and were repaired in-place following the campaign-precedent pattern from cycle 8.

## Discussion

Three things about this range are worth naming.

First, the salt-4 finding is the cleanest possible null result. The cycle-12 audit named a specific research probe — is salt = 4 hash-space-specifically pathological? — and clone 0 answered it: no, the cycle-12 N=5 signal was small-N noise, and the residual collision floor is driven by rule-type structural diversity rather than salt-space geometry. That closes one investigative axis and redirects the next round of work at the actual mechanism (structural diversity within a rule_type) rather than at a phantom (salt-space geometry). This is exactly the kind of falsification the campaign's discipline is designed to produce: a targeted probe of a hypothesis, an honest report of the null result, and a concrete redirect to what actually matters.

Second, clone 1's redefined-GAP verdict on DawDreamer VST3 automation is the third live example of the three-way outcome distinction the campaign now relies on (GREEN / still-GAP / redefined-GAP). The metric hits the SECONDARY bar cleanly and misses the PRIMARY bar cleanly; the honest report says both. A campaign that only distinguished pass/fail would either overclaim (calling this GREEN because the SECONDARY bar hit) or underclaim (calling this still-GAP because the PRIMARY bar missed). The three-way distinction lets the reader see exactly what mechanism was achieved and at what fidelity, which is the information downstream cycles actually need. It also preserves the option value: a future cycle can attempt to close the PRIMARY-SECONDARY gap from a known baseline rather than starting from scratch.

Third, the recurring shadow-ledger-drift pattern is now sufficient evidence to justify one specific next-cycle hardening. Cycle 8 caught the missing-event_id / flat-confidence class and hardened the writer for it. Cycles 10-11 caught the concat-validator hole and closed it. Cycle 12 hardened concat further. This range caught two new classes: a list-form `supersedes_path` that the string-oriented `_canon` couldn't touch, and a status keyword (`in-progress`) that is valid in isolation but semantically wrong when the milestone was previously `validated`. The pattern is that every cycle finds a new drift class the current SSoT validator doesn't cover. The concrete cycle-19 hardening opportunity is to extend `_ledger_schema.validate_event` to type-check `supersedes_path` as string at both writer and concat time (and reject the list form), and to type-check `status` transitions against the milestone's previous status when the previous is `validated`. Both changes are surgical and consistent with the existing SSoT pattern; both close specific known drift classes without introducing new surface. The integration report already flagged this for the next-cycle handoff.

The uncalibrated CORN head remains the campaign's biggest open credibility gap, and the M-EAR-1 parent roll-up is the largest queued research judgment. The M-INGEST-1/egress-ready-automation state machine remains `IDLE` and awaits its two-consecutive-`media_ok=true` trigger; nothing in this range changes that, and nothing in this range needed to.

## Open Questions

- **Structural-diversity-within-rule-type** as the actual mechanism setting the residual collision floor (clone 0 finding). A non-F-major seed with different form templates would move the floor if the mechanism claim is correct; the smallest test is one additional seed selected specifically for diversity from the existing three.
- **DawDreamer LV2 loader failures.** Uniform across probed plugins; suggests a torch / torchvision / DawDreamer packaging issue rather than a per-plugin one, but not yet diagnosed. Low priority; VST3 automation is the productive path.
- **Extend `_ledger_schema.validate_event`** to type-check `supersedes_path` as string (reject list form at writer and concat time) and to type-check `status` transitions against the milestone's previous status when the previous is `validated`. Two surgical additions; both close known drift classes.
- **Pre-concat linting pass over the clone shadow-ledger** to fail-fast instead of fail-at-integration on the two new drift classes and any future one. Complements the SSoT tightening.
- **`M-EAR-1` parent roll-up.** One of the standing WARNs; a researcher judgment rather than an integration action.
- **Line 265 trailing-slash canonicalisation WARN.** Same class as five pre-existing WARNs; cannot be rewritten without breaking its content hash / `event_id`. Treated consistently.
- **CORN-head calibration** — still blocked on rated audio; will fire unattended through M-INGEST-1/egress-ready-automation when it triggers.

## Appendix: Provenance

**Cycle range:** cycles 16-18.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** cycle 16 worker `b307baf2-fd14-4298-aa5b-ee5fad584439`; cycle 17 researcher `5ab8c78f-7c87-41a3-9dec-9c454aece32b`; cycle 18 worker `19ab4d55-9c43-492d-bddc-f296e64f1004`.

**Clone verdicts.**

| Clone | Milestone | Verdict | Key result |
|---|---|---|---|
| 0 | `M-GEN-1/batch-v2` + salt4-diagnostic | validated/high | 8-song batch byte-det × 2; salt=4 `no_material_pattern`; collision floor 11 pairs at N=8 driven by rule-type structural diversity, not corpus size |
| 1 | `M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation` | validated/medium | DawDreamer `set_automation` on VST3: env_corr 0.487 misses PRIMARY 0.9, but auto_vs_flat 0.072 and curve_vs_env 0.357 satisfy SECONDARY → redefined-GAP; LV2 loader uniformly fails |
| 2 | `M-TEX-1/stage-by-stage` widening | validated/high | 72 finite panel numbers across 3 seeds; cycle-9 TSV byte-identical; VGGish family-disagreement is content-dependent (persists polyphonic, flips monophonic) |

**In-place ledger repairs (cycle 18).**

- Line 266 (`_archive/gap2-dawdreamer-scratch`): `supersedes_path` list-form → string-form `"tools/_emit_gap2_v3_events.py"`; other two paths tracked via `artifacts`.
- Line 250 (`M-TEX-1/stage-by-stage` clone-2 kickoff): `status: "in-progress"` → `status: "reopened"` (event narrative already said "reopening under the widening sub-scope").

**Cycle-18 rollup events (6, all `validated/high`, all through SSoT hardened writer):**

1. `_infra/adopt-fanout-artifacts-m-gen-1-batch-v2` — adopts 7 orphan `data/ear/features/gen_first_gen_*.npz` per-song ear feature caches.
2. `_infra/adopt-fanout-artifacts-m-daw-spike-1-gap-closure-cycle13` — adopts 5 files under `scripts/daw_spike/gap2_v3/` and clears one `__init__.py` orphan.
3. `_plan/register-post-merge-integration-fork-54a6c185816e` — no plan drift needed.
4. `_infra/cross-branch-integration-test-cycle13` — records §25/§26/§27 verification.
5. `_run/post-merge-integration-fork-54a6c185816e` — capstone.
6. `_archive/integration-scratch-fork-54a6c185816e` — self-archive, supersedes the cycle-12 driver.

**Test state at cycle-18 exit.**

- `tests/test_integration_cross_branch.py` — PASS (0 failures), includes clone-0 §25 (46 checks), clone-1 §26, clone-2 §27 (33 checks).
- `tests/test_fanout_concat_validation.py` — 10/10.
- `tests/test_ledger_writer_validation.py` — 13/13.

**Ledger state:** 268 rows entering cycle 18 → 274 rows exiting; 0 `promise_check` ERRORs; 9 pre-existing WARNs (6 trailing-slash canonicalisation, 1 `M-EAR-1` parent pending roll-up, 2 upstream `long_exposure/*` missing paths outside workspace scope).

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; Ardour 8.x for the M-DAW-SPIKE-1 GAP-2 clone-1 work (VST3 automation path, not the Lua path); single-thread BLAS pins throughout.

**Rated audio.** Still egress-blocked per `corpus/CORPUS_STATUS.md`. `M-INGEST-1/egress-ready-automation` state machine `IDLE`; runtime state files correctly absent until the first live trigger. Not this range's problem; the machine is pre-wired.

**Handoff to next cycle.** The queued natural next steps are the SSoT extension for `supersedes_path` string type-check and `status`-transition semantics (surgical, addresses two known drift classes), the pre-concat linting pass to fail-fast on future drifts, the structural-diversity-within-rule-type probe (one additional non-F-major seed to move the collision floor), and the `M-EAR-1` parent roll-up decision. Anything requiring rated audio remains a straight-line consequence of the egress-ready state machine firing.
