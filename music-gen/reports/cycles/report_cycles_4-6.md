---
title: "Music-Gen v3 SPINE Milestone — Cycles 4–6"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 SPINE Milestone — Cycles 4–6

## Abstract

This report covers three consecutive cycles of work on the M-V3-SPINE milestone of the Music-Gen v3 campaign, executed on the reference track *Chicken Grease* (source SHA-16 `31a164f845f8e27e`) over a 30-second window. Cycle 3 had halted at the pre-registered STOP clause after finding that MuScriptor's MIDI container serialization was content-dependently nondeterministic on the bass stem, even though the underlying JSON event stream was byte-identical across runs. Cycles 4–6 close that halt by (a) building a canonical MIDI serializer downstream of the deterministic JSON events (Option A), (b) extending the end-to-end pipeline from the compatibility 0–30 s window onto the operator-chosen exposed section at 233.64–263.64 s, and (c) attributing the previously unexplained cross-cycle drift on the guitar stem to a specific torch installation reachable from the system Python interpreter. All three cycles land with the `blocked_on_operator` flag set: the pipeline is byte-deterministic within each cycle and structurally sound, but the only accepted authority for a positive verdict is operator ear judgment on the two delivered A/B pairs, which had not yet arrived at the time of this report. A moderate finding from Cycle 5 — that the c53-era rc7 equalization-and-loudness chain and the plain broadband RMS-match chain produce numerically distinct full-mix reconstructions — was closed in Cycle 6 as an expected first-class property of the two methods rather than a defect to be smoothed away.

## 1. Introduction

The v3 campaign follows a documented pivot away from hand-rolled DSP transcription (permanently banned by Fixed Decision 1) toward a "simplest robust pipeline": source separation → symbolic transcription via a single approved transcriber (MuScriptor) → deterministic re-synthesis and mix-match. The M-V3-SPINE milestone is the spine of that pipeline. Its acceptance rubric is a three-verdict scheme with a STOP-at-rung-1 clause: if the byte-determinism guarantee fails on any probe, the chain halts before proceeding to structural or perceptual gates. Cycle 3 hit exactly that STOP because two consecutive MuScriptor MIDI serializations of the bass stem differed at byte offset 40 across 365 bytes, while the JSON event dump underlying those MIDI files was byte-equal.

Cycles 4–6 pick up from three concrete operator directives issued after Cycle 3:

1. **Adopt Option A**: canonicalize authoritative MIDI downstream of the JSON events using a pure, fixed-PPQ, stable-sort serializer. Demote MuScriptor's own MIDI writer to a debug sidecar. Serialization, not transcription — so Fixed Decision 1 is preserved.
2. **Extend the pipeline to the operator-chosen exposed section** (233.64–263.64 s) once the compat 0–30 s pass lands, so the operator has a peak-and-exposed A/B pair to listen to.
3. **Reconcile per-stem-in-favor** whenever the full-mix MIDI and the sum of per-stem MIDIs disagree.

This report describes what those three cycles did, what they found, and what remains open.

## 2. Methodology carried across all three cycles

### 2.1 Rubric v2 and its integrity chain

Cycle 4 froze a new rubric (`v3_spine_rubric_v2`) before writing any pipeline code, redefining the byte-determinism gate to apply to (a) the JSON event dump, (b) the canonicalized MIDI, and (c) the downstream rendered artifacts, rather than to MuScriptor's MIDI output directly. The rubric document's SHA-256 (`c49db5a12e955f26…451a`) is pinned by a three-way byte-equality assertion — the document hash on disk, a sidecar hash file, and the hash embedded in each cycle's verdict JSON must match on every cycle. This chain held byte-identically across all three cycles and was independently re-verified by the auditor at each pass. Cycle 3's rubric v1 (`b0031164…4b555`) is preserved read-only as a historical anchor.

### 2.2 Determinism protocol

