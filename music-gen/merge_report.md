---
created: 2026-08-28T15:20:40Z
cycle: 13
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/post-merge-integration-fork-54a6c185816e
supersedes: fork-ed041ef4c1dc capstone (cycle 12)
---

# Post-Merge Integration Report — fork 54a6c185816e (cycle 13)

## Fanout outcome

Three clones landed. Zero cross-branch file-tree overlap; each clone
wrote under a disjoint subtree and the cycle-12 hardened concat
validated every merged row at collapse time.

| Clone | Milestone                                                    | Verdict          | Deliverable                                                    |
|-------|--------------------------------------------------------------|------------------|----------------------------------------------------------------|
| 0     | M-GEN-1/batch-v2 + M-GEN-1/salt4-diagnostic                  | validated/high   | docs/gen_batch_v2_report.md                                    |
| 1     | M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation         | validated/medium | docs/daw_spike_gap2_dawdreamer_closure_report.md               |
| 2     | M-TEX-1/stage-by-stage widening (seed_mid_50s, synth_060s)   | validated/high   | docs/tex_stage_by_stage_widening_report.md                     |

## Per-clone summary

### Clone 0 — M-GEN-1/batch-v2 (+ salt=4 diagnostic)

Cycle-11 sampler + coherence gate + render pipeline expanded to 8
salts (0..7) on the cycle-12-expanded 76-row rules ledger. All 59
output files byte-deterministic × 2. Salt=0 anchors pinned on the
76-row ledger (harmonic `rule_0271c7a9f3b5f606`, rhythmic
`rule_88b63bd5e771c045`, melodic `rule_daf022a4051dff00`, form
`rule_8e6c38d5397fb898`, arrangement `rule_51d59f03c4f09e1a`); the
frozen batch-v1 `sampling_manifest.json` is untouched (§21 anchor
block reads it and passes).

**Salt=4 diagnostic verdict: `no_material_pattern`.** The cycle-12
N=5 salt=4 signal (75% of residual collision pairs) was small-N noise.
At N=8: salt=4 collision-endpoint share 13.6% vs uniform 12.5%
(z=+0.14). Salt=1 now leads (5 endpoints), driven by the harmonic
4-clique {0,1,5,6} sharing `rule_0271c7a9f3b5f606` (F_major cycle-9
anchor). No attribution path (hash-space, arrangement-structural,
coherence-gate) crosses its threshold — an honest null result rather
than a forced root cause.

**Collision-floor finding.** Total pairs at N=8 = 11, within 2% of
the constant-per-pair-rate scaling from cycle-12
(4 × C(8,2)/C(5,2) = 11.2). **The collision floor is set by rule-type
structural diversity, NOT corpus size.** Cycle-12's 28→76 expansion
did not reduce per-pair collision rate; the harmonic 4-clique remains
because a single rule (the cycle-9 F_major anchor) covers all four
salts. Cycle-14 lever: synthesize a third breadth seed in a different
mode (D_minor) to shatter the clique.

### Clone 1 — M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation

DawDreamer `set_automation` on Surge XT Effects VST3 param 10 (Output
Mix), 3-point curve 0.0→0.7→0.2 over 10s @ 44.1kHz stereo,
byte-deterministic × 2. **Verdict: redefined-GAP (validated/medium).**
`env_correlation` vs a piecewise-fixed reference = 0.487, below the
PRIMARY 0.9 threshold — but `auto_vs_flat_max_sample_diff` = 0.072
(>> 1e-4 automation-silently-ignored bar) and `curve_vs_envelope`
delta = 0.357 (≥ 0.30 SECONDARY shape-drive bar). The API path
works and drives the parameter; the brief Pearson test is not
diagnostic on the Surge XT delay preset (Output Mix inversely
correlates with mono RMS envelope, weakening Pearson against a step
reference).

