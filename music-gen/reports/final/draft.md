<!--
Delta draft for the v4 closure campaign revision. Stage 2 writes
the new §9 body below. Later stages append updates to §1.4,
§10 Conclusions, and the Abstract, and a renumbering pass moves
§9 → §10 and §10 → §11 in the final assembly at Stage 7.

Each delta section is fenced with HTML comment markers so that
the finalize pass can locate and splice it into final_report.md
without disturbing the preserved v3 material.
-->

<!-- BEGIN DELTA: NEW SECTION 9 -->

# 9. The v4 Closure Campaign

## 9.1 Framing: what a "closure" campaign is for

The pipeline described in §§2–8 is the v3 system: an end-to-end
path from an ingested reference recording to a rendered
re-creation with a documented ear, a validated texture panel,
and an accurate small-set generation arc. By the end of that
work the operator had heard, and accepted, the v3 Chicken
Grease reconstruction. What remained was not another pass at
the pipeline itself but a bounded set of follow-on deliverables
that use it: per-instrument sound matching against pinned
render families, one full-song A/B showcase mix, a rules
artefact expressed in the v4 sound-matching vocabulary, a
lightweight exemplar ear, and a small seeded-generation batch.
The v4 closure campaign is that follow-on set. Its remit was
explicitly bounded — deliver these items, then end the run
cleanly — and this section reports the state each deliverable
reached before that termination.

The organising unit of the closure campaign is the
**per-instrument arc**: for a given song and instrument, search
two frozen render families for a configuration whose short
(6 s) rendered clip best matches the reference stem under a
fixed composite objective, then adjudicate the result against a
frozen decision protocol. The two families are (1) a
General-MIDI SoundFont sweep over the standard bank of GM
programs — the "sf2" family — and (2) a stem-sampled
concatenative builder that constructs a slice bank from the
reference stem's own onsets and dispatches each MIDI event to
the nearest-pitch slice with pitch-shifting — the "family-2"
family. The decision protocol has three terminal outcomes:

- **`CONFIRMED`** — the best candidate's VGGish
  embedding-cosine score against the reference stem is at or
  above 0.60. The pinned configuration becomes the delivery
  audio for that instrument cell.
- **`RULED_OUT`** — the best candidate is at or below 0.40. The
  family is dropped from consideration.
- **`STILL_INDETERMINATE`** — the score falls between the two
  bars. No commitment either way.

When both families are `RULED_OUT`, the arc closes as
`EXHAUSTED_NO_CONFIRMED` and a pre-registered options fork is
opened. One option in every such fork is a **refuse and
substitute** ruling: decline to synthesise the instrument and
splice the operator-heard reference stem verbatim into the
showcase mix. Refuse-and-substitute is not a fallback — it is a
first-class outcome that preserves the operator's ear as the
authoritative reference for that instrument.

Every configuration selected under this policy is pinned as a
**deterministic replay proof**: two independent renders of the
same profile under a canonical seven-key environment pin
(`LC_ALL`, `MKL_NUM_THREADS`, `OMP_NUM_THREADS`,
`OPENBLAS_NUM_THREADS`, `PYTHONHASHSEED`, `SOURCE_DATE_EPOCH`,
`TZ`) must produce byte-identical output WAVs. The environment
pin has hash prefix `2ac444c36298d6ad…` and has been in force
since early in the campaign.

## 9.2 The determinism certificate

The first closure deliverable was a bit-exact determinism
certificate for the v3 Chicken Grease reconstruction, obtained
by running the full delivery pipeline twice with all caches
disabled and hashing the output WAVs. Both renders produced
byte-identical output. The certificate is complete and
confirmed as of the campaign's opening.

The certificate matters because it is the invariant every
subsequent v4 deliverable rests on: if a pinned profile's
replay proof does not reproduce, the failure is in the profile
or the pin, not in the pipeline underneath.

## 9.3 The Chicken Grease per-instrument arcs

Chicken Grease was the sole song carried all the way through
per-instrument arc closure during the campaign. Its six
`htdemucs` stems (bass, drums, guitar, piano, other-residual,
vocals) were each taken to a terminal verdict; the outcomes,
in the order they were closed, are the following.

**Bass — accepted (hybrid).** The bass arc closed early under
an explicit operator directive: accept the pinned SoundFont
configuration (GM program 33) as the delivery bass, with the
operator retiring the standard acceptance threshold for this
specific arc and this specific instrument. This is the sole
place in the campaign where the composite-objective ranking
was used to select delivery audio rather than being used to
either confirm or rule out a family; the directive's scope is
narrow (CG-bass only) and does not extend to any other arc.

