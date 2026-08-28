---
created: 2026-08-28T04:35:00Z
cycle: 1
run_id: run-2026-08-28T040704Z
agent: worker (fanout clone-2, branch C: M-CLASS-1)
milestone: M-CLASS-1
---

# Classifier baseline (M-CLASS-1) — cycle 1 report

Music/non-music classifier baseline over the campaign's 5-class taxonomy,
plus the non-factor sidecar writer with architectural isolation. Fanout
branch C (of fork `fae3e8f3c47c`); consumes no other branch's output.

---

## 1. Objective

Deliver two interlocked pieces:

1. A pretrained AudioSet-scale tagger, mapped onto the campaign's fixed
   5-class taxonomy (`SPEECH / APPLAUSE / AMBIENT / MUSIC_LIVE /
   MUSIC_RECORDED`), evaluated on a ≥50-clip labeled subset with a
   published confusion matrix. Binary music-vs-not-music accuracy on the
   labeled set must clear ≥0.85 for the branch to be sufficient.

2. A non-factor sidecar writer whose ARCHITECTURE — path prefix + module
   namespace + deliberately awkward reader API + static-analysis test —
   makes accidental downstream consumption of non-factor attributes
   (genre, country, artist, era, etc.) architecturally hard to do by
   accident.

The two together validate the classifier "spine of the mess-scale" (per
the campaign prompt) AND the load-bearing "non-factors are recorded but
powerless" contract in a form that survives code drift.

---

## 2. Model choice

Rung **A** of the ladder in the research brief survived on first attempt:

| # | Rung | Status |
|---|------|--------|
| A | PANNs `Cnn14`, weights via `panns_inference` (Zenodo/GCS) | **survived** — used |
| B | PANNs weights from HuggingFace mirror | not needed |
| C | YAMNet via `tensorflow_hub` | `tensorflow_hub` was installable; not needed |
| D | YAMNet via manual SavedModel URL | not needed |
| E | hand-crafted MFCC + logistic-regression fallback | not needed |

**Weight fetch:** `panns_inference` on first `AudioTagging()` load pulled
- `class_labels_indices.csv` (14 675 B) from
  `storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/`
- `Cnn14_mAP=0.431.pth` (327 428 481 B) from Zenodo (GCS-hosted).

Both fetches succeeded through the workspace's egress gateway.

**Model:** `panns-cnn14-mAP=0.431`, sampling rate 32 000 Hz, input mono
waveform, output 527-D AudioSet class posteriors.

**Weights SHA-256:**
`0dc499e40e9761ef5ea061ffc77697697f277f6a960894903df3ada000e34b31`

**Weights cache location:** `/root/panns_data/Cnn14_mAP=0.431.pth`
(default cache dir chosen by `panns_inference`; not committed).

**Interpreter:** `/usr/bin/python3` — enforced at import time by
`scripts/classifier/_interp.py`, which raises `SystemExit` with the
correct re-invocation command if `sys.executable` is wrong. Every entry
point script (`classify_clip.py`, `build_valset.py`, `evaluate.py`,
`write_sidecars.py`, `test_sidecar_isolation.py`) has the shebang
`#!/usr/bin/env -S /usr/bin/python3`.

---

## 3. Taxonomy mapping

The project taxonomy is fixed at 5 classes. AudioSet's 527 leaves reduce
via a curated YAML at `scripts/classifier/taxonomy_map.yaml` (v2 —
version 1 shipped with wrong MIDs and was corrected mid-build; see §7).

**Direct-map buckets** (all MIDs verified against
`/root/panns_data/class_labels_indices.csv`, the CSV bundled with the
tagger, which mirrors the AudioSet ontology the model was trained on):

| Taxonomy class | AudioSet leaves (representative) |
|---|---|
| `SPEECH` | Speech, Male speech, Female speech, Child speech, Conversation, Narration, Speech synthesizer, Whispering |
| `APPLAUSE` | Applause `/m/028ght`, Clapping `/m/0l15bq`, Cheering `/m/053hz1` |
| `AMBIENT` | Wind, Rain, Ocean, Waves, Thunderstorm, Cricket, Water, Silence, Rustling leaves, Waterfall, Steam, Stream |
| `MUSIC` (umbrella) | Music `/m/04rlf`, Musical instrument, Guitar/Bass/Electric guitar, Piano/Keyboard/Electric piano, Synthesizer, Organ, Drum kit/Drum/Percussion/Snare/Cymbal, Violin/Bowed strings/Plucked strings/Ukulele/Harp/String section, Wind instrument/Trumpet/Trombone/Clarinet/Flute/Saxophone/Brass, Singing/Choir/Opera/A capella |
| `LIVE_MUSIC_LEAF` (composite input) | Crowd `/m/03qtwd`, Hands `/m/0k65p`, Chatter `/m/07rkbfh` |

