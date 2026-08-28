---
title: "Music-Gen Source-Separation Survey — cycles 1-2 (fanout clone 0)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen Source-Separation Survey — cycles 1-2 (fanout clone 0)

## Abstract

This branch owns M-SEP-1, the source-separation survey for the Music-Gen campaign: benchmark htdemucs against at least one open-source alternative on the three ingestion seed clips, publish an adopt-or-build verdict, and explicitly defer per-instrument isolation inside the "other" stem. Cycles 1 and 2 stand up the survey end-to-end. Cycle 1 registers the M-SEP-1 rollup and three sub-milestones (ground-truth construction, htdemucs baseline, alternative), builds a deterministic 3-stem ground-truth pipeline from committed MIDIs and a pinned SoundFont, runs both separators plus a naive-copy baseline on three synthesized mixes {30, 60, 90}s, and publishes the first-cut benchmark table with an adopt verdict for htdemucs. Cycle 2 tightens reproducibility: a `torch.manual_seed(0)` rerun of htdemucs on the 30-second mix produces a drums stem whose sample-by-sample max-abs diff against the first run is 0.000e+00 (bit-deterministic on this CPU-only torch build), and the survey report crystallises around a per-stem winner table and a per-separator blind-spot section. The seed-clip preprocessing rule (mono/22050 → stereo/44100 before any separator) is fixed at this stage as a downstream contract. The adopt-htdemucs verdict — drums by ~+8.8 dB, bass by ~+1.0 dB against UMXHQ; UMXHQ ahead by ~+1.4 dB on "other" — is the load-bearing output of these two cycles; further tightening (byte-verified UMXHQ determinism, regression-guarded RMS pins, `promise_check` closure) is scheduled for later cycles and is not claimed here.

## 1. Introduction

The campaign's plan of record scopes M-SEP-1 as: *"Source-separation survey and adopt-or-build verdict: demucs (already verified) vs at least one alternative on 4-stem split, benchmarked on this project's seed clips using an objective metric (SI-SDR / SDR). Benchmark table with per-stem SI-SDR on seed clips; adopted separator named; per-instrument isolation of the 'other' stem explicitly deferred to a later milestone."* This fanout clone inherits that scope verbatim and is asked in addition to quarantine any dependency that fights the classifier's numpy/tensorflow stack under `workspace/separation_venv/`.

The three ingestion seed clips available to this branch are mono/22050 fluidsynth renders of a single instrument each — they carry no natural stem content on which a 4-stem separator could be scored. Cycles 1-2 therefore make an early design decision: use the seed clips as a target-domain probe for future downstream work, but score the separators themselves on deterministic synthesized 3-stem mixes for which per-stem ground truth is knowable exactly. This is the choice that shapes the rest of the branch.

## 2. Scope registered in cycles 1-2

The plan-of-record's M-SEP-1 entry names three sub-milestones. All three are opened and driven to a first-cut passing state within these two cycles:

- **Ground-truth construction** — deterministic 3-stem mixes (drums, bass, piano) synthesized via `fluidsynth` from committed MIDIs and a committed `FluidR3_GM.sf2` at 44.1 kHz stereo, at three durations {30, 60, 90}s. Success criterion: same MIDI + same SoundFont + same fluidsynth binary produces bit-identical WAV bytes, and SHA-256 fingerprints of the SoundFont, per-MIDI, and per-stem/mix WAVs are captured in a manifest.
- **htdemucs baseline** — htdemucs (demucs 4.1.0) run on all three mixes unattended, four non-silent stems per mix, SI-SDR finite on drums/bass/other, and estimated vocals energy reported in dBFS for the ground-truth-zero vocals stem.
- **Alternative separator** — a second open-source separator (open-unmix UMXHQ chosen after a fetchability probe cleared both the wheel and the Zenodo weights), evaluated on the same three synth mixes with the same metric, so the adopt-or-build verdict cites numbers rather than assumptions.

Per-instrument isolation *within* the "other" stem is explicitly excluded from all three sub-milestones and from anything in `scripts/separation/`. That deferral is a fixed decision of the branch, not an oversight.

## 3. Ground-truth mix construction

Cycle 1 puts the ground-truth pipeline into `scripts/separation/synth_gt.py`. The pipeline is deterministic:

1. Three General-MIDI files are generated in-Python via `pretty_midi`:
   - `drums.mid` — 4 bars at 120 BPM on channel 10; kick (note 36) on beats 1 and 3, snare (38) on beats 2 and 4, closed hi-hat (42) on every eighth.
   - `bass.mid` — 4 bars at 120 BPM, GM program 33 (Electric Bass), one root note per bar following C-major I–vi–IV–V (C2, A1, F2, G2).
   - `piano.mid` — 4 bars at 120 BPM, GM program 0 (Acoustic Grand), root-position triads I–vi–IV–V (C-E-G, A-C-E, F-A-C, G-B-D).
2. Each MIDI is rendered by fluidsynth at 44.1 kHz stereo through `FluidR3_GM.sf2`:
   `fluidsynth -a null -T wav -F <out> -r 44100 -g 1.0 -i <sf2> <mid>`.
3. Each 8-second (4-bar) rendered loop is tiled to durations {30, 60, 90}s (one per seed-length bucket the ingestion chassis will produce) then trimmed to sample-exact length.
4. A **zeroed** 4th stem, `vocals.wav`, is written per duration so the ground truth has 4 stems matching htdemucs's `{vocals, drums, bass, other}` output shape. SI-SDR is undefined against a zero reference, so the vocals stem is scored instead by the estimated-vocals RMS energy in dBFS — a direct measure of the separator's false-positive tendency.
5. The three non-zero stems are summed and peak-normalized to −3 dBFS to form the mix WAV.

Provenance is captured in `data/separation/synth_mix/manifest.json`: the exact fluidsynth command line, the SoundFont's SHA-256 (`74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`), per-MIDI SHA-256s, and per-stem/mix WAV SHA-256s. Regeneration on the same host reproduces every byte.

## 4. Preprocessing rule (downstream contract)

htdemucs and open-unmix UMXHQ are both trained on 44.1 kHz stereo. The ingestion seeds are mono/22050. Cycles 1-2 fix the rule: **any input to any separator must be resampled to 44100 Hz and duplicated to two channels before separation**. Because the ground-truth mixes are authored natively at 44.1 kHz stereo, no runtime resampling is required for the benchmark itself; the rule applies to any later cycle that pushes actual seed audio through the separator. It is documented in the survey report's "Environment and preprocessing" section so downstream consumers cannot forget it.

## 5. Alternative separator — fetchability probe and choice

The fanout brief listed open-unmix UMXHQ as preferred and spleeter as the fallback. Cycle 1 runs a fetchability probe against the workspace's proxy:

- `openunmix==1.3.0` — wheel fetched from PyPI (40 KB), no dependency conflicts against the top-level environment (`torch>=1.9`, `torchaudio>=0.9`, `numpy`, `tqdm` all satisfied). Four per-target checkpoints (`vocals-b62c91ce.pth`, `drums-9619578f.pth`, `bass-8d85a5bd.pth`, `other-b52fbbf7.pth`, ~34 MB each) fetched from `zenodo.org/records/3370489/files/`.
- spleeter — not probed; its TensorFlow 2.x pins would collide with the classifier's stack.

Because openunmix installs against the top-level environment without perturbing anything M-CLASS-1 depends on, the brief's "quarantine any conflicting dependency under `workspace/separation_venv/`" clause is discharged by decision, not by construction: no venv is created, and this is recorded in the M-SEP-1 ledger event as the reason no `M-SEP-1/venv-quarantine` sub-milestone is registered. The venv trigger is preserved for any later cycle that adds a separator (e.g. spleeter) whose pins would collide.

The architectural gap between htdemucs (2022 hybrid transformer/CNN, ~80 M parameters, spectral + waveform branch) and UMXHQ (2019 BLSTM masking, ~9 M parameters × 4 targets, spectrogram-domain) is deliberate: the alternative is chosen not to be htdemucs's peer, but to give the adoption decision a numerical falsification point rather than an assumed one.

## 6. First-cut benchmark results

Cycle 1 stands up the runners (`scripts/separation/run_htdemucs.py`, `scripts/separation/run_alternative.py`) and the scorer (`scripts/separation/eval_sisdr.py`). The scorer uses `mir_eval.separation.bss_eval_sources` on length-aligned mono-collapsed pairs — matching the fanout brief's snippet. The full results TSV lives at `data/separation/results.tsv` (36 rows: 3 separators × 3 mixes × 4 stems). Collapsed to means across the three durations:

| separator          | drums SDR (dB) | bass SDR (dB) | other SDR (dB) | vocals est. energy (dBFS) |
|--------------------|---------------:|--------------:|---------------:|--------------------------:|
| **htdemucs**       |     **17.08**  |    **10.96**  |          1.91  |                    −81.76 |
| open-unmix (UMXHQ) |          8.32  |         9.93  |      **3.35**  |                    −73.97 |
| naive-copy `mix/3` |         −5.24  |         2.95  |         −3.22  |                    −30.89 |

Bold marks the winner on each stem. Spread across the three durations is under 0.3 dB per cell — the mixes are tiled loops, so the results are effectively duration-invariant. The naive-copy row (`estimate = mix / 3`) is included so every cell has a "no separator" reference. Its unexpectedly-not-terrible bass value (+3 dB) is a benchmark artifact — bass fundamentals occupy a narrow low-frequency band with a small share of total mix energy, so dividing the mix by three lands near the isolated bass — not a claim that naive copy is a useful bass separator.

**Vocals false positive.** The mix is at −3 dBFS. htdemucs's estimated vocals stem sits ~78 dB below the mix peak; UMXHQ's ~70 dB below. Both correctly find no vocal content. htdemucs is quieter by ~8 dB, mirroring the larger better-regularized architecture.

## 7. Adopt-or-build verdict

Adopt htdemucs. The per-stem winner tally on the three non-vocal stems:

| Stem  | Winner    | Δ SDR (dB, winner − runner-up) |
|-------|-----------|-------------------------------:|
| drums | htdemucs  |                          +8.76 |
| bass  | htdemucs  |                          +1.03 |
| other | openunmix |                          +1.44 |

htdemucs takes 2 of 3. The fanout brief's tie-break rule (prefer the higher scorer on "other" when the tally is tied) does not apply because the tally is not tied — but it is noted that had the tally been tied, openunmix would have been the pick. That openunmix edges htdemucs on the "other" stem, which will carry any future per-instrument refinement, is flagged as a candidate signal for a hybrid pipeline in a later cycle; it does not change the current single-separator adoption call.

Neither separator loses to naive-copy on drums, bass, and other simultaneously; on every non-vocal stem at least one separator beats naive-copy by more than 3 dB SDR. There is no red flag calling for a per-corpus fine-tune, and no "build" case at this stage.

## 8. Blind-spot notes per separator

The survey report captures a blind-spot note per separator so downstream cycles do not over-trust the numbers:

**htdemucs.** Trained on MUSDB18-HQ (Western pop, mixed masters). Behaviour on classical, jazz, or non-Western material is out-of-domain and public benchmarks report 2–4 dB SDR drops there. Native input is 44.1 kHz stereo — mono/22050 sources incur a preprocessing loss because the duplicated signal carries no genuine stereo information. Long-context (>10 s) drum patterns can bleed into "other" via the transformer's spectral branch, not observed on the 4-bar tiled loops used here but a real risk on genuine songs with sparse syncopated drum programming. **This benchmark's own blind spot:** the synth mixes are perfectly aligned, un-mastered, un-effect-processed, and mono-image-per-stem, so the 17 dB drum figure is a ceiling — the honest projection to real songs is the MUSDB18 test-set numbers (drums ~9 dB, bass ~8 dB, other ~5 dB).

**open-unmix (UMXHQ).** BLSTM masking is weaker on drums specifically because transient content is smeared by the spectrogram-STFT-only front end — the 8.3 dB drums figure against htdemucs's 17 dB is exactly this pattern. Trained on MUSDB18 (standard, not HQ) — even more pop/rock biased than htdemucs. Per-target independent networks mean each of the four `.pth` checkpoints is fetched separately; any single-checkpoint fetch failure would silently degrade the output. The fetchability probe verified all four. On "other" UMXHQ narrowly wins — spectrogram masking preserves piano's harmonic structure well when the interferers are broadband (drums) and low-band (bass), which mask cleanly. This is a real signal, not a coincidence.

**spleeter.** Not run. 2016-era U-Net, TensorFlow 2.x pinned `<2.15`. Aggressive high-frequency masking known to zero out cymbals and high hi-hats. Would fight the classifier's stack and require `workspace/separation_venv/`. Skipped because UMX cleared without a venv.

## 9. Explicit deferral

