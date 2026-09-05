# Delta Outline — v4 Closure Campaign Terminal Update

**Delta mode.** A committed baseline `final_report.md` already
covers both the v3 pipeline (§§2–8) and the v4 closure campaign
in progress (§9), and its §9.7 records the exemplar ear (M-V4-EAR),
the seeded generator (M-V4-GEN), and the campaign closure roll-up
(M-V4-CLOSE) as **not started**. The single new source in this
delta scope — the cycle-31 closure report — carries all three
milestones to terminal state on disk (with a candid bookkeeping
gap: their landing events were never registered in the campaign
ledger). It also promotes the v4 rules layer from
scaffold-only to a substantive-extraction landing (97 rules + two
generative models across seven byte-deterministic artifacts).

This revision preserves every baseline section verbatim except:
Abstract (append terminal-close paragraph); §1.4 end-state (refresh
counts, add "closed cleanly" statement, refresh open-threads list);
§9.6 rules (upgrade from scaffold-only to substantive-landing with
bookkeeping caveat); §9.7 (rewrite entirely — EAR/GEN/CLOSE landed
with byte-verified deliverables); §10.1 "What is done" (add v4 EAR,
GEN, CLOSE deliverables); §10.2 "Three live constraints" (recast:
metric-semantics still live; generator pass-rate becomes the second
live constraint; ear-backbone ensemble becomes the third); §10.3
"Actionable next steps" (replace with the audit's `future_work`
list); §10.4 preserve verbatim.

## Intended audience

A reader with domain expertise in music information retrieval,
audio signal processing, and applied ML (transcription, source
separation, embedding-space evaluation, ordinal regression). No
knowledge is assumed of the run's internal process, milestone
identifiers, cycle numbering, ledger status vocabulary, agent
cadence, or workspace bookkeeping — every such term is translated
into plain description at the point of use. Field-standard
notation and acronyms (F1, mel-L1, CLAP, VGGish, LUFS-I, CORN,
MIDI, LV2/VST3, cellular automaton, variable-order Markov) are
used without gloss where already introduced by the baseline.

## Section-by-section change map

| §    | Title (baseline)                                         | Delta action                        | Sources                              |
|------|----------------------------------------------------------|-------------------------------------|--------------------------------------|
| —    | YAML front matter                                        | preserve                            | —                                    |
| —    | Abstract                                                 | **append** terminal-close paragraph | c31 closure report; audit summary    |
| 1    | Introduction §§1.1–1.3                                   | preserve                            | —                                    |
| 1.4  | End-state at a glance                                    | **refresh**                         | audit headline; c31 closure report   |
| 2–8  | Ingestion → Recreation/Generation/Collision              | preserve                            | —                                    |
| 9.1–9.5 | Framing; certificate; per-instrument arcs; showcase; metric-semantics | preserve | —                              |
| 9.6  | The v4 rules layer                                       | **upgrade** to substantive landing  | c31 closure report §Findings         |
| 9.7  | Not started: EAR, GEN, CLOSE                             | **rewrite as "Landed on disk"**     | c31 closure report §Findings + Appendix; audit summary residual_debt |
| 10.1 | What is done                                             | **update**                          | c31 closure report; audit summary    |
| 10.2 | The three live constraints                               | **recast**                          | c31 closure report §Open questions   |
| 10.3 | Actionable next steps                                    | **replace**                         | audit `future_work`; c31 §Open       |
| 10.4 | No new hypotheses                                        | preserve                            | —                                    |
| 11   | References                                               | preserve                            | —                                    |

## Delta content per changed subsection

### Abstract — append one paragraph

Terminal state: the closure campaign ended cleanly. Determinism
certificate holds (byte-equal reconstructions under a pinned
environment). Chicken Grease profile suite terminal per §9.3. A/B
showcase rendered and byte-proven (operator ear remains the LANDS
gate per policy). Rules layer: 97 style rules
(23 harmonic + 23 rhythmic + 23 melodic + 23 form + 5 arrangement)
plus a per-song / per-band statistical model and a per-instrument
radius-1 one-dimensional cellular-automaton + order-2 variable-order
Markov model, byte-deterministic across seven artifacts. Exemplar
ear meets the sanity bar (5/5 focus songs score ≥6 on
leave-one-out, none <5.5). Seeded generator delivered three passers
plus a cross-song hybrid at the eight-iteration stall rule. Two
honest carries: four of the five focus songs remain skeleton-only
because their per-instrument sweeps are blocked by an
operator-authority question about a distance-vs-similarity sign
convention in the composite metric; and the closure cycle's
substantive work landed on disk without corresponding events in the
campaign ledger (single-row bookkeeping recovery).

### §1.4 End-state at a glance — refresh