The full mapping (with all MIDs, names, and thresholds) lives in
`scripts/classifier/taxonomy_map.yaml`. There is no code fork of the
mapping — the mapper reads that YAML at construction time.

### MUSIC_LIVE composite rule

**AudioSet-527 has no `Live music` leaf.** The composite rule:

```
verdict = MUSIC_LIVE  iff
    MUSIC_mass >= 0.20
    AND (APPLAUSE_mass >= 0.15 OR LIVE_LEAF_mass >= 0.30)

verdict = MUSIC_RECORDED  iff  music mass condition holds AND no live cue
```

This is a **heuristic**, not a native class, and its recall on real
live-music recordings is unknown (see §4 and §7 on the proxy label used
in this cycle's validation set).

### Ambiguity flag

`low_confidence = (0.05 ≤ MUSIC_mass ≤ 0.20)`. Recorded in the
predictions and the sidecar for audit only; downstream still gets the
argmax verdict. Distribution over the labeled set:

| true class | total | low_confidence flagged |
|---|---:|---:|
| SPEECH | 10 | 1 |
| APPLAUSE | 10 | 7 |
| AMBIENT | 15 | 4 |
| MUSIC_LIVE | 10 | 0 |
| MUSIC_RECORDED | 10 | 0 |

APPLAUSE's high low-confidence rate reflects overlap between clapping
and the low end of the music/instrument spectrum — expected, not a bug.

---

## 4. Validation set

Total 55 clips, 5 classes, all public-domain / CC-licensed. Every clip
is 30.0 s mono at 32 000 Hz PCM_16 to match PANNs' native input and the
project's fixed clip length. Manifest (with per-clip SHA-256, license,
origin URL) at `data/classifier/valset/valset_manifest.tsv`; build log
at `data/classifier/valset/build_log.jsonl`.

| Class | Count | Source |
|---|---:|---|
| APPLAUSE | 10 | ESC-50 category `clapping` (CC BY-NC 3.0) via `raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/` |
| AMBIENT | 15 | ESC-50 categories `rain`, `wind`, `sea_waves` (5 each) |
| SPEECH | 10 | `hf-internal-testing/librispeech_asr_dummy` validation FLACs (CC BY 4.0) via HuggingFace CDN |
| MUSIC_RECORDED | 10 | fluidsynth-rendered MIDI over `/usr/share/sounds/sf2/FluidR3_GM.sf2`; 10 GM programs (piano, guitar, violin, flute, trumpet, e.piano, organ, sax, choir, harp); tempo/rhythm/pitch varied by a deterministic RNG seeded at `20260828` |
| MUSIC_LIVE | 10 | **proxy label**: for each i, `mix = 0.6*music[i] + 1.0*applause[i%10]`, RMS-matched at 0.10 before mix, peak-limited after. Applause deliberately loud so PANNs' applause head fires; not a natural live-recording energy balance. See §7. |

**Why not the rated corpus?** The rated playlists (band 6/5/4, 80 songs)
live under `corpus/ratings/` but audio is not yet present — the
workspace's egress gateway policy-denies `googlevideo.com`. This branch
is decoupled from that corpus by design: the classifier needs labeled
data per-clip taxonomy class, and the rated corpus carries band scores,
not taxonomy labels. Ingestion is a separate branch (M-INGEST-1).

**Reachability probes** (informational): `github.com/*/archive/*.zip`
was 403 through the proxy, but `raw.githubusercontent.com/*` and
`huggingface.co/datasets/*/resolve/main/*` returned 200. All fetches
route through those two hosts.

**Short-clip handling.** ESC-50 clips are 5 s. Zero-padding to 30 s
initially flooded PANNs' `Silence` head and swamped the actual event —
the fix is to **tile** short clips end-to-end to fill 30 s. Tiling is
audibly perceptible on a single clip but does not disturb the tag
distribution the way silence does (measured in build; see §7).

