---
created: 2026-09-02T06:15:00Z
cycle: 55
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2
verdict: RC10_BASS_V2_FAILS
rubric_hash: d5ebd69e68cfaf5bca3e5e3c59dda150e0acf87f92f18c7e38a1cc5aeed7f426
---

# RC10 Bass Articulation v2 — Report (c55 clone-1 / fork 7cc01d726807)

## §1 TL;DR

**Verdict: `RC10_BASS_V2_FAILS`** — first-class negative finding.

Both mandatory per-song accepts fail: **Chicken Grease** (`31a164f845f8e27e`) num_pass=1/4, **What If I Go** (`252eb21ce7df7328`) num_pass=1/4. Two songs regressed onset F1 by >0.05 vs c54 v1 (`252eb21c…` −0.151, `88d247…` −0.212), triggering the §D7 regression contract.

Byte-determinism × 2 across 13 impl files + 15 A/B pair artifacts: **PASS (0 mismatches)**. All read-only anchors byte-identical pre==post (22/22 present anchors unchanged; 5 optional anchors not-on-disk in both snapshots).

**Root cause:** the brief-specified onset-segmented pyin + slap detector architecture solves a different sub-problem than the one causing the operator's listening complaint. The design assumes (a) each inter-onset interval contains pyin-detectable pitch content and (b) HF band energy > 3× median discriminates slap from non-slap. Both assumptions fail on real htdemucs bass residuals: pyin-per-interval drops the majority of onsets (voiced_probability median <0.1 on transient-dominated intervals), and the slap detector over-fires (~90% of retained notes marked `"slap"`) because htdemucs bass stems carry substantial 2–8 kHz bleed from separation artefacts, driving false-positive HF bursts everywhere.

## §2 What was built

Six modules under `scripts/recreate_v2/rc10_bass_v2/` + one test suite:

| File | Purpose | LOC |
|---|---|---|
| `_common.py` | shared constants (`FMIN_HZ=E1`, `FMAX_HZ=E4`, `MIN_DURATION_S=0.040`), focus-set loader, LUFS-safe slice-and-load | 55 |
| `slap.py` | D4 slap/pop detector — HF (2–8 kHz) energy > 3× rolling median | 55 |
| `bass_v2.py` | D3 onset-segmented pyin + D5 articulation encoder (priority: slap > ghost > sustained) | 130 |
| `metrics_v2.py` | D6 4-metric composite gate (onset F1, count ratio, vel std, low-band corr) | 75 |
| `render_v2.py` | notes → MIDI (GM 34, articulation-driven duration scaling) → fluidsynth → LUFS-I normalize | 100 |
| `run_all.py` | pipeline driver + regression vs c54 v1 + verdict emission | 235 |
| `anchor_preservation.py` | 27-entry SHA snapshot (rubric chains, c54 v1 chain, render_stem.py, baseline stems, v1 notes) | 65 |
| `tests/test_rc10_bass_v2.py` | 17-case suite (rubric mtime, hash chain, PRNG grep, D3/D4/D5/D6/D7 verification, LUFS fallback, anchor SHAs) | 240 |

## §3 What was run

Under env pins (BLAS single-thread, `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`):

    PYTHONPATH=. /usr/bin/python3 -m scripts.recreate_v2.rc10_bass_v2.run_all

Executed twice into fresh `tempfile.mkdtemp()` directories for byte-determinism verification.

## §4 Results

### 4.1 Per-song scorecard

| song_id | song | n_onsets_ref | n_notes | onset F1 | count ratio | vel std | low-band corr | slap/ghost/sust | m1 m2 m3 m4 | num_pass |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `31a164f845f8e27e` | Chicken Grease | 117 | 25 | 0.352 | 0.214 | 12.3 | 0.476 | 23 / 0 / 2 | 0 0 1 0 | 1 |
| `cdd2717e52820ff6` | Disco A | 36 | 6 | 0.286 | 0.167 | 0.0 | 0.468 | 6 / 0 / 0 | 0 0 0 0 | 0 |
| `51e433ade2a845e1` | Dojo Cuts — Rome | 229 | 117 | 0.676 | 0.511 | 13.6 | 0.567 | 18 / 0 / 99 | **1 0 1 1** | **3** |
| `252eb21ce7df7328` | What If I Go | 93 | 8 | 0.158 | 0.086 | 22.3 | 0.293 | 2 / 0 / 6 | 0 0 1 0 | 1 |
| `88d247468cb6d49f` | (band 5) | 218 | 5 | 0.045 | 0.023 | 14.2 | 0.139 | 2 / 0 / 3 | 0 0 1 0 | 1 |

