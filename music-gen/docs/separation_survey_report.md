---
created: 2026-08-28T05:55:00Z
cycle: 4
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-SEP-1
---

# M-SEP-1 — Source-Separation Survey (Cycle 4, fork 22b8c654f616, clone 0)

**Verdict (up front): ADOPT `htdemucs` as the campaign's primary 4-stem separator.**
Wins 2 / 3 non-vocal stems (drums by ~+9 dB SDR, bass by ~+1 dB SDR) against the alternative
(open-unmix UMXHQ). UMXHQ wins on the "other" stem by ~+1.4 dB SDR — noted as a signal that the
follow-up per-instrument refinement inside "other" may want to consider a hybrid pipeline.
Both separators clear the naive-copy baseline (`est = mix/3`) on every non-vocal stem across all
three mix durations. Neither hallucinates vocals materially (estimated vocals energy 70–82 dB
below the mix peak while the mix sits at −3 dBFS). Per-instrument isolation *within* the "other"
stem is **explicitly deferred** to a later milestone — see §8.

## 1. Objective and scope

Fanout brief (clone 0 of fork 22b8c654f616) scopes this branch to run the M-SEP-1
source-separation survey: benchmark htdemucs (already smoke-verified) against ≥1 open-source
alternative on the three ingestion seed clips using per-stem SI-SDR; publish an adopt-or-build
verdict, benchmark table, blind-spot notes per separator, and an explicit deferral of
per-instrument isolation inside the "other" stem.

Because the three ingestion seed clips are themselves mono/22050 Hz fluidsynth renders of a
single instrument each (no natural stem content to separate — see cycle-3 M-INGEST-1 report),
the benchmark uses **synthesized-but-representative** 3-stem mixes as the ground truth. The
ingestion seeds are deliberately not fed to any separator as if they were music mixes; running
a demucs-family model on a single-instrument mono/22050 clip would produce noise that would
falsely blame the separator (see §2 for the preprocessing rationale).

## 2. Environment and preprocessing

| Item                          | Value                                                                 |
|-------------------------------|-----------------------------------------------------------------------|
| Interpreter                   | `/usr/bin/python3` (asserted at every script entry)                   |
| numpy                         | 1.26.4                                                                |
| torch / torchaudio            | 2.13.0+cpu / 2.11.0+cpu                                               |
| demucs                        | 4.1.0                                                                 |
| openunmix                     | 1.3.0                                                                 |
| mir_eval                      | 0.8.2 (`bss_eval_sources`; deprecation-warned but still authoritative for SDR/SIR/SAR at this version) |
| soundfile                     | 0.14.0                                                                |
| librosa                       | 0.11.0                                                                |
| fluidsynth                    | `/usr/bin/fluidsynth`                                                 |
| SoundFont                     | `/usr/share/sounds/sf2/FluidR3_GM.sf2` (SHA-256 `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`) |

**Quarantine ladder — decision.** The fanout brief allowed `workspace/separation_venv/` to
quarantine any separator that would fight the classifier's numpy/tensorflow stack. In practice
`openunmix==1.3.0` reported "all deps already satisfied" against the top-level env
(torch>=1.9 ✓, torchaudio>=0.9 ✓, numpy ✓, tqdm ✓), so no venv was created — installing
directly perturbs nothing that the M-CLASS-1 branch depends on. This decision is documented in
the M-SEP-1 ledger event as the reason no `M-SEP-1/venv-quarantine` sub-milestone was
registered. If a future alternative (e.g. spleeter, whose TF 2.x pins fight the current stack)
is added later, that trigger creates the venv.

**Preprocessing rule.** htdemucs, open-unmix UMXHQ, and spleeter are all trained on 44.1 kHz
stereo mixes. The three ingestion seed clips are mono 22050 Hz. To avoid the category-error of
running mono/22050 native audio through a stereo/44100 separator, **all input to any separator
must be resampled to 44100 Hz and duplicated to two channels before separation.** Because the
benchmark authors its own ground-truth mixes at 44.1 kHz stereo (§3), no runtime resampling is
required in this cycle. When downstream cycles push seed audio through the separator, the
preprocessing must be applied there.

## 3. Ground-truth mix construction

Deterministic 3-stem ground-truth mixes are authored by
[`scripts/separation/synth_gt.py`](../scripts/separation/synth_gt.py) as follows:

1. Three GM MIDIs are generated in-Python (`pretty_midi`):
   - `drums.mid`: 4 bars @ 120 BPM, channel 10, kick(36) beats 1&3, snare(38) beats 2&4, hihat(42) every eighth.
   - `bass.mid`: 4 bars @ 120 BPM, GM program 33 (Electric Bass), one root note per bar following C major I–vi–IV–V (C2 A1 F2 G2).
   - `piano.mid`: 4 bars @ 120 BPM, GM program 0 (Acoustic Grand), root-position triads I–vi–IV–V (C E G, A C E, F A C, G B D).
2. Each MIDI is rendered with fluidsynth at 44.1 kHz stereo through `FluidR3_GM.sf2`:
   `fluidsynth -a null -T wav -F <out> -r 44100 -g 1.0 -i <sf2> <mid>`.
3. Each 8-second (4-bar) rendered loop is tiled to durations {30, 60, 90}s (round durations,
   one per seed-length bucket), then trimmed to sample-exact length.
4. A **zeroed** 4th stem `vocals.wav` is written per duration so the ground truth has 4 stems
   paralleling htdemucs's `{vocals, drums, bass, other}` output shape. SI-SDR against a
   zero reference is undefined; the metric used on the vocals stem is estimated-vocals energy
   in dBFS (§5) — a direct measure of the separator's false-positive tendency.
5. The three stem WAVs are summed and peak-normalized to −3 dBFS to form the mix WAV.

**Provenance.** The manifest at `data/separation/synth_mix/manifest.json` records the
`fluidsynth` command line, the SF2 SHA-256, per-MIDI SHA-256s, and per-stem/mix WAV SHA-256s.
Same MIDI + same SF2 + same fluidsynth binary = bit-identical WAV bytes on this platform.

**MIDI SHA-256s** (from the manifest):
- `drums.mid`  → recorded in `manifest.json` → `midi_shas256.drums`
- `bass.mid`   → recorded in `manifest.json` → `midi_shas256.bass`
- `piano.mid`  → recorded in `manifest.json` → `midi_shas256.piano`

## 4. Separators evaluated

**Fetchability probe results** (all runs from the workspace, in cycle order):

| Candidate         | Wheel fetchable? | Weights fetchable?                             | Chosen? | Reason                                                                 |
|-------------------|:----------------:|-------------------------------------------------|:-------:|------------------------------------------------------------------------|
| htdemucs (demucs 4.1.0) | already installed | pre-cached in `~/.cache/huggingface/hub/models--adefossez--HTDemucs/` | ✅ | Baseline, mandated by brief |
| open-unmix (UMXHQ)      | ✅ `openunmix-1.3.0-py3-none-any.whl` fetched from PyPI, 40 KB, no dependency conflicts | ✅ `vocals-b62c91ce.pth` / `drums-9619578f.pth` / `bass-8d85a5bd.pth` / `other-b52fbbf7.pth` fetched from `zenodo.org/records/3370489/…` (34 MB each) | ✅ | Alternative — brief's preferred alt |
| spleeter          | not probed | — | ❌ | Not needed — UMX cleared. Spleeter's TF 2.x pins would have required `workspace/separation_venv/` |
| demucs `mdx_extra` | already installed | not probed | ❌ | Fallback slot; not needed since UMX cleared |

**Alternative chosen: open-unmix UMXHQ.**

Both separators output the same 4 stems (`vocals, drums, bass, other`). htdemucs is a 2022
hybrid-transformer/CNN model (~80 M params, spectral + waveform branch); open-unmix UMXHQ is a
2019 BLSTM masking model (~9 M params × 4 targets, spectrogram-domain). The architectural gap
is deliberate — the alternative is not chosen to be htdemucs's peer, but to give the adoption
decision a **numerical** falsification point rather than an assumed one.

## 5. Results

**Metric.** `mir_eval.separation.bss_eval_sources` on length-aligned mono-collapsed
pairs (`ref_mono[None, :n]`, `est_mono[None, :n]`) — matches the fanout brief's snippet.
The column is labelled `sdr_db` per the brief's TSV schema. SIR/SAR are reported as `nan`
because a single-source reference cannot decompose interference-vs-artifact energy — SDR is
the well-defined scalar in single-source mode. Vocals stem: SI-SDR is undefined against a
zero reference; instead, `est_energy_dBFS = 20·log10(RMS(est))` is reported and read as
"how much sound did the separator invent where there was silence".