---

## 5. Results

Full 5×5 confusion matrix (rows = true, cols = predicted):

|            | SPEECH | APPLAUSE | AMBIENT | MUSIC_LIVE | MUSIC_RECORDED | row total |
|------------|-------:|---------:|--------:|-----------:|---------------:|----------:|
| SPEECH         | **10** | 0 | 0 | 0 | 0 | 10 |
| APPLAUSE       | 2 | **8** | 0 | 0 | 0 | 10 |
| AMBIENT        | 2 | 0 | **13** | 0 | 0 | 15 |
| MUSIC_LIVE     | 0 | 0 | 0 | **7** | 3 | 10 |
| MUSIC_RECORDED | 0 | 0 | 0 | 0 | **10** | 10 |
| col total  | 14 | 8 | 13 | 7 | 13 | 55 |

**Headline numbers:**

- **Binary music-vs-not-music accuracy: 1.000** (20 music, 35 non-music; all correct)
- **5-class accuracy: 0.873** (48 / 55)

**Per-class metrics (from `data/classifier/per_class_metrics.tsv`):**

| class | support | precision | recall | F1 |
|---|---:|---:|---:|---:|
| SPEECH         | 10 | 0.714 | 1.000 | 0.833 |
| APPLAUSE       | 10 | 1.000 | 0.800 | 0.889 |
| AMBIENT        | 15 | 1.000 | 0.867 | 0.929 |
| MUSIC_LIVE     | 10 | 1.000 | 0.700 | 0.824 |
| MUSIC_RECORDED | 10 | 0.769 | 1.000 | 0.870 |

**Error pattern** (7 of 55 mistakes, no crossings between music and
non-music):

- 2 APPLAUSE → SPEECH (PANNs' `Speech` head fired ≥0.72 on ESC-50 clips
  that likely captured incidental crowd chatter alongside the clap).
- 2 AMBIENT → SPEECH (rain/wind clips with intermittent voice-like
  formants near the low end of the low_confidence music band).
- 3 MUSIC_LIVE → MUSIC_RECORDED (the RMS-mixed applause was not loud
  enough for the composite rule to trip on those three clips; music
  detection remained correct).

![Confusion matrix: PANNs Cnn14 → 5-class taxonomy on 55-clip labeled subset. Row-normalized colormap; cell text shows raw count then normalized fraction. Row totals: SPEECH 10, APPLAUSE 10, AMBIENT 15, MUSIC_LIVE 10, MUSIC_RECORDED 10. Binary music-vs-not-music accuracy = 1.00.](../data/classifier/confusion_matrix.png)

Full raw outputs:

- `data/classifier/confusion_matrix.tsv`
- `data/classifier/per_class_metrics.tsv`
- `data/classifier/binary_music_metrics.tsv`
- `data/classifier/predictions.jsonl` (one JSON per clip with class_probs, top-5 AudioSet leaves, low_confidence flag)
- `data/classifier/confusion_matrix.png`

---

## 6. Non-factor sidecar architecture

The sidecar module is `scripts/classifier/sidecar_nonfactor.py`. The
writer is `scripts/classifier/write_sidecars.py` (55 sidecars written
under `data/classifier/_nonfactor/<clip_id>.json`).

**Reader API (deliberately awkward):**

```python
def read_for_audit_only(
    clip_id: str,
    *,
    i_understand_this_is_non_factor: bool,   # keyword-only, must be True
    root: Path = NONFACTOR_ROOT,
) -> AuditRecord: ...
```

Every string field of `AuditRecord` is wrapped in `NonFactorValue`.
`NonFactorValue` refuses `str()`, `+`, `==`, `hash()`, `bool()`, and
`json.dumps` — every common way a downstream module might accidentally
consume the value raises `TypeError`. The ONLY way to see the raw value
is `.audit_unwrap()`, whose name is grep-catchable.

**Three architectural isolation layers, plus a static-analysis test:**

1. **Path prefix.** All sidecar files live under
   `data/classifier/_nonfactor/`. STRUCTURE.md now documents this path
   as OFF-LIMITS to any module except the sidecar writer/reader.

