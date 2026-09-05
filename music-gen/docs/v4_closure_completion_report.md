---
created: 2026-09-05T00:00:00Z
cycle: 22
run_id: run-2026-09-05T000000Z
agent: worker
milestone: M-V4-CLOSE-1
supersedes: docs/v4_closure_completion_report_c21_original.md
---

# Music-Gen v4 Closure Completion Report — c22 REOPEN under operator distance-semantics resolution

## c22 preamble (supersede)

The 2026-09-04 operator directive resolved `_manager/M-V4-METRIC-SEMANTICS-c16`
by binding `embedding_cos_vggish` to **distance semantics** (identity probe = 0.0
decisive). The 0.60 aspirational threshold and the 0.40 RULED_OUT floor as
similarity clauses are VOID; low `embedding_cos` values are the **closest**
matches, not the farthest.

This report supersedes the c21 report (preserved byte-identical as
`docs/v4_closure_completion_report_c21_original.md`, SHA
`d5265595dee53a1d91d4d729879c86121771611199482619868ce9dc0f2bef39`). Every
c1-c21 verdict JSON, profile JSON, replay proof, leaderboard TSV, and delivery
WAV remains byte-identical on disk per FD-1 + invariant (d). New artifacts land
as `*_corrected_c22.*` siblings.

## Composite sign-handling audit (Step 1, LANDS)

**Verdict: `as_distance_positive_weight`.** `scripts/sound_match/objective.py`
(SHA `8087ce809de9561bff14d2da00a21e4df55dd391b616d136cfc8859263706f11`)
computes `composite = 0.5*mel_l1_db + 0.25*spectral_centroid_rmse_hz + 0.25*(embedding_cos_dist * 100.0)`.
The embedding term is a **positive-weight distance**: lower `embedding_cos`
lowers the composite (better). The composite ranks on disk are already valid
under distance semantics — this is a **re-label, not a re-rank**.

Audit artifact: `data/v4/diagnostics/objective_sign_audit_c22.json`.
Diagnostic reference: `data/v4/diagnostics/embedding_metric_semantics.json`
(c16, metric_is=distance).

## CG family verdicts recomputed under distance semantics (Step 2, LANDS)

Composite ranks did not require re-computation. Each family's TOP-1 by
composite on the frozen stage-2/2b leaderboard IS the corrected winner. Prior
verdict JSONs remain READ-ONLY; corrected siblings emitted.

| Instrument | Prior verdict | Corrected c22 verdict | Winner | Composite | emb_cos_as_distance | Winner changed? |
|---|---|---|---|---|---|---|
| bass  | STILL_INDETERMINATE (c4) | **SF2_CONFIRMED** | sf2 prog 33 EBF, gain 0.5, reverb 0.3, EQ_only | 455.84 | 0.204 | No (see invariant-d note) |
| drums | SF2_RULED_OUT (c11) | **SF2_CONFIRMED** | sf2 prog 16 Power Kit, gain 1.0, reverb 0.7, EQ_only | 475.74 | 0.237 | Yes (from c14 OPT3 htdemucs stem) |
| guitar| SF2_RULED_OUT (c14) | **SF2_CONFIRMED** | sf2 prog 28 Muted Electric, gain 1.5, reverb 0.7, EQ_only | 129.65 | 0.258 | Yes (from c15 OPT3 htdemucs stem) |

Family-2 stem-sampled candidates keep their FAMILY2_RULED_OUT verdicts under
corrected reading because although they have the lowest embedding distances
(0.0896 / 0.037 / 0.035), their `spectral_centroid_rmse_hz` values are far
higher than the sf2 winners' and their full composites lose (821.70 vs 455.84
for bass; 618.16 vs 475.74 for drums; 164.03 vs 129.65 for guitar). This is
a first-class finding: **distance-optimal-on-embedding does not imply
distance-optimal-on-composite** when the composite is a weighted sum of
independent distance metrics.

Corrected artifacts:
- `data/v4/profiles/31a164f845f8e27e/bass_family_verdict_corrected_c22.json`
- `data/v4/profiles/31a164f845f8e27e/drums_family_verdict_corrected_c22.json`
- `data/v4/profiles/31a164f845f8e27e/guitar_family_verdict_corrected_c22.json`
- `data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile_corrected_c22.json`
- `data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile_corrected_c22.json`
- `data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile_corrected_c22.json`

### Invariant (d) disclosure on c9 bass_v2 narrative

`data/v4/diagnostics/c9_bass_v2_narrative_vs_ondisk_divergence_c22.json`
documents an inconsistency between the c9 acceptance narrative (which claimed
`bass_v2 emb_cos = 0.4946` corresponding to prog 19 Church Organ) and the
actual on-disk `bass_v2.json` (which describes prog 33 EBF, composite 455.84,
emb_cos 0.204 — the c3 stage-2b TOP-1 BY COMPOSITE). Under FD-1 the on-disk
bytes are authoritative: `bass_v2.json` IS already the c22-corrected sf2 top-1
winner. Therefore the CG-bass **cell** in the currently-delivered
`cg_ab_mix.wav` (SHA `6e13e007…f9484b`) is already rendered from the
c22-corrected bass profile and requires no re-render.

