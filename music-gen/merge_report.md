---
created: 2026-08-28T16:20:40Z
cycle: 14
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/post-merge-integration-fork-855d4c2e9945
supersedes: fork-54a6c185816e capstone (cycle 13)
---

# Post-Merge Integration Report — fork 855d4c2e9945 (cycle 14)

## Fanout outcome

Three clones landed. Zero cross-branch file-tree overlap; each clone
wrote under a disjoint subtree and the cycle-12 hardened concat
(now also lint-gated per clone-0's cycle-14 tightening) validated
every merged row at collapse time.

| Clone | Milestone                                                     | Verdict            | Deliverable                                              |
|-------|---------------------------------------------------------------|--------------------|----------------------------------------------------------|
| 0     | _infra/ledger-schema-hardening-v2                             | validated/high     | docs/ledger_schema_hardening_v2.md                       |
| 1     | M-GEN-1/collision-floor-investigation                         | validated/high     | docs/collision_floor_investigation_report.md             |
| 2     | M-TEX-1/panel/embedding/content-flip-analysis                 | validated/medium   | docs/tex_embedding_content_flip_report.md                |

## Per-clone summary

### Clone 0 — _infra/ledger-schema-hardening-v2

Closes the three-cycle SSoT ledger-schema hardening arc: writer gate
(cycle 10) → concat gate (cycle 12) → field-type + enum gate (this
cycle). `long_exposure/tools/_ledger_schema.validate_event` now rejects
non-string `supersedes_path` (the cycle-13 line-266 `AttributeError`
crash class) and any `status` outside the canonical enum
{action_required, deferred, in-progress, invalidated, not-started,
reopened, superseded, validated}. A `_lint_clone_shadow` seam is
factored out of `concat_clone_ledgers` and re-exported at
`workspace_bootstrap` module top level, so the per-row pre-concat
validate loop is now a named, importable, testable function rather
than an inline one. Public API of both `append_ledger_event(workspace,
event)` and `concat_clone_ledgers(workspace, fork_dir) → int` is
byte-preserved across cycles 1–13. 277/277 existing ledger rows
validate under the tightened schema (dynamic sweep; ledger grew from
brief-cited 275 to 277 mid-run and the sweep absorbed the growth
correctly). Writer suite 18/18 (five new cases), concat suite 13/13
(three new cases plus the MRO check), integration §28 8/8. Auditor
verdict validated/high.

One honest surprise: cycle-13's line-250 nuance was misclassified in
the original diagnostic as an enum drift when it was actually a
**state-transition drift** class (`validated → in-progress` without an
intervening `reopened`). The enum check passes on `in-progress` — it
is a canonical enum member — so the enum extension does *not* fire on
that specific line. The response was to ship the enum check anyway
(it catches a real `wobble`-style unknown-value class) and hoist the
actual state-transition mechanism to a cycle-15 follow-up. Neither
check is over-claimed to close a class it doesn't.

### Clone 1 — M-GEN-1/collision-floor-investigation

Root-caused the 11-pair collision floor at N=8 salts on the
cycle-12-expanded 76-row rules ledger. Every pair attributed to its
dominant `rule_type` contributor: harmonic 6, rhythmic 2, melodic 2,
arrangement 1, form 0 (with pair (1,5) dual-contributed by harmonic +
melodic, so 10 unique any-collision pairs). Verdict: **dominant-rule
regime — small-K statistical fluctuation on harmonic, NOT structural
clustering** (aggregate 11 observed vs birthday-paradox expected 9.64,
within 15%; one harmonic rule out of K=10 is captured by 4 of the 8
salts). Structural fingerprinting → pairwise distances → cluster
analysis published for all five rule_types.

Intervention proposal (5 candidates, top three surfaced):

- **I4 stratified rejection sampling** (~10 LOC in `sample_ruleset`):
  reject any rule already picked at a lower salt within the same
  rule_type. Predicted total floor at N=8: **0 pairs** (deterministic).
  Trade-off: breaks batch-v1 salt=0 byte-identity anchor for salts
  that would have inherited a picked-again rule; add a regression
  check.
- **I3 corpus-side D_minor seed** (validates cycle-13 handoff #1):
  extract harmonic rules from a non-F_major breadth seed. Predicted
  floor at N=8: 7.75 at H=10, 6.65 at H=20. Blocked on rated-audio
  egress OR requires synthetic breadth-seed expansion.
- **I5 content-aware tiebreak** (concept only): specify in a future
  cycle.

Rules schema (`scripts/rules/schema/rules_v1.json`) and rules ledger
(`data/rules/ledger.jsonl`) SHA-256 unchanged. Byte-deterministic × 2
on all 11 output artifacts. Integration test §29 (44 checks) all PASS.

### Clone 2 — M-TEX-1/panel/embedding/content-flip-analysis

Characterised the cycle-13-observed VGGish family-disagreement flip
via a systematic synthetic sweep across two axes: polyphony P1..P4
(mono → bass+piano → +drums → +other) and envelope E1..E4 (sustained
sine chords → decaying triad → percussion-heavy → harmonic-sustained-
only). Deterministic fluidsynth rendering (SF2 sha `74594e8f…1cb0`)
+ cycle-9 pinned DawDreamer chain applied verbatim (byte-duplicated
locally under `scripts/tex/content_flip/apply_pinned_chain.py`;
grep-verified zero import of `scripts.tex.render_effects_layered`).

**Regression contract held:** all three cycle-13 anchor TSV SHAs
reproduce byte-identically. Byte-determinism × 2: 17/17 SHAs match
under a fresh-subprocess second run.

**Flip characterisation:** `verdict = flip_polydimensional`,
`flip_dimension = both`. Rank-1 sign disagreement on *both* axes
(P1 mono, E1 sustained sine → agree = −1) transitioning to
agreement at rank-≥2. The two rank-1 disagreement points share
"spectral sparsity / tonal simplicity" as an interpretable common
factor — VGGish's AudioSet-trained embedding sits in a manifold-
sparse corner for these signals.

**Promotion recommendation: option (i)** — maintain VGGish at
/medium with a documented content-caveat pathway added to
`scripts/texture/panel.py:texture_distance` docstring. The
polydimensional finding precludes a single-variable gate; the
CLAP-anti-pattern-lock's concrete-alternative-fetch-path clause
cannot be satisfied under the current egress state (no Zenodo mirror
URL, no offline weights bundle SHA); VGGish tracks similarity
reliably in the manifold-typical region where nearly all M-TEX-1
comparisons will land.

Cycle-9 chain isolation grep-verified; SF2 pin `_assert_sf2` runs
before every render; interpreter guard on all six non-`__init__`
modules; non-factor AST isolation clean; panel contract per variant
satisfied (`embedding_rung = vggish` throughout, all metrics finite).
Integration test §30 (8 sub-sections) all PASS.

## Post-merge integration mechanics

- Adopted 7 orphan `scripts/rules/analysis/*.py` files from clone-1
  under `_infra/adopt-fanout-artifacts-m-gen-1-collision-floor-
  investigation`. Same adoption pattern as cycles 3/5/7/8/12/13.
- Registered `_plan/register-post-merge-integration-fork-855d4c2e9945`.
- Cross-branch test verification recorded under
  `_infra/cross-branch-integration-test-cycle14` (§28 + §29 + §30
  all present and green).
- Fork capstone under `_run/post-merge-integration-fork-855d4c2e9945`.
- Self-archive under `_archive/integration-scratch-fork-855d4c2e9945`
  supersedes fork-54a6c185816e integration driver (already stale).

## Validator state (post-merge)

| Check | Result |
|---|---|
| `promise_check` | **0 ERRORs**, 9 accepted WARNs (6 pre-existing trailing-slash canonicalization, 1 M-EAR-1 parent roll-up pending, 2 upstream `long_exposure/*` exemption pattern) |
| `tests/test_integration_cross_branch.py` | PASS (0 failures across §1–§30; §28/§29/§30 new this cycle) |
| `tests/test_ledger_writer_validation.py` | 18/18 pass (cases 14–18 new this cycle) |
| `tests/test_fanout_concat_validation.py` | 13/13 pass (cases 9, 11–13 new this cycle) |
| Ledger row count | 296 → 301 (+5 rollup events) |

## Handoff to cycle 15 researcher

1. **Ship I4 stratified rejection sampling** in `sample_ruleset` (~10
   LOC) with a batch-v1 salt=0 anchor-regression guard. Predicted
   collision floor at N=8: 0 pairs (deterministic). This is the
   biggest single collision-floor lever available and mechanically
   cheaper than I3 corpus expansion.

2. **State-transition validator (clone-0 follow-up b)** — extend
   SSoT `_ledger_schema` with per-milestone status-transition
   check: `validated → in-progress` requires an intervening
   `reopened`. Catches the cycle-13 line-250 mechanism that the
   cycle-14 field-type + enum check cannot express. Should not sit
   indefinitely — surfaced by clone-0's honest §2b analysis.

3. **Docstring caveat one-liner on `scripts/texture/panel.py:
   texture_distance`** — clone-2's option-(i) recommendation ships
   only the report; the actual docstring edit is a separate cycle-15
   docs-only PR (drafted text is in `docs/tex_embedding_content_flip_
   report.md` §8). Should not sequence against clone-2's closure.

4. **Optional-field enumeration under SSoT type-checking (clone-0
   follow-up a)** — cycle-14 hardened only `supersedes_path` and
   `status`; `assessor`, `agent`, `run_id` regex, `event_id`
   UUID5-vs-arbitrary remain untyped. Lower priority than the
   state-transition class.

5. **Drift-class enumeration index (clone-0 follow-up c)** — a
   documented registry of drift classes closed / deferred /
   suspected-but-unproven. Becomes the retrospective spine for
   cycle 15+. Every cycle since 8 has found a new drift class the
   current validator did not cover; the pattern is now explicit
   enough that a registry helps.

6. **I3 D_minor breadth seed** (validates cycle-13 handoff pointer 1
   and clone-1 intervention I3): if a synthetic D_minor 30-s seed
   can be authored deterministically (no rated audio dependency),
   extracting its harmonic rules would break the F_major dominance
   and give a second lever alongside I4. Predicted floor at H=10: 7.75.

7. **M-EAR-1 parent roll-up** — sub-milestones
   (preparation/features, preparation/model, preparation/leak-test)
   all validated for several cycles now. The standing "plan
   milestone 'M-EAR-1' has no ledger events yet" WARN clears with a
   single parent event. Cheap to close.

8. **VGGish content-caveat surfacing at M-GEN-1 scoring time** —
   clone-2's mechanism (spectral sparsity / tonal simplicity → less
   trustworthy VGGish rung reading). If any generated song lands in
   that manifold-sparse corner, the score's ear/embedding column
   should carry the caveat rather than silently down-weight the
   listener's trust.

9. **Cycle-15 diagnostic-ladder starting rung**: if a fourth drift
   class appears at post-merge integration, start at Rung 3 (does
   the tightened validator catch it, and if not, why?) rather than
   at Rung 1 (is the ledger corrupt at all?). Clone-0's report §7
   formalises this.

10. **CLAP anti-pattern remains locked**: reopening requires a
    concrete alternative fetch-path (Zenodo mirror URL, offline
    weights bundle SHA, or egress-relaxation to a specific host).
    Egress-blocked state alone is not sufficient. Documented in
    clone-2 report §8.

## Environment (unchanged since cycle 10)

- Python 3.11.15, `/usr/bin/python3` interpreter guards enforced.
- torch 2.13.0+cpu, torchvision 0.28.0 (register_fake workaround),
  numpy 1.26.4, music21 9.1.0, mir_eval 0.8.2, mscore3 3.2.3
  (`QT_QPA_PLATFORM=offscreen`), fluidsynth (Debian) with pinned
  SF2 `74594e8f…1cb0`, DawDreamer 0.9.0, Surge XT Effects.vst3 at
  `/usr/lib/vst3/`, basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`.
- Single-thread BLAS pins (OMP/MKL/OPENBLAS=1) throughout.
- Egress: still blocked per `corpus/CORPUS_STATUS.md`.

## Session references

- Clone-0: researchers `eb4629c8`, `040a1c86`; workers `8b8714d1`,
  `e63ca7a2`; auditors `6da7d443`, `2046c2c9`.
- Clone-1: worker + auditor pair (see clone-1 merge_report shadow).
- Clone-2: researcher `60fb794d`, worker `7be11a0b`, auditor `4d7421a0`.