Sharper diagnosis carried forward: DawDreamer 0.9.0
`make_plugin_processor` fails uniformly on LV2 ("Unable to load
plugin"). VST3 is the only working automation path. Cycle-9 pinned
DawDreamer chain grep-verified untouched.

Coverage matrix v3 emitted at `data/daw_spike/coverage_matrix_v3.json`
(v2 unmodified). SHA anchors for the four gap2_v3 WAVs pinned in §26
of the cross-branch test.

### Clone 2 — M-TEX-1/stage-by-stage widening

Cycle-9 stage-by-stage panel (1 seed = synth_030s) widened to two
additional breadth seeds (`seed_mid_50s`, `synth_060s`). 3 seeds ×
3 ordered pairs × 8 panel keys = **72 panel numbers**, all finite,
all byte-deterministic × 2. Self-distance guard held on every seed
(numeric ≤ 1e-6, embedding ≤ 1e-4). Cycle-9 `synth_030s` TSV
byte-identical (regression preserved). Cycle-9 pinned DawDreamer
chain composed verbatim — new content is only the input-selection
layer.

**Interpretive verdict: content-dependent family disagreement.**
Family disagreement is preserved on every seed (aggregation-refusal
design commitment upheld), but the *direction* of the VGGish
inversion is content-dependent:

- Polyphonic seeds (`synth_030s`, `synth_060s`): 4/5 metrics rank
  bare closer to original; VGGish embedding inverts (effects closer).
  The cycle-9 signal PERSISTS on the second polyphonic seed.
- Monophonic decaying-triad (`seed_mid_50s`): spectral says effects
  closer; envelope RMS ties; LUFS-M and VGGish invert the inversion
  (bare closer). The chain's linear 0.25→1.4 gain ramp fights the
  natural amplitude decay of sine content.

Legitimate aggregation-refusal support: no single metric ranks pairs
correctly across all three seeds; no seed has all five metrics in
agreement. A single-number aggregate would erase this signal.

## Cross-branch integration verification

`tests/test_integration_cross_branch.py` — **PASS (0 failures)**.
Cycle-13 additions:

- §25 (clone-0): 46 M-GEN-1/batch-v2 invariants — 8 song trees, salt=0
  anchor block, salt=4 verdict enumeration, collision-analysis shape,
  PYTHONHASHSEED discipline, figure/report presence.
- §26 (clone-1): M-DAW-SPIKE-1/gap-closure/gap2-dawdreamer-automation
  invariants — 4 WAV SHA anchors, coverage_v3 shape, negative-attestation
  import checks, ledger event presence. Clone-2's post-merge note
  flagged a potential §26 self-substring-match false positive on the
  negative-attestation docstring — the check passes cleanly in the
  integration environment, so no source fix was needed.
- §27 (clone-2): 33 M-TEX-1/stage-by-stage widening invariants —
  per-seed byte-determinism SHAs, cycle-9 regression preservation,
  self-distance contracts, 8-key panel shape.

Other suites re-verified post-merge: `test_fanout_concat_validation.py`
10/10 pass; `test_ledger_writer_validation.py` 13/13 pass.

## Integration-time repairs

Two ledger repairs were required at integration entry before
`promise_check` and the driver could run cleanly:

1. **Line 266 (clone-1 `_archive/gap2-dawdreamer-scratch`) —**
   `supersedes_path` was emitted as a JSON list (`["tools/_dd_probe.py",
   "tools/_dd_probe2.py", "tools/_emit_gap2_v3_events.py"]`) rather than
   a string. Every other row in the ledger uses string form.
   `promise_check._canon` crashed with `AttributeError: 'list' object has
   no attribute 'lstrip'`. The cycle-12 hardened `concat_clone_ledgers`
   did not catch it — the SSoT `_ledger_schema.validate_event` does not
   type-check `supersedes_path`. Repair: rewrote the field in place to a
   single string (`"tools/_emit_gap2_v3_events.py"`); the other two
   archived paths remain listed in the event's `artifacts` field, so no
   provenance information is lost. Cycle-14 hardening opportunity:
   extend the SSoT validator to reject list-form `supersedes_path` at
   emit and concat time.

2. **Line 250 (clone-2 `M-TEX-1/stage-by-stage` kickoff) —** status
   was emitted as `in-progress` immediately after cycle-9's
   `validated/high` roll-up. `promise_check` errored: transition
   validated → in-progress requires an intervening `reopened` event. The
   event's own narrative reads "this event marks reopening under the
   widening sub-scope", so the status was the wrong keyword. Repair:
   rewrote status to `reopened`. No other fields changed.

Both repairs follow the campaign anti-pattern precedent recorded in
cycle 8 (`M-TRANS-1/basic-pitch/octave-suppression`: "reconstructed at
post-merge integration; original shadow-ledger schema was flat").

## Rollup ledger events (6 emitted)

Ledger grew 268 → 274 rows:

1. `_infra/adopt-fanout-artifacts-m-gen-1-batch-v2` — adopts 7 orphan
   `data/ear/features/gen_first_gen_*.npz` per-song ear-scoring feature
   caches (clone-0).
2. `_infra/adopt-fanout-artifacts-m-daw-spike-1-gap-closure-cycle13`
   — adopts 5 files under `scripts/daw_spike/gap2_v3/` including the
   previously-orphan `__init__.py` (clone-1).
3. `_plan/register-post-merge-integration-fork-54a6c185816e` — records
   the integration cycle. No plan-of-record drift: all cycle-13
   milestone rows were added by the clones themselves.
4. `_infra/cross-branch-integration-test-cycle13` — records post-merge
   verification of §25/§26/§27 extensions.
5. `_run/post-merge-integration-fork-54a6c185816e` — capstone (this
   report + the 3 clone reports).
6. `_archive/integration-scratch-fork-54a6c185816e` — self-archives
   the driver to `tools/stale/`; supersedes fork-`ed041ef4c1dc`
   integration driver (already stale).

## Final validator state

`promise_check`: **0 ERRORs**, 9 WARNs — all pre-existing / unfixable
in this workspace:

- 5 non-canonical artifact-path WARNs (lines 10/17/88/161, cycles 1-11)
  and 1 new (line 265, clone-1 cycle-13) — trailing-slash convention;
  in-place rewrite would break the events' content hashes.
- 1 `M-EAR-1` parent-with-no-events WARN — sub-milestones all
  validated; parent roll-up call carried to cycle 14.
- 2 upstream `long_exposure/{tools/_ledger_schema.py,
  workspace_bootstrap.py}` "missing" WARNs — upstream paths outside
  this workspace's scope.

## Anti-patterns preserved

Nothing this cycle challenged the two locked anti-patterns:

- `M-TEX-1/panel/embedding` (cycle 11): CLAP swap NOT reattempted.
  VGGish rung remains the perceptual embedding.
- `M-TRANS-1/basic-pitch/octave-suppression` (cycle 8): +0.15 uplift
  below +0.3 bar; not reattempted.

## Handoff pointers for cycle 14 (researcher)

Consolidated from the three clone reports:

1. **Break the harmonic 4-clique.** Synthesize a third breadth seed
   in a mode other than F_major (candidate: D_minor) and run only the
   harmonic extractor against it. Would eliminate 6 of 11 residual
   collision pairs at N=8.
2. **`c2` permanent-fire structural constraint.** Prototype a
   form-scoped harmonic extractor to move `chord_progression` from
   `scope=song` to `scope=form_section`.
3. **Rule-type structural diversity is the collision-floor bottleneck**,
   not row count. Reshape corpus-planning targets accordingly.
4. **DawDreamer `set_automation` is now available** for M-GEN-1 effects
   diversity. Promotion path to GREEN-via-DawDreamer: (a) a VST3
   plugin with monotonic mix→RMS response, or (b) a piecewise-linear
   reference tuned to the plugin's actual response curve.
5. **DawDreamer 0.9.0 LV2 loader failure worth surfacing** — every
   LV2 plugin `make_plugin_processor` attempt failed with "Unable to
   load plugin". Not a blocker for GAP-2 (VST3 works) but limits LV2
   inventory for future effects diversity.
6. **Cycle-9 signal generalizes on polyphonic content**, not on
   monophonic decaying-triad. Widening the panel to a fourth
   qualitatively-different seed (candidate: sustained-mono, e.g. an
   organ pad) would sharpen the content-dependency verdict.
7. **M-EAR-1 parent roll-up call** — sub-milestones all validated;
   parent event needed to clear the standing WARN.
8. **Ear head still uncalibrated** — awaiting egress unblock for
   M-EAR-1/armed-harness rated-audio training run.
9. **CLAP embedding rung still blocked** on HF SSL cert (locked
   anti-pattern) — probe a non-HuggingFace mirror if any surfaces.
10. **SSoT validator hardening opportunity** — type-check
    `supersedes_path` as string (reject list) at both writer and concat
    time so clone-1's cycle-13 shadow-ledger drift cannot recur.

## Environment (unchanged from cycle 12)

torch 2.13.0+cpu, torchvision 0.28.0 (register_fake no-op workaround),
numpy 1.26.4, music21 9.1.0, mscore3 3.2.3, basic-pitch 0.4.0 in
quarantined venv, DawDreamer 0.9.0, single-thread BLAS pins
(OMP/MKL/OPENBLAS = 1). Egress: still blocked per
`corpus/CORPUS_STATUS.md`.