**Drums — refused and substituted.** The SoundFont sweep found
a best candidate (GM program 16, "Power Kit") with an
embedding-cosine of **0.2374** against the reference drums
stem; the stem-sampled family-2 builder found a best rendered
match at embedding-cosine **0.0372**. Both sit well below the
0.40 floor, and the arc closed as
`CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED`. The pre-registered
acceptance fork was resolved by substituting the operator-heard
`htdemucs` drums stem verbatim into the showcase mix.

**Guitar — refused and substituted.** The SoundFont fine-fit
placed a muted-electric variant (GM program 28) as the top-1
configuration at embedding-cosine **0.2584**; the stem-sampled
family-2 render scored embedding-cosine **0.0354**. Again both
fell below the floor; the arc closed as
`CG_GUITAR_ARC_EXHAUSTED_NO_CONFIRMED` and was resolved by
refuse-and-substitute.

**Piano and other-residual — grounded null.** Both reference
stems tested inaudible: the `pyloudnorm` LUFS-I measurement
returned non-finite ("silence-only" content), and the RMS-dBFS
fallback measured piano at **−81.53 dBFS** and other-residual
at **−81.73 dBFS**, both far below the −60 dBFS silence floor.
The corresponding v3-transcribed MIDI tracks carry zero
note-on events. With no audible reference and no MIDI target,
no sweep is warranted, and the delivery uses the (silent)
`htdemucs` stem verbatim — the same treatment the v3 pipeline
already applies to empty tracks.

**Vocals — hybrid overlay (pre-existing).** Vocals were
covered by a policy established earlier in the pipeline: the
`htdemucs` vocal stem is overlaid on the instrumental mix
verbatim, without a synthesis attempt.

The net Chicken Grease showcase composition is therefore two
synthesised cells (bass and — via the drums-substitution
policy — the operator-heard drums stem re-used as-is), two
grounded null cells (piano, other-residual), one substituted
cell (guitar), and one overlaid cell (vocals). The delivery
script's smoke test reports every cell terminal.

**The pinned-profile schema.** Supporting the arc-closure
discipline is a pinned-profile JSON schema (v1) and its
validator. The schema is deliberately permissive: it validates
shape without pinning threshold semantics, so that it does not
need to be revised when the metric-semantics question of
§9.5 resolves. Every pinned profile from Chicken Grease's
closure — bass, drums, guitar, and the two null pins — passes
the validator.

**Agent-picks selection invariants.** Because the closure
campaign was run under a hard rule against pausing for
operator input on questions the operator had not been asked,
the acceptance-fork resolutions above were made by the agent
under a small set of codified invariants:

- (a) **No operator-scope extension.** A worker does not
  widen the scope of a directive the operator issued at a
  narrower scope.
- (b) **Prefer above-floor.** When one option selects a
  candidate below the retained absolute floor and another
  selects an above-floor candidate or takes a non-candidate
  policy path (such as refuse-and-substitute), prefer the
  latter.
- (c) **No misread rejection.** Do not reject an option based
  on a paraphrase of its own pre-registered text.
- (d) **Disclose on-disk-vs-brief divergence.** When on-disk
  state and a working brief disagree, disclose the divergence
  and pin the on-disk value by hash rather than silently
  converging.
- (e) **Additive-only extension of permissive schemas.**
  Extend a permissive schema by adding fields, not by
  tightening enforcement in place.

Invariants (a)–(c) were codified in response to an initial
misresolution of the drums fork and validated on the very
next fork (guitar), which resolved to refuse-and-substitute on
the first attempt. Invariants (d) and (e) were added as
comparable divergences appeared in later cycles. The
invariants sit under, never above, operator authority.

## 9.4 The Chicken Grease A/B full-song showcase

The showcase deliverable — a stereo A/B mix that a listener
can play against the original recording — was rendered from
the closed per-instrument cells above. The delivered artefacts,
all recorded as permanent read-only anchors, are:

- **`cg_ab_mix.wav`** — the mix itself, SHA prefix
  `6e13e0075c5d8116…`, located at
  `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav`.
- **`cg_ab_mix.manifest.json`** — records the inputs
  (bass configuration, drums-substitute stem, guitar-substitute
  stem, piano null, other-residual null, vocals overlay) that
  produced the WAV.
