---
title: "Music/Non-Music Classifier Baseline (M-CLASS-1) — cycles 1-1 [clone 2]"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music/Non-Music Classifier Baseline (M-CLASS-1) — cycles 1-1 [clone 2]

## Abstract

A five-class audio-content classifier — `SPEECH / APPLAUSE / AMBIENT / MUSIC_LIVE / MUSIC_RECORDED` — was stood up as a thin taxonomy mapper over PANNs `Cnn14` (AudioSet-pretrained, mAP 0.431). On a purpose-built 55-clip labeled validation subset drawn from ESC-50, LibriSpeech-dummy, and fluidsynth-rendered MIDI, the mapped classifier reaches **1.000 binary music-vs-not-music accuracy** and **0.873 five-class accuracy**, both clearing the sufficiency thresholds set in the research plan (0.85 binary, ≥50 clips with published confusion matrix). Alongside the classifier, a non-factor sidecar subsystem was built to record but architecturally isolate curatorial fields (genre, country, artist, era, language, live-vs-recorded, instrumental-vs-lyrical) so downstream feature code cannot consume them by accident. Isolation is enforced by four independent layers — a segregated path prefix, a namespace with no ordinary reader, a `NonFactorValue` type whose common operations (`str`, `+`, `==`, `hash`, `bool`, `json.dumps`) all raise, and a static-analysis test that also self-tests by planting and catching synthetic violations. All artifacts are reproducible from pinned seeds and pinned weight hashes; independent replay of one held-out clip reproduces class posteriors bit-for-bit.

---

## 1. Objective and Scope

Two interlocked deliverables were in scope for this branch:

1. A pretrained AudioSet-scale audio tagger, mapped onto the campaign's fixed 5-class taxonomy, evaluated on ≥50 labeled clips with a published confusion matrix and binary music-vs-not-music accuracy ≥ 0.85.
2. A non-factor sidecar writer whose architecture — path prefix, module namespace, deliberately awkward reader API, and static-analysis test — makes accidental consumption of curatorial attributes structurally difficult in future code.

The branch was deliberately decoupled from the rated-corpus ingestion work: the classifier requires per-clip taxonomy labels (which the rated playlists do not carry), and rated audio downloads remain blocked by the workspace's egress policy on `googlevideo.com`. Ingestion is a sibling branch (M-INGEST-1).

## 2. Model Choice and Interpreter Discipline

The research plan supplied a five-rung fallback ladder for the tagger. Rung A survived on the first attempt: `panns_inference` fetched `Cnn14_mAP=0.431.pth` (327 MB) from the Zenodo/GCS mirror through the workspace's egress gateway, along with the AudioSet class-index CSV. Rungs B (HuggingFace-mirrored PANNs weights), C/D (YAMNet), and E (MFCC + logistic regression fallback) were not needed but were kept documented as recovery paths.

- **Model**: `panns-cnn14-mAP=0.431`, 32 kHz mono waveform input, 527-dimensional AudioSet posteriors output.
- **Weights SHA-256**: `0dc499e40e9761ef5ea061ffc77697697f277f6a960894903df3ada000e34b31`.
- **Interpreter**: `/usr/bin/python3` (system Python; the harness venv lacks torch/librosa/TF). Every entry point script imports `scripts/classifier/_interp.py`, which raises `SystemExit` with a corrective re-invocation string when `sys.executable` is wrong.

## 3. Taxonomy Mapping

The 527 AudioSet leaves are reduced onto the 5-class taxonomy by a YAML file (`scripts/classifier/taxonomy_map.yaml`) read by the mapper at construction time — there is no code fork of the mapping. Direct-map buckets cover SPEECH (Speech and its speaker/style children), APPLAUSE (Applause / Clapping / Cheering), AMBIENT (Wind, Rain, Ocean, Waves, Thunderstorm, Cricket, Water, Silence, Rustling leaves, Waterfall, Steam, Stream), and MUSIC (the umbrella Music leaf plus instrument, vocal, and genre children).