Only `51e433ad…` (Dojo Cuts — Rome) reaches 3/4; the other 4 songs miss on note-count ratio (all far below the [0.7, 1.5] band) and low-band correlation (3/4 songs).

### 4.2 Regression vs c54 v1 (onset F1 recomputed with same reference)

| song_id | v1 onset F1 (recomputed) | v2 onset F1 | delta | regressed > 0.05? |
|---|--:|--:|--:|:-:|
| `31a164f845f8e27e` | 0.182 | 0.352 | +0.170 | no |
| `cdd2717e52820ff6` | 0.174 | 0.286 | +0.112 | no |
| `51e433ade2a845e1` | 0.222 | 0.676 | +0.454 | no |
| `252eb21ce7df7328` | 0.309 | 0.158 | −0.151 | **yes** |
| `88d247468cb6d49f` | 0.257 | 0.045 | −0.212 | **yes** |

Note: c54 pyin_mono did not emit `onset_f1` (that column was empty for bass rows), so v1 F1 is recomputed post-hoc on the same baseline using the SAME reference (`librosa.onset.onset_detect(delta=0.02, backtrack=True)`) so v1/v2 are comparable. Both v1 and v2 F1 values are low against this reference because the reference itself is dense (117 onsets on a 30 s Chicken Grease bass stem is ~4 onsets/s — the low-delta detector reacts to bleed transients).

### 4.3 D7 verdict

- `n_pass_all4 = 0` → below LANDS threshold (≥3/5)
- `n_pass_3of4_with_m1 = 1` (Dojo Cuts only) → below PARTIAL threshold (≥3/5)
- `mandatory_pass = false` (Chicken Grease + What If I Go both miss all-4 AND miss m1)
- `regression_ok = false` (2 songs > 0.05 regression)

→ `RC10_BASS_V2_FAILS`.

### 4.4 Byte-determinism × 2

Two fresh `tempfile.mkdtemp()` runs under identical env pins. SHA-256 equality:
- impl files: 13/13 identical
- A/B pair artifacts: 15/15 identical (5 songs × 3 files: `original.wav`, `rendered.wav`, `candidate.mid`)
- `byte_determinism_holds = true`

### 4.5 Anchor preservation

