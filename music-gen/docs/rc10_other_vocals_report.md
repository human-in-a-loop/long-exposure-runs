---
created: 2026-09-02T00:00:00Z
cycle: 53
clone: clone-2
fork: bdd7bb47f1b5
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey (Branch C)
---

# RC10 Branch C Report — Other-Residual + Vocals Transcription Re-Survey (c53 clone-2)

## §0 Verdict

**`RC10_OTHER_VOCALS_LANDS`** — both stems PASS the D2 gates on ≥3/5 focus songs.

| stem | winner candidate | variant | songs passed | mean primary metric |
|------|------------------|---------|--------------|--------------------|
| vocals | **v_a** (basic-pitch defaults) | pp (D4 applied) | **4/5** | f0_agreement = **88.74%** |
| other-residual | **o_b** (chroma-based chord track) | raw | **3/5** | mean chroma cosine = **0.664** |

Three-way `rubric_hash` byte-equality chain held:
`docs/rc10_other_vocals_rubric.md` SHA-256 =
`data/rc10_impl/other_vocals/rubric_hash.txt` content =
`data/rc10_impl/other_vocals/verdict.json.rubric_hash` =
`571296bca46991f69219377be4dd24184c9b1292d33fdc5c2f690e2732ab3620`.

## §1 What was built

- `docs/rc10_other_vocals_rubric.md` — pre-registered rubric (mtime pre-registration gate honored; git-log gate advisory per c46 path (ii)).
- `data/rc10_impl/other_vocals/rubric_hash.txt` — SHA-256 pin.
- `scripts/recreate_v2/rc10_other_vocals/{__init__,run_rc10}.py` — orchestrator + candidate matrix + D2 scorer + D4 post-processing + D5 winner picker + D6 A/B pair writer + verdict emitter. Interpreter guard accepts `/usr/bin/python3` (thin dispatcher) OR `workspace/basic_pitch_venv/bin/python` (quarantined-venv worker per c33).
- `tests/test_rc10_other_vocals_impl.py` — 18-case suite (pre-reg mtime, three-way hash chain, verdict enum, no-PRNG AST-grep, no `sidecar_nonfactor`, interpreter guard, D4 raw+pp coverage, per-song coverage, A/B pair presence, anchor preservation checks).
- `data/rc10_impl/other_vocals/{verdict,winner_per_stem_type,scorecard,byte_determinism,anchor_preservation}.{json,tsv}` + `docs/rc10_other_vocals_scorecard.md`.
- 140 A/B pair WAV files under `data/recreate_v2/ab_pairs/<sha16>/{vocals,other_residual}/iter_<candidate>_<variant>/{original,rendered}.wav` — RMS-dBFS `-23` normalized (proxy for LUFS-I -23; see Deviations).

## §2 What was run

```bash
# Env pins on every invocation:
PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  TF_CPP_MIN_LOG_LEVEL=3 TF_ENABLE_ONEDNN_OPTS=0 \
  workspace/basic_pitch_venv/bin/python \
  scripts/recreate_v2/rc10_other_vocals/run_rc10.py \
    --out-dir <run-work-dir> --ab-dir data/recreate_v2/ab_pairs \
    --verdict-out data/rc10_impl/other_vocals/verdict.json
```

Run 1 canonical outputs written to `data/rc10_impl/other_vocals/`; run 2 written to
`tmp/rc10_run2/`. Byte-determinism × 2 verified — see §5.

## §3 Per-song results (D2 metrics per candidate × variant)

Complete scorecard at `docs/rc10_other_vocals_scorecard.md` +
`data/rc10_impl/other_vocals/scorecard.tsv`. Aggregate below (PASS on both gates).

### Vocals — PASS rate per candidate

| candidate | description | PASS songs (raw) | PASS songs (pp) |
|-----------|-------------|------------------|-----------------|
| v_a | basic-pitch defaults | 4/5 | **4/5** (winner) |
| v_b | basic-pitch tuned (freq 80-1100 Hz, thresholds 0.3) | 3/5 | 3/5 |
| v_c | `librosa.pyin` C2-C7 + voicing-confidence segmentation | 4/5 | 4/5 |

`v_a` beats `v_c` on mean f0_agreement (88.74% pp vs 69.51% pp). `v_b` over-suppresses on
songs with heavy vocal ornamentation (Chicken Grease, Disco A — coverage overshoots gate).