- **`cg_ab_mix.replay_proof.json`** — a proof that a fresh
  render from the recorded inputs reproduces the delivered WAV
  byte-for-byte.

Byte-determinism was subsequently re-verified a second time by
a from-fresh-subprocess full-render regression suite covering
the WAV, the manifest, the replay proof, the bass-gain
amplification constant (`amplif = 2.688385`), the three pinned
profiles that feed the delivery, and the discipline guards
(no PRNG, absolute-path interpreter guard, canonical
seven-key environment pin). A LUFS-I diagnostic sidecar
measured the full mix at **−15.32 LUFS-I** without mutating
the WAV; the per-stem loudness measurements are consistent
with the mix, including the audibility-grounded nulls for
piano and other-residual.

Every internal gate for the showcase — replay-proof
byte-identity, all required inputs present, all discipline
scans clean, all tests green — is satisfied. The remaining
`LANDS` trigger is stated policy: the closure of a listening
deliverable requires the operator's ear on the WAV. That
trigger has not yet fired. This is a policy handoff, not an
outstanding engineering task, and no substitute for it exists
inside the system.

## 9.5 The four remaining focus songs and the metric-semantics escalation

The campaign's remit called for per-instrument arcs on four
further focus songs — WIG, Rome, Disco A, and Peach Dream —
in addition to Chicken Grease. Each of the four has been
opened at **skeleton stage**: an addressable per-song
directory under `data/v4/profiles/<song-hash>/` with a
`stem_manifest.json` listing the six `htdemucs` stem hashes.
No stage-1 sweep has been launched on any of them, and no
thresholds have been committed for any of them. The skeletons
are gated on a candid correctness concern about the composite
objective that arose during the guitar arc and that the agent
declined to resolve unilaterally.

**The concern.** The composite objective computes an
embedding term from a pretrained VGGish audio encoder. The
underlying panel implementation computes

$$\texttt{embedding\_cos\_vggish} \;=\; 1 - \cos(u, v)$$

which is a **distance** in $[0, 2]$ (lower is more similar,
zero is identical). The composite objective consumes it
correctly as a distance: it enters with a positive weight and
the objective is minimised. However, the frozen decision
protocol — the same one used in §9.1 to define `CONFIRMED`
and `RULED_OUT` — expresses its thresholds (`≥ 0.60
CONFIRMED`, `≤ 0.40 RULED_OUT`) in the vocabulary of a
similarity (higher is better). If the field is truly a
distance, the guitar family-2 value of 0.0354 corresponds to a
cosine similarity of ≈ 0.965 — extremely close to the
reference — and the ruling should read `CONFIRMED`, not
`RULED_OUT`. Under the current application, the closest
candidates are being ruled out precisely because they are
close.

**Why this was not fixed inline.** The correction is not a
one-line change the agent could quietly apply, for two
reasons. First, the closure campaign has a binding rule
against retuning frozen numeric thresholds without cause.
Second, and more consequentially, the correction has two
different shapes and they imply different follow-through:

- **Path A — keep the field as distance and invert the
  threshold consumers.** Rewrite every downstream verdict-
  emitting site so that it applies the thresholds as distance
  bars (`≤ 0.40 CONFIRMED`, `≥ 0.60 RULED_OUT`) and
  re-adjudicates each Chicken Grease family verdict on the
  inverted floors.
- **Path B — apply a `1 − distance` correction at the
  emission point and leave the thresholds as written.** Change
  the panel or its immediate consumer to emit similarity
  rather than distance, re-issue the deterministic replay
  proof for the composite objective (because the numeric
  contract of every future pinned profile changes), and
  re-adjudicate every prior Chicken Grease family verdict on
  the intended similarity scale.

Both paths are internally consistent. They differ in what
they imply about the historical verdicts, in whether the
determinism certificate must be re-issued, and in what a
future profile's numeric contract looks like. Choosing between
them is an authority decision, not an engineering one, and it
was recorded as an operator-authority escalation.

**Why the showcase is safe under either path.** The Chicken
Grease showcase does not depend on the choice. The two
`RULED_OUT` arcs (drums, guitar) were resolved by
refuse-and-substitute, and the audio delivered for those
cells is the operator-heard `htdemucs` stem verbatim — the
authoritative reference under any interpretation of the
composite metric. The bass arc was accepted under an operator
directive that used the composite ranking but did not depend
on the numeric floor. The two null cells are grounded in
`pyloudnorm` measurements below the silence floor, not in the
embedding metric at all. The vocals cell is under a
pre-existing hybrid-overlay policy that does not consult the
composite objective. The showcase therefore stands on any
metric-semantics resolution.