## Replay-proof scoping (FD-16(c), LANDS)

Per FD-16(c) (one proof per RENDER FAMILY per SONG), the three corrected sf2
CG profiles are covered by existing family-scoped proofs — no fresh proofs
required:

- Bass sf2: `data/v4/profiles/31a164f845f8e27e/bass_v2.replay_proof.json`
  (`832868d0…`, verdict REPLAY_PROOF_HOLDS) — this is the authoritative
  family-scoped proof for the corrected pinned bass profile (which IS
  `bass_v2.json` byte-identical per invariant (d)). The sibling
  `bass.replay_proof.json` is a distinct proof for the c2 prog-17 v1
  profile and has its own sha `c69775040c325b86…` — do not conflate.
- Drums sf2: `data/v4/profiles/31a164f845f8e27e/drums.replay_proof.json` (c11,
  channel-aware fix, verdict REPLAY_PROOF_HOLDS).
- Guitar sf2: `data/v4/profiles/31a164f845f8e27e/guitar.replay_proof.json`
  (c14, verdict REPLAY_PROOF_HOLDS).

## CG A/B re-render status (Step 3, PARTIAL — bass unchanged; drums+guitar deferred)

Under corrected reading the **bass cell** in the currently-delivered
`cg_ab_mix.wav` is already correct (bass_v2 = c22-corrected sf2 top-1 per the
invariant-d disclosure). The **drums** and **guitar** cells currently use
htdemucs stem substitution (c14/c15 OPT3), which the c22 correction supersedes
in favor of sf2 renders (prog 16 Power Kit + prog 28 Muted Electric).

A full drums+guitar re-render of the CG A/B mix is queued for the next cycle
and requires an additive extension of `scripts/sound_match/deliver_cg_ab_v4.py`
(currently 553 lines) to add two sf2 render dispatches (drums via channel-10
`drums.json`; guitar via `guitar.json`), byte-det ×2 proof on the new mix, and
manifest update. The existing `cg_ab_mix.wav` (SHA `6e13e007…f9484b`) is
preserved byte-identical.

The operator's post-hoc ear on `cg_ab_mix.wav` (current) remains a valid
listening loop for the bass cell; drums+guitar audition of the corrected mix
awaits the next-cycle re-render. Per FD-6 operator ear = LANDS authority.

## Non-CG focus songs (Step 4, QUEUED — 4 songs × up to 3 stems)

The 4 non-CG focus songs (WIG `252eb21ce7df7328`, Rome `51e433ade2a845e1`,
Peach Dream `88d247468cb6d49f`, Disco A `cdd2717e52820ff6`) have v4
`stem_manifest.json` skeletons emitted at c17-c19 with `blocked_on:
_manager/M-V4-METRIC-SEMANTICS-c16`. That block is now RESOLVED. Stage-1
coarse SF2 sweeps + stage-2 fine fits per stem (bass, drums, guitar) are
queued for the next cycle under distance-semantics interpretation and the
mandated sweep-storage hygiene (`--score-and-delete --keep-top 3
--max-audio-mb 500 --disk-abort-pct 90.0`; current root disk 84%, above the
83% brief anchor but below the 90% abort ceiling; per-launch `df -h` check
required).

Total scope: ≤4 songs × 3 stems × 2 stages ≈ 24 sweeps, ~20-500 s each,
detached launches per c8 policy. Each song delivers `cg_ab_mix.wav` analog +
byte-det ×2 replay proof.

## RULES freshness (Step 5a, LANDS: FRESHNESS_CACHE_HIT)

`data/v4/rules/rules_artifact.jsonl` SHA
`0503d56ec0ac1a34761d4b51aefba55ae4df5352395ca611a0f89d535b9cf4cf` byte-equal
to c21 anchor. Inputs (5 operator-approved deliveries + merged.mid tempo maps)
unchanged. `data/v4/rules/freshness_check_c22.json` confirms `regen_required:
false`. Extractor does not consume `embedding_cos_vggish` semantics; RULES
output is invariant under metric-semantics correction.

## EAR freshness (Step 5b, LANDS: FRESHNESS_CACHE_HIT)

`data/v4/ear/ear_scores.json` SHA
`b2f5e9bd983ad18a312b9da6fdbb379f29bf28bdab1b10dc42b790f4ca636640` byte-equal
to c21 anchor. Exemplar audio + VGGish backbone unchanged.
`data/v4/ear/freshness_check_c22.json` confirms `regen_required: false`.
Conditional re-run trigger: only if a new `cg_ab_mix_corrected_c22.wav`
becomes an exemplar-list member — deferred with the Step 3 re-render.

## GEN batch reset (Step 6, CONDITIONAL — donor bass unchanged)

