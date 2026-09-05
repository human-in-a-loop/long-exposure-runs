# Delta Outline — v4 Closure Campaign Revision

**Delta mode.** A committed baseline `final_report.md` exists and
covers the v3 pipeline end-state (ingestion → separation →
transcription → merged-score/rules → DAW/palette determinism →
texture panel → CORN ear → recreation/generation/collision arc,
plus references). The v4 closure campaign — a follow-on effort
that sits on top of the v3 pipeline and pursues per-instrument
sound-matching, a full-song showcase, a new rules layer, a
lightweight exemplar ear, and a seeded generator — is not covered
in the baseline. This revision preserves the baseline v3 material
verbatim wherever the cycle reports do not revise it, and inserts
one new top-level section for the v4 closure campaign together
with light updates to the Abstract, Introduction end-state, and
Conclusions/Future-Work sections.

## Intended audience

A reader with domain expertise in music information retrieval,
audio signal processing, and applied ML (transcription, source
separation, embedding-space evaluation, ordinal regression). No
knowledge is assumed of the run's internal process, milestone
identifiers, cycle numbering, ledger status vocabulary, agent
cadence, or workspace bookkeeping — every such term is translated
into plain description at the point of use. Field-standard
notation and acronyms (F1, mel-L1, CLAP, VGGish, LUFS-I, CORN,
MIDI, LV2/VST3) are used without gloss where already introduced
by the baseline.

## Section-by-section change map

| §   | Title (baseline)                                              | Delta action              | Sources                                                                          |
|-----|---------------------------------------------------------------|---------------------------|----------------------------------------------------------------------------------|
| —   | YAML front matter                                             | preserve                  | —                                                                                |
| —   | Abstract                                                      | **update** (append v4)    | audit summary; §9 (new)                                                          |
| 1   | Introduction (bet, three decisions, pipeline shape, end-state)| **update §1.4 end-state** | audit summary                                                                    |
| 2   | Ingestion, Classification, Provenance, Egress-Ready SM        | preserve                  | —                                                                                |
| 3   | Source Separation and Transcription                           | preserve                  | —                                                                                |
| 4   | The Merged Score, MuseScore Bridge, Rules Ledger              | preserve                  | —                                                                                |
| 5   | DAW Stack and Palette-Instrument Determinism Arc              | preserve                  | —                                                                                |
| 6   | The Texture Panel (M-TEX-1)                                   | preserve                  | —                                                                                |
| 7   | The Ear Model (M-EAR-1)                                       | preserve                  | —                                                                                |
| 8   | Recreation, Accurate-Small-Set, Generation, Collision Arc     | preserve                  | —                                                                                |
| **9 (NEW)** | **The v4 Closure Campaign**                           | **new section**           | cycle reports 10–12, 13–15, 16–18; audit summary; ledger causal summary          |
| 10 (was 9)  | Conclusions, Honest Limits, Future Work                 | **update**                | audit summary (residual_debt, future_work); new §9                              |
| 11 (was 10) | References                                              | preserve                  | —                                                                                |

The old §9 is renumbered to §10; the old §10 to §11. Cross-refs
inside preserved sections still resolve because they use section
numbers `2` through `8` that are unaffected.

## New section 9 — subsection outline

**9.1 Framing: closure after v3.** Why a distinct v4 campaign
exists on top of the v3 pipeline (operator ear on the v3
Chicken Grease reconstruction landed; the closure mandate is
per-instrument sound-matching, one full-song showcase, a rules
artifact, a lightweight exemplar ear, and a small generation
batch — then end the run).
*Sources:* v4 campaign prompt; audit summary framing;
report_cycles_16-18 §Introduction.

**9.2 The determinism certificate (M-V4-CERT).** Two `--no-cache`
Chicken Grease runs produced byte-identical delivery WAVs; the
certificate was completed and validated. State the acceptance
shape and the recorded verdict, without cycle vocabulary.
*Sources:* audit summary `plan_milestone_state.M-V4-CERT-1`;
prompt §"Read before your first cycle".