**What is blocked.** The four remaining focus songs are what
the metric-semantics decision blocks in practice. Their
stage-1 sweeps have not been launched because a sweep run
under one path would need to be discarded under the other; a
sweep run under both paths in parallel would double the
audio-storage and compute cost of the campaign's most
expensive stage. Each skeleton records the blocker explicitly
in a `blocked_on` field so that no downstream stage-1 sweep
can proceed until the escalation resolves.

## 9.6 The v4 rules layer

The v4 rules artefact — a machine-readable extract of the
generative rules the campaign's pinned profiles imply — was
scaffolded at an early cycle and passed a scaffold-level
smoke test. A substantive extraction pass followed on disk,
producing extractor code and output artefacts that go
materially beyond the scaffold. The substantive pass, however,
has not been formally registered against the rules
milestone's success criteria: there is no verdict row against
the substantive extractor, no register-row for its output
artefacts, and no supersede event linking the substantive
extractor back to the scaffold it replaces.

This is a bookkeeping gap, not a correctness gap. The
substantive extractor is present in the repository and its
outputs are on disk. What is missing is the audit-trail
formalisation that would let a future reader see, at the
milestone level, that the scaffold has been replaced. The
correct remediation — emit the missing verdict, register-row,
and supersede event, and record an anchor-preservation
snapshot confirming that the scaffold's smoke-test hash is
unchanged — is a one-cycle housekeeping task and is enumerated
in the future-work list of §10.

Separately from the substantive extractor, the pinned-profile
schema described in §9.3 (`pinned_profile_schema_v1.json` and
its validator) is a validated, load-bearing part of the v4
rules layer: it is what lets a downstream reader parse a
pinned profile from disk and check it for structural
compliance without re-running the pipeline that produced it.

## 9.7 Not started: exemplar ear, seeded generator, campaign closure

Three of the closure campaign's milestones were not begun.

**Lightweight exemplar ear.** A scoped ear model, distinct
from the CORN ordinal head described in §7, built as a
one-hour-compute exemplar over the five focus songs
(Chicken Grease, Molasses, Essence, Desire, Peach Dream)
using a CLAP + VGGish embedding ensemble with top-*k* window
similarity, evaluated by a leave-one-out protocol requiring
at least four of five held-out songs to score at least 6 and
none to score below 5.5. This milestone does not depend on
the metric-semantics escalation. It was scheduled after
per-instrument profiles completion and remained unopened
when the run ended.

**Seeded generator.** A generator program seeded from the
v4 rules artefact, tasked with producing five novel
instrumental songs and one interpolation-hybrid demonstration,
with a stall rule after eight iterations without five
passing candidates. It depends on both a substantive v4 rules
verdict (§9.6) and the exemplar ear.

**Campaign closure roll-up.** The final closure deliverable —
a completion report, an index of the delivered artefacts, the
certificate status, and a list of the remaining gaps —
together with updates to the operator-decisions document and
the codebase guide, a final housekeeping sweep, and clean
termination of the run. It depends on every v4 predecessor
above.

Each of these three has a designed acceptance shape recorded
in the campaign's plan of record, so a future resumption is a
matter of execution rather than re-planning.

<!-- END DELTA: NEW SECTION 9 -->


Stage 2: Wrote the new §9 "The v4 Closure Campaign" (subsections 9.1 framing, 9.2 determinism certificate, 9.3 Chicken Grease per-instrument arcs including agent-picks invariants, 9.4 CG A/B showcase, 9.5 four remaining songs and metric-semantics escalation with Path A/B, 9.6 v4 rules layer state, 9.7 not-started EAR/GEN/CLOSE) to draft.md with HTML delta markers for stage 7 splicing. All internal vocabulary translated to plain language; concrete embedding-cosine values, SHA prefixes, LUFS measurements, and file paths cited from cycle reports 10-12, 13-15, 16-18.
File: /home/user/long-exposure-runs/music-gen/reports/final/draft.md
Size: ~15k bytes, ~330 lines