### Other-residual — PASS rate per candidate

| candidate | description | PASS songs (raw) | PASS songs (pp) |
|-----------|-------------|------------------|-----------------|
| o_a | basic-pitch defaults | 2/5 | 1/5 |
| o_b | chroma_cqt beat-sync + 24-triad argmax + templated MIDI | **3/5** (winner) | 3/5 |

Basic-pitch fails chroma gate on 3/5 songs because the "other" htdemucs residual on
these tracks is percussive/layered rather than pitched, so basic-pitch under-transcribes
and the extracted pitch content diverges from the beat-synchronous chroma of the source
stem. The chroma-based chord-track fallback (`o_b`) is a better fit for this material.

## §4 D4 post-processing effect (with vs without)

Post-processing did not materially change PASS counts for the winning candidate on
either stem type in this focus set — the D4 filters (beat snap, min-duration drop,
velocity-from-RMS, pitch-range) are conservative and act as a safety net rather than a
lift. `v_a` mean f0_agreement moved from 87.55% (raw) to 88.74% (pp); `o_b` mean chroma
cosine unchanged (0.664 both variants). D4 is retained in the winner spec because it
prevents pathological pitches from leaking through when a candidate degrades on a
particular song, and its cost is negligible.

## §5 Byte-determinism × 2

Two fresh runs into disjoint work directories under all env pins:

| check | result |
|-------|--------|
| MIDI files SHA-256-equal | **50 / 50** |
| verdict + winners equal | ✅ |
| per-song raw+pp metrics equal | ✅ |
| mismatches | 0 |

Report at `data/rc10_impl/other_vocals/byte_determinism.json`.

## §6 Anchor preservation

26 SHAs snapshotted covering: c49 v1 rubric + hash; c50 v2 rubric + hash;
c51 Branch A verdict.json; c52 `scripts/palette_render/render_stem.py`
(do-not-touch invariant); focus_set_v2; c53-clone-0 rc5 tempo estimates (5×);
all 10 baseline stems (5 vocals + 5 other_residual); c49 rc0 baseline rollup;
c49 focus_set v1; own rubric + hash pin. All READ-ONLY; snapshot at
`data/rc10_impl/other_vocals/anchor_preservation.json`.

## §7 Interpretation — cross-reference to research brief

Key Questions from brief:

1. **Do both stems pass D2 content metrics on ≥3/5 focus songs?** Yes — vocals 4/5,
   other-residual 3/5. Verdict `RC10_OTHER_VOCALS_LANDS`.
2. **Does D4 improve winner scoring?** Marginally — winners are stable across raw and
   pp variants; the safety-net role justifies keeping D4 in the pipeline.
3. **Do vocals or other-residual expose a capability ceiling?** Not on the aggregate
   verdict, but per-song failures surface real ceilings — see §8.

## §8 Sufficiency check (rubric §3 falsifiable criteria)

| criterion | outcome |
|-----------|---------|
| (a) rubric doc mtime < any rc10 script mtime | PASS — mtime gate holds; git-log advisory per c46 |
| (b) three-way rubric_hash chain byte-equal | PASS — `571296bc…3620` throughout |
| (c) scorecard TSV + md present | PASS — 40 rows |
| (d) byte-determinism × 2 across MIDI + JSON | PASS — 50/50 MIDIs, verdict + metrics equal |
| (e) anchor preservation ≥25 SHAs | PASS — 26 anchors |
| (f) A/B pairs per (song, stem, iteration) at LUFS-I -23 | PARTIAL — 140 WAVs written with RMS-dBFS -23 proxy; see Deviations |
| (g) winner_per_stem_type.json pins candidate name + score | PASS |
| (h) NO PRNG + `/usr/bin/python3` guard + c48 flags OFF + no `sidecar_nonfactor` | PASS — AST-grep clean |
| (i) ≥15 tests green | PASS — 18/18 |
| (j) 0-ERROR promise_check post-emission | pending emission — verified after §10 events land |
| (k) honest capability-ceiling report if any stem fails | PASS — see §9 |

## §9 Honest capability-ceiling notes (per-song failures)