AudioSet-527 has no native `Live music` leaf. MUSIC_LIVE is therefore a **composite heuristic**:

```
verdict = MUSIC_LIVE  iff  MUSIC_mass ≥ 0.20
                       AND (APPLAUSE_mass ≥ 0.15 OR LIVE_LEAF_mass ≥ 0.30)
verdict = MUSIC_RECORDED  iff  music-mass condition holds AND no live cue
```

where `LIVE_LEAF_mass` sums the AudioSet leaves `Crowd`, `Hands`, and `Chatter`.

An ambiguity flag `low_confidence = (0.05 ≤ MUSIC_mass ≤ 0.20)` is recorded per clip for audit but does not override the argmax verdict. Distribution: APPLAUSE clips flag most often (7/10), which reflects the known spectral overlap between clapping and low-frequency percussion tags.

## 4. Validation Set

Fifty-five clips, 30.0 s mono at 32 kHz PCM_16, all public-domain or CC-licensed, with per-clip SHA-256 and license/origin URLs captured in `data/classifier/valset/valset_manifest.tsv`:

| Class | Count | Source |
|---|---:|---|
| APPLAUSE       | 10 | ESC-50 `clapping` (CC BY-NC 3.0) |
| AMBIENT        | 15 | ESC-50 `rain`, `wind`, `sea_waves` (5 each) |
| SPEECH         | 10 | `hf-internal-testing/librispeech_asr_dummy` (CC BY 4.0) |
| MUSIC_RECORDED | 10 | fluidsynth-rendered MIDI over `FluidR3_GM.sf2`, 10 GM programs, RNG seed `20260828` |
| MUSIC_LIVE     | 10 | **proxy**: `mix = 0.6·music[i] + 1.0·applause[i%10]`, RMS-matched then peak-limited |

The MUSIC_LIVE row is a proxy label: real live audio has applause well below the music line during performance, but the tagger's applause head must fire for the composite rule to trip, so applause was deliberately inflated. The MUSIC_LIVE recall reported below is therefore an optimistic upper bound on "detectable live audio", not a fair estimate of "typical live recording" — see §7.

Two build-time subtleties are worth naming: (i) `github.com/*/archive/*.zip` was blocked (403) through the workspace proxy, but `raw.githubusercontent.com/*` and `huggingface.co/datasets/*/resolve/main/*` were reachable, so all fetches route through those two hosts; (ii) ESC-50 clips are only 5 s, and zero-padding them to 30 s flooded PANNs' `Silence` head — end-to-end **tiling** was substituted and does not disturb the tag distribution the way silence does. Tiling is a validation-set convenience only; the ingestion chassis will chunk to a natural 30 s and must not tile.

## 5. Results

Confusion matrix (rows = true, cols = predicted; `data/classifier/confusion_matrix.tsv`):

|                | SPEECH | APPLAUSE | AMBIENT | MUSIC_LIVE | MUSIC_RECORDED | row total |
|----------------|-------:|---------:|--------:|-----------:|---------------:|----------:|
| SPEECH         | **10** | 0 | 0 | 0 | 0 | 10 |
| APPLAUSE       | 2 | **8** | 0 | 0 | 0 | 10 |
| AMBIENT        | 2 | 0 | **13** | 0 | 0 | 15 |
| MUSIC_LIVE     | 0 | 0 | 0 | **7** | 3 | 10 |
| MUSIC_RECORDED | 0 | 0 | 0 | 0 | **10** | 10 |
| col total      | 14 | 8 | 13 | 7 | 13 | 55 |

Headline numbers:

- **Binary music-vs-not-music accuracy: 1.000** (20 music vs 35 non-music; zero crossings between the two macro-classes).
- **Five-class accuracy: 0.873** (48 / 55).

Per-class metrics:

| class | support | precision | recall | F1 |
|---|---:|---:|---:|---:|
| SPEECH         | 10 | 0.714 | 1.000 | 0.833 |
| APPLAUSE       | 10 | 1.000 | 0.800 | 0.889 |
| AMBIENT        | 15 | 1.000 | 0.867 | 0.929 |
| MUSIC_LIVE     | 10 | 1.000 | 0.700 | 0.824 |
| MUSIC_RECORDED | 10 | 0.769 | 1.000 | 0.870 |

All seven errors stay inside the music-vs-non-music partition:

- 2 × APPLAUSE → SPEECH: ESC-50 clips with incidental crowd chatter alongside the clap; PANNs' Speech head fired ≥ 0.72.
- 2 × AMBIENT → SPEECH: rain/wind with intermittent voice-like formants.
- 3 × MUSIC_LIVE → MUSIC_RECORDED: the RMS-mixed applause was insufficient to trip the composite rule on those three; music was correctly detected.

## 6. Non-Factor Sidecar Architecture

The load-bearing contract of this branch is not the classifier itself but the guarantee that curatorial labels can be recorded without contaminating downstream features. The sidecar module (`scripts/classifier/sidecar_nonfactor.py`) and writer (`scripts/classifier/write_sidecars.py`) produce one JSON per clip under `data/classifier/_nonfactor/` (55 files this cycle). The reader has an intentionally uncomfortable signature:

```python
def read_for_audit_only(
    clip_id: str,
    *,
    i_understand_this_is_non_factor: bool,   # keyword-only, must be True
    root: Path = NONFACTOR_ROOT,
) -> AuditRecord: ...
```

Four independent isolation layers back the contract:

1. **Path prefix.** All sidecars live under `data/classifier/_nonfactor/`; `STRUCTURE.md` documents the prefix as off-limits to any module except the sidecar writer/reader.
2. **Namespace.** No `read_features`, `load`, `get_sidecar`, or similarly innocuous reader exists — only `read_for_audit_only`, whose name is grep-catchable and whose call site must spell out `i_understand_this_is_non_factor=True`.
3. **Type wrapping.** Every string field is wrapped in `NonFactorValue`, whose `__str__`, `__add__`, `__eq__`, `__hash__`, `__bool__` all raise `TypeError`; `json.dumps` on the value fails; `.audit_unwrap()` is the sole escape hatch (grep-catchable).
4. **Static-analysis test.** `tests/test_sidecar_isolation.py` scans every `.py` under `scripts/` (excluding the two allowlisted files) for imports of `sidecar_nonfactor`, references to `NonFactorValue`/`AuditRecord`/`audit_unwrap`/`read_for_audit_only`, and the substring `_nonfactor/`. Under `--self-test`, it plants a synthetic violator in a temp directory and confirms the scanner catches all five violation categories.

Each sidecar written this cycle carries `genre`, `country`, `date_released`, `language`, `instrumental_vs_lyrics`, `live_vs_recorded`, `artist` as `null` (the curatorial values are not yet known — they arrive with the rated audio), plus the three non-music-class posteriors, plus provenance (`model_id`, `weights_sha256`, `sidecar_schema_version: 1`, and the mandatory `__non_factor_do_not_consume__: true` marker). The point of this cycle is the architectural contract, not the completeness of the values: when labels arrive, none of the reader, writer, or isolation-test signatures change.

## 7. Known Failure Modes and Deferred Work

**MUSIC_LIVE evaluation is proxy-limited.** The 0.70 recall is optimistic for detectable live audio and not representative of typical live recording. The next cycle should substitute real short-form live clips — a CC-BY live-audio sampler, or Free Music Archive's `Live_Recordings` tag if reachable through the proxy.

**Two APPLAUSE and two AMBIENT clips misclassified as SPEECH.** Options include (a) requiring a specific speaker-class contribution (Male/Female/Child) instead of the umbrella `Speech`, and (b) biasing the composite rule toward SILENCE/APPLAUSE when the top-1 AudioSet leaf is one of them. Not urgent — both binary and 5-class accuracy exceed sufficiency.