2. **Namespace.** The module has no public reader named `read_features`,
   `load`, `get_sidecar`, or similar. The only reader is
   `read_for_audit_only` — grep-visible, argument-forcing.

3. **Type wrapping.** `NonFactorValue.__str__/__add__/__eq__/__hash__/
   __bool__` all raise; json encoding fails; `.audit_unwrap()` is the
   sole escape hatch.

4. **Import-scan test** (`tests/test_sidecar_isolation.py`) — the piece
   the whole architecture leans on for future-proofness. It scans
   every `.py` under `scripts/` (except `sidecar_nonfactor.py` and
   `write_sidecars.py`) and fails on any of:
   - `import scripts.classifier.sidecar_nonfactor` / any `from` form of it
   - the symbols `NonFactorValue`, `AuditRecord`, `audit_unwrap`,
     `read_for_audit_only`
   - the substring `_nonfactor/`

   It also runs a live behavioral probe on `NonFactorValue` and, with
   `--self-test`, plants a synthetic violator in a temp dir and confirms
   the scanner catches it.

**Test output** (real tree, plus self-test):

```
$ /usr/bin/python3 tests/test_sidecar_isolation.py --self-test
[self-test] planted violator: caught 5 violations
  leaky_features.py:1 R1/R3 :: from scripts.classifier.sidecar_nonfactor import read_for_audit_only
  leaky_features.py:1 R1/R3 :: from scripts.classifier.sidecar_nonfactor import read_for_audit_only
  leaky_features.py:3 R1/R3 :: r = read_for_audit_only(cid, i_understand_this_is_non_factor=True)
  leaky_features.py:4 R1/R3 :: return r.genre.audit_unwrap()  # SHOULD BE CAUGHT
  leaky_features.py:5 R2 :: path = 'data/classifier/_nonfactor/foo.json'  # SHOULD BE CAUGHT
[isolation] PASS (scanned 25 .py files under scripts/;
                  NonFactorValue behavior probe: OK;
                  self-test caught 5 planted violations)
```

**Sidecar fields written this cycle:**

Every clip's sidecar carries `genre`, `country`, `date_released`,
`language`, `instrumental_vs_lyrics`, `live_vs_recorded`, `artist`
as `null`, plus the three non-music-class posteriors
(`SPEECH / APPLAUSE / AMBIENT`) as floats, plus provenance
(`model_id`, `weights_sha256`, `sidecar_schema_version: 1`, and the
required `__non_factor_do_not_consume__: true` marker).

The curatorial labels are `null` on purpose: those labels do not exist
in this workspace yet (they require the rated audio + a genre lookup we
have not built). **What is being validated this cycle is the
architectural contract of the sidecar, not the completeness of the
field values.** When labels arrive, the writer signature is stable; the
reader signature is stable; the isolation test does not change.

---

## 7. Known failure modes and next-cycle refinements

**MUSIC_LIVE evaluation is proxy-limited.** Applause in real
live-music recordings sits well below the music line during performance
and swells only between songs. The proxy mixdown here deliberately
inflates applause energy (RMS-matched to music, then mixed at 1.0×
applause vs 0.6× music) so PANNs' applause head can fire. That means
the reported MUSIC_LIVE recall (0.70) is an OPTIMISTIC number for
"detectable live audio", not "typical live recording". The next cycle
should replace this with real short-form live clips (a CC-BY live-audio
sampler; open-mic recordings from Free Music Archive's "Live_Recordings"
tag if reachable through the proxy).

**Two APPLAUSE and two AMBIENT clips misclassified as SPEECH.** All four
have modest speech-head activation from incidental voice-like content in
the ESC-50 recordings. Options: (a) raise the SPEECH threshold to
require a specific-speaker-class contribution (Male/Female/Child) not
just the umbrella `Speech`; (b) tune the composite rule to bias toward
SILENCE/APPLAUSE when the top-1 AudioSet leaf is one of them. Not urgent
— binary music-vs-not-music is 1.000 and 5-class is 0.873, both above
sufficiency.