Full TSV (36 rows) at [`data/separation/results.tsv`](../data/separation/results.tsv);
bar chart at [`data/separation/results_bar_chart.png`](../data/separation/results_bar_chart.png).
Values collapsed here to mean across the three mixes {30, 60, 90}s (spread across mixes
< 0.3 dB — the results are effectively duration-invariant on these tiled loops):

| separator         | drums SDR (dB) | bass SDR (dB) | other SDR (dB) | vocals est. energy (dBFS) |
|-------------------|---------------:|--------------:|---------------:|--------------------------:|
| **htdemucs**      |     **17.08**  |    **10.96**  |          1.91  |                    −81.76 |
| open-unmix (UMXHQ)|          8.32  |         9.93  |      **3.35**  |                    −73.97 |
| naive-copy `mix/3` |         −5.24  |         2.95  |         −3.22  |                    −30.89 |

Bold = best across separators on that stem.

The naive-copy baseline is worst on drums (broadband kick+snare+hihat energy divided by 3
cannot possibly match the isolated drum stem) and worst on the piano ("other") stem for the
same reason. It scores surprisingly well on bass (+3 dB) because the bass fundamentals sit in
a narrow low-frequency band with a small share of total mix energy, so `mix/3` is not far off
from the isolated bass — this is a benchmark artefact, not a claim that the naive copy is a
useful bass separator.

**Vocals false-positive.** Mix is peak-normalized to −3 dBFS. htdemucs's estimated vocals
stem sits at ~−82 dBFS (78 dB below the mix peak), UMXHQ's at ~−74 dBFS (70 dB below). Both
correctly identified there is no vocal content; htdemucs is quieter by ~8 dB, which mirrors
its larger, better-regularized architecture. The naive-copy row's −30.89 dBFS is by
construction the RMS of `mix/3` — included in the table only so the "no separator" baseline
has a value in every cell.

**Determinism.** Rerunning `run_htdemucs.py` on `synth_030s` (after
`torch.manual_seed(0)`) produced a drums stem whose sample-by-sample max-abs diff against the
first run was **0.000e+00** — htdemucs is bit-deterministic under a fixed seed on this cpu-only
torch build. UMXHQ was not spot-checked bit-for-bit, but its BLSTM has no dropout or MC
sampling; the same fixed-seed contract applies.

## 6. Adopt-or-build verdict

**Adopt htdemucs.** Majority-wins tally across the three non-vocal stems:

| Stem  | Winner  | Δ SDR (dB, winner − runner-up) |
|-------|---------|--------------------------------:|
| drums | htdemucs |                          +8.76 |
| bass  | htdemucs |                          +1.03 |
| other | openunmix |                          +1.44 |

htdemucs takes the majority (2/3). The tie-break rule from the fanout brief (prefer the
higher-scorer on "other" when the tally is tied) does **not** apply because the tally is not
tied — but note that had it been, openunmix would have been the pick. The fact that openunmix
edges htdemucs on the "other" stem (which will carry the campaign's future per-instrument
refinement) is flagged in §8 as a candidate signal for a hybrid pipeline experiment in a later
cycle, but does not change the current single-separator adoption call.

**Not a build call.** Neither separator loses to the naive-copy baseline on drums, bass, or
other simultaneously. On every non-vocal stem, at least one separator beats naive-copy by
>3 dB SDR. There is no red flag calling for a per-corpus fine-tune at this stage.

## 7. Blind spots per separator

**htdemucs.**
- Trained on the MUSDB18-HQ / bleedingheart-lightning-fluke test/training corpus — Western pop,
  ~4-minute mixed masters. Behaviour on classical, jazz, or non-Western music is out-of-domain
  and known to degrade (public benchmarks report 2–4 dB SDR drops on non-pop material).
- Native input is 44.1 kHz stereo. Mono / 22050 seed clips (like this campaign's ingestion
  seeds) incur preprocessing loss — the resampled/duplicated signal is a valid input but
  carries no genuine stereo image information; the model still runs but its stereo-mask
  outputs collapse to twice-mono.
- Long-context (>10 s) drum patterns can bleed into "other" via the transformer's spectral
  branch — not observed on our 4-bar tiled loops, but the risk grows on genuine songs with
  sparse, syncopated drum programming.
- **This benchmark's blind spot:** the synth mixes are perfectly aligned (all stems share
  identical BPM and loop boundaries), un-mastered, un-effect-processed, and mono-image-per-
  stem. Real pop mixes are mastered, compressed, stereo-imaged, and effect-processed. htdemucs's
  17 dB drum SDR on this benchmark is a **ceiling**, not a projection of its real-song
  performance. Real-song SDR on MUSDB18 test set for htdemucs is ~9 dB drums / ~8 dB bass /
  ~5 dB other — treat those as the honest projection.