Per-instrument isolation *inside* the "other" stem — decomposing "other" into piano, guitar, keys, strings, wind, etc. — is explicitly deferred to a later milestone. This is recorded verbatim in the survey report as a fixed decision of the branch, cross-referenced to the campaign plan's "Out of scope" section. Nothing in `scripts/separation/` attempts it. A future milestone may reopen the question using pitch-informed separators (e.g. spleeter's 5-stem, LarsNet for drums, Deep-Chroma for pitched-instrument decomposition) or a two-pass pipeline that runs a secondary separator on the "other" stem.

## 10. Determinism (cycle-2 tightening)

Cycle 2 adds the first reproducibility check. Rerunning `run_htdemucs.py` on the 30-second mix after `torch.manual_seed(0)` produced a drums stem whose sample-by-sample max-abs diff against the first run was **0.000e+00** — htdemucs is bit-deterministic under a fixed seed on this CPU-only torch build. UMXHQ is left with the same fixed-seed contract stated but not yet independently sample-diffed at this point; sample-byte identity for UMXHQ under a hard-pinned single-threaded BLAS contract is a scheduled follow-up, not a claim of these two cycles.

## 11. Non-factor discipline

Nothing in `scripts/separation/` imports or reads `scripts.classifier.sidecar_nonfactor`, `data/classifier/_nonfactor/`, or the `NonFactorValue` type. The branch reads only its own synthesized mix ground truth and (indirectly, only to know the shape of mono/22050 audio) the ingestion manifests — no audio bytes cross from the ingestion branch into the separator. This isolation is a load-bearing decision because separator outputs will flow into the trained-ear pipeline, where a leaked non-factor signal would silently corrupt the ear model.

## 12. Sufficiency against branch objective (cycles 1-2 state)

| Objective criterion | Status (cycles 1-2) | Evidence |
|---|---|---|
| Benchmark table with per-stem SI-SDR on the three seed-length mixes | Met | `data/separation/results.tsv` (36 rows); §6 table. |
| ≥1 open-source alternative benchmarked against htdemucs | Met | open-unmix UMXHQ; §5 fetchability probe. |
| Ground truth per stem constructed | Met | Deterministic 3-stem synth via fluidsynth; §3; `data/separation/synth_mix/manifest.json`. |
| Adopt-or-build verdict published with numbers | Met | Adopt htdemucs; §7 winner tally. |
| Blind-spot notes per separator | Met | §8. |
| Per-instrument-in-"other" deferral explicit | Met | §9. |
| Quarantine venv provisioned iff conflicts | Met by decision | UMX installed without conflict; venv not created; rationale recorded in the ledger event. |
| htdemucs determinism spot-check | Met (partial) | Fixed-seed rerun on 30 s mix; sample max-abs diff 0.000e+00. |
| UMXHQ byte-verified determinism | Scheduled | Not attempted in cycles 1-2. |
| Regression-guarded per-stem RMS pins | Scheduled | Not attempted in cycles 1-2. |
| `promise_check` fully clean under M-SEP-1 | Scheduled | Shadow-ledger fanout WARNs remain expected until the fork conductor adopts clone events. |

The three primary sub-milestones (`ground-truth`, `htdemucs-baseline`, `alternative`) all reach a passing first-cut state within these two cycles.

## 13. Downstream unblock notice

Downstream milestones may consume the adopted separator (htdemucs, demucs 4.1.0) and the per-stem outputs it produces. The preprocessing rule (mono/22050 → stereo/44100 before separation) is fixed and must be honoured by any caller that feeds native seed audio in. The transcription milestone (M-TRANS-1) inherits `htdemucs` as its stem provider and can proceed once its own dependency posture is resolved.

## 14. Carry-forward for later cycles

The scope opened in cycles 1-2 is discharged as a first-cut. The remaining tightening — none of which is a defect against the branch objective — is:

- UMXHQ sample-byte determinism under a hard-pinned single-threaded BLAS contract, with the mechanism (single-thread → serial reduction ordering → mathematically pinned output) either ruled in or ruled out by direct sample-array equality.
- Per-stem RMS values pinned in an integration-test regression guard at a documented tolerance so silent environment drift is caught.
- Adoption of the clone's shadow-ledger events into the workspace-level ledger by the fork conductor at merge, which will clear the expected M-SEP-1 "no ledger events yet" warnings and any orphan-artifact warnings on `scripts/separation/` files.
- A MUSDB18 spot-check as an out-of-domain second data point, at the maintainer's discretion.
- A future milestone for per-instrument decomposition inside the "other" stem (deliberately not opened here).