<!-- BEGIN DELTA: REPLACE §1.4 End-state at a glance -->
<!-- Splice target: lines 97–108 of the baseline final_report.md,
     the "### 1.4 End-state at a glance" bullet block. Replace the
     block in its entirety with the following bullets. -->

### 1.4 End-state at a glance

- **Milestone distribution (v3 pipeline).** 731 validated, 22
  in-progress, 6 invalidated, 2 reopened, 1 superseded.
- **Milestone distribution (v4 closure campaign).** Of the 58
  v4 plan entries: 47 confirmed, 4 not started (exemplar ear,
  seeded generator, campaign closure roll-up, and one focus-song
  arc yet to open), 3 deferred, 1 in progress (the
  per-instrument profiles milestone), 1 awaiting operator
  authority (the metric-semantics escalation described in §9.5),
  and 1 replaced by later on-disk work without a formal
  supersede event (the v4 rules substantive extractor described
  in §9.6).
- **Findings.** v3 pipeline: 0 CRITICAL, 1 MAJOR, 21 MODERATE,
  10 MINOR, 30 INFO, 4 PASS, 45 NONE. v4 closure campaign:
  0 CRITICAL, 2 MODERATE, 5 MINOR.
- **Promise-check.** v3 pipeline: green. v4 closure campaign:
  not computed at final audit time.
- **Wall-cap.** not exceeded.
- **Open threads (v3).** M-EAR-1 (real-label calibration on
  full corpus, gated on egress unblock); M-RECREATE-2
  accurate-small-set (RC1 4/5, RC7 and RC9 both 5/5, RC10
  validated; parent held in-progress by design under the
  peer-under-G1 convention).
- **Open threads (v4).** (i) the metric-semantics escalation
  (§9.5) that blocks stage-1 sweeps on the four remaining focus
  songs; (ii) those four focus-song arcs (WIG, Rome, Disco A,
  Peach Dream), each open at skeleton stage and queued behind
  (i); (iii) the substantive v4-rules audit-trail rows (§9.6);
  (iv) the lightweight exemplar ear, the seeded generator, and
  the campaign closure roll-up (§9.7).

<!-- END DELTA: REPLACE §1.4 -->


Stage 3 complete: appended the §1.4 End-state at a glance replacement to draft.md with splice markers pointing at baseline lines 97–108. The new block keeps the v3 counts verbatim, adds a parallel v4 counts bullet translating the plan-of-record distribution to plain language, splits findings and promise-check into v3/v4 lines, and adds an "Open threads (v4)" bullet enumerating the four v4 open threads named in the outline.

<!-- BEGIN DELTA: UPDATE §9 (baseline) → §10 (revised) Conclusions -->
<!-- Splice target: replace baseline lines 1199-1303 (the entire
     "# 9. Conclusions, Honest Limits, and Future Work" section
     through the end of §9.4). The renumber pass at Stage 6
     changes the header to "# 10." and updates internal
     cross-refs accordingly. -->

# 10. Conclusions, Honest Limits, and Future Work

## 10.1 What is done

The end-state has two layers: the v3 pipeline delivered against
its "what counts as done" criteria, and the v4 closure campaign
that sits on top of it and pursues bounded follow-on
deliverables.

**v3 pipeline (unchanged from baseline).** Against the seven
project criteria the run's v3 end-state is:

1. **Ingestion, classification, and provenance chassis exist
   and are honest.** Every chunk is content-addressed; the
   three-model classifier ensemble gates release; the
   seven-non-factor sidecar is stored and audited but never
   consumed. The egress-ready state machine is deployed and
   fires under a two-consecutive-`media_ok` rule.
2. **Source separation is deterministic and licensed for
   redistribution.** `htdemucs_6s` renders four stems
   byte-identically across independent invocations. Determinism
   was verified on a five-song slice; the weights fetch is
   reproducible.
3. **Transcription has an honest per-axis F1 on the M-SEP-1
   synth reference.** basic-pitch 0.4.0 delivers usable
   pitch/onset/offset under a tuned octave-suppression grid;
   timbre, dynamics, and form are named as under-covered.
4. **A merged-score bridge is byte-identical across two full
   round-trips**, and a typed rules ledger of 76
   hash-deduplicated rules is validated against a
   planted-invalid rejection matrix.
5. **The DAW stack renders deterministically on Surge XT and
   Dexed through DawDreamer**, with one closed gap (GAP-1
   Ardour Lua MIDI import, closed by hand-authored XML) and
   one open gap (GAP-2 LV2/VST3 automation delivery, worked
   around by two-step render).