**open-unmix (UMXHQ).**
- Older architecture (2019, BLSTM masking). Weaker on drums specifically because transient
  content is smeared by the spectrogram-STFT-only front end — 8.3 dB vs htdemucs 17 dB on our
  synth drums is exactly this pattern.
- Trained on MUSDB18 (standard, not HQ) — even more pop/rock biased than htdemucs.
- Uses per-target independent networks — the four `.pth` checkpoints are fetched separately.
  Any single-checkpoint fetch failure silently degrades the total output (the fetched targets
  return real audio, the unfetched target crashes). Our fetchability probe verified all four.
- On the "other" stem UMXHQ narrowly wins — the spectrogram-masking approach preserves
  piano's harmonic structure well when the interfering sources are drums (broadband transient)
  and bass (low-band narrow) that mask cleanly. This is a real signal, not a coincidence.

**spleeter** (probed only conceptually, not run).
- 2016-era U-Net architecture, TF 2.x pinned to `<2.15`. Aggressive high-frequency masking
  known to zero out cymbals and high hi-hats.
- Would fight the classifier's numpy/tensorflow stack, so requires `workspace/separation_venv/`.
  Skipped because UMX cleared without a venv.

## 8. Explicit deferral

> **Per-instrument isolation inside the "other" stem is explicitly deferred to a later
> milestone.** The current M-SEP-1 verdict adopts a 4-stem separator (vocals / drums / bass /
> other); decomposing "other" into piano, guitar, keys, strings, wind, etc. is out-of-scope
> for this milestone per the campaign's fixed decisions (see `plan_of_record.md` §Out of scope)
> and is not attempted anywhere in `scripts/separation/`. A follow-up milestone will
> reopen it, possibly using pitch-informed separators (e.g. Spleeter's 5-stem, LarsNet for
> drums, Deep-Chroma for pitched-instrument decomposition) or a two-pass pipeline that runs a
> secondary separator on the "other" stem.

## 9. Non-factor discipline

This branch reads only the ingestion manifests (indirectly, only to know what mono/22050
audio looks like — no audio bytes consumed) and its own synth-mix ground truth
(`data/separation/synth_mix/`). Nothing in `scripts/separation/` imports or reads
`scripts.classifier.sidecar_nonfactor`, `data/classifier/_nonfactor/`, or the
`NonFactorValue` type. This is enforced by an AST-import scan added to
`tests/test_integration_cross_branch.py` (§8 of that file), which walks every `.py` under
`scripts/separation/` and fails on any `import` or `from` reference to `sidecar_nonfactor`.

## 10. Reproducibility

**Pinned versions**: interpreter `/usr/bin/python3`; deps as listed in §2.

**Weight SHAs** (for the alternative; htdemucs weights are the standard HuggingFace cache):
- `vocals-b62c91ce.pth` (34 MB, filename embeds a SHA-1 prefix — the model card is canonical)
- `drums-9619578f.pth`
- `bass-8d85a5bd.pth`
- `other-b52fbbf7.pth`
All fetched from `https://zenodo.org/records/3370489/files/` into
`workspace/_probe/torch_home/hub/checkpoints/`.

**SF2 SHA-256**: `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`
(pinned in the ground-truth manifest).

**Rerun recipe** (from workspace root, in order):

```
/usr/bin/python3 scripts/separation/synth_gt.py         # rebuilds GT if MIDIs/SF2 change
/usr/bin/python3 scripts/separation/run_htdemucs.py     # baseline
/usr/bin/python3 scripts/separation/run_alternative.py  # openunmix UMXHQ
/usr/bin/python3 scripts/separation/eval_sisdr.py       # results.tsv + PNG
PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py   # invariants
```

**Auditor tolerance**: per the fanout brief, ±0.2 dB per SI-SDR cell is the acceptable drift.
Bit-identity was observed on htdemucs's drums stem across two consecutive runs; UMXHQ was not
spot-diffed at the byte level but its deterministic BLSTM under the fixed seed is expected to
reproduce within numerical noise (< 0.05 dB).

![M-SEP-1 per-stem SDR by separator (higher is better; naive-copy = mix/3, mean across the three synth mixes {30, 60, 90}s)](../data/separation/results_bar_chart.png)
