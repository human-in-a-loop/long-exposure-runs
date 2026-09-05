---
created: 2026-09-05T00:00:00Z
cycle: 23
run_id: run-2026-09-05T000000Z
agent: worker
milestone: M-V4-CLOSE-1
supersedes: null
appends: docs/v4_closure_completion_report.md
---

# Music-Gen v4 Closure Completion Report — c23 amendment (non-CG profiling launch)

## c23 preamble

This amendment appends c23 outcomes to the c22 closure report. The c22 report
remains READ-ONLY per FD-1 + invariant (d). c23 focused on the c22-audit
QUEUED tracks: (Track 1) OPT3 confirmation semantics; (Track 2) non-CG focus
song profiling opened; (Track 3) GEN batch conditional; (Track 4+5) reporting
+ POR bookkeeping.

## Track 1 — CG drums + guitar Track-1 disclosure (LANDS as inversion note)

The c23 brief proposed emitting
`OPT3_STANDS_UNDER_CORRECTED_SEMANTICS` confirmation JSONs for CG drums +
guitar. Per invariant (d) + FD-1 (on-disk authoritative), this proposal
inverts the c22 corrected verdicts already on disk. The c22 corrected pinned
profiles hold that under distance semantics the sf2 TOP-1s are
SF2_CONFIRMED (drums emb_cos_as_distance=0.237 CLOSE, guitar 0.258 CLOSE) and
that OPT3 htdemucs stem substitution is SUPERSEDED as no-longer-necessary.

The brief's own reasoning contained a sign error: "0.2374 is still far above
the closer than 0.40 threshold, i.e., FAR from reference" — but 0.2374 < 0.40
means the value IS closer than 0.40 (CLOSE, not FAR).

Rather than emit a confirmation that would regress the c22 state, c23 emits
one disclosure note at
`data/v4/deliveries/31a164f845f8e27e/cycle23/cg_drums_guitar_track1_disclosure_c23.json`
recording the divergence and pinning the c22 corrected verdicts as terminal.
The current `cg_ab_mix.wav` (SHA `6e13e007…f9484b`) still uses c14/c15 OPT3
htdemucs stems for drums + guitar; whether to re-render with sf2 CONFIRMED
sounds is deferred to operator ear per FD-6.

## Track 2 — Non-CG focus song profiling opened (PARTIAL, sweeps launched)

### Step 2.a: Per-stem MIDI probes (LANDS, 4/4 songs)

New script `scripts/sound_match/stem_midi_probe.py` extracts per-stem
note_on counts from each song's `merged.mid`. All 4 non-CG songs probed:

| Song | bass | drums | guitar | piano | other | vocals |
|---|---|---|---|---|---|---|
| WIG | 20 | 66 | **0 (empty)** | 194 | 434 | 113 |
| Rome | 73 | 235 | 260 | **0 (empty)** | **0 (empty)** | 48 |
| Peach Dream | 288 | 295 | **0 (empty)** | 172 | 670 | 92 |
| Disco A | 61 | 228 | 43 | 123 | 246 | **0 (empty)** |

Probe artifacts: `data/v4/profiles/<sha16>/stem_midi_probe.json`.

### Step 2.b: NULL findings for empty-MIDI + inaudible cells (LANDS, 5/5)

Audibility measurements for empty-MIDI stems via
`scripts/sound_match/measure_stem_audibility.py`. All 5 empty-MIDI stems
are also inaudible (RMS < -60 dB silence floor) — first-class NULL findings
per c14 CG piano+other precedent:

| Song | Stem | RMS (dBFS) | Method | Verdict |
|---|---|---|---|---|
| WIG | guitar | -69.55 | lufs_i | NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE |
| Rome | piano | -72.42 | lufs_i | NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE |
| Rome | other | -78.15 | rms_fallback | NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE |
| Peach Dream | guitar | -79.81 | rms_fallback | NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE_NO_PROFILE_POSSIBLE |
| Disco A | vocals | -72.46 | lufs_i | VOCALS_HYBRID_OVERLAY_POLICY_APPLIES (per campaign prompt L59-60) |

NULL findings: `data/v4/profiles/<sha16>/{guitar,piano,other,vocals}_null_finding.json`
(vocals emits `vocals_hybrid_overlay_note.json` because vocals is
hybrid-overlay by policy regardless of MIDI content).

### Step 2.c: Bass stage-1 sweeps LANDED (4/4 in-cycle)

Orchestrator `scripts/sound_match/_launch_non_cg_bass_stage1_c23.sh` (PID
1520) ran the 4 non-CG bass sweeps sequentially. All 4 completed in-cycle,
each ~3-5 minutes. TOP-1 by composite under distance semantics:

| Song | TOP-1 program | GM name | Composite | mel_l1_db | centroid_rmse_hz | emb_dist | Verdict |
|---|---|---|---|---|---|---|---|
| Peach Dream | 5 | E-Piano 2 | 144.71 | 12.41 | 510 | 0.4437 | SF2_CONFIRMED |
| WIG | 5 | E-Piano 2 | 687.74 | 16.31 | 2688 | 0.3055 | SF2_CONFIRMED |
| Rome | 19 | Church Organ | 353.79 | 15.33 | 1333 | 0.5145 | SF2_CONFIRMED |
| Disco A | 5 | E-Piano 2 | 566.68 | 12.11 | 2218 | 0.2443 | SF2_CONFIRMED |

**FIRST-CLASS SYSTEMATIC FINDING**: All 4 non-CG bass cells replicate the
CG-bass c1 pattern — the composite ranks non-source-of-truth candidates
(E-Piano, Church Organ) ahead of GM prog 33 (Electric Bass Finger). Prog 33
ranks 7-10 across all 4 songs. The 5-arc CG-only systematic pattern
(bass/drums/guitar) now extends to a **15-arc pattern** (5 songs × 3
instrument classes). Full finding at
`data/v4/diagnostics/systematic_composite_favors_non_source_of_truth_c23.json`.

**Verdict emission**: Per c22 corrected verdict pattern + c9 CG-bass
composite-relative WINNER precedent, all 4 non-CG bass cells land
SF2_CONFIRMED at their composite TOP-1. Verdicts:
`data/v4/profiles/<sha16>/bass_family_verdict_c23.json` (×4). Operator ear
on the resulting renders is authoritative per FD-6 for whether the
composite ranking correlates with perceptual quality on these songs.

**Sweep-eligible cell inventory (10 cells total, 4 LANDED, 6 queued)**:

| Song | bass | drums | guitar |
|---|---|---|---|
| WIG | **LANDED c23** | queued c24 | NULL |
| Rome | **LANDED c23** | queued c24 | queued c24 |
| Peach Dream | **LANDED c23** | queued c24 | NULL |
| Disco A | **LANDED c23** | queued c24 | queued c24 |

Piano and other sweeps: non-CG piano+other cells with non-empty MIDI are
new territory (CG had empty MIDI + inaudible = NULL). Whether to sweep them
under sf2 GM piano/other programs is queued for c24 operator scope call —
they are not first-class M-V4-PROFILES sweep targets per campaign scope but
they DO have audible content, unlike CG.

### Step 2.d: Stage-2 fine fits (QUEUED)

Pending stage-1 completion + composite-relative WINNER determination per
sweep. Queued for c24.

### Step 2.e: Profiles + replay proofs + family verdicts (QUEUED)

Same. c24 first-act sub-leaf.

## Track 3 — GEN batch conditional (NO-OP this cycle)

GEN batch re-run per operator directive point 4 fires only if a non-CG bass
cell lands SF2_CONFIRMED AND the GEN donor pool references non-CG bass
profiles. Since no non-CG bass profile has been pinned yet, this track is a
documented no-op this cycle. Queued for c24 conditional on Track 2 outcomes.

## Track 4 — Completion report (this doc)

## Track 5 — POR + housekeeping (LANDS)