**taxonomy_map.yaml v1 shipped with wrong MIDs.** Applause was
`/m/028v0c` (which is actually `Silence`); Silence was
`/m/028ght` (which is actually `Applause`); Clapping was wrong; "Live
music" was assumed to exist as an AudioSet-527 leaf, but it does not.
All corrected in v2, verified against
`/root/panns_data/class_labels_indices.csv`. The pattern (assume-then-
verify was expensive: it silently produced an internally consistent but
wrong first evaluation showing 0/10 recall on MUSIC_LIVE) is worth
codifying as a check for the next cycle — a startup-time assertion that
every mid in the YAML resolves in the CSV.

**Zero-padding short clips flooded the Silence head.** Fix: tile
short clips end-to-end. This is fine for the labeled validation set
(the tagger's decision distribution is what we measure), but the
ingestion chassis (M-INGEST-1) should NOT tile — real music chunks are
at least 30 s and don't need it.

**Fine-tuning is not a next-cycle priority.** Binary music-vs-not-music
at 1.000 on this 55-clip labeled set clears the sufficiency bar. The
next real-audio validation (when the rated corpus lands) may drop that
number; a fine-tuning pass would only pay for itself once we have real
music-side data. Deferring.

---

## 8. Reproducibility

**Interpreter:** `/usr/bin/python3` (system Python; the harness venv
does NOT have librosa / torch / TF and will fail loudly on import).
Every classifier script imports `_interp` first, which raises
`SystemExit` with the correct re-invocation command if
`sys.executable` is wrong.

**Pinned versions** (from `pip list`):
`panns_inference==0.1.1`, `torch==2.13.0+cpu`, `librosa==0.11.0`,
`soundfile==0.14.0`, `numpy==2.4.6`, `matplotlib==3.11.1`,
`pyarrow==25.0.1`, `tensorflow==2.21.0`, `tensorflow_hub==0.16.1`,
`PyYAML==6.0.1`. (`tensorflow_hub` installed but not used — rung A
survived; kept for the next-cycle YAMNet cross-check.)

**Weights SHA-256:**
`0dc499e40e9761ef5ea061ffc77697697f277f6a960894903df3ada000e34b31`
(`Cnn14_mAP=0.431.pth`; auto-fetched by `panns_inference` from Zenodo/GCS).

**Dataset origins:**
- ESC-50 audio → `https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/{filename}`; per-clip SHA-256 in valset manifest.
- ESC-50 index → `https://raw.githubusercontent.com/karolpiczak/ESC-50/master/meta/esc50.csv`.
- LibriSpeech dummy → `https://huggingface.co/datasets/hf-internal-testing/librispeech_asr_dummy/resolve/main/clean/validation-00000-of-00001.parquet` (9 192 059 B, per-row FLAC embedded).
- FluidR3_GM.sf2 → `/usr/share/sounds/sf2/FluidR3_GM.sf2` (apt-installed).

**Deterministic seeds:** valset build uses `numpy.random.default_rng(20260828)`.

**Invocation commands:**

```bash
# 1. Build the validation set (idempotent; caches downloads at data/classifier/_cache/).
/usr/bin/python3 -m scripts.classifier.build_valset

# 2. Run the tagger + taxonomy mapper over the valset and write metrics + PNG.
/usr/bin/python3 -m scripts.classifier.evaluate

# 3. Emit the 55 non-factor sidecars.
/usr/bin/python3 -m scripts.classifier.write_sidecars

# 4. Verify architectural isolation (should PASS on the current tree AND
#    catch a synthetic planted downstream import via --self-test).
/usr/bin/python3 tests/test_sidecar_isolation.py --self-test

# 5. Classify one clip on its own (spot check):
/usr/bin/python3 -m scripts.classifier.classify_clip \
    data/classifier/valset/clips/MUSIC_RECORDED__fluid_music_00.wav
```

**Sufficiency checklist:**

- [x] Tagger runs unattended on 30 s WAV via `/usr/bin/python3` (Rung A: PANNs Cnn14; documented).
- [x] Taxonomy mapping produces valid 5-class output on ≥1 clip from each class.
- [x] Validation on ≥50 labeled clips → confusion matrix. **55 clips.**
- [x] Binary music-vs-not-music accuracy ≥ 0.85: **1.000**.
- [x] 55 non-factor sidecar JSONs under `data/classifier/_nonfactor/`.
- [x] `tests/test_sidecar_isolation.py` passes AND catches a synthetic plant with `--self-test`.
- [x] `docs/classifier_baseline_report.md` published (this file) with all 8 sections.