Every stem-level artifact — separated audio, JSON event dump, canonical MIDI, per-track rendered WAV — is generated twice into fresh temporary directories under a fixed environment (`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, single-threaded BLAS, `torch.manual_seed(0)`), and its SHA-256 is asserted equal across the two runs. A mismatch on any single probe fires the STOP clause and halts the cycle.

### 2.3 Anchor preservation

At the start of each cycle a snapshot of every read-only artifact from prior cycles (delivery WAVs, canonical MIDIs, locked scripts, the SoundFont, the focus set) is recorded, and at the end of the cycle every anchor is re-hashed and required to match. The count grew from 36 anchors at Cycle 4 to 71 by Cycle 6; all matched pre-vs-post at every cycle, with the auditor independently spot-checking six anchors per cycle.

### 2.4 Fixed environment and interpreter

All pipeline scripts invoke `/usr/bin/python3` explicitly (verified by an AST test guard), with a single-threaded BLAS pin and the environment variables above set via `os.environ.setdefault`. Egress remained blocked at the network layer for all three cycles; the auditor ran an AST scan for `urllib`, `requests`, `httpx`, `socket`, `http`, and `aiohttp` imports and confirmed zero network dependencies in every new script.

## 3. Cycle 4: canonical serializer lands, pipeline reaches the 0–30 s window

Cycle 4 implemented Option A end-to-end.

**Canonical serializer.** A pure function `midi_from_json_events(json_path, out_path, tempo_bpm, time_signature)` was specified before any code was written, then implemented with PPQ fixed at 480, sort key `(tick, channel, pitch, event_kind)` with note-on ordered before note-off, a deterministic instrument-to-channel map, an empty-events baseline, and an atomic write via `tempfile.NamedTemporaryFile` + `os.replace`. The `mido` library was pinned via `importlib.metadata.version` because the shipped 1.3.3 release does not expose `__version__`. Twelve unit tests covered PPQ, sort-key reproducibility, on-before-off, empty-events baseline, the mido pin, byte-determinism ×2 on 3-note / 12-note / empty inputs, absence of any pseudo-random number source or wall-clock reference (grep-verified), the channel map, dangling note-start handling, and the seconds-to-ticks conversion. All twelve passed.

**MuScriptor JSON re-run and a new drift finding.** The second run of MuScriptor with `--format json` on the six stems plus the full-mix slice completed the ×2 requirement Cycle 3 had left open. Six of seven probes produced JSON byte-identical to their Cycle 3 hash. The guitar stem did not: the Cycle 3 hash was `97b5a598…db8424bb` (1168 notes, first event at 0.25 s); the Cycle 4 hash was `3107ba21…e10acc70` (824 notes, first event at 0.24 s). Two consecutive Cycle 4 invocations of the guitar probe agreed with each other, so the drift is between Cycle 3 and Cycle 4, not intra-cycle. Attribution was deferred to Cycle 5.

**Canonical MIDI determinism.** All seven probes serialized twice into fresh temporary directories via the new serializer produced byte-identical MIDI: `f6097216…` (drums), `609b2b8059af4468…` (bass), `4afb8a32…` (guitar), `8a00d5ad…` (vocals), `6062acb1…` (full-mix), and the pinned empty-events hash `586a53e2…` for the empty `other` and `piano` transcriptions. The rung-1a byte-determinism gate passed.

**Tempo, program map, structural gates.** Tempo was carried forward from the RC5 baseline for the full song at 90.7258 BPM in 4/4. A twelve-label GM program map placed drums on channel 10 and confirmed zero notes on GM program 4 (an operator lock). The six canonical per-stem MIDIs were merged onto the tempo map via `merge_per_stem_midi.py`, producing `merged.mid` at SHA `555b41db…6faf19`, with all four structural gates passing: drums on channel 10 non-empty (183 note-ons), bass median pitch 38 (below 55), zero notes on GM program 4, and a symbolic-only vocals track carrying the `voice_symbolic_do_not_render` text meta.

**Render and A/B.** Fluidsynth (SoundFont SHA `74594e8f…1cb0`, `-r 44100 -o synth.cpu-cores=1`, reverb and chorus disabled) rendered the five non-vocal stems twice, all byte-identical. The htdemucs vocals stem was overlaid as a SHA-verified copy. Per-stem RMS-matching against the baseline six-stem separation, summed and peak-limited to 0.707, produced the 30-second reconstruction at SHA `281a3bc6…`, byte-deterministic across two runs.

**Full-mix reconciliation.** The full-mix canonical MIDI carried 490 note events; the sum of per-stem MIDIs carried 1010. Per operator directive point 4, the sum-of-stems was chosen as canonical; the full-mix-only findings were logged but not auto-merged.

**Panel and honest disclosures.** The eight-metric perceptual panel (mel L1, spectral-centroid RMSE, RMS-envelope RMSE, integrated-LUFS RMSE, VGGish cosine distance, and three others) was computed with all values finite. The panel is explicitly **not** an acceptance gate — Fixed Decision 6 reserves that authority for operator ear. The Cycle 4 A/B window was 0–30 s of the source, not the operator-chosen 233.64–263.64 s section; the reason, disclosed in the delivery, is that the RC9 six-stem baseline separation on disk covered only the first 30 s. Extending it to the operator section became Cycle 5's task.

Cycle 4 total wall time was approximately 15 minutes, dominated by the ~5.7 minutes of guitar-probe MuScriptor invocations (three passes). The verdict shipped as `V3_SPINE_CHAIN_LANDS_pending_operator`, blocked on operator ear.

## 4. Cycle 5: pipeline extended onto the operator-chosen section

Cycle 5 executed the same pipeline on the exposed section at 233.64–263.64 s that the D1 auto-picker had identified from the focus set, while also opening the first attribution probe on the Cycle 4 guitar drift.

**Section separation and transcription.** A fresh ffmpeg slice of the source over the operator window was fed into htdemucs, producing six stems that were byte-identical across two runs (six stems × two runs = twelve matching hashes). MuScriptor with `--format json` ran twice on each of the six stems plus the full-mix slice; all fourteen hashes matched. The seven canonical MIDIs likewise matched across two serializations. All four structural gates on the merged file passed on the operator section; per-track fluidsynth render produced five byte-identical stems; the vocals overlay was a SHA-verified copy of the section's htdemucs vocals. Loudness targets were recomputed fresh from the operator-section baseline (the RC9 baseline had covered only 0–30 s), the mix-match ran twice with byte-identical results, and the operator-section reconstruction was delivered alongside the original slice.

**Env-drift audit — first attempt.** A snapshot of the 87 packages inside `workspace/learned_transcribers_venv` was captured as a `c5_baseline`; there was no prior venv snapshot on disk to diff against. A separate probe attempted to reproduce the Cycle 3 guitar JSON hash by re-invoking MuScriptor under the venv's package versions. It reported `probe_status = deferred_egress_blocked`: without pip history from the Cycle 3 era, without cached wheels covering the transitive closure, and with egress forbidden, no closed-form reproduction was possible from inside the venv. The attribution verdict was recorded as `ENV_DRIFT_PROBE_DEFERRED`. Importantly, this deferral does not invalidate Option A — the canonical serializer is a pure function of its JSON input, so whatever caused the JSON to shift between cycles does not compromise the determinism of the MIDI-and-render chain within a single cycle.

**Anchor preservation.** All 57 anchors held byte-identical; sixteen tests passed; the promise-check post plan-of-record update surfaced zero errors.

**Operator handoff at end of Cycle 5.** Two A/B pairs now sat on disk: the Cycle 4 compat pair over 0–30 s and the Cycle 5 exposed-section pair over 233.64–263.64 s. Two moderate items remained open: the deferred environment attribution and a question about whether the plain RMS-match mix path used in Cycle 5 was numerically equivalent to the c53-era rc7 equalization-plus-loudness path that predated the v3 pivot.

## 5. Cycle 6: attribution closed, method-equivalence resolved

Cycle 6 ran as a two-track substantive cycle in the continued absence of an operator ear verdict.

### 5.1 Track A: environment-drift attribution

A local-only filesystem scan across `/root`, `/home`, `/var/cache/apt`, `/var/lib/apt`, `/var/lib/dpkg`, `/var/lib/docker`, `/opt`, `/usr/lib`, `/usr/local/lib`, and `/tmp` enumerated every torch installation reachable from the machine. Two were found:

| Location | Version |
|---|---|
| `/usr/local/lib/python3.11/dist-packages/torch-2.13.0+cpu.dist-info` | 2.13.0+cpu |
| `workspace/learned_transcribers_venv/lib/python3.11/site-packages/torch-2.14.0+cpu.dist-info` | 2.14.0+cpu |

The Cycle 3-era `torch 2.13.0+cpu` is installed at the *system* interpreter path and is directly importable from `/usr/bin/python3` without any venv activation. The Cycle 5 baseline of `torch 2.14.0+cpu` lives inside the venv. The auditor independently reproduced this at the shell:

```
$ /usr/bin/python3 -c "import torch; print(torch.__version__, torch.__file__)"
2.13.0+cpu /usr/local/lib/python3.11/dist-packages/torch/__init__.py
```

This is a coherent mechanism for the Cycle 3-versus-Cycle 4 guitar drift: any Cycle 3-era subprocess invoked through `/usr/bin/python3` was picking up the system-wide torch 2.13 from `dist-packages`, while Cycle 5's venv audit correctly reported 2.14 from `site-packages` — the two audits were looking at different Python environments and were both correct.

The AST test guard confirmed zero network syscall attempts in the scan script and its two siblings. The scan output was byte-identical across two runs. Attribution was upgraded from `DEFERRED` to `ENV_DRIFT_PROBE_CANDIDATE_FOUND_C7_REPRODUCE`; the drafted reproduction command was recorded but not executed, pending operator approval, in accordance with the standing constraint against retuning without operator sign-off.

One earlier statement was refined in light of this finding: the Cycle 5 conclusion that "no c3-era wheel is cached locally" is technically still true (the venv's wheel cache is empty for torch 2.13), but the c3-era torch is present on the system Python — reached by interpreter path, not by wheel install.

### 5.2 Track B: method-equivalence between the two mix chains

Two mix chains were compared on the same operator-section per-track WAV inputs:

| Property | Method A (Cycle 5 canonical) | Method B (rc7 v3-paths fork) |
|---|---|---|
| Chain | plain per-stem RMS-match (gain clamp ±24 dB) → sum → peak-limit 0.707 → int16 | 12-band log-spaced iirpeak EQ (Q=1.4) → RMS loudness match (max 48 dB) → sum → peak-limit 0.999 → deterministic-canonicalize |
| Full-mix SHA | `cc919559b4508b6b…` (from Cycle 5) | `f40796be982998b0…` (this cycle) |

Both chains are internally byte-deterministic across two runs on their own inputs. On the operator-section full-mix, the two chains produce reconstructions that are strongly correlated but not equivalent:

| Metric | Value |
|---|---:|
| max absolute sample-difference | 0.5021 |
| RMS delta | 2.68 dB |
| short-term LUFS delta | 2.27 LU |
| Pearson correlation | 0.9649 |

Interpretation: the twelve-band iirpeak EQ in Method B reshapes each stem's spectrum before the loudness match, whereas Method A applies a single broadband gain. The two chains retain the same underlying signal (correlation stays at 0.96) but with meaningfully different tonal shaping. Under the campaign's Fixed Decision 1 — that observed method disagreement is a first-class finding, not a defect to smooth over — the Cycle 5 open item closes as `MODERATE_2_METHODS_DIFFER_EXPECTED`. No code was changed: the Cycle 5 plain-RMS chain remains the canonical A/B path for now, because retuning without operator ear input is disallowed. The choice of which chain to promote as canonical is now an operator-facing decision.

### 5.3 Discipline

Cycle 6 delivered 71 preserved anchors (all matching pre-versus-post), 17 tests passing (17/17 on independent re-run under the mandated environment), the three-way rubric hash chain unchanged, and zero promise-check errors. Egress remained blocked; no network calls were attempted. Both spec documents were written before their implementation scripts (verified by a modification-time gate: each spec's mtime precedes each script's by 48–133 seconds). Every SHA claimed in the worker's delivery was reproduced by the auditor's independent spot-check (12/12).

## 6. Current state and open decisions

At the end of Cycle 6 the M-V3-SPINE pipeline is complete on both the 0–30 s compat window and the 233.64–263.64 s operator-chosen section, byte-deterministic within any given cycle, structurally sound, and preserved across cycles by a 71-anchor byte-integrity chain. The chain's positive-verdict authority is by design operator ear, and no ear verdict has arrived on either A/B pair. Three operator-gated decisions are queued:

1. **Ear verdict** on either A/B pair. A "lands" verdict on either opens M-V3-FOCUS-1 (the five-song set: *Chicken Grease* mandatory plus four SHA-256-tiebreak picks from `data/recreate_v2/focus_set_v2.json`). A negative verdict pivots to the operator-named failure axis.
2. **Approval to execute the Torch 2.13 reproduction**. The mechanism is attributed; the reproduction command is drafted; the actual re-run of MuScriptor on the Cycle 4 guitar stem under `/usr/bin/python3` needs only permission. If the run reproduces the Cycle 3 guitar JSON hash, the drift is fully closed. If it does not, the finding that "torch version alone is not the drift factor" is itself first-class.
3. **Canonical mix-chain choice**. Two byte-deterministic-within-cycle reconstructions now exist on disk: the Cycle 5 plain-RMS `cc919559…` and the Cycle 6 EQ-plus-loudness `f40796be…`. Which chain the operator listens to next, and which is promoted to canonical, is a policy call, not a code change.

A minor cosmetic finding from Cycle 6 remains a watch item: for the operator-section `other` and `piano` stems whose canonical MIDI is empty, the per-track renderer emits a nominally 2-second silent WAV rather than a 30-second silent one; both methods produce identical output, and the summed full mix is exactly 1 323 000 samples (30 s at 44.1 kHz), so the per-stem file length is a cosmetic artifact rather than a defect.

## 7. Conclusions

Over three cycles the v3 SPINE pipeline moved from a hard STOP on nondeterministic MIDI serialization (Cycle 3) to a determinism-closed, operator-section-covered, structurally-gated end-to-end chain with a mechanistically attributed explanation for the one cross-cycle drift previously outstanding. The canonical-serializer path (Option A) has proved a good fit for the constraint of banning hand-rolled transcription: the JSON event stream from an approved transcriber remains the authority; the MIDI file is a downstream, purely functional projection of those events; and every intermediate artifact is byte-deterministic within each cycle. The Cycle 6 method-equivalence audit demonstrates the value of Fixed Decision 1's treatment of numerical disagreement as evidence rather than error — the two mix chains differ in tonal shaping in a way that is fully explained by their DSP designs, so the disagreement is information for the operator, not a bug to hide.

The remaining work on this milestone is not code; it is three operator decisions. If any of them arrive before the next cycle, the milestone can advance. If none do, the harness has a substantive Track A next cycle already lined up (execute the torch-2.13 reproduction, if approved) and a substantive Track B (draft a one-page loudness and spectral characterization comparing the two mix chains to inform the canonicity choice).

## Appendix: Implementation Details

### A.1 Delivered artifacts by cycle

Cycle 4, under `data/v3/deliveries/31a164f845f8e27e/`:
`original_ab.wav`, `reconstruction_ab.wav`, `full_reconstruction.wav`, `panel.json`, `panel.tsv`, `manifest.json`, `verdict.json`, `muscriptor_nondeterministic.json`.

Cycle 5, under `.../operator_section/`:
`original_ab_operator_section.wav`, `reconstruction_ab_operator_section.wav`, `full_reconstruction_operator_section.wav`, `panel.json`, `panel.tsv`, `manifest.json`, `verdict.json`.

Cycle 6, under `.../cycle6/`:
`verdict_c6.json`, `env_drift_deep_dive.json`, `rc7_method_equivalence.json`.

Working artifacts under `data/v3_spine/31a164f845f8e27e/`: `canonical_midi_determinism.json`, `merged.mid`, `merged_midi_sha.txt`, `full_mix_reconciliation.json`, `gm_program_map_v3_extensions.tsv`, `tempo_choice.json`; `operator_section/` subtree with `htdemucs_determinism.json`, `muscriptor_determinism.json`, `canonical_midi_determinism.json`, `render/` renders, `mix_match_operator_section.json`; `anchor_preservation.json` and `anchor_preservation_post_c6.json`.

Docs authored: `docs/v3_spine_rubric_v2.md`, `docs/v3_spine_canonical_midi_serializer_spec.md`, `docs/v3_spine_venv_delta_audit_spec.md`, `docs/v3_spine_rehtdemucs_operator_section_spec.md`, `docs/v3_spine_env_drift_deep_dive_spec.md`, `docs/v3_spine_method_equivalence_rc7_spec.md`.

Scripts added: `scripts/v3_spine/midi_from_json_events.py`, `merge_per_stem_midi.py`, `env_drift_deep_dive.py`, `rc7_v2_rerun_v3_paths.py`, `method_equivalence_rc7.py` (and cycle-specific driver scripts co-located).

### A.2 Test suites

12 tests for the canonical serializer (Cycle 4), 16 additional cycle-scoped tests (Cycle 5), 17 cycle-scoped tests (Cycle 6). All test files pass on independent re-run under the mandated environment (`PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 BLAS=1`, `/usr/bin/python3`).

### A.3 Environment pins used across all three cycles

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; single-threaded BLAS; `torch.manual_seed(0)`; MuScriptor model SHA `ac80adbd…7fb97ec`; SoundFont SHA `74594e8f…1cb0`; `mido==1.3.3` verified via `importlib.metadata.version`; interpreter `/usr/bin/python3` (guard verified by AST test).

### A.4 Integrity chains

Three-way rubric-v2 hash chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a1…451a` equals `data/v3_spine/rubric_hash_v2.txt` content equals `verdict.json.rubric_hash_v2`, on every cycle. Track A spec-hash chain (Cycle 6): document SHA `a2631e99…4152` equals `env_drift_deep_dive_spec_hash.txt`. Track B spec-hash chain (Cycle 6): document SHA `7869696e…c7e1` equals `method_equivalence_rc7_spec_hash.txt`. Modification-time gate for Cycle 6: both specs were saved 48–133 s before their implementation scripts. Anchor snapshot counts pre/post: 36→36 (Cycle 4), 57→57 (Cycle 5), 71→71 (Cycle 6), with independent auditor spot-checks of ≥5 anchors per cycle, all byte-identical.

### A.5 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 4 | 734586af-8851-4ea1-9fed-d08f87a0924c | ef5837fc-d75c-4a14-886f-ef682b36e884 | 4b8d78ef-5fc0-4484-845f-000c3e06319b |
| 5 | c6fdb545-440e-412d-b3af-6631700078ad | 771ddeba-e9a5-4c25-8d2d-4254c89c11c1 | 0348ed0f-8179-4af4-a7e9-e255d5f2b2d3 |
| 6 | f45de57c-b370-4b9d-9490-6c13934d3af0 | af1da82b-d40e-4d6e-a2bf-14b4860fcf48 | 7f0e4473-0b56-4da0-8195-c4627500da45 |

Cycle-scoped reports are on disk at `docs/v3_spine_report_cycle4.md`, `docs/v3_spine_report_cycle5.md`, `docs/v3_spine_report_cycle6.md`.

### A.6 Wall-time budgets

Cycle 4 total ≈15 min (dominated by ~5.7 min of MuScriptor guitar-stem invocations). Cycle 5 wall time recorded step-by-step in the delivery's `verdict.json.operator_notes`, all subprocess-serial in-turn. Cycle 6 wall time recorded in `verdict_c6.json`.

### A.7 Auditor reconciliation

All three cycles were independently validated. Cycle 4 audit and Cycle 5 audit confirmed the byte-determinism chain, the anchor preservation, and the honest disclosure of the guitar drift and A/B window scope. The Cycle 6 audit (`VALIDATED`) independently reproduced the torch-2.13 attribution at the shell, spot-checked 12 SHAs (all matching), verified the two spec-hash chains and the modification-time gate, ran the 17-test suite green on an independent invocation, and confirmed the AST no-network guard and byte-determinism sidecar on the two new WAV artifacts. No critical findings; two minor observations were noted for future cycles: prefer a single archive ledger row per cycle (Cycle 6 emitted two), and adopt a stable `cycle<N>/` delivery subdirectory convention (three cycles used three different naming patterns).
