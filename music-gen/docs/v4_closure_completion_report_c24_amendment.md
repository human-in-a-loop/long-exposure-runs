---
created: 2026-09-05T00:00:00Z
cycle: 24
run_id: run-2026-09-05T000000Z
agent: worker
milestone: M-V4-CLOSE-1/c24-amendment
supersedes_path: null
---

# Music-Gen v4 Closure Completion Report — c24 Amendment

**Appends** `docs/v4_closure_completion_report.md` (c22 rewrite) and
`docs/v4_closure_completion_report_c23_amendment.md`. Read those first for context.
This amendment records the c24 discipline reset and substantive-track outcomes.

Anchor discipline: c22 report + c23 amendment are READ-ONLY per invariant (d);
this amendment sits as a chronological sibling and does not rewrite either.

## 1. c23 SF2_CONFIRMED verdicts were in-error emissions; c24 reverses

c23 emitted `SF2_CONFIRMED` for all 4 non-CG bass stems on stage-1 alone, extending
the c9 CG-bass composite-relative WINNER precedent to non-CG bass without operator
authority. c24 auditor CRITICAL:
- **C-1 scope-extension**: c9 wording is CG-bass-scoped; extending it without
  operator authority violates agent-picks invariants (a) prefer-no-operator-scope-
  extension + (e) canonical pinned-profile shape stability.
- **C-2 above-floor violation**: Rome (emb_cos_dist 0.5145) and Peach Dream
  (0.4437) sit above the c9-retained 0.40 distance-upper-bound floor — the
  degenerate zone the c9 floor was retained to catch.

c24 Track A reverses all 4 verdicts:

| Song | sha16 | emb_cos_dist | c23 (WRONG) | c24 (REVISED) |
|---|---|---|---|---|
| Rome | 51e433ade2a845e1 | 0.5145 | SF2_CONFIRMED | **SF2_RULED_OUT** (above-floor) |
| Peach Dream | 88d247468cb6d49f | 0.4437 | SF2_CONFIRMED | **SF2_RULED_OUT** (above-floor) |
| What If I Go | 252eb21ce7df7328 | 0.3055 | SF2_CONFIRMED | **STILL_INDETERMINATE** (below-floor) |
| Disco A | cdd2717e52820ff6 | 0.2443 | SF2_CONFIRMED | **STILL_INDETERMINATE** (below-floor) |

The 4 c23 SF2_CONFIRMED artifacts are preserved byte-identical under
`stale/<song>_bass_family_verdict.c23_scope_extension_disclosed.json` per invariant
(d); `supersedes_path` carries the stale path as `str` (c14 lemma) in every
revised verdict.

## 2. Rome + Peach Dream bass RULED_OUT under corrected distance semantics

Reading the c9-retained 0.40 floor as a distance-upper-bound (post c22 metric-
semantics resolution: `embedding_cos_vggish` is a **distance**, not a similarity),
`emb_cos_dist > 0.40` means far-from-reference — the exact "degenerate candidate"
class c9 retained the floor to catch. Rome (0.5145) and Peach Dream (0.4437) fall
in this zone → **SF2_RULED_OUT** is the honest verdict.

## 3. WIG + Disco A bass STILL_INDETERMINATE pending operator authority

WIG (0.3055) and Disco A (0.2443) fall below-floor = close-to-reference; they are
eligible for acceptance under composite-relative WINNER precedent, but that
precedent is CG-bass-scoped per c9. Extending it to non-CG bass is an
operator-authority call per FD-6 — invariants (a)/(b)/(c)/(d) do NOT auto-resolve
this (unlike the c14 drums + c15 guitar OPT3 outcomes where both families landed
RULED_OUT and OPT3 was uniquely anti-stall-preferred).

## 4. Escalation `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` blocked_on_operator

New escalation at `data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json`
(status=`action_required`, authority=`OPERATOR`, `blocked_on_operator=true`,
`supersedes_path=null` new class). Three named paths parallel to c7 CG-bass shape:

- **OPT1** — operator authorizes composite-relative WINNER scope-extension to
  non-CG bass. WIG + Disco A eligible after stage-2 fine fit + per-song replay
  proof; Rome + PD remain RULED_OUT.
- **OPT2** — operator refuses scope-extension. Non-CG bass showcase falls back to
  OPT3 htdemucs stem substitution per c14/c15 invariant-compliant precedent.
- **OPT3** — operator authorizes case-by-case per song.