**Taxonomy YAML v1 shipped with wrong AudioSet identifiers.** Applause was `/m/028v0c` (actually Silence), Silence was `/m/028ght` (actually Applause), Clapping was wrong, and a `Live music` leaf was assumed to exist but does not. The mislabelled mapping produced an internally consistent but wrong first evaluation showing 0/10 MUSIC_LIVE recall before it was caught. V2 was rebuilt against `/root/panns_data/class_labels_indices.csv` (the CSV that ships with the tagger) and every ID was reverified. **Recommendation for the next cycle**: a startup-time assertion that every AudioSet identifier in the YAML resolves in the CSV with matching display name. Assume-then-verify was expensive here; the assertion closes the door on this class of error.

**Zero-padding short clips floods the Silence head.** Fixed for the validation set by tiling; the ingestion chassis must not tile real audio.

**Fine-tuning deferred.** Binary music-vs-not-music at 1.000 on the labeled set clears the sufficiency bar; a fine-tune only pays for itself once the rated corpus (real music-side data) is available.

**Environment side effect worth naming for the merge.** Installing `panns_inference` upgraded `numpy` to 2.4.6 and `tensorflow` to 2.21.0, which breaks `basic-pitch 0.4.0`'s pin of `tensorflow<2.15.1`. This is the transcription branch's (M-TRANS-1) problem, not this branch's, but the reconciliation will need to happen — options are pinning PANNs to its torch-only path, quarantining `basic-pitch` in a separate venv, or replacing `basic-pitch`. Flagged here so it is not lost when the branches merge.

## 8. Reproducibility

- **Interpreter**: `/usr/bin/python3` (enforced by `_interp.py`).
- **Pinned versions**: `panns_inference==0.1.1`, `torch==2.13.0+cpu`, `librosa==0.11.0`, `soundfile==0.14.0`, `numpy==2.4.6`, `matplotlib==3.11.1`, `pyarrow==25.0.1`, `tensorflow==2.21.0`, `tensorflow_hub==0.16.1`, `PyYAML==6.0.1`.
- **Weights SHA-256**: `0dc499e40e9761ef5ea061ffc77697697f277f6a960894903df3ada000e34b31`.
- **Deterministic seeds**: valset build uses `numpy.random.default_rng(20260828)`.
- **Invocation** (all commands idempotent):

```bash
/usr/bin/python3 -m scripts.classifier.build_valset       # build validation set (cached)
/usr/bin/python3 -m scripts.classifier.evaluate           # tag + map + write metrics + PNG
/usr/bin/python3 -m scripts.classifier.write_sidecars     # emit 55 non-factor sidecars
/usr/bin/python3 tests/test_sidecar_isolation.py --self-test   # architecture check + self-test
/usr/bin/python3 -m scripts.classifier.classify_clip \
    data/classifier/valset/clips/MUSIC_RECORDED__fluid_music_00.wav   # spot check
```

An independent re-run of `classify_clip.py` on `AMBIENT__1-28135-B-11.wav` reproduces `class_probs`, `music_mass = 0.03327977657318115`, and the top-5 AudioSet leaves bit-for-bit against the shipped `predictions.jsonl`. All 53 direct-map and 3 composite-input AudioSet identifiers in the taxonomy YAML resolve in `class_labels_indices.csv` with matching display names — the v1 identifier error has been closed off. The isolation self-test catches 5/5 planted violation categories on a synthetic downstream module.

## 9. Sufficiency

The six-item sufficiency checklist set in the research plan is fully met and independently reverified: the tagger runs unattended on 30 s WAV via the system Python; the mapping produces at least one true positive in every taxonomy row; the validation set has 55 labeled clips with a published confusion matrix; binary music-vs-not-music accuracy is 1.000 (well above the 0.85 threshold and also above the 0.90 plan-of-record target); the 55 non-factor sidecars exist under `data/classifier/_nonfactor/` with valid schema and populated provenance; and the isolation test passes on the real tree and catches synthetic plants.