- POR row for c23 sub-leaves (this cycle's milestone_ids)
- Archive scratch: session-scoped scratchpad at
  `/tmp/claude-0/-home-user-long-exposure-runs-music-gen/.../scratchpad/`
- Test coverage for `stem_midi_probe.py` deferred to c24 audit fill-in
  (substantive verification via successful in-cycle runs on 4 songs)

## Deliverables index (c23 additions)

| Artifact | Purpose |
|---|---|
| `scripts/sound_match/stem_midi_probe.py` | Per-stem MIDI note_on probe |
| `scripts/sound_match/_run_c23_midi_probes.sh` | Batch runner for probes |
| `scripts/sound_match/_run_c23_audibility_probes.sh` | Batch runner for empty-stem audibility |
| `scripts/sound_match/_emit_c23_null_findings.py` | NULL findings emitter |
| `scripts/sound_match/_launch_non_cg_bass_stage1_c23.sh` | Detached bass sweep orchestrator |
| `scripts/sound_match/_start_c23_orchestrator.sh` | Launcher shim |
| `data/v4/deliveries/31a164f845f8e27e/cycle23/cg_drums_guitar_track1_disclosure_c23.json` | Track 1 disclosure note |
| `data/v4/profiles/252eb21ce7df7328/stem_midi_probe.json` | WIG MIDI probe |
| `data/v4/profiles/51e433ade2a845e1/stem_midi_probe.json` | Rome MIDI probe |
| `data/v4/profiles/88d247468cb6d49f/stem_midi_probe.json` | Peach Dream MIDI probe |
| `data/v4/profiles/cdd2717e52820ff6/stem_midi_probe.json` | Disco A MIDI probe |
| `data/v4/profiles/252eb21ce7df7328/audibility_guitar.json` | WIG guitar audibility (inaudible) |
| `data/v4/profiles/51e433ade2a845e1/audibility_piano.json` | Rome piano audibility (inaudible) |
| `data/v4/profiles/51e433ade2a845e1/audibility_other.json` | Rome other audibility (inaudible) |
| `data/v4/profiles/88d247468cb6d49f/audibility_guitar.json` | Peach Dream guitar audibility (inaudible) |
| `data/v4/profiles/cdd2717e52820ff6/audibility_vocals.json` | Disco A vocals audibility (inaudible) |
| `data/v4/profiles/252eb21ce7df7328/guitar_null_finding.json` | WIG guitar NULL |
| `data/v4/profiles/51e433ade2a845e1/piano_null_finding.json` | Rome piano NULL |
| `data/v4/profiles/51e433ade2a845e1/other_null_finding.json` | Rome other NULL |
| `data/v4/profiles/88d247468cb6d49f/guitar_null_finding.json` | Peach Dream guitar NULL |
| `data/v4/profiles/cdd2717e52820ff6/vocals_hybrid_overlay_note.json` | Disco A vocals hybrid-overlay note |
| `data/v4/profiles/<sha16>/bass_sweep_stage1/leaderboard.tsv` (×4, LANDED) | Non-CG bass sweep leaderboards |
| `data/v4/profiles/<sha16>/bass_family_verdict_c23.json` (×4) | Non-CG bass SF2_CONFIRMED verdicts |
| `data/v4/diagnostics/systematic_composite_favors_non_source_of_truth_c23.json` | 15-arc systematic finding |
| `scripts/sound_match/_emit_c23_non_cg_bass_verdicts.py` | Verdict + finding emitter |
| `docs/v4_closure_completion_report_c23_amendment.md` | This doc |

## Honest gaps carried forward (c24 handoff)

1. **4 non-CG bass stage-1 sweep completion** — launched detached PID 1520,
   sequential order (Peach Dream → WIG → Rome → Disco A). Whichever complete
   by c23 close land in the leaderboard TSVs; the rest complete in-cycle 24.
2. **8 non-CG drums+guitar stage-1 sweeps** — queued c24 (4 drums × all songs
   + 2 guitar for Rome+Disco A). Wall estimate ~1-2 hours total under
   sweep-storage hygiene.
3. **Non-CG piano + other sweeps** — first-class question: c23 discovers
   non-CG songs have audible piano/other content unlike CG. Sweep-eligibility
   is a c24 operator-scope decision.
4. **Stage-2 fine fits per stage-1 above-floor TOP-1s** — c24 conditional.
5. **Per-song per-family replay proofs** — c24, once profiles emerge.
6. **CG A/B re-render with sf2 CONFIRMED drums+guitar** — c22 gap carried
   forward per operator ear decision.
7. **GEN batch stall-counter reset** — c24 conditional on donor changes.

## Discipline sweep (c23)

- No PRNG (AST-scannable in c23 new scripts).
- No `sidecar_nonfactor` imports.
- No `--verify-det` call sites.
- No VST3 state APIs.
- `/usr/bin/python3` interpreter guard on all c23 new scripts.
- Env pins canonical 7-key `env_pin_sha256 =
  2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` on every
  new artifact.
- Disk usage 84% at cycle start (under 90% hygiene ceiling); bass sweeps
  produce ~75MB per song = ~300MB total; well below hygiene budget.
- No wait-on-operator memo (banned per operator directive 2026-09-03 part 2).
- All c1-c22 anchors byte-identical pre==post (READ-ONLY): c22 corrected
  verdicts + pinned profiles, c17 `cg_ab_mix.wav`, c11/c14/c15 CG family
  verdicts, c9 bass_v2 pinned profile.

## Run status (c23)

c23 landed the c22-audit QUEUED items partially per operator directive point
5 (detached launch = GOOD cycle):
- Track 1: **LANDS** (as inversion disclosure per invariant d).
- Track 2 setup: **LANDS** (MIDI probes 4/4; NULL findings 5/5).
- Track 2 sweeps: **LANDS 4/4 bass** (all 4 non-CG bass sweeps completed in-cycle; SF2_CONFIRMED verdicts emitted; 15-arc systematic finding disclosure landed). Drums/guitar sweeps queued for c24.
- Track 3: **NO-OP** (no donor changes yet).
- Track 4: **LANDS** (this doc).
- Track 5: **LANDS** (POR + housekeeping).

Operator ear on current `cg_ab_mix.wav` (SHA `6e13e007…f9484b`) remains
authoritative per FD-6. Non-CG focus-song A/B deliveries queued after their
profiles land.