Per c24 auditor: neither OPT1 nor OPT2 is disambiguated by invariants
(a)/(b)/(c)/(d); agent-picks invariants are NOT extended to auto-resolve this.

## 5. CG drums + CG guitar OPT3 stand under corrected distance semantics

Track D emits two sibling disclosure JSONs (`supersedes_path=null`; do NOT rewrite
c14 OPT3 drums or c15 OPT3 guitar pinned profiles which stand):

- `data/v4/deliveries/31a164f845f8e27e/cg_drums_acceptance_c22_corrected_disclosure.json`
  — verdict `CG_DRUMS_ACCEPTANCE_STANDS_C22_CORRECTED_UNDER_DISTANCE_SEMANTICS`.
  sf2 top-1 emb_cos_dist 0.2374 is CLOSE to reference (below-floor is GOOD under
  distance); c14 OPT3 stands per invariants (a)/(b)/(c) because composite-relative
  WINNER precedent scope-extension from c9 CG-bass to CG-drums STILL requires
  operator authority per FD-6.
- `data/v4/deliveries/31a164f845f8e27e/cg_guitar_acceptance_c22_corrected_disclosure.json`
  — analogous for guitar with emb_cos_dist 0.2584.

Honest disclosure per invariant (d): c24 brief cited c14 drums pinned SHA prefix
`1fcb2e4660058ff9…`; on-disk SHA is `720f1424e9fcac35…`. On-disk is authoritative
per FD-1; brief cite is stale/transcription-error. c14 drums pinned + c15 guitar
pinned byte-identical pre==post.

## 6. c24 substantive advance status

- **Track B (stage-2 WIG + Disco A)**: DEFERRED to c25. Wall budget compressed to
  ensure discipline reset (Tracks A + D) + closure amendment + POR + housekeeping
  land cleanly. Not required before operator resolves Track A escalation because
  verdicts remain STILL_INDETERMINATE regardless of stage-2 outcome until operator
  authorizes scope-extension.
- **Track C (non-CG drums + guitar stage-1 sweeps)**: DEFERRED to c25. Aspirational
  coverage; c25+ can pick up after Track A escalation lands one way or the other.
- **Track F (test debt fillin for c23 scripts)**: DEFERRED to c25 audit fill-in
  per c10-c22 pattern. Substantive verification of c24 Track A + D via the
  emitter's assert-based end-to-end run + anchor_preservation pre==post.

## 7. Honest gap disclosure: operator ear check recommended before OPT1

E-Piano 2 (GM prog 5) winning 3/4 non-CG bass stage-1 TOP-1s on the frozen
composite despite being wildly ear-implausible for bass content is an
**ear-plausibility flag** deserving operator ear check per campaign L60 "operator
ear = LANDS authority". Recommend operator listen to the 4 non-CG bass stage-1
TOP-1 renders BEFORE OPT1 authorization:

- WIG: `data/v4/profiles/252eb21ce7df7328/bass_sweep_stage1/renders/<top-1>.wav`
- Rome: `data/v4/profiles/51e433ade2a845e1/bass_sweep_stage1/renders/<top-1>.wav`
  (RULED_OUT, but useful as ear reference)
- Peach Dream: `data/v4/profiles/88d247468cb6d49f/bass_sweep_stage1/renders/<top-1>.wav`
  (RULED_OUT)
- Disco A: `data/v4/profiles/cdd2717e52820ff6/bass_sweep_stage1/renders/<top-1>.wav`

The systematic finding (E-Piano/organ over source-of-truth bass on all 4 non-CG
bass cells; extends 5-arc CG-only pattern to 15-arc) is content-driven per the c23
diagnostic `data/v4/diagnostics/systematic_composite_favors_non_source_of_truth_c23.json`
and NOT a defect. It IS a signal that composite ranks may not track ear judgments
on GM SF2 bass candidates for this rated corpus.

---

**Anchor discipline verified**: c22 report + c23 amendment READ-ONLY (byte-identical);
c14 drums pinned + c15 guitar pinned byte-identical; c17 cg_ab_mix.wav sha
`6e13e007…f9484b` byte-identical; c9 bass_v2.json byte-identical.

**env_pin_sha256** (7-key canonical): `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`.

**M-V4-SHOWCASE-1 status**: CG A/B LANDS_pending_operator (unchanged). Non-CG A/B
blocked on Track A escalation resolution.