---

## Appendix: Implementation Details

**Code organization** (`scripts/classifier/`, 10 files):

- `_interp.py` — interpreter guard (raises `SystemExit` with re-invocation string).
- `tagger.py` — thin wrapper around `panns_inference.AudioTagging`.
- `taxonomy.py` — YAML-driven 527→5 mapper, composite MUSIC_LIVE rule, low-confidence flag.
- `taxonomy_map.yaml` — v2 mapping, every AudioSet identifier resolvable in the shipped CSV.
- `classify_clip.py` — CLI entry point for one clip; emits class_probs, music_mass, top-5 AudioSet leaves.
- `evaluate.py` — batch eval over valset; writes confusion matrix (TSV + PNG), per-class metrics, binary metrics, predictions JSONL.
- `build_valset.py` — deterministic builder; ESC-50 fetch, LibriSpeech-dummy fetch, fluidsynth MIDI render, MUSIC_LIVE proxy mixdown.
- `sidecar_nonfactor.py` — `NonFactorValue`, `AuditRecord`, `read_for_audit_only`.
- `write_sidecars.py` — emits the 55 sidecar JSONs.

**Test**: `tests/test_sidecar_isolation.py` (static scanner + behavioral probe + `--self-test` planting).

**Data outputs** (`data/classifier/`):

- `confusion_matrix.tsv`, `confusion_matrix.png`, `per_class_metrics.tsv`, `binary_music_metrics.tsv`
- `predictions.jsonl` — one JSON row per clip (55 rows), class_probs, top-5 AudioSet leaves, low-confidence flag
- `valset/valset_manifest.tsv` — per-clip SHA-256, license, origin URL, class label
- `valset/build_log.jsonl` — build-time provenance
- `valset/clips/*.wav` — 55 files, 30.0 s mono 32 kHz PCM_16
- `_nonfactor/*.json` — 55 sidecars (off-limits path per `STRUCTURE.md`)

**Documentation update**: `STRUCTURE.md` gained an off-limits declaration for `data/classifier/_nonfactor/`, referencing the isolation test as the enforcement mechanism.

**Session references** (this branch, cycle 1):

- Researcher session: `8a00fc0a-2ed1-45b9-ba90-44e3563d9009`
- Worker session: `7902d349-58f4-4162-966f-cf83da321a8e`
- Auditor session: `639646de-0f82-4d5c-aaff-8ad49536e616`
- Milestone identifier: `M-CLASS-1`; branch identifier: `clone-2` of fork `fae3e8f3c47c`.

**Root-conductor merge actions surfaced by the auditor:**

1. Promote the shadow-ledger `M-CLASS-1` validated event (medium confidence) into the main promise ledger, referencing this report, the confusion matrix, and the isolation test. This will clear the "orphan artifact in managed path" warnings that currently attach to classifier artifacts because the branch's ledger events have not yet merged.
2. Route the `numpy 2.4.6 / tensorflow 2.21.0` upgrade as a manager event to M-TRANS-1 so `basic-pitch 0.4.0`'s incompatible pin (`tensorflow<2.15.1`) is reconciled before that branch's next cycle.
3. The four `promise_check` errors currently attached to `M-INGEST-1` sub-milestone identifiers are from the sibling ingestion clone and are not attributable to this branch; the ingestion clone's auditor should reclassify them under the root `M-INGEST-1` identifier or the plan scratch space.

**Verdict**

The branch met every sufficiency criterion set in the research plan, all load-bearing claims reproduce under independent replay, and the sidecar isolation contract holds under adversarial probing. The scoped objective is exhausted; further refinement (real live-audio clips for MUSIC_LIVE, startup-time identifier assertion, SPEECH-threshold tuning, wiring into the ingestion pipeline) depends on the ingestion branch landing its manifest schema and belongs to a future cycle.

<verdict>validated</verdict>