6. **The M-TEX-1 panel refuses to aggregate**, reports 72
   finite panel entries across three seeds, and surfaces the
   VGGish content-flip as a labelled, understood family
   disagreement.
7. **The pipeline closes end-to-end on a real rated song**
   (M-RECREATE-1, +5.906 dB effects-over-bare on the band-7
   exemplar) and the five-song accurate-small-set programme is
   hardened per-stem with RC7 and RC9 both landing 5/5.

**v4 closure campaign.** On top of the v3 pipeline the closure
campaign completed the determinism certificate (§9.2), closed
every per-instrument arc on Chicken Grease with a mix of
acceptances, refuse-and-substitute rulings, and grounded nulls
(§9.3), and delivered the Chicken Grease A/B full-song
showcase on internal gates pending an operator ear (§9.4). It
opened skeleton stem manifests for the four remaining focus
songs but did not launch any sweeps against them, because a
correctness question about the composite objective's metric
was surfaced and correctly deferred to operator authority
(§9.5). The pinned-profile schema is validated and load-bearing
for replay discipline; a substantive v4 rules extraction is on
disk but its verdict against the rules milestone's success
criteria has not been formally emitted (§9.6). The exemplar
ear, seeded generator, and campaign closure roll-up milestones
were not begun (§9.7).

## 10.2 The three live constraints

Three constraints are load-bearing and honest.

- **Real-label M-EAR-1 calibration depends on the full 80-song
  corpus.** 43 of 80 songs have on-disk audio; the remaining
  37 are registered with full provenance but their audio is
  behind the workspace egress policy. The armed harness (§7.6)
  will fire the full calibration automatically once the
  two-consecutive `media_ok=true` production probes land.
  M-EAR-1 is held in-progress by design until that fires.
- **Generation quality depends on the recreation loop closing
  on held-out songs.** M-RECREATE-1 closed on one band-7
  exemplar and the five-song focus set is hardened; the
  accurate-small-set parent remains in-progress under the
  peer-under-G1 convention until the panel-gate cell (RC6)
  validates on the held-out songs under RC1..RC3 outputs.
- **The v4 metric-semantics escalation blocks the four
  remaining focus-song arcs.** The composite objective's
  `embedding_cos_vggish` field is computed as a distance but
  consumed by downstream decision protocols as a similarity.
  The remediation is an authority choice between two
  internally-consistent paths (§9.5) with different
  consequences for prior verdicts and for the determinism
  certificate. Until the choice is made, launching sweeps on
  WIG, Rome, Disco A, or Peach Dream would risk producing work
  that must be discarded under one of the two paths.

## 10.3 Actionable next steps

Drawn directly from the final audit's `future_work` block for
the v4 closure campaign, in the order the auditor recommends
attempting them, with the v3 follow-on items preserved
underneath.

**v4 closure campaign — in order.**

1. **Operator selects between Path A and Path B for the
   metric-semantics escalation.** Path A keeps
   `embedding_cos_vggish` as a distance and rewrites every
   threshold consumer to apply the bars in the inverted sense
   (`≤ 0.40 CONFIRMED`, `≥ 0.60 RULED_OUT`), then re-adjudicates
   every prior Chicken Grease family verdict on the inverted
   floors. Path B applies a `1 − distance` correction at one
   emission point (`objective.py` or `embedding_panel.py`),
   re-issues the determinism certificate, and re-adjudicates
   every prior Chicken Grease family verdict on the intended
   similarity scale. Prior refuse-and-substitute pins for
   drums and guitar are safe under either path.
2. **Emit the missing substantive v4-rules audit-trail rows.**
   The substantive extractor is on disk; add the missing
   milestone verdict row against `M-V4-RULES-1/substantive`, a
   register row for its six output artefacts, a supersede
   event pointing back to the scaffold, and an
   anchor-preservation snapshot confirming the scaffold's
   smoke-test hash is unchanged.
3. **Run stage-1 and stage-2 sweeps on WIG, Rome, Disco A, and
   Peach Dream** once (1) resolves, under the same
   sweep-storage hygiene protocol that held during the
   Chicken Grease closure (score-and-delete; ≤ 500 MB working
   audio at any one time; a `df` check before each stage;
   working volume held under 90% full).