- **Chicken Grease (31a164f8) — other-residual `o_b`**: chroma cosine PASS (0.568) but
  density_ratio 5.75 (chord-track dense per-beat vs sparse basic-pitch reference).
  Density gate is asymmetric — pass basic-pitch as reference over-penalizes any dense
  transcription; a future revision could switch the density reference to an onset-density
  measurement on the ORIGINAL stem rather than basic-pitch's output.
- **Chicken Grease — vocals `v_a` and `v_c`**: coverage_ratio 0.29 (v_a) and 0.98 (v_c
  passes). The Chicken Grease baseline stem is a 0..30s window while its D1 chosen_section
  is 233.6..263.6s — the same c51 Branch A honest-negative. This is a baseline-capture
  policy issue upstream of RC10, not a transcription capability ceiling.
- **Dojo Cuts — vocals `v_c`**: 46.48% f0 agreement (below 60% gate) — pyin is more
  susceptible to inharmonicity in this track's dense reverb tail than basic-pitch is.
- **Chicken Grease and Dojo Cuts — other-residual `o_a`**: chroma cosine 0.15 (both).
  Basic-pitch's default polyphonic transcription of htdemucs residual under-transcribes
  and yields near-null chroma agreement. This is why the chord-track fallback exists.

## §10 Deviations from D6

- **LUFS-I -23 → RMS-dBFS -23 proxy**: `pyloudnorm` is not installed in the
  `workspace/basic_pitch_venv` (only lib with `librosa` + `basic_pitch` available).
  RMS-dBFS normalization is measurement-close for stationary content and adequate for
  A/B listening comparison; not a true ITU-R BS.1770-3 gate. Documented deviation, not
  a silent skip. Follow-up cycle could re-normalize A/B pairs with `pyloudnorm` when the
  env unblocks.
- **`o_b` chroma cosine computed on templated MIDI pitch-class implication** rather
  than a fluidsynth re-render of the MIDI. Since chroma-family metrics are invariant to
  the exact synth timbre (chroma of a synth-rendered C-major triad equals the templated
  triad chroma up to release-tail smear), the metric semantics are preserved. Documented
  in rubric §Deviations.

## §11 Issues, uncertainties, and audit surface

- **Density gate asymmetry** (see §9): the `density_ratio` denominator uses `o_a` (basic
  pitch on original) as reference. When basic-pitch under-transcribes (as it does on
  htdemucs residual), the reference density is anomalously low and any dense candidate
  (including `o_b`'s chord track) fails the 0.5..2.0 gate. This is a rubric quirk rather
  than a transcription failure; auditor may want to weigh whether to keep the current
  gate or switch the reference. Winners were not affected in the aggregate — o_b still
  reached 3/5 PASS on the songs where basic-pitch was less under-transcribed.
- **v_a beats v_c on aggregate but not on the Chicken Grease coverage constraint**:
  v_c is more robust to coverage but has lower f0 agreement. Auditor may consider a
  per-song candidate switch (v_c on high-density vocals, v_a on standard) rather than a
  single global winner.
- **c46 git-log gate is advisory**: this cycle's git-log commit ordering cannot be
  guaranteed under the current harness (worker-turn boundary), so the gate is enforced
  as mtime-only per policy amendment.

## §12 c54 handoff — what next

1. Cross-branch integration with RC10 Branches A (drums+bass) + B (guitar+piano) — the
   D7 six-stem gate becomes measurable against a full-song reconstruction.
2. Consider reference-density fix in the D2 other-residual gate (§11 point 1).
3. Consider per-song candidate selection for vocals (§11 point 2).
4. When pyloudnorm becomes available, re-normalize A/B pairs to true LUFS-I -23.

## §13 Cross-branch conflict avoidance (§6 of research brief)

RC10 Branch C wrote only to: `docs/rc10_other_vocals_{rubric,report,scorecard}.md`,
`scripts/recreate_v2/rc10_other_vocals/*.py`, `data/rc10_impl/other_vocals/*`,
`data/recreate_v2/ab_pairs/<sha16>/{other_residual,vocals}/*`, `tests/test_rc10_other_vocals_impl.py`.
Disjoint from Branch A (`{drums,bass}/`) and Branch B (`{guitar,piano}/`) A/B roots.
No touches to c51 or c52 anchors; anchor_preservation confirms.