**9.3 Per-instrument sound matching (M-V4-PROFILES) — the
Chicken Grease arc.** The two-phase policy (stochastic search,
pinned deterministic replay). Report the closed per-instrument
arcs on Chicken Grease: bass accepted (hybrid directive); drums
ruled out on both SoundFont and stem-sampled families; guitar
ruled out on both families; piano and other-residual grounded
null (sub-silence stems); vocals under pre-existing hybrid
overlay. State the composite objective, the two thresholds
(0.60 accept / 0.40 reject floor on VGGish embedding-cosine),
and the refuse-and-substitute policy for `EXHAUSTED_NO_CONFIRMED`
arcs. Include the pinned-profile schema (M-V4-RULES-1/pinned-
profile-schema-v1) as the artefact discipline supporting replay.
*Sources:* report_cycles_10-12; report_cycles_13-15; ledger
causal chains for `cg-guitar-family2-stem-sampled`,
`cg-guitar-family2-replay-proof`; audit summary
`plan_milestone_state`.

**9.4 The M-V4-SHOWCASE Chicken Grease A/B full-song render.**
Delivery of `cg_ab_mix.wav` with manifest and replay proof;
byte-identity confirmed on re-render. State that the milestone
lands on internal gates and that the operator listening verdict
is stated policy, not a workflow defect.
*Sources:* ledger causal chain
`M-V4-SHOWCASE-1/cg-ab-full-render`; report_cycles_16-18 §CG
A/B mix; audit summary
`plan_milestone_state.M-V4-SHOWCASE-1/cg-ab-full-render`.

**9.5 The four remaining focus songs (WIG, Rome, Disco A,
Peach Dream) and the metric-semantics escalation.** Skeleton
stem manifests are in place for all four songs; no per-instrument
sweeps have been run against them. The blocker is a candid
correctness concern about the composite objective: the
`embedding_cos_vggish` field is documented and computed as a
*distance*, but downstream decision protocols evaluate the
0.60 accept and 0.40 reject bars as if it were a *similarity*.
Two remediation paths (A: keep as distance and invert the
threshold semantics; B: apply `1 - distance` correction in one
place, re-issue the determinism certificate, and re-adjudicate
every prior Chicken Grease family verdict) are named and
awaiting operator direction. Explain why the CG A/B mix
delivery is safe under either path — the arcs it depends on
resolve to *refuse and substitute the operator-heard stem*
under both interpretations — while the four unopened songs
must wait for the choice before sweeps commit.
*Sources:* audit summary
`_manager/M-V4-METRIC-SEMANTICS-c16`; report_cycles_13-15
§"latent correctness concern about the sign convention"; audit
summary `residual_debt[0]`.

**9.6 The v4 rules layer (M-V4-RULES): current state.** The
c20 rules extractor scaffold validated at scaffold-level; a
substantive extraction pass followed on disk (c21+) that has
not yet been formally registered as a substantive-verdict.
Report the state honestly: the pinned-profile schema
(v4 sound-matching layer) is validated and load-bearing for
M-V4-PROFILES replay; the substantive rules extraction is
present as code and outputs but its verdict against the
M-V4-RULES success criteria has not been issued. This is the
"silent supersession" gap named in the residual-debt list.
*Sources:* ledger `M-V4-RULES-1/scaffold-c20` and
`pinned-profile-schema-v1`; audit summary
`plan_milestone_state.M-V4-RULES-1/scaffold-c20`; residual_debt[1].

**9.7 Not started: exemplar ear (M-V4-EAR), seeded generator
(M-V4-GEN), campaign closure (M-V4-CLOSE).** State why these
have not begun (EAR does not depend on metric semantics but was
scheduled after PROFILES completion; GEN depends on both a
substantive rules verdict and EAR; CLOSE depends on all v4
predecessors). Enumerate the acceptance shape each was designed
to meet, so a resumption is a matter of execution rather than
re-planning.
*Sources:* audit summary
`plan_milestone_state.{M-V4-EAR-1,M-V4-GEN-1,M-V4-CLOSE-1}`;
v4 campaign prompt milestone specs.

## Updates to preserved sections

**Abstract.** Append one paragraph describing the v4 closure
campaign: certificate validated; per-instrument Chicken Grease
arcs closed with two acceptances (bass hybrid, vocals hybrid),
three refuse-and-substitute rulings (drums, guitar, other-
residual/piano null); Chicken Grease A/B full-song mix delivered
under a permanent read-only anchor pending operator ear; four
remaining focus songs held behind a candid metric-semantics
escalation; exemplar ear, seeded generator, and campaign
closure not started.