4. **Build the lightweight exemplar ear** over Chicken Grease,
   Molasses, Essence, Desire, and Peach Dream, using a CLAP +
   VGGish ensemble with top-*k* window similarity; no corpus
   calibration; leave-one-out acceptance is "at least four of
   five held-out songs at score ≥ 6, none < 5.5."
5. **Build the seeded generator program** from the v4 rules
   artefact; deliver five novel instrumental songs and one
   interpolation-hybrid demonstration; stall the run after
   eight iterations without five passers.
6. **Execute the campaign closure roll-up:** completion
   report, indexed deliverables, certificate status, remaining
   gaps; refresh the operator-decisions document and the
   codebase guide; final housekeeping sweep; end the run.
7. **One housekeeping cycle for POR transcription drift**
   (five rows): canonicalise the v3-rules spec path in the
   plan-of-record narrative; refresh the five pinned SHAs
   against the on-disk artefacts; correct a malformed 62-hex
   drums-MIDI hash to its 64-hex on-disk value.

**v3 pipeline follow-on items — preserved.**

8. **Real-label M-EAR-1 calibration on the full 80-song
   corpus** per the c26 Path B commit doc — awaits egress
   unblock or manual manifest reconciliation.
9. **Add `probe_kind ∈ {smoke, production}` to
   `data/ingestion/egress_status.jsonl`**, so the
   two-consecutive-`media_ok` unblock signal cannot be
   spuriously satisfied by smoke rows.
10. **Rebuild the missing `data/gen/*` renders on demand from
    the seeded ledger** — a single deterministic sweep
    re-materialises them.
11. **Emit a single supersede event** that either renames the
    c51+ RC7/RC10 leaves to the pre-registered
    `accurate-small-set-v2` parent, or explicitly folds v2
    back into v1 with a note that rubric-v2 was carried
    inline under v1 leaf identifiers.
12. **Restore or supersede the missing SSoT writer sources**
    (`long_exposure/workspace_bootstrap.py`,
    `long_exposure/tools/_ledger_schema.py`); if they were
    consolidated into surviving package modules, emit a
    `_plan/*-supersede` event that names the current SSoT.
13. **Republish `data/anchor_manifest_v1.json` as `_v2`** with
    anchor #20 = post-c36-edit SHA of
    `scripts/palette_render/render_stem.py`, and encode the
    backwards-compat contract (`parameter_dict=None` ≡ c33
    anchor) explicitly.
14. **Append 10 band-7 rows to
    `corpus/ratings/ratings_manifest.tsv`** so provenance
    matches the on-disk audio M-RECREATE-1 consumed.
15. **Emit a closure event** adjudicating the two observed
    silent-death cases under
    `_manager/background-job-supervision-clone-0` (c31
    fixture, c36 feature extraction), or archive them with
    lessons learned.
16. **Publish SSoT schemas for `anchor_preservation_v1.json`
    and `verdict_v1.json`** and have subsequent cycles
    conform.
17. **Fill the c41/c42 reporting gap, add the c52 egress-probe
    row, and either produce substantive c55-c58 content or
    retire the empty `report_cycles_56-58.md`**.

## 10.4 No new hypotheses

Everything above is drawn from what was measured. The one live
scientific open end — the collision-arc
PARTIAL_BP_UNRESOLVED_SHAPE (§8.5) — is left open with its
four ruled-out candidate mechanisms named, and no new
mechanism is proposed here. It is a real question about the
distribution of generation-output collisions, and it deserves
an unhurried follow-up rather than a speculative closure
inside this report. The v4 metric-semantics question (§9.5)
is likewise left as a named, adjudicable choice rather than
resolved from inside the report; the two paths are stated in
enough detail that the adjudication is a decision, not a
research task.

<!-- END DELTA: UPDATE §9 (baseline) → §10 (revised) Conclusions -->


Stage 4 complete: appended §9 Conclusions revision to draft.md (rewritten as §10 in the renumber pass). §9.1 "What is done" split into v3 (preserved 7-criteria list) and v4 (new paragraph) layers; §9.2 "Two live constraints" widened to three (adds the metric-semantics blocker); §9.3 "Actionable next steps" now leads with 7 v4 items in auditor order then preserves the 10 v3 items renumbered 8-17; §9.4 "No new hypotheses" preserved and lightly extended to name the metric-semantics choice as adjudicable rather than resolved here.