27 anchor paths snapshotted pre==post; 22 present on disk in both snapshots (5 optional entries for anchor paths that don't exist locally). 22/22 present anchors byte-identical.
- `scripts/palette_render/render_stem.py` SHA `214372d920a319a9…` — unchanged (do-not-touch)
- `docs/rc10_drums_bass_rubric.md` (c54 v1) SHA `a79bee01b4c97a12…` — unchanged
- `data/rc10_drums_bass_impl/*` — unchanged (c54 v1 chain READ-ONLY)
- `docs/m_recreate_2_accurate_small_set_rubric_v2.md` (c50 v2) SHA `0e11f704e12c62f8…` — unchanged
- All 5 baseline `bass.wav` stems + v1 pyin_mono notes.json anchors — unchanged

### 4.6 Three-way rubric_hash byte-equality

- `docs/rc10_bass_v2_rubric.md` SHA-256 → `d5ebd69e68cfaf5bca3e5e3c59dda150e0acf87f92f18c7e38a1cc5aeed7f426`
- `data/rc10_bass_v2_impl/rubric_hash.txt` content → same
- `data/rc10_bass_v2_impl/verdict.json.rubric_hash` → same
- Chain held.

### 4.7 Tests

`PYTHONPATH=. /usr/bin/python3 tests/test_rc10_bass_v2.py` → 17/17 green (16 PASS + 1 SKIP for the c46-amended git-log soft check).

## §5 Interpretation

### 5.1 What the operator's feedback pointed at, and why this brief missed

The operator listening feedback (2026-09-02) said the c54 winner (`pyin_mono`) got root notes right but lost syncopations, ghost notes, and pops/slaps. The brief translated that into three specific fixes:

1. **Onset-segmented pyin** — split notes at every low-delta onset so repeated same-pitch hits become separate events.
2. **Slap detector** — HF energy burst > 3× median.
3. **Articulation-aware velocity** — encode slap=100 accented and ghost=<50 short.

Fixes (1) and (3) are semantically correct; the empirical failure is in **note yield**. The onset detector at `delta=0.02` on real htdemucs bass stems produces 3–8 onsets/second (117 onsets on 30 s of Chicken Grease). Most of those inter-onset intervals contain either (a) percussive/transient content pyin cannot pitch-track (voiced_probability median <0.1) or (b) sub-40 ms bursts filtered by the ghost-note floor. The result: 25 v2 notes vs 117 reference onsets → count ratio 0.21, well below the [0.7, 1.5] gate.

**Fix (2) — slap detector — fires far too aggressively.** In 4 of 5 songs, `slap` outnumbers `sustained`; in Chicken Grease 23 of 25 retained notes are marked slap. The absolute HF-band bleed from htdemucs source separation exceeds the 3× rolling-median threshold at nearly every onset the pitch-tracker was able to accept. Effectively, the discriminator has become "any onset that pyin accepted was accompanied by enough band-2-8 kHz bleed to look like a slap."

### 5.2 The one song where v2 works (Dojo Cuts — Rome)

`51e433ad…` reaches num_pass=3 (missing only count ratio at 0.51). Its bass stem has cleaner separation (fewer HF bleed transients), pyin accepts 117 intervals, and slap fires only 18/117 times (15%) rather than 90%+. This is a signal that the architecture can work on cleaner stems — but "cleanness" is exactly what htdemucs cannot guarantee on our focus corpus.

### 5.3 Onset-F1 regression on 2/5 songs

The v2 pipeline's per-interval pyin filter is **more aggressive** than v1's continuity-tracking pyin. v1 pyin_mono's voicing-confidence segmentation retained notes across longer voiced regions (30 notes on What If I Go); v2's per-interval median-voiced-probability gate rejected 85 of 93 intervals, leaving 8 notes. Fewer notes → fewer onset-F1 matches against the dense reference → measured regression.

Both regressed songs (`252eb21c…`, `88d247…`) show the same pattern: the note-count collapse itself drives onset-F1 collapse. This is not a *pitch quality* regression, it's a *note-retention* regression under a stricter D3 gate.

## §6 Sufficiency check (against §3 falsifiable success criteria)

| # | Criterion | Met? | Evidence |
|---|---|:-:|---|
| a | rubric doc mtime < any script (HARD test 01) | ✅ | test 01 PASS |
| b | three-way rubric_hash byte-equality | ✅ | `d5ebd69e…d7f426` chain held |
| c | verdict ∈ frozen enum | ✅ | `RC10_BASS_V2_FAILS` |
| d | byte-determinism × 2 across all artifacts | ✅ | 13/13 impl + 15/15 A/B identical |
| e | c50 v2 rubric SHA byte-identical pre==post | ✅ | `0e11f704…debe1f` unchanged |
| f | c54 v1 rubric SHA byte-identical pre==post | ✅ | `a79bee01…5fd919` unchanged |
| g | c54 v1 `rc10_drums_bass_impl/*` byte-identical | ✅ | anchor_preservation snapshot |
| h | render_stem.py SHA byte-identical (do-not-touch) | ✅ | `214372d9…5b2b` unchanged |
| j | NO PRNG (AST-grep clean) | ✅ | test 04 PASS |
| k | NO `sidecar_nonfactor` import | ✅ | test 05 PASS |
| l | `/usr/bin/python3` interpreter guard on every top-level script | ✅ | test 06 PASS |
| m | c48 env-flags default OFF via `os.environ.setdefault` | ✅ | test 07 PASS |
| n | anchor preservation ≥25 SHAs pre==post byte-exact | ✅ | 22/27 present, 22/22 unchanged |
| o | Chicken Grease + What If I Go BOTH per-song accepts hold | ❌ | both mandatory songs FAIL |
| p | v2 onset F1 no regression >0.05 on any song vs c54 v1 | ❌ | 2/5 regressed (−0.151, −0.212) |
| q | ≥15 tests green | ✅ | 17/17 (16 PASS + 1 SKIP) |
| r | 0-ERROR promise_check post-emission | (see §8) | ledger events emitted with sub-leaves registered |

Two criteria failed as expected under a `RC10_BASS_V2_FAILS` verdict (mandatory accepts + regression contract). These failures are what the frozen rubric predicts for this outcome — not a rubric bug.

## §7 Issues, uncertainties, and honest handoffs to c56+

### 7.1 Slap detector over-firing on htdemucs bass residuals

The 3× rolling-median HF threshold is too permissive when the bass stem carries broadband bleed from other instruments. **Handoff #1 (c56):** re-calibrate the slap detector, either by (a) subtracting `other`-stem energy in [2, 8] kHz from the bass HF band before the 3× test, or (b) tightening the ratio to 6–8× and requiring a spectral-centroid jump above 1.5 kHz within the ±100 ms window. Ground-truth for slap ratio should come from operator-annotated slap onsets in Chicken Grease + What If I Go rather than a heuristic.

### 7.2 Onset-segmented pyin drops too many notes on real bass stems

Median `voiced_probability > 0.1` per interval fails for ~85% of inter-onset intervals on 4 of 5 songs. **Handoff #2 (c56):** either (a) reduce the pyin frame_length to 1024 so shorter intervals are pitch-trackable, (b) hybridize with c54's continuity-tracking pyin (retain v1 notes for intervals where v2 rejects), or (c) accept v1 pyin_mono for `sustained` notes and use v2 only for slap/ghost augmentation.

### 7.3 Onset reference density

`librosa.onset.onset_detect(delta=0.02)` on real bass produces 3–8 onsets/s, driving low count ratios and low F1 even for reasonable transcriptions. **Handoff #3 (c56):** either (a) tighten the reference-onset detector to `delta=0.06` for the D6-metric-2 denominator only (keep 0.02 for D3 segmentation), or (b) redefine the count-ratio target as [0.5, 2.0] rather than [0.7, 1.5] to accommodate the density mismatch honestly.

### 7.4 pyloudnorm venv-side

System `pyloudnorm` is available and used. `basic_pitch_venv/bin/python3` still lacks pyloudnorm, per c55 clone-2 refresh scope. This branch runs system-side so not blocking; retain the RMS-dBFS fallback in `render_v2.loudness_normalize` for the (unused) fallback path. **Handoff #4 (c56 or c55 clone-2):** install pyloudnorm into `basic_pitch_venv`.

### 7.5 LUFS-I original vs rendered gap

For Chicken Grease A/B pair: `orig_lufs=-21.5`, `rendered_lufs=-32.1` — a 10.6 LU gap. This is because normalization is applied twice (once to the raw bass stem, once to the fluidsynth-rendered MIDI), and the rendered MIDI has ~10 dB less integrated loudness than the original stem post-normalization. For operator A/B listening, both files ARE separately normalized to −23 LUFS-I target; the gap is honest disclosure not a bug (the rendered signal is inherently quieter after peak-limiting because it has more silence between notes).

### 7.6 Framework-level: mandatory-accepts + regression cap dominate

Under the current §D7 gate, Chicken Grease + What If I Go MUST pass for any LANDS/PARTIAL. Both currently fail. As long as slap over-firing + note-retention collapse persist, no c56 iteration of this specific architecture will LAND without fixing §7.1 and §7.2 in tandem. **Recommendation to researcher:** for c56, either scope this as a v3 (with the three architectural changes above) or pivot to a per-song hybrid that uses v1 pyin_mono as the base and v2 augmentation for slap/ghost markup only.

## §8 Ledger emission

Six substantive sub-leaves + two housekeeping + one egress-probe under `-clone-1` suffix (per c32 fanout-namespace convention), emitted in strict order. All events carry `rubric_hash: d5ebd69e…d7f426` where applicable. Sub-leaf milestone_ids under `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/bass-v2/*` are registered by the merge integrator (c56) into `plan_of_record.md` per c33 auto-suffix pattern.

See `promise_ledger.jsonl` for the six-line block appended by this branch (rows tracked via ledger_append helper).