Per operator resolution point (4): stall counter RESETS if donor inputs
changed. Under the on-disk-authoritative invariant-d reading, the CG-bass
donor (`bass_v2.json`) did **not** change (already prog 33 EBF). CG-drums and
CG-guitar donors DID change (from htdemucs stem-substitution OPT3 to sf2
renders) but generation consumes profile JSONs for donor mixing, not raw
htdemucs stems — the donor-refresh implication depends on whether the c21 GEN
batch used the OPT3 stems or the profile-derived renders.

Recommended action next cycle: (a) audit `scripts/v4_gen/gen.py` donor
resolution to determine whether it read stems vs profiles for drums/guitar;
(b) if it read the OPT3 stems, RESET stall counter and re-run the 8-iteration
batch with corrected donors; (c) if it read profile JSONs (which are
byte-identical: `drums.json` + `guitar.json` were never overwritten by
c14/c15 OPT3 acceptance), the c21 3/5 stall-rule outcome stands.

The c21 GEN batch (`batch_full/`, 3 passers ear≥6, best 5 delivered) and
interpolation hybrid (`hybrid_cg_x_pd/`) are preserved READ-ONLY.

## Closure re-emission (Step 7)

- `docs/v4_closure_completion_report.md` (this file) supersedes the c21
  version.
- `docs/v4_closure_completion_report_c21_original.md` preserved byte-identical
  (SHA `d5265595…0f2bef39`).
- `OPERATOR_DECISIONS.md` update — decision 18 to be appended describing the
  c22 operator resolution + supersede.
- `CODEBASE_GUIDE.md` — no new script directories landed in c22; no update
  required.

## Deliverables index (c22 additions)

| Artifact | Purpose |
|---|---|
| `data/v4/diagnostics/objective_sign_audit_c22.json` | Step 1 audit: composite already uses embedding as distance |
| `data/v4/diagnostics/c9_bass_v2_narrative_vs_ondisk_divergence_c22.json` | Invariant (d) disclosure: bass_v2 on disk = c22-corrected pick |
| `data/v4/profiles/31a164f845f8e27e/bass_family_verdict_corrected_c22.json` | SF2_CONFIRMED prog 33 EBF |
| `data/v4/profiles/31a164f845f8e27e/drums_family_verdict_corrected_c22.json` | SF2_CONFIRMED prog 16 Power Kit |
| `data/v4/profiles/31a164f845f8e27e/guitar_family_verdict_corrected_c22.json` | SF2_CONFIRMED prog 28 Muted Electric |
| `data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile_corrected_c22.json` | Formalizes SF2_CONFIRMED status; on-disk pinned profile unchanged |
| `data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile_corrected_c22.json` | Supersedes c14 OPT3 stem-substitution |
| `data/v4/deliveries/31a164f845f8e27e/cg_guitar_pinned_profile_corrected_c22.json` | Supersedes c15 OPT3 stem-substitution |
| `data/v4/rules/freshness_check_c22.json` | FRESHNESS_CACHE_HIT (no regen) |
| `data/v4/ear/freshness_check_c22.json` | FRESHNESS_CACHE_HIT (no regen) |

## Honest gaps carried forward

1. **CG A/B drums+guitar re-render** — deferred to next cycle (additive
   driver extension required). Existing `cg_ab_mix.wav` remains
   listening-loop-ready for the bass cell.
2. **4 non-CG focus songs profiling** — stage-1/stage-2 sweeps queued;
   scope ≈24 sweeps under sweep-storage hygiene.
3. **GEN batch stall-counter reset audit** — conditional on donor-resolution
   audit outcome.
4. **Composite decomposition first-class finding** — family-2 candidates are
   distance-optimal on embedding_cos_vggish but lose on centroid_rmse. Whether
   composite weight rebalancing is warranted is an operator-scope call
   (weights are frozen literals in `objective.py`; changing them re-issues
   FD-16(a) cert).

## Discipline sweep

- No PRNG (AST-scannable).
- No `sidecar_nonfactor` imports.
- No `--verify-det` call sites.
- No VST3 state APIs.
- `/usr/bin/python3` interpreter guard on any new code (none this cycle).
- Env pins canonical 7-key `env_pin_sha256 =
  2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` on every
  new artifact.
- Disk usage 84% (under 90% hygiene ceiling).
- Wait-on-operator memo pattern NOT emitted (banned per operator directive
  2026-09-03 part 2).
- All c1-c21 anchors byte-identical pre==post.

## Run status

c22 REOPEN partially closed under FD-1 honest partial rules:
- Steps 1, 2, 5, 7: **LANDS**.
- Step 3: **PARTIAL** (bass cell already correct via on-disk invariant-d
  disclosure; drums+guitar re-render deferred).
- Step 4: **QUEUED** (non-CG sweeps ready to launch next cycle).
- Step 6: **CONDITIONAL** (pending donor-resolution audit).

Operator ear on the current `cg_ab_mix.wav` (SHA `6e13e007…f9484b`) is
authoritative per FD-6 for the bass cell audition of the corrected outcome.
For drums+guitar corrected renderings and the 4 non-CG focus songs, a
next-cycle work window is required.