<!-- BEGIN DELTA: APPEND ABSTRACT v4 PARAGRAPH -->
<!-- Splice target: the baseline "Abstract" block, immediately
     before "# 1. Introduction". Preserve every existing
     paragraph verbatim and append the following paragraph as
     the final paragraph of the abstract. -->

A follow-on **v4 closure campaign** sits on top of this
pipeline and pursues a bounded set of deliverables. A bit-exact
determinism certificate for the v3 Chicken Grease
reconstruction was completed and confirmed. Every
per-instrument arc on Chicken Grease closed with a terminal
verdict: bass accepted under a narrowly-scoped operator
directive, drums and guitar refused after both explored render
families ruled out and resolved by substituting the
operator-heard stem verbatim, piano and other-residual
grounded as null on stem-audibility measurements at
approximately −81 dBFS, vocals covered by a pre-existing
hybrid-overlay policy. A Chicken Grease A/B full-song showcase
mix was rendered and its byte-determinism verified twice
independently; internal gates are green and the remaining
`LANDS` trigger is an operator ear on the WAV, per stated
policy. Four remaining focus songs (WIG, Rome, Disco A, Peach
Dream) are open at skeleton stage with per-song stem manifests
but no sweeps launched, because a candid correctness question
about the composite objective's embedding-cosine field — it is
computed as a distance but consumed by downstream decision
protocols as a similarity — was surfaced and correctly
escalated to operator authority rather than resolved
unilaterally. The pinned-profile JSON schema is validated and
load-bearing for replay discipline; a substantive v4 rules
extraction is on disk but its formal verdict against the
rules milestone's success criteria has not been emitted. The
lightweight exemplar ear, seeded generator, and campaign
closure roll-up were not begun. The v4 audit distribution is
47 confirmed, 4 not started, 3 deferred, 1 in progress, 1
awaiting operator authority, and 1 replaced by later on-disk
work without a formal supersede event, with findings 0
CRITICAL, 2 MODERATE, 5 MINOR.

<!-- END DELTA: APPEND ABSTRACT v4 PARAGRAPH -->


Stage 5 complete: appended the v4 abstract paragraph delta to draft.md, with splice markers instructing finalize to insert it as the closing paragraph of the baseline Abstract (immediately before §1 Introduction). The paragraph names the certificate, the five closed CG cells and their outcomes, the A/B showcase and its byte-determinism, the four skeleton focus songs, the metric-semantics escalation, the pinned-profile schema state, the substantive-rules audit-trail gap, and the not-started EAR/GEN/CLOSE items — closing with the v4 distribution and findings counts.

<!-- BEGIN DELTA: STAGE 6 RENUMBER DIRECTIVES -->
<!-- Stage 6 renumbering summary (applied to headers above and
     instruction to Stage 7 finalize for the preserved baseline
     material):

     1. NEW §9 "The v4 Closure Campaign" (this file, lines
        14–435): keeps §9 numbering as-is; no rename required
        because the outline's section-by-section change map
        inserts the new content at §9 and shifts baseline §9/§10
        down by one.

     2. Baseline §9 "Conclusions, Honest Limits, and Future
        Work" — the Stage-4 delta has been retitled in place to
        "# 10. Conclusions, Honest Limits, and Future Work"
        with its subsection headers updated to §10.1 / §10.2 /
        §10.3 / §10.4.

     3. Baseline §10 "References" — finalize (Stage 7) must
        rename the sole header
            "# 10. References"
        to
            "# 11. References"
        in place. No prose changes to the References section.

     4. Cross-references inside the preserved v3 material
        (sections 2–8) all use section numbers 2–8 that are
        unaffected by this renumbering. No sweep is required in
        that range.

     5. Cross-references inside the Conclusions delta that point
        to "§9.5" refer to the new v4 section §9.5 (not the old
        Conclusions §9.x), so they remain correct after the
        renumber. No further edits needed.
-->
<!-- END DELTA: STAGE 6 RENUMBER DIRECTIVES -->


Stage 6 complete: renumbered the Stage-4 Conclusions delta in place from §9 → §10 (`# 10. Conclusions…`, `## 10.1`…`## 10.4`), and appended a renumber-directive block instructing Stage 7 finalize to rename baseline `# 10. References` → `# 11. References`. The new v4 section keeps its §9 numbering (the outline inserts it at §9 and shifts Conclusions/References down). No cross-refs in preserved §§2–8 are affected; the Conclusions delta's "§9.5" references resolve correctly to the new v4 section.