**§1.4 End-state at a glance.** Replace the milestone
distribution bullet with the current audit's plan-of-record
counts translated to plain language ("of 58 v4 plan entries:
47 confirmed, 4 not started, 3 deferred, 1 in progress, 1
awaiting operator, 1 replaced by later work without a formal
supersede event"), refresh the findings line (0 critical, 2
moderate, 5 minor), refresh the promise-check state, and add
"Open threads" bullets for (i) the metric-semantics
escalation, (ii) four focus-song sweeps queued behind (i),
(iii) the substantive v4-rules verdict, and (iv) exemplar ear /
generator / campaign closure.

**§10 (formerly §9) Conclusions, Honest Limits, and Future
Work.** Replace the "actionable next steps" list with the
audit's `future_work` items, in the sequence the auditor
recommends: (a) operator selects between metric-semantics
Path A and Path B; (b) v4 rules author emits the substantive
verdict row and the supersedes event that the c21+ extractor
implicitly earned; (c) after (a) resolves, run stage-1/stage-2
sweeps on WIG/Rome/Disco A/Peach Dream under the sweep-storage
hygiene protocol validated on Chicken Grease; (d) build the
lightweight exemplar ear against Chicken Grease + Molasses +
Essence + Desire + Peach Dream; (e) build the seeded generator
program per its specification; (f) execute the campaign closure
roll-up. Retain the v3-era future-work items (probe-kind, gen
audio regen, plan-ledger supersede, etc.) as a preserved
sublist so no prior commitment is dropped.

## Narrative arc

The report keeps its v3 shape (pipeline flow, sub-topic per
section, honest ends) and inserts the v4 closure campaign as a
single top-level section that reads chronologically only within
its subsections. The reader arrives at §9 already knowing what
the pipeline can do; §9 states what the closure campaign asked
of it, which parts of the closure are done, and where the
remaining work is genuinely blocked (metric-semantics
escalation) versus not-yet-started (ear/generator/closure).

## Stage assignments for the body pass

- **Stage 2:** Write the entire new §9 (subsections 9.1–9.7).
  This is the largest single delta and belongs in one stage so
  the internal cross-references and terminology stay coherent.
- **Stage 3:** Update §1.4 End-state at a glance in place.
  Preserve §1.1–§1.3 verbatim.
- **Stage 4:** Update §10 Conclusions, Honest Limits, and
  Future Work: rewrite §10.1 "What is done" so it lists v3 as
  the completed pipeline foundation and v4 as the closure
  campaign in progress; rewrite §10.2 "Two live constraints"
  as three (add metric-semantics); rewrite §10.3 "Actionable
  next steps" per the audit's `future_work` sequence;
  preserve §10.4 verbatim.
- **Stage 5:** Update the Abstract: append the v4 paragraph;
  otherwise preserve.
- **Stage 6:** Renumber §9→§10, §10→§11. No prose changes.
  (Kept as a dedicated stage because a renumbering pass is the
  most error-prone edit and deserves isolation before finalize.)
- **Stage 7:** Finalize into `final_report.md`, refresh
  MANIFEST "Key Files" section.

## Deliberately excluded from the report

- Cycle numbers, session UUIDs, run-ids, agent labels, and
  ledger status vocabulary (`validated`, `superseded_implicit`,
  `action_required`, etc.). Every such term is translated at
  the point of use per the reporter translation table.
- The v3-heartbeat cycle reports (`report_cycles_17-19`,
  `20-22`, `23-25`, `26-28`, `29-31`, `32-34`, `35-37`,
  `38-40`, `43-45`, `46-48`, `49-51`, `52-54`, `56-58`,
  `61-63`) are v3-campaign material already synthesised into
  the baseline body and are not reopened in this delta.
- The v3-era clone reports (`report_cycles_*_clone_*.md`)
  are also v3 material and are preserved through the baseline.
- Run-mechanics artifacts (`run_mode.json`,
  `final_report.committed`) are working surfaces and do not
  appear in the report.