## 15. Conclusions

Two cycles suffice to reach an adopt verdict for htdemucs backed by numerical evidence rather than by prior belief. The load-bearing constructions delivered are: a deterministic 3-stem ground-truth pipeline whose bytes are reproducible from committed MIDIs and a pinned SoundFont; two separator runners driven from the same interface; a shared SI-SDR scorer that produces a single TSV with a naive-copy row in every cell; a per-stem winner table with a majority-wins tally; a preprocessing rule fixed as a downstream contract; and a blind-spot note per separator plus an explicit deferral of per-instrument work inside "other". The htdemucs determinism check (max-abs diff 0.000e+00 on the 30 s mix drums stem) is the first reproducibility rung; further rungs are scheduled and openly named as scheduled rather than claimed.

## Appendix: Implementation Details

**Scripts (`scripts/separation/`).** `synth_gt.py` (ground-truth mix construction), `run_htdemucs.py` (baseline separator runner), `run_alternative.py` (open-unmix UMXHQ runner), `eval_sisdr.py` (mir_eval `bss_eval_sources` scorer producing `results.tsv` and the bar chart). One later-cycle addition, `verify_umxhq_determinism.py`, is out of scope for this report (it belongs to the cycle that promotes UMXHQ from fixed-seed contract to byte-verified). A superseded `stale/_determinism_check.py` remains on disk under `scripts/separation/stale/` for provenance.

**Data (`data/separation/`).** `synth_mix/manifest.json` records SoundFont SHA-256, per-MIDI SHA-256s, and per-stem/mix WAV SHA-256s for all three durations. `synth_mix/midi/{drums,bass,piano}.mid` are the committed inputs. `synth_mix/gt/synth_{030s,060s,090s}/{drums,bass,piano,vocals}.wav` are the ground-truth stems (vocals stem is zero-signal by construction). `runs/htdemucs/` and `runs/openunmix/` hold per-run outputs. `results.tsv` (36 rows) and `results_bar_chart.png` are the survey outputs.

**Environment.** Interpreter `/usr/bin/python3`. Key pins: numpy 1.26.4, torch 2.13.0+cpu, torchaudio 2.11.0+cpu, demucs 4.1.0, openunmix 1.3.0, mir_eval 0.8.2, soundfile 0.14.0, librosa 0.11.0, fluidsynth `/usr/bin/fluidsynth`, SoundFont `/usr/share/sounds/sf2/FluidR3_GM.sf2` (SHA-256 above).

**Rerun recipe** (from workspace root, in order):

```
/usr/bin/python3 scripts/separation/synth_gt.py
/usr/bin/python3 scripts/separation/run_htdemucs.py
/usr/bin/python3 scripts/separation/run_alternative.py
/usr/bin/python3 scripts/separation/eval_sisdr.py
```

**Sub-milestones opened.** `M-SEP-1/ground-truth`, `M-SEP-1/htdemucs-baseline`, `M-SEP-1/alternative`. All three reach a first-cut passing state within cycles 1-2. `M-SEP-1/venv-quarantine` is deliberately not registered because open-unmix installs cleanly against the top-level environment; the trigger is preserved for any later cycle that adds a separator whose pins conflict.

**Session traceability (fork 22b8c654f616, clone 0).**

- Cycle 1 — researcher `3e736039-a982-4aeb-8f95-8f0257072d24`; worker `9fbf67cd-d02a-4606-8812-11c575f091fb`; auditor `cb2a436f-5bb7-4452-b1dd-95c142203586`.
- Cycle 2 — researcher `6eb60eca-b29d-4482-a84a-3786682d5755`; worker `24bfdfb0-e4d8-42b4-b7b6-5d118438497c`; auditor `e9bd5a3a-c297-44a8-8152-063465dae3f6`.

**Cross-reference map.** `scripts/separation/synth_gt.py` produces the ground-truth mixes that both `run_htdemucs.py` and `run_alternative.py` consume; both runners write per-stem WAVs that `eval_sisdr.py` scores against the ground-truth stems using `mir_eval.separation.bss_eval_sources`, producing `data/separation/results.tsv` and the bar chart. Downstream, M-TRANS-1 will consume the adopted separator (htdemucs) but nothing in this branch depends on M-TRANS-1 or vice versa.