Refresh the plan-of-record counts to plain language ("47 confirmed
at high confidence, 4 recorded as not-yet-registered in the ledger
despite on-disk landings, 3 deferred, 1 in progress, 1 awaiting
operator judgment, 1 replaced by later work without a formal
supersede event"); refresh findings line to "zero critical, one
moderate, one minor"; keep promise-check "green"; refresh
open-threads bullets to: (i) metric-semantics adjudication (still
live), (ii) four focus-song sweeps queued behind (i), (iii)
bookkeeping recovery for the four closure-cycle landings, (iv)
optional ear-backbone ensemble (CLAP install). Add one closing
sentence: the run ended cleanly at its seventh milestone without
idling on the operator.

### §9.6 The v4 rules layer — upgrade

Replace "scaffold validated; substantive extraction implicit and
unregistered" narrative with: substantive extraction landed and
byte-verified. Rules artifact: 97 rules with the exact
23 + 23 + 23 + 23 + 5 distribution across harmonic, rhythmic,
melodic, form, and arrangement categories. Two generative models
alongside: Model A, a per-song / per-band statistical model
(`statistical_model.json`, 21,983 bytes); Model B, a per-instrument
sequence model combining a radius-1 one-dimensional cellular
automaton with an order-2 variable-order Markov model
(`sequence_model.json`, 30,897 bytes). Byte-determinism holds on
two independent runs under a canonical seven-key environment pin
across all seven produced artifacts (rules, both models, audio
descriptors, CA-retention summary, manifest, replay proof).
Corpus-size honesty: of 23 non-empty instrument cells fed to the
cellular-automaton model, 13 were retained by the post-fit
degeneracy check; 10 collapsed to all-off or all-on attractors
under the 8-step self-generation retention test. Both models
remain available to the generator, which falls back to the Markov
model or hash-driven sampling on non-retained cells. Close with
the bookkeeping caveat: the landing was not registered in the
campaign ledger; recovery is a single row referencing the on-disk
SHAs.

### §9.7 Rewrite — from "Not started" to "Landed on disk"

Retitle the section "**Exemplar ear, seeded generator, and
campaign closure — landed on disk**" and rewrite as three
substantive paragraphs:

**Lightweight exemplar ear.** Implemented as a leave-one-out
top-*k* window similarity over VGGish embeddings with a linear
anchor on the leave-one-out mean and a noise floor. Five focus
exemplars score (1–7 scale): Chicken Grease 7.0, Peach Dream 7.0,
Molasses 7.0, Essence 7.0, Desire 6.16. Five of five clear the
sanity bar of 6; none falls below 5.5. Band-4 spot check on three
additional songs: Aguanile 5.18 (clearly lower), Wagon Wheel 6.12
(near Desire), Stay (Live) 7.0 (saturating — honestly disclosed
as VGGish timbre-forgiving behaviour on decoded audio when a probe
song shares R&B/pop timbral character with the exemplar pool). The
originally-planned CLAP + VGGish ensemble is unavailable in this
environment because `torchvision` installation fails on a missing
`nms` operator (spec explicitly permits and documents the
VGGish-only fallback). Byte-determinism holds across two runs when
TensorFlow's oneDNN optimisations are pinned off. Named artifacts:
`ear_scores.json` (SHA `b2f5e9bd…`), exemplar and band-4
embeddings `.npz`, manifest, replay proof.

**Seeded generator.** Combines Model A scaffolding with Model B
bar-to-bar sequencing under deterministic SHA-256-derived index
sampling — no pseudo-random-number generator is imported. The
pre-declared stall rule was eight iterations. Outcome: three
passers at or above the ear-score bar of six (6.9440, 6.7938,
6.2886) plus two near-misses (5.3804, 5.3196); the best five were
delivered and iteration stopped per the stall rule. A cross-song
interpolation hybrid using Chicken Grease as donor A (key and
tempo) and Peach Dream as donor B (cellular-automaton tables)
scored 5.9394. Candidate root causes for 3-of-5 rather than
5-of-5, in decreasing order of impact: VGGish-only ear has narrower
discriminating dimensionality on synthesised content than the CLAP
ensemble would provide; fluidsynth-rendered generated songs share
less timbral space with the human-performed exemplars than the
exemplars share with each other; 16-bar sections may
under-represent the strong stretches that the top-50% window
statistic rewards; and the cellular-automaton retention of 13/23
pushes ten instrument cells onto the fallback chain. Named
artifacts: `data/v4/generated/batch_full/{batch_report.json,
iter_01..08/}` plus `hybrid_cg_x_pd/` with per-iteration manifests
carrying MIDI SHA, song WAV SHA, generator hash, rules hash,
donor, environment pin, and ear score.

**Campaign closure roll-up.** `docs/v4_closure_completion_report.md`
(14,484 bytes) was published with a milestone table, a deliverables
index by artifact SHA, a certificate-status section, an
honest-gaps section, and an inline operator hand-off.
`docs/OPERATOR_DECISIONS.md` and `docs/CODEBASE_GUIDE.md` were
touched to record the closure verdict and add the new module
locations. Read-only anchors — the entire v3 spine, the v2
recreation tree, the terminal §2 of the determinism certificate,
every prior CG-arc profile and replay-proof anchor, the earlier
showcase render, and the operator-authority escalation JSON —
were not modified. Independent audit this cycle byte-verified every
referenced SHA, reconciled the rule counts and model sizes,
confirmed `all_equal=true` on the seven rules artifacts, and
reconciled ear scores against the sanity-bar arithmetic; verdict
was clean-close with zero critical findings and two moderate
process observations (both bookkeeping, non-blocking).

Close the section with a candid parity note: the four milestones
above (rules substantive extraction, ear, generator, closure)
landed on disk without corresponding registration events in the
campaign ledger. All are byte-verifiable from the SHAs listed
above; the bookkeeping recovery is a single row per milestone if
operator-desired.

### §10.1 What is done — update

Add a fourth paragraph under the v4 layer summarising: rules
layer landed with 97 rules and two generative models; exemplar
ear meets the sanity bar; seeded generator delivered three
passers plus a cross-song hybrid; closure report published; the
run ended cleanly at its seventh milestone.

### §10.2 The three live constraints — recast

Live constraints after terminal close:
1. **Metric-semantics adjudication** (unchanged) — the composite
   metric's `embedding_cos_vggish` field is empirically a distance
   but two remediation paths (invert thresholds vs. correct
   composite arithmetic) both violate operator-anchored contracts
   under agent-picks invariants. One operator decision unblocks
   the four non-CG focus-song sweeps.
2. **Generator pass rate** — 3/5 rather than 5/5 at the
   eight-iteration stall. Not a defect; a corpus-and-backbone
   finding with four candidate improvements (CLAP-ensemble ear,
   richer corpus for better CA retention, longer sections,
   additional seeds against a richer rules artifact).
3. **Ear-backbone ensemble unavailable** — `torchvision`
   installation fails on missing `nms` operator; VGGish-only
   fallback is spec-permitted but leaves a saturating case
   (Stay (Live) 7.0) that the CLAP ensemble would disambiguate.

### §10.3 Actionable next steps — replace with audit `future_work`

In the sequence the auditor recommends:
(a) append the four missing completion events (rules substantive,
ear, generator, closure) with the on-disk SHAs the closure report
already cites — pure bookkeeping, closes the ledger-vs-disk parity
gap;
(b) persist the closure-cycle auditor's findings artifact on disk
under `audits/final/stages/` so the clean-close verdict is
independently re-auditable;
(c) operator picks between metric-semantics Path A
(distance-inverted thresholds) and Path B (similarity numeric
fix); acceptance event follows;
(d) record the post-hoc operator listening verdict on the
Chicken Grease A/B mix, closing the standing showcase-acceptance
fork;
(e) after (c) resolves, run stage-1 per-instrument sweeps on
Wonderful It Is, Rome, Peach Dream, and Disco A under the
sweep-storage hygiene protocol validated on Chicken Grease;
(f) formally reconcile the v4 rules milestone status by
superseding the scaffold row with a substantive-extraction landing
row;
(g) install a working `torchvision` build to unlock the
CLAP + VGGish ear ensemble;
(h) re-run the seeded generator once the ear ensemble is
available or once seeds are enriched — the generator is a pure
function of (rules, seed, config) so no redesign is needed to
improve the pass rate.

Retain the v3-era future-work items (probe-kind, generation-audio
regeneration, plan-ledger supersede on merged-score cutovers,
etc.) as a preserved sublist so no prior commitment is dropped.

## Narrative arc

The report keeps its v3 shape (pipeline flow, sub-topic per
section, honest ends). §9 continues to read chronologically within
its subsections, but §9.6 now reports a substantive rules landing
rather than a scaffold-only state, and §9.7 flips from "not
started" to "landed on disk with a candid parity caveat." §10 is
recast to reflect terminal close: three live constraints (only one
of which — metric-semantics — genuinely blocks agent-side
resumption), and an eight-item future-work sequence anchored to
the audit's own recommendations. §10.4 preserves the "no new
hypotheses" closing.

## Stage assignments for the body pass

- **Stage 2 (body):** Edit §9.6 (upgrade to substantive landing);
  rewrite §9.7 in full (retitle, three substantive paragraphs,
  bookkeeping caveat); update §10.1 (add v4 terminal paragraph);
  recast §10.2 (three constraints); replace §10.3 (audit
  `future_work` sequence with v3-era sublist preserved); append
  terminal-close paragraph to Abstract; refresh §1.4 counts,
  findings, open-threads, and closing sentence.
- **Stage 3 (finalize):** Assemble final_report.md from the edited
  draft (frontmatter, abstract, body, references preserved);
  update MANIFEST.md "Key Files" section per the closure report's
  artifact list.

## Deliberately excluded from the report

- Cycle numbers, session UUIDs, run-ids, agent labels, and ledger
  status vocabulary (`validated`, `superseded_implicit`,
  `action_required`, `not-started`, etc.). Every such term is
  translated at the point of use per the reporter translation
  table.
- Process observations that appear only in the auditor's report
  (worker-vs-auditor role split, filesystem-probe counts,
  self-attestation vs. AST scan) — these are harness observations,
  not research findings.
- Run-mechanics artifacts (`run_mode.json`,
  `final_report.committed`, per-stage draft files) — working
  surfaces, not deliverables.
